# Schema Notes

## BL-001 Ingestion Schema (MVP Draft)

### Scope
- One practical ingestion path for exported listening history.
- Normalized output supports downstream ISRC-first alignment and deterministic profiling.

### Input File Assumption (Raw)
- Format: CSV
- One row per listening event.
- Raw columns expected from source export:
	- `track_name`
	- `artist_name`
	- `album_name` (optional)
	- `isrc` (optional but preferred)
	- `played_at` (timestamp)
	- `ms_played` (milliseconds)
	- `platform` (optional)

### Normalized Event Schema (Output)
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event_id` | string | yes | Deterministic row identifier (for traceability). |
| `track_name` | string | yes | Raw track title after trim/normalization. |
| `artist_name` | string | yes | Primary artist string after trim/normalization. |
| `album_name` | string | no | Album title when available. |
| `isrc` | string | no | Uppercased ISRC if present and valid pattern. |
| `played_at` | string | yes | ISO-8601 timestamp in UTC when possible. |
| `ms_played` | integer | yes | Playback duration in milliseconds. |
| `source_platform` | string | yes | Ingestion source identifier (for provenance). |
| `ingest_run_id` | string | yes | Run-level ID linking all rows in one ingest. |
| `row_quality_flag` | string | yes | `ok`, `missing_isrc`, `missing_core_field`, `invalid_timestamp`, etc. |

### Validation Rules (MVP)
- Hard fail row if any core field is missing: `track_name`, `artist_name`, `played_at`, `ms_played`.
- Soft warning if `isrc` is missing; row remains usable for fallback matching.
- Convert `played_at` to ISO-8601 UTC where parseable; otherwise mark `invalid_timestamp`.
- Require `ms_played >= 0`; negative values are invalid.

### Example Mapping
| Raw Input | Normalized Output |
| --- | --- |
| `track_name=Blinding Lights` | `track_name=blinding lights` (normalized casing strategy to be finalized) |
| `artist_name=The Weeknd` | `artist_name=the weeknd` |
| `isrc=USUG11904298` | `isrc=USUG11904298` |
| `played_at=2025-11-21 23:16:02` | `played_at=2025-11-21T23:16:02Z` |
| `ms_played=184000` | `ms_played=184000` |

### Open Decisions
- Confirm canonical text normalization rule (lowercase vs preserve display form + normalized shadow columns).
- Confirm exact `source_platform` value taxonomy.
- Confirm whether partial listens below threshold are excluded at ingestion or later profiling stage.

## BL-003 Alignment Output Schema (MVP Draft)

### Inputs
- Normalized event JSONL from ingestion stage.
- Candidate corpus CSV containing at least: `m4a_track_id`, `isrc`, `track_name`, `artist_name`.

### Matching Policy
- Primary: ISRC exact match (`event.isrc` -> `candidate.isrc`).
- Fallback: normalized exact match on `(track_name, artist_name)`.
- Default behavior: skip hard-invalid rows flagged by ingestion (`missing_core_field`, `invalid_timestamp`, `invalid_ms_played`).

### Alignment Output Fields
| Field | Type | Description |
| --- | --- | --- |
| `event_id` | string | Original ingestion event identifier. |
| `ingest_run_id` | string | Run-level provenance link to ingestion output. |
| `m4a_track_id` | string | Candidate corpus track identifier when matched. |
| `matched_isrc` | string | Matched ISRC value when available. |
| `match_method` | string | `isrc`, `metadata`, or `none`. |
| `track_name` | string | Normalized track name used in matching. |
| `artist_name` | string | Normalized artist name used in matching. |
| `row_quality_flag` | string | Ingestion quality flag passed through for traceability. |

### Alignment Summary Metrics
- `rows_total`
- `rows_considered`
- `rows_skipped_invalid`
- `matched_total`
- `matched_isrc`
- `matched_fallback`
- `unmatched`
- `match_rate`
- `alignment_output_hash`

