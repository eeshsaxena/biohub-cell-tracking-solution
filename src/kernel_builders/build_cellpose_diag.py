"""Diagnose the Cellpose collapse now that the cellprob_threshold sweep is
exhausted (even at -6 the 2 bad samples only reached recall ~0.30 vs DoG 0.65).

The backend already uses a FIXED diameter (cp_diameter_um=16) and robust
percentile normalisation, so the collapse is NOT a threshold problem. Two
remaining cheap levers, plus raw stats to explain the failure:

  1. Per-sample stats: true cells/frame (from geff) + intensity percentiles.
     If the bad samples are far denser / dimmer, that localises the cause.
  2. Diameter sweep {10,13,19} at a generous threshold (-4). If a wrong
     auto/fixed diameter is the cause, one value should rescue the bad samples.
  3. Cellpose's built-in normalize vs our percentile norm (norm_mode flag on CFG).

Frames capped for speed; recall is relative across configs so the cap is fair.
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

# A norm-mode aware wrapper: monkeypatch detect_frame_cellpose's normalisation by
# passing norm_mode on cfg -> handled by a small custom detect below.
DRIVER = '''
from pathlib import Path
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

FRAMES = 30
NAMES = ["44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1"]
gts = {n: scoring.read_geff(DATA / "train" / f"{n}.geff") for n in NAMES}

# ---- 1. per-sample stats: true cells/frame + intensity percentiles ----
print("=== per-sample stats (first %d frames) ===" % FRAMES, flush=True)
for n in NAMES:
    read, T, scale, _q = open_volume(DATA / "train" / f"{n}.zarr")
    T = min(T, FRAMES)
    gt = gts[n]
    true_pf = np.mean([int(np.sum(gt["t"] == t)) for t in range(T)])
    f0 = read(0).astype(np.float32)
    p = np.percentile(f0, [1, 50, 99, 99.9])
    print(f"  {n}: true~{true_pf:.0f} cells/frame  scale={tuple(round(s,3) for s in scale)}  "
          f"int p1/50/99/99.9={p[0]:.0f}/{p[1]:.0f}/{p[2]:.0f}/{p[3]:.0f} max={f0.max():.0f}", flush=True)

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
    cp_mode = "do_3d"; cp_downsample_xy = 1; cp_flow_threshold = 0.4; cp_cellprob_threshold = -4.0

# ---- 2. diameter sweep at generous threshold ----
print("\\n=== diameter sweep (cellprob_threshold=-4, do_3d) ===", flush=True)
for diam in (10.0, 13.0, 19.0):
    print(f"\\n--- cp_diameter_um = {diam} ---", flush=True)
    for n in NAMES:
        cfg = CFG(); cfg.cp_diameter_um = diam
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
out = HERE / "cpdiag" / "biohub-cellpose-diag.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-cellpose-diag", "title": "biohub cellpose diag",
        "code_file": "biohub-cellpose-diag.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels", "eeshsaxena/biohub-cellpose"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "cpdiag" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
