"""Build a Yaroslav public-policy variant with the validated 300-epoch weights."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "external" / "yaroslav" / "biohub-cell-tracking-v4-unet-ilp-reproduction.ipynb"
tag = "yaroslav-policy-300"
weights_ds = "hongdaekim/biohub-300ep-checkpoint-pin-v1"

source_nb = json.loads(SRC.read_text(encoding="utf-8"))
code_cells = [c for c in source_nb["cells"] if c.get("cell_type") == "code"]
assert len(code_cells) >= 4, "unexpected public notebook layout"

env = """import os
os.environ["BIOHUB_TARGET_ARTIFACT_SLUG"] = "biohub-tracking-support-pack-50ep-v1"
os.environ["BIOHUB_DET_THRESHOLD"] = "0.985"
print("Using Yaroslav policy notebook + 300ep checkpoint", flush=True)
"""

swap = f'''\nimport glob, shutil\nfrom pathlib import Path\n_hits = [p for p in glob.glob("/kaggle/input/**/edge_predictor_best.pth", recursive=True) if "biohub-300ep-checkpoint-pin-v1" in p]\nassert _hits, "300ep checkpoint not found"\n_swapdir = Path("/kaggle/working/swap_weights")\n_swapdir.mkdir(parents=True, exist_ok=True)\n_dst = _swapdir / "edge_predictor_best.pth"\nshutil.copy(_hits[0], _dst)\nWEIGHTS_RELATIVE = str(_dst)\nprint("SWAPPED WEIGHTS <-", _hits[0], flush=True)\n'''

# Keep the public notebook's complete code path, dropping only its cover cell.
cells = [env] + ["".join(c["source"]) for c in code_cells[1:2]]
cells += ["".join(code_cells[2]["source"]), swap]
cells += ["".join(c["source"]) for c in code_cells[3:]]
for src in cells:
    compile(src, "<generated>", "exec")

out_dir = HERE / f"sub_{tag}"
out_dir.mkdir(parents=True, exist_ok=True)
nb = {
    "cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
               "source": src.splitlines(keepends=True)} for src in cells],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3.11"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}
(out_dir / f"biohub-{tag}.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
meta = {
    "id": f"eeshsaxena/biohub-{tag}",
    "title": f"biohub {tag}",
    "code_file": f"biohub-{tag}.ipynb",
    "language": "python",
    "kernel_type": "notebook",
    "is_private": True,
    "enable_gpu": True,
    "enable_tpu": False,
    "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4",
    "keywords": [],
    "dataset_sources": ["pilkwang/biohub-tracking-support-pack-50ep-v1", weights_ds],
    "kernel_sources": [],
    "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
(out_dir / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(f"built {out_dir} with {len(cells)} code cells")
