# Recurring Issues Log

Last updated: 2026-04-09

## Purpose
Track friction patterns that appear more than once so future sessions can avoid them automatically.
When the same problem appears in two or more sessions, append an entry here.
`copilot-instructions.md` and the user-level instruction file will read this implicitly through the Automatic Improvement Rule.

## Format
Each entry is a short named block:

```
### RI-NNN — Short title
- first_seen: YYYY-MM-DD
- last_seen: YYYY-MM-DD
- pattern: what keeps happening
- fix_applied: what was done to stop it recurring (or "pending" if still open)
```

---

### RI-001 — Hardcoded model name in prompt/agent frontmatter causes validation rejection
- first_seen: 2026-03-27
- last_seen: 2026-03-27
- pattern: `.prompt.md` and `.agent.md` files with an explicit `model:` frontmatter field get rejected by the VS Code validation layer; the model identifier string is not recognised.
- fix_applied: Removed `model:` field from all agent and prompt frontmatter. Let the active VS Code model selection take effect instead. Also renamed deprecated `mode:` to `agent:` in prompt frontmatter.

---

## Pending / No Fix Yet

None.

---

### RI-002 — Stale checkpoint wording accumulates in state/timeline files
- first_seen: 2026-03-26
- last_seen: 2026-03-29
- pattern: Priority-status checkpoints append correctly but milestone/work-package status labels ("in progress", "planned") are not updated when work completes, causing milestone table to show stale active states long after completion.
- fix_applied: Admin sync waves (C-166, C-189, C-220) correct milestone labels in batch. Trigger an admin sync wave at each major batch-completion boundary.

### RI-003 — Maintenance snapshot `Highest change ID` in change_log.md goes stale
- first_seen: 2026-03-28
- last_seen: 2026-03-29
- pattern: The maintenance snapshot header at the top of `change_log.md` declares the highest entry ID, but new entries are appended in the table without updating the header, causing a permanent discrepancy.
- fix_applied: Update the maintenance snapshot header when it is more than 5 entries behind. The C-220 admin sync wave corrects the value from C-205 to C-219.

### RI-004 — Handoff playbook priority queue goes stale after issue closure
- first_seen: 2026-03-25
- last_seen: 2026-03-29
- pattern: `handoff_friend_chat_playbook.md` Priority Queue and sprint-state note are not updated when unresolved issues close, causing collaborators to receive stale "open issue" instructions.
- fix_applied: Admin sync waves include a handoff-playbook update step. Apply this whenever any UI is closed or a sprint day is completed.

### RI-005 — Startup checklist references missing workflow files
- first_seen: 2026-04-08
- last_seen: 2026-04-09
- pattern: Active instructions expected `07_implementation/backlog.md` and `07_implementation/experiment_log.md`, but those files do not exist in the current repository posture, causing avoidable startup friction.
- fix_applied: Rebased startup/closeout rules on core governance files (`thesis_state`, `timeline`, `change_log`, `decision_log`, `unresolved_issues`, `recurring_issues`) and removed prompt-file dependency from active workflow surfaces.

### RI-006 — Stale active-baseline path points to removed location
- first_seen: 2026-04-09
- last_seen: 2026-04-18
- pattern: Multiple docs still referenced `07_implementation/ACTIVE_BASELINE.md` after runtime-root consolidation, while the only remaining baseline markdown was under `_scratch/final_artefact_bundle/`, causing workflow confusion about active authority.
- fix_applied: Enforced active-root rule in instruction surfaces and admin docs (`07_implementation/` active, `_scratch/` reference-only), added explicit status note in `_scratch/final_artefact_bundle/ACTIVE_BASELINE.md`, and logged decision/change sync (D-048/C-229). Follow-up QC cleanup wave (D-189/C-478) removed lingering stale-path wording from active `09_quality_control` surfaces and re-anchored active authority to thesis_state/timeline plus current run-ID references.
