#!/usr/bin/env python3
"""COMPONENT-level diagnosis: how many misses are the scorer flip-flopping between two
parallel connected components of our own graph?

The trace showed the real mechanism. Our tracks are internally fine; a SHADOW track
runs alongside the true one for a few frames, and the scorer's per-timepoint bipartite
assignment alternates between them. Every alternation destroys an edge, because the
edge we predicted leaves the component the scorer abandoned.

Node-level de-duplication cannot fix this (median separation is 7.4 um, and merging
diverging successors invents divisions). Deleting the SHADOW COMPONENT can: it leaves
the scorer no alternative, so every GT node on that cell matches the surviving track,
which is internally consistent. It also removes nodes, and the node-count penalty is
signed in our favour.

This measures: for each GT track, how often the scorer's pick changes component; how
long the shadow components are; and what an oracle deletion would be worth.
"""
import sys
import os
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D


def components(pnodes, pedges):
    parent = {n: n for n in pnodes}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in pedges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    comp = {n: find(n) for n in pnodes}
    members = defaultdict(list)
    for n, c in comp.items():
        members[c].append(n)
    return comp, members


def main(path):
    allp = D.load_pred_all(path)
    tot = defaultdict(int)
    shadow_len = []
    shadow_info = []
    for s in D.SCORED:
        gpos, gtof, gedges = D.load_gt(s)
        pnodes, pedges = allp[s]
        match = D.scorer_match(gpos, gtof, pnodes)
        gset = D.gt_edge_set(gedges, gtof)
        comp, members = components(pnodes, pedges)
        succ = defaultdict(list)
        for a, b in pedges:
            succ[a].append(b)
        clen = {c: len(m) for c, m in members.items()}
        # timepoint span of each component
        cspan = {c: (min(pnodes[n][0] for n in m), max(pnodes[n][0] for n in m))
                 for c, m in members.items()}

        for g1, g2 in sorted(gset):
            p1, p2 = match.get(g1), match.get(g2)
            if p1 is None or p2 is None:
                tot["unmatched_endpoint"] += 1
                continue
            if p2 in succ[p1]:
                tot["TP"] += 1
                continue
            c1, c2 = comp[p1], comp[p2]
            if c1 == c2:
                tot["FN_same_component"] += 1
                continue
            tot["FN_component_flip"] += 1
            # which side is the shadow? the shorter component
            loser = c2 if clen[c2] < clen[c1] else c1
            keeper = c1 if loser == c2 else c2
            shadow_len.append(clen[loser])
            shadow_info.append(dict(sample=s, loser=loser, keeper=keeper,
                                    lnodes=clen[loser], knodes=clen[keeper],
                                    lspan=cspan[loser], kspan=cspan[keeper]))
    print("=== GT-edge outcomes by component structure")
    for k in ["TP", "FN_component_flip", "FN_same_component", "unmatched_endpoint"]:
        print(f"  {k:22s} {tot[k]:5d}")

    a = np.array(shadow_len)
    print(f"\n=== {len(a)} component-flip misses. Size of the SHORTER component involved:")
    for cut in [2, 3, 5, 8, 12, 20, 40, 100, 1000, 10 ** 9]:
        print(f"    <= {cut:9d} nodes : {(a <= cut).sum():4d} / {len(a)}")
    print(f"    median {np.median(a):.0f}  mean {a.mean():.0f}  max {a.max()}")

    # how many DISTINCT shadow components are implicated, and how big are they
    byc = defaultdict(int)
    for si in shadow_info:
        byc[(si["sample"], si["loser"])] += 1
    print(f"\n=== {len(byc)} distinct shorter-components implicated, "
          f"covering {sum(byc.values())} missed edges")
    sizes = {}
    for si in shadow_info:
        sizes[(si["sample"], si["loser"])] = (si["lnodes"], si["lspan"], si["knodes"])
    rows = sorted(byc.items(), key=lambda kv: -kv[1])
    print("   edges_lost  loser_nodes  loser_span   keeper_nodes  sample")
    for (s, c), n in rows[:40]:
        ln, ls, kn = sizes[(s, c)]
        print(f"    {n:6d}     {ln:8d}   {str(ls):>12s}   {kn:8d}    {s}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/out_t6stk3/submission.csv")
