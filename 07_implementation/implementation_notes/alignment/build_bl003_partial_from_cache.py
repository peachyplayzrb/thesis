from __future__ import annotations

import csv
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

TOP_TRACKS_CSV = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/spotify_api_export/spotify_top_tracks_flat.csv"
)
SAVED_TRACKS_CSV = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/spotify_api_export/spotify_saved_tracks_flat.csv"
)
EXPORT_SUMMARY_JSON = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/spotify_api_export/spotify_export_run_summary.json"
)
CACHE_JSON = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/bl020_lastfm_tag_cache.json"
)
OUTPUT_JSONL = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/bl020_aligned_events_partial_from_cache.jsonl"
)
OUTPUT_REPORT = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/bl020_alignment_report_partial_from_cache.json"
)

TIME_RANGE_WEIGHTS = {
    "short_term": 0.50,
    "medium_term": 0.30,
    "long_term": 0.20,
}
TIME_RANGE_MAX = {
    "short_term": 598,
    "medium_term": 3021,
    "long_term": 5104,
}
SAVED_BONUS = 0.05
USER_ID = "21zsn42xecjhogne4kghyw5hq"

_RE_FEAT = re.compile(r"\s*[\(\[]\s*(?:feat|ft|featuring)\b[^\)\]]*[\)\]]", re.I)
_RE_VERSION = re.compile(
    r"(\s+-\s+|\s+\()(?:remaster|remix|live|version|edit|mix|demo|acoustic|"
    r"deluxe|anniversary|radio|single|original|instrumental|bonus|"
    r"super deluxe|reprise|recorded\b|alternate|alt[. ])\b.*$",
    re.I,
)
_RE_YEAR_DASH = re.compile(r"\s+-\s+\d{4}.*$")
_RE_OP_NUMBER = re.compile(r",?\s+(?:op|k|bwv|hwv|rv)\s*\.?\s*\d+.*$", re.I)
_RE_ACT_NO = re.compile(r",?\s+act\s+[ivxlc\d]+.*$", re.I)
_RE_NONALPHA = re.compile(r"[^a-z0-9 ]")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def normalise(text: str) -> str:
    s = unicodedata.normalize("NFKD", text)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = _RE_FEAT.sub("", s)
    s = _RE_OP_NUMBER.sub("", s)
    s = _RE_ACT_NO.sub("", s)
    s = _RE_VERSION.sub("", s)
    s = _RE_YEAR_DASH.sub("", s)
    s = _RE_NONALPHA.sub(" ", s)
    if s.startswith("the "):
        s = s[4:]
    return " ".join(s.split())


def first_artist(pipe_separated: str) -> str:
    return pipe_separated.split("|")[0].strip()


def build_cache_key(artist: str, title: str) -> str:
    return f"{normalise(first_artist(artist))}::{normalise(title)}"


def compute_preference_weight(rank_per_range: dict[str, int], is_saved: bool) -> float:
    combined = 0.0
    for tr, weight in TIME_RANGE_WEIGHTS.items():
        rank = rank_per_range.get(tr)
        if rank is None:
            continue
        max_rank = TIME_RANGE_MAX[tr]
        normalised = (max_rank - rank) / max_rank
        combined += weight * normalised
    pref = 1.0 + combined
    if is_saved:
        pref = min(2.0, pref + SAVED_BONUS)
    return round(pref, 6)


def interaction_count_proxy(preference_weight: float) -> int:
    return max(1, round((preference_weight - 1.0) * 200000))


def main() -> None:
    root = repo_root()
    top_path = root / TOP_TRACKS_CSV
    saved_path = root / SAVED_TRACKS_CSV
    export_summary_path = root / EXPORT_SUMMARY_JSON
    cache_path = root / CACHE_JSON
    output_jsonl_path = root / OUTPUT_JSONL
    output_report_path = root / OUTPUT_REPORT

    if not top_path.exists() or not saved_path.exists() or not cache_path.exists():
        raise FileNotFoundError("Missing required input files for partial build")

    top_tracks: dict[str, dict[str, object]] = {}
    for row in load_csv(top_path):
        sid = row.get("track_id", "").strip()
        tr = row.get("time_range", "").strip()
        rank_text = row.get("rank", "").strip()
        if not sid or not tr or not rank_text:
            continue
        try:
            rank_int = int(rank_text)
        except ValueError:
            continue

        if sid not in top_tracks:
            top_tracks[sid] = {
                "track_name": row.get("track_name", ""),
                "artist_names": row.get("artist_names", ""),
                "rank_per_range": {},
                "is_saved": False,
            }
        top_tracks[sid]["rank_per_range"][tr] = rank_int

    for row in load_csv(saved_path):
        sid = row.get("track_id", "").strip()
        if not sid:
            continue
        if sid in top_tracks:
            top_tracks[sid]["is_saved"] = True
        else:
            top_tracks[sid] = {
                "track_name": row.get("track_name", ""),
                "artist_names": row.get("artist_names", ""),
                "rank_per_range": {},
                "is_saved": True,
            }

    cache_payload = load_json(cache_path)
    if not isinstance(cache_payload, dict):
        raise RuntimeError("Cache payload is not a JSON object")

    ingest_run_id = "SPOTIFY-API-BL020"
    if export_summary_path.exists():
        summary = load_json(export_summary_path)
        if isinstance(summary, dict):
            ingest_run_id = str(summary.get("run_id", ingest_run_id))

    matched_events: list[dict[str, object]] = []
    stats = {
        "unique_spotify_tracks": len(top_tracks),
        "cache_entries": len(cache_payload),
        "tracks_with_cache": 0,
        "tagged_with_lastfm": 0,
        "no_tags": 0,
        "errors": 0,
        "missing_cache": 0,
    }

    for spotify_id, info in top_tracks.items():
        artist = str(info.get("artist_names", ""))
        title = str(info.get("track_name", ""))
        if not title.strip():
            continue

        cache_key = build_cache_key(artist, title)
        enrichment = cache_payload.get(cache_key)
        if not isinstance(enrichment, dict):
            stats["missing_cache"] += 1
            continue

        stats["tracks_with_cache"] += 1
        tags = enrichment.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        status = str(enrichment.get("status", "error"))
        if status == "ok" and tags:
            stats["tagged_with_lastfm"] += 1
        elif status == "no_tags":
            stats["no_tags"] += 1
        else:
            stats["errors"] += 1

        rank_per_range = info.get("rank_per_range", {})
        is_saved = bool(info.get("is_saved", False))
        if not rank_per_range and is_saved:
            preference_weight = round(1.0 + SAVED_BONUS, 6)
        else:
            preference_weight = compute_preference_weight(rank_per_range, is_saved)

        interaction_count = interaction_count_proxy(preference_weight)
        lead_genre = str(enrichment.get("lead_genre", ""))
        top_tag = str(enrichment.get("top_tag", lead_genre))

        matched_events.append(
            {
                "_sort_key": preference_weight,
                "track_id": f"spotify:{spotify_id}",
                "spotify_track_id": spotify_id,
                "spotify_artist": first_artist(artist),
                "spotify_title": title,
                "is_saved": is_saved,
                "rank_per_range": rank_per_range,
                "interaction_type": "history",
                "signal_source": f"{ingest_run_id}+LASTFM-PARTIAL",
                "interaction_count": interaction_count,
                "preference_weight": preference_weight,
                "lead_genre": lead_genre,
                "top_tag": top_tag,
                "lastfm_status": status,
                "lastfm_tags": tags,
                "lastfm_error": str(enrichment.get("error", "")),
            }
        )

    matched_events.sort(key=lambda e: (-float(e["_sort_key"]), str(e["spotify_title"])))

    output_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl_path.open("w", encoding="utf-8") as handle:
        for rank, event in enumerate(matched_events, start=1):
            payload = {
                "event_id": f"align_partial_{rank:05d}",
                "user_id": USER_ID,
                "track_id": event["track_id"],
                "interaction_type": event["interaction_type"],
                "signal_source": event["signal_source"],
                "interaction_count": event["interaction_count"],
                "preference_weight": event["preference_weight"],
                "seed_rank": rank,
                "lead_genre": event["lead_genre"],
                "top_tag": event["top_tag"],
                "lastfm_status": event["lastfm_status"],
                "lastfm_tags": event["lastfm_tags"],
                "lastfm_error": event["lastfm_error"],
                "spotify_track_id": event["spotify_track_id"],
                "spotify_artist": event["spotify_artist"],
                "spotify_title": event["spotify_title"],
                "is_saved": event["is_saved"],
                "rank_per_range": event["rank_per_range"],
            }
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")

    report = {
        "run_id": f"BL003-PARTIAL-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}",
        "task": "BL-003-partial",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "cache_to_partial_events",
        "input_artifacts": {
            "top_tracks_csv": str(top_path),
            "saved_tracks_csv": str(saved_path),
            "cache_json": str(cache_path),
        },
        "stats": {
            **stats,
            "aligned_events_count": len(matched_events),
            "coverage_over_total_tracks_pct": round(100.0 * len(matched_events) / max(1, len(top_tracks)), 2),
            "tag_coverage_over_partial_pct": round(100.0 * stats["tagged_with_lastfm"] / max(1, len(matched_events)), 2),
        },
        "output_artifacts": {
            "aligned_events_jsonl": str(output_jsonl_path),
            "aligned_events_count": len(matched_events),
        },
    }
    output_report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    print(f"Wrote partial events: {len(matched_events)} -> {output_jsonl_path}")
    print(f"Wrote partial report -> {output_report_path}")


if __name__ == "__main__":
    main()
