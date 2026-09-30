#!/usr/bin/env python3
"""Our 0.954 body with x138's V1284 learned coordinate head in place of our sub-voxel block.

usage: python scratch_kernels/build_ourv.py <tag> [--keep-subvoxel] [--deadline]

WHY. On the SAME x138 body, the only difference between these two public-board arms is
which coordinate refinement fills the slot:
    xsv  = x138 body + OUR sub-voxel soft-argmax   -> 0.951 (our board reading)
    xpub = x138 body + ITS V1284 learned head      -> 0.956 (its author's board reading;
                                                     our own reading of it is pending)
If that gap is real, V1284 is worth about five ticks more than our refinement on the body
where both were measured. Our refinement was worth +0.005 on OUR body (0.946 -> 0.951),
so V1284 is the one untested coordinate lever with a plausible path past 0.954.

The head is PUBLIC: anvithpothula/biohub-v1284-head-s075 (30 KB, CC0). Its patch also
replaces `_index_features` with a trilinear lookup, so the edge model reads features at the
refined float coordinates - which is exactly what our lcefr block did. So the lcefr block
goes too; keeping both would refine the same quantity twice.

Everything else in t6stk3 stays: velocity 0.25, learned bonus 1.6, TIGHT 6.0.
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

SV_START = "# ===== SUB-VOXEL SOFT-ARGMAX REFINEMENT (sweep0911 surviving lever #2) ====="
LC_START = "# ===== LINKER READS THE REFINED COORDINATES (arm lcefr) ====="
LC_END = "def list_test_stems() -> list[str]:"
V_START = "# --------------------------------- V1284 head, AFTER readmit's low-detection dump patch"
V_END = "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])"


def code_cells(path):
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1]
    keep_sv = "--keep-subvoxel" in sys.argv

    nb, cells = code_cells(BASE / "kernel.ipynb")
    _, xcells = code_cells(SRC_X)
    x4 = xcells[4]
    v_block = x4[x4.index(V_START): x4.index(V_END) + len(V_END)]
    # the comment above the block describes ordering against x138's low-detection dump, which
    # does not exist on our body; the patch itself anchors on the raw predictor lines
    v_block = v_block.replace(
        "\n_ps.write_text(_trial_source)\n",
        "\n_ps.write_text(_trial_source)\n",
    )

    c4 = cells[4]
    if keep_sv:
        # keep our sub-voxel block, drop only lcefr (V1284's trilinear index_features replaces it)
        i = c4.index(LC_START)
    else:
        i = c4.index(SV_START)
    j = c4.index(LC_END)
    c4 = c4[:i] + v_block + NL + NL + NL + c4[j:]
    if (SV_START in c4) != keep_sv:
        raise SystemExit("sub-voxel block presence wrong")
    if LC_START in c4:
        raise SystemExit("lcefr block still present")
    if c4.count(V_END) != 1:
        raise SystemExit("V1284 block not inserted exactly once")
    cells[4] = c4

    ident = ('print(' + Q + 'ARM_XENV tag=%s V1284_HEAD=mounted SUBVOXEL=%s' % (tag, "kept" if keep_sv else "removed")
             + Q + ', flush=True)')
    cells[0] = cells[0].rstrip(NL) + NL + ident + NL

    for i2, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i2), "exec")

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
    print("built", dest, "| subvoxel", "kept" if keep_sv else "removed")
    print("  datasets:", meta["dataset_sources"])


if __name__ == "__main__":
    main()
