"""Narrow resumable fetch helper for the three in-scope MaleCNS v1.0 files."""

from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path

from malecns_sim.data.provenance import (
    DatasetProvenance,
    file_provenance,
    write_manifest,
)

OFFICIAL_DATASET_PAGE = "https://male-cns.janelia.org/download/"
MALE_CNS_V1_BASE_URL = (
    "https://storage.googleapis.com/flyem-male-cns/v1.0/"
    "connectome-data/flat-connectome/"
)
IN_SCOPE_FILES = (
    "body-annotations-male-cns-v1.0-minconf-0.5.feather",
    "body-neurotransmitters-male-cns-v1.0.feather",
    "connectome-weights-male-cns-v1.0-minconf-0.5.feather",
)


def fetch_v1_files(output_dir: str | Path) -> DatasetProvenance:
    """Download missing files, resuming a partial ``.part`` file when possible."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    measured = []
    for filename in IN_SCOPE_FILES:
        destination = output_dir / filename
        if not destination.is_file():
            partial = destination.with_name(destination.name + ".part")
            offset = partial.stat().st_size if partial.exists() else 0
            request = urllib.request.Request(
                MALE_CNS_V1_BASE_URL + filename,
                headers={"Range": f"bytes={offset}-"} if offset else {},
            )
            with urllib.request.urlopen(request) as response:
                resumed = offset and response.status == 206
                mode = "ab" if resumed else "wb"
                if not resumed:
                    offset = 0
                with partial.open(mode) as handle:
                    shutil.copyfileobj(response, handle)
            partial.replace(destination)
        measured.append(
            file_provenance(
                destination,
                source_url=MALE_CNS_V1_BASE_URL + filename,
            )
        )
    return DatasetProvenance(
        dataset_name="MaleCNS",
        release="v1.0",
        source_organization="HHMI Janelia / FlyEM",
        official_dataset_page=OFFICIAL_DATASET_PAGE,
        adapter_schema_version="malecns-v1-feather-explicit-mapping-v1",
        files=tuple(measured),
    )


def fetch_and_write_manifest(output_dir: str | Path, manifest_path: str | Path) -> DatasetProvenance:
    provenance = fetch_v1_files(output_dir)
    write_manifest(manifest_path, provenance)
    return provenance
