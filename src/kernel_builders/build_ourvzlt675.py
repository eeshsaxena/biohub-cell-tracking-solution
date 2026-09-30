#!/usr/bin/env python3
"""ourvzlt675 = ourvzlb25r70 (public 0.955, 56657610) with ONE cell-0 change: relink TIGHT 6.5 -> 6.75 (marker ARM_T675H tight_um=6.75, as build_t675b25.py on the t6 body).
Everything else is v_ourvzlb25r70 byte for byte (cells 1..11, metadata apart from id/title). All logic + checks live in
scratch_kernels/ourvzl_envarm.py (md5-pinned base, exact-once anchors, cell diff == cell 0 only, compile all cells).

usage: python scratch_kernels/build_ourvzlt675.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm import ARMS, build  # noqa: E402

TAG = "ourvzlt675"

if __name__ == "__main__":
    build(TAG, ARMS[TAG])
