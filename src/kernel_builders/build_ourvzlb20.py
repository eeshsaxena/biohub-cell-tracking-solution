#!/usr/bin/env python3
"""ourvzlb20 = ourvzlb25r70 (public 0.955, 56657610) with ONE cell-0 change: learned bonus 2.5 -> 2.0 (marker ARM_STK3B learned_bonus=2.0, as build_t65b20.py).
Everything else is v_ourvzlb25r70 byte for byte (cells 1..11, metadata apart from id/title). All logic + checks live in
scratch_kernels/ourvzl_envarm.py (md5-pinned base, exact-once anchors, cell diff == cell 0 only, compile all cells).

usage: python scratch_kernels/build_ourvzlb20.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm import ARMS, build  # noqa: E402

TAG = "ourvzlb20"

if __name__ == "__main__":
    build(TAG, ARMS[TAG])
