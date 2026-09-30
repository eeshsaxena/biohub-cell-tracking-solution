"""Assemble the DEEP sweep kernel: full grid, n_per_embryo=4, long budget.

This is just kaggle/biohub_tune.ipynb (offline zarr + resolver + wide grid) with
kernel metadata and a fresh id. Launch it after the lean tune validates that the
pipeline produces a sensible per-embryo number, to pick real parameters.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

nb = json.load(open(ROOT / "kaggle" / "biohub_tune.ipynb"))
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code":
        compile("".join(c["source"]), f"<cell {i}>", "exec")
print("deep tune notebook cells compile")

out_dir = HERE / "deep"
out_dir.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out_dir / "biohub-cell-tracking-deep.ipynb", "w"), indent=1)

meta = {
    "id": "eeshsaxena/biohub-cell-tracking-deep-sweep",
    "title": "Biohub Cell Tracking Deep Sweep",
    "code_file": "biohub-cell-tracking-deep.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False,
    "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4",
    "keywords": [],
    "dataset_sources": ["eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [],
    "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
json.dump(meta, open(out_dir / "kernel-metadata.json", "w"), indent=2)
print("wrote", out_dir)
