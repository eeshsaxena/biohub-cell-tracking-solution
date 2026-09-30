"""Build a CV RECALL PROBE kernel (no submission cost).

Reuses the EXACT detection stack of the 0.917 Kunal notebook (cells 0-3: model
loading + helpers + the 3-branch flip-TTA heatmaps), then, instead of writing a
submission, runs on TRAIN movies (which have local .geff GT) and measures, per
detection strategy, the node RECALL over the sparse annotated nuclei -- the one
lever that governs the score (edge_J ~= recall^2).

Strategies compared on identical heatmaps (so the comparison is apples-to-apples):
  avg@0.15  current 0.917 detection (mean of 3 branch maps, seed thr 0.15)
  avg@0.10  = the queued recall10 ablation (lower global thr)
  avg@0.08  even lower global thr
  union@0.15  per-branch peaks>=0.15, refined, UNION, physical NMS  <-- the idea
  union@0.12  slightly more permissive union
  modelA/B/C  each branch alone @0.15 (to measure MISS CORRELATION s)

Also reports mean detections/frame vs estimated_number_of_nodes (node_ratio), and
splits results by embryo (44b6 vs 6bba) because the test is 2 UNSEEN embryos and
generalisation is the whole point.

Output: printed table only. Pushing/running this costs GPU time, NOT a submission.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
OUT_DIR = HERE / "probe_union_cv"
OUT_DIR.mkdir(exist_ok=True)

src = json.loads(SRC_NB.read_text(encoding="utf-8"))
# Reuse cells 0,1,2,3 verbatim: model loading, helpers, linker, 3-branch TTA setup.
base_cells = [src["cells"][i] for i in (0, 1, 2, 3)]

# The Kaggle base image lacks zarr; the submission reads .zarr via a blosc2
# fallback, but reading the .geff GT graphs needs zarr -> install it offline.
INSTALL = r'''
import os, glob, subprocess, sys
def find_wheeldir(slug):
    for base in (f"/kaggle/input/{slug}", f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(base):
            return base
    hits = [p for p in glob.glob(f"/kaggle/input/**/{slug}", recursive=True) if os.path.isdir(p)]
    return hits[0] if hits else None
wd = find_wheeldir("biohub-zarr-wheels")
r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-index",
                    f"--find-links={wd}", "zarr"], capture_output=True, text=True)
print("zarr install rc", r.returncode)
if r.returncode:
    print(r.stderr[-800:])
import zarr; print("zarr", zarr.__version__)
'''
install_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": INSTALL}
base_cells = [install_cell] + base_cells

PROBE = r'''
# ===================== CV RECALL PROBE (train movies, local GT) =====================
import numpy as np, glob, time
from pathlib import Path
from scipy.optimize import linear_sum_assignment

TRAIN_DIR = Path(ROOT) / "train"
assert TRAIN_DIR.exists(), ("no train dir under " + str(ROOT) + " ; /kaggle/input: " + str(glob.glob('/kaggle/input/*')))

def read_geff_min(path):
    import zarr
    g = zarr.open_group(str(path), mode="r")
    t = np.asarray(g["nodes/props/t/values"][:]).astype(np.int64)
    z = np.asarray(g["nodes/props/z/values"][:]).astype(np.float64)
    y = np.asarray(g["nodes/props/y/values"][:]).astype(np.float64)
    x = np.asarray(g["nodes/props/x/values"][:]).astype(np.float64)
    n_est = float("nan")
    try:
        extra = dict(g.attrs).get("geff", {}).get("extra", {}) or {}
        if extra.get("estimated_number_of_nodes") is not None:
            n_est = float(extra["estimated_number_of_nodes"])
    except Exception:
        pass
    return t, np.stack([z, y, x], 1), n_est

def frame_recall(det_t, det_pos, gt_t, gt_pos, maxd=7.0):
    sc = SCALE; matched = 0
    for tt in np.unique(gt_t):
        gi = np.nonzero(gt_t == tt)[0]
        pi = np.nonzero(det_t == tt)[0]
        if len(gi) == 0 or len(pi) == 0:
            continue
        d = np.linalg.norm((det_pos[pi][:, None] * sc) - (gt_pos[gi][None] * sc), axis=2)
        cost = np.where(d <= maxd, d, 1e6)
        ri, ci = linear_sum_assignment(cost)
        for a, b in zip(ri, ci):
            if cost[a, b] < 5e5:
                matched += 1
    return matched

def branch_heatmaps(vol):
    hs = []
    for models, ws, pp in _BRANCHES:
        x = pool_norm(vol, pp); acc = None
        for i in _FLIP_VIEWS:
            xv = np.ascontiguousarray(_flip(x, i))
            with torch.no_grad():
                lg = None
                for m, w in zip(models, ws):
                    l = m(torch.from_numpy(xv)[None, None].to(DEVICE))[0, 0].float().cpu().numpy()
                    lg = w * l if lg is None else lg + w * l
            lg = _flip(lg, i)
            acc = lg if acc is None else acc + lg
        hs.append(1.0 / (1.0 + np.exp(-(acc / len(_FLIP_VIEWS)))))
    return hs

def peaks_from_h(h, vol, thr):
    pk = peak_local_max(h, min_distance=1, threshold_abs=thr, exclude_border=False)
    if len(pk) == 0:
        return np.zeros((0, 3)), np.zeros(0)
    sc = h[pk[:, 0], pk[:, 1], pk[:, 2]].astype(float)
    coords = pk.astype(float)
    coords[:, 1] = coords[:, 1] * POOL + (POOL - 1) / 2
    coords[:, 2] = coords[:, 2] * POOL + (POOL - 1) / 2
    ref = np.array([_refine(vol, c)[0] for c in coords])
    return ref, sc

# ---- select movies: top-annotation-count per embryo, both embryos ----
N_PER_EMBRYO = 6
FRAME_STRIDE = 2          # subsample frames for speed; recall is stable under stride
TIME_BUDGET_S = 3600      # hard stop well under the 12h cap
geffs = sorted(TRAIN_DIR.glob("*.geff"))
by_emb = {}
for gp in geffs:
    zp = gp.with_suffix(".zarr")
    if not zp.exists():
        continue
    emb = gp.name.split("_")[0]
    try:
        t, pos, n_est = read_geff_min(gp)
    except Exception:
        continue
    by_emb.setdefault(emb, []).append((len(t), gp, zp, n_est))
sel = []
for emb, lst in sorted(by_emb.items()):
    lst.sort(reverse=True)
    sel += [(emb,) + x[1:] for x in lst[:N_PER_EMBRYO]]
print("embryos:", {k: len(v) for k, v in by_emb.items()}, "| selected", len(sel), "movies")

STRATS = ["avg015", "avg010", "avg008", "union015", "union012", "A015", "B015", "C015"]
agg = {emb: {s: [0, 0] for s in STRATS} for emb in by_emb}   # strat -> [matched, ngt]
det_count = {emb: {s: [0, 0] for s in STRATS} for emb in by_emb}  # [sum_dets, n_frames]
nest_acc = {emb: [0.0, 0] for emb in by_emb}
t_start = time.time()

def collect(strat_coords_by_t):
    """strat_coords_by_t: dict t->(Nx3). Returns (det_t, det_pos)."""
    ts = []; ps = []
    for tt, c in strat_coords_by_t.items():
        if len(c):
            ts.append(np.full(len(c), tt)); ps.append(c)
    if not ps:
        return np.zeros(0, int), np.zeros((0, 3))
    return np.concatenate(ts), np.concatenate(ps)

for emb, gp, zp, n_est in sel:
    if time.time() - t_start > TIME_BUDGET_S:
        print("TIME BUDGET hit, stopping movie loop"); break
    t_gt, pos_gt, n_est = read_geff_min(gp)
    meta = read_array_meta(zp)
    T = meta["shape"][0]
    present = [t for t in range(T) if (Path(zp) / "0" / "c" / str(t) / "0" / "0" / "0").exists()]
    Tmax = (max(present) + 1) if present else 0
    frames = [t for t in range(0, Tmax, FRAME_STRIDE)]
    # only score frames we actually process
    gt_mask = np.isin(t_gt, frames)
    tg = t_gt[gt_mask]; pg = pos_gt[gt_mask]
    if len(tg) == 0:
        continue
    perstrat = {s: {} for s in STRATS}
    t0 = time.time()
    for t in frames:
        vol = load_volume(zp, t, meta)
        hs = branch_heatmaps(vol)
        hmean = np.mean(hs, axis=0)
        # averaged strategies
        for thr, name in [(0.15, "avg015"), (0.10, "avg010"), (0.08, "avg008")]:
            c, s = peaks_from_h(hmean, vol, thr)
            if len(c):
                c, s = _physical_nms(c, s, NMS_UM)
            perstrat[name][t] = c
        # per-branch peaks @0.15 and @0.12
        pb15 = []; pb12 = []
        for bi, h in enumerate(hs):
            c15, s15 = peaks_from_h(h, vol, 0.15)
            if len(c15):
                c15n, s15n = _physical_nms(c15, s15, NMS_UM)
            else:
                c15n, s15n = c15, s15
            perstrat[["A015", "B015", "C015"][bi]][t] = c15n
            pb15.append((c15, s15))
            c12, s12 = peaks_from_h(h, vol, 0.12)
            pb12.append((c12, s12))
        # union @0.15 and @0.12 (concat all branches, then ONE physical NMS)
        for pb, name in [(pb15, "union015"), (pb12, "union012")]:
            cc = [c for c, s in pb if len(c)]; ss = [s for c, s in pb if len(s)]
            if cc:
                C = np.concatenate(cc); S = np.concatenate(ss)
                C, S = _physical_nms(C, S, NMS_UM)
            else:
                C = np.zeros((0, 3))
            perstrat[name][t] = C
        gc.collect()
    # score recall + det counts for this movie
    for s in STRATS:
        det_t, det_pos = collect(perstrat[s])
        m = frame_recall(det_t, det_pos, tg, pg)
        agg[emb][s][0] += m; agg[emb][s][1] += len(tg)
        det_count[emb][s][0] += len(det_pos); det_count[emb][s][1] += len(frames)
    nest_acc[emb][0] += n_est / max(1, Tmax) * len(frames); nest_acc[emb][1] += len(frames)
    r_avg = agg[emb]["avg015"][0] / max(1, agg[emb]["avg015"][1])
    r_uni = agg[emb]["union015"][0] / max(1, agg[emb]["union015"][1])
    print("  " + emb + " " + gp.stem + " ngt=" + str(len(tg)) +
          " avg015=%.3f union015=%.3f" % (r_avg, r_uni) + " (%.0fs)" % (time.time() - t0))

print("\n================ RECALL BY EMBRYO (matched / annotated) ================")
hdr = "embryo    " + "".join("%9s" % s for s in STRATS)
print(hdr)
for emb in sorted(agg):
    row = "%-9s" % emb
    for s in STRATS:
        m, n = agg[emb][s]
        row += "   %.4f" % (m / n if n else float("nan"))
    print(row)

print("\n================ POOLED RECALL (both embryos) ================")
pooled = {s: [0, 0] for s in STRATS}
for emb in agg:
    for s in STRATS:
        pooled[s][0] += agg[emb][s][0]; pooled[s][1] += agg[emb][s][1]
for s in STRATS:
    m, n = pooled[s]
    print("  %-9s recall=%.4f   (implied edge_J ~= %.4f)" % (s, m / n, (m / n) ** 2))

print("\n================ DETECTIONS / FRAME  vs  est_nodes/frame ================")
for emb in sorted(det_count):
    npf = nest_acc[emb][0] / max(1, nest_acc[emb][1])
    print("  " + emb + "  est_nodes/frame ~= %.0f" % npf)
    for s in STRATS:
        d, f = det_count[emb][s]
        dpf = d / f if f else 0
        ratio = (dpf - npf) / npf if npf else float("nan")
        print("     %-9s %.0f det/frame  node_ratio~=%+.2f  penalty~=%.3f" % (s, dpf, ratio, max(0.0, 1 - 0.1 * ratio)))

print("\n================ MISS-CORRELATION (is the union additive?) ================")
def rec(s):
    m, n = pooled[s]; return m / n if n else 0.0
rA, rB, rC = rec("A015"), rec("B015"), rec("C015")
r_union = rec("union015")
indep = 1 - (1 - rA) * (1 - rB) * (1 - rC)
best = max(rA, rB, rC)
print("  per-model recall: A=%.4f B=%.4f C=%.4f" % (rA, rB, rC))
print("  union recall observed = %.4f" % r_union)
print("  if misses INDEPENDENT  -> %.4f  (union near this => uncorrelated, big win)" % indep)
print("  if misses IDENTICAL     -> %.4f  (union near this => correlated, no win)" % best)
if indep > best + 1e-6:
    frac = (r_union - best) / (indep - best)
    print("  observed union sits %.0f%% of the way from correlated->independent" % (100 * frac))
print("\nDECISION: promote union to a submission only if union@thr recall clears")
print("avg015 recall by a real margin AND det/frame stays near est_nodes/frame.")
'''

probe_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": PROBE}
nb = dict(src)
nb["cells"] = base_cells + [probe_cell]

nb_path = OUT_DIR / "biohub-union-cv-probe.ipynb"
nb_path.write_text(json.dumps(nb), encoding="utf-8")

meta = {
    "id": "eeshsaxena/biohub-union-cv-recall-probe",
    "title": "Biohub union cv recall probe",
    "code_file": "biohub-union-cv-probe.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_gpu": True,
    "enable_tpu": False,
    "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4",
    "keywords": ["gpu", "cell-tracking"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models", "eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [],
    "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path)
print("cells:", len(nb["cells"]))
