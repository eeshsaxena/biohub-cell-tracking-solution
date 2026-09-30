"""EDGE-LOSS ATTRIBUTION: measure exactly WHERE each GT edge is lost in fill1.

Stop theorising. For every GT consecutive edge (u,v) on train movies, run the REAL
fill1 pipeline and classify:
  TP            edge predicted correctly
  det_miss      u and/or v had NO matched prediction (detection loss)
  steal         both matched, but pred(u) linked to a DIFFERENT node (link-steal)
  terminate     both matched, but pred(u) had NO successor (track ended)
  other         both matched, pv had a different predecessor, etc.
Also reports how many nodes short_filter removed, and the distance from the
stolen target to the true target (to see if steals are near-misses).

This definitively identifies the lever for the remaining ~0.05-0.08 edge gap.
No submission cost.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "sub_recall_fill" / "biohub-recall-fill-sub.ipynb"
OUT = HERE / "edge_attrib"; OUT.mkdir(exist_ok=True)
nb = json.loads(SRC.read_text(encoding="utf-8"))
# cells 0-4 = Kunal pipeline, cell 5 = fill1 repair override. Drop driver/gate cells.
base = nb["cells"][:6]

INSTALL = r'''
import os, glob, subprocess, sys
def _wd(slug):
    for b in (f"/kaggle/input/{slug}", f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(b): return b
    h=[p for p in glob.glob(f"/kaggle/input/**/{slug}",recursive=True) if os.path.isdir(p)]
    return h[0] if h else None
r=subprocess.run([sys.executable,"-m","pip","install","-q","--no-index",
                  f"--find-links={_wd('biohub-zarr-wheels')}","zarr"],capture_output=True,text=True)
print("zarr rc",r.returncode)
'''

DIAG = r'''
# ============ EDGE-LOSS ATTRIBUTION on train movies (real fill1 pipeline) ============
import numpy as np, time, gc
from pathlib import Path
from collections import defaultdict, Counter
from scipy.optimize import linear_sum_assignment

TRAIN = Path(ROOT)/"train"
def read_geff_min(p):
    import zarr
    g=zarr.open_group(str(p),mode="r")
    t=np.asarray(g["nodes/props/t/values"][:]).astype(np.int64)
    z=np.asarray(g["nodes/props/z/values"][:]).astype(np.float64)
    y=np.asarray(g["nodes/props/y/values"][:]).astype(np.float64)
    x=np.asarray(g["nodes/props/x/values"][:]).astype(np.float64)
    ids=np.asarray(g["nodes/ids"][:]).astype(np.int64)
    try: e=np.asarray(g["edges/ids"][:]).astype(np.int64).reshape(-1,2)
    except KeyError: e=np.zeros((0,2),np.int64)
    return ids,t,np.stack([z,y,x],1),e

# capture the graph the pipeline builds (before _emit flattens it)
CAP={}
_emit_orig=_emit
def _emit_cap(ds,nodes,edges):
    CAP['nodes']=nodes; CAP['edges']=list(edges)
    return _emit_orig(ds,nodes,edges)
_emit=_emit_cap

# also count what short_filter removes
_sf_orig=_short_filter
def _sf_count(nodes,edges):
    n0,e0=len(nodes),len(edges)
    n2,e2=_sf_orig(nodes,edges)
    CAP['sf_removed_nodes']=n0-len(n2); CAP['sf_removed_edges']=e0-len(e2)
    return n2,e2
_short_filter=_sf_count

N_PER_EMB=3; FRAME_CAP=40
geffs=sorted(TRAIN.glob("*.geff"))
by_emb=defaultdict(list)
for gp in geffs:
    if gp.with_suffix(".zarr").exists(): by_emb[gp.name.split("_")[0]].append(gp)
sel=[]
for emb,lst in sorted(by_emb.items()):
    lst=sorted(lst,key=lambda p:-len(read_geff_min(p)[0]))[:N_PER_EMB]
    sel+=[(emb,p) for p in lst]
print("movies:",[(e,p.stem) for e,p in sel],flush=True)

TOT=Counter(); steal_d=[]; sf_rm=0
for emb,gp in sel:
    zp=gp.with_suffix(".zarr")
    ids,gt_t,gt_pos,gt_e=read_geff_min(gp)
    meta=read_array_meta(zp); T=meta["shape"][0]
    present=[t for t in range(T) if (Path(zp)/"0"/"c"/str(t)/"0"/"0"/"0").exists()]
    Tmax=min((max(present)+1) if present else 0, FRAME_CAP)
    if Tmax<3: continue
    t0=time.time()
    dets=[detect(load_volume(zp,t,meta)) for t in range(Tmax)]
    repair_track(dets, gp.stem)           # fills CAP
    nodes=CAP['nodes']; edges=CAP['edges']
    sf_rm+=CAP.get('sf_removed_nodes',0)
    # pred graph maps
    succ=defaultdict(list); pred_of=defaultdict(list)
    for a,b in edges: succ[a].append(b); pred_of[b].append(a)
    # per-frame Hungarian: GT node -> pred node
    pby=defaultdict(list)
    for nid,n in nodes.items(): pby[int(n["t"])].append(nid)
    match={}   # gt index -> pred nid
    gi_by_t=defaultdict(list)
    for i,tt in enumerate(gt_t):
        if int(tt)<Tmax: gi_by_t[int(tt)].append(i)
    for tt,gidx in gi_by_t.items():
        pids=pby.get(tt,[])
        if not pids: continue
        P=np.array([nodes[p]["xyz"] for p in pids],float)*SCALE
        G=gt_pos[gidx]*SCALE
        d=np.linalg.norm(G[:,None]-P[None],axis=2)
        cost=np.where(d<=7.0,d,1e6); ri,ci=linear_sum_assignment(cost)
        for a,b in zip(ri,ci):
            if cost[a,b]<5e5: match[gidx[a]]=pids[b]
    # attribute each GT consecutive edge
    idx={int(v):i for i,v in enumerate(ids)}
    for s,d in gt_e:
        u,v=idx.get(int(s)),idx.get(int(d))
        if u is None or v is None: continue
        if int(gt_t[v])-int(gt_t[u])!=1: continue
        if int(gt_t[v])>=Tmax: continue
        pu,pv=match.get(u),match.get(v)
        if pu is None or pv is None: TOT['det_miss']+=1; continue
        if pv in succ.get(pu,[]): TOT['TP']+=1; continue
        ss=succ.get(pu,[])
        if not ss: TOT['terminate']+=1
        else:
            TOT['steal']+=1
            w=ss[0]
            steal_d.append(float(np.linalg.norm((nodes[w]["xyz"]-nodes[pv]["xyz"])*SCALE)))
    print(f"  {emb} {gp.stem}: {dict(TOT)} ({time.time()-t0:.0f}s)",flush=True)
    gc.collect()

n=sum(TOT.values())
print("\n================ EDGE-LOSS ATTRIBUTION ================")
for k in ('TP','det_miss','steal','terminate'):
    print(f"  {k:12} {TOT[k]:6d}  {100*TOT[k]/max(1,n):5.1f}%")
print(f"  short_filter removed nodes: {sf_rm}")
if steal_d:
    sd=np.array(steal_d)
    print(f"  steal distance to true target (um): med={np.median(sd):.2f} p90={np.percentile(sd,90):.2f}")
print("\nREAD: 'steal' => learned edge/flow model is the lever. 'terminate' => the")
print("linker's gate/cost drops real links (cheap knob!). 'det_miss' => detector.")
'''

cells=[{"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":INSTALL}]+base+\
      [{"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":DIAG}]
nb2=dict(nb); nb2["cells"]=cells
(OUT/"biohub-edge-attrib.ipynb").write_text(json.dumps(nb2),encoding="utf-8")
meta={"id":"eeshsaxena/biohub-edge-attrib","title":"Biohub edge attrib",
      "code_file":"biohub-edge-attrib.ipynb","language":"python","kernel_type":"notebook",
      "is_private":True,"enable_gpu":True,"enable_tpu":False,"enable_internet":False,
      "machine_shape":"NvidiaTeslaT4","keywords":["gpu"],
      "dataset_sources":["xiaoleilian/biohub-unet3d-weights","xiaoleilian/biohub-unet3d-weights-v2models","eeshsaxena/biohub-zarr-wheels"],
      "kernel_sources":[],"competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
(OUT/"kernel-metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
print("built | cells",len(cells))
