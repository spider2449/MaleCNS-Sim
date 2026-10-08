"""Run installed CPU artifact and guide checks inside a certified boundary."""
from __future__ import annotations

from collections import Counter
from email.parser import BytesParser
import contextlib
import hashlib
import importlib.metadata as metadata
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import tarfile
import threading
import urllib.error
import urllib.request
import zipfile


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == '--gpu-guide':
        work = Path(sys.argv[2])
        import malecns_sim
        import cupy
        assert metadata.version('malecns-sim') == '0.4.0'
        assert Path(malecns_sim.__file__).is_relative_to(Path(sys.prefix))
        assert cupy.cuda.runtime.getDeviceCount() >= 1
        guide = (work / 'package/docs/runtime/USER_GUIDE.md').read_text()
        examples = re.findall(r'```python\s*\n(.*?)```', guide, re.S)
        assert len(examples) == 4
        namespace = {}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(examples[0], 'installed-guide-gpu-projection', 'exec'), namespace)
            exec(compile(examples[3], 'installed-guide-gpu-lifecycle', 'exec'), namespace)
        record = {'status': 'INSTALLED GPU GUIDE PASS', 'version': metadata.version('malecns-sim'),
                  'origin': malecns_sim.__file__, 'gpu_device_count': cupy.cuda.runtime.getDeviceCount(),
                  'executed_blocks': [0, 3], 'claim': 'bounded synthetic example; no performance claim'}
        (work / 'gpu-guide-smoke.json').write_text(json.dumps(record, indent=2) + '\n')
        print(record['status'], flush=True)
        return
    work = Path(sys.argv[1]) if len(sys.argv) == 2 else Path('/work')
    dist = work / 'dist'
    wheel, = dist.glob('*.whl')
    sdist, = dist.glob('*.tar.gz')
    with zipfile.ZipFile(wheel) as archive:
        wheel_members = archive.namelist()
        metadata_member, = (name for name in wheel_members if name.endswith('.dist-info/METADATA'))
        wheel_metadata = BytesParser().parsebytes(archive.read(metadata_member))
        assert wheel_metadata['Name'] == 'malecns-sim' and wheel_metadata['Version'] == '0.4.0'
    with tarfile.open(sdist) as archive:
        sdist_members = archive.getnames()
        records = [member for member in archive.getmembers() if member.name.endswith('/PKG-INFO')]
        assert records
        for member in records:
            assert member.isfile() and member.size < 1024 * 1024
            with archive.extractfile(member) as stream:
                sdist_metadata = BytesParser().parsebytes(stream.read())
            assert sdist_metadata['Name'] == 'malecns-sim' and sdist_metadata['Version'] == '0.4.0'
    for member in wheel_members + sdist_members:
        parts = Path(member).parts
        assert not Path(member).is_absolute() and '..' not in parts
        relative = parts[1:] if parts[0].startswith('malecns_sim-') else parts
        assert not relative or relative[0] != 'data'
        assert not set(relative) & {'artifacts', 'references', '.venv', '__pycache__'}
        assert 'male-cns-v1' not in member.lower()
    for guide in ('docs/runtime/USER_GUIDE.md', 'docs/runtime/RELEASE_GATE.md',
                  'docs/releases/0.4.0-preparation.md'):
        assert any(member.endswith('/' + guide) for member in sdist_members)
    import malecns_sim
    import malecns_sim.runtime as runtime_module
    assert Path(malecns_sim.__file__).is_relative_to(Path(sys.prefix))
    assert metadata.version('malecns-sim') == '0.4.0'
    assert importlib.util.find_spec('cupy') is None
    assert set(runtime_module.__all__) == {'prepare_runtime', 'PreparedRuntime', 'SimulationState', 'AdvanceResult'}
    guide_path = work / 'package/docs/runtime/USER_GUIDE.md' if len(sys.argv) == 2 else Path('/input/docs/runtime/USER_GUIDE.md')
    guide = guide_path.read_text()
    examples = re.findall(r'```python\s*\n(.*?)```', guide, re.S)
    assert len(examples) == 4
    namespace = {}
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        exec(compile(examples[0], 'installed-guide-quickstart', 'exec'), namespace)
        exec(compile(examples[2], 'installed-guide-poisson', 'exec'), namespace)
    from malecns_sim import ExplicitStimulus, SpikeSchedule, simulate_lif
    runtime, full = namespace['runtime'], namespace['full']
    assert namespace['state'].timestep == 40
    reference = simulate_lif(namespace['projection'], duration_ms=4.0, stimulus=full)
    whole = runtime.advance(runtime.initial_state(), duration_ms=4.0, stimulus=full)
    state = runtime.initial_state()
    chunks = []
    for start, stop in ((0, 20), (20, 40)):
        local = ExplicitStimulus(tuple(SpikeSchedule(schedule.neuron_id, tuple(
            (step - start) * runtime.dt_ms for time in schedule.spike_times_ms
            for step in (int(round(time / runtime.dt_ms)),) if start <= step < stop
        )) for schedule in full.schedules), weight_mV=full.weight_mV,
            refractory_free_neuron_ids=full.refractory_free_neuron_ids)
        chunks.append(runtime.advance(state, duration_ms=2.0, stimulus=local))
    assert whole.spike_neuron_ids == sum((chunk.spike_neuron_ids for chunk in chunks), ())
    assert whole.spike_timesteps == sum((chunk.spike_timesteps for chunk in chunks), ())
    assert whole.spike_neuron_ids == tuple(map(int, reference.spike_neuron_ids))
    assert whole.spike_timesteps == tuple(map(int, reference.spike_timesteps))
    counts = Counter(whole.spike_neuron_ids)
    assert all(counts[neuron] == int(reference.spike_counts[index])
               for index, neuron in enumerate(runtime.neuron_ids))
    cli = {}
    for name in ('malecns-sim', 'malecns-workbench'):
        entry, = (entry for entry in metadata.entry_points(group='console_scripts') if entry.name == name)
        previous = sys.argv
        sys.argv = [name, '--help']
        try:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                try:
                    entry.load()()
                except SystemExit as error:
                    assert error.code == 0
            assert 'usage:' in output.getvalue()
            cli[name] = entry.value
        finally:
            sys.argv = previous
    from malecns_sim.application.server import LocalServer
    server = LocalServer(0, result_root=work / 'workbench-results')
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    assets = {}
    try:
        url = f'http://127.0.0.1:{server.server_port}'
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url + '/api/status', timeout=10) as response:
            assert json.load(response)['status'] == 'READY'
        try:
            opener.open(url + '/api/runs', timeout=10)
        except urllib.error.HTTPError as error:
            assert error.code == 403
        else:
            raise RuntimeError('unauthenticated protected route admitted')
        request = urllib.request.Request(url + '/api/runs', headers={'X-Local-Session': server.token})
        with opener.open(request, timeout=10) as response:
            assert json.load(response) == {'runs': []}
        for route in ('/', '/app.js', '/style.css', '/arena', '/arena.js', '/arena.css'):
            with opener.open(url + route, timeout=10) as response:
                content = response.read()
                assert content
                assets[route] = hashlib.sha256(content).hexdigest()
    finally:
        server.shutdown()
        thread.join(timeout=10)
        server.server_close()
        assert not thread.is_alive()
    result = {'status': 'CPU ARTIFACT SMOKE PASS', 'platform': sys.platform,
              'python': sys.version, 'origin': malecns_sim.__file__, 'version': metadata.version('malecns-sim'),
              'guide_examples': {'python_fences': 4, 'executed_cpu_blocks': [0, 2],
                                 'signature_reference_block': 1, 'gpu_block': 'separate GPU guide process'}, 'guide_output': capture.getvalue(), 'legacy_continuity': 'PASS',
              'cli': cli, 'http_authentication': 'PASS', 'assets': assets,
              'wheel_members': wheel_members, 'sdist_members': sdist_members,
              'artifacts': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (wheel, sdist)},
              'dependencies': sorted((item.metadata['Name'], item.version) for item in metadata.distributions()),
              'historical_suite': 'NOT RUN', 'I1': 'NOT RUN - REGISTERED-PAYLOAD-REQUIRED'}
    (work / 'smoke.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
