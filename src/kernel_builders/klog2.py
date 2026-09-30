import sys, types, re, unicodedata, json
m=types.ModuleType('slugify')
def sl(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[-\s]+','-',re.sub(r'[^\w\s-]','',s).strip().lower())
m.slugify=sl; sys.modules['slugify']=m
from kaggle.api.kaggle_api_extended import KaggleApi
api=KaggleApi(); api.authenticate()
txt=api.kernels_logs(sys.argv[1])
s=txt if isinstance(txt,str) else json.dumps(txt)
out=[]
try:
    arr=json.loads(s)
    for e in arr:
        d=e.get('data') if isinstance(e,dict) else None
        if d: out.append(d)
    s=''.join(out)
except Exception: pass
print(s[-2500:])
