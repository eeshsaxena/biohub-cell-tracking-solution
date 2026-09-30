"""TRUE-METRIC CV of the trained detector: full detect->link->score pipeline.

Recall != the competition metric. This runs the FULL pipeline (detect_sample_unet
-> assemble -> scoring.per_sample) on the GT-dense held-out samples at thr
{0.05,0.10,0.20} and reports the actual ADJUSTED EDGE JACCARD per embryo (which
accounts for linking quality AND the node-count over-detection penalty). Tells us
the score-optimal threshold, not just the recall-optimal one.

Efficient: heatmap computed ONCE per frame; peaks + linking + scoring run per thr.
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
import numpy as np, time, json, glob, torch

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

def find_file(name):
    hits = glob.glob(f"/kaggle/input/**/{name}", recursive=True)
    if not hits:
        raise RuntimeError(name + " not found")
    return hits[0]
DCFG = json.load(open(find_file("detector.json")))
print("detector config:", DCFG, flush=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = build_unet(base=DCFG["base"], depth=DCFG["depth"]).to(device)
model.load_state_dict(torch.load(find_file("detector.pt"), map_location=device)); model.eval()

CV = ["6bba_09961292", "6bba_bb9f20c3", "44b6_d29c9ab2", "44b6_3a861e03"]
THRS = [0.05, 0.10, 0.20]
MINSEP = float(DCFG.get("min_sep_um", 3.5))
ZT = int(DCFG.get("unet_z_tile", 64)); ZO = int(DCFG.get("unet_z_overlap", 0))

def score_prediction(nodes, edges, gt):
    if not nodes:
        return {"edge_tp": 0, "edge_fp": 0, "edge_fn": len(gt["edges"]),
                "num_pred_nodes": 0, "node_recall": 0.0}
    arr = np.asarray(nodes, dtype=np.float64)
    pred_edges = np.asarray(edges, dtype=np.int64).reshape(-1, 2)
    return scoring.evaluate_edges(arr[:, 0].astype(np.int64), arr[:, 1:4], pred_edges, gt)

rows_by = {thr: {} for thr in THRS}
for n in CV:
    read, T, scale, _q = open_volume(TRAIN / f"{n}.zarr")
    gt = scoring.read_geff(TRAIN / f"{n}.geff")
    # heatmap ONCE per frame -> dets for each thr; shifts once (motion comp)
    dets_by = {thr: [] for thr in THRS}
    shifts = []
    prev = None
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
        cfg = Config(min_sep_um=MINSEP, max_gap=2, link_radius_um=7.0, gap_radius_um=9.0,
                     motion_compensate=True, device="cuda")
        nodes, edges = assemble(dets_by[thr], shifts, cfg, scale)
        er = score_prediction(nodes, edges, gt)
        row = scoring.per_sample(er, gt["n_total"])
        rows_by[thr].setdefault(n.split("_")[0], []).append(row)
        print(f"  {n} thr{thr}: adj={row['adj_edge_jaccard']:.3f} J={row['edge_jaccard']:.3f} "
              f"recall={row['node_recall']:.3f} ratio={row['total_node_ratio']:+.2f} "
              f"npred={er['num_pred_nodes']}", flush=True)
    print(f"  ({n} done in {time.time()-t0:.0f}s)", flush=True)

print("\\n=== worst-embryo ADJUSTED EDGE JACCARD by threshold (the real metric) ===", flush=True)
best = (None, -1)
for thr in THRS:
    per = {e: scoring.summarise(rows)["adj_edge_jaccard"] for e, rows in rows_by[thr].items()}
    worst = min(per.values())
    print(f"  thr={thr}: per-embryo {{{', '.join(f'{e}:{v:.3f}' for e,v in per.items())}}}  worst={worst:.3f}", flush=True)
    if worst > best[1]:
        best = (thr, worst)
print(f"BEST thr={best[0]} worst-embryo adj_edge_jaccard={best[1]:.3f}  (LB DoG=0.825)", flush=True)
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
out = HERE / "detscorecv" / "biohub-detector-scorecv.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-detector-scorecv", "title": "biohub detector scorecv",
        "code_file": "biohub-detector-scorecv.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels", "eeshsaxena/biohub-detector"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "detscorecv" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
