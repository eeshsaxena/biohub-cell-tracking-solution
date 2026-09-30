"""DIVISION-AWARE offline CV. The existing offline harness scores only the EDGE
term (adj_edge_jaccard) and is BLIND to the division term -- yet divisions are
what took the LB from 0.829 (gap1) to 0.837 (gap1+div). This kernel adds
scoring.evaluate_divisions (validated numpy == official tracking_cellmot in
kaggle/test_divisions.py) and sweeps the fork-emission params, reporting

    combined = adj_edge_jaccard + 0.1 * division_jaccard

on the SAME pooled CV that reproduces LB 0.825 for the edge term. Detection is
independent of the division params, so it is cached ONCE and every division
config is a cheap re-link.

Goal: find the fork config that maximises div_jaccard without hurting the edge
term, then submit it. The division term ceiling is +0.1; we currently capture
~0.08 of it (div_jaccard).
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

N_PER = 30   # divisions are rare (~0.76/sample); use more samples for a stable term
by=defaultdict(list)
for z in sorted((DATA/"train").glob("*.zarr")):
    if z.with_suffix(".geff").exists(): by[z.stem.split("_")[0]].append(z)
samples=[p for e in sorted(by) for p in by[e][:N_PER]]
gts={zp: scoring.read_geff(zp.with_suffix(".geff")) for zp in samples}
n_gt_div=sum(sum(1 for i in range(len(g["ids"]))
            if sum(1 for s,d in g["edges"] if int(s)==int(g["ids"][i]))>=2) for g in gts.values())
print("samples/embryo", {e:sum(1 for p in samples if p.stem.startswith(e)) for e in by},
      "| total GT divisions in CV set:", n_gt_div, flush=True)

# LB-0.837 config (round2 gap1+div). Detection params are fixed; only the fork
# (division) params vary, so detection is cached once.
BASE = dict(device="cuda", mode="tune", min_sep_um=6.5, peak_min_frac=0.08,
            max_gap=1, link_radius_um=7.0, gap_radius_um=9.0, max_per_frame=3000,
            motion_compensate=True, detect_divisions=True)

t0=time.time()
CACHE={zp: detect_sample(zp, Config(**BASE)) for zp in samples}
print(f"detection cache built in {time.time()-t0:.0f}s", flush=True)

def score_all(**over):
    cfg = Config(**{**BASE, **over})
    erows=[]; drows=[]; rows_by=defaultdict(list)
    for zp in samples:
        dets, shifts, scale = CACHE[zp]
        nodes, edges = assemble(dets, shifts, cfg, scale)
        gt = gts[zp]
        arr=np.asarray(nodes,float)
        pe=np.asarray(edges).reshape(-1,2)
        er=scoring.evaluate_edges(arr[:,0].astype(int),arr[:,1:4],pe,gt)
        row=scoring.per_sample(er,gt["n_total"])
        erows.append(row); rows_by[zp.stem.split("_")[0]].append(row)
        drows.append(scoring.evaluate_divisions(arr[:,0].astype(int),arr[:,1:4],pe,gt))
    e=scoring.summarise(erows)
    dj=scoring.division_jaccard(drows)
    dtp=sum(r["division_tp"] for r in drows); dfp=sum(r["division_fp"] for r in drows)
    dfn=sum(r["division_fn"] for r in drows)
    adj=e["adj_edge_jaccard"]
    combined = adj + 0.1*(dj if dj==dj else 0.0)
    return dict(adj=adj, dj=(dj if dj==dj else 0.0), dtp=dtp, dfp=dfp, dfn=dfn, comb=combined)

def show(tag, r, base=None):
    d = "" if base is None else f"  dcomb={r['comb']-base:+.4f}"
    print(f"  {tag:38} adj={r['adj']:.4f} div_J={r['dj']:.3f} "
          f"(tp={r['dtp']} fp={r['dfp']} fn={r['dfn']}) comb={r['comb']:.4f}{d}", flush=True)

print("\\n=== A. ANCHORS ===", flush=True)
noforks = score_all(detect_divisions=False)
show("no forks (edge-only, gap1)", noforks)
base = score_all()  # current LB-0.837 config: cap 3, leg 13, sep 15
show("current (cap3 leg13 sep15)", base)
b = base["comb"]

print("\\n=== B. per-sample fork CAP (GT mean 0.76/sample) ===", flush=True)
for cap in (1, 2, 4, 6, 8, 12):
    show(f"max_div_per_sample={cap}", score_all(max_divisions_per_sample=cap), base=b)

print("\\n=== C. parent->daughter leg gate (median 5.75um) ===", flush=True)
for leg in (8.0, 10.0, 13.0, 16.0, 20.0):
    show(f"division_max_leg_um={leg}", score_all(division_max_leg_um=leg), base=b)

print("\\n=== D. daughter<->daughter separation gate (median 10.57um) ===", flush=True)
for sep in (12.0, 15.0, 18.0, 22.0):
    show(f"division_max_sep_um={sep}", score_all(division_max_sep_um=sep), base=b)

print("\\n=== E. BEST-COMBO candidates ===", flush=True)
best=(None,-1,None)
for tag, over in [
    ("cap6 leg16 sep18",  dict(max_divisions_per_sample=6, division_max_leg_um=16.0, division_max_sep_um=18.0)),
    ("cap8 leg16 sep18",  dict(max_divisions_per_sample=8, division_max_leg_um=16.0, division_max_sep_um=18.0)),
    ("cap8 leg13 sep15",  dict(max_divisions_per_sample=8, division_max_leg_um=13.0, division_max_sep_um=15.0)),
    ("cap6 leg20 sep22",  dict(max_divisions_per_sample=6, division_max_leg_um=20.0, division_max_sep_um=22.0)),
    ("cap12 leg16 sep18", dict(max_divisions_per_sample=12, division_max_leg_um=16.0, division_max_sep_um=18.0)),
]:
    r = score_all(**over); show(tag, r, base=b)
    if r["comb"] > best[1]: best=(tag, r["comb"], over)

print(f"\\nBASE combined {base['comb']:.4f} (edge-only {noforks['comb']:.4f})", flush=True)
print(f"BEST: {best[0]} comb={best[1]:.4f}  delta_vs_base={best[1]-base['comb']:+.4f}", flush=True)
print(f"config: {best[2]}", flush=True)
print(f"=> if edge term holds at LB 0.829 and CV div offset transfers, LB ~ "
      f"{0.829 + 0.1*score_all(**best[2])['dj']:.3f}", flush=True)
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
out=HERE/"divcv"/"biohub-div-cv.ipynb"; out.parent.mkdir(parents=True,exist_ok=True)
json.dump(nb,open(out,"w"),indent=1)
meta={"id":"eeshsaxena/biohub-div-cv","title":"biohub div cv",
      "code_file":"biohub-div-cv.ipynb","language":"python","kernel_type":"notebook",
      "is_private":True,"enable_gpu":True,"enable_tpu":False,"enable_internet":False,
      "machine_shape":"NvidiaTeslaT4","keywords":[],
      "dataset_sources":["eeshsaxena/biohub-zarr-wheels"],"kernel_sources":[],
      "competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
json.dump(meta,open(HERE/"divcv"/"kernel-metadata.json","w"),indent=2)
print("wrote",out)
