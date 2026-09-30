"""Wait for the 2 extra recall-lever kernels and submit each once COMPLETE.
Respects the 5/day cap (stops if the daily limit is hit). One attempt each.
"""
import subprocess, sys, time, datetime

PY = sys.executable
COMP = "biohub-cell-tracking-during-development"
SUBS = [
    ("biohub-recall-accel24m6-sub", "fill + max_link8 + STRONGER t+2 accel b2.4/m6 (LB probe past CV peak)"),
    ("biohub-recall-fillsim4-sub",  "fill + max_link8 + appearance-similarity linker sim_w4 (orthogonal to geometry)"),
]


def run(args):
    return subprocess.run([PY, "-m", "kaggle"] + args, capture_output=True, text=True, timeout=300)


def kstatus(slug):
    o = (run(["kernels", "status", f"eeshsaxena/{slug}"]).stdout or "")
    for s in ("COMPLETE", "ERROR", "RUNNING", "QUEUED", "CANCEL"):
        if s in o:
            return s
    return "UNKNOWN"


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    submitted = set()
    deadline = time.time() + 75 * 60
    while len(submitted) < len(SUBS) and time.time() < deadline:
        for slug, msg in SUBS:
            if slug in submitted:
                continue
            st = kstatus(slug)
            if st == "COMPLETE":
                r = run(["competitions", "submit", COMP, "-k", f"eeshsaxena/{slug}",
                         "-v", "1", "-f", "submission.csv", "-m", msg])
                out = ((r.stdout or "") + (r.stderr or "")).strip()
                lo = out.lower()
                if "remaining today" in lo or "successfully submitted" in lo:
                    submitted.add(slug); log(f"SUBMITTED {slug}: {out.splitlines()[-1][:90]}")
                elif "daily submission limit" in lo or "0 submissions" in lo:
                    log(f"DAILY CAP hit at {slug}: {out[:120]}"); return
                else:
                    log(f"submit {slug} UNEXPECTED (no retry): {out[:150]}"); submitted.add(slug)
            elif st == "ERROR":
                log(f"{slug} kernel ERRORED, skipping"); submitted.add(slug)
        time.sleep(30)
    log(f"DONE. submitted={sorted(submitted)}")


if __name__ == "__main__":
    main()
