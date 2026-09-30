#!/usr/bin/env python3
"""t6svyx: our 0.954 t6stk3 body with the sub-voxel soft-argmax applied to y/x ONLY (z offsets zeroed).
lcefr, gain 2.00, clip 0.4999, velocity 0.25, bonus 1.6, TIGHT 6.0: all unchanged. The exact MIRROR of ourvz
(which keeps SV z and hands y/x to V1284).

usage: python scratch_kernels/build_svyx.py <tag>

WHY. ourvz's run log (SV_ARM_HSG200 with y/x zeroed) decomposes t6stk3's refinement by axis for the first time:
z-only mean |offset| 0.336/0.312/0.318/0.340 grid units vs 0.14-0.28 per y/x axis, and ~41% of z offsets sit at
the 0.4999 clip vs ~14% for y/x. So z is the largest and most saturated component of our shift, while the
GT-trained V1284 head (same detector, same neighbourhood features) learned essentially NO z shift (44b6: z .754
zero-shift vs .762 with the head). If the z channel is noise, removing it is the one cheap arm with a path ABOVE
0.954; if it is real, this reads 0.951-0.953 and ourvz reads the complement. Either way the pair {ourvz, t6svyx}
decomposes the z channel on the board, which the 09-26 slate needs.

Mechanics (inside the predictor script that cell 4 patches):
  * `_sv_softarg_offsets` zeroes column 0 (z) of the gained offsets when BIOHUB_SUBVOXEL_YXONLY=1, BEFORE the
    clip; `_sv_refine_lists` therefore carries y/x-only offsets, so BOTH the written coordinates and lcefr's
    refined linker inputs see the same y/x-only geometry (no new code path, a strict subset of t6stk3's);
  * the final assembly prints ARM_SV_YXONLY_AXES with the realised z and y/x mean |offset| computed from the
    concatenated offsets themselves, so the gate can pin z_mean_abs=0.0000 from the predictor's own numbers;
  * every anchor is checked to match exactly once in the cell-4 source AND (predictor-level form) in the real
    patched predictor from data/out_t6stk3/tracking_repo, and the patched predictor must compile.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
REAL_PRED = ROOT / "data" / "out_t6stk3" / "tracking_repo" / "scripts" / "predict_unet_transformer.py"
Q = chr(34)
NL = chr(10)
BS = chr(92)
LN = BS + "n"   # the two characters backslash-n as they appear inside the cell-4 string literals

# 1. helper (lives inside the triple-quoted _SV_HELPER string, so the cell source is the literal text)
SV_RET_OLD = "    sa = sa * _sv_gain()\n    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n"
SV_RET_NEW = ("    sa = sa * _sv_gain()\n"
              "    if os.environ.get('BIOHUB_SUBVOXEL_YXONLY', '0') != '0':\n"
              "        sa[:, 0] = 0.0\n"
              "    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n")
# 2. env + marker, right after the clip env line
SV_ENV_OLD = "os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"
SV_ENV_NEW = ("os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"
              "os.environ['BIOHUB_SUBVOXEL_YXONLY'] = '1'\n"
              "print('ARM_SV_YXONLY=1 (sub-voxel z offsets zeroed, y/x kept at gain 2.00 clip 0.4999)', flush=True)\n")
# 3. assembly print: one more adjacent string literal after the SV_ARM_HSG200 print inside _sv_pairs
PR_LINE = ("        print('SV_ARM_HSG200 nodes=%d mean_abs_off_vox=%.4f frac_clipped=%.4f gain=%.2f' % "
           "(coords.shape[0], _SV_STATS['mean_abs_off'], _SV_STATS['frac_clipped'], _sv_gain()), flush=True)")
AX_LINE = ("        print('ARM_SV_YXONLY_AXES z_mean_abs=%.4f yx_mean_abs=%.4f z_nonzero=%d' % "
           "(float(np.abs(_sv_off[:, 0]).mean()), float(np.abs(_sv_off[:, 1:]).mean()), "
           "int((_sv_off[:, 0] != 0).sum())), flush=True)")
PR_OLD = "     " + Q + PR_LINE + LN + Q + NL
PR_NEW = PR_OLD + "     " + Q + AX_LINE + LN + Q + NL
# predictor-level forms of the same edits (what the kernel writes into the script)
P_PR_OLD = PR_LINE + NL
P_PR_NEW = PR_LINE + NL + AX_LINE + NL


def code_cells(path):
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1]
    nb, cells = code_cells(BASE / "kernel.ipynb")
    c4 = cells[4]
    for a in (SV_RET_OLD, SV_ENV_OLD, PR_OLD):
        if c4.count(a) != 1:
            raise SystemExit("cell-4 anchor %r matched %d" % (a[:60], c4.count(a)))
    if "BIOHUB_SUBVOXEL_YXONLY" in c4 or "BIOHUB_SUBVOXEL_ZONLY" in c4:
        raise SystemExit("base already carries an axis switch")
    c4 = c4.replace(SV_RET_OLD, SV_RET_NEW, 1).replace(SV_ENV_OLD, SV_ENV_NEW, 1).replace(PR_OLD, PR_NEW, 1)
    for must in ("SV_ARM_HSG200", "# ===== LINKER READS THE REFINED COORDINATES (arm lcefr) =====",
                 "ARM_LCEFR patch applied to"):
        if must not in c4:
            raise SystemExit("assembly check failed: %s missing" % must)
    if c4.count("ARM_SV_YXONLY_AXES") != 1 or c4.count("sa[:, 0] = 0.0") != 1:
        raise SystemExit("edit count check failed")
    cells[4] = c4
    ident = 'print(' + Q + 'ARM_XENV tag=%s SUBVOXEL=yx-only LCEFR=kept GAIN=2.00 CLIP=0.4999' % tag + Q + ', flush=True)'
    cells[0] = cells[0].rstrip(NL) + NL + ident + NL
    for k2, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, k2), "exec")
    # the helper string must compile as written and carry the switch
    hs = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    helper = c4[hs:c4.index('"""', hs)]
    compile(helper, "sv_helper", "exec")
    if "BIOHUB_SUBVOXEL_YXONLY" not in helper:
        raise SystemExit("helper y/x-only patch missing")
    # the _sv_pairs replacement text must still be valid Python when written into the predictor: replay the
    # predictor-level edits on the REAL patched predictor from the t6stk3 run and compile it
    if REAL_PRED.exists():
        ps = REAL_PRED.read_text(encoding="utf-8")
        for a in (SV_RET_OLD, P_PR_OLD):
            if ps.count(a) != 1:
                raise SystemExit("predictor-level anchor %r matched %d in the real t6stk3 predictor" % (a[:60], ps.count(a)))
        ps2 = ps.replace(SV_RET_OLD, SV_RET_NEW, 1).replace(P_PR_OLD, P_PR_NEW, 1)
        compile(ps2, str(REAL_PRED), "exec")
        # lcefr's own anchors (pair 1 and pair 9) must survive untouched around the new line
        for a in ("_SV_STATS = {'nodes': 0, 'mean_abs_off': 0.0, 'frac_clipped': 0.0}\n",
                  "    coords[:, 1:] *= ds_arr\n    if not _SV_ON:\n        coords = coords.astype(np.int16)\n"):
            if ps2.count(a) != 1:
                raise SystemExit("lcefr anchor %r no longer matches once after the edit" % a[:50])
        print("real-predictor replay: anchors 1x, compiles, lcefr anchors intact")
    else:
        print("WARNING: real predictor not found, predictor-level replay skipped")

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
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest, "| datasets", meta["dataset_sources"])


if __name__ == "__main__":
    main()
