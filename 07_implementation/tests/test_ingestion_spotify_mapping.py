from ingestion.spotify_mapping import (
    build_playlist_rows,
    build_playlist_item_rows,
    build_recently_played_rows,
    build_saved_track_rows,
)


def _track_payload(track_id: str, track_name: str = "Track Name") -> dict:
    return {
        "type": "track",
        "id": track_id,
        "uri": f"spotify:track:{track_id}",
        "name": track_name,
        "artists": [{"id": "artist-1", "name": "Artist One"}],
        "album": {
            "id": "album-1",
            "name": "Album One",
            "release_date": "2024-01-01",
            "release_date_precision": "day",
        },
        "duration_ms": 180000,
        "popularity": 60,
        "explicit": False,
        "is_playable": True,
        "external_ids": {"isrc": "USRC17607839"},
        "external_urls": {"spotify": f"https://open.spotify.com/track/{track_id}"},
        "href": f"https://api.spotify.com/v1/tracks/{track_id}",
    }


def test_playlist_items_item_first_track_payload_populates_track_fields() -> None:
    rows = build_playlist_item_rows(
        [
            {
                "playlist": {"id": "pl1", "name": "Playlist 1"},
                "items": [
                    {
                        "added_at": "2026-03-28T00:00:00Z",
                        "added_by": {"id": "user-1"},
                        "is_local": False,
                        "item": _track_payload("track-abc", "From Item"),
                    }
                ],
            }
        ]
    )

    assert len(rows) == 1
    assert rows[0]["track_id"] == "track-abc"
    assert rows[0]["track_name"] == "From Item"
    assert rows[0]["artist_names"] == "Artist One"


def test_playlist_items_fallback_to_deprecated_track_payload() -> None:
    rows = build_playlist_item_rows(
        [
            {
                "playlist": {"id": "pl2", "name": "Playlist 2"},
                "items": [
                    {
                        "added_at": "2026-03-28T00:00:00Z",
                        "added_by": {"id": "user-1"},
                        "is_local": False,
                        "track": _track_payload("track-legacy", "From Track"),
                    }
                ],
            }
        ]
    )

    assert len(rows) == 1
    assert rows[0]["track_id"] == "track-legacy"
    assert rows[0]["track_name"] == "From Track"


def test_playlist_items_skip_episode_and_unavailable() -> None:
    rows = build_playlist_item_rows(
        [
            {
                "playlist": {"id": "pl3", "name": "Playlist 3"},
                "items": [
                    {"item": {"type": "episode", "id": "ep-1"}},
                    {"item": None},
                    {"item": _track_payload("track-keep", "Keep Me")},
                ],
            }
        ]
    )

    assert len(rows) == 1
    assert rows[0]["track_id"] == "track-keep"


def test_saved_tracks_item_first_fallback_support() -> None:
    rows = build_saved_track_rows(
        [
            {"added_at": "2026-03-28T00:00:00Z", "item": _track_payload("saved-track")}
        ]
    )

    assert len(rows) == 1
    assert rows[0]["track_id"] == "saved-track"


def test_recently_played_item_first_fallback_support() -> None:
    rows = build_recently_played_rows(
        [
            {
                "played_at": "2026-03-28T00:00:00Z",
                "context": {"type": "playlist", "uri": "spotify:playlist:pl1"},
                "item": _track_payload("recent-track"),
            }
        ]
    )

    assert len(rows) == 1
    assert rows[0]["track_id"] == "recent-track"
    assert rows[0]["context_type"] == "playlist"


def test_playlist_rows_include_item_access_metadata() -> None:
    rows = build_playlist_rows(
        [
            {
                "id": "pl-1",
                "name": "Playlist 1",
                "owner": {"id": "owner-1"},
                "items": {"total": 12},
                "playlist_items_access_status": "forbidden",
                "playlist_items_skipped_reason": "spotify_playlist_items_403_forbidden",
            }
        ]
    )

    assert rows[0]["tracks_total"] == 12
    assert rows[0]["items_access_status"] == "forbidden"
    assert rows[0]["items_skipped_reason"] == "spotify_playlist_items_403_forbidden"
