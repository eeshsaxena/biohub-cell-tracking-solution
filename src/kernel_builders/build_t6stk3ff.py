#!/usr/bin/env python3
"""t6stk3ff = t6stk3 (0.954 production body, no raw-ILP override) + IMGFLOW write-time repair.

usage: python scratch_kernels/build_t6stk3ff.py [tag]        (default tag t6stk3ff)

Same in-kernel helper as build_t6r70ff.py (imported from it, byte-identical: flowfix.py repair() verbatim, pre-registered
TF 5.0 / KEEP 3.5 / GATE 4.5 / MIN_DET 5 / ENDS on, 9.5 h deadline, invariant + exception fallbacks). On this body there
is no override, so the repair runs right after filter_output_graph (+ the empty-graph check), i.e. on exactly the graph
the offline test repaired (the written t6stk3 CSV of the box replays, 122 tuned + 54 held-out train movies).
Why this body and not t6r70: on the t6r70 body the offline gain vanishes on 6bba (76 movies: 6bba -0.03 tick) because
t6r70's raw-ILP override already fixes the same high-motion mislinks on TRAIN with memorised edge probabilities (+21 ticks
on the held-out 6bba replay vs t6stk3, a tie on the board). t6stk3 has no memorised override in the way, so it is the
clean board test of the mechanism: t6stk3ff vs t6stk3 (0.954).
Markers: ARM_XENV tag=<tag> FLOWFIX=1 ... (cell 0), ARM_FLOWFIX enabled=True ... (cell 5), one ARM_FLOWFIX [<movie>]
status=ok ... line per movie, run_stats columns flowfix_*. All other cells are t6stk3's byte for byte (checked below).
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_t6r70ff import HELPER, CALL, C5_DEF_ANCHOR, NL  # noqa: E402  (one helper, two bodies)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
BASE_MD5 = "643f4de949f707e161b118733e35e6df"  # v_t6stk3/kernel.ipynb (box wf13 nbs/t6stk3.ipynb replays)
C5_CALL_ANCHOR = ('                raise AssertionError(f"{dataset}: post-processing removed every node")\n\n'
                  "            for node_id in sorted(nodes_by_id):\n")
C5_STATS_ANCHOR = "                **filter_stats,\n            })\n"


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t6stk3ff"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t6stk3/kernel.ipynb changed since the box bit check (md5 mismatch)")
    nb = json.loads(raw.decode("utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    orig = list(cells)
    c0, c5 = cells[0], cells[5]
    for name, a in (("c5_def", C5_DEF_ANCHOR), ("c5_call", C5_CALL_ANCHOR), ("c5_stats", C5_STATS_ANCHOR)):
        if c5.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c5.count(a)))
    for bad in ("ARM_FLOWFIX", "BIOHUB_FLOWFIX", "flow_repair", "rawlink_override", "BIOHUB_RAWLINK_MIN_PROB"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %s" % bad)
    c5 = c5.replace(C5_DEF_ANCHOR, C5_DEF_ANCHOR.replace("\ndef write_test_submission", HELPER + "\ndef write_test_submission"), 1)
    c5 = c5.replace(C5_CALL_ANCHOR, C5_CALL_ANCHOR.replace("\n\n            for node_id in sorted(nodes_by_id):\n",
                                                           "\n\n" + CALL + "\n            for node_id in sorted(nodes_by_id):\n"), 1)
    c5 = c5.replace(C5_STATS_ANCHOR, "                **filter_stats,\n                **flowfix_stats,\n            })\n", 1)
    c0 = (c0.rstrip(NL) + NL
          + "import time as _ff_time0" + NL
          + "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX deadline clock" + NL
          + "os.environ['BIOHUB_FLOWFIX'] = '1'" + NL
          + "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'" + NL
          + 'print("ARM_XENV tag=%s FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200", flush=True)' % tag + NL)
    cells[0], cells[5] = c0, c5
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i not in (0, 5) and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    if c5.replace(HELPER, "").replace(CALL + "\n", "").replace("                **flowfix_stats,\n", "") != orig[5]:
        raise SystemExit("cell 5 differs from t6stk3's by more than the three ARM_FLOWFIX insertions")
    if c5.count("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()") != 1:
        raise SystemExit("nbrun split anchor count changed")
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
    json.dump(nb, open(dest / "kernel.ipynb", "w", encoding="utf-8"))
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest, "| base v_t6stk3 (md5 %s) | IMGFLOW TF5 KEEP3.5 GATE4.5 MIN_DET5 ENDS1" % BASE_MD5)
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
