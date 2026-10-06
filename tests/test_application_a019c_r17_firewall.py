"""A006R exact-script equivalence and fail-closed admission controls."""
import ast
import hashlib
import subprocess
from pathlib import Path
import pytest
import validation_firewall as guard
from a006r_node import command, SCRIPT
from a007c_node import environment


def test_historical_inline_equivalence():
    source = SCRIPT.read_text().split('\n', 2)[2]
    assert hashlib.sha256(source.encode()).hexdigest() == '68120c63c86df3941d938565589f08425119d43b63a2db855756ba27da5c682e'
    assert SCRIPT.read_text().startswith("// Preserve the historical inline argv layout for unchanged assertions.\nprocess.argv = [process.execPath, process.argv[2]];\n")


def test_a006r_exact_node_controls(tmp_path):
    argv = command()
    assert guard.mandatory_child(argv)
    assert guard.mandatory_child(subprocess.list2cmdline(argv), argv[0])
    alternatives = [[argv[0]], [argv[0], '-e', '1'], [argv[0], '--eval', '1'],
                    ['cmd.exe', '/c', *argv], [argv[0], '--trace-warnings', *argv[1:]]]
    for index, value in [(0, str(tmp_path / 'node.exe')), (7, str(tmp_path / 'other.cjs')),
                         (8, 'a007c-synthetic-dom-contract-v1'), (9, str(tmp_path))]:
        changed = argv.copy()
        changed[index] = value
        alternatives.append(changed)
    for alternative in alternatives:
        assert not guard.mandatory_child(alternative)
        with pytest.raises(guard.SourceAccessDenied):
            subprocess.run(alternative, env=environment(), cwd=str(guard.ROOT))
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run(argv, shell=True, env=environment(), cwd=str(guard.ROOT))
    bad = environment()
    bad['NODE_OPTIONS'] = '--require=other.cjs'
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run(argv, env=bad, cwd=str(guard.ROOT))
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run(argv, env=environment(), cwd=str(tmp_path))
