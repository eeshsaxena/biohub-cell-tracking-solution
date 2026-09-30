#!/usr/bin/env python3
"""t6gtriz = t6stk3 body + TRILINEAR UNet feature gather at the lcefr-refined coordinates, Z AXIS ONLY.

usage:
  python scratch_kernels/build_t6gtriz.py               derive scratch_kernels/v_t6gtriz (see "OUTPUT" below)
  python scratch_kernels/build_t6gtriz.py --out DIR     write the build into DIR instead (must be new or identical)
  python scratch_kernels/build_t6gtriz.py --selftest    also run the CPU emulation (torch, tiny synthetic maps)

WHAT. Same arm as t6gtri (scratch_kernels/build_t6gtri.py), with BIOHUB_GTRI_AXES='z': the four UNet feature
gathers of the edge model (primary src/tgt, secondary src/tgt) read the 32-channel UNet map with a trilinear
lookup whose z is the lcefr/sub-voxel-refined z (|offset| <= 0.4999 voxel) while y/x stay on the integer peak.
In the helper this is the line pair
        if _GT_AXES == 'z':
            q_all[..., 1:] = icoords[..., 1:]
Detection, SV offsets, lcefr geometry inputs, final coordinates, the ILP inputs other than edge_prob and the
whole of cell 5 are untouched. Everything else (self-check, NO-OP guard, ARM_GTRI_STATS / ARM_GTRI_XWIN
markers) is the shared t6gtri block.

SHARED BLOCK, FROZEN. The patch text is imported from build_t6gtri.py (one source for the pair, so t6gtri and
t6gtriz can only differ in the axes switch). Its sha256 is pinned below: if build_t6gtri.py's block or anchor is
ever edited, this builder refuses instead of silently building a different t6gtriz.

CHECKS (all hard failures, no try/except):
  builder-side  cell-4 anchor exactly once in v_t6stk3; no ARM_GTRI anywhere in the base; the REAL t6stk3-patched
                predictor (data/out_t6stk3, the file the Kaggle run actually executed) carries this base's SV
                helper and every lcefr replacement at the expected counts (provenance); each of the 7 predictor
                anchors matches exactly once in REAL and each replacement lands exactly once; the block's own
                runtime patch logic, executed on a scratch copy of REAL, equals an independent sequential
                replace; the z-only helper line appears exactly once; AST: exactly 4 _gt_gather call sites with
                (model, map[:, f_idx(+1)], p_rcoords_X, p_coords_X, p_mask_X) and the only _index_features call
                left is inside _gt_gather; p_rcoords are built before the gathers; _gt_xwin sits after c_src
                in the pair loop; _gt_report after the ARM_LCEFR print; every cell and the patched predictor
                compile; mutation: removing or duplicating any one anchor makes the block raise at runtime.
  runtime       (inside the notebook, cell 4, top level, no try) each anchor count == 1 else RuntimeError;
                exactly 4 gathers routed; compile; persist check; bad axes / lcefr-off raise at import in the
                worker; first call asserts trilinear(integer peaks) == native gather (SELFCHECK); NO-OP guard
                raises if the gathered features never differ from the integer-peak ones; per movie
                `ARM_GTRI_STATS axes=z calls=.. nodes=.. mean_abs_feat_delta=.. selfcheck=1` (cumulative per
                worker; nodes == 2 x ARM_LCEFR nodes_refined because 4 gathers per pair) and
                `ARM_GTRI_XWIN src_nodes=.. src_offpeak=..` (read-only diagnostic).

OUTPUT. scratch_kernels/v_t6gtriz already exists (built 09-26 10:50 by `build_t6gtri.py t6gtriz --axes z`).
Existing v_ dirs are never modified: if the dir exists this builder compares the fresh build byte for byte and
reports IDENTICAL (nothing written) or refuses (exit 2). If it does not exist it is written.
"""
import ast
import filecmp
import hashlib
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import textwrap
import types

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
TAG = "t6gtriz"
AXES = "z"
BASE = SK / "v_t6stk3"
DEST = SK / ("v_" + TAG)
SHARED = SK / "build_t6gtri.py"
REAL = ROOT / "data" / "out_t6stk3" / "tracking_repo" / "scripts" / "predict_unet_transformer.py"
TRAIN = REAL.with_name("train_unet_transformer.py")
NL = chr(10)

SHARED_SHA = "e1307dd00aabecf3fb884b74d17888e25e0e51a6276217251ebb37dacbbfc987"  # sha256(CELL4_ANCHOR + BLOCK)
REAL_SHA = "22260752568a8a914810a790741ad4d25139761500c0b2f3d976957374b2d72b"    # the t6stk3 run's predictor
Z_LINE = "    if _GT_AXES == 'z':\n        q_all[..., 1:] = icoords[..., 1:]\n"
XENV = ('print("ARM_XENV tag=t6gtriz SUBVOXEL=hsg200 LCEFR=kept GTRI=z GAIN=2.00 CLIP=0.4999", flush=True)')
AXES_LINES = ["os.environ['BIOHUB_GTRI_AXES'] = 'z'\n",
              "print('ARM_GTRI axes=z (trilinear UNet gather at the lcefr-refined coords, 4 call sites)', flush=True)\n",
              "print('ARM_GTRI patch applied to', _ps, '| gathers=4 axes=z', flush=True)\n"]
# Prerequisites the block relies on, each exactly once in the REAL predictor (SV + lcefr state of t6stk3).
PREREQ = ["_LC_ON = os.environ.get('BIOHUB_LINKER_REFINED_COORDS', '0') != '0'\n",
          "        _lc_refined_so_far[:, 1:] += _lc_off_so_far\n",
          "            p_rcoords_src = torch.from_numpy(\n",
          "            p_rcoords_tgt = torch.from_numpy(\n",
          "def _sv_softarg_offsets(lg, arr):\n",
          "def _detect_cells_pooled(\n",
          "import torch.nn.functional as F\n",
          "import numpy as np\n"]
EXPECTED_CALLS = {
    "_gt_gather(model, unet_out[:, f_idx], p_rcoords_src, p_coords_src, p_mask_src)",
    "_gt_gather(model, unet_out[:, f_idx + 1], p_rcoords_tgt, p_coords_tgt, p_mask_tgt)",
    "_gt_gather(secondary_model, secondary_unet_out[:, f_idx], p_rcoords_src, p_coords_src, p_mask_src)",
    "_gt_gather(secondary_model, secondary_unet_out[:, f_idx + 1], p_rcoords_tgt, p_coords_tgt, p_mask_tgt)",
}


def fail(msg):
    raise SystemExit("BUILD_T6GTRIZ FAIL: " + msg)


def need_once(text, s, where):
    n = text.count(s)
    if n != 1:
        fail("%s: expected exactly 1 match, got %d: %r" % (where, n, s[:90]))


def load_shared():
    spec = importlib.util.spec_from_file_location("build_t6gtri_shared", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sha = hashlib.sha256((mod.CELL4_ANCHOR + mod.BLOCK).encode("utf-8")).hexdigest()
    if sha != SHARED_SHA:
        fail("build_t6gtri.py block/anchor changed (sha %s != pinned %s): re-verify before rebuilding" % (sha, SHARED_SHA))
    return mod


def run_block(block, src):
    """Execute the block's own patch logic (what cell 4 runs on Kaggle) on a scratch copy of `src`."""
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "predict_unet_transformer.py"
        p.write_text(src, encoding="utf-8")
        ns = {"os": types.SimpleNamespace(environ={}), "_ps": p, "print": lambda *a, **k: None}
        exec(compile(block, "t6gtriz_block", "exec"), ns)
        if ns["os"].environ.get("BIOHUB_GTRI_AXES") != AXES:
            fail("block did not set BIOHUB_GTRI_AXES=%r" % AXES)
        return p.read_text(encoding="utf-8"), ns["_gt_pairs"]


def check_provenance(real, c4):
    if hashlib.sha256(REAL.read_bytes()).hexdigest() != REAL_SHA:
        fail("REAL predictor sha changed: %s" % REAL)
    for s in PREREQ:
        need_once(real, s, "REAL prerequisite")
    if "ARM_GTRI" in real or "_gt_gather" in real:
        fail("REAL predictor already carries gtri code")
    # every lcefr replacement of THIS base cell 4 is in REAL, at the counts the lcefr block asserts
    l0 = c4.index("_lc_pairs = [")
    l1 = c4.index("\n]\n", l0) + 2
    lc_pairs = ast.literal_eval(c4[l0 + len("_lc_pairs = "):l1])
    lc_expected = ast.literal_eval(c4[c4.index("_lc_expected = ", l1) + len("_lc_expected = "):].split(NL, 1)[0])
    if len(lc_pairs) != 9 or len(lc_expected) != 9:
        fail("lcefr table shape changed")
    for (old, new), k in zip(lc_pairs, lc_expected):
        if real.count(new) != k:
            fail("REAL lacks lcefr replacement x%d: %r" % (k, new[:80]))
    # the SV helper of THIS base cell 4 (with lcefr's globals spliced in by lcefr anchor 1) is what REAL carries
    sv0 = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    sv_helper = c4[sv0:c4.index('"""', sv0)]
    need_once(sv_helper, lc_pairs[0][0], "lcefr anchor 1 inside the base SV helper")
    need_once(real, sv_helper.replace(lc_pairs[0][0], lc_pairs[0][1], 1), "REAL vs base SV helper (+lcefr globals)")
    return len(lc_pairs)


def check_patched(real, patched, pairs):
    if len(pairs) != 7:
        fail("expected 7 predictor anchors, block has %d" % len(pairs))
    indep = real
    for old, new in pairs:
        need_once(real, old, "predictor anchor (static, REAL)")
        need_once(indep, old, "predictor anchor (static, sequential)")
        indep = indep.replace(old, new, 1)
    if indep != patched:
        fail("runtime patch logic and the builder's independent replace disagree")
    for old, new in pairs:
        need_once(patched, new, "replacement lands once")
    need_once(patched, Z_LINE, "z-only helper line in patched predictor")
    need_once(patched, "_GT_AXES = os.environ.get('BIOHUB_GTRI_AXES', '')\n", "axes switch")
    for s in ("    _gt_report()\n", "            _gt_xwin(det_logits[f_idx][0], c_src, f_idx, t_src)\n",
              "def _gt_gather(model_obj, feat_maps, rcoords, icoords, mask):\n"):
        need_once(patched, s, "patched predictor")
    if patched.count("_gt_gather(\n") != 4 or patched.count("model._index_features(\n") != 0:
        fail("gather routing count wrong")
    tree = ast.parse(patched)
    compile(tree, "patched_predictor", "exec")
    calls, idx_calls = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "_gt_gather":
                calls.append(node)
            if isinstance(node.func, ast.Attribute) and node.func.attr == "_index_features":
                idx_calls.append(node)
    got = {ast.unparse(c) for c in calls}
    if len(calls) != 4 or got != EXPECTED_CALLS:
        fail("gather call sites wrong: %s" % sorted(got))
    fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    g = fns["_gt_gather"]
    if [ast.unparse(c) for c in idx_calls] != ["model_obj._index_features(feat_maps, icoords, mask)"] or \
            not (g.lineno <= idx_calls[0].lineno <= g.end_lineno):
        fail("an _index_features call survives outside _gt_gather")
    pv = fns["predict_video"]
    lines = patched.splitlines()

    def line_of(s, lo, hi):
        hits = [i + 1 for i in range(lo - 1, hi) if lines[i] == s]
        if len(hits) != 1:
            fail("line %r found %d times in predict_video" % (s, len(hits)))
        return hits[0]
    lo, hi = pv.lineno, pv.end_lineno
    call_lines = sorted(c.lineno for c in calls)
    if not all(lo <= x <= hi for x in call_lines):
        fail("a gather call is outside predict_video")
    r_src = line_of("            p_rcoords_src = torch.from_numpy(", lo, hi)
    r_tgt = line_of("            p_rcoords_tgt = torch.from_numpy(", lo, hi)
    c_src = line_of("            c_src = coords_so_far[s_src:e_src]", lo, hi)
    xwin = line_of("            _gt_xwin(det_logits[f_idx][0], c_src, f_idx, t_src)", lo, hi)
    lcpr = line_of("        print('ARM_LCEFR pairs_refined=%d nodes_refined=%d diff_nodes=%d mean_abs_off_vox=%.4f'", lo, hi)
    rep = line_of("    _gt_report()", lo, hi)
    if not (c_src < xwin < r_src < r_tgt < call_lines[0]):
        fail("pair-loop order wrong (c_src %d xwin %d rsrc %d rtgt %d first gather %d)"
             % (c_src, xwin, r_src, r_tgt, call_lines[0]))
    if not (call_lines[-1] < lcpr < rep):
        fail("_gt_report is not after the ARM_LCEFR per-movie print")
    return {"gathers": call_lines, "xwin": xwin, "report": rep}


def check_runtime_asserts(block, real, pairs):
    """Mutation: remove or duplicate each anchor in a copy of REAL -> the block must raise at runtime."""
    n = 0
    for old, _new in pairs:
        for mutated, want in ((real.replace(old, "", 1), "matched 0 times"),
                              (real.replace(old, old + old, 1), "matched 2 times")):
            try:
                run_block(block, mutated)
            except RuntimeError as e:
                if "ARM_GTRI anchor" not in str(e) or want not in str(e):
                    fail("mutation raised the wrong error: %s" % e)
                n += 1
                continue
            fail("mutated anchor did NOT raise at runtime: %r" % old[:60])
    return n


def build_notebook(shared, block):
    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    for i, c in enumerate(cells):
        if c is not None and ("ARM_GTRI" in c or "_gt_gather" in c or "ARM_XENV tag=" + TAG in c):
            fail("base cell %d already carries gtri code" % i)
    c4 = cells[4]
    need_once(c4, shared.CELL4_ANCHOR, "cell-4 anchor (base)")
    if not shared.CELL4_ANCHOR.startswith("print('ARM_LCEFR"):
        fail("cell-4 anchor is not the top-level lcefr print")
    new4 = c4.replace(shared.CELL4_ANCHOR, shared.CELL4_ANCHOR + block, 1)
    need_once(new4, block, "block in cell 4")
    need_once(new4, Z_LINE, "z-only helper line in cell 4")
    for s in AXES_LINES:
        need_once(new4, s, "axes line in cell 4")
    a = new4.index(shared.CELL4_ANCHOR)
    b = new4.index("# ===== TRILINEAR UNet FEATURE GATHER")
    if not (a < b < new4.index("def list_test_stems()") < new4.index("subprocess.Popen(")):
        fail("block order wrong: must follow lcefr and precede the worker launch")
    if new4.replace(block, "", 1) != c4:
        fail("cell 4 change is not purely additive")
    cells[4] = new4
    cells[0] = cells[0].rstrip(NL) + NL + XENV + NL
    need_once(cells[0], "ARM_XENV tag=", "identity line in cell 0")
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (TAG, i), "exec")
    k = 0
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["source"] = cells[k].splitlines(keepends=True)
            c["outputs"] = []
            c["execution_count"] = None
        k += 1
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + TAG
    meta["title"] = "biohub v " + TAG
    return nb, meta, cells


def write_dir(dest, nb, meta):
    dest.mkdir(parents=True, exist_ok=True)
    with open(dest / "kernel.ipynb", "w", encoding="utf-8") as fh:
        json.dump(nb, fh)
    with open(dest / "kernel-metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)


def emit(dest, nb, meta):
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td) / "v"
        write_dir(tmp, nb, meta)
        if dest.exists():
            names = ("kernel.ipynb", "kernel-metadata.json")
            same = all((dest / f).is_file() and filecmp.cmp(tmp / f, dest / f, shallow=False) for f in names)
            if not same:
                raise SystemExit("BUILD_T6GTRIZ REFUSED: %s exists and differs from this build; existing v_ dirs are "
                                 "never modified (use --out NEWDIR)" % dest)
            return "IDENTICAL (existing dir byte-identical, nothing written)"
    write_dir(dest, nb, meta)
    return "WRITTEN"


# ----------------------------------------------------------------------------------------------------------
# --selftest: CPU emulation of the PATCHED predictor's own helper code (extracted from the patched text) with
# the REAL _index_features (train_unet_transformer.py), REAL _detect_cells_pooled and REAL SV soft-argmax.
# ----------------------------------------------------------------------------------------------------------
def selftest(patched, real):
    import numpy as np
    import torch
    import torch.nn.functional as F
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    out = {}

    def helper_ns(axes, lc_on=True, src=patched):
        seg = src[src.index("_GT_AXES = os.environ.get('BIOHUB_GTRI_AXES', '')\n"):src.index("def _detect_cells_pooled(\n")]
        ns = {"os": types.SimpleNamespace(environ={"BIOHUB_GTRI_AXES": axes}), "torch": torch, "F": F, "np": np,
              "_LC_ON": lc_on, "print": lambda *a, **k: out.setdefault("printed", []).append(" ".join(map(str, a)))}
        exec(compile(seg, "gt_helper", "exec"), ns)
        return ns

    train_src = TRAIN.read_text(encoding="utf-8")
    fdef = [n for n in ast.walk(ast.parse(train_src)) if isinstance(n, ast.FunctionDef) and n.name == "_index_features"]
    if len(fdef) != 1:
        fail("selftest: _index_features not found once in train_unet_transformer.py")
    ins = {"torch": torch}
    exec(textwrap.dedent(ast.get_source_segment(train_src, fdef[0])), ins)

    class Model:
        _index_features = ins["_index_features"]
    model = Model()

    rt = ast.parse(real)
    rns = {"torch": torch, "F": F, "np": np,
           "os": types.SimpleNamespace(environ={"BIOHUB_SUBVOXEL_SOFTARG": "1", "BIOHUB_SUBVOXEL_GAIN_MODE": "fixed",
                                                "BIOHUB_SUBVOXEL_GAIN_FIXED": "2.00", "BIOHUB_SUBVOXEL_CLIP": "0.4999",
                                                "BIOHUB_LINKER_REFINED_COORDS": "1"})}
    sv_seg = real[real.index("_SV_ON = os.environ.get('BIOHUB_SUBVOXEL_SOFTARG'"):real.index("def _detect_cells_pooled(\n")]
    exec(compile(sv_seg, "real_sv", "exec"), rns)
    det = [n for n in rt.body if isinstance(n, ast.FunctionDef) and n.name == "_detect_cells_pooled"][0]
    exec(compile(ast.Module(body=[det], type_ignores=[]), "real_det", "exec"), rns)

    C, Z, Y, X = 6, 9, 11, 13
    # T1: selfcheck + z-only semantics on random maps vs a numpy reference; y/x offsets must be ignored.
    ns = helper_ns("z")
    maps = torch.randn(1, C, Z, Y, X)
    n = 40
    ic = torch.stack([torch.randint(1, Z - 1, (n,)), torch.randint(1, Y - 1, (n,)), torch.randint(1, X - 1, (n,))], 1).float()[None]
    off = torch.from_numpy(rng.uniform(-0.4999, 0.4999, (1, n, 3)).astype(np.float32))
    rc = ic + off
    mask = torch.ones(1, n, dtype=torch.bool)
    got = ns["_gt_gather"](model, maps, rc, ic, mask)
    if ns["_GT_STATS"]["selfcheck"] != 1:
        fail("selftest T1: selfcheck did not run")
    m = maps[0].numpy()
    zr = rc[0, :, 0].numpy()
    z0 = np.floor(zr).astype(int)
    fz = zr - z0
    yi, xi = ic[0, :, 1].long().numpy(), ic[0, :, 2].long().numpy()
    ref = (1 - fz)[:, None] * m[:, z0, yi, xi].T + fz[:, None] * m[:, z0 + 1, yi, xi].T
    err1 = float(np.abs(got[0].numpy() - ref).max())
    rc2 = rc.clone()
    rc2[..., 1:] += 0.3 * torch.sign(torch.randn_like(rc2[..., 1:]))
    err_yx = float((ns["_gt_gather"](model, maps, rc2, ic, mask) - got).abs().max())
    if err1 > 1e-5 or err_yx != 0.0:
        fail("selftest T1: z-only lookup wrong (err %.2e, y/x sensitivity %.2e)" % (err1, err_yx))
    out["T1_zonly_vs_numpy_maxerr"] = err1
    out["T1_yx_offsets_ignored"] = err_yx == 0.0

    # T2: mean |feature delta| z vs zyx on random maps (the plan's 0.14 vs 0.26 claim), same inputs.
    nsz, nsa = helper_ns("z"), helper_ns("zyx")
    big = torch.randn(1, C, Z, Y, X)
    n2 = 400
    ic2 = torch.stack([torch.randint(1, Z - 1, (n2,)), torch.randint(1, Y - 1, (n2,)), torch.randint(1, X - 1, (n2,))], 1).float()[None]
    rc2 = ic2 + torch.from_numpy(rng.uniform(-0.4999, 0.4999, (1, n2, 3)).astype(np.float32))
    m2 = torch.ones(1, n2, dtype=torch.bool)
    for name, h in (("z", nsz), ("zyx", nsa)):
        h["_gt_gather"](model, big, rc2, ic2, m2)
        s = h["_GT_STATS"]
        out["T2_mean_abs_feat_delta_%s" % name] = round(s["sum_abs_delta"] / s["n_delta"], 4)

    # T3: zero offsets -> features identical -> NO-OP guard raises; bad env / lcefr off raise at import.
    ns0 = helper_ns("z")
    same = ns0["_gt_gather"](model, maps, ic.clone(), ic, mask)
    if not torch.equal(same, model._index_features(maps, ic, mask)):
        fail("selftest T3: integer coords did not reproduce the native gather")
    for fn, want in ((lambda: ns0["_gt_report"](), "ARM_GTRI NO-OP"),
                     (lambda: helper_ns("zy"), "bad BIOHUB_GTRI_AXES"),
                     (lambda: helper_ns("", ), "bad BIOHUB_GTRI_AXES"),
                     (lambda: helper_ns("z", lc_on=False), "needs lcefr")):
        try:
            fn()
        except RuntimeError as e:
            if want not in str(e):
                fail("selftest T3: wrong error %s" % e)
            continue
        fail("selftest T3: expected RuntimeError %r" % want)
    out["T3_noop_guard_and_env_guards_raise"] = True

    # T4: axis-order mutant of the helper must trip the SELFCHECK on the first call.
    mut = patched.replace("out += maps[:, loc[:, 0], loc[:, 1], loc[:, 2]].T", "out += maps[:, loc[:, 1], loc[:, 0], loc[:, 2]].T", 1)
    if mut == patched:
        fail("selftest T4: mutation anchor missing")
    nsm = helper_ns("z", src=mut)
    cube = torch.randn(1, C, 10, 10, 10)
    icc = torch.randint(1, 9, (1, 30, 3)).float()
    try:
        nsm["_gt_gather"](model, cube, icc + 0.2, icc, torch.ones(1, 30, dtype=torch.bool))
    except RuntimeError as e:
        if "SELFCHECK FAILED" not in str(e):
            fail("selftest T4: wrong error %s" % e)
        out["T4_axis_swap_mutant_trips_selfcheck"] = True
    else:
        fail("selftest T4: axis-swapped helper passed the selfcheck")

    # T5: REAL chain. Gaussian blobs at sub-voxel z -> REAL _detect_cells_pooled -> REAL SV offsets (gain 2,
    # clip 0.4999) -> tensors built exactly like the predictor (p_coords / p_rcoords) -> _gt_gather on a map
    # that is LINEAR in z (a_c*z + b_c*y + c_c*x + d_c): trilinear is exact on linear fields, so the gathered
    # feature decodes to (refined z, integer y, integer x).
    Zs, Ys, Xs = 12, 24, 24
    zz, yy, xx = np.meshgrid(np.arange(Zs), np.arange(Ys), np.arange(Xs), indexing="ij")
    centers = [(3.3, 5, 6), (6.7, 16, 7), (8.45, 8, 17), (4.9, 18, 18)]
    lg = np.full((Zs, Ys, Xs), -6.0, dtype=np.float32)
    for cz, cy, cx in centers:
        lg = np.maximum(lg, 6.0 - 1.5 * ((zz - cz) ** 2 + 0.5 * (yy - cy) ** 2 + 0.5 * (xx - cx) ** 2)).astype(np.float32)
    lg_t = torch.from_numpy(lg)[None]  # (1, Z, Y, X) == det_logits[f_idx][0]
    arr = rns["_detect_cells_pooled"](lg_t, 5, 0.5, (3, 3, 3))
    offs = rns["_sv_softarg_offsets"](lg_t, arr)
    if len(arr) != len(centers):
        fail("selftest T5: detector found %d peaks, expected %d" % (len(arr), len(centers)))
    r = arr.astype(np.float32)
    r[:, 1:] += offs
    p_coords = torch.from_numpy(arr[:, 1:].astype(np.float32)).unsqueeze(0)
    p_rcoords = torch.from_numpy(np.ascontiguousarray(r[:, 1:], dtype=np.float32)).unsqueeze(0)
    a = torch.tensor([1.0, 2.0, -1.5]); b = torch.tensor([0.25, 0.0, 0.5]); c = torch.tensor([0.0, -0.75, 0.1])
    d = torch.tensor([3.0, -1.0, 0.0])
    Zg, Yg, Xg = torch.meshgrid(torch.arange(Zs).float(), torch.arange(Ys).float(), torch.arange(Xs).float(), indexing="ij")
    lin = (a[:, None, None, None] * Zg + b[:, None, None, None] * Yg + c[:, None, None, None] * Xg + d[:, None, None, None])[None]
    ns5 = helper_ns("z")
    feats = ns5["_gt_gather"](model, lin, p_rcoords, p_coords, torch.ones(1, len(arr), dtype=torch.bool))[0]
    want = (a[None] * p_rcoords[0, :, :1] + b[None] * p_coords[0, :, 1:2] + c[None] * p_coords[0, :, 2:3] + d[None])
    err5 = float((feats - want).abs().max())
    if err5 > 1e-4:
        fail("selftest T5: gathered features != linear field at (refined z, integer y/x): %.2e" % err5)
    true_z = np.array(sorted(cz for cz, _, _ in centers))
    order = np.argsort(arr[:, 1])
    out["T5_real_chain_maxerr"] = err5
    out["T5_peak_z"] = arr[order, 1].tolist()
    out["T5_refined_z"] = [round(float(v), 4) for v in r[order, 1]]
    out["T5_true_z"] = true_z.tolist()
    out["T5_z_offsets_nonzero"] = int((np.abs(offs[:, 0]) > 0).sum())
    ns5["_gt_report"]()
    out["T5_marker"] = [p for p in out.get("printed", []) if p.startswith("ARM_GTRI_STATS")][-1]

    # T6: cross-window diagnostic counts = brute force (only f_idx == 0 and t_src > 0 count).
    ns6 = helper_ns("z")
    c_src = np.concatenate([arr, np.array([[5, 3, 5, 7], [5, 6, 16, 9]], dtype=np.int16)])  # 4 peaks + 2 slope points
    ns6["_gt_xwin"](lg_t, c_src, 1, 5)
    ns6["_gt_xwin"](lg_t, c_src, 0, 0)
    ns6["_gt_xwin"](lg_t, c_src, 0, 5)
    pooled = F.max_pool3d(lg_t[None].float(), 3, stride=1, padding=1)[0, 0].numpy()
    bf = int(sum(lg[z, y, x] < pooled[z, y, x] for _, z, y, x in c_src))
    if (ns6["_GT_STATS"]["xwin_src"], ns6["_GT_STATS"]["xwin_off"]) != (len(c_src), bf) or bf != 2:
        fail("selftest T6: XWIN %s vs brute force %d/%d" % (ns6["_GT_STATS"], len(c_src), bf))
    out["T6_xwin"] = (ns6["_GT_STATS"]["xwin_src"], ns6["_GT_STATS"]["xwin_off"])
    out.pop("printed", None)
    return out


def main():
    args = sys.argv[1:]
    dest = DEST
    if "--out" in args:
        dest = pathlib.Path(args[args.index("--out") + 1]).resolve()
    shared = load_shared()
    block = shared.build_block(AXES)
    if "__AXES__" in block or "try:" in block or "except" in block:
        fail("block has an unresolved placeholder or a try/except")
    for s in AXES_LINES:
        need_once(block, s, "axes line in block")
    need_once(block, Z_LINE, "z-only helper line in block")

    real = REAL.read_text(encoding="utf-8")
    base_c4 = "".join(json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))["cells"][4]["source"])
    n_lc = check_provenance(real, base_c4)
    patched, pairs = run_block(block, real)
    info = check_patched(real, patched, pairs)
    n_mut = check_runtime_asserts(block, real, pairs)
    nb, meta, cells = build_notebook(shared, block)
    status = emit(dest, nb, meta)
    print("ARM t6gtriz | base %s | REAL %s (sha ok, SV helper + %d lcefr replacements present)" % (BASE.name, REAL, n_lc))
    print("anchors: cell-4 x1 | predictor x%d each exactly once (static) and via the runtime logic | "
          "mutations raising at runtime: %d/%d" % (len(pairs), n_mut, 2 * len(pairs)))
    print("patched predictor compiles | gathers at lines %s | xwin line %d | report line %d"
          % (info["gathers"], info["xwin"], info["report"]))
    print("cells compiled: %d | kernel id %s | %s -> %s" % (sum(c is not None for c in cells), meta["id"], status, dest))
    if "--selftest" in args:
        res = selftest(patched, real)
        for k in sorted(res):
            print("SELFTEST", k, "=", res[k])
        print("SELFTEST PASS")


if __name__ == "__main__":
    main()
