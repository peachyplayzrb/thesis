"""BL-005 retrieval/filtering stage executor for BL-011 controllability scenarios."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, NamedTuple, cast

from controllability.reporting import csv_text, json_text
from controllability.weights import candidate_labels
from shared_utils.io_utils import sha256_of_text
from shared_utils.parsing import parse_float


class _SemanticTargets(NamedTuple):
    """Named return from _build_semantic_targets."""

    top_lead_genres: set[str]
    top_tags: set[str]
    top_genres: set[str]


class _SemanticMatchDetails(NamedTuple):
    """Named return from _semantic_match_details."""

    lead_genre_match: bool
    genre_overlap: int
    tag_overlap: int
    semantic_score: int


class _RetrievalSemanticInputs(NamedTuple):
    """Named return from _candidate_semantic_inputs."""

    candidate_genres: list[str]
    candidate_tags: list[str]
    lead_genre: str


def _decision_reason(is_seed_track: bool, semantic_score: int, numeric_pass_count: int, kept: bool) -> str:
    if is_seed_track:
        return "reject: seed track excluded from retrieval output"
    if kept:
        return f"keep: semantic_score={semantic_score}, numeric_pass_count={numeric_pass_count}"
    return (
        f"reject: semantic_score={semantic_score}, "
        f"numeric_pass_count={numeric_pass_count} below keep threshold"
    )


def _build_semantic_targets(
    semantic_profile: dict[str, Any], retrieval_config: dict[str, Any]
) -> _SemanticTargets:
    top_lead_genres = {
        item["label"]
        for item in cast(list[dict[str, Any]], semantic_profile["top_lead_genres"])[
            : int(retrieval_config["top_lead_genre_limit"])
        ]
    }
    top_tags = {
        item["label"]
        for item in cast(list[dict[str, Any]], semantic_profile["top_tags"])[
            : int(retrieval_config["top_tag_limit"])
        ]
    }
    top_genres = {
        item["label"]
        for item in cast(list[dict[str, Any]], semantic_profile["top_genres"])[
            : int(retrieval_config["top_genre_limit"])
        ]
    }
    return _SemanticTargets(
        top_lead_genres=top_lead_genres,
        top_tags=top_tags,
        top_genres=top_genres,
    )


def _scaled_numeric_thresholds(retrieval_config: dict[str, Any]) -> dict[str, float]:
    return {
        key: round(float(value) * float(retrieval_config["threshold_scale"]), 6)
        for key, value in retrieval_config["numeric_thresholds"].items()
    }


def _compute_numeric_distances(
    row: dict[str, str],
    *,
    scaled_thresholds: dict[str, float],
    numeric_centers: dict[str, float],
    numeric_rule_hits: dict[str, int],
) -> tuple[int, dict[str, float | None]]:
    numeric_pass_count = 0
    numeric_distances: dict[str, float | None] = {}

    for column, threshold in scaled_thresholds.items():
        value = parse_float(row.get(column, ""))
        if value is None:
            numeric_distances[column] = None
            continue
        center = numeric_centers.get(column)
        if center is None:
            numeric_distances[column] = None
            continue
        if column == "key":
            raw_diff = abs(value - center)
            distance = min(raw_diff, 12.0 - raw_diff)
        else:
            distance = abs(value - center)
        numeric_distances[column] = round(distance, 6)
        if distance <= threshold:
            numeric_pass_count += 1
            numeric_rule_hits[column] += 1

    return numeric_pass_count, numeric_distances


def _resolve_keep_decision(
    *,
    keep_rule: str,
    is_seed_track: bool,
    semantic_score: int,
    numeric_pass_count: int,
) -> bool:
    if is_seed_track:
        return False
    if "semantic_score >= 2 or" in keep_rule:
        return semantic_score >= 2 or (semantic_score >= 1 and numeric_pass_count >= 1)
    return (
        (semantic_score >= 2 and numeric_pass_count >= 4)
        or (semantic_score == 3 and numeric_pass_count >= 3)
    )


def _candidate_semantic_inputs(row: dict[str, str]) -> _RetrievalSemanticInputs:
    candidate_genres = candidate_labels(row, "genres")
    candidate_tags = candidate_labels(row, "tags")
    lead_genre = candidate_genres[0] if candidate_genres else (candidate_tags[0] if candidate_tags else "")
    return _RetrievalSemanticInputs(
        candidate_genres=candidate_genres,
        candidate_tags=candidate_tags,
        lead_genre=lead_genre,
    )


def _semantic_match_details(
    lead_genre: str,
    candidate_genres: list[str],
    candidate_tags: list[str],
    top_lead_genres: set[str],
    top_genres: set[str],
    top_tags: set[str],
) -> _SemanticMatchDetails:
    lead_genre_match = lead_genre in top_lead_genres if lead_genre else False
    genre_overlap = len(top_genres.intersection(candidate_genres))
    tag_overlap = len(top_tags.intersection(candidate_tags))
    semantic_score = (1 if lead_genre_match else 0) + (1 if genre_overlap > 0 else 0) + (1 if tag_overlap > 0 else 0)
    return _SemanticMatchDetails(
        lead_genre_match=lead_genre_match,
        genre_overlap=genre_overlap,
        tag_overlap=tag_overlap,
        semantic_score=semantic_score,
    )


def _update_semantic_rule_hits(
    semantic_rule_hits: dict[str, int],
    *,
    lead_genre_match: bool,
    genre_overlap: int,
    tag_overlap: int,
) -> None:
    if lead_genre_match:
        semantic_rule_hits["lead_genre_match"] += 1
    if genre_overlap > 0:
        semantic_rule_hits["genre_overlap"] += 1
    if tag_overlap > 0:
        semantic_rule_hits["tag_overlap"] += 1


def _update_decision_counts(
    decision_counts: dict[str, int],
    *,
    is_seed_track: bool,
    kept: bool,
) -> None:
    if is_seed_track:
        decision_counts["seed_excluded"] += 1
    elif kept:
        decision_counts["semantic_and_numeric_keep"] += 1
    else:
        decision_counts["rejected_threshold"] += 1


def _build_decision_row(
    *,
    track_id: str,
    is_seed_track: bool,
    lead_genre: str,
    semantic_score: int,
    lead_genre_match: bool,
    genre_overlap: int,
    tag_overlap: int,
    numeric_pass_count: int,
    kept: bool,
    numeric_distances: dict[str, float | None],
    scaled_thresholds: dict[str, float],
) -> dict[str, object]:
    decision_row: dict[str, object] = {
        "track_id": track_id,
        "is_seed_track": int(is_seed_track),
        "lead_genre": lead_genre,
        "semantic_score": semantic_score,
        "lead_genre_match": int(lead_genre_match),
        "genre_overlap_count": genre_overlap,
        "tag_overlap_count": tag_overlap,
        "numeric_pass_count": numeric_pass_count,
        "decision": "keep" if kept else "reject",
        "decision_reason": _decision_reason(is_seed_track, semantic_score, numeric_pass_count, kept),
    }
    for column in sorted(scaled_thresholds):
        decision_row[f"{column}_distance"] = numeric_distances.get(column)
    return decision_row


def _build_diagnostics(
    *,
    scenario_id: str,
    retrieval_config: dict[str, Any],
    scaled_thresholds: dict[str, float],
    candidate_rows: list[dict[str, str]],
    kept_rows: list[dict[str, str]],
    decision_counts: dict[str, int],
    semantic_rule_hits: dict[str, int],
    numeric_rule_hits: dict[str, int],
) -> dict[str, object]:
    return {
        "run_id": f"BL011-{scenario_id.upper()}-BL005-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-005",
        "scenario_id": scenario_id,
        "config": {
            "top_lead_genre_limit": retrieval_config["top_lead_genre_limit"],
            "top_tag_limit": retrieval_config["top_tag_limit"],
            "top_genre_limit": retrieval_config["top_genre_limit"],
            "threshold_scale": retrieval_config["threshold_scale"],
            "numeric_thresholds": scaled_thresholds,
            "keep_rule": retrieval_config["keep_rule"],
        },
        "counts": {
            "candidate_rows_total": len(candidate_rows),
            "seed_tracks_excluded": decision_counts["seed_excluded"],
            "kept_candidates": len(kept_rows),
            "rejected_non_seed_candidates": decision_counts["rejected_threshold"],
        },
        "rule_hits": {
            "semantic_rule_hits": semantic_rule_hits,
            "numeric_rule_hits": numeric_rule_hits,
        },
        "top_kept_track_ids": [row["track_id"] for row in kept_rows[:15]],
    }


def execute_retrieval_stage(
    profile_stage: dict[str, object],
    candidate_rows: list[dict[str, str]],
    scenario: dict[str, object],
) -> dict[str, object]:
    scenario_id = str(scenario["scenario_id"])
    retrieval_config = cast(dict[str, Any], scenario["retrieval"])
    profile = cast(dict[str, Any], profile_stage["profile"])
    semantic_profile = cast(dict[str, Any], profile["semantic_profile"])
    numeric_feature_profile = cast(dict[str, Any], profile["numeric_feature_profile"])
    seed_trace_rows = cast(list[dict[str, object]], profile_stage["seed_trace_rows"])

    seed_track_ids = {str(row["track_id"]) for row in seed_trace_rows}
    top_lead_genres, top_tags, top_genres = _build_semantic_targets(
        semantic_profile, retrieval_config
    )

    scaled_thresholds = _scaled_numeric_thresholds(retrieval_config)
    numeric_centers = {
        key: float(value)
        for key, value in numeric_feature_profile.items()
        if key in scaled_thresholds
    }
    keep_rule = str(retrieval_config.get("keep_rule", "")).lower()

    decisions: list[dict[str, object]] = []
    kept_rows: list[dict[str, str]] = []
    decision_counts = {"seed_excluded": 0, "semantic_and_numeric_keep": 0, "rejected_threshold": 0}
    semantic_rule_hits = {"lead_genre_match": 0, "genre_overlap": 0, "tag_overlap": 0}
    numeric_rule_hits = {key: 0 for key in scaled_thresholds}

    for row in candidate_rows:
        track_id = row["track_id"]
        is_seed_track = track_id in seed_track_ids
        candidate_genres, candidate_tags, lead_genre = _candidate_semantic_inputs(row)
        lead_genre_match, genre_overlap, tag_overlap, semantic_score = _semantic_match_details(
            lead_genre,
            candidate_genres,
            candidate_tags,
            top_lead_genres,
            top_genres,
            top_tags,
        )
        _update_semantic_rule_hits(
            semantic_rule_hits,
            lead_genre_match=lead_genre_match,
            genre_overlap=genre_overlap,
            tag_overlap=tag_overlap,
        )

        numeric_pass_count, numeric_distances = _compute_numeric_distances(
            row,
            scaled_thresholds=scaled_thresholds,
            numeric_centers=numeric_centers,
            numeric_rule_hits=numeric_rule_hits,
        )

        kept = _resolve_keep_decision(
            keep_rule=keep_rule,
            is_seed_track=is_seed_track,
            semantic_score=semantic_score,
            numeric_pass_count=numeric_pass_count,
        )

        _update_decision_counts(decision_counts, is_seed_track=is_seed_track, kept=kept)

        decisions.append(
            _build_decision_row(
                track_id=track_id,
                is_seed_track=is_seed_track,
                lead_genre=lead_genre,
                semantic_score=semantic_score,
                lead_genre_match=lead_genre_match,
                genre_overlap=genre_overlap,
                tag_overlap=tag_overlap,
                numeric_pass_count=numeric_pass_count,
                kept=kept,
                numeric_distances=numeric_distances,
                scaled_thresholds=scaled_thresholds,
            )
        )
        if kept:
            kept_rows.append(row)

    diagnostics = _build_diagnostics(
        scenario_id=scenario_id,
        retrieval_config=retrieval_config,
        scaled_thresholds=scaled_thresholds,
        candidate_rows=candidate_rows,
        kept_rows=kept_rows,
        decision_counts=decision_counts,
        semantic_rule_hits=semantic_rule_hits,
        numeric_rule_hits=numeric_rule_hits,
    )

    filtered_fields = list(candidate_rows[0].keys())
    decisions_fields = list(decisions[0].keys())
    filtered_text = csv_text(filtered_fields, [dict(row) for row in kept_rows])
    decisions_text = csv_text(decisions_fields, decisions)
    diagnostics_text = json_text(diagnostics)

    return {
        "kept_rows": kept_rows,
        "decisions": decisions,
        "diagnostics": diagnostics,
        "texts": {
            "bl005_filtered_candidates.csv": filtered_text,
            "bl005_candidate_decisions.csv": decisions_text,
            "bl005_candidate_diagnostics.json": diagnostics_text,
        },
        "stable_hashes": {
            "filtered_candidates_hash": sha256_of_text(filtered_text),
            "candidate_decisions_hash": sha256_of_text(decisions_text),
        },
    }
