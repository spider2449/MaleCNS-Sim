"""Small, schema-explicit tabular file boundary.

The exact public MaleCNS v1.0 file schema is intentionally not guessed here.
Callers must provide column mappings when their external tables do not use the
canonical names. Raw files are read locally; this module never downloads data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from malecns_sim.data.model import NormalizedConnectome
from malecns_sim.data.normalize import (
    EdgeColumns,
    NeuronColumns,
    normalize_connectome,
)


def _read_table(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if path.suffix.lower() not in {".csv", ".tsv", ".tab"}:
        raise ValueError(
            f"unsupported table format {path.suffix!r}; use CSV/TSV or provide rows directly"
        )
    separator = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    return pd.read_csv(
        path, sep=separator, dtype=object, keep_default_na=False
    ).to_dict(orient="records")


def load_connectome(
    neuron_path: str | Path,
    edge_path: str | Path,
    *,
    neuron_columns: NeuronColumns | None = None,
    edge_columns: EdgeColumns | None = None,
) -> NormalizedConnectome:
    """Load local CSV/TSV tables through the explicit normalization boundary."""

    return normalize_connectome(
        _read_table(neuron_path),
        _read_table(edge_path),
        neuron_columns=neuron_columns,
        edge_columns=edge_columns,
        provenance={
            "neuron_source": str(Path(neuron_path)),
            "edge_source": str(Path(edge_path)),
            "adapter": "explicit-csv-tsv-columns",
        },
    )
