#!/usr/bin/env python3
"""What headroom is left, and is any of it reachable by post-processing?

The 37 "duplicate" misses turned out to be margin flips against REAL competing cells,
which nothing in the submission can see. This asks whether the OTHER misses are
reachable:

  * our_target_out_of_range (19) - the tracker linked to a node 7-13 um away while the
    correct node sat 0.4-5.7 um away. Was the correct node already taken by another of
    our edges (our linker's own in-degree-1 contention), or simply not chosen?
  * no_successor (8) - our track ended. Is the correct node isolated, or is it the head
    of another of our components, i.e. a stitchable gap?

Both of those are genuine post-processing targets, unlike the margin flips.
"""
import sys
import os
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D


def main(path):
    allp = D.load_pred_all(path)
    cats = defaultdict(int)
    detail = []
    for s in D.SCORED:
        gpos, gtof, gedges = D.load_gt(s)
        pnodes, pedges = allp[s]
        match = D.scorer_match(gpos, gtof, pnodes)
        gset = D.gt_edge_set(gedges, gtof)
        succ, pred = defaultdict(list), defaultdict(list)
        for a, b in pedges:
            succ[a].append(b)
            pred[b].append(a)

        for g1, g2 in sorted(gset):
            p1, p2 = match.get(g1), match.get(g2)
            if p1 is None or p2 is None:
                cats["detection_miss"] += 1
                continue
            if p2 in succ[p1]:
                continue
            ours = succ.get(p1, [])
            dsrc = float(np.linalg.norm(pnodes[p2][1] - pnodes[p1][1]))
            p2_parent = pred.get(p2, [])
            if not ours:
                # our track died at p1. Is p2 reachable?
                why = ("p2_already_has_parent" if p2_parent else "p2_is_free")
                cats[f"no_successor/{why}"] += 1
                detail.append((s, g1, g2, "no_successor", why, round(dsrc, 2),
                               len(p2_parent), 0))
                continue
            q = min(ours, key=lambda z: (float(np.linalg.norm(
                pnodes[z][1] - pnodes[p1][1])), z))
            dq = float(np.linalg.norm(pnodes[q][1] - gpos[g2]))
            if dq <= D.MATCH_UM:
                cats["margin_flip"] += 1
                continue
            # genuine mislink: correct target is within range but we went elsewhere
            dours = float(np.linalg.norm(pnodes[q][1] - pnodes[p1][1]))
            why = ("p2_already_has_parent" if p2_parent else "p2_is_free")
            closer = "p2_is_CLOSER_to_source" if dsrc < dours else "p2_is_farther"
            cats[f"mislink/{why}/{closer}"] += 1
            detail.append((s, g1, g2, "mislink", why, round(dsrc, 2),
                           len(p2_parent), round(dours, 2)))
    print("=== miss taxonomy")
    for k, v in sorted(cats.items(), key=lambda kv: -kv[1]):
        print(f"    {k:46s} {v:4d}")
    print("\n  sample            g1        g2        kind          why                     "
          "d(p2,src) p2_parents  d(ours,src)")
    for d in detail:
        print(f"  {d[0]:16s} {d[1]:9d} {d[2]:9d} {d[3]:14s} {d[4]:22s} {d[5]:8.2f} "
              f"{d[6]:9d}  {d[7]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/out_t6stk3/submission.csv")
