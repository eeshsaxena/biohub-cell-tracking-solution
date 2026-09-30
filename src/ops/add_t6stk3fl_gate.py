#!/usr/bin/env python3
"""Gate entry for t6stk3fl (scratch_kernels/build_t6stk3fl.py = t6stk3ff + FLOWLINK: the IMGFLOW flow used inside the
cell-5 motion relink for sources in flagged windows; wf18 PREREG). Run from the project root; backs up ops/gate.py to
ops/gate.py.bak_t6stk3fl and restores it if the self-test fails.

t6stk3fl moves topology (the relink re-routes edges in high-motion windows), so it is NOT pinned to T6_BODY; instead the
visible run must reproduce the box c5 replay of the SAME kernel (wf18 batch/results/t6stk3fl, vis_pins.json) exactly:
  * need['t6stk3'] markers (read with ast) + sv_mark (>= 4 SV_ARM_HSG200 lines);
  * cell-0 ARM_XENV tag=t6stk3fl FLOWLINK=1 ... FLOWFIX=1 ...; cell-5 'ARM_FLOWFIX enabled=True' and
    'ARM_FLOWLINK enabled=True ... gate=relink(tight 6.0, relaxed 10.0)' lines;
  * per movie: ARM_FLOWLINK status=ok with the pinned flow digest (the flow is bit-identical to the box estimator) and
    flagged windows; relink flagged_sources pinned; FINAL nodes/edges and safe divisions pinned; the ARM_FLOWFIX line
    after FINAL with edges A->B, A == FINAL edges, B == A + bridged - dups, divs X->X, max_in <= 1, secs <= 20;
    written (nodes, edges, divisions) == (FINAL nodes, B, safe divisions); run_stats (nodes, edges, tight edges) pinned;
  * flagged_sources > 0 on at least one visible movie; no FALLBACK / SKIPPED / enabled=False / traceback / foreign ARM_.
Negatives: the t6stk3ff and t6stk3 visible logs must FAIL as t6stk3fl; regressions t6stk3ff / t6stk3 / t6r70 PASS.
"""
import ast
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(os.environ.get("T6STK3FL_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T6STK3FL_GATE", ROOT / "ops" / "gate.py"))
TAG = "t6stk3fl"
PINS = json.loads(r'''{"44b6_0113de3b": {"ff": {"bridged": 0, "changed": 0, "divs": 37, "dups": 0, "e0": 24984, "e1": 24984}, "final": [25662, 24984], "fl_digest": "02c949517869", "fl_flagged_sources": 1114, "fl_flagged_windows": 62, "fl_windows": 792, "run_stats": [25662, 24984, 24915, 1114], "safe_divs": 37, "written": [25662, 24984, 37]}, "44b6_0b24845f": {"ff": {"bridged": 0, "changed": 1, "divs": 13, "dups": 0, "e0": 19414, "e1": 19414}, "final": [20691, 19414], "fl_digest": "dba8c6ba1449", "fl_flagged_sources": 470, "fl_flagged_windows": 27, "fl_windows": 792, "run_stats": [20691, 19414, 19812, 470], "safe_divs": 13, "written": [20691, 19414, 13]}, "6bba_05b6850b": {"ff": {"bridged": 0, "changed": 0, "divs": 6, "dups": 0, "e0": 5930, "e1": 5930}, "final": [6135, 5930], "fl_digest": "840f12b2e578", "fl_flagged_sources": 305, "fl_flagged_windows": 36, "fl_windows": 792, "run_stats": [6135, 5930, 5869, 305], "safe_divs": 6, "written": [6135, 5930, 6]}, "6bba_05db0fb1": {"ff": {"bridged": 1, "changed": 14, "divs": 19, "dups": 0, "e0": 68249, "e1": 68250}, "final": [70365, 68249], "fl_digest": "40a63a3c0ae1", "fl_flagged_sources": 4138, "fl_flagged_windows": 47, "fl_windows": 792, "run_stats": [70365, 68250, 67434, 4138], "safe_divs": 19, "written": [70365, 68250, 19]}}''')


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def gate(logdir, tag):
    lg = str(next((ROOT / "data" / logdir).glob("*.log")))
    out = subprocess.run([sys.executable, str(GATE), lg, tag], capture_output=True, text=True).stdout.strip()
    return out.splitlines()[-1] if out else "NO OUTPUT"


def main():
    t = GATE.read_text(encoding="utf-8")
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    pats = list(need_of(t, "t6stk3")) + [
        r"ARM_XENV tag=t6stk3fl FLOWLINK=1 FL_TF=5\.0 FL_MIN_DET=5 FLOWFIX=1 TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200",
        r"ARM_FLOWFIX enabled=True TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 threads=\d+ deadline_s=34200",
        r"ARM_FLOWLINK enabled=True TF=5\.0 MIN_DET=5 MODE=flow gate=relink\(tight 6\.0, relaxed 10\.0\)",
    ] + [r"ARM_FLOWLINK \[%s\] status=ok windows=%d flagged_windows=%d digest=%s " % (
        d, p["fl_windows"], p["fl_flagged_windows"], p["fl_digest"]) for d, p in sorted(PINS.items())] \
      + [r"ARM_FLOWLINK \[%s\] relink flagged_sources=%d\b" % (d, p["fl_flagged_sources"]) for d, p in sorted(PINS.items())]
    entry = ("        # --- t6stk3fl: t6stk3ff + FLOWLINK (IMGFLOW flow inside the cell-5 motion relink for sources in\n"
             "        # windows with |f| >= 5 um and >= 5 nodes; build_t6stk3fl.py; ops/add_t6stk3fl_gate.py).\n"
             "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n")
    forbid = [r"ARM_FLOWFIX \[\w+\] (?:FALLBACK|SKIPPED)", r"ARM_FLOWLINK \[\w+\] (?:FALLBACK|SKIPPED)",
              r"ARM_FLOWFIX enabled=False", r"ARM_FLOWLINK enabled=False",
              r"Traceback \(most recent call last\)", r"IndentationError", r"ARM_XENV tag=(?!t6stk3fl )",
              r"\bARM_(?!(?:STK3V|STK3B|T60H|LCEFR|XENV|FLOWFIX|FLOWLINK)\b)[A-Z0-9]+", r"ARM_RAWLINK", r"ARM_FLOWCUT",
              r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", r"GDIV_DS", r"SUBVOXEL_ACTIVE", r'"output_linefit_strict_linear": true']
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "unknown": "unknown = [t for t in tags if t not in need and t not in sv_mark"}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    t = t.replace(anchors["need"], entry + anchors["need"], 1)
    t = t.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t = t.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    body = {d: (p["final"][0], p["final"][1], p["safe_divs"], p["run_stats"][2]) for d, p in PINS.items()}
    block = '''# --- %(tag)s (ops/add_t6stk3fl_gate.py): t6stk3ff + ARM_FLOWLINK (flow inside the cell-5 relink). Topology moves,
# so the pins are the box c5 replay of the SAME kernel (wf18 vis_pins.json), not T6_BODY.
if "%(tag)s" in tags:
    import csv, os
    T6FL_BODY = %(body)r
    _fin, _sd, _dv = {}, {}, {}
    for d, n_, e_ in re.findall(r"\\[(\\w+)\\] FINAL: (\\d+) nodes, (\\d+) edges", txt):
        _fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\\[(\\w+)\\] after safe-division repair: \\d+ nodes, \\d+ edges \\([^)]*?\\badded=(\\d+)", txt):
        _sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\\s+(\\w+): nodes=(\\d+) edges=(\\d+) divisions=(\\d+)\\s*$", txt):
        _dv.setdefault(d, (int(n_), int(e_), int(v_)))
    _rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _rs = None
    if os.path.isfile(_rsp):
        with open(_rsp, newline="", encoding="utf-8") as fh:
            _rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("%(tag)s: no run_stats.csv beside the log")
    _flg = []
    for d, (n0, e0, s0, k0) in sorted(T6FL_BODY.items()):
        if _fin.get(d) != (n0, e0) or _sd.get(d) != s0:
            fails.append(f"%(tag)s {d}: FINAL {_fin.get(d)} / safe divisions {_sd.get(d)} != the box replay of this "
                         f"kernel {(n0, e0)} / {s0}")
        _l = re.search(r"ARM_FLOWLINK \\[%%s\\] relink flagged_sources=(\\d+)" %% d, txt)
        _flg.append(int(_l.group(1)) if _l else 0)
        _m = re.search(r"ARM_FLOWFIX \\[%%s\\] status=ok windows=(\\d+) flagged=(\\d+) acted=(\\d+) changed=(\\d+) "
                       r"bridged=(\\d+) dups=(\\d+) edges=(\\d+)->(\\d+) divs=(\\d+)->(\\d+) max_in=(\\d+) secs=([\\d.]+) " %% d, txt)
        if not _m:
            fails.append(f"%(tag)s {d}: no ARM_FLOWFIX status=ok line")
            continue
        _w, _fl, _ac, _ch, _br, _du, _a0, _a1, _v0, _v1, _mi = (int(v) for v in _m.groups()[:11])
        if txt.find(f"[{d}] FINAL:") < 0 or _m.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"%(tag)s {d}: ARM_FLOWFIX line is not after the movie's FINAL line")
        if _a0 != e0 or _a1 != _a0 + _br - _du:
            fails.append(f"%(tag)s {d}: flowfix edges {_a0}->{_a1} inconsistent with FINAL {e0} + {_br} - {_du}")
        if _v0 != _v1 or _v1 != s0 or _mi > 1:
            fails.append(f"%(tag)s {d}: flowfix divisions {_v0}->{_v1} (want {s0}) or in-degree {_mi}")
        if float(_m.group(12)) > 20.0:
            fails.append(f"%(tag)s {d}: flowfix {_m.group(12)} s > 20 s/movie")
        if _dv.get(d) != (n0, _a1, s0):
            fails.append(f"%(tag)s {d}: written nodes/edges/divisions {_dv.get(d)} != {(n0, _a1, s0)}")
        if _rs is not None:
            try:
                _got = tuple(int(float((_rs.get(d) or {})[k])) for k in ("nodes", "edges", "motion_relink_tight_edges"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got != (n0, _a1, k0):
                fails.append(f"%(tag)s {d}: run_stats (nodes, edges, motion_relink_tight_edges) {_got} != {(n0, _a1, k0)}")
    if not _flg or max(_flg) == 0:
        fails.append("%(tag)s: FLOWLINK flagged 0 relink sources on every visible movie: the linker flow never fired")
''' % {"tag": TAG, "body": body}
    t = t.replace(anchors["unknown"], block + anchors["unknown"], 1)
    ast.parse(t)
    compile(t, str(GATE), "exec")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(GATE.read_text(encoding="utf-8"), encoding="utf-8")
    GATE.write_text(t, encoding="utf-8")
    res = {"neg_t6stk3ff_as_t6stk3fl": gate("out_t6stk3ff", TAG), "neg_t6stk3_as_t6stk3fl": gate("out_t6stk3", TAG),
           "pos_t6stk3ff": gate("out_t6stk3ff", "t6stk3ff"), "pos_t6stk3": gate("out_t6stk3", "t6stk3"),
           "pos_t6r70": gate("out_t6r70", "t6r70")}
    print({k: v[:300] for k, v in res.items()})
    if "GATE_FAIL" not in res["neg_t6stk3ff_as_t6stk3fl"] or "GATE_FAIL" not in res["neg_t6stk3_as_t6stk3fl"] \
            or "GATE_PASS" not in res["pos_t6stk3ff"] or "GATE_PASS" not in res["pos_t6stk3"] \
            or "GATE_PASS" not in res["pos_t6r70"]:
        GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit("self-test failed; gate.py restored from " + bak.name)
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
