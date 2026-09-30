"""Trustworthy CV of the trained detector: GT-DENSE held-out samples, ALL frames.

The original 4 CV samples were among the 10 SPARSEST in the dataset (~0.7-1
GT/frame) so their recall was noise. gt-density picked the densest held-out
samples per embryo. This kernel loads detector.pt (dataset biohub-detector) and
reports node recall over all 100 frames, sweeping unet_peak_thresh cheaply
(heatmap computed ONCE per frame, peaks extracted at each threshold).
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
WEIGHTS = find_file("detector.pt")
DCFG = json.load(open(find_file("detector.json")))
print("detector config:", DCFG, flush=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = build_unet(base=DCFG["base"], depth=DCFG["depth"]).to(device)
model.load_state_dict(torch.load(WEIGHTS, map_location=device)); model.eval()

# GT-dense held-out CV picks from biohub-gt-density (2 per embryo, none in training)
CV = ["6bba_09961292", "6bba_bb9f20c3", "44b6_d29c9ab2", "44b6_3a861e03"]
THRS = [0.15, 0.30, 0.45]
MINSEP = float(DCFG.get("min_sep_um", 4.5))

per_emb = {thr: {} for thr in THRS}
for n in CV:
    read, T, scale, _q = open_volume(TRAIN / f"{n}.zarr")
    gt = scoring.read_geff(TRAIN / f"{n}.geff")
    hits = {thr: 0 for thr in THRS}; npred = {thr: 0 for thr in THRS}; tot = 0
    t0 = time.time()
    for t in range(T):
        gi = np.nonzero(gt["t"] == t)[0]
        if len(gi) == 0:
            continue
        fn = normalize_frame(read(t))
        hm = predict_heatmap(fn, model, device,
                             z_tile=int(DCFG.get("unet_z_tile", 32)),
                             z_overlap=int(DCFG.get("unet_z_overlap", 8)))
        tot += len(gi)
        for thr in THRS:
            coords, _ = peaks_from_heatmap(hm, scale, MINSEP, thr)
            npred[thr] += len(coords)
            if len(coords):
                m = scoring.match_nodes(np.full(len(coords), t), coords.astype(float),
                                        np.full(len(gi), t), gt["pos"][gi], scale, 7.0)
                hits[thr] += int(np.sum(m >= 0))
    emb = n.split("_")[0]
    line = f"{n} (true~{tot//max(T,1)}/frame, {tot} total): "
    for thr in THRS:
        rec = hits[thr] / tot if tot else float("nan")
        per_emb[thr].setdefault(emb, []).append(rec)
        line += f" thr{thr}={rec:.3f}(~{npred[thr]//T}pf)"
    print(line + f"  {time.time()-t0:.0f}s", flush=True)

print("\\n=== worst-embryo recall by threshold (vs DoG 0.65) ===", flush=True)
for thr in THRS:
    worst = min(np.mean(v) for v in per_emb[thr].values())
    means = {k: round(float(np.mean(v)), 3) for k, v in per_emb[thr].items()}
    print(f"  thr={thr}: per-embryo {means}  worst-embryo={worst:.3f}", flush=True)
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
out = HERE / "detcv" / "biohub-detector-cv.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-detector-cv", "title": "biohub detector cv",
        "code_file": "biohub-detector-cv.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels", "eeshsaxena/biohub-detector"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "detcv" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
