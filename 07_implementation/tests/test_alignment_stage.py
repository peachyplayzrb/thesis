"""Tests for BL-003 alignment stage shell."""

from __future__ import annotations


# pyright: reportMissingImports=false

import json

import pytest

from alignment.stage import AlignmentStage


def _write_minimal_ds001_csv(path) -> None:
    path.write_text(
        "id,spotify_id,song,artist\n"
        "track_001,sp_001,Song One,Artist One\n",
        encoding="utf-8",
    )


def test_resolve_expected_sources_run_config_scope() -> None:
    expected = AlignmentStage.resolve_expected_sources(
        runtime_scope={"config_source": "run_config"},
        input_scope={
            "include_top_tracks": True,
            "include_saved_tracks": False,
            "include_playlists": True,
            "include_recently_played": False,
        },
        export_selection={},
    )

    assert expected == {
        "top_tracks": True,
        "saved_tracks": False,
        "playlist_items": True,
        "recently_played": False,
    }


def test_enforce_selected_source_requirements_raises_when_strict(tmp_path) -> None:
    stage = AlignmentStage(
        ds001_path=tmp_path / "ds001.csv",
        spotify_dir=tmp_path / "spotify",
        output_dir=tmp_path / "out",
        allow_missing_selected_sources=False,
    )

    with pytest.raises(RuntimeError, match="strict selected-source check failed"):
        stage.enforce_selected_source_requirements(
            expected_sources={"top_tracks": True},
            available_sources={"top_tracks": False},
            source_resilience_policy={"top_tracks": "required"},
        )


def test_enforce_selected_source_requirements_degrades_optional_sources(tmp_path) -> None:
    stage = AlignmentStage(
        ds001_path=tmp_path / "ds001.csv",
        spotify_dir=tmp_path / "spotify",
        output_dir=tmp_path / "out",
        allow_missing_selected_sources=False,
    )

    missing_selected, missing_required, degraded_optional = stage.enforce_selected_source_requirements(
        expected_sources={"top_tracks": True, "playlist_items": True},
        available_sources={"top_tracks": True, "playlist_items": False},
        source_resilience_policy={"top_tracks": "required", "playlist_items": "optional"},
    )

    assert missing_selected == ["playlist_items"]
    assert missing_required == []
    assert degraded_optional == ["playlist_items"]


def test_run_writes_summary_on_empty_input_events(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("BL_RUN_CONFIG_PATH", raising=False)
    monkeypatch.delenv("BL003_INPUT_SCOPE_JSON", raising=False)

    ds001_path = tmp_path / "ds001_candidates.csv"
    _write_minimal_ds001_csv(ds001_path)

    spotify_dir = tmp_path / "spotify_export"
    spotify_dir.mkdir(parents=True, exist_ok=True)

    output_dir = tmp_path / "alignment_outputs"
    stage = AlignmentStage(
        ds001_path=ds001_path,
        spotify_dir=spotify_dir,
        output_dir=output_dir,
        allow_missing_selected_sources=True,
    )

    artifacts = stage.run()

    assert artifacts.summary_path.exists()
    summary = json.loads(artifacts.summary_path.read_text(encoding="utf-8"))
    assert summary["task"] == "BL-003-DS001-spotify-seed-build"
    assert summary["summary_schema_version"] == "bl003-summary-v1"
    assert summary["artifact_contract_version"] == "bl003-artifacts-v1"
    assert summary["counts"]["input_event_rows"] == 0
    assert "match_rate_validation" in summary["counts"]
    assert "seed_contract" in summary["inputs"]
    assert summary["inputs"]["seed_contract"]["seed_contract_schema_version"] == "bl003-seed-contract-v1"
    assert summary["inputs"]["seed_contract"]["top_range_weights"] == {
        "short_term": 0.5,
        "medium_term": 0.3,
        "long_term": 0.2,
    }
    assert summary["inputs"]["seed_contract"]["source_base_weights"]["top_tracks"] == 1.0
    assert summary["inputs"]["seed_contract"]["match_strategy_order"] == [
        "spotify_id_exact",
        "metadata_fallback",
        "fuzzy_title_artist",
    ]
    assert summary["inputs"]["structural_contract"]["structural_contract_schema_version"] == "bl003-structural-contract-v1"
    assert summary["inputs"]["structural_contract"]["output_filenames"]["seed_table_csv"] == "bl003_ds001_spotify_seed_table.csv"
    assert "sha256" in summary["outputs"]
    scope_manifest = json.loads(
        (output_dir / "bl003_source_scope_manifest.json").read_text(encoding="utf-8")
    )
    assert scope_manifest["artifact_schema_version"] == "bl003-source-scope-manifest-v1"
    assert scope_manifest["artifact_contract_version"] == "bl003-artifacts-v1"
    assert scope_manifest["seed_contract"]["seed_contract_schema_version"] == "bl003-seed-contract-v1"
    assert scope_manifest["structural_contract"]["structural_contract_schema_version"] == "bl003-structural-contract-v1"
    assert scope_manifest["seed_contract"]["contract_hash"]
    assert scope_manifest["structural_contract"]["contract_hash"]
    assert artifacts.matched_events_rows == 0
    assert artifacts.seed_table_rows == 0


def test_run_treats_zero_results_source_outcome_as_available_in_strict_mode(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("BL_RUN_CONFIG_PATH", raising=False)
    monkeypatch.delenv("BL003_INPUT_SCOPE_JSON", raising=False)

    ds001_path = tmp_path / "ds001_candidates.csv"
    _write_minimal_ds001_csv(ds001_path)

    spotify_dir = tmp_path / "spotify_export"
    spotify_dir.mkdir(parents=True, exist_ok=True)
    (spotify_dir / "spotify_export_run_summary.json").write_text(
        json.dumps(
            {
                "selection": {
                    "include_top_tracks": True,
                    "include_saved_tracks": False,
                    "include_playlists": False,
                    "include_recently_played": False,
                },
                "source_outcomes": {
                    "top_tracks": {"status": "zero_results"},
                },
            }
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "alignment_outputs"
    stage = AlignmentStage(
        ds001_path=ds001_path,
        spotify_dir=spotify_dir,
        output_dir=output_dir,
        allow_missing_selected_sources=False,
    )

    artifacts = stage.run()
    summary = json.loads(artifacts.summary_path.read_text(encoding="utf-8"))
    assert summary["inputs"]["missing_required_sources"] == []
