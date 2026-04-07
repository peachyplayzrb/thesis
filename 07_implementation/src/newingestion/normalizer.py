"""
Normalization logic: converts provider-specific raw data to canonical domain models.

The normalizer extracts stable Spotify entities and explicit relationships so
 downstream stages work against a clean ingestion contract rather than flattened
 collection rows.
"""

from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from .models import (
    IngestionDomainBundle,
    NewingestionControls,
    PlaylistTrackMembership,
    RecentlyPlayedEvent,
    SavedTrackMembership,
    SpotifyAccountProfile,
    SpotifyAlbum,
    SpotifyArtist,
    SpotifyPlaylist,
    SpotifyTrack,
    TopTrackMembership,
    TrackArtistRelation,
)


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _fallback_id(prefix: str, value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    return f"{prefix}:name:{text}"


def _extract_track_object(raw_track: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(raw_track, dict):
        return None
    track_obj = raw_track.get("track") if "track" in raw_track else raw_track
    return track_obj if isinstance(track_obj, dict) else None


def normalize_spotify_track(raw_track: Dict[str, Any]) -> Optional[SpotifyTrack]:
    track_obj = _extract_track_object(raw_track)
    if not track_obj:
        return None

    track_id = track_obj.get("id")
    if not track_id:
        return None

    external_urls = track_obj.get("external_urls") if isinstance(track_obj.get("external_urls"), dict) else {}
    external_ids = track_obj.get("external_ids") if isinstance(track_obj.get("external_ids"), dict) else {}
    album = track_obj.get("album") if isinstance(track_obj.get("album"), dict) else {}

    return SpotifyTrack(
        track_id=track_id,
        name=track_obj.get("name", ""),
        album_id=album.get("id") or _fallback_id("spotify:album", album.get("name")),
        duration_ms=track_obj.get("duration_ms"),
        explicit=bool(track_obj.get("explicit", False)),
        isrc=external_ids.get("isrc"),
        popularity=track_obj.get("popularity"),
        is_local=bool(track_obj.get("is_local", False)),
        uri=track_obj.get("uri"),
        external_url=external_urls.get("spotify"),
    )


def _extract_album(raw_track: Dict[str, Any]) -> Optional[SpotifyAlbum]:
    track_obj = _extract_track_object(raw_track)
    if not track_obj:
        return None
    album = track_obj.get("album")
    if not isinstance(album, dict):
        return None

    album_id = album.get("id") or _fallback_id("spotify:album", album.get("name"))
    if not album_id:
        return None

    external_urls = album.get("external_urls") if isinstance(album.get("external_urls"), dict) else {}
    return SpotifyAlbum(
        album_id=album_id,
        name=album.get("name", ""),
        album_type=album.get("album_type"),
        release_date=album.get("release_date"),
        release_date_precision=album.get("release_date_precision"),
        total_tracks=album.get("total_tracks"),
        uri=album.get("uri"),
        external_url=external_urls.get("spotify"),
    )


def _extract_artists_and_relations(raw_track: Dict[str, Any], track_id: str) -> tuple[List[SpotifyArtist], List[TrackArtistRelation]]:
    track_obj = _extract_track_object(raw_track)
    if not track_obj:
        return [], []

    artists_payload = track_obj.get("artists")
    if not isinstance(artists_payload, list):
        return [], []

    artists: List[SpotifyArtist] = []
    relations: List[TrackArtistRelation] = []
    for index, artist in enumerate(artists_payload):
        if not isinstance(artist, dict):
            continue
        artist_id = artist.get("id") or _fallback_id("spotify:artist", artist.get("name"))
        if not artist_id:
            continue
        external_urls = artist.get("external_urls") if isinstance(artist.get("external_urls"), dict) else {}
        artists.append(
            SpotifyArtist(
                artist_id=artist_id,
                name=artist.get("name", ""),
                uri=artist.get("uri"),
                external_url=external_urls.get("spotify"),
            )
        )
        relations.append(TrackArtistRelation(track_id=track_id, artist_id=artist_id, artist_order=index))

    return artists, relations


def _extract_playlist(raw_playlist: Dict[str, Any]) -> Optional[SpotifyPlaylist]:
    if not isinstance(raw_playlist, dict):
        return None
    playlist_id = raw_playlist.get("id") or raw_playlist.get("playlist_id")
    if not playlist_id:
        return None
    owner = raw_playlist.get("owner") if isinstance(raw_playlist.get("owner"), dict) else {}
    external_urls = raw_playlist.get("external_urls") if isinstance(raw_playlist.get("external_urls"), dict) else {}
    tracks = raw_playlist.get("tracks") if isinstance(raw_playlist.get("tracks"), dict) else {}
    return SpotifyPlaylist(
        playlist_id=playlist_id,
        name=raw_playlist.get("name", ""),
        owner_id=owner.get("id") or raw_playlist.get("playlist_owner_id"),
        owner_name=owner.get("display_name") or raw_playlist.get("playlist_owner_name"),
        description=raw_playlist.get("description"),
        snapshot_id=raw_playlist.get("snapshot_id") or raw_playlist.get("playlist_snapshot_id"),
        collaborative=bool(raw_playlist.get("collaborative", False)),
        public=raw_playlist.get("public"),
        tracks_total=tracks.get("total") or raw_playlist.get("playlist_tracks_total"),
        uri=raw_playlist.get("uri"),
        external_url=external_urls.get("spotify"),
    )


def _extract_account_profile(raw_profile: Any) -> Optional[SpotifyAccountProfile]:
    if not isinstance(raw_profile, dict):
        return None
    user_id = raw_profile.get("id")
    if not user_id:
        return None
    external_urls = raw_profile.get("external_urls") if isinstance(raw_profile.get("external_urls"), dict) else {}
    followers = raw_profile.get("followers") if isinstance(raw_profile.get("followers"), dict) else {}
    return SpotifyAccountProfile(
        user_id=user_id,
        country=raw_profile.get("country"),
        product=raw_profile.get("product"),
        display_name=raw_profile.get("display_name"),
        email=raw_profile.get("email"),
        uri=raw_profile.get("uri"),
        external_url=external_urls.get("spotify"),
        followers_total=followers.get("total"),
    )


def normalize_raw_data_to_bundle(
    raw_data: Dict[str, Any],
    controls: NewingestionControls,
    run_id: str,
) -> IngestionDomainBundle:
    tracks_by_id: Dict[str, SpotifyTrack] = {}
    artists_by_id: Dict[str, SpotifyArtist] = {}
    albums_by_id: Dict[str, SpotifyAlbum] = {}
    playlists_by_id: Dict[str, SpotifyPlaylist] = {}
    relation_keys: set[tuple[str, str, int]] = set()
    track_artist_relations: List[TrackArtistRelation] = []
    top_track_memberships: List[TopTrackMembership] = []
    saved_track_memberships: List[SavedTrackMembership] = []
    playlist_track_memberships: List[PlaylistTrackMembership] = []
    recently_played_events: List[RecentlyPlayedEvent] = []

    def ingest_track(raw_track: Dict[str, Any]) -> Optional[str]:
        track = normalize_spotify_track(raw_track)
        if not track:
            return None
        tracks_by_id.setdefault(track.track_id, track)

        album = _extract_album(raw_track)
        if album:
            albums_by_id.setdefault(album.album_id, album)

        artists, relations = _extract_artists_and_relations(raw_track, track.track_id)
        for artist in artists:
            artists_by_id.setdefault(artist.artist_id, artist)
        for relation in relations:
            key = (relation.track_id, relation.artist_id, relation.artist_order)
            if key not in relation_keys:
                relation_keys.add(key)
                track_artist_relations.append(relation)

        return track.track_id

    if controls.include_playlists:
        for raw_playlist in raw_data.get("playlists", []):
            playlist = _extract_playlist(raw_playlist)
            if playlist:
                playlists_by_id.setdefault(playlist.playlist_id, playlist)

    if controls.include_top_tracks:
        for time_range, key in (("short_term", "top_tracks_short"), ("medium_term", "top_tracks_medium"), ("long_term", "top_tracks_long")):
            for index, raw_track in enumerate(raw_data.get(key, [])):
                track_id = ingest_track(raw_track)
                if not track_id:
                    continue
                top_track_memberships.append(TopTrackMembership(track_id=track_id, time_range=time_range, rank=index))
                if controls.max_top_tracks > 0 and index + 1 >= controls.max_top_tracks:
                    break

    if controls.include_saved_tracks:
        for index, raw_track in enumerate(raw_data.get("saved_tracks", [])):
            track_id = ingest_track(raw_track)
            if not track_id:
                continue
            added_at = _parse_datetime(raw_track.get("added_at") if isinstance(raw_track, dict) else None)
            saved_track_memberships.append(SavedTrackMembership(track_id=track_id, added_at=added_at))
            if controls.max_saved_tracks > 0 and index + 1 >= controls.max_saved_tracks:
                break

    if controls.include_playlists:
        for index, raw_item in enumerate(raw_data.get("playlist_items", [])):
            track_id = ingest_track(raw_item)
            if not track_id or not isinstance(raw_item, dict):
                continue
            playlist_id = raw_item.get("playlist_id")
            if not playlist_id:
                continue
            playlist = _extract_playlist(raw_item)
            if playlist:
                playlists_by_id.setdefault(playlist.playlist_id, playlist)
            added_by = raw_item.get("added_by") if isinstance(raw_item.get("added_by"), dict) else {}
            track_payload = raw_item.get("track") if isinstance(raw_item.get("track"), dict) else {}
            playlist_track_memberships.append(
                PlaylistTrackMembership(
                    playlist_id=playlist_id,
                    track_id=track_id,
                    position=raw_item.get("playlist_position", index),
                    added_at=_parse_datetime(raw_item.get("added_at")),
                    added_by_id=added_by.get("id"),
                    added_by_uri=added_by.get("uri"),
                    is_local=bool(raw_item.get("is_local", False) or track_payload.get("is_local", False)),
                )
            )
            if controls.max_playlist_items > 0 and len(playlist_track_memberships) >= controls.max_playlist_items:
                break

    if controls.include_recently_played:
        for index, raw_item in enumerate(raw_data.get("recently_played", [])):
            track_id = ingest_track(raw_item)
            if not track_id or not isinstance(raw_item, dict):
                continue
            context = raw_item.get("context") if isinstance(raw_item.get("context"), dict) else {}
            recently_played_events.append(
                RecentlyPlayedEvent(
                    track_id=track_id,
                    played_at=_parse_datetime(raw_item.get("played_at")),
                    context_type=context.get("type"),
                    context_uri=context.get("uri"),
                )
            )
            if controls.max_recently_played > 0 and index + 1 >= controls.max_recently_played:
                break

    account_profile = _extract_account_profile(raw_data.get("user_profile") if isinstance(raw_data, dict) else None)
    selection_flags = {
        "include_top_tracks": controls.include_top_tracks,
        "include_saved_tracks": controls.include_saved_tracks,
        "include_playlists": controls.include_playlists,
        "include_recently_played": controls.include_recently_played,
    }

    return IngestionDomainBundle(
        run_id=run_id,
        generated_at_utc=datetime.now(UTC),
        source_type=controls.source_type,
        account_profile=account_profile,
        tracks=list(tracks_by_id.values()),
        artists=list(artists_by_id.values()),
        albums=list(albums_by_id.values()),
        playlists=list(playlists_by_id.values()),
        track_artist_relations=track_artist_relations,
        top_track_memberships=top_track_memberships,
        saved_track_memberships=saved_track_memberships,
        playlist_track_memberships=playlist_track_memberships,
        recently_played_events=recently_played_events,
        selection_flags=selection_flags,
    )
