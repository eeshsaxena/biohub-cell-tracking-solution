#!/usr/bin/env python3
"""ourv with the V1284 head RETRAINED on ~60 train movies (output of eeshsaxena/biohub-v-v1284cap).

usage: python scratch_kernels/build_ourvr.py <tag> [--base v_ourv|v_ourvg15|...]

WHY. The public head was fitted on 20 movies (4,136 pairs) and its author recorded that volume was
the bottleneck: a 4-movie version was 14.9% WORSE, the 20-movie one 10.8% better. v1284cap captures
the same features on ~60 train movies (placeholders excluded) and refits the head in the identical
format with movie-held-out CV against the public head. This arm changes ONLY which head file loads.

The head arrives through kernel_sources (the capture notebook's /kaggle/working output), so the
notebook requires exactly one v1284_head_retrained.pt under /kaggle/input, checks its format against
the module's make_head(), prints its sha256, and raises if the public head would be loaded instead.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
NL = chr(10)
CAP_KERNEL = "eeshsaxena/biohub-v-v1284cap"

OLD_MOUNT = "_myhead = sorted(Path('/kaggle/input').rglob('biohub-v1284-head-s075/v1284_head.pt'))"
NEW_MOUNT = "_myhead = sorted(Path('/kaggle/input').rglob('v1284_head_retrained.pt'))"
HEAD_SET = "os.environ['V1284_HEAD']=str(_myhead[0])"
HEAD_CHECK = NL.join([
    HEAD_SET,
    "import hashlib as _v1284r_hl, torch as _v1284r_torch",
    "if 'biohub-v1284-head-s075' in str(_myhead[0]): raise RuntimeError('V1284R would load the PUBLIC head')",
    "_v1284r_saved = _v1284r_torch.load(str(_myhead[0]), map_location='cpu', weights_only=True)",
    "if set(_v1284r_saved) < {'state_dict', 'mean', 'scale'}: raise RuntimeError(('V1284R head format', sorted(_v1284r_saved)))",
    "_v1284r_shapes = {k: tuple(v.shape) for k, v in _v1284r_saved['state_dict'].items()}",
    "if _v1284r_shapes != {'0.weight': (32, 224), '0.bias': (32,), '2.weight': (3, 32), '2.bias': (3,)}: raise RuntimeError(('V1284R head shapes', _v1284r_shapes))",
    "print('ARM_V1284R head=retrained path=%s sha256=%s' % (_myhead[0], _v1284r_hl.sha256(open(_myhead[0], 'rb').read()).hexdigest()[:16]), flush=True)",
])


def main():
    tag = sys.argv[1]
    base = SK / "v_ourv"
    if "--base" in sys.argv:
        base = SK / sys.argv[sys.argv.index("--base") + 1]
    nb = json.loads((base / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]

    c4 = cells[4]
    for a in (OLD_MOUNT, HEAD_SET):
        if c4.count(a) != 1:
            raise SystemExit("anchor %r matched %d times" % (a, c4.count(a)))
    c4 = c4.replace(OLD_MOUNT, NEW_MOUNT, 1).replace(HEAD_SET, HEAD_CHECK, 1)
    cells[4] = c4

    c0 = cells[0]
    lines = c0.split(NL)
    idx = [i for i, l in enumerate(lines) if l.startswith('print("ARM_XENV tag=')]
    if len(idx) != 1:
        raise SystemExit("identity line count %d" % len(idx))
    old = lines[idx[0]]
    lines[idx[0]] = old.replace('ARM_XENV tag=', 'ARM_XENV tag=%s V1284R=retrained base=' % tag, 1)
    cells[0] = NL.join(lines)

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
    meta["kernel_sources"] = sorted(set(meta.get("kernel_sources", []) + [CAP_KERNEL]))
    json.dump(meta, open(dest / "kernel-metadata.json", "w", encoding="utf-8"), indent=2)
    print("built", dest, "| base", base.name, "| kernel_sources", meta["kernel_sources"])
    print("  identity:", lines[idx[0]])


if __name__ == "__main__":
    main()
