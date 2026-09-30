#!/usr/bin/env python3
"""Build scratch_kernels/v_nativecen: a CPU-only research notebook (never submitted).

usage: python scratch_kernels/build_nativecen.py

QUESTION. The board rewards cutting the TAIL of frame-to-frame displacement errors (share of GT edges with
3-D displacement error > 3 um).  Detections live on the UNet feature grid (native x (1,4,4)), so in y/x a cell
can jump a whole 1.625 um grid step between frames.  Does refining each detection with a deterministic
intensity-weighted centroid on the NATIVE image (0.40625 um pixels) cut that tail better than the sub-voxel
(SV) soft-argmax that production uses (t6stk3, z gain 2 + y/x gain 2, clip 0.4999 grid)?

WHAT THE NOTEBOOK DOES (all on CPU, reads the competition train volumes that are not available locally):
  1. loads v1284cap_candidates.npz (kernel output eeshsaxena/biohub-v-v1284cap), recomputes the gain-1 1-D
     soft-argmax offsets (SOFT) from the captured features with the EMBEDDED primary detect_head weights
     (a 1x1 conv: 32 weights + bias, so no checkpoint is needed), and rebuilds the local proxy's matched
     pairs (Hungarian per frame at 3 um, det = grid*1.625 um, GT = native*(1.625, 0.40625, 0.40625) um)
     and GT edges (both ends matched).  Fingerprints of the local proxy (scratchpad wf7/calib/cache.npz)
     are embedded and checked: the 24-movie edge set of the proxy must reproduce bit-for-bit; the Kaggle
     run adds GT edges for the 36 movies whose .geff is not local (6bba: 3 -> 39 movies).
  2. per movie, reads each needed native frame from the train .zarr (minimal zarr-v3 reader: blosc2 /
     numcodecs for blosc, zstandard / pyarrow / numcodecs for zstd; the Kaggle image has no zarr package)
     and computes 18 centroid variants around the detection's native position (z, 4y, 4x):
       A{4,6,8}    2-D y/x box centroid on the detection's z slice, bg = window p10, clipped at 0, 1 pass
       A{4,6,8}i   same, iterated with a partial-pixel box re-centred on the float estimate
       G3, G5      2-D Gaussian-weighted (mean-shift) centroid, sigma 3 / 5 native px
       B{4,6,8}z{1,2}  3-D box centroid over z +-1 / +-2 slices (z centroid too), 1 pass
       B6z1i, B6z2i    3-D iterated partial-pixel box
       G4z15       3-D Gaussian-weighted centroid (sigma 4 px y/x, 1.5 slices z)
       D           sub-voxel peak of the Gaussian-smoothed native image (3-point Gaussian fit per axis)
     Shifts are clipped at evaluation to 1 grid step (4 px y/x, 1 slice z) and, in a second pass, to half a
     step (2 px, 0.4999 slice); a failed/empty window falls back to the grid position.
  3. arms = references (zero, SV z2yx2 = t6stk3, SV z0yx2 = t6svyx, SV z2yx0 = t6svz0yx) + every variant with
     z from {grid, SV, native}; per arm: per-detection mean |error| per axis, the share of GT edges with 3-D
     displacement error > 2/3/4 um per embryo and pooled, and a movie-bootstrap 90% interval of the
     difference vs SV (t6stk3).  Marker lines 'NATIVECEN <arm> ...' (all 60 movies) and
     'NATIVECEN_P24 <arm> ...' (the exact local-proxy edge set).  CSV/JSON/NPZ to /kaggle/working.
  4. wall-clock guard (NATIVECEN_BUDGET_S, default 7000 s): no new movie after it; metrics use the movies
     that finished.

Local test: scratchpad wf9/nativecen/test_nativecen.py (real-npz port check + synthetic zarr end to end).
"""
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
TAG = "nativecen"
DEST = SK / ("v_" + TAG)
CAP = ROOT / "data" / "out_v1284cap" / "v1284cap_candidates.npz"
CK = SK / "_ckpt" / "primary50ep" / "edge_predictor_best.pth"
CACHE = pathlib.Path(r"C:\Users\eeshs\AppData\Local\Temp\claude\C--Users-eeshs-Downloads"
                     r"\c663dcfb-9cf8-4d4d-aec8-747bb3f17179\scratchpad\wf7\calib\cache.npz")
GRID = 1.625
NL = chr(10)

# =============================================================================== notebook cells
CELL_CONFIG = r'''
# ===== biohub v nativecen: native-resolution intensity centroids for the captured detections =====
# CPU-only research notebook, NEVER submitted.  Does a deterministic intensity-weighted centroid on the NATIVE
# image (0.40625 um pixels, vs the 1.625 um feature grid) cut the tail of GT-edge displacement errors (> 3 um)
# better than production's sub-voxel soft-argmax (t6stk3)?  Built by scratch_kernels/build_nativecen.py.
import csv
import gzip
import hashlib
import itertools
import json
import math
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore", message="Mean of empty slice")
warnings.filterwarnings("ignore", message="invalid value encountered")
T0 = time.time()
EMBED = json.loads(r"""@@EMBED@@""")

COMPETITION = "biohub-cell-tracking-during-development"
INPUT_ROOT = Path(os.environ.get("NATIVECEN_INPUT_ROOT", "/kaggle/input"))
WORKING = Path(os.environ.get("NATIVECEN_WORKING",
                              "/kaggle/working" if Path("/kaggle/working").exists() else "."))
WORKING.mkdir(parents=True, exist_ok=True)
BUDGET_S = float(os.environ.get("NATIVECEN_BUDGET_S", "7000"))      # no new movie after this (s from start)
EXPECT_PROXY = os.environ.get("NATIVECEN_EXPECT_PROXY", "1") != "0"  # check the local-proxy fingerprints
N_BOOT = int(os.environ.get("NATIVECEN_BOOT", "2000"))
MAX_ITER = int(os.environ.get("NATIVECEN_MAX_ITER", "40"))
TOL = float(os.environ.get("NATIVECEN_TOL", "0.002"))           # px, iterative centroid convergence
GRID = 1.625                                    # um per feature-grid voxel, every axis
VOX = np.array([1.625, 0.40625, 0.40625])       # um per native voxel (z, y, x)
DS = np.array([1, 4, 4])                        # native = grid * DS (strided zarr[t, ::1, ::4, ::4])
GATE = 3.0                                      # um, pair matching gate (zacc.py)
SV_GAIN, SV_CLIP = 2.0, 0.4999                  # production SV (t6stk3): gain 2, clip 0.4999 grid


def elapsed():
    return time.time() - T0


def log(msg):
    print(f"[{elapsed():8.1f}s] {msg}", flush=True)


def sha1_arr(a, dtype):
    return hashlib.sha1(np.ascontiguousarray(np.asarray(a).astype(dtype)).tobytes()).hexdigest()


def find_capture():
    env = os.environ.get("NATIVECEN_CAPTURE")
    if env:
        return Path(env)
    direct = INPUT_ROOT / "biohub-v-v1284cap" / "v1284cap_candidates.npz"
    if direct.exists():
        return direct
    hits = sorted(INPUT_ROOT.rglob("v1284cap_candidates.npz"))
    if not hits:
        raise FileNotFoundError(f"v1284cap_candidates.npz not found under {INPUT_ROOT}")
    return hits[0]


def find_train_dir():
    env = os.environ.get("NATIVECEN_TRAIN_DIR")
    if env:
        return Path(env)
    for c in (INPUT_ROOT / "competitions" / COMPETITION / "train", INPUT_ROOT / COMPETITION / "train"):
        if c.exists():
            return c
    for p in INPUT_ROOT.rglob("*.geff"):
        if p.parent.name == "train":
            return p.parent
    raise FileNotFoundError(f"competition train dir not found under {INPUT_ROOT}")


log(f"NATIVECEN start python {sys.version.split()[0]} numpy {np.__version__} budget_s={BUDGET_S:.0f} "
    f"boot={N_BOOT} max_iter={MAX_ITER} tol={TOL}")
'''

CELL_ZARR = r'''
# ===== minimal zarr-v3 reader (the Kaggle image has no zarr / numcodecs; blosc2 + pyarrow are there) =====
DECODERS_USED = {}


def _order(env_key, default):
    return [s.strip() for s in os.environ.get(env_key, default).split(",") if s.strip()]


def _blosc_decode(buf, nbytes):
    errs = []
    for name in _order("NATIVECEN_BLOSC_ORDER", "blosc2,numcodecs,blosc,imagecodecs"):
        try:
            if name == "blosc2":
                import blosc2
                out = blosc2.decompress(bytes(buf))
            elif name == "numcodecs":
                from numcodecs import blosc as _nb
                out = _nb.decompress(bytes(buf))
            elif name == "blosc":
                import blosc as _pb
                out = _pb.decompress(bytes(buf))
            elif name == "imagecodecs":
                import imagecodecs
                out = imagecodecs.blosc_decode(bytes(buf))
            else:
                continue
            if nbytes is not None and len(out) != nbytes:
                raise ValueError(f"decoded {len(out)} bytes, expected {nbytes}")
            DECODERS_USED["blosc"] = name
            return out
        except Exception as exc:  # noqa: BLE001 - try the next decoder
            errs.append(f"{name}: {type(exc).__name__}: {exc}")
    raise RuntimeError("no working blosc decoder: " + " | ".join(errs))


def _zstd_decode(buf, nbytes):
    errs = []
    for name in _order("NATIVECEN_ZSTD_ORDER", "zstandard,pyarrow,numcodecs,stdlib"):
        try:
            if name == "zstandard":
                import zstandard
                out = zstandard.ZstdDecompressor().decompress(bytes(buf), max_output_size=int(nbytes or 0))
            elif name == "pyarrow":
                if nbytes is None:
                    raise ValueError("pyarrow needs the decompressed size")
                import pyarrow as pa
                out = pa.decompress(bytes(buf), decompressed_size=int(nbytes), codec="zstd", asbytes=True)
            elif name == "numcodecs":
                from numcodecs import Zstd
                out = bytes(Zstd().decode(bytes(buf)))
            elif name == "stdlib":
                from compression import zstd as _cz  # python >= 3.14
                out = _cz.decompress(bytes(buf))
            else:
                continue
            if nbytes is not None and len(out) != nbytes:
                raise ValueError(f"decoded {len(out)} bytes, expected {nbytes}")
            DECODERS_USED["zstd"] = name
            return out
        except Exception as exc:  # noqa: BLE001
            errs.append(f"{name}: {type(exc).__name__}: {exc}")
    raise RuntimeError("no working zstd decoder: " + " | ".join(errs))


class ZArr:
    """Read-only zarr v3 array: regular chunk grid, codecs transpose / bytes / blosc / zstd / gzip / crc32c."""

    def __init__(self, path):
        self.path = Path(path)
        meta = json.loads((self.path / "zarr.json").read_text())
        if meta.get("zarr_format") != 3 or meta.get("node_type") != "array":
            raise ValueError(f"{self.path}: not a zarr v3 array")
        self.meta = meta
        self.shape = tuple(int(s) for s in meta["shape"])
        grid = meta["chunk_grid"]
        if grid.get("name") != "regular":
            raise NotImplementedError(f"chunk grid {grid.get('name')}")
        self.chunks = tuple(int(c) for c in grid["configuration"]["chunk_shape"])
        enc = meta.get("chunk_key_encoding") or {"name": "default"}
        self.key_kind = enc.get("name", "default")
        self.sep = (enc.get("configuration") or {}).get("separator", "/" if self.key_kind == "default" else ".")
        self.aa, self.ab, self.bb = [], None, []
        for c in meta["codecs"]:
            name, cfg = c["name"], (c.get("configuration") or {})
            if name == "sharding_indexed":
                raise NotImplementedError("sharding_indexed codec")
            if name == "transpose":
                self.aa.append([int(i) for i in cfg["order"]])
            elif name in ("bytes", "endian"):
                self.ab = cfg
            else:
                self.bb.append((name, cfg))
        dt = np.dtype(meta["data_type"])
        if dt.itemsize > 1:
            dt = dt.newbyteorder("<" if (self.ab or {}).get("endian", "little") == "little" else ">")
        self.dtype = dt
        fill = meta.get("fill_value", 0)
        try:
            self.fill = np.array(fill).astype(dt.newbyteorder("="))
        except Exception:  # noqa: BLE001
            self.fill = np.array(0).astype(dt.newbyteorder("="))
        self.shape_b = list(self.chunks)
        for o in self.aa:
            self.shape_b = [self.shape_b[i] for i in o]
        self.nbytes = int(np.prod(self.shape_b)) * dt.itemsize

    def _key(self, idx):
        parts = [str(int(i)) for i in idx]
        if self.key_kind == "default":
            parts = ["c"] + parts
        if self.sep == "/":
            return self.path.joinpath(*parts)
        return self.path / self.sep.join(parts)

    def _decode(self, raw):
        data = raw
        for i in range(len(self.bb) - 1, -1, -1):
            name, _cfg = self.bb[i]
            expect = self.nbytes if i == 0 else None
            if name == "blosc":
                data = _blosc_decode(data, expect)
            elif name == "zstd":
                data = _zstd_decode(data, expect)
            elif name == "gzip":
                data = gzip.decompress(bytes(data))
            elif name == "crc32c":
                data = bytes(data)[:-4]
            else:
                raise NotImplementedError(f"codec {name}")
        arr = np.frombuffer(data, dtype=self.dtype)
        if arr.size != int(np.prod(self.shape_b)):
            raise ValueError(f"{self.path}: chunk has {arr.size} elements, expected {int(np.prod(self.shape_b))}")
        arr = arr.reshape(self.shape_b)
        for o in reversed(self.aa):
            arr = arr.transpose(np.argsort(o))
        return arr

    def read(self, region):
        """region: one (start, stop) per dimension -> native-endian ndarray."""
        region = [(int(a), int(b)) for a, b in region]
        out = np.empty([b - a for a, b in region], dtype=self.dtype.newbyteorder("="))
        out[...] = self.fill
        if out.size == 0:
            return out
        ranges = [range(a // c, (b - 1) // c + 1) for (a, b), c in zip(region, self.chunks)]
        for idx in itertools.product(*ranges):
            p = self._key(idx)
            if not p.exists():
                continue
            ch = self._decode(p.read_bytes())
            src, dst = [], []
            for (a, b), c, i in zip(region, self.chunks, idx):
                lo, hi = max(a, i * c), min(b, (i + 1) * c)
                src.append(slice(lo - i * c, hi - i * c))
                dst.append(slice(lo - a, hi - a))
            out[tuple(dst)] = ch[tuple(src)]
        return out

    def read_all(self):
        return self.read([(0, s) for s in self.shape])


def read_array_all(path):
    try:
        return ZArr(path).read_all()
    except NotImplementedError:
        import zarr  # only if a codec is outside the minimal reader
        return np.asarray(zarr.open_array(str(path), mode="r")[:])


def read_geff(geff):
    geff = Path(geff)
    cols = [np.asarray(read_array_all(geff / "nodes" / "props" / k / "values"), np.float64) for k in "tzyx"]
    ids = np.asarray(read_array_all(geff / "nodes" / "ids"))
    edges = np.asarray(read_array_all(geff / "edges" / "ids")).reshape(-1, 2)
    return np.stack(cols, 1), ids, edges


class Volume:
    """One movie's native image: frame(t) -> (Z, Y, X) uint16."""

    def __init__(self, zarr_dir):
        self.root = Path(zarr_dir)
        self.arr = ZArr(self.root / "0")
        if len(self.arr.shape) != 4:
            raise ValueError(f"{self.root}: expected a 4-D (T, Z, Y, X) array, got {self.arr.shape}")

    def frame(self, t):
        T, Z, Y, X = self.arr.shape
        return self.arr.read([(t, t + 1), (0, Z), (0, Y), (0, X)])[0]
'''

CELL_PAIRS = r'''
# ===== capture, SOFT (build.py verbatim), gate-3 pairs + GT edges (zacc.py / zacc3.py verbatim) =====
from scipy.optimize import linear_sum_assignment

CAP_PATH = find_capture()
TRAIN_DIR = find_train_dir()
log(f"capture {CAP_PATH} ({CAP_PATH.stat().st_size / 1e6:.1f} MB); train dir {TRAIN_DIR}")
d = np.load(CAP_PATH, allow_pickle=True)
dets = d["dets"].astype(np.int64)
dm = d["det_movie"]
movies = [str(m) for m in d["movies"]]
n_det = len(dets)
log(f"capture: {n_det} detections, {len(d['gt'])} GT rows, {len(movies)} movies, spacing_um "
    f"{d['spacing_um'].tolist()} voxel_um {d['voxel_um'].tolist()} cand_gate_um {float(d['cand_gate_um'])}")
if not (np.allclose(d["spacing_um"], GRID) and np.allclose(d["voxel_um"], VOX)):
    raise RuntimeError("capture spacing / voxel size differ from the proxy's constants")
CHECKS = {}
FP = EMBED["fp"]
CHECKS["capture_dets_sha1"] = sha1_arr(dets, "<i8") == FP["dets"]
CHECKS["capture_det_movie_sha1"] = sha1_arr(dm, "<i8") == FP["det_movie"]

F_ = d["feats"].astype(np.float64)
w_head = np.array(EMBED["detect_head_w"], dtype=np.float64)
b_head = float(EMBED["detect_head_b"])


def blk(k):
    return F_[:, 32 * k:32 * (k + 1)]


l0 = blk(0) @ w_head + b_head
dl = [blk(k) @ w_head for k in range(1, 7)]  # -z,+z,-y,+y,-x,+x minus centre


def soft1d(a, c, e):
    m = np.maximum(np.maximum(a, c), e)
    ea, ec, ee = np.exp(a - m), np.exp(c - m), np.exp(e - m)
    return (ee - ea) / (ea + ec + ee)


def soft1d_line(ax):
    a = l0 + dl[2 * ax]
    e = l0 + dl[2 * ax + 1]
    s = soft1d(a, l0, e)
    ed = np.all(blk(2 * ax + 1) == 0, 1) | np.all(blk(2 * ax + 2) == 0, 1)
    s[ed] = 0.0
    return s


SOFT = np.stack([soft1d_line(0), soft1d_line(1), soft1d_line(2)], 1)  # gain-1 offsets, grid voxels
del F_
soft_idx = np.array(EMBED["soft_idx"], dtype=np.int64)
if soft_idx.max() < n_det:
    soft_err = float(np.abs(SOFT[soft_idx] - np.array(EMBED["soft_val"])).max())
else:
    soft_err = float("inf")
CHECKS["soft_sample_maxdiff"] = soft_err
CHECKS["soft_match"] = soft_err < 1e-9
log(f"SOFT recomputed from embedded detect_head: mean|off| z {np.abs(SOFT[:, 0]).mean():.4f} "
    f"y {np.abs(SOFT[:, 1]).mean():.4f} x {np.abs(SOFT[:, 2]).mean():.4f}; sample max diff vs proxy {soft_err:.2e}")

pair_det, pair_gt_um, pair_mov, pair_gid = [], [], [], []
gt_edges = {}
GT_SOURCE = {}
for mi, stem in enumerate(movies):
    g = TRAIN_DIR / f"{stem}.geff"
    if g.exists():
        G, gid, E = read_geff(g)
        gt_edges[mi] = E
        GT_SOURCE[stem] = "geff"
    else:  # no geff: capture GT rows, no ids -> no edges for this movie (zacc.py fallback)
        G = d["gt"][d["gt_movie"] == mi]
        gid = -1 - np.arange(len(G))
        gt_edges[mi] = np.zeros((0, 2), np.int64)
        GT_SOURCE[stem] = "capture"
    di = np.flatnonzero(dm == mi)
    for t in np.unique(dets[di, 0]):
        a = di[dets[di, 0] == t]
        bi = np.flatnonzero(G[:, 0].astype(int) == t)
        if not len(bi):
            continue
        A = dets[a, 1:] * GRID
        B = G[bi, 1:] * VOX
        cost = np.linalg.norm(A[:, None] - B[None], axis=2)
        c2 = np.where(cost <= GATE, cost, 1e6)
        r, c = linear_sum_assignment(c2)
        k = cost[r, c] <= GATE
        for i, j in zip(r[k], c[k]):
            pair_det.append(a[i])
            pair_gt_um.append(B[j])
            pair_mov.append(mi)
            pair_gid.append(gid[bi[j]])
P = np.array(pair_det, dtype=np.int64)
GTU = np.array(pair_gt_um, dtype=np.float64)
PM = np.array(pair_mov, dtype=np.int64)
GID = np.array(pair_gid)
emb = np.array([movies[m][:4] for m in PM])
lookup = {(m, g_): i for i, (m, g_) in enumerate(zip(PM.tolist(), GID.tolist()))}
src, dst = [], []
for mi, E in gt_edges.items():
    for u, v in E.tolist():
        iu, iv = lookup.get((mi, u)), lookup.get((mi, v))
        if iu is not None and iv is not None:
            src.append(iu)
            dst.append(iv)
src, dst = np.array(src, dtype=np.int64), np.array(dst, dtype=np.int64)
proxy_idx = np.array([movies.index(s) for s in EMBED["proxy_movies"] if s in movies], dtype=np.int64)
edge_proxy = np.isin(PM[src], proxy_idx) if len(src) else np.zeros(0, bool)
eemb = emb[src] if len(src) else np.zeros(0, "<U4")
CHECKS["pairs_P_sha1"] = sha1_arr(P, "<i8") == FP["P"]
CHECKS["pairs_GTU_sha1"] = sha1_arr(GTU, "<f8") == FP["GTU"]
CHECKS["proxy_src_sha1"] = sha1_arr(src[edge_proxy], "<i8") == FP["src"]
CHECKS["proxy_dst_sha1"] = sha1_arr(dst[edge_proxy], "<i8") == FP["dst"]
n_geff = sum(v == "geff" for v in GT_SOURCE.values())
log(f"pairs {len(P)} (44b6 {np.sum(emb == '44b6')}, 6bba {np.sum(emb == '6bba')}) over {len(np.unique(PM))} movies; "
    f"GT from geff for {n_geff}/{len(movies)} movies")
log(f"GT edges both ends matched: {len(src)} over {len(np.unique(PM[src])) if len(src) else 0} movies "
    f"(44b6 {np.sum(eemb == '44b6')}, 6bba {np.sum(eemb == '6bba')}); proxy-24 subset {int(edge_proxy.sum())} "
    f"(local proxy {FP['n_edges']})")
all_ok = all(bool(v) for k, v in CHECKS.items() if k != "soft_sample_maxdiff")
print("PROXY_REPRO " + " ".join(f"{k}={v}" for k, v in CHECKS.items()) + f" ALL_OK={all_ok}", flush=True)
if EXPECT_PROXY and not all_ok:
    print("PROXY_REPRO WARNING: the rebuilt pairs/edges/SOFT differ from the local proxy; results are still "
          "computed on the rebuilt sets (see flags above)", flush=True)
'''

CELL_CENTROID = r'''
# ===== centroid variants (native voxel units; c0 = (z, 4*y, 4*x) of the grid detection) =====
from scipy.ndimage import gaussian_filter

MAX_SHIFT = np.array([2.0, 8.0, 8.0])  # a run-away estimate (-> neighbour cell) falls back to the grid position


def _axis_w(p, c, half):
    """Partial-pixel box weight: 1 inside |p - c| <= half - 0.5, linear to 0 at half + 0.5."""
    return np.clip(half + 0.5 - np.abs(p - c), 0.0, 1.0)


def cen_box(vol, c0, w, dz=None, iters=1):
    """Intensity-weighted centroid in a box of +-w px (y/x) [and +-dz slices (z)] around the estimate.

    bg = 10th percentile of the window, weights = clip(I - bg, 0).  iters=1: one pass on the integer window
    centred on c0 (exactly +-w px).  iters>1: re-centre on the float estimate with partial-pixel box edges
    (symmetric about the estimate, so a symmetric blob is a fixed point) until the step is < TOL px.
    dz=None: 2-D on the detection's z slice (z shift NaN).  Returns the shift (dz, dy, dx) or None.
    """
    c0 = np.asarray(c0, dtype=np.float64)
    c = c0.copy()
    half = np.array([0.0 if dz is None else dz + 0.5, w + 0.5, w + 0.5])
    zc = int(c0[0])
    for _ in range(max(1, iters)):
        lo = np.floor(c - half).astype(int)
        hi = np.ceil(c + half).astype(int) + 1
        if dz is None:
            lo[0], hi[0] = zc, zc + 1
        lo = np.maximum(lo, 0)
        hi = np.minimum(hi, vol.shape)
        if np.any(hi <= lo):
            return None
        W = vol[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]].astype(np.float64)
        pz, py, px = (np.arange(lo[i], hi[i], dtype=np.float64) for i in range(3))
        wz = np.ones(len(pz)) if dz is None else _axis_w(pz, c[0], half[0])
        box = wz[:, None, None] * _axis_w(py, c[1], half[1])[None, :, None] * _axis_w(px, c[2], half[2])[None, None, :]
        sel = box > 0
        if not sel.any():
            return None
        bg = np.percentile(W[sel], 10.0)
        m = np.clip(W - bg, 0.0, None) * box
        s = m.sum()
        if not s > 0:
            return None
        new = np.array([c0[0] if dz is None else (m.sum((1, 2)) * pz).sum() / s,
                        (m.sum((0, 2)) * py).sum() / s, (m.sum((0, 1)) * px).sum() / s])
        if np.any(np.abs(new - c0) > MAX_SHIFT):
            return None
        step = np.abs(new - c).max()
        c = new
        if step < TOL:
            break
    out = c - c0
    if dz is None:
        out[0] = np.nan
    return out


def cen_gauss(vol, c0, s_yx, s_z=None, iters=None):
    """Gaussian-weighted (mean-shift) centroid: weights = clip(I - p10, 0) * N(p; c, sigma); iterate to the fixed point."""
    iters = MAX_ITER if iters is None else iters
    c0 = np.asarray(c0, dtype=np.float64)
    c = c0.copy()
    R = int(math.ceil(3.0 * s_yx))
    Rz = 0 if s_z is None else int(math.ceil(3.0 * s_z))
    zc = int(c0[0])
    for _ in range(iters):
        ic = np.round(c).astype(int)
        lo = ic - np.array([Rz, R, R])
        hi = ic + np.array([Rz, R, R]) + 1
        if s_z is None:
            lo[0], hi[0] = zc, zc + 1
        lo = np.maximum(lo, 0)
        hi = np.minimum(hi, vol.shape)
        if np.any(hi <= lo):
            return None
        W = vol[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]].astype(np.float64)
        pz, py, px = (np.arange(lo[i], hi[i], dtype=np.float64) for i in range(3))
        gz = np.ones(len(pz)) if s_z is None else np.exp(-0.5 * ((pz - c[0]) / s_z) ** 2)
        g = gz[:, None, None] * np.exp(-0.5 * ((py - c[1]) / s_yx) ** 2)[None, :, None] \
            * np.exp(-0.5 * ((px - c[2]) / s_yx) ** 2)[None, None, :]
        bg = np.percentile(W, 10.0)
        m = np.clip(W - bg, 0.0, None) * g
        s = m.sum()
        if not s > 0:
            return None
        new = np.array([c0[0] if s_z is None else (m.sum((1, 2)) * pz).sum() / s,
                        (m.sum((0, 2)) * py).sum() / s, (m.sum((0, 1)) * px).sum() / s])
        if np.any(np.abs(new - c0) > MAX_SHIFT):
            return None
        step = np.abs(new - c).max()
        c = new
        if step < TOL:
            break
    out = c - c0
    if s_z is None:
        out[0] = np.nan
    return out


def _fit3(a, b, c):
    """Sub-pixel offset of a 3-point peak (b centre): Gaussian (log) fit when all positive, else parabola."""
    if a > 0 and b > 0 and c > 0:
        la, lb, lc = math.log(a), math.log(b), math.log(c)
        den = la - 2.0 * lb + lc
        if den < -1e-12:
            return float(np.clip(0.5 * (la - lc) / den, -0.5, 0.5))
    den = a - 2.0 * b + c
    if den < -1e-12:
        return float(np.clip(0.5 * (a - c) / den, -0.5, 0.5))
    return 0.0


def peak_smooth(vol, c0, sig=(0.7, 1.5, 1.5), search=(1, 4, 4)):
    """Sub-voxel peak of the Gaussian-smoothed native image within +-search of c0, background = crop p10."""
    c0i = np.asarray(c0, dtype=int)
    sig = np.asarray(sig, float)
    search = np.asarray(search, int)
    pad = search + np.ceil(4.0 * sig).astype(int) + 1
    lo = np.maximum(c0i - pad, 0)
    hi = np.minimum(c0i + pad + 1, vol.shape)
    if np.any(hi - lo < 3):
        return None
    crop = vol[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]].astype(np.float64)
    sm = gaussian_filter(crop, sig, mode="nearest", truncate=4.0)
    sm = sm - np.percentile(sm, 10.0)
    rel = c0i - lo
    slo = np.maximum(rel - search, 0)
    shi = np.minimum(rel + search + 1, sm.shape)
    sub = sm[slo[0]:shi[0], slo[1]:shi[1], slo[2]:shi[2]]
    if sub.size == 0 or not np.isfinite(sub).all():
        return None
    p = np.array(np.unravel_index(int(np.argmax(sub)), sub.shape)) + slo
    out = np.zeros(3)
    for ax in range(3):
        if 0 < p[ax] < sm.shape[ax] - 1:
            q = list(p)
            q[ax] = p[ax] - 1
            a = sm[tuple(q)]
            q[ax] = p[ax] + 1
            c = sm[tuple(q)]
            out[ax] = _fit3(a, sm[tuple(p)], c)
    return (p + lo + out) - c0i


VARIANTS = [  # name, kind ('yx' = 2-D, z from elsewhere; 'zyx' = 3-D), function(vol, c0)
    ("A4", "yx", lambda v, c: cen_box(v, c, 4, None, 1)),
    ("A6", "yx", lambda v, c: cen_box(v, c, 6, None, 1)),
    ("A8", "yx", lambda v, c: cen_box(v, c, 8, None, 1)),
    ("A4i", "yx", lambda v, c: cen_box(v, c, 4, None, MAX_ITER)),
    ("A6i", "yx", lambda v, c: cen_box(v, c, 6, None, MAX_ITER)),
    ("A8i", "yx", lambda v, c: cen_box(v, c, 8, None, MAX_ITER)),
    ("G3", "yx", lambda v, c: cen_gauss(v, c, 3.0, None)),
    ("G5", "yx", lambda v, c: cen_gauss(v, c, 5.0, None)),
    ("B4z1", "zyx", lambda v, c: cen_box(v, c, 4, 1, 1)),
    ("B6z1", "zyx", lambda v, c: cen_box(v, c, 6, 1, 1)),
    ("B8z1", "zyx", lambda v, c: cen_box(v, c, 8, 1, 1)),
    ("B4z2", "zyx", lambda v, c: cen_box(v, c, 4, 2, 1)),
    ("B6z2", "zyx", lambda v, c: cen_box(v, c, 6, 2, 1)),
    ("B8z2", "zyx", lambda v, c: cen_box(v, c, 8, 2, 1)),
    ("B6z1i", "zyx", lambda v, c: cen_box(v, c, 6, 1, MAX_ITER)),
    ("B6z2i", "zyx", lambda v, c: cen_box(v, c, 6, 2, MAX_ITER)),
    ("G4z15", "zyx", lambda v, c: cen_gauss(v, c, 4.0, 1.5)),
    ("D", "zyx", lambda v, c: peak_smooth(v, c)),
]
VNAMES = [v[0] for v in VARIANTS]
VKIND = {v[0]: v[1] for v in VARIANTS}


def blob_volume(shape, centre, sig=(1.5, 4.5, 4.5), amp=800.0, bg=150.0, noise=0.0, seed=0):
    zz, yy, xx = np.meshgrid(*[np.arange(s, dtype=np.float64) for s in shape], indexing="ij")
    v = bg + amp * np.exp(-0.5 * (((zz - centre[0]) / sig[0]) ** 2 + ((yy - centre[1]) / sig[1]) ** 2
                                  + ((xx - centre[2]) / sig[2]) ** 2))
    if noise > 0:
        v = v + np.random.default_rng(seed).normal(0.0, noise, v.shape)
    return np.clip(np.round(v), 0, 65535).astype(np.uint16)


def selftest(noise=0.0):
    """Gaussian blob at a known sub-pixel position; start at the grid position the detector would report."""
    centre = np.array([10.3, 40.37, 33.81])
    vol = blob_volume((24, 96, 96), centre, noise=noise)
    c0 = np.array([round(centre[0]), 4 * round(centre[1] / 4), 4 * round(centre[2] / 4)])
    res = {}
    for name, kind, fn in VARIANTS:
        sh = fn(vol, c0)
        if sh is None:
            res[name] = None
            continue
        est = c0 + np.nan_to_num(sh)
        err = np.abs(est - centre)
        res[name] = {"err_y": float(err[1]), "err_x": float(err[2]),
                     "err_z": float(err[0]) if kind == "zyx" else None}
    return centre, c0, res


_c, _c0, _st = selftest()
print(f"NATIVECEN_SELFTEST blob at {_c.tolist()} start {_c0.tolist()} (errors in native px, noise-free):", flush=True)
for _n, _r in _st.items():
    print(f"  {_n:<6} " + ("FAILED" if _r is None else " ".join(
        f"{k}={v:.4f}" for k, v in _r.items() if v is not None)), flush=True)
'''

CELL_LOOP = r'''
# ===== main loop: every captured detection, per movie (proxy-24 movies first), wall-clock guarded =====
SH = np.full((len(VARIANTS), n_det, 3), np.nan, dtype=np.float32)
FAIL = np.zeros((len(VARIANTS), n_det), dtype=bool)
done = np.zeros(n_det, dtype=bool)
VTIME = np.zeros(len(VARIANTS))
pair_of_det = np.full(n_det, -1, dtype=np.int64)
pair_of_det[P] = np.arange(len(P))
order = [int(m) for m in proxy_idx] + [m for m in range(len(movies)) if m not in set(proxy_idx.tolist())]
MOVIE_STATUS = {}
LAYOUT = {}
yx_rank, yx_rank_sw = [], []
rng_order = np.random.default_rng(1)
stopped = False
for k_m, mi in enumerate(order):
    stem = movies[mi]
    if elapsed() > BUDGET_S:
        print(f"NATIVECEN_BUDGET_STOP before movie {k_m + 1}/{len(order)} {stem} at {elapsed():.0f}s", flush=True)
        stopped = True
        break
    zdir = TRAIN_DIR / f"{stem}.zarr"
    if not (zdir / "0" / "zarr.json").exists():
        MOVIE_STATUS[stem] = "no_zarr"
        log(f"NATIVECEN_MOVIE {k_m + 1}/{len(order)} {stem} SKIPPED (no {zdir.name}/0/zarr.json)")
        continue
    t_m = time.time()
    try:
        vol_m = Volume(zdir)
    except Exception as exc:  # noqa: BLE001
        MOVIE_STATUS[stem] = f"open_failed {type(exc).__name__}: {exc}"
        log(f"NATIVECEN_MOVIE {stem} OPEN FAILED {type(exc).__name__}: {exc}")
        continue
    if not LAYOUT:
        rootj = zdir / "zarr.json"
        LAYOUT = {"stem": stem, "array_meta": vol_m.arr.meta,
                  "group_attrs": json.loads(rootj.read_text()).get("attributes", {}) if rootj.exists() else None}
        print("NATIVECEN_LAYOUT array " + json.dumps({k: vol_m.arr.meta.get(k) for k in (
            "shape", "data_type", "chunk_grid", "chunk_key_encoding", "codecs", "dimension_names", "fill_value")}),
            flush=True)
        ga = LAYOUT["group_attrs"] or {}
        print("NATIVECEN_LAYOUT group attrs " + json.dumps(ga)[:1500], flush=True)
    shape = vol_m.arr.shape
    LAYOUT.setdefault("shapes", {})[stem] = list(shape)
    if shape[1] != 64 or shape[2] != 4 * 64 or shape[3] != 4 * 64:
        log(f"NATIVECEN WARNING {stem} shape {shape} (expected (T, 64, 256, 256) for grid 64^3 x (1,4,4))")
    di = np.flatnonzero(dm == mi)
    n_frames = 0
    t_read = 0.0
    read_err = None
    for t in np.unique(dets[di, 0]):
        a = di[dets[di, 0] == t]
        t_r = time.time()
        try:
            vol = vol_m.frame(int(t))
        except Exception as exc:  # noqa: BLE001 - keep the reference arms / other movies alive
            read_err = f"{type(exc).__name__}: {exc}"
            print(f"NATIVECEN_READ_FAILED {stem} t={t} {read_err}", flush=True)
            break
        t_read += time.time() - t_r
        n_frames += 1
        for i in a:
            c0 = (int(dets[i, 1]), 4 * int(dets[i, 2]), 4 * int(dets[i, 3]))
            for vi, (name, kind, fn) in enumerate(VARIANTS):
                t_v = time.time()
                try:
                    sh = fn(vol, c0)
                except Exception:  # noqa: BLE001
                    sh = None
                VTIME[vi] += time.time() - t_v
                if sh is None:
                    FAIL[vi, i] = True
                else:
                    SH[vi, i] = sh
            done[i] = True
        # y/x axis-order evidence on the first frames of each movie: intensity rank at the GT voxel vs y<->x swapped
        if n_frames <= 5:
            pi = pair_of_det[a]
            pi = pi[pi >= 0]
            if len(pi):
                ref = np.sort(vol.ravel()[rng_order.integers(0, vol.size, 20000)].astype(np.float64))
                g_ = np.round(GTU[pi] / VOX).astype(int)
                g_ = np.clip(g_, 0, np.array(vol.shape) - 1)
                ok_sw = (g_[:, 2] < vol.shape[1]) & (g_[:, 1] < vol.shape[2])
                yx_rank.extend((np.searchsorted(ref, vol[g_[:, 0], g_[:, 1], g_[:, 2]].astype(np.float64)) / len(ref)).tolist())
                gs = g_[ok_sw]
                yx_rank_sw.extend((np.searchsorted(ref, vol[gs[:, 0], gs[:, 2], gs[:, 1]].astype(np.float64)) / len(ref)).tolist())
        if elapsed() > BUDGET_S + 600:
            print(f"NATIVECEN_BUDGET_HARD_STOP inside {stem} at t={t}", flush=True)
            stopped = True
            break
    MOVIE_STATUS[stem] = f"read_failed {read_err}" if read_err else ("done" if not stopped else "partial")
    log(f"NATIVECEN_MOVIE {k_m + 1}/{len(order)} {stem} dets={len(di)} frames={n_frames} read={t_read:.1f}s "
        f"total={time.time() - t_m:.1f}s decoders={DECODERS_USED}")
    if stopped:
        break
n_done_m = sum(v == "done" for v in MOVIE_STATUS.values())
log(f"loop finished: movies done {n_done_m}/{len(movies)}, detections done {int(done.sum())}/{n_det}; "
    f"variant seconds " + " ".join(f"{n}={t:.0f}" for n, t in zip(VNAMES, VTIME)))
if yx_rank:
    print(f"NATIVECEN_YXORDER GT-voxel intensity rank median {np.median(yx_rank):.3f} (n={len(yx_rank)}) vs y<->x "
          f"swapped {np.median(yx_rank_sw):.3f} (n={len(yx_rank_sw)}); frac rank>0.8: "
          f"{np.mean(np.array(yx_rank) > 0.8):.3f} vs {np.mean(np.array(yx_rank_sw) > 0.8):.3f}", flush=True)
for vi, name in enumerate(VNAMES):
    m = done
    print(f"  variant {name:<6} fail/fallback rate {FAIL[vi, m].mean() if m.any() else float('nan'):.4f}", flush=True)
np.savez_compressed(WORKING / "nativecen_shifts.npz", variants=np.array(VNAMES), SH=SH, FAIL=FAIL, done=done,
                    dets=dets.astype(np.int16), det_movie=dm, movies=np.array(movies), SOFT=SOFT.astype(np.float32),
                    P=P, GTU=GTU, PM=PM, emb=emb, src=src, dst=dst, edge_proxy=edge_proxy)
log(f"saved {WORKING / 'nativecen_shifts.npz'}")
'''

CELL_METRICS = r'''
# ===== metrics: tails on GT edges, per-detection errors, movie bootstrap vs SV (t6stk3) =====
VI = {n: i for i, n in enumerate(VNAMES)}
CLIPS = {"step": (1.0, 4.0), "half": (0.4999, 2.0)}  # native-shift clip (z slices, y/x px)
BASE_UM = dets[:, 1:].astype(np.float64) * GRID
SV_UM = np.clip(SOFT * SV_GAIN, -SV_CLIP, SV_CLIP) * GRID


def src_off(source, axes, clip):
    """um offsets (n_det, len(axes)) of a z or y/x source: 'grid', 'sv' or a native variant name."""
    if source == "grid":
        return np.zeros((n_det, len(axes)))
    if source == "sv":
        return SV_UM[:, axes]
    sh = np.nan_to_num(SH[VI[source]][:, axes].astype(np.float64))
    lim = np.array([CLIPS[clip][0] if a == 0 else CLIPS[clip][1] for a in axes])
    return np.clip(sh, -lim, lim) * VOX[axes]


def arm_pos(yx, z, clip):
    pos = BASE_UM.copy()
    pos[:, [0]] += src_off(z, [0], clip)
    pos[:, [1, 2]] += src_off(yx, [1, 2], clip)
    return pos


ARMS = [("zero", "grid", "grid"), ("sv_z2yx2_t6stk3", "sv", "sv"), ("sv_z0yx2_t6svyx", "sv", "grid"),
        ("sv_z2yx0_t6svz0yx", "grid", "sv")]
for name, kind, _ in VARIANTS:
    if kind == "yx":
        ARMS += [(f"{name}|z0", name, "grid"), (f"{name}|zSV", name, "sv")]
    else:
        ARMS += [(f"{name}|zN", name, name), (f"{name}|zSV", name, "sv"), (f"{name}z|yxSV", "sv", name)]
REF = "sv_z2yx2_t6stk3"
TH = (2.0, 3.0, 4.0)
EMBS = ("44b6", "6bba")


def boot_weights(emov, seed=12345):
    """Movie-bootstrap count matrices (stratified by embryo), shared by all arms of one edge set."""
    mv = np.unique(emov)
    mv_emb = np.array([movies[m][:4] for m in mv])
    rng = np.random.default_rng(seed)
    out = {}
    for scope in EMBS + ("all",):
        Wb = np.zeros((N_BOOT, len(mv)))
        strata = EMBS if scope == "all" else (scope,)
        for e in strata:
            idx = np.flatnonzero(mv_emb == e)
            if not len(idx):
                continue
            draws = idx[rng.integers(0, len(idx), size=(N_BOOT, len(idx)))]
            np.add.at(Wb, (np.repeat(np.arange(N_BOOT), len(idx)), draws.ravel()), 1.0)
        out[scope] = Wb
    return mv, out


def evaluate(set_name, emask, clip):
    """All arms on the edges in emask (both ends done) and the pairs of those movies."""
    es = np.flatnonzero(emask)
    if not len(es):
        print(f"[{set_name}/{clip}] no edges with both ends processed; skipped", flush=True)
        return []
    s_, d_ = src[es], dst[es]
    true_disp = GTU[d_] - GTU[s_]
    em = eemb[es]
    emov = PM[s_]
    mv, WB = boot_weights(emov)
    inv = np.searchsorted(mv, emov)
    pm = done[P] & np.isin(PM, np.unique(emov))
    r3 = {}
    for name, yx, z in ARMS:
        if (yx not in ("grid", "sv") and yx not in VI) or (z not in ("grid", "sv") and z not in VI):
            continue
        pos = arm_pos(yx, z, clip)
        e = (pos[P[d_]] - pos[P[s_]]) - true_disp
        r3[name] = (np.sqrt((e ** 2).sum(1)), pos)
    rows = []
    ref_r = r3[REF][0]
    for name, (rr, pos) in r3.items():
        row = {"set": set_name, "clip": clip, "arm": name}
        for scope in EMBS + ("all",):
            sel = np.ones(len(es), bool) if scope == "all" else (em == scope)
            row[f"n_{scope}"] = int(sel.sum())
            for t in TH:
                row[f"tail{t:g}_{scope}"] = float(np.mean(rr[sel] > t)) if sel.any() else float("nan")
            for t in TH:
                di_ = (rr > t).astype(float) - (ref_r > t)
                S = np.bincount(inv, weights=di_ * sel, minlength=len(mv))
                N = np.bincount(inv, weights=sel.astype(float), minlength=len(mv))
                pt = float(S.sum() / N.sum()) if N.sum() else float("nan")
                with np.errstate(invalid="ignore", divide="ignore"):
                    bs = (WB[scope] @ S) / (WB[scope] @ N)
                lo, hi = np.nanpercentile(bs, [5, 95]) if np.isfinite(bs).any() else (np.nan, np.nan)
                row[f"d{t:g}_{scope}"], row[f"d{t:g}_{scope}_lo"], row[f"d{t:g}_{scope}_hi"] = pt, float(lo), float(hi)
            if scope == "all":
                row["flip3_better"] = int(np.sum((rr <= 3.0) & (ref_r > 3.0)))
                row["flip3_worse"] = int(np.sum((rr > 3.0) & (ref_r <= 3.0)))
                row["rmse_all"] = float(np.sqrt(np.mean(rr ** 2)))
        for scope in EMBS:
            ps = pm & (emb == scope)
            err = pos[P[ps]] - GTU[ps]
            for ax, an in enumerate("zyx"):
                row[f"mae_{an}_{scope}"] = float(np.abs(err[:, ax]).mean()) if ps.any() else float("nan")
                row[f"bias_{an}_{scope}"] = float(err[:, ax].mean()) if ps.any() else float("nan")
        yx_src = next(a[1] for a in ARMS if a[0] == name)
        z_src = next(a[2] for a in ARMS if a[0] == name)
        fr = [FAIL[VI[s]][P[pm]].mean() for s in {yx_src, z_src} if s in VI]
        row["fallback"] = float(max(fr)) if fr else 0.0
        rows.append(row)
    return rows


def fmt_ci(r, key):
    return f"{r[key]:+.4f}[{r[key + '_lo']:+.4f},{r[key + '_hi']:+.4f}]"


def print_table(rows, marker):
    if not rows:
        return
    r0 = rows[0]
    print(f"\n==== {marker} set={r0['set']} clip={r0['clip']}  edges 44b6 {r0['n_44b6']} 6bba {r0['n_6bba']} "
          f"(movies with both ends processed)  diffs vs {REF}, movie bootstrap 90% ====", flush=True)
    print(f"{'arm':<22}{'t3_44b6':>8}{'t3_6bba':>8}{'t3_all':>8}{'t2_all':>8}{'t4_all':>8}  {'d3_44b6 [90%]':<27}"
          f"{'d3_6bba [90%]':<27}{'d3_all [90%]':<27}{'+/-':>8}{'maeYX44':>8}{'maeYX6b':>8}{'maeZ44':>7}{'maeZ6b':>7}",
          flush=True)
    for r in rows:
        mae44 = 0.5 * (r["mae_y_44b6"] + r["mae_x_44b6"])
        mae6b = 0.5 * (r["mae_y_6bba"] + r["mae_x_6bba"])
        print(f"{r['arm']:<22}{r['tail3_44b6']:8.4f}{r['tail3_6bba']:8.4f}{r['tail3_all']:8.4f}{r['tail2_all']:8.4f}"
              f"{r['tail4_all']:8.4f}  {fmt_ci(r, 'd3_44b6'):<27}{fmt_ci(r, 'd3_6bba'):<27}{fmt_ci(r, 'd3_all'):<27}"
              f"{r['flip3_better']:>4}/{r['flip3_worse']:<3}{mae44:8.3f}{mae6b:8.3f}{r['mae_z_44b6']:7.3f}"
              f"{r['mae_z_6bba']:7.3f}", flush=True)
    for r in rows:
        print(f"{marker} {r['arm']} set={r['set']} clip={r['clip']} "
              f"tail3_44b6={r['tail3_44b6']:.4f} tail3_6bba={r['tail3_6bba']:.4f} tail3_all={r['tail3_all']:.4f} "
              f"tail2_44b6={r['tail2_44b6']:.4f} tail2_6bba={r['tail2_6bba']:.4f} "
              f"tail4_44b6={r['tail4_44b6']:.4f} tail4_6bba={r['tail4_6bba']:.4f} "
              f"d3_44b6={fmt_ci(r, 'd3_44b6')} d3_6bba={fmt_ci(r, 'd3_6bba')} d3_all={fmt_ci(r, 'd3_all')} "
              f"d2_all={fmt_ci(r, 'd2_all')} d4_all={fmt_ci(r, 'd4_all')} flips3=+{r['flip3_better']}/-{r['flip3_worse']} "
              f"mae_zyx_44b6={r['mae_z_44b6']:.3f}/{r['mae_y_44b6']:.3f}/{r['mae_x_44b6']:.3f} "
              f"mae_zyx_6bba={r['mae_z_6bba']:.3f}/{r['mae_y_6bba']:.3f}/{r['mae_x_6bba']:.3f} "
              f"n_edges={r['n_44b6']}/{r['n_6bba']} fallback={r['fallback']:.4f}", flush=True)


# ---- reference arms on the FULL rebuilt edge sets (independent of the image loop) = proxy cross-check
print("\n==== REFERENCE arms on the full rebuilt edge sets (no image needed) ====", flush=True)
ref_rows = []
for set_name, emask in (("proxy24", edge_proxy), ("all60", np.ones(len(src), bool))):
    for name, yx, z in ARMS[:4]:
        pos = arm_pos(yx, z, "step")
        es = np.flatnonzero(emask)
        e = (pos[P[dst[es]]] - pos[P[src[es]]]) - (GTU[dst[es]] - GTU[src[es]])
        rr = np.sqrt((e ** 2).sum(1))
        vals = {sc: float(np.mean(rr[eemb[es] == sc] > 3.0)) if np.any(eemb[es] == sc) else float("nan") for sc in EMBS}
        exp = EMBED["ref_tail3"].get(name) if set_name == "proxy24" else None
        print(f"REF {set_name:<8} {name:<20} tail3 44b6 {vals['44b6']:.4f} 6bba {vals['6bba']:.4f} all "
              f"{np.mean(rr > 3.0):.4f}  n {int((eemb[es] == '44b6').sum())}/{int((eemb[es] == '6bba').sum())}"
              + (f"   (local proxy {exp[0]:.4f}/{exp[1]:.4f})" if exp else ""), flush=True)
        ref_rows.append({"set": set_name, "arm": name, **{f"tail3_{k}": v for k, v in vals.items()}})

# ---- grid -> native mapping evidence (pairs of processed movies)
pm_all = done[P]
if pm_all.any():
    nat_gt = GTU / VOX
    for sc in EMBS:
        ps = pm_all & (emb == sc)
        if not ps.any():
            continue
        res = nat_gt[ps] - dets[P[ps], 1:] * DS
        line = f"NATIVECEN_MAPPING {sc} n={int(ps.sum())} mean(GT_native - DS*grid) z/y/x {res.mean(0).round(3).tolist()}"
        for off in (-1.5, -0.5, 0.0, 0.5, 1.5):
            line += f" | yx MAE@off{off:+.1f} {np.abs(res[:, 1:] - off).mean():.3f}"
        print(line, flush=True)
        for vn in ("A6i", "G3", "B6z2i", "G4z15", "D"):
            sh = SH[VI[vn]][P[ps]].astype(np.float64)
            ok = ~FAIL[VI[vn]][P[ps]]
            cc = [np.corrcoef(sh[ok, a], res[ok, a])[0, 1] if np.isfinite(sh[ok, a]).all() and ok.sum() > 2 else float("nan")
                  for a in range(3)]
            print(f"   {vn:<6} mean shift z/y/x {np.nanmean(sh[ok], 0).round(3).tolist()}  corr(shift, GT residual) "
                  f"z/y/x {np.round(cc, 3).tolist()}  mean|residual - shift| y/x "
                  f"{np.abs(res[ok, 1:] - np.clip(sh[ok, 1:], -4, 4)).mean():.3f} (grid {np.abs(res[ok, 1:]).mean():.3f}, "
                  f"SV g2 {np.abs(res[ok, 1:] - SV_UM[P[ps]][ok, 1:] / VOX[1:]).mean():.3f})", flush=True)

ALL_ROWS = []
both = done[P[src]] & done[P[dst]] if len(src) else np.zeros(0, bool)
for clip in ("step", "half"):
    for set_name, emask, marker in (("all60", both, "NATIVECEN" if clip == "step" else "NATIVECEN_HALF"),
                                    ("proxy24", both & edge_proxy, "NATIVECEN_P24" if clip == "step" else "NATIVECEN_P24_HALF")):
        rows = evaluate(set_name, emask, clip)
        print_table(rows, marker)
        ALL_ROWS += rows

if ALL_ROWS:
    main = [r for r in ALL_ROWS if r["set"] == "all60" and r["clip"] == "step"]
    top = sorted(main, key=lambda r: r["d3_all"])[:12]
    print("\n==== TOP arms by pooled d3 vs t6stk3 (all60, clip step; negative = fewer > 3 um edge errors) ====", flush=True)
    for r in top:
        print(f"TOP {r['arm']:<22} d3_all {fmt_ci(r, 'd3_all')}  d3_44b6 {fmt_ci(r, 'd3_44b6')}  "
              f"d3_6bba {fmt_ci(r, 'd3_6bba')}  flips +{r['flip3_better']}/-{r['flip3_worse']}", flush=True)
    keys = list(ALL_ROWS[0].keys())
    with open(WORKING / "nativecen_table.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=keys)
        wr.writeheader()
        wr.writerows(ALL_ROWS)
    log(f"saved {WORKING / 'nativecen_table.csv'} ({len(ALL_ROWS)} rows)")


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    return o


summary = {"checks": CHECKS, "capture": str(CAP_PATH), "train_dir": str(TRAIN_DIR), "decoders": DECODERS_USED,
           "layout": LAYOUT, "movie_status": MOVIE_STATUS, "gt_source": GT_SOURCE,
           "n_pairs": int(len(P)), "n_edges": int(len(src)), "n_edges_proxy24": int(edge_proxy.sum()),
           "detections_done": int(done.sum()), "variant_seconds": dict(zip(VNAMES, VTIME.tolist())),
           "yx_order": {"gt_rank_median": float(np.median(yx_rank)) if yx_rank else None,
                        "swapped_rank_median": float(np.median(yx_rank_sw)) if yx_rank_sw else None},
           "selftest": _st, "reference_rows": ref_rows, "rows": ALL_ROWS, "seconds": elapsed()}
(WORKING / "nativecen_summary.json").write_text(json.dumps(_jsonable(summary), indent=1))
log(f"saved {WORKING / 'nativecen_summary.json'}; NATIVECEN_DONE")
'''

CELLS = [CELL_CONFIG, CELL_ZARR, CELL_PAIRS, CELL_CENTROID, CELL_LOOP, CELL_METRICS]


def sha1_arr(a, dtype):
    return hashlib.sha1(np.ascontiguousarray(np.asarray(a).astype(dtype)).tobytes()).hexdigest()


def make_embed():
    import torch

    sd = torch.load(CK, map_location="cpu", weights_only=False)
    w = sd["detect_head.weight"].reshape(32).double().numpy()
    b = float(sd["detect_head.bias"].reshape(-1)[0])
    d = np.load(CAP, allow_pickle=True)
    c = np.load(CACHE, allow_pickle=True)
    dets = d["dets"].astype(np.int64)
    if not np.array_equal(c["dets"].astype(np.int64), dets):
        raise SystemExit("proxy cache dets differ from the local capture npz")
    # SOFT rebuilt here must equal the proxy cache (sanity of the embedded weights)
    F_ = d["feats"].astype(np.float64)

    def blk(k):
        return F_[:, 32 * k:32 * (k + 1)]

    l0 = blk(0) @ w + b
    dl = [blk(k) @ w for k in range(1, 7)]

    def soft1d(a, cc, e):
        m = np.maximum(np.maximum(a, cc), e)
        ea, ec, ee = np.exp(a - m), np.exp(cc - m), np.exp(e - m)
        return (ee - ea) / (ea + ec + ee)

    def line(ax):
        s = soft1d(l0 + dl[2 * ax], l0, l0 + dl[2 * ax + 1])
        s[np.all(blk(2 * ax + 1) == 0, 1) | np.all(blk(2 * ax + 2) == 0, 1)] = 0.0
        return s

    SOFT = np.stack([line(0), line(1), line(2)], 1)
    err = float(np.abs(SOFT - c["SOFT"]).max())
    if err > 1e-9:
        raise SystemExit(f"embedded detect_head does not reproduce the proxy SOFT (max diff {err})")
    soft_idx = np.linspace(0, len(dets) - 1, 101).astype(np.int64)
    P, GTU, PM, src, dst, emb = c["P"], c["GTU"], c["PM"], c["src"], c["dst"], c["emb"]
    movies = [str(m) for m in c["movies"]]
    proxy = sorted({movies[m] for m in PM[src].tolist()}, key=movies.index)
    # reference tails (local proxy) for the cross-check print
    ref = {}
    arms = {"zero": (0, 0), "sv_z2yx2_t6stk3": (2, 2), "sv_z0yx2_t6svyx": (0, 2), "sv_z2yx0_t6svz0yx": (2, 0)}
    td = GTU[dst] - GTU[src]
    ee = emb[src]
    for name, (gz, gyx) in arms.items():
        off = np.clip(SOFT * np.array([gz, gyx, gyx]), -0.4999, 0.4999)
        pos = dets[:, 1:] * GRID + off * GRID
        r = np.linalg.norm((pos[P[dst]] - pos[P[src]]) - td, axis=1)
        ref[name] = [float(np.mean(r[ee == "44b6"] > 3)), float(np.mean(r[ee == "6bba"] > 3))]
    embed = {
        "detect_head_w": [float(v) for v in w], "detect_head_b": b,
        "fp": {"dets": sha1_arr(dets, "<i8"), "det_movie": sha1_arr(d["det_movie"], "<i8"),
               "P": sha1_arr(P, "<i8"), "GTU": sha1_arr(GTU, "<f8"), "src": sha1_arr(src, "<i8"),
               "dst": sha1_arr(dst, "<i8"), "n_pairs": int(len(P)), "n_edges": int(len(src))},
        "soft_idx": soft_idx.tolist(), "soft_val": SOFT[soft_idx].tolist(),
        "proxy_movies": proxy, "ref_tail3": ref,
    }
    print(f"embed: detect_head w|b ok (SOFT max diff vs proxy {err:.1e}); pairs {len(P)} edges {len(src)} "
          f"proxy movies {len(proxy)}; ref tails {ref}")
    return embed


def build():
    embed = make_embed()
    ej = json.dumps(embed, separators=(",", ":"))
    if '"""' in ej or "\\" in ej:
        raise SystemExit("embed json would break the raw string")
    cells = [c.strip(NL) + NL for c in CELLS]
    cells[0] = cells[0].replace("@@EMBED@@", ej)
    for i, c in enumerate(cells):
        compile(c, f"{TAG}:cell{i}", "exec")
    nb = {
        "cells": [{"cell_type": "code", "execution_count": None, "id": f"nativecen-{i}", "metadata": {},
                   "outputs": [], "source": c.splitlines(keepends=True)} for i, c in enumerate(cells)],
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python", "version": "3.12"}},
        "nbformat": 4, "nbformat_minor": 5,
    }
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "kernel.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
    meta = {
        "id": "eeshsaxena/biohub-v-" + TAG, "title": "biohub v " + TAG, "code_file": "kernel.ipynb",
        "language": "python", "kernel_type": "notebook", "is_private": True, "enable_gpu": False,
        "enable_tpu": False, "enable_internet": False, "dataset_sources": [],
        "kernel_sources": ["eeshsaxena/biohub-v-v1284cap"],
        "competition_sources": ["biohub-cell-tracking-during-development"], "model_sources": [], "keywords": [],
    }
    (DEST / "kernel-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    size = (DEST / "kernel.ipynb").stat().st_size
    print(f"built {DEST} ({len(cells)} cells, kernel.ipynb {size / 1e3:.0f} kB)")
    return DEST


if __name__ == "__main__":
    sys.exit(0 if build() else 1)
