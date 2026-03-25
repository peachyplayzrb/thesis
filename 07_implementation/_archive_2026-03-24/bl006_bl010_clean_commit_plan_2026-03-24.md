# Clean Commit Plan - BL-006 to BL-010 Freeze Package

## Goal
Create a clean, auditable commit for the freeze checkpoint without mixing unrelated workspace changes.

## Constraints
- Repository currently contains unrelated modified and untracked files.
- Use explicit path-scoped staging only.
- Avoid broad staging commands like `git add .`.

## Recommended Commit Strategy

### Commit A (Freeze Checklist + Plan)
Scope: newly created operator docs only.

Files:
- 07_implementation/implementation_notes/bl010_reproducibility/bl006_bl010_freeze_checklist_2026-03-24.md
- 07_implementation/implementation_notes/bl010_reproducibility/bl006_bl010_clean_commit_plan_2026-03-24.md

Commands:
- `git add -- 07_implementation/implementation_notes/bl010_reproducibility/bl006_bl010_freeze_checklist_2026-03-24.md 07_implementation/implementation_notes/bl010_reproducibility/bl006_bl010_clean_commit_plan_2026-03-24.md`
- `git diff --staged --name-only`
- `git commit -m "docs(freeze): add BL-006 to BL-010 freeze checklist and clean commit plan"`

### Commit B (BL-010 Refresh Evidence + Governance)
Scope: BL-010 refresh artifacts and synchronized logs.

Files:
- 07_implementation/implementation_notes/bl010_reproducibility/bl010_state_log_2026-03-24.md
- 07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json
- 07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_run_matrix.csv
- 07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json
- 07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_01/
- 07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_02/
- 07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_03/
- 07_implementation/experiment_log.md
- 07_implementation/test_notes.md
- 07_implementation/backlog.md
- 00_admin/change_log.md

Commands:
- `git add -- 07_implementation/implementation_notes/bl010_reproducibility/bl010_state_log_2026-03-24.md`
- `git add -- 07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_report.json 07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_run_matrix.csv 07_implementation/implementation_notes/bl010_reproducibility/outputs/bl010_reproducibility_config_snapshot.json`
- `git add -- 07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_01 07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_02 07_implementation/implementation_notes/bl010_reproducibility/outputs/replay_03`
- `git add -- 07_implementation/experiment_log.md 07_implementation/test_notes.md 07_implementation/backlog.md 00_admin/change_log.md`
- `git diff --staged --name-only`
- `git commit -m "chore(bl010): refresh reproducibility evidence and sync governance logs"`

## Verification Before Each Commit
- `git status --short`
- `git diff --staged --name-only`
- `git show --stat --name-only --oneline HEAD` (after commit)

## Guardrails
- Do not stage ingestion/output files unrelated to BL-010 freeze scope.
- Do not stage DS-001 build scripts unless intentionally included in a separate commit.
- Keep website build changes for a later dedicated commit, as requested.
