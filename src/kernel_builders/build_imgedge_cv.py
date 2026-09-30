"""Build an IMAGE-SIGNAL feasibility CV kernel (no submission cost).

THE ONE remaining open question after two exhaustive lever rounds:
  Local geometric link decisions are at ceiling (the 22-feature geometric ranker
  hit OOF AUC 0.98 but +0.0002 score; on 1-positive groups the geometric COST
  already top-1s 92.85%). The gap is the 2.0% "steal" edges: right detection,
  WRONG link, landing ~8.76um away on a NEIGHBOUR. Geometry cannot break those
  ties. The only untested signal is the IMAGE ITSELF: does the appearance of the
  source cell @t look more like its TRUE next-frame cell than like the wrong
  neighbour? If yes, an image-based edge model has real headroom (justifies the
  off-Kaggle training build). If no, the edge-model ceiling is proven and 0.921
  is the accessible wall.

WHAT THIS DOES (train movies, local .geff GT, FREE GPU):
  1. detect every frame with the exact 0.917 Kunal stack (reused cells 0-3),
  2. per consecutive frame pair, find AMBIGUOUS sources: a source i@t whose two
     nearest targets j0,j1 @t+1 are within MARGIN_UM of each other (the tie the
     geometric linker can miss = where steals happen),
  3. GT-match nodes (7um Hungarian) to know each source's TRUE successor,
  4. keep only ambiguous cases where the true target is one of {j0,j1},
  5. compare three pickers on that hard set:
       COST   = nearest target j0 (what the geometric linker picks),
       IMG    = higher normalized cross-correlation of the 3D image patch
                (source@t vs each candidate@t+1),
       FUSE   = distance discounted by image NCC (cost - LAMBDA*ncc),
  6. report, per embryo + pooled, each picker's accuracy on the ambiguous set.

DECISION: IMG (or FUSE) must beat COST by a real margin on BOTH embryos for an
image edge-model to be worth building. Expected null: homogeneous nuclei -> patch
appearance does not separate neighbours -> IMG ~= COST -> ceiling confirmed.
Running this costs GPU time, NOT a submission slot.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
OUT_DIR = HERE / "imgedge_cv"
OUT_DIR.mkdir(exist_ok=True)
src = json.loads(SRC_NB.read_text(encoding="utf-8"))
base_cells = [src["cells"][i] for i in (0, 1, 2, 3)]  # setup + helpers + linker + detect

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
import zarr; print("zarr", zarr.__version__)
'''
install_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": INSTALL}
base_cells = [install_cell] + base_cells

CV = r'''
# ===================== IMAGE-SIGNAL FEASIBILITY CV =====================
import numpy as np, time, os, gc
from pathlib import Path
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

TRAIN_DIR = Path(ROOT) / "train"
assert TRAIN_DIR.exists(), "no train dir under " + str(ROOT)
UNET_THR = 0.15

def read_geff_min(path):
    import zarr
    g = zarr.open_group(str(path), mode="r")
    ids = np.asarray(g["nodes/ids"][:]).astype(np.int64)
    t = np.asarray(g["nodes/props/t/values"][:]).astype(np.int64)
    z = np.asarray(g["nodes/props/z/values"][:]).astype(np.float64)
    y = np.asarray(g["nodes/props/y/values"][:]).astype(np.float64)
    x = np.asarray(g["nodes/props/x/values"][:]).astype(np.float64)
    try:
        e = np.asarray(g["edges/ids"][:]).astype(np.int64).reshape(-1, 2)
    except KeyError:
        e = np.zeros((0, 2), np.int64)
    return {"ids": ids, "t": t, "pos": np.stack([z, y, x], 1), "edges": e}

def match_frame(pt_pos, gt_pos, maxd=7.0):
    """Hungarian match pred coords -> gt indices within this frame. Returns pred_i -> gt_i (or -1)."""
    out = np.full(len(pt_pos), -1, np.int64)
    if len(pt_pos) == 0 or len(gt_pos) == 0:
        return out
    d = np.linalg.norm((pt_pos[:, None] * SCALE) - (gt_pos[None] * SCALE), axis=2)
    cost = np.where(d <= maxd, d, 1e6)
    ri, ci = linear_sum_assignment(cost)
    for a, b in zip(ri, ci):
        if cost[a, b] < 5e5:
            out[a] = b
    return out

def patch(vol, p, rz=2, ry=7, rx=7):
    z, y, x = int(round(p[0])), int(round(p[1])), int(round(p[2]))
    Z, Y, X = vol.shape
    return vol[max(0, z-rz):min(Z, z+rz+1), max(0, y-ry):min(Y, y+ry+1), max(0, x-rx):min(X, x+rx+1)].astype(np.float32)

def ncc(a, b):
    zz = min(a.shape[0], b.shape[0]); yy = min(a.shape[1], b.shape[1]); xx = min(a.shape[2], b.shape[2])
    if zz == 0 or yy == 0 or xx == 0:
        return 0.0
    a = a[:zz, :yy, :xx].ravel().astype(np.float32); b = b[:zz, :yy, :xx].ravel().astype(np.float32)
    a = a - a.mean(); b = b - b.mean()
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na < 1e-6 or nb < 1e-6:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

MAX_LINK_UM = 8.0
MARGIN_UM = 2.0          # ambiguous when |d(i,j1)-d(i,j0)| < this
LAMBDA = 3.0             # FUSE: cost_um - LAMBDA*ncc
N_PER_EMBRYO = 4
MAXT = 60                # cap frames/movie for runtime
TIME_BUDGET_S = 3 * 3600

geffs = sorted(TRAIN_DIR.glob("*.geff"))
by_emb = {}
for gp in geffs:
    zp = gp.with_suffix(".zarr")
    if not zp.exists():
        continue
    by_emb.setdefault(gp.name.split("_")[0], []).append(gp)
sel = []
for emb, lst in sorted(by_emb.items()):
    sel += [(emb, gp) for gp in lst[:N_PER_EMBRYO]]
print("selected", len(sel), "movies:", {k: min(len(v), N_PER_EMBRYO) for k, v in by_emb.items()})

# accumulators per embryo: [n_ambiguous, cost_true, img_true, fuse_true]
acc = {emb: [0, 0, 0, 0] for emb in by_emb}
t_start = time.time()

for emb, gp in sel:
    if time.time() - t_start > TIME_BUDGET_S:
        print("TIME BUDGET hit"); break
    gt = read_geff_min(gp)
    zp = gp.with_suffix(".zarr")
    meta = read_array_meta(zp)
    T = meta["shape"][0]
    present = [t for t in range(T) if (Path(zp) / "0" / "c" / str(t) / "0" / "0" / "0").exists()]
    Tmax = min(MAXT, (max(present) + 1) if present else 0)
    # gt per-frame node lists + successor map (consecutive edges only)
    gt_by_t = {}
    gid_index = {int(v): i for i, v in enumerate(gt["ids"])}
    for i, (tt, pp) in enumerate(zip(gt["t"], gt["pos"])):
        gt_by_t.setdefault(int(tt), []).append(i)
    succ = {}
    for s, d in gt["edges"]:
        si, di = gid_index.get(int(s)), gid_index.get(int(d))
        if si is None or di is None:
            continue
        if int(gt["t"][di]) - int(gt["t"][si]) == 1:
            succ.setdefault(si, []).append(di)
    t0 = time.time()
    prev = None  # (vol, coords, match_arr, t)
    namb = 0
    for t in range(Tmax):
        vol = load_volume(zp, t, meta)
        coords, scores = detect(vol)
        coords = np.asarray(coords, float).reshape(-1, 3)
        # match this frame's detections to GT nodes present at t
        gidx = gt_by_t.get(t, [])
        gpos = gt["pos"][gidx] if gidx else np.zeros((0, 3))
        m_local = match_frame(coords, gpos, 7.0)                 # pred_i -> local gt list index
        m_glob = np.array([gidx[k] if k >= 0 else -1 for k in m_local], np.int64) if len(gidx) else np.full(len(coords), -1, np.int64)
        cur = (vol, coords, m_glob, t)
        if prev is not None and prev[3] == t - 1:
            vP, cP, mP, _ = prev
            P = cP * SCALE; C = coords * SCALE
            if len(cP) and len(coords):
                tree = cKDTree(C)
                kk = min(3, len(coords))
                dists, idxs = tree.query(P, k=kk)
                dists = np.atleast_2d(dists.reshape(len(cP), kk)); idxs = np.atleast_2d(idxs.reshape(len(cP), kk))
                for i in range(len(cP)):
                    d = dists[i]; jd = idxs[i]
                    if kk < 2 or d[1] > MAX_LINK_UM:
                        continue
                    if (d[1] - d[0]) > MARGIN_UM:
                        continue                                  # not an ambiguous tie
                    j0, j1 = int(jd[0]), int(jd[1])
                    gi = mP[i]
                    if gi < 0 or gi not in succ:
                        continue
                    true_succ = set(succ[gi])
                    m0 = m_glob[j0]; m1 = m_glob[j1]
                    is0 = m0 in true_succ; is1 = m1 in true_succ
                    if not (is0 or is1):
                        continue                                  # true target not among the tie -> skip
                    truej = j0 if is0 else j1
                    namb += 1; acc[emb][0] += 1
                    # COST picker = nearest (j0)
                    if j0 == truej:
                        acc[emb][1] += 1
                    # IMG picker = higher NCC(source@t-1 patch, candidate@t patch)
                    ps = patch(vP, cP[i])
                    n0 = ncc(ps, patch(vol, coords[j0])); n1 = ncc(ps, patch(vol, coords[j1]))
                    img_pick = j0 if n0 >= n1 else j1
                    if img_pick == truej:
                        acc[emb][2] += 1
                    # FUSE picker = min(cost - LAMBDA*ncc)
                    f0 = d[0] - LAMBDA * n0; f1 = d[1] - LAMBDA * n1
                    fuse_pick = j0 if f0 <= f1 else j1
                    if fuse_pick == truej:
                        acc[emb][3] += 1
            del vP
        prev = cur
        gc.collect()
    print("  %s %s: ambiguous=%d (%.0fs)" % (emb, gp.stem, namb, time.time() - t0))

print("\n================ IMAGE-SIGNAL ON AMBIGUOUS STEAL-TIES ================")
print("  %-6s %10s %8s %8s %8s" % ("embryo", "n_amb", "COST", "IMG", "FUSE"))
pool = [0, 0, 0, 0]
for emb in sorted(acc):
    n, c, im, fu = acc[emb]
    for k in range(4):
        pool[k] += acc[emb][k]
    if n:
        print("  %-6s %10d %8.4f %8.4f %8.4f" % (emb, n, c / n, im / n, fu / n))
    else:
        print("  %-6s %10d   (no ambiguous cases)" % (emb, n))
n, c, im, fu = pool
if n:
    print("  %-6s %10d %8.4f %8.4f %8.4f" % ("POOLED", n, c / n, im / n, fu / n))
    print("\n  IMG gain over COST (pooled)  = %+.4f" % ((im - c) / n))
    print("  FUSE gain over COST (pooled) = %+.4f" % ((fu - c) / n))

print("\n================ VERDICT ================")
both_img = all((acc[e][2] - acc[e][1]) / acc[e][0] > 0.02 for e in acc if acc[e][0])
both_fuse = all((acc[e][3] - acc[e][1]) / acc[e][0] > 0.02 for e in acc if acc[e][0])
print("  IMG  beats COST by >0.02 on BOTH embryos:", both_img)
print("  FUSE beats COST by >0.02 on BOTH embryos:", both_fuse)
print("  => if TRUE, image context has real headroom -> build the off-Kaggle edge model.")
print("  => if FALSE, appearance cannot break steal-ties -> 0.921 is the accessible ceiling.")
'''

cv_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": CV}
nb = dict(src); nb["cells"] = base_cells + [cv_cell]
nb_path = OUT_DIR / "biohub-imgedge-cv.ipynb"
nb_path.write_text(json.dumps(nb), encoding="utf-8")
meta = {
    "id": "eeshsaxena/biohub-imgedge-cv",
    "title": "Biohub imgedge cv",
    "code_file": "biohub-imgedge-cv.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": ["gpu"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models", "eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path, "| cells", len(nb["cells"]))
