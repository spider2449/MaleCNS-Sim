"""Freeze finite ordinary package inputs and launch their isolated Linux build."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203'
BASE = '80f57f97eb0429d6d9845766a78e0bc41cd524ca'


def protect(event, arguments):
    if event == 'open' and isinstance(arguments[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(arguments[0])).resolve()
        if (path.is_relative_to(ROOT / 'data') or path.is_relative_to(ROOT / 'artifacts')
                or path.is_relative_to(ROOT / 'docs/references')
                or 'male-cns-v1' in path.as_posix().lower()
                or 'male-cns/v1.0' in path.as_posix().lower()):
            raise PermissionError('A025 protected content denied')


def main() -> None:
    sys.addaudithook(protect)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == BASE
    paths = subprocess.check_output(['git', 'ls-files', 'src'], cwd=ROOT, text=True).splitlines()
    paths += ['pyproject.toml', 'uv.lock', 'MANIFEST.in', 'README.md', 'LICENSE',
              'docs/runtime/USER_GUIDE.md', 'docs/runtime/RELEASE_GATE.md',
              'docs/releases/0.4.0-preparation.md']
    paths = sorted(set(paths))
    controls = ['scripts/a025_container_build.py', 'scripts/a025_container_smoke.py']
    token = uuid.uuid4().hex
    run = Path('C:/TEMP') / ('malecns-a025-candidate-' + token)
    inputs, outputs = run / 'input', run / 'output'
    (inputs / 'package').mkdir(parents=True)
    outputs.mkdir()
    hashes = {}
    for relative in paths + controls:
        source = ROOT / relative
        assert source.resolve().is_relative_to(ROOT)
        assert not any(parent.is_symlink() or parent.is_junction()
                       for parent in [source, *source.parents] if parent.is_relative_to(ROOT))
        content = source.read_bytes()
        target = inputs / ('package/' + relative if relative in paths else Path(relative).name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        hashes[relative] = hashlib.sha256(content).hexdigest()
    candidate = {'base': BASE, 'inputs': {path: hashes[path] for path in paths},
                 'controls': {path: hashes[path] for path in controls}, 'image': IMAGE,
                 'scope': 'Linux CPU artifact development; historical suite not run'}
    (inputs / 'candidate.json').write_text(json.dumps(candidate, indent=2) + '\n')
    name = 'malecns-a025-candidate-' + token
    linux = '/mnt/c/TEMP/' + run.name

    def docker(*arguments):
        return subprocess.check_output(['wsl', '-d', 'Ubuntu-24.04', '--exec', '/usr/bin/docker',
                                        *arguments], text=True, timeout=60)

    created = False
    evidence = {'run': str(run), 'candidate': candidate}
    try:
        container = docker('create', '--name', name, '--pull=never', '--init', '--read-only',
            '--user', '1000:1000', '--cap-drop=ALL', '--security-opt', 'no-new-privileges',
            '--network=bridge', '--pids-limit=256', '--memory=4g', '--cpus=2',
            '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m',
            '--mount', 'type=bind,src=' + linux + '/input,dst=/input,readonly',
            '--mount', 'type=bind,src=' + linux + '/output,dst=/work',
            IMAGE, '/usr/local/bin/python', '-I', '-B', '/input/a025_container_build.py').strip()
        created = True
        info = json.loads(docker('inspect', container))[0]
        host = info['HostConfig']
        assert info['Image'] == IMAGE and info['Config']['User'] == '1000:1000'
        assert not host['Privileged'] and host['ReadonlyRootfs']
        assert host['CapDrop'] == ['ALL'] and host['Devices'] == [] and host['PidMode'] == ''
        assert 'no-new-privileges' in host['SecurityOpt'] and host['NetworkMode'] == 'bridge'
        mounts = {mount['Destination']: mount for mount in info['Mounts']}
        assert set(mounts) == {'/input', '/work'}
        assert mounts['/input']['Source'] == linux + '/input' and not mounts['/input']['RW']
        assert mounts['/work']['Source'] == linux + '/output' and mounts['/work']['RW']
        evidence.update(container=container, configuration=host, mounts=info['Mounts'])
        (run / 'controller.json').write_text(json.dumps(evidence, indent=2) + '\n')
        print('A025 isolated candidate: ' + str(run), flush=True)
        with (run / 'container.log').open('w', encoding='utf-8') as log:
            subprocess.run(['wsl', '-d', 'Ubuntu-24.04', '--exec', '/usr/bin/docker',
                            'start', '--attach', container], stdout=log, stderr=subprocess.STDOUT,
                           check=True, timeout=1800)
        state = json.loads(docker('inspect', container))[0]['State']
        evidence['terminal_state'] = state
        assert state['ExitCode'] == 0 and not state['Running'], 'candidate failed; inspect preserved logs'
        after = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in hashes}
        assert after == hashes, 'source/control changed during candidate run'
        evidence.update(status='LINUX CPU BUILD AND SMOKE PASS', before_after_equal=True)
    finally:
        if created:
            state = json.loads(docker('inspect', name))[0]['State']
            if state['Running']:
                docker('stop', '--time', '10', name)
            docker('rm', name)
            assert not docker('ps', '--all', '--quiet', '--filter', 'name=^/' + name + '$').strip()
            evidence['cleanup'] = 'container removed; no matching container remains'
        (run / 'controller.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'status': evidence['status'], 'run': str(run)}))


if __name__ == '__main__':
    raise SystemExit('EXECUTION_DENIED: full Windows/GPU A023 gate is required; Linux development cannot close A025')
