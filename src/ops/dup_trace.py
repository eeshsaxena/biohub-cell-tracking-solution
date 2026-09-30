#!/usr/bin/env python3
"""Trace a GT TRACK against our prediction, frame by frame.

The failures are not scattered - they come in consecutive runs along a single GT
track (8 in a row on 6bba_05b6850b). That is not what isolated duplicate detections
look like. This tool prints, for each GT node on a track: the scorer's matched
predicted node, which of OUR connected components that node belongs to, our node's
offset from the GT centroid, and where our own chain went instead. If the scorer's
picks jump between our components, the problem is assignment instability across two
parallel chains; if they stay in one component, our tracker genuinely walked off.
"""
import sys
import os
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D


def components(pedges, pnodes):
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
    return {n: find(n) for n in pnodes}


def main(sample, tstart, tend):
    path = "data/out_t6stk3/submission.csv"
    allp = D.load_pred_all(path)
    gpos, gtof, gedges = D.load_gt(sample)
    pnodes, pedges = allp[sample]
    match = D.scorer_match(gpos, gtof, pnodes)
    comp = components(pedges, pnodes)
    succ, pred = defaultdict(list), defaultdict(list)
    for a, b in pedges:
        succ[a].append(b)
        pred[b].append(a)
    # GT tracks: follow dt==1 edges
    gsucc = defaultdict(list)
    for a, b in gedges:
        if gtof.get(int(b), -99) - gtof.get(int(a), -99) == 1:
            gsucc[int(a)].append(int(b))

    # find GT nodes in the window
    gids = sorted([g for g, t in gtof.items() if tstart <= t <= tend])
    # group into tracks by walking
    seen = set()
    tracks = []
    for g in gids:
        if g in seen:
            continue
        # walk back to the start inside the window
        chain = [g]
        cur = g
        while gsucc.get(cur):
            cur = gsucc[cur][0]
            if gtof[cur] > tend:
                break
            chain.append(cur)
        if len(chain) >= 3:
            tracks.append(chain)
            seen.update(chain)
    for chain in tracks[:6]:
        print(f"\n--- GT track {chain[0]} .. {chain[-1]} ({len(chain)} nodes)")
        print("    t   gt_id      matched_pred  comp      |pred-GT|   our_succ  succ_comp  "
              "|succ-GT(t+1)|  scorer_pick_next")
        for i, g in enumerate(chain):
            p = match.get(g)
            if p is None:
                print(f"   {gtof[g]:3d}  {g:9d}  UNMATCHED")
                continue
            d = float(np.linalg.norm(pnodes[p][1] - gpos[g]))
            nxt = chain[i + 1] if i + 1 < len(chain) else None
            s = succ.get(p, [])
            if nxt is not None and s:
                q = s[0]
                dq = float(np.linalg.norm(pnodes[q][1] - gpos[nxt]))
                pn = match.get(nxt)
                ok = "OK" if pn == q else f"MISS(pick={pn},comp={comp.get(pn)})"
                print(f"   {gtof[g]:3d}  {g:9d}  {p:9d}  {comp[p]:9d}  {d:7.2f}   "
                      f"{q:9d}  {comp[q]:9d}  {dq:9.2f}   {ok}")
            else:
                print(f"   {gtof[g]:3d}  {g:9d}  {p:9d}  {comp[p]:9d}  {d:7.2f}   "
                      f"{'(end)' if not s else s[0]}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
