"""Calibrate CV against the ONE trustworthy anchor: classical min_sep 6.5 = LB 0.825.

Every 'improvement' we picked on worst-embryo CV (min_sep 4.5, the U-Net) scored
WORSE on the LB. So the CV we've been using does not predict the LB. This run
scores the exact 0.825 config the way the LB aggregates (pooled, weight-averaged
adj_edge_jaccard over ALL samples across both embryos) on many train samples. If
POOLED adj lands near 0.825, pooled-CV is trustworthy and we can rank candidates
without spending LB slots. It also reports per-embryo + worst so we can see how
far the pessimistic worst-embryo number sits below the pooled/LB number.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def strip_local(src):
    out = []
    for ln in src.splitlines(keepends=True):
        s = ln.strip()
        out.append(("# " + ln) if (s == "import scoring" or s.startswith("from pipeline import")) else ln)
    return "".join(out)


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
print("zarr rc",r.returncode)
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

N_PER = 10   # samples per embryo
by=defaultdict(list)
for z in sorted((DATA/"train").glob("*.zarr")):
    if z.with_suffix(".geff").exists(): by[z.stem.split("_")[0]].append(z)
samples=[p for e in sorted(by) for p in by[e][:N_PER]]
print("calibrating on", {e:sum(1 for p in samples if p.stem.startswith(e)) for e in by}, flush=True)

# The exact LB-0.825 config.
cfg=Config(device="cuda", mode="tune", min_sep_um=6.5, peak_min_frac=0.08,
           max_gap=2, link_radius_um=7.0, gap_radius_um=9.0, max_per_frame=3000,
           motion_compensate=True)

rows_by=defaultdict(list); all_rows=[]
for zp in samples:
    t0=time.time()
    dets,shifts,scale=detect_sample(zp,cfg)
    nodes,edges=assemble(dets,shifts,cfg,scale)
    gt=scoring.read_geff(zp.with_suffix(".geff"))
    arr=np.asarray(nodes,float)
    er=scoring.evaluate_edges(arr[:,0].astype(int),arr[:,1:4],np.asarray(edges).reshape(-1,2),gt)
    row=scoring.per_sample(er,gt["n_total"])
    rows_by[zp.stem.split("_")[0]].append(row); all_rows.append(row)
    print(f"  {zp.stem}: adj={row['adj_edge_jaccard']:.3f} J={row['edge_jaccard']:.3f} "
          f"rec={row['node_recall']:.3f} ratio={row['total_node_ratio']:+.2f} {time.time()-t0:.0f}s", flush=True)

print("\\n=== classical min_sep 6.5 (known LB public = 0.825) ===")
for e in sorted(rows_by):
    s=scoring.summarise(rows_by[e]); print(f"  {e}: pooled_adj={s['adj_edge_jaccard']:.4f} n={s['n']}")
pooled=scoring.summarise(all_rows)
worst=min(scoring.summarise(rows_by[e])['adj_edge_jaccard'] for e in rows_by)
print(f"\\n  POOLED adj (LB-style, both embryos)  = {pooled['adj_edge_jaccard']:.4f}   <-- compare to LB 0.825")
print(f"  worst-embryo adj (what we tuned on)  = {worst:.4f}")
print("  If POOLED ~ 0.825, pooled-CV is trustworthy; rank candidates by it, not worst-embryo.")
'''

cells=[INSTALL, "# scoring\n"+SCORING+SHIM, "# pipeline\n"+PIPELINE, DRIVER]
nb_cells=[]
for src in cells:
    compile(src,"<c>","exec")
    nb_cells.append({"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
                     "source":src.splitlines(keepends=True)})
print("cells compile")
nb={"cells":nb_cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
    "language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
out=HERE/"calibcv"/"biohub-calib-cv.ipynb"; out.parent.mkdir(parents=True,exist_ok=True)
json.dump(nb,open(out,"w"),indent=1)
meta={"id":"eeshsaxena/biohub-calib-cv","title":"biohub calib cv","code_file":"biohub-calib-cv.ipynb",
      "language":"python","kernel_type":"notebook","is_private":True,"enable_gpu":True,"enable_tpu":False,
      "enable_internet":False,"machine_shape":"NvidiaTeslaT4","keywords":[],
      "dataset_sources":["eeshsaxena/biohub-zarr-wheels"],"kernel_sources":[],
      "competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
json.dump(meta,open(HERE/"calibcv"/"kernel-metadata.json","w"),indent=2)
print("wrote",out)
