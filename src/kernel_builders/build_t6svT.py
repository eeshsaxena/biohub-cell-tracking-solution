#!/usr/bin/env python3
"""t6stk3 with the sub-voxel 3x3x3 softmax at temperature T (all axes), gain g, clip 0.4999, lcefr kept.

usage: python scratch_kernels/build_t6svT.py <tag> <T> <gain>

WHY (09-26 production-logit study, scratchpad/an/zstudy.py + v_logitcap): on the exact blended logits the production
SV helper reads, softening the softmax (T 1.25-1.5 at gain 2) cuts the GT-edge displacement tail on BOTH embryos
(44b6 0.0114 -> 0.0105, 6bba 0.0070 -> 0.0059; movie-bootstrap P(better) 0.85-0.86 / 0.96-1.00) and at the 2.5 and
3.5 um thresholds too. Size ~0.5 tick: a sub-resolution but consistent lottery ticket. The offsets are the production
formula with the logits divided by T before the softmax (identical to zstudy's sv27T); T=1 reproduces t6stk3.
Markers: ARM_XENV tag=<tag> SVTEMP=<T> GAIN=<g> LCEFR=kept (cell 0), ARM_SVTEMP T=<T> gain=<g> (cell 4),
and the unchanged per-movie SV_ARM_HSG200 line (whose gain field prints <g>).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
NL = chr(10)

SOFT_OLD = "    vals = vals - vals.max(1, keepdims=True)\n"
SOFT_NEW = "    vals = (vals - vals.max(1, keepdims=True)) / float(os.environ.get('BIOHUB_SUBVOXEL_TEMP', '1'))\n"
GAIN_OLD = "os.environ['BIOHUB_SUBVOXEL_GAIN_FIXED'] = '2.00'\n"
ENV_OLD = "os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"


def main():
    tag, T, g = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    if not (0.5 <= T <= 4.0 and 0.5 <= g <= 4.0):
        raise SystemExit("T and gain out of range")
    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    c4 = cells[4]
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
    hs = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    helper = c4[hs:c4.index('"""', hs)]
    compile(helper, "sv_helper", "exec")
    if "BIOHUB_SUBVOXEL_TEMP" not in helper:
        raise SystemExit("helper patch missing")
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
    print("built", dest, "| T", T, "| gain", g)


if __name__ == "__main__":
    main()
