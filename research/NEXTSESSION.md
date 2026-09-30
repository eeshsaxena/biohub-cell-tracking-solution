# NEXTSESSION: biohub cell tracking (refreshed 2026-09-28 06:50 UTC; supersedes the 09-27 08:15 version below)

Read this block first, then the top of `HANDOFF.md` (newest entries first). `FINAL_PICKS.md` is the pick sheet for Eesh.

## 0. ENDGAME STATE (09-28 06:50 UTC) - read this before anything else

**Every lever family is closed on the board.** Since the 09-27 version of this file: FLOWLINK (t6stk3fl) scored 0.953,
t6stk3ff2 0.952, t65s3ff 0.954 (tie); coord-inject (yuki0731, the last untested moonshot) was FALSIFIED offline (worse on
both embryos); the top-100 public sweep found nothing above 0.953; the node-neutral linker sweep found no config clearing
the bar. The exact replay AND the LOEO check both OVER-READ every climbing change (flow family: replay +9.9 / LOEO +3.0 ->
board -1). The board is the only instrument that has ever been right. A 0.02 jump is not reachable from public assets.

**Best public: 0.954** (t6r70 = representative). Board ~01:22Z 09-28: rank 356; 426 teams above 0.953; silver line rank
198 (needs ~0.956); bronze line rank 396 (we are ~40 above it on PUBLIC; on private, bronze ~= our pick beating the
x138-clone block, P ~0.48-0.65). Field still growing ~20 teams/day.

**LIVE RIGHT NOW:**
- **t65b20 = 56628029** submitted 09-28 03:47Z (t65s3 body, relink bonus 1.6->2.0; the best-evidenced node-neutral,
  fork-neutral shot from the linker sweep: replay +2.55 [+1.46,+3.72]). Score due ~10:30-11:30Z. Waiter armed.
- **t65b25** (bonus 2.5, the only neighbor beating t65b20 with 44b6 LB > 0: replay +2.93, incr +0.38 [+0.09,+0.67])
  is being pre-built + gated + visible-run (NO submit) so it is ready the same hour if t65b20 reads >= 0.955.
- Board/notebook threat watch running (`ops/watch/threat_watch.sh` -> `ops/watch/lb_trend.log`, `lb_alerts.log`).

**DECISION RULES for the t65b20 score (56628029):**
- **>= 0.955:** it becomes pick B (or A if `python ops/watch/rep_check.py` shows the representative flipped to it).
  Then submit t65b25 the same day: `python ops/run_today.py ops/plan_t65b25.json --submit-only` (only if its visible
  run GATE_PASSed). Expect only ~+0.4 board tick over t65b20; it is a confirm-the-family shot.
- **0.954 (tie):** picks unchanged; NO neighbor is worth a slot (t65b25's +0.38 replay edge is a fraction of the
  demonstrated positive-side over-read). Hold remaining slots.
- **<= 0.953:** linker-neighbor family falsified; t65b25 dead; picks unchanged.

**PICKS (Eesh sets on the web by ~09-29 12:00 UTC; re-check 22:00-23:00 UTC):** A = **t6r70 (56483584)** fixed.
B = **t65s3 (56496604)** balanced/silver-max (~0.21 silver / ~0.65 bronze) OR **ourvzl (56572442, 0.953)** bronze-max
(~0.19 / ~0.68; V1284 body hedges the dominant private risk). **09-28 06:05Z: user chose "wait for the t65b20 score"**;
bronze margin is eroding (public cushion 74 -> 28; honest bronze ~0.45-0.50), so on a t65b20 tie (0.954 or lower) RE-ASK
with ourvzl as the default and treat ourvzl as B if no answer by ~09-29 11:00Z. Never pick
xpub (0 bronze value), t6dl (== t6stk3), t6stk3fl / t6stk3ff2 (flow family, 0.953/0.952).

**SLOTS:** 09-28: 4 left (1 of 5 used on t65b20). 09-29: submit NOTHING after ~12:00 UTC (a rerun takes 6.5-7.5 h and
must FINISH before 23:59 UTC to count). Do not spend slots on ties/near-duplicates (= LB probing, banned; does not
change the finals).

**If the session restarted:** check 56628029's score first (`kaggle competitions submissions ... -v`, parse with csv -
the description field contains commas), check `data/out_t65b25/` + `ops/gate.py` for the t65b25 build state
(builder `scratch_kernels/build_t65b25.py`, gate installer `ops/add_t65b25_gate.py`), re-arm the threat watch, apply the
rules above, update HANDOFF.md.

---
(Older 09-27 08:15 version follows; sections 2-4 and 6-8 are partly stale - the block above wins on any conflict.)

## 1. Deadlines and hard rules

- **Final selection deadline: 2026-09-29 23:59 UTC.** 2 picks; Kaggle scores the better PRIVATE score of the two.
- A submission most likely has to **finish scoring** before the deadline. Our reruns take 6.5 to 7.5 h (IMGFLOW/FLOWLINK
  arms about +0.5 h). **Submit nothing after ~09-29 12:00 UTC. Set the picks on the web by ~09-29 12:00 UTC** and
  re-check them 22:00-23:00 UTC.
- 5 submissions per UTC day, shared by the whole team. Picks are set **only by Eesh (Team Leader) on the web**
  (Submissions page, tick "Use for Final Score" on exactly 2). Teammates (akkigupta2005, arunendratripathi03, swapiy)
  must not submit or tick anything.
- Standing constraints: never handle credentials/tokens; no em dashes in replies; no heavy jobs on the laptop; the
  college box (`ssh training@192.168.10.30`) is authorized for full use but NEVER kill/starve Eesh's own jobs
  (`run.py prepare test`, `run.py train`, conda envs `fs`, `rsna`, `ltx-v100`), use `nice`; never `grep -r` / `find /`;
  no Kaggle exploits or leaderboard probing with near-duplicates; update HANDOFF.md every session.
- User directive: keep researching autonomously until told to stop.

## 2. Where we stand (09-27 08:05 UTC)

- **Best public: 0.954.** Representative (highest at full precision) = **t6r70 56483584**. Public rank 295; silver line
  rank 197 (inside the 0.955 block); 359 teams above 0.953 and growing ~4/h.
- **Current picks: A = t6r70 (56483584), B = t65s3 (56496604).**
- Refreshed Monte Carlo (box `~/biohub/wf20/mc/mc2_report.txt`): with the current picks, the deadline projection is
  only ~5% silver / ~36% bronze. With **t6stk3fl as pick B** it rises to ~16% / ~54% (~27% / ~68% if t6stk3fl displays
  >= 0.956). The model gives FLOWLINK a LOEO-informed private prior (its main assumption; the verifier agent died).

### Submissions 09-26 / 09-27

| ref | arm | public | note |
|---|---|---|---|
| 56567062 | ourvz | 0.951 | V1284 y/x lookup hurts our body |
| 56567638 | t6svz15 | 0.952 | z sub-voxel gain 3 |
| 56567694 | t6svz0yx | 0.947 | y/x sub-voxel worth +7 |
| 56572442 | ourvzl | 0.953 | |
| 56578479 | t6svT15 | 0.951 | SV softmax temperature (15th SV-param arm to lose) |
| 56592284 | t6stk3ff | 0.954 | IMGFLOW repair; below t6r70 at full precision |
| 56592302 | xpubz | 0.950 | x138 body line closed |
| **56601558** | **t6stk3fl (FLOWLINK)** | **PENDING** | submitted 07:08Z, due ~14:00-15:00Z |

09-27: 3 of 5 slots used, **2 left today**. 09-28: 5. 09-29: use only early (see deadline rule).

## 3. The live lever: image flow (IMGFLOW / FLOWLINK)

- **IMGFLOW** (t6stk3ff): 3-D phase-correlation tissue flow per frame pair (8 windows, y/x 2x-binned); only in windows
  with |flow| >= 5 um and >= 5 detections, flow-inconsistent edges are re-assigned and track ends bridged (write-time
  repair). Replay +2.9, LOEO +1.15. **Board: 0.954 tie.**
- **FLOWLINK** (t6stk3fl): the same flow used inside the cell-5 motion relink (anchor = p + flow for sources in flagged
  windows); ILP untouched. Replay +9.9 vs t6stk3 (held-out +8.5), **LOEO +2.99 vs base [+0.59, +5.94]** (2.4x IMGFLOW).
  Failed its pre-registered LOEO-increment and node-count guards; **cuts division forks 6.4%** (the t6svT15 signature).
  Submitted anyway (13 slots, few candidates, strongest unseen-embryo evidence of any arm).

### Decision rules when t6stk3fl scores

- **>= 0.955**: t6stk3fl becomes pick A if the representative flips to it (run `python ops/watch/rep_check.py`),
  otherwise pick B. Spend today's 2 slots on the division-safe FLOWLINK (t6stk3fld) and FLOWLINK on the t65s3 body
  (t65s3fl) if they passed their gates.
- **0.954**: t6stk3fl probably still beats t65s3 as pick B (MC). One slot to t6stk3fld.
- **<= 0.953**: the division cut probably cost it; try t6stk3fld if it passed; otherwise keep picks and stop spending
  slots on the flow line.
- Always re-run the MC with the fresh board before finalising picks (copy `~/biohub/wf20/mc/mc_picks2.py`).

## 4. Ready and pending candidates

| tag | status | submit command (only per the rules above) |
|---|---|---|
| t6stk3ff2 | gated, visible GATE_PASS; weak (rotated-flow placebo gives 76% of its LOEO gain) | `python ops/run_today.py ops/plan_t6stk3ff2.json --submit-only` |
| t65s3ff | gated, visible GATE_PASS; DEAD after t6stk3ff tied | do not submit |
| t6r70T15 / t6r70ff | DEAD | do not submit |
| t6stk3fld (division-safe FLOWLINK) | being built by workflow **w9as2ln5r** | check its result first |
| t65s3fl (FLOWLINK on t65s3) | being built by workflow **w9as2ln5r** | check its result first |

Workflow w9as2ln5r: run id `wf_c5f2aaaf-a36`, box `~/biohub/wf21/`, scratchpad `wf21/`. If the session died, resume with
`Workflow({scriptPath: "C:\\Users\\eeshs\\.claude\\projects\\C--Users-eeshs-Downloads-biohub-cell-tracking\\c663dcfb-9cf8-4d4d-aec8-747bb3f17179\\workflows\\scripts\\biohub-flowlink-followups-wf_c5f2aaaf-a36.js", resumeFromRunId: "wf_c5f2aaaf-a36"})`
after first checking `~/biohub/wf21/` for partial work (the previous API outage left usable results on the box).

## 5. Tools

- `ops/run_today.py <plan> [--no-submit | --submit-only | --dry]`: push/run/gate/submit; refuses tags without a gate
  entry; sentinels in `ops/state/`.
- `ops/gate.py <log> <tag>`: log-marker gate. New gate entries only through installer scripts that back up gate.py and
  self-test (pattern: `ops/add_t6stk3ff_gate.py`, `ops/add_t6stk3fl_gate.py`). Pin only platform-independent values
  (Kaggle vs box float FFT digests differ).
- `ops/getlog.sh <tag> 8`: fetch a visible-run log into `data/out_<tag>/`.
- `ops/watch/rep_check.py`: passive leaderboard read (rank, representative, blocks). `ops/watch/threat_watch.sh`:
  background watch (logs to `ops/watch/lb_trend.log`, `lb_alerts.log`).
- `scratchpad/an/matchdiff.py <ref> <tags...>`: match-based edge diversity (run from the project root).
- **Exact replay harness (college box):** `~/biohub/wf13_proof` (batch1 = records for all 199 train movies;
  `status.sh`, `score_batch.sh`), fast path `~/biohub/wf16/lensA` (`ARMS="<arm>@t6stk3" bash launch.sh`,
  `score_lensA.sh`, `calib.py`). Calibrated for node-neutral linker changes (board ~= replay - 0.8, LOO RMSE 0.6);
  over-reads rawlink (+14) and image-flow repairs; blind to y/x sub-voxel changes.
- **LOEO (unseen embryo) check:** `~/biohub/wf14_alt/errbudget/verify/loeo_ff.py`, `~/biohub/wf18` `fl_loeo.py`
  (6bba-only models on 71 44b6 movies). The best available predictor for the flow family.

## 6. Background tasks (die with the session; re-arm if needed)

- FLOWLINK score waiter (b3qchn9pq): re-arm with a loop on
  `kaggle competitions submissions biohub-cell-tracking-during-development -v | grep '^56601558'`.
- Threat watch (bsqeo0znk): `timeout 3000000 bash ops/watch/threat_watch.sh` (a 07:49Z trend line was blank during a
  network outage).

## 7. Closed (do not reopen without a new mechanism)

Sub-voxel parameters (15 arms, all lost), z estimators, native centroids, V1284 head family, trilinear gathers,
edge-model and detector fine-tunes, synthetic primary, third-model fusion, divisions (gates/heads/counts), dedup/merge
(incl. image-evidence merge: -3.4), LapTrack, HOCT veto, image-NCC cue, DaXi U-Net, Trackastra, external models,
line-fit/smoothing, node-count pruning and rho calibration, retention guard, density-conditional gates, merge-tolerant
linking, output-level consensus (majority vote: worse than FLOWLINK alone), x138-body arms (xpubz 0.950), SV
temperature. Forum re-read 09-27: nothing public above 0.953; fast climbers use unpublished methods.

## 8. First steps next session

1. `python ops/watch/rep_check.py` and check 56601558 (t6stk3fl).
2. Read the w9as2ln5r result (or resume it).
3. Apply the section-3 decision rules; spend 09-27/09-28 slots only on gated candidates.
4. Re-run the pick MC; update `FINAL_PICKS.md` and HANDOFF.md; remind Eesh to set picks by 09-29 12:00 UTC.
