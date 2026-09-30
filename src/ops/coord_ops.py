#!/usr/bin/env python3
"""COORDINATE-ONLY transforms, and why they are the right lever.

The measurement chain that got here:
  * all 66 linking misses are component flips, none are within-component errors;
  * deleting the competing component costs 42-50 TP, so it is a real cell;
  * only 2 misses are assignment contention;
  * 37 are MARGIN FLIPS - our target is a genuine detection of the right cell, just
    1.49 um (median) farther from the GT centroid than a competing detection.

A margin flip is a LOCALISATION problem, not a linking problem. And the scorer's
assignment depends on node POSITIONS only, so moving a node changes which detection
wins without touching topology, node count, out-degrees or divisions. Nothing
structural can break: FP can only appear if a node that was unmatched becomes matched
into a wrong pairing, and the node count the host penalises is untouched.

Transforms:
  smooth   - moving average along each track (detection jitter is high frequency,
             true cell motion is not)
  linefit  - local linear fit over a window, blended by weight w
  median   - temporal median filter
  none     - identity, for control
Each can be emitted rounded (submission format is integer voxels) or left float, so
the cost of the integer grid is measurable too.
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D

SCALE = D.SCALE


def tracks_of(pnodes, pedges):
    """Split the graph into maximal simple chains (break at divisions/merges)."""
    succ, pred = defaultdict(list), defaultdict(list)
    for a, b in pedges:
        succ[a].append(b)
        pred[b].append(a)
    starts = [n for n in pnodes
              if len(pred.get(n, [])) != 1 or len(succ.get(pred[n][0], [])) != 1]
    seen = set()
    chains = []
    for s in starts:
        cur = s
        ch = []
        while cur is not None and cur not in seen:
            ch.append(cur)
            seen.add(cur)
            nx = succ.get(cur, [])
            cur = nx[0] if len(nx) == 1 and len(pred.get(nx[0], [])) == 1 else None
        if ch:
            chains.append(ch)
    for n in pnodes:
        if n not in seen:
            chains.append([n])
            seen.add(n)
    return chains


def transform(pnodes, pedges, mode, window, weight, rounded=True):
    """Return new pnodes with adjusted positions. Topology untouched."""
    if mode == "none" and rounded:
        return dict(pnodes)
    out = {}
    for ch in tracks_of(pnodes, pedges):
        P = np.stack([pnodes[n][1] for n in ch]) / SCALE  # work in voxel space
        n = len(ch)
        Q = P.copy()
        if mode != "none" and n >= 2:
            for i in range(n):
                lo, hi = max(0, i - window), min(n, i + window + 1)
                seg = P[lo:hi]
                if mode == "smooth":
                    v = seg.mean(axis=0)
                elif mode == "median":
                    v = np.median(seg, axis=0)
                elif mode == "linefit":
                    tt = np.arange(lo, hi, dtype=float)
                    if len(tt) >= 2:
                        A = np.stack([tt, np.ones_like(tt)], axis=1)
                        coef, *_ = np.linalg.lstsq(A, seg, rcond=None)
                        v = coef[0] * i + coef[1]
                    else:
                        v = seg[0]
                else:
                    v = P[i]
                Q[i] = (1 - weight) * P[i] + weight * v
        for i, nd in enumerate(ch):
            q = Q[i]
            if rounded:
                q = np.round(q)
            out[nd] = (pnodes[nd][0], q * SCALE)
    return out


def score(by_sample):
    rows = []
    for s in D.SCORED:
        pnodes, pedges = by_sample[s]
        gpos, gtof, gedges = D.load_gt(s)
        r = D.judge(pnodes, pedges, gpos, gtof, gedges)
        denom = r["tp"] + r["fp"] + r["fn"]
        rows.append(dict(tp=r["tp"], fp=r["fp"], fn=r["fn"], denom=denom,
                         j=r["tp"] / max(denom, 1), nodes=len(pnodes),
                         matched=len(r["match"]), gt_nodes=len(gtof)))
    w = sum(r["denom"] for r in rows)
    return dict(wj=sum(r["j"] * r["denom"] for r in rows) / max(w, 1),
                tp=sum(r["tp"] for r in rows), fp=sum(r["fp"] for r in rows),
                fn=sum(r["fn"] for r in rows), nodes=sum(r["nodes"] for r in rows),
                matched=sum(r["matched"] for r in rows),
                gt_nodes=sum(r["gt_nodes"] for r in rows), rows=rows)


def line(tag, s, base=None):
    d = "" if base is None else (f"  dJ={s['wj']-base['wj']:+.5f} dTP={s['tp']-base['tp']:+4d} "
                                 f"dFP={s['fp']-base['fp']:+3d} dNrec={s['matched']-base['matched']:+4d}")
    return (f"{tag:32s} J={s['wj']:.5f} TP={s['tp']:5d} FP={s['fp']:4d} FN={s['fn']:4d} "
            f"nrec={s['matched']}/{s['gt_nodes']}{d}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("sub", nargs="?", default="data/out_t6stk3/submission.csv")
    ap.add_argument("--modes", default="smooth,linefit,median")
    ap.add_argument("--windows", default="1,2,3")
    ap.add_argument("--weights", default="0.25,0.5,1.0")
    ap.add_argument("--float", action="store_true", help="also test unrounded output")
    a = ap.parse_args()

    allp = D.load_pred_all(a.sub)
    base = score(allp)
    print(line("BASELINE (as submitted)", base))
    if a.float:
        pass
    print()
    for mode in a.modes.split(","):
        for w in [int(x) for x in a.windows.split(",")]:
            for wt in [float(x) for x in a.weights.split(",")]:
                for rnd in ([True, False] if a.float else [True]):
                    out = {}
                    for s in D.SCORED:
                        pn, pe = allp[s]
                        out[s] = (transform(pn, pe, mode, w, wt, rnd), pe)
                    sc = score(out)
                    tag = f"{mode} w={w} wt={wt}{'' if rnd else ' FLOAT'}"
                    print(line(tag, sc, base))
