#!/usr/bin/env python3
"""ourvzlsr = ourvzlb25r70 (public 0.955, 56657610) with ONE cell-0 change: short-track rescue armed: BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC 0.10 -> 0.0 (as build_t65b25r70sr.py).
Everything else is v_ourvzlb25r70 byte for byte (cells 1..11, metadata apart from id/title). All logic + checks live in
scratch_kernels/ourvzl_envarm.py (md5-pinned base, exact-once anchors, cell diff == cell 0 only, compile all cells).

usage: python scratch_kernels/build_ourvzlsr.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ourvzl_envarm import ARMS, build  # noqa: E402

TAG = "ourvzlsr"

if __name__ == "__main__":
    build(TAG, ARMS[TAG])
