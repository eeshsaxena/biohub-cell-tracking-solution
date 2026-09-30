#!/usr/bin/env python3
r"""Gate installer for the tight-6.25 bonus-sweep arms ourvzlb<NN>t625 = ourvzlb30t625 with the learned bonus 3.0 -> <B>
(= ourvzlb25r70, public 0.955, + tight 6.5 -> 6.25 + bonus 2.5 -> <B>). Generalises ops/ourvzl_combo35_gate.py (which
installed ourvzlb35t625 and is left unchanged) to take the bonus value; ARMS below lists the supported tags. Same
machinery (ops/ourvzl_combo_gate.py as C, ops/ourvzl_envarm_gate.py as E): SEQUENTIAL, re-reads gate.py, backs it up to
gate.py.bak_<tag>, restores it if any self-test fails.

  * need/forbid = E.derive's ourvzlt625 derivation with the bonus marker / cell-2 echo / cell-9 echo swapped to <B>, the
    bonus lookahead forbids re-pointed at <B>, and explicit forbids (marker, cell-2 echo, cell-9 echo) for every OTHER
    value in the sweep (2.5, 3.0, 3.5, ...);
  * independent cross-checks against the LIVE ourvzlb30t625 entry AND every live sibling sweep entry (ourvzlb35t625, ...):
    need == theirs with their bonus patterns -> <B> and their XENV renamed, in order; forbid == theirs re-pointed at <B>
    (XENV lookahead renamed) + this arm's extra explicit old-value forbids; every sibling forbid that does not hit a legit
    print of this arm is kept verbatim;
  * cross-check block = ourvzlb25r70's renamed + the tight-edge receipt (<= the 6.5-gate counts on all four movies, < on
    one), exactly as ourvzlb30t625's / ourvzlb35t625's;
  * the patch may only ADD this arm (pure line inserts + the four one-line registries);
  * synthetic positive + mutants from ourvzlb30t625's REAL visible log + run_stats (bonus 3.0 -> <B>, XENV renamed) when it
    passes as itself, else from ourvzlb25r70's (as ourvzl_combo_gate), + pos_syn_from_ourvzlb25r70 always; every sibling
    sweep arm's synthetic log (same source, bonus -> its value, its XENV) must FAIL as this arm, and so must any sibling's
    real visible log present at install time.
"""
import csv
import difflib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ourvzl_combo_gate as C  # noqa: E402

E = C.E
ORIG_DERIVE, ORIG_XCHECK, ORIG_PATCH, ORIG_SYNTH, ORIG_MUTANTS = C.ORIG_DERIVE, C.ORIG_XCHECK, C.ORIG_PATCH, C.ORIG_SYNTH, \
    C.ORIG_MUTANTS

REF = C.BT  # ourvzlb30t625 (bonus 3.0)
# tag -> (bonus, XENV bonus, xcheck variable prefix). ourvzlb35t625 was installed by ops/ourvzl_combo35_gate.py.
ARMS = {"ourvzlb35t625": ("3.5", "3.50", "_zb35t"), "ourvzlb40t625": ("4.0", "4.00", "_zb40t")}
OLD_VALUES = ("2.5", "3.0")  # the base's and ourvzlb30t625's bonus
C9T, C9B = C.C9T, C.C9B
G = {}  # per-install config, filled by configure()


def xenv_of(tag, xb):
    return "ARM_XENV tag=%s TIGHT=6.25 BONUS=%s RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx" % (tag, xb)


def pats_for(bv):
    e = E.esc(bv)
    return dict(mark=r"ARM_STK3B learned_bonus=%s(?!\d)" % e, echo=r'"motion_relink_learned_bonus": %s(?!\d)' % e,
                c9=r"MOTION_RELINK_LEARNED_BONUS +%s(?!\d)" % e, fmark=r"ARM_STK3B learned_bonus=(?!%s(?!\d))" % e,
                fecho=r'"motion_relink_learned_bonus": (?!%s(?!\d))' % e, fc9=r"MOTION_RELINK_LEARNED_BONUS +(?!%s(?!\d))\d" % e)


def configure(tag):
    if tag not in ARMS:
        raise SystemExit("unknown tag " + tag)
    bv, xb, pfx = ARMS[tag]
    sibs = [t for t in ARMS if t != tag]
    others = list(OLD_VALUES) + [ARMS[t][0] for t in sibs]
    # same order as ourvzl_combo35_gate: 2.5 marker/echo, 3.0 marker/echo, cell-9 2.5/3.0, then each sibling's three
    p25, p30 = pats_for("2.5"), pats_for("3.0")
    extra = [p25["mark"], p25["echo"], p30["mark"], p30["echo"], p25["c9"], p30["c9"]]
    for t in sibs:
        ps = pats_for(ARMS[t][0])
        extra += [ps["mark"], ps["echo"], ps["c9"]]
    if extra[:2] != list(C.B_OLD_FORBIDS):
        raise SystemExit("explicit old-value forbids do not start with ourvzl_combo_gate's 2.5 forbids")
    G.clear()
    G.update(tag=tag, bv=bv, xb=xb, pfx=pfx, P=pats_for(bv), xenv=xenv_of(tag, xb), sibs=sibs, others=others,
             extra=extra, spec=dict(kind="tight", t="6.25", b=bv, xt="6.25", xb=xb, mark="T625H", pfx=pfx))


def bonus_subs(s, old, new):
    for pat, repl in ((r"ARM_STK3B learned_bonus=%s(?!\d)" % E.esc(old), "ARM_STK3B learned_bonus=%s" % new),
                      (r'"motion_relink_learned_bonus": %s(?!\d)' % E.esc(old), '"motion_relink_learned_bonus": %s' % new),
                      (r"(MOTION_RELINK_LEARNED_BONUS +)%s(?!\d)" % E.esc(old), r"\g<1>" + new)):
        s, n = re.subn(pat, repl, s)
        if n != 1:
            raise SystemExit("synthetic: bonus swap %r matched %d times (want 1)" % (pat, n))
    return s


def _xcheck_against(t, pats, forbid, src_tag, src_bv, src_xenv, extra_after):
    """need/forbid must equal the live src_tag entry with its bonus re-pointed at this arm's value."""
    S, P = pats_for(src_bv), G["P"]
    n_src = list(E.need_of(t, src_tag))
    nmap = {S["mark"]: P["mark"], S["echo"]: P["echo"], S["c9"]: P["c9"], E.esc(src_xenv): E.esc(G["xenv"])}
    for k in nmap:
        if n_src.count(k) != 1:
            raise SystemExit("need[%r] lacks %r exactly once" % (src_tag, k))
    if [nmap.get(p, p) for p in n_src] != pats:
        raise SystemExit("need is not need[%r] with the bonus %s -> %s + XENV swap" % (src_tag, src_bv, G["bv"]))
    f_src = list(E.forbid_of(t, src_tag, (E.BASE_TAG, E.SR_TAG, src_tag)))
    fmap = {r"ARM_XENV tag=(?!%s )" % src_tag: r"ARM_XENV tag=(?!%s )" % G["tag"], S["fmark"]: P["fmark"],
            S["fecho"]: P["fecho"], S["fc9"]: P["fc9"]}
    for k in fmap:
        if f_src.count(k) != 1:
            raise SystemExit("forbid[%r] lacks %r exactly once" % (src_tag, k))
    # a sibling's explicit forbid of THIS arm's value must be dropped (it would hit this arm's legit prints)
    own = {P["mark"], P["echo"], P["c9"]}
    exp_f = [fmap.get(p, p) for p in f_src if p not in own]
    exp_f += [p for p in extra_after if p not in exp_f]
    if exp_f != forbid:
        raise SystemExit("forbid is not forbid[%r] re-pointed at %s + the extra forbids: extra %r missing %r"
                         % (src_tag, G["bv"], sorted(set(forbid) - set(exp_f)), sorted(set(exp_f) - set(forbid))))
    return f_src


def derive_bx(t, tag):
    sp = E.SPEC[tag]
    E.SPEC[tag] = dict(sp, b="2.5")  # the ourvzlt625 derivation (bonus still 2.5), then swap the bonus on top
    try:
        pats, forbid = ORIG_DERIVE(t, tag)
    finally:
        E.SPEC[tag] = sp
    if E.xenv_line(tag, sp) != G["xenv"]:
        raise SystemExit("XENV line mismatch: %r" % E.xenv_line(tag, sp))
    P = G["P"]
    pats = C.swap1(pats, E.OLD_B_MARK, P["mark"], "need")
    pats = C.swap1(pats, E.OLD_B_ECHO, P["echo"], "need")
    pats = C.swap1(pats, C.B_C9_OLD, P["c9"], "need")
    forbid = C.swap1(forbid, E.OLD_B_FMARK, P["fmark"], "forbid")
    forbid = C.swap1(forbid, E.OLD_B_FECHO, P["fecho"], "forbid")
    forbid = C.swap1(forbid, C.B_FC9_OLD, P["fc9"], "forbid")
    forbid += [p for p in G["extra"] if p not in forbid]
    # ---- independent cross-checks against the LIVE ourvzlb30t625 entry and every live sibling sweep entry
    parents = [_xcheck_against(t, pats, forbid, REF, "3.0", C.BT_XENV_LINE, G["extra"])]
    live_sibs = [s for s in G["sibs"] if "'%s'" % s in t]
    for s in live_sibs:
        parents.append(_xcheck_against(t, pats, forbid, s, ARMS[s][0], xenv_of(s, ARMS[s][1]), G["extra"]))
    bv = G["bv"]
    good = [G["xenv"], "ARM_T625H tight_um=6.25", "ARM_STK3B learned_bonus=%s" % bv, '  "motion_relink_tight_um": 6.25,',
            '  "motion_relink_learned_bonus": %s,' % bv, C9T % "6.25", C9B % bv, "ARM_STK3V velocity_weight=0.25",
            '  "motion_relink_velocity_weight": 0.25,', "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
            '  "rawlink_min_prob": 0.7,', "ARM_SV_ZONLY=1", "ARM_V1284_YX module_patched=1",
            "SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0.1120 frac_clipped=0.1367 gain=2.00",
            "ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0.3361 z_nonzero=25848 final_z_add=0 gather_int_z=1",
            '  "output_linefit_weight": 0.8,', '  "short_track_rescue_trigger_removed_frac": 0.1,']
    bad = [E.BASE_XENV_LINE, C.B30_XENV_LINE, C.T625_XENV_LINE, C.BT_XENV_LINE, C.FB_XENV_LINE, "ARM_T65H tight_um=6.5",
           '"motion_relink_tight_um": 6.5,', C9T % "6.5", '"motion_relink_learned_bonus": 1.6,', C9B % "1.6",
           "ARM_T675H tight_um=6.75", C9T % "7.0", "Traceback (most recent call last)", "ARM_FLOWFIX enabled=True",
           "ARM_LCEFR patch applied to predictor"]
    for v in G["others"] + [bv + "5"]:
        bad += ["ARM_STK3B learned_bonus=%s" % v, '"motion_relink_learned_bonus": %s,' % v, C9B % v]
    bad += [xenv_of(s, ARMS[s][1]) for s in G["sibs"]]
    C.check_forbid(forbid, good, bad)
    for f_src in parents:
        must = {p for p in f_src if not any(re.search(p, g) for g in good)}
        if not must <= set(forbid):
            raise SystemExit("forbid misses parent forbids compatible with this arm: %r" % sorted(must - set(forbid)))
    if len(set(pats)) != len(pats) or len(set(forbid)) != len(forbid):
        raise SystemExit("duplicate need/forbid patterns")
    print("derive: need/forbid cross-checked against the live entries of %s" % ", ".join([REF] + live_sibs))
    return pats, forbid


def xcheck_bx(t, tag):
    block = ORIG_XCHECK(t, tag)
    old = "ourvzlb25r70 + ONE cell-0 env change (tight).\n"
    if block.count(old) != 1:
        raise SystemExit("xcheck head not as expected")
    return block.replace(old, "ourvzlb25r70 + TWO cell-0 env changes (tight 6.25 + bonus %s).\n" % G["bv"], 1)


def patch_bx(t, tag):
    t2, pats, forbid = ORIG_PATCH(t, tag)
    old = ("        # with ONE cell-0 env change (tight: tight 6.25, bonus %s). = need['ourvzlb25r70'] with the changed knob's\n"
           % G["bv"])
    new = ("        # with TWO cell-0 env changes (tight 6.25 + bonus %s = ourvzlb30t625 with bonus 3.0 -> %s). = need['ourvzlb25r70']"
           " with both knobs'\n" % (G["bv"], G["bv"]))
    if t2.count(old) != 1:
        raise SystemExit("need comment not as expected")
    t2 = t2.replace(old, new, 1)
    for tg in [REF, "ourvzlb30", "ourvzlt625", "ourvzlffb30", "ourvzlb25r70ff"] + [s for s in G["sibs"] if "'%s'" % s in t]:
        w = (E.BASE_TAG, E.SR_TAG, tg)
        if E.forbid_of(t2, tg, w) != E.forbid_of(t, tg, w) or E.need_of(t2, tg) != E.need_of(t, tg):
            raise SystemExit("the patch moved the %s entry" % tg)
    ins_ = (', "%s"' % tag, ' "%s": "SV_ARM_HSG200",' % tag, '"%s": 0.15, ' % tag)
    a, b = t.splitlines(keepends=True), t2.splitlines(keepends=True)
    n_rep = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op in ("equal", "insert"):
            continue
        if op != "replace" or (i2 - i1) != (j2 - j1):
            raise SystemExit("patch removes/rewrites gate.py lines (%s %d..%d)" % (op, i1, i2))
        for x, y in zip(a[i1:i2], b[j1:j2]):
            if not any(y[:k] + y[k + len(s):] == x for s in ins_ for k in (m.start() for m in re.finditer(re.escape(s), y))):
                raise SystemExit("patch edits an existing gate.py line beyond adding %s: %r -> %r" % (tag, x[:90], y[:90]))
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
                with open(d / "run_stats.csv", newline="", encoding="utf-8") as fh:
                    _REF_SRC["v"] = (E.log_text(logs[0]), list(csv.DictReader(fh)))
            else:
                print("NOTE: ourvzlb30t625's visible log does not pass as itself (%s); synthetics fall back to ourvzlb25r70"
                      % v[:150])
    return _REF_SRC["v"]


def synth_bx(tag, src, rs_rows, mut=None):
    mut = dict(mut or {})
    use = mut.pop("src", None)
    as_tag = mut.pop("as", tag)  # build the log of another sweep arm (it must FAIL as this one)
    bv, xenv = (G["bv"], G["xenv"]) if as_tag == tag else (ARMS[as_tag][0], xenv_of(as_tag, ARMS[as_tag][1]))
    real = None if use == "b25r70" else _ref_source()
    if real is None:
        s, rs_csv = ORIG_SYNTH(tag, bonus_subs(src, "2.5", bv), rs_rows, mut)
        if as_tag != tag:
            if s.count(G["xenv"]) != 1:
                raise SystemExit("synthetic: own XENV not exactly once")
            s = s.replace(G["xenv"], xenv)
        return s, rs_csv
    s, rs = real
    if s.count(C.BT_XENV_LINE) != 1:
        raise SystemExit("synthetic: ourvzlb30t625 XENV line not exactly once in its log")
    s = bonus_subs(s.replace(C.BT_XENV_LINE, xenv), "3.0", bv)
    s = C.apply_mut(s, mut)
    rows = [dict(r) for r in rs]
    if "tight_step" in mut:
        for r in rows:
            r["motion_relink_tight_edges"] = str(E.BASE_TIGHT[r["dataset"]] + mut["tight_step"])
    return s, C.write_rs(rs, rows)


def mutants_bx(tag):
    bv = G["bv"]
    m = ORIG_MUTANTS(tag)
    m.update({
        "pos_syn_from_ourvzlb25r70": ({"src": "b25r70"}, None),
        "neg_syn_near_bonus_marker": ({"extra_lines": ["ARM_STK3B learned_bonus=%s5" % bv]}, "log contains"),
        "neg_syn_old_tight_cell9": ({"extra_lines": [C9T % "6.5"]}, "log contains"),
        "neg_syn_other_bonus_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 1.6,']}, "log contains"),
        "neg_syn_bonus_marker_missing": ({"replace": [("ARM_STK3B learned_bonus=%s" % bv, "ARM_STK3B gone")]}, None),
        "neg_syn_bonus_echo_missing": ({"replace": [('"motion_relink_learned_bonus": %s' % bv, '"motion_relink_learned_bonuz": %s' % bv)]}, None),
        "neg_syn_bonus_cell9_missing": ({"replace": [((C9B % bv).strip(), (C9B % bv).strip().replace("BONUS", "BONUZ"))]}, None),
        "neg_syn_b30_xenv": ({"extra_lines": [C.B30_XENV_LINE]}, "log contains"),
        "neg_syn_t625_xenv": ({"extra_lines": [C.T625_XENV_LINE]}, "log contains"),
        "neg_syn_b30t625_xenv": ({"extra_lines": [C.BT_XENV_LINE]}, "log contains"),
    })
    for v in G["others"]:
        k = v.replace(".", "")
        m.update({
            "neg_syn_b%s_bonus_marker" % k: ({"extra_lines": ["ARM_STK3B learned_bonus=%s" % v]}, "log contains"),
            "neg_syn_b%s_bonus_echo" % k: ({"extra_lines": ['  "motion_relink_learned_bonus": %s,' % v]}, "log contains"),
            "neg_syn_b%s_bonus_cell9" % k: ({"extra_lines": [C9B % v]}, "log contains"),
        })
    for s in G["sibs"]:
        m["neg_syn_%s_xenv" % s] = ({"extra_lines": [xenv_of(s, ARMS[s][1])]}, "log contains")
        m["neg_syn_%s_log" % s] = ({"as": s}, "marker missing")  # the sibling's whole synthetic log
        m["neg_syn_%s_log_b25r70src" % s] = ({"as": s, "src": "b25r70"}, "marker missing")
    return m


def install(tag):
    configure(tag)
    have = lambda tg: bool(list((E.ROOT / "data").glob("out_%s/*.log" % tg)))  # noqa: E731
    E.SPEC[tag] = G["spec"]
    E.derive, E.xcheck, E.patch, E.synth, E.mutants = derive_bx, xcheck_bx, patch_bx, synth_bx, mutants_bx
    E.NEG_REAL = ("ourvzlb25r70", "ourvzlb30", "ourvzlt625", "ourvzlb25r70ff") + tuple(
        x for x in [REF] + G["sibs"] if have(x))
    E.REGRESS_REQUIRED = tuple(E.REGRESS_REQUIRED) + tuple(
        x for x in ("ourvzlb30", "ourvzlt625", "ourvzlt675", "ourvzlb25r70ff") + ((REF,) if have(REF) else ())
        if x not in E.REGRESS_REQUIRED)
    E.SIBLINGS = tuple(E.SIBLINGS) + tuple(x for x in [C.BT, C.FB] + G["sibs"] if x not in E.SIBLINGS)
    src = _ref_source()
    print("tag %s bonus %s | synthetic source: %s | real negatives: %s" % (
        tag, G["bv"], "ourvzlb30t625 REAL visible log + run_stats (bonus 3.0 -> %s)" % G["bv"] if src else
        "ourvzlb25r70 real log (tight 6.5 -> 6.25, bonus 2.5 -> %s), as ourvzl_combo_gate" % G["bv"], list(E.NEG_REAL)))
    E.install(tag)
