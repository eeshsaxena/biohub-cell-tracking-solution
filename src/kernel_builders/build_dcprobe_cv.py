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
OUT_DIR = HERE / "dcprobe_cv"
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
import numpy as np, glob, time, os
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

# ---------- DeepCenter 4th detection branch (same pooled Z,Y/4,X/4 grid) ----------
# Ported verbatim from _intel/bt_v6 (_DCDeepCenterUNet3D + deepcenter_heatmap_for_frame).
# It is currently used in public stacks ONLY as a gap-veto gate, never in the
# detection average. This probe measures whether adding it to the heatmap MEAN
# raises node recall on BOTH train embryos (gate: >0.005 both, else CV-noise / skip).
import torch as _t
class _DCConv(_t.nn.Module):
    def __init__(s, ci, co):
        super().__init__(); g = min(8, co)
        s.block = _t.nn.Sequential(   # MUST be named 'block' to match bt_v6 _DCConvBlock3d checkpoint keys
            _t.nn.Conv3d(ci, co, 3, padding=1, bias=False), _t.nn.GroupNorm(g, co), _t.nn.SiLU(True),
            _t.nn.Conv3d(co, co, 3, padding=1, bias=False), _t.nn.GroupNorm(g, co), _t.nn.SiLU(True))
    def forward(s, x): return s.block(x)
class _DCUNet(_t.nn.Module):
    def __init__(s, base=24):
        super().__init__(); c = int(base)
        s.enc1 = _DCConv(1, c); s.down1 = _t.nn.MaxPool3d(2, 2)
        s.enc2 = _DCConv(c, c * 2); s.down2 = _t.nn.MaxPool3d(2, 2)
        s.enc3 = _DCConv(c * 2, c * 4); s.down3 = _t.nn.MaxPool3d(2, 2)
        s.bottleneck = _DCConv(c * 4, c * 8)
        s.up3 = _t.nn.ConvTranspose3d(c * 8, c * 4, 2, 2); s.dec3 = _DCConv(c * 8, c * 4)
        s.up2 = _t.nn.ConvTranspose3d(c * 4, c * 2, 2, 2); s.dec2 = _DCConv(c * 4, c * 2)
        s.up1 = _t.nn.ConvTranspose3d(c * 2, c, 2, 2); s.dec1 = _DCConv(c * 2, c)
        s.head = _t.nn.Conv3d(c, 1, 1)
    def forward(s, x):
        e1 = s.enc1(x); e2 = s.enc2(s.down1(e1)); e3 = s.enc3(s.down2(e2)); b = s.bottleneck(s.down3(e3))
        d3 = s.dec3(_t.cat([s.up3(b), e3], 1)); d2 = s.dec2(_t.cat([s.up2(d3), e2], 1)); d1 = s.dec1(_t.cat([s.up1(d2), e1], 1))
        return s.head(d1)
def _dc_find_ckpts():
    # yunus/bt_v6 load DeepCenter from best.pt -> prefer it; try all found candidates.
    import glob as _g
    out = []
    roots = ("/kaggle/input/biohub-deepcenter-unet3d-center-prior-v1",
             "/kaggle/input/datasets/pilkwang/biohub-deepcenter-unet3d-center-prior-v1")
    for root in roots:
        for name in ("best.pt", "checkpoint_last.pt", "last.pt"):
            p = root + "/weights/full_frame_center/" + name
            if os.path.exists(p):
                out.append(p)
    for name in ("best.pt", "checkpoint_last.pt", "last.pt"):
        out += sorted(_g.glob("/kaggle/input/**/full_frame_center/**/" + name, recursive=True))
    seen = set(); uniq = []
    for p in out:
        if p not in seen:
            seen.add(p); uniq.append(p)
    return uniq
def _dc_state(cp):
    st = cp.get("model_state") or cp.get("state_dict") or cp.get("model") or cp
    if not isinstance(st, dict):
        return None
    # strip common prefixes
    out = {}
    for k, v in st.items():
        kk = k
        for pre in ("module.", "model.", "net."):
            if kk.startswith(pre):
                kk = kk[len(pre):]
        out[kk] = v
    return out
def _dc_infer_base(st):
    for k in ("enc1.block.0.weight", "enc1.b.0.weight"):
        if k in st:
            return int(st[k].shape[0])
    # any first conv in enc1
    for k, v in st.items():
        if "enc1" in k and hasattr(v, "shape") and len(v.shape) == 5 and v.shape[1] == 1:
            return int(v.shape[0])
    return 24
_DC = None; _DCPF = 4; _DCNL = 50.0; _DCNH = 99.5; _DCCL = -0.5; _DCCH = 6.0
for _ck in _dc_find_ckpts():
    try:
        print("DeepCenter try:", _ck)
        _cp = _t.load(_ck, map_location=DEVICE, weights_only=False)
        _cfg = _cp.get("config", {}) if isinstance(_cp, dict) else {}
        _cfg = _cfg or {}
        _st = _dc_state(_cp)
        if _st is None:
            print("  no state dict in checkpoint"); continue
        _base = int(_cfg.get("base_channels") or _dc_infer_base(_st))
        _m = _DCUNet(base=_base)
        _miss, _unexp = _m.load_state_dict(_st, strict=False)
        if len(_miss) == 0 and len(_unexp) == 0:
            _m.to(DEVICE); _m.eval(); _DC = _m
            _DCPF = int(_cfg.get("pool_factor", 4)); _DCNL = float(_cfg.get("norm_lo_pct", 50.0)); _DCNH = float(_cfg.get("norm_hi_pct", 99.5))
            _DCCL = float(_cfg.get("norm_clip_lo", -0.5)); _DCCH = float(_cfg.get("norm_clip_hi", 6.0))
            print("  DeepCenter LOADED base=%d pool_factor=%d epoch=%s" % (_base, _DCPF, str(_cp.get("epoch") if isinstance(_cp, dict) else "?")))
            if _DCPF != POOL:
                print("  POOL MISMATCH DeepCenter", _DCPF, "vs Kunal", POOL, "-> disabling"); _DC = None; continue
            break
        else:
            print("  arch mismatch base=%d: missing=%d unexpected=%d" % (_base, len(_miss), len(_unexp)))
    except Exception as _e:
        print("  load error:", type(_e).__name__, _e)
if _DC is None:
    print("DeepCenter DISABLED (no compatible checkpoint) -> dc strategies will be empty; avg015 still valid")
def _dc_poolxy(vol, f):
    if f <= 1: return vol.astype(np.float32)
    z, y, x = vol.shape; y2 = (y // f) * f; x2 = (x // f) * f
    return vol[:, :y2, :x2].astype(np.float32).reshape(z, y2 // f, f, x2 // f, f).mean(axis=(2, 4))
def dc_heatmap(vol):
    if _DC is None: return None
    pooled = _dc_poolxy(vol, _DCPF)
    lo = float(np.percentile(pooled, _DCNL)); hi = float(np.percentile(pooled, _DCNH))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        img = np.zeros_like(pooled, np.float32)
    else:
        img = np.clip((pooled - lo) / (hi - lo), _DCCL, _DCCH).astype(np.float32)
    with _t.no_grad():
        ten = _t.from_numpy(img[None, None]).to(DEVICE, dtype=_t.float32)
        h = _t.sigmoid(_DC(ten))[0, 0].float().cpu().numpy().astype(np.float32)
    return h

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

STRATS = ["avg015", "dc02", "dc03", "dc05", "D015"]
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
        h_dc = dc_heatmap(vol)
        # grid-align DeepCenter map with the Kunal branch maps (defensive; usually equal)
        if h_dc is not None and h_dc.shape != hs[0].shape:
            zz = min(h_dc.shape[0], hs[0].shape[0]); yy = min(h_dc.shape[1], hs[0].shape[1]); xx = min(h_dc.shape[2], hs[0].shape[2])
            h_dc = h_dc[:zz, :yy, :xx]; hs = [h[:zz, :yy, :xx] for h in hs]
        hmean = np.mean(hs, axis=0)                       # baseline = current 3-branch mean (avg015)
        c, s = peaks_from_h(hmean, vol, 0.15)
        if len(c):
            c, s = _physical_nms(c, s, NMS_UM)
        perstrat["avg015"][t] = c
        if h_dc is not None:
            hsum = hs[0] + hs[1] + hs[2]
            for w, name in [(0.2, "dc02"), (0.3, "dc03"), (0.5, "dc05")]:
                hw = (hsum + w * h_dc) / (3.0 + w)
                cw, sw = peaks_from_h(hw, vol, 0.15)
                if len(cw):
                    cw, sw = _physical_nms(cw, sw, NMS_UM)
                perstrat[name][t] = cw
            cD, sD = peaks_from_h(h_dc, vol, 0.15)
            if len(cD):
                cD, sD = _physical_nms(cD, sD, NMS_UM)
            perstrat["D015"][t] = cD
        gc.collect()
    # score recall + det counts for this movie
    for s in STRATS:
        det_t, det_pos = collect(perstrat[s])
        m = frame_recall(det_t, det_pos, tg, pg)
        agg[emb][s][0] += m; agg[emb][s][1] += len(tg)
        det_count[emb][s][0] += len(det_pos); det_count[emb][s][1] += len(frames)
    nest_acc[emb][0] += n_est / max(1, Tmax) * len(frames); nest_acc[emb][1] += len(frames)
    r_avg = agg[emb]["avg015"][0] / max(1, agg[emb]["avg015"][1])
    r_dc3 = agg[emb]["dc03"][0] / max(1, agg[emb]["dc03"][1])
    print("  " + emb + " " + gp.stem + " ngt=" + str(len(tg)) +
          " avg015=%.3f dc03=%.3f" % (r_avg, r_dc3) + " (%.0fs)" % (time.time() - t0))

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

print("\n================ DeepCenter-into-mean: GATE ANALYSIS ================")
def rec(s):
    m, n = pooled[s]; return m / n if n else 0.0
r_avg = rec("avg015"); r_D = rec("D015")
r_dc = {w: rec(w) for w in ("dc02", "dc03", "dc05")}
best_dc = max(r_dc, key=lambda k: r_dc[k])
print("  Kunal-avg recall = %.4f | DeepCenter-alone = %.4f" % (r_avg, r_D))
for w in ("dc02", "dc03", "dc05"):
    print("  %s recall = %.4f  (gain vs avg %+.4f)" % (w, r_dc[w], r_dc[w] - r_avg))
print("  BEST dc-weighted = %s @ %.4f (pooled gain %+.4f)" % (best_dc, r_dc[best_dc], r_dc[best_dc] - r_avg))
print("\n  PER-EMBRYO gate (must be > +0.005 on BOTH to promote):")
_both = True
for emb in sorted(agg):
    ra = agg[emb]["avg015"][0] / max(1, agg[emb]["avg015"][1])
    rb = agg[emb][best_dc][0] / max(1, agg[emb][best_dc][1])
    ok = (rb - ra) > 0.005
    _both = _both and ok
    print("    %-6s avg=%.4f %s=%.4f  gain=%+.4f  %s" % (emb, ra, best_dc, rb, rb - ra, "PASS" if ok else "fail"))
print("\n  GATE %s: DeepCenter-in-mean %s both-embryo >0.005 recall." % ("PASS" if _both else "FAIL", "clears" if _both else "does NOT clear"))
print("  (CV can invert sub-0.005 edge deltas; only a LARGE both-embryo gain is a real submit signal.)")
'''

probe_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": PROBE}
nb = dict(src)
nb["cells"] = base_cells + [probe_cell]

nb_path = OUT_DIR / "biohub-dcprobe-cv.ipynb"
nb_path.write_text(json.dumps(nb), encoding="utf-8")

meta = {
    "id": "eeshsaxena/biohub-dcprobe-cv",
    "title": "Biohub dcprobe cv",
    "code_file": "biohub-dcprobe-cv.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_gpu": True,
    "enable_tpu": False,
    "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4",
    "keywords": ["gpu", "cell-tracking"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models", "eeshsaxena/biohub-zarr-wheels", "pilkwang/biohub-deepcenter-unet3d-center-prior-v1"],
    "kernel_sources": [],
    "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path)
print("cells:", len(nb["cells"]))
