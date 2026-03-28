"""Tests for retrieval.profile_builder."""

from retrieval.profile_builder import build_active_numeric_specs, build_profile_label_set


def test_build_profile_label_set_normalizes_and_limits() -> None:
    profile = {
        "semantic_profile": {
            "top_tags": [
                {"label": " Rock "},
                {"label": "POP"},
                {"label": "jazz"},
            ]
        }
    }
    labels = build_profile_label_set(profile, "top_tags", limit=2)
    assert labels == {"rock", "pop"}


def test_build_profile_label_set_handles_missing_shape() -> None:
    assert build_profile_label_set({}, "top_tags", limit=5) == set()
    assert build_profile_label_set({"semantic_profile": {}}, "top_tags", limit=5) == set()


def test_build_active_numeric_specs_resolves_duration_fallback() -> None:
    profile = {
        "numeric_feature_profile": {
            "duration_ms": 180000.0,
            "tempo": 120.0,
        }
    }
    effective = {
        "duration_ms": {
            "candidate_column": "duration_ms",
            "threshold": 45000.0,
            "circular": False,
        },
        "tempo": {
            "candidate_column": "tempo",
            "threshold": 20.0,
            "circular": False,
        },
        "energy": {
            "candidate_column": "energy",
            "threshold": 0.2,
            "circular": False,
        },
    }
    candidate_columns = {"duration", "tempo"}

    active = build_active_numeric_specs(profile, effective, candidate_columns)

    assert set(active.keys()) == {"duration_ms", "tempo"}
    assert active["duration_ms"]["candidate_column"] == "duration"
    assert active["tempo"]["candidate_column"] == "tempo"
