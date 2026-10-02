"""Small documentation checks tied to authoritative application contracts."""

from importlib.resources import files
from pathlib import Path
import re

from malecns_sim.application import comparisons, models, playback, preparation, robustness


def test_reproducibility_contracts_and_packaged_assets():
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/application/REPRODUCIBILITY.md").read_text(encoding="utf-8")
    for value in (models.EXPERIMENT_SCHEMA, models.RESULT_SCHEMA, playback.SCHEMA,
                  comparisons.SCHEMA, preparation.SCHEMA, robustness.SCHEMA,
                  preparation.PRESET_ID, preparation.PRESET_DIGEST):
        assert value in document
    static = files("malecns_sim.application").joinpath("static")
    for name in ("index.html", "style.css", "app.js", "run-status.js",
                 "playback.js", "compare.js", "robustness.js"):
        assert static.joinpath(name).is_file()


def test_application_docs_are_portable_and_do_not_embed_session_urls():
    root = Path(__file__).resolve().parents[1]
    for name in ("USER_GUIDE.md", "REPRODUCIBILITY.md"):
        content = (root / "docs/application" / name).read_text(encoding="utf-8")
        assert not re.search(r"[A-Za-z]:[\\/]", content)
        assert not re.search(r"#token=[A-Za-z0-9_-]{20,}", content)
