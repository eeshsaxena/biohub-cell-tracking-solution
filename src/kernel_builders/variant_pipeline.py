#!/usr/bin/env python3
"""
Variant submission pipeline for the 5 single-knob grafael-0940 variants.
Status-driven and idempotent:
  - COMPLETE            -> verify submission.csv, submit (once), mark submitted
  - ERROR/CANCEL/ABSENT -> (re)push if a GPU slot is free and attempts < MAX
  - QUEUED/RUNNING      -> wait
Never submits the fork. Caps attempts per variant. State persisted / restartable.
Push via slugify-injected API; status/output/submit via the 3.12 kaggle CLI.
"""
import sys, types, re, unicodedata, subprocess, json, time, pathlib, datetime

# --- slugify shim so kernels_push works despite the broken v0.0.1 stub ---
_m = types.ModuleType('slugify')
def _slugify(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^\w\s-]', '', s).strip().lower()
    return re.sub(r'[-\s]+', '-', s)
_m.slugify = _slugify
sys.modules['slugify'] = _m
from kaggle.api.kaggle_api_extended import KaggleApi
API = KaggleApi(); API.authenticate()

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
COMP = "biohub-cell-tracking-during-development"
USER = "eeshsaxena"
STATE = ROOT / "variant_pipeline_state.json"
LOG = ROOT / "variant_pipeline.log"
MAX_ATTEMPTS = 2

VARIANTS = [
    ("det096",   "v_det096",   "grafael-0940 stack, DET_THRESHOLD 0.96875->0.960 (recall bracket; guard updated)"),
    ("det098",   "v_det098",   "grafael-0940 stack, DET_THRESHOLD 0.96875->0.980 (precision bracket; guard updated)"),
    ("sec080",   "v_sec080",   "grafael-0940 stack, SECONDARY_DETECTION_WEIGHT 0.475->0.80 (public-fork disagreement)"),
    ("bidir040", "v_bidir040", "grafael-0940 stack, BIDIRECTIONAL_EDGE_WEIGHT 0.30->0.40 (push proven lever; guard updated)"),
    ("gap2on",   "v_gap2on",   "grafael-0940 stack, OUTPUT_GAP2_RECOVERY 0->1 (enable disabled recall lever)"),
]
KID = {n: f"{USER}/biohub-v-{n}" for n, _, _ in VARIANTS}
FORK = f"{USER}/biohub-0940-fork"
EXPECTED_COLS = "id,dataset,row_type,node_id,t,z,y,x,source_id,target_id"

def now(): return datetime.datetime.utcnow().strftime("%H:%M:%S")
def log(msg):
    line = f"[{now()}Z] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")

def load_state():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"submitted": [], "failed": [], "attempts": {}, "scores": {}}
def save_state(s): STATE.write_text(json.dumps(s, indent=2))

def cli(args):
    p = subprocess.run(["kaggle"] + args, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    out = "\n".join(l for l in out.splitlines()
                     if "RequestsDependencyWarning" not in l and "warnings.warn" not in l)
    return p.returncode, out

def status(kid):
    _, out = cli(["kernels", "status", kid])
    m = re.search(r'KernelWorkerStatus\.(\w+)', out)
    if m: return m.group(1)
    if "404" in out or "Not Found" in out: return "ABSENT"
    return "UNKNOWN"

def active_gpu_count():
    n = 0
    for kid in list(KID.values()) + [FORK]:
        if status(kid) in ("QUEUED", "RUNNING"): n += 1
    return n

def push(name):
    folder = dict((n, f) for n, f, _ in VARIANTS)[name]
    try:
        r = API.kernels_push(str(ROOT / "scratch_kernels" / folder))
        err = getattr(r, "error", None)
        if err and "Maximum batch" in str(err): return "SLOT_FULL"
        time.sleep(6)
        if status(KID[name]) in ("QUEUED", "RUNNING", "COMPLETE"): return "PUSHED"
        return f"NOSTATUS({err})"
    except Exception as e:
        if "Maximum batch" in str(e): return "SLOT_FULL"
        return f"EXC:{type(e).__name__}"

def verify_and_submit(name, desc):
    outdir = ROOT / "scratch_kernels" / f"out_v_{name}"
    outdir.mkdir(exist_ok=True)
    cli(["kernels", "output", KID[name], "-p", str(outdir)])
    csv = outdir / "submission.csv"
    if not csv.exists():
        log(f"  {name}: NO submission.csv -> FAIL"); return False
    with open(csv, "r", encoding="utf-8") as f: header = f.readline().strip()
    rows = sum(1 for _ in open(csv, "r", encoding="utf-8")) - 1
    if header != EXPECTED_COLS:
        log(f"  {name}: header mismatch -> FAIL"); return False
    if rows < 50000:
        log(f"  {name}: only {rows} rows -> FAIL"); return False
    log(f"  {name}: CSV OK ({rows} rows). Submitting...")
    rc, out = cli(["competitions", "submit", COMP, "-f", str(csv), "-m", desc])
    if "Successfully submitted" in out or rc == 0:
        log(f"  {name}: SUBMITTED ({out.strip()[:70]})"); return True
    log(f"  {name}: submit FAILED rc={rc} ({out.strip()[:100]})"); return False

def main():
    st = load_state()
    st.setdefault("attempts", {})
    # seed prior attempts so already-run kernels don't get infinite retries
    for n, cnt in {"det096": 1, "det098": 1, "sec080": 1}.items():
        st["attempts"].setdefault(n, cnt)
    save_state(st)
    log("=== pipeline start (status-driven). submitted=%s failed=%s attempts=%s ===" %
        (st["submitted"], st["failed"], st["attempts"]))

    for it in range(160):  # ~5.3h cap at 120s
        pushed_this_iter = False
        for name, folder, desc in VARIANTS:
            if name in st["submitted"] or name in st["failed"]:
                continue
            s = status(KID[name])
            if s == "COMPLETE":
                ok = verify_and_submit(name, desc)
                (st["submitted"] if ok else st["failed"]).append(name); save_state(st)
            elif s in ("QUEUED", "RUNNING"):
                pass  # wait
            elif s in ("ERROR", "ABSENT", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED", "UNKNOWN"):
                att = st["attempts"].get(name, 0)
                if att >= MAX_ATTEMPTS:
                    log(f"  {name}: {s}, attempts={att} exhausted -> FAIL")
                    st["failed"].append(name); save_state(st); continue
                if pushed_this_iter:
                    continue  # one push per iteration
                if active_gpu_count() < 2:
                    res = push(name)
                    if res == "PUSHED":
                        st["attempts"][name] = att + 1; save_state(st)
                        log(f"  {name}: pushed (attempt {att+1})"); pushed_this_iter = True
                    elif res == "SLOT_FULL":
                        pass
                    else:
                        log(f"  {name}: push -> {res} (retry later)")
        if all(n in st["submitted"] or n in st["failed"] for n, _, _ in VARIANTS):
            log("=== ALL TERMINAL. submitted=%s failed=%s ===" % (st["submitted"], st["failed"]))
            break
        time.sleep(120)
    else:
        log("=== hit iteration cap; stopping. state=%s ===" % st)

if __name__ == "__main__":
    main()
