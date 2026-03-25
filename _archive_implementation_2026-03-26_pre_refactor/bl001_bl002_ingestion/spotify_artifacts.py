from __future__ import annotations

from pathlib import Path
from typing import Dict


EXPORT_ARTIFACT_FILENAMES = {
    "spotify_profile.json": "spotify_profile.json",
    "spotify_top_tracks_by_range.json": "spotify_top_tracks_by_range.json",
    "spotify_top_tracks_flat.csv": "spotify_top_tracks_flat.csv",
    "spotify_saved_tracks.json": "spotify_saved_tracks.json",
    "spotify_saved_tracks_flat.csv": "spotify_saved_tracks_flat.csv",
    "spotify_playlists.json": "spotify_playlists.json",
    "spotify_playlists_flat.csv": "spotify_playlists_flat.csv",
    "spotify_playlist_items_flat.jsonl": "spotify_playlist_items_flat.jsonl",
    "spotify_playlist_items_flat.csv": "spotify_playlist_items_flat.csv",
    "spotify_recently_played.json": "spotify_recently_played.json",
    "spotify_recently_played_flat.csv": "spotify_recently_played_flat.csv",
}

REQUEST_LOG_FILENAME = "spotify_request_log.jsonl"
SUMMARY_FILENAME = "spotify_export_run_summary.json"
RATE_LIMIT_BLOCK_FILENAME = "spotify_rate_limit_block.json"
CACHE_DB_FILENAME = "spotify_resilience_cache.sqlite"


def build_export_artifact_paths(output_dir: Path) -> Dict[str, Path]:
    return {
        name: output_dir / filename
        for name, filename in EXPORT_ARTIFACT_FILENAMES.items()
    }


def build_support_file_paths(output_dir: Path) -> Dict[str, Path]:
    return {
        "request_log": output_dir / REQUEST_LOG_FILENAME,
        "summary": output_dir / SUMMARY_FILENAME,
        "rate_limit_block": output_dir / RATE_LIMIT_BLOCK_FILENAME,
        "cache_db": output_dir / CACHE_DB_FILENAME,
    }