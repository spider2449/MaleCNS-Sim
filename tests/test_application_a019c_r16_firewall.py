"""Negative controls for the exact A007C validation-only Node admission."""
import subprocess
from pathlib import Path

import pytest
import validation_firewall as guard
from a007c_node import command, environment


def test_exact_node_grammar_and_negative_controls(tmp_path):
    data = tmp_path / 'evidence.json'
    data.write_text('{}')
    argv = command(data)
    assert guard.mandatory_child(argv)
    assert guard.mandatory_child(subprocess.list2cmdline(argv), argv[0])
    alternatives = []
    for index, value in [(0, str(tmp_path / 'node.exe')),
                         (7, str(tmp_path / 'alternate.cjs')),
                         (8, 'wrong-purpose'),
                         (7, str(Path(argv[7]).parent / '..' / 'a019c_firewall' / 'a007c_node.cjs'))]:
        changed = argv.copy()
        changed[index] = value
        alternatives.append(changed)
    alternatives.extend([['cmd.exe', '/c', *argv], [argv[0], '-e', '1'],
                         [argv[0], '--eval', '1'], [argv[0], '--require', argv[7]],
                         [argv[0], '--trace-warnings', *argv[1:]]])
    for alternative in alternatives:
        assert not guard.mandatory_child(alternative)
        with pytest.raises(guard.SourceAccessDenied):
            subprocess.run(alternative, env=environment(), cwd=str(guard.ROOT))
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run(argv, shell=True, env=environment(), cwd=str(guard.ROOT))
    wrong_env = environment()
    wrong_env['NODE_OPTIONS'] = '--require=alternate.cjs'
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run(argv, env=wrong_env, cwd=str(guard.ROOT))
    with pytest.raises(guard.SourceAccessDenied):
        command(guard.ROOT / 'data/evidence.json')
