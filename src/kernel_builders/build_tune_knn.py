"""Round 2 of offline tuning: the LOCAL VELOCITY FIELD (motion_knn).

Round 1 (biohub-tune-offline) sweeps subvoxel / motion_alpha / max_gap /
link_radius / divisions. motion_knn landed after that kernel was pushed, so this
run covers it, on the SAME 20 samples and the same pooled-CV statistic
(baseline anchor: pooled 0.7954 == LB 0.825).

Why it should beat per-cell velocity: a cell's own previous step is one noisy
measurement and is simply absent for cells that just appeared, whereas developing
tissue moves in coherent local flows -- so the median velocity of a cell's k
nearest neighbours is both lower-variance and defined everywhere.

Detection (the expensive part) is cached ONCE with subvoxel on; every linking
variant then re-runs only assemble+score.
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

N_PER=10
by=defaultdict(list)
for z in sorted((DATA/"train").glob("*.zarr")):
    if z.with_suffix(".geff").exists(): by[z.stem.split("_")[0]].append(z)
samples=[p for e in sorted(by) for p in by[e][:N_PER]]
gts={zp: scoring.read_geff(zp.with_suffix(".geff")) for zp in samples}
print("tuning on", {e:sum(1 for p in samples if p.stem.startswith(e)) for e in by}, flush=True)

BASE=dict(device="cuda",mode="tune",min_sep_um=6.5,peak_min_frac=0.08,max_gap=2,
          link_radius_um=7.0,gap_radius_um=9.0,max_per_frame=3000,motion_compensate=True)

def score_all(cache, **over):
    cfg=Config(**{**BASE,**over})
    rows_by=defaultdict(list); allr=[]
    for zp in samples:
        dets,shifts,scale=cache[zp]
        nodes,edges=assemble(dets,shifts,cfg,scale)
        gt=gts[zp]; arr=np.asarray(nodes,float)
        er=scoring.evaluate_edges(arr[:,0].astype(int),arr[:,1:4],np.asarray(edges).reshape(-1,2),gt)
        row=scoring.per_sample(er,gt["n_total"])
        rows_by[zp.stem.split("_")[0]].append(row); allr.append(row)
    pooled=scoring.summarise(allr)
    worst=min(scoring.summarise(v)["adj_edge_jaccard"] for v in rows_by.values())
    ratio=float(np.nanmean([r["total_node_ratio"] for r in allr]))
    return pooled["adj_edge_jaccard"],worst,pooled["node_recall"],ratio

t0=time.time()
cache={zp: detect_sample(zp, Config(**{**BASE,"subvoxel":True})) for zp in samples}
print(f"detection cache (subvoxel) built in {time.time()-t0:.0f}s", flush=True)

def show(tag,res,base=None):
    p,w,r,ra=res
    d="" if base is None else f"  delta={p-base:+.4f}"
    print(f"  {tag:40} pooled={p:.4f} worst={w:.4f} rec={r:.3f} ratio={ra:+.3f}{d}", flush=True)

print("\\n=== subvoxel baseline ===", flush=True)
b=score_all(cache, subvoxel=True); show("subvoxel only", b); base=b[0]

print("\\n=== motion_alpha x motion_knn ===", flush=True)
best=("",-1,{})
for a in (0.5, 0.8, 1.0):
    for k in (0, 3, 5, 8, 12):
        over=dict(subvoxel=True, motion_alpha=a, motion_knn=k)
        res=score_all(cache, **over); show(f"alpha={a} knn={k}", res, base)
        if res[0]>best[1]: best=(f"alpha={a} knn={k}",res[0],over)
print(f"\\nbest motion setting: {best[0]} pooled={best[1]:.4f}", flush=True)

print("\\n=== best motion + gap/radius/divisions ===", flush=True)
for g in (1,2,3):
    show(f"{best[0]} max_gap={g}", score_all(cache, **{**best[2],"max_gap":g}), base)
for lr in (6.0,7.0,8.0):
    show(f"{best[0]} link_radius={lr}", score_all(cache, **{**best[2],"link_radius_um":lr}), base)
show(f"{best[0]} +divisions", score_all(cache, **{**best[2],"detect_divisions":True}), base)

print(f"\\nAnchor: baseline pooled 0.7954 == LB 0.825.", flush=True)
print(f"=> a config at pooled P implies LB ~ {0.825:.3f} + (P - 0.7954)", flush=True)
'''

cells=[INSTALL,"# scoring\\n"+SCORING+SHIM,"# pipeline\\n"+PIPELINE,DRIVER]
cells=[INSTALL,"# scoring\n"+SCORING+SHIM,"# pipeline\n"+PIPELINE,DRIVER]
nb_cells=[]
for src in cells:
    compile(src,"<c>","exec")
    nb_cells.append({"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
                     "source":src.splitlines(keepends=True)})
print("all cells compile")
nb={"cells":nb_cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=HERE/"tuneknn"/"biohub-tune-knn.ipynb"; out.parent.mkdir(parents=True,exist_ok=True)
json.dump(nb,open(out,"w"),indent=1)
meta={"id":"eeshsaxena/biohub-tune-knn","title":"biohub tune knn","code_file":"biohub-tune-knn.ipynb",
      "language":"python","kernel_type":"notebook","is_private":True,"enable_gpu":True,
      "enable_tpu":False,"enable_internet":False,"machine_shape":"NvidiaTeslaT4","keywords":[],
      "dataset_sources":["eeshsaxena/biohub-zarr-wheels"],"kernel_sources":[],
      "competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
json.dump(meta,open(HERE/"tuneknn"/"kernel-metadata.json","w"),indent=2)
print("wrote",out)
