from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path


LEGACY_NUMERIC_COLUMNS = {
    "rhythm.bpm",
    "rhythm.danceability",
    "lowlevel.loudness_ebu128.integrated",
    "V_mean",
    "A_mean",
    "D_mean",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json_hash(payload: object) -> str:
    return sha256_of_text(json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":")))


def json_text(payload: object) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"


def csv_text(fieldnames: list[str], rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_candidate_row(row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    track_id = (normalized.get("track_id") or "").strip()
    if not track_id:
        track_id = (normalized.get("id") or "").strip()
    if not track_id:
        track_id = (normalized.get("ds001_id") or "").strip()
    normalized["track_id"] = track_id
    return normalized


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


def resolve_legacy_mode(paths: dict[str, Path]) -> bool:
    return paths["legacy_events"].exists() and paths["legacy_candidates"].exists()


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


def decision_reason(is_seed_track: bool, semantic_score: int, numeric_pass_count: int, kept: bool) -> str:
    if is_seed_track:
        return "reject: seed track excluded from retrieval output"
    if kept:
        return f"keep: semantic_score={semantic_score}, numeric_pass_count={numeric_pass_count}"
    return f"reject: semantic_score={semantic_score}, numeric_pass_count={numeric_pass_count} below keep threshold"


def build_paths(root: Path) -> dict[str, Path]:
    return {
        "legacy_events": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_synthetic_aligned_events.jsonl",
        "legacy_candidates": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_candidate_stub.csv",
        "legacy_manifest": root / "07_implementation" / "implementation_notes" / "test_assets" / "bl016_asset_manifest.json",
        "legacy_coverage": root / "07_implementation" / "implementation_notes" / "data_layer" / "outputs" / "onion_join_coverage_report.json",
        "active_seed_trace": root / "07_implementation" / "implementation_notes" / "profile" / "outputs" / "bl004_seed_trace.csv",
        "active_candidates": root / "07_implementation" / "implementation_notes" / "data_layer" / "outputs" / "ds001_working_candidate_dataset.csv",
        "baseline_snapshot": root / "07_implementation" / "implementation_notes" / "reproducibility" / "outputs" / "bl010_reproducibility_config_snapshot.json",
        "output_dir": root / "07_implementation" / "implementation_notes" / "controllability" / "outputs",
    }


def ensure_required_inputs(paths: dict[str, Path], root: Path) -> None:
    required = ["baseline_snapshot"]
    if resolve_legacy_mode(paths):
        required.extend(["legacy_events", "legacy_candidates"])
    else:
        required.extend(["active_seed_trace", "active_candidates"])
    missing = [relpath(paths[key], root) for key in required if not paths[key].exists()]
    if missing:
        raise FileNotFoundError(f"BL-011 missing required inputs: {missing}")


def build_scenarios(baseline_snapshot: dict) -> list[dict[str, object]]:
    base_profile = baseline_snapshot["stage_configs"]["profile"]
    base_retrieval = baseline_snapshot["stage_configs"]["retrieval"]
    base_scoring = baseline_snapshot["stage_configs"]["scoring"]
    base_assembly = baseline_snapshot["stage_configs"]["assembly"]
    scoring_weights = dict(
        base_scoring.get("component_weights")
        or base_scoring.get("active_component_weights")
        or base_scoring.get("base_component_weights")
        or {}
    )
    if not scoring_weights:
        raise RuntimeError("BL-011 could not resolve scoring component weights from baseline snapshot")
    if "valence" in scoring_weights:
        override_component = "valence"
        override_raw_value = 0.20
    elif "V_mean" in scoring_weights:
        override_component = "V_mean"
        override_raw_value = 0.20
    else:
        override_component = next(iter(scoring_weights.keys()))
        override_raw_value = min(0.35, float(scoring_weights[override_component]) + 0.08)

    return [
        {
            "scenario_id": "baseline",
            "test_id": "baseline",
            "control_surface": "fixed_bl010_baseline",
            "description": "BL-010 fixed baseline carried forward unchanged for BL-011 comparisons.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": 1.0,
            },
            "scoring": {
                **base_scoring,
                "weight_override_component": None,
                "raw_override_value": None,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "reference",
        },
        {
            "scenario_id": "no_influence_tracks",
            "test_id": "EP-CTRL-001",
            "control_surface": "influence_tracks",
            "description": "Remove the three synthetic influence tracks while keeping all other inputs and parameters fixed.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": 1.0,
            },
            "scoring": {
                **base_scoring,
                "weight_override_component": None,
                "raw_override_value": None,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "profile and ranking shift away from influence-steered indie/alternative emphasis",
        },
        {
            "scenario_id": "valence_weight_up",
            "test_id": "EP-CTRL-002",
            "control_surface": "feature_weight",
            "description": "Increase one score-component raw weight and renormalize all score weights to preserve a 1.0 total.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": 1.0,
            },
            "scoring": {
                **base_scoring,
                "component_weights": normalized_weights_with_override(scoring_weights, override_component, override_raw_value),
                "weight_override_component": override_component,
                "raw_override_value": override_raw_value,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "tracks with stronger fit on the boosted component should gain score contribution and rank position",
        },
        {
            "scenario_id": "stricter_thresholds",
            "test_id": "EP-CTRL-003",
            "control_surface": "candidate_threshold",
            "description": "Tighten all numeric retrieval thresholds by multiplying them by 0.75.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": 0.75,
            },
            "scoring": {
                **base_scoring,
                "weight_override_component": None,
                "raw_override_value": None,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "candidate pool should shrink and playlist overlap should reduce or reorder",
        },
        {
            "scenario_id": "looser_thresholds",
            "test_id": "EP-CTRL-003",
            "control_surface": "candidate_threshold",
            "description": "Loosen all numeric retrieval thresholds by multiplying them by 1.25.",
            "profile": {
                **base_profile,
                "include_interaction_types": ["history", "influence"],
            },
            "retrieval": {
                **base_retrieval,
                "threshold_scale": 1.25,
            },
            "scoring": {
                **base_scoring,
                "weight_override_component": None,
                "raw_override_value": None,
            },
            "assembly": dict(base_assembly),
            "expected_effect": "candidate pool should expand and downstream ranking or playlist composition should change",
        },
    ]


def execute_profile_stage(
    events: list[dict[str, object]],
    candidate_rows_by_id: dict[str, dict[str, str]],
    scenario: dict[str, object],
    root: Path,
    input_artifacts: dict[str, str],
) -> dict[str, object]:
    profile_config = scenario["profile"]
    include_interaction_types = set(profile_config["include_interaction_types"])
    selected_events = [event for event in events if str(event["interaction_type"]) in include_interaction_types]
    if not selected_events:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} selected no events for BL-004")

    numeric_columns = profile_config["numeric_feature_columns"]
    numeric_sums = {column: 0.0 for column in numeric_columns}
    numeric_weights = {column: 0.0 for column in numeric_columns}
    tag_weights: dict[str, float] = {}
    genre_weights: dict[str, float] = {}
    lead_genre_weights: dict[str, float] = {}
    seed_trace_rows: list[dict[str, object]] = []
    missing_track_ids: list[str] = []
    counts_by_type = {"history": 0, "influence": 0}
    weight_by_type = {"history": 0.0, "influence": 0.0}

    user_ids = {str(event["user_id"]) for event in selected_events}
    if len(user_ids) != 1:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} expected one user_id, got {sorted(user_ids)}")
    user_id = next(iter(user_ids))

    for event in selected_events:
        track_id = str(event["track_id"])
        candidate = candidate_rows_by_id.get(track_id)
        if candidate is None:
            missing_track_ids.append(track_id)
            continue

        interaction_type = str(event["interaction_type"])
        preference_weight = float(event["preference_weight"])
        effective_weight = preference_weight

        counts_by_type[interaction_type] = counts_by_type.get(interaction_type, 0) + 1
        weight_by_type[interaction_type] = weight_by_type.get(interaction_type, 0.0) + effective_weight

        for column in numeric_columns:
            value = parse_float(candidate.get(column, ""))
            if value is None:
                continue
            numeric_sums[column] += value * effective_weight
            numeric_weights[column] += effective_weight

        for tag, score in candidate_weight_pairs(candidate, "tags"):
            tag_weights[tag] = tag_weights.get(tag, 0.0) + (effective_weight * score)

        for genre, score in candidate_weight_pairs(candidate, "genres"):
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
                "interaction_count": int(event["interaction_count"]),
                "preference_weight": round(preference_weight, 6),
                "effective_weight": round(effective_weight, 6),
                "lead_genre": lead_genre,
                "top_tag": str(event.get("top_tag", "")),
                "candidate_playcount_sum": int(float(candidate.get("playcount_sum") or "0")),
                "candidate_listener_rows": int(float(candidate.get("listener_rows") or "0")),
            }
        )

    if missing_track_ids:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} missing candidate rows for track_ids: {missing_track_ids}")

    seed_trace_rows.sort(key=lambda row: int(row["seed_rank"]))
    numeric_profile: dict[str, float] = {}
    for column in numeric_columns:
        if numeric_weights[column] > 0:
            numeric_profile[column] = round(numeric_sums[column] / numeric_weights[column], 6)

    total_effective_weight = round(sum(weight_by_type.values()), 6)
    run_timestamp = datetime.now(timezone.utc)
    run_id = f"BL011-{scenario['scenario_id'].upper()}-BL004-{run_timestamp.strftime('%Y%m%d-%H%M%S-%f')}"

    profile = {
        "run_id": run_id,
        "task": "BL-004",
        "generated_at_utc": run_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user_id": user_id,
        "scenario_id": scenario["scenario_id"],
        "input_artifacts": {
            "aligned_events_path": input_artifacts["aligned_events_path"],
            "candidate_stub_path": input_artifacts["candidate_stub_path"],
        },
        "config": {
            "effective_weight_rule": profile_config["effective_weight_rule"],
            "numeric_feature_columns": profile_config["numeric_feature_columns"],
            "top_tag_limit": profile_config["top_tag_limit"],
            "top_genre_limit": profile_config["top_genre_limit"],
            "top_lead_genre_limit": profile_config["top_lead_genre_limit"],
            "aggregation_rules": profile_config["aggregation_rules"],
            "include_interaction_types": list(profile_config["include_interaction_types"]),
        },
        "diagnostics": {
            "events_total": len(selected_events),
            "matched_seed_count": len(seed_trace_rows),
            "missing_seed_count": len(missing_track_ids),
            "missing_track_ids": missing_track_ids,
            "candidate_rows_total": len(candidate_rows_by_id),
            "total_effective_weight": total_effective_weight,
            "weight_by_interaction_type": {key: round(value, 6) for key, value in weight_by_type.items() if value > 0},
        },
        "seed_summary": {
            "counts_by_interaction_type": {key: value for key, value in counts_by_type.items() if value > 0},
            "matched_track_ids": [row["track_id"] for row in seed_trace_rows],
        },
        "numeric_feature_profile": numeric_profile,
        "semantic_profile": {
            "top_tags": sorted_weight_map(tag_weights, int(profile_config["top_tag_limit"])),
            "top_genres": sorted_weight_map(genre_weights, int(profile_config["top_genre_limit"])),
            "top_lead_genres": sorted_weight_map(lead_genre_weights, int(profile_config["top_lead_genre_limit"])),
        },
    }

    summary = {
        "run_id": run_id,
        "scenario_id": scenario["scenario_id"],
        "matched_seed_count": len(seed_trace_rows),
        "total_effective_weight": total_effective_weight,
        "dominant_lead_genres": [item["label"] for item in profile["semantic_profile"]["top_lead_genres"][:5]],
        "dominant_tags": [item["label"] for item in profile["semantic_profile"]["top_tags"][:5]],
        "dominant_genres": [item["label"] for item in profile["semantic_profile"]["top_genres"][:5]],
        "feature_centers": {key: numeric_profile[key] for key in ["rhythm.bpm", "rhythm.danceability", "lowlevel.loudness_ebu128.integrated", "V_mean", "A_mean", "D_mean"] if key in numeric_profile},
    }

    seed_trace_fields = list(seed_trace_rows[0].keys())
    profile_text = json_text(profile)
    summary_text = json_text(summary)
    seed_trace_text = csv_text(seed_trace_fields, seed_trace_rows)

    return {
        "profile": profile,
        "summary": summary,
        "seed_trace_rows": seed_trace_rows,
        "texts": {
            "bl004_preference_profile.json": profile_text,
            "bl004_profile_summary.json": summary_text,
            "bl004_seed_trace.csv": seed_trace_text,
        },
        "stable_hashes": {
            "profile_semantic_hash": canonical_json_hash(
                {
                    "user_id": profile["user_id"],
                    "config": profile["config"],
                    "diagnostics": {
                        "events_total": profile["diagnostics"]["events_total"],
                        "matched_seed_count": profile["diagnostics"]["matched_seed_count"],
                        "missing_seed_count": profile["diagnostics"]["missing_seed_count"],
                        "candidate_rows_total": profile["diagnostics"]["candidate_rows_total"],
                        "total_effective_weight": profile["diagnostics"]["total_effective_weight"],
                        "weight_by_interaction_type": profile["diagnostics"]["weight_by_interaction_type"],
                    },
                    "seed_summary": profile["seed_summary"],
                    "numeric_feature_profile": profile["numeric_feature_profile"],
                    "semantic_profile": profile["semantic_profile"],
                    "summary": {
                        "matched_seed_count": summary["matched_seed_count"],
                        "total_effective_weight": summary["total_effective_weight"],
                        "dominant_lead_genres": summary["dominant_lead_genres"],
                        "dominant_tags": summary["dominant_tags"],
                        "dominant_genres": summary["dominant_genres"],
                        "feature_centers": summary["feature_centers"],
                    },
                }
            ),
            "seed_trace_hash": sha256_of_text(seed_trace_text),
        },
    }


def execute_retrieval_stage(
    profile_stage: dict[str, object],
    candidate_rows: list[dict[str, str]],
    scenario: dict[str, object],
) -> dict[str, object]:
    retrieval_config = scenario["retrieval"]
    profile = profile_stage["profile"]
    seed_trace_rows = profile_stage["seed_trace_rows"]

    seed_track_ids = {str(row["track_id"]) for row in seed_trace_rows}
    top_lead_genres = {item["label"] for item in profile["semantic_profile"]["top_lead_genres"][: int(retrieval_config["top_lead_genre_limit"])]}
    top_tags = {item["label"] for item in profile["semantic_profile"]["top_tags"][: int(retrieval_config["top_tag_limit"])]}
    top_genres = {item["label"] for item in profile["semantic_profile"]["top_genres"][: int(retrieval_config["top_genre_limit"])]}

    scaled_thresholds = {
        key: round(float(value) * float(retrieval_config["threshold_scale"]), 6)
        for key, value in retrieval_config["numeric_thresholds"].items()
    }
    numeric_centers = {key: float(value) for key, value in profile["numeric_feature_profile"].items() if key in scaled_thresholds}
    keep_rule = str(retrieval_config.get("keep_rule", "")).lower()

    decisions: list[dict[str, object]] = []
    kept_rows: list[dict[str, str]] = []
    decision_counts = {"seed_excluded": 0, "semantic_and_numeric_keep": 0, "rejected_threshold": 0}
    semantic_rule_hits = {"lead_genre_match": 0, "genre_overlap": 0, "tag_overlap": 0}
    numeric_rule_hits = {key: 0 for key in scaled_thresholds}

    for row in candidate_rows:
        track_id = row["track_id"]
        is_seed_track = track_id in seed_track_ids
        candidate_genres = candidate_labels(row, "genres")
        candidate_tags = candidate_labels(row, "tags")
        lead_genre = candidate_tags[0] if candidate_tags else (candidate_genres[0] if candidate_genres else "")

        lead_genre_match = lead_genre in top_lead_genres if lead_genre else False
        genre_overlap = len(top_genres.intersection(candidate_genres))
        tag_overlap = len(top_tags.intersection(candidate_tags))

        if lead_genre_match:
            semantic_rule_hits["lead_genre_match"] += 1
        if genre_overlap > 0:
            semantic_rule_hits["genre_overlap"] += 1
        if tag_overlap > 0:
            semantic_rule_hits["tag_overlap"] += 1

        semantic_score = (1 if lead_genre_match else 0) + (1 if genre_overlap > 0 else 0) + (1 if tag_overlap > 0 else 0)

        numeric_pass_count = 0
        numeric_distances: dict[str, float | None] = {}
        for column, threshold in scaled_thresholds.items():
            value = parse_float(row.get(column, ""))
            if value is None:
                numeric_distances[column] = None
                continue
            center = numeric_centers.get(column)
            if center is None:
                numeric_distances[column] = None
                continue
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
            if "semantic_score >= 2 or" in keep_rule:
                kept = semantic_score >= 2 or (semantic_score >= 1 and numeric_pass_count >= 1)
            else:
                kept = ((semantic_score >= 2 and numeric_pass_count >= 4) or (semantic_score == 3 and numeric_pass_count >= 3))

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
            "decision": "keep" if kept else "reject",
            "decision_reason": decision_reason(is_seed_track, semantic_score, numeric_pass_count, kept),
        }
        for column in sorted(scaled_thresholds):
            decision_row[f"{column}_distance"] = numeric_distances.get(column)
        decisions.append(decision_row)
        if kept:
            kept_rows.append(row)

    diagnostics = {
        "run_id": f"BL011-{scenario['scenario_id'].upper()}-BL005-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-005",
        "scenario_id": scenario["scenario_id"],
        "config": {
            "top_lead_genre_limit": retrieval_config["top_lead_genre_limit"],
            "top_tag_limit": retrieval_config["top_tag_limit"],
            "top_genre_limit": retrieval_config["top_genre_limit"],
            "threshold_scale": retrieval_config["threshold_scale"],
            "numeric_thresholds": scaled_thresholds,
            "keep_rule": retrieval_config["keep_rule"],
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
    }

    filtered_fields = list(candidate_rows[0].keys())
    decisions_fields = list(decisions[0].keys())
    filtered_text = csv_text(filtered_fields, kept_rows)
    decisions_text = csv_text(decisions_fields, decisions)
    diagnostics_text = json_text(diagnostics)

    return {
        "kept_rows": kept_rows,
        "decisions": decisions,
        "diagnostics": diagnostics,
        "texts": {
            "bl005_filtered_candidates.csv": filtered_text,
            "bl005_candidate_decisions.csv": decisions_text,
            "bl005_candidate_diagnostics.json": diagnostics_text,
        },
        "stable_hashes": {
            "filtered_candidates_hash": sha256_of_text(filtered_text),
            "candidate_decisions_hash": sha256_of_text(decisions_text),
        },
    }


def execute_scoring_stage(profile_stage: dict[str, object], retrieval_stage: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    scoring_config = scenario["scoring"]
    profile = profile_stage["profile"]
    candidates = retrieval_stage["kept_rows"]
    if not candidates:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} has no BL-005 candidates for BL-006")

    raw_component_weights = (
        scoring_config.get("component_weights")
        or scoring_config.get("active_component_weights")
        or scoring_config.get("base_component_weights")
        or {}
    )
    component_weights = {key: float(value) for key, value in raw_component_weights.items()}
    if not component_weights:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} has no scoring component weights")
    if abs(sum(component_weights.values()) - 1.0) > 1e-4:
        raise RuntimeError(f"Scenario {scenario['scenario_id']} scoring weights must sum to 1.0")

    numeric_thresholds = {key: float(value) for key, value in scoring_config["numeric_thresholds"].items()}
    numeric_components = [key for key in numeric_thresholds if key in component_weights]
    profile_lead_map, profile_lead_total = normalize_weight_map(profile["semantic_profile"]["top_lead_genres"], top_k=6)
    profile_genre_map, profile_genre_total = normalize_weight_map(profile["semantic_profile"]["top_genres"], top_k=8)
    profile_tag_map, profile_tag_total = normalize_weight_map(profile["semantic_profile"]["top_tags"], top_k=10)

    scored_rows: list[dict[str, object]] = []
    component_totals = {component: 0.0 for component in component_weights}

    for row in candidates:
        lead_genres = candidate_labels(row, "genres")
        candidate_tags = candidate_labels(row, "tags")
        lead_genre = candidate_tags[0] if candidate_tags else (lead_genres[0] if lead_genres else "")

        component_similarity: dict[str, float] = {}
        component_contribution: dict[str, float] = {}

        for column in numeric_components:
            threshold = float(numeric_thresholds[column])
            value = parse_float(row.get(column, ""))
            center = float(profile["numeric_feature_profile"][column])
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
        component_contribution["lead_genre"] = round(lead_genre_similarity * component_weights["lead_genre"], 6)

        genre_overlap_similarity, matched_genres = weighted_overlap(lead_genres, profile_genre_map, profile_genre_total)
        tag_overlap_similarity, matched_tags = weighted_overlap(candidate_tags, profile_tag_map, profile_tag_total)
        component_similarity["genre_overlap"] = genre_overlap_similarity
        component_contribution["genre_overlap"] = round(genre_overlap_similarity * component_weights["genre_overlap"], 6)
        component_similarity["tag_overlap"] = tag_overlap_similarity
        component_contribution["tag_overlap"] = round(tag_overlap_similarity * component_weights["tag_overlap"], 6)

        final_score = round(sum(component_contribution.values()), 6)
        for key, value in component_contribution.items():
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

    scored_rows.sort(key=lambda item: (-float(item["final_score"]), str(item["track_id"])))
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
    score_values = [float(row["final_score"]) for row in scored_rows]
    summary = {
        "run_id": f"BL011-{scenario['scenario_id'].upper()}-BL006-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-006",
        "scenario_id": scenario["scenario_id"],
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
            key: round(component_totals[key] / len(scored_rows), 6)
            for key in component_totals
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


def execute_playlist_stage(scoring_stage: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    assembly_config = scenario["assembly"]
    candidates = scoring_stage["scored_rows"]

    playlist: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []
    rule_hits = {"R1_score_threshold": 0, "R2_genre_cap": 0, "R3_consecutive_run": 0, "R4_length_cap": 0}

    for cand in candidates:
        track_id = str(cand["track_id"])
        lead_genre = str(cand["lead_genre"])
        final_score = float(cand["final_score"])
        score_rank = int(cand["rank"])
        decision = "included"
        exclusion_reason = ""

        if len(playlist) >= int(assembly_config["target_size"]):
            decision = "excluded"
            exclusion_reason = "length_cap_reached"
            rule_hits["R4_length_cap"] += 1
        elif final_score < float(assembly_config["min_score_threshold"]):
            decision = "excluded"
            exclusion_reason = "below_score_threshold"
            rule_hits["R1_score_threshold"] += 1
        elif sum(1 for track in playlist if track["lead_genre"] == lead_genre) >= int(assembly_config["max_per_genre"]):
            decision = "excluded"
            exclusion_reason = "genre_cap_exceeded"
            rule_hits["R2_genre_cap"] += 1
        elif len(playlist) >= int(assembly_config["max_consecutive"]) and all(
            track["lead_genre"] == lead_genre for track in playlist[-int(assembly_config["max_consecutive"]):]
        ):
            decision = "excluded"
            exclusion_reason = "consecutive_genre_run"
            rule_hits["R3_consecutive_run"] += 1

        playlist_position: int | str = ""
        if decision == "included":
            playlist_position = len(playlist) + 1
            playlist.append(
                {
                    "playlist_position": playlist_position,
                    "track_id": track_id,
                    "lead_genre": lead_genre,
                    "final_score": round(final_score, 6),
                    "score_rank": score_rank,
                }
            )

        trace_rows.append(
            {
                "score_rank": score_rank,
                "track_id": track_id,
                "lead_genre": lead_genre,
                "final_score": round(final_score, 6),
                "decision": decision,
                "playlist_position": playlist_position,
                "exclusion_reason": exclusion_reason,
            }
        )

    playlist_obj = {
        "run_id": f"BL011-{scenario['scenario_id'].upper()}-BL007-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-007",
        "scenario_id": scenario["scenario_id"],
        "config": dict(assembly_config),
        "playlist_length": len(playlist),
        "tracks": playlist,
    }
    report = {
        "run_id": playlist_obj["run_id"],
        "task": "BL-007",
        "scenario_id": scenario["scenario_id"],
        "config": dict(assembly_config),
        "counts": {
            "candidates_evaluated": len(candidates),
            "tracks_included": len(playlist),
            "tracks_excluded": len(trace_rows) - len(playlist),
        },
        "rule_hits": rule_hits,
        "playlist_genre_mix": {
            genre: sum(1 for track in playlist if track["lead_genre"] == genre)
            for genre in sorted({track["lead_genre"] for track in playlist})
        },
        "playlist_score_range": {
            "max": round(max(float(track["final_score"]) for track in playlist), 6) if playlist else 0.0,
            "min": round(min(float(track["final_score"]) for track in playlist), 6) if playlist else 0.0,
        },
    }

    playlist_text = json_text(playlist_obj)
    trace_text = csv_text(["score_rank", "track_id", "lead_genre", "final_score", "decision", "playlist_position", "exclusion_reason"], trace_rows)
    report_text = json_text(report)

    return {
        "playlist": playlist_obj,
        "trace_rows": trace_rows,
        "report": report,
        "texts": {
            "bl007_playlist.json": playlist_text,
            "bl007_assembly_trace.csv": trace_text,
            "bl007_assembly_report.json": report_text,
        },
        "stable_hashes": {
            "assembly_trace_hash": sha256_of_text(trace_text),
            "playlist_output_hash": canonical_json_hash(playlist_obj["tracks"]),
        },
    }


def execute_scenario(
    scenario: dict[str, object],
    events: list[dict[str, object]],
    candidate_rows: list[dict[str, str]],
    candidate_rows_by_id: dict[str, dict[str, str]],
    root: Path,
    input_artifacts: dict[str, str],
) -> dict[str, object]:
    profile_stage = execute_profile_stage(events, candidate_rows_by_id, scenario, root, input_artifacts)
    retrieval_stage = execute_retrieval_stage(profile_stage, candidate_rows, scenario)
    scoring_stage = execute_scoring_stage(profile_stage, retrieval_stage, scenario)
    playlist_stage = execute_playlist_stage(scoring_stage, scenario)

    ranked_rows = scoring_stage["scored_rows"]
    playlist_tracks = playlist_stage["playlist"]["tracks"]
    rank_map = {str(row["track_id"]): int(row["rank"]) for row in ranked_rows}
    top10_ids = [str(row["track_id"]) for row in ranked_rows[:10]]
    playlist_ids = [str(track["track_id"]) for track in playlist_tracks]

    effective_config = {
        "scenario_id": scenario["scenario_id"],
        "test_id": scenario["test_id"],
        "control_surface": scenario["control_surface"],
        "description": scenario["description"],
        "expected_effect": scenario["expected_effect"],
        "profile": profile_stage["profile"]["config"],
        "retrieval": retrieval_stage["diagnostics"]["config"],
        "scoring": scoring_stage["summary"]["config"],
        "assembly": playlist_stage["playlist"]["config"],
    }

    texts = {}
    texts.update(profile_stage["texts"])
    texts.update(retrieval_stage["texts"])
    texts.update(scoring_stage["texts"])
    texts.update(playlist_stage["texts"])

    stable_hashes = {}
    stable_hashes.update(profile_stage["stable_hashes"])
    stable_hashes.update(retrieval_stage["stable_hashes"])
    stable_hashes.update(scoring_stage["stable_hashes"])
    stable_hashes.update(playlist_stage["stable_hashes"])

    return {
        "scenario_id": scenario["scenario_id"],
        "test_id": scenario["test_id"],
        "control_surface": scenario["control_surface"],
        "description": scenario["description"],
        "expected_effect": scenario["expected_effect"],
        "effective_config": effective_config,
        "config_hash": canonical_json_hash(effective_config),
        "texts": texts,
        "stable_hashes": stable_hashes,
        "metrics": {
            "selected_event_count": profile_stage["profile"]["diagnostics"]["events_total"],
            "matched_seed_count": profile_stage["profile"]["diagnostics"]["matched_seed_count"],
            "candidate_pool_size": retrieval_stage["diagnostics"]["counts"]["kept_candidates"],
            "scored_candidate_count": scoring_stage["summary"]["counts"]["candidates_scored"],
            "playlist_length": playlist_stage["playlist"]["playlist_length"],
            "top10_track_ids": top10_ids,
            "playlist_track_ids": playlist_ids,
            "dominant_lead_genres": profile_stage["summary"]["dominant_lead_genres"],
            "dominant_tags": profile_stage["summary"]["dominant_tags"],
            "mean_component_contributions": scoring_stage["summary"]["mean_component_contributions"],
            "playlist_genre_mix": playlist_stage["report"]["playlist_genre_mix"],
            "rank_map": rank_map,
        },
    }


def write_scenario_outputs(output_dir: Path, scenario_result: dict[str, object]) -> None:
    scenario_dir = output_dir / "scenarios" / str(scenario_result["scenario_id"])
    scenario_dir.mkdir(parents=True, exist_ok=True)
    for filename, text in scenario_result["texts"].items():
        write_text(scenario_dir / filename, text)
    config_path = scenario_dir / "scenario_effective_config.json"
    write_text(config_path, json_text(scenario_result["effective_config"]))


def build_rank_shift_summary(baseline_rank_map: dict[str, int], scenario_rank_map: dict[str, int]) -> dict[str, object]:
    common_ids = sorted(set(baseline_rank_map).intersection(scenario_rank_map))
    if not common_ids:
        return {
            "common_candidate_count": 0,
            "mean_abs_rank_delta": 0.0,
            "max_rank_improvement": 0,
            "max_rank_drop": 0,
            "top_risers": [],
            "top_fallers": [],
        }

    deltas = []
    for track_id in common_ids:
        baseline_rank = baseline_rank_map[track_id]
        scenario_rank = scenario_rank_map[track_id]
        delta = baseline_rank - scenario_rank
        deltas.append({
            "track_id": track_id,
            "baseline_rank": baseline_rank,
            "scenario_rank": scenario_rank,
            "rank_delta": delta,
        })

    mean_abs_rank_delta = round(sum(abs(item["rank_delta"]) for item in deltas) / len(deltas), 3)
    top_risers = sorted([item for item in deltas if item["rank_delta"] > 0], key=lambda item: (-item["rank_delta"], item["track_id"]))[:5]
    top_fallers = sorted([item for item in deltas if item["rank_delta"] < 0], key=lambda item: (item["rank_delta"], item["track_id"]))[:5]

    return {
        "common_candidate_count": len(common_ids),
        "mean_abs_rank_delta": mean_abs_rank_delta,
        "max_rank_improvement": max((item["rank_delta"] for item in deltas), default=0),
        "max_rank_drop": min((item["rank_delta"] for item in deltas), default=0),
        "top_risers": top_risers,
        "top_fallers": top_fallers,
    }


def compare_to_baseline(baseline_result: dict[str, object], scenario_result: dict[str, object]) -> dict[str, object]:
    baseline_metrics = baseline_result["metrics"]
    scenario_metrics = scenario_result["metrics"]
    baseline_top10 = baseline_metrics["top10_track_ids"]
    scenario_top10 = scenario_metrics["top10_track_ids"]
    baseline_playlist = baseline_metrics["playlist_track_ids"]
    scenario_playlist = scenario_metrics["playlist_track_ids"]

    top10_overlap = sorted(set(baseline_top10).intersection(scenario_top10))
    playlist_overlap = sorted(set(baseline_playlist).intersection(scenario_playlist))
    component_delta = {
        key: round(float(scenario_metrics["mean_component_contributions"].get(key, 0.0)) - float(baseline_metrics["mean_component_contributions"].get(key, 0.0)), 6)
        for key in sorted(set(baseline_metrics["mean_component_contributions"]).union(scenario_metrics["mean_component_contributions"]))
    }
    rank_shift_summary = build_rank_shift_summary(baseline_metrics["rank_map"], scenario_metrics["rank_map"])

    observable_shift = any(
        [
            scenario_metrics["candidate_pool_size"] != baseline_metrics["candidate_pool_size"],
            scenario_metrics["playlist_track_ids"] != baseline_metrics["playlist_track_ids"],
            scenario_metrics["top10_track_ids"] != baseline_metrics["top10_track_ids"],
            rank_shift_summary["mean_abs_rank_delta"] > 0,
            scenario_result["stable_hashes"]["profile_semantic_hash"] != baseline_result["stable_hashes"]["profile_semantic_hash"],
        ]
    )

    expected_direction_met = None
    scenario_id = str(scenario_result["scenario_id"])
    if scenario_id == "no_influence_tracks":
        expected_direction_met = scenario_result["stable_hashes"]["profile_semantic_hash"] != baseline_result["stable_hashes"]["profile_semantic_hash"] and observable_shift
    elif scenario_id == "valence_weight_up":
        override_component = str(scenario_result["effective_config"]["scoring"].get("weight_override_component") or "")
        expected_direction_met = component_delta.get(override_component, 0.0) > 0 and rank_shift_summary["mean_abs_rank_delta"] > 0
    elif scenario_id == "stricter_thresholds":
        expected_direction_met = scenario_metrics["candidate_pool_size"] < baseline_metrics["candidate_pool_size"]
    elif scenario_id == "looser_thresholds":
        expected_direction_met = scenario_metrics["candidate_pool_size"] > baseline_metrics["candidate_pool_size"]

    return {
        "observable_shift": observable_shift,
        "expected_direction_met": expected_direction_met,
        "candidate_pool_size_delta": scenario_metrics["candidate_pool_size"] - baseline_metrics["candidate_pool_size"],
        "playlist_length_delta": scenario_metrics["playlist_length"] - baseline_metrics["playlist_length"],
        "top10_overlap_count": len(top10_overlap),
        "top10_overlap_ratio": round(len(top10_overlap) / max(len(baseline_top10), 1), 3),
        "playlist_overlap_count": len(playlist_overlap),
        "playlist_overlap_ratio": round(len(playlist_overlap) / max(len(baseline_playlist), 1), 3),
        "top10_added_track_ids": [track_id for track_id in scenario_top10 if track_id not in baseline_top10],
        "top10_removed_track_ids": [track_id for track_id in baseline_top10 if track_id not in scenario_top10],
        "playlist_added_track_ids": [track_id for track_id in scenario_playlist if track_id not in baseline_playlist],
        "playlist_removed_track_ids": [track_id for track_id in baseline_playlist if track_id not in scenario_playlist],
        "profile_lead_genres_before": baseline_metrics["dominant_lead_genres"],
        "profile_lead_genres_after": scenario_metrics["dominant_lead_genres"],
        "component_mean_delta": component_delta,
        "rank_shift_summary": rank_shift_summary,
    }


def main() -> None:
    root = repo_root()
    paths = build_paths(root)
    ensure_required_inputs(paths, root)
    legacy_mode = resolve_legacy_mode(paths)

    output_dir = paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "scenarios").mkdir(parents=True, exist_ok=True)

    baseline_snapshot = load_json(paths["baseline_snapshot"])
    if legacy_mode:
        events = load_jsonl(paths["legacy_events"])
        candidate_rows = [normalize_candidate_row(row) for row in load_csv_rows(paths["legacy_candidates"])]
        input_artifacts = {
            "aligned_events_path": relpath(paths["legacy_events"], root),
            "candidate_stub_path": relpath(paths["legacy_candidates"], root),
        }
    else:
        seed_rows = load_csv_rows(paths["active_seed_trace"])
        events = []
        for idx, row in enumerate(seed_rows, start=1):
            events.append(
                {
                    "event_id": str(row.get("event_id") or f"seed_event_{idx:06d}"),
                    "track_id": str(row.get("track_id", "")),
                    "interaction_type": str(row.get("interaction_type") or "history"),
                    "signal_source": str(row.get("signal_source") or "seed_trace"),
                    "seed_rank": int(float(row.get("interaction_count") or idx)),
                    "interaction_count": int(float(row.get("interaction_count") or 1)),
                    "preference_weight": float(row.get("preference_weight") or row.get("effective_weight") or 1.0),
                    "user_id": str(row.get("user_id") or "active_user"),
                    "lead_genre": str(row.get("lead_genre") or ""),
                    "top_tag": str(row.get("top_tag") or ""),
                }
            )
        candidate_rows = [normalize_candidate_row(row) for row in load_csv_rows(paths["active_candidates"])]
        input_artifacts = {
            "aligned_events_path": relpath(paths["active_seed_trace"], root),
            "candidate_stub_path": relpath(paths["active_candidates"], root),
        }

    candidate_rows_by_id = {row["track_id"]: row for row in candidate_rows}

    baseline_config_hash = canonical_json_hash(baseline_snapshot)
    scenarios = build_scenarios(baseline_snapshot)

    fixed_inputs = {
        input_artifacts["aligned_events_path"]: sha256_of_file(paths["legacy_events"] if legacy_mode else paths["active_seed_trace"]),
        input_artifacts["candidate_stub_path"]: sha256_of_file(paths["legacy_candidates"] if legacy_mode else paths["active_candidates"]),
    }
    optional_inputs = {
        "legacy_manifest": paths["legacy_manifest"],
        "legacy_coverage": paths["legacy_coverage"],
    }
    for key, path in optional_inputs.items():
        if path.exists():
            fixed_inputs[relpath(path, root)] = sha256_of_file(path)

    config_snapshot = {
        "task": "BL-011",
        "generated_from": relpath(paths["baseline_snapshot"], root),
        "baseline_config_hash": baseline_config_hash,
        "input_source": "legacy_surrogate_assets" if legacy_mode else "active_pipeline_outputs",
        "fixed_inputs": fixed_inputs,
        "optional_dependency_availability": {
            key: {
                "path": relpath(path, root),
                "available": path.exists(),
            }
            for key, path in optional_inputs.items()
        },
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
    }
    config_snapshot_path = output_dir / "bl011_controllability_config_snapshot.json"
    write_text(config_snapshot_path, json_text(config_snapshot))

    run_started = time.time()
    run_id = f"BL011-CTRL-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    scenario_records: list[dict[str, object]] = []

    for scenario in scenarios:
        first_run = execute_scenario(scenario, events, candidate_rows, candidate_rows_by_id, root, input_artifacts)
        second_run = execute_scenario(scenario, events, candidate_rows, candidate_rows_by_id, root, input_artifacts)
        repeat_consistent = first_run["stable_hashes"] == second_run["stable_hashes"]
        write_scenario_outputs(output_dir, first_run)

        scenario_dir = output_dir / "scenarios" / str(first_run["scenario_id"])
        scenario_records.append(
            {
                **first_run,
                "repeat_consistent": repeat_consistent,
                "archive_dir": relpath(scenario_dir, root),
            }
        )

    baseline_result = next(record for record in scenario_records if record["scenario_id"] == "baseline")
    for record in scenario_records:
        if record["scenario_id"] == "baseline":
            record["comparison_to_baseline"] = {
                "observable_shift": False,
                "expected_direction_met": True,
                "candidate_pool_size_delta": 0,
                "playlist_length_delta": 0,
                "top10_overlap_count": 10,
                "top10_overlap_ratio": 1.0,
                "playlist_overlap_count": baseline_result["metrics"]["playlist_length"],
                "playlist_overlap_ratio": 1.0,
                "top10_added_track_ids": [],
                "top10_removed_track_ids": [],
                "playlist_added_track_ids": [],
                "playlist_removed_track_ids": [],
                "profile_lead_genres_before": baseline_result["metrics"]["dominant_lead_genres"],
                "profile_lead_genres_after": baseline_result["metrics"]["dominant_lead_genres"],
                "component_mean_delta": {key: 0.0 for key in baseline_result["metrics"]["mean_component_contributions"]},
                "rank_shift_summary": build_rank_shift_summary(baseline_result["metrics"]["rank_map"], baseline_result["metrics"]["rank_map"]),
            }
        else:
            record["comparison_to_baseline"] = compare_to_baseline(baseline_result, record)

    matrix_rows = []
    for record in scenario_records:
        comparison = record["comparison_to_baseline"]
        matrix_rows.append(
            {
                "scenario_id": record["scenario_id"],
                "test_id": record["test_id"],
                "control_surface": record["control_surface"],
                "repeat_consistent": record["repeat_consistent"],
                "config_hash": record["config_hash"],
                "candidate_pool_size": record["metrics"]["candidate_pool_size"],
                "candidate_pool_size_delta": comparison["candidate_pool_size_delta"],
                "playlist_length": record["metrics"]["playlist_length"],
                "top10_overlap_count": comparison["top10_overlap_count"],
                "playlist_overlap_count": comparison["playlist_overlap_count"],
                "mean_abs_rank_delta": comparison["rank_shift_summary"]["mean_abs_rank_delta"],
                "observable_shift": comparison["observable_shift"],
                "expected_direction_met": comparison["expected_direction_met"],
                "profile_semantic_hash": record["stable_hashes"]["profile_semantic_hash"],
                "ranked_output_hash": record["stable_hashes"]["ranked_output_hash"],
                "playlist_output_hash": record["stable_hashes"]["playlist_output_hash"],
                "archive_dir": record["archive_dir"],
            }
        )

    run_matrix_path = output_dir / "bl011_controllability_run_matrix.csv"
    write_text(run_matrix_path, csv_text(list(matrix_rows[0].keys()), matrix_rows))

    scenario_report_records = []
    for record in scenario_records:
        scenario_report_records.append(
            {
                "scenario_id": record["scenario_id"],
                "test_id": record["test_id"],
                "control_surface": record["control_surface"],
                "description": record["description"],
                "expected_effect": record["expected_effect"],
                "repeat_consistent": record["repeat_consistent"],
                "config_hash": record["config_hash"],
                "effective_config": record["effective_config"],
                "stable_hashes": record["stable_hashes"],
                "metrics": {
                    key: value for key, value in record["metrics"].items() if key != "rank_map"
                },
                "comparison_to_baseline": record["comparison_to_baseline"],
                "archive_dir": record["archive_dir"],
            }
        )

    non_baseline_records = [record for record in scenario_records if record["scenario_id"] != "baseline"]
    report = {
        "run_metadata": {
            "run_id": run_id,
            "task": "BL-011",
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "elapsed_seconds": round(time.time() - run_started, 3),
            "baseline_config_hash": baseline_config_hash,
            "scenario_count": len(scenario_records),
        },
        "inputs": {
            "baseline_snapshot_path": relpath(paths["baseline_snapshot"], root),
            "controllability_config_snapshot_path": relpath(config_snapshot_path, root),
            "fixed_input_hashes": config_snapshot["fixed_inputs"],
        },
        "scope": {
            "evaluation_tests": ["EP-CTRL-001", "EP-CTRL-002", "EP-CTRL-003"],
            "scenario_ids": [record["scenario_id"] for record in scenario_records],
            "stage_scope": ["BL-004", "BL-005", "BL-006", "BL-007"],
            "repeat_method": "each scenario was executed twice with identical parameters and compared via stable stage hashes",
        },
        "scenario_results": scenario_report_records,
        "results": {
            "all_scenarios_repeat_consistent": all(record["repeat_consistent"] for record in scenario_records),
            "all_variant_shifts_observable": all(record["comparison_to_baseline"]["observable_shift"] for record in non_baseline_records),
            "all_variant_directions_met": all(record["comparison_to_baseline"]["expected_direction_met"] for record in non_baseline_records),
            "status": "pass" if all(record["repeat_consistent"] for record in scenario_records) and all(record["comparison_to_baseline"]["observable_shift"] for record in non_baseline_records) and all(record["comparison_to_baseline"]["expected_direction_met"] for record in non_baseline_records) else "bounded-risk",
        },
        "output_artifacts": {
            "config_snapshot_path": relpath(config_snapshot_path, root),
            "run_matrix_path": relpath(run_matrix_path, root),
            "scenario_dirs": [record["archive_dir"] for record in scenario_records],
        },
    }
    report_path = output_dir / "bl011_controllability_report.json"
    write_text(report_path, json_text(report))

    print("BL-011 controllability evaluation complete.")
    print(f"run_id={run_id}")
    print(f"status={report['results']['status']}")
    print(f"report={report_path}")
    print(f"run_matrix={run_matrix_path}")


if __name__ == "__main__":
    main()