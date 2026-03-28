"""Candidate evaluation loop for BL-005 retrieval."""

from __future__ import annotations

from shared_utils.constants import DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD
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


def evaluate_bl005_candidates(
    *,
    candidate_rows: list[dict[str, object]],
    runtime_context: dict[str, object],
) -> tuple[DecisionTracker, list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    active_numeric_specs: dict[str, dict[str, object]] = runtime_context["active_numeric_specs"]
    seed_track_ids: set[str] = runtime_context["seed_track_ids"]
    top_lead_genres: set[str] = runtime_context["top_lead_genres"]
    top_tags: set[str] = runtime_context["top_tags"]
    top_genres: set[str] = runtime_context["top_genres"]
    numeric_centers: dict[str, float] = runtime_context["numeric_centers"]
    numeric_features_enabled = bool(runtime_context["numeric_features_enabled"])
    semantic_strong_keep_score = int(runtime_context["semantic_strong_keep_score"])
    semantic_min_keep_score = int(runtime_context["semantic_min_keep_score"])
    numeric_support_min_pass = int(runtime_context["numeric_support_min_pass"])
    language_filter_enabled = bool(runtime_context["language_filter_enabled"])
    language_filter_codes = set(runtime_context["language_filter_codes"])
    recency_min_release_year = runtime_context["recency_min_release_year"]
    lead_genre_partial_match_threshold = float(
        runtime_context.get(
            "lead_genre_partial_match_threshold",
            DEFAULT_LEAD_GENRE_PARTIAL_MATCH_THRESHOLD,
        )
    )

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

        lead_genre_match_score = 0.0
        if lead_genre and top_lead_genres:
            lead_genre_match_score = max(
                lead_genre_token_similarity(lead_genre, profile_lead_genre)
                for profile_lead_genre in top_lead_genres
            )
        lead_genre_match = lead_genre_match_score >= lead_genre_partial_match_threshold
        genre_overlap = len(top_genres.intersection(candidate_genres))
        tag_overlap = len(top_tags.intersection(candidate_tags))

        genre_overlap_fraction = min(1.0, genre_overlap / max(1, len(top_genres)))
        tag_overlap_fraction = min(1.0, tag_overlap / max(1, len(top_tags)))
        semantic_score = lead_genre_match_score + genre_overlap_fraction + tag_overlap_fraction

        tracker.record_semantic_scores(semantic_score, lead_genre_match, genre_overlap, tag_overlap)

        numeric_pass_count = 0
        numeric_distances: dict[str, float | None] = {}
        numeric_rule_hits_this_candidate: dict[str, bool] = {}

        for profile_column, spec in active_numeric_specs.items():
            value = candidate_numeric_value(  # type: ignore[arg-type]
                row,
                profile_column,
                str(spec["candidate_column"]),
            )
            passed = False

            if value is not None:
                center = numeric_centers.get(profile_column)
                if center is not None:
                    if bool(spec["circular"]):
                        raw_diff = abs(value - center)
                        distance = min(raw_diff, 12.0 - raw_diff)
                    else:
                        distance = abs(value - center)
                    numeric_distances[profile_column] = round(distance, 6)
                    if distance <= float(spec["threshold"]):
                        numeric_pass_count += 1
                        passed = True
                else:
                    numeric_distances[profile_column] = None
            else:
                numeric_distances[profile_column] = None

            numeric_rule_hits_this_candidate[profile_column] = passed

        tracker.record_numeric_scores(numeric_pass_count, numeric_rule_hits_this_candidate)

        kept, decision_path = keep_decision(
            is_seed_track,
            semantic_score,
            numeric_pass_count,
            numeric_features_enabled,
            semantic_strong_keep_score,
            semantic_min_keep_score,
            numeric_support_min_pass,
            language_match=language_match,
            recency_pass=recency_pass,
        )

        decision_row = {
            "track_id": track_id,
            "is_seed_track": int(is_seed_track),
            "lead_genre": lead_genre,
            "semantic_score": round(semantic_score, 6),
            "lead_genre_match": int(lead_genre_match),
            "genre_overlap_count": genre_overlap,
            "tag_overlap_count": tag_overlap,
            "language": language_code or "",
            "language_match": "" if language_match is None else int(language_match),
            "release_year": "" if release_year is None else release_year,
            "release_year_distance": numeric_distances.get("release_year"),
            "numeric_pass_count": numeric_pass_count,
            "danceability_distance": numeric_distances.get("danceability"),
            "energy_distance": numeric_distances.get("energy"),
            "valence_distance": numeric_distances.get("valence"),
            "tempo_distance": numeric_distances.get("tempo"),
            "duration_ms_distance": numeric_distances.get("duration_ms"),
            "key_distance": numeric_distances.get("key"),
            "mode_distance": numeric_distances.get("mode"),
            "decision": "keep" if kept else "reject",
            "decision_path": decision_path,
            "decision_reason": decision_reason(decision_path, semantic_score, numeric_pass_count),
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
