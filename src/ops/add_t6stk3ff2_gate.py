#!/usr/bin/env python3
"""PROPOSED gate entry for t6stk3ff2 (scratch_kernels/build_t6stk3ff2.py = t6stk3ff + Track-B FLOWCUT+RELINK). NOT RUN
on ops/gate.py by the wf17 Track-B agent (dry-run only, on a copy). To install: copy to ops/add_t6stk3ff2_gate.py and run
from the project root; it backs up ops/gate.py and restores it if the self-test fails.
Derived from ops/add_t6stk3ff_gate.py. Differences: tag; XENV / enabled patterns carry the FLOWCUT fields; the per-movie
line carries cut/changed2/bridged2 and the written edges must be B = A + bridged + bridged2 - dups - cut; cut > 0 on at
least one visible movie; ARM_FLOWCUT allowed; negatives: the t6stk3ff AND t6stk3 visible logs must FAIL as t6stk3ff2.
(Text below is the t6stk3ff description; read "B == A + bridged + bridged2 - dups - cut".)

t6stk3ff must prove on the visible run (4 movies):
  * need['t6stk3'] (read out of gate.py with ast) + sv_mark (>= 4 SV_ARM_HSG200 lines before 'Prediction completed');
  * cell-0 ARM_XENV tag=t6stk3ff FLOWFIX=1 ... and the cell-5 'ARM_FLOWFIX enabled=True ...' line;
  * per movie: FINAL nodes/edges and safe divisions EXACTLY the 0.954 body's (T6_BODY): the repair runs after FINAL, so
    the pre-repair graph must be t6stk3's; one 'ARM_FLOWFIX [<movie>] status=ok' line after FINAL with edges=A->B,
    A == FINAL edges, B == A + bridged - dups, divs X->X, max_in <= 1, secs <= 20; cell-10 written (nodes, edges,
    divisions) == (FINAL nodes, B, safe divisions); run_stats (nodes, edges) == (FINAL nodes, B);
  * changed > 0 on at least one visible movie; no FALLBACK / SKIPPED / enabled=False / traceback / foreign ARM_ marker.
Negative test: the t6stk3 visible log (data/out_t6stk3) must FAIL as t6stk3ff and still PASS as t6stk3.
"""
import ast
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(os.environ.get("T6STK3FF2_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T6STK3FF2_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t6stk3ff2"
VIS = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")


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
        r"ARM_XENV tag=t6stk3ff2 FLOWFIX=1 TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200 FLOWCUT=1 R_CUT=6\.5 COS_MAX=0\.8 RELINK=1",
        r"ARM_FLOWFIX enabled=True TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 threads=\d+ deadline_s=34200 FLOWCUT R_CUT=6\.5 COS_MAX=0\.8 RELINK=1",
    ] + [r"ARM_FLOWFIX \[%s\] status=ok windows=\d+ flagged=\d+ acted=\d+ changed=\d+ bridged=\d+ dups=\d+ cut=\d+ changed2=\d+ " % d
         for d in VIS]
    entry = ("        # --- t6stk3ff2: t6stk3ff (0.954 t6stk3 body + IMGFLOW repair) + Track-B FLOWCUT+RELINK (drop flow-\n"
             "        # inconsistent edges in the acted windows, then a second repair pass); nodes and forks untouched\n"
             "        # (build_t6stk3ff2.py; ops/add_t6stk3ff2_gate.py).\n"
             "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n")
    forbid = [r"ARM_FLOWFIX \[\w+\] (?:FALLBACK|SKIPPED)", r"ARM_FLOWFIX enabled=False",
              r"Traceback \(most recent call last\)", r"IndentationError", r"ARM_XENV tag=(?!t6stk3ff2 )",
              r"\bARM_(?!(?:STK3V|STK3B|T60H|LCEFR|XENV|FLOWFIX|FLOWCUT)\b)[A-Z0-9]+", r"ARM_RAWLINK",
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
    block = '''# --- %(tag)s (ops/add_t6stk3ff2_gate.py): t6stk3 + ARM_FLOWFIX + FLOWCUT/RELINK after filter_output_graph. The
# pre-repair graph must be the 0.954 body's (T6_BODY pins); written edges = FINAL + bridged + bridged2 - dups - cut.
if "%(tag)s" in tags:
    import csv, os
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
    _chg, _cut = [], []
    for d, (n0, e0, s0) in sorted(T6_BODY.items()):
        if _fin.get(d) != (n0, e0) or _sd.get(d) != s0:
            fails.append(f"%(tag)s {d}: FINAL {_fin.get(d)} / safe divisions {_sd.get(d)} != the 0.954 body's "
                         f"{(n0, e0)} / {s0}: the repair runs after FINAL, so the pre-repair graph must be t6stk3's")
        _m = re.search(r"ARM_FLOWFIX \\[%%s\\] status=ok windows=(\\d+) flagged=(\\d+) acted=(\\d+) changed=(\\d+) "
                       r"bridged=(\\d+) dups=(\\d+) cut=(\\d+) changed2=(\\d+) bridged2=(\\d+) "
                       r"edges=(\\d+)->(\\d+) divs=(\\d+)->(\\d+) max_in=(\\d+) secs=([\\d.]+) " %% d, txt)
        if not _m:
            fails.append(f"%(tag)s {d}: no ARM_FLOWFIX status=ok line")
            continue
        _w, _fl, _ac, _ch, _br, _du, _cu, _ch2, _br2, _a0, _a1, _v0, _v1, _mi = (int(v) for v in _m.groups()[:14])
        _chg.append(_ch)
        _cut.append(_cu)
        if txt.find(f"[{d}] FINAL:") < 0 or _m.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"%(tag)s {d}: ARM_FLOWFIX line is not after the movie's FINAL line")
        if _a0 != e0 or _a1 != _a0 + _br + _br2 - _du - _cu:
            fails.append(f"%(tag)s {d}: flowfix edges {_a0}->{_a1} inconsistent with FINAL {e0} + {_br} + {_br2} - {_du} - {_cu}")
        if _v0 != _v1 or _v1 != s0 or _mi > 1:
            fails.append(f"%(tag)s {d}: flowfix divisions {_v0}->{_v1} (want {s0}) or in-degree {_mi}")
        if float(_m.group(15)) > 20.0:
            fails.append(f"%(tag)s {d}: flowfix {_m.group(15)} s > 20 s/movie (hidden overhead > ~66 min)")
        if _dv.get(d) != (n0, _a1, s0):
            fails.append(f"%(tag)s {d}: written nodes/edges/divisions {_dv.get(d)} != {(n0, _a1, s0)}")
        if _rs is not None:
            try:
                _got = tuple(int(float((_rs.get(d) or {})[k])) for k in ("nodes", "edges"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got != (n0, _a1):
                fails.append(f"%(tag)s {d}: run_stats (nodes, edges) {_got} != {(n0, _a1)}")
    if not _chg or max(_chg) == 0:
        fails.append("%(tag)s: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
    if not _cut or max(_cut) == 0:
        fails.append("%(tag)s: FLOWCUT cut 0 edges on every visible movie: the extension never fired")
''' % {"tag": TAG}
    t = t.replace(anchors["unknown"], block + anchors["unknown"], 1)
    ast.parse(t)
    compile(t, str(GATE), "exec")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(GATE.read_text(encoding="utf-8"), encoding="utf-8")
    GATE.write_text(t, encoding="utf-8")
    res = {"neg_t6stk3ff_as_t6stk3ff2": gate("out_t6stk3ff", TAG), "neg_t6stk3_as_t6stk3ff2": gate("out_t6stk3", TAG),
           "pos_t6stk3ff": gate("out_t6stk3ff", "t6stk3ff"), "pos_t6stk3": gate("out_t6stk3", "t6stk3"),
           "pos_t6r70": gate("out_t6r70", "t6r70")}
    print({k: v[:300] for k, v in res.items()})
    if "GATE_FAIL" not in res["neg_t6stk3ff_as_t6stk3ff2"] or "GATE_FAIL" not in res["neg_t6stk3_as_t6stk3ff2"] \
            or "GATE_PASS" not in res["pos_t6stk3ff"] or "GATE_PASS" not in res["pos_t6stk3"] \
            or "GATE_PASS" not in res["pos_t6r70"]:
        GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit("self-test failed; gate.py restored from " + bak.name)
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
