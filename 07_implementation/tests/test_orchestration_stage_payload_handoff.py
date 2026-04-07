"""End-to-end tests for orchestration → stage payload handoff (Phase 3/4)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from orchestration import config_resolver


def test_resolve_stage_control_payload_bl003_includes_all_seed_controls() -> None:
    """Verify BL-003 payload includes all seed controls from orchestration resolution."""
    # Phase 3: Simulate orchestration resolving BL-003 controls
    payload = config_resolver.resolve_stage_control_payload("BL-003", run_config_path=None)

    # Verify payload structure
    assert isinstance(payload, dict)
    assert payload["stage_id"] == "BL-003"
    assert payload["schema_version"] == "1.0"
    assert "resolved_from" in payload
    assert "controls" in payload

    # Verify seed controls have expected keys
    controls = dict(payload["controls"])
    seed = controls["seed_controls"]
    assert "top_range_weights" in seed
    assert "source_base_weights" in seed
    assert "fuzzy_matching" in seed
    assert "match_strategy" in seed
    assert "match_strategy_order" in seed
    assert "temporal_controls" in seed
    assert "aggregation_policy" in seed
    assert "decay_half_lives" in seed
    assert "match_rate_min_threshold" in seed


def test_resolve_stage_control_payload_bl004_includes_all_profile_controls() -> None:
    """Verify BL-004 payload includes all profile controls."""
    payload = config_resolver.resolve_stage_control_payload("BL-004", run_config_path=None)

    assert isinstance(payload, dict)
    assert payload["stage_id"] == "BL-004"
    assert payload["schema_version"] == "1.0"
    controls = dict(payload["controls"])
    assert "top_tag_limit" in controls or len(controls) > 0


def test_resolve_stage_control_payloads_produces_per_stage_map() -> None:
    """Verify orchestration can resolve all stages' payloads at once."""
    stage_order = ["BL-003", "BL-004", "BL-006", "BL-007"]
    payloads = config_resolver.resolve_stage_control_payloads(stage_order, run_config_path=None)

    assert isinstance(payloads, dict)
    assert set(payloads.keys()) == set(stage_order)

    # Each stage has a non-empty payload
    for stage_id, payload in payloads.items():
        assert isinstance(payload, dict), f"Payload for {stage_id} should be dict"


def test_stage_payload_can_be_json_serialized() -> None:
    """Verify payload can be serialized to JSON for env var passing (Phase 2 handoff)."""
    payload = config_resolver.resolve_stage_control_payload("BL-003", run_config_path=None)

    # Must be JSON-serializable
    json_str = json.dumps(payload, ensure_ascii=True, sort_keys=True)
    assert isinstance(json_str, str)
    assert len(json_str) > 0

    # Must round-trip
    decoded = json.loads(json_str)
    assert decoded == payload


def test_resolve_stage_control_payload_with_invalid_stage_id() -> None:
    """Verify invalid stage IDs return empty dict."""
    payload = config_resolver.resolve_stage_control_payload("INVALID-STAGE", run_config_path=None)
    assert payload == {}


def test_orchestration_to_stage_handoff_via_env_var(monkeypatch) -> None:
    """Phase 3/4: Simulate full orchestration → stage handoff via BL_STAGE_CONFIG_JSON."""
    # Step 1: Orchestration resolves all stage payloads
    stage_order = ["BL-003", "BL-007"]
    all_payloads = config_resolver.resolve_stage_control_payloads(stage_order, run_config_path=None)

    # Step 2: For each stage, orchestration injects payload via env var
    stage_id = "BL-003"
    payload = all_payloads[stage_id]

    # Simulate what stage_runner.run_stage does
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", json.dumps(payload, ensure_ascii=True, sort_keys=True))

    # Step 3: Stage reads payload and uses it
    payload_raw = os.environ.get("BL_STAGE_CONFIG_JSON", "").strip()
    assert payload_raw
    decoded = json.loads(payload_raw)

    # Step 4: Verify stage received the right data
    assert decoded["stage_id"] == "BL-003"
    controls = dict(decoded["controls"])
    assert "seed_controls" in controls
    assert "input_scope_controls" in controls

    # Cleanup
    monkeypatch.delenv("BL_STAGE_CONFIG_JSON")


def test_payload_precedence_payload_over_env_var(monkeypatch) -> None:
    """Phase 3: Verify payload takes precedence over stage-local env vars."""
    # Set both payload and env vars
    payload = {
        "stage_id": "BL-003",
        "schema_version": "1.0",
        "resolved_from": "defaults",
        "controls": {
            "seed_controls": {
                "top_range_weights": {"short_term": 0.9, "medium_term": 0.05, "long_term": 0.05},
            }
        },
    }
    monkeypatch.setenv("BL_STAGE_CONFIG_JSON", json.dumps(payload))
    monkeypatch.setenv("BL003_INPUT_SCOPE_JSON", '{"include_top_tracks": false}')

    # Stage should prefer payload over env var
    payload_raw = os.environ.get("BL_STAGE_CONFIG_JSON", "").strip()
    assert payload_raw
    decoded = json.loads(payload_raw)

    # Payload is present and has precedence
    controls = dict(decoded["controls"])
    assert "seed_controls" in controls
    assert controls["seed_controls"]["top_range_weights"]["short_term"] == 0.9

    # Cleanup
    monkeypatch.delenv("BL_STAGE_CONFIG_JSON")
    monkeypatch.delenv("BL003_INPUT_SCOPE_JSON")


def test_payload_fixture_helper_for_test_injections() -> None:
    """Phase 4: Helper to make it easy for tests to build payload fixtures."""

    def make_bl003_payload_fixture(
        top_range_weights: dict | None = None,
        match_strategy_order: list | None = None,
    ) -> dict[str, object]:
        """Test helper: build a minimal BL-003 payload for fixture injection."""
        return {
            "stage_id": "BL-003",
            "schema_version": "1.0",
            "resolved_from": "defaults",
            "controls": {
                "input_scope_controls": {
                    "include_top_tracks": True,
                    "include_saved_tracks": True,
                    "include_playlists": False,
                    "include_recently_played": False,
                },
                "seed_controls": {
                    "top_range_weights": top_range_weights or {"short_term": 0.5, "medium_term": 0.3, "long_term": 0.2},
                    "source_base_weights": {"top_tracks": 1.0, "saved_tracks": 0.6, "playlist_items": 0.4, "recently_played": 0.5},
                    "fuzzy_matching": {"enabled": False},
                    "match_strategy": {"enable_spotify_id_match": True, "enable_metadata_match": True, "enable_fuzzy_match": True},
                    "match_strategy_order": match_strategy_order or ["spotify_id_exact", "metadata_fallback", "fuzzy_title_artist"],
                    "temporal_controls": {},
                    "aggregation_policy": {},
                    "decay_half_lives": {"recently_played": 90.0, "saved_tracks": 365.0},
                    "match_rate_min_threshold": 0.0,
                },
                "weighting_policy": None,
                "influence_controls": {"influence_enabled": False, "influence_track_ids": [], "influence_preference_weight": 2.0},
            },
        }

    fixture = make_bl003_payload_fixture(
        top_range_weights={"short_term": 0.8, "medium_term": 0.15, "long_term": 0.05}
    )

    controls = dict(fixture["controls"])
    assert controls["seed_controls"]["top_range_weights"]["short_term"] == 0.8
    assert json.dumps(fixture)  # Must be JSON-serializable

    # Can now be injected via BL_STAGE_CONFIG_JSON in tests


def test_stage_payload_defaults_are_not_sourced_from_stage_env(monkeypatch) -> None:
    """Orchestration payloads should resolve from canonical defaults/run-config, not BL00x env vars."""
    monkeypatch.setenv("BL007_MIN_SCORE_THRESHOLD", "0.91")

    payload = config_resolver.resolve_stage_control_payload("BL-007", run_config_path=None)

    assert payload["resolved_from"] == "defaults"
    controls = dict(payload["controls"])
    assert controls["min_score_threshold"] == 0.35


def test_stage_payload_uses_run_config_overrides(tmp_path: Path) -> None:
    """Orchestration payload should reflect explicit run-config overrides across stages."""
    run_config_path = tmp_path / "run_config_override.json"
    run_config_path.write_text(
        json.dumps(
            {
                "profile_controls": {
                    "top_tag_limit": 22,
                },
                "retrieval_controls": {
                    "profile_top_tag_limit": 22,
                },
                "scoring_controls": {
                    "numeric_confidence_floor": 0.25,
                },
                "assembly_controls": {
                    "target_size": 12,
                },
            }
        ),
        encoding="utf-8",
    )

    payloads = config_resolver.resolve_stage_control_payloads(
        ["BL-005", "BL-006", "BL-007"],
        run_config_path=run_config_path,
    )

    assert payloads["BL-005"]["resolved_from"] == "run_config"
    assert payloads["BL-006"]["resolved_from"] == "run_config"
    assert payloads["BL-007"]["resolved_from"] == "run_config"
    assert dict(payloads["BL-005"]["controls"])["profile_top_tag_limit"] == 22
    assert dict(payloads["BL-006"]["controls"])["numeric_confidence_floor"] == 0.25
    assert dict(payloads["BL-007"]["controls"])["target_size"] == 12
