#!/usr/bin/env python3
"""Anatomy of the 91 misses, and an ORACLE RANKING study of the duplicate problem.

The question this answers: when the tracker links the source to one detection of a
cell and the scorer's bipartite assignment picks a DIFFERENT detection of the same
cell, is there any feature visible in the submission alone that would have told us
which one the scorer was going to pick?

Because the scorer's assignment depends ONLY on node positions, re-pointing an edge
inside a co-location cluster cannot change the assignment. So this is a free lever if
and only if some feature ranks the scorer's pick first more often than the tracker
already does.
"""
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
import dup_lib as D

CLUSTER_R = 7.0


def analyse(path):
    allp = D.load_pred_all(path)
    cases = []
    tot = defaultdict(int)
    for s in D.SCORED:
        gpos, gtof, gedges = D.load_gt(s)
        pnodes, pedges = allp[s]
        match = D.scorer_match(gpos, gtof, pnodes)
        inv = {v: k for k, v in match.items()}
        gset = D.gt_edge_set(gedges, gtof)

        succ = defaultdict(list)
        pred = defaultdict(list)
        for a, b in pedges:
            succ[a].append(b)
            pred[b].append(a)

        by_t = defaultdict(list)
        for nid, (tt, p) in pnodes.items():
            by_t[tt].append(nid)

        for g1, g2 in sorted(gset):
            p1, p2 = match.get(g1), match.get(g2)
            if p1 is None and p2 is None:
                tot["both_missed"] += 1
                continue
            if p1 is None:
                tot["src_missed"] += 1
                continue
            if p2 is None:
                tot["dst_missed"] += 1
                continue
            if p2 in succ[p1]:
                tot["TP"] += 1
                continue
            # LINKING failure with both endpoints detected & matched
            t2 = gtof[g2]
            ours = succ[p1]
            # every predicted node at t2 within CLUSTER_R of the scorer's pick p2
            cl = [n for n in by_t[t2]
                  if np.linalg.norm(pnodes[n][1] - pnodes[p2][1]) <= CLUSTER_R]
            colocated = [q for q in ours
                         if np.linalg.norm(pnodes[q][1] - gpos[g2]) <= D.MATCH_UM]
            kind = ("no_successor" if not ours else
                    "linked_colocated" if colocated else "linked_far")
            tot[kind] += 1
            cases.append(dict(
                sample=s, g1=g1, g2=g2, p1=p1, p2=p2, t2=t2, kind=kind,
                ours=ours, cluster=cl, colocated=colocated,
                pnodes=pnodes, gpos_g2=gpos[g2], pred=pred, succ=succ))
    return cases, tot


def rank_study(cases):
    """For every failure where the scorer's pick p2 is inside the cluster we linked
    into, score candidate tie-breakers by whether they would have chosen p2."""
    feats = defaultdict(lambda: [0, 0])
    detail = []
    for c in cases:
        if c["kind"] != "linked_colocated":
            continue
        pn = c["pnodes"]
        p1 = c["p1"]
        p2 = c["p2"]
        # candidate set the LINKER could legally have chosen: our own successors
        # plus every node co-located with them at t2 (a re-point stays inside the
        # cluster, which is what keeps the scorer's assignment untouched)
        cand = set(c["ours"])
        for q in c["ours"]:
            for n in c["cluster"]:
                if np.linalg.norm(pn[n][1] - pn[q][1]) <= CLUSTER_R:
                    cand.add(n)
        cand = sorted(cand)
        if p2 not in cand:
            detail.append((c["sample"], c["g1"], c["g2"], "p2_not_reachable", len(cand)))
            continue
        src = pn[p1][1]
        # motion extrapolation from p1's own parent
        par = c["pred"].get(p1, [])
        vel = (src - pn[par[0]][1]) if par else np.zeros(3)
        cen = np.mean([pn[q][1] for q in cand], axis=0)
        scores = {
            "dist_to_source": {q: np.linalg.norm(pn[q][1] - src) for q in cand},
            "dist_to_motion": {q: np.linalg.norm(pn[q][1] - (src + vel)) for q in cand},
            "dist_to_centroid": {q: np.linalg.norm(pn[q][1] - cen) for q in cand},
            "lowest_id": {q: q for q in cand},
            "highest_id": {q: -q for q in cand},
            "fewest_parents": {q: len(c["pred"].get(q, [])) for q in cand},
            "most_parents": {q: -len(c["pred"].get(q, [])) for q in cand},
            "has_successor": {q: -len(c["succ"].get(q, [])) for q in cand},
            "no_successor": {q: len(c["succ"].get(q, [])) for q in cand},
        }
        for name, sc in scores.items():
            pick = min(cand, key=lambda q: (sc[q], q))
            feats[name][0] += 1 if pick == p2 else 0
            feats[name][1] += 1
        detail.append((c["sample"], c["g1"], c["g2"], "reachable", len(cand)))
    return feats, detail


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/out_t6stk3/submission.csv"
    cases, tot = analyse(path)
    print("=== GT-edge outcome breakdown")
    for k in ["TP", "no_successor", "linked_colocated", "linked_far",
              "src_missed", "dst_missed", "both_missed"]:
        print(f"  {k:18s} {tot[k]:5d}")
    print(f"  FN total = {sum(v for k, v in tot.items() if k != 'TP')}")

    feats, detail = rank_study(cases)
    nr = sum(1 for d in detail if d[3] == "p2_not_reachable")
    print(f"\n=== of the {len(detail)} colocated-link failures, "
          f"{nr} have the scorer's pick OUTSIDE any cluster we linked into "
          f"(a re-point cannot reach it); {len(detail)-nr} are reachable")
    print("\n=== which tie-breaker picks the scorer's node? (reachable cases only)")
    for name, (hit, n) in sorted(feats.items(), key=lambda kv: -kv[1][0]):
        print(f"  {name:20s} {hit:4d}/{n:4d}  = {hit/max(n,1):.3f}")
