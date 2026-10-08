"""Fresh Windows/GPU validation and CPU artifacts inside an AppContainer."""
from __future__ import annotations

import ctypes
from ctypes import wintypes as W
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback
import tomllib
import zipfile
import threading
from concurrent.futures import ThreadPoolExecutor


def main(run):
    run = Path(run)
    tree = run.parent / 'input/execution'
    tools = run.parent / 'tools'
    frozen = json.loads((tree / 'docs/manifests/a025-frozen-candidate.json').read_text())
    for relative, expected in frozen['candidate'].items():
        assert hashlib.sha256((tree / relative).read_bytes()).hexdigest() == expected
    for denied in ('D:/spider/working/MaleCNS-Sim/data', 'D:/spider/working/MaleCNS-Sim/artifacts'):
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, ctypes.c_void_p, W.DWORD, W.DWORD, W.HANDLE]
        kernel.CreateFileW.restype = W.HANDLE
        handle = kernel.CreateFileW(denied, 0x80000000, 7, None, 3, 0x02000000, None)
        assert handle == ctypes.c_void_p(-1).value and ctypes.get_last_error() == 5
    for name in ('temp', 'home', 'evidence', 'uv-cache', 'cupy-cache', 'cuda-cache', 'npm-cache', 'pytest-cache'):
        (run / name).mkdir(exist_ok=True)
    environment = dict(os.environ, UV_CACHE_DIR=str(run / 'uv-cache'), UV_NO_PROGRESS='1',
        PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',
        TEMP=str(run / 'temp'), TMP=str(run / 'temp'),
        CUPY_CACHE_DIR=str(run / 'cupy-cache'), CUDA_CACHE_PATH=str(run / 'cuda-cache'))
    commands = []
    command_lock = threading.Lock()

    def command(arguments, cwd=run, env=environment, timeout=1800):
        arguments = list(map(str, arguments))
        with command_lock:
            log = run / 'evidence' / f'command-{len(commands):02}.log'
            stream = log.open('w', encoding='utf-8')
            try:
                process = subprocess.Popen(arguments, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT)
            except BaseException:
                stream.close()
                raise
            record = {'argv': arguments, 'cwd': str(cwd), 'pid': process.pid, 'log': str(log)}
            commands.append(record)
            (run / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        with stream:
            try:
                record['exit'] = process.wait(timeout=timeout)
            except BaseException:
                process.kill()
                process.wait()
                raise
        with command_lock:
            (run / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        if record['exit']:
            raise RuntimeError('command failed: ' + str(log))

    bundled, = (tools / 'Lib/ensurepip/_bundled').glob('pip-*.whl')
    pip_tool = run / 'pip-tool'
    with zipfile.ZipFile(bundled) as archive:
        archive.extractall(pip_tool)
    bootstrap = ('import sys,runpy,faulthandler; faulthandler.dump_traceback_later(30,repeat=True); sys.path.insert(0,' + repr(str(pip_tool))
                 + "); runpy.run_module('pip',run_name='__main__')")
    sys.path.insert(0, str(pip_tool / 'pip/_vendor'))
    sys.path.insert(0, str(tree / 'scripts'))
    from packaging.tags import sys_tags
    from packaging.utils import parse_wheel_filename, canonicalize_name
    from a023_validation_environment import expected_validation_dependencies
    from a023_local_repro import expected_dependencies
    lock = tomllib.loads((tree / 'uv.lock').read_text())
    tags = {tag: index for index, tag in enumerate(sys_tags())}

    def file_hash(path):
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        return digest.hexdigest()

    def requirements(names, destination):
        lines = []
        downloads = run / 'locked-wheels'
        downloads.mkdir(exist_ok=True)
        pending = []
        pieces = []
        piece_root = run / 'download-pieces'
        piece_root.mkdir(exist_ok=True)
        for name, version in sorted(names):
            if name == 'malecns-sim':
                continue
            entry, = (entry for entry in lock['package'] if canonicalize_name(entry['name']) == name)
            assert entry['version'] == version
            wheels = []
            for wheel in entry['wheels']:
                filename = wheel['url'].rsplit('/', 1)[1]
                wheel_tags = parse_wheel_filename(filename)[3]
                matches = [tags[tag] for tag in wheel_tags if tag in tags]
                if matches:
                    wheels.append((min(matches), wheel))
            assert wheels, 'no compatible frozen wheel for ' + name
            wheel = min(wheels, key=lambda match: match[0])[1]
            downloaded = downloads / wheel['url'].rsplit('/', 1)[1]
            seed = run.parent / 'input/dependency-seeds' / downloaded.name
            if not downloaded.exists() and seed.exists():
                shutil.copy2(seed, downloaded)
            size = downloaded.stat().st_size if downloaded.exists() else 0
            assert size <= wheel['size']
            for start in range(size, wheel['size'], 8 * 1024 * 1024):
                end = min(start + 8 * 1024 * 1024, wheel['size']) - 1
                part = piece_root / (downloaded.name + f'.{start}-{end}.part')
                pieces.append((wheel, start, end, part))
            pending.append((downloaded, wheel))
            lines.append(name + '==' + version + ' --hash=' + wheel['hash'])
        def download_piece(item):
            wheel, start, end, part = item
            headers = part.with_suffix('.headers')
            download_url = wheel['url'].replace('https://files.pythonhosted.org/',
                                               'https://mirrors.aliyun.com/pypi/')
            command([tools / 'curl.exe', '--fail', '--silent', '--show-error',
                     '--max-time', '7000', '--range', f'{start}-{end}', '--dump-header', headers,
                     '--output', part, download_url], timeout=7200)
            assert part.stat().st_size == end - start + 1
            actual_headers = headers.read_text(encoding='ascii').lower().splitlines()
            assert f'content-range: bytes {start}-{end}/{wheel["size"]}' in actual_headers
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(download_piece, pieces))
        for downloaded, wheel in pending:
            with downloaded.open('ab') as target:
                for piece_wheel, start, end, part in pieces:
                    if piece_wheel['url'] == wheel['url']:
                        with part.open('rb') as source:
                            shutil.copyfileobj(source, target, 1024 * 1024)
            assert downloaded.stat().st_size == wheel['size']
            assert 'sha256:' + file_hash(downloaded) == wheel['hash']
        destination.write_text('\n'.join(lines) + '\n')

    def venv(path):
        command([tools / 'python.exe', '-I', '-m', 'venv', '--without-pip', path])
        for name in ('a025_tempfile_compat.py', 'a025-tempfile-compat.pth',
                     'a025_path_compat.py', 'a025-path-compat.pth', 'a025-volume-map.json'):
            shutil.copy2(tools / 'Lib/site-packages' / name, path / 'Lib/site-packages' / name)
        shutil.copy2(tree / 'scripts/a025_symlink_compat.py', path / 'Lib/site-packages/a025_symlink_compat.py')
        (path / 'Lib/site-packages/a025-symlink-compat.pth').write_text(
            'import a025_symlink_compat; a025_symlink_compat.install()\n')
        return path / 'Scripts/python.exe'

    def pip(python, arguments):
        arguments = [arguments[0], '--progress-bar', 'off', '--no-index',
                     '--find-links', str(run / 'locked-wheels'), *arguments[1:]]
        command([python, '-I', '-B', '-c', bootstrap,
                 '--isolated', '--disable-pip-version-check', *arguments])

    validation_python = venv(tree / '.venv')
    gpu_requirements = run / 'gpu-requirements.txt'
    gpu_dependencies = expected_validation_dependencies(lock)
    assert {'nvidia-cuda-runtime-cu12', 'nvidia-cuda-nvrtc-cu12', 'nvidia-cublas-cu12',
            'nvidia-cufft-cu12', 'nvidia-curand-cu12', 'nvidia-cusolver-cu12',
            'nvidia-cusparse-cu12', 'nvidia-nvjitlink-cu12'} <= {name for name, _ in gpu_dependencies}
    (run / 'dependency-plan.json').write_text(json.dumps(sorted(gpu_dependencies), indent=2) + '\n')
    requirements(gpu_dependencies, gpu_requirements)
    pip(validation_python, ['install', '--no-cache-dir', '--no-deps', '--only-binary=:all:',
                            '--require-hashes', '-r', gpu_requirements])
    command([tools / 'uv.exe', 'sync', '--frozen', '--group', 'dev', '--extra', 'gpu',
             '--no-install-project', '--offline', '--no-build', '--no-managed-python',
             '--python', validation_python], tree)
    package = run / 'package'
    package.mkdir()
    package_paths = [path for path in frozen['candidate'] if path.startswith('src/')]
    package_paths += ['pyproject.toml', 'uv.lock', 'MANIFEST.in', 'README.md', 'LICENSE',
                     'docs/runtime/USER_GUIDE.md', 'docs/runtime/RELEASE_GATE.md',
                     'docs/releases/0.4.0-preparation.md']
    for relative in package_paths:
        source, target = tree / relative, package / relative
        content = source.read_bytes()
        assert hashlib.sha256(content).hexdigest() == frozen['candidate'][relative]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    build_python = venv(run / 'build-env')
    build_requirements = run / 'build-requirements.txt'
    setuptools_wheel = run / 'locked-wheels/setuptools-80.9.0-py3-none-any.whl'
    command([tools / 'curl.exe', '--fail', '--silent', '--show-error', '--max-time', '1700',
             '--output', setuptools_wheel,
             'https://mirrors.aliyun.com/pypi/packages/a3/dc/17031897dae0efacfea57dfd3a82fdd2a2aeb58e0ff71b77b87e44edc772/setuptools-80.9.0-py3-none-any.whl'])
    assert hashlib.sha256(setuptools_wheel.read_bytes()).hexdigest() == '062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922'
    build_requirements.write_text(
        'setuptools @ ' + setuptools_wheel.as_uri() + ' '
        '--hash=sha256:062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922\n')
    pip(build_python, ['install', '--no-cache-dir', '--no-deps', '--only-binary=:all:',
                       '--require-hashes', '-r', build_requirements])
    (run / 'dist').mkdir()
    backend = ('from setuptools.build_meta import build_wheel,build_sdist; '
               'build_wheel(' + repr(str(run / 'dist')) + '); build_sdist(' + repr(str(run / 'dist')) + ')')
    command([build_python, '-I', '-B', '-c', backend], package)
    wheel, = (run / 'dist').glob('*.whl')
    pip(validation_python, ['install', '--no-deps', wheel])
    from a023_local_repro import admitted_environment
    final_environment = admitted_environment(run, tree)
    final_environment['MALECNS_A025_OUTPUT'] = str(run)
    for key in ('MALECNS_A025_SYMLINK_URL', 'MALECNS_A025_SYMLINK_TOKEN'):
        final_environment[key] = os.environ[key]
    final_environment['PATH'] += os.pathsep + 'C:/Program Files/nodejs'
    command([validation_python, '-B', tree / 'scripts/a025_release_validation.py', run], tree, final_environment)
    command([validation_python, '-I', '-B', tree / 'scripts/a025_container_smoke.py', '--gpu-guide', run])
    cpu_python = venv(package / '.venv')
    cpu_requirements = run / 'cpu-requirements.txt'
    cpu_lock = json.loads(json.dumps(lock))
    next(entry for entry in cpu_lock['package'] if entry['name'] == 'malecns-sim')['dev-dependencies']['dev'] = []
    expected_cpu = set(expected_dependencies(cpu_lock))
    requirements(expected_cpu, cpu_requirements)
    pip(cpu_python, ['install', '--no-cache-dir', '--no-deps', '--only-binary=:all:',
                     '--require-hashes', '-r', cpu_requirements])
    pip(cpu_python, ['install', '--no-deps', wheel])
    command([cpu_python, '-I', '-B', tree / 'scripts/a025_container_smoke.py', run])
    after = {path: hashlib.sha256((tree / path).read_bytes()).hexdigest() for path in frozen['candidate']}
    assert after == frozen['candidate']
    result = {'status': 'WINDOWS GPU SUITE AND CPU ARTIFACT PASS', 'commands': commands,
              'immutable': True, 'I1': 'NOT RUN - REGISTERED-PAYLOAD-REQUIRED'}
    (run / 'result.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except BaseException:
        (Path(sys.argv[1]) / 'worker-error.txt').write_text(traceback.format_exc())
        raise SystemExit(1)
