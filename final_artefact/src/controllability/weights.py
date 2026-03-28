from __future__ import annotations

import json

from shared_utils.parsing import parse_csv_labels


def parse_weighted_list(raw_value: str, key_name: str, score_name: str) -> list[tuple[str, float]]:
    if not raw_value:
        return []
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return []

    items: list[tuple[str, float]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        label = item.get(key_name)
        score = item.get(score_name)
        if not isinstance(label, str) or not label.strip():
            continue
        try:
            score_value = float(score)
        except (TypeError, ValueError):
            continue
        items.append((label.strip(), score_value))
    return items


def parse_labels(raw_value: str, label_key: str) -> list[str]:
    if not raw_value:
        return []
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return []

    labels: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        label = item.get(label_key)
        if isinstance(label, str) and label.strip():
            labels.append(label.strip())
    return labels


def candidate_labels(row: dict[str, str], label_type: str) -> list[str]:
    if label_type == "genres":
        legacy = parse_labels(row.get("top_genres_json", ""), "genre")
        if legacy:
            return legacy
        return parse_csv_labels(row.get("genres", ""))
    legacy = parse_labels(row.get("top_tags_json", ""), "tag")
    if legacy:
        return legacy
    return parse_csv_labels(row.get("tags", ""))


def candidate_weight_pairs(row: dict[str, str], label_type: str) -> list[tuple[str, float]]:
    if label_type == "genres":
        legacy = parse_weighted_list(row.get("top_genres_json", ""), "genre", "score")
        if legacy:
            return legacy
        return [(label, 1.0) for label in parse_csv_labels(row.get("genres", ""))]
    legacy = parse_weighted_list(row.get("top_tags_json", ""), "tag", "weight")
    if legacy:
        return legacy
    return [(label, 1.0) for label in parse_csv_labels(row.get("tags", ""))]


def sorted_weight_map(weight_map: dict[str, float], limit: int) -> list[dict[str, float | str]]:
    ordered = sorted(weight_map.items(), key=lambda item: (-item[1], item[0]))
    return [{"label": label, "weight": round(weight, 6)} for label, weight in ordered[:limit]]


def numeric_similarity(value: float | None, center: float, threshold: float) -> float:
    if value is None:
        return 0.0
    similarity = 1.0 - (abs(value - center) / threshold)
    if similarity < 0:
        return 0.0
    if similarity > 1:
        return 1.0
    return round(similarity, 6)


def weighted_overlap(candidate_labels: list[str], profile_weight_map: dict[str, float], profile_total: float) -> tuple[float, list[str]]:
    matched = [label for label in candidate_labels if label in profile_weight_map]
    if not matched or profile_total <= 0:
        return 0.0, []
    overlap_weight = sum(profile_weight_map[label] for label in matched)
    return round(overlap_weight / profile_total, 6), matched


def normalize_weight_map(items: list[dict[str, object]], top_k: int) -> tuple[dict[str, float], float]:
    subset = items[:top_k]
    weight_map: dict[str, float] = {}
    total = 0.0
    for item in subset:
        label = item.get("label")
        weight = item.get("weight")
        if not isinstance(label, str):
            continue
        try:
            numeric_weight = float(weight)
        except (TypeError, ValueError):
            continue
        weight_map[label] = numeric_weight
        total += numeric_weight
    return weight_map, total


def normalized_weights_with_override(base_weights: dict[str, float], component: str, raw_target: float) -> dict[str, float]:
    weights = dict(base_weights)
    weights[component] = raw_target
    total = sum(weights.values())
    return {key: round(value / total, 6) for key, value in weights.items()}


def normalize_component_weight_keys(raw_weights: dict[str, float]) -> dict[str, float]:
    """
    Normalize component weight keys to canonical BL-006 names.

    Handles historical naming variants such as "tempo_score" and
    canonicalizes to "tempo" so scoring and diagnostics use one schema.
    """
    normalized: dict[str, float] = {}
    for raw_key, raw_value in raw_weights.items():
        key = str(raw_key).strip()
        if key.endswith("_score"):
            key = key[: -len("_score")]
        if not key:
            continue
        normalized[key] = normalized.get(key, 0.0) + float(raw_value)

    total = sum(normalized.values())
    if total > 0:
        normalized = {k: round(v / total, 6) for k, v in normalized.items()}
    return normalized
