"""Synthetic exact arithmetic, scratch ownership and index edge cases."""
import sys
from pathlib import Path
from dataclasses import replace

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import diagnose_application_a019i as diagnostic


def test_matrix_replay_and_structural_counts():
    evidence = diagnostic.run()
    assert [row["events"] for row in evidence["cases"]] == [60, 60, 60]
    for row in evidence["cases"]:
        assert row["workspace_bytes"] == 16 * row["n"]
    assert not any(evidence["accepted_registered_reads"].values())


@pytest.mark.parametrize("equal_tau", [False, True])
def test_special_values_and_refractory_boundaries(equal_tau):
    p = diagnostic.lif.REFERENCE_LIF_PARAMETERS
    if equal_tau:
        p = replace(p, tau_synapse_ms=p.tau_membrane_ms)
    v = np.array([-0., 0., -52., -80., np.inf, -np.inf, np.nan, 1e-300])
    g = np.array([0., -0., 2., -2., 0., 1., 3., 1e-300])
    refractory = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    free = np.array([False, True, False, False, False, False, True, False])
    workspace = diagnostic.Workspace(v.size)
    with np.errstate(invalid="ignore"):
        for step in (0, 1, 2, 3, 4):
            mask = (step > refractory) | free
            x, y = v[mask], g[mask]
            expected = diagnostic.lif.linear_state_update(x, y, parameters=p)
            actual = workspace.update(x, y, parameters=p)
            for a, b in zip(expected, actual):
                diagnostic.graph.base.exact(a, b)
    with pytest.raises(AssertionError):
        workspace.update(workspace.v, workspace.g)


def test_integer_duplicates_and_boolean_assignment():
    values = np.array([10., 20., 30.])
    target = np.zeros(4)
    indices = np.array([1, 1, 2])
    target[indices] = values
    assert target.tolist() == [0., 20., 30., 0.]
    added = np.zeros(4)
    np.add.at(added, indices, values)
    assert added[1] == 30. and not np.array_equal(target, added)
    mask = np.array([False, True, True, False])
    target[mask] = np.array([7., 8.])
    assert target.tolist() == [0., 7., 8., 0.]
