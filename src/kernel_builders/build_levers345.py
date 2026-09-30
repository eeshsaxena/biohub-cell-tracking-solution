"""Build the 3 remaining BIOHUB_FINAL_PACKAGE lever kernels from the 0.921 sim4 base.

  biohub-sim4gap-sub   Lever 3: multi-frame gap closing (2-3 frame) w/ midpoint
                       synthesis, image-free CSV post-proc appended after the
                       integrity gate (cannot break detection/linking).
  biohub-sim4mc-sub    Lever 4: global motion compensation — phase_cross_correlation
                       drift per frame pair, subtracted inside the sim4 linker.
  biohub-laptrack-sub  Lever 5: LapTrack 2-stage LAP replaces the per-frame linker
                       (locally-tested config from kaggle/exp_laptrack_ab.py,
                       synth=True so >1-frame gap links become scored edges).

Run:  python scratch_kernels/build_levers345.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "sub_recall_sim4base" / "biohub-recall-sim4base-sub.ipynb"
base = json.loads(BASE.read_text(encoding="utf-8"))
base_meta = json.loads((HERE / "sub_recall_sim4base" / "kernel-metadata.json").read_text())

# cell indices in the sim4 base: 0 setup, 1 helpers, 2 linker+repair_base,
# 3 detect-TTA, 4 patches, 5 gap-fill override, 6 DRIVER, 7 empty, 8 gate.
DRIVER_IDX = 6


def cell(src):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": src}


def write_kernel(tag, title, cells, extra_datasets=()):
    out = HERE / ("sub_" + tag)
    out.mkdir(exist_ok=True)
    kid = "biohub-" + tag + "-sub"
    nb = dict(base); nb["cells"] = cells
    (out / (kid + ".ipynb")).write_text(json.dumps(nb), encoding="utf-8")
    meta = dict(base_meta)
    meta["id"] = "eeshsaxena/" + kid
    meta["title"] = title
    meta["code_file"] = kid + ".ipynb"
    meta["dataset_sources"] = list(base_meta["dataset_sources"]) + list(extra_datasets)
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("built", kid, "| cells", len(cells))


# ---------------------------------------------------------------- lever 3 ----
GAP_CELL = r'''
# ====== POST-PROCESS (lever 3): multi-frame gap closing, 2-3 frames, midpoint
# synthesis. fill1 in-pipeline already closes 1-frame gaps; this adds the LONGER
# gaps. The scorer drops edges with dt>1, so every accepted bridge SYNTHESISES
# the intermediate nodes (linear interpolation), turning it into scored dt=1
# edges. Image-free CSV rewrite after the integrity gate: cannot break the
# 0.921 detection/linking. Gate 10um (package), cap 0.5% of movie nodes.
import pandas as pd, numpy as np
from collections import defaultdict
from scipy.optimize import linear_sum_assignment
SCALE3 = np.array([1.625, 0.40625, 0.40625])
MAX_GAP = 3; GATE_UM = 10.0; CAP_FRAC = 0.005
sub = pd.read_csv("/kaggle/working/submission.csv")
nrows0 = len(sub); tot_added = 0; out_parts = []
for ds in sorted(sub.dataset.unique()):
    ns = sub[(sub.dataset == ds) & (sub.row_type == "node")]
    es = sub[(sub.dataset == ds) & (sub.row_type == "edge")]
    N = {int(r.node_id): (int(r.t), np.array([r.z, r.y, r.x], float)) for r in ns.itertuples()}
    E = [(int(a), int(b)) for a, b in zip(es.source_id, es.target_id)]
    out_d = defaultdict(int); in_d = defaultdict(int)
    for a, b in E:
        out_d[a] += 1; in_d[b] += 1
    by_t = defaultdict(list)
    for nid, (t, _) in N.items():
        by_t[t].append(nid)
    next_id = (max(N) + 1) if N else 1
    cap = max(1, int(CAP_FRAC * len(N))); added = 0
    for gap in range(2, MAX_GAP + 1):
        for t in sorted(by_t):
            if added >= cap:
                break
            ends = [g for g in by_t.get(t, []) if out_d[g] == 0 and in_d[g] == 1]
            starts = [g for g in by_t.get(t + gap, []) if in_d[g] == 0 and out_d[g] >= 1]
            if not ends or not starts:
                continue
            P = np.asarray([N[g][1] for g in ends]) * SCALE3
            Cc = np.asarray([N[g][1] for g in starts]) * SCALE3
            D = np.sqrt(((P[:, None] - Cc[None]) ** 2).sum(2)); BIG = 1e9
            cost = np.where(D > GATE_UM, BIG, D)
            ri, ci = linear_sum_assignment(cost)
            for r, c in sorted(zip(ri, ci), key=lambda rc: D[rc[0], rc[1]]):
                if added >= cap or cost[r, c] >= BIG:
                    continue
                ge, gs = ends[r], starts[c]
                if out_d[ge] > 0 or in_d[gs] > 0:
                    continue
                pe, ps = N[ge][1], N[gs][1]; prev = ge
                for k in range(1, gap):
                    ng = next_id; next_id += 1
                    N[ng] = (t + k, pe + (ps - pe) * (k / gap))
                    by_t[t + k].append(ng)
                    E.append((prev, ng)); out_d[prev] += 1; in_d[ng] += 1; prev = ng
                E.append((prev, gs)); out_d[prev] += 1; in_d[gs] += 1
                added += 1; tot_added += 1
    nrows = [(ds, "node", nid, N[nid][0], float(N[nid][1][0]), float(N[nid][1][1]),
              float(N[nid][1][2]), -1, -1) for nid in sorted(N)]
    erows = [(ds, "edge", -1, -1, -1, -1, -1, a, b) for a, b in E]
    cols9 = [c for c in sub.columns if c != "id"]
    out_parts.append(pd.DataFrame(nrows + erows, columns=cols9))
out = pd.concat(out_parts, ignore_index=True)
out["id"] = range(len(out))
# re-gate: consecutive ids, every edge spans exactly 1 frame, in-deg<=1, out-deg<=2
assert list(out.id) == list(range(len(out)))
for ds, g in out[out.row_type == "node"].groupby("dataset"):
    tof = dict(zip(g.node_id.astype(int), g.t.astype(int)))
    e = out[(out.row_type == "edge") & (out.dataset == ds)]
    if len(e) == 0:
        continue
    spans = {tof[int(b)] - tof[int(a)] for a, b in zip(e.source_id, e.target_id)}
    assert spans <= {1}, (ds, spans)
    assert e.target_id.duplicated().sum() == 0
    assert e.source_id.value_counts().max() <= 2
out.to_csv("/kaggle/working/submission.csv", index=False)
print(f"POST-PROC gap-close: rows {nrows0}->{len(out)} | bridges added {tot_added} "
      f"(<= {MAX_GAP}f, gate {GATE_UM}um) | datasets {out.dataset.nunique()}")
'''

# ---------------------------------------------------------------- lever 4 ----
MC_CELL = r'''
# ====== LEVER 4: GLOBAL MOTION COMPENSATION ===============================
# phase_cross_correlation between consecutive frames (pooled+normalised) gives
# the global rigid drift per frame pair; the sim4 linker then links frame t+1
# in the drift-compensated frame (positions in the OUTPUT stay original).
# SIGN (measured locally): skimage returns the vector that REGISTERS frame t+1
# back onto frame t, i.e. MINUS the content motion — so compensated positions
# are C + shift, NOT C - shift as in the package pseudocode (its sign is wrong).
# Clamped to +-6um: larger estimates are appearance-change artifacts, not drift.
from skimage.registration import phase_cross_correlation
_MC_SHIFTS = {}
MC_MAX_UM = 6.0

def _mc_pair_shift(vol_a, vol_b):
    a = pool_norm(vol_a); b = pool_norm(vol_b)
    if a.shape != b.shape or np.array_equal(a, b):
        return np.zeros(3)
    s, _e, _p = phase_cross_correlation(a, b, upsample_factor=4, normalization="phase")
    vox = np.array([s[0], s[1] * POOL, s[2] * POOL])   # pooled YX -> full-res voxels
    if not np.isfinite(vox).all():
        return np.zeros(3)
    um = vox * SCALE
    if float(np.abs(um).max()) > MC_MAX_UM:
        return np.zeros(3)
    return um

def repair_track(dets, ds):   # sim4 fwd linker + motion compensation
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
    edges = []; succ = {}; pred = {}; vel = {}
    sh = _MC_SHIFTS.get(ds, {})
    for t in range(len(dets) - 1):
        P = np.asarray([nodes[g]["xyz"] for g in frame_ids[t]], float).reshape(-1, 3)
        C = np.asarray([nodes[g]["xyz"] for g in frame_ids[t + 1]], float).reshape(-1, 3)
        if len(P) == 0 or len(C) == 0:
            continue
        dv = sh.get(t)
        C2 = C + (dv / SCALE)[None, :] if dv is not None else C
        prev_vel = np.array([vel.get(g, np.zeros(3)) for g in frame_ids[t]])
        psc = np.array([NSC[g] for g in frame_ids[t]]); csc = np.array([NSC[g] for g in frame_ids[t + 1]])
        for pi, ci in _link_sim(P, C2, prev_vel if len(prev_vel) else None, psc, csc):
            gp, gcc = frame_ids[t][pi], frame_ids[t + 1][ci]
            edges.append((gp, gcc)); succ[gp] = gcc; pred[gcc] = gp
            vel[gcc] = (C2[ci] - P[pi]) * SCALE   # drift-compensated velocity
    nid, ngap = _gap_fill_cfg(nodes, edges, cand, cand_sc, cand_trees, nid, _CFG)
    nodes, edges = _short_filter(nodes, edges)
    _linefit(nodes, edges)
    ndiv = _add_safe_divisions(nodes, edges)
    print("    mc[" + ds + "]: gaps=" + str(ngap) + " divs=" + str(ndiv)
          + " mean|shift|=" + (f"{np.mean([np.abs(v).max() for v in sh.values()]):.2f}um" if sh else "n/a"))
    return _emit(ds, nodes, edges)

def track_movie(zp, ds, T):   # detect + measure global drift per frame pair
    meta = read_array_meta(zp); dets = []; prev = None; shifts = {}
    for t in range(T):
        vol = load_volume(zp, t, meta)
        if prev is not None:
            shifts[t - 1] = _mc_pair_shift(prev, vol)
            del prev
        prev = vol
        dets.append(detect(vol)); gc.collect()
    del prev
    _MC_SHIFTS[ds] = shifts
    return repair_track(dets, ds)
'''

# ---------------------------------------------------------------- lever 5 ----
LT_INSTALL = r'''
# install laptrack from the attached wheel dataset (kernel internet is off)
import subprocess, sys, glob
_w = sorted(glob.glob("/kaggle/input/biohub-laptrack-wheels/*.whl"))
print("wheels:", _w)
subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", "--no-index"] + _w, check=False)
import laptrack
print("laptrack import OK:", getattr(laptrack, "__version__", "?"))
'''

LT_CELL = r'''
# ====== LEVER 5: LapTrack 2-stage LAP linker ================================
# Replaces the per-frame Hungarian with LapTrack's globally-optimal per-frame
# LAP + gap closing (max 3 frames) + native splitting. Config = the locally
# A/B-tested one (kaggle/exp_laptrack_ab.py): cutoff 7um^2, gap 10um^2,
# split 10um^2, merging off. Gap links >1 frame are MATERIALISED with midpoint
# synthesis (synth=True in the A/B) because the scorer drops dt>1 edges.
# Detection (0.15 ensemble + NMS) is UNTOUCHED. Divisions come from LapTrack
# splitting; the sim4 safe-division patch and fill1 are replaced by design.
def repair_track(dets, ds):
    from laptrack import LapTrack
    ut = _CFG["unet_thr"]
    nodes = {}; nid = 1; det_t = []; det_pos = []
    for t, (coords, scores) in enumerate(dets):
        coords = np.asarray(coords, float).reshape(-1, 3); scores = np.asarray(scores, float).reshape(-1)
        for xyz in coords[scores >= ut]:
            nodes[nid] = {"t": t, "xyz": np.asarray(xyz, float)}
            det_t.append(t); det_pos.append(xyz); nid += 1
    if not det_t:
        return _emit(ds, nodes, [])
    det_t = np.asarray(det_t, int); det_pos = np.asarray(det_pos, float)
    mic = det_pos * SCALE[None, :]
    df = pd.DataFrame({"frame": det_t, "z": mic[:, 0], "y": mic[:, 1], "x": mic[:, 2],
                       "orig": np.arange(len(det_t))})
    lt = LapTrack(track_dist_metric="sqeuclidean",
                  cutoff=7.0 ** 2,
                  gap_closing_cutoff=10.0 ** 2,
                  gap_closing_max_frame_count=3,
                  splitting_cutoff=10.0 ** 2,
                  merging_cutoff=False)
    track_df, split_df, _merge = lt.predict_dataframe(
        df, coordinate_cols=["z", "y", "x"], only_coordinate_cols=False)
    track_df = track_df.reset_index()
    edges = []
    def emit(o_a, t_a, p_a, o_b, t_b, p_b):
        nonlocal nid
        dt = t_b - t_a
        if dt < 1:
            return
        prev = o_a + 1
        for k in range(1, dt):            # synthesise midpoints -> scored dt=1 edges
            nodes[nid] = {"t": t_a + k, "xyz": p_a + (p_b - p_a) * (k / dt)}
            edges.append((prev, nid)); prev = nid; nid += 1
        edges.append((prev, o_b + 1))
    rows = track_df.sort_values(["tree_id", "track_id", "frame"])
    for _tid, grp in rows.groupby("track_id"):
        g = grp.sort_values("frame"); prev = None
        for _, r in g.iterrows():
            cur = (int(r["orig"]), int(r["frame"]), det_pos[int(r["orig"])])
            if prev is not None:
                emit(prev[0], prev[1], prev[2], cur[0], cur[1], cur[2])
            prev = cur
    if split_df is not None and len(split_df):
        first = rows.sort_values("frame").groupby("track_id").first()
        last = rows.sort_values("frame").groupby("track_id").last()
        for _, r in split_df.iterrows():
            p, c = r["parent_track_id"], r["child_track_id"]
            if p in last.index and c in first.index:
                la, ch = last.loc[p], first.loc[c]
                emit(int(la["orig"]), int(la["frame"]), det_pos[int(la["orig"])],
                     int(ch["orig"]), int(ch["frame"]), det_pos[int(ch["orig"])])
    nodes, edges = _short_filter(nodes, edges)
    print(f"    laptrack[{ds}]: nodes={len(nodes)} edges={len(edges)}")
    return _emit(ds, nodes, edges)
'''

cells = list(base["cells"])
write_kernel("sim4gap", "biohub sim4gap sub", cells + [cell(GAP_CELL)])
write_kernel("sim4mc", "biohub sim4mc sub",
             cells[:DRIVER_IDX] + [cell(MC_CELL)] + cells[DRIVER_IDX:])
write_kernel("laptrack", "biohub laptrack sub",
             cells[:DRIVER_IDX] + [cell(LT_INSTALL), cell(LT_CELL)] + cells[DRIVER_IDX:],
             extra_datasets=["eeshsaxena/biohub-laptrack-wheels"])
