#!/usr/bin/env python3
"""Shared core for the 09-29 last-slot pre-build arms: each is v_ourvzlb25r70 (public 0.955, 56657610: V1284 y/x head
+ sub-voxel z to the edge model, relink tight 6.5, learned bonus 2.5, rawlink 0.70) with ONE cell-0 env change and a
new ARM_XENV identity line. Nothing else changes (cells 1..11 byte for byte, metadata only id/title).

Arms (each has its own thin builder scratch_kernels/build_<tag>.py that calls build(<tag>, ARMS[<tag>])):
  ourvzlt625 : BIOHUB_MOTION_RELINK_TIGHT_UM "6.5" -> "6.25", marker ARM_T65H tight_um=6.5 -> ARM_T625H tight_um=6.25
  ourvzlt675 : tight "6.5" -> "6.75", marker -> ARM_T675H tight_um=6.75 (the exact two lines v_t675b25 carries)
  ourvzlb30  : BIOHUB_MOTION_RELINK_LEARNED_BONUS '2.5' -> '3.0', marker ARM_STK3B learned_bonus=3.0
  ourvzlb20  : bonus '2.5' -> '2.0', marker ARM_STK3B learned_bonus=2.0 (the exact two lines v_t65b20 carries)
  ourvzlsr   : + os.environ["BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC"] = "0.0" before the XENV line (the exact line
               build_t65b25r70sr.py appended; checked against v_t65b25r70sr)
  ourvzllf100: + os.environ["BIOHUB_OUTPUT_LINEFIT_WEIGHT"] = "1.0" appended right AFTER the (new) XENV line (cell 2 reads it,
               default "0.8", and echoes "output_linefit_weight": 1.0)
XENV: ARM_XENV tag=<tag> TIGHT=<t> BONUS=<b> RAWLINK=0.70 [SR=armed] [LINEFIT_W=1.0] V1284_HEAD=mounted SUBVOXEL=z-to-arr
V1284_AXES=yx

Checks (all hard stops): md5 pins (base + the reference kernels the lines are cross-checked against); every anchor
exactly once in cell 0 and the env name absent outside cells 0/2; the marker is the line right after its env line;
none of the new values already in the base; the cell-2 reader/echo, cell-5 consumer and cell-9 echo exist exactly once;
built cells changed vs base == [0]; cell-0 line diff == exactly the expected lines; exactly one ARM_XENV; compile every
cell; re-read of the written notebook == built cells; metadata == base's except id/title (V1284 head mounted, T4, GPU,
no internet, private).
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourvzlb25r70"
BASE_MD5 = "9019774943ccdb39ebffe553b74325f1"  # v_ourvzlb25r70/kernel.ipynb (pushed 09-28 20:24Z, submitted 56657610, 0.955)
NL = chr(10)
BASE_XENV = ('print("ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr '
             'V1284_AXES=yx", flush=True)')
XENV_FMT = ('print("ARM_XENV tag=%s TIGHT=%s BONUS=%s RAWLINK=0.70 %s%sV1284_HEAD=mounted SUBVOXEL=z-to-arr '
            'V1284_AXES=yx", flush=True)')

TIGHT_ENV = 'os.environ["BIOHUB_MOTION_RELINK_TIGHT_UM"] = "%s"'
TIGHT_MARK = 'print("ARM_%s tight_um=%s", flush=True)'
BONUS_ENV = 'os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'%s\''
BONUS_MARK = 'print("ARM_STK3B learned_bonus=%s", flush=True)'
SR_ENV = 'os.environ["BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC"] = "0.0"'
LF_ENV = 'os.environ["BIOHUB_OUTPUT_LINEFIT_WEIGHT"] = "1.0"'

# reference kernels whose lines must be reproduced verbatim (md5-pinned)
REFS = {
    "v_t675b25": "b8e833a9e0b613c9f3f664f3ec40879f",       # tight 6.75 env + ARM_T675H marker (build_t675b25.py)
    "v_t65b20": "3ceebd4c868985d0fd7c1d02321999f2",        # bonus '2.0' env + ARM_STK3B learned_bonus=2.0 (build_t65b20.py)
    "v_t65b25r70sr": "b098a1503b51c5726fc907cdee0de3eb",   # SR env line (build_t65b25r70sr.py)
}

C2 = {
    "tight": ['MOTION_RELINK_TIGHT_UM = float(os.environ.get("BIOHUB_MOTION_RELINK_TIGHT_UM", "6.0"))',
              '"motion_relink_tight_um": MOTION_RELINK_TIGHT_UM,'],
    "bonus": ['MOTION_RELINK_LEARNED_BONUS = float(os.environ.get("BIOHUB_MOTION_RELINK_LEARNED_BONUS", "0.75"))',
              '"motion_relink_learned_bonus": MOTION_RELINK_LEARNED_BONUS,'],
    "sr": ['SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC = float(os.environ.get("BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC", "0.10"))',
           '"short_track_rescue_trigger_removed_frac": SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC,'],
    "lf": ['OUTPUT_LINEFIT_WEIGHT = float(os.environ.get("BIOHUB_OUTPUT_LINEFIT_WEIGHT", "0.8"))',
           '"output_linefit_weight": OUTPUT_LINEFIT_WEIGHT,'],
}
C5 = {
    "tight": 'for pass_name, gate_um in (("tight", MOTION_RELINK_TIGHT_UM), ("relaxed", MOTION_RELINK_RELAXED_UM)):',
    "bonus": "cost[i, j] = motion + 0.05 * raw - MOTION_RELINK_LEARNED_BONUS * prob",
    "sr": "if removed_frac >= SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC:",
    "lf": "weight = float(np.clip(OUTPUT_LINEFIT_WEIGHT, 0.0, 1.0))",
}
C9 = {"tight": '"MOTION_RELINK_TIGHT_UM",', "bonus": '"MOTION_RELINK_LEARNED_BONUS",'}
ENVNAME = {"tight": "BIOHUB_MOTION_RELINK_TIGHT_UM", "bonus": "BIOHUB_MOTION_RELINK_LEARNED_BONUS",
           "sr": "BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC", "lf": "BIOHUB_OUTPUT_LINEFIT_WEIGHT"}

ARMS = {
    "ourvzlt625": dict(kind="tight", value="6.25", mark="T625H", xt="6.25", xb="2.50", sr=False, ref=None),
    "ourvzlt675": dict(kind="tight", value="6.75", mark="T675H", xt="6.75", xb="2.50", sr=False, ref="v_t675b25"),
    "ourvzlb30": dict(kind="bonus", value="3.0", xt="6.5", xb="3.00", sr=False, ref=None),
    "ourvzlb20": dict(kind="bonus", value="2.0", xt="6.5", xb="2.00", sr=False, ref="v_t65b20"),
    "ourvzlsr": dict(kind="sr", value="0.0", xt="6.5", xb="2.50", sr=True, ref="v_t65b25r70sr"),
    "ourvzllf100": dict(kind="lf", value="1.0", xt="6.5", xb="2.50", sr=False, lf=True, ref=None),
}


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def lines_of(c):
    return c.rstrip(NL).split(NL)


def build(tag, arm):
    kind = arm["kind"]
    if md5(BASE / "kernel.ipynb") != BASE_MD5:
        raise SystemExit("STOP: v_ourvzlb25r70/kernel.ipynb md5 changed (expected %s)" % BASE_MD5)
    for d, m in REFS.items():
        if md5(SK / d / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (d, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    orig = list(cells)
    if len(cells) != 12 or any(c is None for c in cells):
        raise SystemExit("unexpected notebook shape (need 12 code cells)")
    c0 = cells[0]
    ol = lines_of(c0)
    if ol[-1] != BASE_XENV or c0.count("ARM_XENV") != 1 or sum("ARM_XENV" in c for c in cells) != 1:
        raise SystemExit("ourvzlb25r70 cell 0 does not end with its one ARM_XENV line")
    # ---- generic preconditions: the three knobs sit where the gate expects them
    for k in ("tight", "bonus", "sr", "lf"):
        for a in C2[k]:
            if cells[2].count(a) != 1:
                raise SystemExit("cell 2 lacks %r exactly once" % a[:70])
        if cells[5].count(C5[k]) != 1:
            raise SystemExit("cell 5 consumer for %s not exactly once" % k)
        if k in C9 and cells[9].count(C9[k]) != 1:
            raise SystemExit("cell 9 PP_BASE_CONFIG does not list %s exactly once" % k)
        if any(ENVNAME[k] in c for i, c in enumerate(cells) if i not in (0, 2)):
            raise SystemExit("%s referenced outside cells 0/2" % ENVNAME[k])
    t_env_old, t_mark_old = TIGHT_ENV % "6.5", TIGHT_MARK % ("T65H", "6.5")
    b_env_old, b_mark_old = BONUS_ENV % "2.5", BONUS_MARK % "2.5"
    for name, a in (("tight_env", t_env_old), ("tight_mark", t_mark_old), ("bonus_env", b_env_old),
                    ("bonus_mark", b_mark_old)):
        if c0.count(a) != 1:
            raise SystemExit("anchor %s matched %d times in cell 0" % (name, c0.count(a)))
    t_env_idx = next(i for i, x in enumerate(ol) if x.startswith(t_env_old))
    b_env_idx = next(i for i, x in enumerate(ol) if x.startswith(b_env_old))
    if ol[t_env_idx + 1] != t_mark_old or ol[b_env_idx + 1] != b_mark_old or ol[b_env_idx] != b_env_old:
        raise SystemExit("tight/bonus marker is not the line right after its env assignment")
    if any(ENVNAME["sr"] in x for x in ol):
        raise SystemExit("base cell 0 already sets the rescue trigger")
    if any(ENVNAME["lf"] in x for x in ol):
        raise SystemExit("base cell 0 already sets the line-fit weight")
    xenv = XENV_FMT % (tag, arm["xt"], arm["xb"], "SR=armed " if arm["sr"] else "",
                       "LINEFIT_W=1.0 " if arm.get("lf") else "")
    # ---- the edit
    nl = list(ol)
    if kind == "tight":
        env_new, mark_new = TIGHT_ENV % arm["value"], TIGHT_MARK % (arm["mark"], arm["value"])
        for bad in (env_new, "ARM_%s" % arm["mark"], "tight_um=%s" % arm["value"], "TIGHT=%s " % arm["value"]):
            if any(bad in c for c in cells):
                raise SystemExit("base unexpectedly carries %r" % bad)
        nl[t_env_idx] = ol[t_env_idx].replace(t_env_old, env_new, 1)  # trailing t65h comment left alone (as t675b25)
        nl[t_env_idx + 1] = mark_new
        nl[-1] = xenv
        exp = [(ol[t_env_idx], nl[t_env_idx]), (t_mark_old, mark_new), (BASE_XENV, xenv)]
    elif kind == "bonus":
        env_new, mark_new = BONUS_ENV % arm["value"], BONUS_MARK % arm["value"]
        for bad in (env_new, "learned_bonus=%s" % arm["value"], "BONUS=%s " % arm["xb"]):
            if any(bad in c for c in cells):
                raise SystemExit("base unexpectedly carries %r" % bad)
        nl[b_env_idx] = env_new
        nl[b_env_idx + 1] = mark_new
        nl[-1] = xenv
        exp = [(b_env_old, env_new), (b_mark_old, mark_new), (BASE_XENV, xenv)]
    elif kind == "sr":
        nl = ol[:-1] + [SR_ENV, xenv]
        exp = None
    elif kind == "lf":
        nl = ol[:-1] + [xenv, LF_ENV]
        exp = None
    else:
        raise SystemExit("unknown kind " + kind)
    c0n = NL.join(nl) + NL
    cells[0] = c0n
    # ---- reference cross-checks: the changed lines are the proven lines of the reference kernel, verbatim
    if arm["ref"]:
        _, rc = cells_of(SK / arm["ref"] / "kernel.ipynb")
        rl = lines_of(rc[0])
        if kind == "tight":
            ref_env = [x for x in rl if x.startswith(TIGHT_ENV % arm["value"])]
            if ref_env != [nl[t_env_idx]] or rl.count(nl[t_env_idx + 1]) != 1 \
                    or rl[rl.index(ref_env[0]) + 1] != nl[t_env_idx + 1]:
                raise SystemExit("tight env/marker lines differ from %s's: %r" % (arm["ref"], ref_env))
        elif kind == "bonus":
            i = rl.index(nl[b_env_idx]) if nl[b_env_idx] in rl else -1
            if i < 0 or rl.count(nl[b_env_idx]) != 1 or rl[i + 1] != nl[b_env_idx + 1]:
                raise SystemExit("bonus env/marker lines differ from %s's" % arm["ref"])
        elif kind == "sr":
            if rl.count(SR_ENV) != 1 or rl[-2] != SR_ENV or sum(SR_ENV in c for c in rc) != 1:
                raise SystemExit("SR env line is not v_t65b25r70sr's second-to-last cell-0 line verbatim")
    # ---- checks on the built cells
    changed = [i for i, (a, b) in enumerate(zip(orig, cells)) if a != b]
    if changed != [0]:
        raise SystemExit("cells changed vs v_ourvzlb25r70 = %r (expected [0])" % changed)
    bl = lines_of(cells[0])
    if kind == "sr":
        if bl[:-2] != ol[:-1] or bl[-2:] != [SR_ENV, xenv] or len(bl) != len(ol) + 1:
            raise SystemExit("cell 0 differs from the base by more than the XENV swap + SR env line")
        diff = [("", SR_ENV), (BASE_XENV, xenv)]
    elif kind == "lf":
        if bl[:-2] != ol[:-1] or bl[-2:] != [xenv, LF_ENV] or len(bl) != len(ol) + 1:
            raise SystemExit("cell 0 differs from the base by more than the XENV swap + appended line-fit env line")
        diff = [(BASE_XENV, xenv), ("", LF_ENV)]
    else:
        if len(bl) != len(ol):
            raise SystemExit("cell 0 line count changed")
        diff = [(x, y) for x, y in zip(ol, bl) if x != y]
        if diff != exp:
            raise SystemExit("cell 0 diff is not exactly the expected 3 lines: %r" % diff)
    if sum(c.count("ARM_XENV") for c in cells) != 1 or cells[0].count(xenv) != 1:
        raise SystemExit("not exactly one ARM_XENV line in the build")
    # every other knob is the base's value, exactly once
    keep = []
    if kind != "tight":
        keep += [t_env_old, t_mark_old]
    if kind != "bonus":
        keep += [b_env_old, b_mark_old]
    for a in keep + ['os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"', 'os.environ["BIOHUB_MOTION_RELINK_VELOCITY_WEIGHT"] = "0.25"']:
        if cells[0].count(a) != 1:
            raise SystemExit("unchanged knob %r not exactly once in the built cell 0" % a)
    if kind == "tight" and any('RELINK_TIGHT_UM"] = "6.5"' in c or "ARM_T65H" in c for c in cells):
        raise SystemExit("a stale 6.5 tight value survived")
    if kind == "bonus" and any("LEARNED_BONUS\"] = '2.5'" in c or "learned_bonus=2.5" in c for c in cells):
        raise SystemExit("a stale 2.5 bonus value survived")
    if kind != "sr" and any(SR_ENV in c for c in cells):
        raise SystemExit("SR env leaked into a non-sr arm")
    if kind != "lf" and any(ENVNAME["lf"] in c for i, c in enumerate(cells) if i != 2):
        raise SystemExit("line-fit env leaked into a non-lf arm")
    if kind == "lf" and (sum(c.count(ENVNAME["lf"]) for c in cells) != 2 or cells[0].count(LF_ENV) != 1):
        raise SystemExit("line-fit env not set exactly once in cell 0 (+ the one cell-2 read)")
    for i, c in enumerate(cells):
        compile(c, "%s:cell%d" % (tag, i), "exec")
    # ---- write
    k = 0
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["source"] = cells[k].splitlines(keepends=True)
            c["outputs"] = []
            c["execution_count"] = None
        k += 1
    dest = SK / ("v_" + tag)
    dest.mkdir(parents=True, exist_ok=True)
    with open(dest / "kernel.ipynb", "w", encoding="utf-8") as fh:
        json.dump(nb, fh)
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    with open(dest / "kernel-metadata.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    # ---- re-read and report
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read of the written notebook differs from the built cells")
    changed = [i for i, (a, b) in enumerate(zip(orig, built)) if a != b]
    if changed != [0]:
        raise SystemExit("re-read: cells changed vs v_ourvzlb25r70 = %r (expected [0])" % changed)
    bm = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k_ for k_ in set(bm) | set(nm) if bm.get(k_) != nm.get(k_))
    if mdiff != ["id", "title"]:
        raise SystemExit("metadata differs from ourvzlb25r70's beyond id/title: %r" % mdiff)
    if "anvithpothula/biohub-v1284-head-s075" not in nm["dataset_sources"] or nm.get("is_private") is not True \
            or nm.get("enable_internet") is not False or nm.get("enable_gpu") is not True:
        raise SystemExit("metadata: V1284 head not mounted / not private / internet on / no GPU")
    print("built", dest, "| base v_ourvzlb25r70 (md5 %s) | %s -> %s" % (BASE_MD5, ENVNAME[kind], arm["value"]))
    print("cells changed vs v_ourvzlb25r70:", changed, "| metadata diff:", mdiff, "| datasets", nm["dataset_sources"],
          "| machine", nm.get("machine_shape"))
    for x, y in diff:
        if x:
            print("  -", x)
        print("  +", y)
    if arm["ref"]:
        print("changed lines cross-checked verbatim against %s (md5 %s)" % (arm["ref"], REFS[arm["ref"]]))
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))
