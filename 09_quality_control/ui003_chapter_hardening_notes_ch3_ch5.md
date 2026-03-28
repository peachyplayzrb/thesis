# UI-003 Chapter Hardening Notes (Chapters 3 to 5)

Date: 2026-03-27
Linked verdict matrix: `09_quality_control/ui003_claim_verdicts_ch3_ch5.md`

## Chapter 3 target edits

1. Section 3.4.1 numeric consistency fix
- Current issue: claim states approximately 32.2% match rate.
- Required edit: replace with a run-linked value aligned to current evidence (for example `match_rate=0.1595`, `unmatched_rate=0.8405`) and cite it as current baseline evidence rather than universal constant.
- Suggested wording:
  - "On the current v1f evidence baseline, direct DS-001 alignment reports `match_rate=0.1595` (`unmatched_rate=0.8405`), which materially constrains profile representativeness and should be interpreted as a bounded data-coverage limitation rather than a generalized property of all corpora."

2. Section 3.2 corpus defensibility caveat retention
- Keep DS-001 defensibility statement bounded to scope constraints.
- Add explicit note that defensibility claim is about reproducible candidate-side coverage and auditable execution, not complete user-history representativeness.

## Chapter 4 target edits

1. Section 4.8 table completion
- Replace all `pending` entries with current run IDs and pass/fail outcomes.
- Minimal required fields:
  - baseline run ID
  - repeat run IDs or replay count
  - result (`pass`/`fail`)
  - one-line interpretation

2. Section 4.9 table completion
- Replace `pending` values with actual baseline and variant settings from BL-011 scenarios.
- Include at least these rows:
  - influence-track toggle
  - valence-weight increase
  - strict/loose threshold scaling
  - playlist-rule compliance summary

3. Section 4.10 table completion
- Add sampled track count and explanation reconstruction status from BL-008 payload checks.
- Include explicit statement if reconstruction is field-complete but not a strict numerical re-derivation for every component.

## Chapter 5 target edits

1. Section 5.3 evidence linkage tightening
- Keep design-consideration claims tied to Chapter 4 evidence rows (EP IDs) rather than only literature references.
- Add one sentence linking each consideration cluster to implementation evidence class:
  - reproducibility
  - controllability
  - observability
  - alignment diagnostics

2. Section 5.4 limitation precision
- Keep snapshot divergence limitation as currently stated.
- Add one sentence that this is an evidence-packaging caveat, not a contradiction of determinism claims on pinned snapshots.

## Completion checklist

- [x] Verdict labels recorded for Chapter 3 to 5 claims.
- [x] Mismatch and weak-support locations isolated.
- [x] Concrete chapter-level rewrite instructions prepared.
- [x] UI-003 can be closed at control-record level after governance sync.

## Applied verification status (2026-03-28)

- Applied: Chapter 4 Section 4.8 table populated with run-linked reproducibility and observability outcomes.
- Applied: Chapter 4 Section 4.9 table populated with controllability and rule-compliance baseline/variant values.
- Applied: Chapter 4 Section 4.10 table populated with explanation reconstruction sample count and bounded error statement.
- Deferred: Chapter 3 mismatch item UI3-C3-007 remains a wording-level checkpoint to keep long-term numeric references tightly run-linked.

Re-audit note:
- `09_quality_control/ui003_claim_verdicts_ch3_ch5.md` has been refreshed to the 2026-03-28 state with Chapter 4 weak-support claims resolved.
