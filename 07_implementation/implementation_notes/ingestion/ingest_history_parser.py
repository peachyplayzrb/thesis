#!/usr/bin/env python3
"""Minimal deterministic ingestion parser for BL-002 MVP validation.

Transforms raw listening-history CSV rows into normalized JSONL events and
writes run summary metrics for traceable testing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ISRC_PATTERN = re.compile(r"^[A-Z]{2}[A-Z0-9]{3}\d{7}$")
REQUIRED_RAW_FIELDS = ["track_name", "artist_name", "played_at", "ms_played"]


@dataclass
class RowResult:
    normalized: Dict[str, object]
    is_valid: bool


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split()).lower()


def parse_timestamp(raw_value: str) -> Optional[str]:
    value = raw_value.strip()
    if not value:
        return None

    # Handle common export formats: ISO-8601 and "YYYY-MM-DD HH:MM:SS".
    candidates = [value]
    if value.endswith("Z"):
        candidates.append(value[:-1] + "+00:00")

    for candidate in candidates:
        try:
            dt = datetime.fromisoformat(candidate)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt.isoformat().replace("+00:00", "Z")
        except ValueError:
            continue

    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")
    except ValueError:
        return None


def make_event_id(row_index: int, track: str, artist: str, played_at: str, ms_played: str) -> str:
    payload = f"{row_index}|{track}|{artist}|{played_at}|{ms_played}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return digest[:16]


def validate_and_normalize_row(
    row: Dict[str, str], row_index: int, ingest_run_id: str, source_platform: str
) -> RowResult:
    missing_core = [field for field in REQUIRED_RAW_FIELDS if not (row.get(field) or "").strip()]

    track_name_raw = row.get("track_name", "")
    artist_name_raw = row.get("artist_name", "")
    album_name_raw = row.get("album_name", "")
    isrc_raw = row.get("isrc", "")
    played_at_raw = row.get("played_at", "")
    ms_played_raw = row.get("ms_played", "")

    timestamp_iso = parse_timestamp(played_at_raw)

    try:
        ms_played_int = int(ms_played_raw.strip())
    except ValueError:
        ms_played_int = -1

    event_id = make_event_id(
        row_index=row_index,
        track=track_name_raw,
        artist=artist_name_raw,
        played_at=played_at_raw,
        ms_played=ms_played_raw,
    )

    isrc_value = isrc_raw.strip().upper()
    if isrc_value and not ISRC_PATTERN.match(isrc_value):
        isrc_value = ""

    flags: List[str] = []
    is_valid = True

    if missing_core:
        flags.append("missing_core_field")
        is_valid = False

    if timestamp_iso is None:
        flags.append("invalid_timestamp")
        is_valid = False

    if ms_played_int < 0:
        flags.append("invalid_ms_played")
        is_valid = False

    if not isrc_value:
        flags.append("missing_isrc")

    quality_flag = "ok" if not flags else ";".join(flags)

    normalized = {
        "event_id": event_id,
        "track_name": normalize_text(track_name_raw) if track_name_raw.strip() else "",
        "artist_name": normalize_text(artist_name_raw) if artist_name_raw.strip() else "",
        "album_name": normalize_text(album_name_raw) if album_name_raw.strip() else "",
        "isrc": isrc_value,
        "played_at": timestamp_iso or "",
        "ms_played": ms_played_int,
        "source_platform": source_platform,
        "ingest_run_id": ingest_run_id,
        "row_quality_flag": quality_flag,
    }

    return RowResult(normalized=normalized, is_valid=is_valid)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_ingestion(input_csv: Path, output_jsonl: Path, summary_json: Path, ingest_run_id: str, source_platform: str) -> Dict[str, object]:
    rows_total = 0
    rows_valid = 0
    rows_invalid = 0
    rows_missing_isrc = 0

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    normalized_rows: List[Dict[str, object]] = []

    with input_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is missing a header row.")

        for field in REQUIRED_RAW_FIELDS:
            if field not in reader.fieldnames:
                raise ValueError(f"Missing required CSV column: {field}")

        for index, row in enumerate(reader, start=1):
            rows_total += 1
            result = validate_and_normalize_row(
                row=row,
                row_index=index,
                ingest_run_id=ingest_run_id,
                source_platform=source_platform,
            )
            if result.is_valid:
                rows_valid += 1
            else:
                rows_invalid += 1
            if "missing_isrc" in str(result.normalized["row_quality_flag"]):
                rows_missing_isrc += 1
            normalized_rows.append(result.normalized)

    with output_jsonl.open("w", encoding="utf-8", newline="") as handle:
        for row in normalized_rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    summary = {
        "run_id": ingest_run_id,
        "rows_total": rows_total,
        "rows_valid": rows_valid,
        "rows_invalid": rows_invalid,
        "rows_missing_isrc": rows_missing_isrc,
        "input_hash": sha256_file(input_csv),
        "output_hash": sha256_file(output_jsonl),
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_platform": source_platform,
    }

    with summary_json.open("w", encoding="utf-8", newline="") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize listening-history CSV for MVP ingestion tests.")
    parser.add_argument("--input", required=True, type=Path, help="Path to input listening-history CSV.")
    parser.add_argument("--output", required=True, type=Path, help="Path to output normalized JSONL.")
    parser.add_argument("--summary", required=True, type=Path, help="Path to output summary JSON.")
    parser.add_argument("--ingest-run-id", required=True, help="Run identifier for traceability.")
    parser.add_argument("--source-platform", default="unknown", help="Source platform label for provenance.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_ingestion(
        input_csv=args.input,
        output_jsonl=args.output,
        summary_json=args.summary,
        ingest_run_id=args.ingest_run_id,
        source_platform=args.source_platform,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
