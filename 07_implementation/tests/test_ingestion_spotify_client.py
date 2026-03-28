from __future__ import annotations

import argparse
import urllib.error

import pytest

from ingestion.spotify_client import SpotifyApiClient, fetch_all_offset_pages


def _client_args() -> argparse.Namespace:
    return argparse.Namespace(
        client_id="client-id",
        client_secret="client-secret",
        request_timeout_seconds=5,
        max_retries=2,
        max_retry_after_seconds=10,
        batch_pause_ms=0,
        min_request_interval_ms=0,
        max_requests_per_minute=100,
    )


def test_refresh_access_token_retries_url_error_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    client = SpotifyApiClient(
        args=_client_args(),
        token_payload={"access_token": "old-token", "refresh_token": "refresh-token", "expires_at_epoch": 0},
    )
    calls = {"count": 0}

    def fake_request_token(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise urllib.error.URLError("temporary outage")
        return {"access_token": "new-token", "expires_in": 3600, "token_type": "Bearer"}

    monkeypatch.setattr("ingestion.spotify_client.request_token", fake_request_token)
    monkeypatch.setattr("ingestion.spotify_client.time.sleep", lambda *_args, **_kwargs: None)

    client.refresh_access_token()

    assert calls["count"] == 2
    assert client.access_token == "new-token"
def test_fetch_all_offset_pages_advances_by_limit_on_short_page_with_next() -> None:
    class _FakeClient:
        def __init__(self) -> None:
            self.args = argparse.Namespace(batch_pause_ms=0)
            self.seen_offsets: list[int] = []

        def api_get(self, path: str, params: dict[str, object]) -> dict[str, object]:
            offset = int(params.get("offset", 0))
            self.seen_offsets.append(offset)
            if offset == 0:
                return {
                    "items": [{"id": f"p0_{idx}"} for idx in range(25)],
                    "next": "https://api.spotify.com/v1/me/playlists?offset=50&limit=50",
                    "total": 120,
                }
            if offset == 50:
                return {
                    "items": [{"id": f"p1_{idx}"} for idx in range(25)],
                    "next": "https://api.spotify.com/v1/me/playlists?offset=100&limit=50",
                    "total": 120,
                }
            return {
                "items": [],
                "next": None,
                "total": 120,
            }

    client = _FakeClient()
    items = fetch_all_offset_pages(
        client=client,
        path="/me/playlists",
        base_params={},
        limit=50,
    )

    assert client.seen_offsets == [0, 50, 100]
    assert len(items) == 50
    assert len({entry["id"] for entry in items}) == 50


def test_fetch_all_offset_pages_respects_max_items_with_short_pages() -> None:
    class _FakeClient:
        def __init__(self) -> None:
            self.args = argparse.Namespace(batch_pause_ms=0)
            self.seen_offsets: list[int] = []

        def api_get(self, path: str, params: dict[str, object]) -> dict[str, object]:
            offset = int(params.get("offset", 0))
            self.seen_offsets.append(offset)
            if offset == 0:
                return {
                    "items": [{"id": f"item_{idx}"} for idx in range(20)],
                    "next": "https://api.spotify.com/v1/me/tracks?offset=30&limit=30",
                    "total": 200,
                }
            if offset == 30:
                return {
                    "items": [{"id": f"item_{idx}"} for idx in range(20, 40)],
                    "next": "https://api.spotify.com/v1/me/tracks?offset=60&limit=30",
                    "total": 200,
                }
            raise AssertionError(f"unexpected offset {offset}")

    client = _FakeClient()
    items = fetch_all_offset_pages(
        client=client,
        path="/me/tracks",
        base_params={},
        limit=50,
        max_items=30,
    )

    assert client.seen_offsets == [0, 30]
    assert len(items) == 30
