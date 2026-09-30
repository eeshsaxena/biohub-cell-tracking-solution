#!/usr/bin/env python3
"""Collect 20-movie validator CV from the honest kernels + threshold sweep, build the
threshold x safe_div table. NO submissions. Writes threshold_cv_VERDICT.txt."""
import sys, types, re, unicodedata, subprocess, time, pathlib, csv, io
m = types.ModuleType('slugify'); m.slugify = lambda s: s; sys.modules['slugify'] = m
ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "auto_cv.log"; VERD = ROOT / "threshold_cv_VERDICT.txt"
def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"; print(l, flush=True)
    open(LOG, "a", encoding="utf-8").write(l + "\n")
# name -> (det, safe_div)
KERNELS = {"honest-nodiv": ("0.965", "off"), "honest-stack": ("0.965", "on"),
           "dsw0955": ("0.955", "off"), "dsw096": ("0.96", "off"),
           "dsw097": ("0.97", "off"), "dsw098": ("0.98", "off")}
def kid(n): return "eeshsaxena/biohub-v-" + n
def cli(a):
    p = subprocess.run(["kaggle"] + a, capture_output=True, text=True)
    return "\n".join(l for l in ((p.stdout or "") + (p.stderr or "")).splitlines()
                     if "Warning" not in l and "warnings.warn" not in l)
def status(n):
    o = cli(["kernels", "status", kid(n)]); mm = re.search(r"KernelWorkerStatus\.(\w+)", o)
    return mm.group(1) if mm else "UNKNOWN"
def pull_cv(n):
    d = ROOT / "scratch_kernels" / ("out_" + n); d.mkdir(exist_ok=True)
    cli(["kernels", "output", kid(n), "-p", str(d), "-q"])
    f = d / "validator_results.csv"
    try:
        rows = list(csv.DictReader(io.open(f, encoding="utf-8")))
        adj = sum(float(r["adjusted_edge_jaccard"]) for r in rows) / len(rows)
        dj = [float(r["division_jaccard"]) for r in rows if r.get("division_jaccard") not in (None, "")]
        djm = sum(dj) / len(dj) if dj else float("nan")
        return round(adj, 4), round(djm, 4), len(rows)
    except Exception as e:
        return None, None, str(e)[:40]
def main():
    cv = {}
    log("=== auto_cv start ===")
    for _ in range(120):
        for n in KERNELS:
            if n in cv: continue
            st = status(n)
            if st == "COMPLETE":
                adj, dj, k = pull_cv(n)
                cv[n] = (adj, dj, k); log(f"  {n} ({KERNELS[n][0]}/{KERNELS[n][1]}): adjEJ={adj} divJ={dj} ({k})")
            elif st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
                cv[n] = (None, None, st); log(f"  {n}: {st}")
        if all(n in cv for n in KERNELS):
            break
        time.sleep(90)
    # build table
    lines = ["THRESHOLD x SAFE_DIV CV (20-movie validator, honest prune on)\n",
             "kernel           det     safe_div  adjEJ    divJ", "-" * 52]
    for n in sorted(KERNELS, key=lambda x: (KERNELS[x][1], float(KERNELS[x][0]))):
        det, sd = KERNELS[n]; a = cv.get(n, (None, None, "?"))
        lines.append(f"{n:16} {det:6}  {sd:8}  {str(a[0]):7}  {a[1]}")
    # best safe_div=off threshold
    offs = [(float(KERNELS[n][0]), cv[n][0], n) for n in KERNELS
            if KERNELS[n][1] == "off" and cv.get(n, (None,))[0] is not None]
    if offs:
        best = max(offs, key=lambda x: x[1])
        lines.append("")
        lines.append("BEST safe_div=off threshold: det=%s -> adjEJ=%.4f (%s)" % (best[0], best[1], best[2]))
        no = cv.get("honest-nodiv", (None,))[0]; st = cv.get("honest-stack", (None,))[0]
        if no is not None and st is not None:
            lines.append("safe_div off vs on @0.965: %.4f vs %.4f (off %s)" %
                         (no, st, "WINS" if no >= st else "loses on CV"))
    VERD.write_text("\n".join(lines) + "\n")
    log("=== DONE ===\n" + "\n".join(lines))
if __name__ == "__main__":
    main()
