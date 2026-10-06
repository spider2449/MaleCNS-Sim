"""Ordered bootstrap controls; no harness or registered payload is read."""
import os
import subprocess
import sys

import pyarrow as pa
import pyarrow.feather as feather
import pyarrow._feather as native
import pytest
import validation_firewall as guard


def test_01_valid_native_synthetic_control(tmp_path):
    assert guard.ACTIVE
    source = tmp_path / "synthetic.feather"
    feather.write_feather(pa.table({"sentinel": [19]}), source)
    assert native.FeatherReader(str(source), use_memory_map=False,
                                use_threads=True).read().to_pydict() == {"sentinel": [19]}


def test_02_native_registered_source_denied_before_constructor():
    assert guard.ACTIVE
    source = guard.ROOT / "data/raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather"
    with pytest.raises(guard.SourceAccessDenied):
        native.FeatherReader(str(source), use_memory_map=False, use_threads=True).read()


def test_03_python_child_native_guard():
    code = """import validation_firewall as g
import pyarrow._feather as n
assert g.ACTIVE
try:
    n.FeatherReader(str(g.ROOT/'data/raw/male-cns/v1.0/connectome-weights-male-cns-v1.0-minconf-0.5.feather'), False, True)
except g.SourceAccessDenied:
    print('ACTIVE; BLOCKED BEFORE NATIVE CONSTRUCTOR')
else:
    raise AssertionError('native boundary did not reject')
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "ACTIVE; BLOCKED BEFORE NATIVE CONSTRUCTOR" in result.stdout


def test_04_missing_inherited_guard_fails_closed(monkeypatch):
    """Use a harmless child; never test missing activation against real data."""
    monkeypatch.delenv("MALECNS_A019C_R2_FIREWALL")
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.run([sys.executable, "-c", "print('UNGUARDED CHILD EXECUTED')"],
                       capture_output=True, text=True)
