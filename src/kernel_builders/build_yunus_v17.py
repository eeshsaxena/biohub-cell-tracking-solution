"""Build a clean private production fork of the public Yunus v17 lead.

The pulled public notebook contains optional local-validator cells that read
training graphs.  Those cells are deliberately omitted from the Kaggle
candidate; only production inference and the label-free submission audit are
retained.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE / "research" / "yunus-v17"
SOURCE_NOTEBOOK = SOURCE_DIR / "lb-0-920-biohub-cell-tracking-v17.ipynb"
OUT_DIR = HERE / "sub_next-yunus-v17"
CODE_FILE = "biohub-next-yunus-v17.ipynb"


def build() -> None:
    notebook = json.loads(SOURCE_NOTEBOOK.read_text(encoding="utf-8"))
    source_cells = notebook["cells"]

    # Keep the public description plus the production path (configuration,
    # dependency materialisation, inference, post-processing, and the final
    # label-free CSV/topology audit).  The public notebook's cells 8-9 are a
    # local train-graph validator and cell 10 only reports that validator.
    kept_indices = list(range(8))
    notebook["cells"] = [copy.deepcopy(source_cells[i]) for i in kept_indices]
    notebook.setdefault("metadata", {}).setdefault("kaggle", {})["isGpuEnabled"] = True

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / CODE_FILE).write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8"
    )

    metadata = {
        "id": "eeshsaxena/biohub-next-yunus-v17",
        "title": "Biohub next Yunus v17 harmonic association",
        "code_file": CODE_FILE,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4",
        "keywords": ["gpu", "cell-tracking"],
        "dataset_sources": [
            "pilkwang/biohub-deepcenter-unet3d-center-prior-v1",
            "pilkwang/biohub-temporal-unet3d-seed314159-v1",
            "pilkwang/biohub-tracking-support-pack-50ep-v1",
        ],
        "kernel_sources": [],
        "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": [],
    }
    (OUT_DIR / "kernel-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(f"built {OUT_DIR.name}: kept cells {kept_indices}; omitted validator cells 8-10")


if __name__ == "__main__":
    build()
