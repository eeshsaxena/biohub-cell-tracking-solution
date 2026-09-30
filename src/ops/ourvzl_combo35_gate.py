#!/usr/bin/env python3
r"""Gate installer for ourvzlb35t625 (scratch_kernels/build_ourvzlb35t625.py) = ourvzlb30t625 with the learned bonus
3.0 -> 3.5 (= ourvzlb25r70, public 0.955, + tight 6.5 -> 6.25 + bonus 2.5 -> 3.5). Same machinery as the ourvzlb30t625
arm of ops/ourvzl_combo_gate.py (imported as C, on top of ops/ourvzl_envarm_gate.py imported as E): the install is
SEQUENTIAL, re-reads gate.py, backs it up to gate.py.bak_ourvzlb35t625 and restores it if any self-test fails.
ops/ourvzl_combo_gate.py itself is not modified.

  * need/forbid = E.derive's ourvzlt625 derivation (tight 6.25, T625H allowlist, old-6.5 forbids, cell-9 echoes) with
    the bonus marker / cell-2 echo / cell-9 echo swapped to 3.5, the bonus lookahead forbids re-pointed at 3.5, and
    explicit 2.5 AND 3.0 forbids (marker, cell-2 echo, cell-9 echo);
  * independent cross-check against the LIVE ourvzlb30t625 entry: need == need['ourvzlb30t625'] with its three 3.0 bonus
    patterns -> 3.5 and its XENV renamed, in order; forbid == forbid['ourvzlb30t625'] with its XENV lookahead renamed and
    its three 3.0 lookaheads re-pointed at 3.5, + the new explicit 3.0 / cell-9 forbids; every ourvzlb30t625 forbid that
    does not hit a legit print of this arm is kept verbatim;
  * cross-check block = ourvzlb25r70's renamed + the tight-edge receipt (<= the 6.5-gate counts on all four movies, < on
    one), exactly as ourvzlb30t625's;
  * the patch may only ADD this arm (line-level diff vs the old gate.py: pure inserts, plus the four one-line registries
    where the only change is this tag's insertion);
  * synthetic positive + mutants: built from ourvzlb30t625's REAL visible log + run_stats (bonus 3.0 -> 3.5, XENV
    renamed) when data/out_ourvzlb30t625 has a log that PASSES as ourvzlb30t625; otherwise (and additionally, as
    pos_syn_from_ourvzlb25r70) from ourvzlb25r70's real log exactly as ourvzl_combo_gate does (tight 6.5 -> 6.25,
    bonus 2.5 -> 3.5, tight edges -7).
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ourvzl_combo_gate as C  # noqa: E402

E = C.E
ORIG_DERIVE, ORIG_XCHECK, ORIG_PATCH, ORIG_SYNTH, ORIG_MUTANTS = C.ORIG_DERIVE, C.ORIG_XCHECK, C.ORIG_PATCH, C.ORIG_SYNTH, \
    C.ORIG_MUTANTS

TAG = "ourvzlb35t625"
REF = C.BT  # ourvzlb30t625
SPEC35 = dict(kind="tight", t="6.25", b="3.5", xt="6.25", xb="3.50", mark="T625H", pfx="_zb35t")
XENV_LINE = "ARM_XENV tag=ourvzlb35t625 TIGHT=6.25 BONUS=3.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"

B_MARK = r"ARM_STK3B learned_bonus=3\.5(?!\d)"
B_ECHO = r'"motion_relink_learned_bonus": 3\.5(?!\d)'
B_C9 = r"MOTION_RELINK_LEARNED_BONUS +3\.5(?!\d)"
B_FMARK = r"ARM_STK3B learned_bonus=(?!3\.5(?!\d))"
B_FECHO = r'"motion_relink_learned_bonus": (?!3\.5(?!\d))'
B_FC9 = r"MOTION_RELINK_LEARNED_BONUS +(?!3\.5(?!\d))\d"
OLD_FORBIDS = list(C.B_OLD_FORBIDS) + [
    r"ARM_STK3B learned_bonus=3\.0(?!\d)", r'"motion_relink_learned_bonus": 3\.0(?!\d)',
    r"MOTION_RELINK_LEARNED_BONUS +2\.5(?!\d)", r"MOTION_RELINK_LEARNED_BONUS +3\.0(?!\d)"]
C9T, C9B = C.C9T, C.C9B


def bonus_subs(s, old):
    for pat, repl in ((r"ARM_STK3B learned_bonus=%s(?!\d)" % E.esc(old), "ARM_STK3B learned_bonus=3.5"),
                      (r'"motion_relink_learned_bonus": %s(?!\d)' % E.esc(old), '"motion_relink_learned_bonus": 3.5'),
                      (r"(MOTION_RELINK_LEARNED_BONUS +)%s(?!\d)" % E.esc(old), r"\g<1>3.5")):
        s, n = re.subn(pat, repl, s)
        if n != 1:
            raise SystemExit("synthetic: bonus swap %r matched %d times (want 1)" % (pat, n))
    return s


def derive35(t, tag):
    sp = E.SPEC[tag]
    E.SPEC[tag] = dict(sp, b="2.5")  # the ourvzlt625 derivation (bonus still 2.5), then swap the bonus on top
    try:
        pats, forbid = ORIG_DERIVE(t, tag)
    finally:
        E.SPEC[tag] = sp
    if E.xenv_line(tag, sp) != XENV_LINE:
        raise SystemExit("XENV line mismatch: %r" % E.xenv_line(tag, sp))
    pats = C.swap1(pats, E.OLD_B_MARK, B_MARK, "need")
    pats = C.swap1(pats, E.OLD_B_ECHO, B_ECHO, "need")
    pats = C.swap1(pats, C.B_C9_OLD, B_C9, "need")
    forbid = C.swap1(forbid, E.OLD_B_FMARK, B_FMARK, "forbid")
    forbid = C.swap1(forbid, E.OLD_B_FECHO, B_FECHO, "forbid")
    forbid = C.swap1(forbid, C.B_FC9_OLD, B_FC9, "forbid")
    forbid += [p for p in OLD_FORBIDS if p not in forbid]
    # ---- independent cross-check against the LIVE ourvzlb30t625 entry
    n_ref = list(E.need_of(t, REF))
    nmap = {C.B_MARK_NEW: B_MARK, C.B_ECHO_NEW: B_ECHO, C.B_C9_NEW: B_C9, E.esc(C.BT_XENV_LINE): E.esc(XENV_LINE)}
    for k in nmap:
        if n_ref.count(k) != 1:
            raise SystemExit("need['ourvzlb30t625'] lacks %r exactly once" % k)
    if sum("ARM_XENV" in p for p in n_ref) != 1:
        raise SystemExit("need['ourvzlb30t625'] carries more than one XENV")
    if [nmap.get(p, p) for p in n_ref] != pats:
        raise SystemExit("need is not need['ourvzlb30t625'] with the bonus 3.0 -> 3.5 + XENV swap: %r vs %r"
                         % (sorted(set(pats) - set(nmap.get(p, p) for p in n_ref)),
                            sorted(set(nmap.get(p, p) for p in n_ref) - set(pats))))
    f_ref = list(E.forbid_of(t, REF, (E.BASE_TAG, E.SR_TAG, REF)))
    fmap = {r"ARM_XENV tag=(?!%s )" % REF: r"ARM_XENV tag=(?!%s )" % TAG, C.B_FMARK_NEW: B_FMARK,
            C.B_FECHO_NEW: B_FECHO, C.B_FC9_NEW: B_FC9}
    for k in fmap:
        if f_ref.count(k) != 1:
            raise SystemExit("forbid['ourvzlb30t625'] lacks %r exactly once" % k)
    exp_f = [fmap.get(p, p) for p in f_ref]
    exp_f += [p for p in OLD_FORBIDS if p not in exp_f]
    if exp_f != forbid:
        raise SystemExit("forbid is not forbid['ourvzlb30t625'] re-pointed at 3.5 + the 3.0 forbids: extra %r missing %r"
                         % (sorted(set(forbid) - set(exp_f)), sorted(set(exp_f) - set(forbid))))
    good = [XENV_LINE, "ARM_T625H tight_um=6.25", "ARM_STK3B learned_bonus=3.5", '  "motion_relink_tight_um": 6.25,',
            '  "motion_relink_learned_bonus": 3.5,', C9T % "6.25", C9B % "3.5", "ARM_STK3V velocity_weight=0.25",
            '  "motion_relink_velocity_weight": 0.25,', "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
            '  "rawlink_min_prob": 0.7,', "ARM_SV_ZONLY=1", "ARM_V1284_YX module_patched=1",
            "SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0.1120 frac_clipped=0.1367 gain=2.00",
            "ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0.3361 z_nonzero=25848 final_z_add=0 gather_int_z=1",
            '  "output_linefit_weight": 0.8,', '  "short_track_rescue_trigger_removed_frac": 0.1,']
    bad = [E.BASE_XENV_LINE, C.B30_XENV_LINE, C.T625_XENV_LINE, C.BT_XENV_LINE, C.FB_XENV_LINE, "ARM_T65H tight_um=6.5",
           '"motion_relink_tight_um": 6.5,', C9T % "6.5", "ARM_STK3B learned_bonus=2.5", '"motion_relink_learned_bonus": 2.5,',
           C9B % "2.5", "ARM_STK3B learned_bonus=3.0", '"motion_relink_learned_bonus": 3.0,', C9B % "3.0",
           "ARM_STK3B learned_bonus=3.55", '"motion_relink_learned_bonus": 3.55,', C9B % "3.55",
           '"motion_relink_learned_bonus": 1.6,', C9B % "1.6", "ARM_T675H tight_um=6.75", C9T % "7.0",
           "Traceback (most recent call last)", "ARM_FLOWFIX enabled=True", "ARM_LCEFR patch applied to predictor"]
    C.check_forbid(forbid, good, bad)
    must = {p for p in f_ref if not any(re.search(p, g) for g in good)}
    if not must <= set(forbid):
        raise SystemExit("forbid misses ourvzlb30t625 forbids compatible with this arm: %r" % sorted(must - set(forbid)))
    if len(set(pats)) != len(pats) or len(set(forbid)) != len(forbid):
        raise SystemExit("duplicate need/forbid patterns")
    return pats, forbid


def xcheck35(t, tag):
    block = ORIG_XCHECK(t, tag)
    old = "ourvzlb25r70 + ONE cell-0 env change (tight).\n"
    if block.count(old) != 1:
        raise SystemExit("xcheck head not as expected")
    return block.replace(old, "ourvzlb25r70 + TWO cell-0 env changes (tight 6.25 + bonus 3.5).\n", 1)


REG_INSERTS = (', "%s"' % TAG, ' "%s": "SV_ARM_HSG200",' % TAG, '"%s": 0.15, ' % TAG)


def patch35(t, tag):
    import difflib
    t2, pats, forbid = ORIG_PATCH(t, tag)
    old = "        # with ONE cell-0 env change (tight: tight 6.25, bonus 3.5). = need['ourvzlb25r70'] with the changed knob's\n"
    new = ("        # with TWO cell-0 env changes (tight 6.25 + bonus 3.5 = ourvzlb30t625 with bonus 3.0 -> 3.5). = need['ourvzlb25r70']"
           " with both knobs'\n")
    if t2.count(old) != 1:
        raise SystemExit("need comment not as expected")
    t2 = t2.replace(old, new, 1)
    for tg in (REF, "ourvzlb30", "ourvzlt625", "ourvzlffb30", "ourvzlb25r70ff"):
        w = (E.BASE_TAG, E.SR_TAG, tg)
        if E.forbid_of(t2, tg, w) != E.forbid_of(t, tg, w) or E.need_of(t2, tg) != E.need_of(t, tg):
            raise SystemExit("the patch moved the %s entry" % tg)
    # the patch only ADDS this arm: pure line inserts, plus the one-line registries where the only change is this tag
    a, b = t.splitlines(keepends=True), t2.splitlines(keepends=True)
    n_rep = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal" or op == "insert":
            continue
        if op != "replace" or (i2 - i1) != (j2 - j1):
            raise SystemExit("patch removes/rewrites gate.py lines (%s %d..%d)" % (op, i1, i2))
        for x, y in zip(a[i1:i2], b[j1:j2]):
            ok = any(y[:k] + y[k + len(ins):] == x for ins in REG_INSERTS
                     for k in (m.start() for m in re.finditer(re.escape(ins), y)))
            if not ok:
                raise SystemExit("patch edits an existing gate.py line beyond adding %s: %r -> %r" % (TAG, x[:90], y[:90]))
            n_rep += 1
    if n_rep != 4:
        raise SystemExit("expected exactly 4 one-line registry edits (RL_TAGS, orphan cap, sv_mark, tol), got %d" % n_rep)
    compile(t2, str(E.GATE), "exec")
    return t2, pats, forbid


_REF_SRC = {}


def _ref_source():
    """ourvzlb30t625's REAL visible log + run_stats, only if the log exists and passes as ourvzlb30t625."""
    if "v" not in _REF_SRC:
        _REF_SRC["v"] = None
        d = E.ROOT / "data" / ("out_" + REF)
        logs = sorted(d.glob("*.log"))
        if logs and (d / "run_stats.csv").is_file():
            v = E.gate_file(logs[0], REF)
            if "GATE_PASS" in v:
                import csv
                with open(d / "run_stats.csv", newline="", encoding="utf-8") as fh:
                    _REF_SRC["v"] = (E.log_text(logs[0]), list(csv.DictReader(fh)))
            else:
                print("NOTE: ourvzlb30t625's visible log does not pass as itself (%s); synthetics fall back to ourvzlb25r70"
                      % v[:150])
    return _REF_SRC["v"]


def synth35(tag, src, rs_rows, mut=None):
    mut = dict(mut or {})
    use = mut.pop("src", None)
    real = None if use == "b25r70" else _ref_source()
    if real is None:
        # ourvzl_combo_gate's method: ourvzlb25r70's real log, bonus swapped in the SOURCE first, then E.synth's tight swap
        return ORIG_SYNTH(tag, bonus_subs(src, "2.5"), rs_rows, mut)
    s, rs = real
    if s.count(C.BT_XENV_LINE) != 1:
        raise SystemExit("synthetic: ourvzlb30t625 XENV line not exactly once in its log")
    s = bonus_subs(s.replace(C.BT_XENV_LINE, XENV_LINE), "3.0")
    s = C.apply_mut(s, mut)
    rows = [dict(r) for r in rs]
    if "tight_step" in mut:
        for r in rows:
            r["motion_relink_tight_edges"] = str(E.BASE_TIGHT[r["dataset"]] + mut["tight_step"])
    return s, C.write_rs(rs, rows)


def mutants35(tag):
    m = ORIG_MUTANTS(tag)
    m.update({
        "pos_syn_from_ourvzlb25r70": ({"src": "b25r70"}, None),
        "neg_syn_old_bonus_marker": ({"extra_lines": ["ARM_STK3B learned_bonus=2.5"]}, "log contains"),
        "neg_syn_old_bonus_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 2.5,']}, "log contains"),
        "neg_syn_old_bonus_cell9": ({"extra_lines": [C9B % "2.5"]}, "log contains"),
        "neg_syn_b30_bonus_marker": ({"extra_lines": ["ARM_STK3B learned_bonus=3.0"]}, "log contains"),
        "neg_syn_b30_bonus_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 3.0,']}, "log contains"),
        "neg_syn_b30_bonus_cell9": ({"extra_lines": [C9B % "3.0"]}, "log contains"),
        "neg_syn_near_bonus_marker": ({"extra_lines": ["ARM_STK3B learned_bonus=3.55"]}, "log contains"),
        "neg_syn_old_tight_cell9": ({"extra_lines": [C9T % "6.5"]}, "log contains"),
        "neg_syn_other_bonus_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 1.6,']}, "log contains"),
        "neg_syn_bonus_marker_missing": ({"replace": [("ARM_STK3B learned_bonus=3.5", "ARM_STK3B gone")]}, None),
        "neg_syn_bonus_echo_missing": ({"replace": [('"motion_relink_learned_bonus": 3.5', '"motion_relink_learned_bonuz": 3.5')]}, None),
        "neg_syn_bonus_cell9_missing": ({"replace": [((C9B % "3.5").strip(), (C9B % "3.5").strip().replace("BONUS", "BONUZ"))]}, None),
        "neg_syn_b30_xenv": ({"extra_lines": [C.B30_XENV_LINE]}, "log contains"),
        "neg_syn_t625_xenv": ({"extra_lines": [C.T625_XENV_LINE]}, "log contains"),
        "neg_syn_b30t625_xenv": ({"extra_lines": [C.BT_XENV_LINE]}, "log contains"),
    })
    return m


def install(tag):
    if tag != TAG:
        raise SystemExit("unknown tag " + tag)
    have_ref = bool(list((E.ROOT / "data").glob("out_%s/*.log" % REF)))
    E.SPEC[TAG] = SPEC35
    E.derive, E.xcheck, E.patch, E.synth, E.mutants = derive35, xcheck35, patch35, synth35, mutants35
    E.NEG_REAL = ("ourvzlb25r70", "ourvzlb30", "ourvzlt625", "ourvzlb25r70ff") + ((REF,) if have_ref else ())
    E.REGRESS_REQUIRED = tuple(E.REGRESS_REQUIRED) + tuple(
        x for x in ("ourvzlb30", "ourvzlt625", "ourvzlt675", "ourvzlb25r70ff") + ((REF,) if have_ref else ())
        if x not in E.REGRESS_REQUIRED)
    E.SIBLINGS = tuple(E.SIBLINGS) + tuple(x for x in (C.BT, C.FB) if x not in E.SIBLINGS)
    src = _ref_source()
    print("synthetic source:", "ourvzlb30t625 REAL visible log + run_stats (bonus 3.0 -> 3.5)" if src else
          "ourvzlb25r70 real log (tight 6.5 -> 6.25, bonus 2.5 -> 3.5), as ourvzl_combo_gate")
    E.install(tag)
