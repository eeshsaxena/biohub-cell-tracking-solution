#!/usr/bin/env python3
"""Swap the PRIMARY unet_transformer checkpoint on our 0.954 body for a public
synthetic-pretrained one.

usage: python scratch_kernels/build_synprim.py <tag> <dataset-slug-fragment> <filename>
  e.g. python scratch_kernels/build_synprim.py synp biohub-synthetic-5fold-ensemble-v1 synthetic_5fold_swa.pth

WHY: the competition discussion is unanimous that post-processing on the frozen public
weights is saturated, and the one model-side lever anyone reports as working is
pretraining on the public CC0 synthetic set (hikaggler: +0.012-0.018 on a 24-video
hold-out, the only big lever they found in three weeks). bhpepper published a 5-fold
synthetic fine-tuned SWA ensemble of EXACTLY our architecture - verified locally:
136 state-dict keys, identical shapes, zero mismatches against the support pack's
edge_predictor_best.pth, and genuinely different weights (mean |delta| 0.98).

The swap mechanism is lifted verbatim from our own prim300 arm, which is the only
place in this project that has ever safely repointed WEIGHTS_RELATIVE. Two changes:
the dataset slug, and the config.json - bhpepper ships none, so we take the support
pack's own config, which is correct precisely because the state dicts match key for key.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
Q = chr(34)
NL = chr(10)


def block(tag, slug, fname):
    return NL.join([
        '',
        '# --- %s: PRIMARY unet_transformer <- public SYNTHETIC-PRETRAINED checkpoint (%s) ---' % (tag, slug),
        '# Lifted from our prim300 arm. REPO_DIR/weights is a symlink into read-only /kaggle/input, so we',
        '# never write over the materialised primary: we reassign WEIGHTS_RELATIVE to an ABSOLUTE path',
        '# (REPO_DIR / "/abs" == "/abs"), which predict_cmd and the validator then follow.',
        '# This dataset ships no config.json. That is safe here and only here, because the checkpoint was',
        '# verified locally to share all 136 state-dict keys and every shape with the support-pack primary,',
        '# so the support pack\'s own config describes it exactly.',
        'import glob as _sp_glob',
        'import shutil as _sp_shutil',
        '_sp_slug = %s%s%s' % (Q, slug, Q),
        '_sp_name = %s%s%s' % (Q, fname, Q),
        '_sp_cands = sorted(',
        '    _p for _p in _sp_glob.glob("/kaggle/input/**/" + _sp_name, recursive=True) if _sp_slug in _p',
        ')',
        '_sp_distinct = {_integrity_sha256_file(Path(_p)) for _p in _sp_cands}',
        'if not _sp_cands or len(_sp_distinct) != 1:',
        '    raise FileNotFoundError(f"%s: expected one distinct {_sp_slug}/{_sp_name}, found {_sp_cands} {_sp_distinct}")' % tag,
        '_sp_src = Path(_sp_cands[0])',
        '# the support pack primary we are replacing, and its config, both already pinned by cell 3',
        '_sp_cfg_src = Path(_primary_materialized_path).parent / "config.json"',
        'if not _sp_cfg_src.is_file():',
        '    raise FileNotFoundError(f"%s: missing {_sp_cfg_src}")' % tag,
        '_sp_cfg = {"unet_out_channels": 32, "unet_layers": [32, 64, 128], "downsample": [1, 4, 4],',
        '           "window_size": 2, **json.loads(_sp_cfg_src.read_text())}',
        'if (list(_sp_cfg["downsample"]), int(_sp_cfg["window_size"]), int(_sp_cfg["unet_out_channels"]),',
        '        list(_sp_cfg["unet_layers"])) != ([1, 4, 4], 2, 32, [32, 64, 128]):',
        '    raise RuntimeError(f"%s: config.json is not the 1,4,4/W=2 grid: {_sp_cfg}")' % tag,
        '# refuse the swap unless the checkpoint really is our architecture, key for key',
        'import torch as _sp_torch',
        '_sp_new = _sp_torch.load(str(_sp_src), map_location="cpu", weights_only=True)',
        '_sp_new = _sp_new.get("state_dict", _sp_new) if isinstance(_sp_new, dict) and "state_dict" in _sp_new else _sp_new',
        '_sp_old = _sp_torch.load(str(_primary_materialized_path), map_location="cpu", weights_only=True)',
        '_sp_old = _sp_old.get("state_dict", _sp_old) if isinstance(_sp_old, dict) and "state_dict" in _sp_old else _sp_old',
        'if set(_sp_new) != set(_sp_old):',
        '    raise RuntimeError("%s: state-dict keys differ from the support-pack primary")' % tag,
        '_sp_bad = [k for k in _sp_old if tuple(_sp_new[k].shape) != tuple(_sp_old[k].shape)]',
        'if _sp_bad:',
        '    raise RuntimeError(f"%s: shape mismatch on {_sp_bad[:5]}")' % tag,
        '_sp_delta = float(sum((_sp_new[k].float() - _sp_old[k].float()).abs().mean()',
        '                      for k in _sp_old if _sp_old[k].dtype.is_floating_point) / max(len(_sp_old), 1))',
        'if _sp_delta <= 0.0:',
        '    raise RuntimeError("%s: swapped checkpoint is identical to the primary")' % tag,
        'del _sp_new, _sp_old',
        '_sp_dir = WORKING_DIR / "synprim_weights"',
        '_sp_dir.mkdir(parents=True, exist_ok=True)',
        '_sp_dst = _sp_dir / "edge_predictor_best.pth"',
        '_sp_shutil.copyfile(_sp_src, _sp_dst)',
        '_sp_shutil.copyfile(_sp_cfg_src, _sp_dir / "config.json")',
        'WEIGHTS_RELATIVE = str(_sp_dst)',
        'if (REPO_DIR / WEIGHTS_RELATIVE) != _sp_dst or not (REPO_DIR / WEIGHTS_RELATIVE).is_file():',
        '    raise RuntimeError("%s: WEIGHTS_RELATIVE does not resolve to the swapped checkpoint")' % tag,
        '_sp_sha = _integrity_sha256_file(_sp_dst)',
        'if _sp_sha == _primary_expected_sha256:',
        '    raise RuntimeError("%s: swapped checkpoint is byte-identical to the 50ep primary")' % tag,
        'print("SYNPRIM SWAPPED [%s]:", _sp_src, "->", WEIGHTS_RELATIVE, flush=True)' % tag,
        'print("SYNPRIM SWAPPED sha256:", _sp_sha, "(was", _primary_expected_sha256 + ")", flush=True)',
        'print("SYNPRIM SWAPPED mean_abs_delta=%.4f" % _sp_delta, flush=True)',
        'print("SYNPRIM SWAPPED config:", _sp_cfg, flush=True)',
        '',
    ])


def main():
    tag, slug, fname = sys.argv[1], sys.argv[2], sys.argv[3]
    extra_ds = sys.argv[4] if len(sys.argv) > 4 else None

    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]

    anchor = 'print("CUDA device:", _torch.cuda.get_device_name(0))' + NL
    if cells[4].count(anchor) != 1:
        raise SystemExit("cell-4 anchor matched %d times" % cells[4].count(anchor))
    cells[4] = cells[4].replace(anchor, anchor + block(tag, slug, fname), 1)

    ident = 'print("ARM_XENV tag=%s SYNPRIM=%s", flush=True)' % (tag, slug)
    cells[0] = cells[0].rstrip(NL) + NL + ident + NL

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
    ds = extra_ds or slug
    if ds not in meta["dataset_sources"]:
        meta["dataset_sources"] = meta["dataset_sources"] + [ds]
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest)
    print("  dataset_sources:", meta["dataset_sources"])


if __name__ == "__main__":
    main()
