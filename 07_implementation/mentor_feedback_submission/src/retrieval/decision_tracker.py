"""Decision and diagnostics tracker for BL-005 filtering.

I keep the counters and histograms here so the evaluator can stay focused on the
actual keep/reject logic.
"""

from typing import Any


class DecisionTracker:
    """Collect filtering decisions and summarize the scoring diagnostics they produce."""

    def __init__(self, numeric_feature_specs: dict[str, Any]) -> None:
        """Set up the counters and histograms BL-005 needs for its summary output."""
        self.decisions: list[dict[str, object]] = []
        self.kept_rows: list[dict[str, str]] = []

        self.decision_counts = {
            "seed_excluded": 0,
            "kept_candidates": 0,
            "rejected_threshold": 0,
        }
        self.decision_path_counts: dict[str, int] = {}

        self.semantic_rule_hits = {
            "lead_genre_match": 0,
            "genre_overlap": 0,
            "tag_overlap": 0,
        }
        self.numeric_rule_hits = {key: 0 for key in numeric_feature_specs}

        self.semantic_score_distribution: dict[str, int] = {}
        self.numeric_pass_distribution = {
            str(score): 0 for score in range(len(numeric_feature_specs) + 1)
        }
        self.numeric_support_score_distribution: dict[str, int] = {}
        self.numeric_support_score_weighted_distribution: dict[str, int] = {}
        self.numeric_support_score_weighted_absolute_distribution: dict[str, int] = {}
        self.numeric_support_score_selected_distribution: dict[str, int] = {}
        self.effective_semantic_min_distribution: dict[str, int] = {}
        self.effective_numeric_support_min_score_distribution: dict[str, int] = {}

    def record_decision(
        self,
        track_id: str,
        is_seed_track: bool,
        kept: bool,
        decision_path: str,
        decision_record: dict[str, object],
        candidate_row: dict[str, str] | None = None,
    ) -> None:
        """Record one candidate decision and update the keep/reject counters."""
        self.decisions.append(decision_record)

        if is_seed_track:
            self.decision_counts["seed_excluded"] += 1
        elif kept:
            self.decision_counts["kept_candidates"] += 1
            if candidate_row:
                self.kept_rows.append(candidate_row)
        else:
            self.decision_counts["rejected_threshold"] += 1

        self.decision_path_counts[decision_path] = (
            self.decision_path_counts.get(decision_path, 0) + 1
        )

    def record_semantic_scores(
        self,
        semantic_score: float,
        lead_genre_match: bool,
        genre_overlap: int,
        tag_overlap: int,
    ) -> None:
        """Record the semantic side of one candidate evaluation."""
        score_str = f"{semantic_score:.2f}"
        self.semantic_score_distribution[score_str] = (
            self.semantic_score_distribution.get(score_str, 0) + 1
        )

        if lead_genre_match:
            self.semantic_rule_hits["lead_genre_match"] += 1
        if genre_overlap > 0:
            self.semantic_rule_hits["genre_overlap"] += 1
        if tag_overlap > 0:
            self.semantic_rule_hits["tag_overlap"] += 1

    def record_numeric_scores(
        self,
        numeric_pass_count: int,
        numeric_support_score: float,
        numeric_rule_hits_this_candidate: dict[str, bool],
        *,
        numeric_support_score_weighted: float,
        numeric_support_score_weighted_absolute: float,
        numeric_support_score_selected: float,
        effective_semantic_min_keep_score: float,
        effective_numeric_support_min_score: float,
    ) -> None:
        """Record the numeric side of one candidate evaluation."""
        count_str = str(numeric_pass_count)
        self.numeric_pass_distribution[count_str] = (
            self.numeric_pass_distribution.get(count_str, 0) + 1
        )
        support_str = f"{numeric_support_score:.2f}"
        self.numeric_support_score_distribution[support_str] = (
            self.numeric_support_score_distribution.get(support_str, 0) + 1
        )
        weighted_support_str = f"{numeric_support_score_weighted:.2f}"
        self.numeric_support_score_weighted_distribution[weighted_support_str] = (
            self.numeric_support_score_weighted_distribution.get(weighted_support_str, 0) + 1
        )
        weighted_absolute_support_str = f"{numeric_support_score_weighted_absolute:.2f}"
        self.numeric_support_score_weighted_absolute_distribution[weighted_absolute_support_str] = (
            self.numeric_support_score_weighted_absolute_distribution.get(weighted_absolute_support_str, 0) + 1
        )
        selected_support_str = f"{numeric_support_score_selected:.2f}"
        self.numeric_support_score_selected_distribution[selected_support_str] = (
            self.numeric_support_score_selected_distribution.get(selected_support_str, 0) + 1
        )
        effective_semantic_min_str = f"{effective_semantic_min_keep_score:.2f}"
        self.effective_semantic_min_distribution[effective_semantic_min_str] = (
            self.effective_semantic_min_distribution.get(effective_semantic_min_str, 0) + 1
        )
        effective_numeric_min_str = f"{effective_numeric_support_min_score:.2f}"
        self.effective_numeric_support_min_score_distribution[effective_numeric_min_str] = (
            self.effective_numeric_support_min_score_distribution.get(effective_numeric_min_str, 0) + 1
        )

        for feature_name, passed in numeric_rule_hits_this_candidate.items():
            if passed:
                self.numeric_rule_hits[feature_name] = (
                    self.numeric_rule_hits.get(feature_name, 0) + 1
                )

    def get_summary(self) -> dict[str, object]:
        """Return the aggregated BL-005 diagnostics summary."""
        return {
            "decision_counts": self.decision_counts,
            "decision_path_counts": self.decision_path_counts,
            "semantic_rule_hits": self.semantic_rule_hits,
            "numeric_rule_hits": self.numeric_rule_hits,
            "semantic_score_distribution": self.semantic_score_distribution,
            "numeric_pass_distribution": self.numeric_pass_distribution,
            "numeric_support_score_distribution": self.numeric_support_score_distribution,
            "numeric_support_score_weighted_distribution": self.numeric_support_score_weighted_distribution,
            "numeric_support_score_weighted_absolute_distribution": self.numeric_support_score_weighted_absolute_distribution,
            "numeric_support_score_selected_distribution": self.numeric_support_score_selected_distribution,
            "effective_semantic_min_distribution": self.effective_semantic_min_distribution,
            "effective_numeric_support_min_score_distribution": self.effective_numeric_support_min_score_distribution,
        }
