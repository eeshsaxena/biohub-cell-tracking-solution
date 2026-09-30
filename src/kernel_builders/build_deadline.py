#!/usr/bin/env python3
"""Add the rerun deadline guard to our own 0.954 body.

usage: python scratch_kernels/build_deadline.py <tag> [--base v_XXX] [KEY=VALUE ...]

The guard is designed to be a STRICT NO-OP on any run that finishes inside
REPAIR_DEADLINE_S, so the visible 4-movie output must be byte-identical to the base.
That is the thing to verify on the box replay before spending a slot.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BLOCK = SK / "_deadline_block.py"
Q = chr(34)
NL = chr(10)

ANCHOR = (
    '            raw_node_count = len(nodes_by_id)' + NL +
    '            nodes_by_id, edges, filter_stats = filter_output_graph(nodes_by_id, raw_edges, dataset=dataset, deepcenter_bundle=DEEPCENTER_VETO_DETECTOR)' + NL +
    '            if not nodes_by_id:' + NL +
    '                raise AssertionError(f"{dataset}: post-processing removed every node")' + NL
)
GUARDED = (
    '            raw_node_count = len(nodes_by_id)' + NL +
    '            _dataset_t0 = _time.time()' + NL +
    '            if not _deadline_degraded and _dataset_t0 - KERNEL_START_TS > REPAIR_DEADLINE_S:' + NL +
    '                _deadline_degrade()' + NL +
    '            _nodes_snapshot = {node_id: dict(node) for node_id, node in nodes_by_id.items()}' + NL +
    '            _edges_snapshot = [dict(edge) for edge in raw_edges]' + NL +
    '            try:' + NL +
    '                nodes_by_id, edges, filter_stats = filter_output_graph(nodes_by_id, raw_edges, dataset=dataset, deepcenter_bundle=DEEPCENTER_VETO_DETECTOR)' + NL +
    '                filter_stats["repair_fallback"] = 0' + NL +
    '                if not nodes_by_id:' + NL +
    '                    raise AssertionError(f"{dataset}: post-processing removed every node")' + NL +
    '            except Exception as _repair_exc:' + NL +
    '                _traceback.print_exc()' + NL +
    '                print(' + NL +
    '                    f"  [{dataset}] REPAIR FAILED ({type(_repair_exc).__name__}: {_repair_exc});"' + NL +
    '                    " writing the ILP graph with basic filtering instead",' + NL +
    '                    flush=True,' + NL +
    '                )' + NL +
    '                nodes_by_id, edges, filter_stats = fallback_output_graph(_nodes_snapshot, _edges_snapshot)' + NL +
    '            filter_stats["deadline_degraded"] = int(_deadline_degraded)' + NL +
    '            filter_stats["repair_seconds"] = round(_time.time() - _dataset_t0, 1)' + NL +
    '            filter_stats["kernel_elapsed_seconds"] = round(_time.time() - KERNEL_START_TS, 1)' + NL +
    '            print(' + NL +
    '                f"  [{dataset}] ARM_DEADLINE repair {_time.time() - _dataset_t0:.1f}s"' + NL +
    '                f" | kernel elapsed {_time.time() - KERNEL_START_TS:.0f}s"' + NL +
    '                f" | degraded={int(_deadline_degraded)} fallback={filter_stats.get(\'repair_fallback\', 0)}",' + NL +
    '                flush=True,' + NL +
    '            )' + NL
)
DEF_ANCHOR = 'def filter_output_graph('
CACHE_ANCHOR = '    frame_cache[t] = frame' + NL


def main():
    tag = sys.argv[1]
    base = SK / "v_t6stk3"
    args = sys.argv[2:]
    if "--base" in args:
        i = args.index("--base")
        base = SK / args[i + 1]
        args = args[:i] + args[i + 2:]
    env_over = {}
    for a in args:
        if "=" in a and not a.startswith("--"):
            k, v = a.split("=", 1)
            env_over[k] = v

    nb = json.loads((base / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]

    # cell 0: stamp the kernel start time, apply any overrides, print an identity line
    new0 = cells[0]
    for k, v in env_over.items():
        pat = re.compile(r'os\.environ\[\s*["\']%s["\']\s*\]\s*=\s*[^\n]*' % re.escape(k))
        line = 'os.environ["%s"] = "%s"' % (k, v)
        new0 = pat.sub(line, new0, count=1) if pat.search(new0) else new0.rstrip(NL) + NL + line + NL
    stamp = ('import time as _t0_time' + NL +
             'os.environ["BIOHUB_KERNEL_START_TS"] = str(_t0_time.time())' + NL +
             'os.environ.setdefault("BIOHUB_REPAIR_DEADLINE_S", "28800")' + NL +
             'os.environ.setdefault("BIOHUB_FRAME_CACHE_MAX_FRAMES", "48")' + NL)
    ident = ('print(' + Q + 'ARM_XENV tag=%s REPAIR_DEADLINE_S=%%s' % tag + Q
             + ' % (os.environ[' + Q + 'BIOHUB_REPAIR_DEADLINE_S' + Q + '],), flush=True)')
    compile(stamp + ident, "cell0add", "exec")
    cells[0] = new0.rstrip(NL) + NL + stamp + ident + NL

    # cell 5: definitions before filter_output_graph, guarded call site, bounded frame cache
    c5 = cells[5]
    if c5.count(DEF_ANCHOR) != 1:
        raise SystemExit("filter_output_graph anchor matched %d times" % c5.count(DEF_ANCHOR))
    if c5.count(ANCHOR) != 1:
        raise SystemExit("call-site anchor matched %d times" % c5.count(ANCHOR))
    c5 = c5.replace(DEF_ANCHOR, BLOCK.read_text(encoding="utf-8").lstrip(NL) + NL + DEF_ANCHOR, 1)
    c5 = c5.replace(ANCHOR, GUARDED, 1)
    # the two cache-write sites sit at DIFFERENT indentation (one inside a try block), so the
    # inserted call has to inherit each site's own indent or cell 5 will not compile
    def _trim_at(match):
        indent = match.group(1)
        return match.group(0) + indent + '_frame_cache_trim(frame_cache)' + NL
    c5, n_cache = re.subn(r'([ ]+)frame_cache\[t\] = frame' + NL, _trim_at, c5)
    cells[5] = c5
    print("  frame-cache trim inserted at %d site(s)" % n_cache)

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
    meta = json.loads((base / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = "eeshsaxena/biohub-v-" + tag
    meta["title"] = "biohub v " + tag
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest, "| base", base.name, "| env", env_over)


if __name__ == "__main__":
    main()
