#!/usr/bin/env python3
"""ourvz with a multiplier on the sub-voxel z gain (V1284 for y/x, sub-voxel for z only).

usage: python scratch_kernels/build_ourvzg.py <tag> <zmult>

zmult multiplies the sub-voxel z offsets (gain 2.00) before the 0.4999 clip, so zmult 1.5 = effective z gain 3.0.
Built from v_ourvz; only the helper's z line and the identity/markers change. Use only if ourvz and t6svz15 both
say more z helps (t6svyx 0.948 showed the z channel is worth ~6 ticks on the t6 body).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourvz"
NL = chr(10)
ZONLY_OLD = "    if os.environ.get('BIOHUB_SUBVOXEL_ZONLY', '0') != '0':\n        sa[:, 1:] = 0.0\n"
ENV_OLD = "os.environ['BIOHUB_SUBVOXEL_ZONLY'] = '1'\n"
IDENT_OLD = 'print("ARM_XENV tag=ourvz V1284_HEAD=mounted SUBVOXEL=z-only V1284_AXES=yx", flush=True)'


def main():
    tag, zm = sys.argv[1], float(sys.argv[2])
    if not 0.0 < zm <= 2.0:
        raise SystemExit("zmult must be in (0, 2]")
    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    c4 = cells[4]
    for a in (ZONLY_OLD, ENV_OLD):
        if c4.count(a) != 1:
            raise SystemExit("anchor %r matched %d" % (a[:50], c4.count(a)))
    c4 = c4.replace(ZONLY_OLD, ZONLY_OLD + "        sa[:, 0] = sa[:, 0] * float(os.environ.get('BIOHUB_SUBVOXEL_ZGAIN_MULT', '1'))\n", 1)
    c4 = c4.replace(ENV_OLD, ENV_OLD + "os.environ['BIOHUB_SUBVOXEL_ZGAIN_MULT'] = '%s'\n" % repr(zm)
                    + "print('ARM_SV_ZGAIN_MULT=%s (effective z gain %.2f, clip 0.4999)', flush=True)\n" % (repr(zm), 2.0 * zm), 1)
    cells[4] = c4
    if cells[0].count(IDENT_OLD) != 1:
        raise SystemExit("identity not found")
    cells[0] = cells[0].replace(IDENT_OLD, 'print("ARM_XENV tag=%s V1284_HEAD=mounted SUBVOXEL=z-only V1284_AXES=yx ZGAIN_MULT=%s", flush=True)' % (tag, repr(zm)), 1)
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    hs = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    helper = c4[hs:c4.index('"""', hs)]
    compile(helper, "sv_helper", "exec")
    if "BIOHUB_SUBVOXEL_ZGAIN_MULT" not in helper:
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
    print("built", dest, "| z mult", zm)


if __name__ == "__main__":
    main()
