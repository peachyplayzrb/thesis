# Import Data Page Plan

Date: 2026-03-22
Scope: MVP-first Import Data page for playlist generator
Status: Implemented in website prototype

## 1. Purpose
The Import Data page is the user entry point for collecting listening history and optional influence tracks before profile building and playlist generation.

Primary goals:
- Support one practical ingestion route in MVP.
- Preserve transparency, controllability, reproducibility, and observability.
- Provide clear validation and alignment diagnostics before proceeding.

## 2. Source Basis (Repository-Derived)
This plan is grounded in the following project sources:
- 00_admin/Artefact_MVP_definition.md
- 06_data_and_sources/schema_notes.md
- 06_data_and_sources/dataset_registry.md
- 05_design/system_architecture.md
- 05_design/controllability_design.md
- 05_design/observability_design.md
- 05_design/requirements_to_design_map.md
- 07_implementation/implementation_plan.md
- 07_implementation/SPOTIFY_INTEGRATION.md
- 07_implementation/backlog.md
- 07_implementation/website.md

## 3. MVP Product Decision
MVP import path:
- Default and required: Spotify Extended Streaming History CSV upload.
- Optional and phased: Spotify Web API path from existing resilience/integration work.

Rationale:
- Matches MVP artefact constraints and existing BL phase status.
- Reduces implementation risk while enabling real user ingestion.

## 4. Page Information Architecture
Single page with structured sections:
1. Header and context
- Title: Import Data
- One-line explanation of why import is required.

2. Source selection
- Tab A: Upload CSV (active by default).
- Tab B: Spotify Web API (advanced, may be marked beta/deferred).
- Tab C: Help (expected format and troubleshooting).

3. CSV import panel
- File picker and drag-drop target.
- Expected columns summary.
- Start import button.

4. Progress and status panel
- Step indicator: Parse, Validate, Align, Complete.
- Row counters and status text.
- Cancel option while processing.

5. Validation and alignment diagnostics panel
- Rows total, valid, invalid.
- Alignment metrics by method.
- Unmatched sample list with reasons.
- Quality flag counts.

6. Influence tracks panel (optional)
- Add manual seed track rows: track name + artist name.
- Remove/edit controls.
- Help text on how influence tracks steer recommendations.

7. Confirmation panel
- Import summary and run identifiers.
- Continue button to next step.
- Re-upload action.

## 5. User Flow
1. User opens Import Data page.
2. User selects source (CSV default).
3. User uploads CSV file.
4. System performs pre-checks (size, encoding, header presence).
5. System parses and validates rows.
6. System aligns tracks using ISRC-first with metadata fallback.
7. UI displays diagnostics and unmatched examples.
8. User optionally adds influence tracks.
9. User confirms and proceeds to profile/settings.
10. System stores run metadata and observability log.

## 6. Data Contract Plan
Input fields required per event:
- master_metadata_track_name
- master_metadata_album_artist_name
- ts
- ms_played

Optional fields:
- master_metadata_album_album_name
- isrc
- platform

Normalized internal event model:
- event_id
- track_name
- artist_name
- album_name
- isrc
- played_at_utc
- ms_played
- source_platform
- ingest_run_id
- row_quality_flag

Influence track model:
- track_name
- artist_name
- album_name (optional)
- interaction_type set to influence
- signal_source set to user_manual

## 7. Validation Plan
Hard-fail rules:
- Missing track name.
- Missing artist name.
- Missing or invalid timestamp.
- Missing or invalid ms_played.
- Missing required CSV headers.

Soft-warning rules:
- Missing isrc.
- Outlier timestamps.
- Metadata normalization changes.

Encoding and structure checks:
- Prefer UTF-8; detect and convert common alternatives such as cp1252.
- Require header row and at least one data row.

Outcome policy:
- Allow partial success imports when valid rows exist.
- Block progression only when no usable rows remain.

## 8. Diagnostics and Observability Plan
Every import run should produce:
- run_id and ingest_run_id.
- rows_total, rows_valid, rows_invalid, rows_skipped.
- quality flag counts.
- alignment stats:
  - matched_total
  - matched_isrc
  - matched_metadata
  - matched_metadata_plus_duration
  - unmatched
  - match_rate
- unmatched sample rows with reason codes.
- run config snapshot:
  - dataset version
  - pipeline version
  - feature set used downstream

UI should display the most important metrics directly and provide expandable details for advanced inspection.

## 9. Integration Plan with Existing Implementation
Reuse where possible:
- Parser and schema normalization from BL ingestion work.
- Spotify API resilience flow for advanced import tab.
- Observability logging format already planned in implementation artifacts.

Proposed endpoint sequence:
1. POST /api/import/validate
2. POST /api/import/align
3. POST /api/import/commit
4. GET /api/import/:run_id/status

If backend remains partially deferred:
- Keep frontend contract stable.
- Implement temporary mock responses behind a feature flag.

## 10. Error Handling Plan
Must-have error states:
- File too large.
- Wrong encoding.
- Missing required columns.
- Zero valid rows.
- Low match rate warning.
- Full mismatch failure.
- Network/service timeout.

Each error state must provide:
- Plain-language reason.
- Suggested corrective action.
- Retry option without page refresh.

## 11. Security and Data Hygiene Plan
- Accept only allowed file types for CSV flow.
- Sanitize all user-provided text fields.
- Enforce file size limits and server-side re-validation.
- Avoid storing raw files longer than necessary.
- Store only required metadata and run diagnostics for reproducibility.

## 12. Accessibility and UX Quality Plan
- Keyboard-operable controls for all actions.
- Proper labels and aria-live for status updates.
- Focus management on validation failures.
- Clear color contrast for warning and error states.
- Mobile-first responsive behavior with stacked layout.

## 13. Delivery Phases
Phase 1: Frontend skeleton
- Build page layout and section placeholders.
- Wire source tabs and CSV upload UI.

Phase 2: Validation wiring
- Connect pre-checks and validation endpoint.
- Render status and diagnostics.

Phase 3: Alignment and observability wiring
- Connect alignment endpoint.
- Show unmatched samples and match metrics.
- Persist and display run identifiers.

Phase 4: Influence tracks and confirmation
- Add influence input/edit/remove UX.
- Add final summary and continue transition.

Phase 5: Advanced source path
- Enable Spotify Web API import tab from resilience module.

## 14. Acceptance Criteria
The Import Data page is accepted when:
1. User can upload a valid Spotify CSV and receive deterministic validation output.
2. User sees alignment summary with match rates and unmatched examples.
3. User can proceed with partial imports when valid rows exist.
4. User can add optional influence tracks.
5. Each run is traceable via run_id and stored observability metrics.
6. Core flow works on desktop and mobile with accessible interaction.

## 15. Open Risks and Mitigations
- Coverage mismatch with candidate corpus: expose match rate and unmatched details.
- Encoding variability: detect and auto-convert common encodings.
- Deferred scope controls: document as known limitation and retain API shape for BL-021.
- Large input performance: stream parsing and provide progress indicators.

## 16. Immediate Next Build Tasks
1. Add import page files under 07_implementation/website/.
2. Introduce import section routing from current website entry page.
3. Define API contract JSON examples in a companion integration note.
4. Implement frontend diagnostics renderer before backend integration.

## 17. Implementation Completion Checkpoint
Completed on 2026-03-22 in the website prototype:
- Import page UI with source tabs and CSV upload flow.
- Parse, validate, align, and diagnostics rendering flow.
- Optional influence tracks add/remove controls.
- Run summary output with generated run identifiers.

Implemented files:
- 07_implementation/website/index.html
- 07_implementation/website/style.css
- 07_implementation/website/app.js

Implementation log reference:
- 07_implementation/website.md
