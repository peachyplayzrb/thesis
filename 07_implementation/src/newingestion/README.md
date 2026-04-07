# newingestion: Standalone Data Ingestion Stage

A self-contained Python package implementing the stage-class pattern for data extraction, normalization, validation, and emission of ingestion artifacts.

## Overview

**newingestion** is a standalone stage following the architectural pattern of BL-003 through BL-007. It operates independently without requiring orchestration by BL-013, making it suitable for:

- Direct CLI execution
- Integration into orchestration as a future iteration
- Standalone batch operations
- Testing and validation of ingestion workflows

## Architecture

The package follows a thin coordinator + explicit helpers pattern:

```
IngestionStage (coordinator)
├── resolve_paths()              → NewingestionPaths
├── resolve_runtime_controls()   → NewingestionControls
├── preflight()                  → credential verification, setup
├── collect()                    → raw data from source adapter
├── normalize()                  → IngestionDomainBundle (canonical domain model)
├── validate()                   → enhanced bundle with quality checks & warnings
├── write_outputs()              → NewingestionArtifacts (manifest + canonical JSON + CSV exports)
└── run()                        → orchestrates all steps
```

### Key Components

- **models.py**: Frozen dataclasses for domain entities (SpotifyTrack, SpotifyArtist, etc.), relationships, bundle, and artifacts
- **runtime_controls.py**: Payload-first control resolution (BL_STAGE_CONFIG_JSON > run-config > env > defaults)
- **source_adapters.py**: Pluggable adapter interface + Spotify API and CSV history implementations
- **normalizer.py**: Converts provider-specific raw data to IngestionDomainBundle with deduplication and relationship preservation
- **validator.py**: Entity reference integrity checks, duplicate detection, and quality warnings
- **writer.py**: Emits canonical JSON artifacts (tracks, artists, albums, playlists, memberships, events), run manifest, and derived CSV exports
- **stage.py**: IngestionStage coordinator class
- **main.py**: Thin CLI entrypoint

## Usage

### Command-Line Execution

```bash
python -m newingestion.main \
  --root /path/to/newingestion \
  --run-config /path/to/run-config.json \
  --run-id MY-RUN-001 \
  --verbose
```

**Arguments:**
- `--root` (required): Root directory for newingestion (contains outputs/)
- `--run-config` (optional): Path to run-config JSON/YAML with control overrides
- `--run-id` (optional): Explicit run ID (auto-generated if omitted)
- `--verbose` (optional): Enable verbose logging

### Output

The entrypoint prints a JSON summary to stdout:

```json
{
  "run_id": "INGESTION-20260401T120000-ABCDEF",
  "source_type": "spotify_api",
  "counts": {
    "top_tracks_short": 50,
    "top_tracks_medium": 50,
    "top_tracks_long": 50,
    "saved_tracks": 176,
    "playlist_items": 31,
    "recently_played": 0,
    "total_unique_tracks": 287
  },
  "summary_artifact": "/path/to/newingestion/outputs/INGESTION-..._summary.json",
  "warnings": []
}
```

### Programmatic Usage

```python
from pathlib import Path
from newingestion.stage import IngestionStage

stage = IngestionStage(
    root=Path("/path/to/newingestion"),
    run_config_path=Path("/path/to/run-config.json"),
    run_id="MY-RUN-001",
)

artifacts = stage.run()
print(f"Manifest: {artifacts.manifest_artifact_path}")
print(f"Canonical artifacts: {artifacts.artifact_paths}")
print(f"CSV exports: {artifacts.compatibility_export_paths}")
```

## Spotify Setup (Standalone)

Set one of the following auth modes before running with `source_type: spotify_api`:

1. Direct access token mode:
- `BL_SPOTIFY_AUTH_TOKEN=<spotify_access_token>`

2. Refresh token mode (adapter refreshes access token automatically):
- `BL_SPOTIFY_REFRESH_TOKEN=<spotify_refresh_token>`
- `BL_SPOTIFY_CLIENT_ID=<spotify_client_id>`
- `BL_SPOTIFY_CLIENT_SECRET=<spotify_client_secret>`

Optional scope declaration (recommended):
- `BL_SPOTIFY_TOKEN_SCOPES="user-top-read user-library-read playlist-read-private playlist-read-collaborative user-read-recently-played"`

When `BL_SPOTIFY_TOKEN_SCOPES` is set, the adapter validates required scopes for enabled collections.

### Interactive OAuth (Redirect-URI Flow)

If you don't have a pre-existing access token or refresh token, use interactive OAuth to authorize the stage:

```bash
python -m newingestion.main \
  --root "07_implementation/src/newingestion" \
  --run-config "07_implementation/newingestion_smoke.json" \
  --enable-interactive-oauth \
  --oauth-client-id "your-spotify-client-id" \
  --oauth-client-secret "your-spotify-client-secret"
```

Your default browser will open to Spotify's authorization page. Authorize the application, and the token will be captured automatically. The stage will then proceed with ingestion.

**Requirements**:
- OAuth client ID and secret (from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard))
- Redirect URI must match your app's registered settings (default: `http://127.0.0.1:8888/callback`)

**Additional options**:
- `--oauth-redirect-uri`: Custom redirect URI (default: `http://127.0.0.1:8888/callback`)
- `--oauth-timeout-seconds`: Seconds to wait for user authorization (default: 600)
- `--oauth-no-browser`: Skip auto-opening browser; print authorization URL to stdout instead (useful for SSH/Docker/CI)

**Headless example** (SSH, Docker, CI):
```bash
python -m newingestion.main \
  --root "07_implementation/src/newingestion" \
  --enable-interactive-oauth \
  --oauth-client-id "your-id" \
  --oauth-client-secret "your-secret" \
  --oauth-no-browser
```

The authorization URL will be printed; manually open it in a browser on another machine.

**Environment variables** (alternative to CLI args):
```bash
export BL_NEWINGESTION_ENABLE_INTERACTIVE_OAUTH=true
export BL_NEWINGESTION_OAUTH_CLIENT_ID="your-id"
export BL_NEWINGESTION_OAUTH_CLIENT_SECRET="your-secret"

python -m newingestion.main \
  --root "07_implementation/src/newingestion" \
  --run-config "07_implementation/newingestion_smoke.json"
```

## Control Resolution (Payload-First Precedence)

Runtime controls follow a precedence chain to enable environment-aware tuning:

### Priority Order (highest to lowest):

1. **BL_STAGE_CONFIG_JSON environment variable** (orchestration payload)
   - Used by BL-013 to pass stage-specific JSON
   - Example: `{"newingestion": {"source_type": "csv_history"}}`

2. **Run-config file** (--run-config argument)
   - JSON or YAML file with optional `newingestion` section
   - Example:
     ```yaml
     newingestion:
       source_type: spotify_api
       cache_ttl_seconds: 3600
       include_recently_played: false
     ```

3. **Environment variables** (BL_NEWINGESTION_* prefix)
   - E.g., `BL_NEWINGESTION_INCLUDE_SAVED_TRACKS=false`
   - Supports booleans, integers, floats, and strings

4. **Hardcoded defaults** (fallback)
   - Defined in NewingestionControls dataclass

## Data Flow

```
Source Adapter (collect)
    ↓ raw_data (provider-native format with enriched playlist context)
Normalizer (normalize)
    ↓ IngestionDomainBundle (deduplicated entities + explicit relationships)
Validator (validate)
    ↓ bundle enhanced with quality checks, warnings, duplicate detection
Writer (write_outputs)
    ↓ canonical JSON artifacts + run manifest + derived CSV exports
Artifacts emitted to outputs/ directory:
├── (canonical) tracks.json, artists.json, albums.json, playlists.json
├── (membership) top_track_memberships.json, saved_track_memberships.json, playlist_track_memberships.json
├── (events) recently_played_events.json
├── (metadata) account_profile.json, diagnostics.json, duplicate_track_locations.json (if present)
├── (manifest) run_manifest.json (artifact_inventory + compatibility_exports index)
└── (compatibility) top_tracks_short.csv, saved_tracks.csv, playlist_items.csv, etc.
```

## Controls Reference

### Source Selection

| Control | Type | Default | Description |
|---------|------|---------|-------------|
| `source_type` | str | `spotify_api` | Data source: `spotify_api` or `csv_history` |
| `include_top_tracks` | bool | `True` | Collect short/medium/long-term top tracks |
| `include_saved_tracks` | bool | `True` | Collect user's saved/liked tracks |
| `include_playlists` | bool | `True` | Collect user's playlist items |
| `include_recently_played` | bool | `False` | Collect recently played tracks |

### Record Limits (0 = no limit)

| Control | Type | Default | Description |
|---------|------|---------|-------------|
| `max_top_tracks` | int | `0` | Max per time range |
| `max_saved_tracks` | int | `0` | Max saved tracks |
| `max_playlist_items` | int | `0` | Max playlist items |
| `max_recently_played` | int | `0` | Max recently played |

### Resilience

| Control | Type | Range | Default | Description |
|---------|------|-------|---------|-------------|
| `cache_ttl_seconds` | int | [1, 86400] | 3600 | API response cache lifetime |
| `throttle_sleep_seconds` | float | [0.01, 10.0] | 0.1 | Delay between API calls |
| `max_retries` | int | [0, 10] | 3 | Retry attempts on errors |
| `base_backoff_delay_seconds` | float | [0.1, 60.0] | 1.0 | Initial exponential backoff |

### Error Handling

| Control | Type | Default | Description |
|---------|------|---------|-------------|
| `fail_on_missing_scope` | bool | `False` | Raise error if credentials unavailable |
| `fail_on_collection_error` | bool | `False` | Raise error if any collection fails |

### Output

| Control | Type | Default | Description |
|---------|------|---------|-------------|
| `emit_summary_json` | bool | `True` | Write summary JSON artifact |
| `emit_flat_csvs` | bool | `True` | Write CSV files for each collection |
| `include_raw_response_payloads` | bool | `False` | Include raw provider response in normalized JSON |

## Output Artifacts

The writer emits a machine-readable run manifest that indexes all outputs, enabling downstream stages to locate specific artifacts programmatically.

### Run Manifest (`run_manifest.json`)

**Purpose**: Single source of truth for all ingestion outputs; consumed by downstream stages to locate and validate artifacts.

```json
{
  "run_id": "INGESTION-20260401T120000-ABCDEF",
  "generated_at_utc": "2026-04-01T12:00:00.000000",
  "source_type": "spotify_api",
  "user_id": "spotify_user_id",
  "account_country": "US",
  "account_product": "premium",
  "counts": {
    "top_tracks_short": 50,
    "top_tracks_medium": 50,
    "top_tracks_long": 50,
    "saved_tracks": 176,
    "playlist_items": 31,
    "recently_played": 0,
    "total_unique_tracks": 287
  },
  "selection_flags": {
    "include_top_tracks": true,
    "include_saved_tracks": true,
    "include_playlists": true,
    "include_recently_played": false
  },
  "warnings": [],
  "artifact_inventory": {
    "tracks": "07_implementation/outputs/INGESTION-...-tracks.json",
    "artists": "07_implementation/outputs/INGESTION-...-artists.json",
    "albums": "07_implementation/outputs/INGESTION-...-albums.json",
    "playlists": "07_implementation/outputs/INGESTION-...-playlists.json",
    "account_profile": "07_implementation/outputs/INGESTION-...-account_profile.json",
    "track_artist_relations": "07_implementation/outputs/INGESTION-...-track_artist_relations.json",
    "top_track_memberships": "07_implementation/outputs/INGESTION-...-top_track_memberships.json",
    "saved_track_memberships": "07_implementation/outputs/INGESTION-...-saved_track_memberships.json",
    "playlist_track_memberships": "07_implementation/outputs/INGESTION-...-playlist_track_memberships.json",
    "recently_played_events": "07_implementation/outputs/INGESTION-...-recently_played_events.json",
    "diagnostics": "07_implementation/outputs/INGESTION-...-diagnostics.json",
    "duplicate_track_locations": "07_implementation/outputs/INGESTION-...-duplicate_track_locations.json"
  },
  "compatibility_exports": {
    "top_tracks_short": "07_implementation/outputs/INGESTION-...-top_tracks_short.csv",
    "top_tracks_medium": "07_implementation/outputs/INGESTION-...-top_tracks_medium.csv",
    "top_tracks_long": "07_implementation/outputs/INGESTION-...-top_tracks_long.csv",
    "saved_tracks": "07_implementation/outputs/INGESTION-...-saved_tracks.csv",
    "playlist_items": "07_implementation/outputs/INGESTION-...-playlist_items.csv",
    "recently_played": "07_implementation/outputs/INGESTION-...-recently_played.csv"
  }
}
```

### Canonical JSON Artifacts

These are the primary immutable outputs. Each artifact is a JSON array of domain objects with stable schemas.

| Artifact | Schema | Purpose |
|----------|--------|---------|
| `tracks.json` | Array of SpotifyTrack | All unique tracks in the ingestion (deduplicated by track_id) |
| `artists.json` | Array of SpotifyArtist | All unique artists (deduplicated by artist_id) |
| `albums.json` | Array of SpotifyAlbum | All unique albums (deduplicated by album_id) |
| `playlists.json` | Array of SpotifyPlaylist | All playlists in the ingestion (deduplicated by playlist_id) |
| `account_profile.json` | SpotifyAccountProfile | User profile metadata (user_id, country, product, etc.) |
| `track_artist_relations.json` | Array of TrackArtistRelation | Explicit multi-artist relationships with artist_order |
| `top_track_memberships.json` | Array of TopTrackMembership | Track presence in short/medium/long-term top tracks with rank |
| `saved_track_memberships.json` | Array of SavedTrackMembership | Tracks in user's saved/liked collection with added_at timestamp |
| `playlist_track_memberships.json` | Array of PlaylistTrackMembership | Track presence in playlists with position and added metadata |
| `recently_played_events.json` | Array of RecentlyPlayedEvent | Recently played tracks with timestamp and context |
| `duplicate_track_locations.json` | Dict[track_id, List[occurrence]] | Diagnostic artifact: tracks appearing in multiple collections |
| `diagnostics.json` | Dict | Runtime diagnostics: throttle counts, cache stats, API call counts |

### Relationship Preservation

The domain model explicitly preserves multi-entity relationships that would be lost in a flattened schema:

- **Multi-artist tracks**: Each artist→track edge in `track_artist_relations.json` preserves `artist_order` to reconstruct exact credit ordering
- **Playlist context**: Each `PlaylistTrackMembership` captures which playlist, position, and who added it (when available)
- **Temporal context**: `SavedTrackMembership` and `RecentlyPlayedEvent` retain timestamps and context URIs for temporal analysis

### CSV Compatibility Exports (Derived)

When `emit_flat_csvs=True`, the writer derives flat CSV exports from the bundle for backward compatibility and easier spreadsheet consumption:

- `RUNID_top_tracks_short.csv`, `RUNID_top_tracks_medium.csv`, `RUNID_top_tracks_long.csv`
- `RUNID_saved_tracks.csv`
- `RUNID_playlist_items.csv`
- `RUNID_recently_played.csv`

**Note**: CSV exports are *derived* from the canonical JSON; the JSON artifacts are the primary contract for downstream stages. CSV exists only for human inspection and backward compatibility with analysis tools that require flattened data.

### Legacy Summary Artifact (Deprecated)

The `RUNID_summary.json` file that was previously the primary output is now deprecated in favor of the run manifest. A simple summary is still emitted for quick CLI inspection:

```json
{
  "run_id": "INGESTION-...",
  "source_type": "spotify_api",
  "counts": { ... },
  "manifest_artifact": "/path/to/run_manifest.json",
  "canonical_artifacts": { ... },
  "compatibility_exports": { ... },
  "warnings": []
}
```

## Source Adapters

### Supported Sources

- **spotify_api** (default): Spotify Web API extraction with OAuth, pagination, and rate-limit handling
- **csv_history**: Import pre-exported CSV history files

### Adding a New Source

1. Create a new class inheriting from `IngestionSourceAdapter` in `source_adapters.py`
2. Implement `verify_credentials()` and `collect()`
3. Return raw data dict with keys: `top_tracks_short`, `saved_tracks`, etc.
4. Register in `get_adapter()` factory function

Example:
```python
class MySourceAdapter(IngestionSourceAdapter):
    @property
    def source_type(self) -> str:
        return "my_custom_source"

    def verify_credentials(self, context: SourceAdapterContext) -> bool:
        return True

    def collect(self, context: SourceAdapterContext) -> Dict[str, Any]:
        return {"saved_tracks": [...]}
```

## Canonical Event Model

Every collected track is normalized to a `CanonicalTrackEvent` with:

- **Identity**: track_id, track_name, artist_name, album_name
- **Metadata**: duration_ms, explicit, popularity, isrc
- **Temporal**: event_type, time_range, added_at, position_in_source
- **Quality**: quality_flags, is_local
- **Provider**: provider, provider_request_id

## Testing

Run tests with:

```bash
python -m pytest 07_implementation/tests/test_newingestion_stage.py -v
```

Test coverage includes:

- Model creation and freezing
- Control resolution and precedence
- Normalization of Spotify data
- Validation and quality checks
- Stage initialization and workflow
- Adapter instantiation

## Standalone vs. Orchestrated

### Current (Standalone)

- Run directly: `python -m newingestion.main --root /path/to/newingestion`
- No BL-013 integration
- No artifact registry registration
- No run-config schema changes

### Future (Orchestrated)

When ready to integrate with BL-013:

1. Register in `shared_utils/artifact_registry.py`
2. Add dispatcher in `orchestration/config_resolver.py`
3. Add to orchestration in `orchestration/stage_runner.py`

**No changes required to newingestion code for orchestration integration.**

## Dependencies

- Python 3.10+
- Standard library: dataclasses, pathlib, json, csv, datetime, typing
- Optional: pyyaml (for run-config YAML support)

## Package Structure

```
07_implementation/src/newingestion/
├── __init__.py                 # Package initialization
├── main.py                     # CLI entrypoint
├── stage.py                    # IngestionStage coordinator
├── models.py                   # Type contracts
├── runtime_controls.py         # Control resolution
├── source_adapters.py          # Pluggable adapters
├── normalizer.py               # Normalization logic
├── validator.py                # Validation logic
├── writer.py                   # Output writing
├── outputs/                    # Output artifacts directory
└── README.md                   # This file
```

## Status

- **v0.1.0** (2026-04-01): Scaffold complete, all core modules implemented, stage coordinator functional, Spotify/CSV adapters defined (stubs), comprehensive tests included
- **v0.2.0** (future): Complete Spotify API adapter with OAuth, pagination, retry
- **v0.3.0** (future): CSV history adapter implementation
- **v0.4.0** (future): Orchestration integration (optional, preserves standalone operation)

---

**Project**: Thesis Recommendation System
**Date**: April 1, 2026
**Status**: Standalone implementation ready for review and integration
