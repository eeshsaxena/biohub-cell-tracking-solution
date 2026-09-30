#!/usr/bin/env python3
"""ourv with a PER-EMBRYO V1284 head mapping (heads embedded in the notebook as base64).

usage: python scratch_kernels/build_ourvm.py <tag> 44b6=<head.pt> 6bba=<head.pt> [default=<head.pt>] [--gain G]

WHY. The capture run (v1284cap) showed the head retrained on 60 train movies beats the public head on 6bba
(1.102 vs 1.408 um held-out) but LOSES to it on 44b6 (1.211 vs 1.111), because 6bba supplies ~85% of the
pairs. Every movie stem starts with its embryo id (44b6_ / 6bba_), so the refinement module can pick a head
per embryo. This builder embeds the chosen head files in the notebook (34 KB each), writes them to
/kaggle/working/v1284m/ at runtime, and patches the module's refine() to look the head up by stem prefix.

The base is v_ourv. The public head is still mounted (the notebook's own check needs it) but never loaded:
the module reads V1284_HEAD_MAP, not V1284_HEAD, and prints which head it loads for each prefix.
"""
import base64
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_ourv"
NL = chr(10)
BS = chr(92)
Q1 = BS + "'"   # an escaped single quote inside the module's string literal
LN = BS + "n"   # an escaped newline inside the module's string literal

# module-literal anchors (the module is a single-line string literal in cell 4; quotes and newlines are escaped)
MOD_IMPORT_OLD = "import os" + LN + "from pathlib import Path" + LN
MOD_IMPORT_NEW = "import os" + LN + "import json" + LN + "from pathlib import Path" + LN
MOD_CACHE_OLD = (
    "    if _CACHE is None:" + LN +
    "        saved = torch.load(os.environ[" + Q1 + "V1284_HEAD" + Q1 + "], map_location=" + Q1 + "cpu" + Q1 + ", weights_only=True)" + LN +
    "        head = make_head().to(feature.device)" + LN +
    "        head.load_state_dict(saved[" + Q1 + "state_dict" + Q1 + "]); head.eval()" + LN +
    "        _CACHE = (head, saved[" + Q1 + "mean" + Q1 + "].to(feature.device), saved[" + Q1 + "scale" + Q1 + "].to(feature.device))" + LN +
    "    head, mean, scale = _CACHE" + LN
)
MOD_CACHE_NEW = (
    "    if _CACHE is None:" + LN +
    "        _CACHE = {}" + LN +
    "    _pfx = ds_path.stem[:4]" + LN +
    "    if _pfx not in _CACHE:" + LN +
    "        _map = json.loads(os.environ[" + Q1 + "V1284_HEAD_MAP" + Q1 + "])" + LN +
    "        _hp = _map.get(_pfx, _map.get(" + Q1 + "default" + Q1 + "))" + LN +
    "        if _hp is None: raise RuntimeError(" + Q1 + "V1284M no head for prefix " + Q1 + " + _pfx)" + LN +
    "        saved = torch.load(_hp, map_location=" + Q1 + "cpu" + Q1 + ", weights_only=True)" + LN +
    "        head = make_head().to(feature.device)" + LN +
    "        head.load_state_dict(saved[" + Q1 + "state_dict" + Q1 + "]); head.eval()" + LN +
    "        _CACHE[_pfx] = (head, saved[" + Q1 + "mean" + Q1 + "].to(feature.device), saved[" + Q1 + "scale" + Q1 + "].to(feature.device))" + LN +
    "        print(" + Q1 + "V1284M prefix" + Q1 + ", _pfx, " + Q1 + "head" + Q1 + ", _hp, flush=True)" + LN +
    "    head, mean, scale = _CACHE[_pfx]" + LN
)
SHIFT_OLD = "shift = bounded(head, (x-mean)/scale).cpu().numpy() / SPACING"
SHIFT_NEW = SHIFT_OLD + " * float(os.environ.get(" + Q1 + "V1284_GAIN" + Q1 + ", " + Q1 + "1.0" + Q1 + "))"
CHECK_OLD = "> 2.00001:"
CHECK_NEW = "> 2.00001 * max(1.0, float(os.environ.get(" + Q1 + "V1284_GAIN" + Q1 + ", " + Q1 + "1.0" + Q1 + "))):"
HEAD_SET = "os.environ['V1284_HEAD']=str(_myhead[0])"
PATCHED = "print('V1284 head patched AFTER the readmit dump patch; mode =', os.environ['V1284_MODE'])"
OLD_IDENT = 'print("ARM_XENV tag=ourv V1284_HEAD=mounted SUBVOXEL=removed", flush=True)'


def main():
    tag = sys.argv[1]
    gain = 1.0
    args = sys.argv[2:]
    if "--gain" in args:
        i = args.index("--gain")
        gain = float(args[i + 1])
        args = args[:i] + args[i + 2:]
    heads = {}
    for a in args:
        k, v = a.split("=", 1)
        heads[k] = pathlib.Path(v)
    if not {"44b6", "6bba"} <= set(heads):
        raise SystemExit("need 44b6=<pt> and 6bba=<pt>")
    blobs, shas = {}, {}
    for k, p in heads.items():
        b = p.read_bytes()
        blobs[k] = base64.b64encode(b).decode("ascii")
        shas[k] = hashlib.sha256(b).hexdigest()[:16]

    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    c4 = cells[4]
    for a in (MOD_IMPORT_OLD, MOD_CACHE_OLD, SHIFT_OLD, CHECK_OLD, HEAD_SET, PATCHED):
        if c4.count(a) != 1:
            raise SystemExit("anchor %r matched %d times" % (a[:60], c4.count(a)))
    c4 = c4.replace(MOD_IMPORT_OLD, MOD_IMPORT_NEW, 1).replace(MOD_CACHE_OLD, MOD_CACHE_NEW, 1)
    c4 = c4.replace(SHIFT_OLD, SHIFT_NEW, 1).replace(CHECK_OLD, CHECK_NEW, 1)
    map_lines = [
        HEAD_SET,
        "import base64 as _v1284m_b64, hashlib as _v1284m_hl",
        "_v1284m_dir = Path('/kaggle/working/v1284m'); _v1284m_dir.mkdir(parents=True, exist_ok=True)",
        "_v1284m_blobs = " + repr(blobs),
        "_v1284m_expect = " + repr(shas),
        "_v1284m_map = {}",
        "for _k, _b in _v1284m_blobs.items():",
        "    _raw = _v1284m_b64.b64decode(_b)",
        "    if _v1284m_hl.sha256(_raw).hexdigest()[:16] != _v1284m_expect[_k]: raise RuntimeError('V1284M head blob corrupt ' + _k)",
        "    _p = _v1284m_dir / ('v1284_head_' + _k + '.pt'); _p.write_bytes(_raw); _v1284m_map[_k] = str(_p)",
        "    _s = torch.load(str(_p), map_location='cpu', weights_only=True)",
        "    if {tuple(v.shape) for v in _s['state_dict'].values()} != {(32, 224), (32,), (3, 32), (3,)}: raise RuntimeError('V1284M head shapes ' + _k)",
        "os.environ['V1284_HEAD_MAP'] = json.dumps(_v1284m_map)",
        "os.environ['V1284_GAIN'] = %r" % repr(gain),
        "print('ARM_V1284M map=' + ','.join(k + ':' + _v1284m_expect[k] for k in sorted(_v1284m_expect)) + ' gain=' + os.environ['V1284_GAIN'], flush=True)",
    ]
    c4 = c4.replace(HEAD_SET, NL.join(map_lines), 1)
    c4 = c4.replace(PATCHED, PATCHED + NL
                    + "_v1284m_src = (_ps.parent/'v1284_coordinate_refinement.py').read_text()" + NL
                    + "if _v1284m_src.count('V1284_HEAD_MAP') != 1 or _v1284m_src.count('V1284_GAIN') != 2: raise RuntimeError('V1284M module patch missing')" + NL
                    + "print('ARM_V1284M module_patched=1', flush=True)", 1)
    cells[4] = c4
    c0 = cells[0]
    if c0.count(OLD_IDENT) != 1:
        raise SystemExit("identity line not found")
    cells[0] = c0.replace(OLD_IDENT, 'print("ARM_XENV tag=%s V1284M=%s V1284_HEAD=mounted SUBVOXEL=removed V1284_GAIN=%s", flush=True)'
                          % (tag, ",".join(k + ":" + shas[k] for k in sorted(shas)), repr(gain)), 1)
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    start = c4.index("write_text('") + len("write_text(")
    end = c4.index("')" + NL, start) + 1
    module_src = eval(c4[start:end])
    compile(module_src, "v1284_coordinate_refinement.py", "exec")
    if "V1284_HEAD_MAP" not in module_src or "_CACHE[_pfx]" not in module_src:
        raise SystemExit("module patch not in the written source")
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
    print("built", dest, "| heads", {k: (str(v), shas[k]) for k, v in heads.items()}, "| gain", gain)


if __name__ == "__main__":
    main()
