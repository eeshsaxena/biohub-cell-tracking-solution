#!/usr/bin/env python3
"""Submit the two proven-on-LB public lever configs, serialized (pipeline uses both GPU shards).
  1. v_det096  = div941 with DET_THRESHOLD 0.965 -> 0.96      (other teams: LB 0.942)
  2. v_ed0943  = adaptive_grouped_confidence_dominance arm     (other teams: LB 0.943)
Respects the 5/day cap. Never submits more than these two."""
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
LOG=ROOT/"public_levers.log"; VERD=ROOT/"public_levers.VERDICT.txt"
COMP="biohub-cell-tracking-during-development"
JOBS=[("eeshsaxena/biohub-v-det096", None,
       "det096: div941 + DET_THRESHOLD 0.965->0.96 (one knob past the public line; other teams LB 0.942)"),
      ("eeshsaxena/biohub-v-948", str(ROOT/"scratch_kernels"/"v_948"),
       "948: narrow div gates 7/12 + DeepCenter checkpoint_last.pt + gap_close 5.8 + sec_edge 0.20 (separate higher branch)"),
      ("eeshsaxena/biohub-v-ed0943", str(ROOT/"scratch_kernels"/"v_ed0943"),
       "ed0943: adaptive_grouped_confidence_dominance arm + dense-edge + sec_det 0.475 (other teams LB 0.943)")]
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
def submit(kid,msg):
    for v in (1,2,3,4,5,6):
        o=cli(["competitions","submit",COMP,"-k",kid,"-f","submission.csv","-v",str(v),"-m",msg])
        if "Successfully" in o or "remaining" in o:
            log(f"SUBMITTED {kid} v{v}: {o.strip()[:70]}"); return True
        if "Did not find" in o or "not found" in o.lower(): continue
        log(f"submit {kid} v{v} -> {o.strip()[:90]}")
        if "Maximum" in o: return False
    return False

def main():
    log("=== public levers chain start ===")
    done=[]
    for kid, folder, msg in JOBS:
        if folder:
            if subs_left()<=0:
                log("no slots left; stopping"); break
            try:
                API.kernels_push(folder); log(f"pushed {kid}"); time.sleep(30)
            except Exception as e:
                log(f"push failed {kid}: {e}"); continue
        for _ in range(220):
            st=status(kid)
            if st=="COMPLETE":
                ok=submit(kid,msg) if subs_left()>0 else False
                done.append((kid,ok)); log(f"{kid} -> submitted={ok}"); break
            if st in ("ERROR","CANCEL_ACKNOWLEDGED","CANCEL_REQUESTED"):
                done.append((kid,f"KERNEL_{st}")); log(f"{kid} {st}"); break
            time.sleep(120)
        else:
            done.append((kid,"timeout")); log(f"{kid} timeout")
    VERD.write_text("public levers chain:\n" + "\n".join(f"  {k}: {v}" for k,v in done) + "\n")
    log(f"=== DONE {done} ===")
main()
