# BL-001 Spotify Input Output Mapping

## Purpose
Provide a concrete mapping example from Spotify Extended Streaming History CSV fields into the normalized ingestion schema.

## Raw Example Row (Spotify)
| ts | platform | master_metadata_track_name | master_metadata_album_artist_name | master_metadata_album_album_name | ms_played | spotify_track_uri | isrc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-11-21T23:16:02Z | Spotify Android | Blinding Lights | The Weeknd | After Hours | 184000 | spotify:track:0VjIjW4GlUZAMYd2vXMi3b | USUG11904298 |

## Normalized Example Row
| event_id | track_name | artist_name | album_name | isrc | played_at | ms_played | source_platform | ingest_run_id | row_quality_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EVT-000001-EXAMPLE1234 | blinding lights | the weeknd | after hours | USUG11904298 | 2025-11-21T23:16:02Z | 184000 | spotify android | BL002-INGEST-EXAMPLE | ok |

## Mapping Rules Snapshot
- master_metadata_track_name -> track_name
- master_metadata_album_artist_name -> artist_name
- master_metadata_album_album_name -> album_name
- ts -> played_at
- ms_played -> ms_played
- platform -> source_platform (fallback default: spotify_export_csv)
- isrc -> isrc (optional; keep row with missing_isrc when absent)

## Notes
- If track or artist is missing, row_quality_flag becomes missing_core_field.
- If ts is malformed, row_quality_flag becomes invalid_timestamp.
- If ms_played is negative or non-numeric, row_quality_flag becomes invalid_ms_played.
