# Codebase Issues (Current Snapshot)

Last updated: 2026-03-26

## Scope
This report summarizes known structural, maintenance, and cleanup issues in the active implementation pipeline under `07_implementation/implementation_notes`.

## Resolved In This Refactor Pass
- Centralized Windows-safe text write handling into shared utility:
  - `bl000_shared_utils/io_utils.py` (`open_text_write`)
- Removed duplicated local file-write retry logic from:
  - `bl004_profile/build_bl004_preference_profile.py`
  - `bl005_retrieval/build_bl005_candidate_filter.py`
  - `bl000_shared_utils/report_utils.py` now uses shared helper
- Simplified BL-014 runner interface to active-mode only:
  - Removed `--allow-legacy-surrogate-inputs` option from `bl014_quality/run_bl014_quality_suite.py`
  - Removed legacy branch handling in BL-014 freshness computation
- Removed legacy surrogate support from BL-010 and BL-011 runners:
  - `bl010_reproducibility/run_bl010_reproducibility_check.py` now active-only
  - `bl011_controllability/run_bl011_controllability_check.py` now active-only
- Removed legacy surrogate support from BL-009 observability:
  - `bl009_observability/build_bl009_observability_log.py` now active-only for ingestion/source diagnostics
- Added BL-014 freshness auto-refresh fallback:
  - Automatically reruns BL-010 and BL-011 once when freshness evidence is stale
  - Reruns freshness checks after refresh and reports refresh outputs in suite report
- Refactored BL-014 quality runner for clearer structure and stronger check semantics:
  - Extracted freshness input path and path-validation helpers
  - Extracted BL-011 contract reconstruction helper used by freshness mode
  - Corrected `bl010_bl011_freshness_auto_refresh` check to fail when refresh is attempted but not successful
- Refactored BL-013 entrypoint runner for cleaner orchestration control flow:
  - Centralized summary finalization and early-failure exit handling
  - Normalized missing-script failure payload shape to match standard stage result schema
- Refactored BL-011 controllability runner for cleaner structure and safer comparisons:
  - Extracted helper functions for seed event construction, baseline comparison payloads, and result aggregation
  - Fixed baseline top-10 overlap computation to use actual baseline length instead of hardcoded value
- Refactored BL-010 reproducibility runner for cleaner execution flow and runtime configurability:
  - Added CLI controls for replay count, python executable, and output directory
  - Extracted replay execution helper flow and added replay-count guard validation
  - Fixed snapshot replay-count reference regression after constant rename
- Refactored BL-009 observability runner for clearer structure and safer metadata emission:
  - Extracted helpers for required-path validation, canonical config artifact resolution, and artifact map generation
  - Fixed run-index `bootstrap_mode` to reflect runtime control value instead of hardcoded constant
- Refactored BL-008 transparency payload builder for cleaner structure and safer parsing:
  - Extracted helpers for required-path validation, CSV indexing, component ordering, and score-breakdown assembly
  - Added resilient numeric coercion to avoid runtime conversion failures on malformed optional fields
- Closed BL-008 post-refactor validation and logging:
  - BL-008 direct run pass (`BL008-EXPLAIN-20260326-052513-764269`)
  - BL-013 orchestration pass (`BL013-ENTRYPOINT-20260326-052501-025267`)
  - BL-014 active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-052516`)
- Refactored BL-007 playlist assembly runner for clearer structure and safer input handling:
  - Extracted helper functions for required-path checks, CSV contract validation, safe numeric parsing, and decision evaluation
  - Switched BL-007 trace CSV write path to shared Windows-safe writer utility
- Closed BL-007 post-refactor validation and logging:
  - BL-007 direct run pass (`BL007-ASSEMBLE-20260326-053211-780037`)
  - BL-013 orchestration pass (`BL013-ENTRYPOINT-20260326-053201-347874`)
  - BL-014 active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-053216`)
- Refactored BL-006 scoring runner for cleaner structure and safer artifact handling:
  - Added explicit required-input checks for BL-004 profile and BL-005 filtered candidates
  - Replaced BL-006 direct output write-open paths with shared Windows-safe writer utility
  - Removed unused/dead BL-006 main-script paths to simplify scoring orchestration
- Fixed BL-006 semantic-weight extraction fidelity:
  - BL-006 now uses BL-004 provided semantic weights for top genres/tags (normalized) instead of flattening to uniform weights
  - Uniform semantic weighting remains only as a fallback when explicit profile weights are absent
- Closed BL-006 post-refactor validation and logging:
  - BL-006 direct run pass (`BL006-SCORE-20260326-053525-674160`)
  - BL-013 orchestration pass (`BL013-ENTRYPOINT-20260326-053436-692830`)
  - BL-014 active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-053641`)
- Refactored BL-005 retrieval runner for cleaner setup and safer contract handling:
  - Added explicit required-input checks for BL-004 profile/seed trace and DS-001 candidate corpus
  - Extracted helpers for normalized profile-label set construction and active numeric-spec resolution
  - Standardized BL-005 decisions CSV headers via explicit field constant
- Fixed BL-005 robustness issues:
  - Added explicit guard for empty candidate corpus to avoid header/index crashes during output writing
  - Normalized profile semantic labels to lowercase to align with candidate label normalization and avoid case-driven mismatch drift
  - Removed unused BL-005 parser helper/import paths from active retrieval flow
- Closed BL-005 post-refactor validation and logging:
  - BL-005 direct run pass (`BL005-FILTER-20260326-053938-993374`)
  - BL-013 orchestration pass (`BL013-ENTRYPOINT-20260326-053855-098200`)
  - BL-014 active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-054106`)
- Refactored BL-004 profile builder for cleaner structure and safer edge-case handling:
  - Removed unused BL-004 helper/import paths from active profile build flow
  - Added explicit fail-fast guard when interaction-type filtering yields zero retained seed events
  - Hardened summary feature-center projection to skip unavailable numeric keys safely
- Closed BL-004 post-refactor validation and logging:
  - BL-004 direct run pass (`BL004-PROFILE-20260326-054338-122956`)
  - BL-013 orchestration pass (`BL013-ENTRYPOINT-20260326-054256-908316`)
  - BL-014 active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-054458`)
- Refactored BL-003 alignment runner for cleaner output flow and safer write handling:
  - Consolidated repeated CSV output logic behind a shared helper in BL-003 script
  - Replaced BL-003 direct output writes with shared Windows-safe writer utility
  - Removed unused BL-003 imports/dead parsing paths from active alignment flow
- Fixed BL-003 influence diagnostics robustness:
  - Deduplicated configured influence-track IDs before injection to prevent inflated injected-count reporting
- Closed BL-003 post-refactor validation and logging:
  - BL-003 direct run pass (`generated_at_utc=2026-03-26T05:48:25Z`)
  - BL-013 orchestration pass (`BL013-ENTRYPOINT-20260326-054826-307704`)
  - BL-014 active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-054838`)
- Refactored BL-001/BL-002 ingestion runtime support paths for safer execution and output handling:
  - Added package/direct-script import fallback coverage across active ingestion modules
  - Standardized ingestion JSON/JSONL/CSV write paths on shared Windows-safe writer utility
  - Preserved BL-001 schema/contract semantics (no field-policy drift)
- Fixed BL-002 playlist-item accounting robustness:
  - Deduplicated playlist IDs before playlist item retrieval to prevent inflated item counts from repeated playlist fetches
- Closed BL-001/BL-002 post-refactor validation and logging:
  - BL-002 export pass (`SPOTIFY-EXPORT-20260326-055521-905674`)
  - BL-003 direct alignment pass (`generated_at_utc=2026-03-26T05:58:25Z`)
  - BL-013 orchestration pass (`BL013-ENTRYPOINT-20260326-055823-959260`)
  - BL-014 active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-060021`)
- Refactored BL-000 run-config resolver and artifact writer for cleaner structure and safer runtime behavior:
  - Added helperized coercion for positive float controls to avoid malformed-input conversion crashes in ingestion controls
  - Added stable-order de-dup normalization helpers for list-valued controls
  - Deduplicated configured influence track IDs in canonicalized effective config
  - Standardized BL-000 artifact writes on shared Windows-safe writer utility
- Closed BL-000 post-refactor validation and logging:
  - BL-000 resolver/artifact smoke check pass (`BL000-SMOKE-20260326-REF`)
  - BL-013 orchestration pass (`BL013-ENTRYPOINT-20260326-060416-877007`)
  - BL-014 active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-060441`)

## Current Known Issues

### 1) Freshness Coupling Between BL-010/BL-011 and BL-014
Severity: Low

Details:
- BL-014 now auto-refreshes BL-010/BL-011 once when stale evidence is detected.
- First freshness pass may still fail before auto-refresh recovery in the same run.

Recommended action:
- Optionally add a stricter preflight message that explicitly announces stale evidence before refresh.

### 2) Direct Path.open Calls Still Exist Across Wider Codebase
Severity: Medium

Details:
- We hardened core failing paths and shared report writing.
- Some remaining stage scripts may still use direct `Path.open("w")` without shared wrapper.
- Historical evidence: BL-013 run `BL013-ENTRYPOINT-20260326-051352-588315` failed at BL-006 with
  `OSError: [Errno 22] Invalid argument` on direct write open for
  `07_implementation/implementation_notes/bl006_scoring/outputs/bl006_scored_candidates.csv`.
- Current status: latest BL-013 run `BL013-ENTRYPOINT-20260326-052501-025267` is pass.

Recommended action:
- Sweep all write paths and standardize on `io_utils.open_text_write`.
- Keep read paths unchanged unless they show instability.

### 3) Large Artifact Churn In Working Tree
Severity: Low

Details:
- Quality/reproducibility stages regenerate many artifacts each run.
- This makes diffs noisy and slows reviews.

Recommended action:
- Consider splitting generated outputs into a dedicated ignored directory for local runs.
- Keep only canonical reports/matrices tracked if required for thesis evidence.

### 4) Pylance Workspace Configuration Not Found
Severity: Info

Details:
- No workspace `.vscode/settings.json` or pyright config file was found in this repo snapshot.
- No workspace-level Pylance/pyright settings were available to remove.

Recommended action:
- If Pylance is enabled globally in your editor profile, disable it in user settings.
- If you want repo-enforced behavior, add a workspace settings file explicitly and set desired Python analysis provider.

## Operational Health Snapshot (After Refactor)
- BL-013 orchestration: pass
- BL-010 reproducibility: pass
- BL-011 controllability: pass
- BL-014 active freshness suite: pass
- BL-002 ingestion export: pass
- BL-003 alignment (latest direct run): pass
- BL-000 run-config resolver/artifact writer: pass
