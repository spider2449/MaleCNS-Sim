"""Create a fresh frozen-candidate environment; metadata-only Git operations."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from a023_release_validation import BASE, readiness, sha
from a023_local_repro import Job, admitted_environment
from a023_validation_environment import provision as provision_environment


def main():
    record = json.loads((ROOT / 'docs/manifests/a023r11-frozen-candidate.json').read_text())
    if not readiness(record)['EXECUTION_AUTHORIZED']:
        raise RuntimeError('development completion gate denied')
    for path, expected in record['candidate'].items():
        if sha((ROOT / path).read_bytes()) != expected:
            raise RuntimeError('candidate drift: ' + path)
    run = Path('C:/TEMP') / ('malecns-a023r11-final-' + uuid.uuid4().hex)
    run.mkdir()
    for name in ('temp', 'evidence', 'home', 'pytest-cache', 'uv-cache', 'cupy-cache', 'cuda-cache', 'npm-cache'):
        (run / name).mkdir()
    tree = run / 'execution'
    subprocess.run(['git', 'worktree', 'add', '--detach', '--no-checkout', str(tree), BASE], cwd=ROOT, check=True)
    subprocess.run(['git', 'sparse-checkout', 'set', '--no-cone', '--stdin'], input='/*\n!/data/\n!/artifacts/\n', cwd=tree, text=True, check=True)
    subprocess.run(['git', 'checkout', '--detach', BASE], cwd=tree, check=True)
    if (tree / 'data').exists():
        raise RuntimeError('protected root materialized')
    for path, expected in record['candidate'].items():
        destination = tree / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = (ROOT / path).read_bytes()
        if sha(content) != expected:
            raise RuntimeError('candidate changed during transfer')
        destination.write_bytes(content)
        if sha(destination.read_bytes()) != expected:
            raise RuntimeError('candidate transfer mismatch')
    relative = 'docs/manifests/a023r11-frozen-candidate.json'
    (tree / relative).write_bytes((ROOT / relative).read_bytes())
    environment = admitted_environment(run, tree)
    environment['PATH'] += os.pathsep + 'C:/Program Files/nodejs'
    # Provisioning builds only an independent copy with no protected roots.
    provision = {key: value for key, value in environment.items()
                 if not key.startswith('PYTHON') and not key.startswith('MALECNS') and not key.startswith('UV_INTERNAL')}
    uv = shutil.which('uv')
    provisioning = provision_environment(tree, run, uv, sys.executable, provision, record['candidate'])
    python = tree / '.venv/Scripts/python.exe'
    details = {'base': BASE, 'run': str(run), 'tree': str(tree),
               'candidate_manifest_sha256': sha((tree / relative).read_bytes()),
               'environment': environment, 'development_results_reused': False,
               'protected_root_materialized': False, 'suite_invocations': 1}
    details['provisioning'] = provisioning
    details['tools'] = {path: sha(Path(path).read_bytes()) for path in
                        (sys.executable, uv, 'C:/Program Files/nodejs/node.exe')}
    (run / 'evidence/environment.json').write_text(json.dumps(details, indent=2))
    print('PHASE C START: ' + str(run), flush=True)
    job = Job()
    with (run / 'evidence/suite-output.txt').open('w', encoding='utf-8') as output:
        process = subprocess.Popen([str(python), '-B', str(tree / 'scripts/a023_release_validation.py'), str(run)],
                                   cwd=tree, env=environment, stdout=output, stderr=subprocess.STDOUT,
                                   creationflags=4, close_fds=True)
        try:
            job.assign_resume(process)
            result = process.wait(timeout=1800)
            accounting = job.accounting()
            if accounting['active']:
                job.terminate()
                raise RuntimeError('stale descendants after final suite')
            details.update(job=accounting, pytest_process_exit=result, stale_workers=0)
            (run / 'evidence/environment.json').write_text(json.dumps(details, indent=2))
        finally:
            job.close()
    print(json.dumps({'run': str(run), 'exit': result, 'job': accounting}), flush=True)
    return result


if __name__ == '__main__':
    raise SystemExit(main())
