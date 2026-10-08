"""Provision and build ordinary candidate inputs inside a finite mount boundary."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def main() -> None:
    work = Path('/work')
    package = work / 'package'
    shutil.copytree('/input/package', package)
    environment = dict(os.environ, HOME='/work/home', UV_CACHE_DIR='/work/uv-cache',
                       PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1',
                       PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    commands = []

    def run(arguments, cwd=work):
        log = work / f'command-{len(commands):02}.log'
        with log.open('w') as output:
            result = subprocess.run(list(map(str, arguments)), cwd=cwd, env=environment,
                                    stdout=output, stderr=subprocess.STDOUT, timeout=600)
        commands.append({'argv': list(map(str, arguments)), 'cwd': str(cwd),
                         'exit': result.returncode, 'log': log.name})
        (work / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        if result.returncode:
            print(log.read_text(), flush=True)
            raise RuntimeError('command failed: ' + log.name)

    run([sys.executable, '-I', '-m', 'pip', 'install', '--no-cache-dir', '--target',
         '/work/tools', 'uv==0.11.8'])
    uv = '/work/tools/bin/uv'
    run([uv, 'venv', '--python', sys.executable, '/work/build-env', '--no-config'])
    build_python = '/work/build-env/bin/python'
    run([uv, 'pip', 'install', '--python', build_python, '--no-config', 'setuptools==80.9.0'])
    run([uv, 'sync', '--python', sys.executable, '--frozen', '--no-dev',
         '--no-install-project', '--no-config'], package)
    run([uv, 'build', '--python', build_python, '--no-build-isolation', '--no-config',
         '--out-dir', '/work/dist'], package)
    wheel, = (work / 'dist').glob('*.whl')
    run([uv, 'venv', '--python', sys.executable, '/work/installed-env', '--no-config'])
    installed_python = '/work/installed-env/bin/python'
    import tomllib
    lock = tomllib.loads((package / 'uv.lock').read_text())
    names = {'numpy', 'pandas', 'pyarrow', 'scipy', 'python-dateutil', 'six'}
    pins = [entry['name'] + '==' + entry['version'] for entry in lock['package'] if entry['name'] in names]
    assert {pin.split('==')[0] for pin in pins} == names
    run([uv, 'pip', 'install', '--python', installed_python, '--no-config', *pins])
    run([uv, 'pip', 'install', '--python', installed_python, '--no-deps', '--no-config', wheel])
    run([installed_python, '-I', '-B', '/input/a025_container_smoke.py'])
    source = json.loads(Path('/input/candidate.json').read_text())
    actual = {path: hashlib.sha256((package / path).read_bytes()).hexdigest() for path in source['inputs']}
    assert actual == source['inputs'], 'candidate copy changed during build/smoke'
    (work / 'build-result.json').write_text(json.dumps({
        'status': 'LINUX CPU BUILD AND SMOKE PASS', 'commands': commands,
        'input_hashes_equal': True, 'source': source,
        'full_release_safe_suite': 'NOT RUN',
    }, indent=2) + '\n')
    print('LINUX CPU BUILD AND SMOKE PASS', flush=True)


if __name__ == '__main__':
    main()
