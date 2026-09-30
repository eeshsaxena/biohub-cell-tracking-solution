"""Build an hfusion variant whose SECONDARY model is a fine-tuned checkpoint.

hfusion finds its secondary by scanning /kaggle/input for an ARTIFACT_MANIFEST.json whose
model.weight_sha256 equals one hard-coded constant, so the swap is: a private dataset with
the new weights + manifest, and that constant patched. Nothing else in the kernel changes.

usage: python build_secswap.py <tag> <edge_predictor.pth> <config.json>
  -> datasets/secswap_<tag>/   upload: kaggle datasets create -p datasets/secswap_<tag> --dir-mode zip
  -> v_<tag>/                  kernel eeshsaxena/biohub-v-<tag>, adds dataset eeshsaxena/biohub-sec-<tag>
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD_SHA = "9bac2fa0dadc4a6fc1899e0caf187f4b553e0a7cd90ba1261a68b35ffe9e305f"
ANCHOR = f'_secondary_expected_sha256 = "{OLD_SHA}"'

tag, pth, cfg = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
sha = hashlib.sha256(pth.read_bytes()).hexdigest()
if sha == OLD_SHA:
    sys.exit("checkpoint is byte-identical to the public secondary; nothing to swap")
slug = f"biohub-sec-{tag}"

ds = HERE / "datasets" / f"secswap_{tag}"
w = ds / "weights" / "unet_transformer" / "split_0"
if ds.exists():
    shutil.rmtree(ds)
w.mkdir(parents=True)
shutil.copy2(pth, w / "edge_predictor_best.pth")
shutil.copy2(cfg, w / "config.json")
(ds / "ARTIFACT_MANIFEST.json").write_text(json.dumps(
    {"model": {"weight_sha256": sha, "fine_tuned_from": OLD_SHA, "tag": tag}}, indent=2))
(ds / "dataset-metadata.json").write_text(json.dumps(
    {"title": slug, "id": f"eeshsaxena/{slug}", "licenses": [{"name": "CC0-1.0"}]}, indent=2))

kdir = HERE / f"v_{tag}"
if kdir.exists():
    shutil.rmtree(kdir)
kdir.mkdir()
nb = json.loads((HERE / "v_hfusion" / "kernel.ipynb").read_text(encoding="utf-8"))
hits = 0
for cell in nb["cells"]:
    src = "".join(cell["source"])
    if ANCHOR in src:
        hits += src.count(ANCHOR)
        src = src.replace(ANCHOR, f'_secondary_expected_sha256 = "{sha}"  # SECSWAP {tag}')
        cell["source"] = src.splitlines(keepends=True)
    for line in src.splitlines():
        if "secondary_manifest_info" in line and "=" not in line.split("secondary_manifest_info")[0][-3:]:
            print("  manifest use:", line.strip()[:150])
if hits != 1:
    sys.exit(f"expected exactly 1 sha anchor, found {hits}")
(kdir / "kernel.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")

meta = json.loads((HERE / "v_hfusion" / "kernel-metadata.json").read_text())
meta["id"] = f"eeshsaxena/biohub-v-{tag}"
meta["title"] = f"biohub v {tag}"
meta["dataset_sources"] = meta["dataset_sources"] + [f"eeshsaxena/{slug}"]
(kdir / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
print("sha256 ", sha)
print("dataset", ds)
print("kernel ", kdir)
