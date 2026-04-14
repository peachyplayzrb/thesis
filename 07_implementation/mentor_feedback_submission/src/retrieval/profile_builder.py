"""Helpers that pull the parts of the BL-004 profile BL-005 actually needs."""

from __future__ import annotations

from retrieval.candidate_parser import resolve_candidate_column
from retrieval.models import NumericFeatureSpec


def build_profile_weight_map(
    profile: dict[str, object],
    semantic_key: str,
    limit: int,
) -> dict[str, float]:
    """Build one normalized weight map from the semantic profile, capped to the top requested labels."""

    semantic_profile = profile.get("semantic_profile")
    if not isinstance(semantic_profile, dict):
        return {}
    items = semantic_profile.get(semantic_key)
    if not isinstance(items, list):
        return {}

    labels: list[str] = []
    weighted_entries: list[tuple[str, float]] = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        if not isinstance(label, str) or not label.strip():
            continue
        normalized_label = label.strip().lower()
        labels.append(normalized_label)
        raw_weight = item.get("weight")
        if isinstance(raw_weight, (int, float)) and float(raw_weight) > 0:
            weighted_entries.append((normalized_label, float(raw_weight)))

    if weighted_entries:
        total = sum(weight for _, weight in weighted_entries)
        if total > 0:
            return {
                label: round(weight / total, 6)
                for label, weight in weighted_entries
            }

    unique_labels = list(dict.fromkeys(labels))
    if not unique_labels:
        return {}
    uniform_weight = round(1.0 / len(unique_labels), 6)
    return {label: uniform_weight for label in unique_labels}


def build_profile_label_set(
    profile: dict[str, object],
    semantic_key: str,
    limit: int,
) -> set[str]:
    return set(build_profile_weight_map(profile, semantic_key, limit))


def build_active_numeric_specs(
    profile: dict[str, object],
    effective_numeric_specs: dict[str, NumericFeatureSpec],
    candidate_columns: set[str],
) -> dict[str, NumericFeatureSpec]:
    numeric_profile = profile.get("numeric_feature_profile")
    if not isinstance(numeric_profile, dict):
        return {}

    active_specs: dict[str, NumericFeatureSpec] = {}
    for profile_column, spec in effective_numeric_specs.items():
        if profile_column not in numeric_profile:
            continue
        resolved_column = resolve_candidate_column(
            profile_column,
            spec.candidate_column,
            candidate_columns,
        )
        if resolved_column is None:
            continue
        active_specs[profile_column] = NumericFeatureSpec(
            candidate_column=resolved_column,
            threshold=spec.threshold,
            circular=spec.circular,
        )
    return active_specs
