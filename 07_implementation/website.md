# Website Plan, Implementation, and Log

Date: 2026-03-22
Owner: GitHub Copilot (GPT-5.3-Codex)
Location: 07_implementation/website/

## Comprehensive Website Blueprint (v2)

Date: 2026-03-24
Status: Active Plan (supersedes the initial minimal plan)

### 1) Product Purpose
- Deliver a full website-controlled path for the deterministic generator pipeline: import -> profile basis -> run -> results -> inspect evidence.
- Preserve deterministic BL-020 stage behavior while making operation controllable, observable, and recoverable for end users.
- Keep all controls and outputs explainable enough to support thesis evidence and demonstrations.

### 2) User Goals
- Start, monitor, cancel, and rerun ingestion and generation without terminal usage.
- Control input scope and profile basis at a fine-grained level.
- Understand exactly why a playlist was produced (inputs, parameters, stage outputs, and explanations).
- Recover safely from stale data, partial runs, API errors, and unsupported endpoint states.

### 3) UX Principles (Control + Transparency)
- Control-first: every irreversible or high-impact action has explicit controls, confirmation, and safe defaults.
- Transparency-by-default: every stage shows run id, timestamps, status, inputs, output hashes, and artifact links.
- Deterministic trust: rerun actions surface whether config or inputs changed from prior run.
- Recoverability: stale snapshots, cancelled runs, and failed stages always expose next best action.
- Progressive depth: keep quick summaries visible, with expandable diagnostics/log detail.

### 4) End-to-End Website Information Architecture
1. Landing
    - Purpose: clear entry points and current runtime health.
    - Route: `/website/index.html`
2. Import Data
    - Purpose: source selection, ingest run control, live ingest diagnostics.
    - Route: `/website/import.html`
3. Profile Basis
    - Purpose: group/track exclusions and profile-input verification.
    - Route: `/website/profile_basis.html`
4. Run Generator (new)
    - Purpose: trigger BL-004 -> BL-009 chain with selected controls.
    - Route: `/website/run.html`
5. Results + Transparency (new)
    - Purpose: playlist output, explanation payloads, observability snapshot, export/download.
    - Route: `/website/results.html`
6. Run History (new)
    - Purpose: compare past runs, detect drift, reload prior successful state.
    - Route: `/website/history.html`

### 5) Core User Flows
1. Ingest flow
    - Configure source scope -> Start -> OAuth (if required) -> Running diagnostics -> Completed/Cancelled/Failed.
2. Profile preparation flow
    - Load current source -> apply exclusions -> verify included track counts -> save profile basis snapshot.
3. Pipeline run flow
    - Select active run controls -> execute deterministic stages -> observe stage-by-stage state.
4. Results inspection flow
    - Review playlist, score/explanation summaries, and observability metadata -> export evidence package.
5. Recovery flow
    - Failed/cancelled stage -> show cause + actionable recovery options -> rerun from safe checkpoint.

### 6) Control Surfaces To Expose
- Ingestion controls
   - Source toggles and limits.
   - Start/Cancel/Refresh/Clear saved selection.
- Profile basis controls
   - Exclude group.
   - Exclude individual track.
   - Clear exclusions.
   - Clear local snapshot.
   - Refresh from latest export.
- Pipeline controls (new)
   - Run full chain.
   - Run from selected stage (bounded; only valid checkpoints).
   - Cancel active run.
   - Deterministic rerun with prior config lock.
   - Save named run config preset.
- Results controls (new)
   - View summary vs full diagnostics.
   - Download playlist JSON/CSV and explanation payloads.
   - Download run evidence bundle metadata manifest.

### 7) Transparency Surfaces To Expose
- Global run banner
   - `run_id`, status, start/end UTC, elapsed duration, current stage.
- Stage cards
   - Input artifact hash, output artifact hash, row/count summary, status, and failure reason if any.
- Config visibility
   - Active settings and source-scope manifest for current run.
- Evidence links
   - Direct links or file references for BL-004 to BL-009 output artifacts.
- Diff transparency
   - Compare current run vs previous run on key metrics (counts, top-10 overlap, hash changes).

### 8) Target Backend API Contract (Website-Oriented)

Current implemented ingestion endpoints:
- `POST /api/spotify/export/start`
- `GET /api/spotify/export/status`
- `POST /api/spotify/export/cancel`

Planned generator orchestration endpoints:
- `POST /api/pipeline/run/start`
   - Body: profile snapshot reference + run controls.
- `GET /api/pipeline/run/status?run_id=...&after=...`
   - Returns global + per-stage status timeline.
- `POST /api/pipeline/run/cancel`
   - Cancels active pipeline execution.
- `GET /api/pipeline/run/results?run_id=...`
   - Returns summary pointers to playlist/transparency/observability outputs.
- `GET /api/pipeline/run/history?limit=...`
   - Returns prior run index for compare/reload.

Planned utility endpoints:
- `GET /api/health`
- `GET /api/runtime/config`
- `POST /api/runtime/config/validate`

### 9) Frontend State Contracts
- Canonical state domains
   - `ingestionRunState`
   - `profileBasisState`
   - `pipelineRunState`
   - `resultsState`
   - `uiPreferences`
- Persistence boundaries
   - `localStorage` only for user selections and UI preferences.
   - Generated artifacts remain file-system backed through API.
- Source precedence policy
   - Export artifacts (latest valid run) -> local saved snapshot -> empty state.
- Stale data policy
   - Every persisted local snapshot carries `created_at`, `source_run_id`, and compatibility version.

### 10) File and Module Structure Plan

Keep current files, then incrementally split logic by domain.

Current files (already in use):
- `07_implementation/website/index.html`
- `07_implementation/website/import.html`
- `07_implementation/website/profile_basis.html`
- `07_implementation/website/app.js`
- `07_implementation/website/profile_basis.js`
- `07_implementation/website/style.css`
- `07_implementation/setup/website_api_server.py`

Planned website files:
- `07_implementation/website/run.html`
- `07_implementation/website/results.html`
- `07_implementation/website/history.html`
- `07_implementation/website/scripts/core/api_client.js`
- `07_implementation/website/scripts/core/state_store.js`
- `07_implementation/website/scripts/core/storage.js`
- `07_implementation/website/scripts/core/formatters.js`
- `07_implementation/website/scripts/core/constants.js`
- `07_implementation/website/scripts/pages/import_page.js`
- `07_implementation/website/scripts/pages/profile_basis_page.js`
- `07_implementation/website/scripts/pages/run_page.js`
- `07_implementation/website/scripts/pages/results_page.js`
- `07_implementation/website/scripts/pages/history_page.js`
- `07_implementation/website/scripts/components/status_badge.js`
- `07_implementation/website/scripts/components/stage_timeline.js`
- `07_implementation/website/scripts/components/log_viewer.js`
- `07_implementation/website/scripts/components/artifact_table.js`
- `07_implementation/website/styles/tokens.css`
- `07_implementation/website/styles/layout.css`
- `07_implementation/website/styles/components.css`
- `07_implementation/website/styles/pages/import.css`
- `07_implementation/website/styles/pages/profile_basis.css`
- `07_implementation/website/styles/pages/run.css`
- `07_implementation/website/styles/pages/results.css`
- `07_implementation/website/styles/pages/history.css`

Planned backend modules (inside setup):
- `07_implementation/setup/website_api_server.py` (router + HTTP contract)
- `07_implementation/setup/services/run_registry.py` (active/past run bookkeeping)
- `07_implementation/setup/services/ingestion_service.py` (Spotify export orchestration)
- `07_implementation/setup/services/pipeline_service.py` (BL-004 -> BL-009 orchestration)
- `07_implementation/setup/services/artifact_service.py` (artifact discovery + hash summaries)
- `07_implementation/setup/services/events_service.py` (line-based run event stream)

### 11) Pipeline Stage Visibility Model
- Stages to display:
   - BL-004 profile
   - BL-005 retrieval
   - BL-006 scoring
   - BL-007 playlist assembly
   - BL-008 transparency
   - BL-009 observability
- Per-stage data shown:
   - status (`queued|running|completed|failed|cancelled`)
   - start/end UTC and duration
   - primary input/output artifact references
   - row/count metrics
   - deterministic hash snippet

### 12) Error and Recovery Strategy
- Error categories:
   - auth/oauth, network, upstream API rate/permission, artifact missing, contract mismatch, unexpected runtime exception.
- Recovery actions per category:
   - retry now, rerun stage, clear local snapshot, refresh artifacts, open diagnostic log, and copy failure context.
- Safety rules:
   - no silent fallback when data source changed.
   - explicit warning when using stale local data over export data.

### 13) Accessibility and Usability Requirements
- Keyboard reachable controls for all run actions.
- Clear button labels with verb-first action names.
- ARIA-live status region for run-state changes.
- Color is never the only status signal.
- Mobile-first layout for core action cards and timelines.

### 14) Security and Privacy Boundaries
- Never persist OAuth secrets or tokens in website localStorage.
- API responses set no-store headers for status and run metadata.
- Logs should avoid leaking sensitive request headers.
- Restrict local API server bind scope to localhost.

### 15) Testing Plan (Website Integration)
- Contract checks
   - Endpoint response schema validation for start/status/cancel/results/history.
- Scenario checks
   - happy path full run.
   - cancel during ingestion.
   - cancel during pipeline stage.
   - stale snapshot clear and refresh.
   - unsupported endpoint selection handling.
- Determinism checks
   - same inputs/config -> same output hashes.
- UI checks
   - button enable/disable correctness by state.
   - stage timeline transitions.

### 16) Evidence and Governance Hooks
- Each website-triggered run records:
   - `run_id`, selected sources, control settings, stage timeline, artifact hashes, and user actions (start/cancel/retry).
- Update logs in:
   - `07_implementation/website.md`
   - `07_implementation/experiment_log.md`
   - `07_implementation/test_notes.md`
   - `00_admin/change_log.md`

### 17) Delivery Phases
1. Phase A: Stabilize current import/profile controls (complete).
2. Phase B: Add pipeline run orchestration page and API endpoints.
3. Phase C: Add results/transparency page with artifact drill-down.
4. Phase D: Add run history and compare view.
5. Phase E: Split frontend into modular page/core/component files.

### 18) Definition of Done (Website Generator Integration)
- User can complete end-to-end flow entirely from website UI.
- All major actions (start, cancel, rerun, refresh, clear) are available and state-safe.
- Stage-level transparency is visible with artifact references and key metrics.
- Run outputs are downloadable and auditable.
- Logging/evidence artifacts are updated for reproducibility and thesis traceability.

## Objective
Create a simple HTML, CSS, and JavaScript website for user interaction with the playlist generator.

## Plan
1. Create a minimal single-page interface.
2. Add one form with three fields: mood, genre, duration.
3. Add a Generate Playlist button.
4. Add status messaging for ready, loading, and error states.
5. Add results rendering for generated tracks.
6. Keep styling clean and responsive for desktop and mobile.

## Implementation Summary
1. Created `index.html` with:
   - Form inputs for mood, genre, duration.
   - Submit button for generation.
   - Status text block.
   - Results list container.
2. Created `style.css` with:
   - Two-card desktop layout and one-column mobile layout.
   - Input, button, and focus styles.
   - Status modifiers for loading and error.
   - Track item card style.
3. Created `app.js` with:
   - Input parsing and validation.
   - Loading and status state management.
   - Local demo playlist generation logic.
   - Rendering for results, empty state, and error state.
   - Submit event wiring.

## Build Log
- 2026-03-22 01: Identified target location in implementation section.
- 2026-03-22 02: Scaffolded website folder with three files.
- 2026-03-22 03: Implemented semantic HTML structure and form.
- 2026-03-22 04: Implemented responsive styling and state classes.
- 2026-03-22 05: Implemented JS logic, validation, render flow, and handlers.
- 2026-03-22 06: Added this document to capture plan + implementation + log.

## Notes
- Manual mode remains browser-local and stores uploaded/pasted JSON in `localStorage`.
- Spotify mode now uses a real local backend server and starts the Python ingestion/export pipeline through HTTP API endpoints.

## Website Runtime Fix Log

Date: 2026-03-23
Status: Completed

Problem:
- The website intermittently returned HTTP 404 during local testing because multiple ad hoc `python -m http.server` processes were bound across different working directories.
- The browser path depended on whichever folder the temporary server happened to expose.

Fix:
- Added canonical root redirect file: `07_implementation/index.html` → `website/import.html`
- Added stable launcher scripts:
   - `07_implementation/setup/start_website.ps1`
   - `07_implementation/setup/start_website.cmd`
- Standardized the local website root to the `07_implementation/` directory using explicit `--directory` startup.

Canonical local run methods:
```cmd
07_implementation\setup\start_website.cmd
```

Alternative PowerShell form:
```powershell
powershell -ExecutionPolicy Bypass -File 07_implementation\setup\start_website.ps1
```

Canonical local URLs:
- `http://127.0.0.1:5501/`
- `http://127.0.0.1:5501/website/import.html`

Launcher behavior:
- `start_website.cmd` / `start_website.ps1` starts at port `5501` and automatically moves to the next free port if that port is already in use.

Outcome:
- Local website startup is now deterministic.
- Root URL and explicit import page URL both resolve correctly.
- Website import flow continues to read live Spotify export artifacts from `implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/`.

## Real Spotify Ingestion Integration Log

Date: 2026-03-23
Status: Completed

Change:
- Replaced static Spotify import behavior with a real local API-backed ingestion flow.
- The import page now starts `ingestion.export_spotify_max_dataset` through a local Python HTTP server, polls live run status, shows raw logs, exposes the OAuth authorization URL when needed, and persists imported groups only after the backend run completes successfully.

Implementation:
- Added backend server: `07_implementation/setup/website_api_server.py`
- Updated launcher: `07_implementation/setup/start_website.ps1` now runs the API server instead of plain `http.server`
- Import page now calls:
   - `POST /api/spotify/export/start`
   - `GET /api/spotify/export/status`
- Added live run diagnostics UI in `import.html`
- Added endpoint-scoped exporter options in `export_spotify_max_dataset.py`
- Added support for `recently played` export artifacts and profile loading

User-visible behavior:
- Clicking `Ingest` in Spotify mode now starts a real ingestion run.
- The page shows current step, timestamps, exit code, OAuth link, and live log output.
- When the run finishes, the page refreshes export artifacts and saves the selected imported groups for `profile_basis.html`.

Smoke-test evidence:
- Local API-backed server validated on `http://127.0.0.1:5503/`
- Status endpoint returned JSON successfully
- A real API-triggered smoke test completed with run id `SPOTIFY-EXPORT-20260323-224359-435664`
- Smoke test request used `saved_tracks` only with `max_items=2` and completed successfully

Operational note:
- The smoke test intentionally overwrote live export artifacts with a minimal run. A full UI-triggered ingest will regenerate the broader dataset using the user-selected endpoints and limits.

## Profile Page Import Summary Log

Date: 2026-03-23
Status: Completed

Change:
- Added an import summary panel to `profile_basis.html`.
- Fixed source precedence so the profile page uses the saved import-page selection first and only falls back to full export artifacts when no saved selection exists.

Why this mattered:
- Without this fix, the profile page could ignore the user’s chosen endpoint subset from the import page and silently load the full export instead.

User-visible outcome:
- The profile page now shows source, saved/generated time, run id, group count, visible track count, and selection scope.
- If the user imported a scoped selection from the import page, that exact saved selection is what the profile page uses.

## Import Data Page - Implementation Log

Date: 2026-03-22
Status: Implemented

### Execution Scope
- Implemented Import Data page in the website prototype.
- Added CSV-first import flow with parsing, validation, alignment diagnostics, and run summary.
- Added optional influence-track input management.
- Preserved simple structure and no-framework architecture.

### Files Updated
1. `07_implementation/website/index.html`
   - Replaced playlist form with Import Data interface.
   - Added source tabs (Upload CSV, Spotify API, Help).
   - Added CSV upload form and status text.
   - Added diagnostics panel with progress, summary metrics, unmatched list.
   - Added influence track form/list and run summary section.

2. `07_implementation/website/style.css`
   - Added styles for tab navigation and active panel switching.
   - Added progress bar and summary grid styling.
   - Added warning state, utility hidden class, and inline form layout.
   - Added responsive adjustments for tabs and influence form on mobile.

3. `07_implementation/website/app.js`
   - Replaced generator demo logic with import workflow controller.
   - Added CSV parser and required-header validation.
   - Added row-level validation for core fields, timestamp, and play duration.
   - Added alignment simulation with ISRC-first then metadata fallback behavior.
   - Added diagnostics rendering: totals, match rate, unmatched samples.
   - Added influence-track add/remove behavior.
   - Added run-id generation and final run summary render.

### Functional Behavior Delivered
1. User uploads CSV.
2. App runs staged process: Parse -> Validate -> Align -> Complete.
3. App shows totals, valid/invalid counts, matched/unmatched counts, and match rate.
4. App displays unmatched sample rows with reason codes.
5. User can add and remove optional influence tracks.
6. App generates run identifiers and displays run summary.

### Current Limitation
- Alignment is currently deterministic simulation in frontend logic.
- Next integration step is replacing local processImport internals with real backend endpoints.

### Suggested Backend Contract for Next Step
- POST `/api/import/validate`
- POST `/api/import/align`
- POST `/api/import/commit`
- GET `/api/import/:run_id/status`

### Completion Record
- Planning completed in `07_implementation/import_data_page_plan.md`.
- Implementation completed in website files above.
- Logging completed in this document.

## Separate HTML Split Log

Date: 2026-03-22
Status: Completed

Change:
- Moved the Import Data interface into a dedicated page: `07_implementation/website/import.html`.
- Converted `07_implementation/website/index.html` into a simple landing page with a link to `import.html`.

Reason:
- Keep Import Data as a separate HTML page as requested while preserving the existing JS controller in `app.js` for import-specific behavior.

## Spotify API Source Selection Log

Date: 2026-03-22
Status: Completed

Change:
- Added selectable Spotify API ingestion scopes in `07_implementation/website/import.html`:
   - Top Tracks
   - Saved Tracks
   - Playlist Tracks
- Added per-scope row limit inputs.
- Added selection summary text and API import action button.

Behavior:
- User can select/deselect each source before API import.
- At least one source must be selected.
- Selected scopes drive the API import run and are included in run summary output.

Implementation files:
- 07_implementation/website/import.html
- 07_implementation/website/style.css
- 07_implementation/website/app.js

## Spotify API Advanced Control Log

Date: 2026-03-22
Status: Completed

Documentation basis used:
- Spotify Get User's Top Items: time_range options short_term, medium_term, long_term; limit up to 50; offset support.
- Spotify Get User's Saved Tracks: limit up to 50; offset and pagination.
- Spotify Get Current User's Playlists: limit up to 50; offset and pagination.
- Spotify Get Playlist Items: limit up to 100 on items endpoint; pagination and additional_types support.

Control improvements delivered:
- Top Tracks now supports independent control for all three time ranges.
- Each time range has its own enable toggle, limit, and offset.
- Saved Tracks now supports page size, max pages, and start offset.
- Playlist import now supports playlist page size/pages/offset, item page size, and max pages per playlist.
- Added include-episodes option for playlist items behavior.
- Selection summary now reflects exact selected scopes and parameter values.

Outcome:
- User can explicitly scope and tune Spotify API ingestion volume and coverage before import, instead of only using coarse source toggles.

## UX Clarity and Diagnostics Pause Log

Date: 2026-03-22
Status: Completed

Changes:
- Added clear on-page guidance for pagination, limit/page-size, max pages, and offset semantics.
- Added explicit min/max ranges in control labels (for example top tracks limit 1-50).
- Added top-track header row to make limit and offset columns obvious.
- Added frontend clamping so values stay within allowed ranges automatically.
- Hid Import Diagnostics panel for now to reduce UI complexity during control tuning.

Files:
- 07_implementation/website/import.html
- 07_implementation/website/style.css
- 07_implementation/website/app.js

## Max Toggle and Bounds Enforcement Log

Date: 2026-03-22
Status: Completed

Changes:
- Added `Use Max` checkboxes for each numeric Spotify API control.
- When `Use Max` is checked, the associated numeric input snaps to its max and becomes read-only.
- Added strict min/max clamping on input and blur so values cannot remain too large or too small.
- Kept source-level enabling/disabling behavior compatible with max toggles.

Files:
- 07_implementation/website/import.html
- 07_implementation/website/style.css
- 07_implementation/website/app.js

## Top Tracks Cap Alignment Log

Date: 2026-03-22
Status: Completed

Changes:
- Updated top-tracks UI text to state effective cap: max 50 per selected time range.
- Removed top-track offset controls to avoid implying extra pagination depth.
- Kept per-range limit controls with min/max enforcement and optional Use Max toggle.
- Updated API summary and run metadata formatting to remove top-track offset output.

Files:
- 07_implementation/website/import.html
- 07_implementation/website/style.css
- 07_implementation/website/app.js

## Import vs Profile Page Split Log

Date: 2026-03-22
Status: Completed

Changes:
- Kept `import.html` focused on ingestion options only (CSV and Spotify API source controls).
- Removed post-ingestion profile configuration elements from import flow.
- Added new post-ingestion page `profile_basis.html` for profile basis selection.
- Added `profile_basis.js` for profile-source selection, weights, bias controls, and optional influence tracks.

## Real Spotify Export Wiring Log

Date: 2026-03-23
Status: Completed

Changes:
- Added a "Latest Spotify Export" status card to `import.html` with run id, UTC generation time, key counts, and a refresh button.
- Updated `app.js` to load real artifacts from `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/`:
   - `spotify_export_run_summary.json`
   - `spotify_top_tracks_flat.csv`
   - `spotify_saved_tracks_flat.csv`
   - `spotify_playlist_items_flat.csv`
- Replaced Spotify mock-track ingestion path with real-row group building and local persistence for downstream profile-basis selection.
- Kept manual JSON path unchanged.
- Added status-card styling in `style.css`.

Behavior:
- Spotify ingest button is enabled only when export artifacts are detected and at least one endpoint is selected.
- Stored groups now carry real track rows and metadata (including playlist identifiers where available).
- Recently played remains selectable in UI but is skipped during group build because current export artifacts do not include a recently-played flat file.

Files:
- `07_implementation/website/import.html`
- `07_implementation/website/app.js`
- `07_implementation/website/style.css`
- Added navigation link from import page to profile basis page.

Files:
- 07_implementation/website/import.html
- 07_implementation/website/profile_basis.html
- 07_implementation/website/profile_basis.js
- 07_implementation/website/app.js
- 07_implementation/website/style.css

## Import Scope Simplification Log

Date: 2026-03-22
Status: Completed

Changes:
- Replaced detailed Spotify API parameter controls with a fixed pull-scope checklist.
- Import page now states what will be pulled by default:
   - Max top tracks (50 x short, medium, long)
   - All saved tracks
   - All saved public playlists with all playlist items
- Added one opt-out checkbox for each source so users can skip ingesting any source.
- Updated import logic to consume only these three source toggles.

Files:
- 07_implementation/website/import.html
- 07_implementation/website/style.css
- 07_implementation/website/app.js

## Endpoint Limits + Profile Exclusions Log

Date: 2026-03-22
Status: Completed

Import page updates:
- Added endpoint options with limits for:
   - Get Top Tracks
   - Get Saved Tracks
   - Get Public Playlists + Items
   - Get Recently Played
- Each endpoint now has an include checkbox plus a limit control.

Import behavior updates:
- API import now generates grouped import payloads per endpoint and stores them in localStorage for profile-basis review.
- Selection summary reflects active endpoint selections and configured limits.

Profile basis updates:
- Replaced generic profile form with endpoint-group exclusion workflow.
- Profile basis now renders each imported endpoint group and all tracks from each group.
- Added exclusion controls:
   - Exclude entire endpoint group
   - Exclude individual tracks
- Exclusion decisions are saved to localStorage.

Files:
- 07_implementation/website/import.html
- 07_implementation/website/app.js
- 07_implementation/website/profile_basis.html
- 07_implementation/website/profile_basis.js
- 07_implementation/website/style.css

## Full-Control Import Upgrade Log

Date: 2026-03-22
Status: Completed

Changes:
- Upgraded Spotify API import controls back to a full-control model with explicit endpoint tuning.
- Expanded Top Tracks into three independent range controls:
   - short_term include + limit + Use Max
   - medium_term include + limit + Use Max
   - long_term include + limit + Use Max
- Added Use Max toggles to endpoint limit inputs so users can quickly pin each selected limit to its API-safe maximum.
- Restored and rewrote import controller logic in app.js to align with the new control IDs and behaviors.

Behavior:
- Numeric controls are clamped to their allowed bounds.
- Use Max toggles lock value to max and disable manual input until unchecked.
- Top Tracks requires at least one selected range when endpoint is enabled.
- Import continues to persist grouped endpoint outputs for profile-basis exclusions.

Files:
- 07_implementation/website/import.html
- 07_implementation/website/style.css
- 07_implementation/website/app.js

## Freeze + Integration Execution Log

Date: 2026-03-23
Status: Active

Execution decision:
- Freeze current playlist pipeline behavior (BL-020 baseline) to prevent scope drift while website integration is implemented.

Primary objectives in this package:
- Build a usable website interaction layer over the current implementation, not a new algorithm version.
- Connect UI flow to real artifacts and deterministic stage execution outputs.
- Improve reliability and observability in user-facing interaction without changing scoring or assembly logic.

Planned integration sequence:
1. Ingest: wire import controls to real import/export artifacts and stage status reporting.
2. Profile basis: connect exclusions/selections to actual profile-generation inputs.
3. Pipeline run: orchestrate deterministic BL-004 to BL-009 sequence from UI-triggered flow.
4. Results: render playlist, explanation payloads, and run observability metadata in one inspectable path.
5. Hardening: tighten error handling, timeouts, and rerun behavior for reproducible demonstrations.

Scope guardrails:
- Allowed: bug fixes, diagnostics clarity, integration glue, and reproducibility-oriented interaction controls.
- Deferred: BL-021 scope-selection extension and BL-022 corpus-path switching.
- Out of package: new ingestion adapters, ML model additions, or major schema redesign.

Expected evidence artifacts:
- Updated website integration notes and run walkthrough traces.
- Example UI-driven run records linked to BL-020 artifact outputs.
- Change and decision governance entries synchronized in `00_admin/` logs.

## Session Closure Validation Log

Date: 2026-03-24
Status: Completed

Purpose:
- Capture final runtime and artifact validation before chat handoff.

Actions completed:
1. Executed a full Spotify export rerun through the local website API flow.
2. Verified fresh summary artifact output in `spotify_export_run_summary.json`.
3. Confirmed endpoint health for:
   - `/website/import.html`
   - `/website/profile_basis.html`
   - `/api/spotify/export/status`
4. Relaunched website server when a stopped-server condition was detected; confirmed active runtime URL.

Validated run snapshot:
- run_id: `SPOTIFY-EXPORT-20260323-225206-071342`
- generated_at_utc: `2026-03-23T22:52:51Z`
- counts:
   - top_tracks_short_term: `602`
   - top_tracks_medium_term: `3029`
   - top_tracks_long_term: `5114`
   - saved_tracks: `171`
   - playlists: `4`
   - playlist_items: `31`
   - recently_played: `0` (disabled in selection for this run)

Runtime state at closure:
- Active launcher path: `07_implementation/setup/start_website.cmd`
- Active local URL: `http://127.0.0.1:5501/`
- API status: idle and ready for next run

Outcome:
- Import and profile pages are reachable.
- API server is healthy.
- Latest export artifacts are present and synchronized with the validated run.

## Endpoint Reduction + Profile Basis Refinement Log

Date: 2026-03-24
Status: Completed

Purpose:
- Align website-visible ingestion options with endpoints supported and intended for the current app path.
- Remove confusing playlist visibility states on Profile Basis when no actual playlist track rows are available.

Changes completed:
1. Removed recommendations endpoint support end-to-end (exporter/API/UI/schema references).
2. Removed top-artists endpoint support end-to-end (exporter/API/UI/schema references).
3. Updated Profile Basis layout to use the same import-page shell pattern (sidebar + content card).
4. Changed Profile Basis source precedence to prefer full export artifacts over stale local subset snapshots when export artifacts are present.
5. Added playlist visibility rule on Profile Basis: hide playlist groups when no playlist track rows were ingested.
6. Added explicit summary messaging when playlists were requested but hidden because playlist-track ingestion produced no rows.
7. Added market-aware playlist item fetch parameter in exporter (`market` from account profile country) and revalidated behavior.

Validation notes:
- Local runtime checks returned 200 for import/profile pages.
- Post-change export summaries contained no recommendations/top-artists fields.
- Playlist diagnostics confirmed 4 playlists listed, with item rows available only for the owner-accessible playlist in current token context.

Files touched in this phase:
- `07_implementation/implementation_notes/bl001_bl002_ingestion/export_spotify_max_dataset.py`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_mapping.py`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/spotify_artifacts.py`
- `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_schema_reference.md`
- `07_implementation/setup/website_api_server.py`
- `07_implementation/website/import.html`
- `07_implementation/website/app.js`
- `07_implementation/website/profile_basis.html`
- `07_implementation/website/profile_basis.js`
- `07_implementation/website/style.css`

## Interaction Hardening + Bootstrap Acceleration Log

Date: 2026-03-24
Status: Completed

Purpose:
- Improve reliability and recoverability of website-driven Spotify ingestion runs.
- Reduce stale local snapshot confusion between Import and Profile pages.
- Speed up UI iteration with a temporary premade framework layer.

Changes completed:
1. Added cancellable ingestion control path end-to-end.
   - Backend endpoint: `POST /api/spotify/export/cancel`
   - UI control: `Cancel Run` on Import page
   - States covered: `running`, `cancelling`, `cancelled`
2. Hardened API status handling and cache behavior.
   - Safer parsing for malformed `after` query values
   - No-store cache headers on JSON responses to avoid stale status reads
3. Added stale-snapshot controls.
   - Import page: `Clear Saved Selection`
   - Profile page: `Refresh Data`, `Clear Saved Snapshot`
4. Clarified source precedence messaging in Profile Basis.
   - Explicit export-first vs local-fallback behavior in summary text
   - Reload path now resets exclusions and re-renders from current source
5. Added temporary Bootstrap 5 layer for faster styling iteration.
   - Included Bootstrap CSS and JS bundle on:
     - `07_implementation/website/import.html`
     - `07_implementation/website/profile_basis.html`
     - `07_implementation/website/index.html`

Validation notes:
- Local API smoke flow verified start -> status -> cancel -> status transitions.
- Import page reflects cancellation lifecycle and button-state locking during runs.
- Diagnostics checks reported no file errors on touched website files.

Files touched in this phase:
- `07_implementation/setup/website_api_server.py`
- `07_implementation/website/import.html`
- `07_implementation/website/profile_basis.html`
- `07_implementation/website/index.html`
- `07_implementation/website/app.js`
- `07_implementation/website/profile_basis.js`
- `07_implementation/website/style.css`

## Phase B Scaffold: Run Orchestration From Website

Date: 2026-03-24
Status: Implemented

Purpose:
- Start Phase B from the blueprint by enabling website-triggered BL-004 to BL-009 orchestration.
- Provide live run transparency (run status, stage timeline, logs, artifact summary) directly in UI.

Changes completed:
1. Added pipeline API orchestration paths in local website server.
   - `POST /api/pipeline/run/start`
   - `GET /api/pipeline/run/status?after=...`
   - `POST /api/pipeline/run/cancel`
   - `GET /api/pipeline/run/results`
2. Added deterministic stage execution chain in backend job runner.
   - Executes BL-004 -> BL-009 scripts sequentially.
   - Tracks per-stage status, timestamps, exit code, and stage-scoped logs.
   - Supports cancellation and terminal state transitions.
3. Added new run control page.
   - `run.html` with run controls, stage timeline table, artifact summary, and live logs.
   - `run.js` with polling, start/cancel flow, log streaming, and state-safe action locking.
4. Added page-to-page navigation for execution flow.
   - Import -> Profile Basis -> Run Generator links.
   - Landing page updated with direct links to all three pages.
5. Added styling for run-stage transparency components.
   - Stage table and artifact cards integrated into existing style system.

Implementation notes:
- Artifact summary in pipeline status currently reports presence/mtime/size for key BL-004 to BL-009 outputs.
- Pipeline run config payload is accepted and persisted for traceability; advanced config branching remains future work.

Files touched in this phase:
- `07_implementation/setup/website_api_server.py`
- `07_implementation/website/run.html`
- `07_implementation/website/run.js`
- `07_implementation/website/import.html`
- `07_implementation/website/profile_basis.html`
- `07_implementation/website/index.html`
- `07_implementation/website/style.css`

## Phase C/D Delivery: Results, History, and Evidence Bundle Export

Date: 2026-03-24
Status: Implemented

Purpose:
- Complete the immediate next steps after Phase B by adding results inspection, run history comparison, and one-click evidence bundle export from website UI.

Changes completed:
1. Extended pipeline API for transparency and history.
   - Added `GET /api/pipeline/run/history?limit=...`.
   - Upgraded `GET /api/pipeline/run/results` to include run snapshot, compare data, playlist preview, explanation summary, and observability payload.
   - Added `POST /api/pipeline/run/evidence_bundle` to generate a downloadable evidence manifest JSON.
2. Added run-history persistence in backend.
   - Terminal run states (`completed`, `failed`, `cancelled`) are now recorded with stage summary and artifact hashes.
   - Artifact summary now includes SHA-256 hashes for compare and audit use.
3. Added Results page.
   - New `results.html` + `results.js` render run summary, playlist top-10 preview, compare-to-previous details, explanation/observability JSON snapshot, and artifact summary.
4. Added History page.
   - New `history.html` + `history.js` render recent run index and compare counts, with direct links to open specific runs in Results.
5. Added one-click evidence export on Run page.
   - `run.html` now includes an `Export Evidence Bundle` action.
   - `run.js` calls bundle endpoint and downloads the returned JSON manifest.
6. Expanded navigation to full website flow.
   - Added links for Results and Run History in run and landing pages.

Validation notes:
- Diagnostics checks reported no file errors on all touched Python/HTML/JS files.
- Browser page rendering confirms new Run page actions and navigation are visible.
- If API routes return 404 in browser, restart launcher to load latest backend code.

Files touched in this phase:
- `07_implementation/setup/website_api_server.py`
- `07_implementation/website/run.html`
- `07_implementation/website/run.js`
- `07_implementation/website/results.html`
- `07_implementation/website/results.js`
- `07_implementation/website/history.html`
- `07_implementation/website/history.js`
- `07_implementation/website/index.html`

## Per-Stage Control + Transparency Pages Delivery

Date: 2026-03-24
Status: Implemented

Purpose:
- Make each BL-004 to BL-009 stage directly controllable and inspectable from dedicated pages.
- Allow users to run a single stage (or selected stage subset) rather than only full-chain execution.

Changes completed:
1. Added selected-stage execution support in pipeline backend.
   - `POST /api/pipeline/run/start` now accepts `stage_ids` and runs only that subset.
   - Stage selection is validated and reflected in run status payload (`selected_stage_ids`, `available_stage_ids`).
2. Added pipeline stage-catalog endpoint.
   - New `GET /api/pipeline/stages` provides stage labels, scripts, and descriptions for UI metadata.
3. Added dedicated stage pages (one per stage).
   - `stage_bl004.html`
   - `stage_bl005.html`
   - `stage_bl006.html`
   - `stage_bl007.html`
   - `stage_bl008.html`
   - `stage_bl009.html`
4. Added shared stage-page controller.
   - `stage_page.js` handles stage-specific start/cancel/refresh actions, log filtering by stage id, and artifact transparency rendering.
5. Added stage-page navigation from main run page.
   - `run.html` sidebar now links directly to each stage page.

User-visible behavior:
- Each stage page has independent control buttons:
  - `Run This Stage`
  - `Cancel Run`
  - `Refresh`
- Each stage page shows:
  - run and stage status metadata
  - filtered stage logs
  - artifact summary with path, timestamp, and hash

Validation notes:
- Diagnostics reported no file errors for all new/updated files.
- Browser render confirmed stage page UI and stage-specific log visibility.
- If stage metadata endpoint is unavailable in a running browser session, restart server to load latest API routes.

Files touched in this phase:
- `07_implementation/setup/website_api_server.py`
- `07_implementation/website/run.html`
- `07_implementation/website/stage_page.js`
- `07_implementation/website/stage_bl004.html`
- `07_implementation/website/stage_bl005.html`
- `07_implementation/website/stage_bl006.html`
- `07_implementation/website/stage_bl007.html`
- `07_implementation/website/stage_bl008.html`
- `07_implementation/website/stage_bl009.html`

## Per-Stage Parameter Tunability Delivery

Date: 2026-03-24
Status: Implemented

Purpose:
- Extend per-stage controllability from stage selection to stage-specific parameter tuning.
- Ensure stage pages can send validated parameter overrides that actually affect BL-005 to BL-009 execution.

Changes completed:
1. Added backend stage-parameter pass-through for stage subprocess execution.
   - `POST /api/pipeline/run/start` now accepts `stage_params` keyed by stage id.
   - Pipeline runner maps stage params into stage-specific environment variable overrides per stage.
2. Added script-level override support in BL-005 to BL-009 builders.
   - BL-005: semantic and profile-limit thresholds configurable by environment.
   - BL-006: component weights and numeric-threshold JSON overrides supported.
   - BL-007: playlist assembly constraints (size, minimum score, diversity caps) configurable.
   - BL-008: top-contributor explanation depth configurable.
   - BL-009: observability diagnostic sample depth configurable.
3. Added dynamic stage-parameter UI controls to stage pages.
   - `stage_page.js` now renders stage-specific parameter forms for BL-005 to BL-009.
   - Numeric and JSON parameters are validated client-side before run start.
   - Stage run requests include `stage_params` only when overrides are provided.

User-visible behavior:
- BL-004 stage page remains control-only (no parameter form).
- BL-005 to BL-009 pages now expose stage-specific parameter inputs and apply them to the next stage run.
- Parameter usage is surfaced in-page before run dispatch.

Files touched in this phase:
- `07_implementation/setup/website_api_server.py`
- `07_implementation/website/stage_page.js`
- `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
- `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
- `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`
- `07_implementation/implementation_notes/bl008_transparency/build_bl008_explanation_payloads.py`
- `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`

## BL-004 Parameter Tunability Extension

Date: 2026-03-24
Status: Implemented

Purpose:
- Remove the BL-004 tunability gap so all stage pages BL-004 to BL-009 support stage-level parameter control.

Changes completed:
1. Added BL-004 stage parameter controls on stage page UI.
   - `top_tag_limit`
   - `top_genre_limit`
   - `top_lead_genre_limit`
   - `user_id`
2. Added backend mapping of BL-004 stage params to BL-004 environment variables.
3. Added BL-004 script environment override consumption for top limits and user id.

User-visible behavior:
- BL-004 stage page now includes Stage Parameters and sends overrides through `stage_params` when running BL-004.
- BL-004 outputs are now tunable from UI without terminal edits.

Files touched in this phase:
- `07_implementation/website/stage_page.js`
- `07_implementation/setup/website_api_server.py`
- `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py`

## Website Runtime Hardening Pass

Date: 2026-03-24
Status: Implemented

Purpose:
- Improve operational visibility with explicit health and runtime-config APIs.
- Improve stage-page controllability ergonomics with reset/preset controls.
- Add a repeatable smoke check script for quick regression verification.

Changes completed:
1. Added utility API endpoints for runtime observability and validation.
   - `GET /api/health` returns service status, uptime, bind/port, and active job states.
   - `GET /api/runtime/config` returns stage catalog and stage-parameter schema.
   - `POST /api/runtime/config/validate` validates and normalizes `stage_params` payloads.
2. Added run-page health visibility.
   - `run.html` now shows API health state and server uptime.
   - `run.js` polls `/api/health` along with pipeline status updates.
3. Added stage-parameter reset and preset controls.
   - `stage_page.js` now provides `Reset Defaults`, `Save Preset`, and `Load Preset` actions.
   - Presets are persisted per-stage in browser localStorage.
4. Added automation script for rapid website API smoke checks.
   - New script: `07_implementation/setup/smoke_website_api.ps1`
   - Verifies page reachability, health/config endpoints, config validation, stage catalog, and pipeline status response shape.

User-visible behavior:
- Run Generator page now shows whether the local API server is healthy and how long it has been up.
- Stage pages support quick reset to defaults and reusable per-stage parameter presets.
- Operators can run a single smoke script to verify core website+API contract readiness.

Files touched in this phase:
- `07_implementation/setup/website_api_server.py`
- `07_implementation/website/run.html`
- `07_implementation/website/run.js`
- `07_implementation/website/stage_page.js`
- `07_implementation/website/style.css`
- `07_implementation/setup/smoke_website_api.ps1`

## Website IA + Visual Reboot Baseline

Date: 2026-03-24
Status: Implemented (Baseline Slice)

Design direction selected:
- Visual language: studio control room
- Scope: full IA reboot direction
- Baseline page: Import
- Tone: high-contrast technical palette

What changed in this baseline slice:
1. Reframed website navigation around an import-first operational flow.
   - Workflow framing now uses: Import -> Profile Basis -> Run Pipeline -> Inspect Results -> Compare Runs.
2. Rebuilt `import.html` into a control-room shell while preserving existing ingestion behavior and IDs used by `app.js`.
   - Added workflow navigation in sidebar.
   - Added dedicated input-mode section.
   - Reorganized telemetry into side-by-side operational cards.
   - Moved endpoint controls under a single endpoint matrix section.
3. Switched website visual system to a high-contrast technical theme in `style.css`.
   - New dark control-room palette and accent system.
   - Updated card/button/input/table surfaces for contrast consistency.
   - Added import-shell specific classes (`control-shell`, `control-topbar`, `ops-grid`).
4. Updated landing copy in `index.html` to match the new IA language.

Compatibility note:
- Import page JS behavior is intentionally preserved by keeping all existing control IDs and endpoint wiring intact.

Files touched in this phase:
- `07_implementation/website/import.html`
- `07_implementation/website/style.css`
- `07_implementation/website/index.html`
