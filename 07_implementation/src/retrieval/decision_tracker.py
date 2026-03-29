"""
Decision tracking and diagnostics for BL-005 candidate filtering.

Accumulates metrics about decisions, semantic/numeric scoring,
and generates diagnostic reports.
"""

from typing import Any


class DecisionTracker:
    """Tracks filtering decisions and generates diagnostic reports."""

    def __init__(self, numeric_feature_specs: dict[str, Any]) -> None:
        """
        Initialize decision tracker.

        Args:
            numeric_feature_specs: Dict of numeric feature specifications
                (used to initialize numeric_rule_hits and distributions)
        """
        # Decision records
        self.decisions: list[dict[str, object]] = []
        self.kept_rows: list[dict[str, str]] = []

        # Aggregated counts
        self.decision_counts = {
            "seed_excluded": 0,
            "kept_candidates": 0,
            "rejected_threshold": 0,
        }
        self.decision_path_counts: dict[str, int] = {}

        # Rule hit tracking
        self.semantic_rule_hits = {
            "lead_genre_match": 0,
            "genre_overlap": 0,
            "tag_overlap": 0,
        }
        self.numeric_rule_hits = {key: 0 for key in numeric_feature_specs}

        # Distribution tracking
        self.semantic_score_distribution: dict[str, int] = {}
        self.numeric_pass_distribution = {
            str(score): 0 for score in range(len(numeric_feature_specs) + 1)
        }
        self.numeric_support_score_distribution: dict[str, int] = {}

    def record_decision(
        self,
        track_id: str,
        is_seed_track: bool,
        kept: bool,
        decision_path: str,
        decision_record: dict[str, object],
        candidate_row: dict[str, str] | None = None,
    ) -> None:
        """
        Record a filtering decision for a candidate.

        Args:
            track_id: Candidate track ID
            is_seed_track: Whether track is a seed track
            kept: Whether decision was to keep the candidate
            decision_path: Decision path identifier (e.g., "keep_strong_semantic")
            decision_record: Full decision record with all details
            candidate_row: Full candidate row data (included if kept)
        """
        self.decisions.append(decision_record)

        # Update counts
        if is_seed_track:
            self.decision_counts["seed_excluded"] += 1
        elif kept:
            self.decision_counts["kept_candidates"] += 1
            if candidate_row:
                self.kept_rows.append(candidate_row)
        else:
            self.decision_counts["rejected_threshold"] += 1

        # Update decision path histogram
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
        """
        Record semantic scoring results for a candidate.

        Args:
            semantic_score: Total semantic score (0-3)
            lead_genre_match: Whether lead genre matches
            genre_overlap: Number of genres matching
            tag_overlap: Number of tags matching
        """
        # Update distribution
        score_str = f"{semantic_score:.2f}"
        self.semantic_score_distribution[score_str] = (
            self.semantic_score_distribution.get(score_str, 0) + 1
        )

        # Update rule hits
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
    ) -> None:
        """
        Record numeric scoring results for a candidate.

        Args:
            numeric_pass_count: Number of numeric features passing
            numeric_rule_hits_this_candidate: Dict of numeric features that passed
        """
        # Update distribution
        count_str = str(numeric_pass_count)
        self.numeric_pass_distribution[count_str] = (
            self.numeric_pass_distribution.get(count_str, 0) + 1
        )
        support_str = f"{numeric_support_score:.2f}"
        self.numeric_support_score_distribution[support_str] = (
            self.numeric_support_score_distribution.get(support_str, 0) + 1
        )

        # Update rule hits
        for feature_name, passed in numeric_rule_hits_this_candidate.items():
            if passed:
                self.numeric_rule_hits[feature_name] = (
                    self.numeric_rule_hits.get(feature_name, 0) + 1
                )

    def get_summary(self) -> dict[str, object]:
        """
        Get a summary of all tracked metrics.

        Returns:
            Dict with decision_counts, decision_path_counts, rule_hits, distributions
        """
        return {
            "decision_counts": self.decision_counts,
            "decision_path_counts": self.decision_path_counts,
            "semantic_rule_hits": self.semantic_rule_hits,
            "numeric_rule_hits": self.numeric_rule_hits,
            "semantic_score_distribution": self.semantic_score_distribution,
            "numeric_pass_distribution": self.numeric_pass_distribution,
            "numeric_support_score_distribution": self.numeric_support_score_distribution,
        }
