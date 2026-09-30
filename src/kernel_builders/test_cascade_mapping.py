"""Local unit test for the CONFIDENCE-CASCADE linker's index bookkeeping.

Slices the LINKERS block verbatim out of build_cascade_cv.py's CV source string
and execs it against numpy stubs, so the code under test is byte-identical to
what the Kaggle kernel runs. No GPU, no Kaggle data.

    .venv/Scripts/python.exe scratch_kernels/test_cascade_mapping.py
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
SRC = (HERE / "build_cascade_cv.py").read_text(encoding="utf-8")
m = re.search(r"# ---8<--- LINKERS BEGIN.*?\n(.*?)# ---8<--- LINKERS END", SRC, re.S)
assert m, "LINKERS markers not found in build_cascade_cv.py"
BLOCK = m.group(1)
assert "def _link_cascade" in BLOCK and "def _link_accel" in BLOCK

NS = {
    "np": np, "cKDTree": cKDTree, "linear_sum_assignment": linear_sum_assignment,
    "SCALE": np.array([1.0, 1.0, 1.0]),      # unit scale: this test is about indices
    "TIGHT_UM": 6.0, "MAX_LINK_UM": 8.0, "LINK_SIM_W": 2.0,
}
NS["_logit"] = lambda s: np.log(np.clip(np.asarray(s, float), 1e-4, 1 - 1e-4)
                                / (1 - np.clip(np.asarray(s, float), 1e-4, 1 - 1e-4)))
exec(BLOCK, NS)
_link_accel = NS["_link_accel"]
_link_cascade = NS["_link_cascade"]

FAILS = []


def check(cond, msg):
    if cond:
        print("  ok   ", msg)
    else:
        print("  FAIL ", msg)
        FAILS.append(msg)


def _norm(links):
    return sorted((int(a), int(b)) for a, b in links)


def _invariants(links, P, C, tag, gate=None):
    gate = NS["MAX_LINK_UM"] if gate is None else gate
    ps = [a for a, _ in links]; cs = [b for _, b in links]
    check(all(0 <= a < len(P) for a in ps) and all(0 <= b < len(C) for b in cs),
          f"{tag}: indices in range")
    check(len(set(ps)) == len(ps) and len(set(cs)) == len(cs),
          f"{tag}: injective in both source and target")
    if links:
        d = np.array([np.linalg.norm((C[b] - P[a]) * NS["SCALE"]) for a, b in links])
        check(d.max() <= gate + 1e-9, f"{tag}: every link within the raw gate ({d.max():.2f} <= {gate})")


print("== 1. degenerate thresholds must reproduce the control exactly ==")
rng = np.random.default_rng(0)
for trial in range(30):
    N = int(rng.integers(1, 12)); M = int(rng.integers(1, 12))
    P = rng.uniform(0, 12, (N, 3)); C = rng.uniform(0, 12, (M, 3))
    N2 = rng.uniform(0, 12, (int(rng.integers(0, 12)), 3))
    pv = rng.normal(0, 1, (N, 3)); psc = rng.uniform(0.15, 1.0, N); csc = rng.uniform(0.15, 1.0, M)
    ctl = _norm(_link_accel(P, C, N2, pv, psc, csc, 4.0, 0.80))
    lo = _norm(_link_cascade(P, C, N2, pv, psc, csc, 4.0, 0.80, 0.00, False))
    hi = _norm(_link_cascade(P, C, N2, pv, psc, csc, 4.0, 0.80, 9.99, False))
    if lo != ctl or hi != ctl:
        check(False, f"trial {trial}: thr=0 -> {lo == ctl}, thr=inf -> {hi == ctl} (control {len(ctl)} links)")
        break
else:
    check(True, "thr below every score == control (30 random trials)")
    check(True, "thr above every score == control (30 random trials)")

print("== 2. fuzz: gate + injectivity invariants hold for every threshold ==")
rng = np.random.default_rng(7)
bad = 0
for trial in range(200):
    N = int(rng.integers(0, 15)); M = int(rng.integers(0, 15))
    P = rng.uniform(0, 15, (N, 3)); C = rng.uniform(0, 15, (M, 3))
    N2 = rng.uniform(0, 15, (int(rng.integers(0, 15)), 3))
    pv = rng.normal(0, 1.5, (N, 3)) if N else None
    psc = rng.uniform(0.15, 1.0, N); csc = rng.uniform(0.15, 1.0, M)
    for thr in (0.25, 0.35, 0.50, 0.70):
        for s1t in (False, True):
            links = _link_cascade(P, C, N2, pv, psc, csc, 4.0, 0.80, thr, s1t)
            ps = [a for a, _ in links]; cs = [b for _, b in links]
            ok = (all(0 <= a < N for a in ps) and all(0 <= b < M for b in cs)
                  and len(set(ps)) == len(ps) and len(set(cs)) == len(cs))
            if ok and links:
                d = max(float(np.linalg.norm((C[b] - P[a]) * NS["SCALE"])) for a, b in links)
                ok = d <= NS["MAX_LINK_UM"] + 1e-9
            if not ok:
                bad += 1
                print("   first bad case", trial, thr, s1t, links)
                break
        if bad:
            break
    if bad:
        break
check(bad == 0, "200 random frame pairs x 4 thresholds x {tight,loose} stage 1: all valid")
check(NS["MAX_LINK_UM"] == 8.0, "MAX_LINK_UM restored after tight-stage-1 runs")

print("== 3. crafted steal: the low-score node must NOT take the confident cell's partner ==")
# A (confident, real cell) sits next to X (confident, its true next-frame position).
# B is a spurious low-score node slightly closer to X. The single global Hungarian
# minimises TOTAL cost and hands X to B, exiling A to the distant Y. That is the
# measured failure mode (an FP wrong-incoming edge on X + an FN on A->X).
NS["LINK_SIM_W"] = 0.0        # isolate geometry from the appearance term
P = np.array([[0.0, 0.0, 0.0],      # 0 = A, confident
              [0.0, 0.0, 0.5]])     # 1 = B, spurious
C = np.array([[0.0, 3.0, 0.0],      # 0 = Y, low score, far
              [0.0, 0.0, 0.6]])     # 1 = X, confident, A's true partner
psc = np.array([0.90, 0.20]); csc = np.array([0.20, 0.90])
pv = np.zeros((2, 3))
ctl = _norm(_link_accel(P, C, None, pv, psc, csc, 4.0, 0.0))
casc = _norm(_link_cascade(P, C, None, pv, psc, csc, 4.0, 0.0, 0.50, False))
print("   control:", ctl, " cascade:", casc)
check(ctl == [(0, 0), (1, 1)], "control (single Hungarian) does steal X: A->Y, B->X")
check(casc == [(0, 1), (1, 0)], "cascade fixes it: A->X (stage 1), B->Y (stage 2)")

print("== 4. index mapping survives array reordering (labels, not positions) ==")
# Same four points, but shuffled into different array slots. The cascade must
# return the SAME label pairing, which is only true if pidx/cidx map back right.
perm_p = [1, 0]; perm_c = [1, 0]
P2 = P[perm_p]; C2 = C[perm_c]; psc2 = psc[perm_p]; csc2 = csc[perm_c]
casc2 = _link_cascade(P2, C2, None, np.zeros((2, 3)), psc2, csc2, 4.0, 0.0, 0.50, False)
lbl = sorted((perm_p[a], perm_c[b]) for a, b in casc2)
check(lbl == [(0, 1), (1, 0)], f"shuffled arrays give the same label pairing {lbl}")
NS["LINK_SIM_W"] = 2.0

print("== 5. stage-1 tight gate: a far HIGH-HIGH pair is deferred to stage 2, not lost ==")
P = np.array([[0.0, 0.0, 0.0]]); C = np.array([[0.0, 7.0, 0.0]])   # 7um: > TIGHT 6, < MAX 8
psc = np.array([0.9]); csc = np.array([0.9])
loose = _link_cascade(P, C, None, np.zeros((1, 3)), psc, csc, 4.0, 0.0, 0.50, False)
tight = _link_cascade(P, C, None, np.zeros((1, 3)), psc, csc, 4.0, 0.0, 0.50, True)
check(_norm(loose) == [(0, 0)], "loose stage 1 links the 7um pair")
check(_norm(tight) == [(0, 0)], "tight stage 1 defers it but stage 2 still links it")
check(NS["MAX_LINK_UM"] == 8.0, "MAX_LINK_UM restored again")

print("== 6. empty inputs ==")
check(_link_cascade(np.zeros((0, 3)), C, None, None, np.zeros(0), csc, 4.0, 0.8, 0.5, False) == [],
      "no sources -> no links")
check(_link_cascade(P, np.zeros((0, 3)), None, np.zeros((1, 3)), psc, np.zeros(0), 4.0, 0.8, 0.5, False) == [],
      "no targets -> no links")

print()
print("FAILURES:", len(FAILS))
for f in FAILS:
    print("  -", f)
raise SystemExit(1 if FAILS else 0)
