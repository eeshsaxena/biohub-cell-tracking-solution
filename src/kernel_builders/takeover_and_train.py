#!/usr/bin/env python3
"""Wait until the biohub training data is actually on the box, THEN take the V100:
  1. record the exact cmdlines of the GPU jobs into ~/biohub/restore_jobs.sh (so Eesh can relaunch)
  2. stop them
  3. launch the detector training (fine: downsample 1,2,2)
Never kills anything until the data is verified present - no point evicting jobs for nothing.
"""
import subprocess, time, pathlib

ROOT = pathlib.Path(r"C:\Users\eeshs\Downloads\biohub-cell-tracking")
LOG = ROOT / "takeover.log"; VERD = ROOT / "takeover.VERDICT.txt"
BOX = "training@192.168.10.30"
MIN_MOVIES = 15          # require at least this many .zarr on the box before evicting anything

def log(x):
    l = f"[{time.strftime('%H:%M:%SZ', time.gmtime())}] {x}"
    print(l, flush=True); open(LOG, "a", encoding="utf-8").write(l + "\n")
def ssh(cmd, t=300):
    p = subprocess.run(f'ssh -o BatchMode=yes -o ConnectTimeout=20 {BOX} "{cmd}"',
                       shell=True, capture_output=True, text=True, timeout=t)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

def movies_on_box():
    rc, o = ssh("ls -d ~/biohub/data/train/*.zarr 2>/dev/null | wc -l")
    try: return int(o.strip().splitlines()[-1])
    except Exception: return 0

def main():
    log("=== takeover: waiting for data on box ===")
    for i in range(240):                      # up to ~8h
        n = movies_on_box()
        if n >= MIN_MOVIES:
            log(f"data ready: {n} movies on box"); break
        if i % 10 == 0: log(f"  waiting... {n} movies on box")
        time.sleep(120)
    else:
        VERD.write_text("timed out waiting for data; nothing was killed\n"); return

    # 1. save restore script BEFORE touching anything
    save = (
      "OUT=~/biohub/restore_jobs.sh; echo '#!/usr/bin/env bash' > $OUT; "
      "echo '# Auto-saved by Claude before taking the V100 for biohub detector training.' >> $OUT; "
      "echo '# Re-run these to resume the jobs that were stopped.' >> $OUT; "
      "for p in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader); do "
      "  cwd=$(readlink -f /proc/$p/cwd 2>/dev/null); "
      "  cmd=$(tr '\\0' ' ' < /proc/$p/cmdline 2>/dev/null); "
      "  if [ -n \\\"$cmd\\\" ]; then echo \\\"( cd $cwd && nohup $cmd > ~/restore_$p.log 2>&1 & )\\\" >> $OUT; fi; "
      "done; chmod +x $OUT; cat $OUT"
    )
    rc, o = ssh(save)
    log("restore script saved:\n" + o[:600])

    # 2. stop the GPU jobs
    rc, o = ssh("for p in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader); do kill $p 2>/dev/null; done; sleep 12; "
                "for p in $(nvidia-smi --query-compute-apps=pid --format=csv,noheader); do kill -9 $p 2>/dev/null; done; sleep 8; "
                "nvidia-smi --query-gpu=memory.used --format=csv,noheader")
    log(f"after stop, GPU mem used: {o.strip()[-40:]}")

    # 3. launch training
    rc, o = ssh("cd ~/biohub && ./box_train_detector.sh fine 30 0")
    log(f"train launch rc={rc}: {o.strip()[:300]}")
    time.sleep(90)
    rc, o = ssh("tail -12 ~/biohub/runs/train_fine.log 2>/dev/null; nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader")
    log("early training output:\n" + o[:900])
    VERD.write_text(f"TAKEOVER DONE\nrestore: ssh {BOX} '~/biohub/restore_jobs.sh'\n\n{o[:900]}\n")
    log("=== DONE ===")

if __name__ == "__main__":
    main()
