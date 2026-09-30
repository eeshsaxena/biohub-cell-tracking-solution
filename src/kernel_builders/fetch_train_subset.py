#!/usr/bin/env python3
"""Download a SUBSET of biohub train movies (zarr chunks) locally, with 429 backoff.
We only need ~20-30 movies (~9-14GB) to train a detector, not the full 88GB.
Picks movies for which we already have GT .geff locally. Resumable: skips existing files.
Then these get rsync'd to the V100 box. NO GPU used."""
import sys, types, re, unicodedata, time, pathlib, random

m = types.ModuleType('slugify')
def _sl(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', s).strip().lower())
m.slugify = _sl; sys.modules['slugify'] = m
from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
OUT = ROOT / "data" / "train_subset"
LOG = ROOT / "fetch_subset.log"
COMP = "biohub-cell-tracking-during-development"
N_MOVIES = int(sys.argv[1]) if len(sys.argv) > 1 else 24
T_PER = 100  # timepoints per movie

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")

API = KaggleApi(); API.authenticate()

def movies():
    """Movie ids we have GT geff for locally."""
    ids = sorted({p.stem for p in (ROOT / "data" / "train").glob("*.geff")})
    random.Random(0).shuffle(ids)
    return ids[:N_MOVIES]

def fetch(remote, dest):
    """Download one chunk with exponential backoff on 429/errors."""
    if dest.exists() and dest.stat().st_size > 0:
        return "skip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    delay = 2.0
    for attempt in range(7):
        try:
            API.competition_download_file(COMP, remote, path=str(dest.parent), force=False, quiet=True)
            # kaggle writes basename into dest.parent
            got = dest.parent / pathlib.PurePosixPath(remote).name
            if got.exists() and got.stat().st_size > 0:
                if got != dest:
                    got.replace(dest)
                return "ok"
        except Exception as e:
            s = str(e)
            if "429" in s or "Too Many" in s.lower():
                time.sleep(delay); delay = min(delay * 2, 90); continue
            time.sleep(delay); delay = min(delay * 2, 60)
    return "fail"

def main():
    mv = movies()
    log(f"=== fetch_train_subset: {len(mv)} movies x {T_PER} timepoints -> {OUT} ===")
    ok = skip = fail = 0
    for i, mid in enumerate(mv, 1):
        for t in range(T_PER):
            remote = f"train/{mid}.zarr/0/c/{t}/0/0/0"
            dest = OUT / f"{mid}.zarr" / "0" / "c" / str(t) / "0" / "0" / "0"
            r = fetch(remote, dest)
            if r == "ok": ok += 1; time.sleep(0.35)   # gentle pacing to avoid 429
            elif r == "skip": skip += 1
            else: fail += 1
        # movie-level zarr metadata
        for meta in (f"train/{mid}.zarr/zarr.json", f"train/{mid}.zarr/0/zarr.json"):
            d = OUT / f"{mid}.zarr" / pathlib.PurePosixPath(meta).relative_to(f"train/{mid}.zarr")
            fetch(meta, d)
        log(f"[{i}/{len(mv)}] {mid}: ok={ok} skip={skip} fail={fail}")
    log(f"=== DONE ok={ok} skip={skip} fail={fail} out={OUT} ===")

if __name__ == "__main__":
    main()
