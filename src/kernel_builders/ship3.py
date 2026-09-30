#!/usr/bin/env python3
"""Download the per-movie tars to completion, THEN validate, THEN ship to the V100 box.
Fixes the earlier bug: previous version validated/deleted files mid-download and gave up.
Box cannot auth to Kaggle (university network blocks the API), so the laptop is the conduit.
No GPU used."""
import subprocess, time, pathlib, tarfile, shutil

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "ship3.log"; VERD = ROOT / "ship3.VERDICT.txt"
KID = "eeshsaxena/biohub-packsubset"
OUT = ROOT / "data" / "packout3"
BOX = "training@192.168.10.30"; BOXDIR = "~/biohub/data/train"

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")
def sh(c, t=None):
    p = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
    return p.returncode, (p.stdout or "") + (p.stderr or "")
def valid(p):
    try: return p.stat().st_size > 1_000_000 and tarfile.is_tarfile(p)
    except Exception: return False

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log("=== ship3: downloading packer output to completion ===")
    # single long-running download; do NOT interrupt or validate mid-flight
    rc, o = sh(f'kaggle kernels output {KID} -p "{OUT}" -q', t=7200)
    log(f"download rc={rc} {o.strip()[:200]}")

    tars = sorted(OUT.glob("*.tar"))
    good = [p for p in tars if valid(p)]
    bad = [p for p in tars if not valid(p)]
    gb = sum(p.stat().st_size for p in good) / 1e9
    log(f"{len(good)} valid / {len(tars)} tars = {gb:.2f} GB; {len(bad)} bad")

    # one retry pass for bad/missing ones
    if bad or len(good) < 20:
        for p in bad:
            try: p.unlink()
            except Exception: pass
        log("retry pass for missing/corrupt tars")
        rc, o = sh(f'kaggle kernels output {KID} -p "{OUT}" -q', t=7200)
        tars = sorted(OUT.glob("*.tar"))
        good = [p for p in tars if valid(p)]
        gb = sum(p.stat().st_size for p in good) / 1e9
        log(f"after retry: {len(good)} valid = {gb:.2f} GB")

    if not good:
        VERD.write_text("no valid tars\n"); log("FAILED: no valid tars"); return

    sh(f'ssh -o BatchMode=yes {BOX} "mkdir -p {BOXDIR}"')
    sent = 0
    for p in good:
        posix = str(p).replace("\\", "/")
        rc, o = sh(f'scp -o BatchMode=yes "{posix}" {BOX}:{BOXDIR}/', t=1800)
        if rc != 0:
            log(f"  scp FAIL {p.name}: {o[:120]}"); continue
        rc2, o2 = sh(f'ssh -o BatchMode=yes {BOX} "cd {BOXDIR} && tar xf {p.name} && rm -f {p.name}"', t=900)
        if rc2 == 0:
            sent += 1; log(f"  ok {p.name} ({sent}/{len(good)})")
        else:
            log(f"  extract FAIL {p.name}: {o2[:120]}")
    rc, o = sh(f'ssh -o BatchMode=yes {BOX} "cd {BOXDIR} && ls -d *.zarr 2>/dev/null | wc -l; ls -d *.geff 2>/dev/null | wc -l; du -sh ."')
    VERD.write_text(f"SHIPPED {sent}/{len(good)} movies ({gb:.2f} GB)\nbox train dir: {o[:300]}\n")
    log(f"=== DONE {sent} movies on box | {o[:200]} ===")

if __name__ == "__main__":
    main()
