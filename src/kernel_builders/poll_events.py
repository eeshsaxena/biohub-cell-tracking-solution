import sys, types, re, unicodedata, time
m=types.ModuleType('slugify')
def sl(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',s).strip().lower())
m.slugify=sl; sys.modules['slugify']=m
import subprocess
from kaggle.api.kaggle_api_extended import KaggleApi
api=KaggleApi(); api.authenticate()
COMP='biohub-cell-tracking-during-development'
bid_done=False; shz_done=False
def kstatus(kid):
    p=subprocess.run(['kaggle','kernels','status',kid],capture_output=True,text=True)
    mm=re.search(r'KernelWorkerStatus\.(\w+)',(p.stdout or '')+(p.stderr or ''))
    return mm.group(1) if mm else '?'
for _ in range(40):  # ~40 min at 60s
    if not bid_done:
        try:
            subs=api.competition_submissions(COMP)
            for s in subs[:3]:
                if 'bidir040' in (s.description or '') and s.public_score:
                    print(f'BIDIR040 SCORED: {s.public_score}', flush=True); bid_done=True; break
        except Exception as e:
            pass
    if not shz_done:
        st=kstatus('eeshsaxena/biohub-v-shienzhang')
        if st=='COMPLETE':
            print('SHIENZHANG COMPLETE (validator CV ready to pull)', flush=True); shz_done=True
        elif st in ('ERROR','CANCEL_ACKNOWLEDGED','CANCEL_REQUESTED'):
            print(f'SHIENZHANG {st} (guard or runtime error)', flush=True); shz_done=True
    if bid_done and shz_done:
        print('BOTH TERMINAL', flush=True); break
    time.sleep(60)
