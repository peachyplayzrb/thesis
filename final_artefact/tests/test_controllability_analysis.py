"""Tests for controllability.analysis."""

from controllability.analysis import (
    build_baseline_comparison,
    build_rank_shift_summary,
    compare_to_baseline,
    evaluate_results_status,
)


def _result(
    *,
    scenario_id: str,
    top10: list[str],
    playlist: list[str],
    pool_size: int,
    rank_map: dict[str, int],
    mean_component: dict[str, float],
    lead_genres: list[str],
    profile_hash: str,
) -> dict[str, object]:
    return {
        "scenario_id": scenario_id,
        "effective_config": {"scoring": {"weight_override_component": "valence"}},
        "stable_hashes": {
            "profile_semantic_hash": profile_hash,
        },
        "metrics": {
            "top10_track_ids": top10,
            "playlist_track_ids": playlist,
            "candidate_pool_size": pool_size,
            "playlist_length": len(playlist),
            "rank_map": rank_map,
            "mean_component_contributions": mean_component,
            "dominant_lead_genres": lead_genres,
        },
    }


class TestBuildRankShiftSummary:
    def test_empty_when_no_common_candidates(self):
        summary = build_rank_shift_summary({"a": 1}, {"b": 1})
        assert summary["common_candidate_count"] == 0
        assert summary["mean_abs_rank_delta"] == 0.0

    def test_rank_shift_stats_computed(self):
        summary = build_rank_shift_summary({"a": 1, "b": 2}, {"a": 2, "b": 1})
        assert summary["common_candidate_count"] == 2
        assert summary["max_rank_improvement"] == 1
        assert summary["max_rank_drop"] == -1


class TestComparisons:
    def test_build_baseline_comparison_identity(self):
        baseline = _result(
            scenario_id="baseline",
            top10=["a", "b"],
            playlist=["a"],
            pool_size=5,
            rank_map={"a": 1, "b": 2},
            mean_component={"valence": 0.2},
            lead_genres=["indie"],
            profile_hash="h1",
        )
        comp = build_baseline_comparison(baseline)
        assert comp["observable_shift"] is False
        assert comp["expected_direction_met"] is True
        assert comp["top10_overlap_ratio"] == 1.0

    def test_compare_to_baseline_detects_shift(self):
        baseline = _result(
            scenario_id="baseline",
            top10=["a", "b"],
            playlist=["a", "b"],
            pool_size=10,
            rank_map={"a": 1, "b": 2},
            mean_component={"valence": 0.1},
            lead_genres=["indie"],
            profile_hash="h1",
        )
        variant = _result(
            scenario_id="valence_weight_up",
            top10=["b", "a"],
            playlist=["b", "a"],
            pool_size=11,
            rank_map={"a": 2, "b": 1},
            mean_component={"valence": 0.3},
            lead_genres=["alt"],
            profile_hash="h2",
        )
        comp = compare_to_baseline(baseline, variant)
        assert comp["observable_shift"] is True
        assert comp["candidate_pool_size_delta"] == 1
        assert comp["top10_overlap_count"] == 2
        assert comp["expected_direction_met"] is True


class TestEvaluateResultsStatus:
    def test_status_pass_when_all_conditions_true(self):
        records = [
            {
                "scenario_id": "baseline",
                "repeat_consistent": True,
                "comparison_to_baseline": {"observable_shift": False, "expected_direction_met": True},
            },
            {
                "scenario_id": "valence_weight_up",
                "repeat_consistent": True,
                "comparison_to_baseline": {"observable_shift": True, "expected_direction_met": True},
            },
        ]
        status = evaluate_results_status(records)
        assert status["status"] == "pass"

    def test_status_bounded_risk_when_any_condition_fails(self):
        records = [
            {
                "scenario_id": "baseline",
                "repeat_consistent": True,
                "comparison_to_baseline": {"observable_shift": False, "expected_direction_met": True},
            },
            {
                "scenario_id": "stricter_thresholds",
                "repeat_consistent": False,
                "comparison_to_baseline": {"observable_shift": True, "expected_direction_met": True},
            },
        ]
        status = evaluate_results_status(records)
        assert status["status"] == "bounded-risk"
