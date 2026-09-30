#!/usr/bin/env python3
"""Add a gate entry + plan for t6r70T15 (scratch_kernels/build_t6r70T.py: t6r70 + SV softmax temperature T, gain g).

usage: python ops/add_r70T_gate.py [tag] [T] [gain]      (defaults: t6r70T15 1.5 2.00)

Derived from t6r70's own `need` entry (read out of ops/gate.py with ast, not retyped) plus the two t6svT markers,
pins the four per-movie SV_ARM_HSG200 lines to t6svT15's (same detector, same logits, same T -> bit-identical),
adds the tag to the rawlink structural checks (RL_TAGS + the orphan cap) and to sv_mark (before sv_tags is computed),
an allowlist-style forbid (no ARM_<X> outside STK3V/STK3B/T60H/LCEFR/RAWLINK/XENV/SVTEMP), and a per-movie
bookkeeping cross-check (cell-10 written nodes/edges/divisions == FINAL nodes / ARM_RAWLINK final= / safe divisions,
run_stats agrees, line-fit smoothed + skipped == nodes). The T6_BODY exact topology pins are NOT applied: the SV change
moves coordinates and therefore the graph.
gate.py is backed up first; negative tests: the t6r70 log AND the t6svT15 log must both FAIL under the new tag, the
t6r70-log failure must not come from the bookkeeping block (it is a valid rawlink log), and t6r70 / t6svT15 / t6stk3
must still PASS under their own tags. Any miss restores the backup.
"""
import ast
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATE = ROOT / "ops" / "gate.py"
SV_T15 = [  # t6svT15's visible-run SV_ARM_HSG200 lines (data/out_t6svT15), one per movie
    (26532, "0.2511", "0.2822"), (33336, "0.2959", "0.2901"), (7370, "0.3075", "0.3206"), (76396, "0.2917", "0.3075")]


def esc(s):
    return s.replace(".", "\\.")


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
    tag = sys.argv[1] if len(sys.argv) > 1 else "t6r70T15"
    T = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    g = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    gs = "%.2f" % g
    t = GATE.read_text(encoding="utf-8")
    if "'%s'" % tag in t or '"%s"' % tag in t:
        raise SystemExit("gate entry for %s already exists" % tag)
    base = need_of(t, "t6r70")
    pats = list(base) + [
        "ARM_XENV tag=%s SVTEMP=%s GAIN=%s LCEFR=kept" % (tag, esc(repr(T)), esc(gs)),
        "ARM_SVTEMP T=%s gain=%s " % (esc(repr(T)), esc(gs)),
        "SUBVOXEL patch applied to",
    ]
    if (T, g) == (1.5, 2.0):
        pats += [r"SV_ARM_HSG200 nodes=%d mean_abs_off_vox=%s frac_clipped=%s gain=2\.00" % (n, esc(m), esc(f))
                 for n, m, f in SV_T15]
    else:
        pats += [r"SV_ARM_HSG200 nodes=\d+ mean_abs_off_vox=0\.\d+ frac_clipped=0\.\d+ gain=" + esc(gs)]
    entry = ("        # --- %s: t6r70 (0.954 body + raw-ILP override 0.70) with the sub-voxel softmax at temperature %s,\n"
             "        # gain %s (build_t6r70T.py; ops/add_r70T_gate.py). t6r70's markers + the t6svT markers + SV lines pinned\n"
             "        # to t6svT15's (same detector and logits).\n" % (tag, repr(T), gs)
             + "        '%s': [\n" % tag + "".join("            %r,\n" % p for p in pats) + "        ],\n")
    anchors = {
        "need": "        't6dl': [\n",
        "forbid": 'forbid["t6dl"] = [',
        "tol": '"t6svT15": 0.15',
        "rl": 'RL_TAGS = {"rawlink70", "t6r70", "t6rlf"}',
        "iso": 'if {"t6r70", "t6rlf"} & set(tags):',
        "svtags": 'sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n',
    }
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    t = t.replace(anchors["need"], entry + anchors["need"], 1)
    forbid = [r"V1284", r"ARM_SV_ZONLY", r"ARM_SV_YXONLY", r"ARM_SV_AXES", r"ARM_SVZEST", r"SUBVOXEL anchor",
              r"SUBVOXEL offset/coord length mismatch", r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_LCEFR NO-OP",
              r"IndentationError", r"Traceback \(most recent call last\)",
              r"ARM_XENV tag=(?!%s )" % tag,
              r"\bARM_(?!(?:STK3V|STK3B|T60H|LCEFR|RAWLINK|XENV|SVTEMP)\b)[A-Z0-9]+",
              r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", r"GDIV_DS", r"SUBVOXEL_ACTIVE",
              r'"output_linefit_strict_linear": true']
    if T != 1.0:  # the T=1 (t6stk3/t6r70) SV signature: the temperature never reached the helper
        forbid.append(r"SV_ARM_HSG200 nodes=\d+ mean_abs_off_vox=0\.(?:2069|2827|2913|2607) ")
    t = t.replace(anchors["forbid"], "forbid[%r] = %r\n" % (tag, forbid) + anchors["forbid"], 1)
    t = t.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % tag, 1)
    t = t.replace(anchors["rl"], 'RL_TAGS = {"rawlink70", "t6r70", "t6rlf", "%s"}' % tag, 1)
    t = t.replace(anchors["iso"], 'if {"t6r70", "t6rlf", "%s"} & set(tags):' % tag, 1)
    block = '''# --- %(tag)s (ops/add_r70T_gate.py): t6r70 + SV softmax temperature. The SV change moves node coordinates and so
# the graph, which is why the T6_BODY exact topology pins do NOT apply. Instead the override's bookkeeping is
# cross-checked per movie against this run's own prints: cell-10 written nodes/edges/divisions must equal
# (FINAL nodes, ARM_RAWLINK final=, safe divisions added), run_stats must agree, and line-fit smoothed + skipped
# must equal nodes. sv_mark is set here, BEFORE sv_tags is computed, so the >= 4 SV lines check runs for it.
sv_mark["%(tag)s"] = "SV_ARM_HSG200"
if "%(tag)s" in tags:
    import csv, os
    _fin, _sd, _dv, _rlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\\[(\\w+)\\] FINAL: (\\d+) nodes, (\\d+) edges", txt):
        _fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\\[(\\w+)\\] after safe-division repair: \\d+ nodes, \\d+ edges \\([^)]*?\\badded=(\\d+)", txt):
        _sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\\s+(\\w+): nodes=(\\d+) edges=(\\d+) divisions=(\\d+)\\s*$", txt):
        _dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \\[(\\w+)\\] .*? final=(\\d+) ", txt):
        _rlf.setdefault(d, int(f_))
    _rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _rs = None
    if os.path.isfile(_rsp):
        with open(_rsp, newline="", encoding="utf-8") as fh:
            _rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("%(tag)s: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _fin or d not in _sd or d not in _rlf:
            fails.append(f"%(tag)s {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _want = (_fin[d][0], _rlf[d], _sd[d])
        if _dv.get(d) != _want:
            fails.append(f"%(tag)s {d} written nodes/edges/divisions {_dv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_want}")
        if _rs is not None:
            _r = _rs.get(d) or {}
            try:
                _got = tuple(int(float(_r[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                         "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got is None or _got[:3] != _want or _got[3] + _got[4] != _want[0]:
                fails.append(f"%(tag)s {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_got} "
                             f"inconsistent with {_want} (smoothed + skipped must equal nodes)")
''' % {"tag": tag}
    t = t.replace(anchors["svtags"], block + anchors["svtags"], 1)
    ast.parse(t)
    compile(t, str(GATE), "exec")
    bak = GATE.with_name("gate.py.bak_" + tag)
    bak.write_text(GATE.read_text(encoding="utf-8"), encoding="utf-8")
    GATE.write_text(t, encoding="utf-8")
    desc = ("%s: our 0.954 t6r70 body (t6stk3 + raw-ILP override at prob 0.70) with the sub-voxel 3x3x3 softmax at "
            "temperature %s (gain %s, clip 0.4999; lcefr, linker and rawlink unchanged). Softening the softmax cuts the "
            "share of annotated links with a frame-to-frame displacement error above 2.5/3 um on both embryos of 60 "
            "train movies (production logits, movie bootstrap)." % (tag, repr(T), gs))
    json.dump([{"tag": tag, "desc": desc}], open(ROOT / "ops" / ("plan_%s.json" % tag), "w"), indent=1)
    res = {"neg_t6r70": gate("out_t6r70", tag), "neg_t6svT15": gate("out_t6svT15", tag),
           "reg_t6r70": gate("out_t6r70", "t6r70"), "reg_t6svT15": gate("out_t6svT15", "t6svT15"),
           "reg_t6stk3": gate("out_t6stk3", "t6stk3")}
    for k, v in res.items():
        print(k, "|", v[:600])
    ok = ("GATE_FAIL" in res["neg_t6r70"] and "GATE_FAIL" in res["neg_t6svT15"]
          and "written nodes/edges/divisions" not in res["neg_t6r70"] and "run_stats (nodes" not in res["neg_t6r70"]
          and "missing FINAL / safe-division" not in res["neg_t6r70"]
          and all(res[k] == "GATE_PASS" for k in ("reg_t6r70", "reg_t6svT15", "reg_t6stk3")))
    if not ok:
        GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit("NEGATIVE/REGRESSION TEST FAILED - gate.py restored from " + str(bak))
    print("gate entry + plan written for", tag, "| backup", bak.name, "| negative + regression tests OK")


if __name__ == "__main__":
    main()
