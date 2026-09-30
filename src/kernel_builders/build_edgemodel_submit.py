"""Build the EDGE-MODEL SUBMISSION kernel (writes submission.csv over the hidden test).

Trains the learned 3D-CNN image edge model on ALL train movies (both embryos -- the 2
test embryos match neither train embryo, so an all-data model, not the cross-embryo OOF
ones), then runs the full Kunal pipeline on the test with linker=accel_rank folding the
edge probability into the Hungarian cost (full mode, bonus b3.0 -- the v2 CV both-embryo
best, +0.0011 pooled over the accel base). Base = sim4 (LB-0.921 stack) + accel + edge model.

Reuses: Kunal cells 0-4 (detect/load_volume/SCALE/TEST_DIR/COLS/avail_T/read_array_meta),
and the edge-model + candidate/feature/repair machinery from build_edgemodel_v2.py (the CV
cell's definitions, everything before the run-CV driver).

Integrity gate (all test datasets present; every edge advances exactly one frame) mirrors
the Kunal cell-7 contract. Runtime at scoring = train (~40min) + per-sample inference; well
under the 12h cap. Costs a SUBMISSION SLOT only when submitted after COMPLETE.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
V2 = HERE / "build_edgemodel_v2.py"
OUT_DIR = HERE / "sub_edgemodel"
OUT_DIR.mkdir(exist_ok=True)

src = json.loads(SRC_NB.read_text(encoding="utf-8"))
base_cells = [src["cells"][i] for i in (0, 1, 2, 3, 4)]   # definitions (detect, load_volume, COLS, ...)

# ---- extract the edge-model + pipeline DEFINITIONS from build_edgemodel_v2.py ----
v2 = V2.read_text(encoding="utf-8")
cv = v2.split("CV = r'''", 1)[1]
cv = cv.split("\n'''", 1)[0]                               # the whole CV cell body
DEFS = cv.split("# ---------- run CV ----------", 1)[0]    # everything before the driver

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
try:
    import zarr; print("zarr", zarr.__version__)
except Exception as e:
    print("zarr import failed (train GT read will fall back / skip):", str(e)[:120])
'''

TRAIN = r'''
# ===================== TRAIN edge CNN on ALL train movies =====================
import numpy as np, time, gc
from pathlib import Path
TRAIN_DIR = Path(ROOT) / "train"
N_TRAIN_PER_EMB = 6
MAXT = 90
SUBMIT_CFG = dict(unet_thr=0.15, max_dt=1, gate=4.5, snap=3.2, mincand=0.10, cap=0.08, synth=True,
                  div_diverge=2.25, div_sister=15.0, linker="accel", accel_bonus=0.80, accel_max=4.0,
                  short_min=6, max_link=8.0, sim_w=4.0)          # sim4 base + accel

geffs = sorted(TRAIN_DIR.glob("*.geff"))
by_emb = {}
for gp in geffs:
    zp = gp.with_suffix(".zarr")
    if not zp.exists():
        continue
    g = read_geff_min(gp)
    if len(g["edges"]) < 20:
        continue
    by_emb.setdefault(gp.name.split("_")[0], []).append((len(g["ids"]), gp, zp))
sel = []
for emb, lst in sorted(by_emb.items()):
    lst.sort(reverse=True); sel += [(emb,) + x[1:] for x in lst[:N_TRAIN_PER_EMB]]
print("train movies:", {k: min(len(v), N_TRAIN_PER_EMB) for k, v in by_emb.items()}, flush=True)

SPATCH = {}; stems = []; Xl = []; yl = []; Rl = []
t_start = time.time()
for mi, (emb, gp, zp) in enumerate(sel):
    gt = read_geff_min(gp); meta = read_array_meta(zp); T = meta["shape"][0]
    present = [t for t in range(T) if (Path(zp) / "0" / "c" / str(t) / "0" / "0" / "0").exists()]
    Tmax = min(MAXT, (max(present) + 1) if present else 0)
    frames = list(range(Tmax)); fidx = {f: i for i, f in enumerate(frames)}
    keep = np.isin(gt["t"], frames)
    gt_s = {"ids": gt["ids"][keep], "t": np.array([fidx[int(t)] for t in gt["t"][keep]], np.int64),
            "pos": gt["pos"][keep], "edges": [], "n_est": gt["n_est"]}
    idset = set(int(v) for v in gt_s["ids"])
    for s, d in gt["edges"]:
        if int(s) in idset and int(d) in idset:
            gt_s["edges"].append((int(s), int(d)))
    dets = []; spatch = []
    for f in frames:
        vol = load_volume(zp, f, meta); c, s = detect(vol)
        c = np.asarray(c, np.float32).reshape(-1, 3); s = np.asarray(s, np.float32).reshape(-1)
        dets.append((c, s)); spatch.append(extract_patches(vol, c[s >= UNET_THR])); del vol; gc.collect()
    stem = gp.stem; SPATCH[stem] = spatch; stems.append(stem)
    blocks = build_pair_features(dets, SUBMIT_CFG); labs = label_blocks(blocks, dets, SUBMIT_CFG, gt_s)
    for tt, (b, lb) in enumerate(zip(blocks, labs)):
        if b is None or lb is None:
            continue
        k = lb["known"]
        if k.any():
            Xl.append(b["X"][k]); yl.append(lb["y"][k])
            ik = b["ii"][k].astype(np.int32); jk = b["jj"][k].astype(np.int32)
            Rl.append(np.stack([np.full(len(ik), mi, np.int32), np.full(len(ik), tt, np.int32), ik, jk], 1))
    print("  trained-data %s %s (%.0fs)" % (emb, stem, time.time() - t_start), flush=True)

X_all = np.concatenate(Xl).astype(np.float32); y_all = np.concatenate(yl).astype(np.int8); R_all = np.concatenate(Rl)
gmean = X_all.mean(0); gstd = X_all.std(0) + 1e-6; Xn_all = (X_all - gmean) / gstd
print("EDGE-MODEL train rows=%d pos=%.1f%%; fitting CNN on ALL data..." % (len(y_all), 100 * y_all.mean()), flush=True)
MODEL_ALL = train_cnn(R_all, Xn_all, y_all, epochs=16)
print("edge model READY (all-data)", flush=True)
'''

SUBMIT = r'''
# ===================== RUN ON TEST -> submission.csv =====================
import pandas as pd, torch

def _infer_block(b, sp, tt):
    src = sp[tt][b["ii"]]; tgt = sp[tt + 1][b["jj"]]
    P = np.stack([src, tgt], 1).astype(np.float32); Xn = (b["X"] - gmean) / gstd
    out = np.zeros(len(b["ii"]), np.float32); MODEL_ALL.eval()
    with torch.no_grad():
        for s0 in range(0, len(b["ii"]), 1024):
            pb = torch.tensor(P[s0:s0 + 1024], dtype=torch.float32).to(DEV)
            xb = torch.tensor(Xn[s0:s0 + 1024], dtype=torch.float32).to(DEV)
            out[s0:s0 + 1024] = torch.sigmoid(MODEL_ALL(pb, xb)).cpu().numpy()
    return out

CFG_EDGE = dict(SUBMIT_CFG, linker="accel_rank", rank_mode="full", learned_bonus=3.0)   # v2 best

def track_movie_edge(zp, ds, T):
    meta = read_array_meta(zp); dets = []; sp = []
    for t in range(T):
        vol = load_volume(zp, t, meta); c, s = detect(vol)
        c = np.asarray(c, np.float32).reshape(-1, 3); s = np.asarray(s, np.float32).reshape(-1)
        dets.append((c, s)); sp.append(extract_patches(vol, c[s >= UNET_THR])); del vol; gc.collect()
    blocks = build_pair_features(dets, SUBMIT_CFG)
    PR = []
    for tt, b in enumerate(blocks):
        if b is None:
            PR.append(None); continue
        p = _infer_block(b, sp, tt)
        M = np.zeros((b["np"], b["nc"]), np.float32); M[b["ii"], b["jj"]] = p; PR.append(M)
    (pt, pp, pe), ngap, ndiv = repair_cfg(dets, CFG_EDGE, PR)
    node_rows = [(ds, "node", i + 1, int(pt[i]), float(pp[i, 0]), float(pp[i, 1]), float(pp[i, 2]), -1, -1)
                 for i in range(len(pt))]
    edge_rows = [(ds, "edge", -1, -1, -1, -1, -1, int(a) + 1, int(b) + 1) for a, b in pe]
    return pd.DataFrame(node_rows, columns=COLS), pd.DataFrame(edge_rows, columns=COLS)

OUT = "submission.csv"
parts = []
for zp in sorted(TEST_DIR.glob("*.zarr")):
    ds = zp.name.replace(".zarr", ""); T = avail_T(zp)
    if T == 0:
        print("skip", ds); continue
    t0 = time.time(); nodes, edges = track_movie_edge(zp, ds, T); parts += [nodes, edges]
    print("  %s: T=%d nodes=%d edges=%d (%.1fs)" % (ds, T, len(nodes), len(edges), time.time() - t0), flush=True)
sub = pd.concat(parts, ignore_index=True); sub.index.name = "id"; sub.to_csv(OUT)
exp = ["dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
assert list(sub.columns) == exp, list(sub.columns)
print("wrote", OUT, "rows", len(sub), "nodes", int((sub.row_type == 'node').sum()), "edges", int((sub.row_type == 'edge').sum()))

# ---- integrity gate (Kunal cell-7 contract) ----
expected = {p.name.replace('.zarr', '') for p in TEST_DIR.glob('*.zarr')}
written = set(sub.loc[sub.row_type == 'node', 'dataset'].unique())
assert not (expected - written), ("missing datasets", sorted(expected - written))
node_t = {(r.dataset, r.node_id): r.t for r in sub.loc[sub.row_type == 'node'].itertuples()}
for e in sub.loc[sub.row_type == 'edge'].itertuples():
    assert (e.dataset, e.source_id) in node_t and (e.dataset, e.target_id) in node_t, (e.dataset, e.source_id, e.target_id)
    assert node_t[(e.dataset, e.target_id)] == node_t[(e.dataset, e.source_id)] + 1, (e.dataset, e.source_id, e.target_id)
print("submission integrity PASS:", len(expected), "datasets")
'''

def _cell(sourcestr):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": sourcestr}

nb = dict(src)
nb["cells"] = [_cell(INSTALL)] + base_cells + [_cell(DEFS), _cell(TRAIN), _cell(SUBMIT)]
nb_path = OUT_DIR / "biohub-edgemodel-submit.ipynb"
nb_path.write_text(json.dumps(nb), encoding="utf-8")
meta = {
    "id": "eeshsaxena/biohub-edgemodel-submit",
    "title": "Biohub edgemodel submit",
    "code_file": "biohub-edgemodel-submit.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": ["gpu"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models", "eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path, "| cells", len(nb["cells"]))
