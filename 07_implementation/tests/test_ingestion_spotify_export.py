from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from ingestion import export_spotify_max_dataset as export_module


def _args(tmp_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        client_id="client-id",
        client_secret="client-secret",
        redirect_uri="http://127.0.0.1:8001/spotify/auth/callback",
        scopes="user-top-read",
        output_dir="exports/spotify_api_export",
        env_ps1="",
        request_timeout_seconds=5,
        oauth_timeout_seconds=5,
        max_retries=2,
        max_retry_after_seconds=10,
        batch_size_top_tracks=50,
        batch_size_saved_tracks=50,
        batch_size_playlists=50,
        batch_size_playlist_items=50,
        batch_pause_ms=0,
        min_request_interval_ms=0,
        max_requests_per_minute=120,
        include_top_tracks=False,
        include_saved_tracks=False,
        include_playlists=False,
        include_recently_played=False,
        top_time_ranges="short_term,medium_term,long_term",
        top_max_items_short_term=0,
        top_max_items_medium_term=0,
        top_max_items_long_term=0,
        saved_max_items=0,
        playlists_max_items=0,
        playlist_items_max_per_playlist=0,
        recently_played_limit=50,
        no_browser=True,
        force_auth=False,
    )


def test_replace_export_directory_restores_backup_on_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_dir = tmp_path / "spotify_api_export"
    staging_dir = tmp_path / "spotify_api_export_staging"
    output_dir.mkdir()
    staging_dir.mkdir()
    (output_dir / "old.txt").write_text("old", encoding="utf-8")
    (staging_dir / "new.txt").write_text("new", encoding="utf-8")

    original_rename_directory = export_module._rename_directory
    calls = {"count": 0}

    def failing_rename(source: Path, target: Path) -> None:
        calls["count"] += 1
        if calls["count"] == 2:
            raise OSError("rename failed")
        original_rename_directory(source, target)

    monkeypatch.setattr(export_module, "_rename_directory", failing_rename)

    with pytest.raises(OSError, match="rename failed"):
        export_module._replace_export_directory(staging_dir=staging_dir, output_dir=output_dir)

    assert output_dir.exists()
    assert (output_dir / "old.txt").read_text(encoding="utf-8") == "old"
    assert not (output_dir / "new.txt").exists()


def test_fetch_all_data_marks_playlist_403_status(monkeypatch: pytest.MonkeyPatch) -> None:
    args = argparse.Namespace(
        include_top_tracks=False,
        include_saved_tracks=False,
        include_playlists=True,
        include_recently_played=False,
        top_time_ranges="short_term,medium_term,long_term",
        top_max_items_short_term=0,
        top_max_items_medium_term=0,
        top_max_items_long_term=0,
        saved_max_items=0,
        playlists_max_items=0,
        playlist_items_max_per_playlist=0,
        batch_size_playlists=50,
        batch_size_playlist_items=50,
    )
    playlist = {"id": "playlist-1", "name": "Playlist 1", "owner": {"id": "owner-1"}, "items": {"total": 3}}

    class _FakeClient:
        def api_get(self, path: str, params: dict[str, object]) -> dict[str, object]:
            assert path == "/me"
            return {"id": "user-1", "country": "GB"}

    def fake_fetch_all_offset_pages(**kwargs):
        path = kwargs["path"]
        if path == "/me/playlists":
            return [playlist]
        if path == "/playlists/playlist-1/items":
            raise export_module.SpotifyApiError("forbidden", status_code=403)
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(export_module, "fetch_all_offset_pages", fake_fetch_all_offset_pages)

    data = export_module._fetch_all_data(client=_FakeClient(), args=args)

    assert data["playlists"][0]["playlist_items_access_status"] == "forbidden"
    assert data["playlists"][0]["playlist_items_skipped_reason"] == "spotify_playlist_items_403_forbidden"
    assert data["playlist_item_batches"] == []


def test_fetch_all_data_deduplicates_playlists_by_id(monkeypatch: pytest.MonkeyPatch) -> None:
    args = argparse.Namespace(
        include_top_tracks=False,
        include_saved_tracks=False,
        include_playlists=True,
        include_recently_played=False,
        top_time_ranges="short_term,medium_term,long_term",
        top_max_items_short_term=0,
        top_max_items_medium_term=0,
        top_max_items_long_term=0,
        saved_max_items=0,
        playlists_max_items=0,
        playlist_items_max_per_playlist=0,
        batch_size_playlists=50,
        batch_size_playlist_items=50,
    )
    playlist = {"id": "playlist-1", "name": "Playlist 1", "owner": {"id": "owner-1"}, "items": {"total": 3}}
    playlist_calls = {"count": 0}

    class _FakeClient:
        def api_get(self, path: str, params: dict[str, object]) -> dict[str, object]:
            assert path == "/me"
            return {"id": "user-1", "country": "GB"}

    def fake_fetch_all_offset_pages(**kwargs):
        path = kwargs["path"]
        if path == "/me/playlists":
            return [playlist, dict(playlist)]
        if path == "/playlists/playlist-1/items":
            playlist_calls["count"] += 1
            return [{"item": {"type": "track", "id": "t1"}}]
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(export_module, "fetch_all_offset_pages", fake_fetch_all_offset_pages)

    data = export_module._fetch_all_data(client=_FakeClient(), args=args)

    assert len(data["playlists"]) == 1
    assert len(data["playlist_item_batches"]) == 1
    assert playlist_calls["count"] == 1


def test_fetch_all_data_recently_played_uses_single_request_and_clamps_limit() -> None:
    args = argparse.Namespace(
        include_top_tracks=False,
        include_saved_tracks=False,
        include_playlists=False,
        include_recently_played=True,
        top_time_ranges="short_term,medium_term,long_term",
        top_max_items_short_term=0,
        top_max_items_medium_term=0,
        top_max_items_long_term=0,
        saved_max_items=0,
        playlists_max_items=0,
        playlist_items_max_per_playlist=0,
        batch_size_playlists=50,
        batch_size_playlist_items=50,
        recently_played_limit=999,
    )
    recently_played_calls: list[dict[str, object]] = []

    class _FakeClient:
        def api_get(self, path: str, params: dict[str, object]) -> dict[str, object]:
            if path == "/me":
                return {"id": "user-1", "country": "GB"}
            if path == "/me/player/recently-played":
                recently_played_calls.append(params)
                return {
                    "items": [
                        {"track": {"type": "track", "id": "t1"}},
                        {"track": {"type": "track", "id": "t2"}},
                    ],
                    "next": "https://api.spotify.com/v1/me/player/recently-played?before=123",
                    "cursors": {"before": "123"},
                }
            raise AssertionError(f"unexpected path: {path}")

    data = export_module._fetch_all_data(client=_FakeClient(), args=args)

    assert recently_played_calls == [{"limit": 50}]
    assert len(data["recently_played_items"]) == 2


def test_fetch_all_data_recently_played_raises_on_non_list_items() -> None:
    args = argparse.Namespace(
        include_top_tracks=False,
        include_saved_tracks=False,
        include_playlists=False,
        include_recently_played=True,
        top_time_ranges="short_term,medium_term,long_term",
        top_max_items_short_term=0,
        top_max_items_medium_term=0,
        top_max_items_long_term=0,
        saved_max_items=0,
        playlists_max_items=0,
        playlist_items_max_per_playlist=0,
        batch_size_playlists=50,
        batch_size_playlist_items=50,
        recently_played_limit=7,
    )

    class _FakeClient:
        def api_get(self, path: str, params: dict[str, object]) -> dict[str, object]:
            if path == "/me":
                return {"id": "user-1", "country": "GB"}
            if path == "/me/player/recently-played":
                return {"items": {"not": "a-list"}}
            raise AssertionError(f"unexpected path: {path}")

    with pytest.raises(RuntimeError, match="Expected list items"):
        export_module._fetch_all_data(client=_FakeClient(), args=args)


def test_main_writes_summary_to_staging_before_swap(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    args = _args(tmp_path)
    swap_check = {"called": False}

    class _FakeClient:
        def __init__(self, args: argparse.Namespace, token_payload: dict[str, object]) -> None:
            self.args = args
            self.token_payload = token_payload
            self.request_log = [{"path": "/me", "status": 200}]

    def fake_write_all_artifacts(output_dir: Path, data: dict[str, object], generated_at: str):
        artifact_path = output_dir / "spotify_profile.json"
        artifact_path.write_text("{}", encoding="utf-8")
        return {"spotify_profile.json": artifact_path}, {
            "playlist_item_items_total": 0,
            "playlist_item_rows_kept": 0,
            "playlist_item_rows_skipped": 0,
        }

    def fake_replace_export_directory(staging_dir: Path, output_dir: Path) -> None:
        swap_check["called"] = True
        summary_path = staging_dir / "spotify_export_run_summary.json"
        request_log_path = staging_dir / "spotify_request_log.jsonl"
        assert summary_path.exists()
        assert request_log_path.exists()
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        assert summary["artifacts"]["spotify_profile.json"]["path"] == "exports/spotify_api_export/spotify_profile.json"

    monkeypatch.setattr(export_module, "parse_args", lambda: args)
    monkeypatch.setattr(export_module, "impl_root", lambda: tmp_path)
    monkeypatch.setattr(export_module, "complete_oauth_flow", lambda _args: {"access_token": "token", "scope": "user-top-read"})
    monkeypatch.setattr(export_module, "SpotifyApiClient", _FakeClient)
    monkeypatch.setattr(
        export_module,
        "_fetch_all_data",
        lambda client, args: {
            "profile": {"id": "user-1", "country": "GB", "product": "premium"},
            "top_tracks_by_range": {},
            "saved_track_items": [],
            "playlists": [],
            "playlist_item_batches": [],
            "recently_played_items": [],
        },
    )
    monkeypatch.setattr(export_module, "_write_all_artifacts", fake_write_all_artifacts)
    monkeypatch.setattr(export_module, "_replace_export_directory", fake_replace_export_directory)

    export_module.main()

    assert swap_check["called"] is True
