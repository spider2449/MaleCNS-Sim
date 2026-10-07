"""Development regressions using mocks, without scientific execution."""

from types import ModuleType, SimpleNamespace
import threading

import pytest

from a023_release_validation import Collection
from malecns_sim.application import server
from malecns_sim.application.errors import ApplicationError, ErrorCode


def test_actual_builtin_plugin_census(request):
    observer = Collection({}, None)
    observer.pytest_sessionstart(request.session)
    assert observer.plugins
    assert any(entry['module'] == '_pytest.legacypath' for entry in observer.plugins)


@pytest.mark.parametrize('outcome', ['success', 'application_error', 'unexpected_error'])
def test_completion_cannot_clear_a_new_run(monkeypatch, tmp_path, outcome):
    manager = server.RunManager(SimpleNamespace(files=(), engine=None), tmp_path)
    first = server.RunRecord('first', object())
    manager.active = True
    admitted = []

    class InterleavingLock:
        def __init__(self):
            self.lock = threading.Lock()

        def __enter__(self):
            self.lock.acquire()

        def __exit__(self, *args):
            self.lock.release()
            # Admit the next run at the first release of the idle manager.
            if not manager.active and not admitted:
                admitted.append(manager.create(object()))

    manager.lock = InterleavingLock()
    monkeypatch.setattr(server.threading, 'Thread',
                        lambda **kwargs: SimpleNamespace(start=lambda: None))

    def execute(*args, **kwargs):
        if outcome == 'application_error':
            raise ApplicationError(ErrorCode.SIMULATION_FAILED, 'mock failure')
        if outcome == 'unexpected_error':
            raise RuntimeError('mock failure')
        return SimpleNamespace(status='COMPLETED')

    monkeypatch.setattr(server, 'run_experiment', execute)
    monkeypatch.setattr(server, 'write_result', lambda *args: 'mock digest')
    monkeypatch.setattr(server, 'read_result', lambda *args, **kwargs: None)
    manager._execute(first)
    assert first.state == ('COMPLETED' if outcome == 'success' else 'FAILED')
    assert len(admitted) == 1 and manager.active
    with pytest.raises(ApplicationError, match='already active'):
        manager.create(object())


@pytest.mark.parametrize('representation', ['module', 'class', 'instance'])
@pytest.mark.parametrize('trusted', [True, False])
def test_plugin_census_uses_defining_module(representation, trusted):
    module = '_pytest.review_control' if trusted else 'foreign_plugin'
    plugin_class = type('LegacyTmpdirPlugin', (), {'__module__': module})
    plugin = {'module': ModuleType(module), 'class': plugin_class,
              'instance': plugin_class()}[representation]
    manager = SimpleNamespace(list_name_plugin=lambda: [('control', plugin)])
    session = SimpleNamespace(config=SimpleNamespace(pluginmanager=manager))
    observer = Collection({}, None)
    if trusted:
        observer.pytest_sessionstart(session)
        assert observer.plugins == [{'name': 'control', 'module': module}]
    else:
        with pytest.raises(RuntimeError, match='uncontrolled pytest plugin: foreign_plugin'):
            observer.pytest_sessionstart(session)
