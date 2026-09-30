"""Detector v3: AUGMENTED training + TRUE leave-one-embryo-out validation.

Why this kernel exists (the gap in v2/scorecv): the 0.771 CV trained on BOTH
embryos and evaluated on held-out samples of THOSE SAME embryos. The real test is
two DIFFERENT embryos, and STRATEGY.md says leave-one-embryo-out (LOEO) is the
only trustworthy signal. This kernel:

  Phase A (TRUST) -- true LOEO with augmentation:
    train on 6bba only  -> score (full detect->link->score) on 44b6 held-out
    train on 44b6 only  -> score on 6bba held-out
    worst-embryo LOEO adj_edge_jaccard = the number that actually predicts the LB.

  Phase C (SHIP) -- the improved model we would submit:
    train on BOTH embryos' dense samples (excl the 4 held-out CV) WITH augmentation
    + more frames, eval true-metric on the 4 held-out over a fine/low threshold
    sweep {0.03,0.05,0.075,0.10}, bake the score-optimal thr into detector.json,
    save detector.pt (-> re-version the biohub-detector dataset for the v4 submit).

Augmentation (kaggle/detector.augment_patch): 3-axis flips + YX transpose (geom,
applied to input+heatmap together) and gamma/scale/noise jitter (input only) --
directly targets the per-session intensity shift that collapsed pretrained Cellpose.
Everything else (linking, gap recovery, scoring, submission) is reused unchanged.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def strip_local_imports(src):
    out = []
    for ln in src.splitlines(keepends=True):
        s = ln.strip()
        drop = (s == "import scoring" or s == "import detector as D"
                or s.startswith("from pipeline import") or s.startswith("import detector"))
        out.append(("# " + ln) if drop else ln)
    return "".join(out)


SCORING = (ROOT / "kaggle" / "scoring.py").read_text(encoding="utf-8")
PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]
DETECTOR = strip_local_imports((ROOT / "kaggle" / "detector.py").read_text(encoding="utf-8"))
SHIM = '\nimport types as _t\nscoring = _t.SimpleNamespace(**{k: v for k, v in list(globals().items()) if not k.startswith("_")})\n'

INSTALL = '''
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
print("zarr rc", r.returncode, flush=True)
import torch
print("torch", torch.__version__, "cuda", torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "-", flush=True)
'''

DRIVER = '''
from pathlib import Path
import numpy as np, time, json, gc, torch

def find_data_root():
    slug = "biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"), Path(f"/kaggle/input/{slug}")):
        if (c / "train").exists():
            return c
    for p in Path("/kaggle/input").rglob("train"):
        if p.is_dir() and any(p.glob("*.zarr")):
            return p.parent
    raise RuntimeError("no data root")
DATA = find_data_root(); TRAIN = DATA / "train"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
rng = np.random.default_rng(0)

# GT-dense held-out CV (same 4 samples as scorecv -> the 0.771 is directly comparable)
CV = ["6bba_09961292", "6bba_bb9f20c3", "44b6_d29c9ab2", "44b6_3a861e03"]
ALL = sorted(p.stem for p in TRAIN.glob("*.geff"))
pool = [n for n in ALL if n not in CV]

# rank pool by GT density; group by embryo
t0 = time.time(); geffs = {}; counts = {}
for n in pool:
    try:
        g = scoring.read_geff(TRAIN / f"{n}.geff")
    except Exception:
        continue
    geffs[n] = g; counts[n] = len(g["t"])
print(f"ranked {len(counts)} samples by GT density in {time.time()-t0:.0f}s", flush=True)
by_emb = {}
for n in sorted(counts, key=lambda k: -counts[k]):
    by_emb.setdefault(n.split("_")[0], []).append(n)
EMBS = sorted(by_emb)   # ['44b6','6bba']
print("embryos:", {e: len(v) for e, v in by_emb.items()}, flush=True)

N_PER_EMB = 20      # densest samples per embryo used for training
F_PER = 6           # GT-densest frames per sample

# ---- data / model / eval helpers -----------------------------------------
def preload(names):
    """names -> list of (frame_norm float32[Z,Y,X], pts_vox[N,3], scale)."""
    frames = []
    for n in names:
        read, T, scale, _q = open_volume(TRAIN / f"{n}.zarr")
        g = geffs[n]; tt = g["t"]
        if len(tt) == 0:
            continue
        tcount = np.bincount(tt, minlength=int(tt.max()) + 1)
        best_ts = [int(t) for t in np.argsort(-tcount)[:F_PER] if t < T]
        for t in best_ts:
            fr = normalize_frame(read(t))
            gi = np.nonzero(tt == t)[0]
            frames.append((fr.astype(np.float32), g["pos"][gi].astype(np.float32), scale))
    return frames

CFG = dict(steps=3000, patch=(24, 128, 128), sigma_um=2.5, base=32, depth=3,
           batch=4, lr=1.0e-3, unet_peak_thresh=0.05, min_sep_um=3.5,
           unet_z_tile=64, unet_z_overlap=0, augment=True)
print("train config:", CFG, flush=True)

def train_on(names, steps, seed=0):
    frames = preload(names)
    mean = np.mean([len(f[1]) for f in frames]) if frames else 0
    print(f"  train on {len(names)} samples -> {len(frames)} frames, "
          f"mean {mean:.0f} GT/frame", flush=True)
    prov = lambda: frames[np.random.default_rng().integers(len(frames))]
    t0 = time.time()
    model, hist = train_detector(prov, steps=steps, patch=CFG["patch"],
        sigma_um=CFG["sigma_um"], base=CFG["base"], depth=CFG["depth"],
        batch=CFG["batch"], lr=CFG["lr"], device=device, log_every=500,
        seed=seed, augment=CFG["augment"])
    print(f"  trained {steps} steps in {time.time()-t0:.0f}s; "
          f"loss {hist[0][1]:.4f} -> {hist[-1][1]:.4f}", flush=True)
    del frames; gc.collect()
    return model

THRS = [0.03, 0.05, 0.075, 0.10]
MINSEP = CFG["min_sep_um"]; ZT = CFG["unet_z_tile"]; ZO = CFG["unet_z_overlap"]

def score_prediction(nodes, edges, gt):
    if not nodes:
        return {"edge_tp": 0, "edge_fp": 0, "edge_fn": len(gt["edges"]),
                "num_pred_nodes": 0, "node_recall": 0.0}
    arr = np.asarray(nodes, dtype=np.float64)
    pe = np.asarray(edges, dtype=np.int64).reshape(-1, 2)
    return scoring.evaluate_edges(arr[:, 0].astype(np.int64), arr[:, 1:4], pe, gt)

def eval_true_metric(model, names, tag):
    """Full detect->link->score on `names`; returns rows_by[thr][emb]=list(row)."""
    model.eval()
    rows_by = {thr: {} for thr in THRS}
    for n in names:
        read, T, scale, _q = open_volume(TRAIN / f"{n}.zarr")
        gt = scoring.read_geff(TRAIN / f"{n}.geff")
        dets_by = {thr: [] for thr in THRS}; shifts = []; prev = None
        t0 = time.time()
        for t in range(T):
            frame = read(t)
            hm = predict_heatmap(normalize_frame(frame), model, device, z_tile=ZT, z_overlap=ZO)
            for thr in THRS:
                coords, _ = peaks_from_heatmap(hm, scale, MINSEP, thr)
                dets_by[thr].append((coords, np.ones(len(coords), np.float32)))
            if t > 0:
                try:
                    shifts.append(phase_shift(prev, frame, Config(mc_downsample=2)))
                except Exception:
                    shifts.append(np.zeros(3, np.float32))
            prev = frame
        for thr in THRS:
            cfg = Config(min_sep_um=MINSEP, max_gap=2, link_radius_um=7.0,
                         gap_radius_um=9.0, motion_compensate=True, device="cuda")
            nodes, edges = assemble(dets_by[thr], shifts, cfg, scale)
            er = score_prediction(nodes, edges, gt)
            row = scoring.per_sample(er, gt["n_total"])
            rows_by[thr].setdefault(n.split("_")[0], []).append(row)
            print(f"  [{tag}] {n} thr{thr}: adj={row['adj_edge_jaccard']:.3f} "
                  f"J={row['edge_jaccard']:.3f} recall={row['node_recall']:.3f} "
                  f"ratio={row['total_node_ratio']:+.2f} npred={er['num_pred_nodes']}", flush=True)
        print(f"  [{tag}] ({n} done in {time.time()-t0:.0f}s)", flush=True)
    return rows_by

def worst_by_thr(rows_by):
    out = {}
    for thr in THRS:
        per = {e: scoring.summarise(rows)["adj_edge_jaccard"] for e, rows in rows_by[thr].items()}
        out[thr] = (min(per.values()) if per else float("nan"), per)
    return out

# ============================ Phase A: TRUE LOEO ============================
print("\\n########## PHASE A: leave-one-embryo-out (augmented) ##########", flush=True)
loeo_rows = {thr: {} for thr in THRS}
for i, test_emb in enumerate(EMBS):
    train_emb = [e for e in EMBS if e != test_emb][0]
    train_names = by_emb[train_emb][:N_PER_EMB]
    test_names = [n for n in CV if n.startswith(test_emb)]
    print(f"\\n--- LOEO: train on {train_emb} ({len(train_names)}), "
          f"test on {test_emb} {test_names} ---", flush=True)
    m = train_on(train_names, steps=2000, seed=i)
    rb = eval_true_metric(m, test_names, tag=f"LOEO-{test_emb}")
    for thr in THRS:
        loeo_rows[thr].update(rb[thr])   # rb[thr] has just this embryo
    del m; gc.collect(); torch.cuda.empty_cache()

print("\\n=== LOEO worst-embryo ADJUSTED EDGE JACCARD (trustworthy vs LB DoG 0.825) ===", flush=True)
loeo_worst = worst_by_thr(loeo_rows)
loeo_best = max(THRS, key=lambda t: loeo_worst[t][0])
for thr in THRS:
    w, per = loeo_worst[thr]
    print(f"  thr={thr}: {{{', '.join(f'{e}:{v:.3f}' for e,v in per.items())}}}  worst={w:.3f}", flush=True)
print(f"LOEO BEST thr={loeo_best} worst-embryo={loeo_worst[loeo_best][0]:.3f}", flush=True)

# ============================ Phase C: SHIP model ============================
print("\\n########## PHASE C: augmented SHIP model (both embryos) ##########", flush=True)
ship_names = []
for e in EMBS:
    ship_names += by_emb[e][:N_PER_EMB]
ship = train_on(ship_names, steps=CFG["steps"], seed=7)
torch.save(ship.state_dict(), "/kaggle/working/detector.pt")
ship_rows = eval_true_metric(ship, CV, tag="SHIP")
print("\\n=== SHIP (held-out, same-embryo) worst-embryo adj by threshold ===", flush=True)
ship_worst = worst_by_thr(ship_rows)
ship_best = max(THRS, key=lambda t: ship_worst[t][0])
for thr in THRS:
    w, per = ship_worst[thr]
    print(f"  thr={thr}: {{{', '.join(f'{e}:{v:.3f}' for e,v in per.items())}}}  worst={w:.3f}", flush=True)
print(f"SHIP BEST thr={ship_best} worst-embryo={ship_worst[ship_best][0]:.3f} "
      f"(v2 no-aug scorecv was 0.771 @0.05)", flush=True)

# bake the score-optimal threshold from the SHIP held-out sweep
outcfg = dict(CFG); outcfg["unet_peak_thresh"] = float(ship_best)
json.dump(outcfg, open("/kaggle/working/detector.json", "w"))
print("\\nsaved detector.pt + detector.json (unet_peak_thresh ->", ship_best, ")", flush=True)
print("SUMMARY  LOEO(trust)=%.3f @thr%s | SHIP(held-out)=%.3f @thr%s"
      % (loeo_worst[loeo_best][0], loeo_best, ship_worst[ship_best][0], ship_best), flush=True)
'''

cells = [INSTALL, "# scoring\n" + SCORING + SHIM, "# pipeline\n" + PIPELINE,
         "# detector\n" + DETECTOR, DRIVER]
nb_cells = []
for src in cells:
    compile(src, "<c>", "exec")
    nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                     "source": src.splitlines(keepends=True)})
print("all cells compile")
nb = {"cells": nb_cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}}, "nbformat": 4, "nbformat_minor": 5}
out = HERE / "detv3" / "biohub-detector-v3.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-detector-v3", "title": "biohub detector v3",
        "code_file": "biohub-detector-v3.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "detv3" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
