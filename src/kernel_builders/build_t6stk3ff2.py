#!/usr/bin/env python3
"""t6stk3ff2 = t6stk3ff (t6stk3 body + IMGFLOW write-time repair) + the Track-B pre-registered extension
X2 FLOWCUT+RELINK (scratchpad/wf17/trackB/PREREG.md, offline twin ext.py flowcut() + a second flowfix.repair pass).

usage: python scratch_kernels/build_t6stk3ff2.py [tag] [--x1]
       default tag t6stk3ff2 (X2 = cut + relink); --x1 builds the cut-only variant (X1, RELINK False), default tag t6stk3fc

After the unchanged CFG0 repair (TF 5 / KEEP 3.5 / GATE 4.5 / MIN_DET 5 / ENDS), inside the SAME acted windows
(window flow |f| >= 5 um and >= 5 written nodes): every source with total out-degree 1 whose edge goes to t+1 loses that
edge if its flow residual |p_b - p_a - f| >= 6.5 um AND cos(p_b - p_a, f) < 0.8 (X1); then (X2) one more CFG0 repair
pass on the cut graph with the same flows (freed targets are re-assigned, cut track ends may be bridged).
Nodes and forks are never touched; the invariant check now also allows out-degree 1 -> 0 (the cut). Everything else
(flows, guards, deadline, fallbacks, markers) is the t6stk3ff helper byte for byte; the delta is applied by exact,
count-checked string replacement on build_t6r70ff.HELPER, and the result is checked against the offline twin by
scratchpad/wf17/trackB/bitcheck.py.
Markers: ARM_XENV ... FLOWCUT=1 R_CUT=6.5 COS_MAX=0.8 RELINK=<0|1> (cell 0); ARM_FLOWFIX enabled=... cut=... (cell 5).
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_t6r70ff import HELPER, CALL, C5_DEF_ANCHOR, NL  # noqa: E402
from build_t6stk3ff import BASE, BASE_MD5, C5_CALL_ANCHOR, C5_STATS_ANCHOR, SK  # noqa: E402

CUT_FN = r'''

def _ff_cut(t, pos, E, F, cfg, ccfg):
    """ARM_FLOWCUT (Track B X1; offline twin wf17 trackB ext.py flowcut()): in acted windows (|f| >= TF, >= MIN_DET
    written nodes) drop the edge of every total-out-degree-1 source whose edge goes to t+1 when its flow residual is
    >= R_CUT um and cos(d, f) < COS_MAX. Returns (edges, n_cut)."""
    E = np.asarray(E, np.int64).reshape(-1, 2)
    if len(E) == 0:
        return E, 0
    P = pos * _FF_SC
    cnt = _ff_dd(int)
    for tt, p in zip(t, pos):
        cnt[(int(tt),) + _ff_win_of(p)] += 1
    outd = np.bincount(E[:, 0], minlength=len(t))
    keep = np.ones(len(E), bool)
    for k, (a, b) in enumerate(E):
        a, b = int(a), int(b)
        if outd[a] != 1 or t[b] != t[a] + 1:
            continue
        w = (int(t[a]),) + _ff_win_of(pos[a])
        if w not in F:
            continue
        f = np.asarray(F[w][0], float)
        if np.linalg.norm(f) < cfg["TF"] or cnt[w] < cfg["MIN_DET"]:
            continue
        d = P[b] - P[a]
        if np.linalg.norm(d - f) < ccfg["R_CUT"]:
            continue
        nd = np.linalg.norm(d)
        cos = float(np.dot(d, f) / (nd * np.linalg.norm(f))) if nd > 0 else 0.0
        if cos >= ccfg["COS_MAX"]:
            continue
        keep[k] = False
    return E[keep], int((~keep).sum())
'''

# (old, new) exact replacements on the t6stk3ff helper; each old string must occur exactly once
DELTA = [
    ('FLOWFIX_CFG = dict(TF=5.0, KEEP=3.5, GATE=4.5, MIN_DET=5, ENDS=True)\n',
     'FLOWFIX_CFG = dict(TF=5.0, KEEP=3.5, GATE=4.5, MIN_DET=5, ENDS=True)\n'
     'FLOWCUT_CFG = dict(R_CUT=6.5, COS_MAX=0.8, RELINK=os.environ.get("BIOHUB_FLOWCUT_RELINK", "1") == "1")  # ARM_FLOWCUT\n'),
    ('    return E[keep], changed, bridged, len(E) - len(keep)\n',
     '    return E[keep], changed, bridged, len(E) - len(keep)\n' + CUT_FN),
    ('             "flowfix_changed": 0, "flowfix_bridged": 0, "flowfix_dups": 0, "flowfix_secs": 0.0}\n',
     '             "flowfix_changed": 0, "flowfix_bridged": 0, "flowfix_dups": 0, "flowfix_secs": 0.0,\n'
     '             "flowfix_cut": 0, "flowfix_changed2": 0, "flowfix_bridged2": 0}\n'),
    ('        E2, changed, bridged, dups = _ff_repair(t, pos, e, F, FLOWFIX_CFG)\n',
     '        E2, changed, bridged, dups = _ff_repair(t, pos, e, F, FLOWFIX_CFG)\n'
     '        E2, n_cut = _ff_cut(t, pos, E2, F, FLOWFIX_CFG, FLOWCUT_CFG)  # ARM_FLOWCUT (X1)\n'
     '        changed2 = bridged2 = 0\n'
     '        if FLOWCUT_CFG["RELINK"]:  # X2: second CFG0 pass on the cut graph\n'
     '            E2, changed2, bridged2, dups2 = _ff_repair(t, pos, E2, F, FLOWFIX_CFG)\n'
     '            dups += dups2\n'),
    ('        if np.any((dout != 0) & ~((out0 == 0) & (out1 == 1))):\n',
     '        if np.any((dout != 0) & ~(((out0 == 0) & (out1 == 1)) | ((out0 == 1) & (out1 == 0)))):  # cut allowed\n'),
    ('        stats.update(flowfix_changed=int(changed), flowfix_bridged=int(bridged), flowfix_dups=int(dups),\n',
     '        stats.update(flowfix_cut=int(n_cut), flowfix_changed2=int(changed2), flowfix_bridged2=int(bridged2))\n'
     '        stats.update(flowfix_changed=int(changed), flowfix_bridged=int(bridged), flowfix_dups=int(dups),\n'),
    ('              f" acted={stats[\'flowfix_acted\']} changed={changed} bridged={bridged} dups={dups}"\n',
     '              f" acted={stats[\'flowfix_acted\']} changed={changed} bridged={bridged} dups={dups}"\n'
     '              f" cut={n_cut} changed2={changed2} bridged2={bridged2}"\n'),
    ('      f" threads={FLOWFIX_THREADS} deadline_s={FLOWFIX_DEADLINE_S:.0f}", flush=True)\n',
     '      f" threads={FLOWFIX_THREADS} deadline_s={FLOWFIX_DEADLINE_S:.0f}"\n'
     '      f" FLOWCUT R_CUT={FLOWCUT_CFG[\'R_CUT\']} COS_MAX={FLOWCUT_CFG[\'COS_MAX\']}"\n'
     '      f" RELINK={int(FLOWCUT_CFG[\'RELINK\'])}", flush=True)\n'),
]


def helper2():
    h = HELPER
    for old, new in DELTA:
        if h.count(old) != 1:
            raise SystemExit("helper anchor matched %d times: %r" % (h.count(old), old[:80]))
        h = h.replace(old, new, 1)
    return h


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    x1 = "--x1" in sys.argv
    tag = args[0] if args else ("t6stk3fc" if x1 else "t6stk3ff2")
    relink = "0" if x1 else "1"
    H2 = helper2()
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t6stk3/kernel.ipynb changed since the box bit check (md5 mismatch)")
    nb = json.loads(raw.decode("utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    orig = list(cells)
    c0, c5 = cells[0], cells[5]
    for name, a in (("c5_def", C5_DEF_ANCHOR), ("c5_call", C5_CALL_ANCHOR), ("c5_stats", C5_STATS_ANCHOR)):
        if c5.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c5.count(a)))
    for bad in ("ARM_FLOWFIX", "ARM_FLOWCUT", "BIOHUB_FLOWFIX", "flow_repair", "rawlink_override", "BIOHUB_RAWLINK_MIN_PROB"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %s" % bad)
    c5 = c5.replace(C5_DEF_ANCHOR, C5_DEF_ANCHOR.replace("\ndef write_test_submission", H2 + "\ndef write_test_submission"), 1)
    c5 = c5.replace(C5_CALL_ANCHOR, C5_CALL_ANCHOR.replace("\n\n            for node_id in sorted(nodes_by_id):\n",
                                                           "\n\n" + CALL + "\n            for node_id in sorted(nodes_by_id):\n"), 1)
    c5 = c5.replace(C5_STATS_ANCHOR, "                **filter_stats,\n                **flowfix_stats,\n            })\n", 1)
    c0 = (c0.rstrip(NL) + NL
          + "import time as _ff_time0" + NL
          + "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX deadline clock" + NL
          + "os.environ['BIOHUB_FLOWFIX'] = '1'" + NL
          + "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'" + NL
          + "os.environ['BIOHUB_FLOWCUT_RELINK'] = '%s'" % relink + NL
          + ('print("ARM_XENV tag=%s FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200'
             ' FLOWCUT=1 R_CUT=6.5 COS_MAX=0.8 RELINK=%s", flush=True)' % (tag, relink)) + NL)
    cells[0], cells[5] = c0, c5
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i not in (0, 5) and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    if c5.replace(H2, "").replace(CALL + "\n", "").replace("                **flowfix_stats,\n", "") != orig[5]:
        raise SystemExit("cell 5 differs from t6stk3's by more than the three ARM_FLOWFIX insertions")
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    k = 0
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["source"] = cells[k].splitlines(keepends=True)
            c["outputs"] = []
            c["execution_count"] = None
        k += 1
    dest = SK / ("v_" + tag)
    dest.mkdir(parents=True, exist_ok=True)
    json.dump(nb, open(dest / "kernel.ipynb", "w", encoding="utf-8"))
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest, "| base v_t6stk3 (md5 %s) | IMGFLOW CFG0 + FLOWCUT R_CUT 6.5 COS_MAX 0.8 RELINK %s" % (BASE_MD5, relink))
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
