#!/usr/bin/env python3
r"""Gate entry for t65b25 (scratch_kernels/build_t65b25.py) = t65s3 (pick B, relink TIGHT 6.5) with the motion-relink
learned-edge bonus 1.6 -> 2.5 (single-constant successor of t65b20 = bonus 2.0, submitted 56628029). Run from the
project root: it backs up ops/gate.py (gate.py.bak_t65b25), patches it, self-tests, and restores the backup if any
self-test fails.
Dry run: T65B25_GATE=<copy of gate.py> python ops/add_t65b25_gate.py

t65b25 must prove on the visible run (4 movies):
  * need['t65b20'] (read out of gate.py with ast) with its two bonus markers rewritten to 2.5: cell-0
    'ARM_STK3B learned_bonus=2.5' AND the cell-2 CONFIG_DISPLAY echo '"motion_relink_learned_bonus": 2.5' (the echo is
    read out of the live global after float(), so it is the evidence the knob reached the linker); STK3V / T65H + 6.5
    echo / LCEFR runtime counters / line-fit echoes unchanged;
  * the cell-0 identity line ARM_XENV tag=t65b25 TIGHT=6.5 BONUS=2.50 LCEFR=kept;
  * sv_mark (>= 4 SV_ARM_HSG200 lines before 'Prediction completed': the 0.951 sub-voxel body);
  * FINAL within 15% of REF (node-neutral arm: +0.008% expected);
  * forbidden: any 2.0 or 1.6 bonus marker/echo (t65b20 / t65s3 wearing the name), a 6.0 relink echo (t6stk3 family
    wearing the name), a foreign ARM_XENV tag, foreign ARM_ / SV_ARM_ markers, tracebacks / IndentationError.
Self-tests: the t65b20 and t65s3 logs must FAIL as t65b25; t65b20 / t65s3 / t6stk3 / t6r70 / t6stk3ff / ourvzl logs
still PASS as themselves.
"""
import ast
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(os.environ.get("T65B25_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T65B25_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t65b25"
SRC = "t65b20"
OLD_MARK = r"ARM_STK3B learned_bonus=2\.0"
OLD_ECHO = r'"motion_relink_learned_bonus": 2\.0(?!\d)'
OLD_XENV = r"ARM_XENV tag=t65b20 TIGHT=6\.5 BONUS=2\.00 LCEFR=kept"
NEW_MARK = r"ARM_STK3B learned_bonus=2\.5"
NEW_ECHO = r'"motion_relink_learned_bonus": 2\.5(?!\d)'
XENV = r"ARM_XENV tag=t65b25 TIGHT=6\.5 BONUS=2\.50 LCEFR=kept"


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def gate(logdir, tag):
    lg = str(next((ROOT / "data" / logdir).glob("*.log")))
    out = subprocess.run([sys.executable, str(GATE), lg, tag], capture_output=True, text=True).stdout.strip()
    return out.splitlines()[-1] if out else "NO OUTPUT"


def main():
    t = GATE.read_text(encoding="utf-8")
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    base = list(need_of(t, SRC))
    if base.count(OLD_MARK) != 1 or base.count(OLD_ECHO) != 1 or base.count(OLD_XENV) != 1:
        raise SystemExit("need['t65b20'] does not carry exactly one 2.0 marker + one 2.0 echo + one XENV line: %r" % base)
    pats = [NEW_MARK if p == OLD_MARK else NEW_ECHO if p == OLD_ECHO else XENV if p == OLD_XENV else p for p in base]
    for stale in (r"2\.0", r"1\.6", "t65b20"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    if pats.count(NEW_MARK) != 1 or pats.count(NEW_ECHO) != 1 or pats.count(XENV) != 1:
        raise SystemExit("2.5 marker / echo / XENV not each present exactly once: %r" % pats)
    comment = ("        # --- t65b25: pick B t65s3 (relink tight 6.5) with the motion-relink learned-edge bonus 1.6 -> 2.5\n"
               "        # (t65b20 = 2.0, submitted 56628029; cost = motion + 0.05*raw - BONUS*prob inside motion_relink_edges).\n"
               "        # Node- and fork-neutral: exact replay +0.008% nodes, 0 forks (build_t65b25.py; ops/add_t65b25_gate.py).\n"
               "        # The 2.5 echo is the cell-2 receipt; a 2.0 or 1.6 marker/echo is forbidden below (t65b20 / t65s3\n"
               "        # wearing this name).\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    forbid = [r"ARM_STK3B learned_bonus=2\.0", r"ARM_STK3B learned_bonus=1\.6",
              r'"motion_relink_learned_bonus": (2\.0|1\.6)', r"ARM_XENV tag=(?!t65b25 )",
              r"Traceback \(most recent call last\)", "IndentationError",
              r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV)\b)[A-Z0-9]+", "ARM_RAWLINK", "ARM_FLOWFIX",
              r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", "GDIV_DS", "SUBVOXEL_ACTIVE",
              r'"output_linefit_strict_linear": true', r'"motion_relink_tight_um": 6\.0(?!\d)',
              r"ARM_T60H tight_um=6\.0"]
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": '"ourvzl": 0.15'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    t = t.replace(anchors["need"], entry + anchors["need"], 1)
    t = t.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    # sv_mark: t65b20 is in sv_mark (its cell 4 is hsg200's byte for byte); t65b25's cell 4 is t65b20's byte for byte
    if '"t65b20": "SV_ARM_HSG200"' not in t:
        raise SystemExit("t65b20 is not in sv_mark; refusing to guess the body marker")
    t = t.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t = t.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % TAG, 1)
    ast.parse(t)
    compile(t, str(GATE), "exec")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(GATE.read_text(encoding="utf-8"), encoding="utf-8")
    GATE.write_text(t, encoding="utf-8")
    res = {"neg_t65b20_as_t65b25": gate("out_t65b20", TAG),
           "neg_t65s3_as_t65b25": gate("out_t65s3", TAG),
           "neg_t6stk3_as_t65b25": gate("out_t6stk3", TAG),
           "pos_t65b20": gate("out_t65b20", "t65b20"), "pos_t65s3": gate("out_t65s3", "t65s3"),
           "pos_t6stk3": gate("out_t6stk3", "t6stk3"), "pos_t6r70": gate("out_t6r70", "t6r70"),
           "pos_t6stk3ff": gate("out_t6stk3ff", "t6stk3ff")}
    if list((ROOT / "data").glob("out_ourvzl/*.log")):
        res["pos_ourvzl"] = gate("out_ourvzl", "ourvzl")
    if list((ROOT / "data").glob("out_%s/*.log" % TAG)):
        res["pos_" + TAG] = gate("out_" + TAG, TAG)
    for k, v in res.items():
        print(k, "->", v[:400])
    ok = all("GATE_FAIL" in v for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_") and k != "pos_" + TAG)
    if not ok:
        GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit("self-test failed; gate.py restored from " + bak.name)
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
