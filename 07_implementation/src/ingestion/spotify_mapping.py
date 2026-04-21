from __future__ import annotations

from typing import Any

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


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _artist_fields(track: dict[str, Any]) -> tuple[str, str]:
    artists = track.get("artists", [])
    if not isinstance(artists, list):
        return "", ""
    artist_ids = [artist.get("id", "") for artist in artists if isinstance(artist, dict)]
    artist_names = [artist.get("name", "") for artist in artists if isinstance(artist, dict)]
    return (
        " | ".join([str(artist_id) for artist_id in artist_ids if artist_id]),
        " | ".join([str(name) for name in artist_names if name]),
    )


def _duration_fields(track: dict[str, Any]) -> tuple[Any, float | None]:
    duration_ms = track.get("duration_ms")
    duration_seconds = None
    if isinstance(duration_ms, int | float):
        duration_seconds = round(float(duration_ms) / 1000.0, 3)
    return duration_ms, duration_seconds


def extract_track_fields(track: dict[str, Any]) -> dict[str, Any]:
    track_data = _dict_or_empty(track)
    album = _dict_or_empty(track_data.get("album", {}))
    external_ids = _dict_or_empty(track_data.get("external_ids", {}))
    restrictions = _dict_or_empty(track_data.get("restrictions", {}))
    linked_from = _dict_or_empty(track_data.get("linked_from", {}))
    external_urls = _dict_or_empty(track_data.get("external_urls", {}))
    artist_ids, artist_names = _artist_fields(track_data)
    duration_ms, duration_seconds = _duration_fields(track_data)

    return {
        "track_id": track_data.get("id"),
        "track_uri": track_data.get("uri"),
        "track_name": track_data.get("name"),
        "artist_ids": artist_ids,
        "artist_names": artist_names,
        "album_id": album.get("id"),
        "album_name": album.get("name"),
        "release_date": album.get("release_date"),
        "release_date_precision": album.get("release_date_precision"),
        "duration_ms": duration_ms,
        "duration_seconds": duration_seconds,
        "popularity": track_data.get("popularity"),
        "explicit": track_data.get("explicit"),
        "is_playable": track_data.get("is_playable"),
        "restriction_reason": restrictions.get("reason"),
        "linked_from_track_id": linked_from.get("id"),
        "isrc": external_ids.get("isrc"),
        "track_href": track_data.get("href"),
        "track_external_url": external_urls.get("spotify"),
    }


def _resolve_item_payload(item: dict[str, Any]) -> dict[str, Any] | None:
    payload = item.get("item")
    if isinstance(payload, dict):
        return payload
    payload = item.get("track")
    if isinstance(payload, dict):
        return payload
    return None


def build_top_track_rows(top_tracks_by_range: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for time_range, tracks in top_tracks_by_range.items():
        for rank, track in enumerate(tracks, start=1):
            rows.append({"time_range": time_range, "rank": rank, **extract_track_fields(track)})
    return rows


def build_saved_track_rows(saved_track_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in saved_track_items:
        track_payload: dict[str, Any] = {}
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


def build_playlist_rows(playlists: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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


def build_playlist_item_rows(playlist_item_batches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for batch in playlist_item_batches:
        playlist = batch.get("playlist", {}) if isinstance(batch, dict) else {}
        playlist_id = playlist.get("id")
        playlist_name = playlist.get("name")
        items = batch.get("items", []) if isinstance(batch, dict) else []
        for position, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                continue

            payload = _resolve_item_payload(item)
            if not isinstance(payload, dict):
                continue

            item_type = str(payload.get("type", "track")).strip().lower()
            if item_type and item_type != "track":
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
    return rows


def build_recently_played_rows(recently_played_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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
