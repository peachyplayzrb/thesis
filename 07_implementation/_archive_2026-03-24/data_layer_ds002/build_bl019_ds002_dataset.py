from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sqlite3
import tarfile
import time
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List

import h5py


EXPECTED_TRACK_COUNT = 10000

DATASET_FIELDNAMES = [
    "track_id",
    "artist_name",
    "title",
    "release",
    "year",
    "duration",
    "tempo",
    "loudness",
    "key",
    "mode",
    "tags_json",
    "tag_count",
    "artist_mbid",
    "song_id",
    "has_msd",
    "has_lastfm",
    "has_musicbrainz",
]

QUALITY_THRESHOLDS = {
    "min_row_count": 8000,
    "min_metadata_coverage": 1.0,
    "min_lastfm_coverage": 1.0,
    "min_musicbrainz_coverage": 0.0,
    "max_duration_null_rate": 0.01,
    "max_tempo_null_rate": 0.01,
    "max_loudness_null_rate": 0.01,
    "max_key_null_rate": 0.01,
    "max_mode_null_rate": 0.01,
}


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    source_dir = repo_root / "06_data_and_sources"
    default_output_dir = script_path.parent / "outputs"

    parser = argparse.ArgumentParser(
        description="BL-019: Build the DS-002 integrated candidate dataset with deterministic joins and quality checks."
    )
    parser.add_argument("--metadata-db", type=Path, default=source_dir / "track_metadata.db")
    parser.add_argument("--msd-tar", type=Path, default=source_dir / "millionsongsubset.tar.gz")
    parser.add_argument("--lastfm-zip", type=Path, default=source_dir / "lastfm_subset.zip")
    parser.add_argument("--output-dir", type=Path, default=default_output_dir)
    return parser.parse_args()


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def format_float(value: float | None) -> str:
    if value is None:
        return ""
    if not math.isfinite(value):
        return ""
    return f"{value:.6f}"


def format_int(value: int | None) -> str:
    if value is None:
        return ""
    return str(value)


def parse_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8", errors="replace")
        except Exception:
            return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            number = float(text)
        except ValueError:
            return None
    else:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
    if not math.isfinite(number):
        return None
    return number


def parse_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8", errors="replace")
        except Exception:
            return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return int(float(text))
        except ValueError:
            return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def decode_text(value: object) -> str:
    if value is None:
        return ""
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip()
    return str(value).strip()


def normalize_tag(tag: str) -> str:
    return " ".join(tag.strip().lower().split())


def first_nonempty(*values: object) -> str:
    for value in values:
        text = decode_text(value)
        if text:
            return text
    return ""


def first_nonnull_float(*values: object) -> float | None:
    for value in values:
        parsed = parse_float(value)
        if parsed is not None:
            return parsed
    return None


def chunked(items: List[str], size: int) -> Iterable[List[str]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


def load_msd_subset(msd_tar_path: Path) -> tuple[Dict[str, dict], Dict[str, dict], List[str], Dict[str, str]]:
    features_by_track: Dict[str, dict] = {}
    metadata_by_track: Dict[str, dict] = {}
    source_member_by_track: Dict[str, str] = {}

    # Use streaming mode (r|gz) for a single sequential pass through the archive —
    # avoids getmembers() pre-scan of the entire 1.9 GB stream.
    with tarfile.open(msd_tar_path, mode="r|gz") as archive:
        for member in archive:
            if not (member.isfile() and member.name.lower().endswith(".h5")):
                archive.members = []  # release internal member list to save RAM
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                continue
            payload = extracted.read()
            with h5py.File(io.BytesIO(payload), mode="r") as handle:
                analysis_row = handle["analysis"]["songs"][0]
                metadata_row = handle["metadata"]["songs"][0]

                track_id = decode_text(analysis_row["track_id"])
                if not track_id:
                    continue

                features_by_track[track_id] = {
                    "duration": parse_float(analysis_row["duration"]),
                    "tempo": parse_float(analysis_row["tempo"]),
                    "loudness": parse_float(analysis_row["loudness"]),
                    "key": parse_int(analysis_row["key"]),
                    "mode": parse_int(analysis_row["mode"]),
                }
                metadata_by_track[track_id] = {
                    "artist_name": decode_text(metadata_row["artist_name"]),
                    "title": decode_text(metadata_row["title"]),
                    "release": decode_text(metadata_row["release"]),
                    "artist_mbid": decode_text(metadata_row["artist_mbid"]),
                    "song_id": decode_text(metadata_row["song_id"]),
                }
                source_member_by_track[track_id] = member.name

    track_ids = sorted(features_by_track)
    return features_by_track, metadata_by_track, track_ids, source_member_by_track


def load_metadata_rows(metadata_db_path: Path, track_ids: List[str]) -> tuple[Dict[str, dict], int]:
    result: Dict[str, dict] = {}

    with sqlite3.connect(metadata_db_path) as connection:
        cursor = connection.cursor()
        total_rows = int(cursor.execute("SELECT COUNT(*) FROM songs").fetchone()[0])

        for chunk in chunked(track_ids, 800):
            placeholders = ",".join("?" for _ in chunk)
            query = (
                "SELECT track_id, title, artist_name, release, artist_mbid, year, duration, song_id "
                f"FROM songs WHERE track_id IN ({placeholders})"
            )
            for row in cursor.execute(query, chunk):
                result[decode_text(row[0])] = {
                    "title": decode_text(row[1]),
                    "artist_name": decode_text(row[2]),
                    "release": decode_text(row[3]),
                    "artist_mbid": decode_text(row[4]),
                    "year": parse_int(row[5]),
                    "duration": parse_float(row[6]),
                    "song_id": decode_text(row[7]),
                }

    return result, total_rows


def load_lastfm_tags(lastfm_zip_path: Path) -> tuple[Dict[str, List[dict]], int]:
    tags_by_track: Dict[str, List[dict]] = {}

    with zipfile.ZipFile(lastfm_zip_path) as archive:
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".json"))

        for name in names:
            payload = json.loads(archive.read(name).decode("utf-8"))
            track_id = decode_text(payload.get("track_id"))
            if not track_id:
                continue

            aggregated: Dict[str, float] = {}
            raw_tags = payload.get("tags", [])
            if isinstance(raw_tags, list):
                for item in raw_tags:
                    if not isinstance(item, (list, tuple)) or len(item) != 2:
                        continue
                    tag_text = normalize_tag(decode_text(item[0]))
                    if not tag_text:
                        continue
                    weight_value = parse_float(item[1])
                    if weight_value is None:
                        continue
                    aggregated[tag_text] = aggregated.get(tag_text, 0.0) + weight_value

            ordered = [
                {"tag": tag, "weight": round(weight, 6)}
                for tag, weight in sorted(aggregated.items(), key=lambda pair: (-pair[1], pair[0]))
            ]
            tags_by_track[track_id] = ordered

    return tags_by_track, len(tags_by_track)


def build_dataset_rows(
    track_ids: List[str],
    msd_features: Dict[str, dict],
    msd_metadata: Dict[str, dict],
    db_metadata: Dict[str, dict],
    lastfm_tags: Dict[str, List[dict]],
) -> tuple[List[dict], dict]:
    rows: List[dict] = []
    counters = {
        "metadata_matches": 0,
        "lastfm_matches": 0,
        "tracks_with_tags": 0,
        "tracks_with_musicbrainz": 0,
        "duration_missing": 0,
        "tempo_missing": 0,
        "loudness_missing": 0,
        "key_missing": 0,
        "mode_missing": 0,
        "year_missing": 0,
    }

    for track_id in track_ids:
        # intersection-only: skip tracks missing SQLite metadata or Last.fm tags
        if track_id not in db_metadata or track_id not in lastfm_tags:
            continue

        feature_row = msd_features[track_id]
        h5_meta = msd_metadata.get(track_id, {})
        db_meta = db_metadata.get(track_id, {})
        tags = lastfm_tags.get(track_id, [])

        artist_name = first_nonempty(db_meta.get("artist_name"), h5_meta.get("artist_name"))
        title = first_nonempty(db_meta.get("title"), h5_meta.get("title"))
        release = first_nonempty(db_meta.get("release"), h5_meta.get("release"))
        artist_mbid = first_nonempty(db_meta.get("artist_mbid"), h5_meta.get("artist_mbid"))
        song_id = first_nonempty(db_meta.get("song_id"), h5_meta.get("song_id"))
        year = parse_int(db_meta.get("year"))
        duration = first_nonnull_float(feature_row.get("duration"), db_meta.get("duration"))
        tempo = first_nonnull_float(feature_row.get("tempo"))
        loudness = first_nonnull_float(feature_row.get("loudness"))
        key = parse_int(feature_row.get("key"))
        mode = parse_int(feature_row.get("mode"))

        has_metadata = int(bool(artist_name and title))
        has_lastfm = int(track_id in lastfm_tags)
        has_musicbrainz = int(bool(artist_mbid))

        counters["metadata_matches"] += has_metadata
        counters["lastfm_matches"] += has_lastfm
        counters["tracks_with_tags"] += int(len(tags) > 0)
        counters["tracks_with_musicbrainz"] += has_musicbrainz
        counters["duration_missing"] += int(duration is None)
        counters["tempo_missing"] += int(tempo is None)
        counters["loudness_missing"] += int(loudness is None)
        counters["key_missing"] += int(key is None)
        counters["mode_missing"] += int(mode is None)
        counters["year_missing"] += int(year is None)

        rows.append(
            {
                "track_id": track_id,
                "artist_name": artist_name,
                "title": title,
                "release": release,
                "year": format_int(year),
                "duration": format_float(duration),
                "tempo": format_float(tempo),
                "loudness": format_float(loudness),
                "key": format_int(key),
                "mode": format_int(mode),
                "tags_json": json.dumps(tags, ensure_ascii=True, separators=(",", ":")),
                "tag_count": str(len(tags)),
                "artist_mbid": artist_mbid,
                "song_id": song_id,
                "has_msd": "1",
                "has_lastfm": str(has_lastfm),
                "has_musicbrainz": str(has_musicbrainz),
            }
        )

    rows.sort(key=lambda row: row["track_id"])
    return rows, counters


def write_csv(path: Path, fieldnames: List[str], rows: List[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_quality_gates(row_count: int, counters: dict) -> tuple[List[dict], dict, dict]:
    coverage = {
        "metadata": counters["metadata_matches"] / row_count,
        "lastfm": counters["lastfm_matches"] / row_count,
        "musicbrainz": counters["tracks_with_musicbrainz"] / row_count,
    }
    null_rates = {
        "year": counters["year_missing"] / row_count,
        "duration": counters["duration_missing"] / row_count,
        "tempo": counters["tempo_missing"] / row_count,
        "loudness": counters["loudness_missing"] / row_count,
        "key": counters["key_missing"] / row_count,
        "mode": counters["mode_missing"] / row_count,
    }

    gates = [
        {
            "gate": "min_row_count",
            "value": float(row_count),
            "threshold": float(QUALITY_THRESHOLDS["min_row_count"]),
            "comparator": ">=",
            "pass": row_count >= QUALITY_THRESHOLDS["min_row_count"],
        },
        {
            "gate": "metadata_coverage",
            "value": coverage["metadata"],
            "threshold": QUALITY_THRESHOLDS["min_metadata_coverage"],
            "comparator": ">=",
            "pass": coverage["metadata"] >= QUALITY_THRESHOLDS["min_metadata_coverage"],
        },
        {
            "gate": "lastfm_coverage",
            "value": coverage["lastfm"],
            "threshold": QUALITY_THRESHOLDS["min_lastfm_coverage"],
            "comparator": ">=",
            "pass": coverage["lastfm"] >= QUALITY_THRESHOLDS["min_lastfm_coverage"],
        },
        {
            "gate": "musicbrainz_coverage",
            "value": coverage["musicbrainz"],
            "threshold": QUALITY_THRESHOLDS["min_musicbrainz_coverage"],
            "comparator": ">=",
            "pass": coverage["musicbrainz"] >= QUALITY_THRESHOLDS["min_musicbrainz_coverage"],
        },
        {
            "gate": "duration_null_rate",
            "value": null_rates["duration"],
            "threshold": QUALITY_THRESHOLDS["max_duration_null_rate"],
            "comparator": "<=",
            "pass": null_rates["duration"] <= QUALITY_THRESHOLDS["max_duration_null_rate"],
        },
        {
            "gate": "tempo_null_rate",
            "value": null_rates["tempo"],
            "threshold": QUALITY_THRESHOLDS["max_tempo_null_rate"],
            "comparator": "<=",
            "pass": null_rates["tempo"] <= QUALITY_THRESHOLDS["max_tempo_null_rate"],
        },
        {
            "gate": "loudness_null_rate",
            "value": null_rates["loudness"],
            "threshold": QUALITY_THRESHOLDS["max_loudness_null_rate"],
            "comparator": "<=",
            "pass": null_rates["loudness"] <= QUALITY_THRESHOLDS["max_loudness_null_rate"],
        },
        {
            "gate": "key_null_rate",
            "value": null_rates["key"],
            "threshold": QUALITY_THRESHOLDS["max_key_null_rate"],
            "comparator": "<=",
            "pass": null_rates["key"] <= QUALITY_THRESHOLDS["max_key_null_rate"],
        },
        {
            "gate": "mode_null_rate",
            "value": null_rates["mode"],
            "threshold": QUALITY_THRESHOLDS["max_mode_null_rate"],
            "comparator": "<=",
            "pass": null_rates["mode"] <= QUALITY_THRESHOLDS["max_mode_null_rate"],
        },
    ]
    return gates, coverage, null_rates


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = output_dir / "bl019_ds002_integrated_candidate_dataset.csv"
    quality_checks_path = output_dir / "bl019_ds002_quality_checks.csv"
    manifest_path = output_dir / "bl019_ds002_dataset_manifest.json"
    report_path = output_dir / "bl019_ds002_integration_report.json"

    started = time.time()

    msd_features, msd_metadata, track_ids, h5_member_by_track = load_msd_subset(args.msd_tar)
    db_metadata, metadata_db_row_count = load_metadata_rows(args.metadata_db, track_ids)
    lastfm_tags, lastfm_json_count = load_lastfm_tags(args.lastfm_zip)

    rows, counters = build_dataset_rows(track_ids, msd_features, msd_metadata, db_metadata, lastfm_tags)
    write_csv(dataset_path, DATASET_FIELDNAMES, rows)

    gates, coverage, null_rates = build_quality_gates(len(rows), counters)
    quality_rows = [
        {
            "gate": gate["gate"],
            "value": format_float(gate["value"]),
            "threshold": format_float(gate["threshold"]),
            "comparator": gate["comparator"],
            "pass": "1" if gate["pass"] else "0",
        }
        for gate in gates
    ]
    write_csv(quality_checks_path, ["gate", "value", "threshold", "comparator", "pass"], quality_rows)

    dataset_hash = sha256_of_file(dataset_path)
    quality_hash = sha256_of_file(quality_checks_path)

    manifest = {
        "task": "BL-019",
        "dataset_strategy": "DS-002",
        "source_paths": {
            "metadata_db": str(args.metadata_db.resolve()),
            "msd_tar": str(args.msd_tar.resolve()),
            "lastfm_zip": str(args.lastfm_zip.resolve()),
            "musicbrainz_enrichment_mode": "artist_mbid via MSD metadata sources",
        },
        "source_hashes_sha256": {
            "metadata_db": sha256_of_file(args.metadata_db),
            "msd_tar": sha256_of_file(args.msd_tar),
            "lastfm_zip": sha256_of_file(args.lastfm_zip),
        },
        "source_contracts": {
            "canonical_track_universe": "MSD subset HDF5 files (.h5) from millionsongsubset.tar.gz",
            "join_mode": "intersection — only tracks present in all three sources are included",
            "h5_member_count": EXPECTED_TRACK_COUNT,
            "observed_h5_member_count": len(track_ids),
            "metadata_db_row_count": metadata_db_row_count,
            "lastfm_json_count": lastfm_json_count,
        },
        "join_policy": {
            "primary_join_key": "track_id",
            "join_mode": "intersection — tracks missing SQLite metadata or Last.fm tags are excluded",
            "metadata_priority": "track_metadata.db first, MSD HDF5 metadata fallback",
            "musicbrainz_handling": "artist_mbid optional enrichment only",
            "spotify_alignment_note": "metadata-first on normalized title + artist with duration/release tie-breaks; corpus-side ISRC not assumed",
        },
        "dataset_schema": DATASET_FIELDNAMES,
        "quality_gate_thresholds": QUALITY_THRESHOLDS,
        "output_paths": {
            "dataset": str(dataset_path.resolve()),
            "quality_checks": str(quality_checks_path.resolve()),
            "report": str(report_path.resolve()),
        },
        "output_hashes_sha256": {
            dataset_path.name: dataset_hash,
            quality_checks_path.name: quality_hash,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    manifest_hash = sha256_of_file(manifest_path)

    missing_metadata_track_ids = sorted(track_id for track_id in track_ids if track_id not in db_metadata)
    missing_lastfm_track_ids = sorted(track_id for track_id in track_ids if track_id not in lastfm_tags)
    missing_musicbrainz_track_ids = sorted(track_id for track_id, row in zip(track_ids, rows) if row["has_musicbrainz"] == "0")

    report = {
        "run_metadata": {
            "task": "BL-019",
            "generated_at_utc": utc_now(),
            "elapsed_seconds": round(time.time() - started, 3),
            "canonical_track_universe": "MSD subset HDF5 track_id set",
            "musicbrainz_optional_only": True,
        },
        "counts": {
            "rows": len(rows),
            "h5_members": len(track_ids),
            "metadata_db_row_count": metadata_db_row_count,
            "metadata_matches": counters["metadata_matches"],
            "lastfm_json_records": lastfm_json_count,
            "lastfm_matches": counters["lastfm_matches"],
            "tracks_with_tags": counters["tracks_with_tags"],
            "tracks_with_musicbrainz": counters["tracks_with_musicbrainz"],
        },
        "coverage": coverage,
        "null_rates": null_rates,
        "join_diagnostics": {
            "missing_metadata_track_ids_count": len(missing_metadata_track_ids),
            "missing_lastfm_track_ids_count": len(missing_lastfm_track_ids),
            "missing_musicbrainz_track_ids_count": len(missing_musicbrainz_track_ids),
            "sample_missing_lastfm_track_ids": missing_lastfm_track_ids[:10],
            "sample_missing_musicbrainz_track_ids": missing_musicbrainz_track_ids[:10],
            "sample_h5_members": [h5_member_by_track[track_id] for track_id in track_ids[:5]],
        },
        "quality_gates": gates,
        "all_quality_gates_pass": all(gate["pass"] for gate in gates),
        "output_files": {
            "dataset": str(dataset_path.resolve()),
            "manifest": str(manifest_path.resolve()),
            "quality_checks": str(quality_checks_path.resolve()),
        },
        "output_hashes_sha256": {
            dataset_path.name: dataset_hash,
            quality_checks_path.name: quality_hash,
            manifest_path.name: manifest_hash,
        },
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    print("BL-019 DS-002 dataset build complete.")
    print(f"rows={len(rows)}")
    print(f"metadata_coverage={coverage['metadata']:.6f}")
    print(f"lastfm_coverage={coverage['lastfm']:.6f}")
    print(f"musicbrainz_coverage={coverage['musicbrainz']:.6f}")
    print(f"dataset_sha256={dataset_hash}")
    print(f"quality_sha256={quality_hash}")
    print(f"manifest_sha256={manifest_hash}")


if __name__ == "__main__":
    main()
