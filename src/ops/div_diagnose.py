#!/usr/bin/env python3
"""Why does every arm we hold score divJ = 0?

For each of the THREE annotated divisions on the scored movies, report which of the
official score_divisions conditions fails:
  (a) >=1 matched pred node at a timepoint in the GT one-node (pre-split) stage
  (b) the same weakly-connected pred component covers >=2 daughter lineages
  (c) that component contains a pred fork (out-degree >= 2) anywhere in it
"""
import os
import sys
from collections import defaultdict, deque

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score_official import gt, read_sub, assign, SCALE, MATCH_UM, ROOT  # noqa: E402


def diag(tag, sample="6bba_05db0fb1"):
    nodes, edges = read_sub(f"{ROOT}/data/out_{tag}/submission.csv")
    pnodes, pedges = nodes[sample], edges[sample]
    gpos, gtof, gedges, n_est = gt(sample)
    pr_by_t = defaultdict(list)
    for i, v in pnodes.items():
        pr_by_t[v[0]].append(i)
    g_out, g_succ, g_pred = defaultdict(int), defaultdict(list), defaultdict(list)
    for a, b in gedges:
        g_out[a] += 1
        g_succ[a].append(b)
        g_pred[b].append(a)
    pe = set(pedges)
    p_succ, p_pred, out_deg = defaultdict(list), defaultdict(list), defaultdict(int)
    for s, t in pe:
        p_succ[s].append(t)
        p_pred[t].append(s)
        out_deg[s] += 1
    forks = {s for s, c in out_deg.items() if c >= 2}
    print(f"\n### {tag} / {sample}: {len(forks)} predicted forks on this movie")

    for dv in [a for a, c in g_out.items() if c >= 2]:
        children = g_succ[dv]
        keep = set(g_pred.get(dv, [])) | {dv} | set(children)
        for c in children:
            keep |= set(g_succ.get(c, []))
        sub = sorted(keep)
        cnt = defaultdict(int)
        for i in sub:
            cnt[gtof[i]] += 1
        one_node_times = {t for t, c in cnt.items() if c == 1}
        keepset = set(sub)
        lineages = []
        for c in children:
            seen, stack = {c}, [c]
            while stack:
                for nx in g_succ.get(stack.pop(), []):
                    if nx in keepset and nx not in seen:
                        seen.add(nx)
                        stack.append(nx)
            lineages.append(seen)
        m = assign(sub, gpos, gtof, pnodes, pr_by_t)
        mn = {v: k for k, v in m.items()}
        print(f"\n GT division node {dv} at t={gtof[dv]}  subgraph nodes={len(sub)} "
              f"one_node_times={sorted(one_node_times)}  daughters={len(children)}")
        print(f"   GT subgraph ids/t: {[(i, gtof[i]) for i in sub]}")
        print(f"   matched {len(m)}/{len(sub)} of the subgraph: "
              f"{[(g, gtof[g], p) for g, p in m.items()]}")
        # components
        remaining = set(mn)
        k = 0
        while remaining:
            seed = next(iter(remaining))
            visited, q, comp = {seed}, deque([seed]), {seed}
            while q:
                cur = q.popleft()
                for nb in p_succ.get(cur, []) + p_pred.get(cur, []):
                    if nb not in visited:
                        visited.add(nb)
                        q.append(nb)
                        if nb in remaining:
                            comp.add(nb)
            remaining -= comp
            k += 1
            has_one = any(pnodes[p][0] in one_node_times for p in comp)
            mg = {mn[p] for p in comp}
            cov = sum(1 for lin in lineages if lin & mg)
            nf = len(visited & forks)
            print(f"   comp{k}: {len(comp)} matched pred nodes, component size {len(visited)}, "
                  f"covers_one_node_stage={has_one} daughter_lineages={cov}/2 forks_in_component={nf} "
                  f"-> {'CANDIDATE' if (has_one and cov >= 2 and nf) else 'FAIL'}")
        # how far is the nearest pred node to each GT node of the subgraph
        for i in sub:
            pids = pr_by_t.get(gtof[i], [])
            if not pids:
                continue
            P = np.stack([np.array(pnodes[p][1:]) * SCALE for p in pids])
            d = np.linalg.norm(P - gpos[i], axis=1)
            k2 = int(np.argmin(d))
            print(f"     gt {i} t={gtof[i]}: nearest pred {pids[k2]} at {d[k2]:.2f} um "
                  f"({'MATCHED' if i in m else 'unmatched'})")


for tag in sys.argv[1:] or ["t6stk3"]:
    diag(tag)
