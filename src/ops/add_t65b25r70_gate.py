#!/usr/bin/env python3
r"""Gate entry for t65b25r70 (scratch_kernels/build_t65b25r70.py) = t6r70 (t6stk3 + raw-ILP override "rawlink" at
min_prob 0.70) with t65b25's linker settings (motion-relink TIGHT 6.5, learned bonus 2.5). Run from the project root:
it backs up ops/gate.py (gate.py.bak_t65b25r70), patches it, self-tests, and restores the backup if any self-test fails.
Dry run: T65B25R70_GATE=<copy of gate.py> python ops/add_t65b25r70_gate.py

t65b25r70 must prove on the visible run (4 movies):
  * need['t65b25'] (read out of gate.py with ast) minus its ARM_XENV line: STK3V, STK3B 2.5 + cell-2 echo 2.5,
    T65H 6.5 + cell-2 echo 6.5, LCEFR runtime counters, base line-fit echoes;
  * need['t6r70']'s rawlink patterns (read with ast): the cell-2 ARM_RAWLINK min_prob=0.7 enabled=True line, the
    "rawlink_min_prob": 0.7 echo and the four per-movie ARM_RAWLINK lines with accepted >= 1;
  * the cell-0 identity line ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept;
  * t6r70's rawlink structural checks: the tag joins RL_TAGS (per-movie line after FINAL, degree <= 1/2, division
    count unchanged, edge arithmetic anchor + accepted - replaced == final, change fraction window, total-accepted
    window of the t6stk3 body) and the orphan cap (<= 50 per movie, <= 150 total new_isolated);
  * a per-movie cross-check modelled on t6r70T15's: cell-10 written nodes/edges/divisions == (FINAL nodes,
    ARM_RAWLINK final=, safe divisions added) and run_stats.csv agrees (smoothed + skipped == nodes). No exact
    FINAL pins: the linker change moves topology (node-neutral, ~+0.008%);
  * sv_mark SV_ARM_HSG200 (>= 4 lines before 'Prediction completed'); FINAL within 15% of REF;
  * forbidden: any 1.6 / 2.0 bonus marker or echo, a 6.0 relink echo / ARM_T60H marker, rawlink disabled or at a
    different threshold, a foreign ARM_XENV tag, foreign ARM_ / SV_ARM_ markers, tracebacks / IndentationError.
Self-tests: the t6r70 and t65b25 logs must FAIL as t65b25r70; t6r70 / t65b25 / t65b20 / t65s3 / t6stk3 / ourvzl logs
still PASS as themselves.
"""
import ast
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(os.environ.get("T65B25R70_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("T65B25R70_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "t65b25r70"
SIB_XENV = r"ARM_XENV tag=t65b25 TIGHT=6\.5 BONUS=2\.50 LCEFR=kept"
XENV = r"ARM_XENV tag=t65b25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 LCEFR=kept"
LINKER_T6R70 = [r"ARM_STK3B learned_bonus=1\.6", r'"motion_relink_learned_bonus": 1\.6(?!\d)',
                r"ARM_T60H tight_um=6\.0", r'"motion_relink_tight_um": 6\.0(?!\d)']
LINKER_NEW = [r"ARM_STK3B learned_bonus=2\.5", r'"motion_relink_learned_bonus": 2\.5(?!\d)',
              r"ARM_T65H tight_um=6\.5", r'"motion_relink_tight_um": 6\.5(?!\d)']


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def gate(logdir, tag):
    lg = str(next((ROOT / "data" / logdir).glob("*.log")))
    out = subprocess.run([sys.executable, str(GATE), lg, tag], capture_output=True, text=True).stdout.strip()
    return out.splitlines()[-1] if out else "NO OUTPUT"


def main():
    t = GATE.read_text(encoding="utf-8")
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    b25 = list(need_of(t, "t65b25"))
    r70 = list(need_of(t, "t6r70"))
    if b25.count(SIB_XENV) != 1:
        raise SystemExit("need['t65b25'] does not carry exactly one XENV line: %r" % b25)
    rl = [p for p in r70 if "RAWLINK" in p or "rawlink" in p]
    if len(rl) != 6:
        raise SystemExit("need['t6r70'] rawlink patterns != 6: %r" % rl)
    # t6r70's non-rawlink patterns, with its 4 linker patterns swapped to 6.5/2.5, must equal t65b25's minus XENV:
    # i.e. the two arms share every other marker and the union below is exactly "t6r70 with t65b25's linker"
    core_b25 = [p for p in b25 if p != SIB_XENV]
    for o in LINKER_T6R70:
        if r70.count(o) != 1:
            raise SystemExit("need['t6r70'] lacks linker pattern %r" % o)
    core_r70 = [LINKER_NEW[LINKER_T6R70.index(p)] if p in LINKER_T6R70 else p for p in r70 if p not in rl]
    if sorted(core_r70) != sorted(core_b25):
        raise SystemExit("t6r70 (linker swapped) and t65b25 disagree on the shared markers:\n%r\n%r" % (core_r70, core_b25))
    pats = core_b25 + rl + [XENV]
    for stale in (r"2\.0", r"1\.6", r"6\.0", "T60H", "tag=t65b25 ", "tag=t6r70"):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    for p in LINKER_NEW + [XENV]:
        if pats.count(p) != 1:
            raise SystemExit("pattern %r not present exactly once: %r" % (p, pats))
    comment = ("        # --- t65b25r70: t6r70 (t6stk3 + raw-ILP override at prob >= 0.70) with t65b25's linker settings\n"
               "        # (relink tight 6.5, learned bonus 2.5). Stack of the two changes that each beat their base on the board.\n"
               "        # = need['t65b25'] minus its XENV + need['t6r70']'s six rawlink patterns + this arm's XENV\n"
               "        # (build_t65b25r70.py; ops/add_t65b25r70_gate.py). Topology moves with the linker, so no T6_BODY pins;\n"
               "        # RL_TAGS + orphan cap + the written-count cross-check below carry the rawlink bookkeeping.\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    forbid = [r"ARM_STK3B learned_bonus=2\.0", r"ARM_STK3B learned_bonus=1\.6",
              r'"motion_relink_learned_bonus": (2\.0|1\.6)', r"ARM_XENV tag=(?!t65b25r70 )",
              r"Traceback \(most recent call last\)", "IndentationError",
              r"\bARM_(?!(?:STK3V|STK3B|T65H|LCEFR|XENV|RAWLINK)\b)[A-Z0-9]+", "ARM_FLOWFIX",
              r"ARM_RAWLINK min_prob=\S+ enabled=False", r"ARM_RAWLINK (?:\[\w+\] )?min_prob=(?!0\.7(?!\d))",
              r'"rawlink_min_prob": (?!0\.7(?!\d))',
              r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", "GDIV_DS", "SUBVOXEL_ACTIVE",
              r'"output_linefit_strict_linear": true', r'"motion_relink_tight_um": 6\.0(?!\d)',
              r"ARM_T60H tight_um=6\.0"]
    xcheck = (
        "# --- t65b25r70 (ops/add_t65b25r70_gate.py): t6r70 + t65b25's linker (tight 6.5, bonus 2.5). The linker change moves\n"
        "# topology, so the T6_BODY exact pins do NOT apply; as for t6r70T15, the override's bookkeeping is cross-checked per\n"
        "# movie against this run's own prints: cell-10 written nodes/edges/divisions == (FINAL nodes, ARM_RAWLINK final=,\n"
        "# safe divisions added), run_stats agrees, line-fit smoothed + skipped == nodes.\n"
        "if \"t65b25r70\" in tags:\n"
        "    import csv, os\n"
        "    _xfin, _xsd, _xdv, _xrlf = {}, {}, {}, {}\n"
        "    for d, n_, e_ in re.findall(r\"\\[(\\w+)\\] FINAL: (\\d+) nodes, (\\d+) edges\", txt):\n"
        "        _xfin.setdefault(d, (int(n_), int(e_)))\n"
        "    for d, a_ in re.findall(r\"\\[(\\w+)\\] after safe-division repair: \\d+ nodes, \\d+ edges \\([^)]*?\\badded=(\\d+)\", txt):\n"
        "        _xsd.setdefault(d, int(a_))\n"
        "    for d, n_, e_, v_ in re.findall(r\"(?m)^\\s+(\\w+): nodes=(\\d+) edges=(\\d+) divisions=(\\d+)\\s*$\", txt):\n"
        "        _xdv.setdefault(d, (int(n_), int(e_), int(v_)))\n"
        "    for d, f_ in re.findall(r\"ARM_RAWLINK \\[(\\w+)\\] .*? final=(\\d+) \", txt):\n"
        "        _xrlf.setdefault(d, int(f_))\n"
        "    _xrsp = os.path.join(os.path.dirname(os.path.abspath(log)), \"run_stats.csv\")\n"
        "    _xrs = None\n"
        "    if os.path.isfile(_xrsp):\n"
        "        with open(_xrsp, newline=\"\", encoding=\"utf-8\") as fh:\n"
        "            _xrs = {r.get(\"dataset\"): r for r in csv.DictReader(fh)}\n"
        "    else:\n"
        "        fails.append(\"t65b25r70: no run_stats.csv beside the log, so the written counts and line-fit counters are unproven\")\n"
        "    for d in sorted(REF):\n"
        "        if d not in _xfin or d not in _xsd or d not in _xrlf:\n"
        "            fails.append(f\"t65b25r70 {d}: missing FINAL / safe-division / ARM_RAWLINK final= line\")\n"
        "            continue\n"
        "        _xwant = (_xfin[d][0], _xrlf[d], _xsd[d])\n"
        "        if _xdv.get(d) != _xwant:\n"
        "            fails.append(f\"t65b25r70 {d} written nodes/edges/divisions {_xdv.get(d)} != (FINAL nodes, rawlink final=, \"\n"
        "                         f\"safe divisions) {_xwant}\")\n"
        "        if _xrs is not None:\n"
        "            _xr = _xrs.get(d) or {}\n"
        "            try:\n"
        "                _xgot = tuple(int(float(_xr[k])) for k in (\"nodes\", \"edges\", \"safe_divisions_added\",\n"
        "                                                           \"linefit_smoothed_nodes\", \"linefit_skipped_nodes\"))\n"
        "            except (KeyError, TypeError, ValueError):\n"
        "                _xgot = None\n"
        "            if _xgot is None or _xgot[:3] != _xwant or _xgot[3] + _xgot[4] != _xwant[0]:\n"
        "                fails.append(f\"t65b25r70 {d} run_stats (nodes, edges, safe_divisions_added, smoothed, skipped) {_xgot} \"\n"
        "                             f\"inconsistent with {_xwant} (smoothed + skipped must equal nodes)\")\n")
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": '"ourvzl": 0.15',
               "rltags": 'RL_TAGS = {"rawlink70", "t6r70", "t6rlf", "t6r70T15"}',
               "orphan": '    if {"t6r70", "t6rlf", "t6r70T15"} & set(tags):\n',
               "xcheck": 'sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    if '"t65b25": "SV_ARM_HSG200"' not in t or '"t6r70": "SV_ARM_HSG200"' not in t:
        raise SystemExit("t65b25 / t6r70 not in sv_mark; refusing to guess the body marker")
    t = t.replace(anchors["need"], entry + anchors["need"], 1)
    t = t.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t = t.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t = t.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % TAG, 1)
    t = t.replace(anchors["rltags"], 'RL_TAGS = {"rawlink70", "t6r70", "t6rlf", "t6r70T15", "%s"}' % TAG, 1)
    t = t.replace(anchors["orphan"], '    if {"t6r70", "t6rlf", "t6r70T15", "%s"} & set(tags):\n' % TAG, 1)
    t = t.replace(anchors["xcheck"], xcheck + anchors["xcheck"], 1)
    ast.parse(t)
    compile(t, str(GATE), "exec")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(GATE.read_text(encoding="utf-8"), encoding="utf-8")
    GATE.write_text(t, encoding="utf-8")
    res = {"neg_t6r70_as_t65b25r70": gate("out_t6r70", TAG),
           "neg_t65b25_as_t65b25r70": gate("out_t65b25", TAG),
           "pos_t6r70": gate("out_t6r70", "t6r70"), "pos_t65b25": gate("out_t65b25", "t65b25"),
           "pos_t65b20": gate("out_t65b20", "t65b20"), "pos_t65s3": gate("out_t65s3", "t65s3"),
           "pos_t6stk3": gate("out_t6stk3", "t6stk3"), "pos_ourvzl": gate("out_ourvzl", "ourvzl")}
    if list((ROOT / "data").glob("out_%s/*.log" % TAG)):
        res["pos_" + TAG] = gate("out_" + TAG, TAG)
    for k, v in res.items():
        print(k, "->", v[:600])
    ok = all("GATE_FAIL" in v for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_") and k != "pos_" + TAG)
    if not ok:
        GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
        raise SystemExit("self-test failed; gate.py restored from " + bak.name)
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
