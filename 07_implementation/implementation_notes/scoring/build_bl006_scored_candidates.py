from __future__ import annotations

import csv
import hashlib
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path


# DS-002 numeric features and tolerances
NUMERIC_THRESHOLDS = {
    "tempo":    20.0,   # BPM tolerance
    "loudness": 6.0,    # dB
    "key":      2.0,    # semitones (circular distance)
    "mode":     0.5,    # 0=minor/1=major: forces exact-match similarity
}

# Base component weights. Numeric components are dropped and re-normalized when
# the profile is semantic-only.
BASE_COMPONENT_WEIGHTS = {
    "tempo":        0.18,
    "loudness":     0.12,
    "key":          0.10,
    "mode":         0.05,
    "lead_genre":   0.20,
    "genre_overlap":0.17,
    "tag_overlap":  0.18,
}

NUMERIC_COMPONENTS = {"tempo", "loudness", "key", "mode"}


def build_active_component_weights(numeric_profile: dict[str, object]) -> dict[str, float]:
    active = {
        component: weight
        for component, weight in BASE_COMPONENT_WEIGHTS.items()
        if component not in NUMERIC_COMPONENTS or component in numeric_profile
    }
    total = sum(active.values())
    if total <= 0:
        raise RuntimeError("BL-006 requires at least one active scoring component")
    return {component: weight / total for component, weight in active.items()}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_float(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


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


def numeric_similarity(value: float | None, center: float, threshold: float, circular: bool = False) -> float:
    if value is None:
        return 0.0
    if circular:
        raw_diff = abs(value - center)
        diff = min(raw_diff, 12.0 - raw_diff)
    else:
        diff = abs(value - center)
    similarity = 1.0 - (diff / threshold)
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


def main() -> None:
    root = repo_root()
    profile_path = root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_preference_profile.json"
    filtered_candidates_path = root / "07_implementation" / "implementation_notes" / "retrieval" / "outputs" / "bl005_filtered_candidates.csv"
    output_dir = root / "07_implementation" / "implementation_notes" / "scoring" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    profile = load_json(profile_path)
    candidates = load_csv_rows(filtered_candidates_path)
    if not candidates:
        raise RuntimeError("No BL-005 filtered candidates found for BL-006")

    active_component_weights = build_active_component_weights(profile["numeric_feature_profile"])
    if round(sum(active_component_weights.values()), 6) != 1.0:
        raise RuntimeError("BL-006 active component weights must sum to 1.0")

    start_time = time.time()
    run_id = f"BL006-SCORE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    profile_lead_map, profile_lead_total = normalize_weight_map(profile["semantic_profile"]["top_lead_genres"], top_k=6)
    profile_genre_map, profile_genre_total = normalize_weight_map(profile["semantic_profile"]["top_genres"], top_k=8)
    profile_tag_map, profile_tag_total = normalize_weight_map(profile["semantic_profile"]["top_tags"], top_k=10)

    scored_rows: list[dict[str, object]] = []

    for row in candidates:
        # DS-002: tags_json covers both tag and genre signal
        candidate_tags = parse_labels(row.get("tags_json", ""), "tag")
        lead_genre = candidate_tags[0] if candidate_tags else ""
        candidate_genres = candidate_tags  # tags double as genre labels

        component_similarity: dict[str, float] = {}
        component_contribution: dict[str, float] = {}

        for column, threshold in NUMERIC_THRESHOLDS.items():
            value = parse_float(row.get(column, ""))
            center_raw = profile["numeric_feature_profile"].get(column)
            if center_raw is None or column not in active_component_weights:
                similarity = 0.0
            else:
                similarity = numeric_similarity(value, float(center_raw), threshold, circular=(column == "key"))
            component_similarity[column] = similarity
            component_contribution[column] = round(similarity * active_component_weights.get(column, 0.0), 6)

        lead_genre_similarity = 0.0
        if lead_genre and lead_genre in profile_lead_map and profile_lead_total > 0:
            lead_genre_similarity = round(profile_lead_map[lead_genre] / max(profile_lead_map.values()), 6)
        component_similarity["lead_genre"] = lead_genre_similarity
        component_contribution["lead_genre"] = round(lead_genre_similarity * active_component_weights.get("lead_genre", 0.0), 6)

        genre_overlap_similarity, matched_genres = weighted_overlap(candidate_genres, profile_genre_map, profile_genre_total)
        tag_overlap_similarity, matched_tags = weighted_overlap(candidate_tags, profile_tag_map, profile_tag_total)
        component_similarity["genre_overlap"] = genre_overlap_similarity
        component_contribution["genre_overlap"] = round(genre_overlap_similarity * active_component_weights.get("genre_overlap", 0.0), 6)
        component_similarity["tag_overlap"] = tag_overlap_similarity
        component_contribution["tag_overlap"] = round(tag_overlap_similarity * active_component_weights.get("tag_overlap", 0.0), 6)

        final_score = round(sum(component_contribution.values()), 6)

        scored_rows.append(
            {
                "track_id": row["track_id"],
                "lead_genre": lead_genre,
                "matched_genres": "|".join(matched_genres),
                "matched_tags": "|".join(matched_tags),
                "final_score": final_score,
                "tempo_similarity":        component_similarity["tempo"],
                "tempo_contribution":       component_contribution["tempo"],
                "loudness_similarity":      component_similarity["loudness"],
                "loudness_contribution":    component_contribution["loudness"],
                "key_similarity":           component_similarity["key"],
                "key_contribution":         component_contribution["key"],
                "mode_similarity":          component_similarity["mode"],
                "mode_contribution":        component_contribution["mode"],
                "lead_genre_similarity":    component_similarity["lead_genre"],
                "lead_genre_contribution":  component_contribution["lead_genre"],
                "genre_overlap_similarity": component_similarity["genre_overlap"],
                "genre_overlap_contribution": component_contribution["genre_overlap"],
                "tag_overlap_similarity":   component_similarity["tag_overlap"],
                "tag_overlap_contribution": component_contribution["tag_overlap"],
            }
        )

    scored_rows.sort(key=lambda item: (-float(item["final_score"]), str(item["track_id"])))
    for index, row in enumerate(scored_rows, start=1):
        row["rank"] = index

    scored_path = output_dir / "bl006_scored_candidates.csv"
    with scored_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "rank",
            "track_id",
            "lead_genre",
            "matched_genres",
            "matched_tags",
            "final_score",
            "tempo_similarity",
            "tempo_contribution",
            "loudness_similarity",
            "loudness_contribution",
            "key_similarity",
            "key_contribution",
            "mode_similarity",
            "mode_contribution",
            "lead_genre_similarity",
            "lead_genre_contribution",
            "genre_overlap_similarity",
            "genre_overlap_contribution",
            "tag_overlap_similarity",
            "tag_overlap_contribution",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(scored_rows)

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

    score_values = [float(row["final_score"]) for row in scored_rows]
    summary = {
        "run_id": run_id,
        "task": "BL-006",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_artifacts": {
            "profile_path": str(profile_path),
            "profile_sha256": sha256_of_file(profile_path),
            "filtered_candidates_path": str(filtered_candidates_path),
            "filtered_candidates_sha256": sha256_of_file(filtered_candidates_path),
        },
        "config": {
            "numeric_thresholds": NUMERIC_THRESHOLDS,
            "base_component_weights": BASE_COMPONENT_WEIGHTS,
            "active_component_weights": {key: round(value, 6) for key, value in active_component_weights.items()},
            "inactive_components": sorted(set(BASE_COMPONENT_WEIGHTS) - set(active_component_weights)),
            "lead_genre_normalization": "candidate lead genre weight divided by max profile lead-genre weight",
            "genre_overlap_normalization": "sum overlapping profile genre weights / sum top profile genre weights",
            "tag_overlap_normalization": "sum overlapping profile tag weights / sum top profile tag weights",
        },
        "counts": {
            "candidates_scored": len(scored_rows),
        },
        "score_statistics": {
            "max_score": round(max(score_values), 6),
            "min_score": round(min(score_values), 6),
            "mean_score": round(statistics.mean(score_values), 6),
            "median_score": round(statistics.median(score_values), 6),
        },
        "top_candidates": top_candidates,
        "elapsed_seconds": round(time.time() - start_time, 3),
        "output_files": {
            "scored_candidates_path": str(scored_path),
        },
    }

    summary_path = output_dir / "bl006_score_summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    summary["output_hashes_sha256"] = {
        "bl006_scored_candidates.csv": sha256_of_file(scored_path),
    }
    summary["summary_hash_note"] = "summary file hash collected separately in experiment logging to avoid recursive self-reference"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    print("BL-006 candidate scoring complete.")
    print(f"scored_candidates={scored_path}")
    print(f"score_summary={summary_path}")


if __name__ == "__main__":
    main()