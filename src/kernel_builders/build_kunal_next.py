"""Build controlled Kunal-derived ablations for the next quota reset."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE_DIR = HERE / "sub_win-kunal917-exact"
BASE_NOTEBOOK = BASE_DIR / "biohub-win-kunal917-exact.ipynb"
WEIGHT_DATASETS = [
    "xiaoleilian/biohub-unet3d-weights",
    "xiaoleilian/biohub-unet3d-weights-v2models",
]

SPECS = [
    {
        "tag": "next-kunal-recall13",
        "title": "Biohub next Kunal recall threshold 0.13",
        "description": "Kunal 0917 detector with threshold 0.13",
        "replace": {
            "UNET_THRESH=0.15; NMS_UM=4.0": "UNET_THRESH=0.13; NMS_UM=4.0",
            "SHORT_MIN = 6": "SHORT_MIN = 5",
        },
    },
    {
        "tag": "next-kunal-recall10",
        "title": "Biohub next Kunal recall threshold 0.10",
        "description": "Kunal 0917 detector with threshold 0.10 and short-track recall",
        "replace": {
            "UNET_THRESH=0.15; NMS_UM=4.0": "UNET_THRESH=0.10; NMS_UM=4.0",
            "CAND_THR = 0.05": "CAND_THR = 0.03",
            "SHORT_MIN = 6": "SHORT_MIN = 4",
        },
    },
    {
        "tag": "next-kunal-nosim",
        "title": "Biohub next Kunal geometry linker",
        "description": "Kunal 0917 detector with geometry-only association cost",
        "replace": {
            "LINK_SIM_W = 2.0": "LINK_SIM_W = 0.0",
        },
    },
]


def build(spec: dict[str, object]) -> None:
    notebook = json.loads(BASE_NOTEBOOK.read_text(encoding="utf-8"))
    changed = []
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        for old, new in dict(spec["replace"]).items():
            if old in source:
                source = source.replace(old, new)
                changed.append((old, new))
        cell["source"] = source
    expected = len(dict(spec["replace"]))
    if len(changed) < expected:
        raise RuntimeError(f"{spec['tag']}: only changed {changed}, expected {expected}")

    tag = str(spec["tag"])
    out_dir = HERE / f"sub_{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = f"biohub-{tag}.ipynb"
    (out_dir / code_file).write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    metadata = {
        "id": f"eeshsaxena/biohub-{tag}",
        "title": str(spec["title"]),
        "code_file": code_file,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": True,
        "enable_tpu": False,
        "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4",
        "keywords": [],
        "dataset_sources": WEIGHT_DATASETS,
        "kernel_sources": [],
        "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": [],
    }
    (out_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"built {out_dir.name}: {changed}")


if __name__ == "__main__":
    for spec in SPECS:
        build(spec)
