# Recall/edge research — condensed record (2026-08-23)

Live state, dead levers and calibration rules now live in `HANDOFF.md` (CURRENT
STATE). This file keeps only the durable *measurements* worth not re-deriving.

## Metric mechanics (verified against kaggle/scoring.py)
- `score = adj_edge_jaccard + 0.1*division_jaccard`; `adj = J*(1-0.1*node_ratio)`,
  `node_ratio=(N_pred-N_est)/N_est`, N_est ~= 32k/movie (~130x the ~214 annotated).
  An added detection needs only ~0.035% chance of being real to pay => over-detection
  is cheap, but flooding past ~2x N_est kills it (old DoG union = 0.661).
- **An edge counts if the SOURCE **or** the TARGET matched** (`out_valid OR in_valid`).
  So a wrong link costs FP **and** FN, while NO link costs only the FN already lost.
  => pruning ambiguous links can RAISE J. (Basis of the mutual-consistency lever.)
- Node matching: per-timepoint Hungarian at 7um, 1:1. True cell spacing 13-26um, so
  redundant detections go unmatched (harmless).

## Measured quantities (real data)
- Node recall 0.978 -> edge ceiling recall^2 = 0.9565.
- Edge attribution (biohub-edge-attrib, real pipeline): TP 95.4%, det_miss 1.8%,
  **steal 2.0%**, terminate 0.8%. Steal distance to true target med **8.76um** =
  neighbouring cell, i.e. produced by the LOOSE second pass (MAX_LINK_UM 10).
- Implied FP budget 245 (LB) - 391 (CV) vs only 73 steals => most FPs are
  WRONG-INCOMING edges. Edge precision ~0.93 is the real gap, not recall.
- True per-frame displacement: med 1.82um, p99 7.45um. MAX_LINK 10->8 rejects only
  0.74% of true links (10->7: 1.23%).
- Midpoint interpolation for gap-fill: 99.8% within 7um of the true cell (median
  1.0um) => synthesis fill is safe. This is why fill1 (+0.002) works.
- linefit smoothing displaces nodes med 0.65um, only 0.02% beyond the 7um gate.
- GT division geometry: parent-child med 5.5um, sister-sister 11.0um, divergence
  med 1.70um (the shipped 2.25um gate is strict but LB-optimal).

## Sim-fidelity lessons (why local sims misled)
- GT-only / perfect-detection sims OVERSTATE add-detection and division levers:
  they cannot see matched-FP edges, node_ratio, or broken-track-start forks.
- A sim that omits a pipeline stage misleads: the short_filter sim predicted +0.015
  by ignoring gap-fill; the real answer was +0.0005.
- Synthetic clutter must match real geometry: random 8um blobs are far more
  adversarial than real neighbours at 13-26um.

## FP-structure theory (2026-08-23) — this now guides every linker lever

The linker is strictly 1:1, so each matched node has <=1 in- and <=1 out-edge. A
missed GT edge (u,v) therefore produces roughly TWO false positives: a wrong
out-edge from pu, and a wrong in-edge into pv. Check: mislinks = FN - terminates =
163-27 = 136 -> predicted FP ~= 272, vs implied FP 245 (LB) / 391 (CV). Model holds.

Pruning payoff, per the scorer:
- prune an edge with BOTH endpoints unmatched -> FREE (the vast majority of ~125k edges)
- prune a WRONG edge -> -1 FP  => J UP
- prune a CORRECT edge -> -1 TP, +1 FN => J DOWN

Break-even: with J = tp/(tp+fp+fn), pruning helps iff the pruned set is
**> 1/(1+J) = 52.8% wrong**. So the entire game is DISCRIMINATOR QUALITY.
If a discriminator reached 70% precision -> edge J ~0.929; at 90% -> ~0.950.

Better still: FIXING a mislink beats pruning it (tp+1, fp-1, fn-1). Motion is
partly COLLECTIVE — predicting a cell's velocity from the mean of its 4 nearest
moving neighbours gives median error 1.32um vs 1.72um for a zero-motion prior
(77%), so a local-flow prior can re-link steals correctly rather than just drop them.

Levers under test from this theory: mutual-consistency pruning (forward vs backward
Hungarian disagreement), ambiguity-margin pruning (best vs runner-up cost), and the
collective-flow-prior linker.

REJECTED on rules/EV: emitting a speculative SECOND successor per node to exploit
the scorer's out-degree-2 cap. That is duplicate-track/fake-fork gaming (explicitly
off-limits) and it would turn every annotated cell into a division FP, destroying
the 0.026 division term.
