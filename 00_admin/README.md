# 00_admin Control Hub

Last refreshed: 2026-04-09 (admin/instruction simplification wave)

## Purpose
This folder is the governance source of truth for thesis state, decisions, changes, execution posture, and unresolved risks.

## Core Governance Set
Use these as the active operating surface:
1. `thesis_state.md` (canonical title/RQ/scope/posture)
2. `timeline.md` (execution posture and next bounded work)
3. `change_log.md` (C-series change record)
4. `decision_log.md` (D-series design decisions)
5. `unresolved_issues.md` (open blockers and risk state)
6. `recurring_issues.md` (repeat-friction prevention)
7. `GOVERNANCE.md` (control/transparency gate)
8. `operating_protocol.md` (schemas and workflow rules)

## Runtime Root Rule
- Active runtime/workflow surface is `07_implementation/` (entrypoint: `07_implementation/main.py`).
- Treat `_scratch/` (including `_scratch/final_artefact_bundle/`) as reference/archive material unless explicitly requested for historical review.

## Startup Read Order
1. `thesis_state.md`
2. `timeline.md`
3. `change_log.md`
4. `decision_log.md`
5. `unresolved_issues.md`
6. `recurring_issues.md`

## Archive Policy
- Non-core or historical admin documents should be moved under `00_admin/archives/` with a dated consolidation note.
- Keep `change_log.md` and `decision_log.md` append-only.
- If a consolidated topic remains relevant, summarize it in `thesis_state.md` rather than re-expanding file sprawl.

## Hygiene Rules
- Update governance files in the same session as implementation/writing changes.
- Keep evidence linked in `change_log.md` entries.
- Record major workflow/design choices in `decision_log.md`.
