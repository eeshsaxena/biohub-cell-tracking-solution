#!/usr/bin/env python3
"""t65b20 = t65s3 (pick B, 0.954: t6stk3 + motion-relink TIGHT 6.0 -> 6.5) with the motion-relink learned-edge
bonus raised 1.6 -> 2.0. Everything else is t65s3's byte for byte.

usage: python scratch_kernels/build_t65b20.py [tag]        (default tag t65b20)

WHY (09-28 linker sweep, HANDOFF 09-28 ~03:30Z): node-neutral linker sweep on the 72 GT-richest train movies (exact
scorer), 11 arms x 817 runs: tight6.5+bonus2.0 = +2.55 ticks [+1.46, +3.70] pooled vs t6stk3 (44b6 +1.28, 6bba +2.98),
the highest node-neutral linker replay recorded; +0.005% nodes, 0 forks (the bonus only re-weighs the assignment cost
inside motion_relink_edges: cost = motion + 0.05*raw - BONUS*prob). Interactions additive with the tight change.

HOW: t65s3's cell 0 sets os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = '1.6' and prints "ARM_STK3B
learned_bonus=1.6" right beside it (t6stk3's lines; t65s3 only added the TIGHT 6.5 pair). Cell 2 reads the env into
MOTION_RELINK_LEARNED_BONUS and echoes it as "motion_relink_learned_bonus": <float> in CONFIG_DISPLAY, which is the
receipt the gate pins (2.0 not followed by a digit). Both cell-0 lines are anchored exactly once and rewritten 1.6 -> 2.0; a cell-0
ARM_XENV identity line is appended. No other cell is touched (checked below, cell by cell).
Markers: ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.00 LCEFR=kept (cell 0), ARM_STK3B learned_bonus=2.0 (cell 0),
"motion_relink_learned_bonus": 2.0 (cell 2 echo), unchanged ARM_STK3V / ARM_T65H / ARM_LCEFR / SV_ARM_HSG200 lines.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65s3"
BASE_MD5 = "beb2e49d662e8bf6e39b201066d95f45"  # v_t65s3/kernel.ipynb (pick B 56496604; same pin as build_t65s3ff.py)
NL = chr(10)

ENV_OLD = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'1.6\'' + NL
ENV_NEW = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'2.0\'' + NL
MARK_OLD = 'print("ARM_STK3B learned_bonus=1.6", flush=True)' + NL
MARK_NEW = 'print("ARM_STK3B learned_bonus=2.0", flush=True)' + NL
TIGHT_ENV = 'os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.5"'
TIGHT_MARK = 'print("ARM_T65H tight_um=6.5", flush=True)' + NL


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t65b20"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t65s3/kernel.ipynb changed since the replay check (md5 mismatch)")
    nb, cells = cells_of(BASE / "kernel.ipynb")
    orig = list(cells)
    c0 = cells[0]
    for name, a in (("env_bonus", ENV_OLD), ("mark_bonus", MARK_OLD), ("env_tight", TIGHT_ENV), ("mark_tight", TIGHT_MARK)):
        if c0.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c0.count(a)))
    if c0.index(ENV_OLD) + len(ENV_OLD) != c0.index(MARK_OLD):
        raise SystemExit("the ARM_STK3B print is not the line right after the bonus env assignment")
    for bad in ("ARM_XENV", "BIOHUB_FLOWFIX", "ARM_FLOWFIX", "learned_bonus=2", "'2.0'"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %r" % bad)
    # the cell-2 reader / echo must be the ones the gate pins
    if cells[2].count('MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))') != 1 \
            or cells[2].count('"motion_relink_learned_bonus": MOTION_RELINK_LEARNED_BONUS,') != 1:
        raise SystemExit("cell 2 does not read/echo BIOHUB_MOTION_RELINK_LEARNED_BONUS the way the gate expects")
    c0 = c0.replace(ENV_OLD, ENV_NEW, 1).replace(MARK_OLD, MARK_NEW, 1)
    c0 = c0.rstrip(NL) + NL + 'print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.00 LCEFR=kept", flush=True)' % tag + NL
    cells[0] = c0
    # cell-by-cell diff: only cell 0 changes, and only by the two bonus lines + the appended marker
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i != 0 and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    d0 = [(x, y) for x, y in zip(orig[0].splitlines(), cells[0].splitlines()) if x != y]
    if len(cells[0].splitlines()) != len(orig[0].splitlines()) + 1 or len(d0) != 2 \
            or d0[0] != (ENV_OLD.rstrip(NL), ENV_NEW.rstrip(NL)) or d0[1] != (MARK_OLD.rstrip(NL), MARK_NEW.rstrip(NL)) \
            or not cells[0].startswith(orig[0].rstrip(NL).replace(ENV_OLD + MARK_OLD, ENV_NEW + MARK_NEW)):
        raise SystemExit("cell 0 differs from t65s3's by more than the bonus lines + the ARM_XENV marker: %r" % d0)
    if "'1.6'" in cells[0] or "learned_bonus=1.6" in cells[0]:
        raise SystemExit("a 1.6 bonus survived in cell 0")
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
    print("built", dest, "| base v_t65s3 (md5 %s) | TIGHT 6.5 kept | BONUS 1.6 -> 2.0" % BASE_MD5)
    print("cells changed vs v_t65s3:", changed, "(cell 0 only)" if changed == [0] else "UNEXPECTED")
    for x, y in zip(orig[0].splitlines(), built[0].splitlines()):
        if x != y:
            print("  -", x)
            print("  +", y)
    print("  +", built[0].splitlines()[-1], "(appended)")
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
