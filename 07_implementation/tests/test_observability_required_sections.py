from __future__ import annotations

import pytest

from observability.main import ensure_required_sections


def _minimal_run_log() -> dict[str, object]:
    return {
        "run_metadata": {},
        "execution_scope_summary": {},
        "run_config": {},
        "ingestion_alignment_diagnostics": {},
        "stage_diagnostics": {},
        "exclusion_diagnostics": {},
        "validity_boundaries": {},
        "output_artifacts": {},
    }


def test_ensure_required_sections_accepts_validity_boundaries_top_level() -> None:
    run_log = _minimal_run_log()

    ensure_required_sections(run_log)


def test_ensure_required_sections_raises_when_validity_boundaries_missing() -> None:
    run_log = _minimal_run_log()
    run_log.pop("validity_boundaries")

    with pytest.raises(RuntimeError, match="validity_boundaries"):
        ensure_required_sections(run_log)
