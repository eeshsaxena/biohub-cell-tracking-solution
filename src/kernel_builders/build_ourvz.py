#!/usr/bin/env python3
"""ourvz: V1284 head for y/x + our sub-voxel soft-argmax for z, on the t6stk3 linker stack.

usage: python scratch_kernels/build_ourvz.py <tag>

WHY. Per-axis centre error on the capture run's 31,875 detection/GT pairs (scratchpad/an/retrain_cross.py):
the public V1284 head leaves z UNCHANGED (44b6: .762 vs .754 zero; 6bba: .911 vs .887) and earns all of its
value in y/x (.536->.383, .548->.408). Our sub-voxel refinement moves z too, and the board reacted to z shifts
(z clip 1.0 lost 3 ticks). `ourv` replaced the whole sub-voxel block with V1284, so it gave up whatever the
z channel was worth. This arm keeps both, each on the axes it is good at.

Mechanics (all inside the predictor script that cell 4 patches):
  * sub-voxel offsets are computed per frame from the INTEGER peaks (before V1284 touches `arr`) and
    applied at the final assembly; env BIOHUB_SUBVOXEL_ZONLY=1 zeroes their y/x components;
  * V1284 refine() shifts `arr` per frame; its module is patched to zero the z component;
  * V1284's third anchor (`coords = coords.astype(np.int16)`) sits INSIDE our `if not _SV_ON:` branch, so its
    replacement is made a `pass` statement instead of a bare comment (an empty block would not compile);
  * lcefr is dropped exactly as in ourv (V1284's trilinear _index_features feeds float coords to the edge model).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
SRC_X = SK / "_pub0924" / "anvithpothula_biohub-x138" / "biohub-x138.ipynb"
Q = chr(34)
NL = chr(10)
BS = chr(92)
Q1 = BS + "'"
LN = BS + "n"

LC_START = "# ===== LINKER READS THE REFINED COORDINATES (arm lcefr) ====="
LC_END = "def list_test_stems() -> list[str]:"
V_START = "# --------------------------------- V1284 head, AFTER readmit's low-detection dump patch"
V_END = "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])"

# sub-voxel helper: zero y/x when BIOHUB_SUBVOXEL_ZONLY is set (helper lives inside a triple-quoted string)
SV_RET_OLD = "    sa = sa * _sv_gain()\n    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n"
SV_RET_NEW = ("    sa = sa * _sv_gain()\n"
              "    if os.environ.get('BIOHUB_SUBVOXEL_ZONLY', '0') != '0':\n"
              "        sa[:, 1:] = 0.0\n"
              "    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n")
SV_ENV_OLD = "os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"
SV_ENV_NEW = ("os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"
              "os.environ['BIOHUB_SUBVOXEL_ZONLY'] = '1'\n"
              "print('ARM_SV_ZONLY=1 (sub-voxel y/x offsets zeroed, z kept at gain 2.00 clip 0.4999)', flush=True)\n")
# V1284: the int16 anchor replacement must stay a valid statement inside our `if not _SV_ON:` branch
V_REPL_OLD = "'    # Preserve refined geometry through association and graph output.\\n'"
V_REPL_NEW = "'    pass  # Preserve refined geometry through association and graph output.\\n'"
# V1284 module (string literal, escaped): zero the z component of the head's shift
MOD_SHIFT_OLD = "    shift = bounded(head, (x-mean)/scale).cpu().numpy() / SPACING" + LN
MOD_SHIFT_NEW = ("    shift = bounded(head, (x-mean)/scale).cpu().numpy() / SPACING" + LN +
                 "    shift[:, 0] = 0.0  # V1284_YX: the head never helped z; z comes from the sub-voxel refinement" + LN)


def code_cells(path):
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1]
    nb, cells = code_cells(BASE / "kernel.ipynb")
    _, xcells = code_cells(SRC_X)
    x4 = xcells[4]
    v_block = x4[x4.index(V_START): x4.index(V_END) + len(V_END)]
    for a in (V_REPL_OLD, MOD_SHIFT_OLD):
        if v_block.count(a) != 1:
            raise SystemExit("V1284 block anchor %r matched %d" % (a[:50], v_block.count(a)))
    v_block = v_block.replace(V_REPL_OLD, V_REPL_NEW, 1).replace(MOD_SHIFT_OLD, MOD_SHIFT_NEW, 1)
    v_block += (NL + "_v1284yx_src = (_ps.parent/'v1284_coordinate_refinement.py').read_text()" + NL
                + "if _v1284yx_src.count('shift[:, 0] = 0.0') != 1: raise RuntimeError('V1284_YX module patch missing')" + NL
                + "print('ARM_V1284_YX module_patched=1', flush=True)")

    c4 = cells[4]
    for a in (SV_RET_OLD, SV_ENV_OLD, LC_START, LC_END):
        if c4.count(a) != 1:
            raise SystemExit("cell-4 anchor %r matched %d" % (a[:50], c4.count(a)))
    c4 = c4.replace(SV_RET_OLD, SV_RET_NEW, 1).replace(SV_ENV_OLD, SV_ENV_NEW, 1)
    i, j = c4.index(LC_START), c4.index(LC_END)
    c4 = c4[:i] + v_block + NL + NL + NL + c4[j:]
    if LC_START in c4 or c4.count(V_END) != 1 or "SV_ARM_HSG200" not in c4:
        raise SystemExit("assembly check failed")
    cells[4] = c4
    ident = 'print(' + Q + 'ARM_XENV tag=%s V1284_HEAD=mounted SUBVOXEL=z-only V1284_AXES=yx' % tag + Q + ', flush=True)'
    cells[0] = cells[0].rstrip(NL) + NL + ident + NL
    for k2, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, k2), "exec")
    # the module string and the sub-voxel helper string must both compile as written
    start = c4.index("write_text('") + len("write_text(")
    end = c4.index("')" + NL, start) + 1
    module_src = eval(c4[start:end])
    compile(module_src, "v1284_coordinate_refinement.py", "exec")
    if module_src.count("shift[:, 0] = 0.0") != 1:
        raise SystemExit("module z-zero patch missing")
    hs = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    helper = c4[hs:c4.index('"""', hs)]
    compile(helper, "sv_helper", "exec")
    if "BIOHUB_SUBVOXEL_ZONLY" not in helper:
        raise SystemExit("helper z-only patch missing")

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
    if "anvithpothula/biohub-v1284-head-s075" not in meta["dataset_sources"]:
        meta["dataset_sources"] = meta["dataset_sources"] + ["anvithpothula/biohub-v1284-head-s075"]
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest, "| datasets", meta["dataset_sources"])


if __name__ == "__main__":
    main()
