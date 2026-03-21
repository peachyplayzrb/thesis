from __future__ import annotations

import argparse
import base64
from collections import deque
import csv
import hashlib
import json
import os
import re
import secrets
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ACCOUNTS_BASE_URL = "https://accounts.spotify.com"
API_BASE_URL = "https://api.spotify.com/v1"
DEFAULT_SCOPES = [
    "user-top-read",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
    "user-read-private",
]


def clamp_page_size(value: int) -> int:
    return max(1, min(50, int(value)))


class RateLimitCooldownError(RuntimeError):
    def __init__(self, message: str, retry_after_seconds: int, path: str) -> None:
        super().__init__(message)
        self.retry_after_seconds = int(retry_after_seconds)
        self.path = path


class OAuthCallbackState:
    def __init__(self) -> None:
        self.code: Optional[str] = None
        self.state: Optional[str] = None
        self.error: Optional[str] = None
        self.event = threading.Event()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    shared_state: OAuthCallbackState

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        OAuthCallbackHandler.shared_state.code = query.get("code", [None])[0]
        OAuthCallbackHandler.shared_state.state = query.get("state", [None])[0]
        OAuthCallbackHandler.shared_state.error = query.get("error", [None])[0]
        OAuthCallbackHandler.shared_state.event.set()

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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export maximum user-accessible Spotify data for ingestion: top tracks, saved tracks, playlists, and playlist items."
        )
    )
    parser.add_argument("--client-id", default=os.getenv("SPOTIFY_CLIENT_ID", ""), help="Spotify app client id.")
    parser.add_argument("--client-secret", default=os.getenv("SPOTIFY_CLIENT_SECRET", ""), help="Spotify app client secret.")
    parser.add_argument(
        "--redirect-uri",
        default=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8001/spotify/auth/callback"),
        help="Spotify OAuth redirect URI.",
    )
    parser.add_argument(
        "--scopes",
        default=" ".join(DEFAULT_SCOPES),
        help="Space-separated Spotify scopes.",
    )
    parser.add_argument(
        "--output-dir",
        default="07_implementation/implementation_notes/ingestion/outputs/spotify_api_export",
        help="Directory for export artifacts.",
    )
    parser.add_argument(
        "--token-cache",
        default="07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_token_cache.json",
        help="Path to token cache file.",
    )
    parser.add_argument(
        "--env-ps1",
        default="07_implementation/implementation_notes/ingestion/spotify_env_template.ps1",
        help="PowerShell env file path with $env:SPOTIFY_* assignments.",
    )
    parser.add_argument(
        "--request-timeout-seconds",
        type=int,
        default=60,
        help="HTTP timeout per request in seconds.",
    )
    parser.add_argument(
        "--oauth-timeout-seconds",
        type=int,
        default=180,
        help="Timeout waiting for OAuth callback.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=4,
        help="Retries for rate-limits and transient HTTP errors.",
    )
    parser.add_argument(
        "--max-retry-after-seconds",
        type=int,
        default=600,
        help="Abort if Spotify Retry-After exceeds this threshold (seconds).",
    )
    parser.add_argument(
        "--batch-size-top-tracks",
        type=int,
        default=50,
        help="Page size for /me/top/tracks (1-50).",
    )
    parser.add_argument(
        "--batch-size-saved-tracks",
        type=int,
        default=50,
        help="Page size for /me/tracks (1-50).",
    )
    parser.add_argument(
        "--batch-size-playlists",
        type=int,
        default=50,
        help="Page size for /me/playlists (1-50).",
    )
    parser.add_argument(
        "--batch-size-playlist-items",
        type=int,
        default=50,
        help="Page size for /playlists/{id}/items (1-50).",
    )
    parser.add_argument(
        "--batch-pause-ms",
        type=int,
        default=250,
        help="Pause between paged batch requests in milliseconds.",
    )
    parser.add_argument(
        "--min-request-interval-ms",
        type=int,
        default=300,
        help="Minimum interval between API requests in milliseconds.",
    )
    parser.add_argument(
        "--max-requests-per-minute",
        type=int,
        default=120,
        help="Hard cap for API requests per rolling minute.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not auto-open browser; print authorize URL only.",
    )
    parser.add_argument(
        "--force-auth",
        action="store_true",
        help="Ignore token cache and force fresh auth flow.",
    )
    return parser.parse_args()


def parse_ps1_env_file(path: Path) -> Dict[str, str]:
    pattern = re.compile(r"^\s*\$env:(SPOTIFY_CLIENT_ID|SPOTIFY_CLIENT_SECRET|SPOTIFY_REDIRECT_URI)\s*=\s*['\"](.*?)['\"]\s*$")
    values: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        key = match.group(1)
        value = match.group(2)
        values[key] = value
    return values


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
    request = urllib.request.Request(
        url=f"{ACCOUNTS_BASE_URL}/api/token",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def load_token_cache(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_token_cache(path: Path, token_payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(token_payload, indent=2, ensure_ascii=True), encoding="utf-8")


def token_is_usable(token_payload: Dict[str, Any]) -> bool:
    access_token = token_payload.get("access_token")
    expires_at = token_payload.get("expires_at_epoch")
    if not access_token or not isinstance(expires_at, (int, float)):
        return False
    return time.time() < float(expires_at) - 30.0


def complete_oauth_flow(args: argparse.Namespace) -> Dict[str, Any]:
    bind_host, bind_port = parse_redirect_bind(args.redirect_uri)
    state = secrets.token_urlsafe(24)

    callback_state = OAuthCallbackState()
    OAuthCallbackHandler.shared_state = callback_state

    server = HTTPServer((bind_host, bind_port), OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    authorize_url = build_authorize_url(args.client_id, args.redirect_uri, args.scopes, state)
    print("Open this URL to authorize:")
    print(authorize_url)

    if not args.no_browser:
        webbrowser.open(authorize_url)

    if not callback_state.event.wait(timeout=args.oauth_timeout_seconds):
        server.shutdown()
        raise TimeoutError("Timed out waiting for Spotify OAuth callback.")

    server.shutdown()
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


class SpotifyApiClient:
    def __init__(self, args: argparse.Namespace, token_payload: Dict[str, Any]) -> None:
        self.args = args
        self.token_payload = token_payload
        self.request_log: List[Dict[str, Any]] = []
        self._recent_request_epochs: deque[float] = deque()
        self._last_request_epoch: float = 0.0

    @property
    def access_token(self) -> str:
        token = self.token_payload.get("access_token")
        if not token:
            raise RuntimeError("Missing access token.")
        return str(token)

    def refresh_access_token(self) -> None:
        refresh_token = self.token_payload.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("No refresh_token available; re-run with --force-auth.")

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

    def api_get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query = urllib.parse.urlencode(params)
        url = f"{API_BASE_URL}{path}"
        if query:
            url = f"{url}?{query}"

        attempts = 0
        while True:
            attempts += 1
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
                    self.request_log.append(
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
                        self.request_log.append(
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
                        f"[rate_limit] path={path} attempt={attempts} status=429 retry_after_seconds={wait_seconds} backoff_seconds={backoff_seconds}",
                        flush=True,
                    )
                    self.request_log.append(
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
                self.request_log.append(
                    {
                        "timestamp_utc": now_utc(),
                        "path": path,
                        "query": params,
                        "status": status,
                        "attempt": attempts,
                        "error_body": body,
                    }
                )
                raise RuntimeError(f"Spotify API error {status} for {path}: {body}")
            except urllib.error.URLError as error:
                if attempts <= self.args.max_retries:
                    self.request_log.append(
                        {
                            "timestamp_utc": now_utc(),
                            "path": path,
                            "query": params,
                            "status": "url_error",
                            "attempt": attempts,
                            "reason": str(error.reason),
                        }
                    )
                    time.sleep(min(attempts, 5))
                    continue
                raise RuntimeError(f"Network error calling Spotify API path {path}: {error.reason}")

    def _apply_rate_limits(self, path: str) -> None:
        now = time.time()

        min_interval_seconds = max(0.0, float(self.args.min_request_interval_ms) / 1000.0)
        if self._last_request_epoch > 0:
            elapsed = now - self._last_request_epoch
            if elapsed < min_interval_seconds:
                sleep_seconds = min_interval_seconds - elapsed
                print(
                    f"[throttle] path={path} reason=min_interval sleep_seconds={sleep_seconds:.3f}",
                    flush=True,
                )
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


def fetch_all_offset_pages(client: SpotifyApiClient, path: str, base_params: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    offset = 0
    page_index = 0

    while True:
        page_index += 1
        params = dict(base_params)
        params["limit"] = limit
        params["offset"] = offset
        page = client.api_get(path=path, params=params)
        page_items = page.get("items", [])
        if not isinstance(page_items, list):
            raise RuntimeError(f"Expected list items for {path}")

        items.extend(page_items)
        total = int(page.get("total", len(items)))
        print(
            f"[fetch] path={path} page={page_index} offset={offset} got={len(page_items)} total={total}",
            flush=True,
        )
        offset += len(page_items)

        if len(page_items) == 0 or offset >= total:
            break

        pause_seconds = max(0.0, float(client.args.batch_pause_ms) / 1000.0)
        if pause_seconds > 0:
            print(f"[batch_pause] path={path} sleep_seconds={pause_seconds:.3f}", flush=True)
            time.sleep(pause_seconds)

    return items


def extract_track_fields(track: Dict[str, Any]) -> Dict[str, Any]:
    artists = track.get("artists", []) if isinstance(track, dict) else []
    artist_names = [a.get("name", "") for a in artists if isinstance(a, dict)]
    album = track.get("album", {}) if isinstance(track, dict) else {}
    external_ids = track.get("external_ids", {}) if isinstance(track, dict) else {}

    return {
        "track_id": track.get("id"),
        "track_uri": track.get("uri"),
        "track_name": track.get("name"),
        "artist_names": " | ".join([str(name) for name in artist_names if name]),
        "album_name": album.get("name") if isinstance(album, dict) else None,
        "duration_ms": track.get("duration_ms"),
        "popularity": track.get("popularity"),
        "explicit": track.get("explicit"),
        "isrc": external_ids.get("isrc") if isinstance(external_ids, dict) else None,
        "track_href": track.get("href"),
        "track_external_url": (track.get("external_urls", {}) or {}).get("spotify") if isinstance(track, dict) else None,
    }


def main() -> None:
    args = parse_args()
    root = repo_root()
    print("[start] spotify export initializing", flush=True)

    args.batch_size_top_tracks = clamp_page_size(args.batch_size_top_tracks)
    args.batch_size_saved_tracks = clamp_page_size(args.batch_size_saved_tracks)
    args.batch_size_playlists = clamp_page_size(args.batch_size_playlists)
    args.batch_size_playlist_items = clamp_page_size(args.batch_size_playlist_items)
    args.batch_pause_ms = max(0, int(args.batch_pause_ms))
    args.min_request_interval_ms = max(0, int(args.min_request_interval_ms))
    args.max_requests_per_minute = max(1, int(args.max_requests_per_minute))

    if args.env_ps1:
        env_path = root / args.env_ps1
        if env_path.exists():
            parsed = parse_ps1_env_file(env_path)
            if (not args.client_id) and parsed.get("SPOTIFY_CLIENT_ID"):
                args.client_id = parsed["SPOTIFY_CLIENT_ID"]
            if (not args.client_secret) and parsed.get("SPOTIFY_CLIENT_SECRET"):
                args.client_secret = parsed["SPOTIFY_CLIENT_SECRET"]
            if (
                args.redirect_uri == "http://127.0.0.1:8001/spotify/auth/callback"
                and parsed.get("SPOTIFY_REDIRECT_URI")
            ):
                args.redirect_uri = parsed["SPOTIFY_REDIRECT_URI"]
            print(f"[config] loaded env file: {args.env_ps1}", flush=True)
        else:
            print(f"[config] env file not found, skipping: {args.env_ps1}", flush=True)

    if not args.client_id or not args.client_secret:
        raise ValueError("Missing Spotify credentials. Provide --client-id/--client-secret or SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET.")

    output_dir = root / args.output_dir
    token_cache_path = root / args.token_cache
    output_dir.mkdir(parents=True, exist_ok=True)

    token_payload = {}
    if not args.force_auth:
        token_payload = load_token_cache(token_cache_path)

    if not token_is_usable(token_payload):
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

    run_started = time.time()
    run_id = f"SPOTIFY-EXPORT-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    print(f"[run] run_id={run_id}", flush=True)
    print(
        (
            "[config] batches "
            f"top={args.batch_size_top_tracks} "
            f"saved={args.batch_size_saved_tracks} "
            f"playlists={args.batch_size_playlists} "
            f"playlist_items={args.batch_size_playlist_items} "
            f"batch_pause_ms={args.batch_pause_ms}"
        ),
        flush=True,
    )
    print(
        (
            "[config] rate_limit "
            f"min_request_interval_ms={args.min_request_interval_ms} "
            f"max_requests_per_minute={args.max_requests_per_minute} "
            f"max_retries={args.max_retries}"
        ),
        flush=True,
    )

    try:
        profile = client.api_get(path="/me", params={})
    except RateLimitCooldownError as error:
        retry_at = datetime.now(timezone.utc) + timedelta(seconds=error.retry_after_seconds)
        block_report_path = output_dir / "spotify_rate_limit_block.json"
        write_json(
            block_report_path,
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
        print(f"[blocked] report={block_report_path}", flush=True)
        raise
    print(f"[profile] user_id={profile.get('id')}", flush=True)

    top_tracks_by_range: Dict[str, List[Dict[str, Any]]] = {}
    top_track_rows: List[Dict[str, Any]] = []
    for time_range in ["short_term", "medium_term", "long_term"]:
        print(f"[top_tracks] fetching time_range={time_range}", flush=True)
        tracks = fetch_all_offset_pages(
            client=client,
            path="/me/top/tracks",
            base_params={"time_range": time_range},
            limit=args.batch_size_top_tracks,
        )
        top_tracks_by_range[time_range] = tracks
        print(f"[top_tracks] time_range={time_range} count={len(tracks)}", flush=True)
        for rank, track in enumerate(tracks, start=1):
            row = {"time_range": time_range, "rank": rank}
            row.update(extract_track_fields(track))
            top_track_rows.append(row)

    saved_track_items = fetch_all_offset_pages(
        client=client,
        path="/me/tracks",
        base_params={},
        limit=args.batch_size_saved_tracks,
    )
    print(f"[saved_tracks] count={len(saved_track_items)}", flush=True)

    saved_track_rows: List[Dict[str, Any]] = []
    for item in saved_track_items:
        track = item.get("track", {}) if isinstance(item, dict) else {}
        row = {
            "added_at": item.get("added_at") if isinstance(item, dict) else None,
        }
        row.update(extract_track_fields(track if isinstance(track, dict) else {}))
        saved_track_rows.append(row)

    playlists = fetch_all_offset_pages(
        client=client,
        path="/me/playlists",
        base_params={},
        limit=args.batch_size_playlists,
    )
    print(f"[playlists] count={len(playlists)}", flush=True)

    playlist_rows: List[Dict[str, Any]] = []
    playlist_item_rows: List[Dict[str, Any]] = []

    for playlist in playlists:
        playlist_id = playlist.get("id")
        playlist_name = playlist.get("name")
        owner = playlist.get("owner", {}) if isinstance(playlist, dict) else {}
        playlist_rows.append(
            {
                "playlist_id": playlist_id,
                "playlist_name": playlist_name,
                "owner_id": owner.get("id") if isinstance(owner, dict) else None,
                "collaborative": playlist.get("collaborative"),
                "public": playlist.get("public"),
                "tracks_total": (playlist.get("tracks", {}) or {}).get("total"),
                "snapshot_id": playlist.get("snapshot_id"),
                "uri": playlist.get("uri"),
            }
        )

        if not playlist_id:
            continue

        items = fetch_all_offset_pages(
            client=client,
            path=f"/playlists/{playlist_id}/items",
            base_params={"additional_types": "track"},
            limit=args.batch_size_playlist_items,
        )
        print(f"[playlist_items] playlist_id={playlist_id} items={len(items)}", flush=True)

        for position, item in enumerate(items, start=1):
            track = item.get("track") if isinstance(item, dict) else None
            if not isinstance(track, dict):
                track = {}
            row = {
                "playlist_id": playlist_id,
                "playlist_name": playlist_name,
                "playlist_position": position,
                "added_at": item.get("added_at") if isinstance(item, dict) else None,
                "added_by": ((item.get("added_by") or {}).get("id") if isinstance(item, dict) else None),
                "is_local": item.get("is_local") if isinstance(item, dict) else None,
            }
            row.update(extract_track_fields(track))
            playlist_item_rows.append(row)

    generated_at = now_utc()

    profile_path = output_dir / "spotify_profile.json"
    top_tracks_path = output_dir / "spotify_top_tracks_by_range.json"
    top_tracks_csv_path = output_dir / "spotify_top_tracks_flat.csv"
    saved_tracks_path = output_dir / "spotify_saved_tracks.json"
    saved_tracks_csv_path = output_dir / "spotify_saved_tracks_flat.csv"
    playlists_path = output_dir / "spotify_playlists.json"
    playlists_csv_path = output_dir / "spotify_playlists_flat.csv"
    playlist_items_path = output_dir / "spotify_playlist_items_flat.jsonl"
    playlist_items_csv_path = output_dir / "spotify_playlist_items_flat.csv"
    request_log_path = output_dir / "spotify_request_log.jsonl"
    summary_path = output_dir / "spotify_export_run_summary.json"

    write_json(profile_path, profile)
    write_json(
        top_tracks_path,
        {
            "generated_at_utc": generated_at,
            "counts": {k: len(v) for k, v in top_tracks_by_range.items()},
            "items": top_tracks_by_range,
        },
    )
    write_csv(
        top_tracks_csv_path,
        top_track_rows,
        [
            "time_range",
            "rank",
            "track_id",
            "track_uri",
            "track_name",
            "artist_names",
            "album_name",
            "duration_ms",
            "popularity",
            "explicit",
            "isrc",
            "track_href",
            "track_external_url",
        ],
    )

    write_json(saved_tracks_path, {"generated_at_utc": generated_at, "count": len(saved_track_items), "items": saved_track_items})
    write_csv(
        saved_tracks_csv_path,
        saved_track_rows,
        [
            "added_at",
            "track_id",
            "track_uri",
            "track_name",
            "artist_names",
            "album_name",
            "duration_ms",
            "popularity",
            "explicit",
            "isrc",
            "track_href",
            "track_external_url",
        ],
    )

    write_json(playlists_path, {"generated_at_utc": generated_at, "count": len(playlists), "items": playlists})
    write_csv(
        playlists_csv_path,
        playlist_rows,
        [
            "playlist_id",
            "playlist_name",
            "owner_id",
            "collaborative",
            "public",
            "tracks_total",
            "snapshot_id",
            "uri",
        ],
    )

    write_jsonl(playlist_items_path, playlist_item_rows)
    write_csv(
        playlist_items_csv_path,
        playlist_item_rows,
        [
            "playlist_id",
            "playlist_name",
            "playlist_position",
            "added_at",
            "added_by",
            "is_local",
            "track_id",
            "track_uri",
            "track_name",
            "artist_names",
            "album_name",
            "duration_ms",
            "popularity",
            "explicit",
            "isrc",
            "track_href",
            "track_external_url",
        ],
    )

    write_jsonl(request_log_path, client.request_log)

    artifacts = {
        "spotify_profile.json": profile_path,
        "spotify_top_tracks_by_range.json": top_tracks_path,
        "spotify_top_tracks_flat.csv": top_tracks_csv_path,
        "spotify_saved_tracks.json": saved_tracks_path,
        "spotify_saved_tracks_flat.csv": saved_tracks_csv_path,
        "spotify_playlists.json": playlists_path,
        "spotify_playlists_flat.csv": playlists_csv_path,
        "spotify_playlist_items_flat.jsonl": playlist_items_path,
        "spotify_playlist_items_flat.csv": playlist_items_csv_path,
        "spotify_request_log.jsonl": request_log_path,
    }

    elapsed_seconds = round(time.time() - run_started, 3)
    endpoint_counts = {
        "top_tracks_short_term": len(top_tracks_by_range.get("short_term", [])),
        "top_tracks_medium_term": len(top_tracks_by_range.get("medium_term", [])),
        "top_tracks_long_term": len(top_tracks_by_range.get("long_term", [])),
        "saved_tracks": len(saved_track_items),
        "playlists": len(playlists),
        "playlist_items": len(playlist_item_rows),
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
            "spotify_user_id": profile.get("id"),
            "country": profile.get("country"),
            "product": profile.get("product"),
        },
        "counts": endpoint_counts,
        "elapsed_seconds": elapsed_seconds,
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
    print(f"summary={summary_path}")


if __name__ == "__main__":
    try:
        main()
    except RateLimitCooldownError:
        sys.exit(2)
