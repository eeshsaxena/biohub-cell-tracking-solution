"""Learned pack + FULL deterministic GRAPH REPAIR.

Our first learned run (host predict script + a plain geff->CSV flatten) scored
LB 0.887. The public 0.914 pipeline adds a deterministic repair layer on top of
the ILP graph that we skipped entirely:
  motion relink (tight 5.9um / relaxed 9.8um, velocity 0.5, learned bonus 0.78)
  gap close (max_gap 1, 5.75um, reuse existing 3.0um, added-frac cap 0.038)
  synthetic-gap refine, linefit smoothing (w 0.76, window 2)
  safe divisions (parent 4.5um, sister 6.8um, caps 0.008/0.0032)
  single-parent repair, prune isolated, edge_max 14um, enforce-next-frame
Every knob is env-var driven, so we run the reference pipeline verbatim and vary
it through BIOHUB_* env vars.

The reference notebook is TAGGED `candidate_23_300ep_clean_strict_repair` but its
default artifact is the **50ep** pack -- i.e. the public ~0.914 number came from
300-epoch weights while we were running 50-epoch ones (LB 0.887, and completely
FLAT across det 0.95-0.99 and with/without repair, which is what a
weights-limited pipeline looks like). WEIGHTS= swaps in a higher-epoch
`edge_predictor_best.pth` (e.g. hongdaekim/biohub-350ep-checkpoint-pin-v1).

usage: build_learned_repair.py <tag> [WEIGHTS=<kaggle/dataset-slug>]
       [CHECKPOINT=<checkpoint-file-name>] [KEY=VAL ...]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "_forum" / "biohub-cell-tracking-learned-graph-w-gap-recovery.ipynb"

tag = sys.argv[1] if len(sys.argv) > 1 else "repair"
overrides = dict(kv.split("=", 1) for kv in sys.argv[2:])
weights_ds = overrides.pop("WEIGHTS", None)
checkpoint_name = overrides.pop("CHECKPOINT", "edge_predictor_best.pth")
# SOUP=slugA,slugB averages checkpoint state_dicts (SWA / "model soup"). Only valid
# for checkpoints from the SAME training run (e.g. 300ep + 350ep of one run) -- naive
# averaging across DIFFERENT seeds fails on permutation symmetry.
soup_ds = overrides.pop("SOUP", None)

nb = json.load(open(SRC, encoding="utf-8"))
code = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
# cell 0 only displays a cover image from the author's figures dataset -> drop it
body = code[1:]

env_cell = "import os\n" + "".join(
    f'os.environ[{k!r}] = {v!r}\n' for k, v in overrides.items()
) + f'print("overrides: {overrides}", flush=True)\n'

# body[0]=config, body[1]=artifact setup (copies weights into REPO_DIR), body[2]=predict,
# body[3]=repair+CSV. Inject the weight swap AFTER setup and BEFORE predict.
if weights_ds:
    owner, slug = weights_ds.split("/", 1)
    # The artifact setup SYMLINKS the whole `weights` tree from the read-only input
    # mount, so we cannot write anywhere inside REPO_DIR/weights (OSError 30 on both
    # copy and unlink). Instead copy the checkpoint to a writable dir and REPOINT
    # WEIGHTS_RELATIVE at it: pathlib makes `REPO_DIR / "/abs/path"` == "/abs/path",
    # so the notebook's existence check AND the `--weights` arg both follow it.
    swap = f'''
import glob, shutil
from pathlib import Path
cands = [p for p in glob.glob("/kaggle/input/**/{checkpoint_name}", recursive=True)
         if {slug!r} in p]
assert cands, "swap weights NOT FOUND for {slug} / {checkpoint_name}"
_swapdir = Path("/kaggle/working/swap_weights")
_swapdir.mkdir(parents=True, exist_ok=True)
_dst = _swapdir / "edge_predictor_best.pth"
shutil.copy(cands[0], _dst)
WEIGHTS_RELATIVE = str(_dst)
print("SWAPPED WEIGHTS <-", cands[0], "as", _dst.name, flush=True)
print("  -> WEIGHTS_RELATIVE =", WEIGHTS_RELATIVE, _dst.stat().st_size, "bytes", flush=True)
print("  resolves to:", REPO_DIR / WEIGHTS_RELATIVE, flush=True)
'''
    body = body[:2] + [swap] + body[2:]

if soup_ds:
    slugs = [s.split("/", 1)[1] for s in soup_ds.split(",")]
    soup = f'''
import glob, torch
from pathlib import Path
slugs = {slugs!r}
paths = []
for sl in slugs:
    hits = [p for p in glob.glob("/kaggle/input/**/edge_predictor_best.pth", recursive=True) if sl in p]
    assert hits, f"soup checkpoint not found: {{sl}}"
    paths.append(hits[0])
print("SOUP over:", paths, flush=True)
sds = [torch.load(p, map_location="cpu") for p in paths]
sds = [sd.get("state_dict", sd) if isinstance(sd, dict) else sd for sd in sds]
keys = set(sds[0]);  assert all(set(s) == keys for s in sds), "state_dict keys differ"
avg = {{}}
for k in sds[0]:
    v = sds[0][k]
    if torch.is_floating_point(v):
        acc = v.double().clone()
        for s in sds[1:]:
            acc += s[k].double()
        avg[k] = (acc / len(sds)).to(v.dtype)
    else:
        avg[k] = v.clone()          # int/bool buffers: keep, do not average
_sd = Path("/kaggle/working/swap_weights"); _sd.mkdir(parents=True, exist_ok=True)
_dst = _sd / "edge_predictor_best.pth"
torch.save(avg, _dst)
WEIGHTS_RELATIVE = str(_dst)
print("SOUPED WEIGHTS ->", WEIGHTS_RELATIVE, _dst.stat().st_size, "bytes", flush=True)
'''
    body = body[:2] + [soup] + body[2:]

cells = [env_cell] + body
for s in cells:
    compile(s, "<c>", "exec")

nb_out = {
    "cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
               "source": s.splitlines(keepends=True)} for s in cells],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3.11"}},
    "nbformat": 4, "nbformat_minor": 5,
}
d = HERE / f"sub_{tag}"
d.mkdir(parents=True, exist_ok=True)
json.dump(nb_out, open(d / f"biohub-{tag}.ipynb", "w", encoding="utf-8"), indent=1)

meta = {
    "id": f"eeshsaxena/biohub-{tag}", "title": f"biohub {tag}",
    "code_file": f"biohub-{tag}.ipynb", "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": [],
    "dataset_sources": ["pilkwang/biohub-tracking-support-pack-50ep-v1"]
                       + ([weights_ds] if weights_ds else [])
                       + (soup_ds.split(",") if soup_ds else []),
    "kernel_sources": [],
    "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
json.dump(meta, open(d / "kernel-metadata.json", "w"), indent=2)
print(f"built sub_{tag} ({len(cells)} cells) overrides={overrides}")
