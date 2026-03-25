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

## 5. Artifact Evidence (2026-03-25)
Core run-config files:
- `configs/templates/run_config_template_v1.json`
  - size_bytes: `2875`
  - sha256: `50CA44EA049B708061DB07B5215DB604ABE170EB0DF70997EBF2E9A687FD2AF6`
- `configs/profiles/run_config_bl021_probe_v1.json`
  - size_bytes: `429`
  - sha256: `B2157835E1C854E13961CABDC049B32486E076F65C497E70E1211C1511EA75FB`
- `configs/profiles/run_config_bl021_probe_v2.json`
  - size_bytes: `459`
  - sha256: `31E4117A5D4DD334A6F7A738BB026559BD9DE90A455654C059E006D36582C8B1`
- `run_config_utils.py`
  - size_bytes: `29883`
  - sha256: `806CE24A438913E1DE08A48D2A6B7F04E547600483AEEA7A2D5734504269CDF7`
- `docs/semantic_control_map.md`
  - size_bytes: `13218`
  - sha256: `821C750BD06E8D86C61CC33F0EB63E38DFB2966BECE93A722C493A1A2AED2FE5`

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

## 7. Completion Validation (This Log Update)
Checks executed for this state log:
1. File inventory and hash audit across run-config core files and outputs.
2. Canonical latest artifact pair inspection (`run_intent_latest`, `run_effective_config_latest`) including schema versions and run_id.
3. Static wiring scan across BL-003..BL-009 and BL-013 for resolver usage and `BL_RUN_CONFIG_PATH` propagation.
4. Resolver-level invariant review in `run_config_utils.py` (schema, thresholds, coupling, profile-vs-retrieval limits, component weights).

## 8. Conclusion
BL-000 run config is operational, wired through the active BL-013 to BL-009 path, and has current canonical artifact evidence for the latest run. No blocking issue was found for run-config operation under the current contract, and the previous `seed_controls` normalization inconsistency has been remediated.
