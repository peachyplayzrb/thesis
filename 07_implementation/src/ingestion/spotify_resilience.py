#!/usr/bin/env python3
"""
Spotify API resilience utilities: rate-limiting, caching, backoff, job tracking.

Provides reusable patterns for safe, cached Spotify API access with exponential backoff,
throttling, and persistent job progress tracking.
"""

import json
import sqlite3
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import Any

from shared_utils.constants import (
    DEFAULT_API_BASE_DELAY_SEC,
    DEFAULT_API_CACHE_TTL_SECONDS,
    DEFAULT_API_MAX_RETRIES,
    DEFAULT_API_THROTTLE_SLEEP_SEC,
)

# Module-level configuration variables (mutable for testing/run_config override)
DEFAULT_TTL_SECONDS = DEFAULT_API_CACHE_TTL_SECONDS  # 24-hour cache by default
SLEEP_BETWEEN_CALLS_SEC = DEFAULT_API_THROTTLE_SLEEP_SEC      # 120ms throttle between API calls
MAX_RETRIES = DEFAULT_API_MAX_RETRIES
BASE_DELAY_SEC = DEFAULT_API_BASE_DELAY_SEC


def apply_ingestion_controls(ingestion_config: dict) -> None:
    """Apply ingestion controls from run_config to module-level defaults.

    This allows users to override resilience behavior via run_config.ingestion_controls
    without modifying this source file.

    Args:
        ingestion_config: Dict with keys cache_ttl_seconds, throttle_sleep_seconds,
                         max_retries, base_backoff_delay_seconds
    """
    global DEFAULT_TTL_SECONDS, SLEEP_BETWEEN_CALLS_SEC, MAX_RETRIES, BASE_DELAY_SEC

    if ingestion_config:
        DEFAULT_TTL_SECONDS = int(ingestion_config.get("cache_ttl_seconds", DEFAULT_TTL_SECONDS))
        SLEEP_BETWEEN_CALLS_SEC = float(ingestion_config.get("throttle_sleep_seconds", SLEEP_BETWEEN_CALLS_SEC))
        MAX_RETRIES = int(ingestion_config.get("max_retries", MAX_RETRIES))
        BASE_DELAY_SEC = float(ingestion_config.get("base_backoff_delay_seconds", BASE_DELAY_SEC))


# -------------------------
# Time Utilities
# -------------------------
def now_iso() -> str:
    """Return current UTC time in ISO 8601 format (Z-terminated)."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iso_to_dt(s: str | None) -> datetime | None:
    """Parse ISO 8601 string (with optional Z suffix) to datetime."""
    if not s:
        return None
    try:
        return datetime.strptime(s.replace("Z", ""), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=UTC)
    except Exception:
        return None


# -------------------------
# Database Management
# -------------------------
class CacheDB:
    """SQLite-backed endpoint cache with TTL support."""

    def __init__(self, db_path: str = "spotify_cache.sqlite"):
        self.db_path = db_path
        self.init_db()

    def _conn(self) -> sqlite3.Connection:
        """Get a new database connection with WAL mode."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def init_db(self):
        """Initialize cache and job progress tables."""
        conn = self._conn()
        cur = conn.cursor()

        # Endpoint payload cache (keyed by "name" string)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS endpoint_cache (
              cache_key TEXT PRIMARY KEY,
              payload_json TEXT,
              fetched_at TEXT,
              ttl_seconds INTEGER,
              last_status INTEGER,
              last_error TEXT
            );
        """)

        # Per-job progress tracking
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_progress (
              job_id TEXT,
              step_name TEXT,
              done INTEGER DEFAULT 0,
              started_at TEXT,
              finished_at TEXT,
              last_error TEXT,
              items_done INTEGER DEFAULT 0,
              items_total INTEGER DEFAULT 0,
              PRIMARY KEY(job_id, step_name)
            );
        """)

        conn.commit()
        conn.close()

    def cache_get(self, cache_key: str) -> dict[str, Any] | None:
        """Retrieve cached payload if it exists and TTL is valid."""
        conn = self._conn()
        cur = conn.cursor()
        row = cur.execute("""
            SELECT payload_json, fetched_at, ttl_seconds
            FROM endpoint_cache
            WHERE cache_key = ?
        """, (cache_key,)).fetchone()
        conn.close()

        if not row:
            return None

        payload_json, fetched_at, ttl_seconds = row
        fetched_dt = iso_to_dt(fetched_at)
        if not fetched_dt:
            return None

        # Check if TTL expired
        if ttl_seconds is not None:
            if datetime.now(UTC) - fetched_dt > timedelta(seconds=int(ttl_seconds)):
                return None

        try:
            return json.loads(payload_json)
        except Exception:
            return None

    def cache_set(self, cache_key: str, payload: Any, ttl_seconds: int, status: int, err: str | None):
        """Store cached payload (success or failure)."""
        conn = self._conn()
        conn.execute("""
            INSERT INTO endpoint_cache(cache_key, payload_json, fetched_at, ttl_seconds, last_status, last_error)
            VALUES(?, ?, ?, ?, ?, ?)
            ON CONFLICT(cache_key) DO UPDATE SET
              payload_json=excluded.payload_json,
              fetched_at=excluded.fetched_at,
              ttl_seconds=excluded.ttl_seconds,
              last_status=excluded.last_status,
              last_error=excluded.last_error
        """, (
            cache_key,
            json.dumps(payload, ensure_ascii=False),
            now_iso(),
            int(ttl_seconds),
            status,
            err
        ))
        conn.commit()
        conn.close()


class JobProgress:
    """Database-backed job progress tracker."""

    def __init__(self, db_path: str = "spotify_cache.sqlite"):
        self.db_path = db_path
        self.cache_db = CacheDB(db_path)
        self.cache_db.init_db()

    def _conn(self) -> sqlite3.Connection:
        """Get a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def init(self, job_id: str, steps: list):
        """Initialize step tracking for a job."""
        conn = self._conn()
        cur = conn.cursor()
        for s in steps:
            cur.execute("""
                INSERT OR IGNORE INTO job_progress(job_id, step_name, done, started_at, finished_at, last_error, items_done, items_total)
                VALUES(?, ?, 0, NULL, NULL, NULL, 0, 0)
            """, (job_id, s))
        conn.commit()
        conn.close()

    def update(self, job_id: str, step: str, *, started: bool = False, finished: bool = False,
               done: int | None = None, total: int | None = None, err: str | None = None):
        """Update step progress (atomic fields)."""
        conn = self._conn()
        cur = conn.cursor()

        if started:
            cur.execute("""
                UPDATE job_progress
                SET started_at = COALESCE(started_at, ?)
                WHERE job_id = ? AND step_name = ?
            """, (now_iso(), job_id, step))

        if done is not None:
            cur.execute("""
                UPDATE job_progress
                SET items_done = ?
                WHERE job_id = ? AND step_name = ?
            """, (int(done), job_id, step))

        if total is not None:
            cur.execute("""
                UPDATE job_progress
                SET items_total = ?
                WHERE job_id = ? AND step_name = ?
            """, (int(total), job_id, step))

        if err is not None:
            cur.execute("""
                UPDATE job_progress
                SET last_error = ?
                WHERE job_id = ? AND step_name = ?
            """, (err, job_id, step))

        if finished:
            cur.execute("""
                UPDATE job_progress
                SET finished_at = ?, done = 1
                WHERE job_id = ? AND step_name = ?
            """, (now_iso(), job_id, step))

        conn.commit()
        conn.close()

    def read(self, job_id: str) -> dict[str, Any]:
        """Read current progress for all steps in a job."""
        conn = self._conn()
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT step_name, done, started_at, finished_at, last_error, items_done, items_total
            FROM job_progress
            WHERE job_id = ?
            ORDER BY step_name
        """, (job_id,)).fetchall()
        conn.close()

        out = {}
        for r in rows:
            step_name, done, started_at, finished_at, last_error, items_done, items_total = r
            out[step_name] = {
                "done": bool(done),
                "started_at": started_at,
                "finished_at": finished_at,
                "last_error": last_error,
                "items_done": items_done,
                "items_total": items_total,
            }
        return out


# -------------------------
# Retry + Backoff
# -------------------------
def safe_call(
    fn: Callable,
    max_retries: int | None = None,
    base_delay: float | None = None,
) -> tuple[bool, Any | None, int, str | None]:
    """
    Execute fn with exponential backoff on transient errors.

    Returns: (success, data, status_code, error_message)
    """
    try:
        spotify_exceptions = import_module("spotipy.exceptions")
        SpotifyException = spotify_exceptions.SpotifyException
    except ModuleNotFoundError:
        class SpotifyException(Exception):
            http_status: int | None = None

    retries = int(max_retries) if max_retries is not None else int(MAX_RETRIES)
    delay = float(base_delay) if base_delay is not None else float(BASE_DELAY_SEC)
    for attempt in range(retries):
        try:
            data = fn()
            return True, data, 200, None
        except SpotifyException as e:
            status = getattr(e, "http_status", None) or 0
            msg = str(e)

            # Retry only on transient errors
            if status in (429, 500, 502, 503, 504):
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, 20.0)  # Cap at 20 seconds
                    continue
                else:
                    return False, None, status, msg
            else:
                # Don't retry on auth, not-found, etc.
                return False, None, status, msg
        except Exception as e:
            return False, None, 0, f"{type(e).__name__}: {e}"

    return False, None, 429, "Max retries exceeded."


# -------------------------
# Cached Fetch
# -------------------------
def cached_fetch(cache_db: CacheDB, name: str, ttl_seconds: int,
                 fn: Callable, apply_throttle: bool = True) -> dict[str, Any]:
    """
    Fetch from cache if valid, else call Spotify with backoff + cache result.

    Returns: {ok, name, status, cached, data, error}
    """
    # Try cache first
    cached = cache_db.cache_get(name)
    if cached is not None:
        return {
            "ok": True,
            "name": name,
            "status": 200,
            "cached": True,
            "data": cached,
            "error": None
        }

    # Call Spotify with backoff
    ok, data, status, err = safe_call(fn)

    if ok:
        cache_db.cache_set(name, data, ttl_seconds=ttl_seconds, status=status, err=None)
        result = {
            "ok": True,
            "name": name,
            "status": status,
            "cached": False,
            "data": data,
            "error": None
        }
    else:
        # Cache the error too so we don't hammer dead endpoints
        cache_db.cache_set(name, {"error": err, "status": status}, ttl_seconds=ttl_seconds, status=status, err=err)
        result = {
            "ok": False,
            "name": name,
            "status": status,
            "cached": False,
            "data": None,
            "error": err
        }

    if apply_throttle:
        time.sleep(SLEEP_BETWEEN_CALLS_SEC)

    return result


# -------------------------
# Pagination Helpers
# -------------------------
def paginate_offset_all(fetch_page_fn: Callable, page_size: int = 50,
                        max_items: int | None = None) -> list:
    """Paginate offset-based endpoints (limit/offset style)."""
    out = []
    offset = 0
    while True:
        if max_items is not None and len(out) >= max_items:
            break
        limit = page_size if max_items is None else min(page_size, max_items - len(out))
        page = fetch_page_fn(limit=limit, offset=offset)
        items = page.get("items", []) if isinstance(page, dict) else []
        out.extend(items)

        if len(items) < limit:
            break
        if isinstance(page, dict) and not page.get("next"):
            break

        offset += len(items)
    return out


def paginate_cursor_all(fetch_page_fn: Callable, page_size: int = 50,
                        max_items: int | None = None) -> list:
    """Paginate cursor-based endpoints (after-cursor style)."""
    out = []
    after = None
    while True:
        if max_items is not None and len(out) >= max_items:
            break

        limit = page_size if max_items is None else min(page_size, max_items - len(out))
        page = fetch_page_fn(limit=limit, after=after)

        items = page.get("items", [])
        out.extend(items)

        cursors = page.get("cursors", {})
        after = cursors.get("after")
        if not after or len(items) == 0:
            break

    return out
