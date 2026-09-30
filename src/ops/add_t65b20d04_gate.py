#!/usr/bin/env python3
r"""Gate entry for t65b20d04 (scratch_kernels/build_t65b20d04.py) = t65b20 (our top public entry 56628029: t65s3 body,
relink TIGHT 6.5, learned bonus 2.0) with the tracking ILP division weight 1.2 -> 0.4. Run from the project root: it
backs up ops/gate.py (gate.py.bak_t65b20d04), patches it, self-tests, and restores the backup if any self-test fails.
Dry run: T65B20D04_GATE=<copy of gate.py> python ops/add_t65b20d04_gate.py

t65b20d04 must prove on the visible run (4 movies):
  * need['t65b20'] (read out of gate.py with ast) with its XENV line swapped for
    'ARM_XENV tag=t65b20d04 TIGHT=6.5 BONUS=2.00 ILPDIV=0.4 LCEFR=kept' (bonus 2.0 / tight 6.5 / LCEFR / line-fit
    receipts unchanged), plus the division-weight receipts: cell-0 'ARM_ILPDIV weight=0.4', the cell-2 CONFIG_DISPLAY
    echo '"ilp_division_weight": 0.4' (read from the live global after float()), and '--ilp-division-weight 0.4' on
    the predictor command line (the value the ILPSolver actually receives);
  * sv_mark (>= 4 SV_ARM_HSG200 lines before 'Prediction completed': the 0.951 sub-voxel body);
  * FINAL within 15% of REF. Exact FINAL / division counts are NOT pinned: a sub-1 weight lets the ILP fork, so they
    are expected to move;
  * forbidden: any division-weight echo / command-line value / ARM_ILPDIV value other than 0.4 (explicitly 1.2 =
    t65b20 wearing the name), a non-2.0 bonus marker/echo (t65b25 / t65s3), a non-6.5 tight echo/marker, a foreign
    ARM_XENV tag, foreign ARM_ / SV_ARM_ markers, tracebacks / IndentationError.
Self-tests: the t65b20 and t65b25 logs must FAIL as t65b20d04; a synthetic t65b20d04 log (t65b20's log with the three
receipts + markers rewritten, written to a temp dir) must PASS and the same log with one shard still at 1.2 must FAIL;
t65b20 / t65b25 / t70b20 / t65b25r70 / ourvzlb25 / t65s3 / t6stk3 / t6r70 logs still PASS as themselves.
"""
import ast
import json
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("T65B20D04_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T65B20D04_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t65b20d04"
SRC = "t65b20"
OLD_XENV = r"ARM_XENV tag=t65b20 TIGHT=6\.5 BONUS=2\.00 LCEFR=kept"
XENV = r"ARM_XENV tag=t65b20d04 TIGHT=6\.5 BONUS=2\.00 ILPDIV=0\.4 LCEFR=kept"
DIV_NEED = [r"ARM_ILPDIV weight=0\.4(?!\d)",
            r'"ilp_division_weight": 0\.4(?!\d)',
            r"--ilp-division-weight 0\.4(?!\d)"]
OLD_ARMS = r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV)\b)[A-Z0-9]+"
NEW_ARMS = r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|ILPDIV)\b)[A-Z0-9]+"
OLD_XFORB = r"ARM_XENV tag=(?!t65b20 )"
NEW_XFORB = r"ARM_XENV tag=(?!t65b20d04 )"
EXTRA_FORBID = [r'"ilp_division_weight": 1\.2', r"--ilp-division-weight 1\.2", r"ARM_ILPDIV weight=1\.2",
                r'"ilp_division_weight": (?!0\.4(?!\d))', r"--ilp-division-weight (?!0\.4(?!\d))",
                r"ARM_ILPDIV weight=(?!0\.4(?!\d))",
                r"ARM_STK3B learned_bonus=(?!2\.0(?!\d))", r'"motion_relink_learned_bonus": (?!2\.0(?!\d))',
                r'"motion_relink_tight_um": (?!6\.5(?!\d))', r"ARM_T\d+H tight_um=(?!6\.5(?!\d))"]
OTHER_AGENT_TAGS = ("t70b25", "t675b25")  # may be installed concurrently by another agent: must survive this edit


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def forbid_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Subscript):
            tg = node.targets[0]
            if getattr(tg.value, "id", None) == "forbid" and isinstance(tg.slice, ast.Constant) and tg.slice.value == key:
                return ast.literal_eval(node.value)
    raise SystemExit("no forbid[%r] = [...] statement" % key)


def gate_path(lg, tag):
    out = subprocess.run([sys.executable, str(GATE), str(lg), tag], capture_output=True, text=True).stdout.strip()
    return out.splitlines()[-1] if out else "NO OUTPUT"


def gate(logdir, tag):
    return gate_path(next((ROOT / "data" / logdir).glob("*.log")), tag)


def synth_logs(tmp):
    """t65b20's visible log with the division-weight receipts rewritten as a t65b20d04 run would print them."""
    src = next((ROOT / "data" / "out_t65b20").glob("*.log"))
    ev = json.loads(src.read_text(encoding="utf-8"))
    xo = "ARM_XENV tag=t65b20 TIGHT=6.5 BONUS=2.00 LCEFR=kept"
    xn = "ARM_XENV tag=t65b20d04 TIGHT=6.5 BONUS=2.00 ILPDIV=0.4 LCEFR=kept"
    hits = {"echo": 0, "cmd": 0, "xenv": 0}
    good, bad = [], []
    for e in ev:
        d = e.get("data", "")
        g = d
        if '"ilp_division_weight": 1.2,' in g:
            g = g.replace('"ilp_division_weight": 1.2,', '"ilp_division_weight": 0.4,'); hits["echo"] += 1
        if "--ilp-division-weight 1.2 " in g:
            g = g.replace("--ilp-division-weight 1.2 ", "--ilp-division-weight 0.4 "); hits["cmd"] += 1
        if xo in g:
            g = g.replace(xo, "ARM_ILPDIV weight=0.4\n" + xn); hits["xenv"] += 1
        good.append(dict(e, data=g))
        # negative twin: shard 1 still carries 1.2
        bad.append(dict(e, data=d if ("GPU shard 1:" in d and "--ilp-division-weight 1.2 " in d) else g))
    if hits != {"echo": 1, "cmd": 2, "xenv": 1}:
        raise SystemExit("synthetic log rewrite hit counts %r (want echo 1, cmd 2, xenv 1)" % hits)
    pg, pb = pathlib.Path(tmp) / "synth_good.log", pathlib.Path(tmp) / "synth_bad.log"
    pg.write_text(json.dumps(good), encoding="utf-8")
    pb.write_text(json.dumps(bad), encoding="utf-8")
    return pg, pb


def main():
    t = GATE.read_text(encoding="utf-8")
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    present_before = [x for x in OTHER_AGENT_TAGS if "'%s'" % x in t or '"%s"' % x in t]
    base = list(need_of(t, SRC))
    if base.count(OLD_XENV) != 1:
        raise SystemExit("need['t65b20'] does not carry exactly one XENV line: %r" % base)
    if any("ilp_division" in p or "ILPDIV" in p for p in base):
        raise SystemExit("need['t65b20'] unexpectedly already pins a division weight: %r" % base)
    pats = [XENV if p == OLD_XENV else p for p in base] + DIV_NEED
    for stale in ("t65b20 ", r"1\.2", r"2\.5", r"1\.6", r"6\.0"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    if pats.count(XENV) != 1 or len(pats) != len(base) + len(DIV_NEED):
        raise SystemExit("XENV / division receipts not each present exactly once: %r" % pats)
    fb = list(forbid_of(t, SRC))
    if fb.count(OLD_ARMS) != 1 or fb.count(OLD_XFORB) != 1:
        raise SystemExit("forbid['t65b20'] lacks the ARM_ allowlist or the XENV-tag pattern: %r" % fb)
    forbid = [NEW_ARMS if p == OLD_ARMS else NEW_XFORB if p == OLD_XFORB else p for p in fb] + EXTRA_FORBID
    comment = ("        # --- t65b20d04: t65b20 (0.954 top entry 56628029; t65s3 body, relink tight 6.5, learned bonus 2.0)\n"
               "        # with the tracking ILP division weight 1.2 -> 0.4 (build_t65b20d04.py; ops/add_t65b20d04_gate.py).\n"
               "        # With ILP_APPEARANCE_WEIGHT = 0 the solver forks iff p2 >= weight, so 0.4 is the first value that\n"
               "        # lets the ILP fork: FINAL / division counts may move and are NOT pinned. Receipts: cell-0\n"
               "        # ARM_ILPDIV, the cell-2 echo and the predictor command line, all 0.4; any 1.2 is forbidden below.\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": '"ourvzl": 0.15'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    if '"t65b20": "SV_ARM_HSG200"' not in t:
        raise SystemExit("t65b20 is not in sv_mark; refusing to guess the body marker")
    n = t.replace(anchors["need"], entry + anchors["need"], 1)
    n = n.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    # sv_mark: t65b20d04's cell 4 is t65b20's byte for byte (only cell 0 differs), so its body marker is t65b20's
    n = n.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    n = n.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % TAG, 1)
    ast.parse(n)
    compile(n, str(GATE), "exec")
    if need_of(n, TAG) != pats or forbid_of(n, TAG) != forbid:
        raise SystemExit("patched gate.py does not round-trip the new need/forbid entries")
    # another agent may be editing gate.py right now: re-read immediately before writing, refuse on any change
    if GATE.read_text(encoding="utf-8") != t:
        raise SystemExit("gate.py changed while this installer was running; nothing written, re-run it")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(t, encoding="utf-8")
    GATE.write_text(n, encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        sg, sb = synth_logs(tmp)
        res = {"neg_t65b20_as_t65b20d04": gate("out_t65b20", TAG),
               "neg_t65b25_as_t65b20d04": gate("out_t65b25", TAG),
               "neg_synth_shard1_at_1.2": gate_path(sb, TAG),
               "pos_synth_t65b20d04": gate_path(sg, TAG)}
        for tg in ("t65b20", "t65b25", "t70b20", "t65b25r70", "ourvzlb25", "t65s3", "t6stk3", "t6r70"):
            res["pos_" + tg] = gate("out_" + tg, tg)
        if list((ROOT / "data").glob("out_%s/*.log" % TAG)):
            res["real_" + TAG] = gate("out_" + TAG, TAG)
    for k, v in res.items():
        print(k, "->", v[:400])
    ok = all("GATE_FAIL" in v for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_"))
    final_txt = GATE.read_text(encoding="utf-8")
    lost = [x for x in present_before if "'%s'" % x not in final_txt and '"%s"' % x not in final_txt]
    if lost:
        ok = False
        print("ERROR: entries present before this edit are gone afterwards:", lost)
    if not ok:
        GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit("self-test failed; gate.py restored from " + bak.name)
    print("other-agent entries present before and after:", present_before)
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
