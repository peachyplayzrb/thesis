# High-Risk Regression Run Result (2026-03-25)

Reference checklist:
- 00_admin/ops_logs/high_risk_regression_checklist_2026-03-25.md

## Outcome Summary
- Final status: pass
- Initial blockers found: 2
- Resolved blockers: 2
- Code logic regressions found: 0

## Blockers Encountered and Resolution

1. Invocation wiring issue (non-regression)
- Symptom: direct script invocation for BL-002 failed with relative import error.
- Cause: script requires module mode when called from repo root.
- Resolution: used module invocation for BL-002.

2. Pipeline continuity break (state mismatch)
- Symptom: BL-014 failed (18/21) and freshness suite failed after BL-003/BL-004 rerun.
- Cause: upstream artifacts were refreshed without regenerating BL-005..BL-009, causing hash/run-id continuity mismatches.
- Resolution: reran BL-013 via the correct entrypoint script, then reran BL-014 and freshness.

## Final Gate Status

- Gate 1 (BL-002 ingestion/cache namespace): pass
  - observed cache namespace format includes uid:<spotify_user_id>
- Gate 2 (BL-003 alignment + missing source behavior): pass
  - missing_selected_sources includes recently_played and allow_missing_selected_sources=true
- Gate 3 (BL-004 user_id inference): pass
  - BL-004 user_id matches ingestion spotify_user_id
- Gate 4 (BL-013 orchestration continuity): pass
  - executed_stage_count=6, failed_stage_count=0
- Gate 5 (BL-014 + freshness): pass
  - BL-014: 21/21
  - active freshness suite: pass

## Key Evidence Pointers

- BL-002 summary:
  - 07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_export_run_summary.json
- BL-003 summary:
  - 07_implementation/implementation_notes/alignment/outputs/bl003_ds001_spotify_summary.json
- BL-004 summary:
  - 07_implementation/implementation_notes/profile/outputs/bl004_profile_summary.json
- BL-013 latest:
  - 07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_latest.json
- BL-014 report:
  - 07_implementation/implementation_notes/quality/outputs/bl014_sanity_report.json
- Active freshness report:
  - 07_implementation/implementation_notes/quality/outputs/bl_active_freshness_suite_report.json

## Follow-up Fix Applied to Checklist
- Updated BL-013 command in checklist to the actual script:
  - run_bl013_pipeline_entrypoint.py
