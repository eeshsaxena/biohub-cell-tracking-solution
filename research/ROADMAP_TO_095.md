# Roadmap to 0.95 — Biohub cell tracking (2026-08-23)

Current account best **0.919** (`fill1`: aggressive gap-fill on the Kunal 0.917
stack). Post-processing is now thoroughly mapped and **capped ~0.919** (see
`RECALL_RESEARCH.md`): fill helps (+0.002); division-relax, detection-union,
threshold-lowering, NMS-shrink, MAX-fusion all hurt or are dead (LB- and
adversarial-panel-confirmed). Reaching 0.94-0.95 needs MODEL work. This ranks the
directions by EV × tractability, grounded in a gap decomposition.

## The gap decomposition (why divisions are the lead lever)

`score = adj_edge_jaccard + 0.1·division_jaccard`, and `edge_J ≈ recall²`.
- Our recall ≈ **0.978** → edge ceiling ~0.956; observed edge ~**0.906**.
- Our div_jaccard ≈ **0.13** (Kunal VAL-24 6/31/8) → contributes ~0.013.
- 0.906 + 0.013 = **0.919** ✓ (reproduces the LB).

Every public detector plateaus near recall 0.978, so the **edge term is
detector-limited to ~0.906 for the whole pack** (confirmed by `exp_edge_decomp.py`:
appearance-linking already recovers ~+0.40 over geometry; the residual is the hard,
detection-bound tail). That leaves the **0.1-weighted division term** as the only
lever with large, tractable headroom:

| scenario | recall | edge~ | div_jaccard | total |
|---|---|---|---|---|
| us (fill1, observed) | 0.978 | 0.906 | 0.13 | **0.919** |
| leader if edge-driven | 0.992 | 0.974 | 0.13 | 0.987 |
| **leader if division-driven** | 0.978 | 0.906 | **0.52** | **0.958** |
| **us + precise division detector** | 0.978 | 0.906 | **0.50** | **~0.956** |

The edge-driven scenario needs recall 0.99+ (no public detector reaches it → very
hard). The division-driven scenario is both **more plausible** (matches the pack's
recall plateau) and a **far smaller problem**. So:

## Direction A (LEAD) — a PRECISE learned division detector

Target: div_jaccard 0.13 → ~0.5 (≈ **+0.037** on the final score → ~0.956).

Why precision, not more forks: the LB showed *loosening* the geometric divergence
gate (2.25→1.0) HURT −0.016 — it admits broken-track-start FP forks. The current
heuristic is FP-dominated (6 TP / 31 FP). We need to keep the ~TPs while cutting
the FPs, i.e., a classifier, not a looser gate.

Plan:
1. **Candidate generation** (cheap, done): every 1-child parent whose track has a
   nearby orphan at t+1 is a fork candidate (the existing `_add_safe_divisions`
   proposal set, gates wide).
2. **Features per candidate** (image + graph): local image crops of parent/two
   children at t and t+1 (or reuse the detector heatmap/UNet features already
   computed), parent-child + sister distances, divergence trajectory (t+1→t+2),
   detection scores, motion. All available in the pipeline.
3. **Classifier**: small MLP/3D-CNN head → P(real division). Accept a fork only if
   P > τ, τ tuned on LOEO div_jaccard.
4. **Data problem** (the crux): real GT divisions are rare (~0.2/movie, ~40 in
   train). Pretrain on the shared **synthetic 3D microscopy set (~165k divisions,
   ~18.5 GB)** — LOCATE it on Kaggle + verify competition-rules eligibility (this is
   a hard dependency, not an assumption). Fine-tune the head on real GT. If the
   synthetic set is ineligible/unavailable, fall back to heavy augmentation +
   the two train embryos with LOEO, accepting a smaller div_jaccard gain.
5. **Gate before submit**: held-out (LOEO) div_jaccard must beat the shipped
   heuristic's ~0.13 by a real margin; edge term must not regress (the classifier
   only re-filters forks, so edges are unchanged except fork edges).

Feasibility: SMALL model, cheap to train (binary head after pretraining), runs over
a few hundred fork candidates/movie at inference → fits the 12h/T4 cap easily.

**UPDATE 2026-08-23 — `biohub-division-cv` LOEO result (REALITY CHECK):** on REAL
detections the LABELS are the wall, not the model. Wide-gate candidates are plentiful
(3k–25k/movie) but a trainable POSITIVE needs all 3 division nodes (parent + 2
daughters) detected AND matched to the specific GT divider/daughters at 7µm — which
almost never aligns. Result: **~3 positives in 12 movies**; the geometric baseline
itself scored **0 TP / 7 FP / 3 FN** on the subset. Can't train on ~3 positives, and
the division term looks LOW-YIELD on real detections for everyone. So:
  - Direction A is NOT a quick win. It needs (a) candidate/label extraction over
    ALL ~199 train movies (heavy) to gather ~tens of positives, AND (b) pretraining
    on the synthetic ~165k-division set (unconfirmed dependency) — appearance
    features (`division_detector.image_features`) added, ready for that v2.
  - The "leader gap = divisions" hypothesis is WEAKENED: if division TPs are this
    hard for the whole pack, the leader's +0.039 is more likely EDGE/detection
    (recall→~0.95) → Direction B (better base detector), the hard multi-week path.
  - Net: no quick path to 0.95 remains; fill1 0.919 is the validated near-term best.

Immediate refinement from the PENDING scores (55709019 fillnodiv, 55709022
filltightdiv): if `fillnodiv` (safe-div OFF) ≥ fill1, the shipped forks are already
net-harmful → the division-precision lever is confirmed and its headroom is the full
~0.1. If fill1 stays best, shipped forks are mildly net-positive and a precise
detector still adds on top.

## MAJOR UPDATE 2026-08-23 — public/CC0 assets UNBLOCK the model paths

Kaggle dataset search found the dependencies are PUBLIC (referenced in competition
discussion 732103; competition data is CC0):
- **`hitoshisaito/biohub-synthetic16-cc0-subset`** — CC0 synthetic 3D sequences
  (16 seqs, 27,696 nodes, **1,122 divisions**; full set = José Freitas generator).
  RESOLVES the division-detector labeling wall (dense division labels) AND is
  usable to train OWN prize-eligible weights.
- **`daifanhao/biohub-synthetic-detector-pretrain-public-v1`** — `unet_pretrained_
  detector.pth` (synthetic-pretrained detector, 12ep).
- **`justinkim1216/biohub-nnunet-flow-support-v1`** — `biohub_flow_unet.pt` +
  `source/model.py`: a residual 3D UNet with **center + offset + FLOW heads**
  (forward displacement to next frame). This IS the affinity-flow model (Direction
  B), already built + shared, with a companion "nnUNet Flow Infer" notebook doing
  flow-aware motion linking. Downsample (1,4,4), patch (32,128,128).
- `daifanhao/biohub-loeo-synth-code-public-v1` — `kaggle_loeo_train.py` (LOEO train).

Implication: both levers are now tractable, not from-scratch:
  A' (divisions): pretrain the DivMLP on the CC0 synthetic divisions (dense labels)
     -> FT on real GT -> apply to fill1 forks. Labeling wall resolved.
  B' (edge/linking): use the shared FLOW UNet's learned flow in fill1's linker
     (replace the velocity heuristic) -> targets the ~0.05 edge residual directly.
RULES CAVEAT: public weights tie the pack / likely don't qualify for PRIZE; for
prize, train OWN weights on the CC0 synthetic data. Verify the external-data rules
text on Kaggle before a prize submission. Assets pulled to scratch_kernels/pubassets.
Local pubassets: pretrain_manifest.json, DATACARD.md, model.py, README.md.

## Direction A — CLOSED (negative). Division learned-detector does not pan out.

Evidence (all concrete, this session):
- Shipped geometric safe-div (gate 2.25) is near-optimal and strongly net-POSITIVE:
  MEASURED +0.026 on the LB (fill1 0.919 vs fillnodiv 0.893). Looser (1.0)=0.903,
  tighter (3.0)=0.918, off=0.893. Little headroom left in the heuristic.
- Learned classifier on REAL detections: labeling wall (~3 positives / 12 movies;
  a positive needs all 3 division nodes detected+GT-matched at 7µm).
- Synthetic pretraining (CC0, 1,122 div, 265 balanced positives) DOES train, but
  **cross-domain transfer to real divisions FAILS: ROC-AUC 0.524 (~random)**, div_jaccard
  0.286 <= geom 0.333 (`exp_synth_pretrain_div.py`). Synthetic division geometry !=
  real. So the division term is effectively maxed by the geometric heuristic.
- Strategic read: if divisions were the leader's lever, the shared synthetic data
  would help — it doesn't. So the leader's +0.039 is most likely EDGE/DETECTION.

## Direction B — better base detector (recall 0.978 → 0.99)  [now the ONLY live path]

The edge-term path. Own-training the EXISTING host recipe re-derives only ~0.894
(<0.919), so this needs a genuinely BETTER recipe: the two-frame **affinity/flow +
center** model (`AFFINITY_FLOW_RESEARCH.md`) — dense pseudo-labels from multi-tracker
agreement + gold GT, pretrain center+motion on the synthetic set. Multi-week; loss
fix already known (host BCE `--det-neg-weight 1e-2`, avoids the 0.682 dense-MSE bug).
Kaggle cost is the blocker (~2.3h/epoch); needs a cheap-epoch recipe (smaller patch /
larger downsample / `--max-iters`, chained resume) or off-Kaggle GPU. Lower
tractability than A; pursue after A.

## Direction C — mega-ensemble detection average (recall probe)

Add pilkwang DeepCenter + seed314159 (and rep300 TemporalUNet3D) to the Kunal
3-branch heatmap AVERAGE (not union). Uncertain: those families are individually
weaker (0.912) and averaging risks diluting single-model detections (the union
already hurt). Heavy integration (different preproc/resolution/checkpoint formats).
Recall is likely near-saturated (0.978). Low priority; only a CV recall probe
(no submission cost) if A and B stall.

## Resource reality

Kaggle: 5 subs/day, 2 concurrent GPU, 12h/kernel, ~30h/week. Own-training and
synthetic pretraining likely need off-Kaggle GPU (Colab Pro / rented), then ship
weights as a Kaggle dataset for offline inference. The division detector (A) is the
one direction that plausibly fits Kaggle alone if the synthetic set is attachable.

## Prize note

Forking public weights ties the pack and likely doesn't qualify for prize money;
the division detector (A) and affinity-flow model (B) are own reproducible work.
No metric hacks (sentinel nodes / duplicate tracks / fake forks) — banned and under
host review.
