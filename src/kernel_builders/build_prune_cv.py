"""Measure the node-prune quick win on pooled CV: isolated-node fraction, the
node_ratio shift, and the adj_edge gain. Stacks on the current best config
(two-pass tight4 + div cap6). Detection cached once; prune is post-linking so
every row reuses the cache.
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
import numpy as np, time

def find_data_root():
    slug="biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"),Path(f"/kaggle/input/{slug}")):
        if (c/"train").exists(): return c
    for p in Path("/kaggle/input").rglob("train"):
        if p.is_dir() and any(p.glob("*.zarr")): return p.parent
    raise RuntimeError("no data")
DATA=find_data_root()

N_PER=15
by=defaultdict(list)
for z in sorted((DATA/"train").glob("*.zarr")):
    if z.with_suffix(".geff").exists(): by[z.stem.split("_")[0]].append(z)
samples=[p for e in sorted(by) for p in by[e][:N_PER]]
gts={zp: scoring.read_geff(zp.with_suffix(".geff")) for zp in samples}
print("samples", {e:sum(1 for p in samples if p.stem.startswith(e)) for e in by}, flush=True)

BASE=dict(device="cuda", mode="tune", min_sep_um=6.5, peak_min_frac=0.08, max_gap=1,
          link_radius_um=7.0, gap_radius_um=9.0, max_per_frame=3000, motion_compensate=True,
          detect_divisions=True, link_tight_um=4.0, max_divisions_per_sample=6,
          division_max_leg_um=16.0, division_max_sep_um=18.0)

t0=time.time(); CACHE={zp: detect_sample(zp, Config(**BASE)) for zp in samples}
print(f"cache built {time.time()-t0:.0f}s", flush=True)

def score(**over):
    cfg=Config(**{**BASE, **over}); erows=[]; iso_tot=0; node_tot=0
    for zp in samples:
        dets,shifts,scale=CACHE[zp]
        nodes,edges=assemble(dets,shifts,cfg,scale)
        arr=np.asarray(nodes,float); pe=np.asarray(edges).reshape(-1,2)
        # isolated fraction (of the graph actually emitted)
        touched=set(int(a) for a,b in edges)|set(int(b) for a,b in edges)
        iso_tot += len(nodes)-len(touched); node_tot += len(nodes)
        er=scoring.evaluate_edges(arr[:,0].astype(int),arr[:,1:4],pe,gt=gts[zp])
        erows.append(scoring.per_sample(er,gts[zp]["n_total"]))
    e=scoring.summarise(erows)
    ratio=float(np.nanmean([r["total_node_ratio"] for r in erows]))
    return e["adj_edge_jaccard"], e["node_recall"], ratio, iso_tot/max(node_tot,1)

a0,r0,ra0,iso0=score(prune_isolated=False)
print(f"  prune OFF: adj={a0:.4f} rec={r0:.3f} node_ratio={ra0:+.3f} isolated_frac={iso0:.3f}", flush=True)
a1,r1,ra1,iso1=score(prune_isolated=True)
print(f"  prune ON : adj={a1:.4f} rec={r1:.3f} node_ratio={ra1:+.3f} isolated_frac={iso1:.3f}", flush=True)
print(f"\\nNODE-PRUNE delta adj = {a1-a0:+.4f}  (isolated fraction was {iso0:.1%})", flush=True)
print(f"=> if it transfers, LB ~ {0.840 + (a1-a0):.3f}", flush=True)
'''

cells=[INSTALL, "# scoring\n"+SCORING+SHIM, "# pipeline\n"+PIPELINE, DRIVER]
nb_cells=[]
for src in cells:
    compile(src,"<c>","exec")
    nb_cells.append({"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":src.splitlines(keepends=True)})
print("compile ok")
nb={"cells":nb_cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=HERE/"prunecv"/"biohub-prune-cv.ipynb"; out.parent.mkdir(parents=True,exist_ok=True)
json.dump(nb,open(out,"w"),indent=1)
meta={"id":"eeshsaxena/biohub-prune-cv","title":"biohub prune cv","code_file":"biohub-prune-cv.ipynb",
      "language":"python","kernel_type":"notebook","is_private":True,"enable_gpu":True,"enable_tpu":False,
      "enable_internet":False,"machine_shape":"NvidiaTeslaT4","keywords":[],
      "dataset_sources":["eeshsaxena/biohub-zarr-wheels"],"kernel_sources":[],
      "competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
json.dump(meta,open(HERE/"prunecv"/"kernel-metadata.json","w"),indent=2)
print("wrote",out)
