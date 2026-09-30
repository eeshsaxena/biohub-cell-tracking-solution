#!/usr/bin/env python3
"""Wait for the CPU packer kernel, download its single tar, ship to the V100 box, extract.
No GPU used anywhere. Kaggle CPU kernels do not consume GPU quota."""
import subprocess, re, time, pathlib, os

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "ship_subset.log"; VERD = ROOT / "ship_subset.VERDICT.txt"
KID = "eeshsaxena/biohub-packsubset"
OUTDIR = ROOT / "data" / "packout"
BOX = "training@192.168.10.30"
BOXDIR = "~/biohub/data"

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
def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

def main():
    log("=== ship_subset start ===")
    for _ in range(120):                       # ~6h
        st = status()
        if st == "COMPLETE":
            log("packer COMPLETE -> downloading output"); break
        if st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
            VERD.write_text(f"packer {st}\n"); log(f"packer {st}"); return
        time.sleep(120)
    else:
        VERD.write_text("packer timeout\n"); log("timeout"); return

    OUTDIR.mkdir(parents=True, exist_ok=True)
    log(cli(["kernels", "output", KID, "-p", str(OUTDIR), "-q"])[:200] or "output pulled")
    tars = list(OUTDIR.glob("*.tar"))
    if not tars:
        VERD.write_text(f"no tar in output: {[p.name for p in OUTDIR.iterdir()]}\n")
        log("no tar found"); return
    tar = tars[0]; gb = tar.stat().st_size / 1e9
    log(f"downloaded {tar.name} = {gb:.2f} GB")

    # ship to box
    rc, o = sh(f'ssh -o BatchMode=yes {BOX} "mkdir -p {BOXDIR}"')
    posix = str(tar).replace("\\", "/")
    log("scp -> box ...")
    rc, o = sh(f'scp -o BatchMode=yes "{posix}" {BOX}:{BOXDIR}/')
    if rc != 0:
        VERD.write_text(f"scp failed: {o[:300]}\n"); log(f"scp failed: {o[:200]}"); return
    log("scp done; extracting on box")
    rc, o = sh(f'ssh -o BatchMode=yes {BOX} "cd {BOXDIR} && tar xf {tar.name} && ls | head -5 && du -sh ."')
    log(f"extract rc={rc}: {o[:300]}")
    VERD.write_text(f"SHIPPED {tar.name} ({gb:.2f} GB) to box:{BOXDIR}\n{o[:400]}\n")
    log("=== DONE ===")

if __name__ == "__main__":
    main()
