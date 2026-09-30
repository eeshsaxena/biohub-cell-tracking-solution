"""Round 3: DETECTION-side sweep on pooled CV (the axes never properly tested).

Round 1/2 established: max_gap=1 is the only linking gain (+0.0066); motion
prediction and sub-voxel do not help; link_radius 7.0 and min_sep 6.5 are optimal.
Recall sits at 0.904 with node ratio -0.09, so there is still headroom to find
more real cells -- but it has to come from the DETECTOR, not the linker.

Never swept before: `sigmas_um`, the DoG scale set, which was hand-picked from a
14-19 um diameter estimate and directly determines WHICH cells are found. Also
sweeps peak_min_frac and gap_radius_um properly.

IMPORTANT harness fix vs round 1: detection-side parameters (sigmas, peak_min_frac,
min_sep) live inside detect_sample's NMS, so each one needs its OWN detection
cache. Round 1 section D overrode min_sep only at scoring time and silently
produced identical no-op rows. Here every detection variant rebuilds the cache.
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
'''

DRIVER = '''
from pathlib import Path
from collections import defaultdict
import numpy as np, time

def find_data_root():
    slug="biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"),Path(f"/kaggle/input/{slug}")):
        if (c/"train").exists(): return c
    for p in Path("/kaggle/input").rglob("train"):
        if p.is_dir() and any(p.glob("*.zarr")): return p.parent
    raise RuntimeError("no data")
DATA=find_data_root()

N_PER=8   # 16 samples (round 1 used 20; slightly fewer so more configs fit)
by=defaultdict(list)
for z in sorted((DATA/"train").glob("*.zarr")):
    if z.with_suffix(".geff").exists(): by[z.stem.split("_")[0]].append(z)
samples=[p for e in sorted(by) for p in by[e][:N_PER]]
gts={zp: scoring.read_geff(zp.with_suffix(".geff")) for zp in samples}
print("tuning on", {e:sum(1 for p in samples if p.stem.startswith(e)) for e in by}, flush=True)

# Winner from rounds 1-2.
BASE=dict(device="cuda",mode="tune",min_sep_um=6.5,peak_min_frac=0.08,max_gap=1,
          link_radius_um=7.0,gap_radius_um=9.0,max_per_frame=3000,
          motion_compensate=True,detect_divisions=True)

def evaluate(det_over=None, link_over=None):
    """Rebuild the detection cache for det_over, then score with link_over."""
    det_cfg=Config(**{**BASE, **(det_over or {})})
    cfg=Config(**{**BASE, **(det_over or {}), **(link_over or {})})
    rows_by=defaultdict(list); allr=[]
    for zp in samples:
        dets,shifts,scale=detect_sample(zp,det_cfg)
        nodes,edges=assemble(dets,shifts,cfg,scale)
        gt=gts[zp]; arr=np.asarray(nodes,float)
        er=scoring.evaluate_edges(arr[:,0].astype(int),arr[:,1:4],
                                  np.asarray(edges).reshape(-1,2),gt)
        row=scoring.per_sample(er,gt["n_total"])
        rows_by[zp.stem.split("_")[0]].append(row); allr.append(row)
    pooled=scoring.summarise(allr)
    ratio=float(np.nanmean([r["total_node_ratio"] for r in allr]))
    return pooled["adj_edge_jaccard"], pooled["node_recall"], ratio

def show(tag,res,base=None):
    p,r,ra=res
    d="" if base is None else f"  delta={p-base:+.4f}"
    print(f"  {tag:46} pooled={p:.4f} rec={r:.3f} ratio={ra:+.3f}{d}", flush=True)

t0=time.time()
b=evaluate(); show("BASE (min_sep6.5 pmf0.08 gap1 div)", b); base=b[0]
print(f"  (one full pass = {time.time()-t0:.0f}s)", flush=True)

print("\\n=== DoG SCALE SET (sigmas_um) -- never swept before ===", flush=True)
SIGMA_SETS = [
    (2.0, 3.0, 4.0, 5.0),
    (2.5, 3.5, 4.5, 6.0),          # current
    (3.0, 4.0, 5.0, 6.5),
    (2.0, 3.0, 4.0, 5.0, 6.5),     # 5 scales, wider
    (2.5, 4.0, 6.0),               # coarser, 3 scales
    (1.5, 2.5, 3.5, 4.5),          # finer -> smaller nuclei
]
for s in SIGMA_SETS:
    show(f"sigmas={s}", evaluate(det_over=dict(sigmas_um=s)), base)

print("\\n=== peak_min_frac (detection sensitivity) ===", flush=True)
for pmf in (0.05, 0.06, 0.10, 0.12):
    show(f"peak_min_frac={pmf}", evaluate(det_over=dict(peak_min_frac=pmf)), base)

print("\\n=== min_sep (properly rebuilt cache this time) ===", flush=True)
for ms in (5.5, 6.0, 7.0):
    show(f"min_sep={ms}", evaluate(det_over=dict(min_sep_um=ms)), base)

print("\\n=== gap_radius (only 9.0 tested so far) ===", flush=True)
for gr in (7.0, 11.0, 13.0):
    show(f"gap_radius={gr}", evaluate(link_over=dict(gap_radius_um=gr)), base)

print(f"\\nAnchor: pooled 0.7954 == LB 0.825 (20-sample set; this run uses 16 so", flush=True)
print("compare DELTAS within this run, not the absolute value across runs).", flush=True)
'''

cells=[INSTALL,"# scoring\n"+SCORING+SHIM,"# pipeline\n"+PIPELINE,DRIVER]
nb_cells=[]
for src in cells:
    compile(src,"<c>","exec")
    nb_cells.append({"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
                     "source":src.splitlines(keepends=True)})
print("all cells compile")
nb={"cells":nb_cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=HERE/"tunedetect"/"biohub-tune-detect.ipynb"; out.parent.mkdir(parents=True,exist_ok=True)
json.dump(nb,open(out,"w"),indent=1)
meta={"id":"eeshsaxena/biohub-tune-detect","title":"biohub tune detect",
      "code_file":"biohub-tune-detect.ipynb","language":"python","kernel_type":"notebook",
      "is_private":True,"enable_gpu":True,"enable_tpu":False,"enable_internet":False,
      "machine_shape":"NvidiaTeslaT4","keywords":[],
      "dataset_sources":["eeshsaxena/biohub-zarr-wheels"],"kernel_sources":[],
      "competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
json.dump(meta,open(HERE/"tunedetect"/"kernel-metadata.json","w"),indent=2)
print("wrote",out)
