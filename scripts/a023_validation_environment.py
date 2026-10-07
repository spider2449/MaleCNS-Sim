"""Provision genuine package metadata and frozen GPU validation prerequisites."""

from pathlib import Path
import subprocess

from a023_release_validation import sha


def expected_validation_dependencies(lock):
    """Resolve project, runtime, dev and nested GPU extras without changing lock."""
    from packaging.markers import Marker
    from packaging.utils import canonicalize_name

    active = {}
    for package in lock['package']:
        markers = package.get('resolution-markers', [])
        if not markers or any(Marker(marker).evaluate() for marker in markers):
            name = canonicalize_name(package['name'])
            if name in active:
                raise ValueError('ambiguous active lock package')
            active[name] = package
    project = active['malecns-sim']
    queue = [{'name': 'malecns-sim', 'extra': ['gpu']}]
    queue.extend(project['dev-dependencies']['dev'])
    expanded = set()
    result = set()
    while queue:
        dependency = queue.pop()
        if dependency.get('marker') and not Marker(dependency['marker']).evaluate():
            continue
        name = canonicalize_name(dependency['name'])
        package = active[name]
        if dependency.get('version') and dependency['version'] != package['version']:
            raise ValueError('lock dependency version mismatch')
        result.add((name, package['version']))
        for extra in (None, *dependency.get('extra', [])):
            key = (name, extra)
            if key in expanded:
                continue
            expanded.add(key)
            if extra is None:
                queue.extend(package.get('dependencies', []))
            else:
                try:
                    queue.extend(package['optional-dependencies'][extra])
                except KeyError as exc:
                    raise ValueError('unknown lock extra: ' + str(key)) from exc
    return result


def check_dependencies(installed, lock):
    """Reject missing, duplicate, drifted or additional distributions."""
    expected = sorted(expected_validation_dependencies(lock))
    if sorted(installed) != expected:
        raise RuntimeError('validation dependency closure differs from frozen lock')
    return expected


def package_inputs(tree, candidate):
    """Only frozen packaging/source inputs enter the independent build copy."""
    tree = Path(tree)
    if any((tree / root).exists() for root in ('data', 'artifacts')):
        raise RuntimeError('protected root materialized before package provisioning')
    required = {'pyproject.toml', 'README.md', 'LICENSE', 'MANIFEST.in'}
    if not required.issubset(candidate):
        raise RuntimeError('packaging inputs are not frozen')
    return sorted(required | {path for path in candidate if path.startswith('src/')})


def provision(tree, run, uv, python, environment, candidate):
    """Install lock dependencies and a local wheel before final validation."""
    tree, run = Path(tree), Path(run)
    inputs = package_inputs(tree, candidate)
    subprocess.run([uv, 'sync', '--python', python, '--frozen', '--group', 'dev',
                    '--extra', 'gpu', '--no-install-project', '--no-config'],
                   cwd=tree, env=environment, check=True)
    staging = run / 'package-build'
    staging.mkdir()
    for path in inputs:
        source, destination = tree / path, staging / path
        content = source.read_bytes()
        if sha(content) != candidate[path]:
            raise RuntimeError('packaging input drift: ' + path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    wheels = run / 'wheels'
    wheels.mkdir()
    subprocess.run([uv, 'build', '--wheel', '--python', python, '--out-dir', str(wheels), '--no-config'],
                   cwd=staging, env=environment, check=True)
    built = list(wheels.glob('*.whl'))
    if len(built) != 1:
        raise RuntimeError('expected exactly one local validation wheel')
    wheel = built[0]
    subprocess.run([uv, 'pip', 'install', '--python', str(tree / '.venv/Scripts/python.exe'),
                    '--no-deps', '--no-config', str(wheel)],
                   cwd=tree, env=environment, check=True)
    if any(sha((tree / path).read_bytes()) != expected for path, expected in candidate.items()):
        raise RuntimeError('frozen source changed during provisioning')
    return {'wheel': str(wheel), 'wheel_sha256': sha(wheel.read_bytes()),
            'packaging_inputs': {path: candidate[path] for path in inputs},
            'installed_project': True, 'extras': ['gpu'], 'release_packaging_certified': False}


def inspect_environment(tree, lock):
    """Verify installed metadata, source authority and a usable GPU before pytest."""
    import importlib.metadata
    import importlib.util
    from packaging.utils import canonicalize_name

    installed = sorted((canonicalize_name(package.metadata['Name']), package.version)
                       for package in importlib.metadata.distributions())
    check_dependencies(installed, lock)
    source = Path(importlib.util.find_spec('malecns_sim').origin).resolve()
    if source != (Path(tree) / 'src/malecns_sim/__init__.py').resolve():
        raise RuntimeError('validation source import is not the frozen execution tree')
    import cupy as cp
    devices = cp.cuda.runtime.getDeviceCount()
    if devices < 1:
        raise RuntimeError('synthetic GPU validation requires a usable device')
    return {'dependencies': installed, 'source_origin': str(source), 'gpu_device_count': devices}
