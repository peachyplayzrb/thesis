#!/usr/bin/env python3
"""ISRC-first track alignment with deterministic metadata fallback.

Inputs:
- normalized ingestion JSONL events
- candidate corpus CSV (Music4All-like subset)

Outputs:
- alignment JSONL (one row per input event considered)
- summary JSON with match counts and rates
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

HARD_INVALID_FLAGS = {"missing_core_field", "invalid_timestamp", "invalid_ms_played"}


@dataclass
class CandidateRow:
    m4a_track_id: str
    isrc: str
    track_name_norm: str
    artist_name_norm: str


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split()).lower()


def split_flags(flag_str: str) -> List[str]:
    if not flag_str:
        return []
    return [part.strip() for part in flag_str.split(";") if part.strip()]


def load_candidates(candidates_csv: Path) -> Tuple[Dict[str, CandidateRow], Dict[Tuple[str, str], CandidateRow]]:
    by_isrc: Dict[str, CandidateRow] = {}
    by_meta: Dict[Tuple[str, str], CandidateRow] = {}

    with candidates_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = ["m4a_track_id", "isrc", "track_name", "artist_name"]
        if reader.fieldnames is None:
            raise ValueError("Candidate CSV is missing a header row.")
        for field in required:
            if field not in reader.fieldnames:
                raise ValueError(f"Missing required candidate column: {field}")

        for row in reader:
            cand = CandidateRow(
                m4a_track_id=(row.get("m4a_track_id") or "").strip(),
                isrc=(row.get("isrc") or "").strip().upper(),
                track_name_norm=normalize_text(row.get("track_name") or ""),
                artist_name_norm=normalize_text(row.get("artist_name") or ""),
            )
            if cand.isrc and cand.isrc not in by_isrc:
                by_isrc[cand.isrc] = cand
            meta_key = (cand.track_name_norm, cand.artist_name_norm)
            if all(meta_key) and meta_key not in by_meta:
                by_meta[meta_key] = cand

    return by_isrc, by_meta


def align_events(
    events_jsonl: Path,
    candidates_csv: Path,
    output_jsonl: Path,
    summary_json: Path,
    include_invalid_rows: bool,
) -> Dict[str, object]:
    by_isrc, by_meta = load_candidates(candidates_csv)

    rows_total = 0
    rows_considered = 0
    rows_skipped_invalid = 0
    matched_total = 0
    matched_isrc = 0
    matched_fallback = 0
    unmatched = 0

    aligned_rows: List[Dict[str, object]] = []

    with events_jsonl.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows_total += 1
            event = json.loads(line)

            quality = str(event.get("row_quality_flag", ""))
            flags = set(split_flags(quality))
            is_hard_invalid = any(flag in HARD_INVALID_FLAGS for flag in flags)
            if is_hard_invalid and not include_invalid_rows:
                rows_skipped_invalid += 1
                continue

            rows_considered += 1
            event_isrc = str(event.get("isrc", "")).strip().upper()
            event_track = normalize_text(str(event.get("track_name", "")))
            event_artist = normalize_text(str(event.get("artist_name", "")))

            match_method = "none"
            matched_candidate = None

            if event_isrc and event_isrc in by_isrc:
                matched_candidate = by_isrc[event_isrc]
                match_method = "isrc"
                matched_isrc += 1
            else:
                meta_key = (event_track, event_artist)
                if all(meta_key) and meta_key in by_meta:
                    matched_candidate = by_meta[meta_key]
                    match_method = "metadata"
                    matched_fallback += 1

            if matched_candidate is not None:
                matched_total += 1
                aligned_rows.append(
                    {
                        "event_id": event.get("event_id", ""),
                        "ingest_run_id": event.get("ingest_run_id", ""),
                        "m4a_track_id": matched_candidate.m4a_track_id,
                        "matched_isrc": matched_candidate.isrc,
                        "match_method": match_method,
                        "track_name": event_track,
                        "artist_name": event_artist,
                        "row_quality_flag": quality,
                    }
                )
            else:
                unmatched += 1
                aligned_rows.append(
                    {
                        "event_id": event.get("event_id", ""),
                        "ingest_run_id": event.get("ingest_run_id", ""),
                        "m4a_track_id": "",
                        "matched_isrc": "",
                        "match_method": "none",
                        "track_name": event_track,
                        "artist_name": event_artist,
                        "row_quality_flag": quality,
                    }
                )

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    with output_jsonl.open("w", encoding="utf-8", newline="") as handle:
        for row in aligned_rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    # Deterministic hash of output for reproducibility tracking.
    digest = hashlib.sha256()
    with output_jsonl.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)

    match_rate = (matched_total / rows_considered) if rows_considered else 0.0
    summary = {
        "rows_total": rows_total,
        "rows_considered": rows_considered,
        "rows_skipped_invalid": rows_skipped_invalid,
        "matched_total": matched_total,
        "matched_isrc": matched_isrc,
        "matched_fallback": matched_fallback,
        "unmatched": unmatched,
        "match_rate": round(match_rate, 4),
        "alignment_output_hash": digest.hexdigest(),
        "include_invalid_rows": include_invalid_rows,
    }

    with summary_json.open("w", encoding="utf-8", newline="") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Align normalized events to candidate corpus using ISRC-first logic.")
    parser.add_argument("--events", required=True, type=Path, help="Path to normalized events JSONL.")
    parser.add_argument("--candidates", required=True, type=Path, help="Path to candidate corpus CSV.")
    parser.add_argument("--output", required=True, type=Path, help="Path to alignment output JSONL.")
    parser.add_argument("--summary", required=True, type=Path, help="Path to summary JSON.")
    parser.add_argument(
        "--include-invalid-rows",
        action="store_true",
        help="Include rows flagged with hard invalid flags instead of skipping.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = align_events(
        events_jsonl=args.events,
        candidates_csv=args.candidates,
        output_jsonl=args.output,
        summary_json=args.summary,
        include_invalid_rows=args.include_invalid_rows,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
