#!/usr/bin/env python3
r"""Gate entry for t65b25r70sr (scratch_kernels/build_t65b25r70sr.py) = t65b25r70 (t6stk3 body + relink tight 6.5 +
learned bonus 2.5 + t6r70's raw-ILP override "rawlink" 0.70; representative 0.954) with the adaptive short-track rescue
armed unconditionally (BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC 0.10 -> 0.0), exactly as t6sr armed it on
t6stk3. Run from the project root: it backs up ops/gate.py (gate.py.bak_t65b25r70sr), patches it, self-tests, and
restores the backup if any self-test fails.
Dry run: T65B25R70SR_GATE=<copy of gate.py> python ops/add_t65b25r70sr_gate.py

t65b25r70sr must prove on the visible run (4 movies):
  * need['t65b25r70'] (read out of gate.py with ast) minus its ARM_XENV line (linker 6.5 / 2.5 markers + echoes, LCEFR
    runtime counters, line-fit echoes, the six rawlink patterns);
  * t6sr's own requirements (need['t6sr'] minus need['t6stk3'], read with ast): its trigger-0.0 identity line is
    replaced by this arm's XENV + the LIVE cell-2 echo "short_track_rescue_trigger_removed_frac": 0.0 (the value
    after float(), i.e. proof the variable reached the config, which the cell-0 print alone is not); its
    "deepcenter_safe_div_threshold": 0.25 echo is carried over;
  * the cell-0 identity line ARM_XENV tag=t65b25r70sr TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 SR=armed;
  * the rawlink structural checks, as for t65b25r70 (RL_TAGS + orphan cap) and t65b25r70's per-movie written-count
    cross-check (generated from the live block, tag + variable prefix renamed): cell-10 written nodes/edges/divisions
    == (FINAL nodes, ARM_RAWLINK final=, safe divisions added), run_stats agrees, smoothed + skipped == nodes;
  * rescue receipts from run_stats.csv (the rescue has no log line of its own): short_track_rescue_triggered == 1 on
    all four movies (trigger 0.0 => the branch runs everywhere), components <= nodes <= budget per movie, and > 0
    components restored on at least one movie. No float digests are pinned;
  * sv_mark SV_ARM_HSG200 inside the dict literal; FINAL within 15% of REF;
  * forbidden: everything forbid['t65b25r70'] forbids (resolved with ast) with its XENV forbid rewritten to allow only
    tag=t65b25r70sr (so t65b25r70's / t6sr's identity lines fail), PLUS a trigger echo != 0.0 and
    "adaptive_short_track_rescue": false.
Self-tests: the t65b25r70 and t6sr logs must FAIL as t65b25r70sr; t65b25r70 / ourvzlb25r70 / t65b25 / t65b20 / t6r70 /
t6stk3 / t6sr / t6stk3ff (+ t65b25r70ff if its log exists) must still PASS as themselves; every need entry present
before the patch must still exist. A SYNTHETIC t65b25r70sr log (t65b25r70's log with this XENV and the 0.0 echo, run_stats
rescue columns filled) must PASS and mutants must FAIL on their own message.
"""
import ast
import csv
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("T65B25R70SR_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T65B25R70SR_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t65b25r70sr"
BASE_TAG = "t65b25r70"
OLD_XENV = r"ARM_XENV tag=t65b25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 LCEFR=kept"
T6SR_XENV = r"ARM_XENV tag=t6sr BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=0\.0"
XENV = r"ARM_XENV tag=t65b25r70sr TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 SR=armed"
ECHO = r'"short_track_rescue_trigger_removed_frac": 0\.0(?!\d)'
OLD_XFORBID = r"ARM_XENV tag=(?!t65b25r70 )"
NEW_XFORBID = r"ARM_XENV tag=(?!t65b25r70sr )"
SR_FORBID = [r'"short_track_rescue_trigger_removed_frac": (?!0\.0(?!\d))', r'"adaptive_short_track_rescue": false']
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
EXPECT_ENTRIES = ("t65b25r70", "ourvzlb25r70", "t65b20d04", "t70b25", "t675b25", "t65b25r70ff")
REGRESS = ("t65b25r70", "ourvzlb25r70", "t65b25", "t65b20", "t6r70", "t6stk3", "t6sr", "t6stk3ff")
XENV_LINE = "ARM_XENV tag=t65b25r70sr TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 SR=armed"
GOOD_LINES = [XENV_LINE, '  "short_track_rescue_trigger_removed_frac": 0.0,', '  "adaptive_short_track_rescue": true,',
              '  "deepcenter_safe_div_threshold": 0.25,',
              "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
              '  "rawlink_min_prob": 0.7,',
              "ARM_RAWLINK [44b6_0113de3b] min_prob=0.7 candidates=325 accepted=325 replaced=301 anchor=24890 "
              "final=24914 max_in=1 max_out=2 divs=34->34 divs_shielded=2 blocked_parent=0 blocked_daughter=2 "
              "below_min=43 replaced_raw=0 new_isolated=6",
              "ARM_STK3B learned_bonus=2.5", "ARM_T65H tight_um=6.5", "ARM_LCEFR patch applied to predictor",
              "  SHORT_TRACK_RESCUE_MIN_MEAN_EDGE_PROB    0.88"]
BAD_LINES = ['  "short_track_rescue_trigger_removed_frac": 0.1,', '"short_track_rescue_trigger_removed_frac": 0.05,',
             '"adaptive_short_track_rescue": false,', "ARM_XENV tag=t65b25r70 TIGHT",
             "ARM_XENV tag=t6sr BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=0.0",
             "ARM_FLOWFIX enabled=True TF=5.0", "ARM_RAWLINK min_prob=-1.0 enabled=False rule=x",
             '"motion_relink_learned_bonus": 1.6,', "ARM_T60H tight_um=6.0", "Traceback (most recent call last)"]

RESCUE = r'''    # rescue receipts (ops/add_t65b25r70sr_gate.py): the rescue prints no line of its own, so run_stats is the only
    # evidence. Trigger 0.0 => the branch runs on every movie (triggered == 1); components <= nodes <= budget; and
    # at least one visible movie must get components back, otherwise the armed branch did nothing.
    if _srxrs is not None:
        _srxcomp = []
        for d in sorted(REF):
            _srxrow = _srxrs.get(d) or {}
            try:
                _srxq = tuple(int(float(_srxrow[k])) for k in ("short_track_rescue_triggered", "short_track_rescue_components",
                                                             "short_track_rescue_nodes", "short_track_rescue_budget"))
            except (KeyError, TypeError, ValueError):
                _srxq = None
            if _srxq is None:
                fails.append(f"t65b25r70sr {d}: run_stats has no readable short_track_rescue_* columns")
                continue
            if _srxq[0] != 1:
                fails.append(f"t65b25r70sr {d}: short_track_rescue_triggered={_srxq[0]}: with trigger 0.0 the rescue "
                             "branch must run on every movie")
            if not 0 <= _srxq[1] <= _srxq[2] <= _srxq[3]:
                fails.append(f"t65b25r70sr {d}: rescued components/nodes/budget {_srxq[1:]} inconsistent "
                             "(components <= nodes <= budget)")
            _srxcomp.append(_srxq[1])
        if not _srxcomp or max(_srxcomp) == 0:
            fails.append("t65b25r70sr: the armed rescue restored 0 components on every visible movie: the branch did nothing")
'''


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def need_keys(src):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            return {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
    raise SystemExit("no need dict")


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
    watch = {BASE_TAG, TAG}
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
    raw = p.read_text(encoding="utf-8")
    try:
        return "".join(e.get("data", "") for e in json.loads(raw))
    except Exception:
        return raw


def xcheck_from_live(t):
    """The live t65b25r70 cross-check block, renamed for this tag (code byte for byte) + the rescue receipts."""
    start = t.index("# --- t65b25r70 (ops/add_t65b25r70_gate.py)")
    end = t.index('if "t65b25r70" in tags:\n', start)
    stop = t.index("\n# --- ", end) + 1
    code = t[end:stop]
    if code.count("t65b25r70") != 5 or code.count("_xwant") != 6 or "_srx" in code or "\n#" in code.rstrip("\n") \
            or code.count("_xrs = None") != 1:
        raise SystemExit("the live t65b25r70 cross-check block is not the one this installer was written against")
    code = code.replace("t65b25r70", TAG).replace("_x", "_srx")
    head = ("# --- t65b25r70sr (ops/add_t65b25r70sr_gate.py): t65b25r70 + short-track rescue armed (trigger 0.0). The\n"
            "# t65b25r70 per-movie cross-check (generated from its block: written nodes/edges/divisions == (FINAL nodes,\n"
            "# ARM_RAWLINK final=, safe divisions added), run_stats agrees, smoothed + skipped == nodes) + rescue receipts.\n")
    return head + code + RESCUE


def patch(t):
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    base = list(need_of(t, BASE_TAG))
    sr = list(need_of(t, "t6sr"))
    stk = list(need_of(t, "t6stk3"))
    if base.count(OLD_XENV) != 1 or sum("ARM_XENV" in p for p in base) != 1:
        raise SystemExit("need['t65b25r70'] does not carry exactly one XENV line: %r" % base)
    own_sr = [p for p in sr if p not in stk]
    if [p for p in stk if p not in sr] or T6SR_XENV not in own_sr:
        raise SystemExit("need['t6sr'] is not need['t6stk3'] + its own markers: %r" % own_sr)
    carry = [p for p in own_sr if p != T6SR_XENV]
    if carry != [r'"deepcenter_safe_div_threshold": 0\.25(?!\d)']:
        raise SystemExit("t6sr's own non-XENV markers are not the ones this installer was written against: %r" % carry)
    if any("short_track" in p for p in base):
        raise SystemExit("need['t65b25r70'] unexpectedly pins rescue markers")
    pats = [p for p in base if p != OLD_XENV] + [p for p in carry if p not in base] + [ECHO, XENV]
    if len(set(pats)) != len(pats) or pats.count(XENV) != 1 or pats.count(ECHO) != 1:
        raise SystemExit("bad pattern list %r" % pats)
    for stale in (r"1\.6", r"6\.0", "T60H", "tag=t65b25r70 ", "tag=t6sr", "FLOWFIX"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    if sum("RAWLINK" in p or "rawlink" in p for p in pats) != 7:
        raise SystemExit("rawlink patterns not carried over intact: %r" % pats)
    fr = forbid_of(t, BASE_TAG)
    if fr.count(OLD_XFORBID) != 1 or fr.count("ARM_FLOWFIX") != 1:
        raise SystemExit("forbid['t65b25r70'] lacks its XENV forbid / ARM_FLOWFIX exactly once: %r" % fr)
    if any("short_track" in p for p in fr):
        raise SystemExit("forbid['t65b25r70'] mentions the rescue; re-derive by hand")
    forbid = [NEW_XFORBID if p == OLD_XFORBID else p for p in fr] + SR_FORBID
    for line in GOOD_LINES:
        hit = [p for p in forbid if re.search(p, line)]
        if hit:
            raise SystemExit("new forbid list hits a legitimate print %r via %r" % (line[:60], hit))
    for line in BAD_LINES:
        if not any(re.search(p, line) for p in forbid):
            raise SystemExit("new forbid list does not catch %r" % line)
    comment = ("        # --- t65b25r70sr: t65b25r70 (t6stk3 + tight 6.5 + bonus 2.5 + raw-ILP override 0.70; representative 0.954)\n"
               "        # with the short-track rescue armed unconditionally (trigger 0.10 -> 0.0), as t6sr did on t6stk3.\n"
               "        # = need['t65b25r70'] minus its XENV + t6sr's deepcenter echo + the live trigger echo 0.0 + this XENV\n"
               "        # (build_t65b25r70sr.py; ops/add_t65b25r70sr_gate.py). RL_TAGS + orphan cap + the written-count\n"
               "        # cross-check + run_stats rescue receipts (triggered on all movies, components > 0 somewhere) below.\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    xcheck = xcheck_from_live(t)
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": "tol = max({",
               "svtags": 'sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    rl_re = re.compile(r'(?m)^(RL_TAGS = \{"rawlink70", "t6r70"[^}\n]*)\}')
    or_re = re.compile(r'(?m)^(    if \{"t6r70", "t6rlf", "t6r70T15"[^}\n]*)\}( & set\(tags\):)$')
    if len(rl_re.findall(t)) != 1 or len(or_re.findall(t)) != 1:
        raise SystemExit("RL_TAGS / orphan-cap line not found exactly once")
    if '"%s"' % BASE_TAG not in rl_re.search(t).group(1) or '"%s"' % BASE_TAG not in or_re.search(t).group(1):
        raise SystemExit("t65b25r70 is not in RL_TAGS / the orphan cap; refusing to guess")
    t2 = t.replace(anchors["need"], entry + anchors["need"], 1)
    t2 = t2.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t2 = t2.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t2 = t2.replace(anchors["tol"], anchors["tol"] + '"%s": 0.15, ' % TAG, 1)
    t2 = rl_re.sub(lambda m: m.group(1) + ', "%s"}' % TAG, t2, count=1)
    t2 = or_re.sub(lambda m: m.group(1) + ', "%s"}' % TAG + m.group(2), t2, count=1)
    t2 = t2.replace(anchors["svtags"], xcheck + anchors["svtags"], 1)
    lit = [n for n in ast.parse(t2).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "sv_mark"
           and isinstance(n.value, ast.Dict)]
    if len(lit) != 1 or ast.literal_eval(lit[0].value).get(TAG) != "SV_ARM_HSG200" \
            or not t2.index("sv_mark = {") < t2.index('"%s": "SV_ARM_HSG200"' % TAG) < t2.index(anchors["svtags"]):
        raise SystemExit("sv_mark entry for %s is not inside the dict literal before sv_tags is computed" % TAG)
    if forbid_of(t2, TAG) != forbid or need_of(t2, TAG) != pats:
        raise SystemExit("re-parse of the patched gate does not return the new need/forbid entries")
    if '"%s"' % TAG not in rl_re.search(t2).group(1) or '"%s"' % TAG not in or_re.search(t2).group(1):
        raise SystemExit("RL_TAGS / orphan cap patch did not land")
    if not (t2.index('RL_TAGS = {') < t2.index('if "%s" in tags:' % TAG) < t2.index(anchors["svtags"])):
        raise SystemExit("cross-check block misplaced")
    if not need_keys(t) <= need_keys(t2) or (need_keys(t2) - need_keys(t)) != {TAG}:
        raise SystemExit("need keys changed beyond adding %s" % TAG)
    ast.parse(t2)
    compile(t2, str(GATE), "exec")
    return t2, pats, forbid


def synth(src, rs_rows, mut=None):
    """t65b25r70's visible log turned into a plausible t65b25r70sr log (+ run_stats rows with rescue columns)."""
    mut = mut or {}
    s = src
    old_x = "ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept"
    old_e = '"short_track_rescue_trigger_removed_frac": 0.1,'
    if s.count(old_x) != 1 or s.count(old_e) != 1:
        raise SystemExit("synthetic: t65b25r70 XENV / trigger echo not exactly once in its log")
    s = s.replace(old_x, XENV_LINE)
    if not mut.get("keep_echo"):
        s = s.replace(old_e, '"short_track_rescue_trigger_removed_frac": 0.0,')
    if mut.get("adaptive_false"):
        if s.count('"adaptive_short_track_rescue": true,') != 1:
            raise SystemExit("synthetic: adaptive echo not exactly once")
        s = s.replace('"adaptive_short_track_rescue": true,', '"adaptive_short_track_rescue": false,')
    if mut.get("written_off"):
        s, n = re.subn(r"(?m)^(\s+44b6_0b24845f: nodes=\d+ edges=)(\d+)( divisions=\d+\s*)$",
                       lambda mm: mm.group(1) + str(int(mm.group(2)) + 1) + mm.group(3), s, count=1)
        if n != 1:
            raise SystemExit("synthetic: cell-10 line not found")
    if mut.get("orphans"):
        s, n = re.subn(r"(ARM_RAWLINK \[6bba_05db0fb1\] [^\n]*? new_isolated=)\d+", lambda mm: mm.group(1) + "60", s, count=1)
        if n != 1:
            raise SystemExit("synthetic: rawlink line not found")
    for extra in mut.get("extra_lines", []):
        s = s.replace("Prediction completed", extra + "\nPrediction completed", 1) if "Prediction completed" in s else s + extra + "\n"
    rows = []
    comps = mut.get("comps", (5, 6, 2, 7))
    for k, r in enumerate(rs_rows):
        r = dict(r)
        budget = 73 if r["dataset"] == "6bba_05b6850b" else 120
        r.update(short_track_rescue_triggered=str(0 if mut.get("untrig") == r["dataset"] else 1),
                 short_track_rescue_components=str(comps[k]),
                 short_track_rescue_nodes=str(comps[k] * 4 + (200 if mut.get("over_budget") else 1)),
                 short_track_rescue_budget=str(budget))
        if mut.get("drop_cols"):
            for c in ("short_track_rescue_triggered", "short_track_rescue_components"):
                r.pop(c)
        rows.append(r)
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return s, out.getvalue()


def main():
    t = GATE.read_text(encoding="utf-8")
    t2, pats, forbid = patch(t)
    if GATE.read_text(encoding="utf-8") != t:
        raise SystemExit("gate.py changed while patching (another installer?); nothing written")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(t, encoding="utf-8")
    GATE.write_text(t2, encoding="utf-8")
    now = GATE.read_text(encoding="utf-8")
    res = {}
    missing = [k for k in EXPECT_ENTRIES + tuple(sorted(need_keys(t))) if k not in need_keys(now)]
    if missing:
        res["neg_entries_missing"] = "GATE_FAIL: need entries missing after the patch: %r" % missing
    res["neg_t65b25r70_as_" + TAG] = gate("out_t65b25r70", TAG)
    res["neg_t6sr_as_" + TAG] = gate("out_t6sr", TAG)
    for tg in REGRESS + ("t65b25r70ff",):
        if list((ROOT / "data").glob("out_%s/*.log" % tg)):
            res["pos_" + tg] = gate("out_" + tg, tg)
    own = list((ROOT / "data").glob("out_%s/*.log" % TAG))
    if own:
        res["own_" + TAG] = gate("out_" + TAG, TAG)
    src_dir = ROOT / "data" / "out_t65b25r70"
    src = log_text(next(src_dir.glob("*.log")))
    with open(src_dir / "run_stats.csv", newline="", encoding="utf-8") as fh:
        rs_rows = list(csv.DictReader(fh))
    mutants = {
        "neg_syn_echo_still_01": ({"keep_echo": True}, "marker missing"),
        "neg_syn_not_triggered": ({"untrig": "44b6_0b24845f"}, "short_track_rescue_triggered=0"),
        "neg_syn_zero_components": ({"comps": (0, 0, 0, 0)}, "restored 0 components on every visible movie"),
        "neg_syn_over_budget": ({"over_budget": True}, "components <= nodes <= budget"),
        "neg_syn_no_rescue_cols": ({"drop_cols": True}, "no readable short_track_rescue_* columns"),
        "neg_syn_adaptive_false": ({"adaptive_false": True}, "log contains"),
        "neg_syn_old_xenv": ({"extra_lines": ["ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept"]}, "log contains"),
        "neg_syn_t6sr_xenv": ({"extra_lines": ["ARM_XENV tag=t6sr BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=0.0"]}, "log contains"),
        "neg_syn_flowfix_line": ({"extra_lines": ["ARM_FLOWFIX enabled=True TF=5.0 KEEP=3.5"]}, "log contains"),
        "neg_syn_traceback": ({"extra_lines": ["Traceback (most recent call last):"]}, "log contains"),
        "neg_syn_written_mismatch": ({"written_off": True}, "written nodes/edges/divisions"),
        "neg_syn_orphans60": ({"orphans": True}, "rawlink orphaned more than 50 nodes"),
    }
    with tempfile.TemporaryDirectory() as td:
        cases = [("pos_syn_" + TAG, {}, None, True)] + [(k, m, why, True) for k, (m, why) in mutants.items()]
        cases.append(("neg_syn_no_run_stats", {}, "no run_stats.csv beside the log", False))
        for name, mut, why, with_rs in cases:
            body, rs_csv = synth(src, rs_rows, mut)
            d = pathlib.Path(td) / name
            d.mkdir()
            if with_rs:
                (d / "run_stats.csv").write_text(rs_csv, encoding="utf-8", newline="")
            p = d / (name + ".log")
            p.write_text(body, encoding="utf-8")
            res[name] = gate_file(p, TAG)
            if why is not None and why not in res[name]:
                res[name] = "WRONG-REASON (wanted %r): %s" % (why, res[name])
    for k, v in res.items():
        print(k, "->", v[:700])
    ok = all("GATE_FAIL" in v and not v.startswith("WRONG-REASON") for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_")) \
        and all("pos_" + tg in res for tg in REGRESS)
    if not ok:
        if GATE.read_text(encoding="utf-8") == t2:
            GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
            raise SystemExit("self-test failed; gate.py restored from " + bak.name)
        raise SystemExit("self-test failed AND gate.py was modified by someone else meanwhile; NOT restored, check by hand")
    print("gate entry for %s added (backup %s); need entries now %d" % (TAG, bak.name, len(need_keys(now))))


if __name__ == "__main__":
    main()
