"""Submit the 3 validated recall-lever kernels best-first, once the daily quota
has reset (00:00 UTC). Keeps Kunal 0.917 (55681317) as the untouched fallback.

Guards: refuses to submit if the newest existing submission is already dated
today (UTC) AND there are >=5 today (quota likely spent) -- prints and exits so a
cron re-fire can't double-submit. Otherwise submits the 3 in CV-rank order.

Run:  .venv/Scripts/python.exe scratch_kernels/submit_at_reset.py
"""
from __future__ import annotations
import subprocess, sys, datetime

PY = sys.executable
COMP = "biohub-cell-tracking-during-development"
SUBS = [
    ("biohub-recall-accel16m6-sub",     "fill + max_link8 + t+2 acceleration lookahead b1.6/m6 (CV 0.8741, best on both embryos)"),
    ("biohub-recall-fillmax8accel-sub", "fill + max_link8 + t+2 acceleration lookahead b0.80 (CV 0.8732)"),
    ("biohub-recall-fillmax8-sub",      "fill + max_link8 tighter link gate (CV 0.8726)"),
]


def _run(args):
    return subprocess.run([PY, "-m", "kaggle"] + args, capture_output=True, text=True)


def already_submitted_today():
    """Count submissions whose date is today (UTC) to avoid double-submitting."""
    r = _run(["competitions", "submissions", COMP])
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    lines = [l for l in r.stdout.splitlines() if today in l]
    # also detect our own new descriptions to be extra safe
    ours = [l for l in lines if "acceleration lookahead" in l or "tighter link gate" in l]
    return len(lines), len(ours)


def main():
    n_today, n_ours = already_submitted_today()
    print("submissions dated today (UTC):", n_today, "| ours already:", n_ours)
    if n_ours >= len(SUBS):
        print("All recall-lever submissions already made today. Nothing to do.")
        return
    if n_today >= 5:
        print("5 submissions already today -> quota spent; not submitting.")
        return
    for slug, msg in SUBS[n_ours:]:
        r = _run(["competitions", "submit", COMP, "-k", f"eeshsaxena/{slug}",
                  "-v", "1", "-f", "submission.csv", "-m", msg])
        out = (r.stdout or "").strip() + (" | ERR: " + r.stderr.strip() if r.stderr.strip() else "")
        print(f"[{slug}] {out}")
        if "reached your daily submission limit" in (r.stdout + r.stderr).lower():
            print("Hit daily limit mid-batch; stopping."); break
    print("\nNow poll scores: .venv/Scripts/python.exe -m kaggle competitions submissions", COMP)


if __name__ == "__main__":
    main()
