# UI-003 Claim Verdict Matrix (Chapters 3 to 5)

Date: 2026-03-28
Scope: `08_writing/chapter3.md`, `08_writing/chapter4.md`, `08_writing/chapter5.md`
Verdict labels: `supported`, `partially_supported`, `weak_support`, `mismatch`

## Chapter 3

| Claim ID | Chapter location | Claim summary | Verdict | Evidence basis | Action |
| --- | --- | --- | --- | --- | --- |
| UI3-C3-001 | 3.2 | Inspectability requires mechanism-linked outputs, not narrative-only explanation | supported | C-CLM-001, C-CLM-005, C-CLM-011 | none |
| UI3-C3-002 | 3.2 | Practical controllability should expose explicit user influence paths | partially_supported | C-CLM-003, C-CLM-015 | keep bounded wording |
| UI3-C3-003 | 3.2 | Playlist-aware behavior is necessary beyond item-only relevance | supported | C-CLM-004, C-CLM-013 | none |
| UI3-C3-004 | 3.2 | Run-level governance requires observability and reproducibility controls | supported | C-CLM-018, C-CLM-020 | none |
| UI3-C3-005 | 3.4 | Staged metadata/identifier alignment is preferable to one-shot fuzzy matching | supported | C-CLM-017 | none |
| UI3-C3-006 | 3.2 / 3.4 | DS-001 as active corpus is defensible under project constraints | partially_supported | C-CLM-021 | keep task-transfer caveat |
| UI3-C3-007 | 3.4.1 | DS-001 alignment match-rate claim is synchronized to current run-linked baseline evidence (`match_rate=0.1595`, `unmatched_rate=0.8405`) | supported | Chapter 3 Section 3.4.1 now uses canonical run-linked values consistent with Chapter 4 EP-ALIGN-001 | none |

## Chapter 4

| Claim ID | Chapter location | Claim summary | Verdict | Evidence basis | Action |
| --- | --- | --- | --- | --- | --- |
| UI3-C4-001 | 4.7 / Table 4.3 | Reproducibility check passes with deterministic replay behavior | supported | EP-REPRO-001 row + BL-010 report references | none |
| UI3-C4-002 | 4.7 / Table 4.3 | Explanation payload completeness and top-contributor traceability are present | supported | EP-EXPL-001 row + BL-008 artifacts | none |
| UI3-C4-003 | 4.7 / Table 4.3 | Controllability actuation produces interpretable directional deltas | supported | EP-CTRL-002 / EP-CTRL-003 rows + BL-011 scenarios | none |
| UI3-C4-004 | 4.8 | Reproducibility and observability results table content is complete | supported | Section 4.8 now contains run-linked baseline/repeat rows and pass outcomes | none |
| UI3-C4-005 | 4.9 | Controllability and rule-compliance results table content is complete | supported | Section 4.9 now includes baseline and variant controls with directional outcomes | none |
| UI3-C4-006 | 4.10 | Explanation fidelity reconstruction evidence is complete | supported | Section 4.10 now includes sampled-track reconstruction count and bounded error statement | none |
| UI3-C4-007 | 4.7 / EP-ALIGN-001 | High unmatched-rate limitation is explicitly surfaced | supported | EP-ALIGN-001 row (`match_rate=0.1595`, `unmatched_rate=0.8405`) | none |

## Chapter 5

| Claim ID | Chapter location | Claim summary | Verdict | Evidence basis | Action |
| --- | --- | --- | --- | --- | --- |
| UI3-C5-001 | 5.1 | Evaluation interpretation should be objective-protocol aligned, not metric-only | supported | C-CLM-009, C-CLM-010, C-CLM-018, C-CLM-020, C-CLM-022 | none |
| UI3-C5-002 | 5.3 | Key design considerations are evidenced by current implementation and evaluation artifacts | supported | Chapter 4 Table 4.3 + BL-010/BL-011/BL-014 references | none |
| UI3-C5-003 | 5.4 (limitation 1) | BL-010/BL-011 snapshot counts can differ from canonical BL-005 live count due to pinned snapshots | supported | C-182 evidence summary in admin logs + Chapter 4 EP-ALIGN row | none |
| UI3-C5-004 | 5.4 (limitation 2) | Raw JSON hash variance can occur due to metadata while semantic replay remains deterministic | supported | BL-010 report interpretation + prior reproducibility documentation | none |
| UI3-C5-005 | 5.4 (limitation 8) | Alignment ambiguity/unmatched handling remains an explicit system limitation | supported | BL-003 diagnostics, EP-ALIGN-001, unresolved-issue history | none |

## Closure Summary

- `supported`: 18
- `partially_supported`: 2
- `weak_support`: 0
- `mismatch`: 0

UI-003 closure interpretation:
- Claim-verdict recording for Chapters 3 to 5 is complete.
- Chapter 4 weak-support locations are now resolved after the 2026-03-28 hardening pass.
- Chapter 3 mismatch wording alignment checkpoint is now resolved.
