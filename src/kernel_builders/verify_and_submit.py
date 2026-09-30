"""Wait for the round-2 sweep kernel, INDEPENDENTLY verify each CSV is legal for
the scorer, then submit the legal ones once each. Hands-off but safe.

Legality per CSV (mirrors the scorer's hard rules):
  - id column consecutive 0..N-1
  - every test dataset present
  - edges span exactly one frame (t_target - t_source == 1)
  - in-degree <= 1 (no duplicate target_id)  [a merge makes a fork malformed = FP]
  - out-degree <= 2 (forks allowed now that divisions are on)
"""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KAGGLE = str(Path(sys.executable).parent / "kaggle.exe")
USER = "eeshsaxena"
KERNEL = "biohub-submit-sweep"
COMP = "biohub-cell-tracking-during-development"
VERSION = "3"
TAGS = ["gap1div", "gap1", "gap1divsub", "gap1divpmf06", "gap1divfine"]
OUT = ROOT / "scratch_kernels" / "r2out"


def run(args):
    r = subprocess.run(args, capture_output=True, text=True, timeout=600)
    return (r.stdout or "") + (r.stderr or "")


def status():
    o = run([KAGGLE, "kernels", "status", f"{USER}/{KERNEL}"])
    for s in ("COMPLETE", "ERROR", "RUNNING", "QUEUED"):
        if s in o:
            return s
    return "UNKNOWN"


def verify(csv: Path) -> tuple[bool, str]:
    import pandas as pd
    sub = pd.read_csv(csv)
    if list(sub.id) != list(range(len(sub))):
        return False, "id not consecutive"
    nodes = sub[sub.row_type == "node"]
    edges = sub[sub.row_type == "edge"]
    nds = nodes.dataset.nunique()
    for ds, g in nodes.groupby("dataset"):
        t_of = dict(zip(g.node_id, g.t))
        e = edges[edges.dataset == ds]
        if len(e) == 0:
            continue
        spans = {t_of[a] - t_of[b] for a, b in zip(e.target_id, e.source_id)}
        if spans - {1}:
            return False, f"{ds}: edge spans {sorted(spans)} (scorer drops != 1)"
        if e.target_id.duplicated().sum() > 0:
            return False, f"{ds}: in-degree > 1"
        if e.source_id.value_counts().max() > 2:
            return False, f"{ds}: out-degree > 2"
    return True, f"{len(nodes)} nodes / {len(edges)} edges / {nds} datasets"


def main():
    print("waiting for", KERNEL, "v" + VERSION, flush=True)
    for _ in range(120):  # up to ~2 h
        st = status()
        if st in ("COMPLETE", "ERROR"):
            print("kernel status:", st, flush=True)
            break
        time.sleep(60)
    if status() != "COMPLETE":
        print("kernel not COMPLETE; aborting"); return

    OUT.mkdir(parents=True, exist_ok=True)
    run([KAGGLE, "kernels", "output", f"{USER}/{KERNEL}", "-p", str(OUT)])

    results = []
    for tag in TAGS:
        csv = OUT / f"submission_{tag}.csv"
        if not csv.exists():
            print(f"MISSING {csv.name}"); results.append((tag, "missing", None)); continue
        ok, info = verify(csv)
        print(f"[verify] {tag}: {'LEGAL' if ok else 'ILLEGAL'} — {info}", flush=True)
        if not ok:
            results.append((tag, "illegal:" + info, None)); continue
        out = run([KAGGLE, "competitions", "submit", COMP, "-k", f"{USER}/{KERNEL}",
                   "-v", VERSION, "-f", f"submission_{tag}.csv", "-m", f"round2 {tag}"])
        lo = out.lower()
        good = "remaining today" in lo or "successfully submitted" in lo
        status_str = out.strip().splitlines()[-1][:120] if out.strip() else "(no output)"
        print(f"[submit] {tag}: {'OK' if good else 'FAIL'} — {status_str}", flush=True)
        results.append((tag, "submitted" if good else "submit-fail:" + status_str, good))
        time.sleep(3)

    print("\n=== SUMMARY ===")
    for t, s, _ in results:
        print(f"  {t}: {s}")


if __name__ == "__main__":
    main()
