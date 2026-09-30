#!/usr/bin/env python3
"""Slot-free post-processing sweep: replay cell-5 on the box, score against real GT.

This is the loop the project has never had. The four scored test movies are
byte-identical train movies, so (a) their raw ILP geffs are cached on the box from the
real 0.954 run and (b) their ANNOTATION is in data/train, 2,127 dt==1 edges. So a
post-processing variant can be evaluated end to end without a Kaggle slot, and the
replay is the one already validated four times against real Kaggle output
(t6rlf_review/box_replay_t6rlf.py reproduces t6stk3 at J=0.95722 / 2036 TP exactly).

One process per movie, every config inside it, because the DeepCenter heatmaps are the
expensive part and they memoise across configs.

usage: box_sweep.py <dataset> <configs.json> <outdir>
  configs.json: {"label": {"BIOHUB_X": "1.5", ...}, ...}   "base" with {} is the control
"""
import contextlib
import csv
import io
import json
import os
import sys
import time
import types
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
THREADS = int(os.environ.get("RT_THREADS", "2"))
for _k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_k] = str(THREADS)
import numpy as np
import torch

torch.set_num_threads(THREADS)
assert not torch.cuda.is_available(), "GPU must not be used"

if "IPython" not in sys.modules:
    ip = types.ModuleType("IPython")
    ipd = types.ModuleType("IPython.display")
    ipd.display = lambda *a, **k: None
    ip.display = ipd
    sys.modules["IPython"] = ip
    sys.modules["IPython.display"] = ipd

HOME = Path.home() / "biohub"
NB = Path(os.environ.get("SWEEP_NB", str(HOME / "t6rlf_review" / "t6stk3.ipynb")))
GEFF = HOME / "t6rlf_review" / "geff"
TRAIN = HOME / "data" / "train"
CKPT = HOME / "deepcenter" / "weights" / "full_frame_center" / "best.pt"

DS = sys.argv[1]
CONFIGS = json.load(open(sys.argv[2]))
OUT = Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)

HM = {}


def load_ns(overrides):
    """cells 0,1,2 + cell-5 defs, with `overrides` applied AFTER cell 0 sets the defaults."""
    for k in [k for k in os.environ if k.startswith("BIOHUB_")]:
        del os.environ[k]
    nb = json.load(open(NB, encoding="utf-8"))
    src = lambda i: "".join(nb["cells"][i]["source"])
    g = {"__name__": "__box_sweep__"}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src(0), "<cell0>", "exec"), g)
        # cell 0 writes the defaults into os.environ; cell 2 reads them into constants,
        # so the override has to land in between or it is silently ignored.
        for k, v in overrides.items():
            os.environ[k] = str(v)
        # cell 1 is a drift guard that RAISES when a value it pins does not match, so an
        # override of a guarded key has to move the guard too. Without this, mtl4/mtl5/gap58/
        # gap65 all died with "Configuration drift detected" and the sweep silently lost them.
        c1 = src(1)
        for k, v in overrides.items():
            anchor = '    "%s": ' % k
            if anchor in c1:
                i0 = c1.index(anchor)
                j0 = c1.index(chr(10), i0)
                c1 = c1[:i0] + '    "%s": %s,' % (k, float(v)) + c1[j0:]
        exec(compile(c1, "<cell1>", "exec"), g)
        exec(compile(src(2), "<cell2>", "exec"), g)
    os.environ["BIOHUB_DEEPCENTER_CHECKPOINT"] = str(CKPT)
    c5 = src(5)
    cut = c5.index("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()")
    with contextlib.redirect_stdout(buf):
        exec(compile(c5[:cut], "<cell5-defs>", "exec"), g)
        bundle = g["load_deepcenter_veto_detector"]()
    g["TEST_DIR"] = TRAIN
    assert bundle is not None and str(bundle["device"]) == "cpu", bundle
    orig = g["deepcenter_heatmap_for_frame"]

    def memo(dataset, t, detector_bundle, frame_cache, heatmap_cache):
        key = (dataset, int(t))
        if key not in HM:
            HM[key] = orig(dataset, t, detector_bundle, frame_cache, {})
        return HM[key]

    g["deepcenter_heatmap_for_frame"] = memo
    return g, bundle


def load_raw(g):
    graph = g["graph_from_geff"](GEFF / (DS + ".geff"))
    nodes = {}
    for row in graph.node_attrs().iter_rows(named=True):
        nid = int(row["node_id"])
        nodes[nid] = {"node_id": nid, "t": int(row["t"]), "z": float(row["z"]),
                      "y": float(row["y"]), "x": float(row["x"])}
    raw = []
    for row in graph.edge_attrs().iter_rows(named=True):
        ep = row.get("edge_prob") if hasattr(row, "get") else None
        raw.append({"source_id": int(row["source_id"]), "target_id": int(row["target_id"]),
                    "edge_prob": None if ep is None else float(ep)})
    return nodes, raw


def write(label, nodes, edges):
    p = OUT / f"final_{label}_{DS}.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row_type", "node_id", "t", "z", "y", "x", "source_id", "target_id"])
        for nid in sorted(nodes):
            n = nodes[nid]
            w.writerow(["node", nid, int(n["t"]),
                        max(0, int(round(float(n["z"])))),
                        max(0, int(round(float(n["y"])))),
                        max(0, int(round(float(n["x"])))), -1, -1])
        for e in edges:
            w.writerow(["edge", -1, -1, -1, -1, -1, int(e["source_id"]), int(e["target_id"])])
    return p


def main():
    for label, ov in CONFIGS.items():
        t0 = time.time()
        try:
            g, bundle = load_ns(ov)
            nodes, raw = load_raw(g)
            out = g["filter_output_graph"](nodes, [dict(e) for e in raw],
                                           dataset=DS, deepcenter_bundle=bundle)
            n2, e2 = out[0], out[1]
            write(label, n2, e2)
            print(f"{DS} {label:22s} nodes={len(n2)} edges={len(e2)} {time.time()-t0:.0f}s", flush=True)
        except Exception as exc:
            print(f"{DS} {label:22s} FAILED {type(exc).__name__}: {exc}", flush=True)


if __name__ == "__main__":
    main()
