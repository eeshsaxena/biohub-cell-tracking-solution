#!/usr/bin/env python3
"""t65s3fl = t65s3 (pick B, 0.954: t6stk3 + motion-relink TIGHT 6.0 -> 6.5) + FLOWLINK + IMGFLOW write-time repair
(wf21 track A; pre-registration scratchpad/wf21/A/PREREG.md, box ~/biohub/wf21/A/PREREG.md).

usage: python scratch_kernels/build_t65s3fl.py [tag] [--no-ff]
       default tag t65s3fl (FLOWLINK + IMGFLOW repair); --no-ff builds the attribution arm (FLOWLINK only,
       IMGFLOW repair off), default tag t65s3fla.

t65s3's cell 5 is t6stk3's byte for byte (its only difference is the TIGHT env line + ARM_T65H marker in cell 0), so
the t6stk3fl insertions (build_t6stk3fl.py: RELINK_PAIRS / FL_COMMON / FL_KERNEL / prep / post / stats, IMGFLOW helper
from build_t6r70ff) are applied VERBATIM, each anchor matching exactly once. FLOWLINK's gate is the relink's own
gate_um, i.e. t65s3's tight 6.5 / relaxed 10.0 (read from the env at cell 5 import). Result: cell 5 == v_t6stk3fl's
cell 5 byte for byte (checked when v_t6stk3fl exists), cell 0 == t65s3's cell 0 + the same FLOWLINK / FLOWFIX env
lines + ARM_XENV marker as t6stk3fl (tag differs). All other cells are t65s3's byte for byte (checked).
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_t6r70ff import HELPER, CALL, C5_DEF_ANCHOR, NL  # noqa: E402
from build_t6stk3ff import C5_CALL_ANCHOR, C5_STATS_ANCHOR  # noqa: E402
from build_t6stk3fl import (FL_COMMON, FL_KERNEL, RELINK_PAIRS, HELPER_FLOW_OLD, HELPER_FLOW_NEW,  # noqa: E402
                            C5_PREP_OLD, C5_PREP_NEW, C5_POST_OLD, C5_POST_NEW, STATS_NEW, patch_relink)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65s3"
BASE_MD5 = "beb2e49d662e8bf6e39b201066d95f45"  # v_t65s3/kernel.ipynb (pick B 56496604; wf17 trackA replays)
T6STK3_MD5 = "643f4de949f707e161b118733e35e6df"  # v_t6stk3/kernel.ipynb
T6STK3FL_MD5 = "5249259096ab6115089a176a51192459"  # v_t6stk3fl/kernel.ipynb (GATE_PASS visible run, 56601558)
T6STK3FLA_MD5 = "2bfd189e070320f41b4511a99f505448"  # v_t6stk3fla/kernel.ipynb (wf18 replays)


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_ff = "--no-ff" in sys.argv
    tag = args[0] if args else ("t65s3fla" if no_ff else "t65s3fl")
    ff = "0" if no_ff else "1"
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
    for name, a in (("c5_def", C5_DEF_ANCHOR), ("c5_call", C5_CALL_ANCHOR), ("c5_stats", C5_STATS_ANCHOR),
                    ("c5_prep", C5_PREP_OLD), ("c5_post", C5_POST_OLD)):
        if c5.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c5.count(a)))
    for old, _ in RELINK_PAIRS:
        if c5.count(old) != 1:
            raise SystemExit("relink anchor matched %d times: %r" % (c5.count(old), old[:70]))
    if HELPER.count(HELPER_FLOW_OLD) != 1:
        raise SystemExit("helper flow anchor count %d" % HELPER.count(HELPER_FLOW_OLD))
    for bad in ("ARM_FLOWFIX", "ARM_FLOWLINK", "BIOHUB_FLOWFIX", "BIOHUB_FLOWLINK", "flow_repair", "rawlink_override",
                "BIOHUB_RAWLINK_MIN_PROB"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %s" % bad)
    helper = HELPER.replace(HELPER_FLOW_OLD, HELPER_FLOW_NEW, 1)
    block = helper + FL_COMMON + FL_KERNEL
    c5 = patch_relink(c5)
    c5 = c5.replace(C5_DEF_ANCHOR, C5_DEF_ANCHOR.replace("\ndef write_test_submission", block + "\ndef write_test_submission"), 1)
    c5 = c5.replace(C5_PREP_OLD, C5_PREP_NEW, 1)
    c5 = c5.replace(C5_CALL_ANCHOR, C5_CALL_ANCHOR.replace("\n\n            for node_id in sorted(nodes_by_id):\n",
                                                           "\n\n" + CALL + "\n            for node_id in sorted(nodes_by_id):\n"), 1)
    c5 = c5.replace(C5_POST_OLD, C5_POST_NEW, 1)
    c5 = c5.replace(C5_STATS_ANCHOR, STATS_NEW, 1)
    c0 = (c0.rstrip(NL) + NL
          + "import time as _ff_time0" + NL
          + "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX/FLOWLINK deadline clock" + NL
          + "os.environ['BIOHUB_FLOWFIX'] = '%s'" % ff + NL
          + "os.environ['BIOHUB_FLOWLINK'] = '1'" + NL
          + "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'" + NL
          + ('print("ARM_XENV tag=%s FLOWLINK=1 FL_TF=5.0 FL_MIN_DET=5 FLOWFIX=%s TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5'
             ' ENDS=1 DEADLINE_S=34200", flush=True)' % (tag, ff)) + NL)
    cells[0], cells[5] = c0, c5
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i not in (0, 5) and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    # reverse every insertion -> must give t65s3's cell 5 back exactly
    rev = c5.replace(block, "").replace(CALL + "\n", "").replace(STATS_NEW, C5_STATS_ANCHOR)
    rev = rev.replace(C5_PREP_NEW, C5_PREP_OLD).replace(C5_POST_NEW, C5_POST_OLD)
    for old, new in RELINK_PAIRS:
        rev = rev.replace(new, old)
    if rev != orig[5]:
        raise SystemExit("cell 5 differs from t65s3's by more than the ARM_FLOWFIX + ARM_FLOWLINK insertions")
    if not c0.startswith(orig[0].rstrip(NL)):
        raise SystemExit("cell 0 prefix changed")
    if c5.count("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()") != 1:
        raise SystemExit("nbrun split anchor count changed")
    if "import hashlib as _fl_hashlib" not in c5 or "hashlib.md5()" in c5.replace("_fl_hashlib.md5()", ""):
        raise SystemExit("cell 5 hashlib use not self-contained")
    # cross-check against the gated t6stk3fl / replayed t6stk3fla builds: cell 5 identical, cell 0 identical up to the
    # TIGHT lines + tag
    ref_tag, ref_md5 = ("t6stk3fla", T6STK3FLA_MD5) if no_ff else ("t6stk3fl", T6STK3FL_MD5)
    ref = SK / ("v_" + ref_tag) / "kernel.ipynb"
    if ref.exists():
        if hashlib.md5(ref.read_bytes()).hexdigest() != ref_md5:
            raise SystemExit("STOP: v_%s/kernel.ipynb changed (md5 mismatch)" % ref_tag)
        _, rc = cells_of(ref)
        if rc[5] != c5:
            raise SystemExit("cell 5 differs from v_%s's cell 5" % ref_tag)
        if rc[0].replace("tag=%s " % ref_tag, "tag=%s " % tag).replace(stk[0].rstrip(NL), orig[0].rstrip(NL), 1) != c0:
            raise SystemExit("cell 0 differs from v_%s's by more than the TIGHT lines and the tag" % ref_tag)
        for i, (a, b) in enumerate(zip(rc, cells)):
            if i not in (0,) and a != b:
                raise SystemExit("cell %d differs from v_%s's" % (i, ref_tag))
        print("cross-check OK: cells 1..%d == v_%s, cell 0 == v_%s's up to the TIGHT 6.5 lines + tag"
              % (len(cells) - 1, ref_tag, ref_tag))
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
    print("built", dest, "| base v_t65s3 (md5 %s) | FLOWLINK TF5 MIN_DET5 (relink tight 6.5) | IMGFLOW repair %s" % (
        BASE_MD5, "ON (TF5 KEEP3.5 GATE4.5 MIN_DET5 ENDS1)" if ff == "1" else "OFF"))
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
