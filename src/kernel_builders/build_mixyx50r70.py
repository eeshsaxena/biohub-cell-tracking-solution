#!/usr/bin/env python3
"""mixyx50r70 = t65b25r70's full stack (tight 6.5, learned bonus 2.5, rawlink 0.70; board 0.954, team top entry) with
y/x = w * V1284 + (1 - w) * SV, w = 0.5, and z = production SV exactly as in both parents.

usage: python scratch_kernels/build_mixyx50r70.py [tag] [w]        (default tag mixyx50r70, w 0.5)

WHY (scratchpad/wf30): t65b25r70 (y/x = our sub-voxel soft-argmax SV) and ourvzlb25r70 / ourvzlb25 (y/x = the public
V1284 head) sit at the same display on the same detections and linker. The fractional blend was never tested
(ourvg13/15/20 only scaled V1284 UP). Offline proxy: w = 0.5 neutral vs SV, clearly better than pure V1284 on both
embryos; it FAILED the pre-registered bar, and the team leader asked for a board test anyway (post-hoc, PREREG.md).

HOW: v_t65b25r70 and v_ourvzlb25r70 are the same notebook apart from cell 4 (lcefr body vs V1284 body) and the XENV
text (asserted below). The V1284 head is mounted EXACTLY as v_ourvzlb25r70 mounts it, so this arm is built from
v_ourvzlb25r70 (cells 0-3 and 5-11 == v_t65b25r70's apart from the XENV line) with ONE block appended to cell 4
right after the z-to-arr block (nothing after that point in cell 4 touches the predictor; asserted):
  * V1284 module: after `shift[:, 0] = 0.0` the y/x shift is multiplied by w (env BIOHUB_MIXYX_W);
  * sub-voxel helper: new keyword `_mix_keep_yx`; with it the ZONLY zeroing is skipped, so the call returns the
    production t65b25r70 SV on all axes (gain 2.00, clip 0.4999, edge zeroing). The z-only call is untouched, so
    SV_ARM_HSG200 / ARM_SV_Z_TO_ARR (z) stay ourvzlb25r70's bit for bit;
  * per frame: the full SV is taken from the INTEGER peak before V1284 (like the z offset), then after V1284 (w*V y/x)
    and the z-to-arr add, (1-w)*SV y/x is added to `arr` and clipped to the grid, so the edge model, the linker and
    the output all see y/x = w*V1284 + (1-w)*SV (the V1284 trilinear gather now reads the blended y/x; z gather stays
    at the integer peak as in ourvzl). The final assembly adds nothing more (the z-only y/x columns are 0; asserted);
  * per movie: `ARM_MIXYX w=0.5 frames=.. nodes=.. mean_abs_sv_minus_v1284_um y=.. x=.. ... final_yx_add=0` with an
    exactly-once check (per frame) and an assembled-y/x == integer peak + w*V + (1-w)*SV check.
Every predictor / module anchor is asserted exactly once here against the REAL ourvzlb25r70 end state
(data/out_ourvzlb25r70/tracking_repo/scripts, the state at the insertion point) and again at notebook runtime.
Identity: ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx
MIXYX=0.50 replaces ourvzlb25r70's XENV line (not duplicated). Metadata = ourvzlb25r70's apart from id/title.
"""
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourvzlb25r70"
BASE_MD5 = "9019774943ccdb39ebffe553b74325f1"  # v_ourvzlb25r70/kernel.ipynb as built + pushed 09-28 20:24Z
T65 = SK / "v_t65b25r70"
T65_MD5 = "60722ec9a2f277733656ba6bf5b559af"  # v_t65b25r70/kernel.ipynb (submitted 56640601, board 0.954)
REAL = ROOT / "data" / "out_ourvzlb25r70" / "tracking_repo" / "scripts"
NL = chr(10)

XENV_OLD = ('print("ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr '
            'V1284_AXES=yx", flush=True)')
XENV_FMT = ('print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr '
            'V1284_AXES=yx MIXYX=%.2f", flush=True)')
T65_XENV = 'print("ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept", flush=True)'
# cell 4: env + marker right after ourvzl's z-to-arr env print, block right after the z-to-arr block's last print
ENV_ANCHOR = ("print('ARM_SV_Z_TO_ARR=1 (sub-voxel z added to the per-frame detections after V1284; final assembly "
              "skips z; V1284 gather z rounded to the peak: gather_int_z=1)', flush=True)\n")
BLOCK_ANCHOR = ("print('ARM_SV_Z_TO_ARR patch applied to', _ps, '| predictor anchors=4 module anchors=1 gather_int_z=1', "
                "flush=True)\n")
NEXT_AFTER = "def list_test_stems() -> list[str]:"

MOD_PAIRS = [
    ("    shift[:, 0] = 0.0  # V1284_YX: the head never helped z; z comes from the sub-voxel refinement\n",
     "    shift[:, 0] = 0.0  # V1284_YX: the head never helped z; z comes from the sub-voxel refinement\n"
     "    if os.environ.get('BIOHUB_MIXYX_W') is not None:\n"
     "        shift[:, 1:] = shift[:, 1:] * float(os.environ['BIOHUB_MIXYX_W'])  # mixyx: w * V1284 y/x\n"),
]
PRED_PAIRS = [
    # P1 module level (after ourvzl's flag checks): read w once, refuse inconsistent configurations
    ("    raise RuntimeError('ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY=1 (y/x come from V1284)')\n",
     "    raise RuntimeError('ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY=1 (y/x come from V1284)')\n"
     "_MIX_W = os.environ.get('BIOHUB_MIXYX_W')\n"
     "if _MIX_W is not None:\n"
     "    _MIX_W = float(_MIX_W)\n"
     "    if not (0.0 < _MIX_W < 1.0):\n"
     "        raise RuntimeError('ARM_MIXYX w outside (0, 1): %r' % (_MIX_W,))\n"
     "    if not _SV_ZTA:\n"
     "        raise RuntimeError('ARM_MIXYX needs the V1284 z-to-arr body (BIOHUB_SUBVOXEL_Z_TO_ARR=1)')\n"),
    # P2 helper: a keyword that skips the ZONLY zeroing -> the full production SV (all axes, same gain/clip/edges)
    ("def _sv_softarg_offsets(lg, arr):\n",
     "def _sv_softarg_offsets(lg, arr, _mix_keep_yx=False):\n"),
    ("    if os.environ.get('BIOHUB_SUBVOXEL_ZONLY', '0') != '0':\n        sa[:, 1:] = 0.0\n",
     "    if os.environ.get('BIOHUB_SUBVOXEL_ZONLY', '0') != '0' and not _mix_keep_yx:\n        sa[:, 1:] = 0.0\n"),
    # P3 predict_video locals
    ("    _zta_base_z: list[np.ndarray] = []\n",
     "    _zta_base_z: list[np.ndarray] = []\n"
     "    _mix_sv_yx: list[np.ndarray] = []\n"
     "    _mix_v_yx: list[np.ndarray] = []\n"
     "    _mix_add: list[np.ndarray] = []\n"
     "    _mix_base: list[np.ndarray] = []\n"),
    # P4 per frame, BEFORE V1284: full SV from the integer peak (z must equal the z-only call's z)
    ("                _sv_refine_lists.append(_sv_softarg_offsets(det_logits[f_idx][0], arr))\n"
     "                arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])\n",
     "                _sv_refine_lists.append(_sv_softarg_offsets(det_logits[f_idx][0], arr))\n"
     "                if _MIX_W is not None:\n"
     "                    _mix_full = _sv_softarg_offsets(det_logits[f_idx][0], arr, _mix_keep_yx=True)\n"
     "                    if not np.array_equal(_mix_full[:, 0], _sv_refine_lists[-1][:, 0]):\n"
     "                        raise RuntimeError('ARM_MIXYX full-SV z differs from the z-only SV z')\n"
     "                    _mix_sv_yx.append(np.asarray(_mix_full[:, 1:], dtype=np.float32).copy())\n"
     "                    _mix_pre = np.asarray(arr, dtype=np.float32)[:, 2:4].copy()\n"
     "                    if not np.array_equal(_mix_pre, np.round(_mix_pre)):\n"
     "                        raise RuntimeError('ARM_MIXYX detection y/x not integral before V1284')\n"
     "                arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])\n"),
    # P5 per frame, AFTER V1284 (w*V y/x) and the z-to-arr add: + (1-w)*SV y/x, clipped to the grid
    ("                    _zta_applied.append(_zta_o)\n",
     "                    _zta_applied.append(_zta_o)\n"
     "                if _MIX_W is not None:\n"
     "                    _mix_v = np.asarray(arr[:, 2:4], dtype=np.float32) - _mix_pre\n"
     "                    _mix_hi = np.asarray(tuple(det_logits[f_idx][0].shape[-2:]), dtype=np.float32) - 1.0\n"
     "                    arr[:, 2:4] = np.clip(arr[:, 2:4] + (1.0 - _MIX_W) * _mix_sv_yx[-1], 0.0, _mix_hi)\n"
     "                    _mix_v_yx.append(_mix_v)\n"
     "                    _mix_add.append(np.asarray(arr[:, 2:4], dtype=np.float32) - _mix_pre - _mix_v)\n"
     "                    _mix_base.append(_mix_pre)\n"),
    # P6 final assembly: prove exactly-once, prove the assembled y/x, print the per-movie stats
    ("            coords[:, 2:] += _sv_off[:, 1:]  # final_z_add=0: z is already in arr; y/x columns are 0 under ZONLY\n",
     "            if _MIX_W is not None:\n"
     "                if not (len(_mix_sv_yx) == len(_mix_v_yx) == len(_mix_add) == len(_mix_base) == len(_sv_refine_lists)):\n"
     "                    raise RuntimeError('ARM_MIXYX y/x blend not applied exactly once per frame (%d/%d/%d of %d)'\n"
     "                                       % (len(_mix_sv_yx), len(_mix_v_yx), len(_mix_add), len(_sv_refine_lists)))\n"
     "                _mix_s = np.concatenate(_mix_sv_yx).astype(np.float64)\n"
     "                _mix_vv = np.concatenate(_mix_v_yx).astype(np.float64) / _MIX_W\n"
     "                _mix_aa = np.concatenate(_mix_add).astype(np.float64)\n"
     "                _mix_bb = np.concatenate(_mix_base).astype(np.float64)\n"
     "                if _mix_s.shape[0] != _sv_off.shape[0] or _mix_s.shape[0] != coords.shape[0]:\n"
     "                    raise RuntimeError('ARM_MIXYX node count mismatch %d vs %d' % (_mix_s.shape[0], _sv_off.shape[0]))\n"
     "                if _sv_off.shape[0] and np.abs(_sv_off[:, 1:]).max() != 0.0:\n"
     "                    raise RuntimeError('ARM_MIXYX z-only SV y/x columns are not zero (y/x would be added twice)')\n"
     "                if _mix_s.shape[0] and not (np.abs(_mix_s).sum() > 0.0 and np.abs(_mix_vv).sum() > 0.0):\n"
     "                    raise RuntimeError('ARM_MIXYX NO-OP: SV or V1284 y/x all zero')\n"
     "                if not np.allclose(coords[:, 2:4], _mix_bb + _mix_vv * _MIX_W + _mix_aa, rtol=0.0, atol=1e-4):\n"
     "                    raise RuntimeError('ARM_MIXYX assembled y/x != integer peak + w*V1284 + (1-w)*SV')\n"
     "                _mix_d = np.abs(_mix_s - _mix_vv) * 1.625\n"
     "                print('ARM_MIXYX w=%s frames=%d nodes=%d mean_abs_sv_minus_v1284_um y=%.4f x=%.4f '\n"
     "                      'mean_abs_sv_um y=%.4f x=%.4f mean_abs_v1284_um y=%.4f x=%.4f mean_abs_yx_blend_um=%.4f final_yx_add=0'\n"
     "                      % (repr(_MIX_W), len(_mix_v_yx), _mix_s.shape[0],\n"
     "                         *(_mix_d.mean(0) if _mix_s.shape[0] else (0.0, 0.0)),\n"
     "                         *((np.abs(_mix_s) * 1.625).mean(0) if _mix_s.shape[0] else (0.0, 0.0)),\n"
     "                         *((np.abs(_mix_vv) * 1.625).mean(0) if _mix_s.shape[0] else (0.0, 0.0)),\n"
     "                         float(np.linalg.norm((_mix_vv * _MIX_W + _mix_aa) * 1.625, axis=1).mean()) if _mix_s.shape[0] else 0.0),\n"
     "                      flush=True)\n"
     "            coords[:, 2:] += _sv_off[:, 1:]  # final_z_add=0: z is already in arr; y/x columns are 0 under ZONLY\n"),
]
PERSIST_PRED = "ARM_MIXYX w=%s frames="
PERSIST_MOD = "mixyx: w * V1284 y/x"


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def apply_pairs(src, pairs, what):
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            raise SystemExit("%s anchor matched %d times (need 1): %r" % (what, n, old[:70]))
        src = src.replace(old, new, 1)
    return src


def render_block(w):
    L = []
    a = L.append
    a("# ===== MIXED Y/X: w * V1284 + (1 - w) * SUB-VOXEL (arm mixyx, scratchpad/wf30) =====")
    a("# t65b25r70 (y/x = sub-voxel SV) and ourvzlb25r70 (y/x = V1284) share detections, z and linker. Here y/x is the")
    a("# blend: V1284's y/x shift is scaled by w inside its module, the full production SV (from the INTEGER peak, before")
    a("# V1284) is scaled by 1-w and added to `arr` after V1284 + the z-to-arr add, so the edge model, the linker and the")
    a("# output all read the blended y/x. z is untouched (production SV, z-to-arr). Exactly-once checks at the assembly.")
    a("if os.environ.get('BIOHUB_MIXYX_W') != %r or os.environ.get('BIOHUB_SUBVOXEL_Z_TO_ARR') != '1' \\" % repr(w))
    a("        or os.environ.get('BIOHUB_SUBVOXEL_ZONLY') != '1':")
    a("    raise RuntimeError('ARM_MIXYX env flags missing: MIXYX_W=%s, Z_TO_ARR=1 and ZONLY=1 are all required')" % repr(w))
    a("_mix_mod = _ps.parent / 'v1284_coordinate_refinement.py'")
    a("_mix_m = _mix_mod.read_text()")
    a("_mix_mod_pairs = [")
    for old, new in MOD_PAIRS:
        a("    (%r,\n     %r)," % (old, new))
    a("]")
    a("for _mix_old, _mix_new in _mix_mod_pairs:")
    a("    _mix_n = _mix_m.count(_mix_old)")
    a("    if _mix_n != 1:")
    a("        raise RuntimeError('ARM_MIXYX module anchor matched %d times (need 1): %r' % (_mix_n, _mix_old[:60]))")
    a("    _mix_m = _mix_m.replace(_mix_old, _mix_new, 1)")
    a("compile(_mix_m, str(_mix_mod), 'exec')")
    a("_mix_mod.write_text(_mix_m)")
    a("_mix_s = _ps.read_text()")
    a("_mix_pairs = [")
    for old, new in PRED_PAIRS:
        a("    (%r,\n     %r)," % (old, new))
    a("]")
    a("for _mix_old, _mix_new in _mix_pairs:")
    a("    _mix_n = _mix_s.count(_mix_old)")
    a("    if _mix_n != 1:")
    a("        raise RuntimeError('ARM_MIXYX anchor matched %d times (need 1): %r' % (_mix_n, _mix_old[:60]))")
    a("    _mix_s = _mix_s.replace(_mix_old, _mix_new, 1)")
    a("compile(_mix_s, str(_ps), 'exec')")
    a("_ps.write_text(_mix_s)")
    a("if %r not in _ps.read_text() or %r not in _mix_mod.read_text():" % (PERSIST_PRED, PERSIST_MOD))
    a("    raise RuntimeError('ARM_MIXYX PATCH DID NOT PERSIST')")
    a("print('ARM_MIXYX patch applied to', _ps, '| predictor anchors=%d module anchors=%d w=%s', flush=True)"
      % (len(PRED_PAIRS), len(MOD_PAIRS), repr(w)))
    return NL.join(L) + NL


def unit_tests(real_pred, new_pred, real_mod, new_mod, w, t65_helper_src):
    import os
    rng = np.random.default_rng(0)
    old_env = dict(os.environ)
    try:
        os.environ.update({"BIOHUB_SUBVOXEL_SOFTARG": "1", "BIOHUB_SUBVOXEL_GAIN_MODE": "fixed",
                           "BIOHUB_SUBVOXEL_GAIN_FIXED": "2.00", "BIOHUB_SUBVOXEL_CLIP": "0.4999",
                           "BIOHUB_SUBVOXEL_Z_TO_ARR": "1", "BIOHUB_SUBVOXEL_ZONLY": "1", "BIOHUB_MIXYX_W": repr(w)})
        ns_new, ns_old, ns_t65 = {"np": np, "os": os}, {"np": np, "os": os}, {"np": np, "os": os}
        for ns, src in ((ns_new, new_pred), (ns_old, real_pred)):
            s = src.index("_SV_ON = os.environ.get('BIOHUB_SUBVOXEL_SOFTARG'")
            exec(src[s:src.index("def _detect_cells_pooled(", s)], ns)
        exec(t65_helper_src, ns_t65)
        lg = rng.normal(0, 3, size=(1, 12, 40, 40)).astype(np.float32)
        arr = np.stack([np.zeros(300), rng.integers(0, 12, 300), rng.integers(0, 40, 300), rng.integers(0, 40, 300)], 1)
        arr = arr.astype(np.int64)
        zo_new = ns_new["_sv_softarg_offsets"](lg, arr)
        zo_old = ns_old["_sv_softarg_offsets"](lg, arr)
        full = ns_new["_sv_softarg_offsets"](lg, arr, _mix_keep_yx=True)
        os.environ.pop("BIOHUB_SUBVOXEL_ZONLY")
        t65 = ns_t65["_sv_softarg_offsets"](lg, arr)
        if not np.array_equal(zo_new, zo_old):
            raise SystemExit("unit: the z-only helper output changed (SV_ARM_HSG200 / z-to-arr would move)")
        if not np.array_equal(full, t65):
            raise SystemExit("unit: _mix_keep_yx=True does not reproduce t65b25r70's SV helper bit for bit")
        if not np.array_equal(full[:, 0], zo_new[:, 0]) or np.abs(zo_new[:, 1:]).max() != 0.0 or np.abs(full[:, 1:]).max() == 0:
            raise SystemExit("unit: z / y-x split of the two helper calls is wrong")
        # V1284 module: patched refine() shift == w * unpatched shift (y/x), z still 0; uses the real mounted head
        import torch
        head_p = SK / "_v1284" / "v1284_head.pt"
        out = {}
        feat = torch.as_tensor(rng.normal(0, 1, size=(1, 32, 12, 40, 40)).astype(np.float32))
        os.environ["V1284_MODE"] = "candidate"
        os.environ["V1284_HEAD"] = str(head_p)
        for tagm, src in (("old", real_mod), ("new", new_mod)):
            ns = {}
            exec(compile(src, "v1284_" + tagm, "exec"), ns)
            with torch.no_grad():  # the predictor calls refine() under inference mode
                out[tagm] = ns["refine"](None, 0, arr[:40].astype(np.int64), feat)
        dold = out["old"][:, 1:] - arr[:40, 1:]
        dnew = out["new"][:, 1:] - arr[:40, 1:]
        inside = np.all((out["old"][:, 2:] > 0) & (out["old"][:, 2:] < 39), 1)
        if np.abs(dold[:, 0]).max() != 0 or np.abs(dnew[:, 0]).max() != 0:
            raise SystemExit("unit: V1284 moved z")
        if not np.allclose(dnew[inside, 1:], w * dold[inside, 1:], atol=1e-5) or np.abs(dold[:, 1:]).max() == 0:
            raise SystemExit("unit: patched V1284 y/x shift != w * original")
        return {"zonly_identical": True, "keep_yx_eq_t65": True, "v1284_scaled": float(w),
                "mean_abs_v_yx_vox": float(np.abs(dold[:, 1:]).mean()), "rows": int(inside.sum())}
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "mixyx50r70"
    w = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    if not (0.0 < w < 1.0):
        raise SystemExit("w must be in (0, 1)")
    for d, m in ((BASE, BASE_MD5), (T65, T65_MD5)):
        if md5(d / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (d.name, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, t65 = cells_of(T65 / "kernel.ipynb")
    orig = list(cells)
    if len(cells) != 12 or len(t65) != 12 or any(c is None for c in cells):
        raise SystemExit("unexpected notebook shape")
    # ---- "t65b25r70's full stack": ourvzlb25r70 == t65b25r70 outside cell 4, XENV text aside
    diff = [i for i, (a, b) in enumerate(zip(t65, cells)) if a != b]
    if diff != [0, 4]:
        raise SystemExit("v_ourvzlb25r70 vs v_t65b25r70 differ in cells %r (expected [0, 4])" % diff)
    if cells[0].replace(XENV_OLD, T65_XENV, 1) != t65[0] or cells[0].count(XENV_OLD) != 1:
        raise SystemExit("cell 0 differs from t65b25r70's beyond the XENV line")
    # ---- predictor / module anchors against the REAL ourvzlb25r70 end state
    real_pred = (REAL / "predict_unet_transformer.py").read_text(encoding="utf-8")
    real_mod = (REAL / "v1284_coordinate_refinement.py").read_text(encoding="utf-8")
    if "ARM_SV_Z_TO_ARR frames=" not in real_pred or "BIOHUB_V1284_GATHER_INT_Z" not in real_mod:
        raise SystemExit("REAL predictor/module are not the ourvzl end state")
    import re
    for bad in (r"MIXYX", r"(?<![A-Za-z0-9_])_mix_"):  # (secondary_mix_temperature is the base's own name)
        if re.search(bad, real_pred) or re.search(bad, real_mod) or any(re.search(bad, c) for c in cells):
            raise SystemExit("base already carries %r" % bad)
    new_pred = apply_pairs(real_pred, PRED_PAIRS, "predictor")
    new_mod = apply_pairs(real_mod, MOD_PAIRS, "module")
    compile(new_pred, "predict_unet_transformer.py[mixyx]", "exec")
    compile(new_mod, "v1284_coordinate_refinement.py[mixyx]", "exec")
    if new_pred.count(PERSIST_PRED) != 1 or new_mod.count(PERSIST_MOD) != 1:
        raise SystemExit("persistence markers not unique")
    # ordering inside predict_video: SV from integer peak -> full SV -> V1284 -> z add -> y/x add -> coord_offset
    order = ["_sv_refine_lists.append(_sv_softarg_offsets(det_logits[f_idx][0], arr))",
             "_mix_full = _sv_softarg_offsets(det_logits[f_idx][0], arr, _mix_keep_yx=True)",
             "arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])", "arr[:, 1] += _zta_o",
             "arr[:, 2:4] = np.clip(arr[:, 2:4] + (1.0 - _MIX_W) * _mix_sv_yx[-1], 0.0, _mix_hi)",
             "coord_offset[t] = (global_node_count, global_node_count + len(arr))", "coords_so_far = (",
             "raise RuntimeError('ARM_MIXYX assembled y/x", "coords[:, 2:] += _sv_off[:, 1:]",
             "coords[:, 1:] *= ds_arr"]
    pos = [new_pred.index(o) for o in order]
    if pos != sorted(pos):
        raise SystemExit("predictor ordering check failed: %r" % pos)
    # ---- cell 0 identity
    xenv = XENV_FMT % (tag, w)
    cells[0] = cells[0].replace(XENV_OLD, xenv, 1)
    # ---- cell 4: env + marker, block
    c4 = cells[4]
    for a_ in (ENV_ANCHOR, BLOCK_ANCHOR, NEXT_AFTER):
        if c4.count(a_) != 1:
            raise SystemExit("cell-4 anchor %r matched %d" % (a_[:60], c4.count(a_)))
    if not c4.index(ENV_ANCHOR) < c4.index(BLOCK_ANCHOR) < c4.index(NEXT_AFTER):
        raise SystemExit("cell-4 anchor order")
    tail = c4[c4.index(BLOCK_ANCHOR) + len(BLOCK_ANCHOR):]
    if "_ps.write_text" in tail or "_ps.read_text" in tail or "v1284_coordinate_refinement" in tail:
        raise SystemExit("cell 4 touches the predictor/module after the z-to-arr block: REAL is not the insertion state")
    env_new = (ENV_ANCHOR + "os.environ['BIOHUB_MIXYX_W'] = %r\n" % repr(w)
               + "print('ARM_MIXYX w=%s (y/x = %s*V1284 + %s*SV into the per-frame detections after V1284; "
                 "z = SV z-to-arr)', flush=True)\n" % (repr(w), repr(w), repr(round(1.0 - w, 6))))
    block = render_block(w)
    c4 = c4.replace(ENV_ANCHOR, env_new, 1).replace(BLOCK_ANCHOR, BLOCK_ANCHOR + NL + block, 1)
    if c4.count("# ===== MIXED Y/X") != 1 or not (c4.index(env_new) < c4.index(block) < c4.index(NEXT_AFTER)):
        raise SystemExit("cell-4 insertion failed")
    cells[4] = c4
    # the rendered literals must be exactly the asserted pairs
    ns = {}
    b0 = block.index("_mix_mod_pairs = [")
    exec(block[b0:block.index("for _mix_old", b0)], ns)
    b1 = block.index("_mix_pairs = [")
    exec(block[b1:block.index("for _mix_old", b1)], ns)
    if [tuple(p) for p in ns["_mix_pairs"]] != PRED_PAIRS or [tuple(p) for p in ns["_mix_mod_pairs"]] != MOD_PAIRS:
        raise SystemExit("rendered block literals differ from the asserted pairs")
    changed = [i for i, (a_, b_) in enumerate(zip(orig, cells)) if a_ != b_]
    if changed != [0, 4]:
        raise SystemExit("cells changed vs v_ourvzlb25r70 = %r (expected [0, 4])" % changed)
    if sum("ARM_XENV" in c for c in cells) != 1 or cells[0].split(NL).count(xenv) != 1:
        raise SystemExit("XENV line not exactly once")
    for i, c in enumerate(cells):
        compile(c, "%s:cell%d" % (tag, i), "exec")
    # ---- unit tests (numpy + torch on CPU, tiny): helper split + V1284 scaling, against t65b25r70's helper
    t4 = t65[4]
    hs = t4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    unit = unit_tests(real_pred, new_pred, real_mod, new_mod, w, t4[hs:t4.index('"""', hs)])
    # ---- write
    k = 0
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["source"] = cells[k].splitlines(keepends=True)
            c["outputs"] = []
            c["execution_count"] = None
        k += 1
    dest = SK / ("v_" + tag)
    dest.mkdir(parents=True, exist_ok=True)
    with open(dest / "kernel.ipynb", "w", encoding="utf-8") as fh:
        json.dump(nb, fh)
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    with open(dest / "kernel-metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read differs from the built cells")
    bm = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k_ for k_ in set(bm) | set(nm) if bm.get(k_) != nm.get(k_))
    if mdiff != ["id", "title"]:
        raise SystemExit("metadata differs beyond id/title: %r" % mdiff)
    print("built", dest, "| base v_ourvzlb25r70 (md5 %s) == v_t65b25r70 (md5 %s) outside cell 4 + XENV" % (BASE_MD5, T65_MD5))
    print("cells changed vs v_ourvzlb25r70:", changed, "| w =", w, "| datasets", nm["dataset_sources"],
          "| machine", nm.get("machine_shape"))
    print("  cell 0: -", XENV_OLD)
    print("          +", xenv)
    print("  cell 4: + env/marker after the z-to-arr env; + ARM_MIXYX block (%d predictor + %d module anchors, each "
          "matched once against %s)" % (len(PRED_PAIRS), len(MOD_PAIRS), REAL))
    print("unit tests:", unit)
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
