#!/usr/bin/env python3
"""Wait for biohub-v-div941 to COMPLETE, then submit it ONCE (version-bracketed).
Single submission only. Logs to watch_div941.log / .VERDICT.txt. No GPU pushes."""
import subprocess, re, time, pathlib
ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "watch_div941.log"; VERD = ROOT / "watch_div941.VERDICT.txt"
KID = "eeshsaxena/biohub-v-div941"
COMP = "biohub-cell-tracking-during-development"
MSG = ("div941: safe_div 9/14um + sister-symmetry tau0.6 + ILP_div_wt1.2 + "
       "short-track-rescue (public 0.941 geometry recipe on frontier)")
def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")
def cli(a):
    p = subprocess.run(["kaggle"] + a, capture_output=True, text=True)
    return "\n".join(l for l in ((p.stdout or "") + (p.stderr or "")).splitlines()
                     if "warn" not in l.lower() and "%|" not in l)
def status():
    m = re.search(r"KernelWorkerStatus\.(\w+)", cli(["kernels", "status", KID]))
    return m.group(1) if m else "UNKNOWN"
def submit():
    for v in (1, 2, 3, 4, 5, 6):
        o = cli(["competitions", "submit", COMP, "-k", KID, "-f", "submission.csv", "-v", str(v), "-m", MSG])
        if "Successfully" in o or "remaining" in o:
            log(f"SUBMITTED v{v}: {o.strip()[:80]}"); return True
        if "Did not find" in o or "not found" in o.lower():
            continue
        log(f"submit v{v} -> {o.strip()[:100]}")
        if "Maximum" in o: return False
    log("no valid version found to submit"); return False
def main():
    log(f"=== watch_div941 start (status={status()}) ===")
    for _ in range(120):  # ~6h at 180s
        st = status()
        if st == "COMPLETE":
            log("kernel COMPLETE -> submitting")
            ok = submit()
            VERD.write_text(f"div941 COMPLETE, submitted={ok}\nCheck: kaggle competitions submissions {COMP}\n")
            log(f"=== DONE submitted={ok} ==="); return
        if st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
            VERD.write_text(f"div941 {st} -> NOT submitted. Pull log: kaggle kernels output {KID}\n")
            log(f"=== {st}: not submitted ==="); return
        time.sleep(180)
    VERD.write_text("div941 watch timed out (still running after ~6h)\n")
    log("=== timeout ===")
if __name__ == "__main__":
    main()
