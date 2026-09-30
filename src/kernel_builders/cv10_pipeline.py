#!/usr/bin/env python3
"""10-movie CV research pipeline. NO SUBMISSIONS. Just runs the two N5 kernels,
pulls their validators (prunes the 12MB submission.csv), records which deepcenter
checkpoint each run materialized, and writes a paired 10-movie CV verdict."""
import sys, types, re, unicodedata, subprocess, time, pathlib, json
m=types.ModuleType('slugify')
def sl(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',s).strip().lower())
m.slugify=sl; sys.modules['slugify']=m
from kaggle.api.kaggle_api_extended import KaggleApi
API=KaggleApi(); API.authenticate()
ROOT=pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG=ROOT/"cv10_pipeline.log"
VERD=ROOT/"cv10_VERDICT.txt"
def log(x):
    l=f"[{time.strftime('%H:%M:%SZ',time.gmtime())}] {x}"
    print(l,flush=True); open(LOG,'a',encoding='utf-8').write(l+"\n")
def st(kid):
    p=subprocess.run(['kaggle','kernels','status',kid],capture_output=True,text=True)
    mm=re.search(r'KernelWorkerStatus\.(\w+)',(p.stdout or '')+(p.stderr or ''))
    return mm.group(1) if mm else '?'
def push(folder):
    try:
        r=API.kernels_push(str(ROOT/'scratch_kernels'/folder))
        e=getattr(r,'error',None)
        if e and 'Maximum batch' in str(e): return 'SLOT_FULL'
        return 'PUSHED'
    except Exception as ex:
        return 'SLOT_FULL' if 'Maximum batch' in str(ex) else f'ERR:{ex}'
def sha_from_log(kid):
    try:
        t=API.kernels_logs(kid); s=t if isinstance(t,str) else json.dumps(t)
        try:
            arr=json.loads(s); s=''.join(e.get('data','') for e in arr if isinstance(e,dict))
        except Exception: pass
        mm=re.search(r'DeepCenter materialized SHA256:\s*([0-9a-f]{64})', s)
        return mm.group(1)[:8] if mm else '????'
    except Exception: return '????'
def pull(kid, sub):
    d=ROOT/'scratch_kernels'/sub; d.mkdir(exist_ok=True)
    subprocess.run(['kaggle','kernels','output',kid,'-p',str(d),'-q'],capture_output=True,text=True)
    csv=d/'submission.csv'
    if csv.exists(): csv.unlink()
    return d/'validator_results.csv'

BASE='eeshsaxena/biohub-v-cloud948-base-n5'
DET='eeshsaxena/biohub-v-cloud948-det098-n5'
log("cv10 pipeline start (NO submissions)")
det_pushed=False
for _ in range(90):
    sb=st(BASE)
    if sb in ('COMPLETE',) and not det_pushed:
        if st(DET) in ('ERROR','ABSENT','?','UNKNOWN'):
            if push('v_cloud948_det098_n5')=='PUSHED':
                log("pushed det098_n5"); det_pushed=True
    if st(BASE)=='COMPLETE' and st(DET)=='COMPLETE':
        break
    time.sleep(90)
# both done -> pull + compare
bsha, dsha = sha_from_log(BASE), sha_from_log(DET)
bval = pull(BASE,'out_base_n5'); dval = pull(DET,'out_det098_n5')
log(f"base_n5 deepcenter SHA={bsha} | det098_n5 SHA={dsha}")
r=subprocess.run(['python','scratch_kernels/paired_cv.py',
                  f'base_n5={bval}', f'det098_n5={dval}'],capture_output=True,text=True,cwd=str(ROOT))
out=r.stdout+r.stderr
VERD.write_text(f"10-MOVIE CV VERDICT\nbase_n5 deepcenter SHA={bsha} (8040999a=ORIGINAL/0.948-tuned, 8164d1ff=drifted)\n"
                f"det098_n5 deepcenter SHA={dsha}\n\n{out}\n")
log("WROTE cv10_VERDICT.txt")
log(out.strip()[-400:])
