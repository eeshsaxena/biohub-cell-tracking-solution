"""Reproduce the public learned pack (pilkwang ~0.914) offline as our own kernel.

Runs pilkwang's proven UNet+transformer+ILP inference notebook VERBATIM (pulled
source), with the support pack + competition data attached and internet OFF. An
env-config cell prepended so we can smoke-test on a few samples first.

  build_learned_pack.py smoke   -> SLICE=:2 (validate offline install+run, ~min)
  build_learned_pack.py full    -> all test samples (submit this one)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC_NB = HERE / "_forum" / "biohub-cell-tracking-learned-graph-w-gap-recovery.ipynb"

mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
DET = sys.argv[2] if len(sys.argv) > 2 else "0.985"
SLICE = ":2" if mode == "smoke" else ""
TAG = "learned-smoke" if mode == "smoke" else f"learned-d{DET.replace('.','')}"

nb = json.load(open(SRC_NB, encoding="utf-8"))

# Prepend an env-config cell: force offline, T4-safe, optional slice, and the
# proven params (det threshold 0.985, ILP on). These are read by the notebook's
# os.environ.get(...) defaults.
config_src = f'''import os
os.environ["BIOHUB_SLICE"] = {SLICE!r}
os.environ["BIOHUB_ALLOW_PIP_INSTALL"] = "0"     # offline only, wheels from the pack
os.environ["BIOHUB_USE_ILP"] = "1"
os.environ["BIOHUB_DET_THRESHOLD"] = {DET!r}
print("config: SLICE={SLICE!r} offline-wheels ILP=on det={DET}", flush=True)
'''
config_cell = {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
               "source": config_src.splitlines(keepends=True)}

# keep code cells only (drop the cover-image markdown/figure cell 0 which needs an
# unattached figures dataset), prepend our config cell.
code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
# cell 0 is the cover-image loader; it self-skips if the figure is absent, keep it harmless
out_cells = [config_cell] + code_cells

new_nb = {"cells": out_cells,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python", "version": "3.12"}},
          "nbformat": 4, "nbformat_minor": 5}

d = HERE / f"sub_{TAG}"; d.mkdir(parents=True, exist_ok=True)
nb_path = d / f"biohub-{TAG}.ipynb"
json.dump(new_nb, open(nb_path, "w"), indent=1)

meta = {"id": f"eeshsaxena/biohub-{TAG}", "title": f"biohub {TAG}",
        "code_file": f"biohub-{TAG}.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["pilkwang/biohub-tracking-support-pack-50ep-v1"],
        "kernel_sources": [], "model_sources": [],
        "competition_sources": ["biohub-cell-tracking-during-development"]}
json.dump(meta, open(d / "kernel-metadata.json", "w"), indent=2)
print(f"built sub_{TAG} ({len(out_cells)} cells) SLICE={SLICE!r}")
print(f"push: python -m kaggle kernels push -p scratch_kernels/sub_{TAG}")
