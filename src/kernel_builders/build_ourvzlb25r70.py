#!/usr/bin/env python3
"""ourvzlb25r70 = ourvzlb25 (board 0.954, 56640901: the PUBLIC V1284 coordinate head for y/x + our sub-voxel z fed to
the edge model, relink TIGHT 6.5, learned BONUS 2.5) plus t6r70's raw-ILP override "rawlink" at min_prob 0.70.

usage: python scratch_kernels/build_ourvzlb25r70.py [tag]        (default tag ourvzlb25r70)

WHY: the rawlink step turned t65b25 (0.954) into t65b25r70 (0.954, the team's top entry above t65b25). ourvzlb25 is
the second, decorrelated coordinate body at the same display; this applies the same step to it.

HOW: rawlink = exactly what t6r70 added to t6stk3, and it lives in three cells:
  cell 0: one env line  os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"  (after BIOHUB_DEEPCENTER_TTA)
  cell 2: the RAWLINK_MIN_PROB reader, the "rawlink_min_prob" CONFIG_DISPLAY echo and the ARM_RAWLINK print
  cell 5: rawlink_override(), the per-movie call + ARM_RAWLINK print, the run_stats merge and rawlink_actions.csv
The blocks are taken as the line-level INSERT hunks of v_t6stk3 -> v_t6r70 (difflib; any non-insert opcode aborts)
and each one is re-anchored into v_ourvzlb25 by its surrounding t6stk3 context, which must occur EXACTLY ONCE in
both t6stk3 and ourvzlb25. ourvzlb25's cell 4 (the V1284 + z-to-arr predictor patches) is never touched and is
checked byte for byte. ourvzlb25's single identity line
    ARM_XENV tag=ourvzlb25 TIGHT=6.5 BONUS=2.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx
is REPLACED (not duplicated) by
    ARM_XENV tag=ourvzlb25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx
Cross-checks: cells changed vs v_ourvzlb25 == [0, 2, 5]; the built cells 2/5 equal v_t6r70's (and v_t65b25r70's)
byte for byte, which holds because ourvzlb25's cells 2/5 are t6stk3's; the ourvzlb25 -> ourvzlb25r70 line delta
equals the t65b25 -> t65b25r70 delta in all three cells apart from the XENV text; metadata = ourvzlb25's
(same datasets incl. the V1284 head, sources, T4 GPU, no internet) apart from id/title.
"""
import difflib
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourvzlb25"
BASE_MD5 = "3c34fcc1ca563e1a63a1dc6535489739"  # v_ourvzlb25/kernel.ipynb as built by build_ourvzlb25.py (56640901)
RL = SK / "v_t6r70"
RL_MD5 = "38adf357f63250a34ce7f6337c47c626"  # v_t6r70/kernel.ipynb (same pin as build_t65b25r70.py)
BODY = SK / "v_t6stk3"
BODY_MD5 = "643f4de949f707e161b118733e35e6df"  # v_t6stk3/kernel.ipynb (same pin as build_t65b25r70.py)
T65B25 = SK / "v_t65b25"
T65B25_MD5 = "5a7beb98dc0d2c4234e99c34895c3ed1"  # v_t65b25/kernel.ipynb (submitted 56639660)
T65B25R70 = SK / "v_t65b25r70"
T65B25R70_MD5 = "60722ec9a2f277733656ba6bf5b559af"  # v_t65b25r70/kernel.ipynb (submitted 56640601, board 0.954)
NL = chr(10)
RL_CELLS = (0, 2, 5)
V1284_CELL = 4

RAWLINK_ENV = ('os.environ["BIOHUB_RAWLINK_MIN_PROB"] = "0.70"  # rawlink: raw ILP edges >= this override conflicting '
               'final edges (josephadamski91 V1057)')
XENV_OLD = 'print("ARM_XENV tag=ourvzlb25 TIGHT=6.5 BONUS=2.50 V1284_HEAD=mounted SUBVOXEL=z-to-arr V1284_AXES=yx", flush=True)'
XENV_FMT = ('print("ARM_XENV tag=%s TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 V1284_HEAD=mounted SUBVOXEL=z-to-arr '
            'V1284_AXES=yx", flush=True)')
T65B25_XENV = 'print("ARM_XENV tag=t65b25 TIGHT=6.5 BONUS=2.50 LCEFR=kept", flush=True)'
T65B25R70_XENV = 'print("ARM_XENV tag=t65b25r70 TIGHT=6.5 BONUS=2.50 RAWLINK=0.70 LCEFR=kept", flush=True)'
LINKER_LINES = ('os.environ["BIOHUB_MOTION_RELINK_LEARNED_BONUS"] = \'2.5\'',
                'print("ARM_STK3B learned_bonus=2.5", flush=True)',
                'print("ARM_T65H tight_um=6.5", flush=True)',
                'os.environ["BIOHUB_MOTION_RELINK_VELOCITY_WEIGHT"] = "0.25"')


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest()


def cells_of(path):
    nb = json.loads(path.read_bytes().decode("utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def insert_hunks(a, b, what):
    """Line-level hunks turning a into b; every one must be a pure insert. Returns [(a_pos, [lines])]."""
    al, bl = a.split(NL), b.split(NL)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, al, bl, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        if op != "insert":
            raise SystemExit("%s: t6stk3 -> t6r70 has a %r hunk (a[%d:%d] -> b[%d:%d]); rawlink is expected to be "
                             "purely additive" % (what, op, i1, i2, j1, j2))
        out.append((i1, bl[j1:j2]))
    return out


def positions(lines, before, after):
    kb, ka = len(before), len(after)
    return [p for p in range(kb, len(lines) - ka + 1) if lines[p - kb:p] == before and lines[p:p + ka] == after]


def port(src_cell, dst_cell, hunks, what):
    """Insert each hunk into dst at the unique spot whose context (lines around the insert in src) matches."""
    sl, dl = src_cell.split(NL), dst_cell.split(NL)
    plan = []
    for pos, block in hunks:
        for k in range(2, 12):
            before, after = sl[max(pos - k, 0):pos], sl[pos:pos + k]
            if len(positions(sl, before, after)) == 1:
                break
        else:
            raise SystemExit("%s: no unique t6stk3 context for the hunk at line %d" % (what, pos))
        hits = positions(dl, before, after)
        if len(hits) != 1:
            raise SystemExit("%s: anchor for the hunk at t6stk3 line %d (context %d/%d lines) matched %d times in "
                             "ourvzlb25 (need exactly 1)" % (what, pos, len(before), len(after), len(hits)))
        for ln in block:
            if ln.strip() and dl.count(ln) and ("rawlink" in ln.lower()):
                raise SystemExit("%s: ourvzlb25 already carries rawlink line %r" % (what, ln[:80]))
        plan.append((hits[0], block, len(before), len(after)))
    if len({p for p, _, _, _ in plan}) != len(plan):
        raise SystemExit("%s: two hunks re-anchored to the same line" % what)
    for p, block, _, _ in sorted(plan, key=lambda x: -x[0]):
        dl[p:p] = block
    return NL.join(dl), [(p, len(block), kb, ka) for p, block, kb, ka in sorted(plan)]


def line_delta(a, b):
    """Changed / inserted / deleted lines between two cells, as (op, old lines, new lines) tuples."""
    al, bl = a.split(NL), b.split(NL)
    return [(op, tuple(al[i1:i2]), tuple(bl[j1:j2]))
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, al, bl, autojunk=False).get_opcodes() if op != "equal"]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "ourvzlb25r70"
    for d, m in ((BASE, BASE_MD5), (RL, RL_MD5), (BODY, BODY_MD5), (T65B25, T65B25_MD5), (T65B25R70, T65B25R70_MD5)):
        if md5(d / "kernel.ipynb") != m:
            raise SystemExit("STOP: %s/kernel.ipynb md5 changed (expected %s)" % (d.name, m))
    nb, cells = cells_of(BASE / "kernel.ipynb")
    _, rl = cells_of(RL / "kernel.ipynb")
    _, body = cells_of(BODY / "kernel.ipynb")
    _, s25 = cells_of(T65B25 / "kernel.ipynb")
    _, s25r = cells_of(T65B25R70 / "kernel.ipynb")
    orig = list(cells)
    if not (len(cells) == len(rl) == len(body) == len(s25) == len(s25r) == 12) or any(c is None for c in cells):
        raise SystemExit("unexpected notebook shape (need 12 code cells everywhere)")
    # ---- preconditions: where t6r70 differs from t6stk3, and where ourvzlb25 differs from t6stk3
    rl_changed = [i for i, (a, b) in enumerate(zip(body, rl)) if a != b]
    if rl_changed != list(RL_CELLS):
        raise SystemExit("t6stk3 -> t6r70 changed cells %r (expected %r)" % (rl_changed, list(RL_CELLS)))
    base_changed = [i for i, (a, b) in enumerate(zip(body, cells)) if a != b]
    if base_changed != [0, V1284_CELL]:
        raise SystemExit("t6stk3 -> ourvzlb25 changed cells %r (expected [0, 4]: linker cell 0 + V1284 cell 4)" % base_changed)
    for i in (2, 5):
        if cells[i] != body[i]:
            raise SystemExit("ourvzlb25 cell %d is not t6stk3's; the rawlink port assumption fails" % i)
    for i in (RL_CELLS + (V1284_CELL,)):
        if "RAWLINK" in cells[i] or "rawlink" in cells[i]:
            raise SystemExit("ourvzlb25 cell %d already mentions rawlink" % i)
    if any("RAWLINK" in c or "rawlink" in c for c in cells):
        raise SystemExit("ourvzlb25 already mentions rawlink somewhere")
    c0l = cells[0].split(NL)
    if c0l.count(XENV_OLD) != 1 or cells[0].count("ARM_XENV") != 1 or sum("ARM_XENV" in c for c in cells) != 1:
        raise SystemExit("ourvzlb25 must carry exactly one ARM_XENV line (cell 0): %r" % XENV_OLD)
    for ln in LINKER_LINES:
        if c0l.count(ln) != 1:
            raise SystemExit("ourvzlb25 cell 0 lacks linker line %r exactly once" % ln)
    v1284_src = cells[V1284_CELL]
    for mk in ("V1284", "ARM_SV_Z_TO_ARR", "ARM_V1284_YX"):
        if mk not in v1284_src:
            raise SystemExit("ourvzlb25 cell 4 lacks %r: not the V1284 body" % mk)
    # ---- port the rawlink insert hunks, cell by cell
    report = {}
    for i in RL_CELLS:
        hunks = insert_hunks(body[i], rl[i], "cell %d" % i)
        if not hunks:
            raise SystemExit("cell %d: no rawlink hunk found" % i)
        cells[i], report[i] = port(body[i], cells[i], hunks, "cell %d" % i)
    if cells[0].split(NL).count(RAWLINK_ENV) != 1 or cells[0].count("BIOHUB_RAWLINK_MIN_PROB") != 1:
        raise SystemExit("the rawlink env line did not land exactly once in cell 0")
    # ---- identity line: replace ourvzlb25's XENV with this arm's
    xenv = XENV_FMT % tag
    c0l = cells[0].split(NL)
    c0l[c0l.index(XENV_OLD)] = xenv
    cells[0] = NL.join(c0l)
    # ---- checks on the built cells
    if cells[V1284_CELL] != v1284_src or cells[V1284_CELL] != orig[V1284_CELL]:
        raise SystemExit("cell 4 (V1284 predictor patches) changed")
    changed = [i for i, (a, b) in enumerate(zip(orig, cells)) if a != b]
    if changed != list(RL_CELLS):
        raise SystemExit("cells changed vs v_ourvzlb25 = %r (expected %r)" % (changed, list(RL_CELLS)))
    for i in (2, 5):
        if cells[i] != rl[i] or cells[i] != s25r[i]:
            raise SystemExit("built cell %d is not v_t6r70's / v_t65b25r70's byte for byte" % i)
    b0 = cells[0].split(NL)
    for bad in ("tag=ourvzlb25 ", "'1.6'", "learned_bonus=1.6", "ARM_T60H", "tight_um=6.0", "LCEFR"):
        if bad in cells[0]:
            raise SystemExit("stale / foreign text %r in the built cell 0" % bad)
    for need in (RAWLINK_ENV, xenv) + LINKER_LINES:
        if b0.count(need) != 1:
            raise SystemExit("line %r not exactly once in the built cell 0" % need[:70])
    if sum("ARM_XENV" in c for c in cells) != 1:
        raise SystemExit("more than one ARM_XENV line in the build")
    if cells[2].count('RAWLINK_MIN_PROB = float(os.environ.get("BIOHUB_RAWLINK_MIN_PROB", "-1"))') != 1 \
            or cells[2].count('"rawlink_min_prob": RAWLINK_MIN_PROB,') != 1 \
            or cells[2].count('print(f"ARM_RAWLINK min_prob={RAWLINK_MIN_PROB!r} enabled={RAWLINK_MIN_PROB >= 0.0}"') != 1:
        raise SystemExit("cell 2 does not read / echo / print RAWLINK_MIN_PROB exactly once")
    if cells[5].count("def rawlink_override(") != 1 \
            or cells[5].count("edges, rawlink_stats, rawlink_actions = rawlink_override(rawlink_raw_edges, nodes_by_id, edges)") != 1 \
            or cells[5].count("**rawlink_stats,") != 1 or cells[5].count('"rawlink_actions.csv"') != 1:
        raise SystemExit("cell 5 does not define + call rawlink_override exactly once")
    # the ourvzlb25 -> ourvzlb25r70 delta must be the t65b25 -> t65b25r70 delta (XENV text aside) in every cell
    for i in RL_CELLS:
        ours = line_delta(orig[i], cells[i])
        ref = line_delta(s25[i], s25r[i])
        if i == 0:
            ours = [d for d in ours if d != ("replace", (XENV_OLD,), (xenv,))]
            ref = [d for d in ref if d != ("replace", (T65B25_XENV,), (T65B25R70_XENV,))]
        if ours != ref:
            raise SystemExit("cell %d: rawlink delta differs from t65b25 -> t65b25r70:\n ours %r\n ref  %r" % (i, ours, ref))
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
    bm = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    nm = json.loads((dest / "kernel-metadata.json").read_text(encoding="utf-8"))
    mdiff = sorted(k for k in set(bm) | set(nm) if bm.get(k) != nm.get(k))
    if mdiff != ["id", "title"]:
        raise SystemExit("metadata differs from ourvzlb25's beyond id/title: %r" % mdiff)
    print("built", dest, "| base v_ourvzlb25 (md5 %s) + t6r70 rawlink 0.70 (v_t6stk3 -> v_t6r70 insert hunks)" % BASE_MD5)
    print("cells changed vs v_ourvzlb25:", changed, "| cell 4 (V1284) untouched: md5",
          hashlib.md5(built[V1284_CELL].encode("utf-8")).hexdigest(),
          "| metadata diff:", mdiff, "| datasets", nm["dataset_sources"], "| machine", nm.get("machine_shape"),
          "| gpu", nm.get("enable_gpu"), "| internet", nm.get("enable_internet"))
    for i in RL_CELLS:
        d = line_delta(orig[i], built[i])
        n_add = sum(len(new) for op, old, new in d if op == "insert")
        print("  cell %d: %d hunk(s) re-anchored at ourvzlb25 lines %s, +%d lines%s" % (
            i, len(report[i]), [p for p, _, _, _ in report[i]], n_add,
            "; XENV line replaced" if i == 0 else ""))
        if i == 0:
            for op, old, new in d:
                for x in old:
                    print("     -", x)
                for y in new:
                    print("     +", y)
    print("cells 2, 5 == v_t6r70 == v_t65b25r70 byte for byte; ourvzlb25 -> ourvzlb25r70 delta == t65b25 -> t65b25r70 "
          "delta in cells 0/2/5 (XENV text aside)")
    print("kernel.ipynb md5", md5(dest / "kernel.ipynb"))


if __name__ == "__main__":
    main()
