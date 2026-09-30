#!/usr/bin/env python3
"""ourvzlb35t625 = ourvzlb30t625 (= ourvzlb25r70, public 0.955, + tight 6.5 -> 6.25 + bonus 2.5 -> 3.0) with the learned
bonus 3.0 -> 3.5. Derived from v_ourvzlb30t625/kernel.ipynb (md5-pinned) with exactly three cell-0 line changes:
  os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = '3.0'   -> '3.5'
  print("ARM_STK3B learned_bonus=3.0", flush=True)            -> 3.5
  print("ARM_XENV tag=ourvzlb30t625 TIGHT=6.25 BONUS=3.00 ...") -> tag=ourvzlb35t625 ... BONUS=3.50
Tight stays 6.25 (env "6.25" + ARM_T625H marker), everything else identical.

Checks (all hard stops): md5 pins of v_ourvzlb30t625 and v_ourvzlb25r70; every anchor exactly once in cell 0 and in the
notebook, the bonus marker the line right after its env line, XENV the last cell-0 line; no new value already present;
cells 1..11 byte-identical to v_ourvzlb30t625 (and to v_ourvzlb25r70); cell-0 diff vs v_ourvzlb30t625 == exactly those 3
lines; cell-0 diff vs v_ourvzlb25r70 == exactly the 5 knob/XENV lines; exactly one ARM_XENV; no stale 3.0 / 2.5 bonus or
6.5 tight values; tight 6.25 / rawlink 0.70 / velocity 0.25 knobs exactly once; compile every cell; the written file is
the reference file's bytes with the three JSON-encoded lines swapped; re-read == built; metadata == v_ourvzlb30t625's
except id/title (V1284 head mounted, T4, GPU, no internet, private).

usage: python scratch_kernels/build_ourvzlb35t625.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm import (BASE, BASE_MD5, BASE_XENV, BONUS_ENV, BONUS_MARK, ENVNAME, NL, SK, TIGHT_ENV,  # noqa: E402
                           TIGHT_MARK, XENV_FMT, cells_of, lines_of, md5)

TAG = "ourvzlb35t625"
REF = SK / "v_ourvzlb30t625"
REF_MD5 = "b5da64062b99cbee6ac01fb341cb1402"  # v_ourvzlb30t625/kernel.ipynb (build_ourvzlb30t625.py, pushed 09-29)
REF_TAG = "ourvzlb30t625"


def main():
    for p, m in ((REF, REF_MD5), (BASE, BASE_MD5)):
        if md5(p / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (p.name, m))
    nb, cells = cells_of(REF / "kernel.ipynb")
    _, base_cells = cells_of(BASE / "kernel.ipynb")
    orig = list(cells)
    if len(cells) != 12 or any(c is None for c in cells) or len(base_cells) != 12:
        raise SystemExit("unexpected notebook shape (need 12 code cells)")
    if cells[1:] != base_cells[1:]:
        raise SystemExit("v_ourvzlb30t625 cells 1..11 are not v_ourvzlb25r70's")
    c0 = cells[0]
    ol = lines_of(c0)
    ref_xenv = XENV_FMT % (REF_TAG, "6.25", "3.00", "", "")
    if ol[-1] != ref_xenv or c0.count("ARM_XENV") != 1 or sum("ARM_XENV" in c for c in cells) != 1:
        raise SystemExit("ourvzlb30t625 cell 0 does not end with its one ARM_XENV line")
    b_env_old, b_mark_old = BONUS_ENV % "3.0", BONUS_MARK % "3.0"
    b_env_new, b_mark_new = BONUS_ENV % "3.5", BONUS_MARK % "3.5"
    t_env, t_mark = TIGHT_ENV % "6.25", TIGHT_MARK % ("T625H", "6.25")
    xenv = XENV_FMT % (TAG, "6.25", "3.50", "", "")
    for name, a in (("bonus_env", b_env_old), ("bonus_mark", b_mark_old), ("xenv", ref_xenv), ("tight_env", t_env),
                    ("tight_mark", t_mark)):
        if c0.count(a) != 1 or sum(c.count(a) for c in cells) != 1:
            raise SystemExit("anchor %s matched %d times in cell 0" % (name, c0.count(a)))
    b_idx = [i for i, x in enumerate(ol) if x == b_env_old]
    if len(b_idx) != 1:
        raise SystemExit("bonus env line not exactly once as a line")
    b_idx = b_idx[0]
    if ol[b_idx + 1] != b_mark_old:
        raise SystemExit("bonus marker is not the line right after its env assignment")
    for bad in (b_env_new, "learned_bonus=3.5", "BONUS=3.50 ", TAG):
        if any(bad in c for c in cells):
            raise SystemExit("reference unexpectedly carries %r" % bad)
    # ---- the edit
    nl = list(ol)
    nl[b_idx] = b_env_new
    nl[b_idx + 1] = b_mark_new
    nl[-1] = xenv
    exp = sorted([(b_env_old, b_env_new), (b_mark_old, b_mark_new), (ref_xenv, xenv)])
    cells[0] = NL.join(nl) + NL
    # ---- checks on the built cells
    changed = [i for i, (a, b) in enumerate(zip(orig, cells)) if a != b]
    if changed != [0]:
        raise SystemExit("cells changed vs v_ourvzlb30t625 = %r (expected [0])" % changed)
    if cells[1:] != orig[1:] or cells[1:] != base_cells[1:]:
        raise SystemExit("cells 1..11 not byte-identical to v_ourvzlb30t625 / v_ourvzlb25r70")
    bl = lines_of(cells[0])
    if len(bl) != len(ol):
        raise SystemExit("cell 0 line count changed")
    diff = sorted((x, y) for x, y in zip(ol, bl) if x != y)
    if diff != exp:
        raise SystemExit("cell 0 diff is not exactly the expected 3 lines: %r" % diff)
    # vs the public-0.955 base: exactly the tight env + marker, bonus env + marker and XENV lines
    basel = lines_of(base_cells[0])
    bdiff = sorted((x, y) for x, y in zip(basel, bl) if x != y)
    t_idx = [i for i, x in enumerate(bl) if x.startswith(t_env)]
    if len(basel) != len(bl) or len(t_idx) != 1 or bl[t_idx[0] + 1] != t_mark:
        raise SystemExit("tight env/marker not where expected vs v_ourvzlb25r70")
    t_idx = t_idx[0]
    bexp = sorted([(basel[t_idx], bl[t_idx]), (TIGHT_MARK % ("T65H", "6.5"), t_mark), (BONUS_ENV % "2.5", b_env_new),
                   (BONUS_MARK % "2.5", b_mark_new), (BASE_XENV, xenv)])
    if bdiff != bexp or basel[t_idx].replace(TIGHT_ENV % "6.5", t_env, 1) != bl[t_idx]:
        raise SystemExit("cell 0 diff vs v_ourvzlb25r70 is not exactly the 5 knob/XENV lines: %r" % bdiff)
    if sum(c.count("ARM_XENV") for c in cells) != 1 or cells[0].count(xenv) != 1:
        raise SystemExit("not exactly one ARM_XENV line in the build")
    for a in ('os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"', 'os.environ["BIOHUB_MOTION_RELINK_VELOCITY_WEIGHT"] = "0.25"',
              t_env, t_mark, b_env_new, b_mark_new):
        if cells[0].count(a) != 1:
            raise SystemExit("knob %r not exactly once in the built cell 0" % a)
    if any(ENVNAME["bonus"] in c for i, c in enumerate(cells) if i not in (0, 2)) \
            or sum(c.count(ENVNAME["bonus"]) for c in cells) != 2:
        raise SystemExit("bonus env name not exactly once in cell 0 + once in cell 2")
    for v in ("3.0", "2.5"):
        if any(("LEARNED_BONUS\"] = '%s'" % v) in c or ("learned_bonus=%s" % v) in c for c in cells):
            raise SystemExit("a stale %s bonus value survived" % v)
    if any("BONUS=3.00 " in c or "BONUS=2.50 " in c or REF_TAG in c for c in cells):
        raise SystemExit("a stale XENV bonus / tag survived")
    if any('RELINK_TIGHT_UM"] = "6.5"' in c or "ARM_T65H" in c or "tight_um=6.5" in c for c in cells):
        raise SystemExit("a stale 6.5 tight value survived")
    for k in ("sr", "lf"):
        if any(ENVNAME[k] in c for i, c in enumerate(cells) if i != 2):
            raise SystemExit("%s env leaked into this arm" % k)
    if any("FLOWFIX" in c for c in cells):
        raise SystemExit("FLOWFIX leaked into this arm")
    for i, c in enumerate(cells):
        compile(c, "%s:cell%d" % (TAG, i), "exec")
    # ---- write (only cell 0's source changes; everything else is the reference notebook as loaded)
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    if len(code) != 12 or any(c["outputs"] or c["execution_count"] is not None for c in code):
        raise SystemExit("reference notebook has outputs / execution counts")
    code[0]["source"] = cells[0].splitlines(keepends=True)
    dest = SK / ("v_" + TAG)
    dest.mkdir(parents=True, exist_ok=True)
    with open(dest / "kernel.ipynb", "w", encoding="utf-8") as fh:
        json.dump(nb, fh)
    meta = json.loads((REF / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + TAG
    meta["title"] = "biohub v " + TAG
    with open(dest / "kernel-metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    # ---- re-read and report
    raw_ref = (REF / "kernel.ipynb").read_bytes().decode("utf-8")
    for a, b in ((b_env_old, b_env_new), (b_mark_old, b_mark_new), (ref_xenv, xenv)):
        ja, jb = json.dumps(a + NL)[1:-1], json.dumps(b + NL)[1:-1]
        if raw_ref.count(ja) != 1:
            raise SystemExit("raw reference JSON does not carry %r exactly once" % a[:60])
        raw_ref = raw_ref.replace(ja, jb, 1)
    if (dest / "kernel.ipynb").read_bytes().decode("utf-8") != raw_ref:
        raise SystemExit("written notebook is not the reference bytes with the three lines swapped")
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read of the written notebook differs from the built cells")
    if [i for i, (a, b) in enumerate(zip(orig, built)) if a != b] != [0]:
        raise SystemExit("re-read: cells changed vs v_ourvzlb30t625 != [0]")
    rm = json.loads((REF / "kernel-metadata.json").read_text(encoding="utf-8"))
    bm = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k_ for k_ in set(rm) | set(nm) if rm.get(k_) != nm.get(k_))
    bdiffm = sorted(k_ for k_ in set(bm) | set(nm) if bm.get(k_) != nm.get(k_))
    if mdiff != ["id", "title"] or bdiffm != ["id", "title"]:
        raise SystemExit("metadata differs from ourvzlb30t625's / ourvzlb25r70's beyond id/title: %r %r" % (mdiff, bdiffm))
    if "anvithpothula/biohub-v1284-head-s075" not in nm["dataset_sources"] or nm.get("is_private") is not True \
            or nm.get("enable_internet") is not False or nm.get("enable_gpu") is not True \
            or nm.get("machine_shape") != "NvidiaTeslaT4" or nm["id"] != "eeshsaxena/biohub-v-" + TAG:
        raise SystemExit("metadata: V1284 head not mounted / not private / internet on / no GPU / not T4 / wrong id")
    print("built", dest, "| ref v_ourvzlb30t625 (md5 %s) | bonus 3.0 -> 3.5 (tight stays 6.25)" % REF_MD5)
    print("cells changed vs v_ourvzlb30t625:", changed, "| metadata diff:", mdiff, "| datasets", nm["dataset_sources"],
          "| machine", nm.get("machine_shape"))
    for x, y in diff:
        print("  -", x)
        print("  +", y)
    print("cell 0 vs v_ourvzlb25r70 (md5 %s): exactly the 5 tight/bonus/XENV lines; cells 1..11 identical" % BASE_MD5)
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
