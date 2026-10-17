# Biohub Cell Tracking During Development, bronze solution (287 / 3947)

My solution for the Kaggle competition
[Biohub - Cell Tracking During Development](https://www.kaggle.com/competitions/biohub-cell-tracking-during-development),
3D nuclei tracking in developing zebrafish. Final: **rank 287 of 3947, bronze medal** (after Kaggle's final leaderboard cleanup; 303 of 4017 at close).

The full writeup is in [SOLUTION_WRITEUP.md](SOLUTION_WRITEUP.md) (also posted on Kaggle).

## What this is

Two submissions were selected, one from each of two pipelines that share a detector and tracker but place
coordinates differently, so they fail independently on the embryo-disjoint hidden test set:

- **Learned-head body**, public 0.955: learned coordinate head for y/x, sub-voxel refinement for z.
- **Sub-voxel body**, public 0.954: sub-voxel soft-argmax refinement for both y/x and z.

The three ideas that actually moved the score:

1. **Sub-voxel soft-argmax localization.** The base pipeline quantizes detections to a voxel grid. Refining
   each detection off the grid using the detector logits pulls borderline edges inside the 7 um match gate.
   This was the single biggest lever, about +0.006 to +0.007.
2. **Feeding the refined z back into the edge model**, not just into the output. Worth about +2 ticks.
3. **Tracker tuning**: a learned-edge bonus in the motion relinker, and a raw-ILP override rule ("rawlink").

Just as important, a production-exact **replay harness** and its calibration against the leaderboard (board
delta was about replay delta minus 0.8 ticks) kept me from trusting offline numbers that would not transfer.
Most ideas I tried failed. The writeup covers the negative results in detail.

## Repository layout

```
notebooks/          the two selected Kaggle notebooks (source, no weights)
  ourvzlb25r70_0955_learned-head.ipynb
  t65b25r70_0954_sub-voxel.ipynb
src/
  ops/              orchestration + submission tooling (push/gate/submit, leaderboard read, scoring)
  kernel_builders/  scripts that build each experiment notebook from a base by editing one cell
research/           raw working notes (HANDOFF, RESEARCH, FINAL_PICKS, etc.), kept as-is
images/             competition banner and thumbnails
SOLUTION_WRITEUP.md the writeup
```

## What is NOT in this repo, and why

- **Model weights** (detector, edge model, and the V1284 coordinate head). The V1284 head and the base
  detector are other people's public artifacts, not mine to redistribute.
- **Competition data** and the ~1GB of derived caches. Get the data from the competition page.
- **The bundled public pipeline code** (`tracking_repo/`) that ships inside each Kaggle kernel's output.

To actually run a notebook, open it on Kaggle and mount the public datasets it references (see any
`*_kernel-metadata.json` in `notebooks/` for the exact `dataset_sources`).

## Credit

This is built on public work:

- Detector, tracker and support pack: **@pilkwang**
  (`biohub-temporal-unet3d-seed314159-v1`, `biohub-tracking-support-pack-50ep-v1`,
  `biohub-deepcenter-unet3d-center-prior-v1`).
- The "V1284" learned coordinate head: **@anvithpothula** (`biohub-v1284-head-s075`).
- The rawlink raw-ILP override idea: a public "V1057" discussion post by **@josephadamski91**.
- The organizers' scorer, ported to run offline.

## Note on the research notes

`research/` is raw working notes written during the competition, not polished documentation. They record what
was tried and what the leaderboard said, including plenty of dead ends. Notes about other teams' public
notebooks refer only to published, public work.

## Team

The Originals: Eesh Saxena, Arunendra Tripathi, Akanksha Gupta, Swapiy.
