#!/usr/bin/env python3
"""t6stk3 with the sub-voxel Z offset computed by a different estimator (y/x unchanged: production SV gain 2).

usage: python scratch_kernels/build_t6svzest.py <tag> <estimator> <gain>
  estimator: line3 | line5 | line7 | box5 | box7 | parabolic | sigcom5 | sv27T<T> (3x3x3 softmax at temperature T)

Definitions match scratchpad/an/zstudy.py exactly (the offline study on production logit windows):
  lineK   : softmax over the K-slice column through the peak (centre y/x), mean z offset
  boxK    : per slice, logsumexp over the 3x3 y/x neighbourhood; softmax over K slices; mean z offset
  parabolic: 3-point parabolic peak fit on the centre column
  sigcom5 : sigmoid over the 5x3x3 window, summed per slice, centre of mass in z
  sv27T<T>: the production 3x3x3 softmax at temperature T (z component)
The z offset is multiplied by <gain>, zeroed at the first/last z slice (production edge rule), then clipped with the
production clip 0.4999. Windows are edge-padded like the capture (np.pad edge). Writes v_<tag> from v_t6stk3.
Runtime markers: ARM_SVZEST est=<name> gain=<g> (cell 4) and, per movie, the unchanged SV_ARM_HSG200 line.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
BASE = SK / "v_t6stk3"
NL = chr(10)

ENV_OLD = "os.environ['BIOHUB_SUBVOXEL_CLIP'] = '0.4999'\n"
HELPER_OLD = "    sa = sa * _sv_gain()\n    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n"
HELPER_NEW = (
    "    sa = sa * _sv_gain()\n"
    "    _zest = os.environ.get('BIOHUB_SVZ_EST', '')\n"
    "    if _zest:\n"
    "        sa[:, 0] = _svz_estimate(x, idx, _zest) * float(os.environ.get('BIOHUB_SVZ_GAIN', '1'))\n"
    "        sa[(idx[:, 0] == 0) | (idx[:, 0] == x.shape[0] - 1), 0] = 0.0\n"
    "    return np.clip(sa, -_SV_CLIP, _SV_CLIP).astype(np.float32)\n"
)
DEF_ANCHOR = "def _sv_softarg_offsets(lg, arr):\n"
ESTIMATOR_SRC = '''def _svz_softmax_mean(v, ax, T=1.0):
    v = v / T
    v = v - v.max(axis=1, keepdims=True)
    w = np.exp(v)
    w /= w.sum(axis=1, keepdims=True)
    return (w * ax[None, :]).sum(axis=1)


def _svz_estimate(x, idx, name):
    # z offset (grid voxels, before gain) from the logit volume x (Z,Y,X) at integer peaks idx (n,3)
    n = len(idx)
    if n == 0:
        return np.zeros(0, dtype=np.float64)
    pad = np.pad(np.asarray(x, dtype=np.float64), ((3, 3), (1, 1), (1, 1)), mode='edge')
    z, y, xx = idx[:, 0] + 3, idx[:, 1] + 1, idx[:, 2] + 1
    def col(dz):
        return pad[z + dz, y, xx]
    def box(dz):
        b = np.stack([pad[z + dz, y + a, xx + c] for a in (-1, 0, 1) for c in (-1, 0, 1)], 1)
        m = b.max(axis=1, keepdims=True)
        return (m[:, 0] + np.log(np.exp(b - m).sum(axis=1)))
    if name.startswith('line'):
        h = (int(name[4:]) - 1) // 2
        seg = np.stack([col(d) for d in range(-h, h + 1)], 1)
        return _svz_softmax_mean(seg, np.arange(-h, h + 1, dtype=np.float64))
    if name.startswith('box'):
        h = (int(name[3:]) - 1) // 2
        seg = np.stack([box(d) for d in range(-h, h + 1)], 1)
        return _svz_softmax_mean(seg, np.arange(-h, h + 1, dtype=np.float64))
    if name == 'parabolic':
        lm, l0, lp = col(-1), col(0), col(1)
        den = lm - 2 * l0 + lp
        return np.where(np.abs(den) > 1e-9, 0.5 * (lm - lp) / np.where(np.abs(den) > 1e-9, den, 1.0), 0.0)
    if name == 'sigcom5':
        sl = []
        for d in range(-2, 3):
            b = np.stack([pad[z + d, y + a, xx + c] for a in (-1, 0, 1) for c in (-1, 0, 1)], 1)
            sl.append((1.0 / (1.0 + np.exp(-b))).sum(axis=1))
        m = np.stack(sl, 1)
        return (m * np.arange(-2, 3)[None, :]).sum(axis=1) / m.sum(axis=1)
    if name.startswith('sv27T'):
        T = float(name[5:])
        v = np.stack([pad[z + a, y + b, xx + c] for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)], 1)
        return _svz_softmax_mean(v, np.repeat(np.array([-1.0, 0.0, 1.0]), 9), T)
    raise RuntimeError('SVZEST unknown estimator %r' % (name,))


'''


def main():
    tag, est, gain = sys.argv[1], sys.argv[2], float(sys.argv[3])
    ok_names = {"line3", "line5", "line7", "box5", "box7", "parabolic", "sigcom5"}
    if est not in ok_names and not est.startswith("sv27T"):
        raise SystemExit("unknown estimator " + est)
    nb = json.loads((BASE / "kernel.ipynb").read_text(encoding="utf-8"))
    cells = [("".join(c["source"]) if c["cell_type"] == "code" else None) for c in nb["cells"]]
    c4 = cells[4]
    for a in (ENV_OLD, HELPER_OLD, DEF_ANCHOR):
        if c4.count(a) != 1:
            raise SystemExit("anchor %r matched %d times" % (a[:60], c4.count(a)))
    c4 = c4.replace(ENV_OLD, ENV_OLD + "os.environ['BIOHUB_SVZ_EST'] = '%s'\nos.environ['BIOHUB_SVZ_GAIN'] = '%s'\n"
                    "print('ARM_SVZEST est=%s gain=%s (z offset estimator; y/x production SV gain 2)', flush=True)\n"
                    % (est, repr(gain), est, repr(gain)), 1)
    c4 = c4.replace(DEF_ANCHOR, ESTIMATOR_SRC + DEF_ANCHOR, 1).replace(HELPER_OLD, HELPER_NEW, 1)
    cells[4] = c4
    cells[0] = cells[0].rstrip(NL) + NL + 'print("ARM_XENV tag=%s SVZEST=%s ZGAIN=%s LCEFR=kept", flush=True)' % (tag, est, repr(gain)) + NL
    for i, c in enumerate(cells):
        if c is not None:
            compile(c, "%s:cell%d" % (tag, i), "exec")
    hs = c4.index('_SV_HELPER = """') + len('_SV_HELPER = """')
    helper = c4[hs:c4.index('"""', hs)]
    compile(helper, "sv_helper", "exec")
    if "_svz_estimate" not in helper or "BIOHUB_SVZ_EST" not in helper:
        raise SystemExit("helper patch missing")
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
    print("built", dest, "| est", est, "| gain", gain)


if __name__ == "__main__":
    main()
