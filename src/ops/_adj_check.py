import sys, importlib.util
spec = importlib.util.spec_from_file_location("sg", "ops/score_gt.py")
sg = importlib.util.module_from_spec(spec); spec.loader.exec_module(sg)
NEST={'44b6_0113de3b':25755.0,'44b6_0b24845f':32795.0,'6bba_05b6850b':6362.0,'6bba_05db0fb1':69800.0}
ALPHA=0.1
for path in sys.argv[1:]:
    rows=[sg.score_one(path,s) for s in sg.SCORED]
    print("\n=== "+path)
    tw=sum(r['denom'] for r in rows)
    adjw=0.0; rawJ=0.0
    for r in rows:
        ne=NEST[r['sample']]; ratio=(r['pred_nodes']-ne)/ne
        mult=1-ALPHA*ratio; adj=max(0.0,r['j']*mult)
        w=r['denom']/tw
        adjw+=adj*w; rawJ+=r['j']*w
        print("  %-16s J=%.4f ratio=%+.4f mult=%.5f adj=%.5f  w=%.4f FN=%4d nodes=%d"%(r['sample'],r['j'],ratio,mult,adj,w,r['fn'],r['pred_nodes']))
    print("  raw weighted J = %.5f"%rawJ)
    print("  ADJ weighted J = %.5f   (penalty contribution %+.5f)"%(adjw,adjw-rawJ))
