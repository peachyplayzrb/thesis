# Run Config Profile Organization Guide

Legacy note (2026-03-27): this document is retained as focused profile-organizing reference. Canonical unified run-config contract now lives in RUN_CONFIG_UNIFIED_CONTRACT.md.

Date: 2026-03-25
Scope: BL-000 run-config profile files in configs/profiles.

## Goal
Keep all run-config profiles easy to compare and audit by using a single section order and explicit structure.

## Standard Section Order
Use this order for every profile JSON:
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

## Profile Intent
- configs/profiles/run_config_bl021_probe_v1.json:
  - narrow sampling probe (more restrictive input_scope)
- configs/profiles/run_config_bl021_probe_v2.json:
  - wider sampling probe (less restrictive input_scope)

## Editing Rule
When making a new profile, copy from the template and only change the fields you intentionally tune for the scenario.

## Validation Rule
Before use, ensure:
- schema_version is run-config-v1
- retrieval_controls.numeric_thresholds matches scoring_controls.numeric_thresholds
- retrieval profile limits do not exceed profile_controls limits
- scoring component weights sum to 1.0 (within allowed tolerance)
