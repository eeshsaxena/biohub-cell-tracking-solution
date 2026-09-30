#!/usr/bin/env python3
r"""Gate entry for ourvzlb25 (scratch_kernels/build_ourvzlb25.py) = ourvzl (board 0.953, 56572442: our linker stack on
the PUBLIC V1284 coordinate head for y/x + our sub-voxel z fed to the edge model) with t65b25's linker settings:
motion-relink TIGHT 6.0 -> 6.5 um and learned-edge BONUS 1.6 -> 2.5. Run from the project root: it backs up ops/gate.py
(gate.py.bak_ourvzlb25), patches it, self-tests, and restores the backup if any self-test fails.
Dry run: OURVZLB25_GATE=<copy of gate.py> python ops/add_ourvzlb25_gate.py

ourvzlb25 must prove on the visible run (4 movies):
  * need['ourvzl'] (read out of gate.py with ast) with its linker markers rewritten: 'ARM_STK3B learned_bonus=2.5'
    (was 1.6), 'ARM_T65H tight_um=6.5' (was ARM_T60H 6.0); STK3V 0.25 and every V1284 / z-to-arr / per-movie
    SV_ARM_HSG200 + ARM_SV_Z_TO_ARR pin unchanged (the linker acts after detection, so the coordinate prints are
    bit-identical to ourvzl's);
  * ADDED (ourvzl's entry pins no config echoes): the cell-2 CONFIG_DISPLAY receipts
    "motion_relink_learned_bonus": 2.5, "motion_relink_tight_um": 6.5, "motion_relink_velocity_weight": 0.25
    (read out of the live globals after float(), i.e. proof the knobs reached the linker);
  * the cell-0 identity line ARM_XENV tag=ourvzlb25 TIGHT=6.5 BONUS=2.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr
    V1284_AXES=yx (replaces ourvzl's XENV line, keeping its body fields);
  * sv_mark SV_ARM_HSG200 (>= 4 lines before 'Prediction completed'). The tag goes INSIDE the sv_mark dict literal:
    the old `sv_mark["ourvzl"] = ...` line runs AFTER sv_tags is computed, so ourvzl's own >= 4 check never ran;
  * FINAL within 15% of REF (the V1284 body sits at -9.1% on 44b6_0b24845f, same window as ourvzl);
  * forbidden: everything forbid['ourvzl'] forbids (resolved with ast from forbid['ourvz'] + its own list) PLUS any
    bonus marker/echo other than 2.5 (1.6 = ourvzl, 2.0 = t65b20 wearing the name), any tight marker/echo other than
    6.5 / an ARM_T60H line, a foreign ARM_XENV tag (incl. ourvzl's), foreign ARM_ markers (allowed: STK3V STK3B T65H
    XENV SV_ZONLY SV_Z_TO_ARR V1284_YX = exactly ourvzl's set with T60H -> T65H), foreign SV_ARM_ markers,
    GDIV_DS / SUBVOXEL_ACTIVE / strict-linear line-fit.
Self-tests: the ourvzl and t65b25 (and t65b20) logs must FAIL as ourvzlb25; ourvzl / t65b25 / t65b20 / t6stk3 / t6r70 /
t65s3 (+ xpubz, t65b25r70 when their logs exist) still PASS as themselves; a SYNTHETIC ourvzlb25 log (ourvzl's log with
the five cell-0/cell-2 lines rewritten) must PASS, and mutants of it must FAIL: SV lines pushed after 'Prediction
completed' (proves the sv_mark check now runs), a 1.6 bonus echo, an ARM_T60H line, ourvzl's XENV line.
"""
import ast
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("OURVZLB25_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("OURVZLB25_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "ourvzlb25"
SRC = "ourvzl"
OLD_BONUS = r"ARM_STK3B learned_bonus=1\.6"
OLD_TIGHT = r"ARM_T60H tight_um=6\.0"
OLD_XENV = r"ARM_XENV tag=ourvzl V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
VEL = r"ARM_STK3V velocity_weight=0\.25"
NEW_BONUS = r"ARM_STK3B learned_bonus=2\.5"
NEW_TIGHT = r"ARM_T65H tight_um=6\.5"
XENV = r"ARM_XENV tag=ourvzlb25 TIGHT=6\.5 BONUS=2\.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
ECHO_VEL = r'"motion_relink_velocity_weight": 0\.25(?!\d)'
ECHO_BONUS = r'"motion_relink_learned_bonus": 2\.5(?!\d)'
ECHO_TIGHT = r'"motion_relink_tight_um": 6\.5(?!\d)'
EXTRA_FORBID = [r"ARM_STK3B learned_bonus=(?!2\.5(?!\d))", r'"motion_relink_learned_bonus": (?!2\.5(?!\d))',
                r"ARM_T60H", r"ARM_T\d+H tight_um=(?!6\.5(?!\d))", r'"motion_relink_tight_um": (?!6\.5(?!\d))',
                r'"motion_relink_velocity_weight": (?!0\.25(?!\d))',
                r"ARM_XENV tag=(?!ourvzlb25 )",
                r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX)\b)[A-Z0-9]+",
                r"\bSV_ARM_(?!HSG200\b)[A-Z0-9]+", "GDIV_DS", "SUBVOXEL_ACTIVE",
                r'"output_linefit_strict_linear": true']
# synthetic ourvzlb25 log = ourvzl's log with exactly the lines the build changes rewritten
SYN = [("ARM_STK3B learned_bonus=1.6", "ARM_STK3B learned_bonus=2.5"),
       ("ARM_T60H tight_um=6.0", "ARM_T65H tight_um=6.5"),
       ("ARM_XENV tag=ourvzl V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx",
        "ARM_XENV tag=ourvzlb25 TIGHT=6.5 BONUS=2.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"),
       ('"motion_relink_learned_bonus": 1.6', '"motion_relink_learned_bonus": 2.5'),
       ('"motion_relink_tight_um": 6.0', '"motion_relink_tight_um": 6.5')]


def need_of(src, key):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "need":
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return ast.literal_eval(v)
    raise SystemExit("no need entry for " + key)


def _forbid_key(target):
    if isinstance(target, ast.Subscript) and getattr(target.value, "id", None) == "forbid":
        s = target.slice
        if isinstance(s, ast.Constant) and isinstance(s.value, str):
            return s.value
    return None


def forbid_of(src, key):
    """Resolve forbid[key] from the module's top-level statements (literal lists, forbid[x] refs, '+')."""
    body = ast.parse(src).body
    assigns = {}
    for node in body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            k = _forbid_key(node.targets[0])
            if k is not None:
                assigns.setdefault(k, []).append(node)
        # a top-level loop that rewrites forbid[_t] must not touch the keys we resolve
        if isinstance(node, ast.For) and isinstance(node.iter, (ast.Tuple, ast.List)):
            names = {e.value for e in node.iter.elts if isinstance(e, ast.Constant)}
            if names & {"ourvz", "ourvzl"}:
                raise SystemExit("a top-level loop rewrites forbid for %r; refusing to resolve by ast" % (names & {"ourvz", "ourvzl"}))

    def resolve(expr):
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
            return resolve(expr.left) + resolve(expr.right)
        k = _forbid_key(expr)
        if k is not None:
            return resolve_key(k)
        return list(ast.literal_eval(expr))

    def resolve_key(k):
        nodes = assigns.get(k, [])
        if len(nodes) != 1:
            raise SystemExit("forbid[%r] assigned %d times at top level (expected exactly 1)" % (k, len(nodes)))
        return resolve(nodes[0].value)

    return resolve_key(key)


def gate_file(lg, tag):
    out = subprocess.run([sys.executable, str(GATE), str(lg), tag], capture_output=True, text=True).stdout.strip()
    return out.splitlines()[-1] if out else "NO OUTPUT"


def gate(logdir, tag):
    return gate_file(next((ROOT / "data" / logdir).glob("*.log")), tag)


def log_text(p):
    import json
    raw = p.read_text(encoding="utf-8")
    try:
        return "".join(e.get("data", "") for e in json.loads(raw))
    except Exception:
        return raw


def main():
    t = GATE.read_text(encoding="utf-8")
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    base = list(need_of(t, SRC))
    for p in (OLD_BONUS, OLD_TIGHT, OLD_XENV, VEL):
        if base.count(p) != 1:
            raise SystemExit("need['ourvzl'] does not carry exactly one %r: %r" % (p, base))
    if any("motion_relink" in p for p in base):
        raise SystemExit("need['ourvzl'] unexpectedly pins config echoes; re-derive instead of adding: %r" % base)
    pats = []
    for p in base:
        if p == OLD_BONUS:
            pats += [NEW_BONUS, ECHO_BONUS]
        elif p == OLD_TIGHT:
            pats += [NEW_TIGHT, ECHO_TIGHT]
        elif p == VEL:
            pats += [VEL, ECHO_VEL]
        elif p == OLD_XENV:
            pats.append(XENV)
        else:
            pats.append(p)
    for stale in (r"1\.6", r"6\.0", "T60H", "tag=ourvzl "):
        if any(stale in p for p in pats):
            raise SystemExit("a stale pattern %r survived: %r" % (stale, pats))
    for p in (NEW_BONUS, ECHO_BONUS, NEW_TIGHT, ECHO_TIGHT, VEL, ECHO_VEL, XENV):
        if pats.count(p) != 1:
            raise SystemExit("pattern %r not present exactly once: %r" % (p, pats))
    if len(pats) != len(base) + 3:
        raise SystemExit("expected ourvzl's %d patterns + 3 echoes, got %d" % (len(base), len(pats)))
    fz = forbid_of(t, SRC)
    if r"Traceback \(most recent call last\)" not in fz or "ARM_LCEFR" not in fz or len(fz) < 15:
        raise SystemExit("forbid['ourvzl'] resolved to something unexpected: %r" % fz)
    forbid = fz + [p for p in EXTRA_FORBID if p not in fz]
    comment = ("        # --- ourvzlb25: ourvzl (V1284 y/x head + sub-voxel z to the edge model, board 0.953) with t65b25's linker\n"
               "        # settings: relink tight 6.0 -> 6.5, learned bonus 1.6 -> 2.5 (build_ourvzlb25.py; ops/add_ourvzlb25_gate.py).\n"
               "        # = need['ourvzl'] with STK3B/T60H rewritten to 2.5/T65H 6.5 + the three cell-2 linker echoes + this XENV.\n"
               "        # The coordinate pins stay EXACT (the linker acts after detection). sv_mark is in the dict literal.\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": '"ourvzl": 0.15',
               "svtags": 'sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    t2 = t.replace(anchors["need"], entry + anchors["need"], 1)
    t2 = t2.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t2 = t2.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t2 = t2.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % TAG, 1)
    # the sv_mark key must sit in the dict literal, i.e. BEFORE sv_tags is computed (the ourvzl bug)
    lit = [n for n in ast.parse(t2).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "sv_mark"
           and isinstance(n.value, ast.Dict)]
    if len(lit) != 1 or ast.literal_eval(lit[0].value).get(TAG) != "SV_ARM_HSG200" \
            or not t2.index("sv_mark = {") < t2.index('"%s": "SV_ARM_HSG200"' % TAG) < t2.index(anchors["svtags"]):
        raise SystemExit("sv_mark entry for %s is not inside the dict literal before sv_tags is computed" % TAG)
    if forbid_of(t2, TAG) != forbid or need_of(t2, TAG) != pats:
        raise SystemExit("re-parse of the patched gate does not return the new need/forbid entries")
    ast.parse(t2)
    compile(t2, str(GATE), "exec")
    if GATE.read_text(encoding="utf-8") != t:
        raise SystemExit("gate.py changed while patching (another installer?); nothing written")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(t, encoding="utf-8")
    GATE.write_text(t2, encoding="utf-8")
    res = {"neg_ourvzl_as_ourvzlb25": gate("out_ourvzl", TAG),
           "neg_t65b25_as_ourvzlb25": gate("out_t65b25", TAG),
           "neg_t65b20_as_ourvzlb25": gate("out_t65b20", TAG),
           "pos_ourvzl": gate("out_ourvzl", "ourvzl"), "pos_t65b25": gate("out_t65b25", "t65b25"),
           "pos_t65b20": gate("out_t65b20", "t65b20"), "pos_t6stk3": gate("out_t6stk3", "t6stk3"),
           "pos_t6r70": gate("out_t6r70", "t6r70"), "pos_t65s3": gate("out_t65s3", "t65s3")}
    for opt in ("xpubz", "t65b25r70"):
        if list((ROOT / "data").glob("out_%s/*.log" % opt)):
            res["pos_" + opt] = gate("out_" + opt, opt)
    # synthetic positive + mutants built from ourvzl's own log
    src = log_text(next((ROOT / "data" / "out_ourvzl").glob("*.log")))
    syn = src
    for a, b in SYN:
        if syn.count(a) != 1:
            raise SystemExit("synthetic: %r occurs %d times in the ourvzl log" % (a, syn.count(a)))
        syn = syn.replace(a, b)
    pe = syn.find("Prediction completed")
    mutants = {"neg_syn_sv_after_pred": "Prediction completed (mutant: SV lines now after it)\n" + syn,
               "neg_syn_bonus16_echo": syn[:pe] + '"motion_relink_learned_bonus": 1.6,\n' + syn[pe:],
               "neg_syn_t60h_line": syn[:pe] + "ARM_T60H tight_um=6.0\n" + syn[pe:],
               "neg_syn_ourvzl_xenv": syn[:pe] + SYN[2][0] + "\n" + syn[pe:]}
    with tempfile.TemporaryDirectory() as td:
        for name, body in [("pos_syn_ourvzlb25", syn)] + list(mutants.items()):
            p = pathlib.Path(td) / (name + ".log")
            p.write_text(body, encoding="utf-8")
            res[name] = gate_file(p, TAG)
    for k, v in res.items():
        print(k, "->", v[:500])
    ok = all("GATE_FAIL" in v for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_"))
    # the SV-after-pred mutant must fail on the sv_mark count, not on something else
    if "only 0 SV_ARM_HSG200 lines before 'Prediction completed'" not in res["neg_syn_sv_after_pred"]:
        ok = False
        print("sv_mark check did NOT fire for", TAG)
    if not ok:
        if GATE.read_text(encoding="utf-8") == t2:
            GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
            raise SystemExit("self-test failed; gate.py restored from " + bak.name)
        raise SystemExit("self-test failed AND gate.py was modified by someone else meanwhile; NOT restored, check by hand")
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
