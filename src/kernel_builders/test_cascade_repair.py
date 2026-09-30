"""Local smoke test for repair_cfg's "cascade" branch (no GPU, no Kaggle data).

Execs the REAL repair region out of the built cascade notebook against synthetic
detections, with the three graph-post-processing hooks stubbed (they are shared
with the control arm and unchanged here). Catches NameErrors / shape errors in
the new branch before a GPU session is spent on them, and asserts the sanity
property that casc_thr below UNET_THRESH reproduces the accel control exactly.

    .venv/Scripts/python.exe scratch_kernels/test_cascade_repair.py
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
NB = json.loads((HERE / "cascade_cv" / "biohub-cascade-cv.ipynb").read_text(encoding="utf-8"))


def cell_src(i):
    s = NB["cells"][i]["source"]
    return "".join(s) if isinstance(s, list) else s


cv = cell_src(len(NB["cells"]) - 1)
a = cv.index("def _emit_arrays")
b = cv.index("# ---------- run CV ----------")
REGION = cv[a:b]
assert 'cfg.get("linker", "fwd") == "cascade"' in REGION

# _link_sim comes verbatim from the untouched base pipeline cell.
base = "\n".join(cell_src(i) for i in range(len(NB["cells"]) - 1))
m = re.search(r"\ndef _link_sim\(.*?\n    return links\+_hun\(fp,fc,MAX_LINK_UM\)\n", base, re.S)
assert m, "could not slice _link_sim out of the base cells"
LINK_SIM = m.group(0)

NS = {
    "np": np, "defaultdict": defaultdict, "cKDTree": cKDTree,
    "linear_sum_assignment": linear_sum_assignment,
    "SCALE": np.array([1.625, 0.40625, 0.40625]),
    "CAND_THR": 0.05, "MAX_LINK_UM": 10.0, "TIGHT_UM": 6.0, "LINK_SIM_W": 2.0,
    "SHORT_MIN": 6, "DIV_DIVERGE_UM": 2.25, "DIV_GLOBAL_CAP": 0.00375, "DIV_SISTER_UM": 15.0,
    "_logit": lambda s: np.log(np.clip(s, 1e-4, 1 - 1e-4) / (1 - np.clip(s, 1e-4, 1 - 1e-4))),
    # graph post-processing hooks: shared with the control, stubbed out here
    "_short_filter": lambda nodes, edges: (nodes, edges),
    "_linefit": lambda nodes, edges: None,
    "_add_safe_divisions": lambda nodes, edges: 0,
}
exec(LINK_SIM, NS)
exec(REGION, NS)
repair_cfg = NS["repair_cfg"]

# ---- synthetic movie: 40 cells drifting, plus 8 spurious low-score nodes/frame ----
rng = np.random.default_rng(3)
T, NCELL, NSPUR = 12, 40, 8
pos = rng.uniform(5, 60, (NCELL, 3))
vel = rng.normal(0, 0.8, (NCELL, 3))
dets = []
for t in range(T):
    pos = pos + vel + rng.normal(0, 0.15, (NCELL, 3))
    real_sc = rng.uniform(0.55, 0.99, NCELL)
    spur = pos[rng.integers(0, NCELL, NSPUR)] + rng.normal(0, 2.0, (NSPUR, 3))
    spur_sc = rng.uniform(0.15, 0.34, NSPUR)
    low = rng.uniform(5, 60, (5, 3)); low_sc = rng.uniform(0.05, 0.14, 5)   # candidate pool
    coords = np.concatenate([pos, spur, low]); scores = np.concatenate([real_sc, spur_sc, low_sc])
    order = rng.permutation(len(coords))
    dets.append((coords[order], scores[order]))

_F = dict(unet_thr=0.15, max_dt=1, gate=4.5, snap=3.2, mincand=0.10, cap=0.08, synth=True,
          div_diverge=2.25, div_sister=15.0, linker="fwd", short_min=6, max_link=8.0)
CTRL = dict(_F, linker="accel", accel_bonus=0.80, accel_max=4.0)
_CA = dict(_F, linker="cascade", accel_bonus=0.80, accel_max=4.0)

fails = []


def run(cfg, tag):
    (pt, pp, pe), ngap, ndiv = repair_cfg(dets, cfg)
    st = dict(NS["CASC_STAT"])
    print("  %-18s nodes=%4d edges=%4d gaps=%d | stat=%s" % (tag, len(pt), len(pe), ngap, st))
    return pt, pp, pe


print("== repair_cfg smoke test on a synthetic 12-frame movie ==")
c_pt, c_pp, c_pe = run(CTRL, "accel CTRL")
for thr in (0.00, 0.25, 0.35, 0.50, 0.70):
    NS["CASC_STAT"].update({k: 0 for k in NS["CASC_STAT"]})
    pt, pp, pe = run(dict(_CA, casc_thr=thr), "casc%.2f" % thr)
    if thr == 0.00:
        same = (len(pt) == len(c_pt) and len(pe) == len(c_pe)
                and np.array_equal(pt, c_pt) and np.allclose(pp, c_pp) and np.array_equal(pe, c_pe))
        print("   casc0.00 identical to control:", same)
        if not same:
            fails.append("casc0.00 != control")
    if len(pt) == 0 or len(pe) == 0:
        fails.append("casc%.2f produced an empty graph" % thr)
for thr in (0.35, 0.50):
    NS["CASC_STAT"].update({k: 0 for k in NS["CASC_STAT"]})
    pt, pp, pe = run(dict(_CA, casc_thr=thr, casc_tight1=True), "casc%.2f tight1" % thr)
    if len(pe) == 0:
        fails.append("casc%.2f tight1 produced no edges" % thr)
print("   MAX_LINK_UM after all runs:", NS["MAX_LINK_UM"], "(cfg sets 8.0)")
if NS["MAX_LINK_UM"] != 8.0:
    fails.append("MAX_LINK_UM not restored: %r" % NS["MAX_LINK_UM"])

print()
print("FAILURES:", len(fails))
for f in fails:
    print("  -", f)
raise SystemExit(1 if fails else 0)
