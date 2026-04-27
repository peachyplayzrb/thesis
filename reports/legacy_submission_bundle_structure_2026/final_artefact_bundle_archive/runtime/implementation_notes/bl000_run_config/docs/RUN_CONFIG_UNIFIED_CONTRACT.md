# Run Config Unified Contract

Last updated: 2026-03-27
Schema version: run-config-v1

## Purpose
This document is the canonical operator-facing contract for run-config structure, semantic control groups, profile organization, and validation constraints.

This file consolidates guidance previously split across:
- semantic_control_map.md
- run_config_profile_organization_guide.md
- bl000_run_config_state_log_2026-03-25.md

## Canonical Section Order
1. schema_version
2. user_context
3. input_scope
4. interaction_scope
5. influence_tracks
6. seed_controls
7. profile_controls
8. retrieval_controls
9. scoring_controls
10. assembly_controls
11. transparency_controls
12. observability_controls

## Semantic Control Groups
1. Input Composition: input_scope, interaction_scope, influence_tracks (BL-003, BL-004)
2. Seed Gate: seed_controls (BL-003)
3. Profile Construction: profile_controls (BL-004)
4. Retrieval Filtering: retrieval_controls (BL-005)
5. Scoring: scoring_controls (BL-006)
6. Playlist Assembly: assembly_controls (BL-007)
7. Transparency: transparency_controls (BL-008)
8. Observability: observability_controls (BL-009)

## Validation Constraints
- schema_version must be run-config-v1.
- retrieval_controls.numeric_thresholds must match scoring_controls.numeric_thresholds.
- retrieval profile limits must not exceed profile_controls limits.
- scoring component weights must sum to 1.0 within configured tolerance.
- threshold coupling and strict-validation guardrails must remain enforced by resolver logic.

## Retrieval Extensions (BL-005)
- `retrieval_controls.language_filter_enabled`: optional hard-gate toggle.
- `retrieval_controls.language_filter_codes`: optional allowed language list.
- `retrieval_controls.recency_years_min_offset`: optional recency hard-gate offset.
- `retrieval_controls.numeric_thresholds.release_year`: optional release-year proximity threshold.

Note: `scoring_controls.numeric_thresholds.release_year` is retained for threshold-coupling compatibility.

## Profile Organization
- Create new profiles from template first, then modify only intended scenario controls.
- Keep canonical, experimental, and historical profile categorization aligned with configs/profiles/CONFIG_LIFECYCLE.md.
- Promote a profile to canonical baseline only after evidence chain validation in BL-013/BL-010/BL-011/BL-014.

## Command Context
For active run commands and both execution contexts, use:
- 07_implementation/RUN_GUIDE.md

## Related References
- Profile inventory and lifecycle: 07_implementation/implementation_notes/bl000_run_config/configs/profiles/CONFIG_LIFECYCLE.md
- Retention details: 07_implementation/implementation_notes/bl000_run_config/outputs/RUN_CONFIG_RETENTION_POLICY.md
- Baseline authority: 07_implementation/ACTIVE_BASELINE.md
