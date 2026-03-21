from __future__ import annotations

import csv
import json
from pathlib import Path


CORE_GENRES = [
    "indie rock",
    "indie pop",
    "electronic",
    "trip hop",
    "alternative rock",
    "pop",
]

CONTRAST_GENRES = [
    "rap",
    "hip hop",
    "hard rock",
    "country",
    "folk",
    "pop punk",
]

HISTORY_TARGET = 8
INFLUENCE_TARGET = 3
CANDIDATE_TARGET = 60
CORE_CANDIDATE_TARGET = 45


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def parse_top_list(raw_value: str, key_name: str) -> list[str]:
    if not raw_value:
        return []
    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    values: list[str] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        value = item.get(key_name)
        if isinstance(value, str) and value.strip():
            values.append(value.strip())
    return values


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def has_full_coverage(row: dict[str, str]) -> bool:
    required_flags = [
        "has_user_track_counts",
        "has_essentia",
        "has_lyrics",
        "has_tags",
        "has_genres",
    ]
    return all(row.get(flag) == "1" for flag in required_flags)


def enriched_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    enriched: list[dict[str, object]] = []
    for row in rows:
        if not has_full_coverage(row):
            continue
        playcount_sum = int(row.get("playcount_sum") or "0")
        listener_rows = int(row.get("listener_rows") or "0")
        lead_genres = parse_top_list(row.get("top_genres_json", ""), "genre")
        top_tags = parse_top_list(row.get("top_tags_json", ""), "tag")
        enriched.append(
            {
                "row": row,
                "track_id": row["track_id"],
                "playcount_sum": playcount_sum,
                "listener_rows": listener_rows,
                "lead_genre": lead_genres[0] if lead_genres else "",
                "genre_list": lead_genres,
                "top_tag": top_tags[0] if top_tags else "",
                "tag_list": top_tags,
            }
        )
    enriched.sort(key=lambda item: (-int(item["playcount_sum"]), str(item["track_id"])))
    return enriched


def pick_by_genres(
    pool: list[dict[str, object]],
    genres: list[str],
    target_count: int,
    used_track_ids: set[str],
    prefer_distinct_genres: bool,
) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    used_genres: set[str] = set()

    if prefer_distinct_genres:
        for genre in genres:
            for item in pool:
                lead_genre = str(item["lead_genre"])
                track_id = str(item["track_id"])
                if track_id in used_track_ids or lead_genre != genre:
                    continue
                selected.append(item)
                used_track_ids.add(track_id)
                used_genres.add(lead_genre)
                break
            if len(selected) >= target_count:
                return selected

    for item in pool:
        lead_genre = str(item["lead_genre"])
        track_id = str(item["track_id"])
        if track_id in used_track_ids:
            continue
        if lead_genre not in genres:
            continue
        if prefer_distinct_genres and lead_genre in used_genres and len(used_genres) < len(genres):
            continue
        selected.append(item)
        used_track_ids.add(track_id)
        used_genres.add(lead_genre)
        if len(selected) >= target_count:
            break

    return selected


def write_candidate_stub(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_aligned_jsonl(path: Path, history: list[dict[str, object]], influence: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        seed_rank = 1

        history_max = max(int(item["playcount_sum"]) for item in history)
        for item in history:
            playcount_sum = int(item["playcount_sum"])
            payload = {
                "event_id": f"syn_evt_{seed_rank:03d}",
                "user_id": "synthetic_user_001",
                "track_id": str(item["track_id"]),
                "interaction_type": "history",
                "signal_source": "synthetic_history",
                "interaction_count": playcount_sum,
                "preference_weight": round(0.8 + (playcount_sum / history_max), 4),
                "seed_rank": seed_rank,
                "lead_genre": str(item["lead_genre"]),
                "top_tag": str(item["top_tag"]),
            }
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
            seed_rank += 1

        for item in influence:
            payload = {
                "event_id": f"syn_evt_{seed_rank:03d}",
                "user_id": "synthetic_user_001",
                "track_id": str(item["track_id"]),
                "interaction_type": "influence",
                "signal_source": "synthetic_influence",
                "interaction_count": max(1, int(item["listener_rows"])),
                "preference_weight": 1.35,
                "seed_rank": seed_rank,
                "lead_genre": str(item["lead_genre"]),
                "top_tag": str(item["top_tag"]),
            }
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
            seed_rank += 1


def main() -> None:
    root = repo_root()
    canonical_path = root / "07_implementation" / "implementation_notes" / "data_layer" / "outputs" / "onion_canonical_track_table.csv"
    output_dir = root / "07_implementation" / "implementation_notes" / "test_assets"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(canonical_path)
    pool = enriched_rows(rows)

    used_track_ids: set[str] = set()
    history = pick_by_genres(pool, CORE_GENRES, HISTORY_TARGET, used_track_ids, prefer_distinct_genres=True)
    influence = pick_by_genres(pool, CORE_GENRES, INFLUENCE_TARGET, used_track_ids, prefer_distinct_genres=False)

    candidate_items: list[dict[str, object]] = []
    candidate_items.extend(history)
    candidate_items.extend(influence)

    for item in pool:
        if len(candidate_items) >= CORE_CANDIDATE_TARGET:
            break
        track_id = str(item["track_id"])
        if track_id in used_track_ids:
            continue
        if str(item["lead_genre"]) not in CORE_GENRES:
            continue
        candidate_items.append(item)
        used_track_ids.add(track_id)

    for item in pool:
        if len(candidate_items) >= CANDIDATE_TARGET:
            break
        track_id = str(item["track_id"])
        if track_id in used_track_ids:
            continue
        if str(item["lead_genre"]) not in CONTRAST_GENRES:
            continue
        candidate_items.append(item)
        used_track_ids.add(track_id)

    if len(history) != HISTORY_TARGET:
        raise RuntimeError(f"Expected {HISTORY_TARGET} history tracks, got {len(history)}")
    if len(influence) != INFLUENCE_TARGET:
        raise RuntimeError(f"Expected {INFLUENCE_TARGET} influence tracks, got {len(influence)}")
    if len(candidate_items) < CANDIDATE_TARGET:
        raise RuntimeError(f"Expected at least {CANDIDATE_TARGET} candidate rows, got {len(candidate_items)}")

    candidate_rows = [dict(item["row"]) for item in candidate_items[:CANDIDATE_TARGET]]

    aligned_path = output_dir / "bl016_synthetic_aligned_events.jsonl"
    candidate_path = output_dir / "bl016_candidate_stub.csv"
    manifest_path = output_dir / "bl016_asset_manifest.json"

    write_aligned_jsonl(aligned_path, history, influence)
    write_candidate_stub(candidate_path, candidate_rows)

    manifest = {
        "task": "BL-016",
        "generated_from": str(canonical_path),
        "selection_rules": {
            "full_coverage_required": True,
            "history_target": HISTORY_TARGET,
            "influence_target": INFLUENCE_TARGET,
            "candidate_target": CANDIDATE_TARGET,
            "core_candidate_target": CORE_CANDIDATE_TARGET,
            "core_genres": CORE_GENRES,
            "contrast_genres": CONTRAST_GENRES,
            "sort_order": ["playcount_sum desc", "track_id asc"],
        },
        "history_track_ids": [str(item["track_id"]) for item in history],
        "influence_track_ids": [str(item["track_id"]) for item in influence],
        "candidate_track_ids": [row["track_id"] for row in candidate_rows],
        "summary": {
            "history_count": len(history),
            "influence_count": len(influence),
            "candidate_count": len(candidate_rows),
            "core_candidate_count": sum(1 for item in candidate_items[:CANDIDATE_TARGET] if str(item["lead_genre"]) in CORE_GENRES),
            "contrast_candidate_count": sum(1 for item in candidate_items[:CANDIDATE_TARGET] if str(item["lead_genre"]) in CONTRAST_GENRES),
        },
    }

    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=True)

    print("BL-016 synthetic assets created.")
    print(f"aligned_events={aligned_path}")
    print(f"candidate_stub={candidate_path}")
    print(f"manifest={manifest_path}")


if __name__ == "__main__":
    main()