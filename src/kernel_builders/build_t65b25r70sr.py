#!/usr/bin/env python3
"""t65b25r70sr = t65b25r70 (team representative 0.954: t6stk3 body + relink tight 6.5 + learned bonus 2.5 + t6r70's
raw-ILP override "rawlink" at min_prob 0.70) with the adaptive short-track rescue ARMED unconditionally, exactly as t6sr
armed it on the t6stk3 body (tied 0.954): BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC 0.10 -> 0.0.

usage: python scratch_kernels/build_t65b25r70sr.py [tag]        (default tag t65b25r70sr)

t6sr's whole change (v_t6sr vs v_t6stk3, re-derived and checked here) is two lines appended to cell 0: the env
assignment and its ARM_XENV print. The assignment line is copied out of v_t6sr verbatim; t65b25r70's ARM_XENV line is
replaced by that assignment + this arm's ARM_XENV line. Cell 2 reads the variable once (float, default "0.10") and
echoes it in the config display ("short_track_rescue_trigger_removed_frac": 0.0 is the live receipt); cell 5's
filter_output_graph then runs the rescue branch (`removed_frac >= trigger`) on every movie, before FINAL and so
before the rawlink override. The rescue's five knobs (min_len 4, mean edge prob >= 0.88, max mean edge dist 3.0 um,
node budget min(120, 1.2%)) are the base's, untouched.
Checks (hard stops): md5 pins (v_t65b25r70, v_t6sr, v_t6stk3); t6sr differs from t6stk3 in cell 0 only, by exactly
the two appended lines; the env line is exactly once in v_t6sr and absent from the base; cell 2 reads it exactly once;
cells other than 0 byte-identical to t65b25r70; cell 0 differs only by the XENV swap + the env line; compile all cells;
metadata copied from v_t65b25r70 with only id/title changed.
Markers: ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 SR=armed (cell 0); cell-2 echo
"short_track_rescue_trigger_removed_frac": 0.0; run_stats short_track_rescue_triggered/components/nodes.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65b25r70"
BASE_MD5 = "60722ec9a2f277733656ba6bf5b559af"  # v_t65b25r70/kernel.ipynb (submitted 56640601, public 0.954)
SR = SK / "v_t6sr"
SR_MD5 = "7bcf71b4dc695473755a6e7b5247297f"  # v_t6sr/kernel.ipynb (the t6sr board run, 0.954)
BODY = SK / "v_t6stk3"
BODY_MD5 = "643f4de949f707e161b118733e35e6df"
NL = chr(10)
BASE_XENV = 'print("ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept", flush=True)'
SR_ENV = 'os.environ["BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC"] = "0.0"'
SR_XENV = ('print("ARM_XENV tag=t6sr BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC=%s" % '
           '(os.environ["BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC"],), flush=True)')
XENV_FMT = 'print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 SR=armed", flush=True)'
READ = 'SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC = float(os.environ.get("BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC", "0.10"))'


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t65b25r70sr"
    for d, m in ((BASE, BASE_MD5), (SR, SR_MD5), (BODY, BODY_MD5)):
        if md5(d / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (d.name, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, sr = cells_of(SR / "kernel.ipynb")
    _, body = cells_of(BODY / "kernel.ipynb")
    orig = list(cells)
    # ---- re-derive t6sr's change: cell 0 only, exactly two appended lines (env + its XENV)
    if len(sr) != len(body) or [i for i, (a, b) in enumerate(zip(body, sr)) if a != b] != [0]:
        raise SystemExit("v_t6sr differs from v_t6stk3 outside cell 0")
    bl, sl = body[0].rstrip(NL).split(NL), sr[0].rstrip(NL).split(NL)
    if sl[:-2] != bl or sl[-2:] != [SR_ENV, SR_XENV]:
        raise SystemExit("t6sr's cell 0 is not t6stk3's + [env line, XENV]: %r" % sl[-2:])
    if sum(1 for c in sr if c and SR_ENV in c) != 1 or sr[0].count(SR_ENV) != 1:
        raise SystemExit("t6sr's env line is not exactly once")
    # ---- base preconditions
    if any("BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC" in (c or "") for i, c in enumerate(cells) if i != 2):
        raise SystemExit("base already sets/reads the rescue trigger outside cell 2")
    if cells[2].count(READ) != 1 or cells[2].count("BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC") != 1:
        raise SystemExit("cell 2 does not read BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC exactly once (default 0.10)")
    if cells[2].count('"short_track_rescue_trigger_removed_frac": SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC,') < 1:
        raise SystemExit("cell 2 does not echo the trigger")
    if cells[5].count("if removed_frac >= SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC:") != 1:
        raise SystemExit("cell 5 rescue branch anchor not exactly once")
    if cells[0].count("ARM_XENV") != 1:
        raise SystemExit("base cell 0 must carry exactly one ARM_XENV line")
    lines = cells[0].rstrip(NL).split(NL)
    if lines[-1] != BASE_XENV:
        raise SystemExit("t65b25r70 cell 0 does not end with its ARM_XENV line")
    xenv = XENV_FMT % tag
    cells[0] = NL.join(lines[:-1] + [SR_ENV, xenv]) + NL
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i != 0 and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    ol, nl_ = orig[0].rstrip(NL).split(NL), cells[0].rstrip(NL).split(NL)
    if nl_[:-2] != ol[:-1] or nl_[-2:] != [SR_ENV, xenv]:
        raise SystemExit("cell 0 differs from t65b25r70's by more than the XENV swap + env line")
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
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
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read of the written notebook differs from the built cells")
    changed = [i for i, (a, b) in enumerate(zip(orig, built)) if a != b]
    if changed != [0]:
        raise SystemExit("cells changed vs v_t65b25r70 = %r (expected [0])" % changed)
    print("built", dest, "| base v_t65b25r70 (md5 %s) | short-track rescue trigger 0.10 -> 0.0 (t6sr's line)" % BASE_MD5)
    print("cells changed vs v_t65b25r70:", changed)
    print("  cell 0: -", BASE_XENV)
    print("          +", SR_ENV, "(verbatim from v_t6sr md5 %s)" % SR_MD5)
    print("          +", xenv)
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
