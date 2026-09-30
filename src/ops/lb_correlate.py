#!/usr/bin/env python3
"""Tabulate every locally-scored arm against its public-LB score and report
rank correlations for each candidate proxy."""
import json
import glob
import os
import itertools
import numpy as np
from scipy.stats import spearmanr, kendalltau, pearsonr

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_officialscores")

# Board scores taken verbatim from ops/scores.log (the watcher's own record).
BOARD = {
    "divrank": 0.937, "divrank2": 0.943, "hfusion": 0.947, "hsoft": 0.946,
    "gdiv": 0.949, "stk3": 0.952, "t60h": 0.952, "t65h": 0.952,
    "t6stk3": 0.954, "t6r70": 0.954, "t6rlf": 0.953, "t6w72": 0.953,
    "t6lf": 0.953, "t65s3": 0.954, "xsv": 0.951, "xsvf": 0.951,
    "xsvdv": 0.946, "xsvdc": 0.950, "xsvd": 0.945,
}
# Older arms whose board score comes from the HANDOFF lineage table, not scores.log.
BOARD_EXTRA = {"det955": 0.945, "edgetta": 0.941, "946": 0.945}

rows = []
for f in sorted(glob.glob(f"{D}/s3_*.json")):
    r = json.load(open(f))
    rows.append(r)
by = {r["tag"]: r for r in rows}

N_EST = 134712.0


def table(board, title):
    tags = [t for t in board if t in by]
    tags.sort(key=lambda t: -board[t])
    print(f"\n===== {title}  (n={len(tags)}) =====")
    hdr = (f"{'arm':10s} {'board':>6s} {'strictAdj':>9s} {'strictJ':>8s} "
           f"{'lenAdj':>8s} {'lenJ':>8s} {'nodes':>7s} {'Nratio':>8s} {'mult':>7s}")
    print(hdr)
    for t in tags:
        r = by[t]
        ratio = (r["n_pred"] - N_EST) / N_EST
        mult = r["adjEJ"] / r["EJ"] if r["EJ"] else float("nan")
        print(f"{t:10s} {board[t]:6.3f} {r['adjEJ']:9.5f} {r['EJ']:8.5f} "
              f"{r['lenient_adjEJ']:8.5f} {r['lenient_EJ']:8.5f} "
              f"{r['n_pred']:7d} {ratio:+8.4f} {mult:7.5f}")

    b = np.array([board[t] for t in tags])
    prox = {
        "lenient J  (ops/score_gt.py, no node term)": [by[t]["lenient_EJ"] for t in tags],
        "lenient J  x node multiplier": [by[t]["lenient_adjEJ"] for t in tags],
        "STRICT J   (official edge rule, no node term)": [by[t]["EJ"] for t in tags],
        "STRICT J   x node multiplier  = OFFICIAL adjEJ": [by[t]["adjEJ"] for t in tags],
        "node count alone (negated)": [-by[t]["n_pred"] for t in tags],
        "node multiplier alone": [by[t]["adjEJ"] / by[t]["EJ"] for t in tags],
    }
    print(f"\n{'proxy':48s} {'spearman':>9s} {'p':>8s} {'kendall':>8s} {'pearson':>8s}")
    for k, v in prox.items():
        v = np.array(v, dtype=float)
        s = spearmanr(v, b)
        kt = kendalltau(v, b)
        pe = pearsonr(v, b)
        print(f"{k:48s} {s.statistic:9.3f} {s.pvalue:8.4f} "
              f"{kt.statistic:8.3f} {pe.statistic:8.3f}")

    # pairwise concordance on pairs the board actually separates
    print("\npairwise concordance (only pairs whose board scores differ):")
    for k, v in prox.items():
        v = np.array(v, dtype=float)
        ok = tot = 0
        for i, j in itertools.combinations(range(len(tags)), 2):
            if b[i] == b[j]:
                continue
            tot += 1
            if (v[i] - v[j]) * (b[i] - b[j]) > 0:
                ok += 1
        print(f"  {k:48s} {ok:3d}/{tot:3d} = {ok/tot:.3f}")
    return tags, b, prox


tags, b, prox = table(BOARD, "ARMS WITH A BOARD SCORE IN ops/scores.log")
allb = dict(BOARD)
allb.update(BOARD_EXTRA)
table(allb, "PLUS THREE OLDER ARMS (board score from the HANDOFF lineage table)")

# ---- fit the node term: board ~ J + beta * node_ratio ---------------------
print("\n===== does a FITTED node term rescue either proxy? =====")
tg = [t for t in BOARD if t in by]
b = np.array([BOARD[t] for t in tg])
ratio = np.array([(by[t]["n_pred"] - N_EST) / N_EST for t in tg])
for name, key in [("lenient J", "lenient_EJ"), ("strict J", "EJ")]:
    J = np.array([by[t][key] for t in tg])
    best = None
    for beta in np.arange(-3.0, 3.01, 0.01):
        v = J - beta * ratio
        s = spearmanr(v, b).statistic
        if best is None or s > best[1]:
            best = (beta, s)
    print(f"{name:12s}: raw spearman {spearmanr(J, b).statistic:.3f}; "
          f"best beta {best[0]:+.2f} -> spearman {best[1]:.3f} "
          f"(official beta is +0.1*J ~ {0.1*J.mean():.2f})")

# ---- the four candidate bodies -------------------------------------------
print("\n===== THE FOUR CANDIDATE BODIES =====")
print(f"{'arm':8s} {'board':>7s} {'strictAdj':>9s} {'lenAdj':>8s} {'lenJ':>8s} "
      f"{'nodes':>7s} {'mult':>7s} {'divwritten':>10s} {'mpd':>4s}")
for t in ["t6stk3", "xpub", "xbase", "xsv", "t6sr", "t6r70", "t6rlf"]:
    if t not in by:
        continue
    r = by[t]
    bs = f"{BOARD[t]:.3f}" if t in BOARD else "pending"
    print(f"{t:8s} {bs:>7s} {r['adjEJ']:9.5f} {r['lenient_adjEJ']:8.5f} "
          f"{r['lenient_EJ']:8.5f} {r['n_pred']:7d} {r['adjEJ']/r['EJ']:7.5f} "
          f"{r['pred_div']:10d} {r['matched_pred_div']:4d}")

print("\nper-movie breakdown for the bodies that matter:")
for t in ["t6stk3", "xpub", "xbase", "xsv"]:
    if t not in by:
        continue
    print(f"\n-- {t}")
    for m in by[t]["per_movie"]:
        print(f"   {m['sample']:15s} Npred={m['n_pred']:6d} Nest={m['n_est']:6d} "
              f"mult={m['mult']:.5f} w={m['w']:5d} strictJ={m['j']:.5f} "
              f"lenJ={m['len_j']:.5f} matched={m['matched']}/{m['gt_nodes']}")
