# Unresolved Issues

## Active
- UI-002 (2026-03-15): Active Chapter 2 verbatim audit reports `weak_support=24` on `08_writing/chapter2_draft_v11.md` (`total_claim_checks=46` in `09_quality_control/chapter2_verbatim_audit.md`).
	- impact: Chapter 2 cannot be treated as fully citation-hardened under the current zero-weak closure rule.
	- next_action: Perform targeted sentence-level wording hardening for weak-support claims, then rerun audit until `weak_support=0` or approve a bounded non-zero threshold.
	- owner: AI + user
	- status: open

## Resolved
- UI-001 (2026-03-15): Parser mismatch between author-year Chapter 2 style and key-based claim extractor.
	- resolution: Extended `09_quality_control/run_ch2_verbatim_audit.py` to map author-year citations to source-index keys and regenerate current audit output with non-zero claim extraction.
