"""Build a kernel that tests the REAL Kunal 3-UNet detector on Zebrahub crops.

The last compatibility unknown: does the competition-trained detector (recall 0.978 on the
competition test) find Zebrahub nuclei? DoG proxy gave 0.52 locally, but DoG is weak. This
runs the actual UNet detector on the uploaded Zebrahub crops and reports recall vs the crop
tracks at the 7um competition gate. GATE: recall > 0.6 on both embryos => detector transfers,
Phase 2 is fully de-risked. Costs GPU time, NOT a submission slot.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
OUT_DIR = HERE / "zebra_dettest"
OUT_DIR.mkdir(exist_ok=True)
src = json.loads(SRC_NB.read_text(encoding="utf-8"))
base_cells = [src["cells"][i] for i in (0, 1, 2, 3)]           # setup + helpers + linker + detect

INSTALL = r'''
import os, glob, subprocess, sys
def find_wheeldir(slug):
    for base in (f"/kaggle/input/{slug}", f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(base):
            return base
    hits = [p for p in glob.glob(f"/kaggle/input/**/{slug}", recursive=True) if os.path.isdir(p)]
    return hits[0] if hits else None
wd = find_wheeldir("biohub-zarr-wheels")
r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-index",
                    f"--find-links={wd}", "zarr"], capture_output=True, text=True)
print("zarr install rc", r.returncode)
import zarr; print("zarr", zarr.__version__)
'''
install_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": INSTALL}
base_cells = [install_cell] + base_cells

TEST = r'''
# ============ REAL UNet detector recall on Zebrahub crops ============
import numpy as np, glob, gc, zarr
from pathlib import Path
from scipy.optimize import linear_sum_assignment
UNET_THR = 0.15

def read_geff_min(path):
    g = zarr.open_group(str(path), mode="r")
    ids = np.asarray(g["nodes/ids"][:]).astype(np.int64)
    t = np.asarray(g["nodes/props/t/values"][:]).astype(np.int64)
    z = np.asarray(g["nodes/props/z/values"][:]).astype(np.float64)
    y = np.asarray(g["nodes/props/y/values"][:]).astype(np.float64)
    x = np.asarray(g["nodes/props/x/values"][:]).astype(np.float64)
    return {"ids": ids, "t": t, "pos": np.stack([z, y, x], 1)}

def recall_frame(det_xyz, gt_xyz, maxd=7.0):
    if len(det_xyz) == 0 or len(gt_xyz) == 0:
        return 0, len(gt_xyz)
    D = np.linalg.norm((gt_xyz[:, None] * SCALE) - (det_xyz[None] * SCALE), axis=2)
    cost = np.where(D <= maxd, D, 1e6)
    ri, ci = linear_sum_assignment(cost)
    tp = int(sum(cost[a, b] < 5e5 for a, b in zip(ri, ci)))
    return tp, len(gt_xyz)

import zipfile
ZDIRS = [d for d in glob.glob("/kaggle/input/*zebra*") if Path(d).is_dir()]
# Kaggle stores directory uploads as per-dir .zip; extract them (each zip = one .geff/.zarr dir tree)
EXT = "/kaggle/working/zebra_ext"; os.makedirs(EXT, exist_ok=True)
for zd in ZDIRS:
    for zf in glob.glob(os.path.join(zd, "**", "*.zip"), recursive=True):
        dst = os.path.join(EXT, Path(zf).name[:-4])          # strip .zip -> e.g. X.geff / X.zarr
        if not os.path.exists(dst):
            try: zipfile.ZipFile(zf).extractall(dst)
            except Exception as e: print("unzip fail", zf, str(e)[:80])
SEARCH = ZDIRS + [EXT]
def _resolve(gp):
    # the geff dir may be dst itself or dst/<name> depending on how the zip was rooted
    for cand in (gp, gp / gp.name):
        if (cand / "nodes").exists() or (cand / "nodes.zarr").exists() or list(cand.glob("nodes*")):
            return cand
    return gp
crops = []
seen = set()
for zd in SEARCH:
    for gp in sorted(Path(zd).rglob("*.geff")):
        stem = gp.name[:-5]
        if stem in seen: continue
        # find the matching .zarr (sibling in original dir, or extracted)
        cand_zarr = [Path(zd).joinpath(*gp.relative_to(zd).parts).with_suffix(".zarr")]
        cand_zarr += [Path(EXT) / (stem + ".zarr")]
        zp = next((z for z in cand_zarr if z.exists()), None)
        if zp is None: continue
        g_use = _resolve(gp); z_use = zp / (stem + ".zarr") if (zp / (stem + ".zarr")).exists() else zp
        crops.append((stem.split("_c")[0], g_use, z_use)); seen.add(stem)
print("found", len(crops), "zebra crops; SEARCH", SEARCH, flush=True)

by = {}
for emb, gp, zp in crops:
    gt = read_geff_min(gp)
    img = zarr.open_group(str(zp), mode="r")["img"]
    T = int(img.shape[0])
    tp = fn = 0
    for t in range(T):
        gmask = gt["t"] == t
        if gmask.sum() == 0:
            continue
        vol = np.asarray(img[t]).astype(np.float32)
        c, s = detect(vol)
        c = np.asarray(c, np.float32).reshape(-1, 3); s = np.asarray(s, np.float32).reshape(-1)
        seeds = c[s >= UNET_THR]
        a, b = recall_frame(seeds, gt["pos"][gmask])
        tp += a; fn += (b - a)
        gc.collect()
    rec = tp / max(1, tp + fn)
    by.setdefault(emb, []).append(rec)
    print("  %s %s: recall=%.3f (tp=%d fn=%d)" % (emb, gp.stem, rec, tp, fn), flush=True)

print("\n================ REAL UNet DETECTOR RECALL on Zebrahub ================")
allrec = []
for emb in sorted(by):
    r = float(np.mean(by[emb])); allrec.append(r)
    print("  %-14s recall %.3f  (competition detector gets 0.978 on competition test)" % (emb, r))
ok = len(allrec) > 0 and min(allrec) > 0.60
print("\n  GATE (recall > 0.60 on every embryo): %s" % ("PASS -> detector transfers, Phase 2 de-risked"
                                                        if ok else "FAIL -> detector needs Zebrahub fine-tuning"))
'''
test_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": TEST}
nb = dict(src); nb["cells"] = base_cells + [test_cell]
nb_path = OUT_DIR / "biohub-zebra-dettest.ipynb"
nb_path.write_text(json.dumps(nb), encoding="utf-8")
meta = {
    "id": "eeshsaxena/biohub-zebra-dettest",
    "title": "Biohub zebra dettest",
    "code_file": "biohub-zebra-dettest.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": False, "enable_tpu": False, "enable_internet": False,
    "keywords": [],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models",
                        "eeshsaxena/biohub-zarr-wheels", "eeshsaxena/biohub-zebrahub-crops"],
    "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path, "| cells", len(nb["cells"]))
