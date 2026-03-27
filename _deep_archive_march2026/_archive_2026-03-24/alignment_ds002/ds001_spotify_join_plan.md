# DS-001 to Spotify Join Plan

## Objective

Define the deterministic join strategy from Spotify user data to DS-001 candidate tracks.

## Inputs

DS-001 prepared table:
- 07_implementation/implementation_notes/bl000_data_layer/outputs/ds001_working_candidate_dataset.csv

Spotify user exports (any available subset):
- 07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_top_tracks_flat.csv
- 07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_saved_tracks_flat.csv
- 07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_playlist_items_flat.csv
- 07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_recently_played_flat.csv

## Primary Join Strategy

1. Use Spotify track identifier exact match:
   - spotify_export.track_id == ds001.spotify_id

2. Keep source provenance fields in joined rows:
   - source_type (top_tracks, saved_tracks, playlist_items, recently_played)
   - source_timestamp (played_at or added_at where available)
   - source_rank (for top tracks)

This is the default path for DS-001 because spotify_id exists in the corpus.

## Secondary Confidence Strategy

When available, carry Spotify isrc as a confidence signal only:
- spotify_export.isrc

Do not treat ISRC as required because DS-001 base table has no corpus-side ISRC column.

## Fallback Strategy

If track_id is missing in a Spotify source row:

1. Try normalized metadata fallback using:
   - track_name
   - first artist name
   - duration proximity (if available)

2. Mark match_method as metadata_fallback and include confidence notes.

## Suggested Output Fields

- user_source_id
- source_type
- source_timestamp
- source_rank
- spotify_track_id
- spotify_isrc
- ds001_id
- ds001_spotify_id
- artist
- song
- match_method
- match_confidence

## Runtime Notes

- Prefer exact ID match and avoid fuzzy logic whenever possible.
- Keep unmatched Spotify rows in an audit file for traceability.
- Keep join metrics in a summary report:
  - rows_total
  - matched_by_spotify_id
  - matched_by_metadata
  - unmatched
  - match_rate

## Implementation Command

Run from repo root:

```powershell
".venv/Scripts/python.exe" "07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py"
```

## Full Logging Artifacts

The implementation writes both matched and unmatched evidence for complete auditability:

- `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_summary.json`
- `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_trace.csv`
- `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_unmatched.csv`
- `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_matched_events.jsonl`
- `07_implementation/implementation_notes/bl003_alignment/outputs/bl003_ds001_spotify_seed_table.csv`

Logging behavior:

- Trace includes one row per input Spotify event with source metadata, match status, method, and reason.
- Unmatched rows are duplicated into a dedicated unmatched file for quick diagnosis.
- Summary includes input hashes, source file presence/row counts, full match breakdown, and output hashes.
