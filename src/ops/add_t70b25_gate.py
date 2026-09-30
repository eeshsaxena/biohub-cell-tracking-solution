#!/usr/bin/env python3
r"""Gate entry for t70b25 (scratch_kernels/build_t70b25.py) = t70b20 (t65b20 with the motion-relink TIGHT gate widened
6.5 -> 7.0, submitted 56641323) with the learned-edge bonus raised 2.0 -> 2.5 (the step that took t65b20 to t65b25).
Run from the project root: it backs up ops/gate.py (gate.py.bak_t70b25), patches it, self-tests, and restores the
backup if any self-test fails.
Dry run: T70B25_GATE=<copy of gate.py> python ops/add_t70b25_gate.py

Everything is DERIVED from the live t70b20 entry (read out of gate.py with ast), not retyped:
  * need['t70b20'] with its three bonus receipts and its XENV line swapped: cell-0 'ARM_STK3B learned_bonus=2.5',
    the cell-2 CONFIG_DISPLAY echo '"motion_relink_learned_bonus": 2.5' (read out of the live global after float()),
    the cell-9 PP_BASE_CONFIG echo 'MOTION_RELINK_LEARNED_BONUS 2.5' (globals() read AFTER all four movies are
    tracked), and 'ARM_XENV tag=t70b25 TIGHT=7.0 BONUS=2.50 LCEFR=kept'; the three 7.0 tight receipts
    (ARM_T70H tight_um=7.0, the cell-2 and cell-9 echoes), STK3V, LCEFR runtime counters and line-fit echoes unchanged;
  * forbid['t70b20'] with its bonus prohibitions flipped (a 1.6 / 2.0, or any non-2.5, bonus marker or echo is now
    forbidden) and its XENV lookahead renamed; the non-7.0 tight prohibitions (ARM_T65H / ARM_T60H, a 6.5 / 6.0 or
    any non-7.0 tight echo) are kept, plus a generic 'ARM_T<n>H tight_um=<not 7.0>' and 'ARM_STK3B learned_bonus=
    <not 2.5>';
  * t70b20's cell-5 receipt, kept against the SAME 6.5-gate counts (the floor literal is read out of the t70b20 block
    and must equal the counts the real t65b20 / t65b25 / t65s3 runs logged): run_stats.csv motion_relink_tight_edges
    >= those counts on all four movies and > on at least one. The tight pass is effectively a maximum-cardinality
    matching over the gate graph, so its size is independent of the bonus (t65s3 / t65b20 / t65b25 = bonus 1.6 / 2.0
    / 2.5 all logged the same counts) and a 7.0 run always exceeds the 6.5 counts;
  * sv_mark (>= 4 SV_ARM_HSG200 lines before 'Prediction completed'), FINAL within 15% of REF.
Self-tests: the t70b20 log (the base arm) MUST FAIL as t70b25, and so must t65b25 (tight 6.5 wearing the name; also on
the cell-5 receipt), t65b20 and t6stk3; a synthetic t70b20 log with only the XENV line renamed (bonus still 2.0) FAILs;
t65b20 / t65b25 / t70b20 / t65b25r70 / ourvzlb25 / t65s3 / t6stk3 / t6r70 / ourvzl logs (where present) still PASS
as themselves; a synthetic t70b25 log (the t70b20 log with the four bonus/tag lines rewritten, t70b20's own run_stats)
PASSes, and the same log with tight edges equal to / below the 6.5-gate counts FAILs on the receipt.
"""
import ast
import csv
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("T70B25_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T70B25_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t70b25"
SRC = "t70b20"
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
FLOOR_65 = {"44b6_0113de3b": 24616, "44b6_0b24845f": 19921, "6bba_05b6850b": 5911, "6bba_05db0fb1": 67052}
# need: t70b20 pattern -> t70b25 pattern (each must occur exactly once in need['t70b20'])
NEED_SWAP = {
    r"ARM_STK3B learned_bonus=2\.0": r"ARM_STK3B learned_bonus=2\.5",
    r'"motion_relink_learned_bonus": 2\.0(?!\d)': r'"motion_relink_learned_bonus": 2\.5(?!\d)',
    r"MOTION_RELINK_LEARNED_BONUS +2\.0(?!\d)": r"MOTION_RELINK_LEARNED_BONUS +2\.5(?!\d)",
    r"ARM_XENV tag=t70b20 TIGHT=7\.0 BONUS=2\.00 LCEFR=kept": r"ARM_XENV tag=t70b25 TIGHT=7\.0 BONUS=2\.50 LCEFR=kept",
}
NEED_KEEP = (r"ARM_T70H tight_um=7\.0", r'"motion_relink_tight_um": 7\.0(?!\d)', r"MOTION_RELINK_TIGHT_UM +7\.0(?!\d)",
             r"ARM_STK3V velocity_weight=0\.25")
# forbid: t70b20 pattern -> t70b25 pattern (each must occur exactly once in forbid['t70b20'])
FORBID_SWAP = {
    r"ARM_STK3B learned_bonus=(1\.6|2\.5)": r"ARM_STK3B learned_bonus=(1\.6|2\.0)",
    r'"motion_relink_learned_bonus": (1\.6|2\.5)': r'"motion_relink_learned_bonus": (1\.6|2\.0)',
    r'"motion_relink_learned_bonus": (?!2\.0(?!\d))': r'"motion_relink_learned_bonus": (?!2\.5(?!\d))',
    r"MOTION_RELINK_LEARNED_BONUS +(?!2\.0(?!\d))\d": r"MOTION_RELINK_LEARNED_BONUS +(?!2\.5(?!\d))\d",
    r"ARM_XENV tag=(?!t70b20 )": r"ARM_XENV tag=(?!t70b25 )",
}
FORBID_KEEP = (r"ARM_T65H", r"ARM_T60H", r'"motion_relink_tight_um": (6\.5|6\.0)(?!\d)',
               r'"motion_relink_tight_um": (?!7\.0(?!\d))', r"MOTION_RELINK_TIGHT_UM +(?!7\.0(?!\d))\d",
               r"\bARM_(?!(?:STK3V|STK3B|T70H|LCEFR|XENV)\b)[A-Z0-9]+")
FORBID_ADD = [r"ARM_T\d+H tight_um=(?!7\.0(?!\d))", r"ARM_STK3B learned_bonus=(?!2\.5(?!\d))"]
REGRESS = ("t65b20", "t65b25", "t70b20", "t65b25r70", "ourvzlb25", "t65s3", "t6stk3", "t6r70", "ourvzl")
T70_BLOCK_HEAD = "# --- t70b20 (ops/add_t70b20_gate.py)"


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def forbid_of(src, key):
    hits = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript):
            tg = node.targets[0]
            if getattr(tg.value, "id", None) == "forbid" and isinstance(tg.slice, ast.Constant) and tg.slice.value == key:
                hits.append(ast.literal_eval(node.value))
    if len(hits) != 1:
        raise SystemExit("forbid[%r] is assigned %d times in gate.py (expected exactly 1 literal)" % (key, len(hits)))
    return hits[0]


def gate_path(lg, tag):
    out = subprocess.run([sys.executable, str(GATE), str(lg), tag], capture_output=True, text=True).stdout.strip()
    return out.splitlines()[-1] if out else "NO OUTPUT"


def log_of(logdir):
    return next((ROOT / "data" / logdir).glob("*.log"), None)


def gate(logdir, tag):
    return gate_path(log_of(logdir), tag)


def tight_floor():
    """motion_relink_tight_edges of the real 6.5-gate runs; all three must agree movie by movie."""
    per = {}
    for arm in ("t65b20", "t65b25", "t65s3"):
        with open(ROOT / "data" / ("out_" + arm) / "run_stats.csv", newline="", encoding="utf-8") as fh:
            rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
        per[arm] = {d: int(float(rs[d]["motion_relink_tight_edges"])) for d in MOVIES}
    if len({tuple(sorted(v.items())) for v in per.values()}) != 1:
        raise SystemExit("the 6.5-gate runs disagree on motion_relink_tight_edges: %r" % per)
    return per["t65b20"]


def log_text(path):
    raw = path.read_text(encoding="utf-8")
    try:
        return "".join(e.get("data", "") for e in json.loads(raw))
    except Exception:
        return raw


def synthetic(tmp, name, full=True, tight=None):
    """the real t70b20 log with its bonus/tag lines rewritten to t70b25's (full=False: only the XENV line), beside
    t70b20's own run_stats.csv (tight: per-movie overrides of motion_relink_tight_edges)"""
    src = ROOT / "data" / "out_t70b20"
    txt = log_text(log_of("out_t70b20"))
    subs = [("ARM_XENV tag=t70b20 TIGHT=7.0 BONUS=2.00 LCEFR=kept", "ARM_XENV tag=t70b25 TIGHT=7.0 BONUS=2.50 LCEFR=kept")]
    if full:
        subs += [("ARM_STK3B learned_bonus=2.0", "ARM_STK3B learned_bonus=2.5"),
                 ('"motion_relink_learned_bonus": 2.0,', '"motion_relink_learned_bonus": 2.5,')]
    for a, b in subs:
        if txt.count(a) != 1:
            raise SystemExit("synthetic log: %r occurs %d times in the t70b20 log" % (a, txt.count(a)))
        txt = txt.replace(a, b)
    if full:
        txt, n = re.subn(r"MOTION_RELINK_LEARNED_BONUS( +)2\.0(?!\d)", r"MOTION_RELINK_LEARNED_BONUS\g<1>2.5", txt)
        if n != 1:
            raise SystemExit("synthetic log: cell-9 bonus echo occurs %d times" % n)
    d = pathlib.Path(tmp) / name
    d.mkdir()
    (d / "synthetic.log").write_text(txt, encoding="utf-8")
    with open(src / "run_stats.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
        fields = list(rows[0].keys())
    for r in rows:
        if tight and r.get("dataset") in tight:
            r["motion_relink_tight_edges"] = str(tight[r["dataset"]])
    with open(d / "run_stats.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return d / "synthetic.log"


def main():
    t = GATE.read_text(encoding="utf-8")
    t0 = t
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    # ---- need: t70b20's with the bonus receipts + XENV swapped
    base = list(need_of(t, SRC))
    for p in list(NEED_SWAP) + list(NEED_KEEP):
        if base.count(p) != 1:
            raise SystemExit("need['t70b20'] does not carry exactly one %r: %r" % (p, base))
    pats = [NEED_SWAP.get(p, p) for p in base]
    changed = [(a, b) for a, b in zip(base, pats) if a != b]
    if len(pats) != len(base) or changed != [(a, NEED_SWAP[a]) for a in base if a in NEED_SWAP] or len(changed) != 4:
        raise SystemExit("t70b25 need entry is not t70b20's with exactly the 4 swaps: %r" % changed)
    for stale in (r"2\.0", r"1\.6", r"6\.5", r"6\.0", "T65H", "T60H", "t70b20"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived in need: %r" % (stale, pats))
    for p in list(NEED_SWAP.values()) + list(NEED_KEEP):
        if pats.count(p) != 1:
            raise SystemExit("pattern %r not present exactly once: %r" % (p, pats))
    # ---- forbid: t70b20's with the bonus prohibitions flipped + XENV renamed, plus two generic non-value guards
    fb0 = list(forbid_of(t, SRC))
    for p in list(FORBID_SWAP) + list(FORBID_KEEP):
        if fb0.count(p) != 1:
            raise SystemExit("forbid['t70b20'] does not carry exactly one %r: %r" % (p, fb0))
    forbid = [FORBID_SWAP.get(p, p) for p in fb0] + FORBID_ADD
    for p in forbid:
        re.compile(p)
    for stale in ("t70b20", r"(1\.6|2\.5)", r"(?!2\.0(?!\d))"):
        if any(stale in p for p in forbid):
            raise SystemExit("a stale forbid pattern %r survived: %r" % (stale, forbid))
    # ---- cell-5 receipt: the t70b20 block's floor must be the real 6.5-gate counts (and the spec's)
    floor = tight_floor()
    if floor != FLOOR_65:
        raise SystemExit("the 6.5-gate runs' tight edges %r are not the expected %r" % (floor, FLOOR_65))
    i0 = t.find(T70_BLOCK_HEAD)
    i1 = t.find('sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n')
    if t.count(T70_BLOCK_HEAD) != 1 or not 0 <= i0 < i1:
        raise SystemExit("could not locate the t70b20 receipt block right before sv_tags")
    m = re.search(r"_T70_FLOOR = (\{[^}]*\})", t[i0:i1])
    if not m or ast.literal_eval(m.group(1)) != floor:
        raise SystemExit("the t70b20 receipt block's floor %r != the 6.5-gate counts %r" % (m and m.group(1), floor))
    comment = ("        # --- t70b25: t70b20 (relink tight 7.0, bonus 2.0; submitted 56641323) with the learned-edge bonus\n"
               "        # 2.0 -> 2.5 (the t65b20 -> t65b25 step). Derived from need['t70b20'] (ops/add_t70b25_gate.py;\n"
               "        # build_t70b25.py): 2.5 bonus marker + cell-2/cell-9 echoes, 7.0 tight receipts kept, plus the\n"
               "        # motion_relink_tight_edges check below; a 1.6 / 2.0 (any non-2.5) bonus or any non-7.0 tight is\n"
               "        # forbidden (t70b20 / t65b25 / t65b20 / t6stk3 wearing this name).\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    xcheck = (
        "# --- t70b25 (ops/add_t70b25_gate.py): t70b20 with the learned bonus 2.0 -> 2.5, tight gate still 7.0. Same cell-5\n"
        "# receipt as t70b20, against the same 6.5-gate counts: the tight pass is effectively a maximum-cardinality matching\n"
        "# over the gate graph, so its size never depends on the bonus (t65s3 / t65b20 / t65b25 = bonus 1.6 / 2.0 / 2.5 all\n"
        "# logged exactly these counts) and a 7.0 run can never fall below them and must exceed them on at least one movie.\n"
        "if \"t70b25\" in tags:\n"
        "    import csv, os\n"
        "    _T70B25_FLOOR = @FLOOR@\n"
        "    _trsp = os.path.join(os.path.dirname(os.path.abspath(log)), \"run_stats.csv\")\n"
        "    if not os.path.isfile(_trsp):\n"
        "        fails.append(\"t70b25: no run_stats.csv beside the log, so motion_relink_tight_edges is unproven and \"\n"
        "                     \"the 7.0 gate has no evidence it reached cell 5\")\n"
        "    else:\n"
        "        with open(_trsp, newline=\"\", encoding=\"utf-8\") as fh:\n"
        "            _trs = {r.get(\"dataset\"): r for r in csv.DictReader(fh)}\n"
        "        _tgot = {}\n"
        "        for d in sorted(_T70B25_FLOOR):\n"
        "            try: _tgot[d] = int(float((_trs.get(d) or {})[\"motion_relink_tight_edges\"]))\n"
        "            except (KeyError, TypeError, ValueError): _tgot[d] = None\n"
        "        _tmiss = sorted(d for d, v in _tgot.items() if v is None)\n"
        "        _tlow = {d: (v, _T70B25_FLOOR[d]) for d, v in sorted(_tgot.items()) if v is not None and v < _T70B25_FLOOR[d]}\n"
        "        if _tmiss:\n"
        "            fails.append(f\"t70b25 run_stats has no readable motion_relink_tight_edges for {_tmiss}\")\n"
        "        elif _tlow:\n"
        "            fails.append(f\"t70b25 motion_relink_tight_edges fell BELOW the 6.5-gate runs' on {_tlow} (got, floor): \"\n"
        "                         \"widening the gate can only admit more tight edges, so this is not a 7.0 run on this body\")\n"
        "        elif not any(_tgot[d] > _T70B25_FLOOR[d] for d in _tgot):\n"
        "            fails.append(f\"t70b25 motion_relink_tight_edges {_tgot} equal the 6.5-gate runs' on all four movies: \"\n"
        "                         \"the 7.0 gate never reached motion_relink_edges\")\n").replace("@FLOOR@", repr(floor))
    if xcheck.count(repr(floor)) != 1 or "@" in xcheck:
        raise SystemExit("the tight floor was not substituted exactly once into the receipt block")
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": '"ourvzl": 0.15',
               "xcheck": 'sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    # sv_mark: t70b20 is in sv_mark (its cell 4 is hsg200's byte for byte); t70b25's cell 4 is t70b20's byte for byte
    if '"t70b20": "SV_ARM_HSG200"' not in t:
        raise SystemExit("t70b20 is not in sv_mark; refusing to guess the body marker")
    t = t.replace(anchors["need"], entry + anchors["need"], 1)
    t = t.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t = t.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t = t.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % TAG, 1)
    t = t.replace(anchors["xcheck"], xcheck + anchors["xcheck"], 1)
    ast.parse(t)
    compile(t, str(GATE), "exec")
    if need_of(t, TAG) != pats or forbid_of(t, TAG) != forbid:
        raise SystemExit("the written need/forbid entries do not read back as the computed patterns")
    before = GATE.read_text(encoding="utf-8")
    if before != t0:
        raise SystemExit("gate.py changed while the entry was being prepared (another installer?); nothing written, re-run")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(before, encoding="utf-8")
    GATE.write_text(t, encoding="utf-8")
    res = {"neg_t70b20_as_t70b25": gate("out_t70b20", TAG),
           "neg_t65b25_as_t70b25": gate("out_t65b25", TAG),
           "neg_t65b20_as_t70b25": gate("out_t65b20", TAG),
           "neg_t6stk3_as_t70b25": gate("out_t6stk3", TAG)}
    for arm in REGRESS:
        if log_of("out_" + arm) is not None:
            res["pos_" + arm] = gate("out_" + arm, arm)
    with tempfile.TemporaryDirectory() as tmp:
        res["syn_pos_t70b25"] = gate_path(synthetic(tmp, "full"), TAG)
        res["syn_neg_xenv_only"] = gate_path(synthetic(tmp, "xenv", full=False), TAG)
        res["syn_neg_equal_tight"] = gate_path(synthetic(tmp, "equal", tight=dict(floor)), TAG)
        low = dict(floor)
        low[MOVIES[0]] += 5
        low[MOVIES[1]] -= 1
        res["syn_neg_low_tight"] = gate_path(synthetic(tmp, "low", tight=low), TAG)
    if log_of("out_" + TAG) is not None:
        res["run_" + TAG] = gate("out_" + TAG, TAG)
    for k, v in res.items():
        print(k, "->", v[:500])
    ok = all("GATE_FAIL" in v for k, v in res.items() if k.startswith("neg_") or k.startswith("syn_neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_")) \
        and len([k for k in res if k.startswith("pos_")]) == len(REGRESS) \
        and "learned_bonus" in res["neg_t70b20_as_t70b25"] \
        and "motion_relink_tight_edges" in res["neg_t65b25_as_t70b25"] \
        and "learned_bonus" in res["syn_neg_xenv_only"] \
        and "GATE_PASS" in res["syn_pos_t70b25"] \
        and "equal the 6.5-gate runs'" in res["syn_neg_equal_tight"] \
        and "fell BELOW the 6.5-gate runs'" in res["syn_neg_low_tight"]
    now = GATE.read_text(encoding="utf-8")
    if not ok:
        if now != t:
            raise SystemExit("self-test failed AND gate.py was modified by someone else during the self-test: NOT "
                             "restoring blindly; merge by hand against " + bak.name)
        GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit("self-test failed; gate.py restored from " + bak.name)
    if now != t:
        print("NOTE: gate.py was modified by another writer during the self-test; entry present:",
              "'%s': [" % TAG in now)
    print("gate entry for %s added (backup %s); tight floor %r" % (TAG, bak.name, floor))


if __name__ == "__main__":
    main()
