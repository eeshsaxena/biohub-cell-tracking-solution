#!/usr/bin/env python3
"""Stream the FULL biohub train set to the V100 box, in batches.

Why batched: the whole set (~88GB) exceeds free local disk (~85GB) AND a Kaggle kernel's
output cap (~20GB). So: pack BATCH movies on Kaggle (free CPU kernel, no GPU quota) ->
download tars -> scp to box -> extract -> delete local tars -> next batch.
Local disk never holds more than one batch (~13GB).

The box cannot authenticate to Kaggle (university network returns 401 with a valid token),
so this laptop must be the conduit.

Resumable: skips movies already present on the box. No GPU used anywhere.
"""
import sys, types, re, unicodedata, subprocess, time, pathlib, json, tarfile, shutil

m = types.ModuleType('slugify')
def _sl(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', s).strip().lower())
m.slugify = _sl; sys.modules['slugify'] = m
from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "full_pull.log"; VERD = ROOT / "full_pull.VERDICT.txt"
KID = "eeshsaxena/biohub-packfull"
KDIR = ROOT / "scratch_kernels" / "v_packfull"
OUT = ROOT / "data" / "fullpull"
BOX = "training@192.168.10.30"; BOXDIR = "~/biohub/data/train"
BATCH = 30

API = KaggleApi(); API.authenticate()

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")
def sh(c, t=None):
    p = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
    return p.returncode, (p.stdout or "") + (p.stderr or "")
def cli(a, t=None):
    p = subprocess.run(["kaggle"] + a, capture_output=True, text=True, timeout=t)
    return "\n".join(l for l in ((p.stdout or "") + (p.stderr or "")).splitlines()
                     if "warn" not in l.lower())
def kstatus():
    mm = re.search(r"KernelWorkerStatus\.(\w+)", cli(["kernels", "status", KID]))
    return mm.group(1) if mm else "UNKNOWN"

def on_box():
    rc, o = sh(f'ssh -o BatchMode=yes {BOX} "ls -d {BOXDIR}/*.zarr 2>/dev/null | xargs -n1 basename 2>/dev/null"')
    return {l.strip()[:-5] for l in o.splitlines() if l.strip().endswith(".zarr")}

def build_kernel(movies):
    KDIR.mkdir(parents=True, exist_ok=True)
    code = (
        "import os, tarfile, glob, time\n"
        "def find_root():\n"
        "    for b in ('/kaggle/input/competitions/biohub-cell-tracking-during-development',\n"
        "              '/kaggle/input/biohub-cell-tracking-during-development'):\n"
        "        if os.path.isdir(b): return b\n"
        "    for b in glob.glob('/kaggle/input/**/train', recursive=True): return os.path.dirname(b)\n"
        "    raise RuntimeError('no data root')\n"
        "R=find_root(); tr=os.path.join(R,'train')\n"
        f"PICK={json.dumps(movies)}\n"
        "t0=time.time()\n"
        "for i,mv in enumerate(PICK,1):\n"
        "    out='/kaggle/working/%s.tar'%mv\n"
        "    with tarfile.open(out,'w') as tf:\n"
        "        z=os.path.join(tr,mv+'.zarr')\n"
        "        if os.path.isdir(z): tf.add(z,arcname=mv+'.zarr')\n"
        "        g=os.path.join(tr,mv+'.geff')\n"
        "        if os.path.isdir(g): tf.add(g,arcname=mv+'.geff')\n"
        "    print('[%d/%d] %s %.0fMB %.1fmin'%(i,len(PICK),mv,os.path.getsize(out)/1e6,(time.time()-t0)/60),flush=True)\n"
        "print('TOTAL',sum(os.path.getsize(f) for f in glob.glob('/kaggle/working/*.tar'))/1e9,'GB',flush=True)\n"
    )
    nb = {"metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python", "version": "3.12"}},
          "nbformat": 4, "nbformat_minor": 5,
          "cells": [{"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
                     "source": code.splitlines(keepends=True)}]}
    (KDIR / "kernel.ipynb").write_text(json.dumps(nb), encoding="utf-8")
    (KDIR / "kernel-metadata.json").write_text(json.dumps({
        "id": KID, "title": "biohub packfull", "code_file": "kernel.ipynb", "language": "python",
        "kernel_type": "notebook", "is_private": True, "enable_gpu": False, "enable_tpu": False,
        "enable_internet": False, "keywords": [], "dataset_sources": [], "kernel_sources": [],
        "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": []},
        indent=2))

def all_movies():
    """Enumerate train movies from the competition file listing (paged)."""
    names, token = set(), None
    for _ in range(400):
        cmd = ["competitions", "files", "biohub-cell-tracking-during-development",
               "--page-size", "200", "--csv"]
        if token: cmd += ["--page-token", token]
        o = cli(cmd, t=300); token = None
        for line in o.splitlines():
            if line.startswith("Next Page Token"):
                token = line.split("=", 1)[1].strip(); continue
            mm = re.match(r"train/([^/,]+)\.zarr/", line.strip())
            if mm: names.add(mm.group(1))
        if not token: break
    return sorted(names)

def main():
    log("=== full_pull start ===")
    movies = all_movies()
    log(f"train movies discovered: {len(movies)}")
    if not movies:
        VERD.write_text("could not enumerate movies\n"); return
    have = on_box(); log(f"already on box: {len(have)}")
    todo = [m for m in movies if m not in have]
    log(f"to fetch: {len(todo)}")
    OUT.mkdir(parents=True, exist_ok=True)
    shipped = 0
    for bi in range(0, len(todo), BATCH):
        batch = todo[bi:bi + BATCH]
        log(f"--- batch {bi//BATCH+1}/{(len(todo)+BATCH-1)//BATCH}: {len(batch)} movies ---")
        build_kernel(batch)
        try: API.kernels_push(str(KDIR))
        except Exception as e:
            log(f"push failed: {e}"); time.sleep(60); continue
        time.sleep(20)
        for _ in range(180):
            st = kstatus()
            if st == "COMPLETE": break
            if st in ("ERROR", "CANCEL_ACKNOWLEDGED"): log(f"kernel {st}"); break
            time.sleep(60)
        if kstatus() != "COMPLETE":
            log("batch kernel not complete; skipping"); continue
        for p in OUT.glob("*.tar"):
            try: p.unlink()
            except Exception: pass
        cli(["kernels", "output", KID, "-p", str(OUT), "-q"], t=10800)
        tars = [p for p in sorted(OUT.glob("*.tar"))
                if p.stat().st_size > 1_000_000 and tarfile.is_tarfile(p)]
        log(f"downloaded {len(tars)} valid tars ({sum(p.stat().st_size for p in tars)/1e9:.1f} GB)")
        for p in tars:
            posix = str(p).replace("\\", "/")
            rc, o = sh(f'scp -o BatchMode=yes "{posix}" {BOX}:{BOXDIR}/', t=1800)
            if rc == 0:
                rc2, _ = sh(f'ssh -o BatchMode=yes {BOX} "cd {BOXDIR} && tar xf {p.name} && rm -f {p.name}"', t=900)
                if rc2 == 0: shipped += 1
            try: p.unlink()
            except Exception: pass
        rc, o = sh(f'ssh -o BatchMode=yes {BOX} "ls -d {BOXDIR}/*.zarr 2>/dev/null | wc -l; du -sh {BOXDIR}"')
        log(f"box now: {o.strip()[:120]}  (shipped this run: {shipped})")
    VERD.write_text(f"full_pull done, shipped {shipped} movies this run\n")
    log(f"=== DONE shipped={shipped} ===")

if __name__ == "__main__":
    main()
