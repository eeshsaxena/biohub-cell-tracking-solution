import json
from pathlib import Path
HERE = Path(__file__).resolve().parent

probe = r'''
import torch, subprocess, sys
print("torch", torch.__version__, "| cuda build:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    print("capability sm_", torch.cuda.get_device_capability(0))
    print("torch arch list:", torch.cuda.get_arch_list())
    try:
        x = torch.randn(8, 8, device="cuda")
        y = (x @ x).sum().item()
        print("cuda matmul OK:", round(y, 3))
    except Exception as e:
        print("cuda op FAILED:", type(e).__name__, str(e)[:200])
print("---- nvidia-smi ----")
try:
    print(subprocess.run(["nvidia-smi","--query-gpu=name,driver_version,compute_cap",
                          "--format=csv,noheader"], capture_output=True, text=True).stdout)
except Exception as e:
    print("smi err", e)
'''
compile(probe, "<p>", "exec")
nb = {"cells":[{"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
                "source":probe.splitlines(keepends=True)}],
      "metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},
                  "language_info":{"name":"python","version":"3.11"}},
      "nbformat":4,"nbformat_minor":5}
out = HERE/"gpuprobe"/"biohub-gpu-probe.ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(out,"w"), indent=1)
meta={"id":"eeshsaxena/biohub-gpu-probe","title":"biohub gpu probe",
      "code_file":"biohub-gpu-probe.ipynb","language":"python","kernel_type":"notebook",
      "is_private":True,"enable_gpu":True,"enable_tpu":False,"enable_internet":False,
      "keywords":[],"dataset_sources":[],"kernel_sources":[],
      "competition_sources":[],"model_sources":[]}
json.dump(meta, open(HERE/"gpuprobe"/"kernel-metadata.json","w"), indent=2)
print("wrote", out)
