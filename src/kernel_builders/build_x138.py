#!/usr/bin/env python3
"""Build arms that merge the public x138 body (flow relink + readmit + gapfill)
with our own proven patches.

usage: python scratch_kernels/build_x138.py <tag> [--subvoxel] [--lcefr] [--env K=V ...]

The x138 V1284 block is ALWAYS removed: it needs anvithpothula's private
`biohub-v1284-head-s075` dataset, which we cannot mount, so the published
notebook cannot run on our account as-is. Our sub-voxel refinement occupies the
same slot (refine detector coords, keep them float through build_graph).
"""
import json, pathlib, re, sys

Q = chr(34)
ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
SRC_X = SK / "_pub0924" / "anvithpothula_biohub-x138" / "biohub-x138.ipynb"
SRC_OURS = SK / "v_t6stk3" / "kernel.ipynb"

# exact boundaries verified against the two notebooks (see HANDOFF 09-24)
V1284_START = "# --------------------------------- V1284 head, AFTER readmit's low-detection dump patch"
V1284_END = "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])"
SV_START = "# ===== SUB-VOXEL SOFT-ARGMAX REFINEMENT (sweep0911 surviving lever #2) ====="
SV_END = "print('SUBVOXEL patch applied to', _ps, flush=True)"
LC_START = "# ===== LINKER READS THE REFINED COORDINATES (arm lcefr) ====="
LC_END = "def list_test_stems() -> list[str]:"


def cells(path):
    nb = json.load(open(path, encoding="utf-8"))
    return nb, [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]


def slice_between(text, start, end, include_end=True):
    i = text.index(start)
    j = text.index(end, i)
    return text[i: j + (len(end) if include_end else 0)]


def main():
    tag = sys.argv[1]
    want_sv = "--subvoxel" in sys.argv
    want_lc = "--lcefr" in sys.argv
    env_over = {}
    for a in sys.argv[2:]:
        if a.startswith("--env"):
            continue
        if "=" in a and not a.startswith("--"):
            k, v = a.split("=", 1)
            env_over[k] = v

    nb, xc = cells(SRC_X)
    _, oc = cells(SRC_OURS)
    x4 = xc[4]
    o4 = oc[4]

    sv_block = slice_between(o4, SV_START, SV_END) + "\n\n\n"
    lc_block = slice_between(o4, LC_START, LC_END, include_end=False)

    # --- cell 4: drop V1284, put our blocks where it was -------------------
    i = x4.index(V1284_START)
    j = x4.index(V1284_END) + len(V1284_END)
    replacement = ""
    if want_sv:
        replacement += sv_block
    if want_lc:
        replacement += lc_block
    if not replacement:
        replacement = "print('coordinate-refinement slot intentionally empty in this arm', flush=True)"
    new4 = x4[:i] + replacement + x4[j:]
    if V1284_START in new4 or "v1284" in new4.lower():
        raise SystemExit("V1284 residue left in cell 4")
    if want_sv and new4.count(SV_START) != 1:
        raise SystemExit("sub-voxel block not inserted exactly once")
    if want_lc and new4.count(LC_START) != 1:
        raise SystemExit("lcefr block not inserted exactly once")

    # --- cell 0: env overrides --------------------------------------------
    new0 = xc[0]
    for k, v in env_over.items():
        pat = re.compile(r'os\.environ\[\s*["\']%s["\']\s*\]\s*=\s*[^\n]*' % re.escape(k))
        line = 'os.environ["%s"] = "%s"' % (k, v)
        if pat.search(new0):
            new0 = pat.sub(line, new0, count=1)
        else:
            new0 = new0.rstrip("\n") + "\n" + line + "\n"
        if new0.count(line) != 1:
            raise SystemExit("env override %s applied %d times" % (k, new0.count(line)))
    # An identity line read back from os.environ at RUNTIME: it proves WHICH build ran and that
    # every override is live, including keys the pipeline's own config dict never echoes.
    keys = sorted(env_over)
    ident = ('print(' + Q + 'ARM_XENV tag=%s' % tag + (' ' if keys else '')
             + ' '.join(k + '=%s' for k in keys) + Q
             + (' % (' + ', '.join('os.environ[' + Q + k + Q + ']' for k in keys) + ',)' if keys else '')
             + ', flush=True)')
    compile(ident, 'ident', 'exec')
    new0 = new0.rstrip(chr(10)) + chr(10) + ident + chr(10)

    new0 = new0.replace("BIOHUB_PRESET = 'harmonic_v3_division_wide'",
                        "BIOHUB_PRESET = 'x138_merge_%s'" % tag)

    # cell 1 re-states some of the same constants and RAISES on drift, so an override of a
    # guarded key has to move both places or the kernel dies at the guard.
    new1 = xc[1]
    for k, v in env_over.items():
        old_line = '    "%s": ' % k
        if old_line in new1:
            i = new1.index(old_line)
            j = new1.index(chr(10), i)
            new1 = new1[:i] + '    "%s": %s,' % (k, float(v)) + new1[j:]
            print('  guard updated: %s -> %s' % (k, float(v)))

    out_cells = list(xc)
    out_cells[0] = new0
    out_cells[1] = new1
    out_cells[4] = new4


    # --- markers so ops/gate.py can prove the flow / recall stack actually fired ---
    mk = SK / "_x138_markers"
    out_cells[2] = out_cells[2].rstrip(chr(10)) + mk.joinpath("cell2_echo.py").read_text(encoding="utf-8")
    relink_print = (
        '    print(f"  [{dataset}] after edge-filter+motion-relink: {len(nodes_by_id)} nodes, '
        '{len(edges)} edges | {_time.time() - _stage_t0:.1f}s")' + chr(10)
    )
    if out_cells[5].count(relink_print) != 1:
        raise SystemExit("relink print anchor matched %d times" % out_cells[5].count(relink_print))
    out_cells[5] = out_cells[5].replace(
        relink_print, relink_print + mk.joinpath("cell5_echo.py").read_text(encoding="utf-8"), 1
    )

    for idx, s in enumerate(out_cells):
        if s is None:
            continue
        compile(s, "%s:cell%d" % (tag, idx), "exec")

    nb2 = json.loads(json.dumps(nb))
    k = 0
    for c in nb2["cells"]:
        if c["cell_type"] == "code":
            c["source"] = out_cells[k].splitlines(keepends=True)
            c["outputs"] = []
            c["execution_count"] = None
        k += 1

    dest = SK / ("v_" + tag)
    dest.mkdir(parents=True, exist_ok=True)
    json.dump(nb2, open(dest / "kernel.ipynb", "w", encoding="utf-8"))
    meta = json.load(open(SK / "v_t6stk3" / "kernel-metadata.json", encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest)
    print("  subvoxel=%s lcefr=%s env=%s" % (want_sv, want_lc, env_over))
    print("  cell4 %d -> %d chars" % (len(x4), len(new4)))


if __name__ == "__main__":
    main()
