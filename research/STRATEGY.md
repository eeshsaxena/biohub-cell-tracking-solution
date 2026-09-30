# Biohub: Cell Tracking During Development — competitive strategy

Derived from the competition pages, the official scorer source
(`royerlab/kaggle-cell-tracking-competition`), and the public discussion as of
2026-07-28.

---

## 1. The situation

| | |
|---|---|
| Prize | $60,000 (1st $18k, 2nd $12k, 3rd $8k, 4th/5th $6k, 6th/7th $5k) |
| Final submission | 2026-09-29 (entry + team merger 2026-09-22) |
| Format | Code competition, notebook only, **no internet**, **12 h runtime cap** |
| External data | Freely and publicly available data + pretrained models allowed |
| Field | ~1,730 teams, ~20k submissions |
| Public LB | 29% of test. Private = the other 71% |
| Data | 87.6 GB, 199 train samples, 2 embryos (`44b6`, `6bba`), split 71 / 128 |
| Test | ~similar size, **2 different embryos**, disjoint from train |

Leaderboard shape right now: #1 = 0.942, then a dense cliff. Ranks 20 through 49
sit inside 0.913 to 0.916. That is ~30 teams within 0.003 of each other.

Two things follow immediately:

1. **The pack is running the same public pipeline.** Beating 0.916 by a hair is
   worth nothing; the top needs +0.03 over the pack.
2. **The private shakeup will be violent.** Two test embryos, a 29/71 split, and
   a thousand teams inside a 0.03 band. If the public split is dominated by one
   embryo and private by the other, most of that pack reshuffles randomly.
   *Generalization across embryos is the whole game.* LB probing is noise.

---

## 2. The metric, decoded from source

```
score = adj_edge_jaccard + 0.1 * division_jaccard
```

`adj_edge_jaccard` is per-sample, weight-averaged by `(TP+FP+FN)`.
`division_jaccard` is micro-averaged (counts summed globally, then Jaccard).

Node matching: optimal bipartite assignment on centroid distance per timepoint,
scaled by `(z, y, x) = (1.625, 0.40625, 0.40625)` µm/voxel, max 7.0 µm.

Seven properties of the implementation that matter, several of which the field
appears not to be exploiting:

### P1 — Edges between unmatched nodes are completely free

```python
pred_valid = out_valid(source) | in_valid(target)
```

An edge enters the denominator only if its source matched a GT node with
out-degree ≥ 1, **or** its target matched a GT node with in-degree ≥ 1. Ground
truth is sparse (a small fraction of cells are annotated), so the overwhelming
majority of your predicted edges are invisible to the metric: not TP, not FP.

**Consequence: precision on unannotated cells costs nothing** in the edge term.
Measured annotation density is 0.737%, so over 99% of predicted edges are
invisible to the scorer.

**But this does not license unlimited over-detection.** False-positive *edges*
are free; extra *nodes* are not, because they feed the node-count term (P2).
The clamp there is brutal: at `N_pred > 11 x n_total` the adjusted Jaccard is
`max(0, ...)` and the sample scores exactly **zero**. Over-detect modestly, into
the ratio 0 to +0.3 band, and let the sweep pick the point.

### P2 — The node-count penalty is signed, and mild

```python
total_node_ratio = (num_pred_nodes - n_total) / n_total
adj = max(0, edge_jaccard * (1 - 0.1 * total_node_ratio))
```

`n_total` is `estimated_number_of_nodes` from the GEFF metadata (the *true* cell
count, not the annotated count). The coefficient is 0.1, and the term is signed:

* predict 2× too many nodes → ×0.90 (a mere 10% cost)
* predict 1.5× too many → ×0.95
* predict 0.8× → ×1.02

**Correction (measured).** I initially read the signed term as meaning
under-detection is rewarded. It is not. A competitor running at ratio 0.85–0.95
reported that cutting node count a further 17% cost **~0.18 edge Jaccard**,
against a node-term gain of ~1.5%. Recall dominates this term by an order of
magnitude. Treat the node-count penalty as a mild secondary correction to apply
*after* maximising recall, never as a lever in its own right.

So: over-detect, then trim to budget. The one scalar worth sweeping is the
detection threshold, tuned directly against the official metric, not F1.

**Actionable:** you cannot read `n_total` for the hidden test set, but you can
*predict* it from cheap image statistics on the 199 training samples. Note this
is no longer novel: a public notebook already exposes `USE_COUNT_CALIBRATION`,
and one competitor reported it changing nothing (0.728 → 0.728). Worth doing
properly, but budget it as ~0.005, not a differentiator.

### P3 — Only consecutive-frame edges count; gap edges are silently deleted

```python
.filter(pl.col("_target_t") - pl.col("_source_t") == 1)
```

A `t → t+2` edge is dropped before scoring. Not FP, just gone. This is why
"gap closing" was reported as neutral by early competitors: as a long edge it is
literally a no-op.

**Actionable:** when a detection is missed at `t+1`, do not draw a long edge.
**Interpolate a node** at `t+1` and emit two consecutive edges. If the
interpolated centroid lands within 7 µm of the real GT node you gain 2 TPs.
Displacements are tiny (see P7), so interpolation is a favourable bet. Tune the
maximum gap length on CV.

### P4 — Divisions are cheap to attempt and worth up to 0.1

A predicted fork counts as a false positive only if it is:

* `evaluable`: the fork node matched a GT node that has out-degree ≥ 1, or
* `cross_component`: its two child branches match GT nodes in **different** GT
  tracks, or
* `malformed`: a child of the fork has a predecessor other than the fork, or
* `considered`: it sat inside a GT division window and failed the topology test.

A fork on an unannotated cell, with unmatched daughters, is **not counted at
all**. Given sparse GT, most predicted divisions are free.

**Correction (measured).** I first called this the biggest unexploited lever.
Having read the actual ground truth, that was too optimistic. Only **0.24
divisions per sample are annotated** (6 across 25 samples), so the whole train
set holds roughly **48 GT divisions**, and test likely similar.

What that changes:
* A *learned* division classifier is off the table. 48 examples is not a
  training set. This has to be rule-based, thresholded conservatively.
* The term stays worth chasing because the denominator is tiny: recovering 20
  of ~48 divisions with 20 false positives gives Jaccard 0.33, i.e. **+0.033**,
  which is still roughly the pack-to-first gap.
* But it is high variance. A handful of divisions swings it. Do not tune this
  on a small CV subset and believe the number.
* Every public report of naive division emission lost score (0.784 → 0.778,
  and 0.728 → 0.695 with `DETECT_DIV=True`). Ship v1 with divisions **off**,
  and only enable once it beats the off setting on full leave-one-embryo-out.

Hard constraints to respect when emitting forks:
* every node must have **in-degree ≤ 1** (a merge makes the parent fork
  `malformed` → FP)
* every node must have **out-degree ≤ 2** (extras are truncated by lowest edge
  id, unpredictably)
* never fork into two branches that belong to different GT lineages

### P5 — Duplicate and merged edges are collapsed

Duplicate `(source, target)` pairs are deduped; multiple predicted edges mapping
onto the same GT edge keep only the lowest edge id. Track-duplication tricks
were patched out. Do not waste time there.

### P6 — The division-metric exploit is dead

The far-away synthetic hub/fork trick that produced 0.950 was patched and all
submissions were re-scored. Current LB numbers are honest. Ignore it.

### P7 — Motion is tiny, but the acquisition is not clean

Measured per-frame displacements (from public EDA): median 0, p90 ≈ 1–2 voxels,
p95 ≈ 2, p99 ≈ 4, with rare outliers of ±35. Against a 7 µm matching radius,
a correctly detected cell is nearly always trivially linkable.

But the raw data contains **frozen frames** (`vol[t] - vol[t+1] == 0` exactly)
and **sudden global volume jumps**, most likely acquisition artifacts.

**Actionable:** estimate a global rigid shift per frame pair (3D phase
correlation, or the robust median of local displacements) and subtract it before
linking. Cheap, and it converts the jump frames from catastrophic to routine.
Detect frozen frames explicitly and handle them as identity.

---

## 3. Where the points actually are

Ranked by expected gain over the 0.914 pack:

| Lever | Est. gain | Why the field is missing it |
|---|---|---|
| Detection recall via pseudo-label self-training | **+0.01 to +0.03** | Sparse GT (0.737%) makes naive supervised training weak |
| Gap interpolation as nodes, not edges (P3) | +0.005 to +0.015 | Long edges are a silent no-op, so this reads as "neutral" |
| Careful rule-based divisions (P4) | +0.01 to +0.03, high variance | Only ~48 GT divisions; everyone gave up after naive attempts lost score |
| Global motion compensation (P7) | +0.005 to +0.01 | Frozen/jump frames are not obvious |
| Threshold tuned on the *official* metric, not F1 | +0.005 to +0.01 | Proxy metrics mislead here |
| Node-count calibration to predicted `n_total` (P2) | ~+0.005 | Already in a public notebook, reported as no-change |

### Measured ground-truth facts (25 samples of `44b6`)

| | |
|---|---|
| Annotation density | 0.737% of cells annotated |
| Annotated tracks per sample | ~2.6 (~260 nodes over 100 frames) |
| `estimated_number_of_nodes` | median 31,937/sample, range 7,436–78,644 |
| Implied cell density | ~320 cells/frame typical, up to ~790 |
| Implied cell diameter | ~14–19 µm |
| GT divisions | 6 in 25 samples (0.24/sample) |
| Displacement p50 / p90 / p99 | 1.82 / 3.45 / 7.45 µm |
| GT edges inside the 7 µm radius | 98.8% |
| GT edge time deltas | all dt = 1 |

The last two lines are the design constraint: linking is near-trivial for a
correctly detected cell, so effort belongs in detection.

None of these are individually decisive. Stacked and validated properly, they
are the difference between rank 30 and the prize zone.

---

## 4. Validation protocol (the single most important decision)

With 2 train embryos and 2 unseen test embryos, **the only honest signal is
leave-one-embryo-out**.

1. Fold A: train on `44b6` (71 samples), validate on `6bba` (128).
2. Fold B: train on `6bba`, validate on `44b6`.
3. Report both. **Trust the worse one.** The test embryos are new; the gap
   between folds is your best estimate of cross-embryo variance.
4. Score with the official `summarise()`, not a hand-rolled average. Adjusted
   edge Jaccard is weight-averaged by `TP+FP+FN`; division Jaccard is
   micro-averaged. Naive per-sample averaging will lie to you.
5. Keep a CV-vs-LB scatter on every submission. Any change that raises CV and
   lowers LB is an embryo-specific overfit: discard it.
6. **Scoring is fast; inference is not.** The 5–11 h figures on the forum are
   the notebook *building predictions*, not the scorer. The hosts' metric code
   scores the whole train split in about a minute. So local CV iteration is
   cheap and there is no excuse for LB probing, but the 12 h submission cap is
   a genuine engineering constraint on the pipeline itself.

Any tuned constant (threshold, NMS radius, gap length, division threshold) must
be selected on the *held-out* embryo, never on both.

---

## 5. Architecture plan

### Stage 1 — Detection (dominant term)

The blocker is that GT is sparse, so a standard dense segmentation loss is
poisoned by unlabelled positives being treated as background.

Recipe, in order:

1. **Classical detector first.** Multi-scale DoG/LoG in *isotropic* resampled
   space (the z anisotropy is 4×, so resample or scale the kernels). Scale-space
   maximum. This alone reached 0.826 publicly and is a strong pseudo-label
   source.
2. **Measure it against sparse GT** — recall at 7 µm on annotated cells only.
3. **Pseudo-label the whole volume** with the classical detector, optionally
   cross-checked against a second free detector (Cellpose 3D, StarDist-3D; both
   are freely available pretrained models and therefore allowed).
4. **Train a 3D U-Net on the dense pseudo-labels**, then fine-tune on the sparse
   GT with a masked loss. This converts a sparse-label problem into a dense one,
   which is the standard fix and what the strongest public commentary points at.
5. Alternative loss worth testing: **learnable peak detection** — instead of
   binary classification, a local softmax over each annotated voxel's
   neighbourhood, with unannotated regions excluded from the loss entirely.
   A margin variant (peak must exceed neighbours by T) is a good ablation.

Anisotropy matters: use anisotropic kernels or resample to isotropic; a naive
isotropic 3D conv stack wastes capacity on the z axis.

### Stage 1b — HOCT, the highest-upside shortcut

The hosts published **HOCT** (Higher-Order Cell Tracking Transformer, Bragantini,
Theodoro & Royer), with inference code and pretrained weights at
`royerlab/hoct`. It is edge-centric: candidate links attend to each other under
3D geometric constraints, which is aimed squarely at the two failure modes here
(divisions entangling lineages, and edges sharing a node having near-random
label agreement). It reports state of the art on the Cell Tracking Challenge.

Why this is worth trying early:
* Pretrained models are explicitly allowed ("freely & publicly available
  external data is allowed, including pre-trained models").
* Its default tile config is `(t, z, y, x) = (1, 64, 256, 256)`, which is
  *exactly* this dataset's frame shape.
* Jordão Bragantini (a host) posted it and said they have not tried it on the
  competition data, so the field has probably not either.

Two caveats, both real:
* It consumes **segmentation masks**, not points. Our detector produces points,
  so render each detection as a synthetic sphere (the same trick used to feed
  Ultrack in this competition). Host's note: "tracking results depend on the
  quality of the segmentation mask."
* Weights download on first use, and the submission notebook has no internet.
  They must be fetched once and shipped as a Kaggle Dataset.

Treat this as the v2 experiment right after v1 lands, not as the first
submission: it is unvalidated on this data and could easily underperform a
tuned classical linker.

### Stage 2 — Linking

1. Global rigid motion compensation per frame pair (P7).
2. Candidate edges within a gated radius (7 µm is the metric's tolerance;
   p99 displacement is ~4 voxels, so gate generously but not absurdly).
3. **Global optimization, not greedy frame-by-frame Hungarian.** Min-cost flow
   / ILP over a sliding window of frames. `motile` (funkelab) does this and is
   pip-installable — ship it as a Kaggle dataset since inference has no
   internet.
4. Optional learned affinity: a small model scoring `(node_t, node_{t+1})` pairs
   on local appearance + displacement, used as edge cost. The official baseline
   does this with a cross-attention transformer; the public reports say its long
   links are almost always wrong and trivially filterable.
5. Gap interpolation as *nodes* (P3).

### Stage 3 — Divisions

A dedicated binary classifier over `(parent_t, child_a, child_b)` triplets:

* Features: parent intensity and roundness (mitotic cells round up and
  brighten), the two children's separation, symmetry of the split, local
  density, displacement residual.
* Train on GT divisions from the sparse annotations across all 199 samples.
* Threshold tuned to maximize `division_jaccard` on the held-out embryo.
* Enforce the graph constraints from P4 (in-degree ≤ 1, out-degree ≤ 2, no
  cross-lineage forks).

### Stage 4 — Calibration

* Predict `estimated_number_of_nodes` per test sample; set the per-sample
  detection threshold so `N_pred` hits the target (P2).
* Sweep the global threshold / NMS radius / gap length jointly against the
  official metric on the held-out embryo.

---

## 6. Compute plan

Local machine: RTX 4050 Laptop (6 GB VRAM), 15.6 GB RAM, 97 GB free disk.
The dataset alone is 87.6 GB, so a full local copy is not viable.

* **Local:** a 20–30 sample subset spanning both embryos, for fast iteration on
  detection and the CV harness. Download selectively via the Kaggle API.
* **Training:** Kaggle notebooks (30 h/week GPU quota) or Colab. 6 GB VRAM is
  workable for patch-based 3D U-Net training at small batch size, but slow.
* **Inference is a hard constraint.** ~150 test samples × 100 frames ×
  (64, 256, 256) uint16 ≈ 126 GB streamed, inside 12 h. That is roughly
  **4.8 min per sample including I/O**. This rules out heavy ensembles and
  large test-time augmentation. Design for one efficient network in fp16, and
  profile inference *early*, not in the final week.

---

## 7. Nine-week plan (2026-07-28 → 2026-09-29)

| Week | Goal | Exit criterion |
|---|---|---|
| 1 | Environment, data subset, **CV harness reproducing the official metric exactly** | Score a known submission locally and match a known LB value |
| 1 | Join competition, accept rules, submit the public baseline unchanged | A real LB anchor point |
| 2 | Classical multi-scale DoG detector + motion compensation + global linking | LOEO CV ≥ 0.85 |
| 3 | Node-count calibration + threshold sweep on the official metric | +0.01 over week 2 |
| 4 | Gap interpolation as nodes; graph sanity constraints | +0.01 |
| 5 | Division classifier | division Jaccard ≥ 0.25 |
| 6 | Pseudo-label generation + 3D U-Net detector v1 | Beats the classical detector on the held-out embryo |
| 7 | Self-training round 2, learned linking affinity | LOEO CV ≥ 0.93 |
| 8 | Inference optimization to fit 12 h; full-scale dry run | End-to-end submission under 10 h |
| 9 | Ensembling, final threshold calibration, **select 2 submissions by CV not LB** | Submitted with margin |

Hard rule for week 9: pick final submissions by leave-one-embryo-out CV, not by
public LB. With a 29/71 split and a thousand teams inside 0.03, the public board
is close to a coin flip.

---

## 8. Honest risk assessment

* 1,730 teams and $60k means several Kaggle Grandmasters are in this. Multiple
  active competitors are cell-tracking researchers, and the host's own group
  wrote Ultrack, the SOTA method this benchmark is built around.
* Winning outright is not something anyone can promise. A realistic, aggressive
  target for a focused two-month effort is **top 10** (all seven prize slots pay,
  down to $5,000), with gold-medal placement being the more probable good
  outcome.
* The largest single risk is not modelling, it is validation discipline. The
  shakeup will punish LB-chasing more than it punishes weak models.

---

## 9. Key resources

* Official repo (metric, baseline, csv↔geff): https://github.com/royerlab/kaggle-cell-tracking-competition
* Higher-order cell tracking (host co-authored): https://github.com/royerlab/hoct
* Ultrack: https://github.com/royerlab/ultrack
* Trackastra: https://github.com/weigertlab/trackastra
* motile (ILP tracking): https://github.com/funkelab/motile
* Cell Tracking Challenge: https://celltrackingchallenge.net/
* geff format: https://github.com/live-image-tracking-tools/geff
