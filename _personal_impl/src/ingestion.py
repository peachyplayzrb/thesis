from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import re
import secrets
import shutil
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple



DEFAULT_INGESTION_CONTROLS: dict[str, object] = {

    "cache_ttl_seconds": 60 * 60 * 24,
    "throttle_sleep_seconds": 0.12,
    "max_retries": 6,
    "base_backoff_delay_seconds": 1.0,
}


def impl_root(impl_root_override: str | None = None) -> Path:
    if impl_root_override:
        return Path(impl_root_override).resolve()
    env_root = os.environ.get("IMPL_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parents[1]


def cache_ttl_exceeded(mtime_utc: datetime, cutoff_utc: datetime | None) -> bool:
    if cutoff_utc is None:
        return False
    return mtime_utc < cutoff_utc


def normalize_text(value: str | None, *, lowercase: bool = True) -> str:
    if value is None:
        return ""
    text = " ".join(str(value).split())
    if lowercase:
        text = text.lower()
    return text

ACCOUNTS_BASE_URL = "https://accounts.spotify.com"
API_BASE_URL = "https://api.spotify.com/v1"

DEFAULT_SCOPES = [
    "user-top-read",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-read-private",
    "user-read-recently-played",
]

TIME_RANGE_ORDER = ("short_term", "medium_term", "long_term")
EXPORT_SCHEMA_VERSION = "2026-03-28"

REQUEST_LOG_LIMIT_DEFAULT = 20000

TOP_TRACKS_FIELDS = [
    "time_range",
    "rank",
    "track_id",
    "track_uri",
    "track_name",
    "artist_ids",
    "artist_names",
    "album_id",
    "album_name",
    "release_date",
    "release_date_precision",
    "duration_ms",
    "duration_seconds",
    "popularity",
    "explicit",
    "is_playable",
    "restriction_reason",
    "linked_from_track_id",
    "isrc",
    "track_href",
    "track_external_url",
]

SAVED_TRACKS_FIELDS = [
    "added_at",
    "track_id",
    "track_uri",
    "track_name",
    "artist_ids",
    "artist_names",
    "album_id",
    "album_name",
    "release_date",
    "release_date_precision",
    "duration_ms",
    "duration_seconds",
    "popularity",
    "explicit",
    "is_playable",
    "restriction_reason",
    "linked_from_track_id",
    "isrc",
    "track_href",
    "track_external_url",
]

PLAYLISTS_FIELDS = [
    "playlist_id",
    "playlist_name",
    "owner_id",
    "collaborative",
    "public",
    "tracks_total",
    "items_access_status",
    "items_skipped_reason",
    "snapshot_id",
    "uri",
]

PLAYLIST_ITEMS_FIELDS = [
    "playlist_id",
    "playlist_name",
    "playlist_position",
    "added_at",
    "added_by",
    "is_local",
    "track_id",
    "track_uri",
    "track_name",
    "artist_ids",
    "artist_names",
    "album_id",
    "album_name",
    "release_date",
    "release_date_precision",
    "duration_ms",
    "duration_seconds",
    "popularity",
    "explicit",
    "is_playable",
    "restriction_reason",
    "linked_from_track_id",
    "isrc",
    "track_href",
    "track_external_url",
]

RECENTLY_PLAYED_FIELDS = [
    "played_at",
    "context_type",
    "context_uri",
    "track_id",
    "track_uri",
    "track_name",
    "artist_ids",
    "artist_names",
    "album_id",
    "album_name",
    "release_date",
    "release_date_precision",
    "duration_ms",
    "duration_seconds",
    "popularity",
    "explicit",
    "is_playable",
    "restriction_reason",
    "linked_from_track_id",
    "isrc",
    "track_href",
    "track_external_url",
]

EXPORT_ARTIFACT_FILENAMES = {
    "spotify_profile.json": "spotify_profile.json",
    "spotify_top_tracks_by_range.json": "spotify_top_tracks_by_range.json",
    "spotify_top_tracks_flat.csv": "spotify_top_tracks_flat.csv",
    "spotify_saved_tracks.json": "spotify_saved_tracks.json",
    "spotify_saved_tracks_flat.csv": "spotify_saved_tracks_flat.csv",
    "spotify_playlists.json": "spotify_playlists.json",
    "spotify_playlists_flat.csv": "spotify_playlists_flat.csv",
    "spotify_playlist_items_flat.jsonl": "spotify_playlist_items_flat.jsonl",
    "spotify_playlist_items_flat.csv": "spotify_playlist_items_flat.csv",
    "spotify_recently_played.json": "spotify_recently_played.json",
    "spotify_recently_played_flat.csv": "spotify_recently_played_flat.csv",
}

REQUEST_LOG_FILENAME = "spotify_request_log.jsonl"
SUMMARY_FILENAME = "spotify_export_run_summary.json"
RATE_LIMIT_BLOCK_FILENAME = "spotify_rate_limit_block.json"

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


class RateLimitCooldownError(RuntimeError):
    def __init__(self, message: str, retry_after_seconds: int, path: str) -> None:
        super().__init__(message)
        self.retry_after_seconds = int(retry_after_seconds)
        self.path = path


class SpotifyApiError(RuntimeError):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class OAuthCallbackState:
    def __init__(self) -> None:
        self.code: Optional[str] = None
        self.state: Optional[str] = None
        self.error: Optional[str] = None
        self.event = threading.Event()


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def open_text_write(path: Path, *, newline: str | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open("w", encoding="utf-8", newline=newline)


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open_text_write(path) as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open_text_write(path, newline="") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open_text_write(path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_invalid_rows_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open_text_write(path, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def clamp_page_size(value: int) -> int:
    return max(1, min(50, int(value)))


def parse_redirect_bind(redirect_uri: str) -> Tuple[str, int]:
    parsed = urllib.parse.urlparse(redirect_uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    return host, port


def build_authorize_url(client_id: str, redirect_uri: str, scopes: str, state: str) -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scopes,
            "state": state,
            "show_dialog": "true",
        }
    )
    return f"{ACCOUNTS_BASE_URL}/authorize?{query}"


def request_token(
    client_id: str,
    client_secret: str,
    body_fields: Dict[str, str],
    timeout_seconds: int,
) -> Dict[str, Any]:
    payload = urllib.parse.urlencode(body_fields).encode("utf-8")
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    req = urllib.request.Request(
        url=f"{ACCOUNTS_BASE_URL}/api/token",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def build_callback_handler(callback_state: OAuthCallbackState):
    class OAuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)

            callback_state.code = query.get("code", [None])[0]
            callback_state.state = query.get("state", [None])[0]
            callback_state.error = query.get("error", [None])[0]
            callback_state.event.set()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                (
                    "<html><body><h3>Spotify authorization received.</h3>"
                    "<p>You can close this tab and return to the terminal.</p>"
                    "</body></html>"
                ).encode("utf-8")
            )

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return OAuthCallbackHandler


def complete_oauth_flow(args: Any) -> Dict[str, Any]:
    bind_host, bind_port = parse_redirect_bind(args.redirect_uri)
    state = secrets.token_urlsafe(24)

    callback_state = OAuthCallbackState()
    handler_class = build_callback_handler(callback_state)

    server = HTTPServer((bind_host, bind_port), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    authorize_url = build_authorize_url(args.client_id, args.redirect_uri, args.scopes, state)
    print("Open this URL to authorize:")
    print(authorize_url)

    if not args.no_browser:
        webbrowser.open(authorize_url)

    try:
        if not callback_state.event.wait(timeout=args.oauth_timeout_seconds):
            raise TimeoutError("Timed out waiting for Spotify OAuth callback.")

        if callback_state.error:
            raise RuntimeError(f"Spotify authorization error: {callback_state.error}")
        if callback_state.state != state:
            raise RuntimeError("Spotify OAuth state mismatch.")
        if not callback_state.code:
            raise RuntimeError("Missing authorization code in callback.")

        token_response = request_token(
            client_id=args.client_id,
            client_secret=args.client_secret,
            body_fields={
                "grant_type": "authorization_code",
                "code": callback_state.code,
                "redirect_uri": args.redirect_uri,
            },
            timeout_seconds=args.request_timeout_seconds,
        )
        expires_in = int(token_response.get("expires_in", 3600))
        token_response["expires_at_epoch"] = int(time.time()) + expires_in
        return token_response
    finally:
        server.shutdown()


class SpotifyApiClient:
    def __init__(self, args: Any, token_payload: Dict[str, Any]) -> None:
        self.args = args
        self.token_payload = token_payload
        self.request_log: List[Dict[str, Any]] = []
        self.request_log_dropped_count = 0
        self._recent_request_epochs: deque[float] = deque()
        self._last_request_epoch: float = 0.0

    def _append_request_log(self, event: Dict[str, Any]) -> None:
        limit = max(1000, int(getattr(self.args, "request_log_limit", REQUEST_LOG_LIMIT_DEFAULT)))
        if len(self.request_log) >= limit:
            drop_count = len(self.request_log) - limit + 1
            if drop_count > 0:
                del self.request_log[:drop_count]
                self.request_log_dropped_count += drop_count
        self.request_log.append(event)

    @property
    def access_token(self) -> str:
        token = self.token_payload.get("access_token")
        if not token:
            raise RuntimeError("Missing access token.")
        return str(token)

    def refresh_access_token(self) -> None:
        refresh_token = self.token_payload.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("No refresh_token available; re-run full OAuth authorization.")

        attempts = 0
        while True:
            attempts += 1
            try:
                refreshed = request_token(
                    client_id=self.args.client_id,
                    client_secret=self.args.client_secret,
                    body_fields={
                        "grant_type": "refresh_token",
                        "refresh_token": str(refresh_token),
                    },
                    timeout_seconds=self.args.request_timeout_seconds,
                )
                self.token_payload["access_token"] = refreshed["access_token"]
                self.token_payload["expires_in"] = refreshed.get("expires_in", 3600)
                self.token_payload["scope"] = refreshed.get("scope", self.token_payload.get("scope", ""))
                self.token_payload["token_type"] = refreshed.get("token_type", "Bearer")
                self.token_payload["expires_at_epoch"] = int(time.time()) + int(self.token_payload.get("expires_in", 3600))
                if "refresh_token" in refreshed:
                    self.token_payload["refresh_token"] = refreshed["refresh_token"]
                return
            except urllib.error.HTTPError as error:
                status = error.code
                body = error.read().decode("utf-8", errors="replace")
                if status == 429 and attempts <= self.args.max_retries:
                    retry_after = error.headers.get("Retry-After", "1")
                    try:
                        wait_seconds = max(1, int(retry_after))
                    except ValueError:
                        wait_seconds = 1
                    self._append_request_log(
                        {
                            "timestamp_utc": now_utc(),
                            "path": "/oauth/token",
                            "status": status,
                            "attempt": attempts,
                            "retry_after_seconds": wait_seconds,
                            "operation": "refresh_access_token",
                        }
                    )
                    time.sleep(wait_seconds)
                    continue
                if 500 <= status < 600 and attempts <= self.args.max_retries:
                    backoff_seconds = min(float(2**attempts), 30.0)
                    self._append_request_log(
                        {
                            "timestamp_utc": now_utc(),
                            "path": "/oauth/token",
                            "status": status,
                            "attempt": attempts,
                            "backoff_seconds": backoff_seconds,
                            "operation": "refresh_access_token",
                            "error_body": body,
                        }
                    )
                    time.sleep(backoff_seconds)
                    continue
                raise RuntimeError(f"Spotify token refresh failed with status {status}: {body}")
            except urllib.error.URLError as error:
                if attempts <= self.args.max_retries:
                    backoff_seconds = min(float(2**attempts), 30.0)
                    self._append_request_log(
                        {
                            "timestamp_utc": now_utc(),
                            "path": "/oauth/token",
                            "status": "url_error",
                            "attempt": attempts,
                            "backoff_seconds": backoff_seconds,
                            "operation": "refresh_access_token",
                            "reason": str(error.reason),
                        }
                    )
                    time.sleep(backoff_seconds)
                    continue
                raise RuntimeError(f"Network error refreshing Spotify token: {error.reason}")

    def api_get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query = urllib.parse.urlencode(params)
        url = f"{API_BASE_URL}{path}"
        if query:
            url = f"{url}?{query}"

        attempts = 0
        while True:
            attempts += 1
            expires_at_epoch = self.token_payload.get("expires_at_epoch")
            if expires_at_epoch is not None and time.time() >= (float(expires_at_epoch) - 60.0):
                self.refresh_access_token()
            self._apply_rate_limits(path=path)
            req = urllib.request.Request(
                url=url,
                method="GET",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/json",
                },
            )

            try:
                with urllib.request.urlopen(req, timeout=self.args.request_timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                    self._append_request_log(
                        {
                            "timestamp_utc": now_utc(),
                            "path": path,
                            "query": params,
                            "status": response.status,
                            "attempt": attempts,
                            "item_count": len(payload.get("items", [])) if isinstance(payload, dict) else None,
                            "total": payload.get("total") if isinstance(payload, dict) else None,
                        }
                    )
                    return payload

            except urllib.error.HTTPError as error:
                status = error.code
                if status == 401 and attempts <= self.args.max_retries:
                    self.refresh_access_token()
                    continue
                if status == 429 and attempts <= self.args.max_retries:
                    retry_after = error.headers.get("Retry-After", "1")
                    try:
                        wait_seconds = max(1, int(retry_after))
                    except ValueError:
                        wait_seconds = 1
                    max_retry_after = max(1, int(self.args.max_retry_after_seconds))
                    if wait_seconds > max_retry_after:
                        message = (
                            f"Spotify rate limit window too long: retry_after_seconds={wait_seconds} "
                            f"(threshold={max_retry_after}). Stop run and retry later or reduce request cadence."
                        )
                        print(f"[rate_limit_abort] {message}", flush=True)
                        self._append_request_log(
                            {
                                "timestamp_utc": now_utc(),
                                "path": path,
                                "query": params,
                                "status": status,
                                "attempt": attempts,
                                "retry_after_seconds": wait_seconds,
                                "max_retry_after_seconds": max_retry_after,
                                "aborted": True,
                                "reason": "retry_after_exceeds_threshold",
                            }
                        )
                        raise RateLimitCooldownError(message=message, retry_after_seconds=wait_seconds, path=path)
                    backoff_seconds = max(wait_seconds, attempts * 2)
                    print(
                        f"[rate_limit] path={path} attempt={attempts} status=429 "
                        f"retry_after_seconds={wait_seconds} backoff_seconds={backoff_seconds}",
                        flush=True,
                    )
                    self._append_request_log(
                        {
                            "timestamp_utc": now_utc(),
                            "path": path,
                            "query": params,
                            "status": status,
                            "attempt": attempts,
                            "retry_after_seconds": wait_seconds,
                            "backoff_seconds": backoff_seconds,
                        }
                    )
                    time.sleep(backoff_seconds)
                    continue
                body = error.read().decode("utf-8", errors="replace")
                self._append_request_log(
                    {
                        "timestamp_utc": now_utc(),
                        "path": path,
                        "query": params,
                        "status": status,
                        "attempt": attempts,
                        "error_body": body,
                    }
                )
                raise SpotifyApiError(f"Spotify API error {status} for {path}: {body}", status_code=status)

            except urllib.error.URLError as error:
                if attempts <= self.args.max_retries:
                    self._append_request_log(
                        {
                            "timestamp_utc": now_utc(),
                            "path": path,
                            "query": params,
                            "status": "url_error",
                            "attempt": attempts,
                            "reason": str(error.reason),
                        }
                    )
                    time.sleep(min(float(2**attempts), 30.0))
                    continue
                raise RuntimeError(f"Network error calling Spotify API path {path}: {error.reason}")

    def _apply_rate_limits(self, path: str) -> None:
        now = time.time()

        min_interval_seconds = max(0.0, float(self.args.min_request_interval_ms) / 1000.0)
        if self._last_request_epoch > 0:
            elapsed = now - self._last_request_epoch
            if elapsed < min_interval_seconds:
                sleep_seconds = min_interval_seconds - elapsed
                print(f"[throttle] path={path} reason=min_interval sleep_seconds={sleep_seconds:.3f}", flush=True)
                time.sleep(sleep_seconds)
                now = time.time()

        window_seconds = 60.0
        while self._recent_request_epochs and (now - self._recent_request_epochs[0]) > window_seconds:
            self._recent_request_epochs.popleft()

        max_rpm = max(1, int(self.args.max_requests_per_minute))
        if len(self._recent_request_epochs) >= max_rpm:
            oldest = self._recent_request_epochs[0]
            sleep_seconds = max(0.0, window_seconds - (now - oldest))
            if sleep_seconds > 0:
                print(
                    f"[throttle] path={path} reason=max_requests_per_minute sleep_seconds={sleep_seconds:.3f}",
                    flush=True,
                )
                time.sleep(sleep_seconds)
                now = time.time()
                while self._recent_request_epochs and (now - self._recent_request_epochs[0]) > window_seconds:
                    self._recent_request_epochs.popleft()

        self._recent_request_epochs.append(now)
        self._last_request_epoch = now


def fetch_all_offset_pages(
    client: SpotifyApiClient,
    path: str,
    base_params: Dict[str, Any],
    limit: int,
    max_items: Optional[int] = None,
) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    offset = 0
    page_index = 0

    while True:
        page_index += 1
        page_limit = limit
        if max_items is not None:
            remaining = max(0, int(max_items) - len(items))
            if remaining <= 0:
                break
            page_limit = min(limit, remaining)

        params = {**base_params, "limit": page_limit, "offset": offset}
        page = client.api_get(path=path, params=params)
        page_items = page.get("items", [])
        if not isinstance(page_items, list):
            raise RuntimeError(f"Expected list items for {path}")

        if max_items is not None:
            remaining_after_fetch = max(0, int(max_items) - len(items))
            page_items = page_items[:remaining_after_fetch]

        items.extend(page_items)
        total = int(page.get("total", len(items)))
        next_page = page.get("next") if isinstance(page, dict) else None
        print(f"[fetch] path={path} page={page_index} offset={offset} got={len(page_items)} total={total}", flush=True)
        offset += page_limit

        if (
            len(page_items) == 0
            or next_page is None
            or offset >= total
            or (max_items is not None and len(items) >= int(max_items))
        ):
            break

        pause_seconds = max(0.0, float(client.args.batch_pause_ms) / 1000.0)
        if pause_seconds > 0:
            print(f"[batch_pause] path={path} sleep_seconds={pause_seconds:.3f}", flush=True)
            time.sleep(pause_seconds)

    return items


def extract_track_fields(track: Dict[str, Any]) -> Dict[str, Any]:
    artists = track.get("artists", []) if isinstance(track, dict) else []
    artist_ids = [artist.get("id", "") for artist in artists if isinstance(artist, dict)]
    artist_names = [artist.get("name", "") for artist in artists if isinstance(artist, dict)]
    album = track.get("album", {}) if isinstance(track, dict) else {}
    external_ids = track.get("external_ids", {}) if isinstance(track, dict) else {}
    restrictions = track.get("restrictions", {}) if isinstance(track, dict) else {}
    linked_from = track.get("linked_from", {}) if isinstance(track, dict) else {}
    duration_ms = track.get("duration_ms")

    duration_seconds = None
    if isinstance(duration_ms, (int, float)):
        duration_seconds = round(float(duration_ms) / 1000.0, 3)

    return {
        "track_id": track.get("id"),
        "track_uri": track.get("uri"),
        "track_name": track.get("name"),
        "artist_ids": " | ".join([str(artist_id) for artist_id in artist_ids if artist_id]),
        "artist_names": " | ".join([str(name) for name in artist_names if name]),
        "album_id": album.get("id") if isinstance(album, dict) else None,
        "album_name": album.get("name") if isinstance(album, dict) else None,
        "release_date": album.get("release_date") if isinstance(album, dict) else None,
        "release_date_precision": album.get("release_date_precision") if isinstance(album, dict) else None,
        "duration_ms": duration_ms,
        "duration_seconds": duration_seconds,
        "popularity": track.get("popularity"),
        "explicit": track.get("explicit"),
        "is_playable": track.get("is_playable"),
        "restriction_reason": restrictions.get("reason") if isinstance(restrictions, dict) else None,
        "linked_from_track_id": linked_from.get("id") if isinstance(linked_from, dict) else None,
        "isrc": external_ids.get("isrc") if isinstance(external_ids, dict) else None,
        "track_href": track.get("href"),
        "track_external_url": (track.get("external_urls", {}) or {}).get("spotify") if isinstance(track, dict) else None,
    }


def _resolve_item_payload(item: Dict[str, Any]) -> Dict[str, Any] | None:
    payload = item.get("item")
    if isinstance(payload, dict):
        return payload
    payload = item.get("track")
    if isinstance(payload, dict):
        return payload
    return None


def build_top_track_rows(top_tracks_by_range: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for time_range, tracks in top_tracks_by_range.items():
        for rank, track in enumerate(tracks, start=1):
            rows.append({"time_range": time_range, "rank": rank, **extract_track_fields(track)})
    return rows


def build_saved_track_rows(saved_track_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in saved_track_items:
        track_payload: Dict[str, Any] = {}
        if isinstance(item, dict):
            resolved = _resolve_item_payload(item)
            if isinstance(resolved, dict):
                track_payload = resolved
        rows.append(
            {
                "added_at": item.get("added_at") if isinstance(item, dict) else None,
                **extract_track_fields(track_payload),
            }
        )
    return rows


def build_playlist_rows(playlists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for playlist in playlists:
        owner = playlist.get("owner", {}) if isinstance(playlist, dict) else {}
        item_collection = playlist.get("items", {}) if isinstance(playlist, dict) else {}
        track_collection = playlist.get("tracks", {}) if isinstance(playlist, dict) else {}
        rows.append(
            {
                "playlist_id": playlist.get("id"),
                "playlist_name": playlist.get("name"),
                "owner_id": owner.get("id") if isinstance(owner, dict) else None,
                "collaborative": playlist.get("collaborative"),
                "public": playlist.get("public"),
                "tracks_total": (
                    item_collection.get("total") if isinstance(item_collection, dict) and item_collection.get("total") is not None
                    else track_collection.get("total") if isinstance(track_collection, dict)
                    else None
                ),
                "items_access_status": playlist.get("playlist_items_access_status") if isinstance(playlist, dict) else None,
                "items_skipped_reason": playlist.get("playlist_items_skipped_reason") if isinstance(playlist, dict) else None,
                "snapshot_id": playlist.get("snapshot_id"),
                "uri": playlist.get("uri"),
            }
        )
    return rows


def build_playlist_item_rows(
    playlist_item_batches: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], int, int]:
    rows: List[Dict[str, Any]] = []
    skipped_non_track = 0
    skipped_invalid_item = 0
    for batch in playlist_item_batches:
        playlist = batch.get("playlist", {}) if isinstance(batch, dict) else {}
        playlist_id = playlist.get("id")
        playlist_name = playlist.get("name")
        items = batch.get("items", []) if isinstance(batch, dict) else []
        for position, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                skipped_invalid_item += 1
                continue

            payload = _resolve_item_payload(item)
            if not isinstance(payload, dict):
                skipped_invalid_item += 1
                continue

            item_type = str(payload.get("type", "track")).strip().lower()
            if item_type and item_type != "track":
                skipped_non_track += 1
                continue

            rows.append(
                {
                    "playlist_id": playlist_id,
                    "playlist_name": playlist_name,
                    "playlist_position": position,
                    "added_at": item.get("added_at"),
                    "added_by": (item.get("added_by") or {}).get("id"),
                    "is_local": item.get("is_local"),
                    **extract_track_fields(payload),
                }
            )
    return rows, skipped_non_track, skipped_invalid_item


def build_recently_played_rows(recently_played_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in recently_played_items:
        if not isinstance(item, dict):
            continue
        resolved = _resolve_item_payload(item)
        if not isinstance(resolved, dict):
            continue
        item_type = str(resolved.get("type", "track")).strip().lower()
        if item_type and item_type != "track":
            continue
        track = resolved
        context = item.get("context") if isinstance(item, dict) else None
        rows.append(
            {
                "played_at": item.get("played_at") if isinstance(item, dict) else None,
                "context_type": context.get("type") if isinstance(context, dict) else None,
                "context_uri": context.get("uri") if isinstance(context, dict) else None,
                **extract_track_fields(track),
            }
        )
    return rows


def build_export_artifact_paths(output_dir: Path) -> Dict[str, Path]:
    return {name: output_dir / filename for name, filename in EXPORT_ARTIFACT_FILENAMES.items()}


def build_support_file_paths(output_dir: Path) -> Dict[str, Path]:
    return {
        "request_log": output_dir / REQUEST_LOG_FILENAME,
        "summary": output_dir / SUMMARY_FILENAME,
        "rate_limit_block": output_dir / RATE_LIMIT_BLOCK_FILENAME,
    }


def _normalize_optional_cap(value: int) -> int | None:
    safe_value = max(0, int(value))
    return safe_value or None


def _normalize_requested_time_ranges(raw_value: str) -> List[str]:
    parts = [part.strip() for part in str(raw_value).split(",") if part.strip()]
    requested = [time_range for time_range in TIME_RANGE_ORDER if time_range in parts]
    return requested or list(TIME_RANGE_ORDER)


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


def _load_ingestion_controls_from_run_config() -> dict[str, Any] | None:
    run_config_path = os.environ.get("BL_RUN_CONFIG_PATH", "").strip()
    if not run_config_path:
        return None
    try:
        from run_config.run_config_utils import resolve_ingestion_controls

        controls = resolve_ingestion_controls(run_config_path)
        return controls if isinstance(controls, dict) else None
    except Exception:
        return None


def _apply_run_config_controls_to_args(args: argparse.Namespace) -> None:
    controls = _load_ingestion_controls_from_run_config()
    if not controls:
        return

    default_cfg = DEFAULT_INGESTION_CONTROLS

    if int(args.max_retries) == int(default_cfg["max_retries"]):
        args.max_retries = int(controls.get("max_retries", args.max_retries))

    if int(args.batch_pause_ms) == int(float(default_cfg["throttle_sleep_seconds"]) * 1000):
        args.batch_pause_ms = int(float(controls.get("throttle_sleep_seconds", default_cfg["throttle_sleep_seconds"])) * 1000)


def parse_export_args(argv: list[str] | None = None) -> argparse.Namespace:
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
    parser.add_argument("--output-dir", default="ingestion/outputs/spotify_api_export")
    parser.add_argument("--env-ps1", default="ingestion/configs/templates/spotify_env_template.ps1")
    parser.add_argument("--request-timeout-seconds", type=int, default=60)
    parser.add_argument("--oauth-timeout-seconds", type=int, default=180)
    parser.add_argument("--max-retries", type=int, default=int(DEFAULT_INGESTION_CONTROLS["max_retries"]))
    parser.add_argument("--max-retry-after-seconds", type=int, default=600)
    parser.add_argument("--batch-size-top-tracks", type=int, default=50)
    parser.add_argument("--batch-size-saved-tracks", type=int, default=50)
    parser.add_argument("--batch-size-playlists", type=int, default=50)
    parser.add_argument("--batch-size-playlist-items", type=int, default=50)
    parser.add_argument("--batch-pause-ms", type=int, default=int(float(DEFAULT_INGESTION_CONTROLS["throttle_sleep_seconds"]) * 1000))
    parser.add_argument("--min-request-interval-ms", type=int, default=300)
    parser.add_argument("--max-requests-per-minute", type=int, default=120)
    parser.add_argument("--request-log-limit", type=int, default=REQUEST_LOG_LIMIT_DEFAULT)
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
    parser.add_argument(
        "--recently-played-limit",
        type=int,
        default=50,
        help="Maximum recently played items to request in the single Spotify API call (hard capped at 50).",
    )
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--force-auth", action="store_true")
    args = parser.parse_args(argv)
    _apply_run_config_controls_to_args(args)
    return args


@dataclass
class ExportStage:
    root: Path

    def _fetch_all_data(self, client: SpotifyApiClient, args: argparse.Namespace) -> Dict[str, Any]:
        profile = client.api_get(path="/me", params={})
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
                path="/me/tracks",
                base_params={},
                limit=args.batch_size_saved_tracks,
                max_items=_normalize_optional_cap(args.saved_max_items),
            )
            print(f"[saved_tracks] count={len(saved_track_items)}", flush=True)

        playlists: List[Dict[str, Any]] = []
        malformed_playlist_id_count = 0
        if args.include_playlists:
            fetched_playlists = fetch_all_offset_pages(
                client=client,
                path="/me/playlists",
                base_params={},
                limit=args.batch_size_playlists,
                max_items=_normalize_optional_cap(args.playlists_max_items),
            )
            seen_playlist_ids: set[str] = set()
            deduped_playlists: List[Dict[str, Any]] = []
            for playlist in fetched_playlists:
                playlist_id = playlist.get("id") if isinstance(playlist, dict) else None
                if not playlist_id:
                    malformed_playlist_id_count += 1
                    continue
                playlist_id_key = str(playlist_id)
                if playlist_id_key in seen_playlist_ids:
                    continue
                seen_playlist_ids.add(playlist_id_key)
                deduped_playlists.append(playlist)
            playlists = deduped_playlists
            if len(playlists) != len(fetched_playlists):
                print(
                    f"[playlists] dropped={len(fetched_playlists) - len(playlists)} duplicate_or_invalid playlist ids",
                    flush=True,
                )
            print(f"[playlists] count={len(playlists)}", flush=True)

        playlist_item_batches: List[Dict[str, Any]] = []
        if args.include_playlists:
            market = profile.get("country") if isinstance(profile, dict) else None
            for playlist in playlists:
                playlist_id = playlist.get("id")
                if not playlist_id:
                    continue
                playlist_id = str(playlist_id)
                playlist_params: Dict[str, Any] = {}
                if isinstance(market, str) and market:
                    playlist_params["market"] = market
                try:
                    items = fetch_all_offset_pages(
                        client=client,
                        path=f"/playlists/{playlist_id}/items",
                        base_params=playlist_params,
                        limit=args.batch_size_playlist_items,
                        max_items=_normalize_optional_cap(args.playlist_items_max_per_playlist),
                    )
                except SpotifyApiError as err:
                    if err.status_code == 403:
                        playlist["playlist_items_access_status"] = "forbidden"
                        playlist["playlist_items_skipped_reason"] = "spotify_playlist_items_403_forbidden"
                        print(f"[playlist_items] playlist_id={playlist_id} SKIPPED (403 Forbidden — not accessible)", flush=True)
                        continue
                    raise
                playlist["playlist_items_access_status"] = "accessible"
                playlist["playlist_items_skipped_reason"] = None
                print(f"[playlist_items] playlist_id={playlist_id} items={len(items)}", flush=True)
                playlist_item_batches.append({"playlist": playlist, "items": items})

        recently_played_items: List[Dict[str, Any]] = []
        if args.include_recently_played:
            limit = max(1, min(50, int(args.recently_played_limit)))
            rp_page = client.api_get(path="/me/player/recently-played", params={"limit": limit})
            rp_raw = rp_page.get("items", []) if isinstance(rp_page, dict) else []
            if not isinstance(rp_raw, list):
                raise RuntimeError("Expected list items for /me/player/recently-played")
            recently_played_items = rp_raw[:limit]
            print(f"[recently_played] requested_limit={limit} count={len(recently_played_items)}", flush=True)

        return {
            "profile": profile,
            "top_tracks_by_range": top_tracks_by_range,
            "saved_track_items": saved_track_items,
            "playlists": playlists,
            "playlist_item_batches": playlist_item_batches,
            "recently_played_items": recently_played_items,
            "malformed_playlist_id_count": malformed_playlist_id_count,
        }

    def _write_all_artifacts(self, output_dir: Path, data: Dict[str, Any], generated_at: str) -> tuple[Dict[str, Path], Dict[str, int]]:
        top_tracks_by_range = data["top_tracks_by_range"]
        top_track_rows = build_top_track_rows(top_tracks_by_range)
        saved_track_rows = build_saved_track_rows(data["saved_track_items"])
        playlist_rows = build_playlist_rows(data["playlists"])
        playlist_item_rows, skipped_non_track, skipped_invalid_item = build_playlist_item_rows(data["playlist_item_batches"])
        playlist_item_items_total = sum(
            len(batch.get("items", []))
            for batch in data["playlist_item_batches"]
            if isinstance(batch, dict)
        )
        playlist_item_rows_kept = len(playlist_item_rows)
        playlist_item_rows_skipped = max(0, playlist_item_items_total - playlist_item_rows_kept)
        recently_played_rows = build_recently_played_rows(data["recently_played_items"])

        artifacts = build_export_artifact_paths(output_dir)
        written_artifacts: Dict[str, Path] = {}

        write_json(artifacts["spotify_profile.json"], data["profile"])
        written_artifacts["spotify_profile.json"] = artifacts["spotify_profile.json"]

        if top_tracks_by_range:
            write_json(
                artifacts["spotify_top_tracks_by_range.json"],
                {
                    "generated_at_utc": generated_at,
                    "counts": {k: len(v) for k, v in top_tracks_by_range.items()},
                    "items": top_tracks_by_range,
                },
            )
            write_csv(artifacts["spotify_top_tracks_flat.csv"], top_track_rows, TOP_TRACKS_FIELDS)
            written_artifacts["spotify_top_tracks_by_range.json"] = artifacts["spotify_top_tracks_by_range.json"]
            written_artifacts["spotify_top_tracks_flat.csv"] = artifacts["spotify_top_tracks_flat.csv"]

        for _data_key, _json_name, _csv_name, _rows, _fields in [
            ("saved_track_items", "spotify_saved_tracks.json", "spotify_saved_tracks_flat.csv", saved_track_rows, SAVED_TRACKS_FIELDS),
            ("playlists", "spotify_playlists.json", "spotify_playlists_flat.csv", playlist_rows, PLAYLISTS_FIELDS),
            (
                "recently_played_items",
                "spotify_recently_played.json",
                "spotify_recently_played_flat.csv",
                recently_played_rows,
                RECENTLY_PLAYED_FIELDS,
            ),
        ]:
            if data[_data_key]:
                write_json(
                    artifacts[_json_name],
                    {"generated_at_utc": generated_at, "count": len(data[_data_key]), "items": data[_data_key]},
                )
                write_csv(artifacts[_csv_name], _rows, _fields)
                written_artifacts[_json_name] = artifacts[_json_name]
                written_artifacts[_csv_name] = artifacts[_csv_name]

        if playlist_item_rows:
            write_jsonl(artifacts["spotify_playlist_items_flat.jsonl"], playlist_item_rows)
            write_csv(artifacts["spotify_playlist_items_flat.csv"], playlist_item_rows, PLAYLIST_ITEMS_FIELDS)
            written_artifacts["spotify_playlist_items_flat.jsonl"] = artifacts["spotify_playlist_items_flat.jsonl"]
            written_artifacts["spotify_playlist_items_flat.csv"] = artifacts["spotify_playlist_items_flat.csv"]

        build_metrics = {
            "playlist_item_items_total": int(playlist_item_items_total),
            "playlist_item_rows_kept": int(playlist_item_rows_kept),
            "playlist_item_rows_skipped": int(playlist_item_rows_skipped),
            "playlist_item_skipped_non_track": int(skipped_non_track),
            "playlist_item_skipped_invalid_payload": int(skipped_invalid_item),
        }
        return written_artifacts, build_metrics

    def _build_summary_artifacts(self, output_dir: Path, staging_dir: Path, artifacts: Dict[str, Path]) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "path": str((output_dir / path.relative_to(staging_dir)).relative_to(self.root)).replace("\\", "/"),
                "sha256": sha256_of_file(path),
                "bytes": path.stat().st_size,
            }
            for name, path in artifacts.items()
        }

    @staticmethod
    def _rename_directory(source: Path, target: Path) -> None:
        source.replace(target)

    @staticmethod
    def _remove_directory(path: Path) -> None:
        shutil.rmtree(path)

    def _replace_export_directory(self, staging_dir: Path, output_dir: Path) -> None:
        backup_dir = output_dir.parent / f"{output_dir.name}_backup"
        if backup_dir.exists():
            self._remove_directory(backup_dir)

        if not output_dir.exists():
            self._rename_directory(staging_dir, output_dir)
            return

        self._rename_directory(output_dir, backup_dir)
        try:
            self._rename_directory(staging_dir, output_dir)
        except Exception:
            if output_dir.exists():
                self._remove_directory(output_dir)
            if backup_dir.exists():
                self._rename_directory(backup_dir, output_dir)
            raise
        else:
            if backup_dir.exists():
                self._remove_directory(backup_dir)

    @staticmethod
    def _reset_staging_directory(staging_dir: Path) -> None:
        shutil.rmtree(staging_dir, ignore_errors=True)
        staging_dir.mkdir(parents=True, exist_ok=True)

    def run(self, args: argparse.Namespace) -> int:
        print("[start] spotify export initializing", flush=True)

        for attr in ("batch_size_top_tracks", "batch_size_saved_tracks", "batch_size_playlists", "batch_size_playlist_items"):
            setattr(args, attr, clamp_page_size(getattr(args, attr)))
        args.batch_pause_ms = max(0, int(args.batch_pause_ms))
        args.min_request_interval_ms = max(0, int(args.min_request_interval_ms))
        args.max_requests_per_minute = max(1, int(args.max_requests_per_minute))
        args.request_log_limit = max(1000, int(args.request_log_limit))

        if args.env_ps1:
            env_path = self.root / args.env_ps1
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

        if not any((args.include_top_tracks, args.include_saved_tracks, args.include_playlists, args.include_recently_played)):
            args.include_top_tracks = True
            args.include_saved_tracks = True
            args.include_playlists = True

        output_dir = self.root / args.output_dir
        staging_dir = output_dir.parent / f"{output_dir.name}_staging"
        self._reset_staging_directory(staging_dir)

        print("[auth] starting OAuth flow", flush=True)
        token_payload = complete_oauth_flow(args)
        print("[auth] oauth authorization complete", flush=True)
        client = SpotifyApiClient(args=args, token_payload=token_payload)

        support_paths = build_support_file_paths(staging_dir)

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
            data = self._fetch_all_data(client=client, args=args)
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
        artifacts, build_metrics = self._write_all_artifacts(output_dir=staging_dir, data=data, generated_at=generated_at)

        print(
            "[playlist_items] "
            f"rows_raw={build_metrics['playlist_item_items_total']} "
            f"rows_kept_tracks={build_metrics['playlist_item_rows_kept']} "
            f"rows_skipped_non_track_or_unavailable={build_metrics['playlist_item_rows_skipped']}",
            flush=True,
        )

        request_log_path = support_paths["request_log"]
        write_jsonl(request_log_path, client.request_log)
        artifacts["spotify_request_log.jsonl"] = request_log_path

        elapsed_seconds = round(time.time() - run_started, 3)
        top_by_range = data["top_tracks_by_range"]
        playlist_access_counts: Counter[str] = Counter(str(p.get("playlist_items_access_status") or "unknown") for p in data["playlists"])
        endpoint_counts = {
            "top_tracks_short_term": len(top_by_range.get("short_term", [])),
            "top_tracks_medium_term": len(top_by_range.get("medium_term", [])),
            "top_tracks_long_term": len(top_by_range.get("long_term", [])),
            "saved_tracks": len(data["saved_track_items"]),
            "playlists": len(data["playlists"]),
            "playlists_items_accessible": playlist_access_counts["accessible"],
            "playlists_items_forbidden": playlist_access_counts["forbidden"],
            "playlist_items": build_metrics["playlist_item_rows_kept"],
            "playlist_items_raw": build_metrics["playlist_item_items_total"],
            "playlist_items_skipped_non_track_or_unavailable": build_metrics["playlist_item_rows_skipped"],
            "playlist_items_skipped_non_track": build_metrics["playlist_item_skipped_non_track"],
            "playlist_items_skipped_invalid_payload": build_metrics["playlist_item_skipped_invalid_payload"],
            "playlists_skipped_missing_id": int(data.get("malformed_playlist_id_count", 0)),
            "recently_played": len(data["recently_played_items"]),
            "api_calls_logged": len(client.request_log),
            "api_calls_log_dropped": int(client.request_log_dropped_count),
        }

        summary = {
            "task": "BL-002-spotify-api-export",
            "run_id": run_id,
            "export_schema_version": EXPORT_SCHEMA_VERSION,
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
                "request_log_limit": int(args.request_log_limit),
            },
            "elapsed_seconds": elapsed_seconds,
            "resilience": {
                "cache_enabled": False,
                "cache_note": "Endpoint cache disabled; all pages fetched directly from Spotify API",
                "ingestion_controls_loaded_from_run_config": bool(_load_ingestion_controls_from_run_config()),
            },
            "artifacts": self._build_summary_artifacts(output_dir=output_dir, staging_dir=staging_dir, artifacts=artifacts),
            "notes": {
                "api_reference_basis": [
                    "Authorization Code Flow tutorial",
                    "Get User's Top Items",
                    "Get User's Saved Tracks",
                    "Get Current User's Playlists",
                    "Get Playlist Items",
                    "Get Recently Played Tracks",
                ],
                "playlist_items_policy": (
                    "Track-only export: non-track and unavailable playlist entries are skipped; playlists that reject item fetches "
                    "remain in playlist outputs with explicit access-status metadata."
                ),
                "recently_played_policy": "Single Spotify API request only; export captures at most 50 recently played items per run.",
                "policy_note": "Use data for personal ingestion and thesis analysis; do not redistribute Spotify content.",
            },
        }

        summary_path = support_paths["summary"]
        write_json(summary_path, summary)

        self._replace_export_directory(staging_dir=staging_dir, output_dir=output_dir)
        print("[write] summary file written", flush=True)

        print(f"Spotify export complete: run_id={run_id}")
        print(f"top_tracks_short_term={endpoint_counts['top_tracks_short_term']}")
        print(f"top_tracks_medium_term={endpoint_counts['top_tracks_medium_term']}")
        print(f"top_tracks_long_term={endpoint_counts['top_tracks_long_term']}")
        print(f"saved_tracks={endpoint_counts['saved_tracks']}")
        print(f"playlists={endpoint_counts['playlists']}")
        print(f"playlist_items={endpoint_counts['playlist_items']}")
        print(f"recently_played={endpoint_counts['recently_played']}")
        print(f"summary={summary_path}")
        return 0


def first_present(row: Mapping[str, Any], aliases: list[str]) -> str:
    for key in aliases:
        if key in row:
            return str(row.get(key, ""))
    return ""


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


def parse_history_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("BL-002 parser: transform raw listening-history CSV into normalized JSONL with quality flags.")
    )
    parser.add_argument("--input-csv", default="test_assets/sample_listening_history.csv", help="Path to raw listening-history CSV.")
    parser.add_argument("--output-jsonl", default="run_outputs/tc001_normalized_events.jsonl", help="Path to normalized event JSONL output.")
    parser.add_argument("--summary-json", default="run_outputs/tc001_validation_summary.json", help="Path to validation summary JSON output.")
    parser.add_argument("--invalid-rows-csv", default="run_outputs/tc001_invalid_rows.csv", help="Path to CSV listing non-ok rows.")
    parser.add_argument("--source-platform", default="spotify_export_csv", help="Fallback source_platform when platform column is missing/blank.")
    return parser.parse_args(argv)


@dataclass
class HistoryParserStage:
    root: Path

    def run(self, args: argparse.Namespace) -> int:
        input_path = self.root / args.input_csv
        output_path = self.root / args.output_jsonl
        summary_path = self.root / args.summary_json
        invalid_rows_path = self.root / args.invalid_rows_csv

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
                "ms_played": ms_played,
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
        return 0


def run_export(argv: list[str] | None = None) -> int:
    args = parse_export_args(argv)
    return ExportStage(root=impl_root()).run(args)


def run_history_parser(argv: list[str] | None = None) -> int:
    args = parse_history_args(argv)
    return HistoryParserStage(root=impl_root()).run(args)


def parse_top_level_args(argv: list[str] | None = None) -> tuple[str, list[str]]:
    args = list(argv) if argv is not None else sys.argv[1:]
    if args and args[0] in {"export", "parse"}:
        return args[0], args[1:]

    script_name = Path(sys.argv[0]).name.lower()
    if "ingest_history_parser" in script_name:
        return "parse", args
    if "export_spotify_max_dataset" in script_name:
        return "export", args

    return "export", args


def main(argv: list[str] | None = None) -> int:
    mode, remaining = parse_top_level_args(argv)
    if mode == "parse":
        return run_history_parser(remaining)
    return run_export(remaining)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RateLimitCooldownError:
        raise SystemExit(2)
