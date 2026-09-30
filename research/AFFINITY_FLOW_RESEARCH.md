# Legal next model: temporal affinity / flow

## Why this is the next real lever

The established `rep300` pipeline links accurate detections well but is capped
near 0.894. The practical bottleneck is detection recall and surviving short
motion discontinuities, not another linking-threshold sweep. Community research
also points toward scoring candidate `t -> t+1` links with a local temporal
affinity (or displacement/flow) field, then optimising a globally valid graph.

This document deliberately excludes sentinel nodes, duplicate tracks, fake
divisions, or any other metric exploit. A host discussion says the public
division exploit is being reviewed, so it is both unsafe and contrary to the
goal of genuine tracking accuracy.

## Target model

Input: a normalised pair of adjacent 3D frames, optionally concatenated with
the ensemble heatmap and a cheap global-motion estimate.

Outputs at every voxel:

1. center confidence at `t` and `t+1`;
2. a physical displacement vector from `t` to `t+1`;
3. an affinity/confidence for a proposed candidate pair;
4. an occlusion / no-link confidence.

Use the established high-recall detector to create candidate centers. For every
candidate at `t`, score only nearby `t+1` candidates under a physically safe
gate. Combine appearance/flow score with a global one-to-one optimizer; add a
small, separately calibrated division branch rather than changing the model's
main graph objective.

## Labels without fooling ourselves

- Gold positives: sparse official GT edges, with displacement in physical units.
- Gold negatives: spatially nearby but unmatched candidates from the same
  adjacent frame pair; sample hard negatives around the flow endpoint.
- Pseudo positives: links on which at least two independent trackers agree and
  whose motion agrees with the predicted global shift. Keep only short,
  one-to-one, consecutive-frame links.
- Never pseudo-label a candidate merely because one tracker made a long jump;
  conflicts are training negatives or ignored examples.
- If the shared 18.5 GB / 165k-division synthetic microscopy data can be located
  and its license/rules eligibility verified, pretrain center + motion heads
  there first. It is not yet a pinned Kaggle attachment, so it is a research
  dependency, not an assumption in any notebook.

## Holdout protocol

The public leaderboard is optimistic and movie variability is high. Select every
threshold using leave-one-embryo-out validation:

| Gate | Requirement before a leaderboard submission |
|---|---|
| Detection | held-out node recall improves over `rep300`; target >= 0.955 |
| Edges | held-out official edge Jaccard improves, not only training score |
| Robustness | no collapse on frozen frames or global-jump frames |
| Runtime | one representative test movie extrapolates safely below 12 h |
| Contract | every test movie present; all edges are `t -> t+1`; no artificial nodes |

## Build sequence

1. Export candidate centers and two independent short-track graphs for every
   train movie; compute agreement/conflict labels and motion statistics.
2. Train a compact pairwise 3D model on gold + high-confidence pseudo labels.
   Balance easy background away; emphasize candidates inside the physical gate.
3. Fit graph-calibration thresholds only on the training embryo, validate on the
   other embryo, then swap. Record worst-embryo results.
4. Make a submission notebook only after it has passed the five gates above.
   Keep the current high-score portfolio intact as the fallback.

## Explicit image artefacts to model

- Some frame pairs can be frozen duplicates: use a no-motion / copy-frame path
  instead of inventing a displacement.
- Global crop jumps exist: estimate global shift before local matching and use a
  residual motion gate.
- Long links are usually wrong: make termination/new-track cheaper than forcing
  a long match, then rely on the global optimiser only for short candidates.
