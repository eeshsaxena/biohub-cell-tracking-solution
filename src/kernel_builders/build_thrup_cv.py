"""Build a full-pipeline RECALL-LEVER CV kernel (no submission cost).

Reuses the EXACT 0.917 pipeline (Kunal cells 0-4: detect + linker + repair +
patches), then on TRAIN movies (local .geff GT):
  1. detect ONCE per movie (cache dets), then
  2. re-run graph repair under several {seed-threshold x gap-fill} configs, and
  3. score the OFFICIAL adj_edge_jaccard + 0.1*division_jaccard per embryo,
using an inlined copy of the verified numpy scorer.

Lead hypothesis (see RECALL_RESEARCH.md): the winning pipeline's gap-fill is
snap-only, capped at 0.3% of nodes, and multi-frame is off -- yet midpoint
interpolation is 99.8% within 7um of the true cell. Aggressive synthesis fill
should recover interior single-frame misses (each worth 2 edges) near-free.

Output: printed CV table. Running this costs GPU time, NOT a submission slot.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
OUT_DIR = HERE / "thrup_cv"
OUT_DIR.mkdir(exist_ok=True)

src = json.loads(SRC_NB.read_text(encoding="utf-8"))
base_cells = [src["cells"][i] for i in (0, 1, 2, 3, 4)]  # full pipeline incl. patches

# Kaggle base image lacks zarr; needed here to read the .geff GT graphs.
INSTALL = r'''
import os, glob, subprocess, sys
def find_wheeldir(slug):
    for base in (f"/kaggle/input/{slug}", f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(base):
            return base
    hits = [p for p in glob.glob(f"/kaggle/input/**/{slug}", recursive=True) if os.path.isdir(p)]
    return hits[0] if hits else None
wd = find_wheeldir("biohub-zarr-wheels")
r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-index",
                    f"--find-links={wd}", "zarr"], capture_output=True, text=True)
print("zarr install rc", r.returncode)
if r.returncode:
    print(r.stderr[-800:])
import zarr; print("zarr", zarr.__version__)
'''
install_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": INSTALL}
base_cells = [install_cell] + base_cells

CV = r'''
# ===================== FULL-PIPELINE RECALL CV (train, local GT) =====================
import numpy as np, time, glob
from pathlib import Path
from collections import defaultdict
from scipy.optimize import linear_sum_assignment

TRAIN_DIR = Path(ROOT) / "train"
assert TRAIN_DIR.exists(), "no train dir under " + str(ROOT)

# ---------- inlined verified scorer (from kaggle/scoring.py) ----------
ADJ_ALPHA = 0.1
def read_geff_min(path):
    import zarr
    g = zarr.open_group(str(path), mode="r")
    ids = np.asarray(g["nodes/ids"][:]).astype(np.int64)
    t = np.asarray(g["nodes/props/t/values"][:]).astype(np.int64)
    z = np.asarray(g["nodes/props/z/values"][:]).astype(np.float64)
    y = np.asarray(g["nodes/props/y/values"][:]).astype(np.float64)
    x = np.asarray(g["nodes/props/x/values"][:]).astype(np.float64)
    try:
        e = np.asarray(g["edges/ids"][:]).astype(np.int64).reshape(-1, 2)
    except KeyError:
        e = np.zeros((0, 2), np.int64)
    n_est = float("nan")
    try:
        extra = dict(g.attrs).get("geff", {}).get("extra", {}) or {}
        if extra.get("estimated_number_of_nodes") is not None:
            n_est = float(extra["estimated_number_of_nodes"])
    except Exception:
        pass
    return {"ids": ids, "t": t, "pos": np.stack([z, y, x], 1), "edges": e, "n_est": n_est}

def match_nodes(pt, pp, gt_t, gt_pos, maxd=7.0):
    sc = SCALE; out = np.full(len(pt), -1, np.int64)
    if len(pt) == 0 or len(gt_t) == 0:
        return out
    for tt in np.unique(gt_t):
        pi = np.nonzero(pt == tt)[0]; gi = np.nonzero(gt_t == tt)[0]
        if len(pi) == 0 or len(gi) == 0:
            continue
        d = np.linalg.norm((pp[pi][:, None] * sc) - (gt_pos[gi][None] * sc), axis=2)
        cost = np.where(d <= maxd, d, 1e6)
        ri, ci = linear_sum_assignment(cost)
        for a, b in zip(ri, ci):
            if cost[a, b] < 5e5:
                out[pi[a]] = gi[b]
    return out

def eval_edges(pt, pp, pe, gt):
    match = match_nodes(pt, pp, gt["t"], gt["pos"])
    gi = {int(v): i for i, v in enumerate(gt["ids"])}; ng = len(gt["ids"])
    gout = np.zeros(ng, np.int64); gin = np.zeros(ng, np.int64); ges = set()
    for s, d in gt["edges"]:
        si, di = gi.get(int(s)), gi.get(int(d))
        if si is None or di is None:
            continue
        gout[si] += 1; gin[di] += 1; ges.add((si, di))
    edges = [(int(a), int(b)) for a, b in pe]
    seen = set(); dd = []
    for eid, (a, b) in enumerate(edges):
        if (a, b) in seen:
            continue
        seen.add((a, b)); dd.append((eid, a, b))
    step = [(eid, a, b) for eid, a, b in dd if pt[b] - pt[a] == 1]
    best = {}
    for eid, a, b in step:
        ma, mb = match[a], match[b]
        if ma >= 0 and mb >= 0:
            k = (int(ma), int(mb))
            if k not in best or eid < best[k]:
                best[k] = eid
    col = []
    for eid, a, b in step:
        ma, mb = match[a], match[b]
        if ma >= 0 and mb >= 0 and best[(int(ma), int(mb))] != eid:
            continue
        col.append((eid, a, b))
    per = {}
    for eid, a, _b in col:
        per.setdefault(a, []).append(eid)
    allow = {a: set(sorted(v)[:2]) for a, v in per.items()}
    cap = [(eid, a, b) for eid, a, b in col if eid in allow[a]]
    tp = 0; valid = 0
    for _e, a, b in cap:
        ma, mb = match[a], match[b]
        ov = ma >= 0 and gout[ma] > 0; iv = mb >= 0 and gin[mb] > 0
        if ov or iv:
            valid += 1
        if ma >= 0 and mb >= 0 and (int(ma), int(mb)) in ges:
            tp += 1
    return {"tp": tp, "fp": valid - tp, "fn": len(ges) - tp, "npred": len(pt),
            "nrec": float(len(set(int(m) for m in match if m >= 0)) / ng) if ng else 0.0}

def adj_of(er, n_est):
    ratio = (er["npred"] - n_est) / n_est if n_est > 0 else float("nan")
    den = er["tp"] + er["fp"] + er["fn"]
    j = er["tp"] / den if den else float("nan")
    adj = max(0.0, j * (1 - ADJ_ALPHA * ratio)) if (j == j and ratio == ratio) else float("nan")
    return j, adj, ratio, den

# division scorer (compact, mirrors scoring.evaluate_divisions)
def eval_div(pt, pp, pe, gt):
    match = match_nodes(pt, pp, gt["t"], gt["pos"])
    gi = {int(v): i for i, v in enumerate(gt["ids"])}; ng = len(gt["ids"])
    gc = defaultdict(list); gpar = defaultdict(list)
    for s, d in gt["edges"]:
        si, di = gi.get(int(s)), gi.get(int(d))
        if si is None or di is None:
            continue
        gc[si].append(di); gpar[di].append(si)
    gdiv = [i for i in range(ng) if len(gc[i]) >= 2]
    npred = len(pt); pc = defaultdict(list); ppar = defaultdict(list)
    for a, b in pe:
        pc[int(a)].append(int(b)); ppar[int(b)].append(int(a))
    pf = [i for i in range(npred) if len(pc[i]) >= 2]
    evalable = {f for f in pf if match[f] >= 0 and len(gc[int(match[f])]) >= 1}
    bip = defaultdict(set)
    for D in gdiv:
        pside = {D} | set(gpar[D]); lin = {}
        for li, c in enumerate(gc[D]):
            lin.setdefault(c, li)
            for g2 in gc[c]:
                lin.setdefault(g2, li)
        for F in pf:
            pfs = {F} | set(ppar[F])
            if not any(match[x] >= 0 and int(match[x]) in pside for x in pfs):
                continue
            lins = set()
            for c in pc[F]:
                for x in [c, *pc[c]]:
                    m = int(match[x])
                    if m >= 0 and m in lin:
                        lins.add(lin[m])
            if len(lins) >= 2:
                bip[D].add(F)
    mr = {}; ml = {}
    def aug(u, seen):
        for v in bip.get(u, ()):
            if v in seen:
                continue
            seen.add(v)
            if v not in mr or aug(mr[v], seen):
                ml[u] = v; mr[v] = u; return True
        return False
    for u in gdiv:
        aug(u, set())
    tp = len(ml); fp = len(evalable - set(ml.values())); fn = len(gdiv) - tp
    return {"dtp": tp, "dfp": fp, "dfn": fn}

# ---------- config-driven repair (cached dets -> graph) ----------
def _emit_arrays(nodes, edges):
    seen = set(); es = []
    for a, b in edges:
        if a == b or a not in nodes or b not in nodes or (a, b) in seen:
            continue
        seen.add((a, b)); es.append((a, b))
    used = set()
    for a, b in es:
        used.add(a); used.add(b)
    nids = sorted(used); idx = {n: i for i, n in enumerate(nids)}
    pt = np.array([nodes[n]["t"] for n in nids], np.int64)
    pp = np.array([nodes[n]["xyz"] for n in nids], float).reshape(-1, 3)
    pe = np.array([(idx[a], idx[b]) for a, b in es], np.int64).reshape(-1, 2)
    return pt, pp, pe

def _gap_fill_cfg(nodes, edges, cand, cand_sc, cand_trees, next_id, max_dt, gate, snap, mincand, cap_frac, synth):
    T = len(cand); succ = {}; pred = {}
    for a, b in edges:
        succ[a] = b; pred[b] = a
    by_t = defaultdict(list)
    for nid, n in nodes.items():
        by_t[n["t"]].append(nid)
    cand_used = [np.zeros(len(c), bool) for c in cand]
    max_gaps = max(1, int(cap_frac * len(nodes))); nadd = 0; BIG = 1e9
    for dt in range(2, max_dt + 2):        # dt=2 -> 1-frame gap ... dt=max_dt+1
        for t in range(T - dt):
            if nadd >= max_gaps:
                break
            ends = [g for g in by_t.get(t, []) if g not in succ and g in pred]
            starts = [g for g in by_t.get(t + dt, []) if g not in pred and g in succ]
            if not ends or not starts:
                continue
            P = np.asarray([nodes[g]["xyz"] for g in ends], float) * SCALE
            C = np.asarray([nodes[g]["xyz"] for g in starts], float) * SCALE
            D = np.sqrt(((P[:, None] - C[None]) ** 2).sum(2))
            cost = np.where(D > gate * dt, BIG, D)   # gate scales with gap length
            ri, ci = linear_sum_assignment(cost)
            props = sorted((float(D[r, c]), ends[r], starts[c]) for r, c in zip(ri, ci) if cost[r, c] < BIG)
            for d, ge, gs in props:
                if nadd >= max_gaps:
                    break
                if ge in succ or gs in pred:
                    continue
                pe_ = nodes[ge]["xyz"]; ps_ = nodes[gs]["xyz"]
                chain = []; ok = True
                for k in range(1, dt):
                    tk = t + k; interp = pe_ + (ps_ - pe_) * (k / dt); use = None
                    tree = cand_trees[tk] if 0 <= tk < len(cand_trees) else None
                    if tree is not None:
                        dist, idx = tree.query(interp * SCALE)
                        if dist <= snap and not cand_used[tk][idx] and cand_sc[tk][idx] >= mincand:
                            use = np.asarray(cand[tk][idx], float); cand_used[tk][idx] = True
                    if use is None:
                        if synth:
                            use = interp
                        else:
                            ok = False; break
                    chain.append((tk, use))
                if not ok:
                    continue
                prev = ge
                for tk, use in chain:
                    ng = next_id; next_id += 1
                    nodes[ng] = {"t": tk, "xyz": np.asarray(use, float)}
                    edges.append((prev, ng)); succ[prev] = ng; pred[ng] = prev; prev = ng
                edges.append((prev, gs)); succ[prev] = gs; pred[gs] = prev
                nadd += 1
    return next_id, nadd

def _link_fused(prev_xyz, curr_xyz, prev_vel, curr_velout, prev_sc, curr_sc):
    # Bidirectional cost: mean of forward (prev-heading vs curr) and backward
    # (prev vs curr-came-from) predicted distances + appearance sim, gated by raw
    # distance; two-pass tight->loose Hungarian (mirrors _link_sim structure).
    if len(prev_xyz) == 0 or len(curr_xyz) == 0:
        return []
    P = prev_xyz * SCALE[None, :]; C = curr_xyz * SCALE[None, :]
    pred_f = P + (0.5 * prev_vel if prev_vel is not None else 0.0)
    pred_b = C - (0.5 * curr_velout if curr_velout is not None else 0.0)
    N, M = len(P), len(C); BIG = 1e9
    sim = LINK_SIM_W * np.abs(_logit(prev_sc)[:, None] - _logit(curr_sc)[None])
    def _hun(pi, ci, gate):
        if len(pi) == 0 or len(ci) == 0:
            return []
        Draw = np.sqrt(((P[pi][:, None] - C[ci][None]) ** 2).sum(2))
        Df = np.sqrt(((pred_f[pi][:, None] - C[ci][None]) ** 2).sum(2))
        Db = np.sqrt(((P[pi][:, None] - pred_b[ci][None]) ** 2).sum(2))
        cost = np.where(Draw > gate, BIG, 0.5 * (Df + Db)) + np.where(Draw > gate, 0.0, sim[np.ix_(pi, ci)])
        ri, rc = linear_sum_assignment(cost)
        return [(int(pi[r]), int(ci[c])) for r, c in zip(ri, rc) if cost[r, c] < BIG]
    links = _hun(np.arange(N), np.arange(M), min(TIGHT_UM, MAX_LINK_UM))
    up = {p for p, _ in links}; uc = {c for _, c in links}
    fp = np.array([i for i in range(N) if i not in up], int); fc = np.array([j for j in range(M) if j not in uc], int)
    return links + _hun(fp, fc, MAX_LINK_UM)

def repair_cfg(dets, cfg):
    global MAX_LINK_UM, TIGHT_UM, LINK_SIM_W
    if cfg.get("max_link") is not None: MAX_LINK_UM = cfg["max_link"]
    if cfg.get("tight") is not None: TIGHT_UM = cfg["tight"]
    if cfg.get("sim_w") is not None: LINK_SIM_W = cfg["sim_w"]
    ut = cfg["unet_thr"]
    nodes = {}; frame_ids = []; cand = []; cand_sc = []; cand_trees = []; nid = 1; NSC = {}
    for t, (coords, scores) in enumerate(dets):
        coords = np.asarray(coords, float).reshape(-1, 3); scores = np.asarray(scores, float).reshape(-1)
        seeds = coords[scores >= ut]; seed_sc = scores[scores >= ut]
        cm = (scores >= CAND_THR) & (scores < ut)
        cand.append(coords[cm]); cand_sc.append(scores[cm])
        cand_trees.append(cKDTree(cand[-1] * SCALE) if len(cand[-1]) else None)
        ids = []
        for xyz, s_ in zip(seeds, seed_sc):
            nodes[nid] = {"t": t, "xyz": np.asarray(xyz, float)}; NSC[nid] = float(s_); ids.append(nid); nid += 1
        frame_ids.append(ids)
    def _fwd_pass():
        E = []; ve = {}
        for t in range(len(dets) - 1):
            P = np.asarray([nodes[g]["xyz"] for g in frame_ids[t]], float).reshape(-1, 3)
            C = np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 1]], float).reshape(-1, 3)
            if len(P) == 0 or len(C) == 0:
                continue
            pv = np.array([ve.get(g, np.zeros(3)) for g in frame_ids[t]])
            psc = np.array([NSC[g] for g in frame_ids[t]]); csc = np.array([NSC[g] for g in frame_ids[t + 1]])
            for pi, ci in _link_sim(P, C, pv if len(pv) else None, psc, csc):
                gp, gcc = frame_ids[t][pi], frame_ids[t + 1][ci]
                E.append((gp, gcc)); ve[gcc] = (C[ci] - P[pi]) * SCALE
        return E, ve
    edges = []; succ = {}; pred = {}; vel = {}
    if cfg.get("linker", "fwd") == "mutual":
        # NOVEL: forward and backward Hungarians use ASYMMETRIC costs (forward
        # extrapolates prev velocity), so their disagreement flags AMBIGUOUS links.
        # A wrong link costs FP+FN; NO link costs only the FN already lost -> pruning
        # ambiguous links should raise J even if it slightly lowers recall.
        keep_um = cfg.get("mutual_keep_um", 0.0)
        E1, ve1 = _fwd_pass()
        velprev = {}
        for a, b in E1: velprev[b] = ve1.get(b, np.zeros(3))
        for t in range(len(dets) - 1):
            P = np.asarray([nodes[g]["xyz"] for g in frame_ids[t]], float).reshape(-1, 3)
            C = np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 1]], float).reshape(-1, 3)
            if len(P) == 0 or len(C) == 0:
                continue
            pv = np.array([ve1.get(g, np.zeros(3)) for g in frame_ids[t]])
            psc = np.array([NSC[g] for g in frame_ids[t]]); csc = np.array([NSC[g] for g in frame_ids[t + 1]])
            fwd = _link_sim(P, C, pv if len(pv) else None, psc, csc)
            bwd = _link_sim(C, P, None, csc, psc)          # reverse direction, no velocity prior
            bset = {(j, i) for i, j in bwd}                # -> (idx_in_P, idx_in_C)
            for pi, ci in fwd:
                d = float(np.linalg.norm((C[ci] - P[pi]) * SCALE))
                if (pi, ci) not in bset and d > keep_um:
                    continue                                # ambiguous -> prune
                gp, gcc = frame_ids[t][pi], frame_ids[t + 1][ci]
                edges.append((gp, gcc)); succ[gp] = gcc; pred[gcc] = gp; vel[gcc] = (C[ci] - P[pi]) * SCALE
    elif cfg.get("linker", "fwd") == "bidir":
        # pass 1: forward link to estimate motion; pass 2: re-link with fused
        # forward(prev-heading) + backward(curr-came-from) cost for edge precision.
        E1, ve1 = _fwd_pass()
        velout = {}
        for a, b in E1:
            velout[a] = ve1.get(b, np.zeros(3))   # a's OUT-velocity == vel INTO its successor b
        for t in range(len(dets) - 1):
            P = np.asarray([nodes[g]["xyz"] for g in frame_ids[t]], float).reshape(-1, 3)
            C = np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 1]], float).reshape(-1, 3)
            if len(P) == 0 or len(C) == 0:
                continue
            pv = np.array([ve1.get(g, np.zeros(3)) for g in frame_ids[t]])
            cvo = np.array([velout.get(g, np.zeros(3)) for g in frame_ids[t + 1]])
            psc = np.array([NSC[g] for g in frame_ids[t]]); csc = np.array([NSC[g] for g in frame_ids[t + 1]])
            for pi, ci in _link_fused(P, C, pv, cvo, psc, csc):
                gp, gcc = frame_ids[t][pi], frame_ids[t + 1][ci]
                edges.append((gp, gcc)); succ[gp] = gcc; pred[gcc] = gp; vel[gcc] = (C[ci] - P[pi]) * SCALE
    else:
        for t in range(len(dets) - 1):
            P = np.asarray([nodes[g]["xyz"] for g in frame_ids[t]], float).reshape(-1, 3)
            C = np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 1]], float).reshape(-1, 3)
            if len(P) == 0 or len(C) == 0:
                continue
            prev_vel = np.array([vel.get(g, np.zeros(3)) for g in frame_ids[t]])
            psc = np.array([NSC[g] for g in frame_ids[t]]); csc = np.array([NSC[g] for g in frame_ids[t + 1]])
            for pi, ci in _link_sim(P, C, prev_vel if len(prev_vel) else None, psc, csc):
                gp, gcc = frame_ids[t][pi], frame_ids[t + 1][ci]
                edges.append((gp, gcc)); succ[gp] = gcc; pred[gcc] = gp; vel[gcc] = (C[ci] - P[pi]) * SCALE
    nid, ngap = _gap_fill_cfg(nodes, edges, cand, cand_sc, cand_trees, nid,
                              cfg["max_dt"], cfg["gate"], cfg["snap"], cfg["mincand"], cfg["cap"], cfg["synth"])
    global SHORT_MIN
    if cfg.get("short_min") is not None: SHORT_MIN = cfg["short_min"]
    nodes, edges = _short_filter(nodes, edges)
    _linefit(nodes, edges)
    global DIV_DIVERGE_UM, DIV_GLOBAL_CAP, DIV_SISTER_UM
    DIV_DIVERGE_UM = cfg.get("div_diverge", DIV_DIVERGE_UM)
    DIV_GLOBAL_CAP = cfg.get("div_cap", DIV_GLOBAL_CAP)
    DIV_SISTER_UM = cfg.get("div_sister", DIV_SISTER_UM)
    ndiv = _add_safe_divisions(nodes, edges)
    return _emit_arrays(nodes, edges), ngap, ndiv

# ---------- run CV ----------
# gate is PER-FRAME-STEP: total end->start distance allowed = gate*dt.
# base gate 4.5 * dt(=2) = 9.0um == the pipeline's flat GAP1_GATE_UM, so base
# reproduces the 0.917 family exactly (sanity check).
# v4: hold the CV-winning avg+fill_synth1 base; vary the DIVISION gate (real GT
# divergence median 1.70um << the current 2.25um gate, which rejects real mitoses)
# and a longer-gap variant. Division term is 0.1-weighted headroom.
# v6: isolate the LINKER lever (biggest remaining headroom: fill1 detection recall
# ~0.978 -> edge ceiling ~0.956, but edge term ~0.87 -> ~0.09 lost in linking).
# All on the CV-winning fill1+div10 base; compare forward vs bidirectional linker.
# v7: SHORT_MIN sweep on the LB-WINNING fill1 base (fill + SHIPPED div 2.25).
# Local GT modelling: at our 2.2% miss rate short_filter(6) deletes ~1.5% of GT
# edges (0.9563 -> 0.9444). Aggressive gap-fill now JOINS fragments, so the
# tradeoff differs from the public pipelines that standardised on 6 pre-fill.
# Read the adjJ (edge) column — the CV is reliable for edges, not divisions.
_F = dict(unet_thr=0.15, max_dt=1, gate=4.5, snap=3.2, mincand=0.10, cap=0.08, synth=True,
          div_diverge=2.25, div_sister=15.0, linker="fwd", short_min=6, max_link=8.0)
# v10 NOVEL LEVER — precision, not recall. Implied FP=245-391 vs only 73 steals, so
# most FPs are WRONG-INCOMING edges (scoring counts an edge if the SOURCE or the
# TARGET matched). A wrong link costs FP+FN; NO link costs only the FN already lost
# => selectively PRUNING ambiguous links should raise J. Mutual-consistency
# (forward Hungarian AND backward Hungarian agree) flags the ambiguous ones.
# mutual_keep_um = always keep a non-mutual link shorter than this (protects TPs).
CONFIGS = [
    {"name": "thr0.15 (base)", **_F, "linker": "accel", "accel_bonus": 0.80},
    {"name": "thr0.20", **dict(_F, unet_thr=0.20), "linker": "accel", "accel_bonus": 0.80},
    {"name": "thr0.25", **dict(_F, unet_thr=0.25), "linker": "accel", "accel_bonus": 0.80},
    {"name": "thr0.30", **dict(_F, unet_thr=0.30), "linker": "accel", "accel_bonus": 0.80},
    {"name": "thr0.20 cap0.12", **dict(_F, unet_thr=0.20, cap=0.12), "linker": "accel", "accel_bonus": 0.80},
]

N_PER_EMBRYO = 5
FRAME_STRIDE = 1          # MUST be 1: GT edges are consecutive-frame; striding drops them all
TIME_BUDGET_S = 6 * 3600
geffs = sorted(TRAIN_DIR.glob("*.geff"))
by_emb = {}
for gp in geffs:
    zp = gp.with_suffix(".zarr")
    if not zp.exists():
        continue
    g = read_geff_min(gp)
    if len(g["edges"]) < 20:
        continue
    by_emb.setdefault(gp.name.split("_")[0], []).append((len(g["ids"]), gp, zp))
sel = []
for emb, lst in sorted(by_emb.items()):
    lst.sort(reverse=True); sel += [(emb,) + x[1:] for x in lst[:N_PER_EMBRYO]]
print("selected", len(sel), "movies:", {k: min(len(v), N_PER_EMBRYO) for k, v in by_emb.items()})

# ---- detection variants: compute the 3 branch heatmaps ONCE, derive avg + union ----
def _branch_heatmaps(vol):
    hs = []
    for models, ws, pp in _BRANCHES:
        x = pool_norm(vol, pp); acc = None
        for i in _FLIP_VIEWS:
            xv = np.ascontiguousarray(_flip(x, i))
            with torch.no_grad():
                lg = None
                for m, w in zip(models, ws):
                    l = m(torch.from_numpy(xv)[None, None].to(DEVICE))[0, 0].float().cpu().numpy()
                    lg = w * l if lg is None else lg + w * l
            lg = _flip(lg, i)
            acc = lg if acc is None else acc + lg
        hs.append(1.0 / (1.0 + np.exp(-(acc / len(_FLIP_VIEWS)))))
    return hs

def _peaks(h, vol, thr):
    pk = peak_local_max(h, min_distance=1, threshold_abs=thr, exclude_border=False)
    if len(pk) == 0:
        return np.zeros((0, 3)), np.zeros(0)
    sc = h[pk[:, 0], pk[:, 1], pk[:, 2]].astype(float)
    coords = pk.astype(float)
    coords[:, 1] = coords[:, 1] * POOL + (POOL - 1) / 2
    coords[:, 2] = coords[:, 2] * POOL + (POOL - 1) / 2
    ref = np.array([_refine(vol, c)[0] for c in coords])
    return ref, sc

def detect_both(vol):
    hs = _branch_heatmaps(vol)
    hmean = hs[0] if len(hs) == 1 else np.mean(hs, axis=0)
    ca, sa = _peaks(hmean, vol, DETECT_THRESH)
    if len(ca):
        ca, sa = _physical_nms(ca, sa, NMS_UM)
    cc = []; ss = []
    for h in hs:
        c, s = _peaks(h, vol, DETECT_THRESH)
        if len(c):
            cc.append(c); ss.append(s)
    if cc:
        C = np.concatenate(cc); S = np.concatenate(ss); cu, su = _physical_nms(C, S, NMS_UM)
    else:
        cu, su = np.zeros((0, 3)), np.zeros(0)
    return (ca, sa), (cu, su)

VARIANTS = ["avg"]   # union lost on the edge metric in v3; div-lever CV uses avg only
rows = {emb: {v: {c["name"]: {"tp": 0, "fp": 0, "fn": 0, "npred": 0, "nest": 0.0, "nrec": [],
              "dtp": 0, "dfp": 0, "dfn": 0} for c in CONFIGS} for v in VARIANTS} for emb in by_emb}
t_start = time.time()
for emb, gp, zp in sel:
    if time.time() - t_start > TIME_BUDGET_S:
        print("TIME BUDGET hit"); break
    gt = read_geff_min(gp)
    meta = read_array_meta(zp); T = meta["shape"][0]
    present = [t for t in range(T) if (Path(zp) / "0" / "c" / str(t) / "0" / "0" / "0").exists()]
    Tmax = (max(present) + 1) if present else 0
    frames = list(range(0, Tmax, FRAME_STRIDE))
    fidx = {f: i for i, f in enumerate(frames)}
    keep = np.isin(gt["t"], frames)
    gt_s = {"ids": gt["ids"][keep],
            "t": np.array([fidx[int(t)] for t in gt["t"][keep]], np.int64),
            "pos": gt["pos"][keep], "edges": [], "n_est": gt["n_est"]}
    idset = set(int(v) for v in gt_s["ids"])
    for s, d in gt["edges"]:
        if int(s) in idset and int(d) in idset:
            gt_s["edges"].append((int(s), int(d)))
    n_est_scaled = gt["n_est"] * (len(frames) / max(1, Tmax))
    t0 = time.time()
    da = []
    for f in frames:
        da.append(detect(load_volume(zp, f, meta)))   # cell-3 avg TTA detect
        gc.collect()
    for vname, dets in [("avg", da)]:
        for c in CONFIGS:
            (pt, pp, pe), ngap, ndiv = repair_cfg(dets, c)
            er = eval_edges(pt, pp, pe, gt_s); dv = eval_div(pt, pp, pe, gt_s)
            r = rows[emb][vname][c["name"]]
            r["tp"] += er["tp"]; r["fp"] += er["fp"]; r["fn"] += er["fn"]
            r["npred"] += er["npred"]; r["nest"] += n_est_scaled; r["nrec"].append(er["nrec"])
            r["dtp"] += dv["dtp"]; r["dfp"] += dv["dfp"]; r["dfn"] += dv["dfn"]
    b = rows[emb]["avg"][CONFIGS[0]["name"]]; _j, ab, _r, _d = adj_of({"tp": b["tp"], "fp": b["fp"], "fn": b["fn"], "npred": b["npred"]}, b["nest"])
    print("  %s %s: %s adj=%.4f (%.0fs)" % (emb, gp.stem, CONFIGS[0]["name"], ab, time.time() - t0))

def _score_row(r):
    j, adj, ratio, den = adj_of({"tp": r["tp"], "fp": r["fp"], "fn": r["fn"], "npred": r["npred"]}, r["nest"])
    dden = r["dtp"] + r["dfp"] + r["dfn"]
    divj = r["dtp"] / dden if dden else float("nan")
    score = adj + (0.1 * divj if divj == divj else 0.0)
    rec = float(np.mean(r["nrec"])) if r["nrec"] else float("nan")
    return j, adj, divj, score, rec

print("\n================ CV: adj_edge_jaccard + 0.1*div_jaccard ================")
for emb in sorted(rows):
    for v in VARIANTS:
        print("---- embryo", emb, "| detection:", v, "----")
        print("  %-14s %8s %8s %8s %8s %8s" % ("config", "edgeJ", "adjJ", "divJ", "SCORE", "recall"))
        for c in CONFIGS:
            j, adj, divj, score, rec = _score_row(rows[emb][v][c["name"]])
            print("  %-14s %8.4f %8.4f %8.4f %8.4f %8.4f" % (c["name"], j, adj, divj, score, rec))

print("\n================ POOLED (both embryos) ================")
print("  %-4s %-14s %8s %8s %8s" % ("det", "config", "adjJ", "divJ", "SCORE"))
best = None
for v in VARIANTS:
    for c in CONFIGS:
        agg = {"tp": 0, "fp": 0, "fn": 0, "npred": 0, "nest": 0.0, "dtp": 0, "dfp": 0, "dfn": 0, "nrec": []}
        for e in rows:
            r = rows[e][v][c["name"]]
            for k in ("tp", "fp", "fn", "npred", "nest", "dtp", "dfp", "dfn"):
                agg[k] += r[k]
        j, adj, divj, score, rec = _score_row(agg)
        print("  %-4s %-14s %8.4f %8.4f %8.4f" % (v, c["name"], adj, divj, score))
        if best is None or score > best[0]:
            best = (score, v, c["name"])
print("\nBEST pooled:", best)
print("DECISION: submit BEST that also beats avg/base on BOTH embryos. avg/base should reproduce ~0.917.")
'''

cv_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": CV}
nb = dict(src); nb["cells"] = base_cells + [cv_cell]
nb_path = OUT_DIR / "biohub-thrup-cv.ipynb"
nb_path.write_text(json.dumps(nb), encoding="utf-8")
meta = {
    "id": "eeshsaxena/biohub-thrup-cv",
    "title": "Biohub thrup cv",
    "code_file": "biohub-thrup-cv.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": ["gpu"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models", "eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path, "| cells", len(nb["cells"]))
