#!/usr/bin/env python3
"""Gate entry for t65s3ff (scratch_kernels/build_t65s3ff.py) = t65s3 (pick B, relink TIGHT 6.5) + IMGFLOW repair.
Run from the project root: it backs up ops/gate.py (gate.py.bak_t65s3ff), patches it, self-tests, and restores the
backup if any self-test fails. Dry run: T65S3FF_GATE=<copy of gate.py> python ops/add_t65s3ff_gate.py

t65s3ff must prove on the visible run (4 movies):
  * need['t65s3'] (read out of gate.py with ast: STK3V/STK3B/T65H/LCEFR markers + the 6.5 echo + line-fit echoes) and
    sv_mark (>= 4 SV_ARM_HSG200 lines before 'Prediction completed');
  * cell-0 ARM_XENV tag=t65s3ff FLOWFIX=1 ... and the cell-5 'ARM_FLOWFIX enabled=True ...' line;
  * per movie: FINAL nodes/edges, safe divisions and run_stats motion_relink_tight_edges EXACTLY the real t65s3
    visible run's (T65S3_BODY, data/out_t65s3): the repair runs after FINAL, so the pre-repair graph must be t65s3's;
    one 'ARM_FLOWFIX [<movie>] status=ok' line after FINAL with edges=A->B, A == FINAL edges, B == A + bridged - dups,
    divs X->X, max_in <= 1, secs <= 20; cell-10 written (nodes, edges, divisions) == (FINAL nodes, B, safe divisions);
    run_stats (nodes, edges) == (FINAL nodes, B);
  * changed > 0 on at least one visible movie; no FALLBACK / SKIPPED / enabled=False / traceback / foreign ARM_ marker /
    6.0 relink echo (that would be t6stk3ff wearing this name).
Self-tests: t65s3 and t6stk3ff logs must FAIL as t65s3ff; t65s3 / t6stk3 / t6r70 / t6stk3ff logs still PASS as themselves.
"""
import ast
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(os.environ.get("T65S3FF_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T65S3FF_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t65s3ff"
VIS = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
# real t65s3 visible run (data/out_t65s3, pick B 56496604): FINAL nodes, FINAL edges, safe divisions added,
# run_stats motion_relink_tight_edges
T65S3_BODY = {"44b6_0113de3b": (25620, 24883, 34, 24616), "44b6_0b24845f": (20678, 19401, 13, 19921),
              "6bba_05b6850b": (6150, 5954, 5, 5911), "6bba_05db0fb1": (70415, 68288, 26, 67052)}


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
    pats = list(need_of(t, "t65s3")) + [
        r"ARM_XENV tag=t65s3ff FLOWFIX=1 TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200",
        r"ARM_FLOWFIX enabled=True TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 threads=\d+ deadline_s=34200",
    ] + [r"ARM_FLOWFIX \[%s\] status=ok windows=\d+ flagged=\d+ acted=\d+ changed=\d+ " % d for d in VIS]
    entry = ("        # --- t65s3ff: pick B t65s3 (relink tight 6.5) + IMGFLOW write-time repair (image phase-correlation\n"
             "        # flow-compensated re-assignment + track-end bridging in |f| >= 5 um windows) right after\n"
             "        # filter_output_graph; nodes and forks untouched (build_t65s3ff.py; ops/add_t65s3ff_gate.py).\n"
             "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n")
    forbid = [r"ARM_FLOWFIX \[\w+\] (?:FALLBACK|SKIPPED)", r"ARM_FLOWFIX enabled=False",
              r"Traceback \(most recent call last\)", r"IndentationError", r"ARM_XENV tag=(?!t65s3ff )",
              r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|FLOWFIX)\b)[A-Z0-9]+", r"ARM_RAWLINK",
              r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", r"GDIV_DS", r"SUBVOXEL_ACTIVE", r'"output_linefit_strict_linear": true',
              r'"motion_relink_tight_um": 6\.0(?!\d)']
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "unknown": "unknown = [t for t in tags if t not in need and t not in sv_mark"}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    t = t.replace(anchors["need"], entry + anchors["need"], 1)
    t = t.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t = t.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    block = '''# --- %(tag)s (ops/add_t65s3ff_gate.py): t65s3 + ARM_FLOWFIX after filter_output_graph. The pre-repair graph must
# be the real t65s3 run's exactly (FINAL, safe divisions, motion_relink_tight_edges); written = FINAL + bridged - dups.
if "%(tag)s" in tags:
    import csv, os
    T65S3_BODY = %(body)r
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
    _chg = []
    for d, (n0, e0, s0, k0) in sorted(T65S3_BODY.items()):
        if _fin.get(d) != (n0, e0) or _sd.get(d) != s0:
            fails.append(f"%(tag)s {d}: FINAL {_fin.get(d)} / safe divisions {_sd.get(d)} != the real t65s3 run's "
                         f"{(n0, e0)} / {s0}: the repair runs after FINAL, so the pre-repair graph must be t65s3's")
        _m = re.search(r"ARM_FLOWFIX \\[%%s\\] status=ok windows=(\\d+) flagged=(\\d+) acted=(\\d+) changed=(\\d+) "
                       r"bridged=(\\d+) dups=(\\d+) edges=(\\d+)->(\\d+) divs=(\\d+)->(\\d+) max_in=(\\d+) secs=([\\d.]+) " %% d, txt)
        if not _m:
            fails.append(f"%(tag)s {d}: no ARM_FLOWFIX status=ok line")
            continue
        _w, _fl, _ac, _ch, _br, _du, _a0, _a1, _v0, _v1, _mi = (int(v) for v in _m.groups()[:11])
        _chg.append(_ch)
        if txt.find(f"[{d}] FINAL:") < 0 or _m.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"%(tag)s {d}: ARM_FLOWFIX line is not after the movie's FINAL line")
        if _a0 != e0 or _a1 != _a0 + _br - _du:
            fails.append(f"%(tag)s {d}: flowfix edges {_a0}->{_a1} inconsistent with FINAL {e0} + {_br} - {_du}")
        if _v0 != _v1 or _v1 != s0 or _mi > 1:
            fails.append(f"%(tag)s {d}: flowfix divisions {_v0}->{_v1} (want {s0}) or in-degree {_mi}")
        if float(_m.group(12)) > 20.0:
            fails.append(f"%(tag)s {d}: flowfix {_m.group(12)} s > 20 s/movie (hidden overhead > ~66 min)")
        if _dv.get(d) != (n0, _a1, s0):
            fails.append(f"%(tag)s {d}: written nodes/edges/divisions {_dv.get(d)} != {(n0, _a1, s0)}")
        if _rs is not None:
            try:
                _got = tuple(int(float((_rs.get(d) or {})[k])) for k in ("nodes", "edges", "motion_relink_tight_edges"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got != (n0, _a1, k0):
                fails.append(f"%(tag)s {d}: run_stats (nodes, edges, motion_relink_tight_edges) {_got} != {(n0, _a1, k0)}"
                             " (tight edges must be the real t65s3 run's: a 6.0 gate gives fewer)")
    if not _chg or max(_chg) == 0:
        fails.append("%(tag)s: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
''' % {"tag": TAG, "body": T65S3_BODY}
    t = t.replace(anchors["unknown"], block + anchors["unknown"], 1)
    ast.parse(t)
    compile(t, str(GATE), "exec")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(GATE.read_text(encoding="utf-8"), encoding="utf-8")
    GATE.write_text(t, encoding="utf-8")
    res = {"neg_t65s3_as_t65s3ff": gate("out_t65s3", TAG), "neg_t6stk3ff_as_t65s3ff": gate("out_t6stk3ff", TAG),
           "pos_t65s3": gate("out_t65s3", "t65s3"), "pos_t6stk3": gate("out_t6stk3", "t6stk3"),
           "pos_t6r70": gate("out_t6r70", "t6r70"), "pos_t6stk3ff": gate("out_t6stk3ff", "t6stk3ff")}
    if list((ROOT / "data").glob("out_%s/*.log" % TAG)):
        res["pos_t65s3ff"] = gate("out_" + TAG, TAG)
    print({k: v[:300] for k, v in res.items()})
    ok = all("GATE_FAIL" in v for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_") and k != "pos_t65s3ff")
    if not ok:
        GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit("self-test failed; gate.py restored from " + bak.name)
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
