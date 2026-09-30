#!/usr/bin/env python3
"""t6r70 (our representative 0.954 body: t6stk3 + raw-ILP override at prob >= 0.70) with the sub-voxel 3x3x3 softmax
at temperature T (all axes), gain g, clip 0.4999, lcefr kept, rawlink kept.

usage: python scratch_kernels/build_t6r70T.py <tag> <T> <gain>

Same patch as scratch_kernels/build_t6svT.py (which builds on t6stk3), applied to v_t6r70. t6r70's cell 4 is t6stk3's
byte for byte (verified 09-26: md5 92e55d43 on both, _SV_HELPER identical), so the SV helper patched here is the one
t6svT15 ran. This script re-checks that: if t6r70's _SV_HELPER differs from t6stk3's, it stops.
Markers: ARM_XENV tag=<tag> SVTEMP=<T> GAIN=<g> LCEFR=kept (cell 0), ARM_SVTEMP T=<T> gain=<g> (cell 4), the unchanged
per-movie SV_ARM_HSG200 line (gain field prints <g>) and t6r70's own ARM_RAWLINK lines (cells 2/5, untouched).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6r70"
REF_BODY = SK / "v_t6stk3"
NL = chr(10)

SOFT_OLD = "    vals = vals - vals.max(1, keepdims=True)\n"
SOFT_NEW = "    vals = (vals - vals.max(1, keepdims=True)) / float(os.environ.get('BIOHUB_SUBVOXEL_TEMP', '1'))\n"
GAIN_OLD = "os.environ['BIOHUB_SUBVOXEL_GAIN_FIXED'] = '2.00'\n"
ENV_OLD = "os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"


def code_cells(path):
    nb = json.loads((path / "kernel.ipynb").read_text(encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def sv_helper(c4):
    hs = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    return c4[hs:c4.index('"""', hs)]


def main():
    tag, T, g = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    if not (0.5 <= T <= 4.0 and 0.5 <= g <= 4.0):
        raise SystemExit("T and gain out of range")
    nb, cells = code_cells(BASE)
    _, ref_cells = code_cells(REF_BODY)
    c4 = cells[4]
    if sv_helper(c4) != sv_helper(ref_cells[4]):
        raise SystemExit("STOP: t6r70's _SV_HELPER differs from t6stk3's; the t6svT patch is not validated on it")
    if c4 != ref_cells[4]:
        raise SystemExit("STOP: t6r70's cell 4 differs from t6stk3's; re-audit before patching")
    for a in (SOFT_OLD, GAIN_OLD, ENV_OLD):
        if c4.count(a) != 1:
            raise SystemExit("anchor %r matched %d times" % (a[:60], c4.count(a)))
    c4 = c4.replace(SOFT_OLD, SOFT_NEW, 1)
    c4 = c4.replace(GAIN_OLD, "os.environ['BIOHUB_SUBVOXEL_GAIN_FIXED'] = '%.2f'\n" % g, 1)
    c4 = c4.replace(ENV_OLD, ENV_OLD + "os.environ['BIOHUB_SUBVOXEL_TEMP'] = '%s'\n" % repr(T)
                    + "print('ARM_SVTEMP T=%s gain=%.2f (sub-voxel softmax temperature; clip 0.4999; lcefr kept)', flush=True)\n" % (repr(T), g), 1)
    cells[4] = c4
    cells[0] = cells[0].rstrip(NL) + NL + 'print("ARM_XENV tag=%s SVTEMP=%s GAIN=%.2f LCEFR=kept", flush=True)' % (tag, repr(T), g) + NL
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    helper = sv_helper(c4)
    compile(helper, "sv_helper", "exec")
    if "BIOHUB_SUBVOXEL_TEMP" not in helper:
        raise SystemExit("helper patch missing")
    if "BIOHUB_RAWLINK_MIN_PROB" not in cells[0] or "rawlink_override" not in cells[5]:
        raise SystemExit("rawlink component missing from the base")
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
    print("built", dest, "| base v_t6r70 | T", T, "| gain", g)


if __name__ == "__main__":
    main()
