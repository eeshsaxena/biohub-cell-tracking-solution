#!/usr/bin/env python3
r"""Gate entry for ourvzlb35t625 (scratch_kernels/build_ourvzlb35t625.py). All derivation, patching, self-tests and restore-on-failure
live in ops/ourvzl_combo35_gate.py (on top of ops/ourvzl_combo_gate.py + ops/ourvzl_envarm_gate.py). Run from the project root,
SEQUENTIALLY:
python ops/add_ourvzlb35t625_gate.py      (dry run: ENVARM_GATE=<copy of gate.py> python ...)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_combo35_gate import install  # noqa: E402

if __name__ == "__main__":
    install("ourvzlb35t625")
