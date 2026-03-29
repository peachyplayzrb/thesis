"""BL-006 scoring stage executor for BL-011 controllability scenarios."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast

from shared_utils.io_utils import sha256_of_text
from shared_utils.parsing import parse_float
from controllability.reporting import csv_text, json_text
from controllability.weights import (
    candidate_labels,
    normalize_component_weight_keys,
    normalize_weight_map,
    numeric_similarity,
    weighted_overlap,
)


def execute_scoring_stage(
    profile_stage: dict[str, object], retrieval_stage: dict[str, object], scenario: dict[str, object]
) -> dict[str, object]:
    scenario_id = str(scenario["scenario_id"])
    scoring_config = cast(dict[str, Any], scenario["scoring"])
    profile = cast(dict[str, Any], profile_stage["profile"])
    semantic_profile = cast(dict[str, Any], profile["semantic_profile"])
    numeric_feature_profile = cast(dict[str, Any], profile["numeric_feature_profile"])
    candidates = cast(list[dict[str, str]], retrieval_stage["kept_rows"])
    if not candidates:
        raise RuntimeError(f"Scenario {scenario_id} has no BL-005 candidates for BL-006")

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

    numeric_thresholds = {key: float(value) for key, value in scoring_config["numeric_thresholds"].items()}
    numeric_components = [key for key in numeric_thresholds if key in component_weights]
    profile_lead_map, profile_lead_total = normalize_weight_map(
        cast(list[dict[str, object]], semantic_profile["top_lead_genres"]), top_k=6
    )
    profile_genre_map, profile_genre_total = normalize_weight_map(
        cast(list[dict[str, object]], semantic_profile["top_genres"]), top_k=8
    )
    profile_tag_map, profile_tag_total = normalize_weight_map(
        cast(list[dict[str, object]], semantic_profile["top_tags"]), top_k=10
    )

    scored_rows: list[dict[str, object]] = []
    component_totals = {component: 0.0 for component in component_weights}

    for row in candidates:
        lead_genres = candidate_labels(row, "genres")
        candidate_tags = candidate_labels(row, "tags")
        lead_genre = lead_genres[0] if lead_genres else (candidate_tags[0] if candidate_tags else "")

        component_similarity: dict[str, float] = {}
        component_contribution: dict[str, float] = {}

        for column in numeric_components:
            threshold = float(numeric_thresholds[column])
            value = parse_float(row.get(column, ""))
            center = float(cast(Any, numeric_feature_profile[column]))
            if column == "key" and value is not None:
                raw_diff = abs(value - center)
                circular_distance = min(raw_diff, 12.0 - raw_diff)
                similarity = max(0.0, min(1.0, round(1.0 - (circular_distance / threshold), 6)))
            else:
                similarity = numeric_similarity(value, center, threshold)
            component_similarity[column] = similarity
            component_contribution[column] = round(similarity * component_weights[column], 6)

        lead_genre_similarity = 0.0
        if lead_genre and lead_genre in profile_lead_map and profile_lead_total > 0:
            lead_genre_similarity = round(profile_lead_map[lead_genre] / max(profile_lead_map.values()), 6)
        component_similarity["lead_genre"] = lead_genre_similarity
        component_contribution["lead_genre"] = round(
            lead_genre_similarity * component_weights.get("lead_genre", 0.0),
            6,
        )

        genre_overlap_similarity, matched_genres = weighted_overlap(
            lead_genres, profile_genre_map, profile_genre_total
        )
        tag_overlap_similarity, matched_tags = weighted_overlap(
            candidate_tags, profile_tag_map, profile_tag_total
        )
        component_similarity["genre_overlap"] = genre_overlap_similarity
        component_contribution["genre_overlap"] = round(
            genre_overlap_similarity * component_weights.get("genre_overlap", 0.0),
            6,
        )
        component_similarity["tag_overlap"] = tag_overlap_similarity
        component_contribution["tag_overlap"] = round(
            tag_overlap_similarity * component_weights.get("tag_overlap", 0.0),
            6,
        )

        final_score = round(sum(component_contribution.values()), 6)
        for key, value in component_contribution.items():
            if key in component_totals:
                component_totals[key] += value

        row_payload: dict[str, object] = {
            "track_id": row["track_id"],
            "lead_genre": lead_genre,
            "matched_genres": "|".join(matched_genres),
            "matched_tags": "|".join(matched_tags),
            "final_score": final_score,
        }
        ordered_components = list(numeric_components) + [
            component
            for component in ["lead_genre", "genre_overlap", "tag_overlap"]
            if component in component_weights
        ]
        for component in ordered_components:
            row_payload[f"{component}_similarity"] = component_similarity.get(component, 0.0)
            row_payload[f"{component}_contribution"] = component_contribution.get(component, 0.0)
        scored_rows.append(row_payload)

    scored_rows.sort(key=lambda item: (-float(cast(Any, item["final_score"])), str(item["track_id"])))
    for index, row in enumerate(scored_rows, start=1):
        row["rank"] = index

    top_candidates = [
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
    score_values = [float(cast(Any, row["final_score"])) for row in scored_rows]
    summary = {
        "run_id": f"BL011-{scenario_id.upper()}-BL006-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
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
            "score_max": round(max(score_values), 6),
            "score_min": round(min(score_values), 6),
        },
        "top_candidates": top_candidates,
        "mean_component_contributions": {
            key: round(component_totals[key] / len(scored_rows), 6) for key in component_totals
        },
    }

    scored_fields = list(scored_rows[0].keys())
    if "rank" in scored_fields:
        scored_fields.remove("rank")
        scored_fields.insert(0, "rank")
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
