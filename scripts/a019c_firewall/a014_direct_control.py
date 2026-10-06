"""Fixed synthetic direct-interpreter memory control; no caller-supplied code."""
import os
from pathlib import Path
import sys


def main():
    if (sys.argv[1:] != ['a014-tree-memory-control-v1']
            or os.environ.get('MALECNS_A019C_R2_FIREWALL') != '1'):
        return 78
    root = Path(__file__).resolve().parents[2]
    # -S avoids an ignored sitecustomize failure; install explicitly, fail closed.
    sys.path.insert(0, str(root / '.venv' / 'Lib' / 'site-packages'))
    import validation_firewall as guard
    try:
        guard.install()
        if not guard.ACTIVE:
            return 78
    except BaseException:
        return 78
    # Descendants must use the established virtualenv guarded-child contract.
    sys.executable = str(root / '.venv' / 'Scripts' / 'python.exe')
    payload = root / 'data' / 'a019c-r12-denied-probe.feather'
    try:
        open(payload, 'rb')
    except guard.SourceAccessDenied:
        pass
    else:
        return 79
    import subprocess
    probe = subprocess.run([sys.executable, '-c',
        'from pathlib import Path; import validation_firewall as g; '
        'g.check(g.ROOT / "data" / "a019c-r12-descendant-probe.feather")'],
        capture_output=True, text=True)
    if probe.returncode == 0 or 'SourceAccessDenied' not in probe.stderr:
        return 79
    guard.record('direct_control_ready', purpose=guard.DIRECT_PURPOSE)
    import time
    handshake = Path(os.environ['MALECNS_A014_CONTROL_HANDSHAKE'])
    handshake.with_suffix('.ready').write_text('ready', encoding='utf-8')
    deadline = time.monotonic() + 10
    while not handshake.with_suffix('.release').exists():
        if time.monotonic() > deadline:
            return 80
        time.sleep(0.01)
    allocation = bytearray(160 * 1024**2)
    guard.record('direct_control_allocated', bytes=len(allocation))
    handshake.with_suffix('.allocated').write_text(str(len(allocation)), encoding='utf-8')
    print(os.getpid(), flush=True)
    time.sleep(8)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
