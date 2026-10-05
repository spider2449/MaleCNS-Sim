"""Bounded synthetic A018T measurements; never opens real data."""
import argparse
import ast
import cProfile
import inspect
import io
import json
import pstats
import subprocess
import sys
import time
from functools import partial
from pathlib import Path
from unittest.mock import patch
import numpy as np
import certify_application_a018 as original
import malecns_sim.data.staged_integer_merge as a018
import malecns_sim.data.single_pass_integer_merge as a018s
import malecns_sim.data.blockwise_integer_merge as a018t


def profile():
    observations = []
    for overlap in (False, True):
        keys = np.arange(200000, dtype=np.int64)
        other = keys if overlap else keys + keys.size
        left = (keys.copy(), keys.copy(), np.ones(keys.size, dtype=np.int64))
        right = (other.copy(), other.copy(), np.ones(keys.size, dtype=np.int64))
        source = inspect.getsource(a018s.merge_sorted_runs)
        source = source.replace('    output = tuple(', '    allocated = time.perf_counter()\n    output = tuple(')
        source = source.replace('    i = j = used = 0', '    allocation.append(time.perf_counter()-allocated)\n    scan = time.perf_counter()\n    i = j = used = 0')
        source = source.replace('    if used < n + m:', '    scans.append(time.perf_counter()-scan)\n    if used < n + m:')
        source = source.replace('        output = compact_output(output, used)', '        compact = time.perf_counter()\n        output = compact_output(output, used)\n        compactions.append(time.perf_counter()-compact)')
        source = source.replace('        if comparison < 0:', '        branches[comparison] += 1\n        if comparison < 0:')
        counts = dict(scalar_loads=0, comparisons=0, int_conversions=0)
        class Count(ast.NodeTransformer):
            def visit_Subscript(self, node):
                node = self.generic_visit(node)
                if isinstance(node.ctx, ast.Load) and isinstance(node.value, ast.Subscript) and isinstance(node.value.value, ast.Name) and node.value.value.id in ('left', 'right'):
                    return ast.copy_location(ast.Call(func=ast.Name(id='scalar', ctx=ast.Load()), args=[node], keywords=[]), node)
                return node
            def visit_Compare(self, node):
                node = self.generic_visit(node)
                if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'scalar' for n in ast.walk(node)):
                    return ast.copy_location(ast.Call(func=ast.Name(id='count_comparison', ctx=ast.Load()), args=[node], keywords=[]), node)
                return node
        def scalar(value):
            counts['scalar_loads'] += 1
            return value
        def comparison(value):
            counts['comparisons'] += 1
            return value
        def integer(value):
            counts['int_conversions'] += 1
            return int(value)
        ns = dict(np=np, time=time, compact_output=a018s.compact_output,
                  allocation=[], scans=[], compactions=[], branches={-1:0, 0:0, 1:0})
        exec(source, ns)
        ns['merge_sorted_runs'](left, right)
        timings = {k:ns[k].copy() for k in ('allocation', 'scans', 'compactions', 'branches')}
        tree = ast.fix_missing_locations(Count().visit(ast.parse(source)))
        ns.update(scalar=scalar, count_comparison=comparison, int=integer)
        exec(compile(tree, '<counted>', 'exec'), ns)
        ns['merge_sorted_runs'](left, right)
        profiler = cProfile.Profile()
        profiler.runcall(a018s.merge_sorted_runs, left, right)
        stream = io.StringIO()
        pstats.Stats(profiler, stream=stream).sort_stats('tottime').print_stats(12)
        observations.append(dict(overlap=overlap, input_rows=400000,
            python_iterations=200000 if overlap else 400000, output_scalar_writes=600000 if overlap else 1200000,
            counters=counts, timings=timings, cprofile=stream.getvalue()))
    return observations


def profile_blockwise():
    """Instrument native calls separately from uninstrumented timing matrix."""
    observations = []
    for overlap in (False, True):
        keys = np.arange(200000, dtype=np.int64)
        other = keys if overlap else keys + keys.size
        left = (keys.copy(), keys.copy(), np.ones(keys.size, dtype=np.int64))
        right = (other.copy(), other.copy(), np.ones(keys.size, dtype=np.int64))
        for size in (4096, 16384, 65536, 262144):
            counters = {}
            def timed(name, function):
                def call(*args, **kwargs):
                    started = time.perf_counter()
                    result = function(*args, **kwargs)
                    entry = counters.setdefault(name, dict(calls=0, seconds=0.0))
                    entry['calls'] += 1
                    entry['seconds'] += time.perf_counter()-started
                    return result
                return call
            with patch.object(np, 'lexsort', timed('sort', np.lexsort)), \
                 patch.object(np, 'searchsorted', timed('search', np.searchsorted)), \
                 patch.object(np, 'concatenate', timed('concat', np.concatenate)), \
                 patch.object(np, 'empty', timed('allocation', np.empty)), \
                 patch.object(a018t, 'compact_output', timed('compaction', a018t.compact_output)):
                started = time.perf_counter()
                result = a018t.merge_sorted_runs(left, right, block_size=size)
                elapsed = time.perf_counter()-started
            profiler = cProfile.Profile()
            profiler.runcall(a018t.merge_sorted_runs, left, right, block_size=size)
            stream = io.StringIO()
            pstats.Stats(profiler, stream=stream).sort_stats('tottime').print_stats(15)
            observations.append(dict(overlap=overlap, block_size=size, input_rows=400000,
                output_rows=result[0].size, measured_seconds=elapsed, native_calls=counters,
                cprofile=stream.getvalue(), workspace_bound_bytes=128*size))
    return observations


def benchmark(pattern, route, block_size):
    source = inspect.getsource(original.measure)
    source = source.replace('1024 if pattern == "many" else 250000 if pattern == "few" else 65536',
                            '100 if pattern in ("many", "few") else 2048')
    source = source.replace('for start in range(0, rows, size):',
        'starts = list(range(0, rows, size)) if pattern != "few" else [0] + list(range(rows//2, rows, size))\n    for start in starts:')
    source = source.replace('min(start+size, rows)', 'min(start+(rows//2 if pattern == "few" and start == 0 else size), rows)')
    if pattern == 'long_pre':
        source = source.replace('keys // 2000, keys % 2000', 'np.zeros_like(keys), keys')
    ns = dict(original.__dict__)
    ns['merge_staged_integer_runs'] = {'a018':a018.merge_staged_integer_runs,
        'a018s':a018s.merge_staged_integer_runs,
        'a018t':partial(a018t.merge_staged_integer_runs, block_size=block_size)}[route]
    exec(source, ns)
    result = ns['measure'](231800, pattern, 'staged')
    result['route'] = route
    result['block_size'] = block_size
    result['metrics'].pop('schedule', None)
    return result


def matrix(path):
    observations = []
    # No warmup: every measurement uses a fresh process and includes cold merge calls.
    for pattern in ('many', 'unique', 'high', 'moderate', 'few', 'long_pre'):
        for route in ('a018', 'a018s', 'a018t'):
            sizes = (4096, 16384, 65536, 262144) if route == 'a018t' else (65536,)
            for size in sizes:
                for repeat in range(3):
                    child = subprocess.run([sys.executable, __file__, '--pattern', pattern,
                        '--route', route, '--block-size', str(size)], check=True, capture_output=True, text=True)
                    item = json.loads(child.stdout)
                    item['repeat'] = repeat
                    observations.append(item)
        digests = {o['digest'] for o in observations if o['pattern'] == pattern}
        assert len(digests) == 1
        path.write_text(json.dumps(dict(warmup='none; fresh process for every repeat', observations=observations), indent=2))
        print(pattern, 'exact', flush=True)
    path.write_text(json.dumps(dict(warmup='none; fresh process for every repeat',
        profile=profile(), blockwise_profile=profile_blockwise(), observations=observations), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix', type=Path)
    parser.add_argument('--pattern', choices=('many','unique','high','moderate','few','long_pre'))
    parser.add_argument('--route', choices=('a018','a018s','a018t'))
    parser.add_argument('--block-size', type=int, default=16384)
    args = parser.parse_args()
    if args.matrix:
        matrix(args.matrix)
    else:
        print(json.dumps(benchmark(args.pattern, args.route, args.block_size)))
