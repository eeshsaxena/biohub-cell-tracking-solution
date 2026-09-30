#!/usr/bin/env python3
"""UNBIASED tie-breaker study over EVERY GT edge, not just the failures.

The trap the first pass fell into: the 37 colocated failures are *selected* as cases
where the tracker's own choice (essentially nearest-neighbour) was wrong, so "nearest
to source" scores ~6% there by construction and "farthest" would score ~94%. That
number is meaningless. The only honest measurement runs the same tie-breaker over all
2,127 GT edges - the 2,036 the tracker already gets right included - and compares its
hit rate against the tracker's current hit rate on the same population.

Also reports the geometry of the duplicate: how far the losing detection sits from the
winning one, and from the GT centroid.
"""
import sys
import os
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D


def build(path, cluster_r):
    allp = D.load_pred_all(path)
    per = {}
    for s in D.SCORED:
        gpos, gtof, gedges = D.load_gt(s)
        pnodes, pedges = allp[s]
        match = D.scorer_match(gpos, gtof, pnodes)
        gset = D.gt_edge_set(gedges, gtof)
        succ, pred = defaultdict(list), defaultdict(list)
        for a, b in pedges:
            succ[a].append(b)
            pred[b].append(a)
        by_t = defaultdict(list)
        for nid, (tt, p) in pnodes.items():
            by_t[tt].append(nid)
        # position array per timepoint for fast radius queries
        from scipy.spatial import cKDTree
        trees = {}
        for tt, ids in by_t.items():
            trees[tt] = (np.array(ids), cKDTree(np.stack([pnodes[i][1] for i in ids])))
        per[s] = dict(gpos=gpos, gtof=gtof, gset=gset, pnodes=pnodes, pedges=pedges,
                      match=match, succ=succ, pred=pred, trees=trees)
    return per


def candidates(st, p1, cluster_r):
    """Everything a within-cluster re-point of p1's outgoing edge could reach."""
    pn = st["pnodes"]
    out = set(st["succ"].get(p1, []))
    if not out:
        return []
    cand = set(out)
    for q in out:
        tt = pn[q][0]
        ids, tree = st["trees"][tt]
        for j in tree.query_ball_point(pn[q][1], cluster_r):
            cand.add(int(ids[j]))
    return sorted(cand)


TIEBREAKS = [
    "tracker", "near_source", "far_source", "near_motion", "far_motion",
    "near_centroid", "far_centroid", "low_id", "high_id",
    "no_parent_then_near", "no_parent_then_far",
    "longest_forward", "shortest_forward",
]


def pick(name, st, p1, cand, tracker_choice):
    pn = st["pnodes"]
    src = pn[p1][1]
    par = st["pred"].get(p1, [])
    vel = (src - pn[par[0]][1]) if par else np.zeros(3)
    cen = np.mean([pn[q][1] for q in cand], axis=0)

    def d_src(q):
        return float(np.linalg.norm(pn[q][1] - src))

    def d_mot(q):
        return float(np.linalg.norm(pn[q][1] - (src + vel)))

    def d_cen(q):
        return float(np.linalg.norm(pn[q][1] - cen))

    def nparent(q):
        return len(st["pred"].get(q, []))

    def fwd(q, depth=8):
        n, cur = 0, q
        while n < depth:
            s = st["succ"].get(cur, [])
            if not s:
                break
            cur = s[0]
            n += 1
        return n

    keyf = {
        "near_source": lambda q: (d_src(q), q),
        "far_source": lambda q: (-d_src(q), q),
        "near_motion": lambda q: (d_mot(q), q),
        "far_motion": lambda q: (-d_mot(q), q),
        "near_centroid": lambda q: (d_cen(q), q),
        "far_centroid": lambda q: (-d_cen(q), q),
        "low_id": lambda q: (q,),
        "high_id": lambda q: (-q,),
        "no_parent_then_near": lambda q: (nparent(q), d_src(q), q),
        "no_parent_then_far": lambda q: (nparent(q), -d_src(q), q),
        "longest_forward": lambda q: (-fwd(q), d_src(q), q),
        "shortest_forward": lambda q: (fwd(q), d_src(q), q),
    }
    if name == "tracker":
        return tracker_choice
    return min(cand, key=keyf[name])


def main(path, cluster_r):
    per = build(path, cluster_r)
    stats = {n: [0, 0] for n in TIEBREAKS}
    nsize = defaultdict(int)
    reach_only1 = 0
    total_eval = 0
    geom = []
    for s in D.SCORED:
        st = per[s]
        for g1, g2 in sorted(st["gset"]):
            p1, p2 = st["match"].get(g1), st["match"].get(g2)
            if p1 is None or p2 is None:
                continue
            cand = candidates(st, p1, cluster_r)
            if not cand:
                continue
            nsize[len(cand)] += 1
            if len(cand) == 1:
                reach_only1 += 1
            if p2 not in cand:
                continue  # unreachable: no re-point can fix or break this one
            total_eval += 1
            ours = set(st["succ"][p1])
            tracker_choice = p2 if p2 in ours else min(
                ours, key=lambda q: (float(np.linalg.norm(st["pnodes"][q][1] -
                                                          st["pnodes"][p1][1])), q))
            for n in TIEBREAKS:
                c = pick(n, st, p1, cand, tracker_choice)
                stats[n][0] += 1 if c == p2 else 0
                stats[n][1] += 1
            if p2 not in ours:
                q = tracker_choice
                pn = st["pnodes"]
                geom.append((s, float(np.linalg.norm(pn[q][1] - pn[p2][1])),
                             float(np.linalg.norm(pn[q][1] - st["gpos"][g2])),
                             float(np.linalg.norm(pn[p2][1] - st["gpos"][g2])),
                             len(cand)))
    print(f"cluster_r = {cluster_r} um")
    print(f"GT edges where a re-point could matter (p2 reachable) : {total_eval}")
    print(f"  of which the candidate set is a singleton (inert)   : {reach_only1}")
    print("  candidate-set sizes:", dict(sorted(nsize.items())[:10]))
    print("\n  tie-breaker            hits / n      acc     delta vs tracker")
    base = stats["tracker"][0]
    for n in TIEBREAKS:
        h, tn = stats[n]
        print(f"  {n:22s} {h:5d}/{tn:5d}  {h/max(tn,1):.4f}   {h-base:+5d}")
    if geom:
        a = np.array([[g[1], g[2], g[3]] for g in geom])
        print(f"\n  geometry of the {len(geom)} REACHABLE mislinks:")
        print(f"    |ours - scorer_pick|  median {np.median(a[:,0]):.2f} um  "
              f"min {a[:,0].min():.2f} max {a[:,0].max():.2f}")
        print(f"    |ours - GT centroid|  median {np.median(a[:,1]):.2f} um")
        print(f"    |pick - GT centroid|  median {np.median(a[:,2]):.2f} um")


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "data/out_t6stk3/submission.csv"
    r = float(sys.argv[2]) if len(sys.argv) > 2 else 7.0
    main(p, r)
