#!/usr/bin/env python3
"""After det096 drains: push+submit v_946 (the 0.946 shelf recipe), then v_ed0943."""
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
LOG=ROOT/"chain946.log"; COMP="biohub-cell-tracking-during-development"
JOBS=[("eeshsaxena/biohub-v-946", str(ROOT/"scratch_kernels"/"v_946"),
       "946: reyhanksatria 0.946-LB recipe (EDGE_FEATURE_TTA=1 + MOTION_RELINK_LEARNED_BONUS=1.0 + wide gates 9/14), mirrors repointed to public pilkwang datasets"),
      ("eeshsaxena/biohub-v-ed0943", str(ROOT/"scratch_kernels"/"v_ed0943"),
       "ed0943: adaptive_grouped_confidence_dominance arm + dense-edge + sec_det 0.475")]
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
def submit(kid,msg):
    for v in (1,2,3,4,5,6,7):
        o=cli(["competitions","submit",COMP,"-k",kid,"-f","submission.csv","-v",str(v),"-m",msg])
        if "Successfully" in o or "remaining" in o: log(f"SUBMITTED {kid} v{v}"); return True
        if "Did not find" in o or "not found" in o.lower(): continue
        log(f"submit {kid} v{v}: {o.strip()[:80]}")
        if "Maximum" in o: return False
    return False
log("=== chain946 start: waiting for det096 ===")
for _ in range(240):
    if st("eeshsaxena/biohub-v-det096") not in ("RUNNING","QUEUED"): break
    time.sleep(120)
log("det096 drained")
for kid,folder,msg in JOBS:
    if slots()<=0: log("no slots left"); break
    try: API.kernels_push(folder); log(f"pushed {kid}")
    except Exception as e: log(f"push {kid} failed: {e}"); continue
    time.sleep(30)
    ok=False
    for _ in range(200):
        s=st(kid)
        if s=="COMPLETE": ok=True; break
        if s in ("ERROR","CANCEL_ACKNOWLEDGED"): log(f"{kid} {s}"); break
        time.sleep(120)
    if ok: submit(kid,msg)
log("=== chain946 done ===")
