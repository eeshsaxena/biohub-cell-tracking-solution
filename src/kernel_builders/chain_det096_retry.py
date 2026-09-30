#!/usr/bin/env python3
"""Wait for the main lever chain to drain, then push+submit the rebuilt det096."""
import sys, types, re, unicodedata, subprocess, time, pathlib
from datetime import datetime, timezone
m=types.ModuleType('slugify')
def _sl(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',s).strip().lower())
m.slugify=_sl; sys.modules['slugify']=m
from kaggle.api.kaggle_api_extended import KaggleApi
API=KaggleApi(); API.authenticate()
ROOT=pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG=ROOT/"det096_retry.log"
COMP="biohub-cell-tracking-during-development"
KID="eeshsaxena/biohub-v-det096"
FOLDER=str(ROOT/"scratch_kernels"/"v_det096")
MSG="det096 (rebuilt from our div941 base): DET_THRESHOLD 0.965->0.96, guard patched in lockstep"
def log(x):
    l=f"[{time.strftime('%H:%M:%SZ',time.gmtime())}] {x}"
    print(l,flush=True); open(LOG,"a",encoding="utf-8").write(l+"\n")
def cli(a,t=None):
    p=subprocess.run(["kaggle"]+a,capture_output=True,text=True,timeout=t)
    return "\n".join(l for l in ((p.stdout or "")+(p.stderr or "")).splitlines()
                     if "warn" not in l.lower() and "%|" not in l)
def st(k):
    o=cli(["kernels","status",k]); mm=re.search(r"KernelWorkerStatus\.(\w+)",o)
    return mm.group(1) if mm else ("ABSENT" if "404" in o else "UNKNOWN")
def slots():
    t=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return max(0,5-sum(1 for l in cli(["competitions","submissions",COMP]).splitlines() if t in l))
def busy():
    return any(st(k) in ("RUNNING","QUEUED") for k in
               ["eeshsaxena/biohub-v-948","eeshsaxena/biohub-v-ed0943"])
log("=== det096 retry chain start ===")
for _ in range(240):
    if not busy(): log("prior kernels drained"); break
    time.sleep(120)
if slots()<=0: log("no slots left"); sys.exit()
try: API.kernels_push(FOLDER); log("pushed det096")
except Exception as e: log(f"push failed: {e}"); sys.exit()
time.sleep(30)
for _ in range(200):
    s=st(KID)
    if s=="COMPLETE":
        for v in (1,2,3,4,5,6,7):
            o=cli(["competitions","submit",COMP,"-k",KID,"-f","submission.csv","-v",str(v),"-m",MSG])
            if "Successfully" in o or "remaining" in o: log(f"SUBMITTED v{v}"); break
            if "Did not find" in o or "not found" in o.lower(): continue
            log(f"submit v{v}: {o.strip()[:80]}")
            if "Maximum" in o: break
        break
    if s in ("ERROR","CANCEL_ACKNOWLEDGED"):
        log(f"det096 {s}"); break
    time.sleep(120)
log("=== done ===")
