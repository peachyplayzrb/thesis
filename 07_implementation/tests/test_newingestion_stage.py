"""Tests for the newingestion stage and its canonical output contract."""

import json
import os
import sys
import tempfile
import urllib.error
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from newingestion.main import main as newingestion_main
from newingestion.models import (
    IngestionDomainBundle,
    NewingestionControls,
    NewingestionPaths,
    PlaylistTrackMembership,
    SavedTrackMembership,
    SpotifyAccountProfile,
    SpotifyArtist,
    SpotifyTrack,
    TopTrackMembership,
    TrackArtistRelation,
)
from newingestion.normalizer import normalize_raw_data_to_bundle, normalize_spotify_track
from newingestion.runtime_controls import (
    get_newingestion_payload,
    load_newingestion_controls_from_env,
    resolve_newingestion_runtime_controls,
)
from newingestion.source_adapters import (
    CsvHistorySourceAdapter,
    SourceAdapterContext,
    SpotifyApiSourceAdapter,
    get_adapter,
)
from newingestion.stage import IngestionStage
from newingestion.validator import validate_bundle
from newingestion.writer import write_outputs


class TestModels:
    def test_newingestion_controls_default(self):
        controls = NewingestionControls()
        assert controls.source_type == "spotify_api"
        assert controls.include_top_tracks is True
        assert controls.fail_on_missing_scope is False

    def test_newingestion_controls_frozen(self):
        controls = NewingestionControls()
        with pytest.raises(Exception):
            controls.include_top_tracks = False

    def test_domain_bundle_counts(self):
        bundle = IngestionDomainBundle(
            run_id="test-run",
            generated_at_utc=datetime.now(UTC),
            source_type="spotify_api",
            tracks=[SpotifyTrack(track_id="1", name="Song 1"), SpotifyTrack(track_id="2", name="Song 2")],
            top_track_memberships=[TopTrackMembership(track_id="1", time_range="short_term", rank=0)],
            saved_track_memberships=[SavedTrackMembership(track_id="2")],
        )
        counts = bundle.counts()
        assert counts["top_tracks_short"] == 1
        assert counts["saved_tracks"] == 1
        assert counts["total_unique_tracks"] == 2
        assert counts["track_entities"] == 2


class TestRuntimeControls:
    def test_load_from_payload(self):
        payload = json.dumps({"newingestion": {"include_saved_tracks": False}})
        with patch.dict(os.environ, {"BL_STAGE_CONFIG_JSON": payload}):
            payload_result = get_newingestion_payload()
            assert payload_result is not None
            assert payload_result["include_saved_tracks"] is False

    def test_resolve_with_defaults(self):
        controls = resolve_newingestion_runtime_controls(run_config_path=None)
        assert controls.source_type == "spotify_api"
        assert controls.include_top_tracks is True

    def test_load_from_env(self):
        with patch.dict(os.environ, {"BL_NEWINGESTION_INCLUDE_SAVED_TRACKS": "false"}):
            env_controls = load_newingestion_controls_from_env()
            assert env_controls["include_saved_tracks"] is False

    def test_control_clamping(self):
        payload = json.dumps({"newingestion": {"cache_ttl_seconds": 999999, "throttle_sleep_seconds": -5}})
        with patch.dict(os.environ, {"BL_STAGE_CONFIG_JSON": payload}):
            controls = resolve_newingestion_runtime_controls()
            assert controls.cache_ttl_seconds <= 86400
            assert controls.throttle_sleep_seconds >= 0.01


class TestNormalization:
    def test_normalize_spotify_track(self):
        raw_track = {
            "id": "track123",
            "name": "Test Song",
            "artists": [{"id": "artist1", "name": "Lead Artist"}],
            "album": {"id": "album1", "name": "Test Album"},
            "duration_ms": 180000,
            "popularity": 75,
        }
        canonical = normalize_spotify_track(raw_track)
        assert canonical is not None
        assert canonical.track_id == "track123"
        assert canonical.name == "Test Song"
        assert canonical.album_id == "album1"

    def test_normalize_raw_data_to_bundle_preserves_multi_artist_and_playlist_context(self):
        controls = NewingestionControls(include_top_tracks=True, include_saved_tracks=False, include_playlists=True)
        raw_data = {
            "user_profile": {"id": "user123", "country": "US", "product": "premium"},
            "playlists": [
                {
                    "id": "pl1",
                    "name": "My Playlist",
                    "owner": {"id": "owner1", "display_name": "Owner"},
                    "snapshot_id": "snap-1",
                    "tracks": {"total": 1},
                }
            ],
            "top_tracks_short": [
                {
                    "id": "track1",
                    "name": "Song 1",
                    "artists": [
                        {"id": "a1", "name": "Artist 1"},
                        {"id": "a2", "name": "Artist 2"},
                    ],
                    "album": {"id": "al1", "name": "Album 1"},
                }
            ],
            "playlist_items": [
                {
                    "playlist_id": "pl1",
                    "playlist_name": "My Playlist",
                    "playlist_owner_id": "owner1",
                    "playlist_owner_name": "Owner",
                    "playlist_snapshot_id": "snap-1",
                    "playlist_tracks_total": 1,
                    "playlist_position": 0,
                    "added_at": "2026-01-01T00:00:00Z",
                    "track": {
                        "id": "track1",
                        "name": "Song 1",
                        "artists": [
                            {"id": "a1", "name": "Artist 1"},
                            {"id": "a2", "name": "Artist 2"},
                        ],
                        "album": {"id": "al1", "name": "Album 1"},
                    },
                }
            ],
        }

        bundle = normalize_raw_data_to_bundle(raw_data, controls, "run123")
        assert bundle.user_id == "user123"
        assert len(bundle.tracks) == 1
        assert len(bundle.artists) == 2
        assert len(bundle.track_artist_relations) == 2
        assert len(bundle.playlists) == 1
        assert len(bundle.playlist_track_memberships) == 1
        assert bundle.playlist_track_memberships[0].playlist_id == "pl1"
        assert bundle.top_track_memberships[0].track_id == "track1"

    def test_recently_played_preserves_event_timestamp(self):
        controls = NewingestionControls(include_recently_played=True, include_top_tracks=False, include_saved_tracks=False, include_playlists=False)
        raw_data = {
            "user_profile": {"id": "user123"},
            "recently_played": [
                {
                    "track": {
                        "id": "track1",
                        "name": "Song 1",
                        "artists": [{"id": "a1", "name": "Artist 1"}],
                        "album": {"id": "al1", "name": "Album 1"},
                    },
                    "played_at": "2026-04-01T12:00:00Z",
                    "context": {"type": "playlist", "uri": "spotify:playlist:pl1"},
                }
            ],
        }
        bundle = normalize_raw_data_to_bundle(raw_data, controls, "run123")
        assert len(bundle.recently_played_events) == 1
        assert bundle.recently_played_events[0].played_at is not None
        assert bundle.recently_played_events[0].context_type == "playlist"

    def test_normalize_handles_non_dict_user_profile(self):
        controls = NewingestionControls(include_saved_tracks=False, include_top_tracks=False, include_playlists=False)
        bundle = normalize_raw_data_to_bundle({"user_profile": None}, controls, "run123")
        assert bundle.user_id is None

    def test_normalize_spotify_track_rejects_non_dict(self):
        assert normalize_spotify_track("bad") is None


class TestValidationAndWriting:
    def test_validate_bundle_warns_on_missing_user(self):
        bundle = IngestionDomainBundle(run_id="test", generated_at_utc=datetime.now(UTC), source_type="spotify_api")
        validated = validate_bundle(bundle, NewingestionControls())
        assert "User ID not found in profile" in validated.warnings

    def test_validate_bundle_detects_duplicates_from_memberships(self):
        bundle = IngestionDomainBundle(
            run_id="test",
            generated_at_utc=datetime.now(UTC),
            source_type="spotify_api",
            account_profile=SpotifyAccountProfile(user_id="u1"),
            tracks=[SpotifyTrack(track_id="1", name="Song")],
            artists=[SpotifyArtist(artist_id="a1", name="Artist")],
            track_artist_relations=[TrackArtistRelation(track_id="1", artist_id="a1", artist_order=0)],
            top_track_memberships=[TopTrackMembership(track_id="1", time_range="short_term", rank=4)],
            saved_track_memberships=[SavedTrackMembership(track_id="1")],
        )
        validated = validate_bundle(bundle, NewingestionControls())
        assert any("Duplicate track IDs detected" in warning for warning in validated.warnings)
        assert len(validated.duplicate_track_locations["1"]) == 2

    def test_validate_bundle_warns_on_missing_profile_fields(self):
        bundle = IngestionDomainBundle(
            run_id="run-1",
            generated_at_utc=datetime.now(UTC),
            source_type="spotify_api",
            account_profile=SpotifyAccountProfile(user_id="u1", country=None, product=None),
        )
        validated = validate_bundle(bundle, NewingestionControls())
        assert "Spotify profile is missing country or product; token may lack user-read-private scope" in validated.warnings

    def test_validate_bundle_warns_on_incomplete_tracks(self):
        bundle = IngestionDomainBundle(
            run_id="test",
            generated_at_utc=datetime.now(UTC),
            source_type="spotify_api",
            account_profile=SpotifyAccountProfile(user_id="u1"),
            tracks=[SpotifyTrack(track_id="1", name="")],
        )
        validated = validate_bundle(bundle, NewingestionControls(include_top_tracks=False, include_saved_tracks=False, include_playlists=False))
        assert any("tracks missing name or artist" in warning for warning in validated.warnings)

    def test_write_outputs_emits_manifest_and_duplicate_artifact(self):
        controls = NewingestionControls()
        bundle = IngestionDomainBundle(
            run_id="test",
            generated_at_utc=datetime.now(UTC),
            source_type="spotify_api",
            account_profile=SpotifyAccountProfile(user_id="u1", country="US", product="premium"),
            tracks=[SpotifyTrack(track_id="1", name="Song")],
            artists=[SpotifyArtist(artist_id="a1", name="Artist")],
            track_artist_relations=[TrackArtistRelation(track_id="1", artist_id="a1", artist_order=0)],
            top_track_memberships=[TopTrackMembership(track_id="1", time_range="short_term", rank=0)],
            duplicate_track_locations={"1": [{"event_type": "top_track"}, {"event_type": "saved_track"}]},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts = write_outputs(bundle, Path(tmpdir), "RUN-1", controls)
            assert artifacts.manifest_artifact_path.exists()
            assert artifacts.duplicate_track_locations_path is not None
            assert artifacts.duplicate_track_locations_path.exists()
            manifest = json.loads(artifacts.manifest_artifact_path.read_text(encoding="utf-8"))
            assert "tracks" in manifest["artifact_inventory"]
            assert "top_tracks_short" in artifacts.compatibility_export_paths


class TestMainEntrypoint:
    def test_main_accepts_argv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("newingestion.main.IngestionStage") as stage_cls:
                stage_instance = stage_cls.return_value
                stage_instance.run.return_value = MagicMock()
                stage_instance.build_summary.return_value = {"run_id": "test"}
                rc = newingestion_main(["--root", tmpdir])
                assert rc == 0
                stage_cls.assert_called_once()


class TestStage:
    def test_stage_initialization(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stage = IngestionStage(root=Path(tmpdir))
            assert stage.root == Path(tmpdir)
            assert stage.run_id is not None
            assert stage.run_id.startswith("INGESTION-")

    def test_stage_resolve_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stage = IngestionStage(root=Path(tmpdir))
            paths = stage.resolve_paths()
            assert paths.root == Path(tmpdir)
            assert paths.outputs_dir == Path(tmpdir) / "outputs"

    def test_stage_resolve_runtime_controls(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stage = IngestionStage(root=Path(tmpdir))
            controls = stage.resolve_runtime_controls()
            assert isinstance(controls, NewingestionControls)
            assert controls.source_type == "spotify_api"


class TestSourceAdapters:
    def test_get_adapter_spotify(self):
        adapter = get_adapter("spotify_api")
        assert isinstance(adapter, SpotifyApiSourceAdapter)
        assert adapter.source_type == "spotify_api"

    def test_get_adapter_invalid(self):
        with pytest.raises(ValueError):
            get_adapter("invalid_source")

    def test_spotify_verify_credentials_present(self):
        adapter = SpotifyApiSourceAdapter()
        context = SourceAdapterContext(root_path=Path("."), controls=NewingestionControls())
        with patch.dict(os.environ, {"BL_SPOTIFY_AUTH_TOKEN": "abc123"}, clear=False):
            assert adapter.verify_credentials(context) is True

    def test_spotify_verify_credentials_scope_mismatch(self):
        adapter = SpotifyApiSourceAdapter()
        controls = NewingestionControls(include_saved_tracks=True)
        context = SourceAdapterContext(root_path=Path("."), controls=controls)
        with patch.dict(os.environ, {"BL_SPOTIFY_AUTH_TOKEN": "abc123", "BL_SPOTIFY_TOKEN_SCOPES": "user-top-read"}, clear=False):
            assert adapter.verify_credentials(context) is False

    def test_spotify_resolve_token_uses_refresh_flow(self):
        adapter = SpotifyApiSourceAdapter()
        controls = NewingestionControls()
        context = SourceAdapterContext(root_path=Path("."), controls=controls)
        with patch.dict(
            os.environ,
            {
                "BL_SPOTIFY_AUTH_TOKEN": "",
                "BL_SPOTIFY_REFRESH_TOKEN": "refresh",
                "BL_SPOTIFY_CLIENT_ID": "client",
                "BL_SPOTIFY_CLIENT_SECRET": "secret",
            },
            clear=False,
        ):
            with patch("newingestion.source_adapters.request_token", return_value={"access_token": "newtoken"}):
                assert adapter.verify_credentials(context) is True

    def test_spotify_verify_credentials_missing(self):
        adapter = SpotifyApiSourceAdapter()
        context = SourceAdapterContext(root_path=Path("."), controls=NewingestionControls())
        with patch.dict(os.environ, {}, clear=True):
            assert adapter.verify_credentials(context) is False

    def test_spotify_collect_returns_required_shape(self):
        adapter = SpotifyApiSourceAdapter()
        controls = NewingestionControls(include_top_tracks=True, include_saved_tracks=True, include_playlists=False, include_recently_played=False, max_top_tracks=2, max_saved_tracks=1)
        context = SourceAdapterContext(root_path=Path("."), controls=controls)

        def fake_api_get(token, path, params=None, controls=None):
            if path == "/me":
                return {"id": "u1"}
            return {"items": []}

        def fake_fetch_offset_items(token, path, max_items=0, base_params=None, controls=None):
            if path == "/me/top/tracks":
                return [{"id": "t1"}, {"id": "t2"}]
            if path == "/me/tracks":
                return [{"track": {"id": "s1"}}]
            return []

        with patch.dict(os.environ, {"BL_SPOTIFY_AUTH_TOKEN": "abc123"}, clear=False):
            with patch.object(adapter, "_api_get", side_effect=fake_api_get):
                with patch.object(adapter, "_fetch_offset_items", side_effect=fake_fetch_offset_items):
                    out = adapter.collect(context)

        expected_keys = {
            "top_tracks_short",
            "top_tracks_medium",
            "top_tracks_long",
            "saved_tracks",
            "playlists",
            "playlist_items",
            "recently_played",
            "user_profile",
        }
        assert expected_keys.issubset(set(out.keys()))
        assert len(out["top_tracks_short"]) <= 2
        assert len(out["saved_tracks"]) <= 1

    def test_spotify_collect_playlist_items_uses_items_endpoint_and_preserves_playlist_context(self):
        adapter = SpotifyApiSourceAdapter()
        controls = NewingestionControls(include_top_tracks=False, include_saved_tracks=False, include_playlists=True, include_recently_played=False)
        context = SourceAdapterContext(root_path=Path("."), controls=controls)

        def fake_api_get(token, path, params=None, controls=None):
            if path == "/me":
                return {"id": "u1", "country": "MT", "product": "premium"}
            return {"items": []}

        def fake_fetch_offset_items(token, path, max_items=0, base_params=None, controls=None):
            if path == "/me/playlists":
                return [{"id": "playlist-1", "name": "Playlist One", "owner": {"id": "owner-1", "display_name": "Owner"}, "tracks": {"total": 1}}]
            if path == "/playlists/playlist-1/items":
                assert base_params == {"market": "MT"}
                return [{"track": {"id": "p1", "name": "Playlist Song", "artists": [{"id": "a1", "name": "Artist"}]}}]
            return []

        with patch.dict(os.environ, {"BL_SPOTIFY_AUTH_TOKEN": "abc123"}, clear=False):
            with patch.object(adapter, "_api_get", side_effect=fake_api_get):
                with patch.object(adapter, "_fetch_offset_items", side_effect=fake_fetch_offset_items):
                    out = adapter.collect(context)

        assert out["user_profile"]["country"] == "MT"
        assert len(out["playlists"]) == 1
        assert len(out["playlist_items"]) == 1
        assert out["playlist_items"][0]["playlist_id"] == "playlist-1"
        assert out["playlist_items"][0]["playlist_position"] == 0

    def test_spotify_collect_playlist_items_skips_forbidden_playlist(self):
        adapter = SpotifyApiSourceAdapter()
        controls = NewingestionControls(include_top_tracks=False, include_saved_tracks=False, include_playlists=True, include_recently_played=False)
        context = SourceAdapterContext(root_path=Path("."), controls=controls)

        def fake_api_get(token, path, params=None, controls=None):
            if path == "/me":
                return {"id": "u1", "country": "MT", "product": "premium"}
            return {"items": []}

        def fake_fetch_offset_items(token, path, max_items=0, base_params=None, controls=None):
            if path == "/me/playlists":
                return [{"id": "playlist-1"}, {"id": "playlist-2"}]
            if path == "/playlists/playlist-1/items":
                raise urllib.error.HTTPError(path, 403, "Forbidden", None, None)
            if path == "/playlists/playlist-2/items":
                return [{"track": {"id": "p2", "name": "Playlist Song 2", "artists": [{"id": "a2", "name": "Artist 2"}]}}]
            return []

        with patch.dict(os.environ, {"BL_SPOTIFY_AUTH_TOKEN": "abc123"}, clear=False):
            with patch.object(adapter, "_api_get", side_effect=fake_api_get):
                with patch.object(adapter, "_fetch_offset_items", side_effect=fake_fetch_offset_items):
                    out = adapter.collect(context)

        assert len(out["playlist_items"]) == 1
        assert out["playlist_items"][0]["track"]["id"] == "p2"

    def test_csv_verify_credentials_with_file(self):
        adapter = CsvHistorySourceAdapter()
        controls = NewingestionControls(source_type="csv_history")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            inputs = root / "inputs"
            inputs.mkdir(parents=True, exist_ok=True)
            (inputs / "tracks.csv").write_text("track_id,track_name\n1,Song 1\n", encoding="utf-8")
            context = SourceAdapterContext(root_path=root, controls=controls)
            assert adapter.verify_credentials(context) is True

    def test_csv_collect_respects_max_saved_tracks(self):
        adapter = CsvHistorySourceAdapter()
        controls = NewingestionControls(source_type="csv_history", max_saved_tracks=1)
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            inputs = root / "inputs"
            inputs.mkdir(parents=True, exist_ok=True)
            (inputs / "tracks.csv").write_text("track_id,track_name,artist_name\n1,Song 1,Artist 1\n2,Song 2,Artist 2\n", encoding="utf-8")
            context = SourceAdapterContext(root_path=root, controls=controls)
            out = adapter.collect(context)
            assert len(out["saved_tracks"]) == 1
            assert out["playlists"] == []

    def test_spotify_interactive_oauth_called_when_enabled(self):
        adapter = SpotifyApiSourceAdapter()
        controls = NewingestionControls(enable_interactive_oauth=True, oauth_client_id="test_id", oauth_client_secret="test_secret")
        adapter._controls = controls
        mock_response = {"access_token": "oauth_token123", "scope": "user-top-read"}
        with patch.dict(os.environ, {"BL_SPOTIFY_AUTH_TOKEN": "", "BL_SPOTIFY_REFRESH_TOKEN": ""}, clear=True):
            with patch("newingestion.source_adapters.complete_oauth_flow", return_value=mock_response) as mock_oauth:
                token = adapter._resolve_token()
        assert token == "oauth_token123"
        mock_oauth.assert_called_once()

    def test_spotify_interactive_oauth_skipped_when_disabled(self):
        adapter = SpotifyApiSourceAdapter()
        controls = NewingestionControls(enable_interactive_oauth=False)
        adapter._controls = controls
        with patch.dict(os.environ, {"BL_SPOTIFY_AUTH_TOKEN": "", "BL_SPOTIFY_REFRESH_TOKEN": ""}, clear=True):
            with patch("newingestion.source_adapters.complete_oauth_flow") as mock_oauth:
                token = adapter._resolve_token()
        assert token == ""
        mock_oauth.assert_not_called()

    def test_spotify_interactive_oauth_requires_client_creds(self):
        adapter = SpotifyApiSourceAdapter()
        controls = NewingestionControls(enable_interactive_oauth=True, oauth_client_id="test_id")
        adapter._controls = controls
        with patch.dict(os.environ, {"BL_SPOTIFY_AUTH_TOKEN": "", "BL_SPOTIFY_REFRESH_TOKEN": ""}, clear=True):
            with patch("newingestion.source_adapters.complete_oauth_flow") as mock_oauth:
                token = adapter._resolve_token()
        assert token == ""
        mock_oauth.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
