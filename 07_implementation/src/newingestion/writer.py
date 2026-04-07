"""
Output writer for the domain-oriented ingestion bundle.

Canonical outputs are JSON artifacts for entities, memberships, diagnostics, and
run metadata. Optional flat exports are derived compatibility views.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .models import IngestionDomainBundle, NewingestionArtifacts, NewingestionControls


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
    return path


def _bundle_reference_maps(bundle: IngestionDomainBundle) -> Dict[str, Dict[str, Any]]:
    first_artist_by_track_id: Dict[str, str] = {}
    artists_by_id = {artist.artist_id: artist for artist in bundle.artists}
    for relation in sorted(bundle.track_artist_relations, key=lambda item: (item.track_id, item.artist_order)):
        if relation.track_id not in first_artist_by_track_id:
            artist = artists_by_id.get(relation.artist_id)
            first_artist_by_track_id[relation.track_id] = artist.name if artist else ""

    return {
        "tracks": {track.track_id: track for track in bundle.tracks},
        "albums": {album.album_id: album for album in bundle.albums},
        "playlists": {playlist.playlist_id: playlist for playlist in bundle.playlists},
        "first_artist_names": first_artist_by_track_id,
    }


def _write_csv_rows(path: Path, fieldnames: list[str], rows: Iterable[Dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def _write_compatibility_exports(bundle: IngestionDomainBundle, output_dir: Path, run_id: str) -> Dict[str, Path]:
    refs = _bundle_reference_maps(bundle)
    fieldnames = [
        "track_id",
        "track_name",
        "artist_name",
        "album_id",
        "album_name",
        "duration_ms",
        "explicit",
        "isrc",
        "popularity",
        "time_range",
        "rank",
        "added_at",
        "playlist_id",
        "playlist_name",
        "position",
        "played_at",
        "context_type",
        "context_uri",
        "is_local",
    ]

    exports: Dict[str, Path] = {}

    for time_range, export_name in (("short_term", "top_tracks_short"), ("medium_term", "top_tracks_medium"), ("long_term", "top_tracks_long")):
        memberships = [item for item in bundle.top_track_memberships if item.time_range == time_range]
        if not memberships:
            continue
        rows = []
        for membership in memberships:
            track = refs["tracks"].get(membership.track_id)
            album = refs["albums"].get(track.album_id) if track and track.album_id else None
            rows.append(
                {
                    "track_id": membership.track_id,
                    "track_name": track.name if track else "",
                    "artist_name": refs["first_artist_names"].get(membership.track_id, ""),
                    "album_id": track.album_id if track else None,
                    "album_name": album.name if album else None,
                    "duration_ms": track.duration_ms if track else None,
                    "explicit": track.explicit if track else None,
                    "isrc": track.isrc if track else None,
                    "popularity": track.popularity if track else None,
                    "time_range": membership.time_range,
                    "rank": membership.rank,
                    "is_local": track.is_local if track else None,
                }
            )
        exports[export_name] = _write_csv_rows(output_dir / f"{run_id}_{export_name}.csv", fieldnames, rows)

    if bundle.saved_track_memberships:
        rows = []
        for membership in bundle.saved_track_memberships:
            track = refs["tracks"].get(membership.track_id)
            album = refs["albums"].get(track.album_id) if track and track.album_id else None
            rows.append(
                {
                    "track_id": membership.track_id,
                    "track_name": track.name if track else "",
                    "artist_name": refs["first_artist_names"].get(membership.track_id, ""),
                    "album_id": track.album_id if track else None,
                    "album_name": album.name if album else None,
                    "duration_ms": track.duration_ms if track else None,
                    "explicit": track.explicit if track else None,
                    "isrc": track.isrc if track else None,
                    "popularity": track.popularity if track else None,
                    "added_at": membership.added_at.isoformat() if membership.added_at else None,
                    "is_local": track.is_local if track else None,
                }
            )
        exports["saved_tracks"] = _write_csv_rows(output_dir / f"{run_id}_saved_tracks.csv", fieldnames, rows)

    if bundle.playlist_track_memberships:
        rows = []
        for membership in bundle.playlist_track_memberships:
            track = refs["tracks"].get(membership.track_id)
            album = refs["albums"].get(track.album_id) if track and track.album_id else None
            playlist = refs["playlists"].get(membership.playlist_id)
            rows.append(
                {
                    "track_id": membership.track_id,
                    "track_name": track.name if track else "",
                    "artist_name": refs["first_artist_names"].get(membership.track_id, ""),
                    "album_id": track.album_id if track else None,
                    "album_name": album.name if album else None,
                    "duration_ms": track.duration_ms if track else None,
                    "explicit": track.explicit if track else None,
                    "isrc": track.isrc if track else None,
                    "popularity": track.popularity if track else None,
                    "playlist_id": membership.playlist_id,
                    "playlist_name": playlist.name if playlist else None,
                    "position": membership.position,
                    "added_at": membership.added_at.isoformat() if membership.added_at else None,
                    "is_local": membership.is_local,
                }
            )
        exports["playlist_items"] = _write_csv_rows(output_dir / f"{run_id}_playlist_items.csv", fieldnames, rows)

    if bundle.recently_played_events:
        rows = []
        for event in bundle.recently_played_events:
            track = refs["tracks"].get(event.track_id)
            album = refs["albums"].get(track.album_id) if track and track.album_id else None
            rows.append(
                {
                    "track_id": event.track_id,
                    "track_name": track.name if track else "",
                    "artist_name": refs["first_artist_names"].get(event.track_id, ""),
                    "album_id": track.album_id if track else None,
                    "album_name": album.name if album else None,
                    "duration_ms": track.duration_ms if track else None,
                    "explicit": track.explicit if track else None,
                    "isrc": track.isrc if track else None,
                    "popularity": track.popularity if track else None,
                    "played_at": event.played_at.isoformat() if event.played_at else None,
                    "context_type": event.context_type,
                    "context_uri": event.context_uri,
                    "is_local": track.is_local if track else None,
                }
            )
        exports["recently_played"] = _write_csv_rows(output_dir / f"{run_id}_recently_played.csv", fieldnames, rows)

    return exports


def write_outputs(
    bundle: IngestionDomainBundle,
    output_dir: Path,
    run_id: str,
    controls: NewingestionControls,
) -> NewingestionArtifacts:
    output_dir.mkdir(parents=True, exist_ok=True)

    artifact_paths: Dict[str, Path] = {}
    compatibility_export_paths: Dict[str, Path] = {}

    artifact_paths["tracks"] = _write_json(output_dir / f"{run_id}_tracks.json", [item.to_dict() for item in bundle.tracks])
    artifact_paths["artists"] = _write_json(output_dir / f"{run_id}_artists.json", [item.to_dict() for item in bundle.artists])
    artifact_paths["albums"] = _write_json(output_dir / f"{run_id}_albums.json", [item.to_dict() for item in bundle.albums])
    artifact_paths["playlists"] = _write_json(output_dir / f"{run_id}_playlists.json", [item.to_dict() for item in bundle.playlists])
    artifact_paths["account_profile"] = _write_json(
        output_dir / f"{run_id}_account_profile.json",
        bundle.account_profile.to_dict() if bundle.account_profile else None,
    )
    artifact_paths["track_artist_relations"] = _write_json(
        output_dir / f"{run_id}_track_artist_relations.json",
        [item.to_dict() for item in bundle.track_artist_relations],
    )
    artifact_paths["top_track_memberships"] = _write_json(
        output_dir / f"{run_id}_top_track_memberships.json",
        [item.to_dict() for item in bundle.top_track_memberships],
    )
    artifact_paths["saved_track_memberships"] = _write_json(
        output_dir / f"{run_id}_saved_track_memberships.json",
        [item.to_dict() for item in bundle.saved_track_memberships],
    )
    artifact_paths["playlist_track_memberships"] = _write_json(
        output_dir / f"{run_id}_playlist_track_memberships.json",
        [item.to_dict() for item in bundle.playlist_track_memberships],
    )
    artifact_paths["recently_played_events"] = _write_json(
        output_dir / f"{run_id}_recently_played_events.json",
        [item.to_dict() for item in bundle.recently_played_events],
    )

    diagnostics_payload = {
        "warnings": bundle.warnings,
        "selection_flags": bundle.selection_flags,
        "counts": bundle.counts(),
        "duplicate_track_locations": bundle.duplicate_track_locations,
    }
    artifact_paths["diagnostics"] = _write_json(output_dir / f"{run_id}_diagnostics.json", diagnostics_payload)

    if bundle.duplicate_track_locations:
        artifact_paths["duplicate_track_locations"] = _write_json(
            output_dir / f"{run_id}_duplicate_track_locations.json",
            bundle.duplicate_track_locations,
        )

    if controls.include_raw_response_payloads:
        artifact_paths["domain_bundle"] = _write_json(output_dir / f"{run_id}_domain_bundle.json", bundle.to_dict())

    if controls.emit_flat_csvs:
        compatibility_export_paths = _write_compatibility_exports(bundle, output_dir, run_id)

    manifest_payload = {
        "run_id": run_id,
        "generated_at_utc": bundle.generated_at_utc.isoformat(),
        "source_type": bundle.source_type,
        "user_id": bundle.user_id,
        "account_country": bundle.account_country,
        "account_product": bundle.account_product,
        "counts": bundle.counts(),
        "selection_flags": bundle.selection_flags,
        "warnings": bundle.warnings,
        "artifact_inventory": {name: str(path) for name, path in artifact_paths.items()},
        "compatibility_exports": {name: str(path) for name, path in compatibility_export_paths.items()},
    }
    manifest_artifact_path = _write_json(output_dir / f"{run_id}_run_manifest.json", manifest_payload)

    return NewingestionArtifacts(
        run_id=run_id,
        generated_at_utc=bundle.generated_at_utc,
        source_type=controls.source_type,
        manifest_artifact_path=manifest_artifact_path,
        artifact_paths=artifact_paths,
        compatibility_export_paths=compatibility_export_paths,
        counts=bundle.counts(),
        warnings=bundle.warnings,
    )
