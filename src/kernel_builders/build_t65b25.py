#!/usr/bin/env python3
"""t65b25 = t65s3 (pick B, 0.954: t6stk3 + motion-relink TIGHT 6.0 -> 6.5) with the motion-relink learned-edge
bonus raised 1.6 -> 2.5. Everything else is t65s3's byte for byte. Single-constant successor of t65b20 (bonus 2.0,
submitted 56628029): vs v_t65b20 only cell 0 differs, and only by the bonus value (2.0 -> 2.5) and the ARM_XENV tag.

usage: python scratch_kernels/build_t65b25.py [tag]        (default tag t65b25)

WHY (09-28 neighbor replay, HANDOFF 09-28 06:40Z): node-neutral linker replay on the 72 GT-richest train movies (exact
scorer), 4 arms x 72 movies: tight6.5+bonus2.5 = +2.93 ticks [+1.72, +4.16] pooled vs t6stk3 (44b6 +1.93 [+0.46, +3.53],
6bba +3.26), +0.38 [+0.09, +0.67] over t65b20; +0.008% nodes, 0 forks (the bonus only re-weighs the assignment cost
inside motion_relink_edges: cost = motion + 0.05*raw - BONUS*prob). The bonus effect plateaus above 2.5.

HOW: exactly build_t65b20.py's path. t65s3's cell 0 sets os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = '1.6' and
prints "ARM_STK3B learned_bonus=1.6" right beside it. Cell 2 reads the env into MOTION_RELINK_LEARNED_BONUS and echoes
it as "motion_relink_learned_bonus": <float> in CONFIG_DISPLAY, which is the receipt the gate pins (2.5 not followed by
a digit). Both cell-0 lines are anchored exactly once and rewritten 1.6 -> 2.5; a cell-0 ARM_XENV identity line is
appended. No other cell is touched (checked below, cell by cell, against BOTH v_t65s3 and v_t65b20).
Markers: ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.50 LCEFR=kept (cell 0), ARM_STK3B learned_bonus=2.5 (cell 0),
"motion_relink_learned_bonus": 2.5 (cell 2 echo), unchanged ARM_STK3V / ARM_T65H / ARM_LCEFR / SV_ARM_HSG200 lines.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65s3"
BASE_MD5 = "beb2e49d662e8bf6e39b201066d95f45"  # v_t65s3/kernel.ipynb (pick B 56496604; same pin as build_t65b20.py)
SIB = SK / "v_t65b20"
SIB_MD5 = "3ceebd4c868985d0fd7c1d02321999f2"  # v_t65b20/kernel.ipynb as built by build_t65b20.py (submitted 56628029)
NL = chr(10)

ENV_OLD = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'1.6\'' + NL
ENV_NEW = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'2.5\'' + NL
ENV_SIB = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'2.0\'' + NL
MARK_OLD = 'print("ARM_STK3B learned_bonus=1.6", flush=True)' + NL
MARK_NEW = 'print("ARM_STK3B learned_bonus=2.5", flush=True)' + NL
MARK_SIB = 'print("ARM_STK3B learned_bonus=2.0", flush=True)' + NL
TIGHT_ENV = 'os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.5"'
TIGHT_MARK = 'print("ARM_T65H tight_um=6.5", flush=True)' + NL
XENV_FMT = 'print("ARM_XENV tag=%s TIGHT=6.5 BONUS=%s LCEFR=kept", flush=True)'


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t65b25"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t65s3/kernel.ipynb changed since the replay check (md5 mismatch)")
    if hashlib.md5((SIB / "kernel.ipynb").read_bytes()).hexdigest() != SIB_MD5:
        raise SystemExit("STOP: v_t65b20/kernel.ipynb changed since it was submitted (md5 mismatch)")
    nb, cells = cells_of(BASE / "kernel.ipynb")
    orig = list(cells)
    c0 = cells[0]
    for name, a in (("env_bonus", ENV_OLD), ("mark_bonus", MARK_OLD), ("env_tight", TIGHT_ENV), ("mark_tight", TIGHT_MARK)):
        if c0.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c0.count(a)))
    if c0.index(ENV_OLD) + len(ENV_OLD) != c0.index(MARK_OLD):
        raise SystemExit("the ARM_STK3B print is not the line right after the bonus env assignment")
    for bad in ("ARM_XENV", "BIOHUB_FLOWFIX", "ARM_FLOWFIX", "learned_bonus=2", "'2.0'", "'2.5'"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %r" % bad)
    # the cell-2 reader / echo must be the ones the gate pins
    if cells[2].count('MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))') != 1 \
            or cells[2].count('"motion_relink_learned_bonus": MOTION_RELINK_LEARNED_BONUS,') != 1:
        raise SystemExit("cell 2 does not read/echo BIOHUB_MOTION_RELINK_LEARNED_BONUS the way the gate expects")
    c0 = c0.replace(ENV_OLD, ENV_NEW, 1).replace(MARK_OLD, MARK_NEW, 1)
    xenv_new = XENV_FMT % (tag, "2.50")
    c0 = c0.rstrip(NL) + NL + xenv_new + NL
    cells[0] = c0
    # cell-by-cell diff vs v_t65s3: only cell 0 changes, and only by the two bonus lines + the appended marker
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i != 0 and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    d0 = [(x, y) for x, y in zip(orig[0].splitlines(), cells[0].splitlines()) if x != y]
    if len(cells[0].splitlines()) != len(orig[0].splitlines()) + 1 or len(d0) != 2 \
            or d0[0] != (ENV_OLD.rstrip(NL), ENV_NEW.rstrip(NL)) or d0[1] != (MARK_OLD.rstrip(NL), MARK_NEW.rstrip(NL)) \
            or not cells[0].startswith(orig[0].rstrip(NL).replace(ENV_OLD + MARK_OLD, ENV_NEW + MARK_NEW)):
        raise SystemExit("cell 0 differs from t65s3's by more than the bonus lines + the ARM_XENV marker: %r" % d0)
    for bad in ("'1.6'", "learned_bonus=1.6", "'2.0'", "learned_bonus=2.0", "BONUS=2.00"):
        if bad in cells[0]:
            raise SystemExit("a stale bonus value %r survived in cell 0" % bad)
    if cells[0].count(ENV_NEW) != 1 or cells[0].count(MARK_NEW) != 1 or cells[0].count(xenv_new) != 1:
        raise SystemExit("the 2.5 env / marker / ARM_XENV lines are not each present exactly once in cell 0")
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    k = 0
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["source"] = cells[k].splitlines(keepends=True)
            c["outputs"] = []
            c["execution_count"] = None
        k += 1
    dest = SK / ("v_" + tag)
    dest.mkdir(parents=True, exist_ok=True)
    with open(dest / "kernel.ipynb", "w", encoding="utf-8") as fh:
        json.dump(nb, fh)
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    with open(dest / "kernel-metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    # re-read and report the diff vs the base, cell by cell
    _, built = cells_of(dest / "kernel.ipynb")
    changed = [i for i, (a, b) in enumerate(zip(orig, built)) if a != b]
    if len(built) != len(orig) or changed != [0]:
        raise SystemExit("re-read: cells changed vs v_t65s3 = %r (expected [0])" % changed)
    print("built", dest, "| base v_t65s3 (md5 %s) | TIGHT 6.5 kept | BONUS 1.6 -> 2.5" % BASE_MD5)
    print("cells changed vs v_t65s3:", changed, "(cell 0 only)")
    for x, y in zip(orig[0].splitlines(), built[0].splitlines()):
        if x != y:
            print("  -", x)
            print("  +", y)
    print("  +", built[0].splitlines()[-1], "(appended)")
    # cell-by-cell diff vs the submitted sibling v_t65b20: cell 0 only, and only bonus value + tag
    _, sib = cells_of(SIB / "kernel.ipynb")
    if len(sib) != len(built):
        raise SystemExit("v_t65b20 has %d cells, built has %d" % (len(sib), len(built)))
    changed_sib = [i for i, (a, b) in enumerate(zip(sib, built)) if a != b]
    if changed_sib != [0]:
        raise SystemExit("cells changed vs v_t65b20 = %r (expected [0])" % changed_sib)
    sl, bl = sib[0].splitlines(), built[0].splitlines()
    if len(sl) != len(bl):
        raise SystemExit("cell 0 line count differs from v_t65b20 (%d vs %d)" % (len(sl), len(bl)))
    ds = [(x, y) for x, y in zip(sl, bl) if x != y]
    exp = [(ENV_SIB.rstrip(NL), ENV_NEW.rstrip(NL)), (MARK_SIB.rstrip(NL), MARK_NEW.rstrip(NL)),
           (XENV_FMT % ("t65b20", "2.00"), xenv_new)]
    if ds != exp:
        raise SystemExit("cell 0 differs from v_t65b20 by more than bonus value + tag: %r" % ds)
    print("cells changed vs v_t65b20 (md5 %s):" % SIB_MD5, changed_sib, "(cell 0 only; %d lines: env, marker, ARM_XENV)" % len(ds))
    for x, y in ds:
        print("  -", x)
        print("  +", y)
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
