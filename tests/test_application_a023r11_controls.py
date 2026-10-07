"""A011 command composition and inherited authority regression controls."""
import subprocess

import pytest
import validation_firewall as guard
from a011_node import command, environment


def test_a011_exact_authority_and_composition(tmp_path):
    fixture = tmp_path / 'arena.json'
    fixture.write_text('{}')
    argv = command(fixture)
    assert guard.mandatory_child(argv, argv[0])
    assert guard.mandatory_child(subprocess.list2cmdline(argv), argv[0])
    assert guard.guarded_command(argv) == argv
    for index in range(len(argv)):
        changed = argv.copy()
        changed[index] += '-alternate'
        assert not guard.mandatory_child(changed)
        with pytest.raises(guard.SourceAccessDenied):
            subprocess.run(changed, env=environment(), cwd=str(guard.ROOT))
    for changed in ([argv[0], '-e', '1'], ['cmd.exe', '/c', *argv],
                    [*argv[:1], '--allow-child-process', *argv[1:]]):
        assert not guard.mandatory_child(changed)
        with pytest.raises(guard.SourceAccessDenied):
            subprocess.run(changed, env=environment(), cwd=str(guard.ROOT))


@pytest.mark.parametrize('change', ['shell', 'environment', 'cwd', 'executable', 'close_fds'])
def test_a011_activation_cannot_bypass_child_protection(tmp_path, change):
    fixture = tmp_path / 'arena.json'
    fixture.write_text('{}')
    kwargs = dict(env=environment(), cwd=str(guard.ROOT), close_fds=True)
    if change == 'shell':
        kwargs['shell'] = True
    elif change == 'environment':
        kwargs['env']['NODE_OPTIONS'] = '--require=alternate.cjs'
    elif change == 'cwd':
        kwargs['cwd'] = str(tmp_path)
    elif change == 'executable':
        kwargs['executable'] = command(fixture)[0]
    else:
        kwargs['close_fds'] = False
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run(command(fixture), **kwargs)


def test_a011_protected_fixture_denied_before_open():
    with pytest.raises(guard.SourceAccessDenied):
        command(guard.ROOT / 'data/arena.json')


def test_browser_session_historical_assertions_unchanged():
    import ast
    from session_node import SCRIPT
    source = (guard.ROOT / 'tests/test_workbench_session.py').read_text()
    function = next(node for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef) and node.name == 'test_browser_session_recovery')
    assignment = next(node for node in function.body if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == 'script' for target in node.targets))
    assert SCRIPT.read_text().split('\n', 2)[2] == ast.literal_eval(assignment.value)


def test_browser_session_exact_authority(tmp_path):
    from session_node import command
    argv = command()
    assert guard.mandatory_child(argv)
    assert guard.mandatory_child(subprocess.list2cmdline(argv), argv[0])
    for index in range(len(argv)):
        changed = argv.copy()
        changed[index] += '-alternate'
        assert not guard.mandatory_child(changed)
        with pytest.raises(guard.SourceAccessDenied):
            subprocess.run(changed, env=environment(), cwd=str(guard.ROOT))


def ready_fixture():
    from a023_release_validation import BASE
    return {'base': BASE, 'candidate': {'src/example.py': '0' * 64},
            'H': ['historical'], 'I': ['infrastructure'], 'N': ['new'],
            'collection': ['historical', 'infrastructure', 'new'],
            'taxonomy': [{'node_id': 'historical', 'classification': 'Z0',
                          'disposition': 'RUN', 'reason_category': 'synthetic fixture'}],
            'integrity': {'I0': 'FROZEN — UNPROTECTED CONTENT ONLY',
                          'I1': 'NOT RUN — REGISTERED-PAYLOAD-REQUIRED',
                          'I2': 'FROZEN — BOUNDED MANIFEST CONSISTENCY'},
            'terminal': {'A011': 'Z3-RUN', 'A007B': 'Z3-RUN', 'product_changes_allowed': False}}


def test_native_child_environment_composes_exact_authority(monkeypatch):
    import profile_application_a019x as profile
    monkeypatch.setenv('PYTHONPATH', 'untrusted-ambient-path')
    assert profile.child_environment()['PYTHONPATH'] == str(guard.ROOT / 'scripts/a019c_firewall')


def test_complete_readiness_is_pass_capable():
    from a023_release_validation import readiness
    assert readiness(ready_fixture()) == {'EXECUTION_AUTHORIZED': True, 'blockers': []}


@pytest.mark.parametrize('change', ['missing', 'base', 'collection', 'Z2', 'blocked', 'I1', 'mutable', 'taxonomy', 'duplicate'])
def test_readiness_denies_incomplete_or_changed_contract(change):
    from a023_release_validation import readiness
    record = ready_fixture()
    if change == 'missing':
        record.pop('N')
    elif change == 'base':
        record['base'] = 'HEAD'
    elif change == 'collection':
        record['collection'].append('unfrozen')
    elif change == 'Z2':
        record['taxonomy'][0]['classification'] = 'Z2'
    elif change == 'blocked':
        record['taxonomy'][0].update(classification='Z3', disposition='Z3-BLOCKED')
    elif change == 'I1':
        record['integrity']['I1'] = 'PASS'
    elif change == 'mutable':
        record['terminal']['product_changes_allowed'] = True
    elif change == 'taxonomy':
        record['taxonomy'][0]['node_id'] = 'replacement'
    else:
        record['N'].append('new')
    assert readiness(record)['EXECUTION_AUTHORIZED'] is False
