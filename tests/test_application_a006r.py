"""Synthetic browser-state regressions; no scientific engine runs."""
import os
import shutil
import subprocess
from pathlib import Path


def test_visible_run_transitions():
    root = Path(__file__).resolve().parents[1]
    static = root / "src/malecns_sim/application/static"
    if os.environ.get('MALECNS_A019C_R2_FIREWALL') == '1':
        from a006r_node import command
        from a007c_node import environment
        result = subprocess.run(command(), env=environment(), cwd=str(root),
                                capture_output=True, text=True, timeout=30, close_fds=True)
        for marker in ['guard ACTIVE; script-start;', 'workload-start',
                       'registered-payload probe BLOCKED', 'descendant payload probe BLOCKED']:
            assert 'A006R ' + marker in result.stdout
    else:
        node = shutil.which('node')
        assert node, 'Node is required for browser presentation regressions'
        result = subprocess.run([node, str(root / 'tests/js/application_a006r.cjs'), str(static)],
                                capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    print(result.stdout)
