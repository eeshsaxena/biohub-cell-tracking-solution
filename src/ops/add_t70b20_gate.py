#!/usr/bin/env python3
r"""Gate entry for t70b20 (scratch_kernels/build_t70b20.py) = t65b20 (board 0.954: the t65s3 body with relink TIGHT 6.5
and learned bonus 2.0, submitted 56628029) with the motion-relink TIGHT gate widened 6.5 -> 7.0; bonus kept at 2.0.
Run from the project root: it backs up ops/gate.py (gate.py.bak_t70b20), patches it, self-tests, and restores the
backup if any self-test fails.
Dry run: T70B20_GATE=<copy of gate.py> python ops/add_t70b20_gate.py

t70b20 must prove on the visible run (4 movies):
  * need['t65b20'] (read out of gate.py with ast) with its two tight markers rewritten to 7.0 and its XENV line
    swapped: cell-0 'ARM_T70H tight_um=7.0' AND the cell-2 CONFIG_DISPLAY echo '"motion_relink_tight_um": 7.0' (read
    out of the live global after float()); the bonus markers stay at 2.0 (cell-0 'ARM_STK3B learned_bonus=2.0' + the
    cell-2 echo); STK3V / LCEFR runtime counters / line-fit echoes unchanged;
  * the two cell-9 PP_BASE_CONFIG echoes (globals() read AFTER all four movies are tracked, printed as
    `KEY<padded> VALUE`): MOTION_RELINK_TIGHT_UM 7.0 and MOTION_RELINK_LEARNED_BONUS 2.0;
  * the cell-0 identity line ARM_XENV tag=t70b20 TIGHT=7.0 BONUS=2.00 LCEFR=kept;
  * a cell-5 receipt, as t65s3 has: run_stats.csv motion_relink_tight_edges >= the 6.5-gate runs' counts on all four
    movies and > on at least one. The tight pass is effectively a maximum-cardinality matching over the gate graph
    (out-of-gate cells cost gate*1000+1), so its size is monotone in the gate and independent of velocity / bonus: the
    real t65s3, t65b20 and t65b25 runs all logged the same counts, read here from their run_stats.csv;
  * sv_mark (>= 4 SV_ARM_HSG200 lines before 'Prediction completed': the 0.951 sub-voxel body);
  * FINAL within 15% of REF (node-neutral arm: +0.018% expected);
  * forbidden: a 6.5 / 6.0 (or any non-7.0) tight echo, ARM_T65H / ARM_T60H, a 1.6 / 2.5 (or any non-2.0) bonus marker or
    echo, a foreign ARM_XENV tag, foreign ARM_ / SV_ARM_ markers, tracebacks / IndentationError.
Self-tests: the t65b20, t65s3, t65b25 and t6stk3 logs must FAIL as t70b20 (t65b20 also on the cell-5 receipt);
t65b20 / t65b25 / t65s3 / t6stk3 / t6r70 / ourvzl logs still PASS as themselves; a synthetic t70b20 log (the t65b20
log with the four tight/tag lines rewritten, tight edges +1) PASSes, and the same log with the 6.5-run tight edges
or one movie below them FAILs on the receipt.
"""
import ast
import csv
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("T70B20_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T70B20_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t70b20"
SRC = "t65b20"
OLD_TMARK = r"ARM_T65H tight_um=6\.5"
OLD_TECHO = r'"motion_relink_tight_um": 6\.5(?!\d)'
OLD_XENV = r"ARM_XENV tag=t65b20 TIGHT=6\.5 BONUS=2\.00 LCEFR=kept"
NEW_TMARK = r"ARM_T70H tight_um=7\.0"
NEW_TECHO = r'"motion_relink_tight_um": 7\.0(?!\d)'
XENV = r"ARM_XENV tag=t70b20 TIGHT=7\.0 BONUS=2\.00 LCEFR=kept"
BONUS_MARK = r"ARM_STK3B learned_bonus=2\.0"
BONUS_ECHO = r'"motion_relink_learned_bonus": 2\.0(?!\d)'
C9_TIGHT = r"MOTION_RELINK_TIGHT_UM +7\.0(?!\d)"
C9_BONUS = r"MOTION_RELINK_LEARNED_BONUS +2\.0(?!\d)"
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def gate_path(lg, tag):
    out = subprocess.run([sys.executable, str(GATE), str(lg), tag], capture_output=True, text=True).stdout.strip()
    return out.splitlines()[-1] if out else "NO OUTPUT"


def gate(logdir, tag):
    return gate_path(next((ROOT / "data" / logdir).glob("*.log")), tag)


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
    import json
    raw = path.read_text(encoding="utf-8")
    try:
        return "".join(e.get("data", "") for e in json.loads(raw))
    except Exception:
        return raw


def synthetic(tmp, name, bump):
    """the real t65b20 log with its tight/tag lines rewritten to t70b20's, plus its run_stats with tight edges bumped"""
    src = ROOT / "data" / "out_t65b20"
    txt = log_text(next(src.glob("*.log")))
    subs = [("ARM_T65H tight_um=6.5", "ARM_T70H tight_um=7.0"),
            ('"motion_relink_tight_um": 6.5,', '"motion_relink_tight_um": 7.0,'),
            ("ARM_XENV tag=t65b20 TIGHT=6.5 BONUS=2.00 LCEFR=kept", "ARM_XENV tag=t70b20 TIGHT=7.0 BONUS=2.00 LCEFR=kept")]
    for a, b in subs:
        if txt.count(a) != 1:
            raise SystemExit("synthetic log: %r occurs %d times in the t65b20 log" % (a, txt.count(a)))
        txt = txt.replace(a, b)
    txt, n = re.subn(r"MOTION_RELINK_TIGHT_UM( +)6\.5(?!\d)", r"MOTION_RELINK_TIGHT_UM\g<1>7.0", txt)
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
    base = list(need_of(t, SRC))
    for p in (OLD_TMARK, OLD_TECHO, OLD_XENV, BONUS_MARK, BONUS_ECHO):
        if base.count(p) != 1:
            raise SystemExit("need['t65b20'] does not carry exactly one %r: %r" % (p, base))
    swap = {OLD_TMARK: NEW_TMARK, OLD_TECHO: NEW_TECHO, OLD_XENV: XENV}
    pats = [swap.get(p, p) for p in base]
    pats = pats[:pats.index(XENV)] + [C9_TIGHT, C9_BONUS] + pats[pats.index(XENV):]
    for stale in (r"6\.5", r"6\.0", r"1\.6", r"2\.5", "T65H", "T60H", "t65b20"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    for p in (NEW_TMARK, NEW_TECHO, XENV, BONUS_MARK, BONUS_ECHO, C9_TIGHT, C9_BONUS):
        if pats.count(p) != 1:
            raise SystemExit("pattern %r not present exactly once: %r" % (p, pats))
    if len(pats) != len(base) + 2 or [p for p in pats if p not in base] != [NEW_TMARK, NEW_TECHO, C9_TIGHT, C9_BONUS, XENV]:
        raise SystemExit("t70b20 need entry is not t65b20's with the 3 swaps + 2 cell-9 echoes: %r" % pats)
    floor = tight_floor()
    comment = ("        # --- t70b20: t65b20 (0.954; t65s3 body, relink tight 6.5, learned bonus 2.0) with the motion-relink\n"
               "        # TIGHT gate widened 6.5 -> 7.0 (bonus kept 2.0). Node- and fork-neutral: exact replay +0.018% nodes,\n"
               "        # 0 forks (build_t70b20.py; ops/add_t70b20_gate.py). The 7.0 cell-2 and cell-9 echoes are the receipts,\n"
               "        # plus the motion_relink_tight_edges check below; a 6.5 / 6.0 tight echo, ARM_T65H or a non-2.0 bonus\n"
               "        # is forbidden (t65b20 / t65b25 / t65s3 / t6stk3 wearing this name).\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    forbid = [r"ARM_T65H", r"ARM_T60H",
              r'"motion_relink_tight_um": (6\.5|6\.0)(?!\d)', r'"motion_relink_tight_um": (?!7\.0(?!\d))',
              r"MOTION_RELINK_TIGHT_UM +(?!7\.0(?!\d))\d",
              r"ARM_STK3B learned_bonus=(1\.6|2\.5)", r'"motion_relink_learned_bonus": (1\.6|2\.5)',
              r'"motion_relink_learned_bonus": (?!2\.0(?!\d))', r"MOTION_RELINK_LEARNED_BONUS +(?!2\.0(?!\d))\d",
              r"ARM_XENV tag=(?!t70b20 )",
              r"Traceback \(most recent call last\)", "IndentationError",
              r"\bARM_(?!(?:STK3V|STK3B|T70H|LCEFR|XENV)\b)[A-Z0-9]+", "ARM_RAWLINK", "ARM_FLOWFIX",
              r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", "GDIV_DS", "SUBVOXEL_ACTIVE",
              r'"output_linefit_strict_linear": true']
    xcheck = (
        "# --- t70b20 (ops/add_t70b20_gate.py): t65b20 with the relink TIGHT gate 6.5 -> 7.0. Cell-5 receipt, as for t65s3:\n"
        "# out-of-gate cells cost gate*1000+1, so the tight pass is effectively a maximum-cardinality matching over the\n"
        "# gate-restricted bipartite graph; its size depends on the gate and the node positions alone (never velocity or\n"
        "# bonus) and is monotone non-decreasing in the gate. The real 6.5-gate runs (t65s3, t65b20, t65b25) all logged\n"
        "# exactly the counts below; a 7.0 run can never fall below them and must exceed them on at least one movie.\n"
        "if \"t70b20\" in tags:\n"
        "    import csv, os\n"
        "    _T70_FLOOR = @FLOOR@\n"
        "    _trsp = os.path.join(os.path.dirname(os.path.abspath(log)), \"run_stats.csv\")\n"
        "    if not os.path.isfile(_trsp):\n"
        "        fails.append(\"t70b20: no run_stats.csv beside the log, so motion_relink_tight_edges is unproven and \"\n"
        "                     \"the 7.0 gate has no evidence it reached cell 5\")\n"
        "    else:\n"
        "        with open(_trsp, newline=\"\", encoding=\"utf-8\") as fh:\n"
        "            _trs = {r.get(\"dataset\"): r for r in csv.DictReader(fh)}\n"
        "        _tgot = {}\n"
        "        for d in sorted(_T70_FLOOR):\n"
        "            try: _tgot[d] = int(float((_trs.get(d) or {})[\"motion_relink_tight_edges\"]))\n"
        "            except (KeyError, TypeError, ValueError): _tgot[d] = None\n"
        "        _tmiss = sorted(d for d, v in _tgot.items() if v is None)\n"
        "        _tlow = {d: (v, _T70_FLOOR[d]) for d, v in sorted(_tgot.items()) if v is not None and v < _T70_FLOOR[d]}\n"
        "        if _tmiss:\n"
        "            fails.append(f\"t70b20 run_stats has no readable motion_relink_tight_edges for {_tmiss}\")\n"
        "        elif _tlow:\n"
        "            fails.append(f\"t70b20 motion_relink_tight_edges fell BELOW the 6.5-gate runs' on {_tlow} (got, floor): \"\n"
        "                         \"widening the gate can only admit more tight edges, so this is not a 7.0 run on this body\")\n"
        "        elif not any(_tgot[d] > _T70_FLOOR[d] for d in _tgot):\n"
        "            fails.append(f\"t70b20 motion_relink_tight_edges {_tgot} equal the 6.5-gate runs' on all four movies: \"\n"
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
    # sv_mark: t65b20 is in sv_mark (its cell 4 is hsg200's byte for byte); t70b20's cell 4 is t65b20's byte for byte
    if '"t65b20": "SV_ARM_HSG200"' not in t:
        raise SystemExit("t65b20 is not in sv_mark; refusing to guess the body marker")
    t = t.replace(anchors["need"], entry + anchors["need"], 1)
    t = t.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t = t.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t = t.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % TAG, 1)
    t = t.replace(anchors["xcheck"], xcheck + anchors["xcheck"], 1)
    ast.parse(t)
    compile(t, str(GATE), "exec")
    if need_of(t, TAG) != pats:
        raise SystemExit("the written need entry does not read back as the computed patterns")
    before = GATE.read_text(encoding="utf-8")
    if before != t0:
        raise SystemExit("gate.py changed while the entry was being prepared (another installer?); nothing written, re-run")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(before, encoding="utf-8")
    GATE.write_text(t, encoding="utf-8")
    res = {"neg_t65b20_as_t70b20": gate("out_t65b20", TAG),
           "neg_t65s3_as_t70b20": gate("out_t65s3", TAG),
           "neg_t65b25_as_t70b20": gate("out_t65b25", TAG),
           "neg_t6stk3_as_t70b20": gate("out_t6stk3", TAG),
           "pos_t65b20": gate("out_t65b20", "t65b20"), "pos_t65b25": gate("out_t65b25", "t65b25"),
           "pos_t65s3": gate("out_t65s3", "t65s3"), "pos_t6stk3": gate("out_t6stk3", "t6stk3"),
           "pos_t6r70": gate("out_t6r70", "t6r70"), "pos_ourvzl": gate("out_ourvzl", "ourvzl")}
    with tempfile.TemporaryDirectory() as tmp:
        res["syn_pos_t70b20"] = gate_path(synthetic(tmp, "bump", {d: 1 for d in MOVIES}), TAG)
        res["syn_neg_equal_tight"] = gate_path(synthetic(tmp, "equal", {}), TAG)
        res["syn_neg_low_tight"] = gate_path(synthetic(tmp, "low", {MOVIES[0]: 5, MOVIES[1]: -1}), TAG)
    if list((ROOT / "data").glob("out_%s/*.log" % TAG)):
        res["pos_" + TAG] = gate("out_" + TAG, TAG)
    for k, v in res.items():
        print(k, "->", v[:500])
    ok = all("GATE_FAIL" in v for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_") and k != "pos_" + TAG) \
        and "motion_relink_tight_edges" in res["neg_t65b20_as_t70b20"] \
        and "GATE_PASS" in res["syn_pos_t70b20"] \
        and "GATE_FAIL" in res["syn_neg_equal_tight"] and "equal the 6.5-gate runs'" in res["syn_neg_equal_tight"] \
        and "GATE_FAIL" in res["syn_neg_low_tight"] and "fell BELOW the 6.5-gate runs'" in res["syn_neg_low_tight"]
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
