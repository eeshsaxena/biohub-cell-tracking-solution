#!/usr/bin/env python3
"""Is the miss caused by CONTENTION in the global assignment, or by a genuine
sub-micron distance flip?

Dropping the "shadow" component costs 42-50 TP and wrecks node recall, so those
components are real cells, not duplicate detections. That kills the whole
duplicate-merging family. The remaining explanations for a component flip are:

  A) CONTENTION - the node our edge points at is genuinely the closest to the GT cell,
     but the global per-timepoint assignment gave it to a DIFFERENT GT node, so our
     cell had to take second best. Fixable in principle by not emitting the node that
     steals the assignment.
  B) MARGIN FLIP - our target really is farther from the GT centroid than the other
     candidate, by a small margin. Nothing in the submission can see this; it is a
     detector accuracy problem.

This measures which, and how big the margins are.
"""
import sys
import os
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D


def main(path):
    allp = D.load_pred_all(path)
    n_contend = n_margin = 0
    margins = []
    rows = []
    for s in D.SCORED:
        gpos, gtof, gedges = D.load_gt(s)
        pnodes, pedges = allp[s]
        match = D.scorer_match(gpos, gtof, pnodes)
        inv = {v: k for k, v in match.items()}
        gset = D.gt_edge_set(gedges, gtof)
        succ = defaultdict(list)
        for a, b in pedges:
            succ[a].append(b)
        gt_by_t = defaultdict(list)
        for g, t in gtof.items():
            gt_by_t[t].append(g)

        for g1, g2 in sorted(gset):
            p1, p2 = match.get(g1), match.get(g2)
            if p1 is None or p2 is None or p2 in succ[p1]:
                continue
            ours = succ[p1]
            if not ours:
                continue
            q = min(ours, key=lambda z: (float(np.linalg.norm(
                pnodes[z][1] - pnodes[p1][1])), z))
            dq = float(np.linalg.norm(pnodes[q][1] - gpos[g2]))
            dp = float(np.linalg.norm(pnodes[p2][1] - gpos[g2]))
            stolen_by = inv.get(q)
            if stolen_by is not None and stolen_by != g2:
                kind = "CONTENTION"
                n_contend += 1
            elif dq <= D.MATCH_UM:
                kind = "MARGIN_FLIP"
                n_margin += 1
                margins.append(dq - dp)
            else:
                kind = "our_target_out_of_range"
            rows.append((s, g1, g2, kind, round(dq, 2), round(dp, 2),
                         round(dq - dp, 2), stolen_by))
    print(f"=== of the linking misses:")
    c = defaultdict(int)
    for r in rows:
        c[r[3]] += 1
    for k, v in sorted(c.items(), key=lambda kv: -kv[1]):
        print(f"    {k:26s} {v:4d}")
    if margins:
        a = np.array(margins)
        print(f"\n=== MARGIN_FLIP: how much closer is the scorer's pick than ours? "
              f"(um, n={len(a)})")
        print(f"    median {np.median(a):.2f}  p25 {np.percentile(a,25):.2f}  "
              f"p75 {np.percentile(a,75):.2f}  min {a.min():.2f}  max {a.max():.2f}")
        for cut in [0.5, 1.0, 1.5, 2.0, 3.0]:
            print(f"    margin <= {cut:4.1f} um : {(a <= cut).sum():3d} / {len(a)}")
    print("\n  sample            g1        g2        kind          d(ours,GT) "
          "d(pick,GT)  margin  stolen_by")
    for r in rows[:70]:
        print(f"  {r[0]:16s} {r[1]:9d} {r[2]:9d} {r[3]:22s} {r[4]:8.2f} {r[5]:9.2f} "
              f"{r[6]:7.2f}  {r[7]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/out_t6stk3/submission.csv")
