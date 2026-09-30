#!/usr/bin/env python3
"""ourvzlffb30 = ourvzlb25r70ff (ourvzlb25r70, public 0.955, + the IMGFLOW write-time repair; visible GATE_PASS) with ONE
cell-0 change: learned bonus 2.5 -> 3.0 (exactly as ourvzlb30: env '3.0' + marker ARM_STK3B learned_bonus=3.0), + its own
ARM_XENV line (= ourvzlb25r70ff's with tag=ourvzlffb30 and BONUS=3.00). Cells 1..11 (incl. the cell-5 FLOWFIX helper /
call / run_stats) and metadata (apart from id/title) are v_ourvzlb25r70ff's byte for byte.

Reuses scratch_kernels/ourvzl_envarm.py (constants + helpers). Checks (all hard stops): md5 pins of v_ourvzlb25r70ff and
v_ourvzlb30; every anchor exactly once in cell 0, the marker the line right after the env line; the new value not already
in the base; the two bonus lines == v_ourvzlb30's verbatim; cells changed vs ourvzlb25r70ff == [0]; cell-0 diff == exactly
the 3 lines; FLOWFIX env lines kept exactly once; exactly one ARM_XENV; no stale 2.5 bonus; compile every cell; re-read ==
built; metadata == ourvzlb25r70ff's except id/title (V1284 head mounted, T4, GPU, no internet, private).

usage: python scratch_kernels/build_ourvzlffb30.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm import BONUS_ENV, BONUS_MARK, ENVNAME, NL, SK, TIGHT_ENV, TIGHT_MARK, cells_of, lines_of, md5  # noqa: E402

TAG = "ourvzlffb30"
BASE = SK / "v_ourvzlb25r70ff"
BASE_MD5 = "968f58e8101fed7be1cca47c3e0d224d"   # v_ourvzlb25r70ff/kernel.ipynb (visible GATE_PASS 09-29)
REF_B30 = SK / "v_ourvzlb30"
REF_B30_MD5 = "656ea7e412afa2711f3650acb0e0566f"  # v_ourvzlb30/kernel.ipynb (visible GATE_PASS 09-29)
XENV_TMPL = ('print("ARM_XENV tag=%s TIGHT=6.5 BONUS=%s RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 '
             'ENDS=1 DEADLINE_S=34200 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx", flush=True)')
BASE_XENV = XENV_TMPL % ("ourvzlb25r70ff", "2.50")
FF_ENV = ["import time as _ff_time0",
          "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX deadline clock",
          "os.environ['BIOHUB_FLOWFIX'] = '1'",
          "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'"]


def main():
    for p, m in ((BASE, BASE_MD5), (REF_B30, REF_B30_MD5)):
        if md5(p / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (p.name, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, cb = cells_of(REF_B30 / "kernel.ipynb")
    orig = list(cells)
    if len(cells) != 12 or any(c is None for c in cells) or len(cb) != 12:
        raise SystemExit("unexpected notebook shape (need 12 code cells)")
    c0 = cells[0]
    ol = lines_of(c0)
    if ol[-1] != BASE_XENV or c0.count("ARM_XENV") != 1 or sum("ARM_XENV" in c for c in cells) != 1:
        raise SystemExit("ourvzlb25r70ff cell 0 does not end with its one ARM_XENV line")
    if ol[-5:-1] != FF_ENV or any(sum(c.count(x) for c in cells) != 1 for x in FF_ENV):
        raise SystemExit("ourvzlb25r70ff cell 0 does not carry the four FLOWFIX env lines exactly once before its XENV")
    if sum("flowfix_stats" in c for c in cells) < 1 or "def flow_repair" not in cells[5]:
        raise SystemExit("ourvzlb25r70ff cell 5 lacks the FLOWFIX repair")
    b_env_old, b_mark_old = BONUS_ENV % "2.5", BONUS_MARK % "2.5"
    t_env_old, t_mark_old = TIGHT_ENV % "6.5", TIGHT_MARK % ("T65H", "6.5")
    for name, a in (("bonus_env", b_env_old), ("bonus_mark", b_mark_old), ("tight_env", t_env_old),
                    ("tight_mark", t_mark_old)):
        if c0.count(a) != 1 or sum(c.count(a) for c in cells) != 1:
            raise SystemExit("anchor %s matched %d times in cell 0" % (name, c0.count(a)))
    b_idx = [i for i, x in enumerate(ol) if x == b_env_old]
    if len(b_idx) != 1 or ol[b_idx[0] + 1] != b_mark_old:
        raise SystemExit("bonus env line not exactly once / marker not right after it")
    b_idx = b_idx[0]
    b_env_new, b_mark_new = BONUS_ENV % "3.0", BONUS_MARK % "3.0"
    xenv = XENV_TMPL % (TAG, "3.00")
    for bad in (b_env_new, "learned_bonus=3.0", "BONUS=3.00 ", TAG):
        if any(bad in c for c in cells):
            raise SystemExit("base unexpectedly carries %r" % bad)
    # the two new lines are ourvzlb30's, verbatim, at the same index (cells 0 of ff and b30 share the prefix)
    bl30 = lines_of(cb[0])
    if bl30[b_idx] != b_env_new or bl30[b_idx + 1] != b_mark_new or bl30.count(b_env_new) != 1 \
            or bl30[:b_idx] != ol[:b_idx]:
        raise SystemExit("bonus env/marker lines are not v_ourvzlb30's verbatim at the same position")
    # ---- the edit
    nl = list(ol)
    nl[b_idx] = b_env_new
    nl[b_idx + 1] = b_mark_new
    nl[-1] = xenv
    exp = sorted([(b_env_old, b_env_new), (b_mark_old, b_mark_new), (BASE_XENV, xenv)])
    cells[0] = NL.join(nl) + NL
    # ---- checks on the built cells
    changed = [i for i, (a, b) in enumerate(zip(orig, cells)) if a != b]
    if changed != [0]:
        raise SystemExit("cells changed vs v_ourvzlb25r70ff = %r (expected [0])" % changed)
    bl = lines_of(cells[0])
    if len(bl) != len(ol):
        raise SystemExit("cell 0 line count changed")
    diff = sorted((x, y) for x, y in zip(ol, bl) if x != y)
    if diff != exp:
        raise SystemExit("cell 0 diff is not exactly the expected 3 lines: %r" % diff)
    # outside the ff-only lines, cell 0 == ourvzlb30's cell 0 (i.e. ourvzlb30 + FLOWFIX env + this XENV)
    if bl[:-5] != bl30[:-1]:
        raise SystemExit("built cell 0 (minus FLOWFIX env + XENV) != v_ourvzlb30's cell 0 (minus its XENV)")
    if sum(c.count("ARM_XENV") for c in cells) != 1 or cells[0].count(xenv) != 1:
        raise SystemExit("not exactly one ARM_XENV line in the build")
    for a in ['os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"', 'os.environ["BIOHUB_MOTION_RELINK_VELOCITY_WEIGHT"] = "0.25"',
              t_env_old, t_mark_old, b_env_new, b_mark_new] + FF_ENV:
        if cells[0].count(a) != 1:
            raise SystemExit("knob %r not exactly once in the built cell 0" % a)
    if any("LEARNED_BONUS\"] = '2.5'" in c or "learned_bonus=2.5" in c for c in cells):
        raise SystemExit("a stale 2.5 bonus value survived")
    for k in ("sr", "lf"):
        if any(ENVNAME[k] in c for i, c in enumerate(cells) if i != 2):
            raise SystemExit("%s env leaked into this arm" % k)
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
        raise SystemExit("re-read: cells changed vs v_ourvzlb25r70ff != [0]")
    bm = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k_ for k_ in set(bm) | set(nm) if bm.get(k_) != nm.get(k_))
    if mdiff != ["id", "title"]:
        raise SystemExit("metadata differs from ourvzlb25r70ff's beyond id/title: %r" % mdiff)
    if "anvithpothula/biohub-v1284-head-s075" not in nm["dataset_sources"] or nm.get("is_private") is not True \
            or nm.get("enable_internet") is not False or nm.get("enable_gpu") is not True \
            or nm.get("machine_shape") != "NvidiaTeslaT4":
        raise SystemExit("metadata: V1284 head not mounted / not private / internet on / no GPU / not T4")
    print("built", dest, "| base v_ourvzlb25r70ff (md5 %s) | bonus 2.5 -> 3.0" % BASE_MD5)
    print("cells changed vs v_ourvzlb25r70ff:", changed, "| metadata diff:", mdiff, "| datasets", nm["dataset_sources"],
          "| machine", nm.get("machine_shape"))
    for x, y in diff:
        print("  -", x)
        print("  +", y)
    print("bonus lines == v_ourvzlb30 (md5 %s) verbatim; cell 0 == ourvzlb30's + FLOWFIX env + XENV" % REF_B30_MD5)
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
