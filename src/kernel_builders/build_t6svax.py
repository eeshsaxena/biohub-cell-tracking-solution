#!/usr/bin/env python3
"""t6stk3 body with PER-AXIS multipliers on the sub-voxel soft-argmax offsets (z, y, x), lcefr kept.

usage: python scratch_kernels/build_t6svax.py <tag> --z <gz> --yx <gyx>

The multipliers apply ON TOP of the shipped gain 2.00 and BEFORE the clip 0.4999, so:
  --z 0    --yx 1     = t6svyx (sub-voxel y/x only, z zeroed)         [t6svyx itself was hand-built by the
                                                                          09-25 workflow; this reproduces its effect]
  --z 0.5  --yx 1     = z at effective gain 1.0, y/x at 2.0
  --z 0    --yx 1.25  = y/x at effective gain 2.5, z off
  --z 1    --yx 1     = t6stk3 (identity; do not submit)

WHY. The board's sub-voxel curve (0.946 -> 0.951 at gain 2.0) was measured with ONE gain for all axes. The
09-25 per-axis analysis showed the GT-trained V1284 head learned no z shift at all, 41% of our z offsets sit at
the clip (vs 14% for y/x), and the "more z" arm hsgzc10 read below the curve. So the z channel may be neutral or
harmful; t6svyx (z = 0) tests that, and these variants map the axis-split if it pays.
Runtime markers: ARM_SV_AXES zyx_gain=gz,gy,gx (cell 4) and ARM_SV_AXES_STATS z_mean_abs= yx_mean_abs= z_nonzero=
(predictor), plus the unchanged SV_ARM_HSG200 line. Fails loudly if any anchor does not match exactly once.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
NL = chr(10)

ENV_OLD = "os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"
HELPER_OLD = "    sa = sa * _sv_gain()\n    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n"
HELPER_NEW = ("    sa = sa * _sv_gain()\n"
              "    sa = sa * np.array([float(v) for v in os.environ.get('BIOHUB_SUBVOXEL_AXIS_GAIN_ZYX', '1,1,1').split(',')], dtype=np.float64)\n"
              "    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n")
PRINT_OLD = ("     \"        print('SV_ARM_HSG200 nodes=%d mean_abs_off_vox=%.4f frac_clipped=%.4f gain=%.2f' % (coords.shape[0], _SV_STATS['mean_abs_off'], _SV_STATS['frac_clipped'], _sv_gain()), flush=True)\\n\"\n")
PRINT_NEW = (PRINT_OLD +
             "     \"        print('ARM_SV_AXES_STATS z_mean_abs=%.4f yx_mean_abs=%.4f z_nonzero=%d' % (float(np.abs(_sv_off[:, 0]).mean()), float(np.abs(_sv_off[:, 1:]).mean()), int((_sv_off[:, 0] != 0).sum())), flush=True)\\n\"\n")


def main():
    tag = sys.argv[1]
    args = sys.argv[2:]
    gz = float(args[args.index("--z") + 1])
    gyx = float(args[args.index("--yx") + 1])
    if not (0.0 <= gz <= 2.0 and 0.0 <= gyx <= 2.0):
        raise SystemExit("multipliers must be in [0, 2]")
    zyx = "%g,%g,%g" % (gz, gyx, gyx)
    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    c4 = cells[4]
    for a in (ENV_OLD, HELPER_OLD, PRINT_OLD):
        if c4.count(a) != 1:
            raise SystemExit("anchor %r matched %d times" % (a[:60], c4.count(a)))
    c4 = c4.replace(ENV_OLD, ENV_OLD + "os.environ['BIOHUB_SUBVOXEL_AXIS_GAIN_ZYX'] = '%s'\n" % zyx
                    + "print('ARM_SV_AXES zyx_gain=%s (multipliers on the gain-2.00 sub-voxel offsets, before the 0.4999 clip)', flush=True)\n" % zyx, 1)
    c4 = c4.replace(HELPER_OLD, HELPER_NEW, 1).replace(PRINT_OLD, PRINT_NEW, 1)
    cells[4] = c4
    cells[0] = cells[0].rstrip(NL) + NL + 'print("ARM_XENV tag=%s SUBVOXEL=axes zyx_gain=%s LCEFR=kept GAIN=2.00 CLIP=0.4999", flush=True)' % (tag, zyx) + NL
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    hs = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    helper = c4[hs:c4.index('"""', hs)]
    compile(helper, "sv_helper", "exec")
    if "BIOHUB_SUBVOXEL_AXIS_GAIN_ZYX" not in helper:
        raise SystemExit("helper patch missing")
    # the replacement pair for the final assembly is a string literal inside cell 4; make sure it still parses
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
    print("built", dest, "| zyx multipliers", zyx)


if __name__ == "__main__":
    main()
