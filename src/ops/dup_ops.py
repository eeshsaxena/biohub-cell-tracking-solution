#!/usr/bin/env python3
"""Candidate repairs for the component-flip family, applied to a real submission and
scored against the real GT.

Established by measurement before writing any of this:
  * ALL 66 linking misses are component flips; ZERO are within-component errors.
  * Pure re-pointing (option b) is dead: the tracker already gets 2036/2053 of the
    reachable cases and no tie-breaker beats it.
  * Node-level de-duplication (option a/c) barely fires: the median separation
    between our target and the scorer's pick is 7.41 um, and 31/37 pairs have
    successors that diverge, which is exactly what manufactures fake divisions.

So the repair has to work on CHAIN PAIRS, not node pairs. If two components run close
for a stretch, merging them frame-by-frame collapses both chains into one: the merged
node at t has exactly one successor, the merged node at t+1, so no out-degree artefact
can appear. That is the structural difference from the naive dedup that failed.

Operations:
  stitch  - merge a shadow component into its host frame by frame
  drop    - delete the shadow component outright (also cuts node count)
  trim    - delete only the shadow nodes that have a host node within R at that frame
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


# ---------------------------------------------------------------- graph helpers
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


def shadow_pairs(pnodes, pedges, radius, min_frac, min_overlap, max_len_ratio):
    """Find (shadow, host) component pairs that run close together.

    A pair qualifies when they overlap in time for >= min_overlap frames, are within
    `radius` um for >= min_frac of those frames, and the shadow is not longer than
    max_len_ratio * host.
    """
    from scipy.spatial import cKDTree
    comp, members = components(pnodes, pedges)
    clen = {c: len(m) for c, m in members.items()}
    cpos = defaultdict(dict)
    for n, (tt, p) in pnodes.items():
        # a component can in principle have two nodes at one t (after a division);
        # keep the first, these pairs are chains in practice
        cpos[comp[n]].setdefault(tt, p)

    # candidate pairs via a per-frame radius query, so we never do O(C^2)
    by_t = defaultdict(list)
    for n, (tt, p) in pnodes.items():
        by_t[tt].append(n)
    near = defaultdict(int)
    for tt, ids in by_t.items():
        P = np.stack([pnodes[i][1] for i in ids])
        tree = cKDTree(P)
        for i, j in tree.query_pairs(radius):
            ca, cb = comp[ids[i]], comp[ids[j]]
            if ca != cb:
                near[(min(ca, cb), max(ca, cb))] += 1

    pairs = []
    for (ca, cb), nclose in near.items():
        ov = set(cpos[ca]) & set(cpos[cb])
        if len(ov) < min_overlap:
            continue
        frac = nclose / len(ov)
        if frac < min_frac:
            continue
        shadow, host = (ca, cb) if clen[ca] <= clen[cb] else (cb, ca)
        if clen[shadow] > max_len_ratio * clen[host]:
            continue
        pairs.append((shadow, host, len(ov), nclose, frac))
    # one shadow may match several hosts: keep the closest-running host
    best = {}
    for shadow, host, ov, nclose, frac in pairs:
        if shadow not in best or frac > best[shadow][2]:
            best[shadow] = (host, ov, frac)
    # never let a component be both a shadow and a host
    hosts = {h for h, _, _ in best.values()}
    return {s: v for s, v in best.items() if s not in hosts}, comp, members, cpos


# ---------------------------------------------------------------- operations
def apply_op(pnodes, pedges, op, radius, min_frac, min_overlap, max_len_ratio,
             keep_gapfill=True):
    """Returns (new_nodes, new_edges, stats)."""
    best, comp, members, cpos = shadow_pairs(
        pnodes, pedges, radius, min_frac, min_overlap, max_len_ratio)
    stats = dict(pairs=len(best), removed=0, merged=0)
    if not best:
        return dict(pnodes), list(pedges), stats

    drop = set()
    remap = {}
    newpos = {}
    for shadow, (host, ov, frac) in best.items():
        hpos = cpos[host]
        for n in members[shadow]:
            tt = pnodes[n][0]
            if tt in hpos and float(np.linalg.norm(pnodes[n][1] - hpos[tt])) <= radius:
                # a host node covers this frame
                hn = None
                for m in members[host]:
                    if pnodes[m][0] == tt:
                        hn = m
                        break
                if op == "drop" or op == "trim":
                    drop.add(n)
                    if hn is not None:
                        remap[n] = hn
                    stats["removed"] += 1
                elif op == "stitch":
                    drop.add(n)
                    if hn is not None:
                        remap[n] = hn
                        newpos[hn] = (pnodes[n][1] + pnodes[hn][1]) / 2.0
                    stats["merged"] += 1
            else:
                # frame the host does not cover
                if op == "drop":
                    drop.add(n)
                    stats["removed"] += 1
                # trim / stitch keep it (it extends the host track)

    nodes = {}
    for n, (tt, p) in pnodes.items():
        if n in drop:
            continue
        nodes[n] = (tt, newpos.get(n, p))

    seen = set()
    out_edges = []
    in_deg = defaultdict(int)
    out_deg = defaultdict(int)
    pre_out = defaultdict(int)
    for a, b in pedges:
        pre_out[a] += 1
    was_div = {a for a, c in pre_out.items() if c >= 2}
    for a, b in pedges:
        a2 = remap.get(a, a)
        b2 = remap.get(b, b)
        if a2 not in nodes or b2 not in nodes or a2 == b2:
            continue
        if nodes[b2][0] - nodes[a2][0] != 1:
            continue
        k = (a2, b2)
        if k in seen:
            continue
        cap_out = 2 if a2 in was_div else 1
        if out_deg[a2] >= cap_out or in_deg[b2] >= 1:
            continue
        seen.add(k)
        out_deg[a2] += 1
        in_deg[b2] += 1
        out_edges.append(k)
    return nodes, out_edges, stats


# ---------------------------------------------------------------- driver
def score(nodes_edges_by_sample):
    rows = []
    for s in D.SCORED:
        pnodes, pedges = nodes_edges_by_sample[s]
        gpos, gtof, gedges = D.load_gt(s)
        r = D.judge(pnodes, pedges, gpos, gtof, gedges)
        denom = r["tp"] + r["fp"] + r["fn"]
        out_deg = defaultdict(int)
        for a, b in pedges:
            out_deg[a] += 1
        rows.append(dict(sample=s, tp=r["tp"], fp=r["fp"], fn=r["fn"], denom=denom,
                         j=r["tp"] / max(denom, 1), nodes=len(pnodes), edges=len(pedges),
                         div=sum(1 for c in out_deg.values() if c >= 2),
                         matched=len(r["match"]), gt_nodes=len(gtof)))
    w = sum(r["denom"] for r in rows)
    return dict(rows=rows, wj=sum(r["j"] * r["denom"] for r in rows) / max(w, 1),
                tp=sum(r["tp"] for r in rows), fp=sum(r["fp"] for r in rows),
                fn=sum(r["fn"] for r in rows), nodes=sum(r["nodes"] for r in rows),
                edges=sum(r["edges"] for r in rows), div=sum(r["div"] for r in rows),
                matched=sum(r["matched"] for r in rows),
                gt_nodes=sum(r["gt_nodes"] for r in rows))


def line(tag, s, base=None):
    d = "" if base is None else (f"  dJ={s['wj']-base['wj']:+.5f} dTP={s['tp']-base['tp']:+4d} "
                                 f"dFP={s['fp']-base['fp']:+4d} dN={s['nodes']-base['nodes']:+7d}")
    return (f"{tag:34s} J={s['wj']:.5f} TP={s['tp']:5d} FP={s['fp']:4d} FN={s['fn']:4d} "
            f"nodes={s['nodes']:7d} edges={s['edges']:7d} div={s['div']:5d} "
            f"nrec={s['matched']}/{s['gt_nodes']}{d}")


def write_sub(path, by_sample):
    cols = ["id", "dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        i = 0
        for s in D.SCORED:
            pnodes, pedges = by_sample[s]
            for n, (tt, p) in sorted(pnodes.items()):
                q = p / SCALE
                w.writerow([i, s, "node", n, tt, int(round(q[0])), int(round(q[1])),
                            int(round(q[2])), -1, -1])
                i += 1
            for a, b in pedges:
                w.writerow([i, s, "edge", -1, -1, -1, -1, -1, a, b])
                i += 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("sub", nargs="?", default="data/out_t6stk3/submission.csv")
    ap.add_argument("--ops", default="drop,trim,stitch")
    ap.add_argument("--radius", default="5,7,9")
    ap.add_argument("--frac", default="0.6,0.8,1.0")
    ap.add_argument("--overlap", type=int, default=3)
    ap.add_argument("--lenratio", type=float, default=1.0)
    a = ap.parse_args()

    allp = D.load_pred_all(a.sub)
    base = score(allp)
    print(line("BASELINE", base))
    print()
    for op in a.ops.split(","):
        for R in [float(x) for x in a.radius.split(",")]:
            for F in [float(x) for x in a.frac.split(",")]:
                out = {}
                st = dict(pairs=0, removed=0, merged=0)
                for s in D.SCORED:
                    pn, pe = allp[s]
                    n2, e2, stt = apply_op(pn, pe, op, R, F, a.overlap, a.lenratio)
                    out[s] = (n2, e2)
                    for k in st:
                        st[k] += stt[k]
                sc = score(out)
                print(line(f"{op} R={R} F={F}", sc, base),
                      f" pairs={st['pairs']} rm={st['removed']} mg={st['merged']}")
