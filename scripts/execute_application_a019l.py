"""One authorized A019L attempt through the unchanged certified CPU route."""
import contextlib
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

import benchmark_application_a019 as forward
import execute_application_a019d as baseline_adapter

ROOT = Path(__file__).resolve().parents[1]
START = '4d0eeb14fafe70295f3565d8182de913c58c23ee'
BASELINE = ROOT / 'docs/plans/2026-10-06-application-a019d-evidence.json'


def environment():
    """Observe current settings without modifying them or opening sources."""
    config = io.StringIO()
    with contextlib.redirect_stdout(config):
        forward.np.show_config()
    def command(args):
        return subprocess.check_output(args, text=True).strip()
    hardware = json.loads(command(['powershell', '-NoProfile', '-Command',
        '$p=Get-CimInstance Win32_Processor; $o=Get-CimInstance Win32_OperatingSystem; '
        '$s=Get-Process -Id $PID; '
        '@{cpu=$p.Name; cores=$p.NumberOfCores; logical=$p.NumberOfLogicalProcessors; '
        'clock_mhz=$p.CurrentClockSpeed; max_clock_mhz=$p.MaxClockSpeed; load_percent=$p.LoadPercentage; '
        'os=$o.Caption; build=$o.BuildNumber; total_kib=$o.TotalVisibleMemorySize; '
        'free_kib=$o.FreePhysicalMemory; boot=$o.LastBootUpTime.ToUniversalTime().ToString("o"); '
        'affinity=$s.ProcessorAffinity.ToInt64(); priority=$s.PriorityClass.ToString()} | ConvertTo-Json']))
    baseline = json.loads(BASELINE.read_text())
    assert command(['git', 'rev-parse', 'HEAD']) == START
    assert command(['git', 'rev-parse', 'origin/master']) == START
    assert command(['git', 'ls-remote', 'origin', 'refs/heads/master']).split()[0] == START
    assert hashlib.sha256(BASELINE.read_bytes()).hexdigest() == 'ffe43022024d92063de118572d4e26ab93c6c3ec19137bfa2d2dd2f59c593ea4'
    assert sys.version == baseline['environment']['python']
    assert platform.platform() == baseline['environment']['platform']
    assert forward.np.__version__ == baseline['environment']['numpy']
    assert 'i9-7900X' in hardware['cpu'] and hardware['cores'] == 10 and hardware['logical'] == 20
    assert hardware['build'] == '19045' and hardware['free_kib'] * 1024 >= 12 * 1024**3
    assert command(['git', 'hash-object', 'uv.lock']) == 'b9d5025dcb340498b417baf42c15fb826d46fdf3'
    assert not command(['git', 'diff', 'bb7a284c4e74f7c257880fd914b9ad9b99f7fd00', 'HEAD', '--',
        'scripts/benchmark_application_a019.py', 'scripts/benchmark_application_a013.py',
        'scripts/certify_application_a018ur.py', 'scripts/preparation_identity_contract.py'])
    forward.load_contract()
    return dict(recorded_utc=datetime.now(timezone.utc).isoformat(), repository_sha=START,
        python=sys.version, executable=sys.executable, platform=platform.platform(),
        numpy=forward.np.__version__, numpy_build=config.getvalue(), hardware=hardware,
        dependencies=sorted((d.metadata['Name'], d.version) for d in importlib.metadata.distributions()),
        lock_blob=command(['git', 'hash-object', 'uv.lock']),
        lock_sha256=hashlib.sha256((ROOT / 'uv.lock').read_bytes()).hexdigest(),
        thread_environment={k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
            'MKL_NUM_THREADS', 'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')},
        data_root_environment=os.environ.get('MALECNS_DATA_ROOT'),
        power_plan=command(['powercfg', '/getactivescheme']),
        supervision='unchanged Windows Job suspended launch; aggregate caps; 0.01-s poll',
        comparison=dict(cpu='MATCH', os_build='MATCH', python='MATCH', numpy_version='MATCH',
            lock='MATCH', repository='CHANGED', source='UNKNOWN until accepted verification',
            supervision='MATCH', blas_build='A019D_NOT_RECORDED', installed_dependencies='A019D_NOT_RECORDED',
            threads='A019D_NOT_RECORDED', affinity_priority='A019D_NOT_RECORDED',
            power='A019D_NOT_RECORDED', thermal_frequency_load_cache='UNKNOWN',
            memory_total='MATCH', memory_available='CHANGED'),
        comparable=True, comparison_reason='Same host/build/runtime/lock and certified route; no demonstrated material confound. Missing historical thread/power/BLAS metadata remains uncertainty.',
        thermal_telemetry='unavailable; nominal CIM clock is not measured sustained frequency')


def worker():
    """Add exact historical replay checks outside the unchanged call timers."""
    baseline = json.loads(BASELINE.read_text())
    original = forward.historical.checkpoint if hasattr(forward.historical, 'checkpoint') else None
    run_sequences = forward.historical.run_sequences
    def checked_sequences(runtime, windows, ids, evidence, checkpoint, phase, memory):
        checked = 0
        def check():
            nonlocal checked
            while checked < len(evidence['steps']):
                row = evidence['steps'][checked]
                expected = baseline['steps'][checked]['replay']
                actual = json.loads(json.dumps(row['replay']))
                forward.require(actual == expected, 'A019L-REPLAY-MISMATCH',
                    f'historical exact replay mismatch at call {checked + 1}')
                checked += 1
            checkpoint()
        run_sequences(runtime, windows, ids, evidence, check, phase, memory)
        evidence['a019d_exact_replay'] = dict(pass_exact=True, boundaries=checked)
    forward.historical.run_sequences = checked_sequences
    baseline_adapter.worker()


if __name__ == '__main__':
    if '--worker' in sys.argv:
        worker()
    else:
        output = Path(sys.argv[1])
        forward.require(not output.exists(), 'EVIDENCE_EXISTS', 'no overwrite or retry')
        current = environment()
        with tempfile.TemporaryDirectory(prefix='a019l-preflight-') as temporary:
            preflight = Path(temporary) / 'environment.json'
            preflight.write_text(json.dumps(current, indent=2))
            result = forward.supervise([sys.executable, str(Path(__file__).resolve()), '--worker'], output)
        result['a019l_environment_preconsumption'] = current
        result['authorization'] = '授權 A019L; exactly one new full-real CPU attempt; no retry'
        result['starting_sha'] = START
        result['a019d_evidence_sha256'] = hashlib.sha256(BASELINE.read_bytes()).hexdigest()
        forward.historical.dump(output, result)
        print(json.dumps(dict(classification=result['classification'], consumed=result['attempt_count'])))
