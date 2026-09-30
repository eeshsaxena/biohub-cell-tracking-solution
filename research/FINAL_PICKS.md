# Final picks: biohub cell tracking (team "The Originals")

Deadline: **2026-09-29 23:59 UTC**. Kaggle scores the better PRIVATE score of the 2 submissions marked
"Use for Final Score". Private scores were already computed when each submission was scored, so nothing reruns.
ourv (56544543) scored **0.951** on 09-25, so the picks are now fixed unless a later submission beats 0.954. Set them **no later than 09-29 12:00 UTC**. Re-check them at
about 22:00-23:00 UTC on 09-29.

## UPDATE 2026-09-29 14:53Z: LAST SLOT SUBMITTED = ourvzlb30t625 (56679391), scoring (expect ~21:30-23:30Z)

ourvzlb30t625 = ourvzlb25r70 + learned bonus 3.0 + relink tight 6.25 (box replay +0.64 tick on 48 train movies, both
embryos +). Decide the picks when its score is in:
* **If 56679391 displays 0.956+ OR `python ops/watch/rep_check.py` shows it as our representative** (it beat
  ourvzlb25r70 at full precision): **A = ourvzlb30t625 (56679391), B = t65b25r70 (56640601).**
* **Otherwise (it reads 0.955 below ourvzlb25r70, or lower, or is still pending at ~23:30Z):** keep
  **A = ourvzlb25r70 (56657610), B = t65b25r70 (56640601).**
B stays t65b25r70 in both cases: it is the other coordinate body (the decorrelated hedge); ourvzlb30t625 and
ourvzlb25r70 are siblings (0.8% of edges differ). Set exactly two "Use for Final Score" boxes before 23:59Z.

## UPDATE 2026-09-29 09:15Z: PICK A = ourvzlb25r70 (56657610, 0.955); PICK B = t65b25r70 (56640601, 0.954)

ourvzlb25r70 scored **0.955** and is the team representative. The recommended final pair is the top of each of our two
coordinate pipelines: **A = ourvzlb25r70 (56657610)** (V1284 y/x body) and **B = t65b25r70 (56640601)** (our sub-voxel
body). Kaggle scores the better of the two on the private board, and these two differ the most of any pair at our top
level. Swap A only if the final 09-29 submission scores above 0.955 or becomes the representative.
**Set them on the Kaggle Submissions page ("Use for Final Score", exactly two ticked) by ~12:00Z, re-check 22:00-23:00Z.**
Do not pick mixyx50r70 (0.953) or t70b20 (0.953).

## UPDATE 2026-09-28 20:05Z: PICK A = t65b25r70 (56640601); recommended B = ourvzlb25 (56640901)

t65b25r70 (0.954) is now the team representative (third climb in a row). ourvzlb25 also reached 0.954 (ourvzl was 0.953)
on the DIFFERENT V1284 coordinate body, so it is both at our best displayed score and the decorrelated hedge.
**Recommended: A = t65b25r70 (56640601), B = ourvzlb25 (56640901)** (or ourvzlb25r70 if it scores above ourvzlb25).
**Eesh 09-28 ~21:15Z: "mix both of them that will give a higher score"** -> applied as: A = t65b25r70 (main pipeline) +
B = ourvzlb25 line (second pipeline), since Kaggle scores the better of the two picks; PLUS a true single-submission
blend (y/x = 0.5*V1284 + 0.5*SV on the full stack, arm mixyx50r70) being tested offline and built only if it is no
worse than both parents. If the blend scores above both on the board, it becomes pick A or B.

## UPDATE 2026-09-28 18:57Z: PICK A = t65b25 (56639660)

t65b25 (bonus 2.5) displays 0.954 and is now the team representative, above t65b20, which was above t6r70. Under the
"go for the jump" rule: **A = t65b25 (56639660)**, **B = t65b20 (56628029)** unless tonight's t65b25r70 / ourvzlb25 /
t70b20 reads change the ordering (re-check `python ops/watch/rep_check.py`).

## UPDATE 2026-09-28 11:50Z: NEW PICK A = t65b20 (56628029)

t65b20 displays 0.954 but is now the team's representative on the public leaderboard, i.e. strictly above t6r70 at
full precision: the first arm in days to beat our previous best. **Pick A = t65b20 (56628029)** (switch to t65b25
56639660 instead if it scores and becomes the representative; check with `python ops/watch/rep_check.py`).
**EESH'S DECISION 09-28 ~11:55Z: "go for the jump"** (upside over the bronze hedge). Applied as:
- **Pick A** = whichever of t65b20 (56628029) / t65b25 (56639660) is the team representative at full precision.
- **Pick B** = the other of that pair, if it displays >= 0.954; otherwise t6r70 (56483584).
Both picks ride the only line that has climbed on the board. Declined hedge: ourvzl (56572442), the decorrelated
V1284-body arm (+~0.03 bronze). Honest cost: the two picks are siblings, so they rise and fall together on the
hidden embryos; bronze is less protected (public cushion was ~12 places at 11:45Z 09-28).

## UPDATE 2026-09-27 (superseded by the 09-28 block above)

Pick A is fixed: **t6r70 (56483584)**. Pick B is a risk-preference choice, both arms already submitted (no slot needed):
- **B = t65s3 (56496604)** = BALANCED (silver-max): ~0.21 silver / ~0.65 bronze. Keeps the silver lottery; max diversity within our body.
- **B = ourvzl (56572442, 0.953)** = BRONZE-MAX: ~0.19 silver / ~0.68 bronze. Only proven arm on the V1284 coordinate body, so it hedges the dominant private risk (our pipeline losing to the x138 clone block). +0.03 bronze vs t65s3, robust in sign; costs 0.01-0.03 silver.
Do NOT pick xpub (0 bronze value on the current field), t6dl (==t6stk3), or t6stk3fl (flow family closed on the board 09-27).
Honest odds at the deadline: silver ~5-25% (needs ~0.956 we do not have), bronze ~48-65%.
**09-28 06:00Z UPDATE:** the field is growing 4.3 teams/h past 0.953 (445 now, projected ~626 at close); our public
margin above the bronze line is down to 28 places (74 -> 40 -> 28). That lands in the Monte Carlo's "hard" band, so the
honest bronze read is now ~0.45-0.50. This strengthens **B = ourvzl (56572442)**: it is the only pick-side lever that
raises P(bronze) (+0.03, robust in sign), and the silver longshot t65s3 preserves is now worth less than that hedge.
Pending exception: if t65b20 (56628029, scores ~10:30-11:30Z 09-28) reads >= 0.955, it becomes B (or A).
**Eesh's decision 09-28 06:05Z: wait for the t65b20 score.** If it reads 0.954 or lower, the default B is **ourvzl
(56572442)** unless Eesh says otherwise before ~09-29 11:00Z. A 0.02 jump is not reachable from public assets (no top-100 team published a pipeline >0.953). One moonshot under validation: yuki0731 coord-inject (171-movie retrained head + z-refiner, CC0); it may touch a pick ONLY if it clears an LOEO-positive, node-neutral bar.
The single most important act: set exactly two "Use for Final Score" boxes on the web by 09-29 12:00Z, re-check 22:00-23:00Z.

## What to select

**Pick A: 56483584 (t6r70, public 0.954).** It is the team's representative entry on the leaderboard: strictly
above t6stk3 at full precision and at least equal to t65s3 and t6sr.

**Pick B: 56496604 (t65s3, public 0.954).** ourv scored 0.951, so the fallback applies: t65s3 is the 0.954 arm least
correlated with pick A (3.8% of edges differ at 3 um vs 2.0% for t6stk3). 56535504 (t6sr) is an equal alternative.
If a later submission scores 0.955 or higher, it replaces pick B (and pick A if it beats t6r70 at full precision);
HANDOFF.md records any such change.

Monte Carlo (20k draws, scratchpad wf3/mc_silver): realistic P(silver) is about 0.45-0.55 with this pair.
Silver is NOT guaranteed by beating the x138 block: some tied teams escape above it with a different second
pick, and ~20 teams/day are climbing above 0.953.

## What NOT to select

* **xpub (56535352)** or any 0.953 submission from the x138 notebook family. About 200 teams run that exact
  pipeline; Kaggle breaks exact ties by EARLIER submission (verified: the 0.953 block is ordered by submission id),
  so xpub would sit about 188th of ~202 identical runs (public rank ~352). It adds 0 to the chance of silver.
  *Only exception, a deliberate trade:* if ourv reads 0.952 or lower and you would rather lock a bronze floor,
  xpub as pick B trades about 0.035 of silver probability for +0.07 to +0.30 of bronze probability. Default: t65s3.
* **t6dl (56543692).** Byte-identical output to t6stk3; its deadline guard adds nothing because scores are fixed.
* **t6stk3 (56467741) together with t6r70.** They differ on only 2% of edges, so they rise and fall together.

## How to set them (web only, the CLI cannot do it)

1. Open the competition page, then **Submissions** (My Submissions).
2. Tick **Use for Final Score** on exactly pick A and pick B, untick everything else.
3. Reload the page and confirm exactly two are ticked.

If only one is ticked, Kaggle fills the other with the best public score (t6r70). If none are ticked, Kaggle
auto-picks the top 2 public scores, which today would be two submissions from the same body (the weaker pair).
Kaggle's docs give selection rights to the **Team Leader**; Eesh should set and confirm the picks himself.

## Medal lines

Silver = top 5% of RANKED teams at the close (floor(0.05 x N)); today N = 3,896 -> rank 194, expected about
197-201 by the deadline as new teams keep arriving. Bronze = top 10%.

## For teammates (akkigupta2005, arunendratripathi03, swapiy)

Please do not submit, tick or untick anything until the deadline. The 5 daily submissions are shared by the whole
team, and changing the ticked finals can cost the silver medal. If you already ticked something, tell Eesh.
