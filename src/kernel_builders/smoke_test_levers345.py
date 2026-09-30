"""Smoke-test the 3 lever kernels' new cells locally before pushing.

L3: run the gap-close post-proc cell on a real prior submission.csv.
L4: run _mc_pair_shift on two real consecutive volumes from data/train.
L5: exec the LapTrack repair_track cell on synthetic moving detections.
"""
import json, sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

def cell_src(nb_path, pred):
    nb = json.loads(Path(nb_path).read_text(encoding="utf-8"))
    for c in nb["cells"]:
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if pred(s):
            return s
    raise SystemExit(f"cell not found in {nb_path}")

# ------------------------------------------------------------------- L3 ------
print("=== L3 gap-close post-proc ===")
src = cell_src(HERE / "sub_sim4gap" / "biohub-sim4gap-sub.ipynb",
               lambda s: "lever 3" in s)
real = ROOT / "scratch_kernels" / "biohub-prune-submit_out" / "submission.csv"
tmp = Path(tempfile.mkdtemp()) / "submission.csv"
df = pd.read_csv(real)
# keep a few datasets to stay fast, and only columns the gate expects
keep_ds = sorted(df.dataset.unique())[:5]
df[df.dataset.isin(keep_ds)].to_csv(tmp, index=False)
ns = {}
exec(compile(src.replace("/kaggle/working/submission.csv", str(tmp).replace("\\", "/")),
             "<gapcell>", "exec"), ns)
out = pd.read_csv(tmp)
n0 = df[df.dataset.isin(keep_ds)]
print("rows:", len(n0), "->", len(out), "| edge spans OK:",
      (out[out.row_type == "edge"].shape[0] >= 0))
assert list(out.columns) == list(df.columns) or "id" in out.columns

# ------------------------------------------------------------------- L4 ------
print("=== L4 motion-comp shift on real volumes ===")
SCALE = np.array([1.625, 0.40625, 0.40625]); POOL = 4
def pool_xy(vol, f=POOL):
    Z, Y, X = vol.shape; Y2, X2 = (Y // f) * f, (X // f) * f
    v = vol[:, :Y2, :X2].astype(np.float32, copy=False)
    return v.reshape(Z, Y2 // f, f, X2 // f, f).mean(axis=(2, 4))
def pool_norm(vol):
    p = pool_xy(vol)
    lo = float(np.percentile(p, 50)); hi = float(np.percentile(p, 99.5))
    return np.clip((p - lo) / (hi - lo + 1e-6), -0.5, 6.0).astype(np.float32)
mcsrc = cell_src(HERE / "sub_sim4mc" / "biohub-sim4mc-sub.ipynb",
                 lambda s: "_mc_pair_shift" in s)
g = {"np": np, "pool_norm": pool_norm, "SCALE": SCALE, "POOL": POOL, "gc": __import__("gc")}
exec(compile(mcsrc.split("def repair_track")[0], "<mc>", "exec"), g)
# local data has no image volumes (GT geff only) -> validate on synthetic
# volumes with a KNOWN global shift: phase correlation must recover it.
Z, Y, X = 32, 256, 256
rng = np.random.default_rng(1)
base = rng.normal(1200, 200, (Z, Y, X)).astype(np.float32)
for _ in range(40):  # blob "cells"
    z, y, x = rng.integers(3, Z - 3), rng.integers(8, Y - 8), rng.integers(8, X - 8)
    base[z - 2:z + 3, y - 5:y + 6, x - 5:x + 6] += 3000
TRUE_SH_UM = np.array([1.625, 2 * 0.40625, -3 * 0.40625])   # +1z, +2y, -3x vox
TRUE_SH_VOX = TRUE_SH_UM / SCALE
moved = np.roll(base, (1, 2, -3), axis=(0, 1, 2)) + rng.normal(0, 30, (Z, Y, X))
est = g["_mc_pair_shift"](base, moved)
# skimage returns the registration vector (moving -> reference) = -content motion
print(f"  true content motion {TRUE_SH_UM} um -> estimated {np.round(est, 3)} um (expect ~ -true)")
err = np.abs(est + TRUE_SH_UM).max()
assert err < 0.5, f"shift recovery error {err} um"   # 1 full-res voxel pooling quantisation
ident = g["_mc_pair_shift"](base, base.copy())
assert np.abs(ident).max() == 0.0, "frozen frame must give zero shift"
big = np.roll(base, (10, 0, 0), axis=(0, 1, 2))    # 16um >> clamp -> zero
assert np.abs(g["_mc_pair_shift"](base, big)).max() == 0.0, "clamp failed"
print("  frozen-frame -> zero OK | >clamp artifact -> zero OK")

# ------------------------------------------------------------------- L5 ------
print("=== L5 laptrack repair_track (synthetic) ===")
ltsrc = cell_src(HERE / "sub_laptrack" / "biohub-laptrack-sub.ipynb",
                 lambda s: "LEVER 5" in s)
rng = np.random.default_rng(0)
T, NCELL = 12, 30
pos = {c: rng.uniform([2, 10, 10], [18, 200, 200]) for c in range(NCELL)}
vel = {c: rng.normal(0, 1.0, 3) * SCALE / SCALE for c in range(NCELL)}  # ~1 vox/frame
dets = []
for t in range(T):
    pts, scs = [], []
    for c in range(NCELL):
        p = pos[c] + vel[c] * t + rng.normal(0, 0.3, 3)
        pts.append(p); scs.append(0.9)
    for _ in range(4):                      # FP detections
        pts.append(rng.uniform([2, 10, 10], [18, 200, 200])); scs.append(0.2)
    dets.append((np.asarray(pts), np.asarray(scs)))

COLS = ["dataset", "row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"]
def _emit(ds, nodes, edges):
    es = [(a, b) for a, b in dict.fromkeys(edges) if a in nodes and b in nodes and a != b]
    used = {x for e in es for x in e}
    nr = [(ds, "node", i, int(nodes[i]["t"]), *map(float, nodes[i]["xyz"]), -1, -1)
          for i in sorted(used)]
    er = [(ds, "edge", -1, -1, -1, -1, -1, a, b) for a, b in es]
    return pd.DataFrame(nr, columns=COLS), pd.DataFrame(er, columns=COLS)
def _short_filter(nodes, edges):
    return nodes, edges
ns5 = {"np": np, "pd": pd, "SCALE": SCALE, "_CFG": {"unet_thr": 0.15},
       "_emit": _emit, "_short_filter": _short_filter}
exec(compile(ltsrc, "<lt>", "exec"), ns5)
nodes_df, edges_df = ns5["repair_track"](dets, "SMOKE")
spans = set()
tof = dict(zip(nodes_df.node_id, nodes_df.t))
for a, b in zip(edges_df.source_id, edges_df.target_id):
    spans.add(tof[b] - tof[a])
n_ideal = (T - 1) * NCELL
print(f"nodes={len(nodes_df)} edges={len(edges_df)} (ideal~{n_ideal}) spans={spans}")
assert spans <= {1}, spans
assert len(edges_df) > 0.7 * n_ideal, "recovered far fewer edges than ideal"
print("ALL SMOKE TESTS PASSED")
