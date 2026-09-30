#!/usr/bin/env python3
"""t6r70ff = t6r70 (our representative 0.954 body: t6stk3 + raw-ILP override at prob >= 0.70) + IMGFLOW repair:
image phase-correlation flow-compensated re-assignment plus track-end bridging in high-motion windows, applied as a
write-time post-filter to the FINAL graph (after filter_output_graph AND after the raw-ILP override, i.e. exactly the
graph the offline test repaired: the written CSV).

usage: python scratch_kernels/build_t6r70ff.py [tag]        (default tag t6r70ff)

Offline twin: scratchpad/wf14/errbudget/flowfix.py repair() (box ~/biohub/wf14_alt/errbudget/flowfix.py), pre-registered
config TF 5.0 / KEEP 3.5 / GATE 4.5 / MIN_DET 5 / ENDS on. The in-kernel code is that function verbatim (MODE branch
dropped, extra counters returned), fed with the WRITTEN (rounded, clamped) coordinates, nodes in node-id order and edges
in written order, so it reproduces the offline repair of the pre-repair CSV edge for edge (box bit check: wf14 errbudget
port/bitcheck).
Per movie (T frames): 8 windows (z halves x 2x2 y/x) per frame pair, y/x 2x binned, float32 3-D phase correlation ->
local flow f (um). In windows with |f| >= 5 um and >= 5 written nodes: out-degree-1 sources keep their edge if its flow
residual |p_b - p_a - f| <= 3.5 um, otherwise they are re-assigned by Hungarian on flow-compensated distance (gate 4.5
um) over targets not held by kept edges / forks / sources outside the set; track ends (out 0, in > 0) may be bridged to
a free target. A no-merge revert loop keeps in-degree <= 1. Nodes and forks are never touched.
Guards: frame shape must be (64, 256, 256); wall-clock deadline 9.5 h since kernel start (then the movie is written
unrepaired); any exception or invariant break (in-degree > 1, a changed division count, an out-degree change other than
0 -> 1, a non-consecutive edge) writes the unrepaired graph for that movie.
Markers: ARM_XENV tag=<tag> FLOWFIX=1 ... (cell 0), ARM_FLOWFIX enabled=True ... (cell 5 definition), one
ARM_FLOWFIX [<movie>] status=ok ... line per movie (cell 5 writer), run_stats columns flowfix_*.
All other cells are t6r70's byte for byte (checked below).
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6r70"
BASE_MD5 = "38adf357f63250a34ce7f6337c47c626"  # v_t6r70/kernel.ipynb == box wf16 batchA/nbs/t6r70.ipynb
NL = chr(10)

C5_DEF_ANCHOR = 'DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()\n\ndef write_test_submission(tag: str = "base") -> None:\n'
C5_CALL_ANCHOR = ("f\" new_isolated={rawlink_stats['rawlink_new_isolated']}\", flush=True)\n\n"
                  "            for node_id in sorted(nodes_by_id):\n")
C5_STATS_ANCHOR = "                **rawlink_stats,\n            })\n"
C5_RAWSTATS_ANCHOR = "            rawlink_stats: dict[str, object] = {}\n"

HELPER = r'''
# ---- ARM_FLOWFIX (scratch_kernels/build_t6r70ff.py) ---------------------------------------------------------------
# IMGFLOW write-time repair. Offline twin: wf14 errbudget flowfix.py repair(), config TF 5 / KEEP 3.5 / GATE 4.5 /
# MIN_DET 5 / ENDS on. Acts on the FINAL graph after the raw-ILP override; node set and forks untouched.
import time as _ff_time
from collections import defaultdict as _ff_dd
from concurrent.futures import ThreadPoolExecutor as _FF_TPE

FLOWFIX_ENABLED = os.environ.get("BIOHUB_FLOWFIX", "0") == "1"
FLOWFIX_CFG = dict(TF=5.0, KEEP=3.5, GATE=4.5, MIN_DET=5, ENDS=True)
FLOWFIX_DEADLINE_S = float(os.environ.get("BIOHUB_FLOWFIX_DEADLINE_S", "34200"))  # 9.5 h since kernel start
FLOWFIX_THREADS = max(1, min(4, os.cpu_count() or 1))
_FF_SCB = np.array([1.625, 0.8125, 0.8125])  # um per binned voxel (z, y/2, x/2)
_FF_SC = np.array([1.625, 0.40625, 0.40625])


def _ff_kernel_t0() -> float:
    t0 = float(os.environ.get("BIOHUB_FLOWFIX_T0", repr(_ff_time.time())))
    try:
        import psutil
        t0 = min(t0, float(psutil.Process(os.getpid()).create_time()))
    except Exception:
        pass
    return t0


_FF_T0 = _ff_kernel_t0()


def _ff_pc_shift(A, B):
    """shift s (voxels) such that B(x) ~ A(x - s), i.e. content moved by +s from A to B."""
    A = A.astype(np.float32)
    B = B.astype(np.float32)
    A = A - A.mean()
    B = B - B.mean()
    w = np.ones_like(A)
    for ax, n in enumerate(A.shape):
        sh = [1] * A.ndim
        sh[ax] = n
        w = w * np.hanning(n).reshape(sh).astype(np.float32)
    FA = np.fft.fftn(A * w)
    FB = np.fft.fftn(B * w)
    R = FB * np.conj(FA)
    R /= np.abs(R) + 1e-6
    r = np.real(np.fft.ifftn(R))
    k = np.array(np.unravel_index(np.argmax(r), r.shape))
    # 3x3x3 centroid refine (circular)
    sub = np.zeros(3)
    tot = 0.0
    for dz in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                v = r[(k[0] + dz) % r.shape[0], (k[1] + dy) % r.shape[1], (k[2] + dx) % r.shape[2]]
                v = max(v, 0)
                sub += v * np.array([dz, dy, dx])
                tot += v
    k = k + (sub / tot if tot > 0 else 0)
    n = np.array(r.shape)
    k = np.where(k > n / 2, k - n, k)
    peak = float(r.max())
    return k, peak


def _ff_load_binned(dataset, tt):
    v = np.asarray(read_test_frame(dataset, int(tt), {})).astype(np.float32)
    return v.reshape(v.shape[0], v.shape[1] // 2, 2, v.shape[2] // 2, 2).mean(axis=(2, 4))


def _ff_pair(job):
    tt, prev, cur = job
    out = {}
    for iz in range(2):
        for iy in range(2):
            for ix in range(2):
                sl = (slice(32 * iz, 32 * iz + 32), slice(64 * iy, 64 * iy + 64), slice(64 * ix, 64 * ix + 64))
                s, pk = _ff_pc_shift(prev[sl], cur[sl])
                out[(tt, iz, iy, ix)] = (s * _FF_SCB, pk)
    return out


def _ff_flows(dataset, nT, chunk=16):
    F = {}
    with _FF_TPE(FLOWFIX_THREADS) as ex:
        start = 0
        while start < nT - 1:
            stop = min(start + chunk, nT - 1)
            frames = list(ex.map(lambda tt: _ff_load_binned(dataset, tt), range(start, stop + 1)))
            for r in ex.map(_ff_pair, [(start + k, frames[k], frames[k + 1]) for k in range(stop - start)]):
                F.update(r)
            start = stop
    return F


def _ff_win_of(p_vox):
    z, y, x = p_vox
    return (min(int(z // 32), 1), min(int(y // 128), 1), min(int(x // 128), 1))


def _ff_repair(t, pos, e, F, cfg):
    """flowfix.py repair(), MODE 'flow', verbatim; also returns (changed, bridged, dups)."""
    from scipy.optimize import linear_sum_assignment as _lsa
    from scipy.spatial import cKDTree as _KD
    P = pos * np.array([1.625, 0.40625, 0.40625])
    out = _ff_dd(list)
    inn = _ff_dd(list)
    for k, (a, b) in enumerate(e):
        out[int(a)].append(k)
        inn[int(b)].append(k)
    idx = _ff_dd(list)
    for i, tt in enumerate(t):
        idx[int(tt)].append(i)
    E = [list(map(int, r)) for r in e]
    alive = [True] * len(E)
    changed = 0
    bridged = 0
    ends = cfg.get("ENDS", False)
    for tt in sorted(idx):
        if tt + 1 not in idx:
            continue
        src_all = np.array(idx[tt])
        wins = _ff_dd(list)
        for i in src_all:
            wins[_ff_win_of(pos[i])].append(int(i))
        tgt = np.array(idx[tt + 1])
        tree = _KD(P[tgt])
        for w, S in wins.items():
            f, pk = F.get((tt,) + w, (np.zeros(3), 0.0))
            if np.linalg.norm(f) < cfg["TF"] or len(S) < cfg["MIN_DET"]:
                continue
            Sset = set(S)
            srcs = []
            reserved = set()
            for i in S:
                ks = [k for k in out[i] if alive[k] and t[E[k][1]] == tt + 1]
                if len(ks) == 0 and ends and len(inn[i]) > 0:
                    srcs.append((i, None))
                    continue
                if len(ks) != 1:
                    if ks:
                        reserved.update(int(E[k][1]) for k in ks)
                    continue
                k = ks[0]
                b = int(E[k][1])
                if np.linalg.norm(P[b] - P[i] - f) <= cfg["KEEP"]:
                    reserved.add(b)
                else:
                    srcs.append((i, k))
            if not srcs:
                continue
            cand = set()
            for i, k in srcs:
                for j in tree.query_ball_point(P[i] + f, cfg["GATE"]):
                    cand.add(int(tgt[j]))
            cur_tg = {int(E[k][1]) for _, k in srcs if k is not None}
            ok = []
            for j in cand:
                if j in reserved:
                    continue
                holders = [kk for kk in inn[j] if alive[kk] and t[E[kk][0]] == tt]
                if any(int(E[kk][0]) not in Sset for kk in holders):
                    continue
                if any(int(E[kk][0]) in Sset and kk not in [k for _, k in srcs] for kk in holders):
                    continue
                ok.append(j)
            ok = sorted(set(ok) | cur_tg - reserved)
            if not ok:
                continue
            C = np.full((len(srcs), len(ok)), 1e6)
            for r, (i, k) in enumerate(srcs):
                for c, j in enumerate(ok):
                    d = np.linalg.norm(P[j] - P[i] - f)
                    if d <= cfg["GATE"]:
                        C[r, c] = d
            rr, cc = _lsa(C)
            newt = {srcs[r][0]: ok[c] for r, c in zip(rr, cc) if C[r, c] < 1e6}
            cur = {i: (int(E[k][1]) if k is not None else None) for i, k in srcs}
            final = {i: newt.get(i, cur[i]) for i, _ in srcs}
            for _ in range(len(srcs) + 1):
                cnt = _ff_dd(list)
                for i, j in final.items():
                    if j is not None:
                        cnt[j].append(i)
                bad = [(j, L) for j, L in cnt.items() if len(L) > 1]
                if not bad:
                    break
                for j, L in bad:
                    for i in L:
                        if final[i] != cur[i]:
                            final[i] = cur[i]
            else:
                final = dict(cur)
            for i, k in srcs:
                if k is None:
                    if final[i] is not None:
                        E.append([i, final[i]])
                        alive.append(True)
                        kn = len(E) - 1
                        out[i].append(kn)
                        inn[final[i]].append(kn)
                        changed += 1
                        bridged += 1
                    continue
                if final[i] != int(E[k][1]):
                    inn[int(E[k][1])].remove(k)
                    E[k][1] = final[i]
                    inn[final[i]].append(k)
                    changed += 1
    seen = set()
    keep = []
    E = np.array(E, np.int64).reshape(-1, 2)
    for k, (a, b) in enumerate(E):
        key = (int(a), int(b))
        if key in seen:
            continue
        seen.add(key)
        keep.append(k)
    return E[keep], changed, bridged, len(E) - len(keep)


def flow_repair(dataset, nodes_by_id, edges):
    """Returns (edges, stats). On any guard / error the input edges are returned unchanged."""
    t_start = _ff_time.time()
    elapsed = t_start - _FF_T0
    stats = {"flowfix_status": "off", "flowfix_windows": 0, "flowfix_flagged": 0, "flowfix_acted": 0,
             "flowfix_changed": 0, "flowfix_bridged": 0, "flowfix_dups": 0, "flowfix_secs": 0.0}
    if elapsed > FLOWFIX_DEADLINE_S:
        stats["flowfix_status"] = "skipped_deadline"
        print(f"ARM_FLOWFIX [{dataset}] SKIPPED deadline elapsed_h={elapsed / 3600:.2f}", flush=True)
        return edges, stats
    try:
        shp = tuple(np.asarray(read_test_frame(dataset, 0, {})).shape)
        if shp != (64, 256, 256):
            stats["flowfix_status"] = "skipped_shape"
            print(f"ARM_FLOWFIX [{dataset}] SKIPPED shape={shp}", flush=True)
            return edges, stats
        ids = sorted(nodes_by_id)
        index = {nid: i for i, nid in enumerate(ids)}
        t = np.array([int(nodes_by_id[n]["t"]) for n in ids], np.int64)
        pos = np.array([(max(0, int(round(float(nodes_by_id[n]["z"])))),  # the WRITTEN coordinates
                         max(0, int(round(float(nodes_by_id[n]["y"])))),
                         max(0, int(round(float(nodes_by_id[n]["x"]))))) for n in ids], float).reshape(-1, 3)
        e = np.array([(index[int(ed["source_id"])], index[int(ed["target_id"])]) for ed in edges],
                     np.int64).reshape(-1, 2)
        nT = int(t.max()) + 1
        F = _ff_flows(dataset, nT)
        cnt = _ff_dd(int)
        for tt, p in zip(t, pos):
            cnt[(int(tt),) + _ff_win_of(p)] += 1
        flagged = [k for k, v in F.items() if np.linalg.norm(v[0]) >= FLOWFIX_CFG["TF"]]
        stats["flowfix_windows"] = len(F)
        stats["flowfix_flagged"] = len(flagged)
        stats["flowfix_acted"] = sum(1 for k in flagged if cnt.get(k, 0) >= FLOWFIX_CFG["MIN_DET"])
        E2, changed, bridged, dups = _ff_repair(t, pos, e, F, FLOWFIX_CFG)
        n = len(ids)
        in0 = np.bincount(e[:, 1], minlength=n) if len(e) else np.zeros(n, np.int64)
        in1 = np.bincount(E2[:, 1], minlength=n) if len(E2) else np.zeros(n, np.int64)
        out0 = np.bincount(e[:, 0], minlength=n) if len(e) else np.zeros(n, np.int64)
        out1 = np.bincount(E2[:, 0], minlength=n) if len(E2) else np.zeros(n, np.int64)
        why = []
        if in1.max(initial=0) > max(1, in0.max(initial=0)):
            why.append("in_degree")
        if int((out1 >= 2).sum()) != int((out0 >= 2).sum()):
            why.append("divisions")
        dout = out1 - out0
        if np.any((dout != 0) & ~((out0 == 0) & (out1 == 1))):
            why.append("out_degree")
        if len(E2) and np.any(t[E2[:, 1]] - t[E2[:, 0]] != 1):
            why.append("dt")
        secs = _ff_time.time() - t_start
        stats.update(flowfix_changed=int(changed), flowfix_bridged=int(bridged), flowfix_dups=int(dups),
                     flowfix_secs=round(secs, 2))
        if why:
            stats["flowfix_status"] = "fallback_invariant"
            print(f"ARM_FLOWFIX [{dataset}] FALLBACK invariant={','.join(why)} changed={changed}", flush=True)
            return edges, stats
        new_edges = [{"source_id": int(ids[a]), "target_id": int(ids[b])} for a, b in E2]
        stats["flowfix_status"] = "ok"
        print(f"ARM_FLOWFIX [{dataset}] status=ok windows={len(F)} flagged={stats['flowfix_flagged']}"
              f" acted={stats['flowfix_acted']} changed={changed} bridged={bridged} dups={dups}"
              f" edges={len(edges)}->{len(new_edges)} divs={int((out0 >= 2).sum())}->{int((out1 >= 2).sum())}"
              f" max_in={int(in1.max(initial=0))} secs={secs:.1f} elapsed_h={(_ff_time.time() - _FF_T0) / 3600:.2f}",
              flush=True)
        return new_edges, stats
    except Exception as exc:  # never lose a movie to the repair
        stats["flowfix_status"] = "fallback_error"
        print(f"ARM_FLOWFIX [{dataset}] FALLBACK error={type(exc).__name__}: {str(exc)[:200]}", flush=True)
        return edges, stats


print(f"ARM_FLOWFIX enabled={FLOWFIX_ENABLED} TF={FLOWFIX_CFG['TF']} KEEP={FLOWFIX_CFG['KEEP']}"
      f" GATE={FLOWFIX_CFG['GATE']} MIN_DET={FLOWFIX_CFG['MIN_DET']} ENDS={int(FLOWFIX_CFG['ENDS'])}"
      f" threads={FLOWFIX_THREADS} deadline_s={FLOWFIX_DEADLINE_S:.0f}", flush=True)
# ---- end ARM_FLOWFIX helper ---------------------------------------------------------------------------------------

'''

CALL = '''            flowfix_stats: dict[str, object] = {}
            if FLOWFIX_ENABLED:
                edges, flowfix_stats = flow_repair(dataset, nodes_by_id, edges)  # ARM_FLOWFIX: after rawlink, before writing
'''


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t6r70ff"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t6r70/kernel.ipynb changed since the box bit check (md5 mismatch)")
    nb = json.loads(raw.decode("utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    orig = list(cells)
    c0, c5 = cells[0], cells[5]
    for name, a, src in (("c5_def", C5_DEF_ANCHOR, c5), ("c5_call", C5_CALL_ANCHOR, c5), ("c5_stats", C5_STATS_ANCHOR, c5),
                         ("c5_rawstats", C5_RAWSTATS_ANCHOR, c5)):
        if src.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (name, src.count(a)))
    for bad in ("ARM_FLOWFIX", "BIOHUB_FLOWFIX", "flow_repair"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base already carries %s" % bad)
    if "BIOHUB_RAWLINK_MIN_PROB" not in c0 or "rawlink_override" not in c5:
        raise SystemExit("rawlink component missing from the base")
    c5 = c5.replace(C5_DEF_ANCHOR, C5_DEF_ANCHOR.replace("\ndef write_test_submission", HELPER + "\ndef write_test_submission"), 1)
    c5 = c5.replace(C5_CALL_ANCHOR, C5_CALL_ANCHOR.replace("\n\n            for node_id in sorted(nodes_by_id):\n",
                                                           "\n\n" + CALL + "\n            for node_id in sorted(nodes_by_id):\n"), 1)
    c5 = c5.replace(C5_STATS_ANCHOR, "                **rawlink_stats,\n                **flowfix_stats,\n            })\n", 1)
    c0 = (c0.rstrip(NL) + NL
          + "import time as _ff_time0" + NL
          + "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX deadline clock" + NL
          + "os.environ['BIOHUB_FLOWFIX'] = '1'" + NL
          + "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'" + NL
          + 'print("ARM_XENV tag=%s FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200", flush=True)' % tag + NL)
    cells[0], cells[5] = c0, c5
    # every other cell byte-identical to t6r70; cell 5's only differences are the three insertions
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i not in (0, 5) and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    if c5.replace(HELPER, "").replace(CALL + "\n", "").replace("                **flowfix_stats,\n", "") != orig[5]:
        raise SystemExit("cell 5 differs from t6r70's by more than the three ARM_FLOWFIX insertions")
    if c5.count("DEEPCENTER_VETO_DETECTOR = load_deepcenter_veto_detector()") != 1:
        raise SystemExit("nbrun split anchor count changed")
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
    print("built", dest, "| base v_t6r70 (md5 %s) | IMGFLOW TF5 KEEP3.5 GATE4.5 MIN_DET5 ENDS1" % BASE_MD5)
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
