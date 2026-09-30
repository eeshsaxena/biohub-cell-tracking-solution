"""Kaggle CV for the LEARNED DIVISION DETECTOR (Direction A, ROADMAP_TO_095.md).

Runs the fill1 pipeline on TRAIN movies (both embryos) to get REAL-detection graphs
(noise orphans = the hard negatives the local clean-GT test lacked), extracts
fork candidates + graph/detection-score features + GT-matched labels, then does a
TRUE cross-embryo LOEO: train DivMLP on one embryo, test div_jaccard on the other,
vs the shipped geometric safe-div baseline (gate 2.25). No submission cost.

If learned div_jaccard beats geom on BOTH held-out embryos, build a submission that
swaps the geometric safe-div for the classifier (Direction A -> ~0.956 target).
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_NB = HERE / "sub_win-kunal917-exact" / "biohub-win-kunal917-exact.ipynb"
OUT_DIR = HERE / "division_cv"
OUT_DIR.mkdir(exist_ok=True)
src = json.loads(SRC_NB.read_text(encoding="utf-8"))

INSTALL = r'''
import os, glob, subprocess, sys
def _wheeldir(slug):
    for b in (f"/kaggle/input/{slug}", f"/kaggle/input/datasets/eeshsaxena/{slug}"):
        if os.path.isdir(b): return b
    h=[p for p in glob.glob(f"/kaggle/input/**/{slug}", recursive=True) if os.path.isdir(p)]
    return h[0] if h else None
r=subprocess.run([sys.executable,"-m","pip","install","-q","--no-index",
                  f"--find-links={_wheeldir('biohub-zarr-wheels')}","zarr"],capture_output=True,text=True)
print("zarr install rc",r.returncode)
import zarr; print("zarr",zarr.__version__)
'''

CELL = r'''
# ============ LEARNED DIVISION DETECTOR — cross-embryo LOEO CV ============
import numpy as np, time, glob
from pathlib import Path
from collections import defaultdict
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
TRAIN_DIR = Path(ROOT) / "train"

def read_geff_min(path):
    import zarr
    g = zarr.open_group(str(path), mode="r")
    ids = np.asarray(g["nodes/ids"][:]).astype(np.int64)
    t = np.asarray(g["nodes/props/t/values"][:]).astype(np.int64)
    z = np.asarray(g["nodes/props/z/values"][:]).astype(np.float64)
    y = np.asarray(g["nodes/props/y/values"][:]).astype(np.float64)
    x = np.asarray(g["nodes/props/x/values"][:]).astype(np.float64)
    try: e = np.asarray(g["edges/ids"][:]).astype(np.int64).reshape(-1,2)
    except KeyError: e = np.zeros((0,2),np.int64)
    return {"ids": ids, "t": t, "pos": np.stack([z,y,x],1), "edges": e}

def match_nodes(pt, pp, gt_t, gt_pos, maxd=7.0):
    out = np.full(len(pt), -1, np.int64)
    if len(pt)==0 or len(gt_t)==0: return out
    for tt in np.unique(gt_t):
        pi=np.nonzero(pt==tt)[0]; gi=np.nonzero(gt_t==tt)[0]
        if len(pi)==0 or len(gi)==0: continue
        d=np.linalg.norm((pp[pi][:,None]*SCALE)-(gt_pos[gi][None]*SCALE),axis=2)
        cost=np.where(d<=maxd,d,1e6); ri,ci=linear_sum_assignment(cost)
        for a,b in zip(ri,ci):
            if cost[a,b]<5e5: out[pi[a]]=gi[b]
    return out

def eval_div_arrays(pt, pp, pe, gt):
    match=match_nodes(pt,pp,gt["t"],gt["pos"])
    gi={int(v):i for i,v in enumerate(gt["ids"])}; ng=len(gt["ids"])
    gc=defaultdict(list); gpar=defaultdict(list)
    for s,d in gt["edges"]:
        si,di=gi.get(int(s)),gi.get(int(d))
        if si is None or di is None: continue
        gc[si].append(di); gpar[di].append(si)
    gdiv=[i for i in range(ng) if len(gc[i])>=2]
    npred=len(pt); pc=defaultdict(list); ppar=defaultdict(list)
    for a,b in pe: pc[int(a)].append(int(b)); ppar[int(b)].append(int(a))
    pf=[i for i in range(npred) if len(pc[i])>=2]
    evalable={f for f in pf if match[f]>=0 and len(gc[int(match[f])])>=1}
    bip=defaultdict(set)
    for D in gdiv:
        pside={D}|set(gpar[D]); lin={}
        for li,c in enumerate(gc[D]):
            lin.setdefault(c,li)
            for g2 in gc[c]: lin.setdefault(g2,li)
        for F in pf:
            pfs={F}|set(ppar[F])
            if not any(match[x]>=0 and int(match[x]) in pside for x in pfs): continue
            lins=set()
            for c in pc[F]:
                for x in [c,*pc[c]]:
                    m=int(match[x])
                    if m>=0 and m in lin: lins.add(lin[m])
            if len(lins)>=2: bip[D].add(F)
    mr={}; ml={}
    def aug(u,seen):
        for v in bip.get(u,()):
            if v in seen: continue
            seen.add(v)
            if v not in mr or aug(mr[v],seen): ml[u]=v; mr[v]=u; return True
        return False
    for u in gdiv: aug(u,set())
    tp=len(ml); fp=len(evalable-set(ml.values())); fn=len(gdiv)-tp
    return tp,fp,fn

# ---- repair returning the INTERNAL graph + detection scores (fill1 config) ----
_FILL=dict(unet_thr=0.15,max_dt=1,gate=4.5,snap=3.2,mincand=0.10,cap=0.08,synth=True)
def repair_graph(dets):
    ut=_FILL["unet_thr"]; nodes={}; frame_ids=[]; cand=[]; cand_sc=[]; cand_trees=[]; nid=1; NSC={}
    for t,(coords,scores) in enumerate(dets):
        coords=np.asarray(coords,float).reshape(-1,3); scores=np.asarray(scores,float).reshape(-1)
        seeds=coords[scores>=ut]; seed_sc=scores[scores>=ut]
        cm=(scores>=CAND_THR)&(scores<ut); cand.append(coords[cm]); cand_sc.append(scores[cm])
        cand_trees.append(cKDTree(cand[-1]*SCALE) if len(cand[-1]) else None); ids=[]
        for xyz,s_ in zip(seeds,seed_sc):
            nodes[nid]={"t":t,"xyz":np.asarray(xyz,float)}; NSC[nid]=float(s_); ids.append(nid); nid+=1
        frame_ids.append(ids)
    edges=[]; succ={}; pred={}; vel={}
    for t in range(len(dets)-1):
        P=np.asarray([nodes[g]["xyz"] for g in frame_ids[t]],float).reshape(-1,3)
        C=np.asarray([nodes[g]["xyz"] for g in frame_ids[t+1]],float).reshape(-1,3)
        if len(P)==0 or len(C)==0: continue
        pv=np.array([vel.get(g,np.zeros(3)) for g in frame_ids[t]])
        psc=np.array([NSC[g] for g in frame_ids[t]]); csc=np.array([NSC[g] for g in frame_ids[t+1]])
        for pi,ci in _link_sim(P,C,pv if len(pv) else None,psc,csc):
            gp,gcc=frame_ids[t][pi],frame_ids[t+1][ci]
            edges.append((gp,gcc)); succ[gp]=gcc; pred[gcc]=gp; vel[gcc]=(C[ci]-P[pi])*SCALE
    # aggressive fill (reuse cell-4 helpers via a local 1-frame synth pass)
    from collections import defaultdict as _dd
    T=len(cand); s2={}; p2={}
    for a,b in edges: s2[a]=b; p2[b]=a
    by_t=_dd(list)
    for k,n in nodes.items(): by_t[n["t"]].append(k)
    max_gaps=max(1,int(_FILL["cap"]*len(nodes))); nadd=0; BIG=1e9
    for t in range(T-2):
        if nadd>=max_gaps: break
        ends=[g for g in by_t.get(t,[]) if g not in s2 and g in p2]
        starts=[g for g in by_t.get(t+2,[]) if g not in p2 and g in s2]
        if not ends or not starts: continue
        Pe=np.asarray([nodes[g]["xyz"] for g in ends],float)*SCALE
        Cs=np.asarray([nodes[g]["xyz"] for g in starts],float)*SCALE
        D=np.sqrt(((Pe[:,None]-Cs[None])**2).sum(2)); cost=np.where(D>_FILL["gate"]*2,BIG,D)
        ri,ci=linear_sum_assignment(cost)
        for _d,r,c in sorted(((float(D[r,c]),r,c) for r,c in zip(ri,ci) if cost[r,c]<BIG)):
            if nadd>=max_gaps: break
            ge,gs=ends[r],starts[c]
            if ge in s2 or gs in p2: continue
            mid=0.5*(nodes[ge]["xyz"]+nodes[gs]["xyz"]); use=None
            tr=cand_trees[t+1]
            if tr is not None:
                dist,idx=tr.query(mid*SCALE)
                if dist<=_FILL["snap"] and cand_sc[t+1][idx]>=_FILL["mincand"]:
                    use=np.asarray(cand[t+1][idx],float)
            if use is None: use=mid
            ng=nid; nid+=1; nodes[ng]={"t":t+1,"xyz":np.asarray(use,float)}; NSC[ng]=float(_FILL["mincand"])
            edges.append((ge,ng)); edges.append((ng,gs)); s2[ge]=ng; p2[ng]=ge; s2[ng]=gs; p2[gs]=ng; nadd+=1
    nodes,edges=_short_filter(nodes,edges); _linefit(nodes,edges)
    return nodes,edges,NSC

# ---- fork candidates + features + GT-matched labels ----
FEAT=["d_pc","d_pq","d_sis","d_ratio","diverge","cos_ang","ptrack","c1cont","qcont","sp","sc1","sq","tfrac"]
def fork_candidates(nodes,edges,parent_um=15.0,sister_um=18.0,child_um=12.0):
    succ=defaultdict(list); pred=defaultdict(list)
    for a,b in edges: succ[a].append(b); pred[b].append(a)
    by_t=defaultdict(list)
    for k,n in nodes.items(): by_t[n["t"]].append(k)
    o_ids={}; o_tree={}
    for t,ids in by_t.items():
        orph=[g for g in ids if not pred.get(g)]; o_ids[t]=orph
        if orph: o_tree[t]=cKDTree(np.asarray([nodes[g]["xyz"] for g in orph],float)*SCALE)
    cands=[]
    def d_um(a,b): return float(np.sqrt((((np.asarray(a,float)-np.asarray(b,float))*SCALE)**2).sum()))
    for p,n in nodes.items():
        ch=succ.get(p,[])
        if len(ch)!=1: continue
        c1=ch[0]; t=n["t"]
        if nodes[c1]["t"]!=t+1 or d_um(n["xyz"],nodes[c1]["xyz"])>child_um: continue
        tr=o_tree.get(t+1)
        if tr is None: continue
        for idx in tr.query_ball_point(n["xyz"]*SCALE,r=parent_um):
            q=o_ids[t+1][idx]
            if q==c1 or d_um(nodes[c1]["xyz"],nodes[q]["xyz"])>sister_um: continue
            cands.append({"p":p,"c1":c1,"q":q,"t":t})
    return cands,succ,pred

def feats(cands,nodes,succ,pred,NSC,nfr=100):
    def d_um(a,b): return float(np.sqrt((((np.asarray(a,float)-np.asarray(b,float))*SCALE)**2).sum()))
    def tlen(g,cap=10):
        n=0; cur=g
        while pred.get(cur) and len(pred[cur])==1 and n<cap: cur=pred[cur][0]; n+=1
        return n
    X=np.zeros((len(cands),len(FEAT)),np.float32)
    for i,cd in enumerate(cands):
        p,c1,q,t=cd["p"],cd["c1"],cd["q"],cd["t"]
        xp,xc,xq=nodes[p]["xyz"],nodes[c1]["xyz"],nodes[q]["xyz"]
        d_pc=d_um(xp,xc); d_pq=d_um(xp,xq); d_s=d_um(xc,xq)
        c1n=succ.get(c1,[]); qn=succ.get(q,[])
        div=(d_um(nodes[c1n[0]]["xyz"],nodes[qn[0]]["xyz"])-d_s) if (c1n and qn) else 0.0
        v1=(np.asarray(xc)-np.asarray(xp))*SCALE; v2=(np.asarray(xq)-np.asarray(xp))*SCALE
        nm=np.linalg.norm(v1)*np.linalg.norm(v2); cos=float(np.dot(v1,v2)/nm) if nm>1e-6 else 0.0
        X[i]=[d_pc,d_pq,d_s,d_pq/(d_pc+1e-3),div,cos,tlen(p),
              1.0 if c1n else 0.0,1.0 if qn else 0.0,
              NSC.get(p,0.15),NSC.get(c1,0.15),NSC.get(q,0.15),t/max(1,nfr)]
    return X

def labels_real(cands,nodes,edges,gt):
    nids=sorted(nodes); nidx={n:i for i,n in enumerate(nids)}
    pt=np.array([nodes[n]["t"] for n in nids],np.int64)
    pp=np.array([nodes[n]["xyz"] for n in nids],float).reshape(-1,3)
    match=match_nodes(pt,pp,gt["t"],gt["pos"])
    gi={int(v):i for i,v in enumerate(gt["ids"])}
    gc=defaultdict(list)
    for s,d in gt["edges"]:
        si,di=gi.get(int(s)),gi.get(int(d))
        if si is not None and di is not None: gc[si].append(di)
    gdiv=set(i for i in range(len(gt["ids"])) if len(gc[i])>=2)
    lineage={}
    for D in gdiv:
        lm={}
        for li,c in enumerate(gc[D]):
            lm.setdefault(c,li)
            for g2 in gc[c]: lm.setdefault(g2,li)
        lineage[D]=lm
    y=np.zeros(len(cands),np.int64)
    for k,cd in enumerate(cands):
        mp=match[nidx[cd["p"]]]
        if mp<0 or int(mp) not in gdiv: continue
        lm=lineage[int(mp)]
        m1=match[nidx[cd["c1"]]]; mq=match[nidx[cd["q"]]]
        l1=lm.get(int(m1),-1) if m1>=0 else -2; lq=lm.get(int(mq),-1) if mq>=0 else -3
        if l1>=0 and lq>=0 and l1!=lq: y[k]=1
    return y

class DivMLP:
    def __init__(self,nf,h=32):
        import torch.nn as nn, torch; torch.manual_seed(0)
        self.net=nn.Sequential(nn.Linear(nf,h),nn.ReLU(),nn.Linear(h,h),nn.ReLU(),nn.Linear(h,1)); self.mu=None;self.sd=None
    def fit(self,X,y,ep=400):
        import torch, torch.nn as nn
        X=np.asarray(X,np.float32); self.mu=X.mean(0,keepdims=True); self.sd=X.std(0,keepdims=True)+1e-6
        xt=torch.from_numpy((X-self.mu)/self.sd); yt=torch.from_numpy(np.asarray(y,np.float32))[:,None]
        pw=(len(yt)-max(1,int(yt.sum())))/max(1,int(yt.sum()))
        lf=nn.BCEWithLogitsLoss(pos_weight=torch.tensor([float(pw)])); op=torch.optim.Adam(self.net.parameters(),lr=1e-3,weight_decay=1e-4)
        self.net.train()
        for _ in range(ep): op.zero_grad(); l=lf(self.net(xt),yt); l.backward(); op.step()
        return self
    def proba(self,X):
        import torch
        self.net.eval()
        with torch.no_grad():
            X=(np.asarray(X,np.float32)-self.mu)/self.sd
            return torch.sigmoid(self.net(torch.from_numpy(X)))[:,0].numpy()

def score_learned(nodes,edges,cands,proba,tau,gt,frame_cap=0.02,global_cap=0.02):
    order=np.argsort(-proba); used_p=set(); used_q=set(); per=defaultdict(int)
    by_t=defaultdict(int)
    for n in nodes.values(): by_t[n["t"]]+=1
    mx=max(1,int(global_cap*len(nodes))); E=list(edges); added=0
    for i in order:
        if proba[i]<tau or added>=mx: break
        cd=cands[i]
        if cd["p"] in used_p or cd["q"] in used_q: continue
        if per[cd["t"]]>=max(1,int(frame_cap*by_t.get(cd["t"],1))): continue
        E.append((cd["p"],cd["q"])); used_p.add(cd["p"]); used_q.add(cd["q"]); per[cd["t"]]+=1; added+=1
    nids=sorted(nodes); idx={n:i for i,n in enumerate(nids)}
    pt=np.array([nodes[n]["t"] for n in nids],np.int64); pp=np.array([nodes[n]["xyz"] for n in nids],float).reshape(-1,3)
    pe=np.array([(idx[a],idx[b]) for a,b in E if a in idx and b in idx],np.int64).reshape(-1,2)
    return eval_div_arrays(pt,pp,pe,gt)

# ---- run: extract per-movie (features computed ONCE with real scores), LOEO ----
N_PER_EMB=6; STRIDE=1; BUDGET=6*3600
geffs=sorted(TRAIN_DIR.glob("*.geff")); by_emb={}
for gp in geffs:
    zp=gp.with_suffix(".zarr")
    if not zp.exists(): continue
    g=read_geff_min(gp)
    by_emb.setdefault(gp.name.split("_")[0],[]).append((len(g["ids"]),gp,zp))
sel=[]
for emb,lst in sorted(by_emb.items()):
    lst.sort(reverse=True); sel+=[(emb,)+x[1:] for x in lst[:N_PER_EMB]]
print("selected",len(sel),"movies:",{k:min(len(v),N_PER_EMB) for k,v in by_emb.items()},flush=True)

records=[]; t0=time.time()   # (emb, gt, nodes, edges, cands, X, y)
for emb,gp,zp in sel:
    if time.time()-t0>BUDGET: print("budget hit"); break
    gt=read_geff_min(gp); meta=read_array_meta(zp); T=meta["shape"][0]
    present=[t for t in range(T) if (Path(zp)/"0"/"c"/str(t)/"0"/"0"/"0").exists()]
    Tmax=(max(present)+1) if present else 0; frames=list(range(0,Tmax,STRIDE))
    dets=[detect(load_volume(zp,f,meta)) for f in frames]; gc.collect()
    nodes,edges,NSC=repair_graph(dets)
    cands,succ,pred=fork_candidates(nodes,edges)
    if cands:
        X=feats(cands,nodes,succ,pred,NSC); y=labels_real(cands,nodes,edges,gt)
    else:
        X=np.zeros((0,len(FEAT)),np.float32); y=np.zeros(0,np.int64)
    records.append((emb,gt,nodes,edges,cands,X,y))
    print(f"  {emb} {gp.stem}: cands={len(cands)} pos={int(y.sum())} ({time.time()-t0:.0f}s)",flush=True)

embs=sorted(set(r[0] for r in records))

def _base_dj(gt,nodes,edges):
    nids=sorted(nodes); idx={n:i for i,n in enumerate(nids)}
    pt=np.array([nodes[n]["t"] for n in nids],np.int64); pp=np.array([nodes[n]["xyz"] for n in nids],float).reshape(-1,3)
    pe=np.array([(idx[a],idx[b]) for a,b in edges if a in idx and b in idx],np.int64).reshape(-1,2)
    return eval_div_arrays(pt,pp,pe,gt)

def dj_over(recs, clf, tau):
    tp=fp=fn=0
    for (emb,gt,nodes,edges,cands,X,y) in recs:
        if len(cands)==0: t,f,n=_base_dj(gt,nodes,edges)
        else: t,f,n=score_learned(nodes,edges,cands,clf.proba(X),tau,gt)
        tp+=t; fp+=f; fn+=n
    return (tp/(tp+fp+fn) if (tp+fp+fn) else float("nan")),tp,fp,fn

def geom_over(recs, gate):
    global DIV_DIVERGE_UM; tp=fp=fn=0
    for (emb,gt,nodes,edges,cands,X,y) in recs:
        n2={k:dict(v) for k,v in nodes.items()}; e2=list(edges)
        DIV_DIVERGE_UM=gate; _add_safe_divisions(n2,e2)
        t,f,n=_base_dj(gt,n2,e2); tp+=t; fp+=f; fn+=n
    return (tp/(tp+fp+fn) if (tp+fp+fn) else float("nan")),tp,fp,fn

print("\n================ cross-embryo LOEO div_jaccard ================",flush=True)
for test_e in embs:
    tr=[r for r in records if r[0]!=test_e]; te=[r for r in records if r[0]==test_e]
    Xtr=[r[5] for r in tr if len(r[5])]; ytr=[r[6] for r in tr if len(r[6])]
    if not Xtr or sum(int(y.sum()) for y in ytr)<2:
        print(f"[test {test_e}] insufficient train positives",flush=True); continue
    Xtr=np.concatenate(Xtr); ytr=np.concatenate(ytr)
    clf=DivMLP(Xtr.shape[1]).fit(Xtr,ytr)
    best=(-1,0.5)
    for tau in np.linspace(0.3,0.95,14):
        dj,*_=dj_over(tr,clf,float(tau))
        if dj==dj and dj>best[0]: best=(dj,float(tau))
    tau=best[1]
    g=geom_over(te,2.25); L=dj_over(te,clf,tau)
    print(f"[test {test_e}] tau={tau:.2f} trainpos={int(ytr.sum())} | "
          f"geom@2.25 divJ={g[0]:.3f} ({g[1]}/{g[2]}/{g[3]}) | "
          f"LEARNED divJ={L[0]:.3f} ({L[1]}/{L[2]}/{L[3]})",flush=True)

print("\nIf LEARNED > geom@2.25 on BOTH held-out embryos, build the submission that")
print("swaps _add_safe_divisions for the classifier. div_jaccard 0.13->~0.5 => ~0.956.")
'''

install_cell={"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":INSTALL}
div_cell={"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":CELL}
nb=dict(src); nb["cells"]=[install_cell]+[src["cells"][i] for i in (0,1,2,3,4)]+[div_cell]
nbp=OUT_DIR/"biohub-division-cv.ipynb"; nbp.write_text(json.dumps(nb),encoding="utf-8")
meta={"id":"eeshsaxena/biohub-division-cv","title":"Biohub division cv","code_file":"biohub-division-cv.ipynb",
      "language":"python","kernel_type":"notebook","is_private":True,"enable_gpu":True,"enable_tpu":False,
      "enable_internet":False,"machine_shape":"NvidiaTeslaT4","keywords":["gpu"],
      "dataset_sources":["xiaoleilian/biohub-unet3d-weights","xiaoleilian/biohub-unet3d-weights-v2models","eeshsaxena/biohub-zarr-wheels"],
      "kernel_sources":[],"competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
(OUT_DIR/"kernel-metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
print("built",nbp,"| cells",len(nb["cells"]))
