

# ===== RERUN DEADLINE GUARD =============================================================
# WHY THIS EXISTS. The competition's data description says it plainly: "test/ - Example test
# samples (copies from train) ... When a notebook is submitted for rerun, a new hidden test set
# is swapped in. The size of the hidden test set is approximately the same size as the training
# dataset." The training set is 199 movies. Our visible run does FOUR movies with 9 minutes of
# prediction, so the rerun is roughly fifty times that against a 12-hour ceiling, and our own
# body has never carried any wall-clock protection. A timeout on the final submission scores
# nothing at all, which is worse than any tick we could win.
#
# Two protections, both no-ops on a run that finishes comfortably:
#   1. after REPAIR_DEADLINE_S of wall clock, the remaining datasets are written with edge
#      filtering and short-track filtering only - a valid, if plainer, submission;
#   2. a dataset whose post-processing RAISES is written from its ILP graph instead of killing
#      the whole kernel.
# Plus a bound on the frame cache, which is memory-only and cannot change the output.
import time as _time
import traceback as _traceback

KERNEL_START_TS = float(os.environ.get("BIOHUB_KERNEL_START_TS", str(_time.time())))
REPAIR_DEADLINE_S = float(os.environ.get("BIOHUB_REPAIR_DEADLINE_S", "28800"))
FRAME_CACHE_MAX_FRAMES = int(os.environ.get("BIOHUB_FRAME_CACHE_MAX_FRAMES", "48"))
_deadline_degraded = False


def _frame_cache_trim(frame_cache):
    while len(frame_cache) > max(1, FRAME_CACHE_MAX_FRAMES):
        frame_cache.pop(next(iter(frame_cache)))


def _deadline_degrade():
    global _deadline_degraded, OUTPUT_MOTION_RELINK, OUTPUT_GAP_CLOSE, OUTPUT_GAP2_RECOVERY
    global OUTPUT_SAFE_DIVISIONS, OUTPUT_LINEFIT_SMOOTH
    _deadline_degraded = True
    OUTPUT_MOTION_RELINK = False
    OUTPUT_GAP_CLOSE = False
    OUTPUT_GAP2_RECOVERY = False
    OUTPUT_SAFE_DIVISIONS = False
    OUTPUT_LINEFIT_SMOOTH = False
    print(
        f"DEADLINE: {_time.time() - KERNEL_START_TS:.0f}s since kernel start exceeds"
        f" {REPAIR_DEADLINE_S:.0f}s; remaining datasets get edge filtering and"
        " short-track filtering only",
        flush=True,
    )


def fallback_output_graph(nodes_by_id, raw_edges):
    """Cheapest valid graph from the ILP output: consecutive-frame edges within
    OUTPUT_EDGE_MAX_UM, one parent per node, at most two children per node."""
    stats = {"raw_edges": len(raw_edges), "repair_fallback": 1}
    edges = []
    for edge in raw_edges:
        source = nodes_by_id.get(int(edge["source_id"]))
        target = nodes_by_id.get(int(edge["target_id"]))
        if source is None or target is None:
            continue
        if int(target["t"]) != int(source["t"]) + 1:
            continue
        edge["distance_um"] = edge_distance_um(source, target)
        if OUTPUT_EDGE_MAX_UM > 0 and float(edge["distance_um"]) > OUTPUT_EDGE_MAX_UM:
            continue
        edges.append(edge)
    best_by_target = {}
    for edge in edges:
        target_id = int(edge["target_id"])
        prev = best_by_target.get(target_id)
        if prev is None or edge_sort_key(edge) > edge_sort_key(prev):
            best_by_target[target_id] = edge
    by_source = {}
    for edge in best_by_target.values():
        by_source.setdefault(int(edge["source_id"]), []).append(edge)
    edges = []
    for source_edges in by_source.values():
        edges.extend(sorted(source_edges, key=edge_sort_key, reverse=True)[:2])
    incident = {int(e["source_id"]) for e in edges} | {int(e["target_id"]) for e in edges}
    kept = {node_id: node for node_id, node in nodes_by_id.items() if node_id in incident}
    return (kept or nodes_by_id), edges, stats

