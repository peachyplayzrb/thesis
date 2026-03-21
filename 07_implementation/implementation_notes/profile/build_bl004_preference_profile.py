from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path


NUMERIC_FEATURE_COLUMNS = [
    "lowlevel.average_loudness",
    "lowlevel.loudness_ebu128.integrated",
    "rhythm.danceability",
    "rhythm.bpm",
    "rhythm.onset_rate",
    "rhythm.beats_count",
    "rhythm.beats_loudness.mean",
    "lowlevel.spectral_energy.mean",
    "lowlevel.spectral_centroid.mean",
    "lowlevel.spectral_complexity.mean",
    "tonal.chords_changes_rate",
    "tonal.key_edma.strength",
    "tonal.key_krumhansl.strength",
    "tonal.key_temperley.strength",
    "V_mean",
    "A_mean",
    "D_mean",
    "P_mean",
    "V_std",
    "A_std",
    "D_std",
]

SUMMARY_FEATURE_COLUMNS = [
    "rhythm.bpm",
    "rhythm.danceability",
    "lowlevel.loudness_ebu128.integrated",
    "lowlevel.spectral_energy.mean",
    "tonal.key_edma.strength",
    "V_mean",
    "A_mean",
    "D_mean",
]

TOP_TAG_LIMIT = 10
TOP_GENRE_LIMIT = 10
TOP_LEAD_GENRE_LIMIT = 10


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            rows.append(json.loads(text))
    return rows


def load_candidate_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["track_id"]: row for row in reader}


def parse_float(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


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


def sorted_weight_map(weight_map: dict[str, float], limit: int) -> list[dict[str, float | str]]:
    ordered = sorted(weight_map.items(), key=lambda item: (-item[1], item[0]))
    return [
        {"label": label, "weight": round(weight, 6)}
        for label, weight in ordered[:limit]
    ]


def main() -> None:
    root = repo_root()
    input_dir = root / "07_implementation" / "implementation_notes" / "test_assets"
    output_dir = root / "07_implementation" / "implementation_notes" / "profile" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    aligned_path = input_dir / "bl016_synthetic_aligned_events.jsonl"
    candidate_path = input_dir / "bl016_candidate_stub.csv"

    events = load_jsonl(aligned_path)
    candidate_rows = load_candidate_rows(candidate_path)

    if not events:
        raise RuntimeError("No aligned events found for BL-004 input")

    user_ids = {str(event["user_id"]) for event in events}
    if len(user_ids) != 1:
        raise RuntimeError(f"Expected one user_id, got {sorted(user_ids)}")
    user_id = next(iter(user_ids))

    start_time = time.time()
    run_id = f"BL004-PROFILE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    numeric_sums = {column: 0.0 for column in NUMERIC_FEATURE_COLUMNS}
    numeric_weights = {column: 0.0 for column in NUMERIC_FEATURE_COLUMNS}
    tag_weights: dict[str, float] = {}
    genre_weights: dict[str, float] = {}
    lead_genre_weights: dict[str, float] = {}
    seed_trace_rows: list[dict[str, object]] = []
    missing_track_ids: list[str] = []

    counts_by_type = {"history": 0, "influence": 0}
    weight_by_type = {"history": 0.0, "influence": 0.0}
    interaction_count_sum_by_type = {"history": 0, "influence": 0}

    for event in events:
        track_id = str(event["track_id"])
        candidate = candidate_rows.get(track_id)
        if candidate is None:
            missing_track_ids.append(track_id)
            continue

        interaction_type = str(event["interaction_type"])
        preference_weight = float(event["preference_weight"])
        effective_weight = preference_weight
        interaction_count = int(event["interaction_count"])

        counts_by_type[interaction_type] = counts_by_type.get(interaction_type, 0) + 1
        weight_by_type[interaction_type] = weight_by_type.get(interaction_type, 0.0) + effective_weight
        interaction_count_sum_by_type[interaction_type] = interaction_count_sum_by_type.get(interaction_type, 0) + interaction_count

        for column in NUMERIC_FEATURE_COLUMNS:
            value = parse_float(candidate.get(column, ""))
            if value is None:
                continue
            numeric_sums[column] += value * effective_weight
            numeric_weights[column] += effective_weight

        for tag, score in parse_weighted_list(candidate.get("top_tags_json", ""), "tag", "weight"):
            tag_weights[tag] = tag_weights.get(tag, 0.0) + (effective_weight * score)

        for genre, score in parse_weighted_list(candidate.get("top_genres_json", ""), "genre", "score"):
            genre_weights[genre] = genre_weights.get(genre, 0.0) + (effective_weight * score)

        lead_genre = str(event.get("lead_genre", "")).strip()
        if lead_genre:
            lead_genre_weights[lead_genre] = lead_genre_weights.get(lead_genre, 0.0) + effective_weight

        seed_trace_rows.append(
            {
                "event_id": str(event["event_id"]),
                "track_id": track_id,
                "interaction_type": interaction_type,
                "signal_source": str(event["signal_source"]),
                "seed_rank": int(event["seed_rank"]),
                "interaction_count": interaction_count,
                "preference_weight": round(preference_weight, 6),
                "effective_weight": round(effective_weight, 6),
                "lead_genre": lead_genre,
                "top_tag": str(event.get("top_tag", "")),
                "candidate_playcount_sum": int(candidate.get("playcount_sum") or "0"),
                "candidate_listener_rows": int(candidate.get("listener_rows") or "0"),
            }
        )

    if missing_track_ids:
        raise RuntimeError(f"Missing candidate rows for track_ids: {missing_track_ids}")

    total_effective_weight = sum(weight_by_type.values())
    matched_seed_count = len(seed_trace_rows)

    numeric_profile: dict[str, float] = {}
    for column in NUMERIC_FEATURE_COLUMNS:
        if numeric_weights[column] == 0:
            continue
        numeric_profile[column] = round(numeric_sums[column] / numeric_weights[column], 6)

    seed_trace_rows.sort(key=lambda row: int(row["seed_rank"]))

    seed_trace_path = output_dir / "bl004_seed_trace.csv"
    with seed_trace_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(seed_trace_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(seed_trace_rows)

    profile = {
        "run_id": run_id,
        "task": "BL-004",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "user_id": user_id,
        "input_artifacts": {
            "aligned_events_path": str(aligned_path),
            "aligned_events_sha256": sha256_of_file(aligned_path),
            "candidate_stub_path": str(candidate_path),
            "candidate_stub_sha256": sha256_of_file(candidate_path),
        },
        "config": {
            "effective_weight_rule": "effective_weight = preference_weight",
            "numeric_feature_columns": NUMERIC_FEATURE_COLUMNS,
            "top_tag_limit": TOP_TAG_LIMIT,
            "top_genre_limit": TOP_GENRE_LIMIT,
            "top_lead_genre_limit": TOP_LEAD_GENRE_LIMIT,
            "aggregation_rules": {
                "numeric": "weighted mean over matched seeds",
                "tags": "sum(preference_weight * tag_weight)",
                "genres": "sum(preference_weight * genre_score)",
                "lead_genres": "sum(preference_weight)",
            },
        },
        "diagnostics": {
            "events_total": len(events),
            "matched_seed_count": matched_seed_count,
            "missing_seed_count": len(missing_track_ids),
            "missing_track_ids": missing_track_ids,
            "candidate_rows_total": len(candidate_rows),
            "total_effective_weight": round(total_effective_weight, 6),
            "elapsed_seconds": round(time.time() - start_time, 3),
        },
        "seed_summary": {
            "counts_by_interaction_type": counts_by_type,
            "weight_by_interaction_type": {key: round(value, 6) for key, value in weight_by_type.items()},
            "interaction_count_sum_by_interaction_type": interaction_count_sum_by_type,
            "seed_trace_path": str(seed_trace_path),
        },
        "numeric_feature_profile": numeric_profile,
        "semantic_profile": {
            "top_tags": sorted_weight_map(tag_weights, TOP_TAG_LIMIT),
            "top_genres": sorted_weight_map(genre_weights, TOP_GENRE_LIMIT),
            "top_lead_genres": sorted_weight_map(lead_genre_weights, TOP_LEAD_GENRE_LIMIT),
        },
    }

    profile_path = output_dir / "bl004_preference_profile.json"
    with profile_path.open("w", encoding="utf-8") as handle:
        json.dump(profile, handle, indent=2, ensure_ascii=True)

    summary = {
        "run_id": run_id,
        "task": "BL-004",
        "user_id": user_id,
        "matched_seed_count": matched_seed_count,
        "total_effective_weight": round(total_effective_weight, 6),
        "dominant_lead_genres": profile["semantic_profile"]["top_lead_genres"][:5],
        "dominant_tags": profile["semantic_profile"]["top_tags"][:5],
        "dominant_genres": profile["semantic_profile"]["top_genres"][:5],
        "feature_centers": {column: numeric_profile[column] for column in SUMMARY_FEATURE_COLUMNS},
        "artifact_paths": {
            "profile_path": str(profile_path),
            "seed_trace_path": str(seed_trace_path),
        },
        "input_hashes": profile["input_artifacts"],
    }

    summary_path = output_dir / "bl004_profile_summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    print("BL-004 preference profile created.")
    print(f"profile={profile_path}")
    print(f"summary={summary_path}")
    print(f"seed_trace={seed_trace_path}")


if __name__ == "__main__":
    main()