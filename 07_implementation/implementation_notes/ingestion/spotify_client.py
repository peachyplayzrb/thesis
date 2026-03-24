from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .spotify_resilience import CacheDB
    RESILIENCE_AVAILABLE: bool = True
except ImportError:
    CacheDB = None  # type: ignore[assignment,misc]
    RESILIENCE_AVAILABLE = False

from .spotify_auth import request_token  # noqa: E402
from .spotify_io import now_utc  # noqa: E402

API_BASE_URL = "https://api.spotify.com/v1"


class RateLimitCooldownError(RuntimeError):
    def __init__(self, message: str, retry_after_seconds: int, path: str) -> None:
        super().__init__(message)
        self.retry_after_seconds = int(retry_after_seconds)
        self.path = path


class SpotifyApiError(RuntimeError):
    """Raised for non-retryable HTTP errors from the Spotify API."""
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class SpotifyApiClient:
    def __init__(self, args: Any, token_payload: Dict[str, Any]) -> None:
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
                        f"[rate_limit] path={path} attempt={attempts} status=429 "
                        f"retry_after_seconds={wait_seconds} backoff_seconds={backoff_seconds}",
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
                raise SpotifyApiError(f"Spotify API error {status} for {path}: {body}", status_code=status)

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


def cached_api_get(
    client: SpotifyApiClient,
    cache_db: Any,
    path: str,
    params: Dict[str, Any],
    ttl_seconds: int = 86400,
) -> Dict[str, Any]:
    if cache_db is None:
        return client.api_get(path=path, params=params)

    params_str = json.dumps(params, sort_keys=True, separators=(",", ":"))
    params_hash = hashlib.sha256(params_str.encode("utf-8")).hexdigest()[:8]
    cache_key = f"spotify:{path}:{params_hash}"

    cached = cache_db.cache_get(cache_key)
    if cached is not None:
        print(f"[cache_hit] path={path} offset={params.get('offset', 0)} cache_key={cache_key}", flush=True)
        return cached

    try:
        data = client.api_get(path=path, params=params)
        cache_db.cache_set(cache_key, data, ttl_seconds=ttl_seconds, status=200, err=None)
        print(f"[cache_set] path={path} offset={params.get('offset', 0)} cache_key={cache_key}", flush=True)
        return data
    except Exception as exc:
        cache_db.cache_set(cache_key, {"error": str(exc), "status": "exception"}, ttl_seconds=3600, status=0, err=str(exc))
        raise


def fetch_all_offset_pages(
    client: SpotifyApiClient,
    cache_db: Any,
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
        page = cached_api_get(client=client, cache_db=cache_db, path=path, params=params)
        page_items = page.get("items", [])
        if not isinstance(page_items, list):
            raise RuntimeError(f"Expected list items for {path}")

        if max_items is not None:
            remaining_after_fetch = max(0, int(max_items) - len(items))
            page_items = page_items[:remaining_after_fetch]

        items.extend(page_items)
        total = int(page.get("total", len(items)))
        print(f"[fetch] path={path} page={page_index} offset={offset} got={len(page_items)} total={total}", flush=True)
        offset += len(page_items)

        if len(page_items) == 0 or offset >= total or (max_items is not None and len(items) >= int(max_items)):
            break

        pause_seconds = max(0.0, float(client.args.batch_pause_ms) / 1000.0)
        if pause_seconds > 0:
            print(f"[batch_pause] path={path} sleep_seconds={pause_seconds:.3f}", flush=True)
            time.sleep(pause_seconds)

    return items


