"""Pre-submit gate for a FAST-base arm: python gate.py <kernel.log> <tag>. Exit 0 = GATE_PASS, 1 = GATE_FAIL.
Reference = hfusion test output after tight55 (what v_hfast prints): FINAL 25637/20721/6152/70284; 64 fallback frames on
44b6_0b24845f, 1 on 6bba_05b6850b, 0 on the other two. Arms that intend to move counts get per-arm windows below."""
import json, re, sys
REF = {"44b6_0113de3b": 25637, "44b6_0b24845f": 20721, "6bba_05b6850b": 6152, "6bba_05db0fb1": 70284}
REF_FB = {"44b6_0b24845f": 64, "6bba_05b6850b": 1}
log, tags = sys.argv[1], sys.argv[2].split(",")  # stacks: pass the member arms, e.g. prim300,ret80f
raw = open(log, encoding="utf-8").read()
try: txt = "".join(e.get("data", "") for e in json.loads(raw))
except Exception: txt = raw
pred_end = txt.find("Prediction completed")
final = {}
for d, n in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes", txt):
    if d in REF and d not in final: final[d] = int(n)
fb = {}
for m in re.finditer(r"BIOHUB_RETENTION_GUARD (\{.*?\})", txt):
    r = json.loads(m.group(1))
    if r["dataset"] in REF: fb.setdefault(r["dataset"], set()).add(r["frame"])
fb = {d: len(v) for d, v in fb.items()}
fails = []
if set(final) != set(REF): fails.append(f"missing FINAL for {sorted(set(REF) - set(final))}")
# ourv / ourvg*: V1284's moved centres make the ILP keep fewer nodes. Verified 09-25: ourv's RAW ILP node
# counts equal xpub's (the public x138 pipeline, board 0.953) on all four movies (25817/20206/6239/69515),
# so the -10.7% on 44b6_0b24845f is the head's known effect, not a silent failure. Every other check stays.
# ourvg15 (V1284 x1.5): 44b6_0b24845f FINAL 15,635 (-24.5%). Raw ILP nodes fall monotonically with the shift
# (22,478 sub-voxel -> 20,206 x1.0 -> 17,225 x1.5), no traceback, gain marker present, placeholder recall intact
# (51/51) - a dose effect at the ILP stage. ourvg20 stays at 0.15: at x2.0 annotated recall drops (47/51).
tol = max({"ourvzlb30t600": 0.15, "ourvzlb40t625": 0.15, "ourvzlb35t625": 0.15, "ourvzlffb30": 0.15, "ourvzlb30t625": 0.15, "ourvzllf100": 0.15, "ourvzlsr": 0.15, "ourvzlb20": 0.15, "ourvzlb30": 0.15, "ourvzlt675": 0.15, "ourvzlt625": 0.15, "ourvzlb25r70ff": 0.15, "t65b25r70ffsr": 0.15, "t65b25r70sr": 0.15, "t65b25r70ff": 0.15, "ret80f": 0.15, "ret70f": 0.20, "synp": 0.15, "ourv": 0.13,
           "ourvg13": 0.15, "ourvg15": 0.25, "ourvg20": 0.15, "ourvr": 0.15, "ourvrd": 0.15, "ourvz": 0.15, "ourvzl": 0.15, "ourvzlb25r70": 0.15, "mixyx50r70": 0.15, "t675b25": 0.15, "t65b20d04": 0.15, "t70b25": 0.15, "t70b20": 0.15, "ourvzlb25": 0.15, "t65b25r70": 0.15, "t65b25": 0.15, "t65b20": 0.15, "t6svT15": 0.15, "t6r70T15": 0.15, "t6svz05": 0.15, "t6svx125": 0.15, "t6svz15": 0.15, "t6svz0yx": 0.15, "t6svyx": 0.15}.get(t, 0.10) for t in tags)
for d, n in final.items():
    if abs(n - REF[d]) / REF[d] > tol: fails.append(f"{d} FINAL {n} vs {REF[d]} (> {tol:.0%})")
for d, n in fb.items():
    if n > max(3 * REF_FB.get(d, 0), 20): fails.append(f"fallback explosion {d}: {n} frames (ref {REF_FB.get(d, 0)})")
need = {"prim300": [r"PRIMARY SWAPPED sha256: 12b5d32a"], "prim300s70": [r"PRIMARY SWAPPED sha256: 12b5d32a"],
        "tta8z": [r"TTA_ZFLIP_ACTIVE"], "ret80f": [r"guard applied at 0\.80"], "ret70f": [r"guard applied at 0\.70"],
        # hsz0: APPLIED offset must be exactly 0 AND the RAW pre-gain mean must be non-zero, otherwise the
        # "estimator still fired, only the applied offset is zero" claim is unproven and the run is just
        # sub-voxel-off wearing the arm's name.
        "hsz0": [r"SV_ARM_HSZ0 nodes=\d+ mean_abs_off_vox=0\.0000 mode=zero raw_mean_abs_off_vox=0\.\d*[1-9]"],
        "hspin": [r"SV_ARM_HSPIN nodes=\d+ .*clip_zyx=0\.4999,0\.1249,0\.1249 .*written_delta_bound=0"],
        # hsadapt: the estimator must have fired (raw_abs_off > 0) AND a non-zero offset must survive the
        # gain+clip (mean_abs_off_vox > 0). Without this the run is the 0.947 base wearing the arm's name.
        "hsadapt": [r"SV_ARM_HSADAPT nodes=\d+ gain_zyx=\d\.\d{3},\d\.\d{3},\d\.\d{3} "
                    r"raw_abs_off=0\.\d*[1-9]\d* mean_abs_off_vox=0\.\d*[1-9]"],
        # hsg200 / hsg050 / hswin2 rename the marker away from SUBVOXEL_ACTIVE, so without an entry here the
        # gate would pass a run whose sub-voxel block silently did nothing. Each pattern pins the arm's own
        # knob (gain 2.00 / gain 0.50 / win=5) AND demands a non-zero mean offset.
        "hsg200": [r"SV_ARM_HSG200 nodes=\d+ mean_abs_off_vox=0\.\d*[1-9]\d* frac_clipped=\d\.\d{4} gain=2\.00"],
        # hsg3c04 is the matched-magnitude SHAPE arm: gain 3.00 with clip 0.40 is meant to land on
        # hsg200's mean |offset| while saturating far more often. Its silent-failure twin is hsg300
        # (gain 3.00, clip 0.4999), which is already on the board at 0.949, so the gain alone proves
        # nothing. The arm therefore prints its live clip and this pattern pins BOTH knobs.
        "hsg3c04": [r"SV_ARM_HSG3C04 nodes=\d+ mean_abs_off_vox=0\.\d*[1-9]\d* frac_clipped=\d\.\d{4} "
                    r"gain=3\.00 clip=0\.4000"],
        # hsg175 is hsg200 with gain 1.75 at the same 0.4999 clip; pinning gain=1\.75 here is what stops a build
        # that silently kept 2.00 (or lost the patch) from passing under the new name. The clip is NOT printed in
        # the log line, so it cannot be gated: verify it in the notebook source (BIOHUB_SUBVOXEL_CLIP = '0.4999').
        "hsg175": [r"SV_ARM_HSG175 nodes=\d+ mean_abs_off_vox=0\.\d*[1-9]\d* frac_clipped=\d\.\d{4} gain=1\.75"],
        # hsg250 is hsg200 with gain 2.50 at the same 0.4999 clip. Same reasoning as hsg175: pin gain=2\.50 so a
        # build that silently kept 2.00, or lost the patch entirely, cannot pass under the new name. The clip is
        # not printed, so check it in the notebook source (BIOHUB_SUBVOXEL_CLIP = '0.4999').
        "hsg250": [r"SV_ARM_HSG250 nodes=\d+ mean_abs_off_vox=0\.\d*[1-9]\d* frac_clipped=\d\.\d{4} gain=2\.50"],
        # hsg2c04 is hsg200 with the clip tightened 0.4999 -> 0.4000 and the SAME gain 2.00, so the gain alone
        # cannot tell the two apart in a log. Its marker line therefore prints the live clip as well, and this
        # pattern pins gain=2\.00 AND clip=0\.4000: a build that renamed the marker but kept 0.4999 fails here.
        "hsg2c04": [r"SV_ARM_HSG2C04 nodes=\d+ mean_abs_off_vox=0\.\d*[1-9]\d* frac_clipped=\d\.\d{4} "
                    r"gain=2\.00 clip=0\.4000"],
        # hsgzc10 is hsg200 with a PER-AXIS clip (z, y, x) = (1.0000, 0.4999, 0.4999) at the SAME gain 2.00,
        # so the gain alone cannot tell it from hsg200 (0.951) in a log, and a build that lost the new env var
        # would silently fall back to the scalar 0.4999 and reproduce hsg200 under a new name. The marker line
        # therefore prints the live clip vector, and this pattern pins gain=2\.00 AND clip_zyx=1,0.4999,0.4999
        # AND a non-zero z component of mean_abs_off_zyx (the z channel is the whole point of the arm).
        "hsgzc10": [r"SV_ARM_HSGZC10 nodes=\d+ mean_abs_off_vox=0\.\d*[1-9]\d* frac_clipped=\d\.\d{4} "
                    r"gain=2\.00 clip_zyx=1\.0000,0\.4999,0\.4999 frac_clipped_zyx=[\d.,]+ "
                    r"mean_abs_off_zyx=0\.\d*[1-9]\d*,"],
        "hsg050": [r"SV_ARM_HSG050 nodes=\d+ mean_abs_off_vox=0\.\d*[1-9]\d* gain=0\.50 "
                   r"raw_abs_off_vox=0\.\d*[1-9]\d*"],
        "hswin2": [r"SV_ARM_HSWIN2 nodes=\d+ mean_abs_off_vox=0\.\d*[1-9]\d* win=5 frac_clipped=\d\.\d{4}"],
        # --- motion-relink / linker arms (lcvel2, lcbonus2, lcflow2), all rebased onto the 0.951 hsg200 body ---
        # These change the LINKER, not the sub-voxel block, so each one logs TWO markers: its own ARM_<TAG> line
        # (which arm) and the untouched SV_ARM_HSG200 line (which body). The body half is enforced through
        # sv_mark below, which is what stops a linker arm accidentally built on the old 0.949 hsoftfix body, or
        # on the 0.946 no-refinement body, from passing under a 0.951-rebase name.
        # The ARM_ half alone is NOT enough: cell 0 prints its marker right beside the os.environ assignment, so
        # the print fires even if nothing downstream ever reads the variable. Where the notebook echoes the
        # realized value in CONFIG_DISPLAY (cell 2), the pattern therefore pins that echo as well. The echo is
        # read out of the live global after the float() conversion, so it is the first evidence that the knob
        # actually reached the linker rather than just the environment.
        "lcvel2": [r"ARM_LCVEL2 velocity_weight=0\.25",
                   r'"motion_relink_velocity_weight": 0\.25'],
        "lcbonus2": [r"ARM_LCBONUS2 learned_bonus=1\.6",
                     r'"motion_relink_learned_bonus": 1\.6'],
        # lcflow2 has no env knob to echo: it replaces the velocity estimator inside motion_relink_edges and adds
        # three LC_FLOW_* constants in cell 2. Its silent-failure mode is therefore different from the other two.
        # The new estimator can be fully present and still never fire, because it needs LC_FLOW_MIN_SAMPLES=4
        # seeded neighbours within LC_FLOW_RADIUS_UM=40; on a sparse movie every source can fall back to the
        # base's own-step prediction, in which case the run IS hsg200 wearing the arm's name. So require
        # flow_seeded to be non-zero, not merely present, alongside the marker and the new config keys.
        "lcflow2": [r"ARM_LCFLOW2 frames=\d+ flow_seeded=[1-9]\d* self_fallback=\d+ none=\d+",
                    r'"lc_flow_k": \d+', r'"lc_flow_radius_um": \d'],
        # lcefr is the first arm that changes what the MODEL is shown rather than how its output is
        # re-weighed, so its silent-failure mode is different again from the three above. It has no cell-2
        # config echo to pin: the switch is an env var set in cell 4 (BIOHUB_LINKER_REFINED_COORDS) and the
        # prediction runs in SUBPROCESS workers launched later in that same cell. The "patch applied" line is
        # printed by the notebook process at patch time, so it proves the source edit landed but says nothing
        # about whether the workers ever saw the variable. If the variable does not reach them, _LC_ON is False
        # in the worker, the arm degrades to plain hsg200, and the notebook's own no-op guard CANNOT catch it
        # because that guard lives inside `if _LC_ON`. The per-video counter line is therefore the only real
        # evidence, and it is required here with non-zero pairs/nodes/diff_nodes and a non-zero mean offset:
        # diff_nodes counts node slots whose position the linker actually received refined, so a zero there
        # would mean the linker was handed the integer peaks after all.
        "lcefr": [r"ARM_LCEFR patch applied to ",
                  r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                  r"mean_abs_off_vox=0\.\d*[1-9]"],
        # --- STACKS of the three cleared linker arms, and the two LIMIT arms, all on the 0.951 hsg200 body ---
        # A stack's danger is PARTIAL application: if one component silently drops out, the run is a cheaper
        # arm wearing the stack's name and the tie-break reads as a false null. Every component is therefore
        # gated separately and by the SAME evidence the single-arm entries use, never by the stack marker
        # alone. Each arm's own ARM_ markers are unique strings, so a sibling's log can never satisfy them.
        #   velocity / bonus: the cell-0 print fires beside the os.environ assignment and proves nothing on
        #   its own, so the cell-2 CONFIG_DISPLAY echo of the realized float is pinned too (same reasoning as
        #   lcvel2 / lcbonus2 above). NOTE the echo is json.dumps of a float: 0.00 prints as 0.0, not 0.00.
        #   lcefr: pinned with its runtime per-video counter line, not just "patch applied", because the
        #   switch has to survive into the subprocess workers (see the lcefr note above).
        "stk3": [r"ARM_STK3V velocity_weight=0\.25", r"ARM_STK3B learned_bonus=1\.6",
                 r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                 r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                 r"ARM_LCEFR patch applied to ",
                 r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                 r"mean_abs_off_vox=0\.\d*[1-9]"],
        # stkve is stk3 without the bonus change, so the bonus echo is pinned at the BASE value 1.0: that is
        # what stops a run whose lcbonus2 edit leaked in from passing as the two-component arm.
        "stkve": [r"ARM_STKVEV velocity_weight=0\.25",
                  r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                  r'"motion_relink_learned_bonus": 1\.0(?!\d)',
                  r"ARM_LCEFR patch applied to ",
                  r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                  r"mean_abs_off_vox=0\.\d*[1-9]"],
        # stkvb is stk3 without lcefr. It must NOT carry the lcefr counter line; that is checked negatively
        # below, because `need` can only express required patterns.
        "stkvb": [r"ARM_STKVBV velocity_weight=0\.25", r"ARM_STKVBB learned_bonus=1\.6",
                  r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                  r'"motion_relink_learned_bonus": 1\.6(?!\d)'],
        # lcvel0 drives the velocity weight to exactly 0.00, which makes `predicted` equal `source_pos` and
        # is therefore indistinguishable in behaviour from "the knob never reached the linker at all". The
        # cell-2 echo is the only thing that tells those two apart, so it is mandatory here and the negative
        # lookahead matters: without it the pattern would also match a 0.05 or 0.0625 echo.
        "lcvel0": [r"ARM_LCVEL0V velocity_weight=0\.00",
                   r'"motion_relink_velocity_weight": 0\.0(?!\d)'],
        "lcbon22": [r"ARM_LCBON22B learned_bonus=2\.2",
                    r'"motion_relink_learned_bonus": 2\.2(?!\d)'],
        # t60h: the single relink-gate change 5.5 -> 6.0 on the 0.951 body. Pin the live config echo, not just the
        # marker, so a run that silently kept 5.5 cannot pass.
        "t60h": [r"ARM_T60H tight_um=6\.0",
                 r'"motion_relink_tight_um": 6\.0(?!\d)'],
        # t65h: the next relink-gate bracket (6.5) on the 0.951 body; run only if t60h reads >= 0.952.
        # t6stk3: the two 0.952 arms stacked = stk3 (velocity 0.25 + bonus 1.6 + lcefr) + t60h (tight 6.0). All four must fire.
        "t6stk3": [r"ARM_STK3V velocity_weight=0\.25", r"ARM_STK3B learned_bonus=1\.6",
                   r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                   r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                   r"ARM_T60H tight_um=6\.0",
                   r'"motion_relink_tight_um": 6\.0(?!\d)',
                   r"ARM_LCEFR patch applied to ",
                   r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                   r"mean_abs_off_vox=0\.\d*[1-9]"],
        # --- 09-24 X138 MERGE ARMS ------------------------------------------------------------------
        # Body = the PUBLIC notebook anvithpothula/biohub-x138 (LB 0.956, rank 57): neighbourhood-flow
        # motion relink (seed mode, k=12 within 40 um), sub-threshold readmit and a low-detection gap
        # filler. Its V1284 learned coordinate head is REMOVED (it needs a private dataset we cannot
        # mount), and our own board-proven sub-voxel refinement takes that slot. Each arm must prove all
        # THREE of x138's mechanisms fired live, not just that the env was set, because a silent
        # "gap filler idle" would leave the arm scoring as plain x138-minus-V1284.
        # --- 09-24 second round: single env moves on the merged body. Each one is a lever with TWO
        # independent sources: thtennant (rank 32, 0.959) shipped a public notebook for it, and for
        # tight 6.0 our own board already paid a tick for it on our body. ARM_XENV is read back from
        # os.environ at runtime, so it pins which build ran even for knobs the config dict never echoes.
        # --- 09-24 DIVISION-GATE ARMS. Measured from our own 0.954 run_stats, the safe-division
        # funnel on the 4 visible movies is: 4105 candidates killed by the DIVERGENCE gate, 445 of
        # 627 geometric survivors killed by the DeepCenter veto, 396 by mutual-NN, 91 by sister
        # symmetry, 79 divisions finally written, frac caps NOT binding (0 skipped). Divergence and
        # the DeepCenter veto are the two gates worth a slot; each arm moves exactly one of them.
        # Neither knob is echoed by the pipeline's config dict, so ARM_XENV is the proof for
        # xsvdv and the echo is a cross-check for xsvdc.
        # --- 09-24 second division round. xsvdv (+25 divisions) and xsvdc (+52) both worked and attack
        # DIFFERENT gates: xsvdv widens the geometry so more candidates REACH the DeepCenter veto,
        # xsvdc widens the veto so more of the same candidates SURVIVE it. xsvdd stacks them (the
        # super-additivity pattern that took us 0.951 -> 0.954), xsvd10 is the next rung on the veto,
        # xsvwz loosens the veto a different way (isotropic score window instead of a lower threshold),
        # and xsvmx moves the parent-to-daughter cap, the knob a public account measured a tick for at
        # 7 -> 9. Each pins the OTHER division knobs at their shipped values so the arms cannot be
        # confused for one another.
        # --- 09-24 third round, driven by the rank-57 team's OWN experiment log (the env comments of
        # the public notebook anvithpothula/biohub-x56, cross-checked against rogerrogerroger3r):
        #   * 'kimi-v18 LB sweep peaked ~4.0-4.5' for SAFE_DIV_DIVERGE_UM, and larger is STRICTER.
        #     That is the OPPOSITE direction to our xsvdv (1.50). xsvdu tests their peak.
        #   * 'Ground-truth parent-daughter links reach 10.4um; a 7um cap rejected ~25% of real links'
        #     so 9.0 still clips real divisions and 10.5 admits all of them. xsvmp, not xsvmx's 11.0.
        #   * The adaptive short-track rescue is DEAD CODE here: its trigger defaults to 0.10 and our
        #     removed fractions are 0.98/7.7/2.1/0.9 percent, so the five rescue knobs x138 ships are
        #     all inert. xsvsr arms it. It also makes the kernel DETERMINISTIC on a hidden rerun,
        #     because 44b6_0b24845f at 7.7 percent is close enough to 0.10 that slightly worse
        #     detection would arm the block on that movie alone.
        # --- 09-24: the ONE pair anyone has publicly measured as POSITIVE on this lineage.
        # rogerrogerroger3r paid for the clean test: DEEPCENTER_SAFE_DIV_THRESHOLD 0.26 ALONE scored
        # 0.941 (no change), and 0.26 TOGETHER WITH GAP_CLOSE_UM 5.0 -> 5.8 scored 0.942. xsvgc is the
        # gap half alone, xsvp26 is the pair. NOTE: '"gap_close_um": 5.8' appears in EVERY log of this
        # pipeline because it is one of the PP_CANDIDATES the sweep defines but does not select, so it
        # is USELESS as a marker; ARM_XENV is the only proof that 5.8 is the live value.
        'xsvgc': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            '"safe_div_max_um": 9\\.0(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvgc BIOHUB_GAP_CLOSE_UM=5\\.8',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
        ],
        'xsvp26': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            '"safe_div_max_um": 9\\.0(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvp26 BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD=0\\.26 BIOHUB_GAP_CLOSE_UM=5\\.8',
            '"deepcenter_safe_div_threshold": 0\\.26(?!\\d)',
        ],
        'xsvdu': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvdu BIOHUB_SAFE_DIV_DIVERGE_UM=4\\.0',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
            '"safe_div_max_um": 9\\.0(?!\\d)',
        ],
        'xsvmp': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvmp BIOHUB_SAFE_DIV_MAX_UM=10\\.5',
            '"safe_div_max_um": 10\\.5(?!\\d)',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
        ],
        'xsvsr': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvsr BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=0\\.0',
            '"safe_div_max_um": 9\\.0(?!\\d)',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
        ],
        # --- xsvmax: the stack of everything the measurements say is independent and cheap.
        # DIVERGE 1.50 (candidate pool 610 -> 1061) + DeepCenter veto 0.15 (acceptance 161/449 ->
        # 325/285) together write 168 divisions for +80 nodes and +157 edges, and the short-track
        # rescue adds 355 nodes / 274 edges while touching ZERO divisions, so the two act on
        # disjoint parts of the graph. Built ahead of the scores so it can be submitted the moment
        # the division direction is known, without waiting out a 15-minute run plus a log fetch.
        # --- INSURANCE ARMS ON OUR OWN 0.954 BODY (v_t6stk3), built 09-24, NOT pushed yet.
        # add_safe_divisions_postlink is byte-identical between our body and the merged x138 one,
        # so if the merged body loses, these re-ask the same division question on the body that
        # is actually winning, without costing a day to build. They inherit t6stk3's four stack
        # markers plus lcefr unchanged, so those pin the BODY while ARM_XENV pins the knob.
        # --- two more insurance arms on our own body: the cheapest division gain measured
        # anywhere (WIN_Z 1->2 bought +5 divisions for ZERO nodes on the merged body) and the
        # rescue, which our body needs for DETERMINISM as much as for score.
        # --- synp: the PRIMARY unet_transformer checkpoint replaced by bhpepper's public 5-fold
        # SYNTHETIC-PRETRAINED SWA ensemble. The competition discussion is unanimous that
        # post-processing on the frozen public weights is saturated and that pretraining on the
        # public CC0 synthetic set is the only model-side lever anyone reports working
        # (hikaggler: +0.012-0.018 on a 24-video hold-out, the only big lever in three weeks).
        # Verified LOCALLY before building: the checkpoint shares all 136 state-dict keys and every
        # shape with the support-pack primary, with mean |delta| 0.98, so it is a true drop-in and a
        # genuinely different model. The kernel re-checks keys, shapes and delta at runtime and
        # raises rather than silently running the wrong weights.
        # CAVEAT ON THE PRIOR: bhpepper themselves are rank 154 at 0.950, BELOW our 0.954, so this
        # is a genuine test and not a sure thing. Our own prim300 (a different public primary) lost
        # 4 ticks. What makes this one worth a slot is the training REGIME, not the author's rank.
        # --- xpub: anvithpothula/biohub-x138 run VERBATIM, with its V1284 learned coordinate head
        # mounted. That head is PUBLIC (anvithpothula/biohub-v1284-head-s075, 30 KB, 153 downloads,
        # 4 votes). Yesterday I recorded it as private and spent five slots on a body with our own
        # sub-voxel refinement substituted for it (0.951). The error: `kaggle kernels pull -m`
        # returns the dataset_sources list with that entry as an EMPTY STRING, and I read the blank
        # as a redacted private dataset instead of checking the dataset search. ALWAYS run
        # `kaggle datasets list -s <slug>` before concluding an artefact is unavailable.
        # This arm has NO sub-voxel block, so SV_ARM_HSG200 must NOT appear; `forbid` enforces that.
        'xpub': [
            # NOTE: our identity line lives in cell 0 but V1284_MODE is set in cell 4, so it
            # necessarily prints 'unset'. That is a defect in the line, not in the arm - the
            # real proof that the head ran is the V1284 block's own print on the next line.
            'ARM_XENV tag=xpub V1284=unset',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'ILP timeout patch applied',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.0(?!\\d)',
        ],
        'synp': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_XENV tag=synp SYNPRIM=biohub-synthetic-5fold-ensemble-v1',
            'SYNPRIM SWAPPED \\[synp\\]: .*synthetic_5fold_swa\\.pth',
            'SYNPRIM SWAPPED sha256: [0-9a-f]{16}',
            'SYNPRIM SWAPPED mean_abs_delta=[0-9]+\\.[0-9]+',
            "SYNPRIM SWAPPED config: \\{'unet_out_channels': 32",
        ],
        # --- ddsr: the short-track rescue armed AND co-located node de-duplication at 5.0 um.
        # This is the first arm this project has ever validated END TO END before spending a slot.
        # Against the REAL ground truth of the four scored movies (2,127 dt==1 GT edges, recovered
        # from the train split), replayed IN-KERNEL on the box from the 0.954 run's own raw ILP
        # geffs:  base J=0.95722 TP=2036 nodes=122,863  ->  ddsr J=0.96004 TP=2042 nodes=121,737.
        # +6 true-positive edges, 1,126 FEWER nodes, and FP stays 0 on every movie. Both terms move
        # the right way because the node-count penalty is signed.
        # Safety check that had to pass first: across 1,479 merge clusters absorbing 1,498 nodes,
        # ZERO swallow two distinct annotated cells, so 5.0 um is below real inter-cell spacing
        # everywhere we can see. The out-degree cap in the block is what stops the merge inventing
        # divisions (naive rewiring took them 79 -> 656 and faked +0.005 of J).
        # --- t6dl: our 0.954 body plus a RERUN DEADLINE GUARD. Not a score arm.
        # The data description says the visible test/ movies are example copies of train and that
        # a NEW HIDDEN TEST SET roughly the size of the TRAINING SET (199 movies) is swapped in on
        # rerun. Our visible run is 4 movies with 9 minutes of prediction, so the rerun is ~50x
        # that against a 12-hour ceiling, and this body has never carried any wall-clock guard,
        # while the x138 lineage ships one (REPAIR_DEADLINE_S 27000 plus a degrade path).
        # A timeout on the FINAL submission scores nothing, which is worse than losing a tick.
        # The guard must be a strict NO-OP under the deadline, so this arm is expected to score
        # EXACTLY what t6stk3 scores; the gate therefore demands degraded=0 and fallback=0 on the
        # visible run. If either is 1 here, the guard is firing when it should not and the arm is
        # void rather than informative.
        # --- ourv: our 0.954 linker stack (velocity 0.25, bonus 1.6, TIGHT 6.0) with x138's PUBLIC
        # V1284 learned coordinate head in the slot our sub-voxel soft-argmax used to fill. On the
        # x138 body the only difference between xsv (0.951, ours) and xpub (0.956, its author's
        # reading) is which of the two refinements fills that slot. lcefr goes too, because V1284
        # swaps in a trilinear _index_features that already feeds refined coords to the edge model.
        # Anchors verified: all of our cell-4 patches apply with count 1 against the real support-
        # pack predictor, and all four V1284 anchors still match exactly once afterwards.
        'ourv': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_XENV tag=ourv V1284_HEAD=mounted SUBVOXEL=removed',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
        ],
        # --- ourvg<NN>: ourv with the V1284 displacement multiplied by a gain (regressor shrinkage;
        # our own sub-voxel refinement peaked on the board at gain 2.0). The notebook re-reads the
        # written module and raises unless the gain expression is in it, then prints the marker.
        'ourvg15': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_XENV tag=ourvg15 V1284_HEAD=mounted SUBVOXEL=removed V1284_GAIN=1\\.5',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_GAIN gain=1\\.5 module_patched=1',
        ],
        'ourvg20': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_XENV tag=ourvg20 V1284_HEAD=mounted SUBVOXEL=removed V1284_GAIN=2\\.0',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_GAIN gain=2\\.0 module_patched=1',
        ],
        'ourvg13': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_XENV tag=ourvg13 V1284_HEAD=mounted SUBVOXEL=removed V1284_GAIN=1\\.3',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_GAIN gain=1\\.3 module_patched=1',
        ],
        # --- ourvr: ourv with the V1284 head RETRAINED on ~60 train movies (kernel_sources
        # eeshsaxena/biohub-v-v1284cap). The notebook refuses the public head and checks the format.
        'ourvr': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=ourvr V1284R=retrained base=ourv V1284_HEAD=mounted SUBVOXEL=removed',
            'ARM_V1284R head=retrained path=/kaggle/input/[^ ]*v1284_head_retrained\\.pt sha256=f7966cc607f2374d',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
        ],
        # --- ourvrd: ourvr (retrained head) with the shift x0.8325, which matches the public head's mean
        # shift (0.85 um) so the arm tests direction quality alone. Built from v_ourvg083 via build_ourvr.py.
        'ourvrd': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=ourvrd V1284R=retrained base=ourvg083 V1284_HEAD=mounted SUBVOXEL=removed V1284_GAIN=0\\.8325',
            'ARM_V1284R head=retrained path=/kaggle/input/[^ ]*v1284_head_retrained\\.pt sha256=f7966cc607f2374d',
            'ARM_V1284_GAIN gain=0\\.8325 module_patched=1',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
        ],
        # --- ourvz: V1284 head for y/x only + our sub-voxel soft-argmax for z only, t6 linker stack, no lcefr.
        # The predictor prints SV_ARM_HSG200 with a z-only mean offset (smaller than t6stk3's) and the module
        # re-read proves the z-zero line is in the written source.
        'ourvz': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=ourvz V1284_HEAD=mounted SUBVOXEL=z-only V1284_AXES=yx',
            'ARM_SV_ZONLY=1',
            'SUBVOXEL patch applied to',
            'SV_ARM_HSG200 nodes=\\d+ mean_abs_off_vox=0\\.\\d+ frac_clipped=',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
        ],
        # --- t6svyx: t6stk3 with the sub-voxel soft-argmax on y/x ONLY (z offsets zeroed before the clip), lcefr
        # kept, gain 2.00 clip 0.4999, velocity 0.25 / bonus 1.6 / TIGHT 6.0 unchanged. Mirror of ourvz. The predictor
        # prints its own per-axis means (z must be exactly 0, y/x non-zero) and the per-movie SV_ARM_HSG200 numbers
        # must equal t6stk3 minus ourvz (bit-deterministic offsets computed from the integer peaks).
        't6svyx': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_XENV tag=t6svyx SUBVOXEL=yx-only LCEFR=kept GAIN=2\\.00 CLIP=0\\.4999',
            'ARM_SV_YXONLY=1',
            'SUBVOXEL patch applied to',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=(?:0\\.092|0\\.093|0\\.094|0\\.095|0\\.096|0\\.097|0\\.098)\\d frac_clipped=(?:0\\.091|0\\.092|0\\.093|0\\.094|0\\.095|0\\.096|0\\.097)\\d gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=(?:0\\.176|0\\.177|0\\.178|0\\.179|0\\.180|0\\.181|0\\.182)\\d frac_clipped=(?:0\\.180|0\\.181|0\\.182|0\\.183|0\\.184|0\\.185|0\\.186)\\d gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=(?:0\\.182|0\\.183|0\\.184|0\\.185|0\\.186|0\\.187|0\\.188)\\d frac_clipped=(?:0\\.196|0\\.197|0\\.198|0\\.199|0\\.200|0\\.201|0\\.202)\\d gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=(?:0\\.144|0\\.145|0\\.146|0\\.147|0\\.148|0\\.149|0\\.150)\\d frac_clipped=(?:0\\.147|0\\.148|0\\.149|0\\.150|0\\.151|0\\.152|0\\.153)\\d gain=2\\.00',
            'ARM_SV_YXONLY_AXES z_mean_abs=0\\.0000 yx_mean_abs=0\\.\\d*[1-9]\\d* z_nonzero=0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* '
            'mean_abs_off_vox=0\\.\\d*[1-9]',
        ],
        # --- t6svz05 / t6svx125: t6stk3 with per-axis sub-voxel multipliers (build_t6svax.py), lcefr kept.
        't6svz05': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=t6svz05 SUBVOXEL=axes zyx_gain=0\\.5,1,1 LCEFR=kept GAIN=2\\.00 CLIP=0\\.4999',
            'ARM_SV_AXES zyx_gain=0\\.5,1,1 ',
            'SUBVOXEL patch applied to',
            'SV_ARM_HSG200 nodes=\\d+ mean_abs_off_vox=0\\.\\d+ frac_clipped=',
            'ARM_SV_AXES_STATS z_mean_abs=0\\.0[0-9]{3} yx_mean_abs=0\\.\\d+ z_nonzero=\\d+',
            'ARM_LCEFR patch applied to',
        ],
        't6svx125': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=t6svx125 SUBVOXEL=axes zyx_gain=0,1\\.25,1\\.25 LCEFR=kept GAIN=2\\.00 CLIP=0\\.4999',
            'ARM_SV_AXES zyx_gain=0,1\\.25,1\\.25 ',
            'SUBVOXEL patch applied to',
            'SV_ARM_HSG200 nodes=\\d+ mean_abs_off_vox=0\\.\\d+ frac_clipped=',
            'ARM_SV_AXES_STATS z_mean_abs=0\\.0000 yx_mean_abs=0\\.\\d+ z_nonzero=0(?!\\d)',
            'ARM_LCEFR patch applied to',
        ],
        # --- t6svz15 (z gain 3.0) / t6svz0yx (z only, y/x refinement off): t6stk3 + per-axis multipliers.
        't6svz15': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=t6svz15 SUBVOXEL=axes zyx_gain=1\\.5,1,1 LCEFR=kept GAIN=2\\.00 CLIP=0\\.4999',
            'ARM_SV_AXES zyx_gain=1\\.5,1,1 ',
            'SUBVOXEL patch applied to',
            'ARM_SV_AXES_STATS z_mean_abs=0\\.(?!0000)\\d{4} yx_mean_abs=0\\.(?!0000)\\d{4} z_nonzero=[1-9]',
            'ARM_LCEFR patch applied to',
        ],
        't6svz0yx': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=t6svz0yx SUBVOXEL=axes zyx_gain=1,0,0 LCEFR=kept GAIN=2\\.00 CLIP=0\\.4999',
            'ARM_SV_AXES zyx_gain=1,0,0 ',
            'SUBVOXEL patch applied to',
            'ARM_SV_AXES_STATS z_mean_abs=0\\.(?!0000)\\d{4} yx_mean_abs=0\\.0000 z_nonzero=[1-9]',
            'ARM_LCEFR patch applied to',
        ],
        # --- ourvzl: ourvz + the sub-voxel z offset added to the per-frame detections (arr) right after V1284, so
        # the edge model (pos embedding, predict_edges forward/reverse/secondary) and edge dist read refined z, as
        # lcefr did in t6stk3. Final node coords are bitwise ourvz's (detector_coordinates shas must equal ourvz's).
        # SV_ARM_HSG200 lines are pinned EXACTLY to ourvz's: the offsets are bit-deterministic across runs
        # (t6svyx + ourvz == t6stk3 on all 8 numbers). mean_abs_z = 3 x the 3-column z-only mean (rounding window).
        'ourvzl': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=ourvzl V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
        ],
        # --- t6gtri: t6stk3 + TRILINEAR UNet feature gather at the lcefr-refined coords (z, y, x) on all four gather
        # sites (primary src/tgt, secondary src/tgt); build_t6gtri.py. Detection, SV offsets and the lcefr geometry are
        # untouched, so the four per-movie SV_ARM_HSG200 lines are pinned EXACTLY to t6stk3's (bit-identical across
        # six t6-body runs: t6stk3/t6r70/t65s3/t6sr/t6lf/t6w72). The ARM_GTRI_STATS nodes == 2 x lcefr nodes_refined
        # relation is checked below (4 gathers per pair = 2 x (n_src + n_tgt)); FINAL counts are free (every edge
        # probability moves), default 0.10 window.
        "t6gtri": [
            r"ARM_STK3V velocity_weight=0\.25", r"ARM_STK3B learned_bonus=1\.6",
            r'"motion_relink_velocity_weight": 0\.25(?!\d)', r'"motion_relink_learned_bonus": 1\.6(?!\d)',
            r"ARM_T60H tight_um=6\.0", r'"motion_relink_tight_um": 6\.0(?!\d)',
            r"ARM_XENV tag=t6gtri SUBVOXEL=hsg200 LCEFR=kept GTRI=zyx GAIN=2\.00 CLIP=0\.4999",
            r"SUBVOXEL patch applied to", r"ARM_LCEFR patch applied to ",
            r"ARM_GTRI axes=zyx \(trilinear UNet gather at the lcefr-refined coords, 4 call sites\)",
            r"ARM_GTRI patch applied to .* \| gathers=4 axes=zyx",
            r"SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\.2069 frac_clipped=0\.2306 gain=2\.00",
            r"SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\.2827 frac_clipped=0\.2912 gain=2\.00",
            r"SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\.2913 frac_clipped=0\.3129 gain=2\.00",
            r"SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\.2607 frac_clipped=0\.2828 gain=2\.00",
            r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* mean_abs_off_vox=0\.\d*[1-9]",
            r"ARM_GTRI_STATS axes=zyx calls=[1-9]\d* nodes=[1-9]\d* mean_abs_feat_delta=(?!0\.000000)\d+\.\d{6} selfcheck=1",
            r"ARM_GTRI_XWIN src_nodes=[1-9]\d* src_offpeak=\d+",
        ],
        # --- t6svT15: t6stk3 with the sub-voxel softmax at temperature 1.5, gain 2.00 (build_t6svT.py).
        't6svT15': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            'ARM_T60H tight_um=6\\.0',
            'ARM_XENV tag=t6svT15 SVTEMP=1\\.5 GAIN=2\\.00 LCEFR=kept',
            'ARM_SVTEMP T=1\\.5 gain=2\\.00 ',
            'SUBVOXEL patch applied to',
            'SV_ARM_HSG200 nodes=\\d+ mean_abs_off_vox=0\\.\\d+ frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_LCEFR patch applied to',
        ],
        # --- t6r70T15: t6r70 (0.954 body + raw-ILP override 0.70) with the sub-voxel softmax at temperature 1.5,
        # gain 2.00 (build_t6r70T.py; ops/add_r70T_gate.py). t6r70's markers + the t6svT markers + SV lines pinned
        # to t6svT15's (same detector and logits).
        't6r70T15': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_XENV tag=t6r70T15 SVTEMP=1\\.5 GAIN=2\\.00 LCEFR=kept',
            'ARM_SVTEMP T=1\\.5 gain=2\\.00 ',
            'SUBVOXEL patch applied to',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.2511 frac_clipped=0\\.2822 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.2959 frac_clipped=0\\.2901 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.3075 frac_clipped=0\\.3206 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.2917 frac_clipped=0\\.3075 gain=2\\.00',
        ],
        'xpubz': [
            r'ARM_XENV tag=xpubz BODY=x138 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
            r'Low-detection dump applied',
            r'LOWDET \w+: [1-9]\d* peaks above 0\.3',
            r'low-detection pool: [1-9]\d* peaks >= 0\.5',
            r'readmitted [1-9]\d* discarded detections within 4\.0 um',
            r'gap filler: \+[1-9]\d* nodes',
            r'ILP timeout patch applied',
            r'"motion_relink_tight_um": 5\.5(?!\d)',
            r'"det_threshold": 0\.965(?!\d)',
            r'"motion_relink_learned_bonus": 1\.0(?!\d)',
            r'ARM_SV_ZONLY=1',
            r'ARM_SV_Z_TO_ARR=1 ',
            r'SUBVOXEL patch applied to',
            r'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            r'ARM_V1284_YX module_patched=1',
            r'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            r'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\.1120 frac_clipped=0\.1367 gain=2\.00',
            r'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\.1039 frac_clipped=0\.1077 gain=2\.00',
            r'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\.1060 frac_clipped=0\.1137 gain=2\.00',
            r'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\.1132 frac_clipped=0\.1328 gain=2\.00',
            r'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\.33[56]\d z_nonzero=[1-9]\d* final_z_add=0 gather_int_z=1',
            r'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\.311\d z_nonzero=[1-9]\d* final_z_add=0 gather_int_z=1',
            r'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\.31[78]\d z_nonzero=[1-9]\d* final_z_add=0 gather_int_z=1',
            r'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\.339\d z_nonzero=[1-9]\d* final_z_add=0 gather_int_z=1',
        ],
        # --- t6stk3ff: the 0.954 t6stk3 body + IMGFLOW write-time repair (image phase-correlation flow-
        # compensated re-assignment + track-end bridging in |f| >= 5 um windows) right after filter_output_graph;
        # nodes and forks untouched (build_t6stk3ff.py; ops/add_t6stk3ff_gate.py).
        't6stk3ff': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            'ARM_XENV tag=t6stk3ff FLOWFIX=1 TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200',
            'ARM_FLOWFIX enabled=True TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 threads=\\d+ deadline_s=34200',
            'ARM_FLOWFIX \\[44b6_0113de3b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[44b6_0b24845f\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05b6850b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05db0fb1\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
        ],
        # --- t65s3ff: pick B t65s3 (relink tight 6.5) + IMGFLOW write-time repair (image phase-correlation
        # flow-compensated re-assignment + track-end bridging in |f| >= 5 um windows) right after
        # filter_output_graph; nodes and forks untouched (build_t65s3ff.py; ops/add_t65s3ff_gate.py).
        't65s3ff': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_XENV tag=t65s3ff FLOWFIX=1 TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200',
            'ARM_FLOWFIX enabled=True TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 threads=\\d+ deadline_s=34200',
            'ARM_FLOWFIX \\[44b6_0113de3b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[44b6_0b24845f\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05b6850b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05db0fb1\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
        ],
        # --- t6stk3ff2: t6stk3ff (0.954 t6stk3 body + IMGFLOW repair) + Track-B FLOWCUT+RELINK (drop flow-
        # inconsistent edges in the acted windows, then a second repair pass); nodes and forks untouched
        # (build_t6stk3ff2.py; ops/add_t6stk3ff2_gate.py).
        't6stk3ff2': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            'ARM_XENV tag=t6stk3ff2 FLOWFIX=1 TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200 FLOWCUT=1 R_CUT=6\\.5 COS_MAX=0\\.8 RELINK=1',
            'ARM_FLOWFIX enabled=True TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 threads=\\d+ deadline_s=34200 FLOWCUT R_CUT=6\\.5 COS_MAX=0\\.8 RELINK=1',
            'ARM_FLOWFIX \\[44b6_0113de3b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ bridged=\\d+ dups=\\d+ cut=\\d+ changed2=\\d+ ',
            'ARM_FLOWFIX \\[44b6_0b24845f\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ bridged=\\d+ dups=\\d+ cut=\\d+ changed2=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05b6850b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ bridged=\\d+ dups=\\d+ cut=\\d+ changed2=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05db0fb1\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ bridged=\\d+ dups=\\d+ cut=\\d+ changed2=\\d+ ',
        ],
        # --- t6stk3fl: t6stk3ff + FLOWLINK (IMGFLOW flow inside the cell-5 motion relink for sources in
        # windows with |f| >= 5 um and >= 5 nodes; build_t6stk3fl.py; ops/add_t6stk3fl_gate.py).
        't6stk3fl': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            'ARM_XENV tag=t6stk3fl FLOWLINK=1 FL_TF=5\\.0 FL_MIN_DET=5 FLOWFIX=1 TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200',
            'ARM_FLOWFIX enabled=True TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 threads=\\d+ deadline_s=34200',
            'ARM_FLOWLINK enabled=True TF=5\\.0 MIN_DET=5 MODE=flow gate=relink\\(tight 6\\.0, relaxed 10\\.0\\)',
            'ARM_FLOWLINK \\[44b6_0113de3b\\] status=ok windows=792 flagged_windows=62 digest=[0-9a-f]{12} ',
            'ARM_FLOWLINK \\[44b6_0b24845f\\] status=ok windows=792 flagged_windows=27 digest=[0-9a-f]{12} ',
            'ARM_FLOWLINK \\[6bba_05b6850b\\] status=ok windows=792 flagged_windows=36 digest=[0-9a-f]{12} ',
            'ARM_FLOWLINK \\[6bba_05db0fb1\\] status=ok windows=792 flagged_windows=47 digest=[0-9a-f]{12} ',
            'ARM_FLOWLINK \\[44b6_0113de3b\\] relink flagged_sources=1114\\b',
            'ARM_FLOWLINK \\[44b6_0b24845f\\] relink flagged_sources=470\\b',
            'ARM_FLOWLINK \\[6bba_05b6850b\\] relink flagged_sources=305\\b',
            'ARM_FLOWLINK \\[6bba_05db0fb1\\] relink flagged_sources=4138\\b',
        ],
        # --- t65b20: pick B t65s3 (relink tight 6.5) with the motion-relink learned-edge bonus 1.6 -> 2.0
        # (cost = motion + 0.05*raw - BONUS*prob inside motion_relink_edges). Node- and fork-neutral: exact
        # replay +0.005% nodes, 0 forks (build_t65b20.py; ops/add_t65b20_gate.py). The 2.0 echo is the
        # cell-2 receipt; a 1.6 marker or echo is forbidden below (that would be t65s3 wearing this name).
        't65b20': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.0',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.0(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_XENV tag=t65b20 TIGHT=6\\.5 BONUS=2\\.00 LCEFR=kept',
        ],
        # --- t65b25: pick B t65s3 (relink tight 6.5) with the motion-relink learned-edge bonus 1.6 -> 2.5
        # (t65b20 = 2.0, submitted 56628029; cost = motion + 0.05*raw - BONUS*prob inside motion_relink_edges).
        # Node- and fork-neutral: exact replay +0.008% nodes, 0 forks (build_t65b25.py; ops/add_t65b25_gate.py).
        # The 2.5 echo is the cell-2 receipt; a 2.0 or 1.6 marker/echo is forbidden below (t65b20 / t65s3
        # wearing this name).
        't65b25': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_XENV tag=t65b25 TIGHT=6\\.5 BONUS=2\\.50 LCEFR=kept',
        ],
        # --- t65b25r70: t6r70 (t6stk3 + raw-ILP override at prob >= 0.70) with t65b25's linker settings
        # (relink tight 6.5, learned bonus 2.5). Stack of the two changes that each beat their base on the board.
        # = need['t65b25'] minus its XENV + need['t6r70']'s six rawlink patterns + this arm's XENV
        # (build_t65b25r70.py; ops/add_t65b25r70_gate.py). Topology moves with the linker, so no T6_BODY pins;
        # RL_TAGS + orphan cap + the written-count cross-check below carry the rawlink bookkeeping.
        't65b25r70': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_XENV tag=t65b25r70 TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 LCEFR=kept',
        ],
        # --- ourvzlb25: ourvzl (V1284 y/x head + sub-voxel z to the edge model, board 0.953) with t65b25's linker
        # settings: relink tight 6.0 -> 6.5, learned bonus 1.6 -> 2.5 (build_ourvzlb25.py; ops/add_ourvzlb25_gate.py).
        # = need['ourvzl'] with STK3B/T60H rewritten to 2.5/T65H 6.5 + the three cell-2 linker echoes + this XENV.
        # The coordinate pins stay EXACT (the linker acts after detection). sv_mark is in the dict literal.
        'ourvzlb25': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_XENV tag=ourvzlb25 TIGHT=6\\.5 BONUS=2\\.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
        ],
        # --- t70b20: t65b20 (0.954; t65s3 body, relink tight 6.5, learned bonus 2.0) with the motion-relink
        # TIGHT gate widened 6.5 -> 7.0 (bonus kept 2.0). Node- and fork-neutral: exact replay +0.018% nodes,
        # 0 forks (build_t70b20.py; ops/add_t70b20_gate.py). The 7.0 cell-2 and cell-9 echoes are the receipts,
        # plus the motion_relink_tight_edges check below; a 6.5 / 6.0 tight echo, ARM_T65H or a non-2.0 bonus
        # is forbidden (t65b20 / t65b25 / t65s3 / t6stk3 wearing this name).
        't70b20': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.0',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.0(?!\\d)',
            'ARM_T70H tight_um=7\\.0',
            '"motion_relink_tight_um": 7\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'MOTION_RELINK_TIGHT_UM +7\\.0(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +2\\.0(?!\\d)',
            'ARM_XENV tag=t70b20 TIGHT=7\\.0 BONUS=2\\.00 LCEFR=kept',
        ],
        # --- t70b25: t70b20 (relink tight 7.0, bonus 2.0; submitted 56641323) with the learned-edge bonus
        # 2.0 -> 2.5 (the t65b20 -> t65b25 step). Derived from need['t70b20'] (ops/add_t70b25_gate.py;
        # build_t70b25.py): 2.5 bonus marker + cell-2/cell-9 echoes, 7.0 tight receipts kept, plus the
        # motion_relink_tight_edges check below; a 1.6 / 2.0 (any non-2.5) bonus or any non-7.0 tight is
        # forbidden (t70b20 / t65b25 / t65b20 / t6stk3 wearing this name).
        't70b25': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T70H tight_um=7\\.0',
            '"motion_relink_tight_um": 7\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'MOTION_RELINK_TIGHT_UM +7\\.0(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +2\\.5(?!\\d)',
            'ARM_XENV tag=t70b25 TIGHT=7\\.0 BONUS=2\\.50 LCEFR=kept',
        ],
        # --- t65b20d04: t65b20 (0.954 top entry 56628029; t65s3 body, relink tight 6.5, learned bonus 2.0)
        # with the tracking ILP division weight 1.2 -> 0.4 (build_t65b20d04.py; ops/add_t65b20d04_gate.py).
        # With ILP_APPEARANCE_WEIGHT = 0 the solver forks iff p2 >= weight, so 0.4 is the first value that
        # lets the ILP fork: FINAL / division counts may move and are NOT pinned. Receipts: cell-0
        # ARM_ILPDIV, the cell-2 echo and the predictor command line, all 0.4; any 1.2 is forbidden below.
        't65b20d04': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.0',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.0(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_XENV tag=t65b20d04 TIGHT=6\\.5 BONUS=2\\.00 ILPDIV=0\\.4 LCEFR=kept',
            'ARM_ILPDIV weight=0\\.4(?!\\d)',
            '"ilp_division_weight": 0\\.4(?!\\d)',
            '--ilp-division-weight 0\\.4(?!\\d)',
        ],
        # --- t675b25: t65b25 (relink tight 6.5, learned bonus 2.5; submitted 56639660) with the motion-relink
        # TIGHT gate widened 6.5 -> 6.75 (bonus kept 2.5). Derived from need['t65b25'] (ops/add_t675b25_gate.py;
        # build_t675b25.py): ARM_T675H + 6.75 cell-2/cell-9 echoes, 2.5 bonus receipts kept, plus the
        # motion_relink_tight_edges check below; a 6.5 / 6.0 / 7.0 (any non-6.75) tight, ARM_T65H or a non-2.5
        # bonus is forbidden (t65b25 / t70b20 / t70b25 / t65b20 / t65s3 / t6stk3 wearing this name).
        't675b25': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T675H tight_um=6\\.75',
            '"motion_relink_tight_um": 6\\.75(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'MOTION_RELINK_TIGHT_UM +6\\.75(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +2\\.5(?!\\d)',
            'ARM_XENV tag=t675b25 TIGHT=6\\.75 BONUS=2\\.50 LCEFR=kept',
        ],
        # --- ourvzlb25r70: ourvzlb25 (V1284 y/x head + sub-voxel z to the edge model, tight 6.5, bonus 2.5; board
        # 0.954) + t6r70's raw-ILP override at prob >= 0.70 (the step that made t65b25r70 the representative).
        # = need['ourvzlb25'] minus its XENV + need['t6r70']'s six rawlink patterns + this arm's XENV
        # (build_ourvzlb25r70.py; ops/add_ourvzlb25r70_gate.py). Coordinate pins stay EXACT (rawlink acts on the
        # final graph); RL_TAGS + orphan cap + the written-count cross-check carry the rawlink bookkeeping.
        'ourvzlb25r70': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_XENV tag=ourvzlb25r70 TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- t65b25r70ff: t65b25r70 (t6stk3 + tight 6.5 + bonus 2.5 + raw-ILP override 0.70; representative 0.954)
        # + IMGFLOW write-time repair after the override, as build_t6r70ff.py placed it on t6r70.
        # = need['t65b25r70'] minus its XENV + need['t6stk3ff']'s five ARM_FLOWFIX patterns + this arm's XENV
        # (build_t65b25r70ff.py; ops/add_t65b25r70ff_gate.py). RL_TAGS + orphan cap + the flowfix cross-check
        # below (A == rawlink final=, B == A + bridged - dups == written) carry the bookkeeping.
        't65b25r70ff': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_FLOWFIX enabled=True TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 threads=\\d+ deadline_s=34200',
            'ARM_FLOWFIX \\[44b6_0113de3b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[44b6_0b24845f\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05b6850b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05db0fb1\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_XENV tag=t65b25r70ff TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 FLOWFIX=1 TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200',
        ],
        # --- t65b25r70sr: t65b25r70 (t6stk3 + tight 6.5 + bonus 2.5 + raw-ILP override 0.70; representative 0.954)
        # with the short-track rescue armed unconditionally (trigger 0.10 -> 0.0), as t6sr did on t6stk3.
        # = need['t65b25r70'] minus its XENV + t6sr's deepcenter echo + the live trigger echo 0.0 + this XENV
        # (build_t65b25r70sr.py; ops/add_t65b25r70sr_gate.py). RL_TAGS + orphan cap + the written-count
        # cross-check + run_stats rescue receipts (triggered on all movies, components > 0 somewhere) below.
        't65b25r70sr': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
            '"short_track_rescue_trigger_removed_frac": 0\\.0(?!\\d)',
            'ARM_XENV tag=t65b25r70sr TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 SR=armed',
        ],
        # --- mixyx50r70: t65b25r70's full stack with y/x = 0.5*V1284 + 0.5*SV (V1284 mounted as in ourvzlb25r70,
        # z = production SV z-to-arr as in both parents; scratchpad/wf30). = need['ourvzlb25r70'] minus its XENV
        # (z-only SV + z-to-arr pins stay EXACT: the z-only call is untouched) + the ARM_MIXYX env/patch lines +
        # one ARM_MIXYX line per movie at that movie's detection count + this arm's XENV
        # (build_mixyx50r70.py; ops/add_mixyx50r70_gate.py). RL_TAGS + orphan cap + written-count cross-check.
        'mixyx50r70': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_MIXYX w=0\\.5 \\(y/x = 0\\.5\\*V1284 \\+ 0\\.5\\*SV into the per-frame detections after V1284; z = SV z-to-arr\\)',
            'ARM_MIXYX patch applied to .* predictor anchors=7 module anchors=1 w=0\\.5(?!\\d)',
            'ARM_MIXYX w=0\\.5 frames=100 nodes=26532 mean_abs_sv_minus_v1284_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_sv_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_v1284_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_yx_blend_um=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) final_yx_add=0(?!\\d)',
            'ARM_MIXYX w=0\\.5 frames=100 nodes=33336 mean_abs_sv_minus_v1284_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_sv_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_v1284_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_yx_blend_um=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) final_yx_add=0(?!\\d)',
            'ARM_MIXYX w=0\\.5 frames=100 nodes=7370 mean_abs_sv_minus_v1284_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_sv_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_v1284_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_yx_blend_um=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) final_yx_add=0(?!\\d)',
            'ARM_MIXYX w=0\\.5 frames=100 nodes=76396 mean_abs_sv_minus_v1284_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_sv_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_v1284_um y=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) x=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) mean_abs_yx_blend_um=(?:0\\.\\d*[1-9]\\d*|[1-9]\\d*\\.\\d+) final_yx_add=0(?!\\d)',
            'ARM_XENV tag=mixyx50r70 TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx MIXYX=0\\.50',
        ],
        # --- t65b25r70ffsr: t65b25r70 (t6stk3 + tight 6.5 + bonus 2.5 + raw-ILP override 0.70; representative
        # 0.954) with BOTH stacked additions: IMGFLOW write-time repair after the override (t65b25r70ff) and
        # the short-track rescue armed unconditionally (t65b25r70sr). = need['t65b25r70ff'] minus its XENV +
        # need['t65b25r70sr']'s deepcenter + trigger-0.0 echoes + this XENV (build_t65b25r70ffsr.py;
        # ops/add_t65b25r70ffsr_gate.py). RL_TAGS + orphan cap + ff cross-check + rescue receipts + chain below.
        't65b25r70ffsr': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            '"output_linefit_smooth": true',
            '"output_linefit_weight": 0\\.8(?!\\d)',
            '"output_linefit_window": 2(?!\\d)',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_FLOWFIX enabled=True TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 threads=\\d+ deadline_s=34200',
            'ARM_FLOWFIX \\[44b6_0113de3b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[44b6_0b24845f\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05b6850b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05db0fb1\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
            '"short_track_rescue_trigger_removed_frac": 0\\.0(?!\\d)',
            'ARM_XENV tag=t65b25r70ffsr TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 FLOWFIX=1 TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200 SR=armed',
        ],
        # --- ourvzlb25r70ff: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, raw-ILP override
        # 0.70; public 0.955) + the IMGFLOW write-time repair after the override, as t65b25r70ff carries it.
        # = need['ourvzlb25r70'] minus its XENV + the five ARM_FLOWFIX patterns + this arm's XENV
        # (build_ourvzlb25r70ff.py; ops/add_ourvzlb25r70ff_gate.py). Coordinate pins stay EXACT (the repair acts
        # on the written graph); RL_TAGS + orphan cap + the renamed t65b25r70ff cross-check carry the bookkeeping.
        'ourvzlb25r70ff': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_FLOWFIX enabled=True TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 threads=\\d+ deadline_s=34200',
            'ARM_FLOWFIX \\[44b6_0113de3b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[44b6_0b24845f\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05b6850b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05db0fb1\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_XENV tag=ourvzlb25r70ff TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 FLOWFIX=1 TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlt625: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with ONE cell-0 env change (tight: tight 6.25, bonus 2.5). = need['ourvzlb25r70'] with the changed knob's
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlt625.py; ops/add_ourvzlt625_gate.py).
        'ourvzlt625': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T625H tight_um=6\\.25(?!\\d)',
            '"motion_relink_tight_um": 6\\.25(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.25(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +2\\.5(?!\\d)',
            'ARM_XENV tag=ourvzlt625 TIGHT=6\\.25 BONUS=2\\.50 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlt675: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with ONE cell-0 env change (tight: tight 6.75, bonus 2.5). = need['ourvzlb25r70'] with the changed knob's
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlt675.py; ops/add_ourvzlt675_gate.py).
        'ourvzlt675': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T675H tight_um=6\\.75(?!\\d)',
            '"motion_relink_tight_um": 6\\.75(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.75(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +2\\.5(?!\\d)',
            'ARM_XENV tag=ourvzlt675 TIGHT=6\\.75 BONUS=2\\.50 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlb30: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with ONE cell-0 env change (bonus: tight 6.5, bonus 3.0). = need['ourvzlb25r70'] with the changed knob's
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlb30.py; ops/add_ourvzlb30_gate.py).
        'ourvzlb30': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=3\\.0(?!\\d)',
            '"motion_relink_learned_bonus": 3\\.0(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.5(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +3\\.0(?!\\d)',
            'ARM_XENV tag=ourvzlb30 TIGHT=6\\.5 BONUS=3\\.00 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlb20: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with ONE cell-0 env change (bonus: tight 6.5, bonus 2.0). = need['ourvzlb25r70'] with the changed knob's
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlb20.py; ops/add_ourvzlb20_gate.py).
        'ourvzlb20': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.0(?!\\d)',
            '"motion_relink_learned_bonus": 2\\.0(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.5(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +2\\.0(?!\\d)',
            'ARM_XENV tag=ourvzlb20 TIGHT=6\\.5 BONUS=2\\.00 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlsr: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with ONE cell-0 env change (sr: tight 6.5, bonus 2.5, rescue armed). = need['ourvzlb25r70'] with the changed knob's
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlsr.py; ops/add_ourvzlsr_gate.py).
        'ourvzlsr': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.5(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +2\\.5(?!\\d)',
            '"short_track_rescue_trigger_removed_frac": 0\\.0(?!\\d)',
            '"adaptive_short_track_rescue": true',
            'ARM_XENV tag=ourvzlsr TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 SR=armed V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzllf100: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with ONE cell-0 env change (lf: tight 6.5, bonus 2.5, line-fit weight 1.0). = need['ourvzlb25r70'] with the changed knob's
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzllf100.py; ops/add_ourvzllf100_gate.py).
        'ourvzllf100': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=2\\.5',
            '"motion_relink_learned_bonus": 2\\.5(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.5(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +2\\.5(?!\\d)',
            '"output_linefit_weight": 1\\.0(?!\\d)',
            'ARM_XENV tag=ourvzllf100 TIGHT=6\\.5 BONUS=2\\.50 RAWLINK=0\\.70 LINEFIT_W=1\\.0 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlb30t625: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with TWO cell-0 env changes (tight 6.25 + bonus 3.0 = ourvzlt625 + ourvzlb30). = need['ourvzlb25r70'] with both knobs'
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlb30t625.py; ops/add_ourvzlb30t625_gate.py).
        'ourvzlb30t625': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=3\\.0(?!\\d)',
            '"motion_relink_learned_bonus": 3\\.0(?!\\d)',
            'ARM_T625H tight_um=6\\.25(?!\\d)',
            '"motion_relink_tight_um": 6\\.25(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.25(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +3\\.0(?!\\d)',
            'ARM_XENV tag=ourvzlb30t625 TIGHT=6\\.25 BONUS=3\\.00 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlffb30: ourvzlb25r70ff (ourvzlb25r70, public 0.955, + the IMGFLOW write-time repair) with ONE cell-0
        # env change (bonus 2.5 -> 3.0). = need['ourvzlb25r70ff'] with the bonus marker/echo swapped + cell-9
        # echoes + this XENV (scratch_kernels/build_ourvzlffb30.py; ops/add_ourvzlffb30_gate.py via ops/ourvzl_combo_gate.py).
        'ourvzlffb30': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=3\\.0(?!\\d)',
            '"motion_relink_learned_bonus": 3\\.0(?!\\d)',
            'ARM_T65H tight_um=6\\.5',
            '"motion_relink_tight_um": 6\\.5(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_FLOWFIX enabled=True TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 threads=\\d+ deadline_s=34200',
            'ARM_FLOWFIX \\[44b6_0113de3b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[44b6_0b24845f\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05b6850b\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'ARM_FLOWFIX \\[6bba_05db0fb1\\] status=ok windows=\\d+ flagged=\\d+ acted=\\d+ changed=\\d+ ',
            'MOTION_RELINK_TIGHT_UM +6\\.5(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +3\\.0(?!\\d)',
            'ARM_XENV tag=ourvzlffb30 TIGHT=6\\.5 BONUS=3\\.00 RAWLINK=0\\.70 FLOWFIX=1 TF=5\\.0 KEEP=3\\.5 GATE=4\\.5 MIN_DET=5 ENDS=1 DEADLINE_S=34200 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlb35t625: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with TWO cell-0 env changes (tight 6.25 + bonus 3.5 = ourvzlb30t625 with bonus 3.0 -> 3.5). = need['ourvzlb25r70'] with both knobs'
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlb35t625.py; ops/add_ourvzlb35t625_gate.py).
        'ourvzlb35t625': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=3\\.5(?!\\d)',
            '"motion_relink_learned_bonus": 3\\.5(?!\\d)',
            'ARM_T625H tight_um=6\\.25(?!\\d)',
            '"motion_relink_tight_um": 6\\.25(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.25(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +3\\.5(?!\\d)',
            'ARM_XENV tag=ourvzlb35t625 TIGHT=6\\.25 BONUS=3\\.50 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlb40t625: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with TWO cell-0 env changes (tight 6.25 + bonus 4.0 = ourvzlb30t625 with bonus 3.0 -> 4.0). = need['ourvzlb25r70'] with both knobs'
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlb40t625.py; ops/add_ourvzlb40t625_gate.py).
        'ourvzlb40t625': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=4\\.0(?!\\d)',
            '"motion_relink_learned_bonus": 4\\.0(?!\\d)',
            'ARM_T625H tight_um=6\\.25(?!\\d)',
            '"motion_relink_tight_um": 6\\.25(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.25(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +4\\.0(?!\\d)',
            'ARM_XENV tag=ourvzlb40t625 TIGHT=6\\.25 BONUS=4\\.00 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        # --- ourvzlb30t600: ourvzlb25r70 (V1284 y/x head + sub-voxel z, tight 6.5, bonus 2.5, rawlink 0.70; public 0.955)
        # with TWO cell-0 env changes (tight 6.0 + bonus 3.0 = ourvzlb30t625 with tight 6.25 -> 6.0). = need['ourvzlb30t625'] with the tight
        # marker/echo swapped + cell-9 echoes + this XENV (scratch_kernels/build_ourvzlb30t600.py; ops/add_ourvzlb30t600_gate.py).
        'ourvzlb30t600': [
            'ARM_STK3V velocity_weight=0\\.25',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            'ARM_STK3B learned_bonus=3\\.0(?!\\d)',
            '"motion_relink_learned_bonus": 3\\.0(?!\\d)',
            'ARM_T60H tight_um=6\\.0(?!\\d)',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_SV_ZONLY=1',
            'ARM_SV_Z_TO_ARR=1 ',
            'SUBVOXEL patch applied to',
            'V1284 head patched AFTER the readmit dump patch; mode = candidate',
            'ARM_V1284_YX module_patched=1',
            'ARM_SV_Z_TO_ARR patch applied to .* predictor anchors=4 module anchors=1 gather_int_z=1',
            'SV_ARM_HSG200 nodes=26532 mean_abs_off_vox=0\\.1120 frac_clipped=0\\.1367 gain=2\\.00',
            'SV_ARM_HSG200 nodes=33336 mean_abs_off_vox=0\\.1039 frac_clipped=0\\.1077 gain=2\\.00',
            'SV_ARM_HSG200 nodes=7370 mean_abs_off_vox=0\\.1060 frac_clipped=0\\.1137 gain=2\\.00',
            'SV_ARM_HSG200 nodes=76396 mean_abs_off_vox=0\\.1132 frac_clipped=0\\.1328 gain=2\\.00',
            'ARM_SV_Z_TO_ARR frames=100 nodes=26532 mean_abs_z=0\\.33[56]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=33336 mean_abs_z=0\\.311\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=7370 mean_abs_z=0\\.31[78]\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_SV_Z_TO_ARR frames=100 nodes=76396 mean_abs_z=0\\.339\\d z_nonzero=[1-9]\\d* final_z_add=0 gather_int_z=1',
            'ARM_RAWLINK min_prob=0\\.7(?!\\d) enabled=True ',
            '"rawlink_min_prob": 0\\.7(?!\\d)',
            'ARM_RAWLINK \\[44b6_0113de3b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[44b6_0b24845f\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05b6850b\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'ARM_RAWLINK \\[6bba_05db0fb1\\] min_prob=0\\.7 candidates=\\d+ accepted=[1-9]\\d* ',
            'MOTION_RELINK_TIGHT_UM +6\\.0(?!\\d)',
            'MOTION_RELINK_LEARNED_BONUS +3\\.0(?!\\d)',
            'ARM_XENV tag=ourvzlb30t600 TIGHT=6\\.0 BONUS=3\\.00 RAWLINK=0\\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx',
        ],
        't6dl': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_XENV tag=t6dl REPAIR_DEADLINE_S=28800',
            'ARM_DEADLINE repair [0-9.]+s \\| kernel elapsed \\d+s \\| degraded=0 fallback=0',
        ],
        'ddsr': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_XENV tag=ddsr BIOHUB_DEDUP_RADIUS_UM=5\\.0 BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=0\\.0',
            'ARM_DEDUP \\[44b6_0113de3b\\] radius=5\\.00um merged=[1-9]\\d* nodes \\d+->\\d+ edges \\d+->\\d+',
            'ARM_DEDUP \\[6bba_05db0fb1\\] radius=5\\.00um merged=[1-9]\\d* nodes \\d+->\\d+ edges \\d+->\\d+',
        ],
        't6wz': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            'ARM_XENV tag=t6wz BIOHUB_DEEPCENTER_SCORE_WIN_Z=2',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
        ],
        't6sr': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            'ARM_XENV tag=t6sr BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=0\\.0',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
        ],
        't6dv': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            'ARM_XENV tag=t6dv BIOHUB_SAFE_DIV_DIVERGE_UM=1\\.50',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
        ],
        't6dc': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            'ARM_XENV tag=t6dc BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD=0\\.15',
            '"deepcenter_safe_div_threshold": 0\\.15(?!\\d)',
        ],
        't6dd': [
            'ARM_STK3V velocity_weight=0\\.25',
            'ARM_STK3B learned_bonus=1\\.6',
            '"motion_relink_velocity_weight": 0\\.25(?!\\d)',
            '"motion_relink_learned_bonus": 1\\.6(?!\\d)',
            'ARM_T60H tight_um=6\\.0',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
            'ARM_XENV tag=t6dd BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD=0\\.15 BIOHUB_SAFE_DIV_DIVERGE_UM=1\\.50',
            '"deepcenter_safe_div_threshold": 0\\.15(?!\\d)',
        ],
        'xsvmax': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            '"safe_div_max_um": 9\\.0(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvmax BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD=0\\.15 BIOHUB_SAFE_DIV_DIVERGE_UM=1\\.50 BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=0\\.0',
            '"deepcenter_safe_div_threshold": 0\\.15(?!\\d)',
        ],
        'xsvdd': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvdd BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD=0\\.15 BIOHUB_SAFE_DIV_DIVERGE_UM=1\\.50',
            '"deepcenter_safe_div_threshold": 0\\.15(?!\\d)',
            '"safe_div_max_um": 9\\.0(?!\\d)',
        ],
        'xsvd10': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvd10 BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD=0\\.10',
            '"deepcenter_safe_div_threshold": 0\\.1(?!\\d)',
            '"safe_div_max_um": 9\\.0(?!\\d)',
        ],
        'xsvwz': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvwz BIOHUB_DEEPCENTER_SCORE_WIN_Z=2',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
            '"safe_div_max_um": 9\\.0(?!\\d)',
        ],
        'xsvmx': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvmx BIOHUB_SAFE_DIV_MAX_UM=11\\.0',
            '"safe_div_max_um": 11\\.0(?!\\d)',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
        ],
        'xsvdv': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvdv BIOHUB_SAFE_DIV_DIVERGE_UM=1\\.50',
            '"deepcenter_safe_div_threshold": 0\\.25(?!\\d)',
        ],
        'xsvdc': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_XENV tag=xsvdc BIOHUB_DEEPCENTER_SAFE_DIV_THRESHOLD=0\\.15',
            '"deepcenter_safe_div_threshold": 0\\.15(?!\\d)',
        ],
        'xsvt': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 6\\.0(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'ARM_XENV tag=xsvt BIOHUB_MOTION_RELINK_TIGHT_UM=6\\.0',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
        ],
        'xsvd': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',
            'ARM_XENV tag=xsvd BIOHUB_SAFE_DIV_SISTER_SYMMETRY_TAU=0\\.4',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
        ],
        'xsv96': [
            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.96(?!\\d)',
            'ARM_XENV tag=xsv96 BIOHUB_DET_THRESHOLD=0\\.96',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
        ],
        'xsv': [
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',

            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
        ],
        'xsvb': [
            'ARM_XENV tag=xsvb BIOHUB_MOTION_RELINK_LEARNED_BONUS=1\\.6',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',

            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.60',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
        ],
        'xsvf': [
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',

            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            'SV_ARM_HSG200 nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]\\d* frac_clipped=0\\.\\d+ gain=2\\.00',
            'ARM_LCEFR patch applied to ',
            'ARM_LCEFR pairs_refined=[1-9]\\d* nodes_refined=[1-9]\\d* diff_nodes=[1-9]\\d* mean_abs_off_vox=0\\.\\d*[1-9]',
        ],
        'xbase': [
            'ARM_XENV tag=xbase',
            '"motion_relink_tight_um": 5\\.5(?!\\d)',
            '"det_threshold": 0\\.965(?!\\d)',

            'ARM_XFLOW mode=seed k=12 radius=40\\.0 exclude=1\\.5 min_samples=4 gate=True iter=1 raw_admit=True raw_cost=0\\.00 flow_tight=7\\.0 flow_relaxed=0\\.0 velocity=0\\.50',
            'ARM_XRECALL readmit_radius=4\\.0 readmit_min_score=0\\.965 gapfill_max_gap=3 gapfill_min_score=0\\.50 gapfill_added_frac_cap=0\\.030 gapfill_synthetic=0',
            'ARM_XFLOWSTATS frames=[1-9]\\d* flow_frames=[1-9]\\d* flow_predicted=[1-9]\\d*',
            'Low-detection dump applied',
            'LOWDET \\w+: [1-9]\\d* peaks above 0\\.3',
            'low-detection pool: [1-9]\\d* peaks >= 0\\.5',
            'readmitted [1-9]\\d* discarded detections within 4\\.0 um',
            'gap filler: \\+[1-9]\\d* nodes',
            'flow_relaxed=0\\.0 velocity=0\\.50 bonus=1\\.00',
            'coordinate-refinement slot intentionally empty',
        ],
        "t65h": [r"ARM_T65H tight_um=6\.5",
                 r'"motion_relink_tight_um": 6\.5(?!\d)'],
        # --- 09-23 STACK ROUND: the remaining INDEPENDENT components bolted onto the board-confirmed 0.954
        # body (t6stk3 = stk3's velocity 0.25 + learned bonus 1.6 + lcefr, plus t60h's tight 6.0, all on the
        # 0.951 hsg200 sub-voxel body), and the 6.5 relink bracket re-tested INSIDE that stack.
        # A stack's danger is PARTIAL application: if one component silently drops out the run is a cheaper
        # arm wearing this name and its board reading is unattributable. So every component is pinned by the
        # SAME evidence its own single-arm entry uses, never by the stack marker alone:
        #   velocity / bonus / tight: the cell-0 print fires right beside the os.environ assignment and
        #     proves nothing on its own, so the cell-2 CONFIG_DISPLAY echo of the realized float is pinned
        #     too. (?!\d) stops 0.250001 / 1.60001 / 6.05 / 6.55 from satisfying an echo pattern.
        #   lcefr: pinned through its RUNTIME per-video counter line with non-zero counts, not just
        #     "patch applied", because the switch has to survive into the subprocess workers (see the lcefr
        #     note above); "patch applied" alone would pass a run whose workers never saw the variable.
        # The whole line-fit family (smooth / weight / window / strict_linear) is pinned on EVERY entry at
        # the value that arm is supposed to run, so a leaked lfds or lfw72 edit cannot pass under another
        # arm's name; lfds and lfw72 are the same family and must never appear together.
        # Markers from components an arm should NOT carry are rejected by the T6_ALLOWED allowlist below,
        # which also carries the topology and run_stats receipts that `need` cannot express.
        # t6r70 = the 0.954 body + the josephadamski91 V1057 raw-ILP override at prob >= 0.70, divisions
        # protected. All FIVE components must fire. Line-fit stays at the BASE weight 0.8 with the strict
        # switch absent, so a leaked lfds / lfw72 edit cannot pass under this name.
        "t6r70": [r"ARM_STK3V velocity_weight=0\.25", r"ARM_STK3B learned_bonus=1\.6",
                  r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                  r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                  r"ARM_T60H tight_um=6\.0",
                  r'"motion_relink_tight_um": 6\.0(?!\d)',
                  r"ARM_LCEFR patch applied to ",
                  r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                  r"mean_abs_off_vox=0\.\d*[1-9]",
                  r'"output_linefit_smooth": true',
                  r'"output_linefit_weight": 0\.8(?!\d)',
                  r'"output_linefit_window": 2(?!\d)',
                  r"ARM_RAWLINK min_prob=0\.7(?!\d) enabled=True ",
                  r'"rawlink_min_prob": 0\.7(?!\d)',
                  r"ARM_RAWLINK \[44b6_0113de3b\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                  r"ARM_RAWLINK \[44b6_0b24845f\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                  r"ARM_RAWLINK \[6bba_05b6850b\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                  r"ARM_RAWLINK \[6bba_05db0fb1\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* "],
        # t6lf = the 0.954 body + zoli800's strict-linear line-fit. Line-fit is the LAST statement of
        # filter_output_graph and returns only nodes_by_id, while every t6stk3 component acts strictly
        # upstream (lcefr inside the edge model, velocity/bonus/tight inside motion_relink_edges), so an
        # identical topology is a proof and is pinned exactly in the T6_BODY block. The strict switch has
        # no effect the cell-0 print can show, so its cell-2 echo is required AND linefit_smoothed_nodes /
        # linefit_skipped_nodes are pinned in the run_stats block: that is its only cell-5 receipt.
        "t6lf": [r"ARM_STK3V velocity_weight=0\.25", r"ARM_STK3B learned_bonus=1\.6",
                 r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                 r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                 r"ARM_T60H tight_um=6\.0",
                 r'"motion_relink_tight_um": 6\.0(?!\d)',
                 r"ARM_LCEFR patch applied to ",
                 r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                 r"mean_abs_off_vox=0\.\d*[1-9]",
                 r"ARM_LFDS linefit=strict_linear_interior",
                 r'"output_linefit_strict_linear": true',
                 r'"output_linefit_smooth": true',
                 r'"output_linefit_weight": 0\.8(?!\d)',
                 r'"output_linefit_window": 2(?!\d)'],
        # t6rlf = the 0.954 body + rawlink70 + lfds, the two remaining independent components at once.
        # They compose in a FIXED order: line-fit runs inside filter_output_graph and rawlink rewires edges
        # after it, so line-fit sees the pre-override graph and its counters must equal t6lf's exactly.
        # ALL SIX components are pinned; the rawlink half alone would also satisfy t6r70, so lfds is pinned
        # here through its cell-2 echo AND through linefit_smoothed_nodes in the run_stats block.
        "t6rlf": [r"ARM_STK3V velocity_weight=0\.25", r"ARM_STK3B learned_bonus=1\.6",
                  r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                  r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                  r"ARM_T60H tight_um=6\.0",
                  r'"motion_relink_tight_um": 6\.0(?!\d)',
                  r"ARM_LCEFR patch applied to ",
                  r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                  r"mean_abs_off_vox=0\.\d*[1-9]",
                  r"ARM_LFDS linefit=strict_linear_interior",
                  r'"output_linefit_strict_linear": true',
                  r'"output_linefit_smooth": true',
                  r'"output_linefit_weight": 0\.8(?!\d)',
                  r'"output_linefit_window": 2(?!\d)',
                  r"ARM_RAWLINK min_prob=0\.7(?!\d) enabled=True ",
                  r'"rawlink_min_prob": 0\.7(?!\d)',
                  r"ARM_RAWLINK \[44b6_0113de3b\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                  r"ARM_RAWLINK \[44b6_0b24845f\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                  r"ARM_RAWLINK \[6bba_05b6850b\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                  r"ARM_RAWLINK \[6bba_05db0fb1\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* "],
        # t6w72 = the 0.954 body + lfw72's single cell-0 line, OUTPUT_LINEFIT_WEIGHT 0.8 -> 0.72. The weight
        # does not change WHICH nodes are smoothed (linefit_smoothed_nodes is identical to the 0.954 run's),
        # so that counter cannot prove the weight: the cell-2 echo of the realized float is the evidence and
        # (?!\d) stops 0.725 / 0.7200001. smooth + window stay pinned so the ONLY line-fit change is the
        # weight, and the strict switch must be absent (checked negatively in the T6_ALLOWED block).
        "t6w72": [r"ARM_STK3V velocity_weight=0\.25", r"ARM_STK3B learned_bonus=1\.6",
                  r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                  r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                  r"ARM_T60H tight_um=6\.0",
                  r'"motion_relink_tight_um": 6\.0(?!\d)',
                  r"ARM_LCEFR patch applied to ",
                  r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                  r"mean_abs_off_vox=0\.\d*[1-9]",
                  r"ARM_LFW72 linefit_weight=0\.72(?!\d)",
                  r'"output_linefit_weight": 0\.72(?!\d)',
                  r'"output_linefit_smooth": true',
                  r'"output_linefit_window": 2(?!\d)'],
        # --- t6v00 / t6b22: the two RELINK DIAL EXTREMES, one knob each, inside the 0.954 body ------------
        # Neither is an independent component. Velocity, bonus and tight are three knobs on the SAME
        # linear_sum_assignment inside motion_relink_edges, and that function's output REPLACES the whole
        # edge set (`edges = motion_edges` in filter_output_graph), so both arms move topology and are
        # deliberately excluded from the T6_BODY pins the way t65s3 is; their cell-5 receipt is the T6_DIAL
        # block further below.
        # Each arm carries THREE realized echoes of its own knob, not just the cell-0 print:
        #   cell 0  -- fires right beside the os.environ assignment and proves only that the environment
        #              was written, never that anything read it. Necessary, nowhere near sufficient.
        #   cell 2  -- CONFIG_DISPLAY, the float AFTER the float() conversion, out of the same module-level
        #              global that cell 5's motion_relink_edges resolves at call time.
        #   cell 9  -- PP_BASE_CONFIG, read out of globals() AFTER all four movies are tracked, so it is
        #              the only receipt that the global still held the value at tracking time. It prints
        #              `KEY<padded to 40> VALUE`, hence the ` +` between name and number.
        # NOTE both echoes render a float with repr, so 0.00 prints as 0.0 and never as 0.00; (?!\d) is
        # what stops a 0.05 / 0.0625 / 2.25 echo from satisfying the pattern.
        # t6v00 needs this harder than any arm so far: a velocity weight of exactly 0.00 makes `predicted`
        # equal `source_pos` in BOTH arms of the `prev_pos is None` branch, so the run is behaviourally
        # indistinguishable from one where the knob never reached the linker at all. That is the same trap
        # lcvel0 was written for, one level up the stack.
        "t6v00": [r"ARM_T6V00 velocity_weight=0\.00",
                  r'"motion_relink_velocity_weight": 0\.0(?!\d)',
                  r"MOTION_RELINK_VELOCITY_WEIGHT +0\.0(?!\d)",
                  r"ARM_STK3B learned_bonus=1\.6",
                  r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                  r"MOTION_RELINK_LEARNED_BONUS +1\.6(?!\d)",
                  r"ARM_T60H tight_um=6\.0",
                  r'"motion_relink_tight_um": 6\.0(?!\d)',
                  r"MOTION_RELINK_TIGHT_UM +6\.0(?!\d)",
                  r"ARM_LCEFR patch applied to ",
                  r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                  r"mean_abs_off_vox=0\.\d*[1-9]",
                  r'"output_linefit_smooth": true',
                  r'"output_linefit_weight": 0\.8(?!\d)',
                  r'"output_linefit_window": 2(?!\d)'],
        # t6b22 is the far end of the same cost: bonus 1.6 -> 2.2 buys a probability-1 candidate up to 0.6 um
        # of extra slack against `motion + 0.05*raw`. It cannot break the solver -- scipy's
        # linear_sum_assignment takes any finite cost including negative ones, the feasible range here is
        # [-2.2, ~13] and the ONLY thing that reads a cost back is the `cost[r, c] >= big` rejection with
        # big = gate*1000 + 1 = 6001 tight / 10001 relaxed -- but it can still be a silent no-op, so it gets
        # the same three-echo treatment. Velocity stays pinned at 0.25 so a leaked t6v00 edit cannot pass here.
        "t6b22": [r"ARM_T6B22 learned_bonus=2\.2",
                  r'"motion_relink_learned_bonus": 2\.2(?!\d)',
                  r"MOTION_RELINK_LEARNED_BONUS +2\.2(?!\d)",
                  r"ARM_STK3V velocity_weight=0\.25",
                  r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                  r"MOTION_RELINK_VELOCITY_WEIGHT +0\.25(?!\d)",
                  r"ARM_T60H tight_um=6\.0",
                  r'"motion_relink_tight_um": 6\.0(?!\d)',
                  r"MOTION_RELINK_TIGHT_UM +6\.0(?!\d)",
                  r"ARM_LCEFR patch applied to ",
                  r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                  r"mean_abs_off_vox=0\.\d*[1-9]",
                  r'"output_linefit_smooth": true',
                  r'"output_linefit_weight": 0\.8(?!\d)',
                  r'"output_linefit_window": 2(?!\d)'],
        # t65s3 = t6stk3 with the relink gate moved 6.0 -> 6.5. Same four components as t6stk3 but the tight
        # bracket is the OTHER value, so ARM_T65H and the 6.5 echo are pinned and a log that still carries
        # 6.0 is rejected negatively below. NOTE tight, velocity and bonus are three knobs on the SAME
        # linear_sum_assignment inside motion_relink_edges, so this is a re-test of the bracket under the
        # stk3 cost, not an independent component: t65h's 0.952 tie with t60h on the 0.951 body does not
        # carry over. This arm MOVES topology, so it is deliberately excluded from the T6_BODY pins; its
        # cell-5 receipt is the motion_relink_tight_edges monotonicity check instead.
        "t65s3": [r"ARM_STK3V velocity_weight=0\.25", r"ARM_STK3B learned_bonus=1\.6",
                  r'"motion_relink_velocity_weight": 0\.25(?!\d)',
                  r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                  r"ARM_T65H tight_um=6\.5",
                  r'"motion_relink_tight_um": 6\.5(?!\d)',
                  r"ARM_LCEFR patch applied to ",
                  r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                  r"mean_abs_off_vox=0\.\d*[1-9]",
                  r'"output_linefit_smooth": true',
                  r'"output_linefit_weight": 0\.8(?!\d)',
                  r'"output_linefit_window": 2(?!\d)'],
        # t60e: t60h (tight 6.0) stacked with lcefr (refined coords into the edge model): BOTH halves must fire.
        "t60e": [r"ARM_T60H tight_um=6\.0",
                 r'"motion_relink_tight_um": 6\.0(?!\d)',
                 r"ARM_LCEFR patch applied to ",
                 r"ARM_LCEFR pairs_refined=[1-9]\d* nodes_refined=[1-9]\d* diff_nodes=[1-9]\d* "
                 r"mean_abs_off_vox=0\.\d*[1-9]"],
        # gdiv: the post-processing of amanatar/biohub-geometric-fusion v3 (public 0.948) on the 0.951 hsg200 body:
        # DeepCenter safe-div threshold 0.25 -> 0.15, SAFE_DIV_MAX 9 -> 11, SISTER 14 -> 16, EXISTING_CHILD 10 -> 12,
        # plus prune_weak_leaf_nodes at edge_prob < 0.30. ARM_GDIV is printed in cell 2 from the realized globals
        # (after the float() conversion), and every changed knob is ALSO pinned through its CONFIG_DISPLAY echo.
        # Velocity (0.5) and tight (5.5) are pinned at the BASE values, so a leaked lcvel2 / stk3 / t60h edit cannot
        # pass under this name (geometric-fusion itself shipped velocity 0.25; gdiv deliberately does not).
        # GDIV_DS is printed per movie right after FINAL. At least one movie must really prune a leaf, otherwise the
        # prune never fired and the run is a division-only arm; the per-movie totals are checked further below.
        "gdiv": [r"ARM_GDIV deepcenter_safe_div_threshold=0\.15 safe_div_max_um=11\.0 safe_div_sister_max_um=16\.0 "
                 r"safe_div_existing_child_max_um=12\.0 leaf_prune_min_edge_prob=0\.3(?!\d)",
                 r'"deepcenter_safe_div_threshold": 0\.15(?!\d)',
                 r'"safe_div_max_um": 11\.0(?!\d)',
                 r'"safe_div_sister_max_um": 16\.0(?!\d)',
                 r'"safe_div_existing_child_max_um": 12\.0(?!\d)',
                 r'"leaf_prune_min_edge_prob": 0\.3(?!\d)',
                 r'"motion_relink_velocity_weight": 0\.5(?!\d)',
                 r'"motion_relink_tight_um": 5\.5(?!\d)',
                 r"GDIV_DS \[\w+\] leaf_pruned=[1-9]\d* leaf_pruned_edges=[1-9]\d* safe_divisions_added=\d+ "
                 r"division_parents=\d+"],
        # rawlink70: josephadamski91 V1057 raw-ILP override at min_prob 0.70 (0.30 was HELD: unseen-embryo screen
        # 9 up / 26 down). Every relink dial must sit at the base value so a leaked knob cannot pass.
        "rawlink70": [r"ARM_RAWLINK min_prob=0\.7(?!\d) enabled=True ",
                      r'"rawlink_min_prob": 0\.7(?!\d)',
                      r'"motion_relink_velocity_weight": 0\.5(?!\d)',
                      r'"motion_relink_learned_bonus": 1\.0(?!\d)',
                      r'"motion_relink_tight_um": 5\.5(?!\d)',
                      r"ARM_RAWLINK \[44b6_0113de3b\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                      r"ARM_RAWLINK \[44b6_0b24845f\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                      r"ARM_RAWLINK \[6bba_05b6850b\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* ",
                      r"ARM_RAWLINK \[6bba_05db0fb1\] min_prob=0\.7 candidates=\d+ accepted=[1-9]\d* "],
        # --- line-fit arms (lfds, lfw72) on the 0.951 hsg200 body: they change ONLY the written z/y/x ---
        # Both touch nothing but linefit_smooth_output_graph, the last step of filter_output_graph after every
        # topology decision. The exact CPU replay (real frames, real DeepCenter, which reproduced the real hsg200
        # submission row for row) gave node ids, t, edges and divisions identical to hsg200 on all 4 movies, so the
        # per-movie counts are pinned EXACTLY in the linefit block below, not by window.
        # lfds: zoli800's division-safe fit. Only strict linear nodes (1 in, 1 out) are smoothed and the window walk
        # stops at a non-linear node. The cell-0 print fires beside the os.environ line whether or not anything reads
        # it, so the cell-2 echo of the realized global is pinned too; weight/window stay at 0.8/2 so the ONLY change
        # is the switch. The proof that cell 5's patched function actually ran is linefit_smoothed_nodes in
        # run_stats.csv (checked in the block below), which the switch drops from 25610/20690/6162/70292.
        "lfds": [r"ARM_LFDS linefit=strict_linear_interior",
                 r'"output_linefit_strict_linear": true',
                 r'"output_linefit_smooth": true',
                 r'"output_linefit_weight": 0\.8(?!\d)',
                 r'"output_linefit_window": 2(?!\d)',
                 r'"motion_relink_velocity_weight": 0\.5(?!\d)',
                 r'"motion_relink_learned_bonus": 1\.0(?!\d)',
                 r'"motion_relink_tight_um": 5\.5(?!\d)'],
        # lfw72: OUTPUT_LINEFIT_WEIGHT 0.8 -> 0.72 via one cell-0 env line. The weight does not change WHICH nodes
        # are smoothed, so linefit_smoothed_nodes stays at hsg200's values and cannot prove anything; the cell-2
        # echo of the realized float is the evidence, and (?!\d) stops 0.725 or 0.7200001 from passing.
        "lfw72": [r"ARM_LFW72 linefit_weight=0\.72(?!\d)",
                  r'"output_linefit_weight": 0\.72(?!\d)',
                  r'"output_linefit_smooth": true',
                  r'"output_linefit_window": 2(?!\d)',
                  r'"motion_relink_velocity_weight": 0\.5(?!\d)',
                  r'"motion_relink_learned_bonus": 1\.0(?!\d)',
                  r'"motion_relink_tight_um": 5\.5(?!\d)']}
for pat in [q for t in tags for q in need.get(t, [])]:
    if not re.search(pat, txt): fails.append(f"marker missing: {pat}")
if "stkvb" in tags and re.search(r"ARM_LCEFR", txt):
    fails.append("stkvb is the velocity+bonus stack WITHOUT lcefr, but the log carries ARM_LCEFR: this run is "
                 "stk3 (or lcefr) wearing the two-component name, so its score cannot be read against stkve")
if "hspin" in tags and re.search(r"written_delta_bound=[^0\s]", txt):
    fails.append("written_delta_bound != 0 on at least one video (clip too wide for the live ds_arr: written coords would move)")
# ds_arr is (1,4,4), so |off_z| <= 0.4999 can NEVER change the written integer z: only the y and x gains can
# move a submitted coordinate. Require at least one video where the y/x pair is actually amplified.
if "hsadapt" in tags and not re.search(r"SV_ARM_HSADAPT nodes=\d+ gain_zyx=\d\.\d{3},(?!1\.000,1\.000)", txt):
    fails.append("every hsadapt video printed gain_y=gain_x=1.000: the adaptive gain clamped to its floor on both "
                 "axes that can move a written coordinate (z cannot, since |off|<0.5 and ds_z=1), so this run is "
                 "hsoftfix with a 0.4999 clip, not the amplification lever it claims to test")
# gdiv per-movie evidence. (a) Every movie must print GDIV_DS, or the per-movie claims below are unproven.
# (b) A pruned leaf has exactly one incoming edge and no outgoing one, so edges removed must EQUAL nodes removed;
# any mismatch means the prune took structure beyond leaves. (c) The division half must have reached
# add_safe_divisions_postlink: hsg200 (DC 0.25, windows 9/14/10) added 37/11/5/23 = 76 safe divisions on these
# same four movies. The looser threshold and wider windows admit a superset of candidates; the 09-22 box replay
# (real DeepCenter veto on CPU, real frames, which reproduced hsg200's submission byte for byte) forecasts
# 49/40/6/42 = 137 added and 10/11/2/53 leaves pruned. A total <= 76 means the new division knobs never took
# effect and the run is hsg200 plus the leaf prune.
if "gdiv" in tags:
    gd = {}
    for d, *vals in re.findall(r"GDIV_DS \[(\w+)\] leaf_pruned=(\d+) leaf_pruned_edges=(\d+) "
                               r"safe_divisions_added=(\d+) division_parents=(\d+)", txt):
        if d in REF and d not in gd: gd[d] = tuple(int(v) for v in vals)
    if set(gd) != set(REF): fails.append(f"GDIV_DS missing for {sorted(set(REF) - set(gd))}")
    for d, (lp, lpe, _, _) in sorted(gd.items()):
        if lp != lpe: fails.append(f"{d}: leaf_pruned={lp} != leaf_pruned_edges={lpe} (the prune removed more than leaves)")
    gd_added = sum(v[2] for v in gd.values())
    if gd and gd_added <= 76:
        fails.append(f"gdiv added {gd_added} safe divisions over {len(gd)} movies, not above hsg200's 76: the "
                     "0.15 threshold / 11-16-12 windows never reached add_safe_divisions_postlink")
RL_TAGS = {"rawlink70", "t6r70", "t6rlf", "t6r70T15", "t65b25r70", "ourvzlb25r70", "t65b25r70ff", "t65b25r70sr", "mixyx50r70", "t65b25r70ffsr", "ourvzlb25r70ff", "ourvzlt625", "ourvzlt675", "ourvzlb30", "ourvzlb20", "ourvzlsr", "ourvzllf100", "ourvzlb30t625", "ourvzlffb30", "ourvzlb35t625", "ourvzlb40t625", "ourvzlb30t600"}  # every arm that runs the raw-ILP override
if RL_TAGS & set(tags):
    # The single-change guard belongs to rawlink70 ALONE. Its pattern matches "ARM_STK" and "ARM_T60H",
    # which a legitimate t6r70 / t6rlf log carries by design, so reusing it verbatim would wrongly fail
    # the stacked arms. They get the T6_ALLOWED allowlist below instead, which is stricter.
    if "rawlink70" in tags and re.search(r"ARM_(LCEFR|LCFLOW2|LCVEL|LCBON|STK|T60H|GDIV)|GDIV_DS", txt):
        fails.append("rawlink70 log carries another arm's marker (lcefr/lcflow2/lcvel/lcbon/stk/t60h/gdiv): not the "
                     "single-change arm")
    rl = {}
    for m in re.finditer(r"ARM_RAWLINK \[(\w+)\] min_prob=\S+ candidates=(\d+) accepted=(\d+) replaced=(\d+) "
                         r"anchor=(\d+) final=(\d+) max_in=(\d+) max_out=(\d+) divs=(\d+)->(\d+) ", txt):
        if m.group(1) in REF and m.group(1) not in rl: rl[m.group(1)] = m
    if set(rl) != set(REF): fails.append(f"ARM_RAWLINK per-movie line missing for {sorted(set(REF) - set(rl))}")
    for d, m in sorted(rl.items()):
        c, a, r, n0, n1, mi, mo, d0, d1 = (int(v) for v in m.groups()[1:])
        fpos = txt.find(f"[{d}] FINAL:")
        if fpos < 0 or m.start() < fpos: fails.append(f"rawlink line for {d} is not after its FINAL line")
        if mi > 1 or mo > 2: fails.append(f"rawlink degree violation on {d}: in {mi} out {mo}")
        if d0 != d1: fails.append(f"rawlink changed the division count on {d}: {d0}->{d1}")
        if a > c: fails.append(f"rawlink accepted {a} > candidates {c} on {d}")
        if n1 != n0 + a - r: fails.append(f"rawlink edge arithmetic broken on {d}: {n0} + {a} - {r} != {n1}")
        if not 0.001 <= (a + r) / max(n0, 1) <= 0.10:
            fails.append(f"rawlink change fraction out of window on {d}: {(a + r) / max(n0, 1):.4f}")
    rl_acc = sum(int(m.group(3)) for m in rl.values())
    # Per-body accepted window, 0.5x-2.0x of that body's measured total: 1303 on the 0.951 hsg200 body
    # (offline replay) and 1113 on the 0.954 t6stk3 body (the real completed t6r70 run, 362/54/18/679,
    # reproduced independently by CPU replay). Deliberately a WINDOW and not an exact pin: the smallest
    # accepted probability on 6bba_05db0fb1 is 0.7003, 3e-4 above the cut, so one ULP of GPU drift can
    # flip a candidate. Node counts and divisions do not depend on that boundary, which is why they get
    # exact pins in the T6_BODY block instead.
    lo, hi = (651, 2606) if "rawlink70" in tags else (556, 2226)
    if rl and not lo <= rl_acc <= hi:
        fails.append(f"rawlink accepted {rl_acc} raw edges in total, outside [{lo}, {hi}] around this body's "
                     "measured total: not the expected body, or a linker knob leaked")
    # The override runs AFTER prune-isolated and after the min-track-len-6 filter, both of which live inside
    # filter_output_graph, so a node that loses its only edge to a replacement is never re-filtered and is
    # written as a length-1 track. That is rawlink's own property, small and measured (6/2/1/29 = 38 on the
    # 0.954 body), but nothing else in this gate looks at it. Cap it so a future threshold change cannot
    # silently shatter the graph; cell 6 checks degree, time and coordinates but never component size.
    if {"t6r70", "t6rlf", "t6r70T15", "t65b25r70", "ourvzlb25r70", "t65b25r70ff", "t65b25r70sr", "mixyx50r70", "t65b25r70ffsr", "ourvzlb25r70ff", "ourvzlt625", "ourvzlt675", "ourvzlb30", "ourvzlb20", "ourvzlsr", "ourvzllf100", "ourvzlb30t625", "ourvzlffb30", "ourvzlb35t625", "ourvzlb40t625", "ourvzlb30t600"} & set(tags):
        iso = {}
        for m in re.finditer(r"ARM_RAWLINK \[(\w+)\].*? new_isolated=(\d+)", txt):
            iso.setdefault(m.group(1), int(m.group(2)))
        bad = sorted(d for d, v in iso.items() if v > 50)
        if bad:
            fails.append(f"rawlink orphaned more than 50 nodes on {bad} (exact replay: 6/2/1/29): prune-isolated "
                         "and the min-len-6 filter both run INSIDE filter_output_graph, so the override's "
                         "replacements leave length-1 tracks that nothing removes")
        if iso and sum(iso.values()) > 150:
            fails.append(f"rawlink orphaned {sum(iso.values())} nodes in total, over the cap of 150 "
                         "(exact replay: 38)")
# Line-fit arms. Line-fit runs after the FINAL topology is fixed, so a clean run must reproduce hsg200's graph exactly:
# FINAL nodes/edges, safe divisions added (the "after safe-division repair" line), and the final division count
# (cell 10's "<movie>: nodes= edges= divisions=" line). Any drift means a topology knob leaked in or this is not the
# hsg200 body. ASSUMPTION: a Kaggle rerun of the same body reproduces these counts exactly (hsz0 reproduced hfast's
# 25637/20721/6152/70284 exactly; hsg200 itself has never been rerun). A mismatch FAILS, which is the safe direction.
# run_stats.csv is the file `kaggle kernels output` writes beside the log (run_today.py puts both in data/out_<tag>/);
# it is the only place linefit_smoothed_nodes appears, and without it the lfds patch has no runtime evidence.
LF_OWN = {"lfds": "LFDS", "lfw72": "LFW72"}
LF_HSG200 = {"44b6_0113de3b": (25619, 24894, 37), "44b6_0b24845f": (20693, 19400, 11),
             "6bba_05b6850b": (6162, 5964, 5), "6bba_05db0fb1": (70292, 68226, 23)}  # FINAL nodes, edges, safe divs
LF_SMOOTHED = {"lfds": {"44b6_0113de3b": 24084, "44b6_0b24845f": 18082, "6bba_05b6850b": 5754, "6bba_05db0fb1": 66112},
               "lfw72": {"44b6_0113de3b": 25610, "44b6_0b24845f": 20690, "6bba_05b6850b": 6162, "6bba_05db0fb1": 70292}}
for lt in [t for t in tags if t in LF_OWN]:
    # Single-change guard, generic on purpose: ANY other ARM_<X> print (existing or future: t60h, gdiv, rawlink,
    # lcefr, hoct, the other line-fit arm, ...), GDIV_DS, a non-hsg200 sub-voxel marker or the old SUBVOXEL_ACTIVE
    # body fails. \bARM_ cannot match inside SV_ARM_HSG200 because "_" and "A" are both word characters.
    foreign = sorted({f"ARM_{a}" for a in re.findall(r"\bARM_([A-Z0-9]+)", txt) if a != LF_OWN[lt]}
                     | set(re.findall(r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", txt))
                     | {k for k in ("GDIV_DS", "SUBVOXEL_ACTIVE") if k in txt})
    if foreign: fails.append(f"{lt} log carries another arm's marker {foreign}: not the single-change line-fit arm")
    if lt != "lfds" and re.search(r'"output_linefit_strict_linear": true', txt):
        fails.append(f"{lt} log echoes output_linefit_strict_linear=true: the lfds switch leaked into this arm")
    lf_fin, lf_sd, lf_dv = {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        lf_fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        lf_sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        lf_dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, (n0, e0, s0) in sorted(LF_HSG200.items()):
        if lf_fin.get(d) != (n0, e0):
            fails.append(f"{lt} {d} FINAL nodes/edges {lf_fin.get(d)} != hsg200 {(n0, e0)}: line-fit cannot move topology")
        if lf_sd.get(d) != s0:
            fails.append(f"{lt} {d} safe divisions added {lf_sd.get(d)} != hsg200 {s0}")
        if lf_dv.get(d) != (n0, e0, s0):
            fails.append(f"{lt} {d} final written nodes/edges/divisions {lf_dv.get(d)} != hsg200 {(n0, e0, s0)}")
    import csv, os
    rs_path = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    if not os.path.isfile(rs_path):
        fails.append(f"{lt}: no run_stats.csv beside the log, so linefit_smoothed_nodes / safe_divisions_added are unproven")
    else:
        with open(rs_path, newline="", encoding="utf-8") as fh:
            rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
        for d, (n0, e0, s0) in sorted(LF_HSG200.items()):
            r = rs.get(d) or {}
            try: got = tuple(int(float(r[k])) for k in ("nodes", "edges", "safe_divisions_added", "linefit_smoothed_nodes"))
            except (KeyError, TypeError, ValueError): got = None
            want = (n0, e0, s0, LF_SMOOTHED[lt][d])
            if got != want:
                why = ""
                if got is not None and got[3] != want[3]:
                    why = (": the strict-linear patch did not run" if lt == "lfds" else
                           ": line-fit smoothed a different node set, so the lfds switch (or another line-fit edit) leaked")
                fails.append(f"{lt} {d} run_stats (nodes, edges, safe_divisions_added, linefit_smoothed_nodes) {got} != "
                             f"replay {want}{why}")
# --- 09-23 STACK ROUND: everything built on the board-confirmed 0.954 t6stk3 body -------------------
# Three things `need` above cannot express.
# (a) An ALLOWLIST of the markers each arm may carry. The house denylists cannot be reused here:
#     rawlink70's pattern matches "ARM_STK" and "ARM_T60H", which these arms carry by design, and the
#     LF_OWN loop rejects any ARM_<X> but its own, which these arms also carry four of. A denylist would
#     additionally let a FUTURE ARM_<X> through unnoticed. ARM_LFDS and ARM_LFW72 are the same line-fit
#     family, so an allowlist is what keeps them from ever stacking. \bARM_ cannot match inside
#     SV_ARM_HSG200, because "_" and "A" are both word characters.
# (b) The body's topology, EXACTLY. The raw-ILP override only chooses between edges that already exist
#     and line-fit only rewrites coordinates, so none of these arms may move FINAL nodes/edges, the
#     safe-division count or the written division count off the real 0.954 run. t65s3 moves the relink
#     gate itself, so it is deliberately excluded from these pins and gets its own cell-5 receipt below.
# (c) run_stats.csv receipts. The cell-0 prints fire beside the os.environ assignment and the cell-2
#     echoes are read in cell 2, but the line-fit patch lives in cell 5 and linefit_smoothed_nodes /
#     linefit_skipped_nodes are its ONLY runtime evidence: without them t6lf is t6stk3 and t6rlf is t6r70
#     wearing the stacked name. Both are a deterministic function of the final topology and were
#     recomputed straight from the real t6stk3 submission.csv; the same recomputation reproduces
#     t6stk3's own 25609/20684/6158/70401 + 8/3/0/0 AND the real t6r70 run's identical pair, which is
#     what validates the strict-linear column. smoothed + skipped == nodes on every movie, checked too.
T6_ALLOWED = {"t6r70": {"STK3V", "STK3B", "T60H", "LCEFR", "RAWLINK"},
              "t6lf": {"STK3V", "STK3B", "T60H", "LCEFR", "LFDS"},
              "t6rlf": {"STK3V", "STK3B", "T60H", "LCEFR", "RAWLINK", "LFDS"},
              "t6w72": {"STK3V", "STK3B", "T60H", "LCEFR", "LFW72"},
              "t65s3": {"STK3V", "STK3B", "T65H", "LCEFR"},
              # The two dial extremes RENAME the knob they move, so the marker they replace must be gone:
              # t6v00 may not carry STK3V (velocity 0.25) and t6b22 may not carry STK3B (bonus 1.6). A build
              # that kept both would be the 0.954 body with a cosmetic extra print.
              "t6v00": {"T6V00", "STK3B", "T60H", "LCEFR"},
              "t6b22": {"STK3V", "T6B22", "T60H", "LCEFR"}}
T6_DIAL = {"t6v00", "t6b22"}  # relink-cost dials: they move topology, so no T6_BODY pins (see below)
T6_BODY = {"44b6_0113de3b": (25617, 24883, 36), "44b6_0b24845f": (20687, 19410, 13),   # FINAL nodes, FINAL
           "6bba_05b6850b": (6158, 5962, 5), "6bba_05db0fb1": (70401, 68282, 25)}      # edges, safe divs
T6_LINEFIT = {"base": {"44b6_0113de3b": (25609, 8), "44b6_0b24845f": (20684, 3),        # smoothed, skipped
                       "6bba_05b6850b": (6158, 0), "6bba_05db0fb1": (70401, 0)},
              "strict": {"44b6_0113de3b": (24068, 1549), "44b6_0b24845f": (18104, 2583),
                         "6bba_05b6850b": (5754, 404), "6bba_05db0fb1": (66113, 4288)}}
T6_LF_MODE = {"t6r70": "base", "t6w72": "base", "t6lf": "strict", "t6rlf": "strict"}
T6_TIGHT = {"44b6_0113de3b": 24453, "44b6_0b24845f": 19673,   # motion_relink_tight_edges at gate 6.0
            "6bba_05b6850b": 5871, "6bba_05db0fb1": 66525}    # (the real 0.954 run): a 6.5 run cannot go below
for t6 in [t for t in tags if t in T6_ALLOWED]:
    import csv, os  # needed here: the LF_OWN loop that imports these never runs for these tags
    foreign = sorted({f"ARM_{a}" for a in re.findall(r"\bARM_([A-Z0-9]+)", txt) if a not in T6_ALLOWED[t6]}
                     | set(re.findall(r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", txt))
                     | {k for k in ("GDIV_DS", "SUBVOXEL_ACTIVE") if k in txt})
    if foreign:
        fails.append(f"{t6} log carries {foreign}, which is not part of this stack: the run is not {t6}. "
                     "ARM_LFDS and ARM_LFW72 are the same line-fit family and must never stack together")
    if t6 not in ("t6lf", "t6rlf") and re.search(r'"output_linefit_strict_linear": true', txt):
        fails.append(f"{t6} log echoes output_linefit_strict_linear=true: the lfds switch leaked into an arm "
                     "that is supposed to run the base line-fit")
    rs_path = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    rs = None
    if os.path.isfile(rs_path):
        with open(rs_path, newline="", encoding="utf-8") as fh:
            rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    if t6 == "t65s3":
        if re.search(r'"motion_relink_tight_um": 6\.0(?!\d)', txt):
            fails.append("t65s3 log still echoes the 6.0 relink gate: the tight edit never reached the linker "
                         "and this run is t6stk3 wearing the t65s3 name")
        # Cell-5 receipt, and the only one this arm can have. Widening the gate can only ADD cells to the
        # gate-restricted bipartite graph the tight pass matches over (out-of-gate cells are filled with
        # gate*1000+1, so the pass is effectively a maximum-cardinality matching and its SIZE depends on the
        # gate alone, never on velocity/bonus), so motion_relink_tight_edges is monotone non-decreasing in
        # the gate and can never fall below the 0.954 run's counts. Requiring at least one movie STRICTLY
        # above them is what separates a real 6.5 run from a 6.0 run wearing the name: the box 2x2 on the
        # 0.954 geffs measured 24453 -> 24616 on 44b6_0113de3b under exactly this cost regime.
        if rs is None:
            fails.append("t65s3: no run_stats.csv beside the log, so motion_relink_tight_edges is unproven and "
                         "the 6.5 gate has no evidence it reached cell 5")
        else:
            got = {}
            for d in sorted(T6_TIGHT):
                try: got[d] = int(float((rs.get(d) or {})["motion_relink_tight_edges"]))
                except (KeyError, TypeError, ValueError): got[d] = None
            missing = sorted(d for d, v in got.items() if v is None)
            low = sorted(d for d, v in got.items() if v is not None and v < T6_TIGHT[d])
            if missing:
                fails.append(f"t65s3 run_stats has no readable motion_relink_tight_edges for {missing}")
            elif low:
                pairs = {d: (got[d], T6_TIGHT[d]) for d in low}
                fails.append(f"t65s3 motion_relink_tight_edges fell BELOW the 0.954 run's on {pairs} "
                             "(got, expected-floor): widening the gate can only admit more tight edges, so "
                             "this is not a 6.5 run on this body")
            elif not any(got[d] > T6_TIGHT[d] for d in got):
                fails.append(f"t65s3 motion_relink_tight_edges {got} is identical to the 0.954 run's on all "
                             "four movies: the 6.5 gate never reached motion_relink_edges")
        continue
    if t6 in T6_DIAL:
        # Same family as t65s3, for the same reason: velocity, bonus and tight are three knobs on ONE
        # linear_sum_assignment, and motion_relink_edges REPLACES the whole edge set, so these arms move
        # the graph and cannot take the T6_BODY pins. Two receipts instead of those.
        # (a) BODY. The tight pass's gate is UNCHANGED at 6.0 on both arms. Out-of-gate cells are filled
        #     with gate*1000 + 1 = 6001, ~500x the widest feasible in-gate cost, so that pass is
        #     effectively a maximum-cardinality matching over the gate-restricted bipartite graph and its
        #     SIZE depends on the gate and the node positions alone, never on velocity or bonus. The exact
        #     CPU replay on the 0.954 body's own raw ILP geffs -- whose t6stk3 arm reproduced the real
        #     t6stk3 submission row for row on all four movies -- measured motion_relink_tight_edges equal
        #     to T6_TIGHT for BOTH dials on every movie. Pinned as a 1% band rather than an exact equality,
        #     because a node can drift across the 6.0 um gate if the detector moves by one ULP on the GPU.
        # (b) NO-OP. This is the whole reason these two arms need an entry. Velocity 0.00 makes `predicted`
        #     equal `source_pos` in BOTH arms of the prev_pos branch, which is exactly what a knob that
        #     never arrived looks like; a bonus that never reaches the cost is the same story. If the run
        #     reproduces the 0.954 body's FINAL nodes AND edges exactly on all four movies, the dial
        #     changed nothing and its board reading is a false null. So require at least one movie to
        #     differ, while holding every movie inside a 2% band of the 0.954 body: that band is what says
        #     this is still that body and not some other pipeline. The replay forecast sits far inside it.
        if rs is None:
            fails.append(f"{t6}: no run_stats.csv beside the log, so motion_relink_tight_edges is unproven "
                         "and the dial has no cell-5 evidence at all")
        else:
            tight = {}
            for d in sorted(T6_TIGHT):
                try: tight[d] = int(float((rs.get(d) or {})["motion_relink_tight_edges"]))
                except (KeyError, TypeError, ValueError): tight[d] = None
            missing_t = sorted(d for d, v in tight.items() if v is None)
            if missing_t:
                fails.append(f"{t6} run_stats has no readable motion_relink_tight_edges for {missing_t}")
            off = {d: (tight[d], T6_TIGHT[d]) for d in sorted(tight)
                   if tight[d] is not None and abs(tight[d] - T6_TIGHT[d]) > 0.01 * T6_TIGHT[d]}
            if off:
                fails.append(f"{t6} motion_relink_tight_edges {off} (got, 0.954-run) moved more than 1%: the "
                             "tight gate is unchanged at 6.0 and that pass is a maximum-cardinality matching "
                             "over the gate graph, so velocity/bonus cannot move it this far -- the relink "
                             "gate or the body itself is not what this arm claims")
        t6_fin_d = {}
        for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
            t6_fin_d.setdefault(d, (int(n_), int(e_)))
        missing_f = sorted(d for d in T6_BODY if d not in t6_fin_d)
        if missing_f:
            fails.append(f"{t6}: no FINAL nodes/edges line for {missing_f}")
        far = {d: (t6_fin_d[d], (T6_BODY[d][0], T6_BODY[d][1])) for d in sorted(T6_BODY) if d in t6_fin_d
               and (abs(t6_fin_d[d][0] - T6_BODY[d][0]) > 0.02 * T6_BODY[d][0]
                    or abs(t6_fin_d[d][1] - T6_BODY[d][1]) > 0.02 * T6_BODY[d][1])}
        if far:
            fails.append(f"{t6} FINAL nodes/edges {far} (got, 0.954-run) moved more than 2% off the 0.954 "
                         "body: one relink dial cannot reshape the graph this much, so this is not that body")
        if not missing_f and all(t6_fin_d[d] == (T6_BODY[d][0], T6_BODY[d][1]) for d in T6_BODY):
            fails.append(f"{t6} reproduced the 0.954 body's FINAL nodes AND edges EXACTLY on all four "
                         "movies: the dial never reached motion_relink_edges, so this run IS t6stk3 wearing "
                         "the arm's name and its board reading would be a false null")
        continue
    t6_fin, t6_sd, t6_dv, rl_fin = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        t6_fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        t6_sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        t6_dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        rl_fin.setdefault(d, int(f_))
    has_rl = t6 in ("t6r70", "t6rlf")
    if rs is None:
        fails.append(f"{t6}: no run_stats.csv beside the log, so the line-fit counters are unproven and the "
                     "line-fit half of this stack has no runtime evidence")
    for d, (n0, e0, s0) in sorted(T6_BODY.items()):
        # Written edges: the override rewires AFTER the FINAL print, so on a rawlink arm cell 10 must equal
        # the override's own final= count and NOT e0. Cross-checking two independent prints beats pinning
        # either alone. A missing ARM_RAWLINK line is already reported by the rawlink block above.
        we = rl_fin.get(d) if has_rl else e0
        if t6_fin.get(d) != (n0, e0):
            fails.append(f"{t6} {d} FINAL nodes/edges {t6_fin.get(d)} != the 0.954 body's {(n0, e0)}: neither "
                         "the raw-ILP override (it only chooses between edges that already exist) nor "
                         "line-fit (it returns only coordinates) can move the pre-override graph")
        if t6_sd.get(d) != s0:
            fails.append(f"{t6} {d} safe divisions added {t6_sd.get(d)} != the 0.954 body's {s0}")
        if we is not None and t6_dv.get(d) != (n0, we, s0):
            fails.append(f"{t6} {d} written nodes/edges/divisions {t6_dv.get(d)} != {(n0, we, s0)}"
                         + (": edges cross-checked against the override's own final= count, and the override "
                            "is division-protected" if has_rl else ""))
        if rs is None:
            continue
        r = rs.get(d) or {}
        sm, sk = T6_LINEFIT[T6_LF_MODE[t6]][d]
        try:
            got = tuple(int(float(r[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                   "linefit_smoothed_nodes", "linefit_skipped_nodes"))
        except (KeyError, TypeError, ValueError):
            got = None
        want = (n0, we if we is not None else e0, s0, sm, sk)
        if got != want:
            why = ""
            if got is not None and T6_LF_MODE[t6] == "strict" and (got[3], got[4]) == T6_LINEFIT["base"][d]:
                why = (" -- linefit smoothed/skipped still read the BASE line-fit's values, so the "
                       "strict-linear switch never reached cell 5 and this run is the same stack without lfds")
            fails.append(f"{t6} {d} run_stats (nodes, edges, safe_divisions_added, linefit_smoothed_nodes, "
                         f"linefit_skipped_nodes) {got} != {want}{why}")
        if got is not None and got[3] + got[4] != n0:
            fails.append(f"{t6} {d} line-fit smoothed {got[3]} + skipped {got[4]} != {n0} nodes: the smoother "
                         "visits every node exactly once, so these two must add up")
sv_mark = {"t6gtri": "SV_ARM_HSG200", "hspin": "SV_ARM_HSPIN",  # arms that rename the sub-voxel marker
           "hsg2c04": "SV_ARM_HSG2C04",  # gain 2.00 at the tighter 0.40 clip
           "hsgzc10": "SV_ARM_HSGZC10",  # gain 2.00 at the per-axis clip z=1.0000, y/x=0.4999
           "hsadapt": "SV_ARM_HSADAPT",  # hsadapt renames it too: 'hsadapt' does NOT start with 'hsoft'
           "hsz0": "SUBVOXEL_ACTIVE",  # hsz0 keeps SUBVOXEL_ACTIVE and adds SV_ARM_HSZ0 (checked in `need`)
           "hsg200": "SV_ARM_HSG200", "hsg050": "SV_ARM_HSG050", "hswin2": "SV_ARM_HSWIN2",
           "hsg175": "SV_ARM_HSG175", "hsg250": "SV_ARM_HSG250",
           "hsg3c04": "SV_ARM_HSG3C04",  # gain 3.00 at the tighter 0.40 clip
           # The three linker arms do not touch the sub-voxel block at all: they carry hsg200's cell 4 byte for
           # byte, so their BODY marker is SV_ARM_HSG200. Listing them here makes the >= 4 lines check below run
           # for them too, which is the half of the two-marker scheme that proves WHICH body the linker knob ran
           # on. Without it the gate would happily pass an lcvel2 log produced from the old 0.949 hsoftfix body,
           # and the resulting score would be compared against the wrong baseline.
           # lcefr does not touch the sub-voxel block either: it carries hsg200's cell 4 with one purely
           # additive block appended, so SV_ARM_HSG200 must still print its usual >= 4 lines. That is the
           # half of the scheme that proves the linker rewiring ran on the 0.951 body and not on an older one.
           "lcvel2": "SV_ARM_HSG200", "lcbonus2": "SV_ARM_HSG200", "lcflow2": "SV_ARM_HSG200",
           "lcefr": "SV_ARM_HSG200",
           # The stacks and the two limit arms are all built off the same 0.951 body and leave the sub-voxel
           # block untouched (their cell 4 is hsg200's, byte for byte for the non-lcefr arms, and hsg200's
           # plus lcefr's purely additive block for the rest), so their BODY marker is SV_ARM_HSG200 too.
           # Listing them makes the ">= 4 marker lines before 'Prediction completed'" check run for them,
           # which is what proves the linker knobs ran on the 0.951 body and not on an older one.
           "stk3": "SV_ARM_HSG200", "stkve": "SV_ARM_HSG200", "stkvb": "SV_ARM_HSG200",
           "lcvel0": "SV_ARM_HSG200", "lcbon22": "SV_ARM_HSG200", "t60h": "SV_ARM_HSG200",
           # gdiv changes only cell-0 env values and cell-2/cell-5 post-processing; cell 4 is hsg200's byte for
           # byte, so its BODY marker is SV_ARM_HSG200 and the >= 4 lines check proves it ran on the 0.951 body.
           "gdiv": "SV_ARM_HSG200", "rawlink70": "SV_ARM_HSG200",
           # The line-fit arms change only cell 0/2 env reads and (lfds) cell 5's line-fit; cell 4 is hsg200's byte
           # for byte, so the >= 4 SV_ARM_HSG200 lines check proves they ran on the 0.951 body.
           "lfds": "SV_ARM_HSG200", "lfw72": "SV_ARM_HSG200", "t65h": "SV_ARM_HSG200", "t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200", "ourvzlb30t600": "SV_ARM_HSG200", "ourvzlb40t625": "SV_ARM_HSG200", "ourvzlb35t625": "SV_ARM_HSG200", "ourvzlffb30": "SV_ARM_HSG200", "ourvzlb30t625": "SV_ARM_HSG200", "ourvzllf100": "SV_ARM_HSG200", "ourvzlsr": "SV_ARM_HSG200", "ourvzlb20": "SV_ARM_HSG200", "ourvzlb30": "SV_ARM_HSG200", "ourvzlt675": "SV_ARM_HSG200", "ourvzlt625": "SV_ARM_HSG200", "ourvzlb25r70ff": "SV_ARM_HSG200", "t65b25r70ffsr": "SV_ARM_HSG200", "mixyx50r70": "SV_ARM_HSG200", "t65b25r70sr": "SV_ARM_HSG200", "t65b25r70ff": "SV_ARM_HSG200", "ourvzlb25r70": "SV_ARM_HSG200", "t675b25": "SV_ARM_HSG200", "t65b20d04": "SV_ARM_HSG200", "t70b25": "SV_ARM_HSG200", "t70b20": "SV_ARM_HSG200", "ourvzlb25": "SV_ARM_HSG200", "t65b25r70": "SV_ARM_HSG200", "t65b25": "SV_ARM_HSG200", "t65b20": "SV_ARM_HSG200", "t6stk3fl": "SV_ARM_HSG200", "t6stk3ff2": "SV_ARM_HSG200", "t65s3ff": "SV_ARM_HSG200", "t6stk3ff": "SV_ARM_HSG200",
           # The 09-23 stack arms carry t6stk3's cell 4 byte for byte (hsg200's sub-voxel block plus
           # lcefr's purely additive one), so their BODY marker is SV_ARM_HSG200 as well. These keys are
           # NOT optional: without them sv_tags comes back empty for the tag and the ">= 4 SV_ARM_HSG200
           # lines before 'Prediction completed'" check silently does not run at all, while run_today.py's
           # "has a gate entry for this tag" precheck is already satisfied by the `need` entry alone. That
           # check is the half of the two-marker scheme that proves the linker knobs ran on the 0.951
           # sub-voxel body and not on an older one. A real run on this body prints 8 such lines.
           "t6r70": "SV_ARM_HSG200", "t6lf": "SV_ARM_HSG200", "t6rlf": "SV_ARM_HSG200",
           "t6w72": "SV_ARM_HSG200", "t65s3": "SV_ARM_HSG200",
           # The two relink dials touch cell 0 only; their cell 4 is t6stk3's byte for byte (verified by
           # hash), so their BODY marker is SV_ARM_HSG200 and the ">= 4 lines" check proves the dial ran on
           # the 0.951 sub-voxel body. A real run on this body prints 8 such lines.
           "t6v00": "SV_ARM_HSG200", "t6b22": "SV_ARM_HSG200",
           # The x138 merge arms carry OUR sub-voxel block (hsg200's, byte for byte) spliced into
           # x138's cell 4 where its V1284 head used to sit, so their body marker is SV_ARM_HSG200
           # and the ">= 4 lines before Prediction completed" check proves the refinement reached
           # the test set. xbase is deliberately ABSENT here: it has no coordinate refinement at
           # all, and `forbid` below fails it if an SV marker ever appears in its log.
           "xsv": "SV_ARM_HSG200", "xsvb": "SV_ARM_HSG200", "xsvf": "SV_ARM_HSG200",
           "xsvt": "SV_ARM_HSG200", "xsvd": "SV_ARM_HSG200", "xsv96": "SV_ARM_HSG200",
           "xsvdv": "SV_ARM_HSG200", "xsvdc": "SV_ARM_HSG200",
           "xsvdd": "SV_ARM_HSG200", "xsvd10": "SV_ARM_HSG200",
           "xsvwz": "SV_ARM_HSG200", "xsvmx": "SV_ARM_HSG200",
           "xsvdu": "SV_ARM_HSG200", "xsvmp": "SV_ARM_HSG200", "xsvsr": "SV_ARM_HSG200",
           "xsvgc": "SV_ARM_HSG200", "xsvp26": "SV_ARM_HSG200", "xsvmax": "SV_ARM_HSG200",
           "t6dv": "SV_ARM_HSG200", "t6dc": "SV_ARM_HSG200", "t6dd": "SV_ARM_HSG200",
           "t6wz": "SV_ARM_HSG200", "t6sr": "SV_ARM_HSG200", "synp": "SV_ARM_HSG200",
           "ddsr": "SV_ARM_HSG200", "t6dl": "SV_ARM_HSG200", "xpubz": "SV_ARM_HSG200"}
# --- t6r70T15 (ops/add_r70T_gate.py): t6r70 + SV softmax temperature. The SV change moves node coordinates and so
# the graph, which is why the T6_BODY exact topology pins do NOT apply. Instead the override's bookkeeping is
# cross-checked per movie against this run's own prints: cell-10 written nodes/edges/divisions must equal
# (FINAL nodes, ARM_RAWLINK final=, safe divisions added), run_stats must agree, and line-fit smoothed + skipped
# must equal nodes. sv_mark is set here, BEFORE sv_tags is computed, so the >= 4 SV lines check runs for it.
sv_mark["t6r70T15"] = "SV_ARM_HSG200"
if "t6r70T15" in tags:
    import csv, os
    _fin, _sd, _dv, _rlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _rlf.setdefault(d, int(f_))
    _rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _rs = None
    if os.path.isfile(_rsp):
        with open(_rsp, newline="", encoding="utf-8") as fh:
            _rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t6r70T15: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _fin or d not in _sd or d not in _rlf:
            fails.append(f"t6r70T15 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _want = (_fin[d][0], _rlf[d], _sd[d])
        if _dv.get(d) != _want:
            fails.append(f"t6r70T15 {d} written nodes/edges/divisions {_dv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_want}")
        if _rs is not None:
            _r = _rs.get(d) or {}
            try:
                _got = tuple(int(float(_r[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                         "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got is None or _got[:3] != _want or _got[3] + _got[4] != _want[0]:
                fails.append(f"t6r70T15 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_got} "
                             f"inconsistent with {_want} (smoothed + skipped must equal nodes)")
# --- t65b25r70 (ops/add_t65b25r70_gate.py): t6r70 + t65b25's linker (tight 6.5, bonus 2.5). The linker change moves
# topology, so the T6_BODY exact pins do NOT apply; as for t6r70T15, the override's bookkeeping is cross-checked per
# movie against this run's own prints: cell-10 written nodes/edges/divisions == (FINAL nodes, ARM_RAWLINK final=,
# safe divisions added), run_stats agrees, line-fit smoothed + skipped == nodes.
if "t65b25r70" in tags:
    import csv, os
    _xfin, _xsd, _xdv, _xrlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _xfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _xsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _xdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _xrlf.setdefault(d, int(f_))
    _xrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _xrs = None
    if os.path.isfile(_xrsp):
        with open(_xrsp, newline="", encoding="utf-8") as fh:
            _xrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t65b25r70: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _xfin or d not in _xsd or d not in _xrlf:
            fails.append(f"t65b25r70 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _xwant = (_xfin[d][0], _xrlf[d], _xsd[d])
        if _xdv.get(d) != _xwant:
            fails.append(f"t65b25r70 {d} written nodes/edges/divisions {_xdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_xwant}")
        if _xrs is not None:
            _xr = _xrs.get(d) or {}
            try:
                _xgot = tuple(int(float(_xr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _xgot = None
            if _xgot is None or _xgot[:3] != _xwant or _xgot[3] + _xgot[4] != _xwant[0]:
                fails.append(f"t65b25r70 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_xgot} "
                             f"inconsistent with {_xwant} (smoothed + skipped must equal nodes)")
# --- t70b20 (ops/add_t70b20_gate.py): t65b20 with the relink TIGHT gate 6.5 -> 7.0. Cell-5 receipt, as for t65s3:
# out-of-gate cells cost gate*1000+1, so the tight pass is effectively a maximum-cardinality matching over the
# gate-restricted bipartite graph; its size depends on the gate and the node positions alone (never velocity or
# bonus) and is monotone non-decreasing in the gate. The real 6.5-gate runs (t65s3, t65b20, t65b25) all logged
# exactly the counts below; a 7.0 run can never fall below them and must exceed them on at least one movie.
if "t70b20" in tags:
    import csv, os
    _T70_FLOOR = {'44b6_0113de3b': 24616, '44b6_0b24845f': 19921, '6bba_05b6850b': 5911, '6bba_05db0fb1': 67052}
    _trsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    if not os.path.isfile(_trsp):
        fails.append("t70b20: no run_stats.csv beside the log, so motion_relink_tight_edges is unproven and "
                     "the 7.0 gate has no evidence it reached cell 5")
    else:
        with open(_trsp, newline="", encoding="utf-8") as fh:
            _trs = {r.get("dataset"): r for r in csv.DictReader(fh)}
        _tgot = {}
        for d in sorted(_T70_FLOOR):
            try: _tgot[d] = int(float((_trs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _tgot[d] = None
        _tmiss = sorted(d for d, v in _tgot.items() if v is None)
        _tlow = {d: (v, _T70_FLOOR[d]) for d, v in sorted(_tgot.items()) if v is not None and v < _T70_FLOOR[d]}
        if _tmiss:
            fails.append(f"t70b20 run_stats has no readable motion_relink_tight_edges for {_tmiss}")
        elif _tlow:
            fails.append(f"t70b20 motion_relink_tight_edges fell BELOW the 6.5-gate runs' on {_tlow} (got, floor): "
                         "widening the gate can only admit more tight edges, so this is not a 7.0 run on this body")
        elif not any(_tgot[d] > _T70_FLOOR[d] for d in _tgot):
            fails.append(f"t70b20 motion_relink_tight_edges {_tgot} equal the 6.5-gate runs' on all four movies: "
                         "the 7.0 gate never reached motion_relink_edges")
# --- t70b25 (ops/add_t70b25_gate.py): t70b20 with the learned bonus 2.0 -> 2.5, tight gate still 7.0. Same cell-5
# receipt as t70b20, against the same 6.5-gate counts: the tight pass is effectively a maximum-cardinality matching
# over the gate graph, so its size never depends on the bonus (t65s3 / t65b20 / t65b25 = bonus 1.6 / 2.0 / 2.5 all
# logged exactly these counts) and a 7.0 run can never fall below them and must exceed them on at least one movie.
if "t70b25" in tags:
    import csv, os
    _T70B25_FLOOR = {'44b6_0113de3b': 24616, '44b6_0b24845f': 19921, '6bba_05b6850b': 5911, '6bba_05db0fb1': 67052}
    _trsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    if not os.path.isfile(_trsp):
        fails.append("t70b25: no run_stats.csv beside the log, so motion_relink_tight_edges is unproven and "
                     "the 7.0 gate has no evidence it reached cell 5")
    else:
        with open(_trsp, newline="", encoding="utf-8") as fh:
            _trs = {r.get("dataset"): r for r in csv.DictReader(fh)}
        _tgot = {}
        for d in sorted(_T70B25_FLOOR):
            try: _tgot[d] = int(float((_trs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _tgot[d] = None
        _tmiss = sorted(d for d, v in _tgot.items() if v is None)
        _tlow = {d: (v, _T70B25_FLOOR[d]) for d, v in sorted(_tgot.items()) if v is not None and v < _T70B25_FLOOR[d]}
        if _tmiss:
            fails.append(f"t70b25 run_stats has no readable motion_relink_tight_edges for {_tmiss}")
        elif _tlow:
            fails.append(f"t70b25 motion_relink_tight_edges fell BELOW the 6.5-gate runs' on {_tlow} (got, floor): "
                         "widening the gate can only admit more tight edges, so this is not a 7.0 run on this body")
        elif not any(_tgot[d] > _T70B25_FLOOR[d] for d in _tgot):
            fails.append(f"t70b25 motion_relink_tight_edges {_tgot} equal the 6.5-gate runs' on all four movies: "
                         "the 7.0 gate never reached motion_relink_edges")
# --- t675b25 (ops/add_t675b25_gate.py): t65b25 with the relink TIGHT gate 6.5 -> 6.75. Cell-5 receipt, as for t70b20:
# out-of-gate cells cost gate*1000+1, so the tight pass is effectively a maximum-cardinality matching over the
# gate-restricted bipartite graph; its size depends on the gate and the node positions alone (never velocity or
# bonus) and is monotone non-decreasing in the gate. The real 6.5-gate runs (t65s3, t65b20, t65b25) all logged
# exactly the counts below; a 6.75 run can never fall below them and must exceed them on at least one movie.
if "t675b25" in tags:
    import csv, os
    _T675_FLOOR = {'44b6_0113de3b': 24616, '44b6_0b24845f': 19921, '6bba_05b6850b': 5911, '6bba_05db0fb1': 67052}
    _trsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    if not os.path.isfile(_trsp):
        fails.append("t675b25: no run_stats.csv beside the log, so motion_relink_tight_edges is unproven and "
                     "the 6.75 gate has no evidence it reached cell 5")
    else:
        with open(_trsp, newline="", encoding="utf-8") as fh:
            _trs = {r.get("dataset"): r for r in csv.DictReader(fh)}
        _tgot = {}
        for d in sorted(_T675_FLOOR):
            try: _tgot[d] = int(float((_trs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _tgot[d] = None
        _tmiss = sorted(d for d, v in _tgot.items() if v is None)
        _tlow = {d: (v, _T675_FLOOR[d]) for d, v in sorted(_tgot.items()) if v is not None and v < _T675_FLOOR[d]}
        if _tmiss:
            fails.append(f"t675b25 run_stats has no readable motion_relink_tight_edges for {_tmiss}")
        elif _tlow:
            fails.append(f"t675b25 motion_relink_tight_edges fell BELOW the 6.5-gate runs' on {_tlow} (got, floor): "
                         "widening the gate can only admit more tight edges, so this is not a 6.75 run on this body")
        elif not any(_tgot[d] > _T675_FLOOR[d] for d in _tgot):
            fails.append(f"t675b25 motion_relink_tight_edges {_tgot} equal the 6.5-gate runs' on all four movies: "
                         "the 6.75 gate never reached motion_relink_edges")
# --- ourvzlb25r70 (ops/add_ourvzlb25r70_gate.py): ourvzlb25 + t6r70's rawlink 0.70. Same per-movie cross-check as
# t65b25r70 (generated from its block): cell-10 written nodes/edges/divisions == (FINAL nodes, ARM_RAWLINK final=,
# safe divisions added), run_stats agrees, line-fit smoothed + skipped == nodes.
if "ourvzlb25r70" in tags:
    import csv, os
    _ovfin, _ovsd, _ovdv, _ovrlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _ovfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _ovsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _ovdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _ovrlf.setdefault(d, int(f_))
    _ovrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _ovrs = None
    if os.path.isfile(_ovrsp):
        with open(_ovrsp, newline="", encoding="utf-8") as fh:
            _ovrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlb25r70: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _ovfin or d not in _ovsd or d not in _ovrlf:
            fails.append(f"ourvzlb25r70 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _ovwant = (_ovfin[d][0], _ovrlf[d], _ovsd[d])
        if _ovdv.get(d) != _ovwant:
            fails.append(f"ourvzlb25r70 {d} written nodes/edges/divisions {_ovdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_ovwant}")
        if _ovrs is not None:
            _ovr = _ovrs.get(d) or {}
            try:
                _ovgot = tuple(int(float(_ovr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _ovgot = None
            if _ovgot is None or _ovgot[:3] != _ovwant or _ovgot[3] + _ovgot[4] != _ovwant[0]:
                fails.append(f"ourvzlb25r70 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_ovgot} "
                             f"inconsistent with {_ovwant} (smoothed + skipped must equal nodes)")
# --- t65b25r70ff (ops/add_t65b25r70ff_gate.py): t65b25r70 + ARM_FLOWFIX after the rawlink override. Per movie the
# repair must start from the override's own output (flowfix edges A == ARM_RAWLINK final=) and write B = A + bridged -
# dups; divisions unchanged (== safe divisions added), in-degree <= 1, <= 20 s/movie; cell-10 written nodes/edges/
# divisions == (FINAL nodes, B, safe divisions added); run_stats agrees (edges == B, rawlink_final_edges == A,
# flowfix_status ok, changed/bridged/dups as logged, line-fit smoothed + skipped == nodes); changed > 0 somewhere.
if "t65b25r70ff" in tags:
    import csv, os
    _ffxfin, _ffxsd, _ffxdv, _ffxrl = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _ffxfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _ffxsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _ffxdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for _ffxm in re.finditer(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _ffxrl.setdefault(_ffxm.group(1), (int(_ffxm.group(2)), _ffxm.start()))
    _ffxrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _ffxrs = None
    if os.path.isfile(_ffxrsp):
        with open(_ffxrsp, newline="", encoding="utf-8") as fh:
            _ffxrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t65b25r70ff: no run_stats.csv beside the log, so the written counts and flowfix counters are unproven")
    _ffxchg = []
    for d in sorted(REF):
        if d not in _ffxfin or d not in _ffxsd or d not in _ffxrl:
            fails.append(f"t65b25r70ff {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _ffxm = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                          r"bridged=(\d+) dups=(\d+) edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _ffxm:
            fails.append(f"t65b25r70ff {d}: no ARM_FLOWFIX status=ok line")
            continue
        _ffxg = [int(v) for v in _ffxm.groups()[:11]]
        _ffxch, _ffxbr, _ffxdu, _ffxa0, _ffxa1, _ffxv0, _ffxv1, _ffxmi = _ffxg[3:11]
        _ffxn, _ffxs = _ffxfin[d][0], _ffxsd[d]
        _ffxchg.append(_ffxch)
        if _ffxm.start() < _ffxrl[d][1] or _ffxm.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"t65b25r70ff {d}: ARM_FLOWFIX line is not after the movie's FINAL and ARM_RAWLINK lines: the "
                         "repair must act on the override's output")
        if _ffxa0 != _ffxrl[d][0]:
            fails.append(f"t65b25r70ff {d}: flowfix input edges {_ffxa0} != ARM_RAWLINK final={_ffxrl[d][0]}: the repair "
                         "did not start from the override's output")
        if _ffxa1 != _ffxa0 + _ffxbr - _ffxdu:
            fails.append(f"t65b25r70ff {d}: flowfix edges {_ffxa0}->{_ffxa1} inconsistent with {_ffxa0} + bridged "
                         f"{_ffxbr} - dups {_ffxdu}")
        if _ffxv0 != _ffxv1 or _ffxv1 != _ffxs or _ffxmi > 1:
            fails.append(f"t65b25r70ff {d}: flowfix divisions {_ffxv0}->{_ffxv1} (want {_ffxs}) or in-degree {_ffxmi}")
        if float(_ffxm.group(12)) > 20.0:
            fails.append(f"t65b25r70ff {d}: flowfix {_ffxm.group(12)} s > 20 s/movie (hidden overhead > ~66 min)")
        _ffxwant = (_ffxn, _ffxa1, _ffxs)
        if _ffxdv.get(d) != _ffxwant:
            fails.append(f"t65b25r70ff {d} written nodes/edges/divisions {_ffxdv.get(d)} != (FINAL nodes, flowfix B, "
                         f"safe divisions) {_ffxwant}")
        if _ffxrs is not None:
            _ffxr = _ffxrs.get(d) or {}
            try:
                _ffxgot = tuple(int(float(_ffxr[k])) for k in (
                    "nodes", "edges", "safe_divisions_added", "linefit_smoothed_nodes", "linefit_skipped_nodes",
                    "rawlink_final_edges", "flowfix_changed", "flowfix_bridged", "flowfix_dups"))
                _ffxst = _ffxr["flowfix_status"]
            except (KeyError, TypeError, ValueError):
                _ffxgot, _ffxst = None, None
            if _ffxgot is None or _ffxgot[:3] != _ffxwant or _ffxgot[3] + _ffxgot[4] != _ffxn \
                    or _ffxgot[5] != _ffxa0 or _ffxgot[6:] != (_ffxch, _ffxbr, _ffxdu) or _ffxst != "ok":
                fails.append(f"t65b25r70ff {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped, "
                             f"rawlink_final_edges, flowfix changed/bridged/dups) {_ffxgot} status {_ffxst} inconsistent "
                             f"with {_ffxwant} / rawlink final {_ffxa0} / flowfix {(_ffxch, _ffxbr, _ffxdu)} ok")
    if not _ffxchg or max(_ffxchg) == 0:
        fails.append("t65b25r70ff: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
# --- t65b25r70sr (ops/add_t65b25r70sr_gate.py): t65b25r70 + short-track rescue armed (trigger 0.0). The
# t65b25r70 per-movie cross-check (generated from its block: written nodes/edges/divisions == (FINAL nodes,
# ARM_RAWLINK final=, safe divisions added), run_stats agrees, smoothed + skipped == nodes) + rescue receipts.
if "t65b25r70sr" in tags:
    import csv, os
    _srxfin, _srxsd, _srxdv, _srxrlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _srxfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _srxsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _srxdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _srxrlf.setdefault(d, int(f_))
    _srxrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _srxrs = None
    if os.path.isfile(_srxrsp):
        with open(_srxrsp, newline="", encoding="utf-8") as fh:
            _srxrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t65b25r70sr: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _srxfin or d not in _srxsd or d not in _srxrlf:
            fails.append(f"t65b25r70sr {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _srxwant = (_srxfin[d][0], _srxrlf[d], _srxsd[d])
        if _srxdv.get(d) != _srxwant:
            fails.append(f"t65b25r70sr {d} written nodes/edges/divisions {_srxdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_srxwant}")
        if _srxrs is not None:
            _srxr = _srxrs.get(d) or {}
            try:
                _srxgot = tuple(int(float(_srxr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _srxgot = None
            if _srxgot is None or _srxgot[:3] != _srxwant or _srxgot[3] + _srxgot[4] != _srxwant[0]:
                fails.append(f"t65b25r70sr {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_srxgot} "
                             f"inconsistent with {_srxwant} (smoothed + skipped must equal nodes)")
    # rescue receipts (ops/add_t65b25r70sr_gate.py): the rescue prints no line of its own, so run_stats is the only
    # evidence. Trigger 0.0 => the branch runs on every movie (triggered == 1); components <= nodes <= budget; and
    # at least one visible movie must get components back, otherwise the armed branch did nothing.
    if _srxrs is not None:
        _srxcomp = []
        for d in sorted(REF):
            _srxrow = _srxrs.get(d) or {}
            try:
                _srxq = tuple(int(float(_srxrow[k])) for k in ("short_track_rescue_triggered", "short_track_rescue_components",
                                                             "short_track_rescue_nodes", "short_track_rescue_budget"))
            except (KeyError, TypeError, ValueError):
                _srxq = None
            if _srxq is None:
                fails.append(f"t65b25r70sr {d}: run_stats has no readable short_track_rescue_* columns")
                continue
            if _srxq[0] != 1:
                fails.append(f"t65b25r70sr {d}: short_track_rescue_triggered={_srxq[0]}: with trigger 0.0 the rescue "
                             "branch must run on every movie")
            if not 0 <= _srxq[1] <= _srxq[2] <= _srxq[3]:
                fails.append(f"t65b25r70sr {d}: rescued components/nodes/budget {_srxq[1:]} inconsistent "
                             "(components <= nodes <= budget)")
            _srxcomp.append(_srxq[1])
        if not _srxcomp or max(_srxcomp) == 0:
            fails.append("t65b25r70sr: the armed rescue restored 0 components on every visible movie: the branch did nothing")
# --- mixyx50r70 (ops/add_mixyx50r70_gate.py): ourvzlb25r70's per-movie cross-check (generated from its block):
# cell-10 written nodes/edges/divisions == (FINAL nodes, ARM_RAWLINK final=, safe divisions added), run_stats
# agrees, line-fit smoothed + skipped == nodes.
if "mixyx50r70" in tags:
    import csv, os
    _mxfin, _mxsd, _mxdv, _mxrlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _mxfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _mxsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _mxdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _mxrlf.setdefault(d, int(f_))
    _mxrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _mxrs = None
    if os.path.isfile(_mxrsp):
        with open(_mxrsp, newline="", encoding="utf-8") as fh:
            _mxrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("mixyx50r70: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _mxfin or d not in _mxsd or d not in _mxrlf:
            fails.append(f"mixyx50r70 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _mxwant = (_mxfin[d][0], _mxrlf[d], _mxsd[d])
        if _mxdv.get(d) != _mxwant:
            fails.append(f"mixyx50r70 {d} written nodes/edges/divisions {_mxdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_mxwant}")
        if _mxrs is not None:
            _mxr = _mxrs.get(d) or {}
            try:
                _mxgot = tuple(int(float(_mxr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _mxgot = None
            if _mxgot is None or _mxgot[:3] != _mxwant or _mxgot[3] + _mxgot[4] != _mxwant[0]:
                fails.append(f"mixyx50r70 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_mxgot} "
                             f"inconsistent with {_mxwant} (smoothed + skipped must equal nodes)")
# --- t65b25r70ffsr (ops/add_t65b25r70ffsr_gate.py): t65b25r70 + ARM_FLOWFIX after the override + short-track
# rescue armed (trigger 0.0). = the live t65b25r70ff cross-check (renamed: A == rawlink final=, B == A + bridged
# - dups == written, run_stats flowfix_*) + the live t65b25r70sr rescue receipts (renamed) + the post-rescue
# chain (short-track == FINAL, rawlink anchor == FINAL edges, run_stats removed == prune - FINAL).
if "t65b25r70ffsr" in tags:
    import csv, os
    _fsxfin, _fsxsd, _fsxdv, _fsxrl = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _fsxfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _fsxsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _fsxdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for _fsxm in re.finditer(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _fsxrl.setdefault(_fsxm.group(1), (int(_fsxm.group(2)), _fsxm.start()))
    _fsxrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _fsxrs = None
    if os.path.isfile(_fsxrsp):
        with open(_fsxrsp, newline="", encoding="utf-8") as fh:
            _fsxrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t65b25r70ffsr: no run_stats.csv beside the log, so the written counts and flowfix counters are unproven")
    _fsxchg = []
    for d in sorted(REF):
        if d not in _fsxfin or d not in _fsxsd or d not in _fsxrl:
            fails.append(f"t65b25r70ffsr {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _fsxm = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                          r"bridged=(\d+) dups=(\d+) edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _fsxm:
            fails.append(f"t65b25r70ffsr {d}: no ARM_FLOWFIX status=ok line")
            continue
        _fsxg = [int(v) for v in _fsxm.groups()[:11]]
        _fsxch, _fsxbr, _fsxdu, _fsxa0, _fsxa1, _fsxv0, _fsxv1, _fsxmi = _fsxg[3:11]
        _fsxn, _fsxs = _fsxfin[d][0], _fsxsd[d]
        _fsxchg.append(_fsxch)
        if _fsxm.start() < _fsxrl[d][1] or _fsxm.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"t65b25r70ffsr {d}: ARM_FLOWFIX line is not after the movie's FINAL and ARM_RAWLINK lines: the "
                         "repair must act on the override's output")
        if _fsxa0 != _fsxrl[d][0]:
            fails.append(f"t65b25r70ffsr {d}: flowfix input edges {_fsxa0} != ARM_RAWLINK final={_fsxrl[d][0]}: the repair "
                         "did not start from the override's output")
        if _fsxa1 != _fsxa0 + _fsxbr - _fsxdu:
            fails.append(f"t65b25r70ffsr {d}: flowfix edges {_fsxa0}->{_fsxa1} inconsistent with {_fsxa0} + bridged "
                         f"{_fsxbr} - dups {_fsxdu}")
        if _fsxv0 != _fsxv1 or _fsxv1 != _fsxs or _fsxmi > 1:
            fails.append(f"t65b25r70ffsr {d}: flowfix divisions {_fsxv0}->{_fsxv1} (want {_fsxs}) or in-degree {_fsxmi}")
        if float(_fsxm.group(12)) > 20.0:
            fails.append(f"t65b25r70ffsr {d}: flowfix {_fsxm.group(12)} s > 20 s/movie (hidden overhead > ~66 min)")
        _fsxwant = (_fsxn, _fsxa1, _fsxs)
        if _fsxdv.get(d) != _fsxwant:
            fails.append(f"t65b25r70ffsr {d} written nodes/edges/divisions {_fsxdv.get(d)} != (FINAL nodes, flowfix B, "
                         f"safe divisions) {_fsxwant}")
        if _fsxrs is not None:
            _fsxr = _fsxrs.get(d) or {}
            try:
                _fsxgot = tuple(int(float(_fsxr[k])) for k in (
                    "nodes", "edges", "safe_divisions_added", "linefit_smoothed_nodes", "linefit_skipped_nodes",
                    "rawlink_final_edges", "flowfix_changed", "flowfix_bridged", "flowfix_dups"))
                _fsxst = _fsxr["flowfix_status"]
            except (KeyError, TypeError, ValueError):
                _fsxgot, _fsxst = None, None
            if _fsxgot is None or _fsxgot[:3] != _fsxwant or _fsxgot[3] + _fsxgot[4] != _fsxn \
                    or _fsxgot[5] != _fsxa0 or _fsxgot[6:] != (_fsxch, _fsxbr, _fsxdu) or _fsxst != "ok":
                fails.append(f"t65b25r70ffsr {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped, "
                             f"rawlink_final_edges, flowfix changed/bridged/dups) {_fsxgot} status {_fsxst} inconsistent "
                             f"with {_fsxwant} / rawlink final {_fsxa0} / flowfix {(_fsxch, _fsxbr, _fsxdu)} ok")
    if not _fsxchg or max(_fsxchg) == 0:
        fails.append("t65b25r70ffsr: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
    # rescue receipts (ops/add_t65b25r70ffsr_gate.py): the rescue prints no line of its own, so run_stats is the only
    # evidence. Trigger 0.0 => the branch runs on every movie (triggered == 1); components <= nodes <= budget; and
    # at least one visible movie must get components back, otherwise the armed branch did nothing.
    if _fsxrs is not None:
        _fsxcomp = []
        for d in sorted(REF):
            _fsxrow = _fsxrs.get(d) or {}
            try:
                _fsxq = tuple(int(float(_fsxrow[k])) for k in ("short_track_rescue_triggered", "short_track_rescue_components",
                                                             "short_track_rescue_nodes", "short_track_rescue_budget"))
            except (KeyError, TypeError, ValueError):
                _fsxq = None
            if _fsxq is None:
                fails.append(f"t65b25r70ffsr {d}: run_stats has no readable short_track_rescue_* columns")
                continue
            if _fsxq[0] != 1:
                fails.append(f"t65b25r70ffsr {d}: short_track_rescue_triggered={_fsxq[0]}: with trigger 0.0 the rescue "
                             "branch must run on every movie")
            if not 0 <= _fsxq[1] <= _fsxq[2] <= _fsxq[3]:
                fails.append(f"t65b25r70ffsr {d}: rescued components/nodes/budget {_fsxq[1:]} inconsistent "
                             "(components <= nodes <= budget)")
            _fsxcomp.append(_fsxq[1])
        if not _fsxcomp or max(_fsxcomp) == 0:
            fails.append("t65b25r70ffsr: the armed rescue restored 0 components on every visible movie: the branch did nothing")
    # post-rescue chain (ops/add_t65b25r70ffsr_gate.py). The rescue runs INSIDE the short-track filter, i.e. before
    # FINAL, the override and the repair, so every count the flowfix arithmetic above reads is already post-rescue.
    # Tie the links explicitly per movie: short-track line == FINAL; ARM_RAWLINK anchor= == FINAL edges (the override
    # starts from the post-rescue graph); run_stats short_track_nodes/edges_removed == prune-isolated line - FINAL and
    # short_track_components_removed == the short-track line's components_removed (rescued components stayed in).
    _fsxst, _fsxpr, _fsxan = {}, {}, {}
    for d, n_, e_, c_ in re.findall(r"\[(\w+)\] after short-track filtering: (\d+) nodes, (\d+) edges "
                                    r"\(components_removed=(\d+)\)", txt):
        _fsxst.setdefault(d, (int(n_), int(e_), int(c_)))
    for d, n_, e_ in re.findall(r"\[(\w+)\] after division-geometry-filter\+prune-isolated: (\d+) nodes, (\d+) edges", txt):
        _fsxpr.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? anchor=(\d+) ", txt):
        _fsxan.setdefault(d, int(a_))
    for d in sorted(REF):
        _fsxf = _fsxfin.get(d)
        if _fsxf is None or d not in _fsxst or d not in _fsxpr or d not in _fsxan:
            fails.append(f"t65b25r70ffsr {d}: missing FINAL / short-track / prune-isolated / ARM_RAWLINK anchor= line")
            continue
        if _fsxst[d][:2] != _fsxf:
            fails.append(f"t65b25r70ffsr {d}: short-track (post-rescue) nodes/edges {_fsxst[d][:2]} != FINAL {_fsxf}")
        if _fsxan[d] != _fsxf[1]:
            fails.append(f"t65b25r70ffsr {d}: ARM_RAWLINK anchor={_fsxan[d]} != FINAL edges {_fsxf[1]}: the override did "
                         "not start from the post-rescue graph")
        if _fsxrs is not None:
            _fsxrow = _fsxrs.get(d) or {}
            try:
                _fsxrm = tuple(int(float(_fsxrow[k])) for k in ("short_track_nodes_removed", "short_track_edges_removed",
                                                              "short_track_components_removed"))
            except (KeyError, TypeError, ValueError):
                _fsxrm = None
            _fsxrw = (_fsxpr[d][0] - _fsxf[0], _fsxpr[d][1] - _fsxf[1], _fsxst[d][2])
            if _fsxrm != _fsxrw:
                fails.append(f"t65b25r70ffsr {d}: run_stats short_track_nodes/edges/components_removed {_fsxrm} != "
                             f"(prune-isolated - FINAL, components_removed) {_fsxrw}")
# --- ourvzlb25r70ff (ops/add_ourvzlb25r70ff_gate.py): ourvzlb25r70 (V1284 y/x + sub-voxel z, tight 6.5, bonus
# 2.5, rawlink 0.70; public 0.955) + ARM_FLOWFIX after the override. = the live t65b25r70ff cross-check, renamed:
# flowfix A == ARM_RAWLINK final=, B == A + bridged - dups == cell-10 written edges, divisions unchanged, <= 20 s,
# run_stats agrees (edges == B, rawlink_final_edges == A, flowfix_* as logged, smoothed + skipped == nodes).
if "ourvzlb25r70ff" in tags:
    import csv, os
    _ozfxfin, _ozfxsd, _ozfxdv, _ozfxrl = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _ozfxfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _ozfxsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _ozfxdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for _ozfxm in re.finditer(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _ozfxrl.setdefault(_ozfxm.group(1), (int(_ozfxm.group(2)), _ozfxm.start()))
    _ozfxrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _ozfxrs = None
    if os.path.isfile(_ozfxrsp):
        with open(_ozfxrsp, newline="", encoding="utf-8") as fh:
            _ozfxrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlb25r70ff: no run_stats.csv beside the log, so the written counts and flowfix counters are unproven")
    _ozfxchg = []
    for d in sorted(REF):
        if d not in _ozfxfin or d not in _ozfxsd or d not in _ozfxrl:
            fails.append(f"ourvzlb25r70ff {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _ozfxm = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                          r"bridged=(\d+) dups=(\d+) edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _ozfxm:
            fails.append(f"ourvzlb25r70ff {d}: no ARM_FLOWFIX status=ok line")
            continue
        _ozfxg = [int(v) for v in _ozfxm.groups()[:11]]
        _ozfxch, _ozfxbr, _ozfxdu, _ozfxa0, _ozfxa1, _ozfxv0, _ozfxv1, _ozfxmi = _ozfxg[3:11]
        _ozfxn, _ozfxs = _ozfxfin[d][0], _ozfxsd[d]
        _ozfxchg.append(_ozfxch)
        if _ozfxm.start() < _ozfxrl[d][1] or _ozfxm.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"ourvzlb25r70ff {d}: ARM_FLOWFIX line is not after the movie's FINAL and ARM_RAWLINK lines: the "
                         "repair must act on the override's output")
        if _ozfxa0 != _ozfxrl[d][0]:
            fails.append(f"ourvzlb25r70ff {d}: flowfix input edges {_ozfxa0} != ARM_RAWLINK final={_ozfxrl[d][0]}: the repair "
                         "did not start from the override's output")
        if _ozfxa1 != _ozfxa0 + _ozfxbr - _ozfxdu:
            fails.append(f"ourvzlb25r70ff {d}: flowfix edges {_ozfxa0}->{_ozfxa1} inconsistent with {_ozfxa0} + bridged "
                         f"{_ozfxbr} - dups {_ozfxdu}")
        if _ozfxv0 != _ozfxv1 or _ozfxv1 != _ozfxs or _ozfxmi > 1:
            fails.append(f"ourvzlb25r70ff {d}: flowfix divisions {_ozfxv0}->{_ozfxv1} (want {_ozfxs}) or in-degree {_ozfxmi}")
        if float(_ozfxm.group(12)) > 20.0:
            fails.append(f"ourvzlb25r70ff {d}: flowfix {_ozfxm.group(12)} s > 20 s/movie (hidden overhead > ~66 min)")
        _ozfxwant = (_ozfxn, _ozfxa1, _ozfxs)
        if _ozfxdv.get(d) != _ozfxwant:
            fails.append(f"ourvzlb25r70ff {d} written nodes/edges/divisions {_ozfxdv.get(d)} != (FINAL nodes, flowfix B, "
                         f"safe divisions) {_ozfxwant}")
        if _ozfxrs is not None:
            _ozfxr = _ozfxrs.get(d) or {}
            try:
                _ozfxgot = tuple(int(float(_ozfxr[k])) for k in (
                    "nodes", "edges", "safe_divisions_added", "linefit_smoothed_nodes", "linefit_skipped_nodes",
                    "rawlink_final_edges", "flowfix_changed", "flowfix_bridged", "flowfix_dups"))
                _ozfxst = _ozfxr["flowfix_status"]
            except (KeyError, TypeError, ValueError):
                _ozfxgot, _ozfxst = None, None
            if _ozfxgot is None or _ozfxgot[:3] != _ozfxwant or _ozfxgot[3] + _ozfxgot[4] != _ozfxn \
                    or _ozfxgot[5] != _ozfxa0 or _ozfxgot[6:] != (_ozfxch, _ozfxbr, _ozfxdu) or _ozfxst != "ok":
                fails.append(f"ourvzlb25r70ff {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped, "
                             f"rawlink_final_edges, flowfix changed/bridged/dups) {_ozfxgot} status {_ozfxst} inconsistent "
                             f"with {_ozfxwant} / rawlink final {_ozfxa0} / flowfix {(_ozfxch, _ozfxbr, _ozfxdu)} ok")
    if not _ozfxchg or max(_ozfxchg) == 0:
        fails.append("ourvzlb25r70ff: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
# --- ourvzlt625 (ops/add_ourvzlt625_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + ONE cell-0 env change (tight).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + the tight-edge monotonicity receipt.
if "ourvzlt625" in tags:
    import csv, os
    _zt625fin, _zt625sd, _zt625dv, _zt625rlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zt625fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zt625sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zt625dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zt625rlf.setdefault(d, int(f_))
    _zt625rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zt625rs = None
    if os.path.isfile(_zt625rsp):
        with open(_zt625rsp, newline="", encoding="utf-8") as fh:
            _zt625rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlt625: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zt625fin or d not in _zt625sd or d not in _zt625rlf:
            fails.append(f"ourvzlt625 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zt625want = (_zt625fin[d][0], _zt625rlf[d], _zt625sd[d])
        if _zt625dv.get(d) != _zt625want:
            fails.append(f"ourvzlt625 {d} written nodes/edges/divisions {_zt625dv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zt625want}")
        if _zt625rs is not None:
            _zt625r = _zt625rs.get(d) or {}
            try:
                _zt625got = tuple(int(float(_zt625r[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zt625got = None
            if _zt625got is None or _zt625got[:3] != _zt625want or _zt625got[3] + _zt625got[4] != _zt625want[0]:
                fails.append(f"ourvzlt625 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zt625got} "
                             f"inconsistent with {_zt625want} (smoothed + skipped must equal nodes)")
    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts
    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a
    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.
    _zt625TB = {'44b6_0113de3b': 24585, '44b6_0b24845f': 18170, '6bba_05b6850b': 5819, '6bba_05db0fb1': 65963}
    if _zt625rs is not None:
        _zt625tg = {}
        for d in sorted(_zt625TB):
            try: _zt625tg[d] = int(float((_zt625rs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zt625tg[d] = None
        if any(v is None for v in _zt625tg.values()):
            fails.append(f"ourvzlt625 run_stats has no readable motion_relink_tight_edges: {_zt625tg}")
        elif not all(_zt625tg[d] <= _zt625TB[d] for d in _zt625TB) or not any(_zt625tg[d] < _zt625TB[d] for d in _zt625TB):
            fails.append(f"ourvzlt625 motion_relink_tight_edges {_zt625tg} vs the 6.5-gate counts {_zt625TB}: a 6.25 gate must give <= on all four movies and < on at least one")
# --- ourvzlt675 (ops/add_ourvzlt675_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + ONE cell-0 env change (tight).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + the tight-edge monotonicity receipt.
if "ourvzlt675" in tags:
    import csv, os
    _zt675fin, _zt675sd, _zt675dv, _zt675rlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zt675fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zt675sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zt675dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zt675rlf.setdefault(d, int(f_))
    _zt675rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zt675rs = None
    if os.path.isfile(_zt675rsp):
        with open(_zt675rsp, newline="", encoding="utf-8") as fh:
            _zt675rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlt675: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zt675fin or d not in _zt675sd or d not in _zt675rlf:
            fails.append(f"ourvzlt675 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zt675want = (_zt675fin[d][0], _zt675rlf[d], _zt675sd[d])
        if _zt675dv.get(d) != _zt675want:
            fails.append(f"ourvzlt675 {d} written nodes/edges/divisions {_zt675dv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zt675want}")
        if _zt675rs is not None:
            _zt675r = _zt675rs.get(d) or {}
            try:
                _zt675got = tuple(int(float(_zt675r[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zt675got = None
            if _zt675got is None or _zt675got[:3] != _zt675want or _zt675got[3] + _zt675got[4] != _zt675want[0]:
                fails.append(f"ourvzlt675 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zt675got} "
                             f"inconsistent with {_zt675want} (smoothed + skipped must equal nodes)")
    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts
    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a
    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.
    _zt675TB = {'44b6_0113de3b': 24585, '44b6_0b24845f': 18170, '6bba_05b6850b': 5819, '6bba_05db0fb1': 65963}
    if _zt675rs is not None:
        _zt675tg = {}
        for d in sorted(_zt675TB):
            try: _zt675tg[d] = int(float((_zt675rs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zt675tg[d] = None
        if any(v is None for v in _zt675tg.values()):
            fails.append(f"ourvzlt675 run_stats has no readable motion_relink_tight_edges: {_zt675tg}")
        elif not all(_zt675tg[d] >= _zt675TB[d] for d in _zt675TB) or not any(_zt675tg[d] > _zt675TB[d] for d in _zt675TB):
            fails.append(f"ourvzlt675 motion_relink_tight_edges {_zt675tg} vs the 6.5-gate counts {_zt675TB}: a 6.75 gate must give >= on all four movies and > on at least one")
# --- ourvzlb30 (ops/add_ourvzlb30_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + ONE cell-0 env change (bonus).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + tight edges == the 6.5-gate counts.
if "ourvzlb30" in tags:
    import csv, os
    _zb30fin, _zb30sd, _zb30dv, _zb30rlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zb30fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zb30sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zb30dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zb30rlf.setdefault(d, int(f_))
    _zb30rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zb30rs = None
    if os.path.isfile(_zb30rsp):
        with open(_zb30rsp, newline="", encoding="utf-8") as fh:
            _zb30rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlb30: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zb30fin or d not in _zb30sd or d not in _zb30rlf:
            fails.append(f"ourvzlb30 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zb30want = (_zb30fin[d][0], _zb30rlf[d], _zb30sd[d])
        if _zb30dv.get(d) != _zb30want:
            fails.append(f"ourvzlb30 {d} written nodes/edges/divisions {_zb30dv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zb30want}")
        if _zb30rs is not None:
            _zb30r = _zb30rs.get(d) or {}
            try:
                _zb30got = tuple(int(float(_zb30r[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zb30got = None
            if _zb30got is None or _zb30got[:3] != _zb30want or _zb30got[3] + _zb30got[4] != _zb30want[0]:
                fails.append(f"ourvzlb30 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zb30got} "
                             f"inconsistent with {_zb30want} (smoothed + skipped must equal nodes)")
    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts
    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a
    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.
    _zb30TB = {'44b6_0113de3b': 24585, '44b6_0b24845f': 18170, '6bba_05b6850b': 5819, '6bba_05db0fb1': 65963}
    if _zb30rs is not None:
        _zb30tg = {}
        for d in sorted(_zb30TB):
            try: _zb30tg[d] = int(float((_zb30rs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zb30tg[d] = None
        if any(v is None for v in _zb30tg.values()):
            fails.append(f"ourvzlb30 run_stats has no readable motion_relink_tight_edges: {_zb30tg}")
        elif _zb30tg != _zb30TB:
            fails.append(f"ourvzlb30 motion_relink_tight_edges {_zb30tg} != the 6.5-gate counts {_zb30TB}: the tight pass does not depend on the bonus, so the tight gate or the body moved")
# --- ourvzlb20 (ops/add_ourvzlb20_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + ONE cell-0 env change (bonus).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + tight edges == the 6.5-gate counts.
if "ourvzlb20" in tags:
    import csv, os
    _zb20fin, _zb20sd, _zb20dv, _zb20rlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zb20fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zb20sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zb20dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zb20rlf.setdefault(d, int(f_))
    _zb20rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zb20rs = None
    if os.path.isfile(_zb20rsp):
        with open(_zb20rsp, newline="", encoding="utf-8") as fh:
            _zb20rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlb20: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zb20fin or d not in _zb20sd or d not in _zb20rlf:
            fails.append(f"ourvzlb20 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zb20want = (_zb20fin[d][0], _zb20rlf[d], _zb20sd[d])
        if _zb20dv.get(d) != _zb20want:
            fails.append(f"ourvzlb20 {d} written nodes/edges/divisions {_zb20dv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zb20want}")
        if _zb20rs is not None:
            _zb20r = _zb20rs.get(d) or {}
            try:
                _zb20got = tuple(int(float(_zb20r[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zb20got = None
            if _zb20got is None or _zb20got[:3] != _zb20want or _zb20got[3] + _zb20got[4] != _zb20want[0]:
                fails.append(f"ourvzlb20 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zb20got} "
                             f"inconsistent with {_zb20want} (smoothed + skipped must equal nodes)")
    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts
    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a
    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.
    _zb20TB = {'44b6_0113de3b': 24585, '44b6_0b24845f': 18170, '6bba_05b6850b': 5819, '6bba_05db0fb1': 65963}
    if _zb20rs is not None:
        _zb20tg = {}
        for d in sorted(_zb20TB):
            try: _zb20tg[d] = int(float((_zb20rs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zb20tg[d] = None
        if any(v is None for v in _zb20tg.values()):
            fails.append(f"ourvzlb20 run_stats has no readable motion_relink_tight_edges: {_zb20tg}")
        elif _zb20tg != _zb20TB:
            fails.append(f"ourvzlb20 motion_relink_tight_edges {_zb20tg} != the 6.5-gate counts {_zb20TB}: the tight pass does not depend on the bonus, so the tight gate or the body moved")
# --- ourvzlsr (ops/add_ourvzlsr_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + ONE cell-0 env change (sr).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + t65b25r70sr's rescue receipts (renamed).
if "ourvzlsr" in tags:
    import csv, os
    _zsrfin, _zsrsd, _zsrdv, _zsrrlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zsrfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zsrsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zsrdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zsrrlf.setdefault(d, int(f_))
    _zsrrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zsrrs = None
    if os.path.isfile(_zsrrsp):
        with open(_zsrrsp, newline="", encoding="utf-8") as fh:
            _zsrrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlsr: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zsrfin or d not in _zsrsd or d not in _zsrrlf:
            fails.append(f"ourvzlsr {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zsrwant = (_zsrfin[d][0], _zsrrlf[d], _zsrsd[d])
        if _zsrdv.get(d) != _zsrwant:
            fails.append(f"ourvzlsr {d} written nodes/edges/divisions {_zsrdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zsrwant}")
        if _zsrrs is not None:
            _zsrr = _zsrrs.get(d) or {}
            try:
                _zsrgot = tuple(int(float(_zsrr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zsrgot = None
            if _zsrgot is None or _zsrgot[:3] != _zsrwant or _zsrgot[3] + _zsrgot[4] != _zsrwant[0]:
                fails.append(f"ourvzlsr {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zsrgot} "
                             f"inconsistent with {_zsrwant} (smoothed + skipped must equal nodes)")
    # rescue receipts (ops/add_ourvzlsr_gate.py): the rescue prints no line of its own, so run_stats is the only
    # evidence. Trigger 0.0 => the branch runs on every movie (triggered == 1); components <= nodes <= budget; and
    # at least one visible movie must get components back, otherwise the armed branch did nothing.
    if _zsrrs is not None:
        _zsrcomp = []
        for d in sorted(REF):
            _zsrrow = _zsrrs.get(d) or {}
            try:
                _zsrq = tuple(int(float(_zsrrow[k])) for k in ("short_track_rescue_triggered", "short_track_rescue_components",
                                                             "short_track_rescue_nodes", "short_track_rescue_budget"))
            except (KeyError, TypeError, ValueError):
                _zsrq = None
            if _zsrq is None:
                fails.append(f"ourvzlsr {d}: run_stats has no readable short_track_rescue_* columns")
                continue
            if _zsrq[0] != 1:
                fails.append(f"ourvzlsr {d}: short_track_rescue_triggered={_zsrq[0]}: with trigger 0.0 the rescue "
                             "branch must run on every movie")
            if not 0 <= _zsrq[1] <= _zsrq[2] <= _zsrq[3]:
                fails.append(f"ourvzlsr {d}: rescued components/nodes/budget {_zsrq[1:]} inconsistent "
                             "(components <= nodes <= budget)")
            _zsrcomp.append(_zsrq[1])
        if not _zsrcomp or max(_zsrcomp) == 0:
            fails.append("ourvzlsr: the armed rescue restored 0 components on every visible movie: the branch did nothing")
# --- ourvzllf100 (ops/add_ourvzllf100_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + ONE cell-0 env change (lf).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed).
if "ourvzllf100" in tags:
    import csv, os
    _zlffin, _zlfsd, _zlfdv, _zlfrlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zlffin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zlfsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zlfdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zlfrlf.setdefault(d, int(f_))
    _zlfrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zlfrs = None
    if os.path.isfile(_zlfrsp):
        with open(_zlfrsp, newline="", encoding="utf-8") as fh:
            _zlfrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzllf100: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zlffin or d not in _zlfsd or d not in _zlfrlf:
            fails.append(f"ourvzllf100 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zlfwant = (_zlffin[d][0], _zlfrlf[d], _zlfsd[d])
        if _zlfdv.get(d) != _zlfwant:
            fails.append(f"ourvzllf100 {d} written nodes/edges/divisions {_zlfdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zlfwant}")
        if _zlfrs is not None:
            _zlfr = _zlfrs.get(d) or {}
            try:
                _zlfgot = tuple(int(float(_zlfr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zlfgot = None
            if _zlfgot is None or _zlfgot[:3] != _zlfwant or _zlfgot[3] + _zlfgot[4] != _zlfwant[0]:
                fails.append(f"ourvzllf100 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zlfgot} "
                             f"inconsistent with {_zlfwant} (smoothed + skipped must equal nodes)")
# --- ourvzlb30t625 (ops/add_ourvzlb30t625_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + TWO cell-0 env changes (tight 6.25 + bonus 3.0).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + the tight-edge monotonicity receipt.
if "ourvzlb30t625" in tags:
    import csv, os
    _zbtfin, _zbtsd, _zbtdv, _zbtrlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zbtfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zbtsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zbtdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zbtrlf.setdefault(d, int(f_))
    _zbtrsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zbtrs = None
    if os.path.isfile(_zbtrsp):
        with open(_zbtrsp, newline="", encoding="utf-8") as fh:
            _zbtrs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlb30t625: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zbtfin or d not in _zbtsd or d not in _zbtrlf:
            fails.append(f"ourvzlb30t625 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zbtwant = (_zbtfin[d][0], _zbtrlf[d], _zbtsd[d])
        if _zbtdv.get(d) != _zbtwant:
            fails.append(f"ourvzlb30t625 {d} written nodes/edges/divisions {_zbtdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zbtwant}")
        if _zbtrs is not None:
            _zbtr = _zbtrs.get(d) or {}
            try:
                _zbtgot = tuple(int(float(_zbtr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zbtgot = None
            if _zbtgot is None or _zbtgot[:3] != _zbtwant or _zbtgot[3] + _zbtgot[4] != _zbtwant[0]:
                fails.append(f"ourvzlb30t625 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zbtgot} "
                             f"inconsistent with {_zbtwant} (smoothed + skipped must equal nodes)")
    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts
    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a
    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.
    _zbtTB = {'44b6_0113de3b': 24585, '44b6_0b24845f': 18170, '6bba_05b6850b': 5819, '6bba_05db0fb1': 65963}
    if _zbtrs is not None:
        _zbttg = {}
        for d in sorted(_zbtTB):
            try: _zbttg[d] = int(float((_zbtrs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zbttg[d] = None
        if any(v is None for v in _zbttg.values()):
            fails.append(f"ourvzlb30t625 run_stats has no readable motion_relink_tight_edges: {_zbttg}")
        elif not all(_zbttg[d] <= _zbtTB[d] for d in _zbtTB) or not any(_zbttg[d] < _zbtTB[d] for d in _zbtTB):
            fails.append(f"ourvzlb30t625 motion_relink_tight_edges {_zbttg} vs the 6.5-gate counts {_zbtTB}: a 6.25 gate must give <= on all four movies and < on at least one")
# --- ourvzlffb30 (ops/add_ourvzlffb30_gate.py via ops/ourvzl_combo_gate.py): ourvzlb25r70ff + ONE cell-0 env change (bonus 3.0).
# = ourvzlb25r70ff's flowfix cross-check (generated from its block, renamed) + tight edges == the 6.5-gate counts.
if "ourvzlffb30" in tags:
    import csv, os
    _zfb3fin, _zfb3sd, _zfb3dv, _zfb3rl = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zfb3fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zfb3sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zfb3dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for _zfb3m in re.finditer(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zfb3rl.setdefault(_zfb3m.group(1), (int(_zfb3m.group(2)), _zfb3m.start()))
    _zfb3rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zfb3rs = None
    if os.path.isfile(_zfb3rsp):
        with open(_zfb3rsp, newline="", encoding="utf-8") as fh:
            _zfb3rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlffb30: no run_stats.csv beside the log, so the written counts and flowfix counters are unproven")
    _zfb3chg = []
    for d in sorted(REF):
        if d not in _zfb3fin or d not in _zfb3sd or d not in _zfb3rl:
            fails.append(f"ourvzlffb30 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zfb3m = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                          r"bridged=(\d+) dups=(\d+) edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _zfb3m:
            fails.append(f"ourvzlffb30 {d}: no ARM_FLOWFIX status=ok line")
            continue
        _zfb3g = [int(v) for v in _zfb3m.groups()[:11]]
        _zfb3ch, _zfb3br, _zfb3du, _zfb3a0, _zfb3a1, _zfb3v0, _zfb3v1, _zfb3mi = _zfb3g[3:11]
        _zfb3n, _zfb3s = _zfb3fin[d][0], _zfb3sd[d]
        _zfb3chg.append(_zfb3ch)
        if _zfb3m.start() < _zfb3rl[d][1] or _zfb3m.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"ourvzlffb30 {d}: ARM_FLOWFIX line is not after the movie's FINAL and ARM_RAWLINK lines: the "
                         "repair must act on the override's output")
        if _zfb3a0 != _zfb3rl[d][0]:
            fails.append(f"ourvzlffb30 {d}: flowfix input edges {_zfb3a0} != ARM_RAWLINK final={_zfb3rl[d][0]}: the repair "
                         "did not start from the override's output")
        if _zfb3a1 != _zfb3a0 + _zfb3br - _zfb3du:
            fails.append(f"ourvzlffb30 {d}: flowfix edges {_zfb3a0}->{_zfb3a1} inconsistent with {_zfb3a0} + bridged "
                         f"{_zfb3br} - dups {_zfb3du}")
        if _zfb3v0 != _zfb3v1 or _zfb3v1 != _zfb3s or _zfb3mi > 1:
            fails.append(f"ourvzlffb30 {d}: flowfix divisions {_zfb3v0}->{_zfb3v1} (want {_zfb3s}) or in-degree {_zfb3mi}")
        if float(_zfb3m.group(12)) > 20.0:
            fails.append(f"ourvzlffb30 {d}: flowfix {_zfb3m.group(12)} s > 20 s/movie (hidden overhead > ~66 min)")
        _zfb3want = (_zfb3n, _zfb3a1, _zfb3s)
        if _zfb3dv.get(d) != _zfb3want:
            fails.append(f"ourvzlffb30 {d} written nodes/edges/divisions {_zfb3dv.get(d)} != (FINAL nodes, flowfix B, "
                         f"safe divisions) {_zfb3want}")
        if _zfb3rs is not None:
            _zfb3r = _zfb3rs.get(d) or {}
            try:
                _zfb3got = tuple(int(float(_zfb3r[k])) for k in (
                    "nodes", "edges", "safe_divisions_added", "linefit_smoothed_nodes", "linefit_skipped_nodes",
                    "rawlink_final_edges", "flowfix_changed", "flowfix_bridged", "flowfix_dups"))
                _zfb3st = _zfb3r["flowfix_status"]
            except (KeyError, TypeError, ValueError):
                _zfb3got, _zfb3st = None, None
            if _zfb3got is None or _zfb3got[:3] != _zfb3want or _zfb3got[3] + _zfb3got[4] != _zfb3n \
                    or _zfb3got[5] != _zfb3a0 or _zfb3got[6:] != (_zfb3ch, _zfb3br, _zfb3du) or _zfb3st != "ok":
                fails.append(f"ourvzlffb30 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped, "
                             f"rawlink_final_edges, flowfix changed/bridged/dups) {_zfb3got} status {_zfb3st} inconsistent "
                             f"with {_zfb3want} / rawlink final {_zfb3a0} / flowfix {(_zfb3ch, _zfb3br, _zfb3du)} ok")
    if not _zfb3chg or max(_zfb3chg) == 0:
        fails.append("ourvzlffb30: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
    # receipt (ops/ourvzl_combo_gate.py): run_stats motion_relink_tight_edges == the 6.5-gate V1284-body counts
    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff / ourvzlb30 all logged exactly these): the tight pass does not
    # depend on the bonus.
    _zfb3TB = {'44b6_0113de3b': 24585, '44b6_0b24845f': 18170, '6bba_05b6850b': 5819, '6bba_05db0fb1': 65963}
    if _zfb3rs is not None:
        _zfb3tg = {}
        for d in sorted(_zfb3TB):
            try: _zfb3tg[d] = int(float((_zfb3rs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zfb3tg[d] = None
        if any(v is None for v in _zfb3tg.values()):
            fails.append(f"ourvzlffb30 run_stats has no readable motion_relink_tight_edges: {_zfb3tg}")
        elif _zfb3tg != _zfb3TB:
            fails.append(f"ourvzlffb30 motion_relink_tight_edges {_zfb3tg} != the 6.5-gate counts {_zfb3TB}: the tight pass does not depend on the bonus, so the tight gate or the body moved")
# --- ourvzlb35t625 (ops/add_ourvzlb35t625_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + TWO cell-0 env changes (tight 6.25 + bonus 3.5).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + the tight-edge monotonicity receipt.
if "ourvzlb35t625" in tags:
    import csv, os
    _zb35tfin, _zb35tsd, _zb35tdv, _zb35trlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zb35tfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zb35tsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zb35tdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zb35trlf.setdefault(d, int(f_))
    _zb35trsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zb35trs = None
    if os.path.isfile(_zb35trsp):
        with open(_zb35trsp, newline="", encoding="utf-8") as fh:
            _zb35trs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlb35t625: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zb35tfin or d not in _zb35tsd or d not in _zb35trlf:
            fails.append(f"ourvzlb35t625 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zb35twant = (_zb35tfin[d][0], _zb35trlf[d], _zb35tsd[d])
        if _zb35tdv.get(d) != _zb35twant:
            fails.append(f"ourvzlb35t625 {d} written nodes/edges/divisions {_zb35tdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zb35twant}")
        if _zb35trs is not None:
            _zb35tr = _zb35trs.get(d) or {}
            try:
                _zb35tgot = tuple(int(float(_zb35tr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zb35tgot = None
            if _zb35tgot is None or _zb35tgot[:3] != _zb35twant or _zb35tgot[3] + _zb35tgot[4] != _zb35twant[0]:
                fails.append(f"ourvzlb35t625 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zb35tgot} "
                             f"inconsistent with {_zb35twant} (smoothed + skipped must equal nodes)")
    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts
    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a
    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.
    _zb35tTB = {'44b6_0113de3b': 24585, '44b6_0b24845f': 18170, '6bba_05b6850b': 5819, '6bba_05db0fb1': 65963}
    if _zb35trs is not None:
        _zb35ttg = {}
        for d in sorted(_zb35tTB):
            try: _zb35ttg[d] = int(float((_zb35trs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zb35ttg[d] = None
        if any(v is None for v in _zb35ttg.values()):
            fails.append(f"ourvzlb35t625 run_stats has no readable motion_relink_tight_edges: {_zb35ttg}")
        elif not all(_zb35ttg[d] <= _zb35tTB[d] for d in _zb35tTB) or not any(_zb35ttg[d] < _zb35tTB[d] for d in _zb35tTB):
            fails.append(f"ourvzlb35t625 motion_relink_tight_edges {_zb35ttg} vs the 6.5-gate counts {_zb35tTB}: a 6.25 gate must give <= on all four movies and < on at least one")
# --- ourvzlb40t625 (ops/add_ourvzlb40t625_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + TWO cell-0 env changes (tight 6.25 + bonus 4.0).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + the tight-edge monotonicity receipt.
if "ourvzlb40t625" in tags:
    import csv, os
    _zb40tfin, _zb40tsd, _zb40tdv, _zb40trlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zb40tfin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zb40tsd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zb40tdv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zb40trlf.setdefault(d, int(f_))
    _zb40trsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zb40trs = None
    if os.path.isfile(_zb40trsp):
        with open(_zb40trsp, newline="", encoding="utf-8") as fh:
            _zb40trs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlb40t625: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zb40tfin or d not in _zb40tsd or d not in _zb40trlf:
            fails.append(f"ourvzlb40t625 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zb40twant = (_zb40tfin[d][0], _zb40trlf[d], _zb40tsd[d])
        if _zb40tdv.get(d) != _zb40twant:
            fails.append(f"ourvzlb40t625 {d} written nodes/edges/divisions {_zb40tdv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zb40twant}")
        if _zb40trs is not None:
            _zb40tr = _zb40trs.get(d) or {}
            try:
                _zb40tgot = tuple(int(float(_zb40tr[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zb40tgot = None
            if _zb40tgot is None or _zb40tgot[:3] != _zb40twant or _zb40tgot[3] + _zb40tgot[4] != _zb40twant[0]:
                fails.append(f"ourvzlb40t625 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zb40tgot} "
                             f"inconsistent with {_zb40twant} (smoothed + skipped must equal nodes)")
    # receipt (ops/ourvzl_envarm_gate.py): run_stats motion_relink_tight_edges vs the 6.5-gate V1284-body counts
    # (ourvzlb25 / ourvzlb25r70 / ourvzlb25r70ff all logged exactly these). The tight pass is effectively a
    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.
    _zb40tTB = {'44b6_0113de3b': 24585, '44b6_0b24845f': 18170, '6bba_05b6850b': 5819, '6bba_05db0fb1': 65963}
    if _zb40trs is not None:
        _zb40ttg = {}
        for d in sorted(_zb40tTB):
            try: _zb40ttg[d] = int(float((_zb40trs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zb40ttg[d] = None
        if any(v is None for v in _zb40ttg.values()):
            fails.append(f"ourvzlb40t625 run_stats has no readable motion_relink_tight_edges: {_zb40ttg}")
        elif not all(_zb40ttg[d] <= _zb40tTB[d] for d in _zb40tTB) or not any(_zb40ttg[d] < _zb40tTB[d] for d in _zb40tTB):
            fails.append(f"ourvzlb40t625 motion_relink_tight_edges {_zb40ttg} vs the 6.5-gate counts {_zb40tTB}: a 6.25 gate must give <= on all four movies and < on at least one")
# --- ourvzlb30t600 (ops/add_ourvzlb30t600_gate.py via ops/ourvzl_envarm_gate.py): ourvzlb25r70 + TWO cell-0 env changes (tight 6.0 + bonus 3.0 = ourvzlb30t625 with tight 6.25 -> 6.0).
# = ourvzlb25r70's per-movie cross-check (generated from its block, renamed) + the tight-edge monotonicity receipt.
if "ourvzlb30t600" in tags:
    import csv, os
    _zb30t6fin, _zb30t6sd, _zb30t6dv, _zb30t6rlf = {}, {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _zb30t6fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _zb30t6sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _zb30t6dv.setdefault(d, (int(n_), int(e_), int(v_)))
    for d, f_ in re.findall(r"ARM_RAWLINK \[(\w+)\] .*? final=(\d+) ", txt):
        _zb30t6rlf.setdefault(d, int(f_))
    _zb30t6rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _zb30t6rs = None
    if os.path.isfile(_zb30t6rsp):
        with open(_zb30t6rsp, newline="", encoding="utf-8") as fh:
            _zb30t6rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("ourvzlb30t600: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven")
    for d in sorted(REF):
        if d not in _zb30t6fin or d not in _zb30t6sd or d not in _zb30t6rlf:
            fails.append(f"ourvzlb30t600 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line")
            continue
        _zb30t6want = (_zb30t6fin[d][0], _zb30t6rlf[d], _zb30t6sd[d])
        if _zb30t6dv.get(d) != _zb30t6want:
            fails.append(f"ourvzlb30t600 {d} written nodes/edges/divisions {_zb30t6dv.get(d)} != (FINAL nodes, rawlink final=, "
                         f"safe divisions) {_zb30t6want}")
        if _zb30t6rs is not None:
            _zb30t6r = _zb30t6rs.get(d) or {}
            try:
                _zb30t6got = tuple(int(float(_zb30t6r[k])) for k in ("nodes", "edges", "safe_divisions_added",
                                                           "linefit_smoothed_nodes", "linefit_skipped_nodes"))
            except (KeyError, TypeError, ValueError):
                _zb30t6got = None
            if _zb30t6got is None or _zb30t6got[:3] != _zb30t6want or _zb30t6got[3] + _zb30t6got[4] != _zb30t6want[0]:
                fails.append(f"ourvzlb30t600 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_zb30t6got} "
                             f"inconsistent with {_zb30t6want} (smoothed + skipped must equal nodes)")
    # receipt (ops/ourvzl_combo_t600_gate.py): run_stats motion_relink_tight_edges vs the REAL 6.25-gate counts
    # (ourvzlb30t625 and ourvzlt625 both logged exactly these). The tight pass is effectively a
    # max-cardinality matching over the gate graph: monotone in the gate, independent of the bonus.
    _zb30t6TB = {'44b6_0113de3b': 24508, '44b6_0b24845f': 18072, '6bba_05b6850b': 5803, '6bba_05db0fb1': 65713}
    if _zb30t6rs is not None:
        _zb30t6tg = {}
        for d in sorted(_zb30t6TB):
            try: _zb30t6tg[d] = int(float((_zb30t6rs.get(d) or {})["motion_relink_tight_edges"]))
            except (KeyError, TypeError, ValueError): _zb30t6tg[d] = None
        if any(v is None for v in _zb30t6tg.values()):
            fails.append(f"ourvzlb30t600 run_stats has no readable motion_relink_tight_edges: {_zb30t6tg}")
        elif not all(_zb30t6tg[d] <= _zb30t6TB[d] for d in _zb30t6TB) or not any(_zb30t6tg[d] < _zb30t6TB[d] for d in _zb30t6TB):
            fails.append(f"ourvzlb30t600 motion_relink_tight_edges {_zb30t6tg} vs ourvzlb30t625's 6.25-gate counts {_zb30t6TB}: a 6.0 gate must give <= on all four movies and < on at least one")
sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]
if sv_tags:
    sv_pat = sv_mark.get(sv_tags[0], "SUBVOXEL_ACTIVE")
    k = len(re.findall(sv_pat, txt[:pred_end if pred_end >= 0 else len(txt)]))
    if k < 4: fails.append(f"only {k} {sv_pat} lines before 'Prediction completed' (softarg did not reach the test set)")
# Patterns that must NOT appear. x138's recall stack degrades SILENTLY: a missing low-detection dump
# prints "gap filler idle" and the filler simply does nothing, and the wall-clock guard turns the whole
# repair stage off after REPAIR_DEADLINE_S. Either one produces a valid, plausible-looking submission
# that is NOT the arm we meant to test, so both are hard failures.
forbid = {t: [r"gap filler idle", r"LOW-DETECTION DUMP SKIPPED", r"readmit skipped \(non-fatal\)",
              r"DEADLINE: \d+s since kernel start", r"REPAIR FAILED"]
          for t in ("xsv", "xsvb", "xsvf", "xbase", "xsvt", "xsvd", "xsv96", "xsvdv", "xsvdc", "xpub",
                    "xsvdd", "xsvd10", "xsvwz", "xsvmx", "xsvdu", "xsvmp", "xsvsr", "xsvgc", "xsvp26", "xsvmax")}
forbid["xbase"] = forbid["xbase"] + [r"SV_ARM_HSG200", r"ARM_LCEFR"]
# xpub is the published notebook with ITS coordinate head, not ours: our sub-voxel block and
# our lcefr block must both be absent, or the wrong kernel was pushed under this tag.
forbid["xpub"] = forbid["xpub"] + [r"SV_ARM_HSG200", r"ARM_LCEFR"]
# t6dl exists to be inert on the visible run: if the guard degraded or fell back there,
# the run tells us nothing about the guarded body and must not be submitted.
forbid["ourv"] = [r"SV_ARM_HSG200", r"ARM_LCEFR", r"SUBVOXEL anchor", r"V1284 patch anchor mismatch"]
for _t in ("ourvg15", "ourvg20", "ourvg13"):
    forbid[_t] = [r"SV_ARM_HSG200", r"ARM_LCEFR", r"SUBVOXEL anchor", r"V1284 patch anchor mismatch", r"V1284 gain patch missing", r"invalid V1284 displacement"]
forbid["ourvrd"] = [r"SV_ARM_HSG200", r"ARM_LCEFR", r"SUBVOXEL anchor", r"V1284 patch anchor mismatch", r"V1284R would load the PUBLIC head", r"V1284R head format", r"V1284R head shapes", r"invalid V1284 displacement", r"head mount mismatch", r"V1284 gain patch missing"]
for _t in ("t6svz05", "t6svx125"):
    forbid[_t] = [r"V1284", r"ARM_SV_ZONLY", r"ARM_SV_YXONLY", r"SUBVOXEL anchor", r"SUBVOXEL offset/coord length mismatch", r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_LCEFR NO-OP", r"IndentationError"]
for _t in ("t6svz15", "t6svz0yx"):
    forbid[_t] = [r"V1284", r"ARM_SV_ZONLY", r"ARM_SV_YXONLY", r"SUBVOXEL anchor", r"SUBVOXEL offset/coord length mismatch", r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_LCEFR NO-OP", r"IndentationError"]
forbid["ourvz"] = [r"ARM_LCEFR", r"SUBVOXEL anchor", r"V1284 patch anchor mismatch", r"IndentationError", r"invalid V1284 displacement", r"head mount mismatch", r"V1284_YX module patch missing", r"SUBVOXEL offset/coord length mismatch"]
forbid["t6svyx"] = [r"ARM_SV_ZONLY", r"V1284", r"SUBVOXEL anchor", r"SUBVOXEL offset/coord length mismatch", r"ARM_LCEFR NO-OP", r"IndentationError", r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_LCEFR PATCH DID NOT PERSIST"]
forbid["ourvr"] = [r"SV_ARM_HSG200", r"ARM_LCEFR", r"SUBVOXEL anchor", r"V1284 patch anchor mismatch", r"V1284R would load the PUBLIC head", r"V1284R head format", r"V1284R head shapes", r"invalid V1284 displacement", r"head mount mismatch"]
forbid["ourvzl"] = forbid["ourvz"] + [r"ARM_SV_Z_TO_ARR env flags missing", r"ARM_SV_Z_TO_ARR (?:module )?anchor matched", r"ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST", r"ARM_SV_Z_TO_ARR needs the sub-voxel", r"ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY", r"ARM_SV_Z_TO_ARR offset/arr length mismatch", r"not applied exactly once", r"base z not integral", r"ARM_SV_Z_TO_ARR NO-OP", r"assembled z != integer peak", r"final_z_add=[1-9]", r"gather_int_z=0", r"Traceback \(most recent call last\)"]
sv_mark["ourvzl"] = "SV_ARM_HSG200"
forbid["t6gtri"] = [r"ARM_GTRI SELFCHECK FAILED", r"ARM_GTRI NO-OP", r"ARM_GTRI anchor matched", r"ARM_GTRI must route",
                    r"ARM_GTRI PATCH DID NOT PERSIST", r"ARM_GTRI bad BIOHUB_GTRI_AXES", r"ARM_GTRI needs lcefr",
                    r"ARM_GTRI_STATS axes=(?!zyx )", r"GTRI=(?!zyx )", r"ARM_XENV tag=(?!t6gtri )",
                    r"V1284", r"ARM_SV_ZONLY", r"ARM_SV_YXONLY", r"ARM_SV_AXES", r"SUBVOXEL anchor",
                    r"SUBVOXEL offset/coord length mismatch", r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_LCEFR NO-OP",
                    r"ARM_LCEFR anchor matched", r"ARM_LCEFR PATCH DID NOT PERSIST", r"IndentationError",
                    r"Traceback \(most recent call last\)"]
if "t6gtri" in tags:
    # Both counters are cumulative per shard process and printed back to back per movie, so the SETS must match:
    # GTRI nodes = 2 x lcefr nodes_refined for every movie <=> all four gathers of every pair went through the
    # trilinear helper (a build that routed only the primary pair would print 1 x). Sharding-independent.
    _pe = txt[:pred_end if pred_end >= 0 else len(txt)]
    _lc = {int(v) for v in re.findall(r"ARM_LCEFR pairs_refined=\d+ nodes_refined=(\d+) ", _pe)}
    _gt = {int(v) for v in re.findall(r"ARM_GTRI_STATS axes=zyx calls=\d+ nodes=(\d+) ", _pe)}
    if len(_gt) < 4 or _gt != {2 * v for v in _lc}:
        fails.append(f"t6gtri: ARM_GTRI_STATS nodes {sorted(_gt)} != 2 x ARM_LCEFR nodes_refined {sorted(_lc)} "
                     "(need one line per movie, >= 4): not every pair routed all four UNet gathers through the trilinear helper")
forbid["t6svT15"] = [r"V1284", r"ARM_SV_ZONLY", r"ARM_SV_YXONLY", r"ARM_SV_AXES", r"ARM_SVZEST", r"SUBVOXEL anchor", r"SUBVOXEL offset/coord length mismatch", r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_LCEFR NO-OP", r"IndentationError", r"Traceback \(most recent call last\)"]
forbid['t6r70T15'] = ['V1284', 'ARM_SV_ZONLY', 'ARM_SV_YXONLY', 'ARM_SV_AXES', 'ARM_SVZEST', 'SUBVOXEL anchor', 'SUBVOXEL offset/coord length mismatch', 'SUBVOXEL PATCH DID NOT PERSIST', 'ARM_LCEFR NO-OP', 'IndentationError', 'Traceback \\(most recent call last\\)', 'ARM_XENV tag=(?!t6r70T15 )', '\\bARM_(?!(?:STK3V|STK3B|T60H|LCEFR|RAWLINK|XENV|SVTEMP)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'SV_ARM_HSG200 nodes=\\d+ mean_abs_off_vox=0\\.(?:2069|2827|2913|2607) ']
forbid["xpubz"] = [r"gap filler idle", r"LOW-DETECTION DUMP SKIPPED", r"readmit skipped \(non-fatal\)",
                   r"DEADLINE: \d+s since kernel start", r"REPAIR FAILED"] + forbid["ourvzl"] + [
                   r"SUBVOXEL PATCH DID NOT PERSIST", r"ARM_STK3V", r"ARM_STK3B", r"ARM_T60H", r"ARM_XENV tag=(?!xpubz )",
                   r"TTA WARNING", r"WARNING: detection timing anchors not unique"]
sv_mark["xpubz"] = "SV_ARM_HSG200"
forbid['t6stk3ff'] = ['ARM_FLOWFIX \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWFIX enabled=False', 'Traceback \\(most recent call last\\)', 'IndentationError', 'ARM_XENV tag=(?!t6stk3ff )', '\\bARM_(?!(?:STK3V|STK3B|T60H|LCEFR|XENV|FLOWFIX)\\b)[A-Z0-9]+', 'ARM_RAWLINK', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true']
forbid['t65s3ff'] = ['ARM_FLOWFIX \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWFIX enabled=False', 'Traceback \\(most recent call last\\)', 'IndentationError', 'ARM_XENV tag=(?!t65s3ff )', '\\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|FLOWFIX)\\b)[A-Z0-9]+', 'ARM_RAWLINK', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)']
forbid['t6stk3ff2'] = ['ARM_FLOWFIX \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWFIX enabled=False', 'Traceback \\(most recent call last\\)', 'IndentationError', 'ARM_XENV tag=(?!t6stk3ff2 )', '\\bARM_(?!(?:STK3V|STK3B|T60H|LCEFR|XENV|FLOWFIX|FLOWCUT)\\b)[A-Z0-9]+', 'ARM_RAWLINK', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true']
forbid['t6stk3fl'] = ['ARM_FLOWFIX \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWLINK \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWFIX enabled=False', 'ARM_FLOWLINK enabled=False', 'Traceback \\(most recent call last\\)', 'IndentationError', 'ARM_XENV tag=(?!t6stk3fl )', '\\bARM_(?!(?:STK3V|STK3B|T60H|LCEFR|XENV|FLOWFIX|FLOWLINK)\\b)[A-Z0-9]+', 'ARM_RAWLINK', 'ARM_FLOWCUT', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true']
forbid['t65b20'] = ['ARM_STK3B learned_bonus=1\\.6', '"motion_relink_learned_bonus": 1\\.6', 'ARM_XENV tag=(?!t65b20 )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV)\\b)[A-Z0-9]+', 'ARM_RAWLINK', 'ARM_FLOWFIX', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)', 'ARM_T60H tight_um=6\\.0']
forbid['t65b25'] = ['ARM_STK3B learned_bonus=2\\.0', 'ARM_STK3B learned_bonus=1\\.6', '"motion_relink_learned_bonus": (2\\.0|1\\.6)', 'ARM_XENV tag=(?!t65b25 )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV)\\b)[A-Z0-9]+', 'ARM_RAWLINK', 'ARM_FLOWFIX', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)', 'ARM_T60H tight_um=6\\.0']
forbid['t65b25r70'] = ['ARM_STK3B learned_bonus=2\\.0', 'ARM_STK3B learned_bonus=1\\.6', '"motion_relink_learned_bonus": (2\\.0|1\\.6)', 'ARM_XENV tag=(?!t65b25r70 )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK)\\b)[A-Z0-9]+', 'ARM_FLOWFIX', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)', 'ARM_T60H tight_um=6\\.0']
forbid['ourvzlb25'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb25 )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true']
forbid['t70b20'] = ['ARM_T65H', 'ARM_T60H', '"motion_relink_tight_um": (6\\.5|6\\.0)(?!\\d)', '"motion_relink_tight_um": (?!7\\.0(?!\\d))', 'MOTION_RELINK_TIGHT_UM +(?!7\\.0(?!\\d))\\d', 'ARM_STK3B learned_bonus=(1\\.6|2\\.5)', '"motion_relink_learned_bonus": (1\\.6|2\\.5)', '"motion_relink_learned_bonus": (?!2\\.0(?!\\d))', 'MOTION_RELINK_LEARNED_BONUS +(?!2\\.0(?!\\d))\\d', 'ARM_XENV tag=(?!t70b20 )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T70H|LCEFR|XENV)\\b)[A-Z0-9]+', 'ARM_RAWLINK', 'ARM_FLOWFIX', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true']
forbid['t70b25'] = ['ARM_T65H', 'ARM_T60H', '"motion_relink_tight_um": (6\\.5|6\\.0)(?!\\d)', '"motion_relink_tight_um": (?!7\\.0(?!\\d))', 'MOTION_RELINK_TIGHT_UM +(?!7\\.0(?!\\d))\\d', 'ARM_STK3B learned_bonus=(1\\.6|2\\.0)', '"motion_relink_learned_bonus": (1\\.6|2\\.0)', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'MOTION_RELINK_LEARNED_BONUS +(?!2\\.5(?!\\d))\\d', 'ARM_XENV tag=(?!t70b25 )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T70H|LCEFR|XENV)\\b)[A-Z0-9]+', 'ARM_RAWLINK', 'ARM_FLOWFIX', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_T\\d+H tight_um=(?!7\\.0(?!\\d))', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))']
forbid['t65b20d04'] = ['ARM_STK3B learned_bonus=1\\.6', '"motion_relink_learned_bonus": 1\\.6', 'ARM_XENV tag=(?!t65b20d04 )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|ILPDIV)\\b)[A-Z0-9]+', 'ARM_RAWLINK', 'ARM_FLOWFIX', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)', 'ARM_T60H tight_um=6\\.0', '"ilp_division_weight": 1\\.2', '--ilp-division-weight 1\\.2', 'ARM_ILPDIV weight=1\\.2', '"ilp_division_weight": (?!0\\.4(?!\\d))', '--ilp-division-weight (?!0\\.4(?!\\d))', 'ARM_ILPDIV weight=(?!0\\.4(?!\\d))', 'ARM_STK3B learned_bonus=(?!2\\.0(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.0(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))']
forbid['t675b25'] = ['ARM_STK3B learned_bonus=2\\.0', 'ARM_STK3B learned_bonus=1\\.6', '"motion_relink_learned_bonus": (2\\.0|1\\.6)', 'ARM_XENV tag=(?!t675b25 )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T675H|LCEFR|XENV)\\b)[A-Z0-9]+', 'ARM_RAWLINK', 'ARM_FLOWFIX', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)', 'ARM_T60H tight_um=6\\.0', 'ARM_T65H', 'ARM_T70H', 'ARM_T60H', '"motion_relink_tight_um": (6\\.5|6\\.0|7\\.0)(?!\\d)', '"motion_relink_tight_um": (?!6\\.75(?!\\d))', 'MOTION_RELINK_TIGHT_UM +(?!6\\.75(?!\\d))\\d', 'ARM_T\\d+H tight_um=(?!6\\.75(?!\\d))', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'MOTION_RELINK_LEARNED_BONUS +(?!2\\.5(?!\\d))\\d']
forbid['ourvzlb25r70'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb25r70 )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))']
forbid['t65b25r70ff'] = ['ARM_STK3B learned_bonus=2\\.0', 'ARM_STK3B learned_bonus=1\\.6', '"motion_relink_learned_bonus": (2\\.0|1\\.6)', 'ARM_XENV tag=(?!t65b25r70ff )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK|FLOWFIX)\\b)[A-Z0-9]+', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)', 'ARM_T60H tight_um=6\\.0', 'ARM_FLOWFIX \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWFIX enabled=False']
forbid['t65b25r70sr'] = ['ARM_STK3B learned_bonus=2\\.0', 'ARM_STK3B learned_bonus=1\\.6', '"motion_relink_learned_bonus": (2\\.0|1\\.6)', 'ARM_XENV tag=(?!t65b25r70sr )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK)\\b)[A-Z0-9]+', 'ARM_FLOWFIX', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)', 'ARM_T60H tight_um=6\\.0', '"short_track_rescue_trigger_removed_frac": (?!0\\.0(?!\\d))', '"adaptive_short_track_rescue": false']
forbid['mixyx50r70'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!mixyx50r70 )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK|MIXYX)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', 'ARM_MIXYX env flags missing', 'ARM_MIXYX (?:module )?anchor matched', 'ARM_MIXYX PATCH DID NOT PERSIST', 'ARM_MIXYX w outside', 'ARM_MIXYX needs the V1284 z-to-arr body', 'ARM_MIXYX full-SV z differs', 'ARM_MIXYX detection y/x not integral', 'ARM_MIXYX y/x blend not applied exactly once', 'ARM_MIXYX node count mismatch', 'ARM_MIXYX z-only SV y/x columns are not zero', 'ARM_MIXYX NO-OP', 'ARM_MIXYX assembled y/x', 'ARM_MIXYX w=(?!0\\.5(?!\\d))', 'final_yx_add=(?!0(?!\\d))']
forbid['t65b25r70ffsr'] = ['ARM_STK3B learned_bonus=2\\.0', 'ARM_STK3B learned_bonus=1\\.6', '"motion_relink_learned_bonus": (2\\.0|1\\.6)', 'ARM_XENV tag=(?!t65b25r70ffsr )', 'Traceback \\(most recent call last\\)', 'IndentationError', '\\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK|FLOWFIX)\\b)[A-Z0-9]+', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', '"motion_relink_tight_um": 6\\.0(?!\\d)', 'ARM_T60H tight_um=6\\.0', 'ARM_FLOWFIX \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWFIX enabled=False', '"short_track_rescue_trigger_removed_frac": (?!0\\.0(?!\\d))', '"adaptive_short_track_rescue": false']
forbid['ourvzlb25r70ff'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb25r70ff )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK|FLOWFIX)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', 'ARM_FLOWFIX \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWFIX enabled=False']
forbid['ourvzlt625'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.25(?!\\d))', '"motion_relink_tight_um": (?!6\\.25(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlt625 )', '\\bARM_(?!(?:STK3V|STK3B|T625H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bARM_T65H\\b', '"motion_relink_tight_um": 6\\.5(?!\\d)', 'tight_um=6\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.25(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!2\\.5(?!\\d))\\d']
forbid['ourvzlt675'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.75(?!\\d))', '"motion_relink_tight_um": (?!6\\.75(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlt675 )', '\\bARM_(?!(?:STK3V|STK3B|T675H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bARM_T65H\\b', '"motion_relink_tight_um": 6\\.5(?!\\d)', 'tight_um=6\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.75(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!2\\.5(?!\\d))\\d']
forbid['ourvzlb30'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!3\\.0(?!\\d))', '"motion_relink_learned_bonus": (?!3\\.0(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb30 )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', 'ARM_STK3B learned_bonus=2\\.5(?!\\d)', '"motion_relink_learned_bonus": 2\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.5(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!3\\.0(?!\\d))\\d']
forbid['ourvzlb20'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.0(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.0(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb20 )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', 'ARM_STK3B learned_bonus=2\\.5(?!\\d)', '"motion_relink_learned_bonus": 2\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.5(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!2\\.0(?!\\d))\\d']
forbid['ourvzlsr'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlsr )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', 'MOTION_RELINK_TIGHT_UM +(?!6\\.5(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!2\\.5(?!\\d))\\d', '"short_track_rescue_trigger_removed_frac": (?!0\\.0(?!\\d))', '"adaptive_short_track_rescue": false']
forbid['ourvzllf100'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!2\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!2\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzllf100 )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', 'MOTION_RELINK_TIGHT_UM +(?!6\\.5(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!2\\.5(?!\\d))\\d', '"output_linefit_weight": 0\\.8(?!\\d)', '"output_linefit_weight": (?!1\\.0(?!\\d))']
forbid['ourvzlb30t625'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!3\\.0(?!\\d))', '"motion_relink_learned_bonus": (?!3\\.0(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.25(?!\\d))', '"motion_relink_tight_um": (?!6\\.25(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb30t625 )', '\\bARM_(?!(?:STK3V|STK3B|T625H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bARM_T65H\\b', '"motion_relink_tight_um": 6\\.5(?!\\d)', 'tight_um=6\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.25(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!3\\.0(?!\\d))\\d', 'ARM_STK3B learned_bonus=2\\.5(?!\\d)', '"motion_relink_learned_bonus": 2\\.5(?!\\d)']
forbid['ourvzlffb30'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!3\\.0(?!\\d))', '"motion_relink_learned_bonus": (?!3\\.0(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.5(?!\\d))', '"motion_relink_tight_um": (?!6\\.5(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlffb30 )', '\\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK|FLOWFIX)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', 'ARM_FLOWFIX \\[\\w+\\] (?:FALLBACK|SKIPPED)', 'ARM_FLOWFIX enabled=False', 'ARM_STK3B learned_bonus=2\\.5(?!\\d)', '"motion_relink_learned_bonus": 2\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.5(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!3\\.0(?!\\d))\\d']
forbid['ourvzlb35t625'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!3\\.5(?!\\d))', '"motion_relink_learned_bonus": (?!3\\.5(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.25(?!\\d))', '"motion_relink_tight_um": (?!6\\.25(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb35t625 )', '\\bARM_(?!(?:STK3V|STK3B|T625H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bARM_T65H\\b', '"motion_relink_tight_um": 6\\.5(?!\\d)', 'tight_um=6\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.25(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!3\\.5(?!\\d))\\d', 'ARM_STK3B learned_bonus=2\\.5(?!\\d)', '"motion_relink_learned_bonus": 2\\.5(?!\\d)', 'ARM_STK3B learned_bonus=3\\.0(?!\\d)', '"motion_relink_learned_bonus": 3\\.0(?!\\d)', 'MOTION_RELINK_LEARNED_BONUS +2\\.5(?!\\d)', 'MOTION_RELINK_LEARNED_BONUS +3\\.0(?!\\d)']
forbid['ourvzlb40t625'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!4\\.0(?!\\d))', '"motion_relink_learned_bonus": (?!4\\.0(?!\\d))', 'ARM_T60H', 'ARM_T\\d+H tight_um=(?!6\\.25(?!\\d))', '"motion_relink_tight_um": (?!6\\.25(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb40t625 )', '\\bARM_(?!(?:STK3V|STK3B|T625H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bARM_T65H\\b', '"motion_relink_tight_um": 6\\.5(?!\\d)', 'tight_um=6\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.25(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!4\\.0(?!\\d))\\d', 'ARM_STK3B learned_bonus=2\\.5(?!\\d)', '"motion_relink_learned_bonus": 2\\.5(?!\\d)', 'ARM_STK3B learned_bonus=3\\.0(?!\\d)', '"motion_relink_learned_bonus": 3\\.0(?!\\d)', 'MOTION_RELINK_LEARNED_BONUS +2\\.5(?!\\d)', 'MOTION_RELINK_LEARNED_BONUS +3\\.0(?!\\d)', 'ARM_STK3B learned_bonus=3\\.5(?!\\d)', '"motion_relink_learned_bonus": 3\\.5(?!\\d)', 'MOTION_RELINK_LEARNED_BONUS +3\\.5(?!\\d)']
forbid['ourvzlb30t600'] = ['ARM_LCEFR', 'SUBVOXEL anchor', 'V1284 patch anchor mismatch', 'IndentationError', 'invalid V1284 displacement', 'head mount mismatch', 'V1284_YX module patch missing', 'SUBVOXEL offset/coord length mismatch', 'ARM_SV_Z_TO_ARR env flags missing', 'ARM_SV_Z_TO_ARR (?:module )?anchor matched', 'ARM_SV_Z_TO_ARR PATCH DID NOT PERSIST', 'ARM_SV_Z_TO_ARR needs the sub-voxel', 'ARM_SV_Z_TO_ARR expects BIOHUB_SUBVOXEL_ZONLY', 'ARM_SV_Z_TO_ARR offset/arr length mismatch', 'not applied exactly once', 'base z not integral', 'ARM_SV_Z_TO_ARR NO-OP', 'assembled z != integer peak', 'final_z_add=[1-9]', 'gather_int_z=0', 'Traceback \\(most recent call last\\)', 'ARM_STK3B learned_bonus=(?!3\\.0(?!\\d))', '"motion_relink_learned_bonus": (?!3\\.0(?!\\d))', 'ARM_T\\d+H tight_um=(?!6\\.0(?!\\d))', '"motion_relink_tight_um": (?!6\\.0(?!\\d))', '"motion_relink_velocity_weight": (?!0\\.25(?!\\d))', 'ARM_XENV tag=(?!ourvzlb30t600 )', '\\bARM_(?!(?:STK3V|STK3B|T60H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\\b)[A-Z0-9]+', '\\bSV_ARM_(?!HSG200\\b)[A-Z0-9]+', 'GDIV_DS', 'SUBVOXEL_ACTIVE', '"output_linefit_strict_linear": true', 'ARM_RAWLINK min_prob=\\S+ enabled=False', 'ARM_RAWLINK (?:\\[\\w+\\] )?min_prob=(?!0\\.7(?!\\d))', '"rawlink_min_prob": (?!0\\.7(?!\\d))', '\\bARM_T65H\\b', '"motion_relink_tight_um": 6\\.5(?!\\d)', 'tight_um=6\\.5(?!\\d)', 'MOTION_RELINK_TIGHT_UM +(?!6\\.0(?!\\d))\\d', 'MOTION_RELINK_LEARNED_BONUS +(?!3\\.0(?!\\d))\\d', 'ARM_STK3B learned_bonus=2\\.5(?!\\d)', '"motion_relink_learned_bonus": 2\\.5(?!\\d)', '\\bARM_T625H\\b', '"motion_relink_tight_um": 6\\.25(?!\\d)', 'tight_um=6\\.25(?!\\d)', 'MOTION_RELINK_TIGHT_UM +6\\.25(?!\\d)', 'MOTION_RELINK_TIGHT_UM +6\\.5(?!\\d)']
forbid["t6dl"] = [r"DEADLINE: \d+s since kernel start", r"REPAIR FAILED",
                  r"degraded=1", r"fallback=1"]
# xsv and xsvb are built WITHOUT the lcefr block, so an ARM_LCEFR line in their log means an xsvf
# build was pushed under their tag and the arm identity is wrong.
# xsv was pushed before the ARM_XENV identity line existed, so it cannot REQUIRE one; instead it
# forbids every OTHER arm's identity line, which closes the same hole (an xsvd log gated as xsv).
# xsv and xsvf were pushed before the ARM_XENV identity line existed, so their own logs contain
# NO such line. Forbidding ANY ARM_XENV line is therefore both correct for them and future-proof:
# it closes the hole where a newer arm's log (which always carries one) gates as xsv.
forbid["xsv"] = forbid["xsv"] + [r"ARM_XENV tag="]
forbid["xsvf"] = forbid["xsvf"] + [r"ARM_XENV tag="]
for _t in ("xsv", "xsvb", "xsvt", "xsvd", "xsv96", "xsvdv", "xsvdc",
           "xsvdd", "xsvd10", "xsvwz", "xsvmx", "xsvdu", "xsvmp", "xsvsr", "xsvgc", "xsvp26", "xsvmax"):
    forbid[_t] = forbid[_t] + [r"ARM_LCEFR"]
for t in tags:
    for pat in forbid.get(t, []):
        hit = re.search(pat, txt)
        if hit:
            fails.append(f"{t}: log contains {pat!r} ({hit.group(0)[:60]!r}), which means a stage this arm depends on silently did nothing")
# An UNKNOWN tag used to require nothing at all: need.get(tag, []) returned [] and sv_mark had no key, so a typo
# (or a brand-new arm whose entry was never written) sailed through with only the generic FINAL-count check. That is
# the one failure mode this gate exists to prevent, so an unrecognised tag is now a hard failure.
# --- t6stk3ff (ops/add_t6stk3ff_gate.py): t6stk3 + ARM_FLOWFIX after filter_output_graph. The pre-repair graph must
# be the 0.954 body's exactly (T6_BODY pins on FINAL + safe divisions); written edges = FINAL edges + bridged - dups.
if "t6stk3ff" in tags:
    import csv, os
    _fin, _sd, _dv = {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _dv.setdefault(d, (int(n_), int(e_), int(v_)))
    _rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _rs = None
    if os.path.isfile(_rsp):
        with open(_rsp, newline="", encoding="utf-8") as fh:
            _rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t6stk3ff: no run_stats.csv beside the log")
    _chg = []
    for d, (n0, e0, s0) in sorted(T6_BODY.items()):
        if _fin.get(d) != (n0, e0) or _sd.get(d) != s0:
            fails.append(f"t6stk3ff {d}: FINAL {_fin.get(d)} / safe divisions {_sd.get(d)} != the 0.954 body's "
                         f"{(n0, e0)} / {s0}: the repair runs after FINAL, so the pre-repair graph must be t6stk3's")
        _m = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                       r"bridged=(\d+) dups=(\d+) edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _m:
            fails.append(f"t6stk3ff {d}: no ARM_FLOWFIX status=ok line")
            continue
        _w, _fl, _ac, _ch, _br, _du, _a0, _a1, _v0, _v1, _mi = (int(v) for v in _m.groups()[:11])
        _chg.append(_ch)
        if txt.find(f"[{d}] FINAL:") < 0 or _m.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"t6stk3ff {d}: ARM_FLOWFIX line is not after the movie's FINAL line")
        if _a0 != e0 or _a1 != _a0 + _br - _du:
            fails.append(f"t6stk3ff {d}: flowfix edges {_a0}->{_a1} inconsistent with FINAL {e0} + {_br} - {_du}")
        if _v0 != _v1 or _v1 != s0 or _mi > 1:
            fails.append(f"t6stk3ff {d}: flowfix divisions {_v0}->{_v1} (want {s0}) or in-degree {_mi}")
        if float(_m.group(12)) > 20.0:
            fails.append(f"t6stk3ff {d}: flowfix {_m.group(12)} s > 20 s/movie (hidden overhead > ~66 min)")
        if _dv.get(d) != (n0, _a1, s0):
            fails.append(f"t6stk3ff {d}: written nodes/edges/divisions {_dv.get(d)} != {(n0, _a1, s0)}")
        if _rs is not None:
            try:
                _got = tuple(int(float((_rs.get(d) or {})[k])) for k in ("nodes", "edges"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got != (n0, _a1):
                fails.append(f"t6stk3ff {d}: run_stats (nodes, edges) {_got} != {(n0, _a1)}")
    if not _chg or max(_chg) == 0:
        fails.append("t6stk3ff: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
# --- t65s3ff (ops/add_t65s3ff_gate.py): t65s3 + ARM_FLOWFIX after filter_output_graph. The pre-repair graph must
# be the real t65s3 run's exactly (FINAL, safe divisions, motion_relink_tight_edges); written = FINAL + bridged - dups.
if "t65s3ff" in tags:
    import csv, os
    T65S3_BODY = {'44b6_0113de3b': (25620, 24883, 34, 24616), '44b6_0b24845f': (20678, 19401, 13, 19921), '6bba_05b6850b': (6150, 5954, 5, 5911), '6bba_05db0fb1': (70415, 68288, 26, 67052)}
    _fin, _sd, _dv = {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _dv.setdefault(d, (int(n_), int(e_), int(v_)))
    _rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _rs = None
    if os.path.isfile(_rsp):
        with open(_rsp, newline="", encoding="utf-8") as fh:
            _rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t65s3ff: no run_stats.csv beside the log")
    _chg = []
    for d, (n0, e0, s0, k0) in sorted(T65S3_BODY.items()):
        if _fin.get(d) != (n0, e0) or _sd.get(d) != s0:
            fails.append(f"t65s3ff {d}: FINAL {_fin.get(d)} / safe divisions {_sd.get(d)} != the real t65s3 run's "
                         f"{(n0, e0)} / {s0}: the repair runs after FINAL, so the pre-repair graph must be t65s3's")
        _m = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                       r"bridged=(\d+) dups=(\d+) edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _m:
            fails.append(f"t65s3ff {d}: no ARM_FLOWFIX status=ok line")
            continue
        _w, _fl, _ac, _ch, _br, _du, _a0, _a1, _v0, _v1, _mi = (int(v) for v in _m.groups()[:11])
        _chg.append(_ch)
        if txt.find(f"[{d}] FINAL:") < 0 or _m.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"t65s3ff {d}: ARM_FLOWFIX line is not after the movie's FINAL line")
        if _a0 != e0 or _a1 != _a0 + _br - _du:
            fails.append(f"t65s3ff {d}: flowfix edges {_a0}->{_a1} inconsistent with FINAL {e0} + {_br} - {_du}")
        if _v0 != _v1 or _v1 != s0 or _mi > 1:
            fails.append(f"t65s3ff {d}: flowfix divisions {_v0}->{_v1} (want {s0}) or in-degree {_mi}")
        if float(_m.group(12)) > 20.0:
            fails.append(f"t65s3ff {d}: flowfix {_m.group(12)} s > 20 s/movie (hidden overhead > ~66 min)")
        if _dv.get(d) != (n0, _a1, s0):
            fails.append(f"t65s3ff {d}: written nodes/edges/divisions {_dv.get(d)} != {(n0, _a1, s0)}")
        if _rs is not None:
            try:
                _got = tuple(int(float((_rs.get(d) or {})[k])) for k in ("nodes", "edges", "motion_relink_tight_edges"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got != (n0, _a1, k0):
                fails.append(f"t65s3ff {d}: run_stats (nodes, edges, motion_relink_tight_edges) {_got} != {(n0, _a1, k0)}"
                             " (tight edges must be the real t65s3 run's: a 6.0 gate gives fewer)")
    if not _chg or max(_chg) == 0:
        fails.append("t65s3ff: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
# --- t6stk3ff2 (ops/add_t6stk3ff2_gate.py): t6stk3 + ARM_FLOWFIX + FLOWCUT/RELINK after filter_output_graph. The
# pre-repair graph must be the 0.954 body's (T6_BODY pins); written edges = FINAL + bridged + bridged2 - dups - cut.
if "t6stk3ff2" in tags:
    import csv, os
    _fin, _sd, _dv = {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _dv.setdefault(d, (int(n_), int(e_), int(v_)))
    _rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _rs = None
    if os.path.isfile(_rsp):
        with open(_rsp, newline="", encoding="utf-8") as fh:
            _rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t6stk3ff2: no run_stats.csv beside the log")
    _chg, _cut = [], []
    for d, (n0, e0, s0) in sorted(T6_BODY.items()):
        if _fin.get(d) != (n0, e0) or _sd.get(d) != s0:
            fails.append(f"t6stk3ff2 {d}: FINAL {_fin.get(d)} / safe divisions {_sd.get(d)} != the 0.954 body's "
                         f"{(n0, e0)} / {s0}: the repair runs after FINAL, so the pre-repair graph must be t6stk3's")
        _m = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                       r"bridged=(\d+) dups=(\d+) cut=(\d+) changed2=(\d+) bridged2=(\d+) "
                       r"edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _m:
            fails.append(f"t6stk3ff2 {d}: no ARM_FLOWFIX status=ok line")
            continue
        _w, _fl, _ac, _ch, _br, _du, _cu, _ch2, _br2, _a0, _a1, _v0, _v1, _mi = (int(v) for v in _m.groups()[:14])
        _chg.append(_ch)
        _cut.append(_cu)
        if txt.find(f"[{d}] FINAL:") < 0 or _m.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"t6stk3ff2 {d}: ARM_FLOWFIX line is not after the movie's FINAL line")
        if _a0 != e0 or _a1 != _a0 + _br + _br2 - _du - _cu:
            fails.append(f"t6stk3ff2 {d}: flowfix edges {_a0}->{_a1} inconsistent with FINAL {e0} + {_br} + {_br2} - {_du} - {_cu}")
        if _v0 != _v1 or _v1 != s0 or _mi > 1:
            fails.append(f"t6stk3ff2 {d}: flowfix divisions {_v0}->{_v1} (want {s0}) or in-degree {_mi}")
        if float(_m.group(15)) > 20.0:
            fails.append(f"t6stk3ff2 {d}: flowfix {_m.group(15)} s > 20 s/movie (hidden overhead > ~66 min)")
        if _dv.get(d) != (n0, _a1, s0):
            fails.append(f"t6stk3ff2 {d}: written nodes/edges/divisions {_dv.get(d)} != {(n0, _a1, s0)}")
        if _rs is not None:
            try:
                _got = tuple(int(float((_rs.get(d) or {})[k])) for k in ("nodes", "edges"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got != (n0, _a1):
                fails.append(f"t6stk3ff2 {d}: run_stats (nodes, edges) {_got} != {(n0, _a1)}")
    if not _chg or max(_chg) == 0:
        fails.append("t6stk3ff2: ARM_FLOWFIX changed 0 edges on every visible movie: the repair never fired")
    if not _cut or max(_cut) == 0:
        fails.append("t6stk3ff2: FLOWCUT cut 0 edges on every visible movie: the extension never fired")
# --- t6stk3fl (ops/add_t6stk3fl_gate.py): t6stk3ff + ARM_FLOWLINK (flow inside the cell-5 relink). Topology moves,
# so the pins are the box c5 replay of the SAME kernel (wf18 vis_pins.json), not T6_BODY.
if "t6stk3fl" in tags:
    import csv, os
    T6FL_BODY = {'44b6_0113de3b': (25662, 24984, 37, 24915), '44b6_0b24845f': (20691, 19414, 13, 19812), '6bba_05b6850b': (6135, 5930, 6, 5869), '6bba_05db0fb1': (70365, 68249, 19, 67434)}
    _fin, _sd, _dv = {}, {}, {}
    for d, n_, e_ in re.findall(r"\[(\w+)\] FINAL: (\d+) nodes, (\d+) edges", txt):
        _fin.setdefault(d, (int(n_), int(e_)))
    for d, a_ in re.findall(r"\[(\w+)\] after safe-division repair: \d+ nodes, \d+ edges \([^)]*?\badded=(\d+)", txt):
        _sd.setdefault(d, int(a_))
    for d, n_, e_, v_ in re.findall(r"(?m)^\s+(\w+): nodes=(\d+) edges=(\d+) divisions=(\d+)\s*$", txt):
        _dv.setdefault(d, (int(n_), int(e_), int(v_)))
    _rsp = os.path.join(os.path.dirname(os.path.abspath(log)), "run_stats.csv")
    _rs = None
    if os.path.isfile(_rsp):
        with open(_rsp, newline="", encoding="utf-8") as fh:
            _rs = {r.get("dataset"): r for r in csv.DictReader(fh)}
    else:
        fails.append("t6stk3fl: no run_stats.csv beside the log")
    _flg = []
    for d, (n0, e0, s0, k0) in sorted(T6FL_BODY.items()):
        if _fin.get(d) != (n0, e0) or _sd.get(d) != s0:
            fails.append(f"t6stk3fl {d}: FINAL {_fin.get(d)} / safe divisions {_sd.get(d)} != the box replay of this "
                         f"kernel {(n0, e0)} / {s0}")
        _l = re.search(r"ARM_FLOWLINK \[%s\] relink flagged_sources=(\d+)" % d, txt)
        _flg.append(int(_l.group(1)) if _l else 0)
        _m = re.search(r"ARM_FLOWFIX \[%s\] status=ok windows=(\d+) flagged=(\d+) acted=(\d+) changed=(\d+) "
                       r"bridged=(\d+) dups=(\d+) edges=(\d+)->(\d+) divs=(\d+)->(\d+) max_in=(\d+) secs=([\d.]+) " % d, txt)
        if not _m:
            fails.append(f"t6stk3fl {d}: no ARM_FLOWFIX status=ok line")
            continue
        _w, _fl, _ac, _ch, _br, _du, _a0, _a1, _v0, _v1, _mi = (int(v) for v in _m.groups()[:11])
        if txt.find(f"[{d}] FINAL:") < 0 or _m.start() < txt.find(f"[{d}] FINAL:"):
            fails.append(f"t6stk3fl {d}: ARM_FLOWFIX line is not after the movie's FINAL line")
        if _a0 != e0 or _a1 != _a0 + _br - _du:
            fails.append(f"t6stk3fl {d}: flowfix edges {_a0}->{_a1} inconsistent with FINAL {e0} + {_br} - {_du}")
        if _v0 != _v1 or _v1 != s0 or _mi > 1:
            fails.append(f"t6stk3fl {d}: flowfix divisions {_v0}->{_v1} (want {s0}) or in-degree {_mi}")
        if float(_m.group(12)) > 20.0:
            fails.append(f"t6stk3fl {d}: flowfix {_m.group(12)} s > 20 s/movie")
        if _dv.get(d) != (n0, _a1, s0):
            fails.append(f"t6stk3fl {d}: written nodes/edges/divisions {_dv.get(d)} != {(n0, _a1, s0)}")
        if _rs is not None:
            try:
                _got = tuple(int(float((_rs.get(d) or {})[k])) for k in ("nodes", "edges", "motion_relink_tight_edges"))
            except (KeyError, TypeError, ValueError):
                _got = None
            if _got != (n0, _a1, k0):
                fails.append(f"t6stk3fl {d}: run_stats (nodes, edges, motion_relink_tight_edges) {_got} != {(n0, _a1, k0)}")
    if not _flg or max(_flg) == 0:
        fails.append("t6stk3fl: FLOWLINK flagged 0 relink sources on every visible movie: the linker flow never fired")
unknown = [t for t in tags if t not in need and t not in sv_mark and not t.startswith("hsoft")]
if unknown:
    fails.append(f"unknown tag(s) {unknown}: no need/sv_mark entry, so this arm would be submitted ungated. "
                 "Add an entry (markers + the live config echoes) before submitting it.")
print("FINAL", final, "| fallback frames", fb)
print("GATE_FAIL: " + "; ".join(fails) if fails else "GATE_PASS")
sys.exit(1 if fails else 0)
