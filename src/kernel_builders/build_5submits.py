"""Code comps validate the canonical output name `submission.csv` per kernel
version, so the one-kernel-many-CSVs trick 400s. Instead: 5 separate kernels,
each producing submission.csv at one min_sep, pushed to run in parallel. Then
submit each with -v 1 -f submission.csv.
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

DRIVER_TMPL = '''
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
           device="cuda", min_sep_um={ms}, peak_min_frac=0.08, max_gap=2, link_radius_um=7.0,
           gap_radius_um=9.0, max_per_frame=3000, motion_compensate=True,
           detect_divisions=False, time_budget_s=10.5*3600, verbose=True)
main(cfg)
import pandas as pd
sub=pd.read_csv("/kaggle/working/submission.csv")
print("rows",len(sub),"datasets",sub.dataset.nunique())
'''

CONFIGS = [("s7p0", 7.0), ("s8p5", 8.5), ("s10p0", 10.0), ("s12p0", 12.0), ("s15p0", 15.0)]

for tag, ms in CONFIGS:
    driver = DRIVER_TMPL.format(slug="{slug}", ms=ms)
    cells = [INSTALL, "# pipeline\n" + PIPELINE, driver]
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
    out = subprocess.run(["kaggle", "kernels", "push", "-p", str(d)], capture_output=True, text=True)
    print(tag, "->", (out.stdout + out.stderr).strip().splitlines()[-1])
print("all 5 pushed")
