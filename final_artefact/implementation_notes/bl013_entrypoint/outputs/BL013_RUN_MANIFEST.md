# BL-013 Run Manifest

Last updated: 2026-03-28
Scope: `07_implementation/implementation_notes/bl013_entrypoint/outputs`

## Purpose
Provide a compact index of dense BL-013 orchestration output waves so operators can map run IDs to intent quickly.

## Grouped Run Waves

### Wave A - Pre-canonical hardening and migration validation
- date range: 2026-03-24 to 2026-03-25
- profile mix: historical tuning and hardening passes
- representative runs:
  - `BL013-ENTRYPOINT-20260325-020526-881730`
  - `BL013-ENTRYPOINT-20260325-225113-845270`
- status: historical-retained

### Wave B - Canonical v1f evidence chain
- date range: 2026-03-26 to 2026-03-27
- profile: `run_config_ui013_tuning_v1f.json`
- representative runs:
  - `BL013-ENTRYPOINT-20260327-201712-508978`
  - `BL013-ENTRYPOINT-20260327-203411-538709`
- governance role: canonical reporting baseline evidence

### Wave C - Experimental v2a evidence wave
- date range: 2026-03-27
- profile: `run_config_ui013_tuning_v2a_retrieval_tight.json`
- representative runs:
  - `BL013-ENTRYPOINT-20260327-000046-113676`
  - `BL013-ENTRYPOINT-20260327-002121-545346`
- governance role: experimental comparison evidence (non-canonical)

## Active Pointer
- `bl013_orchestration_run_latest.json` points to the most recent run only.
- Treat this file as a convenience pointer, not historical inventory.

## Canonical Rule
Use D-033 policy when interpreting BL-013 runs:
- v1f chain for canonical reporting
- v2a chain for experimental analysis

## Maintenance
When new high-density run waves are created, append a new wave section with:
- date range
- active profile
- representative run IDs
- governance role
