# HANDOFF - biohub cell tracking

## 09-29 21:46Z: FINAL. ourvzlb30t625 (56679391) = **0.954** (below ourvzlb25r70 0.955). USER: "stop researching".
Picks unchanged: **A = ourvzlb25r70 (56657610, 0.955), B = t65b25r70 (56640601, 0.954)**. Board 21:46Z: rank 497,
0.955 block = ranks 420-528, bronze line 401 (inside the 0.956 block), silver 200, 4012 ranked. Private decides.
Post-mortem: the V1284-body replay's +0.64 (bonus 3.0 + tight 6.25) did not transfer, same over-read as the t6-body
calibration (board ~ replay - 0.8). Cross-body replay is invalid (V1284 head trained on train movies: t6 body reads
-10.5 ticks on replay vs -1 on the board). Box driver stopped; no jobs of ours left on the box.

## 09-29 14:52Z: **LAST SLOT SUBMITTED: ourvzlb30t625 = 56679391** (user-authorized: "submit the best acc to you")
0 submissions left today (5/5). Pick rule for tonight is in FINAL_PICKS.md (A = ourvzlb30t625 only if it displays
0.956+ or becomes the representative; else A = ourvzlb25r70; B = t65b25r70 either way).
Round 4 (48 movies, ticks vs ourvzlb25r70): **b30t625r65 +1.01 [+0.38,+1.61] (44b6 +1.37, 6bba +0.87, 30/11)**,
b30t625 +0.64, b30t600 +0.52 (6bba +0.10), b30t625r75 0.00 (6bba -0.27). r65 met the evidence part of the switch
rule (+0.37 >= +0.30, both +, div 0) but had NO Kaggle build: build + 33-min visible run -> submittable ~15:40Z, and
scoring latency today was 7.4-8.5 h (ourvzlb25r70 00:46Z -> ~09:15Z; t65b25r70ff > 7.4 h), so its score could land
after the 23:59Z pick deadline. Rawlink is also the replay's known over-read class. -> Submitted b30t625 at 14:52Z for
margin. LESSON: pre-build every arm on the replay's frontier axis (here rawlink), not only the likeliest winners.
The rawlink-down direction (0.70 -> 0.65) is the strongest unexploited replay signal on the V1284 body.

## 09-29 14:30Z: FULL 48 MOVIES (r06): ourvzlb30t625 CONFIRMED as the rule winner
pooled [90% CI] / 44b6 / 6bba / division part / wins-losses, ticks vs ourvzlb25r70:
| **b30t625** | **+0.64 [-0.01,+1.23]** P 0.95 | +1.32 | +0.38 | 0.00 | 27/13 |
| b40t625 | +0.57 | +1.32 | +0.35 | -0.12 | 29/16 |
| b30t675 | +0.56 | +0.58 | +0.48 | +0.12 | 20/20 |
| b35t625 | +0.53 | +1.39 | +0.27 | -0.12 | 33/11 |
| t625 / b30 | +0.32 / +0.27 | | | | |
| ffb30t625 (IMGFLOW, excluded) | +1.07 [+0.34,+1.83] | | | | |
Visible GATE_PASS so far: ourvzlb30t625, ourvzlffb30, ourvzlb35t625 (14:19Z). ourvzlb40t625 running; ourvzlb30t600
pushed 14:25Z (ETA ~14:58Z). Round 4 (b30t600, b30t625r65, b30t625r75) read at 14:50Z.

## 09-29 14:20Z: USER GO (conditional): "try till 9 pm then submit the best acc to you" (9 pm IST = 15:30Z)
-> I submit ONE arm at ~15:15-15:20Z (margin for ~7 h scoring before 23:59Z). Default = ourvzlb30t625.
ROUND 4 on the box (ARMS b30t625 b35t625 b40t625 b30t600 b30t625r65 b30t625r75; dropped the decided arms). Notebooks
scratchpad/wf34/r4 (cell 0 only; c5 replay runs cells 0..11 with only the predictor served from the donor, so tight
and rawlink are replayed). PRE-REGISTERED SWITCH RULE: a round-4 arm replaces ourvzlb30t625 only if it beats it by
>= +0.30 pooled (paired movies), is positive on both embryos, has a division part >= 0, AND has a visible GATE_PASS by
15:10Z. Kaggle pre-build of ourvzlb30t600 requested (agent). ourvzlb35t625 / ourvzlb40t625 visible runs in flight.

## 09-29 14:08Z: RULE VERDICT (40/48 paired) = **ourvzlb30t625** -> presented to the user; SUBMIT ONLY ON HIS GO
r05c (40 movies, ticks vs ourvzlb25r70; pooled [90% CI] / 44b6 / 6bba / division part / wins-losses):
| **b30t625** | **+0.73 [+0.03,+1.35]** P 0.96 | +1.37 | +0.48 | div 0.00 | 25/8 | visible GATE_PASS |
| b40t625 | +0.66 | +1.45 | +0.42 | div -0.15 | 26/11 | visible run pushed 14:05Z |
| b35t625 | +0.59 | +1.45 | +0.32 | div -0.15 | 30/6 | visible run pushed 13:52Z |
| b30t675 | +0.55 | +0.64 | +0.45 | | 16/17 | |
| t625 / b30 / b40 / b35 | +0.38 / +0.31 / +0.29 / +0.22 | | | | | singles |
| ffb30t625 (IMGFLOW) | +1.32 | +2.93 | +0.67 | | 24/9 | excluded by the rule (IMGFLOW never transferred) |
Bonus line flat past 3.0 and bonus >= 3.5 starts losing divisions on 6bba; b30t625 = highest non-IMGFLOW, both
embryos +, beats best single part (t625 +0.38) by +0.35 >= 0.15, CI now excludes 0. Expected board after the
t6-body calibration (-0.8) ~ -0.1 tick: a coin flip for a representative flip, P(display 0.956) ~15%.
Submit command (user's go only, by 15:30Z): `python ops/run_today.py ops/plan_ourvzlb30t625.json --submit-only`.

## 09-29 14:00Z: ROUND 2+3 INTERIM (32/48 paired) + VISIBLE GATES
Visible GATE_PASS: ourvzlb30t625 (+92 nodes, edge diff 0.0080 vs base, change driven by tight 6.25), ourvzlffb30.
ourvzlb35t625 built + gate installed (agent) + visible run pushed ~13:52Z (--no-submit, task brr56oqyy); ourvzlb40t625
build requested. r05ci (32 movies, ticks vs ourvzlb25r70, pooled / 44b6 / 6bba / wins-losses):
b30 +0.22 | b35 +0.28 | b40 +0.36 | b30t625 +0.54 (+0.98/+0.27, 21/6) | b35t625 +0.55 (+1.06/+0.31, 25/4) |
b40t625 +0.63 (+1.06/+0.43, 21/9) | ffb30t625 (r05i, 31 mov) +0.96. Bonus line flattening; b30t625..b40t625 = noise apart.
CAVEAT (checked 14:00Z): the edge model (pilkwang support pack, method unet_transformer_alltrain_seed314159_v1,
train_datasets 199) was trained on ALL train movies -> the replay is 100% in-sample for learned-edge trust; no held-out
subset exists. Bonus + tight-down both shift trust toward the learned edges, so treat the replay deltas as upper bounds
(t6-body calibration board ~ replay - 0.8). Precedent in favour: on the t6 body, replay steps of +0.4..+0.6 on the bonus
line flipped the representative twice.

## 09-29 13:40Z: BOX BACK; ROUND 2 INTERIM (19/48 paired movies) + ROUND 3 (bonus line) QUEUED
r04 interim vs ourvzlb25r70 (ticks; 44b6 / 6bba; per-movie wins/losses):
| arm | pooled [90% CI] | 44b6 | 6bba | note |
| ffb30t625 | +1.38 [+0.61,+2.11] | +4.14 | +0.19 | IMGFLOW (never transferred on board); ff adds ~0 on 6bba |
| ffb30 | +0.93 | +3.33 | -0.10 | IMGFLOW, 6bba negative -> fails rule |
| **b30t625** | **+0.60 [-0.08,+1.27]** | +1.59 | +0.18 | best non-IMGFLOW, both +, combo beats best part b30 (+0.27) by +0.33 >= 0.15 |
| b30t675 | +0.55 | +0.65 | +0.51 | both + |
| b35 | +0.52 [-0.02,+1.11] | +0.91 | +0.35 | both +; bonus line still rising (b25 0, b30 +0.27, b35 +0.52) |
| v015 / v035 / lf070 | +0.01 / +0.08 / -0.04 | | all 6bba < 0 | DROPPED from the driver at 13:38Z |
Round 3 added to the running driver (ARMS file): b35t625, b40t625, b40 (notebooks scratchpad/wf34/r3, cell-0 bonus line
only, md5 f66c537d / e2decbb6 / e66fb0ab). Interim rule verdict: **ourvzlb30t625** (visible run RUNNING on Kaggle, gate
installed; auto gate-check task bgdqja9n8). Pre-build of ourvzlb35t625 (kernel + gate, NO push) running in case the
bonus line keeps rising. Still NO SUBMIT without the user's go; last safe submit 15:30Z.

## 09-29 13:15Z: USER AWAY ~40 MIN ("keep doing automatically") - LAST SLOT STILL REQUIRES HIS EXPLICIT GO
Session restarted 13:10Z; box round-2 driver survived (18/48 movies per arm at 13:14Z, ETA ~13:45Z; auto-score r04 at
13:46Z, task bzz9i7e2k). Pre-build agent resumed: ourvzlb30t625 + ourvzlffb30 visible runs pushed 13:04-13:05Z, gate
entries being installed. DO NOT SUBMIT without the user's go (his standing order: "don't use the last submission until
I tell you"; "keep doing automatically" = keep working). LAST SAFE SUBMIT 15:30Z.
DECISION RULE for the recommendation (pre-registered 13:15Z): among arms with a visible GATE_PASS (or buildable by
~14:40Z), pick the highest pooled r04 replay delta vs ourvzlb25r70 that is POSITIVE ON BOTH EMBRYOS; prefer non-IMGFLOW
arms (IMGFLOW never transferred on the board); a combo is preferred over its parts only if it beats the best single part
by >= +0.15 pooled. Current best single: ourvzlb30 (+0.27, both +). If nothing beats it, recommend ourvzlb30.
Submit command pattern: `python ops/run_today.py ops/plan_<tag>.json --submit-only`.
13:22Z: **BOX UNREACHABLE** - the laptop moved to another network (Wi-Fi 10.119.x, not the college 192.168.10.x; no
Tailscale on the laptop). Round 2 keeps running on the box but cannot be read until the laptop is back on the college
network (then: `cd ~/biohub/wf33/B && venv... analyze_B.py r04 b30 t625 ff b30t625 ffb30 b30t675 ffb30t625 b35 v015 v035
lf070`). The 13:46Z auto-score will fail harmlessly. FALLBACK per the pre-registered rule = round-1 winner
**ourvzlb30** (+0.27 [-0.03,+0.61], both embryos +, visible GATE_PASS): `python ops/run_today.py ops/plan_ourvzlb30.json
--submit-only` (only on the user's go, by 15:30Z). Combos ourvzlb30t625 / ourvzlffb30: gates installed, Kaggle visible
runs RUNNING at 13:18Z (no replay numbers without the box -> not preferred over ourvzlb30).

## 09-29 13:05Z: USER "RESEARCH MORE" (declined to pick the last-slot arm) -> ROUND 2 on the V1284-body replay
Box ~/biohub/wf33/B driver relaunched 13:00Z (pid in driver.pid; RECW 0, C5W 14; records reused), 8 arms x 48 movies:
b30t625, ffb30, b30t675, ffb30t625, b35, v015 (velocity 0.15), v035, lf070 (line-fit 0.7). Notebooks built locally
(scratchpad/wf34/r2, md5-pinned bases v_ourvzlb25r70 / v_ourvzlb25r70ff, cell 0 only). Auto-score r04 at 13:32Z.
Kaggle pre-builds (no submit) of the two likeliest combos in parallel: ourvzlb30t625, ourvzlffb30.
Already submit-ready (visible GATE_PASS): ourvzlb30, ourvzlt625, ourvzlt675, ourvzllf100 (DEAD), ourvzlsr, ourvzlb20,
ourvzlb25r70ff. LAST SAFE SUBMIT 15:30Z; the user must give the go.

## 09-29 11:35Z: V1284-BODY REPLAY COMPLETE (48 movies, 24/24; r03 in ~/biohub/wf33/B) -> LAST-SLOT RECOMMENDATION = ourvzlb30
vs ourvzlb25r70 (ticks, pooled [90% CI], 44b6 / 6bba, per-movie wins):
| arm | pooled | 44b6 | 6bba | P(>0) | wins |
| **b30** (bonus 3.0) | **+0.27 [-0.03, +0.61]** | +0.44 | +0.21 | 0.92 | 14/18 |
| t625 (tight 6.25) | +0.32 [-0.23, +0.87] | +0.88 [+0.08,+1.89] | +0.12 | 0.83 | 23/15 |
| t675 (tight 6.75) | +0.36 [-0.20, +0.98] | +0.14 | +0.38 (incl. +0.10 div) | 0.85 | 18/20 |
| ff (IMGFLOW) | +0.35 [-0.13, +0.84] | +1.41 | -0.05 | 0.88 | 11/5 |
| sr | +0.07 | | | | 5/42 |
| b20 | +0.08 | | | | |
| lf090 | -1.12 | | -1.64 | | | DEAD
| **lf100** (line-fit 1.0) | **-2.72 [-4.45, -0.94]** | -1.34 | -3.23 | 0.007 | | DEAD (the visible-4 +0.004 was noise)
Nothing clears the calibrated bar (replay >= +1.5 both embryos); all within ~±0.5 tick. b30 = the most BALANCED
(both embryos positive, tightest CI, P 0.92) AND the family with the best board-transfer record (bonus steps 1.6 ->
2.0 -> 2.5 each flipped the representative on the t6 body). ff down-weighted (IMGFLOW never transferred on the board:
t6stk3ff / t65b25r70ff ties, FLOWLINK -1). Honest: expected ~0 to +0.3 tick; P(display 0.956) ~15-20%; can't hurt the
finals (picks are chosen after scoring).
READY (visible GATE_PASS): ourvzlb30, ourvzlt625, ourvzlt675, ourvzlb25r70ff. Submit (ONLY on the user's go, by 15:30Z):
`python ops/run_today.py ops/plan_ourvzlb30.json --submit-only`. Box grid stopped (STOP file).

## 09-29 10:50Z: session restart recovered; V1284-BODY REPLAY IS LIVE (box ~/biohub/wf33/B, driver drive_B.py survived)
* Lens B agents died with the session but the box driver kept running. SELF-CHECK PASSED: the box record of
  ourvzlb25r70 on visible movie 6bba_05b6850b == the Kaggle visible run row-for-row. PREREG in wf33/B/PREREG.md.
* r02 partial score (10 paired movies, 5/5), vs ourvzlb25r70: ff +1.06 [+0.38,+1.70] (44b6 +2.05, 6bba +0.54, 5/0
  wins) - BUT IMGFLOW over-read by ~3 ticks on the t6 body (replay +2.85 -> board tie), so ff is likely ~0 on the board;
  rl0 (rawlink OFF) -11.2 (rawlink's in-sample over-read, board showed +1); t675 +0.54 (6bba-only); b30 +0.33;
  t625 +0.14 (44b6+/6bba-); sr +0.11; b20 -0.54. All within noise at n=10.
* Lens A (census) died; its partial files (scratchpad/wf33/A/lfscore.py) found a BODY-SPECIFIC line-fit effect on the
  4 visible movies: BIOHUB_OUTPUT_LINEFIT_WEIGHT 0.8 -> 1.0 = +0.0039 on the V1284 body but -0.0064 on the t6 body
  (line-fit was tuned on the SV body; V1284 y/x may be noisier). ADDED LIVE to the box grid: arms lf100 / lf090
  (cell-0 `os.environ["BIOHUB_OUTPUT_LINEFIT_WEIGHT"]` = "1.0" / "0.9"; built from v_ourvzlb25r70 md5-pinned,
  scratchpad/wf34). ARMS now: base_c5 ff lf100 lf090 sr t625 t675 b20 b30 (rl0 dropped); C5W 5 -> 8 (no user jobs).
  Driver backfills new arms on already-recorded movies. Auto re-score r03 at 11:30Z (task in background).
* Pre-build agent (ourvzlt625/t675/b30/sr/b20 Kaggle variants) resumed via SendMessage; its gate entries were not yet
  installed at restart; t625/t675 visible runs pushed 10:00Z.

## 09-29 10:15Z: FINAL +0.001 HUNT (workflow wo7snadk0, run wf_50a7e8c0-b22; box ~/biohub/wf33, scratchpad/wf33)
USER: "research more, even a 0.001 gain will help, you have ultracode". Timeline: candidate chosen by ~12:30Z -> build +
gate + visible run by ~14:30Z -> user go -> submit by ~15:30Z (must finish scoring before 23:59Z).
A = census of every kernel knob in v_ourvzlb25r70 vs the board record (never-tested / old-body-only knobs, top 5);
B = FIRST-EVER replay of the V1284 body: record ourvzlb25r70's detections on ~48 GT-rich movies (24/24) on the box,
then fast-replay a pre-registered cell-5 grid (tight 6.25/6.75, bonus 2.0/3.0, rescue armed, IMGFLOW on, rawlink off);
decider picks at most ONE candidate vs the default ourvzlb25r70ff (building) or HOLD.
10:25Z USER "increase throughput": box already saturated by lens B (GPU 100%, 3 record workers, no user jobs), so the
BUILD step was taken off the critical path instead: a pre-build agent is building + gating + visible-running every
grid candidate as a cell-0 env variant of v_ourvzlb25r70 (ourvzlt625, ourvzlt675, ourvzlb30, ourvzlsr (reuse
ourvzlb25r70sr if it exists), ourvzlb20), NO submit, max 2 Kaggle GPU sessions, target done ~12:15Z. Whichever the
decider picks at ~12:30Z is then submittable at once (user's go still required).
**FALLBACK READY: ourvzlb25r70ff** (IMGFLOW on the 0.955 arm): build_ourvzlb25r70ff.py -> v_ourvzlb25r70ff, gate
add_ourvzlb25r70ff_gate.py (backup gate.py.bak_ourvzlb25r70ff; 10 PASS / 27 FAIL self-test), visible GATE_PASS
(09:22-09:54Z); pre-repair output == ourvzlb25r70 exactly; flowfix changed 32/2/2/277, edges +97, nodes/divisions
unchanged; diversity 0.0023. Submit: `python ops/run_today.py ops/plan_ourvzlb25r70ff.json --submit-only`.
(ourvzlb25r70sr was NOT built - the pre-build agent builds its own ourvzlsr.)

## 09-29 09:15Z: **ourvzlb25r70 = 0.955 (FIRST 0.955)**; t65b25r70sr 0.954; mixyx50r70 0.953; t65b25r70ff running
* ourvzlb25r70 (56657610) = representative, display 0.955: rawlink 0.70 stacked on the V1284 body lifted it
  0.954 -> 0.955 (same step as t65b25 -> t65b25r70 on the t6 body). Board 09:13Z: rank 447, #74 of 102 in the 0.955 block
  (ranks 374-475); **bronze line 398 = 25th in the 0.955 block**; 0.956 block = ranks 228-373 (fully above bronze).
* mixyx50r70 (56659511) = **0.953**: the 50/50 SV+V1284 y/x blend scored BELOW both parents (0.954 / 0.955). Blend CLOSED.
* t65b25r70sr (56659169) = 0.954: tie on display; ordering vs t65b25r70 now unobservable (rep moved to ourvzlb25r70).
* **USER 09:15Z: DO NOT USE THE LAST 09-29 SLOT UNTIL HE SAYS SO.** He wants >= 0.957 "to be safe" (honest: +2 ticks with
  one slot left is very unlikely; 0.956 = the realistic stretch target).
* PICKS NOW: **A = ourvzlb25r70 (56657610, 0.955)**, **B = t65b25r70 (56640601, 0.954)** = the top of each coordinate
  body (maximally diversified pair between our two best pipelines). Eesh sets them on the web.
* Last-slot candidate (USER 09:20Z: "build only one, only 1 submission remaining"): **ourvzlb25r70ff** (IMGFLOW on the
  0.955 arm) building, no submit; the sr arm was DROPPED (twice board-neutral; on the V1284 body the rescue being OFF
  coincided with the +1 from ourvzl to ourvzlb25). Decide after t65b25r70ff's main-body read (waiter bgsi1uj06) and the
  user's go. LAST SAFE SUBMIT ~15:30Z (7 h scoring -> ~22:30Z < 23:59Z).
* USER 09:22Z: "read all forums once again" -> full re-sweep since 09-28 15:00Z running (scratchpad/wf31).
* 10:00Z: **V1284 GAIN > 1 REFUTED offline** (scratchpad/wf32/gain.py; public head on the 60 v1284cap movies, 31,874
  GT pairs, y/x only): least-squares optimal gain 44b6 g* 1.10 [1.06, 1.14] (error flat 1.0-1.2) but **6bba g* 0.53
  [0.43, 0.64] = the head OVER-corrects on 6bba** (y/x err 0.909 at g0.8 vs 0.932 at g1.0 vs 1.038 at g1.5); pooled g*
  0.61; only 18% of 6bba movies have g* > 1. The 09-25 "ourvg15/20 dead" note was reasoning-only (never board-tested),
  but the shrinkage hypothesis fails -> no gain arm. (g < 1 is offline-mildly better but the mixyx50r70 board read
  (V1284 weight halved toward SV) lost 2 ticks, and offline V1284 measures have disagreed with the board -> not a bet.)
* Forum re-sweep 09:40Z (scratchpad/wf31): nothing portable; no host posts; Kaggle AUTO-SELECTS if picks are not set
  (would likely pair 0.955 with a same-body 0.954 - Eesh must set picks); "don't write float centroids" (we write ints);
  johntaylorai publishes settings after the deadline; no notebook > 0.953.
* 09:18Z: **t65b25r70ff = 0.954** (tie). Since t65b25r70 sat ~#5 from the top of the 0.954 block, neither ff nor sr
  crossing to 0.955 means both effects are tiny or <= 0 on the main body -> ourvzlb25r70ff is unlikely to reach 0.956
  (we are #71 of 98 in the 0.955 block; ~+0.0003-0.0004 needed for a 0.956 display). Board 09:18Z: rank 448;
  595 above 0.953; bronze line 398 = 21st in the 0.955 block.

## 09-29 04:30Z: session restarted; 4 submissions still scoring (due ~07:30-10:00Z); reaction arm pre-building
Pending: ourvzlb25r70 56657610, t65b25r70ff 56659166, t65b25r70sr 56659169, mixyx50r70 56659511 (waiter re-armed after
the restart). Board 04:26Z: rank 445, 0.954 block ranks 441-574 (we are #5 from its top again), 0.955 block 331-440,
**bronze line 398 now in the MIDDLE of the 0.955 block** (public bronze needs ~0.9552+, not a bare 0.955); 574 teams
above 0.953. 09-29 slots: 4 used, 1 left (reaction). Pre-building **t65b25r70ffsr** (ff + sr both stacked on
t65b25r70; disjoint stages) so it can go out immediately if ff and/or sr climb. REACTION RULE: submit the reserve slot
by ~10:30Z at the latest (7 h scoring -> done ~17:30Z, well before 23:59Z).
05:15Z: **t65b25r70ffsr READY** (build_t65b25r70ffsr.py -> v_t65b25r70ffsr; add_t65b25r70ffsr_gate.py, backup
gate.py.bak_t65b25r70ffsr; 9 PASS / 31 FAIL self-test; visible GATE_PASS 05:10Z; pre-flowfix graph == t65b25r70sr;
flowfix == ff on 3/4 movies; nodes +387 vs t65b25r70 (= sr); divisions 79; diversity vs t65b25r70 0.0036 = ff 0.0023 +
sr 0.0013). Submit: `python ops/run_today.py ops/plan_t65b25r70ffsr.json --submit-only`.

## 09-29 01:10Z: WE ARE #5 FROM THE TOP OF THE 0.954 BLOCK -> one more small gain likely reads 0.955. USER: aim 0.955/0.956
Board 00:55Z: rank 429; 0.954 block = 137 teams (ranks 425-561), only 4 teams above us inside it; 0.955 block 312-424;
bronze line 397 now sits INSIDE the 0.955 block. The last climb (t65b25 -> t65b25r70) passed 25 teams inside the block.
The linker is at its measurable optimum on every axis (bonus plateau 2.5, tight >6.5 lost on board, vel/linefit optimal,
rawlink 0.70 tuned), so the next increment must be a different mechanism stacked on t65b25r70:
1. mixyx50r70 (0.5 SV + 0.5 V1284 y/x) - offline test running (scratchpad/wf30).
2. **t65b25r70ff** (IMGFLOW repair after rawlink, ported as build_t6r70ff.py did) - building.
3. **t65b25r70sr** (short-track rescue armed unconditionally, as t6sr) - building.
01:51Z: **t65b25r70ff SUBMITTED = 56659166** (visible GATE_PASS; pre-repair graph == t65b25r70; flowfix changed
30/3/3/292 edges; nodes/divisions unchanged; diversity vs t65b25r70 0.0023) and **t65b25r70sr SUBMITTED = 56659169**
(rescue fired on all 4 movies, +387 nodes / +303 edges, divisions unchanged; diversity 0.0013). 09-29 slots: 3 used, 2
left (blend mixyx50r70 + 1 reserve). Scores due ~08:30-09:30Z (waiter armed).
02:05Z: **mixyx50r70 SUBMITTED = 56659511** (user's coordinate-blend idea; y/x = 0.5*V1284 + 0.5*SV on the full t65b25r70
stack). Offline (wf30): FAILED the pre-registered bar (w=0.5 44b6 tail .0119 vs SV .0114; pooled .0093 vs .0092) -
~neutral vs t65b25r70, clearly better than pure V1284 (ourvzlb25r70) on both embryos; SV and V1284 errors are highly
correlated (r 0.82 y / 0.74 x) so averaging gains little; V1284 is 44b6-strong / 6bba-weak. Built under the team
leader's post-hoc relaxation ("build unless clearly worse than both"). Visible GATE_PASS; nodes -1.91% vs t65b25r70
(44b6_0b24845f -6.8% = the V1284 node cut, also present in ourvzlb25 = 0.954); divisions 76; sits between its parents
(matchdiff 0.029 / 0.023). 09-29 slots: 4 used, **1 left = reserve for a ~09:30-11:30Z reaction**.
SLOT PLAN 09-29: submit the passing ones ~03:00-05:00Z (scores ~10-12Z); keep 1 slot in reserve for a ~11:30Z reaction
(finishes before 23:59Z). ourvzlb25r70 (56657610) scores ~07:30-08:30Z.

## 09-29 00:46Z: ourvzlb25r70 SUBMITTED = 56657610 (09-29 slot 1/5; 4 left; LAST SAFE SUBMIT ~12:00Z)
Visible GATE_PASS (build_ourvzlb25r70.py; cells 2/5 byte-identical to t65b25r70's rawlink blocks; cell 4 V1284
untouched; pre-rawlink graph == ourvzlb25 exactly; rawlink accepted 846 vs t65b25r70's 989; divisions unchanged;
diversity vs t65b25r70 0.041). Score due ~07:30-08:30Z (waiter armed). If it tops ourvzlb25 it becomes pick B.
USER ~21:15Z: "mix both of them that will give a higher score" -> picks A = t65b25r70, B = ourvzlb25 line (Kaggle takes
the better of the two) + a true blend arm mixyx50r70 (y/x = 0.5*V1284 + 0.5*SV on the full stack) under offline test
(scratchpad/wf30 PREREG), built only if no worse than both parents.

## 09-28 20:05Z: **t65b25r70 = 0.954 = NEW REPRESENTATIVE**; ourvzlb25 = 0.954 (+1 vs ourvzl); t70b20 = 0.953 (-1)
* Third consecutive representative flip: t65b20 -> t65b25 -> **t65b25r70 (56640601)**. The rawlink 0.70 override STACKS
  with the climbing linker (tight 6.5 + bonus 2.5). Rank 427 -> **402 (5 places below the public bronze line 397)**;
  536 teams above 0.953.
* ourvzlb25 (56640901) = 0.954: the climbing linker transferred to the decorrelated V1284 body too (ourvzl 0.953).
* t70b20 (56641323) = 0.953: widening the tight gate past 6.5 HURTS on the board (matches its 44b6 replay weakness).
  Tight axis CLOSED at 6.5 -> t675b25 / t70b25 NOT submitted (the 14:20Z rule: t675b25 only if t70b20 did not read below
  t65b20).
* Rawlink threshold already tuned (09-22 unseen-embryo screen: 0.30-0.60 band hurts, 0.70 best, 0.80/0.90 smaller) ->
  no threshold variants.
* **09-29 00:00Z CANDIDATE: ourvzlb25r70** = ourvzlb25 + rawlink 0.70 (mirror of the step that made t65b25r70 the rep, on
  the decorrelated body). Building + gating + visible run now; submit when slots reset.
* PICKS: **A = t65b25r70 (56640601)**. B: ourvzlb25 (56640901) now sits at our best display (0.954) AND is the
  decorrelated hedge -> it dominates a same-body sibling as B (hedge at no display cost). Re-raising with the user (his
  "go for the jump" choice was made when the hedge was a tick lower at 0.953). If ourvzlb25r70 flips above ourvzlb25,
  it replaces ourvzlb25 as B.

## 09-28 18:57Z: **t65b25 = 0.954 AND THE REPRESENTATIVE FLIPPED AGAIN (56639660 > t65b20 > t6r70).** Rank 436 -> 427.
Second consecutive positive-side transfer on the node-neutral bonus line: bonus 1.6 (t65s3) -> 2.0 (t65b20, flip) -> 2.5
(t65b25, flip), exactly the replay's ordering (+1.91 -> +2.55 -> +2.93). The replay now calls positive moves right 2/2
on this line. **PICK A = t65b25 (56639660).** Board 18:57Z: 533 above 0.953, bronze line 397 -> we are 30 places below
PUBLIC bronze. Per the 14:20Z tree ("t65b25 flips -> t675b25, only if t70b20 did not read below t65b20"): t675b25 is
the 09-29 00:00Z candidate once t70b20's read is in; t70b25 if t70b20 flips instead. Pending: t65b25r70, ourvzlb25,
t70b20 (waiter bs6f2r5wf).

## 09-28 15:45Z: RE-SWEEP (scratchpad/wf28): nothing public > 0.953; ONE actionable lever: ILP_DIVISION_WEIGHT 0.4
* WARNING: board 15:30Z = 503 teams at >= 0.954; **our rank 410 = 14 places BELOW the public bronze line (396)**
  (we were 12 above it at 11:45Z). 412 of the 503 submitted since 09-27 15:00Z. Private decides; trend is bad.
* kunaldesale2408 V11 (run 10:41Z, unscored): validator ON + 7 sweep candidates; the run picked dcsafediv020
  (DeepCenter safe-div 0.25 -> 0.20; our xsvdc analogue lost). Not portable. Lineage Forge V11/V12 (0.947 body): copies
  of the forum levers below. No new weights/datasets. anhadmahajan06 = 0.946.
* **Forum 743929 (johntaylorai, rank 114, 0.959; "(AI)" account, unverified):** fork of the 0.953 public notebook +
  own post-processing (0.957), then **ILP_DIVISION_WEIGHT 1.2 -> 0.4 (0.958)**, then READMIT_MIN_SCORE 0.965 -> 0.94
  (0.959); each +0.001 vs a same-round control; node count moved < 1%; local validator blind. Our HANDOFF "ILP division
  weight PROVEN INERT" only covered weights >= 1 (0.4 lets the ILP fork). Readmit does not port (no readmit stage on
  the t6 body; x138 body on the never-submit list).
* ACTION: (a) t65b20d04 = t65b20 with ILP_DIVISION_WEIGHT 0.4: build + gate + visible run, diff vs t65b20 (inert or not);
  (b) full-path box replay (ILP reruns from recorded detections) of division weight 0.4 on 199 movies, edge + division
  parts. If it moves edges with nodes within 1% and gates pass -> the best-evidenced single-knob 09-29 slot.
* José Freitas (732103, rank 63, 0.962) says his synthetic set "works" - needs a retrain, not usable by the deadline.
* ~16:15Z: **t65b20d04 BUILT, GATED, visible GATE_PASS - ACTIVE, not inert** (build_t65b20d04.py -> v_t65b20d04; single
  env literal cell 0 `BIOHUB_ILP_DIVISION_WEIGHT` 1.2 -> 0.4, read by cells 2/4/7; gate add_t65b20d04_gate.py requires
  3 receipts of 0.4). Diff vs t65b20: submission differs, edge diversity 0.0026 (t65b25 vs t65b20 = 0.0015); nodes +101
  (+0.082%, worst movie +0.17%); written divisions 80 -> 84. Raw ILP now emits 1,059 forks (0 before) + 222 extra kept
  nodes, but the one-to-one motion relink discards every ILP fork; the effect reaches the output through the extra nodes
  and the learned bonus on second-child pairs. Node change < 1% as the forum team reported. Submit command:
  `python ops/run_today.py ops/plan_t65b20d04.json --submit-only`. Box replay (wf29) will say whether it helps offline.
* ~18:00Z: **ILP DIVISION WEIGHT 0.4 = NEGATIVE, CLOSED. Do NOT submit t65b20d04.** Full-path replay (edge model + ILP +
  cell 5, from batch1 records), all 199 movies, self-check byte-identical to the c5 path (80/80, 76/76): t65b20d04 vs
  t65b20 = **-0.87 [-1.25, -0.48] pooled, P(>0) 0.000**; 44b6 -1.82 [-3.42,-0.35], 6bba -0.69 [-1.01,-0.38]; edge part
  TP -25 / FP +86 / FN +25; division part exactly flat (the 123 extra written forks land on unannotated cells);
  nodes +0.19%; adjEJ wins/losses 24/157; still -0.31 after dropping the 10 worst movies. The ILP forks on noise
  (0 -> 43,092) and the relink discards them; what survives is extra kept nodes. The replay usually OVER-reads
  learned-edge changes, so a clean negative is convincing. The forum +0.001 (one board read, unverified account,
  different body) does not transfer.
* Box note: a stray `bash -c until [ -f /tmp/valdone ]; do :; done` busy-loop (nice 0) has spun one core ~31 h - not
  started by wf29; possibly an orphaned waiter from an earlier automation. Left alone; ask the user before killing.

## 09-28 14:20Z: TIGHT-GATE AXIS AT BONUS 2.5 (wf27, box ~/biohub/wf27, ranked_wf27.txt) - nothing beats t65b25 on the bar
| arm | pooled vs t6stk3 | 44b6 | 6bba | incr vs t65b25 (pooled / 44b6) |
| t675b25 (6.75/2.5) | +3.31 [+1.92,+4.87] | +1.85 | +3.85 | +0.39 [-0.39,+1.23] / -0.07 |
| t70b25 (7.0/2.5) | +3.28 [+1.83,+4.85] | +1.06 | +4.03 | +0.36 [-0.56,+1.32] / -0.86 |
| t65b25 (ref, reproduced exactly) | +2.93 [+1.72,+4.16] | +1.93 | +3.26 | ref |
| t60b25 (6.0/2.5) | +0.63 | +0.54 | +0.66 | -2.30 |
t70b25 vs t70b20: **+0.42 [+0.11,+0.73]**, both embryos positive (the cleanest increment). Past tight 6.5 all extra gain is
6bba; 44b6 peaks at 6.5; bonus 2.5 does NOT repair tight 7.0's 44b6 gap (-0.86 at b2.5 vs -0.75 at b2.0).
CORRECTION: "fork-neutral" only held for SCORED divisions (net 0); RAW output forks (safe-division insertions) fall with
wider tight gates: t65b20/t65b25 -1.7%, t675b25 -2.6%, t70b20 -2.9%, t70b25 -3.0%. t65b20's representative flip says
-1.7% is harmless on the board; tonight's t70b20 read tests ~-3%.
09-29 FOLLOW-UP TREE (slots usable until ~12:00Z): t70b20 flips the representative -> submit **t70b25**; t65b25 flips ->
**t675b25** (weak, ~0-0.2 tick; only if t70b20 did not read below t65b20); neither flips -> HOLD. Both being pre-built +
gated + visible-run now (no submit).
~16:00Z: BOTH PRE-BUILT, GATED, visible GATE_PASS, NOT submitted: **t70b25** (build_t70b25.py -> v_t70b25, cell 0 only
vs t70b20; add_t70b25_gate.py keeps the tight-edge floor; nodes +0.008% vs t70b20; tight edges identical to t70b20) and
**t675b25** (build_t675b25.py -> v_t675b25, cell 0 only vs t65b25; add_t675b25_gate.py; nodes -0.004% vs t65b25; tight
edges strictly between the 6.5 and 7.0 counts on every movie). Submit commands:
`python ops/run_today.py ops/plan_t70b25.json --submit-only` / `python ops/run_today.py ops/plan_t675b25.json --submit-only`.

## 09-28 11:50Z: t65b20 = 0.954 AND THE REPRESENTATIVE FLIPPED TO IT (56628029 > t6r70 at full precision). t65b25 SUBMITTED.
First arm in days to beat t6r70 on the board (sub-tick; display unchanged). The node-neutral linker replay's positive
side transferred at least partially (t65b20 replay +2.55). => **NEW PICK A = t65b20 (56628029)**. Following the
pre-registered spirit (a representative flip counts like a >= 0.955 read for pick A), the gated neighbor
**t65b25 (bonus 2.5, replay +2.93, incr +0.38 over t65b20 with 44b6 LB > 0) SUBMITTED 11:46Z = 56639660** (09-28 slot 2;
3 left). Score due ~18:30-19:30Z (waiter armed). If t65b25 flips the representative again, it becomes pick A.
Board 11:45Z: **476 above 0.953; rank 384; bronze line 396 -> PUBLIC margin only 12 places** (74 -> 40 -> 28 -> 12).
**USER DECISION ~11:55Z: "go for the jump"** -> A = representative of {t65b20, t65b25}; B = the other of the pair if it
displays >= 0.954, else t6r70. ourvzl hedge DECLINED knowingly (siblings rise/fall together; less bronze protection).
"Jump" shot in build (~11:58Z): **t65b25r70** = t65b25 linker settings + t6r70's raw-ILP override 0.70 (stacks the two
changes that each beat their base at full precision; replay can't read rawlink, so a board-only bet). Builder
build_t65b25r70.py, gate add_t65b25r70_gate.py, plan plan_t65b25r70.json; submit on a 09-28 slot if the visible run
GATE_PASSes (user's standing "go for the jump" / "use slots on shots" direction).
**USER 12:00Z: "submit the 3 other submissions with 3 different angles".** The 3 remaining 09-28 slots:
1. STACK angle t65b25r70 (rawlink 0.70 + tight 6.5 + bonus 2.5): visible GATE_PASS (pre-rawlink graph == t65b25
   exactly; rawlink accepted 989 vs t6r70's 1113; divisions unchanged) -> **SUBMITTED 12:23Z = 56640601** (slot 3/5).
2. TIGHT-GATE angle: **t70b20 SUBMITTED 12:54Z = 56641323** (slot 5/5; ALL 09-28 slots used). Visible GATE_PASS, nodes
   +0.021% (matches replay), tight edges +143/+155/+36/+494 (gate enforces >= the 6.5 counts), safe divisions net 0.
   Knowingly overrides the 06:40Z "do not chase t70b20" note (44b6 incr -0.75) because the user asked for 3 angles.
   Original plan: **t70b20** (t65b20 with tight 7.0; replay +2.86, 6bba +3.64, 44b6 +0.53) - agent builds, gates,
   visible-runs and SUBMITS itself on GATE_PASS (authorized). build_t70b20.py / add_t70b20_gate.py / plan_t70b20.json.
3. DECORRELATED-BODY angle: **ourvzlb25 SUBMITTED 12:36Z = 56640901** (slot 4/5). Visible GATE_PASS, detection md5 ==
   ourvzl's, SV/z-to-arr pins exact; FINAL nodes -0.084% total (44b6_0b24845f -0.47% = the short-track RESCUE threshold
   flipping off (0.1006 -> 0.0999 removal share), board-neutral per the t6sr tie; 6bba_05b6850b -0.31%). Original plan:
   **ourvzlb25** (ourvzl V1284 body + tight 6.5 + bonus 2.5; board-only, replay can't judge
   V1284) - agent builds/gates/visible-runs/SUBMITS on GATE_PASS. If it reads >= 0.954 it is the ideal pick B
   (upside + hedge). build_ourvzlb25.py / add_ourvzlb25_gate.py (sv_mark placed INSIDE the literal) / plan_ourvzlb25.json.
Kaggle max 2 concurrent GPU sessions: agents wait for a free slot. College box reconnected 11:54Z, idle.
(Superseded analysis kept below.)
PICK B: t65b20 and t65b25 are t65s3-body siblings (highly correlated with t65s3 and t6r70), so the decorrelated hedge
**B = ourvzl (56572442, V1284 body)** is even more clearly the bronze-max choice now. Per the 06:05Z rule (t65b20 read
0.954), re-asking the user with ourvzl as default; if no answer by ~09-29 11:00Z the sheet says A = best of
{t65b20, t65b25} at full precision, B = ourvzl.

## 09-28 06:00Z: BRONZE MARGIN ERODING FAST - field growth 4.3 teams/h; deadline projection lands in the MC "hard" band
lb_trend 05:48Z: 445 above 0.953 (426 at 01:22Z, 380 on 09-27 14:08Z, 258 on 09-26 am); rank 368; bronze line 396
(10% of 3964) -> PUBLIC margin only 28 places (74 -> 40 -> 28 over two days). Growth over the last 24 h = 4.3/h ->
projected ~626 above 0.953 at the 09-29 23:59Z close (bronze line ~401). The wf20 MC bands: ~386 -> P(bronze) 0.65,
~460 -> 0.57, ~540 -> 0.48; the projection is at/beyond "hard" -> honest P(bronze) now ~0.45-0.50, NOT 0.55-0.65.
IMPLICATION: bronze on private = our pick beating the x138 clone block; the only pick-side lever that raises it is
B = ourvzl (V1284 body, decorrelated coordinate factor; +0.03 in every MC sensitivity, sign robust). The silver
lottery t65s3 preserves (~0.19-0.21) is now worth less than the bronze hedge. RECOMMEND B = ourvzl unless t65b20 reads
>= 0.955 (then t65b20 itself is B or A). User deferred the B choice on 09-27; re-raised with these numbers 09-28 06:05Z.
**USER DECISION 09-28 06:05Z: "Wait for t65b20 score."** RULE: when 56628029 lands: >= 0.955 -> t65b20 is B (or A if the
representative flips), no further question needed; 0.954 or lower -> RE-ASK the user for B with **ourvzl as the
default/recommended**, and if he does not answer before ~09-29 11:00Z, the pick sheet says ourvzl. Picks are set by
Eesh on the web by ~09-29 12:00Z.
(threat_watch "DANGER" alerts fire on the stale SILVER line; the bronze line is the live one. 3 watch procs = harmless
duplicates from re-arms.)

## 09-28 06:40Z: t65b20 NEIGHBOR REPLAY (wf26, box ~/biohub/wf26/lensA; 4 arms x 72 movies, self-check reproduces wf25)
| arm | tight/bonus | pooled vs t6stk3 | 44b6 | 6bba | dNodes | incr vs t65b20 |
| **t65b25** | 6.5/2.5 | **+2.93 [+1.72,+4.16]** | **+1.93 [+0.46,+3.53]** | +3.26 | +0.008% | **+0.38 [+0.09,+0.67]** (44b6 +0.64 LB +0.01) |
| t65b30 | 6.5/3.0 | +2.90 | +1.98 | +3.20 | +0.011% | +0.34 [-0.14,+0.82] (plateau, dominated) |
| t70b20 | 7.0/2.0 | +2.86 | +0.53 [-1.37,..] | +3.64 | +0.018% | 44b6 -0.75: tight-7 = 6bba-only, CLOSED |
| t65b20 (submitted) | 6.5/2.0 | +2.55 | +1.28 [-0.05,..] | +2.98 | +0.005% | ref |
All fork-neutral (0 divisions moved). Bonus monotone to 2.5 then plateaus (b30 adds nothing, adds nodes).
**t65b25 is the ONLY neighbor clearing the sweep's failing criterion (44b6 LB +0.46 > 0) with a positive increment LB.**
DECISION RULES for the t65b20 score (56628029, due ~10:30-11:30Z):
* >= 0.955: submit t65b25 (t65s3 body, bonus 2.5; cell-0-only change, inherits t65b20's build/gate path) same day.
  Calibrated expectation only ~+0.36 board tick over t65b20 (confirm-the-family shot). Do NOT chase t70b20 / b30.
* 0.954 (tie): NO neighbor is worth a slot (t65b25's +0.38 replay edge is a fraction of the demonstrated positive-side
  over-read) -> hold slots, picks unchanged.
* <= 0.953: the linker-neighbor family is falsified on the board; t65b25 dead.
05:50Z: **t65b25 PRE-BUILT + GATED + visible GATE_PASS (NOT submitted)**: build_t65b25.py -> v_t65b25 (cell 0 only vs
t65b20: bonus 2.0->2.5 + tag), add_t65b25_gate.py (backup gate.py.bak_t65b25; negatives t65b20/t65s3/t6stk3 FAIL,
6 regressions PASS), plan_t65b25.json; visible run 05:19->05:48Z, 0 tracebacks, nodes +8 (+0.007%) vs t65b20,
diversity vs t6r70 2.02%. Submit ONLY if 56628029 >= 0.955: `python ops/run_today.py ops/plan_t65b25.json --submit-only`.

## 09-28 ~03:30Z: LINKER SWEEP (wnap4nn6m, box ~/biohub/wf25) = NO config clears the bar; ONE best-evidenced shot: t65b20
11 node-neutral arms x 72 GT-richest movies (36/36), 817 runs, 0 fails, self-check stk3rep byte-identical = 0.00.
Production on the t6 body = tight 6.0 / velocity 0.25 / bonus 1.6 / linefit 0.8/2 / relaxed 10.0.
| config | pooled | 44b6 | 6bba | nodes | forks |
| **t65b20** (tight6.5+bonus2.0) | **+2.55 [+1.46,+3.70]** | +1.28 [-0.04,+2.66] | +2.98 [+1.51,+4.57] | +0.005% | 0 |
| t70 | +2.16 | +0.01 | +2.88 | +0.016% | 0 |
| t65 (=t65s3, board 0.954 tie) | +1.91 | +0.87 | +2.26 | | |
| b20 | +0.54 | +0.30 | +0.62 | | |
| lfw90 / v35 / v15 | ~0 | | | | | (vel 0.25 + linefit 0.8 already optimal)
| r8 / r9 (relaxed gate) | negative, DELETES 0.12-0.28% nodes -> rejected |
Interactions additive (t65b20 ~ t65 + b20), not synergistic. The positive signal is 6bba-heavy (44b6 flat by tight 7.0)
= a cross-embryo asymmetry risk. t65b20 FAILS the bar only on 44b6 LB (-0.04). Calibration says board ~ +1.6, but the
positive side has never held (t65s3 replay +1.37 -> board 0). HONEST: most likely another 0.954 tie; small chance 0.955.
DECISION: build + gate + visible-run + SUBMIT t65b20 on a 09-28 slot as the best-evidenced, node-neutral, FORK-NEUTRAL
(no division risk) shot left (user wants slots used on shots; can't hurt finals). Linker axis otherwise EXHAUSTED.
03:47Z: t65b20 built (build_t65b20.py -> v_t65b20, only cell 0 differs from t65s3: bonus 1.6->2.0 + marker), gate
installed (add_t65b20_gate.py, backup gate.py.bak_t65b20; negatives FAIL, regressions PASS), visible run GATE_PASS
(0 tracebacks; nodes -7 = -0.006%; safe divs +2 GPU drift), diversity vs t6r70 1.95% (t65s3 1.88%).
**SUBMITTED = 56628029** (09-28 slot 1/5; 4 left). Score due ~10:30-11:30Z (waiter armed). Rule: >= 0.955 -> it becomes
pick B (or A if representative flips); 0.954 -> tie, picks unchanged; <= 0.953 -> confirms the positive-side over-read.

## 09-28 01:25Z: overnight shots scored: t65s3ff = 0.954 (tie), t6stk3ff2 = 0.952 (-2). Flow family confirmed capped.
Neither beats t6r70. Board confirmed the offline read this time (t6stk3ff2's aggressive flowcut = -2). Board 01:22Z:
426 teams above 0.953 (was 380), rank 356 (silver line 198, bronze line 396 - we are still 40 ranks above bronze on
PUBLIC). Picks unchanged. 09-28 = 5 fresh slots. NEXT RESEARCH: the ONE class where the replay is a validated board
predictor (node-neutral linker changes: board = -0.83 + 0.95*replay, LOO-RMSE 0.6) has NOT been swept systematically for
a POSITIVE config - launching a linker-parameter sweep on the wf16 lensA fast-replay to look for any config with
replay >= +2 (90% lower bound > +0.8) on BOTH embryos, node-neutral. Most likely empty (velocity/bonus/tight/gap/rescue/
safe-div all individually tested) but it is the one cheap, board-transferable-for-this-class search left.

## 09-27 17:10Z: COORD-INJECT (yuki0731/biohub-coord-inject) = FALSIFIED, CLOSED. The last moonshot is dead.
Workflow w430zutl6 (scratchpad/wf24, box ~/biohub/wf24). The refiners are SEPARABLE from the detector
(heatmap_tag='' -> use_heatmap=False; they take a raw pooled image crop -> refined coord), so Path A ("refine OUR
coords") is a clean test. On 35 train movies (21 44b6 / 14 6bba, 13,419 GT edges), pre-registered md5-locked before any
coord-inject tail computed, harness validated (prodSV reproduces baseline 44b6 E>3 0.0117): coord-inject makes the >3um
displacement tail WORSE than production SV on BOTH embryos, EVERY axis, EVERY threshold, bootstrap 90% CIs excluding 0
on the worse side. CI-z (the new z-refiner axis) 44b6 -0.0033 / 6bba -0.0027; CI-xy -0.0067/-0.0049; CI-all
-0.0138/-0.0089 (~-2.3 ticks pooled, -3.07 on 44b6). Also moves nodes AWAY from GT (median pos err 44b6 1.010->1.233 um).
Mechanism: the refiner optimizes the board-FLAT node<=2um quantity and, fitted to THEIR detector's candidate
distribution, mislocalizes ours. Path B (their full 4-seed ensemble) not warranted (same flat quantity; the refined-coord
distribution is tail-harmful in place). NO build, NO gate, NO push, NO submit; box left clean.
=> Every lever is now closed on the board. NO candidate with board-transferable evidence exists. Remaining slots (09-27
x2 expiring 00:00Z, then 5 on 09-28, ~5 on 09-29 morning) have NOTHING worth spending on: everything ready is a tie
(no info, won't be picked) or known-negative; submitting them = near-duplicate LB probing (banned) and does not change
the finals. HOLD the slots. THE GAME IS NOW PURELY FINAL-PICK SELECTION + setting them on time.
## 09-27 17:10Z: USER ordered "submit 2 things even if local is not passing" -> t6stk3ff2 = 56614776, t65s3ff = 56614784
User's reasoning: our offline instruments have been wrong (they over-read the flow family). Chose the 2 GATED, ready,
GENUINELY-DIFFERENT-output arms never board-tested (NOT decimal-probing duplicates; a low score can't hurt the finals):
t6stk3ff2 (t6stk3 body + IMGFLOW + flowcut, more aggressive than t6stk3ff's 0.954 tie) and t65s3ff (IMGFLOW on the
pick-B body). Both GATE_PASS at submit. 09-27 slots now 5/5 used. Scores due ~23:30-00:30Z (waiter b3smpe0vh, rep_check
NAMES updated). Honest prior: both flow-family, most likely 0.953-0.954; small tail chance one reads 0.955. If either
reads >= 0.955 (or its representative flips), reconsider picks. Otherwise picks unchanged.

PICKS: A t6r70 56483584; B = t65s3 56496604 (balanced, silver-max ~0.21/0.65) OR ourvzl 56572442 (bronze-max ~0.19/0.68)
- user deferred the choice (09-27), will decide before 09-29 12:00Z. Eesh sets 2 boxes on the web by 12:00Z 09-29,
re-check 22:00-23:00Z. Honest: silver ~5-25% (needs ~0.956 we don't have), bronze ~48-65% (FAVORITE). Top-100 not reachable.

## 09-27 15:20Z: TOP-100 SWEEP + BRONZE MC (w3jaxadms). One real PICK lever (costless) + one lottery ticket.
BRONZE (fresh MC, board 14:32Z, 386 above 0.953): P(bronze) ~0.55 central (0.48-0.65), we are a FAVORITE not safe;
decline is field growth (~20 teams/day), not pick choice. Dominant risk = OUR private falling below the ~397-team x138
clone block (P(our better pick beats x138) only ~0.67 t65s3 / ~0.70 ourvzl); if we lose that we drop to rank ~730+.
**PICK-B lever (NO slot needed, both already submitted):** ourvzl (56572442, 0.953) is the P(bronze)-MAX B: +0.03
central over t65s3 (sign robust across all sensitivities) because it is the ONLY proven arm on the V1284 body (drops the
shared coordinate factor Cs) so it decorrelates from the dominant risk. COST: -0.01..-0.03 silver. t65s3 stays
silver-MAX (0.208 vs 0.195) + within-body max diversity. => balanced = {t6r70, t65s3}; bronze-max = {t6r70, ourvzl}.
Do NOT pick xpub (0 bronze value on this field), t6dl (==t6stk3), t6stk3fl (flow family closed on board).
TOP-100 PUBLIC = essentially dry: all 100 >= 0.959; 89/100 publish NO comp kernel; the 11 that do are the <=0.953
baseline family we already ported; no public kernel/dataset anywhere > 0.953.
ONE NEW ASSET (CC0, not in HANDOFF): **yuki0731/biohub-coord-inject** (team #69, 0.961) = the actual 171-movie retrained
V1284 localization head + a DEDICATED z-refiner + rot180-distilled xy refiner + 8-view/rot TTA + coord_inject_runtime.py
(read to scratchpad/wf23/t100/ci/). This is exactly HANDOFF's one named untested moonshot ("V1284 head retrained on far
more movies") AND adds the two things that sank V1284 (z never moved; no cross-view TTA). Base rate negative-to-flat
(V1284 body-interaction -3 on our body; coord refinement hits the FLAT node<=2um quantity). Worth ONE validated box run
(slots ~free): capture on our detections -> cheap falsification (>3um displacement tail per embryo vs production SV
0.0114/0.0070) -> only if it beats BOTH by >~2 ticks, full replay + LOEO node-neutral. Do NOT touch a pick unless
LOEO-positive on the held-out embryo. (Also soutasakurai vector-field-unet CC0 = flow+split predictor, LOW priority: flow
family closed.) Running as workflow (coord-inject validation).
ACTION FOR EESH: set 2 picks on the web by 09-29 12:00Z (rerun must finish before 23:59Z); re-check 22:00-23:00Z.

## 09-27 14:55Z: LAST-PUSH SCAN (wjh25hycv) = NO board-transferable lever remains; HOLD the slots, KEEP the picks
* Discussion re-read (full 120-thread list, scratchpad/wf22/forum): NOTHING new since 04:45Z - 3 spam comments, one
  unverified "stuck at 0.957" self-report, one "AI labeling tool" aside. No host post, no method disclosure, no
  runtime/metric detail. 743006 re-endorses LOEO methodology; 742942 (~70% of "FP" are real unannotated cells) and
  742266 (loss tracks node count not offline-J) reinforce our closed families.
* Detector/localization axis: CLOSED by construction. The metric pays for UNDER-detection (T_pred/T_true ~0.76 = +2.4%
  node-count credit) and tracks the >3um displacement TAIL, not centroid RMS (node<=2um is flat across all thresholds).
  So recall/ensemble/TTA changes spend the credit + don't touch the tail; "better localization" optimizes the flat
  quantity. Only ever-positive localization lever = the sub-voxel soft-argmax already in the body (+7), family saturated.
  Weight-averaging public folds == synp (lost). z-flip TTA -11/-2; 16-view breaks 12 h.
* WHAT-TRANSFERS table (definitive, box calib files): node-neutral linker changes at/below best -> replay predicts board
  well (board = -0.83 + 0.95*replay, Spearman .977, LOO-RMSE 0.61) BUT every anchor is <= 0 (loser regime, +0.82 tick
  optimism). The POSITIVE side (the only region that climbs): the instrument BREAKS - IMGFLOW replay +2.85 -> board 0;
  FLOWLINK replay +9.94 -> board -1; LOEO ROSE (+1.15 -> +2.99) as the board FELL. 3 instruments, 4 attempts, flow
  family over-read/inverted every time. => the board is effectively unpredictable for any change capable of climbing.
* DECISION: **HOLD the 09-27/28 slots** (scores already computed; nothing queued has board-transferable evidence; board
  latency 6-7 h so nothing new lands in time). **Picks: A t6r70 56483584, B t65s3 56496604** (t65s3 = max diversity 3.8%
  vs t6r70; do NOT switch B to FLOWLINK: 0.953, -6% forks = t6svT15 signature, only the contradicted LOEO prior favors
  it). Honest odds: silver ~5-25% (need ~0.956 we don't have), bronze ~35-70% (reduces to: our pipeline private beats
  the x138 clone; 2nd pick barely moves it). 0.02 jump NOT reachable from public assets (0.97 teams retrained detector
  heads; that gain doesn't survive to unseen embryos for us).
* ACTION FOR EESH: set the 2 picks on the Kaggle web UI by ~09-29 12:00Z (rerun must finish before 23:59Z); re-check
  22:00-23:00Z. Only spend a slot if a NEW detector/localization signature appears (the one class that ever transferred).

## 09-27 14:30Z: FLOWLINK (t6stk3fl, 56601558) = **0.953** (-1). FLOW FAMILY CLOSED ON THE BOARD. Picks unchanged.
* Board: t6stk3ff (IMGFLOW) 0.954 tie, t6stk3fl (FLOWLINK) 0.953. Offline: IMGFLOW replay +2.9 / LOEO +1.23; FLOWLINK
  replay +9.9 / LOEO +2.99. => NEITHER the calibrated replay NOR the LOEO unseen-embryo check predicts the board for
  image-flow changes (both over-read; transfer ~0 or negative). Possible extra cost in FLOWLINK: division forks -6%.
* Follow-ups (workflow w9as2ln5r died with the session; results recovered from ~/biohub/wf21):
  - C t6stk3fld ("division-safe" FLOWLINK: frozen base division families): forks STILL -6.0% pooled (-5.2% dense) ->
    pre-registered P1 FAIL (edge gain kept: held-out +8.39 vs FLOWLINK +8.53; LOEO +2.84 vs base). DEAD.
  - A t65s3fl (FLOWLINK on t65s3): LOEO fl65 vs base +2.98, vs t6stk3fl -0.02 = the same effect as FLOWLINK. DEAD.
  - t65s3ff, t6stk3ff2 (IMGFLOW variants): DEAD with the family.
* Picks stay A t6r70 56483584, B t65s3 56496604 (the MC's preference for t6stk3fl as B rested on the LOEO prior, which the
  board has now contradicted twice). Board 14:08Z: rank 315; 380 teams above 0.953; silver line 197 near the top of the
  0.955 block (192-267) -> silver needs ~0.956; bronze line 395 is inside the 0.953 (x138-clone) block, so bronze on
  private ~= our pick's private beating the x138 clone.
* Remaining slots: 09-27 2, 09-28 5, 09-29 morning. NO candidate with board-transferable evidence exists. Detector
  fine-tunes were board-negative before (ftaugb21 -10, ftgc0 -5). Do not spend slots on EV~0 near-duplicates.

## 09-27 08:10Z: CONSENSUS DEAD + MC REFRESH (wkm7bjid1 agents died on an API outage; their box work survived in ~/biohub/wf20)
* Output-level majority vote (trackA: P / V2 / V3 / V4 over {t6stk3, t65s3, t6sr, t6stk3ff, t6stk3fla, ...}): every vote
  variant is WORSE than the best single arm (FLOWLINK): replay -9.6 (P), LOEO -1.7..-3.0; votes just dilute FLOWLINK's
  edits back toward the base. CLOSED. (score_all.json, loeo_cons.json, replay_judgement.json)
* MC refresh (~/biohub/wf20/mc/mc2_report.txt; board 07:14Z; 356 above 0.953; fl scenarios = t6stk3fl's display):
  NOW (sigma .002): t6r70 alone 0.21/0.68 (P silver / P bronze), +t65s3 0.25/0.71, +t6stk3ff 0.25/0.72, +t6stk3fl
  0.43/0.82 (prior over fl's display). DEADLINE projection (field above x138 grows to ~600): t6r70+t65s3 only
  0.05/0.36 (!), +t6stk3fl 0.16/0.54 (0.27/0.68 if fl >= 0.956, 0.10/0.45 if fl = 0.954). The model gives FLOWLINK a
  LOEO-informed private prior; that is its main assumption (unverified: the MC verifier agent died). Even at a 0.954
  display, t6stk3fl as pick B beats t65s3 in this model. => bronze is NO LONGER SAFE with the current picks.

## 09-27 07:10Z: t6stk3ff = 0.954 (tie; representative still t6r70), xpubz = 0.950 (-3). t6stk3fl SUBMITTED = 56601558
* IMGFLOW on the board: display 0.954, not above t6r70 at full precision. Replay +2.9 / calibrated +2.1 did NOT show;
  consistent with the LOEO-shrunk ~+0.8 or less. => the replay calibration's positive side over-reads image-flow
  repairs (in-sample detector); LOEO is the better guide for this family.
* xpubz 0.950: SV z to arr + V1284 y/x on the x138 body loses 3 vs xpub. x138-body line CLOSED.
* DEVIATION from the 04:10Z rule ("<= 0.954 -> hold t6stk3fl"), made deliberately: ~13 slots remain with almost no other
  candidates, a weak read costs nothing for the finals, and FLOWLINK has the strongest unseen-embryo evidence of any arm
  (LOEO +2.99 [+0.59, +5.94] vs base, ~2.4x IMGFLOW's +1.23). Known risk: division forks -6.4% (t6svT15 pattern).
  Submitted 07:08Z (09-27 slot 3/5; 2 left today). Score due ~14:00-15:00Z (waiter b3qchn9pq).
* t65s3ff DEAD (ties t6stk3ff on LOEO; t6stk3ff did not reach 0.955). t6stk3ff2 on hold (needs a positive IMGFLOW read).
* 07:20Z workflow wkm7bjid1 (run wf_115ca28f-495; box ~/biohub/wf20, scratchpad/wf20): (A) output-level edge
  CONSENSUS (majority vote) across our 0.954-family arms on the replay + LOEO (never tried before); (B) final-pick MC
  refresh with the current board + LOEO-informed priors, decision rules for the t6stk3fl score.
* Picks unchanged: A t6r70 56483584, B t65s3 56496604. Board 07:07Z: rank 293; 356 teams above 0.953; 0.955 block
  ranks 174-246, silver line 197.

## 09-27 04:45Z: FORUM / NOTEBOOK / BOARD RE-SWEEP (w8ks8zk52, scratchpad/wf19) - no technique to port; two operational notes
* Forum: 8 threads active since 09-25, none board-measured, no host statement, nothing on motion/flow. 743765 (unconfirmed,
  participant reply): a submission must FINISH scoring before 09-29 23:59Z to count -> our reruns take 6.5-7.5 h (+0.5 h
  with IMGFLOW): submit the last candidates on 09-27/28, nothing after ~09-29 12:00Z. 742942 comments: GT division
  coordinates/timing noisy (daughters sometimes 1 frame late), ~70% of "FP" detections are real unannotated cells.
  743006: shake-up stats (public gain holds on private ~75% in code comps) -> prefer LOEO-backed changes.
* Notebooks: nothing public above 0.953 (all 1,041 kernels checked); amanatar v6 has a silent REPAIR FAILED
  (NameError) -> our gate's "REPAIR FAILED" forbid stays essential.
* Board 03:44Z: 334 teams above 0.953 (MC assumptions of ~230 are stale; re-run mc_silver before finals); 0.955+ 235,
  0.956+ 163 (+2.2/h), 0.957+ 120; silver line rank 196 inside the 0.955 block; straight-line projection: 0.956+ passes
  rank 196 ~09-27 19:00Z, 0.957+ ~09-29 10:00Z. OUR RANK 281. Fast private jumps (taiseiu 0.953 -> 0.971 in 5 subs).

## 09-27 ~04:10Z: FLOWLINK (t6stk3fl) - huge replay gain, LOEO marginal -> verifier RESEARCH-MORE; PREPARED, not submitted
w3ju4mqrv (run wf_66010cb2-7b3; scratchpad/wf18, box ~/biohub/wf18). Injection = cell-5 motion relink (the ILP has no
distance term: edge_weight = -edge_prob): sources in flagged windows (|f| >= 5 um, >= 5 nodes) use anchor = p + f,
predicted = anchor; gate/cost from it; ILP byte-identical. t6stk3fl = FLOWLINK + IMGFLOW repair (repair adds +0.08).
PREREG 01:01Z (md5 d949b071) before any measurement; held-out = md5-odd 110 movies.
| comparison | pooled | held-out 110 | LOEO (44b6, 6bba-only models) |
| fl vs t6stk3 | +9.94 [+6.98, +13.12] | +8.53 | FLA vs base +2.99 [+0.59, +5.94] (FF vs base +1.23) |
| fl vs t6stk3ff | +7.09 [+4.51, +9.87] | +5.79 [+2.69, +9.04] | +1.76 [-0.07, +4.00] (P 0.94; 29/11) |
Nulls: negated flow -4.83 (LOEO), zero +0.11. FAILED pre-registered C3 (LOEO lower bound -0.07) and C4 (node counts:
33 movies move > 0.3%, all from downstream short-track/gap-fill stages; rho term +0.04). Verifier: LOEO increment rests
on one movie (drop3 +0.10, drop5 -0.26); replay gain +0.98 after dropping the top 20 dense 6bba movies; **division forks
-6.4% (3071 -> 2875; visible 6bba_05db0fb1 25 -> 19, same signature as t6svT15)**; in-sample inflation 3.8x.
PREPARED anyway so it is ready for the t6stk3ff board read: gate INSTALLED (ops/add_t6stk3fl_gate.py, backup
gate.py.bak_t6stk3fl; pins = box c5 replay of the same kernel; negatives FAIL, regressions PASS), plan
ops/plan_t6stk3fl.json, visible run COMPLETE 03:46Z: first GATE_FAIL only on the 4 pinned flow DIGESTS (Kaggle vs box
float FFT differ; flagged windows 62/27/36/47, relink flagged_sources, FINAL counts and written edges all == the box
replay pins) -> digest pins relaxed to [0-9a-f]{12} (backup gate.py.bak_t6stk3fl_digest) -> **GATE_PASS**, 0 tracebacks,
flow 8.6-9.1 s/movie; regressions + negative still correct. READY. DECISION after t6stk3ff scores:
>= 0.956 (replay positive side confirmed at ~calibration) -> t6stk3fl becomes the top candidate; 0.955 -> t65s3ff first,
t6stk3fl a considered second; <= 0.954 -> hold t6stk3fl (LOEO alone does not clear the bar).

## 09-27 01:40Z: IMGFLOW FOLLOW-UPS (w7y9sl49t, run wf_49586828-fdd) - two conditional tickets READY/in prep, C dead
* **t65s3ff** (IMGFLOW on the pick-B body): builder scratch_kernels/build_t65s3ff.py, gate INSTALLED
  (ops/add_t65s3ff_gate.py, backup gate.py.bak_t65s3ff), plan ops/plan_t65s3ff.json, visible run GATE_PASS (edges changed
  180/7/8/313), replay == Kaggle on 4/4. Replays: both embryos +, held-out 77 +; LOEO (t65s3 linker) +1.12 [+0.41, +1.99]
  9/0. On LOEO it TIES t6stk3ff (0.67193 vs 0.67191); diversity vs t6r70 1.83%, vs t6stk3ff 1.25%.
  RULE: submit (`python ops/run_today.py ops/plan_t65s3ff.json --submit-only`) ONLY if t6stk3ff displays >= 0.955
  (then P(t65s3ff >= 0.955) ~0.75); DEAD if t6stk3ff <= 0.954.
* **t6stk3ff2** (IMGFLOW + pre-registered FLOWCUT: in flagged windows cut edges with flow residual >= 6.5 um and
  cos < 0.8, then a 2nd repair pass): replays over t6stk3ff +2.43 [+1.13, +3.84] (held-out half +1.54); LOEO +1.94 but
  on held-out LOEO movies only +1.03 [-0.26, +2.92] and a ROTATED-flow cut placebo gives 76% of it (most gain = freeing
  sources in high-motion windows). Verifier: weak conditional candidate, ~+0.4 over t6stk3ff. Gate INSTALLED
  (ops/add_t6stk3ff2_gate.py, backup gate.py.bak_t6stk3ff2; negatives t6stk3ff/t6stk3 FAIL, regressions PASS), plan
  ops/plan_t6stk3ff2.json, visible run 01:32Z **GATE_PASS**, 0 tracebacks, written edges 24809/19396/5877/67759 ==
  the offline prediction exactly (cut 189/20/92/1038). READY.
  RULE: submit only if t6stk3ff displays >= 0.955 (maybe 0.954 if the representative flips to t6stk3ff).
* Track C (image-evidence merge of straddling detection pairs) DEAD: IMGMERGE-1 -3.41 ticks pooled, -2.36 held-out.
* 01:50Z: workflow w3ju4mqrv (run wf_66010cb2-7b3; box ~/biohub/wf18, scratchpad/wf18): flow INSIDE the linker (shift
  t+1 candidate geometry / relink motion by the image flow in flagged windows only), pre-registered, replay + held-out +
  LOEO, verifier. Would become t6stk3fl if it passes.

## 09-27 00:20Z: REPLAY IS A VALIDATED INSTRUMENT FOR NODE-NEUTRAL POST-DETECTION (LINKER) CHANGES (wdjiob01y lens A)
Box ~/biohub/wf16/lensA (fast path nbrun_c5.py: byte-identical to full replays in 7/7 checks; replay a new arm:
put notebook in batchA/nbs/, `ARMS="<arm>@t6stk3" bash launch.sh`; score: `bash score_lensA.sh OUT.json <arms>` then
`calib.py OUT.json`). Calibration vs board (n=198 movies):
* LINKER arms, no rawlink (11 anchors: t6sr, t65s3, t6w72, t6lf, stk3, t60h, t65h, hsg200, lcbonus2, lcvel2, gdiv):
  Spearman 0.977, sign 9/9, board-gap>=2 pairs ordered 28/28; **board ~= -0.83 + 0.95 x replay, LOO RMSE 0.61 tick**.
  Bias replay - board = +0.82 (10/10 arms). EVERY linker anchor is <= 0 on the board: no positive anchor yet
  (t6stk3ff will be the first test of the positive side).
* RAWLINK / trust-the-learned-edge-model changes: replay +14 ticks too high (t6r70 +14.1 replay vs 0 board) -> UNUSABLE.
* SV coordinate changes: under-read (bias +2.7); y/x invisible; only >= 5-tick directions.
* Division part: needs >= ~100 movies (1 div TP ~0.46 tick; SE ~0.65 tick at 198); below that use the edge part only.
* SCREEN BAR for a slot: replay >= +2 with 90% lower bound > +0.8, both embryos, edge events not confined to <= 3
  movies, node count ~unchanged (split out the signed rho term), plus LOEO for anything using a trained model.
  By this calibration t6stk3ff (replay +2.91) predicts ~+2.1 board; its LOEO shrink says ~+0.8. Board decides ~07:00Z.
Lens B (dense autopsy): no lever passed; best (lbm85 track merge) = +0.12 replay, all node-count term -> NO slot.
Verdict: stop dense-movie linking levers; what is left is detection/localisation (+ IMGFLOW family, wf17).

## 09-27 00:05Z: SUBMITTED t6stk3ff = 56592284 and xpubz = 56592302 (09-27 slots 1-2 of 5; 3 left today)
Both GATE_PASS at submit. Scores due ~06:30-07:30Z (waiter task bjy51987c, then rep_check). rep_check NAMES updated.
Decision rules: t6stk3ff -> pick A if it displays >= 0.955 or the representative flips to it at 0.954; if >= 0.955, a
t65s3ff (workflow w7y9sl49t track A) becomes the pick-B / next-slot candidate. xpubz -> pick B only if >= 0.955 (7%
diversity vs t6r70). Remaining 09-27 slots: only arms that pass the evidence standard (pre-registered, replay both
embryos + held-out, LOEO-positive) or are genuinely different tickets - no near-duplicates.

## 09-26 21:30Z: BOX REPLAY COMPLETE (199 train movies x 5 arms) + follow-up workflow w7y9sl49t launched
Full replay (batch1/score_latest.json), pooled dTicks vs t6stk3: t6svT15 -0.88 (board -3), t6svz15 -0.75 (board -2),
t6svz0yx -1.06 (board -7), t6svyx -4.52 (board -6): SIGN RIGHT 4/4, magnitudes compressed 1.3-7x. Use the replay as a
sign screen for post-detection changes (not a magnitude predictor; in-sample detector hides y/x effects).
USER 21:25Z: "keep going autonomously". Follow-ups running (run wf_49586828-fdd, box ~/biohub/wf17, scratchpad/wf17):
A = t65s3ff (IMGFLOW on the pick-B body; replay + LOEO + gate + visible run), B = pre-registered IMGFLOW extensions
(increment >= +0.5, both embryos/halves, LOEO+), C = image-evidence fix for the 'two detections straddle one GT cell'
class (40% of edge loss; kill if separator AUC < 0.75 held-out). The 00:02Z submissions (t6stk3ff, xpubz; task
bakroy1ld) stay scheduled.

## 09-26 21:05Z: IMGFLOW (t6stk3ff) = FIRST LEVER WITH AN UNSEEN-EMBRYO POSITIVE -> GATED, scheduled for 09-27 00:02Z
Alternatives workflow wds71zmt4 (run wf_98f9e0c7-16f) DONE. IMGFLOW = write-time repair after filter_output_graph:
3-D phase correlation of raw frame pairs (8 windows, y/x 2x-binned) -> local tissue flow; ONLY in windows with |f| >= 5 um
and >= 5 detections, edges inconsistent with the flow are re-assigned by Hungarian on flow-compensated distance
(KEEP 3.5 / GATE 4.5 um) + flow-consistent track ends bridged; nodes and forks untouched, no merges (guards: 9.5 h
deadline, invariant checks, per-movie fallback). Motivation (exact replays): frames where annotated tracks move >= 5 um
(2.6% of GT edges) have TP 74% vs 96%; the linker snaps to neighbours (median step 2.3 vs GT 6.4 um).
Evidence: t6stk3 body, 176 train replays +2.91 [+2.33, +3.53] (44b6 +4.49, 6bba +2.59; 76 wins / 6 losses), config fixed
before 54 held-out movies (+3.08 there); nulls negated -0.62 / zero -0.12; **LOEO (6bba-only models on 44b6 = unseen
embryo): +1.15 [+0.40, +2.06], 9 wins / 0 losses** (memorised models +4.11 -> in-sample inflation ~3.6x). Divisions
unchanged everywhere. Visible run GATE_PASS (edges changed 179 / 7 / 7 / 272; +3.80 ticks on the 4 visible movies);
Kaggle flow step 7-10 s/movie (~+30 min hidden). Verifier: SUBMIT-CANDIDATE, central +0.6 tick (-0.5..+1.5),
P(display >= 0.955) ~0.25-0.3. t6r70ff DEAD (6bba -0.03: rawlink already restores those edges in-sample).
Better per-source flow estimator (v2) DEAD (+0.34 tick; even GT flow caps the repair at +1.25 on train).
Files: scratch_kernels/build_t6stk3ff.py, v_t6stk3ff (md5 1467d415), ops/add_t6stk3ff_gate.py (INSTALLED, backup
gate.py.bak_t6stk3ff; negative t6stk3-as-t6stk3ff FAILS, regressions pass), data/out_t6stk3ff, ops/plan_t6stk3ff.json;
analysis scratchpad/wf14/errbudget, box ~/biohub/wf14_alt/errbudget (verify/loeo_ff.*). Diversity vs t6r70 0.94%.
Other ranked ideas: TTT of the edge transformer LATER (EV 0.1), ILP-collapse rescue LATER (never fires on competition-
like data), boundary short-track keep LATER (+0.02), Zebrahub edge fine-tune CLOSED, flow-compensated ILP geometry LATER.
SCHEDULED (task bakroy1ld): at 00:02Z 09-27 submit t6stk3ff then xpubz (--submit-only; ops/run_0927_submit.out).
If the session died, check that file / ops/state/*.SUBMITTED and run by hand. Pick rule: t6stk3ff replaces pick A only
if it reads >= 0.955 or beats t6r70 at full precision (rep_check representative flips).

## 09-26 19:10Z: xpubz GATE ENTRY APPLIED (backup ops/gate.py.bak_xpubz; negatives xpub/ourvzl/t6stk3 logs FAIL under
xpubz, regressions PASS, patterns raw strings) + visible run pushed (--no-submit, task bjkpablkj, ops/run_xpubz.out).
Candidate for a 09-27 slot per the pre-registered ourvzl condition (EV ~0 vs xpub 0.953; its value is a genuinely
different ticket: x138 recall stack + V1284 y/x + our SV z fed to the edge model, ~7% edge diversity vs t6r70).
Submit command once GATE_PASS: `python ops/run_today.py ops/plan_xpubz.json --submit-only`.
19:24Z: xpubz visible run **GATE_PASS**, 0 tracebacks, FINAL 25,705 / 19,790 / 6,184 / 69,835 (xpub: 25,728 / 19,522 /
6,220 / 69,749); match-based edge diversity vs t6r70 6.4% (xpub 7.1%). READY for a 09-27 slot.

## 09-26 18:57Z: t6svT15 = **0.951** (-3). SV-TEMPERATURE FAMILY CLOSED. Do NOT submit t6r70T15.
The skeptic (P(> t6r70) 0.30) and the box replay (-1.7, P 0.09) called it; the tail proxy's "+1" was wrong again
(15th SV-parameter arm to lose). Picks unchanged: A t6r70 56483584, B t65s3 56496604.
Board 18:57Z: rank 243; 0.955 block = ranks 147-202 -> the SILVER LINE (196) IS NOW INSIDE THE 0.955 BLOCK; 0.954 block
203-301; 301 teams above 0.953. Silver on public now needs a high 0.955.
09-26 box/alternatives findings so far (details in the workflow outputs): dense-movie autopsy (wdjiob01y lens B): 40% of
edge loss = our two detections straddle the GT cell ~7.6 um apart (a detection/localisation issue; linking is
geometrically consistent), 26% large one-frame jumps (~7 um vs 1.7) linked to neighbours, 25% missed detections; no
targeted lever passed. Replay bias: relink-over-ILP edges are 9% precise in-sample but t6r70 tied on the board => the
in-sample edge model makes ILP-trusting arms look falsely good. Alternatives ideation: Trackastra NO-GO (91% vs NN
97.7%), external-model family closed, rho calibration closed, merge-tolerant linking negative, boundary short-track
exemption +0.17 tick; PROMISING: IMGFLOW (image phase-correlation flow-compensated re-assignment in high-motion windows,
+2.85 ticks on train sim) and an ILP-collapse rescue (fires on 3/3 Zebrahub daxi crops, 0/116 train) - ranking/prototype
phase running (wds71zmt4).

## 09-26 16:10Z: ourvzl = 0.953 (+2 vs ourvz 0.951) | EXACT-PRODUCTION BOX REPLAY (105 train movies): T15 -1.7 ticks
* ourvzl 56572442 = 0.953: feeding refined z to the edge model on the V1284 body is worth ~+2. Meets the pre-registered
  conditions "reopen edge fine-tune if ourvzl >= ourvz + 0.002" (borderline, display rounding) and "xpubz only if
  ourvzl >= 0.953 and >= ourvz" -> xpubz (x138 body + V1284 y/x + SV z to arr; plan ops/plan_xpubz.json, gate hunks in
  scratchpad/wf8/skeptic_xpubz) is ELIGIBLE for a 09-27 slot (EV ~0 vs xpub 0.953, diversity ~7% vs t6r70).
* BOX REPLAY HARNESS (~/biohub/wf13_proof, survives session restarts; driver batch_run.py pid 2022805, progress
  batch1/progress.log, status: `bash status.sh`, score: `bash score_batch.sh` -> batch1/score_latest.json):
  runs the REAL notebook cells (nbrun.py) per movie; record stage once (detection) then per-arm replay ~30-60 s/movie;
  SELFCHECK replay-vs-record submission IDENTICAL; exact official scorer (score_lib). 105 movies (53 44b6 / 52 6bba):
  | arm | pooled dTicks [90% CI] | edge part | div part | P(d>0) | board |
  | t6svT15 | -1.69 [-4.03, +0.32] | +0.87 (P 0.89) | -2.56 | 0.09 | pending (56578479) |
  | t6svz15 | -0.97 | +0.34 | -1.31 | 0.23 | -2 |
  | t6svz0yx | -0.03 | -1.07 | +1.04 | 0.49 | **-7** |
  | t6svyx | -4.84 | -0.77 | -4.07 | 0.02 | -6 |
  Signs agree 3/3 but the replay MISSES the y/x anchor's size (0 vs -7): in-sample detector -> y/x refinement is
  invisible on train movies. The division part is noisy (pooled div TP 19 / FP 44 / FN 70 on 105 movies, one div TP =
  ~0.75 tick here) and dominates arm differences. T15: edge part mildly positive, divisions worse (FP 44 -> 56).
  Kaggle-environment trainrep kernels (biohub-trainrep-t6stk3 / -t6svT15 COMPLETE, -t6svz15 running; 40 movies):
  scoring via scratchpad/wf13/kaggle/fetch_score.sh -> trainrep_K40.json: T15 vs t6stk3 on 40 movies (Kaggle env,
  exact scorer): +0.25 ticks [95% CI -1.70, +2.44], P(>0) 0.585 (44b6 -1.34, 6bba +0.88; edge +0.91, divJ -0.0066);
  with the 4 visible movies -0.02. TWO INDEPENDENT EXACT REPLAYS AGREE: edge part ~+0.9 tick, divisions ~-0.7..-2.6,
  net ~ -0.5 tick (level). The T family is NOT a proven gain; the board reading decides.
* 16:30Z: workflow wdjiob01y (run wf_035383fd-692): (A) calibrate the box replay against every replayable board-scored
  arm (t6r70, t65s3, t6sr, t6dl, stk3, t60h, ...) -> what change types it can resolve; (B) exact error autopsy of the
  low-scoring DENSE movies (0.66-0.75, many FP edges; dense movies dominate the weighted score) + targeted post-detection
  levers replayed on ~100 movies; skeptic verdict. Box dirs ~/biohub/wf16/<lens>; batch1 is read-only for it.
* Watchers re-armed after the session restart: threat watch bsqeo0znk, t6svT15 score waiter bkwdnvx6r; alternatives
  workflow resumed as wds71zmt4 (same run id wf_98f9e0c7-16f, cached agents reused).

## 09-26 12:15Z: t6r70T15 BUILT + GATE_PASS (not submitted); SKEPTIC puts the T family at P(> t6r70) ~0.30
* scratch_kernels/build_t6r70T.py -> v_t6r70T15 (t6r70 cell 4 == t6stk3 cell 4, md5 92e55d43; only temp line/env/markers
  differ). Gate via ops/add_r70T_gate.py (backup gate.py.bak_t6r70T15; negatives t6r70 + t6svT15 logs FAIL). Visible
  run GATE_PASS, nodes == t6svT15's exactly, rawlink 1,127 accepted; diversity vs t6r70 1.29%. Submit command (DO NOT run
  unless the board rewards T): `python ops/run_today.py ops/plan_t6r70T15.json --submit-only`.
* SKEPTIC (scratchpad/wf13/skeptic): the whole proxy gain = ~19 GT edges (7 fewer >3 um, 12 fewer >2.5 um), 6bba from 3
  movies (one carries 62%); split-half winner shrinks 0.33x; with written-grid y/x rounding S halves and 6bba turns
  worse; **T15 cuts division forks 79 -> 72 on the visible movies (6bba_05db0fb1 25 -> 19, at candidate generation)**
  ~ -0.7..-1.5 ticks via divJ; P(T15 > t6stk3) 0.40, P(display >= 0.955) 0.30, P(> t6r70) 0.30; t6r70T15 > t6r70 ~0.38.
  => If 56578479 reads <= 0.954, the T family is closed (do not spend a slot on t6r70T15). If it reads >= 0.955,
  t6r70T15 becomes a candidate (it stacks T on the representative body).
* Gate bug noted by the builder: sv_mark["ourvzl"] is set after sv_tags is computed, so ourvzl's >= 4 SV-line check never
  ran (ourvzl is already submitted; harmless now).
 "submit this notebook for now" -> t6svT15 SUBMITTED = 56578479 (09-26 slot 5/5, all used)
Honest prior at submission (proxy calibration, entry below): ~level with t6stk3, P(display >= 0.955) ~0.39, P(> t6r70) ~0.43.
Score due ~18:00-19:00Z. Picks unchanged unless it reads >= 0.955 (then it becomes pick A if above t6r70 at full
precision; check rep_check.py representative). Alternatives search running: workflow wx5pp12mq (5 lenses -> ranker ->
up to 3 prototypes -> verify; files scratchpad/wf14, box ~/biohub/wf14_alt).

## 09-26 11:45Z: PROXY CALIBRATION vs 14 BOARD-SCORED SV ARMS (wl31pzc03 agent 1) - t6svT15 NOT PROVEN (~coin flip)
Anchors: t6 body (svyx -6, svz0yx -7, svz15 -2) + hsg200 body (hsz0 -5, hsg050 -6, hsoftfix -2, hsadapt -1, hsg250 -1,
hsg300 -2, hsg400 -2, hsg800 -3, hsg2c10 -1, hsg4c10 -14, hsgzc10 -3). Large effects tracked well (Spearman 0.83, sign
13/14, within-body pairs with >= 2-tick gap ordered 33/34) but on the 8 small anchors (|S| < 0.01, where T15 sits)
Spearman 0.26 [-0.79, 0.92], and 7/8 lost MORE than the linear fit said (mean residual -0.97 tick, t ~ -3.3).
**ALL 14 SV-parameter arms lost on the board; none tied or won** - incl. hsadapt, the only anchor the proxy rated
BETTER (S -0.0010 -> board -1). T15 moves 39% of written y/x voxels (mean |d off| 0.18 um ~ hsg300 size).
Model-averaged (pseudo-BMA) T15 prediction: -0.03 tick, 90% PI [-3.0, +2.9]; P(true > t6stk3) 0.51, P(display >= 0.955)
0.39, P(public > t6r70) 0.43. The earlier "+1 tick" came from the 3-anchor through-origin fit, which LOO shows
under-predicts losses on small perturbations. T ridge is narrow in gain (g1.75/g2.25 halve S). Verdict: NOT substantial.

## 09-26 11:00Z: USER - t6svT15 NOT to be submitted without SUBSTANTIAL PROOF it beats the current best (0.954).
The 00:02Z auto-submit job (bgr6ix99q) was STOPPED. Proof workflows running: wl31pzc03 (proxy calibration against every
board-scored SV arm + LOO prediction; builds/gates t6r70T15 = t6r70 body + T1.5, visible run, no submit) and w2wkuj8e2
(exact-production paired replay on GT train movies on the college box, anchors t6svz15/t6svz0yx/t6svyx as instrument
check, work dir ~/biohub/wf13_proof; plus Kaggle-environment train replay kernels biohub-trainrep-*). Submit only after
the evidence clears the bar AND the user says so.
DaXi (Ultrack unet-daxi.pt, host-lab public U-Net) = NO-GO (workflow w01ewmw6j; files ~/biohub/wf12_daxi, scratchpad/wf12):
fg saturated (AUC 0.51/0.53); contour/segment cues < 0.5 on the hard cases (they restate distance); only patch NCC on
DaXi maps works (0.645/0.710) and it is the August raw-NCC family (+0.15% of edges over raw NCC, n.s.); z estimators
all worse than production SV. Runtime ~0.34 s/frame would also add ~2-5 h to the hidden run.

## 09-26 09:05Z: SCORES ourvz 0.951 | t6svz15 0.952 | t6svz0yx 0.947 -> picks UNCHANGED (A t6r70, B t65s3)
* ourvz 0.951 = ourv: the trilinear y/x V1284 lookup costs ~3 ticks on our body whatever z does -> t6gtri DEAD (same
  gather), ourvz15 DEAD (t6svz15 < 0.955). ourvzl (56572442, due ~13:30Z) is now very likely ~0.951 too.
* t6svz0yx 0.947: SV y/x is worth +7 ticks (SV z +6, t6svyx 0.948). Both axes of the sub-voxel step are essential.
* t6svz15 0.952: z gain 3 loses 2 ticks, exactly the direction the production-logit proxy predicted (g2.5 worse).
PROXY CALIBRATION (scratchpad/an/yx/yxstudy.py, production logits, 60 movies, prod reproduced to 1.5e-7): with
S = pooled delta(>3 um) + pooled delta(>2.5 um): z=0 +0.0231 -> -6 board ticks; yx=0 +0.0222 -> -7; z g3 +0.0034 -> -2.
~0.0017-0.0035 per tick, right sign 3/3. (The >3 um tail alone under-reads the y/x channel: yx=0 is only +0.0077.)
t6svT15 (all-axes T1.5 g2): S = -0.0028 (P(better @3um) 0.84 / 1.00) -> predicted +1 (0.8-1.6) tick. Best joint arm in the
grid: z T1 g1.5 | yx T1.5 g2 S = -0.0036 (P 0.95/1.00) - same mechanism, within grid-search selection noise of t6svT15,
so t6svT15 stays the one ticket for this family (pre-registered; no near-duplicate). y/x gain alone (T1) is flat (g1-3).
09-27 PLAN: slot 1 t6svT15 (gated, ready). xpubz only if ourvzl >= 0.953 (unlikely now). t6gtri/t6gtriz dropped.
SCHEDULED: background job bgr6ix99q submits t6svT15 at 00:02Z 09-27 (`--submit-only`, log ops/run_t6svT15_submit.out).
If the session restarted, check that file / ops/state/t6svT15.SUBMITTED and run the command by hand if it is missing.

## 09-26 08:40Z: t6svT15 visible run GATE_PASS (READY for a 09-27 slot: `python ops/run_today.py ops/plan_t6svT15.json --submit-only`)
0 tracebacks, ARM_SVTEMP T=1.5 gain=2.00; FINAL nodes 25,634 / 20,668 / 6,159 / 70,322 (NO 44b6_0b24845f node cut:
t6stk3 20,687; the trilinear-gather arms cut it to ~18.5-18.8k). Match-based edge diversity vs t6r70 = 2.13% (t6stk3 1.00%,
t65s3 1.9%). Rank 08:25Z: 207 (0.954 block = 172-258, 0.955 = 126-171, silver line 196, 258 teams above 0.953).
DaXi study (host-lab Ultrack U-Net on the box, cross-embryo boundary/foreground cue for the crowded-region mislinks)
running as workflow w01ewmw6j; prior low (Aug image-NCC cue was real but addressable cases rare, +0.001 CV).

## 09-26 09:00Z: EDGE-MODEL FINE-TUNE (college V100) = NO-GO (workflow wpp3vqam9; notes scratchpad/wf11)
Audit: the edge model (transformer.*, 580k params; UNet 1.5M + detect_head 33, cleanly separable; checkpoint = flat
state_dict, overlay of transformer.* is a clean swap) trains on ITS OWN integer detection peaks (logit > 0.3, 5 um pool),
never GT; the GT//4 floor (train_unet_transformer.py:562-564) is only the detector target. Real train/inference gaps:
integer vs refined coords, single-pass vs 8-view-TTA features, logit>0.3 vs sigmoid>0.965 blended detections, reverse
pass never trained, BatchNorm batch vs running stats. Primary 50ep weights ARE on the box
(~/biohub/weights_primary50ep/split_0, sha 12f6881e matches the kernel pin); box env ~/biohub/.venv.
SKEPTIC (measured, production detections + production SV offsets, logitcap): nearest-source pick is right 96.3% (44b6)
/ 97.0% (6bba) of GT edges with integer coords; SV coords change the pick on 0.86% of 44b6 edges (0.55% fixed, 0.31%
broken) = net +0.24% of GT edges (CI -0.05..+0.57), 6bba +0.07% -> geometry headroom via the edge model <= ~1 tick.
lcefr alone tied on the board twice (hsg200, x138 body); the old learned edge model: +0.02-0.04 CV -> +0.000 LB;
LOEO calib0922 never calibrated for edge arms (37/39 holds only for SV gain arms, board_style metric); an edge-only
change already caused a node cut on 44b6_0b24845f (t6gtri -9.2%) like the V1284 arms that lost. Prior >= 3 ticks 2-4%.
REOPEN ONLY IF ourvzl >= ourvz + 0.002 on the board (the clean edge-input-z pair; ourvzl due ~13:30Z).
Remaining GPU ideas considered and not pursued: TTA-feature alignment fine-tune (same learned-part transfer risk).

## 09-26 08:30Z: SV SOFTMAX TEMPERATURE = most robust offline gain found today; t6svT15 built + gated + running
Production-logit tail study (T x gain grid, 400-rep movie bootstrap): a ridge at T 1.25-2.0 with gain 2-2.5 improves the
>3 um tail on BOTH embryos (production T1 g2: 0.0114/0.0070). T1.5 g2: 0.0105/0.0059 (P(better) 0.86 / 1.00; also
better at 2.5 um -0.0017 and 3.5 um -0.0003). T1.25 g2: same numbers (0.85 / 0.96). T2.0 g2.5: 0.0105/0.0052 (0.83/1.00).
Gain alone (T1): 1.5 is best (-0.0002/-0.0007), 2.5+ worse. Size ~0.5 tick (slope ~4 ticks/pp on production logits):
sub-resolution but the most consistent offline improvement today.
Built `scratch_kernels/build_t6svT.py <tag> <T> <gain>` (logits/T before the production softmax; T=1 reproduces
t6stk3; unit test vs reference formula max err 5e-8). `ops/add_svT_gate.py` writes gate+plan with auto negative test
(t6stk3 log FAILS; regressions pass). t6svT15 (T1.5 g2) visible run pushed 08:00Z (ops/run_t6svT15.out). Candidate
for a 09-27 slot (lottery ticket). USER (08:20Z): the college V100 box is AUTHORIZED for CPU+GPU work - do not
disturb the user's own jobs (rsna / ltx-v100 / fs). Edge-model fine-tune design workflow (wpp3vqam9) running.

## 09-26 08:10Z: Z-ESTIMATOR STUDY ON PRODUCTION LOGITS (v_logitcap, 60 movies) - PRODUCTION SV z IS ~OPTIMAL
scratchpad/an/zstudy.py on data/out_logitcap/logitcap (fixed: materialise npz arrays once; 3 s runtime). All 31,875
pairs / 6,896 GT edges joined; recomputed SV27 g2 == production z to 1.5e-7. Tail > 3 um (44b6 / 6bba), y/x = production:
production SV z g2 (t6stk3) 0.0114 / 0.0070 | zero z 0.0217 / 0.0278 (the 6-tick channel, reconfirmed) |
SV27 g1.0 .0114/.0089 | **g1.5 .0112/.0056 (-0.0002/-0.0015, ~0.5 tick)** | g2.5 .0126/.0078 (worse: t6svz15 at g3
should lose) | T0.5 .0121/.0085 | T2.0 = prod | line3/5/7 .0117-.0160 / .0122-.0163 (worse) | box5 g1 .0098/.0074
(mixed) | box7 .0114-.0145 / .0085-.0115 | parabolic .0114-.0131 / .0119-.0130 | sigmoid-COM5 .0126-.0143 / .0156-.0178.
Production logits give a much lower tail than the primary-only proxy (0.0114/0.0070 vs 0.0169/0.0163), and the
ranking is clearer. VERDICT: the z lever is fully mapped - its ~6 ticks are real and already in our body; no z
estimator beats production by a board-readable margin (best: z gain 1.5, ~0.5 tick). No z-estimator arm queued
(t6svz075 = build_t6svax --z 0.75 --yx 1 is the only candidate, a sub-resolution lottery ticket).

## 09-26 08:00Z: FULL RE-SWEEP (user request: "clustering" on the board) - nothing public explains the jumps
* Forum (sorted by recent comments): no thread newer than 743222 (1 d). Read 743146 (rules question on third-party
  pretrained weights, no content) and 741386 (external zebrafish data): #1 Sergio Alvarez confirms the public
  Ultrack/Zebrahub embryo is a DIFFERENT embryo with the same spacing and external data is allowed - top teams can
  validate on truly unseen embryos. We already built a Zebrahub proxy (HANDOFF) and it was WRONG-SIGNED 3/3 on board.
* New datasets 09-25/26: koushikrudra/biohub-zerogpu-consensus-v1 (a precomputed submission.csv - useless on the
  hidden rerun and on our never-do list), kabirk22/biohub2 (36 GB normalized train tensors), fagbolapeter/
  biohub-trained-4ep (4-epoch model val graphs), sub-cache/leaderboard-intelligence sets. No new weights/heads.
* Notebooks: none created after 09-24; andrey4522 v3-raunak and y3uanm notebooks show NO public score (never
  submitted); tobimichigan 0.097. Top public by score still 0.953.
=> The 1-3-submission jumpers to 0.955-0.963 use something shared privately (likely the competition Discord).
   Nothing to port.

## 09-26 07:45Z: USER DIRECTIVE - DO NOT USE TODAY'S LAST SLOT (09-26 slot 5 stays unused). Keep researching.

## 09-26 07:40Z: t6gtri visible run GATE_PASS - but it shares the "V1284 node cut", so slot 5 WAITS for ourvz
07:35Z: rank 200, BELOW the public silver line (196); 253 teams above 0.953. (watch now logs rank alerts to
ops/watch/lb_alerts.log instead of exiting; author-code alerts still exit.)
t6gtri: 0 tracebacks, ARM_GTRI_STATS nodes = 2 x lcefr (four gathers), feature delta 0.064-0.092; nodes 25,561 /
18,783 / 6,033 / 69,257 = 119,634 (-2.6% vs t6stk3); edge diff vs t6r70 3.65% (match-based).
KEY OBSERVATION: every arm with a trilinear y/x feature lookup at refined coordinates cuts 44b6_0b24845f to ~18.5-18.8k
(ourv 18,509, ourvz 18,692, ourvzl 18,826, t6gtri 18,783; t6stk3 20,687). The common factor is the TRILINEAR GATHER,
not the V1284 head. ourv lost 3 ticks; if ourvz (trilinear y/x, SV z) also lands ~0.951, the gather is the likely
culprit and t6gtri would lose too. => slot 5 decision waits for ourvz's score (~09:00Z):
ourvz >= 0.953 -> t6gtri is a fair shot (submit); ourvz <= 0.952 -> skip t6gtri, use slot 5 on a z-estimator winner
(if any) or t6gtriz (z-only gather, no y/x trilinear).

## !!! 09-26 07:05Z: WE ARE AT THE SILVER LINE. ourvzl SUBMITTED (slot 4/5). t6gtri gated + visible run pushed. !!!
rep_check 07:03Z: rank **194**, silver line 195 (of 3,919 ranked); 0.954 block = ranks 166-248 (83 teams); 0.955 =
121-165; 248 teams above 0.953 (+15 in one hour). A displayed 0.955 is what escapes the block.
POLICY CHANGE: slots are no longer scarce relative to the rank emergency (1 left today, 5/day after) and picks are
chosen afterwards, so every slot now goes to a GENUINELY DIFFERENT arm with any real P(>=0.955) (still no
near-duplicate LB probing). Holding is no longer the default.
* ourvzl submitted 07:03Z (did not wait for ourvz's score; the audit put P(>=0.955) ~0.08, P(>=0.954) ~0.25).
* t6gtri gate entry APPLIED (from wf8/geometry/gtri/gate_entry_t6gtri.txt, sv_mark put inside the literal): negative
  t6stk3 log FAILS, synthetic good log PASSES, all 9 mutant logs FAIL for the right reason, regressions ourvz/ourvzl/
  t6svz15/t6svz0yx/t6stk3/ourv all PASS. Visible run pushed 07:05Z (ops/run_t6gtri.out). Candidate for slot 5 today
  unless the z-estimator study (logitcap ~07:40Z) produces a stronger arm first.
* Native-resolution centroids closed (entry below).

## 09-26 07:00Z: NATIVE-RESOLUTION CENTROIDS = CLOSED (v_nativecen, data/out_nativecen)
PROXY_REPRO ALL_OK=True (reproduces the proxy exactly). all60 set (44b6 21 movies / 6bba 39 movies, not just 3):
t6stk3 tail3 0.0169 / 0.0141 is the TOP arm; every native variant is worse: best B4z2z|yxSV (native z over +-2
slices, SV y/x) d3 +0.0007 [-0.0006,+0.0020]; A8|zSV (native y/x) +0.0040; iterative/Gaussian y/x much worse
(fallback up to 9%). The proxy24 "6bba gain" of native z (0.0130 vs 0.0163 on 3 movies) vanished on 39 movies
(winner's curse, caught offline). Production SV (logit soft-argmax, gain 2) is at least as good as every image-based
refinement tried. Native mapping confirmed: native = grid x (1,4,4), no +1.5 offset (yx MAE lowest at offset 0).
Remaining z research: the production-logit z-estimator study (v_logitcap, landing ~07:40Z).

## 09-26 06:35Z: z-estimator arm PIPELINE (three commands + one ~30 min run)
1. `python scratch_kernels/build_t6svzest.py <tag> <est> <gain>`
2. `python ops/add_svzest_gate.py <tag> <est> <gain> "<desc>"` (writes gate entry + plan; auto negative-test:
   t6stk3 log must FAIL under the tag; tested and gate.py restored after the test)
3. `python ops/run_today.py ops/plan_<tag>.json --no-submit` -> `bash ops/getlog.sh <tag> 8` ->
   `python ops/gate.py data/out_<tag>/*.log <tag>` -> `python ops/run_today.py ops/plan_<tag>.json --submit-only`

## 09-26 06:45Z: GEOMETRY-PRECISION AUDIT (wl2svnq1x) - three arms built, none passed a value skeptic
Predictions (body x head lens: the predictor output does not depend on the body, the 5-tick interaction is all
post-processing): ourvz 0.951 (0.950-0.953, P>=0.954 ~0.12; keeps ~90% of V1284's edge-model damage: raw edge_prob
0.8615 vs t6stk3 0.8792); ourvzl 0.952 (0.950-0.955, P>=0.954 ~0.25, P>=0.955 ~0.08; confound: its visible run fired
the short-track rescue on 44b6_0b24845f).
Built (correct: byte-identical rebuilds, anchors once, mutants raise), NOT gated, NOT pushed; SP = scratchpad/wf8:
1. xpubz (x138 body + V1284 y/x + SV z fed to arr; plan ops/plan_xpubz.json). Gate: apply the hunks of
   `diff ops/gate.py SP/skeptic_xpubz/gate/gate_x_svlit.py` (sv_mark INSIDE the literal at ~:1492, not after 1524).
   Condition: only if ourvzl >= 0.953 AND ourvzl >= ourvz. EV ~0 vs xpub. Diversity vs t6r70 ~7%.
2. t6gtri (trilinear UNet gather at lcefr coords, all axes; plan ops/plan_t6gtri.json). Gate from
   SP/geometry/gtri/gate_entry_t6gtri.txt with sv_mark moved into the literal + FINAL +-3% band. Filler only. EV 0.
3. t6gtriz (same, z only; plan ops/plan_t6gtriz.json). Gate: hunks of `diff ops/gate.py SP/geometry/gate_with_t6gtriz.py`.
   Use instead of t6gtri, only if ourvzl <= 0.951. EV 0.
Dead: t6dcsv (DeepCenter sub-voxel lookup: ~5-10 decision flips, 0 ticks); t6xwin (research only).
PRIORITY for 09-27: a t6svzest winner (if the logitcap study beats SV z beyond resolution on BOTH embryos) >
ourvz15 (decide_0926 condition) > xpubz (condition) > t6gtri/t6gtriz (filler).

## 09-26 06:10Z: ARM FACTORY for the winning z estimator + native-centroid notebook PUSHED
* `scratch_kernels/build_t6svzest.py <tag> <estimator> <gain>` (base v_t6stk3, lcefr kept, y/x production SV):
  estimators line3/5/7, box5/7, parabolic, sigcom5, sv27T<T>, identical to zstudy.py (unit test: max |kernel -
  study| = 0.0 for every estimator; y/x bit-identical to production). Markers: ARM_XENV tag=<tag> SVZEST=<est>
  ZGAIN=<g> LCEFR=kept and ARM_SVZEST est=<est> gain=<g>. Needs a gate entry + plan when used.
* v_nativecen (CPU-only, no GPU quota) PUSHED 05:43Z: native-resolution intensity centroids (18 variants, 2-D y/x and
  3-D incl. z, iterative, Gaussian-weighted) vs zero/SV on the tail metric; all 60 movies have GT geffs on Kaggle
  (6bba grows from 3 to 39 movies); outputs nativecen_table.csv / summary.json / shifts.npz -> data/out_nativecen.
  Caveats from the verifiers: PROXY_REPRO sha flags can read False harmlessly (GT row order); confirm any winner
  on the 36 6bba movies the proxy never saw (winner's curse); its SV reference is the proxy's primary-only 1-D SV,
  not production; one real cell showed native z-intensity peaking ~2 slices below GT z (possible z bias).
* The kernel's native-resolution reads: the pipeline reads frames with stride [t, ::1, ::4, ::4]; a native-centroid
  arm would need a full-resolution frame read per t (~8 MB) - feasible but a real build.

## 09-26 06:00Z: z-estimator study READY (scratchpad/an/zstudy.py; run after logitcap lands)
`python scratchpad/an/zstudy.py` (env LOGITCAP_DIR overrides the input dir). Joins logitcap rows to the proxy's GT
pairs by (stem,t,z,y,x), keeps production y/x SV, swaps only z; ~20 estimators: SV27 gains 1-2.5 and temperatures,
1-D line soft-argmax over 3/5/7 slices, 3x3-summed box soft-argmax over 5/7 slices, parabolic fit, sigmoid COM5;
tail > 2.5/3/3.5 um per embryo vs production. Smoke-tested on synthetic windows: runs end to end; SV27 g2 reproduces
production z to 1.5e-8 on non-edge rows (edge rows follow the production zeroing rule, which the real `sv` has).

## 09-26 05:40Z: v_logitcap PUSHED (production logit windows for 60 train movies; ~2 h; no slot)
scratch_kernels/build_logitcap.py -> v_logitcap. Per movie /kaggle/working/logitcap/<stem>.npz: coords int16 (n,4)
feature grid, win float32 (n,7,3,3) BLENDED/guard-fallback detection logits (edge-padded), peak, sv (exact production
SV offsets), use_primary, per-frame guard stats. Skeptic 1 proved bit-for-bit equality with the t6stk3 predictor's
tensor and SV; its only blocker (float16 windows) was fixed by switching to float32 (all dtype self-checks now exact).
Skeptic 2: safe to push. Join to GT/V1284 features via data/out_v1284cap/v1284cap_candidates.npz by (stem,t,z,y,x).
Known minor: a flush exception kills the whole shard (low risk). Background fetch -> data/out_logitcap.
NEXT when it lands: offline z-estimator study (5/7-slice soft-argmax, Gaussian/parabolic fits, gains, robust
estimators) on the >3 um displacement-tail proxy, per embryo; build the winner only if it beats SV z beyond the
proxy's resolution on BOTH embryos.

## 09-26 05:25Z: leaderboard forensics - private recipes circulating, nothing public above 0.953
155 teams >= 0.955; 134 of them submitted 09-25/26. 14 are "fork-like jumpers" (<= 15 total submissions), e.g.
Tiagomgfernandes 0.956 with ONE submission, Rio 0.958 with 3, William Zhao 0.956 with 3, Ascent 0.963 with 12.
Public notebooks by score: raunak v3 0.953, amanatar optimized-biohub-max-score best 0.953 (V4; current version
errors), kunaldesale 0.953, anvithpothula x138 renamed "biohub-0-953-lb-original". => whatever lifts teams to
0.955+ is not public; nothing to port.

## 09-26 05:15Z (clock-corrected): INSTRUMENT UPGRADE IN BUILD - production logit-window capture (workflow wy315b67e)
v_logitcap (from v_v1284cap): saves, per train detection, the BLENDED retention-guarded detection-logit window the
production SV helper reads, 7 slices in z x 3 x 3 (float16), for the same 60 movies. Lets us test z estimators
offline on production-exact inputs (5/7-slice soft-argmax, Gaussian/parabolic fits, lower gains, robust
estimators) against the tail proxy, where a perfect z would cut t6stk3's tail ~4x. GPU run ~2 h (weekly quota
reset today), no slot. Push after both skeptics pass. (Timestamps in the entries just above were estimates; the
real clock was ~2 h earlier.)

## 09-26 07:00Z: z-estimator blends on the proxy (y/x = SV gain 2; tail > 3 um, 44b6 / 6bba)
zero .0238/.0293 | SV z2 (t6stk3) .0169/.0163 | V1284 z .0164/.0189 | **0.5 SV + 0.5 V1284 .0150/.0159** |
0.7 SV + 0.3 V1284 .0160/.0152 | SV z1.5 .0162/.0163. Both blends beat t6stk3 on both embryos but by 0.04-0.19 pp
(~0.3-1.2 ticks), below the proxy's ~2-tick resolution, and V1284 arms carry the body-x-head caveat. Low-priority
lottery ticket "t6zbl" (t6 body, lcefr kept, y/x SV, z = 0.5 SV + 0.5 V1284 head z) - build only if a slot is idle
AND ourvz/ourvzl show V1284 is not toxic on this body.

## 09-26 06:50Z: t6stk3's REMAINING displacement tail is still mostly Z (proxy, GT edges > 3 um)
44b6: 71 tail edges of 4,199 (0.0169); z-dominated 58%; tail if y/x perfect 0.0067, if z perfect 0.0043.
6bba: 44 of 2,697 (0.0163); z-dominated 89%; tail if y/x perfect 0.0100, if z perfect 0.0015.
=> The largest remaining room is a better Z ESTIMATE (the 3-point logit soft-argmax overshoots: mean |z err| worse
than zero shift). Candidate: intensity-weighted native z centroid over +-1..2 slices (included as variant (b) in the
v_nativecen test). If it cuts the z tail on both embryos, build it as the SV-z replacement on the t6 body.

## 09-26 06:40Z: NEW LEVER FAMILY UNDER TEST - native-resolution intensity centroids (workflow wwnu2aodi)
Detections sit on a grid 4x coarser than the image in y/x (1.625 vs 0.406 um), so y/x can jump a whole grid step
between frames exactly like integer z did. An intensity-weighted centroid on the NATIVE image around each detection
is 4x finer and deterministic (should transfer to unseen embryos). Test: CPU-only Kaggle notebook v_nativecen
(no GPU quota) reading train zarrs + the v1284cap capture, measuring the >3 um displacement tail vs SV per embryo.
Build it into the kernel ONLY if the tail drops beyond the proxy's resolution (~0.3 pp, ~2 ticks) on BOTH embryos.
Running in parallel: geometry-precision audit (wl2svnq1x: DeepCenter lookups at rounded coords etc.).

## 09-26 06:30Z: `ops/decide_0926.py` - run it the moment today's 3 scores land (read-only)
Applies the slot-4 rule (ourvzl), the ourvz15 condition and the pick-B rule (match-based diversity), prints exact
commands. Dry-run tested on 4 outcome combinations; live run says "NOT ALL SCORED YET" until all three complete.

## 09-26 06:20Z: retention-guard source SWITCHING checked (tail hypothesis) - weak, no arm
44b6_0b24845f: 64/100 frames primary-only, 22 blended<->primary switches between consecutive frames (pattern
PPPPPPPPPPPPPPPbbbbbPPPbPbPPbbbbPPbbbbbbbbbbbbbPbbPPbPPbbbPPPPPbPPPbbbPbbPPPP...). At switch transitions (t6stk3
visible output): track ends/node 0.0616 vs 0.0593 non-switch, starts at t+1 0.0581 vs 0.0502 (+16%), edges > 3 um
0.098 vs 0.146 (FEWER). Switches cluster mid-movie (confound). A movie-level fallback / hysteresis would touch only
low-agreement movies with a small per-transition effect: not worth a slot.

## 09-26 06:10Z: THE Z MECHANISM, MEASURED: SV z CUTS THE DISPLACEMENT-ERROR *TAIL*, NOT THE MEAN
On the capture proxy (scratchpad/wf7/calib/cache.npz, 31,875 matched detections / 6,896 GT edges):
* Per-detection mean |z error| gets WORSE with SV z (44b6: zero 0.754, g1 0.813, g2 0.870, g3 0.904; 6bba: 0.887 /
  0.903 / 0.942 / 0.971 um); V1284 z ~= zero (0.762 / 0.911) - V1284 z correlates with the true residual (+0.50 /
  +0.26) but overshoots.
* Mean z DISPLACEMENT error per GT edge also worse (0.663 -> 0.723 um on 44b6), BUT the share of GT edges with a 3-D
  displacement error > 3 um drops sharply: 44b6 0.0238 -> 0.0169, 6bba 0.0293 -> 0.0163 (t6svyx -> t6stk3).
  Integer z makes a cell jump a whole slice (1.6 um) when it drifts across a boundary; those rare jumps break links
  against the um gates (TIGHT 6.0 etc.). The board rewards cutting jump-tails, not average accuracy.
* Tail table (>3 um, 44b6 / 6bba): zero .0279/.0311 | t6svyx .0238/.0293 (.948) | t6stk3 .0169/.0163 (.954) |
  t6svz15 .0188/.0197 | t6svz0yx .0229/.0260 | ourv .0160/.0197 (.951) | ourvz .0152/.0208. Predicts t6svz0yx and
  t6svz15 below t6stk3; ourvz mixed by embryo.
* Pre-relink temporal smoothing (ORACLE: smoothing along true GT tracks): w=0.15 -> tail .0155/.0145 (~ +1 tick at
  best, oracle), w>=0.25 much worse. No better than the existing post-link line-fit (+-1 tick). DEAD END.

## 09-26 05:40Z: public notebook check - raunakdey07/biohub-harmonic-fusion-v3 v5 (re-run 09-25 09:09) = 0.953
Mounts biohub-v1284-head-s075; code diff vs x138 = comments/blank lines only (scratch_kernels/_pub0926/raunak). Another
x138 copy feeding the 0.953 block. No new public notebook above 0.953.

## 09-26 05:25Z: two dead ends checked while waiting
* Placeholder GT rates t6svyx ABOVE t6stk3 (weighted J 0.9591 vs 0.9572) - the board put it 6 ticks BELOW. The
  placeholders cannot see even a 6-tick effect (in-sample detectors). Never use them for anything.
* Division count vs board over 33 scored arms: Pearson -0.09 (no lever). The t6-only -0.82 is t6svyx alone (89 vs
  79 divisions). What else moved with z off: DeepCenter gap accepts 19 -> 11, geometric division candidates
  627 -> 649 -> the DeepCenter / geometry stages are where the geometry-precision workflow (wl2svnq1x) is looking.

## 09-26 05:15Z: MATCH-BASED DIVERSITY vs pick A (t6r70) + pick-B rule (scratchpad/an/matchdiff.py)
Per-frame Hungarian node matching (<= 3 um), edge survival both directions: t6stk3 1.0% | t6sr 1.1% | t6svz15 1.6% |
**t65s3 1.9%** (current B) | t6svz0yx 4.4% | ourvzl 4.9% | ourvz 5.2% | ourv 6.0% | xpub 7.1%. Ratios match the old
binned measure, so the wf3 Monte Carlo (corr r70-ourv 0.58, r70-s3 0.847) still applies. At ~230 teams above 0.953,
sigma 0.0015: {t6r70,t65s3} P(silver) 0.58 | {t6r70, V1284-family@0.954} 0.67 | @0.955 0.84 | @0.956 0.96.
**PICK-B RULE (updated): any of ourvz / ourvzl / t6svz0yx reading >= 0.954 replaces t65s3 as pick B** (highest score
first, then most diverse). A reading >= 0.955 on ANY arm: it becomes pick B, and pick A too if the leaderboard's
representative submission flips to it (rep_check.py).

## 09-26 05:00Z: PROXY SCREEN (w38oftkbq) - NO VARIANT BEATS t6stk3 BEYOND THE PROXY'S RESOLUTION
Calibration (scratchpad/wf7/calib): the metric is the fraction of GT EDGES with 3-D displacement error > 3 um (not
per detection). The quoted r=-0.94 was driven by the hsg4c10 outlier; on 11 clean hsg points r ~ -0.70..-0.85, LOO
error ~1.3-1.4 ticks: the proxy rejects >= 2-tick losers, it cannot find 1-tick wins. Proxy y/x offsets are 16-20%
larger than production's (z within 3%). The z channel is worth ~2x more on the t6 body than the hsg slope predicts
(lcefr). V1284 arms cannot be calibrated (5-tick body x head interaction: +2 on x138, -3 on t6). hsg400 = 0.949
(not 0.948; old note wrong). GT coordinates sit on the integer lattice.
Screen (scratchpad/wf7/screen, ~40 variants, both embryos): best gain pair = z1.5/yx2 (+0.3..0.5 tick = noise);
z3 (t6svz15) -0.9..-1.6 ticks; y/x 0 (t6svz0yx) -3..-4 ticks; every V1284 variant splits by embryo (better 44b6,
worse 6bba). Only "winner": z clip 0.40 (built: scratch_kernels/build_t6svzc.py -> v_t6svzc40, NO gate/plan) -
skeptic showed it is a z-grid threshold artifact (changes 9 of 6,896 edges, each nudged from ~3.1 to <3.0 um), mean
refined-z change 0.066 um, far below any board-readable effect. Verdict: do not spend a slot on proxy winners; follow
the decision table (ourvzl if ourvz >= 0.952, or = 0.951 with t6svz0yx >= 0.952). t6svzc40 = spare filler only if
t6svz15 <= 0.953 and t6svz0yx <= 0.951 and a slot is otherwise unused.

## 09-26 04:05Z: ourvzl visible run GATE_PASS (ready: `python ops/run_today.py ops/plan_ourvzl.json --submit-only`)
ARM_SV_Z_TO_ARR frames=100 on every movie, final_z_add=0, gather_int_z=1, z_mean 0.312-0.336 (= ourvz), 0 tracebacks.
FINAL 25,616 / 18,826 / 6,075 / 69,175 (ourvz 25,614 / 18,692 / 6,098 / 69,151): the edge model now sees refined z and
the ILP keeps slightly different nodes, as intended. Awaiting ourvz/t6svz15/t6svz0yx scores for the decision table.

## 09-26 04:00Z: Z-LEVER WORKFLOW (w70gu2flo) - CORRECTIONS + AN OFFLINE INSTRUMENT THAT TRACKS THE BOARD
CORRECTIONS to entries below: (a) SV z DOES reach written z via line-fit smoothing (t6stk3 vs t6svyx differ on 19.8%
of written z, 97% of those +-1 slice) but that written channel is worth <= 0.3 tick; the 6 ticks are which links/
nodes get selected (~600 edges swapped, ILP edge_prob via lcefr, um gates tuned on refined geometry). (b) ourv DID
move z: the ourv module applies `result[:,1:] += shift` with no z zeroing (mean |z| 0.37 voxel, written z changed on
29% of nodes); the public head moves z without making it more accurate. (c) ourvz expectation revised to ~0.951
(0.949-0.952), not 0.953-0.954.
OFFLINE PROXY: detect_head is a 1x1 conv (train_unet_transformer.py:437) and the primary50ep checkpoint sha matches
the kernel -> exact primary TTA logits at the 7 captured points = w.f + b on v1284cap features. 1-D z soft-argmax on
primary logits reproduces production magnitudes (z |off| 0.328, 36% clipped vs 0.31-0.34 / 32-41% in logs).
**The fraction of matched detections displaced > 3 um tracks the old board gain curve (Pearson -0.94); RMSE does
not.** Table (31,875 GT matches, 24 movies): z gain 0 -> >3um 0.0260 (board 0.948, t6svyx) | 1.0 0.0168 | 1.5 0.0162 |
2.0 0.0167 (board 0.954) | 3.0 0.0191 | 4.0 0.0209. Predictions: t6svz15 0.952-0.953, t6svz0yx 0.948-0.950, ourvz
~0.951. Scripts: scratchpad/wf6/zacc/ (proxy) + zdose/ + floatz/.
DECISION TABLE for 09-26 slots 4-5 (after scores): ourvz >= 0.952 -> submit ourvzl; ourvz = 0.951 -> ourvzl only if
t6svz0yx >= 0.952; ourvz <= 0.950 -> hold. t6svz15 >= 0.955 & ourvz >= 0.954 -> ourvz15 (needs gate+plan). t6svz05
and t6svx125 REFUTED (t6svz05's gate regex also wrong: requires z_mean_abs 0.0xxx, a correct run is ~0.20).
Ideas killed: constant z bias (GT sits +0.34 slice above detections, but it cancels in displacements), z-only
line-fit, writer z bias, relink z weight (0/3,549 edges changed at 0.75), GAP_REFINE_WIN_Z, DEEPCENTER_SCORE_WIN_Z.
NEXT (in progress): screen a grid of localization variants with the proxy to find one predicted to beat t6stk3.

## 09-26 03:30Z: `ourvzl` BUILT + VERIFIED + visible run pushed (scratch_kernels/build_ourvzl.py, workflow wpr16kq6i)
Trace (real ourvz predictor): in ourvz the EDGE MODEL sees INTEGER z everywhere (pos embedding, predict_edges
forward/reverse/secondary geometry, trilinear V1284 gather, edge dist); refined z only reaches the output coords
(geff nodes -> cell-5 post-processing, DeepCenter windows, writer). The ILP uses only edge_prob (no coordinates).
In t6stk3, lcefr fed SV-refined coords (all axes) to pos features, predict_edges geometry and edge dist, while the
UNet gather stayed at the integer peak. ourvzl = ourvz + SV z added to arr right AFTER V1284 (so V1284's
sample_features still sees the integer peak), final assembly skips the z add (exactly-once assertion; mutants
"z twice" and "z skipped" both raise), V1284 trilinear gather rounds z (GATHER_INT_Z=1, lcefr analogue). Final
node coords are bitwise ourvz's. Two skeptics: ok. Gate entry added (pins SV_ARM_HSG200 to ourvz's exact values,
ARM_SV_Z_TO_ARR per-movie lines, forbids Traceback); negative tests: ourvz and t6stk3 logs FAIL as ourvzl;
regression ourvz/t6svz15/t6svz0yx/ourv still PASS. Known ~0 risk: a NO-OP guard raises if a movie has detections
but every z offset is exactly 0 (practically impossible). Plan: ops/plan_ourvzl.json. Visible run pushed 03:30Z.
USE: if ourvz scores low (~0.951-0.952) the z value lives in the edge model -> ourvzl is the fix. If ourvz >= 0.955,
ourvzl is the natural "both paths" follow-up.

## 09-26 03:10Z: SLOTS 2+3 SUBMITTED - the z-dose pair (scores ~09:30-10:00Z)
Submission ids 09-26: ourvz 56567062 (02:32Z), t6svz15 56567638 (03:07Z), t6svz0yx 56567694 (03:10Z).
* t6svz15 (t6stk3, z gain 3.0, y/x 2.0): GATE_PASS; z_mean_abs 0.364-0.382 voxel (gain 2 was ~0.31-0.34), FINAL
  25,616 / 20,711 / 6,152 / 70,367; submitted 03:07Z.
* t6svz0yx (t6stk3, SV z only at gain 2, y/x zeroed): GATE_PASS; yx_mean_abs 0.0000, z 0.312-0.336, FINAL 25,579 /
  20,664 / 6,154 / 70,330; submitted ~03:10Z.
With t6stk3 (z+y/x, 0.954) and t6svyx (y/x only, 0.948) this completes a 2x2 on the t6 body: z on/off x y/x on/off,
plus the z-dose point. Remaining today: 2 slots, decided by ourvz / t6svz15 / t6svz0yx + the z-lever workflow.

## 09-26 02:50Z: SILVER LINE NOW INSIDE THE 0.954 BLOCK. TARGET FOR EVERY SLOT = 0.955.
rep_check: 0.957 ranks 74-89 (16) | 0.956 90-113 (24) | 0.955 114-154 (41) | **0.954 155-227 (73; us rank 175)** |
0.953 228-527 (300). Silver = rank 195 of 3,918 ranked; bronze = 391. We are 20 ranks above the silver line, inside
a 73-team display block whose private order is noise. A displayed 0.955 = rank <= 154 = safe silver on public.

## 09-26 03:00Z: ourvz expectation (stated to user) + ourvz15 pre-built
ourvz central 0.953-0.954, P(>=0.955) ~0.30, floor ~0.951. Key uncertainty: in t6stk3 the SV-refined z also feeds the
EDGE MODEL (lcefr); in ourvz the SV z offsets reach only the output coordinates (post-processing), because V1284's
trilinear _index_features replaces the lcefr path and sees integer z. If the 6 z-ticks live in the edge model,
ourvz recovers little. t6stk3-vs-t6svyx stage counts barely move (+10 divisions and -8 DeepCenter gap accepts with
z off), so the z effect is in WHICH edges are chosen, not how many.
Pre-built for the evening: `v_ourvz15` (scratch_kernels/build_ourvzg.py <tag> <zmult>): ourvz with z gain x1.5
(effective 3.0); helper unit-tested. Needs a gate entry + plan before use. Use only if ourvz >= 0.954 AND
t6svz15 >= t6stk3.

## 09-26 02:45Z: z MECHANISM + discussion reread
* The writer ROUNDS (cell 5: "z": max(0, int(round(float(node["z"]))))). SV z offsets are clipped < 0.5 voxel, so
  they NEVER change a written z. The +6 ticks come from post-processing that consumes float z (relink distances,
  gap fill midpoints, line-fit smoothing, division geometry) and lcefr (edge model reads refined coords). The
  all-axis sub-voxel gain curve (0.946 -> 0.951 at gain 2) is therefore probably mostly z.
* In flight (run-only, pushed 02:35Z): t6svz15 (z gain 3.0, y/x 2.0) and t6svz0yx (z only, y/x zeroed); gate entries
  added + negative-tested; plans ops/plan_t6svz15.json / plan_t6svz0yx.json.
* Forum 743222 (imissher, 18h): 8 board tests on the public 0.947 stack, all negative: relink off -2, ILP candidate
  0.48->0.30 0.000, z-flip TTA 8->16 views -2 (confirms our drop), DET 0.960/0.970 -2/-3, secondary weight 0.65 -3,
  own secondary model -9, synthetic fine-tune of the secondary -6; "geometric repair always helped, trusting the
  learned association more always failed - fits test being a different embryo". 2xT4 trains ~12-25 epochs per 8h vs
  402 for the public primary: detector training is not closable on Kaggle. 743006: #1 (Gabriel) asks the same
  public/private question, no answer. Nothing else new.

## !!! 09-26 02:32Z: t6svyx = 0.948 (-6). OUR SUB-VOXEL Z CHANNEL IS WORTH ~+6 TICKS. ourvz SUBMITTED (slot 1/5). !!!
| arm | y/x refinement | z refinement | lcefr | board |
|---|---|---|---|---|
| t6stk3 | sub-voxel | sub-voxel | yes | 0.954 |
| t6svyx | sub-voxel | NONE | yes | **0.948** |
| ourv | V1284 | none (head never moves z) | no | 0.951 |
| **ourvz** | V1284 | sub-voxel | no | **pending (submitted 02:32Z)** |
Reading: z channel ~ +6 (t6stk3 vs t6svyx); V1284 y/x beats sub-voxel y/x by ~+3 (ourv vs t6svyx, modulo lcefr).
If additive, ourvz ~ 0.951 + 6 = ~0.957. The largest measured effect in the project; the z axis is THE live lever.
**Silver line LEFT the 0.953 block** (threat watch 02:30Z): 206 teams above 0.953, silver line rank 195 (of 3,908),
we are rank 161 at 0.954. Silver now = top-195 among climbers; a real gain is needed, not just beating x138.
Next research (in progress): WHY is z worth 6 ticks (writer rounding/truncation? GT z convention bias?) and can a
direct z lever do better (z gain, constant z bias). Picks: A t6r70, B t65s3 until ourvz scores; if ourvz >= 0.955 it
becomes pick A or B (measure pairdiff: ourvz differs from t6r70 on ~52% of 3um-binned edges = max diversity).

## 09-25 19:35Z: threat watch: anvithpothula RENAMED biohub-x138 -> "biohub-0-953-lb-runnable-with-public-datasets"
Same lastRunTime (09-21 09:47:58) = rename only, no new code; advertises 0.953 + public datasets -> more forks into
the 0.953 block (irrelevant to us, we sit above it). Drift: above-0.953 = 184 (was 158 this morning), we are rank
148, silver line 195 -> ~11 more climbers push silver out of the block. Watch re-armed with the new baseline.

## 09-25 19:04Z: t6svyx SUBMITTED (slot 5/5 of 09-25) - submission id 56558354
The 15:15Z chained job died with a session restart before downloading the log; recovered 19:00Z: getlog -> GATE_PASS
(ARM_SV_YXONLY_AXES z_mean_abs=0.0000 z_nonzero=0 on all movies, yx_mean_abs 0.142-0.268; FINAL 25,621 / 20,725 /
6,161 / 70,317 = 122,824 vs t6stk3 122,863; 0 tracebacks) -> submitted 19:04Z. Score due ~01:30-02:30Z 09-26.
Reading rule (unchanged): >= 0.954 -> z channel is noise/harm -> 09-26 slot 1 t6svz05, slot 2 t6svx125 (both built,
gated, planned); <= 0.952 -> z is real -> 09-26 slot 1 ourvz (ready: `python ops/run_today.py ops/plan_ourvz.json
--submit-only`); 0.953 -> unreadable, ourvz for pick-B option value. Picks: A t6r70; B t65s3 unless t6svyx >= 0.954
AND pairdiff vs t6r70 > 3.8% (measure after the score; do not assume).
Lesson: chained run->gate->submit jobs die with the session; after a restart, check ops/run_<tag>.out and
ops/state/<tag>.* before assuming a submission happened.

## 09-25 15:30Z: 09-26 VARIANTS PRE-BUILT (scratch_kernels/build_t6svax.py = per-axis sub-voxel multipliers, t6 body)
`build_t6svax.py <tag> --z gz --yx gyx`: multipliers on the gain-2.00 offsets before the 0.4999 clip; lcefr kept.
Built + helper unit-tested: `v_t6svz05` (--z 0.5 --yx 1: z at effective gain 1.0) and `v_t6svx125` (--z 0 --yx
1.25: y/x at 2.5, z off). Markers: ARM_XENV tag=<tag> SUBVOXEL=axes zyx_gain=<z,y,x> ..., ARM_SV_AXES zyx_gain=,
ARM_SV_AXES_STATS z_mean_abs= yx_mean_abs= z_nonzero=. Gate entries staged (scratchpad/an/gate_t6svax.py).
Use per the t6svyx reading rule: t6svyx >= 0.954 -> 09-26 slot 1 t6svz05, slot 2 t6svx125; t6svyx <= 0.952 ->
slot 1 ourvz (ready), the variants shelved.

## 09-25 15:15Z: BOARD DRIFT TODAY (ops/watch/lb_trend.log): teams above 0.953 158 -> 177; we fell rank 129 -> 144
Silver line still 194 (inside the 0.953 block); 17 more climbers push it above the block, likely by 09-26. From then
silver = top ~197 among teams above 0.953, so a real gain from t6svyx/ourvz matters, not just beating x138.

## 09-25 15:15Z: LAST SLOT OF 09-25 -> `t6svyx` (t6stk3 with sub-voxel y/x ONLY, z offsets zeroed, lcefr kept)
Chosen by the 15-agent workflow (wq21udk4t; survivors: t6svyx, ourvz) as the only submittable arm with a path
ABOVE 0.954: evidence that our z shifts may hurt = the GT-trained V1284 head learned no z shift; 41% of our z
offsets sit at the clip vs 14% for y/x; hsgzc10 (more z) read 1-2 ticks below the magnitude curve; hsadapt (least
z) 0.950. Honest EV ~-1 tick, P(>=0.954) ~0.30, P(>=0.955) ~0.15. Mirror of ourvz: the pair isolates the z channel
on both bodies. Built by the workflow at scratch_kernels/v_t6svyx (t6stk3 datasets only), gate entry added
(markers ARM_XENV tag=t6svyx SUBVOXEL=yx-only LCEFR=kept ..., ARM_SV_YXONLY=1, ARM_SV_YXONLY_AXES z_mean_abs=
0.0000 ... z_nonzero=0, per-movie SV_ARM_HSG200 windows, ARM_LCEFR markers; forbids V1284/ARM_SV_ZONLY/anchor
errors; tol 0.15), negative-tested (t6stk3 log FAILS), ourvz still PASSES. Pushed 15:15Z, chained: run -> gate ->
submit on GATE_PASS (ops/run_t6svyx.out). Fallback if it fails: `python ops/run_today.py ops/plan_ourvz.json
--submit-only` (ourvz is gated and ready; otherwise it is 09-26 slot 1).
READING RULE for t6svyx: >= 0.954 -> z is noise/harm on our body (then ourvz ~0.951, dead; 09-26 = y/x-only gain
variants: z gain 1.0, y/x gain 2.5 with z 0); <= 0.952 -> z is real, ourvz expectation rises to 0.953-0.954 and it
takes 09-26 slot 1; 0.953 unreadable. Picks: A stays t6r70 unless t6svyx >= 0.956; B -> t6svyx only if >= 0.954 AND
its 3 um edge difference vs t6r70 (pairdiff) exceeds t65s3's 3.8%.
Refuted this round: ourvi (written-y/x swap, hsg4c10 failure mode), t6b22 (tie = LB probe), t6dc, ourvg15/20,
ourvr/ourvrd, t6dv/dd/wz, r90s3 (+0.2 forecast, unrun), x138-body arms, HOLD (user asked for a submission).

## 09-25 14:45Z: ourvz visible run GATE_PASS (V1284 y/x + sub-voxel z, t6 linker, no lcefr)
Nodes 25,614 / 18,692 / 6,098 / 69,151 = 119,555 (ourv 119,307; t6stk3 122,863). Markers all present
(ARM_SV_ZONLY=1, ARM_V1284_YX module_patched=1, SV_ARM_HSG200 mean_abs_off_vox 0.104-0.113 = z-only), no errors.
Ready to submit: `python ops/run_today.py ops/plan_ourvz.json --submit-only`. Expected value after ourv = 0.951:
between 0.951 and ~0.954 (it can only recover what the z channel was worth); its score isolates the z channel
(ourvz - ourv = SV-z value; t6stk3 - ourvz = SV-y/x+lcefr minus V1284-y/x).

## !!! 09-25 14:32Z: ourv = 0.951 (-3). THE PUBLIC V1284 HEAD HURTS OUR BODY. V1284 LINE CLOSED. !!!
Board: x138 body: xsv (our SV) 0.951 < xpub (V1284) 0.953. OUR body: t6stk3 (SV + lcefr) 0.954 > ourv (V1284,
no lcefr) 0.951. The heads INTERACT with the body: our linker stack (velocity 0.25 / bonus 1.6 / TIGHT 6.0) and
lcefr were tuned on SV-refined geometry; V1284's coordinates + its trilinear feature lookup break that.
Consequences: ourvg15 / ourvg20 (more V1284) DEAD. ourvr / ourvrd DEAD (already). ourvz (V1284 y/x + SV z) can only
recover toward 0.954, never above unless SV-z was net negative; low upside, some pick-B diversity value if 0.954.
**FINAL PICK B = t65s3 (56496604)** per the Monte Carlo rule (ourv < 0.953). Pick A = t6r70 (56483584).
Slot 5 of 09-25: user instruction 14:32Z = research 1 h, then submit the last one. Workflow launched.

## 09-25 14:00Z: SLOT-5 RULE (current) and the 09-26 slate
Slot 5 of 09-25 (must be run + gated + submitted before 23:59Z; ourv score due ~14:50Z):
* ourv >= 0.954 -> **ourvz** if its visible run has gated by then (queued 13:56Z behind ourvr/ourvrd; expect
  ~14:45Z), else ourvg15. ourvz is a new mechanism (z channel restored); ourvg15 is only a dose test.
* ourv = 0.953 -> ourvz (does restoring z recover the tick?). Fallback ourvg15 only if ourvz fails its gate.
* ourv <= 0.952 -> HOLD (V1284 y/x is net negative on our body; the hybrid inherits that).
09-26 slate (5 slots): the better of {ourvz, ourvg15} not yet spent; then ourvz + gain 1.5 on the y/x head if
both helped; then HOLD. ourvr / ourvrd: NEVER (cross-embryo test). Final picks per FINAL_PICKS.md, re-evaluated
after each score: pick B = the best-scoring structurally-different arm (ourv / ourvz / ourvg15) if >= 0.953,
else t65s3.

## 09-25 14:25Z: ourvr visible run GATE_PASS (record only, NOT submitted)
ourvr (retrained head, x1.2 magnitude): total nodes 118,702 vs ourv 119,307 (-0.5%) vs t6stk3 122,863; per movie
25,568 / 18,076 / 6,017 / 69,041; no traceback; head sha f7966cc607f2374d loaded. Mechanically sound, but the
cross-embryo test (above) makes its hidden-set prior negative. Kept as evidence that the head-swap mechanism works.
ourvrd (retrained x0.8325, public-head magnitude) also GATE_PASS: 119,922 nodes (25,606 / 18,752 / 6,050 / 69,514),
+0.5% vs ourv. Same verdict: record only, never submit.

## 09-25 14:15Z: t6dl = 0.954 (as predicted: byte-identical to t6stk3). PIPELINE IS DETERMINISTIC across runs.
Five arms on the t6 body now read 0.954 (t6stk3, t6r70, t65s3, t6sr, t6dl). ourv still pending (t6dl took 7h15m).
NEW ARM `ourvz` (scratch_kernels/build_ourvz.py): V1284 head for y/x ONLY + our sub-voxel soft-argmax for z ONLY,
on the t6 linker stack (lcefr dropped as in ourv). Mechanism: the public head never improves z (per-axis table
above) while our refinement does, and z shifts moved the board (hsgzc10 -3). Fixes the V1284-inside-`if not
_SV_ON` anchor trap with a `pass`. Offline: applied to the real t6stk3-patched predictor, all 4 anchors match
once, script compiles, sub-voxel offsets are computed from integer peaks before V1284 touches `arr`.
Markers: ARM_XENV tag=ourvz ... SUBVOXEL=z-only V1284_AXES=yx | ARM_SV_ZONLY=1 | ARM_V1284_YX module_patched=1.

## 09-25 14:05Z: CROSS-EMBRYO TEST = RETRAINED V1284 HEADS DO NOT TRANSFER. ourvr / ourvrd CLOSED (never submit)
scratchpad/an/retrain_cross.py (pairs 31,875: 44b6 4,676 / 6bba 27,199), centre error in um on ALL pairs of the
target embryo, head trained on the OTHER embryo only:
| target | zero | public head | cross-embryo head | best gain | movies cross beats public |
|---|---|---|---|---|---|
| 44b6 | 1.326 | **1.069** | 1.318 (= zero) | 0.5 -> 1.220 | 1/21 |
| 6bba | 1.485 | **1.393** | 1.405 | 0.7 -> 1.363 | 16/39 |
Per axis (44b6 target): zero z .754 y .536 x .548 | public z .762 y .383 x .408 | cross z **1.005** y .412 x .485.
=> A head fitted on one embryo transfers y/x partially and DESTROYS z on a new embryo. The hidden set is unseen
embryos, so ourvr/ourvrd (6bba-dominated head) would most likely score BELOW ourv. Both visible runs may finish
for the record; NEVER submit them. The balanced/per-embryo heads (scratchpad/an/heads/) are dead for the same
reason. The morning's "in-sample CV win" (1.104 vs 1.346) was within-embryo and is irrelevant to the board.
Within-embryo variants (retrain_local.py, 5-fold by movie): on 44b6 all 1.179 / balanced 1.137 / per-44b6 1.113 vs
public 1.069 - every retrained variant loses to the public head on 44b6 even in-embryo. Heads saved in
scratchpad/an/heads/ for the record only.
Also visible: the PUBLIC head does not touch z either (z .762 vs zero .754 on 44b6; .911 vs .887 on 6bba); all
of its value is y/x. Our sub-voxel soft-argmax refines z too (hsz0 / z-clip arms on the board moved the score),
so ourv may be GIVING UP a z benefit that t6stk3 had. Possible hybrid: V1284 for y/x + sub-voxel for z. See below.

## !!! 09-25 13:55Z: THE HIDDEN TEST SET IS FROM UNSEEN EMBRYOS (data description, "Embryo Identity") !!!
Verbatim: "**Train and test sets are embryo-disjoint** - no embryo appears in both." (scratch_kernels/
_intel0922/lb/page_data-description.md:26). Consequences:
* Per-embryo head selection by stem prefix (build_ourvm.py) is USELESS for the board: hidden stems carry other
  embryo ids. Keep the builder only as a base64-embedded single-head mechanism (key "default").
* Every "in-sample" argument about the public weights is wrong for the board: the hidden set is out-of-embryo
  for EVERYONE. LOEO (unseen-embryo) screens are the right proxy design; their 37/39 agreement at >= 3 ticks
  now makes sense.
* The retrained V1284 head must be judged on CROSS-EMBRYO transfer: train on 6bba -> evaluate on 44b6 and
  vice versa, vs zero-shift and vs the public head (whose 20 training movies probably span both embryos).
  The per-movie CV (which showed 44b6 getting WORSE than public) already hints the retrained head is more
  embryo-specific. Cross-embryo run: scratchpad/an/retrain_cross.py (in progress).
* ourvr / ourvrd visible runs continue (no slot); their board prior is LOWER than this morning's estimate
  until the cross-embryo numbers are in.

## !!! 09-25 13:45Z: RETRAINED V1284 HEAD IS A CLEAR HELD-OUT WIN - THE ONE LIVE MOONSHOT !!!
`v1284cap` COMPLETE (60 train movies, all captured; conversion check ok; 31,875 pairs at 3 um, 37,383 at 7 um).
**5-fold movie-held-out centre error (um): no refinement 1.462 | public head 1.346 | RETRAINED 1.104**
(-24.5% vs zero; -18.0% vs public; improves 53/60 movies vs the public head's 41/60; at the 7 um readout
1.828 / 1.685 / 1.439). Chosen config epochs=50, shrink=1.0, Huber. Head saved: data/out_v1284cap/
v1284_head_retrained.pt sha256 f7966cc607f2374d (+ summary json + v1284cap_candidates.npz 44,641 detections).
Dose-match (scratchpad/an/dose_match.py, all 44,641 captured detections): mean |shift| public 0.850 um vs
retrained 1.021 um (x1.20); cosine between the heads median 0.69, 86% positive. So `ourvr` = better direction
AND ~x1.2 magnitude; `ourvrd` = retrained x0.8325 = public magnitude, direction quality only.
**PER-EMBRYO SPLIT (summary per_movie), the key caveat:** 44b6 (21 movies): public 1.111 um, retrained **1.211**
(worse; better on 3/21). 6bba (39 movies): public 1.408, retrained **1.102** (38/39 better). 6bba supplies ~85%
of the pairs (~980 GT nodes/movie vs ~284), so the head learned 6bba's geometry. CV grid is flat (1.104-1.135
across epochs/shrink), so no regularisation choice fixes it. Fix = embryo-balanced or PER-EMBRYO heads chosen by
stem prefix at inference (the movie stem carries the embryo id) - retrainable locally in seconds from
v1284cap_candidates.npz (tiny MLP, 44,641 rows). Whether the hidden set shares the two train embryos decides
if this transfers; the public detector's 0.947-0.954 on the hidden set (vs LOEO's collapse on an unseen
embryo) argues the hidden movies ARE from the same two embryos.
**Revises the morning refutation of ourvr**: that argued a better-CV head is "a gain arm in disguise". Magnitude
is only x1.2 (ourvg15 = x1.5 of the public head), and unlike a scalar gain the retrained head moves centres in
better directions (18% lower held-out error). Both variants built + gated (head sha PINNED in gate for ourvr and
ourvrd; the gate refuses the public head). Visible runs: `ourvr` pushed 13:45Z, `ourvrd` pushed 13:46Z (run-only).
**SLOT PLAN once ourv scores:** ourv >= 0.954 -> slot 5 = ourvr (if its run gates in time, else ourvg15);
09-26 slate = ourvrd, ourvg15, then the better of ourvr/ourvrd stacked with x1.2-1.5 gain.
ourv = 0.953 -> slot 5 = ourvrd (cleanest test of direction quality at proven magnitude).
ourv <= 0.952 -> hold slot 5; 09-26: ourvrd only (low prior).
GPU quota: believed to reset Saturday 00:00 UTC = 2026-09-26 00:00Z (~10 h), unverified.

## 09-25 ~10:40Z: IDLE-SLOT POLICY REFRAMED + synp recalibration ruled out
Final picks are chosen AFTER scoring and pick A (t6r70) protects silver regardless, so a genuinely different,
high-variance arm costs only a slot (+GPU): positive option value. HOLD applies to near-duplicates only.
Candidate moonshots with real variance = the V1284 line only (ourv pending, ourvg15 staged, ourvr if capture CV
is informative). Checked and dropped: **synp recalibration** - the synthetic primary over-fires movie-dependently
(raw nodes +5% 0113de3b, +49% 05b6850b, +85% 0b24845f -> 40,000 cap) and the retention guard (use_primary when
blend < 0.9 x primary candidates, e.g. 115/140) amplifies it; one global DET cannot match all movies; prior < 10%.

## 09-25 ~10:30Z: USER ASKED FOR 0.97 - HONEST CEILING + last public lead closed
* thtennant (0.959) public ablation ladder, board scores read from each notebook page: gapfill 0.947, flow2 0.947,
  gapfill-det096 0.947, fast 0.946, readmit 0.946, fast-tight60 0.946, flow2-det096 0.946, divprec **0.942**
  (their own board also punished divprec), 2 pages unreadable. => every published component sits at 0.942-0.947;
  their 0.959 is unpublished work. No public route above our body.
* Compute: box V100 (single GPU) at 97% util (user's RSNA job + an ltx-v100 process), load ~35-40 -> NOT
  available without disturbing the user's jobs. Kaggle T4s only (weekly quota partly used).
* Honest ceiling for the last 4 days: ~0.955-0.957 (V1284 line if ourv lands well). 0.97 (+16 ticks) would need
  the week-scale model training the top-10 teams did; no lever found by 3 workflows + ~50 board arms moves > 2.

## 09-25 ~10:15Z: ENDGAME ASSURANCE (workflow wk87e8cgy) - PICK-B RULE CORRECTED; FINAL_PICKS.md rewritten
**Pick A = 56483584 (t6r70).** Representative entry: strictly above t6stk3, >= t65s3/t6sr at full precision.
**Pick B: ourv (56544543) if it reads >= 0.953; if <= 0.952 / failed / pending at 09-29 12:00Z -> t65s3
(56496604)** (t6sr 56535504 equal alternative). Supersedes "ourv if >= 0.952" (at 0.952 ourv loses to t65s3 in
12/12 simulated scenarios). Optional bronze floor only if ourv <= 0.952: xpub as B trades ~0.035 P(silver) for
+0.07..+0.30 P(bronze) when <= ~230 teams end above 0.953 (vanishes at ~260). Default t65s3; user decides.
Monte Carlo (scratchpad/wf3/mc_silver/mc_report.txt, 20k draws, sigma 0.0020 calibrated on held-out embryos):
P(silver) ~0.45-0.55 with {t6r70,t65s3}, ~0.53-0.64 with {t6r70,ourv@0.954}. **Silver != beat x138**: ~23-37
tied teams escape above x138 via a different second pick, so P(silver) is 0.05-0.25 below P(beat x138).
Verified: max-of-2 private (page_rules.md:37); exact ties -> earlier submission (page_rules.md:142 + the 0.953
block is in strictly increasing submission id, 201/201 pairs); private fixed at scoring (usesSynchronousReruns);
identical pipelines tie in practice (~95%, not guaranteed); medals awarded (research comp); no selection ->
top-2 public; one tick -> other auto-filled with best public; silver = floor(5% of RANKED teams) at close
(~197-201, not a fixed 194); selection rights formally = Team Leader (so Eesh sets + confirms picks).
Corrections: t65s3 vs t6r70 edge difference is 3.8% at 3 um tolerance (7.6% was an exact-position artefact),
t6stk3 2.0%, t6sr 2.25%; ourv/xpub 12-14% (not 85%). xpub would rank ~188th of 202 identical runs (not the very
bottom). The rerun-timeout argument for t6dl is obsolete (scores fixed). ops/watch/rep_check.py now uses ranked N.

## 09-25 ~09:45Z: FALLBACK PICK B CHANGED t6stk3 -> t65s3 (diversity), + tools
Position-keyed edge comparison against pick A t6r70 (scratchpad/an/pairdiff.py): t6stk3 differs on 2.0% of
edges, t6sr 2.3%, t6dl 2.0%, **t65s3 7.6%** (ourv/xpub ~85%, because V1284 moves every coordinate). t6r70 is
t6stk3 + a 1% edge override, so {t6r70, t6stk3} is nearly one pick. **If ourv < 0.952, pick B = t65s3
(56496604)**, not t6stk3. FINAL_PICKS.md (repo root) = the user/teammate-facing sheet: exact ids, what not to
tick, web-only selection steps. `ops/watch/rep_check.py` = passive LB read (our rank, representative submission,
block sizes); at 09:40Z: rank 127, representative t6r70, 0.953 block 228 teams (157-384), 156 teams above 0.953,
silver line rank 194. `ops/watch/threat_watch.sh` running (author code releases / silver line leaving block).
ourvg15 gate tolerance pre-staged to 0.25 (GATE_PASS); ourvg20 still fails; ourv still passes.

## 09-25 ~09:30Z: SLOT-5 RULE (refined) + two anvithpothula notebooks checked
**Slot 5 of 09-25: ourv >= 0.954 -> submit ourvg15; ourv <= 0.953 -> HOLD.** Rationale: an unspent slot is worth
exactly 0; at ourv = 0.954, ourvg15 is still a genuine dose test of the V1284 mechanism (not a near-duplicate:
-3.9% nodes vs ourv, concentrated on low-agreement movies), and its answer decides whether the V1284 line gets
09-26 slots. Never treat a 1-tick ourvg15 lead as a pick change (public SD ~0.002-0.0035). Before submitting,
raise ourvg15's count tolerance in ops/gate.py to 0.25 with the raw-ILP-stage reason (its only gate failure).
Checked (scratch_kernels/_pub0925/): anvithpothula/biohub-v1284-head-s075-notebook = empty Kaggle template;
anvithpothula/divqc-ground-truth-free-division-qc = a GT-free QC flag for UNDER-called divisions (not a lever).
Its official-scorer measurement on 50 movies: div TP 17 / FP 19 / FN 56 -> divJ 0.185, 35/50 movies score 0 -
consistent with our wf2 finding (divJ FN-limited; oracle FP removal ~+5 ticks but FP forks are not identifiable
without GT).

## 09-25 ~09:15Z: BIG-LEVER HUNT (workflow wsfyt0u3n, 5 lenses) = ZERO CANDIDATES -> HOLD
Lenses: conditional fusion, division channel, ILP/graph constants, out-of-sample (LOEO) mining, public assets.
None found an untested lever with a plausible >= 3-tick effect. Slate for 09-26..09-28 is EMPTY unless:
(a) ourv >= 0.955 (then ourvg15), (b) a public notebook/weights > 0.954 WITH code appears (watch anvithpothula
0.956, thtennant 0.959, y3uanm 0.955; port only components with a board datum), (c) a forum post reports a
board-measured >= 3-tick lever on the published stack. Holding slots is correct: sub-3-tick arms are unreadable
(public SD ~0.002-0.0035) and near-duplicates to read decimals = LB probing.
**Key facts from it (keep):**
* hikaggler's "conditional fusion" is ALREADY in our body (low_margin_consensus secondary linking + retention
  guard); third-model variants cap at ~1.5 ticks; andnyu's base was 0.945 not 0.947 (its 0.946 = noise +1).
* **LOEO screen calibration**: its metric agreed with the board on 37/39 pairs whose board gap was >= 3 ticks,
  coin-flip at 1 tick (scratch_kernels/_calib0922/calib_summary.json). No unboarded OOS-positive lever > 0.7 tick.
  LOEO says: coordinate refinement generalizes to unseen embryos; node-count and division-precision levers are
  embryo-specific (Tp/Tt 0.773 vs 0.970 between embryos); learned parts fitted on train transfer worse (V1284 is
  the one board exception) -> ourv's private transfer is less certain than its public reading.
* **EXACT DIVISION METRIC (patched host scorer, royerlab aa65e90 = official_scorer_075fc5):** multi-frame edges
  dropped, merges collapsed. TP = GT division paired 1:1 with a predicted fork F where F (or predecessor) matches
  the GT divider/parent side (+-1 frame) and TWO distinct pred child branches contain nodes matched to the GT
  child/grandchild of two different daughters (Hungarian per division per t at 7 um; daughter edges need not
  match); F not cross-component/malformed. FP = forks at matched annotated GT nodes with out-degree >= 1, forks in
  a GT division's local window that did not pair, forks whose branches land on >= 2 GT components, forks with a
  merged child - minus TPs. FN = unpaired GT divisions. **A fork on an unannotated cell costs NOTHING.**
  Measured (plain-python port scratchpad/wf2/division/newdiv.py): only ~1.3-1.8% of our forks are FP, so divJ is
  FN-limited; oracle-removing every FP = +0.005-0.0065 max; added forks break even at ~17% precision and every
  candidate pool is < 5%; recall is capped by the gates (13/48 GT divisions pass them on exact GT coords = our
  measured recall). **CORRECTION:** every local division scorer we used (ops/score_official.py, vendored
  division_metrics.py, kernel compute_division_confusion, box hfval3/div20) is the PRE-patch weak-component rule;
  the old claim "every division we add is FP" misreads the metric.

## 09-25 ~09:00Z: OUR OWN BOARD DATA SAYS NODE COUNT IS *NOT* THE LEVER (30 scored arms with visible run_stats)
| arm | board | visible total nodes | vs its base |
|---|---|---|---|
| hfusion | 0.947 | 122,794 | base |
| hdet975 | 0.945 | 121,218 | -1.3% nodes, -2 ticks |
| hdet98 | 0.945 | 120,236 | -2.1% nodes, -2 ticks |
| mtl8 | 0.947 | 119,494 | -2.7% nodes, tie |
| xsv | 0.951 | 124,144 | base (x138 body) |
| xpub | 0.953 | 121,219 | -2.4% nodes, +2 ticks |
| t6stk3/t6r70/t6lf/t6w72/t6rlf | 0.954/0.954/0.953/0.953/0.953 | 122,863 (identical) | same count, 1-tick spread |
Cutting nodes via DET LOST; via MIN_TRACK_LEN TIED; via V1284 GAINED. So V1284's +2 on x138 is not explained
by its node cut (the forum rule does not hold as a free lever on our lineage). Consequence: ourvg15's larger
node cut is NOT evidence for it; the gain line lives or dies on ourv's own reading only.
Also: the public LB ranks ties by EXACT score and names each team's representative submission (passive read,
scratch_kernels/_intel0922/lb/fetch_lbweb.py). If our representative flips from 56483584 (t6r70) to 56544543
(ourv) after ourv scores, ourv > t6r70 at full precision even if both display 0.954. No extra submission needed.

## 09-25 ~08:40Z: CONTINGENCY WORKFLOW RESULT (10 agents, 4 lenses + 5 adversarial verifies + synthesis)
Full text: task output wg888r4gj; scratch evidence under scratchpad/wf/{linker,v1284_nodecount,frontier,finalpick}.
**FINAL PICKS (supersedes the endgame plan below):**
* **Pick A = t6r70 (56483584).** The public LB API shows it as our TEAM REPRESENTATIVE submission, i.e. the
  best full-precision public score among our 0.954s (t6stk3/t65s3/t6sr/t6r70). Read passively, not probed.
* **Pick B = ourv (56544543) if it reads >= 0.952** (different body output: 119,307 nodes vs xpub 121,219, so it
  cannot tie the x138 block); **else t6stk3 (56467741).** Estimated P(max private > x138 private): ~0.69-0.87
  with ourv as B vs ~0.59-0.66 for a same-body pair.
* NEVER: xpub or any x138-body arm (tie -> bottom of block), t6dl (byte-identical to the earlier t6stk3), two
  V1284-on-our-body arms together, or any pick on a 1-tick lead of a gain variant (public SD ~0.002-0.0035).
* Set picks >= 12 h before 09-29 23:59Z; re-check ~1 h before on My Submissions (CLI cannot show selection).
  Teammates (akkigupta2005, arunendratripathi03, swapiy): do not Select/Unselect anything; Eesh sets finals.
  If nobody selects, Kaggle auto-picks the top 2 public = a same-body pair (worse).
**SLOT 5 of 09-25 (held for ourv):** ourv >= 0.955 -> submit ourvg15 (gate tol for ourvg15 must be raised to
0.25 with a comment; the cut is at the raw ILP stage). ourv <= 0.954 -> nothing verified beats leaving it unspent
(r70sr/t6b22 refuted as near-duplicate ties; submitting near-duplicates to read decimals = LB probing, banned).
**REFUTED on verification:** r70sr (two ties stacked, ~0 info), ourvr (centre accuracy has no proven route to the
board; a better-CV squared-loss head predicts LARGER shifts = a gain arm in disguise), ourvr70, t6tri, t6b22.
Also closed: readmit/gap-fill ports (add nodes), weak-leaf prune (only prunes 0-prob relinked ends), ddsr
(creates in-degree-2 nodes, merges division sisters), ILP app/disapp weights (pinned, no datum), 16-view TTA
(prediction ~7.5 h hidden x2 exceeds 12 h).
**THREAT:** teams above 0.953 went 67 (09-22) -> 135 -> 150 -> 155; ~39 more push the silver line ABOVE the 0.953
block (likely 09-26/27). Then silver = top-194 among x138-tweak teams, not just "beat x138". No public notebook
> 0.953 yet; watch anvithpothula (0.956), thtennant (0.959), y3uanm (0.955) for code releases. Daily: leaderboard
pull + `kaggle kernels list --user anvithpothula` + `kaggle datasets list -s v1284`.

## !!! 09-25 07:40Z: SILVER IS DECIDED BY ONE COMPARISON - OUR PICK vs THE x138 PIPELINE ON PRIVATE !!!
Full leaderboard pulled (3,898 teams). We are **rank 123 at 0.954** (was ~86 two days ago).
| public score | ranks | teams |
|---|---|---|
| 0.956 | 62-81 | 20 |
| 0.955 | 82-107 | 26 |
| **0.954 (us)** | **108-150** | 43 |
| **0.953** | **151-368** | **218** (185 of them posted on 09-24) |
| 0.952 | 369-388 | 20 |
Medal lines: **silver = top 5% = rank 194**, which sits INSIDE the 0.953 block; bronze = rank 389;
gold ~ rank 17 = 0.965.
**What the 0.953 block is**: the top public notebooks by score are kunaldesale2408/biohub-cell-tracking
v10 (0.953, 259 forks) and anvithpothula/biohub-x138. A code diff (agent, 09-25) shows **kunaldesale v10
IS x138 verbatim** with the V1284 dataset attached - i.e. exactly our `xpub` arm (0.953 on our account).
So ~200 teams run one identical pipeline and will get one identical private score.
Consequences:
* **Silver <=> our final pick's PRIVATE score beats xpub's PRIVATE score.** Anything tying it lands at the
  BOTTOM of the tie (Kaggle breaks ties by earlier submission; ours are later) -> rank ~368 -> bronze.
* **xpub is therefore USELESS as a final pick.** Supersedes the endgame plan below that named it pick B.
* Public frontier is 0.953; amanatar "optimized-biohub-max-score" is 0.910 (current version errors),
  andnyu synthetic-conditional-third-model 0.946 - no public notebook above us to fear today, but a new
  0.955+ fork source in the last 4 days would push silver above 0.954. Re-pull the board daily.
* Our margin over the block on public is ONE tick. Widening it is the whole game for silver.

### V1284 CUTS NODES AT THE ILP, SAME ON BOTH BODIES (ourv port verified faithful)
Raw ILP node counts are IDENTICAL between ourv and xpub on all four movies (25,817 / 20,206 / 6,239 /
69,515), so V1284's moved centres change which nodes the ILP keeps, independent of the linker stack.
| arm | total output nodes | board |
|---|---|---|
| xsv (x138 + our sub-voxel) | 124,144 | 0.951 |
| xpub (x138 + V1284) | 121,219 (-2.4%) | 0.953 |
| t6stk3 (ours + our sub-voxel) | 122,863 | 0.954 |
| ourv (ours + V1284) | 119,307 (-2.9%) | pending |
ourv also trips the short-track rescue on 44b6_0b24845f (removed frac crosses 0.10): 17 comps / 73 nodes.
**Metric note (busyaprime, verified vs the organisers' scorer):** score = sum_i TP_i*(1-0.1*rho_i) /
sum_i(TP+FP+FN) + 0.1*divJ, rho_i = (N_pred-N_est)/N_est, **NOT clipped at 1** - under-predicting is a
bonus, but only through TP_i, so dropping nodes pays only if they carry ~10x fewer TP than average.
GT is extremely sparse: median 4 annotated tracks / 228 nodes per movie vs N_est ~28,600.

### 09-25 ~08:00Z: t6sr = 0.954 (TIE). Arming the short-track rescue is neutral on the t6 body.
So ourv's rescue trigger on 44b6_0b24845f is not a liability. t6sr joins t6stk3/t6r70/t65s3/(t6dl pending)
as a fourth 0.954 on the same body: that body's public reading is very stable.

### 09-25 07:34Z: `ourv` SUBMITTED (slot 4/5). Gate needed ONE documented override.
The generic FINAL-count drift check failed: 44b6_0b24845f 18,509 vs ref 20,721 (-10.7% > 10%). Every
identity/config marker passed, no traceback. The drop is already present at the RAW ILP stage and equals
xpub's raw count exactly (20,206), i.e. it is V1284's known effect, so `ops/gate.py` now carries
tol ourv 0.13 / ourvg* 0.15 with that reason in a comment. Nothing else in the gate was relaxed.
`ourvg15` pushed 07:32Z (run only, not submitted). Score watcher: background loop appends to ops/scores.log.
Pending scores: t6sr 56535504, t6dl 56543692, ourv (07:34Z).

### HOW V1284 CUTS NODES: NOT DEDUP, IT RESHUFFLES THE LINKING (09-25, ours vs t6stk3 outputs)
44b6_0b24845f: 3,287 t6stk3 nodes have no ourv node within 3 um (~16% churn, net -2,178). Dropped nodes have
the SAME nearest-neighbour spacing as kept ones (median 9.45 vs 9.41 um; <4 um: 0.6% vs 0.4%), so it is not
duplicate removal; they sit on shorter tracks (median 16 vs 21 frames). 6bba_05db0fb1: 3,024 dropped, NN 7.32
vs 7.64 um, track len 32 vs 51. A <=2 um centre shift re-routes the ILP broadly. No cheap direct lever here.
Forum re-read 09-25 (threads 742131/742169/741446/742266/741651/743006): nothing new board-measured.
andnyu/biohub-synthetic-conditional-third-model = 0.946 (below its 0.947 base): synthetic fusion closed too.

### TTA: considered 09-25, NOT recommended
Detection TTA in our body is already the full 8-view D4 group in y/x (flips, rot90 k=1/3, transpose,
anti-transpose). The only unused symmetry is the z-flip (-> 16 views). The one board datum is ambiguous:
tta8z replaced D4's 4 rotation/transpose views with 4 z-flip views and lost 11 ticks (0.947 -> 0.936), which
fits "rotations are valuable" AND "z-flips hurt" equally. A 16-view arm is high-variance and ~2x prediction
runtime. Skip unless the V1284 line is exhausted and slots are idle.
**09-25 ~10:00Z: DROPPED even for idle slots.** Public recipe = D4 8-view (support pack default was 4-view,
`/4`); tta8z kept the 4 shared flips and swapped the 4 rotation/transpose views for 4 z-flips -> -11. With z
4x coarser than y/x, a 1-voxel z misregistration under flipping is a plausible harm; 16 views = half z-flipped
-> central estimate between -5 and +1 ticks, negative EV, plus timeout risk.

### ourvg15 VISIBLE RUN (09-25 ~08:05Z): GATE_FAIL on count drift only; mechanism is real, not breakage
No traceback; `ARM_V1284_GAIN gain=1.5 module_patched=1` present. Raw ILP nodes on 44b6_0b24845f fall
MONOTONICALLY with the centre shift: t6stk3 22,478 -> ourv 20,206 -> ourvg15 17,225 (final 20,687 / 18,509 /
15,635 = -24.5% vs gate ref). Other movies move 0-2%. Totals: t6stk3 122,863, ourv 119,307, ourvg15 114,663.
Placeholder TP there 48/49 (not board evidence). 0b24845f is the movie with 64/100 retention-guard fallback
frames (low primary/secondary agreement, N_est 32,795 vs our ~20k), so V1284-gain node cuts concentrate on
low-agreement movies. Gate NOT widened yet: decide after ourv's score + ourvg20's run.

### ourvg20 (gain 2.0) VISIBLE RUN: RULED OUT - the shift starts BREAKING linking, not trimming nodes
| arm | 0b24845f raw/out | total out | placeholder node recall 0b24845f / 05db0fb1 | FN 05db0fb1 |
|---|---|---|---|---|
| t6stk3 | 22,478 / 20,687 | 122,863 | 51/51 / 1217/1229 | 72 |
| ourv (x1.0) | 20,206 / 18,509 | 119,307 | 51/51 / 1215/1229 | 80 |
| ourvg15 (x1.5) | 17,225 / 15,635 | 114,663 | 51/51 / 1212/1229 | 81 |
| ourvg20 (x2.0) | 13,222 / 11,675 | 106,728 | **47/51** / **1204/1229** | **89** |
Node counts fall steeply with gain and at 2.0 annotated recall visibly drops. So the V1284 node cut is at
least partly LINKING DISRUPTION from moved centres, not pure precision. Never submit ourvg20. ourvg15 only
if ourv clearly beats 0.954 (then it tests "a bit more of the same"); otherwise drop the gain line.

### IN FLIGHT (09-25 ~07:40Z)
* `ourvg15` (gain 1.5) and `ourvg20` (gain 2.0): pushed run-only (`ops/run_ourvg15.out`, `ops/run_ourvg20.out`).
* `v_v1284cap` (scratch_kernels/build_v1284cap.py) PUSHED 07:58Z 09-25 (run only, ~2-2.4 h): captures V1284
  features on 60 TRAIN movies (21 x 44b6 + 39 x 6bba, placeholders excluded), matches to GT (3 um gate, 7 um
  readout), 5-fold movie-held-out CV vs zero-shift and vs the public head, then fits on all and writes
  /kaggle/working/v1284_head_retrained.pt (identical format) + summary json. Markers: `V1284CAP movies=..
  pairs=..`, `V1284CAP cv_err zero=.. public=.. retrained=..`. Pushed early (no slot spent) so the arm can be
  ready before ourv scores. Offline: conversion verified (grid x (1,4,4) native; raw nodes 1.94 um mean vs GT,
  public head 1.72 um = -11%).
* `ourvr` BUILT (`scratch_kernels/build_ourvr.py`): ourv with ONLY the head file swapped to the retrained one,
  mounted via kernel_sources eeshsaxena/biohub-v-v1284cap; notebook refuses the public head, checks shapes,
  prints `ARM_V1284R head=retrained ... sha256=`. Gate entry added + negative-tested (ourv log as ourvr FAILS).
  Push ONLY after v1284cap's CV shows retrained < public error. `--base v_ourvg15` builds a gain+retrained combo.
* ourvg15 + ourvg20 visible runs COMPLETE; logs being fetched/gated.
* Research workflow `biohub-contingency-levers` running: 4 lenses + adversarial verify + contingency synthesis.
* Slot 5 of 09-25 is HELD until ourv scores (user instruction 09-25).

### NEXT ARM BUILT: `ourvg15` = ourv with the V1284 shift x1.5 (`scratch_kernels/build_ourvg.py <tag> <gain>`)
Rationale: V1284 is an MSE regressor (shrinks toward 0 out of sample); our own sub-voxel refinement peaked
on the board at gain 2.0 (1.0: 0.949, 2.0: 0.951, 3.0: 0.949). Gate entries exist for ourvg15/20/13 and
demand `ARM_V1284_GAIN gain=X module_patched=1` (the notebook re-reads the written module and raises if
the gain expression is missing). Submit ONLY if ourv >= 0.954.

## ENDGAME PLAN (written 2026-09-25 07:15Z, four days out)

### WHERE WE ACTUALLY STAND
* **Rank ~86 of 3,871 at 0.954.** Silver is the top 5% (~193), so **silver is held** with margin.
  Gold is roughly rank 17, about **0.966 = +12 ticks**. No lever tried in 157 submissions has shown
  anything like that, and the discussion says the teams up there retrained models.
* **Our body is the best thing available to us**, and it now beats the strongest public notebook when
  both run on our account (t6stk3 0.954 vs x138-verbatim 0.953).
* **The board is the only instrument**: the visible test movies are placeholders, ~199 hidden movies
  are scored, ~6 h latency, 5 readings a day. Offline numbers are hypotheses.
* **The public board is 29% of the hidden set** (~58 movies); private is ~141. Our top arms sit at
  0.953-0.954, which the public board cannot separate. Private will reshuffle them.

### WHAT IS CLOSED ON THE BOARD (do not spend slots here)
Every post-processing knob on our body since 09-22 (0.953-0.954); division gates both directions
(0.945-0.950); line-fit; tight radius beyond 6.0; refinement gain; the merged x138 body with our
refinement (0.951); the synthetic primary as a drop-in (structurally broken: node cap hit, 86-frame
fallback explosion).

### WHAT IS STILL OPEN
1. **ourv** - our linker stack with the public V1284 head instead of our sub-voxel block. The only
   clean comparison says V1284 beats our refinement by +2 on the x138 body (0.953 vs 0.951). Modest
   prior. If it scores >= 0.955 it is a new best AND a structurally different final-pair candidate.
2. **A V1284 head retrained on far more movies.** Its author trained on 20 movies and recorded that
   volume was the bottleneck (the 4-movie version was 14.9% worse). We hold 199 train movies with GT on
   the box. ONLY worth doing if ourv shows V1284 helps on our body - and it needs hours of GPU on a
   box that is currently also running the user's RSNA fine-tune, so it must not be started blind.

### FINAL SELECTION - THIS IS WHERE THE PRIZE IS DECIDED
Principle: with public unable to separate our top arms, pick for ROBUSTNESS on the 71% we cannot see.
* **Pick A = t6dl.** It is t6stk3 byte-for-byte on the visible run (proven: identical node dict and
  edge set, guard reports degraded=0 fallback=0), plus the rerun deadline guard. The t6stk3 body is
  our most-replicated result - t6stk3, t6r70 and t65s3 are three different arms on it that ALL scored
  0.954 - and t6dl adds timeout protection on top. There is no reason to pick unguarded t6stk3 over it.
* **Pick B = the best STRUCTURALLY DIFFERENT arm at >= 0.953**, so the pair does not fail together if
  the private movies favour a different body. Today that is **xpub (0.953)**: the x138 body with flow
  relink, readmit, gap filling and V1284 - a different recall stack, and it carries its own deadline
  guard natively. If ourv lands >= 0.954 it is a better B, since it keeps our proven linker stack.
* **Tell the teammates**: four members can change the two final picks. They must not.

### SLOT POLICY FOR THE LAST FOUR DAYS
Most of the remaining ~22 slots have no high-value target. Spending them on near-duplicates of 0.954
only buys noise. Spend a slot only when it (a) tests a genuinely open hypothesis above, or (b) confirms
a final-pair candidate. Holding a slot is a legitimate choice.

## 09-25: THE SYNTHETIC-PRETRAINED PRIMARY (synp) IS STRUCTURALLY BROKEN, NOT JUST CONFOUNDED
`synp` = our body with bhpepper's public 5-fold synthetic SWA as the PRIMARY checkpoint - the one
ready-made test of the discussion's single reported model-side lever. Its placeholder J (0.9196) was
worthless as evidence, because the placeholders are in-sample for the public weights. But the gate
refused it on grounds that have nothing to do with J and would hold on the hidden set:
| movie | t6stk3 nodes | synp nodes | |
|-------|------------:|-----------:|--|
| 44b6_0113de3b | 25,617 | 26,853 | +5% |
| **44b6_0b24845f** | 20,687 | **40,000** | **+93%, and 40,000 exactly: it hits a hard CAP** |
| **6bba_05b6850b** | 6,158 | **9,029** | **+47%** |
| 6bba_05db0fb1 | 70,401 | 75,918 | +8% |
and the dual-seed **retention guard fell back on 86 frames of 6bba_05b6850b against a reference of 1**
- the synthetic primary's detections diverge so far from the secondary's that the blend stops trusting
it. That is a CALIBRATION failure: DET_THRESHOLD 0.965 and the 0.80 blend were tuned for the public
50ep primary, and the synthetic model over-fires badly under them. It explains bhpepper's own 0.950.
Making it viable would mean re-tuning DET and the blend for a new primary with zero board evidence,
on a lineage where the last primary swap (prim300) cost 4 ticks. **Closed as a drop-in.**

## 09-25 ~07:00Z: xpub = 0.953. THE PUBLIC "0.956" DOES NOT REPRODUCE ON OUR ACCOUNT.
`xpub` is anvithpothula/biohub-x138 run VERBATIM, with its real V1284 head mounted from the public
dataset. Its author's board shows 0.956. On our account it scores **0.953**.
So:
* **OUR OWN BODY IS STILL THE BEST THING WE HAVE, AND IT BEATS THE STRONGEST PUBLIC NOTEBOOK WHEN
  BOTH RUN ON OUR ACCOUNT**: t6stk3 0.954 > xpub 0.953. We are not missing an easy public win.
  The author's 0.956 came from a different version, a different day's hidden sample, or variance -
  we cannot tell which, and it does not matter: the version anyone can run scores 0.953 for us.
* **The clean V1284-vs-our-refinement comparison, both on the x138 body, both on our account:**
    xsv  (x138 + our sub-voxel)  = 0.951
    xpub (x138 + V1284 head)     = 0.953
  V1284 is worth about **+2 ticks** over our sub-voxel on that body - not the +5 the public number
  implied, and within about one noise band of zero. Real but modest.
* That makes `ourv` (our linker stack + V1284 instead of our sub-voxel + lcefr) a fair test with a
  modest prior: if the +2 transfers, ~0.956; if it does not, ~0.954. It is running now.
* For the FINAL PAIR, xpub at 0.953 is now a weaker structurally-different second pick than it
  looked. Keep it in reserve; do not pair it with t6stk3 on the strength of its public 0.956.

## !!!!!! 09-25: STOP. THE FOUR "TEST" MOVIES ARE NEVER SCORED. !!!!!!
From the competition's own data description, which has been sitting in
`scratch_kernels/_intel0922/lb/page_data-description.md` in this repo the whole time, verbatim:

> **test/** - Example test samples (copies from train). Contains `.zarr` image volumes only - no
> ground truth is provided. **When a notebook is submitted for rerun, a new hidden test set is
> swapped in. The size of the hidden test set is approximately the same size as the training
> dataset.**

So: the four movies we can see are PLACEHOLDERS. On submission Kaggle swaps in a completely
different hidden test set of roughly **199 movies**, and every score we have ever received comes
from that, not from these four.

### WHAT THIS INVALIDATES - ALL OF IT MINE, ALL OF IT FROM TODAY
* The 2,127-edge "validator" measures movies that are never scored. `ops/score_gt.py` is not a score
  predictor and must not be used as one.
* Therefore: the J=0.95722 baseline, the 2036 TP / 0 FP / 91 FN breakdown, the "66 linking vs 16
  detection" split, the 37 mislinks and their 7.41 um separation, the de-duplication radius curve,
  and the sweep-1/sweep-2 result that "ten knobs move zero scored edges" - every one of those
  describes the placeholder movies. None of it is evidence about the board.
* The N_est numbers read from those four geffs (25,755 / 32,795 / 6,362 / 69,800) are the
  placeholders' estimates, not the hidden set's.

### WHAT IT EXPLAINS, AND THESE ARE THE TELLS I SHOULD HAVE READ EARLIER
* **Scoring takes hours.** Kaggle is not scoring a CSV, it is RE-RUNNING our notebook over ~199
  movies. Our visible run does 4 movies in 9 minutes of prediction; the rerun does ~50x that.
* **Every offline screen this project ever built failed**, in three different generations. It was
  never only the in-sample detector weights (Eric's all-train manifest finding) - the movies
  themselves are not the scored ones.
* **x138 ships `REPAIR_DEADLINE_S = 27000` (7.5 hours) and a `_deadline_degrade()` that switches off
  the whole repair stage.** Its author was defending against exactly this rerun. That is not
  paranoia, it is the shape of the problem.

### THE RISK THIS EXPOSES IN OUR OWN FINAL PICK
**Our 0.954 body (t6stk3) has NO deadline guard at all**: zero occurrences of REPAIR_DEADLINE,
KERNEL_START_TS or any wall-clock degrade path. `xpub` (the x138 lineage) has six. Our arms have
completed the rerun so far, so there is margin today - but there is no protection if the final rerun
is slower, and a timeout on the final submission scores nothing at all. This now matters more than
any tick we might win.

### WHAT STILL STANDS
* The box replay is still a MECHANISM checker: it proves a change fires, and it measures how many
  nodes and edges it moves. That is worth keeping. It is not a ranker.
* Everything learned from the BOARD stands, because the board is the hidden set: the 0.954 plateau,
  the five 09-24 division arms all losing, line-fit closed, and so on.
* Everything learned from the DISCUSSION stands, because those competitors were also measuring
  against the board: the public weights are all-train, node-count calibration predicts board
  movement, synthetic pretraining is the only model lever anyone reports working, a trained division
  head is worth +-0.001.
* Generic transforms (the short-track rescue, node de-duplication) still DO what they do on any
  data. What is unvalidated is whether that helps the score. Only the board can say.

### THE RULE GOING FORWARD
The board is the only measurement instrument in this competition, at 5 readings a day with a
multi-hour latency, and it reads a test set we cannot see. Any claim of the form "X improves the
score" that is not a board reading is a hypothesis. Write it down as one.



## !!!! 09-25: THE SINGLE BIGGEST REMAINING DEFECT, CHARACTERISED EXACTLY !!!!
Failure breakdown on the 2,127 real GT edges, before and after the de-duplication arm:
| class | base | ddsr |
|-------|-----:|-----:|
| TP | 2036 | **2042** |
| linked to a DUPLICATE of the right cell | **37** | **34** |
| linked to a genuinely different cell | 21 | 24 |
| source node missed | 8 | 8 |
| target node missed | 8 | 7 |
| both nodes missed | 9 | 6 |
| no outgoing edge at all | 8 | 6 |
**De-duplication at 5.0 um only fixed 3 of the 37 duplicate cases.** Its +6 TP came mostly from the
rescue and from cleaning up isolated nodes, not from the mechanism it was built for. The reason is
now measured: the two co-located nodes are usually MORE than 5 um apart, and raising the radius to
5.5 makes J worse (0.95675) because it starts merging things it should not.

### WHAT THE 37 CASES ACTUALLY ARE
For every one of the 37, compare the node the SCORER matched to the GT cell against the node OUR
tracker linked to:
* **the scorer's node is closer to the true cell in 37 of 37 cases. Always.**
* median distance to the GT cell: **scorer's node 3.72 um, our node 5.77 um**
* degree tells them apart not at all: both have in-degree 1 and out-degree 1 in ~36 of 37 cases
So the picture is unambiguous. Two detections sit on one cell. The scorer takes the better-localised
one. **Our motion relink takes the other**, because its cost is `motion + 0.05*raw - bonus*prob`,
i.e. it optimises fit to the PREDICTED POSITION and knows nothing about which detection is actually
centred on a cell. The tracker gets the cell right and the node wrong, and the metric scores nodes.
**37 edges is 1.74% of the 2,127 GT edges. Converting them all would take J from 0.960 to about
0.977.** It is by far the largest identified pot left, and it is a LINKING fix, not a detector one.

### THE ARM THIS IMPLIES (not yet built)
Merging is the wrong tool, as measured. The right one is CHOOSING THE BETTER-CENTRED NODE: when two
candidate targets at the same timepoint are co-located, break the tie on how well each is centred on
a cell rather than on motion cost. The pipeline already computes exactly that quantity - the
DeepCenter centre-prior heatmap it uses for the gap and safe-division vetoes - so the signal is in
hand and needs no new model.
Two things to be careful about when building it:
1. the re-point has to respect the one-to-one constraint, so it is a re-assignment and not a
   per-edge greedy snap, or two sources will land on the same target;
2. it must be validated on the box replay first, where the heatmaps are available, exactly as ddsr
   was, before a slot is spent.
CHEAPER PROXIES WORTH TESTING FIRST, since neither needs the heatmap: prefer the co-located node
whose INCOMING edge has the higher learned edge probability, or the one with the longer surviving
track. Both are already in the graph. Test them in the replay before reaching for DeepCenter.

### CORRECTION, SAME DAY: THOSE 37 ARE MOSTLY NOT DUPLICATES. MERGING CANNOT FIX THEM.
I measured the SEPARATION between the node the scorer matched and the node our tracker linked to,
across the 37 cases:
| percentile | p10 | p25 | **p50** | p75 | p90 | max |
|---|---:|---:|---:|---:|---:|---:|
| separation | 4.15 | 6.08 | **7.41 um** | 9.08 | 10.38 | 11.38 |
| merge radius | 4 um | 5 um | 6 um | 7 um | 8 um | 9 um | 10 um |
|--------------|-----|-----|-----|-----|-----|-----|------|
| cases it would catch (of 37) | 3 | 5 | 9 | 16 | 19 | 25 | 32 |
At 5.0 um a merge catches 5, which is exactly the 3 conversions ddsr actually achieved. To catch
most of them you would need 9-10 um, and at that radius you are certainly merging genuinely distinct
cells.
**AND THE FRAMING WAS WRONG.** Two nodes 7.4 um apart are not two detections of one cell. The
scorer's node is 3.72 um from the GT cell and ours is 5.77 um, on opposite sides of it. With a 7.0 um
matching gate and cells spaced on that same order, "within 7 um of the correct cell" frequently means
"on the NEIGHBOURING cell". So most of these 37 are genuine mislinks into a crowded neighbourhood,
not a node-identity artefact - which is exactly what OpPrime reported in the discussion
("crowded neighbourhoods seem particularly difficult"). I over-read the earlier number.
NO CHEAP PROXY PICKS THE RIGHT NODE EITHER, measured on the same 37:
* track length: the scorer's node is in the SHORTER track 23 times of 37 (median 52 vs our 61), so
  preferring longer tracks makes it WORSE;
* trajectory smoothness (deviation from the midpoint of predecessor and successor): 16 vs 13, and
  the medians are identical at 0.81 um. A coin flip.
* degree: both nodes have in-degree 1 and out-degree 1 in 36 of 37.
The ONLY quantity that separates them is distance to the true cell centre, which is image
information. That points at the DeepCenter centre prior, which the pipeline already computes for its
vetoes - but it is a real re-assignment problem (one-to-one constraint), not a per-edge snap, and it
must be validated on the box replay before a slot.
WHAT THIS MEANS FOR ddsr: its +6 TP is real and measured, but it comes from the short-track rescue
and from pruning isolated nodes, NOT from the mechanism it was named for. Its other half, -1,126
nodes against the signed node-count penalty, is unaffected by this correction.

## !!!! 09-25: THE SLOT-FREE LOOP IS BUILT, AND SWEEP 1 IS A HARD NEGATIVE !!!!

### THE LOOP
`ops/box_sweep.py` (on the box as `~/biohub/box_sweep.py`) replays cell-5 post-processing from the
CACHED RAW ILP GEFFS of the real 0.954 run, for any set of env overrides; `~/biohub/box_score.py`
scores the result against the 2,127-edge ground truth of the four scored movies.
VERIFIED EXACT: the replay reproduces the real Kaggle run - J=0.95722, TP=2036, FP=0, FN=91,
122,863 nodes, and per movie 6bba_05b6850b 6158 nodes / 5962 edges.
COST: the first config on a movie is ~4 minutes (DeepCenter heatmaps, 8-view TTA); every config
after that is **4 seconds**, because the heatmaps memoise inside the process. Four movies run in
parallel. So a 10-config sweep is ~10 minutes of wall clock and ZERO Kaggle slots.
Run it with `~/biohub/run_sweep1.sh` as the template; python is `~/biohub/hoct_venv/bin/python`
(the `.venv` has no pandas). `SWEEP_NB=<notebook>` swaps the body under test.

### SWEEP 1: TEN POST-PROCESSING CONFIGS, ALL FOUR MOVIES, 2,127 GT EDGES
| config | J | TP | FP | FN | nodes | read |
|--------|------:|----:|---:|---:|------:|------|
| base | 0.95722 | 2036 | 0 | 91 | 122,863 | the 0.954 body |
| **rescue** | **0.95910** | **2040** | 0 | 87 | 123,250 | **the only config that adds TPs: +4** |
| rescueP80 | 0.95910 | 2040 | 0 | 87 | 123,277 | same 4 edges, more nodes |
| rescueBig | 0.95910 | 2040 | 0 | 87 | 123,571 | same 4 edges, +708 nodes |
| rescueLen3 | 0.95910 | 2040 | 0 | 87 | 123,252 | same 4 edges |
| relaxed9 | 0.95722 | 2036 | 0 | 91 | **122,691** | identical edges, **-172 nodes** |
| tight575 | 0.95722 | 2036 | 0 | 91 | 122,861 | identical edges |
| dcgap15 | 0.95722 | 2036 | 0 | 91 | 122,978 | identical edges, +115 nodes |
| tight625 | 0.95675 | 2035 | 0 | 92 | 122,876 | -1 TP |
| relaxed12 | 0.95628 | 2034 | 0 | 93 | 123,196 | -2 TP |
(mtl4, mtl5, gap58, gap65 FAILED: cell 1's drift guard pins OUTPUT_MIN_TRACK_LEN and GAP_CLOSE_UM,
so box_sweep must move the guard too, exactly as build_x138.py does. Fix before sweep 2.)

**THE RESULT: of ten post-processing knobs, ONE moves a single scored edge.** The short-track
rescue adds 4 TPs; all four of its variants add the SAME 4, so the extra rescue knobs buy nothing
and plain `rescue` is the cheapest in nodes. Everything else is bit-identical on the annotated
tracks or actively worse. On 6bba_05b6850b alone, all ten configs gave byte-identical TP/FP/FN
(829/0/16) while the node count moved over a 1.4% range.
**This is why the board has been pinned at 0.953-0.954 through every knob we have tried.** The
annotated cells sit in easy, well-tracked regions; these knobs only rearrange the unannotated
majority. The post-processing knob space is exhausted on the scored edges, and we now know that
without spending a slot to learn it.
WHAT REMAINS USEFUL IN IT: since J is provably invariant to several knobs, the only thing they can
change on the board is the NODE COUNT, and the penalty is signed and uncapped. relaxed9 gives
-172 nodes at identical edges. That is only -0.14%, worth about +0.0001, i.e. under board
resolution on its own - but it is free and composes.

### THE ARM THAT DID COME OUT OF THIS: CO-LOCATED NODE DE-DUPLICATION (`v_ddsr`)
The measured error structure says where to aim: 2,036 TP, **zero FP anywhere**, 91 FN. Of the 91,
66 are linking failures, and **37 of the 58 "linked elsewhere" cases link to a node that is itself
within 7 um of the correct target** - a second detection of the same cell that lost the scorer's
per-timepoint assignment. The tracker picked the right CELL and the wrong NODE.
Merging co-located detections, composed on top of the rescue, measured offline:
  base 0.95722  ->  +rescue 0.95910  ->  **+dedup(5.0 um) 0.96004**, and nodes **-1.22%**.
Both terms move the right way, since the node penalty is signed.
THE TRAP, and why the out-degree cap in the block is not optional: rewiring naively lets two merged
sources each keep their own successor, which took divisions 79 -> 656 and inflated J to 0.96192 by
giving every source two chances at the right target. Our annotation is far too sparse to see the
false-positive cost of that, so it is not a real gain. With the cap, a merged source keeps one
outgoing edge unless it was genuinely a division before the merge.
Radius is a real optimum, not a monotone: 4.0 -> 0.95957, **5.0 -> 0.96004**, 5.5 -> 0.95675.
Built by `scratch_kernels/build_dedup.py` (block in `scratch_kernels/_dedup_block.py`), verified
IN-KERNEL by the box replay before any slot was spent: on 6bba_05b6850b the kernel's own
`ARM_DEDUP` line reports merged=14, nodes 6185->6171, matching the offline simulator's 15 on that
movie.

## !!!! 09-24 TWO ERRORS OF MINE, BOTH NOW FIXED, BOTH EXPENSIVE !!!!

### ERROR 1: THE V1284 HEAD IS PUBLIC. IT ALWAYS WAS. THIS COST YESTERDAY'S FIVE SLOTS.
`anvithpothula/biohub-v1284-head-s075` - 30 KB, 153 downloads, 4 votes, listed by
`kaggle datasets list -s v1284` and it downloads on our account.
I recorded it as private and built all five 09-24 arms around REPLACING it with our sub-voxel
refinement. Those arms scored 0.945-0.951 against our own 0.954.
**HOW THE ERROR HAPPENED, so it is not repeated:** `kaggle kernels pull -m` returns x138's
`dataset_sources` as `['', 'pilkwang/...deepcenter...', 'pilkwang/...temporal...', 'pilkwang/...50ep...']`.
The FIRST ENTRY IS AN EMPTY STRING - the CLI blanks that slot - and I read the blank as a redacted
private dataset instead of looking it up. **RULE: never conclude an artefact is unavailable from a
blank in a metadata dump. Run `kaggle datasets list -s <slug>` first.**
ACTION TAKEN: `v_xpub` = the x138 notebook VERBATIM with the real V1284 head mounted, queued to run.
That is the configuration its author scored **0.956** with, i.e. two ticks above our 0.954.

### ERROR 2: WE HAD GROUND TRUTH FOR ONLY 4.7% OF THE SCORED EDGE WEIGHT, ON THE WRONG EMBRYO
The four scored test movies are byte-identical to four TRAIN movies - the project has known that for
weeks and used it for exact replay. What nobody checked is that this means **their GROUND TRUTH is
in the train split too**. `data/manifest.json` says so plainly: each of the four appears under
`split: train` with 21 geff files. We had downloaded the two 44b6 ones and never the two 6bba ones.
DOWNLOADED NOW (21 files each, ~15 KB) into `data/train/6bba_05b6850b.geff` and
`data/train/6bba_05db0fb1.geff`. Loaded and counted:
| scored movie | GT nodes | GT edges | dt==1 edges | GT divisions |
|--------------|---------:|---------:|------------:|-------------:|
| 44b6_0113de3b | 52 | 50 | 50 | 0 |
| 44b6_0b24845f | 51 | 49 | 49 | 0 |
| **6bba_05b6850b** | **861** | **845** | **845** | **0** |
| **6bba_05db0fb1** | **1,229** | **1,183** | **1,183** | **3** |
| **TOTAL** | **2,193** | **2,127** | **2,127** | **3** |
**The two movies we had no ground truth for carry 2,028 of the 2,127 GT edges - 95.3% of the weight.**
Every local measurement this project has ever made ran on 99 edges, 4.7% of the real weight, on the
embryo that barely matters. That is the true reason the offline screens never tracked the board, on
top of the in-sample memorisation Eric documented.
**THE STANDING RULE "local in-sample scoring is useless, 1 GT edge is worth 28 board ticks" IS NOW
OBSOLETE.** With 2,127 paired GT edges on the exact scored movies, one edge is worth about 1.3 board
ticks, and for PAIRED comparisons (same movies, same detections, only the config differs) almost all
the variance cancels. Per the discussion, post-processing settings chosen locally DO carry to the
board, even though trained-model rankings do not - so this validator is admissible for exactly the
kind of arm we keep spending slots on.

### AND IT SETTLES THE DIVISION QUESTION OUTRIGHT
**The four scored movies contain THREE annotated divisions. We write 79.**
divJ = TP/(P + N - TP) with N = 3 and TP <= 3, so on the visible movies divJ <= 3/(79+3-3) = 0.038
no matter what we do, and every division we add makes the denominator worse. That is the complete
explanation of all five 09-24 results at once:
* loosening gates (xsvdv 98 div, xsvdc 125 div) adds FPs to a term that is already nearly all FP -> loses
* tightening (xsvd 50 div) removes some FPs but breaks edges elsewhere -> loses more
* and the earlier break-even algebra assumed N ~ 100-150. **N is 3.** The whole "0.08 unclaimed in
  the division term" estimate, which came from a public account's inference on a DIFFERENT body,
  does not describe the movies we are actually scored on.
**THE DIVISION AXIS IS CLOSED, arithmetically, not empirically.** Do not spend another slot on it.
Do not submit t6dc / t6dv / t6dd / t6wz. (t6sr stays, for determinism, not for divisions.)
CAVEAT WORTH KEEPING: the public LB is 29% of the test set. If the hidden 71% is annotated more
densely for divisions, the term could matter there - but we cannot see it, and nothing we can
measure supports spending slots on it.

## !!!! 09-24: READ THE COMPETITION DISCUSSION. IT CHANGES THE PLAN. !!!!
Read via the in-app browser (Kaggle discussion pages are JS-rendered; `get_page_text` after a 5s
wait works, the CLI has no discussions endpoint). The threads that matter, with ranks, because rank
is the only calibration we have on who to believe:

### 1. WHY OUR OFFLINE PROXIES ARE INVERTED - ROOT CAUSE, CONFIRMED BY ANOTHER COMPETITOR
Eric (rank 124), discussion/742064: he opened `split_manifest.json` inside the public secondary model
(pilkwang/biohub-temporal-unet3d-seed314159-v1) and found the method is
`unet_transformer_alltrain_seed314159_v1` and **the train list contains all 199 videos**; the 40
"test" videos in that manifest are a SUBSET of them. The DeepCenter manifest lists 71 train videos.
=> **Any local hold-out drawn from the 199 train videos is IN-SAMPLE for the public detectors.**
Steps that correct detector errors look good locally because the detector has memorised those
videos, so there is nothing left to correct. His own counter-example: a sub-voxel peak refinement
gained **+0.0078** on the 12 official validation videos with divisions and **-0.002 on the LB**,
consistently over two submissions.
This is the mechanism behind every "the proxy is inverted" observation we and two other accounts
have recorded. It is not noise, it is memorisation. NOTE FOR US: our own sub-voxel refinement went
the other way (+0.005 on the BOARD), so ours was a genuine gain, not the same artefact.

### 2. WHAT ACTUALLY MOVES THE SCORE, FROM SOMEONE WHO SPENT THREE WEEKS ON THE MODEL SIDE
hikaggler (rank ~400, own pipeline 0.939), discussion/741749. Measured one variable at a time on a
24-video hold-out stratified across both lineages, paired SE ~0.006.
**DID NOT MOVE**: deeper/wider U-Net (inflates node count and loses on the N_pred term); longer
training 60 -> 131 epochs (edge Jaccard up, node-count term eats it); strong augmentation, Gaussian
heatmap loss, local-softmax peak loss; wider temporal window 2 -> 9 frames (recovers ~0.1% of GT
nodes); **a trained division head** (local divJ 0.07 -> 0.19 but **+-0.001 on the LB**);
post-processing knobs (saturated, same as the public sweeps).
**DID MOVE**: **pretraining on the public CC0 synthetic dataset, +0.012 to +0.018 over from-scratch.
"This was the only big lever I found."** Also conditional two-model fusion (use the second model only
where the primary is uncertain); plain averaging does nothing.
Details he gave: the CC0 set is the output of José Freitas's `biohub-synthetic-dataset` notebook,
1,539 static volumes and 2,174 time sequences. He used only 497 of the sequences for 80 epochs, then
fine-tuned on 175 real videos for 60 epochs: hold-out 0.9146 -> 0.9269. Repeating with ALL 2,174 at
the same gradient-step count came out **worse** (adj -0.005). **What helps is SOME of that data, not
more of it.** Caveats he states: it pushes node count up, so part of the gain is paid back through
N_pred, and it buys nothing on divisions because the generator does not model mitosis over time.
* His division ablation: turning division creation off cost him 0.022, so his divJ is about 0.22.
  That independently matches rogerrogerroger3r's 0.020 / divJ ~0.20 and our own working estimate.
* **"Node-count calibration predicted my LB movement far better than missed detections did. I can
  change recall by a point and the LB does not react, while the N_pred ratio term shows up every
  time."** Same message from Justin CH123 (rank 88): ten single-knob changes, all lost, and the loss
  tracked the change in predicted NODE COUNT, not the offline score. A change that moved the node
  count by four nodes still lost 0.001.
* **"Post-processing settings chosen locally DO carry over to the LB, but the local ranking of two
  TRAINED MODELS does not."**

### 3. FROM THE TOP OF THE BOARD
Ogurtsov (**rank 6, 0.968**) answered hikaggler's direct question - is the remaining 0.018 reachable
from the published U-Net + transformer + ILP at all, or have people up there replaced it?
**"It's reachable to some extent but pretty risky."** Asked to clarify, he said his concern is the
PRIVATE leaderboard, not training stability. Elsewhere: "I guess you have some room for improvement
in all directions." A competitor quoting a 0.969 team: **"you can't just be lazy and improve one
thing, you have to improve all parts."**

### 4. THE GROUND TRUTH ITSELF HAS ERRORS
Quantizr (rank 56, 0.956 in only 5 submissions), discussion/742942, posted 6 hours ago: centroids
that are not within 7 um of the correctly linked cell, links that are simply wrong, and an annotated
"division" where the blue daughter is visibly present in earlier frames. "I just hope the test set
isn't annotated this badly... but that might explain why some models which I think should do worse on
manually annotated data seem to do better on the actual test set."
=> A hard ceiling we cannot move, and another reason local scoring misleads.

### 5. THE ACTIONABLE FIND: A PUBLIC SYNTHETIC-PRETRAINED MODEL THAT IS A VERIFIED DROP-IN
Since synthetic pretraining is the one lever anyone reports working and we cannot train one in the
time left, I searched for a published one. `kaggle datasets list -s "biohub synthetic"`:
* **bhpepper/biohub-synthetic-5fold-ensemble-v1** (46 MB): 5 fold checkpoints plus a 5-fold SWA,
  "Stage 2 Synthetic Fine-Tuning", ensemble_summary reports mean proxy 0.9672 / mean recall 0.9679.
* daifanhao/biohub-synthetic-detector-pretrain-public-v1: its manifest shows 12 epochs in **26
  seconds**. That is a toy. Ignore it.
**VERIFIED LOCALLY AGAINST OUR OWN WEIGHTS** (`scratch_kernels/_synth/synthetic_5fold_swa.pth` vs
`scratch_kernels/_ckpt/ftgc0/edge_predictor_best.pth`): **136 state-dict keys in each, identical
sets, every shape identical, zero mismatches**, and mean |delta| over the shared float tensors is
**0.98** (max 35.2), so it is a true drop-in AND a genuinely different model rather than a re-upload.
The key names (`unet.encoder_blocks.*`, `transformer.pair_mlp.*`) confirm it is the same
UNet + transformer that does BOTH detection and edge scoring in our pipeline.
BUILT AND RUNNING as `synp` (`scratch_kernels/build_synprim.py`, swap mechanism lifted verbatim from
our own prim300 arm, which is the only place in this project that has safely repointed
WEIGHTS_RELATIVE). The kernel re-verifies keys, shapes and a non-zero delta AT RUNTIME and raises
rather than silently running the wrong weights. bhpepper ships no config.json; we use the support
pack's own, which is correct precisely because the state dicts match key for key.
**HONEST PRIOR, STATE IT BEFORE THE SCORE LANDS**: bhpepper themselves are **rank 154 at 0.950,
four ticks BELOW us**, and our own prim300 (a different public primary, no synthetic pretraining)
lost 4 ticks. What makes this worth a slot is the training REGIME, which is the only thing the
discussion says moves the board, not the author's standing.

### 6. WHAT THE DISCUSSION CLOSES FOR US
* A trained division head is NOT worth building: someone did it, local divJ 0.07 -> 0.19, LB +-0.001.
  Combined with our own five division submissions all losing, **the division axis is now closed from
  both directions and by two independent accounts.**
* Deeper/wider/longer-trained detectors are not worth the V100 time: all measured neutral or
  negative, and all lose through the node-count term.
* Node count is the single most predictive quantity for board movement. Any future arm should be
  judged first on how many nodes it writes.

## !!!! 09-24 FINAL: ALL FIVE SUBMISSIONS LOST. THE MERGED BODY IS ABANDONED. !!!!
| arm | divisions | what changed | public LB | vs xsv | vs our 0.954 |
|-----|----------:|--------------|----------:|-------:|-------------:|
| xsvd | 50 | sister symmetry 0.6 -> 0.4 (STRICTER, pool unchanged) | **0.945** | -0.006 | **-0.009** |
| xsvdv | 98 | DIVERGE 2.25 -> 1.50 (LOOSER, pool 610 -> 1061) | **0.946** | -0.005 | **-0.008** |
| xsvdc | 125 | DeepCenter veto 0.25 -> 0.15 (LOOSER, pool unchanged) | **0.950** | -0.001 | **-0.004** |
| **xsv** | 73 | the merged x138 body + our sub-voxel refinement | **0.951** | 0 | **-0.003** |
| xsvf | 76 | xsv + lcefr | **0.951** | 0 | **-0.003** |
| (ours) | 79 | **t6stk3 / t6r70 / t65s3** | **0.954** | +0.003 | 0 |

### 1. THE MERGED BODY LOSES. STOP WORKING ON IT.
x138 scores 0.956 on ITS OWN account WITH its private V1284 learned coordinate head. Swap that head
for our sub-voxel refinement and it scores 0.951. Our own body scores 0.954. So the entire
flow + readmit + gapfill stack, which is what x138 adds over the common ancestor, is worth NOTHING
to us once our own localization work is in place - and it costs three ticks.
Note the coincidence that makes this crisp: our OLD `hsg200` body (hfusion + sub-voxel refinement,
no flow, no readmit, no gapfill, no linker stack) also scored exactly **0.951**. Two completely
different recall stacks, same score. What took us from 0.951 to 0.954 was our own linker stack
(velocity 0.25 + bonus 1.6 + lcefr + TIGHT 6.0), and on the merged body that stack is inoperative
because the flow prior replaces the motion model those knobs tune - it fires on 198 of 198 frames.

### 2. THE DIVISION COUNT IS NOT THE VARIABLE. THE CANDIDATE POOL IS.
Read the table by count and it looks incoherent: 98 divisions scores WORSE (0.946) than 125
divisions (0.950). Read it by MECHANISM and it is clean:
* `xsvdv` widens the geometric candidate POOL, 610 -> 1061, and loses **5 ticks**.
* `xsvdc` leaves the pool at 610 and only lets more of the SAME candidates past the veto, and loses
  **1 tick** despite writing 27 MORE divisions than xsvdv.
* `xsvd` narrows nothing and only tightens symmetry, cutting the pool's survivors to 50, and loses
  **6 ticks**.
=> **The divergence gate is rejecting genuinely bad candidates and must not be loosened.** The
DeepCenter veto threshold is roughly neutral in both directions. The division count on this lineage
is already at its optimum somewhere near 73-79, and BOTH directions away from it cost score.

### 3. MY OWN BREAK-EVEN PREDICTION WAS WRONG, AND THIS IS WHY
I derived that adding divisions raises divJ whenever their precision exceeds divJ/(1+divJ) = 16.7%,
and concluded the recall direction was favoured. The algebra is right; the model of the COST is not.
I modelled an added division as adding exactly one edge. It does more than that: the safe-division
repair re-parents a node that the tracker had already assigned, so a wrong division can simultaneously
create a false edge AND destroy a true one, which is twice the adjEJ damage per error, and it also
perturbs the per-timepoint bipartite matching that decides which predicted nodes match GT at all.
**LESSON FOR EVERY FUTURE METRIC ARGUMENT ON THIS PROJECT: a term-level derivation that ignores how
a change couples into the OTHER term is not evidence, it is a hypothesis.** The board is the judge.

### 4. WHAT THIS LEAVES
Our 0.954 body is the main line and has now survived every challenger. Everything tried on it since
09-22 returns 0.953 or 0.954. Five arms are running on it (t6dc, t6dv, t6wz, t6dd, t6sr) carrying
the division knobs across from the merged body, but the merged-body evidence above says to expect
them to be flat-to-negative - EXCEPT `t6sr`, which is about determinism rather than score (see the
trigger-margin section below).

## !!!! 09-24 09:30Z FIRST SCORE IS IN: **xsv = 0.951**. THE MERGED BODY LOSES BY 3 TICKS. !!!!
`xsv` (the public x138 body + our sub-voxel refinement) scored **0.951** against our own
**t6stk3 = 0.954**. x138 scores 0.956 on ITS OWN account, so the three ticks are the price of
swapping its private V1284 learned coordinate head for our sub-voxel block, plus whatever our own
stack (velocity 0.25, bonus 1.6, tight 6.0, lcefr) was worth that the flow prior does not replace.
WHAT THIS DOES AND DOES NOT CLOSE:
* It does NOT say flow / readmit / gapfill are bad. It says THIS combination is 3 ticks worse than
  the body we already had, and that our localization stack is not a drop-in substitute for V1284
  on their body. We measured the mechanism for that earlier: on the merged body the refinement
  moves only 63 links (0.05%), because the flow prior swamps a 0.4 um coordinate correction, AND
  it COSTS 11 divisions (xsv 73 vs xbase 84).
* **OUR OWN 0.954 BODY IS THE MAIN LINE AGAIN.** The four other 09-24 submissions (xsvf, xsvdv,
  xsvdc, xsvd) are still pending and are deltas ON 0.951 - their SIGN is what transfers, because
  `add_safe_divisions_postlink` and every gate it calls are byte-identical between the two bodies.
PIVOT EXECUTED 09:34Z, five arms running on OUR body (`ops/plan_ourdiv.json`, no slots spent):
`t6dc` (DeepCenter veto 0.15 - the largest division mover measured anywhere), `t6dv` (DIVERGE 1.50),
`t6wz` (DeepCenter score window WIN_Z 2 - the cheapest, +5 divisions for ZERO nodes on the merged
body), `t6dd` (both gates), `t6sr` (rescue armed).

### !!! A LATENT RISK IN OUR ACTUAL FINAL PICK: t6stk3 IS 0.64 POINTS FROM A BEHAVIOUR CHANGE !!!
The adaptive short-track rescue is fenced behind `removed_frac >= SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC`,
which defaults to 0.10 and which NOBODY on this lineage sets. Read the code: the denominator is
`len(nodes_by_id)` BEFORE the removal is applied, so removed_frac = removed / (kept + removed).
Measured on our own 0.954 run:
| movie | removed | before | removed_frac | margin to the 0.10 trigger |
|-------|--------:|-------:|-------------:|---------------------------:|
| 44b6_0113de3b | 276 | 25,893 | 0.0107 | +0.0893 |
| **44b6_0b24845f** | **2,137** | **22,824** | **0.0936** | **+0.0064** |
| 6bba_05b6850b | 176 | 6,334 | 0.0278 | +0.0722 |
| 6bba_05db0fb1 | 745 | 71,146 | 0.0105 | +0.0895 |
**t6stk3 - the arm we currently intend to select as Final A - sits 0.64 percentage points below a
threshold that switches on a block which has never executed in any run we have ever scored.** If
the private rerun's detection differs even slightly on that one movie, the rescue arms itself and
puts back up to 120 nodes per dataset in an output we have never seen a score for.
That is an argument for shipping `t6sr` (trigger 0.0, rescue always on) REGARDLESS of whether it
scores above or below 0.954: it converts an untested conditional branch into a tested unconditional
one. On the merged body arming it restored 81 components / 355 nodes / 274 edges and touched ZERO
divisions, and the offline replay predicted that within 6% before the arm was built.

## STATE AT 2026-09-24 ~08:00Z (read this first)
SLOTS: **all 5 of 09-24 used**, and ALL FIVE ARE STILL PENDING five hours after the first one.
| ref | time | arm | divisions |
|-----|------|-----|----------:|
| 56510298 | 03:17Z | **xsv** (the merged x138 body + our sub-voxel refinement) | 73 |
| 56510498 | 03:27Z | xsvf (+ lcefr) | 76 |
| 56511289 | 04:09Z | xsvdv (DIVERGE 1.50) | 98 |
| 56511403 | 04:15Z | xsvdc (DeepCenter veto 0.15) | 125 |
| 56512153 | 04:58Z | xsvd (sister symmetry 0.4) | 50 |
The delay is NOT a platform outage: a fresh leaderboard pull shows other teams' best submissions
dated as late as 06:42Z today, so the scorer is alive. The most likely cause is that Kaggle re-runs
a submitted kernel and our 19 same-day GPU runs competed with our own re-runs for the account's GPU
allocation. LESSON: do not saturate GPU with --no-submit runs while submissions are queued.
`ops/watch_scores.sh` is running; `grep -E "^5651" ops/scores.log` is the check.
ARMS: **20 built, 19 run, all gated** (xsvmax pushed 07:54Z). Nothing is waiting on compute.
THE DECISION TREE, pre-registered so the scores are acted on and not re-litigated:
* **xsvdc (125) > xsv (73)** -> recall wins. Submit `xsvd10` (147) and `xsvmax` (168 + rescue).
* **xsvdc < xsv AND xsvd (50) > xsv** -> precision wins. Submit `xsvdu` (32), then `xsvd`-stacks.
* **both below xsv** -> the division count is already at its optimum on this body. Move the slots to
  `xsvsr` (the rescue, which touches zero divisions) and `xsvp26` (the publicly-paid-for pair).
* **xsv itself below 0.954** -> the merged body loses; re-test the same division deltas on OUR body,
  since add_safe_divisions_postlink is byte-identical there.
!! TEAM: four members (akkigupta2005, arunendratripathi03, eeshsaxena, swapiy) can all submit and
can all change the two final picks; the 5/day limit is TEAM-WIDE. The user still needs to tell them
not to touch either. FINAL PICKS AS THEY STAND: A = t6stk3 (0.954, submission 56467741),
B = t6r70 (0.954, genuinely different output). Revise as the merged arms score.

### RESUME COMMANDS (background runners die with the session; restart them, they are idempotent)
```
cd C:/Users/eeshs/Downloads/biohub-cell-tracking
bash ops/getlog.sh <tag> 6                                # retry until the .log downloads
python ops/run_today.py ops/plan_<tag>.json --submit-only  # gate + submit one arm
python ops/run_today.py ops/plan_XXXX.json --no-submit     # run arms, spends GPU but NO slot
bash ops/watch_scores.sh 240 &                            # appends scored rows to ops/scores.log
grep -E "^5651" ops/scores.log                            # today's scores as they land
```
A restarted run_today re-reads the sentinels in `ops/state/`, so an arm already PUSHED goes straight
back into the in-flight set and an arm already SUBMITTED is skipped. Nothing is double-submitted.

### THE COMPLETE ARM TABLE, MEASURED (09-24; 20 arms, all one knob from xsv unless noted)
| arm | change from xsv | divisions | nodes | edges | dNodes | dEdges |
|-----|-----------------|----------:|------:|------:|-------:|-------:|
| xsvdu | DIVERGE 2.25 -> **4.0** (stricter, the public sweep peak) | **32** | 124,126 | 119,832 | -18 | -55 |
| xsvd | sister symmetry 0.6 -> 0.4 | 50 | 124,135 | 119,857 | -9 | -30 |
| xsvt | TIGHT 6.0 | 70 | 124,174 | 119,924 | +30 | +37 |
| xsvb | learned bonus 1.6 | 72 | 124,143 | 119,894 | -1 | +7 |
| **xsv** | (the merged body) | **73** | 124,144 | 119,887 | 0 | 0 |
| xsvsr | short-track rescue ARMED | 73 | **124,499** | 120,161 | **+355** | +274 |
| xsv96 | DET 0.96 | 74 | **124,564** | 120,297 | **+420** | +410 |
| xsvmp | parent cap 9.0 -> 10.5 | 75 | 124,149 | 119,893 | +5 | +6 |
| xsvf | + lcefr | 76 | 124,216 | 119,982 | +72 | +95 |
| xbase | NO coordinate refinement | 84 | 124,246 | 120,038 | +102 | +151 |
| xsvdv | DIVERGE 2.25 -> 1.50 | 98 | 124,161 | 119,925 | +17 | +38 |
| xsvdc | DeepCenter veto 0.25 -> 0.15 | 125 | 124,203 | 119,985 | +59 | +98 |
| xsvd10 | DeepCenter veto 0.25 -> 0.10 | 147 | 124,221 | 120,021 | +77 | +134 |
| xsvdd | DIVERGE 1.50 **and** veto 0.15 | 168 | 124,224 | 120,044 | +80 | +157 |
| xsvwz | DeepCenter score window WIN_Z 1 -> 2 | **78** | 124,144 | 119,895 | **+0** | +8 |
| xsvmx | parent cap 9.0 -> 11.0 | 75 | 124,149 | 119,893 | +5 | +6 |
| xsvgc | GAP_CLOSE_UM 5.0 -> 5.8 | 72 | 124,157 | 119,906 | +13 | +19 |
| xsvp26 | GAP 5.8 + DeepCenter veto 0.26 (the publicly-paid-for pair) | 68 | 124,157 | 119,902 | +13 | +15 |
| xsvmax | xsvdd **and** the rescue armed | (running 07:54Z) | | | | |

THINGS THIS TABLE SETTLES WITHOUT SPENDING A SLOT:
1. **THE DEEPCENTER VETO IS THE BINDING GATE, NOT THE DISTANCE CAPS.** `xsvmp` widens the parent cap
   9.0 -> 10.5 and the candidate pool jumps 610 -> 792 (+30%), but divisions written move only
   73 -> 75: the veto eats essentially every new candidate. The sister cap is already wide enough to
   admit every real division (public: GT sister separations reach 13.7 um against a 14.0 cap). So
   **the distance-cap family is CLOSED** - widening it just feeds the veto more work. The gates that
   actually move the pool are the VETO (xsvdc / xsvd10) and DIVERGENCE (610 -> 1,061 loose,
   610 -> 203 strict).
2. **DIVISIONS ARE CHEAP IN NODES.** xsvdd buys 95 extra divisions for +80 nodes and +157 edges.
3. **xsv96 IS A SLOT-WASTER**: the only arm that moves node count materially (+0.34%) and it buys
   one division, on top of the rank-57 team's own logged sweep (0.96 -> 0.937, 0.95 -> 0.937).
4. **xsvb AND xsvt ARE DEAD**: 72 and 70 divisions against 73, node counts within 30. Pure
   re-ranking is inert on this body, as it was on ours.
5. **xsvwz IS THE CHEAPEST DIVISION GAIN IN THE TABLE**: widening the DeepCenter SCORE WINDOW in z
   (WIN_Z 1 -> 2, i.e. take the centre-prior score over an isotropic neighbourhood instead of one
   z slice) raises acceptances 161 -> 183 and divisions 73 -> 78 for **zero extra nodes** and +8
   edges. It loosens the same binding veto as xsvdc but through the SCORE rather than the
   threshold, so the two are stackable if recall wins.
6. **THE PUBLICLY-PAID-FOR PAIR DOES NOT TRANSFER**: xsvgc (GAP_CLOSE_UM 5.8 alone) moves +13 nodes
   and +19 edges - essentially inert here - and xsvp26 (the pair) CUTS divisions 73 -> 68 because
   0.26 tightens the veto. The +0.001 that pair earned publicly was on a different body, and this
   is a clean example of why single-knob transfers need re-measuring.

### THE ONE PIECE OF ALGEBRA THAT DECIDES THE DIVISION DIRECTION
divJ = TP/(TP+FP+FN) = TP/(P + N - TP), where P = divisions we write and N = ground-truth divisions
in the scored set. Add dP more of which a fraction p are correct:

    new = (TP + p*dP) / (D + dP*(1-p))   where D = P + N - TP
    it increases  <=>  p*D > TP*(1-p)  <=>  p > TP/(P+N)  <=>  p > divJ / (1 + divJ)

**The break-even precision on ADDED divisions is divJ/(1+divJ), and N cancels out entirely.**
The public measurement puts this lineage's divJ at about 0.20, so the bar is **16.7%**: adding
divisions RAISES the score as long as better than one in six is real. That is a very low bar and it
says the RECALL direction is favoured unless the veto is rejecting almost pure noise.
SIZE OF THE BET (N ~ 100, bounded below at ~30 by TP <= N against the public P=148 / divJ=0.20
reading; our P=73 -> TP ~ 29):
| precision of the 95 divisions xsvdd adds | new divJ | score change |
|---|---:|---:|
| p = 0.30 | 0.272 | **+0.0072** |
| p = 0.20 | 0.217 | +0.0017 |
| p = 0.166 (break-even) | 0.200 | 0.000 |
| p = 0.10 | 0.167 | -0.0033 |

Each added division adds ONE edge, so 95 of them is 0.08% of our 120k edges against a divJ term that
can move 7 ticks. **The asymmetry favours recall.**
THIS PARTLY CONTRADICTS the rank-57 team's note that their divergence sweep "peaked ~4.0-4.5"
(stricter). That sweep ran on a different body with different base precision, and the same author's
single-knob claims have already failed to replicate once (rogerrogerroger3r paid for the clean test
of their 0.26 claim and got a null). Both directions are in flight against the SAME body - xsvd at
50 divisions and xsvdc at 125 - so the scores settle it with data rather than authority.

### CONFIRMED LIVE: THE SHORT-TRACK RESCUE WAS DEAD CODE, AND ARMING IT WORKS
| counter (per movie) | xsv | xsvsr |
|---------------------|-----|-------|
| short_track_rescue_triggered | 0 / 0 / 0 / 0 | **1 / 1 / 1 / 1** |
| short_track_rescue_components | 0 | **22 / 28 / 4 / 27 = 81** |
| short_track_rescue_nodes | 0 | **97 / 120 / 19 / 119 = 355** |
| short_track_components_removed | 61 / 405 / 31 / 152 | 39 / 377 / 27 / 125 |
| divisions | 73 | **73 (unchanged)** |

The offline replay predicted ~86 components / ~380 nodes before the arm was built; the live run gave
81 / 355, within 6%. Divisions are untouched exactly as predicted, because a component containing a
fork is already kept unconditionally and the rescue skips anything intersecting that set.
WHAT THIS ARM IS: the filter deletes every component shorter than 6 frames; the rescue puts back the
length-4-5 ones whose mean LEARNED edge probability is >= 0.88 and whose mean edge is <= 3.0 um,
ranked and capped at 120 nodes per movie. A SELECTIVE, confidence-ranked undo of ~13% of the
deletions - not the blunt minimum-track-length move the public write-ups have shown to be a trap.
Break-even is roughly p = 0.55-0.6 on the 274 restored edges. The SECOND reason to ship it stands on
its own: 44b6_0b24845f removes 7.7% of its nodes against a 0.10 trigger, so a hidden rerun with
slightly worse detection would arm this block on that movie ALONE. Every submission we have made so
far carries that undeclared conditional behaviour; arming it makes the kernel deterministic.

### INSURANCE: THE SAME DIVISION QUESTION, PRE-BUILT ON OUR OWN 0.954 BODY
`add_safe_divisions_postlink` and every gate it calls are byte-identical between v_t6stk3 and the
merged x138 body, so a division-gate delta measured on one is at least a hypothesis on the other.
Built with the new `scratch_kernels/build_ourdiv.py` (env-only arms on v_t6stk3; it also moves the
cell-1 drift guard and appends the same runtime ARM_XENV identity line):
`t6dv` (DIVERGE 1.50), `t6dc` (DeepCenter veto 0.15), `t6dd` (both).
BUILT AND GATED BUT DELIBERATELY NOT PUSHED - they are only needed if xsv loses to 0.954, and 19
same-day GPU runs are the most likely reason five submissions sat in PENDING for five hours, so
adding three more while those re-runs are queued would make the wait worse.
Their gate entries inherit t6stk3's four stack markers plus lcefr unchanged, so those pin the BODY
while ARM_XENV pins the knob. Verified: the real t6stk3 log passes as t6stk3 and FAILS as t6dv.

## !!!! 2026-09-24: THE PUBLIC NOTEBOOKS ABOVE US ARE THE LEVER. PORTING x138 / frontier947. !!!!
BOARD NOW: we are **rank 83 of 3868 at 0.954** (team "The Originals", 151 subs). Top = 0.975 (Sergio Alvarez),
0.973 yu4u, 0.970 Tang. Distribution: 2 teams >= 0.975, 6 >= 0.970, 12 >= 0.965, 23 >= 0.960, 58 >= 0.955,
261 >= 0.950, 1015 in the 0.945 bucket (the old public plateau). Gold is about rank 17 (~0.966), silver ~rank 193,
so we are ALREADY in silver and 12-13 ticks short of gold. t65s3 came back **0.954** (tie), so the relink gate is
flat at 6.0/6.5 inside the stack too.

### THE FIND: public notebooks from teams ABOVE us, with mechanisms we have never run
Cross-referenced every public notebook author against the top-150 of the leaderboard:
| author | rank | LB | notebooks |
|--------|------|----|-----------|
| **thtennant** | **32** | **0.959** | ELEVEN `biohub-frontier947-*` notebooks = a full public ABLATION LADDER (fast, det096, tight60, flow2, readmit, gapfill, **divprec**) |
| **anvithpothula** | **57** | **0.956** | `biohub-x138`, which credits `agent/frontier943_flow`, `agent/frontier947_readmit`, `agent/frontier947_gapfill` (so thtennant is the ORIGINAL source and x138 is a port of it) |
| andrey4522 | 53 | 0.956 | biohub-harmonic-fusion-v3-raunak |
| rogerrogerroger3r | 77 | 0.954 | biohub-run91 / run92 |
| zhincez | 103 | 0.952 | `a-dividing-nucleus-gets-smaller-not-dimmer`, `label-eda-two-embryos-151-divisions-199-films` |
Public notebooks by authors BELOW the plateau, checked and DEPRIORITISED: kunaldesale2408 **0.942** (his v5
second-pass division repair did not pay), amanatar 0.948, flexonafft 0.947, pilkwang 0.949. Their new mechanisms
(leaf-prune, second-pass div repair, extended ppsweep) all sit at or under 0.947, so they are not the lever.

### WHAT x138 HAS THAT WE DO NOT (all three are node-RECALL / MOTION, i.e. orthogonal to our localization work)
1. **Neighbourhood-flow motion relink** (`FLOW_MODE=seed`, k=12, radius 40 um, exclude 1.5 um, min 4 samples,
   iter 1, flow_tight 7.0, RAW_COST 0): a tight seed pass builds a displacement field, then every source is
   re-assigned against the MEDIAN DISPLACEMENT OF ITS 12 NEAREST CONFIDENT NEIGHBOURS instead of its own last step.
   Its own seed match is excluded from its sample so a wrong seed cannot vote for itself.
   **CRUCIALLY IT ALSO WIDENS ADMISSION**: a target inside the gate of the PREDICTED position is admitted even if
   it is outside the raw gate, so a cell moving 8 um with its neighbours can compete in the tight pass. That is the
   mechanism that gets past our measured ceiling ("only 11.69% of sources have more than one candidate in the gate";
   every pure re-ranking dial we tried was inert because ~88% of links are forced).
2. **Sub-threshold readmit** (`READMIT_RADIUS_UM=4`, `MIN_SCORE=0.965`): detections the ILP discarded are put back
   when they sit within 4 um of an open track end/start.
3. **Low-detection gap filler** (`LOWDET_THRESHOLD=0.3` dump + `GAPFILL_MAX_GAP=3`, min score 0.5, step 5 um, peak
   radius 3.5 um, exclude 2 um, `ALLOW_SYNTHETIC=0`, added-node cap 3%): gaps are filled with REAL sub-threshold
   detector peaks, never invented nodes.
AND WHAT WE HAVE THAT x138 DOES NOT: the sub-voxel soft-argmax refinement (worth +0.005 on our body), lcefr,
learned bonus 1.6, tight 6.0, velocity 0.25. **x138's own coordinate refinement is a LEARNED head (`V1284`) that
needs his PRIVATE dataset `biohub-v1284-head-s075`, which we cannot mount, so the published notebook cannot run on
our account at all.** Our sub-voxel block takes exactly that slot: both refine detector coords and both keep the
coords float through `build_graph` (V1284 replaces the same `coords.astype(np.int16)` line ours does).

### THE MERGE, AND WHY IT IS SAFE (built + verified 09-24, `scratch_kernels/build_x138.py`)
Our v_t6stk3 and x138 are the SAME 12-cell notebook: 7 cells are byte-identical, all of our arm-specific work is
cell 0 (env) + cell 4 (patch blocks), and all of his is cells 0/2/3/4/5. So the merge is a splice, not a rewrite:
cells 0,1,2,3,5..11 = his; cell 4 = his with the V1284 block cut out and our sub-voxel (+ optional lcefr) block
put in its place, which is also the correct ORDER (his own comment records that V1284 had to run AFTER his
low-detection dump patch because both anchor on the same `coord_offset[t]` line).
**VERIFIED BY SIMULATION against the real support-pack `predict_unet_transformer.py`** (26,008 bytes, the same file
the kernel downloads): all 13 of his patches apply with anchor count exactly 1, and after them ALL FOUR of our
sub-voxel anchors still match exactly once, all nine lcefr anchors match their expected counts (`_lc_expected`
= [1,1,1,1,1,2,1,1,1]), and the fully patched source compiles.
ARMS BUILT AND RUNNING 09-24 (`ops/plan_0924.json`, started 02:54Z with --no-submit):
| tag | what |
|-----|------|
| **xsv** | x138 (V1284 removed) + our sub-voxel refinement. THE MAIN BET: his recall/motion stack x our localization stack. |
| **xsvf** | xsv + lcefr, so the learned edge model reads the refined float coords too. |
| **xbase** | x138 (V1284 removed), NO coordinate refinement. Control: how much of his 0.956 is the flow/readmit/gapfill stack alone. |
| **xsvb** | xsv + learned bonus 1.0 -> 1.6. Under the flow cost the raw-distance term is 0, so the bonus now competes directly against the flow residual. |

### GATE (ops/gate.py, backup ops/gate.py.bak_x138) - x138's stack DEGRADES SILENTLY, so this matters
Each x-arm must show, live: the `ARM_XFLOW` / `ARM_XRECALL` config echoes (added by our builder, cell 2), a per-
dataset `ARM_XFLOWSTATS ... flow_frames>0 flow_predicted>0` (added after the relink print in cell 5), plus his own
`Low-detection dump applied`, `LOWDET <ds>: N peaks above 0.3`, `low-detection pool: N peaks >= 0.5`,
`readmitted N discarded detections`, and `gap filler: +N nodes`.
NEW `forbid` BLOCK (this gate had no negative checks before): an x-arm FAILS if the log contains `gap filler idle`,
`LOW-DETECTION DUMP SKIPPED`, `readmit skipped (non-fatal)`, `DEADLINE: Ns since kernel start` or `REPAIR FAILED`.
Every one of those leaves a valid, plausible-looking submission that is NOT the arm we meant to test - x138's own
comments record that exact failure ("x122 v1 FAILED SILENTLY ... every movie logged 'gap filler idle'").
xbase additionally forbids `SV_ARM_HSG200`/`ARM_LCEFR`, and xsv/xsvb forbid `ARM_LCEFR`, so the arms cannot be
confused for one another. Regression tested: real t6stk3 log still GATE_PASSes as t6stk3 and fails as t65s3/xsv;
forged x-logs pass; the idle / no-flow / wrong-bonus / wrong-body variants each fail with the right message.

### xsv RAN CLEAN: ALL THREE OF x138'S MECHANISMS FIRED LIVE ON OUR ACCOUNT (09-24 03:09Z, GATE_PASS)
The merge works. Run took ~15 minutes (not hours), so the whole ladder is affordable on quota.
Measured from `data/out_xsv/run_stats.csv` against our 0.954 `data/out_t6stk3/run_stats.csv`:
| quantity | t6stk3 (0.954) | xsv |
|----------|---------------|-----|
| nodes | 122,863 | **124,144** (+1.04%) |
| edges | 118,537 | **119,887** (+1.14%) |
| divisions written | 79 | 73 |
| readmitted nodes | - | **770** (83 / 302 / 58 / 327) |
| gap-filler nodes (real sub-threshold peaks) | - | **134**, from pools of 3.4k-52k free peaks |
| flow frames / flow-predicted sources | - | **198 per movie / 103k-284k** |
| relaxed-pass edges | 2,925 | 1,335 (the flow gate pulls links into the TIGHT pass, as designed) |
The ppsweep selected `base` with no overrides on BOTH runs (`BIOHUB_VALIDATOR_ENABLE=0`), so the
comparison is clean and there is no hidden post-process confound.
WATCH THE NODE RATIO: +1.04% nodes costs about 0.001 through the adjEJ node penalty on its own, so
the recall stack has to buy back more than a tick in J before it shows as a gain.
OPS NOTE: x138 leaves `tracking_repo/` and `edge_cache/` in /kaggle/working, so `kaggle kernels
output` for these arms downloads ~45 MB and takes minutes. Budget for that in run_today timing.

### 09-24 04:58Z: ALL 5 SLOTS SPENT, AND THEY MAP THE DIVISION-COUNT CURVE
Division counts are now measured offline for the whole family, so today's five submissions are not
five guesses, they are four points on one curve plus the body test:
| arm | one change from xsv | divisions | nodes | edges | submitted |
|-----|---------------------|----------:|------:|------:|:---------:|
| **xsvd** | sister symmetry tau 0.6 -> **0.4** (STRICTER) | **50** | 124,135 | 119,857 | YES 04:58Z |
| xsvb | learned bonus 1.6 | 72 | 124,143 | 119,894 | no - inert |
| xsvt | TIGHT 6.0 | 70 | 124,174 | 119,924 | no - near-duplicate |
| **xsv** | (the merged body itself) | **73** | 124,144 | 119,887 | YES 03:17Z |
| **xsvf** | + lcefr | 76 | 124,216 | 119,982 | YES 03:27Z |
| xbase | NO coordinate refinement | 84 | 124,246 | 120,038 | no - held |
| **xsvdv** | DIVERGE 2.25 -> **1.50** (looser) | **98** | 124,161 | 119,925 | YES 04:09Z |
| **xsvdc** | DeepCenter veto 0.25 -> **0.15** (looser) | **125** | 124,203 | 119,985 | YES 04:15Z |
NOTE thtennant's `divprec` knob is a PRECISION knob, confirmed by our own counts: tau 0.6 -> 0.4
raises symmetry rejections 82 -> 110 and CUTS divisions 73 -> 50. So the name means what it says, and
xsvd is the precision end of the ladder while xsvdv/xsvdc are the recall end.
WHAT THE FIVE SCORES WILL TELL US, whatever they are: the sign and the rough optimum of the division
count on the real board, in one day, at 50 / 73 / 98 / 125 divisions against the same body. That is
the single most valuable thing the 0.1*divJ term can be made to reveal, and it is worth more than
holding a slot back for a reaction that can be made tomorrow anyway.
EXTENDED LADDER (measured, arms already run and waiting for slots):
| arm | change | divisions | nodes | edges |
|-----|--------|----------:|------:|------:|
| xsvd10 | DeepCenter veto 0.25 -> 0.10 | **147** | 124,221 | 120,021 |
| **xsvdd** | DIVERGE 1.50 **and** DeepCenter 0.15 | **168** | 124,224 | 120,044 |
THE DIVISION STACK IS SUPER-ADDITIVE IN COUNT, the same pattern that took us 0.951 -> 0.954:
base 73, +25 from xsvdv alone, +52 from xsvdc alone, and **+95 stacked** (73 -> 168). The two knobs
really do act on different gates - xsvdv raises the candidate pool 610 -> 1061 while leaving the
veto acceptance rate alone, xsvdc raises acceptance 161/449 -> 325/285 on an unchanged pool, and
stacked you get 518 accepted out of 1061. The frame and global frac caps are STILL not binding at
168 divisions (`safe_division_skipped_cap = 0` everywhere), so the ladder can go further if the
board says up.
FULL MEASURED LADDER NOW AVAILABLE, all on the same body, one knob apart: 50 (xsvd) / 70 (xsvt) /
72 (xsvb) / 73 (xsv) / 76 (xsvf) / 84 (xbase) / 98 (xsvdv) / 125 (xsvdc) / 147 (xsvd10) / 168
(xsvdd), with xsvdu (DIVERGE 4.0) still to run at the precision end.

STILL RUNNING FOR TOMORROW (no slots needed to run them): xsvdd (DIVERGE 1.50 + DC 0.15 stacked),
xsvd10 (DC 0.10), xsvwz (DeepCenter isotropic score window), xsvmx (parent cap 11.0), then xsvdu
(DIVERGE 4.0, the public sweep peak), xsvmp (parent cap 10.5, the GT-derived value), xsvsr (arms the
dead short-track rescue), xsvp26 (the only publicly-paid-for POSITIVE pair) and xsvgc (its gap half).

### FACT FOR FINAL SELECTION: THE PUBLIC LEADERBOARD IS 29% OF THE TEST SET
rogerrogerroger3r states it plainly in `one-knob-moved-twice`: "this competition scores the public
leaderboard on 29% of the test set". So every public number we have, ours included, is measured on
under a third of what the private ranking will use, and a 0.001 step is not defensible as a real
effect from one submission. That is the arithmetic behind our own rule and it strengthens it:
FOR THE TWO FINAL PICKS, take the top of the public cluster AND make the pair STRUCTURALLY
DIFFERENT, so the choice is robust to which way the 29% fell. A 0.954 body built on our own
localization stack and a merged-body arm built on flow + readmit + gapfill are exactly that kind of
pair, if the merged body earns its place.

### GATE TRAP FOUND 09-24: THE PP_CANDIDATES LIST ECHOES VALUES THAT ARE NOT LIVE
`"gap_close_um": 5.8` appears in EVERY log this pipeline produces, including runs whose live value
is 5.0, because 5.8 is one of the PP_CANDIDATES the post-process sweep DEFINES (the sweep then
selects `base` with no overrides, since BIOHUB_VALIDATOR_ENABLE=0). So a config echo is only a valid
gate marker when the value is unique in the log. Audited every marker currently in use against four
real logs: `deepcenter_safe_div_threshold` (0.25 on xsv/xsvdv/xbase, 0.15 on xsvdc),
`safe_div_max_um` (9.0), `motion_relink_tight_um` (5.5) and `det_threshold` (0.965) are each unique,
so those pins are sound. `gap_close_um` is NOT, and the xsvgc / xsvp26 entries deliberately do not
use it - their proof is the runtime ARM_XENV line.

### !!! 09-24: THE RANK-57 TEAM PUBLISHED THEIR EXPERIMENT LOG IN THEIR ENV COMMENTS !!!
`scratch_kernels/_pub0924/anvithpothula_biohub-x56/biohub-x56.ipynb` cell 0 carries anvithpothula's
own LB-measured notes beside each knob. Cross-checked against rogerrogerroger3r's paid ablations.
THIS CHANGES THE DIVISION DIRECTION AND KILLS TWO ARMS WE HAD BUILT:
* **`SAFE_DIV_DIVERGE_UM`: "larger = stricter ... kimi-v18 LB sweep peaked ~4.0-4.5."** Our `xsvdv`
  moved it the OPPOSITE way (2.25 -> 1.50, looser, +25 divisions). A public LB sweep says the peak
  is at 4.0-4.5, i.e. FEWER but higher-precision divisions. Built `xsvdu` (DIVERGE 4.0) as the
  counter-direction arm. If xsvdv reads negative, xsvdu is the immediate next submission.
* **`SAFE_DIV_MAX_UM`: "Ground-truth parent-daughter links reach 10.4um; a 7um cap rejected ~25% of
  real links."** So the shipped 9.0 still clips real divisions, and anything above ~10.5 adds
  nothing. Built `xsvmp` (10.5) and RETIRED `xsvmx` (11.0) as the worse-chosen value.
* **`SAFE_DIV_SISTER_MAX_UM`: "Ground-truth divisions have sister separations up to 13.7um (median
  10.4, p90 13.0) ... 14um admits all of them."** The shipped 14.0 already admits every real
  division, so raising it is a pure false-positive generator. **CLOSE that knob.**
* **`DET_THRESHOLD`: their own sweep reads "0.96 -> 0.937, 0.95 -> 0.937, 0.94 -> 0.936".**
  **DO NOT SUBMIT `xsv96`** (DET 0.96): 0.96 is a measured -0.004 on this lineage.
* `DEEPCENTER_SAFE_DIV_THRESHOLD` 0.26: x56 claims "moved divisions 148->87 and scored 0.942", but
  rogerrogerroger3r PAID for the clean test and got 0.941 for 0.26 ALONE and 0.942 only for
  0.26 + GAP_CLOSE_UM 5.8. So the knob is not a standalone lever, and "the pair is not the sum of
  its parts". Treat single-knob division sweeps with that caveat.
=> THE DIVISION AXIS IS A PRECISION PROBLEM AS MUCH AS A RECALL ONE. We now have both directions in
flight or ready: recall (xsvdv 98 divisions, xsvdc 125, xsvdd, xsvd10) and precision (xsvdu at the
public sweep peak). Whichever side the board rewards, one day's slots map the sign.

### ALSO CLOSED 09-24 BY THE MINING WORKFLOW (45 agents, 5 miners + 40 adversarial verifiers)
Only ONE of 40 candidate levers survived refutation. The refutations that matter:
* **`xsvt` (TIGHT 5.5 -> 6.0) IS A NEAR-DUPLICATE OF xsv AND MUST NOT BE SUBMITTED.** When the flow
  prior fires (it fires on 198 of 198 frames) the passes use FLOW_TIGHT 7.0, not MOTION_RELINK_TIGHT;
  the latter only sets the seed gate, and the seed measurement shows it barely moves the field.
* **THE WHOLE FLOW FAMILY IS CLOSED**, measured not argued: FLOW_TIGHT above 7.0 and FLOW_RELAXED are
  already ~6.7 sigma out on the flow residual (our own edges: mean 1.639, p50 1.675, p90 2.725,
  p99 4.062, max 7.761 um); FLOW_ITER 2 rebuilds the same field; FLOW_RADIUS is only a
  distance_upper_bound that the K=12 nearest are already inside; FLOW_EXCLUDE 3.0 moves the median
  by 0.0002 um; FLOW_MIN_SAMPLES never binds; FLOW_RAW_COST is pure re-ranking; FLOW_GATE=0 strictly
  REMOVES admission. Do not spend a slot anywhere in this family.
* **THE GAPFILL FAMILY IS MOSTLY CLOSED**: LOWDET_THRESHOLD is masked by the stricter
  GAPFILL_MIN_SCORE=0.5; GAPFILL_MAX_ADDED_FRAC never fires; GAPFILL_EXCLUDE loosening is a trap;
  readmit anchors are not the binding constraint (780 nodes already have no outgoing edge).
* `GAP_CLOSE_MAX_GAP` is hard-clamped: `effective_gap_max = min(GAP_CLOSE_MAX_GAP, 1)`, so the "2"
  every notebook sets has always been a 1. `gap_reused_existing = 0` on all four movies.
* THE ONE SURVIVOR: **the adaptive short-track rescue is DEAD CODE.**
  `SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC` defaults to 0.10 and nobody sets it, so the block is
  fenced off; our removed fractions are 0.98 / 7.7 / 2.1 / 0.9 percent and it has fired ZERO times
  (`short_track_rescue_triggered = 0` on every row of every run_stats we have). The five rescue
  knobs x138 ships are therefore all inert. An offline replay from our cached geffs measured that
  arming it restores ~86 components / ~380 nodes / ~294 edges, all division-free, at +0.28% nodes.
  Direction is a genuine coin-flip with a tilt (break-even is p ~= 0.55-0.6 on ~275 restored edges).
  **The real reason to ship it is DETERMINISM**: 44b6_0b24845f sits at 7.7% against a 0.10 trigger,
  so a hidden-test rerun with slightly worse detection would arm the block on that movie alone.
  Our current submissions carry that undeclared conditional behaviour. Built as `xsvsr`.

### 09-24 04:15Z: TWO POINTS ON THE DIVISION-RECALL CURVE ARE NOW IN FLIGHT, AND xsvb IS DEAD
| arm | change | geometric candidates | DeepCenter acc/rej | divisions | nodes | edges |
|-----|--------|---------------------:|-------------------:|----------:|------:|------:|
| xsv | (reference) | 610 | 161/449 | 73 | 124,144 | 119,887 |
| **xsvdv** | DIVERGE 2.25 -> 1.50 | **1,061** | 249/812 | **98** (+34%) | 124,161 | 119,925 |
| **xsvdc** | DeepCenter veto 0.25 -> 0.15 | 610 | **325/285** | **125** (+71%) | 124,203 | 119,985 |
| xsvb | learned bonus 1.0 -> 1.6 | 608 | 159/449 | 72 | 124,143 | 119,894 |
The two division arms attack DIFFERENT gates: xsvdv widens the GEOMETRY (more candidates reach the
veto), xsvdc widens the VETO (more of the same candidates survive it). Both cost almost nothing in
nodes (+0.01% and +0.05%). Submitting both on the same day deliberately puts TWO POINTS on the
division-recall curve: if xsvdc > xsvdv > xsv, keep pushing recall; if xsvdc < xsvdv, we have found
the precision/recall peak in one day instead of three.
**xsvb (learned bonus 1.6) IS INERT ON THIS BODY AND MUST NOT BE SUBMITTED**: 608 vs 610 candidates,
72 vs 73 divisions, 124,143 vs 124,144 nodes, 119,894 vs 119,887 edges. That is the same result our
09-23 dial measurements predicted - the bonus is a pure RE-RANKING knob, ~88% of links are forced,
and under the flow cost the raw-distance term is 0 so the bonus competes only with the flow
residual. Do not spend a slot on it. THE RULE HOLDS ON THE MERGED BODY TOO: only ADMISSION-moving
changes (which candidates are reachable) are worth slots; pure re-ranking is inert.
SLOTS 09-24: 4 of 5 used (xsv, xsvf, xsvdv, xsvdc). ONE HELD for a reaction to xsv's score.
The held slot's best candidates are `xbase` (is our refinement net-NEGATIVE here, since it writes 84
divisions vs xsv's 73?) and whatever the lever-mining workflow surfaces.

### 09-24 04:09Z: THE DIVERGENCE GATE IS A REAL LEVER, AND THE REFINEMENT *COSTS* DIVISIONS HERE
`xsvdv` (SAFE_DIV_DIVERGE_UM 2.25 -> 1.50) GATE_PASS and SUBMITTED. Funnel totals over the 4 movies:
| metric | t6stk3 (0.954) | xsv | xbase | xsvdv |
|--------|---------------:|----:|------:|------:|
| nodes | 122,863 | 124,144 | 124,246 | 124,161 |
| edges | 118,537 | 119,887 | 120,038 | 119,925 |
| geometric division candidates | 627 | 610 | 694 | **1,061** |
| divergence-rejected | 4,105 | 3,724 | 3,761 | **3,273** |
| DeepCenter accepted / rejected | 182/445 | 161/449 | 179/515 | **249/812** |
| **divisions written** | 79 | 73 | **84** | **98** |
TWO THINGS COME OUT OF THIS.
1. **The divergence relaxation does exactly what we wanted**: +451 candidates past the gate, +74%
   geometric candidates, **+25 divisions (73 -> 98, +34%)**, and the node count moves by 17 (0.01%)
   and edges by 38 (0.03%). It buys divisions at almost no adjEJ node-penalty cost. This is the
   right SHAPE of lever; whether the added divisions are correct is what the board will say.
2. **CORRECTION TO THE EARLIER READ OF xbase.** I wrote that xbase was a weak use of a slot because
   the refinement only moves 63 links on this body. The division counts say otherwise: xbase writes
   **84** divisions and xsv only **73**, so our sub-voxel refinement LOSES 11 divisions (13%) on the
   x138 body - the refined coordinates make the safe-division geometry gates stricter. At 0.1*divJ
   that is a real potential cost, and it can outweigh the small written-coordinate gain. **xsv vs
   xbase is now a genuine open question and xbase is worth a slot**, because if the refinement is
   net-negative here the right final body is xbase + division gates, not xsv + division gates.
   (This also explains part of why t6stk3 wrote 79: different body, different geometry.)

### MEASURED 09-24: ON THE x138 BODY THE SUB-VOXEL REFINEMENT MOVES ALMOST NO LINKS
Matched every xsv node to its nearest xbase node within 2 um per (dataset, timepoint), then mapped
the edges through that matching (both submissions are local: `data/out_xsv/submission.csv`,
`data/out_xbase/submission.csv`):
* 120,033 of 124,144 xsv nodes (96.69%) have an xbase counterpart within 2 um.
* Of the edges whose BOTH endpoints matched, **114,379 are the same link and only 63 differ (0.05%)**.
On OUR old body the refinement was worth +0.005, and the 09-18 hsz0 control showed the applied
offset itself was worth +0.003 with the float channel held constant. The mechanism there was that
the linker read sub-voxel coordinates and changed its assignment. **The flow prior absorbs that
channel**: it predicts a cell's next position from its 12 nearest neighbours' median displacement,
which swamps a 0.4 um coordinate correction. So on the merged body the refinement should be worth
only its WRITTEN-COORDINATE effect on the scorer's 7 um matching, not its linking effect.
CONSEQUENCE FOR SLOT SPEND: xsv vs xbase is a nearly-predictable comparison and xbase is a weak use
of a slot. Put the slots on mechanisms that move ADMISSION (which candidates are reachable) - the
division gates first, since the division channel is worth 0.020 with about 0.08 unclaimed.
ALSO NOTE: xsv and xbase differ by 4,111 unmatched nodes (3.3%), because the gap filler and the
readmit stage respond to the different geometry. The two arms are not a clean one-variable pair.

### THE DIVISION CHANNEL: 0.08 IS ON THE TABLE AND WE MEASURED EXACTLY WHICH GATE EATS IT
Public, leaderboard-measured, by rogerrogerroger3r (rank 77, 0.954, notebook
`what-each-piece-of-this-pipeline-is-worth`): the SAME run with every division turned off scores
**0.924 -> 0.904**, so the whole division channel is worth **0.020**. Since score = adjEJ + 0.1*divJ,
this lineage's **divJ is about 0.20**, and roughly **0.08 of the final score is still unclaimed in that
term**. That is larger than every localization and linker gain we have ever made, combined.

OUR OWN DIVISION FUNNEL, counted from `data/out_t6stk3/run_stats.csv` (the real 0.954 run, 4 movies):
| stage | count |
|-------|-------|
| rejected by the DIVERGENCE gate (`SAFE_DIV_DIVERGE_UM` 2.25) | **4105** |
| rejected by mutual-NN | 396 |
| rejected by sister symmetry (tau 0.6) | 91 |
| geometric survivors reaching the DeepCenter veto | 627 |
| ... DeepCenter ACCEPTED / REJECTED (threshold 0.25) | 182 / **445** |
| divisions actually written | **79** |
| skipped by the frame/global frac caps | **0** (the caps are NOT binding: the global cap would allow ~460) |
=> The two gates worth a slot are DIVERGENCE and the DEEPCENTER VETO, in that order. thtennant's
public `frontier947-divprec-v1` independently moves a third one (sister symmetry 0.6 -> 0.4), and
amanatar's extended sweep names exactly this family (`dcsd015`, `dcsd010`, `divwide`, `sym075`,
`diverge150`). Our old `gdiv` (0.949, -0.002) moved FIVE division knobs plus a leaf prune AT ONCE, so
it says nothing about any single one. **THE DIVISION AXIS IS REOPENED FOR SINGLE-KNOB ARMS.**
Built + gated: `xsvdv` (DIVERGE 2.25 -> 1.50), `xsvdc` (DeepCenter veto 0.25 -> 0.15), `xsvd`
(sister symmetry 0.6 -> 0.4, thtennant's divprec).

### REFUTED BEFORE IT COST A SLOT: LOWERING `ILP_DIVISION_WEIGHT` IS A NO-OP HERE
rogerrogerroger3r also proves (notebook `biohub-the-proxy-is-inverted-the-ilp-can-t-fork`) that in
tracksdata's ILP the out-flow constraint makes out-degree 2 possible ONLY when the division variable
is 1, and with `ILP_APPEARANCE_WEIGHT = 0` the objective change is `division_weight - p2`, so the
solver forks only when `p2 >= division_weight`. Since `p2 <= 1`, **any division weight >= 1 makes an
ILP fork arithmetically impossible, and this lineage ships 1.2.** Confirmed on our own run: run_stats
has `safe_divisions_added = 79` and `division_like_sources = 79`, identical, plus
`dropped_multi_child_edges = 0` on all four movies. Every division we output comes from the
post-process, and the ILP contributes exactly zero.
It is TEMPTING to conclude "so drop the weight below 1.0 and open a new, learned-probability division
channel". **DO NOT BUILD THAT ARM.** Read cell 5: `motion_relink_edges` REPLACES the edge list
wholesale with a `linear_sum_assignment` one-to-one matching (at most one child per source by
construction), and `OUTPUT_SINGLE_CHILD_REPAIR` then keeps only the best outgoing edge per source.
Any fork the ILP produced is destroyed twice over before `add_safe_divisions_postlink` runs. Lowering
the weight would cost a slot and change nothing. (Same reason every public `division_weight` sweep
above 1.0 was a no-op: they were all the same run.)

### TWO INDEPENDENT PUBLIC CONFIRMATIONS OF OUR OWN MEASUREMENT RULES (no new lever, but they close doors)
* zhincez, `the-metric-pays-you-to-delete-nodes`: the uncapped node-count multiplier looks like free
  score offline (+0.013 on a 4-film validator, winning on every film) and gave **-0.004 on the board**.
  Three of their submissions say the lever is not there. Matches our own closed "node-count pruning".
* rogerrogerroger3r: on three real submissions the held-out PROXY_SCORE ranks them in the EXACT REVERSE
  of the leaderboard, and the predictor of the direction is the written node count. Their rule, which is
  now ours too: **an offline proxy is admissible only between two candidates whose node count is
  essentially unchanged.** That is a sharper version of our "the offline screen is a coin flip at 1 tick".
* The rank-21 public notebook (analyticaobscura, 0.962 on the board) is NOT a 0.962 recipe: it is a
  5-cell portfolio-styled notebook of their old ~0.941 line. Checked and dropped.

### NEXT (not yet built)
BUILT AND GATED, WAITING FOR SLOTS (all are single env moves on the merged body, so `build_x138.py` makes them
with `--env`, and each carries an `ARM_XENV` line read back from os.environ at runtime that pins which build ran):
`xsvt` (TIGHT 5.5 -> 6.0: our own board paid a tick for this AND thtennant shipped a `tight60` notebook),
`xsv96` (DET 0.965 -> 0.96, thtennant's `det096`; untested on a body whose recall stack puts nodes back),
`xsvd` / `xsvdv` / `xsvdc` (the three division gates above).
thtennant's other named lever, `SAFE_DIV_SISTER_MIN_UM`, is DEAD by his own comment in the source:
"it did not hold on both caches (RESEARCH 24)", and he ships it at 0 (off). Do not spend a slot on it.

---


## 2026-09-23 RESULTS: 0.954 HOLDS. LINE-FIT CLOSED, RAW-ILP OVERRIDE NEUTRAL.
| arm | LB | read |
|-----|----|------|
| t6r70 (0.954 body + raw-ILP override 0.70) | **0.954** | TIE. Predicted: 23% of the links it would add are already final edges here, so its standalone gain was already captured. Keep as a FINAL-B diversity candidate (different output, same score). |
| t6lf (+ strict-linear line-fit) | 0.953 | -0.001 |
| t6w72 (+ line-fit weight 0.72) | 0.953 | -0.001 |
| t6rlf (override + line-fit) | 0.953 | -0.001, consistent with line-fit being the harmful half |
=> THE LINE-FIT FAMILY IS CLOSED: both directions (strict-linear gating and a lower weight) cost a tick on the refined
body. Do not touch line-fit again. Coordinates after the refinement are at an optimum.
STILL BEST: t6stk3 0.954 (and t6r70 0.954 with a genuinely different output).
CLOSED SO FAR: line-fit (both ways), divisions (gdiv 0.949), tight radius (6.0 optimum; 5.5/6.5 both worse or tied),
refinement gain (2.0 peak), 5x5x5 window, z re-slicing, hoct veto, learned offset head, node-count pruning, rawlink at
0.30, the offline screen as a 1-tick decision tool.
LAST SLOT 09-23 SPENT ON t65s3 (SUBMITTED 14:56Z, GATE_PASS): TIGHT 6.0 -> 6.5 INSIDE the stack. 09-23 used all 5.
WHY NOT THE DIALS (measured, ops/wf_dials.js run wf_22d56e40-449; the BOX WAS UNREACHABLE so this was done locally):
* Leverage on the real 0.954 detections: velocity 0.25 -> 0.00 changes the geometric argmin on 79/118458 sources
  (0.067%); bonus 1.6 -> 2.2 has a HARD ceiling of 116 links (0.098%, since (2.2-1.6)*|dp| <= 0.6 um). For scale,
  t6r70 rewired 1.00% of links and bought ZERO ticks. Both dials are an order of magnitude below a proven-inert change.
* Only 11.69% of sources have more than one candidate inside the 6.0 um gate at all: ~88% of links are forced.
  The learned bonus currently overrides geometry on ~0.37% of contested links (~51 links in the whole submission).
* VELOCITY 0.00 IS REFUTED ON DIRECTION: over all 81 local GT movies / 28,331 triples the least-squares optimum is
  w = 0.3077 (grid min 0.3125). Our 0.25 is AT the optimum; 0.00 costs +0.0895 um vs +0.0428 um for the 0.5 we moved
  away from, and on the 6bba family (63% of visible links) w* = 0.39 and 0.00 is the WORST value on the grid.
  So 0.5 -> 0.25 moved TOWARD a minimum; 0.00 overshoots it. Do not build velocity-0 arms.
* t65s3 has real leverage: 6.0 -> 6.5 gives 6.58% of sources a new candidate and the same step on the 0.951 body
  rewired 3.5% of links (it tied there, but inside the stacked cost the interaction was untested).
* CALIBRATION THAT MATTERS FOR ALL FUTURE ARMS: edge-change size does NOT predict board movement on this body.
  t6r70 1.00% of links changed -> TIE; t6lf/t6w72 0% of links but 15-19% of COORDINATES moved -> -1 tick each.
  Coordinates are the sensitive axis and they are already at an optimum; pure rewiring is cheap and mostly inert.
* Local in-sample scoring is USELESS here: only 2 of the 4 visible movies have local GT (99 GT edges), so ONE GT edge
  is worth ~28 board ticks. It ranked t6r70 +0.028 over t6stk3 (board: tie) and gdiv above hfusion (board: -0.002).
STILL BEST 0.954: t6stk3 and t6r70 (same score, different outputs).
ONE SLOT LEFT on 09-23; researching the last untested levers in the relink family (dial EXTREMES: velocity 0.00 and
bonus 2.2, both continuing directions that paid) with the exact replay grid: ops/wf_dials.js (run wf_22d56e40-449).
NOTE v_t6v00 was built but NEVER pushed (no Kaggle run); v_t6b22 is built AND has a COMPLETE run, unsubmitted.

## !!!! 2026-09-23: NEW BEST **0.954** = `t6stk3`. STACKING IS SUPER-ADDITIVE. !!!!
| arm | LB | note |
|-----|----|------|
| **t6stk3** | **0.954** | stk3 + t60h = relink velocity 0.25 + learned bonus 1.6 + refined coords into the edge model + TIGHT 6.0 |
| t60h | 0.952 | TIGHT 5.5 -> 6.0 alone |
| stk3 | 0.952 | the three linker changes alone |
| t65h | 0.952 | TIGHT 6.5: TIES 6.0, so the radius axis has PLATEAUED (5.5 -> 0.951, 6.0 -> 0.952, 6.5 -> 0.952) |
| gdiv | 0.949 | division knobs + leaf prune HURT (-0.002 vs 0.951): the division axis is CLOSED on this body, and it also kills hsgdint |
| lcefr / lcvel2 / lcbonus2 | 0.951 | the components, each a tie alone |
THE PATTERN THAT IS WINNING: independent sub-threshold gains STACK. 0.951 -> 0.952 (each mechanism alone) -> 0.954 (both).
0.946 (no refinement) -> 0.951 (refinement) -> 0.954 (+ linker + gate radius). Keep adding INDEPENDENT mechanisms to the
best body and check the stack on the board; the board is the only judge (the LOEO screen calibration FAILED, see below).
09-23 SUBMISSIONS (4 of 5; 1 slot held): t6r70, t6rlf, t6w72, t6lf, all GATE_PASS on the 0.954 t6stk3 body.
  All five stack arms passed adversarial review (priorities t6r70 1, t6lf/t6rlf 2, t6w72 3, t65s3 4). t65s3 PARKED:
  the exact refined replay says 6.5 < 6.0 and the board already tied it at 0.952.
  Overlap finding: 23% of the links rawlink would add on the 0.951 body are ALREADY final edges on the 0.954 body
  (the relink changes got there first), so expect a SMALLER marginal gain than standalone; super-additivity is not
  guaranteed to compound. rawlink also strands 89 short components / 38 singletons (a property of the component).
* !! GATE HOLE FIXED: an UNKNOWN tag used to require nothing and PASS (need.get(tag, []) -> []). gate.py now hard-fails
  unrecognised tags. Verified: nonexistent_tag on the t6stk3 log = GATE_FAIL; hsg200/stk3/t60h/t65h/gdiv/t6stk3 still pass.
  Backup ops/gate.py.bak_unknowntag.
* OPS NOTE: `kaggle kernels output` can fail transiently; the runner then writes <tag>.NOLOG and REFUSES to submit
  (correct). Recovery: delete the sentinel, re-run the download, then `python ops/run_today.py <plan> --submit-only`.
* Dial extremes t6v00 (velocity 0.00) and t6b22 (bonus 2.2) are BUILT and RUNNING unsubmitted; a reviewer is writing
  their gate entries and will name which one earns the last slot.
RADIUS/CONSTANT AUDIT DONE (ops/wf_radius.js). Results:
* The 'hfusion's hidden rerun wrote TIGHT 6.0' story is WRONG. Exact replay (reproduces hfusion's and t60h's real rows
  byte for byte) shows the hidden validator would pick combo(tight55 + relaxed9 + bonus125) = 0.947; base could not win.
  t60h's tick is REAL but it is the REFINEMENT MOVING THE OPTIMUM, not a recovered setting. Exact refined TIGHT curve on
  05db0fb1: 5.5 -0.0115, 5.75 -0.0042, 6.0 BEST, 6.25 -0.0013, 6.5 -0.0047 (matches the board: 6.5 ties 6.0).
* r90s3 (RELAXED 10 -> 9 on the 0.954 body) BUILT at scratch_kernels/v_r90s3 but HOLD: the screen agrees with the board
  95% at >= 3-tick gaps, 59% at 2 ticks, 48% AT 1 TICK (a coin), and r90's forecast is 0.2 ticks; its 54/17 sign test
  resampled onto 4-movie panels is positive only 56% of the time; the gain is a DIVISION artifact carried by 2 of 71
  movies while every direct division reading is negative (hfusion's sweep ranked relaxed9 LAST of 7; the replay loses a
  division parent). Its gate entry text is in the workflow output if it is ever revisited.
* INERT constants (0 changes when moved): GAP2_MAX_STEP_UM, GAP_CLOSE_REUSE_UM, SHORT_TRACK_RESCUE_MAX_MEAN_EDGE_DIST_UM,
  OUTPUT_EDGE_MAX_UM. Live but small: GAP_CLOSE_UM, DEEPCENTER_GAP_CONFIRM_MIN_SPAN_UM.
* USE THE SCREEN ONLY FOR >= 3-TICK QUESTIONS (gross harm), never for 1-tick choices.
THROUGHPUT CHANGE 09-23: ops/run_today.py now has --no-submit (push + run + gate-later, spends GPU quota but NO slot) and
--submit-only (gate + submit kernels that already finished). Runs are started BEFORE the reviews finish; the gate still
guards every submission. plan_0923.json = t6r70, t6lf, t6rlf, t6w72, t65s3, all started 04:19Z with --no-submit.
TEAM-UP REQUEST (hjyact) 09-23: DECLINE. The team-merger deadline passed at 2026-09-22 23:59Z, so joining is impossible;
sharing code outside a team violates rules 3.5.d/3.6.a. Their board standing is 0.947 (rank 876), not the 0.928 they
quoted for their own pipeline; either way below our 0.954. Do not exchange code or data with them.
NEXT: stack the remaining independent, already-reviewed components onto v_t6stk3: rawlink70 (raw ILP override at 0.70),
lfds (division-safe line-fit), lfw72 (line-fit weight 0.72), and a TIGHT 6.5 variant of the stacked body.
DO NOT stack: gdiv/division knobs (board-negative), hsgdint (same axis), hoct1 (closed), any refinement-gain change
(the gain curve is mapped and 2.0 is the peak).

## !!!! 2026-09-22 14:20Z: NEW BEST **0.952** x2: `t60h` AND `stk3` (two DIFFERENT mechanisms) !!!!
| arm | LB | change on the 0.951 hsg200 body |
|-----|----|--------------------------------|
| **t60h** | **0.952** | ONLY MOTION_RELINK_TIGHT_UM 5.5 -> 6.0 (every arm since 09-17 had hard-coded 5.5; hfusion's hidden-rerun validator most likely chose 6.0, which explains hsz0 0.946 vs hfusion 0.947 on byte-identical visible output) |
| **stk3** | **0.952** | relink velocity 0.25 + learned bonus 1.6 + refined coords into the edge model: three arms that EACH tied at 0.951 (disjoint 1-6% edge changes), stacked. Sub-threshold gains ADD. |
| gdiv | pending | division knobs + leaf prune |
LESSONS: (1) a hard-coded constant from the pre-refinement era cost a tick; audit the others. (2) stacking genuine ties with
disjoint change sets can clear the board's 0.001 resolution: individual 0.951 ties were NOT zero.
USER said "choose best" for the last 2 slots of 09-22 -> chose t6stk3 + t65h (plan_0922_D.json, pushed 14:23Z):
  t6stk3 = stk3 + tight 6.0 (both 0.952 mechanisms; v_t6stk3 = v_stk3 with only the tight line changed; gate entry tested:
           fails the stk3 and t60h logs alone, passes only when all four markers fire).
  t65h   = tight 6.5 bracket (is the radius curve still rising?).
09-22 SUBMISSIONS (all 5 used): stk3 0.952, t60h 0.952, gdiv pending, t65h (14:54Z) pending, t6stk3 (15:00Z) pending.
All five passed ops/gate.py before submission.
!! SCREEN CALIBRATION FAILED (ops/wf_calib.js; files scratch_kernels/_calib0922/): the refined LOEO screen tracks ONLY
refinement on/off (+0.0040 vs board +0.005). It cannot place the gain peak (flat from 1.0 to 4.0), it scores the 0.937
collapse (g4 clip1.0) as its BEST arm (+0.0079), misses the z-reslice harm (0.948), and predicted t60h as a tie (board
+0.001). Spearman over 14 arms +0.29 (p 0.31). Root causes: 44b6 GT has only 26 annotated divisions in 71 movies, so
division damage is invisible; ILP links on lattice coords; DeepCenter off; far fewer saturated offsets. Judge: NOT
trustworthy for coordinate or linker knobs. Offline grid search SKIPPED. RULE STANDS: the board decides; offline tools
(exact visible replay, LOEO screen) only verify mechanics and veto gross harm.
RESEARCH RUNNING: a radius/constant audit
(ops/wf_radius.js, wf_e817f718-565): which PP_CANDIDATES hfusion's hidden validator could pick, the relaxed/gap radii on
the refined body, and up to 2 reviewed arms on v_t60h (tags start with 'r').
FINAL PICKS NOW (revise as scores land): A = the best of t6stk3 / t60h / stk3; B = a 0.952 with a DIFFERENT mechanism.
t60h and stk3 are a natural A/B pair today (gate radius vs linker costs+features).

## 2026-09-22 ~06:30Z: RESEARCH DONE (INTEL_0922.md + RESEARCH_0922.md). NOTHING SUBMITTED TODAY. AWAITING USER GO.
* !! TEAM NOW HAS 4 MEMBERS: akkigupta2005, arunendratripathi03, eeshsaxena, swapiy (4 leaderboard snapshots agree; it
  was 2 on 09-17). User must confirm the merge was intended and ask the new members not to submit or touch the finals:
  the 5/day and the 2 final picks are team-wide. Merger deadline 09-22 23:59Z.
* Kaggle ranks on the UNTRUNCATED score: team representative submission is lcvel2 (56403386), so lcvel2 > hsg200 at full
  precision. Passive read only; never submit near-duplicates to read decimals (that is leaderboard probing).
* Standing: public rank 98/3798 at 0.951 (silver band; silver line 0.948, gold 0.961, prize 0.967, leader 0.974). ~10
  teams/day are arriving at >= 0.951, so a flat 0.951 drifts to the silver edge (~rank 150-185) by 09-29.
  Public = 29% of test, private = 71%. Public kernel publishing closes 09-22 23:59Z. No host post since 09-16.
* NEW LEAD (deep research): TIGHT 5.5 may be costing a tick. hsz0 and hfusion wrote byte-identical VISIBLE submissions
  but scored 0.946 vs 0.947: hfusion's validator reruns on the hidden set, where 6bba_05db0fb1 (3 GT divisions) replaces
  6bba_09961292 in its validation set, which most likely flipped its choice to TIGHT 6.0. Every arm since 09-17
  hard-codes 5.5. Counter-evidence exists (LOEO favours 5.5 on 2 of 3 shards), so it is a one-slot hypothesis.
  => BUILT `v_t60h` = v_hsg200 with ONLY the cell-0 env line 5.5 -> 6.0 + marker ARM_T60H (1 cell changed, compiles,
  SV_ARM_HSG200 x2). Gate entry added and tested both ways (FAILS the real hsg200 log, PASSES an injected one; hsg200
  regression still passes). Not pushed.
* META-GATE: dead. No output statistic predicts the LB (nested LOO MAE 0.00226 vs 0.00235 for the mean; best feature
  permutation p=0.146). Visible outputs cannot gate anything (hsz0 == hfusion bytes, different scores).
* stk3 and stkve: COMPLETE, GATE_PASS (re-verified), NOT submitted. stk3 is mostly lcefr again (0.56% of matched edges
  from lcefr); stkve is 0.31% from stk3 = near-replicate, skip it. Outputs in scratch_kernels/_deep0922/{stk3,stkve}/.
  Submit later with: kaggle competitions submit biohub-cell-tracking-during-development -k eeshsaxena/biohub-v-stk3 -v 1 -f submission.csv -m "..."
* gdiv (intel's candidate: amanatar geometric-fusion division knobs DC 0.15 / MAX 11 / SISTER 16 / CHILD 12 + leaf prune
  0.30, velocity kept 0.5) is being built and reviewed. The only public kernel above 0.947 (0.948), purely post-processing.
* Learned offset head (josephadamski91): weights private, needs a capture run: NOT safe today, tomorrow at the earliest.
* RECOMMENDED TODAY (<= 3 slots): stk3 (ready), t60h (one GPU run), gdiv (if its review says SHIP). Skip stkve, stkvb,
  lcvel0, lcbon22 (dials that already tied / near-replicates).
* USER APPROVED 09-22 ~06:00Z: stk3 + t60h + gdiv (gdiv ONLY if its review says SHIP). stk3 SUBMITTED 06:08Z (v1,
  gate re-verified). t60h pushed 06:03Z via ops/run_today.py plan_0922_B.json (gate then auto-submit). gdiv pending review.
* 09-22 06:40Z t60h SUBMITTED (GATE_PASS). Today so far: stk3 + t60h submitted, 3 slots left. gdiv review resumed
  (workflow ops/wf_gdiv.js, run wf_25f20ad2-170; build cached, v_gdiv exists) -> run via run_today.py ONLY if SHIP.
  rawlink (josephadamski91 V1057: raw ILP edges prob >= 0.30 override conflicting final edges, divisions protected)
  being studied/built/reviewed for 09-23 (ops/wf_rawlink.js, run wf_ec964266-f4b); it must NOT edit gate.py.
  After a session restart: resume workflows with Workflow({scriptPath:'ops/wf_*.js', resumeFromRunId}).
* 09-22 ~06:50Z USER: "keep researching in parallel, don't stop until I say, keep going autonomously".
  Third parallel job: ops/wf_parb.js (run wf_88b0bbb1-57a): (A) did the refinement break divisions (99 -> 76) and a
  legit way to recover them, (B) micron thresholds tuned before the refinement existed, (C) an in-kernel learned offset
  head (capture on train movies inside the kernel, no dataset upload). Builds + reviews up to 3 arms for 09-23.
  Standing rule for autonomous mode: build/review freely; submissions only with the user's approval per day.
* 09-22 07:00Z gdiv review = SHIP; pushed via plan_0922_C.json (gate then auto-submit, user-approved). MEASURED on the box
  (exact replay of cell 5 that reproduces the real 0.951 submission byte for byte): divisions 76 -> 137 (+80%), 76 leaf
  nodes pruned (all hung off 0-prob relink edges), FINAL nodes ~unchanged, 359 nodes' written coords move (linefit),
  0 out-of-volume / dangling / degree violations. gate.py gdiv entry added by the reviewer (tested both ways).
* 09-22 07:46Z gdiv SUBMITTED (GATE_PASS). TODAY'S SUBMISSIONS: stk3 06:08Z, t60h 06:40Z, gdiv 07:46Z (3 of 5; 2 unused).
  The real Kaggle gdiv run matched the box replay EXACTLY (divisions 49/40/6/42 = 137, leaves 10/11/2/53, FINAL
  25618/20721/6160/70248), so the replay tool is validated against a fresh Kaggle run, not only the old hsg200.
* rawlink (V1057 at prob >= 0.30) = HOLD. Port exact (3 implementations agree, 80k-graph fuzz clean) and valid, but the
  unseen-embryo box screen says it HURTS at 0.30: mean -0.00100, 9 up / 26 down, sign p=0.006; harm is in prob band
  0.30-0.70. By threshold: 0.70 -> +0.00054 (9/5, p=0.42, 2.40% of visible edges); 0.80 -> +0.00030 (6/1, 1.72%);
  0.90 -> +0.00006. NOTE the edge-prob floor on this lineage is 0.48 (DUAL_SEED_EDGE_THRESHOLD), so 0.30 == 0.48.
  => BUILT v_rawlink70 (v_rawlink with only the cell-0 env 0.30 -> 0.70; cell 4 == hsg200). gate.py entry `rawlink70`
  added (need patterns + per-movie arithmetic/degree/division checks + total accepted in [651, 2606] + a guard that
  fails if another arm's marker is present). Tested: fails hsg200 log, passes a synthetic good log, fails threshold
  0.3 / foreign GDIV_DS marker / changed division count; hsg200, stk3, t60h, gdiv still pass their real logs.
  Backup of the pre-edit gate: ops/gate.py.bak0922. CANDIDATE FOR 09-23 (needs the user's daily go).
* Top-teams code reading relaunched (it died on a network error in the deep research): ops/wf_topteams.js, run
  wf_91c8aa1d-f67 -> TOPTEAMS_0922.md.
* TOP-TEAMS CODE READ (TOPTEAMS_0922.md): 10 public authors on teams above 0.951; nothing public explains any score;
  every public pipeline is older than / a subset of ours; the top 5 teams (0.967+) publish nothing current.
  Levers: (1) lfds division-safe line-fit (zoli800, VOXEL ART lineage 0.967): smooth only strict linear interiors,
  ~20%; (2) hoct1 HOCT consensus edge veto mode 1 (needs 2 public datasets, +0.32 GPU-h), ~8%; (3) lfw72 linefit
  weight 0.8 -> 0.72, ~7%. KEY INSIGHT: line-fit is a COORDINATE-shaping knob, the only family that has paid here.
  lfds + lfw72 being built + LOEO-screened + reviewed: ops/wf_linefit.js (run wf_351c2188-b8e).
  Flags: BANNED anvithpothula augment_dataset hub node (t=-1000, -10000 coords); weishanshan033 static submission.csv;
  do not copy enddl22 'GPT FEEDBACK' single-edge LB fitting (close to probing).
  Compliance idea (0 LB change): clip the writer at the UPPER volume bound too (int(np.clip(round(x),0,size-1))).
  Already-scored submissions were accepted on the full hidden set, so this only matters for future arms.
* RESEARCH B DONE (ops/wf_parb.js): (A) the refinement cut divisions 99 -> 76 mainly via the DIVERGENCE (24) and
  SYMMETRY (12) tails, not DC/sister/child gates (0 of the losses). hsgdint (division gates judged on the unrefined
  integer peaks, refined coords still written) built at scratch_kernels/v_hsgdint: replay exact, restores 40 of 59 lost
  forks, divisions 76 -> 99, but only 0.08% of edges and the GT study says NEUTRAL-TO-NEGATIVE (-0.00102, TP stays 8,
  FP 24 -> 30) => HOLD. Revisit only if gdiv reads >= 0.952. (B) threshold arms dv200/dcs875 unreadable, dropped.
  (C) learned offset head CLOSED: heads fit on memorized train movies transfer WORSE than the fixed soft-argmax to an
  unseen embryo (bias-free yx std 0.782-0.811 vs 0.778); ceiling 0.012 um.
  CORRECTION: the refinement moves the typical node ~0.85 um (per-movie mean 0.76-0.93), NOT ~0.42 um.
* hoct1 CLOSED, not built: MODE 1 was ALREADY on the board (sjlee101 biohub-lf-hoctveto-b, the exact source) = 0.947,
  tie; the +0.0040 was a MODE-2 number on in-sample movies; on our body ~0.2% of edges; +0.37-0.40 h visible and a real
  risk of partial silent fallback or a >12 h kill on the hidden rerun (scale 10-22.8x). Do not revisit.
* PRE-BUILT for 09-23, conditional on t60h: v_t65h (tight 6.5, 1 line vs t60h) and v_t60e (t60h + the exact lcefr cell 4).
  Both compile, SV_ARM_HSG200 x2. GATE ENTRIES NOT YET ADDED (wait until wf_linefit finishes editing gate.py): t65h needs
  ARM_T65H tight_um=6.5 + echo 6.5; t60e needs ARM_T60H + echo 6.0 + the ARM_LCEFR per-video worker line (nonzero).
* LINE-FIT ARMS: v_lfds and v_lfw72 both SHIP (clean review, exact replay: topology identical to hsg200, only z/y/x
  move, lfds 14.6% / lfw72 19.6% of nodes; volume max 63/254/254) but the screen shows NO GAIN: lfw72 -0.00077 +- 0.00094
  (15/21), lfds -0.00055 +- 0.00091 (19/20); 0.8 sits on a flat spot; turning line-fit OFF costs -0.022 (8/52).
  gate.py entries added by the reviewer (backup ops/gate.py.bak_linefit). Low priority: expected ~0.
* !! THE REFINED LOEO SCREEN (box ~/biohub/lfsv_review/): 71 unseen-embryo 44b6 graphs + OUR refinement added from dumped
  soft-argmax offsets. The refinement ALONE scores +0.0040 +- 0.0017 (47 up / 24 down) there vs +0.005 on the board:
  the FIRST offline proxy that reproduces a board effect. Calibration against the whole board record running:
  ops/wf_calib.js (run wf_8655b597-767). If it tracks the gain curve + the 0.937 collapse, use it to search coordinate
  knobs (gain x clip x line-fit weight x window) offline, with a held-out half to beat the multiple-comparison winner.
* gate.py: t65h and t60e entries added and tested both ways (backup ops/gate.py.bak_t65); hsg200/t60h/lcefr/stk3/gdiv
  still pass their real logs. The 09-23 shelf is fully gated: rawlink70, t65h, t60e, lfds, lfw72.
* NEW CAPABILITY: the 4 VISIBLE test movies are byte-identical to train movies on the box, so any POST-PROCESSING arm
  (cell 5) can be replayed EXACTLY on the box CPU from a kernel's raw ILP geffs (tracking_repo/predictions/*.geff) plus
  the real frames and CPU DeepCenter (matches the Kaggle log 0.134447). Use it to VERIFY mechanics (counts, validity).
  Do NOT use it as a score gate: 4 in-sample movies vs ~58 unseen-embryo public movies; offline gates have failed here.
* FINAL-PICK DISAGREEMENT to resolve by 09-29: intel says B = lcvel2 (representative best at full precision); deep research
  says B = lcefr (most divergent 0.951 output, 2.33% of matched edges). A = hsg200 unless an arm shows 0.952+.

## 2026-09-22: ROUND 5 RUNNING FROM EESH'S OWN ACCOUNT (user: "submit 5 using my api")
* The round-4 ties are GENUINE: all five round-4 submissions differ from hsg200 (sha), and the three 0.951 linker arms
  change largely DISJOINT edge sets: lcvel2 2.72%, lcbonus2 0.94%, lcefr 6.16% of 118,484 edges; pairwise Jaccard of the
  changed-edge sets 0.127 / 0.143 / 0.039. So each moves thousands of links and nets to ~0 on a 3-decimal board.
* Round 5 = stacks + limits, all built by composing the reviewed edits (anchors verified unique; the stacks' cell 4 is
  byte-identical to v_lcefr) and ALL FIVE cleared adversarial review (no error, no no-op, no banned behaviour):
  stk3 (vel 0.25 + bonus 1.6 + lcefr), stkve (vel 0.25 + lcefr), stkvb (vel 0.25 + bonus 1.6), lcvel0 (vel 0.00),
  lcbon22 (bonus 2.2). Reviewer run order: stk3, stkve, lcvel0, lcbon22, stkvb (stkvb lowest: its two knobs compete for
  the same decisions, simulated stack = 0.52-0.71x the sum of parts; expected ~2% edges, below lcvel2 alone).
  Relink cost is `motion + 0.05*raw - BONUS*prob`; feasible range stays far below the post-solve rejection threshold
  (5501 tight / 10001 relaxed) for every arm; negative costs are fine (checked vs brute force).
* gate.py now has exact-value entries for all five (lcvel0 expects the config echo `0.0`), each also requiring >= 4
  SV_ARM_HSG200 lines (proves the 0.951 body) and, for lcefr stacks, the per-video worker counter line.
* NEW RUNNER `ops/run_today.py plan.json [--dry]`: pushes from eeshsaxena (kaggle_push_safe.py), <= 2 in flight, polls,
  downloads output to data/out_<tag>, runs ops/gate.py, submits ONLY on GATE_PASS, sentinels in ops/state/
  (PUSHED/COMPLETE/GATEFAIL/SUBMITTED/ERROR), stops on a weekly-quota refusal. Log: ops/run_today.log.
  Started 09-22 04:01Z with plan_0922_A.json = [stk3, stkve]. Slots 3-5 held until the 09-22 intel sweep reports.
* 09-22 ~04:10Z USER: "do more research before submitting anything else". The runner was STOPPED before it could
  submit (no SUBMITTED sentinel; only stk3.PUSHED / stkve.PUSHED in ops/state/). Both kernels keep running on Kaggle and
  can be submitted later with `kaggle competitions submit <comp> -k eeshsaxena/biohub-v-<tag> -v 1 -f submission.csv -m ...`
  AFTER gating their logs. Research running: intel sweep (forum/kernels/LB) + deep research (josephadamski91 learned
  offset head, 0.952 teams' kernels, a meta-gate built from our own ~16 board points, final-selection strategy).
  DO NOT relaunch run_today.py for these tags without the user's go-ahead after the research memo.

## 2026-09-21: ROUND 4 SCORED. NOTHING BEAT 0.951. TWO AXES CLOSED, THREE EXACT TIES TO AUDIT.
| arm | LB | read |
|-----|----|------|
| lcefr (refined coords -> linker geometry inputs) | 0.951 | TIE with base |
| lcvel2 (MOTION_RELINK_VELOCITY_WEIGHT 0.25) | 0.951 | TIE |
| lcbonus2 (MOTION_RELINK_LEARNED_BONUS 1.6) | 0.951 | TIE |
| hsg250 (gain 2.50) | 0.950 | CONFIRMS the interior peak at gain 2.00; the magnitude axis is CLOSED |
| hsgzc10 (per-axis clip z=1.0) | 0.948 | z RE-SLICING HURTS (-0.003). Keep the z clip <= 0.5. Closed. |
BOARD CURVE NOW (realized mean |offset| in downsampled voxels -> LB): 0.000 -> 0.946 | 0.080 -> 0.945 | 0.160 -> 0.949 |
0.219 -> 0.950 | **0.257 -> 0.951** | 0.279 -> 0.950 | 0.301 -> 0.949 | 0.320 -> 0.950 | 0.326 -> 0.949 | 0.373 -> 0.948 |
0.640 -> 0.937. Plus z-only loosening -> 0.948. The localization lever is FULLY MAPPED: gain 2.00 + clip 0.4999 is optimal.
PENDING AUDIT (outputs pulled to scratch_kernels/_res0921/): for each of the three 0.951 ties, run ops/gate.py and compare
submission.csv sha256 + FINAL node counts + run_stats relink counts against hsg200 (24235/709/24944, 19294/1095/20389,
5825/212/6037, 65770/2256/68026). Identical sha => the arm changed NOTHING and the tie is a duplicate, not a measurement.
Remember the correction: for pure COST re-ranking arms (lcvel2, lcbonus2) identical relink COUNTS do not prove a no-op;
use the sha. lcefr is different: it changes the link probabilities themselves, so it can change the admitted set.
NEXT IDEA IF THE TIES ARE GENUINE (different output, same score): STACK them. Three independent changes that each land
exactly on 0.951 may each be worth less than the board's 0.001 resolution; stacking hsg200 + lcvel2 + lcbonus2 + lcefr is
the cheapest way to find out. If the ties are duplicates instead, the linker axis is closed and only final selection remains.
FINAL SELECTION (2026-09-29, 2 slots): A = hsg200 0.951. B should be a genuinely DIFFERENT output, not a display twin.

## 2026-09-20: ROUND-4 SLATE = 4 ARMS (`~/OneDrive/Desktop/biohub_next5/`), lcflow2 HELD
Verified by me independently (sha256 vs source, compile, cells-changed, markers, metadata): 1_hsg250 (gain 2.50),
2_lcvel2 (MOTION_RELINK_VELOCITY_WEIGHT 0.25), 3_hsgzc10 (per-axis clip z=1.0, y/x=0.4999), 4_lcbonus2 (LEARNED_BONUS 1.6).
* `lcflow2` (neighbourhood velocity) = BUILT, SAFE, but HELD: it re-ranks only **0.03%** of relink edges (2-8 pairs per
  movie out of ~118k total; 0.017-0.067% even under 2-voxel injected jitter), i.e. it returns 0.951 regardless of whether
  the idea is right. Ship it only after the lever is made large enough to read (pair the flow prior with a raised velocity
  weight, or widen the admission gate).
* !! CORRECTION to the free-readout heuristic: "identical relink counts => the arm re-ranked nothing" is INVALID for
  lcflow2 and any other pure COST re-ranking arm. `big = gate*1000+1` dominates every feasible cost, so the LSAP optimum
  always maximises feasible-assignment CARDINALITY, which is a property of the gate-admissible graph. Counts stayed
  identical in a case where 82 of 432 edges changed. For cost-only arms use `flow_seeded > 0` + the submission sha256.
* Trap confirmed: `scratch_kernels/_hsoft949/tracking_repo/scripts/predict_unet_transformer.py` is NOT pristine (carries
  the old patch). The unpatched predictor is `scratch_kernels/_ckpt/supportpack/predict_unet_transformer.py`
  (md5 a2bbd2b33666aab525a9b4b510c48bd9). Replaying cell 4 against it reproduces the real 0.951 predictor exactly (0 diff).
* Reference runtime correction: the log's "Prediction completed in 9.50 minutes" is for ALL FOUR movies, not per movie.

## !!!! 2026-09-19 21:00Z: MIXED SLATE OF 4 ON THE DESKTOP (`~/OneDrive/Desktop/biohub_next5/` + .zip). LOCALIZATION IS MAPPED AND FLAT ON TOP, SO WE OPEN THE LINKER AXIS !!!!
The section below this one (20:00Z) closed the localization question: eleven board points collapse onto ONE unimodal
curve in node-weighted realized mean |offset|, the peak is INTERIOR at gain 2.00 / clip 0.4999 (`hsg200` = 0.951), and
the top of that curve is FLAT (0.949 to 0.951 across a wide band). The remaining headroom on that axis is the same
size as the board's own +-0.001 roughness. So tomorrow's slate is deliberately MIXED: two arms finish the localization
map, two arms open a lever we have never touched.

### THE SLATE, IN RUN ORDER (4 arms, not 5: see EXCLUSIONS)
| # | arm | axis | change vs the 0.951 `hsg200` body | markers in the log | predicted |
|---|-----|------|-----------------------------------|--------------------|-----------|
| 1 | `hsg250` | localization | sub-voxel gain 2.00 -> 2.50, clip 0.4999 unchanged | `SV_ARM_HSG250 ... gain=2.50` | 0.950 (0.949-0.951) |
| 2 | `lcvel2` | **linker** | `MOTION_RELINK_VELOCITY_WEIGHT` 0.5 -> 0.25 | `ARM_LCVEL2 velocity_weight=0.25` **and** `SV_ARM_HSG200` | 0.951 +-0.002 |
| 3 | `hsgzc10` | localization | per-axis clip (z, y, x) = (1.0000, 0.4999, 0.4999) at gain 2.00 | `SV_ARM_HSGZC10 ... clip_zyx=1.0000,0.4999,0.4999` | 0.950-0.951 |
| 4 | `lcbonus2` | **linker** | `MOTION_RELINK_LEARNED_BONUS` 1.0 -> 1.6 | `ARM_LCBONUS2 learned_bonus=1.6` **and** `SV_ARM_HSG200` | 0.951 +-0.002 |

They ALTERNATE by axis on purpose. The teammate runs 2 at a time, so round 1 = (1, 2) and round 2 = (3, 4): if the day
is cut short we still hold one reading from each half instead of two from the same one. The 5th team slot is left
UNSPENT. Do not fill it with a replicate: the pipeline is bit-deterministic (identical EDGE_TTA deltas to six decimals
across two run days and two Kaggle sessions), so a replicate reproduces exactly and measures nothing.

Desktop folder `~/OneDrive/Desktop/biohub_next5/` (+ `biohub_next5.zip`, 218576 bytes), one subfolder per arm in run
order, each with `kernel.ipynb` (sha256-verified byte copy of `scratch_kernels/v_<tag>/kernel.ipynb`), `notes.txt`
(title, the 4 exact dataset addresses, GPU T4 x2 / Internet OFF / Persistence none / Save and Run All, the marker
lines, the submission description) and a plain-language `README.txt`.
| folder | source | kernel.ipynb sha256 |
|--------|--------|---------------------|
| `1_hsg250` | `scratch_kernels/v_hsg250/` | `924c36b4beaffeb1bbe08f2ec496a75fc42541eee57b921ee68cb1fcfb88078c` |
| `2_lcvel2` | `scratch_kernels/v_lcvel2/` | `2f6175606adc0b378e3f23b14a331b5a75fa1c7df42dcddb7463be4614b95ba1` |
| `3_hsgzc10` | `scratch_kernels/v_hsgzc10/` | `b7a4b55b2a03522a9fb08ef48ef598f0844525edace7e0922a930db0b74b273a` |
| `4_lcbonus2` | `scratch_kernels/v_lcbonus2/` | `54cf29877fa5bd771cbe7282c10cd45c65d82509953f61f75c127f6b7bd52263` |

### WHY THE LINKER, AND WHAT IT IS REALISTICALLY WORTH
It is the first axis in weeks that is not already closed, and it is worth opening ONLY because localization is flat.
Be honest about the prior: the earlier linker autopsy found the production linker picks the NEAREST candidate 99.87%
of the time, and when it errs the true partner sits a median 7.62 um away while the chosen one sits 3.54 um away, so
only about 10% of mis-assignments are reachable by a better cost at all. These arms are therefore worth about +-0.002
each, which is only twice the board roughness. Read them as a DIRECTION, not a measurement.
The two are deliberately opposed, which is what makes the pair informative even when each point is not:
* `lcvel2` (weight 0.5 -> 0.25) pushes the cost TOWARD pure nearest-neighbour.
* `lcbonus2` (bonus 1.0 -> 1.6) pushes it AWAY from distance and toward the learned edge probability.
So whichever way the board moves we recover the sign of the axis. If both read 0.951 the linker COST is not the
bottleneck and the next probe has to be structural (the gate, the gap-close thresholds, the division logic), not
another dial on the same cost function.
Both arms are cost-reranking only: `cost[i,j] = motion + 0.05*raw - BONUS*prob` is rewritten but the `raw > gate_um`
admission gate is untouched, so the candidate set per source is exactly the base's and no new edge becomes reachable.
FREE ZERO-GPU READ-OUT when the logs come back: compare `run_stats.csv` motion_relink counts against the hsg200 run
(tight/relaxed/total per movie: 24235/709/24944, 19294/1095/20389, 5825/212/6037, 65770/2256/68026). If an arm's four
counts are identical to the last digit AND the submission sha256 is unchanged, that arm re-ranked nothing and its
board point is a duplicate of 0.951 carrying no information. That check costs nothing and should be done before the
score is interpreted at all.

### REBASE PROVENANCE (the linker arms were built on the OLD body and had to be moved)
`lcvel`, `lcbonus` and `lcflow` were built and adversarially reviewed against `v_hsoftfix` (the 0.949 body). Comparing
them to today's 0.951 would have confounded the linker change with the sub-voxel change, so each was rebased onto
`v_hsg200` and re-tagged with a trailing `2`.
The rebase is a clean transplant because of a precondition that was re-derived, not assumed: cell-by-cell difflib says
`v_hsoftfix` and `v_hsg200` differ in **cell 4 ONLY** (52542 -> 53462 chars, the sub-voxel gain/clip block:
`BIOHUB_SUBVOXEL_GAIN_MODE=fixed`, `GAIN_FIXED=2.00`, `CLIP=0.4999`, the `_sv_gain()` helper, `sa = sa * _sv_gain()`
before `np.clip(sa, -_SV_CLIP, _SV_CLIP)`, and the `SUBVOXEL_ACTIVE` -> `SV_ARM_HSG200` rename). The linker edits live
in cells 0, 2 and 5, which are byte-identical between the two bases, so the two changes have ZERO interaction.
Method, per arm: diff `v_lc*` against `v_hsoftfix` to recover the exact edit, confirm every anchor occurs exactly 1x in
BOTH bodies (no forcing), then `BUILD_BASE=v_hsg200 python build_multi.py <newtag> '<pairs>'`, which aborts and rmtree's
on any count mismatch. Recovered edits:
| arm | edit | anchors | cells touched |
|-----|------|---------|---------------|
| `lcvel2` | insert the env line + marker after `import os` | 1 (the bare `import os` occurs 2x, so the 2-line anchor is what makes it unique) | cell 0 only, +2 / -0 lines |
| `lcbonus2` | rewrite the existing `BIOHUB_MOTION_RELINK_LEARNED_BONUS` line '1.0' -> '1.6' + marker | 1 | cell 0 only, +2 / -1 lines |
| `lcflow2` | 3 `LC_FLOW_*` constants + 3 config echoes + an 84-line neighbourhood-flow block + replace the own-step predictor + 4 stat keys | 5, each 1x | cells 2 and 5, +105 / -5 lines |
Each arm's own marker was renamed `ARM_<TAG>` -> `ARM_<TAG>2` so a log cannot be mistaken for the 0.949-body run, and
the body marker `SV_ARM_HSG200` was left ALONE (it appears exactly 2x in the notebook: the runtime print and the
`if 'SV_ARM_HSG200' not in _ps.read_text(): raise RuntimeError('SUBVOXEL PATCH DID NOT PERSIST')` persist check).
**Every rebased arm therefore logs BOTH markers, and that pair is the provenance proof: ARM_ says which arm, SV_ says
which body.** Independent verification of `lcbonus2` re-implemented build_multi.py's algorithm in a scratchpad and
byte-compared the result to the on-disk notebook (md5 `500c51ff9c9ccb4fd0c6494edec284e5`, identical), proving the
artifact came from the builder off the 0.951 body and was not hand-touched afterwards.

### EXCLUSIONS (two arms were built and are NOT shipping)
1. **`lcshift` is EXCLUDED PERMANENTLY, do not rebase it.** Its reviewer found it can write a node OUTSIDE the image
   volume. Out-of-volume nodes are on the banned list: they game the metric instead of tracking better. The other
   three linker arms were checked against exactly this failure mode and are clean, because none of them ever assigns
   to a node coordinate. `lcvel2`'s `predicted` is a cost-only quantity (built at c5:496/498, consumed only at c5:504
   inside `motion = norm(target_pos - predicted)`) and is never written out; `lcbonus2` only scales a term in the cost
   matrix; `lcflow2`'s 98 added lines contain no assignment to z/y/x/t, `nodes_by_id` or `position_um`.
2. **`lcflow2` is BUILT but HELD.** `scratch_kernels/v_lcflow2/` exists, is validated by its builder and carries
   `ARM_LCFLOW2` + `SV_ARM_HSG200`, but its adversarial review did not return a verdict, so it has no independent
   sign-off. Shipping an unreviewed arm into a scarce slot is the wrong trade when a slot can simply be banked. It is
   NOT in the desktop folder. To revive it: run the review, and note its builder's own caveat that the arm selected
   exactly the same edges as the base in every synthetic case tried, so it may be a no-op on real data too. The
   numbering closed up naturally because it was last in the intended order, so `1_hsg250 / 2_lcvel2 / 3_hsgzc10 /
   4_lcbonus2` needed no renumbering.

### ONE REAL TRAP FOUND WHILE REBASING (worth more than the arms)
`scratch_kernels/_hsoft949/tracking_repo/scripts/predict_unet_transformer.py` is **NOT a pristine predictor**: an
earlier session patched it in place, so it already carries the older `SUBVOXEL_ACTIVE` patch (`_SV_ON` x4). Cell 4's
4th anchor therefore matches 0 times against it and the patch block raises `SUBVOXEL anchor matched 0 times (need 1)`.
Anyone re-running that check naively will read a spurious failure of a good build. The genuinely unpatched script is
`scratch_kernels/_ckpt/supportpack/predict_unet_transformer.py` (26008 bytes, md5 `a2bbd2b33666aab525a9b4b510c48bd9`).
More generally: a checkout inside `scratch_kernels/` has been mutated by a past run and must not be treated as a
reference copy. The lcflow2 builder worked around it by reversing `v_hsoftfix`'s own 4 cell-4 pairs to reconstruct the
pre-sub-voxel text, then applying the arm's 4 pairs forward, and the result was byte-identical to the predictor the
real 0.951 run produced (`_res0919/hsg200/tracking_repo/scripts/predict_unet_transformer.py`, 53836 bytes).

### `ops/gate.py` NOW COVERS THE LINKER TAGS
`lcvel2`, `lcbonus2` and `lcflow2` are gated the same way the sub-voxel tags are, in BOTH halves of the two-marker
scheme:
* `need[tag]` pins the arm's own `ARM_<TAG>` line AND, where the notebook echoes the realized value in CONFIG_DISPLAY,
  that echo too (`"motion_relink_velocity_weight": 0.25`, `"motion_relink_learned_bonus": 1.6`). The ARM_ print alone
  is NOT sufficient evidence: cell 0 prints it right beside the `os.environ` assignment, so it fires even if nothing
  downstream ever reads the variable. The echo is read out of the live global after the `float()` conversion.
* `sv_mark[tag] = "SV_ARM_HSG200"` makes the existing ">= 4 body-marker lines before 'Prediction completed'" check run
  for them, which is what rejects a linker arm accidentally run on the old 0.949 hsoftfix body.
* `lcflow2` has no env knob to echo, and its distinct silent-failure mode is that the new estimator is present but
  never fires (it needs 4 seeded neighbours within 40 um; on a sparse movie every source can fall back to the base's
  own-step prediction, making the run hsg200 under a new name). Its pattern therefore requires `flow_seeded=[1-9]\d*`,
  not merely the marker.
VERIFIED IN BOTH DIRECTIONS on the real `_res0919/hsg200/biohub-v-hsg200.log`:
* NEGATIVE, rc=1 GATE_FAIL: that log with tag `lcvel2` / `lcbonus2` / `lcflow2` (no ARM_ marker present); an lcflow2
  log with `flow_seeded=0`; an lcvel2 log whose body marker was swapped to `SUBVOXEL_ACTIVE` (wrong body); an lcvel2
  log carrying the ARM_ print while the echo still reads 0.5 (env set, never read).
* POSITIVE, rc=0 GATE_PASS: the same log with the marker lines injected in real runtime format, proving the patterns
  match actual output and the gate is not simply always-failing.
* NO REGRESSION: `hsg200`, `hsz0`, `hsadapt`, `hsg300`, `hsg2c10` still GATE_PASS on their own logs.

### DECISION RULE FOR READING THE FOUR SCORES (set it now, before the numbers arrive)
Board roughness is +-0.001 and the pipeline is bit-deterministic, so a single point is a direction, not a measurement.
* **Any arm >= 0.952**: genuine new best. It becomes the base and we push THAT axis again immediately. Rebase
  everything else onto it before the next slate, the way the linker arms were rebased onto hsg200.
* **`hsg250` or `hsgzc10` <= 0.951**: localization is CLOSED. `hsg250` at 0.949-0.951 confirms the flat top and the
  interior peak at gain 2.00; `hsgzc10` at 0.950-0.951 says the z channel is not a separate lever either. Either way,
  stop spending slots on sub-voxel magnitude. A drop to 0.948 or below on `hsg250` would instead mean the downslope is
  much steeper than the 1-D collapse predicts, which is a fact about the curve, not an invitation to re-probe it.
* **Both `lcvel2` and `lcbonus2` at 0.951**: the linker COST is not the bottleneck, exactly as the 99.87% autopsy
  predicted. Do not turn another dial on the same cost function. Move to structural linker questions or to an axis
  outside the linker entirely.
* **`lcvel2` > `lcbonus2`**: the cost should lean further toward nearest-neighbour. Next probe is weight 0.0, not 0.4.
* **`lcbonus2` > `lcvel2`**: the learned probability is underweighted. Next probe raises the bonus again (2.2) and it
  is worth reviving `lcflow2`, since a better velocity estimate matters more in that regime.
* **Both below 0.949**: the linker axis is closed on both sides in one day, which is a clean, cheap result. Bank it
  and go elsewhere.
* **ALWAYS FIRST**: run `python ops/gate.py <log> <tag>` and do the free `run_stats.csv` count comparison above. An arm
  whose relink counts are byte-identical to hsg200's produced no change at all, and its score must be discarded as a
  replicate rather than read as a tie.

## !!!! 2026-09-19 20:00Z: GAIN 2.0 / CLIP 0.4999 IS AN **INTERIOR OPTIMUM**. A LOOSER CLIP IS HARMFUL. FINE MAP OF 5 ON THE DESKTOP (`~/OneDrive/Desktop/biohub_peak/` + .zip) !!!!
**CORRECTION TO THE SECTION BELOW**: "THE GAIN CURVE IS STILL RISING AT 2.0" (09-19, earlier today) is REFUTED. The
teammate ran the rest of the ladder and the curve turned over immediately past 2.0. `hsg200` (gain 2.00, clip 0.4999)
is a genuine interior peak, not the edge of a rising line. The companion guess in that section, "if gain 3/4/8 all sit
at 0.951 the knob has saturated and only the clip axis remains", did not happen either: 3/4/8 all DROPPED, and the clip
axis turns out to be mostly quantised away (see BAND STRUCTURE below).

### FULL 11-POINT BOARD CURVE (every point is one real submission on the same hfast + sub-voxel body)
| clip | gain | arm | LB | note |
|------|------|-----|----|------|
| 0.4999 | 0.00 | hsz0 | **0.946** | OUR TRUE BASE (offset off, float path on) |
| 0.4999 | 0.50 | hsg050 | 0.945 | below base: the low end is flat/noisy |
| 0.4999 | 1.00 | hsoftfix / hsg100 | 0.949 | |
| 0.4999 | ~1.55 per-axis adaptive | hsadapt | 0.950 | |
| 0.4999 | **2.00** | **hsg200** | **0.951** | **BEST EVER, interior peak** |
| 0.4999 | 3.00 | hsg300 | 0.949 | |
| 0.4999 | 4.00 | hsg400 | 0.949 | |
| 0.4999 | 8.00 | hsg800 | 0.948 | |
| 1.0000 | 2.00 | hsg2c10 | 0.950 | looser clip costs 0.001 |
| 1.0000 | 4.00 | hsg4c10 | **0.937** | CATASTROPHE: loose clip + big gain |
| 0.4999 | 1.00, 5x5x5 window | hswin2 | 0.944 | wider window CLOSED, do not revisit |

**READ.** (1) The lever is worth **+0.005** over its own base (0.946 -> 0.951), and the peak is INTERIOR: 0.949, 0.950,
**0.951**, 0.949 as gain goes 1.0, 1.55, 2.0, 3.0. (2) The clip is a robustifier, not a limitation. Loosening it loses
0.001 on its own (hsg2c10) and loosening it together with a big gain is catastrophic (hsg4c10 0.937, the single worst
arm we have ever submitted on this body). (3) Offline models have now been wrong FOUR times on this axis (exact-scorer
wanted gain 0.5-0.65, shrinkage math wanted 1.4-1.6, a large-radius window was predicted fine and scored 0.944, and
"still rising at 2.0" was wrong too). The board is the judge; do not re-litigate this axis with simulations.

### THE 1-D COLLAPSE (the useful model, but it is a fit to 10 points, not a law)
Ten of the eleven points (hswin2 excluded, it changes the estimator not the magnitude) lie on ONE unimodal curve in
node-weighted realized mean |offset| (downsampled voxels, x1.625 for um):
0.0000 -> 0.946 | 0.0800 -> 0.945 | 0.1600 -> 0.949 | 0.2188 -> 0.950 | **0.2574 -> 0.951** | 0.3007 -> 0.949 |
0.3200 -> 0.950 | 0.3261 -> 0.949 | 0.3733 -> 0.948 | 0.6400 -> 0.937.
Only two points violate monotonicity and both by exactly 0.001. So the surface does not care whether a given magnitude
was produced by gain or by clip: hsg2c10 (0.320), hsg300 (0.301) and hsg400 (0.326) all read 0.949-0.950. Corollary:
"the clip is a separate axis" is NOT supported except at the far corner, where it is confounded with pure magnitude.

### LOG FACTS (pulled to `scratch_kernels/_res0920/<tag>/biohub-v-<tag>.log`; hsz0/hsadapt/hsg200 in `_res0919/`)
EVERY ARM FIRED: each log carries exactly 8 `SV_ARM_<TAG>` lines (4 movies x 2 GPU shards) before "Prediction
completed", `gate.py` returns GATE_PASS on all eight, fallback frames identical in every run (44b6_0b24845f 64,
6bba_05b6850b 1). mean_abs_off_vox / frac_clipped per movie, keyed by pre-filter node count:
| arm | gain | clip | n=26532 | n=33336 | n=7370 | n=76396 | wmean abs off |
|-----|------|------|---------|---------|--------|---------|------------|
| hsz0 | 0.00 | 0.4999 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 (raw estimate still fired: 0.1313/0.1727/0.1810/0.1624) |
| hsadapt | ~1.55 | 0.4999 | 0.1872/0.1503 | 0.2330/0.1439 | 0.2344/0.1396 | 0.2221/0.1569 | 0.2188 |
| hsg200 | 2.00 | 0.4999 | 0.2069/0.2306 | 0.2827/0.2912 | 0.2913/0.3129 | 0.2607/0.2828 | 0.2574 |
| hsg300 | 3.00 | 0.4999 | 0.2410/0.3288 | 0.3320/0.4499 | 0.3394/0.4718 | 0.3041/0.4165 | 0.3007 |
| hsg400 | 4.00 | 0.4999 | 0.2617/0.3880 | 0.3602/0.5424 | 0.3665/0.5621 | 0.3297/0.4947 | 0.3261 |
| hsg800 | 8.00 | 0.4999 | 0.3031/0.5013 | 0.4100/0.7073 | 0.4138/0.7208 | 0.3777/0.6399 | 0.3733 |
| hsg2c10 | 2.00 | 1.0000 | 0.2626/0.0132 | 0.3454/0.0175 | 0.3620/0.0231 | 0.3248/0.0174 | 0.3200 |
| hsg4c10 | 4.00 | 1.0000 | 0.4139/0.2305 | 0.5655/0.2912 | 0.5826/0.3129 | 0.5215/0.2827 | 0.6400 |
* At gain 2 a clip of 1.0 is essentially NON-BINDING (frac_clipped 1.3-2.3%), so hsg2c10 is the pure gain-2 offset field.
* **hsg4c10 IS hsg200 WITH EVERY OFFSET DOUBLED**, component for component: identical frac_clipped to four decimals
  (same clip/gain threshold 0.25) and means exactly 2x. Node counts did NOT move (122772 vs 122766 rows, FINAL within
  0.1%, fallback frames identical, GATE_PASS), so the 0.937 is NOT a detection failure, it is geometry-dependent
  post-processing. Submission diff vs hsz0: median node moves 1.149 um (2 native voxels in y and x) vs hsg200's 0.406,
  12.3% of nodes move >2 um vs 3.7%, 41.2% change written z vs 19.7%, divisions 102 vs hsg200's 76 (hsz0 base 99).
  Mechanism: the node is relocated into a voxel the detector's own NMS rejected while the edge features still index the
  original integer peak, so position and appearance disagree and every micron-threshold stage mis-fires (gap close 5.0,
  SAFE_DIV 9.0/14.0, motion relink, short-track rescue 3.0).
* NOISE FLOOR: the pipeline is BIT-DETERMINISTIC (EDGE_TTA mean_abs_feat_delta identical to six decimals across all
  eight arms, two run days, two Kaggle sessions). The +-0.001 wiggle is therefore metric roughness, not run noise. A
  literal replicate submission would reproduce exactly and measure NOTHING: never spend a slot on one.
* Not pulled: hsg050 has no .log in its Kaggle output and `_res0919/hswin2` is empty, so 0.945 and 0.944 are unverified
  at the marker level.

### **BAND STRUCTURE: THE CLIP AXIS IS MOSTLY QUANTISED AWAY** (new mechanical finding, review pass 09-19)
The offset is added BEFORE `coords[:,1:] *= ds_arr` with ds=(1,4,4), and the writer rounds. So written y/x =
`4*peak + round(4*offset)` and written z = `peak + round(offset)`. Consequences, verified over 2e6 samples and on the
real extracted helper:
* **At a FIXED gain, every clip in [0.375, 0.5) produces IDENTICAL written voxels.** So `hsg2c04` (gain 2, clip 0.40)
  is bit-identical to `hsg200` pre-smoothing, and `hsg3c04` (gain 3, clip 0.40) is bit-identical to `hsg300`
  pre-smoothing. The band edges sit at 4C = 1.5 and 0.5, i.e. C = 0.375 and C = 0.125; clip 0.3749 differs on 73.9%
  of nodes, clip 0.375 does not differ at all.
* Those two arms are NOT no-ops only because `linefit_smooth_output_graph` (weight 0.8, window 2) runs AFTER the offset
  and breaks the integer alignment, re-rounding about 22-27% of nodes by exactly one native voxel. Their board reading
  is therefore a DITHER measurement around 0.951 and 0.949 respectively, which is genuinely useful (it measures the
  metric's local roughness) but it is NOT a clip-axis measurement.
* A y/x offset flips the written native voxel every 0.125 downsampled voxels, not every 0.5. The old note that "an
  offset only changes the written output when it crosses a half-voxel boundary" is WRONG for y/x; it is right only for
  z, where ds_z = 1 and any clip below 0.5 can never flip the rounding (z then moves only indirectly, through the line
  fit, for about 11-20% of nodes).
* FREE ZERO-GPU CHECK when the logs come back: the pre-ILP coordinate manifest hashes must be EQUAL between hsg3c04
  and hsg300 (hsg300's are 7ad1bea839af9b05dc850717 / f780d7f76a08374782a13620 / 852fc25c7834633a2721c1f1 /
  face22e4c5b841b2a68f04db) and between hsg2c04 and hsg200 (67a028b7 / e26d5894 / fab6babf / a454a444). If they match,
  the reading is dither; if not, the band analysis is wrong and that is worth more than the LB point.

### THE FINE MAP: 5 ARMS BUILT, VALIDATED AND ON THE DESKTOP
Folder `~/OneDrive/Desktop/biohub_peak/` (+ `biohub_peak.zip`), one subfolder per arm in RUN ORDER, each with
`kernel.ipynb` (sha256-verified byte copy of `scratch_kernels/v_<tag>/kernel.ipynb`), `notes.txt` and a plain-language
`README.txt` for the teammate. All five are the `v_hsg200` 0.951 body with cell 4 only touched.
| # | arm | change vs hsg200 | marker | predicted | what it settles |
|---|-----|------------------|--------|-----------|-----------------|
| 1 | `hsg250` | gain 2.50, clip 0.4999 | SV_ARM_HSG250 | 0.950 (0.949-0.951) | the one clean gain reading left, on the measured downslope. 15-26% of nodes get a different written voxel. >=0.952 moves the optimum above 2. |
| 2 | `hsgzc10` | gain 2.00, PER-AXIS clip z=1.0000, y/x=0.4999 (new env `BIOHUB_SUBVOXEL_CLIP_ZYX`) | SV_ARM_HSGZC10 | 0.950-0.951 | the only untested direction. y/x bit-identical to hsg200, z re-slices for ~8-12% of nodes. Splits the hsg2c10 confound (z vs y/x). |
| 3 | `hsg2c04` | gain 2.00, clip 0.4000 | SV_ARM_HSG2C04 | 0.950-0.951 | NOT a clip reading (see BAND STRUCTURE): it is a dither re-roll of the 0.951 field. 0.951 = the peak is robust; 0.949 = the whole 0.945-0.951 span is inside rounding noise. |
| 4 | `hsg175` | gain 1.75, clip 0.4999 | SV_ARM_HSG175 | 0.950-0.951 | fills the last gap (hsadapt 0.950 to hsg200 0.951). Moves ~16-19% of nodes but interpolates a 1-count bracket, so it completes the map without deciding anything. |
| 5 | `hsg3c04` | gain 3.00, clip 0.4000 | SV_ARM_HSG3C04 | 0.949-0.950 | intended as the matched-magnitude SHAPE arm; band structure makes it a dither re-roll of hsg300 instead. Run last, drop first. |
Build recipe unchanged: `BUILD_BASE=v_hsg200 python build_multi.py <tag> '<json pairs>'`, marker string appears exactly
2x (the print and the persist check). hsg2c04 / hsg3c04 / hsgzc10 also APPEND the live clip to the marker line
(`clip=%.4f`, or `clip_zyx=` for the per-axis arm), because with the gain unchanged the log could not otherwise prove
which clip ran. `ops/gate.py` now has `need` AND `sv_mark` entries for all five tags; before today it was BLIND to any
unlisted tag and returned GATE_PASS on the zero-offset hsz0 log, i.e. it would have blessed a dead patch. Negative
control to re-run before the teammate day: `python ops/gate.py scratch_kernels/_res0919/hsz0/biohub-v-hsz0.log <tag>`
must print GATE_FAIL for every one of the five.
CAVEAT recorded for the hsgzc10 log: with an array clip, the single headline `frac_clipped` averages a loose z axis in
and is NOT comparable across arms. Compare the y and x entries of `frac_clipped_zyx` instead.
GOTCHA for any future build: `scratch_kernels/_hsoft949/tracking_repo/scripts/predict_unet_transformer.py` is NOT a
pristine predictor, it is a post-run artifact that already carries SUBVOXEL_ACTIVE and the edge-TTA patches. The real
pristine source is `scratch_kernels/_ckpt/supportpack/predict_unet_transformer.py`, sha256
c44e771ba5980b820f93091e03a303c25dfe8f3232e501f54dc9565731c234b9, which is exactly what cell 3's
`_support_expected_sha256` pins. Validate patch pairs against that file, not the _hsoft949 one.

### DECISION RULE FOR READING THESE FIVE
* **>= 0.952 on any arm**: genuine new best, it becomes the base and we push that direction again the next day.
* **0.951**: a TIE, not a win. The board's roughness is +-0.001 and the pipeline is deterministic, so a tie means the
  setting does not matter, not that it is better.
* **<= 0.950**: that direction is CLOSED. Do not spend another slot on it.
* **ALL FIVE TIE AT 0.951** => the sub-voxel axis is CLOSED. Stop mapping it, keep gain 2.00 / clip 0.4999, and move
  to the linker. For the 2026-09-29 FINAL SELECTION pick the setting justified by the SHAPE of the curve (smooth-fit
  peak, gain about 1.9-2.2 at clip 0.4999), NOT the single highest reading: this is a four-movie public split and
  0.951 stands only 0.002 above its neighbours, which is about 2x the roughness floor.
* OPPORTUNITY COST, stated plainly: the leader is at 0.970 and this lever's entire measured span is 0.945-0.951. Even a
  perfect fine map buys 0.001-0.002. Cap this axis at ONE more teammate day.
* NEXT AXIS after this day: the relink/linker knobs already built and reviewed, `v_lcvel` (MOTION_RELINK_VELOCITY_WEIGHT
  0.5 -> 0.25), `v_lcshift` (constant annotation-ward coordinate shift, needs a writer-ceiling check first), `v_lcbonus`
  (MOTION_RELINK_LEARNED_BONUS 1.0 -> 1.6) and `v_lcflow` (neighbourhood velocity estimate). They all sit on the 0.949
  `v_hsoftfix` body and MUST be rebased onto `v_hsg200` before use. `v_lczw` is self-condemned, do not submit it.


## MULTI-MICRON WORKFLOW (stopped at the ship stage 09-19 on request; run id wf_b58cb724-c0d, resume with
`Workflow({scriptPath:"ops/wf_multimicron.js", resumeFromRunId:"wf_b58cb724-c0d"})`, all recon/build/review agents cached)
### Kills (measured with the exact scorer clone, 199 production graphs) - do NOT rebuild these
* The residual-conditioned "+0.08 localization oracle" is DEAD: moving every matched node with residual > R onto its GT,
  edges unchanged, is worth -0.00003 (R=2/3/4). Localization reaches the score ONLY through the linker, and the curve is
  flat until the residual is roughly halved. Never quote +0.08 again.
* Pure coordinate NOISE costs: 0.26 um -0.0001 | 0.5 um -0.0003 | 1.0 um -0.0014 | 2.0 um -0.0113 | 4.0 um -0.0945.
  => any large-radius mean-shift is wildly asymmetric risk. DOWNGRADED/rejected.
* CROSS-MODEL peak averaging is DEAD: the two detectors' error vectors correlate rho 0.73-0.88 (median cosine 0.93-0.97),
  so averaging cancels almost nothing (30 movies, 6,197 triple-matched nodes).
* DEEPCENTER-guided refinement is MEASURED NEGATIVE: at the GT position DeepCenter's centroid sits mean (-0.23,-0.23,-0.32) um
  off with median |offset| 0.94 um, i.e. its centre is NOT the Kaggle annotation. Confirms hengck23's clue.
  Notes on DeepCenter itself (all verified from its source on the box, ~/biohub/deepcenter/source_scripts/):
  it is OUR OWN model repackaged as pilkwang/...-center-prior-v1; trained on the Kaggle .geff annotations; heatmap grid is
  1.625 um isotropic = EXACTLY the detector's downsampled lattice; shipped best.pt is EPOCH 2 of 1000 (epoch 500 val loss
  0.317 = heavy overfit) and the kernel pins that epoch; its README's coordinate contract contradicts its own training code
  by half a pooled voxel (0.61 um/axis) - the training label is mis-registered, do not trust the README formula.
* No public kernel scores >= 0.948 (hard bound: a scored kernel submission would show in its team's best). Five teams at
  >= 0.948 have any public kernel at all. josephadamski91 (0.949) ships a LEARNED coordinate-offset regressor inline
  (v1284_coordinate_refinement.py) - the closest public analogue of our lever, legitimate, worth reading next time.
### Arms BUILT and reviewed (all mechanically clean, none submitted) - NOTE: built on v_hsoftfix (0.949), so REBASE onto
`v_hsg200` (0.951) before using: v_lcvel (MOTION_RELINK_VELOCITY_WEIGHT 0.5->0.25), v_lcshift (constant annotation-ward
coordinate shift), v_lczw (anisotropic z weight 0.75 in the relink metric; reviewer says DO NOT SUBMIT, self-condemned),
v_lcbonus (MOTION_RELINK_LEARNED_BONUS 1.0->1.6), v_lcflow (neighbourhood velocity estimate instead of single-cell),
v_lcstack. Reviewer verdicts: lcvel and lcflow are "not slot-worthy alone"; lcshift needs a writer-ceiling check first.
=> The relink/linker knobs are the honest next axis after the gain ladder, but each is priced at +-0.002 at best.

## !!!! 2026-09-19: **0.951** = `hsg200` (sub-voxel gain 2.0). ~~THE GAIN CURVE IS STILL RISING AT 2.0~~ !!!!
**[SUPERSEDED 2026-09-19 20:00Z, see the top section]** The curve is NOT still rising: gain 3.00 -> 0.949, 4.00 -> 0.949, 8.00 -> 0.948. Gain 2.0 / clip 0.4999 is an INTERIOR optimum. Everything below is kept as the record of what we believed at the time.
Teammate ran the whole ladder (09-18/19). Public LB, all on the same body (hfast + sub-voxel patch):
| gain | arm | LB |
|------|-----|----|
| 0.0 (offset off, float path on) | hsz0 | **0.946** = OUR TRUE BASE |
| 0.50 | hsg050 | 0.945 |
| 1.00 | hsoftfix | 0.949 |
| ~1.55 adaptive per-axis | hsadapt | 0.950 |
| **2.00** | **hsg200** | **0.951 <- NEW BEST** |
| 1.00, 5x5x5 window | hswin2 | 0.944 (wider window CLOSED) |
READ: (1) the refinement is worth **+0.005** over its own base, not +0.002: hsz0 0.946 proves the fast/float base is
0.946, NOT the 0.947 hfusion number we had been differencing against. (2) The curve is MONOTONE RISING from 1.0 to 2.0
and did NOT turn over where every offline model said it would. Both offline predictions were wrong AGAIN (the exact
scorer wanted gain 0.5-0.65, the shrinkage math wanted 1.4-1.6; the board says >= 2.0). Offline gates remain useless.
    [CORRECTION 09-19 20:00Z: read (2) is half wrong. Rising from 1.0 to 2.0 is right, "the board says >= 2.0" is not:
    it turns over AT 2.0 (3.0 -> 0.949). The peak is interior and the offline models were wrong in BOTH directions.]
(3) hsg050 0.945 < hsz0 0.946 means the low end is flat/noisy; the signal lives at the HIGH end.
NEXT LADDER BUILT + upload folder `~/OneDrive/Desktop/biohub_gain2/` (+ .zip), all validated (1 cell changed each,
every code cell compiles, markers unique, ids set):
| # | arm | change vs hsg200 | marker |
|---|-----|------------------|--------|
| 1 | hsg300 | gain 3.00 | SV_ARM_HSG300 |
| 2 | hsg2c10 | clip 0.4999 -> 1.0000 at gain 2 (OPENS THE Z RE-SLICE CHANNEL: clip <= 0.5 can never flip z rounding) | SV_ARM_HSG2C10 |
| 3 | hsg400 | gain 4.00 | SV_ARM_HSG400 |
| 4 | hsg4c10 | gain 4.00 + clip 1.0000 | SV_ARM_HSG4C10 |
| 5 | hsg800 | gain 8.00 (guard widened to 10), saturation limit = "move every peak a half voxel along the logit gradient" | SV_ARM_HSG800 |
Knobs live in cell 4 of v_hsg200: env BIOHUB_SUBVOXEL_GAIN_MODE/GAIN_FIXED/CLIP + `_sv_gain()` guard (0..4, widened to
0..10 for hsg800) + `np.clip(sa, -_SV_CLIP, _SV_CLIP)`. Build with `BUILD_BASE=v_hsg200 python build_multi.py <tag> ...`
(marker string appears 2x: the print and the persist check).
DECISION RULE: any arm > 0.951 becomes the new base and we push that axis again; the first arm that drops closes that
direction. If gain 3/4/8 all sit at 0.951 the knob has saturated and only the clip axis remains.
    [OUTCOME 09-19 20:00Z: gain 3/4/8 did NOT sit at 0.951, they dropped to 0.949/0.949/0.948, so the knob did not
    saturate, it turned over. And the clip axis is largely quantised away: at a fixed gain every clip in [0.375, 0.5)
    writes the SAME integers, because written y/x = 4*peak + round(4*offset). See the top section, BAND STRUCTURE.]

## !!!! 2026-09-18 13:00Z: THE SUB-VOXEL LEVER IS MEASURED. CEILING IS ~+0.001. LADDER OF 5 IS ON THE DESKTOP !!!!
Three independent measurement passes (box CPU exact-scorer clone, synthetic estimator study, real production logs)
now bound this lever end to end. Read this section before spending any of the 5 daily team slots.

### 09-17 BOARD (teammate arunendratripathi03, his quota, 4 arms)
| arm | public LB | vs 0.947 | read |
|-----|-----------|----------|------|
| **hsoftfix** | **0.949** | **+0.002** | sub-voxel 3x3x3 soft-argmax on the blended det logits. STILL OUR BEST. |
| ret80f | 0.946 | -0.001 | retention 0.90 -> 0.80 CLOSED |
| prim300 | 0.943 | -0.004 | public 300ep primary CLOSED (our 50ep primary is better on this body) |
| hdet95 | 0.946 | -0.001 | DET axis CLOSED ON BOTH SIDES (0.94/0.95 low, 0.975/0.98 high; 0.965 is the peak) |
| tta8z | 0.936 | -0.011 | Z-flip-only TTA CLOSED (the rot90/transpose views matter) |

Every non-localization axis on that list is closed. 123+ teams sit at 0.947; leader 0.970.

### WHAT THE MEASUREMENTS SAY (and what they REFUTE)
1. **SHRINKAGE IS 0.647, NOT ~0.80.** The 0.949 run's own printed `SUBVOXEL_ACTIVE` lines give mean_abs_off_vox
   0.1313 / 0.1727 / 0.1810 / 0.1624 (4 movies, 143,634 nodes, mean 0.1618); `data/out_hsoft` gives 0.1615 over 8
   movies. A true sub-voxel residual is uniform on [-0.5, 0.5], so an unbiased estimator must print 0.2500.
   Recovery = 0.1618 / 0.25 = 0.647, and the two runs agree to 0.001. Moment-matched gain = 1.55.
   There is NO bias, only multiplicative shrinkage (|bias| < 0.006 vox in all 72 synthetic regimes). Analytically a
   bare 3x3x3 softmax maxes out at 0.926 recovery at ANY logit scale, so a gain is mandatory, not a hack.
2. **THE PAYOFF CURVE FOR WRITTEN COORDINATES IS FLAT AT ZERO.** Exact scorer clone
   (`~/biohub/annot_prior/score_lib.py`, validated to 0.0 diff), 199 production graphs, paired-movie bootstrap.
   Base insample199 = 0.917332, out-of-sample proxy loeo71 = 0.667721. Moving EVERY predicted node all the way onto
   its matched GT and rematching: dScore -0.00003 [-0.00009, +0.00000] in sample and exactly +0.00000 out of sample,
   while the mean residual falls 1.91 -> 0.00 um. Slope -0.00001 per um.
   Why: 82.0% of matched GT nodes have exactly ONE pred within the 7 um cap (mean 1.20 candidates), only 1.07% of
   pairs are contested, only 0.85% sit beyond 6 um, and edge TP is `(match[src], match[dst]) in gt_edge_set`, a
   function of WHICH node matched WHICH, never of distance. The metric is binary in localization and already saturated.
   **RETIRED: the "+0.08 adjEJ if every GT cell were localized to <=2 um" autopsy oracle.** It does not reproduce
   against the official scorer. That oracle moved predictions onto GT, so it also fixed recall and precision.
3. **OVER-CORRECTION IS THE ONLY THING THE METRIC NOTICES.** The same reachable magnitude in the WRONG direction
   costs -0.02463 in sample and -0.04217 out of sample; a full-scale U(-0.5, 0.5) dither costs -0.00421 / -0.00912.
   So this axis is a one-sided bet: no prize, real downside.
4. **Z IS STRUCTURALLY UNREACHABLE IN THE OUTPUT.** ds_arr = (1,4,4) and scale (1.625, 0.40625, 0.40625) um, so the
   downsampled voxel is ISOTROPIC 1.625 um and the +-0.5 clip is +-0.8125 um per axis. A z offset is multiplied by 1,
   so `max(0, int(round(x)))` can only move z when |off| >= 0.5, which happened for 0.02% of nodes. y and x are
   multiplied by 4 and move whenever |off| >= 0.125, which happened for 53.8%. Written z RMS is pinned at
   1.625/sqrt(12) = 0.4691 um forever and accounts for 86.6% of the remaining squared error.
   Z is not entirely inert: linefit smoothing runs AFTER the offset (25,614 of 25,621 nodes smoothed) and turned the
   sub-voxel bias into ~11% of nodes moving exactly +-1 native slice. That is a side effect, not a lever.
5. **WRITTEN-COORDINATE HEADROOM, in um of 3D RMS:** no refinement 0.8229 -> the 0.949 run 0.5705 -> best gain setting
   0.5106 -> perfect sub-voxel oracle 0.4976. The 0.949 run already took 77.4% of that gap. After a gain fix only
   0.013 um of the original 0.325 um remains. **The estimator end of localization is essentially closed.**
6. **THE FLOAT CHANNEL IS THE ONLY THING NEITHER HARNESS SCORED.** The patch skips the int16 cast, so coords reach
   `build_graph` as float32 and motion-relink 5.5 um, gap-close 5.0 um, the division geometry filter and the 14 um
   edge cap all read sub-voxel positions INCLUDING z. Float offset RMSE improves 0.3184 -> 0.0998 um under an adaptive
   gain. The payoff-curve harness perturbed already-built graphs and re-ran only the scorer, so it cannot see this.
   This is the only surviving mechanism by which the +0.002 can be real. The learned EDGE predictor is NOT affected
   either way: edges are built from `coords_so_far`, the int16 peak array, before the offsets are applied.
7. **TEMPERATURE IS DEAD.** wum3D at T = 0.50 / 0.75 / 1.00 / 1.50 / 2.00 / 3.00 =
   0.5822 / 0.5680 / 0.5705 / 0.6016 / 0.6496 / 0.7553. The best case, T=0.75, buys 0.0025 um against the gain's
   0.0599 um, and recovery is monotone decreasing in T, so T < 1 is just a gain with extra nonlinearity.
   Do not spend a slot on a temperature arm.
8. **RADIUS 2 AND CENTRE-OF-MASS ARE DOMINATED.** 5x5x5 softmax gives 0.5374 um (clip 0.5) or 0.5333 (clip 1.0), both
   worse than gain-on-radius-1 at 0.5141. Gaussian distance weighting is actively harmful (0.5771 / 0.6088 / 0.6484 at
   tau 1.4 / 1.0 / 0.8) because it re-adds the shrinkage we are trying to remove. Centre-of-mass above a fraction of
   the peak never beats baseline (0.6394 / 0.5997 / 0.5751 at 0.3 / 0.5 / 0.7) and its radius-2 variant has a 0.9098 um
   worst case, which is worse than doing nothing at all.
9. **CORRECTION to the EXP4 note below ("jitter 1.0->0.4px = +0.014 adjJ, port refine_centroids = #1 lever").** That is
   a SIMULATION (`kaggle/exp_sim2.py` EXP4 on 24 local 44b6 GT movies with GT positions used as detections), not a
   measurement of refine_centroids, and its units are MICRONS, not px (`det_pos + N(0, jit) / SCALE`, with SCALE in
   um per voxel; the print label is wrong and this file inherited the error). The curve saturates at 0.7 um: adjJ
   0.8805 / 0.9238 / 0.9372 / 0.9377 / 0.9393 at sigma 1.5 / 1.0 / 0.7 / 0.4 / 0.0 um, so below 0.7 um only +0.002
   total remains. Intensity-weighted centroid is also a DIFFERENT lever and does not transfer (see item 8, and forum
   740145 where hengck23 says the Kaggle GT is Ultrack-derived and "sometimes annotates cell corners", i.e. the
   intensity centroid is the wrong target, which is why parabolic-on-image scored -0.036). A complete public CPU
   implementation exists if we ever want it: `refine_all_nodes` at line 1670 of
   `scratch_kernels/_loc0918/vmerckle_biohub-cand-refine-clip-bounds/biohub-cand-refine-clip-bounds.ipynb`
   (WIN_Z 1, WIN_YX 4, p20 baseline, 2.0 um Euclidean shift cap). Final-B diversification material at best.
10. **NEW 09-18, MEASURED HERE: DO NOT CALIBRATE THE ESTIMATOR FROM THE SUBMISSION FILE.** Two adversarial reviews
    decoded `y mod 4` from the 0.949 submission, got mean|off_y| ~ 0.223, and concluded that y/x recovery is already
    ~0.90 so only a gain near 1.10 is available. That decode is invalid, because the NO-SUB-VOXEL baselines show the
    same spread. Node rows only:
    * hsoftfix 0.949 (sub-voxel ON): y mod4 {0:38186, 1:29722, 2:24748, 3:30123} -> mean|off_y| ~ 0.2226, x ~ 0.2275
    * hfusion 0.947 (NO sub-voxel): y mod4 {0:35577, 1:36813, 2:13801, 3:36603} -> mean|off_y| ~ 0.2057, x ~ 0.2156
    * hsoft 0.946 (patch inactive on test): y ~ 0.2054, x ~ 0.2155
    So roughly 92% of the off-lattice spread is LINEFIT SMOOTHING, not the sub-voxel offset; the offset's incremental
    contribution is +0.017 (y) and +0.012 (x). The only direct measurement of the estimator is its own printed
    mean_abs_off_vox, which says recovery 0.647. Reproduce with `scratchpad/modcheck2.py`.
11. **NODE COUNTS DID NOT MOVE**, so the 0.949 is pure J and not the N_pred multiplier: hsoftfix FINAL
    25621 / 20720 / 6157 / 70281 (122,779) versus the hfast reference 25637 / 20721 / 6152 / 70284 (122,794), a drift
    of -0.012%; fallback frames 64 + 1 match the reference exactly; `ppsweep_selected.json` = base, no overrides.
12. **THE BASE CONFOUND IS STILL OPEN AND IS THE LEADING ALTERNATIVE EXPLANATION.** `hfast` was never run on Kaggle
    and there is no `data/out_hfast/`, so hsoftfix's +0.002 is measured against `hfusion`, a DIFFERENT GPU run, on a
    3-decimal board. "hfast == hfusion" is an argument (validator off plus TIGHT_UM 5.5, which hfusion's ppsweep also
    selected), not a measurement. On this body a postprocess-selection difference alone has moved the board a full
    tick: hsoft scored 0.946 with its patch inactive on test purely because its in-kernel sweep picked
    combo(relaxed9 + tight55).

### HONEST CEILING
The 0.949 run bought 0.2524 um of written-coordinate 3D RMS over the 0.947 base and that coincided with +0.002. The
best remaining gain fix buys a further 0.0599 um, i.e. 23.7% more of the same quantity, so roughly **+0.0005 if the LB
response is linear**, which is half a board tick. The exact-scorer harness says the written channel is worth **0.000**
and that a realistic patch simulation PEAKS at gain 0.5 to 0.65 and declines above it. The two bodies disagree about
the SIGN of a gain increase. **This lever will not take us from 0.949 to 0.970.** The remaining real headroom is node
recall (0.9777, i.e. 2.2% of GT nodes have no pred within 7 um), divJ (0.0868), and the crowded / merged-peak regime
(pool_kernel_um 3.0 on a 1.625 um isotropic grid gives only a 4.875 um suppression window for 5 to 8 um nuclei; a
neighbour at 2 voxels triples the error for EVERY method including no refinement).

### THE LADDER (built, adversarially reviewed, staged for the teammate)
`C:/Users/eeshs/OneDrive/Desktop/biohub_subvoxel/` holds 5 folders, each with `kernel.ipynb` (sha256 verified against
its `scratch_kernels/v_*/` source), a `notes.txt` (title, the 4 dataset addresses, GPU T4 x2 / Internet OFF /
Persistence none, the marker line, the exact submission description, how to read the score) and a plain-language
`README.txt`.
Every arm holds CLIP 0.4999 instead of 0.5: `np.clip` can emit exactly 0.5 and `round()` is half-to-even in both numpy
and python, so for an ODD z index round(k + 0.5) = k + 1, a full 1.625 um jump the wrong way. It is inert at gain 1.0
(0.02% of nodes clip) but worth +0.0016 um at gain 1.40, +0.0054 at 1.60 and +0.0260 at 2.00. Bug avoidance, not a
second variable.

| rank | folder | setting | expectation | what it settles |
|------|--------|---------|-------------|-----------------|
| 1 | `1_hsz0` | gain 0.0 | 0.947 (0.946-0.949) | resolves the base confound. PROBABLY COSTS NO SLOT. |
| 2 | `2_hsadapt` | per-axis adaptive, ~1.55 effective | 0.949 (0.948-0.950) | the gain direction the shrinkage math chose; the only setting that never loses across 72 regimes and 81 stress cases |
| 3 | `3_hsg200` | gain 2.00 fixed | 0.947 (0.945-0.949) | the DOWNSIDE slope; the arm most likely to move the board by a resolvable amount |
| 4 | `4_hswin2` | 5x5x5 window, no gain | 0.948 (0.947-0.949) | independent estimator family; cross-check that the board responds to error itself and not to our formula |
| 5 | `5_hsg050` | gain 0.50 fixed | 0.949 (0.948-0.949) | the direction the exact scorer preferred; with 0 / 0.5 / 1.0 / adaptive / 2.0 we get a 5-point curve in one day |

Run order at 2 in flight: (hsz0, hsadapt), then (hsg200, hswin2), then (hsg050).
`v_hspin` was built and REJECTED as an effective no-op: pinning the clip per axis at 0.4999 / 0.1249 / 0.1249 freezes
every written coordinate, and the only surviving channel is the post-hoc relinker, which the 0.949 log already bounds
at 25 nodes out of 122,800.
KNOWN RISK ON hswin2: a 5x5x5 window reaches +-3.25 um while the measured node-to-node p10 is about 3.8 downsampled
voxels, so it can swallow a neighbour. Drop this arm first if slots get tight.

### hsz0 COSTS NO SLOT IF WE CHECK FIRST
Run it, pull it, then compare BEFORE submitting.
Cheapest check (pre-linker, bit level, no slot, no waiting): `BIOHUB_DIAGNOSTIC_ARM` is on, so each run writes
`detector_coordinates_harmonic_association_production_*.jsonl` carrying a sha256 of the int16 pre-graph coords.
hsz0's four test shas must equal hsoft's EXACTLY: 44b6_0113de3b `0530845ee4e4d065`, 44b6_0b24845f `e84f4e67b2fdfa53`,
6bba_05b6850b `ae49b787ba401ce0`, 6bba_05db0fb1 `2516386d5a22524d`.
Then `python scratch_kernels/compare_submissions.py data/out_hfusion/submission.csv <pull>/submission.csv`.
SUBMIT ONLY ON FAST_MISMATCH. **The old FAST_OK rule ("counts within 0.2%") was NOT sufficient and has been tightened
to row equality**: hfusion versus the real 0.949 hsoftfix has a worst per-dataset count difference of only 0.1244%, so
the legacy rule would have called them the same submission, while 58.38% of shared nodes actually moved. hsoft versus
hfusion moved 1.61% of nodes and lost a full tick. Read the new "moved N (x%)" line: anything in the 0.0x% range is GPU
nondeterminism, not a real base difference.

### GATE (`ops/gate.py`) NOW COVERS EVERY ARM
Added 09-18: `hsg200`, `hsg050` and `hswin2` marker regexes plus their entries in `sv_mark`, so the ">= 4 marker lines
before 'Prediction completed'" liveness check fires for them too. Before this, those three tags passed on node counts
alone, and a run whose sub-voxel block silently did nothing would have read GATE_PASS and burned a slot. Each pattern
pins the arm's own knob (gain=2.00 / gain=0.50 / win=5) AND requires a non-zero mean offset. Regression tested: the
real hsoftfix log still GATE_PASSes as `hsoftfix`, GATE_FAILs as `hsg200`, forged per-arm logs pass, and zero-offset
twins of those forged logs fail.

### PRE-REGISTERED DECISION RULE (write the outcome here; do not re-litigate after seeing the number)
* **hsz0 row-identical to hfusion locally, or scoring 0.947** -> the base is 0.947 and the +0.002 IS the patch. Given
  item 2, that means it arrived through the FLOAT channel (item 6), not the written coordinates. Read the gain curve as
  real and keep one 09-19 slot for a fixed gain of 1.55 if the curve is rising.
* **hsz0 scoring 0.948 or 0.949** -> the +0.002 is base drift, not localization. CLOSE THE WHOLE AXIS. Keep hsoftfix as
  Final A on its measured number, move every remaining slot to node recall and divJ, and do not build another sub-voxel
  arm.
* **Any arm below 0.949** -> that setting is dropped, permanently. No re-runs, no "it was noise".
* **The row 0 / 0.5 / 1.0 / adaptive / 2.0 comes back FLAT at 0.949** -> the board cannot resolve this knob at 3
  decimals. Close the axis, keep hsoftfix as Final A, and record the 09-17 +0.002 as unexplained.
* **Monotone up to hsadapt and down at hsg200** -> the optimum is near the moment-matched 1.55. ONE more fixed-gain arm
  at 1.4 to 1.6 on 09-19, then stop.
* **hsg050 (0.5) >= hsadapt AND >= hsoftfix** -> the exact-scorer simulation was right, we were already
  over-correcting, the shrinkage story is falsified and the axis closes at the low end.
* **hsg200 <= 0.946** -> over-correction is punished as measured, the safe range stops near 1.5, and this bounds every
  future localization knob. That is a USEFUL loss: record it and move on.
* **A marker line missing, or mean_abs_off_vox not in its predicted band** -> the run is VOID, not a score. Do not
  submit it and do not read it as evidence about the knob.
* **FINAL SELECTION (2026-09-29):** A = hsoftfix 0.949 unless an arm beats it outright. B = hfusion 0.947 as the safe
  control, or the best genuinely DIFFERENT arm. The public intensity-centroid `refine_all_nodes` port is the only
  diversified candidate we have and it is expected neutral to negative, so B stays hfusion unless something changes.


## !!!! 2026-09-18 04:30Z: NEW BEST **0.949** = `hsoftfix` (SUB-VOXEL SOFT-ARGMAX). THE LOCALIZATION AXIS IS LIVE !!!!
Teammate arunendratripathi03 ran 4 arms on his own quota (09-17 20:00-20:40Z submissions):
| arm | public LB | vs 0.947 | read |
|-----|-----------|----------|------|
| **hsoftfix** | **0.949** | **+0.002** | sub-voxel 3x3x3 soft-argmax on the blended det logits, applied BEFORE test prediction. FIRST score above the public plateau. |
| ret80f | 0.946 | -0.001 | retention 0.90->0.80 CLOSED |
| prim300 | 0.943 | -0.004 | public 300ep primary CLOSED (our 50ep primary is better on this body) |
| tta8z | 0.936 | -0.011 | Z-flip-only TTA CLOSED (the rot90/transpose views matter) |
| hdet95 | 0.946 | -0.001 | DET axis CLOSED ON BOTH SIDES (0.94/0.95 low, 0.975/0.98 high; 0.965 is the peak) |
=> Every non-localization axis is closed. hsoftfix confirms the 09-06 autopsy: localization, not linking, is the headroom
(~~residual-conditioned oracle = +0.08 adjEJ if every GT cell were localized to <=2 um~~ **RETIRED 2026-09-18: that
oracle does not reproduce against the official scorer. On 199 production graphs, moving every pred node onto its
matched GT is worth -0.00003 in sample and +0.00000 out of sample. The old oracle also fixed recall and precision,
which is where its +0.08 came from. See the top section item 2.**).
The patch (cell 4 of v_hsoftfix, 4 anchors into the predictor): 3x3x3 softmax over the FINAL BLENDED det logits, NO
temperature, offset zeroed on boundary peaks, clipped +-0.5 in DOWNSAMPLED grid units, added before `coords *= ds_arr`,
int16 cast skipped so coords stay float; edge features still index INTEGER peaks; the writer still rounds to int.
KNOWN: ~~a synthetic test of this exact code recovers only ~80% of the true offset~~ **CORRECTED 2026-09-18: recovery
is 0.647, measured from the run's OWN printed mean_abs_off_vox (0.1618) against the 0.2500 a uniform sub-voxel residual
forces; two runs agree to 0.001. So it under-corrects MORE than this said, and the moment-matched gain is 1.55.**
Of the "obvious next knobs", only GAIN survived measurement: temperature is redundant and monotone worse for T>1, and
a radius-2 window is dominated by gain-on-radius-1. Float writer is dead (hfloat 0.937); parabolic is dead (-0.036).
NEXT: workflow `biohub-subvoxel-push` (running 09-18) measures the estimator bias and the exact payoff curve on the box
CPU, then builds a 4-6 variant ladder into `~/OneDrive/Desktop/biohub_subvoxel/` for the teammate (5 slots free on 09-18).
FINAL SELECTION now: A = hsoftfix (0.949) unless a variant beats it; B = hfusion 0.947 as the safe control, or the best
genuinely-different arm. hfast was never run on Kaggle; hsoftfix's 0.949 implies the fast base is intact (it is hfast + patch).

### ARM `v_hsz0` (built 09-18): the control that resolves the base confound, and it probably costs NO slot
`scratch_kernels/v_hsz0/` = v_hsoftfix with `BIOHUB_SUBVOXEL_GAIN_MODE='zero'`, a new `_sv_apply_gain` branch that
multiplies the clipped soft-argmax offset by exactly 0.0. Nothing else moves: same 4 anchors, same clip, same boundary
rule, same estimator, and the FLOAT PATH STAYS (`_SV_ON` is still true, so the int16 cast is still skipped and coords
reach build_graph as float32). One change, not two. It prints the normal `SUBVOXEL_ACTIVE` line (so the >=4 gate check
still applies) plus `SV_ARM_HSZ0 nodes=N mean_abs_off_vox=0.0000 mode=zero raw_mean_abs_off_vox=R`, where R is the RAW
pre-gain mean (expect ~0.16): that proves the estimator still fired and only the APPLIED offset is zero. The predictor
also raises if `|_sv_off|.max() != 0`.
WHY: hfast has never been scored on the board and there is no `data/out_hfast/`, so "hfast == hfusion" is an argument,
not a measurement, and hsoftfix's +0.002 is measured against hfusion, a different GPU run. This class of drift is worth
a full tick on this body (hsoft scored 0.946 with its patch inactive on test, purely because its in-kernel sweep picked
combo(relaxed9+tight55)). hsz0 output should be the hfast base exactly, since adding 0.0 and staying float32 does not
change any value (integers are exact in float32); the only residual difference from hfast is the DTYPE reaching
build_graph.
PROCEDURE (cheap): teammate runs it, we pull submission.csv, then
`python scratch_kernels/compare_submissions.py data/out_hfusion/submission.csv <pulled>/submission.csv`.
SUBMIT ONLY IF THE ROWS ARE NOT EXACTLY EQUAL. Row-identical means hfast == hfusion and the float dtype is inert, so
the 0.949 is the offset and no slot is spent. `python ops/gate.py <log> hsz0` checks FINAL counts plus both markers.
ADVERSARIAL REVIEW 09-18 (independent re-derivation, no build changes needed): only cell 4 differs from v_hsoftfix
(5 hunks, 37 +/- lines); the 4 runtime anchors each match EXACTLY 1x on the pre-sub-voxel text reconstructed by
reverse-applying hsoftfix to the real 0.949 runtime file (that replay reproduces the 0.949 file byte-identically);
the estimator body is byte-identical to the 0.949 helper apart from the wrapped `return`, so the window is still
3x3x3 with pad 1 (no widened-window indexing risk, runtime delta ~0); `_sv_apply_gain` with mode 'off' or unset is
bit-identical to the 0.949 helper and mode 'zero' returns exact +0.0; the writer path `max(0, int(round(ds*peak)))`
was exercised and equals the hfast integer path exactly; `ds_arr` is [1,4,4] and max written coord is 252, so the
int16 cast hfast still performs cannot overflow and the two paths agree; the patch is written at cell-4 line 326 and
prediction launches at line 531, so the hsoft "patch applied after the test prediction" trap does NOT apply here;
cell 1 pins no BIOHUB_SUBVOXEL_* key, cell 3's predictor sha256 pin is the PRISTINE file checked before cell 4
patches, and cell 6 pins no coordinate value; every subprocess gets `{**os.environ, ...}` so GAIN_MODE reaches the
shards and the in-predictor `|_sv_off|.max() != 0` raise cannot fire.
ZERO-SLOT CHECKPOINT, better than comparing submission.csv: BIOHUB_DIAGNOSTIC_ARM is on, so each run writes
`detector_coordinates_harmonic_association_production_*.jsonl` with a sha256 of the int16 pre-graph coords. hsoft
(0.946) is the BASE detector, because its sub-voxel patch landed after the test prediction. hsz0's four test-dataset
shas must equal hsoft's EXACTLY: 44b6_0113de3b 0530845ee4e4d065, 44b6_0b24845f e84f4e67b2fdfa53,
6bba_05b6850b ae49b787ba401ce0, 6bba_05db0fb1 2516386d5a22524d (hsoftfix's differ, as the offsets moved the coords).
A match proves both that the detector is bit-reproducible across GPU runs and that hsz0 reaches build_graph with the
base coords, so any later submission.csv difference is the LINKER, not noise. A mismatch means do not read the
submission comparison as a config result. Supporting evidence already on disk: hsoft and hsoftfix agree on all four
row counts (26532/33336/7370/76396) across two separate runs.
GATE TIGHTENED 09-18: `need["hsz0"]` now also requires `raw_mean_abs_off_vox=0.<non-zero>`. Without it a run where the
estimator itself degenerated to zeros would GATE_PASS and be mistaken for the intended control (expected raw mean is
0.13 to 0.18, from the 0.949 log). Verified: real hsoftfix log still GATE_PASS, a synthetic hsz0 log passes, and the
same log with raw_mean 0.0000 now GATE_FAILs.

## STATE 2026-09-17 ~05:40Z (laptop clock is IST, UTC+5:30) - ORCHESTRATOR STOPPED; TEAMMATE RUNS THE W1 ARMS; NEW 0.97 HYPOTHESIS
* User: our GPU quota "won't come back any time soon"; a TEAMMATE will commit + submit the notebooks on their own quota.
  => `ops/postreset_w1.sh` was STOPPED (pids 1007/1009/1017 killed, verified gone) so our account never double-submits
  into the team's shared 5/day. Do NOT relaunch it while the teammate owns the queue.
* All W1 arms (hfast, ret80f, prim300, hsoftfix, tta8z, t60f, hdet94f) use ONLY public datasets (3x pilkwang +
  hongdaekim 300ep for prim300), zero `eeshsaxena` refs: portable. Bundle being built at `teammate_bundle/`
  (+ `teammate_bundle.zip`, README for the teammate, `EESH_NOTES.md` for gating their runs). Legal only if the
  teammate is ON THE TEAM (private code sharing outside a team is prohibited); check the merger deadline.
* Evidence that submission reruns do not need the submitter's quota: hdet95 was submitted 09-17 00:28Z, 8 h after
  our quota ran out (09-16 16:23Z), and was accepted (PENDING).
* NEW HYPOTHESIS (user: "top is 0.97, not GPU training"): the node-count multiplier `1 - 0.1*(N_pred/N_est - 1)` has
  no cap and counts ALL predicted nodes, while GT is ~1 tracked cell per movie (44b6_0113de3b: 52 GT nodes vs
  N_est 25,755) and edges between unmatched detections are free. If annotated cells are PREDICTABLE (crop centered
  on the annotated lineage, track length, start at t=0...), pruning the rest lifts the multiplier from ~1.025
  toward 1.10 without losing J: up to ~+0.07, and +0.023 would explain 0.970. Never examined before (no notes on
  annotation position). Workflow `biohub-annotation-prior` running: GT geometry on 199 movies, exact scorer from
  source, cross-embryo prune rules on box CPU, 3-lens skeptic verify, builds `v_ap_*` + `ANNOT_PRIOR_REPORT.md`.
  NOT the old 08-28 abstention lever (that pruned EDGES with a learned CNN edge model).
* ANNOTATION-PRIOR HYPOTHESIS = REFUTED (FINAL 09-17 ~07:30Z, full write-up `ANNOT_PRIOR_REPORT.md`; 0 rules survived, no
  kernels built). Geometric family (32 rules): best cross-embryo +0.0004, LOEO44 +0.0000. Weighted in-sample multiplier is
  1.006, not 1.025 (adjEJ weights = TP+FP+FN per movie).
  Box work in ~/biohub/annot_prior (score_lib.py reproduces the OFFICIAL scorer exactly, box repo HEAD 075fc5f).
  - Scorer facts: N_pred = every node row; one-to-one max-weight matching per frame, 7 um; only dt==1 edges; out-degree
    capped at 2 by CSV row order; edge between two unmatched nodes FREE; edge with one matched endpoint is FP only if
    that GT node has a GT edge on that side. Local vendored metric (data/out_hsoft/tracking_repo) is OLDER: use the box.
  - GT geometry (199 movies, all (100,64,256,256)): 44b6 crops are centred on one annotated cell at t=50 (voxel
    32,128,128 in 71/71 movies) but that track is only ~31% of 44b6 GT nodes; 6bba crops are NOT centred (3/128).
    44b6 ~4 GT tracks / 214 nodes per movie, 6bba ~29 tracks / 826 nodes. Host: evaluated on "a random sparse subset".
    Likely origin: random mosaic sparse-label channel (Ultrack paper) = invisible in the dense channel we get.
  - Oracles (production graphs, exact): keep matched nodes +0.130; keep whole tracks touching GT +0.072 (pure multiplier).
    The old "+0.024 oracle cap" was WRONG. But break-even needs a pruned set with annotated-edge density <= ~0.06-0.10 of
    average; best feature bin reaches 0.17-0.21 in-sample and 0.55 on honest LOEO.
  - 188 exact-scored track-structure variants + 14 positional rules: best cross-embryo min +0.00065 (drop lowest 2% by
    span x edge prob), NEGATIVE on honest LOEO44 (-0.0064, CI excludes 0). Every dose > ~2% of nodes is negative.
    => No test-time-available prior identifies annotated cells. Node-count pruning is CLOSED as a route to 0.97.
    The leader's gains must come from J (detection/linking quality), consistent with the +0.08 localization oracle.
* 0.948/0.949 CLUSTER HUNT DONE (31 agents, evidence `scratch_kernels/_intel0917b/`): NO shared trick. Tie-order audit:
  inside 0.947 there are runs of 235/163/42 teams in submission-id order (= identical copies); 0.948 tier has 27 runs,
  longest 5 (random ~27.5) => ~77 teams with DIFFERENT unrounded scores. Tier = best-of-many near-neutral variants on a
  3-decimal board (median subs: 22 at 0.947, 47.5 at 0.948, 66 at 0.949). Real tier counts 09-17 05:40Z: 571 at 0.947,
  54 at 0.948, 23 at 0.949, 74 at >= 0.950. No pilkwang dataset version since July; all 994 kernels top out at 0.947.
  Only visible case: SailorRen 0.948 = learned gate on safe-division proposals (+0.0000036 locally). Spec for an exact
  replica (`g1b`: DC SAFE_DIV 0.20 + in-kernel logistic gate, assert n_pos 147 / n_neg 2876, loss 0.2725900686) is in the
  workflow output; LOW priority (display lottery, ~0 private). Do NOT queue SAFE_DIV 0.20 alone, ILP_DIVISION_WEIGHT 0.6,
  SECONDARY_EDGE_FEATURE_TTA_WEIGHT 1.0, feifanque V1, thtennant fast-v1 (all == 0.947 outputs). t60f IS a real change on hfast.
* LEGITIMACY OF NODE-COUNT PRUNING (re-ruled 09-17 with forum evidence): the hunt's synthesizer flagged it as an exploit
  under our own internal wording, BUT: forum 728300 quotes the Evaluation page ("Scoring above 1.0 is not a bug and the
  evaluation page says as much"); forum 739686, LB #1 Sergio Alvarez (0.970): "Every node/edges removal I've done
  reflected public lb/cv score. About the unbounded score, the hosts are aware... its the expected behavior". hengck23
  (739018): "detect just enough annotated nodes (up to N_est or less)"; "sparse annotation are not random tracks. they are
  difficult tracks (or tracks annotated by ultrack and hand corrected by host)". => pruning REAL detections to optimise
  the published multiplier is within the rules as the host runs them. Fabricated nodes/hubs/negative t remain BANNED.
  Counter-datapoint: Antonoof deleted 44.7% of nodes/44% edges -> public 0.954 -> 0.954 (J loss ate the 1.0009->1.050
  multiplier gain): selection quality is everything.
* hdet95 = **0.946** (09-17 19:00Z). DET axis now closed on BOTH sides (0.94/0.95 low, 0.975/0.98 high, 0.965 = peak):
  DROP hdet94f from the queue; the fifth arm is t60f. 4 slots were left on the 09-17 UTC day.
* MANUAL-UPLOAD SET for the teammate (he uploads by hand; his token was offered and REFUSED - never handle tokens, and
  using his token would be account sharing; told him to expire it): `~/OneDrive/Desktop/biohub_submit_4/`
  = 1_prim300, 2_hsoftfix, 3_tta8z, 4_ret80f (kernel.ipynb + notes.txt each, README.txt on top). hfast is NOT submitted:
  the forum author of the same validator-off + tight55 change reports identical output, so the control is corroborated
  externally and a slot is better spent on an arm. Remaining for later: t60f.
* BUNDLE DONE + reviewed (2 reviewers: ready_to_send): `teammate_bundle.zip` (19 files, notebook sha256 == v_* sources,
  `SHA256SUMS.txt`). Team "The Originals" (TeamId 16610471) = eeshsaxena + **arunendratripathi03** -> sharing with him
  is legal. Merger deadline 2026-09-22 23:59Z; final 09-29 23:59Z; 5 subs/day is PER TEAM; 2 finals; team has 122 subs.
  Runtime WITHOUT the validator is only ~0.48 GPU-h per arm (hfusion's 6442 s was 4452 s validator/PPSWEEP + 344 s
  rewrite) -> GPU is no longer the bottleneck on his account; SUBMISSION SLOTS are. Order: hfast+ret80f, prim300+hsoftfix,
  tta8z+(hdet94f only if hdet95 >= 0.948 else t60f). push_one.py refuses hdet94f without --eesh-approved.
  To gate his runs he must add eeshsaxena as a view collaborator, then
  `kaggle kernels output arunendratripathi03/biohub-v-<tag> -p data/out_<tag>`, `python ops/gate.py <log> <tag>`,
  compare hfast vs `data/out_hfusion/submission.csv` (sha a69c78229c6556d0) BEFORE trusting any arm. See teammate_bundle/EESH_NOTES.md.
  Look-alike datasets to avoid in web UI: tom99763/biohub-tracking-support-pack-50ep-v1, pilkwang/biohub-tracking-support-pack-v1,
  hongdaekim/biohub-350ep-checkpoint-pin-v1.

## STATE 2026-09-12: best LB **0.947** (`hfusion`/`lforge`/`sectta`), rank ~77 of 3415.

## STATE 2026-09-17 09:30Z - ONE ORCHESTRATOR (`ops/postreset_w1.sh`) OWNS THE POST-RESET WAVE
### Intel refresh (09-17 ~02:50Z): the field is moving past us
148 teams now sit at >= 0.948 (61 on 09-11). NEW clusters: 53 teams at exactly 0.948 and 23 at 0.949, mostly
dated 09-15/16. No public kernel scores above 0.947 and no forum post explains it (private sharing, or small
tuning spreading). >= 0.958: 16 teams (Sergio Alvarez 0.970). A 0.947 rank is sliding.
Public kernels worth knowing: thtennant/biohub-frontier947-fast-v1 (= our fast base: VALIDATOR_ENABLE=0 +
tight55 hardcoded, plus rglob-skip + KD-tree relink speedups, 13.5 min on T4x2; its det096 twin sets DET 0.96),
haideptry DivNet division veto (0.946), feifanque division-competition repair (V1 0.947, V2 unscored).
### Corrections the post-reset audit found (all fixed)
* F1: the retention knob has a FIFTH pinned site - cell 6 `_guard_expected_use_primary = ... retention < 0.9`
  ("Frame-retention decision is inconsistent"). v_ret80 and v_ret80f are rebuilt with 5 sites (verified: 0 leftovers).
* F2: TWO copies of the quota-wait script were running (TaskStop kills the wrapper, NOT the bash child), plus a
  stale `watch_kernel.py ppbase` - risk of double submission. All four killed 09-17 ~09:15Z (pids 414, 6486,
  6817, 7236). LESSON: after TaskStop, verify via /proc/*/cmdline; never overwrite a script that is running.
* TRAP: `build_primswap.py` / `v_ftgcprim` would have ERRORED - REPO_DIR/weights is a symlink into read-only
  /kaggle/input, so copying over `_primary_materialized_path` raises OSError 30. prim300 instead points the
  predictor's `--weights` at a writable copy. Do not reuse build_primswap.py.
* hsoft's 0.946 NEVER TESTED sub-voxel refinement: its patch was applied after the test prediction had already
  run (SUBVOXEL_ACTIVE only for validator movies; the test geff has integer coords), and its in-kernel sweep
  picked combo(relaxed9+tight55). So soft-argmax is UNTESTED on the board -> `hsoftfix` inserts it before prediction.
* hfast reference counts: FINAL 25637/20721/6152/70284 (post-tight55); fallback frames 64 on 44b6_0b24845f, 1 on 6bba_05b6850b.
### W1 arms (all on the fast base, all built + dry-run simulated against the real support-pack predictor)
| arm | change | mechanism / board evidence |
|-----|--------|----------------------------|
| ret80f | retention 0.90 -> 0.80 (5 sites) | fewer primary-only fallbacks; ftaugb21's near-total fallback cost -0.010 |
| prim300 | PRIMARY <- public hongdaekim/biohub-300ep-checkpoint-pin-v1 | on the older single-model pipeline the board ranked rep300 0.894 > seed314159 0.892 > rep350 0.890 > 50ep 0.887: our primary was the WORST checkpoint there |
| hsoftfix | sub-voxel soft-argmax before test prediction | untested on the board (see above) |
| tta8z | TTA views -> Z2^3 flips (removes the rot90/transpose views, which were never training augs; training DOES flip Z) | in-distribution TTA on the axis the metric punishes |
| t60f or hdet94f | TIGHT_UM 6.0 (untuned base) / DET 0.94 if hdet95 >= 0.948 | does the in-sample tight55 selection transfer / DET climb |
GATE (`ops/gate.py <log> <tag>`): FINAL node counts within 10% (15% ret80f) of the reference, no fallback explosion,
and the arm's marker present (PRIMARY SWAPPED sha 12b5d32a / TTA_ZFLIP_ACTIVE / guard applied at 0.80).
Pre-registered LB rules: <= 0.947 NULL/CLOSED; 0.948 HINT (needs a confirming neighbour); >= 0.949 SIGNAL
(neighbour + a 2-arm stack). Neighbour/stack triples ready in the session scratchpad `plan0920/`
(ret70f, prim300s70, hsoftT2, hdet955f, hdet96f; stacks s_p3_r80, s_tz_hs, s_p3_tz, s_r80_hs via make_stack.py).
ORCHESTRATOR `ops/postreset_w1.sh` (running since 09-17 ~09:30Z): probes the quota hourly by pushing hfast ->
verifies hfast == hfusion (stops on MISMATCH for manual review) -> runs the 5 arms with <= 2 in flight -> gates
each on its own log -> submits only GATE_PASS. Sentinels in `ops/state/`. After any session restart: confirm no
copy is alive (/proc/*/cmdline), then `bash ops/postreset_w1.sh` resumes from the sentinels.

## STATE 2026-09-17 02:40Z - BLEND AXIS CLOSED, KAGGLE GPU QUOTA EXHAUSTED
### The blend-weight curve on the REAL board has a clean peak at the public value
| SECONDARY_DETECTION_WEIGHT | public LB |
|----------------------------|-----------|
| ~0.00 (ftaugb21, confounded) | 0.937 |
| 0.20 (sdw20) | 0.939 |
| 0.40 (sdw40) | 0.943 |
| **0.80 (public recipe)** | **0.947** |
| 0.90 (sdw90) | 0.944 |
| edge weight 0.15 -> 0.05 (sew05) | **0.947** (tie) |
=> CLOSED at 0.80. The Zebrahub proxy ranked 0.20 BEST (+0.030); the board ranks it second-worst (-0.008).
=> `sew05` ties 0.947 with GENUINELY DIFFERENT output (edge blending changed) - unlike lforge/sectta/vdr25,
   whose validator numbers are identical to hfusion. **sew05 is the best final-#2 diversity candidate so far.**
### KAGGLE WEEKLY GPU QUOTA (30 h) EXHAUSTED at 2026-09-16 16:23Z
`Kernel push error: Maximum weekly GPU quota of 30.00 hours reached.` New kernel COMMITS are impossible until
the weekly reset (believed Saturday 00:00 UTC = 2026-09-20; NOT verified). Submitting an ALREADY-COMMITTED
kernel still works (hdet95 went through at 00:28Z 09-17). GPU hours, not submission slots, are now the binding
constraint: one hfusion commit costs ~1.1 h, so ~27 commits per week. Spend them only on pre-built, mechanism-
backed arms.
### In flight / queued
* `hdet95` (DET 0.965 -> 0.95, env + guard) SUBMITTED 00:28Z 09-17, scoring.
* `ret80` ERRORED on its first run: a FOURTH site pins the value - cell 6 validates every guard record with
  `float(_guard_record["minimum_retention"]) != 0.9 -> RuntimeError("Frame-retention diagnostic contract
  changed")`. REBUILT with all four sites (cell 0 env, cell 4 re-assertion, cell 1 guard text, cell 6 contract).
  An erroring kernel never submits, so no slot was lost.
* `ppbase` (force base post-process) built, never pushed (quota).
* AUTOMATED: a background loop tries to push `ret80` hourly; its first success detects the quota reset, then it
  pushes `ppbase` and auto-submits both. If the session restarts, re-run it:
  `bash scratch_kernels/await_quota_then_run.sh`.
### FAST BASE `v_hfast` - ~3x more experiments per GPU-quota hour (built 09-17, verify on first commit)
Every commit burned ~65 min because the notebook runs an in-kernel validator on 8 train videos plus a 7-arm
post-process sweep that ALWAYS selects `tight55` (= MOTION_RELINK_TIGHT_UM 5.5; confirmed again in hfusion's
ppsweep_selected.json). hfast adds two cell-0 lines after VALIDATOR_N_PER_TYPE:
  `os.environ["BIOHUB_VALIDATOR_ENABLE"] = "0"` and `os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "5.5"`.
Safety checked in code: cell 7 reads VALIDATOR_ENABLE (default "1") and initialises `val_stems = []`
unconditionally; cells 9 and 10 gate every validator/sweep use on `VALIDATOR_ENABLE and val_stems`, so cell 10
takes its "validator unavailable -- keeping the base configuration" branch; cell 11 only prints len(val_stems).
MOTION_RELINK_TIGHT_UM defaults to 6.0 in cell 2 and is NOT in the drift guard. So hfast's BASE output should
equal hfusion's final tight55 output.
VERIFICATION GATE: `scratch_kernels/compare_submissions.py data/out_hfusion/submission.csv
data/out_hfast/submission.csv` (hfusion's real submission.csv is now saved, sha256 a69c78229c6556d0...).
FAST_OK, TIGHTENED 2026-09-18 = identical sha256, or identical CONTENT once the positional `id` column is dropped.
The old rule (every per-dataset node/edge count within 0.2%) is retired as evidence and now prints as
"LEGACY count-only verdict". Proof it was unsound: run the comparison on hfusion (0.947) vs the real hsoftfix
(0.949) file and the legacy rule answers FAST_OK (worst per-dataset count diff 0.1244%) even though 58.4% of the
shared node ids moved and the board scored the two files 0.002 apart. hsoft (0.946) vs hfusion likewise differed
on only 1.6% of shared nodes. compare_submissions.py now also prints how many rows differ and how many nodes kept
their (dataset, node_id, t) identity but moved, per axis.
`build_multi.py` now takes `BUILD_BASE=v_hfast` to build arms on the fast template.
Pre-built on the fast base: `v_ret80f` (retention 0.80, all four sites) and `v_t60f` (MOTION_RELINK_TIGHT_UM 6.0,
i.e. the untuned base arm = the "ppbase" question for free).
AUTOMATION (background, `scratch_kernels/await_quota_then_run.sh`): push hfast hourly until the quota is back ->
wait COMPLETE -> compare -> touch hfast.VERIFIED or hfast.MISMATCH -> run ret80f + t60f (or ret80 + ppbase on
the full-cost base if mismatched) and auto-submit both. Re-run the script after any session restart; it resumes
from the sentinel files. hfast itself is NOT submitted (identical output would waste a slot).
### FOCUS-3D as a straight detector scores 0.839 on the public LB
qiweiyin/focus3d-nuclei-physical-pp-submit: public 0.839, best 0.854, 31 min on T4 x2. So Team #16's 0.957 is
NOT "use FOCUS-3D"; if their FOCUS-3D + HOCT reading is right, the gain lives in the tracker and tuning, which
we cannot reproduce without GPU. Deprioritized.

## STATE 2026-09-16 14:35Z (after a session restart that killed the queue + one watcher)
Blend-weight arms on the LB (the only axis with a real-board slope: ~0.00 -> 0.937, 0.80 -> 0.947):
| kernel | SECONDARY_DETECTION_WEIGHT (or change) | status |
|--------|----------------------------------------|--------|
| sdw20 | 0.20 | submitted 13:07Z, scoring |
| sdw90 | 0.90 | kernel finished while its watcher was dead; SUBMITTED 14:31Z on recovery |
| sdw40 | 0.40 | kernel running; new watcher will submit on completion |
| sew05 | SECONDARY_EDGE_WEIGHT 0.15 -> 0.05 | never pushed (queue died); re-queued 14:32Z |
That uses all 5 of 09-16's slots (ftgc0, sdw20, sdw90, sdw40, sew05).
PRE-BUILT, NOT PUSHED: `v_sdw95` (0.95) and `v_sdw85` (0.85).
PRE-REGISTERED RULE for 09-17's first slot:
  * sdw90 >= 0.948 -> push sdw95 (continue up the slope).
  * sdw90 = 0.947 and sdw40 < 0.947 -> the optimum is near 0.80-0.90; sdw85 only if sdw90 hinted up.
  * sdw20 or sdw40 >= 0.948 -> midpoint between the best LB point and its better neighbour.
  * everything <= 0.947 -> the weight axis is CLOSED at 0.80; spend nothing more on it.
### 09-17 SLOT PLAN (5 slots). Only DETECTION-LEVEL changes have ever moved the board by >= 0.002
(detector swaps -0.005 / -0.010, DET 0.975/0.98 -0.002 each); post-proc knobs sit below display precision.
PRE-BUILT AND VERIFIED, NOT PUSHED (all via `scratch_kernels/build_multi.py`, exact expected-count replacements):
| kernel | change | why it is a live question on the REAL board |
|--------|--------|---------------------------------------------|
| `v_ret80` | DUAL_SEED_MIN_CANDIDATE_RETENTION 0.90 -> 0.80 at ALL THREE sites (cell 0 env, cell 4 re-assertion, cell 1 guard text) | ftaugb21's near-total fallback to primary-only detection cost -0.010, and dense 44b6 movies already fall back on 64-100% of frames. Fewer fallbacks = the blend is used more. |
| `v_hdet95` | DET_THRESHOLD 0.965 -> 0.95 (cell 0 env + cell 1 guard numeric) | on this body 0.975 and 0.98 each scored -0.002; the LOWER side was never tested here |
| `v_ppbase` | PPSWEEP_SELECT_MARGIN 0.001 -> 1.0 (forces `base`) | the kernel picks `tight55` from IN-SAMPLE train videos (+0.0021 there); does that selection transfer? |
| `v_sdw95` / `v_sdw85` | secondary detection weight 0.95 / 0.85 | weight-axis follow-ups, per the rule above |
ALLOCATION: slots 1-4 on the independent axes (weight follow-up per its rule, ret80, hdet95, ppbase) early in the
UTC day so they score together; hold slot 5 for the best same-axis follow-up once the first of them lands.
PRE-STAGED 16:00Z: `scratch_kernels/prestage_then_submit.sh ret80 hdet95 ppbase` pushes the three kernels NOW
(commits cost no submission slot) and submits them right after 00:00Z 09-17, so their scores land hours earlier.
If the session restarts before then: check `kaggle kernels status` for the three tags and re-attach
`watch_kernel.py` AFTER 00:00Z (the sentinels make it idempotent). The weight follow-up (sdw95/sdw85) is NOT
staged: it depends on sdw90's score.
Gotcha found while building: DUAL_SEED_MIN_CANDIDATE_RETENTION is re-set to "0.90" in cell 4 line 84 right
before the retention guard is patched in, so a single-site change would be silently undone at runtime.
RECOVERY LESSON: background watchers do not survive a session restart. After any restart, run
`kaggle kernels status` for every in-flight tag and re-attach `watch_kernel.py` (it submits immediately if the
kernel is already COMPLETE, and is idempotent via the `<tag>.SUBMITTED` sentinel).

## !!!! 2026-09-16 19:15Z: THERE IS NO RELIABLE OFFLINE GATE. THE PUBLIC LB IS THE ONLY TRUSTWORTHY SIGNAL. !!!!
Tested the kernel's OWN in-kernel validator (8 held-out TRAIN movies, `validator_results.csv`) against the LB
for every scored kernel (selected PPSWEEP config, combined = weighted adjEJ + 0.1*pooled divJ, vs hfusion):
| kernel | dLB | d validator | verdict |
|--------|-----|-------------|---------|
| hdet98 / hdet975 | -0.002 / -0.002 | -0.0012 / -0.0008 | sign right |
| ftaugb21 | -0.010 | -0.0011 | sign right, magnitude 10x too small |
| **ftgc0** | **-0.005** | **+0.0058** | **WRONG SIGN** (secondary fine-tuned on those same train movies = memorized) |
| **hfloat** | **-0.010** | **+0.0000** | **BLIND**: the float writer runs AFTER the validator, so it can never see writer changes |
| hsoft / vdr20 | -0.001 / -0.001 | -0.0011 / +0.0000 | below display precision |
Sign agreement on arms with |dLB| >= 0.002: **3/5; Pearson r = 0.03**. No signal. Together with the Zebrahub
proxy (wrong sign twice), BOTH offline loops are refuted. Decision: stop CPU pipeline tuning; use submission slots
to bracket on the LB directly, one variable at a time, and only on an axis that already shows a slope there.
(The research synthesis quoted ftaugb21's validator as -0.0070; recomputed here as -0.0011 on the same file.)
### FINAL-SELECTION CONSEQUENCE: lforge, sectta and vdr25 are NOT diversification
Their validator numbers are IDENTICAL to hfusion to 4 decimals (base 0.9490, tight55 0.9511, Tp/Tt 0.905,
identical stems). They are the same pipeline in effect; picking one of them as final #2 hedges nothing.
vdr20/vdr25's reranker is not even active in the validator path (d validator exactly 0).
A genuinely different final #2 must come from an axis that actually changes the output (e.g. a blend-weight arm).

## !!!! 2026-09-16 12:10Z: THE ZEBRAHUB PROXY IS REFUTED. DO NOT USE IT TO CHOOSE PIPELINE SETTINGS. !!!!
| submission | what it changed | Zebrahub proxy predicted | REAL public LB |
|------------|-----------------|--------------------------|----------------|
| `ftaugb21` | blend collapsed -> primary-only detection + drifted secondary edges | +0.012 | **0.937 (-0.010)** |
| `ftgc0` | secondary replaced by the better-generalizing gamma/contrast fine-tune | +0.016 | **0.942 (-0.005)** |
Both offline predictions had the WRONG SIGN. The proxy ranks detectors by raw detection quality against DENSE
automated Ultrack labels; the competition scores SPARSE hand labels with a node-count term, on a different
microscope, with 100-frame movies instead of 24-frame crops. Raw recall is not what the metric pays for.
WHAT THE PROXY IS STILL GOOD FOR: comparing two checkpoints of the SAME model family on detection quality
(that ranking was consistent with deteval). WHAT IT MUST NOT DECIDE: blend weights, thresholds, post-proc, or
anything about the assembled pipeline. The CPU rig itself (predict_dualseed.py, zebra_pipeline.py) remains
useful infrastructure; the DATA it scores against is the problem.
Offline sweeps stopped 12:15Z and the box CPU released. Results kept in ~/biohub/loeo_harness/out/zebra_ds_*.json.
### `sdw00` (weight exactly 0.00) ERRORS - the kernel forbids it structurally
`RuntimeError: No frame-retention diagnostics were produced` (cell 7). The predict patch only enters the blend
branch `if secondary_detection_weight > 0.0:`, so at exactly 0.00 no guard records exist and the kernel's own
diagnostics check raises. Use **0.01** if you ever want the primary-only-detection arm. GOOD NEWS: a kernel
that ERRORS never submits, so the slot is NOT consumed (the watcher exits 1 without submitting).
That freed slot went to `sdw90` instead.
### CHECKED AND DEAD BEFORE COSTING A SLOT: "give the PRIMARY 8-view TTA too"
The shipped kernel ALREADY does it. Cell 4 patches the support-pack primary TTA block (which really does end in
`det_logits[f] / 4`) into a `_nv`-counted 8-view scheme: 3 flips + rot90 k=1,3 + transpose + anti-transpose.
That is also why the later ensemble patch anchors on `/ _nv` and why `build_dualseed.py` had to rewrite the
anchor for the box copy. Primary and secondary both get 8 views; there is no asymmetry to exploit.
### THE REAL-BOARD GRADIENT POINTS THE OTHER WAY - TEST `sdw90` NEXT
Public LB, secondary DETECTION weight: ~0.00 (ftaugb21) = 0.937 | 0.80 (shipped) = 0.947.
So on the true test set, MORE weight on the secondary is better, the opposite of the Zebrahub proxy.
If sdw20 / sdw00 confirm the ordering (expect ~0.940-0.945 and ~0.937-0.940), the untested direction is UP:
build `sdw90` with `build_envvar.py sdw90 BIOHUB_SECONDARY_DETECTION_WEIGHT 0.80 0.90` (the predict patch
requires the value in [0,1), so 0.90/0.95 are legal, 1.0 is not). One variable, no GPU, first slot tomorrow.
### THE PATTERN WE NOW HAVE TO ACCEPT
EVERY single-variable deviation from the public 0.947 recipe that we have tested on the REAL board scores
<= 0.947: DET 0.975/0.98 -> 0.945, MIN_TRACK_LEN 8 -> 0.947, SECONDARY_EDGE_WEIGHT 0.25 -> 0.944 (946 body),
division reranker -> 0.946/0.947, sub-voxel softargmax -> 0.946, float writer -> 0.937, detector swaps ->
0.937/0.942. The public recipe is a well-tuned local optimum, which is exactly why 123 teams sit on it.
Beating it needs a structurally better COMPONENT, not another knob - and our two attempts at a better detector
both lost on the board despite winning offline.

## (superseded reasoning, kept for the record) 2026-09-16 11:30Z: `ftaugb21` = 0.937
ftaugb21 ran with a secondary whose aligned logits collapsed the blend, so hfusion fell back to PRIMARY-ONLY
detection on nearly every frame, while that same drifted fine-tune still supplied edges at weight 0.15.
The CPU proxy on unseen Zebrahub crops predicted the opposite: ds_pub00 (primary-only detection) scored
+0.012 ABOVE production there. The real LB says -0.010. So one of these is true:
  (a) the Zebrahub proxy does not transfer (dense automated GT rewards raw recall; the daxi crops are a
      different microscope; 24-frame crops vs 100-frame movies), or
  (b) ftaugb21's loss came from its DRIFTED SECONDARY EDGES, not from the detection fallback.
TODAY'S 4 SLOTS ARE SPENT DECOMPOSING EXACTLY THIS (submissions cannot hurt us: only the 2 selected on 09-29
count, so the only cost is kernel GPU quota):
| kernel | single change from the 0.947 recipe | decides |
|--------|--------------------------------------|---------|
| `sdw20` (submitted 11:10Z) | SECONDARY_DETECTION_WEIGHT 0.80 -> 0.20 | does the proxy's headline lever transfer at all |
| `sdw00` (running) | 0.80 -> 0.00, PUBLIC secondary kept for edges | isolates the detection fallback (vs ftaugb21's drifted edges) |
| `sdw40` (queued) | 0.80 -> 0.40 | brackets the offline optimum from above |
| `sew05` (queued) | SECONDARY_EDGE_WEIGHT 0.15 -> 0.05, detection untouched | isolates the secondary's EDGE contribution |
READ THEM TOGETHER: if sdw00 ~ 0.947 then ftaugb21's -0.010 was the drifted EDGES and the detection axis is
alive; if sdw00 ~ 0.937 the fallback itself is the cause and the whole lower-the-secondary axis is dead
regardless of what Zebrahub says. sdw20 vs sdw40 then gives the shape.
Kaggle allows only 2 concurrent GPU sessions: `scratch_kernels/queue_push.sh <tag:message> ...` pushes and
auto-submits the rest as sessions free.
Builder for single-value variants: `scratch_kernels/build_envvar.py <tag> <ENV> <old> <new> [note]`
(asserts the anchor appears exactly once).

## STATE 2026-09-16 03:40Z
IN FLIGHT ON THE LB (Kaggle scoring backlog is ~10 h): `ftgc0` (ref 56267255, submitted 02:27Z) and
`ftaugb21` (56261855, 19:50Z 09-15). Best confirmed = 0.947 (hfusion/lforge/sectta/mtl8/vdr25).
BOX: the user's own Fingerspell training (envs/fs, 2 procs, 9.1 GB of 16) owns the GPU as of 03:33Z.
Our biohub processes: NONE. Rule for now: CPU-only on the box, never touch their job.
### LEVER HUNT 2026-09-16 (47 agents, 5 hunters + adversarial verify): 41 candidates -> 2 survivors, BOTH 0.000 gain
The public information space is EXHAUSTED: no public kernel scores above 0.947, and no forum post since 09-13
from a 0.958+ team says what they changed. Everything else was already closed in this file.
SURVIVOR 1 (slot protection): five knobs in the shipped kernel are DEAD - do not sweep them.
  * BIDIRECTIONAL_FUSION_MODE: the harmonic formula is hardcoded in the patch string; cell 1's guard requires the
    literal "harmonic_probability", so any other value RAISES instead of selecting a different fusion.
  * GAP_CLOSE_MAX_GAP: `effective_gap_max = min(GAP_CLOSE_MAX_GAP, 1)`; run_stats confirms 1 on all movies.
  * GAP2_MAX_STEP_UM: dominated by GAP2_MAX_TOTAL_UM (10.2) for any value >= 3.4.
  * GAP_CLOSE_REUSE_UM: gap_reused_existing = 0 on all 4 movies (only ~5-27 isolated nodes exist to reuse).
  * MOTION_RELINK_MAX_FRAME_NODES = 2600: never fires (max observed per-frame detections 851 over 24 movies).
  PROOF from our own 0.947 log: the PPSWEEP arms `gap2step40` and `reuse28` scored bit-identical to base
  (proxy 0.9490 adj 0.9260 divJ 0.2308 tp/fp/fn 3/1/9) on 8 videos = 2 of 7 sweep candidates are inert (~14 min wasted).
  **DO NOT raise MOTION_RELINK_MAX_FRAME_NODES**: relink is an O(n^2) python loop at ~1.4 us/pair, so n=10000 is
  ~7.7 h for ONE movie against the 12 h cap; expected benefit is ~3e-5 (a cap hit only costs that movie's relink,
  which is worth ~-0.002/58). Also distrust two stale strings our kernel prints: "Reverse-time association weight:
  0.200" (the guarded value is 0.15) and `dual_seed_frame_retention_guard_report.json` (describes the ANCESTOR
  config: secondary 0.475, det 0.96875, gap_close 5.8 - NOT what we run).
SURVIVOR 2 (measurement tool): `predict_unet_transformer.py` chooses its device with
`torch.device("cuda" if torch.cuda.is_available() else "cpu")`, so **`CUDA_VISIBLE_DEVICES=` forces a full CPU
prediction with ZERO code edits** (~7.4 s/frame at 4 threads). That gives a GPU-free path to end-to-end scoring
while the user's job owns the card. Caveats from the verify pass: it is a single-checkpoint proxy (no 0.80-weight
secondary, no 8-view TTA), and loeo_pipeline.py needs its GT_DIR line changed to point at zebra_comp.
**FIDELITY TEST PASSED (04:41Z): CPU PREDICTION == GPU PREDICTION, EXACTLY.**
`CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 PYTHONPATH=src nice -n 19 python scripts/predict_unet_transformer.py
--data-dir <dir> --debug-video <dir>/<stem>.zarr --weights <ckpt> --det-threshold 0.965 --use-ilp
--ilp-division-weight 1.2 --ilp-appearance-weight 0.0 --ilp-disappearance-weight 2 --unet-batch-size 4`
6bba_05b6850b: GPU nodes 6145 edges 5832 vs CPU nodes 6145 edges 5832 (identical). Log prints `device=cpu`.
~13 min per 100-frame movie at 8 threads, ~3 min per 24-frame zebra crop at 6 threads.
Output lands at `predictions/training/unet_transformer/split_0/<stem>.zarr.geff` (note the `.zarr.geff` name;
rename to `<stem>.geff` for the harness). NOTE it runs at PredictConfig defaults (pool_kernel_um 3.0, no
secondary, no 8-view TTA), so it is a single-checkpoint PROXY, valid for A/B between detectors, not for absolute
comparison with production numbers.
=> **THE GPU IS NO LONGER REQUIRED TO EVALUATE A DETECTOR END TO END.** This finally gives an honest
(out-of-sample) full-metric loop: every previous local number was in-sample, since the public detector trained
on all 199 train movies. First use: `~/biohub/zebra_e2e_run.sh` (detached, log `zebra_e2e_run.log`, markers ZEBRA_E2E_DONE then
ZEBRA_DETSWEEP_DONE) scores FOUR configs end to end (detection + linking + ILP + repair, official adjEJ/divJ) on
the 8 unseen-embryo Zebrahub crops via `~/biohub/loeo_harness/zebra_pipeline.py` (a copy of loeo_pipeline.py
whose GT_DIR honours $ZEBRA_GT_DIR): public @0.965, ftgc ep00 @0.965, public @0.955, public @0.98. The last two
answer a question the LB would charge 2 slots and 20 h for: is DET 0.965 (tuned on the memorized public board)
right for UNSEEN embryos? ~3 min per crop per config at 6 threads, nice 19.
GOTCHA that cost one restart: `ls $DIR/*.zarr` lists the CONTENTS of the zarr directories (they are dirs), so
building a movie list that way yields "0"/"zarr.json". Use `for p in $DIR/*.zarr; do basename "${p%.zarr}"; done`.
(Same trap makes `ls $D/*.geff | wc -l` report 39 for 8 graphs; trust the harness's own `n=8`.)

### !!! FIRST HONEST END-TO-END RESULT ON UNSEEN EMBRYOS (2026-09-16 06:05Z): ftgc WINS BIG
8 Zebrahub crops, 4 unseen embryos, full pipeline (detect + link + ILP + repair), official metric:
| detector (sole, DET 0.965) | adjEJ | divJ | Tp/Tt | combined |
|-----------------------------|-------|------|-------|----------|
| public secondary (alltrain 400ep) | 0.44402 | 0.0097 (TP 1 FP 24 FN 78) | 0.683 | 0.44499 |
| **ftgc ep00 (gamma/contrast fine-tune)** | **0.51646** | 0.0261 (TP 3 FP 36 FN 76) | 0.787 | **0.51906** |
**+0.072 adjEJ (+16% relative)**, consistent with the +0.027 count-matched node<=2um from deteval.
Absolutes are low by construction (dense Ultrack GT counts every missed cell as FN; the daxi crops are a harder
domain; the proxy runs ONE checkpoint with no secondary and no 8-view TTA at pool_kernel_um 3.0). Only the
RELATIVE ordering is meaningful, and both models were scored on identical crops, GT and pipeline.
IMPORTANT CONSEQUENCE: this measures ftgc as the SOLE detector, whereas the submitted `ftgc0` only swaps it into
the SECONDARY slot, where hfusion's retention guard can bypass it entirely on dense frames. If ftgc really is a
much better detector, the bigger lever is the PRIMARY slot (or dropping dual-seed), not the secondary.
=> queued on CPU: `~/biohub/zebra_primary_run.sh` scores the production PRIMARY (support-pack 50ep, sha
12f6881e, at `~/biohub/weights_primary50ep/`) and `ftgc @ DET 0.98` on the same crops, to rank all three
detectors and get ftgc's own count/accuracy operating point.
STAGED, NOT PUSHED: `scratch_kernels/build_primswap.py` + `scratch_kernels/v_ftgcprim/` +
`datasets/primswap_ftgcprim/` = hfusion with ftgc ep00 in the **PRIMARY** slot (secondary left public).
Mechanics: the primary is materialized from the support pack and checksum-guarded, so the builder leaves that
guard verifying the ORIGINAL artifact and inserts a swap block right after it that finds our weights by sha
under /kaggle/input, copies them over `_primary_materialized_path`, and PRINTS `PRIMARY SWAPPED ... sha256 ...`
so the run's own log records what drove inference. Validated locally (anchor hit once, guard intact).
### !!! DETECTOR RANKING ON UNSEEN EMBRYOS (07:29Z) - THE 400-EPOCH SECONDARY IS THE WORST MODEL WE HAVE
Same 8 crops, same pipeline, sole detector, official metric:
| detector | adjEJ | divJ | Tp/Tt | combined |
|----------|-------|------|-------|----------|
| **primary, support-pack 50ep (sha 12f6881e)** | **0.53048** | 0.0083 | 0.800 | **0.53130** |
| ftgc ep00 (fine-tuned FROM the secondary) | 0.51646 | 0.0261 | 0.787 | 0.51906 |
| ftgc ep00 @ DET 0.98 | 0.51476 | 0.0263 | 0.784 | 0.51740 |
| public secondary, alltrain 400ep | 0.44402 | 0.0097 | 0.683 | 0.44499 |
| public secondary @ DET 0.955 | 0.44405 | 0.0098 | 0.683 | 0.44503 |
| public secondary @ DET 0.98 | 0.43871 | 0.0090 | 0.672 | 0.43961 |
1. **DET is FLAT on unseen embryos** (0.955 ~ 0.965 > 0.98): the peaks are saturated, the threshold barely moves
   the count. No lever there, and it kills the "retune DET for unseen embryos" idea for 2 slots' worth of savings.
2. **The 50-epoch primary beats the 400-epoch alltrain secondary by +0.086 adjEJ on unseen embryos.** Classic
   overfitting: the long alltrain run memorized the two training embryos. Tp/Tt tells the same story (0.800 vs
   0.683): on unseen data we UNDER-detect, and the better generalizer simply finds more real cells.
3. => **DO NOT push `v_ftgcprim`** (shelved): swapping ftgc into the primary slot would replace the BEST model
   with a worse one. ftgc only beats the model it was fine-tuned from.
4. => NEW SUSPECT, the most suspicious number in the pipeline: hfusion blends detection as
   `0.2*primary + 0.8*secondary`, i.e. **80% of the detection weight sits on the worst-generalizing model**.
   The retention guard only rescues this where the blend loses candidates (dense 44b6 frames).
   This also reframes the two pending submissions: `ftaugb21` is effectively "detection from the primary alone",
   so ftaugb21 > 0.947 would confirm the secondary's detection is net harmful on hidden embryos.
### CPU DUAL-SEED RIG (new, running): tune the blend offline instead of buying answers at 1 slot / 10 h each
`~/biohub/kaggle-cell-tracking-competition/scripts/predict_dualseed.py` = the box's predict script with
hfusion's OWN 8 patch strings applied (extracted from the notebook into `~/biohub/dualseed_patches.json`,
applied by `~/biohub/build_dualseed.py`): secondary model + 8-view secondary TTA + mean/std logit alignment +
0.2/0.8 blend + retention guard + edge blending. Fully env-driven (BIOHUB_SECONDARY_WEIGHTS /
_DETECTION_WEIGHT / _EDGE_WEIGHT / _LINK_MODE / _LOW_MARGIN_MAX / DUAL_SEED_EDGE_THRESHOLD).
TWO FIXES needed to run it off-Kaggle: (a) the box repo is one version behind the support pack - it averages TTA
logits with a literal `4` where the pack uses `_nv`, so `build_dualseed.py` rewrites that in the anchors;
(b) the guard writes `/kaggle/working/retention_guard_*.jsonl`, now `Path(os.environ.get("BIOHUB_GUARD_DIR", ...))`.
### !!! BIGGEST FINDING OF THE PROJECT SO FAR (2026-09-16 10:57Z): SECONDARY_DETECTION_WEIGHT 0.80 IS WRONG
4 unseen-embryo crops, production dual-seed pipeline reproduced on CPU, official metric:
| config | adjEJ | divJ | Tp/Tt | combined | crops better than production |
|--------|-------|------|-------|----------|------------------------------|
| ds_pub80 = **production hfusion** | 0.48720 | 0.0000 | 0.813 | 0.48720 | - |
| ds_pub40 | 0.50508 | 0.0204 | 0.902 | 0.50713 | 4/4 (+0.017/+0.011/+0.000/+0.042) |
| **ds_pub20** | **0.51514** | 0.0208 | 0.953 | **0.51723** | **4/4 (+0.019/+0.011/+0.017/+0.065)** |
| ds_pub00 (primary-only detection) | 0.49885 | 0.0213 | 0.939 | 0.50097 | 3/4 |
| ds_ftgc80 (= the submitted ftgc0) | 0.50306 | 0.0182 | 0.848 | 0.50488 | 3/4 |
MECHANISM: the blend is `0.2*primary + 0.8*secondary`, and the secondary is the 400-epoch alltrain model that
is our WORST model on unseen embryos (adjEJ 0.444 vs the 50-epoch primary's 0.530). The public notebook tuned
0.80 when everyone's harness was IN-SAMPLE, where the memorized secondary looks excellent. Lowering the weight
raises Tp/Tt from 0.813 toward ~0.95 (we under-detect on unseen embryos), which lifts both jaccard and divJ.
Note the optimum is interior: 0.00 is WORSE than 0.20, so the secondary does carry signal, just far less than
0.80 implies. **`BIOHUB_SECONDARY_DETECTION_WEIGHT` is NOT in the cell-1 `_EXPECTED_NUMERIC` drift guard**
(that guard pins only DET_THRESHOLD, ILP_APPEARANCE/DISAPPEARANCE, GAP_CLOSE_UM, MIN_TRACK_LEN,
BIDIRECTIONAL_EDGE_WEIGHT + two text keys), so this is a ONE-LINE change at cell 3.
**SUBMITTED 2026-09-16 ~11:10Z as `eeshsaxena/biohub-v-sdw20`** (single variable changed from the 0.947 recipe;
watcher `sdw20.log`). Refinement running: `dualseed_sweep2.sh` = ftgc-as-secondary @0.20, pub @0.30, pub @0.10.
GATE before pushing it: the primary50ep ranking above must show ftgc > primary50ep on the unseen crops
(expected, since the primary is a 50-epoch model and ftgc descends from the 400-epoch secondary), and ideally
ftgc0's LB score should be in hand. The Zebrahub e2e test already exercised ftgc's EDGE head (it scored
detection + linking + ILP end to end), so the swap is not detection-only speculation.
Caveat to keep in mind when reading it: Zebrahub GT is DENSE automated Ultrack output, so FP edges and divJ do
not mean what they mean against the competition's sparse hand labels; trust the RELATIVE adjEJ/jaccard ordering.
DECISION GATES (pre-registered): if `ftaugb21` >= 0.947 the secondary detection contributes ~nothing on hidden
embryos and the whole secondary-swap axis (including ftgc) is dead; if it drops to <= 0.944 the blend is
load-bearing. If `ftgc0` >= 0.949 book the GPU for ep02/ep03 when free; 0.947 +-0.001 = indistinguishable, spend
nothing more on it; <= 0.945 close the line.

## LB RESULTS 2026-09-15
* `vdr25` (hfusion + learned division reranker, thr 2.5, real DeepCenter veto) = **0.947** (ref 56254336),
  identical to hfusion at display precision. Local +0.00219/+0.00034 did not show on the public LB.
* `vdr20` (thr 2.0, the locally "robust" setting, +0.00135/+0.00087 on both embryos) = **0.946** (ref 56254335).
=> LEARNED DIVISION RERANKER IS CLOSED: neutral (thr 2.5) to -0.001 (thr 2.0) on the honest public LB.
   Another case of small in-sample local gains not transferring. Do not revisit.
* `ftaugb21` (dual-seed detection effectively OFF, see below) still pending.

## 2026-09-15 EVENING: LB MOVED, NEW AXIS = FINE-TUNED SECONDARY TESTED ON THE HONEST LB
LB top: 0.970 (Sergio Alvarez), 0.968, 0.966 (Tang = tangai1), 0.966, 0.965; 13 teams >= 0.958.
Public kernels still top out at 0.947: sjlee101 `biohub-lf-hoctveto-div-b` (HOCT consensus veto) = 0.947,
anhadmahajan06 = 0.940, caassicca v5 = 0.942, tangai1 `b02-dynamic` = **0.714** (broken; its runtime
dataset is PRIVATE anyway). => the 0.96+ gains are private work, nothing to fork.
Forum (read 09-15):
* denpugovkin kernel "plants one out-of-volume ancestor so every track shares a root" = EXPLOIT, rejected.
* Le Quang Canh (34th): fine-tuning detection HEAD on dense labels -0.0033, head+ENCODER -0.038 when the
  edge transformer is frozen and reads that encoder. Constant dzyx offset correction -0.0031.
  Of 381 wrong-link cases, velocity picks the true child 0 times; link model prefers truth 15%.
* hengck23: "best way to reduce nodes is to cluster them and represent them by centroid" (greedy NMS on
  refined coords, radius 1 voxel in 64^3 canonical grid, in his end2end no-ILP kernel).
* Hammad Farooq: PPSWEEP always selects tight55 (MOTION_RELINK_TIGHT_UM 5.5) on train videos.
BOX GPU IS 16 GB (not 32): only one training job at a time.
### ftaug (RUNNING on the box, replaced ft144)
ft144 = same data + same weak augs (brightness +-0.1, flips) at lr 2e-5 = "train longer", expected ~null,
stopped at 923/1500 of epoch 0. ftaug = fine-tune the SECONDARY (box public ckpt sha 9bac2fa0... IS
hfusion's secondary, verified) with cross-embryo appearance augs: gamma 0.7-1.5 (p .8), contrast
0.8-1.25 (p .5), gaussian noise sigma<=0.04 (p .5), + brightness + flips. lr 5e-5, 6 x 1500 iters, bs 8.
(Original secondary recipe, training_config.json: 199 train movies, lr 1e-4 constant AdamW, bs 8,
brightness+flip only, 400 of 500 target epochs, best epoch 381. Primary = support-pack-50ep, sha 12f6881e...)
`scripts/train_unet_transformer_aug.py` + `scripts/augmentations_v2.py`, --method unet_transformer_ftaug,
saves EVERY epoch to `weights/unet_transformer_ftaug/split_0/edge_predictor_epNN.pth`. Log `runs/ft_ftaug.log`.
### How to LB-test a checkpoint: `scratch_kernels/build_secswap.py <tag> <pth> <config.json>`
hfusion picks its secondary by scanning /kaggle/input manifests for ONE hard-coded sha256; the builder
writes a private dataset (weights/unet_transformer/split_0 + ARTIFACT_MANIFEST.json) and patches that
constant. Dry-run verified. The public LB is an honest unseen-embryo test (~58 movies), so detector
changes CAN be validated there; local harness numbers for a fine-tuned detector are in-sample.
Secondary carries detection weight 0.80 in fusion, so detection changes propagate.
HOCT queue (dt=1 fix applied) still waits behind the trainer.
### UNSEEN-EMBRYO DETECTOR CHECK (chain running on the box)
Zebrahub (host-approved external data) = embryos no model has seen, with DENSE automated Ultrack tracks
(not hand GT, different annotation convention: use for RELATIVE public-vs-finetune comparison only).
* `~/biohub/zebra_gen_loop.sh` -> `phase1_zebrahub.py` for ZSNS001_tail, ZSNS003, ZSNS004, ZSNS005
  (level 0, 24 frames, <=5 crops of 64x256x256 each) -> `~/biohub/zebra_crops`, log `zebra_gen.log`.
* `~/biohub/zebra_to_comp.py` converts crops to the competition layout ('0' array + multiscales +
  image_statistics.quantiles) -> `~/biohub/data/zebra_comp` + `movies_zebra.txt`.
* `~/biohub/zeval_chain2.sh` (log `zeval_chain2.log`; replaced zeval_ep00_chain.sh): as soon as
  `edge_predictor_ep00.pth` exists, in-sample sanity public vs ftaug_ep00 on 8 split0-test movies
  (`out/s0_public_vs_ep00.txt`, DET 0.955/0.965/0.975); then, once crops are done, converts them and runs
  public vs EVERY ftaug epoch present on Zebrahub (`out/zebra_public_vs_epNN.txt`).
* Box link to public.czbiohub.org is ~1 MB/s: ~35-55 min per level-0 crop. Loop1 stopped after
  ZSNS001_tail c000-c004 + ZSNS003_c000; `zebra_gen_loop2.sh` adds ONE crop each of ZSNS004 and ZSNS005
  (appends to zebra_gen.log, prints ZEBRA_GEN_DONE for chain2). => 8 crops over 4 unseen embryos.
* Smoke test (public, ZSNS001_tail_c000, 4 frames, DET 0.965): recall@7 0.944, node<=2um 0.551,
  edge<=2um 0.374. Harness works on converted crops (pydantic geff-metadata warning is harmless).
  Always pass --out-json: without it deteval writes out/loc_<label>.json and can overwrite old files.
Decision rule: ftaug epoch goes to the LB only if Zebrahub node recall / <=2um residual is not worse
than public AND T_pred/T_true on split0 has not drifted badly (count calibration feeds adjEJ).
### ftaug EPOCH 0 RESULT (in-sample, 8 split0-test movies, raw detector peaks)
Localization UNCHANGED (node<=2um 0.7157 vs public 0.7142, recall@7 0.9956 vs 0.9959) but the model is
OVER-CONFIDENT: n_pred at DET 0.965 = 224,278 vs 181,357 (+24%); 44b6 Tp/Tt 0.861 -> 1.115, 6bba 1.197 -> 1.271.
Count vs threshold (secondary alone): public 0.965 = 181k | ftaug 0.99 = 205k, 0.995 = 190k, 0.998 = 166k.
=> count-matched threshold ~0.9963 on 44b6, ~0.995 on 6bba = +~2.1 logits. At matched count localization
is identical to public. Fix = shift `detect_head.bias` by -2.1 (`~/biohub/ftaug_calib/ep00_b21/`), verify
count, then LB-test THAT (fusion blends LOGITS 0.2*primary + 0.8*secondary before DET, so a secondary bias
shift passes through as 0.8x). Weight drift overall only 0.17%; the count shift comes from features.
Kaggle CLI bug on Windows: `kaggle datasets create -p datasets/x` mangles the upload temp path
("...uploads\datasets/x_ARTIFACT_MANIFEST.json.json"). Run it from INSIDE the folder with `-p .`.
Dataset `eeshsaxena/biohub-sec-ftaug0` (UNCALIBRATED ep00) exists; its kernel was NOT pushed on purpose.
### ZEBRAHUB UNSEEN-EMBRYO RESULT (2026-09-15 19:00Z): THE AUGMENTED FINE-TUNE FINDS MORE CELLS
8 crops, 4 embryos (ZSNS001_tail x5, ZSNS003, ZSNS004, ZSNS005), dense Ultrack GT (75,083 nodes), deteval.
Official-matcher recall@7 vs n_pred (count-matched comparison is what matters):
| model | DET | n_pred | recall@7 | node<=2um |
|-------|-----|--------|----------|-----------|
| public | 0.955/0.965/0.975/0.99 | 77.5k/76.3k/74.6k/69.0k | 0.559/0.551/0.541/0.505 | 0.298/0.295/0.290/0.275 |
| ftaug ep00 raw | 0.965 | 82.8k (+8.5%) | 0.599 | 0.319 |
| ftaug ep00_b21 (submitted) | 0.955/0.965/0.975 | 73.3k/70.9k/67.2k | 0.554/0.543/0.527 | 0.308/0.304/0.298 |
| ftaug ep01 raw | 0.955/0.965/0.975 | 77.7k/76.8k/75.4k | 0.575/0.571/0.565 | 0.297/0.297/0.295 |
!!! CORRECTION (per-crop check): ZSNS003_c000, ZSNS004_c000, ZSNS005_c000 are BROKEN - GT tracks are
misaligned with the image (EVERY detector: node<=2um ~0.005, median residual 8-13 um, rec@7 0.06-0.33).
The ALL rows above are diluted by them. ONLY the 5 ZSNS001_tail crops are valid = ONE unseen embryo.
Valid-only (5 tail crops, n_gt 41,294), recomputed from the per-movie tables:
| model | n_pred | recall@7 | node<=2um | node<=2um crops up |
|-------|--------|----------|-----------|--------------------|
| public @0.965 | 51,296 | 0.886 | 0.531 | - |
| ep00_b21 @0.965 (submitted) | 50,866 (-0.8%) | 0.897 (+0.011) | **0.549 (+0.018)** | 4/5 (c000 -0.001) |
| ep00_b21 @0.955 | 51,954 (+1.3%) | 0.907 (+0.021) | 0.555 (+0.024) | 5/5 |
| ep01 raw @0.965 | 54,513 (+6.3%) | 0.935 (+0.049) | 0.535 (+0.004) | 2/5 (c003 -0.055, c004 -0.014) |
=> At matched count the calibrated ep00 LOCALIZES better on the unseen embryo; ep01 detects more cells but
places them worse. Localization (<=2um) is what the residual oracle ties to adjEJ, so b21 > ep01.
The -2.1 bias is about count-neutral on the valid embryo (-0.8%); the "-7% on unseen" came from broken crops.
Public recall 0.886 on the valid unseen embryo vs 0.996 in-sample: real but moderate domain gap.
ROOT CAUSE (found 2026-09-16): ZSNS003/004/005 `*_tracks.csv` z,y,x are LEVEL-0 VOXEL INDICES (z max
256/288/261 vs image Z planes 258/294/291; y,x fit the 1910-2750 voxel extents), not microns.
phase1 took them as microns and its coarse auto-calibration picked (1, .5, .5): z 24% short, y/x 12% short.
Correct: um = voxel * (1.24, 0.439, 0.439). ZSNS001_tail tracks ARE microns (hence valid).
FIX without re-download: `~/biohub/fix_zebra_gt.py` rebuilds only the geff for the same vlo/time window
(images were fetched in image space, so they are correct); bad geffs kept as `*.geff.bad_units`.
For any NEW full-embryo crops, phase1 must convert voxel->um with the level-0 scale first.
FIX APPLIED + VERIFIED: replaying phase1's crop selection reproduced the existing node counts exactly
(19,143 / 6,463 / 8,183), vlo = [0,984,125] / [16,845,499] / [27,957,723]; rebuilt GT = 12,468 / 8,245 /
1,892 nodes. Public (4 frames): median residual 12.6->6.05 / 7.7->3.8 / 12.8->3.8 um, rec@7 0.08->0.32 /
0.38->0.75 / 0.15->0.86. Detector-free offset fit (`fit_zebra_offset.py`, max smoothed intensity at GT
nodes) finds <= 1 voxel shift on ALL crops incl. the good tail crop (consistent z -1 vox everywhere), early
and late frames agree => GT is now aligned; the remaining gap is the DETECTOR failing on these 2024 "daxi"
full-embryo acquisitions (harder domain shift than tail). All 8 crops are now valid for relative tests.
Re-run on 8 fixed crops -> `out/zebra8fix_public_vs_{b21,ep01}.txt`.
### 8 FIXED CROPS RESULT (2026-09-16): MIXED - ftaug is NOT clearly better on unseen embryos
DET 0.965, per-domain aggregates recomputed from the per-movie tables:
| domain | model | n_pred | recall@7 | node<=2um |
|--------|-------|--------|----------|-----------|
| tail (ZSNS001_tail x5, DIM images) | public / b21 / ep01 | 51.3k / 50.9k / 54.5k | 0.886 / 0.897 / 0.935 | 0.531 / 0.549 / 0.535 |
| daxi (ZSNS003/004/005, BRIGHT 16-bit) | public / b21 / ep01 | 25.0k / 20.1k (-20%) / 22.3k (-11%) | 0.504 / 0.430 / 0.459 | 0.116 / 0.101 / 0.110 |
On daxi embryos BOTH fine-tunes detect FEWER cells than public and lose recall (per crop: ZSNS003 b21
n_pred -28%, ZSNS004 -18%, ZSNS005 -17%); the -2.1 bias over-corrects there. On the tail embryo b21 wins at
matched count. Which domain resembles the hidden competition embryos decides the sign (intensity
comparison running). DECISION: do NOT spend an LB slot on ep01; the running ftaugb21 LB score is the arbiter.
INTENSITY DOMAINS (raw uint16, `~/biohub/intensity_cmp.py`, nonzero voxels p99/p50 and top-decile CV):
* competition is MIXED: dense/bright movies (44b6_0b24845f p99/p50 2.0 fgCV 0.07, 6bba_05db0fb1 2.4/0.16)
  AND sparse/contrasty ones (6bba_05b6850b 15.7/0.58, 6bba_062c8d37 10.0/0.65, 44b6_0113de3b 7.7/0.46).
* Zebrahub daxi crops ~ the DENSE competition movies (p99/p50 1.9-6.4, fgCV 0.05-0.12, q999 750-1320).
* Zebrahub tail crops are dim (q999 100-190) with 40-81% zero padding, contrast like the SPARSE movies.
=> b21 helps on sparse-like data and under-detects on dense-like data. hfusion's retention guard falls back
   to PRIMARY-only exactly when the blend loses candidates (dense 44b6 movies already fall back 64-100%), so
   the pipeline should route dense frames away from the under-detecting secondary. The LB decides.
### !!! ftaugb21 RUN LOG: THE STANDALONE BIAS CALIBRATION BROKE THE BLEND (submitted anyway, ref 56261855)
Kernel completed in ~65 min, watcher submitted 19:50Z. `compare_kernel_runs.py data/out_hfusion data/out_ftaugb21`:
retention-guard fallback frames exploded: 44b6_0b24845f 64->100, 44b6_12dfb391 28->100, 44b6_267148e4 0->87,
6bba_05db0fb1 0->99, 6bba_07e24132 1->100, 6bba_05b6850b 1->73; blend/primary on some movies 0.04-0.07.
=> with b21 the BLEND (0.2*primary + 0.8*secondary logits) loses almost all candidates, so nearly every frame
ran PRIMARY-ONLY detection. ftaugb21's LB therefore measures "dual-seed detection OFF", not the fine-tune.
In-kernel validator (in-sample): d_combined -0.0011 (base) .. -0.0026 (tight55). Expect <= 0.947.
Frame-level (primary vs blended candidates): 6bba_05db0fb1 793 vs 686 (0.865, just under the 0.90 guard;
hfusion never fell back here); 44b6_12dfb391 ~450 vs 2-23 (blend ~0.5-5%: near-total collapse on this dense
44b6 movie, same direction as the Zebrahub "daxi/dense" under-detection, far beyond the -2.1 bias alone).
LESSON: calibrate a secondary swap on the BLEND candidate count vs the primary (what the guard checks),
never on the secondary's standalone count.
DEEPER (read from the patch code): hfusion ALIGNS the secondary before blending, per frame:
  aligned = (s - mean_s) * clamp(std_p / std_s, 0.5, 2.0) + mean_p ; blend = 0.2*p + 0.8*aligned
=> the blend is INVARIANT to any affine change of the secondary logits (bias AND temperature) unless the
   clamp binds. So detect_head.bias -2.1 was a NO-OP inside the blend; b21 == raw ep00 there. The collapse
   comes from the SHAPE of ftaug's logit distribution (peaks lower in z-score units vs the whole-volume
   std), which no bias/temperature fixes. `biohub-v-ftaug0` (raw) is therefore expected to collapse too.
   Offline replica `~/biohub/blend_guard.py <movies> <n_frames> label=ckpt ...` (primary 4-view TTA,
   secondary 8-view TTA as the kernel, same alignment/threshold/guard) reports retention, fallback frames,
   raw std ratio and top-200 peak z-score per secondary. RUN IT BEFORE ANY FUTURE SECONDARY SWAP.
CONFIRMED by the replica (12 frames each; primary 50ep sha 12f6881e on the box at ~/biohub/weights_primary50ep):
| movie | secondary | retention mean (min) | fallback | raw std p/s | top-200 peak z |
|-------|-----------|----------------------|----------|-------------|----------------|
| 44b6_12dfb391 | public | 0.996 (0.966) | 0/12 | 1.13 | 3.93 |
| 44b6_12dfb391 | ep00 = b21 (IDENTICAL) | 0.291 (0.124) | 12/12 | 0.79 | 2.89 |
| 44b6_12dfb391 | ep01 | 0.306 | 12/12 | 0.78 | 2.92 |
| 6bba_05db0fb1 | public / ep00 / ep01 | 1.022 / 0.887 / 0.947 | 0 / 9 / 0 | 1.22 / 1.06 / 1.10 | 3.27 / 2.48 / 2.70 |
| 6bba_062c8d37 | public / ep00 / ep01 | 0.991 / 0.935 / 0.901 | 0 / 2 / 6 | 1.33 / 0.96 / 0.96 | 5.53 / 4.15 / 4.03 |
The aug fine-tune (noise aug most likely) inflates background logit variance: peaks stand out ~25% less in
std units, so the standardized blend loses candidates. INCOMPATIBLE with hfusion's fusion.
KERNEL-LEVEL CONFIRMATION: `biohub-v-ftaug0` (raw ep00, sha 31ac0f15) completed and is IDENTICAL to ftaugb21
in every compared number (same fallback frames per movie, same run_stats, validator d_combined -0.00110 base /
-0.00255 tight55). The detect_head bias is invisible to hfusion. ftaug0 NOT submitted (outputs in data/out_ftaug0).
DECISION 2026-09-15 ~20:15Z: ftaug line STOPPED (trainer killed after epoch 2, checkpoints ep00-ep02 kept);
do NOT submit `biohub-v-ftaug0`. GPU handed to the queued HOCT dt=1 test.
HOCT queue started 20:05Z (control dt=3 on 44b6_a21120c2, then dt=1 on the 6 division-rich movies in
`~/biohub/movies_hoct_test.txt`), log `~/biohub/hoct_queue.log` (lines: delta_t distribution, HOCT_RESULT json).
### HOCT (host tracker, our watershed masks) = CLEAN NEGATIVE, CLOSED 2026-09-15 ~21:00Z
The "metric drops dt!=1 edges" hypothesis is FALSE: the dt=3 control had only 210 of 21,049 solution edges
with dt>1, and dt=1 was WORSE on the same movie (adjEJ 0.8555 -> 0.8389).
| movie | HOCT dt=1 adjEJ | our harness baseline | div TP/FP/FN | forks |
|-------|-----------------|----------------------|--------------|-------|
| 44b6_a21120c2 | 0.839 | 0.924 | 1/4/1 | 303 |
| 44b6_c50204e0 | CRASHED (TorchScript error in hoct.predict, 36k seeds) | 0.842 | - | - |
| 44b6_d2f34f90 | 0.611 | 0.963 | 0/5/2 | 190 |
| 6bba_48816121 | 0.638 | 0.933 | 1/6/4 | 192 |
| 6bba_09961292 | 0.695 | 0.899 | 0/16/4 | 285 |
| 6bba_afb141ff | 0.907 | 0.916 | 0/4/4 | 78 |
HOCT on our masks is far below our pipeline on every movie and does not find divisions (2 TP / 35 FP).
Do not revisit without real segmentation masks (not seeded watershed from our points).
!!! 2026-09-15 21:12Z: ftgc OOM'd at launch. A NEW job appeared on the GPU 3 min after HOCT freed it:
pid 1346034 `miniconda3/envs/fs/bin/python scripts/train.py --config configs/stgcn.yaml` in
/home/training/Fingerspell-train-code (parent `bash /home/training/train_pose.sh`), 12.7 GB. NOT killed
(started after the "kill all other" instruction, may be the user's own new job; asked the user).
ftgc re-queued as `~/biohub/ftgc_chain2.sh` (log `ftgc_chain2.log`): waits until that pid exits AND GPU
memory < 3 GB, then runs the same fine-tune + per-epoch screening.
22:16Z: Fingerspell job 1346034 exited, ftgc LAUNCHED (pid 1472117, 9.4 GB). A second Fingerspell process
(pid 1472672, envs/fs, 3.7 GB) then appeared; both currently fit in 16 GB. Watch for OOM if it grows.
22:32Z: ftgc confirmed training (136/136 tensors, GPU 13.2/16 GB, no OOM) but SHARED-GPU SLOW: 4.86 s/it
(vs 1.9 alone) -> ~2 h/epoch, ep00 screen ~00:30Z, 4 epochs ~8 h. Screening outputs appear as
`sandbox/deteval/out/blendguard_ftgc_epNN.txt` and `zebra8fix_public_vs_ftgc_epNN.txt`.
### ftgc ep00 SCREEN (2026-09-16 00:27Z): BLEND GATE PASSES - the NOISE AUG was the culprit
blend_guard, 12 frames/movie: retention public -> ftgc 0.996->1.005 (44b6_12dfb391), 1.022->1.019
(6bba_05db0fb1), 0.991->0.991 (6bba_062c8d37); fallback frames 0/12 everywhere (ftaug was 12/12 on the
first movie); peak z 3.93->3.77, 3.27->3.30, 5.53->5.12 (within ~4-7% of public). So gamma+contrast is
compatible with hfusion's standardized blend; the noise aug was what flattened the peaks.
Zebrahub @0.965 per crop, node<=2um: tail c000-c004 0.544->0.596, 0.495->0.547, 0.626->0.673,
0.553->0.581, 0.441->0.502 (5/5 UP) but n_pred +3 to +9%; daxi ZSNS003 0.060->0.046 (n_pred -21%),
ZSNS004 0.187->0.190 (-3%), ZSNS005 0.178->0.174 (-9%). COUNT-MATCHED SWEEP (0.90..0.99) = **ftgc ep00 WINS on unseen embryos** (`out/zebra_sweep_ftgc_ep00.txt`):
| n_pred | public node<=2um | ftgc node<=2um | delta |
|--------|------------------|----------------|-------|
| ~81.0k | 0.3966 (thr 0.90) | 0.4188 (0.90) | +0.022 |
| ~77.5k | 0.3877 (0.955) | 0.4145 (0.965) | +0.027 |
| ~73.3k | 0.3740 (0.98) | ~0.409 (interp) | +0.035 |
ftgc's whole count/accuracy curve is above public's. Official matcher at matched count (77.4k vs 77.5k):
recall@7 0.7700 vs 0.7591, **edge<=2um 0.2894 vs 0.2567 (+0.033)**, matched median 1.89 vs 1.97 um.
In-sample split0 count-matched (ftgc@0.98 181,218 vs public@0.965 181,357): node<=2um 0.7194 vs 0.7142,
edge<=2um 0.5852 vs 0.5807, 44b6 node<=2um 0.6988 vs 0.6842 (+0.015), 6bba neutral. (Both memorized.)
=> ftgc ep00 is the first detector change that passes the blend gate AND wins count-matched on unseen data.
PER-CROP count-matched (node<=2um, public vs ftgc at ~equal n_pred): tail c000 0.557->0.597, c001 0.509->0.548,
c002 0.654->0.674, c003 0.558->0.582, c004 0.454->0.500 (5/5 WIN, +0.04..+0.05); ZSNS004 0.190->0.194 (+0.004);
ZSNS005 ~0.180->0.180 (tie, rec@7 -0.03); ZSNS003 0.060->0.055 (-0.005, the hardest crop: public rec@7 only
0.33, median residual 5.6um). No count collapse anywhere (unlike ftaug's -20% on daxi).
**SUBMITTED 2026-09-16 02:27Z (4 slots left that UTC day): `eeshsaxena/biohub-v-ftgc0`** (dataset `biohub-sec-ftgc0`, ckpt sha
7ee561f4..., watcher `ftgc0.log` / sentinel `ftgc0.SUBMITTED`). Read against hfusion 0.947.
ftgc ep01 finished 02:28Z (val acc*recall 0.9667 vs ep00 0.9630, det loss 0.0025) and is being screened.
!!! 2026-09-16 02:31Z: USER ASKED FOR THE GPU BACK (Fingerspell job). Killed the ftgc trainer 5% into ep02
and stopped `ftgc_chain2.sh`, so ep02/ep03 were NEVER trained. GPU 14.3 GB -> 4.6 GB used of 16.
Kept: `weights/unet_transformer_ftgc/split_0/edge_predictor_ep00.pth` (SUBMITTED as ftgc0) and `_ep01.pth`.
To resume the remaining 2 epochs when the box is free: rerun `~/biohub/ftgc_chain2.sh` (~95 min/epoch alone;
it had degraded to 7.4 s/it while sharing the card).
### ftgc ep01 VERDICT (02:50Z): NO GAIN over ep00 -> NOT submitted, ep00 stays the only candidate
Count-matched zebra (node<=2um): 77.4k ep00 0.4145 vs 77.5k ep01 0.4144; 75.3k 0.4122 vs 75.8k 0.4120;
72.3k 0.4074 vs 0.4063. Official matcher at matched count: edge<=2um 0.2894 (ep00) vs 0.2881 (ep01),
recall@7 0.7700 both. Blend gate WORSE: min retention 0.914 / 1.005 / **0.900** (ep01) vs 0.977 / 1.010 /
0.944 (ep00) - 0.900 sits exactly on hfusion's 0.90 fallback threshold; peak z 3.58/3.43/5.03 vs 3.77/3.30/5.12.
=> one epoch of gamma/contrast aug captures the gain; more epochs drift the logit shape without improving
localization. Do not spend GPU on ftgc ep02/ep03 unless ftgc0's LB score is clearly positive.
GPU fully free at 02:50Z (6 MiB of 16 GB; the Fingerspell job is also gone). Submit ep01 only if it beats ep00 count-matched on the same zebra sweep
(`out/zebra_sweep_ftgc_ep01.txt` vs `..._ep00.txt`).
NOTE: SSH to the box was down ~01:15-02:29Z (college link), which killed one watcher; jobs on the box
(setsid) survived. Always relaunch watchers after an outage rather than assuming they are alive.
QUEUED behind HOCT: `~/biohub/ftgc_chain.sh` (log `ftgc_chain.log`) = gamma/contrast-only fine-tune
(`scripts/train_unet_transformer_gc.py`, --method unet_transformer_ftgc, 4 epochs, lr 5e-5, per-epoch ckpts,
log `runs/ft_ftgc.log`). Each epoch is auto-screened: `out/blendguard_ftgc_epNN.txt` (retention / peak z vs
public on 3 movies) + `out/zebra8fix_public_vs_ftgc_epNN.txt` (8 unseen-embryo crops). LB only if retention
>= public-like (no fallback explosion) AND daxi crops do not lose recall.
If detector fine-tuning is ever revisited: drop the noise aug, and gate every checkpoint on blend_guard
(peak z within ~5% of public, retention >= public) BEFORE any Kaggle run.
Follow-up pushed 2026-09-15 ~20:00Z: `biohub-v-ftaug0` (RAW ep00, no bias) WITHOUT auto-submit: read its guard
fallback rates in the log first; submit only if the blend is used at least as often as in hfusion.
When ftaugb21 completes: download its log (`kaggle kernels output ... --file-pattern '\.log$|run_stats|validator_results'`)
and compare BIOHUB_RETENTION_GUARD fallback rates + validator_results.csv against `data/out_hfusion/`.
SCRIPTING PITFALL (cost one eval): a remote `pgrep -f "label-b ftaug_ep01_s[0]"` guard inside an ssh
command whose OWN text contains "ftaug_ep01_s0" matches itself, so "already running" was true and the eval
never launched. Guard on a pid/lock file, or on a string that is not literally in the launching command.
The ep01 in-sample count curve was therefore NOT measured; only run it if ep01 survives the 8-crop check.
### hfusion RETENTION GUARD: on 44b6-like movies the SECONDARY detection is mostly NOT USED
Per frame, hfusion blends det logits (0.2 primary + 0.8 secondary) and falls back to PRIMARY-ONLY if the
blend keeps < 0.90 of the primary's candidates. hfusion v2 log (`data/out_hfusion/`): fallback on
44b6_0b24845f 64 frames (blend/primary 0.78), 44b6_2a2eff9f 100/100 (0.74), 44b6_12dfb391 28 (0.88);
6bba clips only 1-3 frames. So a secondary swap mostly changes 6bba-like (sparser) frames. The
UNCALIBRATED ftaug (+24% candidates) would flip many 44b6 frames from primary-only to blended, which is a
second, confounded behaviour change; the bias-calibrated b21 keeps the fallback pattern as it was.
Dataset `eeshsaxena/biohub-sec-ftaugb21` (ep00, detect_head.bias -2.1, sha 106beb02...) uploaded + ready.
Calibration verified (8 split0 movies, DET 0.965): n_pred 187,626 vs public 181,357 (+3.5%; 44b6 +5.0%,
6bba -1.2%), localization identical. **Kernel `eeshsaxena/biohub-v-ftaugb21` pushed 2026-09-15 ~18:45Z,
watcher `watch_kernel.py` auto-submits (log `ftaugb21.log`, sentinel `ftaugb21.SUBMITTED`).**
Read it against hfusion 0.947. Expect a small effect (secondary is unused on most 44b6-like frames).
**KAGGLE CLI PUSH BUG (laptop):** `kaggle kernels push` for a NEW kernel crashes in `slugify(title)` with
`NameError: unicode`, because a Python-2 package `slugify-0.0.1` (site-packages/slugify.py, installed
2026-08-10) shadows python-slugify 8.0.4. Environment left untouched; use
`python scratch_kernels/kaggle_push_safe.py <kernel folder>` (imports kaggle, patches the module's slugify,
runs the CLI). ftaugb21 v1 was pushed this way.
Helper for the next checkpoint: `SKIP_PUSH=1 bash scratch_kernels/ship_secswap.sh <tag> <remote split_0 dir> x`
(scp -> build_secswap -> upload from inside folder -> wait ready; drop SKIP_PUSH to also push the kernel;
checkpoints land in `scratch_kernels/_ckpt/<tag>/`). Then `python watch_kernel.py eeshsaxena/biohub-v-<tag> <tag> "<msg>"`.
### CLOSED 09-15: node clustering / duplicate merging (hengck23 trick) is a no-op for us
out_946 submission (122,791 nodes, 4 clips): same-frame NN distance p1 4.67 um, p50 8.17 um; only 38 nodes
(0.03%) have a neighbour < 2 um, 86 (0.07%) < 3 um. The detector's peak NMS already removes duplicates.

## 2026-09-15: FORUM SWEEP OVERTURNED TWO PREMISES + ILP DIVISION HYPOTHESIS = CLEAN NEGATIVE

### !!! CORRECTION: THE PUBLIC LB IS *NOT* A MEMORIZATION READOUT !!!
Host (Thibgolds, /discussion/723921, /discussion/716062): the 4 VISIBLE test clips are PLACEHOLDERS
(copies of train). The real LB uses "a much bigger test set, deliberately kept private", roughly the
size of train, with NO embryo_id overlap. Public = 29% of that (~58 movies), all UNSEEN embryos.
=> My "public LB = memorized twins" theory was WRONG, and so was my "+-0.010 noise floor" - it was
   derived from the 4 placeholder clips. Real public sample is ~58 unseen-embryo movies.
=> Public and private are BOTH unseen-embryo samples, so they should correlate well.
BUT the LB is still noisy for another reason: few distinct test embryos, movie-to-movie spread ~+-0.14
(Mendrika, rank 395). Mark (rank 14) and Yubo saw local CV +0.01..+0.03 map to +0.001 LB.

### !!! CAUTION: OUR LOCAL HARNESS IS IN-SAMPLE FOR THE DETECTOR !!!
The public weights were trained on ALL 199 train movies (Mark_RowSet, rank 1469, /discussion/730160:
"split_manifest.json lists 199 under train"). Every local harness number uses memorized detections.
Mark ablated a post-proc stage for +0.0184 locally and it flipped to -0.003 on LB, because corrective
stages look useless on memorized videos. Our reranker's +0.00135/+0.00087 is subject to this too.

### VETO TEST v2 WORKED (the v1 bug is fixed)
v1 was VOID: `apply_env` deletes every BIOHUB_* var and reloads repair_prod, so `BIOHUB_DC_HEATMAPS`
was always empty. Renamed to `DCV_HEATMAPS_DIR` (NOT BIOHUB_*). Guard passed: vv_base 0.91759 != stub
0.91574. With the REAL DeepCenter veto active:
| config | 44b6 | 6bba |
|--------|------|------|
| base | 0.91759 | 0.92112 |
| reranker thr2.0 | **+0.00135** | **+0.00087** |
| reranker thr2.5 | +0.00219 | +0.00034 |
| DC safe-div thr 0.35 | -0.00126 | - |
thr 2.0 is the ROBUST one (clearly positive on both). SUBMITTED as vdr20 + vdr25 (2026-09-15).

### ILP DIVISION HYPOTHESIS = CLEAN NEGATIVE (do not revisit)
Forum (Le Quang Canh, rank 31): relink discards the solver's forks. CONFIRMED in code - L2958-2961
`edges = motion_edges`, and motion_relink_edges uses linear_sum_assignment (1:1, cannot fork).
BUT the raw ILP produces ZERO forks on all 199 movies anyway. Cause: ILP_APPEARANCE_WEIGHT=0.0 makes a
new track FREE, so with division cost 1.2 a fork (-0.9-0.9+1.2=-0.6) always loses to starting the
second daughter as a new track (-0.9). (Softmax is dim=0 over SOURCES, so it does NOT split mass.)
Tested directly: one network pass, ILP solved at 5 division weights, 10+10 movies, official evaluator:
| div weight | forks 44b6/6bba | TP | FP | divJ 6bba |
|-----------|-----------------|----|----|-----------|
| 1.2 (ships) | 0/0 | 0/0 | 0/0 | 0 |
| 0.5 | 1806/978 | 0/3 | 30/44 | 0.051 |
| 0.0 | 2282/1185 | 0/3 | 30/52 | 0.045 |
| geometric safe-div (ships) | | | | **0.1075** |
Lowering the cost makes the solver fork on NOISE: thousands of forks, zero TP on 44b6. This edge model
carries no usable division signal. The geometric heuristic is >2x better. KEEP IT.
NOTE: others' divJ 0.22-0.28 are LB numbers; our local 0.11 is in-sample and NOT directly comparable.

### HOST RULINGS (no changes since 09-11)
External data allowed: Zebrahub + all its resources (/discussion/734330), CTC datasets with citation.
Self-trained models uploaded as datasets allowed if reproducible (/discussion/724502).
HOCT (host's tracker) inference code + pretrained model public: github.com/royerlab/hoct.

### GPU SHARING NOTE
A `uvicorn src.api:app` from ~/Documents/Img-3D (NOT ours) holds 13.4 GB of the V100 at 0% util,
up 19h+. Do NOT kill it. Inference needs only ~1.1 GB and fits alongside; TRAINING (~13 GB) will not.
## !!! THE DIVISION BREAK-EVEN RULE (derived + measured 2026-09-14) - SCREEN EVERY FILTER WITH IT !!!
For divJ = T/(T+F+N): removing a false positive shrinks the denominator by 1; losing a true
positive moves it into FN, so the numerator drops while the denominator does not.
  delta divJ ~ (k*T/D - m) / D   for k FPs removed and m TPs lost, D = T+F+N
  => BREAK-EVEN: **k/m > D/T** (the inverse of divJ).
Measured: D/T = **9.7** on 44b6 and **11.9** on 6bba. So any division filter must remove
**more than ~10-12 false positives per true positive it costs**, or it LOSES.
This explains everything in the division family:
| filter | TP lost | FP removed | ratio | vs break-even | result |
|--------|---------|------------|-------|---------------|--------|
| tau 0.45 on 44b6 | 1 (6->5) | 18 (32->14) | **18:1** | > 9.7 | **+0.00192** |
| tau 0.45 on 6bba | 3 (21->18) | 22 (125->103) | **7.3:1** | < 11.9 | **-0.00034** |
| caps halved/quartered | removes FP and TP at ~the base rate (~6:1) | | | << break-even | monotonically worse |

### tau 0.45 FAILS THE BOTH-EMBRYOS GATE
44b6 +0.00192, 6bba -0.00034, movie-weighted over 199 = **+0.0005**. Not worth a submission.
This is the THIRD lever to look convincing on 44b6 and die on 6bba (after mtl8 and the
node-count family). 44b6 alone is not evidence; always run both prefixes.

## GPU: THE HARNESS NOW RUNS THE *REAL* DEEPCENTER VETO (was stubbed to always-accept)
Production's veto rejects ~64% of proposals; the harness accepted all of them, so every division
number it ever produced (today's AND all div20 work) was an UPPER BOUND.
* `dc_precompute.py` computes center-prior heatmaps for all 199 movies on the GPU (~15 s/movie,
  ~10 GB) into `~/biohub/dc_heatmaps`, using ONLY the checkpoint's own training script
  (`deepcenter/source_scripts/train_full_frame_center_detector.py`) - no kernel code needed.
  Verified it is production's checkpoint: 0 missing of 50 tensors, and epoch=2
  best_score=-0.04500306242456039 matches the production kernel log exactly.
* `enable_dc_veto.py` replaces the always-accept stub in `loeo_harness/repair_prod.py` with the
  real windowed-max veto in POOLED coords (backup `repair_prod.py.preveto`). It stays OFF unless
  `BIOHUB_DC_HEATMAPS` is set, so all stub-era measurements remain reproducible.
* Re-run the division sweep with `BIOHUB_DC_HEATMAPS=~/biohub/dc_heatmaps` to get the first
  production-faithful division numbers, and to make DEEPCENTER_* knobs testable at all
  (`d_dc035` returning the baseline to 6 s.f. was the tell that they were inert by construction).
## DIVISION SWEEP, 71 movies, full official metric (2026-09-13) - FIRST POSITIVE LEVER IN DAYS
| config | mechanism | divJ | TP/FP/FN | Tp/Tt | delta combined |
|--------|-----------|------|----------|-------|----------------|
| d_base | ships | 0.1034 | 6/32/20 | 0.773 | - |
| **d_tau045** | SISTER_SYMMETRY_TAU 0.6->0.45, SELECTIVE | **0.1250** | **5/14/21** | 0.773 | **+0.00192** |
| d_tau030 | tau 0.30 (over-tight) | | | | +0.00144 |
| d_maxum7 | SAFE_DIV_MAX_UM 9->7, SELECTIVE | | | | +0.00073 |
| d_dc035 | DEEPCENTER threshold | - | - | - | +0.00000 (UNTESTABLE, see below) |
| d_cap_h / d_cap_q | caps halved / quartered, INDISCRIMINATE | | | | -0.00111 / -0.00189 |
| d_off | divisions off entirely | 0 | 0/0/26 | | **-0.01064** (the whole mechanism is worth this) |
| d_mtl8_tau045 | mtl8 + tau045 | | | | **+0.00342** |
| d_mtl8_caph | mtl8 + cap_h | | | | +0.00038 |
**SELECTIVE beats INDISCRIMINATE.** tau 0.45 cuts FP 32->14 for the cost of ONE TP; cutting the
budget instead raises FN faster than it cuts FP and is monotonically worse. Same lesson as the
node-count family: WHICH you remove matters, not HOW MANY.
**PERFECT ADDITIVITY**: mtl8 (+0.00148) + tau045 (+0.00192) = +0.00340, measured +0.00342.
mtl8 + cap_h predicted +0.00037, measured +0.00038. The levers are independent, so tau's gain
does NOT depend on the node-count operating point - the axis that made mtl8 embryo-specific.
That is a structural argument for tau transferring, now backed by measured independence.
**DO NOT SHIP THE COMBO**: mtl8 is embryo-NEGATIVE (-0.0011 on 6bba). tau alone is the candidate.
NOTE the old div20 harness measured tau 0.45 at **-0.0063**, the OPPOSITE sign. With 29 division
events and a +-0.0058 noise floor it carried no information. Ignore every div20 division verdict.

## !!! THE LOCAL HARNESS STUBS DEEPCENTER - DIVISION NUMBERS ABOVE ARE UPPER BOUNDS !!!
`deepcenter_accept_repair_point` is stubbed to `return True` and the harness passes
`deepcenter_bundle=None`; `refine_synthetic_midpoint` is DISABLED too. In PRODUCTION the veto
rejects ~64% of proposals that reach it (real kernel log: `deepcenter_rejected = 110,
post_veto_candidates = 62, added = 49`). So the harness sees INFLATED division FPs, and part of
tau's gain may be redundant with a filter production already applies.
* `d_dc035` reading exactly 0.91574 (= baseline to 6 s.f.) is the TELL: DEEPCENTER_* knobs are
  inert here BY CONSTRUCTION, not null.
* A full port was attempted (weights downloaded to `~/biohub/deepcenter`, 8 functions extracted
  to `sweep0911/dc_extract.py`) but `_DCDeepCenterUNet3D` lives outside baseline_code.py and the
  port kept growing. ABANDONED in favour of the cheaper faithful test below.
* **PRODUCTION-FAITHFUL TEST (running): kernels `v_vtau060` / `v_vtau045`** = hfusion with
  tau 0.60 vs 0.45 and VALIDATOR_N_PER_TYPE 4->8 (16 held-out movies). The kernel's own validator
  runs WITH DeepCenter, PPSWEEP and dual-seed active and writes `validator_results.csv`.
  **Read the validator output from the kernel log - NO submission needed.** This is the number
  that decides whether tau ships.
GENERAL RULE: the local harness is right for RELATIVE comparisons that do not involve DeepCenter;
never read its absolute division rates as production truth.
## !!! READ BEFORE TRUSTING ANY LB DELTA - I VIOLATED THIS ALL WEEK (restated 2026-09-12) !!!
GT is ~0.74% sparse. The public score rests on ~4 movies / ~836 GT edges =>
**1-sigma on J is about +-0.010.** The paired LOCAL harness (199 movies, same movies + same
cached detections, only the config differs, so variance cancels) has a noise floor near
**+-0.0007**, i.e. roughly **7x the power**. This inverts the instinct "trust the LB, not CV".
Every closure I recorded this week from a small LB delta is NOT statistically supported:
| result | delta vs 0.947 | sigma | what I wrongly claimed |
|--------|----------------|-------|------------------------|
| hdet98 / hdet975 | -0.002 | 0.2 | "DET closed, consistent trend" (two 0.2s readings are still not evidence) |
| hsoft | -0.001 | 0.1 | "public-neutral" (unmeasurable either way) |
| divrank2 | -0.002 | 0.2 | "division reranker is LB-negative" (closed on nothing) |
| hfloat | -0.010 | ~1.0 | "refuted" - the ONLY one near 1 sigma, and it leans on the
|        |        |       |   truncation mechanism being independently plausible |
CONSEQUENCES:
* DET as a node-count lever is NOT actually closed by the LB. The *mechanism* argument
  (holes inside tracks break edges, and coverage is per-node while J is per-edge) still stands,
  but it needs a PAIRED LOCAL test on both embryos to be called closed. NOT YET DONE - do it.
* The divrank re-test now queued is not optional; the original closure had no support.
* Our own 0.945 -> 0.947 gain is itself only ~0.2 sigma on public. It is reproducible (232 teams
  sit on that exact number, so it is deterministic per config), but reproducible is not the same
  as better on the private 71%.
RULE: judge every config on the paired 199-movie harness across BOTH embryo prefixes. Use the LB
only to confirm a kernel ran and produced a sane score. Never close a lever on a sub-0.01 LB delta.
## !!! NODE-COUNT TUNING IS CLOSED AS A PRIVATE-SET STRATEGY (measured 2026-09-12) !!!
The cross-embryo check killed mtl8, the one lever that had looked real:
| MIN_TRACK_LEN 6->8 | 44b6 (71 mv) | 6bba (128 mv) | movie-weighted (199) |
|--------------------|--------------|----------------|----------------------|
| delta combined | **+0.00148** | **-0.00110** | **-0.0002 (nil)** |
The embryos move in OPPOSITE directions, and the mechanism is the per-embryo operating point:
44b6 sits at Tp/Tt 0.773 (a credit is available, so removing nodes collects it), 6bba sits at
0.970 (removing nodes pushes below 1 and J loss dominates). The convincing 44b6
"peak with turnover" was fitting ONE embryo's ratio.
GENERAL CONSEQUENCE: **any GLOBAL node-count lever is embryo-specific by construction.** Its
optimum depends on where the embryo already sits, the two known embryos are 0.20 apart, and the
private embryos are unseen. This retroactively explains hdet98 (-0.002) and every historical
DET plateau. Do not tune node count globally again. A per-movie ADAPTIVE scheme is the only
version that could work, and it needs T_true at test time, which we do not have (the metric
reads `estimated_number_of_nodes` from the GT geff; submissions never see it).
NOTE `mtl8` was already submitted before this result; it is NOT a finals candidate.
LESSON: validate on BOTH embryo prefixes BEFORE promoting any lever. A single-embryo peak with
a clean turnover curve and p=1.4e-08 still turned out to be embryo-specific.
## !!! THE CENTRAL MECHANISM, MEASURED TODAY: NODE REMOVAL MUST PRESERVE *EDGE* INTEGRITY !!!
adjEJ = J * (1 - 0.1*(T_pred/T_true - 1)). Removing nodes raises the multiplier, so it looks
like free score. It is not, and the reason is now measured:
| removal criterion | what it does to tracks | result |
|-------------------|------------------------|--------|
| DET_THRESHOLD 0.965->0.98 | punches HOLES INSIDE tracks | **LB 0.945 (-0.002)** |
| OUTPUT_MIN_TRACK_LEN 6->8 | removes WHOLE short tracks | local peak, **+0.00148** |
**I predicted +0.010 for DET 0.98 and was WRONG.** The error: deteval's flat metric is
node<=2um COVERAGE (does each GT cell have SOME detection within 2um), but J is measured on
EDGES. A cell can stay covered at t while its partner at t+1 is removed, breaking the edge.
Flat coverage NEVER implied intact edges. This also vindicates the old grafael-body evidence
(DET 0.970 -> 0.934) that I had been calling puzzling counter-evidence: it was simply right.
=> DET as a node-count lever is CLOSED. Only EDGE-COHERENT removal can work.

### Node-count / J frontier, backed out of the measurements (71 movies, 44b6)
| config | Tp/Tt | multiplier | implied J | adjEJ |
|--------|-------|-----------|-----------|-------|
| mtl6 (ships) | 0.773 | 1.0227 | 0.8853 | 0.90539 |
| **mtl8** | 0.751 | 1.0249 | 0.8848 | **0.90687** |
| mtl10 | 0.729 | 1.0271 | 0.8801 | 0.90391 |
| mtl12 | 0.705 | 1.0295 | 0.8747 | 0.90048 |
J falls monotonically, the multiplier rises, the product peaks at 8. So MIN_TRACK_LEN does
remove REAL nodes past 8 - it is only a mediocre proxy for "spurious".

## NEW MECHANISM BUILT TODAY (untested): COMPONENT-LEVEL CONFIDENCE FILTER
If removal must be edge-coherent, then whole-component removal is the right shape, and LENGTH
is the crudest possible signal for it. Verified absent from the pipeline: `mean_edge_prob`
occurs ONCE, only inside the short-track RESCUE path; nothing drops whole tracks by confidence.
Added `filter_low_confidence_components()` to `~/biohub/loeo_harness/repair_prod.py`
(backup: `repair_prod.py.preconf`), called right after `filter_short_track_components`:
drops whole weakly-connected components whose MEAN EDGE PROBABILITY is below
`BIOHUB_OUTPUT_TRACK_MIN_MEAN_PROB` (0 = off, so the baseline is bit-identical), with
`BIOHUB_OUTPUT_TRACK_PROB_MAX_NODES` (0 = no cap) restricting it to short components so long
established tracks are never considered. Nodes and edges leave together by construction.
Sweep queued (`run_conf_sweep.sh` -> `conf_sweep.log`): thresholds 0.30/0.50/0.60/0.70, then
two capped variants, then a 6bba cross-embryo check. **The FIRST config `c_noop` must reproduce
comb 0.91574 exactly; if it does not, the patch is not a no-op and every later row is void.**

## PER-EMBRYO NODE-COUNT DIVERGENCE (matters for the private set)
| embryo | movies | Tp/Tt | multiplier | divJ |
|--------|--------|-------|-----------|------|
| 44b6 | 71 | **0.773** | 1.023 | 0.1034 (TP 6 / FP 32 / FN 20) |
| 6bba | 128 | **0.970** | 1.003 | 0.0840 (TP 21 / FP 125 / FN 104) |
The embryos sit at very different operating points, so a GLOBAL node-count setting is NOT
embryo-invariant and the private embryos are unseen. Any node-count lever must be validated on
BOTH prefixes before it goes into a final (the deteval README demands exactly this).

## LOCAL FULL-METRIC TESTBED (use this instead of submissions)
`~/biohub/loeo_harness/loeo_pipeline.py <pred_dir> <movies.txt> <label> [KEY=VAL ...]`
runs prologue + epilogue + the official scorer over predicted geffs and accepts env overrides.
199 predicted graphs live in `~/biohub/pred_graphs`; lists `movies_44b6_all.txt` (71),
`movies_6bba_all.txt` (128). Costs NO submissions. Always bootstrap a delta before shipping.

## TODAY'S LB RESULTS
| kernel | change | LB |
|--------|--------|-----|
| hfusion / lforge / sectta | 0.947 recipe, and two inert knobs | **0.947** |
| hsoft | sub-voxel softarg (verified firing) | 0.946 |
| hfloat | float coordinate writer | 0.937 |
| hdet98 | DET 0.98 | 0.945 |
| hdet975 / mtl8 | DET 0.975 / MIN_TRACK_LEN 8 | PENDING |

## FINALS (2026-09-29): A = `hfusion` (anchor). B = best validated-on-BOTH-embryos variant,
falling back to `hsoft` (public-neutral, proxy-positive) if nothing better validates.

## CLOSED TODAY, WITH NUMBERS
### 1. FLOAT COORDINATE WRITER = DEAD (-0.010)
The sweep's TOP-ranked lever (+0.0051 on the unseen-embryo proxy, CI excluded 0) lost 0.010 on
the LB. Cause is the risk the sweep itself named: the scorer TRUNCATES floats instead of rounding,
giving a systematic -0.5 voxel bias. Truncation applies on private too => dead both directions.
LESSON: a proxy CI excluding zero is not enough when the output CONTRACT is unverified.
### 2. SUB-VOXEL SOFTARG = neutral on public (0.946, -0.001)
Mechanism verified live (16 `SUBVOXEL_ACTIVE` lines, mean offset 0.17 lattice voxel). Keeps int
coords, so it dodges what killed hfloat. Proxy said +0.0050 on unseen embryos, ~0 on memorized.
=> a PRIVATE-ONLY bet. Use only as the diversified Final B, never as the primary.
### 3. DETECTOR ENSEMBLING (hengck23 cell-point-detector) = CLOSED, unaffordable
Loaded cleanly with `weights_only=True` (no untrusted pickle), 0 missing/0 unexpected of 112,
12 s/movie. On our 20-movie harness it is WORSE than the public detector:
  node<=2um 0.658-0.663 vs public **0.6999**; T_pred/T_true 1.34-1.47 vs ~0.85-1.0.
(his claimed 1.434um was a MEAN over matched nodes on ONE movie; measured like-for-like his
 median is 1.72um, identical to public.)
BUT the errors are strongly decorrelated - it finds **+0.0965 of GT that public misses**
(union ceiling 0.8121 vs public 0.7156). It still cannot be used, because harvesting costs nodes:
| hengck thr | d coverage | Tp/Tt | d from coverage | d from node-count | NET |
|-----------|-----------|-------|------------------|-------------------|-----|
| 0.8 | +0.0267 | 1.149 | +0.007 | -0.034 | **-0.027** |
| 0.9 | +0.0061 | 0.859 | +0.002 | -0.009 | **-0.007** |
| 0.95| +0.0001 | 0.768 | ~0 | ~0 | ~0 |
Tightening its threshold removes cost and benefit together. Detector ensembling is CLOSED.

## THE NODE-COUNT TERM IS THE BINDING CONSTRAINT (and the live lever)
adjEJ = J * (1 - 0.1*(T_pred - T_true)/T_true). Production sits at **T_pred/T_true = 0.763**,
i.e. already earning a ~+2.4% CREDIT. It is what killed the detector ensemble, so attack it directly.
KEY MEASUREMENT: **node<=2um is FLAT across every detection threshold** (public: 0.7544@0.80 vs
0.7538@0.98) while node count falls steadily. DET is purely a node-count lever, never a
localization lever - which is WHY every DET sweep we ever ran plateaued.
IN FLIGHT: `hdet98` (DET 0.965->0.98, SUBMITTED) and `hdet975` (0.975) on the hfusion body.
 * !! DET_THRESHOLD IS INSIDE `_EXPECTED_NUMERIC` in this body. My first build patched only the
   env line; both kernels would have died on "Configuration drift detected" and burned 2 slots.
   Patch env AND guard in lockstep, then assert zero stale "0.965" references. !!
 * Counter-evidence: on the OLD grafael body higher DET scored WORSE (0.970->0.934 vs 0.965->0.941),
   so downstream linking may degrade in a way raw coverage does not show. Two points give the shape.
ALSO RUNNING (local, full official metric): `loeo_pipeline.py` sweep of OUTPUT_MIN_TRACK_LEN
(6/8/10/12) over 71 movies - the same node-count family, testable WITHOUT a submission.
`loeo_pipeline.py <pred_dir> <movies.txt> <label> [KEY=VAL ...]` runs prologue+epilogue+official
scorer on predicted geffs and accepts env overrides. This is the local testbed to use from now on.
Bootstrap every delta before submitting (the division reranker shipped at 1.7x BELOW 1 sigma).

## PPSWEEP selects `combo(relaxed9+tight55)` at runtime
(MOTION_RELINK_RELAXED_UM 9.0 + TIGHT_UM 5.5, chosen on 8 held-out TRAIN videos). Already active
in our 0.947. The sweep measured tight55 at noise level, so nothing further there.

## FINALS (2026-09-29): A = `hfusion` 0.947 (anchor). B = `hsoft` (private-favouring, public-neutral).
Kaggle scores the BEST of the two on private, so B should be the diversified bet, not a near-copy.

## LEVER-HUNT RESULT (ultracode, 142 agents, 16.4M subagent tokens, ~3.2h)
41 distinct levers from 52 kernels + 3 detector deep-dives + forum + rules + code archaeology.
**Exactly ONE family survived 2-of-3 adversarial lenses: OUTPUT-COORDINATE PRECISION.**
40 rejected (novelty killed 39: already in baseline or on the closed list; private-transfer killed 40).
Verifiers ran real end-to-end measurements with bootstrap CIs on the box:
| variant | unseen-embryo proxy dAdjEJ (n, t, 95% CI) | memorized dAdjEJ |
|---------|---------------------------------------------|------------------|
| **float writer**  | **+0.0051** (54, 2.76, [+0.0016,+0.0087]) | +0.0007 (non-negative) |
| **softarg (full)**| **+0.0050** (71, 2.83, [+0.0016,+0.0085]) | -0.0025 (wide CI) |
| outonly_softarg   | +0.0039 | -0.0060 |
| parabolic (any)   | +0.0021 n.s. | -0.0050; public twin -0.036 -> NEVER USE |
**Why float writer works:** linefit_smooth already produces FLOAT positions, but the writer does
`max(0, int(round(float(node[k]))))` (cell 5), snapping z back onto the 1.625um slice grid and
throwing the smoothing away. Fix = `round(max(0.0, float(node[k])), 3)`.
**RISK:** the Evaluation page describes z/y/x as "integer centroid coordinates in voxels". The
scorer may REJECT floats (slot lost) or silently truncate (ambiguous). hfloat's LB score answers it.
If floats are rejected, hsoft is the in-spec route (softarg still helps with int rounding).
**Public LB CANNOT validate these:** on the 44b6 public twins the deltas were 0.0000 and -0.0002.
The case rests on the unseen-embryo proxy (LOEO detector, a weak proxy). Expect ~0 on public.
Settings the proxy CONFIRMED to leave alone: PPSWEEP on; SAFE_DIV_SISTER_SYMMETRY_TAU 0.6
(0.75 measured -0.0012, CI excludes 0). Null/harmful on unseen proxies: AdaBN, scale TTA,
pool kernel 6.0, hysteresis, DC node veto, boundary exemption, always-on short-track rescue.

### Softarg implementation (v_hsoft) - verified before submitting
Patch appended to the END of notebook cell 4 (after the last `_ps.write_text`, the secondary-TTA
patch), so it sees the fully patched predict_unet_transformer.py. 4 anchors, each verified to match
EXACTLY ONCE in the production file; the patch raises on any mismatch (no silent false null) and
prints `SUBVOXEL_ACTIVE nodes=.. mean_abs_off_vox=..`. Peaks stay int for `_index_features`; only
output coords get the offset, kept float (build_graph stores Float64). The coordinate-manifest SHA
is diagnostic only (1 reference, no assert). Synthetic Gaussian test: direction correct on every
axis, magnitude ~80% of true (softmax shrinkage, conservative), edges zeroed.

## RECOMMENDED FINALS (revised): Final A = hfusion (0.947 control). Final B = whichever of
hfloat / hsoft scores within 0.002 of A on public (public cannot show their gain; they are the
private-set bet). Prefer float if the scorer accepted it.

## FORUM / RULES (read by the sweep's forum agent)
* External data + public pretrained models are EXPLICITLY ALLOWED (Code Requirements page).
* hengck23 (240th) independently corroborates output precision: his refine step cut localization
  error 1.1766 -> 0.969 ("magic or overfitting?", 740145).
* hengck23 StrongUNet3D point detector has public weights (hengck23-cell-point-detector-demo,
  69MB) - passed legitimacy as a 3rd ensemble member, failed private-transfer on thin evidence.
* REJECTED exploits: outwrest augment_dataset hub node (patched Jul 17, now lowers score);
  hengck23's "smart encoding" of test info into submissions (= leaderboard probing);
  duplicate-track inflation (host filters exact dups; perturbed copies lower J).

## LOEO NODE-COUNT FLIP = REFUTED (within-embryo control). See section below.

## WHY WE FELL TO ~457: a NEW PUBLIC RECIPE we structurally could not reach
LB snapshot 2026-09-11: 0.948+ = 61 teams | **0.947 = 123** | **0.946 = 272** | 0.945 (us) = 52.
A 123-team cluster = a public notebook. Found it: Sept 9-10 kernels
`flexonafft/biohub-harmonic-fusion` (170 votes), `flexonafft/biohub-lineage-forge-precision-tracking`,
`sjlee101/biohub-lf-dctta*`. They add THREE mechanisms as **NEW CODE** (0 references in our 946 body,
so no knob on our side could ever reach them):
  * `DEEPCENTER_TTA=1`                          - TTA on the DeepCenter center-prior model
  * `SECONDARY_EDGE_FEATURE_TTA=1` (+_WEIGHT 0.75) - edge-feature TTA on the SECONDARY model
  * `PPSWEEP` - in-kernel post-proc selection: 7 candidates (gap45, tight55, relaxed9, bonus125,
    gap2step40, reuse28, dcgap035) scored on held-out TRAIN videos; applied only if it beats base by
    SELECT_MARGIN without losing > MAX_ADJ_LOSS adjEJ. LEGITIMATE (train labels, never test).
    Caveat: those videos were memorized by the alltrain detector, so selection happens under
    memorized conditions and may transfer less well to private.
All four audited CLEAN, and use ONLY the 3 public pilkwang datasets we already use (no mirrors).
=> `eeshsaxena/biohub-v-hfusion` = harmonic-fusion forked UNMODIFIED. v1 ERRORED (T4/P100 issue),
   **v2 COMPLETE and SUBMITTED 2026-09-11** (4 slots left that day). Watcher died with the session;
   submitted by hand, sentinel `hfusion.SUBMITTED`.

## LOEO NODE-COUNT FLIP HYPOTHESIS = REFUTED by the within-embryo control (2026-09-11 16:12Z)
| LOEO detector evaluated on | embryo seen? | T_pred/T_true @~0.965 | node<=2um |
|----------------------------|--------------|-----------------------|-----------|
| its OWN 12 held-out 6bba   | YES          | **1.596**             | 0.528     |
| 71 movies of 44b6          | NO           | 1.374                 | 0.604     |
It over-predicts MORE on its own embryo than on the unseen one, and localizes worse there too.
=> explanation (b): over-prediction is a property of the under-trained LOEO model (16 epochs,
   one embryo, from scratch), NOT an unseen-embryo effect. No evidence the public detector will
   over-predict on private. **No adaptive node-count calibration lever. Do not pursue.**
=> The 0.754 vs 0.604 gap is NOT a clean memorization gap either: the LOEO detector is weaker
   across the board (0.528 even at home). It is a poor proxy for "public detector on unseen data".
   **We still cannot quantify the private memorization gap.**
SURVIVES (held in all 3 evaluations: public, LOEO-cross, LOEO-within): localization is FLAT across
every DET threshold. DET is purely a node-count lever. That is why every DET sweep plateaued.
Process note: flagged as "unconfirmed, do not act until control lands" - the control landed and
killed it. Holding the action was the right call.

## (superseded) ORIGINAL LOEO CLAIM, kept for the record:
Leave-one-embryo-out (LOEO): a detector trained ONLY on embryo 6bba, evaluated on all 71 movies of
embryo 44b6, which it never saw. Compared with the public alltrain detector, which MEMORIZED 44b6.
| detector on 44b6 | saw 44b6? | node<=2um | T_pred/T_true @ DET 0.96 |
|------------------|-----------|-----------|--------------------------|
| public           | YES       | **0.754** | **0.903** (under-predicts -> metric CREDIT) |
| LOEO (6bba-only) | NO        | **0.604** | **1.374** (over-predicts  -> metric PENALTY) |
1. **node<=2um is FLAT across every DET threshold (0.80-0.98) for BOTH detectors.** DET is purely a
   NODE-COUNT lever, never a localization lever. This is WHY every DET sweep we ran plateaued.
2. **Node-count term may FLIP SIGN on unseen embryos.** Memorized under-predicts (0.903 -> +~0.01);
   honest over-predicts (1.374 -> -~0.04). If that transfers to the public detector on the PRIVATE
   embryos, a threshold tuned on public is badly miscalibrated for private, for EVERY team.
**NOT YET ESTABLISHED.** Two explanations with opposite implications:
   (a) an UNSEEN EMBRYO causes over-prediction  -> a real, exploitable private-set lever
   (b) the LOEO model over-predicts EVERYWHERE because it is less trained -> irrelevant to private
**The control** (`~/biohub/run_loeo_withinvs.sh`, alive, gated on graph generation): same LOEO
detector on its OWN 12 held-out 6bba movies. If T_pred/T_true there is ~0.9 -> (a). If ~1.4 -> (b).
Output: `~/biohub/sandbox/deteval/out/loeo_on_6bba_heldout.{txt,json}`, log `loeo_withinvs.log`.
Also in flight: full-pipeline LOEO graphs for 44b6 (50/71 at 14:27Z) -> honest full-metric score on
an unseen embryo vs the memorized baseline = the memorization gap ON THE ACTUAL METRIC.
**If (a) holds, the lever is ADAPTIVE per-movie node-count calibration**, since one global DET cannot
be right for both memorized public and unseen private. Do not act on this until the control lands.

## LEVER-HUNT WORKFLOW (ultracode, 14-agent sweep) - resumed after a session restart
Sweep 14/14 + dedup done; verify was 38/54 when interrupted. Resumed from cache as run
`wf_c7a9bb3e-44a`, script copied to `scratch_kernels/_intel/sweep0911/lever_hunt.js`.
Sources: 52 public kernels, 3 detector deep-dives (hengck23/cell-point-detector, tangai1 c42 PU
appearance detector, tangai1 c43 detector ensemble), forum + RULES (external-data ruling), and a code
archaeologist over the baseline's 62 knobs that run on untested defaults.

## THE STRATEGIC FACT THAT REFRAMES EVERYTHING
From INTEL.md (metric deep-probe): **"Train/test embryo-disjoint; visible test = train copies."**
* PUBLIC board = copies of TRAIN volumes, which the alltrain detector memorized.
* PRIVATE board (71%, decides the winner) = embryos NOBODY trained on. A true domain shift.
* Train has exactly 2 embryos: **44b6 (71 movies, 20,197 GT nodes, 26 divs)** and
  **6bba (128 movies, 113,121 GT nodes, 125 divs)**.
=> Neither the public LB nor our local harness predicts private (both memorized).
=> Everyone uses the SAME public detector, so on private everyone's detection degrades
   identically. The winner among honest teams = whoever's post-detection pipeline holds up
   best under detection that has NEVER SEEN the embryo.
=> LOEO is the ONLY honest way to reproduce the private condition with our data.

## LOEO EXPERIMENT (running)
* Detector trained on **6bba ONLY** (`~/biohub/data/train_6bba`, 128 symlinked movies,
  verified ZERO 44b6 leakage), **FROM SCRATCH** (init from public would leak - it saw 44b6),
  native 1,4,4, bs 6 (headroom for the user's RSNA job), lr 1e-4, 16 x 1500-iter blocks.
  Split 116 train / 12 val. ~3.9 s/it early -> ~90 min/block -> ~24h.
  Log `~/biohub/runs/loeo_6bba.log`. Writes to the DEFAULT weights/ path (there is no
  --output-dir flag); ft122 is safe in ckpt_snapshots/ft122_final.
* Chained eval `~/biohub/run_loeo_eval.sh` -> `loeo_eval.log`: on the 71 UNSEEN 44b6 movies,
  public (memorized) vs LOEO (honest), DET swept 0.80..0.98.

### LOEO CHAIN - runs ON THE BOX, survives session restarts (set up 2026-09-11)
1. `~/biohub/box_loeo.sh` -> training, log `~/biohub/runs/loeo_6bba.log`
   epoch 0: recall 0.8683 (6bba val). ~40 min/block, 16 blocks ~= 10.7h.
2. `~/biohub/run_loeo_eval.sh` (waits for trainer exit) -> `~/biohub/loeo_eval.log`
   snapshots ckpt to `~/biohub/ckpt_snapshots/loeo_6bba/`, then deteval on the 71 44b6
   movies, public(memorized) vs LOEO(honest), DET swept 0.80..0.98.
3. `~/biohub/run_loeo_graphs.sh` (waits for "LOEO EVAL DONE") -> `loeo_graphs_driver.log`
   LOEO graphs on 44b6 @ det 0.965 -> `~/biohub/pred_graphs_loeo/`, then scored.
* Full-pipeline harness ported to `~/biohub/loeo_harness/` (repair_prod + scoring +
  divmetrics + loeo_pipeline.py; PROD_ENV and load_pred_geff copied VERBATIM from run20).
  Smoke test: 3 movies adjEJ 0.896 (local harness 0.899). ~23 s/movie on CPU.
  usage: `loeo_pipeline.py <pred_dir> <movies.txt> <label> [KEY=VAL ...]` -> out/<label>.json
* Memorized reference: `public_memorized_44b6_det0965` (public graphs, 71 movies).
* CAVEAT: box graphs come from the STOCK predict script (no secondary model, no dual-seed,
  no 8-view TTA patches). Absolute numbers will NOT match production; the RELATIVE
  public-vs-LOEO comparison and the DIRECTION of DET calibration are what transfer.

### Why this is worth a day of GPU: DET THRESHOLD CALIBRATION FOR PRIVATE
Production DET=0.96 was tuned against the MEMORIZED public board. On an unseen embryo the
detector's confidence distribution shifts, so the right threshold may differ substantially.
The node-count term (T_pred/T_true) and edge recall both hinge on it. If 0.96 is
miscalibrated for new embryos, that may cost more on private than anything tuned on
public - and the fix is ONE NUMBER in the final submission.
Second payoff: honest detections on 44b6 let us score candidate finals under private-like
detection (needs the repair harness ported to the box - NOT yet there; only deteval is).

### RISK
Both previous FROM-SCRATCH runs peaked by epoch 1-3. This one removes one cause (native
resolution, flip-aug bug already fixed) but may still be unstable. Abort if it collapses.

## RSNA JOB ON THE BOX IS THE USER'S - NEVER KILL IT
pid 1774468 `box_finetune_radimagenet.py --fold 3` (miniconda3/envs/rsna), ~1 GB.
Share the card. Size our batches to leave headroom.

## RECOMMENDED FINALS (UPDATED 2026-09-15 23:00Z; supersedes the pair/ed0943 advice below)
Current 0.947 submissions: `hfusion` 56167373, `lforge` 56171880, `sectta` 56172900, `mtl8` 56185308,
`vdr25` 56254336. Below: hsoft/vdr20 0.946, pair/det955/hdet98/hdet975 0.945.
* **Final 1 = `hfusion` (56167373)**: the public harmonic-fusion notebook forked UNMODIFIED; no local-only tweaks,
  audited clean. mtl8 and vdr25 tie it but add levers that were embryo-negative or LB-neutral.
* **Final 2 = `lforge` (56171880)**: same 0.947, different lineage (lineage-forge, no harmonic fusion), also
  audited clean and unmodified. `sectta` (lforge + DeepCenter TTA 0.25 + secondary TTA) is a close alternative.
* Caveat: every candidate shares the same public detector stack, so the diversity is modest. Re-open this only if
  a new submission beats 0.947 on the public LB (e.g. an ftgc checkpoint that passes blend_guard + Zebrahub).
* The user makes the final selection on Kaggle by 2026-09-29.
## (superseded) RECOMMENDED FINALS: `pair` (0.945) + `ed0943` (0.943).

## FINAL-SELECTION RECOMMENDATION (the most important remaining decision)
Kaggle scores the **BEST of your 2 selected finals** on the private set (71% of test).
So final #2 should be chosen for DIVERSITY, not rank.

Submissions cluster into three LINEAGES:
| lineage | submissions | public |
|---------|-------------|--------|
| **946 body** (reyhanksatria) | pair, det955, sew25, 946, divrank2 | 0.943-**0.945** |
| **ed0943** (dominance arm)    | ed0943, stack | 0.943 |
| **div941** (qrz1201 repro)    | div941, div941full, det955val, edgetta | 0.941 |

* **Final 1 = `pair` (ref 56117989, 0.945).** Best public, most-replicated lineage (5 subs,
  all 0.943-0.945 = the most robust estimate we have). `det955` (56128881) is EQUIVALENT
  (DET 0.955 vs 0.96, both 0.945, the DET plateau is flat) - either is fine.
* **Final 2 = `ed0943` (ref 56093174, 0.943).** Best of a genuinely different lineage.
  If private tracks public, `pair` counts and this costs nothing. If the 946 lineage has
  public-specific fit, this can hold up. It is a free option.
* **Do NOT pick `pair` + `det955`** - near-duplicates, nearly the same bet twice.
Honest caveat: all lineages share the SAME public detector, which is the dominant error
source, so they are correlated and the diversity benefit is real but modest.

### Exploit audit of both finals (done 2026-09-11) - CLEAN
negative-coord synthetic rows 0 | test-label/geff reads 0 | hardcoded test ids 0 |
requests/urllib 0. Flagged items checked by hand and are benign: the only unusual input
path is the bare `/kaggle/input/` root (dataset discovery); every `synthetic` token is
legitimate gap-closing midpoint synthesis (`gap_inserted_synthetic`,
`refine_synthetic_midpoint`, ...). ed0943 carries nothing that pair does not.

## !!! CORRECTION 2026-09-11: THE DETECTOR EVAL WAS CONFOUNDED BY MEMORIZATION !!!
The public detector is `method = unet_transformer_alltrain_seed314159_v1` - trained on ALL
199 training movies, NO held-out split (checked SNAPSHOT_MANIFEST.json). Therefore:
* Its deteval score on ANY train movie is MEMORIZED, not a generalization estimate.
  On the 19-movie split, public = 0.6733 because it TRAINED on those 19.
* ft122 was trained (fine-tuned) on the OTHER 180, so its 0.5499 on the 19 is closer to
  held-out. The comparison was tilted toward public. I called it "a clear fail, not
  borderline" - that was OVERCONFIDENT.
* WHAT STILL HOLDS: the 1,2,2 result has a MECHANISTIC cause independent of memorization
  (scale learned at 1,4,4; doubling Y/X makes cells 2x larger in voxels; over-prediction
  Tp/Tt 1.41 vs 1.07). So 1,2,2 is very likely genuinely worse.
* WHAT IS NOT ESTABLISHED: "fine-tuning hurts generalization". It was never testable here.
* CONSEQUENCE: **there is NO clean local test of detector generalization anywhere in the
  training data.** Every train movie is memorized by the public detector. The only honest
  test of a detector is the PRIVATE set. The ft144 control will be confounded the same way.
  => DO NOT ship an unvalidated detector. Detector work cannot be validated locally.

## WHY THIS MATTERS FOR WINNING (the strategic picture)
* Public LB = 4 test volumes that are byte-verified TWINS of train volumes, which the
  alltrain detector memorized. Public reads +0.034 to +0.077 ABOVE honest holdout CV.
* Private LB = 71% of test, presumably NOT twins -> every team's detector is honest there,
  every team drops, and the board RESHUFFLES.
* Several >=0.95 public scores come from the `augment_dataset` hub-node METRIC EXPLOIT
  (DQ risk; host already patched a similar division exploit on 2026-07-17). We deliberately
  do NOT use it. If those teams are DQ'd or their trick fails on private, honest ~0.945
  configs move UP. Only 36 of 3286 teams hold >=0.948 publicly.
* So: the controllable levers for the private board are (1) robustness, (2) final-selection
  diversity, (3) staying clean. All three are in hand.

## DETECTOR FINE-TUNE = CLEAR FAIL on the pre-registered test (SEE CORRECTION ABOVE - confounded)
`ft122`: FULL-INIT from the 400ep checkpoint (136/136 tensors), downsample 1,2,2, lr 2e-5,
12 x 1500-iter blocks. Training curve: plateau, NOT collapse (0.9274 -> 0.9351, flat from
epoch 4) - the pretrained init fixed the from-scratch instability. But:
| per-node localization, same 19 movies | public | ft122 | delta |
|---|---|---|---|
| **node <= 2um** | **0.6733** | **0.5499** | **-0.123** |
| node <= 1um | 0.2320 | 0.1711 | -0.061 |
| median / p90 residual | 1.72 / 2.19 um | 1.86 / 3.28 um | worse |
| predicted/true nodes | 1.07 | **1.41** | over-predicting |
| 44b6 / 6bba <=2um | 0.684 / 0.672 | 0.613 / 0.542 | both DOWN |
Far below the public model's own bootstrap CI lower bound (0.6332). Official-matcher view
agrees (0.537 -> 0.422). MECHANISM: the model learned its scale at 1,4,4; doubling Y/X
resolution makes every cell 2x larger in voxels -> more peaks, placed worse. This also
explains both from-scratch 1,2,2 failures. **Finer resolution hurts, with or without
pretraining.** Checkpoint + eval preserved at `~/biohub/ckpt_snapshots/ft122_final/`.
NOTE the public baseline on THIS 19-movie split is 0.6733; the 0.6999 in older notes is the
20-movie edge20 set. Always compare on the same movies.

### Control in flight: `ft144` (same fine-tune at NATIVE 1,4,4, 8 blocks)
Separates "fine-tuning hurts" from "the resolution change hurts". Eval auto-chained
(`~/biohub/run_deteval_ft144.sh` -> `deteval_ft144.log`). Expectation: roughly flat, since
the public model is already converged (best_epoch 381/400, best_score 0.978). Only a
materially higher node<=2um with a CI excluding zero would change the recommendation.

## HONEST CEILING: 0.945 for this pipeline
Both big terms are detection-bound and the detector cannot be improved:
* EDGE: 96.69% of GT edges already correct where detection works; only 3% of fragmentation
  is a true gap (0% inside the gap radius); 90% of mis-assignments are the true partner
  sitting 2.24x farther than the chosen one. Linking is not the problem.
* DIVISION: learned reranker LB 0.943 vs 0.945 (NEGATIVE). Local +0.00345 was 1.7x smaller
  than one sigma (+/-0.00576 on 29 divisions) - never resolvable.
* DETECTOR: 3 attempts (scratch 1,2,2 / scratch 1,4,4 / fine-tune 1,2,2), all negative.

## PROCESS RULES LEARNED (read before any future experiment)
1. **Bootstrap the local delta over movies before submitting.** If |delta| < 1 sigma, do not
   spend a slot. (Cost two submissions on the division reranker.)
2. **A logistic threshold is scale-dependent** - never swap a model without re-sweeping.
3. **The 20-movie adjEJ harness is unpowered below ~0.01** - it has mispredicted the LB 5x.
4. **Identical sweep rows = suspect env propagation first** (the apply_env bug), but verify
   before calling it a bug: 3 of 4 such cases this session were genuine true negatives.
5. **tqdm carriage returns hide log lines** - always `tr '
' '
'` before grepping.
6. **Box soft FD limit is 1024** - training needs `ulimit -n 65536` (hard limit ~1M).

## CLOSED NEGATIVES (do not re-run)
detector fine-tune @1,2,2 | detector from scratch (1,2,2 and 1,4,4) | learned division
reranker | edge-feature TTA (public "+0.005" claim is FALSE) | DET threshold (0.96=0.955) |
SECONDARY_EDGE_WEIGHT | distance gates | mutual-NN | divergence | global 2-pass | per-movie
budgets | image features | gap-closing | edge re-assignment | short-track pruning vs
divisions | orphan-relax | node-count pruning | relink family

## !!! PROCESS RULE LEARNED THE HARD WAY: COMPUTE THE NOISE FLOOR FIRST !!!
The 20-movie harness holds **29 GT divisions**. Bootstrapped over movies, the 1-sigma noise
on 0.1*divJ is **+/-0.00576** (95% CI width 0.0225). The effect I shipped two submissions on
was **+0.00345 = 1.7x SMALLER than one sigma**. It was never resolvable on this harness.
LB confirmed: local +0.00345 -> **LB -0.002**.
BEFORE treating any local delta as real, bootstrap it over movies. If |delta| < 1 sigma,
do NOT spend a submission.

## DIVISION TRACK: CLOSED, LB-NEGATIVE
| submission | what | LB |
|------------|------|-----|
| `divrank`  | learned reranker, WRONG threshold scale (leaky model @2.0 = ~6.3) | **0.937** |
| `divrank2` | learned reranker, held-out model, correct scale, thr 2.0 | **0.943** |
| `pair` / `det955` | no reranker | **0.945** |
The mechanism is real, verified firing (DIVRANK_ACTIVE, 792 invocations), and validated
+0.00345 locally - and it still LOSES 0.002 on the LB. This is the **5th** time the 20-movie
adjEJ harness has mispredicted the LB (prune stack, edge model, SAFE_DIV_MAX_UM, relink
family, now the division ranker). Treat that harness as UNPOWERED for anything below ~0.01.

## THE TWO BIG TERMS ARE BOTH DETECTION-BOUND (measured, 199 movies + 20-movie cache)
### Edge term: 96.69% already correct where detection works
GT edges 12,587 | both ends detected+matched 12,332 (98.0%) | **already present 11,924
(96.69%)** | fragmented 408 (3.31%).
Of the 408 fragmented: source already linked elsewhere 306 (75%), target already linked 321
(79%), **TRUE GAP (both ends free) = 13 (3%)** at median 10.8um with **0% inside the 5um
GAP_CLOSE_UM radius**. => gap-closing is correctly inert; stop testing it.
Of the 306 source-mis-linked: true target NEARER than chosen **31 (10%)**, FARTHER **275
(90%)**; dist to TRUE p50 **7.62um** vs CHOSEN p50 **3.54um** (**2.24x**). The linker picks
the nearest and the true partner is 2.24x farther - it is behaving correctly given its
inputs. => "+0.06 from fixing assignments" is FALSE.

### Division term: ceiling ~+0.0035 locally, and that is below the noise floor. Closed.

## THE ONLY REMAINING BET: FINE-TUNE THE PUBLIC CHECKPOINT (armed, box was DOWN)
Detection localization is worth **+0.0804** (residual-conditioned oracle: every GT cell
inside 2um -> adjEJ 0.9793). Both prior detector runs trained **FROM SCRATCH** for 40 epochs
against a **400-epoch** public model and collapsed at epoch 1-3. Never tried: fine-tune the
public checkpoint itself.
* `~/biohub/ft_patch.py` adds `--init-weights` = FULL UNetNodeTransformer init.
  The stock `--unet-weights` restores only the 74 `unet.*` keys and leaves 60 `transformer.*`
  + 2 `detect_head.*` RANDOM, which is not a fine-tune. Patch asserts on every anchor and
  raises if >10 tensors are missing.
* `~/biohub/box_finetune.sh ft122` = pretrained init + downsample **1,2,2**, bs 3, lr 2e-5,
  12 epochs. Controls: `ft144` (same downsample, isolates "finer" from "more training"),
  `ft122b` (lr 1e-4).
* `/tmp/autolaunch_ft.sh` polls the box for 4h and fires automatically when it returns.

### PRE-REGISTERED SUCCESS CRITERION (fixed BEFORE any result)
Judge ONLY on `sandbox/deteval/eval_localization.py`, the per-node localization residual over
tens of thousands of nodes - NOT on local adjEJ (unpowered, see above).
**PASS = bare-detector fraction of GT nodes within 2um EXCEEDS the public baseline 0.6999.**
Anything else is a fail, however good adjEJ looks.

## CLOSED NEGATIVES (do not re-run)
learned division reranker (LB 0.943 vs 0.945) | edge-feature TTA (public "+0.005" is FALSE) |
DET threshold (0.96=0.955=0.945) | SECONDARY_EDGE_WEIGHT | distance gates (recover ZERO) |
mutual-NN | divergence | global 2-pass | per-movie budgets | IMAGE features (real signal,
AUC 0.75, zero gain over geometry) | gap-closing (3% of fragmentation is a true gap) |
edge re-assignment (90% detection-driven) | short-track pruning vs divisions | orphan-relax |
detector training FROM SCRATCH | node-count pruning | relink family

## ASSETS
`~/biohub/pred_graphs` 199 graphs | `divrank_big.npz` 290,942 proposals / 98 positives |
`divrank_model.json` (held out) | `repair_learn.py` / `repair_glob.py` |
`frag_oracle_local.py` / `frag_blame.py` / `oracle_rank.py` / `gate_blame.py`

## HONEST CEILING ASSESSMENT: 0.97 IS NOT REACHABLE VIA LINKING/REPAIR
Every remaining lever has now been measured to exhaustion. Both big terms are
DETECTION-BOUND, and the detector is the one thing we could not improve.

### Edge term: 96.69% already correct where detection works
| | count | share |
|---|-------|-------|
| GT edges | 12,587 | |
| both endpoints detected+matched | 12,332 | 98.0% |
| **already present in our graph** | **11,924** | **96.69%** |
| fragmented | 408 | 3.31% |

**Fragmentation is NOT a gap-closing problem.** Of the 408:
  source already linked elsewhere 306 (75%) | target already linked 321 (79%)
  **TRUE GAP (both ends free) = 13 (3%)**, median 10.8um, and **0% within the 5um
  GAP_CLOSE_UM radius** (0% even within 8um).
=> every gap-close knob is correctly inert. Stop testing them.

**And the mis-assignments are not winnable either:**
| of the 306 source-mis-linked | n | share |
|------------------------------|---|-------|
| true target was NEARER than chosen (avoidable) | 31 | **10%** |
| true target was FARTHER than chosen | 275 | **90%** |
  dist to TRUE target p50 **7.62um** vs CHOSEN p50 **3.54um**, ratio **2.24x**.
The linker picks the nearest and the true partner is 2.24x farther. It is behaving
correctly given its inputs. Max winnable by better linking = 31 edges / 20 movies.
=> the "+0.06 from fixing assignments" estimate is FALSE. Confirms the original autopsy:
residual-conditioned oracle said detection within 2um gives adjEJ 0.9793 (+0.0804).

### Division term: mechanism at its ceiling, ~+0.0035
Best = per-frame learned reranker, held-out model, thr 2.0 (SUBMITTED as divrank2).
Everything else loses: thr 2.5 +0.00407 (inside noise), global 2-pass -0.0014 to -0.0061,
divergence OFF +0.00055, thr 4.0 -0.005. See the table further down.
**Recall beats precision here**: budget 2/movie gives FP=0 and divJ still falls to 0.138,
because divJ = TP/(29+FP) and the 29 misses dominate the denominator.

### THE ONE UNTRIED ROUTE TO THE BIG PRIZE
Detection localization is worth +0.08 and is the ONLY thing that is. Our two detector runs
both trained **FROM SCRATCH** (40 epochs) against a public **400-epoch** checkpoint and
collapsed at epoch 1-3. NEVER TRIED: **fine-tune the public 400ep checkpoint** at finer
downsample (1,2,2) for a few epochs, instead of training from scratch. That preserves the
learned features and only adapts spatial precision. This is the single highest-value
remaining experiment. Needs the V100 (box was DOWN at 2026-09-10, ssh timeout).

## THE BUG THAT COST A SUBMISSION (divrank = 0.937, -0.008)
A logistic THRESHOLD IS SCALE-DEPENDENT:
    divrank_model.json  intercept -3.5667  <- HELD OUT, validated, USE THIS
    divrank_model_full  intercept -7.8434  <- leaky vs the harness
I validated model.json@2.0 (+0.00345) then submitted model_full@2.0 = ~6.3 on the validated
scale -> forks 569->260, TP 8->6. Local predicted -0.00255, LB delivered **-0.008**.
NEVER swap a model without re-sweeping its threshold.
Silver lining: the LB is demonstrably SENSITIVE to division changes, so divrank2 is a real test.

### Leakage - settled
`divrank_model.json` is BYTE-IDENTICAL to a model retrained excluding all 20 harness movies
(max|coef diff| = 0.0). +0.00345 is honest.

## DIVISION TABLE (held-out model, divJ = TP/(29+FP))
| config | delta | divJ | TP | FP |
|--------|-------|------|----|----|
| per-frame thr 2.5 | +0.00407 | 0.2308 | 9 | 10 |
| **per-frame thr 2.0 (SUBMITTED)** | +0.00345 | 0.2250 | 9 | 11 |
| GLOBAL 2-pass budget 64 | +0.00244 | 0.2143 | 9 | 13 |
| thr 2.0 + DIVERGENCE OFF | +0.00055 | 0.1887 | 10 | 24 |
| BASELINE | 0 | 0.1860 | 8 | 14 |
| GLOBAL 2-pass budget 2 | -0.00614 | 0.1379 | 4 | 0 |

## FN AUTOPSY: A no-fork 16 (76%) | B coverage-blocked 5 (24%) | C pairing 0 (0%)
## GATE ABLATION: distance gates recover ZERO; only divergence (+5) and symmetry (+3)
   raise reachability, and both are net-negative. (deepcenter row = harness artifact,
   local runs pass deepcenter_bundle=None.)

## CLOSED NEGATIVES (do not re-run)
edge-feature TTA (public "+0.005" claim is FALSE) | DET threshold (0.96=0.955=0.945) |
SECONDARY_EDGE_WEIGHT | distance gates | mutual-NN | divergence | global 2-pass |
per-movie budgets | IMAGE features (brightness/mass-conservation: real signal, AUC 0.75,
but ZERO gain over geometry) | gap-closing (only 3% of fragmentation is a true gap) |
edge re-assignment (90% detection-driven) | short-track pruning vs divisions |
orphan-relax alone | detector training FROM SCRATCH | node-count pruning | relink family

## ASSETS
`~/biohub/pred_graphs` 199 graphs | `divrank_big.npz` 290,942 proposals / 98 positives |
`divrank_model.json` (HELD OUT) | `repair_learn.py` / `repair_glob.py` |
`frag_oracle_local.py` / `frag_blame.py` / `oracle_rank.py` / `gate_blame.py`

## !! THE BUG THAT COST A SUBMISSION - READ FIRST !!
A logistic score THRESHOLD IS SCALE-DEPENDENT. Same data, different hyperparameters ->
different intercepts:
    divrank_model.json  intercept -3.5667   <- HELD OUT, validated, USE THIS
    divrank_model_full  intercept -7.8434   <- trained on ALL 199 (leaky vs harness)
I validated model.json@2.0 (+0.00345) then SUBMITTED model_full@2.0, which acts like ~6.3
on the validated scale: forks 569->260, TP 8->6, **-0.00255**.
NEVER swap a model without re-sweeping its threshold.

### Leakage - settled, do not re-litigate
19 of 20 harness movies ARE in divrank_big.npz, BUT `divrank_model.json` is BYTE-IDENTICAL
to a model retrained excluding all 20 (verified max|coef diff| = 0.0). So model.json is
genuinely held out; +0.00345 is honest. Only model_full is leaky, which is exactly why its
apparent "more data" advantage evaporates.

## THE DIVISION MECHANISM IS AT ITS CEILING: ~+0.0035, and everything else LOSES
Held-out model, 20-movie harness, divJ = TP/(29+FP):
| config                                   | delta     | divJ   | TP | FP |
|------------------------------------------|-----------|--------|----|----|
| per-frame thr 2.5                        | +0.00407  | 0.2308 |  9 | 10 |
| **per-frame thr 2.0  (SUBMITTED)**       | +0.00345  | 0.2250 |  9 | 11 |
| per-frame thr 1.0 / 0.5 / 0.0            | +0.00294  | 0.2143 |  9 | 13 |
| GLOBAL 2-pass, budget 64/movie           | +0.00244  | 0.2143 |  9 | 13 |
| thr 2.0 + DIVERGENCE OFF                 | +0.00055  | 0.1887 | 10 | 24 |
| BASELINE (geometric)                     |  0.00000  | 0.1860 |  8 | 14 |
| GLOBAL 2-pass, budget 8/movie            | -0.00141  | 0.1875 |  6 |  3 |
| GLOBAL 2-pass, budget 2/movie            | -0.00614  | 0.1379 |  4 |  0 |
| per-frame thr 4.0                        | -0.00496  | 0.1429 |  5 |  6 |
thr 2.5 beats 2.0 by 0.0006 = INSIDE NOISE (one division is worth ~0.002 on 29). The curve
is flat over [0,3]; taking the argmax would fit noise. Submitted mid-range 2.0 deliberately.

### RECALL beats precision here (corrects my earlier reasoning)
Budget 2/movie matches the true GT rate (~1.5) and achieves **FP = 0**, yet divJ falls to
0.138. Because divJ = TP/(29+FP), the 29 missed divisions dominate the denominator, so
once FP is small, extra TP is worth far more than removing FP. Do not chase precision.

### At thr 2.0 forks only drop 569->494 but TP 8->9, FP 14->11
=> the gain comes from REORDERING, not filtering. And global 2-pass reordering is WORSE
than frame-local, so frame-local greedy ordering is NOT costing us anything.

## GATE ABLATION (gate_blame.py) - which gate blocks the 16 no-fork misses
| gate disabled      | A (no-fork) | TP | FP  | forks |
|--------------------|-------------|----|-----|-------|
| baseline           | 16          |  8 |  14 |   569 |
| divergence OFF     | **11**      |  6 |  44 |  1223 |
| symmetry OFF       | **13**      |  7 |  26 |  1192 |
| parent 9->15       | 16          |  8 |  14 |   586 |
| sister 14->25      | 16          |  8 |  14 |   569 |
| mutual-NN OFF      | 16          |  8 |  15 |   578 |
**Distance gates recover NOTHING** - the earlier "wide gates never win" was testing the
wrong knobs. Only divergence (+5) and symmetry (+3) raise reachability, and divergence
retested cleanly at held-out scale is a REAL negative (+0.00055, buys TP 9->10 for +14 FP).
CAVEAT: the deepcenter-veto row is a harness artifact (local runs pass
deepcenter_bundle=None so the veto is inert), NOT a finding about the real pipeline.

## FN AUTOPSY (21 misses): A no-fork 16 (76%) | B coverage-blocked 5 (24%) | C pairing 0
C = 0 means a fork in a connected component ALWAYS wins its pairing. Nothing to gain there.

## IMAGE FEATURES = NEGATIVE (closed)
Physically sound and individually confirmed - dividing parents ARE brighter
(parent_peak_rel AUC 0.752) and true daughters ARE ~2x more equal in mass (daughter_sym
0.091 vs 0.160) - but they add nothing over geometry:
    geometry only 40% rank1 / median 7.5 | +brightness 37% / 8.5 (HURTS: bright = dense =
    short distances) | +daughter_sym 41% / 7.0 (+1 of 98) | +mass_ratio 40% / 7.5
Data kept at `~/biohub/imgfeat_rows.json` (112,761 proposals, 98 positives, 69 movies).

## ASSETS
`~/biohub/pred_graphs` 199 predicted graphs | `sandbox/div20/divrank_big.npz` 290,942
labeled proposals / 98 positives | `divrank_model.json` (HELD OUT - use this) |
`repair_learn.py` (per-frame) / `repair_glob.py` (global 2-pass) |
oracle_rank / divrank_{data,train,eval,thresh,recal,thr_holdout} / gate_blame / glob_sweep

## CLOSED NEGATIVES
edge-feature TTA (2 bodies, verified live; public "+0.005" claim is FALSE) | DET threshold
(plateaued 0.96=0.955=0.945) | SECONDARY_EDGE_WEIGHT 0.25 | distance gates | mutual-NN |
divergence | global 2-pass selection | per-movie budgets | image features | short-track
pruning vs divisions | orphan-relax alone | detector retraining | node-count pruning

## !! THE BUG THAT COST A SUBMISSION - READ FIRST !!
A logistic score THRESHOLD IS SCALE-DEPENDENT. Two models trained on the same data
with different hyperparameters have different intercepts:
    divrank_model.json  intercept -3.5667   <- HELD OUT, validated, USE THIS
    divrank_model_full  intercept -7.8434   <- trained on ALL 199 (leaky vs harness)
Applying the threshold tuned for one to the other is meaningless. I validated
model.json@2.0 (+0.00345) then SUBMITTED model_full@2.0, which behaves like ~6.3 on the
validated scale: forks 569->260, TP 8->6, **-0.00255**. Never swap a model without
re-sweeping its threshold.

| config                                | delta combined | note                        |
|---------------------------------------|----------------|-----------------------------|
| model_full @ thr 1.0                  | +0.00474       | LEAKY (trained on harness)  |
| **model.json @ thr 2.0**              | **+0.00345**   | **HONEST held-out**         |
| model_full @ thr -4.0/-3/-2.5/-2       | +0.00293       | leaky                       |
| model_full @ thr 2.0 (SUBMITTED once) | -0.00255       | the bug                     |

### Leakage status - settled, do not re-litigate
19 of the 20 harness movies ARE in divrank_big.npz. But `divrank_model.json` is
BYTE-IDENTICAL to a model retrained from scratch excluding all 20 harness movies
(verified: max|coef diff| = 0.0). So model.json is genuinely held out and its
+0.00345 is honest. Only model_full is leaky - which is exactly why its apparent
"more data" advantage never materialised.

### CONFOUNDED, NOT NEGATIVE - divergence must be retested
The div_diverge_rank sweep ran model_FULL at thresholds 2.0-7.0, ALL over-strict.
Its "divergence off loses" rows are VOID, not evidence. Retest is running at
held-out-model scale (`divrank_thr_holdout.py`).

### GATE ABLATION (real, from gate_blame.py) - which gate blocks the 16 no-fork misses
| gate disabled        | A (no-fork) | TP | FP  | forks | divJ   |
|----------------------|-------------|----|-----|-------|--------|
| baseline             | 16          |  8 |  14 |   569 | 0.1860 |
| **divergence OFF**   | **11**      |  6 |  44 |  1223 | 0.0822 |
| **symmetry OFF**     | **13**      |  7 |  26 |  1192 | 0.1273 |
| parent gate 9->15    | 16          |  8 |  14 |   586 | 0.1860 |
| sister gate 14->25   | 16          |  8 |  14 |   569 | 0.1860 |
| mutual-NN OFF        | 16          |  8 |  15 |   578 | 0.1820 |
**The DISTANCE gates recover NOTHING.** Earlier "wide gates never win" was testing the
wrong knobs. Only divergence (+5) and symmetry (+3) raise reachability.
CAVEAT: the deepcenter-veto row is a harness artifact (local runs pass
deepcenter_bundle=None, so the veto is inert). Not a finding about the real pipeline.

### IMAGE FEATURES = NEGATIVE (closed)
Hypothesis was sound and individually confirmed: dividing parents ARE brighter
(parent_peak_rel AUC 0.752, pos med 1.047 vs neg 0.565) and true daughters ARE ~2x more
equal in mass (daughter_sym pos med 0.091 vs 0.160). But they add nothing over geometry:
    geometry only      rank1 40%  median 7.5
    + brightness       rank1 37%  median 8.5   (HURTS - bright = dense = short distances)
    + daughter_sym     rank1 41%  median 7.0   (+1 case of 98)
    + mass_ratio       rank1 40%  median 7.5
Not worth porting frame-loading into the kernel repair path. Data:
`~/biohub/imgfeat_rows.json` (112,761 proposals, 98 positives, 69 movies).

### SUBMITTED: `eeshsaxena/biohub-v-divrank2` v1 (watcher watch_divrank2.py)
v_pair body + reranker in `add_safe_divisions_postlink`, HELD-OUT coefficients inline
(intercept -3.56667), thr 2.0, gates unchanged. Prints DIVRANK_ACTIVE and RAISES if it
scores zero proposals.

### CLOSED NEGATIVES
edge-feature TTA (2 bodies, verified live, public "+0.005" claim is FALSE) | DET threshold
(plateaued 0.96=0.955=0.945) | SECONDARY_EDGE_WEIGHT 0.25 | distance gates | mutual-NN |
image features | short-track pruning vs divisions | orphan-relax alone | detector retraining

## *** THE NODE-COUNT CALIBRATION RULE (2026-09-09) - explains ALL 4 transfer failures ***

DECISIVE MEASUREMENT (not ours - found by mining analyticaobscura/biohub-lb-942 vs
redoctopusk/biohub-942tta, which are BYTE-EQUAL except BIOHUB_EDGE_FEATURE_TTA, both running the
same 7-candidate sweep on the SAME 8 held-out stems):
  turning EDGE_FEATURE_TTA ON moved their local proxy 0.96053 -> 0.94919  (-0.011)
  adj_edge_jaccard 0.92976 -> 0.92611 | div_J 0.3077 -> 0.2308
  PREDICTED NODES 169,925 -> 183,082
i.e. the change that GAINS on the LB reads as a -0.011 REGRESSION locally.

>>> THE RULE: the local validator is admissible ONLY when the two candidates write essentially the
>>> SAME NUMBER OF NODES. Any node-count-changing edit gets an INVERTED signal, because
>>> adjusted_edge_jaccard adjusts against your predicted node count while the GT is sparse (~1%).

This retro-explains every transfer failure in this repo - prune stack, learned edge model, the
relink family, SAFE_DIV_MAX_UM=11 - ALL of them changed node counts. Use this rule instead of the
blanket "never trust local CV": node-count-NEUTRAL edits (e.g. MOTION_RELINK_TIGHT_UM) ARE
measurable locally.

## VERIFIED ONE-KNOB LB PROBE TABLE (real submission ids, body = published 0.941 = ours minus TTA)
| knob | from -> to | LB | delta | sub id |
|---|---|---|---|---|
| DET_THRESHOLD | 0.965 -> 0.96 | 0.942 | +0.001 | 56053765, replicated 56066524 |
| DET_THRESHOLD | 0.965 -> 0.95 | 0.940 | -0.001 | 56064970 |
| DET_THRESHOLD | 0.965 -> 0.94 | 0.938 | -0.003 | 56060188 |
| DET_THRESHOLD | 0.965 -> 0.985 | 0.937 | -0.004 | 56025813 |
| SECONDARY_EDGE_WEIGHT | 0.15 -> 0.25 | 0.942 | +0.001 | 56065642 |
| DEEPCENTER_SAFE_DIV_THRESHOLD 0.26 + GAP_CLOSE_UM 5.8 (PAIR) | | 0.942 | +0.001 | 56056273 |
| SAFE_DIV_SISTER_MAX_UM | 12 -> 14 | 0.939 | +0.004 | 55954542->56023518 |
| SAFE_DIV_MAX_UM | 7 -> 9 | 0.940 | +0.001 | 56024104 |
| divisions entirely OFF | | 0.904 vs 0.924 | -0.020 | 55809052/55809701 |
MEASURED NEUTRAL (do NOT spend a slot): SECONDARY_LINK_MODE->adaptive (56060190);
DEEPCENTER_GAP_THRESHOLD 0.25->0.35 (56064989); DUAL_SEED_EDGE_THRESHOLD 0.48->0.42 (56065638);
DEEPCENTER_SAFE_DIV_THRESHOLD 0.26 ALONE (56056279); SAFE_DIV_MAX_UM 9->10;
SAFE_DIV_EXISTING_CHILD_MAX_UM 10->12; MOTION_RELINK_LEARNED_BONUS 1.0->1.5; GAP_CLOSE_UM 5.8->6.5.
MEASURED HARMFUL: SAFE_DIV_DIVERGE_UM 2.25->4.5 = -0.002 (TWICE on this body - the kimi sweep that
peaks at 4.5 is a DIFFERENT body and is a TRAP); SAFE_DIV_MAX_UM 9->7 = -0.001.
PROVEN INERT: ILP_DIVISION_WEIGHT. With ILP_APPEARANCE_WEIGHT=0.0 the solver forks iff
p2 >= division_weight and p2 <= 1, so ANY weight >= 1 makes forking impossible. We ship 1.2 =>
100% of our divisions come from the safe-div post-process. Sweeping it produces a byte-identical
submission. Never spend a slot on it.

## OUR 0.925 det096 WAS A BROKEN RUN, NOT A MEASUREMENT
v_det096 is byte-identical (code + all 49 knob values) to busyaprime's 0.942 kernel. Our own log is
internally impossible: DET 0.955 -> 0.941, DET 0.960 -> 0.925, DET 0.965 -> 0.941. A monotone knob
cannot crater 0.016 at an interior point flanked by two identical values. DISCARD the 0.925.

## TITLES ARE NOT SCORES (verified against the live board)
Of 7 public notebooks titled "948", NOT ONE author holds 0.948 (their bests: 0.946 x4, 0.943,
0.941, 0.939). busyaprime ran one and scored 0.935 (sub 56045620).
CRITICAL: reyhanksatria/biohub-cell-tracking-0-946-lb - the kernel OUR 946 recipe came from - has an
author board best of **0.944, not 0.946**. So EDGE_FEATURE_TTA is worth ~+0.003, which matches our
own measured 0.941 -> 0.944 EXACTLY. We are at PARITY with that author, not behind.

## PUBLIC/PRIVATE + SHAKE-UP (matters more than any knob)
Public LB = 29% of test data; medals decided on the other 71%. Every 0.001 rung is inside the noise
of that sample (SE ~1e-3). 206 teams tied at 0.946; only 36 of 3286 hold >= 0.948.
MEMORISATION READOUT: the 4 public test volumes are byte-verified TWINS of TRAIN volumes, and the
detector checkpoint everyone uses lists 199 training datasets INCLUDING all four twins. Calibrated
against two parameter-free pipelines that memorised nothing, the public LB reads +0.034 and +0.077
ABOVE honest holdout CV. Expect pipelines whose public score came from seeing those volumes to DROP
on private.
=> FINAL SELECTION: pick the two finals MANUALLY (Kaggle's auto best-by-public cannot break the
   206-way tie), and weight MECHANISM over public rank.

---

## *** EDGE_FEATURE_TTA = THE 0.941->0.946 LEVER (137-agent sweep, 2026-09-08) ***

Exhaustive workflow: 96 candidate kernels swept from 6 angles, 40 pulled+diffed, 0 exploits found,
every candidate knob judged by 3 lenses (adoption / mechanism / compatibility), 2-of-3 to survive.

### THE NEAR-CONTROLLED EXPERIMENT (strongest evidence this project has produced)
Diffing ALL env knobs (BOTH quote styles) between our 0.941 config (49 knobs) and the public
0.946 config (54 knobs): the ONLY FUNCTIONAL DIFFERENCE IS `BIOHUB_EDGE_FEATURE_TTA=1`.
Everything else that differs is mirror plumbing (MODEL_ARTIFACTS, SECONDARY_ARTIFACT_MANIFEST,
TARGET_ARTIFACT_SLUG, ALLOW_ARTIFACT_FALLBACK, DEEPCENTER_CHECKPOINT all just repoint to
reyhanksatria's own mirrors of the same public pilkwang datasets).

### CORRECTIONS TO EARLIER CLAIMS IN THIS FILE
* "seen in 1 kernel" was WRONG. Six INDEPENDENT authors set it to '1':
  reyhanksatria (the 0.946 LB kernel), flexonafft (harmonic-fusion + lineage-forge),
  remusswift (942tta), redoctopusk (948tta), rogerrogerroger3r (run79), brucezheng666 (942tta-repro).
  Spans the 0.942 / 0.946 / 0.948 tiers. ZERO authors set it to '0'. This is what the
  "942tta"/"948tta"/"948tta2" kernel naming refers to - the whole upper shelf is named after it.
* `BIOHUB_MOTION_RELINK_LEARNED_BONUS=1.0` is NOT a differentiator - WE ALREADY SET IT.
  Our kernel writes it with MIXED quotes (os.environ["...RELINK_LEARNED_BONUS"] = '1.0'),
  which is why an earlier single-quote-style scan missed it.

### MECHANISM (read from the code, not inferred)
model.encode(imgs) returns (unet_out, det_logits). The stock 8-view D4 detection TTA computes a
feature map for every augmented view and THROWS IT AWAY (`_, det_flip = model.encode(imgs_flip)`),
averaging only det_logits and keeping the single-pass unet_out. The ~60-line patch captures those
already-computed feature maps, applies the INVERSE geometric transform to each (flip / rot90 -k /
transpose), averages all 8 views, and reassigns unet_out. unet_out is indexed into
unet_feat_src/unet_feat_tgt and fed to model.predict_edges(...) -> edge_logits_pair -> the ILP.
So it TTA-smooths exactly the features that generate EDGE scores, and the metric is edge-dominated.
COST: the 8 augmented encodes ALREADY RUN for detection TTA. Marginal cost = one feature-map clone
plus 7 inverse-transform-and-add ops. NO extra forward passes. Nearly free.

### ADOPTION PATH: APPEND, DO NOT PORT
Our body has ZERO references to the knob, so setting the env var alone is a SILENT NO-OP.
BUT we do NOT need to swap to a foreign body: our kernel already installs its own D4 TTA source
patch, and a byte-comparison shows their `_et_old` anchor is EXACTLY our patched block plus one
trailing newline (ours 1348 chars, theirs 1349, startswith=True, remainder='
' supplied by the
file). So the patch cell APPENDS to our tuned base and its anchor matches uniquely.
=> built scratch_kernels/v_edgetta = our div941 (SAFE_DIV_MAX_UM=9.0, DET_THRESHOLD=0.965 intact)
   + the patch appended to the host cell that owns `_ps` + BIOHUB_EDGE_FEATURE_TTA=1.

### THE PATCH IS SELF-VERIFYING (why it cannot produce a false null)
It raises RuntimeError on: non-unique anchor, compile failure, patch-not-persisted, AND on
`_delta == 0.0` with the message "EDGE-TTA NO-OP ... would read as a false null". It either prints
EDGE_TTA_ACTIVE with a nonzero mean_abs_feat_delta, or the kernel crashes loudly. Check the log for
that line before trusting any score movement.

### CAVEATS (stated, not hidden)
1. The ISOLATED delta of this lever is unmeasured by anyone - adoption is the evidence, not an ablation.
2. The 6 authors may be copying a common ancestor, so they are not fully statistically independent.
3. cfg.det_tta is a repo default in both bodies and never passed as a CLI flag; if it were False the
   block never executes - but that risk is identical for us and for them.

### SUBMISSIONS QUEUED 2026-09-08 (all 5 slots, all exploit-free)
  948     narrow gates 7/12 + checkpoint_last + TTA + sec_edge 0.20
  946     wide gates 9/14 + TTA + learned_bonus (mirrors repointed to public datasets)
  det096  DET_THRESHOLD 0.96 on our own base
  ed0943  adaptive_grouped_confidence_dominance
  edgetta OUR base + ONLY the TTA patch  <-- scientifically cleanest: ONE variable vs a known score
NOTE: 948 (narrow 7/12) and 946 (wide 9/14) are ALTERNATIVE BRANCHES, NOT ADDITIVE - they disagree
on the division gates while sharing TTA. Submitting both is a deliberate hedge.

---

## *** THE 0.946 SHELF LEVER FOUND 2026-09-08: EDGE_FEATURE_TTA ***

The field moved: 0.941 is now rank ~316 of a much larger board. Clusters: 0.946=92 teams,
0.942=119, 0.943=39, 0.941=85. rank@0.945=124, @0.950=21, @0.955=8, @0.960=7 (prize).

### WHAT THE HIGHER SHELVES ACTUALLY SET (our div941 knobs are a strict SUBSET)
Diffing reyhanksatria/biohub-cell-tracking-0-946-lb (54 knobs) vs our div941 (48):
  BIOHUB_EDGE_FEATURE_TTA            = 1     <-- ALGORITHMIC, the common factor
  BIOHUB_MOTION_RELINK_LEARNED_BONUS = 1.0   <-- ALGORITHMIC
  BIOHUB_MODEL_ARTIFACTS / SECONDARY_ARTIFACT_MANIFEST / TARGET_ARTIFACT_SLUG /
  ALLOW_ARTIFACT_FALLBACK            = paths to their PRIVATE MIRRORS (plumbing only)

EDGE_FEATURE_TTA presence across configs:
  our div941: NO | our v_948 (submitted): YES | 948tta2: YES | 948base: NO | 0.946lb: YES
=> it is the common factor of every higher-scoring config, and it explains the "948tta"/"948tta2"
   kernel naming. THE WHOLE SHELF IS BUILT ON TTA.

### CRITICAL GOTCHA
Our div941 kernel BODY contains ZERO references to EDGE_FEATURE_TTA (the 0.946 body has 2).
The newer kernels ship UPDATED CODE that implements edge-feature TTA. So setting the env var on
our old base would be a SILENT NO-OP. You must adopt the newer kernel body, not just the knob.

### MIRROR-DATASET TRICK (secondary, but real)
The 0.946 kernel loads DeepCenter best.pt from reyhanksatria's OWN MIRROR of the pilkwang
datasets, keeping _deepcenter_expected_sha256 = 8040999a and EXPECTED_EPOCH = 2. This PINS the
good checkpoint against the known non-determinism (pilkwang's mount serves best.pt as either
8040999a or the drifted 8164d1ff). Their mirrors are PRIVATE (not attachable). If we ever need to
pin it, mirror the dataset ourselves via a free CPU kernel that verifies the sha before copying.

### KERNELS BUILT / QUEUED 2026-09-08
  v_948   = redoctopusk/biohub-948tta2 (narrow gates 7/12 + checkpoint_last + gap 5.8 +
            sec_edge 0.20 + EDGE_FEATURE_TTA=1). SUBMITTED. rishabhr0y/biohub-948-sew20 is
            byte-identical in config => independent corroboration of the recipe.
  v_946   = reyhanksatria 0.946-LB kernel with the 3 private mirror paths repointed to the public
            pilkwang datasets (5 replacements, 0 leftovers). QUEUED.
  v_det096= REBUILT from our own div941 base (DET_THRESHOLD 0.96, guard patched in lockstep).
  v_ed0943= adaptive_grouped_confidence_dominance arm. QUEUED last (lowest value).

### FAILURE MODE TO AVOID WHEN COPYING PUBLIC KERNELS
v_det096 v1 ERRORED because the source kernel (busyaprime) contained the AUTHOR'S OWN ANALYSIS
CELLS reading our_probes.csv / provenance.csv / single_knob_steps.csv from a private dataset.
ALWAYS grep a pulled kernel for `find("...csv")` / `assert hits` before pushing. v_948, v_946 and
v_ed0943 were checked and are clean.

### METHOD CORRECTION
My knob-diff initially reported "knobs=0" for the 0.946 kernel because it uses SINGLE quotes
(os.environ['BIOHUB_X']) while the regex only matched double quotes. Always match both.

---

## *** DETECTOR RESULT 2026-09-08: THE 1,2,2 DOWNSAMPLE HYPOTHESIS IS FALSIFIED ***

Trained TemporalUNet3D at downsample 1,2,2 on 199 movies (180 train / 19 held out), stopped at
epoch 5 because val recall PEAKED AT EPOCH 3 and then regressed:
  ep0 0.9127 -> ep1 0.9311 -> ep2 0.9353 -> **ep3 0.9427 (peak)** -> ep4 0.9419 -> ep5 0.9299
  train det loss kept FALLING (0.0084->0.0067) while val recall fell = textbook overfitting,
  and it arrived at epoch 3, far earlier than the old "overfits past ~epoch 10" note.
Best checkpoint saved: ~/biohub/ckpt_snapshots/BEST_ep3/ sha256 1adaa515d9fc8c0b32cbec04b13f4af7...

### THE PRE-REGISTERED TEST FAILED (stated BEFORE looking at results)
Prediction: "node<=1um is quantisation-limited at 1,4,4 (grid 1.625um/axis); at 1,2,2 the Y/X step
halves, so if node<=1um does not rise sharply, the finer downsample did not do what it was
trained to do."
RESULT: node<=1um ours 0.2294 vs public 0.2320 = -0.0026 (CI [-0.0334,+0.0443], straddles 0).
IT DID NOT RISE. => finer downsample buys nothing in the band it was supposed to fix.

### FULL A/B (19 held-out movies, 13,335 GT nodes, 12,875 GT edges, GPU, bootstrap n=2000)
DELTA (public - ours), positive = PUBLIC BETTER:
  ALL node frac  <=1um +0.0026  <=2um +0.0726  <=3um +0.0580  <=5um +0.0314  <=7um +0.0079
  ALL edge E/G   <=1um -0.0062  <=2um +0.0581  <=3um +0.0592  <=5um +0.0416  <=7um +0.0112
  CIs EXCLUDE ZERO: node<=2um [+0.0341,+0.1178], edge<=2um [+0.0157,+0.1081]
  Public wins on BOTH embryos. Absolute: ours node<=2um 0.6007 vs public 0.6733 (target was
  >0.6999); ours edge<=2um 0.4784 vs public 0.5365 (target >0.5839).

### MECHANISM OF THE LOSS: MASSIVE OVER-PREDICTION
  Tp/Tt ours 1.382 vs public 1.027. n_pred 509,275 vs 378,539 (+35%).
  Pathological case 44b6_706092f0: 85,087 predictions for 118 GT nodes, <=2um only 0.153,
  median residual 3.08um. The undertrained model sprays detections.

### VERDICT: DO NOT SUBMIT THIS CHECKPOINT. LB best remains 0.941 (div941 config).
Two separable failures: (a) the RESOLUTION lever is wrong (pre-registered test), and (b) the run
was UNDERTRAINED (peak at epoch 3 vs the public model's 50 epochs on all 199 movies).
IF detector work is resumed, do NOT simply retrain at 1,2,2 for longer - the resolution axis is
falsified. The remaining plausible directions are a proper LR schedule + augmentation to get past
the epoch-3 overfit wall, or the `base` (1,4,4) control to separate training-quality from
resolution. Note the public checkpoint saw ALL 199 movies incl. our 19 held-out ones, so the A/B
was already CONSERVATIVE in our favour and we still lost clearly.

---

## SUBMISSION PATH IS BUILT + VERIFIED (scratch_kernels/build_detector_kernel.py)

One command turns a trained checkpoint into a submittable kernel:
  python scratch_kernels/build_detector_kernel.py --ckpt-sha <sha256> --dataset eeshsaxena/<slug>
It patches all three traps automatically and REFUSES to write (exit 1) if any patch is incomplete:
  1+2. both sha256 gates (they share the constant 12f6881e...): manifest gate ~line787 AND the
       ACTUAL-BYTES gate ~line819. Verified: 2 replacements, 0 stale.
  3.   injects BIOHUB_SECONDARY_WEIGHTS="" (+ zero secondary weights) because our 1,2,2 primary
       against the public 1,4,4 secondary raises "incompatible inference grids".
  plus a weight-swap hook after materialize_inference_repo() that copies our .pth (and config.json)
  over REPO_DIR/WEIGHTS_RELATIVE and prints "swapped in our detector: <path>".
VERIFIED on a dry run: 10 cells, 0 syntax errors, all hooks present, old sha absent.
NOTE: the string "incompatible inference grids" still appears in the body - that is just the
raise's message text in the source, NOT a live failure; the guard only runs if
secondary_weights_text is non-empty, and we set it empty.
PREREQ: the checkpoint must already be uploaded as a Kaggle dataset laid out as
  weights/unet_transformer/split_0/edge_predictor_best.pth  (+ config.json alongside).

### TRAINING PROGRESS (recall is the trainer's own val metric, per epoch)
  ep0 recall=0.9127  ep1 recall=0.9311  ep2 recall=0.9353   (all improved, all checkpointed)
  det loss 0.0184 -> 0.0118 -> 0.0100. ~3h37m/epoch. Gains decelerating but NOT plateaued.
  Per-epoch snapshots auto-captured by ~/biohub/ckpt_watch.sh into ~/biohub/ckpt_snapshots/epN/
  (the trainer overwrites the live file on every improvement, so the watcher is load-bearing).

---

## EPOCH-0 A/B RESULT 2026-09-07 - INCONCLUSIVE, do not over-read

Ran sandbox/deteval A/B: ours(1,2,2, epoch 0) vs public(1,4,4, fully trained).
DELTA (public - ours), positive = PUBLIC better:
  ALL node frac:  <=1um +0.0714  <=2um +0.2857  <=3um +0.5000  <=5um +0.2500  <=7um 0.0000
  bootstrap 95% CI: <=1um [+0.0000,+0.1667]  <=2um [+0.0000,+0.5000]
Our checkpoint loses at every band, BUT THIS PROVES NOTHING:
 1. SAMPLE = 28 GT NODES (2 movies, n_gt 12 and 16; capped at --limit 2 --max-frames 16 to fit
    CPU). EVERY bootstrap CI has lower bound exactly +0.0000 - the signature of no resolving power.
 2. 1-epoch model vs a 50-epoch/199-movie model. It SHOULD lose. Says nothing about 1,2,2 vs 1,4,4.
=> The pre-registered <=1um test is NOT YET ANSWERABLE. Do not conclude the downsample lever is
   dead (or alive) from this.

### CONFOUND TO REMEMBER
Comparing our trained 1,2,2 against the PUBLIC checkpoint conflates TWO variables (resolution AND
training run). Cleanly isolating downsample needs the `base` control (1,4,4) trained identically -
that is why box_train_detector.sh has a `base` mode - but it doubles GPU time (~3.5h/epoch each).

### OPERATIONAL FACTS LEARNED
- GPU eval CANNOT run concurrently with training: training holds 13.77GB of 15.77GB, eval OOMs at
  a 768MB alloc. Training is UNAFFECTED by the eval's OOM (separate process).
- CPU eval works but is ~15x too slow for a meaningful sample (2 movies x 16 frames took ~50 min;
  a proper 5-10 movie x 100 frame run would be ~12h).
- => do the REAL A/B only when training is stopped and the GPU is free.
- Checkpoints: the trainer OVERWRITES weights/unet_transformer/split_0/edge_predictor_best.pth on
  every val improvement. SNAPSHOT IT before it moves. Snapshots live in ~/biohub/ckpt_snapshots/
  (ep0/unet_transformer/split_0/{edge_predictor_best.pth,config.json} - the harness needs
  config.json ADJACENT to the .pth or it cannot read the downsample).
- Epoch cost: train 12729.9s + test 306.5s = ~3h37m/epoch. 40 epochs = ~6 days (upper bound only).
- Epoch 0 val: acc=0.9997 recall=0.9127 best=0.9125.

---

## DETECTOR EVALUATION HARNESS (sandbox/deteval/) - built 2026-09-07, smoke-tested

DO NOT judge a trained detector by local adjEJ (4 transfer failures, most recently relink at
-0.002 LB despite +0.010..+0.018 local with tight CIs). Judge it by the LOCALIZATION RESIDUAL:
for each GT node, distance to the NEAREST predicted node (scale 1.625/0.40625/0.40625 um).
That is a per-node statistic over ~13k nodes, not a ~1% subsample graph metric.

### CORRECTED BASELINE - the old "55% within 2um" was the WRONG YARDSTICK
0.5456 was measured on POST-REPAIR production graphs. Re-measured on RAW detector output over
the same 20 movies (this is what a bare checkpoint must beat):

| public detector, raw | node<=1um | node<=2um | node<=3um | recall@7 | E(2um)/G |
|---|---|---|---|---|---|
| det0.980 ALL | 0.2803 | **0.6999** | 0.8398 | 0.9838 | 0.5839 |
| det0.955 ALL | 0.2816 | 0.7021 | 0.8415 | 0.9855 | 0.5869 |
44b6/6bba at det0.980: <=1um .3226/.2659, <=2um .7052/.6981.

TARGETS: node<=2um > 0.6999 AND E(2um)/G > 0.5839, with BOTH embryo prefixes moving the same way.

### THE PRE-REGISTERED TEST (state it before looking at results)
node<=1um is 0.2803 at downsample 1,4,4 because the peak grid quantises to 1.625um/axis - that
band is quantisation-limited BY CONSTRUCTION. Our run trains at 1,2,2, halving the Y/X step.
**If node<=1um does not rise sharply, the finer downsample did NOT do what it was trained to do.**

### HARNESS FACTS
- `sandbox/deteval/eval_localization.py` runs ONLY the detection stage (no linking/ILP/repair),
  or reads an existing .geff with `--pred-dir` and no model at all. Reuses load_model /
  pool_kernel_from_um / _load_frame / _detect_cells_pooled from predict_unet_transformer.py and
  mirrors predict_video's window schedule. Honours the checkpoint's own downsample/window_size/
  pool_kernel_um. Forces math SDP (sm_70). Asserts its peak extraction reproduces
  _detect_cells_pooled bit-for-bit on the first frame of every run.
- `sandbox/deteval/gtmatch.py` vendors the official matcher from kaggle/scoring.py (the box has no
  kaggle/); `python gtmatch.py selftest` re-checks against the original so it cannot drift.
- `--det-thresholds` peels every threshold off ONE forward pass, so sweeping is nearly free.
- Mirrored to ~/biohub/sandbox/deteval/ on the box. Public weights staged at
  ~/biohub/weights_public/unet_transformer/split_0/ (sha 9bac2fa0..e305f), away from the training
  output dir. Movie lists: movies_split0_test.txt (the 19 the running job holds out), movies_edge20.txt.

### VALIDATION OF THE HARNESS ITSELF
- Reproduced the published det0.955-det0.980 effect (+0.0029 raw vs +0.0024 published).
- Recovered n_gtE = 12587, exactly matching resoracle_det0.980.json.
- CPU end-to-end vs the real public checkpoint on 20 frames of 44b6_12dfb391: node<=2um
  0.8629 (model) vs 0.8629 (production geff). Training job never touched.

### TWO CAVEATS TO REPORT WITH ANY RESULT
1. The public checkpoint's training_config.json says train_datasets: 199 - it has seen EVERY movie
   we can test on, while ours holds out 19. The A/B is therefore CONSERVATIVE (biased against us).
2. The out_dsw098 geffs came from the production kernel with SECONDARY_DETECTION_WEIGHT=0.80,
   i.e. a DUAL-SEED mix, not a single checkpoint. Report both views.

---

## HOW TO SHIP A TRAINED DETECTOR (worked out 2026-09-07, BEFORE training finished)

Our trainer writes `edge_predictor_best.pth` - exactly the filename the kernel wants at
`weights/unet_transformer/split_0/edge_predictor_best.pth` (METHOD = "unet_transformer").

### THREE INTEGRITY GATES IN THE KERNEL (all must be handled)
1. line ~787: manifest-declared `model.weight_sha256` vs `_expected_primary_sha256`.
2. line ~877: `_primary_actual_sha256 = _integrity_sha256_file(_primary_materialized_path)`
   vs `_primary_expected_sha256` - **this one hashes the REAL checkpoint bytes. It is the blocker.**
3. line ~803: `_support_expected_sha256` hashes every repo source file (incl. train/predict
   scripts). Weights do not touch these, so this one is fine - but do NOT patch repo sources.
Both SHA constants hold the same value ("12f6881e...") and appear at lines ~787 and ~819.
Patch BOTH to the new checkpoint's sha256. Same class of patch as the config-drift guard.

### GOOD NEWS: downsample comes FROM the checkpoint
`model, window_size, downsample = load_model(weights_path, device)`. The `(1,4,4)` in the
signature is only a default. So a 1,2,2-trained checkpoint drives inference at 1,2,2
automatically - no inference-side change needed.

### THE REAL TRAP: THE DUAL-SEED GRID GUARD
predict_unet_transformer.py raises:
  "Primary and secondary models have incompatible inference grids"
if `secondary_window_size != window_size or secondary_downsample != downsample`.
The production 0.941 config runs a SECONDARY seed at 1,4,4. Our detector is 1,2,2.
=> swapping only the primary HARD-FAILS. Options:
  (A) set BIOHUB_SECONDARY_WEIGHTS="" to disable the secondary. Works, but LOSES dual-seed
      fusion, which is part of what earns 0.941. Net effect could be negative even if our
      detector is better. This is the cheapest first test of raw detector quality.
  (B) train a SECOND seed at 1,2,2 and use both. Keeps fusion. Costs another ~35h of V100.
  (C) train at 1,4,4 to stay drop-in compatible with the existing secondary - but 1,4,4 is
      the public resolution, so it forfeits the localization lever we are testing.
Recommended order: (A) to measure whether our detector alone is competitive, then (B) if it is.

### PACKAGING RECIPE
1. On the box: sha256sum the trained edge_predictor_best.pth.
2. Upload it as a small Kaggle dataset (the file is ~8-25MB; the big repo/ and wheels/ can keep
   coming from pilkwang's dataset, so we do NOT need to mirror the whole artifact).
3. In the kernel: attach our dataset, copy our .pth over the materialized weights path AFTER
   materialize_inference_repo(), and patch the two SHA constants to our value.
4. Push, wait COMPLETE, submit with -k <kernel> -f submission.csv -v <version>.

---

## DETECTOR TRAINING ON THE V100 - RUNNING 2026-09-07

RUN: `bash ~/biohub/box_train_detector.sh loc 40 0` (pid 536767)
CONFIG: 199 movies (auto-split 180 train / 19 val), downsample **1,2,2** (2x finer in Y/X than the
public 1,4,4), unet-layers 32,64,128, **batch-size 3**, det-neg-weight 0.01 (default), workers 20,
--single-gpu. Log: ~/biohub/runs/train_loc.log
RATIONALE: the edge autopsy proved the linker is 99.56% accurate wherever detection lands within
2um, and a residual-conditioned oracle showed moving every GT cell into the <=2um band is worth
**+0.0804 with the linker unchanged**. Recall is NOT the lever (0.980->0.955 moved the <=2um band
by 0.2% and LOWERED adjEJ), so this run targets LOCALIZATION PRECISION via spatial resolution.
THROUGHPUT: ~2.25 s/it, 5629 iters/epoch => ~3.5 h/epoch. GPU 13.9GB/16GB, 93-100% util.
40 epochs is an UPPER BOUND: the script saves a checkpoint every time val score (acc*recall)
improves (train_unet_transformer.py:1197), and our own prior finding is that this detector
overfits past ~epoch 10. Stop it whenever val plateaus; the best checkpoint is preserved.

### SIX BLOCKERS THAT HAD TO BE FIXED (a fresh box will hit ALL of these)
1. MISSING DEPS: `polars` and `tracksdata` are not installed by default; the trainer dies at
   import, so `--help` prints NOTHING and every argument looks invalid. Install them.
2. **DO NOT RUN `pip install -e .`** in kaggle-cell-tracking-competition. It pulls
   torch 2.14 + nvidia_cudnn_cu13 (CUDA 13), which DROPPED Volta/sm_70 and silently destroys
   V100 support. Install with `--constraint` pinning `torch==2.6.0+cu124` (~/biohub/constraints.txt).
3. CRLF: scp'ing a shell script from Windows gives `set -euo pipefail
` -> "invalid option name".
   Fix with `sed -i 's/
$//'`.
4. UPSTREAM BUG in scripts/augmentations.py `flip_augment`: `coords[masks, dim]` raises
   IndexError (mask [2,33] vs tensor [2,3]) on some windows. Worked around by setting
   `DEFAULT_AUGMENTATIONS = [brightness_augment]` (line 113). Original file backed up as
   scripts/train_unet_transformer.py.bak.
5. V100 = sm_70 CANNOT use flash / mem-efficient SDP -> "CUDA error: invalid configuration
   argument" inside scaled_dot_product_attention. Patched the script to force the math backend
   (enable_flash_sdp(False) / enable_mem_efficient_sdp(False) / enable_math_sdp(True)).
   Consequence: attention is slower AND uses more memory (materialises the full matrix).
6. OOM: batch 4 at downsample 1,2,2 needs 14.83 of 15.77 GiB. batch 3 +
   `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` fits at ~13.9GB.

### NOT DONE (known remaining speedup)
The trainer has NO autocast/GradScaler - it is pure fp32. The V100 has fp16 tensor cores, so AMP
could roughly halve the epoch time, but it means wrapping a custom edge+detection loss and the
attention block, with NaN risk. Not attempted while a working run was in progress.

### HOW TO VALIDATE THE TRAINED DETECTOR (important)
Do NOT judge it by local adjEJ - that harness has failed to transfer 4 times. Judge it by the
LOCALIZATION RESIDUAL DISTRIBUTION (fraction of GT nodes whose nearest predicted node is within
2um), which is a direct, high-signal statistic and is exactly what the +0.080 oracle was
conditioned on. Baseline to beat: 55% of GT nodes within 2um.

---

## *** LB RESULTS 2026-09-07: THE RELINK FAMILY IS DEAD. 4th CV->LB FAILURE. ***

| submission | local prediction | ACTUAL LB |
|---|---|---|
| relinkoff (BIOHUB_OUTPUT_MOTION_RELINK=0) | +0.0146 / +0.0182 / +0.0430 | **0.939** (-0.002) |
| relink (drop zero-prob motion-relink edges, postshort) | +0.0098 / +0.0108 / +0.0155 | **0.939** (-0.002) |
| det955val (DET_THRESHOLD 0.955) | "noise" | **0.941** (flat) - PREDICTED CORRECTLY |
| div941 / div941full | - | **0.941** = STILL BEST |

BOTH relink levers LOST on the LB despite the strongest local evidence we have ever produced:
both embryos up, bootstrap CIs excluding zero, replicated on THREE independent detection sets
(det0.980 / det0.955 / det0.965), and a clean mechanism (zero-prob relink edges had a 3.35:1
FP:TP ratio vs a 1.1:1 break-even). The filter was VERIFIED to fire on the real test data
(dropped=3367, spared_forks=31 over the 4 test datasets), so this was not a silent no-op.

### THE CALIBRATION RULE (now overwhelming, 4 failures)
1. prune stack: +0.0103 local -> +0.000 LB
2. learned edge model: +0.02-0.04 on ALL CV folds -> +0.000 LB
3. SAFE_DIV_MAX_UM=11: +0.012 (4mv) -> +0.0038 (8mv) -> -0.0017 (20mv), reversed sign
4. relink family: +0.010..+0.018 local, BOTH embryos, tight CIs -> **-0.002 LB**
=> The 20-movie local harness can reliably say "THIS IS NOISE" (it called det955 correctly).
   It CANNOT say "this is a gain". Do NOT spend a slot on a local-only positive again.
WHY: the validator uses TRAIN embryos (44b6/6bba) while the test set is DIFFERENT embryos, and
GT annotates only 1.06% of nodes - local adjEJ is a ~1% subsample of a different biological
sample, which is enough to invert a +-0.01 effect.

### CONSEQUENCE FOR THE DETECTOR PLAN
The edge autopsy's +0.080 localization ceiling is still the only real headroom, BUT a trained
detector CANNOT be validated on this local harness either. Any detector run must be judged by
the LB directly, or by a validation protocol that does not rely on these 20 train-embryo movies.
Budget slots accordingly.

### STATUS: best = 0.941 (div941 config is the reference). Data pull COMPLETE (199/199 movies,
~80GB on the box). All cheap axes closed: division gates, orphan-stealing, division recall,
node-count pruning, edge-prob floors (32-rule battery), relink family.

---

## EDGE-TERM AUTOPSY 2026-09-06 (supersedes the division work as the active line)

Scorer re-confirmed from source: adjEJ = max(0, J*(1 - 0.1*(T_pred-T_true)/T_true)), T_true =
GT geff `estimated_number_of_nodes`. NO upper cap (GT-as-pred gives adjEJ 1.097-1.100).
20 movies, 13014 GT nodes, 12587 GT edges, 29 GT divisions.

### 1. NODE-COUNT PENALTY IS A BONUS - close that line
T_pred/T_true = 0.753. We predict 375,182 vs T_true 498,172 => we are 25% UNDER N_est and the
adjustment term CREDITS us +0.0084 mean adjEJ. hengck23's "detect just enough nodes (<= N_est)"
claim is FALSIFIED for us. Pruning toward N_est LOSES money (to T_true -0.0036, to 0.9*T_true
-0.0131). [CORRECTED 09-17: the "+0.024 oracle cap" was the 20% dose of a capped sweep; exact oracles are
+0.130 (keep matched nodes) / +0.072 (keep GT-touching tracks), but NO test-time prior gets near them - see the
09-17 ANNOTATION-PRIOR section at the top and ANNOT_PRIOR_REPORT.md.] NOT a lever.
~100% of the ~0.101 edge gap is the JACCARD.

### 2. "MOST LOSS IS LINKING" WAS A MISREADING OF THE 7um GATE
Raw split at 7um looks like DETECTION 0.0232 / LINKING 0.0710 (25/75), but conditioned on
match residual the linker is nearly perfect:
  residual <=1um -> 99.79% accurate | <=2um -> 99.56% | <=3um -> 99.12% | <=7um -> 97.25%
Missed reachable edges have worst-endpoint residual median 4.05um vs 1.85um for TPs. The linker
picks the NEAREST predicted node 99.3-100% of the time; when it misses, it moves 1.85um (normal
motion) while the metric's "correct" partner sits 9.07um away (within 3um only 2.8% of the time).
FP edges carry mean edge_prob 0.477 vs 0.900 for TPs => not confidently wrong, just no good
candidate. 7um is 3.4x typical one-frame displacement (2.09um) and ~0.8x cell spacing (9.1um).

### 3. THE REAL CEILING: DETECTOR LOCALIZATION, NOT RECALL
RESIDUAL-CONDITIONED ORACLE (measured): if the detector localized every GT cell to <=2um - which
it already achieves for 55% of GT nodes - the CURRENT UNCHANGED LINKER gives J 0.9795,
mean adjEJ 0.9793, delta +0.0804 [+0.0575,+0.1045], BOTH embryos up. That is 98% of the
perfect-linker ceiling with ZERO linker change.
=> If the V100 is used, train the DETECTOR for LOCALIZATION PRECISION. Not recall, not the linker.
Threshold tuning is exhausted: 0.980->0.955 adds 12% more nodes but moves the <=2um band only
0.5456->0.5480 and LOWERS adjEJ 0.8989->0.8975. It is the detector MODEL, not its threshold.

### 4. edge_J ~= node_recall^2 IS FALSIFIED for the current pipeline
mean edge_J 0.8905 vs node_recall^2 0.9544 vs node_recall 0.9766. edge_J is 0.064 BELOW
node_recall^2. Node precision vs GT is meaningless (GT samples only 0.17-15.4% of cells).

### 5. ZERO-PROB RELINK LEVER -- VALIDATED IN-PIPELINE 2026-09-07 (sandbox/relink/)
The repair wrapper fabricates edges the edge model NEVER scored: `motion_relinked:1` with
`edge_prob:0.0`. VERIFIED: raw geffs have min edge_prob 0.480 (= DUAL_SEED_EDGE_THRESHOLD) and
ZERO edges at/below 0. Final-graph relinked probs live in {0.0} u [0.48, 1.0] -- nothing in
between -- so any probability floor below 0.48 is EXACTLY the same filter, and 0.60 is
destructive (-0.013 / -0.018). The floor variant is a dead end; exactly-zero is the rule.

IMPLEMENTATION: `drop_zeroprob_relink_edges()` in sandbox/div20/repair_prod.py, env-gated,
DEFAULT OFF. `BIOHUB_DROP_ZEROPROB_RELINK=1`, `_STAGE=postrelink|postdiv|postshort`,
`_SPARE_FORKS=1` (skip edges whose source has out-degree>=2), `_EPS`.
Applied by sandbox/relink/patch_repair_prod.py + patch2_postshort.py (both idempotent;
`patch_repair_prod.py --revert` restores sandbox/relink/repair_prod_baseline.py).
REGRESSION PROVED: flag OFF gives a graph hash identical to the frozen pre-patch module on
20/20 + 20/20 + 4/4 movies and reproduces 0.9174782980807328 / 8-14-21 / 569 forks exactly.

*** PLACEMENT IS THE WHOLE RESULT: the drop must be the LAST edge-level operation. ***
20-movie combined, paired movie bootstrap 20k, base det0.980 = 0.9175 / det0.955 = 0.9179:
  stage        what re-runs after the drop                 d0.980    d0.955   both embryos
  postrelink   single-parent, gap-close, gap2, epilogue   -0.0106   -0.0064   DOWN/DOWN
  postdiv      prune-isolated, SHORT-TRACK, linefit       +0.0049   +0.0065   FAIL (44b6 -)
  postshort    prune-isolated, linefit                    +0.0098   +0.0108   PASS
    det0.980 postshort: CI [+0.0026,+0.0182] P>0 .998  44b6 +0.0058 / 6bba +0.0139
    det0.955 postshort: CI [+0.0042,+0.0186] P>0 1.00  44b6 +0.0074 / 6bba +0.0141
    det0.965 (n=4, EXACT prod config): 0.9096 -> 0.9251 (+0.0155), both embryos up
WHY postdiv loses half the gain (measured, sandbox/relink/diag.py stages): dropping a zero-prob
edge mid-track splits the track, and the short-track filter (MIN_TRACK_LEN=6) then deletes the
fragments -- 13,108 -> 25,117 nodes removed, taking 75 extra TRUE-POSITIVE edges with them
(edge TP 11900 post-hoc vs 11825 in-pipeline). Run the drop AFTER that filter and the post-hoc
+0.0097 is reproduced exactly. Division sparing is mandatory: without it divJ 0.186 -> 0.100.

*** BIGGER, AND IT IS AN EXISTING ENV KNOB: `BIOHUB_OUTPUT_MOTION_RELINK=0` ***
No existing knob can select the zero-prob subset (the gates are distance-based and 41% of
zero-prob relinks are under 4um, where they are only 0.3-3.3% of the population; TIGHT/RELAXED/
LEARNED_BONUS sweeps are all <= +0.0016 and fail the both-embryo gate). But turning the whole
LAP OFF beats the surgical drop on every set:
  det0.980  0.9175 -> 0.9321  (+0.0146)  CI [-0.0015,+0.0325] P>0 .962  44b6 +0.0062 / 6bba +0.0235
  det0.955  0.9179 -> 0.9361  (+0.0182)  CI [+0.0038,+0.0338] P>0 .993  44b6 +0.0167 / 6bba +0.0216
  det0.965  0.9096 -> 0.9526  (+0.0430, n=4, +0.0230 on adjEJ alone; the rest is 1 division)
It is a PARETO move, not a trade: edge TP 11957 -> 12021 AND edge FP 614 -> 445 (det0.980).
The raw learned edges plus single-parent repair are simply better than the Hungarian relink.
RISKS before shipping: (a) bootstrap SD 0.0087 vs 0.0040 for the surgical drop -- the gain leans
on 44b6_267148e4 (+0.052) and 44b6_587a1e22 (+0.067) and 44b6_706092f0 goes -0.050;
(b) forks 569 -> 657 (det0.980) / 592 -> 700, and the scorer caps out-degree at 2, so extra
forks are invisible locally but could bite on the hidden test; (c) every rival kernel in the
pilkwang stack ships relink ON, so this is a deliberate divergence.
The two levers are MUTUALLY EXCLUSIVE (relink off => no relinked edges to drop).
DECISION: `BIOHUB_OUTPUT_MOTION_RELINK=0` needs NO code patch in the real kernel, only an env
change. The surgical drop needs a ~25-line patch and gives half the gain with half the variance.
Scripts: sandbox/relink/{harness,variants,regress,boot,table,permovie,diag}.py,
results_det0.{980,955,965}.json.

### 6. EDGE-FLOOR / DEGREE-AWARE FILTERS ON TOP OF THE RELINK DROP -- CLEAN NEGATIVE, LINE CLOSED
2026-09-07, sandbox/edgefloor/. Question: after the zero-prob relink drop, is there a further
structurally-identifiable subset of BAD edges? Answer: NO, and the reason is structural, not a
tuning failure. 40 in-pipeline configs x (det0.980 20mv, det0.955 20mv, det0.965 4mv) + a 32-rule
post-hoc scope battery + an 11-rule LAP-override probe. NOTHING beat the base on ANY set.

BASE REPRODUCED EXACTLY (RB = E_postshort_spare): 0.9273 / 0.9287 / 0.9251, per-embryo
44b6 0.9557 / 6bba 0.9058, 44b6 0.9524 / 6bba 0.9112, 44b6 0.8918 / 6bba 0.9518.

*** THE RAW GEFF IS ALREADY A STRICT 1-1 MATCHING WITH A HARD 0.48 CUT (sandbox/edgefloor/rawcheck.py) ***
Measured on ALL 44 movie-instances of all three thresholds: max out-degree = max in-degree = 1,
min edge_prob = 0.480 (0.480025 / 0.480004 / 0.480047), ZERO edges below 0.48. Three consequences,
each of which kills one of the proposed levers outright:
  (a) a GLOBAL floor F <= 0.48 is a MATHEMATICAL no-op. Confirmed in-pipeline by GRAPH HASH:
      F in {0.05,0.10,0.15,0.20,0.30,0.40,0.45,0.48} is bit-identical to RB on 20/20, 20/20, 4/4.
      There is no "peak then collapse" curve -- it is flat, then a cliff, and the cliff starts
      the instant the floor enters the model's own support.
  (b) "contested target" (target in-degree >= 2) is an EMPTY SCOPE. The linker emits one parent
      per node and OUTPUT_SINGLE_PARENT_REPAIR re-enforces it. F*_ctarget drops 0 edges at EVERY
      floor up to 0.70 and is hash-identical to RB. The two largest FP classes from the edge
      autopsy (target-matched/source-unmatched 50.5%, wrong-node 39.9%) are NOT addressable here:
      the contested-target information was destroyed upstream.
  (c) the motion-relink LAP has NO alternative SCORED candidate to override, so every "wrong node"
      link it makes is a pair the model never scored (edge_prob == 0.0) -- exactly the population
      the validated relink drop already removes. LAP src_override count = 0 (sandbox/edgefloor/override.py).
      THE ZERO-PROB DROP DID NOT FIND *A* LEVER, IT CONSUMED THE ENTIRE SUB-THRESHOLD POPULATION.

FLOOR CURVE (dCombined vs RB; det0.980 / det0.955 / det0.965):
  F<=0.48  +0.0000 / +0.0000 / +0.0000   (bit-identical, 0 edges dropped)
  F=0.49   -0.0013 / -0.0016 / -0.0006   (972 / 1044 / 218 edges)
  F=0.50   -0.0015 / -0.0021 / -0.0023
  F=0.55   -0.0091 / -0.0132 / -0.0037
  F=0.60   -0.0225 / -0.0283 / -0.0212
  F=0.70   -0.0570 / -0.0596 / -0.0680
Bootstrap 20k on the least-bad: F0.49 CI [-0.0024,-0.0004] / [-0.0026,-0.0008]; F0.50
[-0.0024,-0.0005] / [-0.0035,-0.0006]. Both FAIL both-embryos-up on both sets.

DEGREE-AWARE VARIANTS (best dComb over all floors, det0.980 / det0.955):
  ctarget (target in-deg>=2)        +0.0000 / +0.0000  EMPTY SCOPE, hash-identical, not a result
  weakfork (drop weaker fork child) -0.0024 / -0.0018  and divJ does NOT stay put:
       0.1860->0.1628, 0.2045->0.1860, and on det0.965 0.2000->0.0000 (forks 96->91).
       Confirms SPARE_FORKS in the base is load-bearing, not decoration.
  long (low-prob AND top-decile length)  best -0.0008 / -0.0009 (F0.55_long99) -- CI
       [-0.0018,+0.0000] / [-0.0020,-0.0000], fails both-embryos on both sets.
  ctarget_or_long == long exactly (ctarget contributes nothing).

POST-HOC SCOPE BATTERY (sandbox/edgefloor/scopes.py, 32 rules, break-even 1/J = 1.09 FPs per TP):
validated against the in-pipeline result -- rule `prob<0.40` reproduces E_postshort_all's
dComb -0.0084 to 4 dp. NOT ONE rule clears break-even: distance top-1/5/10%, motion-residual
top-1/5/10%, relaxed-relink pass, mid-movie track heads, mid-movie track tails, components
<=8/<=12 nodes, and every prob x geometry cross -- all FP/TP between 0.06 and 0.79 versus the
1.09 needed. Post-drop mean edge_prob is 0.904 for TPs and 0.749 for FPs, and every band above
0.48 is TP-rich. `tail & prob<0.70` shows +0.0010 on det0.955 but -0.0015 on 44b6 of det0.980:
noise from the node-count factor, not FP removal. Do not chase it.

CODE: sandbox/edgefloor/{patch_floor,variants,boot,table,autopsy,scopes,override,rawcheck}.py,
results_det0.{980,955,965}.json. patch_floor.py adds `drop_lowprob_edges()` to
sandbox/div20/repair_prod.py, env-gated `BIOHUB_DROP_LOWPROB` (+_FLOOR/_MODE/_SPARE_FORKS/
_LEN_PCT/_LEN_UM), DEFAULT OFF, idempotent, at the same postshort position as the relink drop.
REGRESSION RE-PROVED after patching: flag OFF is hash-identical to the frozen pre-patch module on
20/20 + 20/20 and reproduces 0.9174782980807328 / 0.9179237283944859 exactly.
VERDICT: do NOT spend a submission slot on any edge-floor or degree-aware filter. The edge-prob
axis is exhausted. Anything further has to come from the DETECTOR (see section 3) or from the
relink-off decision in section 5.

### DET_THRESHOLD 0.955 = NOISE, DO NOT SHIP
20-movie like-for-like: combined +0.0004, CI [-0.0065,+0.0079], P(d>0)=0.519, FAILS both-embryo
test (44b6 -0.0050 / 6bba +0.0052), adjEJ worse on 12/20 movies. Of 9 missing 2nd daughters only
5 were ever a detector problem; the other 4 are ASSIGNMENT COLLISIONS a perfect detector cannot
fix. The 4 remaining detector misses are BLIND SPOTS: nearest-neighbour distance bit-identical at
0.955 vs 0.980 (8.79/8.12/7.62/10.90um) - the threshold moved them 0.00um. Division-recall
oracle ceiling <= +0.009. DIVISION RECOVERY IS CLOSED FROM BOTH SIDES.

---

## CURRENT STATE 2026-09-06 (newest first; supersedes every block below)

**LB 0.941, rank ~103 / 1042.** Best subs: `biohub-v-div941` and `biohub-v-div941full`
(both 0.941, submitted 2026-09-05). Previous best was 0.935.

### How we got to 0.941
The 0.940-0.941 public "shelf" is ONE byte-identical code lineage; only env values differ.
The winning recipe over our old 0.935 frontier is division GEOMETRY:
`SAFE_DIV_MAX_UM=9.0, SAFE_DIV_SISTER_MAX_UM=14.0, SAFE_DIV_SISTER_SYMMETRY_TAU=0.6,
ILP_DIVISION_WEIGHT=1.2, DIVERGE_UM=2.25, DET_THRESHOLD=0.965` + short-track-rescue.
Verified NEUTRAL (both scored exactly 0.941): `DIVERGE_UM=4.0`, `SECONDARY_LINK_MODE=adaptive`.

### THE RESCORE THESIS IS DEAD — do not re-inherit it
The division-jaccard exploit was patched 2026-07-17/18 (royerlab PR#2). The rescore ALREADY
happened, ~7 weeks before our Aug/Sep subs. The live board is fully post-rescore. safe_div
OFF scores 0.907 (near-last); safe_div forks are LEGITIMATE, not an exploit.

### EXPLOIT — recognise and AVOID (DQ risk)
`augment_dataset()`: appends a hub node at t=-1000, (z,y,x)=(-10000,-10000,-10000) wired into
roots of the top ~3000 weakly-connected components, plus FORKS=20 fake divider nodes.
Signature: `augment_dataset`, `hub_id`, `FORKS =`, `MAX_COMPONENTS =`, coord -10000, negative t.
Present in `amanatar/improved-metric-hack-last-call` and `anvithpothula/biohub-0-95`.
NOTE: `rx.weakly_connected_components` alone is NOT a tell (our own kernel uses it legitimately).
**Our kernels are clean.**

### KNOB TUNING IS CLOSED (rigorous negative, 20 movies / 29 divisions, both embryos)
Harness `sandbox/div20/` validated against the kernel's own numbers (adjEJ 0.9365 vs 0.9365,
div TP/FP/FN 1/0/4 exact). Baseline: adjEJ 0.89887, micro divJ 0.18605, combined 0.91748.
- `SAFE_DIV_MAX_UM` is INERT at production caps: 9->13 leaves TP/FP/FN at 8/14/21 exactly.
- The old "MAX_UM=11 = +0.011" was an artifact of tuning the WRONG module (sandbox/repair.py is
  the old cloud948 wrapper, no tau gate). On 20 movies it REVERSES to -0.0017.
  (4 movies +0.012 -> 8 movies +0.0038 -> 20 movies -0.0017.)
- tau and diverge are at a local optimum in BOTH directions.
- ORPHAN RELAXATION (steal a claimed 2nd daughter) implemented + FALSIFIED: only 2 of 29
  divisions are legitimately stealable; every variant lost monotonically and TP never moved off 8.
- Only survivor `caps x0.5` (+0.0009) has bootstrap CI [-0.0005,+0.0040] and is +0.0000 on the
  4 exact-config movies. NOT worth a slot.

### LOCALISATION IS NOT THE PROBLEM (oracle-proven)
Snapping ALL 2235 matched nodes onto exact GT positions changes divJ by EXACTLY 0.0000.
Our division sites are already well localised (median 2.40um, 17% >3um vs k3v1npark's 39%).
ORACLE-LINK (adding the true 2nd-daughter edge) = +0.0249. So it is a LINKING/DETECTION problem.

### WHERE THE REMAINING HEADROOM IS
- 31% of GT divisions have NO predicted node for the second daughter at all -> DETECTION RECALL.
- Our raw linker emits out-degree <=1 EVERYWHERE (pre-repair divJ = 0.000); 100% of our
  divisions are synthesised by `add_safe_divisions_postlink`.
- divJ ~= h/(1 + M_spurious/G) ~= 0.60h, so score gain ~= 0.060 * delta_recall.
- Division FPs are ~99% discounted (GT annotates only 1.06% of nodes).
=> Next real lever is a better DETECTOR (or a learned fork classifier), not geometry.

### LOCAL CV DOES NOT TRANSFER — hard-won rule
prune stack +0.0103 local -> +0.000 LB. Edge model +0.02-0.04 on all folds -> +0.000 LB.
MAX_UM=11 +0.012 -> reversed sign with more data. Trust LB-isolated levers only.

### INFRASTRUCTURE NOTES
- The V100 box CANNOT authenticate to Kaggle: valid token, correct client (2.2.4), clean TLS,
  but the university egress (14.139.202.226) returns {"code":401,"Unauthenticated"}.
  The LAPTOP must be the conduit for all Kaggle data.
- Kaggle CPU kernels are FREE (no GPU quota) - use them to tar competition data into per-movie
  archives, then download+scp. Single huge files fail (IncompleteRead); ~450MB per-movie tars work.
- torch on the V100 must be the CUDA 12 build (`--index-url .../whl/cu124`). Default torch 2.14
  pulls CUDA 13, which DROPPED Volta/sm_70 support and will not run on a V100.
- `sandbox/score.py` has a bug: divJ is always 0.0 (`per_sample` never emits `division_jaccard`).
  Every `combined` it ever logged equals adjEJ. Corrected scorer: `sandbox/divresearch/score_full.py`.
- Config drift guard: changing a guarded knob requires patching BOTH `os.environ[...]` AND the
  `_EXPECTED_NUMERIC` dict in lockstep, or the kernel raises "Configuration drift detected".

### IN FLIGHT
- `biohub-v-det955val`: div941 + DET_THRESHOLD 0.955 + VALIDATOR_N_PER_TYPE=10
  (first divJ measurement on the EXACT production config, 20 movies). Auto-submits.
- Full train-set pull to the box: 129/199 movies, 55GB (batched via free CPU kernels).
- Detector training staged: `scratch_kernels/box_train_detector.sh` (recall|negw|fine|base),
  targets det recall at division sites. NOT yet launched - ARC job holds the GPU.


---

# HANDOFF — Biohub Cell Tracking (Kaggle)

Newest block first (2026-08-30). Read the CURRENT STATE — 2026-08-30 block below;
every dated block under it is historical and already superseded. Full lever
history lives in `AUTONOMOUS_LOG.md`, `RECALL_RESEARCH.md`, and `INTEL.md`.

---

## CURRENT STATE — 2026-08-30  (LATEST — single source of truth; supersedes ALL blocks below)

**ACCOUNT BEST = 0.921** (`55751003` "sim4" = fill + max_link8 + appearance linker
sim_w4), BANKED. Deadline **2026-09-29** (~30 days out). Field: leaders 0.962
(Ayati = z7777), prize zone (top ~7) is **>=0.95**. We are mid-pack.

**2026-08-30 LB RESULTS (all 4 in):** sim4iso 55880067 = **0.921**, sim4post
55880097 = **0.921**, sim4gap 55882151 = **0.921**, sim4mc 55882156 = **0.922**
— post-proc cleanup and MC do NOT hurt; all within LB noise of sim4, all are
scored 09-29 candidates (tied-cluster). EVENING: user authorized ONE more
submission -> **55897352 sim4mcref** (sim4mc + grafael refine swap,
positions-only) PENDING. USER DIRECTIVE otherwise stands: NO MORE SUBMISSIONS.
refine_cv kernel (paired 5-arm refine test, no submission) pushed v2 after a
DIV_SISTER_UM=None config bug (v1 errored) — running as
eeshsaxena/biohub-refine-variant-cv.

**>>> 08-30 INTEL SHIFT: public frontier 0.920 -> 0.937.** Public notebooks
`notoverkil/biohub-base-0937` (0.937) etc. all run the SAME pilkwang stack:
temporal-UNet (2-frame window, det thr 0.965) + UNetNodeTransformer LEARNED
edge probabilities + tracksdata ILP (native divisions) + heavy repair wrapper.
Full mechanism + adoption paths in INTEL.md (08-30 block). Structural autopsy
vs our 0.919: they emit 0.925x our nodes (PRECISION win), zero edges >7.3um,
and we emit 1.6x their nodes on 44b6_0b24845f (anomalous over-detection on
ONE movie — density-adaptive detection gate is the new untested own-work lever).

**>>> 08-30 SIMULATION VERDICTS** (`kaggle/exp_sim_levers.py`, 24 local 44b6 GT
movies, verified scorer incl. node penalty — all local, ZERO submissions):
1. **Density-gate value envelope = LARGE**: 50% FP contamination costs -0.145
   adjJ (0.921->0.776); removing 80% of FPs at 0 collateral recovers +0.136, at
   2% collateral still +0.104. => precise per-movie FP/density gate is the
   highest-value own-work lever left; gate PRECISION is the open question.
2. **ILP vs bare Hungarian, de-confounded**: +0.018 raw but +0.0034 of it is
   just the wider 10um candidate gate (hungarian-g10 same-8 = 0.9335 vs ILP-flat
   0.9392 vs hungarian 0.9301); residual global-solve gain +0.0057. ZERO native
   divisions recovered in sim even with sharp probs -> division coupling is NOT
   the driver. Modest, not decisive; sim4's real linker (velocity+appearance,
   gate 8) is stronger than the harness's bare Hungarian anyway.
3. **Motion comp**: helps only at drift >= ~1-2um/frame (2um/frame: hungarian
   0.9059 -> mc-est 0.9143, oracle 0.9276); image-free median-NN drift estimator
   ~= oracle at high drift. Real drift magnitude unknown; sim4mc LB (pending)
   is a noisy read, not evidence.
4. **Edge-clamp 7.5um: NO-OP** on bare harness (linker gates at 7um; the 11.8um
   tail comes from linefit/gap-fill post-proc — testable only on real output;
   likely tiny).

**>>> 08-30 EVENING — frontier 0.937 -> 0.940 + SIM ROUND 2** (full detail in
INTEL.md evening block; sims in `kaggle/exp_sim2.py`, zero submissions):
- 0.940 = 0.937 stack + centroid refinement + harmonic bidirectional fusion
  w=0.30 + velocity EMA + secondary-det-weight 0.475. Their LB telemetry
  confirms division weight is LB-invisible (all values score 0.915).
- ~~**EXP4: jitter 1.0->0.4px = +0.014 adjJ, port refine_centroids = #1 lever.**~~ **REFUTED 2026-09-18, see the
  top section item 9.** The units are MICRONS not px (`det_pos + N(0,jit)/SCALE`, SCALE in um/voxel; the print label
  is wrong), it is a SIMULATION that assumed refine_centroids halves the error rather than a measurement of it, the
  curve saturates at 0.7 um (adjJ 0.9372 at 0.7 vs 0.9377 at 0.4 vs 0.9393 at 0.0), and an intensity-weighted centroid
  is a different lever that measured WORSE than doing nothing in the 09-18 estimator sweep.
- EXP5 mutual-NN gating: noise in realistic regime, +0.007/+0.029 only under
  dense FP. EXP6: nodes/frame CANNOT flag FP-dense movies (AUC 0.625 — it
  measures true embryo density). Density-gate design must use within-movie
  observables instead.

**09-29 FINAL SELECTION (2 slots, both banked, do not lose these):**
1. `55751003` 0.921 — sim4 (own-velocity + appearance linker)
2. `55802000` 0.921 — flow-k8 (collective-flow linker)
Two TIED top-cluster scores from STRUCTURALLY DIFFERENT linking mechanisms =
free diversification against a private rerank. Keep unless something beats BOTH
on paired CV (below).

### >>> THE #1 RULE — the public LB cannot rank our configs (08-28, proven) <<<
GT is ~0.737% sparse -> a ~4-movie scored test ~= 836 GT edges -> **1-sigma on
edge-J = +-0.0104**. Our ENTIRE submitted spread is 0.918-0.921 = 0.003 = **~0.3
sigma = pure noise.** Every "LB verdict" recorded between 0.918-0.921 (prune dead,
flow worse, accel neutral, edge-model hurts) is a NOISE reading, not evidence.
**PAIRED CV** (identical movies + cached detections, only the config differs)
cancels variance -> noise floor **+-0.0007, ~7x the LB's power.** => Judge every
candidate on **pooled adjJ+0.1divJ over BOTH embryos on the 10 local train movies**,
never on the LB. (Leaders at 0.95+ ARE genuinely better: 0.03 = ~3 sigma. Our own
0.918-vs-0.921 ordering is not.) Full derivation: LB NOISE ANALYSIS block below.

### NEW RESEARCH (2026-08-30) — files in `Downloads/`: `RESEARCH.md`, `NEXT_SESSION.md`, `biohub_complete_package.zip`
A fresh 60-query pass diagnoses the gap as **structural, not parametric**: our
stack (classical 3D-maxima detection + greedy frame-pair Hungarian 1:1 + post-hoc
divisions) is the TrackMate-class public baseline (Tobi-joshua's open pipeline is
identical). The 0.94+ pack runs **Ultrack** — the ORGANIZERS' own method (Royer
Lab, Nature Methods 2025): multi-hypothesis detection + GLOBAL ILP/LAP (native
1->2) + multi-frame gap close + frame registration.

**THE ONE GENUINELY-UNTESTED LEVER = LapTrack** (`pip install laptrack`; pure
Python, CPU). 2-stage LAP: Stage 1 frame-to-frame (≈ our Hungarian), Stage 2
**GLOBAL gap-closing + native splitting**. We never tested a trajectory-level
linker — the 08-27 "min-cost-flow decomposes into per-frame Hungarians" proof only
covers frame-pair-LOCAL costs; Stage-2 gap-closing is trajectory-level and does
NOT decompose. Ready-to-port integration: `biohub_complete_package/laptrack_integration.py`
(detections->df, custom cost, drift estimate, convert-back, local-GT tuner).

**HONEST RECONCILIATION — the research over-claims divisions.** RESEARCH.md's
headline ("Hungarian forfeits divisions, div_J 0.13, lose 0.012-0.017") is
CONTRADICTED by our measured data: our **div_J = 0.26** (contribution +0.026),
already ABOVE the public frontier (~0.2), and loosening divisions HURTS (LB 0.903).
So LapTrack's DIVISION edge is ~zero for us; its only plausible upside is the
GLOBAL GAP-CLOSING / trajectory linking. Treat +0.007-0.014 as an optimistic
ceiling — a real but probably smaller swing. It is nonetheless the single best
untested idea left.

### LAPTRACK — TESTED 2026-08-30 (local paired A/B), MARGINAL-TO-NEGATIVE
`kaggle/exp_laptrack_ab.py` (laptrack 0.17.0, 24 local 44b6 movies, GT positions as
detections, verified scorer). Result by regime (edgeJ / precision):
- Clean/low-noise, recall-limited (drop .02-.06, no FP): laptrack beats bare
  two-pass Hungarian by only **+0.007-0.009**; laptrack+synth looks huge (+0.04-0.10)
  but that gain IS midpoint gap-fill synthesis our `sim4`/`fill1` ALREADY ships.
- **REALISTIC regime (drop .02 + jitter 1um + 5% FP): laptrack LOSES** — edgeJ
  0.9132 vs ours **0.9265**, precision **0.96 vs 0.99**. LapTrack's global LAP links
  MORE permissively => higher recall, LOWER precision. But PRECISION (the 2% steals)
  is the exact gap; LapTrack attacks the wrong axis and is less precise everywhere.
- Theoretical clincher: tightening LapTrack to recover precision collapses its
  Stage-1 to a frame-pair LAP = our Hungarian; its only differentiators (gap-close,
  split) are what cost the precision. Same result as the 08-27 decomposition proof.
CAVEATS: 44b6-only (6bba needs Kaggle), synthetic error model, baseline was BARE
Hungarian (real sim4 is stronger => LapTrack vs sim4 is worse still), params untuned.
=> **Do NOT spend the 12h build + a slot on LapTrack.** It does not address the
precision gap and its recall gain duplicates our synth. The RESEARCH.md +0.007-0.014
estimate rests on a wrong premise (div_J 0.13; ours is 0.26) and a bare baseline.
LapTrack now joins the exhausted list. 0.921 (sim4) remains the ceiling.

### CONCRETE NEXT ACTION (in order; no LB slot until step 2 clears)
1. **Ship LapTrack offline + confirm import.** Internet is OFF at submission ->
   `pip install` fails. Package laptrack + deps as a wheels dataset (mirror
   `biohub-zarr-wheels`) and confirm it imports on the T4 base image (10-min kernel).
2. **PAIRED-CV A/B (no GPU, no slot):** sim4 linker vs LapTrack on the 10 local
   `data/train/*.geff` movies, pooled adjJ+0.1divJ, BOTH embryos; tune the 4
   cutoffs (`laptrack_integration.py: tune_laptrack_parameters`). SHIP ONLY IF it
   beats sim4 on BOTH embryos by > the +-0.0007 CV floor.
3. If it wins -> build a submit kernel, verify the 12h-cap fit + the integrity gate
   (4/4 datasets, every edge t->t+1), submit. Keep sim4 0.921 as the untouched anchor.
4. Cheap post-proc levers (`NEW_LEVERS_CODE.txt`: isolated-node removal, short-orphan
   prune, multi-frame gap close, motion comp) — quick paired-CV tests, LOW prior
   (short_filter / gap-cap / prune already measured SATURATED or within-noise, see
   dead-ends). Ship only a clear both-embryo CV winner.

### EXHAUSTED — do NOT re-derive (all with CV+LB evidence in the blocks below)
learned edge/prune models (2-embryo overfit; LB dose-response INVERSE to CV);
flow/flowprior (CV gain anti-correlates with LB); abstention (LB-dead); t+2 accel
& joint/global-flow (decompose; both-embryo-neutral); divisions (0.26 near-optimal;
relax hurts); DeepCenter veto/mean (negative); detection thr/NMS/gap-cap/union
(saturated at thr 0.15, recall 0.978 ceiling); own detector training (680 GPU-h,
infeasible); Zebrahub external data (RTX-4050 A/B: learned edge <= geometry on a
novel embryo). The classical+Hungarian ceiling is 0.921; LapTrack is the ONE
structural swing that might reach ~0.925-0.935. The 0.95 prize zone is out of reach
with accessible own-work.

---

## CURRENT STATE — 2026-08-28  (historical; superseded by the 08-30 block above)

### >>> READ FIRST: THE LB CANNOT MEASURE OUR CONFIGS (08-28 statistical finding) <<<
GT is ~0.737% sparse -> **median 209 consecutive GT edges per movie** (25 local movies; the 2
visible test movies have only ~50 each). A ~4-movie scored test = ~836 GT edges -> **1-sigma on
J = +-0.0104**. Our ENTIRE LB spread across every config ever submitted is 0.918..0.921 = 0.003
= **~0.3 sigma**. The public LB is statistically INCAPABLE of ranking our submissions.
**THIS INVERTS THE OLD RULE "CV lies, trust only LB".** CV comparisons are PAIRED (same movies,
same cached detections, only the config differs) so variance cancels -> measured noise floor
**+-0.0007**; an LB difference carries ~+-0.005. **CV has ~7x the power.** Every "LB verdict"
recorded between 0.918-0.921 (prune dead, flow worse, edge model hurts, accel neutral) is a NOISE
READING, not evidence. The leaders at 0.95+ ARE genuinely better (0.03 = ~3 sigma); our internal
ordering is not. Full derivation in the LB NOISE ANALYSIS section below.

### HIT-AND-TRIAL LADDER (08-29) — ALL 5 SUBMITTED, quota 0 left, all PENDING
GPU permitted for SUBMISSIONS ONLY (no more CV experiments). These are the CV-best prune doses
that had NEVER been scored (tau .60 @ gate10 was, = 0.918). Builder `build_pruned_submit.py`,
arm via env `BIO_ARM=prunE|prunF|prunG|prunH|prunI`. All arms share: accel base + sim_w4 +
learned-edge prune + re-route b2.0 + div_diverge 3.0 (division TIGHTENING = the LB-safe direction).

| ref | arm | config | CV vs control | edges emitted |
|---|---|---|---|---|
| `55862228` | prunE | tau .70 gate10 | **+0.0051 (CV peak)** | 122,794 |
| `55862229` | prunF | tau .50 gate10 | +0.0046 | 124,039 |
| `55862826` | prunG | tau .60 gate8 (SHIPPED gate) | +0.0049 | 122,980 |
| `55862827` | prunH | tau .40 gate10 | +0.0038 | 124,057 |
| `55863297` | prunI | tau .70 gate12 (WIDE, untested) | n/a | 122,766 |
(baseline emits ~124,120 edges. Edge count is MONOTONE in the dose -> the pruner behaves exactly
as configured, and the 5 arms form a clean DOSE-RESPONSE LADDER. When the scores land, that is
itself a direct empirical test of the noise analysis: if the LB responds to prune strength the
lever is real; if the 5 scores just scatter, it confirms the LB is measuring noise.)
All five passed the integrity gate (4/4 datasets, every edge t->t+1) with the SHIP cfg verified
in each kernel log -- no silent zeros.
**GOTCHA: Kaggle slugifies the TITLE -> prunE became `biohub-prune-submit` (NOT `prune-e`).**
Read the slug back from the push output before `kernels status` / `competitions submit`.
HONEST CAVEAT: with LB noise +-0.005, five draws will PROBABLY yield something >0.921 by luck
alone. That is a real PUBLIC-LB rank gain but does NOT transfer to private (noise is redrawn).
The lasting value is making the CV-best configs AVAILABLE as 09-29 candidates -- you cannot
select what you never submitted.

### 09-29 FINAL SELECTION — hedge the ESTIMATOR, not just the mechanism
The two estimators rank our candidates ANTI-correlated (the signature of one being pure noise):
  prune tau.60: CV +0.0049 (best) but LB 0.918 (worst) | flow k8: CV +0.0015, LB 0.921 |
  sim4: CV base, LB 0.921.
Final standing takes the BETTER of your 2 picks, so cover BOTH hypotheses rather than one twice:
  1. `55751003` sim4 0.921      -- wins if the LB ordering is real (CV biased by train/test shift)
  2. `55826863` prune tau.60 0.918 -- wins if CV is right and the LB was too coarse to see it
(The earlier "both 0.921s" plan hedges MECHANISM but bets entirely on the weaker instrument.
 If a hit-and-trial arm scores well AND has top CV, it can replace pick 2.)


**ACCOUNT BEST = 0.921** (`55751003` sim4), banked. Every LB lever exhausted (flow/ranker/
prune/edge-model all <=0.921 -- the learned edge model ANTI-correlates on LB because it overfits
the 2 train embryos). See the ABSTENTION FINAL VERDICT block below.

**ZEBRAHUB EXTERNAL-DATA BET = FAILED** (tested on the RTX 4050, 2026-08-28). The pipeline is
fully de-risked (detector transfers 0.963, dynamics match, alignment+placement solved, 4 embryos
usable) BUT the local whole-embryo-holdout A/B shows the learned edge model does NOT beat the
GEOMETRIC COST on a novel embryo (ties/loses), and more embryos barely helps (+0.002-0.007). Same
wall as the competition: geometry is at CEILING for the local edge decision. => external data
does NOT break 0.921. See SCOPE_ZEBRAHUB.md "LOCAL A/B ON THE 4050". 
**FINAL VERDICT: 0.921 (sim4, 55751003) is the DEFINITIVE accessible own-work ceiling.** Every
lever exhausted with direct evidence: detection (0.978 recall ceiling), geometry linking (cost at
ceiling), learned edge model (<=cost on novel embryos, comp AND zebra), prune/abstention (LB
anti-correlated), external data (4050 A/B negative), global-flow/divisions/metric (dead). The
0.95 prize zone is NOT reachable with accessible methods. Do NOT spend slots on rerolls of tested
<=0.921 configs.

**09-29 FINAL SELECTION (CORRECTED after a full 50-submission audit) — pick BOTH 0.921s:**
  1. `55751003`  0.921  sim4 (fill+max_link8+appearance sim_w4)      -- momentum+appearance linker
  2. `55802000`  0.921  flowprior k8 (a.25/b.75 collective flow)     -- neighbourhood-flow linker
Two submissions are TIED at the top score but use STRUCTURALLY DIFFERENT linking mechanisms
(own-velocity+appearance vs collective flow field of k nearest moving neighbours). Since the final
standing is the PRIVATE test, this gives top public score TWICE from two different mechanisms =
genuine diversification against a private rerank at ZERO cost. This SUPERSEDES the earlier
"0.921 + Kunal 0.917" plan, which needlessly gave up 0.004 for diversity we can get for free.
- Detector transfers (UNet recall 0.963 on Zebrahub), edge dynamics match (1.81 vs 1.82um),
  alignment solved (xy*0.5 auto-calib), placement solved (cell-seeded, hollow-shell-safe).
- 4 distinct dense external embryos usable (ZSNS001/003/004/005). Kaggle dataset
  `eeshsaxena/biohub-zebrahub-crops` uploaded (starter: ZSNS001_tail x6 + ZSNS004 x3).
- Files: phase0/phase1_zebrahub.py, scratch_kernels/build_zebra_edgemodel.py (Phase 2, the A/B),
  build_zebra_dettest.py. All compile-verified + logic-tested.
- BLOCKER: Kaggle weekly GPU quota EXHAUSTED (resets in days) -> the DECISIVE A/B (does zebra
  raise held-out-comp-embryo AUC vs comp-only?) runs then OR on the user's box. Honest ceiling
  even if A/B positive: ~0.925-0.93 (edge model touches only ~2% steal edges), NOT the 0.95 prize.
- NO submissions pending; quota 0 today.

## CURRENT STATE — 2026-08-26  (single source of truth; supersedes the 08-23
## block below, which is now historical)

**ACCOUNT BEST = 0.921** (`55751003`, 2026-08-24: fill + max_link8 + appearance
linker **sim_w4**). Prior anchors: fillmax8/accel = 0.920 (`55746864/69/74`,
`55750902`), fill1 = 0.919 (`55701475`), Kunal 0.917 (`55681317`) fallback.
The 08-23 handoff's "0.919 best" is superseded by these 08-24 results.

**LEADERBOARD CONTEXT (08-26, via CLI):** top = 0.962 (Ayati, z7777), TWEAK
0.953, Cooper 0.950, then a dense 0.942-0.947 pack. Prize zone (top ~7) is
**>=0.95**. We are ~0.921 => well below prize; the gap is the EDGE/LINKING term
(confirms TWEAK's "+0.03-0.05 graph plugin on unchanged detections").

### 08-24 lever results (all on the fill+max_link8 stack)
| lever | LB / CV | verdict |
|---|---|---|
| **sim_w4** (appearance weight 2.0->4.0) | **LB 0.921** | best submitted; +0.001 over 0.920 (LB-noise-small) |
| t+2 accel b1.6/m6, b2.4/m6, b0.80 | LB 0.920 | neutral vs fillmax8 on LB (CV said +0.0006-0.0015) |
| max_link8 tighter gate | LB 0.920 | = fillmax8 |

### 08-24 CV levers built but NOT submitted (harvested 08-26)
| CV kernel | pooled (base 0.8726) | verdict |
|---|---|---|
| **flowprior** `flow a.25 b.75 k4` | **0.8758 (+0.0032, BOTH embryos)** | **LARGEST CV GAIN TO DATE — never submitted** |
| flowprior `flow a0 b1 k4` | 0.8741 (+0.0015 both) | robust alt |
| DeepCenter **veto** on synth nodes | -0.0070 both | **NEGATIVE — dead (INTEL #3 killed)** |
| **cascade** | no arm beats accel-CTRL | **NEGATIVE — dead** |
| **margin** (geometry assoc-prune, INTEL #2-lite) | every arm loses both | **NEGATIVE — dead; ranker needs a LEARNED discriminator** |
| learned **ranker** CV (INTEL #2) | never pushed (404) | untested; margin-fail lowers its prior |

**FLOWPRIOR = the lead lever.** Pure geometry (no assets/external data): 2-pass
linker, pass 2 predicts `pred = P + alpha*own_vel + beta*local_flow` where
local_flow = inverse-distance-weighted mean OUT-velocity of the source's k
nearest MOVING neighbours. Directly kills the 2.0% "steal" edges (steals land
~8.76um away on a neighbour; neighbours move together, so the flow field gives a
better landing spot). CV is clean: sanity control (beta=0) reproduces base to
every digit; both embryos win monotone in beta; mechanism = more TP edges AND
fewer FP+FN. Builder: `scratch_kernels/build_flowprior_cv.py` (the flow linker is
in `_link_flow`/`repair_cfg` linker=="flowprior").

### 08-27 RESULTS — flowprior is real but MARGINAL; ranker DEAD
**flowcombo-cv (16 movies, control = live sim4 0.921):** the original v11 flowprior
+0.0032 SHRANK against the true base. VERDICT vs sim4: flowA k4 44b6 +0.0037 / 6bba
**-0.0003** (fails), flowA+sim4 k4 +0.0052 / **-0.0007** (fails), **flowA+sim4 k8
+0.0030 / +0.0009 = the ONLY both-embryo winner, +0.0015 pooled.** Wider k rescues
the harder embryo (6bba -0.0003@k4 -> +0.0009@k8). The v11 +0.0032 was a
small-movie-set + weaker-base artifact — the user's "research before submitting"
call was correct.
**ranker-cv (INTEL #2, learned assoc ranker): DEAD.** Classifier is great (OOF AUC
0.9799, x-embryo 0.976-0.978) but applying it to linking = **+0.0002** (noise).
Diagnostic: on 1-positive groups the geometric COST already top-1s 92.85% vs ranker
92.48% (WORSE); on low-margin groups cost 0.644 vs ranker 0.589 (WORSE). => LOCAL
link decisions are at CEILING; geometric features are exhausted. Rules out the whole
local-discriminator family.
**THEORY (important):** global min-cost-flow with frame-pair-local costs DECOMPOSES
into the per-frame Hungarians we already solve => no gain. A real edge-precision jump
needs TRAJECTORY-level costs or a LEARNED IMAGE-BASED edge model (the 680-GPU-hr
transformer we can't train, or TWEAK's non-public plugin). **0.921 -> 0.94 is NOT
reachable with legal own-work on this stack in-session.**

### ROUND 2 (08-27, "try again") — 6-agent lever hunt + 2 zero-downside actions
Workflow `biohub-lever-hunt` (5 research agents + synth) verdict: NO lever likely
beats 0.921 (gap = linking-precision/steals, untouched by all candidates). Two
+value zero-downside actions taken:
- **yunus_v17 SUBMITTED** (`biohub-next-yunus-v17-harmonic-association` v1; fresh
  UTC-day slot, 4 left). Independent learned dual-seed UNet-transformer + harmonic
  association; label-free (ground_truth_accessed=false), 239627 rows, all 4 datasets,
  edges consecutive. Won't beat 0.921 (family ceilings ~0.913 for us) — value = real
  LB datapoint for the family + 09-29 hedge candidate. Builder `build_yunus_v17.py`.
- **DeepCenter-into-detection-MEAN probe** (`biohub-dcprobe-cv`, FREE): GATE **FAILED**
  (valid run, v2). DeepCenter loaded (best.pt, base=24; v1 had a key-name bug `s.b` vs
  checkpoint `s.block` -> ran empty -> void). Recall: avg015 0.9857; dc-weighted 0.2/0.3/0.5
  = 0.9852/0.9841/0.9832 (monotonically WORSE -> DeepCenter dilutes the stronger Kunal
  branches). Per-embryo: 44b6 +0.0011, 6bba -0.0013 -> helps one, hurts the other, pooled
  DOWN. NOT submitted. Closes the DeepCenter-in-average question (the last genuinely-new
  large structural lever). Port lives in `build_dcprobe_cv.py`. LESSON: recall is not the
  binding constraint anyway (edge is steal/precision-bound), so even a robust recall bump
  likely would not move the score.
- SKIPPED (dead/banned): metric-exploit (division-hub trick patched + under host
  review = DQ risk; node-count knob = dead threshold; N_est hidden at test),
  harmonic-onto-Kunal (reduces to the dead 0.903 bidir linker — no learned edge
  matrix in the Kunal stack).

### IMAGE-SIGNAL FEASIBILITY (08-27, `biohub-imgedge-cv`, FREE) — CLOSES the edge-model question
The last open question: can IMAGE appearance break the 2% steal-ties geometry cannot? On
ambiguous near-distance ties (source with 2 targets within 2um), 3 pickers COST(nearest) /
IMG(3D-patch NCC) / FUSE(dist-3*NCC). RESULT (pooled 79 ties): COST 0.734, IMG 0.798,
**FUSE 0.785 (+0.051, beats COST on BOTH: 44b6 .882->.941, 6bba .694->.742).** => IMAGE
SIGNAL IS REAL (the first positive edge-term finding all session). BUT ambiguous ties are
only **~10/movie** (79 across 8 movie-subsets), so a PERFECT fix moves edge-J ~0.6/8000 =
**+0.0001 = negligible.** This is exactly WHY public image-based edge transformers cap
~0.917-0.920 (below our 0.921): the signal is genuine but the addressable cases are too rare.
A full off-Kaggle edge model = large build for ~0.0001-0.005, unlikely to even transfer.
**VERDICT: edge-model path CLOSED as not-worth-it. 0.921 is the accessible ceiling, now
confirmed by DIRECT MEASUREMENT, not analogy.** Port: `build_imgedge_cv.py`.

### ROUND 3 RESULT (08-27) — the IMAGE EDGE MODEL WORKS (first real edge lever)
`biohub-edgemodel-cv` (v1, 8 movies, cross-embryo OOF) BEAT the geometric ranker on the
decisive axis: LOW-MARGIN ambiguous ties cost 0.682 -> **model 0.727** (the geo-ranker got
WORSE, 0.644->0.589); overall top-1 cost 0.932 -> model 0.936 (right MORE than distance even
on clear cases); OOF cross-embryo AUC 0.977/0.968. ACTUAL pipeline dSCORE, **both embryos
positive**: full b1.0 = 44b6 +0.0013, 6bba +0.0006, **pooled +0.0009** (monotone b0.5 +0.0003
-> b1.0 +0.0009 => headroom). Weights saved to edge_model/ (edgecnn_<emb>.pt = cross-emb OOF
models; norm.npz). This is the FIRST lever all session that beats cost on the ambiguous cases
AND clears the both-embryo bar. Small but real + mechanistically sound (image breaks steal-ties
geometry can't).
### ROUND 3c (08-27) — edge model v2 result + SUBMISSION built
v2 (`biohub-edgemodel-v2`, 12 movies): OOF cross-emb AUC **0.980** (44b6 .979/6bba .980);
bonus sweep both-embryo +: b1.0 +0.0005, b2.0 +0.0010, **b3.0 +0.0011** (44b6 +.0011/6bba +.0010,
most balanced); rescue negative. Lever is real+cross-emb-validated but PLATEAUS ~+0.001 CV
(low-margin ties tied cost this run). SUBMISSION kernel BUILT + pushed: `biohub-edgemodel-submit`
(`build_edgemodel_submit.py`): trains edge CNN on ALL train data, runs full pipeline on hidden
test with linker=accel_rank full-b3.0 on the **sim4 base** -> submission.csv (integrity-gated).
Re-trains in-kernel at scoring (~40min train + inference, <12h). Waiter `bx0wg7cgs`. NOTE: edge
model validated on sim_w=2 accel base (+0.0011); shipping on sim_w=4 base (unvalidated interaction
but likely additive). Honest expected LB ~0.921-0.922 (flat-to-marginal; +0.001 CV is sub-wall).
Value = real LB datapoint for the learned-image-edge approach + prize-eligible OWN-WORK pipeline.

### ROUND 3b — `biohub-edgemodel-v2`
Strengthen: 12 movies (6/emb), 90 frames, 16 epochs, bonus sweep full b{1.0,1.5,2.0,3.0} +
rescue s0.4. Waiter `bmol4geul`. Goal: push +0.0009 toward the >0.005 noise wall.
SUBMISSION PLAN (once best bonus known): build a submission kernel that (1) trains the edge CNN
on ALL train movies (both embryos -> edgecnn_all.pt; the OOF models are for validation only, and
the 2 TEST embryos match neither train embryo so use an all-data model), (2) runs the full Kunal
pipeline on TEST with linker=accel_rank + best bonus -> submission.csv. `build_edgemodel_cv.py`/
`_v2.py` hold the extraction+CNN+integration code to port. Local torch CPU-only; RTX 4050 avail
for heavier off-Kaggle training if the compact model's signal grows.

### ROUND 3 (08-27, "build the edge-model") — (superseded by results above)
The image-signal test said appearance IS real edge signal but ties are rare. User directed
building the actual learned IMAGE edge model anyway (goal: prize-eligible own-work pipeline).
KEY: this is CHEAP enough to train ON KAGGLE (the 680-GPU-hr figure was for the full DETECTOR;
a compact edge classifier on pre-extracted patches trains in ~1-2h). `biohub-edgemodel-cv`
(`build_edgemodel_cv.py`, cloned from build_ranker_cv.py): reuses the ranker's candidate/
feature/label/`_link_accel_pr`/`repair_cfg(accel_rank)` scaffold, swaps HGB for a 3D-CNN on
2-channel patch pairs (source@t, target@t+1; 5x21x21, per-patch normalized) fused with the 31
geometry feats. EMBRYO-level OOF (train 44b6->predict 6bba & vice versa = honest 2-unseen-embryo
analogue). Reports OOF cross-embryo AUC, group top-1 + LOW-MARGIN accuracy (the bar: beat COST
0.644 on ambiguous, where the geo-ranker got 0.589 and FAILED), and the ACTUAL pipeline dSCORE
(rescue/full arms). SAVES weights to /kaggle/working/edge_model/ for a submission kernel. Waiter
`b10lus608`. IF both-embryo +dSCORE clears noise -> port to sim4 base + submit. Local torch is
CPU-only; user has RTX 4050 (6GB) for heavier off-Kaggle training from the extracted patches if
the Kaggle compact model shows signal. GATE: geo-ranker was AUC 0.98 but +0.0002 score, so AUC
alone is NOT the bar -- the ambiguous-line accuracy + real dSCORE are.

### ROUND 4 (08-27) — THE ABSTENTION LEVER (biggest finding of the project)
**Metric algebra:** `J = TP/(TP+FP+FN)` and **TP+FN = |GT edges| is CONSTANT** (verified in
kaggle/scoring.py: `edge_fn = n_gt_edges - tp`, `edge_fp = valid - tp`). So a WRONG edge costs
an FP *and* an FN; emitting NOTHING costs only the FN already lost. Deleting a wrong edge
shrinks the denominator for FREE. **Break-even precision = 1/(1+J) = 52.8%** (at J=0.893).
Confirmed numerically on the verified scorer (pruning 10 wrong edges: J 0.714 -> 0.833; crossover
exactly at the predicted precision). Our 136 wrong edges are worth up to **+0.033** if removed.
Earlier pruning attempts failed with a GEOMETRIC discriminator; the AUC-0.98 image edge model
had never been pointed at this (all prior uses only RE-ROUTED links).
CV RESULTS (12-movie, cross-embryo OOF, pooled dSCORE vs control 0.8910):
| arm | 44b6 | 6bba | pooled |
|---|---|---|---|
| **ml10 + prune .25 + b2** | +0.0046 | +0.0015 | **+0.0028 (BEST)** |
| b2 + prune.10 + dist-tier | +0.0044 | +0.0015 | +0.0025 |
| ml10 + prune .25 | +0.0044 | +0.0003 | +0.0020 |
| prune .10 alone (ml8) | +0.0018 | +0.0017 | +0.0017 |
| **gate ml10 ALONE (no prune)** | -0.0022 | -0.0026 | **-0.0022** |
| distance-only d>6 | +0.0038 | -0.0020 | -0.0000 |
| nomatch abstention | +0.0007 | +0.0003 | +0.0004 |
KEY: a LOOSE GATE is -0.0022 ALONE but +0.0028 WITH the pruner (+0.005 swing) — the pruner
UNLOCKS a setting that was harmful. Abstention (+0.0017) > re-routing (+0.0011), as the
asymmetry predicts. Distance-only = break-even EXACTLY as predicted from local GT (true motion
median 1.82um, p99 7.45um) — and adds nothing on top of the model (raw_distance_um is already
a model feature). Pruner precision backed out ~55-82% vs 53.7% bar; tau-curve DECLINES past the
optimum => the limit is the RANKING, not the threshold.
DEAD by algebra (no compute spent): dual-emission (scorer allows 2 edges/source, break-even
47.2%, edge gain ~+0.002 but each extra fork on a GT-matched parent is a division FP = -0.021);
node-dropping for the node_ratio bonus (loses ~2X in J to gain ~0.09X in penalty).
SUBMITTED (user-authorised 2): **A = ml10+prune.25+b2** (`55824199`, integrity PASS, 255458
rows) and **B = ml8+prune.10+b2** (building). Both on the sim_w=4 base (CV used sim_w=2 —
small unvalidated interaction, accepted for the better base). Builders:
`build_edgeprune_cv.py` (tau sweep), `build_prune2_cv.py` (loose gate + nomatch + 12um FEATURE
gate — REQUIRED for ml10+, else 8-12um pairs get prob 0 and are pruned unconditionally),
`build_prune3_cv.py` (distance tier), `build_prune4_cv.py` (division recovery, RUNNING),
`build_prune5_cv.py` (SECOND-STAGE decision-trained pruner + DIRECT prune-precision readout,
queued), `build_pruned_submit.py` (BIO_ARM=prunA|prunB submission builder).
NOTE: prune runs LAST (after gap-fill) or the pipeline re-bridges what it removes.
LB: **yunus v17 = 0.920** (independent learned-transformer family caps BELOW our 0.921).

### FINAL POSITION (08-27, after 2 exhaustive rounds + image-signal test)
Account best = **0.921** (`55751003` sim4), UNCHANGED and BANKED. Every lever tested with
CV+LB+gate evidence: flow (LB-dead), ranker (dead), global-flow (proof), DeepCenter-mean
(gate fail), detector-union (dead), metric (banned), IMAGE edge-signal (real but negligible).
The 0.94+ pack is not reachable with legal in-reach own-work. FOR 09-29 FINAL SELECTION (2
slots): pick **sim4 0.921** (`55751003`) as anchor + one DIVERSE hedge (best-scoring learned
family, e.g. Kunal-exact 0.917 or yunus once scored) in case private LB reranks. Do NOT waste
future sessions re-deriving dead levers — the ceiling is measured.

### SUBMITTED 08-27 (earlier, prev UTC day: flow probes)
- **flowA+sim4 k8** (`55802000`, slot 1) = fillmax8+sim4+flowprior(a.25/b.75,k8).
  CV +0.0015 both-embryo. PENDING.
- **flowB1+sim4 k12** (`55802740`, slot 2) = fillmax8+sim4+PURE flow(a0/b1,k12).
  CV **+0.0028 both-embryo, the best flow config** (flowrefine sweep). PENDING.
  KEY FINDING: pure collective flow (own-momentum OFF) with 12-neighbour pooling
  beats mixed a.25/b.75 — the denoised neighbourhood displacement is a better next-
  position predictor than a cell's own velocity (coherent tissue motion).
- 0.921 (`55751003`) stays banked as fallback. Builder =
  `build_recall_submission.py` env vars `BIO_LINKER=flowprior BIO_ALPHA BIO_BETA
  BIO_KFLOW BIO_SIMW BIO_TAG` (flowprior fully ported into the submission linker).
- **LB RESULT (FINAL): flowprior is LB-DEAD.** flow k8 (`55802000`, +0.0015 CV) =
  **0.921 FLAT**; pure-flow k12 (`55802740`, +0.0028 CV, the CV-"best") = **0.919
  WORSE**. => the flow lever's CV gain is ANTI-CORRELATED with LB (bigger CV gain ->
  worse LB): textbook overfitting to the 2 train embryos. DO NOT submit any flow
  variant (all would score <=0.921). **Account best stays 0.921 (sim4, `55751003`).**
  This is the STRONGEST calibration result yet: the 2-embryo CV is not merely noisy
  for sub-0.003 edge gains, it can INVERT them. Future sessions: do NOT trust CV
  deltas < ~0.005; only LB-isolated levers count. Held slots 3-5 (nothing +EV to
  spend them on).
- (superseded) HOLDING slots 3-5 for LB feedback.
  If flow helps on LB -> refine further; if flat/negative -> flow is LB-dead, stop.
  flowrefine full VERDICT (all both-embryo +): k8 +.0030/+.0009, k12 +.0019/+.0016,
  k16 +.0012/+.0018, b.9k8 +.0042/+.0005, **b1k12 +.0040/+.0024 (best)**.

### IN FLIGHT (08-27) — no submission cost
`biohub-flowrefine-cv` (`build_flowrefine_cv.py`, 16 movies): sweeps k {8,12,16} + β
{.75,.9,1.0} vs sim4, to squeeze the flow lever's best both-embryo config for slots
2-3. Submit only a config that beats k8 on BOTH embryos; else hold slots.
Public intel mined (`_intel/`): reyhan_graphpatch = same Kunal family; bt_v6 /
navaz_best / saiteja_v16 = learned transformer+ILP (caps 0.894 for us). No public
0.94+ method. Chrome extension NOT connected => Kaggle discussion CONTENT unreachable
(leaderboard via CLI only; field 0.94-0.96, prize >=0.95).

---

## CURRENT STATE — 2026-08-23  (historical; superseded by 08-26 above)

**ACCOUNT BEST = 0.919** (`55701475` "fill1"). Fallback: Kunal 0.917 (`55681317`).
fill1 = the exact Kunal 3-UNet flip-TTA detection + score-aware fwd linker +
short_filter(6) + linefit + SHIPPED safe-divisions (divergence 2.25), with ONLY the
gap-fill step changed to aggressive midpoint SYNTHESIS (cap 8%, gap=1, thr 0.15).
Builder `scratch_kernels/build_recall_submission.py` (CFG/DIV_CFG/LINKER/TAG);
guarded submit `scratch_kernels/submit_at_reset.py`. Quota: 5/5 used 2026-08-23,
resets 00:00 UTC.

### MEASURED score decomposition (from LB isolation, not theory)
| submission | LB | meaning |
|---|---|---|
| fill1 (gap-fill + shipped div) | **0.919** | best |
| filltightdiv (div gate 3.0) | 0.918 | ~= fill1 |
| filldiv (div gate 1.0) | 0.903 | loosening divisions HURTS |
| **fillnodiv (divisions OFF)** | **0.893** | **isolates the EDGE term** |

=> **edge term 0.893, division contribution +0.026** (div_jaccard ~0.26). Node
recall 0.978 => edge ceiling (recall^2) **0.9565**, so **0.0635 is lost AFTER
detection = a GRAPH/LINKING loss**, NOT a detector loss. Leader 0.958 is most
plausibly edge ~0.93 (better linking), since the division term is capped at 0.1.

### LEVERS — all LB/CV tested
POSITIVE: aggressive gap-fill (+0.002, the one win).
NEGATIVE/DEAD (do NOT retry): division relax (-0.016) & divisions off (-0.026) =>
shipped gate 2.25 is near-optimal; detection union; seed-threshold lowering; NMS
shrink; MAX-fusion; bidir linker (LB 0.903, masked); gap max_dt=3; **SHORT_MIN
sweep** (CV v7: sm6 .8661 / sm5 .8666 / sm4 .8666 / sm3 .8658 — noise; node recall
rises but edge J doesn't, because gap-fill already rejoins real fragments);
**linefit** (measured
locally: smoothing displaces nodes a median 0.65um / p99 3.1um from truth, only
0.02% exceed the 7um match gate => harmless, not a lever); **learned division detector** (real labeling wall ~3 positives/12 movies; CC0
synthetic pretrain transfers at ROC-AUC 0.52 = random); **own detector training**
(count-calibrated recall@500: 44b6 0.628, 6bba 0.013 bimodal collapse vs 0.978).

### CALIBRATION RULES (hard-won)
- CV (10 train movies) is reliable for the EDGE term, NOT the rare DIVISION term
  (CV said div-relax +0.0016; LB said -0.016). LB is the only judge for divisions.
- Perfect-detection/GT-only sims OVERSTATE add-detection & division levers (they
  cannot see matched-FP edges, node_ratio, or broken-track-start forks).
- Local sims that omit a pipeline stage mislead (my short_filter sim predicted
  +0.015 by ignoring gap-fill; real answer was +0.0005).

### EDGE-LOSS ATTRIBUTION RESULT (biohub-edge-attrib, real pipeline, train movies)
| outcome | count | share |
|---|---|---|
| TP | 3401 | **95.4%** |
| det_miss | 63 | 1.8% |
| **steal** (linked to a different node) | 73 | **2.0%** |
| terminate (no successor) | 27 | 0.8% |

Steal distance to the TRUE target: **med 8.76um, p90 11.6um** — i.e. steals link to a
NEIGHBOURING cell. Cells move only ~1.8um/frame (p99 7.45), so those links are made in
the linker's LOOSE second pass (MAX_LINK_UM=10). KEY CONSEQUENCE: each steal costs an
FN *and* emits an FP edge, so edge PRECISION (implied ~0.93 from LB J 0.893 vs train
recall 0.954) is the real gap — NOT recall, and NOT the detector (det_miss only 1.8%).
Tightening MAX_LINK 10->8 rejects just 0.74% of true links (10->7: 1.23%), so it should
kill steals almost for free. => `biohub-recall-lever-cv` v9 sweeps max_link {10,8,7} x
LINK_SIM_W {2,4}. This is the most promising untested lever for beating 0.919.

### LINKER SWEEP RESULTS (CV, pooled adjJ+0.1divJ; base fill1 = 0.8720)
| config | 44b6 | 6bba | pooled | verdict |
|---|---|---|---|---|
| fill1 (max_link 10) | 0.8633 | 0.8678 | 0.8720 | LB 0.919 anchor |
| **fillmax8** (max_link 8) | 0.8664 | 0.8678 | 0.8726 | + on 44b6, tie 6bba |
| **fillmax8 + t+2 accel b0.80** | 0.8660 | **0.8722** | **0.8732** | **CV BEST**, + on BOTH |
| max_link 7 | 0.8642 | 0.8677 | 0.8724 | worse than 8 |
| sim_w 4 | 0.8658 | 0.8678 | 0.8730 | ~= accel, not additive |
| mutual-consistency pruning (keep 0/2/3/4) | 0.862-0.865 | 0.8675-0.8678 | 0.8715-0.8724 | **NEGATIVE — all below base** |

- **t+2 acceleration lookahead WORKS but is small (+0.0006).** Implemented in both the
  CV and the submission builder (`ACCEL_CFG`); intel says it is the single change in
  the public 0.915 no-hack lineage inherited by the 0.920 forks.
- **Mutual-consistency pruning FAILED.** The FP-structure theory is right (a wrong
  link costs FP+FN, no link costs only the FN) but the discriminator does not reach
  the required >52.8% precision. Pruning levers need a much better discriminator —
  i.e. the learned 22-feature association ranker (INTEL.md lever #2), not geometry.

### MORE LEVER RESULTS (2026-08-23 late)
- **t+2 accel tuned well BEYOND the public default**: bonus 0.20 (public) -> 1.60 and
  tolerance 4->6um. Pooled 0.8726 (fillmax8) -> **0.8741**, winning on BOTH embryos
  (44b6 0.8666, 6bba 0.8733). Largest CV gain since gap-fill; all of it edge-term.
- **2-opt identity-SWAP repair: NEGATIVE.** Only 2-5 swaps found per movie and every
  margin scored below base (0.8720-0.8724 vs 0.8726). Informative: our steals are NOT
  clean two-way identity exchanges, they are ONE-SIDED mislinks — so 2-opt has almost
  nothing to fix. Rules out the whole "swap-detection" family.
- **Mutual-consistency pruning: NEGATIVE** (see table above) — geometry cannot reach
  the >52.8% discriminator precision that pruning requires.
=> Both pruning AND swap families are now closed. The remaining hope for the edge
term is a LEARNED discriminator (association ranker) or better node quality.

### SUBMIT AT 00:00 UTC RESET (best-first)
1. `biohub-recall-accel16m6-sub` — fill + max_link 8 + t+2 accel b1.6/m6 (CV **0.8741**)
2. `biohub-recall-fillmax8accel-sub` — same with accel 0.80 (CV 0.8732)
3. `biohub-recall-fillmax8-sub` — fill + max_link 8 (CV 0.8726)
Anchor stays fill1 = **0.919** (`55701475`); Kunal 0.917 (`55681317`) is the fallback.
See `INTEL.md` for the ranked next levers (learned association ranker, DeepCenter
veto on synthesised nodes, harmonic edge-score fusion, Zebrahub external data).

### IN FLIGHT (autonomous chain)
1. `biohub-edge-attrib` — attributes EVERY lost GT edge to det_miss / steal /
   terminate on the real fill1 pipeline. Decides the next lever: 'terminate' =>
   cheap gate knob; 'steal' => needs a learned edge/flow model.
2. `biohub-recall-lever-cv` v8 — LINKER sweep on fill1: LINK_SIM_W {0,2,4,8}
   (appearance weight, never swept) + wider gates (tight 8 / max_link 12).
Best surviving config gets submitted at the 00:00 UTC reset.

### Kaggle traps (still live)
Base image lacks zarr (reading .geff GT needs offline `biohub-zarr-wheels`; the
submission itself uses a blosc2 fallback). train/ = 199 .zarr + 199 .geff
(44b6x71, 6bba x128). Must set T4 machine_shape. Kernel slug derives from TITLE —
make metadata `id` match or re-push 409s. Max 2 concurrent GPU sessions ACCOUNT-WIDE.

### Research tooling (local, no GPU)
`kaggle/exp_{scoring_optimum,recall_levers,union_ceiling,division_tune,edge_decomp,
synth_pretrain_div}.py` on `data/train/*.geff`; `kaggle/division_detector.py`.
Public/CC0 assets (synthetic data, flow-UNet template) catalogued in
`ROADMAP_TO_095.md`. Full lever history in `RECALL_RESEARCH.md`.

---

## TL;DR

- **Competition:** Kaggle "Biohub - Cell Tracking During Development". Code
  competition: notebook-only, **internet OFF**, 12 h cap, single T4. Final
  submission **2026-09-29**. 2 train embryos (`44b6`, `6bba`), 2 *different* test
  embryos. **5 submissions/day. Max 2 concurrent GPU kernels.**
- **Best account LB = 0.919** — fill1 (aggressive gap-fill on the Kunal 0.917
  stack; see CURRENT STATE above). Prior anchor `biohub-win-Kunal 0917 exact`
  = 0.917. The validated learned-pipeline baseline remains **0.894** (`biohub-rep300`).
  (TemporalUNet3D + node cross-attention edge transformer + pyscipopt ILP) with
  **300-epoch weights** + full deterministic graph repair.
- **Trajectory:** 0.825 → 0.841 (a week of classical DoG tuning) → 0.887 (switch to
  the learned pipeline) → **0.894** (300ep weights).
- **0.894 is the CEILING of the public-weights pipeline.** Six independent probes
  failed to beat it (below). **Stop tuning it.**
- **The scoring identity that governs everything: `edge_J ≈ node_recall²`.**
  Proven locally in `kaggle/exp_linker_ceiling.py`. Linking, divisions and node
  position precision are ALL solved; the entire remaining gap is DETECTION RECALL.

---

## THE decisive experiment (do not redo — just trust it)

`kaggle/exp_linker_ceiling.py` (runs locally on the GT `.geff` graphs, no images, no GPU).
Feed GT node positions in as "perfect detections" and link them with our own linker:

```
clean ceiling (perfect positions)   edge J 0.9874   (precision 1.000)
z-quantisation ±0.8um               0.9862   <- position precision is IRRELEVANT
xy noise 0.4um                      0.9869      (explains why subvoxel was neutral)
DROP  8% of cells (recall 0.92)     0.8292   <- MATCHES our real LB edge ~0.83
DROP 12% of cells (recall 0.88)     0.7717
```

So `edge_J ≈ node_recall²`. Our recall ~0.92 → edge ~0.83. The 0.914 pack implies
recall ≈ **0.955**; the 0.942 leader implies ≈ **0.97**.
**=> The ONLY lever left is detection recall that generalises to 2 unseen embryos.**

---

## Current best pipeline (how to reproduce 0.894)

```bash
python scratch_kernels/build_learned_repair.py rep300 \
    WEIGHTS=hongdaekim/biohub-300ep-checkpoint-pin-v1
python -m kaggle kernels push -p scratch_kernels/sub_rep300
# when COMPLETE:
python -m kaggle competitions submit biohub-cell-tracking-during-development \
    -k eeshsaxena/biohub-rep300 -v 1 -f submission.csv -m "..."
```

`build_learned_repair.py <tag> [WEIGHTS=slug] [SOUP=slugA,slugB] [BIOHUB_*=val ...]`
runs the public reference notebook (`scratch_kernels/_forum/biohub-cell-tracking-
learned-graph-w-gap-recovery.ipynb`) verbatim, with env-var overrides. Runtime
~30 min for the full hidden test (~1.5 min/sample) — comfortably inside 12 h.

Every graph-repair knob is a `BIOHUB_*` env var: motion relink (tight 5.9um /
relaxed 9.8um), gap close (max_gap 1, 5.75um, added-frac cap 0.038), linefit
smoothing (w 0.76, window 2), safe divisions, single-parent repair, prune-isolated,
edge_max 14um. Defaults are the tuned ones.

**The weights are the ONLY thing that mattered.** The reference notebook is tagged
`EXPERIMENT_TAG = "candidate_23_300ep_clean_strict_repair"` but ships the **50ep**
pack (`TARGET_ARTIFACT_SLUG`), which is why running it as-is gives 0.887, not 0.914.

---

## Everything that FAILED to beat 0.894 (do not retry)

| probe | LB |
|---|---|
| `rep300` 300ep weights + full repair | **0.894** ← best |
| `rep300r` + recall-leaning repair (single-child, gap budget 0.06) | 0.894 (**+0.000**) |
| `repseed` independent seed-314159 model | 0.892 |
| `soup35` SWA average of 300ep+350ep | 0.891 |
| `r3d97` det 0.97 **on 300ep weights** | 0.893 |
| `rep350` 350ep weights | 0.890 (past the generalisation peak) |
| 50ep weights, det 0.95/0.97/0.985/0.99, repair on/off | all 0.886-0.887 (flat) |

Two things worth internalising:
- **The epoch curve peaks near 300**: 350ep is *worse* than 300ep. More training is
  not the lever.
- **The det threshold is genuinely dead**, not masked. It was flat on 50ep weights;
  I re-swept it on the good 300ep weights specifically to rule out "the weak model
  hid the effect" — still flat. Same for every repair parameter.

Older dead ends (classical era): our own dense-target 3D U-Net (LB 0.682, memorises
with 2 embryos), pretrained Cellpose (bimodal collapse), per-cell motion prediction
(falsified), sub-voxel refinement (neutral), detection-density/min_sep sweeps
(exhausted), and **worst-embryo CV ranking** (ranked configs BACKWARDS — always use
POOLED `adj_edge_jaccard`).

---

## The prize problem (read before planning)

Public weights **tie** the pack rather than beat it, and a prize-winning solution
almost certainly must be our own reproducible work. So 0.894 is a *floor*, not a
finish. But:

**Own-training is measured infeasible on Kaggle free tier.** The host trainer now
works end-to-end (`scratch_kernels/build_own_train.py`) — training genuinely runs and
prints `Detection loss: weight=1.0, neg_weight=0.01`, i.e. the correct sparse
supervision. But it costs **~2.3 h/epoch** (3 epochs unfinished after 6.8 h).
300 epochs ≈ **680 GPU-hours** vs a 12 h kernel cap and 30 h/week quota.

And reproducing the host recipe would only re-derive ~0.894 anyway (50ep→300ep was
just +0.007; 350ep was worse). **So the recipe itself has to change, aimed at
detection recall.** Options, cheapest first:
1. Make an epoch cheap enough to fit: `--max-iters`, smaller `--patch`, larger
   `--downsample`, fewer frames sampled per sample. Then 300 epochs may fit in 2-3
   chained 11 h kernels (resume from `checkpoint_last.pth`).
2. Train off Kaggle (Colab Pro / rented GPU), ship weights as a Kaggle dataset.
3. Attack recall without training: a *union* of the learned detector with a
   complementary classical operator (DoG / determinant-of-Hessian / h-maxima).
   Over-detection is nearly free — the node-ratio penalty coefficient is only 0.1,
   and unmatched detections are invisible to the edge term — so a union that adds
   true cells is close to pure recall gain. **This is the cheapest untried idea and
   it targets the one lever that matters.**

---

## Kaggle environment traps (each one cost a failed run)

1. **`weights/` is a SYMLINK into the read-only `/kaggle/input` mount.** It broke
   three separate ways: `shutil.copy` into it, `Path.unlink()` of a file inside it,
   and training writing checkpoints — all `OSError 30: Read-only file system`.
   - To *swap* weights: copy the checkpoint to `/kaggle/working/swap_weights/` and
     **reassign `WEIGHTS_RELATIVE` to that absolute path**. pathlib makes
     `REPO_DIR / "/abs/p" == "/abs/p"`, so the notebook's check and `--weights` both
     follow it, and later cells see the reassignment. (Implemented as `WEIGHTS=`.)
   - To *train*: materialise the tree first —
     `shutil.copytree(w.resolve(), w, symlinks=False)` + `chmod`, BEFORE training.
2. **A kernel reports COMPLETE even when a training/predict subprocess dies rc=1.**
   Always print `rc` and the tail of stderr, or a failure looks like success.
3. The repo is **src-layout and NOT pip-installed** → subprocesses need
   `PYTHONPATH=REPO_DIR/src` or `ModuleNotFoundError: biohub_tracking`.
4. Host default `--batch-size 16` **OOMs a 14.6 GB T4** at `loss.backward()`.
   Use `--batch-size 4 --num-workers 2`.
5. **Max 2 concurrent GPU kernels**, and there is **no CLI cancel** — to kill a
   running kernel, push a trivial no-op version of it (frees the slot immediately).
6. Data mounts at `/kaggle/input/competitions/<slug>` (extra `competitions/`).
   Base image lacks zarr → install OFFLINE from a wheels dataset. Default GPU is
   P100 (sm_60) which base torch rejects → set `"machine_shape": "NvidiaTeslaT4"`.
7. Kaggle's per-file **download** API 429s hard; the kernels/datasets API is fine.
   Iterate ON Kaggle. `kaggle` is not on PATH here — use
   `.venv/Scripts/python.exe -m kaggle`.
8. LB scoring is **slow** (often hours). Submit and move on; don't block on scores.
9. Beware f-string brace collisions when generating notebook code from templates
   (`{...}` dict/set literals and nested f-strings need escaping).

---

## Repo map (what is actually current)

- `scratch_kernels/build_learned_repair.py` — **the submission builder.** Reference
  pipeline + `WEIGHTS=` / `SOUP=` / `BIOHUB_*` overrides.
- `scratch_kernels/build_own_train.py` — own-training kernel (works; too slow).
- `scratch_kernels/_forum/*.ipynb` — pulled public notebooks (reference pipeline,
  classical baseline, review notebook). Pull more with `kaggle kernels pull <ref>`.
- `kaggle/exp_linker_ceiling.py` — the `edge_J ≈ recall²` experiment.
- `kaggle/scoring.py` — numpy metric, **verified == official** (60/60 edges,
  30/30 divisions). Includes `evaluate_divisions` + `division_jaccard`.
- `kaggle/pipeline.py` — the classical DoG pipeline (superseded; caps ~0.85).
  Still hosts `link_tight_um` (two-pass linking) and `prune_isolated`.
- `kaggle/test_*.py` — all green (scoring, divisions, pipeline, two-pass, notebook).
- `official/` — the organizers' source, incl. `scripts/train_unet_transformer.py`
  and the true metric (`src/tracking_cellmot/metrics.py`, `division_metrics.py`).
- `data/train/*.geff` — GT graphs available LOCALLY (images are not).

## Metric reference

`score = adj_edge_jaccard + 0.1 * division_jaccard` (additive, max 1.1).
`adj = max(0, J * (1 - 0.1 * node_ratio))`, `node_ratio = (N_pred - N_est)/N_est`.
Only edges with `t_target - t_source == 1` count (gap edges are dropped, not
penalised). Node matching is a per-timepoint Hungarian at 7 um. **Edges between
UNMATCHED detections are FREE**, and a division FP only counts if the fork's parent
matched a real GT node — so over-detection and speculative forks are cheap.
Only ~0.737% of cells are annotated.

---

## ABSTENTION LEVER — FINAL LB VERDICT (2026-08-28)  ***READ THIS***

The abstention/prune lever (the biggest theoretical finding of the project, +0.033 ceiling)
is **LB-DEAD by a clean dose-response experiment.** Three submissions, a monotone ladder in
prune strength, scored INVERSELY to CV:

| sub | config | CV pooled | **LB** |
|---|---|---|---|
| prunB | tau0.10 | +0.0018 | **0.920** |
| prunA | tau0.25 gate10 | +0.0028 | **0.919** |
| prunD | tau0.60 gate10 div3.0 | +0.0049 | **0.918** |
| sim4 (banked, NO learned edge model) | — | — | **0.921** |

**The harder we prune, the WORSE the LB.** The CV dose-response is the exact inverse of the LB
dose-response. Also on LB: edge-model RE-ROUTE b3.0 = 0.920 (CV +0.0011). So EVERY learned-edge-
model intervention is net-negative, monotone with dose.

**ROOT CAUSE (definitive): the learned CNN edge model, trained on only 2 embryos, is
ANTI-INFORMATIVE on the 2 NOVEL test embryos.** Cross-embryo OOF on train (AUC-on-decisions
0.85-0.87, prune precision 72-94%) OVERESTIMATES generalization because it only ever holds out
1 of the 2 embryo TYPES; the test has 2 genuinely-new embryos. The detector generalizes (recall
0.978 on test) because it was trained on lots of data; the LINKER edge-model does not because
there are only 2 embryos of edge supervision.

**=> THE ENTIRE LEARNED-EDGE-MODEL DIRECTION IS CLOSED on LB.** Do NOT submit more learned-model
variants (re-route, prune, second-stage, ensemble/TTA — prune7 pushed CV to +0.0053 but it will
NOT transfer). The pure-geometric base (sim4) at 0.921 is the own-work ceiling. Geometric
abstention (distance-only) is break-even in CV so it neither helps nor hurts. All submitted
prune builders/kernels retained for the record: build_edgeprune/prune2..7_cv.py, build_pruned_submit.py.

**THE ONLY PATH THAT ADDRESSES THE ROOT CAUSE = EXTERNAL DATA.** Zebrahub imaging + *_tracks.csv
is HOST-CONFIRMED allowed, no test overlap (INTEL #5, forum 734330). It is zebrafish (same domain).
Training the edge model on Zebrahub's MANY embryos + our 2 would give the linker the embryo
diversity it lacks. This is the one lever with a path past 0.921, but it is a MAJOR multi-session
build (acquire Zebrahub [large], convert to our patch/track format, retrain). Detector already
generalizes, so target the EDGE model specifically. Odds uncertain; it is the honest next swing.

**09-29 FINAL SELECTION (2 slots): sim4 0.921 (55751003) anchor + flow-k8 0.921 (55802000) or
Kunal-exact 0.917 as a diverse hedge. NOT any prune/edge-model sub (all <=0.920).**

## ZEBRAHUB EXTERNAL-DATA PATH (2026-08-28) — Phase 0 GO
Scope in `SCOPE_ZEBRAHUB.md`; verifier `phase0_zebrahub.py` (self-downloads from
public.czbiohub.org, no auth). Phase 0 EXECUTED remotely = **GO**: same lab/marker/format,
voxel needs mild resample (L0 1.24/0.439/0.439 -> comp 1.625/0.40625/0.40625, factor
0.76/1.08/1.08), tracks are DENSE (ZSNS001_tail = 7.5M edges vs our ~10k sparse; 6 embryos
available). This is the ROOT-CAUSE fix for the 2-embryo overfit that made every learned-edge
lever LB-negative. Next: Phase 0 detector-recall at level 0 on the GPU box, then Phase 1
(dice embryos to competition-format crops) + Phase 2 (retrain edge model, WHOLE-embryo holdout).
Risks: automated-track label noise; modest ceiling (~0.925-0.93). Public URLs + exact fetch/
convert code are in phase0_zebrahub.py.

---

## AUTONOMOUS ZEBRAHUB EXECUTION (2026-08-28, 3-4hr run)
Phases 0/1/2 built+verified (SCOPE_ZEBRAHUB.md). Executing the detector-transfer test AUTONOMOUSLY
(no box needed): generate a few REAL level-0 Zebrahub crops here -> upload as Kaggle dataset
`eeshsaxena/biohub-zebrahub-crops` -> run the REAL Kunal UNet detector on them
(`build_zebra_dettest.py` -> kernel `biohub-zebra-dettest`, FREE) -> recall vs crop tracks @7um.
If recall>0.6 both embryos: detector transfers -> run Phase 2 (`build_zebra_edgemodel.py`) for the
DECISIVE A/B (AUC with-zebra vs comp-only on held-out competition embryos).
STATE: level-0 crop download slow (tracks CSV ~400MB/embryo; now disk-cached in .cache_*.csv).
DoG-proxy detector recall was 0.52 (weak proxy; UNet strictly stronger). LB unchanged 0.921
(quota 0 today; all prune subs 0.918-0.920 < 0.921). phase1 outputs zebra_real/; upload meta in
zebra_real_meta.json (copy as dataset-metadata.json). No submissions without user OK.

### JOINT MULTI-FRAME LINKER (08-28, `biohub-joint-cv`) — NEGATIVE, closes the last family
Hypothesis: the shipped t+2 `accel` bonus is OPTIMISTIC (rewards a link if ANY t+2 node continues
it smoothly, even one owned by another track = the steal loophole), which is why it was LB-flat.
Fix = SELF-CONSISTENT: score each link against the ACTUALLY-ASSIGNED successor and iterate
(coordinate descent on a joint multi-frame objective; does NOT decompose into per-frame Hungarians,
so the earlier "global min-cost-flow decomposes" proof does not apply).
RESULT: every arm fails. joint r1/r2/r3 = -0.0003 pooled (IDENTICAL across rounds => the refinement
converges instantly: the greedy solution ALREADY IS self-consistent). Best arm joint r2 b1.6 =
+0.0002 pooled but **-0.0007 on 44b6** => fails the both-embryo gate. Stronger bonus / wider gate
strictly worse (-0.0006 to -0.0025). Port: `build_joint_cv.py` (_link_joint + linker="jointaccel").
=> The acceleration/smoothness signal is too weak to reorder ANY assignment. The joint/global
trajectory-optimization family is CLOSED. Combined with the 4050 zebra A/B (learned edge <= cost on
novel embryos), there is NO remaining untested lever. **0.921 stands as the definitive ceiling.**

### DETECTION-SIDE SWEEPS (08-28) — BOTH NEGATIVE, closes the recall side
1. **GAP-FILL CAP** (`biohub-fill-cv`): cap .12/.16/.24 are **BIT-IDENTICAL to control (+0.0000)**
   => the 8% cap was NEVER BINDING; gap-fill already fills every gap it can find and is SATURATED
   (limited by candidate availability via gate/snap/mincand, not by budget). Widening the gap gate
   to 6um HURTS (-0.0020 pooled, -0.0027 on 6bba). mincand .05 / snap 4.5: no change or slightly
   negative. => the one historically-winning lever is fully exhausted at its shipped setting.
2. **THRESHOLD x FILL** (`biohub-thrfill-cv`): every arm loses. thr .10 does exactly what theory
   predicts -- node recall 0.9784 -> **0.9821** and raw edgeJ 0.8607 -> **0.8622** -- but ADJUSTED
   score DROPS -0.0034, because the extra nodes raise node_ratio and the 0.1x penalty eats more
   than the recall gain returns. thr .20 collapses recall to 0.9544 (-0.0016). A larger fill cap
   rescues NEITHER direction. => **thr 0.15 is provably AT THE OPTIMUM**: recall gain and
   node-ratio penalty are exactly balanced there. Ports: `build_fill_cv.py`, `build_revfill_cv.py`.
=> The DETECTION/RECALL side is now as closed as the linking side. Nothing remains untested.

### *** LB NOISE ANALYSIS (08-28) — THE KEY STATISTICAL FINDING, READ BEFORE TRUSTING ANY LB DELTA ***
GT is ~0.737% sparse: measured across 25 readable local movies, consecutive GT edges per movie =
**median 209** (mean 254, min 49, max 919). The 2 visible test movies carry only ~50 each.
If the scored test is ~4 movies (~836 GT edges), 1-sigma on J = **+-0.0104**.
**OUR ENTIRE LB SPREAD ACROSS EVERY CONFIG EVER SUBMITTED IS 0.918..0.921 = 0.003 = ~0.3 sigma.**
=> The public LB CANNOT distinguish our submissions from one another. Every "LB verdict" this
project recorded between 0.918 and 0.921 is INSIDE THE NOISE, including:
  - "prune is LB-dead (0.918 vs 0.921)"        -> no evidence either way
  - "flow k12 is worse (0.919)"                -> no evidence
  - "edge model hurts (0.920)"                 -> no evidence
  - "accel is neutral (0.920)"                 -> no evidence
**THIS INVERTS THE PROJECT'S CALIBRATION RULE.** CV comparisons are PAIRED (identical movies,
identical cached detections, ONLY the config differs), so nearly all variance cancels -> measured
run-to-run noise floor **+-0.0007**. The LB difference carries ~+-0.005. **CV has ~7x the
statistical power of the LB for ranking our configs.** The old rule "CV lies, trust only LB" was
exactly backwards: CV was right and the LB was too coarse to confirm it.
WHAT IS STILL TRUE: the leaders at 0.95+ ARE genuinely better (0.03 gap = ~3 sigma, far outside
noise). Our own internal 0.918-vs-0.921 ranking is not.
IMPLICATIONS:
  1. Do NOT spend slots trying to resolve <0.01 differences on the public LB -- it is impossible.
  2. For the 09-29 FINAL SELECTION, top-public-score is a NOISE-selection criterion. Prefer models
     that are (a) top of the LB cluster AND (b) best on the high-power paired CV, AND pick two
     STRUCTURALLY DIFFERENT mechanisms so the pair is robust to which way the noise fell.
     Current pick (both 0.921, appearance-linker `55751003` + flow-linker `55802000`) satisfies
     this: same top cluster, two different mechanisms. KEEP IT.
  3. Levers previously dismissed on LB evidence alone (prune tau.60 CV +0.0049 both embryos at
     7-sigma) were never actually disproven. They remain plausible-but-unconfirmed, not dead.
TOOLING BUILT (CPU-only, no GPU/slot): `score_local.py` scores any submission.csv against the GT
we hold for the visible test movies; `fuzz_post.py` fuzzes post-process transforms on a real
submission. Local scoring reproduced the LB ordering for prune (0.850-0.858 local vs 0.913 base),
confirming the tooling works -- but with only ~99 GT edges on 2 movies it too is +-0.03, so it is
a sanity check, not a ranker.
