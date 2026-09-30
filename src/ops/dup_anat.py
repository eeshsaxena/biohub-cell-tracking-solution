#!/usr/bin/env python3
"""Anatomy of the 37 colocated mislinks: are they PARALLEL CHAINS or lone duplicates?

This decides which repair is even applicable.
  * If the scorer's node p2 has a parent r, and r sits on top of our source p1, then
    two chains are tracking one cell and the scorer flipped between them. Merging the
    two chains fixes it with NO out-degree artefact, because the successors merge too.
  * If p2 has no parent at all, it is an orphan detection that the scorer preferred.
    Merging q into p2 still fixes it and costs one node.
  * If p2's parent is somewhere else entirely, merging invents a multi-parent node.

Also reports how far apart the two detections are, which sets the merge radius, and
what the successors do, which is what drives the out-degree artefact.
"""
import sys
import os
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D


def main(path):
    allp = D.load_pred_all(path)
    kinds = defaultdict(int)
    dists = []
    rows = []
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
            if p1 is None or p2 is None or p2 in succ[p1]:
                continue
            ours = succ[p1]
            if not ours:
                continue
            # our chosen target, nearest to source
            q = min(ours, key=lambda z: (float(np.linalg.norm(pnodes[z][1] - pnodes[p1][1])), z))
            d_q_gt = float(np.linalg.norm(pnodes[q][1] - gpos[g2]))
            if d_q_gt > D.MATCH_UM:
                continue  # 'linked_far', a genuine tracking error, different problem
            d_qp2 = float(np.linalg.norm(pnodes[q][1] - pnodes[p2][1]))
            par = pred.get(p2, [])
            if not par:
                kind = "p2_orphan"
            else:
                r = par[0]
                d_rp1 = float(np.linalg.norm(pnodes[r][1] - pnodes[p1][1]))
                kind = ("parallel_chain" if d_rp1 <= 7.0 else "p2_parent_far")
            kinds[kind] += 1
            dists.append(d_qp2)
            # would a merge of {q, p2} create an out-degree conflict?
            sq, sp = succ.get(q, []), succ.get(p2, [])
            if sq and sp:
                dd = float(np.linalg.norm(pnodes[sq[0]][1] - pnodes[sp[0]][1]))
                conf = "succ_agree<=5" if dd <= 5.0 else f"succ_split_{dd:.1f}"
            elif not sq and not sp:
                conf = "both_terminal"
            else:
                conf = "one_terminal"
            rows.append((s, g1, g2, kind, round(d_qp2, 2), round(d_q_gt, 2),
                         round(float(np.linalg.norm(pnodes[p2][1] - gpos[g2])), 2), conf))
    print("=== the 37 colocated mislinks, by structure")
    for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
        print(f"  {k:18s} {v:4d}")
    a = np.array(dists)
    print(f"\n  |our_target - scorer_pick| : median {np.median(a):.2f}  mean {a.mean():.2f}")
    for r in [2, 3, 4, 5, 6, 7, 8, 10, 12, 14]:
        print(f"    within {r:2d} um : {(a <= r).sum():3d} / {len(a)}")
    cc = defaultdict(int)
    for row in rows:
        cc[row[7] if row[7].startswith(("succ_agree", "both", "one")) else "succ_split"] += 1
    print("\n  successor behaviour of the duplicate pair (drives the out-degree artefact):")
    for k, v in sorted(cc.items(), key=lambda kv: -kv[1]):
        print(f"    {k:18s} {v:4d}")
    print("\n  detail (sample, gt_src, gt_dst, kind, d(q,p2), d(q,GT), d(p2,GT), succ):")
    for row in rows:
        print("   ", row)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/out_t6stk3/submission.csv")
