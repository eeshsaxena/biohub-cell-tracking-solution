#!/usr/bin/env python3
"""Clean waiter: submit cloud948 (0.948 floor) when COMPLETE; when cloud948 +
det098v2 both COMPLETE, pull 4-movie validators and run paired_cv -> VERDICT file.
Does NOT auto-submit the det098 edge."""
import sys, types, re, unicodedata, subprocess, json, time, pathlib, datetime
m=types.ModuleType('slugify')
def _sl(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',s).strip().lower())
m.slugify=_sl; sys.modules['slugify']=m
from kaggle.api.kaggle_api_extended import KaggleApi
API=KaggleApi(); API.authenticate()
ROOT=pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
COMP="biohub-cell-tracking-during-development"; USER="eeshsaxena"
LOG=ROOT/"cloud_wait.log"; VERD=ROOT/"cloud_wait_VERDICT.txt"; ST=ROOT/"cloud_wait_state.json"
def now(): return datetime.datetime.utcnow().strftime("%H:%M:%S")
def log(m):
    l=f"[{now()}Z] {m}"; print(l,flush=True); open(LOG,"a",encoding="utf-8").write(l+"\n")
def cli(a):
    p=subprocess.run(["kaggle"]+a,capture_output=True,text=True)
    return "\n".join(x for x in ((p.stdout or "")+(p.stderr or "")).splitlines() if "Warning" not in x and "warnings.warn" not in x)
def status(k):
    o=cli(["kernels","status",f"{USER}/{k}"]); mm=re.search(r'KernelWorkerStatus\.(\w+)',o)
    return mm.group(1) if mm else ("ABSENT" if "404" in o else "?")
def submit(k,desc):
    for v in [3,2,4,1,5]:
        o=cli(["competitions","submit",COMP,"-k",f"{USER}/{k}","-f","submission.csv","-v",str(v),"-m",desc])
        if "remaining" in o or "Successfully" in o: log(f"SUBMITTED {k} v{v}: {o.splitlines()[-1][:60]}"); return True
        if "Did not find provided Notebook Output File" in o: continue
    log(f"submit {k} failed: {o[:100]}"); return False
def pull(k,dst):
    d=ROOT/"scratch_kernels"/dst; d.mkdir(exist_ok=True)
    cli(["kernels","output",f"{USER}/{k}","-p",str(d),"-q"]); (d/"submission.csv").unlink(missing_ok=True)
    return (d/"validator_results.csv").exists()
def load(): return json.loads(ST.read_text()) if ST.exists() else {"sub":False,"cv":False}
def save(s): ST.write_text(json.dumps(s))
s=load(); log(f"start state={s}")
for _ in range(120):
    if not s["sub"] and status("biohub-v-cloud948")=="COMPLETE":
        if submit("biohub-v-cloud948","cloud948 0.948 frontier replay (deepcenter SHA-refreshed) - selection floor"): s["sub"]=True; save(s)
    if not s["cv"]:
        c=status("biohub-v-cloud948"); d=status("biohub-v-cloud948-det098v2")
        if c=="COMPLETE" and d=="COMPLETE":
            okc=pull("biohub-v-cloud948","out_cloud948"); okd=pull("biohub-v-cloud948-det098v2","out_det098v2")
            if okc and okd:
                p=subprocess.run(["python",str(ROOT/"scratch_kernels"/"paired_cv.py"),
                    "c948=scratch_kernels/out_cloud948/validator_results.csv",
                    "c948_det098=scratch_kernels/out_det098v2/validator_results.csv"],
                    capture_output=True,text=True,cwd=str(ROOT))
                VERD.write_text(p.stdout); log("PAIRED CV (det098 edge vs cloud948 base):")
                for ln in p.stdout.splitlines(): log("  "+ln)
                s["cv"]=True; save(s)
            else: log(f"pull incomplete c948={okc} det098={okd}")
        elif d=="ERROR": log("det098v2 ERROR"); s["cv"]=True; save(s)
    if s["sub"] and s["cv"]: log("done"); break
    time.sleep(90)
