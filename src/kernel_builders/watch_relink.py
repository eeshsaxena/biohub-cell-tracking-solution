#!/usr/bin/env python3
"""Wait for biohub-v-relink, verify the zero-prob filter actually fired, then submit ONCE."""
import subprocess, re, time, pathlib, csv, io
ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT/"relink.log"; VERD = ROOT/"relink.VERDICT.txt"
KID = "eeshsaxena/biohub-v-relink"
COMP = "biohub-cell-tracking-during-development"
MSG = ("relink: drop zero-prob motion-relinked edges post-short-track, sparing forks "
       "(local +0.0098/+0.0108/+0.0155 on det .980/.955/.965, both embryos, divJ unchanged)")
OUT = ROOT/"data"/"out_relink"
def log(x):
    l=f"[{time.strftime('%H:%M:%SZ',time.gmtime())}] {x}"
    print(l,flush=True); open(LOG,"a",encoding="utf-8").write(l+"\n")
def cli(a,t=None):
    p=subprocess.run(["kaggle"]+a,capture_output=True,text=True,timeout=t)
    return "\n".join(l for l in ((p.stdout or "")+(p.stderr or "")).splitlines()
                     if "warn" not in l.lower() and "%|" not in l)
def status():
    m=re.search(r"KernelWorkerStatus\.(\w+)",cli(["kernels","status",KID]))
    return m.group(1) if m else "UNKNOWN"
def submit():
    for v in (1,2,3,4,5,6):
        o=cli(["competitions","submit",COMP,"-k",KID,"-f","submission.csv","-v",str(v),"-m",MSG])
        if "Successfully" in o or "remaining" in o:
            log(f"SUBMITTED v{v}: {o.strip()[:70]}"); return True
        if "Did not find" in o or "not found" in o.lower(): continue
        log(f"submit v{v} -> {o.strip()[:90]}")
        if "Maximum" in o: return False
    return False
def check_fired():
    OUT.mkdir(parents=True,exist_ok=True)
    cli(["kernels","output",KID,"-p",str(OUT),"-q"],t=7200)
    f=OUT/"run_stats.csv"
    if not f.exists(): return "no run_stats.csv"
    rows=list(csv.DictReader(io.open(f,encoding="utf-8")))
    d=sum(float(r.get("zeroprob_relink_dropped",0) or 0) for r in rows)
    s=sum(float(r.get("zeroprob_relink_spared_forks",0) or 0) for r in rows)
    return f"filter fired: dropped={d:.0f} spared_forks={s:.0f} over {len(rows)} datasets"
def main():
    log("=== watch_relink start ===")
    for _ in range(220):
        st=status()
        if st=="COMPLETE":
            log("COMPLETE -> submitting"); ok=submit()
            info=check_fired(); log(info)
            VERD.write_text(f"relink submitted={ok}\n{info}\n"); log("=== DONE ==="); return
        if st in ("ERROR","CANCEL_ACKNOWLEDGED","CANCEL_REQUESTED"):
            OUT.mkdir(parents=True,exist_ok=True)
            cli(["kernels","output",KID,"-p",str(OUT),"-q"],t=1800)
            lg=list(OUT.glob("*.log")); tail=lg[0].read_text(encoding="utf-8",errors="ignore")[-1200:] if lg else ""
            VERD.write_text(f"relink {st}\n{tail}\n"); log(f"{st}: {tail[-350:]}"); return
        time.sleep(120)
    VERD.write_text("timeout\n")
main()
