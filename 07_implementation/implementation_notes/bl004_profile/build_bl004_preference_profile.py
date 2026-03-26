from __future__ import annotations

import csv
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.config_loader import load_run_config_utils_module
from bl000_shared_utils.env_utils import env_int, env_str
from bl000_shared_utils.io_utils import (
    load_csv_rows,
    load_jsonl,
    parse_csv_labels,
    parse_float,
    sha256_of_file,
)
from bl000_shared_utils.path_utils import repo_root


# Hybrid profile: semantic labels + numeric centers from DS-001 candidate dataset.
NUMERIC_FEATURE_COLUMNS: list[str] = [
    "danceability",
    "energy",
    "valence",
    "tempo",
    "key",
    "mode",
    "popularity",
    "duration_ms",
]

SUMMARY_FEATURE_COLUMNS: list[str] = [
    "danceability",
    "energy",
    "valence",
    "tempo",
]

DEFAULT_TOP_TAG_LIMIT = 10
DEFAULT_TOP_GENRE_LIMIT = 10
DEFAULT_TOP_LEAD_GENRE_LIMIT = 10
DEFAULT_INCLUDE_INTERACTION_TYPES: list[str] = ["history", "influence"]
DEFAULT_INPUT_SCOPE: dict[str, object] = {
    "source_family": "spotify_api_export",
    "include_top_tracks": True,
    "top_time_ranges": ["short_term", "medium_term", "long_term"],
    "include_saved_tracks": True,
    "saved_tracks_limit": None,
    "include_playlists": True,
    "playlists_limit": None,
    "playlist_items_per_playlist_limit": None,
    "include_recently_played": True,
    "recently_played_limit": 50,
}


def infer_user_id_from_ingestion(root: Path) -> str | None:
    profile_path = (
        root
        / "07_implementation"
        / "implementation_notes"
        / "bl001_bl002_ingestion"
        / "outputs"
        / "spotify_api_export"
        / "spotify_profile.json"
    )
    if not profile_path.exists():
        return None
    try:
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    user_id = payload.get("id") if isinstance(payload, dict) else None
    if isinstance(user_id, str) and user_id.strip():
        return user_id.strip()
    return None


def resolve_bl004_runtime_controls() -> dict[str, object]:
    root = repo_root()
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip() or None
    env_user_id = env_str("BL004_USER_ID", "")
    inferred_user_id = infer_user_id_from_ingestion(root)

    def resolve_user_id(candidate: object) -> str:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
        if env_user_id:
            return env_user_id
        if inferred_user_id:
            return inferred_user_id
        return "unknown_user"

    if run_config_path:
        run_config_utils = load_run_config_utils_module()
        controls = run_config_utils.resolve_bl004_controls(run_config_path)
        user_id = resolve_user_id(controls.get("user_id"))
        return {
            "config_source": "run_config",
            "run_config_path": controls.get("config_path"),
            "run_config_schema_version": controls.get("schema_version"),
            "input_scope": dict(controls.get("input_scope") or DEFAULT_INPUT_SCOPE),
            "top_tag_limit": int(controls["top_tag_limit"]),
            "top_genre_limit": int(controls["top_genre_limit"]),
            "top_lead_genre_limit": int(controls["top_lead_genre_limit"]),
            "user_id": user_id,
            "include_interaction_types": list(controls.get("include_interaction_types") or DEFAULT_INCLUDE_INTERACTION_TYPES),
        }

    return {
        "config_source": "environment",
        "run_config_path": None,
        "run_config_schema_version": None,
        "input_scope": dict(DEFAULT_INPUT_SCOPE),
        "top_tag_limit": env_int("BL004_TOP_TAG_LIMIT", DEFAULT_TOP_TAG_LIMIT),
        "top_genre_limit": env_int("BL004_TOP_GENRE_LIMIT", DEFAULT_TOP_GENRE_LIMIT),
        "top_lead_genre_limit": env_int("BL004_TOP_LEAD_GENRE_LIMIT", DEFAULT_TOP_LEAD_GENRE_LIMIT),
        "user_id": resolve_user_id(None),
        "include_interaction_types": list(DEFAULT_INCLUDE_INTERACTION_TYPES),
    }


def load_csv(path: Path) -> list[dict[str, str]]:
    return load_csv_rows(path)


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


def parse_event_weighted_list(raw_value: object) -> list[tuple[str, float]]:
    if isinstance(raw_value, str):
        if not raw_value.strip():
            return []
        try:
            payload = json.loads(raw_value)
        except json.JSONDecodeError:
            return []
    elif isinstance(raw_value, list):
        payload = raw_value
    else:
        return []

    items: list[tuple[str, float]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        label = item.get("tag")
        score = item.get("weight")
        if not isinstance(label, str) or not label.strip():
            continue
        try:
            score_value = float(score)
        except (TypeError, ValueError):
            continue
        items.append((label.strip(), score_value))
    return items


def resolve_lead_genre(genres: list[str], tags: list[str]) -> str:
    if genres:
        return genres[0]
    if tags:
        return tags[0]
    return ""


def sorted_weight_map(weight_map: dict[str, float], limit: int) -> list[dict[str, float | str]]:
    ordered = sorted(weight_map.items(), key=lambda item: (-item[1], item[0]))
    return [
        {"label": label, "weight": round(weight, 6)}
        for label, weight in ordered[:limit]
    ]


def circular_mean_key(sum_x: float, sum_y: float) -> float | None:
    if sum_x == 0.0 and sum_y == 0.0:
        return None
    angle = math.atan2(sum_y, sum_x)
    if angle < 0.0:
        angle += 2.0 * math.pi
    return (angle / (2.0 * math.pi)) * 12.0


def main() -> None:
    root = repo_root()
    output_dir = root / "07_implementation" / "implementation_notes" / "bl004_profile" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    seed_table_path = (
        root / "07_implementation" / "implementation_notes"
        / "bl003_alignment" / "outputs" / "bl003_ds001_spotify_seed_table.csv"
    )

    seed_rows = load_csv(seed_table_path)
    if not seed_rows:
        raise RuntimeError("No DS-001 seed rows found for BL-004 input")

    runtime_controls = resolve_bl004_runtime_controls()
    user_id = str(runtime_controls["user_id"])
    input_scope = dict(runtime_controls["input_scope"])
    top_tag_limit = int(runtime_controls["top_tag_limit"])
    top_genre_limit = int(runtime_controls["top_genre_limit"])
    top_lead_genre_limit = int(runtime_controls["top_lead_genre_limit"])
    include_interaction_types = set(runtime_controls["include_interaction_types"])

    start_time = time.time()
    run_id = f"BL004-PROFILE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    numeric_sums = {column: 0.0 for column in NUMERIC_FEATURE_COLUMNS}
    numeric_weights = {column: 0.0 for column in NUMERIC_FEATURE_COLUMNS}
    tag_weights: dict[str, float] = {}
    genre_weights: dict[str, float] = {}
    lead_genre_weights: dict[str, float] = {}
    seed_trace_rows: list[dict[str, object]] = []

    counts_by_type = {"history": 0, "influence": 0}
    weight_by_type = {"history": 0.0, "influence": 0.0}
    interaction_count_sum_by_type = {"history": 0, "influence": 0}
    numeric_observations = {column: 0 for column in NUMERIC_FEATURE_COLUMNS}
    missing_numeric_track_ids: list[str] = []
    key_circular_sum_x = 0.0
    key_circular_sum_y = 0.0

    for index, row in enumerate(seed_rows, start=1):
        track_id = str(row.get("ds001_id", "")).strip()
        spotify_ids = str(row.get("spotify_track_ids", "")).strip().split("|")
        spotify_id = next((item for item in spotify_ids if item), "")
        # Read interaction_type from seed table; fall back to "history" for backward compat with older seed files
        raw_itypes = str(row.get("interaction_types", "") or row.get("interaction_type", "")).strip()
        row_interaction_types = {t.strip() for t in raw_itypes.split("|") if t.strip()} if raw_itypes else {"history"}
        if not row_interaction_types.intersection(include_interaction_types):
            continue
        # Use the most specific single interaction_type label for trace/summary (prefer "influence" if present)
        interaction_type = "influence" if "influence" in row_interaction_types else "history"
        preference_weight = parse_float(str(row.get("preference_weight_sum", ""))) or 0.0
        if preference_weight <= 0:
            continue
        effective_weight = preference_weight
        interaction_count = int(parse_float(str(row.get("interaction_count_sum", ""))) or max(1, round(preference_weight * 10)))
        tags = parse_csv_labels(str(row.get("tags", "")))
        genres = parse_csv_labels(str(row.get("genres", "")))

        counts_by_type[interaction_type] = counts_by_type.get(interaction_type, 0) + 1
        weight_by_type[interaction_type] = weight_by_type.get(interaction_type, 0.0) + effective_weight
        interaction_count_sum_by_type[interaction_type] = interaction_count_sum_by_type.get(interaction_type, 0) + interaction_count

        for tag in tags:
            tag_weights[tag] = tag_weights.get(tag, 0.0) + effective_weight

        for genre in genres:
            genre_weights[genre] = genre_weights.get(genre, 0.0) + effective_weight

        row_has_numeric_value = False
        for column in NUMERIC_FEATURE_COLUMNS:
            parsed_value = parse_float(str(row.get(column, "")))
            if parsed_value is None:
                continue
            row_has_numeric_value = True
            numeric_sums[column] += parsed_value * effective_weight
            numeric_weights[column] += effective_weight
            numeric_observations[column] += 1
            if column == "key":
                angle = (parsed_value / 12.0) * 2.0 * math.pi
                key_circular_sum_x += math.cos(angle) * effective_weight
                key_circular_sum_y += math.sin(angle) * effective_weight
        if not row_has_numeric_value:
            missing_numeric_track_ids.append(track_id)

        lead_genre = resolve_lead_genre(genres, tags)
        if lead_genre:
            lead_genre_weights[lead_genre] = lead_genre_weights.get(lead_genre, 0.0) + effective_weight

        seed_trace_rows.append(
            {
                "event_id": f"ds001_seed_{index:06d}",
                "track_id": track_id,
                "spotify_track_id": spotify_id,
                "spotify_artist": str(row.get("artist", "")),
                "spotify_title": str(row.get("song", "")),
                "interaction_type": interaction_type,
                "signal_source": "ds001_seed_table",
                "seed_rank": index,
                "interaction_count": interaction_count,
                "preference_weight": round(preference_weight, 6),
                "effective_weight": round(effective_weight, 6),
                "lead_genre": lead_genre,
                "top_tag": tags[0] if tags else "",
                "numeric_feature_coverage": "1" if row_has_numeric_value else "0",
                "lastfm_status": "not_applicable_ds001",
            }
        )

    total_effective_weight = sum(weight_by_type.values())
    matched_seed_count = len(seed_trace_rows)

    numeric_profile: dict[str, float] = {}
    for column in NUMERIC_FEATURE_COLUMNS:
        if numeric_weights[column] == 0:
            continue
        if column == "key":
            circular_key = circular_mean_key(key_circular_sum_x, key_circular_sum_y)
            if circular_key is None:
                continue
            numeric_profile[column] = round(circular_key, 6)
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
        "config_source": str(runtime_controls["config_source"]),
        "run_config_path": runtime_controls["run_config_path"],
        "run_config_schema_version": runtime_controls["run_config_schema_version"],
        "input_artifacts": {
            "seed_table_path": str(seed_table_path),
            "seed_table_sha256": sha256_of_file(seed_table_path),
        },
        "config": {
            "input_scope": input_scope,
            "effective_weight_rule": "effective_weight = preference_weight",
            "numeric_feature_columns": NUMERIC_FEATURE_COLUMNS,
            "profile_mode": "hybrid_semantic_numeric_from_bl003_enriched_seed_table",
            "top_tag_limit": top_tag_limit,
            "top_genre_limit": top_genre_limit,
            "top_lead_genre_limit": top_lead_genre_limit,
            "aggregation_rules": {
                "numeric": "weighted mean over numeric columns embedded in the BL-003 enriched seed table; key uses weighted circular mean on the 12-semitone wheel",
                "tags": "sum(preference_weight) over DS-001 tag labels",
                "genres": "sum(preference_weight) over DS-001 genre labels",
                "lead_genres": "sum(preference_weight)",
            },
        },
        "diagnostics": {
            "events_total": len(seed_rows),
            "matched_seed_count": matched_seed_count,
            "missing_seed_count": len(missing_numeric_track_ids),
            "missing_track_ids": missing_numeric_track_ids[:50],
            "candidate_rows_total": len(seed_rows),
            "numeric_observations": numeric_observations,
            "key_aggregation_method": "weighted_circular_mean",
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
            "top_tags": sorted_weight_map(tag_weights, top_tag_limit),
            "top_genres": sorted_weight_map(genre_weights, top_genre_limit),
            "top_lead_genres": sorted_weight_map(lead_genre_weights, top_lead_genre_limit),
        },
    }

    profile_path = output_dir / "bl004_preference_profile.json"
    with profile_path.open("w", encoding="utf-8") as handle:
        json.dump(profile, handle, indent=2, ensure_ascii=True)

    summary = {
        "run_id": run_id,
        "task": "BL-004",
        "user_id": user_id,
        "config_source": str(runtime_controls["config_source"]),
        "run_config_path": runtime_controls["run_config_path"],
        "run_config_schema_version": runtime_controls["run_config_schema_version"],
        "input_scope": input_scope,
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