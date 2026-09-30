#!/usr/bin/env python3
"""Re-fetch the 46 empty/corrupt GT geffs listed in gt_broken.txt.
Each geff is 21 tiny files (~54KB total). This triples the GT divisions available for
local validation (6 -> ~17), which is the binding limit on all division research.
CPU/network only. No GPU, no submissions."""
import sys, types, re, unicodedata, time, pathlib

m = types.ModuleType('slugify')
def _sl(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', s).strip().lower())
m.slugify = _sl; sys.modules['slugify'] = m
from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
COMP = "biohub-cell-tracking-during-development"
LOG = ROOT / "refetch_gt.log"
API = KaggleApi(); API.authenticate()

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")

TMPL_SRC = ROOT / "data/train/44b6_12dfb391.geff"
TMPL = sorted(p.relative_to(TMPL_SRC).as_posix() for p in TMPL_SRC.rglob("*") if p.is_file())

def fetch(remote, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    d = 2.0
    for _ in range(6):
        try:
            API.competition_download_file(COMP, remote, path=str(dest.parent), force=False, quiet=True)
            got = dest.parent / pathlib.PurePosixPath(remote).name
            if got.exists() and got.stat().st_size > 0:
                if got != dest: got.replace(dest)
                return True
        except Exception as e:
            if "429" in str(e): time.sleep(d); d = min(d * 2, 60)
            else: time.sleep(1.2)
    return False

def main():
    names = [n.strip() for n in (ROOT / "gt_broken.txt").read_text().splitlines() if n.strip()]
    log(f"=== refetch {len(names)} GT geffs x {len(TMPL)} files ===")
    done = failed = 0
    for i, name in enumerate(names, 1):
        stem = name[:-5] if name.endswith(".geff") else name
        miss = 0
        for rel in TMPL:
            dest = ROOT / "data/train" / f"{stem}.geff" / rel
            if not fetch(f"train/{stem}.geff/{rel}", dest):
                miss += 1
            time.sleep(0.12)
        if miss == 0: done += 1
        else: failed += 1
        log(f"[{i}/{len(names)}] {stem}: {'OK' if miss==0 else f'MISSING {miss}'} (done={done} failed={failed})")
    log(f"=== DONE ok={done} failed={failed} ===")

if __name__ == "__main__":
    main()
