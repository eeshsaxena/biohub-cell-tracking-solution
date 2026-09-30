#!/usr/bin/env python3
"""Scorer v3 = a from-source reimplementation of the COMPLETE official metric.

Ported line-by-line from the vendored competition code that ships inside every
one of our own run outputs:
  data/out_<tag>/tracking_repo/src/biohub_tracking/metrics.py
  data/out_<tag>/tracking_repo/src/biohub_tracking/division_metrics.py

Three things it gets right that ops/score_gt.py does not:

1. EDGE VALIDITY. metrics.py::_evaluate_matched_graph marks a predicted edge as
   scoreable when out_valid(source) OR in_valid(target) - NOT when both endpoints
   matched. A link from a correctly matched cell to a wrong, unannotated cell IS a
   false positive. score_gt.py drops it, which is why it reports FP = 0 everywhere.
   J = TP / (gt_edges + valid_pred_edges - TP).

2. NODE-COUNT PENALTY, per movie, with the host's own number:
   adjJ = max(0, J * (1 - 0.1*(N_pred - N_est)/N_est)), N_est from the geff extra
   `estimated_number_of_nodes`.  Aggregated as a weight-average over movies with
   weights TP+FP+FN.

3. DIVISIONS. division_metrics.py::evaluate_divisions:
   * TP  = GT divisions recovered, under a GENEROUS structural test (a weakly
           connected pred component that covers the one-node stage and >= 2 daughter
           lineages, and that contains at least one pred fork anywhere in it).
   * FP  = count_matched_pred_divisions - TP, where that count only includes pred
           forks whose MATCHED GT node has out_degree >= 1. A fork on an
           unannotated cell is FREE. It is NOT "every division we write".
   * FN  = 3 - TP on the public movies.
   score = adjEJ + 0.1 * divJ
"""
import csv
import json
import os
import sys
from collections import defaultdict, deque

import numpy as np
import zarr
from scipy.optimize import linear_sum_assignment

SCALE = np.array([1.625, 0.40625, 0.40625])
MATCH_UM = 7.0
ALPHA = 0.1
DIVW = 0.1
SCORED = ["44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1"]
ROOT = "C:/Users/eeshs/Downloads/biohub-cell-tracking"

_gt = {}


def gt(sample):
    if sample in _gt:
        return _gt[sample]
    g = f"{ROOT}/data/train/{sample}.geff"
    t = np.asarray(zarr.open(f"{g}/nodes/props/t/values", mode="r")[:])
    z = np.asarray(zarr.open(f"{g}/nodes/props/z/values", mode="r")[:])
    y = np.asarray(zarr.open(f"{g}/nodes/props/y/values", mode="r")[:])
    x = np.asarray(zarr.open(f"{g}/nodes/props/x/values", mode="r")[:])
    ids = np.asarray(zarr.open(f"{g}/nodes/ids", mode="r")[:])
    edges = np.asarray(zarr.open(f"{g}/edges/ids", mode="r")[:]).reshape(-1, 2)
    pos = {int(i): np.array([zz, yy, xx]) * SCALE for i, zz, yy, xx in zip(ids, z, y, x)}
    tof = {int(i): int(tt) for i, tt in zip(ids, t)}
    meta = json.load(open(f"{g}/zarr.json"))["attributes"]["geff"]
    n_est = meta["extra"]["estimated_number_of_nodes"]
    _gt[sample] = (pos, tof, [(int(a), int(b)) for a, b in edges], n_est)
    return _gt[sample]


def read_sub(path):
    nodes = defaultdict(dict)
    edges = defaultdict(list)
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ds = r["dataset"]
            if r["row_type"] == "node":
                nodes[ds][int(r["node_id"])] = (
                    int(r["t"]), float(r["z"]), float(r["y"]), float(r["x"]))
            else:
                edges[ds].append((int(r["source_id"]), int(r["target_id"])))
    return nodes, edges


def assign(gids, gpos, gtof, pnodes, pr_by_t):
    """Per-timepoint optimal one-to-one assignment, gated at 7 um. gt id -> pred id."""
    by_t = defaultdict(list)
    for i in gids:
        by_t[gtof[i]].append(i)
    match = {}
    for tt, ids in by_t.items():
        pids = pr_by_t.get(tt, [])
        if not pids:
            continue
        G = np.stack([gpos[i] for i in ids])
        P = np.stack([np.array(pnodes[i][1:]) * SCALE for i in pids])
        d = np.linalg.norm(G[:, None, :] - P[None, :, :], axis=2)
        cost = np.where(d <= MATCH_UM, d, MATCH_UM * 10.0)
        ri, ci = linear_sum_assignment(cost)
        for a, b in zip(ri, ci):
            if d[a, b] <= MATCH_UM:
                match[ids[a]] = pids[b]
    return match


def bipartite(left, adj):
    match_r, match_l = {}, {}

    def aug(u, seen):
        for v in adj.get(u, ()):
            if v in seen:
                continue
            seen.add(v)
            if v not in match_r or aug(match_r[v], seen):
                match_l[u] = v
                match_r[v] = u
                return True
        return False

    for u in left:
        aug(u, set())
    return match_l


def score_movie(sample, pnodes, pedges):
    gpos, gtof, gedges, n_est = gt(sample)

    pr_by_t = defaultdict(list)
    for i, v in pnodes.items():
        pr_by_t[v[0]].append(i)

    # ---- full-graph matching --------------------------------------------
    match = assign(list(gtof), gpos, gtof, pnodes, pr_by_t)
    inv = {v: k for k, v in match.items()}

    g_out, g_in = defaultdict(int), defaultdict(int)
    g_succ, g_pred = defaultdict(list), defaultdict(list)
    gset = set()
    for a, b in gedges:
        g_out[a] += 1
        g_in[b] += 1
        g_succ[a].append(b)
        g_pred[b].append(a)
        gset.add((a, b))
    gt_num_edges = len(gset)

    out_valid = {p: (g_out.get(inv[p], 0) > 0) for p in inv}
    in_valid = {p: (g_in.get(inv[p], 0) > 0) for p in inv}

    # ---- predicted graph -------------------------------------------------
    pe = set()
    for s, t in pedges:
        pe.add((s, t))
    p_succ, p_pred = defaultdict(list), defaultdict(list)
    out_deg = defaultdict(int)
    for s, t in pe:
        p_succ[s].append(t)
        p_pred[t].append(s)
        out_deg[s] += 1
    pred_div_nodes = {s for s, c in out_deg.items() if c >= 2}

    tp = valid = 0
    len_tp = len_fp = 0
    for s, t in pe:
        gs, gt_ = inv.get(s), inv.get(t)
        is_tp = gs is not None and gt_ is not None and (gs, gt_) in gset
        if is_tp:
            tp += 1
        if out_valid.get(s, False) or in_valid.get(t, False):
            valid += 1
        if gs is not None and gt_ is not None:
            if is_tp:
                len_tp += 1
            else:
                len_fp += 1
    fp = valid - tp
    fn = gt_num_edges - tp
    j = tp / max(gt_num_edges + valid - tp, 1)
    len_j = len_tp / max(len_tp + len_fp + gt_num_edges - len_tp, 1)

    n_pred = len(pnodes)
    ratio = (n_pred - n_est) / n_est
    mult = 1 - ALPHA * ratio
    adj_j = max(0.0, j * mult)
    len_adj = max(0.0, len_j * mult)

    # ---- divisions: FP side ---------------------------------------------
    matched_pred_divs = sum(
        1 for p in pred_div_nodes
        if p in inv and g_out.get(inv[p], 0) >= 1
    )

    # ---- divisions: TP side ---------------------------------------------
    gt_div_nodes = [a for a, c in g_out.items() if c >= 2]
    candidates = {}
    for dv in gt_div_nodes:
        keep = set(g_pred.get(dv, [])) | {dv}
        children = g_succ.get(dv, [])
        keep |= set(children)
        for c in children:
            keep |= set(g_succ.get(c, []))
        sub = sorted(keep)
        # timepoints of the subgraph with exactly one GT node
        cnt = defaultdict(int)
        for i in sub:
            cnt[gtof[i]] += 1
        one_node_times = {tt for tt, c in cnt.items() if c == 1}
        if not one_node_times or len(children) < 2:
            candidates[dv] = set()
            continue
        # daughter lineages inside the subgraph
        keepset = set(sub)
        lineages = []
        for c in children:
            seen, stack = {c}, [c]
            while stack:
                for nx in g_succ.get(stack.pop(), []):
                    if nx in keepset and nx not in seen:
                        seen.add(nx)
                        stack.append(nx)
            lineages.append(seen)
        # match pred against THIS subgraph only
        m = assign(sub, gpos, gtof, pnodes, pr_by_t)
        mnodes = {v: k for k, v in m.items()}  # pred id -> gt id
        # weakly connected components of the pred graph over the matched pred nodes
        remaining = set(mnodes)
        cand = set()
        while remaining:
            seed = next(iter(remaining))
            visited = {seed}
            q = deque([seed])
            comp = {seed}
            while q:
                cur = q.popleft()
                for nb in p_succ.get(cur, []) + p_pred.get(cur, []):
                    if nb not in visited:
                        visited.add(nb)
                        q.append(nb)
                        if nb in remaining:
                            comp.add(nb)
            remaining -= comp
            has_one = any(pnodes[p][0] in one_node_times for p in comp)
            if not has_one:
                continue
            mg = {mnodes[p] for p in comp}
            cov = sum(1 for lin in lineages if lin & mg)
            if cov >= 2:
                cand |= visited & pred_div_nodes
        candidates[dv] = cand

    pairing = bipartite(list(candidates), candidates)
    div_tp = len(pairing)
    div_fn = len(candidates) - div_tp
    div_fp = max(0, matched_pred_divs - div_tp)

    return dict(sample=sample, tp=tp, fp=fp, fn=fn, j=j, adj=adj_j,
                w=tp + fp + fn, n_pred=n_pred, n_est=n_est, ratio=ratio, mult=mult,
                len_j=len_j, len_adj=len_adj, len_tp=len_tp, len_fp=len_fp,
                len_w=len_tp + len_fp + gt_num_edges - len_tp,
                matched=len(match), gt_nodes=len(gtof), gt_edges=gt_num_edges,
                pred_div=len(pred_div_nodes), matched_pred_div=matched_pred_divs,
                div_tp=div_tp, div_fp=div_fp, div_fn=div_fn)


def main():
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_officialscores")
    os.makedirs(outdir, exist_ok=True)
    for tag in sys.argv[1:]:
        path = f"{ROOT}/data/out_{tag}/submission.csv"
        if not os.path.exists(path):
            print(f"SKIP {tag}", flush=True)
            continue
        dst = f"{outdir}/s3_{tag}.json"
        if os.path.exists(dst):
            print(f"HAVE {tag}", flush=True)
            continue
        nodes, edges = read_sub(path)
        rows = [score_movie(s, nodes.get(s, {}), edges.get(s, [])) for s in SCORED]
        W = sum(r["w"] for r in rows)
        adjEJ = sum(r["adj"] * r["w"] for r in rows) / W
        EJ = sum(r["tp"] for r in rows) / max(sum(r["w"] for r in rows), 1)
        LW = sum(r["len_w"] for r in rows)
        len_adjEJ = sum(r["len_adj"] * r["len_w"] for r in rows) / LW
        len_EJ = sum(r["len_tp"] for r in rows) / max(LW, 1)
        dtp = sum(r["div_tp"] for r in rows)
        dfp = sum(r["div_fp"] for r in rows)
        dfn = sum(r["div_fn"] for r in rows)
        divj = dtp / max(dtp + dfp + dfn, 1)
        rec = dict(tag=tag,
                   score=adjEJ + DIVW * divj,
                   adjEJ=adjEJ, EJ=EJ,
                   lenient_EJ=len_EJ, lenient_adjEJ=len_adjEJ,
                   lenient_score=len_adjEJ + DIVW * divj,
                   divj=divj, div_tp=dtp, div_fp=dfp, div_fn=dfn,
                   pred_div=sum(r["pred_div"] for r in rows),
                   matched_pred_div=sum(r["matched_pred_div"] for r in rows),
                   n_pred=sum(r["n_pred"] for r in rows),
                   n_est=sum(r["n_est"] for r in rows),
                   tp=sum(r["tp"] for r in rows), fp=sum(r["fp"] for r in rows),
                   fn=sum(r["fn"] for r in rows),
                   matched=sum(r["matched"] for r in rows),
                   per_movie=rows)
        json.dump(rec, open(dst, "w"), indent=1)
        print(f"{tag:10s} SCORE={rec['score']:.5f}  adjEJ={adjEJ:.5f} EJ={EJ:.5f} "
              f"divJ={divj:.4f} (tp{dtp}/fp{dfp}/fn{dfn}) mpd={rec['matched_pred_div']} "
              f"| lenAdj={len_adjEJ:.5f} N={rec['n_pred']}", flush=True)


if __name__ == "__main__":
    main()
