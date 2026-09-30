#!/usr/bin/env python3
"""ourvzllf100 = ourvzlb25r70 (public 0.955, 56657610) with ONE cell-0 change: output line-fit weight 0.8 -> 1.0 (BIOHUB_OUTPUT_LINEFIT_WEIGHT appended after the XENV line).
Everything else is v_ourvzlb25r70 byte for byte (cells 1..11, metadata apart from id/title). All logic + checks live in
scratch_kernels/ourvzl_envarm.py (md5-pinned base, exact-once anchors, cell diff == cell 0 only, compile all cells).

usage: python scratch_kernels/build_ourvzllf100.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm import ARMS, build  # noqa: E402

TAG = "ourvzllf100"

if __name__ == "__main__":
    build(TAG, ARMS[TAG])
