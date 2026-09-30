#!/usr/bin/env python3
"""t65b25r70ff = t65b25r70 (team representative 0.954: t6stk3 body + relink tight 6.5 + learned bonus 2.5 + t6r70's
raw-ILP override "rawlink" at min_prob 0.70) + the IMGFLOW write-time repair, ported EXACTLY as build_t6r70ff.py
ported it onto the t6r70 body (the same rawlink body with the 6.0 / 1.6 linker).

usage: python scratch_kernels/build_t65b25r70ff.py [tag]        (default tag t65b25r70ff)

HOW: the in-kernel helper, the call block, the run_stats insertion and all four cell-5 anchors are IMPORTED from
build_t6r70ff.py (one helper, three bodies). v_t65b25r70's cell 5 is v_t6r70's byte for byte (build_t65b25r70.py
checks that), so the repair lands at the identical place: after the rawlink override (its ARM_RAWLINK print) and
before the writer loop, i.e. on the graph that is written. Cell 0: t65b25r70's ARM_XENV line is replaced by t6r70ff's
four FLOWFIX env lines (deadline clock, BIOHUB_FLOWFIX=1, DEADLINE_S 34200) + this arm's ARM_XENV line.
Checks (all hard stops): base md5 pins (v_t65b25r70, v_t6r70ff); every anchor exactly once; no FLOWFIX already in the
base; cells other than 0/5 byte-identical to t65b25r70; cell 5 minus the three insertions == t65b25r70's; cell 5 ==
v_t6r70ff's cell 5 byte for byte; cell 0 == v_t6r70ff's cell 0 with t65b25's four linker lines and this XENV;
compile every cell; metadata copied from v_t65b25r70 with only id/title changed.
Markers: ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1
DEADLINE_S=34200 (cell 0), ARM_FLOWFIX enabled=True ... (cell 5 definition), one ARM_FLOWFIX [<movie>] status=ok ...
line per movie after its ARM_RAWLINK line (cell 5 writer), run_stats columns flowfix_*.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_t6r70ff import (HELPER, CALL, C5_DEF_ANCHOR, C5_CALL_ANCHOR, C5_STATS_ANCHOR,  # noqa: E402
                           C5_RAWSTATS_ANCHOR, NL)
from build_t65b25r70 import SWAPS  # noqa: E402  (t6stk3 -> t65b25 linker lines)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65b25r70"
BASE_MD5 = "60722ec9a2f277733656ba6bf5b559af"  # v_t65b25r70/kernel.ipynb (submitted 56640601, public 0.954)
SIB = SK / "v_t6r70ff"
SIB_MD5 = "1f7ea2bb4c81f7562ccdf5a8d943f04b"  # v_t6r70ff/kernel.ipynb as built by build_t6r70ff.py
BASE_XENV = 'print("ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept", flush=True)'
SIB_XENV = 'print("ARM_XENV tag=t6r70ff FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200", flush=True)'
XENV_FMT = ('print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 '
            'ENDS=1 DEADLINE_S=34200", flush=True)')
FF_ENV = ["import time as _ff_time0",
          "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX deadline clock",
          "os.environ['BIOHUB_FLOWFIX'] = '1'",
          "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'"]
STATS_NEW = "                **rawlink_stats,\n                **flowfix_stats,\n            })\n"


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t65b25r70ff"
    for d, m in ((BASE, BASE_MD5), (SIB, SIB_MD5)):
        if md5(d / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (d.name, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, sib = cells_of(SIB / "kernel.ipynb")
    orig = list(cells)
    c0, c5 = cells[0], cells[5]
    for name, a in (("c5_def", C5_DEF_ANCHOR), ("c5_call", C5_CALL_ANCHOR), ("c5_stats", C5_STATS_ANCHOR),
                    ("c5_rawstats", C5_RAWSTATS_ANCHOR)):
        if c5.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c5.count(a)))
    for bad in ("ARM_FLOWFIX", "BIOHUB_FLOWFIX", "flow_repair", "flowfix_stats"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base already carries %s" % bad)
    if "BIOHUB_RAWLINK_MIN_PROB" not in c0 or c5.count("def rawlink_override(") != 1:
        raise SystemExit("rawlink component missing from the base")
    lines = c0.rstrip(NL).split(NL)
    if lines[-1] != BASE_XENV or c0.count("ARM_XENV") != 1:
        raise SystemExit("t65b25r70 cell 0 does not end with its one ARM_XENV line")
    for _, new in SWAPS:
        if lines.count(new) != 1:
            raise SystemExit("t65b25 linker line %r not exactly once in the base cell 0" % new[:60])
    xenv = XENV_FMT % tag
    # ---- the three cell-5 insertions, exactly as build_t6r70ff.py makes them
    c5 = c5.replace(C5_DEF_ANCHOR, C5_DEF_ANCHOR.replace("\ndef write_test_submission", HELPER + "\ndef write_test_submission"), 1)
    c5 = c5.replace(C5_CALL_ANCHOR, C5_CALL_ANCHOR.replace("\n\n            for node_id in sorted(nodes_by_id):\n",
                                                           "\n\n" + CALL + "\n            for node_id in sorted(nodes_by_id):\n"), 1)
    c5 = c5.replace(C5_STATS_ANCHOR, STATS_NEW, 1)
    # ---- cell 0: drop t65b25r70's XENV, append t6r70ff's FLOWFIX env lines + this arm's XENV
    c0 = NL.join(lines[:-1] + FF_ENV + [xenv]) + NL
    cells[0], cells[5] = c0, c5
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i not in (0, 5) and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    if c5.replace(HELPER, "").replace(CALL + "\n", "").replace("                **flowfix_stats,\n", "") != orig[5]:
        raise SystemExit("cell 5 differs from t65b25r70's by more than the three ARM_FLOWFIX insertions")
    for a in (HELPER, CALL, "**flowfix_stats,"):
        if c5.count(a) != 1:
            raise SystemExit("insertion %r not exactly once in built cell 5" % a[:50])
    if c5.index("def rawlink_override(") > c5.index("edges, flowfix_stats = flow_repair(") \
            or c5.index("rawlink_stats['rawlink_new_isolated']") > c5.index("edges, flowfix_stats = flow_repair("):
        raise SystemExit("the repair call is not after the rawlink override")
    if c5.count("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()") != 1:
        raise SystemExit("nbrun split anchor count changed")
    # ---- cross-check vs v_t6r70ff: cell 5 byte-identical; cell 0 = its cell 0 with the linker swaps + this XENV
    if len(sib) != len(cells):
        raise SystemExit("cell count differs from v_t6r70ff")
    if cells[5] != sib[5]:
        raise SystemExit("built cell 5 is not v_t6r70ff's cell 5 byte for byte")
    for i in range(len(cells)):
        if i not in (0,) and cells[i] != sib[i]:
            raise SystemExit("built cell %d differs from v_t6r70ff's (expected cell 0 only)" % i)
    sl = sib[0].rstrip(NL).split(NL)
    if sl[-1] != SIB_XENV or sl[-5:-1] != FF_ENV:
        raise SystemExit("v_t6r70ff cell 0 does not end with the FLOWFIX env lines + its XENV")
    exp = list(sl)
    for old, new in SWAPS:
        if exp.count(old) != 1:
            raise SystemExit("t6r70ff cell 0 lacks linker line %r" % old[:60])
        exp[exp.index(old)] = new
    exp[-1] = xenv
    if exp != c0.rstrip(NL).split(NL):
        raise SystemExit("built cell 0 != v_t6r70ff cell 0 with t65b25's 4 linker lines and this XENV")
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
    # ---- re-read the written notebook and report the diff vs the base
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read of the written notebook differs from the built cells")
    changed = [i for i, (a, b) in enumerate(zip(orig, built)) if a != b]
    if changed != [0, 5]:
        raise SystemExit("cells changed vs v_t65b25r70 = %r (expected [0, 5])" % changed)
    print("built", dest, "| base v_t65b25r70 (md5 %s) | IMGFLOW TF5 KEEP3.5 GATE4.5 MIN_DET5 ENDS1 after rawlink" % BASE_MD5)
    print("cells changed vs v_t65b25r70:", changed)
    print("  cell 0: -", BASE_XENV)
    for l in FF_ENV + [xenv]:
        print("          +", l)
    print("  cell 5: + ARM_FLOWFIX helper (%d lines) before write_test_submission" % HELPER.count(NL))
    print("          + call block after the ARM_RAWLINK per-movie print:")
    for l in CALL.rstrip(NL).split(NL):
        print("            ", l)
    print("          + **flowfix_stats in the run_stats row")
    print("cells vs v_t6r70ff (md5 %s): cell 5 identical, cell 0 = its + t65b25 linker swaps + this XENV" % SIB_MD5)
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
