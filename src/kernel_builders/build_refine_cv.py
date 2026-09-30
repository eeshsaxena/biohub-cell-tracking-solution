"""Build the REFINE-VARIANT CV kernel (no submission cost).

Question (from INTEL.md evening block): the 0.937->0.940 public delta added
refine_centroids (baseline p20, window (1,3,3), max shift 2.8um). Our pipeline
ALREADY refines (window (2,5), min-baseline, NO clamp). EXP4 says halving
jitter = +0.014 adjJ. This kernel measures the PAIRED delta of 5 refine
variants on train movies against local GT, one GPU pass, 5 CPU arms.

Base: sim4base cells 0-5 (exact shipped 0.921 sim4 incl. cell-5 overrides),
plus the zarr install cell, plus the CV cell below.

Run:  python scratch_kernels/build_refine_cv.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_recall_sim4base" / "biohub-recall-sim4base-sub.ipynb"
OUT_DIR = HERE / "refine_cv"
OUT_DIR.mkdir(exist_ok=True)

src = json.loads(SRC_NB.read_text(encoding="utf-8"))
base_cells = [src["cells"][i] for i in (0, 1, 2, 3, 4, 5)]  # incl. sim4 overrides

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
# ===================== REFINE-VARIANT CV (paired, sim4 base, local GT) =====================
import numpy as np, time, glob
from pathlib import Path
from collections import defaultdict
from scipy.optimize import linear_sum_assignment

TRAIN_DIR = Path(ROOT) / "train"
assert TRAIN_DIR.exists(), "no train dir under " + str(ROOT)

# ---------- inlined verified scorer (same as recall_cv) ----------
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
    edges = []; succ = {}; pred = {}; vel = {}
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
    if cfg.get("div_diverge") is not None: DIV_DIVERGE_UM = cfg["div_diverge"]
    if cfg.get("div_cap") is not None: DIV_GLOBAL_CAP = cfg["div_cap"]
    if cfg.get("div_sister") is not None: DIV_SISTER_UM = cfg["div_sister"]
    ndiv = _add_safe_divisions(nodes, edges)
    return _emit_arrays(nodes, edges), ngap, ndiv

# ---------- refine variants ----------
def refine_from_patch(patch, origin, peak, rz, ryx, baseline, max_shift_um):
    z, y, x = (int(round(v)) for v in peak)
    oz, oy, ox = (int(v) for v in origin)
    Z, Y, X = patch.shape
    az0, az1 = max(oz, z - rz), min(oz + Z, z + rz + 1)
    ay0, ay1 = max(oy, y - ryx), min(oy + Y, y + ryx + 1)
    ax0, ax1 = max(ox, x - ryx), min(ox + X, x + ryx + 1)
    crop = patch[az0 - oz:az1 - oz, ay0 - oy:ay1 - oy, ax0 - ox:ax1 - ox].astype(np.float32)
    bg = float(crop.min()) if baseline == "min" else float(np.percentile(crop, 20.0))
    w = np.clip(crop - bg, 0, None); s = float(w.sum())
    if s <= 0:
        return np.asarray(peak, float)
    zz, yy, xx = np.mgrid[az0:az1, ay0:ay1, ax0:ax1]
    c = np.array([(zz * w).sum() / s, (yy * w).sum() / s, (xx * w).sum() / s])
    if max_shift_um is not None and float(np.linalg.norm((c - np.asarray(peak, float)) * SCALE)) > max_shift_um:
        return np.asarray(peak, float)
    return c

VARIANTS = [
    ("base(2,5,min)",     dict(rz=2, ryx=5, baseline="min", max_shift_um=None)),  # == shipped sim4
    ("graf(1,3,p20,2.8)", dict(rz=1, ryx=3, baseline="p20", max_shift_um=2.8)),   # the 0.940 lever
    ("graf-noclamp",      dict(rz=1, ryx=3, baseline="p20", max_shift_um=None)),
    ("winonly(1,3,min)",  dict(rz=1, ryx=3, baseline="min", max_shift_um=None)),
    ("p20only(2,5,p20)",  dict(rz=2, ryx=5, baseline="p20", max_shift_um=None)),
]
SIM4 = dict(unet_thr=0.15, max_dt=1, gate=4.5, snap=3.2, mincand=0.10, cap=0.08, synth=True,
            div_diverge=2.25, div_sister=15.0, linker="fwd", short_min=6,
            max_link=8.0, tight=None, sim_w=4.0)

# ---------- detection pass with patch caching (GPU once per movie) ----------
PRZ, PRYX = 2, 5          # extraction window covers the LARGEST variant window
MAX_PEAKS = 4000

def detect_cache(vol):
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
    h = hs[0] if len(hs) == 1 else np.mean(hs, axis=0)
    pk = peak_local_max(h, min_distance=1, threshold_abs=DETECT_THRESH, exclude_border=False)
    if len(pk) == 0:
        return (np.zeros((0, 3)), np.zeros(0),
                np.zeros((0, 2 * PRZ + 1, 2 * PRYX + 1, 2 * PRYX + 1), np.float16),
                np.zeros((0, 3), np.int64))
    sc = h[pk[:, 0], pk[:, 1], pk[:, 2]].astype(float)
    if len(pk) > MAX_PEAKS:
        keep = np.argsort(-sc)[:MAX_PEAKS]; pk = pk[keep]; sc = sc[keep]
    coords = pk.astype(float)
    coords[:, 1] = coords[:, 1] * POOL + (POOL - 1) / 2
    coords[:, 2] = coords[:, 2] * POOL + (POOL - 1) / 2
    Z, Y, X = vol.shape
    patches = np.zeros((len(pk), 2 * PRZ + 1, 2 * PRYX + 1, 2 * PRYX + 1), np.float16)
    origins = np.zeros((len(pk), 3), np.int64)
    for i in range(len(coords)):
        z, y, x = (int(round(v)) for v in coords[i])
        z0, z1 = max(0, z - PRZ), min(Z, z + PRZ + 1)
        y0, y1 = max(0, y - PRYX), min(Y, y + PRYX + 1)
        x0, x1 = max(0, x - PRYX), min(X, x + PRYX + 1)
        origins[i] = (z0, y0, x0)
        patches[i, :z1 - z0, :y1 - y0, :x1 - x0] = vol[z0:z1, y0:y1, x0:x1].astype(np.float16)
    return coords, sc, patches, origins

# ---------- run CV ----------
N_PER_EMBRYO = 5
FRAME_STRIDE = 1
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

def zero_row():
    return {"tp": 0, "fp": 0, "fn": 0, "npred": 0, "nest": 0.0, "nrec": [],
            "dtp": 0, "dfp": 0, "dfn": 0}
rows = {emb: {v[0]: zero_row() for v in VARIANTS} for emb in by_emb}
per_mov = {}
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
    cache = []
    for f in frames:
        cache.append(detect_cache(load_volume(zp, f, meta)))
        gc.collect()
    for vname, vw in VARIANTS:
        dets = []
        for coords, sc, patches, origins in cache:
            if len(coords):
                ref = np.array([refine_from_patch(p, o, c, **vw)
                                for p, o, c in zip(patches, origins, coords)])
                ca, sa = _physical_nms(ref, sc, NMS_UM)
            else:
                ca, sa = np.zeros((0, 3)), np.zeros(0)
            dets.append((ca, sa))
        (pt, pp, pe), ngap, ndiv = repair_cfg(dets, SIM4)
        er = eval_edges(pt, pp, pe, gt_s); dv = eval_div(pt, pp, pe, gt_s)
        r = rows[emb][vname]
        r["tp"] += er["tp"]; r["fp"] += er["fp"]; r["fn"] += er["fn"]
        r["npred"] += er["npred"]; r["nest"] += n_est_scaled; r["nrec"].append(er["nrec"])
        r["dtp"] += dv["dtp"]; r["dfp"] += dv["dfp"]; r["dfn"] += dv["dfn"]
        _j, _a, _ra, _d = adj_of({"tp": er["tp"], "fp": er["fp"], "fn": er["fn"],
                                  "npred": er["npred"]}, n_est_scaled)
        per_mov[(gp.stem, vname)] = _a
    print("  %s %s: cached %d frames, 5 variants scored (%.0fs)"
          % (emb, gp.stem, len(frames), time.time() - t0))

def _score_row(r):
    j, adj, ratio, den = adj_of({"tp": r["tp"], "fp": r["fp"], "fn": r["fn"], "npred": r["npred"]}, r["nest"])
    dden = r["dtp"] + r["dfp"] + r["dfn"]
    divj = r["dtp"] / dden if dden else float("nan")
    return j, adj, divj, adj + (0.1 * divj if divj == divj else 0.0)

print("\n================ CV: refine variants (adj_edge_jaccard + 0.1*divJ) ================")
for emb in sorted(rows):
    print("---- embryo", emb, "----")
    print("  %-18s %8s %8s %8s %8s" % ("variant", "edgeJ", "adjJ", "divJ", "SCORE"))
    for vname, _vw in VARIANTS:
        j, adj, divj, score = _score_row(rows[emb][vname])
        print("  %-18s %8.4f %8.4f %8.4f %8.4f" % (vname, j, adj, divj, score))

print("\n================ POOLED + PAIRED delta vs base ================")
base_name = VARIANTS[0][0]
print("  %-18s %8s %8s %8s   %s" % ("variant", "adjJ", "divJ", "SCORE", "paired d(adjJ) mean+-se"))
for vname, _vw in VARIANTS:
    agg = zero_row()
    for e in rows:
        r = rows[e][vname]
        for k in ("tp", "fp", "fn", "npred", "nest", "dtp", "dfp", "dfn"):
            agg[k] += r[k]
    j, adj, divj, score = _score_row(agg)
    ds_list = sorted({ds for ds, v in per_mov if v == vname} & {ds for ds, v in per_mov if v == base_name})
    if ds_list:
        d = np.array([per_mov[(ds, vname)] - per_mov[(ds, base_name)] for ds in ds_list])
        pair = "%+.4f +- %.4f (n=%d)" % (d.mean(), d.std() / max(len(d), 1) ** 0.5, len(d))
    else:
        pair = "n/a"
    print("  %-18s %8.4f %8.4f %8.4f   %s" % (vname, adj, divj, score, pair))
print("\nDECISION: adopt a variant only if paired delta > 2*se AND positive on BOTH embryos.")
'''

cv_cell = {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": CV}
nb = dict(src); nb["cells"] = base_cells + [cv_cell]

# compile-check every cell before writing
for c in nb["cells"]:
    compile("".join(c["source"]) if isinstance(c["source"], list) else c["source"], "<c>", "exec")

nb_path = OUT_DIR / "biohub-refine-cv.ipynb"
nb_path.write_text(json.dumps(nb), encoding="utf-8")
meta = {
    "id": "eeshsaxena/biohub-refine-cv",
    "title": "Biohub refine variant cv",
    "code_file": "biohub-refine-cv.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": False,
    "machine_shape": "NvidiaTeslaT4", "keywords": ["gpu"],
    "dataset_sources": ["xiaoleilian/biohub-unet3d-weights",
                        "xiaoleilian/biohub-unet3d-weights-v2models",
                        "eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [], "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
(OUT_DIR / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print("built", nb_path, "| cells", len(nb["cells"]))
