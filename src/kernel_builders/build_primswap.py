"""Build an hfusion variant whose PRIMARY detector is one of our own fine-tuned checkpoints.

Unlike the secondary (which hfusion finds by scanning manifests for one hard-coded sha256), the primary is
materialized from the support-pack artifact and then checksum-guarded. So we leave that guard intact, and
copy our weights over the materialized file immediately afterwards, printing the swap so the notebook's own
output says exactly what ran.

usage: python build_primswap.py <tag> <edge_predictor.pth> <config.json>
  -> datasets/primswap_<tag>/   upload: (cd into it) kaggle datasets create -p . --dir-mode zip
  -> v_<tag>/                   kernel eeshsaxena/biohub-v-<tag>, adds dataset eeshsaxena/biohub-prim-<tag>
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUARD_ANCHOR = """if _primary_actual_sha256 != _primary_expected_sha256:
    raise RuntimeError(
        "Materialized primary model checksum mismatch: "
        f"expected {_primary_expected_sha256}, got {_primary_actual_sha256}"
    )
"""

tag, pth, cfg = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
sha = hashlib.sha256(pth.read_bytes()).hexdigest()
slug = f"biohub-prim-{tag}"

ds = HERE / "datasets" / f"primswap_{tag}"
w = ds / "weights" / "unet_transformer" / "split_0"
if ds.exists():
    shutil.rmtree(ds)
w.mkdir(parents=True)
shutil.copy2(pth, w / "edge_predictor_best.pth")
shutil.copy2(cfg, w / "config.json")
(ds / "ARTIFACT_MANIFEST.json").write_text(json.dumps(
    {"model": {"weight_sha256": sha, "role": "primary_swap", "tag": tag}}, indent=2))
(ds / "dataset-metadata.json").write_text(json.dumps(
    {"title": slug, "id": f"eeshsaxena/{slug}", "licenses": [{"name": "CC0-1.0"}]}, indent=2))

swap = f'''
# --- PRIMARY SWAP ({tag}): our own fine-tuned detector replaces the support-pack primary ---
# The integrity guard above still verifies the ORIGINAL artifact; the swap happens after it and is printed,
# so the run's own log records which weights actually drove inference.
_primswap_expected = "{sha}"
_primswap_src = None
for _cand in sorted(Path("/kaggle/input").rglob("weights/unet_transformer/split_0/edge_predictor_best.pth")):
    if _integrity_sha256_file(_cand) == _primswap_expected:
        _primswap_src = _cand
        break
if _primswap_src is None:
    raise FileNotFoundError("primary-swap weights not found in /kaggle/input (sha256 " + _primswap_expected + ")")
shutil.copyfile(_primswap_src, _primary_materialized_path)
_primary_actual_sha256 = _integrity_sha256_file(_primary_materialized_path)
if _primary_actual_sha256 != _primswap_expected:
    raise RuntimeError("primary swap failed to take effect")
print("PRIMARY SWAPPED [{tag}]:", _primswap_src)
print("PRIMARY SWAPPED sha256:", _primary_actual_sha256, "(was", _primary_expected_sha256 + ")")
'''

kdir = HERE / f"v_{tag}"
if kdir.exists():
    shutil.rmtree(kdir)
kdir.mkdir()
nb = json.loads((HERE / "v_hfusion" / "kernel.ipynb").read_text(encoding="utf-8"))
hits = 0
for cell in nb["cells"]:
    src = "".join(cell["source"])
    if GUARD_ANCHOR in src:
        hits += src.count(GUARD_ANCHOR)
        src = src.replace(GUARD_ANCHOR, GUARD_ANCHOR + swap, 1)
        cell["source"] = src.splitlines(keepends=True)
if hits != 1:
    sys.exit(f"expected exactly 1 primary-guard anchor, found {hits}")
(kdir / "kernel.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")

meta = json.loads((HERE / "v_hfusion" / "kernel-metadata.json").read_text())
meta["id"] = f"eeshsaxena/biohub-v-{tag}"
meta["title"] = f"biohub v {tag}"
meta["dataset_sources"] = meta["dataset_sources"] + [f"eeshsaxena/{slug}"]
(kdir / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
print("sha256 ", sha)
print("dataset", ds)
print("kernel ", kdir)
