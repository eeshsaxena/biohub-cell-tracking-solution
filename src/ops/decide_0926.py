#!/usr/bin/env python3
"""Apply the 09-26 decision table to today's three scores and print the actions (read-only; submits nothing).

usage: python ops/decide_0926.py            (reads the live submission list via the kaggle CLI)
       python ops/decide_0926.py 0.952 0.953 0.950   (ourvz t6svz15 t6svz0yx, for dry runs)

Rules (HANDOFF 09-26 04:00Z + 05:15Z):
  slot 4:  ourvz >= 0.952 -> ourvzl;  ourvz == 0.951 -> ourvzl only if t6svz0yx >= 0.952;  ourvz <= 0.950 -> hold
  ourvz15: only if t6svz15 >= 0.955 and ourvz >= 0.954 (needs a gate entry + plan first)
  pick B:  any of ourvz / t6svz0yx / t6svz15 reading >= 0.954 replaces t65s3, most diverse first among the best
           score (match-based edge difference vs t6r70: ourvz 5.2%, t6svz0yx 4.4%, t6svz15 1.6%, t65s3 1.9%)
"""
import subprocess
import sys

IDS = {"56567062": "ourvz", "56567638": "t6svz15", "56567694": "t6svz0yx"}
DIVERSITY = {"ourvz": 0.052, "t6svz0yx": 0.044, "t6svz15": 0.016, "t65s3": 0.019}
SUB_ID = {"ourvz": "56567062", "t6svz15": "56567638", "t6svz0yx": "56567694", "t65s3": "56496604"}


def live_scores():
    out = subprocess.run(["kaggle", "competitions", "submissions", "biohub-cell-tracking-during-development"],
                         capture_output=True, text=True, timeout=120).stdout
    sc = {}
    for line in out.splitlines():
        parts = line.split()
        if parts and parts[0] in IDS:
            status = [p for p in parts if p.startswith("SubmissionStatus.")]
            val = parts[-1]
            if status and status[0].endswith("COMPLETE"):
                sc[IDS[parts[0]]] = float(val)
            else:
                sc[IDS[parts[0]]] = None
    return sc


def main():
    if len(sys.argv) == 4:
        sc = dict(zip(["ourvz", "t6svz15", "t6svz0yx"], map(float, sys.argv[1:])))
    else:
        sc = live_scores()
    print("scores:", sc)
    if any(v is None for v in sc.values()) or len(sc) < 3:
        print("NOT ALL SCORED YET - no decision.")
        return
    o, z15, z0 = sc["ourvz"], sc["t6svz15"], sc["t6svz0yx"]
    r = lambda v: round(v, 3)
    # slot 4
    if r(o) >= 0.952 or (r(o) == 0.951 and r(z0) >= 0.952):
        print("SLOT 4 -> submit ourvzl:  python ops/run_today.py ops/plan_ourvzl.json --submit-only")
    else:
        print("SLOT 4 -> HOLD ourvzl (the z value does not transfer through V1284 y/x on this body).")
    if r(z15) >= 0.955 and r(o) >= 0.954:
        print("ALSO: ourvz15 is justified (z gain 3 + V1284 y/x) - add its gate entry + plan, run, submit in slot 5.")
    # pick B
    cands = [(v, DIVERSITY[k], k) for k, v in (("ourvz", o), ("t6svz15", z15), ("t6svz0yx", z0)) if r(v) >= 0.954]
    if cands:
        best = max(cands, key=lambda c: (round(c[0], 3), c[1]))
        print(f"PICK B -> {best[2]} ({SUB_ID[best[2]]}, public {best[0]:.3f}, diversity {best[1]:.1%}) replaces t65s3 (56496604).")
        if r(best[0]) >= 0.955:
            print("   It reads >= 0.955: run python ops/watch/rep_check.py - if the representative flips to it, it becomes PICK A too.")
    else:
        print("PICK B -> unchanged: t65s3 (56496604). Pick A unchanged: t6r70 (56483584).")
    # what the numbers mean
    print(f"z-dose reading: t6svz15 {z15:.3f} vs t6stk3 0.954 ; y/x value: t6stk3 0.954 - t6svz0yx {z0:.3f} = {0.954 - z0:+.3f}")


if __name__ == "__main__":
    main()
