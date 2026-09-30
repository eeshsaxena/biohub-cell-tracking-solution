"""Build a SUBMISSION kernel = the exact 0.917 Kunal pipeline with the winning
aggressive gap-fill config swapped into repair (chosen by biohub-recall-lever-cv).

Everything else (3-branch flip-TTA detection, score-aware linker, short-filter,
linefit, safe divisions, post-export integrity gate) is byte-identical to
sub_win-kunal917-exact. Only the gap-fill step changes: multi-frame + midpoint
SYNTHESIS (99.8% within 7um of the true cell, per RECALL_RESEARCH.md) instead of
snap-only capped at 0.3%.

Usage: set CFG below to the CV-winning config, then:
  python scratch_kernels/build_recall_submission.py
  python -m kaggle kernels push -p scratch_kernels/sub_recall_fill
Only submit after the kernel COMPLETEs and its submission.csv passes the contract.
"""
from __future__ import annotations
import json
from pathlib import Path

# CV winner (biohub-recall-lever-cv v3): avg detection + fill_synth1 beat the 0.917
# base on BOTH embryos (+0.0078 pooled). Union and threshold-lowering hurt the edge
# term, so keep detection = the exact 0.917 stack; change ONLY the gap-fill step.
CFG = {"unet_thr": 0.15, "max_dt": 1, "gate": 4.5, "snap": 3.2, "mincand": 0.10, "cap": 0.08, "synth": True}
# Division-gate override (None => keep the exact 0.917 defaults). Local GT tuning
# (exp_division_tune.py): relaxing the divergence gate 2.25 -> 1.0 doubled recovered
# real divisions (2->4 TP) with ZERO added FP at the ceiling. Legal (real mitoses).
# LB (2026-08-23): fill1 (shipped div 2.25) = 0.919 NEW BEST; div-diverge1.0 = 0.903
# (relaxing divergence HURT -0.016). So test FEWER forks: div_diverge 999 disables
# safe-div entirely; 3.0 keeps only the most confident forks.
DIV_CFG = {"div_diverge": None, "div_cap": None, "div_sister": None}   # SHIPPED gate (LB-best)
LINKER = "fwd"
LINK_CFG = {"max_link": 8.0, "tight": None, "sim_w": 4.0}
# t+2 acceleration lookahead (intel lever #1). accel_bonus 0 = OFF.
ACCEL_CFG = {"accel_bonus": 0.0, "accel_max": 6.0}   # sim4 base (no accel)
# Collective flow-prior linker (CV v11 winner, +0.0032 pooled on BOTH embryos;
# the largest CV gain to date). Active ONLY when LINKER == "flowprior". pass-2
# pred = P + alpha*own_vel + beta*local_flow, where local_flow = inverse-distance
# mean OUT-velocity of the k nearest MOVING neighbours. alpha/beta/kflow chosen by
# biohub-flowcombo-cv. accel is bypassed when flowprior is active.
FLOW_CFG = {"alpha": 0.25, "beta": 0.75, "kflow": 4}
TAG = "sim4base"   # 0.921 anchor for post-proc variants

# Env overrides so variants build without editing: e.g.
#   BIO_LINKER=flowprior BIO_BETA=0.75 BIO_SIMW=4 BIO_TAG=flowA_sim4 python build_recall_submission.py
import os as _os
LINKER = _os.environ.get("BIO_LINKER", LINKER)
if "BIO_ALPHA" in _os.environ: FLOW_CFG["alpha"] = float(_os.environ["BIO_ALPHA"])
if "BIO_BETA" in _os.environ: FLOW_CFG["beta"] = float(_os.environ["BIO_BETA"])
if "BIO_KFLOW" in _os.environ: FLOW_CFG["kflow"] = int(_os.environ["BIO_KFLOW"])
if "BIO_SIMW" in _os.environ: LINK_CFG["sim_w"] = float(_os.environ["BIO_SIMW"])
if "BIO_ACCEL" in _os.environ: ACCEL_CFG["accel_bonus"] = float(_os.environ["BIO_ACCEL"])
TAG = _os.environ.get("BIO_TAG", TAG)

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
OUT_DIR = HERE / ("sub_recall_" + TAG)
OUT_DIR.mkdir(exist_ok=True)
src = json.loads(SRC_NB.read_text(encoding="utf-8"))

# cells: 0 setup, 1 helpers, 2 linker+repair_base, 3 detect-TTA, 4 repair+patches,
#        5 driver(writes submission.csv), 6 empty, 7 integrity gate.
cells = list(src["cells"])

# Override cell inserted AFTER cell 4 (patched repair_track) and BEFORE the driver:
# redefine repair_track to use aggressive multi-frame midpoint-synthesis gap fill.
OVERRIDE = r'''
# ============ AGGRESSIVE GAP-FILL OVERRIDE (recall lever, CV-selected) ============
_CFG = __CFG__
_DIVCFG = __DIVCFG__
_LINKER = "__LINKER__"
print("recall-fill submission cfg:", _CFG, "| div cfg:", _DIVCFG, "| linker:", _LINKER)
# Reassign the safe-division gates (module globals from the patches cell) if set.
if _DIVCFG.get("div_diverge") is not None: DIV_DIVERGE_UM = _DIVCFG["div_diverge"]
if _DIVCFG.get("div_cap") is not None: DIV_GLOBAL_CAP = _DIVCFG["div_cap"]
if _DIVCFG.get("div_sister") is not None: DIV_SISTER_UM = _DIVCFG["div_sister"]
_LINKCFG = __LINKCFG__
if _LINKCFG.get("max_link") is not None: MAX_LINK_UM = _LINKCFG["max_link"]
if _LINKCFG.get("tight") is not None: TIGHT_UM = _LINKCFG["tight"]
if _LINKCFG.get("sim_w") is not None: LINK_SIM_W = _LINKCFG["sim_w"]
print("linker cfg:", _LINKCFG, "| MAX_LINK_UM", MAX_LINK_UM)

def _gap_fill_cfg(nodes, edges, cand, cand_sc, cand_trees, next_id, cfg):
    max_dt = cfg["max_dt"]; gate = cfg["gate"]; snap = cfg["snap"]
    mincand = cfg["mincand"]; cap_frac = cfg["cap"]; synth = cfg["synth"]
    T = len(cand); succ = {}; pred = {}
    for a, b in edges:
        succ[a] = b; pred[b] = a
    by_t = defaultdict(list)
    for nid, n in nodes.items():
        by_t[n["t"]].append(nid)
    cand_used = [np.zeros(len(c), bool) for c in cand]
    max_gaps = max(1, int(cap_frac * len(nodes))); nadd = 0; BIG = 1e9
    for dt in range(2, max_dt + 2):
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
            cost = np.where(D > gate * dt, BIG, D)
            ri, ci = linear_sum_assignment(cost)
            props = sorted((float(D[r, c]), ends[r], starts[c]) for r, c in zip(ri, ci) if cost[r, c] < BIG)
            for d, ge, gs in props:
                if nadd >= max_gaps:
                    break
                if ge in succ or gs in pred:
                    continue
                pe_ = nodes[ge]["xyz"]; ps_ = nodes[gs]["xyz"]; chain = []; ok = True
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

_ACCEL = __ACCELCFG__
_FLOW = __FLOWCFG__
def _local_flow(P_um, out_vel, has_vel, k):
    """Inverse-distance mean OUT-velocity of the k nearest MOVING neighbours."""
    N = len(P_um)
    flow = np.zeros((N, 3), float)
    idxs = np.nonzero(has_vel)[0]
    if N == 0 or len(idxs) == 0 or k <= 0:
        return flow
    tree = cKDTree(P_um[idxs])
    kq = int(min(k + 1, len(idxs)))          # +1 so we can drop self
    dist, nb = tree.query(P_um, k=kq)
    dist = np.asarray(dist, float).reshape(N, kq)
    nb = np.asarray(nb, np.int64).reshape(N, kq)
    gnb = idxs[nb]                            # -> indices into the full source list
    valid = gnb != np.arange(N)[:, None]      # drop self
    valid &= np.cumsum(valid, axis=1) <= k    # keep only the first k non-self
    w = np.where(valid, 1.0 / (dist + 1.0), 0.0)   # inverse distance, 1um softening
    den = w.sum(1)
    num = (w[:, :, None] * out_vel[gnb]).sum(1)
    ok = den > 1e-12
    flow[ok] = num[ok] / den[ok][:, None]
    return flow

def _link_flow(prev_xyz, curr_xyz, prev_vel, flow, prev_sc, curr_sc, alpha, beta):
    """_link_sim with pred extended by the local flow field.

    pred = P + alpha*own_vel + beta*local_flow.  Everything else (raw-distance
    gate, appearance term, tight->loose two-pass Hungarian) is byte-identical to
    _link_sim, so alpha=0.5 / beta=0.0 reproduces the shipped forward linker.
    """
    if len(prev_xyz) == 0 or len(curr_xyz) == 0:
        return []
    P = prev_xyz * SCALE[None, :]; C = curr_xyz * SCALE[None, :]
    pred = P + (alpha * prev_vel if prev_vel is not None else 0.0)
    if flow is not None and beta:
        pred = pred + beta * flow
    N, M = len(P), len(C); BIG = 1e9
    sim = LINK_SIM_W * np.abs(_logit(prev_sc)[:, None] - _logit(curr_sc)[None])
    def _hun(pi, ci, gate):
        if len(pi) == 0 or len(ci) == 0:
            return []
        Draw = np.sqrt(((P[pi][:, None] - C[ci][None]) ** 2).sum(2))
        D = np.sqrt(((pred[pi][:, None] - C[ci][None]) ** 2).sum(2))
        cost = np.where(Draw > gate, BIG, D) + np.where(Draw > gate, 0.0, sim[np.ix_(pi, ci)])
        ri, rc = linear_sum_assignment(cost)
        return [(int(pi[r]), int(ci[c])) for r, c in zip(ri, rc) if cost[r, c] < BIG]
    links = _hun(np.arange(N), np.arange(M), min(TIGHT_UM, MAX_LINK_UM))
    up = {p for p, _ in links}; uc = {c for _, c in links}
    fp = np.array([i for i in range(N) if i not in up], int); fc = np.array([j for j in range(M) if j not in uc], int)
    return links + _hun(fp, fc, MAX_LINK_UM)

def _link_accel(prev_xyz, curr_xyz, next_xyz, prev_vel, prev_sc, curr_sc):
    amax = _ACCEL["accel_max"]; abonus = _ACCEL["accel_bonus"]
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
            gi, gj = np.nonzero(Draw <= gate)
            if len(gi):
                resid, _ = tree2.query(2.0 * C[ci][gj] - P[pi][gi])
                cost[gi, gj] -= abonus * np.clip(1.0 - resid / amax, 0.0, None)
        ri, rc = linear_sum_assignment(cost)
        return [(int(pi[r]), int(ci[c])) for r, c in zip(ri, rc) if cost[r, c] < BIG]
    links = _hun(np.arange(N), np.arange(M), min(TIGHT_UM, MAX_LINK_UM))
    up = {p for p, _ in links}; uc = {c for _, c in links}
    fp = np.array([i for i in range(N) if i not in up], int); fc = np.array([j for j in range(M) if j not in uc], int)
    return links + _hun(fp, fc, MAX_LINK_UM)

def _link_fused(prev_xyz, curr_xyz, prev_vel, curr_velout, prev_sc, curr_sc):
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

def repair_track(dets, ds):
    ut = _CFG["unet_thr"]
    nodes = {}; frame_ids = []; cand = []; cand_sc = []; cand_trees = []; nid = 1; NSC = {}
    for t, (coords, scores) in enumerate(dets):
        coords = np.asarray(coords, float).reshape(-1, 3); scores = np.asarray(scores, float).reshape(-1)
        seeds = coords[scores >= ut]
        cm = (scores >= CAND_THR) & (scores < ut)
        cand.append(coords[cm]); cand_sc.append(scores[cm])
        cand_trees.append(cKDTree(cand[-1] * SCALE) if len(cand[-1]) else None)
        seed_sc = scores[scores >= ut]; ids = []
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
    if _LINKER == "bidir":
        E1, ve1 = _fwd_pass()
        velout = {}
        for a, b in E1:
            velout[a] = ve1.get(b, np.zeros(3))
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
    elif _LINKER == "flowprior":
        # COLLECTIVE FLOW PRIOR (CV v11 winner). pass 1 = normal fwd link to
        # estimate every node's OUT-velocity; pass 2 = re-link with
        # pred = P + alpha*own_vel + beta*local_flow. Kills the 2.0% "steal" edges.
        alpha = float(_FLOW.get("alpha", 0.25)); beta = float(_FLOW.get("beta", 0.75))
        kflow = int(_FLOW.get("kflow", 4))
        E1, ve1 = _fwd_pass()
        velout = {}
        for a, b in E1:
            velout[a] = ve1.get(b, np.zeros(3))   # a's OUT-velocity == vel INTO its successor b
        for t in range(len(dets) - 1):
            P = np.asarray([nodes[g]["xyz"] for g in frame_ids[t]], float).reshape(-1, 3)
            C = np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 1]], float).reshape(-1, 3)
            if len(P) == 0 or len(C) == 0:
                continue
            pv = np.array([ve1.get(g, np.zeros(3)) for g in frame_ids[t]])          # own IN-velocity
            ov = np.array([velout.get(g, np.zeros(3)) for g in frame_ids[t]])       # own OUT-velocity (pass 1)
            hv = np.array([g in velout for g in frame_ids[t]], bool)                # confident pass-1 link?
            fl = _local_flow(P * SCALE[None, :], ov, hv, kflow) if beta else None
            psc = np.array([NSC[g] for g in frame_ids[t]]); csc = np.array([NSC[g] for g in frame_ids[t + 1]])
            for pi, ci in _link_flow(P, C, pv, fl, psc, csc, alpha, beta):
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
            if _ACCEL["accel_bonus"] > 0:
                _N2 = (np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 2]], float).reshape(-1, 3)
                       if t + 2 < len(frame_ids) else None)
                _lk = _link_accel(P, C, _N2, prev_vel if len(prev_vel) else None, psc, csc)
            else:
                _lk = _link_sim(P, C, prev_vel if len(prev_vel) else None, psc, csc)
            for pi, ci in _lk:
                gp, gcc = frame_ids[t][pi], frame_ids[t + 1][ci]
                edges.append((gp, gcc)); succ[gp] = gcc; pred[gcc] = gp; vel[gcc] = (C[ci] - P[pi]) * SCALE
    nid, ngap = _gap_fill_cfg(nodes, edges, cand, cand_sc, cand_trees, nid, _CFG)
    nodes, edges = _short_filter(nodes, edges)
    _linefit(nodes, edges)
    ndiv = _add_safe_divisions(nodes, edges)
    print("    recall-fill[" + ds + "]: gaps=" + str(ngap) + " divs=" + str(ndiv))
    return _emit(ds, nodes, edges)
'''.replace("__CFG__", repr(CFG)).replace("__DIVCFG__", repr(DIV_CFG)).replace("__LINKER__", LINKER).replace("__LINKCFG__", repr(LINK_CFG)).replace("__ACCELCFG__", repr(ACCEL_CFG)).replace("__FLOWCFG__", repr(FLOW_CFG))

override_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": OVERRIDE}
# insert override right before the driver (cell index 5)
new_cells = cells[:5] + [override_cell] + cells[5:]
nb = dict(src); nb["cells"] = new_cells
_kid = "biohub-recall-" + TAG + "-sub"
nb_path = OUT_DIR / (_kid + ".ipynb")
nb_path.write_text(json.dumps(nb), encoding="utf-8")

meta = {
    "id": "eeshsaxena/" + _kid,
    "title": "Biohub recall " + TAG + " sub",
    "code_file": _kid + ".ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": ["gpu"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights", "xiaoleilian/biohub-unet3d-weights-v2models"],
    "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path, "| cells", len(nb["cells"]), "| TAG", TAG)
