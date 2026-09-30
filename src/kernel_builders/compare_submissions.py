"""Compare two submission.csv files: exact hash, per-dataset node/edge counts, and a ROW-EXACT content check.

FAST_OK rule, TIGHTENED 2026-09-18: two files are "the same submission" only when they are byte-identical, or
identical in content once the purely positional `id` column is dropped. The old rule ("every per-dataset node/edge
count within 0.2%") is NOT sufficient evidence of equality: hsoft differed from hfusion on only 0.2-0.6% of rows
and still lost 0.001 on the board, so a count-level match can hide a real score change. The count-only verdict is
still printed, labelled LEGACY, so old logs stay readable, but VERDICT now follows the row-exact rule.

usage: python compare_submissions.py <a.csv> <b.csv>
"""
import csv, hashlib, sys
from collections import Counter

FIELDS = ('dataset', 'row_type', 'node_id', 't', 'z', 'y', 'x', 'source_id', 'target_id')  # everything but `id`


def load(p):
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    nodes, edges, rows = Counter(), Counter(), Counter()
    coords = {}
    with open(p, newline='') as f:
        for r in csv.DictReader(f):
            (nodes if r['row_type'] == 'node' else edges)[r['dataset']] += 1
            rows[tuple(r[k] for k in FIELDS)] += 1
            if r['row_type'] == 'node':
                coords[(r['dataset'], r['node_id'], r['t'])] = (r['z'], r['y'], r['x'])
    return h, nodes, edges, rows, coords


a, b = sys.argv[1], sys.argv[2]
ha, na, ea, ra, ca = load(a)
hb, nb, eb, rb, cb = load(b)
worst = 0.0
for ds in sorted(set(na) | set(nb)):
    for kind, x, y in (('nodes', na, nb), ('edges', ea, eb)):
        rel = abs(x[ds] - y[ds]) / max(x[ds], 1)
        worst = max(worst, rel)
        print(f'{ds:16s} {kind:5s} {x[ds]:7d} vs {y[ds]:7d}  rel diff {rel:.4%}')

total = max(sum(ra.values()), sum(rb.values()), 1)
only_a = sum((ra - rb).values())
only_b = sum((rb - ra).values())
row_identical = ra == rb
print(f'rows {sum(ra.values())} vs {sum(rb.values())} | only in A {only_a} | only in B {only_b} '
      f'| differing rows {max(only_a, only_b) / total:.4%}')

# how many NODES kept their identity (dataset, node_id, t) but MOVED: the sub-voxel question, specifically
shared = ca.keys() & cb.keys()
moved = [k for k in shared if ca[k] != cb[k]]
if shared:
    per_axis = [sum(1 for k in moved if ca[k][i] != cb[k][i]) for i in range(3)]
    print(f'shared node ids {len(shared)} | moved {len(moved)} ({len(moved) / len(shared):.4%}) '
          f'| z/y/x moved {per_axis[0]}/{per_axis[1]}/{per_axis[2]}')

print('IDENTICAL' if ha == hb else
      ('row-identical (only the `id` column differs)' if row_identical else
       f'hashes differ; worst per-dataset count diff {worst:.4%}'))
print('LEGACY count-only verdict:', 'FAST_OK' if ha == hb or worst <= 0.002 else 'FAST_MISMATCH')
print('VERDICT:', 'FAST_OK' if ha == hb or row_identical else 'FAST_MISMATCH')
