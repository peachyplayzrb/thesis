from __future__ import annotations

import csv
import hashlib
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path


NUMERIC_THRESHOLDS = {
    "rhythm.bpm": 20.0,
    "rhythm.danceability": 0.4,
    "lowlevel.loudness_ebu128.integrated": 6.0,
    "V_mean": 0.8,
    "A_mean": 0.9,
    "D_mean": 0.8,
}

COMPONENT_WEIGHTS = {
    "rhythm.bpm": 0.10,
    "rhythm.danceability": 0.10,
    "lowlevel.loudness_ebu128.integrated": 0.08,
    "V_mean": 0.12,
    "A_mean": 0.08,
    "D_mean": 0.08,
    "lead_genre": 0.12,
    "genre_overlap": 0.16,
    "tag_overlap": 0.16,
}


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

    if round(sum(COMPONENT_WEIGHTS.values()), 6) != 1.0:
        raise RuntimeError("BL-006 component weights must sum to 1.0")

    start_time = time.time()
    run_id = f"BL006-SCORE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    profile_lead_map, profile_lead_total = normalize_weight_map(profile["semantic_profile"]["top_lead_genres"], top_k=6)
    profile_genre_map, profile_genre_total = normalize_weight_map(profile["semantic_profile"]["top_genres"], top_k=8)
    profile_tag_map, profile_tag_total = normalize_weight_map(profile["semantic_profile"]["top_tags"], top_k=10)

    scored_rows: list[dict[str, object]] = []

    for row in candidates:
        lead_genres = parse_labels(row.get("top_genres_json", ""), "genre")
        candidate_tags = parse_labels(row.get("top_tags_json", ""), "tag")
        lead_genre = lead_genres[0] if lead_genres else ""

        component_similarity: dict[str, float] = {}
        component_contribution: dict[str, float] = {}

        for column, threshold in NUMERIC_THRESHOLDS.items():
            value = parse_float(row.get(column, ""))
            center = float(profile["numeric_feature_profile"][column])
            similarity = numeric_similarity(value, center, threshold)
            component_similarity[column] = similarity
            component_contribution[column] = round(similarity * COMPONENT_WEIGHTS[column], 6)

        lead_genre_similarity = 0.0
        if lead_genre and lead_genre in profile_lead_map and profile_lead_total > 0:
            lead_genre_similarity = round(profile_lead_map[lead_genre] / max(profile_lead_map.values()), 6)
        component_similarity["lead_genre"] = lead_genre_similarity
        component_contribution["lead_genre"] = round(lead_genre_similarity * COMPONENT_WEIGHTS["lead_genre"], 6)

        genre_overlap_similarity, matched_genres = weighted_overlap(lead_genres, profile_genre_map, profile_genre_total)
        tag_overlap_similarity, matched_tags = weighted_overlap(candidate_tags, profile_tag_map, profile_tag_total)
        component_similarity["genre_overlap"] = genre_overlap_similarity
        component_contribution["genre_overlap"] = round(genre_overlap_similarity * COMPONENT_WEIGHTS["genre_overlap"], 6)
        component_similarity["tag_overlap"] = tag_overlap_similarity
        component_contribution["tag_overlap"] = round(tag_overlap_similarity * COMPONENT_WEIGHTS["tag_overlap"], 6)

        final_score = round(sum(component_contribution.values()), 6)

        scored_rows.append(
            {
                "track_id": row["track_id"],
                "lead_genre": lead_genre,
                "matched_genres": "|".join(matched_genres),
                "matched_tags": "|".join(matched_tags),
                "final_score": final_score,
                "bpm_similarity": component_similarity["rhythm.bpm"],
                "bpm_contribution": component_contribution["rhythm.bpm"],
                "danceability_similarity": component_similarity["rhythm.danceability"],
                "danceability_contribution": component_contribution["rhythm.danceability"],
                "loudness_similarity": component_similarity["lowlevel.loudness_ebu128.integrated"],
                "loudness_contribution": component_contribution["lowlevel.loudness_ebu128.integrated"],
                "V_mean_similarity": component_similarity["V_mean"],
                "V_mean_contribution": component_contribution["V_mean"],
                "A_mean_similarity": component_similarity["A_mean"],
                "A_mean_contribution": component_contribution["A_mean"],
                "D_mean_similarity": component_similarity["D_mean"],
                "D_mean_contribution": component_contribution["D_mean"],
                "lead_genre_similarity": component_similarity["lead_genre"],
                "lead_genre_contribution": component_contribution["lead_genre"],
                "genre_overlap_similarity": component_similarity["genre_overlap"],
                "genre_overlap_contribution": component_contribution["genre_overlap"],
                "tag_overlap_similarity": component_similarity["tag_overlap"],
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
            "bpm_similarity",
            "bpm_contribution",
            "danceability_similarity",
            "danceability_contribution",
            "loudness_similarity",
            "loudness_contribution",
            "V_mean_similarity",
            "V_mean_contribution",
            "A_mean_similarity",
            "A_mean_contribution",
            "D_mean_similarity",
            "D_mean_contribution",
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
            "component_weights": COMPONENT_WEIGHTS,
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