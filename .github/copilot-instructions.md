# Copilot Instructions For Thesis Environment

## Primary Workflow Assumption
This repo must work well when the user starts with ordinary natural-language chat messages.

Do not depend on slash prompts as the main entry path.
Treat `.github/prompts/` as optional helpers for recurring structured tasks, not as the required way to start work.

When a new chat begins, infer the intended mode from the user request:
- Ask-style requests: explanation, review, triage, repo navigation, impact analysis, planning, or "what next" questions.
- Plan/Autopilot-style requests: implementation, writing updates, repo edits, running checks, logging, or end-to-end execution.

If the request is ambiguous, infer the lightest reasonable mode first, explain what you are checking, and continue without waiting for the user to restate the request in a predefined format.

## Session Start Rule
At the start of every new chat session, and before any substantial implementation, writing, or research work, perform the following checklist WITHOUT waiting to be asked.

The checklist also applies whenever the user says anything like "make sure everything is logged", "check the logs", "are we tracking everything", or "start of session".

For quick lightweight questions that only need a brief explanation and no repo changes, do the minimum context rebuild needed to answer accurately instead of forcing a full heavy startup ritual.

For Plan/Autopilot or any edit/run request, always run the full checklist first:

1. Read `00_admin/thesis_state.md` — confirm current title, RQ, and scope are unchanged.
2. Read `07_implementation/backlog.md` — identify which items are `done`, `in-progress`, and `todo`.
3. Read `07_implementation/experiment_log.md` — check whether every `done` backlog item has a corresponding `EXP-XXX` entry. If any are missing, create them.
4. Read `00_admin/change_log.md` — confirm the highest `C-###` ID and check for any empty/stub entries. Fix any stubs found.
5. Read `00_admin/decision_log.md` — confirm the highest `D-###` ID.
6. Read `00_admin/unresolved_issues.md` — note any open issues that may block current work.
7. Read `00_admin/recurring_issues.md` — review known friction patterns to avoid repeating them.
8. Report what was found and what (if anything) was fixed before proceeding.

This checklist must run before any implementation, writing, or research work begins in the session.

## Mode Routing
Use the following behavior split by default.

### Ask Mode Default
- Rebuild only the amount of context needed for an accurate answer, unless the request clearly opens a larger work session.
- Prefer reading, searching, reviewing, and explaining over editing.
- For review requests, present findings first.
- If the user is clearly asking for implementation, say that execution will proceed and shift into the execution path instead of staying in analysis.

### Plan Or Autopilot Default
- Run the full session-start checklist before editing or executing.
- Rebuild state from canonical control files instead of asking the user to repeat project context.
- Carry work through inspection, implementation, verification, governance sync, and session closeout.
- Treat natural-language requests like "continue from current state", "finish the next item", or "fix this" as valid execution starts.

## Natural-Language Continuation Rule
Do not require the user to mention backlog IDs, prompts, or explicit mode names for ordinary continuation.

When the user says things like:
- "continue from current state"
- "what should I do next"
- "review this"
- "fix this"
- "finish the current work"

use thesis state, backlog, unresolved issues, experiment log, and the current file/editor context to determine the most likely continuation path.

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

## Prompt Role
Prompt files under `.github/prompts/` are optional specialist utilities for recurring structured tasks.

Do not assume the user will invoke them.
Do not redirect the user into prompts when the same work can be inferred from a normal chat request.

## Implementation Session Rule
During any implementation session:
- Before writing code for a backlog item, create an `EXP-XXX` entry in `07_implementation/experiment_log.md` with `status: planned`.
- After the run completes (pass or fail), update that entry with actual results, metrics, artifact paths, and `deterministic_repeat_checked`.
- If a design choice is made during implementation (e.g. which algorithm, which schema field, which threshold), log a `D-###` entry in `00_admin/decision_log.md`.
- After any meaningful set of changes to tracked files, add a `C-###` entry in `00_admin/change_log.md`.
- Update the backlog item status in `07_implementation/backlog.md` as soon as work changes state.

For repo-tooling or workflow customizations that are not tied cleanly to an existing BL item, still keep change and decision logs synchronized and create an experiment-log entry when the work meaningfully changes how execution in this repo is supposed to happen.

## Automatic Improvement Rule
This repo should become easier to use over time.

When the same friction appears repeatedly:
1. First adapt behavior through persistent memory or lightweight instruction updates.
2. If the friction is repo-specific and safe to automate, update the repo customization surface directly.
3. If the change is risky, scope-changing, or could surprise collaborators, surface the proposed change before applying it.

Read `00_admin/recurring_issues.md` at the start of any new session to pick up known friction patterns and their applied fixes. When a new recurring pattern is confirmed (seen in two or more sessions), append a new `RI-NNN` entry to that file.

Examples of friction that should trigger improvement:
- the user repeatedly starts with vague natural-language continuation requests and the agent still asks for avoidable restatement
- the same logging or handoff gap appears across multiple sessions
- Ask-style reviews repeatedly drift into unnecessary implementation
- Plan/Autopilot sessions repeatedly miss a needed context file or closeout step

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

## Preferred Customization Surface
- Workspace-wide thesis governance belongs in `.github/copilot-instructions.md`.
- Ask-heavy review/navigation behavior belongs in `.github/agents/thesis-ask.agent.md`.
- End-to-end execution behavior belongs in `.github/agents/thesis-autopilot.agent.md`.
- User-personal workflow preferences that should follow across workspaces belong in the user profile instruction surface, not in thesis-specific repo files.
