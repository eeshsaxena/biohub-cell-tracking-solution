#!/usr/bin/env python3
"""Derive v_logitcap from v_v1284cap: save the production detection-logit window around EVERY
detection on the same 60 train movies, so better z estimators can be tested offline.

usage: python scratch_kernels/build_logitcap.py

WHY. In t6stk3's remaining displacement tail z dominates (58% / 89% of tail edges on 44b6 / 6bba),
and our z comes from the sub-voxel (SV) 3x3x3 softmax over the BLENDED detection logits at each
integer peak (gain 2, clip 0.4999), which overshoots. Testing wider z windows, Gaussian/parabolic
fits, lower gains or robust estimators offline needs the exact production logits around each
detection, wider in z than the 3 slices SV sees.

WHAT (derived kernel, TRAINING/CAPTURE only, never submitted):
  * cells 0-4 are v_v1284cap's (same datasets, same deterministic 60-movie prefix-stratified
    selection, same 6 h wall-clock guard, same capture-only predictor: edge loop / graph / ILP /
    geff skipped, failing movie logged and skipped). Cell 0 gains a LOGITCAP config tail.
  * cell 4 gains ONE runtime patch block, run on _trial_source right after the V1284CAP patch
    and before the predictor is written. Every anchor is asserted to match exactly once:
      1. the SV helper, VERBATIM from v_t6stk3 cell 4 (_SV_HELPER), with t6stk3's env
         (SOFTARG=1, gain fixed 2.00, clip 0.4999), plus the LOGITCAP helpers, inserted before
         `def _detect_cells_pooled(`. v_v1284cap does NOT contain it: it derives from v_ourv,
         which removed the SV block (checked: no `_sv_softarg_offsets` in its predictor).
      2. `_logitcap_reset(ds_path, downsample, T)` at the start of predict_video.
      3. the retention guard records (use_primary, primary_candidates, blended_candidates) for
         each frame right where it picks primary-only vs blended logits.
      4. right after `arr = _detect_cells_pooled(det_logits[f_idx][0], ...)` in the per-frame
         loop: `_logitcap_frame(det_logits[f_idx][0], t, arr)`, which stores for every detection
         the window det_logits[f_idx][0][z-3:z+4, y-1:y+2, x-1:x+2] (7x3x3, out-of-volume
         entries = edge value, float32), the peak logit (float32), and the production SV offsets
         computed by the verbatim helper on the same volume (float32 (n,3); NOT applied to arr).
      5. after each finished movie (capture branch): `_logitcap_flush(stem, coords)` asserts
         the capture equals predict_video's own returned coords (same rows, same order, grid x
         downsample), that every frame 0..T-1 was captured once and that each window centre is
         the peak logit, then writes <LOGITCAP_DIR>/<stem>.npz atomically and prints
         `LOGITCAP movie=<stem> dets=<n> frames=<k> bytes=<b> ...`.
  * cell 5 (V1284 head training) is replaced by a small summary cell: per-movie counts, bytes,
    sanity fractions, _manifest.json, `LOGITCAP DONE movies=<m> dets=<N> bytes=<B>`.

V1284 FEATURE CAPTURE: OFF by default (LOGITCAP_KEEP_V1284=0), the simpler robust path.
  - V1284_MODE stays 'capture' because it drives the proven capture-only control flow
    (edge-loop skip, per-movie try/except, budget guard, _DONE.json markers).
  - In capture mode refine() returns `arr` unchanged, so skipping the call changes no detection:
    the logits and peaks are bit-for-bit what the V1284 run produced from the same code.
  - V1284 features for these 60 movies already exist: data/out_v1284cap/v1284cap_candidates.npz
    (every detection within 7 um of a GT node, exact int (movie,t,z,y,x) coords) - an offline
    join on those coords gives the same detections their features.
  - Keeping it ON would add ~1 GB of per-frame 224-float feature npz to /kaggle/working and a
    per-frame gather+compress for nothing new. LOGITCAP_KEEP_V1284=1 restores it (tested offline).

Output per movie /kaggle/working/logitcap/<stem>.npz:
  coords int16 (n,4) [t,z,y,x] on the feature grid (z native, y/x = native/4), win float32
  (n,7,3,3) [dz,dy,dx], peak float32 (n,), sv float32 (n,3) production SV offsets (grid voxels),
  use_primary int8 (n,) (1 = retention guard used primary-only logits for that frame, 0 = blended,
  -1 = no blending), frames/frame_dets/frame_use_primary/frame_primary_candidates/
  frame_blended_candidates (per frame), shape int16 (3,) grid volume (Z,Y,X), downsample,
  half_zyx, sv_gain, sv_clip.
Expected size: ~1.34 M detections over the 60 movies (v1284cap log) x ~150 B = ~0.2 GB total,
<= ~15 MB for the largest movie. Runtime ~= v1284cap's prediction phase (109.6 min for 60 movies
on 2 x T4) + ~6 min setup; the hook adds one GPU->CPU copy of the frame's logit volume
(the same copy t6stk3's SV helper makes) per frame.
"""
import ast
import json
import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_v1284cap"
T6 = SK / "v_t6stk3"
REF_PREDICTOR = ROOT / "data" / "out_v1284cap" / "tracking_repo" / "scripts" / "predict_unet_transformer.py"
REF_T6_PREDICTOR = ROOT / "data" / "out_t6stk3" / "tracking_repo" / "scripts" / "predict_unet_transformer.py"
TAG = "logitcap"
NL = chr(10)

# t6stk3's SV env, asserted to appear verbatim in v_t6stk3 cell 4
SV_ENV = ("os.environ['BIOHUB_SUBVOXEL_SOFTARG'] = '1'\n"
          "os.environ['BIOHUB_SUBVOXEL_GAIN_MODE'] = 'fixed'\n"
          "os.environ['BIOHUB_SUBVOXEL_GAIN_FIXED'] = '2.00'\n"
          "os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n")

# ----------------------------------------------------------------------------- cell 0 tail
CELL0_TAIL = r'''
# ===== LOGITCAP: blended detection-logit windows around every detection on TRAIN movies (NEVER submitted) =====
# Derived from v_v1284cap: same 60 train movies, same budget guard, same capture-only predictor.
# The V1284CAP_* training settings above are unused here (the training cell is replaced).
os.environ.setdefault("LOGITCAP_DIR", "/kaggle/working/logitcap")
os.environ.setdefault("LOGITCAP_HALF_ZYX", "3,1,1")   # window (2*3+1, 2*1+1, 2*1+1) = 7x3x3 grid voxels
os.environ.setdefault("LOGITCAP_KEEP_V1284", "0")     # 1 = also keep the V1284 per-frame feature capture
print("ARM_LOGITCAP dir=%s half_zyx=%s keep_v1284=%s n_movies=%s budget_s=%s" % (
    os.environ["LOGITCAP_DIR"], os.environ["LOGITCAP_HALF_ZYX"], os.environ["LOGITCAP_KEEP_V1284"],
    os.environ["V1284CAP_N_MOVIES"], os.environ["BIOHUB_CAPTURE_BUDGET_S"]), flush=True)
'''

# ----------------------------------------------------------------------------- predictor helpers
# Module-level code inserted into predict_unet_transformer.py (after the verbatim SV helper).
# Must not contain a backslash or a triple double quote (embedded as a triple-quoted literal).
LOGITCAP_HELPERS = r'''# ----- LOGITCAP (capture kernel only): window of the detection logits that _detect_cells_pooled
# saw (blended primary+secondary unless the retention guard fell back to primary) around every
# detection, plus the production SV offsets on the same volume. Nothing here changes a detection.
_LOGITCAP = {}
_LOGITCAP_HALF = tuple(int(v) for v in os.environ.get('LOGITCAP_HALF_ZYX', '3,1,1').split(','))
if len(_LOGITCAP_HALF) != 3 or min(_LOGITCAP_HALF) < 1:
    raise RuntimeError('LOGITCAP bad LOGITCAP_HALF_ZYX %r' % (_LOGITCAP_HALF,))


def _logitcap_reset(ds_path, downsample, n_frames):
    _LOGITCAP.clear()
    _LOGITCAP.update({'stem': Path(ds_path).stem, 'downsample': tuple(int(d) for d in downsample),
                      'n_frames': int(n_frames), 'shape': None, 'guard': {},
                      'coords': [], 'win': [], 'peak': [], 'sv': [],
                      'frames': [], 'frame_dets': [], 'frame_guard': []})


def _logitcap_windows(vol, idx, half):
    # (n, 2hz+1, 2hy+1, 2hx+1) windows of vol (Z,Y,X) centred on integer idx (n,3). Indices
    # outside the volume take the edge value: identical to np.pad(vol, half, mode='edge') + slice.
    oz, oy, ox = (np.arange(-h, h + 1) for h in half)
    zz = np.clip(idx[:, 0, None, None, None] + oz[None, :, None, None], 0, vol.shape[0] - 1)
    yy = np.clip(idx[:, 1, None, None, None] + oy[None, None, :, None], 0, vol.shape[1] - 1)
    xx = np.clip(idx[:, 2, None, None, None] + ox[None, None, None, :], 0, vol.shape[2] - 1)
    return vol[zz, yy, xx]


def _logitcap_frame(lg, t, arr):
    # called right after arr = _detect_cells_pooled(det_logits[f_idx][0], t, ...)
    if not _LOGITCAP:
        raise RuntimeError('LOGITCAP buffer not initialised (predict_video reset hook missing)')
    vol = lg.detach().float().cpu().numpy() if hasattr(lg, 'detach') else np.asarray(lg, dtype=np.float32)
    vol = vol.reshape(vol.shape[-3:])
    shape = tuple(int(s) for s in vol.shape)
    if _LOGITCAP['shape'] is None:
        _LOGITCAP['shape'] = shape
    elif _LOGITCAP['shape'] != shape:
        raise RuntimeError('LOGITCAP volume shape changed %r -> %r' % (_LOGITCAP['shape'], shape))
    arr = np.asarray(arr)
    n = len(arr)
    coords = arr.astype(np.int16).reshape(n, 4)
    idx = coords[:, 1:4].astype(np.int64)
    if n and (np.any(coords[:, 0] != int(t)) or idx.min() < 0 or np.any(idx >= np.asarray(shape))):
        raise RuntimeError('LOGITCAP bad detections for frame %d' % int(t))
    if int(t) in _LOGITCAP['frames']:
        raise RuntimeError('LOGITCAP frame %d captured twice' % int(t))
    win = _logitcap_windows(vol, idx, _LOGITCAP_HALF)
    sv = np.asarray(_sv_softarg_offsets(vol, coords), dtype=np.float32).reshape(n, 3)
    _LOGITCAP['coords'].append(coords)
    _LOGITCAP['win'].append(win.astype(np.float32))
    _LOGITCAP['peak'].append(vol[idx[:, 0], idx[:, 1], idx[:, 2]].astype(np.float32))
    _LOGITCAP['sv'].append(sv)
    _LOGITCAP['frames'].append(int(t))
    _LOGITCAP['frame_dets'].append(n)
    _LOGITCAP['frame_guard'].append(tuple(int(v) for v in _LOGITCAP['guard'].get(int(t), (-1, -1, -1))))


def _logitcap_flush(stem, coords_native):
    # validate the movie's capture against predict_video's returned coords, then write it
    if _LOGITCAP.get('stem') != stem:
        raise RuntimeError('LOGITCAP buffer holds %r, not %r' % (_LOGITCAP.get('stem'), stem))
    k = len(_LOGITCAP['frames'])
    if k != _LOGITCAP['n_frames'] or sorted(_LOGITCAP['frames']) != list(range(k)):
        raise RuntimeError('LOGITCAP %s captured %d frames, expected %d' % (stem, k, _LOGITCAP['n_frames']))
    wshape = tuple(2 * h + 1 for h in _LOGITCAP_HALF)
    coords = np.concatenate(_LOGITCAP['coords']) if _LOGITCAP['coords'] else np.zeros((0, 4), np.int16)
    win = np.concatenate(_LOGITCAP['win']) if _LOGITCAP['win'] else np.zeros((0,) + wshape, np.float32)
    peak = np.concatenate(_LOGITCAP['peak']) if _LOGITCAP['peak'] else np.zeros(0, np.float32)
    sv = np.concatenate(_LOGITCAP['sv']) if _LOGITCAP['sv'] else np.zeros((0, 3), np.float32)
    frame_dets = np.asarray(_LOGITCAP['frame_dets'], dtype=np.int32)
    guard = np.asarray(_LOGITCAP['frame_guard'], dtype=np.int32).reshape(k, 3)
    # the capture must describe exactly the detections predict_video returned, in the same order
    ref = np.asarray(coords_native, dtype=np.float64)
    ds = np.asarray(_LOGITCAP['downsample'], dtype=np.float64)
    if (ref.shape != (len(coords), 4) or not np.array_equal(ref[:, 0], coords[:, 0].astype(np.float64))
            or not np.array_equal(ref[:, 1:], coords[:, 1:].astype(np.float64) * ds)):
        raise RuntimeError('LOGITCAP %s capture != predict_video coords (%r vs %r)'
                           % (stem, ref.shape, coords.shape))
    if int(frame_dets.sum()) != len(coords) or win.shape != (len(coords),) + wshape or len(sv) != len(coords):
        raise RuntimeError('LOGITCAP %s internal count mismatch' % stem)
    hz, hy, hx = _LOGITCAP_HALF
    if len(coords) and not np.array_equal(win[:, hz, hy, hx], peak.astype(np.float32)):
        raise RuntimeError('LOGITCAP %s window centre != peak logit' % stem)
    core = win[:, hz - 1:hz + 2, hy - 1:hy + 2, hx - 1:hx + 2].reshape(len(coords), -1)
    centre_is_max = float(np.mean(win[:, hz, hy, hx] >= core.max(1))) if len(coords) else 1.0
    out_dir = Path(os.environ.get('LOGITCAP_DIR', '/kaggle/working/logitcap'))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (stem + '.npz')
    tmp = out_dir / (stem + '.partial.npz')
    np.savez_compressed(tmp, coords=coords, win=win, peak=peak, sv=sv,
                        use_primary=np.repeat(guard[:, 0], frame_dets).astype(np.int8),
                        frames=np.asarray(_LOGITCAP['frames'], dtype=np.int16), frame_dets=frame_dets,
                        frame_use_primary=guard[:, 0].astype(np.int8),
                        frame_primary_candidates=guard[:, 1], frame_blended_candidates=guard[:, 2],
                        shape=np.asarray(_LOGITCAP['shape'], dtype=np.int16),
                        downsample=np.asarray(_LOGITCAP['downsample'], dtype=np.int16),
                        half_zyx=np.asarray(_LOGITCAP_HALF, dtype=np.int16),
                        sv_gain=np.float32(_sv_gain()), sv_clip=np.float32(_SV_CLIP))
    os.replace(tmp, out)
    n_bytes = int(out.stat().st_size)
    print('LOGITCAP movie=%s dets=%d frames=%d bytes=%d primary_frames=%d guard_unknown_frames=%d '
          'centre_is_max=%.4f mean_abs_sv_z=%.4f' % (
              stem, len(coords), k, n_bytes, int((guard[:, 0] == 1).sum()), int((guard[:, 0] < 0).sum()),
              centre_is_max, float(np.abs(sv[:, 0]).mean()) if len(sv) else 0.0), flush=True)
    _LOGITCAP.clear()
    return n_bytes


'''

# ----------------------------------------------------------------------------- runtime anchors
# (old, new) pairs applied to _trial_source (the fully patched V1284CAP predictor) at kernel time.
R_INIT_OLD = "    coord_lists: list[np.ndarray] = []\n"
R_INIT_NEW = R_INIT_OLD + "    _logitcap_reset(ds_path, downsample, T)\n"

R_GUARD_OLD = ("                    det_logits[f] = (\n"
               "                        primary_det if use_primary_detection else blended_det\n"
               "                    )\n")
R_GUARD_NEW = R_GUARD_OLD + (
    "                    _LOGITCAP['guard'][int(frame_indices[f])] = (\n"
    "                        int(use_primary_detection), int(primary_candidates), int(blended_candidates)\n"
    "                    )\n")

R_DETECT_OLD = ("                arr = _detect_cells_pooled(\n"
                "                    det_logits[f_idx][0], t, cfg.det_threshold, pool_k,\n"
                "                )\n"
                "                arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])\n")
R_DETECT_NEW = ("                arr = _detect_cells_pooled(\n"
                "                    det_logits[f_idx][0], t, cfg.det_threshold, pool_k,\n"
                "                )\n"
                "                _logitcap_frame(det_logits[f_idx][0], t, arr)\n"
                "                if os.environ.get('LOGITCAP_KEEP_V1284', '0') != '0':\n"
                "                    arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])\n")

R_FLUSH_OLD = "            _v1284cap_seconds = _v1284cap_time.time() - _v1284cap_start\n"
R_FLUSH_NEW = R_FLUSH_OLD + "            _logitcap_flush(ds_path.stem, _v1284cap_coords)\n"

R_HELPER_OLD = "def _detect_cells_pooled(\n"

PATCH_TEMPLATE = r'''
# --------------------------------- LOGITCAP: detection-logit windows (derived kernel, never submitted)
# Runs on _trial_source right after the V1284CAP capture-only patch. Adds, with every anchor asserted
# to match exactly once: the SV helper VERBATIM from v_t6stk3 (+ t6stk3's SV env) and the LOGITCAP
# helpers before _detect_cells_pooled; a per-movie buffer reset in predict_video; the retention-guard
# decision per frame; a hook right after arr = _detect_cells_pooled(det_logits[f_idx][0], ...) that
# stores the 7x3x3 logit window, the peak logit and the production SV offsets (NOT applied to arr);
# and a per-movie validated flush to <LOGITCAP_DIR>/<stem>.npz. The V1284 feature capture runs only
# if LOGITCAP_KEEP_V1284=1 (in capture mode refine() returns arr unchanged either way).
@@SV_ENV@@_LOGITCAP_SV_HELPER = """@@SV_HELPER@@"""
_LOGITCAP_HELPERS = """@@HELPERS@@"""
compile(_LOGITCAP_SV_HELPER + _LOGITCAP_HELPERS, "logitcap_helpers", "exec")


def _logitcap_replace_once(src, old, new, what):
    n = src.count(old)
    if n != 1:
        raise RuntimeError("LOGITCAP anchor %r matched %d times (need exactly 1)" % (what, n))
    return src.replace(old, new, 1)


if "_sv_softarg_offsets" in _trial_source or "_LOGITCAP" in _trial_source:
    raise RuntimeError("LOGITCAP: predictor already contains an SV or LOGITCAP block")
_trial_source = _logitcap_replace_once(
    _trial_source, @@R_HELPER_OLD@@, _LOGITCAP_SV_HELPER + _LOGITCAP_HELPERS + @@R_HELPER_OLD@@,
    "def _detect_cells_pooled")
_trial_source = _logitcap_replace_once(_trial_source, @@R_INIT_OLD@@, @@R_INIT_NEW@@, "coord_lists init")
_trial_source = _logitcap_replace_once(_trial_source, @@R_GUARD_OLD@@, @@R_GUARD_NEW@@, "retention guard choice")
_trial_source = _logitcap_replace_once(_trial_source, @@R_DETECT_OLD@@, @@R_DETECT_NEW@@, "per-frame detection")
_trial_source = _logitcap_replace_once(_trial_source, @@R_FLUSH_OLD@@, @@R_FLUSH_NEW@@, "capture-branch movie done")
for _logitcap_probe in ("_logitcap_reset(ds_path, downsample, T)", "_LOGITCAP['guard'][int(frame_indices[f])]",
                        "_logitcap_frame(det_logits[f_idx][0], t, arr)",
                        "_logitcap_flush(ds_path.stem, _v1284cap_coords)", "def _sv_softarg_offsets(lg, arr):"):
    if _trial_source.count(_logitcap_probe) != 1:
        raise RuntimeError("LOGITCAP probe %r count=%d" % (_logitcap_probe, _trial_source.count(_logitcap_probe)))
compile(_trial_source, str(_ps), "exec")
print("LOGITCAP predictor patch applied: 5 anchors x1, SV gain=%s clip=%s (offsets saved, not applied), "
      "window half_zyx=%s, keep_v1284=%s" % (
          os.environ["BIOHUB_SUBVOXEL_GAIN_FIXED"], os.environ["BIOHUB_SUBVOXEL_CLIP"],
          os.environ.get("LOGITCAP_HALF_ZYX", "3,1,1"), os.environ.get("LOGITCAP_KEEP_V1284", "0")), flush=True)
'''

A_WRITE = ("_ps.write_text(_trial_source)\n"
           "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])")

# ----------------------------------------------------------------------------- final cell
SUMMARY_CELL = r'''
# ===== LOGITCAP: summary of the captured detection-logit windows (no training) =====
# Per movie <LOGITCAP_DIR>/<stem>.npz: coords int16 (n,4) [t,z,y,x] on the feature grid (z native,
# y/x = native/4), win float32 (n,7,3,3) blended (or guard-fallback primary) detection logits around
# the peak (out-of-volume = edge value), peak float32, sv float32 (n,3) production SV offsets (gain 2,
# clip 0.4999, grid voxels, not applied), use_primary int8 per detection, per-frame guard columns.
import json
import os
from pathlib import Path

import numpy as np


def logitcap_summary():
    cap_dir = Path(os.environ.get("LOGITCAP_DIR", "/kaggle/working/logitcap"))
    files = sorted(p for p in cap_dir.glob("*.npz") if not p.name.endswith(".partial.npz")) if cap_dir.exists() else []
    partial = sorted(p.name for p in cap_dir.glob("*.partial.npz")) if cap_dir.exists() else []
    selected = [str(s) for s in globals().get("test_stems", [])]
    thr = float(globals().get("DET_THRESHOLD", os.environ.get("BIOHUB_DET_THRESHOLD", "0.5")))
    logit_thr = float(np.log(thr / (1.0 - thr)))
    rows, problems = [], []
    total_dets = total_bytes = 0
    for p in files:
        with np.load(p) as z:
            coords, win, peak, sv = z["coords"], z["win"], z["peak"], z["sv"]
            use_primary, frames, frame_dets = z["use_primary"], z["frames"], z["frame_dets"]
            frame_use_primary = z["frame_use_primary"]
            shape, half = z["shape"].astype(int), z["half_zyx"].astype(int)
        n = int(len(coords))
        hz, hy, hx = (int(h) for h in half)
        ok = (coords.shape == (n, 4) and coords.dtype == np.int16 and win.dtype == np.float32
              and win.shape == (n, 2 * hz + 1, 2 * hy + 1, 2 * hx + 1) and sv.shape == (n, 3)
              and peak.shape == (n,) and use_primary.shape == (n,) and int(frame_dets.sum()) == n
              and len(frames) == len(frame_dets))
        if not ok:
            problems.append(p.stem)
        centre = win[:, hz, hy, hx].astype(np.float32) if ok else np.zeros(0, np.float32)
        core = (win[:, hz - 1:hz + 2, hy - 1:hy + 2, hx - 1:hx + 2].reshape(n, -1).astype(np.float32)
                if ok else np.zeros((0, 27), np.float32))
        zc = coords[:, 1].astype(int)
        row = {"stem": p.stem, "dets": n, "frames": int(len(frames)), "bytes": int(p.stat().st_size),
               "primary_frames": int((frame_use_primary == 1).sum()),
               "guard_unknown_frames": int((frame_use_primary < 0).sum()),
               "centre_is_max": float(np.mean(centre >= core.max(1))) if len(centre) else 1.0,
               "centre_above_thr": float(np.mean(centre >= logit_thr - 0.02)) if len(centre) else 1.0,
               "z_window_hits_edge": float(np.mean((zc < hz) | (zc > int(shape[0]) - 1 - hz))) if n else 0.0,
               "mean_abs_sv_zyx": [round(float(v), 4) for v in (np.abs(sv).mean(0) if n else np.zeros(3))],
               "grid_shape": [int(s) for s in shape], "ok": bool(ok)}
        rows.append(row)
        total_dets += n
        total_bytes += row["bytes"]
        print("LOGITCAP_SUMMARY movie=%s dets=%d frames=%d bytes=%d primary_frames=%d centre_is_max=%.4f "
              "centre_above_thr=%.4f z_window_hits_edge=%.4f mean_abs_sv_zyx=%s grid=%s ok=%s" % (
                  row["stem"], n, row["frames"], row["bytes"], row["primary_frames"], row["centre_is_max"],
                  row["centre_above_thr"], row["z_window_hits_edge"], row["mean_abs_sv_zyx"],
                  row["grid_shape"], ok), flush=True)
    captured = {r["stem"] for r in rows}
    missing = [s for s in selected if s not in captured]
    v1284_dir = Path(os.environ.get("V1284_CAPTURE", "/kaggle/working/v1284cap"))
    v1284_bytes = sum(q.stat().st_size for q in v1284_dir.rglob("*") if q.is_file()) if v1284_dir.exists() else 0
    manifest = {"movies": rows, "selected": selected, "missing": missing, "partial": partial,
                "problems": problems, "total_dets": total_dets, "total_bytes": total_bytes,
                "det_threshold": thr, "keep_v1284": os.environ.get("LOGITCAP_KEEP_V1284", "0"),
                "v1284_capture_bytes": int(v1284_bytes)}
    if cap_dir.exists():
        (cap_dir / "_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"LOGITCAP selected={len(selected)} captured={len(rows)} missing={missing} partial={partial} "
          f"problems={problems} v1284_capture_bytes={v1284_bytes}", flush=True)
    print(f"LOGITCAP DONE movies={len(rows)} dets={total_dets} bytes={total_bytes}", flush=True)
    return manifest


LOGITCAP_MANIFEST = logitcap_summary()
'''


# ----------------------------------------------------------------------------- build
def code_cells(path):
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def replace_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        raise SystemExit("anchor %r matched %d times (need exactly 1)" % (what, n))
    return text.replace(old, new, 1)


def t6_sv_helper():
    """The _SV_HELPER string literal from v_t6stk3 cell 4 (production SV helper), verbatim."""
    _, cells = code_cells(T6 / "kernel.ipynb")
    c4 = cells[4]
    if c4.count(SV_ENV) != 1:
        raise SystemExit("t6stk3 SV env block not found exactly once in v_t6stk3 cell 4")
    found = [node.value.value for node in ast.walk(ast.parse(c4))
             if isinstance(node, ast.Assign) and len(node.targets) == 1
             and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "_SV_HELPER"
             and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)]
    if len(found) != 1:
        raise SystemExit("v_t6stk3 cell 4: _SV_HELPER assignments found = %d" % len(found))
    helper = found[0]
    for probe in ("def _sv_gain():", "def _sv_softarg_offsets(lg, arr):", "_SV_CLIP = float("):
        if helper.count(probe) != 1:
            raise SystemExit("SV helper probe %r count %d" % (probe, helper.count(probe)))
    if REF_T6_PREDICTOR.exists():
        # the real t6stk3 predictor has t6stk3's lcefr lines between the env header and the functions
        ref = REF_T6_PREDICTOR.read_text(encoding="utf-8")
        cut = helper.index("def _sv_gain():")
        for part in (helper[:cut].rstrip(NL), helper[cut:]):
            if ref.count(part) != 1:
                raise SystemExit("SV helper part not verbatim in the real t6stk3 predictor %s" % REF_T6_PREDICTOR)
    return helper


def make_patch(sv_helper):
    for name, text in (("SV helper", sv_helper), ("LOGITCAP helpers", LOGITCAP_HELPERS)):
        if "\\" in text or '"""' in text:
            raise SystemExit("%s cannot be embedded as a triple-quoted literal" % name)
    compile(sv_helper + LOGITCAP_HELPERS, "logitcap_helpers", "exec")
    patch = PATCH_TEMPLATE
    subs = {"@@SV_ENV@@": SV_ENV, "@@SV_HELPER@@": sv_helper, "@@HELPERS@@": LOGITCAP_HELPERS,
            "@@R_HELPER_OLD@@": repr(R_HELPER_OLD), "@@R_INIT_OLD@@": repr(R_INIT_OLD),
            "@@R_INIT_NEW@@": repr(R_INIT_NEW), "@@R_GUARD_OLD@@": repr(R_GUARD_OLD),
            "@@R_GUARD_NEW@@": repr(R_GUARD_NEW), "@@R_DETECT_OLD@@": repr(R_DETECT_OLD),
            "@@R_DETECT_NEW@@": repr(R_DETECT_NEW), "@@R_FLUSH_OLD@@": repr(R_FLUSH_OLD),
            "@@R_FLUSH_NEW@@": repr(R_FLUSH_NEW)}
    for key, val in subs.items():
        if key not in patch:
            raise SystemExit("template key %s missing" % key)
        patch = patch.replace(key, val)
    if "@@" in patch:
        raise SystemExit("unfilled template key in the LOGITCAP patch")
    compile(patch, "logitcap_patch", "exec")
    return patch


def apply_patch_to(predictor_text, patch):
    """Execute the runtime patch exactly as the kernel will, on a predictor text; return the result."""
    ns = {"_trial_source": predictor_text, "_ps": pathlib.PurePosixPath("predict_unet_transformer.py"),
          "os": types.SimpleNamespace(environ={})}
    exec(compile(patch, "logitcap_patch", "exec"), ns)
    return ns["_trial_source"]


def build():
    nb, cells = code_cells(BASE / "kernel.ipynb")
    if len(cells) != 6 or any(c is None for c in cells):
        raise SystemExit("unexpected v_v1284cap layout: %d cells" % len(cells))
    for probe, cell_i in (("# ===== V1284CAP: capture V1284 features on TRAIN movies", 0),
                          ("# --------------------------------- V1284CAP: capture-only predictor", 4),
                          ("V1284CAP_SUMMARY = v1284cap_main()", 5)):
        if cells[cell_i].count(probe) != 1:
            raise SystemExit("base probe %r count %d in cell %d" % (probe, cells[cell_i].count(probe), cell_i))
    if "_sv_softarg_offsets" in "".join(cells) or "LOGITCAP" in "".join(cells):
        raise SystemExit("v_v1284cap already contains an SV / LOGITCAP block")

    patch = make_patch(t6_sv_helper())
    c4 = replace_once(cells[4], A_WRITE, patch.lstrip(NL) + NL + A_WRITE, "V1284 _trial_source write")
    if c4.index("# --------------------------------- LOGITCAP") < c4.index("V1284CAP capture-only predictor patch applied"):
        raise SystemExit("LOGITCAP patch must run after the V1284CAP patch")

    new_cells = [cells[0].rstrip(NL) + NL + CELL0_TAIL, cells[1], cells[2], cells[3], c4, SUMMARY_CELL.lstrip(NL)]
    for i, c in enumerate(new_cells):
        compile(c, "%s:cell%d" % (TAG, i), "exec")
    if "v1284cap_main" in new_cells[5] or "_cap_fit" in new_cells[5]:
        raise SystemExit("training code left in the summary cell")

    # runtime anchors, checked on the REAL patched predictor of the v1284cap run (== _trial_source there)
    if REF_PREDICTOR.exists():
        ref = REF_PREDICTOR.read_text(encoding="utf-8")
        patched = apply_patch_to(ref, patch)
        compile(patched, "predict_unet_transformer.py", "exec")
        print("  runtime patch verified on", REF_PREDICTOR.relative_to(ROOT),
              "(+%d lines)" % (patched.count(NL) - ref.count(NL)))
    else:
        print("  WARNING: reference predictor missing; runtime anchors checked only at kernel time", file=sys.stderr)

    out_cells = []
    for i, src in enumerate(new_cells):
        cell = dict(nb["cells"][i])
        cell["source"] = src.splitlines(keepends=True)
        cell["outputs"] = []
        cell["execution_count"] = None
        out_cells.append(cell)
    nb["cells"] = out_cells

    dest = SK / ("v_" + TAG)
    dest.mkdir(parents=True, exist_ok=True)
    with open(dest / "kernel.ipynb", "w", encoding="utf-8") as fh:
        json.dump(nb, fh)
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + TAG
    meta["title"] = "biohub v " + TAG
    meta["is_private"] = True
    meta["enable_gpu"] = True
    meta["enable_internet"] = False
    with open(dest / "kernel-metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    print("built", dest)
    print("  cells: 0-4 from v_v1284cap (0 +LOGITCAP config, 4 +LOGITCAP predictor patch), 5 = LOGITCAP summary")
    print("  datasets:", meta["dataset_sources"])
    return dest


if __name__ == "__main__":
    build()
