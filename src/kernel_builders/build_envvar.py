"""Build an hfusion variant with ONE env value changed. usage: build_envvar.py <tag> <ENV_NAME> <old> <new> [note]"""
import json, shutil, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
tag, name, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
note = sys.argv[5] if len(sys.argv) > 5 else ""
OLD = f'os.environ["{name}"] = "{old}"'
NEW = f'os.environ["{name}"] = "{new}"' + (f'  # {tag}: {note}' if note else f'  # {tag}')
kdir = HERE / f"v_{tag}"
if kdir.exists():
    shutil.rmtree(kdir)
kdir.mkdir()
nb = json.loads((HERE / "v_hfusion" / "kernel.ipynb").read_text(encoding="utf-8"))
hits = 0
for cell in nb["cells"]:
    src = "".join(cell["source"])
    if OLD in src:
        hits += src.count(OLD)
        cell["source"] = src.replace(OLD, NEW).splitlines(keepends=True)
if hits != 1:
    sys.exit(f"expected exactly 1 occurrence of {OLD}, found {hits}")
(kdir / "kernel.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
meta = json.loads((HERE / "v_hfusion" / "kernel-metadata.json").read_text())
meta["id"] = f"eeshsaxena/biohub-v-{tag}"
meta["title"] = f"biohub v {tag}"
(kdir / "kernel-metadata.json").write_text(json.dumps(meta, indent=2))
body = "".join("".join(c["source"]) for c in nb["cells"])
print(f"{tag}: patched {hits}x | new present: {NEW in body} | old gone: {OLD not in body}")
