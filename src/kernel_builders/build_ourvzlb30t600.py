#!/usr/bin/env python3
"""ourvzlb30t600 = ourvzlb30t625 (= ourvzlb25r70, public 0.955, + tight 6.5 -> 6.25 + bonus 2.5 -> 3.0) with ONLY the relink
tight gate 6.25 -> 6.0 (bonus stays 3.0, rawlink 0.70). Derived from v_ourvzlb30t625/kernel.ipynb (md5-pinned) with exactly
three cell-0 line changes:
  os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.25"  # <comment>  -> "6.0" (trailing comment kept)
  print("ARM_T625H tight_um=6.25", flush=True)                      -> print("ARM_T60H tight_um=6.0", flush=True)
  print("ARM_XENV tag=ourvzlb30t625 TIGHT=6.25 BONUS=3.00 ...")      -> tag=ourvzlb30t600 TIGHT=6.0 BONUS=3.00
The 6.0 env/marker pair is the one v_ourv carries (ARM_T60H tight_um=6.0), same TIGHT_MARK scheme as ourvzlt625.

Checks (hard stops): md5 pins of v_ourvzlb30t625 / v_ourvzlb25r70 / v_ourv; anchors exactly once; marker right after its env
line; XENV last; cells 1..11 byte-identical to v_ourvzlb30t625 (and v_ourvzlb25r70); cell-0 diff == exactly those 3 lines;
the new marker == v_ourv's verbatim; exactly one ARM_XENV; no stale 6.25 / 6.5 tight values; bonus 3.0 / rawlink 0.70 /
velocity 0.25 exactly once; compile every cell; written bytes == reference bytes with the 3 JSON lines swapped; re-read ==
built; metadata == v_ourvzlb30t625's except id/title.

usage: python scratch_kernels/build_ourvzlb30t600.py
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm import (BASE, BASE_MD5, BONUS_ENV, BONUS_MARK, ENVNAME, NL, SK, TIGHT_ENV,  # noqa: E402
                           TIGHT_MARK, XENV_FMT, cells_of, lines_of, md5)

TAG = "ourvzlb30t600"
REF = SK / "v_ourvzlb30t625"
REF_MD5 = "b5da64062b99cbee6ac01fb341cb1402"
REF_TAG = "ourvzlb30t625"
OURV = SK / "v_ourv"


def main():
    for p, m in ((REF, REF_MD5), (BASE, BASE_MD5)):
        if md5(p / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (p.name, m))
    ourv_md5 = md5(OURV / "kernel.ipynb")
    nb, cells = cells_of(REF / "kernel.ipynb")
    _, base_cells = cells_of(BASE / "kernel.ipynb")
    _, ourv_cells = cells_of(OURV / "kernel.ipynb")
    orig = list(cells)
    if len(cells) != 12 or any(c is None for c in cells) or cells[1:] != base_cells[1:]:
        raise SystemExit("unexpected notebook shape / v_ourvzlb30t625 cells 1..11 are not v_ourvzlb25r70's")
    c0 = cells[0]
    ol = lines_of(c0)
    ref_xenv = XENV_FMT % (REF_TAG, "6.25", "3.00", "", "")
    if ol[-1] != ref_xenv or c0.count("ARM_XENV") != 1 or sum("ARM_XENV" in c for c in cells) != 1:
        raise SystemExit("ourvzlb30t625 cell 0 does not end with its one ARM_XENV line")
    t_env_old, t_mark_old = TIGHT_ENV % "6.25", TIGHT_MARK % ("T625H", "6.25")
    t_env_new, t_mark_new = TIGHT_ENV % "6.0", TIGHT_MARK % ("T60H", "6.0")
    b_env, b_mark = BONUS_ENV % "3.0", BONUS_MARK % "3.0"
    xenv = XENV_FMT % (TAG, "6.0", "3.00", "", "")
    for name, a in (("tight_env", t_env_old), ("tight_mark", t_mark_old), ("xenv", ref_xenv), ("bonus_env", b_env),
                    ("bonus_mark", b_mark)):
        if c0.count(a) != 1 or sum(c.count(a) for c in cells) != 1:
            raise SystemExit("anchor %s matched %d times in cell 0" % (name, c0.count(a)))
    t_idx = [i for i, x in enumerate(ol) if x.startswith(t_env_old)]
    if len(t_idx) != 1 or ol[t_idx[0] + 1] != t_mark_old:
        raise SystemExit("tight env line not once / marker not the line right after it")
    t_idx = t_idx[0]
    if ourv_cells[0].count(t_mark_new) != 1:
        raise SystemExit("v_ourv does not carry %r exactly once (marker scheme check)" % t_mark_new)
    for bad in (t_env_new, "ARM_T60H", "tight_um=6.0", "TIGHT=6.0 ", TAG):
        if any(bad in c for c in cells):
            raise SystemExit("reference unexpectedly carries %r" % bad)
    # ---- the edit
    nl = list(ol)
    nl[t_idx] = ol[t_idx].replace(t_env_old, t_env_new, 1)  # trailing comment kept
    nl[t_idx + 1] = t_mark_new
    nl[-1] = xenv
    exp = sorted([(ol[t_idx], nl[t_idx]), (t_mark_old, t_mark_new), (ref_xenv, xenv)])
    if nl[t_idx][len(t_env_new):] != ol[t_idx][len(t_env_old):] or not nl[t_idx][len(t_env_new):].startswith("  #"):
        raise SystemExit("tight env trailing comment not preserved")
    cells[0] = NL.join(nl) + NL
    # ---- checks
    changed = [i for i, (a, b) in enumerate(zip(orig, cells)) if a != b]
    if changed != [0] or cells[1:] != base_cells[1:]:
        raise SystemExit("cells changed vs v_ourvzlb30t625 = %r (expected [0])" % changed)
    bl = lines_of(cells[0])
    diff = sorted((x, y) for x, y in zip(ol, bl) if x != y)
    if len(bl) != len(ol) or diff != exp:
        raise SystemExit("cell 0 diff is not exactly the expected 3 lines: %r" % diff)
    if sum(c.count("ARM_XENV") for c in cells) != 1 or cells[0].count(xenv) != 1:
        raise SystemExit("not exactly one ARM_XENV line in the build")
    for a in ('os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"', 'os.environ["BIOHUB_MOTION_RELINK_VELOCITY_WEIGHT"] = "0.25"',
              t_env_new, t_mark_new, b_env, b_mark):
        if cells[0].count(a) != 1:
            raise SystemExit("knob %r not exactly once in the built cell 0" % a)
    if any(ENVNAME["tight"] in c for i, c in enumerate(cells) if i not in (0, 2)) \
            or sum(c.count(ENVNAME["tight"]) for c in cells) != 2:
        raise SystemExit("tight env name not exactly once in cell 0 + once in cell 2")
    for v in ("6.25", "6.5", "6.75", "7.0"):
        if any(('RELINK_TIGHT_UM"] = "%s"' % v) in c or ("tight_um=%s" % v) in c or ("TIGHT=%s " % v) in c for c in cells):
            raise SystemExit("a stale %s tight value survived" % v)
    if any("ARM_T625H" in c or "ARM_T65H" in c or REF_TAG in c for c in cells):
        raise SystemExit("a stale tight marker / tag survived")
    if any("LEARNED_BONUS\"] = '2.5'" in c or "learned_bonus=2.5" in c for c in cells):
        raise SystemExit("a stale 2.5 bonus value survived")
    for k in ("sr", "lf"):
        if any(ENVNAME[k] in c for i, c in enumerate(cells) if i != 2):
            raise SystemExit("%s env leaked into this arm" % k)
    if any("FLOWFIX" in c for c in cells):
        raise SystemExit("FLOWFIX leaked into this arm")
    for i, c in enumerate(cells):
        compile(c, "%s:cell%d" % (TAG, i), "exec")
    # ---- write (only cell 0's source changes)
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
    for a, b in ((ol[t_idx], nl[t_idx]), (t_mark_old, t_mark_new), (ref_xenv, xenv)):
        ja, jb = json.dumps(a + NL)[1:-1], json.dumps(b + NL)[1:-1]
        if raw_ref.count(ja) != 1:
            raise SystemExit("raw reference JSON does not carry %r exactly once" % a[:60])
        raw_ref = raw_ref.replace(ja, jb, 1)
    if (dest / "kernel.ipynb").read_bytes().decode("utf-8") != raw_ref:
        raise SystemExit("written notebook is not the reference bytes with the three lines swapped")
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read of the written notebook differs from the built cells")
    rm = json.loads((REF / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k_ for k_ in set(rm) | set(nm) if rm.get(k_) != nm.get(k_))
    if mdiff != ["id", "title"]:
        raise SystemExit("metadata differs from ourvzlb30t625's beyond id/title: %r" % mdiff)
    if "anvithpothula/biohub-v1284-head-s075" not in nm["dataset_sources"] or nm.get("is_private") is not True \
            or nm.get("enable_internet") is not False or nm.get("enable_gpu") is not True \
            or nm.get("machine_shape") != "NvidiaTeslaT4" or nm["id"] != "eeshsaxena/biohub-v-" + TAG:
        raise SystemExit("metadata: V1284 head not mounted / not private / internet on / no GPU / not T4 / wrong id")
    print("built", dest, "| ref v_ourvzlb30t625 (md5 %s) | tight 6.25 -> 6.0 (bonus stays 3.0) | marker scheme = v_ourv (md5 %s)"
          % (REF_MD5, ourv_md5))
    print("cells changed vs v_ourvzlb30t625:", changed, "| metadata diff:", mdiff, "| machine", nm.get("machine_shape"))
    for x, y in diff:
        print("  -", x)
        print("  +", y)
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
