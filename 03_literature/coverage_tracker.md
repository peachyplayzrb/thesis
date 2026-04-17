# Coverage Tracker

## 2026-04-17 Paper-Note Baseline Alignment

- Closed the only confirmed note-coverage gap by adding:
	- `03_literature/paper_notes/P-066_peffers_design_2007.md`
- Purpose of this batch:
	- restore one-to-one coverage between `03_literature/source_index.csv` and `03_literature/paper_notes/` for the active 66-source literature set
	- anchor Chapter 3 methodology language to a processed note rather than only a bibliography/source-index entry
- Follow-on normalization still pending for later batches:
	- optional-field consistency across older notes

## 2026-04-17 Paper-Note Status Normalization

- Added explicit `source_index_status` metadata to all note files whose source entries remain classified as `screened_keep` or `screened_support` in `03_literature/source_index.csv`.
- Normalized note IDs in this batch:
	- `P-041`, `P-042`, `P-043`, `P-044`, `P-045`, `P-046`, `P-047`, `P-048`, `P-049`, `P-050`, `P-051`, `P-052`, `P-053`, `P-054`, `P-055`, `P-056`, `P-057`, `P-058`, `P-061`, `P-062`, `P-063`, `P-066`
- Policy applied:
	- `document_status` continues to mean note-processing state
	- `source_index_status` now preserves triage meaning from the source index when that meaning is more specific than generic processing
- Follow-on normalization still pending:
	- optional-field consistency across older notes

## 2026-04-17 Paper-Note Optional-Field Normalization

- Added the missing `supported_architecture_layer` field to the last five core notes that still lacked it.
- Normalized note IDs in this batch:
	- `P-001`, `P-002`, `P-003`, `P-004`, `P-005`
- Policy applied:
	- core paper notes should declare the architecture layers they most directly inform when that mapping is already clear from `relevance_to_thesis`, `design_implications`, and `chapter_use_cases`
- Follow-on normalization still pending:
	- `gap_implications` backfill for older notes still missing that field

## 2026-04-17 Paper-Note Gap-Implications Backfill

- Added the missing `gap_implications` field to the remaining 23 older literature notes that already had enough thesis-specific context in `relevance_to_thesis`, `supported_architecture_layer`, `theme_mapping`, and `design_implications`.
- Normalized note IDs in this batch:
	- `P-006`, `P-007`, `P-008`, `P-009`, `P-010`, `P-011`, `P-012`, `P-013`, `P-014`, `P-015`, `P-016`, `P-017`, `P-018`, `P-019`, `P-020`, `P-021`, `P-022`, `P-023`, `P-024`, `P-025`, `P-026`, `P-027`, `P-028`
- Policy applied:
	- when a note already states its thesis relevance and architecture-layer implications clearly, `gap_implications` should summarize the specific literature gap the thesis is using that source to motivate or bound
- Follow-on normalization still pending:
	- theme-mapping drift review before Chapter 3 rationale rewriting

## 2026-04-17 Paper-Note Theme-Mapping Drift Cleanup

- Audited the note-corpus theme vocabulary after optional-field backfill and normalized only four low-risk singleton drifts that created avoidable retrieval fragmentation.
- Normalized note IDs in this batch:
	- `P-002`, `P-032`, `P-046`, `P-066`
- Policy applied:
	- preserve strategically distinct theme clusters, but merge singleton or near-singleton tags when they create search/index fragmentation without adding meaningful conceptual resolution
- Result:
	- literature-note normalization phase is now clean enough to support Chapter 3 option-space and selected-design rationale rewriting

## 2026-03-23 Recovered Source Processing

- Processed recovered evidence packages for:
	- P-011 `adomavicius_toward_2005`
	- P-003 `tintarev_evaluating_2012`
	- P-002 `tintarev_survey_2007` (refresh)
- Updated paper notes with source recovery provenance and strengthened findings:
	- `03_literature/paper_notes/P-011_adomavicius_toward_2005.md`
	- `03_literature/paper_notes/P-003_tintarev_masthoff_2012.md`
	- `03_literature/paper_notes/P-002_tintarev_masthoff_2007.md`
- Added claim-check extraction artifacts:
	- `10_resources/papers/_extracted_claim_check/Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.txt`
	- `10_resources/papers/_extracted_claim_check/Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.txt`
	- `10_resources/papers/_extracted_claim_check/Tintarev and Masthoff - 2007 - A Survey of Explanations in Recommender Systems.txt`
- Updated unresolved issue tracking to indicate these two previously blocked sources are no longer missing for citation-hardening runs:
	- `00_admin/unresolved_issues.md` (UI-003 progress update)
