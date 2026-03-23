"""
BL-003: Enrich Spotify API export with Last.fm top tags.

Reads:
    - spotify_top_tracks_flat.csv   (time-range ranked top tracks)
    - spotify_saved_tracks_flat.csv (manually saved tracks)

Produces:
    - bl020_aligned_events.jsonl    (semantic seed events for BL-004 input)
    - bl020_alignment_report.json   (enrichment statistics and provenance)
    - bl020_lastfm_tag_cache.json   (persistent Last.fm response cache)

This replaces the failed DS-002 fuzzy alignment path. Spotify audio-feature
endpoints are deprecated, so BL-020 now derives a real user preference profile
from Last.fm top tags on the imported Spotify tracks, then matches that semantic
profile against DS-002 candidate tags downstream.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths (relative to repo root)
# ---------------------------------------------------------------------------
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
OUTPUT_JSONL = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/bl020_aligned_events.jsonl"
)
OUTPUT_REPORT = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/bl020_alignment_report.json"
)
CACHE_JSON = (
    "07_implementation/implementation_notes/ingestion/outputs"
    "/bl020_lastfm_tag_cache.json"
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TIME_RANGE_WEIGHTS = {
    "short_term":  0.50,
    "medium_term": 0.30,
    "long_term":   0.20,
}
TIME_RANGE_MAX = {
    "short_term":  598,
    "medium_term": 3021,
    "long_term":   5104,
}
SAVED_BONUS    = 0.05
USER_ID = "21zsn42xecjhogne4kghyw5hq"
LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"
REQUEST_TIMEOUT_SECONDS = 20
MIN_REQUEST_INTERVAL_SECONDS = 0.25
MAX_TAGS_PER_TRACK = 10
CACHE_FLUSH_INTERVAL = 100
CACHE_SCHEMA_VERSION = 2

# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------
_RE_FEAT    = re.compile(r"\s*[\(\[]\s*(?:feat|ft|featuring)\b[^\)\]]*[\)\]]", re.I)
_RE_VERSION = re.compile(
    r"(\s+-\s+|\s+\()(?:remaster|remix|live|version|edit|mix|demo|acoustic|"
    r"deluxe|anniversary|radio|single|original|instrumental|bonus|"
    r"super deluxe|reprise|recorded\b|alternate|alt[. ])\b.*$",
    re.I,
)
_RE_YEAR_DASH = re.compile(r"\s+-\s+\d{4}.*$")       # " - 2017 Mix", " - Live 1988"
_RE_OP_NUMBER = re.compile(r",?\s+(?:op|k|bwv|hwv|rv)\s*\.?\s*\d+.*$", re.I)  # classical
_RE_ACT_NO    = re.compile(r",?\s+act\s+[ivxlc\d]+.*$", re.I)                  # opera
_RE_NONALPHA  = re.compile(r"[^a-z0-9 ]")


def normalise(text: str) -> str:
    """Lowercase, transliterate, strip version/feat/opus markers, collapse spaces."""
    s = unicodedata.normalize("NFKD", text)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = _RE_FEAT.sub("", s)
    s = _RE_OP_NUMBER.sub("", s)    # strip classical opus numbers
    s = _RE_ACT_NO.sub("", s)       # strip opera act markers
    s = _RE_VERSION.sub("", s)
    s = _RE_YEAR_DASH.sub("", s)
    s = _RE_NONALPHA.sub(" ", s)
    # strip leading "the "
    if s.startswith("the "):
        s = s[4:]
    return " ".join(s.split())


def lookup_text(text: str) -> str:
    """Prepare artist/title text for external metadata lookups."""
    s = unicodedata.normalize("NFKD", text)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = _RE_FEAT.sub("", s)
    s = _RE_OP_NUMBER.sub("", s)
    s = _RE_ACT_NO.sub("", s)
    s = _RE_VERSION.sub("", s)
    s = _RE_YEAR_DASH.sub("", s)
    return " ".join(s.split()).strip(" -")


def unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        text = item.strip()
        key = text.lower()
        if not text or key in seen:
            continue
        seen.add(key)
        ordered.append(text)
    return ordered


def build_artist_variants(artist: str) -> list[str]:
    primary = first_artist(artist)
    return unique_preserve_order([primary, lookup_text(primary)])


def build_title_variants(title: str) -> list[str]:
    cleaned = lookup_text(title)
    return unique_preserve_order([title, cleaned])


def first_artist(pipe_separated: str) -> str:
    """Return the first (primary) artist from a pipe-separated list."""
    return pipe_separated.split("|")[0].strip()


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------
def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BL-003 Last.fm enrichment for Spotify seed tracks")
    parser.add_argument(
        "--api-key",
        default=os.getenv("LASTFM_API_KEY", ""),
        help="Last.fm API key. Defaults to LASTFM_API_KEY environment variable.",
    )
    return parser.parse_args()


def load_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def build_cache_key(artist: str, title: str) -> str:
    return f"{normalise(first_artist(artist))}::{normalise(title)}"


def normalise_lastfm_tags(payload: object) -> list[dict[str, object]]:
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return []

    parsed: list[tuple[str, int]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        count = item.get("count", 0)
        if not isinstance(name, str) or not name.strip():
            continue
        try:
            count_value = int(count)
        except (TypeError, ValueError):
            continue
        if count_value <= 0:
            continue
        parsed.append((name.strip().lower(), count_value))

    if not parsed:
        return []

    parsed.sort(key=lambda item: (-item[1], item[0]))
    parsed = parsed[:MAX_TAGS_PER_TRACK]
    max_count = max(item[1] for item in parsed)
    return [
        {
            "tag": label,
            "weight": round(count / max_count, 6),
            "count": count,
        }
        for label, count in parsed
    ]


def request_lastfm_method(api_key: str, params: dict[str, str]) -> dict[str, object]:
    request = urllib.request.Request(
        f"{LASTFM_API_URL}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "thesis-music-recommender/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return {"ok": True, "payload": json.loads(response.read().decode("utf-8"))}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {"ok": False, "error": f"HTTP {error.code}: {body[:200]}"}
    except Exception as error:  # pragma: no cover
        return {"ok": False, "error": str(error)}


def extract_tags_response(payload: object) -> dict[str, object]:
    if isinstance(payload, dict) and payload.get("error"):
        return {
            "status": "error",
            "error": str(payload.get("message", payload["error"])),
            "tags": [],
        }

    tags = normalise_lastfm_tags(payload.get("toptags", {}).get("tag", [])) if isinstance(payload, dict) else []
    if not tags:
        return {"status": "no_tags", "error": "", "tags": []}

    return {
        "status": "ok",
        "error": "",
        "tags": tags,
        "lead_genre": str(tags[0]["tag"]),
        "top_tag": str(tags[0]["tag"]),
    }


def search_lastfm_track(api_key: str, artist: str, title: str) -> tuple[str, str] | None:
    result = request_lastfm_method(
        api_key,
        {
            "method": "track.search",
            "artist": artist,
            "track": title,
            "limit": "5",
            "api_key": api_key,
            "format": "json",
        },
    )
    if not result.get("ok"):
        return None

    payload = result.get("payload")
    matches = payload.get("results", {}).get("trackmatches", {}).get("track", []) if isinstance(payload, dict) else []
    if isinstance(matches, dict):
        matches = [matches]
    if not isinstance(matches, list):
        return None

    artist_norm = normalise(artist)
    title_norm = normalise(title)
    for match in matches:
        if not isinstance(match, dict):
            continue
        candidate_artist = str(match.get("artist", "")).strip()
        candidate_title = str(match.get("name", "")).strip()
        if not candidate_artist or not candidate_title:
            continue
        if normalise(candidate_artist) == artist_norm and normalise(candidate_title) == title_norm:
            return candidate_artist, candidate_title

    first_match = matches[0] if matches else None
    if isinstance(first_match, dict):
        candidate_artist = str(first_match.get("artist", "")).strip()
        candidate_title = str(first_match.get("name", "")).strip()
        if candidate_artist and candidate_title:
            return candidate_artist, candidate_title
    return None


def request_lastfm_top_tags(api_key: str, artist: str, title: str) -> dict[str, object]:
    errors: list[str] = []
    for artist_variant in build_artist_variants(artist):
        for title_variant in build_title_variants(title):
            result = request_lastfm_method(
                api_key,
                {
                    "method": "track.getTopTags",
                    "artist": artist_variant,
                    "track": title_variant,
                    "autocorrect": "1",
                    "api_key": api_key,
                    "format": "json",
                },
            )
            if not result.get("ok"):
                errors.append(str(result.get("error", "unknown error")))
                continue
            parsed = extract_tags_response(result.get("payload"))
            if parsed["status"] == "ok":
                parsed["lookup_source"] = "track.getTopTags"
                parsed["lookup_artist"] = artist_variant
                parsed["lookup_title"] = title_variant
                parsed["cache_version"] = CACHE_SCHEMA_VERSION
                return parsed

    corrected = search_lastfm_track(api_key, build_artist_variants(artist)[-1], build_title_variants(title)[-1])
    if corrected is not None:
        corrected_artist, corrected_title = corrected
        result = request_lastfm_method(
            api_key,
            {
                "method": "track.getTopTags",
                "artist": corrected_artist,
                "track": corrected_title,
                "autocorrect": "1",
                "api_key": api_key,
                "format": "json",
            },
        )
        if result.get("ok"):
            parsed = extract_tags_response(result.get("payload"))
            if parsed["status"] == "ok":
                parsed["lookup_source"] = "track.search->track.getTopTags"
                parsed["lookup_artist"] = corrected_artist
                parsed["lookup_title"] = corrected_title
                parsed["cache_version"] = CACHE_SCHEMA_VERSION
                return parsed
        else:
            errors.append(str(result.get("error", "unknown error")))

    for artist_variant in build_artist_variants(artist):
        result = request_lastfm_method(
            api_key,
            {
                "method": "artist.getTopTags",
                "artist": artist_variant,
                "autocorrect": "1",
                "api_key": api_key,
                "format": "json",
            },
        )
        if not result.get("ok"):
            errors.append(str(result.get("error", "unknown error")))
            continue
        parsed = extract_tags_response(result.get("payload"))
        if parsed["status"] == "ok":
            parsed["lookup_source"] = "artist.getTopTags"
            parsed["lookup_artist"] = artist_variant
            parsed["lookup_title"] = ""
            parsed["cache_version"] = CACHE_SCHEMA_VERSION
            return parsed

    if errors:
        return {"status": "error", "error": errors[-1], "tags": [], "cache_version": CACHE_SCHEMA_VERSION}
    return {"status": "no_tags", "error": "", "tags": [], "cache_version": CACHE_SCHEMA_VERSION}


def request_lastfm_top_tags_fast(
    api_key: str,
    artist: str,
    title: str,
    artist_fallback_cache: dict[str, dict[str, object]],
) -> dict[str, object]:
    """
    Fast wrapper around track-level lookup.

    It first attempts the full track-level resolution path. If that fails to produce
    tags, it reuses an in-memory artist-level fallback cache so repeated tracks from
    the same artist do not trigger duplicate artist.getTopTags requests.
    """
    artist_key = normalise(first_artist(artist))
    cached_artist = artist_fallback_cache.get(artist_key)
    if isinstance(cached_artist, dict):
        reused = dict(cached_artist)
        reused["lookup_source"] = "artist.getTopTags(cache)"
        reused["cache_version"] = CACHE_SCHEMA_VERSION
        return reused

    track_result = request_lastfm_top_tags(api_key, artist, title)
    if track_result.get("status") == "ok":
        return track_result

    # No reusable artist fallback in memory; return track result as-is.
    return track_result


# ---------------------------------------------------------------------------
# Preference weight
# ---------------------------------------------------------------------------
def compute_preference_weight(
    rank_per_range: dict[str, int],
    is_saved: bool,
) -> float:
    """Weighted combination of normalised rank scores across time ranges."""
    combined = 0.0
    for tr, weight in TIME_RANGE_WEIGHTS.items():
        rank = rank_per_range.get(tr)
        if rank is None:
            continue
        max_rank = TIME_RANGE_MAX[tr]
        normalised = (max_rank - rank) / max_rank        # 1-(rank-1)/max where rank 1→ (max-1)/max ≈ 1.0
        combined += weight * normalised
    pref = 1.0 + combined
    if is_saved:
        pref = min(2.0, pref + SAVED_BONUS)
    return round(pref, 6)


def interaction_count_proxy(preference_weight: float) -> int:
    """Synthesise a play-count proxy from preference weight (range ~1–200000)."""
    return max(1, round((preference_weight - 1.0) * 200000))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    args = parse_args()
    if not args.api_key:
        raise RuntimeError("Missing Last.fm API key. Set LASTFM_API_KEY or pass --api-key.")

    root = repo_root()
    t0 = time.time()

    # Resolve paths
    top_path    = root / TOP_TRACKS_CSV
    saved_path  = root / SAVED_TRACKS_CSV
    out_jsonl   = root / OUTPUT_JSONL
    out_report  = root / OUTPUT_REPORT
    export_sum  = root / EXPORT_SUMMARY_JSON
    cache_path  = root / CACHE_JSON

    for p in (top_path, saved_path):
        if not p.exists():
            raise FileNotFoundError(f"Required input not found: {p}")

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    # Load export run_id for provenance
    ingest_run_id = "SPOTIFY-API-BL020"
    if export_sum.exists():
        try:
            ingest_run_id = json.loads(export_sum.read_text(encoding="utf-8")).get(
                "run_id", ingest_run_id
            )
        except Exception:
            pass

    cache_payload = load_json(cache_path, {})
    if not isinstance(cache_payload, dict):
        cache_payload = {}

    # Reuse successful artist-level fallbacks across tracks in this run.
    artist_fallback_cache: dict[str, dict[str, object]] = {}
    for cached in cache_payload.values():
        if not isinstance(cached, dict):
            continue
        if cached.get("status") != "ok":
            continue
        if str(cached.get("lookup_source", "")).startswith("artist.getTopTags"):
            artist_name = str(cached.get("lookup_artist", "")).strip()
            if artist_name:
                artist_fallback_cache[normalise(artist_name)] = cached

    # top_tracks: {spotify_track_id -> {track_name, artist_names, rank_per_range}}
    top_tracks: dict[str, dict] = {}

    print("Loading Spotify top tracks ...", flush=True)
    for row in load_csv(top_path):
        sid   = row.get("track_id", "").strip()
        tr    = row.get("time_range", "").strip()
        rank  = row.get("rank", "").strip()
        if not sid or not tr or not rank:
            continue
        try:
            rank_int = int(rank)
        except ValueError:
            continue
        if sid not in top_tracks:
            top_tracks[sid] = {
                "track_name":   row.get("track_name", ""),
                "artist_names": row.get("artist_names", ""),
                "duration_ms":  row.get("duration_ms", "0"),
                "isrc":         row.get("isrc", ""),
                "rank_per_range": {},
                "is_saved": False,
            }
        top_tracks[sid]["rank_per_range"][tr] = rank_int

    print(f"  Unique Spotify top-track entries: {len(top_tracks)}", flush=True)

    # saved tracks: flag existing top tracks or add new entries
    print("Loading Spotify saved tracks ...", flush=True)
    saved_count = 0
    for row in load_csv(saved_path):
        sid = row.get("track_id", "").strip()
        if not sid:
            continue
        if sid in top_tracks:
            top_tracks[sid]["is_saved"] = True
        else:
            top_tracks[sid] = {
                "track_name":   row.get("track_name", ""),
                "artist_names": row.get("artist_names", ""),
                "duration_ms":  row.get("duration_ms", "0"),
                "isrc":         row.get("isrc", ""),
                "rank_per_range": {},
                "is_saved": True,
            }
        saved_count += 1
    print(f"  Saved tracks processed: {saved_count}", flush=True)

    # -----------------------------------------------------------------------
    # Last.fm enrichment
    # -----------------------------------------------------------------------
    total_tracks = len(top_tracks)
    print(f"Enriching {total_tracks} unique tracks with Last.fm top tags ...", flush=True)
    matched_events: list[dict] = []
    stats = {
        "total_attempted": 0,
        "enriched": 0,
        "no_tags": 0,
        "errors": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "failure_examples": [],
    }
    last_request_epoch = 0.0
    interrupted = False

    for index, (spotify_id, info) in enumerate(top_tracks.items(), start=1):
        try:
            stats["total_attempted"] += 1
            artist = info["artist_names"]
            title  = info["track_name"]
            if not title.strip():
                stats["no_tags"] += 1
                continue

            cache_key = build_cache_key(artist, title)
            cached = cache_payload.get(cache_key)
            cached_is_current = (
                isinstance(cached, dict)
                and int(cached.get("cache_version", 0)) >= CACHE_SCHEMA_VERSION
            )
            if cached_is_current:
                enrichment = cached
                stats["cache_hits"] += 1
            else:
                now = time.time()
                sleep_seconds = MIN_REQUEST_INTERVAL_SECONDS - (now - last_request_epoch)
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)
                enrichment = request_lastfm_top_tags_fast(
                    args.api_key,
                    artist,
                    title,
                    artist_fallback_cache,
                )
                last_request_epoch = time.time()
                cache_payload[cache_key] = enrichment
                if enrichment.get("status") == "ok" and str(enrichment.get("lookup_source", "")).startswith("artist.getTopTags"):
                    artist_lookup = str(enrichment.get("lookup_artist", "")).strip() or first_artist(artist)
                    artist_fallback_cache[normalise(artist_lookup)] = enrichment
                stats["cache_misses"] += 1
                if stats["cache_misses"] % CACHE_FLUSH_INTERVAL == 0:
                    write_json(cache_path, cache_payload)

            if not info["rank_per_range"] and info["is_saved"]:
                pref_weight = round(1.0 + SAVED_BONUS, 6)
            else:
                pref_weight = compute_preference_weight(info["rank_per_range"], info["is_saved"])
            interaction_count = interaction_count_proxy(pref_weight)

            tags = enrichment.get("tags", []) if isinstance(enrichment, dict) else []
            if not isinstance(tags, list):
                tags = []
            lead_genre = str(enrichment.get("lead_genre", "")) if isinstance(enrichment, dict) else ""
            top_tag = str(enrichment.get("top_tag", lead_genre)) if isinstance(enrichment, dict) else lead_genre
            status = str(enrichment.get("status", "error")) if isinstance(enrichment, dict) else "error"

            if status == "ok" and tags:
                stats["enriched"] += 1
            elif status == "no_tags":
                stats["no_tags"] += 1
            else:
                stats["errors"] += 1
                if len(stats["failure_examples"]) < 20:
                    stats["failure_examples"].append(
                        {
                            "spotify_track_id": spotify_id,
                            "artist": first_artist(artist),
                            "title": title,
                            "status": status,
                            "error": str(enrichment.get("error", "")) if isinstance(enrichment, dict) else "",
                        }
                    )

            matched_events.append(
                {
                    "_sort_key": pref_weight,
                    "track_id":         f"spotify:{spotify_id}",
                    "spotify_track_id": spotify_id,
                    "spotify_artist":   first_artist(artist),
                    "spotify_title":    title,
                    "is_saved":         info["is_saved"],
                    "rank_per_range":   info["rank_per_range"],
                    "interaction_type": "history",
                    "signal_source":    f"{ingest_run_id}+LASTFM",
                    "interaction_count": interaction_count,
                    "preference_weight": pref_weight,
                    "lead_genre":       lead_genre,
                    "top_tag":          top_tag,
                    "lastfm_status":    status,
                    "lastfm_tags":      tags,
                    "lastfm_error":     str(enrichment.get("error", "")) if isinstance(enrichment, dict) else "",
                }
            )

            cache_total = stats["cache_hits"] + stats["cache_misses"]
            cache_hit_pct = (100.0 * stats["cache_hits"] / cache_total) if cache_total else 0.0
            print(
                f"  progress {index}/{total_tracks} | tagged={stats['enriched']} "
                f"no_tags={stats['no_tags']} errors={stats['errors']} "
                f"cache_hit={cache_hit_pct:.1f}%"
            , flush=True)
        except KeyboardInterrupt:
            interrupted = True
            print(
                f"Interrupted at {index}/{total_tracks}. "
                f"Writing partial outputs for {len(matched_events)} processed tracks ...",
                flush=True,
            )
            write_json(cache_path, cache_payload)
            break

    # Sort by preference_weight desc, assign seed_rank
    matched_events.sort(key=lambda e: (-e["_sort_key"], e["spotify_title"]))
    print(
        f"Enrichment results: {stats['enriched']} tagged / "
        f"{stats['no_tags']} no-tags / {stats['errors']} errors out of {stats['total_attempted']}"
    , flush=True)

    # -----------------------------------------------------------------------
    # Write JSONL
    # -----------------------------------------------------------------------
    run_id = f"BL003-ALIGN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    with out_jsonl.open("w", encoding="utf-8") as f:
        for rank, event in enumerate(matched_events, start=1):
            payload: dict = {
                "event_id":          f"align_{rank:05d}",
                "user_id":           USER_ID,
                "track_id":          event["track_id"],
                "interaction_type":  event["interaction_type"],
                "signal_source":     event["signal_source"],
                "interaction_count": event["interaction_count"],
                "preference_weight": event["preference_weight"],
                "seed_rank":         rank,
                "lead_genre":        event["lead_genre"],
                "top_tag":           event["top_tag"],
                "lastfm_status":     event["lastfm_status"],
                "lastfm_tags":       event["lastfm_tags"],
                "lastfm_error":      event["lastfm_error"],
                "spotify_track_id":  event["spotify_track_id"],
                "spotify_artist":    event["spotify_artist"],
                "spotify_title":     event["spotify_title"],
                "is_saved":          event["is_saved"],
                "rank_per_range":    event["rank_per_range"],
            }
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    elapsed = round(time.time() - t0, 2)
    write_json(cache_path, cache_payload)
    print(f"Wrote {len(matched_events)} semantic seed events -> {out_jsonl}", flush=True)

    # -----------------------------------------------------------------------
    # Write report
    # -----------------------------------------------------------------------
    report = {
        "run_id":           run_id,
        "task":             "BL-003",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_seconds":  elapsed,
        "interrupted":      interrupted,
        "user_id":          USER_ID,
        "mode":             "lastfm_tag_enrichment",
        "input_artifacts": {
            "top_tracks_csv":    str(top_path),
            "top_tracks_sha256": sha256_file(top_path),
            "saved_tracks_csv":  str(saved_path),
            "saved_tracks_sha256": sha256_file(saved_path),
        },
        "stats": {
            "unique_spotify_tracks":  stats["total_attempted"],
            "tagged_with_lastfm":     stats["enriched"],
            "no_tags":                stats["no_tags"],
            "request_errors":         stats["errors"],
            "tag_coverage_pct":       round(
                100 * stats["enriched"] / max(1, stats["total_attempted"]), 2
            ),
            "cache_hits":             stats["cache_hits"],
            "cache_misses":           stats["cache_misses"],
            "saved_tracks_flagged":   saved_count,
        },
        "failure_examples": stats["failure_examples"],
        "output_artifacts": {
            "aligned_events_jsonl": str(out_jsonl),
            "aligned_events_count": len(matched_events),
            "lastfm_cache_json": str(cache_path),
        },
    }
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Report written -> {out_report}", flush=True)


if __name__ == "__main__":
    main()
