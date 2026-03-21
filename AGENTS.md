# Thesis Workspace Agent Rules

This file mirrors the workspace behavior so collaborator sessions remain consistent.

## Automatic Session Start
At the start of every chat session, run this checklist before doing implementation, writing, or research work:
1. Read `00_admin/thesis_state.md` and confirm title/RQ/scope state.
2. Read `07_implementation/backlog.md` and summarize done/in-progress/todo.
3. Read `07_implementation/experiment_log.md` and verify done items have `EXP-XXX` entries.
4. Read `00_admin/change_log.md` and verify highest `C-###`, fixing any stubs.
5. Read `00_admin/decision_log.md` and verify highest `D-###`.
6. Read `00_admin/unresolved_issues.md` and surface active blockers.
7. Report findings and fixes before proceeding.

## Automatic Session Close
Before ending a chat where any work happened:
1. Sync `07_implementation/backlog.md`.
2. Sync `07_implementation/experiment_log.md`.
3. Add/update `00_admin/change_log.md` (`C-###`).
4. Add/update `00_admin/decision_log.md` (`D-###`) if decisions occurred.
5. Sync `00_admin/unresolved_issues.md`.
6. Report closure status and open blockers.

## Protected Scope
Do not change thesis title, research question, scope boundaries, or methodology without explicit approval.
