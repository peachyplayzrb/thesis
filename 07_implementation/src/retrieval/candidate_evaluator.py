"""Candidate evaluation loop for BL-005 retrieval."""

from __future__ import annotations

from scoring.scoring_engine import numeric_similarity, weighted_overlap
from shared_utils.genre_utils import lead_genre_token_similarity
from shared_utils.parsing import parse_csv_labels

from retrieval.candidate_parser import (
    candidate_language_code,
    candidate_numeric_value,
    candidate_release_year,
    resolve_lead_genre,
)
from retrieval.decision_tracker import DecisionTracker
from retrieval.filtering_logic import decision_reason, keep_decision
from retrieval.models import RetrievalContext, RetrievalEvaluationResult, context_from_mapping


def circular_distance_12(a: float, b: float) -> float:
    """Return shortest non-negative distance between two values on a 12-step circle."""
    normalized_a = a % 12.0
    normalized_b = b % 12.0
    raw_diff = abs(normalized_a - normalized_b)
    return min(raw_diff, 12.0 - raw_diff)


def weighted_lead_genre_similarity(candidate_label: str, profile_weights: dict[str, float]) -> float:
    if not candidate_label or not profile_weights:
        return 0.0
    score = sum(
        lead_genre_token_similarity(candidate_label, profile_label) * weight
        for profile_label, weight in profile_weights.items()
    )
    return round(max(0.0, min(score, 1.0)), 6)


def evaluate_bl005_candidates(
    *,
    candidate_rows: list[dict[str, str]],
    runtime_context: RetrievalContext | dict[str, object],
) -> tuple[DecisionTracker, list[dict[str, object]], list[dict[str, str]], dict[str, object]]:
    context = (
        runtime_context
        if isinstance(runtime_context, RetrievalContext)
        else context_from_mapping(runtime_context)
    )

    active_numeric_specs = context.active_numeric_specs
    seed_track_ids = context.seed_track_ids
    top_lead_genres = context.top_lead_genres
    top_tags = context.top_tags
    top_genres = context.top_genres
    numeric_centers = context.numeric_centers
    numeric_features_enabled = context.numeric_features_enabled
    semantic_strong_keep_score = context.semantic_strong_keep_score
    semantic_min_keep_score = context.semantic_min_keep_score
    numeric_support_min_pass = context.numeric_support_min_pass
    numeric_support_min_score = context.numeric_support_min_score
    language_filter_enabled = context.language_filter_enabled
    language_filter_codes = set(context.language_filter_codes)
    recency_min_release_year = context.recency_min_release_year
    lead_genre_partial_match_threshold = context.lead_genre_partial_match_threshold
    use_weighted_semantics = context.use_weighted_semantics
    use_continuous_numeric = context.use_continuous_numeric
    lead_genre_weights = context.lead_genre_weights
    tag_weights = context.tag_weights
    genre_weights = context.genre_weights
    feature_confidence_by_name = context.feature_confidence_by_name
    profile_numeric_confidence_factor = context.profile_numeric_confidence_factor
    semantic_overlap_damping = context.semantic_overlap_damping
    effective_semantic_strong_keep_score = context.effective_semantic_strong_keep_score
    effective_semantic_min_keep_score = context.effective_semantic_min_keep_score
    effective_numeric_support_min_pass = context.effective_numeric_support_min_pass
    effective_numeric_support_min_score = context.effective_numeric_support_min_score
    numeric_support_score_mode = str(context.numeric_support_score_mode or "weighted_absolute").strip().lower()

    tracker = DecisionTracker(active_numeric_specs)

    for row in candidate_rows:
        track_id = str(row["track_id"])
        is_seed_track = track_id in seed_track_ids

        candidate_tags = parse_csv_labels(str(row.get("tags", "")))
        candidate_genres = parse_csv_labels(str(row.get("genres", "")))
        lead_genre = resolve_lead_genre(candidate_genres, candidate_tags)
        language_code = candidate_language_code(row)  # type: ignore[arg-type]
        release_year = candidate_release_year(row)  # type: ignore[arg-type]

        language_match: bool | None = None
        if language_filter_enabled:
            language_match = bool(language_code and language_code in language_filter_codes)

        recency_pass: bool | None = None
        if recency_min_release_year is not None:
            recency_pass = bool(release_year is not None and release_year >= int(recency_min_release_year))

        genre_overlap = len(top_genres.intersection(candidate_genres))
        tag_overlap = len(top_tags.intersection(candidate_tags))

        if use_weighted_semantics:
            lead_genre_match_score = weighted_lead_genre_similarity(lead_genre, lead_genre_weights)
            genre_overlap_fraction = weighted_overlap(candidate_genres, genre_weights)
            tag_overlap_fraction = weighted_overlap(candidate_tags, tag_weights)
        else:
            lead_genre_match_score = 0.0
            if lead_genre and top_lead_genres:
                lead_genre_match_score = max(
                    lead_genre_token_similarity(lead_genre, profile_lead_genre)
                    for profile_lead_genre in top_lead_genres
                )
            genre_overlap_fraction = min(1.0, genre_overlap / max(1, len(top_genres)))
            tag_overlap_fraction = min(1.0, tag_overlap / max(1, len(top_tags)))

        genre_overlap_fraction = round(genre_overlap_fraction * semantic_overlap_damping, 6)
        tag_overlap_fraction = round(tag_overlap_fraction * semantic_overlap_damping, 6)

        lead_genre_match = lead_genre_match_score >= lead_genre_partial_match_threshold
        semantic_score = lead_genre_match_score + genre_overlap_fraction + tag_overlap_fraction

        tracker.record_semantic_scores(semantic_score, lead_genre_match, genre_overlap, tag_overlap)

        numeric_pass_count = 0
        numeric_support_score = 0.0
        weighted_support_numerator = 0.0
        weighted_support_denominator = 0.0
        numeric_support_score_weighted = 0.0
        numeric_support_score_weighted_absolute = 0.0
        numeric_distances: dict[str, float | None] = {}
        numeric_similarities: dict[str, float] = {}
        numeric_rule_hits_this_candidate: dict[str, bool] = {}

        for profile_column, spec in active_numeric_specs.items():
            value = candidate_numeric_value(
                row,
                profile_column,
                spec.candidate_column,
            )
            passed = False

            if value is not None:
                center = numeric_centers.get(profile_column)
                if center is not None:
                    if spec.circular:
                        distance = circular_distance_12(value, center)
                    else:
                        distance = abs(value - center)
                    similarity = numeric_similarity(value, center, spec.threshold, spec.circular)
                    numeric_distances[profile_column] = round(distance, 6)
                    numeric_similarities[profile_column] = similarity
                    numeric_support_score += similarity
                    confidence_weight = max(
                        0.0,
                        min(1.0, float(feature_confidence_by_name.get(profile_column, 1.0))),
                    )
                    weighted_support_numerator += similarity * confidence_weight
                    weighted_support_denominator += confidence_weight
                    if distance <= spec.threshold:
                        numeric_pass_count += 1
                        passed = True
                else:
                    numeric_distances[profile_column] = None
                    numeric_similarities[profile_column] = 0.0
            else:
                numeric_distances[profile_column] = None
                numeric_similarities[profile_column] = 0.0

            numeric_rule_hits_this_candidate[profile_column] = passed

        numeric_support_score = round(numeric_support_score, 6)
        if weighted_support_denominator > 0:
            weighted_average_similarity = weighted_support_numerator / weighted_support_denominator
            numeric_support_score_weighted = weighted_average_similarity * float(len(active_numeric_specs))
        numeric_support_score_weighted = round(numeric_support_score_weighted, 6)
        numeric_support_score_weighted_absolute = round(
            numeric_support_score_weighted * max(0.0, min(1.0, profile_numeric_confidence_factor)),
            6,
        )
        if numeric_support_score_mode == "raw":
            numeric_support_score_selected = numeric_support_score
        elif numeric_support_score_mode == "weighted":
            numeric_support_score_selected = numeric_support_score_weighted
        else:
            numeric_support_score_selected = numeric_support_score_weighted_absolute

        tracker.record_numeric_scores(
            numeric_pass_count,
            numeric_support_score,
            numeric_rule_hits_this_candidate,
            numeric_support_score_weighted=numeric_support_score_weighted,
            numeric_support_score_weighted_absolute=numeric_support_score_weighted_absolute,
            numeric_support_score_selected=numeric_support_score_selected,
            effective_semantic_min_keep_score=effective_semantic_min_keep_score,
            effective_numeric_support_min_score=effective_numeric_support_min_score,
        )

        kept, decision_path = keep_decision(
            is_seed_track,
            semantic_score,
            numeric_pass_count,
            numeric_features_enabled,
            effective_semantic_strong_keep_score,
            effective_semantic_min_keep_score,
            effective_numeric_support_min_pass,
            numeric_support_score=numeric_support_score_selected,
            numeric_support_min_score=effective_numeric_support_min_score,
            use_continuous_numeric=use_continuous_numeric,
            language_match=language_match,
            recency_pass=recency_pass,
        )

        decision_row = {
            "track_id": track_id,
            "is_seed_track": int(is_seed_track),
            "lead_genre": lead_genre,
            "semantic_score": round(semantic_score, 6),
            "lead_genre_similarity": round(lead_genre_match_score, 6),
            "genre_overlap_score": round(genre_overlap_fraction, 6),
            "tag_overlap_score": round(tag_overlap_fraction, 6),
            "lead_genre_match": int(lead_genre_match),
            "genre_overlap_count": genre_overlap,
            "tag_overlap_count": tag_overlap,
            "language": language_code or "",
            "language_match": "" if language_match is None else int(language_match),
            "release_year": "" if release_year is None else release_year,
            "release_year_distance": numeric_distances.get("release_year"),
            "numeric_pass_count": numeric_pass_count,
            "numeric_support_score": numeric_support_score,
            "numeric_support_score_weighted": numeric_support_score_weighted,
            "numeric_support_score_weighted_absolute": numeric_support_score_weighted_absolute,
            "numeric_support_score_selected": numeric_support_score_selected,
            "numeric_support_score_mode": numeric_support_score_mode,
            "numeric_confidence_weight_sum": round(weighted_support_denominator, 6),
            "profile_numeric_confidence_factor": round(profile_numeric_confidence_factor, 6),
            "effective_semantic_strong_keep_score": round(effective_semantic_strong_keep_score, 6),
            "effective_semantic_min_keep_score": round(effective_semantic_min_keep_score, 6),
            "effective_numeric_support_min_pass": effective_numeric_support_min_pass,
            "effective_numeric_support_min_score": round(effective_numeric_support_min_score, 6),
            "danceability_distance": numeric_distances.get("danceability"),
            "danceability_similarity": numeric_similarities.get("danceability", 0.0),
            "energy_distance": numeric_distances.get("energy"),
            "energy_similarity": numeric_similarities.get("energy", 0.0),
            "valence_distance": numeric_distances.get("valence"),
            "valence_similarity": numeric_similarities.get("valence", 0.0),
            "tempo_distance": numeric_distances.get("tempo"),
            "tempo_similarity": numeric_similarities.get("tempo", 0.0),
            "popularity_distance": numeric_distances.get("popularity"),
            "popularity_similarity": numeric_similarities.get("popularity", 0.0),
            "duration_ms_distance": numeric_distances.get("duration_ms"),
            "duration_ms_similarity": numeric_similarities.get("duration_ms", 0.0),
            "key_distance": numeric_distances.get("key"),
            "key_similarity": numeric_similarities.get("key", 0.0),
            "mode_distance": numeric_distances.get("mode"),
            "mode_similarity": numeric_similarities.get("mode", 0.0),
            "decision": "keep" if kept else "reject",
            "decision_path": decision_path,
            "decision_reason": decision_reason(
                decision_path,
                semantic_score,
                numeric_pass_count,
                numeric_support_score=numeric_support_score_selected,
                use_continuous_numeric=use_continuous_numeric,
            ),
        }

        tracker.record_decision(
            track_id,
            is_seed_track,
            kept,
            decision_path,
            decision_row,
            row if kept else None,
        )

    summary = tracker.get_summary()
    return tracker, tracker.decisions, tracker.kept_rows, summary


class RetrievalEvaluator:
    """OO wrapper for BL-005 candidate evaluation over a fixed runtime context."""

    def __init__(self, runtime_context: RetrievalContext) -> None:
        self.runtime_context = runtime_context

    def evaluate(self, candidate_rows: list[dict[str, str]]) -> RetrievalEvaluationResult:
        _, decisions, kept_rows, summary = evaluate_bl005_candidates(
            candidate_rows=candidate_rows,
            runtime_context=self.runtime_context,
        )
        return RetrievalEvaluationResult(
            decisions=decisions,
            kept_rows=kept_rows,
            summary=summary,
        )
