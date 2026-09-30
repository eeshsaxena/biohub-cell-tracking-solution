"""SUBMIT kernel for the trained U-Net detector.

Reuses the ENTIRE downstream pipeline (linking / gap recovery / graph
constraints / submission CSV + format checks) unchanged by monkeypatching only
the detection step: rebind the global `detect_sample` to the U-Net version before
calling main(). process_sample() looks up `detect_sample` by name at call time,
so the whole test run flows through the trained detector.

Requires a Kaggle dataset `eeshsaxena/biohub-detector` holding detector.pt +
detector.json (produced by biohub-detector-train). Attach it + zarr-wheels.
Only push this AFTER the training kernel's held-out recall beats DoG's 0.65.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def strip_local_imports(src):
    out = []
    for ln in src.splitlines(keepends=True):
        s = ln.strip()
        drop = (s == "import scoring" or s.startswith("from pipeline import")
                or s.startswith("import detector"))
        out.append(("# " + ln) if drop else ln)
    return "".join(out)


SCORING = (ROOT / "kaggle" / "scoring.py").read_text(encoding="utf-8")
PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]
DETECTOR = strip_local_imports((ROOT / "kaggle" / "detector.py").read_text(encoding="utf-8"))
SHIM = '\nimport types as _t\nscoring = _t.SimpleNamespace(**{k: v for k, v in list(globals().items()) if not k.startswith("_")})\n'

OFFLINE_ZARR = '''
import os, glob, subprocess, sys
print("INPUT MOUNTS:", os.listdir("/kaggle/input"))
_whls = glob.glob("/kaggle/input/**/zarr-*.whl", recursive=True)
wd = os.path.dirname(_whls[0]) if _whls else "/kaggle/input/biohub-zarr-wheels"
r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-index",
                    f"--find-links={wd}", "zarr"], capture_output=True, text=True)
print("zarr pip rc:", r.returncode, flush=True)
import zarr, torch
print("zarr", zarr.__version__, "| torch", torch.__version__,
      "| cuda", torch.cuda.is_available(), flush=True)
'''

DRIVER = '''
from pathlib import Path
import numpy as np, dataclasses, torch, json, glob

def find_data_root():
    slug = "biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"), Path(f"/kaggle/input/{slug}")):
        if (c / "test").exists() or (c / "train").exists():
            return c
    for p in Path("/kaggle/input").rglob("test"):
        if p.is_dir() and any(p.glob("*.zarr")):
            return p.parent
    raise RuntimeError("no data root")
DATA = find_data_root()
print("data root:", DATA, flush=True)

# ---- locate the trained detector (dataset biohub-detector) ----
def find_file(name):
    hits = glob.glob(f"/kaggle/input/**/{name}", recursive=True)
    if not hits:
        raise RuntimeError(f"{name} not found under /kaggle/input")
    return hits[0]
WEIGHTS = find_file("detector.pt")
DCFG = json.load(open(find_file("detector.json")))
print("detector config:", DCFG, flush=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_MODEL = build_unet(base=DCFG["base"], depth=DCFG["depth"]).to(device)
_MODEL.load_state_dict(torch.load(WEIGHTS, map_location=device))
_MODEL.eval()
print("loaded U-Net detector on", device, flush=True)

# ---- monkeypatch detection: rebind the global `detect_sample` ----
def detect_sample(zarr_path, cfg):  # noqa: F811  (overrides pipeline's global)
    return detect_sample_unet(zarr_path, cfg, _MODEL, device=device)

# --- ship overrides (set here, NOT in the dataset, so a pending submission that
# reuses biohub-detector is never disturbed). ---
# v4: v3 (uncapped, thr0.10) scored LB 0.682 << DoG 0.825 -- over-detection (up to
# 645 nodes/frame) triggered the node-ratio penalty on unseen embryos. v4 adds a
# per-frame COUNT CAP (~DoG density) to kill that penalty, keeps thr0.05 for recall,
# and uses the link-sweep winner (radius7, gap1).
SHIP_THR = 0.05
SHIP_MAX_PER_FRAME = 280   # count-calibrate to ~DoG density (ratio ~0); 0 = uncapped
SHIP_LINK_RADIUS = 7.0
SHIP_MAX_GAP = 1
SHIP_GAP_RADIUS = 9.0

best = Config(
    mode="submit",
    data_root=DATA,
    out_csv=Path("/kaggle/working/submission.csv"),
    device="cuda",
    min_sep_um=float(DCFG.get("min_sep_um", 4.5)),
    max_gap=SHIP_MAX_GAP,
    link_radius_um=SHIP_LINK_RADIUS,
    gap_radius_um=SHIP_GAP_RADIUS,
    motion_compensate=True,
    detect_divisions=False,
    time_budget_s=10.5 * 3600,
    verbose=True,
)
# U-Net inference knobs (read via getattr inside detect_frame_unet)
best.unet_peak_thresh = SHIP_THR
best.unet_max_per_frame = SHIP_MAX_PER_FRAME
best.unet_z_tile = int(DCFG.get("unet_z_tile", 64))
best.unet_z_overlap = int(DCFG.get("unet_z_overlap", 0))
print(f"SHIP config: thr={SHIP_THR} max_per_frame={SHIP_MAX_PER_FRAME} "
      f"link_radius={SHIP_LINK_RADIUS} max_gap={SHIP_MAX_GAP} gap_radius={SHIP_GAP_RADIUS}", flush=True)

main(best)
'''

SUBMIT_CHECK = '''
import pandas as pd
sub = pd.read_csv("/kaggle/working/submission.csv")
print(sub.shape, "|", dict(sub.row_type.value_counts()), "| datasets:", sub.dataset.nunique(), flush=True)
test_dirs = {p.stem for p in (DATA / "test").glob("*.zarr")}
missing = test_dirs - set(sub.dataset.unique())
assert not missing, f"missing datasets: {missing}"
nodes = sub[sub.row_type == "node"]; edges = sub[sub.row_type == "edge"]
assert list(sub.id) == list(range(len(sub))), "id column must be consecutive"
for ds, g in nodes.groupby("dataset"):
    t_of = dict(zip(g.node_id, g.t))
    e = edges[edges.dataset == ds]
    if len(e) == 0:
        print(f"  WARNING {ds}: no edges, scores 0"); continue
    spans = {t_of[a] - t_of[b] for a, b in zip(e.target_id, e.source_id)}
    assert spans <= {1}, f"{ds}: edges spanning {sorted(spans)} DISCARDED"
    assert e.target_id.duplicated().sum() == 0, f"{ds}: in-degree > 1"
    assert e.source_id.value_counts().max() <= 2, f"{ds}: out-degree > 2"
print("\\nall submission checks passed", flush=True)
'''

cells = [OFFLINE_ZARR, "# scoring\n" + SCORING + SHIM, "# pipeline\n" + PIPELINE,
         "# detector\n" + DETECTOR, DRIVER, SUBMIT_CHECK]
nb_cells = []
for src in cells:
    compile(src, "<c>", "exec")
    nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                     "source": src.splitlines(keepends=True)})
print("all cells compile")
nb = {"cells": nb_cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}}, "nbformat": 4, "nbformat_minor": 5}
out = HERE / "detsubmit" / "biohub-detector-submit.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-detector-submit", "title": "biohub detector submit",
        "code_file": "biohub-detector-submit.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels", "eeshsaxena/biohub-detector"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "detsubmit" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
