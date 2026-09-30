#!/usr/bin/env python3
r"""Gate entry for ourvzlsr (scratch_kernels/build_ourvzlsr.py) = ourvzlb25r70 (public 0.955) with ONE cell-0 env change.
All derivation, patching, self-tests and restore-on-failure live in ops/ourvzl_envarm_gate.py (SPEC['ourvzlsr']).
Run from the project root: python ops/add_ourvzlsr_gate.py      (dry run: ENVARM_GATE=<copy of gate.py> python ...)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm_gate import install  # noqa: E402

if __name__ == "__main__":
    install("ourvzlsr")
