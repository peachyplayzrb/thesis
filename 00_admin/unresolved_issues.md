# Unresolved Issues

## Active
- UI-002 (2026-03-15): Active Chapter 2 verbatim audit reports `weak_support=24` on `08_writing/chapter2_draft_v11.md` (`total_claim_checks=46` in `09_quality_control/chapter2_verbatim_audit.md`).
	- impact: Chapter 2 cannot be treated as fully citation-hardened under the current zero-weak closure rule.
	- next_action: Perform targeted sentence-level wording hardening for weak-support claims, then rerun audit until `weak_support=0` or approve a bounded non-zero threshold.
	- owner: AI + user
	- status: open

- UI-003 (2026-03-19): Thesis-wide citation verification and literature leverage pass not yet fully tracked in repository control files.
	- impact: Risk of citation overreach, underused evidence from available PDFs, and missed opportunities to strengthen Chapters 2 to 5 before submission hardening.
	- next_action: Execute the following thesis-wide work package using local PDFs in `10_resources/papers/` and chapter claims in active drafts.
		1. Build claim-citation matrix from Chapter 2 and extend mapping to Chapters 3 to 5 where literature-backed claims appear.
		2. Verify each claim against the cited PDF and record verdicts: supported, partially_supported, weak_support, or mismatch.
		3. Extract high-value direct evidence per paper: findings, limitations, trade-offs, methods, and dataset constraints.
		4. Record replacement-citation options where current support is weak or indirect.
		5. Produce chapter-targeted hardening notes: claim rewrites, citation swaps, and insertion opportunities.
		6. Add thesis-wide literature leverage backlog with priority labels (P0 defendability, P1 quality uplift, P2 stretch).
	- owner: AI + user
	- status: open
	- due_window: 2026-03-19 to 2026-03-24

## Resolved
- UI-001 (2026-03-15): Parser mismatch between author-year Chapter 2 style and key-based claim extractor.
	- resolution: Extended `09_quality_control/run_ch2_verbatim_audit.py` to map author-year citations to source-index keys and regenerate current audit output with non-zero claim extraction.
