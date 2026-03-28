# Ingestion De-Caching Decision Log
Date: 2026-03-28
Scope: final_artefact ingestion pipeline (Spotify export path)
Status: Implemented and validated

## 1) Decision Record
Decision made:
- Remove ingestion endpoint caching (SQLite response cache).
- Remove token cache handling from exporter execution path.
- Force a full OAuth flow for each export run.
- Preserve downstream artifact contracts so BL-003 and later stages continue to work without schema/path changes to required outputs.

Why this decision was made:
- Caching complexity was not providing enough value for the current workflow.
- The user explicitly requested simplification and removal of cache/token-cache behavior.
- The pipeline is artifact-driven; reproducibility and downstream stage contracts depend on generated files, not internal cache storage.

Expected tradeoff:
- Pros: simpler logic, fewer stale-state edge cases, clearer run behavior, lower maintenance complexity.
- Cons: more API calls and OAuth interaction per run; no speedup from reusing cached endpoint pages.

## 2) High-Level Behavior Changes
Before:
- Exporter could read/save a token cache file and optionally reuse it.
- Pagination fetches could route through a SQLite endpoint cache (if resilience module available).
- Summary metadata included cache DB path/details.

After:
- Exporter always initiates OAuth flow and does not load/save token cache.
- All pagination fetches call Spotify API directly (no endpoint cache wrapper).
- Summary metadata explicitly reports cache disabled and no cache DB path.
- Support artifact list no longer includes cache DB entry.

## 3) File-Level Change Log

### A) src/ingestion/export_spotify_max_dataset.py
Primary intent:
- Remove token-cache and endpoint-cache control flow from main export orchestration.

Detailed edits:
- Imports:
  - Removed token-cache helper imports: load_token_cache, save_token_cache, token_is_usable.
  - Removed cache-related imports: RESILIENCE_AVAILABLE, CacheDB.
- CLI arguments:
  - Removed --token-cache argument.
- Scope-check helper:
  - Removed _token_has_requested_scopes helper (no longer needed when cache reuse path is removed).
- Data fetch function:
  - _fetch_all_data(...) signature no longer accepts cache_db.
  - Removed client cache namespace assignment branch tied to cache behavior.
  - Updated all fetch_all_offset_pages(...) calls to omit cache_db.
- Main auth flow:
  - Removed cached token load/refresh/reuse branching.
  - Replaced with unconditional OAuth path:
    - print auth start message
    - token_payload = complete_oauth_flow(args)
    - print auth complete message
- Resilience/cache setup:
  - Removed CacheDB initialization and RESILIENCE_AVAILABLE branch.
  - Replaced with explicit "endpoint caching disabled" log line.
- Data fetch call site:
  - Updated to _fetch_all_data(client=client, args=args).
- Run summary:
  - Set resilience.cache_enabled = False.
  - Removed resilience.cache_db_path.
  - Updated resilience.cache_note to direct-fetch wording.
- Finalization:
  - Removed end-of-run token cache save.

### B) src/ingestion/spotify_client.py
Primary intent:
- Remove endpoint cache wrapper and make pagination direct-call only.

Detailed edits:
- Removed cache scaffolding:
  - Deleted import/use of hashlib for cache key construction.
  - Removed optional spotify_resilience import bridge and CacheDB/RESILIENCE_AVAILABLE symbols.
- Removed cached_api_get(...):
  - Deleted complete cache key/namespace/cache_hit/cache_set logic.
- Updated fetch_all_offset_pages(...):
  - Removed cache_db parameter from function signature.
  - Replaced cached_api_get(...) with direct client.api_get(...).

### C) src/ingestion/spotify_artifacts.py
Primary intent:
- Remove cache DB support artifact path from artifact model.

Detailed edits:
- Removed CACHE_DB_FILENAME constant.
- Removed "cache_db" entry from build_support_file_paths(...).
- Kept request_log, summary, and rate_limit_block support artifacts unchanged.

### D) src/ingestion/spotify_io.py
Primary intent:
- Restore helper compatibility used by ingestion modules/script execution paths.

Detailed edits:
- Added now_utc() helper.
- Added sha256_of_file(path) compatibility wrapper.
- Added repo_root() helper.
- Added required imports:
  - datetime/timezone
  - shared sha256 helper
  - impl_root

Reason this was added:
- A post-refactor smoke run exposed missing helper imports for script/runtime compatibility; these functions resolved that gap.

## 4) Validation and Verification Performed
Validation executed:
- Automated tests:
  - pytest on final_artefact tests completed successfully.
  - Result: 181 passed.
- CLI smoke validation:
  - Ran exporter with --help.
  - Initial failure identified missing helper import path for now_utc.
  - After spotify_io.py compatibility patch, --help executed successfully.
- Reference confirmation:
  - Confirmed ingestion cache/token-cache references removed from active ingestion execution path modules.

## 5) Downstream Contract Impact
Preserved:
- Core exported data artifacts expected by BL-003 and downstream stages.
- Export summary file generation and key run metadata (with revised resilience section).

Changed intentionally:
- No token cache persistence behavior.
- No endpoint cache support artifact path.
- Resilience metadata now declares caching disabled.

## 6) Risks and Notes
Known/accepted impacts:
- Export runs may take longer due to direct API fetch each run.
- OAuth interaction is always required.

Known non-blocking diagnostics context:
- Editor/static analysis has shown unresolved fallback import warnings in some script-import contexts; these were pre-existing environmental/static-analysis conditions and did not block runtime smoke validation after compatibility helper patch.

## 7) Outstanding Optional Cleanup (Not Required for Current Decision)
Potential follow-up cleanup:
- Remove now-unused cache-oriented code paths in src/ingestion/spotify_resilience.py.
- Remove/refactor token-cache helper utilities in src/ingestion/spotify_auth.py if they are now fully dead for intended workflows.

## 8) Suggested Isolated Verification Run (No Override of Existing Outputs)
Use a separate output directory for one live OAuth export and BL-003 check:
- Run exporter with --output-dir pointed to a scratch/staging folder.
- Run BL-003 with --spotify-export-dir pointing to that staging export.
- Verify required artifacts are present and BL-003 source checks pass.

## 9) Final Implementation Outcome
The requested simplification was completed:
- Endpoint caching removed from ingestion runtime path.
- Token cache handling removed from ingestion runtime path.
- Export flow now follows a clear, deterministic auth-and-fetch path each run.
- Test suite and smoke checks passed after compatibility fix.

---

## 10) Program-Wide Alignment Addendum (2026-03-28)

To keep the rest of the program aligned with cache removal, a follow-up implementation pass completed the following:

### Runtime messaging and dead-code cleanup
- Updated `src/ingestion/spotify_client.py` refresh-token error messaging to remove cache-era `--force-auth` guidance and reflect full OAuth rerun behavior.
- Removed now-unused token-cache helper functions from `src/ingestion/spotify_auth.py`:
  - `load_token_cache(...)`
  - `save_token_cache(...)`
  - `token_is_usable(...)`

### Documentation alignment
- Updated `src/ingestion/docs/spotify_api_ingestion_runbook.md`:
  - removed token cache / sqlite cache artifacts from output list
  - updated first-run behavior wording to direct-fetch, no persisted cache behavior
  - removed stale notes tied to token-cache handling and `--force-auth` cache-era usage
- Updated `src/ingestion/docs/spotify_schema_reference.md`:
  - removed sqlite cache artifact from active support artifacts
  - clarified endpoint caching is disabled

### Historical log policy applied
- Preserved historical state logs as snapshots and added explicit deprecation notices:
  - `src/ingestion/docs/bl001_state_log_2026-03-24.md`
  - `src/ingestion/docs/bl002_state_log_2026-03-24.md`
- Both files now point readers to this changelog for current behavior.

### Validation after addendum changes
- Diagnostics on edited files: no errors.
- Regression tests: `181 passed`.
- Targeted stale-reference search:
  - no active runtime/runbook/schema references to token cache or sqlite endpoint cache remain
  - one remaining sqlite-cache mention exists only in a preserved historical snapshot file, which is intentional

---

## 11) Playlist Item API Payload Migration Fix (2026-03-28)

### Problem observed
- Isolated export produced playlist rows where playlist metadata fields were populated but all track fields were blank.
- Root cause: mapper expected deprecated `track` payload while current Spotify playlist-item responses expose `item` (track or episode) as primary payload.

### Fix implemented
- Updated `src/ingestion/spotify_mapping.py`:
  - Added item-first payload resolver with fallback to deprecated `track` key for backward compatibility.
  - Updated playlist item flattening to keep only rows where payload type is `track`.
  - Skips non-track payloads (for example episodes) and unavailable/null payloads.
  - Extended same item-first fallback behavior to saved and recently-played track extraction paths.
- Updated `src/ingestion/export_spotify_max_dataset.py`:
  - Added playlist item keep/skip accounting metrics during artifact build.
  - Summary now reports:
    - `playlist_items` (kept track rows)
    - `playlist_items_raw` (raw fetched rows)
    - `playlist_items_skipped_non_track_or_unavailable`
  - Added exporter log line showing raw/kept/skipped playlist item counts.

### Documentation updates
- `src/ingestion/docs/spotify_api_ingestion_runbook.md`:
  - documented item-first parsing and track-only playlist-item policy.
- `src/ingestion/docs/spotify_schema_reference.md`:
  - documented track-only playlist-item export policy and playlist-item summary count semantics.

### Policy decision captured
- Track-only playlist ingestion is intentional for current BL-002/BL-003 pipeline behavior.
- Episode or unavailable playlist entries are excluded from flat playlist-item outputs in this implementation pass.
