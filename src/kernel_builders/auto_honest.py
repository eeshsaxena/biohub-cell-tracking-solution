#!/usr/bin/env python3
"""Autonomous honest-submission pipeline (GPU is back).
- SUBMIT honest_nodiv + honest_stack the moment each COMPLETEs (version-bracketed). 2 subs only.
- Keep the GPU busy: push dsw096/097/098 (safe_div-off threshold CV, NO submit) into freed slots.
- Collect validator CV from the dsw runs. Log to auto_honest.log. Cap: never submit >5/day."""
import sys, types, re, unicodedata, subprocess, time, pathlib, glob, json
m = types.ModuleType('slugify')
def _sl(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', s).strip().lower())
m.slugify = _sl; sys.modules['slugify'] = m
from kaggle.api.kaggle_api_extended import KaggleApi
API = KaggleApi(); API.authenticate()

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
COMP = "biohub-cell-tracking-during-development"
LOG = ROOT / "auto_honest.log"; VERD = ROOT / "auto_honest_VERDICT.txt"
def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")

SUBMIT = {  # name -> submit message
    "honest-nodiv": "honest: safe_div OFF + min_track_len8 + tip/weak-node prune (post-rescore optimal)",
    "honest-stack": "honest: safe_div ON + min_track_len8 + tip/weak-node prune (pre-rescore hedge)",
}
OCCUPY = ["dsw096", "dsw097", "dsw098"]   # CV only, NO submit
def kid(n): return "eeshsaxena/biohub-v-" + n
def folder(n): return str(ROOT / "scratch_kernels" / ("v_" + n.replace("-", "_")))

def cli(args):
    p = subprocess.run(["kaggle"] + args, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return "\n".join(l for l in out.splitlines() if "RequestsDependencyWarning" not in l and "warnings.warn" not in l)
def status(n):
    o = cli(["kernels", "status", kid(n)])
    mm = re.search(r"KernelWorkerStatus\.(\w+)", o)
    return mm.group(1) if mm else ("ABSENT" if "404" in o else "UNKNOWN")
def subs_today():
    from datetime import datetime, timezone
    t = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return sum(1 for s in API.competition_submissions(COMP) if str(s.date).startswith(t))
def push(n):
    try:
        r = API.kernels_push(folder(n)); e = getattr(r, "error", None)
        if e and "Maximum" in str(e): return "SLOT_FULL"
        time.sleep(6)
        return "PUSHED" if status(n) in ("QUEUED", "RUNNING", "COMPLETE") else "RETRY"
    except Exception as ex:
        return "SLOT_FULL" if "Maximum" in str(ex) else f"ERR:{str(ex)[:50]}"
def submit(n, msg):
    for v in (1, 2, 3, 4):
        o = cli(["competitions", "submit", COMP, "-k", kid(n), "-f", "submission.csv", "-v", str(v), "-m", msg])
        o = "\n".join(l for l in o.splitlines() if "%|" not in l)
        if "remaining" in o or "Successfully" in o:
            log(f"  SUBMITTED {n} v{v}: {o.strip()[:60]}"); return True
        if "Did not find" in o or "not found" in o.lower():
            continue
        log(f"  submit {n} v{v} -> {o.strip()[:90]}")
        if "Maximum" in o: return False
    log(f"  {n}: no valid version found to submit"); return False
def pull_cv(n):
    d = ROOT / "scratch_kernels" / ("out_" + n); d.mkdir(exist_ok=True)
    cli(["kernels", "output", kid(n), "-p", str(d), "-q"])
    f = d / "validator_results.csv"
    try:
        import csv, io
        rows = list(csv.DictReader(io.open(f, encoding="utf-8")))
        adj = sum(float(r["adjusted_edge_jaccard"]) for r in rows) / len(rows)
        return round(adj, 4), len(rows)
    except Exception:
        return None, 0

def main():
    submitted, failed, occ_pushed, cv = set(), set(), set(), {}
    log("=== auto_honest start. subs_today=%d ===" % subs_today())
    for _ in range(200):  # ~5h at 90s
        # 1) submit completed honest kernels
        for n, msg in SUBMIT.items():
            if n in submitted or n in failed: continue
            st = status(n)
            if st == "COMPLETE":
                if subs_today() >= 5:
                    log(f"  {n}: daily cap reached, not submitting"); failed.add(n); continue
                (submitted if submit(n, msg) else failed).add(n)
            elif st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
                log(f"  {n}: {st} -> will not submit"); failed.add(n)
        # 2) occupy freed slots with dsw CV runs
        active = sum(1 for n in list(SUBMIT) + list(occ_pushed) if status(n) in ("QUEUED", "RUNNING"))
        if active < 2 and OCCUPY:
            nxt = OCCUPY[0]; r = push(nxt)
            if r == "PUSHED": occ_pushed.add(nxt); OCCUPY.pop(0); log(f"  occupy: pushed {nxt} (CV)")
            elif r != "SLOT_FULL": log(f"  occupy {nxt}: {r}")
        # 3) collect dsw CVs
        for n in list(occ_pushed):
            if n not in cv and status(n) == "COMPLETE":
                adj, k = pull_cv(n); cv[n] = adj; log(f"  CV {n}: adjEJ={adj} ({k} movies)")
        # 4) done?
        done_sub = all(n in submitted or n in failed for n in SUBMIT)
        done_occ = not OCCUPY and all(status(n) in ("COMPLETE", "ERROR") for n in occ_pushed)
        if done_sub and done_occ:
            break
        time.sleep(90)
    VERD.write_text("AUTO HONEST VERDICT\nsubmitted=%s failed=%s\nthreshold CV (safe_div off): %s\n"
                    % (sorted(submitted), sorted(failed), cv))
    log("=== DONE. submitted=%s failed=%s CV=%s ===" % (sorted(submitted), sorted(failed), cv))

if __name__ == "__main__":
    main()
