"""Optimized detection override for the Kunal 0.917 pipeline (runtime headroom).

Drop-in replacement for cell-3 `detect`. Two changes, both aimed at cutting the
detection wall-clock (which dominates runtime) so recall levers (aggressive fill,
union) fit under the 12h cap:

  1. BATCH the 4 flip-TTA views into ONE forward per model. Numerically identical:
     BatchNorm3d in eval() uses running stats, so per-sample outputs don't depend
     on batch size. Fewer kernel launches + Python overhead.
  2. fp16 AUTOCAST on CUDA. ~2x faster conv3d on T4; heatmap shifts ~1e-3, well
     below the 0.15 seed threshold. MUST be recall-verified on Kaggle before use.

Falls back to the exact fp32 per-flip path on any error (OOM etc.), so it can
never do worse than the baseline. Verify recall-equivalence + speedup in the CV
harness (add as a detect variant) before folding into a submission.
"""

OPT_DETECT = r'''
# ============ OPTIMIZED DETECT (batched flip-TTA + fp16) ============
_detect_ref = detect  # keep exact baseline for fallback / A-B

def _detect_opt(vol):
    hs = []
    for models, ws, pp in _BRANCHES:
        x = pool_norm(vol, pp)
        views = np.stack([np.ascontiguousarray(_flip(x, i)) for i in _FLIP_VIEWS])  # (V,Z,Y,X)
        xb = torch.from_numpy(views)[:, None].to(DEVICE)                            # (V,1,Z,Y,X)
        with torch.no_grad():
            if DEVICE == "cuda":
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    lg = None
                    for m, w in zip(models, ws):
                        l = m(xb)[:, 0]
                        lg = w * l if lg is None else lg + w * l
            else:
                lg = None
                for m, w in zip(models, ws):
                    l = m(xb)[:, 0]
                    lg = w * l if lg is None else lg + w * l
        lg = lg.float().cpu().numpy()                                               # (V,Z,Y,X)
        acc = None
        for vi, i in enumerate(_FLIP_VIEWS):
            li = _flip(lg[vi], i)
            acc = li if acc is None else acc + li
        hs.append(1.0 / (1.0 + np.exp(-(acc / len(_FLIP_VIEWS)))))
    h = hs[0] if len(hs) == 1 else np.mean(hs, axis=0)
    pk = peak_local_max(h, min_distance=1, threshold_abs=DETECT_THRESH, exclude_border=False)
    if len(pk) == 0:
        return np.zeros((0, 3)), np.zeros(0)
    sc = h[pk[:, 0], pk[:, 1], pk[:, 2]].astype(float)
    coords = pk.astype(float)
    coords[:, 1] = coords[:, 1] * POOL + (POOL - 1) / 2
    coords[:, 2] = coords[:, 2] * POOL + (POOL - 1) / 2
    ref = np.array([_refine(vol, c)[0] for c in coords])
    return _physical_nms(ref, sc, NMS_UM)

def detect(vol):
    try:
        return _detect_opt(vol)
    except Exception as e:
        print("opt-detect fell back to baseline:", str(e)[:80])
        return _detect_ref(vol)
'''
