#!/usr/bin/env python3
r"""Shared gate installer for the 09-29 last-slot env arms on the ourvzlb25r70 body (scratch_kernels/ourvzl_envarm.py):
each arm is v_ourvzlb25r70 (public 0.955) with ONE cell-0 env change. Thin per-tag wrappers ops/add_<tag>_gate.py call
install(<tag>). Run from the project root: it re-reads ops/gate.py, backs it up (gate.py.bak_<tag>), patches it,
self-tests, and restores the backup if any self-test fails.
Dry run: ENVARM_GATE=<copy of gate.py> python ops/add_<tag>_gate.py

Everything is DERIVED from the live ourvzlb25r70 entry (read out of gate.py with ast), not retyped:
  * need = need['ourvzlb25r70'] minus its XENV, with the changed knob's cell-0 marker + cell-2 echo swapped to the new
    value (tight arms: ARM_T<n>H tight_um=<v> + "motion_relink_tight_um": <v>; bonus arms: ARM_STK3B learned_bonus=<v>
    + "motion_relink_learned_bonus": <v>), + the cell-9 PP_BASE_CONFIG echoes MOTION_RELINK_TIGHT_UM / _LEARNED_BONUS at
    the arm's values (read from globals AFTER tracking), + the sr / lf cell-2 echoes for those arms, + this arm's XENV.
    Every V1284 / z-to-arr / per-movie SV_ARM_HSG200 + ARM_SV_Z_TO_ARR coordinate pin is kept EXACTLY (all these knobs act
    after detection) and the six rawlink patterns are kept. FINAL counts are NOT pinned (tight/bonus/sr move topology);
  * forbid = forbid['ourvzlb25r70'] with its XENV lookahead renamed, the changed knob's value lookaheads re-pointed at the
    new value (so the OLD value and ANY other value fail), the ARM_ allowlist T65H -> T<n>H for tight arms, PLUS explicit
    old-value forbids (marker, cell-2 echo), cell-9 echo lookaheads for both linker knobs, and for sr/lf a non-0.0 trigger
    / "adaptive_short_track_rescue": false / a non-1.0 line-fit weight (0.8 explicitly);
  * the tag joins RL_TAGS + the orphan cap + tol 0.15 + sv_mark (INSIDE the dict literal) like ourvzlb25r70, and gets
    ourvzlb25r70's per-movie cross-check block (generated from the live block: tag + variable prefix renamed; written
    nodes/edges/divisions == (FINAL nodes, rawlink final=, safe divs), run_stats agrees, smoothed + skipped == nodes);
  * receipts: tight arms: run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts (24585/18170/5819/65963,
    reproduced exactly by ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff): the tight pass is effectively a max-cardinality
    matching over the gate graph (monotone in the gate, independent of the bonus), so 6.25 must be <= on all four and <
    on one, 6.75 >= on all four and > on one; bonus arms: == on all four (bonus-independent, as t65s3/t65b20/t65b25 showed
    on the t6 body); sr: t65b25r70sr's rescue receipts (renamed): triggered == 1 everywhere, components <= nodes <=
    budget, components > 0 on at least one movie.
Self-tests: the ourvzlb25r70 and ourvzlb25r70ff logs must FAIL as <tag>; ourvzlb25r70 / ourvzlb25 / t65b25r70 /
t65b25r70sr / t65b25r70ff / t6stk3 / t6r70 / ourvzlb25r70ff / t65b25r70ffsr / mixyx50r70 (+ every sibling env arm already
installed that has a visible log) must still PASS as themselves; every need entry present before the patch must still
exist. A SYNTHETIC <tag> log (ourvzlb25r70's REAL visible log + run_stats with the markers/echoes/XENV swapped and the
receipt columns moved the right way) must PASS and every mutant must FAIL (on its own message where it has one).
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

ROOT = pathlib.Path(os.environ.get("ENVARM_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("ENVARM_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
BASE_TAG = "ourvzlb25r70"
SR_TAG = "t65b25r70sr"
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
BASE_TIGHT = {"44b6_0113de3b": 24585, "44b6_0b24845f": 18170, "6bba_05b6850b": 5819, "6bba_05db0fb1": 65963}
BASE_XENV = r"ARM_XENV tag=ourvzlb25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
BASE_XENV_LINE = "ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
OLD_XFORBID = r"ARM_XENV tag=(?!ourvzlb25r70 )"
OLD_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\b)[A-Z0-9]+"
OLD_T_MARK = r"ARM_T65H tight_um=6\.5"
OLD_T_ECHO = r'"motion_relink_tight_um": 6\.5(?!\d)'
OLD_B_MARK = r"ARM_STK3B learned_bonus=2\.5"
OLD_B_ECHO = r'"motion_relink_learned_bonus": 2\.5(?!\d)'
OLD_T_FMARK = r"ARM_T\d+H tight_um=(?!6\.5(?!\d))"
OLD_T_FECHO = r'"motion_relink_tight_um": (?!6\.5(?!\d))'
OLD_B_FMARK = r"ARM_STK3B learned_bonus=(?!2\.5(?!\d))"
OLD_B_FECHO = r'"motion_relink_learned_bonus": (?!2\.5(?!\d))'
REGRESS_REQUIRED = ("ourvzlb25r70", "ourvzlb25", "t65b25r70", "t65b25r70sr", "t65b25r70ff", "t6stk3", "t6r70",
                    "ourvzlb25r70ff", "t65b25r70ffsr", "mixyx50r70")
SIBLINGS = ("ourvzlt625", "ourvzlt675", "ourvzlb30", "ourvzlb20", "ourvzlsr", "ourvzllf100")
NEG_REAL = ("ourvzlb25r70", "ourvzlb25r70ff")

SPEC = {
    "ourvzlt625": dict(kind="tight", t="6.25", b="2.5", xt="6.25", xb="2.50", mark="T625H", pfx="_zt625"),
    "ourvzlt675": dict(kind="tight", t="6.75", b="2.5", xt="6.75", xb="2.50", mark="T675H", pfx="_zt675"),
    "ourvzlb30": dict(kind="bonus", t="6.5", b="3.0", xt="6.5", xb="3.00", pfx="_zb30"),
    "ourvzlb20": dict(kind="bonus", t="6.5", b="2.0", xt="6.5", xb="2.00", pfx="_zb20"),
    "ourvzlsr": dict(kind="sr", t="6.5", b="2.5", xt="6.5", xb="2.50", extra="SR=armed ", pfx="_zsr"),
    "ourvzllf100": dict(kind="lf", t="6.5", b="2.5", xt="6.5", xb="2.50", extra="LINEFIT_W=1.0 ", pfx="_zlf"),
}


def esc(v):
    return v.replace(".", r"\.")


def xenv_line(tag, sp):
    return ("ARM_XENV tag=%s TIGHT=%s BONUS=%s RAWLINK=0.70 %sV1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
            % (tag, sp["xt"], sp["xb"], sp.get("extra", "")))


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


def forbid_of(src, key, watch):
    body = ast.parse(src).body
    assigns = {}
    for node in body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            k = _forbid_key(node.targets[0])
            if k is not None:
                assigns.setdefault(k, []).append(node)
        if isinstance(node, ast.For) and isinstance(node.iter, (ast.Tuple, ast.List)):
            names = {e.value for e in node.iter.elts if isinstance(e, ast.Constant)}
            if names & set(watch):
                raise SystemExit("a top-level loop rewrites forbid for %r; refusing to resolve by ast" % (names & set(watch)))

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


def derive(t, tag):
    sp = SPEC[tag]
    kind, tv, bv = sp["kind"], sp["t"], sp["b"]
    watch = (BASE_TAG, SR_TAG, tag)
    base = list(need_of(t, BASE_TAG))
    for p in (BASE_XENV, OLD_T_MARK, OLD_T_ECHO, OLD_B_MARK, OLD_B_ECHO):
        if base.count(p) != 1:
            raise SystemExit("need['ourvzlb25r70'] lacks %r exactly once" % p)
    if sum("ARM_XENV" in p for p in base) != 1:
        raise SystemExit("need['ourvzlb25r70'] carries more than one XENV")
    # ---- need
    pats = [p for p in base if p != BASE_XENV]
    if kind == "tight":
        pats = [r"ARM_%s tight_um=%s(?!\d)" % (sp["mark"], esc(tv)) if p == OLD_T_MARK else
                r'"motion_relink_tight_um": %s(?!\d)' % esc(tv) if p == OLD_T_ECHO else p for p in pats]
    elif kind == "bonus":
        pats = [r"ARM_STK3B learned_bonus=%s(?!\d)" % esc(bv) if p == OLD_B_MARK else
                r'"motion_relink_learned_bonus": %s(?!\d)' % esc(bv) if p == OLD_B_ECHO else p for p in pats]
    pats += [r"MOTION_RELINK_TIGHT_UM +%s(?!\d)" % esc(tv), r"MOTION_RELINK_LEARNED_BONUS +%s(?!\d)" % esc(bv)]
    if kind == "sr":
        pats += [r'"short_track_rescue_trigger_removed_frac": 0\.0(?!\d)', r'"adaptive_short_track_rescue": true']
    if kind == "lf":
        pats += [r'"output_linefit_weight": 1\.0(?!\d)']
    xenv = esc(xenv_line(tag, sp))
    pats += [xenv]
    if len(set(pats)) != len(pats) or pats.count(xenv) != 1:
        raise SystemExit("need list malformed: %r" % pats)
    if sum(p.startswith(("SV_ARM_HSG200 nodes=", "ARM_SV_Z_TO_ARR frames=100 nodes=")) for p in pats) != 8:
        raise SystemExit("the eight per-movie V1284 / z-to-arr coordinate pins are not all carried over")
    if sum(("RAWLINK" in p or "rawlink" in p) and not p.startswith("ARM_XENV") for p in pats) != 6:
        raise SystemExit("rawlink patterns not carried over intact")
    # ---- forbid
    fz = forbid_of(t, BASE_TAG, watch)
    for p in (OLD_XFORBID, OLD_ALLOW, OLD_T_FMARK, OLD_T_FECHO, OLD_B_FMARK, OLD_B_FECHO):
        if fz.count(p) != 1:
            raise SystemExit("forbid['ourvzlb25r70'] lacks %r exactly once" % p)
    rw = {OLD_XFORBID: r"ARM_XENV tag=(?!%s )" % tag}
    add = []
    if kind == "tight":
        rw[OLD_T_FMARK] = r"ARM_T\d+H tight_um=(?!%s(?!\d))" % esc(tv)
        rw[OLD_T_FECHO] = r'"motion_relink_tight_um": (?!%s(?!\d))' % esc(tv)
        rw[OLD_ALLOW] = OLD_ALLOW.replace("|T65H|", "|%s|" % sp["mark"])
        add += [r"\bARM_T65H\b", r'"motion_relink_tight_um": 6\.5(?!\d)', r"tight_um=6\.5(?!\d)"]
    if kind == "bonus":
        rw[OLD_B_FMARK] = r"ARM_STK3B learned_bonus=(?!%s(?!\d))" % esc(bv)
        rw[OLD_B_FECHO] = r'"motion_relink_learned_bonus": (?!%s(?!\d))' % esc(bv)
        add += [r"ARM_STK3B learned_bonus=2\.5(?!\d)", r'"motion_relink_learned_bonus": 2\.5(?!\d)']
    add += [r"MOTION_RELINK_TIGHT_UM +(?!%s(?!\d))\d" % esc(tv), r"MOTION_RELINK_LEARNED_BONUS +(?!%s(?!\d))\d" % esc(bv)]
    if kind == "sr":
        add += [r'"short_track_rescue_trigger_removed_frac": (?!0\.0(?!\d))', r'"adaptive_short_track_rescue": false']
    if kind == "lf":
        add += [r'"output_linefit_weight": 0\.8(?!\d)', r'"output_linefit_weight": (?!1\.0(?!\d))']
    forbid = [rw.get(p, p) for p in fz] + [p for p in add if p not in fz]
    if OLD_XFORBID in forbid or (kind == "tight" and (OLD_ALLOW in forbid or OLD_T_FMARK in forbid)) \
            or (kind == "bonus" and OLD_B_FMARK in forbid):
        raise SystemExit("an old-value forbid survived the rewrite")
    # legit prints of THIS arm must not hit any forbid; the old value / other values / other arms must
    good = [xenv_line(tag, sp), "ARM_STK3V velocity_weight=0.25", '  "motion_relink_velocity_weight": 0.25,',
            "ARM_%s tight_um=%s" % (sp.get("mark", "T65H"), tv), "ARM_STK3B learned_bonus=%s" % bv,
            '  "motion_relink_tight_um": %s,' % tv, '  "motion_relink_learned_bonus": %s,' % bv,
            "  MOTION_RELINK_TIGHT_UM                   %s" % tv, "  MOTION_RELINK_LEARNED_BONUS              %s" % bv,
            "ARM_RAWLINK min_prob=0.7 enabled=True rule=raw_ilp_override_final_divisions_protected",
            '  "rawlink_min_prob": 0.7,', "ARM_SV_ZONLY=1", "ARM_V1284_YX module_patched=1",
            "SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0.1120 frac_clipped=0.1367 gain=2.00",
            "ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0.3361 z_nonzero=25848 final_z_add=0 gather_int_z=1",
            '  "output_linefit_weight": %s,' % ("1.0" if kind == "lf" else "0.8"),
            '  "short_track_rescue_trigger_removed_frac": %s,' % ("0.0" if kind == "sr" else "0.1")]
    bad = [BASE_XENV_LINE, "ARM_XENV tag=ourvzlb25r70ff TIGHT=6.5", "ARM_LCEFR patch applied to predictor",
           "Traceback (most recent call last)", "ARM_RAWLINK min_prob=-1.0 enabled=False rule=x", "ARM_FLOWFIX enabled=True",
           '"motion_relink_tight_um": 7.0,', '"motion_relink_learned_bonus": 1.6,', "ARM_T60H tight_um=6.0",
           "  MOTION_RELINK_TIGHT_UM                   7.0", "  MOTION_RELINK_LEARNED_BONUS              1.6"]
    if kind == "tight":
        bad += ["ARM_T65H tight_um=6.5", '"motion_relink_tight_um": 6.5,', "  MOTION_RELINK_TIGHT_UM                   6.5"]
    if kind == "bonus":
        bad += ["ARM_STK3B learned_bonus=2.5", '"motion_relink_learned_bonus": 2.5,',
                "  MOTION_RELINK_LEARNED_BONUS              2.5"]
    if kind == "sr":
        bad += ['"short_track_rescue_trigger_removed_frac": 0.1,', '"adaptive_short_track_rescue": false']
    if kind == "lf":
        bad += ['"output_linefit_weight": 0.8,', '"output_linefit_weight": 0.9,']
    for line in good:
        hit = [p for p in forbid if re.search(p, line)]
        if hit:
            raise SystemExit("new forbid list hits a legitimate print %r via %r" % (line[:70], hit))
    for line in bad:
        if not any(re.search(p, line) for p in forbid):
            raise SystemExit("new forbid list does not catch %r" % line)
    return pats, forbid


def xcheck(t, tag):
    sp = SPEC[tag]
    pfx = sp["pfx"]
    if pfx in t:
        raise SystemExit("variable prefix %s already used in gate.py" % pfx)
    s = t.index("# --- ourvzlb25r70 (ops/add_ourvzlb25r70_gate.py)")
    e = t.index('if "ourvzlb25r70" in tags:\n', s)
    code = t[e:t.index("\n# --- ", e) + 1]
    if code.count("ourvzlb25r70") != 5 or code.count("_ov") != 38 or len(re.findall(r"_ov[a-z]", code)) != 38 \
            or "\n#" in code.rstrip("\n"):
        raise SystemExit("the live ourvzlb25r70 cross-check block is not the one this installer was written against")
    block = code.replace("ourvzlb25r70", tag).replace("_ov", pfx)
    kind = sp["kind"]
    if kind in ("tight", "bonus"):
        cmp_ = {"tight": ("<=", "<") if float(sp["t"]) < 6.5 else (">=", ">"), "bonus": ("==", None)}[kind]
        block += (
            "    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts\n"
            "    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a\n"
            "    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.\n"
            "    %sTB = %r\n" % (pfx, BASE_TIGHT) +
            "    if %srs is not None:\n" % pfx +
            "        %stg = {}\n" % pfx +
            "        for d in sorted(%sTB):\n" % pfx +
            "            try: %stg[d] = int(float((%srs.get(d) or {})[\"motion_relink_tight_edges\"]))\n" % (pfx, pfx) +
            "            except (KeyError, TypeError, ValueError): %stg[d] = None\n" % pfx +
            "        if any(v is None for v in %stg.values()):\n" % pfx +
            "            fails.append(f\"%s run_stats has no readable motion_relink_tight_edges: {%stg}\")\n" % (tag, pfx))
        if kind == "tight":
            ok_all, ok_one = cmp_
            block += (
                "        elif not all(%stg[d] %s %sTB[d] for d in %sTB) or not any(%stg[d] %s %sTB[d] for d in %sTB):\n"
                % (pfx, ok_all, pfx, pfx, pfx, ok_one, pfx, pfx) +
                "            fails.append(f\"%s motion_relink_tight_edges {%stg} vs the 6.5-gate counts {%sTB}: a %s gate must "
                "give %s on all four movies and %s on at least one\")\n" % (tag, pfx, pfx, sp["t"], ok_all, ok_one))
        else:
            block += (
                "        elif %stg != %sTB:\n" % (pfx, pfx) +
                "            fails.append(f\"%s motion_relink_tight_edges {%stg} != the 6.5-gate counts {%sTB}: the tight pass "
                "does not depend on the bonus, so the tight gate or the body moved\")\n" % (tag, pfx, pfx))
    if kind == "sr":
        s2 = t.index("# --- t65b25r70sr (ops/add_t65b25r70sr_gate.py)")
        e2 = t.index('if "t65b25r70sr" in tags:\n', s2)
        sr = t[e2:t.index("\n# --- ", e2) + 1]
        r = sr.index("    # rescue receipts (ops/add_t65b25r70sr_gate.py)")
        tail = sr[r:]
        if tail.count("t65b25r70sr") != 5 or tail.count("_srx") != 18 or len(re.findall(r"_srx[a-z]", tail)) != 18 \
                or "_srxrs" not in tail:
            raise SystemExit("the live t65b25r70sr rescue-receipt block is not the one this installer was written against")
        block += tail.replace("t65b25r70sr", tag).replace("_srx", pfx)
    head = ("# --- %s (ops/add_%s_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + ONE cell-0 env change (%s).\n"
            "# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed)%s.\n"
            % (tag, tag, kind, {"tight": " + the tight-edge monotonicity receipt",
                                "bonus": " + tight edges == the 6.5-gate counts",
                                "sr": " + t65b25r70sr's rescue receipts (renamed)", "lf": ""}[kind]))
    return head + block


def patch(t, tag):
    if "'%s'" % tag in t or '"%s"' % tag in t:
        raise SystemExit("gate entry for %s already exists" % tag)
    pats, forbid = derive(t, tag)
    sp = SPEC[tag]
    comment = ("        # --- %s: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)\n"
               "        # with ONE cell-0 env change (%s: tight %s, bonus %s%s). = need['ourvzlb25r70'] with the changed knob's\n"
               "        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_%s.py; ops/add_%s_gate.py).\n"
               % (tag, sp["kind"], sp["t"], sp["b"], {"sr": ", rescue armed", "lf": ", line-fit weight 1.0"}.get(sp["kind"], ""),
                  tag, tag))
    entry = comment + "        '%s': [\n" % tag + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    xc = xcheck(t, tag)
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
        raise SystemExit("ourvzlb25r70 is not in RL_TAGS / the orphan cap; refusing to guess")
    t2 = t.replace(anchors["need"], entry + anchors["need"], 1)
    t2 = t2.replace(anchors["forbid"], "forbid[%r] = %r\n" % (tag, forbid) + anchors["forbid"], 1)
    t2 = t2.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % tag, 1)
    t2 = t2.replace(anchors["tol"], anchors["tol"] + '"%s": 0.15, ' % tag, 1)
    t2 = rl_re.sub(lambda m: m.group(1) + ', "%s"}' % tag, t2, count=1)
    t2 = or_re.sub(lambda m: m.group(1) + ', "%s"}' % tag + m.group(2), t2, count=1)
    t2 = t2.replace(anchors["svtags"], xc + anchors["svtags"], 1)
    # ---- structural re-checks
    lit = [n for n in ast.parse(t2).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "sv_mark"
           and isinstance(n.value, ast.Dict)]
    if len(lit) != 1 or ast.literal_eval(lit[0].value).get(tag) != "SV_ARM_HSG200" \
            or not t2.index("sv_mark = {") < t2.index('"%s": "SV_ARM_HSG200"' % tag) < t2.index(anchors["svtags"]):
        raise SystemExit("sv_mark entry for %s is not inside the dict literal before sv_tags is computed" % tag)
    watch = (BASE_TAG, SR_TAG, tag)
    if forbid_of(t2, tag, watch) != forbid or need_of(t2, tag) != pats:
        raise SystemExit("re-parse of the patched gate does not return the new need/forbid entries")
    for tg in (BASE_TAG, SR_TAG):
        if forbid_of(t2, tg, watch) != forbid_of(t, tg, watch) or need_of(t2, tg) != need_of(t, tg):
            raise SystemExit("the patch moved the %s entry" % tg)
    if '"%s"' % tag not in rl_re.search(t2).group(1) or '"%s"' % tag not in or_re.search(t2).group(1):
        raise SystemExit("RL_TAGS / orphan cap patch did not land")
    if not (t2.index("RL_TAGS = {") < t2.index('if "%s" in tags:' % tag) < t2.index(anchors["svtags"])):
        raise SystemExit("cross-check block misplaced")
    if t2.count('if "%s" in tags:' % tag) != 1:
        raise SystemExit("cross-check block not exactly once")
    if (need_keys(t2) - need_keys(t)) != {tag} or not need_keys(t) <= need_keys(t2):
        raise SystemExit("need keys changed beyond adding %s" % tag)
    compile(t2, str(GATE), "exec")
    return t2, pats, forbid


def synth(tag, src, rs_rows, mut=None):
    """ourvzlb25r70's REAL visible log (+ run_stats) turned into a plausible <tag> log."""
    sp, mut = SPEC[tag], (mut or {})
    kind, tv, bv = sp["kind"], sp["t"], sp["b"]
    s = src
    if s.count(BASE_XENV_LINE) != 1:
        raise SystemExit("synthetic: ourvzlb25r70 XENV line not exactly once in its log")
    s = s.replace(BASE_XENV_LINE, xenv_line(tag, sp))

    def sub1(pat, repl, s_, n_exp=None):
        s2, n = re.subn(pat, repl, s_)
        if n < 1 or (n_exp is not None and n != n_exp):
            raise SystemExit("synthetic: %r matched %d times" % (pat, n))
        return s2
    if kind == "tight":
        s = sub1(r"ARM_T65H tight_um=6\.5(?!\d)", "ARM_%s tight_um=%s" % (sp["mark"], tv), s)
        s = sub1(r'"motion_relink_tight_um": 6\.5(?!\d)', '"motion_relink_tight_um": %s' % tv, s)
        s = sub1(r"(MOTION_RELINK_TIGHT_UM +)6\.5(?!\d)", r"\g<1>" + tv, s)
    if kind == "bonus":
        s = sub1(r"ARM_STK3B learned_bonus=2\.5(?!\d)", "ARM_STK3B learned_bonus=%s" % bv, s)
        s = sub1(r'"motion_relink_learned_bonus": 2\.5(?!\d)', '"motion_relink_learned_bonus": %s' % bv, s)
        s = sub1(r"(MOTION_RELINK_LEARNED_BONUS +)2\.5(?!\d)", r"\g<1>" + bv, s)
    if kind == "sr":
        s = sub1(r'"short_track_rescue_trigger_removed_frac": 0\.1(?!\d)', '"short_track_rescue_trigger_removed_frac": 0.0', s)
    if kind == "lf":
        s = sub1(r'"output_linefit_weight": 0\.8(?!\d)', '"output_linefit_weight": 1.0', s)
    for a, b in mut.get("replace", []):
        if a not in s:
            raise SystemExit("synthetic mutant: %r not in the log" % a)
        s = s.replace(a, b)
    for extra in mut.get("extra_lines", []):
        i = s.find("Prediction completed")
        j = s.rfind("\n", 0, i) + 1 if i >= 0 else len(s)
        s = s[:j] + extra + "\n" + s[j:]
    rows = [dict(r) for r in rs_rows]
    for r in rows:
        d = r["dataset"]
        if kind == "tight":
            step = mut.get("tight_step", -7 if float(tv) < 6.5 else 7)
            r["motion_relink_tight_edges"] = str(BASE_TIGHT[d] + step)
        if kind == "bonus" and mut.get("tight_step"):
            r["motion_relink_tight_edges"] = str(BASE_TIGHT[d] + mut["tight_step"])
        if kind == "sr":
            comp = mut.get("sr_comp", 3 if d == "6bba_05db0fb1" else 0)
            r.update(short_track_rescue_triggered=str(mut.get("sr_trig", 1)), short_track_rescue_components=str(comp),
                     short_track_rescue_nodes=str(comp * 5), short_track_rescue_budget="120")
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=list(rs_rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return s, out.getvalue()


def mutants(tag):
    sp = SPEC[tag]
    kind, tv, bv = sp["kind"], sp["t"], sp["b"]
    m = {
        "neg_syn_base_xenv": ({"extra_lines": [BASE_XENV_LINE]}, "log contains"),
        "neg_syn_traceback": ({"extra_lines": ["Traceback (most recent call last):"]}, "log contains"),
        "neg_syn_lcefr_line": ({"extra_lines": ["ARM_LCEFR patch applied to predictor"]}, "log contains"),
        "neg_syn_rawlink_disabled": ({"extra_lines": ["ARM_RAWLINK min_prob=-1.0 enabled=False rule=x"]}, "log contains"),
        "neg_syn_v1284_failure": ({"extra_lines": ["V1284 patch anchor mismatch in predictor"]}, "log contains"),
        "neg_syn_sv_pin_changed": ({"replace": [("SV_ARM_HSG200 nodes=7370 ", "SV_ARM_HSG200 nodes=7371 ")]}, "marker missing"),
        "neg_syn_xenv_missing": ({"replace": [(xenv_line(tag, sp), "ARM_XENVX gone")]}, None),
        "neg_syn_cell9_tight_other": ({"extra_lines": ["  MOTION_RELINK_TIGHT_UM                   7.0"]}, "log contains"),
        "neg_syn_cell9_bonus_other": ({"extra_lines": ["  MOTION_RELINK_LEARNED_BONUS              1.6"]}, "log contains"),
        "neg_syn_orphans60": ({"replace": [("new_isolated=", "new_isolated=6")]}, None),
    }
    if kind == "tight":
        m.update({
            "neg_syn_old_marker": ({"extra_lines": ["ARM_T65H tight_um=6.5"]}, "log contains"),
            "neg_syn_old_echo": ({"extra_lines": ['  "motion_relink_tight_um": 6.5,']}, "log contains"),
            "neg_syn_other_marker": ({"extra_lines": ["ARM_T70H tight_um=7.0"]}, "log contains"),
            "neg_syn_new_marker_missing": ({"replace": [("ARM_%s tight_um=%s" % (sp["mark"], tv), "ARM_TXXH gone")]}, None),
            "neg_syn_tight_edges_equal": ({"tight_step": 0}, "motion_relink_tight_edges"),
            "neg_syn_tight_edges_wrong_way": ({"tight_step": 7 if float(tv) < 6.5 else -7}, "motion_relink_tight_edges"),
        })
    if kind == "bonus":
        m.update({
            "neg_syn_old_marker": ({"extra_lines": ["ARM_STK3B learned_bonus=2.5"]}, "log contains"),
            "neg_syn_old_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 2.5,']}, "log contains"),
            "neg_syn_other_echo": ({"extra_lines": ['  "motion_relink_learned_bonus": 1.6,']}, "log contains"),
            "neg_syn_new_marker_missing": ({"replace": [("ARM_STK3B learned_bonus=%s" % bv, "ARM_STK3B gone")]}, None),
            "neg_syn_tight_edges_moved": ({"tight_step": 3}, "motion_relink_tight_edges"),
        })
    if kind == "sr":
        m.update({
            "neg_syn_old_trigger": ({"extra_lines": ['  "short_track_rescue_trigger_removed_frac": 0.1,']}, "log contains"),
            "neg_syn_not_triggered": ({"sr_trig": 0}, "short_track_rescue_triggered"),
            "neg_syn_rescued_nothing": ({"sr_comp": 0}, "restored 0 components"),
        })
    if kind == "lf":
        m.update({
            "neg_syn_old_weight": ({"extra_lines": ['  "output_linefit_weight": 0.8,']}, "log contains"),
            "neg_syn_other_weight": ({"extra_lines": ['  "output_linefit_weight": 0.9,']}, "log contains"),
            "neg_syn_weight_missing": ({"replace": [('"output_linefit_weight": 1.0', '"output_linefit_wt": 1.0')]}, None),
        })
    return m


def sibling_verdicts(tag, gate_text):
    out = {}
    for tg in SIBLINGS:
        if tg != tag and ('"%s" in tags' % tg) in gate_text and list((ROOT / "data").glob("out_%s/*.log" % tg)):
            v = gate("out_" + tg, tg)
            out[tg] = ("GATE_PASS" in v, v)
    return out


def selftest(tag, t, t2, sib_before):
    now = GATE.read_text(encoding="utf-8")
    res = {}
    missing = [k for k in sorted(need_keys(t)) if k not in need_keys(now)]
    if missing:
        res["pos_entries_missing"] = "NEED ENTRIES MISSING after the patch: %r" % missing
    for tg in NEG_REAL:
        res["neg_%s_as_%s" % (tg, tag)] = gate("out_" + tg, tag)
    for tg in REGRESS_REQUIRED:
        if not list((ROOT / "data").glob("out_%s/*.log" % tg)):
            res["pos_" + tg] = "MISSING LOG for a required regression"
            continue
        res["pos_" + tg] = gate("out_" + tg, tg)
    info = {}
    for tg, (ok0, v) in sibling_verdicts(tag, now).items():
        before = sib_before.get(tg)
        if before is not None and before[0] != ok0:
            res["neg_sibling_changed_" + tg] = "SIBLING VERDICT CHANGED: before %r after %r" % (before[1][:150], v[:150])
        info["sibling_" + tg] = v
    own = list((ROOT / "data").glob("out_%s/*.log" % tag))
    if own:
        info["own_visible_" + tag] = gate("out_" + tag, tag)  # reported, not part of the self-test verdict
    src_dir = ROOT / "data" / "out_ourvzlb25r70"
    src = log_text(next(src_dir.glob("*.log")))
    with open(src_dir / "run_stats.csv", newline="", encoding="utf-8") as fh:
        rs_rows = list(csv.DictReader(fh))
    with tempfile.TemporaryDirectory() as td:
        cases = [("pos_syn_" + tag, {}, None, True)] + [(k, mm, why, True) for k, (mm, why) in mutants(tag).items()]
        cases.append(("neg_syn_no_run_stats", {}, "no run_stats.csv beside the log", False))
        for name, mut, why, with_rs in cases:
            body, rs_csv = synth(tag, src, rs_rows, mut)
            d = pathlib.Path(td) / name
            d.mkdir()
            if with_rs:
                (d / "run_stats.csv").write_text(rs_csv, encoding="utf-8", newline="")
            p = d / (name + ".log")
            p.write_text(body, encoding="utf-8")
            res[name] = gate_file(p, tag)
            if why is not None and why not in res[name]:
                res[name] = "WRONG-REASON (wanted %r): %s" % (why, res[name])
    for k, v in list(res.items()) + list(info.items()):
        print(k, "->", v[:400])
    ok = all("GATE_FAIL" in v and not v.startswith("WRONG-REASON") for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_"))
    return ok, info


def install(tag):
    t = GATE.read_text(encoding="utf-8")
    sib_before = sibling_verdicts(tag, t)
    t2, pats, forbid = patch(t, tag)
    if GATE.read_text(encoding="utf-8") != t:
        raise SystemExit("gate.py changed while patching (another installer?); nothing written")
    bak = GATE.with_name("gate.py.bak_" + tag)
    bak.write_text(t, encoding="utf-8")
    GATE.write_text(t2, encoding="utf-8")
    try:
        ok, info = selftest(tag, t, t2, sib_before)
    except BaseException:
        if GATE.read_text(encoding="utf-8") == t2:
            GATE.write_text(t, encoding="utf-8")
            print("self-test aborted; gate.py restored from " + bak.name)
        raise
    if not ok:
        if GATE.read_text(encoding="utf-8") == t2:
            GATE.write_text(t, encoding="utf-8")
            raise SystemExit("self-test FAILED; gate.py restored from " + bak.name)
        raise SystemExit("self-test failed AND gate.py was modified by someone else meanwhile; NOT restored, check by hand")
    print("SELFTEST OK: gate entry for %s added (backup %s); need entries now %d; %d need patterns, %d forbids"
          % (tag, bak.name, len(need_keys(GATE.read_text(encoding="utf-8"))), len(pats), len(forbid)))
