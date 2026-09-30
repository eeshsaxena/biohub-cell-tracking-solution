"""Stabilise Cellpose: sweep cellprob_threshold to fix the samples where it
collapses (recall 0.02/0.17, node ratio -0.8 = detecting ~20% of cells).

Cellpose already hits recall ~1.0 on well-behaved samples (>> DoG's 0.65). The
failures are a threshold problem: on samples whose normalised intensity sits low
for the model, cellprob stays under 0 and few masks survive. Lowering
cellprob_threshold recovers them. FP detections are cheap (invisible to the edge
metric unless matched), so we can afford a generous threshold.

Frames capped for speed; recall is relative across thresholds so the cap is fair.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def strip_local_imports(src):
    out = []
    for ln in src.splitlines(keepends=True):
        s = ln.strip()
        out.append(("# " + ln) if (s == "import scoring" or s.startswith("from pipeline import")) else ln)
    return "".join(out)


SCORING = (ROOT / "kaggle" / "scoring.py").read_text(encoding="utf-8")
PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]
CPDET = strip_local_imports((ROOT / "kaggle" / "cellpose_detect.py").read_text(encoding="utf-8"))
SHIM = '\nimport types as _t\nscoring = _t.SimpleNamespace(**{k: v for k, v in list(globals().items()) if not k.startswith("_")})\n'

INSTALL = '''
import os, glob, subprocess, sys
def find_wheeldir(slug):
    for base in (f"/kaggle/input/{slug}", f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(base):
            return base
    hits = [p for p in glob.glob(f"/kaggle/input/**/{slug}", recursive=True) if os.path.isdir(p)]
    return hits[0] if hits else None
for name, slug in [("zarr", "biohub-zarr-wheels"), ("cellpose", "biohub-cellpose")]:
    wd = find_wheeldir(slug)
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-index",
                        f"--find-links={wd}", name], capture_output=True, text=True)
    print(name, "rc", r.returncode, flush=True)
CELLPOSE_WEIGHTS = os.path.join(find_wheeldir("biohub-cellpose") or "", "nucleitorch_0")
'''

DRIVER = '''
from pathlib import Path
from collections import defaultdict
import numpy as np, time
from cellpose import models

def find_data_root():
    slug = "biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"), Path(f"/kaggle/input/{slug}")):
        if (c / "train").exists():
            return c
    for p in Path("/kaggle/input").rglob("train"):
        if p.is_dir() and any(p.glob("*.zarr")):
            return p.parent
    raise RuntimeError("no data root")
DATA = find_data_root()
model = models.CellposeModel(gpu=True, pretrained_model=CELLPOSE_WEIGHTS)

FRAMES = 50
# The 2 good + 2 collapsed samples from the CV run.
NAMES = ["44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1"]
gts = {n: scoring.read_geff(DATA / "train" / f"{n}.geff") for n in NAMES}

def cellpose_recall(zp, cfg, gt):
    read, T, scale, _q = open_volume(zp)
    T = min(T, FRAMES)
    hit = tot = npred = 0
    for t in range(T):
        gi = np.nonzero(gt["t"] == t)[0]
        coords = detect_frame_cellpose(read(t), model, cfg, scale)
        npred += len(coords)
        if len(gi) == 0:
            continue
        m = scoring.match_nodes(np.full(len(coords), t), coords.astype(float),
                                np.full(len(gi), t), gt["pos"][gi], scale, 7.0)
        hit += int(np.sum(m >= 0)); tot += len(gi)
    return (hit / tot if tot else float("nan")), npred

class CFG:
    cp_mode = "do_3d"; cp_downsample_xy = 1; cp_diameter_um = 16.0; cp_flow_threshold = 0.4

for thr in (0.0, -2.0, -4.0, -6.0):
    print(f"\\n=== cellprob_threshold = {thr} ===", flush=True)
    for n in NAMES:
        cfg = CFG(); cfg.cp_cellprob_threshold = thr
        t0 = time.time()
        rec, npred = cellpose_recall(DATA / "train" / f"{n}.zarr", cfg, gts[n])
        print(f"  {n}: recall={rec:.3f}  ~{npred//FRAMES} cells/frame  {time.time()-t0:.0f}s", flush=True)
'''

cells = [INSTALL, "# scoring\n" + SCORING + SHIM, "# pipeline\n" + PIPELINE, "# cpdet\n" + CPDET, DRIVER]
nb_cells = []
for src in cells:
    compile(src, "<c>", "exec")
    nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                     "source": src.splitlines(keepends=True)})
print("all cells compile")
nb = {"cells": nb_cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}}, "nbformat": 4, "nbformat_minor": 5}
out = HERE / "cpsweep" / "biohub-cellpose-sweep.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-cellpose-sweep", "title": "biohub cellpose sweep",
        "code_file": "biohub-cellpose-sweep.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels", "eeshsaxena/biohub-cellpose"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "cpsweep" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
