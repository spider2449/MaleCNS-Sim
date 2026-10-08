"""Freeze and execute an A025 candidate in the certified native Windows boundary."""
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
import uuid
import tomllib

ROOT = Path(__file__).resolve().parents[1]
BASE = '80f57f97eb0429d6d9845766a78e0bc41cd524ca'


def guard(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).resolve()
        if (any(path.is_relative_to(ROOT / denied) for denied in ('data', 'artifacts', 'docs/references'))
                or 'male-cns-v1' in path.as_posix().lower() or 'male-cns/v1.0' in path.as_posix().lower()):
            raise PermissionError('A025 protected content denied before transfer')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    sys.addaudithook(guard)
    sys.path.insert(0, str(ROOT / 'scripts'))
    from a025_windows_isolation import launch, api, require, prepare_tempfile_compat
    from a023_local_repro import Job
    from a025_metadata_controls import MetadataRights
    from a025_symlink_broker import SyntheticSymlinkBroker
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == BASE
    if len(sys.argv) != 4:
        raise SystemExit('usage: a025_windows_candidate.py <fresh-isolation-certificate> <closed-dependency-cache-run> <fresh-symlink-certificate>')
    certificate = Path(sys.argv[1]).resolve(strict=True)
    assert certificate.parent.parent == Path('C:/TEMP') and certificate.name == 'isolation.json'
    certification = json.loads(certificate.read_text())
    assert certification['status'] == 'PASS' and certification['immutable']
    assert certification['probe']['gpu_device_count'] >= 1 and certification['profile_cleanup_hresult'] == 0
    assert certification['controller_sha256'] == sha(ROOT / 'scripts/a025_windows_isolation.py')
    assert certification['probe']['loopback'] == 'PASS' and certification['probe']['node'] == 'v24.13.0'
    assert 'pip 25.2' in certification['probe']['pip_target_environment']
    assert certification['probe']['pip_hashed_wheel_install'] == 'PASS'
    assert certification['probe']['uv_frozen_sync_control']['status'] == 'PASS'
    assert certification['probe']['uv_interpreter_query']['exit'] == 0
    assert certification['probe']['original_environment_private_output'] == 'PASS'
    assert certification['probe']['strict_native_path_resolution'] == 'PASS'
    assert certification['probe']['stock_python_startup_without_warning'] == 'PASS'
    assert certification['probe']['node_main_module_metadata'] == 'PASS'
    assert len(certification['probe']['metadata_device_denials']) == 4
    assert certification['metadata_cleanup'] == 'temporary profile SID entries removed'
    assert certification['metadata_helper_sha256'] == sha(ROOT / 'scripts/a025_metadata_controls.py')
    assert certification['probe']['nsight_suspended_native_create_cleanup']['status'] == 'PASS'
    nsight = Path('C:/Program Files/NVIDIA Corporation/Nsight Systems 2025.5.2/target-windows-x64/nsys.exe')
    assert certification['nsight_sha256'] == sha(nsight)
    assert certification['nsight_cleanup'] == 'temporary SID grant removed; tool bytes unchanged'
    symlink_certificate = Path(sys.argv[3]).resolve(strict=True)
    assert symlink_certificate.parent.parent == Path('C:/TEMP') and symlink_certificate.name == 'symlink.json'
    symlink_controls = json.loads(symlink_certificate.read_text())
    assert symlink_controls['status'] == 'PASS' and symlink_controls['profile_cleanup_hresult'] == 0
    assert symlink_controls['broker_cleanup'] == 'closed' and symlink_controls['probe']['skipped'] == 0
    assert symlink_controls['outside_request_denial'].startswith('PASS')
    assert symlink_controls['control_sha256'] == sha(ROOT / 'scripts/a025_symlink_controls.py')
    assert all(sha(ROOT / 'scripts' / name) == expected for name, expected in symlink_controls['helpers'].items())
    assert all(sha(ROOT / name) == expected for name, expected in symlink_controls['original_source_hashes'].items())
    historical = json.loads((ROOT / 'docs/manifests/a023r11-frozen-candidate.json').read_text())
    paths = set(historical['candidate'])
    paths.update(('docs/runtime/USER_GUIDE.md', 'docs/runtime/RELEASE_GATE.md',
                  'docs/releases/0.4.0-preparation.md', 'scripts/a025_release_validation.py',
                  'scripts/a025_windows_worker.py', 'scripts/a025_container_smoke.py',
                  'scripts/a025_windows_isolation.py', 'scripts/a025_windows_candidate.py',
                  'scripts/a025_tempfile_compat.py',
                  'scripts/a025_path_compat.py', 'scripts/a025_metadata_controls.py',
                  'scripts/a025_symlink_broker.py', 'scripts/a025_symlink_compat.py', 'scripts/a025_symlink_controls.py',
                  'docs/plans/2026-10-08-application-a025-windows-isolation.md',
                  'docs/plans/2026-10-08-application-a025-v040-release-candidate.md',
                  'docs/plans/2026-10-08-application-a025-route-recertification.md'))
    paths.discard('docs/manifests/a023r11-frozen-candidate.json')
    assert not any(path.startswith(('data/', 'artifacts/', 'docs/references/')) for path in paths)
    run = Path('C:/TEMP') / ('malecns-a025-windows-candidate-' + uuid.uuid4().hex)
    tree, tools, output = run / 'input/execution', run / 'tools', run / 'output'
    tree.mkdir(parents=True)
    (tree / '.venv').mkdir()
    tools.mkdir()
    output.mkdir()
    (output / 'temp').mkdir()
    seed_root = run / 'input/dependency-seeds'
    seed_root.mkdir()
    seeds = {}
    if len(sys.argv) >= 3:
        cache_run = Path(sys.argv[2]).resolve(strict=True)
        assert cache_run.parent == Path('C:/TEMP') and cache_run.name.startswith('malecns-a025-windows-candidate-')
        producer = json.loads((cache_run / 'controller.json').read_text())
        assert producer['base'] == BASE and producer['profile_cleanup_hresult'] == 0
        assert producer['job_cleanup'] == 'closed; kill-on-close retained'
        for package in tomllib.loads((ROOT / 'uv.lock').read_text())['package']:
            for wheel in package.get('wheels', []):
                name = wheel['url'].rsplit('/', 1)[1]
                source = cache_run / 'output/locked-wheels' / name
                if not source.exists() or name in seeds:
                    continue
                assert source.resolve().is_relative_to(cache_run / 'output/locked-wheels')
                assert not any(path.is_symlink() or path.is_junction() for path in [source, *source.parents]
                               if path.is_relative_to(cache_run))
                size = source.stat().st_size
                assert size <= wheel['size']
                if not size:
                    continue
                target = seed_root / name
                shutil.copy2(source, target)
                with target.open('rb') as stream:
                    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                if size == wheel['size']:
                    assert 'sha256:' + digest == wheel['hash']
                seeds[name] = {'bytes': size, 'sha256': digest, 'artifact_sha256': wheel['hash'],
                               'state': 'COMPLETE HASH VERIFIED' if size == wheel['size'] else 'QUARANTINED PREFIX - NOT INSTALLABLE'}
    hashes = {}
    for relative in sorted(paths):
        source = ROOT / relative
        assert source.resolve().is_relative_to(ROOT)
        assert not any(path.is_symlink() or path.is_junction() for path in [source, *source.parents]
                       if path.is_relative_to(ROOT))
        content = source.read_bytes()
        target = tree / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        hashes[relative] = hashlib.sha256(content).hexdigest()
    frozen = dict(historical, base=BASE, candidate=hashes)
    (tree / 'docs/manifests/a025-frozen-candidate.json').write_text(json.dumps(frozen, indent=2) + '\n')
    runtime = Path(sys._base_executable).parent
    for path in runtime.iterdir():
        if path.is_file() and (path.suffix.lower() == '.dll' or path.name == 'python.exe'):
            shutil.copy2(path, tools / path.name)
    for name in ('Lib', 'DLLs'):
        shutil.copytree(runtime / name, tools / name,
                       ignore=shutil.ignore_patterns('__pycache__', 'site-packages'))
    prepare_tempfile_compat(tools)
    shutil.copy2(shutil.which('uv'), tools / 'uv.exe')
    shutil.copy2('C:/Windows/System32/curl.exe', tools / 'curl.exe')
    userenv = ctypes.WinDLL('userenv', use_last_error=True)
    userenv.CreateAppContainerProfile.argtypes = [W.LPCWSTR, W.LPCWSTR, W.LPCWSTR, ctypes.c_void_p,
                                                W.DWORD, ctypes.POINTER(ctypes.c_void_p)]
    userenv.CreateAppContainerProfile.restype = ctypes.c_long
    userenv.DeleteAppContainerProfile.argtypes = [W.LPCWSTR]
    userenv.DeleteAppContainerProfile.restype = ctypes.c_long
    adv = ctypes.WinDLL('advapi32', use_last_error=True)
    adv.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(W.LPWSTR)]
    adv.FreeSid.argtypes = [ctypes.c_void_p]
    kernel = api()
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    sid, sid_text = ctypes.c_void_p(), W.LPWSTR()
    profile = 'MaleCNSA025.' + uuid.uuid4().hex
    assert userenv.CreateAppContainerProfile(profile, profile, 'A025 frozen Windows candidate', None, 0, ctypes.byref(sid)) == 0
    node_granted = loopback_granted = nsight_granted = False
    node = Path('C:/Program Files/nodejs/node.exe')
    node_hash = sha(node)
    job = None
    metadata_rights = None
    broker = None
    evidence = {'run': str(run), 'base': BASE, 'profile': profile,
                'certificate_sha256': sha(certificate), 'candidate': hashes, 'status': 'FAIL',
                'dependency_seeds': seeds, 'symlink_certificate_sha256': sha(symlink_certificate),
                'nsight_sha256': sha(nsight)}
    try:
        require(adv.ConvertSidToStringSidW(sid, ctypes.byref(sid_text)))
        evidence['sid'] = sid_text.value
        metadata_rights = MetadataRights(sid, [Path('C:/'), Path('C:/TEMP'), run, run / 'input'])
        evidence['metadata_rights'] = [{'object': name, 'mask': hex(mask)}
                                      for _, name, mask in metadata_rights.records]
        for path, permission in ((tools, '(OI)(CI)RX'), (tree, '(OI)(CI)RX'), (seed_root, '(OI)(CI)RX'),
                                 (tree / '.venv', '(OI)(CI)M'), (output, '(OI)(CI)M')):
            subprocess.run(['icacls', str(path), '/grant', '*' + sid_text.value + ':' + permission],
                           check=True, capture_output=True)
        for path in (tree / '.venv', output):
            subprocess.run(['icacls', str(path), '/setintegritylevel', '(OI)(CI)L'], check=True, capture_output=True)
        subprocess.run(['icacls', str(node), '/grant', '*' + sid_text.value + ':RX'], check=True, capture_output=True)
        node_granted = True
        subprocess.run(['icacls', str(nsight), '/grant', '*' + sid_text.value + ':RX'], check=True, capture_output=True)
        nsight_granted = True
        subprocess.run(['CheckNetIsolation.exe', 'LoopbackExempt', '-a', '-n=' + profile], check=True, capture_output=True)
        loopback_granted = True
        tool_hashes = {path.relative_to(tools).as_posix(): sha(path) for path in tools.rglob('*') if path.is_file()}
        assert all(certification['tool_input_hashes']['tools/' + path] == expected for path, expected in tool_hashes.items())
        evidence['tools'] = tool_hashes
        (run / 'controller.json').write_text(json.dumps(evidence, indent=2) + '\n')
        print('A025 Windows candidate: ' + str(run), flush=True)
        job = Job()
        broker = SyntheticSymlinkBroker(output / 'temp')
        evidence['process'] = launch(tools / 'python.exe', tree / 'scripts/a025_windows_worker.py',
                                     output, sid, job, internet=True, timeout_ms=14400000, extra_environment=broker.environment())
        assert evidence['process']['exit'] == 0 and evidence['process']['job']['active'] == 0
        assert {path: sha(ROOT / path) for path in hashes} == hashes
        assert {path: sha(tools / path) for path in tool_hashes} == tool_hashes
        for name, identity in seeds.items():
            with (seed_root / name).open('rb') as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == identity['sha256']
        assert sha(node) == node_hash
        assert len(broker.receipts) == 1
        evidence['symlink_receipts'] = broker.receipts
        evidence.update(status='WINDOWS GPU SUITE AND CPU ARTIFACT PASS', immutable=True)
    finally:
        if job is not None:
            job.close()
            evidence['job_cleanup'] = 'closed; kill-on-close retained'
        if broker is not None:
            broker.close()
            evidence['broker_cleanup'] = 'closed; thread and request handlers joined'
            evidence['symlink_receipts'] = broker.receipts
        if nsight_granted:
            subprocess.run(['icacls', str(nsight), '/remove:g', '*' + sid_text.value], check=True, capture_output=True)
            assert sha(nsight) == evidence['nsight_sha256']
            evidence['nsight_cleanup'] = 'temporary SID grant removed; tool bytes unchanged'
        if loopback_granted:
            subprocess.run(['CheckNetIsolation.exe', 'LoopbackExempt', '-d', '-n=' + profile], check=True, capture_output=True)
            evidence['loopback_cleanup'] = 'profile-only exemption removed'
        if node_granted:
            subprocess.run(['icacls', str(node), '/remove:g', '*' + sid_text.value], check=True, capture_output=True)
            assert sha(node) == node_hash
            evidence['node_cleanup'] = 'temporary SID grant removed; node bytes unchanged'
        if metadata_rights is not None:
            metadata_rights.close()
            evidence['metadata_cleanup'] = 'temporary profile SID entries removed'
        evidence['profile_cleanup_hresult'] = userenv.DeleteAppContainerProfile(profile)
        if evidence['profile_cleanup_hresult'] != 0:
            evidence['status'] = 'FAIL'
        if sid_text:
            kernel.LocalFree(sid_text)
        adv.FreeSid(sid)
        (run / 'controller.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'status': evidence['status'], 'run': str(run)}))
    if evidence['status'] != 'WINDOWS GPU SUITE AND CPU ARTIFACT PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
