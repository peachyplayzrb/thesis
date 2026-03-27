# Run Config Output Retention Policy

Last updated: 2026-03-27
Scope: `07_implementation/implementation_notes/bl000_run_config/outputs`

## Purpose
Control growth of timestamped `run_intent_*` and `run_effective_config_*` artifacts while preserving reproducibility and auditability.

## Policy (Docs-Only In This Pass)
- Keep `*_latest.json` pointers always.
- Keep timestamped artifacts for the recent active window (recommended: 30 days).
- Keep at least one canonical snapshot set for each governance-significant baseline family:
  - canonical v1f
  - experimental v2a
- Archive (do not hard-delete) older timestamped artifacts outside the active window.

## Archive Requirements
Any archive execution pass must produce:
- a move manifest mapping source to archive destination
- a validation report confirming retained canonical and latest pointers
- a rollback plan

## Governance Rule
Retention execution is operational work and must be logged in `00_admin/change_log.md` with affected path scope and manifest reference.

## Current Pass Note
This policy is documented only in the current pass. No run-config output files were deleted or moved here.