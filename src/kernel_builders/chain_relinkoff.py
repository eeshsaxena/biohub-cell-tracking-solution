#!/usr/bin/env python3
"""Wait for v_relink to finish (frees GPU shards + lets its watcher submit),
then push v_relinkoff and submit it ONCE. Respects the 5/day cap."""
import sys, types, re, unicodedata, subprocess, time, pathlib
from datetime import datetime, timezone
m = types.ModuleType('slugify')
def _sl(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',s).strip().lower())
m.slugify=_sl; sys.modules['slugify']=m
from kaggle.api.kaggle_api_extended import KaggleApi
API=KaggleApi(); API.authenticate()

ROOT=pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG=ROOT/"relinkoff.log"; VERD=ROOT/"relinkoff.VERDICT.txt"
COMP="biohub-cell-tracking-during-development"
PREV="eeshsaxena/biohub-v-relink"
KID="eeshsaxena/biohub-v-relinkoff"
FOLDER=str(ROOT/"scratch_kernels"/"v_relinkoff")
MSG=("relinkoff: BIOHUB_OUTPUT_MOTION_RELINK=0 - raw learned edges + single-parent repair "
     "beat Hungarian relink (Pareto: edge TP 11957->12021, FP 614->445; +0.0146/.980 +0.0182/.955, both embryos)")
def log(x):
    l=f"[{time.strftime('%H:%M:%SZ',time.gmtime())}] {x}"
    print(l,flush=True); open(LOG,"a",encoding="utf-8").write(l+"\n")
def cli(a,t=None):
    p=subprocess.run(["kaggle"]+a,capture_output=True,text=True,timeout=t)
    return "\n".join(l for l in ((p.stdout or "")+(p.stderr or "")).splitlines()
                     if "warn" not in l.lower() and "%|" not in l)
def status(k):
    o=cli(["kernels","status",k]); mm=re.search(r"KernelWorkerStatus\.(\w+)",o)
    return mm.group(1) if mm else ("ABSENT" if "404" in o else "UNKNOWN")
def subs_left():
    t=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    o=cli(["competitions","submissions",COMP])
    return max(0,5-sum(1 for l in o.splitlines() if t in l))
def submit():
    for v in (1,2,3,4,5,6):
        o=cli(["competitions","submit",COMP,"-k",KID,"-f","submission.csv","-v",str(v),"-m",MSG])
        if "Successfully" in o or "remaining" in o:
            log(f"SUBMITTED v{v}: {o.strip()[:70]}"); return True
        if "Did not find" in o or "not found" in o.lower(): continue
        log(f"submit v{v} -> {o.strip()[:90]}")
        if "Maximum" in o: return False
    return False
def main():
    log("=== chain_relinkoff start ===")
    for _ in range(200):
        st=status(PREV)
        if st in ("COMPLETE","ERROR","CANCEL_ACKNOWLEDGED","CANCEL_REQUESTED"):
            log(f"{PREV} -> {st}; proceeding"); break
        time.sleep(120)
    time.sleep(150)   # let the relink watcher submit first
    if subs_left()<=0:
        VERD.write_text("no slots left; relinkoff NOT pushed\n"); log("cap reached"); return
    try:
        API.kernels_push(FOLDER); log("pushed v_relinkoff")
    except Exception as e:
        VERD.write_text(f"push failed: {e}\n"); log(f"push failed: {e}"); return
    time.sleep(30)
    for _ in range(200):
        st=status(KID)
        if st=="COMPLETE":
            ok=submit() if subs_left()>0 else False
            VERD.write_text(f"relinkoff COMPLETE submitted={ok}\n"); log(f"=== DONE submitted={ok} ==="); return
        if st in ("ERROR","CANCEL_ACKNOWLEDGED","CANCEL_REQUESTED"):
            VERD.write_text(f"relinkoff {st}\n"); log(st); return
        time.sleep(120)
    VERD.write_text("relinkoff timeout\n")
main()
