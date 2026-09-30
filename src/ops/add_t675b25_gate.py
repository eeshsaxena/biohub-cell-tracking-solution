#!/usr/bin/env python3
r"""Gate entry for t675b25 (scratch_kernels/build_t675b25.py) = t65b25 (t65s3 body, relink TIGHT 6.5, learned bonus 2.5;
submitted 56639660) with the motion-relink TIGHT gate widened 6.5 -> 6.75; bonus kept at 2.5.
Run from the project root: it backs up ops/gate.py (gate.py.bak_t675b25), patches it, self-tests, and restores the
backup if any self-test fails. Install AFTER ops/add_t70b25_gate.py (never concurrently).
Dry run: T675B25_GATE=<copy of gate.py> python ops/add_t675b25_gate.py

Everything is DERIVED from the live t65b25 entry (read out of gate.py with ast), not retyped:
  * need['t65b25'] with its two tight receipts and its XENV line swapped: cell-0 'ARM_T675H tight_um=6.75' and the
    cell-2 CONFIG_DISPLAY echo '"motion_relink_tight_um": 6.75' (read out of the live global after float()), plus, as
    t70b20 added, the two cell-9 PP_BASE_CONFIG echoes (globals() read AFTER all four movies are tracked):
    MOTION_RELINK_TIGHT_UM 6.75 and MOTION_RELINK_LEARNED_BONUS 2.5; then 'ARM_XENV tag=t675b25 TIGHT=6.75 BONUS=2.50
    LCEFR=kept'. The 2.5 bonus receipts (cell-0 marker + cell-2 echo), STK3V, LCEFR runtime counters and line-fit
    echoes are unchanged;
  * forbid['t65b25'] with its XENV lookahead renamed and its ARM_ allowlist T65H -> T675H (so ARM_T65H is now a
    foreign marker); its 1.6 / 2.0 bonus and 6.0 tight prohibitions are kept; added: ARM_T65H / ARM_T70H / ARM_T60H,
    a 6.5 / 6.0 / 7.0 (or any non-6.75) tight marker or echo, any non-2.5 bonus marker or echo;
  * a cell-5 receipt like t70b20's: run_stats.csv motion_relink_tight_edges >= the 6.5-gate runs' counts (24616 /
    19921 / 5911 / 67052, read from the real t65b20 / t65b25 / t65s3 run_stats and required to agree) on all four
    movies and > on at least one. The tight pass is effectively a maximum-cardinality matching over the gate graph, so
    its size is monotone non-decreasing in the gate and independent of the bonus;
  * sv_mark (>= 4 SV_ARM_HSG200 lines before 'Prediction completed'), FINAL within 15% of REF.
Self-tests: the t65b25 log (the base arm) MUST FAIL as t675b25 (also on the cell-5 receipt), and so must t70b20 /
t65b20 / t65s3 / t6stk3 (and t70b25 when its visible log is present); a synthetic t65b25 log with only the XENV line
renamed FAILs; t65b20 / t65b25 / t70b20 / t65b25r70 / ourvzlb25 / t65s3 / t6stk3 / t6r70 / ourvzl (and t70b25, if its
entry and log exist and it passed before this install) still PASS as themselves; a synthetic t675b25 log (the t65b25
log with the four tight/tag lines rewritten, tight edges +1) PASSes, and the same log with tight edges equal to / one
movie below the 6.5-gate counts FAILs on the receipt.
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

ROOT = pathlib.Path(os.environ.get("T675B25_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T675B25_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t675b25"
SRC = "t65b25"
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
FLOOR_65 = {"44b6_0113de3b": 24616, "44b6_0b24845f": 19921, "6bba_05b6850b": 5911, "6bba_05db0fb1": 67052}
XENV = r"ARM_XENV tag=t675b25 TIGHT=6\.75 BONUS=2\.50 LCEFR=kept"
# need: t65b25 pattern -> t675b25 pattern (each must occur exactly once in need['t65b25'])
NEED_SWAP = {
    r"ARM_T65H tight_um=6\.5": r"ARM_T675H tight_um=6\.75",
    r'"motion_relink_tight_um": 6\.5(?!\d)': r'"motion_relink_tight_um": 6\.75(?!\d)',
    r"ARM_XENV tag=t65b25 TIGHT=6\.5 BONUS=2\.50 LCEFR=kept": XENV,
}
C9_TIGHT = r"MOTION_RELINK_TIGHT_UM +6\.75(?!\d)"
C9_BONUS = r"MOTION_RELINK_LEARNED_BONUS +2\.5(?!\d)"
NEED_KEEP = (r"ARM_STK3B learned_bonus=2\.5", r'"motion_relink_learned_bonus": 2\.5(?!\d)',
             r"ARM_STK3V velocity_weight=0\.25")
# forbid: t65b25 pattern -> t675b25 pattern (each must occur exactly once in forbid['t65b25'])
FORBID_SWAP = {
    r"ARM_XENV tag=(?!t65b25 )": r"ARM_XENV tag=(?!t675b25 )",
    r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV)\b)[A-Z0-9]+": r"\bARM_(?!(?:STK3V|STK3B|T675H|LCEFR|XENV)\b)[A-Z0-9]+",
}
FORBID_KEEP = (r"ARM_STK3B learned_bonus=2\.0", r"ARM_STK3B learned_bonus=1\.6", r'"motion_relink_learned_bonus": (2\.0|1\.6)',
               r'"motion_relink_tight_um": 6\.0(?!\d)', r"ARM_T60H tight_um=6\.0")
FORBID_ADD = [r"ARM_T65H", r"ARM_T70H", r"ARM_T60H",
              r'"motion_relink_tight_um": (6\.5|6\.0|7\.0)(?!\d)', r'"motion_relink_tight_um": (?!6\.75(?!\d))',
              r"MOTION_RELINK_TIGHT_UM +(?!6\.75(?!\d))\d", r"ARM_T\d+H tight_um=(?!6\.75(?!\d))",
              r"ARM_STK3B learned_bonus=(?!2\.5(?!\d))", r'"motion_relink_learned_bonus": (?!2\.5(?!\d))',
              r"MOTION_RELINK_LEARNED_BONUS +(?!2\.5(?!\d))\d"]
REGRESS = ("t65b20", "t65b25", "t70b20", "t65b25r70", "ourvzlb25", "t65s3", "t6stk3", "t6r70", "ourvzl")


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
    return per["t65b25"]


def log_text(path):
    raw = path.read_text(encoding="utf-8")
    try:
        return "".join(e.get("data", "") for e in json.loads(raw))
    except Exception:
        return raw


def synthetic(tmp, name, bump, full=True):
    """the real t65b25 log with its tight/tag lines rewritten to t675b25's (full=False: only the XENV line), beside
    its run_stats with motion_relink_tight_edges bumped per movie"""
    src = ROOT / "data" / "out_t65b25"
    txt = log_text(log_of("out_t65b25"))
    subs = [("ARM_XENV tag=t65b25 TIGHT=6.5 BONUS=2.50 LCEFR=kept", "ARM_XENV tag=t675b25 TIGHT=6.75 BONUS=2.50 LCEFR=kept")]
    if full:
        subs += [("ARM_T65H tight_um=6.5", "ARM_T675H tight_um=6.75"),
                 ('"motion_relink_tight_um": 6.5,', '"motion_relink_tight_um": 6.75,')]
    for a, b in subs:
        if txt.count(a) != 1:
            raise SystemExit("synthetic log: %r occurs %d times in the t65b25 log" % (a, txt.count(a)))
        txt = txt.replace(a, b)
    if full:
        txt, n = re.subn(r"MOTION_RELINK_TIGHT_UM( +)6\.5(?!\d)", r"MOTION_RELINK_TIGHT_UM\g<1>6.75", txt)
        if n != 1:
            raise SystemExit("synthetic log: cell-9 tight echo occurs %d times" % n)
    d = pathlib.Path(tmp) / name
    d.mkdir()
    (d / "synthetic.log").write_text(txt, encoding="utf-8")
    with open(src / "run_stats.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
        fields = list(rows[0].keys())
    for r in rows:
        if r.get("dataset") in bump:
            r["motion_relink_tight_edges"] = str(int(float(r["motion_relink_tight_edges"])) + bump[r["dataset"]])
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
    # ---- need: t65b25's with the tight receipts + XENV swapped, and the two cell-9 echoes inserted before XENV
    base = list(need_of(t, SRC))
    for p in list(NEED_SWAP) + list(NEED_KEEP):
        if base.count(p) != 1:
            raise SystemExit("need['t65b25'] does not carry exactly one %r: %r" % (p, base))
    if any("MOTION_RELINK_TIGHT_UM +" in p or "MOTION_RELINK_LEARNED_BONUS +" in p for p in base):
        raise SystemExit("need['t65b25'] unexpectedly already pins cell-9 echoes: %r" % base)
    pats = [NEED_SWAP.get(p, p) for p in base]
    pats = pats[:pats.index(XENV)] + [C9_TIGHT, C9_BONUS] + pats[pats.index(XENV):]
    for stale in (r"6\.5", r"6\.0", r"7\.0", r"2\.0", r"1\.6", "T65H", "T60H", "T70H", "t65b25"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived in need: %r" % (stale, pats))
    for p in list(NEED_SWAP.values()) + list(NEED_KEEP) + [C9_TIGHT, C9_BONUS]:
        if pats.count(p) != 1:
            raise SystemExit("pattern %r not present exactly once: %r" % (p, pats))
    new = [p for p in pats if p not in base]
    if len(pats) != len(base) + 2 or new != [NEED_SWAP[r"ARM_T65H tight_um=6\.5"],
                                             NEED_SWAP[r'"motion_relink_tight_um": 6\.5(?!\d)'], C9_TIGHT, C9_BONUS, XENV]:
        raise SystemExit("t675b25 need entry is not t65b25's with the 3 swaps + 2 cell-9 echoes: %r" % new)
    # ---- forbid: t65b25's with XENV / ARM_ allowlist renamed, plus the non-6.75 tight / non-2.5 bonus guards
    fb0 = list(forbid_of(t, SRC))
    for p in list(FORBID_SWAP) + list(FORBID_KEEP):
        if fb0.count(p) != 1:
            raise SystemExit("forbid['t65b25'] does not carry exactly one %r: %r" % (p, fb0))
    forbid = [FORBID_SWAP.get(p, p) for p in fb0] + FORBID_ADD
    for p in forbid:
        re.compile(p)
    if any("t65b25" in p or "T65H)" in p for p in forbid) or any("|T65H|" in p for p in forbid):
        raise SystemExit("a stale t65b25 forbid pattern survived: %r" % forbid)
    # ---- cell-5 receipt floor = the real 6.5-gate runs' tight edges (and the spec's)
    floor = tight_floor()
    if floor != FLOOR_65:
        raise SystemExit("the 6.5-gate runs' tight edges %r are not the expected %r" % (floor, FLOOR_65))
    comment = ("        # --- t675b25: t65b25 (relink tight 6.5, learned bonus 2.5; submitted 56639660) with the motion-relink\n"
               "        # TIGHT gate widened 6.5 -> 6.75 (bonus kept 2.5). Derived from need['t65b25'] (ops/add_t675b25_gate.py;\n"
               "        # build_t675b25.py): ARM_T675H + 6.75 cell-2/cell-9 echoes, 2.5 bonus receipts kept, plus the\n"
               "        # motion_relink_tight_edges check below; a 6.5 / 6.0 / 7.0 (any non-6.75) tight, ARM_T65H or a non-2.5\n"
               "        # bonus is forbidden (t65b25 / t70b20 / t70b25 / t65b20 / t65s3 / t6stk3 wearing this name).\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    xcheck = (
        "# --- t675b25 (ops/add_t675b25_gate.py): t65b25 with the relink TIGHT gate 6.5 -> 6.75. Cell-5 receipt, as for t70b20:\n"
        "# out-of-gate cells cost gate*1000+1, so the tight pass is effectively a maximum-cardinality matching over the\n"
        "# gate-restricted bipartite graph; its size depends on the gate and the node positions alone (never velocity or\n"
        "# bonus) and is monotone non-decreasing in the gate. The real 6.5-gate runs (t65s3, t65b20, t65b25) all logged\n"
        "# exactly the counts below; a 6.75 run can never fall below them and must exceed them on at least one movie.\n"
        "if \"t675b25\" in tags:\n"
        "    import csv, os\n"
        "    _T675_FLOOR = @FLOOR@\n"
        "    _trsp = os.path.join(os.path.dirname(os.path.abspath(log)), \"run_stats.csv\")\n"
        "    if not os.path.isfile(_trsp):\n"
        "        fails.append(\"t675b25: no run_stats.csv beside the log, so motion_relink_tight_edges is unproven and \"\n"
        "                     \"the 6.75 gate has no evidence it reached cell 5\")\n"
        "    else:\n"
        "        with open(_trsp, newline=\"\", encoding=\"utf-8\") as fh:\n"
        "            _trs = {r.get(\"dataset\"): r for r in csv.DictReader(fh)}\n"
        "        _tgot = {}\n"
        "        for d in sorted(_T675_FLOOR):\n"
        "            try: _tgot[d] = int(float((_trs.get(d) or {})[\"motion_relink_tight_edges\"]))\n"
        "            except (KeyError, TypeError, ValueError): _tgot[d] = None\n"
        "        _tmiss = sorted(d for d, v in _tgot.items() if v is None)\n"
        "        _tlow = {d: (v, _T675_FLOOR[d]) for d, v in sorted(_tgot.items()) if v is not None and v < _T675_FLOOR[d]}\n"
        "        if _tmiss:\n"
        "            fails.append(f\"t675b25 run_stats has no readable motion_relink_tight_edges for {_tmiss}\")\n"
        "        elif _tlow:\n"
        "            fails.append(f\"t675b25 motion_relink_tight_edges fell BELOW the 6.5-gate runs' on {_tlow} (got, floor): \"\n"
        "                         \"widening the gate can only admit more tight edges, so this is not a 6.75 run on this body\")\n"
        "        elif not any(_tgot[d] > _T675_FLOOR[d] for d in _tgot):\n"
        "            fails.append(f\"t675b25 motion_relink_tight_edges {_tgot} equal the 6.5-gate runs' on all four movies: \"\n"
        "                         \"the 6.75 gate never reached motion_relink_edges\")\n").replace("@FLOOR@", repr(floor))
    if xcheck.count(repr(floor)) != 1 or "@" in xcheck:
        raise SystemExit("the tight floor was not substituted exactly once into the receipt block")
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": '"ourvzl": 0.15',
               "xcheck": 'sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    # sv_mark: t65b25 is in sv_mark (its cell 4 is hsg200's byte for byte); t675b25's cell 4 is t65b25's byte for byte
    if '"t65b25": "SV_ARM_HSG200"' not in t:
        raise SystemExit("t65b25 is not in sv_mark; refusing to guess the body marker")
    # t70b25 joins the regressions only if its entry + visible log exist and it PASSes before this install
    regress = list(REGRESS)
    t70b25_log = log_of("out_t70b25")
    if t70b25_log is not None and "'t70b25': [" in t and "GATE_PASS" in gate_path(t70b25_log, "t70b25"):
        regress.append("t70b25")
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
    res = {"neg_t65b25_as_t675b25": gate("out_t65b25", TAG),
           "neg_t70b20_as_t675b25": gate("out_t70b20", TAG),
           "neg_t65b20_as_t675b25": gate("out_t65b20", TAG),
           "neg_t65s3_as_t675b25": gate("out_t65s3", TAG),
           "neg_t6stk3_as_t675b25": gate("out_t6stk3", TAG)}
    if t70b25_log is not None:
        res["neg_t70b25_as_t675b25"] = gate_path(t70b25_log, TAG)
    for arm in regress:
        if log_of("out_" + arm) is not None:
            res["pos_" + arm] = gate("out_" + arm, arm)
    with tempfile.TemporaryDirectory() as tmp:
        res["syn_pos_t675b25"] = gate_path(synthetic(tmp, "bump", {d: 1 for d in MOVIES}), TAG)
        res["syn_neg_xenv_only"] = gate_path(synthetic(tmp, "xenv", {d: 1 for d in MOVIES}, full=False), TAG)
        res["syn_neg_equal_tight"] = gate_path(synthetic(tmp, "equal", {}), TAG)
        res["syn_neg_low_tight"] = gate_path(synthetic(tmp, "low", {MOVIES[0]: 5, MOVIES[1]: -1}), TAG)
    if log_of("out_" + TAG) is not None:
        res["run_" + TAG] = gate("out_" + TAG, TAG)
    for k, v in res.items():
        print(k, "->", v[:500])
    ok = all("GATE_FAIL" in v for k, v in res.items() if k.startswith("neg_") or k.startswith("syn_neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_")) \
        and len([k for k in res if k.startswith("pos_")]) == len(regress) \
        and "motion_relink_tight_edges" in res["neg_t65b25_as_t675b25"] \
        and "ARM_T65H" in res["syn_neg_xenv_only"] \
        and "GATE_PASS" in res["syn_pos_t675b25"] \
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
    print("gate entry for %s added (backup %s); tight floor %r; regressions %s" % (TAG, bak.name, floor, regress))


if __name__ == "__main__":
    main()
