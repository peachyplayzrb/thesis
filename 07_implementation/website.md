# Website Plan, Implementation, and Log

Date: 2026-03-22
Owner: GitHub Copilot (GPT-5.3-Codex)
Location: 07_implementation/website/

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
- The JavaScript currently uses a local demo generator so the website works immediately without backend setup.
- To connect real generation logic, replace the body of requestPlaylist in app.js with a fetch call to your backend endpoint.

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
   - Get Top Artists
   - Get Saved Tracks
   - Get Public Playlists + Items
   - Get Recently Played
   - Get Followed Artists
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
- Freeze current recommendation pipeline behavior (BL-020 baseline) to prevent scope drift while website integration is implemented.

Primary objectives in this package:
- Build a usable website interaction layer over the current implementation, not a new recommendation algorithm version.
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
