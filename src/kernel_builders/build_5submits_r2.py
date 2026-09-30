"""Round-2 attack as 5 per-config kernels, each writing the canonical
submission.csv (the one-kernel-many-CSVs form 400s on code comps). Builds +
pushes sub_gap1div ... ; submit each later with -v1 -f submission.csv.
"""
import json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]

INSTALL = '''
import os, glob, subprocess, sys
def find_wheeldir(slug):
    for base in (f"/kaggle/input/{slug}", f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(base): return base
    h=[p for p in glob.glob(f"/kaggle/input/**/{slug}",recursive=True) if os.path.isdir(p)]
    return h[0] if h else None
subprocess.run([sys.executable,"-m","pip","install","-q","--no-index",
    f"--find-links={find_wheeldir('biohub-zarr-wheels')}","zarr"],check=True)
import zarr
'''

# Validated base (round-2): min_sep 6.5 optimum, gap1, divisions on.
BASE = dict(min_sep_um=6.5, peak_min_frac=0.08, max_gap=1, link_radius_um=7.0,
            gap_radius_um=9.0, max_per_frame=3000, motion_compensate=True, detect_divisions=True)
CONFIGS = {
    "gap1div":      {},                                   # offline favorite (pooled 0.8021)
    "gap1":         {"detect_divisions": False},          # isolates the divisions term
    "gap1divsub":   {"subvoxel": True},                   # sub-voxel peak refinement
    "gap1divpmf06": {"peak_min_frac": 0.06},              # denser peaks (ratio is negative)
    "gap1divfine":  {"sigmas_um": (1.5, 2.5, 3.5, 4.5)},  # finer DoG scales
}


def driver(merged):
    kw = ", ".join(f"{k}={v!r}" for k, v in merged.items())
    return f'''
from pathlib import Path
def find_data_root():
    slug="biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{{slug}}"),Path(f"/kaggle/input/{{slug}}")):
        if (c/"test").exists(): return c
    for p in Path("/kaggle/input").rglob("test"):
        if p.is_dir() and any(p.glob("*.zarr")): return p.parent
    raise RuntimeError("no data")
DATA=find_data_root()
cfg=Config(mode="submit", data_root=DATA, out_csv=Path("/kaggle/working/submission.csv"),
           device="cuda", time_budget_s=10.5*3600, verbose=True, {kw})
main(cfg)
import pandas as pd
sub=pd.read_csv("/kaggle/working/submission.csv")
print("rows",len(sub),"datasets",sub.dataset.nunique())
'''


for tag, over in CONFIGS.items():
    merged = {**BASE, **over}
    cells = [INSTALL, "# pipeline\n" + PIPELINE, driver(merged)]
    for src in cells:
        compile(src, "<c>", "exec")
    nb = {"cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                     "source": s.splitlines(keepends=True)} for s in cells],
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python", "version": "3.11"}}, "nbformat": 4, "nbformat_minor": 5}
    d = HERE / f"sub_{tag}"; d.mkdir(parents=True, exist_ok=True)
    json.dump(nb, open(d / f"biohub-sub-{tag}.ipynb", "w"), indent=1)
    meta = {"id": f"eeshsaxena/biohub-sub-{tag}", "title": f"biohub sub {tag}",
            "code_file": f"biohub-sub-{tag}.ipynb", "language": "python", "kernel_type": "notebook",
            "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
            "machine_shape": "NvidiaTeslaT4", "keywords": [],
            "dataset_sources": ["eeshsaxena/biohub-zarr-wheels"], "kernel_sources": [],
            "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": []}
    json.dump(meta, open(d / "kernel-metadata.json", "w"), indent=2)
    print(f"built sub_{tag}: {merged}")
print("all 5 round-2 kernel dirs built")
