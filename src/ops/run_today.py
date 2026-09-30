#!/usr/bin/env python3
"""Push, run, gate and submit a fixed list of arms from eeshsaxena's account.

usage:
  python ops/run_today.py plan.json            # real run
  python ops/run_today.py plan.json --dry      # validate only, pushes and submits nothing

plan.json: [{"tag": "stk3", "desc": "one-line submission description"}, ...]  (run in list order)

Rules it enforces:
  * at most 2 kernels running at once (Kaggle's per-account GPU session cap)
  * never more submissions than entries in the plan, and never a tag twice (sentinels in ops/state/)
  * a kernel is submitted ONLY if ops/gate.py prints GATE_PASS on its own log
  * a weekly-quota refusal stops everything and is reported, nothing is retried blindly
"""
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / "scratch_kernels"
STATE = ROOT / "ops" / "state"
COMP = "biohub-cell-tracking-during-development"
OWNER = "eeshsaxena"
LOGF = ROOT / "ops" / "run_today.log"

STATE.mkdir(parents=True, exist_ok=True)


def log(msg):
    line = f"[{time.strftime('%m-%d %H:%MZ', time.gmtime())}] {msg}"
    print(line, flush=True)
    with open(LOGF, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd, timeout=900):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, "\n".join(l for l in out.splitlines() if "urllib3" not in l and "Warning" not in l)


def sentinel(tag, name, text=""):
    (STATE / f"{tag}.{name}").write_text(text or time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime()), encoding="utf-8")


def has(tag, name):
    return (STATE / f"{tag}.{name}").exists()


def status(tag):
    _, out = run(["kaggle", "kernels", "status", f"{OWNER}/biohub-v-{tag}"], 300)
    m = re.search(r"KernelWorkerStatus\.(\w+)", out) or re.search(r'status "?(\w+)"?', out)
    return (m.group(1).upper() if m else "UNKNOWN"), out


def push(tag):
    rc, out = run([sys.executable, str(SK / "kaggle_push_safe.py"), str(SK / f"v_{tag}")], 900)
    return out


def validate(plan):
    ok = True
    gate_src = (ROOT / "ops" / "gate.py").read_text(encoding="utf-8")
    for item in plan:
        tag = item["tag"]
        d = SK / f"v_{tag}"
        meta = d / "kernel-metadata.json"
        if not (d / "kernel.ipynb").exists() or not meta.exists():
            log(f"DRY FAIL {tag}: folder incomplete"); ok = False; continue
        m = json.loads(meta.read_text())
        if m.get("id") != f"{OWNER}/biohub-v-{tag}":
            log(f"DRY FAIL {tag}: metadata id {m.get('id')!r}"); ok = False
        if m.get("is_private") is not True or m.get("enable_internet") is not False:
            log(f"DRY FAIL {tag}: must be private with internet off"); ok = False
        nb = json.loads((d / "kernel.ipynb").read_text(encoding="utf-8"))
        for i, c in enumerate(nb["cells"]):
            if c["cell_type"] == "code":
                compile("".join(c["source"]), f"{tag}:cell{i}", "exec")
        if f'"{tag}"' not in gate_src:
            if "--no-submit" in sys.argv:
                log(f"NOTE {tag}: no ops/gate.py entry yet. Fine for a run-only pass, but --submit-only will refuse it.")
            else:
                log(f"DRY FAIL {tag}: ops/gate.py has no entry for this tag, it would not be gated"); ok = False
        if not item.get("desc"):
            log(f"DRY FAIL {tag}: no submission description"); ok = False
        if has(tag, "SUBMITTED"):
            log(f"DRY NOTE {tag}: already SUBMITTED, will be skipped")
    log("DRY RESULT: " + ("ALL OK" if ok else "PROBLEMS FOUND"))
    return ok


def finish(tag, desc):
    out_dir = ROOT / "data" / f"out_{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    # `kaggle kernels output` returns the bundle WITHOUT the .log fairly often, and these arms
    # also ship a ~45 MB tracking_repo, so re-downloading a log we already have is both slow and
    # a fresh chance to lose it. ops/getlog.sh is the retry loop for the missing case.
    if not sorted(out_dir.glob("*.log")):
        run(["kaggle", "kernels", "output", f"{OWNER}/biohub-v-{tag}", "-p", str(out_dir)], 1800)
    else:
        log(f"{tag}: reusing the log already in {out_dir.name}, not re-downloading")
    logs = sorted(out_dir.glob("*.log"))
    if not logs:
        log(f"{tag}: no log downloaded, NOT submitting"); sentinel(tag, "NOLOG"); return
    rc, gout = run([sys.executable, str(ROOT / "ops" / "gate.py"), str(logs[0]), tag], 600)
    verdict = "GATE_PASS" if "GATE_PASS" in gout else "GATE_FAIL"
    log(f"{tag}: {verdict} | {gout.strip().splitlines()[-1][:200] if gout.strip() else ''}")
    if verdict != "GATE_PASS":
        sentinel(tag, "GATEFAIL", gout); return
    for v in (1, 2, 3):
        rc, sout = run(["kaggle", "competitions", "submit", COMP, "-k", f"{OWNER}/biohub-v-{tag}",
                        "-f", "submission.csv", "-v", str(v), "-m", desc], 1800)
        if "Successfully" in sout or "remaining" in sout.lower():
            sentinel(tag, "SUBMITTED", sout); log(f"{tag}: SUBMITTED v{v}: {sout.strip()[:160]}"); return
        if "Maximum" in sout or "limit" in sout.lower():
            log(f"{tag}: submission refused: {sout.strip()[:200]}"); sentinel(tag, "SUBREFUSED", sout); return
    log(f"{tag}: no submittable version found"); sentinel(tag, "SUBFAIL")


def main():
    plan = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    dry = "--dry" in sys.argv
    no_submit = "--no-submit" in sys.argv      # run + gate only, leave the slot unspent
    submit_only = "--submit-only" in sys.argv  # gate + submit kernels that already finished
    if not validate(plan):
        sys.exit(1)
    if dry:
        return
    if submit_only:
        for item in plan:
            tag = item["tag"]
            if has(tag, "SUBMITTED"):
                log(f"{tag}: already SUBMITTED, skipping"); continue
            st, _ = status(tag)
            if st != "COMPLETE":
                log(f"{tag}: status {st}, not COMPLETE, skipping"); continue
            finish(tag, item["desc"])
        return
    queue = [p for p in plan if not has(p["tag"], "SUBMITTED")]
    flight = {}
    while queue or flight:
        # start work while under the 2-session cap
        while queue and len(flight) < 2:
            item = queue[0]
            tag = item["tag"]
            if has(tag, "PUSHED"):
                flight[tag] = item; queue.pop(0); continue
            out = push(tag)
            if "successfully pushed" in out.lower():
                sentinel(tag, "PUSHED", out); log(f"{tag}: pushed"); flight[tag] = item; queue.pop(0)
            elif "weekly gpu quota" in out.lower():
                log(f"STOP: weekly GPU quota reached while pushing {tag}: {out.strip()[:200]}"); sys.exit(2)
            elif "session count" in out.lower():
                log(f"{tag}: 2-session cap hit, waiting"); break
            else:
                log(f"{tag}: push failed: {out.strip()[:300]}"); sentinel(tag, "PUSHFAIL", out); queue.pop(0)
        time.sleep(90)
        for tag in list(flight):
            st, raw = status(tag)
            if st == "COMPLETE":
                sentinel(tag, "COMPLETE"); log(f"{tag}: COMPLETE")
                item = flight.pop(tag)
                if no_submit:
                    log(f"{tag}: --no-submit, leaving it unsubmitted (gate + submit later with --submit-only)")
                else:
                    finish(tag, item["desc"])
            elif st in ("ERROR", "CANCEL_ACKNOWLEDGED", "CANCEL_REQUESTED"):
                sentinel(tag, "ERROR", raw); log(f"{tag}: {st}, not submitting (no slot used)"); flight.pop(tag)
    log("ALL DONE")


if __name__ == "__main__":
    main()
