#!/usr/bin/env python3
"""t6stk3 body + TRILINEAR UNet feature gather at the lcefr-refined coordinates (arm "gtri").

usage: python scratch_kernels/build_t6gtri.py <tag> --axes zyx|z
       (t6gtri = --axes zyx, t6gtriz = --axes z)

WHY (geometry-consumer audit, 09-26). After lcefr, every CONTINUOUS geometry input of the linker reads the
sub-voxel-refined positions (sinusoidal pos embedding, predict_edges forward / reverse / secondary displacement,
edge dist) and cell 5 is float end to end (relink, gap close, gap2, safe-division geometry, line-fit). The last
population-scale INTEGER read is the UNet feature gather: `_index_features` samples the 32-channel UNet map at the
integer detector peak for the primary src/tgt and the secondary src/tgt of EVERY frame pair. The board said the
z channel is worth ~6 ticks because integer z makes a cell's geometry jump a whole 1.625 um grid step when it drifts
across a voxel boundary (tail effect). The appearance features still make that jump. This arm replaces the four
gathers with a trilinear lookup at the SAME refined coordinates lcefr already feeds the geometry inputs
(|offset| <= 0.4999 voxel), i.e. it completes lcefr. Deterministic, no learned parameters.
  --axes zyx : trilinear in z, y and x.
  --axes z   : trilinear in z only (y/x stay on the integer peak) - the smaller perturbation, aimed at the
               z-dominated displacement tail.
RISK. The edge model was TRAINED on integer-peak gathers (train_unet_transformer.py detect_and_match +
_index_features), so interpolated features are slightly out of distribution. Nearest public evidence: the V1284
package (learned coords + the same trilinear lookup) was +2 on the x138 body and -3 on ours (confounded with V1284's
coordinates and no lcefr); ourvz / ourvzl (trilinear y/x gather) scores refine that prior.

Mechanics (appended to cell 4 AFTER the lcefr block; anchors asserted here against the REAL t6stk3-patched
predictor from the Kaggle run, and again at notebook runtime):
  * module helper `_gt_gather(model, maps, rcoords, icoords, mask)`: native gather at the integer peaks, then a
    trilinear lookup at the refined coords; the FIRST call asserts trilinear(integer peaks) == native gather
    (axis-order / convention guard, raises ARM_GTRI SELFCHECK FAILED);
  * the four call sites `model._index_features(unet_out[...], p_coords_*, p_mask_*)` and the two secondary ones
    call `_gt_gather(..., p_rcoords_*, p_coords_*, ...)`;
  * NO-OP guard: raises if the gathered features never differ from the integer-peak features;
  * per movie: `ARM_GTRI_STATS axes=.. calls=.. nodes=.. mean_abs_feat_delta=.. selfcheck=1` (cumulative);
  * FREE DIAGNOSTIC (read-only): `ARM_GTRI_XWIN src_nodes=.. src_offpeak=..` = source-frame nodes (t >= 1) whose
    integer peak (detected in window [t-1, t]) is NOT a 3x3x3 local max of the detection logits of the window
    [t, t+1] whose UNet features the pair (t, t+1) gathers from. Quantifies the cross-window peak mismatch.
Final coordinates, detection, thresholds, ILP inputs other than edge_prob, and cell 5 are untouched.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
REAL = ROOT / "data" / "out_t6stk3" / "tracking_repo" / "scripts" / "predict_unet_transformer.py"
NL = chr(10)

CELL4_ANCHOR = ("print('ARM_LCEFR patch applied to', _ps, '| linker reads refined coords, gather stays integer', "
                "flush=True)\n")

BLOCK = r'''

# ===== TRILINEAR UNet FEATURE GATHER AT THE REFINED COORDINATES (arm gtri) =====
# lcefr fed the refined (float) positions to every continuous geometry input of the linker but left the four UNet
# feature gathers on the integer peak. Replace them with a trilinear lookup at the SAME refined coordinates.
# Axes per BIOHUB_GTRI_AXES ('zyx' or 'z'; for 'z' the y/x lookup stays on the integer peak).
os.environ['BIOHUB_GTRI_AXES'] = '__AXES__'
print('ARM_GTRI axes=__AXES__ (trilinear UNet gather at the lcefr-refined coords, 4 call sites)', flush=True)
_gt_s = _ps.read_text()
_GT_HELPER = """_GT_AXES = os.environ.get('BIOHUB_GTRI_AXES', '')
_GT_STATS = {'calls': 0, 'nodes': 0, 'sum_abs_delta': 0.0, 'n_delta': 0, 'selfcheck': 0,
             'xwin_src': 0, 'xwin_off': 0}
if _GT_AXES not in ('zyx', 'z'):
    raise RuntimeError('ARM_GTRI bad BIOHUB_GTRI_AXES %r' % (_GT_AXES,))
if not _LC_ON:
    raise RuntimeError('ARM_GTRI needs lcefr (BIOHUB_LINKER_REFINED_COORDS) enabled: no refined coords to gather at')


def _gt_trilinear(maps, q):
    # maps (C, Z, Y, X); q (n, 3) float coords on the map grid -> (n, C).
    # Integer q reproduces maps[:, z, y, x] exactly (weight 1 on the base corner, 0 elsewhere).
    sizes = maps.shape[-3:]
    q = q.clone()
    for axis in range(3):
        q[:, axis].clamp_(0, sizes[axis] - 1)
    low = q.floor().long()
    frac = q - low.to(q.dtype)
    out = torch.zeros((q.shape[0], maps.shape[0]), device=maps.device, dtype=maps.dtype)
    for dz in (0, 1):
        for dy in (0, 1):
            for dx in (0, 1):
                shift = torch.tensor([dz, dy, dx], device=maps.device)
                loc = low + shift
                for axis in range(3):
                    loc[:, axis].clamp_(0, sizes[axis] - 1)
                w = torch.where(shift.bool(), frac, 1 - frac).prod(dim=1)
                out += maps[:, loc[:, 0], loc[:, 1], loc[:, 2]].T * w[:, None].to(maps.dtype)
    return out


def _gt_gather(model_obj, feat_maps, rcoords, icoords, mask):
    # feat_maps (B, C, Z, Y, X); rcoords = refined, icoords = integer peaks, both (B, N, 3) on the map grid.
    base = model_obj._index_features(feat_maps, icoords, mask)
    q_all = rcoords.clone()
    if _GT_AXES == 'z':
        q_all[..., 1:] = icoords[..., 1:]
    out = torch.zeros_like(base)
    for b in range(feat_maps.shape[0]):
        n = int(mask[b].sum().item())
        if n == 0:
            continue
        if _GT_STATS['selfcheck'] == 0:
            chk = _gt_trilinear(feat_maps[b], icoords[b, :n].float())
            if not torch.allclose(chk.float(), base[b, :n].float(), atol=1e-6, rtol=0.0):
                raise RuntimeError('ARM_GTRI SELFCHECK FAILED: trilinear at the integer peaks != native gather')
            _GT_STATS['selfcheck'] = 1
        out[b, :n] = _gt_trilinear(feat_maps[b], q_all[b, :n].float())
    d = (out - base).abs()
    _GT_STATS['calls'] += 1
    _GT_STATS['nodes'] += int(mask.sum().item())
    _GT_STATS['sum_abs_delta'] += float(d.sum().item())
    _GT_STATS['n_delta'] += int(d.numel())
    return out


def _gt_xwin(frame_logits, c_src, f_idx, t_src):
    # read-only diagnostic: is each source node's integer peak (detected in window [t-1, t]) still a 3x3x3 local
    # max of THIS window's detection logits (window [t, t+1], whose UNet features the pair gathers from)?
    if f_idx != 0 or int(t_src) == 0 or len(c_src) == 0:
        return
    lg = frame_logits
    while lg.dim() > 3:
        lg = lg[0]
    pooled = F.max_pool3d(lg[None, None].float(), 3, stride=1, padding=1)[0, 0]
    idx = torch.as_tensor(np.asarray(c_src[:, 1:], dtype=np.int64), device=lg.device)
    v = lg.float()[idx[:, 0], idx[:, 1], idx[:, 2]]
    pv = pooled[idx[:, 0], idx[:, 1], idx[:, 2]]
    _GT_STATS['xwin_src'] += int(len(c_src))
    _GT_STATS['xwin_off'] += int((v < pv).sum().item())


def _gt_report():
    if _GT_STATS['calls'] > 0 and _GT_STATS['sum_abs_delta'] == 0.0:
        raise RuntimeError('ARM_GTRI NO-OP: the trilinear gather returned the integer-peak features exactly, '
                           'so this arm would read as a false null')
    print('ARM_GTRI_STATS axes=%s calls=%d nodes=%d mean_abs_feat_delta=%.6f selfcheck=%d'
          % (_GT_AXES, _GT_STATS['calls'], _GT_STATS['nodes'],
             _GT_STATS['sum_abs_delta'] / max(1, _GT_STATS['n_delta']), _GT_STATS['selfcheck']), flush=True)
    print('ARM_GTRI_XWIN src_nodes=%d src_offpeak=%d' % (_GT_STATS['xwin_src'], _GT_STATS['xwin_off']), flush=True)


"""
_gt_pairs = [
    # 1. module helper, right before the detection function (after the sub-voxel + lcefr globals)
    ("def _detect_cells_pooled(\n", _GT_HELPER + "def _detect_cells_pooled(\n"),
    # 2-3. primary gathers
    ("            unet_feat_src = model._index_features(\n"
     "                unet_out[:, f_idx], p_coords_src, p_mask_src,\n"
     "            )\n",
     "            unet_feat_src = _gt_gather(\n"
     "                model, unet_out[:, f_idx], p_rcoords_src, p_coords_src, p_mask_src,\n"
     "            )\n"),
    ("            unet_feat_tgt = model._index_features(\n"
     "                unet_out[:, f_idx + 1], p_coords_tgt, p_mask_tgt,\n"
     "            )\n",
     "            unet_feat_tgt = _gt_gather(\n"
     "                model, unet_out[:, f_idx + 1], p_rcoords_tgt, p_coords_tgt, p_mask_tgt,\n"
     "            )\n"),
    # 4-5. secondary (dual-seed) gathers
    ("                secondary_feat_src = secondary_model._index_features(\n"
     "                    secondary_unet_out[:, f_idx], p_coords_src, p_mask_src,\n"
     "                )\n",
     "                secondary_feat_src = _gt_gather(\n"
     "                    secondary_model, secondary_unet_out[:, f_idx], p_rcoords_src, p_coords_src, p_mask_src,\n"
     "                )\n"),
    ("                secondary_feat_tgt = secondary_model._index_features(\n"
     "                    secondary_unet_out[:, f_idx + 1], p_coords_tgt, p_mask_tgt,\n"
     "                )\n",
     "                secondary_feat_tgt = _gt_gather(\n"
     "                    secondary_model, secondary_unet_out[:, f_idx + 1], p_rcoords_tgt, p_coords_tgt, p_mask_tgt,\n"
     "                )\n"),
    # 6. read-only cross-window diagnostic, in the pair loop right where lcefr slices the refined coords
    ("            if _LC_ON:\n"
     "                r_src = _lc_refined_so_far[s_src:e_src]\n",
     "            _gt_xwin(det_logits[f_idx][0], c_src, f_idx, t_src)\n"
     "            if _LC_ON:\n"
     "                r_src = _lc_refined_so_far[s_src:e_src]\n"),
    # 7. per-movie marker + NO-OP guard, before the pre-ILP coordinate manifest
    ("    # Label-free, pre-ILP detector-coordinate manifest. This executes inside\n",
     "    _gt_report()\n"
     "    # Label-free, pre-ILP detector-coordinate manifest. This executes inside\n"),
]
for _gt_old, _gt_new in _gt_pairs:
    _gt_n = _gt_s.count(_gt_old)
    if _gt_n != 1:
        raise RuntimeError('ARM_GTRI anchor matched %d times (need 1): %r' % (_gt_n, _gt_old[:70]))
    _gt_s = _gt_s.replace(_gt_old, _gt_new, 1)
if _gt_s.count('model._index_features(\n') or _gt_s.count('_gt_gather(\n') != 4:
    raise RuntimeError('ARM_GTRI must route exactly the four UNet gathers through _gt_gather')
compile(_gt_s, str(_ps), 'exec')
_ps.write_text(_gt_s)
if 'ARM_GTRI_STATS' not in _ps.read_text():
    raise RuntimeError('ARM_GTRI PATCH DID NOT PERSIST')
print('ARM_GTRI patch applied to', _ps, '| gathers=4 axes=__AXES__', flush=True)
'''


def build_block(axes: str) -> str:
    return BLOCK.replace("__AXES__", axes)


def check_against_real(block: str) -> str:
    """Execute the block's patch logic on a scratch copy of the REAL t6stk3-patched predictor; return new text."""
    import os
    import tempfile
    src = REAL.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "predict_unet_transformer.py"
        p.write_text(src, encoding="utf-8")
        ns = {"os": os, "_ps": p, "print": lambda *a, **k: None}
        exec(compile(block, "gtri_block", "exec"), ns)
        return p.read_text(encoding="utf-8")


def main():
    tag = sys.argv[1]
    args = sys.argv[2:]
    axes = args[args.index("--axes") + 1]
    if axes not in ("zyx", "z"):
        raise SystemExit("--axes must be zyx or z")
    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    c4 = cells[4]
    if c4.count(CELL4_ANCHOR) != 1:
        raise SystemExit("cell-4 anchor matched %d times" % c4.count(CELL4_ANCHOR))
    if "ARM_GTRI" in c4:
        raise SystemExit("base already carries ARM_GTRI")
    block = build_block(axes)
    patched = check_against_real(block)
    if patched.count("_gt_gather(\n") != 4 or "ARM_GTRI_STATS" not in patched:
        raise SystemExit("offline application to the real predictor failed")
    compile(patched, "patched_predictor", "exec")
    c4 = c4.replace(CELL4_ANCHOR, CELL4_ANCHOR + block, 1)
    if c4.index(CELL4_ANCHOR) > c4.index("# ===== TRILINEAR UNet FEATURE GATHER") or \
            c4.index("# ===== TRILINEAR UNet FEATURE GATHER") > c4.index("def list_test_stems()"):
        raise SystemExit("block order wrong")
    cells[4] = c4
    cells[0] = (cells[0].rstrip(NL) + NL +
                'print("ARM_XENV tag=%s SUBVOXEL=hsg200 LCEFR=kept GTRI=%s GAIN=2.00 CLIP=0.4999", flush=True)'
                % (tag, axes) + NL)
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
    print("built", dest, "| gtri axes", axes, "| offline anchors ok on", REAL)


if __name__ == "__main__":
    main()
