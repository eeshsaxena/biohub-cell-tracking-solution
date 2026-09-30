#!/usr/bin/env python3
"""Wait for biohub-v-det955val, submit ONCE, then pull the 20-movie validator CV.
The CV is the real prize: our first divJ measurement on the EXACT production config
(VALIDATOR_N_PER_TYPE=10 -> 20 movies instead of the usual 4)."""
import subprocess, re, time, pathlib, csv, io

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "det955.log"; VERD = ROOT / "det955.VERDICT.txt"
KID = "eeshsaxena/biohub-v-det955val"
COMP = "biohub-cell-tracking-during-development"
MSG = "det955val: div941 recipe + DET_THRESHOLD 0.965->0.955 (target missing 2nd daughters) + 20-movie validator"
OUT = ROOT / "data" / "out_det955"

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")
def cli(a, t=None):
    p = subprocess.run(["kaggle"] + a, capture_output=True, text=True, timeout=t)
    return "\n".join(l for l in ((p.stdout or "") + (p.stderr or "")).splitlines()
                     if "warn" not in l.lower() and "%|" not in l)
def status():
    m = re.search(r"KernelWorkerStatus\.(\w+)", cli(["kernels", "status", KID]))
    return m.group(1) if m else "UNKNOWN"

def submit():
    for v in (1, 2, 3, 4, 5, 6):
        o = cli(["competitions", "submit", COMP, "-k", KID, "-f", "submission.csv", "-v", str(v), "-m", MSG])
        if "Successfully" in o or "remaining" in o:
            log(f"SUBMITTED v{v}: {o.strip()[:70]}"); return True
        if "Did not find" in o or "not found" in o.lower():
            continue
        log(f"submit v{v} -> {o.strip()[:90]}")
        if "Maximum" in o: return False
    return False

def cv():
    OUT.mkdir(parents=True, exist_ok=True)
    cli(["kernels", "output", KID, "-p", str(OUT), "-q"], t=7200)
    f = OUT / "validator_results.csv"
    if not f.exists():
        log("no validator_results.csv"); return None
    rows = list(csv.DictReader(io.open(f, encoding="utf-8")))
    tp = sum(float(r.get("div_tp", 0) or 0) for r in rows)
    fp = sum(float(r.get("div_fp", 0) or 0) for r in rows)
    fn = sum(float(r.get("div_fn", 0) or 0) for r in rows)
    adj = sum(float(r["adjusted_edge_jaccard"]) for r in rows) / max(1, len(rows))
    micro = tp / (tp + fp + fn) if (tp + fp + fn) else float("nan")
    s = (f"movies={len(rows)}  mean adjEJ={adj:.5f}\n"
         f"divisions TP={tp:.0f} FP={fp:.0f} FN={fn:.0f}  micro divJ={micro:.4f}\n"
         f"combined ~= {adj + 0.1*micro:.5f}\n")
    # per-embryo
    for pre in ("44b6", "6bba"):
        sub = [r for r in rows if r.get("stem", "").startswith(pre)]
        if sub:
            a = sum(float(r["adjusted_edge_jaccard"]) for r in sub) / len(sub)
            t2 = sum(float(r.get("div_tp", 0) or 0) for r in sub)
            f2 = sum(float(r.get("div_fp", 0) or 0) for r in sub)
            n2 = sum(float(r.get("div_fn", 0) or 0) for r in sub)
            d2 = t2 / (t2 + f2 + n2) if (t2 + f2 + n2) else float("nan")
            s += f"  {pre}: n={len(sub)} adjEJ={a:.5f} div {t2:.0f}/{f2:.0f}/{n2:.0f} divJ={d2:.4f}\n"
    log(s); return s

def main():
    log("=== watch_det955 start ===")
    for _ in range(200):
        st = status()
        if st == "COMPLETE":
            log("COMPLETE -> submitting"); ok = submit()
            c = cv()
            VERD.write_text(f"det955val submitted={ok}\n\n{c or ''}\n")
            log("=== DONE ==="); return
        if st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
            log(f"{st} -> pulling log for diagnosis")
            OUT.mkdir(parents=True, exist_ok=True)
            cli(["kernels", "output", KID, "-p", str(OUT), "-q"], t=1800)
            lg = list(OUT.glob("*.log"))
            tail = ""
            if lg:
                tail = lg[0].read_text(encoding="utf-8", errors="ignore")[-1500:]
            VERD.write_text(f"det955val {st}\n\n{tail}\n")
            log(f"{st}: {tail[-400:]}"); return
        time.sleep(120)
    VERD.write_text("timeout\n")

if __name__ == "__main__":
    main()
