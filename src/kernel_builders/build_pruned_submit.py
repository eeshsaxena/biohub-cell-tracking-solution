"""Build the PRUNED EDGE-MODEL SUBMISSION kernel (writes submission.csv on the hidden test).

Same shape as build_edgemodel_submit.py, but its definitions come from
build_prune2_cv.py, so the submission supports the ABSTENTION lever:

    J = TP/(TP+FP+FN) and TP+FN = |GT edges| is CONSTANT.  A WRONG edge therefore
    costs an FP *and* an FN; emitting NOTHING costs only the FN that was already
    lost.  Dropping a wrong edge shrinks the denominator for free.  Break-even
    precision = 1/(1+1/J) = 52.8% of pruned edges actually being wrong.

Set SHIP below to the CV-winning arm before pushing (prune_tau / prune_mode /
max_link / learned_bonus).  Trains the edge CNN on ALL train movies (the 2 test
embryos match neither train embryo, so an all-data model beats the cross-embryo
OOF ones), then runs the full pipeline on the test.

NOTE: candidates are built at a 12um gate so the probability matrix covers every
pair a loose-gate arm can link; at an 8um gate the 8-12um pairs would carry
probability 0 and be pruned unconditionally, silently defeating the lever.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
SRC_BUILDER = HERE / "build_prune2_cv.py"          # has EPROB/SRCMAX + prune step
OUT_DIR = HERE / ("sub_" + __import__("os").environ.get("BIO_ARM","prunA"))
OUT_DIR.mkdir(exist_ok=True)

# ======== SET THIS TO THE CV WINNER BEFORE PUSHING ========
import os
# A = round-2 winner: loose gate 10um + learned prune 0.25 + re-route bonus 2.0
#     (CV +0.0028 pooled, positive on BOTH embryos). The loose gate is -0.0022 ALONE;
#     it only pays once the pruner deletes the junk it admits.
# B = conservative: shipped gate 8um + prune 0.10 + bonus 2.0 (CV +0.0018 both embryos),
#     isolating the pruning mechanism with no gate change.
# C = round-4 winner: A + division gate TIGHTENED to 3.0 (CV +0.0031 pooled, both
#     embryos). NOTE the CV-best arm was div 1.75, but that is a division RELAXATION --
#     the exact move CV has scored positive while the LB punished it hard (div gate 1.0
#     -> LB 0.903; div-relax measured -0.016). Tightening was LB-neutral (0.918 vs 0.919),
#     so div 3.0 takes nearly the same CV gain in the direction the LB has shown is safe.
_ARMS = {
    "prunA": {"max_link": 10.0, "prune_tau": 0.25, "prune_mode": "chosen", "learned_bonus": 2.0},
    "prunB": {"max_link": 8.0,  "prune_tau": 0.10, "prune_mode": "chosen", "learned_bonus": 2.0},
    "prunC": {"max_link": 10.0, "prune_tau": 0.25, "prune_mode": "chosen", "learned_bonus": 2.0,
              "div_diverge": 3.0},
    # D = prune6 winner region. The direct precision readout showed the pruner runs at
    #     73-94% precision (break-even 53.7%) but was only deleting 12% of wrong edges --
    #     recall, not precision, was the limit. tau .60 = CV +0.0049 both embryos; tau .70
    #     is +0.0051 but sits nearer the tau .85 collapse, and the two differ by less than
    #     the measured +-0.0007 CV noise, so .60 is the robust pick.
    "prunD": {"max_link": 10.0, "prune_tau": 0.60, "prune_mode": "chosen", "learned_bonus": 2.0,
              "div_diverge": 3.0},
    # ---- HIT-AND-TRIAL LADDER (08-28). LB noise on J is +-0.005..0.010 (only ~836 GT edges in a
    # ~4-movie test) while the PAIRED CV noise floor is +-0.0007, so CV is the higher-power
    # estimator. These are the CV-best prune doses that were NEVER scored (tau .60 was, = 0.918).
    # CV pooled vs control: .70 +0.0051 | .50 +0.0046 | .40 +0.0038 | .60@ml8 +0.0049 | .30 ~+0.003
    "prunE": {"max_link": 10.0, "prune_tau": 0.70, "prune_mode": "chosen", "learned_bonus": 2.0,
              "div_diverge": 3.0},
    "prunF": {"max_link": 10.0, "prune_tau": 0.50, "prune_mode": "chosen", "learned_bonus": 2.0,
              "div_diverge": 3.0},
    "prunG": {"max_link": 8.0,  "prune_tau": 0.60, "prune_mode": "chosen", "learned_bonus": 2.0,
              "div_diverge": 3.0},
    "prunH": {"max_link": 10.0, "prune_tau": 0.40, "prune_mode": "chosen", "learned_bonus": 2.0,
              "div_diverge": 3.0},
    "prunI": {"max_link": 12.0, "prune_tau": 0.70, "prune_mode": "chosen", "learned_bonus": 2.0,
              "div_diverge": 3.0},
}
TAG = os.environ.get("BIO_ARM", "prunA")
SHIP = _ARMS[TAG]
# ==========================================================

src = json.loads(SRC_NB.read_text(encoding="utf-8"))
base_cells = [src["cells"][i] for i in (0, 1, 2, 3, 4)]

b = SRC_BUILDER.read_text(encoding="utf-8")
cv = b.split("CV = r'''", 1)[1].split("\n'''", 1)[0]
DEFS = cv.split("# ---------- run CV ----------", 1)[0]

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
    print("zarr import failed:", str(e)[:120])
'''

TRAIN = r'''
# ===================== TRAIN edge CNN on ALL train movies =====================
import numpy as np, time, gc
from pathlib import Path
TRAIN_DIR = Path(ROOT) / "train"
N_TRAIN_PER_EMB = 6
MAXT = 90
BASE_CFG = dict(unet_thr=0.15, max_dt=1, gate=4.5, snap=3.2, mincand=0.10, cap=0.08, synth=True,
                div_diverge=2.25, div_sister=15.0, linker="accel", accel_bonus=0.80, accel_max=4.0,
                short_min=6, max_link=8.0, sim_w=4.0)          # sim4 (LB-0.921) base + accel
FEATCFG = dict(BASE_CFG, max_link=12.0)                        # widest gate any arm can use

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
t0all = time.time()
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
    blocks = build_pair_features(dets, FEATCFG); labs = label_blocks(blocks, dets, FEATCFG, gt_s)
    for tt, (bb, lb) in enumerate(zip(blocks, labs)):
        if bb is None or lb is None:
            continue
        k = lb["known"]
        if k.any():
            Xl.append(bb["X"][k]); yl.append(lb["y"][k])
            ik = bb["ii"][k].astype(np.int32); jk = bb["jj"][k].astype(np.int32)
            Rl.append(np.stack([np.full(len(ik), mi, np.int32), np.full(len(ik), tt, np.int32), ik, jk], 1))
    print("  data %s %s (%.0fs)" % (emb, stem, time.time() - t0all), flush=True)

X_all = np.concatenate(Xl).astype(np.float32); y_all = np.concatenate(yl).astype(np.int8); R_all = np.concatenate(Rl)
gmean = X_all.mean(0); gstd = X_all.std(0) + 1e-6; Xn_all = (X_all - gmean) / gstd
print("EDGE-MODEL rows=%d pos=%.1f%%; fitting on ALL data..." % (len(y_all), 100 * y_all.mean()), flush=True)
MODEL_ALL = train_cnn(R_all, Xn_all, y_all, epochs=16)
print("edge model READY", flush=True)
'''

SUBMIT = r'''
# ===================== RUN ON TEST -> submission.csv =====================
import pandas as pd, torch
SHIP = __SHIP__
print("SHIP cfg:", SHIP, flush=True)
CFG_SHIP = dict(BASE_CFG, linker="accel_rank", rank_mode="full", **SHIP)

def _infer_block(bb, sp, tt):
    src = sp[tt][bb["ii"]]; tgt = sp[tt + 1][bb["jj"]]
    P = np.stack([src, tgt], 1).astype(np.float32); Xn = (bb["X"] - gmean) / gstd
    out = np.zeros(len(bb["ii"]), np.float32); MODEL_ALL.eval()
    with torch.no_grad():
        for s0 in range(0, len(bb["ii"]), 1024):
            pb = torch.tensor(P[s0:s0 + 1024], dtype=torch.float32).to(DEV)
            xb = torch.tensor(Xn[s0:s0 + 1024], dtype=torch.float32).to(DEV)
            out[s0:s0 + 1024] = torch.sigmoid(MODEL_ALL(pb, xb)).cpu().numpy()
    return out

def track_movie_pruned(zp, ds, T):
    meta = read_array_meta(zp); dets = []; sp = []
    for t in range(T):
        vol = load_volume(zp, t, meta); c, s = detect(vol)
        c = np.asarray(c, np.float32).reshape(-1, 3); s = np.asarray(s, np.float32).reshape(-1)
        dets.append((c, s)); sp.append(extract_patches(vol, c[s >= UNET_THR])); del vol; gc.collect()
    blocks = build_pair_features(dets, FEATCFG)
    PR = []
    for tt, bb in enumerate(blocks):
        if bb is None:
            PR.append(None); continue
        p = _infer_block(bb, sp, tt)
        M = np.zeros((bb["np"], bb["nc"]), np.float32); M[bb["ii"], bb["jj"]] = p; PR.append(M)
    (pt, pp, pe), ngap, ndiv = repair_cfg(dets, CFG_SHIP, PR)
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
    t0 = time.time(); nodes, edges = track_movie_pruned(zp, ds, T); parts += [nodes, edges]
    print("  %s: T=%d nodes=%d edges=%d (%.1fs)" % (ds, T, len(nodes), len(edges), time.time() - t0), flush=True)
sub = pd.concat(parts, ignore_index=True); sub.index.name = "id"; sub.to_csv(OUT)
exp = ["dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
assert list(sub.columns) == exp, list(sub.columns)
print("wrote", OUT, "rows", len(sub), "nodes", int((sub.row_type == 'node').sum()), "edges", int((sub.row_type == 'edge').sum()))

expected = {p.name.replace('.zarr', '') for p in TEST_DIR.glob('*.zarr')}
written = set(sub.loc[sub.row_type == 'node', 'dataset'].unique())
assert not (expected - written), ("missing datasets", sorted(expected - written))
node_t = {(r.dataset, r.node_id): r.t for r in sub.loc[sub.row_type == 'node'].itertuples()}
for e in sub.loc[sub.row_type == 'edge'].itertuples():
    assert (e.dataset, e.source_id) in node_t and (e.dataset, e.target_id) in node_t
    assert node_t[(e.dataset, e.target_id)] == node_t[(e.dataset, e.source_id)] + 1
print("submission integrity PASS:", len(expected), "datasets")
'''.replace("__SHIP__", repr(SHIP))


def _cell(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s}

nb = dict(src)
nb["cells"] = [_cell(INSTALL)] + base_cells + [_cell(DEFS), _cell(TRAIN), _cell(SUBMIT)]
nb_path = OUT_DIR / ("biohub-" + TAG + "-submit.ipynb")
nb_path.write_text(json.dumps(nb), encoding="utf-8")
meta = {
    "id": "eeshsaxena/biohub-" + TAG + "-submit",
    "title": "Biohub " + TAG + " submit",
    "code_file": "biohub-" + TAG + "-submit.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": ["gpu"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models", "eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path, "| cells", len(nb["cells"]), "| SHIP", SHIP)
