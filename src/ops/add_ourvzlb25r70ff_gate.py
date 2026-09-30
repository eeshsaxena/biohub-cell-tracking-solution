#!/usr/bin/env python3
r"""Gate entry for ourvzlb25r70ff (scratch_kernels/build_ourvzlb25r70ff.py) = ourvzlb25r70 (team top entry, public 0.955:
the V1284 coordinate head for y/x + our sub-voxel z to the edge model, relink tight 6.5, learned bonus 2.5, raw-ILP
override "rawlink" 0.70) + the IMGFLOW write-time repair after the override, ported exactly as t65b25r70ff carries it.
Run from the project root: it backs up ops/gate.py (gate.py.bak_ourvzlb25r70ff), patches it, self-tests, and restores
the backup if any self-test fails.
Dry run: OURVZLB25R70FF_GATE=<copy of gate.py> python ops/add_ourvzlb25r70ff_gate.py

ourvzlb25r70ff must prove on the visible run (4 movies):
  * need: need['ourvzlb25r70'] (read with ast) minus its XENV (STK3V / STK3B 2.5 / T65H 6.5 + echoes, every V1284 /
    z-to-arr / per-movie SV_ARM_HSG200 + ARM_SV_Z_TO_ARR pin EXACTLY - the repair acts on the written graph long after
    detection, so the coordinate prints are ourvzlb25r70's bit for bit - and the six rawlink patterns) + the five
    ARM_FLOWFIX patterns (re-derived as need['t65b25r70ff'] minus need['t65b25r70'], both XENVs aside, and checked equal
    to need['t6stk3ff']'s) + this arm's XENV;
  * forbid: forbid['ourvzlb25r70'] (resolved with ast) with two rewrites: its XENV forbid allows only
    tag=ourvzlb25r70ff and its ARM_ allowlist gains FLOWFIX (that allowlist is what forbids ARM_FLOWFIX on the base;
    it has no bare 'ARM_FLOWFIX' forbid), PLUS forbid['t65b25r70ff']'s two FLOWFIX failure forbids (a FALLBACK/SKIPPED
    movie, enabled=False). Everything else (ARM_LCEFR, tight/bonus/velocity values, every V1284 + z-to-arr failure,
    rawlink off / != 0.7, tracebacks, foreign SV_ARM_) is kept;
  * the tag joins RL_TAGS (per-movie rawlink line after FINAL, degree <= 1/2, division count unchanged, anchor + accepted
    - replaced == final, change-fraction window, total-accepted window) and the orphan cap, like ourvzlb25r70;
  * per-movie cross-check = the live t65b25r70ff block, renamed (flowfix A == ARM_RAWLINK final=, B == A + bridged -
    dups, divisions unchanged == safe divisions added, in-degree <= 1, secs <= 20, the status=ok line after the movie's
    FINAL and ARM_RAWLINK lines, cell-10 written (nodes, edges, divisions) == (FINAL nodes, B, safe divisions), run_stats
    agrees incl. rawlink_final_edges == A, flowfix_status ok and changed/bridged/dups, line-fit smoothed + skipped ==
    nodes; changed > 0 somewhere). ourvzlb25r70's own written-count block (written edges == rawlink final=) is NOT
    applied: with the repair the written edges are B, which the renamed ff block pins instead. No float digests;
  * sv_mark SV_ARM_HSG200 INSIDE the dict literal (>= 4 lines before 'Prediction completed'); FINAL within 15% of REF.
Self-tests: the ourvzlb25r70, t65b25r70ff and ourvzlb25 logs must FAIL as ourvzlb25r70ff; ourvzlb25r70 / ourvzlb25 /
t65b25r70 / t65b25r70sr / t65b25r70ff / t65b25r70ffsr / mixyx50r70 / t6stk3 / t6r70 must still PASS as themselves; every
need entry present before the patch must still exist. A SYNTHETIC ourvzlb25r70ff log (ourvzlb25r70's REAL visible log +
run_stats with this XENV, the FLOWFIX prints injected after each ARM_RAWLINK line, cell-10 and run_stats edges moved by
`bridged`, flowfix_* columns filled) must PASS and every mutant must FAIL on its own message.
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

ROOT = pathlib.Path(os.environ.get("OURVZLB25R70FF_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("OURVZLB25R70FF_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "ourvzlb25r70ff"
BASE_TAG = "ourvzlb25r70"
FF_TAG = "t65b25r70ff"
FF_BASE_TAG = "t65b25r70"
FF_REF_TAG = "t6stk3ff"
BASE_XENV = r"ARM_XENV tag=ourvzlb25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
FF_XENV = (r"ARM_XENV tag=t65b25r70ff TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 FLOWFIX=1 TF=5\.0 KEEP=3\.5 GATE=4\.5 "
           r"MIN_DET=5 ENDS=1 DEADLINE_S=34200")
FF_BASE_XENV = r"ARM_XENV tag=t65b25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 LCEFR=kept"
XENV = (r"ARM_XENV tag=ourvzlb25r70ff TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 FLOWFIX=1 TF=5\.0 KEEP=3\.5 GATE=4\.5 "
        r"MIN_DET=5 ENDS=1 DEADLINE_S=34200 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx")
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
FF_ADD = [r"ARM_FLOWFIX enabled=True TF=5\.0 KEEP=3\.5 GATE=4\.5 MIN_DET=5 ENDS=1 threads=\d+ deadline_s=34200"] + [
    r"ARM_FLOWFIX \[%s\] status=ok windows=\d+ flagged=\d+ acted=\d+ changed=\d+ " % d for d in MOVIES]
OLD_XFORBID = r"ARM_XENV tag=(?!ourvzlb25r70 )"
NEW_XFORBID = r"ARM_XENV tag=(?!ourvzlb25r70ff )"
OLD_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\b)[A-Z0-9]+"
NEW_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK|FLOWFIX)\b)[A-Z0-9]+"
FF_FORBID = [r"ARM_FLOWFIX \[\w+\] (?:FALLBACK|SKIPPED)", r"ARM_FLOWFIX enabled=False"]
EXPECT_ENTRIES = ("ourvzlb25r70", "ourvzlb25", "t65b25r70", "t65b25r70sr", "t65b25r70ff", "t65b25r70ffsr", "mixyx50r70",
                  "t6stk3", "t6r70")
REGRESS = EXPECT_ENTRIES
NEG_REAL = ("ourvzlb25r70", "t65b25r70ff", "ourvzlb25")
XENV_LINE = ("ARM_XENV tag=ourvzlb25r70ff TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 "
             "ENDS=1 DEADLINE_S=34200 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx")
BASE_XENV_LINE = "ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
ENABLED_LINE = "ARM_FLOWFIX enabled=True TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 threads=4 deadline_s=34200"
GOOD_LINES = [
    XENV_LINE, ENABLED_LINE,
    "ARM_FLOWFIX [44b6_0113de3b] status=ok windows=792 flagged=62 acted=37 changed=30 bridged=17 dups=0 "
    "edges=24907->24924 divs=34->34 max_in=1 secs=8.0 elapsed_h=0.38",
    "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
    '  "rawlink_min_prob": 0.7,',
    "ARM_RAWLINK [44b6_0113de3b] min_prob=0.7 candidates=312 accepted=312 replaced=290 anchor=24885 final=24907 "
    "max_in=1 max_out=2 divs=34->34 divs_shielded=1 blocked_parent=1 blocked_daughter=2 below_min=38 replaced_raw=0 "
    "new_isolated=5",
    "ARM_STK3V velocity_weight=0.25", "ARM_STK3B learned_bonus=2.5", "ARM_T65H tight_um=6.5", "ARM_SV_ZONLY=1",
    "ARM_V1284_YX module_patched=1", "SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0.1120 frac_clipped=0.1367 gain=2.00",
    "ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0.3356 z_nonzero=9000 final_z_add=0 gather_int_z=1"]
BAD_LINES = ["ARM_FLOWFIX [44b6_0113de3b] FALLBACK error=ValueError: x", "ARM_FLOWFIX [6bba_05b6850b] SKIPPED deadline",
             "ARM_FLOWFIX enabled=False TF=5.0", BASE_XENV_LINE,
             "ARM_XENV tag=ourvzlb25 TIGHT=6.5 BONUS=2.50 V1284_HEAD=mounted", "ARM_XENV tag=t65b25r70ff TIGHT=6.5",
             "ARM_XENV tag=t65b25r70 TIGHT=6.5", "ARM_XENV tag=t6stk3ff FLOWFIX=1", "ARM_LCEFR patch applied to predictor",
             "ARM_RAWLINK min_prob=-1.0 enabled=False rule=x", "ARM_RAWLINK [44b6_0113de3b] min_prob=0.3 candidates=1 ",
             '"rawlink_min_prob": 0.3,', '"motion_relink_learned_bonus": 1.6,', '"motion_relink_tight_um": 6.0,',
             "ARM_T60H tight_um=6.0", "Traceback (most recent call last)", "ARM_FLOWLINK enabled=True", "ARM_FLOWCUT x",
             "SV_ARM_HSG250 nodes=1", "V1284 patch anchor mismatch", "ARM_SV_Z_TO_ARR NO-OP", "final_z_add=3"]


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
    watch = {BASE_TAG, FF_TAG, FF_BASE_TAG, TAG}
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
    """The live t65b25r70ff cross-check block, renamed for this tag (code byte for byte apart from tag + prefix)."""
    s = t.index("# --- t65b25r70ff (ops/add_t65b25r70ff_gate.py)")
    e = t.index('if "t65b25r70ff" in tags:\n', s)
    ff = t[e:t.index("\n# --- ", e) + 1]
    if ff.count("t65b25r70ff") != 12 or ff.count("_ffx") != 106 or "_ozfx" in t or ff.count("_ffxrs = None") != 1 \
            or "\n#" in ff.rstrip("\n") or not ff.rstrip("\n").endswith("the repair never fired\")"):
        raise SystemExit("the live t65b25r70ff cross-check block is not the one this installer was written against")
    for must in ('"rawlink_final_edges", "flowfix_changed", "flowfix_bridged", "flowfix_dups"',
                 "if _ffxa0 != _ffxrl[d][0]:", "if _ffxa1 != _ffxa0 + _ffxbr - _ffxdu:", "_ffxwant = (_ffxn, _ffxa1, _ffxs)",
                 'float(_ffxm.group(12)) > 20.0'):
        if ff.count(must) != 1:
            raise SystemExit("live t65b25r70ff block lacks %r exactly once" % must)
    head = ("# --- ourvzlb25r70ff (ops/add_ourvzlb25r70ff_gate.py): ourvzlb25r70 (V1284 y/x + sub-voxel z, tight 6.5, bonus\n"
            "# 2.5, rawlink 0.70; public 0.955) + ARM_FLOWFIX after the override. = the live t65b25r70ff cross-check, renamed:\n"
            "# flowfix A == ARM_RAWLINK final=, B == A + bridged - dups == cell-10 written edges, divisions unchanged, <= 20 s,\n"
            "# run_stats agrees (edges == B, rawlink_final_edges == A, flowfix_* as logged, smoothed + skipped == nodes).\n")
    return head + ff.replace("t65b25r70ff", TAG).replace("_ffx", "_ozfx")


def patch(t):
    """Return the patched gate text for source text t (pure function of t)."""
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    # ---- need: ourvzlb25r70's minus XENV + the five FLOWFIX patterns (re-derived from t65b25r70ff) + this XENV
    base, ffn, ffb_n, ref = (list(need_of(t, BASE_TAG)), list(need_of(t, FF_TAG)), list(need_of(t, FF_BASE_TAG)),
                             list(need_of(t, FF_REF_TAG)))
    if base.count(BASE_XENV) != 1 or sum("ARM_XENV" in p for p in base) != 1:
        raise SystemExit("need['ourvzlb25r70'] does not carry exactly its one XENV line: %r" % base)
    if any("FLOWFIX" in p for p in base):
        raise SystemExit("need['ourvzlb25r70'] unexpectedly pins FLOWFIX markers")
    if ffn.count(FF_XENV) != 1 or ffb_n.count(FF_BASE_XENV) != 1:
        raise SystemExit("need['t65b25r70ff'] / need['t65b25r70'] do not carry exactly their XENV lines")
    if [p for p in ffn if p != FF_XENV] != [p for p in ffb_n if p != FF_BASE_XENV] + FF_ADD:
        raise SystemExit("need['t65b25r70ff'] != need['t65b25r70'] - XENV + the five FLOWFIX patterns: %r" % ffn)
    if [p for p in ref if p.startswith("ARM_FLOWFIX")] != FF_ADD:
        raise SystemExit("need['t6stk3ff'] FLOWFIX patterns differ from t65b25r70ff's")
    pats = [p for p in base if p != BASE_XENV] + FF_ADD + [XENV]
    if len(pats) != len(base) + 5 or len(set(pats)) != len(pats) or pats.count(XENV) != 1:
        raise SystemExit("expected ourvzlb25r70's %d patterns - XENV + 5 FLOWFIX + XENV, got %r" % (len(base), pats))
    for stale in (r"1\.6", r"6\.0", "T60H", "LCEFR", "tag=ourvzlb25r70 ", "tag=t65b25r70", "tag=t6stk3ff"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    if sum("RAWLINK" in p or "rawlink" in p for p in pats) != 7:  # 6 rawlink + the XENV's RAWLINK=0.70
        raise SystemExit("rawlink patterns not carried over intact: %r" % pats)
    if sum(p.startswith(("SV_ARM_HSG200 nodes=", "ARM_SV_Z_TO_ARR frames=100 nodes=")) for p in pats) != 8:
        raise SystemExit("the eight per-movie V1284 / z-to-arr coordinate pins are not all carried over")
    # ---- forbid: ourvzlb25r70's with the XENV + ARM_ allowlist rewrites, + t65b25r70ff's two FLOWFIX failure forbids
    fz, fff = forbid_of(t, BASE_TAG), forbid_of(t, FF_TAG)
    if fz.count(OLD_XFORBID) != 1 or fz.count(OLD_ALLOW) != 1:
        raise SystemExit("forbid['ourvzlb25r70'] lacks its XENV forbid / ARM_ allowlist exactly once: %r" % fz)
    if any("FLOWFIX" in p for p in fz):
        raise SystemExit("forbid['ourvzlb25r70'] mentions FLOWFIX explicitly; re-derive by hand: %r" % fz)
    for p in FF_FORBID:
        if fff.count(p) != 1 or forbid_of(t, FF_REF_TAG).count(p) != 1:
            raise SystemExit("forbid['t65b25r70ff'] / forbid['t6stk3ff'] lack %r" % p)
    forbid = [NEW_XFORBID if p == OLD_XFORBID else NEW_ALLOW if p == OLD_ALLOW else p for p in fz]
    forbid += [p for p in FF_FORBID if p not in forbid]
    if len(forbid) != len(fz) + 2 or OLD_XFORBID in forbid or OLD_ALLOW in forbid:
        raise SystemExit("combined forbid list malformed: %r" % forbid)
    for line in GOOD_LINES:
        hit = [p for p in forbid if re.search(p, line)]
        if hit:
            raise SystemExit("new forbid list hits a legitimate print %r via %r" % (line[:60], hit))
    for line in BAD_LINES:
        if not any(re.search(p, line) for p in forbid):
            raise SystemExit("new forbid list does not catch %r" % line)
    # ---- patch text
    comment = ("        # --- ourvzlb25r70ff: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, raw-ILP override\n"
               "        # 0.70; public 0.955) + the IMGFLOW write-time repair after the override, as t65b25r70ff carries it.\n"
               "        # = need['ourvzlb25r70'] minus its XENV + the five ARM_FLOWFIX patterns + this arm's XENV\n"
               "        # (build_ourvzlb25r70ff.py; ops/add_ourvzlb25r70ff_gate.py). Coordinate pins stay EXACT (the repair acts\n"
               "        # on the written graph); RL_TAGS + orphan cap + the renamed t65b25r70ff cross-check carry the bookkeeping.\n")
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
    for tg in (BASE_TAG, FF_TAG):
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
    for tg in (BASE_TAG, FF_TAG, FF_BASE_TAG, FF_REF_TAG):
        if forbid_of(t2, tg) != forbid_of(t, tg) or need_of(t2, tg) != need_of(t, tg):
            raise SystemExit("the patch moved the %s entry" % tg)
    if '"%s"' % TAG not in rl_re.search(t2).group(1) or '"%s"' % TAG not in or_re.search(t2).group(1):
        raise SystemExit("RL_TAGS / orphan cap patch did not land")
    if not (t2.index('RL_TAGS = {') < t2.index('if "%s" in tags:' % TAG) < t2.index(anchors["svtags"])):
        raise SystemExit("cross-check block misplaced")
    if t2.count('if "%s" in tags:' % TAG) != 1 or t2.count("_ozfx") != 106:
        raise SystemExit("cross-check block not exactly once / renamed prefix count off")
    if not need_keys(t) <= need_keys(t2) or (need_keys(t2) - need_keys(t)) != {TAG}:
        raise SystemExit("need keys changed beyond adding %s" % TAG)
    ast.parse(t2)
    compile(t2, str(GATE), "exec")
    return t2, pats, forbid


def synth(src, rs_rows, mut=None):
    """ourvzlb25r70's REAL visible log turned into a plausible ourvzlb25r70ff log (+ matching run_stats rows)."""
    mut = mut or {}
    s = src
    if s.count(BASE_XENV_LINE) != 1:
        raise SystemExit("synthetic: ourvzlb25r70 XENV line not exactly once in its log")
    s = s.replace(BASE_XENV_LINE, XENV_LINE)
    s = insert_after_line(s, XENV_LINE, (mut.get("enabled", ENABLED_LINE)) + "\n")
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
    if mut.get("orphans60"):
        s, n = re.subn(r"(ARM_RAWLINK \[6bba_05db0fb1\] [^\n]*? new_isolated=)(\d+)", lambda mm: mm.group(1) + "60", s,
                       count=1)
        if n != 1:
            raise SystemExit("synthetic: rawlink new_isolated not found")
    if mut.get("pin_off"):  # the SV line prints twice per movie in the real log; move every copy
        if s.count("SV_ARM_HSG200 nodes=7370 ") < 1:
            raise SystemExit("synthetic: 6bba_05b6850b SV pin not in the log")
        s = s.replace("SV_ARM_HSG200 nodes=7370 ", "SV_ARM_HSG200 nodes=7371 ")
    for extra in mut.get("extra_lines", []):
        s = insert_before_line(s, "Prediction completed", extra + "\n") if "Prediction completed" in s else s + extra + "\n"
    if mut.get("sv_after_pred"):
        s = "Prediction completed (mutant: SV lines now after it)\n" + s
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
    try:
        selftest(t, t2, bak)
    except BaseException:
        if GATE.read_text(encoding="utf-8") == t2:
            GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
            print("self-test aborted; gate.py restored from " + bak.name)
        raise


def selftest(t, t2, bak):
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
    # ---- synthetic positive + mutants from ourvzlb25r70's REAL visible log (+ its run_stats.csv)
    src_dir = ROOT / "data" / "out_ourvzlb25r70"
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
        # base side (ourvzlb25r70's / V1284 body's)
        "neg_syn_base_xenv": ({"extra_lines": [BASE_XENV_LINE]}, "log contains"),
        "neg_syn_ff_xenv": ({"extra_lines": ["ARM_XENV tag=t65b25r70ff TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1"]}, "log contains"),
        "neg_syn_lcefr_line": ({"extra_lines": ["ARM_LCEFR patch applied to predictor"]}, "log contains"),
        "neg_syn_v1284_failure": ({"extra_lines": ["V1284 patch anchor mismatch in predictor"]}, "log contains"),
        "neg_syn_sv_pin_changed": ({"pin_off": True}, "marker missing"),
        "neg_syn_sv_after_pred": ({"sv_after_pred": True}, "only 0 SV_ARM_HSG200 lines before 'Prediction completed'"),
        "neg_syn_orphans60": ({"orphans60": True}, "rawlink orphaned more than 50 nodes"),
        "neg_syn_rawlink_disabled": ({"extra_lines": ["ARM_RAWLINK min_prob=-1.0 enabled=False rule=raw_ilp_override_final_divisions_protected"]}, "log contains"),
        "neg_syn_bonus16": ({"extra_lines": ['"motion_relink_learned_bonus": 1.6,']}, "log contains"),
        "neg_syn_t60h_line": ({"extra_lines": ["ARM_T60H tight_um=6.0"]}, "log contains"),
        "neg_syn_flowlink_marker": ({"extra_lines": ["ARM_FLOWLINK enabled=True"]}, "log contains"),
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
