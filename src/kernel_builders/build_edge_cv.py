"""OFFLINE edge-term validation of the forum's two-pass linking + denser detection,
on the pooled CV that reproduces LB 0.825/0.837. Reports adj_edge AND
division_jaccard AND combined so a config is judged on the true objective.

Two-pass (link_tight_um): pass 1 commits confident short links, pass 2 fills the
rest -- forbids the far "steal" a single global Hungarian uses to lower total
cost. This targets the 15-18% of achievable edges the linker currently loses.

Detection is cached per peak_min_frac (denser catches dimmer nuclei); the tight
gate is linking-only and reuses each cache.
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

N_PER = 12   # 24 samples; edge term is stable here (anchor used 20 -> 0.7954)
by=defaultdict(list)
for z in sorted((DATA/"train").glob("*.zarr")):
    if z.with_suffix(".geff").exists(): by[z.stem.split("_")[0]].append(z)
samples=[p for e in sorted(by) for p in by[e][:N_PER]]
gts={zp: scoring.read_geff(zp.with_suffix(".geff")) for zp in samples}
print("samples/embryo", {e:sum(1 for p in samples if p.stem.startswith(e)) for e in by}, flush=True)

BASE = dict(device="cuda", mode="tune", min_sep_um=6.5, peak_min_frac=0.08,
            max_gap=1, link_radius_um=7.0, gap_radius_um=9.0, max_per_frame=3000,
            motion_compensate=True, detect_divisions=True)

def build_cache(**over):
    cfg=Config(**{**BASE, **over}); t0=time.time()
    c={zp: detect_sample(zp,cfg) for zp in samples}
    print(f"  (cache {over} built in {time.time()-t0:.0f}s)", flush=True)
    return c

def score(cache, **over):
    cfg=Config(**{**BASE, **over})
    erows=[]; drows=[]; rby=defaultdict(list)
    for zp in samples:
        dets,shifts,scale=cache[zp]
        nodes,edges=assemble(dets,shifts,cfg,scale)
        gt=gts[zp]; arr=np.asarray(nodes,float); pe=np.asarray(edges).reshape(-1,2)
        er=scoring.evaluate_edges(arr[:,0].astype(int),arr[:,1:4],pe,gt)
        row=scoring.per_sample(er,gt["n_total"]); erows.append(row); rby[zp.stem.split("_")[0]].append(row)
        drows.append(scoring.evaluate_divisions(arr[:,0].astype(int),arr[:,1:4],pe,gt))
    e=scoring.summarise(erows); dj=scoring.division_jaccard(drows)
    dj=dj if dj==dj else 0.0
    worst=min(scoring.summarise(v)["adj_edge_jaccard"] for v in rby.values())
    return dict(adj=e["adj_edge_jaccard"], rec=e["node_recall"], worst=worst,
                dj=dj, comb=e["adj_edge_jaccard"]+0.1*dj)

def show(tag,r,base=None):
    d="" if base is None else f"  dadj={r['adj']-base:+.4f}"
    print(f"  {tag:34} adj={r['adj']:.4f} rec={r['rec']:.3f} worst={r['worst']:.4f} "
          f"divJ={r['dj']:.3f} comb={r['comb']:.4f}{d}", flush=True)

print("\\n=== CACHE A: pmf 0.08 (LB-0.837 detection) ===", flush=True)
cA=build_cache(peak_min_frac=0.08)
base=score(cA); show("single-pass (anchor)", base); b=base["adj"]
for tg in (4.0, 5.0, 6.0):
    show(f"two-pass tight={tg}", score(cA, link_tight_um=tg), base=b)
show("two-pass t6 + motion0.5", score(cA, link_tight_um=6.0, motion_alpha=0.5), base=b)

print("\\n=== CACHE B: pmf 0.04 (denser -> dimmer nuclei) ===", flush=True)
cB=build_cache(peak_min_frac=0.04)
show("pmf04 single-pass", score(cB, peak_min_frac=0.04), base=b)
show("pmf04 two-pass t6", score(cB, peak_min_frac=0.04, link_tight_um=6.0), base=b)

print("\\n=== CACHE C: pmf 0.03 (denser still) ===", flush=True)
cC=build_cache(peak_min_frac=0.03)
show("pmf03 single-pass", score(cC, peak_min_frac=0.03), base=b)
show("pmf03 two-pass t6", score(cC, peak_min_frac=0.03, link_tight_um=6.0), base=b)

print(f"\\nANCHOR adj={base['adj']:.4f} (LB ~0.829 edge). Pick the largest adj gain that", flush=True)
print("also holds worst-embryo; two-pass is linking-only so it is a safe LB bet.", flush=True)
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
out=HERE/"edgecv"/"biohub-edge-cv.ipynb"; out.parent.mkdir(parents=True,exist_ok=True)
json.dump(nb,open(out,"w"),indent=1)
meta={"id":"eeshsaxena/biohub-edge-cv","title":"biohub edge cv",
      "code_file":"biohub-edge-cv.ipynb","language":"python","kernel_type":"notebook",
      "is_private":True,"enable_gpu":True,"enable_tpu":False,"enable_internet":False,
      "machine_shape":"NvidiaTeslaT4","keywords":[],
      "dataset_sources":["eeshsaxena/biohub-zarr-wheels"],"kernel_sources":[],
      "competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
json.dump(meta,open(HERE/"edgecv"/"kernel-metadata.json","w"),indent=2)
print("wrote",out)
