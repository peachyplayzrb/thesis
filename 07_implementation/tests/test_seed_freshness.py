"""Tests for BL-013 seed freshness validation against BL-003 contracts."""

from __future__ import annotations

# pyright: reportMissingImports=false

import json
from pathlib import Path

from orchestration import seed_freshness
from shared_utils.hashing import canonical_json_hash


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_effective_config(path: Path) -> None:
    _write_json(
        path,
        {
            "effective_config": {
                "input_scope": {
                    "include_top_tracks": True,
                    "include_saved_tracks": True,
                    "include_playlists": False,
                    "include_recently_played": True,
                },
                "influence_tracks": {
                    "enabled": True,
                    "track_ids": ["sp_123", "sp_456"],
                    "preference_weight": 1.5,
                },
                "seed_controls": {
                    "match_rate_min_threshold": 0.6,
                    "top_range_weights": {
                        "short_term": 0.5,
                        "medium_term": 0.3,
                        "long_term": 0.2,
                    },
                    "source_base_weights": {
                        "top_tracks": 1.0,
                        "saved_tracks": 0.6,
                        "playlist_items": 0.4,
                        "recently_played": 0.5,
                    },
                    "decay_half_lives": {
                        "recently_played": 90.0,
                        "saved_tracks": 365.0,
                    },
                    "fuzzy_matching": {
                        "enabled": True,
                        "artist_threshold": 0.91,
                        "title_threshold": 0.92,
                        "combined_threshold": 0.93,
                        "max_duration_delta_ms": 4000,
                        "max_artist_candidates": 8,
                    },
                    "weighting_policy": {
                        "top_tracks": {
                            "min_rank_floor": 0.08,
                            "scale_multiplier": 90.0,
                            "default_time_range_weight": 0.25,
                        },
                        "playlist_items": {
                            "min_position_floor": 0.06,
                            "scale_multiplier": 18.0,
                        },
                    },
                },
            }
        },
    )


def test_validate_seed_freshness_accepts_matching_full_contract(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(seed_freshness, "BL003_SUMMARY_PATH", Path("bl003_summary.json"))

    run_config_path = tmp_path / "run_config.json"
    run_config_path.write_text("{}", encoding="utf-8")
    effective_path = tmp_path / "run_effective_config.json"
    _write_effective_config(effective_path)

    expected = seed_freshness._normalized_contract_from_effective(effective_path)
    _write_json(
        tmp_path / "bl003_summary.json",
        {
            "inputs": {
                "config_source": "run_config",
                "run_config_path": str(run_config_path.resolve()),
                "seed_contract": {
                    **dict(expected["seed_contract"]),
                    "contract_hash": str(expected["seed_contract_hash"]),
                },
                "structural_contract": {
                    **dict(expected["structural_contract"]),
                    "contract_hash": str(expected["structural_contract_hash"]),
                },
            }
        },
    )

    is_fresh, reason = seed_freshness.validate_bl003_seed_freshness(
        root=tmp_path,
        run_config_path=run_config_path,
        run_effective_config_path=effective_path,
    )

    assert is_fresh is True
    assert reason == "ok"


def test_validate_seed_freshness_rejects_seed_contract_mismatch(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(seed_freshness, "BL003_SUMMARY_PATH", Path("bl003_summary.json"))

    run_config_path = tmp_path / "run_config.json"
    run_config_path.write_text("{}", encoding="utf-8")
    effective_path = tmp_path / "run_effective_config.json"
    _write_effective_config(effective_path)

    expected = seed_freshness._normalized_contract_from_effective(effective_path)
    seed_contract = dict(expected["seed_contract"])
    top_range_weights = dict(seed_contract["top_range_weights"])
    top_range_weights["short_term"] = 0.75
    seed_contract["top_range_weights"] = top_range_weights

    _write_json(
        tmp_path / "bl003_summary.json",
        {
            "inputs": {
                "config_source": "run_config",
                "run_config_path": str(run_config_path.resolve()),
                "seed_contract": {
                    **seed_contract,
                    "contract_hash": canonical_json_hash(seed_contract, uppercase=True),
                },
                "structural_contract": {
                    **dict(expected["structural_contract"]),
                    "contract_hash": str(expected["structural_contract_hash"]),
                },
            }
        },
    )

    is_fresh, reason = seed_freshness.validate_bl003_seed_freshness(
        root=tmp_path,
        run_config_path=run_config_path,
        run_effective_config_path=effective_path,
    )

    assert is_fresh is False
    assert "seed contract" in reason


def test_validate_seed_freshness_rejects_structural_contract_schema_mismatch(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(seed_freshness, "BL003_SUMMARY_PATH", Path("bl003_summary.json"))

    run_config_path = tmp_path / "run_config.json"
    run_config_path.write_text("{}", encoding="utf-8")
    effective_path = tmp_path / "run_effective_config.json"
    _write_effective_config(effective_path)

    expected = seed_freshness._normalized_contract_from_effective(effective_path)
    structural_contract = dict(expected["structural_contract"])
    structural_contract["structural_contract_schema_version"] = "bl003-structural-contract-v0"

    _write_json(
        tmp_path / "bl003_summary.json",
        {
            "inputs": {
                "config_source": "run_config",
                "run_config_path": str(run_config_path.resolve()),
                "seed_contract": {
                    **dict(expected["seed_contract"]),
                    "contract_hash": str(expected["seed_contract_hash"]),
                },
                "structural_contract": {
                    **structural_contract,
                    "contract_hash": canonical_json_hash(structural_contract, uppercase=True),
                },
            }
        },
    )

    is_fresh, reason = seed_freshness.validate_bl003_seed_freshness(
        root=tmp_path,
        run_config_path=run_config_path,
        run_effective_config_path=effective_path,
    )

    assert is_fresh is False
    assert "structural contract schema version" in reason


def test_validate_seed_freshness_rejects_legacy_summary_without_seed_contract(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(seed_freshness, "BL003_SUMMARY_PATH", Path("bl003_summary.json"))

    run_config_path = tmp_path / "run_config.json"
    run_config_path.write_text("{}", encoding="utf-8")
    effective_path = tmp_path / "run_effective_config.json"
    _write_effective_config(effective_path)

    expected = seed_freshness._normalized_contract_from_effective(effective_path)
    expected_seed = dict(expected["seed_contract"])

    _write_json(
        tmp_path / "bl003_summary.json",
        {
            "inputs": {
                "config_source": "run_config",
                "run_config_path": str(run_config_path.resolve()),
                "input_scope": dict(expected_seed["input_scope"]),
                "influence_tracks": dict(expected_seed["influence_tracks"]),
            }
        },
    )

    is_fresh, reason = seed_freshness.validate_bl003_seed_freshness(
        root=tmp_path,
        run_config_path=run_config_path,
        run_effective_config_path=effective_path,
    )

    assert is_fresh is False
    assert "seed contract missing" in reason


def test_validate_seed_freshness_fails_fast_on_malformed_seed_contract_type(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(seed_freshness, "BL003_SUMMARY_PATH", Path("bl003_summary.json"))

    run_config_path = tmp_path / "run_config.json"
    run_config_path.write_text("{}", encoding="utf-8")
    effective_path = tmp_path / "run_effective_config.json"
    _write_effective_config(effective_path)

    _write_json(
        tmp_path / "bl003_summary.json",
        {
            "inputs": {
                "config_source": "run_config",
                "run_config_path": str(run_config_path.resolve()),
                "seed_contract": "not-an-object",
            }
        },
    )

    is_fresh, reason = seed_freshness.validate_bl003_seed_freshness(
        root=tmp_path,
        run_config_path=run_config_path,
        run_effective_config_path=effective_path,
    )

    assert is_fresh is False
    assert "seed_contract must be an object" in reason


def test_validate_seed_freshness_fails_fast_on_malformed_structural_contract_type(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(seed_freshness, "BL003_SUMMARY_PATH", Path("bl003_summary.json"))

    run_config_path = tmp_path / "run_config.json"
    run_config_path.write_text("{}", encoding="utf-8")
    effective_path = tmp_path / "run_effective_config.json"
    _write_effective_config(effective_path)

    _write_json(
        tmp_path / "bl003_summary.json",
        {
            "inputs": {
                "config_source": "run_config",
                "run_config_path": str(run_config_path.resolve()),
                "seed_contract": {},
                "structural_contract": ["bad-shape"],
            }
        },
    )

    is_fresh, reason = seed_freshness.validate_bl003_seed_freshness(
        root=tmp_path,
        run_config_path=run_config_path,
        run_effective_config_path=effective_path,
    )

    assert is_fresh is False
    assert "structural_contract must be an object" in reason
