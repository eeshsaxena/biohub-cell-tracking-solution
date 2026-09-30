#!/usr/bin/env python3
r"""Gate entry for t65b25r70ff (scratch_kernels/build_t65b25r70ff.py) = t65b25r70 (t6stk3 body + relink tight 6.5 +
learned bonus 2.5 + t6r70's raw-ILP override "rawlink" 0.70; representative 0.954) + the IMGFLOW write-time repair,
placed after the rawlink override exactly as build_t6r70ff.py placed it. Run from the project root: it backs up
ops/gate.py (gate.py.bak_t65b25r70ff), patches it, self-tests, and restores the backup if any self-test fails.
Dry run: T65B25R70FF_GATE=<copy of gate.py> python ops/add_t65b25r70ff_gate.py

t65b25r70ff must prove on the visible run (4 movies):
  * need['t65b25r70'] (read out of gate.py with ast) minus its ARM_XENV line: STK3V, STK3B 2.5 + echo, T65H 6.5 + echo,
    LCEFR runtime counters, base line-fit echoes, the six rawlink patterns (cell-2 enabled line at 0.7, the echo, four
    per-movie ARM_RAWLINK lines with accepted >= 1);
  * need['t6stk3ff']'s five ARM_FLOWFIX patterns (read with ast): 'ARM_FLOWFIX enabled=True TF=5.0 KEEP=3.5 GATE=4.5
    MIN_DET=5 ENDS=1 threads=N deadline_s=34200' and one 'ARM_FLOWFIX [<movie>] status=ok ...' line per movie;
  * the cell-0 identity line ARM_XENV tag=t65b25r70ff TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5
    GATE=4.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200 (replaces t65b25r70's XENV line);
  * the rawlink structural checks, as for t65b25r70: the tag joins RL_TAGS (per-movie line after FINAL, degree <= 1/2,
    division count unchanged, anchor + accepted - replaced == final, change-fraction window, total-accepted window) and
    the orphan cap (<= 50 per movie, <= 150 total new_isolated);
  * a per-movie FLOWFIX cross-check (t6stk3ff's arithmetic, re-anchored on the override's output): the status=ok line
    comes AFTER the movie's ARM_RAWLINK line; flowfix edges A->B with A == ARM_RAWLINK final= and B == A + bridged -
    dups; divs X->X with X == safe divisions added; max_in <= 1; secs <= 20; cell-10 written nodes/edges/divisions ==
    (FINAL nodes, B, safe divisions added); run_stats (nodes, edges, safe_divisions_added) == (FINAL nodes, B, safe
    divisions), rawlink_final_edges == A, flowfix_status ok with changed/bridged/dups equal to the log line, line-fit
    smoothed + skipped == nodes; changed > 0 on at least one visible movie. No float digests are pinned;
  * sv_mark SV_ARM_HSG200 inside the dict literal (>= 4 lines before 'Prediction completed'); FINAL within 15% of REF;
  * forbidden: everything forbid['t65b25r70'] forbids (resolved with ast) with three rewrites: its XENV forbid allows
    only tag=t65b25r70ff, its bare 'ARM_FLOWFIX' forbid is dropped and its ARM_ allowlist gains FLOWFIX; PLUS
    forbid['t6stk3ff']'s two FLOWFIX failure forbids (a FALLBACK/SKIPPED movie, enabled=False).
Self-tests: the t65b25r70 and t6stk3ff logs must FAIL as t65b25r70ff; t65b25r70 / ourvzlb25r70 / t65b25 / t65b20 /
t6r70 / t6stk3 / t6sr / t6stk3ff must still PASS as themselves; every need entry present before the patch (incl.
t65b25r70, ourvzlb25r70, t65b20d04, t70b25, t675b25 and any concurrently added one) must still exist. A SYNTHETIC
t65b25r70ff log (t65b25r70's log + FLOWFIX prints, cell-10 edges and run_stats edges moved by `bridged`) must PASS and
mutants must FAIL on their own message.
"""
import ast
import csv
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("T65B25R70FF_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T65B25R70FF_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t65b25r70ff"
BASE_TAG = "t65b25r70"
FF_TAG = "t6stk3ff"
OLD_XENV = r"ARM_XENV tag=t65b25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 LCEFR=kept"
XENV = (r"ARM_XENV tag=t65b25r70ff TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 FLOWFIX=1 TF=5\.0 KEEP=3\.5 GATE=4\.5 "
        r"MIN_DET=5 ENDS=1 DEADLINE_S=34200")
OLD_XFORBID = r"ARM_XENV tag=(?!t65b25r70 )"
NEW_XFORBID = r"ARM_XENV tag=(?!t65b25r70ff )"
OLD_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK)\b)[A-Z0-9]+"
NEW_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK|FLOWFIX)\b)[A-Z0-9]+"
FF_FORBID = [r"ARM_FLOWFIX \[\w+\] (?:FALLBACK|SKIPPED)", r"ARM_FLOWFIX enabled=False"]
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
EXPECT_ENTRIES = ("t65b25r70", "ourvzlb25r70", "t65b20d04", "t70b25", "t675b25")
REGRESS = ("t65b25r70", "ourvzlb25r70", "t65b25", "t65b20", "t6r70", "t6stk3", "t6sr", "t6stk3ff")
XENV_LINE = ("ARM_XENV tag=t65b25r70ff TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 "
             "ENDS=1 DEADLINE_S=34200")
ENABLED_LINE = "ARM_FLOWFIX enabled=True TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 threads=4 deadline_s=34200"
# real prints that the new forbid list must NOT hit (t6stk3ff / t65b25r70 visible runs)
GOOD_LINES = [
    ENABLED_LINE, XENV_LINE,
    "ARM_FLOWFIX [44b6_0113de3b] status=ok windows=792 flagged=62 acted=37 changed=179 bridged=41 dups=0 "
    "edges=24883->24924 divs=36->36 max_in=1 secs=8.3 elapsed_h=0.40",
    "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
    '  "rawlink_min_prob": 0.7,',
    "ARM_RAWLINK [44b6_0113de3b] min_prob=0.7 candidates=325 accepted=325 replaced=301 anchor=24890 final=24914 "
    "max_in=1 max_out=2 divs=34->34 divs_shielded=2 blocked_parent=0 blocked_daughter=2 below_min=43 replaced_raw=0 "
    "new_isolated=6",
    "ARM_STK3B learned_bonus=2.5", "ARM_T65H tight_um=6.5", "ARM_LCEFR patch applied to predictor"]
BAD_LINES = ["ARM_FLOWFIX [44b6_0113de3b] FALLBACK error=ValueError: x", "ARM_FLOWFIX [6bba_05b6850b] SKIPPED deadline",
             "ARM_FLOWFIX enabled=False TF=5.0", "ARM_XENV tag=t65b25r70 TIGHT", "ARM_XENV tag=t6stk3ff FLOWFIX=1",
             "ARM_RAWLINK min_prob=-1.0 enabled=False rule=x", "ARM_RAWLINK [44b6_0113de3b] min_prob=0.3 candidates=1 ",
             '"rawlink_min_prob": 0.3,', '"motion_relink_learned_bonus": 1.6,', '"motion_relink_tight_um": 6.0,',
             "ARM_T60H tight_um=6.0", "Traceback (most recent call last)", "ARM_FLOWLINK enabled=True",
             "ARM_FLOWCUT x", "SV_ARM_HSG250 nodes=1"]

XCHECK = r'''# --- t65b25r70ff (ops/add_t65b25r70ff_gate.py): t65b25r70 + ARM_FLOWFIX after the rawlink override. Per movie the
# repair must start from the override's own output (flowfix edges A == ARM_RAWLINK final=) and write B = A + bridged -
# dups; divisions unchanged (== safe divisions added), in-degree <= 1, <= 20 s/movie; cell-10 written nodes/edges/
# divisions == (FINAL nodes, B, safe divisions added); run_stats agrees (edges == B, rawlink_final_edges == A,
# flowfix_status ok, changed/bridged/dups as logged, line-fit smoothed + skipped == nodes); changed > 0 somewhere.
if "t65b25r70ff" in tags:
    import csv, os
    _ffxfin, _ffxsd, _ffxdv, _ffxrl = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _ffxfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _ffxsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _ffxdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for _ffxm in re.finditer(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _ffxrl.setdefault(_ffxm.group(1), (int(_ffxm.group(2)), _ffxm.start()))
    _ffxrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _ffxrs = None
    if os.path.isfile(_ffxrsp):
        with open(_ffxrsp, newline="", encoding="utf-8") as fh:
            _ffxrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t65b25r70ff: no run_stats.csv beside the log, so the written counts and flowfix counters are unproven")
    _ffxchg = []
    for d in sorted(REF):
        if d not in _ffxfin or d not in _ffxsd or d not in _ffxrl:
            fails.append(f"t65b25r70ff {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _ffxm = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                          r"bridged=(\d+) dups=(\d+) edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _ffxm:
            fails.append(f"t65b25r70ff {d}: no ARM_FLOWFIX status=ok line")
            continue
        _ffxg = [int(v) for v in _ffxm.groups()[:11]]
        _ffxch, _ffxbr, _ffxdu, _ffxa0, _ffxa1, _ffxv0, _ffxv1, _ffxmi = _ffxg[3:11]
        _ffxn, _ffxs = _ffxfin[d][0], _ffxsd[d]
        _ffxchg.append(_ffxch)
        if _ffxm.start() < _ffxrl[d][1] or _ffxm.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"t65b25r70ff {d}: ARM_FLOWFIX line is not after the movie's FINAL and ARM_RAWLINK lines: the "
                         "repair must act on the override's output")
        if _ffxa0 != _ffxrl[d][0]:
            fails.append(f"t65b25r70ff {d}: flowfix input edges {_ffxa0} != ARM_RAWLINK final={_ffxrl[d][0]}: the repair "
                         "did not start from the override's output")
        if _ffxa1 != _ffxa0 + _ffxbr - _ffxdu:
            fails.append(f"t65b25r70ff {d}: flowfix edges {_ffxa0}->{_ffxa1} inconsistent with {_ffxa0} + bridged "
                         f"{_ffxbr} - dups {_ffxdu}")
        if _ffxv0 != _ffxv1 or _ffxv1 != _ffxs or _ffxmi > 1:
            fails.append(f"t65b25r70ff {d}: flowfix divisions {_ffxv0}->{_ffxv1} (want {_ffxs}) or in-degree {_ffxmi}")
        if float(_ffxm.group(12)) > 20.0:
            fails.append(f"t65b25r70ff {d}: flowfix {_ffxm.group(12)} s > 20 s/movie (hidden overhead > ~66 min)")
        _ffxwant = (_ffxn, _ffxa1, _ffxs)
        if _ffxdv.get(d) != _ffxwant:
            fails.append(f"t65b25r70ff {d} written nodes/edges/divisions {_ffxdv.get(d)} != (FINAL nodes, flowfix B, "
                         f"safe divisions) {_ffxwant}")
        if _ffxrs is not None:
            _ffxr = _ffxrs.get(d) or {}
            try:
                _ffxgot = tuple(int(float(_ffxr[k])) for k in (
                    "nodes", "edges", "safe_divisions_added", "linefit_smoothed_nodes", "linefit_skipped_nodes",
                    "rawlink_final_edges", "flowfix_changed", "flowfix_bridged", "flowfix_dups"))
                _ffxst = _ffxr["flowfix_status"]
            except (KeyError, TypeError, ValueError):
                _ffxgot, _ffxst = None, None
            if _ffxgot is None or _ffxgot[:3] != _ffxwant or _ffxgot[3] + _ffxgot[4] != _ffxn \
                    or _ffxgot[5] != _ffxa0 or _ffxgot[6:] != (_ffxch, _ffxbr, _ffxdu) or _ffxst != "ok":
                fails.append(f"t65b25r70ff {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped, "
                             f"rawlink_final_edges, flowfix changed/bridged/dups) {_ffxgot} status {_ffxst} inconsistent "
                             f"with {_ffxwant} / rawlink final {_ffxa0} / flowfix {(_ffxch, _ffxbr, _ffxdu)} ok")
    if not _ffxchg or max(_ffxchg) == 0:
        fails.append("t65b25r70ff: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
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
    watch = {BASE_TAG, FF_TAG, TAG}
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


def insert_after_line(txt, needle, add):
    i = txt.find(needle)
    if i < 0:
        raise SystemExit("synthetic: %r not in the source log" % needle)
    j = txt.index("\n", i) + 1
    return txt[:j] + add + txt[j:]


def insert_before_line(txt, needle, add):
    i = txt.find(needle)
    if i < 0:
        raise SystemExit("synthetic: %r not in the source log" % needle)
    j = txt.rfind("\n", 0, i) + 1
    return txt[:j] + add + txt[j:]


def patch(t):
    """Return the patched gate text for source text t (pure function of t)."""
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    # ---- need
    base = list(need_of(t, BASE_TAG))
    ffn = list(need_of(t, FF_TAG))
    if base.count(OLD_XENV) != 1 or sum("ARM_XENV" in p for p in base) != 1:
        raise SystemExit("need['t65b25r70'] does not carry exactly one XENV line: %r" % base)
    if any("FLOWFIX" in p for p in base):
        raise SystemExit("need['t65b25r70'] unexpectedly pins FLOWFIX markers")
    ff = [p for p in ffn if p.startswith("ARM_FLOWFIX")]
    want_ff = [r"ARM_FLOWFIX enabled=True TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 threads=\d+ deadline_s=34200"] + [
        r"ARM_FLOWFIX \[%s\] status=ok windows=\d+ flagged=\d+ acted=\d+ changed=\d+ " % d for d in MOVIES]
    if ff != want_ff:
        raise SystemExit("need['t6stk3ff'] FLOWFIX patterns are not the five this installer was written against: %r" % ff)
    pats = [p for p in base if p != OLD_XENV] + ff + [XENV]
    if len(pats) != len(base) + 5 or len(set(pats)) != len(pats) or pats.count(XENV) != 1:
        raise SystemExit("expected t65b25r70's %d patterns - XENV + 5 FLOWFIX + XENV, got %r" % (len(base), pats))
    for stale in (r"1\.6", r"6\.0", "T60H", "tag=t65b25r70 ", "tag=t6stk3ff"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    if sum("RAWLINK" in p or "rawlink" in p for p in pats) != 7:  # 6 rawlink + the XENV's RAWLINK=0.70
        raise SystemExit("rawlink patterns not carried over intact: %r" % pats)
    # ---- forbid
    fr = forbid_of(t, BASE_TAG)
    ffb = forbid_of(t, FF_TAG)
    if fr.count(OLD_XFORBID) != 1 or fr.count(OLD_ALLOW) != 1 or fr.count("ARM_FLOWFIX") != 1:
        raise SystemExit("forbid['t65b25r70'] lacks its XENV forbid / ARM_ allowlist / ARM_FLOWFIX exactly once: %r" % fr)
    for p in FF_FORBID:
        if ffb.count(p) != 1:
            raise SystemExit("forbid['t6stk3ff'] lacks %r" % p)
    forbid = [NEW_XFORBID if p == OLD_XFORBID else NEW_ALLOW if p == OLD_ALLOW else p for p in fr if p != "ARM_FLOWFIX"]
    forbid += [p for p in FF_FORBID if p not in forbid]
    for line in GOOD_LINES:
        hit = [p for p in forbid if re.search(p, line)]
        if hit:
            raise SystemExit("new forbid list hits a legitimate print %r via %r" % (line[:60], hit))
    for line in BAD_LINES:
        if not any(re.search(p, line) for p in forbid):
            raise SystemExit("new forbid list does not catch %r" % line)
    # ---- patch text
    comment = ("        # --- t65b25r70ff: t65b25r70 (t6stk3 + tight 6.5 + bonus 2.5 + raw-ILP override 0.70; representative 0.954)\n"
               "        # + IMGFLOW write-time repair after the override, as build_t6r70ff.py placed it on t6r70.\n"
               "        # = need['t65b25r70'] minus its XENV + need['t6stk3ff']'s five ARM_FLOWFIX patterns + this arm's XENV\n"
               "        # (build_t65b25r70ff.py; ops/add_t65b25r70ff_gate.py). RL_TAGS + orphan cap + the flowfix cross-check\n"
               "        # below (A == rawlink final=, B == A + bridged - dups == written) carry the bookkeeping.\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
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
    t2 = t2.replace(anchors["svtags"], XCHECK + anchors["svtags"], 1)
    # ---- structural re-checks on the patched text
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
    """t65b25r70's visible log turned into a plausible t65b25r70ff log (+ matching run_stats rows)."""
    mut = mut or {}
    s = src
    old_x = "ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept"
    if s.count(old_x) != 1:
        raise SystemExit("synthetic: t65b25r70 XENV line not exactly once in its log")
    s = s.replace(old_x, XENV_LINE)
    s = insert_after_line(s, XENV_LINE, (mut.get("enabled", ENABLED_LINE)) + "\n")
    rows = {r["dataset"]: dict(r) for r in rs_rows}
    for k, d in enumerate(MOVIES):
        m = re.search(r"ARM_RAWLINK \[%s\] .*? final=(\d+) " % d, s)
        a0 = int(m.group(1))
        sd = int(re.search(r"\[%s\] after safe-division repair: [^\n]*?\badded=(\d+)" % d, s).group(1))
        ch, br, du = mut.get("changed", (40 + k)), (3 + k), mut.get("dups", 0)
        a_in = a0 + mut.get("a0_off", 0)
        a1 = a_in + br - du
        if mut.get("arith_off"):
            a1 += 1
        line = ("ARM_FLOWFIX [%s] status=ok windows=792 flagged=40 acted=30 changed=%d bridged=%d dups=%d edges=%d->%d "
                "divs=%d->%d max_in=1 secs=%s elapsed_h=0.40\n"
                % (d, ch, br, du, a_in, a1, sd, sd + mut.get("div_off", 0), mut.get("secs", "8.1")))
        if mut.get("skip_movie") == d:
            pass
        elif mut.get("before_rawlink"):
            s = insert_before_line(s, "ARM_RAWLINK [%s] " % d, line)
        else:
            s = insert_after_line(s, "ARM_RAWLINK [%s] " % d, line)
        if not mut.get("no_written_update"):
            s, n = re.subn(r"(?m)^(\s+%s: nodes=\d+ edges=)(\d+)( divisions=\d+\s*)$" % d,
                           lambda mm: mm.group(1) + str(a1) + mm.group(3), s, count=1)
            if n != 1:
                raise SystemExit("synthetic: cell-10 line for %s not found" % d)
        r = rows[d]
        r["edges"] = str(a1)
        r.update(flowfix_status=mut.get("rs_status", "ok"), flowfix_windows="792", flowfix_flagged="40",
                 flowfix_acted="30", flowfix_changed=str(ch), flowfix_bridged=str(br), flowfix_dups=str(du),
                 flowfix_secs="8.1")
    for extra in mut.get("extra_lines", []):
        s = insert_before_line(s, "Prediction completed", extra + "\n") if "Prediction completed" in s else s + extra + "\n"
    out = io.StringIO()
    fields = list(rs_rows[0].keys()) + [k for k in rows[MOVIES[0]] if k not in rs_rows[0]]
    w = csv.DictWriter(out, fieldnames=fields)
    w.writeheader()
    for r in rs_rows:
        w.writerow(rows[r["dataset"]])
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
    missing = [k for k in EXPECT_ENTRIES + tuple(sorted(need_keys(t))) if k not in need_keys(now)]
    res = {}
    if missing:
        res["neg_entries_missing"] = "GATE_FAIL: need entries missing after the patch: %r" % missing
    # ---- self-tests on real logs
    res["neg_t65b25r70_as_" + TAG] = gate("out_t65b25r70", TAG)
    res["neg_t6stk3ff_as_" + TAG] = gate("out_t6stk3ff", TAG)
    for tg in REGRESS:
        if list((ROOT / "data").glob("out_%s/*.log" % tg)):
            res["pos_" + tg] = gate("out_" + tg, tg)
    own = list((ROOT / "data").glob("out_%s/*.log" % TAG))
    if own:
        res["own_" + TAG] = gate("out_" + TAG, TAG)
    # ---- synthetic positive + mutants from t65b25r70's visible log (+ its run_stats.csv)
    src_dir = ROOT / "data" / "out_t65b25r70"
    src = log_text(next(src_dir.glob("*.log")))
    with open(src_dir / "run_stats.csv", newline="", encoding="utf-8") as fh:
        rs_rows = list(csv.DictReader(fh))
    mutants = {
        "neg_syn_fallback_line": ({"extra_lines": ["ARM_FLOWFIX [6bba_05b6850b] FALLBACK error=ValueError: boom"]}, "log contains"),
        "neg_syn_enabled_false": ({"enabled": ENABLED_LINE.replace("enabled=True", "enabled=False")}, "log contains"),
        "neg_syn_input_not_rawlink_final": ({"a0_off": -1}, "did not start from the override's output"),
        "neg_syn_edge_arithmetic": ({"arith_off": True}, "inconsistent with"),
        "neg_syn_before_rawlink": ({"before_rawlink": True}, "is not after the movie's FINAL and ARM_RAWLINK"),
        "neg_syn_written_mismatch": ({"no_written_update": True}, "written nodes/edges/divisions"),
        "neg_syn_divs_changed": ({"div_off": 1}, "flowfix divisions"),
        "neg_syn_slow": ({"secs": "25.0"}, "s > 20 s/movie"),
        "neg_syn_never_fired": ({"changed": 0}, "changed 0 edges on every visible movie"),
        "neg_syn_missing_movie": ({"skip_movie": "44b6_0b24845f"}, "no ARM_FLOWFIX status=ok line"),
        "neg_syn_old_xenv": ({"extra_lines": ["ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept"]}, "log contains"),
        "neg_syn_rawlink_disabled": ({"extra_lines": ["ARM_RAWLINK min_prob=-1.0 enabled=False rule=raw_ilp_override_final_divisions_protected"]}, "log contains"),
        "neg_syn_flowlink_marker": ({"extra_lines": ["ARM_FLOWLINK enabled=True"]}, "log contains"),
        "neg_syn_bonus16": ({"extra_lines": ['"motion_relink_learned_bonus": 1.6,']}, "log contains"),
        "neg_syn_runstats_status": ({"rs_status": "fallback_error"}, "run_stats"),
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
