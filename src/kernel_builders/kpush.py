import sys, types, re, unicodedata
# Correct Py3 slugify, injected BEFORE kaggle imports the broken shadow stub
m = types.ModuleType('slugify')
def slugify(string):
    s = unicodedata.normalize('NFKD', str(string)).encode('ascii','ignore').decode('ascii')
    s = re.sub(r'[^\w\s-]', '', s).strip().lower()
    return re.sub(r'[-\s]+', '-', s)
m.slugify = slugify
sys.modules['slugify'] = m

from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi(); api.authenticate()
for folder in sys.argv[1:]:
    try:
        r = api.kernels_push(folder)
        ref = getattr(r, 'ref', None) or getattr(r, 'versionNumber', r)
        err = getattr(r, 'error', None)
        print(f'PUSHED {folder}: ref={ref} err={err}')
    except Exception as e:
        print(f'FAIL {folder}: {type(e).__name__}: {e}')
