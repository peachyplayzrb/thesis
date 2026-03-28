"""Tests for controllability.weights."""

from controllability.weights import (
    candidate_labels,
    candidate_weight_pairs,
    normalize_component_weight_keys,
    normalize_weight_map,
    normalized_weights_with_override,
    numeric_similarity,
    parse_labels,
    parse_weighted_list,
    sorted_weight_map,
    weighted_overlap,
)


class TestParseHelpers:
    def test_parse_weighted_list_valid_json(self):
        raw = '[{"genre":"rock","score":0.8},{"genre":"pop","score":0.2}]'
        assert parse_weighted_list(raw, "genre", "score") == [("rock", 0.8), ("pop", 0.2)]

    def test_parse_weighted_list_invalid_json_returns_empty(self):
        assert parse_weighted_list("not-json", "genre", "score") == []

    def test_parse_labels_returns_only_present_labels(self):
        raw = '[{"tag":"energetic"},{"tag":"indie"}]'
        assert parse_labels(raw, "tag") == ["energetic", "indie"]


class TestCandidateLabelSelection:
    def test_candidate_labels_prefers_legacy_genres_json(self):
        row = {
            "top_genres_json": '[{"genre":"alt"}]',
            "genres": "pop,rock",
        }
        assert candidate_labels(row, "genres") == ["alt"]

    def test_candidate_labels_falls_back_to_csv_tags(self):
        row = {
            "top_tags_json": "",
            "tags": "mellow, focus",
        }
        assert candidate_labels(row, "tags") == ["mellow", "focus"]

    def test_candidate_weight_pairs_fallback_default_weight(self):
        row = {
            "top_tags_json": "",
            "tags": "dance,night",
        }
        assert candidate_weight_pairs(row, "tags") == [("dance", 1.0), ("night", 1.0)]


class TestWeightMath:
    def test_sorted_weight_map_order_and_rounding(self):
        weight_map = {"b": 0.1234567, "a": 0.1234567, "c": 0.1}
        result = sorted_weight_map(weight_map, limit=2)
        assert result == [{"label": "a", "weight": 0.123457}, {"label": "b", "weight": 0.123457}]

    def test_numeric_similarity_bounds(self):
        assert numeric_similarity(None, center=0.5, threshold=0.2) == 0.0
        assert numeric_similarity(0.5, center=0.5, threshold=0.2) == 1.0
        assert numeric_similarity(0.9, center=0.5, threshold=0.2) == 0.0

    def test_weighted_overlap(self):
        overlap, labels = weighted_overlap(["rock", "jazz"], {"rock": 0.6, "pop": 0.4}, 1.0)
        assert overlap == 0.6
        assert labels == ["rock"]

    def test_normalize_weight_map(self):
        items = [{"label": "rock", "weight": 2.0}, {"label": "pop", "weight": 1.0}]
        weight_map, total = normalize_weight_map(items, top_k=2)
        assert weight_map == {"rock": 2.0, "pop": 1.0}
        assert total == 3.0

    def test_normalized_weights_with_override_sums_to_one(self):
        weights = normalized_weights_with_override({"a": 0.6, "b": 0.4}, "b", 1.0)
        assert round(sum(weights.values()), 6) == 1.0
        assert weights["b"] > weights["a"]

    def test_normalize_component_weight_keys_collapses_score_suffix(self):
        normalized = normalize_component_weight_keys({"tempo_score": 0.4, "tempo": 0.6, "energy_score": 1.0})
        assert set(normalized.keys()) == {"tempo", "energy"}
        assert round(sum(normalized.values()), 6) == 1.0
