"""Frozen-candidate release-safe validation with a separate final certification boundary."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c5ad89377575592665344f6420126b16c29b4339'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def readiness(record):
    """Incomplete taxonomy or identities can never authorize execution."""
    reasons = []
    required = {'base', 'candidate', 'H', 'I', 'N', 'collection', 'taxonomy', 'integrity', 'terminal'}
    if not isinstance(record, dict) or set(record) != required:
        return {'EXECUTION_AUTHORIZED': False, 'blockers': ['invalid readiness schema']}
    if record['base'] != BASE or not record['candidate']:
        reasons.append('candidate/base not frozen')
    groups = [record[key] for key in ('H', 'I', 'N')]
    if any(not isinstance(group, list) or len(group) != len(set(group)) for group in groups):
        reasons.append('invalid exact node identities')
    else:
        union = set().union(*map(set, groups))
        if sum(map(len, groups)) != len(union) or sorted(union) != record['collection']:
            reasons.append('H union I union N mismatch')
        entries = record['taxonomy']
        if not isinstance(entries, list) or len(entries) != len(record['H']):
            reasons.append('taxonomy incomplete')
        elif {entry.get('node_id') for entry in entries} != set(record['H']):
            reasons.append('taxonomy identity mismatch')
        elif any(entry.get('classification') not in ('Z0', 'Z1', 'Z3')
                 or entry.get('disposition') not in ('RUN', 'NOT RUN — REGISTERED-PAYLOAD-REQUIRED', 'Z3-RUN', 'Z3-NOT-RUN')
                 or not entry.get('reason_category') for entry in entries):
            reasons.append('unresolved or blocked taxonomy')
        elif any((entry['classification'] == 'Z0' and entry['disposition'] != 'RUN')
                 or (entry['classification'] == 'Z1' and entry['disposition'] != 'NOT RUN — REGISTERED-PAYLOAD-REQUIRED')
                 or (entry['classification'] == 'Z3' and entry['disposition'] not in ('Z3-RUN', 'Z3-NOT-RUN'))
                 for entry in entries):
            reasons.append('classification/disposition mismatch')
    if record['integrity'] != {'I0': 'FROZEN — UNPROTECTED CONTENT ONLY',
                               'I1': 'NOT RUN — REGISTERED-PAYLOAD-REQUIRED',
                               'I2': 'FROZEN — BOUNDED MANIFEST CONSISTENCY'}:
        reasons.append('integrity disposition unresolved')
    if record['terminal'] != {'A011': 'Z3-RUN', 'A007B': 'Z3-RUN', 'product_changes_allowed': False}:
        reasons.append('development completion not terminal')
    return {'EXECUTION_AUTHORIZED': not reasons, 'blockers': reasons}


class Collection:
    def __init__(self, frozen, output):
        self.frozen, self.output = frozen, output
        self.results, self.plugins = [], []
        self.collected = []

    def pytest_sessionstart(self, session):
        for name, plugin in session.config.pluginmanager.list_name_plugin():
            if plugin is None:
                continue
            if isinstance(plugin, ModuleType):
                module = plugin.__name__
            elif isinstance(plugin, type):
                module = plugin.__module__
            else:
                module = type(plugin).__module__
            if not (module.startswith('_pytest.') or module in ('_pytest', 'builtins', '__main__', 'a023_release_validation')):
                raise RuntimeError('uncontrolled pytest plugin: ' + module)
            self.plugins.append({'name': name, 'module': module})

    def pytest_collection_modifyitems(self, session, config, items):
        self.collected = sorted(item.nodeid for item in items)
        if self.collected != self.frozen['collection']:
            raise RuntimeError('exact final collection mismatch')
        excluded = {entry['node_id'] for entry in self.frozen['taxonomy']
                    if entry['disposition'] in ('NOT RUN — REGISTERED-PAYLOAD-REQUIRED', 'Z3-NOT-RUN')}
        removed = [item for item in items if item.nodeid in excluded]
        items[:] = [item for item in items if item.nodeid not in excluded]
        config.hook.pytest_deselected(items=removed)

    def pytest_runtest_logreport(self, report):
        if report.when == 'call' or report.failed or report.skipped:
            self.results.append({'node_id': report.nodeid, 'phase': report.when,
                                 'outcome': report.outcome,
                                 'reason': str(report.longrepr) if report.failed or report.skipped else None})


def final(run):
    """One suite invocation; no retry or source edits in this process."""
    import validation_firewall as guard
    if not guard.ACTIVE:
        raise RuntimeError('firewall must be active before pytest import')
    sys.path.insert(0, str(ROOT / 'scripts'))
    from a023_local_repro import canonical_path
    original_check = guard.check
    counters = {'accepted_protected_checks': 0, 'denied_protected_checks': 0}
    def checked(value):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return original_check(value)
        path = canonical_path(value)
        protected = (any(path.is_relative_to(root.resolve()) for root in guard.DENIED_ROOTS)
                     or 'male-cns-v1' in str(path).lower()
                     or 'male-cns/v1.0' in path.as_posix().lower())
        try:
            result = original_check(path)
        except guard.SourceAccessDenied:
            if protected:
                counters['denied_protected_checks'] += 1
            raise
        if protected:
            counters['accepted_protected_checks'] += 1
            raise RuntimeError('registered protection unexpectedly admitted')
        return result
    guard.check = checked
    record = json.loads((ROOT / 'docs/manifests/a023r11-frozen-candidate.json').read_text())
    decision = readiness(record)
    if not decision['EXECUTION_AUTHORIZED']:
        raise RuntimeError(str(decision))
    before = {path: sha((ROOT / path).read_bytes()) for path in record['candidate']}
    if before != record['candidate']:
        raise RuntimeError('frozen candidate byte identity mismatch')
    manifest_identity = sha((ROOT / 'docs/manifests/a023r11-frozen-candidate.json').read_bytes())
    if (run / 'evidence/firewall.jsonl').exists():
        events = [json.loads(line) for line in (run / 'evidence/firewall.jsonl').read_text().splitlines()]
        if not events or events[0]['kind'] != 'active':
            raise RuntimeError('fresh firewall log missing activation')

    def writes(event, args):
        values = []
        if event == 'open':
            mode, flags = args[1], args[2]
            if (isinstance(mode, str) and any(letter in mode for letter in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
                values = [args[0]]
        elif event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.utime', 'os.truncate'):
            values = [args[0]]
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            values = list(args[:2])
        for value in values:
            if isinstance(value, (str, bytes, os.PathLike)):
                path = canonical_path(value)
                if path.is_relative_to(ROOT) or not path.is_relative_to(run):
                    raise PermissionError('write outside dedicated certification outputs: ' + str(path))

    sys.addaudithook(writes)
    import pytest
    import tomllib
    from a023_validation_environment import inspect_environment
    prerequisites = inspect_environment(ROOT, tomllib.loads((ROOT / 'uv.lock').read_text()))
    installed = prerequisites['dependencies']
    observer = Collection(record, run)
    result = pytest.main(['tests', '-q', '-s', '--tb=short', '-c', str(ROOT / 'pyproject.toml'),
                          '-o', 'cache_dir=' + str(run / 'pytest-cache'),
                          '-o', 'log_file=' + str(run / 'evidence/pytest.log'),
                          '--basetemp=' + str(run / 'temp/pytest')], plugins=[observer])
    after = {path: sha((ROOT / path).read_bytes()) for path in before}
    immutable = before == after and manifest_identity == sha((ROOT / 'docs/manifests/a023r11-frozen-candidate.json').read_bytes())
    events = [json.loads(line) for line in (run / 'evidence/firewall.jsonl').read_text().splitlines()]
    # The unchanged guard denies registered opens before content and wraps Arrow native readers.
    # Counter scope is this fresh process tree only; development history is excluded.
    protected_accepted = counters['accepted_protected_checks']
    selected = {entry['node_id'] for entry in record['taxonomy'] if entry['disposition'] in ('RUN', 'Z3-RUN')}
    selected.update(record['I'] + record['N'])
    completed = {entry['node_id'] for entry in observer.results if entry['phase'] == 'call' or entry['outcome'] == 'skipped'}
    passed = result == 0 and immutable and completed == selected and protected_accepted == 0
    evidence = {'schema': 'a023r11-final-validation-v1', 'phase': 'C', 'base': BASE,
                'tree': str(ROOT), 'run': str(run), 'pid': os.getpid(),
                'python': sys.version, 'executable': sys.executable,
                'dependencies': installed, 'pytest_version': pytest.__version__,
                'prerequisites': prerequisites,
                'manifest_sha256': manifest_identity, 'candidate': before,
                'environment': dict(os.environ), 'plugins': observer.plugins,
                'collection': observer.collected, 'results': observer.results,
                'I0': 'PASS — UNPROTECTED CONTENT ONLY' if immutable else 'FAIL',
                'I1': record['integrity']['I1'],
                'I2': 'PASS — BOUNDED MANIFEST CONSISTENCY' if observer.collected == record['collection'] else 'FAIL',
                'protected_payload_accepted_opens': protected_accepted,
                'parent_protection_counters': counters,
                'counter_scope': 'Fresh final parent check/audit and wrapped Arrow readers; unchanged fail-closed child firewalls and exact Node read grants; protected inputs absent',
                'protected_denials': sum(event['kind'] == 'blocked' for event in events),
                'immutable': immutable, 'pytest_exit': result,
                'result': 'ZERO-PAYLOAD RELEASE-SAFE VALIDATION PASS' if passed else 'FINAL CERTIFICATION FAIL'}
    (run / 'evidence/final-validation.json').write_text(json.dumps(evidence, indent=2))
    print(evidence['result'], flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(final(Path(sys.argv[1]).resolve(strict=True)))
