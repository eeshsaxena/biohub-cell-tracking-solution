import sys, importlib.util
import numpy as np
from collections import defaultdict
spec = importlib.util.spec_from_file_location("sg","ops/score_gt.py")
sg = importlib.util.module_from_spec(spec); spec.loader.exec_module(sg)
path=sys.argv[1]
TOT=defaultdict(int); near=0; dists=[]
for sample in sg.SCORED:
    gpos,gtof,gedges=sg.load_gt(sample)
    pnodes,pedges=sg.load_pred(path,sample)
    gt_by_t,pr_by_t=defaultdict(list),defaultdict(list)
    for i,tt in gtof.items(): gt_by_t[tt].append(i)
    for i,(tt,_) in pnodes.items(): pr_by_t[tt].append(i)
    from scipy.optimize import linear_sum_assignment
    match={}
    for tt,gids in gt_by_t.items():
        pids=pr_by_t.get(tt,[])
        if not pids: continue
        G=np.stack([gpos[i] for i in gids]); P=np.stack([pnodes[i][1] for i in pids])
        d=np.linalg.norm(G[:,None,:]-P[None,:,:],axis=2)
        cost=np.where(d<=sg.MATCH_UM,d,sg.MATCH_UM*10.0)
        ri,ci=linear_sum_assignment(cost)
        for a,b in zip(ri,ci):
            if d[a,b]<=sg.MATCH_UM: match[gids[a]]=pids[b]
    out=defaultdict(list)
    for s,t in pedges: out[s].append(t)
    gset={(int(a),int(b)) for a,b in gedges if gtof.get(int(b),-99)-gtof.get(int(a),-99)==1}
    for (ga,gb) in gset:
        pa,pb=match.get(ga),match.get(gb)
        if pa is not None and pb is not None:
            if pb in out.get(pa,[]): TOT['TP']+=1; continue
            TOT['LINK']+=1
            # did pa link somewhere?
            tg=out.get(pa,[])
            if tg:
                TOT['LINKED_ELSEWHERE']+=1
                correct=gpos[gb]
                dd=min(np.linalg.norm(pnodes[x][1]-correct) for x in tg)
                dists.append(dd)
                if dd<=sg.MATCH_UM: near+=1
            else: TOT['NO_OUT']+=1
        elif pa is None and pb is None: TOT['BOTH_MISSED']+=1
        else: TOT['DETECT']+=1
print(path)
for k in ['TP','LINK','LINKED_ELSEWHERE','NO_OUT','DETECT','BOTH_MISSED']:
    print("  %-18s %d"%(k,TOT[k]))
print("  FN total = %d"%(TOT['LINK']+TOT['DETECT']+TOT['BOTH_MISSED']))
print("  of LINKED_ELSEWHERE: chosen target within 7um of correct cell = %d"%near)
if dists: print("  median dist chosen->correct = %.2f um"%float(np.median(dists)))
