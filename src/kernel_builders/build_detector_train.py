"""Train the heatmap 3D U-Net detector on the 2 labelled embryos (Kaggle T4).

The real leaderboard lever: classical DoG caps ~0.65 recall, pretrained Cellpose
collapses on ~half the samples. A detector trained on THIS dataset's own nuclei
should beat both. This kernel:
  1. preloads a diverse working set of frames (both embryos, excl. the 4 CV
     samples) into RAM, normalised, with their GT centroids;
  2. trains the U-Net to regress Gaussian heatmaps;
  3. saves weights + config to /kaggle/working/detector.pt (+ .json);
  4. evaluates node recall on the SAME 4 CV samples cellpose used, so the number
     is directly comparable (DoG 0.65, Cellpose worst-embryo 0.44).

NOTE: held-out-SAMPLES eval (same embryos) is a first signal, not full LOEO.
If recall clearly beats 0.65 we ship a submit kernel, then do a proper
leave-one-embryo-out run.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def strip_local_imports(src):
    out = []
    for ln in src.splitlines(keepends=True):
        s = ln.strip()
        drop = (s == "import scoring" or s == "import detector as D"
                or s.startswith("from pipeline import") or s.startswith("import detector"))
        out.append(("# " + ln) if drop else ln)
    return "".join(out)


SCORING = (ROOT / "kaggle" / "scoring.py").read_text(encoding="utf-8")
PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]
DETECTOR = strip_local_imports((ROOT / "kaggle" / "detector.py").read_text(encoding="utf-8"))
SHIM = '\nimport types as _t\nscoring = _t.SimpleNamespace(**{k: v for k, v in list(globals().items()) if not k.startswith("_")})\n'

INSTALL = '''
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
print("zarr rc", r.returncode, flush=True)
import torch
print("torch", torch.__version__, "cuda", torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "-", flush=True)
'''

DRIVER = '''
from pathlib import Path
import numpy as np, time, json, torch

def find_data_root():
    slug = "biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"), Path(f"/kaggle/input/{slug}")):
        if (c / "train").exists():
            return c
    for p in Path("/kaggle/input").rglob("train"):
        if p.is_dir() and any(p.glob("*.zarr")):
            return p.parent
    raise RuntimeError("no data root")
DATA = find_data_root()
TRAIN = DATA / "train"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

rng = np.random.default_rng(0)
# GT-dense held-out CV (from biohub-gt-density; densest 2 per embryo). v1 used the
# 4 SPARSEST samples by accident -> noisy eval. Also train on GT-DENSE samples and
# the GT-DENSE FRAMES within them, so heatmap targets aren't near-empty.
CV = ["6bba_09961292", "6bba_bb9f20c3", "44b6_d29c9ab2", "44b6_3a861e03"]  # held out
ALL = sorted(p.stem for p in TRAIN.glob("*.geff"))
pool = [n for n in ALL if n not in CV]

# rank pool by total GT node count (read every geff once; ~30s, cheap vs training)
t0 = time.time()
geffs, counts = {}, {}
for n in pool:
    try:
        g = scoring.read_geff(TRAIN / f"{n}.geff")
    except Exception:
        continue
    geffs[n] = g
    counts[n] = len(g["t"])
print(f"ranked {len(counts)} samples by GT density in {time.time()-t0:.0f}s", flush=True)
by_emb = {}
for n in sorted(counts, key=lambda k: -counts[k]):
    by_emb.setdefault(n.split("_")[0], []).append(n)

N_PER_EMB = 18       # densest N samples per embryo (more coverage of nucleus appearance)
F_PER = 4            # GT-densest frames per sample
picks = []
for emb, names in by_emb.items():
    picks.extend(names[:N_PER_EMB])
print("training samples (densest per embryo):",
      {e: [n for n in picks if n.startswith(e)] for e in by_emb}, flush=True)

frames = []  # list of (frame_norm float32[Z,Y,X], pts_vox[N,3], scale)
t0 = time.time()
for n in picks:
    read, T, scale, _q = open_volume(TRAIN / f"{n}.zarr")
    g = geffs[n]
    tt = g["t"]
    if len(tt) == 0:
        continue
    tcount = np.bincount(tt, minlength=int(tt.max()) + 1)
    best_ts = [int(t) for t in np.argsort(-tcount)[:F_PER] if t < T]
    for t in best_ts:
        fr = normalize_frame(read(t))
        gi = np.nonzero(tt == t)[0]
        frames.append((fr.astype(np.float32), g["pos"][gi].astype(np.float32), scale))
print(f"preloaded {len(frames)} frames in {time.time()-t0:.0f}s "
      f"(RAM ~{sum(f[0].nbytes for f in frames)/1e9:.2f} GB)", flush=True)
mean_cells = np.mean([len(f[1]) for f in frames])
print(f"mean GT nuclei/frame in working set: {mean_cells:.0f}", flush=True)

def provider():
    return frames[rng.integers(len(frames))]

# ---- train ----
# v2 levers (CV showed recall ~= fraction of ALL cells detected; must detect MORE):
# lower peak thresh -> detect closer to the true ~240/frame; sharper sigma + smaller
# min_sep separate dense nuclei; trained on GT-dense data (above).
CFG = dict(steps=3500, patch=(24, 128, 128), sigma_um=2.5, base=32, depth=3,
           batch=4, lr=1.0e-3, unet_peak_thresh=0.10, min_sep_um=3.5,
           unet_z_tile=32, unet_z_overlap=8)
print("train config:", CFG, flush=True)
t0 = time.time()
model, hist = train_detector(
    provider, steps=CFG["steps"], patch=CFG["patch"], sigma_um=CFG["sigma_um"],
    base=CFG["base"], depth=CFG["depth"], batch=CFG["batch"], lr=CFG["lr"],
    device=device, log_every=250)
print(f"trained in {time.time()-t0:.0f}s; loss {hist[0][1]:.4f} -> {hist[-1][1]:.4f}", flush=True)
for s, l in hist:
    print(f"  step {s:5d}  loss {l:.4f}", flush=True)

torch.save(model.state_dict(), "/kaggle/working/detector.pt")
json.dump(CFG, open("/kaggle/working/detector.json", "w"))
print("saved detector.pt + detector.json", flush=True)

# ---- trustworthy eval: GT-dense CV, all frames, SWEEP low thresholds ----
# (heatmap computed ONCE per frame; peaks extracted at each threshold cheaply)
EVAL_FRAMES = 80
THRS = [0.05, 0.10, 0.20]
MINSEP = CFG["min_sep_um"]
print("\\n=== held-out recall (%d frames, GT-dense CV, thr sweep; vs DoG 0.65) ===" % EVAL_FRAMES, flush=True)
per_emb = {thr: {} for thr in THRS}
for n in CV:
    read, T, scale, _q = open_volume(TRAIN / f"{n}.zarr")
    gt = scoring.read_geff(TRAIN / f"{n}.geff")
    T = min(T, EVAL_FRAMES)
    hits = {thr: 0 for thr in THRS}; npred = {thr: 0 for thr in THRS}; tot = 0
    t0 = time.time()
    for t in range(T):
        gi = np.nonzero(gt["t"] == t)[0]
        if len(gi) == 0:
            continue
        hm = predict_heatmap(normalize_frame(read(t)), model, device,
                             z_tile=CFG["unet_z_tile"], z_overlap=CFG["unet_z_overlap"])
        tot += len(gi)
        for thr in THRS:
            coords, _ = peaks_from_heatmap(hm, scale, MINSEP, thr)
            npred[thr] += len(coords)
            if len(coords):
                m = scoring.match_nodes(np.full(len(coords), t), coords.astype(float),
                                        np.full(len(gi), t), gt["pos"][gi], scale, 7.0)
                hits[thr] += int(np.sum(m >= 0))
    line = f"  {n} (true~{tot//max(T,1)}/frame): "
    for thr in THRS:
        rec = hits[thr] / tot if tot else float("nan")
        per_emb[thr].setdefault(n.split("_")[0], []).append(rec)
        line += f" thr{thr}={rec:.3f}(~{npred[thr]//T}pf)"
    print(line + f"  {time.time()-t0:.0f}s", flush=True)
print("\\n=== worst-embryo recall by threshold (vs DoG 0.65) ===", flush=True)
best_thr, best_worst = None, -1
for thr in THRS:
    worst = min(np.mean(v) for v in per_emb[thr].values())
    means = {k: round(float(np.mean(v)), 3) for k, v in per_emb[thr].items()}
    print(f"  thr={thr}: per-embryo {means}  worst-embryo={worst:.3f}", flush=True)
    if worst > best_worst:
        best_worst, best_thr = worst, thr
print(f"BEST: thr={best_thr} worst-embryo={best_worst:.3f} (DoG 0.65)", flush=True)
# bake the winning threshold into the saved config for the submit kernel
CFG["unet_peak_thresh"] = float(best_thr)
json.dump(CFG, open("/kaggle/working/detector.json", "w"))
print("updated detector.json unet_peak_thresh ->", best_thr, flush=True)
'''

cells = [INSTALL, "# scoring\n" + SCORING + SHIM, "# pipeline\n" + PIPELINE,
         "# detector\n" + DETECTOR, DRIVER]
nb_cells = []
for src in cells:
    compile(src, "<c>", "exec")
    nb_cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                     "source": src.splitlines(keepends=True)})
print("all cells compile")
nb = {"cells": nb_cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.11"}}, "nbformat": 4, "nbformat_minor": 5}
out = HERE / "dettrain" / "biohub-detector-train.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)
meta = {"id": "eeshsaxena/biohub-detector-train", "title": "biohub detector train",
        "code_file": "biohub-detector-train.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
        "machine_shape": "NvidiaTeslaT4", "keywords": [],
        "dataset_sources": ["eeshsaxena/biohub-zarr-wheels"],
        "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
        "model_sources": []}
json.dump(meta, open(HERE / "dettrain" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
