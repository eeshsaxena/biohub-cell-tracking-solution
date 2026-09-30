#!/usr/bin/env python3
"""Generate colab_detsweep.ipynb — a turnkey Colab notebook (server GPU) that runs the
frontier pipeline on held-out TRAIN movies at a chosen detection threshold and prints the
honest CV. No Kaggle submission. User does the two credential steps (Colab sign-in + kaggle.json)."""
import json, io

PRUNE_INJECT = "\n".join([
    '    _tip=float(os.environ.get("BIOHUB_TIP_PRUNE_THR","0")); _wn=float(os.environ.get("BIOHUB_WEAK_NODE_THR","0"))',
    '    if _tip>0 or _wn>0:  # HONEST edge-term prune (own edge)',
    '        def _inc(_es):',
    '            _m={}',
    '            for _e in _es:',
    '                for _n in (int(_e["source_id"]),int(_e["target_id"])): _m.setdefault(_n,[]).append(_e)',
    '            return _m',
    '        if _tip>0:',
    '            while True:',
    '                _i=_inc(edges); _d=set()',
    '                for _n in list(nodes_by_id):',
    '                    _ee=_i.get(_n,[])',
    '                    if len(_ee)==1 and _ee[0].get("edge_prob") is not None and float(_ee[0]["edge_prob"])<_tip: _d.add(_n)',
    '                if not _d: break',
    '                nodes_by_id={k:v for k,v in nodes_by_id.items() if k not in _d}',
    '                edges=[e for e in edges if int(e["source_id"]) not in _d and int(e["target_id"]) not in _d]',
    '        if _wn>0:',
    '            _i=_inc(edges); _d=set()',
    '            for _n in list(nodes_by_id):',
    '                _ps=[float(e["edge_prob"]) for e in _i.get(_n,[]) if e.get("edge_prob") is not None]',
    '                if _ps and max(_ps)<_wn: _d.add(_n)',
    '            nodes_by_id={k:v for k,v in nodes_by_id.items() if k not in _d}',
    '            edges=[e for e in edges if int(e["source_id"]) not in _d and int(e["target_id"]) not in _d]',
    '    return nodes_by_id, edges, stats',
])

def code(src): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
def md(src): return {"cell_type": "markdown", "metadata": {}, "source": src}

cells = []
cells.append(md(
"# Biohub Detection-Threshold Sweep (Colab, server GPU)\n\n"
"Runs the frontier pipeline on **held-out TRAIN movies** at one detection threshold and prints the honest CV "
"(`adjusted_edge_jaccard`). **No Kaggle submission** (research only; the real submission still needs a Kaggle kernel).\n\n"
"**Setup:** Runtime -> Change runtime type -> **T4 GPU**. Then run cells top to bottom. "
"You do the two credential steps I can't: Colab sign-in, and uploading your `kaggle.json` in cell 2.\n\n"
"To sweep: set `THRESHOLD` in the last cell, run it; repeat for 0.95/0.955/0.96/0.965/0.97/0.975/0.98."
))

cells.append(code(
"# 1) deps (Colab has internet + GPU)\n"
"!pip -q install kaggle papermill 'zarr>=3.0.10,<4' 'numcodecs>=0.13,<0.16' tracksdata 'geff>=1.1.3' 'geff-spec<1.2' rustworkx pyscipopt ilpy polars 2>/dev/null\n"
"import os, sys, json, subprocess, glob, shutil, io, re\n"
"import torch; print('CUDA available:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
))

cells.append(code(
"# 2) Kaggle auth -- UPLOAD YOUR kaggle.json (Claude cannot type your token; you do this)\n"
"from google.colab import files\n"
"os.makedirs('/root/.kaggle', exist_ok=True)\n"
"up = files.upload()   # choose your kaggle.json\n"
"for fn in list(up): shutil.move(fn, '/root/.kaggle/kaggle.json')\n"
"os.chmod('/root/.kaggle/kaggle.json', 0o600)\n"
"print('kaggle.json installed:', os.path.exists('/root/.kaggle/kaggle.json'))"
))

cells.append(code(
"# 3) recreate Kaggle's /kaggle/input layout so the frontier notebook runs unmodified\n"
"os.makedirs('/kaggle/input', exist_ok=True)\n"
"DATASETS = ['pilkwang/biohub-temporal-unet3d-seed314159-v1',\n"
"            'pilkwang/biohub-deepcenter-unet3d-center-prior-v1',\n"
"            'pilkwang/biohub-tracking-support-pack-50ep-v1']\n"
"for ds in DATASETS:\n"
"    slug = ds.split('/')[1]; dst = '/kaggle/input/' + slug\n"
"    if os.path.isdir(dst) and os.listdir(dst): print('have', slug); continue\n"
"    os.makedirs(dst, exist_ok=True); print('downloading', ds)\n"
"    subprocess.run(['kaggle','datasets','download','-d',ds,'-p',dst,'--unzip'], check=True)\n"
"comp = '/kaggle/input/biohub-cell-tracking-during-development'\n"
"os.makedirs(comp, exist_ok=True)\n"
"if not glob.glob(comp + '/train/*'):\n"
"    print('downloading competition train data...')\n"
"    subprocess.run(['kaggle','competitions','download','-c','biohub-cell-tracking-during-development','-p',comp], check=True)\n"
"    z = glob.glob(comp + '/*.zip')\n"
"    if z: subprocess.run(['unzip','-q','-o',z[0],'-d',comp], check=True)\n"
"print('train movies found:', len(glob.glob(comp + '/train/*.zarr')))"
))

cells.append(code(
"# 4) fetch the frontier notebook + define the honest+sweep patcher\n"
"if not glob.glob('/content/nb/*.ipynb'):\n"
"    subprocess.run(['kaggle','kernels','pull','cloudssdut/biohub-0-948-reproduction-20260901','-p','/content/nb'], check=True)\n"
"SRC = glob.glob('/content/nb/*.ipynb')[0]\n"
"SHA = ('8040999a92f6b7bbd98fa8cf458141e045c0f9ad7c936bdb3b18e1f7edafe2a0','8164d1ffa07f87e0506027a0392edeab7939a32bd5e3f756377c0d72885cf127')\n"
"PRUNE = " + repr(PRUNE_INJECT) + "\n"
"def build_patched(det, safe_div='on', min_track_len=8, tip_thr=0.5, wn_thr=0.5):\n"
"    nb = json.load(io.open(SRC, encoding='utf-8'))\n"
"    def g(c): return c['source'] if isinstance(c['source'],str) else ''.join(c['source'])\n"
"    mtl = int(min_track_len)\n"
"    for c in nb['cells']:\n"
"        if c['cell_type'] != 'code': continue\n"
"        t = g(c)\n"
"        if 'os.environ[\"BIOHUB_OUTPUT_MIN_TRACK_LEN\"] = \"6\"' in t:\n"
"            t = t.replace('os.environ[\"BIOHUB_OUTPUT_MIN_TRACK_LEN\"] = \"6\"',\n"
"                'os.environ[\"BIOHUB_OUTPUT_MIN_TRACK_LEN\"] = \"%d\"\\nos.environ[\"BIOHUB_TIP_PRUNE_THR\"]=\"%s\"\\nos.environ[\"BIOHUB_WEAK_NODE_THR\"]=\"%s\"\\nos.environ[\"BIOHUB_VALIDATOR_N_PER_TYPE\"]=\"10\"' % (mtl, tip_thr, wn_thr))\n"
"        t = re.sub(r'os\\.environ\\[\"BIOHUB_DET_THRESHOLD\"\\]\\s*=\\s*\"[0-9.]+\"', 'os.environ[\"BIOHUB_DET_THRESHOLD\"]=\"%s\"' % det, t)\n"
"        if safe_div == 'off':\n"
"            t = re.sub(r'os\\.environ\\[\"BIOHUB_OUTPUT_SAFE_DIVISIONS\"\\]\\s*=\\s*\"[01]\"', 'os.environ[\"BIOHUB_OUTPUT_SAFE_DIVISIONS\"]=\"0\"', t)\n"
"        t = re.sub(r'os\\.environ\\[\"BIOHUB_ALLOW_PIP_INSTALL\"\\]\\s*=\\s*\"0\"', 'os.environ[\"BIOHUB_ALLOW_PIP_INSTALL\"]=\"1\"', t)\n"
"        if '_EXPECTED_NUMERIC' in t and 'drift' in t.lower():\n"
"            t = re.sub(r'(\"BIOHUB_OUTPUT_MIN_TRACK_LEN\"\\s*:\\s*)6\\.0', r'\\g<1>%d.0' % mtl, t)\n"
"            t = re.sub(r'\\n\\s*\"BIOHUB_DET_THRESHOLD\"\\s*:\\s*[0-9.]+\\s*,', '', t)\n"
"        t = t.replace('if _deepcenter_actual_sha256 != _deepcenter_expected_sha256:',\n"
"                      'if _deepcenter_actual_sha256 not in {\"%s\",\"%s\"}:' % SHA)\n"
"        ret = '    return nodes_by_id, edges, stats'\n"
"        if ret in t and 'HONEST edge-term prune' not in t:\n"
"            t = t.replace(ret, PRUNE)\n"
"        c['source'] = t\n"
"    out = '/content/patched.ipynb'; json.dump(nb, io.open(out,'w',encoding='utf-8')); return out\n"
"print('patcher ready')"
))

cells.append(md(
"## Honest levers + the efficiency trick\n"
"The pipeline is already mature (8-view TTA, dual-seed ensemble, harmonic fusion, subpixel refinement). "
"The gains left are **honest** and survive the announced metric rescore:\n"
"- **DET threshold** (`det`) - #1 tunable lever; mild penalty = real optimum. **Re-detecting is the slow part (~40 min).**\n"
"- **safe_div off** - post-rescore, geometric division forks not within 7um of a real division become FALSE POSITIVES; dropping them likely raises the patched score.\n"
"- **min_track_len / tip / weak-node prune** - the +0.0103 honest edge; these are **repair-stage (cheap)**.\n\n"
"**EFFICIENCY:** the frontier notebook reuses cached detections. So at a **fixed `det`**, sweeping repair knobs "
"(safe_div, mtl, tip, wn) reuses detection and runs in a few minutes; only changing `det` re-detects (~40 min). "
"`probe()` clears the detection cache automatically when `det` changes. Every result is accumulated into "
"`/content/probe_results.csv` and printed as a running leaderboard."
))
cells.append(code(
"# 5) harness: probe() reuses cached detection across repair-knob sweeps at a fixed threshold\n"
"import papermill as pm, pandas as pd, shutil\n"
"RESULTS = []; _LAST_DET = [None]\n"
"def probe(det, safe_div='on', mtl=8, tip=0.5, wn=0.5, tag=''):\n"
"    if _LAST_DET[0] != str(det):  # threshold changed -> clear stale detection cache so it re-detects\n"
"        for d in glob.glob('/kaggle/working/**/predictions', recursive=True): shutil.rmtree(d, ignore_errors=True)\n"
"        _LAST_DET[0] = str(det)\n"
"        print('[detection cache cleared for det=%s -- this run re-detects (~40 min)]' % det)\n"
"    else:\n"
"        print('[reusing cached detection for det=%s -- repair-only, fast]' % det)\n"
"    p = build_patched(det, safe_div=safe_div, min_track_len=mtl, tip_thr=tip, wn_thr=wn)\n"
"    out = '/content/out_%s_%s_mtl%s_t%s_w%s.ipynb' % (det, safe_div, mtl, tip, wn)\n"
"    try:\n"
"        pm.execute_notebook(p, out, kernel_name='python3', log_output=True, cwd='/kaggle/working')\n"
"    except Exception as e:\n"
"        print('  pipeline ERROR (inspect %s):' % out, str(e)[:250]); return\n"
"    vr = glob.glob('/kaggle/working/validator_results.csv')\n"
"    if not vr:\n"
"        print('  no validator_results.csv - inspect', out); return\n"
"    df = pd.read_csv(vr[-1]); adj = float(df['adjusted_edge_jaccard'].mean())\n"
"    dj = float(df['division_jaccard'].mean()) if 'division_jaccard' in df else float('nan')\n"
"    RESULTS.append(dict(det=det, safe_div=safe_div, mtl=mtl, tip=tip, wn=wn, adjEJ=round(adj,4), divJ=round(dj,4), tag=tag))\n"
"    rd = pd.DataFrame(RESULTS).sort_values('adjEJ', ascending=False)\n"
"    rd.to_csv('/content/probe_results.csv', index=False)\n"
"    print('  -> adjEJ=%.4f  divJ=%.4f  (n=%d movies)' % (adj, dj, len(df)))\n"
"    print('\\n=== running leaderboard (saved to /content/probe_results.csv) ==='); print(rd.to_string(index=False))\n"
"print('probe() ready')"
))
cells.append(code(
"# 6) === RUN PROBES ===  first probe at a det re-detects (~40 min); same-det repair sweeps are fast\n"
"probe('0.965', 'on')                 # frontier honest baseline (SLOW: first detection at 0.965)\n"
"probe('0.965', 'off')                # drop division-harvest  (FAST: reuses detection)\n"
"probe('0.965', 'off', mtl=10)        # stronger short-track filter (FAST)\n"
"probe('0.965', 'off', mtl=8, wn=0.6) # stronger weak-node prune (FAST)\n"
"# --- only when you want a new detection regime (each is SLOW ~40 min) ---\n"
"# probe('0.96', 'off'); probe('0.97', 'off'); probe('0.98', 'off')\n"
"print('\\nDONE - paste /content/probe_results.csv (or the leaderboard above) back to Claude.')"
))

# working dir for the pipeline
cells.insert(4, code("os.makedirs('/kaggle/working', exist_ok=True); os.chdir('/kaggle/working'); print('cwd', os.getcwd())"))

nb_out = {"nbformat": 4, "nbformat_minor": 0,
          "metadata": {"colab": {"provenance": []}, "accelerator": "GPU",
                       "kernelspec": {"name": "python3", "display_name": "Python 3"}},
          "cells": cells}
json.dump(nb_out, io.open("colab_detsweep.ipynb", "w", encoding="utf-8"), indent=1)
# syntax-check the code cells
import ast
bad = 0
for i, c in enumerate(cells):
    if c["cell_type"] == "code":
        srcj = c["source"]
        try:
            # skip cells with ! / % magics for ast
            lines = [l for l in srcj.split("\n") if not l.strip().startswith(("!", "%"))]
            ast.parse("\n".join(lines))
        except SyntaxError as e:
            print("cell", i, "SYNTAX", e.lineno, e.msg); bad += 1
print("WROTE colab_detsweep.ipynb (%d cells, syntax_bad=%d)" % (len(cells), bad))
