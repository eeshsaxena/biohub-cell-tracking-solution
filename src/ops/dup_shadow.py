#!/usr/bin/env python3
"""Is the losing component a SHADOW of the same cell, or a different real cell?

This is the decision point. If the loser only ever matches the SAME GT track that the
keeper matches, it is a duplicate chain on one cell and deleting it is nearly free.
If it also carries GT nodes of its own track, deleting it destroys those edges and the
whole family is a trap.

Also measures the separation statistics that any deletion rule would have to key on,
and - critically - how far apart two GENUINELY DIFFERENT GT tracks run, because that
is the false-positive rate of any "these two components are too close" rule.
"""
import sys
import os
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D
from dup_comp import components


def gt_tracks(gedges, gtof):
    """label each GT node with its track id (follow dt==1 edges, split at divisions)"""
    nxt = defaultdict(list)
    prv = defaultdict(list)
    for a, b in gedges:
        a, b = int(a), int(b)
        if gtof.get(b, -99) - gtof.get(a, -99) == 1:
            nxt[a].append(b)
            prv[b].append(a)
    lab = {}
    tid = 0
    for g in sorted(gtof):
        if g in lab or prv.get(g):
            continue
        cur, t = g, tid
        tid += 1
        while True:
            lab[cur] = t
            s = nxt.get(cur, [])
            if len(s) != 1:
                break
            cur = s[0]
            if cur in lab:
                break
    for g in sorted(gtof):
        if g not in lab:
            lab[g] = tid
            tid += 1
    return lab


def main(path):
    allp = D.load_pred_all(path)
    same_track = 0
    diff_track = 0
    detail = []
    sep_shadow = []
    sep_realpair = []
    for s in D.SCORED:
        gpos, gtof, gedges = D.load_gt(s)
        pnodes, pedges = allp[s]
        match = D.scorer_match(gpos, gtof, pnodes)
        gset = D.gt_edge_set(gedges, gtof)
        comp, members = components(pnodes, pedges)
        succ = defaultdict(list)
        for a, b in pedges:
            succ[a].append(b)
        tlab = gt_tracks(gedges, gtof)
        clen = {c: len(m) for c, m in members.items()}

        # which GT tracks does each component carry?
        comp_tracks = defaultdict(set)
        for g, p in match.items():
            comp_tracks[comp[p]].add(tlab[g])

        # node positions per component per timepoint
        cpos = defaultdict(dict)
        for n, (tt, p) in pnodes.items():
            cpos[comp[n]][tt] = p

        for g1, g2 in sorted(gset):
            p1, p2 = match.get(g1), match.get(g2)
            if p1 is None or p2 is None or p2 in succ[p1]:
                continue
            c1, c2 = comp[p1], comp[p2]
            if c1 == c2:
                continue
            loser, keeper = (c2, c1) if clen[c2] < clen[c1] else (c1, c2)
            lt, kt = comp_tracks[loser], comp_tracks[keeper]
            if lt <= kt or lt == kt:
                same_track += 1
                tag = "loser_carries_no_own_track"
            elif lt & kt:
                same_track += 1
                tag = "overlapping"
            else:
                diff_track += 1
                tag = "DISJOINT_TRACKS"
            # separation profile over the loser's lifetime
            ov = sorted(set(cpos[loser]) & set(cpos[keeper]))
            d = [float(np.linalg.norm(cpos[loser][t] - cpos[keeper][t])) for t in ov]
            detail.append((s, loser, keeper, clen[loser], clen[keeper],
                           len(lt), len(kt), tag, len(ov),
                           round(float(np.median(d)), 2) if d else None))
            if d:
                sep_shadow.extend(d)

        # baseline: separation between two components that each carry a DIFFERENT GT
        # track and are nearest neighbours -> the real inter-cell distance
        tcomp = {}
        for c, ts in comp_tracks.items():
            if len(ts) == 1:
                tcomp[c] = list(ts)[0]
        cs = list(tcomp)
        for i, ca in enumerate(cs):
            best = None
            for cb in cs:
                if cb == ca or tcomp[cb] == tcomp[ca]:
                    continue
                ov = set(cpos[ca]) & set(cpos[cb])
                if len(ov) < 5:
                    continue
                dd = float(np.median([np.linalg.norm(cpos[ca][t] - cpos[cb][t]) for t in ov]))
                best = dd if best is None else min(best, dd)
            if best is not None:
                sep_realpair.append(best)

    print(f"=== component-flip misses: loser on the SAME GT track as the keeper : {same_track}")
    print(f"                           loser on a DISJOINT GT track            : {diff_track}")
    a = np.array(sep_shadow)
    b = np.array(sep_realpair)
    print(f"\n=== median frame-wise separation, loser vs keeper (shadow pairs), "
          f"n={len(a)} frames")
    print(f"    median {np.median(a):.2f}  p10 {np.percentile(a,10):.2f}  "
          f"p90 {np.percentile(a,90):.2f}")
    print(f"=== nearest-neighbour separation between components carrying DIFFERENT GT "
          f"tracks, n={len(b)}")
    print(f"    median {np.median(b):.2f}  p5 {np.percentile(b,5):.2f}  "
          f"p10 {np.percentile(b,10):.2f}  p25 {np.percentile(b,25):.2f}")
    print("\n  sample            loser  keeper  lnodes knodes ltracks ktracks  tag"
          "                        overlap  med_sep")
    for d in detail[:50]:
        print(f"  {d[0]:16s} {d[1]:7d} {d[2]:7d} {d[3]:6d} {d[4]:6d} {d[5]:6d} {d[6]:7d}  "
              f"{d[7]:26s} {d[8]:6d}  {d[9]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/out_t6stk3/submission.csv")
