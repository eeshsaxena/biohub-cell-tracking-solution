r"""Compare two hfusion-family kernel runs from their downloaded outputs.

usage: python compare_kernel_runs.py <base_dir> <variant_dir>
Each dir holds `<kernel>.log`, `run_stats.csv`, `validator_results.csv` as downloaded by
  kaggle kernels output <owner/kernel> -p <dir> --file-pattern '(\.log$|run_stats\.csv$|validator_results\.csv$)'
Reports: retention-guard fallback per dataset, final node/edge counts on the placeholder clips, and the
in-kernel validator (held-out TRAIN videos, in-sample for the detector) per config and per movie.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


def guard_records(run_dir: Path) -> dict:
    seen = {}
    for log in run_dir.glob("*.log"):
        for line in log.open(encoding="utf-8", errors="ignore"):
            if "BIOHUB_RETENTION_GUARD" not in line:
                continue
            try:
                data = json.loads(line.strip().lstrip(",").lstrip("[").rstrip("]"))["data"]
            except Exception:
                continue
            for part in data.split("\n"):
                if part.startswith("BIOHUB_RETENTION_GUARD "):
                    d = json.loads(part[len("BIOHUB_RETENTION_GUARD "):])
                    seen[(d["dataset"], d["frame"])] = d
    out = defaultdict(lambda: [0, 0, 0])
    for (ds, _), d in seen.items():
        out[ds][0] += 1
        out[ds][1] += d["primary_candidates"]
        out[ds][2] += d["blended_candidates"]
    return out


def read_csv(path: Path) -> list:
    return list(csv.DictReader(path.open(newline=""))) if path.exists() else []


def main() -> None:
    base, var = Path(sys.argv[1]), Path(sys.argv[2])
    print("== retention-guard fallbacks (frames that used PRIMARY only)")
    gb, gv = guard_records(base), guard_records(var)
    for ds in sorted(set(gb) | set(gv)):
        b, v = gb.get(ds, [0, 0, 0]), gv.get(ds, [0, 0, 0])
        rb = b[2] / b[1] if b[1] else float("nan")
        rv = v[2] / v[1] if v[1] else float("nan")
        print(f"  {ds:18s} fallback frames {b[0]:4d} -> {v[0]:4d} | blend/primary on those {rb:.3f} -> {rv:.3f}")

    print("== placeholder clips (run_stats.csv)")
    sb = {r["dataset"]: r for r in read_csv(base / "run_stats.csv")}
    sv = {r["dataset"]: r for r in read_csv(var / "run_stats.csv")}
    for ds in sorted(set(sb) | set(sv)):
        b, v = sb.get(ds, {}), sv.get(ds, {})
        cols = ("raw_nodes", "nodes", "edges", "safe_divisions_added", "short_track_nodes_removed")
        print("  " + ds + "  " + "  ".join(f"{c} {b.get(c, '-')}->{v.get(c, '-')}" for c in cols))

    print("== in-kernel validator (in-sample detector; RELATIVE only)")
    vb, vv = read_csv(base / "validator_results.csv"), read_csv(var / "validator_results.csv")
    def agg(rows):
        acc = defaultdict(lambda: [0.0, 0.0, 0, 0, 0, 0.0, 0.0])
        for r in rows:
            a = acc[r["config"]]
            w = float(r["weight"])
            a[0] += float(r["adjusted_edge_jaccard"]) * w
            a[1] += w
            a[2] += int(r["div_tp"]); a[3] += int(r["div_fp"]); a[4] += int(r["div_fn"])
            a[5] += float(r["t_pred"]); a[6] += float(r["t_true"])
        return {k: (v[0] / v[1], v[2] / max(v[2] + v[3] + v[4], 1), v[5] / v[6]) for k, v in acc.items()}
    ab, av = agg(vb), agg(vv)
    for cfg in sorted(set(ab) | set(av)):
        b, v = ab.get(cfg), av.get(cfg)
        fmt = lambda x: "-" if x is None else f"adjEJ {x[0]:.5f} divJ {x[1]:.3f} Tp/Tt {x[2]:.3f}"
        combined = lambda x: None if x is None else x[0] + 0.1 * x[1]
        delta = "" if b is None or v is None else f"  d_combined {combined(v) - combined(b):+.5f}"
        print(f"  {cfg:12s} {fmt(b)}  ->  {fmt(v)}{delta}")
    per_b = {(r["config"], r["stem"]): r for r in vb}
    print("== per movie, config=base: adjEJ base -> variant, t_pred base -> variant")
    for r in vv:
        if r["config"] != "base":
            continue
        b = per_b.get(("base", r["stem"]))
        if b:
            print(f"  {r['stem']:16s} {float(b['adjusted_edge_jaccard']):.4f} -> {float(r['adjusted_edge_jaccard']):.4f}"
                  f"   t_pred {b['t_pred']} -> {r['t_pred']} (t_true {r['t_true']})")


if __name__ == "__main__":
    main()
