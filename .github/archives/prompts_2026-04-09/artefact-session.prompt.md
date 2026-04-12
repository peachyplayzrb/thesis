# Artefact Session Prompt
Use this prompt at the start of a work session to keep Copilot focused, minimize wasted premium requests, and produce thesis evidence alongside implementation.

## Reusable Prompt
Work on this thesis repo as an artefact-based project.

Before doing anything, read and align with:
- `00_admin/thesis_state.md`
- `00_admin/thesis_scope_lock.md`
- `00_admin/Artefact_MVP_definition.md`
- `07_implementation/backlog.md`
- `07_implementation/test_notes.md`
- `07_implementation/experiment_log.md`

Then:
1. Identify the next smallest P0 backlog item or subtask.
2. State the concrete output artifact that will prove progress.
3. Implement only the minimum viable slice needed for that artifact.
4. Record run evidence, assumptions, and failure modes.
5. Update any directly affected thesis/control files if needed.

Constraints:
- Keep work inside the locked MVP scope.
- Prefer deterministic, inspectable implementation choices.
- Do not broaden scope or change title/RQ/methodology without explicit approval.
- Prefer finishing one complete unit of work over discussing multiple options.
- If code is changed, also update the evidence trail.

Output format:
- first: what you will implement now
- second: what evidence artifact will be produced
- third: the actual code/file changes
- fourth: what was logged and what remains next