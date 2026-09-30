#!/usr/bin/env python3
"""
Cloud948 frontier pipeline (status-driven, idempotent, restartable).
- cloud948          : the 0.948 frontier floor. SUBMIT when COMPLETE (bank it).
- cloud948_base_n5  : frontier, 10-movie validator (CV base).
- cloud948_det098_n5: frontier + DET 0.980, 10-movie validator (own edge). PUSH when slot free.
When both N5 kernels COMPLETE: pull validators (prune submission.csv), run paired_cv,
write verdict to cloud_pipeline_VERDICT.txt. Does NOT auto-submit the edge (human decides).
"""
import sys, types, re, unicodedata, subprocess, json, time, pathlib
m=types.ModuleType('slugify')
def _sl(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',s).strip().lower())
m.slugify=_sl; sys.modules['slugify']=m
from kaggle.api.kaggle_api_extended import KaggleApi
API=KaggleApi(); API.authenticate()

ROOT=pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
COMP="biohub-cell-tracking-during-development"; USER="eeshsaxena"
LOG=ROOT/"cloud_pipeline.log"; STATE=ROOT/"cloud_pipeline_state.json"; VERDICT=ROOT/"cloud_pipeline_VERDICT.txt"
import datetime
def now(): return datetime.datetime.utcnow().strftime("%H:%M:%S")
def log(msg):
    line=f"[{now()}Z] {msg}"; print(line,flush=True)
    with open(LOG,"a",encoding="utf-8") as f: f.write(line+"\n")
def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {"submitted":[],"pushed":[],"cv_done":False}
def save(s): STATE.write_text(json.dumps(s,indent=2))
def cli(a):
    p=subprocess.run(["kaggle"]+a,capture_output=True,text=True)
    o=(p.stdout or "")+(p.stderr or "")
    return p.returncode,"\n".join(l for l in o.splitlines() if "Warning" not in l and "warnings.warn" not in l)
def status(kid):
    _,o=cli(["kernels","status",f"{USER}/{kid}"])
    mm=re.search(r'KernelWorkerStatus\.(\w+)',o)
    return mm.group(1) if mm else ("ABSENT" if "404" in o else "UNKNOWN")
def active():
    return sum(1 for k in ["biohub-v-cloud948","biohub-v-cloud948-base-n5","biohub-v-cloud948-det098-n5"] if status(k) in ("QUEUED","RUNNING"))
def push(folder,kid):
    try:
        r=API.kernels_push(str(ROOT/"scratch_kernels"/folder)); e=getattr(r,"error",None)
        if e and "Maximum batch" in str(e): return "SLOT_FULL"
        time.sleep(6)
        return "PUSHED" if status(kid) in ("QUEUED","RUNNING","COMPLETE") else f"NOSTATUS:{e}"
    except Exception as ex:
        return "SLOT_FULL" if "Maximum batch" in str(ex) else f"EXC:{type(ex).__name__}"
def submit_kernel(kid,desc):
    # bracket versions high->low; a wrong/errored version 400s "Did not find provided Notebook Output File"
    for v in [3,2,4,1,5]:
        rc,o=cli(["competitions","submit",COMP,"-k",f"{USER}/{kid}","-f","submission.csv","-v",str(v),"-m",desc])
        if "remaining" in o or "Successfully" in o:
            log(f"  SUBMITTED {kid} v{v}: {o.strip().splitlines()[-1][:60]}"); return True
        if "Did not find provided Notebook Output File" in o:
            continue
    log(f"  submit {kid} FAILED all versions: {o.strip()[:100]}"); return False
def pull_validator(kid,dst):
    d=ROOT/"scratch_kernels"/dst; d.mkdir(exist_ok=True)
    cli(["kernels","output",f"{USER}/{kid}","-p",str(d),"-q"])
    (d/"submission.csv").unlink(missing_ok=True)
    return (d/"validator_results.csv").exists()

def main():
    s=load()
    log(f"=== cloud pipeline start. state={s} ===")
    for it in range(120):
        # 1) push det098_n5 when slot free
        if "det098_n5" not in s["pushed"]:
            st=status("biohub-v-cloud948-det098-n5")
            if st in ("QUEUED","RUNNING","COMPLETE"):
                s["pushed"].append("det098_n5"); save(s)
            elif active()<2:
                r=push("v_cloud948_det098_n5","biohub-v-cloud948-det098-n5")
                if r=="PUSHED": s["pushed"].append("det098_n5"); save(s); log("  pushed det098_n5")
                else: log(f"  det098_n5 push: {r}")
        # 2) submit cloud948 floor when done
        if "cloud948" not in s["submitted"] and status("biohub-v-cloud948")=="COMPLETE":
            if submit_kernel("biohub-v-cloud948","cloud948 0.948 frontier replay (deepcenter SHA-refreshed) - selection floor"):
                s["submitted"].append("cloud948"); save(s)
        # 3) paired CV when both N5 done
        if not s["cv_done"]:
            b=status("biohub-v-cloud948-base-n5"); d=status("biohub-v-cloud948-det098-n5")
            if b=="COMPLETE" and d=="COMPLETE":
                okb=pull_validator("biohub-v-cloud948-base-n5","out_cloud_base")
                okd=pull_validator("biohub-v-cloud948-det098-n5","out_cloud_det098")
                if okb and okd:
                    rc,o=cli([]) if False else (0,"")
                    p=subprocess.run(["python",str(ROOT/"scratch_kernels"/"paired_cv.py"),
                        f"c948base=scratch_kernels/out_cloud_base/validator_results.csv",
                        f"c948det098=scratch_kernels/out_cloud_det098/validator_results.csv"],
                        capture_output=True,text=True,cwd=str(ROOT))
                    VERDICT.write_text(p.stdout)
                    log("  PAIRED CV (10-movie) written to cloud_pipeline_VERDICT.txt:")
                    for ln in p.stdout.splitlines(): log("    "+ln)
                    s["cv_done"]=True; save(s)
                else:
                    log(f"  validator pull incomplete (base={okb} det098={okd}); retry")
            elif b in ("ERROR",) or d in ("ERROR",):
                log(f"  N5 kernel error: base={b} det098={d}");
                if b=="ERROR" and d=="ERROR": s["cv_done"]=True; save(s)
        # done?
        if "cloud948" in s["submitted"] and (s["cv_done"] or ("det098_n5" not in s["pushed"] and False)):
            if s["cv_done"]:
                log("=== pipeline complete ==="); break
        time.sleep(90)
    else:
        log("=== iteration cap hit ===")

if __name__=="__main__":
    main()
