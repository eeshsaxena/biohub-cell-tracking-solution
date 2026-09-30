import sys, types, re, unicodedata, time
m=types.ModuleType('slugify')
def sl(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',s).strip().lower())
m.slugify=sl; sys.modules['slugify']=m
from kaggle.api.kaggle_api_extended import KaggleApi
a=KaggleApi(); a.authenticate()
COMP='biohub-cell-tracking-during-development'
seen=set()
for _ in range(60):  # ~2h at 120s
    try:
        subs=a.competition_submissions(COMP)
        today=[x for x in subs if str(x.date).startswith('2026-09-02')]
        for s in today:
            if s.public_score and s.ref not in seen:
                seen.add(s.ref)
                tag=re.search(r'\[sweep\d+\]|cloud948|bidir040',(s.description or ''))
                tag=tag.group(0) if tag else (s.description or '')[:16]
                print(f'SCORE {tag} = {s.public_score}', flush=True)
        scored=[x for x in today if x.public_score]
        if len(today)>=5 and len(scored)>=len(today):
            print(f'ALL {len(scored)} TODAY SCORED', flush=True); break
    except Exception as e:
        pass
    time.sleep(120)
