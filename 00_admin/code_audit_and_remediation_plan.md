# Code Audit and Remediation Plan (Open Items Only)

Last updated: 2026-04-21
Owner: user
Scope: `07_implementation/src` and supporting governance/tooling surfaces

---

## 1) Current State Snapshot

Completed and closed:
- CR-1 through CR-8 are resolved in governance (`UNDO-S` closed).
- Core gates and advisory checks are green in latest evidence artifacts.
- Determinism replay command path and wrapper/CI integration are active.

Source of truth for completed work remains:
- `00_admin/unresolved_issues.md`
- `00_admin/change_log.md`
- `00_admin/decision_log.md`

This document now tracks only remaining plan work.

---

## 2) Remaining Open Work

### O-1) Mutation testing lane (not yet operationalized)

Goal:
- Add an advisory mutation-testing surface to catch logic gaps missed by line/branch coverage.

Preferred path:
- Start with `mutmut` (faster practical adoption than `cosmic-ray` for current workflow).

Minimum deliverables:
1. Script surface in `07_implementation/scripts/` (advisory mode).
2. VS Code task surface in `.vscode/tasks.json`.
3. Canonical report artifact at root (for example `mutation_src_report_latest.txt`).
4. Bounded pilot run on high-value modules first:
   - `src/retrieval`
   - `src/scoring`
   - `src/transparency`
5. Survivor triage policy documented (equivalent vs real survivor, follow-up test required).

Closure evidence:
- One successful pilot report attached and summarized in change log.
- Any real survivor converted into tests or unresolved item with owner and severity.

---

### O-2) Semgrep anti-pattern rules (not yet operationalized)

Goal:
- Add targeted static rules for policy-level anti-patterns that generic linting does not catch.

Minimum rulepack scope:
- Silent fallback for unknown policy/mode values.
- Undeclared or unaudited env-var control channels.
- Duplicate helper logic risk where authoritative implementation should be single-source.

Minimum deliverables:
1. Script surface in `07_implementation/scripts/` (advisory mode).
2. VS Code task surface in `.vscode/tasks.json`.
3. Canonical report artifact at root (for example `semgrep_src_report_latest.txt`).

Closure evidence:
- Initial advisory run report generated.
- Findings triaged into fixed vs deferred with explicit rationale.

---

### O-3) Property-based test expansion beyond current bounded set

Status:
- Hypothesis is already integrated, but broader invariant coverage remains optional and incomplete.

Goal:
- Extend property tests only where contract risk is still concentrated.

Priority expansion targets:
- Retrieval threshold-edge monotonicity/inclusion invariants.
- Scoring normalization and contribution-boundary invariants.
- Run-config coercion/idempotence invariants for nested control payloads.

Closure evidence:
- New property tests added for selected targets with stable pass in normal test workflow.

---

## 3) Definition of Done for This Open-Items File

This file can be archived or marked complete when all are true:
- [ ] Mutation advisory lane is operational with report artifact and triage policy.
- [ ] Semgrep advisory lane is operational with first triage run complete.
- [ ] Optional property-test expansion targets are either implemented or explicitly deferred with rationale.
- [ ] `00_admin/unresolved_issues.md`, `00_admin/change_log.md`, and `00_admin/decision_log.md` reflect the true status.

---

## 4) Practical Constraints

- Keep all additions advisory-first (non-blocking) unless policy is explicitly upgraded.
- Preserve active runtime authority in `07_implementation/`.
- Keep compatibility-safe behavior and avoid schema-breaking changes.
- Treat `_scratch/` as reference only unless explicitly requested.
