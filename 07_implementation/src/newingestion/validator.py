"""
Validation logic for the new domain-oriented ingestion bundle.

Validation stays focused on integrity and operator-facing diagnostics rather
than shaping the output contract.
"""

from collections import defaultdict
from dataclasses import replace
from typing import Any, Dict, List

from .models import IngestionDomainBundle, NewingestionControls


def _build_duplicate_track_locations(bundle: IngestionDomainBundle) -> Dict[str, List[Dict[str, Any]]]:
    artist_names = {artist.artist_id: artist.name for artist in bundle.artists}
    playlist_names = {playlist.playlist_id: playlist.name for playlist in bundle.playlists}
    primary_artist_by_track_id: Dict[str, str | None] = {}
    for relation in sorted(bundle.track_artist_relations, key=lambda item: (item.track_id, item.artist_order)):
        primary_artist_by_track_id.setdefault(relation.track_id, artist_names.get(relation.artist_id))

    track_names = {track.track_id: track.name for track in bundle.tracks}
    locations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for membership in bundle.top_track_memberships:
        locations[membership.track_id].append(
            {
                "event_type": "top_track",
                "time_range": membership.time_range,
                "position_in_source": membership.rank,
                "track_name": track_names.get(membership.track_id, ""),
                "artist_name": primary_artist_by_track_id.get(membership.track_id),
            }
        )

    for membership in bundle.saved_track_memberships:
        locations[membership.track_id].append(
            {
                "event_type": "saved_track",
                "time_range": None,
                "position_in_source": None,
                "track_name": track_names.get(membership.track_id, ""),
                "artist_name": primary_artist_by_track_id.get(membership.track_id),
                "added_at": membership.added_at.isoformat() if membership.added_at else None,
            }
        )

    for membership in bundle.playlist_track_memberships:
        locations[membership.track_id].append(
            {
                "event_type": "playlist_item",
                "time_range": None,
                "position_in_source": membership.position,
                "playlist_id": membership.playlist_id,
                "playlist_name": playlist_names.get(membership.playlist_id),
                "track_name": track_names.get(membership.track_id, ""),
                "artist_name": primary_artist_by_track_id.get(membership.track_id),
            }
        )

    for event in bundle.recently_played_events:
        locations[event.track_id].append(
            {
                "event_type": "recently_played",
                "time_range": None,
                "position_in_source": None,
                "track_name": track_names.get(event.track_id, ""),
                "artist_name": primary_artist_by_track_id.get(event.track_id),
                "played_at": event.played_at.isoformat() if event.played_at else None,
            }
        )

    return {
        track_id: occurrences
        for track_id, occurrences in locations.items()
        if len(occurrences) > 1
    }



def validate_bundle(bundle: IngestionDomainBundle, controls: NewingestionControls) -> IngestionDomainBundle:
    warnings: List[str] = []

    if not bundle.user_id:
        warnings.append("User ID not found in profile")
    if bundle.user_id and (not bundle.account_country or not bundle.account_product):
        warnings.append("Spotify profile is missing country or product; token may lack user-read-private scope")

    track_ids = {track.track_id for track in bundle.tracks}
    artist_ids = {artist.artist_id for artist in bundle.artists}
    album_ids = {album.album_id for album in bundle.albums}
    playlist_ids = {playlist.playlist_id for playlist in bundle.playlists}

    missing_album_links = sum(1 for track in bundle.tracks if track.album_id and track.album_id not in album_ids)
    missing_artist_links = sum(1 for relation in bundle.track_artist_relations if relation.artist_id not in artist_ids)
    missing_track_links = sum(
        1
        for relation in bundle.top_track_memberships + bundle.saved_track_memberships + bundle.playlist_track_memberships + bundle.recently_played_events
        if relation.track_id not in track_ids
    )
    missing_playlist_links = sum(1 for relation in bundle.playlist_track_memberships if relation.playlist_id not in playlist_ids)

    if missing_album_links > 0:
        warnings.append(f"{missing_album_links} tracks reference missing album entities")
    if missing_artist_links > 0:
        warnings.append(f"{missing_artist_links} track-artist relations reference missing artist entities")
    if missing_track_links > 0:
        warnings.append(f"{missing_track_links} memberships or events reference missing track entities")
    if missing_playlist_links > 0:
        warnings.append(f"{missing_playlist_links} playlist memberships reference missing playlist entities")

    incomplete_tracks = sum(1 for track in bundle.tracks if not track.name)
    tracks_without_artists = sum(1 for track in bundle.tracks if not any(rel.track_id == track.track_id for rel in bundle.track_artist_relations))
    if incomplete_tracks > 0 or tracks_without_artists > 0:
        warnings.append(f"{incomplete_tracks + tracks_without_artists} tracks missing name or artist")

    counts = bundle.counts()
    if controls.include_top_tracks and counts["top_tracks_short"] + counts["top_tracks_medium"] + counts["top_tracks_long"] == 0:
        warnings.append("Top tracks collection is empty but was requested")
    if controls.include_saved_tracks and counts["saved_tracks"] == 0:
        warnings.append("Saved tracks collection is empty but was requested")
    if controls.include_playlists and counts["playlist_items"] == 0:
        warnings.append("Playlist items collection is empty but was requested")
    if controls.include_recently_played and counts["recently_played"] == 0:
        warnings.append("Recently played collection is empty but was requested")

    duplicate_track_locations = _build_duplicate_track_locations(bundle)
    if duplicate_track_locations:
        duplicate_occurrence_count = sum(len(item) for item in duplicate_track_locations.values())
        warnings.append(
            f"Duplicate track IDs detected: {duplicate_occurrence_count} total occurrences, {len(duplicate_track_locations)} duplicated track IDs"
        )

    if controls.fail_on_collection_error and warnings:
        raise RuntimeError(f"Collection validation failed with {len(warnings)} warning(s): {warnings[0]}")

    return replace(bundle, warnings=warnings, duplicate_track_locations=duplicate_track_locations)
