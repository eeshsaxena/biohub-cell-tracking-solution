"""OFFLINE tuning on the now-VALIDATED pooled CV (no submissions burned).

biohub-calib-cv proved pooled adj_edge_jaccard tracks the leaderboard:
    pooled CV 0.7954  vs  LB 0.825   (worst-embryo 0.7218 was the misleading stat
    that made us pick min_sep 4.5 and the U-Net, both of which LOST on the LB).

Per-sample calib data showed recall is already 0.88-0.96 while J/recall is only
0.82-0.95 -> LINKING, not detection, is where the score leaks. Node ratio is also
consistently NEGATIVE (-0.03..-0.25) -> we under-detect, so there is headroom to
add cells without paying the ratio penalty.

This sweeps the two new levers plus the classical knobs, on the SAME 20 samples as
the anchor so every number is directly comparable to 0.7954:
  * subvoxel     -- parabolic peak refinement (z voxel 1.625 um vs 1.82 um median motion)
  * motion_alpha -- per-cell constant-velocity prediction in the linker
  * max_gap / link_radius / peak_min_frac / divisions
Detection is cached per (subvoxel, peak_min_frac) so the linking sweep is cheap.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

SCORING = (ROOT / "kaggle" / "scoring.py").read_text(encoding="utf-8")
PIPELINE = (ROOT / "kaggle" / "pipeline.py").read_text(encoding="utf-8").split('if __name__ == "__main__":')[0]
SHIM = '\nimport types as _t\nscoring = _t.SimpleNamespace(**{k: v for k, v in list(globals().items()) if not k.startswith("_")})\n'

INSTALL = '''
import os, glob, subprocess, sys
def find_wheeldir(slug):
    for base in (f"/kaggle/input/{slug}", f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(base): return base
    h=[p for p in glob.glob(f"/kaggle/input/**/{slug}",recursive=True) if os.path.isdir(p)]
    return h[0] if h else None
r=subprocess.run([sys.executable,"-m","pip","install","-q","--no-index",
    f"--find-links={find_wheeldir('biohub-zarr-wheels')}","zarr"],capture_output=True,text=True)
print("zarr rc",r.returncode, flush=True)
import torch; print("torch",torch.__version__,"cuda",torch.cuda.is_available(), flush=True)
'''

DRIVER = '''
from pathlib import Path
from collections import defaultdict
import numpy as np, time, dataclasses

def find_data_root():
    slug="biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"),Path(f"/kaggle/input/{slug}")):
        if (c/"train").exists(): return c
    for p in Path("/kaggle/input").rglob("train"):
        if p.is_dir() and any(p.glob("*.zarr")): return p.parent
    raise RuntimeError("no data")
DATA=find_data_root()

N_PER = 10   # SAME 20 samples as biohub-calib-cv -> comparable to the 0.7954 anchor
by=defaultdict(list)
for z in sorted((DATA/"train").glob("*.zarr")):
    if z.with_suffix(".geff").exists(): by[z.stem.split("_")[0]].append(z)
samples=[p for e in sorted(by) for p in by[e][:N_PER]]
gts={zp: scoring.read_geff(zp.with_suffix(".geff")) for zp in samples}
print("tuning on", {e:sum(1 for p in samples if p.stem.startswith(e)) for e in by}, flush=True)

BASE = dict(device="cuda", mode="tune", min_sep_um=6.5, peak_min_frac=0.08,
            max_gap=2, link_radius_um=7.0, gap_radius_um=9.0, max_per_frame=3000,
            motion_compensate=True)

def score_all(cache, **over):
    cfg = Config(**{**BASE, **over})
    rows_by=defaultdict(list); allr=[]
    for zp in samples:
        dets, shifts, scale = cache[zp]
        nodes, edges = assemble(dets, shifts, cfg, scale)
        gt = gts[zp]
        arr=np.asarray(nodes,float)
        er=scoring.evaluate_edges(arr[:,0].astype(int),arr[:,1:4],
                                  np.asarray(edges).reshape(-1,2),gt)
        row=scoring.per_sample(er,gt["n_total"])
        rows_by[zp.stem.split("_")[0]].append(row); allr.append(row)
    pooled=scoring.summarise(allr)
    worst=min(scoring.summarise(v)["adj_edge_jaccard"] for v in rows_by.values())
    ratio=float(np.nanmean([r["total_node_ratio"] for r in allr]))
    return pooled["adj_edge_jaccard"], worst, pooled["node_recall"], ratio

def build_cache(**over):
    cfg = Config(**{**BASE, **over})
    cache={}
    t0=time.time()
    for zp in samples:
        cache[zp]=detect_sample(zp,cfg)
    print(f"  (detection cache built in {time.time()-t0:.0f}s)", flush=True)
    return cache

def show(tag, pooled, worst, rec, ratio, base=None):
    delta = "" if base is None else f"  delta={pooled-base:+.4f}"
    print(f"  {tag:44} pooled={pooled:.4f} worst={worst:.4f} rec={rec:.3f} ratio={ratio:+.3f}{delta}", flush=True)

print("\\n=== A. BASELINE (reproduce the 0.7954 anchor / LB 0.825) ===", flush=True)
cache_plain = build_cache(subvoxel=False)
base_pooled, w, r, ra = score_all(cache_plain)
show("baseline min_sep6.5 (anchor 0.7954)", base_pooled, w, r, ra)

print("\\n=== B. LINKING levers on plain detections ===", flush=True)
for a in (0.3, 0.5, 0.8, 1.0):
    show(f"motion_alpha={a}", *score_all(cache_plain, motion_alpha=a), base=base_pooled)
for g in (0, 1, 3):
    show(f"max_gap={g}", *score_all(cache_plain, max_gap=g), base=base_pooled)
for lr in (5.0, 6.0, 8.0, 9.0):
    show(f"link_radius={lr}", *score_all(cache_plain, link_radius_um=lr), base=base_pooled)
show("divisions=True", *score_all(cache_plain, detect_divisions=True), base=base_pooled)

print("\\n=== C. SUB-VOXEL detections ===", flush=True)
cache_sub = build_cache(subvoxel=True)
sub_pooled, w, r, ra = score_all(cache_sub, subvoxel=True)
show("subvoxel", sub_pooled, w, r, ra, base=base_pooled)
for a in (0.3, 0.5, 0.8):
    show(f"subvoxel + motion_alpha={a}", *score_all(cache_sub, subvoxel=True, motion_alpha=a), base=base_pooled)
for g in (1, 3):
    show(f"subvoxel + max_gap={g}", *score_all(cache_sub, subvoxel=True, max_gap=g), base=base_pooled)

print("\\n=== D. DENSER detection (ratio is negative -> room to add cells) ===", flush=True)
cache_dense = build_cache(subvoxel=True, peak_min_frac=0.04)
d_pooled, w, r, ra = score_all(cache_dense, subvoxel=True, peak_min_frac=0.04)
show("subvoxel + peak_min_frac=0.04", d_pooled, w, r, ra, base=base_pooled)
for ms in (5.5, 6.0):
    show(f"subvoxel pmf0.04 min_sep={ms}",
         *score_all(cache_dense, subvoxel=True, peak_min_frac=0.04, min_sep_um=ms), base=base_pooled)

print("\\n=== E. BEST COMBO candidates ===", flush=True)
best=(None,-1)
for cache, tag, over in [
    (cache_sub,   "sub+a0.5+gap1",            dict(subvoxel=True, motion_alpha=0.5, max_gap=1)),
    (cache_sub,   "sub+a0.5+gap2+div",        dict(subvoxel=True, motion_alpha=0.5, detect_divisions=True)),
    (cache_sub,   "sub+a0.8+gap2+div",        dict(subvoxel=True, motion_alpha=0.8, detect_divisions=True)),
    (cache_dense, "sub+dense+a0.5+div",       dict(subvoxel=True, peak_min_frac=0.04, motion_alpha=0.5, detect_divisions=True)),
    (cache_dense, "sub+dense+a0.5+ms6.0+div", dict(subvoxel=True, peak_min_frac=0.04, min_sep_um=6.0, motion_alpha=0.5, detect_divisions=True)),
]:
    p,w,r,ra = score_all(cache, **over)
    show(tag, p, w, r, ra, base=base_pooled)
    if p > best[1]: best=(tag,p,over)
print(f"\\nBEST: {best[0]} pooled={best[1]:.4f} (baseline {base_pooled:.4f}, LB anchor 0.825)", flush=True)
print(f"config: {best[2]}", flush=True)
print(f"=> expected LB ~ {0.825 + (best[1]-base_pooled):.3f} if the CV offset holds", flush=True)
'''

cells=[INSTALL, "# scoring\n"+SCORING+SHIM, "# pipeline\n"+PIPELINE, DRIVER]
nb_cells=[]
for src in cells:
    compile(src,"<c>","exec")
    nb_cells.append({"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
                     "source":src.splitlines(keepends=True)})
print("all cells compile")
nb={"cells":nb_cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=HERE/"tuneoffline"/"biohub-tune-offline.ipynb"; out.parent.mkdir(parents=True,exist_ok=True)
json.dump(nb,open(out,"w"),indent=1)
meta={"id":"eeshsaxena/biohub-tune-offline","title":"biohub tune offline",
      "code_file":"biohub-tune-offline.ipynb","language":"python","kernel_type":"notebook",
      "is_private":True,"enable_gpu":True,"enable_tpu":False,"enable_internet":False,
      "machine_shape":"NvidiaTeslaT4","keywords":[],
      "dataset_sources":["eeshsaxena/biohub-zarr-wheels"],"kernel_sources":[],
      "competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
json.dump(meta,open(HERE/"tuneoffline"/"kernel-metadata.json","w"),indent=2)
print("wrote",out)
