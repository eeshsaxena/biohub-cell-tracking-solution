#!/usr/bin/env python3
"""t65s3ff = t65s3 (pick B, 0.954: t6stk3 + motion-relink TIGHT 6.0 -> 6.5) + IMGFLOW write-time repair.

usage: python scratch_kernels/build_t65s3ff.py [tag]        (default tag t65s3ff)

Same in-kernel helper as build_t6stk3ff.py / build_t6r70ff.py (imported from build_t6r70ff, byte-identical: flowfix.py
repair() verbatim, pre-registered TF 5.0 / KEEP 3.5 / GATE 4.5 / MIN_DET 5 / ENDS on, 9.5 h deadline, invariant +
exception fallbacks). t65s3 has no raw-ILP override, so (as on t6stk3) the repair runs right after filter_output_graph
(+ the empty-graph check), i.e. on exactly the graph the offline test repaired (the written t65s3 CSV of the box c5
replays, wf17 trackA). t65s3's cell 5 is t6stk3's byte for byte (its only difference is the TIGHT env line in cell 0),
so the t6stk3ff anchors are reused and each must match exactly once.
Markers: ARM_XENV tag=<tag> FLOWFIX=1 ... (cell 0), ARM_FLOWFIX enabled=True ... (cell 5), one ARM_FLOWFIX [<movie>]
status=ok ... line per movie, run_stats columns flowfix_*. All other cells are t65s3's byte for byte (checked below).
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_t6r70ff import HELPER, CALL, C5_DEF_ANCHOR, NL  # noqa: E402  (one helper, three bodies)
from build_t6stk3ff import C5_CALL_ANCHOR, C5_STATS_ANCHOR  # noqa: E402  (t65s3 cell 5 == t6stk3 cell 5)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65s3"
BASE_MD5 = "beb2e49d662e8bf6e39b201066d95f45"  # v_t65s3/kernel.ipynb (pick B 56496604; wf17 trackA replays)
T6STK3_MD5 = "643f4de949f707e161b118733e35e6df"  # v_t6stk3/kernel.ipynb


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t65s3ff"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t65s3/kernel.ipynb changed since the replay check (md5 mismatch)")
    if hashlib.md5((SK / "v_t6stk3" / "kernel.ipynb").read_bytes()).hexdigest() != T6STK3_MD5:
        raise SystemExit("STOP: v_t6stk3/kernel.ipynb changed (md5 mismatch)")
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, stk = cells_of(SK / "v_t6stk3" / "kernel.ipynb")
    # the body really is t6stk3 + TIGHT 6.5: cells 1..11 identical, cell 0 differs only in the TIGHT lines
    for i, (a, b) in enumerate(zip(stk, cells)):
        if i != 0 and a != b:
            raise SystemExit("t65s3 cell %d differs from t6stk3's: anchors not transferable" % i)
    d0 = [(x, y) for x, y in zip(stk[0].splitlines(), cells[0].splitlines()) if x != y]
    if len(stk[0].splitlines()) != len(cells[0].splitlines()) or len(d0) != 2 \
            or 'BIOHUB_MOTION_RELINK_TIGHT_UM"] = "6.5"' not in d0[0][1] or "ARM_T65H tight_um=6.5" not in d0[1][1]:
        raise SystemExit("t65s3 cell 0 is not t6stk3's + the TIGHT 6.5 lines: %r" % d0)
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
        raise SystemExit("cell 5 differs from t65s3's by more than the three ARM_FLOWFIX insertions")
    if not c0.startswith(orig[0].rstrip(NL)):
        raise SystemExit("cell 0 prefix changed")
    if c5.count("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()") != 1:
        raise SystemExit("nbrun split anchor count changed")
    # cross-check against the gated t6stk3ff build: cell 5 identical, cell 0 identical up to the TIGHT lines + tag
    ff = SK / "v_t6stk3ff" / "kernel.ipynb"
    if ff.exists():
        _, ffc = cells_of(ff)
        if ffc[5] != c5:
            raise SystemExit("cell 5 differs from v_t6stk3ff's cell 5 (the helper must be byte-identical)")
        if ffc[0].replace("tag=t6stk3ff ", "tag=%s " % tag).replace(stk[0].rstrip(NL), orig[0].rstrip(NL), 1) != c0:
            raise SystemExit("cell 0 differs from v_t6stk3ff's by more than the TIGHT lines and the tag")
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
    print("built", dest, "| base v_t65s3 (md5 %s) | IMGFLOW TF5 KEEP3.5 GATE4.5 MIN_DET5 ENDS1" % BASE_MD5)
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
