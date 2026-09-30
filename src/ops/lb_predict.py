#!/usr/bin/env python3
"""Calibrate board ~ local adjEJ and predict the pending arms."""
import json
import glob
import os
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_officialscores")
BOARD = {
    "divrank": 0.937, "divrank2": 0.943, "hfusion": 0.947, "hsoft": 0.946,
    "gdiv": 0.949, "stk3": 0.952, "t60h": 0.952, "t65h": 0.952,
    "t6stk3": 0.954, "t6r70": 0.954, "t6rlf": 0.953, "t6w72": 0.953,
    "t6lf": 0.953, "t65s3": 0.954, "xsv": 0.951, "xsvf": 0.951,
    "xsvdv": 0.946, "xsvdc": 0.950, "xsvd": 0.945,
    "det955": 0.945, "edgetta": 0.941, "946": 0.945,
}
XBODY = {"xsv", "xsvf", "xsvdv", "xsvdc", "xsvd", "xbase", "xpub", "xsv96",
         "xsvb", "xsvd10", "xsvdd", "xsvdu", "xsvgc", "xsvmp", "xsvmx",
         "xsvp26", "xsvsr", "xsvt", "xsvwz"}
TBODY = {"t6stk3", "t6r70", "t6rlf", "t6w72", "t6lf", "t65s3", "stk3",
         "t60h", "t65h", "t6dc", "t6dd", "t6dv", "t6wz", "t6sr"}

by = {}
for f in glob.glob(f"{D}/s3_*.json"):
    r = json.load(open(f))
    by[r["tag"]] = r


def fit(tags, key="adjEJ"):
    x = np.array([by[t][key] for t in tags])
    y = np.array([BOARD[t] for t in tags])
    A = np.vstack([x, np.ones_like(x)]).T
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    resid = y - pred
    return coef, resid.std(ddof=2), x, y


print("=== SLOPE OF BOARD ON LOCAL adjEJ ===")
for name, sel in [("all 22 arms", list(BOARD)),
                  ("our t-lineage only (9)", [t for t in BOARD if t in TBODY]),
                  ("x-lineage only (5)", [t for t in BOARD if t in XBODY])]:
    tags = [t for t in sel if t in by]
    if len(tags) < 3:
        continue
    coef, sd, x, y = fit(tags)
    print(f"{name:26s} n={len(tags):2d}  board = {coef[0]:+.4f}*adjEJ "
          f"{coef[1]:+.4f}   residual sd = {sd:.4f}")

# t-lineage calibration, used for prediction
tt = [t for t in BOARD if t in TBODY and t in by]
coef_t, sd_t, xt, yt = fit(tt)
print("\n=== PREDICTIONS from the t-lineage calibration "
      "(valid only for arms on OUR body) ===")
for t in ["t6sr", "t6dc", "t6dd", "t6dv", "t6wz"]:
    if t not in by:
        continue
    p = coef_t[0] * by[t]["adjEJ"] + coef_t[1]
    print(f"  {t:8s} adjEJ {by[t]['adjEJ']:.5f} -> predicted board "
          f"{p:.4f}  +/- {2*sd_t:.4f}")

print("\n=== THE x-LINEAGE: what the board already paid for a local delta ===")
print("  xsv    local 0.90530 -> board 0.951   (x138 body + OUR sub-voxel)")
print("  xbase  local 0.90558 -> not submitted (x138 body, NO coordinate head)")
print("  xpub   local 0.91798 -> PENDING       (x138 body + its own V1284 head)")
print("  author's own board score for exactly the xpub configuration: 0.956")
dv = by["xpub"]["adjEJ"] - by["xsv"]["adjEJ"]
print(f"  local delta xpub - xsv = {dv:+.5f}; the board delta for the SAME "
      f"two configurations (author 0.956 vs our xsv 0.951) = +0.005")
print(f"  => realised transfer coefficient on that one pair: "
      f"{0.005/dv:.2f} board points per local point")

print("\n=== transfer coefficient inside our own body, large deltas only ===")
base = "t6stk3"
for t in ["t6rlf", "t6r70", "t6lf", "stk3", "t60h", "t65h", "t65s3"]:
    dl = by[t]["adjEJ"] - by[base]["adjEJ"]
    db = BOARD[t] - BOARD[base]
    k = db / dl if abs(dl) > 1e-6 else float("nan")
    print(f"  {t:8s} local {dl:+.5f}  board {db:+.3f}   ratio {k:+.2f}")

print("\n=== the arm we should NOT spend a slot on ===")
s = by["synp"]
print(f"  synp: adjEJ {s['adjEJ']:.5f} vs t6stk3 {by['t6stk3']['adjEJ']:.5f} "
      f"= {s['adjEJ']-by['t6stk3']['adjEJ']:+.5f}")
print(f"        nodes {s['n_pred']} vs N_est {s['n_est']} "
      f"= {(s['n_pred']-s['n_est'])/s['n_est']*100:+.1f}%  "
      f"(t6stk3 is {(by['t6stk3']['n_pred']-s['n_est'])/s['n_est']*100:+.1f}%)")
for m in s["per_movie"]:
    print(f"        {m['sample']:15s} N={m['n_pred']:6d} Nest={m['n_est']:6d} "
          f"mult={m['mult']:.4f} strictJ={m['j']:.4f}")
