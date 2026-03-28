# Spotify Export Schema Reference

This document defines the current exported CSV/JSON schema used by the Spotify ingestion pipeline.

## Scope

Output root:
- `src/ingestion/outputs/spotify_api_export/`

Primary run metadata:
- `spotify_export_run_summary.json`
- `spotify_request_log.jsonl`

Support artifacts:
- `spotify_rate_limit_block.json` (written when a run is blocked by API rate limits)
- `spotify_resilience_cache.sqlite` (SQLite cache store when resilience caching is enabled)

## Dataset Files

### `spotify_top_tracks_flat.csv`
Columns:
- `time_range`
- `rank`
- `track_id`
- `track_uri`
- `track_name`
- `artist_ids`
- `artist_names`
- `album_id`
- `album_name`
- `release_date`
- `release_date_precision`
- `duration_ms`
- `duration_seconds`
- `popularity`
- `explicit`
- `is_playable`
- `restriction_reason`
- `linked_from_track_id`
- `isrc`
- `track_href`
- `track_external_url`

### `spotify_saved_tracks_flat.csv`
Columns:
- `added_at`
- `track_id`
- `track_uri`
- `track_name`
- `artist_ids`
- `artist_names`
- `album_id`
- `album_name`
- `release_date`
- `release_date_precision`
- `duration_ms`
- `duration_seconds`
- `popularity`
- `explicit`
- `is_playable`
- `restriction_reason`
- `linked_from_track_id`
- `isrc`
- `track_href`
- `track_external_url`

### `spotify_playlists_flat.csv`
Columns:
- `playlist_id`
- `playlist_name`
- `owner_id`
- `collaborative`
- `public`
- `tracks_total`
- `snapshot_id`
- `uri`

### `spotify_playlist_items_flat.csv`
Columns:
- `playlist_id`
- `playlist_name`
- `playlist_position`
- `added_at`
- `added_by`
- `is_local`
- `track_id`
- `track_uri`
- `track_name`
- `artist_ids`
- `artist_names`
- `album_id`
- `album_name`
- `release_date`
- `release_date_precision`
- `duration_ms`
- `duration_seconds`
- `popularity`
- `explicit`
- `is_playable`
- `restriction_reason`
- `linked_from_track_id`
- `isrc`
- `track_href`
- `track_external_url`

### `spotify_recently_played_flat.csv`
Columns:
- `played_at`
- `context_type`
- `context_uri`
- `track_id`
- `track_uri`
- `track_name`
- `artist_ids`
- `artist_names`
- `album_id`
- `album_name`
- `release_date`
- `release_date_precision`
- `duration_ms`
- `duration_seconds`
- `popularity`
- `explicit`
- `is_playable`
- `restriction_reason`
- `linked_from_track_id`
- `isrc`
- `track_href`
- `track_external_url`

## Field Notes

- `track_id`: stable Spotify track identifier.
- `isrc`: best cross-source key for high-confidence record linkage.
- `release_date` + `release_date_precision`: keep temporal values with precision context.
- `duration_seconds`: convenience numeric derived from `duration_ms`.
- `restriction_reason`: market/product/explicit restrictions when present.
- `linked_from_track_id`: original track id when relinking occurs.

## Backward Compatibility

- New columns are append-only additions to track-level datasets.
- Existing core columns (`track_id`, `track_name`, `artist_names`, `isrc`) are unchanged.
