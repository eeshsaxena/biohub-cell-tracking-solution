#!/usr/bin/env python3
"""t6stk3fl = t6stk3ff (t6stk3 body + IMGFLOW write-time repair) + FLOWLINK: the SAME image phase-correlation flow used
EARLIER, inside the cell-5 motion relink (wf18, pre-registered in scratchpad/wf18/PREREG.md, box ~/biohub/wf18/PREREG.md).

usage: python scratch_kernels/build_t6stk3fl.py [tag] [--no-ff]
       default tag t6stk3fl (FLOWLINK + IMGFLOW repair); --no-ff builds the attribution arm (FLOWLINK only,
       IMGFLOW repair off), default tag t6stk3fla.

FLOWLINK (only change vs t6stk3ff besides markers/stats): per movie the IMGFLOW flows F (8 windows per frame pair,
y/x 2x binned, 3-D phase correlation; `_ff_flows` verbatim) are computed ONCE before filter_output_graph. Inside
motion_relink_edges.assign_pass, a SOURCE node whose window (float voxel coords, `_ff_win_of` rule) has |f| >= 5 um
and >= 5 relink-input nodes is flow-compensated: anchor = p + f, predicted = anchor (no velocity term), admission
gate on |target - anchor| (tight 6.0 / relaxed 10.0 unchanged), cost = |target - predicted| + 0.05 |target - anchor|
- BONUS * prob. Unflagged sources run the production expression unchanged; the ILP / cell 4 is byte-identical;
nodes and coordinates are untouched; stored distance_um stays physical. The IMGFLOW repair (t6stk3fl only) then
runs verbatim on the final graph, re-using the same F (identical values; saves the second flow pass).
Guards: shape (64,256,256), shared 9.5 h deadline, any exception -> F=None -> production relink for that movie.
Markers: ARM_XENV tag=<tag> FLOWLINK=1 FLOWFIX=<0|1> ... (cell 0), ARM_FLOWLINK enabled=True ... (cell 5 def), one
ARM_FLOWLINK [<movie>] status=ok ... digest=<md5 of F> line per movie + flowlink_* run_stats columns.
The FLOWLINK text below (FL_COMMON + RELINK_PAIRS) is imported VERBATIM by the offline / LOEO harness
(scratchpad/wf18/fl_offline.py) so replay, LOEO and kernel run the same code.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_t6r70ff import HELPER, CALL, C5_DEF_ANCHOR, NL  # noqa: E402
from build_t6stk3ff import BASE, BASE_MD5, C5_CALL_ANCHOR, C5_STATS_ANCHOR, SK  # noqa: E402

# ---- shared FLOWLINK core (kernel AND offline harness) ------------------------------------------------------------
FL_COMMON = r'''
# ---- ARM_FLOWLINK core (scratch_kernels/build_t6stk3fl.py; wf18 PREREG) --------------------------------------------
from collections import defaultdict as _fl_dd

FLOWLINK_ENABLED = os.environ.get("BIOHUB_FLOWLINK", "0") == "1"
FLOWLINK_CFG = dict(TF=5.0, MIN_DET=5, MODE="flow")
_FL_CTX = {"dataset": None, "F": None, "nT": 0}


def _fl_win_of(p_vox):
    z, y, x = p_vox
    return (min(int(z // 32), 1), min(int(y // 128), 1), min(int(x // 128), 1))


def _fl_flag_map(nodes_by_id):
    """source node id -> flow f (um) for nodes in flagged windows: |F[(t, w)]| >= TF and >= MIN_DET relink-input nodes
    at frame t in window w (w from the node's float voxel coordinates)."""
    F = _FL_CTX.get("F")
    if not F:
        return {}
    cnt = _fl_dd(int)
    win = {}
    for nid, node in nodes_by_id.items():
        k = (int(node["t"]),) + _fl_win_of((float(node["z"]), float(node["y"]), float(node["x"])))
        win[nid] = k
        cnt[k] += 1
    flag = {}
    for nid, k in win.items():
        v = F.get(k)
        if v is None:
            continue
        f = np.asarray(v[0], dtype=np.float64)
        if np.linalg.norm(f) < FLOWLINK_CFG["TF"] or cnt[k] < FLOWLINK_CFG["MIN_DET"]:
            continue
        if FLOWLINK_CFG["MODE"] == "neg":
            f = -f
        elif FLOWLINK_CFG["MODE"] == "zero":
            f = np.zeros(3)
        flag[nid] = f
    return flag
# ---- end ARM_FLOWLINK core ----------------------------------------------------------------------------------------
'''

# exact (old, new) replacements inside motion_relink_edges (each old string must occur exactly once in cell 5 AND in
# loeo_harness/repair_prod.py's copy of the function)
RELINK_PAIRS = [
    ("    position_um = {node_id: _position_um(node) for node_id, node in nodes_by_id.items()}\n",
     "    position_um = {node_id: _position_um(node) for node_id, node in nodes_by_id.items()}\n"
     "    _fl_flag = _fl_flag_map(nodes_by_id) if FLOWLINK_ENABLED else {}  # ARM_FLOWLINK\n"
     "    stats[\"flowlink_flagged_sources\"] = len(_fl_flag)\n"),
    ("            source_pos = position_um[source_id]\n"
     "            prev_pos = predecessor_position_um.get(source_id)\n"
     "            if prev_pos is None:\n"
     "                predicted = source_pos\n"
     "            else:\n"
     "                predicted = source_pos + MOTION_RELINK_VELOCITY_WEIGHT * (source_pos - prev_pos)\n"
     "            for j, target_id in enumerate(target_ids):\n"
     "                target_pos = position_um[target_id]\n"
     "                raw = float(np.linalg.norm(target_pos - source_pos))\n"
     "                if raw > gate_um:\n"
     "                    continue\n"
     "                motion = float(np.linalg.norm(target_pos - predicted))\n"
     "                prob = learned_prob(source_id, target_id)\n"
     "                raw_dist[i, j] = raw\n"
     "                motion_dist[i, j] = motion\n"
     "                prob_matrix[i, j] = prob\n"
     "                cost[i, j] = motion + 0.05 * raw - MOTION_RELINK_LEARNED_BONUS * prob\n",
     "            source_pos = position_um[source_id]\n"
     "            prev_pos = predecessor_position_um.get(source_id)\n"
     "            _fl_f = _fl_flag.get(source_id)  # ARM_FLOWLINK: flagged high-motion window -> flow-compensated geometry\n"
     "            if _fl_f is not None:\n"
     "                _fl_anchor = source_pos + _fl_f\n"
     "                predicted = _fl_anchor\n"
     "            elif prev_pos is None:\n"
     "                predicted = source_pos\n"
     "            else:\n"
     "                predicted = source_pos + MOTION_RELINK_VELOCITY_WEIGHT * (source_pos - prev_pos)\n"
     "            for j, target_id in enumerate(target_ids):\n"
     "                target_pos = position_um[target_id]\n"
     "                raw = float(np.linalg.norm(target_pos - source_pos))\n"
     "                gate_d = raw if _fl_f is None else float(np.linalg.norm(target_pos - _fl_anchor))\n"
     "                if gate_d > gate_um:\n"
     "                    continue\n"
     "                motion = float(np.linalg.norm(target_pos - predicted))\n"
     "                prob = learned_prob(source_id, target_id)\n"
     "                raw_dist[i, j] = raw\n"
     "                motion_dist[i, j] = motion\n"
     "                prob_matrix[i, j] = prob\n"
     "                cost[i, j] = motion + 0.05 * gate_d - MOTION_RELINK_LEARNED_BONUS * prob\n"),
]

# kernel-only: flow computation before filter_output_graph (IMGFLOW estimator + guards), shared with the repair
FL_KERNEL = r'''
# ---- ARM_FLOWLINK kernel part: flows once per movie, before filter_output_graph ------------------------------------
import hashlib as _fl_hashlib


def _fl_digest(F):
    h = _fl_hashlib.md5()
    for k in sorted(F):
        h.update(repr(k).encode())
        h.update(np.asarray(F[k][0], dtype=np.float64).tobytes())
    return h.hexdigest()[:12]


def flowlink_prepare(dataset, nodes_by_id):
    """Sets _FL_CTX for this movie. On any guard / error F stays None (production relink)."""
    t_start = _ff_time.time()
    elapsed = t_start - _FF_T0
    _FL_CTX.update(dataset=dataset, F=None, nT=0)
    st = {"flowlink_status": "off", "flowlink_windows": 0, "flowlink_flagged_windows": 0, "flowlink_secs": 0.0}
    if elapsed > FLOWFIX_DEADLINE_S:
        st["flowlink_status"] = "skipped_deadline"
        print(f"ARM_FLOWLINK [{dataset}] SKIPPED deadline elapsed_h={elapsed / 3600:.2f}", flush=True)
        return st
    try:
        shp = tuple(np.asarray(read_test_frame(dataset, 0, {})).shape)
        if shp != (64, 256, 256):
            st["flowlink_status"] = "skipped_shape"
            print(f"ARM_FLOWLINK [{dataset}] SKIPPED shape={shp}", flush=True)
            return st
        nT = int(max(int(n["t"]) for n in nodes_by_id.values())) + 1
        F = _ff_flows(dataset, nT)
        _FL_CTX.update(F=F, nT=nT)
        st["flowlink_windows"] = len(F)
        st["flowlink_flagged_windows"] = sum(1 for v in F.values() if np.linalg.norm(v[0]) >= FLOWLINK_CFG["TF"])
        st["flowlink_secs"] = round(_ff_time.time() - t_start, 2)
        st["flowlink_status"] = "ok"
        print(f"ARM_FLOWLINK [{dataset}] status=ok windows={len(F)} flagged_windows={st['flowlink_flagged_windows']}"
              f" digest={_fl_digest(F)} secs={st['flowlink_secs']:.1f}", flush=True)
        return st
    except Exception as exc:  # never lose a movie to the flow
        _FL_CTX.update(F=None, nT=0)
        st["flowlink_status"] = "fallback_error"
        print(f"ARM_FLOWLINK [{dataset}] FALLBACK error={type(exc).__name__}: {str(exc)[:200]}", flush=True)
        return st


def _fl_shared_flows(dataset, nT):
    """IMGFLOW repair re-uses the relink's flows (same estimator, same frames) when they cover this movie."""
    F = _FL_CTX.get("F")
    if F is not None and _FL_CTX.get("dataset") == dataset and int(_FL_CTX.get("nT", 0)) >= int(nT):
        return F
    return _ff_flows(dataset, nT)


print(f"ARM_FLOWLINK enabled={FLOWLINK_ENABLED} TF={FLOWLINK_CFG['TF']} MIN_DET={FLOWLINK_CFG['MIN_DET']}"
      f" MODE={FLOWLINK_CFG['MODE']} gate=relink(tight {MOTION_RELINK_TIGHT_UM}, relaxed {MOTION_RELINK_RELAXED_UM})",
      flush=True)
# ---- end ARM_FLOWLINK kernel part ---------------------------------------------------------------------------------
'''

HELPER_FLOW_OLD = "        F = _ff_flows(dataset, nT)\n"
HELPER_FLOW_NEW = "        F = _fl_shared_flows(dataset, nT)  # ARM_FLOWLINK: re-use the relink's flows\n"
C5_PREP_OLD = ("            raw_node_count = len(nodes_by_id)\n"
               "            nodes_by_id, edges, filter_stats = filter_output_graph(")
C5_PREP_NEW = ("            raw_node_count = len(nodes_by_id)\n"
               "            flowlink_stats: dict[str, object] = {}\n"
               "            if FLOWLINK_ENABLED:\n"
               "                flowlink_stats = flowlink_prepare(dataset, nodes_by_id)  # ARM_FLOWLINK\n"
               "            nodes_by_id, edges, filter_stats = filter_output_graph(")
C5_POST_OLD = '                raise AssertionError(f"{dataset}: post-processing removed every node")\n'
C5_POST_NEW = ('                raise AssertionError(f"{dataset}: post-processing removed every node")\n'
               '            if FLOWLINK_ENABLED:\n'
               '                print(f"ARM_FLOWLINK [{dataset}] relink flagged_sources='
               '{filter_stats.get(\'flowlink_flagged_sources\', -1)}", flush=True)\n')
STATS_NEW = "                **filter_stats,\n                **flowfix_stats,\n                **flowlink_stats,\n            })\n"


def patch_relink(src):
    for old, new in RELINK_PAIRS:
        if src.count(old) != 1:
            raise SystemExit("relink anchor matched %d times: %r" % (src.count(old), old[:70]))
        src = src.replace(old, new, 1)
    return src


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_ff = "--no-ff" in sys.argv
    tag = args[0] if args else ("t6stk3fla" if no_ff else "t6stk3fl")
    ff = "0" if no_ff else "1"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t6stk3/kernel.ipynb changed since the box bit check (md5 mismatch)")
    nb = json.loads(raw.decode("utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    orig = list(cells)
    c0, c5 = cells[0], cells[5]
    for name, a in (("c5_def", C5_DEF_ANCHOR), ("c5_call", C5_CALL_ANCHOR), ("c5_stats", C5_STATS_ANCHOR),
                    ("c5_prep", C5_PREP_OLD), ("c5_post", C5_POST_OLD)):
        if c5.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c5.count(a)))
    if HELPER.count(HELPER_FLOW_OLD) != 1:
        raise SystemExit("helper flow anchor count %d" % HELPER.count(HELPER_FLOW_OLD))
    for bad in ("ARM_FLOWFIX", "ARM_FLOWLINK", "BIOHUB_FLOWFIX", "BIOHUB_FLOWLINK", "flow_repair", "rawlink_override",
                "BIOHUB_RAWLINK_MIN_PROB"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %s" % bad)
    helper = HELPER.replace(HELPER_FLOW_OLD, HELPER_FLOW_NEW, 1)
    block = helper + FL_COMMON + FL_KERNEL
    c5 = patch_relink(c5)
    c5 = c5.replace(C5_DEF_ANCHOR, C5_DEF_ANCHOR.replace("\ndef write_test_submission", block + "\ndef write_test_submission"), 1)
    c5 = c5.replace(C5_PREP_OLD, C5_PREP_NEW, 1)
    c5 = c5.replace(C5_CALL_ANCHOR, C5_CALL_ANCHOR.replace("\n\n            for node_id in sorted(nodes_by_id):\n",
                                                           "\n\n" + CALL + "\n            for node_id in sorted(nodes_by_id):\n"), 1)
    c5 = c5.replace(C5_POST_OLD, C5_POST_NEW, 1)
    c5 = c5.replace(C5_STATS_ANCHOR, STATS_NEW, 1)
    c0 = (c0.rstrip(NL) + NL
          + "import time as _ff_time0" + NL
          + "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX/FLOWLINK deadline clock" + NL
          + "os.environ['BIOHUB_FLOWFIX'] = '%s'" % ff + NL
          + "os.environ['BIOHUB_FLOWLINK'] = '1'" + NL
          + "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'" + NL
          + ('print("ARM_XENV tag=%s FLOWLINK=1 FL_TF=5.0 FL_MIN_DET=5 FLOWFIX=%s TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5'
             ' ENDS=1 DEADLINE_S=34200", flush=True)' % (tag, ff)) + NL)
    cells[0], cells[5] = c0, c5
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i not in (0, 5) and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    # reverse every insertion -> must give t6stk3's cell 5 back exactly
    rev = c5.replace(block, "").replace(CALL + "\n", "").replace(STATS_NEW, C5_STATS_ANCHOR)
    rev = rev.replace(C5_PREP_NEW, C5_PREP_OLD).replace(C5_POST_NEW, C5_POST_OLD)
    for old, new in RELINK_PAIRS:
        rev = rev.replace(new, old)
    if rev != orig[5]:
        raise SystemExit("cell 5 differs from t6stk3's by more than the ARM_FLOWFIX + ARM_FLOWLINK insertions")
    if c5.count("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()") != 1:
        raise SystemExit("nbrun split anchor count changed")
    if "import hashlib as _fl_hashlib" not in c5 or "hashlib.md5()" in c5.replace("_fl_hashlib.md5()", ""):
        raise SystemExit("cell 5 hashlib use not self-contained")
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
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
    print("built", dest, "| base v_t6stk3 (md5 %s) | FLOWLINK TF5 MIN_DET5 | IMGFLOW repair %s" % (
        BASE_MD5, "ON (TF5 KEEP3.5 GATE4.5 MIN_DET5 ENDS1)" if ff == "1" else "OFF"))
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
