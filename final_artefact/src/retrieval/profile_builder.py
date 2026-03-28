"""Profile-context builders for BL-005 retrieval."""

from __future__ import annotations

from retrieval.candidate_parser import resolve_candidate_column


def build_profile_label_set(
    profile: dict[str, object],
    semantic_key: str,
    limit: int,
) -> set[str]:
    semantic_profile = profile.get("semantic_profile")
    if not isinstance(semantic_profile, dict):
        return set()
    items = semantic_profile.get(semantic_key)
    if not isinstance(items, list):
        return set()

    labels: set[str] = set()
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        if isinstance(label, str) and label.strip():
            labels.add(label.strip().lower())
    return labels


def build_active_numeric_specs(
    profile: dict[str, object],
    effective_numeric_specs: dict[str, dict[str, object]],
    candidate_columns: set[str],
) -> dict[str, dict[str, object]]:
    numeric_profile = profile.get("numeric_feature_profile")
    if not isinstance(numeric_profile, dict):
        return {}

    active_specs: dict[str, dict[str, object]] = {}
    for profile_column, spec in effective_numeric_specs.items():
        if profile_column not in numeric_profile:
            continue
        resolved_column = resolve_candidate_column(
            profile_column,
            str(spec["candidate_column"]),
            candidate_columns,
        )
        if resolved_column is None:
            continue
        active_specs[profile_column] = {
            **spec,
            "candidate_column": resolved_column,
        }
    return active_specs
