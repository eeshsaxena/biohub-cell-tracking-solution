#!/usr/bin/env python3
"""ourvzlb25r70ff = ourvzlb25r70 (team top entry, public 0.955, 56657610: the PUBLIC V1284 coordinate head for y/x + our
sub-voxel z fed to the edge model, relink tight 6.5, learned bonus 2.5, raw-ILP override "rawlink" 0.70) + the IMGFLOW
write-time repair, ported EXACTLY as build_t65b25r70ff.py ported it onto t65b25r70 (which took it from build_t6r70ff.py).

usage: python scratch_kernels/build_ourvzlb25r70ff.py [tag]        (default tag ourvzlb25r70ff)

WHY IT IS THE SAME PORT: ourvzlb25r70 differs from t65b25r70 in cells 0 and 4 only; its cells 2 and 5 are t65b25r70's
byte for byte (checked below), so the repair helper / call / run_stats insertion land at the identical cell-5 places:
the helper before write_test_submission, the call block after the per-movie ARM_RAWLINK print and before the writer loop
(i.e. on the graph that is written), **flowfix_stats after **rawlink_stats. Cell 0: ourvzlb25r70's ARM_XENV line (its
last line) is replaced by t6r70ff's four FLOWFIX env lines + this arm's ARM_XENV line. Cell 4 (the V1284 + z-to-arr
predictor patches) is never touched and is checked byte for byte.
Checks (all hard stops): md5 pins (v_ourvzlb25r70, v_t65b25r70, v_t65b25r70ff); every cell-5 anchor exactly once; no
FLOWFIX already in the base; cells changed vs ourvzlb25r70 == [0, 5]; cell 5 minus the three insertions == the base's;
built cell 5 == v_t65b25r70ff's cell 5 byte for byte; built cell 0 == v_t65b25r70ff's cell 0 with only the XENV line
swapped; the ourvzlb25r70 -> ourvzlb25r70ff line delta == the t65b25r70 -> t65b25r70ff delta in cells 0/5 (XENV text
aside); stage order filter -> rawlink -> flowfix -> writer; exactly one ARM_XENV; compile every cell; metadata copied from
v_ourvzlb25r70 (same datasets incl. the V1284 head, T4, no internet) with only id/title changed.
Markers: ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1
DEADLINE_S=34200 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx (cell 0), ARM_FLOWFIX enabled=True ... (cell 5
definition), one ARM_FLOWFIX [<movie>] status=ok ... line per movie after its ARM_RAWLINK line, run_stats flowfix_*.
"""
import difflib
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_t6r70ff import (HELPER, CALL, C5_DEF_ANCHOR, C5_CALL_ANCHOR, C5_STATS_ANCHOR,  # noqa: E402
                           C5_RAWSTATS_ANCHOR, NL)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourvzlb25r70"
BASE_MD5 = "9019774943ccdb39ebffe553b74325f1"  # v_ourvzlb25r70/kernel.ipynb (pushed 09-28 20:24Z, submitted 56657610, 0.955)
T65 = SK / "v_t65b25r70"
T65_MD5 = "60722ec9a2f277733656ba6bf5b559af"  # v_t65b25r70/kernel.ipynb (submitted 56640601, public 0.954)
T65FF = SK / "v_t65b25r70ff"
T65FF_MD5 = "e58610d94202109c95096c6d96c2fc93"  # v_t65b25r70ff/kernel.ipynb (submitted 56659166)
V1284_CELL = 4
BASE_XENV = ('print("ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr '
             'V1284_AXES=yx", flush=True)')
T65_XENV = 'print("ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept", flush=True)'
T65FF_XENV = ('print("ARM_XENV tag=t65b25r70ff TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 '
              'MIN_DET=5 ENDS=1 DEADLINE_S=34200", flush=True)')
XENV_FMT = ('print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 '
            'ENDS=1 DEADLINE_S=34200 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx", flush=True)')
FF_ENV = ["import time as _ff_time0",
          "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX deadline clock",
          "os.environ['BIOHUB_FLOWFIX'] = '1'",
          "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'"]
STATS_NEW = "                **rawlink_stats,\n                **flowfix_stats,\n            })\n"
FF_STATS_LINE = "                **flowfix_stats,\n"
FF_CALL_LINE = "edges, flowfix_stats = flow_repair("


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def lines_of(c):
    return c.rstrip(NL).split(NL)


def line_delta(a, b):
    al, bl = a.split(NL), b.split(NL)
    return [(op, tuple(al[i1:i2]), tuple(bl[j1:j2]))
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, al, bl, autojunk=False).get_opcodes() if op != "equal"]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "ourvzlb25r70ff"
    for d, m in ((BASE, BASE_MD5), (T65, T65_MD5), (T65FF, T65FF_MD5)):
        if md5(d / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (d.name, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, t65 = cells_of(T65 / "kernel.ipynb")
    _, t65ff = cells_of(T65FF / "kernel.ipynb")
    orig = list(cells)
    if not (len(cells) == len(t65) == len(t65ff) == 12) or any(c is None for c in cells):
        raise SystemExit("unexpected notebook shape (need 12 code cells everywhere)")
    # ---- preconditions: the port assumption (cells 2/5 are t65b25r70's) and the reference port (t65b25r70ff)
    if [i for i, (a, b) in enumerate(zip(t65, cells)) if a != b] != [0, V1284_CELL]:
        raise SystemExit("ourvzlb25r70 differs from t65b25r70 outside cells [0, 4]")
    for i in (2, 5):
        if cells[i] != t65[i]:
            raise SystemExit("ourvzlb25r70 cell %d is not t65b25r70's byte for byte; the port assumption fails" % i)
    if [i for i, (a, b) in enumerate(zip(t65, t65ff)) if a != b] != [0, 5]:
        raise SystemExit("v_t65b25r70ff differs from v_t65b25r70 outside cells [0, 5]")
    c0, c5 = cells[0], cells[5]
    for name, a in (("c5_def", C5_DEF_ANCHOR), ("c5_call", C5_CALL_ANCHOR), ("c5_stats", C5_STATS_ANCHOR),
                    ("c5_rawstats", C5_RAWSTATS_ANCHOR)):
        if c5.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c5.count(a)))
    for bad in ("ARM_FLOWFIX", "BIOHUB_FLOWFIX", "flow_repair", "flowfix_stats", "_ff_"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base already carries %s" % bad)
    if c0.count('os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"') != 1 or c5.count("def rawlink_override(") != 1:
        raise SystemExit("rawlink component missing from the base")
    lines = lines_of(c0)
    if lines[-1] != BASE_XENV or c0.count("ARM_XENV") != 1 or sum("ARM_XENV" in c for c in cells) != 1:
        raise SystemExit("ourvzlb25r70 cell 0 does not end with its one ARM_XENV line")
    tl = lines_of(t65[0])
    if tl[-1] != T65_XENV or lines[:-1] != tl[:-1]:
        raise SystemExit("ourvzlb25r70 cell 0 is not t65b25r70's cell 0 with only the XENV line different")
    v1284_src = cells[V1284_CELL]
    for mk in ("V1284", "ARM_SV_Z_TO_ARR", "ARM_V1284_YX"):
        if mk not in v1284_src:
            raise SystemExit("ourvzlb25r70 cell 4 lacks %r: not the V1284 body" % mk)
    xenv = XENV_FMT % tag
    # ---- the three cell-5 insertions, exactly as build_t65b25r70ff.py (and build_t6r70ff.py) make them
    c5 = c5.replace(C5_DEF_ANCHOR, C5_DEF_ANCHOR.replace("\ndef write_test_submission", HELPER + "\ndef write_test_submission"), 1)
    c5 = c5.replace(C5_CALL_ANCHOR, C5_CALL_ANCHOR.replace("\n\n            for node_id in sorted(nodes_by_id):\n",
                                                           "\n\n" + CALL + "\n            for node_id in sorted(nodes_by_id):\n"), 1)
    c5 = c5.replace(C5_STATS_ANCHOR, STATS_NEW, 1)
    # ---- cell 0: drop ourvzlb25r70's XENV, append the four FLOWFIX env lines + this arm's XENV
    c0 = NL.join(lines[:-1] + FF_ENV + [xenv]) + NL
    cells[0], cells[5] = c0, c5
    # ---- checks on the built cells
    changed = [i for i, (a, b) in enumerate(zip(orig, cells)) if a != b]
    if changed != [0, 5]:
        raise SystemExit("cells changed vs v_ourvzlb25r70 = %r (expected [0, 5])" % changed)
    if cells[V1284_CELL] != v1284_src or cells[V1284_CELL] != orig[V1284_CELL]:
        raise SystemExit("cell 4 (V1284 predictor patches) changed")
    if c5.replace(HELPER, "").replace(CALL + "\n", "").replace(FF_STATS_LINE, "") != orig[5]:
        raise SystemExit("cell 5 differs from ourvzlb25r70's by more than the three ARM_FLOWFIX insertions")
    for a in (HELPER, CALL, FF_STATS_LINE, FF_CALL_LINE):
        if c5.count(a) != 1:
            raise SystemExit("insertion %r not exactly once in built cell 5" % a[:50])
    if cells[5] != t65ff[5]:
        raise SystemExit("built cell 5 is not v_t65b25r70ff's cell 5 byte for byte")
    fl = lines_of(t65ff[0])
    if fl[-1] != T65FF_XENV or fl[:-1] + [xenv] != lines_of(c0):
        raise SystemExit("built cell 0 != v_t65b25r70ff's cell 0 with only the XENV line swapped")
    if lines_of(c0) != lines[:-1] + FF_ENV + [xenv]:
        raise SystemExit("built cell 0 != base[:-1] + 4 FLOWFIX env lines + this XENV")
    for i in (0, 5):
        ours = line_delta(orig[i], cells[i])
        ref = line_delta(t65[i], t65ff[i])
        if i == 0:  # compare with the XENV texts mapped onto the reference arm's
            ours = [(op, tuple(T65_XENV if x == BASE_XENV else x for x in o),
                     tuple(T65FF_XENV if x == xenv else x for x in n)) for op, o, n in ours]
        if ours != ref:
            raise SystemExit("cell %d: ourvzlb25r70 -> %s delta != t65b25r70 -> t65b25r70ff delta:\n ours %r\n ref  %r"
                             % (i, tag, ours, ref))
    w = c5.index("def write_test_submission")
    order = [c5.index(s, w) for s in ("nodes_by_id, edges, filter_stats = filter_output_graph(",
                                      "edges, rawlink_stats, rawlink_actions = rawlink_override(",
                                      FF_CALL_LINE, "for node_id in sorted(nodes_by_id):")]
    if order != sorted(order):
        raise SystemExit("writer stage order is not filter -> rawlink -> flowfix -> write: %r" % order)
    if c5.index("rawlink_stats['rawlink_new_isolated']") > c5.index(FF_CALL_LINE):
        raise SystemExit("the repair call is not after the per-movie ARM_RAWLINK print")
    if c5.count("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()") != 1:
        raise SystemExit("nbrun split anchor count changed")
    if sum(c.count("ARM_XENV") for c in cells) != 1 or c0.count(xenv) != 1:
        raise SystemExit("not exactly one ARM_XENV line in the build")
    for need in FF_ENV + ['os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"  # rawlink',
                          "os.environ[\"BIOHUB_MOTION_RELINK_LEARNED_BONUS\"] = '2.5'",
                          'os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.5"']:
        if sum(1 for ln in lines_of(c0) if ln.startswith(need)) != 1:
            raise SystemExit("line %r not exactly once in the built cell 0" % need[:60])
    for i, c in enumerate(cells):
        compile(c, "%s:cell%d" % (tag, i), "exec")
    # ---- write
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
    # ---- re-read and report
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read of the written notebook differs from the built cells")
    changed = [i for i, (a, b) in enumerate(zip(orig, built)) if a != b]
    if changed != [0, 5]:
        raise SystemExit("cells changed vs v_ourvzlb25r70 = %r (expected [0, 5])" % changed)
    bm = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k_ for k_ in set(bm) | set(nm) if bm.get(k_) != nm.get(k_))
    if mdiff != ["id", "title"]:
        raise SystemExit("metadata differs from ourvzlb25r70's beyond id/title: %r" % mdiff)
    if "anvithpothula/biohub-v1284-head-s075" not in nm["dataset_sources"]:
        raise SystemExit("the V1284 head dataset is not mounted")
    print("built", dest, "| base v_ourvzlb25r70 (md5 %s) | IMGFLOW TF5 KEEP3.5 GATE4.5 MIN_DET5 ENDS1 after rawlink" % BASE_MD5)
    print("cells changed vs v_ourvzlb25r70:", changed, "| cell 4 (V1284) untouched: md5",
          hashlib.md5(built[V1284_CELL].encode("utf-8")).hexdigest(), "| metadata diff:", mdiff)
    print("  datasets", nm["dataset_sources"], "| machine", nm.get("machine_shape"), "| gpu", nm.get("enable_gpu"),
          "| internet", nm.get("enable_internet"))
    print("  cell 0: -", BASE_XENV)
    for l in FF_ENV + [xenv]:
        print("          +", l)
    print("  cell 5: + ARM_FLOWFIX helper (%d lines) before write_test_submission" % HELPER.count(NL))
    print("          + call block after the ARM_RAWLINK per-movie print (before the writer loop):")
    for l in CALL.rstrip(NL).split(NL):
        print("            ", l)
    print("          + **flowfix_stats in the run_stats row")
    print("cross-checks: cell 5 == v_t65b25r70ff cell 5 byte for byte; cell 0 == v_t65b25r70ff cell 0 with only the XENV "
          "line swapped; delta == t65b25r70 -> t65b25r70ff delta (XENV aside); writer order filter/rawlink/flowfix/write:",
          order)
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
