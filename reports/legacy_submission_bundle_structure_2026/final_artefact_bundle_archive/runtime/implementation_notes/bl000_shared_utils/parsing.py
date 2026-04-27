"""
Shared parsing and normalization helpers.
"""

from __future__ import annotations


def parse_float(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value: str) -> int | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None


def parse_csv_labels(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    labels: list[str] = []
    seen: set[str] = set()
    for piece in raw_value.split(","):
        label = piece.strip().lower()
        if not label or label in seen:
            continue
        seen.add(label)
        labels.append(label)
    return labels


def normalize_text(value: str | None, *, lowercase: bool = True) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if lowercase:
        text = text.lower()
    return text


def normalize_candidate_row(row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    track_id = (normalized.get("track_id") or "").strip()
    if not track_id:
        track_id = (normalized.get("id") or "").strip()
    if not track_id:
        track_id = (normalized.get("ds001_id") or "").strip()
    normalized["track_id"] = track_id
    return normalized
