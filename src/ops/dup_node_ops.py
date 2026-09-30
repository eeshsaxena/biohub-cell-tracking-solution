#!/usr/bin/env python3
"""The three assigned options (a) merge / (b) re-point / (c) drop, measured properly.

Every arm reports TP, FP, FN, node count, division count and node recall, because FP
is currently ZERO everywhere and any arm that manufactures a scoreable FP is spending
real money.

Survivor rules for (a):
  first     - lowest node id (what the earlier naive dedup did)
  linked    - the node the tracker actually linked INTO (has an incoming edge)
  centroid  - keep a node but move it to the cluster centroid
  parent    - the node whose incoming edge is shortest
All merges cap out-degree at 1 (2 for sources that were already divisions) and cap
in-degree at 1, so neither the fake-division artefact nor a multi-parent node can
appear.
"""
import argparse
import os
import sys
from collections import defaultdict

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dup_lib as D


def clusters_at_t(pnodes, radius):
    by_t = defaultdict(list)
    for n, (tt, p) in pnodes.items():
        by_t[tt].append(n)
    out = []
    for tt, ids in by_t.items():
        if len(ids) < 2:
            out.append([ids[0]] if ids else [])
            continue
        P = np.stack([pnodes[i][1] for i in ids])
        tree = cKDTree(P)
        parent = list(range(len(ids)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for i, j in tree.query_pairs(radius):
            ri, rj = find(i), find(j)
            if ri != rj:
                parent[max(ri, rj)] = min(ri, rj)
        groups = defaultdict(list)
        for i in range(len(ids)):
            groups[find(i)].append(ids[i])
        out.extend(groups.values())
    return out


def rebuild(nodes, edges, was_div):
    seen, in_deg, out_deg, keep = set(), defaultdict(int), defaultdict(int), []
    # shorter links first so the in-degree-1 cap keeps the physically plausible parent
    edges = sorted(edges, key=lambda e: float(np.linalg.norm(
        nodes[e[1]][1] - nodes[e[0]][1])) if e[0] in nodes and e[1] in nodes else 1e9)
    for a, b in edges:
        if a not in nodes or b not in nodes or a == b:
            continue
        if nodes[b][0] - nodes[a][0] != 1:
            continue
        if (a, b) in seen:
            continue
        if out_deg[a] >= (2 if a in was_div else 1) or in_deg[b] >= 1:
            continue
        seen.add((a, b))
        out_deg[a] += 1
        in_deg[b] += 1
        keep.append((a, b))
    return keep


def apply_node_op(pnodes, pedges, op, radius, survivor="linked"):
    pre_out = defaultdict(int)
    parents = defaultdict(list)
    for a, b in pedges:
        pre_out[a] += 1
        parents[b].append(a)
    was_div = {a for a, c in pre_out.items() if c >= 2}
    groups = [g for g in clusters_at_t(pnodes, radius) if len(g) > 1]

    remap, drop, newpos = {}, set(), {}
    for g in groups:
        if survivor == "first":
            keep = min(g)
        elif survivor == "linked":
            linked = [n for n in g if parents.get(n)]
            keep = min(linked) if linked else min(g)
        elif survivor == "parent":
            def plen(n):
                ps = parents.get(n)
                return float(np.linalg.norm(pnodes[n][1] - pnodes[ps[0]][1])) if ps else 1e9
            keep = min(g, key=lambda n: (plen(n), n))
        else:
            keep = min(g)
        if op == "merge":
            if survivor == "centroid":
                newpos[keep] = np.mean([pnodes[n][1] for n in g], axis=0)
            for n in g:
                if n != keep:
                    remap[n] = keep
                    drop.add(n)
        elif op == "drop":
            for n in g:
                if n != keep:
                    drop.add(n)          # no rewire: the edge simply disappears
        elif op == "repoint":
            pass                          # handled below, nothing removed

    if op == "repoint":
        member = {}
        for g in groups:
            for n in g:
                member[n] = g
        new_edges = []
        for a, b in pedges:
            g = member.get(b)
            if g and len(g) > 1:
                # pick the cluster member closest to the source's extrapolated position
                b = min(g, key=lambda q: (float(np.linalg.norm(
                    pnodes[q][1] - pnodes[a][1])), q))
            new_edges.append((a, b))
        return dict(pnodes), rebuild(pnodes, new_edges, was_div)

    nodes = {n: (tt, newpos.get(n, p)) for n, (tt, p) in pnodes.items() if n not in drop}
    edges = [(remap.get(a, a), remap.get(b, b)) for a, b in pedges]
    return nodes, rebuild(nodes, edges, was_div)


def score(by_sample):
    rows = []
    for s in D.SCORED:
        pnodes, pedges = by_sample[s]
        gpos, gtof, gedges = D.load_gt(s)
        r = D.judge(pnodes, pedges, gpos, gtof, gedges)
        denom = r["tp"] + r["fp"] + r["fn"]
        od = defaultdict(int)
        for a, b in pedges:
            od[a] += 1
        rows.append(dict(tp=r["tp"], fp=r["fp"], fn=r["fn"], denom=denom,
                         j=r["tp"] / max(denom, 1), nodes=len(pnodes), edges=len(pedges),
                         div=sum(1 for c in od.values() if c >= 2),
                         matched=len(r["match"]), gt_nodes=len(gtof)))
    w = sum(r["denom"] for r in rows)
    return dict(wj=sum(r["j"] * r["denom"] for r in rows) / max(w, 1),
                **{k: sum(r[k] for r in rows) for k in
                   ["tp", "fp", "fn", "nodes", "edges", "div", "matched", "gt_nodes"]})


def line(tag, s, base=None):
    d = "" if base is None else (
        f"  dJ={s['wj']-base['wj']:+.5f} dTP={s['tp']-base['tp']:+5d} "
        f"dFP={s['fp']-base['fp']:+5d} dNode={s['nodes']-base['nodes']:+7d} "
        f"dDiv={s['div']-base['div']:+5d}")
    return (f"{tag:30s} J={s['wj']:.5f} TP={s['tp']:5d} FP={s['fp']:5d} FN={s['fn']:4d} "
            f"nodes={s['nodes']:7d} div={s['div']:5d} nrec={s['matched']}/{s['gt_nodes']}{d}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("sub", nargs="?", default="data/out_t6stk3/submission.csv")
    ap.add_argument("--radius", default="3,5,7")
    a = ap.parse_args()
    allp = D.load_pred_all(a.sub)
    base = score(allp)
    print(line("BASELINE", base))
    print()
    for R in [float(x) for x in a.radius.split(",")]:
        for op, surv in [("merge", "first"), ("merge", "linked"), ("merge", "centroid"),
                         ("merge", "parent"), ("drop", "linked"), ("repoint", "-")]:
            out = {}
            for s in D.SCORED:
                pn, pe = allp[s]
                out[s] = apply_node_op(pn, pe, op, R, surv)
            print(line(f"({op}/{surv}) R={R}", score(out), base))
        print()
