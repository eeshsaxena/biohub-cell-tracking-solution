"""Build submit kernels for the remaining portfolio configs. Fill CONFIGS from
the edge-cv winners, run this, then push each dir and submit. Base = LB-0.837
round2 (gap1 + divisions). Each kernel runs full test detection+tracking and
writes the canonical submission.csv (verified by an in-notebook schema check).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]

BASE = dict(min_sep_um=6.5, peak_min_frac=0.08, max_gap=1, link_radius_um=7.0,
            gap_radius_um=9.0, max_per_frame=3000, motion_compensate=True,
            detect_divisions=True)

# edge-cv winners: two-pass tight=4 is the only positive edge lever (+0.0008 pooled,
# +worst-embryo, linking-only = safe). Denser + motion both regressed. div cap6 gave
# +0.003 on the LB (divtuned 0.840). Portfolio combines the two positive levers and
# isolates each on the LB for future signal.
DIV6 = dict(max_divisions_per_sample=6, division_max_leg_um=16.0, division_max_sep_um=18.0)
CONFIGS = {
    "tp4div6":  dict(link_tight_um=4.0, **DIV6),          # combined best (primary)
    "tp4":      dict(link_tight_um=4.0),                  # isolate two-pass on LB
    "div8":     dict(max_divisions_per_sample=8, division_max_leg_um=16.0, division_max_sep_um=18.0),
    "tp4div8":  dict(link_tight_um=4.0, max_divisions_per_sample=8, division_max_leg_um=16.0, division_max_sep_um=18.0),
}

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


def build(tag, over):
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
    print(f"built sub_{tag}: {over}")


if __name__ == "__main__":
    only = sys.argv[1:] or list(CONFIGS)
    for tag in only:
        build(tag, CONFIGS[tag])
    print("\nnext: push each dir, then submit -v1 -f submission.csv")
