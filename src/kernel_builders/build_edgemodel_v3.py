"""Build a LEARNED EDGE-ASSOCIATION RANKER CV kernel (no submission cost).

Copied from build_accel_cv.py (itself build_recall_cv.py + the t+2 accel linker),
which supplies the exact 0.917 pipeline cells, `_link_sim`/`_link_accel`,
`repair_cfg`, `match_nodes` and the inlined numpy scorer.

WHY: the edge term is 0.893 at edge RECALL 0.954, so the gap is edge PRECISION
(~0.93). Geometric mutual-consistency pruning failed (it needs >52.8% precision on
the pruned set). A LEARNED ranker is the discriminator that can reach it, and unlike
the division detector there is no labeling wall: every candidate edge in every
train movie is labelled by the .geff GT.

WHAT THIS KERNEL DOES
  1. detect ONCE per train movie (cached),
  2. generate candidate edges (source @t -> every target @t+1 inside the 8um gate),
  3. compute the recovered public 22-feature contract (minus edge_prob, which needs
     an edge transformer we do not have) + a few computable extras,
  4. LABEL each candidate from the .geff GT via a per-timepoint 7um Hungarian node
     match (positive iff the matched GT source/target form a real consecutive edge),
  5. train a HistGradientBoosting classifier with MOVIE-LEVEL out-of-fold splits,
  6. apply it in two modes and score the official adjJ + 0.1*divJ per embryo:
       'rescue' = low_margin_top2_rescue (surgical: only rows whose top-2 cost
                  margin < 0.35um; if the ranker prefers the runner-up by >= 0.15,
                  subtract min(0.20, advantage) from that candidate's cost)
       'full'   = cost -= LEARNED_BONUS * ranker_prob everywhere
  against an UNTOUCHED control (accel b0.80, CV pooled 0.8732).

Output: printed OOF AUC / group top-1 tables + the per-arm CV table.
Running this costs GPU time, NOT a submission slot.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
OUT_DIR = HERE / "edgemodel_v3"
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

def _link_accel(prev_xyz, curr_xyz, next_xyz, prev_vel, prev_sc, curr_sc, amax, abonus):
    """Assignment cost with a t+2 ACCELERATION LOOKAHEAD bonus.

    A steal links to a NEIGHBOURING cell (measured: 8.76um away while cells move
    ~1.8um/frame). The stolen target keeps its OWN velocity, so continuing the
    proposed edge (i@t -> j@t+1) to t+2 requires a large acceleration. A true edge
    continues smoothly. Frame-pair-local Hungarian cannot see this; t+2 can.
    residual = min_k || (k - j) - (j - i) ||  over nodes k at t+2 near the constant-
    velocity prediction; bonus = abonus * max(0, 1 - residual/amax), subtracted from cost.
    """
    if len(prev_xyz) == 0 or len(curr_xyz) == 0:
        return []
    P = prev_xyz * SCALE[None, :]; C = curr_xyz * SCALE[None, :]
    pred = P + (0.5 * prev_vel if prev_vel is not None else 0.0)
    N, M = len(P), len(C); BIG = 1e9
    sim = LINK_SIM_W * np.abs(_logit(prev_sc)[:, None] - _logit(curr_sc)[None])
    tree2 = cKDTree(next_xyz * SCALE[None, :]) if (next_xyz is not None and len(next_xyz)) else None
    def _hun(pi, ci, gate):
        if len(pi) == 0 or len(ci) == 0:
            return []
        Draw = np.sqrt(((P[pi][:, None] - C[ci][None]) ** 2).sum(2))
        D = np.sqrt(((pred[pi][:, None] - C[ci][None]) ** 2).sum(2))
        cost = np.where(Draw > gate, BIG, D) + np.where(Draw > gate, 0.0, sim[np.ix_(pi, ci)])
        if tree2 is not None and abonus > 0:
            gi, gj = np.nonzero(Draw <= gate)          # only gated pairs (cheap)
            if len(gi):
                # constant-velocity prediction into t+2: 2*C[j] - P[i]
                predict2 = 2.0 * C[ci][gj] - P[pi][gi]
                resid, _ = tree2.query(predict2)
                bonus = abonus * np.clip(1.0 - resid / amax, 0.0, None)
                cost[gi, gj] -= bonus
        ri, rc = linear_sum_assignment(cost)
        return [(int(pi[r]), int(ci[c])) for r, c in zip(ri, rc) if cost[r, c] < BIG]
    links = _hun(np.arange(N), np.arange(M), min(TIGHT_UM, MAX_LINK_UM))
    up = {p for p, _ in links}; uc = {c for _, c in links}
    fp = np.array([i for i in range(N) if i not in up], int); fc = np.array([j for j in range(M) if j not in uc], int)
    return links + _hun(fp, fc, MAX_LINK_UM)

# ===================== LEARNED EDGE-ASSOCIATION RANKER =====================
# A candidate is (source i @ t -> target j @ t+1) with raw physical distance
# <= max_link. EVERY feature below is derived from the DETECTIONS and the BASE
# (accel) linker graph only -- nothing reads the GT, so all of it is available
# at test time. Labels come from the .geff GT and are used ONLY for training.
FEAT_NAMES = [
    # --- the recovered public 22-feature contract, minus edge_prob (that needs
    #     the public edge transformer we do not have; score_source/score_target/
    #     abs_logit_diff are the computable stand-in, and are exactly what our
    #     linker already uses as its appearance term) ---
    "source_in_degree", "source_out_degree", "target_in_degree", "target_out_degree",
    "source_density_7um", "target_density_7um",
    "raw_distance_um", "motion_distance_um", "motion_gain_um",
    "candidate_rank", "candidate_count",
    "dz_um", "dy_um", "dx_um", "abs_dz_um", "abs_dy_um", "abs_dx_um",
    "velocity_um", "source_frame_size_norm", "target_frame_size_norm", "t_norm",
    # --- computable extras (detections / base graph only) ---
    "score_source", "score_target", "abs_logit_diff",
    "link_cost_um", "cost_rank", "cost_margin_um", "row_top2_margin_um",
    "accel_resid_um", "target_candidate_rank", "target_candidate_count",
]
FCOL = {n: k for k, n in enumerate(FEAT_NAMES)}
COST_COL = FCOL["link_cost_um"]; TOP2_COL = FCOL["row_top2_margin_um"]


def _seed_frames(dets, ut):
    """Per-frame (xyz, score) of SEED nodes -- identical order to repair_cfg."""
    F = []
    for coords, scores in dets:
        coords = np.asarray(coords, float).reshape(-1, 3)
        scores = np.asarray(scores, float).reshape(-1)
        m = scores >= ut
        F.append((coords[m], scores[m]))
    return F


def _grp_rank(keys, vals):
    """Rank (0-based) of each row inside its `keys` group, ordered by `vals` asc."""
    n = len(keys)
    if n == 0:
        return np.zeros(0, np.int64)
    o = np.lexsort((vals, keys)); sk = keys[o]
    first = np.empty(n, bool); first[0] = True
    if n > 1:
        first[1:] = sk[1:] != sk[:-1]
    start = np.maximum.accumulate(np.where(first, np.arange(n), 0))
    r = np.empty(n, np.int64); r[o] = np.arange(n) - start
    return r


def build_pair_features(dets, cfg):
    """-> list (len T-1) of dict(ii, jj, X) with X float32 (n_pairs, n_feats)."""
    global MAX_LINK_UM, TIGHT_UM, LINK_SIM_W
    MAX_LINK_UM = float(cfg["max_link"])
    if cfg.get("tight") is not None:
        TIGHT_UM = cfg["tight"]
    if cfg.get("sim_w") is not None:
        LINK_SIM_W = cfg["sim_w"]
    ut = cfg["unet_thr"]; gate = float(cfg["max_link"])
    amax = float(cfg.get("accel_max", 4.0)); abonus = float(cfg.get("accel_bonus", 0.0))
    F = _seed_frames(dets, ut); T = len(F)
    nper = np.array([len(f[0]) for f in F], float)
    nmax = max(1.0, float(nper.max()) if len(nper) else 1.0)
    tden = float(max(1, T - 1))

    # ---- base graph: EXACTLY the control linker, giving in-velocities + degrees
    vel = [np.zeros((len(F[t][0]), 3)) for t in range(T)]
    indeg = [np.zeros(len(F[t][0]), np.float32) for t in range(T)]
    outdeg = [np.zeros(len(F[t][0]), np.float32) for t in range(T)]
    for t in range(T - 1):
        P, psc = F[t]; C, csc = F[t + 1]
        if len(P) == 0 or len(C) == 0:
            continue
        N2 = F[t + 2][0] if t + 2 < T else None
        for i, j in _link_accel(P, C, N2, vel[t] if len(vel[t]) else None, psc, csc, amax, abonus):
            vel[t + 1][j] = (C[j] - P[i]) * SCALE
            outdeg[t][i] += 1.0; indeg[t + 1][j] += 1.0

    # ---- local density: # OTHER seeds within 7um at the same timepoint
    dens = []
    for t in range(T):
        pts = F[t][0] * SCALE[None, :]
        if len(pts) == 0:
            dens.append(np.zeros(0, np.float32)); continue
        tr = cKDTree(pts)
        try:
            c = np.asarray(tr.query_ball_point(pts, 7.0, return_length=True), float)
        except TypeError:
            c = np.array([len(z) for z in tr.query_ball_point(pts, 7.0)], float)
        dens.append((c - 1.0).astype(np.float32))

    blocks = []
    for t in range(T - 1):
        P, psc = F[t]; C, csc = F[t + 1]
        if len(P) == 0 or len(C) == 0:
            blocks.append(None); continue
        Pp = P * SCALE[None, :]; Cp = C * SCALE[None, :]
        Draw = np.sqrt(((Pp[:, None] - Cp[None]) ** 2).sum(2))
        ii, jj = np.nonzero(Draw <= gate)
        if len(ii) == 0:
            blocks.append(None); continue
        d_raw = Draw[ii, jj]
        predp = Pp + 0.5 * vel[t]
        d_mot = np.sqrt(((predp[ii] - Cp[jj]) ** 2).sum(1))
        dvec = Cp[jj] - Pp[ii]
        lgd = np.abs(_logit(psc)[ii] - _logit(csc)[jj])
        if t + 2 < T and len(F[t + 2][0]):
            tr2 = cKDTree(F[t + 2][0] * SCALE[None, :])
            resid, _ = tr2.query(2.0 * Cp[jj] - Pp[ii])
        else:
            resid = np.full(len(ii), 2.0 * amax)
        cost = d_mot + LINK_SIM_W * lgd - abonus * np.clip(1.0 - resid / amax, 0.0, None)
        cnt = np.bincount(ii, minlength=len(P)).astype(np.float32)
        tcnt = np.bincount(jj, minlength=len(C)).astype(np.float32)
        rank = _grp_rank(ii, d_raw); trank = _grp_rank(jj, d_raw); crank = _grp_rank(ii, cost)
        # per-source best / runner-up cost (feature only; the linker recomputes
        # its own margin inside each Hungarian pass)
        best = np.full(len(P), np.inf); second = np.full(len(P), np.inf)
        o = np.lexsort((cost, ii)); si = ii[o]; sc_ = cost[o]
        fst = np.empty(len(o), bool); fst[0] = True
        if len(o) > 1:
            fst[1:] = si[1:] != si[:-1]
        best[si[fst]] = sc_[fst]
        i2 = np.nonzero(fst)[0] + 1
        i2 = i2[i2 < len(o)]
        i2 = i2[~fst[i2]]
        if len(i2):
            second[si[i2]] = sc_[i2]
        b_ii = best[ii]; s_ii = second[ii]
        margin = cost - b_ii
        top2 = np.where(np.isfinite(s_ii), s_ii - b_ii, 99.0)

        X = np.zeros((len(ii), len(FEAT_NAMES)), np.float32)
        X[:, FCOL["source_in_degree"]] = indeg[t][ii]
        X[:, FCOL["source_out_degree"]] = outdeg[t][ii]
        X[:, FCOL["target_in_degree"]] = indeg[t + 1][jj]
        X[:, FCOL["target_out_degree"]] = outdeg[t + 1][jj]
        X[:, FCOL["source_density_7um"]] = dens[t][ii]
        X[:, FCOL["target_density_7um"]] = dens[t + 1][jj]
        X[:, FCOL["raw_distance_um"]] = d_raw
        X[:, FCOL["motion_distance_um"]] = d_mot
        X[:, FCOL["motion_gain_um"]] = d_raw - d_mot
        X[:, FCOL["candidate_rank"]] = rank
        X[:, FCOL["candidate_count"]] = cnt[ii]
        X[:, FCOL["dz_um"]] = dvec[:, 0]
        X[:, FCOL["dy_um"]] = dvec[:, 1]
        X[:, FCOL["dx_um"]] = dvec[:, 2]
        X[:, FCOL["abs_dz_um"]] = np.abs(dvec[:, 0])
        X[:, FCOL["abs_dy_um"]] = np.abs(dvec[:, 1])
        X[:, FCOL["abs_dx_um"]] = np.abs(dvec[:, 2])
        X[:, FCOL["velocity_um"]] = np.sqrt((vel[t] ** 2).sum(1))[ii]
        X[:, FCOL["source_frame_size_norm"]] = len(P) / nmax
        X[:, FCOL["target_frame_size_norm"]] = len(C) / nmax
        X[:, FCOL["t_norm"]] = t / tden
        X[:, FCOL["score_source"]] = psc[ii]
        X[:, FCOL["score_target"]] = csc[jj]
        X[:, FCOL["abs_logit_diff"]] = lgd
        X[:, FCOL["link_cost_um"]] = cost
        X[:, FCOL["cost_rank"]] = crank
        X[:, FCOL["cost_margin_um"]] = margin
        X[:, FCOL["row_top2_margin_um"]] = top2
        X[:, FCOL["accel_resid_um"]] = resid
        X[:, FCOL["target_candidate_rank"]] = trank
        X[:, FCOL["target_candidate_count"]] = tcnt[jj]
        blocks.append({"ii": ii.astype(np.int32), "jj": jj.astype(np.int32), "X": X,
                       "np": len(P), "nc": len(C)})
    return blocks


def label_blocks(blocks, dets, cfg, gt):
    """Label every candidate against the .geff GT.

    Node matching = per-timepoint Hungarian at 7um in PHYSICAL units (match_nodes).
    A candidate is POSITIVE iff the source's matched GT node and the target's
    matched GT node form a real consecutive GT edge.  A candidate is TRAINABLE
    (`known`) iff the source matched a GT node that HAS an outgoing consecutive
    GT edge -- only then do we actually know the answer for that source.
    """
    F = _seed_frames(dets, cfg["unet_thr"]); T = len(F)
    lens = [len(F[t][0]) for t in range(T)]
    off = np.concatenate([[0], np.cumsum(lens)]).astype(np.int64)
    if off[-1] == 0:
        return [None] * len(blocks)
    pt = np.concatenate([np.full(lens[t], t, np.int64) for t in range(T)])
    pp = np.concatenate([F[t][0].reshape(-1, 3) for t in range(T)]).reshape(-1, 3)
    match = match_nodes(pt, pp, gt["t"], gt["pos"])
    gi = {int(v): i for i, v in enumerate(gt["ids"])}
    NG = max(1, len(gt["ids"]))
    gout = np.zeros(NG, np.int64); keys = []
    for s, d in gt["edges"]:
        si, di = gi.get(int(s)), gi.get(int(d))
        if si is None or di is None:
            continue
        if int(gt["t"][di]) != int(gt["t"][si]) + 1:
            continue
        gout[si] += 1; keys.append(si * NG + di)
    gkeys = np.sort(np.array(keys, np.int64)) if keys else np.zeros(0, np.int64)
    out = []
    for t, b in enumerate(blocks):
        if b is None:
            out.append(None); continue
        ms = match[off[t] + b["ii"]]; mt = match[off[t + 1] + b["jj"]]
        valid = (ms >= 0) & (mt >= 0)
        k = np.where(valid, np.maximum(ms, 0).astype(np.int64) * NG + np.maximum(mt, 0), -1)
        if len(gkeys):
            idx = np.clip(np.searchsorted(gkeys, k), 0, len(gkeys) - 1)
            y = (valid & (gkeys[idx] == k)).astype(np.int8)
        else:
            y = np.zeros(len(k), np.int8)
        known = (ms >= 0) & (gout[np.maximum(ms, 0)] > 0)
        out.append({"y": y, "known": known, "src": (off[t] + b["ii"]).astype(np.int64)})
    return out


def _link_accel_pr(prev_xyz, curr_xyz, next_xyz, prev_vel, prev_sc, curr_sc,
                   amax, abonus, PR, mode, low_margin, min_adv, max_sub, learned_bonus):
    """_link_accel with the LEARNED RANKER folded into the assignment cost.

    mode 'rescue' (low_margin_top2_rescue) -- SURGICAL: the cost matrix is left
      untouched except on rows whose top-2 cost margin < low_margin; there, if the
      ranker prefers the runner-up by >= min_adv, subtract min(max_sub, advantage)
      from the runner-up's cost.
    mode 'full' -- cost -= learned_bonus * ranker_prob on every gated pair.
    """
    if len(prev_xyz) == 0 or len(curr_xyz) == 0:
        return []
    P = prev_xyz * SCALE[None, :]; C = curr_xyz * SCALE[None, :]
    pred = P + (0.5 * prev_vel if prev_vel is not None else 0.0)
    N, M = len(P), len(C); BIG = 1e9
    sim = LINK_SIM_W * np.abs(_logit(prev_sc)[:, None] - _logit(curr_sc)[None])
    tree2 = cKDTree(next_xyz * SCALE[None, :]) if (next_xyz is not None and len(next_xyz)) else None

    def _hun(pi, ci, gate):
        if len(pi) == 0 or len(ci) == 0:
            return []
        Draw = np.sqrt(((P[pi][:, None] - C[ci][None]) ** 2).sum(2))
        D = np.sqrt(((pred[pi][:, None] - C[ci][None]) ** 2).sum(2))
        gated = Draw <= gate
        cost = np.where(gated, D, BIG) + np.where(gated, sim[np.ix_(pi, ci)], 0.0)
        if tree2 is not None and abonus > 0:
            gi_, gj_ = np.nonzero(gated)
            if len(gi_):
                predict2 = 2.0 * C[ci][gj_] - P[pi][gi_]
                resid, _ = tree2.query(predict2)
                cost[gi_, gj_] -= abonus * np.clip(1.0 - resid / amax, 0.0, None)
        if PR is not None:
            sub = PR[np.ix_(pi, ci)]
            if mode == "full":
                cost = cost - learned_bonus * np.where(gated, sub, 0.0)
            elif mode == "rescue" and cost.shape[1] >= 2:
                cm = np.where(gated, cost, np.inf)
                part = np.argpartition(cm, 1, axis=1)[:, :2]
                rows = np.arange(cm.shape[0])
                a = cm[rows, part[:, 0]]; b = cm[rows, part[:, 1]]
                swap = b < a
                j1 = np.where(swap, part[:, 1], part[:, 0])
                j2 = np.where(swap, part[:, 0], part[:, 1])
                c1 = cm[rows, j1]; c2 = cm[rows, j2]
                adv = sub[rows, j2] - sub[rows, j1]
                fin = np.isfinite(c1) & np.isfinite(c2)
                gap = np.where(fin, c2, 0.0) - np.where(fin, c1, 0.0)
                hit = fin & (gap < low_margin) & (adv >= min_adv)
                if hit.any():
                    r = rows[hit]; cjj = j2[hit]
                    cost[r, cjj] = cost[r, cjj] - np.minimum(max_sub, adv[hit])
        ri, rc = linear_sum_assignment(cost)
        return [(int(pi[r]), int(ci[c])) for r, c in zip(ri, rc) if cost[r, c] < BIG / 2]

    links = _hun(np.arange(N), np.arange(M), min(TIGHT_UM, MAX_LINK_UM))
    up = {p for p, _ in links}; uc = {c for _, c in links}
    fp = np.array([i for i in range(N) if i not in up], int)
    fc = np.array([j for j in range(M) if j not in uc], int)
    return links + _hun(fp, fc, MAX_LINK_UM)


def repair_cfg(dets, cfg, pr=None):
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
    if cfg.get("linker", "fwd") == "accel_rank":
        # identical to "accel" except the cost matrix is modified by the LEARNED
        # ranker probabilities `pr[t]` (dense n_t x n_t+1, 0 outside the gate).
        amax = cfg.get("accel_max", 4.0); abonus = cfg.get("accel_bonus", 0.20)
        mode = cfg.get("rank_mode", "rescue")
        lm = cfg.get("low_margin", 0.35); ma = cfg.get("min_adv", 0.15)
        ms = cfg.get("max_sub", 0.20); lb = cfg.get("learned_bonus", 1.0)
        for t in range(len(dets) - 1):
            P = np.asarray([nodes[g]["xyz"] for g in frame_ids[t]], float).reshape(-1, 3)
            C = np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 1]], float).reshape(-1, 3)
            if len(P) == 0 or len(C) == 0:
                continue
            N2 = (np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 2]], float).reshape(-1, 3)
                  if t + 2 < len(frame_ids) else None)
            prev_vel = np.array([vel.get(g, np.zeros(3)) for g in frame_ids[t]])
            psc = np.array([NSC[g] for g in frame_ids[t]]); csc = np.array([NSC[g] for g in frame_ids[t + 1]])
            PRm = pr[t] if (pr is not None and t < len(pr)) else None
            if PRm is not None and PRm.shape != (len(P), len(C)):
                raise AssertionError("ranker prob shape %s != (%d,%d) at t=%d"
                                     % (PRm.shape, len(P), len(C), t))
            for pi, ci in _link_accel_pr(P, C, N2, prev_vel if len(prev_vel) else None, psc, csc,
                                         amax, abonus, PRm, mode, lm, ma, ms, lb):
                gp, gcc = frame_ids[t][pi], frame_ids[t + 1][ci]
                edges.append((gp, gcc)); succ[gp] = gcc; pred[gcc] = gp; vel[gcc] = (C[ci] - P[pi]) * SCALE
    elif cfg.get("linker", "fwd") == "accel":
        amax = cfg.get("accel_max", 4.0); abonus = cfg.get("accel_bonus", 0.20)
        for t in range(len(dets) - 1):
            P = np.asarray([nodes[g]["xyz"] for g in frame_ids[t]], float).reshape(-1, 3)
            C = np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 1]], float).reshape(-1, 3)
            if len(P) == 0 or len(C) == 0:
                continue
            N2 = (np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 2]], float).reshape(-1, 3)
                  if t + 2 < len(frame_ids) else None)
            prev_vel = np.array([vel.get(g, np.zeros(3)) for g in frame_ids[t]])
            psc = np.array([NSC[g] for g in frame_ids[t]]); csc = np.array([NSC[g] for g in frame_ids[t + 1]])
            for pi, ci in _link_accel(P, C, N2, prev_vel if len(prev_vel) else None, psc, csc, amax, abonus):
                gp, gcc = frame_ids[t][pi], frame_ids[t + 1][ci]
                edges.append((gp, gcc)); succ[gp] = gcc; pred[gcc] = gp; vel[gcc] = (C[ci] - P[pi]) * SCALE
    elif cfg.get("linker", "fwd") == "mutual":
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

# ================= IMAGE EDGE MODEL: patches + compact 3D CNN =================
import torch, torch.nn as nn
DEV = "cuda" if torch.cuda.is_available() else "cpu"
UNET_THR = 0.15
PZ, PY, PX = 2, 10, 10                      # patch half-sizes (voxels) -> (5,21,21)
DZ, DY, DX = 2 * PZ + 1, 2 * PY + 1, 2 * PX + 1

def extract_patches(vol, coords):
    """coords (n,3) full-res voxel (z,y,x) -> (n,DZ,DY,DX) float16, zero-padded at
    edges, per-patch standardized (robust to per-embryo intensity scale)."""
    Z, Y, X = vol.shape
    n = len(coords)
    out = np.zeros((n, DZ, DY, DX), np.float16)
    if n == 0:
        return out
    v = vol.astype(np.float32)
    for k in range(n):
        z = int(round(coords[k, 0])); y = int(round(coords[k, 1])); x = int(round(coords[k, 2]))
        z0, z1 = max(0, z - PZ), min(Z, z + PZ + 1)
        y0, y1 = max(0, y - PY), min(Y, y + PY + 1)
        x0, x1 = max(0, x - PX), min(X, x + PX + 1)
        pa = v[z0:z1, y0:y1, x0:x1]
        if pa.size == 0:
            continue
        m = float(pa.mean()); sd = float(pa.std()) + 1e-3
        out[k, (z0 - (z - PZ)):(z0 - (z - PZ)) + (z1 - z0),
                (y0 - (y - PY)):(y0 - (y - PY)) + (y1 - y0),
                (x0 - (x - PX)):(x0 - (x - PX)) + (x1 - x0)] = ((pa - m) / sd).astype(np.float16)
    return out

class EdgeCNN(nn.Module):
    """2-channel patch pair (source@t, target@t+1) -> 32-d embedding, fused with the
    31 geometry features -> edge-probability logit."""
    def __init__(self, n_geo):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv3d(3, 16, 3, padding=1), nn.BatchNorm3d(16), nn.ReLU(), nn.MaxPool3d(2),
            nn.Conv3d(16, 32, 3, padding=1), nn.BatchNorm3d(32), nn.ReLU(), nn.MaxPool3d(2),
            nn.Conv3d(32, 32, 3, padding=1), nn.BatchNorm3d(32), nn.ReLU(),
            nn.AdaptiveAvgPool3d(1),
        )
        self.head = nn.Sequential(
            nn.Linear(32 + n_geo, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, 1))

    def forward(self, patch2, geo):
        e = self.enc(patch2).flatten(1)
        return self.head(torch.cat([e, geo], 1)).squeeze(1)

def _gather(refs):
    """refs (n,4)=(movie_idx,pair_t,src_i,tgt_j) -> 3-channel stack (n,3,DZ,DY,DX) f16:
    ch0 source@t, ch1 target@t+1, ch2 target's location in the PREVIOUS frame t
    (motion continuity: was a cell near the target's position one frame earlier)."""
    n = len(refs)
    src = np.zeros((n, DZ, DY, DX), np.float16); tgt = np.zeros((n, DZ, DY, DX), np.float16)
    prv = np.zeros((n, DZ, DY, DX), np.float16)
    for r in range(n):
        mi, tt, i, j = int(refs[r, 0]), int(refs[r, 1]), int(refs[r, 2]), int(refs[r, 3])
        st = stems[mi]; sp = SPATCH[st]; spp = SPATCH_PREV[st]
        src[r] = sp[tt][i]; tgt[r] = sp[tt + 1][j]; prv[r] = spp[tt + 1][j]
    return np.stack([src, tgt, prv], 1)

def train_cnn(refs, Xn, y, epochs=16, bs=256):
    P = _gather(refs)
    Pt = torch.tensor(P, dtype=torch.float32); Xt = torch.tensor(Xn, dtype=torch.float32)
    yt = torch.tensor(y.astype(np.float32))
    ds = torch.utils.data.TensorDataset(Pt, Xt, yt)
    dl = torch.utils.data.DataLoader(ds, batch_size=bs, shuffle=True, drop_last=(len(y) > bs))
    mdl = EdgeCNN(Xn.shape[1]).to(DEV)
    opt = torch.optim.Adam(mdl.parameters(), lr=1e-3, weight_decay=1e-4)
    pw = torch.tensor([max(0.3, (1.0 - y.mean()) / max(1e-3, y.mean()))], device=DEV)
    lossf = nn.BCEWithLogitsLoss(pos_weight=pw)
    mdl.train()
    for ep in range(epochs):
        for pb, xb, yb in dl:
            pb = pb.to(DEV); xb = xb.to(DEV); yb = yb.to(DEV)
            if np.random.rand() < 0.5: pb = torch.flip(pb, dims=[3])   # y-flip aug
            if np.random.rand() < 0.5: pb = torch.flip(pb, dims=[4])   # x-flip aug
            opt.zero_grad(); loss = lossf(mdl(pb, xb), yb); loss.backward(); opt.step()
    return mdl

def infer_cnn(mdl, refs, Xn, bs=1024):
    P = _gather(refs); out = np.zeros(len(refs), np.float32); mdl.eval()
    with torch.no_grad():
        for s0 in range(0, len(refs), bs):
            pb = torch.tensor(P[s0:s0 + bs], dtype=torch.float32).to(DEV)
            xb = torch.tensor(Xn[s0:s0 + bs], dtype=torch.float32).to(DEV)
            out[s0:s0 + bs] = torch.sigmoid(mdl(pb, xb)).cpu().numpy()
    return out

# ---------- run CV ----------
# LEARNED IMAGE-EDGE MODEL (3D-CNN patch pair + geometry), EMBRYO-level out-of-fold.
# Base config = our current best (LB 0.919 family + max_link 8 + t+2 accel 0.80),
# which is ALSO the untouched control arm.
_F = dict(unet_thr=0.15, max_dt=1, gate=4.5, snap=3.2, mincand=0.10, cap=0.08, synth=True,
          div_diverge=2.25, div_sister=15.0, linker="accel", accel_bonus=0.80, accel_max=4.0,
          short_min=6, max_link=8.0)
CONFIGS = [
    {"name": "control accel", **_F},                       # NEVER sees the model
    {"name": "full b1.0", **_F, "linker": "accel_rank", "rank_mode": "full", "learned_bonus": 1.0},
    {"name": "full b1.5", **_F, "linker": "accel_rank", "rank_mode": "full", "learned_bonus": 1.5},
    {"name": "full b2.0", **_F, "linker": "accel_rank", "rank_mode": "full", "learned_bonus": 2.0},
    {"name": "full b3.0", **_F, "linker": "accel_rank", "rank_mode": "full", "learned_bonus": 3.0},
    {"name": "rescue .6/.1 s.4", **_F, "linker": "accel_rank", "rank_mode": "rescue",
     "low_margin": 0.60, "min_adv": 0.10, "max_sub": 0.40},
]

N_PER_EMBRYO = 5
MAXT = 80                 # v3 stores 2 patch arrays (own + prev frame) -> trim to cap memory
FRAME_STRIDE = 1          # MUST be 1: GT edges are consecutive-frame
TIME_BUDGET_S = 7 * 3600
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
print("selected", len(sel), "movies:", {k: min(len(v), N_PER_EMBRYO) for k, v in by_emb.items()}, flush=True)

# ================= PASS A: detect once, build features, label from GT =================
DETS = {}; BLK = {}; GTS = {}; NEST = {}; EMB = {}; SPATCH = {}; SPATCH_PREV = {}; stems = []
Xl = []; yl = []; gl = []; ml = []; Rl = []
t_start = time.time()
for (emb, gp, zp) in sel:
    if time.time() - t_start > TIME_BUDGET_S:
        print("TIME BUDGET hit in pass A"); break
    mi = len(stems); stem = gp.stem
    gt = read_geff_min(gp)
    meta = read_array_meta(zp); T = meta["shape"][0]
    present = [t for t in range(T) if (Path(zp) / "0" / "c" / str(t) / "0" / "0" / "0").exists()]
    Tmax = min(MAXT, (max(present) + 1) if present else 0)
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
    t0 = time.time()
    dets = []; spatch = []; spatch_prev = []; vol_prev = None
    for f in frames:
        vol = load_volume(zp, f, meta)
        c, s = detect(vol)
        c = np.asarray(c, np.float32).reshape(-1, 3); s = np.asarray(s, np.float32).reshape(-1)
        dets.append((c, s)); seeds = c[s >= UNET_THR]
        spatch.append(extract_patches(vol, seeds))               # own-frame patch (aligns with _seed_frames)
        spatch_prev.append(extract_patches(vol_prev, seeds) if vol_prev is not None
                           else np.zeros((len(seeds), DZ, DY, DX), np.float16))   # prev-frame at these positions
        vol_prev = vol; gc.collect()
    SPATCH[stem] = spatch; SPATCH_PREV[stem] = spatch_prev
    tdet = time.time() - t0
    blocks = build_pair_features(dets, _F)
    labs = label_blocks(blocks, dets, _F, gt_s)
    npair = 0; npos = 0; nkn = 0
    for tt, (b, lb) in enumerate(zip(blocks, labs)):
        if b is None or lb is None:
            continue
        npair += len(b["ii"]); k = lb["known"]
        nkn += int(k.sum()); npos += int(lb["y"][k].sum())
        if k.any():
            Xl.append(b["X"][k]); yl.append(lb["y"][k])
            gl.append(mi * 10 ** 7 + lb["src"][k]); ml.append(np.full(int(k.sum()), mi, np.int32))
            ik = b["ii"][k].astype(np.int32); jk = b["jj"][k].astype(np.int32)
            Rl.append(np.stack([np.full(len(ik), mi, np.int32), np.full(len(ik), tt, np.int32), ik, jk], 1))
    DETS[stem] = dets; BLK[stem] = blocks; GTS[stem] = gt_s; EMB[stem] = emb
    NEST[stem] = gt["n_est"] * (len(frames) / max(1, Tmax))
    stems.append(stem)
    print("  A %s %s: T=%d pairs=%d labelled=%d pos=%d (det %.0fs)"
          % (emb, stem, len(frames), npair, nkn, npos, tdet), flush=True)

X_all = np.concatenate(Xl).astype(np.float32); y_all = np.concatenate(yl).astype(np.int8)
g_all = np.concatenate(gl); m_all = np.concatenate(ml); R_all = np.concatenate(Rl)
emb_all = np.array([EMB[stems[i]] for i in m_all])
print("\nTRAIN MATRIX: rows=%d pos=%d (%.3f%%) feats=%d movies=%d"
      % (len(y_all), int(y_all.sum()), 100.0 * y_all.mean(), X_all.shape[1], len(stems)), flush=True)

# ================= TRAIN: EMBRYO-level out-of-fold (honest 2-unseen-embryo analogue) =================
from sklearn.metrics import roc_auc_score
import os

gmean = X_all.mean(0); gstd = X_all.std(0) + 1e-6
Xn_all = (X_all - gmean) / gstd

MODELS = {}                    # embryo -> CNN trained on the OTHER embryo, used to predict it
oof = np.full(len(y_all), np.nan, np.float64)
for hold in sorted(set(emb_all)):
    tr = emb_all != hold; te = ~tr
    if te.sum() == 0 or y_all[tr].sum() < 20:
        continue
    print("  training CNN: hold %s (train n=%d pos=%.1f%%)" % (hold, int(tr.sum()), 100 * y_all[tr].mean()), flush=True)
    mdl = train_cnn(R_all[tr], Xn_all[tr], y_all[tr])
    MODELS[hold] = mdl
    oof[te] = infer_cnn(mdl, R_all[te], Xn_all[te])
ok = np.isfinite(oof)
print("\n================ IMAGE EDGE MODEL (out-of-fold, EMBRYO-level = cross-embryo) ================")
print("  OOF AUC (all)          : %.4f" % roc_auc_score(y_all[ok], oof[ok]))
print("  baseline AUC (-cost)   : %.4f" % roc_auc_score(y_all[ok], -X_all[ok, COST_COL]))
print("  (ranker geo-only was 0.98 AUC but +0.0002 score; the bar is beating COST on the AMBIGUOUS line below)")
for emb in sorted(set(emb_all)):
    e = ok & (emb_all == emb)
    if e.sum() and 0 < y_all[e].sum() < e.sum():
        print("  OOF AUC %s (cross-emb) : %.4f  (baseline %.4f, n=%d)"
              % (emb, roc_auc_score(y_all[e], oof[e]), roc_auc_score(y_all[e], -X_all[e, COST_COL]), int(e.sum())))

# ---- SAVE weights + norm for the submission kernel ----
try:
    os.makedirs("/kaggle/working/edge_model", exist_ok=True)
    for emb, mdl in MODELS.items():
        torch.save(mdl.state_dict(), "/kaggle/working/edge_model/edgecnn_%s.pt" % emb)
    np.savez("/kaggle/working/edge_model/norm.npz", gmean=gmean, gstd=gstd,
             pz=PZ, py=PY, px=PX, n_geo=X_all.shape[1])
    print("  saved edge_model/ (state_dicts + norm) for the submission kernel", flush=True)
except Exception as e:
    print("  (weight save skipped:", str(e)[:120], ")")

# ---- group-level top-1: does the model pick the true successor where geometry is ambiguous?
groups = defaultdict(list)
for r in np.nonzero(ok)[0]:
    groups[int(g_all[r])].append(r)
tot = 0; b_ok = 0; r_ok = 0; ltot = 0; lb_ok = 0; lr_ok = 0
for _k, rows in groups.items():
    rr = np.array(rows)
    if y_all[rr].sum() != 1 or len(rr) < 2:
        continue
    truth = rr[np.argmax(y_all[rr])]
    bpick = rr[np.argmin(X_all[rr, COST_COL])]
    rpick = rr[np.argmax(oof[rr])]
    tot += 1; b_ok += int(bpick == truth); r_ok += int(rpick == truth)
    if float(X_all[rr[0], TOP2_COL]) < 0.35:
        ltot += 1; lb_ok += int(bpick == truth); lr_ok += int(rpick == truth)
print("  group top-1 (1-positive groups, n=%d): cost %.4f -> ranker %.4f" %
      (tot, b_ok / max(1, tot), r_ok / max(1, tot)))
print("  LOW-MARGIN groups (top2 margin < 0.35um, n=%d): cost %.4f -> ranker %.4f" %
      (ltot, lb_ok / max(1, ltot), lr_ok / max(1, ltot)))
print("  ^ the model can only help if it beats cost on THAT second (ambiguous) line.", flush=True)

# ================= PASS B: apply per arm, score =================
rows = {emb: {c["name"]: {"tp": 0, "fp": 0, "fn": 0, "npred": 0, "nest": 0.0, "nrec": [],
              "dtp": 0, "dfp": 0, "dfn": 0} for c in CONFIGS} for emb in sorted(set(EMB.values()))}
for mi, stem in enumerate(stems):
    if time.time() - t_start > TIME_BUDGET_S + 1800:
        print("TIME BUDGET hit in pass B"); break
    dets = DETS[stem]; blocks = BLK[stem]; gt_s = GTS[stem]; emb = EMB[stem]
    mdl = MODELS.get(emb)          # model trained on the OTHER embryo (cross-embryo, honest)
    sp = SPATCH[stem]
    PR = []
    for tt, b in enumerate(blocks):
        if b is None or mdl is None:
            PR.append(None); continue
        refs = np.stack([np.full(len(b["ii"]), mi, np.int32), np.full(len(b["ii"]), tt, np.int32),
                         b["ii"].astype(np.int32), b["jj"].astype(np.int32)], 1)
        Xn_b = (b["X"] - gmean) / gstd
        p = infer_cnn(mdl, refs, Xn_b).astype(np.float32)
        M = np.zeros((b["np"], b["nc"]), np.float32)
        M[b["ii"], b["jj"]] = p
        PR.append(M)
    t0 = time.time()
    for c in CONFIGS:
        (pt, pp, pe), ngap, ndiv = repair_cfg(dets, c, PR if c.get("linker") == "accel_rank" else None)
        er = eval_edges(pt, pp, pe, gt_s); dv = eval_div(pt, pp, pe, gt_s)
        r = rows[emb][c["name"]]
        r["tp"] += er["tp"]; r["fp"] += er["fp"]; r["fn"] += er["fn"]
        r["npred"] += er["npred"]; r["nest"] += NEST[stem]; r["nrec"].append(er["nrec"])
        r["dtp"] += dv["dtp"]; r["dfp"] += dv["dfp"]; r["dfn"] += dv["dfn"]
    b0 = rows[emb][CONFIGS[0]["name"]]
    _j, ab, _r, _d = adj_of({"tp": b0["tp"], "fp": b0["fp"], "fn": b0["fn"], "npred": b0["npred"]}, b0["nest"])
    print("  B %s %s: control running adj=%.4f (%.0fs)" % (emb, stem, ab, time.time() - t0), flush=True)
    PR = None; gc.collect()

def _score_row(r):
    j, adj, ratio, den = adj_of({"tp": r["tp"], "fp": r["fp"], "fn": r["fn"], "npred": r["npred"]}, r["nest"])
    dden = r["dtp"] + r["dfp"] + r["dfn"]
    divj = r["dtp"] / dden if dden else float("nan")
    score = adj + (0.1 * divj if divj == divj else 0.0)
    rec = float(np.mean(r["nrec"])) if r["nrec"] else float("nan")
    return j, adj, divj, score, rec

print("\n================ CV: adj_edge_jaccard + 0.1*div_jaccard ================")
for emb in sorted(rows):
    print("---- embryo", emb, "----")
    print("  %-16s %8s %8s %8s %8s %8s %8s" % ("config", "edgeJ", "adjJ", "divJ", "SCORE", "recall", "dSCORE"))
    base = _score_row(rows[emb][CONFIGS[0]["name"]])
    for c in CONFIGS:
        j, adj, divj, score, rec = _score_row(rows[emb][c["name"]])
        print("  %-16s %8.4f %8.4f %8.4f %8.4f %8.4f %+8.4f"
              % (c["name"], j, adj, divj, score, rec, score - base[3]))

print("\n================ POOLED (both embryos) ================")
print("  %-16s %8s %8s %8s %8s" % ("config", "adjJ", "divJ", "SCORE", "dSCORE"))
pooled = {}
for c in CONFIGS:
    agg = {"tp": 0, "fp": 0, "fn": 0, "npred": 0, "nest": 0.0, "dtp": 0, "dfp": 0, "dfn": 0, "nrec": []}
    for e in rows:
        r = rows[e][c["name"]]
        for k in ("tp", "fp", "fn", "npred", "nest", "dtp", "dfp", "dfn"):
            agg[k] += r[k]
        agg["nrec"] += r["nrec"]
    pooled[c["name"]] = _score_row(agg)
b_ = pooled[CONFIGS[0]["name"]][3]
best = None
for c in CONFIGS:
    j, adj, divj, score, rec = pooled[c["name"]]
    print("  %-16s %8.4f %8.4f %8.4f %+8.4f" % (c["name"], adj, divj, score, score - b_))
    if best is None or score > best[0]:
        best = (score, c["name"])
print("\nBEST pooled:", best, "| control =", "%.4f" % b_)
print("DECISION RULE: only a ranker arm that beats the control on BOTH embryos is real.")
'''

cv_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": CV}
nb = dict(src); nb["cells"] = base_cells + [cv_cell]
nb_path = OUT_DIR / "biohub-edgemodel-v3.ipynb"
nb_path.write_text(json.dumps(nb), encoding="utf-8")
meta = {
    "id": "eeshsaxena/biohub-edgemodel-v3",
    "title": "Biohub edgemodel v3",
    "code_file": "biohub-edgemodel-v3.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": ["gpu"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models", "eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path, "| cells", len(nb["cells"]))
