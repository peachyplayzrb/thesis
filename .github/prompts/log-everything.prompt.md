---
agent: ask
description: Run end-of-session logging-completeness pass
---

Run a full logging-completeness pass for this session.

Required checks:
1. `07_implementation/backlog.md` status updates match work performed.
2. `07_implementation/experiment_log.md` includes all planned/run entries (`EXP-XXX`) from this session.
3. `00_admin/change_log.md` has a session-level `C-###` entry with evidence and affected components.
4. `00_admin/decision_log.md` includes any implementation-time design decisions (`D-###`).
5. `00_admin/unresolved_issues.md` reflects any new blockers or resolved blockers.

Output format:
- Findings
- Fixes applied
- Remaining open risks (if any)
