"""Synthetic-only downstream profiling of unchanged production function bodies."""
from __future__ import annotations

import ast
from contextlib import ExitStack
import inspect
import json
import math
import os
from pathlib import Path
import statistics
import sys
import tempfile
import textwrap
import time
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from investigate_application_a014 import WindowsMemory, synthetic_files
from malecns_sim.analysis import task008
from malecns_sim.data import male_cns_v1 as male
from malecns_sim.data.model import NumericNormalizedConnectome
from malecns_sim.dynamics import lif
from malecns_sim.graph import signed, sparse, fingerprint
from malecns_sim.sign import ConservativeSignPolicy, Shiu2024SignPolicy

SHAPES = ('sorted', 'random', 'destination_cluster', 'source_cluster', 'mixed', 'all_exc')


def payload(values):
    """Deduplicate visible numeric owners; exclude unmeasurable object payloads."""
    owners = {}
    arrays = {}
    def visit(name, value, depth=0):
        if isinstance(value, np.ndarray):
            arrays[name] = int(value.size)
            owner = value
            while isinstance(owner.base, np.ndarray):
                owner = owner.base
            owners[id(owner)] = int(owner.nbytes)
        elif depth < 3 and hasattr(value, '__dataclass_fields__'):
            for field in value.__dataclass_fields__:
                visit(name + '.' + field, getattr(value, field), depth + 1)
        elif depth < 3 and hasattr(value, 'indptr'):
            for field in ('indptr', 'indices', 'data'):
                visit(name + '.' + field, getattr(value, field), depth + 1)
    for name, value in values.items():
        visit(name, value)
    return {'visible_owner_bytes': sum(owners.values()), 'array_elements': arrays}


class Probe:
    def __init__(self):
        self.rows = []
        self.overhead = 0.0
        self.monitor = WindowsMemory(os.getpid()) if os.name == 'nt' else None

    def start(self, name, values):
        started = time.perf_counter()
        before = payload(values)
        self.overhead += time.perf_counter() - started
        return name, before, self.overhead, time.perf_counter()

    def end(self, token, values):
        name, before, overhead, started = token
        elapsed = time.perf_counter() - started - (self.overhead - overhead)
        sampling = time.perf_counter()
        after = payload(values)
        self.rows.append({'stage': name, 'seconds': max(0.0, elapsed),
                          'input': before, 'output': after,
                          'temporary_peak_bytes': None,
                          **(self.monitor.snapshot() if self.monitor else {})})
        self.overhead += time.perf_counter() - sampling

    def close(self):
        if self.monitor:
            self.monitor.close()


def instrument(function, probe):
    """Insert probes only between top-level statements, never inside edge loops."""
    function = getattr(function, '__func__', function)
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    node = tree.body[0]
    node.decorator_list = []
    body = []
    for index, statement in enumerate(node.body):
        if index == 0 and isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant):
            body.append(statement)
            continue
        label = function.__qualname__ + ':' + ast.unparse(statement).splitlines()[0][:150]
        body.extend(ast.parse('_a018u_token = _a018u_probe.start(' + repr(label) + ', locals())').body)
        if isinstance(statement, ast.Return):
            body.append(ast.Assign(targets=[ast.Name(id='_a018u_result', ctx=ast.Store())], value=statement.value))
        else:
            body.append(statement)
        body.extend(ast.parse('_a018u_probe.end(_a018u_token, locals())').body)
        if isinstance(statement, ast.Return):
            body.extend(ast.parse('return _a018u_result').body)
    node.body = body
    namespace = dict(function.__globals__, _a018u_probe=probe)
    exec(compile(ast.fix_missing_locations(tree), '<a018u-synthetic-probe>', 'exec'), namespace)
    return namespace[node.name]


def fixture(directory, neurons, edges, shape):
    """Build only generated metadata and canonical unique grouped integer edges."""
    if not 1 <= neurons <= 20000 or not 0 <= edges <= 1000000:
        raise ValueError('synthetic bounds exceeded')
    files = synthetic_files(directory, 0, neurons)
    import pyarrow as pa
    import pyarrow.feather as feather
    labels = ['acetylcholine'] * neurons if shape == 'all_exc' else [
        ('acetylcholine', 'gaba', 'glutamate', 'unknown', None)[i % 5] for i in range(neurons)]
    feather.write_feather(pa.table({'body': np.arange(1, neurons + 1), 'consensus_nt': labels}), files[1])
    rng = np.random.default_rng(18018)
    if shape == 'source_cluster':
        keys = np.arange(edges, dtype=np.int64)
    elif shape == 'destination_cluster':
        keys = (np.arange(edges, dtype=np.int64) % neurons) * neurons + np.arange(edges) // neurons
    else:
        keys = rng.choice(neurons * neurons, edges, replace=False)
    keys.sort()
    if shape == 'random':
        rng.shuffle(keys)
    numeric = NumericNormalizedConnectome(np.arange(1, neurons + 1, dtype=np.int64),
        keys // neurons + 1, keys % neurons + 1, np.arange(edges, dtype=np.int64) % 9 + 1,
        provenance=(('synthetic', 'a018u'),))
    return files, numeric


def run(files, numeric, *, probe=None, threshold=0, conservative=False):
    """Run the actual preparation oracle with a synthetic in-memory loader."""
    with ExitStack() as stack:
        stack.enter_context(patch.object(task008, 'load_male_cns_v1_numeric', lambda *a: numeric))
        if probe:
            for owner, name, method in (
                (signed, 'graph_fingerprint', False),
                (lif, 'signed_graph_fingerprint', False),
                (task008, 'signed_graph_fingerprint', False),
                (task008, 'project_numeric_connectome', False),
                (task008, 'threshold_curated_projection', False),
                (signed.SignedAnatomicalConnectome, 'from_projection', True),
                (sparse.SparseDirectedGraph, 'from_numeric_connectome', True),
                (lif.EffectiveSignedProjection, 'from_signed_connectome', True),
            ):
                replacement = instrument(getattr(owner, name), probe)
                stack.enter_context(patch.object(owner, name, classmethod(replacement) if method else replacement))
            prepare = instrument(task008.prepare_network, probe)
        else:
            prepare = task008.prepare_network
        started = time.perf_counter()
        result = prepare(*files, min_synapses=threshold,
                         sign_policy=ConservativeSignPolicy() if conservative else Shiu2024SignPolicy())
        token = probe.start('runtime_ready', {'prepared': result}) if probe else None
        runtime = lif.PreparedRuntime(result.projection)
        identity = runtime.identity
        delay = runtime.parameters.grid_steps(runtime.dt_ms)
        if probe:
            probe.end(token, {'prepared': result, 'runtime': runtime})
        return result, identity, delay, time.perf_counter() - started


def breakdown(measurement):
    """Disjoint stage accounting; parent and nested intervals never double count."""
    groups = dict(metadata=0.0, projection=0.0, sign=0.0, anatomical_csr=0.0,
                  effective_weight_filter=0.0, outgoing=0.0, digest=0.0, runtime=0.0)
    for row in measurement['stages']:
        name = row['stage']
        group = None
        if name.startswith('prepare_network:') and any(name.startswith('prepare_network:' + prefix)
                for prefix in ('annotations =', 'evidence =', 'selection =')):
            group = 'metadata'
        elif name.startswith('project_numeric_connectome:'):
            group = 'projection'
        elif name.startswith('SignedAnatomicalConnectome.from_projection:') and ':return ' not in name:
            group = 'sign'
        elif name.startswith('SparseDirectedGraph.from_numeric_connectome:'):
            group = 'anatomical_csr'
        elif name.startswith(('graph_fingerprint:', 'signed_graph_fingerprint:')):
            group = 'digest'
        elif name == 'runtime_ready':
            group = 'runtime'
        elif name.startswith('EffectiveSignedProjection.from_signed_connectome:'):
            code = name.split(':', 1)[1]
            if code.startswith('for array in arrays:'):
                group = 'digest'
            elif code.startswith(('for value in ', 'return ')):
                pass  # Nested signed digests already accounted separately.
            elif code.startswith(('order =', 'source, target, effective =', 'indptr =',
                    'np.add.at', 'np.cumsum', 'outgoing_targets =', 'outgoing_weights =')):
                group = 'outgoing'
            else:
                group = 'effective_weight_filter'
        if group:
            groups[group] += row['seconds']
    groups['miscellaneous'] = max(0.0, measurement['instrumented_seconds']
        - measurement['probe_overhead_seconds'] - sum(groups.values()))
    return groups


def budget(measurements):
    """Engineering rate envelope, not an empirical full-scale upper bound."""
    full_n, full_e = 166700, 25582938
    large = [m for m in measurements if m['edges'] == 1000000]
    best = {}
    for group in ('sign', 'anatomical_csr', 'effective_weight_filter', 'outgoing', 'digest', 'runtime', 'miscellaneous'):
        estimates = []
        for m in large:
            ratio = max(full_n / m['neurons'], full_e / m['edges'])
            if group == 'outgoing':
                ratio *= math.log2(full_e) / math.log2(m['edges'])
            if group == 'runtime':
                ratio = 1
            estimates.append(m['breakdown_seconds'][group] * ratio)
        best[group] = max(estimates)
    # Finalization/import/allocator and identity verification operational allowance.
    best['miscellaneous'] = max(5.0, best['miscellaneous'])
    historical, simple, throughput, stress_merge = 38.8289515, 28.983115, 21.952660, 57.966230
    downstream = sum(best.values())
    totals = {'best': historical + simple + downstream,
              'conservative': historical + stress_merge + 4 * downstream,
              'stress': 2 * historical + stress_merge + 8 * downstream}
    return {'grouped_edges': full_e, 'neurons': full_n, 'stage_base_seconds': best,
            'stage_conservative_seconds': {k: 4*v for k, v in best.items()},
            'stage_stress_seconds': {k: 8*v for k, v in best.items()},
            'downstream_base_seconds': downstream, 'known_pre_sign_nonmerge_seconds': historical,
            'stress_pre_sign_multiplier': 2,
            'merge_seconds': {'simple': simple, 'throughput': throughput, 'stress': stress_merge},
            'total_seconds': totals, 'headroom_seconds': {k: 600-v for k, v in totals.items()},
            'upper_bound_proven': False, 'incoming_csr': 'not constructed in production boundary'}


def certify_series(measurements):
    """Replay every measured fixture outside timing to certify exact oracle identity."""
    def equal(left, right):
        assert type(left) is type(right)
        if isinstance(left, np.ndarray):
            assert left.dtype == right.dtype and left.shape == right.shape
            assert left.tobytes() == right.tobytes()
            assert left.flags.writeable == right.flags.writeable
        elif hasattr(left, '__dataclass_fields__'):
            for field in left.__dataclass_fields__:
                if field not in ('preparation_seconds', 'graph_loading_seconds', 'setup_seconds'):
                    equal(getattr(left, field), getattr(right, field))
        else:
            assert left == right
    certificates = []
    for m in measurements:
        with tempfile.TemporaryDirectory(prefix='a018u-exact-') as directory:
            files, numeric = fixture(Path(directory), m['neurons'], m['edges'], m['shape'])
            reference, identity, delay, _ = run(files, numeric)
            probe = Probe()
            try:
                actual, actual_identity, actual_delay, _ = run(files, numeric, probe=probe)
            finally:
                probe.close()
            equal(reference, actual)
            assert reference.fingerprint == m['fingerprint']
            assert identity == actual_identity and delay == actual_delay
            certificates.append({'neurons': m['neurons'], 'edges': m['edges'],
                                 'shape': m['shape'], 'exact': True})
    return certificates


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('refuse to overwrite evidence')
    results = []
    for neurons, edges in ((100, 1000), (2000, 100000), (20000, 100000), (20000, 1000000)):
        for shape in SHAPES:
            with tempfile.TemporaryDirectory(prefix='a018u-synthetic-') as directory:
                files, numeric = fixture(Path(directory), neurons, edges, shape)
                times = []
                for _ in range(3):
                    result, identity, delay, elapsed = run(files, numeric)
                    times.append(elapsed)
                    del result
                probe = Probe()
                try:
                    result, identity, delay, elapsed = run(files, numeric, probe=probe)
                    for row in probe.rows:
                        for boundary in ('input', 'output'):
                            counts = row[boundary].pop('array_elements')
                            row[boundary]['visible_array_element_count'] = sum(counts.values())
                    results.append({'neurons': neurons, 'edges': edges, 'shape': shape,
                        'oracle_seconds': times, 'median_seconds': statistics.median(times),
                        'instrumented_seconds': elapsed, 'probe_overhead_seconds': probe.overhead,
                        'fingerprint': result.fingerprint, 'runtime_identity': identity,
                        'delay_steps': delay, 'stages': probe.rows})
                finally:
                    probe.close()
                del result, numeric
            print(neurons, edges, shape, statistics.median(times), flush=True)
    for m in results:
        m['breakdown_seconds'] = breakdown(m)
    args.output.write_text(json.dumps({'schema': 'application-a018u-synthetic-v1',
        'production_changed': False, 'full_real_preparations': 0, 'budget': budget(results),
        'oracle_certificates': certify_series(results),
        'measurements': results}, separators=(',', ':')) + '\n')


if __name__ == '__main__':
    main()
