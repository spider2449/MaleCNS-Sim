"""Provenance fixture closure leaves all Git execution denied."""
import subprocess
import json

import pytest
import validation_firewall as guard


def test_historical_code_fixture_is_fixed_and_verified(monkeypatch):
    import test_application_a018ui as historical
    from pathlib import Path
    for key in historical.PINNED_CODE_HASHES:
        revision, path = key.split(':', 1)
        assert historical.historical_source(path, revision)
    with pytest.raises(KeyError):
        historical.historical_source('data/derived/task008-results.json')
    with pytest.raises(KeyError):
        historical.historical_source('src/malecns_sim/dynamics/lif.py', 'HEAD')
    fixture_path = historical.ROOT / 'tests/fixtures/application-a019c-historical-code.json'
    payload = json.loads(fixture_path.read_text())
    key = historical.HISTORICAL + ':src/malecns_sim/dynamics/lif.py'
    payload['sources'][key]['source'] += '\n# Corrupted synthetic oracle.\n'
    original = Path.read_text
    monkeypatch.setattr(Path, 'read_text', lambda self, *a, **k:
                        json.dumps(payload) if self == fixture_path else original(self, *a, **k))
    with pytest.raises(AssertionError):
        historical.historical_source('src/malecns_sim/dynamics/lif.py')


def test_production_provenance_rejection_is_optional(monkeypatch):
    from pathlib import Path
    from malecns_sim.application import service
    original = subprocess.Popen
    calls = []

    def observe(argv, **kwargs):
        calls.append((argv, kwargs['cwd']))
        return original(argv, **kwargs)

    monkeypatch.setattr(subprocess, 'Popen', observe)
    assert service._git_provenance() == {'git_commit': None, 'git_dirty': None}
    assert calls == [(['git', 'rev-parse', '--show-toplevel'],
                      Path(service.__file__).resolve().parent)]


def test_git_execution_remains_denied(tmp_path):
    git = 'C:/Program Files/Git/cmd/git.exe'
    for argv in ([git, 'rev-parse', 'HEAD'], ['git', 'status', '--porcelain'],
                 [git, 'diff'], [git, 'cat-file', '-p', 'HEAD'],
                 ['cmd.exe', '/c', git, 'rev-parse', 'HEAD']):
        for cwd in (str(guard.ROOT), str(tmp_path)):
            with pytest.raises(guard.SourceAccessDenied):
                subprocess.run(argv, cwd=cwd, capture_output=True, timeout=2)
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run([git, 'rev-parse', 'HEAD'], shell=True)
    with pytest.raises(guard.SourceAccessDenied):
        (guard.ROOT / 'data/male-cns-v1-connectome.feather').read_bytes()
