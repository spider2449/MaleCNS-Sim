"""Bounded first-slice options backed by a registered local dataset."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid5

from malecns_sim.data.neurotransmitter import NeurotransmitterResolutionPolicy
from malecns_sim.dynamics.lif import LIFParameters
from malecns_sim.homology import population_fingerprint
from malecns_sim.sign import Shiu2024SignPolicy

from .errors import ApplicationError, ErrorCode
from .models import (
    ALLOWED_FREQUENCIES_HZ, DatasetIdentity, ExperimentSpec, InterventionSpec,
    ModelSpec, ObservablesSpec, RobustnessRequest, SeedPolicy, SignPolicySpec,
    StimulusSpec, TargetSpec,
)
from .models import canonical_bytes
from .service import DatasetFiles, ProductionEngine, validate_experiment

DATASET_KEY = "male-cns-v1"
MANIFEST_DIGEST = "e3c26d37039625e8a0623a7b6f83cb70d01663c99f8e32d4ffb2d79709b80631"
MAPPING_FINGERPRINT = "832d8428c458e59cfff7b52fc257a4ba3fd85fdd6f3ebf47f01e02e218f50269"
PROJECTION_FINGERPRINT = "fde3d0f58b65235da3dfefb552cfe8a3bac8429312c30287e598e289115a93d4"
SOURCE_FILES = (
    ("body-annotations-male-cns-v1.0-minconf-0.5.feather", "2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2"),
    ("body-neurotransmitters-male-cns-v1.0.feather", "95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621"),
    ("connectome-weights-male-cns-v1.0-minconf-0.5.feather", "e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1"),
)


@dataclass(slots=True)
class DatasetCatalog:
    root: Path
    engine: ProductionEngine
    _identities: object | None = None

    @classmethod
    def local(cls, engine: ProductionEngine | None = None) -> "DatasetCatalog":
        root = Path(os.environ.get("MALECNS_DATA_ROOT", Path.cwd() / "data"))
        return cls(root, engine or ProductionEngine())

    @property
    def files(self) -> DatasetFiles:
        base = self.root / "raw" / "male-cns" / "v1.0"
        return DatasetFiles(*(base / name for name, _ in SOURCE_FILES), MANIFEST_DIGEST, MAPPING_FINGERPRINT)

    @property
    def identity(self) -> DatasetIdentity:
        return DatasetIdentity("MaleCNS-v1.0", MANIFEST_DIGEST, *(sha for _, sha in SOURCE_FILES), PROJECTION_FINGERPRINT, MAPPING_FINGERPRINT)

    def available(self) -> bool:
        return all(path.is_file() for path in (self.files.annotation, self.files.neurotransmitter, self.files.weights))

    def metadata(self) -> dict:
        return {"key": DATASET_KEY, "display_name": "MaleCNS v1.0 curated graph", "available": self.available(),
                "status": "AVAILABLE" if self.available() else "DATASET_UNAVAILABLE",
                "manifest_digest": MANIFEST_DIGEST, "mapping_fingerprint": MAPPING_FINGERPRINT,
                "projection_fingerprint": PROJECTION_FINGERPRINT}

    def populations(self):
        if not self.available():
            raise ApplicationError(ErrorCode.DATASET_PROVENANCE, "DATASET_UNAVAILABLE")
        if self._identities is None:
            self._identities = self.engine.identities(self.files)
        return self._identities

    def options(self) -> dict:
        identities = self.populations()
        return {"dataset_key": DATASET_KEY, "frequencies_hz": ALLOWED_FREQUENCIES_HZ,
                "sides": {"L": {"stimulus_count": len(identities.sugar_left.candidate_body_ids), "target": "MN9_R", "target_id": 16949},
                          "R": {"stimulus_count": len(identities.sugar_right.candidate_body_ids), "target": "MN9_L", "target_id": 10331}},
                "interventions": ["none", "outgoing_silence"], "silence_targets": {"L": [16949], "R": [10331]},
                "duration_ms": 100.0, "dt_ms": 0.1, "default_seed": 1555062870,
                "cuda_available": self.engine.cuda_available()}

    def spec(self, selection: dict) -> ExperimentSpec:
        if not isinstance(selection, dict) or set(selection) != {"dataset_key", "side", "frequency_hz", "mode", "backend", "seed"}:
            raise ApplicationError(ErrorCode.INVALID_SPEC, "selection requires exact fields")
        if selection["dataset_key"] != DATASET_KEY or selection["side"] not in ("L", "R"):
            raise ApplicationError(ErrorCode.INVALID_SPEC, "unsupported dataset or side")
        side = selection["side"]
        if selection["mode"] not in ("none", "outgoing_silence"):
            raise ApplicationError(ErrorCode.UNSUPPORTED_OPERATION, "unsupported intervention")
        identities = self.populations()
        population = identities.sugar_left if side == "L" else identities.sugar_right
        target = 16949 if side == "L" else 10331
        parameters = LIFParameters()
        spec = ExperimentSpec(
            "application-experiment-v1", str(uuid5(UUID("1fd947d8-3edc-4507-951d-c111f25e9a9b"), canonical_bytes(selection).decode("utf-8"))), self.identity, selection["backend"],
            SeedPolicy("explicit", (selection["seed"],)), 100.0, 0.1, 1,
            StimulusSpec(population_fingerprint(population), tuple(sorted(int(i) for i in population.candidate_body_ids)), side,
                         selection["frequency_hz"], 0.0, 100.0, 250.0, "reference-poisson-direct-voltage-v1"),
            TargetSpec(target, "contralateral"),
            InterventionSpec(selection["mode"], (target,) if selection["mode"] == "outgoing_silence" else ()),
            ModelSpec(parameters, parameters.fingerprint),
            SignPolicySpec(Shiu2024SignPolicy().policy_id, NeurotransmitterResolutionPolicy().policy_id),
            ObservablesSpec(True, (), False, None), RobustnessRequest("none", (), None),
        )
        return validate_experiment(spec)
