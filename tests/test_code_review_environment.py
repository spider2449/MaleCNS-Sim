"""Environment recovery controls without protected payload or performance claims."""

import copy
from pathlib import Path
import tomllib

import pytest

from a023_validation_environment import (
    check_dependencies, expected_validation_dependencies, inspect_environment, package_inputs,
)

ROOT = Path(__file__).resolve().parents[1]


def locked():
    return tomllib.loads((ROOT / 'uv.lock').read_text())


def test_gpu_closure_is_complete_and_does_not_mutate_lock():
    lock = locked()
    before = copy.deepcopy(lock)
    expected = expected_validation_dependencies(lock)
    assert ('malecns-sim', '0.3.0') in expected
    assert ('cupy-cuda12x', '14.2.0') in expected
    assert ('cuda-toolkit', '12.9.2.0') in expected
    assert {'nvidia-cuda-runtime-cu12', 'nvidia-cuda-nvrtc-cu12', 'nvidia-cublas-cu12',
            'nvidia-cufft-cu12', 'nvidia-curand-cu12', 'nvidia-cusolver-cu12',
            'nvidia-cusparse-cu12', 'nvidia-nvjitlink-cu12'} <= {name for name, _ in expected}
    assert lock == before


@pytest.mark.parametrize('change', ['project', 'gpu', 'extra', 'duplicate', 'version'])
def test_dependency_census_rejects_incomplete_or_changed_environment(change):
    lock = locked()
    installed = sorted(expected_validation_dependencies(lock))
    if change in ('project', 'gpu'):
        missing = 'malecns-sim' if change == 'project' else 'cupy-cuda12x'
        installed = [item for item in installed if item[0] != missing]
    elif change == 'extra':
        installed.append(('foreign-package', '1.0'))
    elif change == 'duplicate':
        installed.append(installed[0])
    else:
        installed = [(name, '0.0' if name == 'malecns-sim' else version)
                     for name, version in installed]
    with pytest.raises(RuntimeError, match='dependency closure'):
        check_dependencies(installed, lock)


def test_late_extra_expansion_and_cycles():
    lock = {'package': [
        {'name': 'malecns-sim', 'version': '0.3.0',
         'dependencies': [{'name': 'shared'}],
         'optional-dependencies': {'gpu': [{'name': 'shared', 'extra': ['device']}]},
         'dev-dependencies': {'dev': [{'name': 'shared'}]}},
        {'name': 'shared', 'version': '1', 'dependencies': [{'name': 'shared'}],
         'optional-dependencies': {'device': [{'name': 'driver'}]}},
        {'name': 'driver', 'version': '2'},
    ]}
    assert expected_validation_dependencies(lock) == {
        ('malecns-sim', '0.3.0'), ('shared', '1'), ('driver', '2')}


@pytest.mark.parametrize('root', ['data', 'artifacts'])
def test_provisioning_rejects_materialized_protected_root(tmp_path, root):
    (tmp_path / root).mkdir()
    with pytest.raises(RuntimeError, match='protected root materialized'):
        package_inputs(tmp_path, {})


def test_frozen_packaging_inputs_are_required(tmp_path):
    with pytest.raises(RuntimeError, match='packaging inputs are not frozen'):
        package_inputs(tmp_path, {'src/malecns_sim/__init__.py': 'mock digest'})


def test_genuine_project_metadata_and_gpu_prerequisites():
    evidence = inspect_environment(ROOT, locked())
    assert evidence['gpu_device_count'] >= 1
    assert ('malecns-sim', '0.3.0') in evidence['dependencies']
    assert Path(evidence['source_origin']) == ROOT / 'src/malecns_sim/__init__.py'
