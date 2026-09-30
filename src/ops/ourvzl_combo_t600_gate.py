#!/usr/bin/env python3
r"""Gate installer for ourvzlb30t600 (scratch_kernels/build_ourvzlb30t600.py) = ourvzlb30t625 with ONLY the relink tight gate
6.25 -> 6.0 (bonus 3.0, rawlink 0.70). Same machinery as ops/ourvzl_combo35_gate.py (C = ops/ourvzl_combo_gate.py, E =
ops/ourvzl_envarm_gate.py): SEQUENTIAL, re-reads gate.py, backs it up to gate.py.bak_ourvzlb30t600, restores on failure.

  * need = the LIVE need['ourvzlb30t625'] with its three 6.25 tight patterns (ARM_T625H marker, cell-2 echo, cell-9 echo)
    -> 6.0 (ARM_T60H tight_um=6.0, the marker v_ourv carries) and its XENV renamed; bonus 3.0 patterns kept verbatim;
  * forbid = the LIVE forbid['ourvzlb30t625'] with the XENV lookahead renamed, the three tight lookaheads re-pointed at 6.0,
    the ARM_ allowlist T625H -> T60H, the inherited bare 'ARM_T60H' forbid dropped (it is this arm's legit marker), plus
    explicit 6.25 forbids (\bARM_T625H\b, cell-2 echo, tight_um=, cell-9) and a cell-9 6.5 forbid; checked against legit
    6.0 prints and bad 6.25 / 6.5 / 6.75 / 7.0 / 6.05 prints; every other ourvzlb30t625 forbid kept verbatim;
  * cross-check block = ourvzlb25r70's renamed + the tight-edge receipt against ourvzlb30t625's REAL 6.25-gate counts
    (24508/18072/5803/65713, == ourvzlt625's): <= on all four movies and < on at least one;
  * the patch may only ADD this arm (pure line inserts + the four one-line registries);
  * synthetic positive + mutants from ourvzlb30t625's REAL visible log + run_stats (tight 6.25 -> 6.0, XENV renamed, tight
    edges -7) + pos_syn_from_ourvzlb25r70 (tight 6.5 -> 6.0, bonus 2.5 -> 3.0); ourvzlb30t625's real log (and the
    ourvzlb35t625 / ourvzlb40t625 ones if present) must FAIL as this arm.
"""
import csv
import difflib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ourvzl_combo_gate as C  # noqa: E402

E = C.E
ORIG_XCHECK, ORIG_PATCH, ORIG_SYNTH, ORIG_MUTANTS = C.ORIG_XCHECK, C.ORIG_PATCH, C.ORIG_SYNTH, C.ORIG_MUTANTS

TAG = "ourvzlb30t600"
REF = C.BT  # ourvzlb30t625
SPEC = dict(kind="tight", t="6.0", b="3.0", xt="6.0", xb="3.00", mark="T60H", pfx="_zb30t6")
XENV_LINE = "ARM_XENV tag=ourvzlb30t600 TIGHT=6.0 BONUS=3.00 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
T625 = {"44b6_0113de3b": 24508, "44b6_0b24845f": 18072, "6bba_05b6850b": 5803, "6bba_05db0fb1": 65713}
C9T, C9B = C.C9T, C.C9B
NMAP = {r"ARM_T625H tight_um=6\.25(?!\d)": r"ARM_T60H tight_um=6\.0(?!\d)",
        r'"motion_relink_tight_um": 6\.25(?!\d)': r'"motion_relink_tight_um": 6\.0(?!\d)',
        r"MOTION_RELINK_TIGHT_UM +6\.25(?!\d)": r"MOTION_RELINK_TIGHT_UM +6\.0(?!\d)",
        E.esc(C.BT_XENV_LINE): E.esc(XENV_LINE)}
FMAP = {r"ARM_XENV tag=(?!%s )" % REF: r"ARM_XENV tag=(?!%s )" % TAG,
        r"ARM_T\d+H tight_um=(?!6\.25(?!\d))": r"ARM_T\d+H tight_um=(?!6\.0(?!\d))",
        r'"motion_relink_tight_um": (?!6\.25(?!\d))': r'"motion_relink_tight_um": (?!6\.0(?!\d))',
        r"MOTION_RELINK_TIGHT_UM +(?!6\.25(?!\d))\d": r"MOTION_RELINK_TIGHT_UM +(?!6\.0(?!\d))\d",
        r"\bARM_(?!(?:STK3V|STK3B|T625H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\b)[A-Z0-9]+":
            r"\bARM_(?!(?:STK3V|STK3B|T60H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\b)[A-Z0-9]+"}
DROP = {"ARM_T60H"}
EXTRA = [r"\bARM_T625H\b", r'"motion_relink_tight_um": 6\.25(?!\d)', r"tight_um=6\.25(?!\d)",
         r"MOTION_RELINK_TIGHT_UM +6\.25(?!\d)", r"MOTION_RELINK_TIGHT_UM +6\.5(?!\d)"]


def derive_t6(t, tag):
    n_ref = list(E.need_of(t, REF))
    for k in NMAP:
        if n_ref.count(k) != 1:
            raise SystemExit("need['ourvzlb30t625'] lacks %r exactly once" % k)
    if sum("ARM_XENV" in p for p in n_ref) != 1:
        raise SystemExit("need['ourvzlb30t625'] carries more than one XENV")
    for p in (C.B_MARK_NEW, C.B_ECHO_NEW, C.B_C9_NEW):
        if n_ref.count(p) != 1:
            raise SystemExit("need['ourvzlb30t625'] lacks bonus 3.0 pattern %r" % p)
    pats = [NMAP.get(p, p) for p in n_ref]
    f_ref = list(E.forbid_of(t, REF, (E.BASE_TAG, E.SR_TAG, REF)))
    for k in list(FMAP) + list(DROP):
        if f_ref.count(k) != 1:
            raise SystemExit("forbid['ourvzlb30t625'] lacks %r exactly once" % k)
    forbid = [FMAP.get(p, p) for p in f_ref if p not in DROP]
    forbid += [p for p in EXTRA if p not in forbid]
    good = [XENV_LINE, "ARM_T60H tight_um=6.0", '  "motion_relink_tight_um": 6.0,', C9T % "6.0",
            "ARM_STK3B learned_bonus=3.0", '  "motion_relink_learned_bonus": 3.0,', C9B % "3.0",
            "ARM_STK3V velocity_weight=0.25", '  "motion_relink_velocity_weight": 0.25,',
            "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected", '  "rawlink_min_prob": 0.7,',
            "ARM_SV_ZONLY=1", "ARM_V1284_YX module_patched=1",
            "SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0.1120 frac_clipped=0.1367 gain=2.00",
            "ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0.3361 z_nonzero=25848 final_z_add=0 gather_int_z=1",
            '  "output_linefit_weight": 0.8,', '  "short_track_rescue_trigger_removed_frac": 0.1,']
    bad = [E.BASE_XENV_LINE, C.B30_XENV_LINE, C.T625_XENV_LINE, C.BT_XENV_LINE, C.FB_XENV_LINE,
           "ARM_STK3B learned_bonus=2.5", '"motion_relink_learned_bonus": 2.5,', C9B % "2.5", C9B % "3.5",
           '"motion_relink_learned_bonus": 3.5,', "Traceback (most recent call last)", "ARM_FLOWFIX enabled=True",
           "ARM_LCEFR patch applied to predictor"]
    for v, mk in (("6.25", "T625H"), ("6.5", "T65H"), ("6.75", "T675H"), ("7.0", "T70H"), ("6.05", "T605H")):
        bad += ["ARM_%s tight_um=%s" % (mk, v), '"motion_relink_tight_um": %s,' % v, C9T % v]
    C.check_forbid(forbid, good, bad)
    must = {p for p in f_ref if not any(re.search(p, g) for g in good)}
    if not must <= set(forbid):
        raise SystemExit("forbid misses ourvzlb30t625 forbids compatible with this arm: %r" % sorted(must - set(forbid)))
    hit = sorted(p for p in f_ref if any(re.search(p, g) for g in good))
    if set(hit) != (set(FMAP) | DROP):
        raise SystemExit("unexpected ourvzlb30t625 forbids hit this arm's legit prints: %r" % hit)
    if len(set(pats)) != len(pats) or len(set(forbid)) != len(forbid):
        raise SystemExit("duplicate need/forbid patterns")
    print("derive: need/forbid = live ourvzlb30t625 entry re-pointed at tight 6.0; parent forbids hitting legit 6.0 prints "
          "(re-pointed or dropped): %d" % len(hit))
    return pats, forbid


def xcheck_t6(t, tag):
    block = ORIG_XCHECK(t, tag)  # E.BASE_TIGHT == T625 during this install: the receipt compares against 6.25 counts
    reps = [("ourvzlb25r70 + ONE cell-0 env change (tight).\n",
             "ourvzlb25r70 + TWO cell-0 env changes (tight 6.0 + bonus 3.0 = ourvzlb30t625 with tight 6.25 -> 6.0).\n"),
            ("    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts\n"
             "    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a\n",
             "    # receipt (ops/ourvzl_combo_t600_gate.py): run_stats motion_relink_tight_edges vs the REAL 6.25-gate counts\n"
             "    # (ourvzlb30t625 and ourvzlt625 both logged exactly these). The tight pass is effectively a\n"),
            ("vs the 6.5-gate counts {", "vs ourvzlb30t625's 6.25-gate counts {")]
    for a, b in reps:
        if block.count(a) != 1:
            raise SystemExit("xcheck text not as expected: %r" % a[:60])
        block = block.replace(a, b, 1)
    if "%r" % T625 not in block or "6.5-gate" in block:
        raise SystemExit("receipt does not compare against the 6.25-gate counts")
    return block


def patch_t6(t, tag):
    t2, pats, forbid = ORIG_PATCH(t, tag)
    old = "        # with ONE cell-0 env change (tight: tight 6.0, bonus 3.0). = need['ourvzlb25r70'] with the changed knob's\n"
    new = ("        # with TWO cell-0 env changes (tight 6.0 + bonus 3.0 = ourvzlb30t625 with tight 6.25 -> 6.0). = need['ourvzlb30t625']"
           " with the tight\n")
    if t2.count(old) != 1:
        raise SystemExit("need comment not as expected")
    t2 = t2.replace(old, new, 1)
    for tg in [REF, "ourvzlb30", "ourvzlt625", "ourvzlffb30", "ourvzlb25r70ff", "ourvzlb35t625", "ourvzlb40t625"]:
        if "'%s'" % tg not in t:
            continue
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
        raise SystemExit("expected exactly 4 one-line registry edits, got %d" % n_rep)
    compile(t2, str(E.GATE), "exec")
    return t2, pats, forbid


_REF_SRC = {}


def _ref_source():
    if "v" not in _REF_SRC:
        _REF_SRC["v"] = None
        d = E.ROOT / "data" / ("out_" + REF)
        logs = sorted(d.glob("*.log"))
        if logs and (d / "run_stats.csv").is_file() and "GATE_PASS" in E.gate_file(logs[0], REF):
            with open(d / "run_stats.csv", newline="", encoding="utf-8") as fh:
                rs = list(csv.DictReader(fh))
            if {r["dataset"]: int(float(r["motion_relink_tight_edges"])) for r in rs} != T625:
                raise SystemExit("ourvzlb30t625's real run_stats tight edges are not the pinned 6.25 counts")
            _REF_SRC["v"] = (E.log_text(logs[0]), rs)
    return _REF_SRC["v"]


def sub1(pat, repl, s):
    s2, n = re.subn(pat, repl, s)
    if n != 1:
        raise SystemExit("synthetic: %r matched %d times (want 1)" % (pat, n))
    return s2


def synth_t6(tag, src, rs_rows, mut=None):
    mut = dict(mut or {})
    use = mut.pop("src", None)
    real = None if use == "b25r70" else _ref_source()
    if real is None:
        return ORIG_SYNTH(tag, C.bonus_subs(src), rs_rows, mut)  # C.bonus_subs: 2.5 -> 3.0; E.synth: tight 6.5 -> 6.0
    s, rs = real
    if s.count(C.BT_XENV_LINE) != 1:
        raise SystemExit("synthetic: ourvzlb30t625 XENV line not exactly once in its log")
    s = s.replace(C.BT_XENV_LINE, XENV_LINE)
    s = sub1(r"ARM_T625H tight_um=6\.25(?!\d)", "ARM_T60H tight_um=6.0", s)
    s = sub1(r'"motion_relink_tight_um": 6\.25(?!\d)', '"motion_relink_tight_um": 6.0', s)
    s = sub1(r"(MOTION_RELINK_TIGHT_UM +)6\.25(?!\d)", r"\g<1>6.0", s)
    s = C.apply_mut(s, mut)
    rows = [dict(r) for r in rs]
    step = mut.get("tight_step", -7)
    for r in rows:
        r["motion_relink_tight_edges"] = str(T625[r["dataset"]] + step)
    return s, C.write_rs(rs, rows)


def mutants_t6(tag):
    m = ORIG_MUTANTS(tag)
    m.update({
        "pos_syn_from_ourvzlb25r70": ({"src": "b25r70"}, None),
        "neg_syn_t625_marker": ({"extra_lines": ["ARM_T625H tight_um=6.25"]}, "log contains"),
        "neg_syn_t625_echo": ({"extra_lines": ['  "motion_relink_tight_um": 6.25,']}, "log contains"),
        "neg_syn_t625_cell9": ({"extra_lines": [C9T % "6.25"]}, "log contains"),
        "neg_syn_t65_cell9": ({"extra_lines": [C9T % "6.5"]}, "log contains"),
        "neg_syn_t675_echo": ({"extra_lines": ['  "motion_relink_tight_um": 6.75,']}, "log contains"),
        "neg_syn_t70_echo": ({"extra_lines": ['  "motion_relink_tight_um": 7.0,']}, "log contains"),
        "neg_syn_near_tight_echo": ({"extra_lines": ['  "motion_relink_tight_um": 6.05,']}, "log contains"),
        "neg_syn_tight_echo_missing": ({"replace": [('"motion_relink_tight_um": 6.0', '"motion_relink_tight_uz": 6.0')]}, None),
        "neg_syn_tight_cell9_missing": ({"replace": [((C9T % "6.0").strip(), (C9T % "6.0").strip().replace("TIGHT", "TIGHZ"))]}, None),
        "neg_syn_old_bonus_marker": ({"extra_lines": ["ARM_STK3B learned_bonus=2.5"]}, "log contains"),
        "neg_syn_other_bonus_cell9": ({"extra_lines": [C9B % "3.5"]}, "log contains"),
        "neg_syn_bonus_marker_missing": ({"replace": [("ARM_STK3B learned_bonus=3.0", "ARM_STK3B gone")]}, None),
        "neg_syn_b30t625_xenv": ({"extra_lines": [C.BT_XENV_LINE]}, "log contains"),
        "neg_syn_t625_xenv": ({"extra_lines": [C.T625_XENV_LINE]}, "log contains"),
    })
    return m


def install(tag):
    if tag != TAG:
        raise SystemExit("unknown tag " + tag)
    have = lambda tg: bool(list((E.ROOT / "data").glob("out_%s/*.log" % tg)))  # noqa: E731
    E.BASE_TIGHT = dict(T625)  # receipt + synthetic tight edges are relative to the REAL 6.25-gate counts
    E.SPEC[TAG] = SPEC
    E.derive, E.xcheck, E.patch, E.synth, E.mutants = derive_t6, xcheck_t6, patch_t6, synth_t6, mutants_t6
    E.NEG_REAL = ("ourvzlb25r70", "ourvzlb30", "ourvzlt625", "ourvzlb25r70ff") + tuple(
        x for x in (REF, "ourvzlb35t625", "ourvzlb40t625") if have(x))
    E.REGRESS_REQUIRED = tuple(E.REGRESS_REQUIRED) + tuple(
        x for x in ("ourvzlb30", "ourvzlt625", "ourvzlt675", "ourvzlb25r70ff") + ((REF,) if have(REF) else ())
        if x not in E.REGRESS_REQUIRED)
    E.SIBLINGS = tuple(E.SIBLINGS) + tuple(
        x for x in (C.BT, C.FB, "ourvzlb35t625", "ourvzlb40t625") if x not in E.SIBLINGS)
    if _ref_source() is None:
        raise SystemExit("ourvzlb30t625's real visible log / run_stats missing or not passing; the receipt is pinned to it")
    print("tag %s | synthetic source: ourvzlb30t625 REAL log + run_stats (tight 6.25 -> 6.0, edges -7) | real negatives: %s"
          % (tag, list(E.NEG_REAL)))
    E.install(tag)
