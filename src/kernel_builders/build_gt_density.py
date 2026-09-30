"""Rank ALL train samples by GT annotation density (CPU-only, NO GPU -> quota-free).

The cellpose-diag run revealed the 4 CV samples are a bad benchmark: 2 of them
have ~0-1 annotated nuclei/frame in the first 30 frames, so recall there is noise.
This kernel reads every train .geff and reports, per sample: total GT nodes, GT
nodes in frames [0,30) vs [0,100), edges, and the per-embryo distribution — so we
can pick GT-DENSE CV samples and eval over frames where GT actually exists.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

SCORING = (ROOT / "kaggle" / "scoring.py").read_text(encoding="utf-8")
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
'''

DRIVER = '''
from pathlib import Path
import numpy as np

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
TRAIN = DATA / "train"
names = sorted(p.stem for p in TRAIN.glob("*.geff"))
print("n train geff:", len(names), flush=True)

rows = []
for n in names:
    try:
        g = scoring.read_geff(TRAIN / f"{n}.geff")
    except Exception as e:
        print("  ERR", n, e, flush=True); continue
    t = g["t"]; ne = len(g["edges"])
    Tmax = int(t.max()) + 1 if len(t) else 0
    n30 = int(np.sum(t < 30))
    rows.append((n, len(t), n30, ne, Tmax, 0))
rows.sort(key=lambda r: -r[1])
print("\\n=== samples by total GT nodes (top 20) ===", flush=True)
print(f"{'sample':16} {'nodes':>7} {'nodes<30':>9} {'edges':>7} {'Tmax':>5} {'nodes/frame':>11}", flush=True)
for n, tot, n30, ne, Tmax, _ in rows[:20]:
    print(f"{n:16} {tot:7d} {n30:9d} {ne:7d} {Tmax:5d} {tot/max(Tmax,1):11.1f}", flush=True)
print("\\n=== bottom 10 (sparsest) ===", flush=True)
for n, tot, n30, ne, Tmax, _ in rows[-10:]:
    print(f"{n:16} {tot:7d} {n30:9d} {ne:7d} {Tmax:5d} {tot/max(Tmax,1):11.1f}", flush=True)

# per-embryo stats + suggested dense CV picks (top-2 densest per embryo)
by_emb = {}
for n, tot, n30, ne, Tmax, _ in rows:
    by_emb.setdefault(n.split("_")[0], []).append((n, tot, n30, ne, Tmax))
print("\\n=== per-embryo ===", flush=True)
for emb, rs in by_emb.items():
    tots = np.array([r[1] for r in rs])
    print(f"  {emb}: {len(rs)} samples, GT nodes total median {int(np.median(tots))} "
          f"min {int(tots.min())} max {int(tots.max())}", flush=True)
    dense = sorted(rs, key=lambda r: -r[1])[:2]
    print(f"    densest CV picks: {[d[0] for d in dense]} (nodes {[d[1] for d in dense]})", flush=True)
'''

cells = [INSTALL, "# scoring\n" + SCORING + SHIM, DRIVER]
nb_cells = []
for src in cells:
    compile(src, "<c>", "exec")
    nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                     "source": src.splitlines(keepends=True)})
print("all cells compile")
nb = {"cells": nb_cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}}, "nbformat": 4, "nbformat_minor": 5}
out = HERE / "gtdensity" / "biohub-gt-density.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-gt-density", "title": "biohub gt density",
        "code_file": "biohub-gt-density.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": False, "enable_tpu": False, "enable_internet": False,
        "keywords": [], "dataset_sources": ["eeshsaxena/biohub-zarr-wheels"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "gtdensity" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
