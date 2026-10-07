"""Negative controls for the narrow A019X native launch boundary."""
from pathlib import Path
import sys
import tempfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import profile_application_a019x as profile
import validation_firewall as guard


@pytest.fixture
def output():
    with tempfile.TemporaryDirectory(prefix='malecns-a019x-') as directory:
        yield Path(directory)


def test_frozen_sources_and_original_guard_admission():
    profile.check_pins()
    assert guard.ACTIVE
    assert not guard.mandatory_child([str(profile.NSYS), 'profile'])
    with pytest.raises(guard.SourceAccessDenied):
        guard.guarded_command([str(profile.NSYS), 'profile'])


@pytest.mark.parametrize('kind,case,role', [
    ('control', 'success', ''), ('control', 'failure', ''), ('control', 'timeout', ''),
    ('workload', 'S1', 'CPU'), ('workload', 'S1', 'GPU'), ('workload', 'S4', 'TRACE'),
    ('export', 'S1', ''),
])
def test_exact_launch_contract(output, kind, case, role):
    argv = profile.command(output, kind, case, role)
    assert profile.validate_launch(argv, output, kind, case, role) == argv
    if kind != 'export':
        assert str(profile.ENTRY) in argv and str(profile.SELF) in argv
    if kind == 'control':
        assert '--capture-range-end=stop' not in argv
    if role == 'TRACE':
        assert '--capture-range-end=stop' in argv


@pytest.mark.parametrize('change', ['executable', 'shell', 'entry', 'worker', 'extra', 'output'])
def test_native_argv_alternatives_denied(output, change):
    argv = profile.command(output, 'workload', 'S4', 'TRACE')
    if change == 'executable':
        argv[0] = str(profile.ROOT / 'alternate.exe')
    elif change == 'shell':
        argv = ['cmd.exe', '/c', *argv]
    elif change == 'entry':
        argv[argv.index(str(profile.ENTRY))] = '-c'
    elif change == 'worker':
        argv[argv.index(str(profile.SELF))] = str(profile.ROOT / 'arbitrary.py')
    elif change == 'output':
        argv[-1] = str(profile.ROOT / 'data')
    else:
        argv.append('--duration=60')
    with pytest.raises(ValueError, match='NATIVE_ARGV_NOT_EXACT'):
        profile.validate_launch(argv, output, 'workload', 'S4', 'TRACE')


@pytest.mark.parametrize('name,value', [
    ('MALECNS_A019C_R2_FIREWALL', None), ('MALECNS_A019C_R2_FIREWALL', 'corrupt'),
    ('PYTHONPATH', ''), ('PYTHONHOME', 'alternate'), ('PYTHONSTARTUP', 'arbitrary.py'),
])
def test_worker_environment_alternatives_denied(output, name, value):
    env = profile.child_environment()
    if value is None:
        env.pop(name, None)
    else:
        env[name] = value
    with pytest.raises(ValueError, match='CHILD_'):
        profile.validate_launch(profile.command(output, 'workload', 'S1', 'TRACE'),
                                output, 'workload', 'S1', 'TRACE', env)


def test_missing_activation_allowed_only_for_harmless_control(output):
    env = profile.child_environment()
    env.pop('MALECNS_A019C_R2_FIREWALL', None)
    argv = profile.command(output, 'control', 'missing')
    assert profile.validate_launch(argv, output, 'control', 'missing', env=env) == argv


@pytest.mark.parametrize('kind,case,role', [
    ('workload', 'S2', 'TRACE'), ('workload', 'S4', 'TUNE'),
    ('control', 'arbitrary', ''), ('export', 'S4', 'arbitrary'), ('shell', '', ''),
])
def test_unknown_native_roles_denied(output, kind, case, role):
    with pytest.raises(ValueError):
        profile.command(output, kind, case, role)


def test_registered_output_denied_before_launch():
    with pytest.raises(guard.SourceAccessDenied):
        profile.output_root(profile.ROOT / 'data')
    with pytest.raises(ValueError, match='OUTPUT_OUTSIDE'):
        profile.output_root(profile.ROOT / 'docs/plans')
