"""Single authorized A019D invocation of the unchanged certified forward route."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone

import benchmark_application_a019 as forward
from malecns_sim.application.workbench import DatasetCatalog, SOURCE_FILES


def worker():
    monitor = forward.historical.WindowsMemory(os.getpid())
    consumed = False
    sources = []
    consumption = None
    preparation_start = None
    preparation_end = None

    def notify(phase, **details):
        nonlocal preparation_start, preparation_end
        now = datetime.now(timezone.utc).isoformat()
        if phase == 'prepare' and preparation_start is None:
            preparation_start = now
        if phase == 'identity' and preparation_end is None:
            preparation_end = now
        forward.emit(phase, utc=now, **details)

    try:
        available = monitor.available()
        forward.require(available >= forward.historical.AVAILABLE_MIN,
                        'WATCHDOG_PREFLIGHT_FAILED', '12 GiB available required')
        catalog = DatasetCatalog.local()
        forward.require(catalog.available(), 'SOURCE_PREFLIGHT_FAILED', 'registered sources missing')
        files = catalog.files
        for path, (_, expected) in zip((files.annotation, files.neurotransmitter, files.weights), SOURCE_FILES):
            value = hashlib.sha256()
            with path.open('rb') as stream:
                if path == files.weights:
                    consumed = True
                    consumption = dict(utc=datetime.now(timezone.utc).isoformat(),
                                       pid=os.getpid(), path=str(path.resolve()),
                                       point='first successful registered edge-source binary open for source identity verification')
                    forward.emit('source_verification', attempt_count=1, consumption=consumption)
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    value.update(chunk)
            sources.append(dict(path=str(path.resolve()), bytes=path.stat().st_size,
                                sha256=value.hexdigest(), expected_sha256=expected))
            forward.require(value.hexdigest() == expected, 'IDENTITY_MISMATCH', 'registered source hash mismatch')
        forward.emit('source_verification', attempt_count=int(consumed), sources=sources)
        result = forward.run_forward(forward.Source(files, None), notify=notify,
                                     memory=monitor.snapshot, real_authorized=True,
                                     available_physical_bytes=available, contained_watchdog=True)
        result['attempt_count'] = int(consumed)
        result['available_physical_bytes'] = available
    except Exception as exc:
        result = dict(schema='application-stateful-benchmark-evidence-v1',
                      classification=getattr(exc, 'classification', 'HARNESS_FAILURE'),
                      stop_detail=repr(exc), attempt_count=int(consumed))
    finally:
        monitor.close()
    result.update(sources=sources, consumption=consumption,
                  preparation_start_utc=preparation_start, preparation_end_utc=preparation_end,
                  environment=dict(python=sys.version, executable=sys.executable,
                                   platform=platform.platform(), numpy=forward.np.__version__))
    forward.emit('result', evidence=result)


if __name__ == '__main__':
    if '--worker' in sys.argv:
        worker()
    else:
        output = Path(sys.argv[1])
        result = forward.supervise([sys.executable, str(Path(__file__).resolve()), '--worker'], output)
        print(json.dumps(dict(classification=result['classification'], attempt_count=result['attempt_count'])))
