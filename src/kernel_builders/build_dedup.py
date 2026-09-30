#!/usr/bin/env python3
"""Build the co-located node de-duplication arm on our 0.954 body.

usage: python scratch_kernels/build_dedup.py <tag> <radius_um> [KEY=VALUE ...]

Inserts _dedup_block.py into cell 5 just before the FINAL print, and calls it as the last
post-processing step. Every other stage is byte-identical to t6stk3.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
BLOCK = SK / "_dedup_block.py"
Q = chr(34)
NL = chr(10)

ANCHOR_DEF = '    print(f"  [{dataset}] FINAL: {len(nodes_by_id)} nodes, {len(edges)} edges")' + NL
CALL = ('    nodes_by_id, edges = dedup_colocated_nodes(nodes_by_id, edges, stats, dataset=dataset)' + NL)
DEF_ANCHOR = 'def filter_output_graph('


def main():
    tag, radius = sys.argv[1], sys.argv[2]
    env_over = {"BIOHUB_DEDUP_RADIUS_UM": radius}
    for a in sys.argv[3:]:
        if "=" in a and not a.startswith("--"):
            k, v = a.split("=", 1)
            env_over[k] = v

    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]

    # cell 0: env, plus a runtime identity line
    new0 = cells[0]
    for k, v in env_over.items():
        pat = re.compile(r'os\.environ\[\s*["\']%s["\']\s*\]\s*=\s*[^\n]*' % re.escape(k))
        line = 'os.environ["%s"] = "%s"' % (k, v)
        new0 = pat.sub(line, new0, count=1) if pat.search(new0) else new0.rstrip(NL) + NL + line + NL
        if new0.count(line) != 1:
            raise SystemExit("env %s applied %d times" % (k, new0.count(line)))
    keys = sorted(env_over)
    ident = ('print(' + Q + 'ARM_XENV tag=%s ' % tag + ' '.join(k + '=%s' for k in keys) + Q
             + ' % (' + ', '.join('os.environ[' + Q + k + Q + ']' for k in keys) + ',), flush=True)')
    compile(ident, "ident", "exec")
    cells[0] = new0.rstrip(NL) + NL + ident + NL

    # cell 1 drift guard, for any key it pins
    new1 = cells[1]
    for k, v in env_over.items():
        a = '    "%s": ' % k
        if a in new1:
            i = new1.index(a)
            j = new1.index(NL, i)
            new1 = new1[:i] + '    "%s": %s,' % (k, float(v)) + new1[j:]
            print("  guard updated: %s -> %s" % (k, float(v)))
    cells[1] = new1

    # cell 5: the block before filter_output_graph, the call before the FINAL print
    c5 = cells[5]
    if c5.count(DEF_ANCHOR) != 1:
        raise SystemExit("filter_output_graph anchor matched %d times" % c5.count(DEF_ANCHOR))
    if c5.count(ANCHOR_DEF) != 1:
        raise SystemExit("FINAL print anchor matched %d times" % c5.count(ANCHOR_DEF))
    c5 = c5.replace(DEF_ANCHOR, BLOCK.read_text(encoding="utf-8").lstrip(NL) + NL + DEF_ANCHOR, 1)
    c5 = c5.replace(ANCHOR_DEF, CALL + ANCHOR_DEF, 1)
    cells[5] = c5

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
    json.dump(nb, open(dest / "kernel.ipynb", "w", encoding="utf-8"))
    meta = json.loads((BASE / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest, "|", env_over)


if __name__ == "__main__":
    main()
