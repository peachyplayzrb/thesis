# Unresolved Issues
## Active

- UI-007 (2026-03-21): Spotify API ingestion currently blocked by provider-side long cooldown (`HTTP 429`) on `/me` despite conservative batching/throttling settings.
	- impact: Live BL-002 Spotify export artifacts (top tracks, saved tracks, playlists, playlist items) cannot be completed until cooldown expires or credentials rotate.
	- observed_evidence:
		- `retry_after_seconds=84882`
		- `retry_at_utc=2026-03-22T02:40:32Z`
		- blocker artifact: `07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_rate_limit_block.json`
	- next_action:
		1. Retry after `retry_at_utc` with current conservative run flags.
		2. If cooldown persists, rotate to a new Spotify app `client_id/client_secret`, remove token cache, and run with `--force-auth`.
	- owner: AI + user
	- status: open

- UI-002 (2026-03-15): Active Chapter 2 verbatim audit reports `weak_support=24` on `08_writing/chapter2_draft_v11.md` (`total_claim_checks=46` in `09_quality_control/chapter2_verbatim_audit.md`).
	- next_action: Perform targeted sentence-level wording hardening for weak-support claims, then rerun audit until `weak_support=0` or approve a bounded non-zero threshold.
	- owner: AI + user
	- status: open

- UI-003 (2026-03-19): Thesis-wide citation verification and literature leverage pass not yet fully tracked in repository control files.
	- impact: Risk of citation overreach, underused evidence from available PDFs, and missed opportunities to strengthen Chapters 2 to 5 before submission hardening.
	- progress_update_2026-03-19:
		1. Governance tracking created and logged (`C-013`) with active timeline work package (`WP-CITE-001`).
		2. Initial PDF claim-validation and extracted-evidence artifacts committed under `10_resources/papers/_extracted/` and `10_resources/papers/_extracted_claim_check/`.
		3. Chapter 2 master draft and related writing artifacts committed for traceability.
		4. Remaining work centers on full completion of the UI-003 action list and final synthesis report.
	- progress_update_2026-03-21:
		1. Two literature-pack PDFs were not extractable in the current workflow and are now explicitly tracked:
			- `10_resources/previous_drafts/lit_review_resource_pack/files/381/Adomavicius and Tuzhilin - 2005 - Toward the next generation of recommender systems a survey of the state-of-the-art and possible ext.pdf`
			- `10_resources/previous_drafts/lit_review_resource_pack/files/391/Tintarev and Masthoff - 2012 - Evaluating the effectiveness of explanations for recommender systems Methodological issues and empi.pdf`
		2. Citation-hardening runs that depend on these sources should treat them as missing inputs until recoverable copies are restored or equivalent sources are substituted.
	- next_action: Execute the following thesis-wide work package using local PDFs in `10_resources/papers/` and chapter claims in active drafts.
		1. Build claim-citation matrix from Chapter 2 and extend mapping to Chapters 3 to 5 where literature-backed claims appear.
		2. Verify each claim against the cited PDF and record verdicts: supported, partially_supported, weak_support, or mismatch.
		3. Extract high-value direct evidence per paper: findings, limitations, trade-offs, methods, and dataset constraints.
		4. Record replacement-citation options where current support is weak or indirect.
		5. Produce chapter-targeted hardening notes: claim rewrites, citation swaps, and insertion opportunities.
		6. Add thesis-wide literature leverage backlog with priority labels (P0 defendability, P1 quality uplift, P2 stretch).
	- status: open
	- due_window: 2026-03-19 to 2026-03-24

## Resolved
- UI-006 (2026-03-21): Governance mismatch after DS-002 activation where `thesis_state.md` still stated Music4All/Music4All-Onion as current primary scope.
	- resolution: Synchronized `00_admin/thesis_state.md` to DS-002 active wording and aligned related objective/assumption/limitation phrasing; marked issue closed after synchronization.
	- evidence: `00_admin/thesis_state.md` (2026-03-21 update), `00_admin/change_log.md` (`C-042`).

- UI-005 (2026-03-19): Base Music4All is unusable in the current environment; Onion-only workaround was the active interim path.
	- resolution: Superseded by 2026-03-21 planning decision `D-015`, which activates DS-002 as the current BL-019 strategy.
	- evidence: `00_admin/decision_log.md` (`D-015`); `06_data_and_sources/dataset_registry.md` DS-002 status update.


- UI-004 (2026-03-19): Candidate corpus change review between Music4All-Onion and `MSD subset + Last.fm Tag Dataset + MusicBrainz mapping`.
	- resolution: BL-018 feasibility review completed. Result: do not switch corpus. Keep Music4All-Onion as the active MVP corpus and retain the MSD-based option as fallback only.
	- evidence: `07_implementation/implementation_notes/data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; `00_admin/decision_log.md` D-008.

- UI-001 (2026-03-15): Parser mismatch between author-year Chapter 2 style and key-based claim extractor.
	- resolution: Extended `09_quality_control/run_ch2_verbatim_audit.py` to map author-year citations to source-index keys and regenerate current audit output with non-zero claim extraction.
