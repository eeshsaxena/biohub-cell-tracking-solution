#!/usr/bin/env python3
"""ourvzl: ourvz with the sub-voxel z offset carried INTO the per-frame detections, so the edge model sees it.

usage: python scratch_kernels/build_ourvzl.py [tag]        (default tag: ourvzl)

WHY. ourvz (V1284 head for y/x + our sub-voxel soft-argmax for z, t6 linker stack, lcefr dropped) adds the z
offset only at the FINAL coords assembly of predict_video. Everything between detection and that assembly reads
INTEGER z: the sinusoidal pos embedding, the predict_edges geometry (forward, bidirectional reverse, secondary
low-margin model) and the edge distance. In t6stk3 (0.954) lcefr fed those inputs the refined z. t6stk3 vs t6svyx
says the z channel is worth ~6 ticks; ourvz tests "z in the output only", this arm adds "z in the edge model too".

Mechanics (all inside the predictor script that cell 4 patches, applied AFTER the V1284 block):
  * each frame's z offset (computed from the INTEGER peak, gain 2.00, clip 0.4999, y/x zeroed by ZONLY) is added
    to arr[:, 1] right AFTER `_v1284_refine` and BEFORE coord_offset / coord_lists. Never before V1284: its
    sample_features casts arr to long (truncation), and _sv_softarg_offsets already ran on the integer peak;
  * the final assembly then adds ONLY the (zero) y/x columns of the sub-voxel offsets, never z again, asserts that
    the assembled z equals integer peak + one offset bit for bit, and prints
    `ARM_SV_Z_TO_ARR frames=.. nodes=.. mean_abs_z=.. z_nonzero=.. final_z_add=0 gather_int_z=1` per movie;
  * V1284's trilinear _index_features rounds z back to the integer peak (|offset| <= 0.4999 so round() returns
    the peak), exactly as lcefr kept the UNet gather at the peak: the edge model's FEATURES stay bitwise those of
    ourvz and only its z GEOMETRY changes. Final node coordinates are bitwise those of ourvz.
Every anchor is asserted here against the REAL ourvz-patched predictor/module from the Kaggle run (cell 4 does not
touch the predictor after the V1284 block, so that file is the exact state at our insertion point), and asserted
again at notebook runtime (RuntimeError on any count != 1).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourvz"
REAL = ROOT / "data" / "out_ourvz" / "tracking_repo" / "scripts"
NL = chr(10)

IDENT_OLD = 'print("ARM_XENV tag=ourvz V1284_HEAD=mounted SUBVOXEL=z-only V1284_AXES=yx", flush=True)'
IDENT_NEW = 'print("ARM_XENV tag=%s V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx", flush=True)'

# cell 4: flags right next to the ZONLY env line
ENV_ANCHOR = ("os.environ['BIOHUB_SUBVOXEL_ZONLY'] = '1'\n"
              "print('ARM_SV_ZONLY=1 (sub-voxel y/x offsets zeroed, z kept at gain 2.00 clip 0.4999)', flush=True)\n")
ENV_NEW = (ENV_ANCHOR +
           "os.environ['BIOHUB_SUBVOXEL_Z_TO_ARR'] = '1'\n"
           "os.environ['BIOHUB_V1284_GATHER_INT_Z'] = '1'\n"
           "print('ARM_SV_Z_TO_ARR=1 (sub-voxel z added to the per-frame detections after V1284; final assembly "
           "skips z; V1284 gather z rounded to the peak: gather_int_z=1)', flush=True)\n")
# cell 4: the patch block goes right after the V1284 block (its anchor line only exists after V1284 patched _ps)
BLOCK_ANCHOR = "print('ARM_V1284_YX module_patched=1', flush=True)\n"
CELL4_ORDER = ["print('SUBVOXEL patch applied to', _ps, flush=True)",
               "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])",
               BLOCK_ANCHOR,
               "def list_test_stems() -> list[str]:"]

# ---------------------------------------------------------------- predictor patches (applied in this order)
PRED_PAIRS = [
    # P1 module level, inside the sub-voxel helper: read the flag once, refuse inconsistent configurations
    ("_SV_STATS = {'nodes': 0, 'mean_abs_off': 0.0, 'frac_clipped': 0.0}\n",
     "_SV_STATS = {'nodes': 0, 'mean_abs_off': 0.0, 'frac_clipped': 0.0}\n"
     "_SV_ZTA = os.environ.get('BIOHUB_SUBVOXEL_Z_TO_ARR', '0') != '0'\n"
     "if _SV_ZTA and not _SV_ON:\n"
     "    raise RuntimeError('ARM_SV_Z_TO_ARR needs the sub-voxel refinement enabled (BIOHUB_SUBVOXEL_SOFTARG=1)')\n"
     "if _SV_ZTA and os.environ.get('BIOHUB_SUBVOXEL_ZONLY', '0') == '0':\n"
     "    raise RuntimeError('ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY=1 (y/x come from V1284)')\n"),
    # P2 predict_video locals
    ("    _sv_refine_lists: list[np.ndarray] = []\n",
     "    _sv_refine_lists: list[np.ndarray] = []\n"
     "    _zta_applied: list[np.ndarray] = []\n"
     "    _zta_base_z: list[np.ndarray] = []\n"),
    # P3 per frame: after V1284 refines y/x, before coord_offset / coord_lists
    ("                arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])\n",
     "                arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])\n"
     "                if _SV_ZTA:\n"
     "                    _zta_o = np.asarray(_sv_refine_lists[-1], dtype=np.float32)[:, 0].copy()\n"
     "                    if _zta_o.shape[0] != len(arr):\n"
     "                        raise RuntimeError('ARM_SV_Z_TO_ARR offset/arr length mismatch %d vs %d'\n"
     "                                           % (_zta_o.shape[0], len(arr)))\n"
     "                    arr = np.array(arr, dtype=np.float32)\n"
     "                    _zta_base_z.append(arr[:, 1].copy())\n"
     "                    arr[:, 1] += _zta_o\n"
     "                    _zta_applied.append(_zta_o)\n"),
    # P4 final assembly: z is already in coord_lists, add only the (zero) y/x columns, prove exactly-once
    ("        coords[:, 1:] += _sv_off\n",
     "        if _SV_ZTA:\n"
     "            if len(_zta_applied) != len(_sv_refine_lists) or len(_zta_base_z) != len(_sv_refine_lists):\n"
     "                raise RuntimeError('ARM_SV_Z_TO_ARR z offset not applied exactly once per frame (%d/%d of %d)'\n"
     "                                   % (len(_zta_applied), len(_zta_base_z), len(_sv_refine_lists)))\n"
     "            _zta_all = np.concatenate(_zta_applied).astype(np.float32)\n"
     "            _zta_base = np.concatenate(_zta_base_z).astype(np.float32)\n"
     "            if _zta_all.shape[0] != _sv_off.shape[0] or not np.array_equal(_zta_all, _sv_off[:, 0]):\n"
     "                raise RuntimeError('ARM_SV_Z_TO_ARR z offset not applied exactly once per node')\n"
     "            if not np.array_equal(_zta_base, np.round(_zta_base)):\n"
     "                raise RuntimeError('ARM_SV_Z_TO_ARR base z not integral (V1284 moved z?)')\n"
     "            if _zta_all.shape[0] > 0 and not (_zta_all != 0.0).any():\n"
     "                raise RuntimeError('ARM_SV_Z_TO_ARR NO-OP: no detection received a z offset')\n"
     "            coords[:, 2:] += _sv_off[:, 1:]  # final_z_add=0: z is already in arr; y/x columns are 0 under ZONLY\n"
     "            if not np.array_equal(coords[:, 1], _zta_base + _zta_all):\n"
     "                raise RuntimeError('ARM_SV_Z_TO_ARR assembled z != integer peak + one sub-voxel offset')\n"
     "            print('ARM_SV_Z_TO_ARR frames=%d nodes=%d mean_abs_z=%.4f z_nonzero=%d final_z_add=0 gather_int_z=%s'\n"
     "                  % (len(_zta_applied), _zta_all.shape[0],\n"
     "                     float(np.abs(_zta_all).mean()) if _zta_all.shape[0] else 0.0,\n"
     "                     int((_zta_all != 0.0).sum()), os.environ.get('BIOHUB_V1284_GATHER_INT_Z', '0')), flush=True)\n"
     "        else:\n"
     "            coords[:, 1:] += _sv_off\n"),
]
# V1284 module: the trilinear gather rounds z back to the integer peak (lcefr kept the gather at the peak)
MOD_PAIRS = [
    ("        q = coords[batch, :n].clone()\n",
     "        q = coords[batch, :n].clone()\n"
     "        if os.environ.get('BIOHUB_V1284_GATHER_INT_Z', '0') != '0':\n"
     "            q[:, 0] = torch.round(q[:, 0])  # ourvzl: z gather stays at the integer peak (|sv z| <= 0.4999)\n"),
]
PERSIST_PRED = "ARM_SV_Z_TO_ARR frames="
PERSIST_MOD = "BIOHUB_V1284_GATHER_INT_Z"


def apply_pairs(src, pairs, what):
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            raise SystemExit("%s anchor matched %d times (need 1): %r" % (what, n, old[:70]))
        src = src.replace(old, new, 1)
    return src


def render_block():
    L = []
    w = L.append
    w("# ===== SUB-VOXEL Z INTO THE PER-FRAME DETECTIONS (arm ourvzl) =====")
    w("# ourvz adds the sub-voxel z offset only at the final coords assembly, so the edge model (pos embedding,")
    w("# predict_edges geometry forward/reverse/secondary) and the edge distance read INTEGER z; t6stk3's lcefr fed")
    w("# them refined z. Here each frame's z offset is added to `arr` right AFTER V1284 refines y/x (never before:")
    w("# V1284's sample_features casts arr to long = truncation) and BEFORE coord_offset, the final assembly skips z")
    w("# (applied exactly once, asserted), and V1284's trilinear gather rounds z back to the integer peak, as lcefr")
    w("# kept the UNet gather at the peak. Final node coordinates are bitwise those of ourvz.")
    w("if (os.environ.get('BIOHUB_SUBVOXEL_Z_TO_ARR') != '1' or os.environ.get('BIOHUB_SUBVOXEL_ZONLY') != '1'")
    w("        or os.environ.get('BIOHUB_V1284_GATHER_INT_Z') != '1'):")
    w("    raise RuntimeError('ARM_SV_Z_TO_ARR env flags missing: Z_TO_ARR, ZONLY and GATHER_INT_Z must all be 1')")
    w("_zta_mod = _ps.parent / 'v1284_coordinate_refinement.py'")
    w("_zta_m = _zta_mod.read_text()")
    w("_zta_mod_pairs = [")
    for old, new in MOD_PAIRS:
        w("    (%r,\n     %r)," % (old, new))
    w("]")
    w("for _zta_old, _zta_new in _zta_mod_pairs:")
    w("    _zta_n = _zta_m.count(_zta_old)")
    w("    if _zta_n != 1:")
    w("        raise RuntimeError('ARM_SV_Z_TO_ARR module anchor matched %d times (need 1): %r' % (_zta_n, _zta_old[:60]))")
    w("    _zta_m = _zta_m.replace(_zta_old, _zta_new, 1)")
    w("compile(_zta_m, str(_zta_mod), 'exec')")
    w("_zta_mod.write_text(_zta_m)")
    w("_zta_s = _ps.read_text()")
    w("_zta_pairs = [")
    for old, new in PRED_PAIRS:
        w("    (%r,\n     %r)," % (old, new))
    w("]")
    w("for _zta_old, _zta_new in _zta_pairs:")
    w("    _zta_n = _zta_s.count(_zta_old)")
    w("    if _zta_n != 1:")
    w("        raise RuntimeError('ARM_SV_Z_TO_ARR anchor matched %d times (need 1): %r' % (_zta_n, _zta_old[:60]))")
    w("    _zta_s = _zta_s.replace(_zta_old, _zta_new, 1)")
    w("compile(_zta_s, str(_ps), 'exec')")
    w("_ps.write_text(_zta_s)")
    w("if %r not in _ps.read_text() or %r not in _zta_mod.read_text():" % (PERSIST_PRED, PERSIST_MOD))
    w("    raise RuntimeError('ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST')")
    w("print('ARM_SV_Z_TO_ARR patch applied to', _ps, '| predictor anchors=%d module anchors=%d gather_int_z=1', flush=True)"
      % (len(PRED_PAIRS), len(MOD_PAIRS)))
    return NL.join(L) + NL


def code_cells(path):
    nb = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "ourvzl"
    nb, cells = code_cells(BASE / "kernel.ipynb")

    # 1. the predictor + module anchors against the REAL ourvz end state (== state at our insertion point)
    real_pred = (REAL / "predict_unet_transformer.py").read_text(encoding="utf-8")
    real_mod = (REAL / "v1284_coordinate_refinement.py").read_text(encoding="utf-8")
    if "_v1284_refine" not in real_pred or "shift[:, 0] = 0.0" not in real_mod or "SV_ARM_HSG200" not in real_pred:
        raise SystemExit("REAL ourvz predictor/module is not the ourvz end state")
    new_pred = apply_pairs(real_pred, PRED_PAIRS, "predictor")
    new_mod = apply_pairs(real_mod, MOD_PAIRS, "module")
    compile(new_pred, "predict_unet_transformer.py[ourvzl]", "exec")
    compile(new_mod, "v1284_coordinate_refinement.py[ourvzl]", "exec")
    if new_pred.count(PERSIST_PRED) != 1 or new_mod.count(PERSIST_MOD) != 1:
        raise SystemExit("persistence markers not unique in the patched sources")
    # ordering inside predict_video: SV offsets from the integer peak -> V1284 -> z add -> coord_offset
    i_sv = new_pred.index("_sv_refine_lists.append(_sv_softarg_offsets(")
    i_v = new_pred.index("arr = _v1284_refine(ds_path, t, arr, unet_out[:, f_idx])")
    i_z = new_pred.index("arr[:, 1] += _zta_o")
    i_co = new_pred.index("coord_offset[t] = (global_node_count, global_node_count + len(arr))")
    i_edges = new_pred.index("coords_so_far = (")
    i_fin = new_pred.index("coords[:, 2:] += _sv_off[:, 1:]")
    if not (i_sv < i_v < i_z < i_co < i_edges < i_fin):
        raise SystemExit("predictor ordering check failed")

    # 2. cell 0 identity
    c0 = cells[0]
    if c0.count(IDENT_OLD) != 1 or c0.count("tag=ourvz ") != 1:
        raise SystemExit("cell-0 identity anchor matched %d" % c0.count(IDENT_OLD))
    cells[0] = c0.replace(IDENT_OLD, IDENT_NEW % tag, 1)

    # 3. cell 4: env flags + marker next to ZONLY, patch block right after the V1284 block
    c4 = cells[4]
    for a in [ENV_ANCHOR] + CELL4_ORDER:
        if c4.count(a) != 1:
            raise SystemExit("cell-4 anchor %r matched %d" % (a[:60], c4.count(a)))
    pos = [c4.index(a) for a in CELL4_ORDER]
    if pos != sorted(pos) or c4.index(ENV_ANCHOR) > pos[0]:
        raise SystemExit("cell-4 order check failed: %r" % pos)
    for bad in ("BIOHUB_SUBVOXEL_Z_TO_ARR", "BIOHUB_SUBVOXEL_Z_INTO_ARR", "ARM_SV_Z_TO_ARR", "ARM_LCEFR", "_LC_ON"):
        if bad in c4:
            raise SystemExit("base cell 4 already contains %r" % bad)
    block = render_block()
    c4 = c4.replace(ENV_ANCHOR, ENV_NEW, 1)
    c4 = c4.replace(BLOCK_ANCHOR, BLOCK_ANCHOR + NL + block, 1)
    if c4.count("# ===== SUB-VOXEL Z INTO THE PER-FRAME DETECTIONS") != 1:
        raise SystemExit("block insertion failed")
    if not (c4.index(ENV_NEW) < c4.index(BLOCK_ANCHOR) < c4.index(block) < c4.index(CELL4_ORDER[-1])):
        raise SystemExit("cell-4 final order check failed")
    cells[4] = c4

    # 4. the block's literals must be exactly the pairs asserted above (repr round-trip)
    ns = {}
    bstart = block.index("_zta_mod_pairs = [")
    exec(block[bstart:block.index("for _zta_old", bstart)], ns)
    pstart = block.index("_zta_pairs = [")
    exec(block[pstart:block.index("for _zta_old", pstart)], ns)
    if [tuple(p) for p in ns["_zta_pairs"]] != PRED_PAIRS or [tuple(p) for p in ns["_zta_mod_pairs"]] != MOD_PAIRS:
        raise SystemExit("rendered block literals differ from the asserted pairs")

    for k2, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, k2), "exec")

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
    print("built", dest, "| datasets", meta["dataset_sources"])
    print("predictor anchors=%d module anchors=%d all matched once against %s" % (len(PRED_PAIRS), len(MOD_PAIRS), REAL))


if __name__ == "__main__":
    main()
