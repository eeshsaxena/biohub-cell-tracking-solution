#!/usr/bin/env python3
"""Add a gate entry + plan for a t6svzest arm (built by scratch_kernels/build_t6svzest.py).

usage: python ops/add_svzest_gate.py <tag> <estimator> <gain> "<plan description>"

Markers required: the t6 linker stack (STK3V/STK3B/T60H), the arm identity from cell 0, the ARM_SVZEST line from
cell 4, the sub-voxel patch line and the lcefr patch line. Forbids V1284 and other arms' SV variants. Count tolerance
0.15. Refuses if the tag already has an entry. After writing, the t6stk3 log must FAIL under the new tag.
"""
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
    tag, est, gain, desc = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    g = repr(gain)
    p = ROOT / "ops" / "gate.py"
    t = p.read_text(encoding="utf-8")
    if "'%s'" % tag in t:
        raise SystemExit("gate entry for %s already exists" % tag)
    anchor = "        't6dl': [\n"
    assert t.count(anchor) == 1
    entry = (
        "        # --- %s: t6stk3 with the sub-voxel z offset from estimator %s x %s (build_t6svzest.py).\n" % (tag, est, g) +
        "        '%s': [\n" % tag +
        "            'ARM_STK3V velocity_weight=0" + D + ".25',\n"
        "            'ARM_STK3B learned_bonus=1" + D + ".6',\n"
        "            'ARM_T60H tight_um=6" + D + ".0',\n"
        "            'ARM_XENV tag=" + tag + " SVZEST=" + esc(est) + " ZGAIN=" + esc(g) + " LCEFR=kept',\n"
        "            'ARM_SVZEST est=" + esc(est) + " gain=" + esc(g) + " ',\n"
        "            'SUBVOXEL patch applied to',\n"
        "            'ARM_LCEFR patch applied to',\n"
        "        ],\n"
    )
    t = t.replace(anchor, entry + anchor, 1)
    fa = 'forbid["t6dl"] = ['
    assert t.count(fa) == 1
    t = t.replace(fa, 'forbid["%s"] = [r"V1284", r"ARM_SV_ZONLY", r"ARM_SV_YXONLY", r"ARM_SV_AXES", r"SUBVOXEL anchor", '
                  'r"SUBVOXEL offset/coord length mismatch", r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_LCEFR NO-OP", '
                  'r"SVZEST unknown estimator", r"IndentationError"]\n' % tag + fa, 1)
    tol_anchor = '"ourvzl": 0.15'
    assert t.count(tol_anchor) == 1
    t = t.replace(tol_anchor, tol_anchor + ', "%s": 0.15' % tag, 1)
    bak = p.with_name("gate.py.bak_" + tag)
    bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    p.write_text(t, encoding="utf-8")
    import ast
    ast.parse(t)
    json.dump([{"tag": tag, "desc": desc}], open(ROOT / "ops" / ("plan_%s.json" % tag), "w"), indent=1)
    neg = subprocess.run([sys.executable, str(p), str(next((ROOT / "data" / "out_t6stk3").glob("*.log"))), tag],
                         capture_output=True, text=True).stdout.strip().splitlines()[-1]
    print("gate entry + plan written for", tag, "| negative test (t6stk3 log):", neg[:90])
    if "GATE_FAIL" not in neg:
        raise SystemExit("NEGATIVE TEST DID NOT FAIL - restore " + str(bak))


if __name__ == "__main__":
    main()
