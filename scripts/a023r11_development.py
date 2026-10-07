"""Development-only collection and release-safe candidate checks; never G16 evidence."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {
    'tests/test_task006.py::test_reference_provenance_manifest_is_pinned': 'Registered Shiu provenance required',
    'tests/test_task007.py::test_exact_id_reference_is_preserved_as_canonical_strings': 'Default loader opens registered FlyWire mapping evidence',
    'tests/test_application_a003.py::test_selection_uses_stable_a002_digest_and_rejects_extra_fields': 'Registered catalog identities require protected content',
    'tests/test_application_a003.py::test_validate_and_run_requests_share_exact_spec_identity': 'Registered catalog identities require protected content',
    'tests/test_application_a003.py::test_result_events_and_backend_export_routes': 'Registered catalog identities require protected content',
    'tests/test_tracked_integrity.py::test_tracked_integrity_accepts_copy_and_rejects_corrupt_metadata': 'Copies and hashes protected registered evidence',
    'tests/test_application_a018uj.py::test_independent_frozen_artifact_reconstruction_and_provenance': 'Historical protected Git blob read',
    'tests/test_application_a018uj.py::test_no_real_execution_and_scientific_default_unchanged': 'Historical Git diff includes protected data; synthetic defaults remain covered by A018UI and A023',
    'tests/test_task007b.py::test_production_task007_readout_uses_only_the_resolved_mn9_body': 'Registered Feather inputs required',
    'tests/test_task007c.py::test_cuda_bounded_real_graph_equivalence': 'Registered full graph required',
    'tests/test_task008a.py::test_task008_result_preservation_manifest_is_explicit': 'Registered protected provenance required',
}


class Development:
    def pytest_collection_modifyitems(self, session, config, items):
        self.nodes = sorted(item.nodeid for item in items)
        removed = [item for item in items if item.nodeid in EXCLUDED]
        items[:] = [item for item in items if item.nodeid not in EXCLUDED]
        config.hook.pytest_deselected(items=removed)


if __name__ == '__main__':
    import validation_firewall as guard
    assert guard.ACTIVE
    import pytest
    observer = Development()
    print('DEVELOPMENT TEST — NOT FINAL CERTIFICATION', flush=True)
    result = pytest.main(['tests', '-q', *sys.argv[1:]], plugins=[observer])
    destination = Path('C:/TEMP/a023r11-development-collection.json')
    destination.write_text(json.dumps(observer.nodes, indent=2))
    raise SystemExit(result)
