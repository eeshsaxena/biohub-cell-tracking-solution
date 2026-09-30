#!/usr/bin/env python3
"""Wait for the per-movie packer, download tars with retries, VALIDATE each, ship to V100 box.
CPU/network only - no GPU quota anywhere."""
import subprocess, re, time, pathlib, tarfile

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "ship2.log"; VERD = ROOT / "ship2.VERDICT.txt"
KID = "eeshsaxena/biohub-packsubset"
OUT = ROOT / "data" / "packout2"
BOX = "training@192.168.10.30"; BOXDIR = "~/biohub/data"

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")
def cli(a):
    p = subprocess.run(["kaggle"] + a, capture_output=True, text=True)
    return "\n".join(l for l in ((p.stdout or "") + (p.stderr or "")).splitlines()
                     if "warn" not in l.lower())
def status():
    m = re.search(r"KernelWorkerStatus\.(\w+)", cli(["kernels", "status", KID]))
    return m.group(1) if m else "UNKNOWN"
def sh(c):
    p = subprocess.run(c, shell=True, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")
def valid(p):
    try:
        return p.stat().st_size > 1_000_000 and tarfile.is_tarfile(p)
    except Exception:
        return False

def main():
    log("=== ship2 start ===")
    for _ in range(150):
        st = status()
        if st == "COMPLETE": log("packer COMPLETE"); break
        if st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
            VERD.write_text(f"packer {st}\n"); log(f"packer {st}"); return
        time.sleep(120)
    else:
        VERD.write_text("packer timeout\n"); return

    OUT.mkdir(parents=True, exist_ok=True)
    # retry loop: kaggle re-pulls output; keep going until tar count stops growing
    good = 0
    for attempt in range(1, 9):
        cli(["kernels", "output", KID, "-p", str(OUT), "-q"])
        tars = sorted(OUT.glob("*.tar"))
        good_now = [p for p in tars if valid(p)]
        log(f"attempt {attempt}: {len(good_now)}/{len(tars)} valid tars, "
            f"{sum(p.stat().st_size for p in good_now)/1e9:.2f} GB")
        for p in tars:                       # drop corrupt/truncated
            if not valid(p):
                try: p.unlink()
                except Exception: pass
        if len(good_now) >= 20 or len(good_now) == good:
            good = len(good_now); break
        good = len(good_now)

    tars = [p for p in sorted(OUT.glob("*.tar")) if valid(p)]
    if not tars:
        VERD.write_text("no valid tars downloaded\n"); log("no valid tars"); return
    gb = sum(p.stat().st_size for p in tars) / 1e9
    log(f"shipping {len(tars)} tars = {gb:.2f} GB")

    sh(f'ssh -o BatchMode=yes {BOX} "mkdir -p {BOXDIR}"')
    sent = 0
    for p in tars:
        posix = str(p).replace("\\", "/")
        rc, o = sh(f'scp -o BatchMode=yes "{posix}" {BOX}:{BOXDIR}/')
        if rc == 0:
            rc2, o2 = sh(f'ssh -o BatchMode=yes {BOX} "cd {BOXDIR} && tar xf {p.name} && rm -f {p.name}"')
            if rc2 == 0: sent += 1; log(f"  ok {p.name}")
            else: log(f"  extract failed {p.name}: {o2[:120]}")
        else:
            log(f"  scp failed {p.name}: {o[:120]}")
    rc, o = sh(f'ssh -o BatchMode=yes {BOX} "cd {BOXDIR} && ls -d *.zarr 2>/dev/null | wc -l && du -sh ."')
    VERD.write_text(f"SHIPPED {sent}/{len(tars)} movie tars ({gb:.2f} GB)\nbox: {o[:300]}\n")
    log(f"=== DONE {sent}/{len(tars)} shipped | box: {o[:200]} ===")

if __name__ == "__main__":
    main()
