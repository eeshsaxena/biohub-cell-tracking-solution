#!/usr/bin/env python3
"""Wait for biohub-v-det955, then submit ONCE. Guards against double-spend."""
import subprocess, re, time, pathlib

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG  = ROOT / "det955p.log"
VERD = ROOT / "det955p.VERDICT.txt"
DONE = ROOT / "det955p.SUBMITTED"
KID  = "eeshsaxena/biohub-v-det955"
COMP = "biohub-cell-tracking-during-development"
MSG  = ("det955: DET_THRESHOLD 0.96->0.955 on the pair body (LB 0.945). "
        "sew25 proved SECONDARY_EDGE_WEIGHT 0.25 is null (0.944->0.944), so pair's +0.001 "
        "is DET 0.96 alone. This probes whether the DET gradient keeps paying one more step.")

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")

def cli(a, t=None):
    p = subprocess.run(["kaggle"] + a, capture_output=True, text=True, timeout=t)
    return "\n".join(l for l in ((p.stdout or "") + (p.stderr or "")).splitlines()
                     if "warn" not in l.lower() and "%|" not in l and "urllib3" not in l)

def status():
    m = re.search(r"KernelWorkerStatus\.(\w+)", cli(["kernels", "status", KID], t=300))
    return m.group(1) if m else "UNKNOWN"

def main():
    log("=== watch_det955p start ===")
    if DONE.exists():
        log("already submitted (sentinel present) - refusing to double-spend"); return
    for _ in range(240):
        st = status()
        if st == "COMPLETE":
            log("COMPLETE -> submitting once")
            o = cli(["competitions", "submit", COMP, "-k", KID, "-f", "submission.csv",
                     "-v", "1", "-m", MSG], t=1800)
            DONE.write_text(o)
            log(f"submit result: {o.strip()[:200]}")
            VERD.write_text(f"det955 submitted\n{o}\n")
            log("=== DONE ==="); return
        if st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
            log(f"{st} -> not submitting")
            VERD.write_text(f"det955 {st}\n"); return
        time.sleep(120)
    VERD.write_text("timeout waiting for kernel\n")

if __name__ == "__main__":
    main()
