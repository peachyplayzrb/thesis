# Friend Handoff Playbook

Last updated: 2026-03-29 (00_admin full synchronization wave C-220)

## Purpose
This file gives a collaborator the exact way to use chat in this thesis repo so work quality, logging, and governance remain consistent.

## Start Here (Read In Order)
1. `00_admin/thesis_state.md`
2. `00_admin/operating_protocol.md`
3. `.github/copilot-instructions.md`
4. `07_implementation/backlog.md`
5. `07_implementation/experiment_log.md`
6. `00_admin/change_log.md`
7. `00_admin/decision_log.md`
8. `00_admin/unresolved_issues.md`

## Session Start Behavior (Automatic)
No special first message is required.

The workspace instructions are configured so the AI must run the full session-start checklist automatically before implementation, writing, or research updates begin.

Optional first message (still useful):
"Session start checklist and continue from highest-priority open item."

## Working Message Pattern
Use one of these patterns for every task:

1. "Plan BL-XXX, implement it, run checks, and log everything."
2. "Continue from unresolved issue UI-XXX and log everything."
3. "Do a full logging pass for this session before we end."

## Non-Negotiable Rules
1. Do not change title, research question, scope, or methodology without explicit approval.
2. Every implementation item moved to in-progress or done must have:
   - one `EXP-XXX` run entry,
   - one `C-###` change-log entry,
   - backlog status update.
3. Every implementation run must include deterministic repeat checking and recorded result.
4. If a fact changes an earlier assumption, update the existing admin/source file in the same session.
5. End every session with a "log everything" pass.

## Current Priority Queue (At Handoff)
All in-repo implementation and QC tasks are complete. No active unresolved issues exist.
1. External submission packaging: Canvas deadline, cover/declaration template, Turnitin package assembly.
2. Final formatting and submission constraint compliance check (see `09_quality_control/chapter_readiness_checks.md`).
3. Viva/demo preparation.

Current sprint state note: 7-day mentor-ready sprint (WP-DRAFT-001) is complete as of 2026-03-29. 00_admin synchronization wave C-220 is the last in-repo admin action before physical submission.
Governance sync note: all unresolved issues (UI-001 through UI-013) are closed. Canonical baseline is v1f. Architecture migration wave (C-204 through C-218) is complete. Documentation sync C-219 is complete.

## Clean-Code Status (2026-03-28)
Final-artefact clean-code pass is complete (C-192). All phases done:
- F1–F4: shared utilities, hashing, parsing, import standardization.
- F5/G1: dead `sha256_direct` removed; `sha256_of_values` canonical in `shared_utils/hashing.py`; BL-009 observability resolver migrated to `resolve_stage_controls` factory.
- Tests: 171/171 pass. New `test_observability_runtime_controls.py` added.
- G2 deferred (BL-004 profile resolver, BL-011 controllability resolver) per D-039 — complex env-parsing logic, low submission benefit.

## Technical Snapshot (Before Chat Switch)
1. Canonical implementation baseline: v1f (`run_config_ui013_tuning_v1f.json`, D-033).
2. Active canonical orchestration reference: `BL013-ENTRYPOINT-20260327-201712-508978` (pass).
3. Active canonical sanity: `BL014-SANITY-20260327-201731-408637` (22/22 pass).
4. Active canonical reproducibility: `BL010-REPRO-20260327-201949` (`deterministic_match=true`, 3 replays).
5. Active canonical controllability: `BL011-CTRL-20260327-202057` (`all_variant_shifts_observable=true`, 5 scenarios).
6. Active freshness suite: `BL-FRESHNESS-SUITE-20260327-201942` (19/19 pass).
7. Architecture migration complete: BL-003 through BL-007 now have typed stage classes + models with controllable-logic uplifts (C-205 through C-218); pyright clean on all touched files.
8. Known pinning caveat: BL-010 internal snapshot uses 70,680 candidates, BL-011 uses 33,096, canonical v1f uses 46,776 — see `00_admin/bl010_bl011_baseline_pinning_manifest.md` for rationale.

## Run References
1. BL-013 entrypoint command docs:
   - `07_implementation/implementation_notes/bl013_entrypoint/bl013_run_command.md`
2. Spotify API ingestion runbook:
   - `07_implementation/implementation_notes/bl001_bl002_ingestion/docs/spotify_api_ingestion_runbook.md`

## Autonomous Mode Handoff
Use this mode when you want one-command execution with automatic session reporting.

1. Full contract + report (recommended)
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File 07_implementation/scripts/autopilot_launch.ps1 -Mode full-contract`
2. Validate-only + report
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File 07_implementation/scripts/autopilot_launch.ps1 -Mode validate-only`
3. Focused gates (single mode)
   - `preflight`, `ci-guard`, `typecheck`, `tests`
4. Report output
   - A markdown session report is written to `00_admin/autopilot_session_YYYY-MM-DD-HHMMSS.md`.
5. Sign-off rule
   - Treat BL-014 `overall_status=pass` as required before session sign-off updates.

## Session Close Checklist
1. `07_implementation/backlog.md` reflects real status.
2. `07_implementation/experiment_log.md` includes all runs from this chat.
3. `00_admin/change_log.md` has a new `C-###` for session-level changes.
4. `00_admin/decision_log.md` includes any new design choices (`D-###`).
5. `00_admin/unresolved_issues.md` updated for new blockers or resolved blockers.
6. If code changed, ensure outputs/artifacts are linked in logs.

This close pass should happen automatically in the final response when session changes occurred.

## Notes For Collaborator
- Keep wording simple and concrete in chapter edits.
- Avoid introducing new tools, adapters, or datasets unless logged and justified.
- If unsure, ask the AI to run the session checklist again before continuing.
