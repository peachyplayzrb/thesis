from __future__ import annotations

from typing import Any, Dict, List


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


def build_top_track_rows(top_tracks_by_range: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for time_range, tracks in top_tracks_by_range.items():
        for rank, track in enumerate(tracks, start=1):
            rows.append({"time_range": time_range, "rank": rank, **extract_track_fields(track)})
    return rows


def build_saved_track_rows(saved_track_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in saved_track_items:
        rows.append(
            {
                "added_at": item.get("added_at") if isinstance(item, dict) else None,
                **extract_track_fields(item.get("track", {}) if isinstance(item, dict) else {}),
            }
        )
    return rows


def build_playlist_rows(playlists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for playlist in playlists:
        owner = playlist.get("owner", {}) if isinstance(playlist, dict) else {}
        rows.append(
            {
                "playlist_id": playlist.get("id"),
                "playlist_name": playlist.get("name"),
                "owner_id": owner.get("id") if isinstance(owner, dict) else None,
                "collaborative": playlist.get("collaborative"),
                "public": playlist.get("public"),
                "tracks_total": (playlist.get("tracks", {}) or {}).get("total"),
                "snapshot_id": playlist.get("snapshot_id"),
                "uri": playlist.get("uri"),
            }
        )
    return rows


def build_playlist_item_rows(playlist_item_batches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for batch in playlist_item_batches:
        playlist = batch.get("playlist", {}) if isinstance(batch, dict) else {}
        playlist_id = playlist.get("id")
        playlist_name = playlist.get("name")
        items = batch.get("items", []) if isinstance(batch, dict) else []
        for position, item in enumerate(items, start=1):
            track = item.get("track") if isinstance(item, dict) else None
            if not isinstance(track, dict):
                track = {}
            rows.append(
                {
                    "playlist_id": playlist_id,
                    "playlist_name": playlist_name,
                    "playlist_position": position,
                    "added_at": item.get("added_at") if isinstance(item, dict) else None,
                    "added_by": (item.get("added_by") or {}).get("id") if isinstance(item, dict) else None,
                    "is_local": item.get("is_local") if isinstance(item, dict) else None,
                    **extract_track_fields(track),
                }
            )
    return rows


def build_recently_played_rows(recently_played_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in recently_played_items:
        track = item.get("track") if isinstance(item, dict) else None
        if not isinstance(track, dict):
            track = {}
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


