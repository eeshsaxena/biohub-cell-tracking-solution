# Annotation-prior node pruning: report (2026-09-17)

## Verdict
**HYPOTHESIS REFUTED.** No information available at test time (crop position, border distance, z depth, space-time cone,
track length or persistence, t=0/T-1 touching, edge confidence, or a 22-feature learned mix) predicts which cells are annotated
strongly enough to prune on. VERIFIED RULES = none, so **no kernel variants were built** (step 1 skipped by design) and
**no submission is recommended**. Node-count pruning is closed as a route from 0.947 to 0.970.

## Hypothesis
adjEJ = J*(1 - 0.1*(N_pred-N_est)/N_est) has no cap, so removing unannotated predicted nodes raises the multiplier toward 1.10
while J is kept. That only works if the annotated subset can be predicted from test-time information.

## Scorer facts (official repo on box, HEAD 075fc5f == upstream; the local vendored copy is OLDER, do not use it)
- N_pred = graph.num_nodes(), i.e. every node row (src/tracking_cellmot/metrics.py:330). ratio and adj at metrics.py:439-451, no cap.
- N_est = geff extra `estimated_number_of_nodes` (scripts/evaluate.py:52-57), per movie, range 3,783-78,644.
- Matching: per frame, one-to-one max-cardinality then max-weight (weight 1/(1+d)), d <= 7.0 um, scale from zarr (1.625, 0.40625, 0.40625).
- Edges: dedupe, keep only dt==1 (metrics.py:74-87), collapse merges, cap out-degree at 2 by CSV row order (metrics.py:140-153).
  An edge between two unmatched nodes is FREE. An edge with one matched endpoint is FP only if that GT node has a GT edge on that side.
- Division FP now = considered | evaluable | cross-component | malformed forks (division_metrics.py:358-361, 449+). Malformed needs
  no matching, so the note "a division FP needs a matched parent" is outdated (drift 2 FP in 199 movies).
- Aggregation (metrics.py:471-503): adjEJ weighted by w=TP+FP+FN per movie; divJ pooled; score = adjEJ + 0.1*divJ.
  Effective in-sample multiplier is 1.006 (44b6 1.023, 6bba 1.003), not the pooled-ratio 1.025.
- Pruning hazards: a movie with nodes but 0 edges scores adj=0 at full weight; dangling edge ids raise KeyError; re-index ids.
- ~/biohub/annot_prior/score_lib.py reproduces the official scorer exactly (max |diff| 0.0 on 1,350 + 83 spot scorings).

## GT geometry
- All 199 movies (100,64,256,256), about 102x104x104 um. Every GT edge has dt==1.
- 44b6: 71/71 crops have a GT node at (t50, z32, y128, x128). That centred track is only 31.5% of pooled GT nodes (median 47%/movie).
- 6bba: only 3/128 exact, centred track 6.9% of GT nodes, other tracks flat in radius. Test embryos could follow either convention.
- Density: 44b6 median 4 tracks / 214 nodes (~0.7% of N_est); 6bba median 29 tracks / 826 nodes (~10%). Forum: ~22 tracks/movie,
  median labelled track 35 frames. The "one tracked cell per movie" premise (44b6_0113de3b) is an outlier, not typical.
- Within-movie AUC annotated vs predicted (44b6/6bba): rnorm 0.31/0.45, border 0.70/0.57, track length 0.72/0.67, z 0.52/0.49.
  Track-length AUC falls to 0.55 on honest LOEO (mostly detector-trained-on-GT artifact).
- Host: evaluation on "a random sparse subset" of cells. Likely source is random mosaic sparse labelling (Ultrack paper Fig. 4),
  invisible in the dense channel. No host statement on crop sampling or N_est estimation.

## Oracle bounds (production graphs = kernel output, exact official scoring, uses GT, reference only)
| oracle | 44b6 | 6bba | pooled 199 | LOEO44 |
|---|---|---|---|---|
| base score | 0.9194 | 0.9174 | 0.9178 | 0.6708 |
| keep matched nodes | +0.1286 | +0.1309 | +0.1305 | +0.1174 |
| keep components touching GT (pure multiplier, J unchanged) | +0.0658 | +0.0732 | +0.0720 | +0.0531 |
| keep tracklets touching GT | +0.0766 | +0.0813 | +0.0806 | +0.0562 |

The HANDOFF "+0.024 oracle cap" (HANDOFF.md:2022) is WRONG: it is the drop-20% dose of a capped sweep
(prune_det0.980.json, reproduced as +0.0267 official). The real ceiling is +0.07 (track) to +0.13 (node). HANDOFF.md:31 already
has the correction; line 2022 still carries the old claim.
Break-even: a prune set must be at least 11-15x depleted in annotated cells vs a random predicted node (LR <= ~0.07-0.10).
Best observed: 0.17-0.21 in-sample (2.5-5x depletion), 0.55 on honest LOEO (<2x).

## Rule table (exact official score delta; fit on one embryo, test on the other; LOEO44 = 6bba-only detector on 44b6)
| rule (unit) | fit 44b6 -> test 6bba | fit 6bba -> test 44b6 | LOEO44 | min both |
|---|---|---|---|---|
| c_maxb/t_maxb: drop tracks entirely within 1 um of a face | +0.0004 | +0.0006 / +0.0008 | +0.0000 | +0.0004 |
| c_maxbxy: same, xy faces only | +0.0004 | +0.0002 | +0.0000 | +0.0002 |
| cq_maxb: drop f of nodes, most border-hugging comps | +0.0003 (f=.01) | +0.0007 | -0.0004 | +0.0003 |
| n_bxy: drop nodes <0.25 um from xy face | +0.0005 | +0.0001 | +0.0005 | +0.0001 |
| n_bxyz / n_bz (forced 0.25 um) | -0.0014 / -0.0018 | -0.0046 | +0.0004 / 0 | -0.0046 |
| n_rxy / n_rxyz / ellipsoids (radius from centre) | noop (R=70: -0.0003) | -0.0011 | -0.0006 | -0.0011 |
| z windows (n_zlo/n_zhi/n_zwin) | -0.0128 forced | -0.0074 forced | -0.0013 | -0.0128 |
| space-time cones at t=50 (node / comp) | 0 | 0 | R70: -0.011 | 0 |
| c_minb: drop tracks that ever touch a face | -0.2067 forced | -0.1661 | -0.0131 | -0.2067 |
| quantile radius/border prunes at f=0.10 | -0.020..-0.049 | -0.020..-0.031 | -0.007..-0.016 | < 0 |
| min track span >= L (production already L>=6) | -0.00001 (L=7) | noop | L=7: -0.0080 | -0.00001 |
| min track nodes >= L | -0.0009 | noop | L=8: -0.0129 | -0.0009 |
| boundary-touching tracks only / span OR boundary | noop / -0.0020 | noop | -0.36 / -0.019 | -0.0020 |
| mean edge prob >= p | noop | -0.00015 | -0.0006 | -0.00015 |
| top-q by span x edge prob (q=0.98) | +0.00065 | +0.0018 | **-0.0064** [-0.0094,-0.0036] | +0.00065 |
| top-K tracks per movie (any score) | -0.0009..-0.0040 | noop | K2000: -0.0010 | < 0 |
| spur prune (short leaf branch after fork) | +0.0001 (L<4) | -0.0013 (L<6) | +0.0004 [-0.0003,+0.0016] | -0.0013 |
| trim track ends k=1 | noop | noop | -0.0252 | 0 |
| 22-feature logistic, drop lowest q | noop (q=.01 -0.001) | +0.0002 | -0.0043 [-0.0068,-0.0021] | 0 |

Dose-response: every rule that removes more than ~2% of nodes is negative on all three sets; at 50% removed, -0.12 to -0.44.

## Verdicts per lens
- Scorer: formula confirmed uncapped; headroom real (+0.07..+0.13) but proportional to 0.1*J*r.
- GT geometry: one exact positional fact (44b6 centring at t=50) that covers 31% of annotated mass and fails on 6bba. Not a lever.
- Dataset construction: host says random sparse subset; no documented selection bias to exploit.
- Geometric experiments (32 rules): best cross-embryo min +0.0004, LOEO +0.0000. CLOSED.
- Track-structure experiments (188 variants): best cross-embryo min +0.00065, negative on honest LOEO. CLOSED.

## Legitimacy
- Prior-based node pruning below N_est to collect the multiplier = GREY/metric-gaming. Not banned by rule text, but hosts invite
  gaming reports (/discussion/723655) and already patched and rescored one exploit; rules 3.8.d / 3.16 apply. A later cap would
  keep the J loss and delete the gain. Moot now, since it does not work.
- Removing genuinely false structures (spurs, 1-um border slivers, mislinks) = LEGITIMATE model quality, but measured at 1e-4 here.
- Deliberate LB formula probes (junk nodes) = the user's call only.

## Built variants and expected LB deltas
None built (no rule passed). Had the best candidates been built, the honest expectation is:
c_maxb d=1: +0.0000 (LOEO CI [-0.0002,+0.0002]), invisible on a 3-decimal board. topq_span_x_ep q0.98: about -0.006
(LOEO CI excludes 0). spur<6: +0.0004 [-0.0003,+0.0016]. All below the calibration floor where +0.002..+0.018 local gains failed.

## Recommendation and what it implies about the 0.97 teams
1. Spend no slots on node or track pruning by any annotation prior. Fix HANDOFF.md:2022.
2. Reaching 0.970 by pruning would need removing ~1/3 of predicted nodes at 11-15x annotated depletion; nothing observable
   gets past 5x in-sample or 2x on an unseen embryo. So the leaders are very unlikely to be farming the multiplier with a prior.
   Their gain most plausibly comes from J (detection and linking precision) and divisions. Antonoof's 44.7% prune with LB flat
   (/discussion/739686) matches this: it was break-even at best.
3. Where real headroom sits (legitimate): the node oracle lifts J 0.9035 -> 0.9469 purely by removing FP edges that touch
   annotated tracks (mislinks and spurious branches), and 137/159 division FPs are spurious forks off annotated tracks
   (divJ 0.087 -> 0.156, about +0.007). Those are linking and division-precision problems, not annotation-prior problems.
   This does not settle whether the leaders used GPU training.

Artifacts: ~/biohub/annot_prior/{score_lib.py, oracle_*.json, geom/, exp_geometric/, exp_track-structure/}; local copies in the
session scratchpad. Nothing left running on the box (nice 19, <= 6 workers, no GPU).
