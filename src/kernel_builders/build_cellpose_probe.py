"""Cellpose COMPUTE + SANITY dry-run kernel.

Before any submission: install cellpose offline, load the nuclei model, and time
detection on a few real test frames across modes/downsample. Reports per-frame
seconds, mean cells/frame, and the projected 150-sample hours so we know whether
Cellpose fits the 12 h cap — and roughly whether its cell count is sane.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def strip_pipeline_import(src: str) -> str:
    out = []
    for ln in src.splitlines(keepends=True):
        if ln.strip().startswith("from pipeline import"):
            out.append("# " + ln)  # names live in the shared notebook namespace
        else:
            out.append(ln)
    return "".join(out)


PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split(
    'if __name__ == "__main__":')[0]
CPDET = strip_pipeline_import((ROOT / "kaggle" / "cellpose_detect.py").read_text(encoding="utf-8"))

INSTALL = '''
import os, glob, subprocess, sys

def find_wheeldir(slug):
    # Datasets mount at /kaggle/input/datasets/<user>/<slug> when attached via API.
    for base in (f"/kaggle/input/{slug}",
                 f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(base):
            return base
    hits = [p for p in glob.glob(f"/kaggle/input/**/{slug}", recursive=True) if os.path.isdir(p)]
    return hits[0] if hits else None

for name, slug in [("zarr", "biohub-zarr-wheels"), ("cellpose", "biohub-cellpose")]:
    wd = find_wheeldir(slug)
    print(name, "wheeldir ->", wd)
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-index",
                        f"--find-links={wd}", name], capture_output=True, text=True)
    print(name, "install rc", r.returncode)
    if r.returncode:
        print(r.stdout[-1500:]); print(r.stderr[-1500:])

CELLPOSE_WEIGHTS = os.path.join(find_wheeldir("biohub-cellpose") or "", "nucleitorch_0")
import zarr, cellpose
print("zarr", zarr.__version__, "| cellpose", cellpose.version, "| weights:", CELLPOSE_WEIGHTS)
'''

RESOLVER = '''
from pathlib import Path
def find_data_root():
    slug = "biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"), Path(f"/kaggle/input/{slug}")):
        if (c / "test").exists() or (c / "train").exists():
            return c
    for p in Path("/kaggle/input").rglob("test"):
        if p.is_dir() and any(p.glob("*.zarr")):
            return p.parent
    raise RuntimeError("data root not found")
DATA = find_data_root()
print("data root:", DATA)
'''

DRIVER = '''
import time, numpy as np
from cellpose import models

model = models.CellposeModel(gpu=True, pretrained_model=CELLPOSE_WEIGHTS)
print("model loaded; gpu:", model.gpu)

class CFG:
    cp_diameter_um = 16.0
    cp_flow_threshold = 0.4
    cp_cellprob_threshold = 0.0
    cp_stitch = 0.3
    motion_compensate = False

test = sorted((DATA / "test").glob("*.zarr"))
print("visible test samples:", [p.stem for p in test])
zp = test[0]
read, T, scale, _q = open_volume(zp)
print("sample", zp.stem, "T", T, "scale", scale)

# Warm up the model once (first eval compiles/loads and is not representative).
_ = detect_frame_cellpose(read(0), model, CFG(), scale)

for mode, ds in [("stitch", 1), ("stitch", 2), ("do_3d", 2), ("do_3d", 1)]:
    cfg = CFG(); cfg.cp_mode = mode; cfg.cp_downsample_xy = ds
    t0 = time.time(); tot = 0
    for t in range(3):
        c = detect_frame_cellpose(read(t), model, cfg, scale); tot += len(c)
    per = (time.time() - t0) / 3
    print(f"  mode={mode:6} ds={ds}  {per:5.2f}s/frame  ~{tot/3:5.0f} cells  "
          f"-> {per*100/60:4.1f} min/sample, {per*100*150/3600:4.1f} h for 150 samples")
print("DONE")
'''

cells = [
    {"cell_type": "code", "source": INSTALL.splitlines(keepends=True)},
    {"cell_type": "code", "source": ("# pipeline\n" + PIPELINE).splitlines(keepends=True)},
    {"cell_type": "code", "source": ("# cellpose_detect\n" + CPDET).splitlines(keepends=True)},
    {"cell_type": "code", "source": RESOLVER.splitlines(keepends=True)},
    {"cell_type": "code", "source": DRIVER.splitlines(keepends=True)},
]
for c in cells:
    c.update(execution_count=None, metadata={}, outputs=[])
    compile("".join(c["source"]), "<c>", "exec")
print("all cells compile")

nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "cpprobe" / "biohub-cellpose-probe.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-cellpose-probe", "title": "biohub cellpose probe",
        "code_file": "biohub-cellpose-probe.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels", "eeshsaxena/biohub-cellpose"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "cpprobe" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
