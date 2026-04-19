from __future__ import annotations

from pathlib import Path

from reproducibility.input_validation import validate_bl009_outputs


def _touch(path: Path, content: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_validate_bl009_outputs_accepts_current_canonical_artifacts(tmp_path: Path) -> None:
    src_root = tmp_path / "src"
    observability_outputs = src_root / "observability" / "outputs"
    _touch(
        observability_outputs / "bl009_run_observability_log.json",
        content=(
            '{'
            '"run_metadata": {},'
            '"execution_scope_summary": {},'
            '"run_config": {},'
            '"ingestion_alignment_diagnostics": {},'
            '"stage_diagnostics": {},'
            '"exclusion_diagnostics": {},'
            '"validity_boundaries": {},'
            '"output_artifacts": {}'
            '}'
        ),
    )
    _touch(observability_outputs / "bl009_run_index.csv", content="run_id\nBL009\n")
    _touch(src_root / "transparency" / "outputs" / "bl008_explanation_payloads.json")
    _touch(src_root / "playlist" / "outputs" / "bl007_assembly_report.json")
    _touch(src_root / "scoring" / "outputs" / "bl006_score_summary.json")
    _touch(src_root / "retrieval" / "outputs" / "bl005_candidate_diagnostics.json")
    _touch(src_root / "profile" / "outputs" / "profile_summary.json")
    _touch(src_root / "alignment" / "outputs" / "bl003_ds001_spotify_summary.json")

    result = validate_bl009_outputs(str(observability_outputs), "warn")

    assert result["status"] == "pass"
    assert result["violations"] == []
    assert result["details"]["missing_files"] == []


def test_validate_bl009_outputs_warns_when_current_and_legacy_artifacts_missing(tmp_path: Path) -> None:
    observability_outputs = tmp_path / "src" / "observability" / "outputs"
    _touch(
        observability_outputs / "bl009_run_observability_log.json",
        content=(
            '{'
            '"run_metadata": {},'
            '"execution_scope_summary": {},'
            '"run_config": {},'
            '"ingestion_alignment_diagnostics": {},'
            '"stage_diagnostics": {},'
            '"exclusion_diagnostics": {},'
            '"validity_boundaries": {},'
            '"output_artifacts": {}'
            '}'
        ),
    )
    _touch(observability_outputs / "bl009_run_index.csv", content="run_id\nBL009\n")

    result = validate_bl009_outputs(str(observability_outputs), "warn")

    assert result["status"] == "warn"
    assert "missing_file=bl008_explanation_payloads.json" in result["violations"]
    assert "missing_file=bl003_ds001_spotify_summary.json" in result["violations"]
