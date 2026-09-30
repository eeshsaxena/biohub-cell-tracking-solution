#!/usr/bin/env python3
"""
Paired in-kernel-validator CV comparison vs the grafael-0940 fork baseline.

Usage:
  python scratch_kernels/paired_cv.py name=path/to/validator_results.csv [name2=path2 ...]
Baseline is always scratch_kernels/out_fork/validator_results.csv (fork, CV 0.9179).
Only movies COMMON to all inputs are used (true paired comparison).
Prints weighted adjusted_edge_jaccard, delta vs fork, per-movie table, and a
noise-band verdict (4-movie validator CV is ~+/-0.004; treat |delta|<0.004 as noise).
"""
import csv, io, os, sys, pathlib

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
BASE = ROOT / "scratch_kernels" / "out_fork" / "validator_results.csv"
NOISE = 0.004  # 4-movie validator CV noise band

def load(p):
    rows = list(csv.DictReader(io.open(p, encoding="utf-8")))
    return {r["stem"]: (float(r["adjusted_edge_jaccard"]), float(r["weight"])) for r in rows}

def main():
    inputs = [("fork(base)", str(BASE))]
    for a in sys.argv[1:]:
        if "=" not in a:
            print(f"bad arg {a!r}; use name=path"); sys.exit(2)
        n, p = a.split("=", 1)
        inputs.append((n, p))
    data = {}
    for n, p in inputs:
        if not os.path.exists(p):
            print(f"MISSING {n}: {p}"); continue
        data[n] = load(p)
    if "fork(base)" not in data:
        print("no baseline"); sys.exit(1)
    common = set.intersection(*[set(d) for d in data.values()])
    if not common:
        print("no common movies across inputs"); sys.exit(1)
    def cv(d):
        ws = sum(d[m][1] for m in common)
        return sum(d[m][0] * d[m][1] for m in common) / ws
    base = cv(data["fork(base)"])
    print(f"common movies: {len(common)}   (noise band +/-{NOISE})")
    print(f"\n{'variant':16} {'CV':>8} {'d vs fork':>10}  verdict")
    for n, _ in inputs:
        if n not in data: continue
        c = cv(data[n]); d = c - base
        if n == "fork(base)":
            v = "baseline"
        elif d > NOISE:   v = "REAL GAIN (>noise)"
        elif d < -NOISE:  v = "REAL LOSS"
        else:             v = "noise"
        print(f"{n:16} {c:8.4f} {d:+10.4f}  {v}")
    names = [n for n, _ in inputs if n in data]
    print("\nper-movie adjEJ:")
    print(f"{'movie':22} " + " ".join(f"{n[:9]:>9}" for n in names))
    for mv in sorted(common):
        print(f"{mv:22} " + " ".join(f"{data[n][mv][0]:9.4f}" for n in names))

if __name__ == "__main__":
    main()
