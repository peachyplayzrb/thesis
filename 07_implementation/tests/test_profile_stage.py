"""Tests for BL-004 profile stage OO shell."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from profile.models import ProfileAggregation, ProfileControls, ProfileInputs, ProfilePaths
from profile.runtime_controls import resolve_bl004_runtime_controls
from profile.stage import NUMERIC_FEATURE_COLUMNS, ProfileStage
from shared_utils.constants import DEFAULT_INPUT_SCOPE, DEFAULT_PROFILE_CONTROLS


def _write_load_inputs_artifacts(
    tmp_path: Path,
    *,
    include_runtime_scope_diagnostics: bool,
) -> ProfilePaths:
    seed_table_path = tmp_path / "seed.csv"
    numeric_headers = ",".join(NUMERIC_FEATURE_COLUMNS)
    numeric_values = "0.5,0.5,0.5,120,1,1,50,180000,2010"
    seed_table_path.write_text(
        (
            "ds001_id,spotify_track_ids,interaction_types,preference_weight_sum,"
            f"interaction_count_sum,match_confidence_score,tags,genres,artist,song,{numeric_headers}\n"
            f"track_1,sp_1,history,1.0,5,1.0,rock,rock,artist_a,song_a,{numeric_values}\n"
        ),
        encoding="utf-8",
    )

    summary_inputs: dict[str, object] = {
        "seed_contract": {
            "seed_contract_schema_version": "bl003-seed-contract-v1",
            "contract_hash": "seed-hash",
        },
        "structural_contract": {
            "structural_contract_schema_version": "bl003-structural-contract-v1",
            "contract_hash": "struct-hash",
            "seed_table_fieldnames": [
                "ds001_id",
                "spotify_track_ids",
                "interaction_types",
                "preference_weight_sum",
                "interaction_count_sum",
                "match_confidence_score",
                "tags",
                "genres",
                "artist",
                "song",
                *NUMERIC_FEATURE_COLUMNS,
            ],
        },
    }
    if include_runtime_scope_diagnostics:
        summary_inputs["runtime_scope_diagnostics"] = {"resolution_path": "run_config"}

    summary_payload = {
        "inputs": summary_inputs,
        "counts": {
            "input_event_rows": 1,
            "matched_by_spotify_id": 1,
            "matched_by_metadata": 0,
            "matched_by_fuzzy": 0,
            "unmatched": 0,
        },
    }
    summary_path = tmp_path / "bl003_summary.json"
    summary_path.write_text(json.dumps(summary_payload), encoding="utf-8")

    manifest_payload = {
        "rows_selected": {"top_tracks": 1},
        "rows_available": {"top_tracks": 1},
        "seed_contract": {
            "seed_contract_schema_version": "bl003-seed-contract-v1",
            "contract_hash": "seed-hash",
        },
        "structural_contract": {
            "structural_contract_schema_version": "bl003-structural-contract-v1",
            "contract_hash": "struct-hash",
            "seed_table_fieldnames": [
                "ds001_id",
                "spotify_track_ids",
                "interaction_types",
                "preference_weight_sum",
                "interaction_count_sum",
                "match_confidence_score",
                "tags",
                "genres",
                "artist",
                "song",
                *NUMERIC_FEATURE_COLUMNS,
            ],
        },
    }
    manifest_path = tmp_path / "bl003_manifest.json"
    manifest_path.write_text(json.dumps(manifest_payload), encoding="utf-8")

    output_dir = tmp_path / "outputs"
    return ProfilePaths(
        seed_table_path=seed_table_path,
        bl003_summary_path=summary_path,
        bl003_manifest_path=manifest_path,
        output_dir=output_dir,
        seed_trace_path=output_dir / "seed_trace.csv",
        profile_path=output_dir / "profile.json",
        summary_path=output_dir / "summary.json",
    )


def _controls(include_types: list[str] | None = None, **overrides: object) -> ProfileControls:
    base = ProfileControls(
        config_source="test",
        run_config_path=None,
        run_config_schema_version=None,
        input_scope={"spotify_sources": ["top_tracks"]},
        top_tag_limit=3,
        top_genre_limit=3,
        top_lead_genre_limit=3,
        user_id="user_1",
        include_interaction_types=include_types or ["history", "influence"],
    )
    if not overrides:
        return base
    return ProfileControls(**{**base.__dict__, **overrides})


def _inputs(seed_rows: list[dict[str, object]]) -> ProfileInputs:
    return ProfileInputs(
        seed_rows=seed_rows,
        bl003_summary={"inputs": {}},
        bl003_manifest={"rows_selected": {}, "rows_available": {}},
        bl003_seed_contract={"seed_contract_schema_version": "bl003-seed-contract-v1"},
        bl003_structural_contract={
            "structural_contract_schema_version": "bl003-structural-contract-v1",
            "seed_table_fieldnames": [
                "ds001_id",
                "spotify_track_ids",
                "interaction_types",
                "preference_weight_sum",
                "interaction_count_sum",
                "match_confidence_score",
                "tags",
                "genres",
                "artist",
                "song",
                *NUMERIC_FEATURE_COLUMNS,
            ],
        },
        bl003_seed_contract_hash="seed-hash",
        bl003_structural_contract_hash="struct-hash",
    )


def test_circular_mean_key_handles_zero_vector() -> None:
    assert ProfileStage.circular_mean_key(0.0, 0.0) is None


def test_sorted_weight_map_is_deterministic_on_ties() -> None:
    weights = {"rock": 1.0, "jazz": 1.0, "ambient": 2.0}
    result = ProfileStage.sorted_weight_map(weights, limit=3)
    assert [row["label"] for row in result] == ["ambient", "jazz", "rock"]


def test_aggregate_inputs_respects_interaction_type_filter() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "track_history",
                "spotify_track_ids": "sp_hist",
                "interaction_types": "history",
                "preference_weight_sum": "0.7",
                "interaction_count_sum": "7",
                "tags": "rock,indie",
                "genres": "rock",
                "tempo": "100",
                "release": "2011",
                "key": "1",
                "artist": "A",
                "song": "S1",
            },
            {
                "ds001_id": "track_influence",
                "spotify_track_ids": "sp_inf",
                "interaction_types": "influence",
                "preference_weight_sum": "0.6",
                "interaction_count_sum": "6",
                "tags": "jazz",
                "genres": "jazz",
                "tempo": "130",
                "release": "2019",
                "key": "11",
                "artist": "B",
                "song": "S2",
            },
        ]
    )

    aggregation = ProfileStage.aggregate_inputs(inputs, _controls(include_types=["history"]))

    assert aggregation.input_row_count == 2
    assert aggregation.matched_seed_count == 1
    assert [row["track_id"] for row in aggregation.seed_trace_rows] == ["track_history"]
    assert aggregation.counts_by_type["history"] == 1
    assert aggregation.counts_by_type["influence"] == 0
    assert "release_year" in aggregation.numeric_profile
    assert round(aggregation.numeric_profile["tempo"], 3) == 100.0


def test_aggregate_inputs_uses_confidence_adjusted_effective_weight() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "track_high_conf",
                "spotify_track_ids": "sp_high",
                "interaction_types": "history",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "10",
                "match_confidence_score": "1.0",
                "tags": "rock",
                "genres": "rock",
                "tempo": "100",
                "release": "2011",
                "key": "1",
                "artist": "A",
                "song": "S1",
            },
            {
                "ds001_id": "track_low_conf",
                "spotify_track_ids": "sp_low",
                "interaction_types": "influence",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "10",
                "match_confidence_score": "0.0",
                "tags": "jazz",
                "genres": "jazz",
                "tempo": "140",
                "release": "2019",
                "key": "11",
                "artist": "B",
                "song": "S2",
            },
        ]
    )

    aggregation = ProfileStage.aggregate_inputs(inputs, _controls())

    assert aggregation.matched_seed_count == 2
    assert aggregation.weight_by_type["history"] == 1.0
    assert aggregation.weight_by_type["influence"] == 0.5
    assert aggregation.total_effective_weight == 1.5
    assert aggregation.confidence_adjusted_weight_sum == 1.5
    assert aggregation.seed_trace_rows[0]["effective_weight"] == 1.0
    assert aggregation.seed_trace_rows[1]["effective_weight"] == 0.5


def test_aggregate_inputs_supports_direct_confidence_weighting_mode() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "track_1",
                "spotify_track_ids": "sp_1",
                "interaction_types": "history",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "5",
                "match_confidence_score": "0.4",
                "tags": "ambient",
                "genres": "ambient",
                "tempo": "100",
                "key": "1",
                "release": "2011",
                "artist": "A",
                "song": "S1",
            }
        ]
    )
    controls = _controls(
        confidence_weighting_mode="direct_confidence",
        confidence_bin_high_threshold=0.8,
        confidence_bin_medium_threshold=0.3,
    )

    aggregation = ProfileStage.aggregate_inputs(inputs, controls)

    assert aggregation.total_effective_weight == 0.4
    assert aggregation.seed_trace_rows[0]["effective_weight"] == 0.4
    assert aggregation.confidence_bins["high_0_9_plus"] == 0
    assert aggregation.confidence_bins["medium_0_5_to_0_9"] == 1


def test_aggregate_inputs_excludes_blank_track_id_from_missing_numeric_ids() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "",
                "spotify_track_ids": "sp_only",
                "interaction_types": "history",
                "preference_weight_sum": "0.5",
                "interaction_count_sum": "5",
                "tags": "ambient",
                "genres": "ambient",
                "artist": "A",
                "song": "S1",
            }
        ]
    )

    aggregation = ProfileStage.aggregate_inputs(inputs, _controls(include_types=["history"]))

    assert aggregation.blank_track_id_row_count == 1
    assert aggregation.missing_numeric_track_ids == []
    assert aggregation.seed_trace_rows[0]["track_id"] == "sp_only"


def test_build_profile_payload_emits_missing_numeric_diagnostics_keys(tmp_path: Path) -> None:
    aggregation = ProfileAggregation(
        input_row_count=3,
        seed_trace_rows=[{"seed_rank": 1}],
        numeric_profile={"tempo": 120.0},
        tag_weights={},
        genre_weights={},
        lead_genre_weights={},
        counts_by_type={"history": 1, "influence": 0},
        weight_by_type={"history": 1.0, "influence": 0.0},
        interaction_count_sum_by_type={"history": 5, "influence": 0},
        numeric_observations={column: 0 for column in NUMERIC_FEATURE_COLUMNS},
        missing_numeric_track_ids=["track_1", "track_2"],
        blank_track_id_row_count=1,
        total_effective_weight=1.0,
        confidence_adjusted_weight_sum=0.8,
        confidence_bins={
            "high_0_9_plus": 1,
            "medium_0_5_to_0_9": 0,
            "low_below_0_5": 0,
        },
        match_method_counts={
            "spotify_id_exact": 1,
            "metadata_fallback": 0,
            "fuzzy_title_artist": 0,
        },
        history_preference_weight_sum=1.0,
        influence_preference_weight_sum=0.0,
        history_interaction_count_sum=5,
        influence_interaction_count_sum=0,
        matched_seed_count=1,
    )

    controls = _controls()
    seed_table_path = tmp_path / "seed.csv"
    seed_table_path.write_text("ds001_id\ntrack_1\n", encoding="utf-8")

    paths = ProfilePaths(
        seed_table_path=seed_table_path,
        bl003_summary_path=Path("bl003_summary.json"),
        bl003_manifest_path=Path("bl003_manifest.json"),
        output_dir=Path("outputs"),
        seed_trace_path=Path("seed_trace.csv"),
        profile_path=Path("profile.json"),
        summary_path=Path("summary.json"),
    )
    inputs = _inputs([])

    payload = ProfileStage.build_profile_payload(
        run_id="BL004-test",
        controls=controls,
        paths=paths,
        inputs=inputs,
        aggregation=aggregation,
        elapsed_seconds=0.1,
    )
    diagnostics = payload["diagnostics"]

    assert diagnostics["missing_numeric_track_count"] == 2
    assert diagnostics["missing_numeric_track_ids"] == ["track_1", "track_2"]
    assert diagnostics["blank_track_id_rows"] == 1
    assert diagnostics["confidence_adjusted_weight_sum"] == 0.8
    assert diagnostics["match_method_counts"]["spotify_id_exact"] == 1
    assert payload["input_artifacts"]["bl003_seed_contract_hash"] == "seed-hash"
    assert payload["input_artifacts"]["bl003_structural_contract_hash"] == "struct-hash"


def test_aggregate_inputs_supports_primary_type_only_attribution() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "mixed_row",
                "spotify_track_ids": "sp_mixed",
                "interaction_types": "history|influence",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "10",
                "tags": "rock",
                "genres": "rock",
                "tempo": "100",
                "release": "2011",
                "key": "1",
                "artist": "A",
                "song": "S1",
            }
        ]
    )
    controls = _controls(interaction_attribution_mode="primary_type_only")

    aggregation = ProfileStage.aggregate_inputs(inputs, controls)

    assert aggregation.mixed_interaction_row_count == 1
    assert aggregation.primary_type_attribution_row_count == 1
    assert aggregation.attribution_weight_by_type["influence"] == aggregation.total_effective_weight
    assert aggregation.attribution_weight_by_type["history"] == 0.0


def test_aggregate_inputs_tracks_fallback_diagnostics() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "track_1",
                "spotify_track_ids": "sp_1",
                "interaction_types": "garbage",
                "preference_weight_sum": "1.2",
                "interaction_count_sum": "",
                "match_confidence_score": "bad-value",
                "tags": "rock",
                "genres": "rock",
                "tempo": "120",
                "release": "2010",
                "key": "1",
                "artist": "A",
                "song": "S1",
            },
            {
                "ds001_id": "track_2",
                "spotify_track_ids": "sp_2",
                "interaction_types": "history",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "",
                "match_confidence_score": "bad-value",
                "tags": "jazz",
                "genres": "jazz",
                "tempo": "110",
                "release": "2012",
                "key": "2",
                "artist": "B",
                "song": "S2",
            }
        ]
    )

    aggregation = ProfileStage.aggregate_inputs(inputs, _controls())

    assert aggregation.confidence_fallback_row_count == 1
    assert aggregation.defaulted_interaction_type_row_count == 1
    assert aggregation.synthetic_interaction_count_row_count == 1
    assert aggregation.synthetic_history_weight_row_count == 1
    assert aggregation.synthetic_influence_weight_row_count == 0
    assert len(aggregation.validation_warnings) == 3


def test_aggregate_inputs_strict_confidence_policy_raises() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "track_1",
                "spotify_track_ids": "sp_1",
                "interaction_types": "history",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "5",
                "match_confidence_score": "bad-value",
                "tags": "rock",
                "genres": "rock",
                "tempo": "120",
                "release": "2010",
                "key": "1",
                "artist": "A",
                "song": "S1",
            }
        ]
    )
    controls = _controls(confidence_validation_policy="strict")

    with pytest.raises(RuntimeError, match="BL-004 strict validation failed"):
        ProfileStage.aggregate_inputs(inputs, controls)


def test_validate_bl003_handshake_warn_policy_collects_warnings() -> None:
    warnings = ProfileStage._validate_bl003_handshake(
        summary_payload={"inputs": {}},
        structural_contract={"seed_table_fieldnames": []},
        policy="warn",
    )

    assert warnings == [
        "missing BL-003 summary input key: runtime_scope_diagnostics",
        "missing BL-003 structural seed field: match_confidence_score",
    ]


def test_validate_bl003_handshake_strict_policy_raises() -> None:
    with pytest.raises(RuntimeError, match="BL-004 handshake validation failed"):
        ProfileStage._validate_bl003_handshake(
            summary_payload={"inputs": {}},
            structural_contract={"seed_table_fieldnames": []},
            policy="strict",
        )


def test_load_inputs_warn_handshake_policy_tracks_warning(tmp_path: Path) -> None:
    paths = _write_load_inputs_artifacts(
        tmp_path,
        include_runtime_scope_diagnostics=False,
    )
    inputs = ProfileStage.load_inputs(paths, _controls(bl003_handshake_validation_policy="warn"))

    assert inputs.bl003_handshake_warnings == [
        "missing BL-003 summary input key: runtime_scope_diagnostics"
    ]


def test_load_inputs_strict_handshake_policy_raises(tmp_path: Path) -> None:
    paths = _write_load_inputs_artifacts(
        tmp_path,
        include_runtime_scope_diagnostics=False,
    )

    with pytest.raises(RuntimeError, match="BL-004 handshake validation failed"):
        ProfileStage.load_inputs(paths, _controls(bl003_handshake_validation_policy="strict"))


def test_aggregate_inputs_tracks_malformed_numeric_diagnostics() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "track_1",
                "spotify_track_ids": "sp_1",
                "interaction_types": "history",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "bad-count",
                "match_confidence_score": "bad-confidence",
                "history_preference_weight_sum": "bad-history",
                "influence_preference_weight_sum": "",
                "tempo": "fast",
                "release": "",
                "key": "",
                "artist": "A",
                "song": "S1",
                "tags": "rock",
                "genres": "rock",
            }
        ]
    )

    aggregation = ProfileStage.aggregate_inputs(inputs, _controls())

    assert aggregation.confidence_malformed_row_count == 1
    assert aggregation.interaction_count_malformed_row_count == 1
    assert aggregation.history_weight_malformed_row_count == 1
    assert aggregation.malformed_numeric_row_count == 1
    assert aggregation.no_numeric_signal_row_count == 0
    assert aggregation.malformed_numeric_value_count_by_feature["tempo"] == 1


def test_aggregate_inputs_numeric_malformed_threshold_raises() -> None:
    inputs = _inputs(
        [
            {
                "ds001_id": "track_1",
                "spotify_track_ids": "sp_1",
                "interaction_types": "history",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "5",
                "tempo": "bad",
                "artist": "A",
                "song": "S1",
                "tags": "rock",
                "genres": "rock",
            },
            {
                "ds001_id": "track_2",
                "spotify_track_ids": "sp_2",
                "interaction_types": "history",
                "preference_weight_sum": "1.0",
                "interaction_count_sum": "5",
                "tempo": "still-bad",
                "artist": "B",
                "song": "S2",
                "tags": "pop",
                "genres": "pop",
            }
        ]
    )

    controls = _controls(numeric_malformed_row_threshold=1)
    with pytest.raises(RuntimeError, match="numeric integrity threshold failed"):
        ProfileStage.aggregate_inputs(inputs, controls)


def test_build_profile_payload_emits_fallback_diagnostics_keys(tmp_path: Path) -> None:
    aggregation = ProfileAggregation(
        input_row_count=1,
        seed_trace_rows=[{"seed_rank": 1}],
        numeric_profile={"tempo": 100.0},
        tag_weights={},
        genre_weights={},
        lead_genre_weights={},
        counts_by_type={"history": 1, "influence": 0},
        weight_by_type={"history": 1.0, "influence": 0.0},
        interaction_count_sum_by_type={"history": 10, "influence": 0},
        numeric_observations={column: 0 for column in NUMERIC_FEATURE_COLUMNS},
        missing_numeric_track_ids=[],
        blank_track_id_row_count=0,
        total_effective_weight=1.0,
        confidence_adjusted_weight_sum=1.0,
        confidence_bins={
            "high_0_9_plus": 1,
            "medium_0_5_to_0_9": 0,
            "low_below_0_5": 0,
        },
        match_method_counts={
            "spotify_id_exact": 1,
            "metadata_fallback": 0,
            "fuzzy_title_artist": 0,
        },
        history_preference_weight_sum=1.0,
        influence_preference_weight_sum=0.0,
        history_interaction_count_sum=10,
        influence_interaction_count_sum=0,
        matched_seed_count=1,
        confidence_fallback_row_count=1,
        defaulted_interaction_type_row_count=2,
        synthetic_interaction_count_row_count=3,
        synthetic_history_weight_row_count=4,
        synthetic_influence_weight_row_count=5,
        validation_policies={
            "confidence_validation_policy": "warn",
            "interaction_type_validation_policy": "warn",
            "synthetic_data_validation_policy": "warn",
        },
        validation_warnings=["warned"],
    )

    controls = _controls()
    seed_table_path = tmp_path / "seed.csv"
    seed_table_path.write_text("ds001_id\ntrack_1\n", encoding="utf-8")
    paths = ProfilePaths(
        seed_table_path=seed_table_path,
        bl003_summary_path=Path("bl003_summary.json"),
        bl003_manifest_path=Path("bl003_manifest.json"),
        output_dir=Path("outputs"),
        seed_trace_path=Path("seed_trace.csv"),
        profile_path=Path("profile.json"),
        summary_path=Path("summary.json"),
    )

    payload = ProfileStage.build_profile_payload(
        run_id="BL004-test",
        controls=controls,
        paths=paths,
        inputs=_inputs([]),
        aggregation=aggregation,
        elapsed_seconds=0.1,
    )
    diagnostics = payload["diagnostics"]

    assert diagnostics["confidence_fallback_row_count"] == 1
    assert diagnostics["defaulted_interaction_type_row_count"] == 2
    assert diagnostics["synthetic_interaction_count_row_count"] == 3
    assert diagnostics["synthetic_history_weight_row_count"] == 4
    assert diagnostics["synthetic_influence_weight_row_count"] == 5
    assert diagnostics["validation_policies"]["confidence_validation_policy"] == "warn"
    assert diagnostics["validation_warnings"] == ["warned"]


def test_validate_seed_table_schema_raises_on_missing_contract_columns() -> None:
    seed_rows = [
        {
            "ds001_id": "track_1",
            "spotify_track_ids": "sp_1",
            "interaction_types": "history",
            "preference_weight_sum": "0.5",
            "interaction_count_sum": "5",
            "tags": "ambient",
            "genres": "ambient",
            "artist": "A",
            "song": "S",
            "danceability": "0.1",
            "energy": "0.2",
            "valence": "0.3",
            "tempo": "100",
            "key": "1",
            "mode": "1",
            "popularity": "10",
            "duration_ms": "200000",
            "release": "2020",
        }
    ]
    structural_contract = {
        "seed_table_fieldnames": [
            "ds001_id",
            "spotify_track_ids",
            "interaction_types",
            "preference_weight_sum",
            "interaction_count_sum",
            "missing_column_from_seed_table",
        ]
    }

    with pytest.raises(RuntimeError, match="missing columns"):
        ProfileStage._validate_seed_table_schema(seed_rows, structural_contract)


def test_build_summary_payload_includes_bl003_coverage() -> None:
    controls = _controls()
    paths = ProfilePaths(
        seed_table_path=Path("seed.csv"),
        bl003_summary_path=Path("bl003_summary.json"),
        bl003_manifest_path=Path("bl003_manifest.json"),
        output_dir=Path("outputs"),
        seed_trace_path=Path("seed_trace.csv"),
        profile_path=Path("profile.json"),
        summary_path=Path("summary.json"),
    )
    inputs = ProfileInputs(
        seed_rows=[],
        bl003_summary={
            "counts": {
                "input_event_rows": 10,
                "matched_by_spotify_id": 5,
                "matched_by_metadata": 2,
                "matched_by_fuzzy": 1,
                "unmatched": 2,
            }
        },
        bl003_manifest={
            "rows_selected": {"top_tracks": 50},
            "rows_available": {"top_tracks": 60},
        },
        bl003_seed_contract={"seed_contract_schema_version": "bl003-seed-contract-v1"},
        bl003_structural_contract={"structural_contract_schema_version": "bl003-structural-contract-v1"},
        bl003_seed_contract_hash="seed-hash",
        bl003_structural_contract_hash="struct-hash",
    )
    aggregation = ProfileAggregation(
        input_row_count=1,
        seed_trace_rows=[{"seed_rank": 1}],
        numeric_profile={"tempo": 120.0},
        tag_weights={},
        genre_weights={},
        lead_genre_weights={},
        counts_by_type={"history": 1, "influence": 0},
        weight_by_type={"history": 1.0, "influence": 0.0},
        interaction_count_sum_by_type={"history": 5, "influence": 0},
        numeric_observations={column: 0 for column in NUMERIC_FEATURE_COLUMNS},
        missing_numeric_track_ids=[],
        blank_track_id_row_count=0,
        total_effective_weight=1.0,
        confidence_adjusted_weight_sum=0.9,
        confidence_bins={
            "high_0_9_plus": 1,
            "medium_0_5_to_0_9": 0,
            "low_below_0_5": 0,
        },
        match_method_counts={
            "spotify_id_exact": 1,
            "metadata_fallback": 0,
            "fuzzy_title_artist": 0,
        },
        history_preference_weight_sum=1.0,
        influence_preference_weight_sum=0.0,
        history_interaction_count_sum=5,
        influence_interaction_count_sum=0,
        matched_seed_count=1,
    )

    payload = ProfileStage.build_summary_payload(
        run_id="BL004-test",
        controls=controls,
        paths=paths,
        inputs=inputs,
        profile={"semantic_profile": {}, "input_artifacts": {}},
        aggregation=aggregation,
    )

    coverage = payload["bl003_coverage"]
    assert coverage["rows_selected"]["top_tracks"] == 50
    assert coverage["rows_available"]["top_tracks"] == 60
    assert coverage["match_counts"]["matched_total"] == 8
    assert coverage["match_counts"]["match_rate"] == 0.8


def test_resolve_bl004_runtime_controls_defaults_input_scope(monkeypatch) -> None:
    monkeypatch.delenv("BL_STAGE_CONFIG_JSON", raising=False)
    monkeypatch.setenv("BL004_TOP_TAG_LIMIT", "5")
    monkeypatch.setenv("BL004_TOP_GENRE_LIMIT", "5")
    monkeypatch.setenv("BL004_TOP_LEAD_GENRE_LIMIT", "5")
    monkeypatch.setenv("BL004_INCLUDE_INTERACTION_TYPES", "history,influence")

    controls = resolve_bl004_runtime_controls()

    assert controls["input_scope"] == dict(DEFAULT_INPUT_SCOPE)
    assert controls["confidence_validation_policy"] == "warn"
    assert controls["interaction_type_validation_policy"] == "warn"
    assert controls["synthetic_data_validation_policy"] == "warn"
    assert controls["bl003_handshake_validation_policy"] == "warn"
    assert controls["numeric_malformed_row_threshold"] is None
    assert controls["no_numeric_signal_row_threshold"] is None


def test_resolve_bl004_runtime_controls_payload_uses_defaults_not_env(monkeypatch) -> None:
    monkeypatch.setenv("BL004_TOP_TAG_LIMIT", "99")
    monkeypatch.setenv(
        "BL_STAGE_CONFIG_JSON",
        json.dumps(
            {
                "controls": {
                    "top_genre_limit": 6,
                }
            }
        ),
    )

    controls = resolve_bl004_runtime_controls()

    assert controls["config_source"] == "defaults"
    assert controls["top_tag_limit"] == int(DEFAULT_PROFILE_CONTROLS["top_tag_limit"])
    assert controls["top_genre_limit"] == 6
    assert controls["confidence_validation_policy"] == "warn"
    assert controls["bl003_handshake_validation_policy"] == "warn"
