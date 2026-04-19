"""BL-006 scoring stage executor for BL-011 controllability scenarios."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from controllability.reporting import csv_text, json_text
from controllability.weights import (
    candidate_labels,
    normalize_component_weight_keys,
    normalize_weight_map,
    numeric_similarity,
    weighted_overlap,
)
from shared_utils.io_utils import sha256_of_text
from shared_utils.parsing import parse_float


def _resolve_component_weights(
    scenario_id: str, scoring_config: dict[str, Any]
) -> dict[str, float]:
    raw_component_weights = (
        scoring_config.get("component_weights")
        or scoring_config.get("active_component_weights")
        or scoring_config.get("base_component_weights")
        or {}
    )
    component_weights = normalize_component_weight_keys(
        {key: float(value) for key, value in raw_component_weights.items()}
    )
    if not component_weights:
        raise RuntimeError(f"Scenario {scenario_id} has no scoring component weights")
    if abs(sum(component_weights.values()) - 1.0) > 1e-4:
        raise RuntimeError(f"Scenario {scenario_id} scoring weights must sum to 1.0")
    return component_weights


def _profile_weight_maps(
    semantic_profile: dict[str, Any],
) -> tuple[dict[str, float], float, dict[str, float], float, dict[str, float], float]:
    profile_lead_map, profile_lead_total = normalize_weight_map(
        cast(list[dict[str, object]], semantic_profile["top_lead_genres"]), top_k=6
    )
    profile_genre_map, profile_genre_total = normalize_weight_map(
        cast(list[dict[str, object]], semantic_profile["top_genres"]), top_k=8
    )
    profile_tag_map, profile_tag_total = normalize_weight_map(
        cast(list[dict[str, object]], semantic_profile["top_tags"]), top_k=10
    )
    return (
        profile_lead_map,
        profile_lead_total,
        profile_genre_map,
        profile_genre_total,
        profile_tag_map,
        profile_tag_total,
    )


def _ordered_components(
    numeric_components: list[str], component_weights: dict[str, float]
) -> list[str]:
    return list(numeric_components) + [
        component
        for component in ["lead_genre", "genre_overlap", "tag_overlap"]
        if component in component_weights
    ]


def _component_similarity_for_numeric_column(
    column: str,
    row: dict[str, str],
    numeric_feature_profile: dict[str, Any],
    numeric_thresholds: dict[str, float],
) -> float:
    threshold = float(numeric_thresholds[column])
    value = parse_float(row.get(column, ""))
    center = float(cast(Any, numeric_feature_profile[column]))
    if column == "key" and value is not None:
        raw_diff = abs(value - center)
        circular_distance = min(raw_diff, 12.0 - raw_diff)
        return max(0.0, min(1.0, round(1.0 - (circular_distance / threshold), 6)))
    return numeric_similarity(value, center, threshold)


def _numeric_components_for_candidate(
    row: dict[str, str],
    numeric_components: list[str],
    numeric_feature_profile: dict[str, Any],
    numeric_thresholds: dict[str, float],
    component_weights: dict[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    component_similarity: dict[str, float] = {}
    component_contribution: dict[str, float] = {}
    for column in numeric_components:
        similarity = _component_similarity_for_numeric_column(
            column, row, numeric_feature_profile, numeric_thresholds
        )
        component_similarity[column] = similarity
        component_contribution[column] = round(similarity * component_weights[column], 6)
    return component_similarity, component_contribution


def _semantic_components_for_candidate(
    lead_genres: list[str],
    candidate_tags: list[str],
    profile_lead_map: dict[str, float],
    profile_lead_total: float,
    profile_genre_map: dict[str, float],
    profile_genre_total: float,
    profile_tag_map: dict[str, float],
    profile_tag_total: float,
    component_weights: dict[str, float],
) -> tuple[str, list[str], list[str], dict[str, float], dict[str, float]]:
    lead_genre = lead_genres[0] if lead_genres else (candidate_tags[0] if candidate_tags else "")

    lead_genre_similarity = 0.0
    if lead_genre and lead_genre in profile_lead_map and profile_lead_total > 0:
        lead_genre_similarity = round(profile_lead_map[lead_genre] / max(profile_lead_map.values()), 6)

    genre_overlap_similarity, matched_genres = weighted_overlap(
        lead_genres, profile_genre_map, profile_genre_total
    )
    tag_overlap_similarity, matched_tags = weighted_overlap(
        candidate_tags, profile_tag_map, profile_tag_total
    )

    component_similarity = {
        "lead_genre": lead_genre_similarity,
        "genre_overlap": genre_overlap_similarity,
        "tag_overlap": tag_overlap_similarity,
    }
    component_contribution = {
        "lead_genre": round(
            lead_genre_similarity * component_weights.get("lead_genre", 0.0),
            6,
        ),
        "genre_overlap": round(
            genre_overlap_similarity * component_weights.get("genre_overlap", 0.0),
            6,
        ),
        "tag_overlap": round(
            tag_overlap_similarity * component_weights.get("tag_overlap", 0.0),
            6,
        ),
    }
    return lead_genre, matched_genres, matched_tags, component_similarity, component_contribution


def _scored_row_payload(
    row: dict[str, str],
    lead_genre: str,
    matched_genres: list[str],
    matched_tags: list[str],
    final_score: float,
    ordered_components: list[str],
    component_similarity: dict[str, float],
    component_contribution: dict[str, float],
) -> dict[str, object]:
    row_payload: dict[str, object] = {
        "track_id": row["track_id"],
        "lead_genre": lead_genre,
        "matched_genres": "|".join(matched_genres),
        "matched_tags": "|".join(matched_tags),
        "final_score": final_score,
    }
    for component in ordered_components:
        row_payload[f"{component}_similarity"] = component_similarity.get(component, 0.0)
        row_payload[f"{component}_contribution"] = component_contribution.get(component, 0.0)
    return row_payload


def _build_top_candidates(scored_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "rank": row["rank"],
            "track_id": row["track_id"],
            "lead_genre": row["lead_genre"],
            "final_score": row["final_score"],
            "matched_genres": row["matched_genres"],
            "matched_tags": row["matched_tags"],
        }
        for row in scored_rows[:10]
    ]


def _build_summary(
    scenario_id: str,
    numeric_thresholds: dict[str, float],
    component_weights: dict[str, float],
    scoring_config: dict[str, Any],
    scored_rows: list[dict[str, object]],
    component_totals: dict[str, float],
) -> dict[str, object]:
    score_values = [float(cast(Any, row["final_score"])) for row in scored_rows]
    return {
        "run_id": f"BL011-{scenario_id.upper()}-BL006-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-006",
        "scenario_id": scenario_id,
        "config": {
            "numeric_thresholds": numeric_thresholds,
            "component_weights": component_weights,
            "weight_override_component": scoring_config["weight_override_component"],
            "raw_override_value": scoring_config["raw_override_value"],
        },
        "counts": {
            "candidates_scored": len(scored_rows),
            "score_max": round(max(score_values), 6) if score_values else 0.0,
            "score_min": round(min(score_values), 6) if score_values else 0.0,
        },
        "top_candidates": _build_top_candidates(scored_rows),
        "mean_component_contributions": {
            key: (round(component_totals[key] / len(scored_rows), 6) if scored_rows else 0.0)
            for key in component_totals
        },
    }


def _scored_fields(ordered_components: list[str]) -> list[str]:
    fields = [
        "rank",
        "track_id",
        "lead_genre",
        "matched_genres",
        "matched_tags",
        "final_score",
    ]
    for component in ordered_components:
        fields.append(f"{component}_similarity")
        fields.append(f"{component}_contribution")
    return fields


def execute_scoring_stage(
    profile_stage: dict[str, object], retrieval_stage: dict[str, object], scenario: dict[str, object]
) -> dict[str, object]:
    scenario_id = str(scenario["scenario_id"])
    scoring_config = cast(dict[str, Any], scenario["scoring"])
    profile = cast(dict[str, Any], profile_stage["profile"])
    semantic_profile = cast(dict[str, Any], profile["semantic_profile"])
    numeric_feature_profile = cast(dict[str, Any], profile["numeric_feature_profile"])
    candidates = cast(list[dict[str, str]], retrieval_stage["kept_rows"])

    component_weights = _resolve_component_weights(scenario_id, scoring_config)

    numeric_thresholds = {key: float(value) for key, value in scoring_config["numeric_thresholds"].items()}
    numeric_components = [key for key in numeric_thresholds if key in component_weights]
    ordered_components = _ordered_components(numeric_components, component_weights)
    (
        profile_lead_map,
        profile_lead_total,
        profile_genre_map,
        profile_genre_total,
        profile_tag_map,
        profile_tag_total,
    ) = _profile_weight_maps(semantic_profile)

    scored_rows: list[dict[str, object]] = []
    component_totals = {component: 0.0 for component in component_weights}

    for row in candidates:
        lead_genres = candidate_labels(row, "genres")
        candidate_tags = candidate_labels(row, "tags")

        numeric_similarity_map, numeric_contribution_map = _numeric_components_for_candidate(
            row,
            numeric_components,
            numeric_feature_profile,
            numeric_thresholds,
            component_weights,
        )
        (
            lead_genre,
            matched_genres,
            matched_tags,
            semantic_similarity_map,
            semantic_contribution_map,
        ) = _semantic_components_for_candidate(
            lead_genres,
            candidate_tags,
            profile_lead_map,
            profile_lead_total,
            profile_genre_map,
            profile_genre_total,
            profile_tag_map,
            profile_tag_total,
            component_weights,
        )

        component_similarity = {**numeric_similarity_map, **semantic_similarity_map}
        component_contribution = {**numeric_contribution_map, **semantic_contribution_map}

        final_score = round(sum(component_contribution.values()), 6)
        for key, value in component_contribution.items():
            if key in component_totals:
                component_totals[key] += value

        scored_rows.append(
            _scored_row_payload(
                row,
                lead_genre,
                matched_genres,
                matched_tags,
                final_score,
                ordered_components,
                component_similarity,
                component_contribution,
            )
        )

    scored_rows.sort(key=lambda item: (-float(cast(Any, item["final_score"])), str(item["track_id"])))
    for index, row in enumerate(scored_rows, start=1):
        row["rank"] = index

    summary = _build_summary(
        scenario_id,
        numeric_thresholds,
        component_weights,
        scoring_config,
        scored_rows,
        component_totals,
    )

    scored_fields = _scored_fields(ordered_components)
    scored_text = csv_text(scored_fields, scored_rows)
    summary_text = json_text(summary)

    return {
        "scored_rows": scored_rows,
        "summary": summary,
        "texts": {
            "bl006_scored_candidates.csv": scored_text,
            "bl006_score_summary.json": summary_text,
        },
        "stable_hashes": {
            "ranked_output_hash": sha256_of_text(scored_text),
        },
    }
