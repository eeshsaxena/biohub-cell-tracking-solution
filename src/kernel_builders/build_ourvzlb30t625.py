#!/usr/bin/env python3
"""ourvzlb30t625 = ourvzlb25r70 (public 0.955, 56657610) with TWO cell-0 changes: learned bonus 2.5 -> 3.0 (exactly as
ourvzlb30: env '3.0' + marker ARM_STK3B learned_bonus=3.0) AND relink tight 6.5 -> 6.25 (exactly as ourvzlt625: env "6.25"
+ marker ARM_T625H tight_um=6.25), + its own ARM_XENV line. Cells 1..11 and metadata (apart from id/title) are
v_ourvzlb25r70's byte for byte.

Reuses scratch_kernels/ourvzl_envarm.py (constants + helpers). Checks (all hard stops): md5 pins of v_ourvzlb25r70,
v_ourvzlb30, v_ourvzlt625; every anchor exactly once in cell 0, each marker the line right after its env line; neither new
value already in the base; built cell 0 == v_ourvzlt625's cell 0 except the two bonus lines (== v_ourvzlb30's, same
index) and the XENV line, and == v_ourvzlb30's cell 0 except the two tight lines (== v_ourvzlt625's) and the XENV line;
cells changed vs base == [0]; cell-0 diff == exactly those 5 lines; exactly one ARM_XENV; no stale 6.5 / 2.5 values;
compile every cell; re-read == built; metadata == base's except id/title (V1284 head mounted, T4, GPU, no internet,
private).

usage: python scratch_kernels/build_ourvzlb30t625.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm import (BASE, BASE_MD5, BASE_XENV, BONUS_ENV, BONUS_MARK, ENVNAME, NL, SK, TIGHT_ENV,  # noqa: E402
                           TIGHT_MARK, XENV_FMT, cells_of, lines_of, md5)

TAG = "ourvzlb30t625"
REF_B30 = SK / "v_ourvzlb30"
REF_B30_MD5 = "656ea7e412afa2711f3650acb0e0566f"   # v_ourvzlb30/kernel.ipynb (visible GATE_PASS 09-29)
REF_T625 = SK / "v_ourvzlt625"
REF_T625_MD5 = "ee5264fec3a7af6abe741b5245764f85"  # v_ourvzlt625/kernel.ipynb (visible GATE_PASS 09-29)


def main():
    for p, m in ((BASE, BASE_MD5), (REF_B30, REF_B30_MD5), (REF_T625, REF_T625_MD5)):
        if md5(p / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (p.name, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, cb = cells_of(REF_B30 / "kernel.ipynb")
    _, ct = cells_of(REF_T625 / "kernel.ipynb")
    orig = list(cells)
    if len(cells) != 12 or any(c is None for c in cells) or len(cb) != 12 or len(ct) != 12:
        raise SystemExit("unexpected notebook shape (need 12 code cells)")
    if cb[1:] != cells[1:] or ct[1:] != cells[1:]:
        raise SystemExit("v_ourvzlb30 / v_ourvzlt625 cells 1..11 are not the base's")
    c0 = cells[0]
    ol = lines_of(c0)
    if ol[-1] != BASE_XENV or c0.count("ARM_XENV") != 1 or sum("ARM_XENV" in c for c in cells) != 1:
        raise SystemExit("ourvzlb25r70 cell 0 does not end with its one ARM_XENV line")
    t_env_old, t_mark_old = TIGHT_ENV % "6.5", TIGHT_MARK % ("T65H", "6.5")
    b_env_old, b_mark_old = BONUS_ENV % "2.5", BONUS_MARK % "2.5"
    for name, a in (("tight_env", t_env_old), ("tight_mark", t_mark_old), ("bonus_env", b_env_old),
                    ("bonus_mark", b_mark_old)):
        if c0.count(a) != 1 or sum(c.count(a) for c in cells) != 1:
            raise SystemExit("anchor %s matched %d times in cell 0" % (name, c0.count(a)))
    t_idx = [i for i, x in enumerate(ol) if x.startswith(t_env_old)]
    b_idx = [i for i, x in enumerate(ol) if x == b_env_old]
    if len(t_idx) != 1 or len(b_idx) != 1:
        raise SystemExit("tight/bonus env line not exactly once as a line")
    t_idx, b_idx = t_idx[0], b_idx[0]
    if ol[t_idx + 1] != t_mark_old or ol[b_idx + 1] != b_mark_old:
        raise SystemExit("tight/bonus marker is not the line right after its env assignment")
    t_env_new, t_mark_new = TIGHT_ENV % "6.25", TIGHT_MARK % ("T625H", "6.25")
    b_env_new, b_mark_new = BONUS_ENV % "3.0", BONUS_MARK % "3.0"
    xenv = XENV_FMT % (TAG, "6.25", "3.00", "", "")
    for bad in (t_env_new, "ARM_T625H", "tight_um=6.25", "TIGHT=6.25 ", b_env_new, "learned_bonus=3.0", "BONUS=3.00 ", TAG):
        if any(bad in c for c in cells):
            raise SystemExit("base unexpectedly carries %r" % bad)
    # ---- the edit
    nl = list(ol)
    nl[t_idx] = ol[t_idx].replace(t_env_old, t_env_new, 1)  # trailing t65h comment left alone (as ourvzlt625)
    nl[t_idx + 1] = t_mark_new
    nl[b_idx] = b_env_new
    nl[b_idx + 1] = b_mark_new
    nl[-1] = xenv
    exp = sorted([(ol[t_idx], nl[t_idx]), (t_mark_old, t_mark_new), (b_env_old, b_env_new), (b_mark_old, b_mark_new),
                  (BASE_XENV, xenv)])
    cells[0] = NL.join(nl) + NL
    # ---- cross-checks against the two single-change arms (their proven lines, verbatim, same positions)
    bl30, lt625 = lines_of(cb[0]), lines_of(ct[0])
    if len(bl30) != len(ol) or len(lt625) != len(ol):
        raise SystemExit("reference cell-0 line counts differ from the base's")
    for i, x in enumerate(nl):
        want_t = bl30[i] if i in (b_idx, b_idx + 1) else (xenv if i == len(nl) - 1 else lt625[i])
        want_b = lt625[i] if i in (t_idx, t_idx + 1) else (xenv if i == len(nl) - 1 else bl30[i])
        if x != want_t or x != want_b:
            raise SystemExit("cell-0 line %d differs from the ourvzlb30 + ourvzlt625 union: %r" % (i, x[:90]))
    if lt625[t_idx] != nl[t_idx] or lt625[t_idx + 1] != t_mark_new or bl30[b_idx] != b_env_new \
            or bl30[b_idx + 1] != b_mark_new:
        raise SystemExit("changed lines are not the reference arms' lines verbatim")
    # ---- checks on the built cells
    changed = [i for i, (a, b) in enumerate(zip(orig, cells)) if a != b]
    if changed != [0]:
        raise SystemExit("cells changed vs v_ourvzlb25r70 = %r (expected [0])" % changed)
    bl = lines_of(cells[0])
    if len(bl) != len(ol):
        raise SystemExit("cell 0 line count changed")
    diff = sorted((x, y) for x, y in zip(ol, bl) if x != y)
    if diff != exp:
        raise SystemExit("cell 0 diff is not exactly the expected 5 lines: %r" % diff)
    if sum(c.count("ARM_XENV") for c in cells) != 1 or cells[0].count(xenv) != 1:
        raise SystemExit("not exactly one ARM_XENV line in the build")
    for a in ('os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"', 'os.environ["BIOHUB_MOTION_RELINK_VELOCITY_WEIGHT"] = "0.25"',
              t_env_new, t_mark_new, b_env_new, b_mark_new):
        if cells[0].count(a) != 1:
            raise SystemExit("knob %r not exactly once in the built cell 0" % a)
    if any('RELINK_TIGHT_UM"] = "6.5"' in c or "ARM_T65H" in c or "tight_um=6.5" in c for c in cells):
        raise SystemExit("a stale 6.5 tight value survived")
    if any("LEARNED_BONUS\"] = '2.5'" in c or "learned_bonus=2.5" in c for c in cells):
        raise SystemExit("a stale 2.5 bonus value survived")
    for k in ("sr", "lf"):
        if any(ENVNAME[k] in c for i, c in enumerate(cells) if i != 2):
            raise SystemExit("%s env leaked into this arm" % k)
    if any("FLOWFIX" in c for c in cells):
        raise SystemExit("FLOWFIX leaked into this arm")
    for i, c in enumerate(cells):
        compile(c, "%s:cell%d" % (TAG, i), "exec")
    # ---- write
    k = 0
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["source"] = cells[k].splitlines(keepends=True)
            c["outputs"] = []
            c["execution_count"] = None
        k += 1
    dest = SK / ("v_" + TAG)
    dest.mkdir(parents=True, exist_ok=True)
    with open(dest / "kernel.ipynb", "w", encoding="utf-8") as fh:
        json.dump(nb, fh)
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + TAG
    meta["title"] = "biohub v " + TAG
    with open(dest / "kernel-metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    # ---- re-read and report
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read of the written notebook differs from the built cells")
    if [i for i, (a, b) in enumerate(zip(orig, built)) if a != b] != [0]:
        raise SystemExit("re-read: cells changed vs v_ourvzlb25r70 != [0]")
    bm = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k_ for k_ in set(bm) | set(nm) if bm.get(k_) != nm.get(k_))
    if mdiff != ["id", "title"]:
        raise SystemExit("metadata differs from ourvzlb25r70's beyond id/title: %r" % mdiff)
    if "anvithpothula/biohub-v1284-head-s075" not in nm["dataset_sources"] or nm.get("is_private") is not True \
            or nm.get("enable_internet") is not False or nm.get("enable_gpu") is not True \
            or nm.get("machine_shape") != "NvidiaTeslaT4":
        raise SystemExit("metadata: V1284 head not mounted / not private / internet on / no GPU / not T4")
    print("built", dest, "| base v_ourvzlb25r70 (md5 %s) | tight 6.5 -> 6.25 + bonus 2.5 -> 3.0" % BASE_MD5)
    print("cells changed vs v_ourvzlb25r70:", changed, "| metadata diff:", mdiff, "| datasets", nm["dataset_sources"],
          "| machine", nm.get("machine_shape"))
    for x, y in diff:
        print("  -", x)
        print("  +", y)
    print("cell 0 == v_ourvzlt625 (md5 %s) + v_ourvzlb30 (md5 %s) changed lines, verbatim" % (REF_T625_MD5, REF_B30_MD5))
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
