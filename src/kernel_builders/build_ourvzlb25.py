#!/usr/bin/env python3
"""ourvzlb25 = ourvzl (board 0.953, 56572442: our linker stack on the PUBLIC V1284 coordinate head for y/x + our
sub-voxel z fed to the edge model) with t65b25's climbing linker settings: motion-relink TIGHT gate 6.0 -> 6.5 um and
learned-edge BONUS 1.6 -> 2.5. Everything else is ourvzl's byte for byte (cell 4 = the V1284 + z-to-arr body).

usage: python scratch_kernels/build_ourvzlb25.py [tag]        (default tag ourvzlb25)

WHY: t65b20 (t6 body, tight 6.5 / bonus 2.0) became the team's top entry above t6r70; t65b25 (bonus 2.5) is its
gated neighbor (replay +0.38 over t65b20). ourvzl is a DIFFERENT coordinate body (V1284 y/x) from the t6/t65 line, so
the same linker change on it is both an upside shot and a decorrelated hedge. The linker knobs act after detection
(cost = motion + 0.05*raw - BONUS*prob inside motion_relink_edges; tight = the relink gate), so the V1284 / sub-voxel
detections and their SV_ARM_HSG200 / ARM_SV_Z_TO_ARR prints must be unchanged.

HOW: ourvzl's cell 0 carries exactly t6stk3's linker lines (tight 6.0 + ARM_T60H, bonus '1.6' + ARM_STK3B,
velocity 0.25 + ARM_STK3V). The four lines t6stk3 -> t65b25 changed in cell 0 (tight env + ARM_T65H marker from
v_t65s3, bonus env + ARM_STK3B marker) are rewritten here to the byte-identical t65b25 lines, and the check below
proves the ourvzl -> ourvzlb25 line diff equals the t6stk3 -> t65b25 line diff. ourvzl's single identity line
    ARM_XENV tag=ourvzl V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx
is REPLACED (not duplicated: a second tag=ourvzl line would be a foreign XENV tag) by
    ARM_XENV tag=ourvzlb25 TIGHT=6.5 BONUS=2.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx
which keeps ourvzl's body identity fields. Cell 2 reads both envs and echoes "motion_relink_tight_um": 6.5 and
"motion_relink_learned_bonus": 2.5 in CONFIG_DISPLAY (the receipts the gate pins). No other cell is touched.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourvzl"
BASE_MD5 = "da305e401e50aee05250932e85d0d79e"  # v_ourvzl/kernel.ipynb (submitted 56572442; == kaggle pull 09-28)
T6STK3 = SK / "v_t6stk3"
T6STK3_MD5 = "643f4de949f707e161b118733e35e6df"  # v_t6stk3/kernel.ipynb (same pin as build_t65b25r70.py)
T65B25 = SK / "v_t65b25"
T65B25_MD5 = "5a7beb98dc0d2c4234e99c34895c3ed1"  # v_t65b25/kernel.ipynb (submitted 56639660)
NL = chr(10)

BONUS_ENV_OLD = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'1.6\''
BONUS_ENV_NEW = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'2.5\''
BONUS_MARK_OLD = 'print("ARM_STK3B learned_bonus=1.6", flush=True)'
BONUS_MARK_NEW = 'print("ARM_STK3B learned_bonus=2.5", flush=True)'
TIGHT_ENV_OLD = ('os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.0"  # t60h: untested on the 0.951 body; '
                 "hfusion's hidden-rerun validator likely picked 6.0")
TIGHT_ENV_NEW = ('os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.5"  # t65h: untested on the 0.951 body; '
                 "hfusion's hidden-rerun validator likely picked 6.0")
TIGHT_MARK_OLD = 'print("ARM_T60H tight_um=6.0", flush=True)'
TIGHT_MARK_NEW = 'print("ARM_T65H tight_um=6.5", flush=True)'
XENV_OLD = 'print("ARM_XENV tag=ourvzl V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx", flush=True)'
XENV_FMT = 'print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx", flush=True)'
VEL_ENV = 'os.environ["BIOHUB_MOTION_RELINK_VELOCITY_WEIGHT"] = "0.25"'
VEL_MARK = 'print("ARM_STK3V velocity_weight=0.25", flush=True)'


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def line_diff(a, b):
    al, bl = a.splitlines(), b.splitlines()
    return [(x, y) for x, y in zip(al, bl) if x != y], len(al), len(bl)


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "ourvzlb25"
    for p, want, what in ((BASE, BASE_MD5, "v_ourvzl"), (T6STK3, T6STK3_MD5, "v_t6stk3"), (T65B25, T65B25_MD5, "v_t65b25")):
        if md5(p / "kernel.ipynb") != want:
            raise SystemExit("STOP: %s/kernel.ipynb changed (md5 mismatch)" % what)
    nb, cells = cells_of(BASE / "kernel.ipynb")
    orig = list(cells)
    c0 = cells[0]
    lines = c0.split(NL)
    anchors = {"bonus_env": BONUS_ENV_OLD, "bonus_mark": BONUS_MARK_OLD, "tight_env": TIGHT_ENV_OLD,
               "tight_mark": TIGHT_MARK_OLD, "xenv": XENV_OLD, "vel_env": VEL_ENV, "vel_mark": VEL_MARK}
    for name, a in anchors.items():
        if lines.count(a) != 1 or c0.count(a) != 1:
            raise SystemExit("anchor %s matched %d lines / %d substrings in cell 0" % (name, lines.count(a), c0.count(a)))
    if lines.index(BONUS_ENV_OLD) + 1 != lines.index(BONUS_MARK_OLD) or lines.index(TIGHT_ENV_OLD) + 1 != lines.index(TIGHT_MARK_OLD):
        raise SystemExit("the ARM_STK3B / ARM_T60H prints are not right after their env assignments")
    for bad in ("'2.5'", "learned_bonus=2", "ARM_T65H", '"6.5"  # t65h', "ourvzlb25", "BIOHUB_FLOWFIX", "ARM_RAWLINK", "ARM_LCEFR"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %r" % bad)
    if sum("ARM_XENV" in (c or "") for c in cells) != 1 or c0.count("ARM_XENV") != 1:
        raise SystemExit("ourvzl should carry exactly one ARM_XENV line (cell 0)")
    # cell 2 must read + echo both knobs the way the gate expects (same reader as t6stk3 / t65b25)
    c2 = cells[2]
    for rd in ('MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))',
               '"motion_relink_learned_bonus": MOTION_RELINK_LEARNED_BONUS,',
               'os.environ.get("BIOHUB_MOTION_RELINK_TIGHT_UM"', '"motion_relink_tight_um": '):
        if c2.count(rd) != 1:
            raise SystemExit("cell 2 does not read/echo the linker knob via %r exactly once (%d)" % (rd, c2.count(rd)))
    xenv_new = XENV_FMT % tag
    rep = {BONUS_ENV_OLD: BONUS_ENV_NEW, BONUS_MARK_OLD: BONUS_MARK_NEW, TIGHT_ENV_OLD: TIGHT_ENV_NEW,
           TIGHT_MARK_OLD: TIGHT_MARK_NEW, XENV_OLD: xenv_new}
    cells[0] = NL.join(rep.get(l, l) for l in lines)
    # ---- checks on the new cell 0
    new0 = cells[0]
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i != 0 and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    d0, n_old, n_new = line_diff(orig[0], new0)
    if n_old != n_new or sorted(d0) != sorted(rep.items()):
        raise SystemExit("cell 0 differs from ourvzl's by more than the 4 linker lines + the XENV tag: %r" % d0)
    for bad in ("'1.6'", "learned_bonus=1.6", '"6.0"  # t60h', "ARM_T60H", "tight_um=6.0", "tag=ourvzl ", "BONUS=1.60"):
        if bad in new0:
            raise SystemExit("a stale ourvzl linker value %r survived in cell 0" % bad)
    for good in (BONUS_ENV_NEW, BONUS_MARK_NEW, TIGHT_ENV_NEW, TIGHT_MARK_NEW, xenv_new, VEL_ENV, VEL_MARK):
        if new0.split(NL).count(good) != 1:
            raise SystemExit("line %r not present exactly once in the new cell 0" % good)
    # the linker delta must be EXACTLY the one t6stk3 -> t65b25 applied (same 4 line pairs, byte for byte)
    _, s6 = cells_of(T6STK3 / "kernel.ipynb")
    _, s25 = cells_of(T65B25 / "kernel.ipynb")
    ref, n6, n25 = line_diff(s6[0], s25[0])
    if n25 != n6 + 1 or s25[0].rstrip(NL).split(NL)[-1] != 'print("ARM_XENV tag=t65b25 TIGHT=6.5 BONUS=2.50 LCEFR=kept", flush=True)':
        raise SystemExit("t6stk3 -> t65b25 cell 0 is not 'changed lines + one appended XENV line'")
    ours = [p for p in d0 if p[0] != XENV_OLD]
    if sorted(ref) != sorted(ours) or len(ref) != 4:
        raise SystemExit("linker delta differs from t6stk3 -> t65b25:\n ref %r\n ours %r" % (ref, ours))
    # ourvzl's non-cell-0 linker plumbing (cells 2/5/9/10) is t6stk3's, so the same env reaches the same code
    for i in range(1, len(orig)):
        for key in ("LEARNED_BONUS", "TIGHT_UM"):
            if (orig[i] or "").count(key) != (s6[i] or "").count(key):
                raise SystemExit("cell %d: %s references differ between ourvzl and t6stk3" % (i, key))
    for i in (2, 5, 9, 10):
        if orig[i] != s6[i]:
            raise SystemExit("cell %d of ourvzl is not t6stk3's byte for byte (linker plumbing)" % i)
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
    # re-read and report the diff vs the base, cell by cell; metadata identical apart from id/title
    _, built = cells_of(dest / "kernel.ipynb")
    changed = [i for i, (a, b) in enumerate(zip(orig, built)) if a != b]
    if len(built) != len(orig) or changed != [0]:
        raise SystemExit("re-read: cells changed vs v_ourvzl = %r (expected [0])" % changed)
    bm = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k for k in set(bm) | set(nm) if bm.get(k) != nm.get(k))
    if mdiff != ["id", "title"]:
        raise SystemExit("metadata differs from ourvzl's beyond id/title: %r" % mdiff)
    print("built", dest, "| base v_ourvzl (md5 %s) | TIGHT 6.0 -> 6.5 | BONUS 1.6 -> 2.5" % BASE_MD5)
    print("cells changed vs v_ourvzl:", changed, "(cell 0 only) | metadata diff:", mdiff,
          "| datasets", nm["dataset_sources"], "| machine", nm.get("machine_shape"))
    for x, y in line_diff(orig[0], built[0])[0]:
        print("  -", x)
        print("  +", y)
    print("linker delta == t6stk3 -> t65b25 cell-0 delta (4 lines, byte for byte): OK")
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
