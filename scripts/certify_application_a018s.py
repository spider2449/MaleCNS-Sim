"""Synthetic-only A018S profiling and fresh-process comparison."""
import argparse
import inspect
import json
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
from certify_application_a018 import measure
import malecns_sim.data.staged_integer_merge as staged


def profile():
    source = inspect.getsource(staged.merge_sorted_runs)
    source = source.replace('for write in (False, True):', 'for write in (False, True):\n        started = time.perf_counter()')
    source = source.replace('        if not write:\n            output', '        timings.append(time.perf_counter() - started)\n        if not write:\n            allocated = time.perf_counter()\n            output')
    source = source.replace('    return output', '            allocations.append(time.perf_counter() - allocated)\n    return output')
    namespace = dict(np=np, time=time, timings=[], allocations=[])
    exec(source, namespace)
    observations = []
    for overlap in (False, True):
        keys = np.arange(200000, dtype=np.int64)
        left = (keys.copy(), keys.copy(), np.ones(keys.size, dtype=np.int64))
        other = keys if overlap else keys + keys.size
        right = (other.copy(), other.copy(), np.ones(keys.size, dtype=np.int64))
        namespace['timings'].clear()
        namespace['allocations'].clear()
        result = namespace['merge_sorted_runs'](left, right)
        observations.append(dict(overlap=overlap, input_rows=400000, output_rows=result[0].size,
            scan_seconds=namespace['timings'].copy(), allocation_seconds=namespace['allocations'].copy(),
            comparisons_per_scan=200000, scans=2))
    return observations


def benchmark(pattern, route):
    import certify_application_a018 as original
    import malecns_sim.data.single_pass_integer_merge as optimized
    source = inspect.getsource(original.measure)
    source = source.replace('1024 if pattern == "many" else 250000 if pattern == "few" else 65536',
                            '100 if pattern in ("many", "few") else 2048')
    source = source.replace('for start in range(0, rows, size):',
        'starts = list(range(0, rows, size)) if pattern != "few" else [0] + list(range(rows//2, rows, size))\n    for start in starts:')
    source = source.replace('min(start+size, rows)',
        'min(start + (rows//2 if pattern == "few" and start == 0 else size), rows)')
    namespace = dict(original.__dict__)
    namespace['merge_staged_integer_runs'] = (staged.merge_staged_integer_runs if route == 'baseline'
                                             else optimized.merge_staged_integer_runs)
    exec(source, namespace)
    module = staged if route == 'baseline' else optimized
    primitive = module.merge_sorted_runs
    counters = dict(key_comparisons=0, equal_key_events=0, merge_calls=0)
    def counted(left, right):
        result = primitive(left, right)
        counters['merge_calls'] += 1
        comparisons = 0
        if left[0].size and right[0].size:
            boundary = min((int(left[0][-1]), int(left[1][-1])),
                           (int(right[0][-1]), int(right[1][-1])))
            low = int(np.searchsorted(result[0], boundary[0], side='left'))
            high = int(np.searchsorted(result[0], boundary[0], side='right'))
            comparisons = low + int(np.searchsorted(result[1][low:high], boundary[1], side='right'))
        multiplier = 2 if route == 'baseline' else 1
        counters['key_comparisons'] += multiplier * comparisons
        counters['equal_key_events'] += multiplier * (left[0].size + right[0].size - result[0].size)
        return result
    with patch.object(module, 'merge_sorted_runs', counted):
        result = namespace['measure'](231800, pattern, 'staged')
    result['metrics'].update(counters)
    result['route'] = route
    result['metrics'].pop('schedule', None)
    result['metrics'].setdefault('compaction_rows_read', 0)
    result['metrics'].setdefault('compaction_rows_written', 0)
    result['metrics']['row_touches'] = sum(result['metrics'][key] for key in
        ('rows_read', 'rows_written', 'compaction_rows_read', 'compaction_rows_written'))
    metrics = result['metrics']
    metrics.setdefault('first_scan_rows', metrics['rows_read']//2)
    metrics.setdefault('second_scan_rows', metrics['rows_read']//2)
    metrics['seconds_per_million_input_reads'] = metrics['merge_seconds']*1e6/metrics['rows_read']
    metrics['seconds_per_million_total_touches'] = metrics['merge_seconds']*1e6/metrics['row_touches']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', action='store_true')
    parser.add_argument('--matrix', type=Path)
    parser.add_argument('--pattern')
    parser.add_argument('--route')
    args = parser.parse_args()
    if args.profile:
        print(json.dumps(profile(), indent=2))
    elif args.matrix:
        observations = []
        for pattern in ('high', 'moderate', 'unique', 'many', 'few'):
            for repeat in range(3):
                pair = []
                for route in ('baseline', 'optimized'):
                    child = subprocess.run([sys.executable, __file__, '--pattern', pattern,
                        '--route', route], capture_output=True, text=True, check=True)
                    item = json.loads(child.stdout)
                    item['repeat'] = repeat
                    observations.append(item)
                    pair.append(item)
                assert pair[0]['digest'] == pair[1]['digest']
            print(pattern, 'exact', flush=True)
        args.matrix.write_text(json.dumps(dict(profile=profile(), observations=observations), indent=2))
    else:
        print(json.dumps(benchmark(args.pattern, args.route)))
