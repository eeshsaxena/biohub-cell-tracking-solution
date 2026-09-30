#!/usr/bin/env python3
r"""Gate entry for mixyx50r70 (scratch_kernels/build_mixyx50r70.py) = t65b25r70's full stack with y/x = 0.5 * V1284 +
0.5 * SV (the V1284 head mounted exactly as ourvzlb25r70 mounts it; z = production SV z-to-arr as in both parents).
Run from the project root: it backs up ops/gate.py (gate.py.bak_mixyx50r70), patches it, self-tests, and restores
the backup if any self-test fails.  Dry run: MIXYX50R70_GATE=<copy of gate.py> python ops/add_mixyx50r70_gate.py

mixyx50r70 must prove on the visible run (4 movies):
  * need['ourvzlb25r70'] (read with ast) minus its ARM_XENV line: linker knobs + echoes (tight 6.5, bonus 2.5,
    velocity 0.25), the V1284 mount / z-to-arr markers, the per-movie SV_ARM_HSG200 + ARM_SV_Z_TO_ARR pins EXACTLY
    (the z-only sub-voxel call is untouched, so z and the z-only SV stats are ourvzlb25r70's bit for bit; the build's
    unit test and scratchpad/wf30/sim_mix.py prove it), and the six rawlink patterns;
  * the mixyx markers: the cell-4 env line `ARM_MIXYX w=0.5 (y/x = 0.5*V1284 + 0.5*SV ...`, the runtime patch line
    (7 predictor + 1 module anchors, w=0.5) and, per test movie, `ARM_MIXYX w=0.5 frames=100 nodes=<the movie's
    detection count> mean_abs_sv_minus_v1284_um y=<non-zero> x=<non-zero> ... final_yx_add=0`;
  * the identity line ARM_XENV tag=mixyx50r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr
    V1284_AXES=yx MIXYX=0.50;
  * exactly as ourvzlb25r70: RL_TAGS (rawlink bookkeeping + accepted window), the orphan cap, the per-movie written
    count cross-check (block generated from the live ourvzlb25r70 block, prefix _ov -> _mx, round-trip checked),
    sv_mark SV_ARM_HSG200 inside the dict literal, FINAL within 15% of REF;
  * forbidden: forbid['ourvzlb25r70'] (resolved with ast) with its XENV forbid now allowing only tag=mixyx50r70 and
    its ARM_ allowlist gaining MIXYX, plus every ARM_MIXYX runtime failure message, any ARM_MIXYX w other than 0.5,
    and final_yx_add != 0.
Self-tests: the ourvzlb25r70 and t65b25r70 logs (both parents) must FAIL as mixyx50r70; t65b25r70 / ourvzlb25r70 /
ourvzlb25 / t65b25 / t6stk3 / t6r70 must still PASS as themselves. A SYNTHETIC mixyx50r70 log (ourvzlb25r70's log with
the XENV swapped and the ARM_MIXYX lines added, counts untouched so the rawlink / written-count checks stay
consistent) must PASS, and mutants must FAIL, the structural ones on their own message.
"""
import ast
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("MIXYX50R70_ROOT", pathlib.Path(__file__).resolve().parents[1]))
GATE = pathlib.Path(os.environ.get("MIXYX50R70_GATE", ROOT / "ops" / "gate.py"))  # dry run: point at a COPY
TAG = "mixyx50r70"
BASE_TAG = "ourvzlb25r70"
T65_TAG = "t65b25r70"
OLD_XENV = (r"ARM_XENV tag=ourvzlb25r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr "
            r"V1284_AXES=yx")
XENV = (r"ARM_XENV tag=mixyx50r70 TIGHT=6\.5 BONUS=2\.50 RAWLINK=0\.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr "
        r"V1284_AXES=yx MIXYX=0\.50")
OLD_XFORBID = r"ARM_XENV tag=(?!ourvzlb25r70 )"
NEW_XFORBID = r"ARM_XENV tag=(?!mixyx50r70 )"
OLD_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK)\b)[A-Z0-9]+"
NEW_ALLOW = r"\bARM_(?!(?:STK3V|STK3B|T65H|XENV|SV_ZONLY|SV_Z_TO_ARR|V1284_YX|RAWLINK|MIXYX)\b)[A-Z0-9]+"
MOVIES = ("44b6_0113de3b", "44b6_0b24845f", "6bba_05b6850b", "6bba_05db0fb1")
MIX_NEED_FIXED = [r"ARM_MIXYX w=0\.5 \(y/x = 0\.5\*V1284 \+ 0\.5\*SV into the per-frame detections after V1284; "
                  r"z = SV z-to-arr\)",
                  r"ARM_MIXYX patch applied to .* predictor anchors=7 module anchors=1 w=0\.5(?!\d)"]
NZ = r"(?:0\.\d*[1-9]\d*|[1-9]\d*\.\d+)"  # a printed %.4f value that is not 0.0000
MIX_MOVIE_FMT = (r"ARM_MIXYX w=0\.5 frames=100 nodes=%d mean_abs_sv_minus_v1284_um y=NZ x=NZ "
                 r"mean_abs_sv_um y=NZ x=NZ mean_abs_v1284_um y=NZ x=NZ "
                 r"mean_abs_yx_blend_um=NZ final_yx_add=0(?!\d)").replace("NZ", NZ.replace("%", "%%"))
MIX_FORBID = [r"ARM_MIXYX env flags missing", r"ARM_MIXYX (?:module )?anchor matched", r"ARM_MIXYX PATCH DID NOT PERSIST",
              r"ARM_MIXYX w outside", r"ARM_MIXYX needs the V1284 z-to-arr body", r"ARM_MIXYX full-SV z differs",
              r"ARM_MIXYX detection y/x not integral", r"ARM_MIXYX y/x blend not applied exactly once",
              r"ARM_MIXYX node count mismatch", r"ARM_MIXYX z-only SV y/x columns are not zero", r"ARM_MIXYX NO-OP",
              r"ARM_MIXYX assembled y/x", r"ARM_MIXYX w=(?!0\.5(?!\d))", r"final_yx_add=(?!0(?!\d))"]
# real-shaped mixyx prints that the new forbid list must NOT hit
GOOD_LINES = [
    "ARM_MIXYX w=0.5 (y/x = 0.5*V1284 + 0.5*SV into the per-frame detections after V1284; z = SV z-to-arr)",
    "ARM_MIXYX patch applied to /kaggle/working/tracking_repo/scripts/predict_unet_transformer.py | predictor anchors=7 "
    "module anchors=1 w=0.5",
    "ARM_MIXYX w=0.5 frames=100 nodes=26532 mean_abs_sv_minus_v1284_um y=0.3003 x=0.3825 mean_abs_sv_um y=0.4307 "
    "x=0.4233 mean_abs_v1284_um y=0.3048 x=0.3870 mean_abs_yx_blend_um=0.4100 final_yx_add=0",
    "ARM_XENV tag=mixyx50r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx MIXYX=0.50",
    "ARM_RAWLINK [44b6_0113de3b] min_prob=0.7 candidates=325 accepted=325 replaced=301 anchor=24890 final=24914 "
    "max_in=1 max_out=2 divs=34->34 divs_shielded=2 blocked_parent=0 blocked_daughter=2 below_min=43 replaced_raw=0 "
    "new_isolated=6"]


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
    watch = {BASE_TAG, T65_TAG, TAG}
    for node in body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            k = _forbid_key(node.targets[0])
            if k is not None:
                assigns.setdefault(k, []).append(node)
        if isinstance(node, ast.For) and isinstance(node.iter, (ast.Tuple, ast.List)):
            names = {e.value for e in node.iter.elts if isinstance(e, ast.Constant)}
            if names & watch:
                raise SystemExit("a top-level loop rewrites forbid for %r; refusing to resolve by ast" % (names & watch))

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


def xcheck_from_live(t):
    """The live ourvzlb25r70 cross-check block, renamed for this tag (comment lines dropped, code byte for byte)."""
    start = t.index("# --- ourvzlb25r70 (ops/add_ourvzlb25r70_gate.py)")
    begin = t.index('if "ourvzlb25r70" in tags:\n', start)
    ends = [t.index('sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n', begin)]
    if "\n# --- " in t[begin:]:
        ends.append(t.index("\n# --- ", begin) + 1)  # another installer's block may follow ours
    code = t[begin:min(ends)]
    if code.count("ourvzlb25r70") != 5 or code.count("_ovwant") != 6 or "_mx" in code or "\n#" in code.rstrip("\n"):
        raise SystemExit("the live ourvzlb25r70 cross-check block is not the one this installer was written against")
    new = code.replace("ourvzlb25r70", TAG).replace("_ov", "_mx")
    if "_ov" in new or new.replace(TAG, "ourvzlb25r70").replace("_mx", "_ov") != code:
        raise SystemExit("cross-check rename is not a clean round trip")
    return new


def live_line(t, pat):
    """The single live gate line matching pat."""
    hits = re.findall(pat, t)
    if len(hits) != 1:
        raise SystemExit("live-line pattern %r matched %d times" % (pat[:50], len(hits)))
    return hits[0]


def insert_before_each(txt, needle, add_fn):
    out, pos, k = [], 0, 0
    for m in re.finditer(needle, txt):
        ls = txt.rfind("\n", 0, m.start()) + 1
        out.append(txt[pos:ls])
        out.append(add_fn(m))
        pos = ls
        k += 1
    out.append(txt[pos:])
    return "".join(out), k


def main():
    t = GATE.read_text(encoding="utf-8")
    if "'%s'" % TAG in t or '"%s"' % TAG in t:
        raise SystemExit("gate entry for %s already exists" % TAG)
    # ---- need
    base = list(need_of(t, BASE_TAG))
    if base.count(OLD_XENV) != 1 or sum("ARM_XENV" in p for p in base) != 1:
        raise SystemExit("need['ourvzlb25r70'] does not carry exactly one XENV line: %r" % base)
    if any("MIXYX" in p for p in base):
        raise SystemExit("need['ourvzlb25r70'] unexpectedly mentions MIXYX")
    nodes = []
    for p in base:
        m = re.match(r"SV_ARM_HSG200 nodes=(\d+) ", p)
        if m:
            nodes.append(int(m.group(1)))
    zt = [int(re.match(r"ARM_SV_Z_TO_ARR frames=100 nodes=(\d+) ", p).group(1)) for p in base
          if p.startswith("ARM_SV_Z_TO_ARR frames=100 nodes=")]
    if len(nodes) != 4 or sorted(nodes) != sorted(zt):
        raise SystemExit("need['ourvzlb25r70'] per-movie SV pins are not the 4 expected: %r / %r" % (nodes, zt))
    t65 = list(need_of(t, T65_TAG))
    rl_base = [p for p in base if ("RAWLINK" in p or "rawlink" in p) and not p.startswith("ARM_XENV")]
    rl_t65 = [p for p in t65 if ("RAWLINK" in p or "rawlink" in p) and not p.startswith("ARM_XENV")]
    if len(rl_base) != 6 or rl_base != rl_t65:
        raise SystemExit("rawlink patterns of ourvzlb25r70 (%d) != t65b25r70's" % len(rl_base))
    for knob in ('ARM_STK3B learned_bonus=2\\.5', 'ARM_T65H tight_um=6\\.5', 'ARM_STK3V velocity_weight=0\\.25'):
        if knob not in base or knob not in t65:
            raise SystemExit("linker knob %r not pinned by both parents" % knob)
    core = [p for p in base if p != OLD_XENV]
    pats = core + MIX_NEED_FIXED + [MIX_MOVIE_FMT % n for n in nodes] + [XENV]
    if len(pats) != len(base) + 6 or len(set(pats)) != len(pats) or pats.count(XENV) != 1:
        raise SystemExit("unexpected need list shape: %r" % pats)
    for line in GOOD_LINES[:3]:
        if not any(re.search(p, line) for p in pats if "MIXYX" in p):
            raise SystemExit("no mixyx need pattern matches the real-shaped line %r" % line[:70])
    # ---- forbid
    fz = forbid_of(t, BASE_TAG)
    if fz.count(OLD_XFORBID) != 1 or fz.count(OLD_ALLOW) != 1:
        raise SystemExit("forbid['ourvzlb25r70'] lacks its XENV forbid / ARM_ allowlist exactly once: %r" % fz)
    if any("MIXYX" in p for p in fz):
        raise SystemExit("forbid['ourvzlb25r70'] mentions MIXYX; re-derive by hand")
    forbid = [NEW_XFORBID if p == OLD_XFORBID else NEW_ALLOW if p == OLD_ALLOW else p for p in fz]
    forbid += [p for p in MIX_FORBID if p not in forbid]
    for line in GOOD_LINES:
        hit = [p for p in forbid if re.search(p, line)]
        if hit:
            raise SystemExit("new forbid list hits a legitimate print %r via %r" % (line[:60], hit))
    for line in ("ARM_MIXYX w=0.3 frames=100 nodes=1", "final_yx_add=1", "ARM_MIXYX PATCH DID NOT PERSIST",
                 "ARM_MIXYX anchor matched 0 times", "ARM_XENV tag=ourvzlb25r70 TIGHT", "ARM_XENV tag=t65b25r70 TIGHT",
                 "ARM_LCEFR patch applied to x", "Traceback (most recent call last)", "ARM_RAWLINK min_prob=-1.0 enabled=False",
                 '"motion_relink_learned_bonus": 1.6,', "ARM_T60H tight_um=6.0", "ARM_FLOWFIX enabled=True",
                 "ARM_MIXYX NO-OP: SV or V1284 y/x all zero"):
        if not any(re.search(p, line) for p in forbid):
            raise SystemExit("new forbid list does not catch %r" % line)
    # ---- patch text
    comment = ("        # --- mixyx50r70: t65b25r70's full stack with y/x = 0.5*V1284 + 0.5*SV (V1284 mounted as in ourvzlb25r70,\n"
               "        # z = production SV z-to-arr as in both parents; scratchpad/wf30). = need['ourvzlb25r70'] minus its XENV\n"
               "        # (z-only SV + z-to-arr pins stay EXACT: the z-only call is untouched) + the ARM_MIXYX env/patch lines +\n"
               "        # one ARM_MIXYX line per movie at that movie's detection count + this arm's XENV\n"
               "        # (build_mixyx50r70.py; ops/add_mixyx50r70_gate.py). RL_TAGS + orphan cap + written-count cross-check.\n")
    entry = comment + "        '%s': [\n" % TAG + "".join("            %r,\n" % p for p in pats) + "        ],\n"
    xcheck = ("# --- mixyx50r70 (ops/add_mixyx50r70_gate.py): ourvzlb25r70's per-movie cross-check (generated from its block):\n"
              "# cell-10 written nodes/edges/divisions == (FINAL nodes, ARM_RAWLINK final=, safe divisions added), run_stats\n"
              "# agrees, line-fit smoothed + skipped == nodes.\n") + xcheck_from_live(t)
    anchors = {"need": "        't6dl': [\n", "forbid": 'forbid["t6dl"] = [',
               "svmark": '"t60e": "SV_ARM_HSG200", "t6stk3": "SV_ARM_HSG200",',
               "tol": '"ourvzlb25r70": 0.15',
               # other installers keep appending tags to these two sets: take the single live line
               "rltags": live_line(t, r'RL_TAGS = \{[^}\n]*"ourvzlb25r70"[^}\n]*\}'),
               "orphan": live_line(t, r'    if \{"t6r70", "t6rlf", "t6r70T15", "t65b25r70"[^}\n]*"ourvzlb25r70"[^}\n]*\}'
                                      r' & set\(tags\):\n'),
               "svtags": 'sv_tags = [t for t in tags if t.startswith("hsoft") or t in sv_mark]\n'}
    for k, a in anchors.items():
        if t.count(a) != 1:
            raise SystemExit("anchor %s matched %d times" % (k, t.count(a)))
    t2 = t.replace(anchors["need"], entry + anchors["need"], 1)
    t2 = t2.replace(anchors["forbid"], "forbid[%r] = %r\n" % (TAG, forbid) + anchors["forbid"], 1)
    t2 = t2.replace(anchors["svmark"], anchors["svmark"] + ' "%s": "SV_ARM_HSG200",' % TAG, 1)
    t2 = t2.replace(anchors["tol"], anchors["tol"] + ', "%s": 0.15' % TAG, 1)
    t2 = t2.replace(anchors["rltags"], anchors["rltags"][:-1] + ', "%s"}' % TAG, 1)
    t2 = t2.replace(anchors["orphan"], anchors["orphan"].replace("} & set(tags):", ', "%s"} & set(tags):' % TAG), 1)
    t2 = t2.replace(anchors["svtags"], xcheck + anchors["svtags"], 1)
    lit = [n for n in ast.parse(t2).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "sv_mark"
           and isinstance(n.value, ast.Dict)]
    if len(lit) != 1 or ast.literal_eval(lit[0].value).get(TAG) != "SV_ARM_HSG200" \
            or not t2.index("sv_mark = {") < t2.index('"%s": "SV_ARM_HSG200"' % TAG) < t2.index(anchors["svtags"]):
        raise SystemExit("sv_mark entry for %s is not inside the dict literal before sv_tags is computed" % TAG)
    if forbid_of(t2, TAG) != forbid or need_of(t2, TAG) != pats:
        raise SystemExit("re-parse of the patched gate does not return the new need/forbid entries")
    if not (t2.index('RL_TAGS = {') < t2.index('"%s" in tags:' % TAG) < t2.index(anchors["svtags"])):
        raise SystemExit("cross-check block misplaced")
    if ('"%s"' % TAG) not in t2[t2.index("RL_TAGS = {"):t2.index("\n", t2.index("RL_TAGS = {"))]:
        raise SystemExit("RL_TAGS patch missing")
    set_pat = (r"RL_TAGS = (\{[^}\n]*\})", r'\n    if (\{"t6r70", "t6rlf", "t6r70T15", "t65b25r70"[^}\n]*\}) & set\(tags\):\n')
    for sp in set_pat:
        a_, b_ = re.findall(sp, t), re.findall(sp, t2)
        if len(a_) != 1 or len(b_) != 1 or ast.literal_eval(b_[0]) != ast.literal_eval(a_[0]) | {TAG}:
            raise SystemExit("set patch %r changed more than adding %s" % (sp[:20], TAG))
    compile(t2, str(GATE), "exec")
    if GATE.read_text(encoding="utf-8") != t:
        raise SystemExit("gate.py changed while patching (another installer?); nothing written")
    bak = GATE.with_name("gate.py.bak_" + TAG)
    bak.write_text(t, encoding="utf-8")
    GATE.write_text(t2, encoding="utf-8")
    # ---- self-tests on real logs
    res = {"neg_ourvzlb25r70_as_mixyx50r70": gate("out_ourvzlb25r70", TAG),
           "neg_t65b25r70_as_mixyx50r70": gate("out_t65b25r70", TAG),
           "pos_t65b25r70": gate("out_t65b25r70", "t65b25r70"), "pos_ourvzlb25r70": gate("out_ourvzlb25r70", "ourvzlb25r70"),
           "pos_ourvzlb25": gate("out_ourvzlb25", "ourvzlb25"), "pos_t65b25": gate("out_t65b25", "t65b25"),
           "pos_t6stk3": gate("out_t6stk3", "t6stk3"), "pos_t6r70": gate("out_t6r70", "t6r70")}
    own = list((ROOT / "data").glob("out_%s/*.log" % TAG))
    if own:
        res["own_" + TAG] = gate("out_" + TAG, TAG)
    # ---- synthetic positive + mutants from ourvzlb25r70's log (+ its run_stats.csv)
    src_dir = ROOT / "data" / "out_ourvzlb25r70"
    src = log_text(next(src_dir.glob("*.log")))
    old_x = "ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx"
    new_x = old_x.replace("tag=ourvzlb25r70", "tag=mixyx50r70") + " MIXYX=0.50"
    env_line = GOOD_LINES[0] + "\n"
    patch_line = GOOD_LINES[1] + "\n"

    def mix_line(n, w="0.5", fin="0", d="0.3003"):
        return ("ARM_MIXYX w=%s frames=100 nodes=%d mean_abs_sv_minus_v1284_um y=%s x=0.3825 mean_abs_sv_um y=0.4307 "
                "x=0.4233 mean_abs_v1284_um y=0.3048 x=0.3870 mean_abs_yx_blend_um=0.4100 final_yx_add=%s\n" % (w, n, d, fin))

    def build(skip_node=None, **kw):
        s = src
        if s.count(old_x) != 1:
            raise SystemExit("synthetic: ourvzlb25r70 XENV line not exactly once in its log")
        s = s.replace(old_x, new_x)
        a = s.index("ARM_SV_Z_TO_ARR=1 (")
        a = s.index("\n", a) + 1
        s = s[:a] + env_line + s[a:]
        b = s.index("ARM_SV_Z_TO_ARR patch applied to")
        b = s.index("\n", b) + 1
        s = s[:b] + patch_line + s[b:]
        s, k = insert_before_each(s, r"ARM_SV_Z_TO_ARR frames=100 nodes=(\d+) ",
                                  lambda m: "" if int(m.group(1)) == skip_node else mix_line(int(m.group(1)), **kw))
        if k < 4:
            raise SystemExit("synthetic: fewer than 4 ARM_SV_Z_TO_ARR per-movie lines in the source log")
        return s

    syn = build()
    pe = syn.find("Prediction completed")
    fe = syn.find("[44b6_0113de3b] FINAL: ")
    mutants = {
        "neg_syn_w03": (build(w="0.3"), None),
        "neg_syn_final_yx_add1": (build(fin="1"), None),
        "neg_syn_noop_d0": (build(d="0.0000"), "marker missing"),
        "neg_syn_movie_line_missing": (build(skip_node=7370), "marker missing"),
        "neg_syn_parent_xenv": (syn[:pe] + old_x + "\n" + syn[pe:], None),
        "neg_syn_t65_xenv": (syn[:pe] + "ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept\n" + syn[pe:], None),
        "neg_syn_not_persist": (syn[:pe] + "RuntimeError: ARM_MIXYX PATCH DID NOT PERSIST\n" + syn[pe:], "ARM_MIXYX PATCH DID NOT PERSIST"),
        "neg_syn_traceback": (syn[:fe] + "Traceback (most recent call last):\n" + syn[fe:], None),
        "neg_syn_lcefr_line": (syn[:pe] + "ARM_LCEFR patch applied to predictor\n" + syn[pe:], None),
        "neg_syn_no_env_marker": (syn.replace(env_line, "", 1), "marker missing"),
        "neg_syn_rawlink_disabled": (syn[:pe] + "ARM_RAWLINK min_prob=-1.0 enabled=False rule=raw_ilp_override_final_divisions_protected\n" + syn[pe:], None),
        "neg_syn_sv_after_pred": ("Prediction completed (mutant: SV lines now after it)\n" + syn,
                                  "only 0 SV_ARM_HSG200 lines before 'Prediction completed'"),
    }
    with tempfile.TemporaryDirectory() as td:
        cases = [("pos_syn_mixyx50r70", syn, None, True)] + [(k, v, why, True) for k, (v, why) in mutants.items()]
        cases.append(("neg_syn_no_run_stats", syn, "no run_stats.csv beside the log", False))
        for name, body, why, with_rs in cases:
            d = pathlib.Path(td) / name
            d.mkdir()
            if with_rs:
                shutil.copy(src_dir / "run_stats.csv", d / "run_stats.csv")
            p = d / (name + ".log")
            p.write_text(body, encoding="utf-8")
            res[name] = gate_file(p, TAG)
            if why is not None and why not in res[name]:
                res[name] = "WRONG-REASON (wanted %r): %s" % (why, res[name])
    for k, v in res.items():
        print(k, "->", v[:600])
    ok = all("GATE_FAIL" in v and not v.startswith("WRONG-REASON") for k, v in res.items() if k.startswith("neg_")) \
        and all("GATE_PASS" in v for k, v in res.items() if k.startswith("pos_"))
    if not ok:
        if GATE.read_text(encoding="utf-8") == t2:
            GATE.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
            raise SystemExit("self-test failed; gate.py restored from " + bak.name)
        raise SystemExit("self-test failed AND gate.py was modified by someone else meanwhile; NOT restored, check by hand")
    print("gate entry for %s added (backup %s)" % (TAG, bak.name))


if __name__ == "__main__":
    main()
