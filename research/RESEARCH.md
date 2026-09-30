# RESEARCH.md — Biohub Cell Tracking (project-canonical, MEASURED)

2026-08-30. Merges the external research corpus (`Downloads/RESEARCH.md`, 60+
web queries — accurate on facts) with OUR measured results (accurate on levers).
Where the external doc and our measurements disagree, **our measurements win**
(they are on the real pipeline + verified scorer; the external estimates are
priors). Two external claims are simply WRONG and corrected below.

---

## 1. THE METRIC (external + our scoring.py, verified == official 60/60 + 30/30)
`score = adjusted_edge_jaccard + 0.1 * division_jaccard`  (additive, max 1.1)
`adj = max(0, edge_J * (1 - 0.1 * (N_pred - N_est)/N_est))`
- Only edges with `t_target - t_source == 1` count; gap edges are DROPPED (not
  penalised) — so global gap-closing that makes long edges is a NO-OP unless you
  SYNTHESISE the intermediate node (our `fill1` does; LapTrack does not).
- Node match = per-timepoint Hungarian at 7um. Edges between UNMATCHED nodes are
  FREE (invisible). A division FP counts only if the fork's parent matched a real
  GT node. Under-prediction (N_pred < N_est) is a mild BONUS; over-prediction a
  mild penalty (coeff 0.1). GT is ~0.737% sparse.

## 2. OUR MEASURED SCORE DECOMPOSITION (LB isolation, not theory)
| submission | LB | meaning |
|---|---|---|
| fill1 (gap-fill + shipped div) | 0.919 | (superseded by sim4) |
| **sim4** (+ max_link8 + appearance sim_w4) | **0.921** | BEST |
| fillnodiv (divisions OFF) | 0.893 | isolates the EDGE term |
=> **edge term ~0.893, division contribution +0.026 (div_J ~0.26).** Node recall
0.978 => recall^2 edge ceiling ~0.9565, so ~0.064 is lost AFTER detection = a
GRAPH/LINKING (edge-precision) loss. Edge-loss attribution on the real pipeline:
TP 95.4%, det_miss 1.8%, **steal 2.0%** (link to a NEIGHBOUR ~8.76um away),
terminate 0.8%. **The gap is edge PRECISION (steals), not recall, not the detector.**

## 3. *** CORRECTIONS TO THE EXTERNAL RESEARCH ***
- **"div_J = 0.13, Hungarian forfeits 0.012-0.017 from divisions"** -> WRONG. Our
  measured div_J is **0.26** (already above the reported public frontier ~0.2), and
  loosening the division gate HURTS on LB (0.903). Divisions are near-optimal and
  DEAD as a lever. LapTrack's native-division advantage is therefore ~zero for us.
- **"LapTrack +0.007-0.014 -> 0.930-0.938, P(>0.93)~50%"** -> WRONG. Tested locally
  (`kaggle/exp_laptrack_ab.py`, 24 movies, verified scorer): raw LapTrack beats bare
  two-pass Hungarian by only +0.008, and in the realistic FP+jitter regime it LOSES
  (edge-J 0.9132 vs ours 0.9265) with WORSE precision (0.96 vs 0.99). Its global LAP
  links more permissively (more recall, less precision) — the wrong axis. The `+synth`
  gain is the midpoint gap-fill our sim4 ALREADY ships. VERDICT: negative/marginal.
- The external probability tables inherit both errors; treat them as unfounded.

## 4. ACCURATE EXTERNAL FACTS (keep these)
- **Competitor LB:** Ayati 0.962, Cooper/maxnau 0.955-0.956, TWEAK 0.952, Yunus
  0.938; us 0.921. The 0.94+ pack has 200+ entries on fundamentally different
  (Ultrack-class) architectures.
- **TWEAK (LB#3) publicly described** a "universal plugin" giving +0.03-0.05 on ANY
  public model, UNTUNED = a GRAPH/LINKING win on unchanged detections. Independently
  confirms our edge-precision attribution; a retrained detector is NOT the path.
- **Ultrack = the ORGANIZERS' method** (Royer Lab, Nature Methods 2025): multi-
  hypothesis segmentation + global ILP (native 1->2) + frame registration; "2x
  fewer errors than TrackMate". Our stack IS the TrackMate-class baseline
  (Tobi-joshua's open pipeline is identical). The gap is STRUCTURAL.
- **External data is host-confirmed allowed** (forum 734330): Zebrahub imaging +
  *_tracks.csv, no test overlap. The one root-cause fix for the 2-embryo overfit.
- Test set = 150 samples, SAME embryo types as train (no hidden types), micro-averaged.

## 5. LEVER LEDGER (our measurements; * = external prior only, untested by us)
POSITIVE (shipped): aggressive gap-fill midpoint synthesis (+0.002 -> the win that
made 0.919); max_link8 + appearance sim_w4 (-> 0.921).
NEGATIVE / DEAD (do not retry): LapTrack (sec 3); learned edge/prune models
(2-embryo overfit, LB dose-response inverse to CV); flow/flowprior (CV anti-
correlates with LB); abstention/prune (LB-dead); t+2 accel, joint/global-flow
(decompose into per-frame Hungarians; both-embryo-neutral); divisions (0.26 near-
optimal; relax hurts); DeepCenter veto/mean (negative); detection thr/NMS/gap-cap/
union (saturated at thr 0.15); own detector training (~680 GPU-h, infeasible free
tier); 2-opt swap repair (steals are one-sided, not swaps); Kunal-exact (0.917).
UNTESTED (low prior): *global motion compensation (needs images wired to linker;
steals are neighbour-mislinks not global drift); *LapTrack (now tested = negative).

## 6. WHY WE'RE STUCK AT 0.921 (the honest structural answer)
Local link decisions are at a GEOMETRIC CEILING: on 1-positive candidate groups the
distance cost already top-1s ~93%; a learned ranker (OOF AUC 0.98) improved this by
+0.0002 = noise, and PRUNING with it anti-correlated on LB (2-embryo overfit). The
theory: min-cost-flow with frame-pair-LOCAL costs DECOMPOSES into the per-frame
Hungarians we already solve, so "global optimization" (LapTrack included) gives no
free lunch on the frame-to-frame decision. Beating this needs TRAJECTORY-level costs
or a LEARNED IMAGE edge model with embryo diversity — i.e. external data + a large
train we cannot run on the free tier.

## 7. THE 0.95 PATH (out of reach with accessible own-work)
= an Ultrack-class pipeline: multi-hypothesis detection + global ILP with native
divisions + learned image-edge costs trained on MANY embryos (Zebrahub). Honest
ceiling of the accessible Zebrahub swing: ~0.925-0.93 (edge model touches only ~2%
steal edges), NOT the 0.95 prize. Deadline 2026-09-29.

## 8. FILES
Measured evidence: `kaggle/exp_laptrack_ab.py` (LapTrack A/B), `exp_linker_ceiling.py`
(edge_J~recall^2), `exp_*` (scoring/recall/division/edge-decomp), `scoring.py`
(verified metric). Submission builder: `scratch_kernels/build_recall_submission.py`.
Full history: `HANDOFF.md` (single source of truth), `RECALL_RESEARCH.md`, `INTEL.md`.
External corpus (facts, not lever estimates): `Downloads/biohub_complete_package.zip`.
