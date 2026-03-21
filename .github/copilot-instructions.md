# Copilot Instructions For Thesis Environment

## Session Start Rule
At the start of every chat session — or whenever the user says anything like "make sure everything is logged", "check the logs", "are we tracking everything", or "start of session" — perform the following checklist WITHOUT waiting to be asked:

1. Read `00_admin/thesis_state.md` — confirm current title, RQ, and scope are unchanged.
2. Read `07_implementation/backlog.md` — identify which items are `done`, `in-progress`, and `todo`.
3. Read `07_implementation/experiment_log.md` — check whether every `done` backlog item has a corresponding `EXP-XXX` entry. If any are missing, create them.
4. Read `00_admin/change_log.md` — confirm the highest `C-###` ID and check for any empty/stub entries. Fix any stubs found.
5. Read `00_admin/decision_log.md` — confirm the highest `D-###` ID.
6. Read `00_admin/unresolved_issues.md` — note any open issues that may block current work.
7. Report what was found and what (if anything) was fixed before proceeding.

This checklist must run before any implementation, writing, or research work begins in the session.

## Collaborator Handoff Mode
If a collaborator is taking over this repo, enforce the same workflow used by the original owner:
- Run the session-start checklist automatically on the first task message in every new chat.
- Use the same checklist and logging strictness as the original workflow.
- Keep implementation updates synchronized across backlog, experiment, decision, change, and unresolved-issues files.
- If a request is ambiguous, resolve ambiguity without skipping governance updates.
- Before ending chat, run a full logging-completeness pass and report any gaps fixed.

## Session Close Rule
At the end of every chat session where any file updates, run activity, or governance changes occurred:
1. Verify backlog, experiment, change, decision, and unresolved-issues synchronization.
2. Apply any missing updates directly.
3. Report the closure status and remaining blockers.

Do this automatically without requiring the user to type "log everything".

## Recommended Prompt Shortcuts
Collaborators should use these prompts to stay consistent:
- `run /session-start-check`
- `log everything`
- `continue BL-XXX and log everything`

Prompt files:
- `.github/prompts/session-start-check.prompt.md`
- `.github/prompts/log-everything.prompt.md`

## Implementation Session Rule
During any implementation session:
- Before writing code for a backlog item, create an `EXP-XXX` entry in `07_implementation/experiment_log.md` with `status: planned`.
- After the run completes (pass or fail), update that entry with actual results, metrics, artifact paths, and `deterministic_repeat_checked`.
- If a design choice is made during implementation (e.g. which algorithm, which schema field, which threshold), log a `D-###` entry in `00_admin/decision_log.md`.
- After any meaningful set of changes to tracked files, add a `C-###` entry in `00_admin/change_log.md`.
- Update the backlog item status in `07_implementation/backlog.md` as soon as work changes state.

## General Rules
- Always consult `00_admin/thesis_state.md` before major guidance.
- Do not silently rewrite title, research question, scope, or methodology.
- If protected changes are needed, create a change proposal in `00_admin/change_log.md`.
- Distinguish evidence from interpretation.
- Update linked files when new evidence affects themes, design, or gap statements.
- Keep terminology consistent with current thesis state.
- Do not overstate claims; flag weak support in `09_quality_control/citation_checks.md`.
- Add mentor questions to `00_admin/mentor_question_log.md` when ambiguity affects assessment risk.
- Prefer concise, reusable outputs over long freeform text.
- Follow schemas and ID formats in `00_admin/operating_protocol.md`.
