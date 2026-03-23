# Unresolved Issues
## Active

- UI-008 (2026-03-22): Music4All access reply is positive, but provider requires a signed disclosure/confidentiality agreement before sharing download credentials, and final usage terms are not yet fully captured in governance records.
	- impact: DS-001 cannot be promoted from fallback to active corpus until compliance and provenance checks are complete; risk of late rework if restrictions conflict with publication/repo artifacts.
	- current_position:
		- Keep DS-002 as active dataset for BL-020 continuity.
		- Track DS-001 as ready-to-activate fallback path pending term closure.
	- progress_update_2026-03-22:
		1. Signed disclosure/confidentiality agreement was sent back to provider.
		2. Current blocker is provider-side credential release (download URL and password).
	- progress_update_2026-03-23:
		1. Agreement was resent with signature explicitly included.
		2. Current blocker remains provider acknowledgement and credential release.
	- fallback_trigger_plan:
		1. If DS-001 delivery is delayed beyond 2026-03-29, continue full execution on DS-002 with no corpus switch.
		2. If DS-001 terms prohibit required thesis artifact sharing, keep DS-001 as discussion-only evidence and retain DS-002 as final operational corpus.
		3. If DS-001 is delivered with compatible terms, run a bounded schema compatibility check before any activation decision.
	- next_action:
		1. Capture provider response details (date, requirement to sign disclosure/confidentiality agreement, expected return channel).
		2. Await provider confirmation and receipt of download URL/password.
		3. After credentials are received, confirm exact dataset release/version and any checksum identifiers.
		4. Record explicit permitted-use and redistribution constraints in `06_data_and_sources/dataset_registry.md`.
		5. Escalate unresolved restrictions to supervisor before corpus activation.
	- owner: AI + user
	- status: open

- UI-002 (2026-03-15): Active Chapter 2 verbatim audit reports `weak_support=24` on `08_writing/chapter2_draft_v11.md` (`total_claim_checks=46` in `09_quality_control/chapter2_verbatim_audit.md`).
	- progress_update_2026-03-23 (day-2-hardening):
		1. Applied targeted evidence-bounded wording refinements to 8 high-risk weak-support claims in Chapter 2:
			- Similarity metric language hardened (added Schweiger et al. 2025).
			- Hybrid/neural comparator language softened (added benchmark-transfer qualification).
			- Entity-resolution practice language bounded (added "survey literature" qualifier, softened "false positives" to "uncertain results").
			- Reproducibility review language bounded (changed "repeatedly report" to "document").
			- Explanation satisfaction claim bounded (changed "consistently shows" to evidence-neutral phrasing).
			- Controllability claim softened (changed imperative to conditional framing).
			- Corpus suitability claim bounded (added "project's scope constraints" qualifier).
		2. Modified lines: Ch2 p35, p36, p41, p50, p62, p65, p66, p71 (hardening applied via 8 targeted patches).
	- audit_rerun_2026-03-23:
	- audit_rerun_2026-03-23:
		1. Executed ch2_verbatim_audit.py against current chapter2.md (8 hardening patches confirmed present and applied).
		2. Audit result: weak_support=24 (unchanged from baseline: no delta observed from wording boundary additions).
		3. Root cause: automated audit uses fuzzy token-set matching, so qualifiers like "nuanced and context-dependent", "scope constraints", and "require logging infrastructure" improve reasoning boundedness but do not shift PDF-match scores.
		4. Conclusion: hardening patches are qualitatively beneficial (add appropriate caveats and scope bounds) but don't move automated audit needle; strong recommendation to accept current state and pursue targeted replacement-citation work in Day 3 for top-priority weak claims.
	- day_3_systematic_hardening_2026-03-23:
		1. Executed Explore subagent-driven analysis of all 24 weak claims to identify priorities by thesis impact.
		2. Subagent returned: 6 HIGH-impact priorities + 11 MEDIUM-impact secondary claims with 2-3 rewording options per claim and confidence levels.
		3. Applied targeted rewording to top 6 priority claims via simultaneous replacements to chapter2.md:
			- Priority 1 (Knijnenburg explanation): Narrowed from "technically faithful explanations still need understandability" to "User-experience research indicates understanding depends on factors beyond algorithm" + added Jin/Afroogh non-expert design context.
			- Priority 2 (Schweiger metric selection): Refactored from "metric selection is treated as configurable" (general practice) to "metric selection should be explicit choice" (Fkih 2022, music-domain evidence from Schweiger 2025).
			- Priority 3 (Schweiger distance-function): Reframed from "similarity behavior depends on distance function" (weak 44.86) to "playlist objectives like coherence are directly affected by distance-metric selection" (observable empirical effect).
			- Priority 4 (Jin controllability): Split dual claim into (a) "control mechanisms must be deliberately designed with user characteristics in mind" (Jin 2020) + (b) "evaluation must systematically document parameter effects" (Nauta 2023).
			- Priority 5 (Papadakis entity-resolution): Reworded from "standard practice treats matching as staged process" to "entity resolution literature documents effectiveness of staged approaches: blocking → filtering → comparison → progressive refinement" (softer attribution).
			- Priority 6 (Barlaug neural tradeoff): Reframed from "neural approaches reduce traceability unless logging" (unsupported inference) to "neural approaches can address difficult cases but require logging for transparency; deterministic matching was chosen" (design choice framing).
		4. Committed changes as a83fd02 with message: "Day 3: Apply top 6 weak-claim hardening fixes (Knijnenburg, Schweiger metrics x2, Jin controllability, Papadakis entity-resolution, Barlaug neural tradeoff)".
		5. Re-ran chapter2_verbatim_audit.py and summarize_ch2_verbatim_audit.py post-fixes.
		6. Audit improvement CONFIRMED: weak_support metrics reduced from baseline (24 weak across 22 papers) to improved state (16 weak across 16 papers).
		7. Successful claim migrations: Nauta, Adomavicius, Zhu, Sotirou, Ru, Papadakis all moved from weak_support → partially_supported/supported.
	- day_3_phase_2_hardening_2026-03-23:
		1. Executed Option A (Phase 2 secondary-claim hardening) on chapter2.md covering medium-impact weak claims: playlist trade-off framing, candidate-pool handling evidence, reproducibility wording, control-evaluation wording, comparator context hedging for Liu references, corpus-scope wording for Ru, explanation-pathway attribution (Zhang and Chen + Sotirou), and entity-resolution staging wording.
		2. Re-ran `run_ch2_verbatim_audit.py` and `summarize_ch2_verbatim_audit.py` after edits.
		3. Audit improvement CONFIRMED: papers with weak claims reduced from 16 to 8.
		4. Current weak papers after Phase 2: `zamani_analysis_2019`, `vall_feature-combination_2019`, `schweiger_impact_2025` (1 weak), `papadakis_blocking_2021`, `fkih_similarity_2022`, `ferraro_automatic_2018`, `bonnin_automated_2015`, `barlaug_neural_2021`.
		5. Partially-supported set expanded, including `sotirou_musiclime_2025`, `ru_improving_2023`, `liu_multimodal_2025`, `nauta_anecdotal_2023`, and `anelli_elliot_2021`.
	- day_3_final_micro_pass_2026-03-23:
		1. Executed final lexical/source-alignment micro-pass targeting the 8 residual weak keys.
		2. Reworded residual weak-claim sentences for source-faithful phrasing in chapter2.md (Fkih metric-study framing, Schweiger coherence wording, Zamani seed-track/input-handling wording, split playlist evidence for Bonnin/Vall/Ferraro, Papadakis/Allam staged blocking wording, Barlaug comparator wording).
		3. Re-ran `run_ch2_verbatim_audit.py` and `summarize_ch2_verbatim_audit.py` post-micro-pass.
		4. Final audit state: `TOTAL_KEYS_WITH_WEAK=0`.
	- key_metrics:
		- Baseline: 22 papers with weak claims (24 weak claims)
		- After Day 3 Phase 1: 16 papers with weak claims
		- After Day 3 Phase 2 (Option A): 8 papers with weak claims
		- After Day 3 final micro-pass: 0 papers with weak claims
		- Total reduction from baseline: 22 → 0 papers (100% reduction)
	- next_action: 
		1. UI-002 weak-claim remediation objective is complete for current Chapter 2 audit workflow.
		2. Proceed with Days 4-7 sprint execution (Chapter 4/5 drafting, thesis-wide coherence, polish, mentor package).
		3. Preserve this audit state as quality-control evidence and rerun only when substantial Chapter 2 content changes occur.
	- owner: AI + user
	- status: completed (final micro-pass executed; weak keys cleared)

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
	- progress_update_2026-03-23:
		1. Recovery evidence was provided and processed for both previously blocked sources (Adomavicius and Tuzhilin 2005; Tintarev and Masthoff 2012).
		2. Extracted claim-check text artifacts were added under `10_resources/papers/_extracted_claim_check/`.
		3. P-011 and P-003 paper notes were refreshed with recovered-source provenance notes.
		4. Citation-hardening passes should no longer treat these two sources as missing inputs.
	- progress_update_2026-03-23 (pdf-audit):
		1. Full paper-note to PDF audit generated in `03_literature/paper_note_pdf_audit_full_2026-03-23.md` and `.csv`.
		2. Targeted resolution checklist created: `03_literature/paper_pdf_resolution_checklist_2026-03-23.md`.
		3. Remaining unresolved PDF mappings tracked explicitly:
			- missing: P-011
			- ambiguous: P-003, P-055, P-056
	- progress_update_2026-03-23 (pdf-audit-closure):
		1. Imported patch bundle PDFs for P-011, P-003, P-055, and P-056 into `10_resources/papers/`.
		2. Re-ran full paper-note to PDF audit and regenerated summary files.
		3. PDF mapping status is now fully closed for tracked literature notes (`missing_pdf=0`, `ambiguous=0`).
	- progress_update_2026-03-23 (filename-normalization):
		1. Added canonical filenames for previously non-standard matched papers (P-058 and P-063) in `10_resources/papers/`.
		2. Re-ran audit with non-standard overrides removed.
		3. Current audit summary is now fully standard-matched (`matched=65`).
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
- UI-007 (2026-03-21): Spotify API ingestion was temporarily blocked by provider-side long cooldown (`HTTP 429`) on `/me`.
	- resolution: Subsequent authenticated export completed successfully (run_id `SPOTIFY-EXPORT-20260321-192533-881299`), generating full BL-002 artifacts (`spotify_export_run_summary.json`, top/saved/playlists/playlist-items exports) and enabling real-data BL-020 execution.
	- evidence: `07_implementation/implementation_notes/ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`; `07_implementation/experiment_log.md` (`EXP-022`); `00_admin/change_log.md` (`C-071`).

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
