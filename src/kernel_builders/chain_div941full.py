#!/usr/bin/env python3
"""Shot 2 of 3. Wait for div941 to finish (frees the GPU shards + lets its watcher submit),
then push v_div941full (diverge4.0 + adaptive) and submit it ONCE.
Respects the 5/day submission cap. Never pushes more than this one kernel."""
import sys, types, re, unicodedata, subprocess, time, pathlib
from datetime import datetime, timezone
m = types.ModuleType('slugify')
def _sl(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', s).strip().lower())
m.slugify = _sl; sys.modules['slugify'] = m

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "chain_div941full.log"; VERD = ROOT / "chain_div941full.VERDICT.txt"
COMP = "biohub-cell-tracking-during-development"
PREV = "eeshsaxena/biohub-v-div941"
KID = "eeshsaxena/biohub-v-div941full"
FOLDER = str(ROOT / "scratch_kernels" / "v_div941full")
MSG = ("div941full: safe_div 9/14um + tau0.6 + DIVERGE 4.0 + adaptive secondary link "
       "(top-voted public recipe; diverge/adaptive upgrade over div941)")

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")
def cli(a):
    p = subprocess.run(["kaggle"] + a, capture_output=True, text=True)
    return "\n".join(l for l in ((p.stdout or "") + (p.stderr or "")).splitlines()
                     if "warn" not in l.lower() and "%|" not in l)
def status(kid):
    o = cli(["kernels", "status", kid])
    mm = re.search(r"KernelWorkerStatus\.(\w+)", o)
    return mm.group(1) if mm else ("ABSENT" if "404" in o else "UNKNOWN")
def subs_left():
    t = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    o = cli(["competitions", "submissions", COMP])
    return max(0, 5 - sum(1 for l in o.splitlines() if t in l))
def submit():
    for v in (1, 2, 3, 4, 5, 6):
        o = cli(["competitions", "submit", COMP, "-k", KID, "-f", "submission.csv", "-v", str(v), "-m", MSG])
        if "Successfully" in o or "remaining" in o:
            log(f"SUBMITTED v{v}: {o.strip()[:80]}"); return True
        if "Did not find" in o or "not found" in o.lower():
            continue
        log(f"submit v{v} -> {o.strip()[:100]}")
        if "Maximum" in o: return False
    log("no valid version to submit"); return False

def main():
    log("=== chain_div941full start ===")
    # 1) wait for the previous kernel to stop occupying the GPU shards
    for _ in range(160):  # ~8h
        st = status(PREV)
        if st in ("COMPLETE", "ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
            log(f"{PREV} -> {st}; proceeding"); break
        time.sleep(180)
    time.sleep(120)  # let the div941 watcher submit first
    if subs_left() <= 0:
        VERD.write_text("no submissions left today; div941full NOT pushed\n"); log("cap reached"); return
    # 2) push shot 2
    from kaggle.api.kaggle_api_extended import KaggleApi
    API = KaggleApi(); API.authenticate()
    try:
        API.kernels_push(FOLDER); log("pushed v_div941full")
    except Exception as e:
        VERD.write_text(f"push failed: {e}\n"); log(f"push failed: {e}"); return
    time.sleep(30)
    # 3) wait + submit
    for _ in range(160):
        st = status(KID)
        if st == "COMPLETE":
            ok = submit() if subs_left() > 0 else False
            VERD.write_text(f"div941full COMPLETE, submitted={ok}\n")
            log(f"=== DONE submitted={ok} ==="); return
        if st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
            VERD.write_text(f"div941full {st}; not submitted\n"); log(f"{st}"); return
        time.sleep(180)
    VERD.write_text("div941full timed out\n"); log("timeout")

if __name__ == "__main__":
    main()
