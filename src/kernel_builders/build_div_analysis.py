"""Analyze DIVISIONS in the train GT (CPU-only -> no GPU quota).

score = adj_edge_jaccard + 0.1 * division_jaccard (ADDITIVE, official metrics.py:522).
We emit zero divisions, so we forfeit the whole 0.1. division_jaccard >= 0 and is
ADDED, so emitting forks can only help the division term; the only cost is a few FP
edges. To emit forks WELL we need the geometry of real divisions.

Reports:
  1. how many samples have >=1 division, and the count distribution
  2. per division: parent->daughter displacement, daughter-daughter separation,
     and the ratio vs normal (non-division) frame-to-frame displacement
  3. a separability check: can (two candidate successors close together) discriminate
     a real division from a normal link? -> gives the decision rule + thresholds
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
DATA = find_data_root(); TRAIN = DATA / "train"
names = sorted(p.stem for p in TRAIN.glob("*.geff"))
print("samples:", len(names), flush=True)

n_with_div = 0
div_counts = []
par_dau_um = []      # parent -> daughter displacement (um)
dau_dau_um = []      # daughter <-> daughter separation (um)
normal_um = []       # normal (out-degree 1) frame-to-frame displacement (um)
total_div = 0
total_edges = 0

for n in names:
    g = scoring.read_geff(TRAIN / f"{n}.geff")
    ids, t, pos, edges, scale = g["ids"], g["t"], g["pos"], g["edges"], g["scale"]
    sc = np.asarray(scale, dtype=np.float64)
    idx = {int(v): i for i, v in enumerate(ids)}
    out = {}
    for s, d in edges:
        si, di = idx.get(int(s)), idx.get(int(d))
        if si is None or di is None:
            continue
        if t[di] - t[si] != 1:
            continue
        out.setdefault(si, []).append(di)
    total_edges += sum(len(v) for v in out.values())
    divs = {s: ds for s, ds in out.items() if len(ds) >= 2}
    if divs:
        n_with_div += 1
    div_counts.append(len(divs))
    total_div += len(divs)
    for s, ds in out.items():
        p = pos[s] * sc
        if len(ds) == 1:
            normal_um.append(float(np.linalg.norm(pos[ds[0]] * sc - p)))
        else:
            d0, d1 = pos[ds[0]] * sc, pos[ds[1]] * sc
            par_dau_um.append(float(np.linalg.norm(d0 - p)))
            par_dau_um.append(float(np.linalg.norm(d1 - p)))
            dau_dau_um.append(float(np.linalg.norm(d0 - d1)))

div_counts = np.array(div_counts)
print(f"\\n=== DIVISION PREVALENCE ===", flush=True)
print(f"samples with >=1 division: {n_with_div}/{len(names)}", flush=True)
print(f"total divisions: {total_div}  (mean {div_counts.mean():.2f}/sample, max {div_counts.max()})", flush=True)
print(f"total dt=1 GT edges: {total_edges}  -> divisions are {100.0*total_div/max(total_edges,1):.3f}% of edges", flush=True)
print(f"division count histogram: {np.bincount(div_counts).tolist()}", flush=True)

def stats(name, a):
    a = np.asarray(a)
    if not len(a):
        print(f"  {name}: (none)", flush=True); return
    q = np.percentile(a, [1, 5, 25, 50, 75, 95, 99])
    print(f"  {name}: n={len(a)} mean={a.mean():.2f} "
          f"p1/p5/p25/p50/p75/p95/p99 = {q[0]:.2f}/{q[1]:.2f}/{q[2]:.2f}/{q[3]:.2f}/{q[4]:.2f}/{q[5]:.2f}/{q[6]:.2f}", flush=True)

print(f"\\n=== GEOMETRY (um) ===", flush=True)
stats("parent->daughter displacement", par_dau_um)
stats("daughter<->daughter separation", dau_dau_um)
stats("normal (out-deg 1) displacement", normal_um)

# Separability: if we see a cell whose 2 nearest next-frame candidates are both
# within R and mutually within S, how often is that actually a division?
print(f"\\n=== SEPARABILITY of the fork rule ===", flush=True)
nd = np.asarray(dau_dau_um); npd = np.asarray(par_dau_um); nn = np.asarray(normal_um)
if len(nd):
    for S in (6.0, 8.0, 10.0, 12.0, 15.0):
        frac = float(np.mean(nd <= S))
        print(f"  daughter-daughter <= {S:4.1f}um covers {frac*100:5.1f}% of real divisions", flush=True)
    for R in (5.0, 7.0, 9.0):
        fr = float(np.mean(npd <= R)); fn_ = float(np.mean(nn <= R))
        print(f"  parent->daughter <= {R:3.1f}um: {fr*100:5.1f}% of division legs "
              f"(vs {fn_*100:5.1f}% of normal links)", flush=True)
print(f"\\nIMPLICATION: divisions are ~{100.0*total_div/max(total_edges,1):.3f}% of edges, so emitting", flush=True)
print("a fork costs ~1 FP edge each while division_jaccard is worth up to +0.1 total.", flush=True)
print("Pick the daughter-daughter threshold that covers most real divisions, and cap", flush=True)
print("the number of forks per sample near the observed mean to control div_fp.", flush=True)
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
out = HERE / "divanalysis" / "biohub-div-analysis.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-div-analysis", "title": "biohub div analysis",
        "code_file": "biohub-div-analysis.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": False, "enable_tpu": False, "enable_internet": False,
        "keywords": [], "dataset_sources": ["eeshsaxena/biohub-zarr-wheels"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "divanalysis" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
