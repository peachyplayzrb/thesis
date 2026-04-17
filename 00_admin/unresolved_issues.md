# Unresolved Issues

Last updated: 2026-04-17 UTC (UNDO-G/UNDO-H/UNDO-I closure decisions finalized; six active design-verification items remain)

## Active

### UNDO-A: Profile intake validation — Roy & Dutta (2022) input data quality caveat

**Status**: Open, Medium priority (design verification)

**Trigger**: Chapter 3 Section 3.6 states alignment treats uncertainty as visible through diagnostics, and Section 3.7 states profile construction is normative. Roy & Dutta (2022) finding: interaction evidence may reflect convenience/exposure rather than stable preference. Design question: does profile intake reject/flag low-fidelity evidence before it enters downstream operations?

**Description**: While Chapter 3 emphasizes that uncertainty remains visible at the point where evidence enters the system, Chapter 3 does not explicitly specify what profile-intake validation prevents structurally low-quality rows from entering profile construction. Investigate whether BL-004 (profiling stage) enforces explicit row-quality gates that distinguish and surface low-confidence/weak-evidence rows in observability output.

**Implementation contact**: `07_implementation/src/profiling.py` (BL-004); `07_implementation/implementation_notes/bl004_profiling/`

**Blocking**: No (design verification, not critical path); planned investigation after Chapter 5/6 proofing or as pre-submission design audit.

---

### UNDO-B: Sequential coherence in playlist assembly — Schedl et al. (2018) music-specific dynamics caveat

**Status**: Open, Medium-High priority (design verification)

**Trigger**: Chapter 3 Section 3.10 describes multi-objective playlist assembly (coherence, diversity, novelty, ordering) but does not explicitly ground coherence in music-specific sequential/relational listening. Schedl et al. (2018) finding: music consumption is sequential and relational, not purely itemwise. Design question: does BL-007 assembly model sequential/transition coherence between adjacent tracks?

**Description**: Chapter 3 lists coherence as one of four competing objectives in playlist assembly but does not specify whether coherence models sequential relationships or only item-level similarity. Investigate whether BL-007 (assembly stage) constrains transition coherence or only item-level feature similarity.

**Implementation contact**: `07_implementation/src/playlist/rules.py` (BL-007); Chapter 4 Sections 4.6-4.7 (assembly rule implementation)

**Blocking**: No; escalate to decision entry if sequential coherence is absent and design claims sequential sensitivity.

---

### UNDO-C: Candidate-shaping diagnostics fidelity — Zamani & Ferraro (2018/2019) visibility caveat

**Status**: Open, Medium priority (design verification)

**Trigger**: Chapter 3 Section 3.8 emphasizes candidate shaping must "show how many items were retained, why other items were filtered out, and how strongly the current profile settings determined the reachable search space." Zamani/Ferraro finding: candidate generation is most consequential but least visible. Design question: do BL-005 diagnostics expose threshold effects, exclusion categories, and pool-size trends with sufficient detail?

**Description**: Chapter 3 Section 3.8 states candidate shaping must show filtering logic completely. Investigate whether BL-005 (retrieval/candidate-shaping stage) surfaces threshold-effect counts, exclusion category diagnostics, candidate-pool size trends, and control-effect observability at the detail level claimed by design.

**Implementation contact**: `07_implementation/src/retrieval.py` (BL-005); `07_implementation/src/observability.py` (BL-009); `07_implementation/implementation_notes/bl005_retrieval/`

**Blocking**: No; planned investigation during Chapter 5 evaluation setup or design-audit pass.

---

### UNDO-D: Scoring sensitivity diagnostics hardening — Fkih et al. (2022) and Flexer (2016) metric-subjectivity caveat

**Status**: Open, Medium-High priority (design verification)

**Trigger**: Chapter 3 Section 3.9 positions deterministic scoring as a weighted approximation of preference fit. Fkih et al. (2022) indicates similarity-function choice materially changes recommendation outcomes, and Flexer (2016) indicates music similarity has subjective agreement limits. Design question: does BL-006 expose run-level sensitivity and uncertainty-facing diagnostics that make this dependency explicit?

**Description**: Current BL-006 outputs report component contributions but do not provide a dedicated sensitivity slice that quantifies score/rank movement under bounded scoring-component perturbations. Investigate whether BL-006 should emit additive sensitivity diagnostics (for example top-k overlap shift, rank volatility, and component-dominance change) so scoring claims remain explicitly approximation-bounded.

**Implementation contact**: `07_implementation/src/scoring/scoring_engine.py` (BL-006); `07_implementation/src/scoring/result_reporter.py`; `07_implementation/src/quality/sanity_checks.py` (BL-014 advisories)

**Blocking**: No; escalate to decision entry if scoring rationale in Chapter 3/5 remains stronger than emitted sensitivity evidence.

---

### UNDO-E: Multi-dimensional explanation-quality metrics — Nauta et al. (2023) and Lopes et al. (2022) evaluation-fragmentation caveat

**Status**: Open, Medium priority (design verification)

**Trigger**: Chapter 3 and Chapter 5 frame explanation quality as evaluable and reproducible. Nauta et al. (2023) and Lopes et al. (2022) emphasize multi-criteria quantitative evaluation rather than anecdotal or single-metric explainability judgement. Design question: do BL-008 and BL-014 expose a sufficiently explicit explanation-quality metric vector at run level?

**Description**: BL-014 currently emits `advisory_bl008_explanation_fidelity` warnings when internal consistency checks fail, but it does not emit a compact multi-dimensional metric surface for comparison across runs. Investigate whether BL-008/BL-009/BL-014 should emit additive quantitative dimensions (for example completeness, consistency, sparsity/readability proxy, and replay stability) with explicit thresholds or comparison baselines.

**Implementation contact**: `07_implementation/src/transparency/main.py` (BL-008); `07_implementation/src/observability/main.py` (BL-009); `07_implementation/src/quality/sanity_checks.py` (BL-014)

**Blocking**: No; planned as a design-audit enhancement before final Chapter 5 evaluation hardening.

---

### UNDO-F: Human-centered controllability interpretation proxies — Knijnenburg et al. (2012) and Afroogh (2024) trust-boundary caveat

**Status**: Open, Medium priority (design verification)

**Trigger**: BL-011 currently verifies that configuration variants produce observable shifts, but literature indicates trust/acceptance is multi-factor and not inferable from transparency alone. Design question: does controllability evaluation include interpretable proxy summaries that avoid over-claiming human-centered outcomes?

**Description**: Current BL-011 evidence demonstrates deterministic and observable variant shifts, but lacks an explicit proxy layer that summarizes whether those shifts remain interpretable to a human reviewer (for example concentration of effects, rank-locality of change, and explanation-driver stability under variant perturbation). Investigate whether additive BL-011 reporting should expose these bounded interpretation proxies.

**Implementation contact**: `07_implementation/src/controllability/analysis.py` (BL-011); `07_implementation/src/controllability/reporting.py`; `07_implementation/src/observability/main.py` (validity boundaries)

**Blocking**: No; escalate to decision entry if Chapter 6 contribution language risks implying trust or UX outcomes beyond current evidence.

---

### UNDO-G: Control-effect gate enforcement in orchestration — Control Testing Protocol and Control Surface Registry contract gap

**Status**: Closed (implemented), Medium-High priority (design verification)

**Trigger**: `05_design/CONTROL_TESTING_PROTOCOL.md` and `05_design/CONTROL_SURFACE_REGISTRY.md` require measurable control effects and escalation for zero-effect controls. Design question: is control-effect validation enforced as a first-class gate in the active BL-013/BL-014 execution flow rather than as an external manual check?

**Description**: Current protocol guidance defines measurable-effect thresholds and escalation behavior. Implementation is now complete in BL-014: `advisory_bl011_control_effect_gate` surfaces weak/no-op controls from BL-011 result metrics, `gate_results` records policy-backed warn/strict gate status with strict fail escalation, and policy resolution is config-first from BL-009 run-config observability validation policies before snapshot/report/env/default fallback.

**Implementation contact**: `07_implementation/src/quality/suite.py` (BL-013 orchestration quality flow); `07_implementation/src/quality/sanity_checks.py` (BL-014 checks); `07_implementation/src/controllability/analysis.py` (effect metrics)

**Blocking**: No; closure formalized on current implementation evidence.

---

### UNDO-H: Unified control-causality payload contract — Transparency Design/Addendum cross-stage trace gap

**Status**: Closed (implemented), Medium priority (design verification)

**Trigger**: `05_design/transparency_design.md`, `05_design/transparency_design_addendum.md`, and `05_design/TRANSPARENCY_SPEC.md` require explicit linkage from user controls to downstream decisions. Design question: do BL-008/BL-009 expose one unified control-causality block per track/run that ties accepted/rejected outcomes to concrete control values?

**Description**: Existing explanations and observability outputs were previously fragmented across stages, but implementation is now complete. BL-008 payloads emit per-track `control_causality` blocks plus additive rejected-track control-causality payloads; BL-009 emits `control_causality_summary` and `rejected_control_causality_summary`; BL-014 emits advisory and policy-backed gate coverage (`gate_bl008_control_causality_contract`) with strict fail escalation.

**Implementation contact**: `07_implementation/src/transparency/main.py` (BL-008 payloads); `07_implementation/src/observability/main.py` (BL-009 aggregation); `07_implementation/src/playlist/stage.py` and `07_implementation/src/retrieval.py` (source diagnostics)

**Blocking**: No; closure formalized on current implementation evidence.

---

### UNDO-I: BL-005 threshold-attribution and what-if diagnostics — Design-level filtering rationale gap

**Status**: Closed (implemented), Medium priority (design verification)

**Trigger**: `05_design/transparency_design_addendum.md` identifies partial BL-005 rejection rationale and missing threshold-impact summaries/counterfactual hints. Design question: does retrieval diagnostics show which thresholds dominate rejection volume and what directional pool change is expected under bounded threshold relaxation/tightening?

**Description**: Implementation is now complete. BL-005 diagnostics emit additive `threshold_attribution` and `bounded_what_if_estimates`; BL-014 emits advisory and policy-backed gate coverage (`gate_bl005_threshold_diagnostics_contract`) with warn default / strict fail escalation; policy resolution is config-first from BL-009 run-config validation policies before env/default fallback.

**Implementation contact**: `07_implementation/src/retrieval.py` (BL-005 diagnostics); `07_implementation/src/observability/main.py` (BL-009 summary surfaces); `07_implementation/src/quality/sanity_checks.py` (contract checks)

**Blocking**: No; closure formalized on current implementation evidence.

Active-set sync note (2026-04-14 mentor bundle validation): Confirmed no new active blocker after the mentor handoff bundle validation/package pass. A bundle-local BL-007 syntax defect in `07_implementation/mentor_feedback_submission/src/playlist/rules.py` was corrected, and the bundle wrapper now passes BL-013 (`BL013-ENTRYPOINT-20260414-121918-379574`) plus BL-014 (`BL014-SANITY-20260414-121945-312010`, `36/36`).


Active-set sync note (2026-03-25 18:25 UTC): Open items are UI-003 (citation package closure) and UI-013 (pipeline optimization and evidence-hygiene closure).
Active-set sync note (2026-03-25 22:55 UTC): Open items remain UI-003 (citation package closure) and UI-013 (pipeline optimization and evidence-hygiene closure); UI-013 control-surface uplift is implemented, optimization tuning closure is pending.
Active-set sync note (2026-03-25 23:00 UTC): Open items remain UI-003 and UI-013; UI-013 BL-008 explanation-dominance criterion is now passing under the v1b profile, with remaining closure work centered on BL-010/BL-011 path-semantics normalization and final evidence packaging.
Active-set sync note (2026-03-25 23:10 UTC): Open items remain UI-003 and UI-013; UI-013 path-semantics normalization for BL-010/BL-011 is now implemented and revalidated (`BL010-REPRO-20260325-231041`, `BL011-CTRL-20260325-231130`, freshness `BL-FRESHNESS-20260325-231159`), leaving final evidence packaging as the remaining closure step.
Active-set sync note (2026-03-26 UTC): Open items remain UI-003 and UI-013. Implementation hardening pass completed (C-176/C-177): artifact-load validation hardened across BL-003/BL-008/BL-009/BL-010/BL-011/DS-001 with fail-fast helpers and schema guards; BL-006 scoring engine empty lead-genre false match fixed. BL-010/BL-011/BL-014 all pass on updated baseline. UI-013 remaining work is final evidence packaging and BL-005/BL-006 tuning sweep closure.
Active-set sync note (2026-03-26 17:56 UTC): Open items remain UI-003 and UI-013. BL-006 contribution semantics are now corrected and BL-007 to BL-009 lineage has been refreshed (`BL006-SCORE-20260326-175531-101302`, `BL007-ASSEMBLE-20260326-175552-183434`, `BL008-EXPLAIN-20260326-175552-995824`, `BL009-OBSERVE-20260326-175553-758828`, `BL014-SANITY-20260326-175554-065408`). This fixes a real transparency/evidence bug, but BL-008 diversity evidence must be regenerated under the corrected weighted-contribution contract before UI-013 can be closed.
Active-set sync note (2026-03-26 18:06 UTC): Open items now reduce to UI-003 only. UI-013 is closed after refreshed v1b acceptance evidence on the corrected BL-006 weighted-contribution contract passed all thresholds (`BL013-ENTRYPOINT-20260326-180047-134553`, `BL014-SANITY-20260326-180057-357905`; BL-008 dominance `0.3`, BL-005 kept `54402`, BL-003 match rate `0.1595`).
Active-set sync note (2026-03-26 21:03 UTC): Open active item remains UI-003 (citation package closure). Pipeline is now stable on the v1f baseline (`run_config_ui013_tuning_v1f.json`): danceability, energy, and valence are active end-to-end in BL-005 and BL-006; BL-013 restore `BL013-ENTRYPOINT-20260326-210305-914179` and BL-014 sanity pass (`22/22`). BL-010 reproducibility pass (`BL010-REPRO-20260326-205834`); BL-011 controllability pass (`BL011-CTRL-20260326-205932`). Active freshness suite at `6/8` — non-blocking evidence-alignment caveat documented in CODEBASE_ISSUES_CURRENT.md. Planned next steps: freshness re-alignment, UI-003 citation closure, chapter alignment to v1f counts, and evaluation evidence packaging for Chapter 5.
Active-set sync note (2026-03-26 21:27 UTC): Freshness re-alignment is complete. BL-010 pass (`BL010-REPRO-20260326-212523`), BL-011 pass (`BL011-CTRL-20260326-212611`), BL-013 restore pass (`BL013-ENTRYPOINT-20260326-212711-234744`), BL-014 sanity pass (`BL014-SANITY-20260326-212725-976781`), and active freshness suite pass (`BL-FRESHNESS-SUITE-20260326-212726`, `7/7`). Open active issue remains UI-003 only.
Active-set sync note (2026-03-26 22:30 UTC): Evidence audit completed for the canonical v1f baseline (EXP-048 / C-182). All 10 playlist track titles resolved from `ds001_working_candidate_dataset.csv`. BL-010/BL-011 config-snapshot divergence documented: BL-010 uses 70,680 candidates (pinned snapshot), BL-011 uses 33,096 (pinned snapshot), canonical v1f uses 46,776; both evaluation passes remain valid on their respective pinned states. Key chapter-alignment numbers confirmed: 46,776 filtered candidates, 10 scoring components, 22/22 sanity checks, 7/7 freshness, 1064 seeds, ~84% alignment miss rate. Dissertation claims by strength packaged. Open active issue remains UI-003 only.
Active-set sync note (2026-03-27 01:22 UTC): v1f evidence refresh and document-consistency pass completed. BL-013 pass (`BL013-ENTRYPOINT-20260327-012149-023331`), BL-014 sanity pass (`BL014-SANITY-20260327-011939-797165`, `22/22`), BL-010 pass (`BL010-REPRO-20260327-011941`), BL-011 pass (`BL011-CTRL-20260327-012056`), and active freshness suite pass (`BL-FRESHNESS-SUITE-20260327-012201`, `19/19`). Chapter 4 EP matrix rows are now populated and abstract draft is in place. Open active issue remains UI-003 only.
Active-set sync note (2026-03-27 03:05 UTC): UI-003 closure package is now complete at control-record level. Chapters 3 to 5 claim-verdict matrix and chapter-targeted hardening notes are logged in `09_quality_control/ui003_claim_verdicts_ch3_ch5.md` and `09_quality_control/ui003_chapter_hardening_notes_ch3_ch5.md`. No active unresolved issues remain.
Active-set sync note (2026-03-29 UTC): Confirmed no active unresolved issues. Architecture migration wave (BL-003 typed boundaries + stage-shell, BL-004 through BL-007 OO migration + controllable-logic uplift) is complete and logged. Documentation sync C-219 is complete. 00_admin full synchronization wave C-220 is in progress. Only remaining active scope is physical submission packaging.
Active-set sync note (2026-03-30 UTC): Aggressive root archival wave accepted and executed (D-044/C-222). No new unresolved blocker opened by this operation; active runtime posture remains `07_implementation/main.py` with archived root wrappers/config surfaces retained in deep archive.
Active-set sync note (2026-04-09 UTC): Confirmed no active unresolved issues after the pyright/full-contract closure wave. The active `07_implementation` runtime path revalidated clean with pytest `361/361`, pyright `0 errors, 0 warnings, 0 informations`, BL-013 pass `BL013-ENTRYPOINT-20260409-180340-350614`, and BL-014 pass `BL014-SANITY-20260409-180356-824725` (`28/28`).
Active-set sync note (2026-04-09 runtime-root governance): Confirmed no active blocker. Workflow authority is now explicitly anchored to `07_implementation/`; `_scratch/` (including `_scratch/final_artefact_bundle/`) is reference-only and should not be treated as active runtime control surface.
Active-set sync note (2026-04-10 zero-trust audit closeout): Confirmed no new unresolved blocker from the Chapter 2 zero-trust reference audit cycle; all citations extracted from the frozen Chapter 2 baseline received manual verdicts, and no citation remained unverifiable.
Active-set sync note (2026-04-12 user_csv validation closeout): Confirmed no active blocker after BL-003 `user_csv` integration validation. Wrapper pass `BL013-ENTRYPOINT-20260412-211514-304085` and sanity pass `BL014-SANITY-20260412-211538-292523` (`28/28`) succeeded with a live sample `user_csv_flat.csv`; BL-003 summary and BL-009 observability outputs both record `user_csv=10` rows under advisory policy.
Active-set sync note (2026-04-12 configurable fuzzy wave-1 closeout): Confirmed no active blocker after the BL-003 fuzzy-control rollout. Targeted BL-003 tests passed (`97/97`), full pytest passed (`411/411`), and wrapper validation remained green (`BL013-ENTRYPOINT-20260412-213836-591492`, `BL014-SANITY-20260412-213859-249947`, `28/28`) with exact-match precedence unchanged.
Active-set sync note (2026-04-13 row-quality handshake + unmatched-classification closeout): Confirmed no active blocker after Slice 12 completion. BL-004 row-quality handshake checks and strict synthetic-reconstruction enforcement plus BL-003 unmatched-reason classification are implemented and validated (`pytest 25/25`; `BL013-ENTRYPOINT-20260413-011824-759642`; `BL014-SANITY-20260413-011850-557804`, `29/29`).
Active-set sync note (2026-04-13 semantic-alignment clarity closeout): Confirmed no active blocker after Slice 13 completion. BL-004 now emits explicit diagnostics-basis metadata and BL-003 event-level companion counters to prevent row/event interpretation drift, and BL-004 payloads now carry `bl003_config_source` for provenance continuity (`pytest 24/24`; `BL013-ENTRYPOINT-20260413-014731-291681`; `BL014-SANITY-20260413-014753-532309`, `29/29`).
Active-set sync note (2026-04-13 BL-005 handshake hardening closeout): Confirmed no active blocker after Slice 14 completion. BL-005 now enforces policy-gated BL-004 handshake validation with additive diagnostics, and BL-014 now includes `schema_bl004_bl005_handshake_contract` continuity checks (`pytest 48/48`; `BL013-ENTRYPOINT-20260413-103628-028213`; `BL014-SANITY-20260413-103658-484887`, `30/30`).
Active-set sync note (2026-04-13 BL-005 parity-closure closeout): Confirmed no active blocker after Slice 16 completion. BL-005 retrieval handshake validation now includes seed-trace confidence row-quality checks and BL-014 now has symmetric main-level negative fixture evidence for `schema_bl004_bl005_handshake_contract` failure behavior (`pytest 20/20`; `BL013-ENTRYPOINT-20260413-105724-234842`; `BL014-SANITY-20260413-105751-328487`, `30/30`).
Active-set sync note (2026-04-13 BL-005 runtime-control diagnostics closeout): Confirmed no active blocker after Slice 17 completion. BL-005 now emits explicit runtime-control fallback/coercion diagnostics (payload parse-error and normalization event metadata) in retrieval diagnostics payloads, with focused tests and wrapper validation green (`pytest 9/9`; `BL013-ENTRYPOINT-20260413-111111-723084`; `BL014-SANITY-20260413-111136-703270`, `30/30`).
Active-set sync note (2026-04-13 BL-005 advisory-visibility closeout): Confirmed no active blocker after Slice 18 completion. BL-014 now emits `advisory_bl005_control_resolution_fallback_volume` for elevated BL-005 control-resolution normalization/coercion volume and records the advisory threshold in config snapshot metadata (`pytest 27/27`; `BL013-ENTRYPOINT-20260413-111934-887225`; `BL014-SANITY-20260413-111957-022045`, `30/30`).
Active-set sync note (2026-04-13 BL-006 handshake/diagnostics parity closeout): Confirmed no active blocker after Slice 19 completion. BL-006 now enforces policy-gated BL-005↔BL-006 handshake validation with runtime-control diagnostics parity fields, and BL-014 now enforces `schema_bl005_bl006_handshake_contract`; validation is green (`pytest 58/58`; `BL013-ENTRYPOINT-20260413-114004-966558`; `BL014-SANITY-20260413-114023-656004`, `31/31`).
Active-set sync note (2026-04-13 BL-014 handshake advisory closeout): Confirmed no active blocker after Slice 15 completion. BL-014 now emits `advisory_bl005_handshake_warning_volume` for elevated BL-005 warn-mode handshake violations while preserving pass/fail contract checks (`pytest 14/14`; `BL013-ENTRYPOINT-20260413-104436-925545`; `BL014-SANITY-20260413-104503-647428`, `30/30`).
Active-set sync note (2026-04-13 BL-007 diagnostics-fidelity + influence-effectiveness closeout): Confirmed no active blocker after Slice 20 completion. BL-007 now distinguishes post-fill unprocessed exclusions from true in-loop length-cap events and emits additive influence-effectiveness diagnostics in assembly reports; validation is green (`pytest 14/14`; `BL013-ENTRYPOINT-20260413-120151-300654`; `BL014-SANITY-20260413-120211-217312`, `31/31`).
Active-set sync note (2026-04-13 BL-007 opportunity-cost control-surface closeout): Confirmed no active blocker after Slice 21 completion. BL-007 now supports configurable opportunity-cost diagnostic sample sizing via additive `opportunity_cost_top_k_examples` controls across run-config/runtime/stage surfaces; validation is green (`pytest 46/46`; `BL013-ENTRYPOINT-20260413-120730-444412`; `BL014-SANITY-20260413-120749-603771`, `31/31`).
Active-set sync note (2026-04-13 BL-007 utility-decay control-surface closeout): Confirmed no active blocker after Slice 22 completion. BL-007 now exposes additive `utility_decay_factor` end-to-end with bounded `[0.0, 1.0]` sanitization and deterministic utility-greedy rank-decay behavior when enabled; validation is green (`pytest 47/47`; `BL013-ENTRYPOINT-20260413-121526-609780`; `BL014-SANITY-20260413-121545-776184`, `31/31`).
Active-set sync note (2026-04-13 BL-007 handshake-hardening wave closeout): Confirmed no active blocker after Slice 23 completion. Policy-gated BL-006↔BL-007 handshake validation is now wired end-to-end; BL-014 raises to 32/32 checks completing the handshake hardening wave across all four stage boundaries (Slices 10, 14, 19, 23); validation is green (`pytest 482/482`; `BL014-SANITY-20260413-125444-585602`, `32/32`).
Active-set sync note (2026-04-13 BL-008 explanation-fidelity advisory closeout): Confirmed no active blocker after Slice 24 completion. BL-008 now emits additive contribution-share/margin and causal/narrative driver fields with score-banded explanation wording, and BL-014 now emits warn-safe advisory `advisory_bl008_explanation_fidelity` for explanation coherence without changing fail criteria; focused validation is green (`pytest 43/43`).
Active-set sync note (2026-04-13 BL-008 provenance de-dup closeout): Confirmed no active blocker after Slice 25 completion. BL-008 now supports run-level provenance summary plus per-track provenance references with toggle-controlled inline provenance emission, preserving compatibility defaults; focused validation is green (`pytest 49/49`).
Active-set sync note (2026-04-13 BL-008 assembly-context enrichment closeout): Confirmed no active blocker after Slice 26 completion. BL-008 now enriches per-track assembly context with additive BL-007 trace/report policy metadata while preserving compatibility keys; focused validation is green (`pytest 50/50`).
Active-set sync note (2026-04-13 BL-008 handshake hardening closeout): Confirmed no active blocker after Slice 27 completion. Policy-gated BL-007↔BL-008 handshake validation now runs at the explanation-generation entry point, checking required playlist track and trace header fields; BL-014 raises to 33/33 checks completing the handshake hardening wave (Slices 10, 14, 19, 23, 27); focused validation is green (`pytest 58/58`; `D-103`, `C-336`).
Active-set sync note (2026-04-13 BL-009 handshake hardening closeout): Confirmed no active blocker after Slice 28 completion. Policy-gated BL-008↔BL-009 handshake validation now runs at the observability entry point, checking required BL-008 summary/payload structure and explanation-count consistency; BL-014 raises to 34/34 checks extending the handshake hardening wave downstream through BL-009; focused validation is green (`pytest 80/80`; `D-104`, `C-337`).

## Resolved (Recent)

- UNDO-G (2026-04-17): Control-effect gate enforcement in orchestration.
	- resolution: Closed. BL-014 now enforces policy-backed control-effect gate behavior (`warn` default / `strict` fail escalation) and resolves policy config-first from BL-009 run-config observability validation policies.
	- evidence:
		1. `00_admin/decision_log.md` (`D-155`, `D-159`, `D-161`).
		2. `00_admin/change_log.md` (`C-443`, `C-447`, `C-449`).
		3. `07_implementation/src/quality/sanity_checks.py` and full validation evidence (`pytest 563/563`, wrapper validate-only pass, full contract pass).

- UNDO-H (2026-04-17): Unified control-causality payload contract.
	- resolution: Closed. BL-008/BL-009 now expose unified control-causality surfaces for included and rejected tracks, and BL-014 enforces policy-backed contract gating (`warn` default / `strict` fail escalation).
	- evidence:
		1. `00_admin/decision_log.md` (`D-156`, `D-157`, `D-158`, `D-161`).
		2. `00_admin/change_log.md` (`C-444`, `C-445`, `C-446`, `C-449`).
		3. `07_implementation/src/transparency/main.py`, `07_implementation/src/transparency/payload_builder.py`, `07_implementation/src/observability/main.py`, `07_implementation/src/quality/sanity_checks.py`.

- UNDO-I (2026-04-17): BL-005 threshold-attribution and what-if diagnostics.
	- resolution: Closed. BL-005 diagnostics now emit threshold-attribution and bounded what-if fields, and BL-014 enforces policy-backed threshold-diagnostics gating with config-first policy resolution (`warn` default / `strict` fail escalation).
	- evidence:
		1. `00_admin/decision_log.md` (`D-153`, `D-160`, `D-161`).
		2. `00_admin/change_log.md` (`C-441`, `C-448`, `C-449`).
		3. `07_implementation/src/retrieval/stage.py`, `07_implementation/src/quality/sanity_checks.py`, `07_implementation/tests/test_quality_sanity_checks.py`.

- UI-014 (2026-04-12): Architecture rebuild RQ/objective derivation blocker.
	- resolution: Closed. RQ and objective set were derived from confirmed Chapter 2 tensions, scope and artefact definition were locked for rebuild posture, and governance/foundation mirrors were synchronized.
	- evidence:
		1. `00_admin/decision_log.md` (`D-053`, `D-054`).
		2. `00_admin/change_log.md` (`C-283`).
		3. `00_admin/thesis_state.md`, `02_foundation/current_title_and_rq.md`, `02_foundation/objectives.md`, `02_foundation/contribution_statement.md`, `02_foundation/assumptions.md`, `02_foundation/limitations.md`, `00_admin/timeline.md`.

- UI-003 (2026-03-19): Thesis-wide citation verification and literature leverage synthesis closure.
	- resolution: Closed at control-record level. Claim-citation matrix expansion for Chapters 3 to 5 is complete, verdict labels were recorded (`supported`, `partially_supported`, `weak_support`, `mismatch`), and chapter-targeted hardening notes were documented for remaining weak/mismatch text locations.
	- evidence:
		1. `09_quality_control/ui003_claim_verdicts_ch3_ch5.md` (claim-level verdict matrix).
		2. `09_quality_control/ui003_chapter_hardening_notes_ch3_ch5.md` (chapter-targeted rewrite/citation-swap notes).
		3. Cross-reference consistency maintained with `09_quality_control/claim_evidence_map.md` and `09_quality_control/citation_checks.md`.

- UI-013 (2026-03-25): Pipeline optimization and evidence-hygiene package closure on the active BL baseline.
	- resolution: Closed. The controlled tuning sweep, BL-010/BL-011 path-semantics normalization, BL-006 transparency-contract correction, and refreshed v1b acceptance evidence now all align on one corrected active baseline.
	- evidence:
		1. Canonical implementation reporting baseline is now `07_implementation/implementation_notes/bl000_run_config/configs/profiles/run_config_ui013_tuning_v1f.json` per D-033 (superseding the baseline-selection aspect of D-032). `run_config_ui013_tuning_v2a_retrieval_tight.json` remains experimental.
		2. Controlled sweep across `v1`, `v1a`, `v1b`, `v1c` remains logged in `_scratch/ui013_tuning_sweep_results.json`.
		3. BL-010 / BL-011 path-semantics normalization and freshness evidence remains passing from 2026-03-25.
		4. BL-006 transparency-contract correction completed on 2026-03-26 (`C-178`, `EXP-046`).
		5. Refreshed v1b acceptance pass on corrected semantics succeeded (`BL013-ENTRYPOINT-20260326-180047-134553`, `BL014-SANITY-20260326-180057-357905`).
		6. Acceptance metrics now satisfy all UI-013 thresholds on the corrected baseline: `bl003_match_rate=0.1595`, `bl005_kept_candidates=54402`, `bl006_numeric_minus_semantic=-0.068775`, `bl008_top_label_dominance_share=0.3`.
		7. Refreshed BL-008 top-contributor distribution is `{Lead genre match:3, Tag overlap:3, Tempo (BPM):3, Genre overlap:1}` in `_scratch/ui013_v1b_bl008_focus_result.json`.

- UI-010 (2026-03-25): Control-evaluation artifacts risk drift from current live data baselines.
	- resolution: Closed. BL-010 and BL-011 evidence was regenerated after the lead-genre fix, freshness expectations were recorded in test notes, and a dedicated quality check now fails when BL-010/BL-011 evidence no longer matches the current active baseline contracts.
	- evidence:
		1. `07_implementation/implementation_notes/bl010_reproducibility/run_bl010_reproducibility_check.py` defaults to active pipeline outputs unless legacy mode is explicitly enabled.
		2. `07_implementation/implementation_notes/bl011_controllability/run_bl011_controllability_check.py` defaults to active pipeline outputs unless legacy mode is explicitly enabled.
		3. BL-010 reproducibility refresh passed (`BL010-REPRO-20260325-020749`, `deterministic_match=true`, `fixed_input_source=active_pipeline_outputs`).
		4. BL-011 controllability refresh passed (`BL011-CTRL-20260325-020828`, `all_scenarios_repeat_consistent=true`, `all_variant_shifts_observable=true`, `status=pass`).
		5. `07_implementation/implementation_notes/bl014_quality/check_bl010_bl011_freshness.py` passed on 2026-03-25 (`BL-FRESHNESS-20260325-021237`, `9/9` checks).
		6. `07_implementation/implementation_notes/bl014_quality/run_active_freshness_suite.py` passed on 2026-03-25 (`BL-FRESHNESS-SUITE-20260325-021510`, `6/6` checks), consolidating active freshness checks for BL-013, BL-014, and BL-010/BL-011.

- UI-012 (2026-03-25): Lead-genre semantic contract was inconsistent across BL-004, BL-005, and BL-006.
	- resolution: Closed. BL-004, BL-005, and BL-006 now use one canonical lead-genre rule: prefer the first `genres` label and only fall back to the first `tags` label when no genre is present.
	- evidence:
		1. `07_implementation/implementation_notes/bl004_profile/build_bl004_preference_profile.py` now resolves lead genre with the canonical genre-first rule.
		2. `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py` now uses the same genre-first rule for `lead_genre_match`.
		3. `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py` now uses the same genre-first rule for `lead_genre_similarity`.
		4. BL-013 canonical rerun passed (`BL013-ENTRYPOINT-20260325-020526-881730`).
		5. BL-014 sanity suite passed (`BL014-SANITY-20260325-020553-870468`, `21/21` checks).

- UI-011 (2026-03-25): Tier-1 pipeline remediation package closure tracking item.
	- resolution: Closed. All Tier-1 remediation items (CRI-004, CRI-002, HIGH-003, HIGH-004, CRI-003) are implemented with integrated validation evidence complete.
	- evidence:
		1. BL-013 integrated canonical run passed (`BL013-ENTRYPOINT-20260325-014411-311800`).
		2. BL-014 sanity suite passed (`BL014-SANITY-20260325-014516-905552`, `21/21` checks).
		3. Consolidated execution record logged in `00_admin/tier1_hardening_execution_log_2026-03-25.md`.

- UI-009 (2026-03-25): BL-013 stale-seed false-pass risk under run-config execution.
	- resolution: Implemented a BL-003 freshness guard in BL-013. When `--run-config` is supplied without `--refresh-seed`, BL-013 now fails fast on seed-contract mismatch and instructs the operator to refresh BL-003.
	- evidence:
		1. `07_implementation/implementation_notes/bl013_entrypoint/run_bl013_pipeline_entrypoint.py` includes `BL-003-FRESHNESS-GUARD` preflight validation.
		2. `07_implementation/implementation_notes/bl003_alignment/build_bl003_ds001_spotify_seed_table.py` now emits `inputs.seed_contract` + contract hash for comparison.
		3. Validation run on 2026-03-25: fail without refresh, pass with `--refresh-seed`.

- UI-008 (2026-03-22): Music4All governance-closure tracking item.
	- resolution: Closed by current-state confirmation that DS-001 is already received and operational for active runs; unresolved-issue status removed per user directive.
	- evidence: user confirmation in chat on 2026-03-25; `06_data_and_sources/dataset_registry.md` DS-001 delivery state; `00_admin/thesis_state.md` active DS-001 posture.

- UI-002 (2026-03-15): Chapter 2 weak-support remediation objective.
	- resolution: Day 2 and Day 3 hardening passes completed; final micro-pass achieved `TOTAL_KEYS_WITH_WEAK=0` for current Chapter 2 audit workflow.
	- key_metrics:
		- baseline: 22 papers with weak claims (24 weak claims)
		- final: 0 papers with weak claims
		- reduction: 100% of baseline weak-claim papers removed in current audited state
	- evidence: `09_quality_control/chapter2_verbatim_audit.md`; `09_quality_control/summarize_ch2_verbatim_audit.py`; `00_admin/timeline.md` (Day 3 closure note).

- UI-007 (2026-03-21): Spotify API ingestion was temporarily blocked by provider-side long cooldown (`HTTP 429`) on `/me`.
	- resolution: Subsequent authenticated export completed successfully (run_id `SPOTIFY-EXPORT-20260321-192533-881299`), generating full BL-002 artifacts and enabling real-data BL-020 execution.
	- evidence: `07_implementation/implementation_notes/bl001_bl002_ingestion/outputs/spotify_api_export/spotify_export_run_summary.json`; `07_implementation/experiment_log.md` (`EXP-022`); `00_admin/change_log.md` (`C-071`).

## Resolved (Historical)

- UI-006 (2026-03-21): Governance mismatch after DS-002 activation where `thesis_state.md` still stated Music4All/Music4All-Onion as current primary scope.
	- resolution: Synchronized `00_admin/thesis_state.md` to DS-002 active wording and aligned objective/assumption/limitation phrasing.
	- evidence: `00_admin/thesis_state.md` (2026-03-21 update), `00_admin/change_log.md` (`C-042`).

- UI-005 (2026-03-19): Base Music4All was unusable in the local environment; Onion-only workaround was the active interim path.
	- resolution: Superseded by planning decision `D-015`, which activated DS-002 as the BL-019 strategy.
	- evidence: `00_admin/decision_log.md` (`D-015`); `06_data_and_sources/dataset_registry.md` DS-002 status update.

- UI-004 (2026-03-19): Candidate corpus change review between Music4All-Onion and `MSD subset + Last.fm Tag Dataset + MusicBrainz mapping`.
	- resolution: BL-018 feasibility review completed. Result: do not switch corpus; retain MSD-based option as fallback only.
	- evidence: `07_implementation/implementation_notes/bl000_data_layer/candidate_corpus_feasibility_review_2026-03-19.md`; `00_admin/decision_log.md` (`D-008`).

- UI-001 (2026-03-15): Parser mismatch between author-year Chapter 2 style and key-based claim extractor.
	- resolution: Extended `09_quality_control/run_ch2_verbatim_audit.py` to map author-year citations to source-index keys and regenerate non-zero claim extraction.
        - evidence: `09_quality_control/run_ch2_verbatim_audit.py`; `09_quality_control/chapter2_verbatim_audit.md`; `00_admin/change_log.md` (`C-009`).

**Active-set sync note (2026-04-17 literature integration wave):** Three design-verification items flagged (UNDO-A, UNDO-B, UNDO-C) after Chapter 3 literature-gap analysis and targeted prose-depth integration pass (C-421). All items are Medium priority, non-blocking, and deferred to post-Chapter-3-finalization investigation phase. Prose additions to Chapter 3 sections 3.5, 3.7, 3.9, 3.11 deepen design reasoning with specific literature caveats (Flexer & Grill, Herlocker, Knijnenburg, Afroogh). No chapter restructuring; section numbering unchanged.

**Active-set sync note (2026-04-17 literature-to-implementation upgrade triage):** Three additional non-blocking design-verification items were added (`UNDO-D`, `UNDO-E`, `UNDO-F`) after checking normalized literature notes against active implementation surfaces (`BL-006`, `BL-008`, `BL-009`, `BL-011`, `BL-014`). The unresolved set now tracks six medium-priority implementation-upgrade verifications in total.

**Active-set sync note (2026-04-17 design-chapter implementation triage):** Three additional design-to-implementation upgrade items were added (`UNDO-G`, `UNDO-H`, `UNDO-I`) after mapping Chapter 3 design authority and design-control specs to active runtime behavior (`chapter3_information_sheet`, `CONTROL_TESTING_PROTOCOL`, `CONTROL_SURFACE_REGISTRY`, `transparency_design*`).

**Active-set sync note (2026-04-17 closure formalization):** `UNDO-G`, `UNDO-H`, and `UNDO-I` are now closed following implementation completion and full validation (`pytest 563/563`, wrapper validate-only pass, full contract pass). Active unresolved design-verification set is now six items (`UNDO-A` through `UNDO-F`).
