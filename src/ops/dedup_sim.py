#!/usr/bin/env python3
"""Simulate node DE-DUPLICATION on a finished submission and re-score it.

Why: against the real ground truth of the four scored movies, 37 of our 91 missing
edges (41%) are cases where the tracker linked the source to a node that is ITSELF
within 7 um of the correct target cell - a competing detection of the same cell that
lost the scorer's per-timepoint bipartite assignment. hengck23 described exactly this
failure in the competition discussion. Merging such duplicates should convert those
misses into hits AND cut the node count, and the node-count penalty is signed, so
fewer nodes multiplies the score up.

The transform: within one (dataset, timepoint), single-linkage cluster predicted nodes
whose physical separation is <= RADIUS um; keep one survivor per cluster at the cluster
centroid; rewire every edge onto survivors; drop self-loops and duplicate edges.
"""
import csv
import sys
from collections import defaultdict

import numpy as np
from scipy.spatial import cKDTree

SCALE = np.array([1.625, 0.40625, 0.40625])


def dedup(path, radius, out_path):
    rows = list(csv.DictReader(open(path, newline="")))
    nodes = [r for r in rows if r["row_type"] == "node"]
    edges = [r for r in rows if r["row_type"] == "edge"]
    by_key = defaultdict(list)
    for r in nodes:
        by_key[(r["dataset"], int(r["t"]))].append(r)

    remap = {}
    survivors = []
    merged = 0
    for key, group in by_key.items():
        if len(group) == 1:
            survivors.append(group[0])
            remap[(key[0], int(group[0]["node_id"]))] = int(group[0]["node_id"])
            continue
        P = np.stack([np.array([float(r["z"]), float(r["y"]), float(r["x"])]) * SCALE for r in group])
        tree = cKDTree(P)
        pairs = tree.query_pairs(radius) if radius > 0 else set()
        parent = list(range(len(group)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for a, b in pairs:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
        clusters = defaultdict(list)
        for i in range(len(group)):
            clusters[find(i)].append(i)
        for root, members in clusters.items():
            keep = group[members[0]]
            if len(members) > 1:
                merged += len(members) - 1
                c = P[members].mean(axis=0) / SCALE
                keep = dict(keep)
                keep["z"] = str(int(round(c[0])))
                keep["y"] = str(int(round(c[1])))
                keep["x"] = str(int(round(c[2])))
            survivors.append(keep)
            for m in members:
                remap[(key[0], int(group[m]["node_id"]))] = int(group[members[0]]["node_id"])

    # Which sources were REAL divisions before the merge? Everything else must stay
    # out-degree 1, or the merge invents divisions wholesale: at radius 5.0 the naive
    # rewire took the division count from 79 to 656, because two merged sources each
    # brought their own successor along.
    pre_out = defaultdict(int)
    for e in edges:
        pre_out[(e["dataset"], int(e["source_id"]))] += 1
    was_division = {k for k, v in pre_out.items() if v >= 2}
    div_survivors = {(k[0], remap.get(k)) for k in was_division if remap.get(k) is not None}

    seen = set()
    kept_by_source = defaultdict(int)
    out_edges = []
    for e in edges:
        s = remap.get((e["dataset"], int(e["source_id"])))
        t = remap.get((e["dataset"], int(e["target_id"])))
        if s is None or t is None or s == t:
            continue
        k = (e["dataset"], s, t)
        if k in seen:
            continue
        if kept_by_source[(e["dataset"], s)] >= 1 and (e["dataset"], s) not in div_survivors:
            continue
        if kept_by_source[(e["dataset"], s)] >= 2:
            continue
        seen.add(k)
        kept_by_source[(e["dataset"], s)] += 1
        e = dict(e)
        e["source_id"], e["target_id"] = str(s), str(t)
        out_edges.append(e)

    cols = ["id", "dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        i = 0
        for r in survivors:
            r = dict(r)
            r["id"] = i
            i += 1
            w.writerow({c: r[c] for c in cols})
        for r in out_edges:
            r = dict(r)
            r["id"] = i
            i += 1
            w.writerow({c: r[c] for c in cols})
    return len(survivors), len(out_edges), merged


OUTDIR = r"C:/Users/eeshs/AppData/Local/Temp/claude/C--Users-eeshs-Downloads/c663dcfb-9cf8-4d4d-aec8-747bb3f17179/scratchpad/dedup"

if __name__ == "__main__":
    src = sys.argv[1]
    for radius in [float(x) for x in sys.argv[2:]] or [2.0, 3.0, 4.0, 5.0, 6.0]:
        out = OUTDIR + "/dedup_%s.csv" % str(radius).replace(".", "p")
        n, e, m = dedup(src, radius, out)
        print(f"radius {radius:4.1f} um -> nodes {n} edges {e} (merged {m}) -> {out}", flush=True)
