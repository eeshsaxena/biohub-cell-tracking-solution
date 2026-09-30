#!/usr/bin/env python3
r"""Gate installers for the two 09-29 final-day combo arms. Reuses ops/ourvzl_envarm_gate.py (imported as E: patch /
install / selftest / restore-on-failure / sibling + regression checks) and overrides only the per-arm pieces, so the
install is SEQUENTIAL, re-reads gate.py, backs it up to gate.py.bak_<tag> and restores it if any self-test fails.

ourvzlb30t625 (scratch_kernels/build_ourvzlb30t625.py) = ourvzlb25r70 + tight 6.5 -> 6.25 + bonus 2.5 -> 3.0:
  * need/forbid = E.derive's ourvzlt625 derivation (tight swapped to 6.25, T625H allowlist, old-6.5 forbids, cell-9
    echoes) with the bonus marker / cell-2 echo / cell-9 echo additionally swapped to 3.0, the bonus lookahead forbids
    re-pointed at 3.0 and explicit 2.5 forbids added (= ourvzlb30's bonus requirements);
  * union cross-check against the LIVE ourvzlb30 + ourvzlt625 entries: every need pattern of either (XENV aside, and
    minus the other arm's old value) is in the new need and nothing else is; every forbid of either that does not hit a
    legit print of this arm is in the new forbid;
  * cross-check block = ourvzlb25r70's renamed + ourvzlt625's tight-edge receipt (<= the 6.5-gate counts on all four
    movies, < on one: the tight pass is bonus-independent, so the bonus does not change the receipt).
ourvzlffb30 (scratch_kernels/build_ourvzlffb30.py) = ourvzlb25r70ff + bonus 2.5 -> 3.0:
  * need = need['ourvzlb25r70ff'] (ast) minus its XENV with the bonus marker / cell-2 echo swapped to 3.0, + the cell-9
    echoes MOTION_RELINK_TIGHT_UM 6.5 / MOTION_RELINK_LEARNED_BONUS 3.0, + this XENV; forbid = forbid['ourvzlb25r70ff']
    with the XENV lookahead renamed, the bonus lookaheads re-pointed at 3.0, + explicit 2.5 forbids + cell-9 lookaheads;
  * cross-check block = ourvzlb25r70ff's (flowfix bookkeeping) renamed + the bonus receipt (tight edges == the 6.5-gate
    counts, which ourvzlb25r70ff logged exactly);
  * synthetic positives/mutants are built from ourvzlb25r70ff's REAL visible log + run_stats.
"""
import csv
import io
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ourvzl_envarm_gate as E  # noqa: E402

ORIG_DERIVE, ORIG_XCHECK, ORIG_PATCH, ORIG_SYNTH, ORIG_MUTANTS = E.derive, E.xcheck, E.patch, E.synth, E.mutants

B_MARK_NEW = r"ARM_STK3B learned_bonus=3\.0(?!\d)"
B_ECHO_NEW = r'"motion_relink_learned_bonus": 3\.0(?!\d)'
B_C9_OLD, B_C9_NEW = r"MOTION_RELINK_LEARNED_BONUS +2\.5(?!\d)", r"MOTION_RELINK_LEARNED_BONUS +3\.0(?!\d)"
T_C9_65 = r"MOTION_RELINK_TIGHT_UM +6\.5(?!\d)"
B_FMARK_NEW = r"ARM_STK3B learned_bonus=(?!3\.0(?!\d))"
B_FECHO_NEW = r'"motion_relink_learned_bonus": (?!3\.0(?!\d))'
B_FC9_OLD, B_FC9_NEW = r"MOTION_RELINK_LEARNED_BONUS +(?!2\.5(?!\d))\d", r"MOTION_RELINK_LEARNED_BONUS +(?!3\.0(?!\d))\d"
T_FC9_65 = r"MOTION_RELINK_TIGHT_UM +(?!6\.5(?!\d))\d"
B_OLD_FORBIDS = [r"ARM_STK3B learned_bonus=2\.5(?!\d)", r'"motion_relink_learned_bonus": 2\.5(?!\d)']
B_SUBS = [(r"ARM_STK3B learned_bonus=2\.5(?!\d)", "ARM_STK3B learned_bonus=3.0"),
          (r'"motion_relink_learned_bonus": 2\.5(?!\d)', '"motion_relink_learned_bonus": 3.0'),
          (r"(MOTION_RELINK_LEARNED_BONUS +)2\.5(?!\d)", r"\g<1>3.0")]
C9T = "  MOTION_RELINK_TIGHT_UM                   %s"
C9B = "  MOTION_RELINK_LEARNED_BONUS              %s"


def swap1(lst, old, new, what):
    if lst.count(old) != 1:
        raise SystemExit("%s: %r not exactly once (%d)" % (what, old, lst.count(old)))
    return [new if p == old else p for p in lst]


def check_forbid(forbid, good, bad):
    for line in good:
        hit = [p for p in forbid if re.search(p, line)]
        if hit:
            raise SystemExit("new forbid list hits a legitimate print %r via %r" % (line[:80], hit))
    for line in bad:
        if not any(re.search(p, line) for p in forbid):
            raise SystemExit("new forbid list does not catch %r" % line)


def bonus_subs(s):
    for pat, repl in B_SUBS:
        s, n = re.subn(pat, repl, s)
        if n != 1:
            raise SystemExit("synthetic: bonus swap %r matched %d times (want 1)" % (pat, n))
    return s


def write_rs(rs_rows, rows):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=list(rs_rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return out.getvalue()


def apply_mut(s, mut):
    for a, b in mut.get("replace", []):
        if a not in s:
            raise SystemExit("synthetic mutant: %r not in the log" % a)
        s = s.replace(a, b)
    for extra in mut.get("extra_lines", []):
        i = s.find("Prediction completed")
        j = s.rfind("\n", 0, i) + 1 if i >= 0 else len(s)
        s = s[:j] + extra + "\n" + s[j:]
    return s


# ====================================================================== ARM 1: ourvzlb30t625
BT = "ourvzlb30t625"
BT_SPEC = dict(kind="tight", t="6.25", b="3.0", xt="6.25", xb="3.00", mark="T625H", pfx="_zbt")
BT_XENV_LINE = "ARM_XENV tag=ourvzlb30t625 TIGHT=6.25 BONUS=3.00 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
B30_XENV_LINE = "ARM_XENV tag=ourvzlb30 TIGHT=6.5 BONUS=3.00 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
T625_XENV_LINE = "ARM_XENV tag=ourvzlt625 TIGHT=6.25 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"


def derive_bt(t, tag):
    sp = E.SPEC[tag]
    E.SPEC[tag] = dict(sp, b="2.5")  # the ourvzlt625 derivation (bonus still 2.5), then swap the bonus on top
    try:
        pats, forbid = ORIG_DERIVE(t, tag)
    finally:
        E.SPEC[tag] = sp
    if E.xenv_line(tag, sp) != BT_XENV_LINE:
        raise SystemExit("XENV line mismatch: %r" % E.xenv_line(tag, sp))
    pats = swap1(pats, E.OLD_B_MARK, B_MARK_NEW, "need")
    pats = swap1(pats, E.OLD_B_ECHO, B_ECHO_NEW, "need")
    pats = swap1(pats, B_C9_OLD, B_C9_NEW, "need")
    forbid = swap1(forbid, E.OLD_B_FMARK, B_FMARK_NEW, "forbid")
    forbid = swap1(forbid, E.OLD_B_FECHO, B_FECHO_NEW, "forbid")
    forbid = swap1(forbid, B_FC9_OLD, B_FC9_NEW, "forbid")
    forbid += [p for p in B_OLD_FORBIDS if p not in forbid]
    # ---- union cross-check against the LIVE single-change entries
    n30, n625 = E.need_of(t, "ourvzlb30"), E.need_of(t, "ourvzlt625")
    x30 = [p for p in n30 if p.startswith("ARM_XENV")]
    x625 = [p for p in n625 if p.startswith("ARM_XENV")]
    if len(x30) != 1 or len(x625) != 1:
        raise SystemExit("ourvzlb30 / ourvzlt625 need entries do not carry exactly one XENV each")
    old_t = {E.OLD_T_MARK, E.OLD_T_ECHO, T_C9_65}
    old_b = {E.OLD_B_MARK, E.OLD_B_ECHO, B_C9_OLD}
    if not old_t <= set(n30) or not old_b <= set(n625):
        raise SystemExit("ourvzlb30 / ourvzlt625 entries do not carry the other knob's old value where expected")
    union = (set(n30) - set(x30) - old_t) | (set(n625) - set(x625) - old_b)
    mine = set(pats) - {E.esc(BT_XENV_LINE)}
    if union != mine:
        raise SystemExit("need is not the ourvzlb30 + ourvzlt625 union: extra %r missing %r"
                         % (sorted(mine - union), sorted(union - mine)))
    good = [BT_XENV_LINE, "ARM_T625H tight_um=6.25", "ARM_STK3B learned_bonus=3.0", '  "motion_relink_tight_um": 6.25,',
            '  "motion_relink_learned_bonus": 3.0,', C9T % "6.25", C9B % "3.0", "ARM_STK3V velocity_weight=0.25",
            '  "motion_relink_velocity_weight": 0.25,', "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
            '  "rawlink_min_prob": 0.7,', "ARM_SV_ZONLY=1", "ARM_V1284_YX module_patched=1",
            "SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0.1120 frac_clipped=0.1367 gain=2.00",
            "ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0.3361 z_nonzero=25848 final_z_add=0 gather_int_z=1",
            '  "output_linefit_weight": 0.8,', '  "short_track_rescue_trigger_removed_frac": 0.1,']
    bad = [E.BASE_XENV_LINE, B30_XENV_LINE, T625_XENV_LINE, "ARM_T65H tight_um=6.5", '"motion_relink_tight_um": 6.5,',
           C9T % "6.5", "ARM_STK3B learned_bonus=2.5", '"motion_relink_learned_bonus": 2.5,', C9B % "2.5",
           '"motion_relink_learned_bonus": 1.6,', C9B % "1.6", "ARM_T675H tight_um=6.75", C9T % "7.0",
           "Traceback (most recent call last)", "ARM_FLOWFIX enabled=True", "ARM_LCEFR patch applied to predictor"]
    check_forbid(forbid, good, bad)
    f_parents = set(E.forbid_of(t, "ourvzlb30", (E.BASE_TAG, E.SR_TAG, "ourvzlb30"))) | \
        set(E.forbid_of(t, "ourvzlt625", (E.BASE_TAG, E.SR_TAG, "ourvzlt625")))
    must = {p for p in f_parents if not p.startswith("ARM_XENV tag=(?!") and not any(re.search(p, g) for g in good)}
    if not must <= set(forbid):
        raise SystemExit("forbid misses parent forbids that are compatible with this arm: %r" % sorted(must - set(forbid)))
    if len(set(pats)) != len(pats) or len(set(forbid)) != len(forbid):
        raise SystemExit("duplicate need/forbid patterns")
    return pats, forbid


def xcheck_bt(t, tag):
    block = ORIG_XCHECK(t, tag)
    old = "ourvzlb25r70 + ONE cell-0 env change (tight).\n"
    if block.count(old) != 1:
        raise SystemExit("xcheck head not as expected")
    return block.replace(old, "ourvzlb25r70 + TWO cell-0 env changes (tight 6.25 + bonus 3.0).\n", 1)


def patch_bt(t, tag):
    t2, pats, forbid = ORIG_PATCH(t, tag)
    old = "        # with ONE cell-0 env change (tight: tight 6.25, bonus 3.0). = need['ourvzlb25r70'] with the changed knob's\n"
    new = "        # with TWO cell-0 env changes (tight 6.25 + bonus 3.0 = ourvzlt625 + ourvzlb30). = need['ourvzlb25r70'] with both knobs'\n"
    if t2.count(old) != 1:
        raise SystemExit("need comment not as expected")
    t2 = t2.replace(old, new, 1)
    compile(t2, str(E.GATE), "exec")
    return t2, pats, forbid


def synth_bt(tag, src, rs_rows, mut=None):
    mut = dict(mut or {})
    # bonus swapped in the SOURCE first so mutants that re-inject old values are not rewritten
    return ORIG_SYNTH(tag, bonus_subs(src), rs_rows, mut)


def mutants_bt(tag):
    m = ORIG_MUTANTS(tag)
    m.update({
        "neg_syn_old_bonus_marker": ({"extra_lines": ["ARM_STK3B learned_bonus=2.5"]}, "log contains"),
        "neg_syn_old_bonus_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 2.5,']}, "log contains"),
        "neg_syn_old_bonus_cell9": ({"extra_lines": [C9B % "2.5"]}, "log contains"),
        "neg_syn_old_tight_cell9": ({"extra_lines": [C9T % "6.5"]}, "log contains"),
        "neg_syn_other_bonus_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 1.6,']}, "log contains"),
        "neg_syn_bonus_marker_missing": ({"replace": [("ARM_STK3B learned_bonus=3.0", "ARM_STK3B gone")]}, None),
        "neg_syn_bonus_echo_missing": ({"replace": [('"motion_relink_learned_bonus": 3.0', '"motion_relink_learned_bonuz": 3.0')]}, None),
        "neg_syn_b30_xenv": ({"extra_lines": [B30_XENV_LINE]}, "log contains"),
        "neg_syn_t625_xenv": ({"extra_lines": [T625_XENV_LINE]}, "log contains"),
    })
    return m


# ====================================================================== ARM 2: ourvzlffb30
FB = "ourvzlffb30"
FB_BASE = "ourvzlb25r70ff"
FB_SPEC = dict(kind="bonus", t="6.5", b="3.0", xt="6.5", xb="3.00", pfx="_zfb3")
FF_XENV_LINE = ("ARM_XENV tag=ourvzlb25r70ff TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 "
                "ENDS=1 DEADLINE_S=34200 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx")
FB_XENV_LINE = FF_XENV_LINE.replace("tag=ourvzlb25r70ff ", "tag=ourvzlffb30 ").replace("BONUS=2.50 ", "BONUS=3.00 ")
FF_XFORBID = r"ARM_XENV tag=(?!ourvzlb25r70ff )"
FF_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK|FLOWFIX)\b)[A-Z0-9]+"


def derive_fb(t, tag):
    watch = (E.BASE_TAG, E.SR_TAG, FB_BASE, tag)
    base = list(E.need_of(t, FB_BASE))
    xff = E.esc(FF_XENV_LINE)
    for p in (xff, E.OLD_B_MARK, E.OLD_B_ECHO, E.OLD_T_MARK, E.OLD_T_ECHO):
        if base.count(p) != 1:
            raise SystemExit("need['ourvzlb25r70ff'] lacks %r exactly once" % p)
    if sum("ARM_XENV" in p for p in base) != 1:
        raise SystemExit("need['ourvzlb25r70ff'] carries more than one XENV")
    pats = [p for p in base if p != xff]
    pats = swap1(pats, E.OLD_B_MARK, B_MARK_NEW, "need")
    pats = swap1(pats, E.OLD_B_ECHO, B_ECHO_NEW, "need")
    if any(p.startswith("MOTION_RELINK_") for p in pats):
        raise SystemExit("need['ourvzlb25r70ff'] already pins cell-9 echoes; installer not written for that")
    pats += [T_C9_65, B_C9_NEW, E.esc(FB_XENV_LINE)]
    if sum(p.startswith(("SV_ARM_HSG200 nodes=", "ARM_SV_Z_TO_ARR frames=100 nodes=")) for p in pats) != 8:
        raise SystemExit("the eight per-movie V1284 / z-to-arr coordinate pins are not all carried over")
    if sum(p.startswith("ARM_FLOWFIX") for p in pats) != 5:
        raise SystemExit("the five ARM_FLOWFIX patterns are not all carried over")
    if sum(("RAWLINK" in p or "rawlink" in p) and not p.startswith("ARM_XENV") for p in pats) != 6:
        raise SystemExit("rawlink patterns not carried over intact")
    fz = E.forbid_of(t, FB_BASE, watch)
    for p in (FF_XFORBID, FF_ALLOW, E.OLD_B_FMARK, E.OLD_B_FECHO, E.OLD_T_FMARK, E.OLD_T_FECHO):
        if fz.count(p) != 1:
            raise SystemExit("forbid['ourvzlb25r70ff'] lacks %r exactly once" % p)
    rw = {FF_XFORBID: r"ARM_XENV tag=(?!%s )" % tag, E.OLD_B_FMARK: B_FMARK_NEW, E.OLD_B_FECHO: B_FECHO_NEW}
    add = B_OLD_FORBIDS + [T_FC9_65, B_FC9_NEW]
    forbid = [rw.get(p, p) for p in fz] + [p for p in add if p not in fz]
    if FF_XFORBID in forbid or E.OLD_B_FMARK in forbid or E.OLD_B_FECHO in forbid:
        raise SystemExit("an old-value forbid survived the rewrite")
    good = [FB_XENV_LINE, "ARM_STK3B learned_bonus=3.0", '  "motion_relink_learned_bonus": 3.0,', C9B % "3.0",
            "ARM_T65H tight_um=6.5", '  "motion_relink_tight_um": 6.5,', C9T % "6.5", "ARM_STK3V velocity_weight=0.25",
            '  "motion_relink_velocity_weight": 0.25,',
            "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected", '  "rawlink_min_prob": 0.7,',
            "ARM_SV_ZONLY=1", "ARM_V1284_YX module_patched=1",
            "ARM_FLOWFIX enabled=True TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 threads=4 deadline_s=34200",
            "ARM_FLOWFIX [6bba_05b6850b] status=ok windows=792 flagged=36 acted=25 changed=2 bridged=1 dups=0 edges=5867->5868 divs=6->6 max_in=1 secs=7.3 elapsed_h=0.46",
            "SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0.1120 frac_clipped=0.1367 gain=2.00",
            "ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0.3361 z_nonzero=25848 final_z_add=0 gather_int_z=1"]
    bad = [FF_XENV_LINE, E.BASE_XENV_LINE, B30_XENV_LINE, "ARM_STK3B learned_bonus=2.5", '"motion_relink_learned_bonus": 2.5,',
           C9B % "2.5", '"motion_relink_learned_bonus": 1.6,', C9B % "1.6", C9T % "6.25", "ARM_T625H tight_um=6.25",
           '"motion_relink_tight_um": 6.25,', "Traceback (most recent call last)", "ARM_FLOWFIX enabled=False",
           "ARM_FLOWFIX [6bba_05b6850b] FALLBACK deadline", "ARM_LCEFR patch applied to predictor"]
    check_forbid(forbid, good, bad)
    # every ourvzlb25r70ff forbid that is compatible with this arm's legit prints is kept verbatim
    must = {p for p in fz if p != FF_XFORBID and not any(re.search(p, g) for g in good)}
    if not must <= set(forbid) or len(set(pats)) != len(pats) or len(set(forbid)) != len(forbid):
        raise SystemExit("forbid lost ourvzlb25r70ff forbids / duplicate patterns")
    return pats, forbid


def xcheck_fb(t, tag):
    pfx = FB_SPEC["pfx"]
    if pfx in t:
        raise SystemExit("variable prefix %s already used in gate.py" % pfx)
    s = t.index("# --- ourvzlb25r70ff (ops/add_ourvzlb25r70ff_gate.py)")
    e = t.index('if "ourvzlb25r70ff" in tags:\n', s)
    code = t[e:t.index("\n# --- ", e) + 1]
    if code.count("ourvzlb25r70ff") != 12 or code.count("ourvzlb25r70") != 12 or code.count("_ozfx") != 106 \
            or len(re.findall(r"_ozfx[a-z0-9]", code)) != 106 or "\n#" in code.rstrip("\n") or "_ozfxrs = " not in code:
        raise SystemExit("the live ourvzlb25r70ff cross-check block is not the one this installer was written against")
    block = code.replace("ourvzlb25r70ff", tag).replace("_ozfx", pfx)
    block += (
        "    # receipt (ops/ourvzl_combo_gate.py): run_stats motion_relink_tight_edges == the 6.5-gate V1284-body counts\n"
        "    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff / ourvzlb30 all logged exactly these): the tight pass does not\n"
        "    # depend on the bonus.\n"
        "    %sTB = %r\n" % (pfx, E.BASE_TIGHT) +
        "    if %srs is not None:\n" % pfx +
        "        %stg = {}\n" % pfx +
        "        for d in sorted(%sTB):\n" % pfx +
        "            try: %stg[d] = int(float((%srs.get(d) or {})[\"motion_relink_tight_edges\"]))\n" % (pfx, pfx) +
        "            except (KeyError, TypeError, ValueError): %stg[d] = None\n" % pfx +
        "        if any(v is None for v in %stg.values()):\n" % pfx +
        "            fails.append(f\"%s run_stats has no readable motion_relink_tight_edges: {%stg}\")\n" % (tag, pfx) +
        "        elif %stg != %sTB:\n" % (pfx, pfx) +
        "            fails.append(f\"%s motion_relink_tight_edges {%stg} != the 6.5-gate counts {%sTB}: the tight pass "
        "does not depend on the bonus, so the tight gate or the body moved\")\n" % (tag, pfx, pfx))
    head = ("# --- %s (ops/add_%s_gate.py via ops/ourvzl_combo_gate.py): ourvzlb25r70ff + ONE cell-0 env change (bonus 3.0).\n"
            "# = ourvzlb25r70ff's flowfix cross-check (generated from its block, renamed) + tight edges == the 6.5-gate counts.\n"
            % (tag, tag))
    return head + block


def patch_fb(t, tag):
    t2, pats, forbid = ORIG_PATCH(t, tag)
    old = ("        # --- %s: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)\n"
           "        # with ONE cell-0 env change (bonus: tight 6.5, bonus 3.0). = need['ourvzlb25r70'] with the changed knob's\n"
           "        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_%s.py; ops/add_%s_gate.py).\n"
           % (tag, tag, tag))
    new = ("        # --- %s: ourvzlb25r70ff (ourvzlb25r70, public 0.955, + the IMGFLOW write-time repair) with ONE cell-0\n"
           "        # env change (bonus 2.5 -> 3.0). = need['ourvzlb25r70ff'] with the bonus marker/echo swapped + cell-9\n"
           "        # echoes + this XENV (scratch_kernels/build_%s.py; ops/add_%s_gate.py via ops/ourvzl_combo_gate.py).\n"
           % (tag, tag, tag))
    if t2.count(old) != 1:
        raise SystemExit("need comment not as expected")
    t2 = t2.replace(old, new, 1)
    for tg in (FB_BASE, "ourvzlb30", "ourvzlt625"):
        w = (E.BASE_TAG, E.SR_TAG, tg)
        if E.forbid_of(t2, tg, w) != E.forbid_of(t, tg, w) or E.need_of(t2, tg) != E.need_of(t, tg):
            raise SystemExit("the patch moved the %s entry" % tg)
    compile(t2, str(E.GATE), "exec")
    return t2, pats, forbid


_FF_SRC = {}


def _ff_source():
    if not _FF_SRC:
        d = E.ROOT / "data" / "out_ourvzlb25r70ff"
        _FF_SRC["log"] = E.log_text(next(d.glob("*.log")))
        with open(d / "run_stats.csv", newline="", encoding="utf-8") as fh:
            _FF_SRC["rs"] = list(csv.DictReader(fh))
    return _FF_SRC["log"], _FF_SRC["rs"]


def synth_fb(tag, src, rs_rows, mut=None):
    """ourvzlb25r70ff's REAL visible log (+ run_stats) turned into a plausible ourvzlffb30 log (the src/rs_rows the core
    selftest passes are ourvzlb25r70's and are ignored here)."""
    mut = mut or {}
    s, rs = _ff_source()
    if s.count(FF_XENV_LINE) != 1:
        raise SystemExit("synthetic: ourvzlb25r70ff XENV line not exactly once in its log")
    s = bonus_subs(s.replace(FF_XENV_LINE, FB_XENV_LINE))
    s = apply_mut(s, mut)
    rows = [dict(r) for r in rs]
    for r in rows:
        if mut.get("tight_step"):
            r["motion_relink_tight_edges"] = str(E.BASE_TIGHT[r["dataset"]] + mut["tight_step"])
    return s, write_rs(rs, rows)


def mutants_fb(tag):
    return {
        "neg_syn_base_xenv": ({"extra_lines": [FF_XENV_LINE]}, "log contains"),
        "neg_syn_b25r70_xenv": ({"extra_lines": [E.BASE_XENV_LINE]}, "log contains"),
        "neg_syn_b30_xenv": ({"extra_lines": [B30_XENV_LINE]}, "log contains"),
        "neg_syn_traceback": ({"extra_lines": ["Traceback (most recent call last):"]}, "log contains"),
        "neg_syn_lcefr_line": ({"extra_lines": ["ARM_LCEFR patch applied to predictor"]}, "log contains"),
        "neg_syn_rawlink_disabled": ({"extra_lines": ["ARM_RAWLINK min_prob=-1.0 enabled=False rule=x"]}, "log contains"),
        "neg_syn_v1284_failure": ({"extra_lines": ["V1284 patch anchor mismatch in predictor"]}, "log contains"),
        "neg_syn_sv_pin_changed": ({"replace": [("SV_ARM_HSG200 nodes=7370 ", "SV_ARM_HSG200 nodes=7371 ")]}, "marker missing"),
        "neg_syn_xenv_missing": ({"replace": [(FB_XENV_LINE, "ARM_XENVX gone")]}, None),
        "neg_syn_flowfix_disabled": ({"extra_lines": ["ARM_FLOWFIX enabled=False"]}, "log contains"),
        "neg_syn_flowfix_fallback": ({"extra_lines": ["ARM_FLOWFIX [6bba_05b6850b] FALLBACK deadline"]}, "log contains"),
        "neg_syn_flowfix_line_missing": ({"replace": [("ARM_FLOWFIX [6bba_05b6850b] status=ok", "ARM_FLOWFIX [6bba_05b6850b] status=gone")]}, None),
        "neg_syn_old_marker": ({"extra_lines": ["ARM_STK3B learned_bonus=2.5"]}, "log contains"),
        "neg_syn_old_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 2.5,']}, "log contains"),
        "neg_syn_old_cell9": ({"extra_lines": [C9B % "2.5"]}, "log contains"),
        "neg_syn_other_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 1.6,']}, "log contains"),
        "neg_syn_cell9_tight_other": ({"extra_lines": [C9T % "7.0"]}, "log contains"),
        "neg_syn_new_marker_missing": ({"replace": [("ARM_STK3B learned_bonus=3.0", "ARM_STK3B gone")]}, None),
        "neg_syn_tight_edges_moved": ({"tight_step": 3}, "motion_relink_tight_edges"),
        "neg_syn_orphans60": ({"replace": [("new_isolated=", "new_isolated=6")]}, None),
    }


# ====================================================================== install
def install(tag):
    if tag == BT:
        E.SPEC[BT] = BT_SPEC
        E.derive, E.xcheck, E.patch, E.synth, E.mutants = derive_bt, xcheck_bt, patch_bt, synth_bt, mutants_bt
        E.NEG_REAL = ("ourvzlb25r70", "ourvzlb30", "ourvzlt625", "ourvzlb25r70ff")
    elif tag == FB:
        E.SPEC[FB] = FB_SPEC
        E.derive, E.xcheck, E.patch, E.synth, E.mutants = derive_fb, xcheck_fb, patch_fb, synth_fb, mutants_fb
        E.NEG_REAL = ("ourvzlb25r70ff", "ourvzlb30", "ourvzlb25r70")
    else:
        raise SystemExit("unknown tag " + tag)
    E.REGRESS_REQUIRED = tuple(E.REGRESS_REQUIRED) + tuple(
        x for x in ("ourvzlb30", "ourvzlt625", "ourvzlt675", "ourvzlb25r70ff") if x not in E.REGRESS_REQUIRED)
    E.SIBLINGS = tuple(E.SIBLINGS) + tuple(x for x in (BT, FB) if x not in E.SIBLINGS)
    E.install(tag)
