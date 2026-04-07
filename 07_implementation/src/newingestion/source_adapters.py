"""
Source adapter interface and concrete implementations for data acquisition.

Adapters handle provider-specific acquisition logic (OAuth, API calls, pagination, etc.)
and return raw data in a consistent format that can be normalized to CanonicalTrackEvent.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path
import csv
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

from .models import NewingestionControls
from ingestion.spotify_auth import request_token, complete_oauth_flow


@dataclass
class SourceAdapterContext:
    """
    Context for source adapter execution.

    Provides credential paths, cache locations, and control settings.
    """
    root_path: Path
    controls: NewingestionControls
    cache_dir: Optional[Path] = None


class IngestionSourceAdapter(ABC):
    """
    Abstract base for ingestion data source adapters.

    Concrete adapters implement specific provider protocols (Spotify API, CSV history, etc.)
    and return raw data in a provider-native format (typically a dict with lists of objects).
    """

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Return the identifier of this source (e.g., 'spotify_api', 'csv_history')."""
        pass

    @abstractmethod
    def verify_credentials(self, context: SourceAdapterContext) -> bool:
        """
        Verify that required credentials exist and are valid.

        Args:
            context: Adapter execution context

        Returns:
            True if credentials are available and valid
        """
        pass

    @abstractmethod
    def collect(self, context: SourceAdapterContext) -> Dict[str, Any]:
        """
        Acquire raw data from this source.

        Implementation should handle pagination, retry, rate-limiting, and error handling
        according to provider protocol and controls settings.

        Args:
            context: Adapter execution context

        Returns:
            Dict with keys like 'top_tracks_short', 'saved_tracks', etc.,
            each mapping to raw provider objects.
        """
        pass


class SpotifyApiSourceAdapter(IngestionSourceAdapter):
    """
    Concrete adapter for Spotify Web API data acquisition.

    Handles OAuth flow, API pagination, rate-limit retry, and resilience caching.
    """

    @property
    def source_type(self) -> str:
        return "spotify_api"

    def _required_scopes(self, controls: NewingestionControls) -> set[str]:
        scopes = {"user-read-private"}
        if controls.include_top_tracks:
            scopes.add("user-top-read")
        if controls.include_saved_tracks:
            scopes.add("user-library-read")
        if controls.include_playlists:
            scopes.update({"playlist-read-private", "playlist-read-collaborative"})
        if controls.include_recently_played:
            scopes.add("user-read-recently-played")
        return scopes

    def _resolve_token(self) -> str:
        """
        Resolve Spotify access token with fallback chain:
        1. Direct env token (BL_SPOTIFY_AUTH_TOKEN)
        2. Refresh token flow (BL_SPOTIFY_REFRESH_TOKEN + client creds)
        3. Interactive OAuth (if enable_interactive_oauth=True + client_id/secret)
        4. Return empty string (fail soft)
        """
        cached_token = getattr(self, "_resolved_token", "")
        if cached_token:
            return cached_token

        # Priority 1: Direct access token from env
        token = os.environ.get("BL_SPOTIFY_AUTH_TOKEN", "").strip()
        if token:
            self._resolved_token = token
            return token

        # Priority 2: Refresh token grant
        refresh_token = os.environ.get("BL_SPOTIFY_REFRESH_TOKEN", "").strip()
        client_id = os.environ.get("BL_SPOTIFY_CLIENT_ID", "").strip()
        client_secret = os.environ.get("BL_SPOTIFY_CLIENT_SECRET", "").strip()
        if refresh_token and client_id and client_secret:
            refreshed = request_token(
                client_id=client_id,
                client_secret=client_secret,
                body_fields={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                timeout_seconds=30,
            )
            refreshed_token = str(refreshed.get("access_token", "")).strip()
            if refreshed_token:
                self._resolved_token = refreshed_token
                return refreshed_token

        # Priority 3: Interactive OAuth (if enabled and creds available)
        if hasattr(self, "_controls") and self._controls:
            if self._controls.enable_interactive_oauth:
                oauth_client_id = os.environ.get("BL_SPOTIFY_CLIENT_ID", "").strip() or \
                                  (self._controls.oauth_client_id or "").strip()
                oauth_client_secret = os.environ.get("BL_SPOTIFY_CLIENT_SECRET", "").strip() or \
                                      (self._controls.oauth_client_secret or "").strip()

                if oauth_client_id and oauth_client_secret:
                    try:
                        # Build minimal args-like object for complete_oauth_flow
                        class OAuthArgs:
                            pass
                        args = OAuthArgs()
                        args.client_id = oauth_client_id
                        args.client_secret = oauth_client_secret
                        args.redirect_uri = self._controls.oauth_redirect_uri
                        args.scopes = " ".join(self._required_scopes(self._controls))
                        args.no_browser = self._controls.oauth_no_browser
                        args.oauth_timeout_seconds = self._controls.oauth_timeout_seconds
                        args.request_timeout_seconds = 30

                        print(f"[newingestion] attempting interactive OAuth with redirect_uri={args.redirect_uri}", flush=True)
                        token_response = complete_oauth_flow(args)
                        access_token = str(token_response.get("access_token", "")).strip()
                        if access_token:
                            self._resolved_token = access_token
                            return access_token
                    except Exception as e:
                        print(f"[newingestion] interactive OAuth failed: {type(e).__name__}: {e}", flush=True)

        return ""

    def _api_get(self, token: str, path: str, params: Optional[Dict[str, Any]] = None, controls: Optional[NewingestionControls] = None) -> Dict[str, Any]:
        """Minimal Spotify GET helper with conservative retry handling."""
        params = params or {}
        controls = controls or NewingestionControls()
        query = urllib.parse.urlencode(params)
        url = f"https://api.spotify.com/v1{path}"
        if query:
            url = f"{url}?{query}"

        retries = max(0, int(controls.max_retries))
        for attempt in range(retries + 1):
            req = urllib.request.Request(
                url=url,
                method="GET",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < retries:
                    retry_after = exc.headers.get("Retry-After", "1")
                    try:
                        wait_seconds = max(1.0, float(retry_after))
                    except ValueError:
                        wait_seconds = max(1.0, float(controls.base_backoff_delay_seconds))
                    time.sleep(wait_seconds)
                    continue
                if 500 <= exc.code < 600 and attempt < retries:
                    delay = max(0.1, float(controls.base_backoff_delay_seconds)) * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise
            except urllib.error.URLError:
                if attempt < retries:
                    delay = max(0.1, float(controls.base_backoff_delay_seconds)) * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise

        return {}

    def _fetch_offset_items(self, token: str, path: str, max_items: int = 0, base_params: Optional[Dict[str, Any]] = None, controls: Optional[NewingestionControls] = None) -> List[Dict[str, Any]]:
        """Fetch offset-paginated Spotify items and apply optional cap."""
        items: List[Dict[str, Any]] = []
        offset = 0
        limit = 50
        while True:
            params = dict(base_params or {})
            params.update({"limit": limit, "offset": offset})
            payload = self._api_get(token, path, params, controls=controls)
            page_items = payload.get("items", []) if isinstance(payload, dict) else []
            if not page_items:
                break
            items.extend(page_items)
            if max_items > 0 and len(items) >= max_items:
                return items[:max_items]
            if len(page_items) < limit:
                break
            offset += limit
        return items

    def verify_credentials(self, context: SourceAdapterContext) -> bool:
        """
        Verify Spotify OAuth credentials are available.

        Looks for:
        - BL_SPOTIFY_AUTH_TOKEN environment variable, OR
        - Stored refresh token in cache directory, OR
        - Interactive OAuth (if enabled)

        Args:
            context: Adapter execution context

        Returns:
            True if credentials can be obtained
        """
        self._controls = context.controls
        token = self._resolve_token()
        if not token:
            return False

        declared_scopes = set(
            s.strip()
            for s in os.environ.get("BL_SPOTIFY_TOKEN_SCOPES", "").split()
            if s.strip()
        )
        required_scopes = self._required_scopes(context.controls)
        if declared_scopes and not required_scopes.issubset(declared_scopes):
            return False

        return True

    def collect(self, context: SourceAdapterContext) -> Dict[str, Any]:
        """
        Acquire raw Spotify data via Web API.

        Collects:
        - Top tracks (3 time ranges: short, medium, long)
        - Saved/liked tracks
        - User playlists and playlist items
        - Recently played tracks (if enabled)

        Handles pagination and respects record limits in context.

        Args:
            context: Adapter execution context

        Returns:
            Dict with keys:
                - 'top_tracks_short': list of track objects
                - 'top_tracks_medium': list of track objects
                - 'top_tracks_long': list of track objects
                - 'saved_tracks': list of track objects
                - 'playlist_items': list of track objects
                - 'recently_played': list of track objects
                - 'user_profile': user profile object
        """
        self._controls = context.controls
        token = self._resolve_token()
        if not token:
            if context.controls.fail_on_collection_error:
                raise RuntimeError("BL_SPOTIFY_AUTH_TOKEN is not set.")
            return {
                "top_tracks_short": [],
                "top_tracks_medium": [],
                "top_tracks_long": [],
                "saved_tracks": [],
                "playlists": [],
                "playlist_items": [],
                "recently_played": [],
                "user_profile": {},
            }

        output = {
            "top_tracks_short": [],
            "top_tracks_medium": [],
            "top_tracks_long": [],
            "saved_tracks": [],
            "playlists": [],
            "playlist_items": [],
            "recently_played": [],
            "user_profile": {},
        }

        def guarded_fetch(label: str, fetch_fn, default):
            try:
                return fetch_fn()
            except Exception as exc:
                if context.controls.fail_on_collection_error:
                    raise
                print(
                    f"[newingestion] {label} failed: {type(exc).__name__}: {exc}",
                    flush=True,
                )
                return default

        try:
            output["user_profile"] = self._api_get(token, "/me", {}, controls=context.controls)
        except Exception as exc:
            if context.controls.fail_on_collection_error:
                raise
            print(
                f"[newingestion] profile fetch failed: {type(exc).__name__}: {exc}",
                flush=True,
            )
            output["user_profile"] = {}

        if context.controls.include_top_tracks:
            top_cap = context.controls.max_top_tracks
            output["top_tracks_short"] = guarded_fetch(
                "top tracks short-term collection",
                lambda: self._fetch_offset_items(token, "/me/top/tracks", max_items=top_cap, base_params={"time_range": "short_term"}, controls=context.controls)
                ,
                [],
            )
            output["top_tracks_medium"] = guarded_fetch(
                "top tracks medium-term collection",
                lambda: self._fetch_offset_items(token, "/me/top/tracks", max_items=top_cap, base_params={"time_range": "medium_term"}, controls=context.controls)
                ,
                [],
            )
            output["top_tracks_long"] = guarded_fetch(
                "top tracks long-term collection",
                lambda: self._fetch_offset_items(token, "/me/top/tracks", max_items=top_cap, base_params={"time_range": "long_term"}, controls=context.controls)
                ,
                [],
            )

        if context.controls.include_saved_tracks:
            output["saved_tracks"] = guarded_fetch(
                "saved tracks collection",
                lambda: self._fetch_offset_items(
                    token,
                    "/me/tracks",
                    max_items=context.controls.max_saved_tracks,
                    controls=context.controls,
                ),
                [],
            )

        if context.controls.include_playlists:
            playlists = guarded_fetch(
                "playlists collection",
                lambda: self._fetch_offset_items(token, "/me/playlists", max_items=0, controls=context.controls)
                ,
                [],
            )
            output["playlists"] = playlists
            max_items = context.controls.max_playlist_items
            playlist_items: List[Dict[str, Any]] = []
            market = output["user_profile"].get("country") if isinstance(output["user_profile"], dict) else None
            for playlist in playlists:
                playlist_id = playlist.get("id")
                if not playlist_id:
                    continue
                playlist_params: Optional[Dict[str, Any]] = None
                if isinstance(market, str) and market:
                    playlist_params = {"market": market}
                try:
                    items = self._fetch_offset_items(
                        token,
                        f"/playlists/{playlist_id}/items",
                        max_items=0,
                        base_params=playlist_params,
                        controls=context.controls,
                    )
                except urllib.error.HTTPError as exc:
                    if exc.code == 403:
                        print(
                            f"[newingestion] playlist items fetch forbidden for playlist_id={playlist_id}; skipping playlist",
                            flush=True,
                        )
                        continue
                    if context.controls.fail_on_collection_error:
                        raise
                    print(
                        f"[newingestion] playlist items fetch failed for playlist_id={playlist_id}: {type(exc).__name__}: {exc}",
                        flush=True,
                    )
                    continue
                except Exception as exc:
                    if context.controls.fail_on_collection_error:
                        raise
                    print(
                        f"[newingestion] playlist items fetch failed for playlist_id={playlist_id}: {type(exc).__name__}: {exc}",
                        flush=True,
                    )
                    continue
                for item_index, item in enumerate(items):
                    if not isinstance(item, dict):
                        continue
                    enriched_item = dict(item)
                    enriched_item["playlist_id"] = playlist_id
                    enriched_item["playlist_name"] = playlist.get("name")
                    owner = playlist.get("owner") if isinstance(playlist.get("owner"), dict) else {}
                    enriched_item["playlist_owner_id"] = owner.get("id")
                    enriched_item["playlist_owner_name"] = owner.get("display_name") or owner.get("id")
                    enriched_item["playlist_snapshot_id"] = playlist.get("snapshot_id")
                    enriched_item["playlist_tracks_total"] = (playlist.get("tracks") or {}).get("total") if isinstance(playlist.get("tracks"), dict) else None
                    enriched_item["playlist_position"] = item_index
                    if playlist.get("description") is not None:
                        enriched_item["description"] = playlist.get("description")
                    if playlist.get("uri") is not None:
                        enriched_item["uri"] = playlist.get("uri")
                    if playlist.get("external_urls") is not None:
                        enriched_item["external_urls"] = playlist.get("external_urls")
                    if playlist.get("collaborative") is not None:
                        enriched_item["collaborative"] = playlist.get("collaborative")
                    if playlist.get("public") is not None:
                        enriched_item["public"] = playlist.get("public")
                    playlist_items.append(enriched_item)
                if max_items > 0 and len(playlist_items) >= max_items:
                    playlist_items = playlist_items[:max_items]
                    break
            output["playlist_items"] = playlist_items

        if context.controls.include_recently_played:
            try:
                payload = self._api_get(token, "/me/player/recently-played", {"limit": 50}, controls=context.controls)
                recent = payload.get("items", []) if isinstance(payload, dict) else []
                cap = context.controls.max_recently_played
                output["recently_played"] = recent[:cap] if cap > 0 else recent
            except Exception as exc:
                if context.controls.fail_on_collection_error:
                    raise
                print(
                    f"[newingestion] recently played collection failed: {type(exc).__name__}: {exc}",
                    flush=True,
                )
                output["recently_played"] = []

        return output


class CsvHistorySourceAdapter(IngestionSourceAdapter):
    """
    Concrete adapter for CSV history import.

    Reads pre-exported history CSVs and returns data in a consistent format.
    Useful for accepting user-provided data or offline analysis.
    """

    @property
    def source_type(self) -> str:
        return "csv_history"

    def verify_credentials(self, context: SourceAdapterContext) -> bool:
        """
        Verify required CSV files exist.

        Looks for *.csv files in context.root_path/inputs/

        Args:
            context: Adapter execution context

        Returns:
            True if at least one input CSV is available
        """
        inputs_dir = context.root_path / "inputs"
        return inputs_dir.exists() and any(inputs_dir.glob("*.csv"))

    def collect(self, context: SourceAdapterContext) -> Dict[str, Any]:
        """
        Load raw data from CSV files.

        Expected CSV structure: one row per track with columns like track_id, track_name, etc.

        Args:
            context: Adapter execution context

        Returns:
            Dict with keys like 'saved_tracks': [parsed rows as dicts]
        """
        inputs_dir = context.root_path / "inputs"
        max_rows = context.controls.max_saved_tracks
        saved_tracks: List[Dict[str, Any]] = []

        if not inputs_dir.exists():
            return {
                "top_tracks_short": [],
                "top_tracks_medium": [],
                "top_tracks_long": [],
                "saved_tracks": [],
                "playlists": [],
                "playlist_items": [],
                "recently_played": [],
                "user_profile": {},
            }

        for csv_path in inputs_dir.glob("*.csv"):
            with open(csv_path, "r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    track_id = row.get("track_id") or row.get("id") or ""
                    if not track_id:
                        continue
                    artist_name = row.get("artist_name") or row.get("artist") or ""
                    mapped = {
                        "track": {
                            "id": track_id,
                            "name": row.get("track_name") or row.get("name") or "",
                            "artists": [{"name": artist_name}] if artist_name else [],
                            "album": {"name": row.get("album_name") or ""},
                            "duration_ms": int(row.get("duration_ms")) if row.get("duration_ms") else None,
                            "explicit": str(row.get("explicit", "")).lower() in {"true", "1", "yes"},
                            "popularity": int(row.get("popularity")) if row.get("popularity") else None,
                            "external_ids": {"isrc": row.get("isrc")},
                            "is_local": str(row.get("is_local", "")).lower() in {"true", "1", "yes"},
                        },
                        "added_at": row.get("added_at"),
                    }
                    saved_tracks.append(mapped)
                    if max_rows > 0 and len(saved_tracks) >= max_rows:
                        break
            if max_rows > 0 and len(saved_tracks) >= max_rows:
                break

        return {
            "top_tracks_short": [],
            "top_tracks_medium": [],
            "top_tracks_long": [],
            "saved_tracks": saved_tracks,
            "playlists": [],
            "playlist_items": [],
            "recently_played": [],
            "user_profile": {},
        }


def get_adapter(source_type: str) -> IngestionSourceAdapter:
    """
    Factory function to get the appropriate adapter for a source type.

    Args:
        source_type: One of 'spotify_api', 'csv_history', etc.

    Returns:
        Instantiated adapter

    Raises:
        ValueError: If source_type is not recognized
    """
    adapters = {
        "spotify_api": SpotifyApiSourceAdapter,
        "csv_history": CsvHistorySourceAdapter,
    }

    if source_type not in adapters:
        raise ValueError(f"Unknown source type: {source_type}. Supported: {list(adapters.keys())}")

    return adapters[source_type]()
