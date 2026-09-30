"""Assemble the Kaggle tune kernel with a clean, compile-checked run cell."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

nb = json.load(open(ROOT / "kaggle" / "biohub_tune.ipynb"))

run_cell = [
    "# Install zarr OFFLINE from the shipped wheel dataset. Self-diagnosing: on\n",
    "# failure it prints the mount path, the wheels present, and the full pip log.\n",
    "import os, glob, subprocess, sys\n",
    'print("INPUT MOUNTS:", os.listdir("/kaggle/input"))\n',
    '_whls = glob.glob("/kaggle/input/**/zarr-*.whl", recursive=True)\n',
    'wd = os.path.dirname(_whls[0]) if _whls else "/kaggle/input/biohub-zarr-wheels"\n',
    'print("wheeldir:", wd, "| zarr wheel found:", bool(_whls))\n',
    'r = subprocess.run([sys.executable, "-m", "pip", "install", "--no-index",\n',
    '                    f"--find-links={wd}", "zarr"],\n',
    "                   capture_output=True, text=True)\n",
    'print("pip rc:", r.returncode)\n',
    'if r.returncode != 0:\n',
    '    print("PIP STDOUT:\\n", r.stdout[-2500:])\n',
    '    print("PIP STDERR:\\n", r.stderr[-2500:])\n',
    "import zarr\n",
    'print("zarr", zarr.__version__, "installed offline from", wd)\n',
    "\n",
    "from pathlib import Path\n",
    "\n",
    "def find_data_root():\n",
    '    slug = "biohub-cell-tracking-during-development"\n',
    '    for c in (Path(f"/kaggle/input/competitions/{slug}"),\n',
    '              Path(f"/kaggle/input/{slug}")):\n',
    '        if (c / "test").exists() or (c / "train").exists():\n',
    "            return c\n",
    '    for p in Path("/kaggle/input").rglob("test"):\n',
    '        if p.is_dir() and any(p.glob("*.zarr")):\n',
    "            return p.parent\n",
    '    raise RuntimeError("competition data root not found")\n',
    "\n",
    "DATA = find_data_root()\n",
    'print("data root:", DATA)\n',
    "\n",
    "# FIRST REAL-DATA RUN: lean and fast, to confirm the pipeline works on real\n",
    "# pixels and get a first per-embryo number before the deep 6 h sweep.\n",
    'base = Config(mode="tune", device="cuda", verbose=True, max_per_frame=2000)\n',
    "\n",
    "best = autotune(\n",
    '    DATA / "train",\n',
    "    base,\n",
    "    n_per_embryo=2,\n",
    "    detection_grid=[\n",
    '        {"min_sep_um": ms, "peak_min_frac": pf}\n',
    "        for ms in (6.5, 8.0, 10.0, 12.0)\n",
    "        for pf in (0.08, 0.20)\n",
    "    ],\n",
    "    linking_grid=[\n",
    '        {"max_gap": g, "link_radius_um": r, "motion_compensate": mc}\n',
    "        for g in (0, 1, 2)\n",
    "        for r in (5.5, 7.0)\n",
    "        for mc in (True, False)\n",
    "    ],\n",
    "    budget_s=3600,\n",
    ")\n",
    "print()\n",
    'print("FIRST REAL NUMBER (worst embryo selects). Chosen config:")\n',
    'for k in ("sigmas_um", "min_sep_um", "peak_min_frac", "max_gap",\n',
    '          "link_radius_um", "gap_radius_um", "motion_compensate"):\n',
    '    print("    %s=%r," % (k, getattr(best, k)))\n',
]
nb["cells"][-1]["source"] = run_cell

# Compile-check every code cell before we ever push.
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code":
        compile("".join(c["source"]), f"<cell {i}>", "exec")
print("all code cells compile")

out = HERE / "new" / "biohub-cell-tracking-tune.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out, "w"), indent=1)

meta = {
    "id": "eeshsaxena/biohub-cell-tracking-tune",
    "title": "Biohub Cell Tracking Tune",
    "code_file": "biohub-cell-tracking-tune.ipynb",
    "language": "python", "kernel_type": "notebook",
    "is_private": True, "enable_gpu": True, "enable_tpu": False,
    "enable_internet": False,
    # Force T4 (sm_75). The default P100 (sm_60) is unsupported by the base
    # image's torch 2.10 (arch list sm_70..sm_120), which raises
    # cudaErrorNoKernelImageForDevice on every CUDA op.
    "machine_shape": "NvidiaTeslaT4",
    "keywords": [],
    "dataset_sources": ["eeshsaxena/biohub-zarr-wheels"],
    "kernel_sources": [],
    "competition_sources": ["biohub-cell-tracking-during-development"],
    "model_sources": [],
}
json.dump(meta, open(HERE / "new" / "kernel-metadata.json", "w"), indent=2)
print("wrote", out)
