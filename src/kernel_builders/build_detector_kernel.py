#!/usr/bin/env python3
"""Turn a trained detector checkpoint into a submittable Kaggle kernel.

Handles the three traps found by inspection (see HANDOFF "HOW TO SHIP A TRAINED DETECTOR"):
  1. manifest-declared weight sha256 gate      (_expected_primary_sha256, ~line 787)
  2. ACTUAL-BYTES checkpoint sha256 gate       (_primary_expected_sha256, ~line 819)  <- the real blocker
  3. dual-seed grid guard: a 1,2,2 primary against the public 1,4,4 secondary raises
     "Primary and secondary models have incompatible inference grids" -> we must disable
     the secondary (BIOHUB_SECONDARY_WEIGHTS="") since our model is a different grid.

Usage:
  python build_detector_kernel.py --ckpt-sha <sha256> --dataset eeshsaxena/<slug> [--out v_detsub]
The checkpoint must already be uploaded as a Kaggle dataset laid out as:
  weights/unet_transformer/split_0/edge_predictor_best.pth   (+ config.json alongside)
"""
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt-sha", required=True, help="sha256 of the trained edge_predictor_best.pth")
    ap.add_argument("--dataset", required=True, help="kaggle dataset slug holding our weights")
    ap.add_argument("--base", default="scratch_kernels/v_div941/kernel.ipynb")
    ap.add_argument("--out", default="scratch_kernels/v_detsub")
    ap.add_argument("--kernel-id", default="eeshsaxena/biohub-v-detsub")
    a = ap.parse_args()

    nb = json.loads((ROOT / a.base).read_text(encoding="utf-8"))
    OLD_SHA = "12f6881ee3620a831697ca098ff8f48e687a24225f4e048b538deec3562fe771"
    n_sha = n_sec = n_copy = 0

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        s = cell.get("source", "")
        if not isinstance(s, str):
            s = "".join(s)

        # (1)+(2) both SHA gates hold the same constant
        if OLD_SHA in s:
            s = s.replace(OLD_SHA, a.ckpt_sha)
            n_sha += s.count(a.ckpt_sha)

        # (3) disable the secondary seed - our grid differs from the public 1,4,4 seed
        marker = 'os.environ["BIOHUB_DET_THRESHOLD"]'
        if marker in s and 'BIOHUB_SECONDARY_WEIGHTS' not in s:
            inject = (
                '\n# our detector is downsample 1,2,2; the public secondary seed is 1,4,4.\n'
                '# predict_unet_transformer raises "incompatible inference grids" if they differ,\n'
                '# so the secondary seed MUST be disabled when shipping our checkpoint.\n'
                'os.environ["BIOHUB_SECONDARY_WEIGHTS"] = ""\n'
                'os.environ["BIOHUB_SECONDARY_EDGE_WEIGHT"] = "0"\n'
                'os.environ["BIOHUB_SECONDARY_DETECTION_WEIGHT"] = "0"\n'
            )
            idx = s.index(marker)
            eol = s.index("\n", idx) + 1
            s = s[:eol] + inject + s[eol:]
            n_sec += 1

        # copy our weights over the materialized path, after the repo is materialized
        if "materialize_inference_repo(ARTIFACTS)" in s and "OURW" not in s:
            s = s.replace(
                "materialize_inference_repo(ARTIFACTS)",
                "materialize_inference_repo(ARTIFACTS)\n"
                "# --- swap in our trained detector ---\n"
                "import shutil as _sh, glob as _gl\n"
                f'OURW = _gl.glob("/kaggle/input/{a.dataset.split("/")[-1]}/**/edge_predictor_best.pth", recursive=True)\n'
                'if not OURW:\n'
                '    raise RuntimeError("our detector weights not found in attached dataset")\n'
                '_dst = REPO_DIR / WEIGHTS_RELATIVE\n'
                '_dst.parent.mkdir(parents=True, exist_ok=True)\n'
                '_sh.copy(OURW[0], _dst)\n'
                '_cfg = [p for p in _gl.glob("/kaggle/input/'
                f'{a.dataset.split("/")[-1]}' + '/**/config.json", recursive=True)]\n'
                'if _cfg: _sh.copy(_cfg[0], _dst.parent / "config.json")\n'
                'print("swapped in our detector:", OURW[0])\n'
            )
            n_copy += 1
        cell["source"] = s

    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "kernel.ipynb").write_text(json.dumps(nb), encoding="utf-8")
    meta = json.loads((ROOT / "scratch_kernels/v_div941/kernel-metadata.json").read_text())
    meta["id"] = a.kernel_id
    meta["title"] = a.kernel_id.split("/")[-1].replace("-", " ")
    meta["dataset_sources"] = list(dict.fromkeys(meta.get("dataset_sources", []) + [a.dataset]))
    (out / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))

    print(f"sha patches       : {n_sha} (expect 2: manifest gate + actual-bytes gate)")
    print(f"secondary disabled: {n_sec} (expect 1)")
    print(f"weight-swap hooks : {n_copy} (expect 1)")
    body = "".join(c.get("source","") if isinstance(c.get("source",""),str) else "".join(c["source"]) for c in nb["cells"])
    print("old sha remaining :", body.count(OLD_SHA), "(want 0)")
    print("built ->", out)
    if n_sha < 2 or n_sec != 1 or n_copy != 1 or body.count(OLD_SHA):
        print("*** PATCH INCOMPLETE - do not push ***"); sys.exit(1)


if __name__ == "__main__":
    main()
