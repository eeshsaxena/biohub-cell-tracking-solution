#!/usr/bin/env python3
"""ourv with the V1284 displacement multiplied by a gain.

usage: python scratch_kernels/build_ourvg.py <tag> <gain>

WHY. V1284 is a small MLP regressor trained with a squared loss on 4,136 detection/GT pairs.
Regressors fitted that way shrink toward zero on data they did not see, and the board already
told us how much that matters for THIS quantity: our own sub-voxel soft-argmax, which has the
same kind of multiplicative shrinkage, scored 0.949 at gain 1.0, 0.951 at gain 2.0, 0.949 at 3.0.
V1284 at gain 1.0 is the `ourv` arm; this arm asks whether it is also under-shifting.

The head's output is bounded to 2 um by construction and the module raises if any shift
exceeds 2.00001 um, so the check is widened by exactly the gain and nothing else changes.
A runtime marker in the notebook proves the gain actually reached the predictor module.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourv"
NL = chr(10)

SHIFT_OLD = "shift = bounded(head, (x-mean)/scale).cpu().numpy() / SPACING"
SHIFT_NEW = ("shift = bounded(head, (x-mean)/scale).cpu().numpy() / SPACING"
             " * float(os.environ.get(\\'V1284_GAIN\\', \\'1.0\\'))")
CHECK_OLD = "> 2.00001:"
CHECK_NEW = "> 2.00001 * max(1.0, float(os.environ.get(\\'V1284_GAIN\\', \\'1.0\\'))):"
MODE_LINE = "os.environ['V1284_MODE']='candidate'"
OLD_IDENT = 'print("ARM_XENV tag=ourv V1284_HEAD=mounted SUBVOXEL=removed", flush=True)'
PATCHED = "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])"


def main():
    tag, gain = sys.argv[1], float(sys.argv[2])
    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]

    c4 = cells[4]
    for anchor in (SHIFT_OLD, CHECK_OLD, MODE_LINE, PATCHED):
        if c4.count(anchor) != 1:
            raise SystemExit("anchor %r matched %d times" % (anchor, c4.count(anchor)))
    c4 = c4.replace(SHIFT_OLD, SHIFT_NEW, 1)
    c4 = c4.replace(CHECK_OLD, CHECK_NEW, 1)
    c4 = c4.replace(MODE_LINE, MODE_LINE + NL + "os.environ['V1284_GAIN']='%s'" % repr(gain), 1)
    # prove, from the written module file itself, that the gain expression is in the code the
    # predictor imports - a print of the env var alone would pass even if the patch missed
    c4 = c4.replace(PATCHED, PATCHED + NL
                    + "_v1284_src = (_ps.parent/'v1284_coordinate_refinement.py').read_text()" + NL
                    + "if _v1284_src.count(\"V1284_GAIN\") != 2: raise RuntimeError('V1284 gain patch missing')" + NL
                    + "print('ARM_V1284_GAIN gain=%s module_patched=1' % os.environ['V1284_GAIN'], flush=True)", 1)
    cells[4] = c4

    c0 = cells[0]
    if c0.count(OLD_IDENT) != 1:
        raise SystemExit("identity line not found in cell 0")
    cells[0] = c0.replace(OLD_IDENT, 'print("ARM_XENV tag=%s V1284_HEAD=mounted SUBVOXEL=removed V1284_GAIN=%s", flush=True)'
                          % (tag, repr(gain)), 1)

    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    # the module source is a string literal inside cell 4: compile THAT too
    start = c4.index("write_text('") + len("write_text(")
    end = c4.index("')\n", start) + 1
    module_src = eval(c4[start:end])
    compile(module_src, "v1284_coordinate_refinement.py", "exec")
    if module_src.count("V1284_GAIN") != 2:
        raise SystemExit("module gain patch count wrong")

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
    print("built", dest, "| gain", gain)


if __name__ == "__main__":
    main()
