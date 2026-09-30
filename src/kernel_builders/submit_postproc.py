"""Wait for the 2 post-proc kernels and submit each once COMPLETE. One attempt each."""
import subprocess, sys, time

PY = sys.executable
COMP = "biohub-cell-tracking-during-development"
SUBS = [
    ("biohub-sim4iso-sub",  "sim4 + isolated-node removal (degree-0 cleanup, image-free post-proc)"),
    ("biohub-sim4post-sub", "sim4 + isolated + short-orphan<3 removal (post-processing)"),
]


def run(a):
    return subprocess.run([PY, "-m", "kaggle"] + a, capture_output=True, text=True, timeout=300)


def kstatus(slug):
    o = (run(["kernels", "status", f"eeshsaxena/{slug}"]).stdout or "")
    for s in ("COMPLETE", "ERROR", "RUNNING", "QUEUED"):
        if s in o:
            return s
    return "UNKNOWN"


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def main():
    done = set()
    deadline = time.time() + 80 * 60
    while len(done) < len(SUBS) and time.time() < deadline:
        for slug, msg in SUBS:
            if slug in done:
                continue
            st = kstatus(slug)
            if st == "COMPLETE":
                r = run(["competitions", "submit", COMP, "-k", f"eeshsaxena/{slug}",
                         "-v", "1", "-f", "submission.csv", "-m", msg])
                out = ((r.stdout or "") + (r.stderr or "")).strip()
                lo = out.lower()
                if "remaining today" in lo or "successfully submitted" in lo:
                    done.add(slug); log(f"SUBMITTED {slug}: {out.splitlines()[-1][:90]}")
                elif "daily submission limit" in lo or "0 submissions" in lo:
                    log(f"DAILY CAP at {slug}: {out[:120]}"); return
                else:
                    log(f"submit {slug} UNEXPECTED (no retry): {out[:150]}"); done.add(slug)
            elif st == "ERROR":
                log(f"{slug} ERRORED, skipping"); done.add(slug)
        time.sleep(30)
    log(f"DONE. submitted={sorted(done)}")


if __name__ == "__main__":
    main()
