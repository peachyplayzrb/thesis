# BL-000 State Log - Run Config

**Log Date:** 2026-03-25  
**Stage:** BL-000 (Run Config)  
**Primary Module:** `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`

---

## 1. Purpose
BL-000 run config provides the canonical configuration contract for BL-003 through BL-009. It defines defaults, merges optional overrides, enforces cross-stage constraints, and emits canonical run-config artifacts (`run_intent`, `run_effective_config`) for traceability.

## 2. Current Active Contract
Schema and artifacts:
- Run-config schema version: `run-config-v1`
- Intent artifact schema: `run-intent-v1`
- Effective artifact schema: `run-effective-config-v1`

Config-governance surface (new on 2026-03-25):
- `control_mode.validation_profile` (`strict` | `explore`)
- `control_mode.allow_threshold_decoupling` (bool)
- `control_mode.allow_weight_auto_normalization` (bool)
- `observability_controls.bootstrap_mode` (bool)

Canonical configuration surfaces:
- Template: `07_implementation/implementation_notes/bl000_run_config/configs/templates/run_config_template_v1.json`
- Resolver/validator module: `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`
- Semantic operator map: `07_implementation/implementation_notes/bl000_run_config/docs/semantic_control_map.md`

Canonical artifact outputs:
- `07_implementation/implementation_notes/bl000_run_config/outputs/run_intent_<timestamp>.json`
- `07_implementation/implementation_notes/bl000_run_config/outputs/run_effective_config_<timestamp>.json`
- `07_implementation/implementation_notes/bl000_run_config/outputs/run_intent_latest.json`
- `07_implementation/implementation_notes/bl000_run_config/outputs/run_effective_config_latest.json`

## 3. Stage Wiring Status (Implementation)
Current implementation uses `BL_RUN_CONFIG_PATH` environment propagation from BL-013 into downstream stages.

Observed consumers:
- BL-003: `build_bl003_ds001_spotify_seed_table.py` (`resolve_input_scope_controls`, `resolve_bl003_influence_controls`, `resolve_bl003_seed_controls`)
- BL-004: `build_bl004_preference_profile.py` (`resolve_bl004_controls`)
- BL-005: `build_bl005_candidate_filter.py` (`resolve_bl005_controls`)
- BL-006: `build_bl006_scored_candidates.py` (`resolve_bl006_controls`)
- BL-007: `build_bl007_playlist.py` (`resolve_bl007_controls`)
- BL-008: `build_bl008_explanation_payloads.py` (`resolve_bl008_controls`)
- BL-009: `build_bl009_observability_log.py` (`resolve_bl009_controls`, `resolve_input_scope_controls`)

Entrypoint propagation:
- `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py`
  - accepts `--run-config`
  - sets `BL_RUN_CONFIG_PATH` in stage environment

## 4. Validation and Invariant Enforcement (Current)
`run_config_utils.py` currently enforces the following behaviors:
- Schema guard: rejects unsupported `schema_version`
- Type coercion and fallback defaults for user/input/profile/retrieval/scoring/assembly/transparency/observability controls
- Positive-threshold enforcement for numeric threshold maps
- Positive float enforcement for `assembly_controls.min_score_threshold`
- Component-weight validation: numeric, non-negative, and sum-to-1.0 within tolerance (`+/- 0.01`)
- Retrieval-scoring numeric threshold coupling: retrieval and scoring threshold maps must match exactly
- Profile-retrieval constraints:
  - `retrieval.profile_top_tag_limit <= profile.top_tag_limit`
  - `retrieval.profile_top_genre_limit <= profile.top_genre_limit`
  - `retrieval.profile_top_lead_genre_limit <= profile.top_lead_genre_limit`

Control-mode behavior notes:
- `strict` profile keeps threshold-coupling and strict weight-sum validation enabled.
- `allow_threshold_decoupling=true` permits retrieval/scoring numeric threshold maps to differ.
- `allow_weight_auto_normalization=true` permits component weights to sum outside `1.0 +/- 0.01` and defers normalization warning behavior to BL-006 runtime diagnostics.
- BL-009 bootstrap metadata is now control-driven through run-config (`observability_controls.bootstrap_mode`) rather than hardcoded.

## 5. Artifact Evidence (2026-03-25)
Core run-config files:
- `configs/templates/run_config_template_v1.json`
  - size_bytes: `3663`
  - sha256: `EDC39CE8D50A943419E7BF38935D790CFDE2EAC14389AD1ADC68C99D695C54AD`
- `outputs/run_config_profile_test_threshold_015.json`
  - size_bytes: `2811`
  - sha256: `06D57DA824590B07040D2471274CEF8E1EE75BFB6CDEF59723705AABC0B18895`
- `configs/profiles/run_config_bl021_probe_v1.json`
  - size_bytes: `429`
  - sha256: `B2157835E1C854E13961CABDC049B32486E076F65C497E70E1211C1511EA75FB`
- `configs/profiles/run_config_bl021_probe_v2.json`
  - size_bytes: `459`
  - sha256: `31E4117A5D4DD334A6F7A738BB026559BD9DE90A455654C059E006D36582C8B1`
- `run_config_utils.py`
  - size_bytes: `33986`
  - sha256: `C879DFC58778D2BF9FA6B5BE112378B69FD6E9669F74BEC5C6E117AB54CABF1E`
- `docs/semantic_control_map.md`
  - size_bytes: `14039`
  - sha256: `0EC2CDEB8F599280E822C63763BF92C19F02C3F6C8033C9D347857702F49DF11`

Latest canonical artifact pair:
- `outputs/run_intent_latest.json`
  - mtime_utc: `2026-03-25T17:34:09Z`
  - artifact_type: `run_intent`
  - artifact_schema_version: `run-intent-v1`
  - run_id: `BL013-ENTRYPOINT-20260325-173409-100435`
  - sha256: `F1D0F50C07C7598D96C8C84BFE01ADE02D5914EC11A956C28B0819A9A5078FB9`
- `outputs/run_effective_config_latest.json`
  - mtime_utc: `2026-03-25T17:34:09Z`
  - artifact_type: `run_effective_config`
  - artifact_schema_version: `run-effective-config-v1`
  - run_id: `BL013-ENTRYPOINT-20260325-173409-100435`
  - sha256: `58F55650EC0E029AEBB3A983BD90DC8971D61F6C56E2BD99B9ECE6B207D81563`

Latest artifact intent source:
- mode: `explicit_run_config`
- run_config_path: `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_bl021_probe_v2.json`

## 6. Known Contract Notes / Caveats
1. Resolved on 2026-03-25: `seed_controls.match_rate_min_threshold` is now canonicalized through `run_config_utils.py`.
2. BL-003 now resolves match-rate threshold via shared resolver controls (not direct raw JSON extraction).
3. Effective-config artifacts now include normalized `seed_controls`, removing the prior template-vs-canonicalization inconsistency.

Operational impact:
- No blocking issues detected in current run-config contract behavior.
- Prior `seed_controls` normalization caveat is closed.
- Config-driven control/governance surface is now explicit in the schema, reducing hardcoded behavior in downstream observability semantics.

## 7. Completion Validation (This Log Update)
Checks executed for this state log:
1. File inventory and hash audit across run-config core files and outputs.
2. Canonical latest artifact pair inspection (`run_intent_latest`, `run_effective_config_latest`) including schema versions and run_id.
3. Static wiring scan across BL-003..BL-009 and BL-013 for resolver usage and `BL_RUN_CONFIG_PATH` propagation.
4. Resolver-level invariant review in `run_config_utils.py` (schema, thresholds, coupling, profile-vs-retrieval limits, component weights).

## 8. Conclusion
BL-000 run config is operational, wired through the active BL-013 to BL-009 path, and has current canonical artifact evidence for the latest run. No blocking issue was found for run-config operation under the current contract, and the previous `seed_controls` normalization inconsistency has been remediated.

## 9. UI-013 Delta Update (2026-03-25 23:00 UTC)
Objective:
- Complete focused BL-008 explanation-diversity control uplift through run-config without introducing hardcoded selection logic.

Implemented control-surface additions:
- `transparency_controls.blend_primary_contributor_on_near_tie` (bool)
- `transparency_controls.primary_contributor_tie_delta` (non-negative float)

Resolver and normalization status:
- `run_config_utils.py` now canonicalizes both fields in effective config resolution and exposes them through `resolve_bl008_controls`.
- BL-008 runtime now consumes these controls from run-config when `BL_RUN_CONFIG_PATH` is set.

Validated profile and runtime evidence:
- Active tuned profile: `configs/profiles/run_config_ui013_tuning_v1b.json`
- Effective transparency controls in latest validated run:
  - `top_contributor_limit=3`
  - `blend_primary_contributor_on_near_tie=true`
  - `primary_contributor_tie_delta=0.09`

Latest canonical artifact pair (focused validation run):
- `outputs/run_intent_latest.json`
  - run_id: `BL013-ENTRYPOINT-20260325-225725-328263`
- `outputs/run_effective_config_latest.json`
  - run_id: `BL013-ENTRYPOINT-20260325-225725-328263`

Outcome linkage:
- BL-008 top-label dominance share reduced to `0.5` on v1b-focused rerun, satisfying UI-013 target (`<= 0.6`) while BL-014 remains pass.

---

## 10. Structural Cleanup and Validation Update (2026-03-26)
Objective:
- Clean and harden BL-000 resolver/writer behavior while preserving the active run-config contract.

Implemented refactor and issue fixes:
- `run_config_utils.py` cleanup:
  - Added package/direct-script fallback import for shared write utility (`open_text_write`) to improve execution parity.
  - Extracted `_coerce_min_positive_float` and used it for ingestion float controls to prevent `ValueError` crashes on malformed numeric input and preserve safe defaults.
  - Extracted `_normalize_allowed_tokens` and applied it to list controls (`input_scope.top_time_ranges`, `interaction_scope.include_interaction_types`) with stable-order de-duplication.
  - De-duplicated `influence_tracks.track_ids` during canonicalization to prevent redundant downstream influence processing.
  - Migrated run-config artifact writes (`run_intent*`, `run_effective_config*`) to shared Windows-safe writer path.

Contract impact:
- No schema change (`run-config-v1` unchanged).
- No control-surface removal.
- Invariant enforcement (threshold coupling, profile/retrieval limits, component-weight checks) remains intact.

Validation evidence:
- BL-000 direct smoke check (resolver + artifact writer): pass
  - run_id: `BL000-SMOKE-20260326-REF`
  - artifacts written:
    - `outputs/run_intent_20260326-060435-501919.json`
    - `outputs/run_effective_config_20260326-060435-501919.json`
- BL-013 orchestration after BL-000 cleanup: pass
  - run_id: `BL013-ENTRYPOINT-20260326-060416-877007`
  - failed_stage_count: `0`
- BL-014 active freshness suite after BL-000 cleanup: pass
  - run_id: `BL-FRESHNESS-SUITE-20260326-060441`
  - checks_passed: `7/7`

Status:
- BL-000 run-config remains operational and downstream-compatible.
- Cleanup closed with no observed regressions in BL-013/BL-014 validation path.

## Update - 2026-03-26 19:15 UTC (Current Pipeline Sync)

### Current Active Evidence
- Latest canonical run-config artifacts now point to the explicit v1b profile run:
  - BL-013 run_id: `BL013-ENTRYPOINT-20260326-191529-313858`
  - `run_intent_latest.json` generated_at_utc: `2026-03-26T19:15:29Z`
  - `run_effective_config_latest.json` generated_at_utc: `2026-03-26T19:15:29Z`
- Latest explicit config path:
  - `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1b.json`

### Effective Control Snapshot
- profile limits: top_genre `10`, top_lead_genre `10`, top_tag `10`
- retrieval thresholds: tempo `15.0`, key `1.5`, mode `0.5`, duration_ms `30000.0`
- scoring weights: lead_genre `0.23`, genre_overlap `0.19`, tag_overlap `0.23`, tempo `0.12`
- transparency controls: near-tie blending enabled, tie delta `0.09`

### Status
- BL-000 run-config is current, actively driving the latest orchestration run, and remains consistent with downstream BL-003 through BL-009 evidence.

## Update - 2026-03-26 21:03 UTC (v1f Baseline Promotion)

### Current Active Evidence
- Latest canonical run-config artifacts now point to the explicit v1f profile run:
  - BL-013 run_id: `BL013-ENTRYPOINT-20260326-210305-914179`
  - `run_intent_latest.json` generated_at_utc: `2026-03-26T21:03:05Z`
  - `run_effective_config_latest.json` generated_at_utc: `2026-03-26T21:03:05Z`
- Latest explicit config path:
  - `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json`

### Effective Control Snapshot
- profile limits: top_genre `10`, top_lead_genre `10`, top_tag `10`
- retrieval thresholds: danceability `0.15`, energy `0.15`, valence `0.15`, tempo `15.0`, key `1.5`, mode `0.5`, duration_ms `30000.0`
- retrieval keep rule: `semantic_score >= 3 or (semantic_score >= 1 and numeric_pass_count >= 4)`
- scoring weights: danceability `0.04`, energy `0.03`, valence `0.03`, tempo `0.03`, duration_ms `0.02`, key `0.02`, mode `0.01`, lead_genre `0.29`, genre_overlap `0.24`, tag_overlap `0.29`
- transparency controls: near-tie blending enabled, tie delta `0.09`

### Status
- BL-000 run-config is current, and the active canonical contract now reflects the post-seven-feature BL-005 retune (`v1f`) rather than the earlier v1b/v1d snapshots.

## Update - 2026-03-27 (Alignment Lock)

### Baseline classification
- canonical active baseline: `configs/profiles/run_config_ui013_tuning_v1f.json`
- experimental profile: `configs/profiles/run_config_ui013_tuning_v2a_retrieval_tight.json`
- historical references: earlier v1/v1a/v1b/v1d/v1e iterations remain for traceability only

### Operational reporting rule
- Implementation reporting and governance snapshots must cite v1f evidence when stating current behavior.
- v2a can be cited only as experimental tuning context unless explicitly promoted by a new decision record.

### Evidence pointers
- latest integrated v1f chain tracked in backlog:
  - BL-013: `BL013-ENTRYPOINT-20260326-215741-269303`
  - BL-010: `BL010-REPRO-20260326-215557`
  - BL-011: `BL011-CTRL-20260326-215213`
  - BL-014: `BL014-SANITY-20260326-215415-562794`
  - freshness suite: `BL-FRESHNESS-SUITE-20260326-215416`
