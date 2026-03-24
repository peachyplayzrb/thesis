# Friend Handoff Playbook

Last updated: 2026-03-25

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
1. Resolve UI-008: close DS-001 governance/provenance/terms verification after access reopening.
2. Resolve UI-003: finish thesis-wide citation verification package and synthesis closeout.
3. Execute Days 4 to 7 of `00_admin/mentor_draft_7day_sprint_2026-03-23.md`.
4. Continue `WP-WEBINT-001` freeze-and-integrate website package with bounded hardening only.

Current sprint state note: Day 4 is active as of 2026-03-25.

## Run References
1. BL-013 entrypoint command docs:
   - `07_implementation/implementation_notes/entrypoint/bl013_run_command.md`
2. Spotify API ingestion runbook:
   - `07_implementation/implementation_notes/ingestion/spotify_api_ingestion_runbook.md`

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