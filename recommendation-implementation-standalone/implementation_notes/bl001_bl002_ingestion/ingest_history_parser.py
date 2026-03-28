from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from bl000_shared_utils.hashing import sha256_of_file as shared_sha256_of_file
from bl000_shared_utils.io_utils import open_text_write
from bl000_shared_utils.path_utils import impl_root


REQUIRED_LOGICAL_FIELDS = ["track_name", "artist_name", "played_at", "ms_played"]
RAW_COLUMN_ALIASES = {
    "track_name": ["track_name", "master_metadata_track_name"],
    "artist_name": ["artist_name", "master_metadata_album_artist_name"],
    "album_name": ["album_name", "master_metadata_album_album_name"],
    "isrc": ["isrc"],
    "played_at": ["played_at", "ts"],
    "ms_played": ["ms_played"],
    "platform": ["platform"],
}
ISRC_PATTERN = re.compile(r"^[A-Z]{2}[A-Z0-9]{3}\d{7}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "BL-002 parser: transform raw listening-history CSV into normalized JSONL with quality flags."
        )
    )
    parser.add_argument(
        "--input-csv",
        default="07_implementation/implementation_notes/test_assets/sample_listening_history.csv",
        help="Path to raw listening-history CSV.",
    )
    parser.add_argument(
        "--output-jsonl",
        default="07_implementation/implementation_notes/run_outputs/tc001_normalized_events.jsonl",
        help="Path to normalized event JSONL output.",
    )
    parser.add_argument(
        "--summary-json",
        default="07_implementation/implementation_notes/run_outputs/tc001_validation_summary.json",
        help="Path to validation summary JSON output.",
    )
    parser.add_argument(
        "--invalid-rows-csv",
        default="07_implementation/implementation_notes/run_outputs/tc001_invalid_rows.csv",
        help="Path to CSV listing non-ok rows.",
    )
    parser.add_argument(
        "--source-platform",
        default="spotify_export_csv",
        help="Fallback source_platform when platform column is missing/blank.",
    )
    return parser.parse_args()


def sha256_of_file(path: Path) -> str:
    return shared_sha256_of_file(path, uppercase=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with open_text_write(path) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with open_text_write(path, newline="") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_invalid_rows_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with open_text_write(path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def first_present(row: dict[str, Any], aliases: list[str]) -> str:
    for key in aliases:
        if key in row:
            return str(row.get(key, ""))
    return ""


def normalize_text(value: str | None, lowercase: bool = True) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    collapsed = " ".join(text.split())
    if lowercase:
        return collapsed.lower()
    return collapsed


def normalize_isrc(value: str | None) -> str:
    token = normalize_text(value, lowercase=False).upper()
    if not token:
        return ""
    if ISRC_PATTERN.match(token):
        return token
    return ""


def parse_timestamp_to_utc(value: str | None) -> tuple[str, bool]:
    text = normalize_text(value, lowercase=False)
    if not text:
        return "", False

    candidates = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]

    parsed: datetime | None = None
    iso_candidate = text.replace("Z", "+00:00") if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(iso_candidate)
    except ValueError:
        parsed = None

    if parsed is None:
        for fmt in candidates:
            try:
                parsed = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue

    if parsed is None:
        return "", False

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)

    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ"), True


def parse_ms_played(value: str | None) -> tuple[int | None, bool]:
    text = normalize_text(value, lowercase=False)
    if not text:
        return None, False
    try:
        parsed = int(text)
    except ValueError:
        return None, False
    if parsed < 0:
        return None, False
    return parsed, True


def build_event_id(row_number: int, track_name: str, artist_name: str, played_at: str, ms_played: int | None) -> str:
    payload = f"{row_number}|{track_name}|{artist_name}|{played_at}|{ms_played if ms_played is not None else ''}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()
    return f"EVT-{row_number:06d}-{digest[:12]}"


def classify_row(track_name: str, artist_name: str, played_at_raw: str | None, ms_played_raw: str | None, isrc: str) -> tuple[str, str, int | None]:
    normalized_played_at, ts_ok = parse_timestamp_to_utc(played_at_raw)
    normalized_ms_played, ms_ok = parse_ms_played(ms_played_raw)

    missing_core = not track_name or not artist_name or not normalize_text(played_at_raw, lowercase=False) or not normalize_text(ms_played_raw, lowercase=False)
    if missing_core:
        return "missing_core_field", normalized_played_at, normalized_ms_played
    if not ts_ok:
        return "invalid_timestamp", "", normalized_ms_played
    if not ms_ok:
        return "invalid_ms_played", normalized_played_at, None
    if not isrc:
        return "missing_isrc", normalized_played_at, normalized_ms_played
    return "ok", normalized_played_at, normalized_ms_played


def main() -> None:
    args = parse_args()
    root = impl_root()

    input_path = root / args.input_csv
    output_path = root / args.output_jsonl
    summary_path = root / args.summary_json
    invalid_rows_path = root / args.invalid_rows_csv

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    invalid_rows_path.parent.mkdir(parents=True, exist_ok=True)

    input_sha = sha256_of_file(input_path)
    ingest_run_id = f"BL002-INGEST-{input_sha[:12]}"

    with input_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        rows = list(reader)

    missing_columns: list[str] = []
    for logical_field in REQUIRED_LOGICAL_FIELDS:
        aliases = RAW_COLUMN_ALIASES[logical_field]
        if not any(alias in header for alias in aliases):
            missing_columns.append(f"{logical_field} (aliases={aliases})")
    if missing_columns:
        raise ValueError(f"Missing required CSV columns for logical fields: {missing_columns}")

    normalized_events: list[dict[str, Any]] = []
    invalid_rows: list[dict[str, Any]] = []

    summary = {
        "task": "BL-002",
        "ingest_run_id": ingest_run_id,
        "input_csv": args.input_csv,
        "input_sha256": input_sha,
        "rows_total": 0,
        "rows_valid": 0,
        "rows_invalid": 0,
        "rows_missing_isrc": 0,
        "rows_by_quality_flag": {
            "ok": 0,
            "missing_isrc": 0,
            "missing_core_field": 0,
            "invalid_timestamp": 0,
            "invalid_ms_played": 0,
        },
    }

    for index, raw_row in enumerate(rows, start=1):
        track_name = normalize_text(first_present(raw_row, RAW_COLUMN_ALIASES["track_name"]))
        artist_name = normalize_text(first_present(raw_row, RAW_COLUMN_ALIASES["artist_name"]))
        album_name = normalize_text(first_present(raw_row, RAW_COLUMN_ALIASES["album_name"]))
        isrc = normalize_isrc(first_present(raw_row, RAW_COLUMN_ALIASES["isrc"]))

        quality_flag, played_at, ms_played = classify_row(
            track_name=track_name,
            artist_name=artist_name,
            played_at_raw=first_present(raw_row, RAW_COLUMN_ALIASES["played_at"]),
            ms_played_raw=first_present(raw_row, RAW_COLUMN_ALIASES["ms_played"]),
            isrc=isrc,
        )

        source_platform = normalize_text(first_present(raw_row, RAW_COLUMN_ALIASES["platform"])) or normalize_text(args.source_platform)
        event_id = build_event_id(index, track_name, artist_name, played_at, ms_played)

        event = {
            "event_id": event_id,
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": album_name,
            "isrc": isrc,
            "played_at": played_at,
            "ms_played": ms_played if ms_played is not None else -1,
            "source_platform": source_platform,
            "ingest_run_id": ingest_run_id,
            "row_quality_flag": quality_flag,
        }
        normalized_events.append(event)

        summary["rows_total"] += 1
        summary["rows_by_quality_flag"][quality_flag] += 1

        if quality_flag in ("ok", "missing_isrc"):
            summary["rows_valid"] += 1
        else:
            summary["rows_invalid"] += 1

        if quality_flag == "missing_isrc":
            summary["rows_missing_isrc"] += 1

        if quality_flag not in ("ok", "missing_isrc"):
            invalid_rows.append(
                {
                    "row_number": index,
                    "event_id": event_id,
                    "row_quality_flag": quality_flag,
                    "track_name": track_name,
                    "artist_name": artist_name,
                    "played_at_raw": normalize_text(first_present(raw_row, RAW_COLUMN_ALIASES["played_at"]), lowercase=False),
                    "ms_played_raw": normalize_text(first_present(raw_row, RAW_COLUMN_ALIASES["ms_played"]), lowercase=False),
                    "isrc_raw": normalize_text(first_present(raw_row, RAW_COLUMN_ALIASES["isrc"]), lowercase=False),
                }
            )

    write_jsonl(output_path, normalized_events)

    invalid_fieldnames = [
        "row_number",
        "event_id",
        "row_quality_flag",
        "track_name",
        "artist_name",
        "played_at_raw",
        "ms_played_raw",
        "isrc_raw",
    ]
    write_invalid_rows_csv(invalid_rows_path, invalid_rows, invalid_fieldnames)

    summary["output_jsonl"] = args.output_jsonl
    summary["invalid_rows_csv"] = args.invalid_rows_csv
    summary["output_jsonl_sha256"] = sha256_of_file(output_path)
    summary["invalid_rows_sha256"] = sha256_of_file(invalid_rows_path)

    write_json(summary_path, summary)

    print(f"BL-002 ingestion complete: ingest_run_id={ingest_run_id}")
    print(f"rows_total={summary['rows_total']}")
    print(f"rows_valid={summary['rows_valid']}")
    print(f"rows_invalid={summary['rows_invalid']}")
    print(f"rows_missing_isrc={summary['rows_missing_isrc']}")
    print(f"normalized_events={output_path}")
    print(f"summary={summary_path}")
    print(f"invalid_rows={invalid_rows_path}")


if __name__ == "__main__":
    main()
