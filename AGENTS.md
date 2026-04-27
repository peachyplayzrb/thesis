# Codex Bridge For This Thesis Repo

This file adapts the existing Copilot setup for Codex. It does not replace `.github/copilot-instructions.md`; that file remains the canonical workspace instruction surface for this repository. When instructions conflict, follow the repo-local governance files first, then this bridge.

## Canonical Instruction Sources

Use these existing files as the source of truth before substantial repo work:

- `.github/copilot-instructions.md`
- `.github/agents/thesis-ask.agent.md`
- `.github/agents/thesis-autopilot.agent.md`
- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.github/workflows/ci.yml`
- `.vscode/mcp.json`
- User-profile natural-language workflow instruction file when accessible in the runtime environment, such as `natural-language-workflow.instructions.md`

The archived prompt files under `.github/archives/prompts_2026-04-09/` are historical/reference material unless the user explicitly asks for them.

## Active Runtime Surface

- Treat `07_implementation/` as the active implementation/runtime root.
- Treat `_scratch/` as legacy or reference-only unless the user explicitly reopens it.
- For Python work, align with the configured workspace/runtime split:
  - Workspace interpreter setting: `${workspaceFolder}\.venv\Scripts\python.exe`
  - Implementation runtime working directory: `07_implementation`
  - Implementation runtime interpreter when running inside `07_implementation`: `python.exe`
  - Source root inside implementation runtime: `src`
  - Prefer existing task/script wrappers, such as `run_tool_with_venv_fallback.ps1`, over ad hoc direct executable paths.
- Preserve existing task labels, script entrypoints, report paths, and artifact contracts unless the user explicitly asks for a workflow change.

## Natural-Language Routing

The user usually starts with ordinary chat rather than slash prompts. Infer the workflow from intent:

- Ask/review/explain/check questions: read the relevant files, answer directly, and avoid edits unless the user asks for fixes.
- Build/fix/run/make/do requests: act execution-first, make focused changes, run the relevant checks, and report outcomes.
- When the user asks for a complete check or broad review, use a code-review stance: list bugs, logic risks, missing tests, and verification gaps before summaries.

Prefer direct execution and iterative polish. Do not force the user to restate context when the repo can answer it.

## User Workflow Defaults

Assume these user preferences unless the user says otherwise:

- They prefer practical execution over abstract planning.
- They value concrete readiness checks, especially for report/thesis work.
- They want short, concrete progress updates while work is underway.
- They use a Windows/PowerShell environment with a broad CLI baseline including `rg`, `fd`, `jq`, `yq`, `bat`, `delta`, `hyperfine`, `fzf`, `sg`, `sd`, `zoxide`, `eza`, `lazygit`, `gh`, `just`, `tldr`, `xh`, `doggo`, `dust`, `duf`, `procs`, `starship`, `gitui`, `hexyl`, `broot`, `lazydocker`, `mprocs`, and `bottom`.

## Startup Checklist For Substantial Work

For Ask-style lightweight, read-only questions, rebuild only the minimum context needed for an accurate answer.

For Plan/Autopilot or any edit/run request, run the full startup checklist first, once per chat unless a restart audit is requested or drift appears, and report findings before edits/execution:

1. `00_admin/thesis_state.md`
2. `00_admin/timeline.md`
3. `00_admin/change_log.md`
4. `00_admin/decision_log.md`
5. `00_admin/unresolved_issues.md`
6. `00_admin/recurring_issues.md`

This checklist must run before substantial implementation, writing, or research work begins.

## Collaborator Handoff Mode

If a collaborator takes over this repo, enforce the same workflow posture:

- Run the startup checklist automatically on the first task message in each new chat.
- Keep implementation updates synchronized across thesis state, timeline, decision, change, unresolved-issues, and recurring-issues files.
- Resolve ordinary ambiguity without requiring rigid prompt restatement.
- Before ending the chat, run a logging-completeness pass and report any gaps fixed.

## Prompt Role

Prompt files are not the default workflow surface. Do not require slash-prompt invocation when natural-language chat can infer and execute the request safely.

## Local Copilot Runtime Settings

When local/user VS Code Copilot runtime toggles are available, such as autopilot enablement, tool auto-approve, terminal auto-approve, edits auto-approve, or nested agent-file usage, respect them as active execution posture and do not assume default prompting behavior from a clean install.

## Governance Logging

For meaningful tracked changes, keep the governance ledgers synchronized:

- Add a `C-###` entry in `00_admin/change_log.md` for material changes.
- Add a `D-###` entry in `00_admin/decision_log.md` when a durable workflow, architecture, evidence, or policy decision is made.
- During implementation, if a design choice is made, such as an algorithm, schema, threshold, or policy decision, log a `D-###`.
- Update `00_admin/thesis_state.md`, `00_admin/timeline.md`, and `00_admin/unresolved_issues.md` when posture or checkpoint state changes.
- If no tracked files changed, do not add no-op `C-###` or `D-###` entries.
- For repo-tooling or workflow customizations not tied to a BL item, still keep `C-###` and `D-###` synchronized and include concrete artifact/validation evidence.

Respect `00_admin/recurring_issues.md`, especially the rule against hardcoding model names in prompt or agent frontmatter.

## Verification Commands

Prefer existing VS Code tasks first because they preserve repo wrappers and artifact contracts:

- `07: Ruff Check src`
- `07: Typecheck (pyright)`
- `07: Tests + Coverage src`
- `07: CI Guard Phase 6`
- `07: Validate + Determinism Replay x3 (Wrapper)`
- `07: Full Contract (Preflight + Check-All)`

If running raw commands directly, use CI-parity commands from `07_implementation`:

```powershell
cd 07_implementation
python -m ruff check src
python -m pyright --project pyrightconfig.json
python -m pytest tests -v --cov=src --cov-report=term-missing --cov-fail-under=65
python ci_guard_phase_6_check.py
python main.py --validate-only --verify-determinism --verify-determinism-replay-count 3
```

The CI contract runs from `07_implementation` and includes Ruff, Pyright, pytest with coverage threshold, phase-6 guard, and validate-only deterministic replay.

## Session Close Rule

At the end of any chat where tracked files or governance state changed:

1. Verify synchronization of thesis state, timeline, change log, decision log, unresolved issues, and recurring issues.
2. Apply any missing synchronization updates directly.
3. Report closure status and remaining blockers.

Do this automatically without requiring the user to request logging.

## Closeout

When work is complete, report:

- Files changed.
- Checks run and whether they passed.
- Any checks not run, with a brief reason.
- Any remaining blocker or follow-up that actually matters.

Keep the final answer concise and concrete.
