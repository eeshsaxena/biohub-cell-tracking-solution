#!/usr/bin/env python3
"""t6stk3fld = t6stk3fl (t6stk3ff + FLOWLINK) with DIVISION-SAFE FLOWLINK ("FLD": base division families are frozen).
wf21 track C, pre-registered (scratchpad/wf21/C/PREREG.md, md5 eb1cefcf9970f954a8c8c1757b8ea9f0; box ~/biohub/wf21/C).

usage: python scratch_kernels/build_t6stk3fld.py [tag]        (default tag t6stk3fld)

Why: every written fork of the t6stk3 body is added post-link by add_safe_divisions_postlink (the ILP writes none, the
motion relink is one-to-one). FLOWLINK re-routes edges around fork parents (flagged parents, daughters taken by flagged
sources) and leaves new unmatched targets -> t6stk3fla writes 6.4% fewer forks (3071 -> 2875 on 199 train replays).
FLD, per movie when FLOWLINK has flows:
  1. BASE PASS: the unmodified production post-processing (filter_output_graph with FLOWLINK off == t6stk3's cell-5
     graph) on deep copies, stdout suppressed. Base fork parents P = raw nodes with written out-degree >= 2; family
     F = P + children + the children's successors (raw ids).
  2. RELINK (main pass): flagged sources in F are un-flagged (production geometry); flow-compensated sources may not
     link into F.
  3. SAFE DIVISIONS (main pass): a second child only at a base fork parent (source in P); all else unchanged.
  Then the IMGFLOW write-time repair verbatim (forks untouched).
No-output-effect guards: exact relink frame reuse from the base pass (identical frame inputs -> identical Hungarian;
BIOHUB_FLD_REUSE), per-movie memo of DeepCenter point scores across the two passes, 8.0 h deadline
(BIOHUB_FLD_DEADLINE_S=28800) and base-pass exceptions -> production relink for that movie (t6stk3ff behaviour).
Markers: ARM_XENV tag=<tag> FLOWLINK=1 FLD=1 ..., ARM_FLD enabled=True ..., per movie 'ARM_FLD [<m>] status=ok
base_forks=...' (before the main pass) and 'ARM_FLD [<m>] main forks=... at_base_parents=...' (after FINAL).
The relink / safe-division patch strings (FLD_RELINK_PAIRS, FLD_SD_PAIR) are imported VERBATIM by the LOEO harness
(scratchpad/wf21/C/fld_loeo.py) so replay, LOEO and kernel run the same code.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_t6stk3fl as BFL  # noqa: E402
from build_t6r70ff import HELPER, CALL, C5_DEF_ANCHOR, NL  # noqa: E402
from build_t6stk3ff import BASE, BASE_MD5, C5_CALL_ANCHOR, C5_STATS_ANCHOR, SK  # noqa: E402

# ---- relink patch = FLOWLINK pairs with the FLD family freeze folded in (kernel AND LOEO harness) --------------------
_FL_FLAG_LINE = ("    _fl_flag = _fl_flag_map(nodes_by_id) if FLOWLINK_ENABLED else {}  # ARM_FLOWLINK\n"
                 "    stats[\"flowlink_flagged_sources\"] = len(_fl_flag)\n")
_FLD_FLAG_LINE = ("    _fl_flag = _fl_flag_map(nodes_by_id) if (FLOWLINK_ENABLED and not _FL_CTX.get(\"fld_off\")) else {}"
                  "  # ARM_FLOWLINK\n"
                  "    _fld_fam = _FL_CTX.get(\"fld_family\") or frozenset()  # ARM_FLD: base division families are frozen\n"
                  "    _fld_frozen = [_fld_k for _fld_k in _fl_flag if _fld_k in _fld_fam]\n"
                  "    for _fld_k in _fld_frozen:\n"
                  "        del _fl_flag[_fld_k]\n"
                  "    stats[\"fld_frozen_sources\"] = len(_fld_frozen)\n"
                  "    stats[\"flowlink_flagged_sources\"] = len(_fl_flag)\n")
_FL_GATE_LINE = ("                raw = float(np.linalg.norm(target_pos - source_pos))\n"
                 "                gate_d = raw if _fl_f is None else float(np.linalg.norm(target_pos - _fl_anchor))\n")
_FLD_GATE_LINE = ("                raw = float(np.linalg.norm(target_pos - source_pos))\n"
                  "                if _fl_f is not None and target_id in _fld_fam:  # ARM_FLD: no flow link into a frozen family\n"
                  "                    continue\n"
                  "                gate_d = raw if _fl_f is None else float(np.linalg.norm(target_pos - _fl_anchor))\n")
for _o, _n, _k in ((_FL_FLAG_LINE, _FLD_FLAG_LINE, 0), (_FL_GATE_LINE, _FLD_GATE_LINE, 1)):
    if BFL.RELINK_PAIRS[_k][1].count(_o) != 1:
        raise SystemExit("FLOWLINK pair %d does not contain the expected FLD anchor" % _k)
FLD_RELINK_PAIRS = [
    (BFL.RELINK_PAIRS[0][0], BFL.RELINK_PAIRS[0][1].replace(_FL_FLAG_LINE, _FLD_FLAG_LINE)),
    (BFL.RELINK_PAIRS[1][0], BFL.RELINK_PAIRS[1][1].replace(_FL_GATE_LINE, _FLD_GATE_LINE)),
    # exact frame reuse (no output effect): look up before the tight/relaxed passes, store after them
    ("        frame_matches: list[tuple[int, int, float, float, str, float]] = []\n"
     "        for pass_name, gate_um in ((\"tight\", MOTION_RELINK_TIGHT_UM), (\"relaxed\", MOTION_RELINK_RELAXED_UM)):\n",
     "        frame_matches: list[tuple[int, int, float, float, str, float]] = []\n"
     "        _fld_key, _fld_hit = _fld_frame_lookup(t, source_ids, target_ids, predecessor_position_um, _fl_flag)  # ARM_FLD\n"
     "        if _fld_hit is not None:\n"
     "            frame_matches = list(_fld_hit)\n"
     "            for _fld_m in frame_matches:\n"
     "                stats[\"motion_relink_tight_edges\" if _fld_m[4] == \"tight\" else \"motion_relink_relaxed_edges\"] += 1\n"
     "        for pass_name, gate_um in (() if _fld_hit is not None else\n"
     "                                   ((\"tight\", MOTION_RELINK_TIGHT_UM), (\"relaxed\", MOTION_RELINK_RELAXED_UM))):\n"),
    ("        for source_id, target_id, raw, motion, pass_name, prob in frame_matches:\n",
     "        _fld_frame_store(_fld_key, frame_matches)  # ARM_FLD\n"
     "        for source_id, target_id, raw, motion, pass_name, prob in frame_matches:\n"),
]
FLD_SD_PAIR = ("        for source_id in source_ids:\n            source = nodes_by_id[source_id]\n",
               "        for source_id in source_ids:\n"
               "            if _FL_CTX.get(\"fld_parents\") is not None and source_id not in _FL_CTX[\"fld_parents\"]:  # ARM_FLD\n"
               "                continue\n"
               "            source = nodes_by_id[source_id]\n")

# ---- frame reuse helpers (kernel AND LOEO harness; defined next to FL_COMMON) -----------------------------------------
FLD_COMMON = r'''
# ---- ARM_FLD core (scratch_kernels/build_t6stk3fld.py; wf21 track C PREREG) -------------------------------------------
_FLD_RELINK = {"mode": None, "memo": {}, "hits": 0}


def _fld_frame_lookup(t, source_ids, target_ids, pred, flag):
    """record (base pass): key to store the frame's matches; reuse (main pass): the base pass's matches iff no source of
    the frame is flagged and (t, sources, targets, predecessor positions) are identical -> identical Hungarian."""
    mode = _FLD_RELINK["mode"]
    if mode is None:
        return None, None
    if mode == "reuse" and any(s in flag for s in source_ids):
        return None, None
    key = (int(t), tuple(source_ids), tuple(target_ids),
           tuple(pred[s].tobytes() if s in pred else None for s in source_ids))
    if mode == "reuse":
        hit = _FLD_RELINK["memo"].get(key)
        if hit is not None:
            _FLD_RELINK["hits"] += 1
        return None, hit
    return key, None


def _fld_frame_store(key, frame_matches):
    if key is not None and _FLD_RELINK["mode"] == "record":
        _FLD_RELINK["memo"][key] = tuple(frame_matches)
# ---- end ARM_FLD core -------------------------------------------------------------------------------------------------
'''

FLD_KERNEL = r'''
# ---- ARM_FLD kernel part: base pass -> frozen division families, DeepCenter memo, deadline ----------------------------
import contextlib as _fld_contextlib
import copy as _fld_copy
import io as _fld_io

FLD_DEADLINE_S = float(os.environ.get("BIOHUB_FLD_DEADLINE_S", "28800"))
FLD_REUSE = os.environ.get("BIOHUB_FLD_REUSE", "1") == "1"
_FLD_DC_MEMO = {}
_fld_dc_score_orig = deepcenter_score_point


def deepcenter_score_point(dataset, t, point, detector_bundle, frame_cache, heatmap_cache):
    """ARM_FLD: memoised per movie so the base pass and the main pass score each DeepCenter point once (the score is a
    deterministic function of (movie, t, point))."""
    key = (dataset, int(t), float(point[0]), float(point[1]), float(point[2]))
    if key in _FLD_DC_MEMO:
        return _FLD_DC_MEMO[key]
    value = _fld_dc_score_orig(dataset, t, point, detector_bundle, frame_cache, heatmap_cache)
    _FLD_DC_MEMO[key] = value
    return value


def _fld_reset():
    _FL_CTX.update(fld_family=None, fld_parents=None, fld_off=False)
    _FLD_RELINK.update(mode=None, memo={}, hits=0)
    _FLD_DC_MEMO.clear()


def fld_prepare(dataset, nodes_by_id, raw_edges):
    """Base pass (production post-processing, FLOWLINK off) -> frozen families for the main pass. Any guard / error ->
    fld_off (production relink for this movie)."""
    _fld_reset()
    st = {"fld_status": "off", "fld_base_forks": -1, "fld_family_nodes": 0, "fld_secs": 0.0}
    if _FL_CTX.get("F") is None:
        st["fld_status"] = "no_flow"
        print(f"ARM_FLD [{dataset}] no_flow -> production relink", flush=True)
        return st
    t_start = _ff_time.time()
    elapsed = t_start - _FF_T0
    if elapsed > FLD_DEADLINE_S:
        _FL_CTX["fld_off"] = True
        st["fld_status"] = "skipped_deadline"
        print(f"ARM_FLD [{dataset}] SKIPPED deadline elapsed_h={elapsed / 3600:.2f} -> production relink", flush=True)
        return st
    try:
        _FL_CTX["fld_off"] = True
        _FLD_RELINK.update(mode="record" if FLD_REUSE else None, memo={}, hits=0)
        with _fld_contextlib.redirect_stdout(_fld_io.StringIO()):
            b_nodes, b_edges, _b_stats = filter_output_graph(
                _fld_copy.deepcopy(nodes_by_id), _fld_copy.deepcopy(raw_edges), dataset=dataset,
                deepcenter_bundle=DEEPCENTER_VETO_DETECTOR)
        out = {}
        for e in b_edges:
            out.setdefault(int(e["source_id"]), []).append(int(e["target_id"]))
        raw_ids = set(nodes_by_id)
        n_forks = sum(1 for c in out.values() if len(c) >= 2)
        parents = {p for p, c in out.items() if len(c) >= 2 and p in raw_ids}
        fam = set(parents)
        for p in parents:
            for c in out[p]:
                fam.add(c)
                fam.update(out.get(c, []))
        fam &= raw_ids
        _FL_CTX.update(fld_family=frozenset(fam), fld_parents=frozenset(parents), fld_off=False)
        _FLD_RELINK["mode"] = "reuse" if FLD_REUSE else None
        st.update(fld_status="ok", fld_base_forks=n_forks, fld_family_nodes=len(fam),
                  fld_secs=round(_ff_time.time() - t_start, 2))
        print(f"ARM_FLD [{dataset}] status=ok base_forks={n_forks} parents={len(parents)} family_nodes={len(fam)}"
              f" base_nodes={len(b_nodes)} base_edges={len(b_edges)} memo_frames={len(_FLD_RELINK['memo'])}"
              f" secs={st['fld_secs']:.1f}", flush=True)
        return st
    except Exception as exc:  # division-safe fallback: production relink for this movie
        _fld_reset()
        _FL_CTX["fld_off"] = True
        st["fld_status"] = "fallback_error"
        print(f"ARM_FLD [{dataset}] FALLBACK error={type(exc).__name__}: {str(exc)[:200]} -> production relink",
              flush=True)
        return st


def fld_finish(dataset, edges):
    out = {}
    for e in edges:
        out[int(e["source_id"])] = out.get(int(e["source_id"]), 0) + 1
    forks = {p for p, c in out.items() if c >= 2}
    parents = _FL_CTX.get("fld_parents")
    if parents is not None:
        print(f"ARM_FLD [{dataset}] main forks={len(forks)} at_base_parents={len(forks & parents)}"
              f" base_parents={len(parents)} reused_frames={_FLD_RELINK['hits']}", flush=True)
    else:
        print(f"ARM_FLD [{dataset}] main forks={len(forks)} production", flush=True)
    _fld_reset()


print(f"ARM_FLD enabled=True family=parent+children+grandchildren safe_div=base_parents_only reuse={int(FLD_REUSE)}"
      f" deadline_s={FLD_DEADLINE_S:.0f}", flush=True)
# ---- end ARM_FLD kernel part ------------------------------------------------------------------------------------------
'''

C5_PREP_NEW = BFL.C5_PREP_NEW.replace(
    "                flowlink_stats = flowlink_prepare(dataset, nodes_by_id)  # ARM_FLOWLINK\n",
    "                flowlink_stats = flowlink_prepare(dataset, nodes_by_id)  # ARM_FLOWLINK\n"
    "                flowlink_stats.update(fld_prepare(dataset, nodes_by_id, raw_edges))  # ARM_FLD\n")
C5_POST_NEW = BFL.C5_POST_NEW + ("            if FLOWLINK_ENABLED:\n"
                                 "                fld_finish(dataset, edges)  # ARM_FLD\n")


def patch(src, pairs, what):
    for old, new in pairs:
        if src.count(old) != 1:
            raise SystemExit("%s anchor matched %d times: %r" % (what, src.count(old), old[:70]))
        src = src.replace(old, new, 1)
    return src


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tag = args[0] if args else "t6stk3fld"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t6stk3/kernel.ipynb changed since the box bit check (md5 mismatch)")
    nb = json.loads(raw.decode("utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    orig = list(cells)
    c0, c5 = cells[0], cells[5]
    for name, a in (("c5_def", C5_DEF_ANCHOR), ("c5_call", C5_CALL_ANCHOR), ("c5_stats", C5_STATS_ANCHOR),
                    ("c5_prep", BFL.C5_PREP_OLD), ("c5_post", BFL.C5_POST_OLD)):
        if c5.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, c5.count(a)))
    if HELPER.count(BFL.HELPER_FLOW_OLD) != 1:
        raise SystemExit("helper flow anchor count %d" % HELPER.count(BFL.HELPER_FLOW_OLD))
    for bad in ("ARM_FLOWFIX", "ARM_FLOWLINK", "ARM_FLD", "BIOHUB_FLOWFIX", "BIOHUB_FLOWLINK", "BIOHUB_FLD",
                "flow_repair", "rawlink_override", "BIOHUB_RAWLINK_MIN_PROB"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %s" % bad)
    helper = HELPER.replace(BFL.HELPER_FLOW_OLD, BFL.HELPER_FLOW_NEW, 1)
    block = helper + BFL.FL_COMMON + FLD_COMMON + BFL.FL_KERNEL + FLD_KERNEL
    c5 = patch(c5, FLD_RELINK_PAIRS, "relink")
    c5 = patch(c5, [FLD_SD_PAIR], "safe-division")
    c5 = c5.replace(C5_DEF_ANCHOR, C5_DEF_ANCHOR.replace("\ndef write_test_submission", block + "\ndef write_test_submission"), 1)
    c5 = c5.replace(BFL.C5_PREP_OLD, C5_PREP_NEW, 1)
    c5 = c5.replace(C5_CALL_ANCHOR, C5_CALL_ANCHOR.replace("\n\n            for node_id in sorted(nodes_by_id):\n",
                                                           "\n\n" + CALL + "\n            for node_id in sorted(nodes_by_id):\n"), 1)
    c5 = c5.replace(BFL.C5_POST_OLD, C5_POST_NEW, 1)
    c5 = c5.replace(C5_STATS_ANCHOR, BFL.STATS_NEW, 1)
    c0 = (c0.rstrip(NL) + NL
          + "import time as _ff_time0" + NL
          + "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX/FLOWLINK/FLD deadline clock" + NL
          + "os.environ['BIOHUB_FLOWFIX'] = '1'" + NL
          + "os.environ['BIOHUB_FLOWLINK'] = '1'" + NL
          + "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'" + NL
          + "os.environ['BIOHUB_FLD_REUSE'] = '1'" + NL
          + "os.environ['BIOHUB_FLD_DEADLINE_S'] = '28800'" + NL
          + ('print("ARM_XENV tag=%s FLOWLINK=1 FL_TF=5.0 FL_MIN_DET=5 FLD=1 FLD_DEADLINE_S=28800 FLOWFIX=1 TF=5.0'
             ' KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200", flush=True)' % tag) + NL)
    cells[0], cells[5] = c0, c5
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i not in (0, 5) and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    # reverse every insertion -> must give t6stk3's cell 5 back exactly
    rev = c5.replace(block, "").replace(CALL + "\n", "").replace(BFL.STATS_NEW, C5_STATS_ANCHOR)
    rev = rev.replace(C5_PREP_NEW, BFL.C5_PREP_OLD).replace(C5_POST_NEW, BFL.C5_POST_OLD)
    for old, new in FLD_RELINK_PAIRS + [FLD_SD_PAIR]:
        rev = rev.replace(new, old)
    if rev != orig[5]:
        raise SystemExit("cell 5 differs from t6stk3's by more than the ARM_FLOWFIX + ARM_FLOWLINK + ARM_FLD insertions")
    if c5.count("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()") != 1:
        raise SystemExit("nbrun split anchor count changed")
    # the DeepCenter memo must wrap the production scorer defined BEFORE it (and the replay's dc_wrap hook point)
    if not (c5.index("def deepcenter_score_point(") < c5.index("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()")
            < c5.index("_fld_dc_score_orig = deepcenter_score_point") < c5.index("def write_test_submission")):
        raise SystemExit("DeepCenter memo placement unexpected")
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
    print("built", dest, "| base v_t6stk3 (md5 %s) | FLOWLINK TF5 MIN_DET5 + FLD (frozen base division families) |"
          " IMGFLOW repair ON (TF5 KEEP3.5 GATE4.5 MIN_DET5 ENDS1)" % BASE_MD5)
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
