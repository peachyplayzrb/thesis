from __future__ import annotations

import argparse
import ast
import bz2
import csv
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ESSENTIA_COLUMNS = [
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
]

LYRICS_COLUMNS = [
    "V_mean",
    "A_mean",
    "D_mean",
    "P_mean",
    "V_std",
    "A_std",
    "D_std",
]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    default_selected_dir = repo_root / "10_resources" / "datasets" / "music4all_onion" / "selected"
    default_output_dir = script_path.parent / "outputs"

    parser = argparse.ArgumentParser(
        description="BL-017: Build Onion-only canonical dataset layer with deterministic joins and quality checks."
    )
    parser.add_argument("--selected-dir", type=Path, default=default_selected_dir)
    parser.add_argument("--output-dir", type=Path, default=default_output_dir)
    parser.add_argument("--top-tags", type=int, default=10)
    parser.add_argument("--top-genres", type=int, default=8)
    parser.add_argument(
        "--max-user-track-rows",
        type=int,
        default=None,
        help="Optional cap for rows read from userid_trackid_count.tsv.bz2 (for smoke tests).",
    )
    parser.add_argument(
        "--max-track-rows-per-file",
        type=int,
        default=None,
        help="Optional cap for rows read from each id_* track matrix file (for smoke tests).",
    )
    return parser.parse_args()


def open_bz2_tsv(path: Path) -> Iterable[List[str]]:
    with bz2.open(path, mode="rt", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            yield row


def parse_float(value: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    return number


def parse_int(value: str) -> int | None:
    text = value.strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def normalize_tag_items(raw_payload: str) -> List[Tuple[str, float]]:
    payload = raw_payload.strip()
    if not payload:
        return []

    try:
        parsed = ast.literal_eval(payload)
    except Exception:
        return []

    pairs: List[Tuple[str, float]] = []
    if isinstance(parsed, dict):
        iterable = parsed.items()
    elif isinstance(parsed, (list, tuple)):
        iterable = parsed
    else:
        return []

    for item in iterable:
        if isinstance(item, tuple) and len(item) == 2:
            tag, weight = item
        elif isinstance(item, list) and len(item) == 2:
            tag, weight = item
        else:
            continue

        tag_text = str(tag).strip()
        if not tag_text:
            continue
        try:
            weight_value = float(weight)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(weight_value):
            continue
        pairs.append((tag_text, weight_value))

    pairs.sort(key=lambda item: (-item[1], item[0]))
    return pairs


def load_user_track_counts(path: Path, max_rows: int | None = None) -> Dict[str, Dict[str, int]]:
    rows = open_bz2_tsv(path)
    header = next(rows, None)
    if header is None:
        raise ValueError(f"Empty file: {path}")

    required = {"track_id", "count"}
    missing = required.difference(header)
    if missing:
        raise ValueError(f"Missing required columns in {path.name}: {sorted(missing)}")

    index = {name: i for i, name in enumerate(header)}
    result: Dict[str, Dict[str, int]] = {}

    processed = 0
    for row in rows:
        if max_rows is not None and processed >= max_rows:
            break
        if len(row) <= index["count"]:
            continue
        track_id = row[index["track_id"]].strip()
        if not track_id:
            continue

        count_value = parse_int(row[index["count"]])
        if count_value is None:
            continue

        if track_id not in result:
            result[track_id] = {"listener_rows": 0, "playcount_sum": 0}
        result[track_id]["listener_rows"] += 1
        result[track_id]["playcount_sum"] += count_value
        processed += 1

    return result


def load_selected_numeric_matrix(path: Path, selected_columns: List[str]) -> Tuple[Dict[str, Dict[str, float | None]], Dict[str, int]]:
    rows = open_bz2_tsv(path)
    header = next(rows, None)
    if header is None:
        raise ValueError(f"Empty file: {path}")
    if "id" not in header:
        raise ValueError(f"Missing id column in {path.name}")

    header_index = {name: i for i, name in enumerate(header)}
    missing_columns = [name for name in selected_columns if name not in header_index]
    if missing_columns:
        raise ValueError(f"Missing selected columns in {path.name}: {missing_columns}")

    id_index = header_index["id"]
    result: Dict[str, Dict[str, float | None]] = {}
    missing_by_column = {column: 0 for column in selected_columns}

    for row in rows:
        if len(row) <= id_index:
            continue
        track_id = row[id_index].strip()
        if not track_id:
            continue

        feature_values: Dict[str, float | None] = {}
        for column in selected_columns:
            idx = header_index[column]
            value = row[idx] if idx < len(row) else ""
            parsed = parse_float(value)
            if parsed is None:
                missing_by_column[column] += 1
            feature_values[column] = parsed
        result[track_id] = feature_values

    return result, missing_by_column


def load_selected_numeric_matrix_with_cap(
    path: Path,
    selected_columns: List[str],
    max_rows: int | None = None,
) -> Tuple[Dict[str, Dict[str, float | None]], Dict[str, int]]:
    rows = open_bz2_tsv(path)
    header = next(rows, None)
    if header is None:
        raise ValueError(f"Empty file: {path}")
    if "id" not in header:
        raise ValueError(f"Missing id column in {path.name}")

    header_index = {name: i for i, name in enumerate(header)}
    missing_columns = [name for name in selected_columns if name not in header_index]
    if missing_columns:
        raise ValueError(f"Missing selected columns in {path.name}: {missing_columns}")

    id_index = header_index["id"]
    result: Dict[str, Dict[str, float | None]] = {}
    missing_by_column = {column: 0 for column in selected_columns}

    processed = 0
    for row in rows:
        if max_rows is not None and processed >= max_rows:
            break
        if len(row) <= id_index:
            continue
        track_id = row[id_index].strip()
        if not track_id:
            continue

        feature_values: Dict[str, float | None] = {}
        for column in selected_columns:
            idx = header_index[column]
            value = row[idx] if idx < len(row) else ""
            parsed = parse_float(value)
            if parsed is None:
                missing_by_column[column] += 1
            feature_values[column] = parsed
        result[track_id] = feature_values
        processed += 1

    return result, missing_by_column


def load_tags(path: Path, top_k: int, max_rows: int | None = None) -> Dict[str, Dict[str, str | int]]:
    rows = open_bz2_tsv(path)
    header = next(rows, None)
    if header is None:
        raise ValueError(f"Empty file: {path}")
    if "id" not in header:
        raise ValueError(f"Missing id column in {path.name}")

    id_index = header.index("id")
    payload_index = 1 if len(header) > 1 else None
    if payload_index is None:
        raise ValueError(f"Missing tags payload column in {path.name}")

    result: Dict[str, Dict[str, str | int]] = {}
    processed = 0
    for row in rows:
        if max_rows is not None and processed >= max_rows:
            break
        if len(row) <= max(id_index, payload_index):
            continue
        track_id = row[id_index].strip()
        if not track_id:
            continue

        pairs = normalize_tag_items(row[payload_index])
        top_pairs = pairs[:top_k]
        top_payload = [{"tag": tag, "weight": weight} for tag, weight in top_pairs]
        result[track_id] = {
            "top_tags_json": json.dumps(top_payload, ensure_ascii=True, separators=(",", ":")),
            "tag_count": len(pairs),
        }
        processed += 1

    return result


def load_genres(path: Path, top_k: int, max_rows: int | None = None) -> Dict[str, Dict[str, str | int]]:
    rows = open_bz2_tsv(path)
    header = next(rows, None)
    if header is None:
        raise ValueError(f"Empty file: {path}")
    if "id" not in header:
        raise ValueError(f"Missing id column in {path.name}")

    id_index = header.index("id")
    genre_columns = [column for column in header if column != "id"]
    genre_indexes = [(header.index(column), column) for column in genre_columns]

    result: Dict[str, Dict[str, str | int]] = {}
    processed = 0
    for row in rows:
        if max_rows is not None and processed >= max_rows:
            break
        if len(row) <= id_index:
            continue
        track_id = row[id_index].strip()
        if not track_id:
            continue

        non_zero: List[Tuple[str, float]] = []
        for idx, column in genre_indexes:
            value = row[idx] if idx < len(row) else ""
            score = parse_float(value)
            if score is None or score <= 0:
                continue
            non_zero.append((column, score))

        non_zero.sort(key=lambda item: (-item[1], item[0]))
        top_genres = non_zero[:top_k]
        top_payload = [{"genre": genre, "score": score} for genre, score in top_genres]
        result[track_id] = {
            "top_genres_json": json.dumps(top_payload, ensure_ascii=True, separators=(",", ":")),
            "non_zero_genre_count": len(non_zero),
        }
        processed += 1

    return result


def value_for_csv(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    selected_dir = args.selected_dir
    required_files = {
        "user_track_counts": selected_dir / "userid_trackid_count.tsv.bz2",
        "essentia": selected_dir / "id_essentia.tsv.bz2",
        "lyrics": selected_dir / "id_lyrics_sentiment_functionals.tsv.bz2",
        "tags": selected_dir / "id_tags_dict.tsv.bz2",
        "genres": selected_dir / "id_genres_tf-idf.tsv.bz2",
    }

    missing_inputs = [str(path) for path in required_files.values() if not path.exists()]
    if missing_inputs:
        raise FileNotFoundError(f"Missing input files: {missing_inputs}")

    start_time = time.time()

    user_track_counts = load_user_track_counts(
        required_files["user_track_counts"],
        max_rows=args.max_user_track_rows,
    )
    essentia_data, essentia_missing = load_selected_numeric_matrix_with_cap(
        required_files["essentia"],
        ESSENTIA_COLUMNS,
        max_rows=args.max_track_rows_per_file,
    )
    lyrics_data, lyrics_missing = load_selected_numeric_matrix_with_cap(
        required_files["lyrics"],
        LYRICS_COLUMNS,
        max_rows=args.max_track_rows_per_file,
    )
    tags_data = load_tags(
        required_files["tags"],
        top_k=max(1, args.top_tags),
        max_rows=args.max_track_rows_per_file,
    )
    genres_data = load_genres(
        required_files["genres"],
        top_k=max(1, args.top_genres),
        max_rows=args.max_track_rows_per_file,
    )

    id_sets = {
        "user_track_counts": set(user_track_counts.keys()),
        "essentia": set(essentia_data.keys()),
        "lyrics": set(lyrics_data.keys()),
        "tags": set(tags_data.keys()),
        "genres": set(genres_data.keys()),
    }
    all_track_ids = sorted(set().union(*id_sets.values()))

    canonical_columns = [
        "track_id",
        "has_user_track_counts",
        "has_essentia",
        "has_lyrics",
        "has_tags",
        "has_genres",
        "listener_rows",
        "playcount_sum",
    ]
    canonical_columns.extend(ESSENTIA_COLUMNS)
    canonical_columns.extend(LYRICS_COLUMNS)
    canonical_columns.extend(["tag_count", "top_tags_json", "non_zero_genre_count", "top_genres_json"])

    canonical_path = args.output_dir / "onion_canonical_track_table.csv"
    availability_counts = {
        "has_user_track_counts": 0,
        "has_essentia": 0,
        "has_lyrics": 0,
        "has_tags": 0,
        "has_genres": 0,
    }

    with canonical_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(canonical_columns)

        for track_id in all_track_ids:
            has_user_track_counts = track_id in user_track_counts
            has_essentia = track_id in essentia_data
            has_lyrics = track_id in lyrics_data
            has_tags = track_id in tags_data
            has_genres = track_id in genres_data

            if has_user_track_counts:
                availability_counts["has_user_track_counts"] += 1
            if has_essentia:
                availability_counts["has_essentia"] += 1
            if has_lyrics:
                availability_counts["has_lyrics"] += 1
            if has_tags:
                availability_counts["has_tags"] += 1
            if has_genres:
                availability_counts["has_genres"] += 1

            row: List[object] = [
                track_id,
                int(has_user_track_counts),
                int(has_essentia),
                int(has_lyrics),
                int(has_tags),
                int(has_genres),
                user_track_counts.get(track_id, {}).get("listener_rows"),
                user_track_counts.get(track_id, {}).get("playcount_sum"),
            ]

            essentia_values = essentia_data.get(track_id, {})
            row.extend(essentia_values.get(column) for column in ESSENTIA_COLUMNS)

            lyrics_values = lyrics_data.get(track_id, {})
            row.extend(lyrics_values.get(column) for column in LYRICS_COLUMNS)

            tag_values = tags_data.get(track_id, {})
            genre_values = genres_data.get(track_id, {})
            row.extend(
                [
                    tag_values.get("tag_count"),
                    tag_values.get("top_tags_json"),
                    genre_values.get("non_zero_genre_count"),
                    genre_values.get("top_genres_json"),
                ]
            )

            writer.writerow([value_for_csv(value) for value in row])

    intersections = {
        "all_sources": len(set.intersection(*id_sets.values())),
        "counts_and_essentia": len(id_sets["user_track_counts"].intersection(id_sets["essentia"])),
        "counts_and_lyrics": len(id_sets["user_track_counts"].intersection(id_sets["lyrics"])),
        "counts_and_tags": len(id_sets["user_track_counts"].intersection(id_sets["tags"])),
        "counts_and_genres": len(id_sets["user_track_counts"].intersection(id_sets["genres"])),
    }

    coverage_report = {
        "run_metadata": {
            "task": "BL-017",
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "elapsed_seconds": round(time.time() - start_time, 3),
            "selected_dir": str(selected_dir),
            "output_dir": str(args.output_dir),
            "top_tags": max(1, args.top_tags),
            "top_genres": max(1, args.top_genres),
            "max_user_track_rows": args.max_user_track_rows,
            "max_track_rows_per_file": args.max_track_rows_per_file,
        },
        "source_track_counts": {name: len(values) for name, values in id_sets.items()},
        "track_id_universe_count": len(all_track_ids),
        "join_intersections": intersections,
        "availability_counts": availability_counts,
        "missingness": {
            "essentia": essentia_missing,
            "lyrics": lyrics_missing,
        },
        "output_files": {
            "canonical_track_table": str(canonical_path),
        },
    }

    coverage_path = args.output_dir / "onion_join_coverage_report.json"
    with coverage_path.open("w", encoding="utf-8") as handle:
        json.dump(coverage_report, handle, indent=2, ensure_ascii=True)

    manifest = {
        "task": "BL-017",
        "selected_files": {
            "user_track_counts": "userid_trackid_count.tsv.bz2",
            "essentia": "id_essentia.tsv.bz2",
            "lyrics": "id_lyrics_sentiment_functionals.tsv.bz2",
            "tags": "id_tags_dict.tsv.bz2",
            "genres": "id_genres_tf-idf.tsv.bz2",
        },
        "column_manifest": [
            {
                "output_column": "track_id",
                "source_file": "multiple",
                "source_column": "id or track_id",
                "type": "string",
            },
            {
                "output_column": "listener_rows",
                "source_file": "userid_trackid_count.tsv.bz2",
                "source_column": "count of (user_id, track_id) rows",
                "type": "integer",
            },
            {
                "output_column": "playcount_sum",
                "source_file": "userid_trackid_count.tsv.bz2",
                "source_column": "sum(count)",
                "type": "integer",
            },
        ],
        "essentia_columns": ESSENTIA_COLUMNS,
        "lyrics_columns": LYRICS_COLUMNS,
        "derived_columns": [
            {
                "output_column": "top_tags_json",
                "rule": f"top {max(1, args.top_tags)} tags sorted by descending weight",
            },
            {
                "output_column": "top_genres_json",
                "rule": f"top {max(1, args.top_genres)} non-zero genres sorted by descending score",
            },
            {
                "output_column": "has_*",
                "rule": "binary per-source availability flags",
            },
        ],
    }

    for column in ESSENTIA_COLUMNS:
        manifest["column_manifest"].append(
            {
                "output_column": column,
                "source_file": "id_essentia.tsv.bz2",
                "source_column": column,
                "type": "float",
            }
        )

    for column in LYRICS_COLUMNS:
        manifest["column_manifest"].append(
            {
                "output_column": column,
                "source_file": "id_lyrics_sentiment_functionals.tsv.bz2",
                "source_column": column,
                "type": "float",
            }
        )

    manifest_path = args.output_dir / "onion_selected_column_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=True)

    output_hashes = {
        "onion_canonical_track_table.csv": sha256_of_file(canonical_path),
        "onion_join_coverage_report.json": sha256_of_file(coverage_path),
        "onion_selected_column_manifest.json": sha256_of_file(manifest_path),
    }

    coverage_report["output_hashes_sha256"] = output_hashes
    with coverage_path.open("w", encoding="utf-8") as handle:
        json.dump(coverage_report, handle, indent=2, ensure_ascii=True)

    print("BL-017 canonical layer build complete.")
    print(f"Rows in canonical table: {len(all_track_ids)}")
    print(f"Output directory: {args.output_dir}")
    print("Output file hashes (sha256):")
    for name, digest in output_hashes.items():
        print(f"  {name}: {digest}")


if __name__ == "__main__":
    main()