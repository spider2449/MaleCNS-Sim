"""Freeze development identities without opening protected payload roots."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from a023_release_validation import BASE, readiness, sha
from a023r11_development import EXCLUDED


def reviewed_new_nodes(manifests):
    """Retain the original N identities and admit only the reviewed additions."""
    historical = (manifests / 'a023r11-before-code-review-frozen-candidate.json').read_bytes()
    if sha(historical) != '4b04b8ec50f8fdab7a99e2d33922d1ef8fdc639ab9de74c278b5b1525a4fb8d2':
        raise RuntimeError('historical frozen manifest identity mismatch')
    original = json.loads(historical)['N']
    prefix = 'tests/test_code_review_fixes.py::'
    additions = {prefix + 'test_actual_builtin_plugin_census'}
    additions.update(prefix + 'test_completion_cannot_clear_a_new_run[' + outcome + ']'
                     for outcome in ('success', 'application_error', 'unexpected_error'))
    additions.update(prefix + 'test_plugin_census_uses_defining_module[' + trusted + '-' + representation + ']'
                     for trusted in ('True', 'False')
                     for representation in ('module', 'class', 'instance'))
    if len(original) != 20 or len(set(original)) != 20 or len(additions) != 10:
        raise RuntimeError('reviewed N identity count mismatch')
    environment_prefix = 'tests/test_code_review_environment.py::'
    environment_nodes = {environment_prefix + name for name in (
        'test_gpu_closure_is_complete_and_does_not_mutate_lock',
        'test_late_extra_expansion_and_cycles',
        'test_frozen_packaging_inputs_are_required',
        'test_genuine_project_metadata_and_gpu_prerequisites',
    )}
    environment_nodes.update(environment_prefix + 'test_dependency_census_rejects_incomplete_or_changed_environment[' + change + ']'
                             for change in ('project', 'gpu', 'extra', 'duplicate', 'version'))
    environment_nodes.update(environment_prefix + 'test_provisioning_rejects_materialized_protected_root[' + root + ']'
                             for root in ('data', 'artifacts'))
    if len(environment_nodes) != 11:
        raise RuntimeError('environment N identity count mismatch')
    return set(original) | additions | environment_nodes


def main():
    manifests = ROOT / 'docs/manifests'
    h = (manifests / 'a023-validation-baseline-h.txt').read_text().splitlines()
    i = (manifests / 'a023-validation-infrastructure-i.txt').read_text().splitlines()
    collection_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('C:/TEMP/a023r11-development-collection.json')
    collected = json.loads(collection_path.read_text())
    n = sorted(set(collected) - set(h) - set(i))
    if len(h) != 1503 or len(i) != 12 or set(n) != reviewed_new_nodes(manifests) or set(collected) != set(h + i + n):
        raise RuntimeError('final collection or N identity mismatch')
    original = json.loads((manifests / 'a023-zero-payload-taxonomy.json').read_text())
    if {entry['node_id'] for entry in original['entries']} != set(h):
        raise RuntimeError('frozen H taxonomy drift')
    special = {
        'tests/test_application_a011.py::test_http_ui_assets_and_commands': 'C2 resolved: exact permission Node route retains historical JS/HTTP assertions',
        'tests/test_application_a007b.py::test_full_sweep_and_retention_stress': 'T0 correctness/ownership/retention assertions; incidental timing is not performance evidence',
        'tests/test_workbench_session.py::test_browser_session_recovery': 'Exact Node permission composition preserves literal historical inline assertions',
        'tests/test_application_a018r.py::test_supervisor_time_failure_cleans_without_retry': 'Synthetic timeout fixture admits guarded readiness and requires prepare_start; timeout/zero-attempt/cleanup assertions retained',
    }
    for node in h:
        if node.startswith('tests/test_task017.py::test_task017_resume_gate_rejects_modified_certified_infrastructure_blob['):
            special[node] = 'Synthetic Git identity mock installed before assertion; every rejection assertion retained'
        if node.startswith('tests/test_application_a019x.py::test_exact_launch_contract[') or node in (
                'tests/test_application_a019x.py::test_missing_activation_allowed_only_for_harmless_control',
                'tests/test_application_a019x_cleanup.py::test_assignment_failure_terminates_unassigned_suspended_root'):
            special[node] = 'Exact native child environment constructed from fixed firewall path; contract/rejection assertions retained; suspended cleanup control performs no profiler workload'
    optional = 'tests/test_application_a019h.py::test_starting_commit_exact_replay'
    entries = []
    for node in h:
        if node in EXCLUDED:
            classification, disposition, reason = 'Z1', 'NOT RUN — REGISTERED-PAYLOAD-REQUIRED', EXCLUDED[node]
        elif node == optional:
            classification, disposition, reason = 'Z3', 'Z3-NOT-RUN', 'Optional external starting-SHA module absent; no external source admitted; independent historical replay remains covered by pinned A018UI fixtures and A023 continuity'
        elif node in special:
            classification, disposition, reason = 'Z3', 'Z3-RUN', special[node]
        else:
            classification, disposition = 'Z0', 'RUN'
            reason = ('Reviewed ordinary test source and loader/fixture/child dependencies: in-memory or generated temporary inputs, ordinary source/docs, fixed code fixtures or fail-closed denial controls. '
                      'Optional GPU capability skips retain their assertions; timing/accounting tests make no performance claim.')
        entries.append({'node_id': node, 'classification': classification, 'disposition': disposition,
                        'reason_category': reason, 'A023_relevance': 'Public facade/unchanged-engine regression' if 'a023.py' in node else 'Historical release-safe regression; protected exclusions do not import the public facade'})
    counts = {key: sum(entry['classification'] == key for entry in entries) for key in ('Z0', 'Z1', 'Z2', 'Z3')}
    taxonomy = {'status': 'COMPLETE — FROZEN FOR PHASE C', **counts,
                'Z3-BLOCKED': 0, 'entries': entries}
    (manifests / 'a023-zero-payload-taxonomy.json').write_text(json.dumps(taxonomy, indent=2) + '\n', encoding='utf-8')
    (manifests / 'a023-validation-new-n.txt').write_text('\n'.join(n) + '\n', encoding='utf-8')
    (manifests / 'a023-validation-final-collection.txt').write_text('\n'.join(collected) + '\n', encoding='utf-8')
    if len(sys.argv) > 2:
        inventory = Path(sys.argv[2]).read_text(encoding='utf-8-sig').splitlines()
    else:
        inventory = subprocess.check_output(['git', 'ls-files', '-c', '-o', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    paths = sorted({path for path in inventory if path.startswith(('src/', 'tests/', 'scripts/', 'docs/', 'plans/', 'manifests/'))
                    or path in ('pyproject.toml', 'uv.lock', 'MANIFEST.in', 'README.md', 'LICENSE', '.gitignore', '.gitattributes')})
    paths = [path for path in paths if path != 'docs/manifests/a023r11-frozen-candidate.json']
    record = {'base': BASE, 'candidate': {path: sha((ROOT / path).read_bytes()) for path in paths},
              'H': h, 'I': i, 'N': n, 'collection': collected, 'taxonomy': entries,
              'integrity': {'I0': 'FROZEN — UNPROTECTED CONTENT ONLY', 'I1': 'NOT RUN — REGISTERED-PAYLOAD-REQUIRED',
                            'I2': 'FROZEN — BOUNDED MANIFEST CONSISTENCY'},
              'terminal': {'A011': 'Z3-RUN', 'A007B': 'Z3-RUN', 'product_changes_allowed': False}}
    if not readiness(record)['EXECUTION_AUTHORIZED']:
        raise RuntimeError(str(readiness(record)))
    destination = manifests / 'a023r11-frozen-candidate.json'
    destination.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'counts': counts, 'N': len(n), 'collection': len(collected),
                      'candidate_files': len(paths), 'candidate_manifest_sha256': sha(destination.read_bytes()),
                      'readiness': readiness(record)}))


if __name__ == '__main__':
    main()
