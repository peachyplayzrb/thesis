# Thesis Project: Controllable, Transparent Playlist Generation

## Thesis Focus
**Primary Objective**: Design a "deterministic, transparent, controllable, and observable" playlist generation pipeline.

**Research Question**: How can a single-user playlist generation pipeline remain automated while also being transparent, controllable, observable, and reproducible when using cross-source music preference data?

**Design Principles**:
1. **Controllability**: Every control has measurable, traceable effects
2. **Transparency**: Every decision is explainable and auditable
3. **Determinism**: Same input → same output (reproducibility)
4. **Observability**: Full diagnostics and decision logs

## Current Implementation Status
- ✅ Transparency: Strong (BL-008, BL-009 explanations and logs)
- ✅ Reproducibility: Strong (BL-010 determinism checks)
- ✅ Controllability governance: Phase 1-4 control/transparency framework is in place
- ✅ Runtime modularity: Phase 5-6 split BL-013 orchestration, BL-011 controllability, and BL-003 alignment helpers into focused modules while preserving stable entrypoints
- ✅ Architecture migration: BL-003 through BL-007 now have typed stage classes, typed model contracts, and thin compatibility `main.py` wrappers; BL-004 through BL-007 controllable-logic uplifts add run-config/env-driven policy controls

## Active Development
Current in-repo implementation work is effectively closed.
Remaining active work is bounded to submission packaging and any last-mile documentation polish.
Control audit: `05_design/CONTROL_SURFACE_REGISTRY.md`

---

# 00_admin Control Hub

Last refreshed: 2026-03-30 (aggressive root archival wave + admin synchronization C-222)

## Purpose
This folder is the governance and execution-control layer for the thesis. It tracks current state, scope, decisions, changes, timeline, unresolved risks, and mentor interaction artifacts.

## Read Order (Daily)
1. `thesis_state.md`
2. `timeline.md`
3. `unresolved_issues.md`
4. `decision_log.md`
5. `change_log.md`

## File Map
- `thesis_state.md`: canonical current posture (title, RQ, scope, implementation state).
- `thesis_scope_lock.md`: explicit in-scope/out-of-scope boundaries.
- `Artefact_MVP_definition.md`: minimum artefact contract.
- `methodology_definition.md`: DSR positioning and traceability rule.
- `evaluation_plan.md`: Chapter 4 evidence contract and test matrix.
- `timeline.md`: milestones + active work packages.
- `unresolved_issues.md`: active/closed blockers and risk actions.
- `decision_log.md`: D-series design decisions.
- `change_log.md`: C-series change history.
- `mentor_question_log.md`: MQ-series open/answered/deferred mentor questions.
- `mentor_feedback_log.md`: MF-series mentor feedback records.
- `handoff_friend_chat_playbook.md`: collaborator startup and session-close rules.
- `operating_protocol.md`: logging and workflow policy.
- `templates/`: reusable entry templates.

## Current Open Control Items (as of 2026-03-29)
1. No active unresolved governance issue in `unresolved_issues.md`.
2. Mentor response backlog in `mentor_question_log.md`: MQ-001, MQ-002, MQ-003, MQ-004, and MQ-007 are open (MQ-005, MQ-006, MQ-008 are deferred).

Admin sync checkpoint (2026-03-29): UI-003 closure and v1f canonical posture remain reflected across control files. Phase 5-6 modularization recorded. BL-003 typed-boundary + stage-shell migration complete. BL-004 through BL-007 OO-stage migration and controllable-logic uplift complete (C-205 through C-218). Documentation sync wave complete (C-219). 00_admin full synchronization wave complete (C-220). Only remaining active scope: physical submission packaging.

Admin sync checkpoint (2026-03-30): Aggressive root archival wave accepted (D-044/C-222). Root files `.controllability-transparency.instructions.md`, `.gitattributes`, `requirements.txt`, `pyrightconfig.json`, `main_standalone.py`, and `final_artefact.py` moved to `_deep_archive_march2026/_packages_reference_2026-03-30/`; deep archive is ignored in git; active runtime remains `07_implementation/main.py`.

## Hygiene Rules
- Keep this folder as the single source of truth for governance state.
- When implementation/writing reality changes, update admin files in the same session.
- Do not delete historical decisions/changes; mark superseded/deprecated where needed.
