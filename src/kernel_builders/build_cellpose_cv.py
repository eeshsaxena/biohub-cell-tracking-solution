"""Decisive test: does Cellpose detection actually beat DoG on the real metric?

Runs Cellpose detection on a few TRAIN samples (with GT), links + scores with the
validated scorer, and reports per-embryo adj_edge_jaccard + node_recall. Compare
to DoG's ~0.65 worst-embryo CV. If Cellpose doesn't clearly win, abandon it
(compute is already marginal at ~11.8 h). If it wins, then fight the compute.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def strip_local_imports(src: str) -> str:
    out = []
    for ln in src.splitlines(keepends=True):
        s = ln.strip()
        if s == "import scoring" or s.startswith("from pipeline import"):
            out.append("# " + ln)
        else:
            out.append(ln)
    return "".join(out)


SCORING = (ROOT / "kaggle" / "scoring.py").read_text(encoding="utf-8")
PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split(
    'if __name__ == "__main__":')[0]
CPDET = strip_local_imports((ROOT / "kaggle" / "cellpose_detect.py").read_text(encoding="utf-8"))

# scoring.py functions referenced as scoring.<name> in a shared namespace:
SCORING_SHIM = '''
import types as _t
scoring = _t.SimpleNamespace(**{k: v for k, v in list(globals().items()) if not k.startswith("_")})
'''

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
    print(name, "rc", r.returncode)
    if r.returncode: print(r.stderr[-800:])
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

cfg = Config(device="cuda", motion_compensate=True, max_gap=2,
             link_radius_um=7.0, gap_radius_um=9.0)
cfg.cp_mode = "do_3d"; cfg.cp_downsample_xy = 1; cfg.cp_diameter_um = 16.0
cfg.cp_flow_threshold = 0.4; cfg.cp_cellprob_threshold = 0.0

# 2 samples per embryo that have BOTH zarr and geff.
by = defaultdict(list)
for z in sorted((DATA / "train").glob("*.zarr")):
    if z.with_suffix(".geff").exists():
        by[z.stem.split("_")[0]].append(z)
samples = [p for e in sorted(by) for p in by[e][:2]]
print("scoring cellpose on:", [p.stem for p in samples])

rows = defaultdict(list)
for zp in samples:
    t0 = time.time()
    dets, shifts, scale = detect_sample_cellpose(zp, cfg, model)
    nodes, edges = assemble(dets, shifts, cfg, scale)
    gt = scoring.read_geff(zp.with_suffix(".geff"))
    arr = np.asarray(nodes, float)
    er = scoring.evaluate_edges(arr[:,0].astype(int), arr[:,1:4],
                                np.asarray(edges).reshape(-1,2), gt)
    row = scoring.per_sample(er, gt["n_total"])
    rows[zp.stem.split("_")[0]].append(row)
    print(f"  {zp.stem}: adj={row['adj_edge_jaccard']:.3f} recall={row['node_recall']:.3f} "
          f"nodes={er['num_pred_nodes']} ratio={row['total_node_ratio']:+.2f} {time.time()-t0:.0f}s", flush=True)

print("\\n=== Cellpose per-embryo (vs DoG worst-embryo 0.65) ===")
worst = 9
for e in sorted(rows):
    s = scoring.summarise(rows[e]); rec = np.mean([r["node_recall"] for r in rows[e]])
    print(f"  {e}: adj_edge={s['adj_edge_jaccard']:.4f} recall={rec:.3f}")
    worst = min(worst, s["adj_edge_jaccard"])
print(f"  worst-embryo adj_edge = {worst:.4f}  (DoG was 0.65)")
'''

cells = [
    {"source": INSTALL},
    {"source": "# scoring\n" + SCORING + SCORING_SHIM},
    {"source": "# pipeline\n" + PIPELINE},
    {"source": "# cellpose_detect\n" + CPDET},
    {"source": DRIVER},
]
nb_cells = []
for c in cells:
    src = c["source"]
    compile(src, "<c>", "exec")
    nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                     "outputs": [], "source": src.splitlines(keepends=True)})
print("all cells compile")

nb = {"cells": nb_cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "cpcv" / "biohub-cellpose-cv.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-cellpose-cv", "title": "biohub cellpose cv",
        "code_file": "biohub-cellpose-cv.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels", "eeshsaxena/biohub-cellpose"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "cpcv" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
