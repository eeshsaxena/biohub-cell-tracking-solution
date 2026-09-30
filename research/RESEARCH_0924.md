# 2026-09-24 research: the teams above us published their machinery

## Where we stand
Rank **83 of 3868**, score **0.954**. Top is 0.975. Silver already; gold is about rank 17,
which needs roughly 0.966, so 12 ticks.
Yesterday's last arm, `t65s3`, came back 0.954 (tie), closing the relink gate at 6.0/6.5.

## The find
I cross-referenced every public notebook author against the top 150 of the leaderboard.
Two teams above us have published their entire pipeline:

| author | rank | LB | what is public |
|--------|-----:|---:|----------------|
| **thtennant** | **32** | **0.959** | eleven `biohub-frontier947-*` notebooks: a full ablation ladder (fast, det096, tight60, flow2, readmit, gapfill, divprec) |
| **anvithpothula** | **57** | **0.956** | `biohub-x138`, which credits thtennant's agents by name, so it is a port of the above |

Everything else public sits at or below the 0.947 plateau (kunaldesale 0.942, amanatar 0.948,
flexonafft 0.947, pilkwang 0.949). The rank-21 notebook is a portfolio page for their old 0.941 line.

## Three mechanisms they have that we never ran
All of them are node-recall or motion, which is orthogonal to the localization work that got us
from 0.946 to 0.954.

1. **Neighbourhood-flow motion relink.** A tight seed pass builds a displacement field; every cell
   is then re-assigned against the median displacement of its 12 nearest confident neighbours
   instead of its own last step. Crucially it also **widens admission**: a target inside the gate of
   the predicted position is admitted even when it is outside the raw gate. That is what gets past
   the ceiling we measured, where only 11.7% of cells have more than one candidate in the gate and
   every pure re-ranking dial we tried was inert.
2. **Sub-threshold readmit.** Detections the solver discarded come back if they sit within 4 um of
   an open track end.
3. **Low-detection gap filler.** Gaps are filled with real detector peaks from a 0.3-threshold dump,
   never with invented nodes.

What we have that they do not: the sub-voxel refinement (+0.005 on our body), lcefr, bonus 1.6,
tight 6.0. Their own coordinate refinement is a learned head that needs a private dataset we cannot
mount, so our sub-voxel block takes exactly that slot.

## The merge is built, verified and running
Our kernel and theirs are the same 12-cell notebook, so it is a splice rather than a rewrite.
Verified by simulating the whole patch chain against the real support-pack source: all 13 of their
patches apply with anchor count exactly 1, and all four of our sub-voxel anchors still match exactly
once afterwards. The gate gained a `forbid` list, because their recall stack degrades silently
(a missing dump prints "gap filler idle" and the filler just does nothing).

First arm `xsv` ran clean in 15 minutes and every mechanism fired live: 770 readmitted nodes,
134 gap-filled nodes, flow active on all 198 frames of every movie. Nodes +1.0%, edges +1.1%.

## The bigger pot: divisions
Measured publicly on the real leaderboard by rogerrogerroger3r: turning every division off costs
**0.020**, so this lineage's division Jaccard is about **0.20** and roughly **0.08 of the score is
still unclaimed there**. That is larger than every localization and linker gain we have ever made.

I counted our own division funnel from the 0.954 run:

| gate | rejections |
|------|-----------:|
| divergence (`SAFE_DIV_DIVERGE_UM` 2.25) | **4105** |
| DeepCenter veto (0.25) | **445** of 627 survivors |
| mutual nearest neighbour | 396 |
| sister symmetry (0.6) | 91 |
| **divisions actually written** | **79** |

The frame and global caps are not binding at all. So divergence and the DeepCenter veto are the two
gates worth a slot. Our old `gdiv` arm moved five division knobs at once and lost two ticks, which
says nothing about any single one, so the axis is reopened for single-knob arms.

**Refuted before it cost a slot:** the same author proves the solver can only fork when the second
daughter's probability exceeds `ILP_DIVISION_WEIGHT`, and this lineage ships 1.2, so the solver
never forks. Tempting conclusion: drop it below 1. But the motion relink replaces the edge list with
a one-to-one matching and single-child repair then keeps one child per parent, so any fork is
destroyed twice before the division post-process runs. That arm would have changed nothing.

## Arms built and gated
`xsv` (submitted), `xsvf` (+lcefr), `xbase` (control), `xsvb` (bonus 1.6), `xsvt` (tight 6.0),
`xsv96` (det 0.96), `xsvd` / `xsvdv` / `xsvdc` (the three division gates).
