#!/usr/bin/env python3
"""TRAINREP: run an UNMODIFIED production kernel on a fixed set of K train movies (exact-production paired replay).

usage: python scratch_kernels/build_trainrep.py <src_tag> <dst_tag>
  e.g. python scratch_kernels/build_trainrep.py t6stk3  trainrep-t6stk3
       python scratch_kernels/build_trainrep.py t6svT15 trainrep-t6svT15
  reads scratch_kernels/v_<src_tag>/, writes scratch_kernels/v_<dst_tag>/ with id eeshsaxena/biohub-<dst_tag>.

WHY: every offline instrument so far re-implements part of the pipeline (lattice-coord ILP, DeepCenter off, ...)
and reads at best 1-2 board ticks as a coin flip. This derives a kernel that runs the production notebook
byte-for-byte on K train movies (which have GT), so arm-vs-arm deltas are paired per movie with the real
detector + TTA + retention guard + DeepCenter + SV + lcefr + ILP + cell-5 post-processing on the real Kaggle stack.

THE ONLY CHANGE (cell 2, one anchor, asserted to match exactly once in the whole notebook):
  right after  TEST_DIR = COMP_DIR / "test"  a block builds /tmp/biohub_trainrep/test/<stem>.zarr ->
  symlinks to COMP_DIR/train/<stem>.zarr for the K stems below (ONLY .zarr, no GT .geff next to them = the exact
  test layout), rebinds TEST_DIR to that directory and prints 'TRAINREP tag=<dst> K=<k>'. Every consumer of the
  movie set (cell 4 list_test_stems + predictor --data-dir, cell 5 read_test_frame, cell 6 retention audit,
  cell 10 final check) reads TEST_DIR, so the pipeline is otherwise untouched. The farm lives in /tmp (not
  /kaggle/working) so the kernel's saved output never contains image data. Paths are used unresolved
  (io.open_dataset joins ds_path.parent / <stem>.zarr|.geff), so no GT geff is ever visible to the predictor.

MOVIES (K=40, identical for every arm): the 20 train movies with the most GT edges in EACH embryo (44b6 / 6bba),
ties by stem, EXCLUDING the 4 visible-test placeholders (44b6_0113de3b 44b6_0b24845f 6bba_05b6850b 6bba_05db0fb1:
those already have per-arm outputs from the visible runs in data/out_<tag>/ and are scored separately).
GT counts from ~/biohub/data/train/*.geff (box, score_lib.read_geff_arrays). 39,748 GT edges total
(44b6 11,331 / 6bba 28,417); cut 325 / 1179 GT edges.
RUNTIME (t6stk3 visible log + logitcap 60-movie log): ~200 s detection/movie/GPU + 1.1 ms/node link on 2 x T4
shards, cell 5 ~2-3 ms/node sequential, ~700 s fixed (setup 290 s + DeepCenter /kaggle/input glob 400 s):
est. 2.5-2.9 h for these 40 dense movies (mean ~41k nodes); the same model gives 9.7-11.2 h for 199 test-like
movies, consistent with the hidden run finishing inside 12 h.
CAVEAT: production weights were trained on all 199 train movies, so detection is in-sample; the arms differ only
after detection, and the instrument is validated against board anchors (t6svz15 -2 ticks vs t6stk3).
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
NL = chr(10)

TRAINREP_STEMS = [
    "44b6_d29c9ab2", "44b6_3a861e03", "44b6_d5e7d891", "44b6_12dfb391", "44b6_ddf577ad",
    "44b6_668e0cc7", "44b6_c96cfa10", "44b6_8f5ab931", "44b6_7e557709", "44b6_7a302da0",
    "44b6_d78e09d9", "44b6_a2bb48bb", "44b6_3bb3690f", "44b6_8cc6506c", "44b6_eb2880fc",
    "44b6_949adeb1", "44b6_996155de", "44b6_587a1e22", "44b6_8f9ecab4", "44b6_c50204e0",
    "6bba_bb9f20c3", "6bba_09961292", "6bba_784a78c9", "6bba_57b7cc1e", "6bba_cff5865f",
    "6bba_5dfe9ad1", "6bba_ae82a791", "6bba_786893ac", "6bba_1d0d8384", "6bba_9a41d029",
    "6bba_cdcfe533", "6bba_6feb10f0", "6bba_6feeb0b1", "6bba_af149c94", "6bba_283bf9f1",
    "6bba_b329af44", "6bba_ebff6e76", "6bba_337b1b3a", "6bba_ef7b4f7e", "6bba_3fda6b25",
]
PLACEHOLDERS = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
STEMS_SHA1 = hashlib.sha1(",".join(sorted(TRAINREP_STEMS)).encode()).hexdigest()[:12]

ANCHOR = 'TEST_DIR = COMP_DIR / "test"\n'


def block(dst_tag):
    stems = "[" + ", ".join(repr(s) for s in TRAINREP_STEMS) + "]"
    return (
        "# TRAINREP (build_trainrep.py): the ONLY change vs the source kernel - run the unmodified pipeline on a\n"
        "# fixed list of train movies laid out exactly like the test set (symlinked .zarr only, no GT next to them).\n"
        "TRAINREP_TAG = %r\n" % dst_tag
        + "TRAINREP_STEMS = %s\n" % stems
        + "_trainrep_src = COMP_DIR / \"train\"\n"
        "_trainrep_dir = Path(\"/tmp/biohub_trainrep/test\")\n"
        "if _trainrep_dir.exists():\n"
        "    shutil.rmtree(_trainrep_dir)\n"
        "_trainrep_dir.mkdir(parents=True)\n"
        "for _trainrep_stem in TRAINREP_STEMS:\n"
        "    _trainrep_zarr = _trainrep_src / f\"{_trainrep_stem}.zarr\"\n"
        "    if not (_trainrep_zarr / \"0\" / \"zarr.json\").is_file():\n"
        "        raise FileNotFoundError(f\"TRAINREP missing train movie {_trainrep_zarr}\")\n"
        "    (_trainrep_dir / f\"{_trainrep_stem}.zarr\").symlink_to(_trainrep_zarr, target_is_directory=True)\n"
        "if sorted(p.name for p in _trainrep_dir.iterdir()) != sorted(f\"{s}.zarr\" for s in TRAINREP_STEMS):\n"
        "    raise RuntimeError(\"TRAINREP movie farm mismatch\")\n"
        "TEST_DIR = _trainrep_dir\n"
        "print(f\"TRAINREP tag={TRAINREP_TAG} K={len(TRAINREP_STEMS)}\", flush=True)\n"
        + "print(\"TRAINREP_STEMS sha1=%s\", sorted(TRAINREP_STEMS), flush=True)\n" % STEMS_SHA1
    )


def cell_sources(nb):
    return ["".join(c["source"]) for c in nb["cells"]]


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__.split(NL + NL)[1])
    src_tag, dst_tag = sys.argv[1], sys.argv[2]
    if not dst_tag.startswith("trainrep-") or not all(ch.isalnum() or ch == "-" for ch in dst_tag):
        raise SystemExit("dst_tag must look like trainrep-<name> (letters, digits, '-')")
    if len(TRAINREP_STEMS) != 40 or len(set(TRAINREP_STEMS)) != 40 or set(TRAINREP_STEMS) & set(PLACEHOLDERS):
        raise SystemExit("TRAINREP_STEMS list broken")
    if sum(s.startswith("44b6_") for s in TRAINREP_STEMS) != 20 or sum(s.startswith("6bba_") for s in TRAINREP_STEMS) != 20:
        raise SystemExit("TRAINREP_STEMS not 20/20 stratified")
    src = SK / ("v_" + src_tag)
    nb = json.loads((src / "kernel.ipynb").read_text(encoding="utf-8"))
    orig = json.loads((src / "kernel.ipynb").read_text(encoding="utf-8"))
    srcs = cell_sources(nb)

    # --- anchors: exactly once in the whole notebook, and it is in cell 2; no prior TRAINREP ---
    hits = [(i, s.count(ANCHOR)) for i, s in enumerate(srcs) if s.count(ANCHOR)]
    if hits != [(2, 1)]:
        raise SystemExit("anchor %r hits %s (need exactly [(2, 1)])" % (ANCHOR, hits))
    if any("TRAINREP" in s for s in srcs):
        raise SystemExit("source already contains TRAINREP")
    if "import shutil" not in srcs[2] or "from pathlib import Path" not in srcs[2]:
        raise SystemExit("cell 2 lost its shutil/Path imports")
    # every movie-set consumer must go through TEST_DIR (checked on the source, fail loudly if that changed)
    if "--data-dir" not in srcs[4] or "str(TEST_DIR)," not in srcs[4] or "TEST_DIR.iterdir()" not in srcs[4]:
        raise SystemExit("cell 4 movie discovery no longer reads TEST_DIR")
    if 'zarr_path = TEST_DIR / f"{dataset}.zarr"' not in srcs[5]:
        raise SystemExit("cell 5 frame reader no longer reads TEST_DIR")
    for i, s in enumerate(srcs):
        for bad in ('COMP_DIR / "test"', "/test/", "'test')", '"test")'):
            if i != 2 and bad in s:
                raise SystemExit("cell %d references the test set directly: %r" % (i, bad))

    new2 = srcs[2].replace(ANCHOR, ANCHOR + block(dst_tag), 1)
    for i, s in enumerate(srcs):
        compile(new2 if i == 2 else s, "%s:cell%d" % (dst_tag, i), "exec")
    nb["cells"][2]["source"] = new2.splitlines(keepends=True)

    # --- cell diff: prove only cell 2 changed and only by the inserted block ---
    for i, (a, b) in enumerate(zip(orig["cells"], nb["cells"])):
        if i == 2:
            ka = {k: v for k, v in a.items() if k != "source"}
            kb = {k: v for k, v in b.items() if k != "source"}
            if ka != kb:
                raise SystemExit("cell 2 non-source fields changed")
            sa, sb = "".join(a["source"]), "".join(b["source"])
            if sb != sa.replace(ANCHOR, ANCHOR + block(dst_tag), 1) or len(sb) - len(sa) != len(block(dst_tag)):
                raise SystemExit("cell 2 diff is not exactly the inserted block")
        elif a != b:
            raise SystemExit("cell %d changed" % i)
    if len(orig["cells"]) != len(nb["cells"]) or {k: v for k, v in orig.items() if k != "cells"} != {k: v for k, v in nb.items() if k != "cells"}:
        raise SystemExit("notebook structure/metadata changed")

    dest = SK / ("v_" + dst_tag)
    dest.mkdir(parents=True, exist_ok=True)
    json.dump(nb, open(dest / "kernel.ipynb", "w", encoding="utf-8"))
    meta = json.loads((src / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta_src = dict(meta)
    meta["id"] = "eeshsaxena/biohub-" + dst_tag
    meta["title"] = "biohub " + dst_tag
    if {k: v for k, v in meta.items() if k not in ("id", "title")} != {k: v for k, v in meta_src.items() if k not in ("id", "title")}:
        raise SystemExit("metadata drift")
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    (dest / "TRAINREP_STEMS.json").write_text(json.dumps(TRAINREP_STEMS, indent=1) + NL)

    # round-trip check of what was written
    back = json.loads((dest / "kernel.ipynb").read_text(encoding="utf-8"))
    bsrc = cell_sources(back)
    changed = [i for i, (a, b) in enumerate(zip(srcs, bsrc)) if a != b]
    if changed != [2] or bsrc[2] != new2:
        raise SystemExit("written notebook differs unexpectedly: %s" % changed)
    print("built %s from v_%s | id %s | K=%d (44b6 20 / 6bba 20) stems_sha1=%s | changed cells %s (+%d chars, 1 anchor)"
          % (dest.name, src_tag, meta["id"], len(TRAINREP_STEMS), STEMS_SHA1, changed, len(block(dst_tag))))


if __name__ == "__main__":
    main()
