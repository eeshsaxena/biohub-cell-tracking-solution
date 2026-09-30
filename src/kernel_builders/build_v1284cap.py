#!/usr/bin/env python3
"""Derive v_v1284cap: capture V1284 features on many TRAIN movies, then retrain the V1284 head.

usage: python scratch_kernels/build_v1284cap.py

WHY. The public V1284 head was trained on 20 train movies (4,136 detection<->GT pairs) and
held-out-by-movie it cut centre error ~10.8%; its 4-movie version was 14.9% WORSE, so data
volume is the bottleneck. This kernel runs OUR pipeline (v_ourv, unchanged detector + features,
including edge-feature TTA averaging, so the features match what the head sees at inference)
over N train movies in V1284_MODE=capture, then trains the head in the module's exact
parameterisation with leave-movies-out CV against zero-shift and the public head.

The derived kernel is a TRAINING kernel and is never submitted:
  (a) V1284_MODE='capture', V1284_CAPTURE=/kaggle/working/v1284cap (V1284 block's 'candidate'
      assignment is replaced; env reaches the shard subprocesses via {**os.environ}).
  (b) the predictor's own --data-dir / splits-json path is pointed at COMP_DIR/train with a
      deterministic, prefix-stratified list of N train stems (placeholders excluded).
      open_dataset(load_image=False, require_tracks=False) only opens <dir>/<stem>.zarr,
      so no symlink dir is needed.
  (c) cells 5-11 (post-processing, submission, guards, validator, pp-sweep, manifest) are
      dropped; in capture mode the predictor also skips edges/graph/ILP/geff export, and the
      shard merge is replaced by a tolerant wait.
  (d) a final cell matches captures to GT, CVs by movie, trains, saves
      /kaggle/working/v1284_head_retrained.pt (+ summary json + compact candidates npz).
"""
import ast
import json
import pathlib
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourv"
TAG = "v1284cap"
NL = chr(10)

PLACEHOLDER_STEMS = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")

# ----------------------------------------------------------------------------- cell 0 tail
CELL0_TAIL = r'''
# ===== V1284CAP: capture V1284 features on TRAIN movies + retrain the head (NEVER submitted) =====
os.environ.setdefault("V1284CAP_N_MOVIES", "60")              # train movies to capture
os.environ.setdefault("V1284CAP_STRATIFY", "proportional")    # or "equal" (per embryo prefix)
os.environ.setdefault("BIOHUB_CAPTURE_BUDGET_S", str(6 * 3600))  # no NEW movie after this (from shard launch)
os.environ.setdefault("V1284CAP_GATE_UM", "3.0")              # training-pair gate (um)
os.environ.setdefault("V1284CAP_EVAL_GATE_UM", "7.0")         # metric gate, extra CV readout
os.environ.setdefault("V1284CAP_FOLDS", "5")
os.environ.setdefault("V1284CAP_EPOCH_CHECKPOINTS", "25,50,100,200")
os.environ.setdefault("V1284CAP_SHRINKS", "0.5,0.75,1.0")
os.environ.setdefault("V1284CAP_EPOCHS", "auto")              # or an int from the checkpoint list
os.environ.setdefault("V1284CAP_SHRINK", "auto")              # or a float
os.environ.setdefault("V1284CAP_LOSS", "huber")               # huber | mse | l2
os.environ.setdefault("V1284CAP_KEEP_RAW", "0")               # 1 = keep raw per-frame captures
print("ARM_V1284CAP n_movies=%s budget_s=%s gate_um=%s" % (
    os.environ["V1284CAP_N_MOVIES"], os.environ["BIOHUB_CAPTURE_BUDGET_S"],
    os.environ["V1284CAP_GATE_UM"]), flush=True)
'''

# ----------------------------------------------------------------------------- cell 4 edits
A_MODE = "os.environ['V1284_MODE']='candidate'\n"
R_MODE = (
    "os.environ['V1284_MODE']='capture'  # V1284CAP: was candidate; capture features, no refinement\n"
    "os.environ['V1284_CAPTURE']='/kaggle/working/v1284cap'\n"
    "Path(os.environ['V1284_CAPTURE']).mkdir(parents=True, exist_ok=True)\n"
)

A_WRITE = ("_ps.write_text(_trial_source)\n"
           "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])")

# Runs at kernel time on _trial_source (the fully patched predictor, i.e. exactly what
# data/out_ourv/tracking_repo/scripts/predict_unet_transformer.py contains) right before it is written.
CAPTURE_PATCH = r'''
# --------------------------------- V1284CAP: capture-only predictor (derived kernel, never submitted)
# With V1284_MODE=capture the predictor only needs detection + refine()'s feature capture:
#   * the per-pair edge loop is skipped (refine() runs BEFORE it; edges are never used),
#   * graph build / ILP / geff export are skipped,
#   * no NEW movie starts once V1284CAP_DEADLINE_EPOCH has passed (wall-clock guard),
#   * a failing movie is logged and skipped instead of killing the whole shard,
#   * every finished movie writes <V1284_CAPTURE>/<stem>/_DONE.json.
import textwrap as _v1284cap_textwrap
_V1284CAP_EDGE_OLD = "        for f_idx in range(W - 1):\n"
_V1284CAP_EDGE_NEW = ("        for f_idx in (range(0) if os.environ.get('V1284_MODE') == 'capture'"
                      " else range(W - 1)):\n")
if _trial_source.count(_V1284CAP_EDGE_OLD) != 1:
    raise RuntimeError("V1284CAP edge-loop anchor count=%d" % _trial_source.count(_V1284CAP_EDGE_OLD))
_trial_source = _trial_source.replace(_V1284CAP_EDGE_OLD, _V1284CAP_EDGE_NEW, 1)

_V1284CAP_LOOP = ('    for name in tqdm(test_names, desc="Predicting", disable=not INTERACTIVE):\n'
                  '        ds_path = data_dir / name\n')
_V1284CAP_CALL = '        coords, edges = predict_video(\n'
_V1284CAP_CALL_END = '\n            )\n'
if _trial_source.count(_V1284CAP_LOOP + _V1284CAP_CALL) != 1:
    raise RuntimeError("V1284CAP movie-loop anchor count=%d"
                       % _trial_source.count(_V1284CAP_LOOP + _V1284CAP_CALL))
_v1284cap_i0 = _trial_source.index(_V1284CAP_LOOP + _V1284CAP_CALL) + len(_V1284CAP_LOOP)
_v1284cap_i1 = _trial_source.index(_V1284CAP_CALL_END, _v1284cap_i0) + len(_V1284CAP_CALL_END)
# reuse the ORIGINAL call text so the capture run passes exactly the same kwargs
_v1284cap_call = _trial_source[_v1284cap_i0:_v1284cap_i1].replace(
    'coords, edges = predict_video(', '_v1284cap_coords, _v1284cap_edges = predict_video(', 1)
compile(_v1284cap_textwrap.dedent(_v1284cap_call), "v1284cap_call", "exec")
_v1284cap_branch = (
    "        if os.environ.get('V1284_MODE') == 'capture':\n"
    "            import time as _v1284cap_time\n"
    "            if _v1284cap_time.time() > float(os.environ.get('V1284CAP_DEADLINE_EPOCH', 'inf')):\n"
    "                print(f'V1284CAP_BUDGET_SKIP {name}', flush=True)\n"
    "                continue\n"
    "            _v1284cap_start = _v1284cap_time.time()\n"
    "            try:\n"
    + _v1284cap_textwrap.indent(_v1284cap_call, ' ' * 8)
    + "            except Exception as _v1284cap_exc:\n"
    "                print(f'V1284CAP_MOVIE_FAILED {name} {type(_v1284cap_exc).__name__}: {_v1284cap_exc}',\n"
    "                      flush=True)\n"
    "                if torch.cuda.is_available():\n"
    "                    torch.cuda.empty_cache()\n"
    "                continue\n"
    "            _v1284cap_seconds = _v1284cap_time.time() - _v1284cap_start\n"
    "            _v1284cap_marker = Path(os.environ['V1284_CAPTURE']) / ds_path.stem / '_DONE.json'\n"
    "            _v1284cap_marker.parent.mkdir(parents=True, exist_ok=True)\n"
    "            _v1284cap_marker.write_text(json.dumps({'stem': ds_path.stem,\n"
    "                'detections': int(len(_v1284cap_coords)), 'seconds': round(_v1284cap_seconds, 1)}))\n"
    "            print(f'V1284CAP_MOVIE_DONE {name} detections={len(_v1284cap_coords)} '\n"
    "                  f'seconds={_v1284cap_seconds:.1f}', flush=True)\n"
    "            continue\n"
)
_trial_source = _trial_source[:_v1284cap_i0] + _v1284cap_branch + _trial_source[_v1284cap_i0:]
compile(_trial_source, str(_ps), "exec")
print("V1284CAP capture-only predictor patch applied (edges/ILP/geff skipped, budget guard on)",
      flush=True)
'''

A_STEMS = ('test_stems = list_test_stems()\n'
           'print(f"Found {len(test_stems)} test videos")\n'
           'print(test_stems[:10])\n')

SELECT_FN = r'''
def _v1284cap_select(stems, n_want, exclude, mode="proportional"):
    """Deterministic, embryo-prefix-stratified train-stem selection.

    Within a prefix the order is sha1(stem); quotas are proportional (largest remainder) or
    equal. The returned list is interleaved so that EVERY prefix of it is itself stratified:
    the shards take [i::2] of it, and the wall-clock guard cuts each shard's tail.
    """
    import hashlib as _h
    pool = sorted(s for s in set(stems) if s not in set(exclude))
    by_prefix = {}
    for s in pool:
        by_prefix.setdefault(s.split("_")[0], []).append(s)
    for p in by_prefix:
        by_prefix[p].sort(key=lambda s: _h.sha1(s.encode()).hexdigest())
    n_want = max(0, min(int(n_want), len(pool)))
    prefixes = sorted(by_prefix)
    if mode == "equal":
        quota = {p: 0 for p in prefixes}
        left = n_want
        while left > 0:
            progressed = False
            for p in prefixes:
                if left and quota[p] < len(by_prefix[p]):
                    quota[p] += 1
                    left -= 1
                    progressed = True
            if not progressed:
                break
    else:
        exact = {p: n_want * len(by_prefix[p]) / max(1, len(pool)) for p in prefixes}
        quota = {p: int(exact[p]) for p in prefixes}
        rest = sorted(prefixes, key=lambda p: (-(exact[p] - quota[p]), p))
        for p in rest[: n_want - sum(quota.values())]:
            quota[p] += 1
    ranked = []
    for p in prefixes:
        for r, s in enumerate(by_prefix[p][: quota[p]]):
            ranked.append(((r + 0.5) / quota[p], p, s))
    return [s for _, _, s in sorted(ranked)]
'''

R_STEMS = (SELECT_FN + r'''

V1284CAP_TRAIN_DIR = COMP_DIR / "train"
V1284CAP_EXCLUDE = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")  # test placeholders
_v1284cap_all = sorted(p.name[:-5] for p in V1284CAP_TRAIN_DIR.iterdir() if p.name.endswith(".zarr"))
_v1284cap_all = [s for s in _v1284cap_all if (V1284CAP_TRAIN_DIR / f"{s}.geff").exists()]
test_stems = _v1284cap_select(_v1284cap_all, int(os.environ["V1284CAP_N_MOVIES"]), V1284CAP_EXCLUDE,
                              os.environ.get("V1284CAP_STRATIFY", "proportional"))
if not test_stems or set(test_stems) & set(V1284CAP_EXCLUDE):
    raise RuntimeError("V1284CAP train-stem selection failed")
print("V1284CAP selected %d train movies (eligible %d, placeholders excluded) per prefix %s" % (
    len(test_stems), len([s for s in _v1284cap_all if s not in V1284CAP_EXCLUDE]),
    {p: sum(s.startswith(p + "_") for s in test_stems) for p in sorted({s.split("_")[0] for s in test_stems})}),
    flush=True)
print(test_stems)
''')

A_DATADIR = '    "--data-dir",\n    str(TEST_DIR),\n'
R_DATADIR = '    "--data-dir",\n    str(V1284CAP_TRAIN_DIR),  # V1284CAP: train movies, not test\n'

A_START = "start_time = time.time()\n"
R_START = ('os.environ["V1284CAP_DEADLINE_EPOCH"] = str(time.time() + float(os.environ["BIOHUB_CAPTURE_BUDGET_S"]))\n'
           'print("V1284CAP no new movie after", time.strftime("%H:%M:%S", time.gmtime(float('
           'os.environ["V1284CAP_DEADLINE_EPOCH"]))), "UTC", flush=True)\n'
           "start_time = time.time()\n")

A_MERGE = ("    _wait_for_prediction_shards(processes, commands)\n"
           "    _merge_prediction_shards(worker_count)\n")
R_MERGE = ("    # V1284CAP: wait for EVERY shard (a failure must not kill the other shard, whose finished\n"
           "    # movies are already captured) and skip the geff merge: capture mode writes no graphs.\n"
           "    _v1284cap_rc = {i: p.wait() for i, p in processes.items()}\n"
           "    print('V1284CAP shard return codes:', _v1284cap_rc, flush=True)\n")

# ----------------------------------------------------------------------------- final cell
TRAIN_CELL = r'''
# ===== V1284CAP: retrain the V1284 learned coordinate head on the captured TRAIN movies =====
# Capture layout: <V1284_CAPTURE>/<stem>/<t:04d>.npz with coords=(n,4) int16 [t, z, y, x] on the
# UNet FEATURE grid (config downsample (1,4,4): native = grid * (1,4,4)) and features=(n,224).
# One feature-grid voxel is 1.625 um on every axis (module SPACING); GT geff nodes are NATIVE voxels
# with (z,y,x) scale (1.625, 0.40625, 0.40625) um. So det_um = grid*1.625 and gt_um = native*scale,
# target_um = gt_um - det_um, which is exactly what refine() adds back:
#   result[:,1:] += bounded(head((x-mean)/scale)) / SPACING  ->  native = result*(1,4,4).
import hashlib
import importlib.util
import json
import math
import os
import shutil
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import zarr
from scipy.optimize import linear_sum_assignment

V1284CAP_VOXEL_UM = np.array([1.625, 0.40625, 0.40625], dtype=np.float64)


def _cap_load_module(path):
    spec = importlib.util.spec_from_file_location("v1284_refinement_for_training", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cap_read_gt(geff):
    cols = []
    for key in ("t", "z", "y", "x"):
        arr = zarr.open_array(str(Path(geff) / "nodes" / "props" / key / "values"), mode="r")
        cols.append(np.asarray(arr[:], dtype=np.float64))
    return np.stack(cols, axis=1)


def _cap_assign(cost, gate):
    """Metric-style matching: optimal bipartite assignment, pairs above the gate dropped."""
    big = 1e6
    gated = np.where(cost <= gate, cost, big)
    rows, cols = linear_sum_assignment(gated)
    keep = gated[rows, cols] < big
    return rows[keep], cols[keep]


def _cap_collect(cap_dir, gt_dir, spacing, cand_gate):
    """Load every captured frame that has GT; keep detections within cand_gate um of a GT node."""
    movies, feats, dets, det_movie, gts, gt_movie = [], [], [], [], [], []
    nn_expected, nn_control = [], []
    for folder in sorted(p for p in Path(cap_dir).iterdir() if p.is_dir()):
        stem = folder.name
        geff = Path(gt_dir) / f"{stem}.geff"
        frames = {int(p.stem): p for p in folder.glob("[0-9][0-9][0-9][0-9].npz")}
        if not frames:
            continue
        if not geff.exists():
            print(f"V1284CAP WARNING no GT geff for {stem}; skipped", flush=True)
            continue
        gt = _cap_read_gt(geff)
        mi = len(movies)
        n_gt_cov = 0
        n_det_frames = 0
        for t in sorted(set(gt[:, 0].astype(int).tolist())):
            if t not in frames:
                continue
            with np.load(frames[t]) as z:
                coords = np.asarray(z["coords"])
                features = np.asarray(z["features"], dtype=np.float32)
            g = gt[gt[:, 0].astype(int) == t]
            n_gt_cov += len(g)
            gts.append(g)
            gt_movie.append(np.full(len(g), mi, dtype=np.int32))
            if not len(coords):
                continue
            if coords.ndim != 2 or coords.shape[1] != 4 or features.shape != (len(coords), 224):
                raise RuntimeError(f"bad capture {frames[t]}: coords {coords.shape} features {features.shape}")
            if np.any(coords[:, 0].astype(int) != t):
                raise RuntimeError(f"capture t column mismatch in {frames[t]}")
            n_det_frames += 1
            det_um = coords[:, 1:].astype(np.float64) * spacing
            gt_um = g[:, 1:] * V1284CAP_VOXEL_UM
            d = np.sqrt(((gt_um[:, None, :] - det_um[None, :, :]) ** 2).sum(-1))
            nn_expected.append(d.min(axis=1))
            ctrl_um = coords[:, 1:].astype(np.float64) * V1284CAP_VOXEL_UM  # control: forget the x4
            nn_control.append(np.sqrt(((gt_um[:, None, :] - ctrl_um[None, :, :]) ** 2).sum(-1)).min(axis=1))
            keep = np.flatnonzero((d <= cand_gate).any(axis=0))
            feats.append(features[keep])
            dets.append(coords[keep].astype(np.int16))
            det_movie.append(np.full(len(keep), mi, dtype=np.int32))
        movies.append({"stem": stem, "gt_nodes": int(len(gt)), "gt_nodes_in_captured_frames": int(n_gt_cov),
                       "frames_captured": len(frames), "gt_frames_with_detections": n_det_frames,
                       "complete": (folder / "_DONE.json").exists()})
    cat = lambda xs, shape, dt: np.concatenate(xs) if xs else np.zeros(shape, dt)
    return {
        "movies": movies,
        "feats": cat(feats, (0, 224), np.float32),
        "dets": cat(dets, (0, 4), np.int16),
        "det_movie": cat(det_movie, (0,), np.int32),
        "gt": cat(gts, (0, 4), np.float64),
        "gt_movie": cat(gt_movie, (0,), np.int32),
        "nn_expected": cat(nn_expected, (0,), np.float64),
        "nn_control": cat(nn_control, (0,), np.float64),
    }


def _cap_pairs(data, spacing, gate):
    """Hungarian matching per (movie, t) between GT nodes and candidate detections."""
    det_um = data["dets"][:, 1:].astype(np.float64) * spacing
    gt_um = data["gt"][:, 1:] * V1284CAP_VOXEL_UM
    det_key = data["det_movie"].astype(np.int64) * 100000 + data["dets"][:, 0].astype(np.int64)
    gt_key = data["gt_movie"].astype(np.int64) * 100000 + data["gt"][:, 0].astype(np.int64)
    det_groups = {}
    for i, k in enumerate(det_key.tolist()):
        det_groups.setdefault(k, []).append(i)
    di_all, gi_all = [], []
    gt_groups = {}
    for i, k in enumerate(gt_key.tolist()):
        gt_groups.setdefault(k, []).append(i)
    for k, gi in gt_groups.items():
        di = det_groups.get(k)
        if not di:
            continue
        gi = np.asarray(gi)
        di = np.asarray(di)
        cost = np.sqrt(((gt_um[gi][:, None, :] - det_um[di][None, :, :]) ** 2).sum(-1))
        r, c = _cap_assign(cost, gate)
        gi_all.append(gi[r])
        di_all.append(di[c])
    di_all = np.concatenate(di_all) if di_all else np.zeros(0, np.int64)
    gi_all = np.concatenate(gi_all) if gi_all else np.zeros(0, np.int64)
    return {
        "X": data["feats"][di_all],
        "Y": gt_um[gi_all] - det_um[di_all],
        "movie": data["det_movie"][di_all],
    }


def _cap_folds(stems, k):
    """Deterministic movie folds: sha1 order within prefix, running index across prefixes."""
    by = {}
    for s in sorted(stems, key=lambda s: hashlib.sha1(s.encode()).hexdigest()):
        by.setdefault(s.split("_")[0], []).append(s)
    fold, i = {}, 0
    for p in sorted(by):
        for s in by[p]:
            fold[s] = i % k
            i += 1
    return fold


def _cap_loss(pred, y, name, delta):
    if name == "mse":
        return ((pred - y) ** 2).sum(-1).mean()
    if name == "l2":
        return torch.sqrt(((pred - y) ** 2).sum(-1) + 1e-6).mean()
    if name == "huber":
        return F.huber_loss(pred, y, delta=delta, reduction="none").sum(-1).mean()
    raise ValueError(f"unknown V1284CAP_LOSS {name!r}")


def _cap_fit(mod, X, Y, checkpoints, seed, lr, wd, batch, loss, delta, device="cpu"):
    """Train make_head() on standardised features; snapshot the state at each checkpoint epoch."""
    X = torch.as_tensor(X, dtype=torch.float32, device=device)
    Y = torch.as_tensor(Y, dtype=torch.float32, device=device)
    mean = X.mean(0)
    scale = X.std(0).clamp_min(1e-6)
    xn = (X - mean) / scale
    torch.manual_seed(seed)
    head = mod.make_head().to(device)  # init on CPU (seeded), then moved
    opt = torch.optim.AdamW(head.parameters(), lr=lr, weight_decay=wd)
    gen = torch.Generator().manual_seed(seed)
    snaps, n = {}, len(X)
    head.train()
    for epoch in range(1, max(checkpoints) + 1):
        perm = torch.randperm(n, generator=gen).to(device)
        for i in range(0, n, batch):
            idx = perm[i:i + batch]
            value = _cap_loss(mod.bounded(head, xn[idx]), Y[idx], loss, delta)
            opt.zero_grad(set_to_none=True)
            value.backward()
            opt.step()
        if epoch in checkpoints:
            snaps[epoch] = {k: v.detach().cpu().clone() for k, v in head.state_dict().items()}
    return snaps, mean.cpu(), scale.cpu()


@torch.no_grad()
def _cap_predict(mod, state, mean, scale, X, shrink=1.0):
    head = mod.make_head()
    head.load_state_dict(state)
    head.eval()
    if shrink != 1.0:
        head[-1].weight.mul_(shrink)
        head[-1].bias.mul_(shrink)
    if not len(X):
        return np.zeros((0, 3))
    xn = (torch.as_tensor(X, dtype=torch.float32) - mean.float()) / scale.float()
    return mod.bounded(head, xn).numpy().astype(np.float64)


def _cap_err(Y, P):
    return np.linalg.norm(Y - P, axis=1)


def _cap_module_smoke(mod, head_path):
    """Load the saved file through the module's own candidate-mode refine() path."""
    old = {k: os.environ.get(k) for k in ("V1284_MODE", "V1284_HEAD")}
    os.environ["V1284_MODE"] = "candidate"
    os.environ["V1284_HEAD"] = str(head_path)
    mod._CACHE = None
    try:
        g = torch.Generator().manual_seed(0)
        feature = torch.randn(1, 32, 6, 24, 24, generator=g)
        arr = np.array([[3, 0, 0, 0], [3, 2, 11, 7], [3, 5, 23, 23]], dtype=np.int16)
        with torch.no_grad():  # predict_video() is @torch.no_grad(); refine() relies on it
            out = mod.refine(Path("v1284cap_smoke"), 3, arr, feature)
        if out.shape != arr.shape or not np.isfinite(out).all():
            raise RuntimeError("V1284CAP smoke: bad refine output")
        return float(np.linalg.norm((out[:, 1:] - arr[:, 1:]) * mod.SPACING, axis=1).max())
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        mod._CACHE = None


def _cap_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def v1284cap_main():
    t0 = time.time()
    cap_dir = Path(os.environ["V1284_CAPTURE"])
    gt_dir = Path(os.environ.get("V1284CAP_GT_DIR", str(COMP_DIR / "train")))
    out_dir = Path(os.environ.get("V1284CAP_OUT_DIR", str(WORKING_DIR)))
    module_path = Path(os.environ.get("V1284CAP_MODULE", str(_ps.parent / "v1284_coordinate_refinement.py")))
    gate = float(os.environ.get("V1284CAP_GATE_UM", "3.0"))
    eval_gate = float(os.environ.get("V1284CAP_EVAL_GATE_UM", "7.0"))
    n_folds = int(os.environ.get("V1284CAP_FOLDS", "5"))
    checkpoints = sorted({int(v) for v in os.environ.get("V1284CAP_EPOCH_CHECKPOINTS", "25,50,100,200").split(",")})
    shrinks = sorted({float(v) for v in os.environ.get("V1284CAP_SHRINKS", "0.5,0.75,1.0").split(",")})
    epochs_env = os.environ.get("V1284CAP_EPOCHS", "auto")
    shrink_env = os.environ.get("V1284CAP_SHRINK", "auto")
    if epochs_env != "auto":
        checkpoints = sorted(set(checkpoints) | {int(epochs_env)})
    if shrink_env != "auto":
        shrinks = sorted(set(shrinks) | {float(shrink_env)})
    lr = float(os.environ.get("V1284CAP_LR", "1e-3"))
    wd = float(os.environ.get("V1284CAP_WD", "1e-2"))
    batch = int(os.environ.get("V1284CAP_BATCH", "512"))
    device = os.environ.get("V1284CAP_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
    loss = os.environ.get("V1284CAP_LOSS", "huber")
    delta = float(os.environ.get("V1284CAP_HUBER_DELTA_UM", "1.0"))
    seed = int(os.environ.get("V1284CAP_SEED", "1284"))
    keep_raw = os.environ.get("V1284CAP_KEEP_RAW", "0") != "0"
    if gate > eval_gate:
        raise ValueError("V1284CAP_GATE_UM must be <= V1284CAP_EVAL_GATE_UM")
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

    mod = _cap_load_module(module_path)
    spacing = np.asarray(mod.SPACING, dtype=np.float64)
    if not np.allclose(spacing, [1.625, 1.625, 1.625]):
        raise RuntimeError(f"unexpected module SPACING {spacing}")

    # ---- public head (what v_ourv applies today, on these same features)
    pub_env = os.environ.get("V1284CAP_PUBLIC_HEAD", "")
    pub_paths = [Path(pub_env)] if pub_env else sorted(
        p for p in Path("/kaggle/input").rglob("v1284_head.pt") if "biohub-v1284-head-s075" in str(p))
    public = None
    if pub_paths and pub_paths[0].is_file():
        saved = torch.load(str(pub_paths[0]), map_location="cpu", weights_only=True)
        public = (saved["state_dict"], saved["mean"].float(), saved["scale"].float(), saved)
        print("V1284CAP public head:", pub_paths[0], flush=True)
    else:
        print("V1284CAP WARNING public head not found; public column will be nan", flush=True)

    # ---- captures + GT
    done = sorted(p.parent.name for p in cap_dir.glob("*/_DONE.json"))
    started = sorted(p.name for p in cap_dir.iterdir() if p.is_dir()) if cap_dir.exists() else []
    print(f"V1284CAP capture dirs={len(started)} complete={len(done)} partial={sorted(set(started) - set(done))}",
          flush=True)
    data = _cap_collect(cap_dir, gt_dir, spacing, eval_gate)
    stems = [m["stem"] for m in data["movies"]]

    # ---- coordinate-conversion check (nearest detection per GT node)
    nn_e, nn_c = data["nn_expected"], data["nn_control"]
    med_e = float(np.median(nn_e)) if len(nn_e) else float("nan")
    med_c = float(np.median(nn_c)) if len(nn_c) else float("nan")
    conv_ok = bool(len(nn_e) and med_e <= 3.0 and med_e < 0.5 * med_c)
    print(f"V1284CAP conversion_check median_nn_um expected(grid*1.625)={med_e:.3f} "
          f"control(no x4)={med_c:.3f} ok={conv_ok}", flush=True)

    # ---- compact candidates file (everything within the eval gate of a GT node), kept for offline work
    cand_path = out_dir / "v1284cap_candidates.npz"
    np.savez_compressed(cand_path, feats=data["feats"], dets=data["dets"], det_movie=data["det_movie"],
                        gt=data["gt"], gt_movie=data["gt_movie"], movies=np.array(stems),
                        spacing_um=spacing, voxel_um=V1284CAP_VOXEL_UM, cand_gate_um=eval_gate)
    print(f"V1284CAP candidates saved {cand_path} rows={len(data['feats'])} "
          f"({cand_path.stat().st_size / 1e6:.1f} MB)", flush=True)

    tr = _cap_pairs(data, spacing, gate)
    ev = _cap_pairs(data, spacing, eval_gate)
    d_ev = np.linalg.norm(ev["Y"], axis=1)
    movies_with_pairs = sorted({stems[i] for i in tr["movie"].tolist()})
    print(f"V1284CAP movies={len(movies_with_pairs)} pairs={len(tr['Y'])} "
          f"(pairs@{eval_gate:g}um={len(ev['Y'])}, gt_nodes_in_captured_frames="
          f"{sum(m['gt_nodes_in_captured_frames'] for m in data['movies'])})", flush=True)
    dist_summary = {}
    if len(d_ev):
        q = np.percentile(d_ev, [10, 25, 50, 75, 90])
        dist_summary = {"p10": q[0], "p25": q[1], "p50": q[2], "p75": q[3], "p90": q[4],
                        "mean": float(d_ev.mean()), "frac_le_2um": float(np.mean(d_ev <= 2.0)),
                        "frac_le_3um": float(np.mean(d_ev <= 3.0)),
                        "mean_signed_um_zyx": ev["Y"].mean(0).round(4).tolist()}
        dist_summary = {k: (round(float(v), 4) if not isinstance(v, list) else v) for k, v in dist_summary.items()}
        print(f"V1284CAP matched_dist_um@{eval_gate:g} " + json.dumps(dist_summary), flush=True)
    summary = {"conversion_check": {"median_nn_expected_um": med_e, "median_nn_control_um": med_c, "ok": conv_ok},
               "movies": data["movies"], "gate_um": gate, "eval_gate_um": eval_gate,
               "pairs": int(len(tr["Y"])), "pairs_eval_gate": int(len(ev["Y"])),
               "matched_distance_um": dist_summary, "candidates_file": str(cand_path)}
    summary_path = out_dir / "v1284_head_retrained_summary.json"
    if not conv_ok:
        summary["error"] = "conversion check failed"
        summary_path.write_text(json.dumps(summary, indent=2))
        raise RuntimeError("V1284CAP coordinate conversion check failed; raw captures kept for inspection")
    if len(tr["Y"]) < 200 or len(movies_with_pairs) < 2:
        summary["error"] = "too few pairs"
        summary_path.write_text(json.dumps(summary, indent=2))
        raise RuntimeError(f"V1284CAP too few training pairs ({len(tr['Y'])}) / movies ({len(movies_with_pairs)})")

    # ---- leave-movies-out CV: zero shift vs public head vs retrained (epoch x shrink grid)
    k = min(n_folds, len(movies_with_pairs))
    fold_of = _cap_folds(movies_with_pairs, k)
    fold_tr = np.array([fold_of.get(stems[i], -1) for i in tr["movie"].tolist()], dtype=np.int64)
    # eval-gate pairs only from movies that have a fold (i.e. at least one train-gate pair)
    ev_keep = np.array([stems[i] in fold_of for i in ev["movie"].tolist()], dtype=bool)
    ev = {key: val[ev_keep] for key, val in ev.items()}
    d_ev = np.linalg.norm(ev["Y"], axis=1)
    fold_ev = np.array([fold_of[stems[i]] for i in ev["movie"].tolist()], dtype=np.int64)
    configs = [(e, s) for e in checkpoints for s in shrinks]
    err_tr = {c: np.full(len(tr["Y"]), np.nan) for c in configs}
    err_ev = {c: np.full(len(ev["Y"]), np.nan) for c in configs}
    pub_tr = (_cap_err(tr["Y"], _cap_predict(mod, public[0], public[1], public[2], tr["X"])) if public
              else np.full(len(tr["Y"]), np.nan))
    pub_ev = (_cap_err(ev["Y"], _cap_predict(mod, public[0], public[1], public[2], ev["X"])) if public
              else np.full(len(ev["Y"]), np.nan))
    zero_tr = np.linalg.norm(tr["Y"], axis=1)
    zero_ev = d_ev
    for f in range(k):
        train_mask = fold_tr != f
        snaps, mean, scale = _cap_fit(mod, tr["X"][train_mask], tr["Y"][train_mask], set(checkpoints),
                                      seed + f, lr, wd, batch, loss, delta, device)
        for (e, s) in configs:
            m = fold_tr == f
            err_tr[(e, s)][m] = _cap_err(tr["Y"][m], _cap_predict(mod, snaps[e], mean, scale, tr["X"][m], s))
            m = fold_ev == f
            err_ev[(e, s)][m] = _cap_err(ev["Y"][m], _cap_predict(mod, snaps[e], mean, scale, ev["X"][m], s))
        print(f"V1284CAP fold {f} trained on {int(train_mask.sum())} pairs "
              f"({time.time() - t0:.0f}s elapsed)", flush=True)
    grid = {f"e{e}_s{s:g}": {"cv_err": round(float(np.nanmean(err_tr[(e, s)])), 4),
                             "cv_err_eval_gate": round(float(np.nanmean(err_ev[(e, s)])), 4)}
            for (e, s) in configs}
    print("V1284CAP cv grid (train-gate err / eval-gate err): " + json.dumps(grid), flush=True)
    best = min(configs, key=lambda c: (np.nanmean(err_tr[c]), -c[1], c[0]))
    chosen = (int(epochs_env) if epochs_env != "auto" else best[0],
              float(shrink_env) if shrink_env != "auto" else best[1])
    fold_rows = []
    for f in range(k):
        m, mv = fold_tr == f, fold_ev == f
        row = {"fold": f, "movies": sorted(s for s, ff in fold_of.items() if ff == f), "pairs": int(m.sum()),
               "zero": float(zero_tr[m].mean()), "public": float(np.nanmean(pub_tr[m])),
               "retrained": float(err_tr[chosen][m].mean()),
               "zero_eval_gate": float(zero_ev[mv].mean()) if mv.any() else float("nan"),
               "public_eval_gate": float(np.nanmean(pub_ev[mv])) if mv.any() else float("nan"),
               "retrained_eval_gate": float(err_ev[chosen][mv].mean()) if mv.any() else float("nan")}
        fold_rows.append(row)
        print(f"V1284CAP fold {f} movies={len(row['movies'])} pairs={row['pairs']} err_um zero={row['zero']:.4f} "
              f"public={row['public']:.4f} retrained={row['retrained']:.4f} "
              f"({100 * (row['retrained'] / row['zero'] - 1):+.1f}% vs zero) | @{eval_gate:g}um "
              f"zero={row['zero_eval_gate']:.4f} public={row['public_eval_gate']:.4f} "
              f"retrained={row['retrained_eval_gate']:.4f}", flush=True)
    per_movie = []
    for mi_stem in movies_with_pairs:
        m = np.array([stems[i] == mi_stem for i in tr["movie"].tolist()])
        per_movie.append({"stem": mi_stem, "pairs": int(m.sum()), "zero": float(zero_tr[m].mean()),
                          "public": float(np.nanmean(pub_tr[m])), "retrained": float(err_tr[chosen][m].mean())})
    n_better = sum(r["retrained"] < r["zero"] for r in per_movie)
    n_better_pub = sum(r["retrained"] < r["public"] for r in per_movie)
    cv = {"zero": float(zero_tr.mean()), "public": float(np.nanmean(pub_tr)),
          "retrained": float(err_tr[chosen].mean()),
          "zero_eval_gate": float(zero_ev.mean()), "public_eval_gate": float(np.nanmean(pub_ev)),
          "retrained_eval_gate": float(err_ev[chosen].mean())}
    print(f"V1284CAP cv_err zero={cv['zero']:.4f} public={cv['public']:.4f} retrained={cv['retrained']:.4f} "
          f"| retrained vs zero {100 * (cv['retrained'] / cv['zero'] - 1):+.1f}% vs public "
          f"{100 * (cv['retrained'] / cv['public'] - 1):+.1f}% | movies improved vs zero {n_better}/{len(per_movie)} "
          f"vs public {n_better_pub}/{len(per_movie)} | config epochs={chosen[0]} shrink={chosen[1]:g}", flush=True)
    print(f"V1284CAP cv_err@{eval_gate:g}um zero={cv['zero_eval_gate']:.4f} public={cv['public_eval_gate']:.4f} "
          f"retrained={cv['retrained_eval_gate']:.4f}", flush=True)

    # ---- final head on ALL movies, identical checkpoint format to the public head
    snaps, mean, scale = _cap_fit(mod, tr["X"], tr["Y"], {chosen[0]}, seed + 1000, lr, wd, batch, loss, delta,
                                  device)
    head = mod.make_head()
    head.load_state_dict(snaps[chosen[0]])
    with torch.no_grad():
        head[-1].weight.mul_(chosen[1])
        head[-1].bias.mul_(chosen[1])
    payload = {"state_dict": {k2: v.detach().cpu().float().contiguous().clone() for k2, v in head.state_dict().items()},
               "mean": mean.detach().cpu().float().contiguous().clone(),
               "scale": scale.detach().cpu().float().contiguous().clone()}
    head_path = out_dir / "v1284_head_retrained.pt"
    torch.save(payload, str(head_path))
    back = torch.load(str(head_path), map_location="cpu", weights_only=True)
    ref = public[3] if public else {"state_dict": mod.make_head().state_dict(),
                                    "mean": torch.zeros(224), "scale": torch.ones(224)}
    if set(back) != set(ref) or set(back["state_dict"]) != set(ref["state_dict"]):
        raise RuntimeError("V1284CAP saved head keys differ from the public head")
    for k2 in ref["state_dict"]:
        a, b = back["state_dict"][k2], ref["state_dict"][k2]
        if a.shape != b.shape or a.dtype != b.dtype:
            raise RuntimeError(f"V1284CAP saved head {k2} {a.shape}/{a.dtype} != {b.shape}/{b.dtype}")
    for k2 in ("mean", "scale"):
        if back[k2].shape != ref[k2].shape or back[k2].dtype != ref[k2].dtype:
            raise RuntimeError(f"V1284CAP saved head {k2} shape/dtype mismatch")
    smoke_max_um = _cap_module_smoke(mod, head_path)
    in_sample = _cap_err(tr["Y"], _cap_predict(mod, back["state_dict"], back["mean"], back["scale"], tr["X"]))
    print(f"V1284CAP saved {head_path} sha256={_cap_sha256(head_path)[:16]} in_sample_err={in_sample.mean():.4f} "
          f"module_refine_smoke_max_shift_um={smoke_max_um:.3f}", flush=True)

    summary.update({"cv": cv, "folds": fold_rows, "per_movie": per_movie, "grid": grid,
                    "chosen": {"epochs": chosen[0], "shrink": chosen[1], "auto_epochs": epochs_env == "auto",
                               "auto_shrink": shrink_env == "auto"},
                    "train": {"loss": loss, "huber_delta_um": delta, "lr": lr, "weight_decay": wd, "batch": batch,
                              "seed": seed, "folds": k, "device": device},
                    "movies_improved_vs_zero": n_better, "movies_improved_vs_public": n_better_pub,
                    "head_file": str(head_path), "head_sha256": _cap_sha256(head_path),
                    "public_head_file": str(pub_paths[0]) if public else None,
                    "in_sample_err": float(in_sample.mean()), "seconds": round(time.time() - t0, 1)})
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"V1284CAP summary {summary_path}", flush=True)
    if not keep_raw and cap_dir.exists():
        shutil.rmtree(cap_dir)
        print(f"V1284CAP raw captures removed ({cap_dir}); v1284cap_candidates.npz keeps every detection "
              f"within {eval_gate:g} um of a GT node", flush=True)
    print(f"V1284CAP train_cell_seconds={time.time() - t0:.0f}", flush=True)
    return summary


V1284CAP_SUMMARY = v1284cap_main()
'''


def code_cells(path):
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def replace_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        raise SystemExit("anchor %r matched %d times (need exactly 1)" % (what, n))
    return text.replace(old, new, 1)


def module_source(cell4):
    """The v1284_coordinate_refinement.py string literal written by the V1284 block."""
    for node in ast.walk(ast.parse(cell4)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "write_text" and node.args
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
                and "def refine(" in node.args[0].value):
            return node.args[0].value
    raise SystemExit("V1284 module string not found in cell 4")


def build():
    nb, cells = code_cells(BASE / "kernel.ipynb")
    if len(cells) != 12 or any(c is None for c in cells):
        raise SystemExit("unexpected v_ourv layout: %d cells" % len(cells))

    c4 = cells[4]
    c4 = replace_once(c4, A_MODE, R_MODE, "V1284_MODE candidate")
    c4 = replace_once(c4, A_WRITE, CAPTURE_PATCH.lstrip(NL) + NL + A_WRITE, "V1284 _trial_source write")
    c4 = replace_once(c4, A_STEMS, R_STEMS.lstrip(NL), "test_stems = list_test_stems()")
    c4 = replace_once(c4, A_DATADIR, R_DATADIR, "--data-dir TEST_DIR")
    c4 = replace_once(c4, A_START, R_START, "start_time")
    c4 = replace_once(c4, A_MERGE, R_MERGE, "shard wait+merge")
    for probe in ("'candidate'", "_merge_prediction_shards(worker_count)\n", "str(TEST_DIR)"):
        if probe in c4.replace("def _merge_prediction_shards(worker_count", ""):
            raise SystemExit("leftover after edits: %r" % probe)

    new_cells = [cells[0].rstrip(NL) + NL + CELL0_TAIL, cells[1], cells[2], cells[3], c4,
                 TRAIN_CELL.lstrip(NL)]
    for i, c in enumerate(new_cells):
        compile(c, "%s:cell%d" % (TAG, i), "exec")
    compile(module_source(c4), "v1284_coordinate_refinement.py", "exec")

    out_cells = []
    for i, src in enumerate(new_cells):
        cell = dict(nb["cells"][i]) if i < 5 else {"cell_type": "code", "metadata": {}}
        cell["source"] = src.splitlines(keepends=True)
        cell["outputs"] = []
        cell["execution_count"] = None
        out_cells.append(cell)
    nb["cells"] = out_cells

    dest = SK / ("v_" + TAG)
    dest.mkdir(parents=True, exist_ok=True)
    json.dump(nb, open(dest / "kernel.ipynb", "w", encoding="utf-8"))
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + TAG
    meta["title"] = "biohub v " + TAG
    meta["enable_gpu"] = True
    meta["enable_internet"] = False
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest)
    print("  cells: 0-4 from v_ourv (0 +config, 4 patched), 5 = V1284CAP training; dropped v_ourv cells 5-11")
    print("  datasets:", meta["dataset_sources"])
    return dest


if __name__ == "__main__":
    build()
