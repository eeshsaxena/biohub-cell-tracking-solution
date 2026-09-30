#!/usr/bin/env python3
"""Env-only arms on OUR OWN 0.954 body (v_t6stk3), as insurance.

usage: python scratch_kernels/build_ourdiv.py <tag> KEY=VALUE [KEY=VALUE ...]

The division post-process is byte-identical between v_t6stk3 and the merged x138
body, so every division-gate delta we measure on one transfers as a hypothesis to
the other. These arms exist so that a losing merged body costs us a decision, not
a day: they are built but NOT pushed until the 09-24 scores say which body to use.
"""
import json, pathlib, re, sys

Q = chr(34)
ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"


def main():
    tag = sys.argv[1]
    env_over = {}
    for a in sys.argv[2:]:
        if "=" in a and not a.startswith("--"):
            k, v = a.split("=", 1)
            env_over[k] = v
    if not env_over:
        raise SystemExit("no env overrides given")

    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]

    new0 = cells[0]
    for k, v in env_over.items():
        pat = re.compile(r'os\.environ\[\s*["\']%s["\']\s*\]\s*=\s*[^\n]*' % re.escape(k))
        line = 'os.environ["%s"] = "%s"' % (k, v)
        new0 = pat.sub(line, new0, count=1) if pat.search(new0) else new0.rstrip(chr(10)) + chr(10) + line + chr(10)
        if new0.count(line) != 1:
            raise SystemExit("env override %s applied %d times" % (k, new0.count(line)))

    # cell 1 restates some constants and RAISES on drift; move both or the kernel dies there.
    new1 = cells[1]
    for k, v in env_over.items():
        anchor = '    "%s": ' % k
        if anchor in new1:
            i = new1.index(anchor)
            j = new1.index(chr(10), i)
            new1 = new1[:i] + '    "%s": %s,' % (k, float(v)) + new1[j:]
            print("  guard updated: %s -> %s" % (k, float(v)))

    keys = sorted(env_over)
    ident = ('print(' + Q + 'ARM_XENV tag=%s ' % tag + ' '.join(k + '=%s' for k in keys) + Q
             + ' % (' + ', '.join('os.environ[' + Q + k + Q + ']' for k in keys) + ',), flush=True)')
    compile(ident, "ident", "exec")
    new0 = new0.rstrip(chr(10)) + chr(10) + ident + chr(10)

    cells[0], cells[1] = new0, new1
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
