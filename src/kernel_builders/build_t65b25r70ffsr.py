#!/usr/bin/env python3
"""t65b25r70ffsr = t65b25r70 (team top entry 0.954: t6stk3 body + relink tight 6.5 + learned bonus 2.5 + raw-ILP override
"rawlink" 0.70) with BOTH stacked additions that went out separately on 09-29:
  * t65b25r70ff: the IMGFLOW write-time repair (cell 0 FLOWFIX env lines + cell 5 helper / call / run_stats insertion,
    after the rawlink override and before the writer loop), as built by build_t65b25r70ff.py;
  * t65b25r70sr: the short-track rescue armed unconditionally (cell 0 line
    os.environ["BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC"] = "0.0"), as built by build_t65b25r70sr.py.
The two touch disjoint lines/stages: the rescue runs inside filter_output_graph (before FINAL, so before the override
and the repair); the repair acts on the override's output. Pipeline order per movie: filter_output_graph (rescue) ->
FINAL -> rawlink_override -> flow_repair -> writer.

usage: python scratch_kernels/build_t65b25r70ffsr.py [tag]        (default tag t65b25r70ffsr)

HOW: start from v_t65b25r70ff; in cell 0 drop its ARM_XENV line and append sr's env line (copied verbatim out of
v_t65b25r70sr) + this arm's ARM_XENV line. Nothing else changes.
Checks (all hard stops): md5 pins (v_t65b25r70, v_t65b25r70ff, v_t65b25r70sr); ff's change vs t65b25r70 = cells
[0, 5] with cell 0 = base[:-1] + the 4 FLOWFIX env lines + its XENV; sr's change vs t65b25r70 = cell [0] only with
cell 0 = base[:-1] + [env line, its XENV]; every anchor exactly once; built cell diff vs v_t65b25r70ff = cell 0 only,
= its lines minus XENV + [sr env line, this XENV]; built cell diff vs v_t65b25r70sr = cells [0, 5], cell 0 = its lines
minus XENV with the 4 FLOWFIX env lines inserted before the sr env line + this XENV, cell 5 minus the three FLOWFIX
insertions == sr's cell 5; stage order in the writer (filter_output_graph < rawlink_override < flow_repair < node
writer loop); compile every cell; metadata copied from v_t65b25r70 with only id/title changed.
Markers: ARM_XENV tag=<tag> TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 ENDS=1
DEADLINE_S=34200 SR=armed (cell 0); cell-2 echo "short_track_rescue_trigger_removed_frac": 0.0; ARM_FLOWFIX enabled=
and per-movie status=ok lines; run_stats short_track_rescue_* and flowfix_* columns.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_t6r70ff import HELPER, CALL, NL  # noqa: E402  (the three cell-5 FLOWFIX insertions)

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t65b25r70"
BASE_MD5 = "60722ec9a2f277733656ba6bf5b559af"  # v_t65b25r70/kernel.ipynb (submitted 56640601, public 0.954)
FF = SK / "v_t65b25r70ff"
FF_MD5 = "e58610d94202109c95096c6d96c2fc93"  # v_t65b25r70ff/kernel.ipynb (submitted 56659166)
SR = SK / "v_t65b25r70sr"
SR_MD5 = "b098a1503b51c5726fc907cdee0de3eb"  # v_t65b25r70sr/kernel.ipynb (submitted 56659169)
BASE_XENV = 'print("ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept", flush=True)'
FF_XENV = ('print("ARM_XENV tag=t65b25r70ff TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 '
           'MIN_DET=5 ENDS=1 DEADLINE_S=34200", flush=True)')
SR_XENV = 'print("ARM_XENV tag=t65b25r70sr TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 SR=armed", flush=True)'
XENV_FMT = ('print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 FLOWFIX=1 TF=5.0 KEEP=3.5 GATE=4.5 MIN_DET=5 '
            'ENDS=1 DEADLINE_S=34200 SR=armed", flush=True)')
FF_ENV = ["import time as _ff_time0",
          "os.environ.setdefault('BIOHUB_FLOWFIX_T0', repr(_ff_time0.time()))  # ARM_FLOWFIX deadline clock",
          "os.environ['BIOHUB_FLOWFIX'] = '1'",
          "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'"]
SR_ENV = 'os.environ["BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC"] = "0.0"'
READ = ('SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC = float(os.environ.get("BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC", '
        '"0.10"))')
RESCUE_BRANCH = "if removed_frac >= SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC:"
FF_STATS_LINE = "                **flowfix_stats,\n"
FF_CALL_LINE = "edges, flowfix_stats = flow_repair("


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def lines_of(c):
    return c.rstrip(NL).split(NL)


def once(hay, needle, what):
    if hay.count(needle) != 1:
        raise SystemExit("anchor %s matched %d times" % (what, hay.count(needle)))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "t65b25r70ffsr"
    for d, m in ((BASE, BASE_MD5), (FF, FF_MD5), (SR, SR_MD5)):
        if md5(d / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (d.name, m))
    _, base = cells_of(BASE / "kernel.ipynb")
    nb, ff = cells_of(FF / "kernel.ipynb")
    _, sr = cells_of(SR / "kernel.ipynb")
    if not len(base) == len(ff) == len(sr):
        raise SystemExit("cell counts differ: base %d ff %d sr %d" % (len(base), len(ff), len(sr)))
    # ---- re-derive both changes against t65b25r70
    ff_changed = [i for i, (a, b) in enumerate(zip(base, ff)) if a != b]
    sr_changed = [i for i, (a, b) in enumerate(zip(base, sr)) if a != b]
    if ff_changed != [0, 5]:
        raise SystemExit("v_t65b25r70ff differs from v_t65b25r70 in cells %r (expected [0, 5])" % ff_changed)
    if sr_changed != [0]:
        raise SystemExit("v_t65b25r70sr differs from v_t65b25r70 in cells %r (expected [0])" % sr_changed)
    bl, fl, sl = lines_of(base[0]), lines_of(ff[0]), lines_of(sr[0])
    if bl[-1] != BASE_XENV or base[0].count("ARM_XENV") != 1:
        raise SystemExit("t65b25r70 cell 0 does not end with its one ARM_XENV line")
    if fl != bl[:-1] + FF_ENV + [FF_XENV] or ff[0].count("ARM_XENV") != 1:
        raise SystemExit("v_t65b25r70ff cell 0 != base[:-1] + 4 FLOWFIX env lines + its XENV")
    if sl != bl[:-1] + [SR_ENV, SR_XENV] or sr[0].count("ARM_XENV") != 1:
        raise SystemExit("v_t65b25r70sr cell 0 != base[:-1] + [trigger env line, its XENV]")
    sr_env = sl[-2]  # verbatim out of v_t65b25r70sr
    if sr_env != SR_ENV:
        raise SystemExit("sr env line mismatch")
    # ---- exactly-once anchors / disjointness
    if ff[5].replace(HELPER, "").replace(CALL + "\n", "").replace(FF_STATS_LINE, "") != sr[5]:
        raise SystemExit("ff cell 5 minus the three FLOWFIX insertions != sr cell 5 (== base cell 5)")
    for what, hay, needle in (("ff c5 helper", ff[5], HELPER), ("ff c5 call", ff[5], CALL), ("ff c5 stats", ff[5], FF_STATS_LINE),
                              ("ff c5 call line", ff[5], FF_CALL_LINE), ("c2 trigger read", ff[2], READ),
                              ("c5 rescue branch", ff[5], RESCUE_BRANCH), ("ff c0 FLOWFIX on", ff[0], "os.environ['BIOHUB_FLOWFIX'] = '1'"),
                              ("sr c0 env", sr[0], SR_ENV)):
        once(hay, needle, what)
    if ff[2].count("BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC") != 1:
        raise SystemExit("cell 2 does not read BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC exactly once")
    if any("BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC" in (c or "") for i, c in enumerate(ff) if i != 2):
        raise SystemExit("v_t65b25r70ff already sets the rescue trigger outside cell 2")
    for bad in ("ARM_FLOWFIX", "BIOHUB_FLOWFIX", "flow_repair", "flowfix_stats"):
        if any(bad in (c or "") for c in sr):
            raise SystemExit("v_t65b25r70sr already carries %s" % bad)
    # ---- build: ff's cell 0 minus its XENV + sr's env line + this XENV
    xenv = XENV_FMT % tag
    cells = list(ff)
    cells[0] = NL.join(fl[:-1] + [sr_env, xenv]) + NL
    nl0 = lines_of(cells[0])
    # ---- diff vs v_t65b25r70ff: cell 0 only, = its lines minus XENV + [sr env, XENV]
    d_ff = [i for i, (a, b) in enumerate(zip(ff, cells)) if a != b]
    if d_ff != [0] or nl0[:-2] != fl[:-1] or nl0[-2:] != [SR_ENV, xenv]:
        raise SystemExit("built vs v_t65b25r70ff: cells %r / cell 0 is not ff[:-1] + [sr env, XENV]" % d_ff)
    # ---- diff vs v_t65b25r70sr: cells 0 and 5; cell 0 = sr[:-2] + FLOWFIX env + [sr env, XENV]; cell 5 = sr + 3 inserts
    d_sr = [i for i, (a, b) in enumerate(zip(sr, cells)) if a != b]
    if d_sr != [0, 5]:
        raise SystemExit("built vs v_t65b25r70sr: cells %r changed (expected [0, 5])" % d_sr)
    if nl0 != sl[:-2] + FF_ENV + [SR_ENV, xenv]:
        raise SystemExit("built cell 0 != sr[:-2] + 4 FLOWFIX env lines + [sr env, XENV]")
    if cells[5] != ff[5] or cells[5].replace(HELPER, "").replace(CALL + "\n", "").replace(FF_STATS_LINE, "") != sr[5]:
        raise SystemExit("built cell 5 is not ff's, or minus the FLOWFIX insertions is not sr's")
    for i in range(len(cells)):
        if i not in (0, 5) and not cells[i] == ff[i] == sr[i] == base[i]:
            raise SystemExit("cell %d is not identical across base/ff/sr/built" % i)
    c0 = cells[0]
    for needle in (SR_ENV, "os.environ['BIOHUB_FLOWFIX'] = '1'", "os.environ['BIOHUB_FLOWFIX_DEADLINE_S'] = '34200'",
                   'os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"', "ARM_XENV"):
        once(c0, needle, "built c0 " + needle[:40])
    if sum(c.count("BIOHUB_SHORT_TRACK_RESCUE_TRIGGER_REMOVED_FRAC") for c in cells if c) != 2:
        raise SystemExit("the rescue trigger must appear exactly twice (cell-0 set, cell-2 read)")
    # ---- stage order in the writer: filter (rescue inside) -> FINAL -> rawlink -> flowfix -> node writer loop
    c5 = cells[5]
    w = c5.index("def write_test_submission")
    order = [c5.index(s, w) for s in ("nodes_by_id, edges, filter_stats = filter_output_graph(",
                                      "edges, rawlink_stats, rawlink_actions = rawlink_override(",
                                      FF_CALL_LINE, "for node_id in sorted(nodes_by_id):")]
    if order != sorted(order):
        raise SystemExit("writer stage order is not filter -> rawlink -> flowfix -> write: %r" % order)
    fsc = c5.index("def filter_short_track_components(")
    if not fsc < c5.index(RESCUE_BRANCH) < c5.index("\ndef ", fsc + 10):
        raise SystemExit("the rescue branch is not inside filter_short_track_components")
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
    # ---- re-read the written notebook and report the diffs
    _, built = cells_of(dest / "kernel.ipynb")
    if built != cells:
        raise SystemExit("re-read of the written notebook differs from the built cells")
    ffm = json.loads((FF / "kernel-metadata.json").read_text(encoding="utf-8"))
    for k_ in meta:
        if k_ not in ("id", "title") and meta[k_] != ffm.get(k_):
            raise SystemExit("metadata %s differs from v_t65b25r70ff's" % k_)
    print("built", dest, "| from v_t65b25r70ff (md5 %s) + sr's cell-0 line from v_t65b25r70sr (md5 %s)" % (FF_MD5, SR_MD5))
    print("cells changed vs v_t65b25r70ff:", [i for i, (a, b) in enumerate(zip(ff, built)) if a != b])
    print("  cell 0: -", FF_XENV)
    print("          +", SR_ENV)
    print("          +", xenv)
    print("cells changed vs v_t65b25r70sr:", [i for i, (a, b) in enumerate(zip(sr, built)) if a != b])
    print("  cell 0: -", SR_XENV)
    for l in FF_ENV:
        print("          + (before the sr env line)", l)
    print("          +", xenv)
    print("  cell 5: + ARM_FLOWFIX helper (%d lines), call block (%d lines), **flowfix_stats (ff's cell 5 byte for byte)"
          % (HELPER.count(NL), CALL.count(NL) + 1))
    print("cells changed vs v_t65b25r70:", [i for i, (a, b) in enumerate(zip(base, built)) if a != b])
    print("writer stage offsets filter/rawlink/flowfix/write:", order)
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
