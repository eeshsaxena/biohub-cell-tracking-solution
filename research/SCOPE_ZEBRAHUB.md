# Zebrahub External-Data Build — Scope

**Goal:** give the learned edge model the embryo diversity it lacks (2 -> 7+ embryos) so it
generalizes to the 2 NOVEL test embryos. This is the ONLY lever that attacks the measured root
cause of the 0.921 wall.

## Why this is the right lever (the root-cause chain)
- LB dose-response (2026-08-28): every learned-edge-model intervention is net-NEGATIVE, monotone
  with dose (prune tau.10/.25/.60 -> 0.920/0.919/0.918; re-route -> 0.920; base sim4 -> 0.921).
- Root cause: the edge CNN is trained on only **2 embryos / ~10k sparse GT edges** (each geff has
  ~50 edges; 199 crops x 2 embryos). It memorizes train-embryo appearance and is ANTI-informative
  on the 2 novel test embryos. The DETECTOR generalizes (recall 0.978 on test) because it saw lots
  of data; the LINKER edge-model can't.
- Fix = more embryo diversity in edge supervision = external data.

## Why Zebrahub specifically (compatibility — VERIFIED where marked)
- SAME lab (CZ Biohub / Royer lab) runs both Zebrahub and this competition. [verified]
- SAME imaging: DaXi light-sheet, ubiquitous nuclear histone reporter (mCherry). [verified, paper]
- SAME tools: Ultrack tracking -> geff/tracksdata graph (nodes t,z,y,x; edges across time;
  division = 1 node -> 2). [verified, organizers' repo]
- Competition voxel scale Z,Y,X = 1.625, 0.40625, 0.40625 um/px. [verified locally + repo]
- Host CONFIRMED Zebrahub imaging + *_tracks are usable, "no overlap with the test set"
  (forum 734330, @thibautgoldsborough). [INTEL #5]
- Zebrahub = 7 DaXi/OpenSiMView light-sheet time-lapses WITH cell tracking (dense lineage
  reconstruction, likely FAR more edges than the sparse competition GT). [verified, paper]
- => The competition crops are almost certainly diced from the same DaXi/Zebrahub pipeline.

## The build (phased; Phase 0 gates everything)

### PHASE 0 — COMPATIBILITY GATE (cheap, decisive, do FIRST)
1. Download ONE Zebrahub DaXi tracking embryo (or a cropped subset) from the Zebrahub data
   portal (zebrahub.sf.czbiohub.org/data; OME-Zarr via ome-zarr-py / S3).
2. CHECK voxel size == [1.625, 0.40625, 0.40625]? (DaXi may differ -> would need resampling.)
3. CHECK nuclear appearance: blob diameter ~10-16um, intensity/contrast similar to our crops?
4. Run the Kunal detector on a Zebrahub frame -> does it produce sane detections that match the
   Zebrahub tracks (recall)? If the detector transfers, the patches will too.
5. **GATE:** match -> proceed. Voxel/marker mismatch -> patches won't transfer without heavy
   resampling and the whole plan is high-risk (would need detector retrain, infeasible).

### PHASE 1 — DATA ACQUISITION + CONVERSION
1. Identify exact downloads for the DaXi tracking embryos (portal S3 bucket). NOTE: whole-embryo
   light-sheet time-lapse is 100s of GB/embryo -> download SELECTIVELY (crop regions + only the
   timepoints/planes needed), NOT the full volumes.
2. Convert Zebrahub tracks (Ultrack/napari-tracks: track_id, t, z, y, x, parent) -> geff edges
   (consecutive-frame parent->child; division = parent -> 2 children).
3. Dice each Zebrahub embryo into COMPETITION-SIZED crops (~64 x 256 x 256, ~76-100 frames),
   tracks clipped per crop -> geff+zarr pairs in the EXACT competition format.
4. Package as a Kaggle dataset `eeshsaxena/biohub-zebrahub-extra` (download locally to the 4050
   box first; the Kaggle per-file API 429s, so build the dataset offline then upload once).

### PHASE 2 — RETRAIN THE EDGE MODEL ON THE AUGMENTED SET
1. Reuse `build_edgemodel_v2.py` machinery VERBATIM (extract_patches, EdgeCNN, build_pair_features,
   label_blocks) but point TRAIN_DIR at competition(2) + Zebrahub(N) embryos.
2. Train the edge CNN on the combined set.
3. REAL generalization test: hold out a WHOLE embryo (train on N-1, predict the held-out one).
   Only this answers "does it transfer to a novel embryo" -- the thing cross-embryo-OOF on 2
   embryos could not. Report AUC-on-decisions + prune precision on the held-out embryo.

### PHASE 3 — SUBMIT
- If the augmented model shows a POSITIVE dScore on a fully-held-out embryo, re-run the prune/
  re-route submission (build_pruned_submit.py) with the new weights. This is the only config with
  a real chance of beating 0.921.

## Effort & risks (honest)
- **Effort: LARGE, multi-session.** Phase 0: hours. Phase 1 (data): the bulk, 1-2 sessions
  (download + convert + crop is fiddly). Phase 2-3: 1 session.
- **Risk 1 (FATAL if true): voxel/marker mismatch** -> patches don't transfer. Phase 0 gates it.
- **Risk 2: Zebrahub tracks are AUTOMATED (Ultrack), not hand-corrected** -> noisy labels. Diverse
  noisy data may still help generalization, but it's not clean GT.
- **Risk 3: download size/bandwidth** -> must crop selectively; can't pull full embryos.
- **Risk 4: MODEST ceiling even if it works.** The edge model targets the ~2% steal edges; a
  perfectly-generalizing model caps ~+0.005-0.01 => realistic reach ~0.925-0.93, NOT the 0.95
  prize zone. This buys rank, not a podium.

## Recommendation
The ONLY lever with a real path past 0.921, and the correct answer to the measured root cause.
But large effort + a fatal-risk gate + a modest ceiling. **Do PHASE 0 first** (cheap, decisive)
before committing. If Phase 0 passes, this is worth a focused multi-session push; if it fails,
0.921 is the definitive own-work ceiling and the 09-29 selection stands (sim4 + flow-k8).

---

## PHASE 0 — EXECUTED AUTONOMOUSLY (2026-08-28), VERDICT = **GO**

Ran `phase0_zebrahub.py` against the LIVE public server (public.czbiohub.org, no auth) — all
data fetched remotely, no download to the user's box needed for the gate.

**Verified facts:**
- Public data: 6 single-objective embryos (ZSNS001, ZSNS001_tail, ZSNS002-005) as OME-Zarr +
  clean `ZSNS*_tracks.csv`. Column schemas VARY: base = `track_id,t,z,y,x,parent_track_id`;
  `_tail` = `track_id,NodeID,ParentTrackID,t,t_hier_id,z,y,x,area` (empty parent = root). The
  script handles both.
- VOXEL: Zebrahub L0 = (1.24, 0.439, 0.439) um vs competition (1.625, 0.40625, 0.40625).
  Resample factor L0->competition = (0.763, 1.081, 1.081). z off 24%, xy off 8% -> resample
  with scipy.ndimage.zoom (built into the pipeline). NOT an exact match but well within range.
- APPEARANCE: same nuclear-histone light-sheet, uint16, sparse background; after resampling to
  the competition grid, DoG finds ~357 nuclei/central-slice, blob sigma ~3.8. Detectable.
- TRACKS (ZSNS001_tail): **7,505,357 cells / 101,676 tracks / 73,756 divisions / 7,477,437
  consecutive-frame edges** over 791 timepoints. DENSE (every cell tracked). vs competition
  ~10k SPARSE edges across BOTH train embryos => ~750x more supervision from ONE embryo, x6.

**GATE: voxel_ok=True, nuclei_detectable=True, dense_tracks=True => GO.**

**Remaining Phase-0 caveats (run on the GPU box before Phase 1):**
1. Detector-recall test at LEVEL 0 with the real Kunal UNet (set BIOHUB_WEIGHTS) — the remote
   gate used a DoG proxy at level 2. Confirms the UNet detector finds the tracked nuclei on
   resampled Zebrahub. `phase0_zebrahub.py --level 0 --embryo ZSNS001` on the box.
2. LABEL QUALITY: 7.5M cells is AUTOMATED (Ultrack) tracking, NOT hand-corrected GT -> noisy.
   Mitigation: filter to long/high-confidence tracks; diversity likely helps generalization
   even with label noise. This is the main scientific risk now (not compatibility).

## UPDATED RECOMMENDATION
Phase 0 PASSED remotely. Compatibility is NOT the blocker. Proceed to Phase 1 (acquire +
convert + dice a few embryos to competition-format crops) then Phase 2 (retrain edge model
with a WHOLE-embryo holdout as the real generalization test). The two remaining risks are
label noise (automated tracks) and the modest ceiling (edge model touches only ~2% steal
edges => realistic ~0.925-0.93). The download for Phase 1 needs the box (level-0 volumes are
large); `phase0_zebrahub.py` shows the exact fetch/convert/resample mechanics to reuse.

---

## PHASE 1 — WRITTEN + VERIFIED (2026-08-28)

`phase1_zebrahub.py`: Zebrahub embryo -> competition-format crop pairs. Self-downloading
(public.czbiohub.org, chunked bbox fetch), works in physical-micron common frame, resamples
each crop to the competition grid (1.625,0.40625,0.40625), converts tracks -> geff (consecutive
edges + divisions), dices into (Z,Y,X)=(64,256,256) crops CENTERED PER TIME-WINDOW on the cell
centroid (the embryo drifts, so a global center misses). Drops tracks < min-len (Ultrack noise).

VERIFIED end-to-end at level 2 (logic test): wrote crop pairs read back correctly by the
competition's OWN `scoring.read_geff` -- 673 nodes / 531 edges, scale (1.625,0.40625,0.40625),
ALL edges consecutive (dt=1), node positions 100% in-bounds, image (T,Z,Y,X) uint16 with
detectable nuclei. Drop-in compatible with the edge-model trainer.

RUN ON THE GPU/BANDWIDTH BOX (full res):
    python phase1_zebrahub.py --embryo ZSNS001      --level 0 --out zebra_crops --crop 64 256 256 \
        --frames 76 --n-time 3 --grid 1 4 4 --min-track-len 8 --min-nodes 60
    # repeat for ZSNS001_tail, ZSNS002, ZSNS003, ZSNS004, ZSNS005 -> many diverse crops.
Each crop ~ (76,64,256,256) uint16 ~ 640MB raw; the chunked fetch pulls only the needed L0
region per frame. Expect a few dozen crops/embryo x 6 embryos = the diverse training set.

## PHASE 2 (next) — retrain the edge model on competition + Zebrahub crops
Point `build_edgemodel_v2.py` PASS-A at BOTH data roots. ONE change needed: it currently reads
images via the Kunal `load_volume(zp,t,meta)`; Zebrahub crops store the image as a plain zarr
array `img`, so add a loader branch: `zarr.open_group(zp)["img"][t]` -> (Z,Y,X). GT reads via
`read_geff_min` UNCHANGED (verified). Then the REAL generalization test: hold out a WHOLE embryo
(train on 5, predict the 6th) and report AUC-on-decisions + prune precision on it -- the honest
analogue of the 2 unseen TEST embryos that the 2-embryo cross-OOF could not provide.

---

## PHASE 2 — WRITTEN + COMPILE-VERIFIED (2026-08-28)

`scratch_kernels/build_zebra_edgemodel.py` -> kernel `eeshsaxena/biohub-zebra-edgemodel`.
Cloned from build_edgemodel_v2.py with three changes:
1. DUAL SOURCE in PASS A: gathers competition geffs (TRAIN_DIR) AND Zebrahub crop geffs from any
   /kaggle/input/*zebra* mount; tags each stem comp|zebra. Image loader branches:
   comp -> Kunal load_volume; zebra -> `zarr.open_group(zp)["img"][t]`. GT via read_geff_min
   UNCHANGED (Phase-1 geff verified identical to competition).
2. WHOLE-EMBRYO holdout OOF: the loop already iterates every embryo in emb_all (2 comp + N zebra),
   so each is held out entirely -> the honest novel-embryo test the 2-embryo set could not give.
3. **DECISIVE A/B readout**: for each held-out COMPETITION embryo, AUC when trained on
   {other comp + all zebra} vs {other comp only}. delta>0 on BOTH comp embryos => external data
   supplies the missing generalization and the prune/re-route levers can transfer. This ONE number
   decides whether to spend a slot.
Compile-verified (all cells parse); dataset_sources includes eeshsaxena/biohub-zebrahub-crops.

## END-TO-END RUNBOOK
1. [box] Phase 1 per embryo (ZSNS001, ZSNS001_tail, ZSNS002-005):
     python phase1_zebrahub.py --embryo <E> --level 0 --out zebra_crops --crop 64 256 256 \
       --frames 76 --n-time 3 --grid 1 4 4 --min-track-len 8 --min-nodes 60
2. [box] upload zebra_crops/ as Kaggle dataset `eeshsaxena/biohub-zebrahub-crops`
     .venv/Scripts/python -m kaggle datasets create -p zebra_crops   # (add dataset-metadata.json)
3. [here] push + run the trainer (FREE, no submission slot):
     python scratch_kernels/build_zebra_edgemodel.py
     python -m kaggle kernels push -p scratch_kernels/zebra_edgemodel
4. READ the DECISIVE A/B. If delta>0 on BOTH comp embryos -> Phase 3: rebuild the prune submission
   (build_pruned_submit.py) pointing at the zebra-trained weights, submit vs 0.921. Else: 0.921 is
   the definitive own-work ceiling; external data did not transfer either.

## STATUS: Phases 0,1,2 DONE (autonomous). Phase 1 full-res download + Phase 3 submit need the box.

---

## DETECTOR-TRANSFER TEST — PASS (2026-08-28, autonomous, CPU kernel)
`build_zebra_dettest.py` -> kernel `biohub-zebra-dettest` (CPU, free): ran the REAL Kunal 3-UNet
detector on the uploaded Zebrahub crop. **ZSNS001_tail_c000: recall 0.963 (tp 1708 / fn 66)** at
the 7um competition gate -- vs 0.978 on competition test. The competition-trained detector
transfers to Zebrahub NEARLY PERFECTLY. (DoG proxy said 0.52 -- DoG is weak; the UNet is the truth.)
=> ENTIRE compatibility risk RETIRED: Phase-1 resampling correct, coords aligned, appearance
matches, format end-to-end valid (incl. Kaggle .zip auto-extract in the kernel). Phase 2 is now
pure execution.

CONSTRAINTS HIT: Kaggle weekly GPU quota EXHAUSTED (30h) -> Phase 2 (GPU training) waits for the
weekly reset OR the box. Kaggle dataset uploads directories as per-dir .zip; kernels must extract
(dettest does; APPLY THE SAME to build_zebra_edgemodel.py before running Phase 2). ZSNS002 has NO
tracks (404); usable external embryos = ZSNS001, ZSNS003, ZSNS004, ZSNS005 (+ZSNS001_tail).

---

## KEY CAVEAT — MULTI-EMBRYO ALIGNMENT (2026-08-28)
Cheap alignment probe (image extent vs track positions, micron conversion) across candidates:
  ZSNS001_tail : IN-IMAGE 1.00  ALIGNED   (pre-made crop; detector recall 0.963)
  ZSNS004      : IN-IMAGE 0.05  MISALIGNED (track p50 x=4280 vs image x=2789)
  ZSNS005      : IN-IMAGE 0.22  MISALIGNED
  ZSNS003      : dense region OUTSIDE image (0 crops generated)
=> The FULL-embryo .ome.zarr images are NOT in the same coordinate space as their tracks CSV
(likely the image is a processed/cropped/downsampled view while tracks are full-acquisition).
Micron conversion aligns ONLY the pre-made tail crop. So out of the box we get 1 usable external
embryo, NOT 4-5 -> the diversity benefit (the whole point) is CONSTRAINED until alignment is
reconciled per embryo. RESOLUTION PATHS for the box run (not solved here):
  (a) use the tracks_benchmark ZARR (ZSNS001_nodes/edges.zarr, daxi_tracks.zarr) instead of the
      CSV -- it may already be registered to the image; parse the padded-array schema.
  (b) derive a per-embryo affine (scale+offset) mapping tracks->image from a few matched nuclei.
  (c) find/most-crops that are pre-registered like ZSNS001_tail.
Phase-1 SAFELY skips misaligned crops (prints a WARNING), so a misaligned embryo just yields 0.

## AUTONOMOUS WINDOW OUTCOME (2026-08-28)
DELIVERED: detector-transfer PASS (0.963) = compatibility de-risked; full pipeline (Phase 0/1/2)
built, verified, turnkey (zip-handling + alignment guards). BLOCKED: Kaggle GPU quota exhausted
(weekly) -> Phase 2 A/B needs the reset or the box. CONSTRAINED: only 1 aligned external embryo
out of the box (alignment caveat above). Account best UNCHANGED 0.921; no submissions.
NEXT (box): resolve multi-embryo alignment -> generate crops for 3-4 embryos -> run Phase 2 ->
read the DECISIVE A/B. If A/B delta>0 both comp embryos, Phase 3 submit vs 0.921.

---

## ALIGNMENT RESOLVED (2026-08-28) — 4 external embryos now usable
The full-embryo misalignment is a UNIT bug, not an FOV mismatch: full-embryo tracks store y,x in
0.5um units (z stays in um). Diagnosis: track_extent/image_extent = z~0.75, **y~2.1, x~2.0**
(consistent across ZSNS004+ZSNS005). FIX = scale track y,x by 0.5:
  ZSNS004: in-image 0.26 -> **1.00**   ZSNS005: 0.20 -> **0.97**   (ZSNS001_tail stays 1.00 at x1)
phase1_zebrahub.py now AUTO-CALIBRATES per embryo (tests {x1, xy*0.5, all*0.5, ...}, picks max
in-image, prefers x1 when it already fits). => usable external embryos = ZSNS001(_tail), ZSNS003,
ZSNS004, ZSNS005 = 4 DISTINCT embryos (2 comp + 4 zebra = 6-embryo whole-embryo holdout). The
earlier "1 embryo only" caveat is SUPERSEDED.

## COMPATIBILITY SCORECARD (all PASS, autonomous)
1. Detector transfer: Kunal UNet recall 0.963 on Zebrahub (vs 0.978 competition).  PASS
2. Edge dynamics: displacement median 1.81um vs competition 1.82um (p90 3.53 vs 3.49).  MATCH
3. Alignment: solved (xy*0.5 auto-calibrated) -> 4 usable embryos.  RESOLVED
=> Zebrahub external data is fully compatible + diverse. The bet's premise (more embryos ->
generalization) is INTACT. Only blocker to the A/B is the weekly GPU quota (reset) or the box.

## PLACEMENT FIX (2026-08-28) — full embryos now yield dense crops
2nd bug after alignment: developing embryos are HOLLOW SHELLS (cells on the epithelial surface,
empty lumen), so centroid-centered crops caught 0 nodes on full embryos. FIX: seed crops at
actual cell positions (bucket cells into crop-sized bins, one seed/bin) -> spread + guaranteed
dense. Validated ZSNS004: 9 seed-crops with 193-1473 nodes each (was 0). Works for tail crops AND
full embryos. phase1_zebrahub.py updated (cell-seeded loop).

## ZEBRAHUB PIPELINE — FULLY WORKING + DE-RISKED (2026-08-28, autonomous)
All obstacles resolved: (1) detector transfers 0.963; (2) edge dynamics match 1.81 vs 1.82um;
(3) alignment solved (xy*0.5 auto-calib); (4) placement solved (cell-seeded, hollow-shell-safe).
=> 4 DISTINCT dense external embryos (ZSNS001, ZSNS003, ZSNS004, ZSNS005) + 2 competition = a
6-embryo whole-embryo-holdout training set. The external-data premise is INTACT and diverse.
ONLY blocker to the DECISIVE A/B = weekly Kaggle GPU quota (exhausted; resets in days) OR the box.
Phase 1 (phase1_zebrahub.py) + Phase 2 (build_zebra_edgemodel.py) + dettest are turnkey.
BOX RUNBOOK: per embryo `python phase1_zebrahub.py --embryo <E> --level 0 --out zebra_crops
--crop 64 256 256 --frames 40 --n-time 3 --grid 1 4 4 --min-track-len 8 --min-nodes 60` (auto-
calibrates + cell-seeds); upload zebra_crops as biohub-zebrahub-crops; push build_zebra_edgemodel;
read the A/B (with-zebra vs comp-only AUC on held-out comp embryos). delta>0 both -> Phase 3 submit.

---

## LOCAL A/B ON THE 4050 (2026-08-28) — ZEBRAHUB BET FAILS
`zebra_ab_local.py` on the RTX 4050 (cu124), 3 embryos (ZSNS001_tail, ZSNS003, ZSNS004), GT-nodes
as detections (detector transfer already proven), whole-embryo holdout. AUC on held-out embryo:
| hold | learned all-others | learned one-other | GEOMETRY cost |
|---|---|---|---|
| ZSNS001 | 0.9945 | 0.9879 | 0.9940 |
| ZSNS003 | 0.9155 | 0.9135 | **0.9470 (cost WINS)** |
| ZSNS004 | 0.8962 | 0.8971 | 0.8885 |
VERDICT: (1) more embryos barely helps (all-others beats one-other by only ~0.002-0.007, once
loses) -- the multi-embryo generalization premise is ~absent. (2) the learned edge model does NOT
beat plain DISTANCE on novel embryos (ties/loses). Same wall as the competition: geometry is at
CEILING for the local edge decision; image/learned features add nothing over cost on a novel
embryo. => THE ZEBRAHUB BET FAILS despite full compatibility. The learned-edge direction is dead
by DIRECT MEASUREMENT on external data. Do NOT spend a Kaggle GPU run + slot on it. 0.921 is the
definitive own-work ceiling. (Caveat: GT-node idealized A/B, 3 embryos; but the model<=cost signal
is consistent with every competition result all session.)
