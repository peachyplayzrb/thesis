from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from .spotify_auth import complete_oauth_flow, load_token_cache, save_token_cache, token_is_usable
from .spotify_client import (
    RESILIENCE_AVAILABLE,
    CacheDB,
    RateLimitCooldownError,
    SpotifyApiClient,
    SpotifyApiError,
    fetch_all_offset_pages,
)
from .spotify_io import clamp_page_size, now_utc, repo_root, sha256_of_file, write_csv, write_json, write_jsonl
from .spotify_artifacts import build_export_artifact_paths, build_support_file_paths
from .spotify_mapping import (
    PLAYLISTS_FIELDS,
    PLAYLIST_ITEMS_FIELDS,
    RECENTLY_PLAYED_FIELDS,
    SAVED_TRACKS_FIELDS,
    TOP_TRACKS_FIELDS,
    build_playlist_item_rows,
    build_playlist_rows,
    build_recently_played_rows,
    build_saved_track_rows,
    build_top_track_rows,
)

DEFAULT_SCOPES = [
    "user-top-read",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-read-private",
    "user-read-recently-played",
]

TIME_RANGE_ORDER = ("short_term", "medium_term", "long_term")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export maximum user-accessible Spotify data for ingestion: "
            "top tracks, saved tracks, playlists, and playlist items."
        )
    )
    parser.add_argument("--client-id", default=os.getenv("SPOTIFY_CLIENT_ID", ""))
    parser.add_argument("--client-secret", default=os.getenv("SPOTIFY_CLIENT_SECRET", ""))
    parser.add_argument(
        "--redirect-uri",
        default=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8001/spotify/auth/callback"),
    )
    parser.add_argument("--scopes", default=" ".join(DEFAULT_SCOPES))
    parser.add_argument(
        "--output-dir",
        default="07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export",
    )
    parser.add_argument(
        "--token-cache",
        default="07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_token_cache.json",
    )
    parser.add_argument(
        "--env-ps1",
        default="07_implementation/implementation_notes/bl001_bl002_ingestion/configs/templates/spotify_env_template.ps1",
    )
    parser.add_argument("--request-timeout-seconds", type=int, default=60)
    parser.add_argument("--oauth-timeout-seconds", type=int, default=180)
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--max-retry-after-seconds", type=int, default=600)
    parser.add_argument("--batch-size-top-tracks", type=int, default=50)
    parser.add_argument("--batch-size-saved-tracks", type=int, default=50)
    parser.add_argument("--batch-size-playlists", type=int, default=50)
    parser.add_argument("--batch-size-playlist-items", type=int, default=50)
    parser.add_argument("--batch-pause-ms", type=int, default=250)
    parser.add_argument("--min-request-interval-ms", type=int, default=300)
    parser.add_argument("--max-requests-per-minute", type=int, default=120)
    parser.add_argument("--include-top-tracks", action="store_true")
    parser.add_argument("--include-saved-tracks", action="store_true")
    parser.add_argument("--include-playlists", action="store_true")
    parser.add_argument("--include-recently-played", action="store_true")
    parser.add_argument("--top-time-ranges", default=",".join(TIME_RANGE_ORDER))
    parser.add_argument("--top-max-items-short-term", type=int, default=0)
    parser.add_argument("--top-max-items-medium-term", type=int, default=0)
    parser.add_argument("--top-max-items-long-term", type=int, default=0)
    parser.add_argument("--saved-max-items", type=int, default=0)
    parser.add_argument("--playlists-max-items", type=int, default=0)
    parser.add_argument("--playlist-items-max-per-playlist", type=int, default=0)
    parser.add_argument("--recently-played-limit", type=int, default=50)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--force-auth", action="store_true")
    return parser.parse_args()


def _normalize_optional_cap(value: int) -> int | None:
    safe_value = max(0, int(value))
    return safe_value or None


def _normalize_requested_time_ranges(raw_value: str) -> List[str]:
    parts = [part.strip() for part in str(raw_value).split(",") if part.strip()]
    requested = [time_range for time_range in TIME_RANGE_ORDER if time_range in parts]
    return requested or list(TIME_RANGE_ORDER)


def _token_has_requested_scopes(token_payload: Dict[str, Any], requested_scopes: str) -> bool:
    granted = set(str(token_payload.get("scope", "")).split())
    requested = set(str(requested_scopes).split())
    return requested.issubset(granted)


def parse_ps1_env_file(path: Path) -> Dict[str, str]:
    pattern = re.compile(
        r"^\s*\$env:(SPOTIFY_CLIENT_ID|SPOTIFY_CLIENT_SECRET|SPOTIFY_REDIRECT_URI)\s*=\s*['\"](.*?)['\"]\s*$"
    )
    values: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def _fetch_all_data(
    client: SpotifyApiClient,
    cache_db: Any,
    args: argparse.Namespace,
) -> Dict[str, Any]:
    profile = client.api_get(path="/me", params={})
    if isinstance(profile, dict) and profile.get("id"):
        client.cache_namespace = f"uid:{profile.get('id')}"
    print(f"[profile] user_id={profile.get('id')}", flush=True)

    top_tracks_by_range: Dict[str, List[Dict[str, Any]]] = {}
    requested_time_ranges = _normalize_requested_time_ranges(args.top_time_ranges)
    time_range_caps = {
        "short_term": _normalize_optional_cap(args.top_max_items_short_term),
        "medium_term": _normalize_optional_cap(args.top_max_items_medium_term),
        "long_term": _normalize_optional_cap(args.top_max_items_long_term),
    }

    if args.include_top_tracks:
        for time_range in requested_time_ranges:
            print(f"[top_tracks] fetching time_range={time_range}", flush=True)
            tracks = fetch_all_offset_pages(
                client=client,
                cache_db=cache_db,
                path="/me/top/tracks",
                base_params={"time_range": time_range},
                limit=args.batch_size_top_tracks,
                max_items=time_range_caps.get(time_range),
            )
            top_tracks_by_range[time_range] = tracks
            print(f"[top_tracks] time_range={time_range} count={len(tracks)}", flush=True)

    saved_track_items: List[Dict[str, Any]] = []
    if args.include_saved_tracks:
        saved_track_items = fetch_all_offset_pages(
            client=client,
            cache_db=cache_db,
            path="/me/tracks",
            base_params={},
            limit=args.batch_size_saved_tracks,
            max_items=_normalize_optional_cap(args.saved_max_items),
        )
        print(f"[saved_tracks] count={len(saved_track_items)}", flush=True)

    playlists: List[Dict[str, Any]] = []
    if args.include_playlists:
        playlists = fetch_all_offset_pages(
            client=client,
            cache_db=cache_db,
            path="/me/playlists",
            base_params={},
            limit=args.batch_size_playlists,
            max_items=_normalize_optional_cap(args.playlists_max_items),
        )
        print(f"[playlists] count={len(playlists)}", flush=True)

    playlist_item_batches: List[Dict[str, Any]] = []
    if args.include_playlists:
        market = profile.get("country") if isinstance(profile, dict) else None
        for playlist in playlists:
            playlist_id = playlist.get("id")
            if not playlist_id:
                continue
            playlist_params: Dict[str, Any] = {"additional_types": "track"}
            if isinstance(market, str) and market:
                playlist_params["market"] = market
            try:
                items = fetch_all_offset_pages(
                    client=client,
                    cache_db=cache_db,
                    path=f"/playlists/{playlist_id}/items",
                    base_params=playlist_params,
                    limit=args.batch_size_playlist_items,
                    max_items=_normalize_optional_cap(args.playlist_items_max_per_playlist),
                )
            except SpotifyApiError as err:
                if err.status_code == 403:
                    print(f"[playlist_items] playlist_id={playlist_id} SKIPPED (403 Forbidden — not accessible)", flush=True)
                    continue
                raise
            print(f"[playlist_items] playlist_id={playlist_id} items={len(items)}", flush=True)
            playlist_item_batches.append({"playlist": playlist, "items": items})

    recently_played_items: List[Dict[str, Any]] = []
    if args.include_recently_played:
        limit = max(1, min(50, int(args.recently_played_limit)))
        page = client.api_get(path="/me/player/recently-played", params={"limit": limit})
        recently_played_items = page.get("items", []) if isinstance(page, dict) else []
        print(f"[recently_played] count={len(recently_played_items)}", flush=True)

    return {
        "profile": profile,
        "top_tracks_by_range": top_tracks_by_range,
        "saved_track_items": saved_track_items,
        "playlists": playlists,
        "playlist_item_batches": playlist_item_batches,
        "recently_played_items": recently_played_items,
    }


def _write_all_artifacts(
    output_dir: Path,
    data: Dict[str, Any],
    generated_at: str,
) -> Dict[str, Path]:
    top_tracks_by_range = data["top_tracks_by_range"]
    top_track_rows = build_top_track_rows(top_tracks_by_range)
    saved_track_rows = build_saved_track_rows(data["saved_track_items"])
    playlist_rows = build_playlist_rows(data["playlists"])
    playlist_item_rows = build_playlist_item_rows(data["playlist_item_batches"])
    recently_played_rows = build_recently_played_rows(data["recently_played_items"])

    artifacts = build_export_artifact_paths(output_dir)
    written_artifacts: Dict[str, Path] = {}

    write_json(artifacts["spotify_profile.json"], data["profile"])
    written_artifacts["spotify_profile.json"] = artifacts["spotify_profile.json"]

    if top_tracks_by_range:
        write_json(
            artifacts["spotify_top_tracks_by_range.json"],
            {"generated_at_utc": generated_at, "counts": {k: len(v) for k, v in top_tracks_by_range.items()}, "items": top_tracks_by_range},
        )
        write_csv(artifacts["spotify_top_tracks_flat.csv"], top_track_rows, TOP_TRACKS_FIELDS)
        written_artifacts["spotify_top_tracks_by_range.json"] = artifacts["spotify_top_tracks_by_range.json"]
        written_artifacts["spotify_top_tracks_flat.csv"] = artifacts["spotify_top_tracks_flat.csv"]

    if data["saved_track_items"]:
        write_json(
            artifacts["spotify_saved_tracks.json"],
            {"generated_at_utc": generated_at, "count": len(data["saved_track_items"]), "items": data["saved_track_items"]},
        )
        write_csv(artifacts["spotify_saved_tracks_flat.csv"], saved_track_rows, SAVED_TRACKS_FIELDS)
        written_artifacts["spotify_saved_tracks.json"] = artifacts["spotify_saved_tracks.json"]
        written_artifacts["spotify_saved_tracks_flat.csv"] = artifacts["spotify_saved_tracks_flat.csv"]

    if data["playlists"]:
        write_json(
            artifacts["spotify_playlists.json"],
            {"generated_at_utc": generated_at, "count": len(data["playlists"]), "items": data["playlists"]},
        )
        write_csv(artifacts["spotify_playlists_flat.csv"], playlist_rows, PLAYLISTS_FIELDS)
        written_artifacts["spotify_playlists.json"] = artifacts["spotify_playlists.json"]
        written_artifacts["spotify_playlists_flat.csv"] = artifacts["spotify_playlists_flat.csv"]

    if playlist_item_rows:
        write_jsonl(artifacts["spotify_playlist_items_flat.jsonl"], playlist_item_rows)
        write_csv(artifacts["spotify_playlist_items_flat.csv"], playlist_item_rows, PLAYLIST_ITEMS_FIELDS)
        written_artifacts["spotify_playlist_items_flat.jsonl"] = artifacts["spotify_playlist_items_flat.jsonl"]
        written_artifacts["spotify_playlist_items_flat.csv"] = artifacts["spotify_playlist_items_flat.csv"]

    if data["recently_played_items"]:
        write_json(
            artifacts["spotify_recently_played.json"],
            {"generated_at_utc": generated_at, "count": len(data["recently_played_items"]), "items": data["recently_played_items"]},
        )
        write_csv(artifacts["spotify_recently_played_flat.csv"], recently_played_rows, RECENTLY_PLAYED_FIELDS)
        written_artifacts["spotify_recently_played.json"] = artifacts["spotify_recently_played.json"]
        written_artifacts["spotify_recently_played_flat.csv"] = artifacts["spotify_recently_played_flat.csv"]

    return written_artifacts


def _clear_previous_export_artifacts(output_dir: Path) -> None:
    artifacts = build_export_artifact_paths(output_dir)
    support_paths = build_support_file_paths(output_dir)
    removable_paths = list(artifacts.values()) + [support_paths["request_log"], support_paths["summary"], support_paths["rate_limit_block"]]
    # Remove legacy recommendation artifacts from older runs.
    removable_paths.extend([
        output_dir / "spotify_top_artists_by_range.json",
        output_dir / "spotify_top_artists_flat.csv",
        output_dir / "spotify_recommendations.json",
        output_dir / "spotify_recommendations_flat.csv",
    ])
    for path in removable_paths:
        if path.exists():
            path.unlink()


def main() -> None:
    args = parse_args()
    root = repo_root()
    print("[start] spotify export initializing", flush=True)

    for attr in ("batch_size_top_tracks", "batch_size_saved_tracks", "batch_size_playlists", "batch_size_playlist_items"):
        setattr(args, attr, clamp_page_size(getattr(args, attr)))
    args.batch_pause_ms = max(0, int(args.batch_pause_ms))
    args.min_request_interval_ms = max(0, int(args.min_request_interval_ms))
    args.max_requests_per_minute = max(1, int(args.max_requests_per_minute))

    if args.env_ps1:
        env_path = root / args.env_ps1
        if env_path.exists():
            parsed = parse_ps1_env_file(env_path)
            if not args.client_id:
                args.client_id = parsed.get("SPOTIFY_CLIENT_ID", args.client_id)
            if not args.client_secret:
                args.client_secret = parsed.get("SPOTIFY_CLIENT_SECRET", args.client_secret)
            if args.redirect_uri == "http://127.0.0.1:8001/spotify/auth/callback" and parsed.get("SPOTIFY_REDIRECT_URI"):
                args.redirect_uri = parsed["SPOTIFY_REDIRECT_URI"]
            print(f"[config] loaded env file: {args.env_ps1}", flush=True)
        else:
            print(f"[config] env file not found, skipping: {args.env_ps1}", flush=True)

    if not args.client_id or not args.client_secret:
        raise ValueError(
            "Missing Spotify credentials. Provide --client-id/--client-secret or SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET."
        )

    if not any((
        args.include_top_tracks,
        args.include_saved_tracks,
        args.include_playlists,
        args.include_recently_played,
    )):
        args.include_top_tracks = True
        args.include_saved_tracks = True
        args.include_playlists = True

    output_dir = root / args.output_dir
    token_cache_path = root / args.token_cache
    output_dir.mkdir(parents=True, exist_ok=True)
    _clear_previous_export_artifacts(output_dir)

    token_payload: Dict[str, Any] = {}
    if not args.force_auth:
        token_payload = load_token_cache(token_cache_path)

    if token_is_usable(token_payload) and not _token_has_requested_scopes(token_payload, args.scopes):
        print("[auth] cached token missing requested scopes, starting token flow", flush=True)
        token_payload = complete_oauth_flow(args)
        print("[auth] oauth authorization complete", flush=True)
    elif not token_is_usable(token_payload):
        print("[auth] no usable cached token, starting token flow", flush=True)
        if token_payload.get("refresh_token") and not args.force_auth:
            temp_client = SpotifyApiClient(args=args, token_payload=token_payload)
            temp_client.refresh_access_token()
            token_payload = temp_client.token_payload
            print("[auth] refreshed cached token", flush=True)
        else:
            token_payload = complete_oauth_flow(args)
            print("[auth] oauth authorization complete", flush=True)
    else:
        print("[auth] using cached access token", flush=True)

    save_token_cache(token_cache_path, token_payload)
    client = SpotifyApiClient(args=args, token_payload=token_payload)

    support_paths = build_support_file_paths(output_dir)
    cache_db_path = support_paths["cache_db"]
    cache_db: Any = None
    if RESILIENCE_AVAILABLE:
        print("[resilience] initializing SQLite cache", flush=True)
        cache_db = CacheDB(str(cache_db_path))
    else:
        print("[resilience] caching disabled", flush=True)

    run_started = time.time()
    run_id = f"SPOTIFY-EXPORT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    print(f"[run] run_id={run_id}", flush=True)
    print(
        f"[config] batches top={args.batch_size_top_tracks} saved={args.batch_size_saved_tracks} "
        f"playlists={args.batch_size_playlists} playlist_items={args.batch_size_playlist_items} "
        f"batch_pause_ms={args.batch_pause_ms}",
        flush=True,
    )
    print(
        f"[config] rate_limit min_request_interval_ms={args.min_request_interval_ms} "
        f"max_requests_per_minute={args.max_requests_per_minute} max_retries={args.max_retries}",
        flush=True,
    )

    try:
        data = _fetch_all_data(client=client, cache_db=cache_db, args=args)
    except RateLimitCooldownError as error:
        retry_at = datetime.now(timezone.utc) + timedelta(seconds=error.retry_after_seconds)
        write_json(
            support_paths["rate_limit_block"],
            {
                "task": "BL-002-spotify-api-export",
                "run_id": run_id,
                "generated_at_utc": now_utc(),
                "status": "blocked_by_rate_limit",
                "path": error.path,
                "retry_after_seconds": error.retry_after_seconds,
                "retry_at_utc": retry_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "guidance": "Wait until retry_at_utc or rotate to a new Spotify app client id/secret and re-authenticate.",
            },
        )
        print(f"[blocked] {error}", flush=True)
        print(f"[blocked] retry_at_utc={retry_at.strftime('%Y-%m-%dT%H:%M:%SZ')}", flush=True)
        raise

    generated_at = now_utc()
    artifacts = _write_all_artifacts(output_dir=output_dir, data=data, generated_at=generated_at)

    request_log_path = support_paths["request_log"]
    write_jsonl(request_log_path, client.request_log)
    artifacts["spotify_request_log.jsonl"] = request_log_path

    elapsed_seconds = round(time.time() - run_started, 3)
    top_by_range = data["top_tracks_by_range"]
    endpoint_counts = {
        "top_tracks_short_term": len(top_by_range.get("short_term", [])),
        "top_tracks_medium_term": len(top_by_range.get("medium_term", [])),
        "top_tracks_long_term": len(top_by_range.get("long_term", [])),
        "saved_tracks": len(data["saved_track_items"]),
        "playlists": len(data["playlists"]),
        "playlist_items": sum(len(batch.get("items", [])) for batch in data["playlist_item_batches"]),
        "recently_played": len(data["recently_played_items"]),
        "api_calls_logged": len(client.request_log),
    }

    summary = {
        "task": "BL-002-spotify-api-export",
        "run_id": run_id,
        "generated_at_utc": generated_at,
        "oauth": {
            "redirect_uri": args.redirect_uri,
            "scopes_requested": args.scopes.split(),
            "scope_granted": str(token_payload.get("scope", "")).split(),
        },
        "account_profile": {
            "spotify_user_id": data["profile"].get("id"),
            "country": data["profile"].get("country"),
            "product": data["profile"].get("product"),
        },
        "counts": endpoint_counts,
        "selection": {
            "include_top_tracks": args.include_top_tracks,
            "include_saved_tracks": args.include_saved_tracks,
            "include_playlists": args.include_playlists,
            "include_recently_played": args.include_recently_played,
            "top_time_ranges": _normalize_requested_time_ranges(args.top_time_ranges),
            "top_caps": {
                "short_term": _normalize_optional_cap(args.top_max_items_short_term),
                "medium_term": _normalize_optional_cap(args.top_max_items_medium_term),
                "long_term": _normalize_optional_cap(args.top_max_items_long_term),
            },
            "saved_max_items": _normalize_optional_cap(args.saved_max_items),
            "playlists_max_items": _normalize_optional_cap(args.playlists_max_items),
            "playlist_items_max_per_playlist": _normalize_optional_cap(args.playlist_items_max_per_playlist),
            "recently_played_limit": max(1, min(50, int(args.recently_played_limit))),
        },
        "elapsed_seconds": elapsed_seconds,
        "resilience": {
            "cache_enabled": RESILIENCE_AVAILABLE and cache_db is not None,
            "cache_db_path": str(cache_db_path.relative_to(root)).replace("\\", "/") if cache_db is not None else None,
            "cache_note": "SQLite cache with 24-hour TTL for static endpoints; enables fast re-runs",
        },
        "artifacts": {
            name: {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "sha256": sha256_of_file(path),
                "bytes": path.stat().st_size,
            }
            for name, path in artifacts.items()
        },
        "notes": {
            "api_reference_basis": [
                "Authorization Code Flow tutorial",
                "Get User's Top Items",
                "Get User's Saved Tracks",
                "Get Current User's Playlists",
                "Get Playlist Items",
            ],
            "policy_note": "Use data for personal ingestion and thesis analysis; do not redistribute Spotify content.",
        },
    }

    summary_path = support_paths["summary"]
    write_json(summary_path, summary)
    print("[write] summary file written", flush=True)
    save_token_cache(token_cache_path, token_payload)

    print(f"Spotify export complete: run_id={run_id}")
    print(f"top_tracks_short_term={endpoint_counts['top_tracks_short_term']}")
    print(f"top_tracks_medium_term={endpoint_counts['top_tracks_medium_term']}")
    print(f"top_tracks_long_term={endpoint_counts['top_tracks_long_term']}")
    print(f"saved_tracks={endpoint_counts['saved_tracks']}")
    print(f"playlists={endpoint_counts['playlists']}")
    print(f"playlist_items={endpoint_counts['playlist_items']}")
    print(f"recently_played={endpoint_counts['recently_played']}")
    print(f"summary={summary_path}")


if __name__ == "__main__":
    try:
        main()
    except RateLimitCooldownError:
        sys.exit(2)
