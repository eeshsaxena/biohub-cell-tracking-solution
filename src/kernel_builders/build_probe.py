"""Push a tiny kernel that reports the real on-Kaggle data layout."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

probe = r'''
import os
from pathlib import Path

root = Path("/kaggle/input")

# Walk to a bounded depth and print the directory skeleton, so we can see
# exactly where train/test/.zarr/.geff actually live.
def walk(d, depth, maxdepth=4, shown=[0]):
    if depth > maxdepth or shown[0] > 400:
        return
    try:
        items = sorted(d.iterdir())
    except Exception as e:
        print("  " * depth, d.name, "ERR", e); return
    ndir = sum(1 for x in items if x.is_dir())
    zc = sum(1 for x in items if x.name.endswith(".zarr"))
    gc = sum(1 for x in items if x.name.endswith(".geff"))
    tag = f"  [{len(items)} items, {ndir} dirs" + (f", {zc} .zarr" if zc else "") + (f", {gc} .geff" if gc else "") + "]"
    print("  " * depth + d.name + "/" + tag)
    shown[0] += 1
    # Descend, but if a dir has many .zarr/.geff, just show a couple examples.
    for x in items[:8]:
        if x.is_dir():
            walk(x, depth + 1, maxdepth, shown)

print("=== skeleton of /kaggle/input (depth<=4) ===")
walk(root, 0)

# Try to locate any train/test dir and any zarr anywhere.
print("\n=== searching for train/test dirs and .zarr/.geff ===")
found = 0
for dp, dns, fns in os.walk(root):
    base = os.path.basename(dp)
    if base in ("train", "test"):
        p = Path(dp)
        zc = len(list(p.glob("*.zarr"))); gc = len(list(p.glob("*.geff")))
        print(f"  {dp}  (*.zarr={zc}, *.geff={gc})")
        for it in sorted(p.iterdir())[:4]:
            print("       e.g.", it.name)
        found += 1
    if found > 6:
        break
'''

nb = {
    "cells": [{"cell_type": "code", "execution_count": None, "metadata": {},
               "outputs": [], "source": probe.splitlines(keepends=True)}],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                "name": "python3"},
                 "language_info": {"name": "python", "version": "3.11"}},
    "nbformat": 4, "nbformat_minor": 5,
}
compile(probe, "<probe>", "exec")
print("probe compiles")

out = HERE / "probe" / "biohub-probe-data.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {
    "id": "eeshsaxena/biohub-probe-data",
    "title": "biohub probe data",
    "code_file": "biohub-probe-data.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": False, "enable_tpu": False,
    "enable_internet": False,
    "keywords": [], "dataset_sources": [], "kernel_sources": [],
    "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
json.dump(meta, open(HERE / "probe" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
