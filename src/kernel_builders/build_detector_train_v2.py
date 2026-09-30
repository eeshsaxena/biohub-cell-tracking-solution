"""USE-EVERYTHING detector training: the one live lever toward winning (Direction B).

Trains a heatmap detector on CC0 SYNTHETIC (dense labels) + REAL GT (sparse labels,
corrected weighted-BCE: firing on unannotated real cells is ~free -> avoids the old
0.682 dense-MSE memorisation bug). Real frames are POOLED by 4 in Y,X -> isotropic
64^3, matching the synthetic geometry so one detector spans both domains.

Evaluates LOEO held-out detection recall (peaks vs GT annotated cells @7um,
count-calibrated) against the fill1 detector's ~0.978. If held-out recall clears
0.978 by a real margin, this is a genuinely better base detector -> the path to a
winning edge term (edge_J ~= recall^2). Honest expectation: likely ~0.97-0.98
(domain gap + sparse real labels); a real gain is the goal but not guaranteed.

No submission cost (training/eval kernel). Saves unet_detector_v2.pth to output.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = HERE / "detector_train_v2"
OUT_DIR.mkdir(exist_ok=True)

DETECTOR = (ROOT / "kaggle" / "detector.py").read_text(encoding="utf-8")
SCORING = (ROOT / "kaggle" / "scoring.py").read_text(encoding="utf-8")

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
import zarr; print("zarr",zarr.__version__)
'''

DRIVER = r'''
# ===================== DETECTOR TRAINING (synthetic + real, LOEO recall) =====================
import numpy as np, glob, time, gc
from pathlib import Path
import torch, torch.nn.functional as F

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("device", DEVICE, "torch", torch.__version__, flush=True)
ISO = np.array([1.625, 1.625, 1.625])          # both domains after pooling
SIGMA_UM = 3.0
POOL = 4
PATCH = (24, 64, 64)
STEPS = int(os.environ.get("STEPS", "2500"))
BATCH = 4

def find_data_root():
    slug="biohub-cell-tracking-during-development"
    for c in (Path(f"/kaggle/input/competitions/{slug}"), Path(f"/kaggle/input/{slug}")):
        if (c/"train").exists(): return c/"train"
    for p in Path("/kaggle/input").rglob("train"):
        if p.is_dir() and any(p.glob("*.zarr")): return p
    raise RuntimeError("no train")
TRAIN = find_data_root()
SYN = sorted(glob.glob("/kaggle/input/**/sequences/*.npz", recursive=True))
print("real train:", len(list(TRAIN.glob("*.geff"))), "| synthetic seqs:", len(SYN), flush=True)

def read_geff_pts(gp):
    import zarr
    g=zarr.open_group(str(gp),mode="r")
    t=np.asarray(g["nodes/props/t/values"][:]).astype(np.int64)
    z=np.asarray(g["nodes/props/z/values"][:]).astype(np.float64)
    y=np.asarray(g["nodes/props/y/values"][:]).astype(np.float64)
    x=np.asarray(g["nodes/props/x/values"][:]).astype(np.float64)
    return t, np.stack([z,y,x],1)

def pool_frame(vol):  # (Z,Y,X) -> (Z, Y//4, X//4) mean pool in Y,X
    Z,Y,X=vol.shape; Y2,X2=(Y//POOL)*POOL,(X//POOL)*POOL
    v=vol[:,:Y2,:X2].astype(np.float32)
    return v.reshape(Z,Y2//POOL,POOL,X2//POOL,POOL).mean(axis=(2,4))

# ---- build frame providers: list of (frame_norm, pts_vox_pooled, dense_flag) ----
def synth_frames(cap=16):
    out=[]
    for f in SYN[:cap]:
        d=np.load(f,allow_pickle=True); vols=d["volumes"]; nodes=d["nodes"]
        for t in range(vols.shape[0]):
            pts=nodes[nodes[:,0]==t][:,1:4].astype(np.float32)  # zyx iso voxel
            out.append((normalize_frame(vols[t]), pts, True))
    return out

def real_frames(embryo, movie_cap=8, frame_cap=12):
    import zarr
    out=[]
    geffs=[gp for gp in sorted(TRAIN.glob("*.geff")) if gp.name.startswith(embryo)][:movie_cap]
    for gp in geffs:
        zp=gp.with_suffix(".zarr")
        if not zp.exists(): continue
        t,pos=read_geff_pts(gp)
        try: za=zarr.open(str(zp),mode="r")["0"]
        except Exception: continue
        frames=sorted(set(int(v) for v in t))[:frame_cap]
        for fr in frames:
            m=(t==fr)
            if m.sum()==0: continue
            try: vol=np.asarray(za[fr])
            except Exception: continue
            pv=pos[m].copy(); pv[:,1]/=POOL; pv[:,2]/=POOL   # pool Y,X coords
            out.append((normalize_frame(pool_frame(vol)), pv.astype(np.float32), False))
        gc.collect()
    return out

SIG = sigma_vox_from_um(SIGMA_UM, ISO)

def _peaks(hm, scale, thr, nms_um):
    from skimage.feature import peak_local_max
    from scipy.spatial import cKDTree
    pk=peak_local_max(hm, min_distance=1, threshold_abs=thr, exclude_border=False)
    if len(pk)==0: return np.zeros((0,3)), np.zeros(0)
    sc=hm[pk[:,0],pk[:,1],pk[:,2]]; pts=pk.astype(float)*scale
    order=np.argsort(-sc); tree=cKDTree(pts); killed=np.zeros(len(pk),bool); keep=[]
    for i in order:
        if killed[i]: continue
        keep.append(int(i)); killed[tree.query_ball_point(pts[i], nms_um)]=True
    keep=np.array(keep); return pk[keep].astype(float), sc[keep]   # sorted by score desc

def sample_batch(frames, rng, dense_ratio=0.5):
    xs=[]; ys=[]; ws=[]
    for _ in range(BATCH):
        fr,pts,dense = frames[rng.integers(len(frames))]
        x,y = sample_patch(fr, pts, PATCH, SIG, rng)   # each (1,Z,Y,X)
        neg_w = 1.0 if dense else 0.03
        w = np.where(y>0.05, 8.0, neg_w).astype(np.float32)
        xs.append(x); ys.append(y); ws.append(w)
    X=torch.from_numpy(np.stack(xs)).float().to(DEVICE)   # (B,1,Z,Y,X)
    Y=torch.from_numpy(np.stack(ys)).float().to(DEVICE)
    W=torch.from_numpy(np.stack(ws)).float().to(DEVICE)
    return X,Y,W

def train(frames, steps):
    model=build_unet(base=24,depth=3).to(DEVICE); model.train()
    opt=torch.optim.Adam(model.parameters(),lr=1e-3)
    rng=np.random.default_rng(0); t0=time.time()
    for s in range(steps):
        X,Y,W=sample_batch(frames,rng)
        pred=model(X)
        loss=F.binary_cross_entropy_with_logits(pred,Y,weight=W)
        opt.zero_grad(); loss.backward(); opt.step()
        if s%400==0: print(f"  step {s} loss {loss.item():.4f} ({time.time()-t0:.0f}s)",flush=True)
    model.eval(); return model

KS=[300, 500, 800, 0]   # count-calibrated recall @ top-K peaks/frame (0=all)
def recall_on(embryo, model, movie_cap=6, frame_cap=20, maxd=7.0):
    import zarr
    from scipy.optimize import linear_sum_assignment
    geffs=[gp for gp in sorted(TRAIN.glob("*.geff")) if gp.name.startswith(embryo)][:movie_cap]
    matched={k:0 for k in KS}; total=0; ndet=0; nfr=0
    for gp in geffs:
        zp=gp.with_suffix(".zarr")
        if not zp.exists(): continue
        t,pos=read_geff_pts(gp)
        try: za=zarr.open(str(zp),mode="r")["0"]
        except Exception: continue
        for fr in sorted(set(int(v) for v in t))[:frame_cap]:
            m=(t==fr); gtp=pos[m]
            if len(gtp)==0: continue
            try: vol=pool_frame(np.asarray(za[fr]))
            except Exception: continue
            hm=predict_heatmap(normalize_frame(vol),model,DEVICE)
            hm=1.0/(1.0+np.exp(-hm))
            coords,scores=_peaks(hm, ISO, 0.3, 4.0)   # sorted by score desc
            ndet+=len(coords); nfr+=1; total+=len(gtp)
            if len(coords)==0: continue
            gtp_p=gtp.copy(); gtp_p[:,1]/=POOL; gtp_p[:,2]/=POOL
            for K in KS:
                cc = coords if (K==0 or len(coords)<=K) else coords[:K]
                d=np.linalg.norm((cc[:,None]*ISO)-(gtp_p[None]*ISO),axis=2)
                cost=np.where(d<=maxd,d,1e6); ri,ci=linear_sum_assignment(cost)
                matched[K]+=sum(1 for a,b in zip(ri,ci) if cost[a,b]<5e5)
        gc.collect()
    return {K: matched[K]/max(1,total) for K in KS}, ndet/max(1,nfr)

# ---- run: LOEO. train on synth + other embryo, eval held-out ----
syn=synth_frames()
print("synthetic frames:", len(syn), flush=True)
EMB=["44b6","6bba"]
if os.environ.get("BIOHUB_FINAL","0")=="1":   # produce submission detector (all data, no holdout)
    tr = syn + real_frames("44b6") + real_frames("6bba")
    print(f"\nFINAL: train on synth+both ({len(tr)} frames), steps={STEPS}",flush=True)
    model=train(tr, STEPS)
    torch.save({"state_dict":model.state_dict(),"base":24,"depth":3,"mode":"final"},
               "/kaggle/working/unet_detector_final.pth")
    print("saved /kaggle/working/unet_detector_final.pth",flush=True); EMB=[]
for test_e in EMB:
    train_e=[e for e in EMB if e!=test_e][0]
    tr = syn + real_frames(train_e)
    print(f"\n[LOEO test={test_e}] train frames={len(tr)} (synth+{train_e}); steps={STEPS}",flush=True)
    model=train(tr, STEPS)
    rec, dpf = recall_on(test_e, model)
    rstr=" ".join(f"@{k or 'all'}={rec[k]:.3f}" for k in KS)
    print(f"[LOEO test={test_e}] held-out recall {rstr}  (raw det/frame~={dpf:.0f}; fill1 ~0.978 at ~500/frame)",flush=True)
    torch.save({"state_dict":model.state_dict(),"base":24,"depth":3,"test_embryo":test_e},
               f"/kaggle/working/unet_detector_v2_heldout_{test_e}.pth")
print("\nIf held-out recall clears 0.978 by a real margin -> better base detector; wire into")
print("the fill1 pipeline detection stage and CV the edge term. Else: domain gap confirms")
print("the public detectors are already near-ceiling on real recall.")
'''

install={"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":INSTALL}
det={"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":DETECTOR}
scr={"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":SCORING}
drv={"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":"import os\n"+DRIVER}
nb={"cells":[install,det,scr,drv],
    "metadata":{"kernelspec":{"name":"python3","display_name":"Python 3"}},"nbformat":4,"nbformat_minor":5}
nbp=OUT_DIR/"biohub-detector-train-v2.ipynb"; nbp.write_text(json.dumps(nb),encoding="utf-8")
meta={"id":"eeshsaxena/biohub-detector-train-v2","title":"Biohub detector train v2",
      "code_file":"biohub-detector-train-v2.ipynb","language":"python","kernel_type":"notebook",
      "is_private":True,"enable_gpu":True,"enable_tpu":False,"enable_internet":False,
      "machine_shape":"NvidiaTeslaT4","keywords":["gpu"],
      "dataset_sources":["hitoshisaito/biohub-synthetic16-cc0-subset","eeshsaxena/biohub-zarr-wheels"],
      "kernel_sources":[],"competition_sources":["biohub-cell-tracking-during-development"],"model_sources":[]}
(OUT_DIR/"kernel-metadata.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
print("built",nbp,"| cells",len(nb["cells"]))
