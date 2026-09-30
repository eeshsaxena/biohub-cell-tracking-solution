#!/usr/bin/env python3
"""Frontier detection-threshold sweep: submit ALL 4 points (research), push the
two un-run points as slots free, collect validators. Dedup vs live submissions
so cloud948 is never double-submitted."""
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
LOG=ROOT/"sweep_pipeline.log"; ST=ROOT/"sweep_state.json"

# (short, kernel-id, submit-desc(has unique tag), push-folder or None, out-dir)
K=[
 ("c948_0965","biohub-v-cloud948",         "[sweep0965] cloud948 0.948 frontier floor (DET 0.965)",          None,                    "out_sw_0965"),
 ("c948_0970","biohub-v-c948-det0970",       "[sweep0970] frontier + DET_THRESHOLD 0.965->0.970",             "v_c948-det0970",        "out_sw_0970"),
 ("c948_0980","biohub-v-cloud948-det098v2", "[sweep0980] frontier + DET_THRESHOLD 0.965->0.980 (our CV lever)","None",                 "out_sw_0980"),
 ("c948_0985","biohub-v-c948-det0985",       "[sweep0985] frontier + DET_THRESHOLD 0.965->0.985",             "v_c948-det0985",        "out_sw_0985"),
]
for i,(s,k,desc,pf,od) in enumerate(K):
    if pf=="None": K[i]=(s,k,desc,None,od)

def now(): return datetime.datetime.utcnow().strftime("%H:%M:%S")
def log(x):
    l=f"[{now()}Z] {x}"; print(l,flush=True); open(LOG,"a",encoding="utf-8").write(l+"\n")
def cli(a):
    p=subprocess.run(["kaggle"]+a,capture_output=True,text=True)
    return "\n".join(x for x in ((p.stdout or "")+(p.stderr or "")).splitlines() if "Warning" not in x and "warnings.warn" not in x)
def status(k):
    o=cli(["kernels","status",f"{USER}/{k}"]); mm=re.search(r'KernelWorkerStatus\.(\w+)',o)
    return mm.group(1) if mm else ("ABSENT" if "404" in o else "?")
def active():
    return sum(1 for _,k,_,_,_ in K if status(k) in ("QUEUED","RUNNING"))
def submitted_tags():
    try:
        subs=API.competition_submissions(COMP)
        return " ".join((x.description or "") for x in subs[:25])
    except Exception: return ""
def push(pf,kid):
    try:
        r=API.kernels_push(str(ROOT/"scratch_kernels"/pf)); e=getattr(r,"error",None)
        if e and "Maximum batch" in str(e): return "SLOT_FULL"
        time.sleep(6); return "PUSHED" if status(kid) in ("QUEUED","RUNNING","COMPLETE") else f"NO:{e}"
    except Exception as ex: return "SLOT_FULL" if "Maximum batch" in str(ex) else f"EXC:{type(ex).__name__}"
def submit(kid,desc):
    for v in [3,2,4,1,5,6]:
        o=cli(["competitions","submit",COMP,"-k",f"{USER}/{kid}","-f","submission.csv","-v",str(v),"-m",desc])
        if "remaining" in o or "Successfully" in o: log(f"SUBMITTED {kid} v{v}: {o.splitlines()[-1][:55]}"); return True
        if "Did not find provided Notebook Output File" in o: continue
        if "reached your submission limit" in o.lower() or "maximum" in o.lower() and "submission" in o.lower():
            log(f"DAILY LIMIT hit submitting {kid}: {o[:80]}"); return "LIMIT"
    log(f"submit {kid} FAILED: {o[:90]}"); return False
def pull(kid,od):
    d=ROOT/"scratch_kernels"/od; d.mkdir(exist_ok=True)
    cli(["kernels","output",f"{USER}/{kid}","-p",str(d),"-q"]); (d/"submission.csv").unlink(missing_ok=True)
    return (d/"validator_results.csv").exists()
def load(): return json.loads(ST.read_text()) if ST.exists() else {"submitted":[],"pushed":[],"pulled":[]}
def save(s): ST.write_text(json.dumps(s,indent=2))

s=load(); log(f"sweep start state={s}")
for _ in range(140):
    tags=submitted_tags()
    for short,kid,desc,pf,od in K:
        tag=re.search(r'\[sweep\d+\]',desc).group(0)
        # dedup: if the unique tag already appears in live submissions, mark submitted
        if short not in s["submitted"] and tag in tags:
            s["submitted"].append(short); save(s); log(f"{short} already submitted (dedup {tag})")
        # push un-run
        if pf and short not in s["pushed"]:
            st=status(kid)
            if st in ("QUEUED","RUNNING","COMPLETE"): s["pushed"].append(short); save(s)
            elif active()<2:
                r=push(pf,kid)
                if r=="PUSHED": s["pushed"].append(short); save(s); log(f"pushed {short}")
                else: log(f"{short} push: {r}")
        # submit + pull when COMPLETE
        if short not in s["submitted"] and status(kid)=="COMPLETE":
            r=submit(kid,desc)
            if r is True: s["submitted"].append(short); save(s)
            elif r=="LIMIT": log("stopping submits (daily limit)")
        if short not in s["pulled"] and status(kid)=="COMPLETE":
            if pull(kid,od): s["pulled"].append(short); save(s); log(f"pulled validator {short}")
    if all(short in s["submitted"] for short,_,_,_,_ in K):
        log("=== all 4 sweep points submitted ==="); break
    time.sleep(90)
# final CV table if validators present
paths=[f"{short.replace('c948_','t')}=scratch_kernels/{od}/validator_results.csv" for short,_,_,_,od in K if short in s["pulled"]]
if paths:
    p=subprocess.run(["python",str(ROOT/"scratch_kernels"/"paired_cv.py")]+paths,capture_output=True,text=True,cwd=str(ROOT))
    (ROOT/"sweep_VERDICT.txt").write_text(p.stdout); log("PAIRED CV sweep:")
    for ln in p.stdout.splitlines(): log("  "+ln)
