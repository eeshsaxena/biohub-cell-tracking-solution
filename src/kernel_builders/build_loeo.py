"""LEAVE-ONE-EMBRYO-OUT diagnostic: does the trained detector transfer to an
UNSEEN embryo? v3 (trained on BOTH embryos) scored LB 0.682 << DoG 0.825, while
same-embryo CV said 0.77. The test has 2 DIFFERENT embryos, so the only honest
signal is cross-embryo. This trains on ONE embryo and scores (full detect->link->
metric) the OTHER, sweeping the per-frame COUNT CAP (unet_max_per_frame) to test
whether count-calibration removes the over-detection penalty that likely sank v3.

Both directions -> worst-embryo cross-embryo adjusted edge Jaccard. If that clears
DoG's ~0.65 CV-equivalent / points above 0.82-ish, a count-capped U-Net can beat
0.825; if it collapses, the detector overfits embryo appearance (need augmentation).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def strip_local_imports(src):
    out = []
    for ln in src.splitlines(keepends=True):
        s = ln.strip()
        drop = (s == "import scoring" or s.startswith("from pipeline import")
                or s.startswith("import detector"))
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
print("torch", torch.__version__, "cuda", torch.cuda.is_available(), flush=True)
'''

DRIVER = '''
from pathlib import Path
import numpy as np, time, json, torch

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

# rank all samples by GT density (read every geff once)
rng = np.random.default_rng(0)
ALL = sorted(p.stem for p in TRAIN.glob("*.geff"))
geffs, counts = {}, {}
for n in ALL:
    try:
        g = scoring.read_geff(TRAIN / f"{n}.geff")
    except Exception:
        continue
    geffs[n] = g; counts[n] = len(g["t"])
by_emb = {}
for n in sorted(counts, key=lambda k: -counts[k]):
    by_emb.setdefault(n.split("_")[0], []).append(n)
print("embryos:", {k: len(v) for k, v in by_emb.items()}, flush=True)

N_TRAIN = 14; F_PER = 4
def preload(names):
    frames = []
    for n in names:
        read, T, scale, _q = open_volume(TRAIN / f"{n}.zarr")
        g = geffs[n]; tt = g["t"]
        if len(tt) == 0:
            continue
        tc = np.bincount(tt, minlength=int(tt.max()) + 1)
        for t in [int(x) for x in np.argsort(-tc)[:F_PER] if x < T]:
            gi = np.nonzero(tt == t)[0]
            frames.append((normalize_frame(read(t)).astype(np.float32), g["pos"][gi].astype(np.float32), scale))
    return frames

def score_prediction(nodes, edges, gt):
    if not nodes:
        return {"edge_tp": 0, "edge_fp": 0, "edge_fn": len(gt["edges"]), "num_pred_nodes": 0, "node_recall": 0.0}
    arr = np.asarray(nodes, dtype=np.float64)
    return scoring.evaluate_edges(arr[:, 0].astype(np.int64), arr[:, 1:4],
                                  np.asarray(edges, dtype=np.int64).reshape(-1, 2), gt)

SIGMA = 2.5; MINSEP = 3.5; THR = 0.05
BUDGETS = [0, 250, 350]   # 0 = uncapped (like v3); others = count-calibrated
results = {}
for train_emb, eval_emb in [("44b6", "6bba"), ("6bba", "44b6")]:
    tr_names = by_emb[train_emb][:N_TRAIN]
    ev_names = by_emb[eval_emb][:2]   # densest 2 of the UNSEEN embryo
    print(f"\\n### TRAIN {train_emb} ({len(tr_names)}) -> EVAL {eval_emb} {ev_names} ###", flush=True)
    frames = preload(tr_names)
    print(f"preloaded {len(frames)} frames, mean GT/frame {np.mean([len(f[1]) for f in frames]):.0f}", flush=True)
    t0 = time.time()
    model, hist = train_detector(lambda: frames[rng.integers(len(frames))], steps=3000,
                                 patch=(24, 128, 128), sigma_um=SIGMA, base=32, depth=3,
                                 batch=4, lr=1e-3, device=device, log_every=1000)
    print(f"trained in {time.time()-t0:.0f}s, loss {hist[0][1]:.3f}->{hist[-1][1]:.3f}", flush=True)
    for n in ev_names:
        read, T, scale, _q = open_volume(TRAIN / f"{n}.zarr")
        gt = geffs[n]
        # heatmap once per frame; dets per budget
        dets_by = {b: [] for b in BUDGETS}; shifts = []; prev = None
        t0 = time.time()
        for t in range(T):
            frame = read(t)
            hm = predict_heatmap(normalize_frame(frame), model, device, z_tile=64, z_overlap=0)
            for b in BUDGETS:
                coords, _ = peaks_from_heatmap(hm, scale, MINSEP, THR, max_per_frame=b)
                dets_by[b].append((coords, np.ones(len(coords), np.float32)))
            if t > 0:
                try: shifts.append(phase_shift(prev, frame, Config(mc_downsample=2)))
                except Exception: shifts.append(np.zeros(3, np.float32))
            prev = frame
        for b in BUDGETS:
            cfg = Config(min_sep_um=MINSEP, max_gap=1, link_radius_um=7.0, gap_radius_um=9.0,
                         motion_compensate=True, device="cuda")
            nodes, edges = assemble(dets_by[b], shifts, cfg, scale)
            row = scoring.per_sample(score_prediction(nodes, edges, gt), gt["n_total"])
            results.setdefault(b, {}).setdefault(eval_emb, []).append(row)
            print(f"  [{eval_emb}] {n} budget={b}: adj={row['adj_edge_jaccard']:.3f} "
                  f"J={row['edge_jaccard']:.3f} recall={row['node_recall']:.3f} "
                  f"ratio={row['total_node_ratio']:+.2f} npred={row['num_pred_nodes']}", flush=True)
        print(f"  ({n} eval {time.time()-t0:.0f}s)", flush=True)

print("\\n=== CROSS-EMBRYO (LOEO) worst-embryo adj by count budget (DoG LB 0.825) ===", flush=True)
for b in BUDGETS:
    per = {e: scoring.summarise(rows)["adj_edge_jaccard"] for e, rows in results[b].items()}
    worst = min(per.values())
    print(f"  budget={b}: {{{', '.join(f'{e}:{v:.3f}' for e,v in per.items())}}} worst={worst:.3f}", flush=True)
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
out = HERE / "loeo" / "biohub-loeo.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-loeo", "title": "biohub loeo",
        "code_file": "biohub-loeo.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "loeo" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
