from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path


PROFILE_TOP_LEAD_GENRE_LIMIT = 6
PROFILE_TOP_TAG_LIMIT = 10
PROFILE_TOP_GENRE_LIMIT = 8

# DS-002 numeric features and tolerances
NUMERIC_THRESHOLDS = {
    "tempo":    20.0,   # BPM tolerance
    "loudness": 6.0,    # dB tolerance
    "key":      2.0,    # semitones (circular distance)
    "mode":     0.5,    # 0=minor/1=major: 0.5 forces exact match
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


def parse_list(raw_value: str, label_key: str) -> list[str]:
    if not raw_value:
        return []
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    result: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        label = item.get(label_key)
        if isinstance(label, str) and label.strip():
            result.append(label.strip())
    return result


def decision_reason(is_seed_track: bool, semantic_score: int, numeric_pass_count: int, kept: bool) -> str:
    if is_seed_track:
        return "reject: seed track excluded from retrieval output"
    if kept:
        return f"keep: semantic_score={semantic_score}, numeric_pass_count={numeric_pass_count}"
    return f"reject: semantic_score={semantic_score}, numeric_pass_count={numeric_pass_count} below keep threshold"


def main() -> None:
    root = repo_root()
    profile_path = root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_preference_profile.json"
    seed_trace_path = root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_seed_trace.csv"
    candidate_path = (
        root / "07_implementation" / "implementation_notes"
        / "data_layer" / "outputs" / "bl019_ds002_integrated_candidate_dataset.csv"
    )
    output_dir = root / "07_implementation" / "implementation_notes" / "retrieval" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    profile = load_json(profile_path)
    candidate_rows = load_csv_rows(candidate_path)
    seed_trace_rows = load_csv_rows(seed_trace_path)

    seed_track_ids = {row["track_id"] for row in seed_trace_rows}
    top_lead_genres = {item["label"] for item in profile["semantic_profile"]["top_lead_genres"][:PROFILE_TOP_LEAD_GENRE_LIMIT]}
    top_tags = {item["label"] for item in profile["semantic_profile"]["top_tags"][:PROFILE_TOP_TAG_LIMIT]}
    top_genres = {item["label"] for item in profile["semantic_profile"]["top_genres"][:PROFILE_TOP_GENRE_LIMIT]}
    numeric_centers = {key: float(value) for key, value in profile["numeric_feature_profile"].items() if key in NUMERIC_THRESHOLDS}
    numeric_features_enabled = bool(numeric_centers)

    decisions: list[dict[str, object]] = []
    kept_rows: list[dict[str, str]] = []
    decision_counts = {
        "seed_excluded": 0,
        "semantic_and_numeric_keep": 0,
        "rejected_threshold": 0,
    }
    semantic_rule_hits = {
        "lead_genre_match": 0,
        "genre_overlap": 0,
        "tag_overlap": 0,
    }
    numeric_rule_hits = {key: 0 for key in NUMERIC_THRESHOLDS}

    start_time = time.time()
    run_id = f"BL005-FILTER-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    for row in candidate_rows:
        track_id = row["track_id"]
        is_seed_track = track_id in seed_track_ids

        # DS-002 uses tags_json (covers both tag and genre signal)
        lead_genre = ""
        candidate_tags = parse_list(row.get("tags_json", ""), "tag")
        if candidate_tags:
            lead_genre = candidate_tags[0]   # top tag acts as lead genre
        candidate_genres = candidate_tags    # same list for genre overlap

        lead_genre_match = lead_genre in top_lead_genres if lead_genre else False
        genre_overlap = len(top_genres.intersection(candidate_genres))
        tag_overlap = len(top_tags.intersection(candidate_tags))

        if lead_genre_match:
            semantic_rule_hits["lead_genre_match"] += 1
        if genre_overlap > 0:
            semantic_rule_hits["genre_overlap"] += 1
        if tag_overlap > 0:
            semantic_rule_hits["tag_overlap"] += 1

        semantic_score = 0
        semantic_score += 1 if lead_genre_match else 0
        semantic_score += 1 if genre_overlap > 0 else 0
        semantic_score += 1 if tag_overlap > 0 else 0

        numeric_pass_count = 0
        numeric_distances: dict[str, float | None] = {}
        for column, threshold in NUMERIC_THRESHOLDS.items():
            value = parse_float(row.get(column, ""))
            if value is None:
                numeric_distances[column] = None
                continue
            center = numeric_centers.get(column)
            if center is None:
                numeric_distances[column] = None
                continue
            # Circular distance for key (0-11 semitone wheel)
            if column == "key":
                raw_diff = abs(value - center)
                distance = min(raw_diff, 12.0 - raw_diff)
            else:
                distance = abs(value - center)
            numeric_distances[column] = round(distance, 6)
            if distance <= threshold:
                numeric_pass_count += 1
                numeric_rule_hits[column] += 1

        kept = False
        if not is_seed_track:
            if numeric_features_enabled:
                kept = (tag_overlap > 0) or (numeric_pass_count >= 2)
            else:
                kept = semantic_score >= 1

        if is_seed_track:
            decision_counts["seed_excluded"] += 1
        elif kept:
            decision_counts["semantic_and_numeric_keep"] += 1
        else:
            decision_counts["rejected_threshold"] += 1

        decision_row = {
            "track_id": track_id,
            "is_seed_track": int(is_seed_track),
            "lead_genre": lead_genre,
            "semantic_score": semantic_score,
            "lead_genre_match": int(lead_genre_match),
            "genre_overlap_count": genre_overlap,
            "tag_overlap_count": tag_overlap,
            "numeric_pass_count": numeric_pass_count,
            "tempo_distance":    numeric_distances.get("tempo"),
            "loudness_distance": numeric_distances.get("loudness"),
            "key_distance":      numeric_distances.get("key"),
            "mode_distance":     numeric_distances.get("mode"),
            "decision": "keep" if kept else "reject",
            "decision_reason": decision_reason(is_seed_track, semantic_score, numeric_pass_count, kept),
        }
        decisions.append(decision_row)
        if kept:
            kept_rows.append(row)

    filtered_path = output_dir / "bl005_filtered_candidates.csv"
    with filtered_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(candidate_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(kept_rows)

    decisions_path = output_dir / "bl005_candidate_decisions.csv"
    with decisions_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(decisions[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(decisions)

    diagnostics = {
        "run_id": run_id,
        "task": "BL-005",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_artifacts": {
            "profile_path": str(profile_path),
            "profile_sha256": sha256_of_file(profile_path),
            "seed_trace_path": str(seed_trace_path),
            "seed_trace_sha256": sha256_of_file(seed_trace_path),
            "candidate_stub_path": str(candidate_path),
            "candidate_stub_sha256": sha256_of_file(candidate_path),
        },
        "config": {
            "top_lead_genre_limit": PROFILE_TOP_LEAD_GENRE_LIMIT,
            "top_tag_limit": PROFILE_TOP_TAG_LIMIT,
            "top_genre_limit": PROFILE_TOP_GENRE_LIMIT,
            "numeric_thresholds": NUMERIC_THRESHOLDS,
            "numeric_features_enabled": numeric_features_enabled,
            "keep_rule": (
                "keep if not seed and ((tag_overlap > 0) or (numeric_pass_count >= 2))"
                if numeric_features_enabled
                else "keep if not seed and semantic_score >= 1"
            ),
        },
        "counts": {
            "candidate_rows_total": len(candidate_rows),
            "seed_tracks_excluded": decision_counts["seed_excluded"],
            "kept_candidates": len(kept_rows),
            "rejected_non_seed_candidates": decision_counts["rejected_threshold"],
        },
        "rule_hits": {
            "semantic_rule_hits": semantic_rule_hits,
            "numeric_rule_hits": numeric_rule_hits,
        },
        "top_kept_track_ids": [row["track_id"] for row in kept_rows[:15]],
        "elapsed_seconds": round(time.time() - start_time, 3),
        "output_files": {
            "filtered_candidates_path": str(filtered_path),
            "candidate_decisions_path": str(decisions_path),
        },
    }

    diagnostics_path = output_dir / "bl005_candidate_diagnostics.json"
    with diagnostics_path.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    diagnostics["output_hashes_sha256"] = {
        "bl005_filtered_candidates.csv": sha256_of_file(filtered_path),
        "bl005_candidate_decisions.csv": sha256_of_file(decisions_path),
    }
    diagnostics["diagnostics_hash_note"] = "diagnostics file does not store its own hash to avoid recursive self-reference"
    with diagnostics_path.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, indent=2, ensure_ascii=True)

    print("BL-005 candidate filtering complete.")
    print(f"filtered_candidates={filtered_path}")
    print(f"decisions={decisions_path}")
    print(f"diagnostics={diagnostics_path}")


if __name__ == "__main__":
    main()