#!/usr/bin/env python3
"""xpubz: the PUBLIC x138 body run as published (flow relink + readmit + gap filler, V1284 head for y/x), with the
head's z replaced by our sub-voxel z, fed to the per-frame detections exactly as ourvzl does on our body.

usage: python scratch_kernels/build_xpubz.py [tag]        (default tag: xpubz)

WHY. xpub (the public notebook verbatim) = 0.953, shared by ~220 teams. The public V1284 head moves z (mean |z| 0.37
voxel, 29% of written z changed) without making z more accurate (per-axis table in build_ourvz.py), while our
sub-voxel z is the largest measured lever on our own body (t6stk3 0.954 vs t6svyx 0.948). This arm changes ONLY the
coordinate head on the x138 body: y/x from V1284 (unchanged), z from the sub-voxel soft-argmax (gain 2.00, clip
0.4999) added to `arr` right after V1284 (so the edge model's positional/geometry inputs read refined z), V1284's
trilinear gather rounded back to the integer z peak (GATHER_INT_Z, lcefr analogue). Everything else - cells 0-3,
5-11, x138's env, readmit, gap filler, flow relink, bonus 1.0, TIGHT 5.5 - is the public notebook byte for byte.
It cannot tie the x138 block: the edge model's inputs change, so the ILP output changes.

Composition, no new mechanism: the sub-voxel block is t6stk3's (byte for byte, as in xsv/xsvf on this body) with
build_ourvz.py's ZONLY edits and build_ourvzl.py's Z_TO_ARR/GATHER_INT_Z env lines; it is placed immediately BEFORE
x138's V1284 block (the slot xsv/xsvf used, i.e. after readmit's low-detection dump patch, whose anchors it must not
disturb). The V1284 block gets build_ourvz.py's two edits (z shift zeroed in the module; the int16 anchor replaced by
a `pass` so it stays valid inside the sub-voxel `if not _SV_ON:` branch) and its module check; build_ourvzl.py's
rendered patch block follows it. Every anchor/constant is imported from those two builders, not re-typed.
"""
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
SRC_X = SK / "_pub0924" / "anvithpothula_biohub-x138" / "biohub-x138.ipynb"
SRC_OURS = SK / "v_t6stk3" / "kernel.ipynb"
META_BASE = SK / "v_xpub" / "kernel-metadata.json"
NL = chr(10)
Q = chr(34)

SV_START = "# ===== SUB-VOXEL SOFT-ARGMAX REFINEMENT (sweep0911 surviving lever #2) ====="
SV_END = "print('SUBVOXEL patch applied to', _ps, flush=True)"
V_START = "# --------------------------------- V1284 head, AFTER readmit's low-detection dump patch"
V_END = "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])"
LOWDET_TAIL = 'print("Low-detection dump disabled (BIOHUB_CACHE_DIR unset)")'


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SK / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def code_cells(path):
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        raise SystemExit("%s anchor matched %d times (need 1): %r" % (what, n, old[:70]))
    return text.replace(old, new, 1)


def compose_cell4(x4, o4, bz, bzl):
    """x138 cell 4 -> xpubz cell 4. Returns (new cell 4, sv block, v block, zta block)."""
    # 1. our sub-voxel block (t6stk3, byte for byte) + ZONLY (build_ourvz) + Z_TO_ARR/GATHER_INT_Z env (build_ourvzl)
    i, j = o4.index(SV_START), o4.index(SV_END) + len(SV_END)
    sv = o4[i:j]
    sv = once(sv, bz.SV_RET_OLD, bz.SV_RET_NEW, "sv helper ZONLY")
    sv = once(sv, bz.SV_ENV_OLD, bz.SV_ENV_NEW, "sv env ZONLY")
    sv = once(sv, bzl.ENV_ANCHOR, bzl.ENV_NEW, "sv env Z_TO_ARR")
    # 2. x138's own V1284 block with build_ourvz's two edits + its module check
    vi, vj = x4.index(V_START), x4.index(V_END) + len(V_END)
    vb = x4[vi:vj]
    vb = once(vb, bz.V_REPL_OLD, bz.V_REPL_NEW, "V1284 int16->pass")
    vb = once(vb, bz.MOD_SHIFT_OLD, bz.MOD_SHIFT_NEW, "V1284 module z-zero")
    vb += (NL + "_v1284yx_src = (_ps.parent/'v1284_coordinate_refinement.py').read_text()" + NL
           + "if _v1284yx_src.count('shift[:, 0] = 0.0') != 1: raise RuntimeError('V1284_YX module patch missing')" + NL
           + "print('ARM_V1284_YX module_patched=1', flush=True)" + NL)
    if not vb.endswith(bzl.BLOCK_ANCHOR):
        raise SystemExit("V1284 block does not end with ourvzl's BLOCK_ANCHOR")
    # 3. ourvzl's rendered patch block (predictor P1-P4 + module gather-int-z, runtime-asserted)
    zta = bzl.render_block()
    # 4. splice: [x138 up to V1284] + sv + [V1284 block] + zta + [x138 after V1284]
    head, tail = x4[:vi], x4[vj:]
    if LOWDET_TAIL not in head:
        raise SystemExit("low-detection dump block is not before the V1284 slot")
    new4 = head + sv + NL + NL + NL + vb + NL + zta + tail
    # 5. structure checks
    for a, n in [(SV_START, 1), (SV_END, 1), (V_START, 1), (V_END, 1), (bzl.BLOCK_ANCHOR, 1),
                 ("# ===== SUB-VOXEL Z INTO THE PER-FRAME DETECTIONS (arm ourvzl) =====", 1),
                 ("os.environ['BIOHUB_SUBVOXEL_ZONLY'] = '1'", 1), ("os.environ['BIOHUB_SUBVOXEL_Z_TO_ARR'] = '1'", 1),
                 ("os.environ['BIOHUB_V1284_GATHER_INT_Z'] = '1'", 1), ("LINKER READS THE REFINED COORDINATES", 0),
                 ("_LC_ON", 0)]:
        if new4.count(a) != n:
            raise SystemExit("cell-4 count of %r is %d (need %d)" % (a[:60], new4.count(a), n))
    order = [new4.index(LOWDET_TAIL), new4.index(SV_START), new4.index(SV_END), new4.index(V_START),
             new4.index(V_END), new4.index(bzl.BLOCK_ANCHOR), new4.index("# ===== SUB-VOXEL Z INTO THE PER-FRAME"),
             new4.index("start_time = time.time()")]
    if order != sorted(order):
        raise SystemExit("cell-4 order check failed: %r" % order)
    # everything outside the three inserted/edited blocks must be x138's bytes
    if new4[:vi] != x4[:vi] or not new4.endswith(tail):
        raise SystemExit("x138 cell 4 outside the head slot was modified")
    return new4, sv, vb, zta


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "xpubz"
    bz, bzl = _load("build_ourvz"), _load("build_ourvzl")
    nb, xc = code_cells(SRC_X)
    _, oc = code_cells(SRC_OURS)
    new4, sv, vb, zta = compose_cell4(xc[4], oc[4], bz, bzl)
    # the sub-voxel block must be t6stk3's except for the three documented edits
    base_sv = oc[4][oc[4].index(SV_START): oc[4].index(SV_END) + len(SV_END)]
    if sv.replace(bzl.ENV_NEW, bzl.ENV_ANCHOR).replace(bz.SV_ENV_NEW, bz.SV_ENV_OLD).replace(bz.SV_RET_NEW, bz.SV_RET_OLD) != base_sv:
        raise SystemExit("sub-voxel block differs from t6stk3's beyond the ZONLY/Z_TO_ARR edits")
    # the helper string and the V1284 module string must compile as they will be written
    hs = sv.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    compile(sv[hs: sv.index('"""', hs)], "sv_helper", "exec")
    ms = vb.index("write_text('") + len("write_text(")
    me = vb.index("')" + NL, ms) + 1
    module_src = eval(vb[ms:me])
    compile(module_src, "v1284_coordinate_refinement.py", "exec")
    if module_src.count("shift[:, 0] = 0.0") != 1:
        raise SystemExit("module z-zero patch missing")

    cells = list(xc)
    cells[4] = new4
    ident = ('print(' + Q + 'ARM_XENV tag=%s BODY=x138 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx' % tag
             + Q + ', flush=True)')
    cells[0] = cells[0].rstrip(NL) + NL + ident + NL
    for k2, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, k2), "exec")
    for k2 in range(len(cells)):
        if k2 not in (0, 4) and cells[k2] != xc[k2]:
            raise SystemExit("cell %d differs from the public notebook" % k2)

    k = 0
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["source"] = cells[k].splitlines(keepends=True)
            c["outputs"] = []
            c["execution_count"] = None
        k += 1
    dest = SK / ("v_" + tag)
    dest.mkdir(parents=True, exist_ok=True)
    json.dump(nb, open(dest / "kernel.ipynb", "w", encoding="utf-8"))
    meta = json.loads(META_BASE.read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    if "anvithpothula/biohub-v1284-head-s075" not in meta["dataset_sources"]:
        raise SystemExit("V1284 head dataset missing from the x138 metadata")
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest, "| datasets", meta["dataset_sources"])
    print("cell 4: x138 %d -> %d chars (sv %d, v1284 %d, zta %d)" % (len(xc[4]), len(new4), len(sv), len(vb), len(zta)))


if __name__ == "__main__":
    main()
