#!/usr/bin/env python3
"""t65b20d04 = t65b20 (our top public entry 56628029: t65s3 body, relink TIGHT 6.5, learned bonus 2.0) with the tracking
ILP division weight lowered 1.2 -> 0.4. Everything else is t65b20's byte for byte.

usage: python scratch_kernels/build_t65b20d04.py [tag]        (default tag t65b20d04)

WHY (HANDOFF 09-28 15:45Z): forum 743929 reports ILP_DIVISION_WEIGHT 1.2 -> 0.4 as +0.001 on the public board over a
same-round control on the 0.953 public body. Our "PROVEN INERT" note only covers weights >= 1: with
ILP_APPEARANCE_WEIGHT = 0 the solver forks iff p2 >= division_weight, and p2 <= 1, so 0.4 is the first value that lets
the ILP fork at all. Whether a fork survives motion_relink_edges (one-to-one relink) is what the visible run measures;
the ILP-selected edges also seed learned_edge_probs (the BONUS*prob term), so the arm can move edges without forks.

WHERE the weight lives in v_t65b20 (every site; only the first carries a value):
  cell 0  os.environ["BIOHUB_ILP_DIVISION_WEIGHT"] = "1.2"      <- the ONLY literal; rewritten to "0.4"
  cell 2  ILP_DIVISION_WEIGHT = float(os.environ.get("BIOHUB_ILP_DIVISION_WEIGHT", "1.0"))   (reader, unchanged)
  cell 2  "ilp_division_weight": ILP_DIVISION_WEIGHT,           (CONFIG_DISPLAY echo = gate receipt, unchanged)
  cell 4  "--ilp-division-weight", str(ILP_DIVISION_WEIGHT)     (test predictor command; both GPU shards, unchanged)
  cell 7  "--ilp-division-weight", str(ILP_DIVISION_WEIGHT)     (in-kernel validator command; VALIDATOR_ENABLE=0)
The predictor (scripts/predict_unet_transformer.py) passes cfg.ilp_division_weight straight to td.solvers.ILPSolver
(division_weight=...); the dual-seed / reverse passes fuse edge probabilities BEFORE that single ILP call, so there is
no second solver site. The kernel's cell-4 patches do not touch the ILP arguments (checked below).
Markers: cell 0 'ARM_ILPDIV weight=0.4' (right after the env line) and
'ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.00 ILPDIV=0.4 LCEFR=kept' (replaces t65b20's XENV line). Receipts in the log:
'"ilp_division_weight": 0.4' (cell-2 echo) and '--ilp-division-weight 0.4' on each GPU-shard command line.
"""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65b20"
BASE_MD5 = "3ceebd4c868985d0fd7c1d02321999f2"  # v_t65b20/kernel.ipynb as built by build_t65b20.py (submitted 56628029)
NL = chr(10)

ENV_OLD = 'os.environ["BIOHUB_ILP_DIVISION_WEIGHT"] = "1.2"     ' + NL  # t65b20 carries 5 trailing spaces here
ENV_NEW = 'os.environ["BIOHUB_ILP_DIVISION_WEIGHT"] = "0.4"' + NL
MARK_NEW = 'print("ARM_ILPDIV weight=0.4", flush=True)' + NL
XENV_OLD = 'print("ARM_XENV tag=t65b20 TIGHT=6.5 BONUS=2.00 LCEFR=kept", flush=True)'
XENV_FMT = 'print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.00 ILPDIV=0.4 LCEFR=kept", flush=True)'
# downstream sites: must exist exactly once each and must carry no literal weight
SITES = {
    2: ['ILP_DIVISION_WEIGHT = float(os.environ.get("BIOHUB_ILP_DIVISION_WEIGHT", "1.0"))' + NL,
        '    "ilp_division_weight": ILP_DIVISION_WEIGHT,' + NL],
    4: ['    "--ilp-division-weight",' + NL + '    str(ILP_DIVISION_WEIGHT),' + NL],
    7: ['        "--ilp-division-weight", str(ILP_DIVISION_WEIGHT),' + NL],
}


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t65b20d04"
    raw = (BASE / "kernel.ipynb").read_bytes()
    if hashlib.md5(raw).hexdigest() != BASE_MD5:
        raise SystemExit("STOP: v_t65b20/kernel.ipynb changed since it was submitted (md5 mismatch)")
    nb, cells = cells_of(BASE / "kernel.ipynb")
    orig = list(cells)
    c0 = cells[0]
    for name, a in (("env_divw", ENV_OLD), ("xenv", XENV_OLD)):
        if c0.count(a) != 1:
            raise SystemExit("anchor %s matched %d times in cell 0" % (name, c0.count(a)))
    # the env line is the only place a division-weight VALUE is set anywhere in the notebook
    for i, c in enumerate(cells):
        if c is None:
            continue
        n_env = c.count("BIOHUB_ILP_DIVISION_WEIGHT")
        want = {0: 1, 2: 1}.get(i, 0)
        if n_env != want:
            raise SystemExit("cell %d mentions BIOHUB_ILP_DIVISION_WEIGHT %d times (want %d)" % (i, n_env, want))
        n_glob = c.count("ILP_DIVISION_WEIGHT") - n_env
        want_g = {2: 2, 4: 1, 7: 1}.get(i, 0)
        if n_glob != want_g:
            raise SystemExit("cell %d uses the ILP_DIVISION_WEIGHT global %d times (want %d)" % (i, n_glob, want_g))
        if i != 0 and ("division_weight=" in c or "division-weight=" in c):
            raise SystemExit("cell %d sets a division weight by keyword; not a known site" % i)
    for i, anchors in SITES.items():
        for a in anchors:
            if cells[i].count(a) != 1:
                raise SystemExit("downstream site in cell %d matched %d times: %r" % (i, cells[i].count(a), a))
    for bad in ("ARM_ILPDIV", "ILPDIV=", "t65b20d04"):
        if any(bad in (c or "") for c in cells):
            raise SystemExit("base unexpectedly carries %r" % bad)
    if c0.count("1.2") != 1:
        raise SystemExit("cell 0 carries %d '1.2' literals (want exactly the env one)" % c0.count("1.2"))
    xenv_new = XENV_FMT % tag
    c0 = c0.replace(ENV_OLD, ENV_NEW + MARK_NEW, 1).replace(XENV_OLD, xenv_new, 1)
    cells[0] = c0
    # cell-by-cell diff vs v_t65b20: only cell 0 changes
    for i, (a, b) in enumerate(zip(orig, cells)):
        if i != 0 and a != b:
            raise SystemExit("cell %d changed unexpectedly" % i)
    ol, nl_ = orig[0].splitlines(), cells[0].splitlines()
    k = ol.index(ENV_OLD.rstrip(NL))
    if nl_[:k] != ol[:k] or nl_[k] != ENV_NEW.rstrip(NL) or nl_[k + 1] != MARK_NEW.rstrip(NL):
        raise SystemExit("cell 0 env / marker rewrite is not in place")
    tail_o, tail_n = ol[k + 1:], nl_[k + 2:]
    dt = [(x, y) for x, y in zip(tail_o, tail_n) if x != y]
    if len(tail_o) != len(tail_n) or dt != [(XENV_OLD, xenv_new)]:
        raise SystemExit("cell 0 differs from t65b20's by more than env + marker + XENV: %r" % dt)
    for bad in ('"1.2"', "tag=t65b20 ", "ILPDIV=1.2"):
        if bad in cells[0]:
            raise SystemExit("a stale value %r survived in cell 0" % bad)
    if "1.2" in cells[0]:
        raise SystemExit("a stale 1.2 literal survived in cell 0")
    for a in (ENV_NEW, MARK_NEW, xenv_new):
        if cells[0].count(a) != 1:
            raise SystemExit("%r is not present exactly once in cell 0" % a)
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
    # re-read and report the diff vs the base, cell by cell
    _, built = cells_of(dest / "kernel.ipynb")
    changed = [i for i, (a, b) in enumerate(zip(orig, built)) if a != b]
    if len(built) != len(orig) or changed != [0] or built[0] != cells[0]:
        raise SystemExit("re-read: cells changed vs v_t65b20 = %r (expected [0])" % changed)
    print("built", dest, "| base v_t65b20 (md5 %s) | ILP division weight 1.2 -> 0.4" % BASE_MD5)
    print("cells changed vs v_t65b20:", changed, "(cell 0 only)")
    import difflib
    for line in difflib.unified_diff(orig[0].splitlines(), built[0].splitlines(), "v_t65b20:cell0", dest.name + ":cell0",
                                     n=0, lineterm=""):
        print("  " + repr(line) if line.startswith(("-", "+")) and line.rstrip() != line else "  " + line)
    print("kernel.ipynb md5", hashlib.md5((dest / "kernel.ipynb").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
