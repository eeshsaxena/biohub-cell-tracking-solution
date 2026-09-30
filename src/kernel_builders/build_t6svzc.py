#!/usr/bin/env python3
"""t6stk3 body with a PER-AXIS CLIP on the sub-voxel soft-argmax offsets (optionally with build_t6svax-style per-axis
gain multipliers), lcefr kept.

usage: python scratch_kernels/build_t6svzc.py <tag> --zclip <cz> [--yxclip <cyx>] [--z <gz_mult>] [--yx <gyx_mult>]

  --zclip 0.40                 = t6stk3 with the z offsets clipped at +-0.40 grid voxel (y/x untouched)  [tag t6svzc40]
  --zclip 0.35                 = same at +-0.35
  --zclip 0.40 --yxclip 0.40   = all axes clipped at +-0.40
  --z 1.25 --zclip 0.40        = z gain 2.5 with z clip 0.40
Multipliers apply ON TOP of the shipped gain 2.00 (as in build_t6svax.py); the per-axis clip is applied after the
existing scalar 0.4999 clip, so every offset stays strictly < 0.5 voxel and the integer-peak invariant the kernel
relies on (rounding a refined coordinate returns the peak) still holds. Clips must lie in [0.20, 0.4999].

WHY (wf7 screen, scratchpad/wf7/screen/screen*.py): on the offline proxy (fraction of GT edges with 3-D displacement
error > 3 um, primary TTA logits on the v1284cap features), tightening the z clip from 0.4999 to 0.35-0.40 is the only
change that lowers the error fraction on BOTH embryos in all four metric variants (gate-3/gate-5 edges x
scaled/unscaled offsets). Size: +0.3 tick (gate-5 scaled, the calibration's preferred metric) to +0.8-1.1 tick
(gate-3), i.e. BELOW the proxy's +-1.5 tick resolution. The clip axis is also where the proxy was least calibrated on
the board (hsg2c10 / hsgzc10 residuals of opposite sign). Treat as a low-confidence arm.

Runtime markers: ARM_XENV tag=... clip_zyx=..., ARM_SV_AXES zyx_gain=... clip_zyx=..., ARM_SV_AXES_STATS (as
t6svax) and ARM_SV_ZCLIP_STATS z_clip= z_mean_abs= z_frac_at_clip=, plus the unchanged SV_ARM_HSG200 line (its
frac_clipped still counts offsets at the scalar 0.4999 clip, so it DROPS for z when the z clip is tighter).
The builder unit-tests the patched helper against the t6stk3 helper on a synthetic logit volume.
"""
import json
import os
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
NL = chr(10)

ENV_OLD = "os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"
HELPER_OLD = "    sa = sa * _sv_gain()\n    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n"
HELPER_NEW = ("    sa = sa * _sv_gain()\n"
              "    sa = sa * np.array([float(v) for v in os.environ.get('BIOHUB_SUBVOXEL_AXIS_GAIN_ZYX', '1,1,1').split(',')], dtype=np.float64)\n"
              "    sa = np.clip(sa, -_SV_CLIP, _SV_CLIP)\n"
              "    _cl = np.minimum(np.array([float(v) for v in os.environ.get('BIOHUB_SUBVOXEL_CLIP_ZYX', '0.4999,0.4999,0.4999').split(',')], dtype=np.float64), _SV_CLIP)\n"
              "    return np.clip(sa, -_cl, _cl).astype(np.float32)\n")
PRINT_OLD = ("     \"        print('SV_ARM_HSG200 nodes=%d mean_abs_off_vox=%.4f frac_clipped=%.4f gain=%.2f' % (coords.shape[0], _SV_STATS['mean_abs_off'], _SV_STATS['frac_clipped'], _sv_gain()), flush=True)\\n\"\n")
PRINT_NEW = (PRINT_OLD +
             "     \"        print('ARM_SV_AXES_STATS z_mean_abs=%.4f yx_mean_abs=%.4f z_nonzero=%d' % (float(np.abs(_sv_off[:, 0]).mean()), float(np.abs(_sv_off[:, 1:]).mean()), int((_sv_off[:, 0] != 0).sum())), flush=True)\\n\"\n"
             "     \"        print('ARM_SV_ZCLIP_STATS z_clip=%.4f z_mean_abs=%.4f z_frac_at_clip=%.4f yx_max_abs=%.4f' % (float(os.environ.get('BIOHUB_SUBVOXEL_CLIP_ZYX', '0.4999,0.4999,0.4999').split(',')[0]), float(np.abs(_sv_off[:, 0]).mean()), float((np.abs(_sv_off[:, 0]) >= float(os.environ.get('BIOHUB_SUBVOXEL_CLIP_ZYX', '0.4999,0.4999,0.4999').split(',')[0]) - 1e-6).mean()), float(np.abs(_sv_off[:, 1:]).max()) if len(_sv_off) else 0.0), flush=True)\\n\"\n")


def _arg(args, name, default):
    return float(args[args.index(name) + 1]) if name in args else default


def _helper_src(c4):
    hs = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    return c4[hs:c4.index('"""', hs)]


def _run_helper(src, env, lg, arr):
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        ns = {"np": np, "os": os}
        exec(compile(src, "sv_helper", "exec"), ns)
        return ns["_sv_softarg_offsets"](lg, arr)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def unit_test(base_helper, new_helper, gz, gyx, cz, cyx):
    rng = np.random.default_rng(0)
    lg = rng.normal(0, 1.5, (12, 40, 40)).astype(np.float32)
    arr = np.stack([np.zeros(600, int), rng.integers(0, 12, 600), rng.integers(0, 40, 600), rng.integers(0, 40, 600)], 1)
    env0 = {"BIOHUB_SUBVOXEL_SOFTARG": "1", "BIOHUB_SUBVOXEL_GAIN_MODE": "fixed", "BIOHUB_SUBVOXEL_GAIN_FIXED": "2.00",
            "BIOHUB_SUBVOXEL_CLIP": "0.4999"}
    ref = _run_helper(base_helper, env0, lg, arr).astype(np.float64)
    # reference with the gain multipliers but NO per-axis clip: recompute from an unclipped base (gain 1, clip 9)
    raw = _run_helper(base_helper, dict(env0, BIOHUB_SUBVOXEL_GAIN_FIXED="1.00", BIOHUB_SUBVOXEL_CLIP="9"), lg, arr).astype(np.float64)
    want = np.clip(np.clip(raw * 2.0 * np.array([gz, gyx, gyx]), -0.4999, 0.4999), -np.array([cz, cyx, cyx]), np.array([cz, cyx, cyx]))
    got = _run_helper(new_helper, dict(env0, BIOHUB_SUBVOXEL_AXIS_GAIN_ZYX="%g,%g,%g" % (gz, gyx, gyx),
                                       BIOHUB_SUBVOXEL_CLIP_ZYX="%g,%g,%g" % (cz, cyx, cyx)), lg, arr).astype(np.float64)
    assert np.abs(got - want).max() < 1e-5, ("helper mismatch", np.abs(got - want).max())
    assert np.abs(got[:, 0]).max() <= cz + 1e-6 and np.abs(got[:, 1:]).max() <= cyx + 1e-6 and np.abs(got).max() < 0.5
    if gz == 1 and gyx == 1:
        assert np.abs(got[:, 1:] - ref[:, 1:]).max() < 1e-6 if cyx >= 0.4999 else True, "y/x changed although only z is clipped"
        assert np.abs(got[:, 0] - np.clip(ref[:, 0], -cz, cz)).max() < 1e-6, "z != clip(t6stk3 z)"
    # identity: default env (no per-axis clip) reproduces t6stk3 bit-for-bit
    ident = _run_helper(new_helper, dict(env0, BIOHUB_SUBVOXEL_AXIS_GAIN_ZYX="1,1,1", BIOHUB_SUBVOXEL_CLIP_ZYX="0.4999,0.4999,0.4999"), lg, arr)
    assert np.array_equal(ident, ref.astype(np.float32)), "identity settings do not reproduce t6stk3"
    frac = float(np.mean(np.abs(got[:, 0]) >= cz - 1e-6))
    print("unit test ok | synthetic z frac at clip %.3f (t6stk3 %.3f) | max|off| %.4f" % (frac, float(np.mean(np.abs(ref[:, 0]) >= 0.4999 - 1e-6)), float(np.abs(got).max())))


def main():
    tag = sys.argv[1]
    args = sys.argv[2:]
    if "--zclip" not in args:
        raise SystemExit("--zclip is required")
    cz = _arg(args, "--zclip", 0.4999)
    cyx = _arg(args, "--yxclip", 0.4999)
    gz = _arg(args, "--z", 1.0)
    gyx = _arg(args, "--yx", 1.0)
    if not (0.20 <= cz <= 0.4999 and 0.20 <= cyx <= 0.4999):
        raise SystemExit("clips must be in [0.20, 0.4999]")
    if not (0.0 <= gz <= 2.0 and 0.0 <= gyx <= 2.0):
        raise SystemExit("multipliers must be in [0, 2]")
    zyx = "%g,%g,%g" % (gz, gyx, gyx)
    clz = "%g,%g,%g" % (cz, cyx, cyx)
    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    c4 = cells[4]
    for a in (ENV_OLD, HELPER_OLD, PRINT_OLD):
        if c4.count(a) != 1:
            raise SystemExit("anchor %r matched %d times" % (a[:60], c4.count(a)))
    base_helper = _helper_src(c4)
    c4 = c4.replace(ENV_OLD, ENV_OLD + "os.environ['BIOHUB_SUBVOXEL_AXIS_GAIN_ZYX'] = '%s'\n" % zyx
                    + "os.environ['BIOHUB_SUBVOXEL_CLIP_ZYX'] = '%s'\n" % clz
                    + "print('ARM_SV_AXES zyx_gain=%s clip_zyx=%s (multipliers on the gain-2.00 sub-voxel offsets, then clip 0.4999, then per-axis clip)', flush=True)\n" % (zyx, clz), 1)
    c4 = c4.replace(HELPER_OLD, HELPER_NEW, 1).replace(PRINT_OLD, PRINT_NEW, 1)
    cells[4] = c4
    cells[0] = cells[0].rstrip(NL) + NL + 'print("ARM_XENV tag=%s SUBVOXEL=axes zyx_gain=%s clip_zyx=%s LCEFR=kept GAIN=2.00 CLIP=0.4999", flush=True)' % (tag, zyx, clz) + NL
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    helper = _helper_src(c4)
    compile(helper, "sv_helper", "exec")
    if "BIOHUB_SUBVOXEL_CLIP_ZYX" not in helper or "BIOHUB_SUBVOXEL_AXIS_GAIN_ZYX" not in helper:
        raise SystemExit("helper patch missing")
    if c4.count("ARM_SV_ZCLIP_STATS") != 1 or c4.count("ARM_SV_AXES_STATS") != 1:
        raise SystemExit("stats patch missing")
    unit_test(base_helper, helper, gz, gyx, cz, cyx)
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
    print("built", dest, "| zyx multipliers", zyx, "| clip zyx", clz)


if __name__ == "__main__":
    main()
