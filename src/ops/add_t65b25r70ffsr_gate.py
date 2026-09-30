#!/usr/bin/env python3
r"""Gate entry for t65b25r70ffsr (scratch_kernels/build_t65b25r70ffsr.py) = t65b25r70 (t6stk3 body + relink tight 6.5 +
learned bonus 2.5 + raw-ILP override "rawlink" 0.70; representative 0.954) with BOTH stacked additions: the IMGFLOW
write-time repair after the override (t65b25r70ff) and the short-track rescue armed unconditionally (t65b25r70sr).
Run from the project root: it backs up ops/gate.py (gate.py.bak_t65b25r70ffsr), patches it, self-tests, and restores
the backup if any self-test fails.
Dry run: T65B25R70FFSR_GATE=<copy of gate.py> python ops/add_t65b25r70ffsr_gate.py

t65b25r70ffsr must prove on the visible run (4 movies) the UNION of both entries' requirements:
  * need: need['t65b25r70ff'] (read with ast) minus its XENV (t65b25r70's linker / LCEFR / line-fit / six rawlink
    patterns + the five ARM_FLOWFIX patterns) + need['t65b25r70sr']'s own additions minus its XENV (t6sr's
    "deepcenter_safe_div_threshold": 0.25 echo + the LIVE cell-2 echo "short_track_rescue_trigger_removed_frac": 0.0)
    + this arm's XENV. Both parents are checked to be need['t65b25r70'] minus its XENV plus exactly those additions;
  * forbid: forbid['t65b25r70ff'] (resolved with ast; already t65b25r70's with the bare ARM_FLOWFIX dropped, FLOWFIX in
    the ARM_ allowlist, FALLBACK/SKIPPED/enabled=False forbids) with its XENV forbid rewritten to allow only
    tag=t65b25r70ffsr, PLUS forbid['t65b25r70sr']'s two rescue forbids (trigger echo != 0.0, adaptive rescue false).
    sr's bare 'ARM_FLOWFIX' forbid is NOT carried (this arm prints ARM_FLOWFIX by design);
  * RL_TAGS + orphan cap (rawlink structural checks, as for both parents); sv_mark SV_ARM_HSG200 in the dict literal;
    FINAL within 15% of REF;
  * per-movie cross-check = the live t65b25r70ff block (renamed; flowfix A == ARM_RAWLINK final=, B == A + bridged -
    dups, divisions unchanged, secs <= 20, written (nodes, edges, divisions) == (FINAL nodes, B, safe divisions),
    run_stats agrees incl. flowfix_* and rawlink_final_edges, changed > 0 somewhere) + the live t65b25r70sr rescue
    receipts (renamed; triggered == 1 on all four movies, components <= nodes <= budget, components > 0 somewhere)
    + a POST-RESCUE CHAIN check. The rescue runs INSIDE the short-track filter (filter_output_graph), i.e. BEFORE
    FINAL, the override and the repair, so every count the ff arithmetic reads (FINAL nodes, rawlink final=, written)
    is already post-rescue and the ff arithmetic applies unchanged. The chain makes that explicit per movie:
    "after short-track filtering" (nodes, edges) == FINAL; ARM_RAWLINK anchor= == FINAL edges (the override starts
    from the post-rescue graph); run_stats short_track_nodes_removed / edges_removed == prune-isolated line - FINAL and
    short_track_components_removed == the short-track line's components_removed (the rescued components stayed in).
    No float digests are pinned; no counts are pinned to another run.
Self-tests: the t65b25r70ff, t65b25r70sr and t65b25r70 logs must FAIL as t65b25r70ffsr; t65b25r70 / t65b25r70ff /
t65b25r70sr / mixyx50r70 / ourvzlb25r70 / t65b25 / t6stk3 / t6r70 must still PASS as themselves; every need entry
present before the patch must still exist. A SYNTHETIC t65b25r70ffsr log (t65b25r70sr's REAL visible log + run_stats,
i.e. real post-rescue counts, with this XENV and FLOWFIX prints injected after each ARM_RAWLINK line, written edges and
run_stats edges moved by `bridged`, flowfix_* columns filled) must PASS and every mutant must FAIL on its own message.
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

ROOT = pathlib.Path(os.environ.get("T65B25R70FFSR_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T65B25R70FFSR_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t65b25r70ffsr"
BASE_TAG = "t65b25r70"
FF_TAG = "t65b25r70ff"
SR_TAG = "t65b25r70sr"
BASE_XENV = r"ARM_XENV tag=t65b25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 LCEFR=kept"
FF_XENV = (r"ARM_XENV tag=t65b25r70ff TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 FLOWFIX=1 TF=5\.0 KEEP=3\.5 GATE=4\.5 "
           r"MIN_DET=5 ENDS=1 DEADLINE_S=34200")
SR_XENV = r"ARM_XENV tag=t65b25r70sr TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 SR=armed"
XENV = (r"ARM_XENV tag=t65b25r70ffsr TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 FLOWFIX=1 TF=5\.0 KEEP=3\.5 GATE=4\.5 "
        r"MIN_DET=5 ENDS=1 DEADLINE_S=34200 SR=armed")
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
FF_ADD = [r"ARM_FLOWFIX enabled=True TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 threads=\d+ deadline_s=34200"] + [
    r"ARM_FLOWFIX \[%s\] status=ok windows=\d+ flagged=\d+ acted=\d+ changed=\d+ " % d for d in MOVIES]
SR_ADD = [r'"deepcenter_safe_div_threshold": 0\.25(?!\d)', r'"short_track_rescue_trigger_removed_frac": 0\.0(?!\d)']
FF_XFORBID = r"ARM_XENV tag=(?!t65b25r70ff )"
SR_XFORBID = r"ARM_XENV tag=(?!t65b25r70sr )"
BASE_XFORBID = r"ARM_XENV tag=(?!t65b25r70 )"
NEW_XFORBID = r"ARM_XENV tag=(?!t65b25r70ffsr )"
BASE_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK)\b)[A-Z0-9]+"
FF_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK|FLOWFIX)\b)[A-Z0-9]+"
FF_FORBID = [r"ARM_FLOWFIX \[\w+\] (?:FALLBACK|SKIPPED)", r"ARM_FLOWFIX enabled=False"]
SR_FORBID = [r'"short_track_rescue_trigger_removed_frac": (?!0\.0(?!\d))', r'"adaptive_short_track_rescue": false']
EXPECT_ENTRIES = ("t65b25r70", "t65b25r70ff", "t65b25r70sr", "mixyx50r70", "ourvzlb25r70", "t65b25", "t6stk3", "t6r70")
REGRESS = ("t65b25r70", "t65b25r70ff", "t65b25r70sr", "mixyx50r70", "ourvzlb25r70", "t65b25", "t6stk3", "t6r70")
NEG_REAL = ("t65b25r70ff", "t65b25r70sr", "t65b25r70")
XENV_LINE = ("ARM_XENV tag=t65b25r70ffsr TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 "
             "ENDS=1 DEADLINE_S=34200 SR=armed")
SR_XENV_LINE = "ARM_XENV tag=t65b25r70sr TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 SR=armed"
ENABLED_LINE = "ARM_FLOWFIX enabled=True TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 threads=4 deadline_s=34200"
GOOD_LINES = [
    XENV_LINE, ENABLED_LINE,
    "ARM_FLOWFIX [44b6_0113de3b] status=ok windows=792 flagged=62 acted=37 changed=30 bridged=17 dups=0 "
    "edges=24914->24931 divs=34->34 max_in=1 secs=8.0 elapsed_h=0.38",
    "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
    '  "rawlink_min_prob": 0.7,',
    "ARM_RAWLINK [44b6_0113de3b] min_prob=0.7 candidates=327 accepted=327 replaced=301 anchor=24984 final=25010 "
    "max_in=1 max_out=2 divs=34->34 divs_shielded=2 blocked_parent=0 blocked_daughter=2 below_min=43 replaced_raw=0 "
    "new_isolated=6",
    '  "short_track_rescue_trigger_removed_frac": 0.0,', '  "adaptive_short_track_rescue": true,',
    '  "deepcenter_safe_div_threshold": 0.25,', "  SHORT_TRACK_RESCUE_MIN_MEAN_EDGE_PROB    0.88",
    "ARM_STK3B learned_bonus=2.5", "ARM_T65H tight_um=6.5", "ARM_LCEFR patch applied to predictor"]
BAD_LINES = ["ARM_FLOWFIX [44b6_0113de3b] FALLBACK error=ValueError: x", "ARM_FLOWFIX [6bba_05b6850b] SKIPPED deadline",
             "ARM_FLOWFIX enabled=False TF=5.0", "ARM_XENV tag=t65b25r70 TIGHT", "ARM_XENV tag=t65b25r70ff TIGHT",
             "ARM_XENV tag=t65b25r70sr TIGHT", "ARM_XENV tag=t6stk3ff FLOWFIX=1",
             "ARM_XENV tag=t6sr BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=0.0",
             '  "short_track_rescue_trigger_removed_frac": 0.1,', '"adaptive_short_track_rescue": false,',
             "ARM_RAWLINK min_prob=-1.0 enabled=False rule=x", "ARM_RAWLINK [44b6_0113de3b] min_prob=0.3 candidates=1 ",
             '"rawlink_min_prob": 0.3,', '"motion_relink_learned_bonus": 1.6,', '"motion_relink_tight_um": 6.0,',
             "ARM_T60H tight_um=6.0", "Traceback (most recent call last)", "ARM_FLOWLINK enabled=True",
             "ARM_FLOWCUT x", "SV_ARM_HSG250 nodes=1"]

CHAIN = r'''    # post-rescue chain (ops/add_t65b25r70ffsr_gate.py). The rescue runs INSIDE the short-track filter, i.e. before
    # FINAL, the override and the repair, so every count the flowfix arithmetic above reads is already post-rescue.
    # Tie the links explicitly per movie: short-track line == FINAL; ARM_RAWLINK anchor= == FINAL edges (the override
    # starts from the post-rescue graph); run_stats short_track_nodes/edges_removed == prune-isolated line - FINAL and
    # short_track_components_removed == the short-track line's components_removed (rescued components stayed in).
    _fsxst, _fsxpr, _fsxan = {}, {}, {}
    for d, n_, e_, c_ in re.findall(r"\[(\w+)\] after short-track filtering: (\d+) nodes, (\d+) edges "
                                    r"\(components_removed=(\d+)\)", txt):
        _fsxst.setdefault(d, (int(n_), int(e_), int(c_)))
    for d, n_, e_ in re.findall(r"\[(\w+)\] after division-geometry-filter\+prune-isolated: (\d+) nodes, (\d+) edges", txt):
        _fsxpr.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? anchor=(\d+) ", txt):
        _fsxan.setdefault(d, int(a_))
    for d in sorted(REF):
        _fsxf = _fsxfin.get(d)
        if _fsxf is None or d not in _fsxst or d not in _fsxpr or d not in _fsxan:
            fails.append(f"t65b25r70ffsr {d}: missing FINAL / short-track / prune-isolated / ARM_RAWLINK anchor= line")
            continue
        if _fsxst[d][:2] != _fsxf:
            fails.append(f"t65b25r70ffsr {d}: short-track (post-rescue) nodes/edges {_fsxst[d][:2]} != FINAL {_fsxf}")
        if _fsxan[d] != _fsxf[1]:
            fails.append(f"t65b25r70ffsr {d}: ARM_RAWLINK anchor={_fsxan[d]} != FINAL edges {_fsxf[1]}: the override did "
                         "not start from the post-rescue graph")
        if _fsxrs is not None:
            _fsxrow = _fsxrs.get(d) or {}
            try:
                _fsxrm = tuple(int(float(_fsxrow[k])) for k in ("short_track_nodes_removed", "short_track_edges_removed",
                                                              "short_track_components_removed"))
            except (KeyError, TypeError, ValueError):
                _fsxrm = None
            _fsxrw = (_fsxpr[d][0] - _fsxf[0], _fsxpr[d][1] - _fsxf[1], _fsxst[d][2])
            if _fsxrm != _fsxrw:
                fails.append(f"t65b25r70ffsr {d}: run_stats short_track_nodes/edges/components_removed {_fsxrm} != "
                             f"(prune-isolated - FINAL, components_removed) {_fsxrw}")
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
    watch = {BASE_TAG, FF_TAG, SR_TAG, TAG}
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


def xcheck_from_live(t):
    """The live t65b25r70ff block + the live t65b25r70sr rescue receipts, renamed for this tag, + the chain block."""
    s = t.index("# --- t65b25r70ff (ops/add_t65b25r70ff_gate.py)")
    e = t.index('if "t65b25r70ff" in tags:\n', s)
    ff = t[e:t.index("\n# --- ", e) + 1]
    if ff.count("t65b25r70ff") != 12 or ff.count("_ffx") != 106 or "_fsx" in ff or ff.count("_ffxrs = None") != 1 \
            or "\n#" in ff.rstrip("\n") or not ff.rstrip("\n").endswith("the repair never fired\")"):
        raise SystemExit("the live t65b25r70ff cross-check block is not the one this installer was written against")
    s2 = t.index("    # rescue receipts (ops/add_t65b25r70sr_gate.py)")
    if not t.index('if "t65b25r70sr" in tags:\n') < s2:
        raise SystemExit("the rescue receipts are not inside the t65b25r70sr block")
    rs = t[s2:t.index("\n# --- ", s2) + 1]
    if rs.count("t65b25r70sr") != 5 or rs.count("_srx") != 18 or "_fsx" in rs or not rs.startswith("    # rescue") \
            or rs.count("if _srxrs is not None:") != 1:
        raise SystemExit("the live t65b25r70sr rescue-receipt block is not the one this installer was written against")
    ff = ff.replace("t65b25r70ff", TAG).replace("_ffx", "_fsx")
    rs = rs.replace("t65b25r70sr", TAG).replace("_srx", "_fsx")
    head = ("# --- t65b25r70ffsr (ops/add_t65b25r70ffsr_gate.py): t65b25r70 + ARM_FLOWFIX after the override + short-track\n"
            "# rescue armed (trigger 0.0). = the live t65b25r70ff cross-check (renamed: A == rawlink final=, B == A + bridged\n"
            "# - dups == written, run_stats flowfix_*) + the live t65b25r70sr rescue receipts (renamed) + the post-rescue\n"
            "# chain (short-track == FINAL, rawlink anchor == FINAL edges, run_stats removed == prune - FINAL).\n")
    return head + ff + rs + CHAIN


def patch(t):
    """Return the patched gate text for source text t (pure function of t)."""
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    # ---- need: union of both parents, each re-derived against need['t65b25r70']
    base, ffn, srn = list(need_of(t, BASE_TAG)), list(need_of(t, FF_TAG)), list(need_of(t, SR_TAG))
    if base.count(BASE_XENV) != 1 or ffn.count(FF_XENV) != 1 or srn.count(SR_XENV) != 1:
        raise SystemExit("a parent need entry does not carry exactly its one XENV pattern")
    body = [p for p in base if p != BASE_XENV]
    if [p for p in ffn if p != FF_XENV] != body + FF_ADD:
        raise SystemExit("need['t65b25r70ff'] != need['t65b25r70'] - XENV + the five FLOWFIX patterns: %r" % ffn)
    if [p for p in srn if p != SR_XENV] != body + SR_ADD:
        raise SystemExit("need['t65b25r70sr'] != need['t65b25r70'] - XENV + deepcenter echo + trigger echo: %r" % srn)
    pats = [p for p in ffn if p != FF_XENV] + [p for p in srn if p not in ffn and p != SR_XENV] + [XENV]
    if pats != body + FF_ADD + SR_ADD + [XENV] or len(set(pats)) != len(pats):
        raise SystemExit("union need list is not body + FLOWFIX + rescue echoes + XENV: %r" % pats)
    for stale in (r"1\.6", r"6\.0", "T60H", "tag=t65b25r70 ", "tag=t65b25r70ff ", "tag=t65b25r70sr ", "tag=t6sr",
                  "tag=t6stk3ff"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    if sum("RAWLINK" in p or "rawlink" in p for p in pats) != 7:  # 6 rawlink + the XENV's RAWLINK=0.70
        raise SystemExit("rawlink patterns not carried over intact: %r" % pats)
    # ---- forbid: ff's list with the XENV forbid rewritten + sr's two rescue forbids
    fb, ffb, srb = forbid_of(t, BASE_TAG), forbid_of(t, FF_TAG), forbid_of(t, SR_TAG)
    if [p for p in fb if p not in ffb] != [BASE_XFORBID, BASE_ALLOW, "ARM_FLOWFIX"] \
            or [p for p in ffb if p not in fb] != [FF_XFORBID, FF_ALLOW] + FF_FORBID:
        raise SystemExit("forbid['t65b25r70ff'] is not forbid['t65b25r70'] with the three FLOWFIX rewrites: %r" % ffb)
    if [p for p in fb if p not in srb] != [BASE_XFORBID] or [p for p in srb if p not in fb] != [SR_XFORBID] + SR_FORBID:
        raise SystemExit("forbid['t65b25r70sr'] is not forbid['t65b25r70'] with its XENV rewrite + 2 rescue forbids: %r" % srb)
    if ffb.count(FF_XFORBID) != 1:
        raise SystemExit("ff XENV forbid not exactly once")
    # sr's OWN additions over forbid['t65b25r70'] (its XENV rewrite excluded); the base items sr shares (incl. the bare
    # ARM_FLOWFIX forbid and the FLOWFIX-less ARM_ allowlist) are already rewritten in ff's list
    forbid = [NEW_XFORBID if p == FF_XFORBID else p for p in ffb] + [p for p in srb if p not in fb and p != SR_XFORBID]
    if forbid[len(ffb):] != SR_FORBID or "ARM_FLOWFIX" in forbid or FF_XFORBID in forbid or SR_XFORBID in forbid:
        raise SystemExit("combined forbid list malformed: %r" % forbid)
    for line in GOOD_LINES:
        hit = [p for p in forbid if re.search(p, line)]
        if hit:
            raise SystemExit("new forbid list hits a legitimate print %r via %r" % (line[:60], hit))
    for line in BAD_LINES:
        if not any(re.search(p, line) for p in forbid):
            raise SystemExit("new forbid list does not catch %r" % line)
    # ---- patch text
    comment = ("        # --- t65b25r70ffsr: t65b25r70 (t6stk3 + tight 6.5 + bonus 2.5 + raw-ILP override 0.70; representative\n"
               "        # 0.954) with BOTH stacked additions: IMGFLOW write-time repair after the override (t65b25r70ff) and\n"
               "        # the short-track rescue armed unconditionally (t65b25r70sr). = need['t65b25r70ff'] minus its XENV +\n"
               "        # need['t65b25r70sr']'s deepcenter + trigger-0.0 echoes + this XENV (build_t65b25r70ffsr.py;\n"
               "        # ops/add_t65b25r70ffsr_gate.py). RL_TAGS + orphan cap + ff cross-check + rescue receipts + chain below.\n")
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
    for tg in (BASE_TAG, FF_TAG, SR_TAG):
        if '"%s"' % tg not in rl_re.search(t).group(1) or '"%s"' % tg not in or_re.search(t).group(1):
            raise SystemExit("%s is not in RL_TAGS / the orphan cap; refusing to guess" % tg)
    t2 = t.replace(anchors["need"], entry + anchors["need"], 1)
    t2 = t2.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t2 = t2.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t2 = t2.replace(anchors["tol"], anchors["tol"] + '"%s": 0.15, ' % TAG, 1)
    t2 = rl_re.sub(lambda m: m.group(1) + ', "%s"}' % TAG, t2, count=1)
    t2 = or_re.sub(lambda m: m.group(1) + ', "%s"}' % TAG + m.group(2), t2, count=1)
    t2 = t2.replace(anchors["svtags"], xcheck + anchors["svtags"], 1)
    # ---- structural re-checks on the patched text
    lit = [n for n in ast.parse(t2).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "sv_mark"
           and isinstance(n.value, ast.Dict)]
    if len(lit) != 1 or ast.literal_eval(lit[0].value).get(TAG) != "SV_ARM_HSG200" \
            or not t2.index("sv_mark = {") < t2.index('"%s": "SV_ARM_HSG200"' % TAG) < t2.index(anchors["svtags"]):
        raise SystemExit("sv_mark entry for %s is not inside the dict literal before sv_tags is computed" % TAG)
    if forbid_of(t2, TAG) != forbid or need_of(t2, TAG) != pats:
        raise SystemExit("re-parse of the patched gate does not return the new need/forbid entries")
    if forbid_of(t2, FF_TAG) != ffb or forbid_of(t2, SR_TAG) != srb or need_of(t2, FF_TAG) != ffn \
            or need_of(t2, SR_TAG) != srn:
        raise SystemExit("the patch moved a parent entry")
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
    """t65b25r70sr's REAL visible log (post-rescue counts) turned into a plausible t65b25r70ffsr log (+ run_stats)."""
    mut = mut or {}
    s = src
    if s.count(SR_XENV_LINE) != 1 or s.count('"short_track_rescue_trigger_removed_frac": 0.0,') != 1:
        raise SystemExit("synthetic: t65b25r70sr XENV / trigger echo not exactly once in its log")
    s = s.replace(SR_XENV_LINE, XENV_LINE)
    s = insert_after_line(s, XENV_LINE, (mut.get("enabled", ENABLED_LINE)) + "\n")
    if mut.get("echo01"):
        s = s.replace('"short_track_rescue_trigger_removed_frac": 0.0,', '"short_track_rescue_trigger_removed_frac": 0.1,')
    if mut.get("adaptive_false"):
        if s.count('"adaptive_short_track_rescue": true,') != 1:
            raise SystemExit("synthetic: adaptive echo not exactly once")
        s = s.replace('"adaptive_short_track_rescue": true,', '"adaptive_short_track_rescue": false,')
    rows = {r["dataset"]: dict(r) for r in rs_rows}
    for k, d in enumerate(MOVIES):
        m = re.search(r"ARM_RAWLINK \[%s\] .*? final=(\d+) " % d, s)
        a0 = int(m.group(1))
        sd = int(re.search(r"\[%s\] after safe-division repair: [^\n]*?\badded=(\d+)" % d, s).group(1))
        ch, br, du = mut.get("changed", (30 + k)), (3 + k), mut.get("dups", 0)
        a_in = a0 + mut.get("a0_off", 0)
        a1 = a_in + br - du + (1 if mut.get("arith_off") else 0)
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
        if mut.get("untrig") == d:
            r["short_track_rescue_triggered"] = "0"
        if mut.get("zero_comps"):
            r["short_track_rescue_components"] = "0"
            r["short_track_rescue_nodes"] = "0"
        if mut.get("over_budget"):
            r["short_track_rescue_nodes"] = str(int(r["short_track_rescue_budget"]) + 1)
        if mut.get("drop_cols"):
            for c in ("short_track_rescue_triggered", "short_track_rescue_components"):
                r.pop(c)
        if mut.get("removed_off") == d:
            r["short_track_nodes_removed"] = str(int(r["short_track_nodes_removed"]) + 1)
    if mut.get("anchor_off"):
        s, n = re.subn(r"(ARM_RAWLINK \[44b6_0b24845f\] [^\n]*? anchor=)(\d+)", lambda mm: mm.group(1) + str(int(mm.group(2)) + 1), s, count=1)
        if n != 1:
            raise SystemExit("synthetic: rawlink anchor not found")
    if mut.get("short_off"):
        s, n = re.subn(r"(\[6bba_05b6850b\] after short-track filtering: )(\d+)", lambda mm: mm.group(1) + str(int(mm.group(2)) + 1), s, count=1)
        if n != 1:
            raise SystemExit("synthetic: short-track line not found")
    for extra in mut.get("extra_lines", []):
        s = insert_before_line(s, "Prediction completed", extra + "\n") if "Prediction completed" in s else s + extra + "\n"
    out = io.StringIO()
    fields = list(rs_rows[0].keys()) + [k for k in rows[MOVIES[0]] if k not in rs_rows[0]]
    fields = [f for f in fields if all(f in rows[r["dataset"]] for r in rs_rows)]
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
    for tg in NEG_REAL:
        res["neg_%s_as_%s" % (tg, TAG)] = gate("out_" + tg, TAG)
    for tg in REGRESS:
        if list((ROOT / "data").glob("out_%s/*.log" % tg)):
            res["pos_" + tg] = gate("out_" + tg, tg)
    own = list((ROOT / "data").glob("out_%s/*.log" % TAG))
    if own:
        res["own_" + TAG] = gate("out_" + TAG, TAG)
    # ---- synthetic positive + mutants from t65b25r70sr's REAL visible log (+ its run_stats.csv)
    src_dir = ROOT / "data" / "out_t65b25r70sr"
    src = log_text(next(src_dir.glob("*.log")))
    with open(src_dir / "run_stats.csv", newline="", encoding="utf-8") as fh:
        rs_rows = list(csv.DictReader(fh))
    mutants = {
        # flowfix side (t65b25r70ff's mutants)
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
        "neg_syn_runstats_status": ({"rs_status": "fallback_error"}, "run_stats"),
        # rescue side (t65b25r70sr's mutants)
        "neg_syn_echo_01": ({"echo01": True}, "marker missing"),
        "neg_syn_not_triggered": ({"untrig": "44b6_0b24845f"}, "short_track_rescue_triggered=0"),
        "neg_syn_zero_components": ({"zero_comps": True}, "restored 0 components on every visible movie"),
        "neg_syn_over_budget": ({"over_budget": True}, "components <= nodes <= budget"),
        "neg_syn_no_rescue_cols": ({"drop_cols": True}, "no readable short_track_rescue_* columns"),
        "neg_syn_adaptive_false": ({"adaptive_false": True}, "log contains"),
        # post-rescue chain (this entry's own)
        "neg_syn_removed_mismatch": ({"removed_off": "6bba_05db0fb1"}, "short_track_nodes/edges/components_removed"),
        "neg_syn_anchor_not_final": ({"anchor_off": True}, "did not start from the post-rescue graph"),
        "neg_syn_shorttrack_not_final": ({"short_off": True}, "short-track (post-rescue) nodes/edges"),
        # identity / generic
        "neg_syn_base_xenv": ({"extra_lines": ["ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept"]}, "log contains"),
        "neg_syn_ff_xenv": ({"extra_lines": ["ARM_XENV tag=t65b25r70ff TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1"]}, "log contains"),
        "neg_syn_sr_xenv": ({"extra_lines": [SR_XENV_LINE]}, "log contains"),
        "neg_syn_rawlink_disabled": ({"extra_lines": ["ARM_RAWLINK min_prob=-1.0 enabled=False rule=raw_ilp_override_final_divisions_protected"]}, "log contains"),
        "neg_syn_flowlink_marker": ({"extra_lines": ["ARM_FLOWLINK enabled=True"]}, "log contains"),
        "neg_syn_bonus16": ({"extra_lines": ['"motion_relink_learned_bonus": 1.6,']}, "log contains"),
        "neg_syn_traceback": ({"extra_lines": ["Traceback (most recent call last):"]}, "log contains"),
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
        and all("pos_" + tg in res for tg in REGRESS) and all("neg_%s_as_%s" % (tg, TAG) in res for tg in NEG_REAL)
    if not ok:
        if GATE.read_text(encoding="utf-8") == t2:
            GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
            raise SystemExit("self-test failed; gate.py restored from " + bak.name)
        raise SystemExit("self-test failed AND gate.py was modified by someone else meanwhile; NOT restored, check by hand")
    print("gate entry for %s added (backup %s); need entries now %d" % (TAG, bak.name, len(need_keys(now))))


if __name__ == "__main__":
    main()
