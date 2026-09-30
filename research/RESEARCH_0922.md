# RESEARCH_0922 · decision memo (biohub, 2026-09-22). Nothing has been submitted.
Bottom line: use at most 2 of today's 5 slots, stk3 (ready) and t60h (one line, build and review first). Finals stay hsg200 + lcefr unless one of them reads 0.952.

## New today (zero slots): our hard-coded TIGHT 5.5 is the live question
- hsz0 and hfusion wrote byte-identical visible submission.csv (sha a69c7822) but scored 0.946 vs 0.947.
- Box, train geff (read-only): 6bba_05db0fb1 has 3 GT divisions; 6bba_05b6850b and both 44b6 placeholders have 0. hfusion's validator ranks stems by (has division, name), 4 per prefix, and skips TEST_DIR stems. On the hidden rerun nothing is skipped, so 05db0fb1 replaces 6bba_09961292 in its validation set.
- Recomputed from data/out_hfusion/validator_results.csv: tight55's margin is +0.00206 on the visible 8 and +0.00143 on the 7 shared movies. It stays selected (margin rule 0.001) only if 05db0fb1 costs tight55 less than about 0.0004 adjEJ.
- Box memorized-graph pairs (rev_t55 vs lcflow_base, _deep0922/memo_t55_pairs.txt): 05db0fb1 d55 = -0.0042. Margin drops to about +0.0001, so hfusion's hidden run most likely wrote TIGHT 6.0. That explains 0.947 vs 0.946, and every arm since 09-17 (all 0.951s) hard-codes 5.5.
- Against it: critic LOEO on unseen 44b6 embryos (6bba-trained detector, pre-refinement graphs) favours 5.5 on 2 of 3 shards (+0.0007, -0.0004, +0.0017). Over 40 memorized movies 5.5 averages -0.0014 (13 up, 16 down). The harness also disagreed in sign with the real validator on 07e24132. So it is a one-slot hypothesis, not a fact.

## 1. Today's slots (the user launches and submits)
1. stk3: already run, GATE_PASS, sha 26b581ad0d64d15e (`kaggle competitions submit -k eeshsaxena/biohub-v-stk3 -v 1`). Expect 0.951; P(0.952) about 10-20%. Worth a slot only because it costs nothing and a 0.952 would change Final A.
2. t60h: v_hsg200 with only cell 0 `BIOHUB_MOTION_RELINK_TIGHT_UM` "5.5" -> "6.0". Build via BUILD_BASE=v_hsg200 into a new folder. Add a gate entry: an ARM_T60H line echoing the live value, plus >= 4 SV_ARM_HSG200 lines. Adversarial review: the diff is exactly one line. One ~23 min GPU run, then submit on GATE_PASS. Expect 0.951-0.952, downside 0.950. Every reading teaches something: 0.952 means the gate was costing a tick; 0.950 means 5.5 holds on unseen embryos and the hard-code stays.
3-5. Leave unused. stkve is a 0.31%-edge replicate of stk3. lcvel0 and lcbon22 push dials that already tied. stkvb is lcvel2 + lcbonus2, and the board could not resolve either alone. hvalon would reproduce t60h's likely hidden choice at +65 GPU-min.
Not safe today: rawlink (new ~90-line linker code), w3det (13 predictor patches, +13% runtime), and the learned offset head (weights private, capture run needed).

## 2. Meta-gate verdict on stk3 / stkve (outputs pulled, both GATE_PASS)
- No output statistic survives an honest test. Nested LOO MAE is 0.00226 against 0.00235 for predicting the mean; the best feature has permutation p=0.146. Fragmentation tracks the gain family (rho -0.90) but mispredicts all three linker arms (0.9486 / 0.9522 / 0.9548 for three true 0.951s).
- stk3 is mostly lcefr again: 0.56% of matched edges from lcefr, 2.75% from hsg200. stkve is 0.31% from stk3. Read both as 0.951.
- Visible outputs cannot gate anything: hsz0 and hfusion match byte for byte yet scored differently.

## 3. Final picks (select manually; 4 members can change it, so tell all of them not to)
- Now: A = hsg200 (0.951). It is the centre of the gain plateau (quadratic peak at gain 1.8-2.0) and has the fewest changes.
- B = lcefr (0.951, ref 56403633). It is the most divergent 0.951 output: 2.33% of matched edges, nearly disjoint from lcvel2/lcbonus2. The expected hedge is small, +0.0003 to +0.0006 private.
- stk3 >= 0.952 -> A = stk3, B = hsg200. stk3 <= 0.950 -> B = lcvel2 instead of lcefr.
- t60h >= 0.952 -> A = t60h, B = lcefr (best hedge on the 5.5 gate). Both at 0.952 -> A = t60h, B = stk3.
- Never pick a no-refinement arm, hsadapt or hsg250. The board truncates to 3 decimals, so 0.951 means [0.951, 0.952).

## 4. Plan to 09-29 (~30 slots left; expect to use under 15)
- 09-22: stk3 + t60h as above. Public kernel publishing closes 23:59Z tonight.
  The crowd "0.951" kernels are titles, not scores: haideptry's team best is 0.947 and his "0.948" kernels list 0.944/0.945; takaito's team best is 0.946 and gshift is unscored. That lowers the silver-line risk, but the intel sweep has the final word.
- 09-23: if t60h reads 0.952, stack 6.0 onto lcefr (t60e) and try one bracket at 6.5, then stop. Otherwise close the gate axis.
  Either way, build rawlink as a single change on the best body. It ports Joseph's V1057 (raw ILP edges with prob >= 0.30 override conflicting final edges, divisions protected, in <= 1 / out <= 2 asserts). Review it and submit 1.
- 09-24: gshift (takaito: per-frame median MNN drift correction in motion relink) only after a box LOEO screen (CPU, nice 19) and only if the intel sweep finds a real score for it.
  w3det only if the sweep ties Joseph's 0.949 to the public W3 map. It needs count==1 anchor asserts and a compile() check.
- 09-25..27: at most 2 structural arms per day, each a single change with a gate entry and review. Drop hdres: all training data is in-sample for both detectors, it needs a 1.75 h capture run, and the expected result is a tie.
- 09-28: code freeze. 09-29: select finals by 20:00 UTC, confirm them in the UI, and message all 4 members.
- Standing rules: a tie measures nothing. No replicates (the pipeline is deterministic). Nothing from the banned list.
