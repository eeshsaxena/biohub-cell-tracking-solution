#!/usr/bin/env python3
"""Add a gate entry + plan for a t6svT arm (scratch_kernels/build_t6svT.py: SV softmax temperature T, gain g).

usage: python ops/add_svT_gate.py <tag> <T> <gain> "<plan description>"
After writing, the t6stk3 log must FAIL under the new tag (auto-checked; gate.py is backed up first).
"""
import ast
import json
import pathlib
import subprocess
import sys

BS = chr(92)
D = BS + BS
ROOT = pathlib.Path(__file__).resolve().parents[1]


def esc(s):
    return s.replace(".", D + ".")


def main():
    tag, T, g, desc = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    p = ROOT / "ops" / "gate.py"
    t = p.read_text(encoding="utf-8")
    if "'%s'" % tag in t:
        raise SystemExit("gate entry for %s already exists" % tag)
    anchor = "        't6dl': [\n"
    assert t.count(anchor) == 1
    gs = "%.2f" % g
    entry = (
        "        # --- %s: t6stk3 with the sub-voxel softmax at temperature %s, gain %s (build_t6svT.py).\n" % (tag, repr(T), gs) +
        "        '%s': [\n" % tag +
        "            'ARM_STK3V velocity_weight=0" + D + ".25',\n"
        "            'ARM_STK3B learned_bonus=1" + D + ".6',\n"
        "            'ARM_T60H tight_um=6" + D + ".0',\n"
        "            'ARM_XENV tag=" + tag + " SVTEMP=" + esc(repr(T)) + " GAIN=" + esc(gs) + " LCEFR=kept',\n"
        "            'ARM_SVTEMP T=" + esc(repr(T)) + " gain=" + esc(gs) + " ',\n"
        "            'SUBVOXEL patch applied to',\n"
        "            'SV_ARM_HSG200 nodes=" + D + "d+ mean_abs_off_vox=0" + D + "." + D + "d+ frac_clipped=0" + D + "." + D + "d+ gain=" + esc(gs) + "',\n"
        "            'ARM_LCEFR patch applied to',\n"
        "        ],\n"
    )
    t = t.replace(anchor, entry + anchor, 1)
    fa = 'forbid["t6dl"] = ['
    assert t.count(fa) == 1
    t = t.replace(fa, 'forbid["%s"] = [r"V1284", r"ARM_SV_ZONLY", r"ARM_SV_YXONLY", r"ARM_SV_AXES", r"ARM_SVZEST", r"SUBVOXEL anchor", '
                  'r"SUBVOXEL offset/coord length mismatch", r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_LCEFR NO-OP", '
                  'r"IndentationError", r"Traceback \\(most recent call last\\)"]\n' % tag + fa, 1)
    tol_anchor = '"ourvzl": 0.15'
    assert t.count(tol_anchor) == 1
    t = t.replace(tol_anchor, tol_anchor + ', "%s": 0.15' % tag, 1)
    bak = p.with_name("gate.py.bak_" + tag)
    bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    ast.parse(t)
    p.write_text(t, encoding="utf-8")
    json.dump([{"tag": tag, "desc": desc}], open(ROOT / "ops" / ("plan_%s.json" % tag), "w"), indent=1)
    neg = subprocess.run([sys.executable, str(p), str(next((ROOT / "data" / "out_t6stk3").glob("*.log"))), tag],
                         capture_output=True, text=True).stdout.strip().splitlines()[-1]
    print("gate entry + plan written for", tag, "| negative test (t6stk3 log):", neg[:90])
    if "GATE_FAIL" not in neg:
        bak_text = bak.read_text(encoding="utf-8")
        p.write_text(bak_text, encoding="utf-8")
        raise SystemExit("NEGATIVE TEST DID NOT FAIL - gate.py restored from " + str(bak))


if __name__ == "__main__":
    main()
