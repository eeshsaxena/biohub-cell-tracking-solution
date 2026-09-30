"""Build an hfusion variant from exact substring replacements, each with an EXPECTED occurrence count.

Needed because some settings live in several places at once: DET_THRESHOLD is set in cell 0 AND pinned by the
cell-1 drift guard; DUAL_SEED_MIN_CANDIDATE_RETENTION is set in cell 0, re-asserted in cell 4 before the
predictor is patched, AND pinned as text in the drift guard. Changing only one site either raises in the guard
or is silently undone.

usage: python build_multi.py <tag> '<json list of [old, new, expected_count]>'
"""
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = os.environ.get("BUILD_BASE", "v_hfusion")  # e.g. BUILD_BASE=v_hfast
tag = sys.argv[1]
edits = json.loads(sys.argv[2])

kdir = HERE / f"v_{tag}"
if kdir.exists():
    shutil.rmtree(kdir)
kdir.mkdir()
nb = json.loads((HERE / BASE / "kernel.ipynb").read_text(encoding="utf-8"))
body = "".join("".join(c["source"]) for c in nb["cells"])

for old, new, expected in edits:
    found = body.count(old)
    if found != expected:
        shutil.rmtree(kdir)
        sys.exit(f"{tag}: expected {expected}x of {old!r}, found {found}x - aborting, nothing written")

for cell in nb["cells"]:
    src = "".join(cell["source"])
    for old, new, _ in edits:
        src = src.replace(old, new)
    cell["source"] = src.splitlines(keepends=True)

out = "".join("".join(c["source"]) for c in nb["cells"])
for old, new, expected in edits:
    if out.count(new) < expected or (old not in new and old in out):
        shutil.rmtree(kdir)
        sys.exit(f"{tag}: post-check failed for {old!r} -> {new!r}")

(kdir / "kernel.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
meta = json.loads((HERE / BASE / "kernel-metadata.json").read_text())
meta["id"] = f"eeshsaxena/biohub-v-{tag}"
meta["title"] = f"biohub v {tag}"
(kdir / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
print(f"{tag} (base {BASE}): " + ", ".join(f"{e[2]}x {e[0][-40:]!r}" for e in edits) + " -> OK")
