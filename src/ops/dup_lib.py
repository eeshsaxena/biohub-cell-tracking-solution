#!/usr/bin/env python3
"""Shared loader + scorer-faithful matcher for the duplicate-detection study.

Everything here mirrors ops/score_gt.py exactly (same SCALE, same 7.0 um gate, same
per-timepoint global bipartite assignment) so that any classification computed on top
of it is describing the real scorer's behaviour and not an approximation of it.
"""
import csv
import os
from collections import defaultdict

import numpy as np
import zarr
from scipy.optimize import linear_sum_assignment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCALE = np.array([1.625, 0.40625, 0.40625])
MATCH_UM = 7.0
SCORED = ["44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1"]

_GT_CACHE = {}


def load_gt(sample):
    if sample in _GT_CACHE:
        return _GT_CACHE[sample]
    g = os.path.join(ROOT, "data", "train", sample + ".geff")
    t = np.asarray(zarr.open(f"{g}/nodes/props/t/values", mode="r")[:])
    z = np.asarray(zarr.open(f"{g}/nodes/props/z/values", mode="r")[:])
    y = np.asarray(zarr.open(f"{g}/nodes/props/y/values", mode="r")[:])
    x = np.asarray(zarr.open(f"{g}/nodes/props/x/values", mode="r")[:])
    ids = np.asarray(zarr.open(f"{g}/nodes/ids", mode="r")[:])
    edges = np.asarray(zarr.open(f"{g}/edges/ids", mode="r")[:]).reshape(-1, 2)
    pos = {int(i): np.array([zz, yy, xx], dtype=float) * SCALE
           for i, zz, yy, xx in zip(ids, z, y, x)}
    tof = {int(i): int(tt) for i, tt in zip(ids, t)}
    _GT_CACHE[sample] = (pos, tof, edges)
    return pos, tof, edges


def load_pred(path, sample):
    """nodes: id -> (t, scaled_pos);  edges: list of (src, dst)"""
    nodes, edges = {}, []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["dataset"] != sample:
                continue
            if r["row_type"] == "node":
                nodes[int(r["node_id"])] = (
                    int(r["t"]),
                    np.array([float(r["z"]), float(r["y"]), float(r["x"])]) * SCALE,
                )
            else:
                edges.append((int(r["source_id"]), int(r["target_id"])))
    return nodes, edges


def load_pred_all(path):
    """One pass over the whole csv -> {sample: (nodes, edges)}"""
    out = {s: ({}, []) for s in SCORED}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            ds = r["dataset"]
            if ds not in out:
                continue
            nodes, edges = out[ds]
            if r["row_type"] == "node":
                nodes[int(r["node_id"])] = (
                    int(r["t"]),
                    np.array([float(r["z"]), float(r["y"]), float(r["x"])]) * SCALE,
                )
            else:
                edges.append((int(r["source_id"]), int(r["target_id"])))
    return out


def scorer_match(gpos, gtof, pnodes):
    """The metric's own per-timepoint global assignment. Returns gt_id -> pred_id."""
    gt_by_t, pr_by_t = defaultdict(list), defaultdict(list)
    for i, tt in gtof.items():
        gt_by_t[tt].append(i)
    for i, (tt, _) in pnodes.items():
        pr_by_t[tt].append(i)
    match = {}
    for tt, gids in gt_by_t.items():
        pids = pr_by_t.get(tt, [])
        if not pids:
            continue
        G = np.stack([gpos[i] for i in gids])
        P = np.stack([pnodes[i][1] for i in pids])
        d = np.linalg.norm(G[:, None, :] - P[None, :, :], axis=2)
        cost = np.where(d <= MATCH_UM, d, MATCH_UM * 10.0)
        ri, ci = linear_sum_assignment(cost)
        for a, b in zip(ri, ci):
            if d[a, b] <= MATCH_UM:
                match[gids[a]] = pids[b]
    return match


def gt_edge_set(gedges, gtof):
    return {(int(a), int(b)) for a, b in gedges
            if gtof.get(int(b), -99) - gtof.get(int(a), -99) == 1}


def judge(pnodes, pedges, gpos, gtof, gedges, match=None):
    """TP / FP / FN under the sparse-annotation rule."""
    if match is None:
        match = scorer_match(gpos, gtof, pnodes)
    inv = {v: k for k, v in match.items()}
    gset = gt_edge_set(gedges, gtof)
    tp = fp = 0
    tp_edges = set()
    for s, t in pedges:
        gs, gt_ = inv.get(s), inv.get(t)
        if gs is None or gt_ is None:
            continue
        if (gs, gt_) in gset:
            tp += 1
            tp_edges.add((gs, gt_))
        else:
            fp += 1
    return dict(tp=tp, fp=fp, fn=len(gset) - tp, gset=gset, match=match,
                inv=inv, tp_edges=tp_edges)


def score_submission(path, verbose=False):
    """Full weighted edge J + division stats, identical to ops/score_gt.py."""
    allp = load_pred_all(path)
    rows = []
    for s in SCORED:
        gpos, gtof, gedges = load_gt(s)
        pnodes, pedges = allp[s]
        r = judge(pnodes, pedges, gpos, gtof, gedges)
        denom = r["tp"] + r["fp"] + r["fn"]
        out_deg = defaultdict(int)
        in_deg = defaultdict(int)
        for a, b in pedges:
            out_deg[a] += 1
            in_deg[b] += 1
        pred_div = {a for a, c in out_deg.items() if c >= 2}
        g_out = defaultdict(int)
        for a, b in gedges:
            g_out[int(a)] += 1
        gt_div = {a for a, c in g_out.items() if c >= 2}
        div_tp = sum(1 for g in gt_div if r["match"].get(g) in pred_div)
        rows.append(dict(sample=s, tp=r["tp"], fp=r["fp"], fn=r["fn"],
                         j=r["tp"] / max(denom, 1), denom=denom,
                         nodes=len(pnodes), edges=len(pedges),
                         pred_div=len(pred_div), gt_div=len(gt_div), div_tp=div_tp,
                         multi_parent=sum(1 for c in in_deg.values() if c >= 2),
                         matched=len(r["match"]), gt_nodes=len(gtof)))
    w = sum(r["denom"] for r in rows)
    wj = sum(r["j"] * r["denom"] for r in rows) / max(w, 1)
    dtp = sum(r["div_tp"] for r in rows)
    dp = sum(r["pred_div"] for r in rows)
    dg = sum(r["gt_div"] for r in rows)
    summary = dict(rows=rows, wj=wj, tp=sum(r["tp"] for r in rows),
                   fp=sum(r["fp"] for r in rows), fn=sum(r["fn"] for r in rows),
                   nodes=sum(r["nodes"] for r in rows), edges=sum(r["edges"] for r in rows),
                   pred_div=dp, gt_div=dg, div_tp=dtp,
                   divj=dtp / max(dp + dg - dtp, 1),
                   multi_parent=sum(r["multi_parent"] for r in rows))
    if verbose:
        for r in rows:
            print(f"  {r['sample']:16s} J={r['j']:.4f} TP={r['tp']:5d} FP={r['fp']:5d} "
                  f"FN={r['fn']:4d} nodes={r['nodes']:6d} div={r['pred_div']:4d} "
                  f"mp={r['multi_parent']:3d}")
    return summary


def fmt(summary, label=""):
    return (f"{label:28s} J={summary['wj']:.5f} TP={summary['tp']:5d} FP={summary['fp']:5d} "
            f"FN={summary['fn']:4d} nodes={summary['nodes']:7d} edges={summary['edges']:7d} "
            f"div={summary['pred_div']:5d} mp={summary['multi_parent']:4d}")
