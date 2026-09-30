#!/usr/bin/env python3
"""t70b20 = t65b20 (board 0.954, the team's top entry: t65s3 body = t6stk3 + motion-relink TIGHT 6.0 -> 6.5, with the
learned-edge bonus 1.6 -> 2.0) with the motion-relink TIGHT gate widened 6.5 -> 7.0. Bonus stays 2.0. Everything else
is t65b20's byte for byte: vs v_t65b20 only cell 0 differs, and only by the tight env value, the tight marker and the
ARM_XENV identity line.

usage: python scratch_kernels/build_t70b20.py [tag]        (default tag t70b20)

WHY (09-28 neighbor replay wf26, HANDOFF 09-28 06:40Z): node-neutral linker replay on the 72 GT-richest train movies
(exact scorer): tight7.0+bonus2.0 = +2.86 ticks pooled vs t6stk3 (44b6 +0.53 [-1.37, +2.68], 6bba +3.64), +0.018%
nodes, 0 forks. A deliberately different angle from the bonus line (t65b25): the wider tight gate recovers larger
single-frame moves in the first (tight) relink pass instead of re-weighing the assignment cost.

HOW: t65b20's cell 0 sets os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.5" (t65s3's line, with its original t65h
comment) and prints "ARM_T65H tight_um=6.5" on the next line. Cell 2 reads the env into MOTION_RELINK_TIGHT_UM
(float, default 6.0) and echoes it as "motion_relink_tight_um": <float> in CONFIG_DISPLAY; cell 5's
motion_relink_edges uses that global for the tight pass; cell 9 prints it again (PP_BASE_CONFIG, after tracking).
The env value is rewritten 6.5 -> 7.0 (the trailing comment is left alone), the marker is renamed to
"ARM_T70H tight_um=7.0" (a new arm name, so the gate's ARM_ allowlist rejects a t65-family log wearing this tag), and
the t65b20 ARM_XENV line is replaced in place. The unrelated BIOHUB_GAP_DENSITY_REFERENCE_UM = "6.5" stays.
Markers: ARM_XENV tag=<tag> TIGHT=7.0 BONUS=2.00 LCEFR=kept (cell 0), ARM_T70H tight_um=7.0 (cell 0),
"motion_relink_tight_um": 7.0 (cell 2 echo), MOTION_RELINK_TIGHT_UM 7.0 (cell 9 echo), unchanged ARM_STK3V /
ARM_STK3B learned_bonus=2.0 / ARM_LCEFR / SV_ARM_HSG200 lines.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65b20"
BASE_MD5 = "3ceebd4c868985d0fd7c1d02321999f2"  # v_t65b20/kernel.ipynb as built by build_t65b20.py (submitted 56628029)
NL = chr(10)

TIGHT_ENV_OLD = 'os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.5"'
TIGHT_ENV_NEW = 'os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "7.0"'
TIGHT_MARK_OLD = 'print("ARM_T65H tight_um=6.5", flush=True)' + NL
TIGHT_MARK_NEW = 'print("ARM_T70H tight_um=7.0", flush=True)' + NL
XENV_OLD = 'print("ARM_XENV tag=t65b20 TIGHT=6.5 BONUS=2.00 LCEFR=kept", flush=True)'
XENV_FMT = 'print("ARM_XENV tag=%s TIGHT=7.0 BONUS=2.00 LCEFR=kept", flush=True)'
BONUS_ENV = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'2.0\'' + NL
BONUS_MARK = 'print("ARM_STK3B learned_bonus=2.0", flush=True)' + NL
GAP_REF = 'os.environ["BIOHUB_GAP_DENSITY_REFERENCE_UM"] = "6.5"'  # unrelated 6.5, must survive untouched
C2_READ = 'MOTION_RELINK_TIGHT_UM = float(os.environ.get("BIOHUB_MOTION_RELINK_TIGHT_UM", "6.0"))'
C2_ECHO = '"motion_relink_tight_um": MOTION_RELINK_TIGHT_UM,'
C5_USE = 'for pass_name, gate_um in (("tight", MOTION_RELINK_TIGHT_UM), ("relaxed", MOTION_RELINK_RELAXED_UM)):'
C9_ECHO = '"MOTION_RELINK_TIGHT_UM",'


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t70b20"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t65b20/kernel.ipynb changed since it was submitted (md5 mismatch)")
    nb, cells = cells_of(BASE / "kernel.ipynb")
    orig = list(cells)
    c0 = cells[0]
    for name, a in (("env_tight", TIGHT_ENV_OLD), ("mark_tight", TIGHT_MARK_OLD), ("xenv", XENV_OLD),
                    ("env_bonus", BONUS_ENV), ("mark_bonus", BONUS_MARK), ("gap_ref", GAP_REF)):
        if c0.count(a) != 1:
            raise SystemExit("anchor %s matched %d times in cell 0" % (name, c0.count(a)))
    # the ARM_T65H print must be the line right after the tight env assignment (whose line carries a comment)
    env_line_end = c0.index(NL, c0.index(TIGHT_ENV_OLD)) + 1
    if env_line_end != c0.index(TIGHT_MARK_OLD):
        raise SystemExit("the ARM_T65H print is not the line right after the tight env assignment")
    if c0.rstrip(NL).splitlines()[-1] != XENV_OLD:
        raise SystemExit("t65b20's ARM_XENV line is not the last line of cell 0")
    for bad in ("ARM_T70H", "tight_um=7", "TIGHT=7", "tag=t70b20", "BIOHUB_FLOWFIX", "ARM_FLOWFIX", "RAWLINK"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %r" % bad)
    if any("BIOHUB_MOTION_RELINK_TIGHT_UM" in (c or "") for i, c in enumerate(cells) if i not in (0, 2)):
        raise SystemExit("BIOHUB_MOTION_RELINK_TIGHT_UM is referenced outside cells 0 and 2")
    # the cell-2 reader / echo, the cell-5 consumer and the cell-9 echo must be the ones the gate pins
    if cells[2].count(C2_READ) != 1 or cells[2].count(C2_ECHO) != 1:
        raise SystemExit("cell 2 does not read/echo BIOHUB_MOTION_RELINK_TIGHT_UM the way the gate expects")
    if cells[5].count(C5_USE) != 1:
        raise SystemExit("cell 5's motion_relink_edges does not take the tight gate from MOTION_RELINK_TIGHT_UM")
    if cells[9].count(C9_ECHO) != 1:
        raise SystemExit("cell 9's PP_BASE_CONFIG print does not list MOTION_RELINK_TIGHT_UM")
    xenv_new = XENV_FMT % tag
    c0 = c0.replace(TIGHT_ENV_OLD, TIGHT_ENV_NEW, 1).replace(TIGHT_MARK_OLD, TIGHT_MARK_NEW, 1)
    c0 = c0.replace(XENV_OLD, xenv_new, 1)
    cells[0] = c0
    # cell-by-cell diff vs v_t65b20: only cell 0 changes, and only by the tight env, tight marker and ARM_XENV lines
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i != 0 and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    ol, nl_ = orig[0].splitlines(), cells[0].splitlines()
    d0 = [(x, y) for x, y in zip(ol, nl_) if x != y]
    env_old_line = next(x for x in ol if x.startswith(TIGHT_ENV_OLD))
    exp = [(env_old_line, env_old_line.replace(TIGHT_ENV_OLD, TIGHT_ENV_NEW, 1)),
           (TIGHT_MARK_OLD.rstrip(NL), TIGHT_MARK_NEW.rstrip(NL)), (XENV_OLD, xenv_new)]
    if len(nl_) != len(ol) or d0 != exp:
        raise SystemExit("cell 0 differs from t65b20's by more than the tight env / marker / ARM_XENV lines: %r" % d0)
    # no leftover 6.5 tight value anywhere: the only 6.5 left in cell 0 is the unrelated gap-density reference
    for bad in ('RELINK_TIGHT_UM"] = "6.5"', "ARM_T65H", "tight_um=6.5", "TIGHT=6.5", "tag=t65b20"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("a stale t65b20 tight value %r survived" % bad)
    left65 = [x for x in cells[0].splitlines() if "6.5" in x]
    if len(left65) != 1 or not left65[0].startswith(GAP_REF):
        raise SystemExit("unexpected 6.5 lines left in cell 0: %r" % left65)
    for a in (TIGHT_MARK_NEW, BONUS_ENV, BONUS_MARK):
        if cells[0].count(a) != 1:
            raise SystemExit("%r is not present exactly once in cell 0" % a.rstrip(NL))
    if cells[0].count(TIGHT_ENV_NEW) != 1 or cells[0].count(xenv_new) != 1:
        raise SystemExit("the 7.0 env / ARM_XENV lines are not each present exactly once in cell 0")
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
        raise SystemExit("re-read: cells changed vs v_t65b20 = %r (expected [0])" % changed)
    bd = [(x, y) for x, y in zip(orig[0].splitlines(), built[0].splitlines()) if x != y]
    if bd != exp:
        raise SystemExit("re-read: cell 0 diff vs v_t65b20 is not the expected 3 lines: %r" % bd)
    print("built", dest, "| base v_t65b20 (md5 %s) | TIGHT 6.5 -> 7.0 | BONUS 2.0 kept" % BASE_MD5)
    print("cells changed vs v_t65b20:", changed, "(cell 0 only; %d lines: tight env, tight marker, ARM_XENV)" % len(bd))
    for x, y in bd:
        print("  -", x)
        print("  +", y)
    print("metadata:", meta["id"], "|", meta["title"], "| private", meta.get("is_private"),
          "| internet", meta.get("enable_internet"), "|", meta.get("machine_shape"))
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
