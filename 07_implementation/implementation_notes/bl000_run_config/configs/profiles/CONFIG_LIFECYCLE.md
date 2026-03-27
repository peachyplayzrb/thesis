# Run Config Profile Lifecycle

Last updated: 2026-03-27
Schema: `run-config-v1`

## Purpose
Define lifecycle status for all profile files under this folder so operators can distinguish canonical, experimental, and historical profiles.

## Lifecycle States
- `canonical`: active baseline for implementation reporting and governance summaries
- `experimental`: active test profile, non-canonical until explicit promotion decision
- `historical-retained`: preserved for audit/replay traceability

## Current Status Map
- `run_config_ui013_tuning_v1.json`: historical-retained
- `run_config_ui013_tuning_v1a.json`: historical-retained
- `run_config_ui013_tuning_v1b.json`: historical-retained
- `run_config_ui013_tuning_v1c.json`: historical-retained
- `run_config_ui013_tuning_v1d.json`: historical-retained
- `run_config_ui013_tuning_v1e.json`: historical-retained
- `run_config_ui013_tuning_v1f.json`: canonical
- `run_config_ui013_tuning_v2a_retrieval_tight.json`: experimental

## Governance References
- D-033: sets `v1f` as canonical baseline and keeps `v2a` as experimental.
- C-184: evidence sync after 2026-03-27 v2a run wave.

## Operator Rule
Use only `v1f` for canonical implementation reporting unless a new promotion decision explicitly supersedes D-033.