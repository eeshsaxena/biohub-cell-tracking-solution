"""Create three exact, offline Kaggle forks of high-scoring public notebooks."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE / "research"

SPECS = [
    {
        "tag": "win-kunal917-exact",
        "source_dir": "biohub-kunal-0917-exact-repro",
        "source_file": "biohub-kunal-0917-exact-repro.ipynb",
        "title": "Biohub win Kunal 0917 exact repro",
        "datasets": [
            "xiaoleilian/biohub-unet3d-weights",
            "xiaoleilian/biohub-unet3d-weights-v2models",
        ],
    },
    {
        "tag": "win-two-seed912-exact",
        "source_dir": "two-seeds",
        "source_file": "biohub-cell-tracking-two-seeds-logit-blend.ipynb",
        "title": "Biohub win two-seed DeepCenter blend",
        "datasets": [
            "pilkwang/biohub-deepcenter-unet3d-center-prior-v1",
            "pilkwang/biohub-temporal-unet3d-seed314159-v1",
            "pilkwang/biohub-tracking-support-pack-50ep-v1",
            "pilkwang/pilkwang-public-dataset-for-notebooks-figures",
        ],
    },
    {
        "tag": "win-masterpiece-v16-exact",
        "source_dir": "biohub-masterpiece-tracker-version-16",
        "source_file": "biohub-masterpiece-tracker-version-16.ipynb",
        "title": "Biohub win masterpiece tracker v16 exact",
        "datasets": [
            "pilkwang/biohub-deepcenter-unet3d-center-prior-v1",
            "pilkwang/biohub-local-association-ranker-unet300-v1",
            "pilkwang/biohub-temporal-unet3d-seed314159-v1",
            "pilkwang/biohub-tracking-support-pack-50ep-v1",
        ],
    },
]


def build(spec: dict[str, object]) -> None:
    tag = str(spec["tag"])
    source = RESEARCH / str(spec["source_dir"]) / str(spec["source_file"])
    notebook = json.loads(source.read_text(encoding="utf-8"))
    assert notebook.get("nbformat") == 4, f"invalid notebook: {source}"

    # The original Kunal repro checks its schema but does not fail if a visible
    # test movie was skipped.  This guard is deliberately post-export: it
    # changes neither detector nor linker outputs, but turns a partial CSV into
    # a failed kernel rather than a costly leaderboard submission.
    if tag == "win-kunal917-exact":
        notebook["cells"].append({
            "cell_type": "code",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": [
                "# Submission integrity gate (post-export; does not alter predictions)\n",
                "expected_datasets = {p.name.replace('.zarr', '') for p in TEST_DIR.glob('*.zarr')}\n",
                "written_datasets = set(sub.loc[sub.row_type == 'node', 'dataset'].unique())\n",
                "missing_datasets = expected_datasets - written_datasets\n",
                "assert not missing_datasets, f'missing output for test datasets: {sorted(missing_datasets)}'\n",
                "node_t = {(r.dataset, r.node_id): r.t for r in sub.loc[sub.row_type == 'node'].itertuples()}\n",
                "for edge in sub.loc[sub.row_type == 'edge'].itertuples():\n",
                "    source_key, target_key = (edge.dataset, edge.source_id), (edge.dataset, edge.target_id)\n",
                "    assert target_key in node_t and source_key in node_t, (edge.dataset, edge.source_id, edge.target_id)\n",
                "    assert node_t[target_key] == node_t[source_key] + 1, (edge.dataset, edge.source_id, edge.target_id)\n",
                "print('submission integrity PASS:', len(expected_datasets), 'datasets')\n",
            ],
        })

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
        "dataset_sources": spec["datasets"],
        "kernel_sources": [],
        "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": [],
    }
    (out_dir / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"built {out_dir.name} from {source.name}")


if __name__ == "__main__":
    for spec in SPECS:
        build(spec)
