#!/usr/bin/env python3
"""t65b25r70 = t6r70 (t6stk3 + raw-ILP override "rawlink" at min_prob 0.70) with t65b25's linker settings
(motion-relink TIGHT 6.0 -> 6.5 and learned-edge bonus 1.6 -> 2.5, the exact lines v_t65s3 / v_t65b25 carry).

usage: python scratch_kernels/build_t65b25r70.py [tag]        (default tag t65b25r70)

WHY: both components beat their base on the public board at full precision (t6r70 > t6stk3; t65b20 > t6r70, t65b25 is
its replay-gated bonus-2.5 neighbor). They are disjoint deltas on the same t6stk3 body:
  t6r70  vs t6stk3: cell 0 +1 line (BIOHUB_RAWLINK_MIN_PROB "0.70"), cell 2 reader/echo/ARM_RAWLINK, cell 5 rawlink_override.
  t65b25 vs t6stk3: cell 0 only: tight env + ARM_T65H marker, bonus env + ARM_STK3B marker, appended ARM_XENV.
HOW: start from v_t6r70 (its rawlink blocks stay byte for byte) and rewrite t6stk3's four cell-0 linker lines into
t65s3/t65b25's four lines, then append an ARM_XENV identity line. Checked cell by cell against BOTH v_t6r70 (only those
cell-0 lines differ) and v_t65b25 (only the rawlink env line, the ARM_XENV text and t6r70's cell 2/5 blocks differ,
and those cells equal v_t6r70's exactly).
Markers: ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept (cell 0), ARM_T65H tight_um=6.5 (cell 0),
ARM_STK3B learned_bonus=2.5 (cell 0), t6r70's ARM_RAWLINK lines (cells 2/5), unchanged SV_ARM_HSG200 line.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6r70"
BASE_MD5 = "38adf357f63250a34ce7f6337c47c626"  # v_t6r70/kernel.ipynb (representative 0.954 before t65b20)
SIB = SK / "v_t65b25"
SIB_MD5 = "5a7beb98dc0d2c4234e99c34895c3ed1"  # v_t65b25/kernel.ipynb as built by build_t65b25.py (submitted 56639660)
BODY = SK / "v_t6stk3"
BODY_MD5 = "643f4de949f707e161b118733e35e6df"
NL = chr(10)

# t6stk3 lines (present in v_t6r70) -> t65s3/t65b25 lines, exactly as those kernels carry them
SWAPS = [
    ('os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.0"  # t60h: untested on the 0.951 body; hfusion\'s hidden-rerun validator likely picked 6.0',
     'os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.5"  # t65h: untested on the 0.951 body; hfusion\'s hidden-rerun validator likely picked 6.0'),
    ('print("ARM_T60H tight_um=6.0", flush=True)',
     'print("ARM_T65H tight_um=6.5", flush=True)'),
    ('os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'1.6\'',
     'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'2.5\''),
    ('print("ARM_STK3B learned_bonus=1.6", flush=True)',
     'print("ARM_STK3B learned_bonus=2.5", flush=True)'),
]
RAWLINK_ENV = 'os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"  # rawlink: raw ILP edges >= this override conflicting final edges (josephadamski91 V1057)'
XENV_FMT = 'print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept", flush=True)'
SIB_XENV = 'print("ARM_XENV tag=t65b25 TIGHT=6.5 BONUS=2.50 LCEFR=kept", flush=True)'


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t65b25r70"
    for d, m in ((BASE, BASE_MD5), (SIB, SIB_MD5), (BODY, BODY_MD5)):
        if md5(d / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (d.name, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, sib = cells_of(SIB / "kernel.ipynb")
    orig = list(cells)
    c0 = cells[0]
    lines = c0.split(NL)
    for old, new in SWAPS:
        if lines.count(old) != 1:
            raise SystemExit("anchor %r matched %d lines in t6r70 cell 0" % (old[:60], lines.count(old)))
        if sum(1 for l in sib[0].split(NL) if l == new) != 1:
            raise SystemExit("target %r is not exactly once in v_t65b25 cell 0" % new[:60])
    if lines.count(RAWLINK_ENV) != 1:
        raise SystemExit("rawlink env line not exactly once in t6r70 cell 0")
    for bad in ("ARM_XENV", "ARM_T65H", "'2.5'", "'2.0'", "learned_bonus=2"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %r" % bad)
    if cells[2].count('MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))') != 1 \
            or cells[2].count('"motion_relink_learned_bonus": MOTION_RELINK_LEARNED_BONUS,') != 1:
        raise SystemExit("cell 2 does not read/echo BIOHUB_MOTION_RELINK_LEARNED_BONUS the way the gate expects")
    if "BIOHUB_RAWLINK_MIN_PROB" not in cells[2] or cells[5].count("def rawlink_override(") != 1:
        raise SystemExit("rawlink component missing from the base")
    for old, new in SWAPS:
        lines[lines.index(old)] = new
    c0 = NL.join(lines)
    xenv = XENV_FMT % tag
    c0 = c0.rstrip(NL) + NL + xenv + NL
    cells[0] = c0
    for bad in ('"6.0"', "tight_um=6.0", "'1.6'", "learned_bonus=1.6", "'2.0'", "learned_bonus=2.0", "BONUS=2.00", "ARM_T60H"):
        if bad in cells[0]:
            raise SystemExit("a stale linker value %r survived in cell 0" % bad)
    for need in [n for _, n in SWAPS] + [RAWLINK_ENV, xenv]:
        if cells[0].split(NL).count(need) != 1:
            raise SystemExit("line %r not exactly once in built cell 0" % need[:60])
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
    sib_meta = json.loads((SIB / "kernel-metadata.json").read_text(encoding="utf-8"))
    for key in ("dataset_sources", "competition_sources", "kernel_sources", "model_sources", "enable_gpu",
                "enable_internet", "machine_shape", "is_private"):
        if meta.get(key) != sib_meta.get(key):
            raise SystemExit("v_t6r70 and v_t65b25 metadata differ on %s" % key)
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    with open(dest / "kernel-metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    # ---- re-read and diff vs v_t6r70: cell 0 only, the 4 linker lines + appended ARM_XENV
    _, built = cells_of(dest / "kernel.ipynb")
    if len(built) != len(orig):
        raise SystemExit("cell count changed")
    changed = [i for i, (a, b) in enumerate(zip(orig, built)) if a != b]
    if changed != [0]:
        raise SystemExit("cells changed vs v_t6r70 = %r (expected [0])" % changed)
    ol, bl = orig[0].rstrip(NL).split(NL), built[0].rstrip(NL).split(NL)
    if len(bl) != len(ol) + 1 or bl[-1] != xenv:
        raise SystemExit("cell 0 is not t6r70's + one appended ARM_XENV line")
    d0 = [(x, y) for x, y in zip(ol, bl) if x != y]
    if sorted(d0) != sorted(SWAPS) or len(d0) != len(SWAPS):
        raise SystemExit("cell 0 differs from t6r70's by more than the 4 linker lines: %r" % d0)
    print("built", dest, "| base v_t6r70 (md5 %s) | TIGHT 6.0 -> 6.5 | BONUS 1.6 -> 2.5 | RAWLINK 0.70 kept" % BASE_MD5)
    print("cells changed vs v_t6r70:", changed, "(cell 0 only; %d swapped lines + ARM_XENV)" % len(d0))
    for x, y in d0:
        print("  -", x)
        print("  +", y)
    print("  +", xenv, "(appended)")

    # ---- diff vs v_t65b25: cell 0 = rawlink env line + ARM_XENV text; cells 2/5 = t6r70's rawlink blocks
    changed_sib = [i for i, (a, b) in enumerate(zip(sib, built)) if a != b]
    if changed_sib != [0, 2, 5]:
        raise SystemExit("cells changed vs v_t65b25 = %r (expected [0, 2, 5])" % changed_sib)
    for i in (2, 5):
        if built[i] != orig[i]:
            raise SystemExit("cell %d is not t6r70's byte for byte" % i)
    _, body = cells_of(BODY / "kernel.ipynb")
    for i in (2, 5):
        if sib[i] != body[i]:
            raise SystemExit("v_t65b25 cell %d is not t6stk3's (the rawlink port assumption fails)" % i)
    sl = sib[0].rstrip(NL).split(NL)
    exp = [l for l in bl if l != RAWLINK_ENV]
    exp[-1] = SIB_XENV
    if exp != sl:
        raise SystemExit("cell 0 minus the rawlink env line (and with t65b25's tag) is not v_t65b25's cell 0")
    print("cells changed vs v_t65b25 (md5 %s):" % SIB_MD5, changed_sib)
    print("  cell 0: + %s" % RAWLINK_ENV)
    print("          - %s" % SIB_XENV)
    print("          + %s" % xenv)
    print("  cells 2, 5: == v_t6r70 byte for byte (rawlink reader/echo/ARM_RAWLINK + rawlink_override); v_t65b25's == t6stk3's")
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
