#!/usr/bin/env python3
r"""Gate entry for ourvzlb25r70 (scratch_kernels/build_ourvzlb25r70.py) = ourvzlb25 (V1284 y/x head + sub-voxel z to
the edge model, relink tight 6.5, learned bonus 2.5; board 0.954) plus t6r70's raw-ILP override "rawlink" at min_prob
0.70 (the step that turned t65b25 into t65b25r70). Run from the project root: it backs up ops/gate.py
(gate.py.bak_ourvzlb25r70), patches it, self-tests, and restores the backup if any self-test fails.
Dry run: OURVZLB25R70_GATE=<copy of gate.py> python ops/add_ourvzlb25r70_gate.py

ourvzlb25r70 must prove on the visible run (4 movies):
  * need['ourvzlb25'] (read out of gate.py with ast) minus its ARM_XENV line: STK3V 0.25 / STK3B 2.5 / T65H 6.5 + the
    three cell-2 linker echoes, and every V1284 / z-to-arr / per-movie SV_ARM_HSG200 + ARM_SV_Z_TO_ARR pin EXACTLY
    (rawlink acts on the final graph, long after detection, so the coordinate prints are ourvzlb25's bit for bit);
  * need['t6r70']'s six rawlink patterns (read with ast, and checked equal to need['t65b25r70']'s): the cell-2
    ARM_RAWLINK min_prob=0.7 enabled=True line, the "rawlink_min_prob": 0.7 echo and the four per-movie ARM_RAWLINK
    lines with accepted >= 1;
  * the cell-0 identity line ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted
    SUBVOXEL=z-to-arr V1284_AXES=yx (replaces ourvzlb25's XENV line);
  * exactly as the t65b25r70 entry: the tag joins RL_TAGS (per-movie line after FINAL, degree <= 1/2, division count
    unchanged, anchor + accepted - replaced == final, change-fraction window, total-accepted window) and the orphan cap
    (<= 50 per movie, <= 150 total new_isolated), plus the per-movie cross-check: cell-10 written nodes/edges/divisions
    == (FINAL nodes, ARM_RAWLINK final=, safe divisions added) and run_stats.csv agrees (smoothed + skipped == nodes).
    The block is generated from the live t65b25r70 block (tag + variable prefix renamed) and checked against it;
  * sv_mark SV_ARM_HSG200 INSIDE the dict literal (>= 4 lines before 'Prediction completed'); FINAL within 15% of REF;
  * forbidden: everything forbid['ourvzlb25'] forbids (resolved with ast) with two rewrites: its XENV forbid now
    allows only tag=ourvzlb25r70, and its ARM_ allowlist gains RAWLINK (the only rawlink-forbidding element it has);
    PLUS t65b25r70's three rawlink-value forbids (read with ast): a disabled rawlink, an ARM_RAWLINK line at any
    min_prob != 0.7, a "rawlink_min_prob" echo != 0.7. ourvzlb25's own forbids keep tight != 6.5 / bonus != 2.5 /
    ARM_T60H / ARM_LCEFR (t6 body) / foreign SV_ARM_ / tracebacks / IndentationError / every V1284 + z-to-arr failure.
Self-tests: the ourvzlb25 and t65b25r70 logs must FAIL as ourvzlb25r70; ourvzlb25 / t65b25r70 / t65b25 / t65b20 /
ourvzl / t6r70 / t6stk3 must still PASS as themselves. A SYNTHETIC ourvzlb25r70 log (ourvzlb25's log + the rawlink
prints, accepted == replaced so the written counts and run_stats stay consistent) must PASS, and mutants must FAIL,
the structural ones on their own message: rawlink disabled, a 0.3 threshold, a 1.6 bonus echo, an ARM_T60H line,
ourvzlb25's XENV line, a traceback, an ARM_LCEFR line, written edges != rawlink final= (cross-check), new_isolated=60
(orphan cap), accepted 10 per movie (RL_TAGS total window), SV lines after 'Prediction completed' (sv_mark), no
run_stats.csv beside the log.
"""
import ast
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("OURVZLB25R70_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("OURVZLB25R70_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "ourvzlb25r70"
BASE_TAG = "ourvzlb25"
RL_TAG = "t65b25r70"
OLD_XENV = r"ARM_XENV tag=ourvzlb25 TIGHT=6\.5 BONUS=2\.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
XENV = r"ARM_XENV tag=ourvzlb25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
OLD_XFORBID = r"ARM_XENV tag=(?!ourvzlb25 )"
NEW_XFORBID = r"ARM_XENV tag=(?!ourvzlb25r70 )"
OLD_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX)\b)[A-Z0-9]+"
NEW_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\b)[A-Z0-9]+"
RL_FORBID = [r"ARM_RAWLINK min_prob=\S+ enabled=False", r"ARM_RAWLINK (?:\[\w+\] )?min_prob=(?!0\.7(?!\d))",
             r'"rawlink_min_prob": (?!0\.7(?!\d))']
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
# real rawlink prints (t65b25r70 visible run) that the new forbid list must NOT hit
GOOD_RL_LINES = [
    "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
    '  "rawlink_min_prob": 0.7,',
    "ARM_RAWLINK [44b6_0113de3b] min_prob=0.7 candidates=325 accepted=325 replaced=301 anchor=24890 final=24914 "
    "max_in=1 max_out=2 divs=34->34 divs_shielded=2 blocked_parent=0 blocked_daughter=2 below_min=43 replaced_raw=0 "
    "new_isolated=6",
    "ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"]


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def _forbid_key(target):
    if isinstance(target, ast.Subscript) and getattr(target.value, "id", None) == "forbid":
        s = target.slice
        if isinstance(s, ast.Constant) and isinstance(s.value, str):
            return s.value
    return None


def forbid_of(src, key):
    """Resolve forbid[key] from the module's top-level statements (literal lists, forbid[x] refs, '+')."""
    body = ast.parse(src).body
    assigns = {}
    watch = {BASE_TAG, RL_TAG, TAG}
    for node in body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            k = _forbid_key(node.targets[0])
            if k is not None:
                assigns.setdefault(k, []).append(node)
        if isinstance(node, ast.For) and isinstance(node.iter, (ast.Tuple, ast.List)):
            names = {e.value for e in node.iter.elts if isinstance(e, ast.Constant)}
            if names & watch:
                raise SystemExit("a top-level loop rewrites forbid for %r; refusing to resolve by ast" % (names & watch))

    def resolve(expr):
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
            return resolve(expr.left) + resolve(expr.right)
        k = _forbid_key(expr)
        if k is not None:
            return resolve_key(k)
        return list(ast.literal_eval(expr))

    def resolve_key(k):
        nodes = assigns.get(k, [])
        if len(nodes) != 1:
            raise SystemExit("forbid[%r] assigned %d times at top level (expected exactly 1)" % (k, len(nodes)))
        return resolve(nodes[0].value)

    return resolve_key(key)


def gate_file(lg, tag):
    out = subprocess.run([sys.executable, str(GATE), str(lg), tag], capture_output=True, text=True).stdout.strip()
    return out.splitlines()[-1] if out else "NO OUTPUT"


def gate(logdir, tag):
    return gate_file(next((ROOT / "data" / logdir).glob("*.log")), tag)


def log_text(p):
    import json
    raw = p.read_text(encoding="utf-8")
    try:
        return "".join(e.get("data", "") for e in json.loads(raw))
    except Exception:
        return raw


def xcheck_from_live(t):
    """The live t65b25r70 cross-check block, renamed for this tag (comment lines dropped, code byte for byte)."""
    start = t.index("# --- t65b25r70 (ops/add_t65b25r70_gate.py)")
    end = t.index('if "t65b25r70" in tags:\n', start)
    stop = t.index("\n# --- ", end) + 1
    code = t[end:stop]
    if code.count("t65b25r70") != 5 or code.count("_xwant") != 6 or "_ov" in code or "\n#" in code.rstrip("\n"):
        raise SystemExit("the live t65b25r70 cross-check block is not the one this installer was written against")
    return code.replace("t65b25r70", TAG).replace("_x", "_ov")


def insert_after_line(txt, needle, add):
    i = txt.find(needle)
    if i < 0:
        raise SystemExit("synthetic: %r not in the source log" % needle)
    j = txt.index("\n", i) + 1
    return txt[:j] + add + txt[j:]


def main():
    t = GATE.read_text(encoding="utf-8")
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    # ---- need
    base = list(need_of(t, BASE_TAG))
    r70 = list(need_of(t, "t6r70"))
    b25r = list(need_of(t, RL_TAG))
    if base.count(OLD_XENV) != 1 or sum("ARM_XENV" in p for p in base) != 1:
        raise SystemExit("need['ourvzlb25'] does not carry exactly one XENV line: %r" % base)
    if any("RAWLINK" in p or "rawlink" in p for p in base):
        raise SystemExit("need['ourvzlb25'] unexpectedly pins rawlink markers: %r" % base)
    rl = [p for p in r70 if ("RAWLINK" in p or "rawlink" in p) and not p.startswith("ARM_XENV")]
    rl_b25r = [p for p in b25r if ("RAWLINK" in p or "rawlink" in p) and not p.startswith("ARM_XENV")]
    if any(p.startswith("ARM_XENV") for p in r70):
        raise SystemExit("need['t6r70'] unexpectedly carries an ARM_XENV line: %r" % r70)
    if len(rl) != 6 or rl != rl_b25r:
        raise SystemExit("need['t6r70'] rawlink patterns (%d) != need['t65b25r70']'s:\n%r\n%r" % (len(rl), rl, rl_b25r))
    core = [p for p in base if p != OLD_XENV]
    pats = core + rl + [XENV]
    for stale in (r"1\.6", r"6\.0", "T60H", "LCEFR", "tag=ourvzlb25 ", "tag=t65b25r70"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    if len(pats) != len(base) + 6 or pats.count(XENV) != 1 or len(set(pats)) != len(pats):
        raise SystemExit("expected ourvzlb25's %d patterns - XENV + 6 rawlink + XENV, got %r" % (len(base), pats))
    # ---- forbid
    fz = forbid_of(t, BASE_TAG)
    fr = forbid_of(t, RL_TAG)
    if fz.count(OLD_XFORBID) != 1 or fz.count(OLD_ALLOW) != 1:
        raise SystemExit("forbid['ourvzlb25'] lacks its XENV forbid / ARM_ allowlist exactly once: %r" % fz)
    for p in RL_FORBID:
        if fr.count(p) != 1:
            raise SystemExit("forbid['t65b25r70'] lacks rawlink forbid %r" % p)
    if any("RAWLINK" in p or "rawlink" in p for p in fz):
        raise SystemExit("forbid['ourvzlb25'] mentions rawlink explicitly; re-derive by hand: %r" % fz)
    forbid = [NEW_XFORBID if p == OLD_XFORBID else NEW_ALLOW if p == OLD_ALLOW else p for p in fz]
    forbid += [p for p in RL_FORBID if p not in forbid]
    for line in GOOD_RL_LINES:
        hit = [p for p in forbid if re.search(p, line)]
        if hit:
            raise SystemExit("new forbid list hits a legitimate rawlink/XENV print %r via %r" % (line[:60], hit))
    for line in ("ARM_RAWLINK min_prob=-1.0 enabled=False rule=x", "ARM_RAWLINK [44b6_0113de3b] min_prob=0.3 candidates=1 ",
                 '"rawlink_min_prob": 0.3,', "ARM_XENV tag=ourvzlb25 TIGHT", "ARM_LCEFR patch applied to x",
                 '"motion_relink_learned_bonus": 1.6,', '"motion_relink_tight_um": 6.0,', "ARM_T60H tight_um=6.0",
                 "Traceback (most recent call last)", "ARM_FLOWFIX enabled=True"):
        if not any(re.search(p, line) for p in forbid):
            raise SystemExit("new forbid list does not catch %r" % line)
    # ---- patch text
    comment = ("        # --- ourvzlb25r70: ourvzlb25 (V1284 y/x head + sub-voxel z to the edge model, tight 6.5, bonus 2.5; board\n"
               "        # 0.954) + t6r70's raw-ILP override at prob >= 0.70 (the step that made t65b25r70 the representative).\n"
               "        # = need['ourvzlb25'] minus its XENV + need['t6r70']'s six rawlink patterns + this arm's XENV\n"
               "        # (build_ourvzlb25r70.py; ops/add_ourvzlb25r70_gate.py). Coordinate pins stay EXACT (rawlink acts on the\n"
               "        # final graph); RL_TAGS + orphan cap + the written-count cross-check carry the rawlink bookkeeping.\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    xcheck = ("# --- ourvzlb25r70 (ops/add_ourvzlb25r70_gate.py): ourvzlb25 + t6r70's rawlink 0.70. Same per-movie cross-check as\n"
              "# t65b25r70 (generated from its block): cell-10 written nodes/edges/divisions == (FINAL nodes, ARM_RAWLINK final=,\n"
              "# safe divisions added), run_stats agrees, line-fit smoothed + skipped == nodes.\n") + xcheck_from_live(t)
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": '"ourvzl": 0.15',
               "rltags": 'RL_TAGS = {"rawlink70", "t6r70", "t6rlf", "t6r70T15", "t65b25r70"}',
               "orphan": '    if {"t6r70", "t6rlf", "t6r70T15", "t65b25r70"} & set(tags):\n',
               "svtags": 'sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    t2 = t.replace(anchors["need"], entry + anchors["need"], 1)
    t2 = t2.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t2 = t2.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t2 = t2.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % TAG, 1)
    t2 = t2.replace(anchors["rltags"], anchors["rltags"][:-1] + ', "%s"}' % TAG, 1)
    t2 = t2.replace(anchors["orphan"], '    if {"t6r70", "t6rlf", "t6r70T15", "t65b25r70", "%s"} & set(tags):\n' % TAG, 1)
    t2 = t2.replace(anchors["svtags"], xcheck + anchors["svtags"], 1)
    # structural re-checks on the patched text
    lit = [n for n in ast.parse(t2).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "sv_mark"
           and isinstance(n.value, ast.Dict)]
    if len(lit) != 1 or ast.literal_eval(lit[0].value).get(TAG) != "SV_ARM_HSG200" \
            or not t2.index("sv_mark = {") < t2.index('"%s": "SV_ARM_HSG200"' % TAG) < t2.index(anchors["svtags"]):
        raise SystemExit("sv_mark entry for %s is not inside the dict literal before sv_tags is computed" % TAG)
    if forbid_of(t2, TAG) != forbid or need_of(t2, TAG) != pats:
        raise SystemExit("re-parse of the patched gate does not return the new need/forbid entries")
    if not (t2.index('"%s" in tags:' % TAG) < t2.index(anchors["svtags"])
            and t2.index('RL_TAGS = {') < t2.index('"%s" in tags:' % TAG)):
        raise SystemExit("cross-check block misplaced")
    ast.parse(t2)
    compile(t2, str(GATE), "exec")
    if GATE.read_text(encoding="utf-8") != t:
        raise SystemExit("gate.py changed while patching (another installer?); nothing written")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(t, encoding="utf-8")
    GATE.write_text(t2, encoding="utf-8")
    # ---- self-tests on real logs
    res = {"neg_ourvzlb25_as_ourvzlb25r70": gate("out_ourvzlb25", TAG),
           "neg_t65b25r70_as_ourvzlb25r70": gate("out_t65b25r70", TAG),
           "pos_ourvzlb25": gate("out_ourvzlb25", "ourvzlb25"), "pos_t65b25r70": gate("out_t65b25r70", "t65b25r70"),
           "pos_t65b25": gate("out_t65b25", "t65b25"), "pos_t65b20": gate("out_t65b20", "t65b20"),
           "pos_ourvzl": gate("out_ourvzl", "ourvzl"), "pos_t6r70": gate("out_t6r70", "t6r70"),
           "pos_t6stk3": gate("out_t6stk3", "t6stk3")}
    own = list((ROOT / "data").glob("out_%s/*.log" % TAG))
    if own:
        res["own_" + TAG] = gate("out_" + TAG, TAG)
    # ---- synthetic positive + mutants from ourvzlb25's log (+ its run_stats.csv)
    src_dir = ROOT / "data" / "out_ourvzlb25"
    src = log_text(next(src_dir.glob("*.log")))
    fin = {d: tuple(int(x) for x in re.search(r"\[%s\] FINAL: (\d+) nodes, (\d+) edges" % d, src).groups()) for d in MOVIES}
    sdv = {d: int(re.search(r"\[%s\] after safe-division repair: [^\n]*?\badded=(\d+)" % d, src).group(1)) for d in MOVIES}
    acc = dict(zip(MOVIES, (300, 40, 15, 600)))

    def rl_line(d, k=None, extra_final=0, iso=0, prob="0.7"):
        k = acc[d] if k is None else k
        e = fin[d][1]
        return ("ARM_RAWLINK [%s] min_prob=%s candidates=%d accepted=%d replaced=%d anchor=%d final=%d max_in=1 "
                "max_out=2 divs=%d->%d divs_shielded=0 blocked_parent=0 blocked_daughter=0 below_min=10 replaced_raw=0 "
                "new_isolated=%d\n" % (d, prob, k + extra_final, k + extra_final, k, e, e + extra_final,
                                       sdv[d], sdv[d], iso))

    xenv_old_line = "ARM_XENV tag=ourvzlb25 TIGHT=6.5 BONUS=2.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
    xenv_new_line = "ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
    cell2 = "  \"rawlink_min_prob\": 0.7,\nARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected\n"

    def build(**kw):
        s = src
        if s.count(xenv_old_line) != 1:
            raise SystemExit("synthetic: ourvzlb25 XENV line not exactly once in its log")
        s = s.replace(xenv_old_line, xenv_new_line)
        s = insert_after_line(s, xenv_new_line, cell2)
        for d in MOVIES:
            s = insert_after_line(s, "[%s] FINAL: " % d, rl_line(d, **kw.get(d, {})))
        return s

    syn = build()
    pe = syn.find("Prediction completed")
    fe = syn.find("[44b6_0113de3b] FINAL: ")
    mutants = {
        "neg_syn_rawlink_disabled": (syn[:pe] + "ARM_RAWLINK min_prob=-1.0 enabled=False rule=raw_ilp_override_final_divisions_protected\n" + syn[pe:], None),
        "neg_syn_threshold_030": (build(**{"6bba_05b6850b": {"prob": "0.3"}}), None),
        "neg_syn_bonus16_echo": (syn[:pe] + '"motion_relink_learned_bonus": 1.6,\n' + syn[pe:], None),
        "neg_syn_t60h_line": (syn[:pe] + "ARM_T60H tight_um=6.0\n" + syn[pe:], None),
        "neg_syn_ourvzlb25_xenv": (syn[:pe] + xenv_old_line + "\n" + syn[pe:], None),
        "neg_syn_traceback": (syn[:fe] + "Traceback (most recent call last):\n" + syn[fe:], None),
        "neg_syn_lcefr_line": (syn[:pe] + "ARM_LCEFR patch applied to predictor\n" + syn[pe:], None),
        "neg_syn_written_mismatch": (build(**{"44b6_0b24845f": {"extra_final": 1}}), "written nodes/edges/divisions"),
        "neg_syn_orphans60": (build(**{"6bba_05db0fb1": {"iso": 60}}), "rawlink orphaned more than 50 nodes"),
        "neg_syn_accepted_window": (build(**{d: {"k": 10} for d in MOVIES}), "raw edges in total, outside"),
        "neg_syn_sv_after_pred": ("Prediction completed (mutant: SV lines now after it)\n" + syn,
                                  "only 0 SV_ARM_HSG200 lines before 'Prediction completed'"),
    }
    with tempfile.TemporaryDirectory() as td:
        cases = [("pos_syn_ourvzlb25r70", syn, None, True)] + [(k, v, why, True) for k, (v, why) in mutants.items()]
        cases.append(("neg_syn_no_run_stats", syn, "no run_stats.csv beside the log", False))
        for name, body, why, with_rs in cases:
            d = pathlib.Path(td) / name
            d.mkdir()
            if with_rs:
                shutil.copy(src_dir / "run_stats.csv", d / "run_stats.csv")
            p = d / (name + ".log")
            p.write_text(body, encoding="utf-8")
            res[name] = gate_file(p, TAG)
            if why is not None and why not in res[name]:
                res[name] = "WRONG-REASON (wanted %r): %s" % (why, res[name])
    for k, v in res.items():
        print(k, "->", v[:700])
    ok = all("GATE_FAIL" in v and not v.startswith("WRONG-REASON") for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_"))
    if not ok:
        if GATE.read_text(encoding="utf-8") == t2:
            GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
            raise SystemExit("self-test failed; gate.py restored from " + bak.name)
        raise SystemExit("self-test failed AND gate.py was modified by someone else meanwhile; NOT restored, check by hand")
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
