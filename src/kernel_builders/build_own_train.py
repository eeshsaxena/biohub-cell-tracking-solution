"""PRIZE PATH: train OUR OWN detector+edge model with the organizers' open-source
training script, instead of shipping someone else's public checkpoint.

Why this is the real path:
  * public weights saturate at LB 0.894 (300ep best; 350ep 0.890 and a different
    seed 0.892 are both WORSE, and every downstream knob is flat) -- so there is
    nothing left to tune on borrowed weights;
  * forking public weights ties the pack and likely does not qualify for prize money.

Our previous own-trained detector failed (LB 0.682) because
`kaggle/detector.py:pos_weighted_mse` used DENSE MSE, penalising the net for firing
on the ~99% of real cells that are UNANNOTATED. The host script gets this right:
single-voxel weighted BCE with `--det-neg-weight 1e-2`, so a detection on an
unannotated real cell costs ~nothing and the net learns generic "cell-ness".

Epoch target: 300. Measured on the LB, 300ep (0.894) > 350ep (0.890), so the
generalisation peak is near 300 -- do NOT just train as long as possible.

Reuses the reference notebook's config + artifact-setup cells (repo + offline
wheels), then runs training and saves the checkpoint to /kaggle/working so it can
be published as a dataset and used for inference.

usage: build_own_train.py [tag] [EPOCHS=300] [KEY=VAL ...]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "_forum" / "biohub-cell-tracking-learned-graph-w-gap-recovery.ipynb"

tag = sys.argv[1] if len(sys.argv) > 1 else "owntrain"
kv = dict(a.split("=", 1) for a in sys.argv[2:])
EPOCHS = kv.pop("EPOCHS", "300")
NEG_W = kv.pop("NEG_WEIGHT", "1e-2")
MAX_H = kv.pop("MAX_HOURS", "10.5")
# The host default batch_size=16 OOMs a 14.6 GiB T4 at loss.backward().
BATCH = kv.pop("BATCH", "4")

nb = json.load(open(SRC, encoding="utf-8"))
code = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
# code[1] = config/imports, code[2] = artifact setup (repo + offline wheels)
setup = code[1:3]

TRAIN = f'''
import json, subprocess, sys, time, os, glob, shutil
from pathlib import Path

DATA = None
for c in ("/kaggle/input/competitions/biohub-cell-tracking-during-development",
          "/kaggle/input/biohub-cell-tracking-during-development"):
    if Path(c, "train").exists():
        DATA = Path(c); break
assert DATA, "train data not found"
TRAIN_DIR = DATA / "train"

# Train on every sample that has BOTH image and ground-truth graph.
stems = sorted(p.stem for p in TRAIN_DIR.glob("*.zarr")
               if (TRAIN_DIR / (p.stem + ".geff")).exists())
print("train samples:", len(stems), flush=True)

# Hold out the LAST sample of each embryo so the run reports an honest val number
# (2 embryos only, so this is a sanity check, not a generalisation estimate).
by = {{}}
for s in stems:
    by.setdefault(s.split("_")[0], []).append(s)
val = [v[-1] for v in by.values()]
tr = [s for s in stems if s not in val]
print("embryos:", {{k: len(v) for k, v in by.items()}}, "| train", len(tr), "val", val, flush=True)

splits = REPO_DIR / "own_splits.json"
splits.write_text(json.dumps([{{"split": 0, "train": tr, "test": val}}], indent=2))

OUT = Path("/kaggle/working/own_weights"); OUT.mkdir(parents=True, exist_ok=True)

cmd = [sys.executable, "scripts/train_unet_transformer.py",
       "--data-dir", str(TRAIN_DIR),
       "--splits", splits.name,
       "--split", "0",
       "--epochs", "{EPOCHS}",
       "--batch-size", "{BATCH}",
       "--num-workers", "2",
       "--det-neg-weight", "{NEG_W}",   # THE FIX: sparse supervision
       "--single-gpu"]
print(" ".join(cmd), flush=True)
# The repo is a src-layout package that is NOT pip-installed, so the training
# subprocess needs src/ on PYTHONPATH or it dies with ModuleNotFoundError.
env = dict(os.environ)
env["PYTHONPATH"] = str(REPO_DIR / "src") + os.pathsep + env.get("PYTHONPATH", "")

# The artifact setup SYMLINKS `weights/` from the read-only /kaggle/input mount, so
# training cannot write its checkpoints/config there (OSError 30). Materialise the
# tree as REAL writable files first (symlinks=False dereferences), then chmod.
_w = REPO_DIR / "weights"
if _w.is_symlink() or _w.exists():
    _real = _w.resolve()
    if _w.is_symlink():
        _w.unlink()
    else:
        shutil.rmtree(_w, ignore_errors=True)
    shutil.copytree(_real, _w, symlinks=False)
    for _root, _ds, _fs in os.walk(_w):
        os.chmod(_root, 0o755)
        for _fn in _fs:
            os.chmod(os.path.join(_root, _fn), 0o644)
    print("materialised writable weights tree at", _w, flush=True)

# Record the pack's pre-existing checkpoints (AFTER the copy, so mtimes are stable)
# so a training-produced file is never confused with a shipped one.
PRE = dict((p_, os.path.getmtime(p_)) for p_ in
           glob.glob(str(REPO_DIR / "weights" / "**" / "*.pth"), recursive=True))
print("pre-existing pack checkpoints:", len(PRE), flush=True)

t0 = time.time()
p = subprocess.run(cmd, cwd=str(REPO_DIR), capture_output=True, text=True, env=env)
print("rc", p.returncode, "in", (time.time()-t0)/3600, "h", flush=True)
print(p.stdout[-6000:], flush=True)
if p.returncode != 0:
    print("STDERR:", p.stderr[-6000:], flush=True)

# Collect ONLY checkpoints this run created or modified -- a plain glob would also
# pick up the pack's shipped weights and we would publish someone else's model.
found = glob.glob(str(REPO_DIR / "weights" / "**" / "*.pth"), recursive=True)
found += glob.glob("/kaggle/working/**/*.pth", recursive=True)
found = [f for f in found if "swap_weights" not in f and "own_weights" not in f]
print("checkpoints (OURS = new or modified during this run):", flush=True)
for f in sorted(set(found)):
    sz = os.path.getsize(f)
    ours = (f not in PRE) or (os.path.getmtime(f) > PRE[f])
    print("   " + ("OURS " if ours else "pack ") + f + " " + str(sz), flush=True)
    if ours and sz > 1e6:
        try:
            shutil.copy(f, OUT / Path(f).name)
        except Exception as e:
            print("   copy failed", e, flush=True)
print("saved to", OUT, os.listdir(OUT), flush=True)
if not os.listdir(OUT):
    print("WARNING: training produced NO checkpoint of our own", flush=True)
'''

cells = setup + [TRAIN]
for s in cells:
    compile(s, "<c>", "exec")

nb_out = {
    "cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
               "source": s.splitlines(keepends=True)} for s in cells],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3.11"}},
    "nbformat": 4, "nbformat_minor": 5,
}
d = HERE / f"train_{tag}"
d.mkdir(parents=True, exist_ok=True)
json.dump(nb_out, open(d / f"biohub-{tag}.ipynb", "w", encoding="utf-8"), indent=1)
meta = {
    "id": f"eeshsaxena/biohub-{tag}", "title": f"biohub {tag}",
    "code_file": f"biohub-{tag}.ipynb", "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": [],
    "dataset_sources": ["pilkwang/biohub-tracking-support-pack-50ep-v1"],
    "kernel_sources": [],
    "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
json.dump(meta, open(d / "kernel-metadata.json", "w"), indent=2)
print(f"built train_{tag}: epochs={EPOCHS} neg_weight={NEG_W}")
