# Unresolved Issues

Last updated: 2026-04-19 UTC (MFT-A1 through MFT-A6 are now implemented under UNDO-R: BL-006 now emits additive raw-vs-final score surfaces and explicit no-op influence diagnostics, influence accounting is split into new-injected vs relabelled counters, BL-013 run effective artifacts persist environment-override provenance in `env_overrides`, wrapper pass-through parity is complete, and strict validation-profile semantics now coerce all stage handshake policies to strict. D-tooling tranche is now complete: D1-D9 implemented and D10 optional evidence tooling is now wired (interrogate advisory script/task/report surface), while remaining non-mandatory for baseline gates. B/E tranche (B1/B2/B6/E1/E2/E3) is now implemented: lockfile, Python version pin/guard, runtime-environment metadata in effective-config artifact, GitHub Actions CI workflow, bounded Python-version matrix coverage policy, and bounded cross-platform (Linux plus Windows) CI execution. C-test tranche now includes C4 property-based invariant coverage, C5 schema-key parity coverage, and C6 explicit boundary-case matrix coverage. F-doc tranche is complete (F1-F5), G-methodology tranche is complete (G1/G3), and H-housekeeping tranche is now complete (H1-H5): repository license posture aligned; `.gitignore` and generated-artifact hygiene re-verified; `pyproject.toml` metadata/tool clarity expanded; installability posture documented as script-first; input-asset redistribution/license audit completed. Remaining blockers are external submission/package confirmations tracked in `09_quality_control/submission_readiness_status.md`.)

## Active

### UNDO-R: Mentor feedback remediation backlog (A-H comprehensive TODO set)

**Status**: Active (2026-04-19)

**Trigger**: Mentor feedback review surfaced a mixed set of real implementation defects, reproducibility-hardening gaps, CI/tooling omissions, and submission-methodology packaging gaps. User requested a comprehensive actionable TODO set covering every feedback item.

**Description**: Track all mentor-feedback items as explicit action-checklist tasks with completion evidence. This backlog is intentionally comprehensive and includes both code-facing and packaging-facing work.

**Comprehensive TODO checklist**

**A) Defects and contract correctness**
- [x] `MFT-A1`: Add `raw_final_score` alongside `final_score` in BL-006 scored output, keep BL-008/BL-009 explanation surfaces coherent against both fields, and add regression tests for score-column contract.
- [x] `MFT-A2`: Split influence injection accounting into `new_injected_count` vs `relabelled_count` (replace overloaded `injected_count`) and update all dependent summaries/tests.
- [x] `MFT-A3`: Make `validation_profile=strict` enforce strict policy coercion across stage handshake policies (or remove/rename misleading strict mode semantics).
- [x] `MFT-A4`: Persist environment-override provenance in effective config artifact (`env_overrides` with source and value-normalization notes).
- [x] `MFT-A5`: Extend wrapper pass-through controls to include no-refresh-seed and explicit stages selection parity with orchestration CLI.
- [x] `MFT-A6`: Emit explicit warning/diagnostic when BL-006 influence apply is enabled but BL-003 influence is disabled (silent no-op prevention).

**B) Determinism and reproducibility hardening**
- [x] `MFT-B1`: Add a lockfile or equivalent transitive dependency freeze mechanism for reproducible installs.
- [x] `MFT-B2`: Add explicit Python version pin + fail-fast environment guard for unsupported interpreter versions.
- [x] `MFT-B3`: Complete deterministic iteration audit for dict/set-sensitive paths and record outcome artifact. [Done: `07_implementation/DETERMINISTIC_ITERATION_AUDIT.md` — C-544]
- [x] `MFT-B4`: Add explicit seed/randomness policy note artifact stating no stochastic runtime paths (or seed policy if any are introduced). [Done: `07_implementation/DETERMINISM_RANDOMNESS_POLICY.md` — C-544]
- [x] `MFT-B5`: Add centralized hash-input chain summary in BL-013 (input artifacts and config authority chain). [Done: `hash_input_chain` block in `src/orchestration/summary_builder.py` + tests — C-545]
- [x] `MFT-B6`: Add platform/runtime metadata capture (`sys.version`, locale/encoding, timezone, OS) to effective run artifact.
- [x] `MFT-B7`: Formalize deterministic verification replay (3-replay evidence) as repeatable contract path in docs and CI/task flow. [Done: wrapper pass-through + CI validate step + task + README command path — C-546]

**C) Test-depth hardening**
- [x] `MFT-C1`: Add coverage measurement (`pytest-cov`) and define minimum threshold policy for active runtime modules.
- [x] `MFT-C2`: Add golden-artifact [Done: test_golden_artifacts.py — C-543] reproducibility test(s) for byte/hash-stable expected outputs on fixed fixture inputs.
- [x] `MFT-C3`: Close residual unit-test blind spots for newly identified contract-sensitive paths (A1-A6 outcomes).
- [x] `MFT-C4`: Add bounded property-based tests (Hypothesis) for key invariants in parsing/coercion and stage contract validation.
- [x] `MFT-C5`: Add schema-key contract parity test (declared config keys vs consumed runtime keys, including deprecations).
- [x] `MFT-C6`: Add explicit boundary-case matrix coverage for zero/empty/single-item and threshold-edge conditions.

**D) Tooling and quality automation**
- [x] `MFT-D1`: Keep Ruff check/fix workflow as canonical lint path and close with docs/task parity verification (workflow active; README/task parity synchronized).
- [x] `MFT-D2`: Define and document strict static-analysis posture (pyright profile, staged strict rollout, and gate behavior).
- [x] `MFT-D3`: Wire pytest plus coverage reporting into one repeatable quality command/task surface with an explicit threshold policy.
- [x] `MFT-D4`: Add Hypothesis dependency/tooling only after scoped property tests are introduced.
- [x] `MFT-D5`: Add pre-commit hooks (lint/type/test lightweight gates) after D2/D3 baseline stabilization.
- [x] `MFT-D6`: Add dependency vulnerability audit step (`pip-audit` or equivalent) in advisory-first mode with report artifacts.
- [x] `MFT-D7`: Add security static analysis step (`bandit` advisory-first) with report artifacts for submission hardening evidence (Python 3.14 compatibility fallback to Ruff `S` rules when Bandit AST parsing fails).
- [x] `MFT-D8`: Keep dead-code hygiene (`vulture`) active and close with documented execution cadence/threshold policy (workflow active and posture documented).
- [x] `MFT-D9`: Keep complexity audit (`radon`) active and record explicit decision on `xenon` advisory-vs-strict posture (advisory-only for current remediation tranche).
- [x] `MFT-D10`: Decide on docstring-coverage tooling (`interrogate`) as optional viva/submission evidence add-on (decision: keep optional, not baseline-gated; advisory tooling surface now active via `scripts/docstring_coverage_src.ps1` and `07: Docstring Coverage src (Advisory)`).

**E) CI and matrix execution**
- [x] `MFT-E1`: Add CI workflow for end-to-end contract checks (lint, tests, typecheck, validate-only path).
- [x] `MFT-E2`: Add Python-version matrix coverage policy in CI (bounded to supported interpreter set).
- [x] `MFT-E3`: Add cross-platform CI execution (Windows plus Linux) for reproducibility posture.

**F) Documentation and demo readiness**
- [x] `MFT-F1`: Resolve README architecture-reference drift (missing architecture reference path) and ensure implementation-doc discoverability.
- [x] `MFT-F2`: Add unified run-config reference with control descriptions, ranges, defaults, and stage-effect mapping.
- [x] `MFT-F3`: Add dedicated reproducibility playbook doc (operator steps + expected artifacts + interpretation boundaries).
- [x] `MFT-F4`: Curate and label demo-ready alternate profiles (including influence-policy variants) with explicit usage guidance.
- [x] `MFT-F5`: Expand troubleshooting section with BL-013/BL-014 failure triage and common environment issues.
- [x] `MFT-F6`: Add concise defense/viva run script document (demo sequence + expected outputs + fallback plan). [Done: VIVA_RUN_SCRIPT.md — C-543]

**G) Chapter-methodology evidence strengthening**
- [x] `MFT-G1`: Add explicit ablation evidence table(s) aligned to implemented control surfaces.
- [x] `MFT-G2`: Add baseline comparator evidence (bounded simple baselines) or document justified non-inclusion with stronger limitations framing. [Done: chapter6.md 6.4 item 6 expanded — C-543]
- [x] `MFT-G3`: Add explicit sensitivity-analysis write-through using existing diagnostics in chapter-facing evidence tables.
- [x] `MFT-G4`: Add explicit controllability-demonstration evidence for influence policy-mode transitions (for example `reserved_slots` variants). [Done: chapter5.md Table 5.3 new row — C-543]

**H) Submission housekeeping and governance artifacts**
- [x] `MFT-H1`: Add repository license file and align package/readme licensing statements.
- [x] `MFT-H2`: Re-verify `.gitignore` and generated-artifact hygiene against current runtime and mentor-bundle workflows.
- [x] `MFT-H3`: Expand `pyproject.toml` project metadata/tool sections as needed for reproducibility/tooling clarity.
- [x] `MFT-H4`: Decide and document installable-package posture (`pip install -e` compatible or explicitly script-first).
- [x] `MFT-H5`: Complete input-asset redistribution/license audit for submission package legality.

**Execution priority order (mentor aligned)**
1. ~~`MFT-B1`, `MFT-B2`, `MFT-B6`, `MFT-E1`~~ ✅ Implemented (C-542 / D-251)
2. ~~`MFT-C2`, `MFT-F6`, `MFT-G2`, `MFT-G4`~~ ✅ Implemented (C-543 / D-236)
3. UNDO-R implementation remediation checklist complete; remaining blockers are external submission/package confirmations.

**Deferred (post-baseline or conditional)**
- none inside UNDO-R implementation checklist; optional future tooling expansion remains discretionary.

**Blocking**: Medium. Core pipeline is currently green, but this backlog represents the active remediation path for mentor-feedback closure and defense-readiness hardening.

Submission-preparation blockers remain tracked in:
- `09_quality_control/submission_readiness_status.md` for packaging artifacts and external submission confirmations.
- `01_requirements/ambiguity_flags.md` for current-year policy or staff-confirmation uncertainties.

---

## Deferred Non-Blocking Improvements (Added 2026-04-18 doc-sync wave)

### UNDO-P: Counterfactual transparency depth beyond bounded diagnostics

**Status**: Resolved (2026-04-18, C-490 / D-199)

**Trigger**: Transparency documentation now reflects that BL-005/BL-009 bounded directional diagnostics exist, but full rerun-level counterfactual analysis is still out of current implementation scope.

**Description**: Investigate whether a bounded, reproducible scenario-run layer can be added for selected control families (thresholds, language filter, assembly limits) so users can inspect explicit before/after outcome deltas under controlled what-if runs, without changing baseline deterministic contracts.

**Resolution**: Extended `_build_bounded_what_if_estimates` in `retrieval/stage.py` to emit a `per_control_family_scenarios` section. Includes: (1) `thresholds` (existing ±10% perturbation repackaged with explicit labeling), (2) `language_filter` (bounded row-level what-if: how many language-rejected candidates would have passed current threshold rules if the gate were disabled), (3) `assembly_limits` (out-of-BL-005-scope note with UNDO-Q pointer). All existing output keys preserved; 621/621 tests pass.

**Implementation contact**: `07_implementation/src/retrieval/stage.py`, `07_implementation/tests/test_retrieval_stage.py`

**Blocking**: Resolved; was non-blocking.

---

### UNDO-Q: Cross-stage influence-effect attribution narrative hardening

**Status**: Resolved (2026-04-18, C-491 / D-200)

**Trigger**: Influence diagnostics and policy controls are now present, but cross-stage narrative attribution (profile shift -> retrieval shaping -> assembly outcome) remains partially implicit for chapter-facing and user-facing interpretation.

**Description**: Add a bounded cross-stage attribution summary contract that links influence-related inputs and diagnostics across BL-004, BL-005/BL-006, BL-007, and BL-009 into one concise explanation surface while preserving current additive compatibility.

**Resolution**: Added `build_cross_stage_influence_attribution_summary()` in `observability/main.py` and wired it into BL-009 run logs as `cross_stage_influence_attribution_summary` (`cross-stage-influence-attribution-v1`). The summary now emits stage-linked fields for BL-004 interaction attribution, BL-005 retrieval language-filter and threshold-direction signals, BL-006 scoring context, BL-007 influence assembly outcomes, and BL-009 control-causality coverage. Added unit coverage in `tests/test_observability_signal_mode_summary.py`; full suite passes (622/622).

**Implementation contact**: `07_implementation/src/observability/main.py`, `07_implementation/tests/test_observability_signal_mode_summary.py`

**Blocking**: Resolved; was non-blocking interpretability-depth enhancement.

---

## Resolved (2026-04-18 hardening wave)

### UNDO-J: Candidate-shaping causal-strength quantification depth — Chapter 3 Section 3.8 reachable-search-space claim

**Status**: Resolved (2026-04-18) — implementation hardening completed and synchronized

**Trigger**: Chapter 3 Section 3.8 requires diagnostics that show not only retained/excluded counts but also "how strongly the current profile settings determined the reachable search space." Current BL-005/BL-009 evidence is strong on counts/categories but weaker on explicit dominance attribution and bounded directional impact summaries.

**Description**: Verify and, if needed, extend BL-005/BL-009 diagnostics so threshold and profile-control contribution is quantifiably attributable (for example: ranked rejection-driver contribution shares and bounded directionality summaries under controlled threshold relaxation/tightening). Treat this as fidelity-depth hardening of an existing surface, not a claim that current diagnostics are absent.

**Resolution**: BL-005 now emits `candidate_shaping_fidelity.rejection_driver_contribution` (ranked rejection-driver shares and dominant driver summary) and `candidate_shaping_fidelity.threshold_effects.directional_impact_summary`; BL-009 propagates both in `retrieval_fidelity_summary`; BL-014 candidate-shaping contract checks require these depth fields; and post-UNDO chapter-readiness/full-contract synchronization completed on the 2026-04-18 validated baseline.

**Implementation contact**: `07_implementation/src/retrieval/stage.py` (BL-005), `07_implementation/src/observability/main.py` (BL-009), `07_implementation/src/quality/sanity_checks.py` (BL-014 contract expectations)

**Blocking**: No; non-blocking quality-depth follow-up.

---

### UNDO-K: Playlist trade-off metric explicitness — Chapter 3 Section 3.10 multi-objective assembly claim

**Status**: Resolved (2026-04-18) — implementation hardening completed and synchronized

**Trigger**: Chapter 3 Section 3.10 frames playlist assembly as explicit coherence/diversity/novelty/ordering trade-offs. Current BL-007 reporting includes strong trace and rule-hit visibility, but cross-run quantitative trade-off summary metrics remain limited.

**Description**: Add or formalize aggregate trade-off metrics in BL-007/BL-009 evidence surfaces (for example: diversity distribution summaries, novelty-distance summaries, ordering-pressure summaries) so Chapter 3 multi-objective claims can be defended with direct quantitative run evidence.

**Resolution**: BL-007 now emits `tradeoff_metrics_summary` containing `diversity_distribution_summary`, `novelty_distance_summary`, and `ordering_pressure_summary`; BL-009 emits run-level `playlist_tradeoff_summary`; and chapter-readiness/full-contract synchronization completed on the 2026-04-18 validated baseline.

**Implementation contact**: `07_implementation/src/playlist/rules.py`, `07_implementation/src/playlist/stage.py`, `07_implementation/src/observability/main.py`

**Blocking**: No; non-blocking quality-depth follow-up.

---

### UNDO-L: Multi-parameter interaction coverage — Chapter 3 Section 3.12 controlled-variation boundary

**Status**: Resolved (2026-04-18) — implementation hardening completed and synchronized

**Trigger**: Controlled-variation evidence currently emphasizes one-factor-at-a-time behavior, which aligns to Chapter 3 protocol intent but leaves interaction effects underexplored.

**Description**: Add a bounded interaction-check layer (small fixed interaction matrix) for high-impact controls so controllability claims can distinguish single-factor effects from interaction-driven behavior without expanding beyond thesis scope.

**Resolution**: BL-011 now includes a bounded interaction matrix via `EP-CTRL-005` with two fixed high-impact interaction scenarios (`no_influence_plus_stricter_thresholds`, `valence_up_plus_stricter_thresholds`); scenario and report surfaces emit explicit interaction metadata and `interaction_coverage_summary`; and chapter-readiness/full-contract synchronization completed on the 2026-04-18 validated baseline.

**Implementation contact**: `07_implementation/src/controllability/analysis.py` (BL-011), `07_implementation/src/reproducibility/main.py` (BL-010 optional matrix trace), `07_implementation/src/quality/sanity_checks.py` (BL-014 advisory/gate posture)

**Blocking**: No; non-blocking evaluation-depth follow-up.

---

### UNDO-M: Feature-availability and sparsity diagnostics visibility — Chapter 3 Section 3.7 interpretable-feature boundary

**Status**: Resolved (2026-04-18) — implementation hardening completed and synchronized

**Trigger**: Chapter 3 Section 3.7 explicitly frames interpretable features and bounded sufficiency. Current reporting does not consistently foreground feature-availability/sparsity rates in chapter-facing evidence.

**Description**: Surface explicit feature-availability and missingness diagnostics (profile-side and candidate-side) in BL-004/BL-006/BL-009 summaries so feature-space boundaries are measurable in run evidence rather than only discussed narratively.

**Resolution**: BL-004 now emits additive `feature_availability_summary` with numeric coverage/sparsity and missingness rates; BL-006 emits candidate-side `feature_availability_summary`; BL-009 emits run-level fused `feature_availability_summary` with boundary indicators; and chapter-readiness/full-contract synchronization completed on the 2026-04-18 validated baseline.

**Implementation contact**: `07_implementation/src/profile/stage.py` (BL-004), `07_implementation/src/scoring/stage.py` and `07_implementation/src/scoring/diagnostics.py` (BL-006), `07_implementation/src/observability/main.py` (BL-009)

**Blocking**: No; non-blocking diagnostic-depth follow-up.

---

### UNDO-N: Control-surface discoverability and range transparency — Chapter 3 Section 3.12 configuration-as-method instrument claim

**Status**: Resolved (2026-04-18) — implementation hardening completed and synchronized

**Resolution**: `run_config/control_registry.py` now provides `CONTROL_REGISTRY` (24 entries, `control-registry-v1` schema) covering BL-004 through BL-011 with name/section/stage/type/valid_range/default/effect_surface metadata, `build_control_registry_snapshot()` for structured snapshot emission, and BL-009 now emits `control_registry_snapshot` as an additive top-level run log key. Chapter-readiness/full-contract synchronization completed on the 2026-04-18 validated baseline.

**Trigger**: Chapter 3 Section 3.12 treats configuration as a methodological instrument. Controls are implemented, but discoverability of available controls/ranges/policies remains fragmented across run-config schema, defaults, and stage docs.

**Description**: Add one authoritative machine-readable control registry artifact (emitted or generated in active runtime path) that maps control name -> stage -> valid range -> default -> expected effect surface. Preserve existing controls; improve discoverability and audit ergonomics.

**Implementation contact**: `07_implementation/src/run_config/run_config_utils.py`, `07_implementation/src/shared_utils/constants.py`, `07_implementation/src/observability/main.py` (optional registry snapshot propagation), `05_design/CONTROL_SURFACE_REGISTRY.md` (design mirror)

**Blocking**: No; non-blocking usability/evidence follow-up.

---

### UNDO-O: Reproducibility interpretation boundary clarity — Chapter 3 Section 3.12 replay claim framing

**Status**: Resolved (2026-04-18) — C-469 / D-181

**Resolution**: Added `build_interpretation_boundaries()` to `reproducibility/main.py`, emitting `interpretation_boundaries` (`reproducibility-interpretation-v1` schema with `verdict_basis`, `consistency_domain.covered`, `consistency_domain.not_covered`, `non_claims`) into the BL-010 report. Added `build_reproducibility_interpretation()` to `observability/main.py`, emitting `reproducibility_interpretation` inside `validity_boundaries` in the BL-009 run log. Hardened `chapter5.md` Section 5.8 item 1 and `chapter6.md` Section 6.4 item 4 to explicitly name artifact-level framing and environmental invariance non-claims. 5 new regression tests added; 609/609 tests pass; pyright 0 errors.

**Original trigger**: BL-010 and BL-009 provide strong deterministic replay evidence, but chapter-facing interpretation can over-compress artifact-level reproducibility into broader behavioral invariance if not explicitly bounded.

---

## Resolved (Design Verification)

### UNDO-B: Sequential coherence in playlist assembly — Schedl et al. (2018) music-specific dynamics caveat

**Status**: Resolved (2026-04-17) — C-458 / D-170

**Resolution**: Implemented `transition_feature_distance`, `transition_smoothness_score`, and `build_transition_diagnostics` in `playlist/rules.py`. Always-on `transition_diagnostics` block emitted to `bl007_assembly_report.json` for every run. Opt-in `transition_smoothness_weight` control (default 0.0) wired through the full controls stack (DEFAULT_ASSEMBLY_CONTROLS → PlaylistControls → PlaylistContext → assemble_bucketed). BL-014 advisory fires when mean smoothness < 0.5. BL-009 observability log surfaces transition_diagnostics. 11 new tests added. 574/574 tests pass; pyright 0 errors.

**Original trigger**: Chapter 3 Section 3.10 describes multi-objective playlist assembly but did not ground coherence in sequential/relational listening (Schedl et al. 2018).

---

### UNDO-C: Candidate-shaping diagnostics fidelity — Zamani & Ferraro (2018/2019) visibility caveat

**Status**: Resolved (2026-04-17) — C-461 / D-173

**Trigger**: Chapter 3 Section 3.8 emphasizes candidate shaping must "show how many items were retained, why other items were filtered out, and how strongly the current profile settings determined the reachable search space." Zamani/Ferraro finding: candidate generation is most consequential but least visible. Design question: do BL-005 diagnostics expose threshold effects, exclusion categories, and pool-size trends with sufficient detail?

**Description**: Chapter 3 Section 3.8 states candidate shaping must show filtering logic completely. Implementation is now complete: BL-005 diagnostics emit additive `candidate_shaping_fidelity` with pool-progression trend surfaces, exclusion categories, control-effect observability shares, and threshold-effects packaging; BL-009 now propagates these diagnostics and emits run-level `retrieval_fidelity_summary`; BL-014 now enforces policy-backed contract coverage (`gate_bl005_candidate_shaping_diagnostics_contract`) with warn default and strict fail escalation.

**Resolution**: Added BL-005 UNDO-C diagnostics in `retrieval/stage.py` (`candidate_shaping_fidelity` with `pool_progression`, `exclusion_categories`, `control_effect_observability`, and `threshold_effects`), propagated additive surfaces in BL-009 (`observability/main.py`) including `retrieval_fidelity_summary`, and hardened BL-014 with advisory plus policy-backed gate behavior (`advisory_bl005_candidate_shaping_diagnostics_contract`, `gate_bl005_candidate_shaping_diagnostics_contract`) with config-first policy resolution. Validation passed (`pytest 588/588`, `pyright 0`, full contract pass: `BL013-ENTRYPOINT-20260417-180608-473274`, `BL014-SANITY-20260417-180636-403769`, `36/36`).

**Implementation contact**: `07_implementation/src/retrieval/stage.py` (BL-005); `07_implementation/src/observability/main.py` (BL-009); `07_implementation/src/quality/sanity_checks.py` (BL-014)

**Blocking**: No; closure formalized on implementation evidence.

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

**Active-set sync note (2026-04-17 literature integration wave):** Two design-verification items flagged (UNDO-B, UNDO-C) after Chapter 3 literature-gap analysis and targeted prose-depth integration pass (C-421). All items are Medium priority, non-blocking, and deferred to post-Chapter-3-finalization investigation phase. Prose additions to Chapter 3 sections 3.5, 3.7, 3.9, 3.11 deepen design reasoning with specific literature caveats (Flexer & Grill, Herlocker, Knijnenburg, Afroogh). No chapter restructuring; section numbering unchanged.

**Active-set sync note (2026-04-17 literature-to-implementation upgrade triage):** Three additional non-blocking design-verification items were added (`UNDO-D`, `UNDO-E`, `UNDO-F`) after checking normalized literature notes against active implementation surfaces (`BL-006`, `BL-008`, `BL-009`, `BL-011`, `BL-014`). The unresolved set now tracks five medium-priority implementation-upgrade verifications in total.

**Active-set sync note (2026-04-17 design-chapter implementation triage):** Three additional design-to-implementation upgrade items were added (`UNDO-G`, `UNDO-H`, `UNDO-I`) after mapping Chapter 3 design authority and design-control specs to active runtime behavior (`chapter3_information_sheet`, `CONTROL_TESTING_PROTOCOL`, `CONTROL_SURFACE_REGISTRY`, `transparency_design*`).

**Active-set sync note (2026-04-17 closure formalization):** `UNDO-G`, `UNDO-H`, and `UNDO-I` are now closed following implementation completion and full validation (`pytest 563/563`, wrapper validate-only pass, full contract pass). Active unresolved design-verification set at that checkpoint was five items (`UNDO-B` through `UNDO-F`).

**Active-set sync note (2026-04-17 UNDO-C closure):** `UNDO-C` is now closed after BL-005 candidate-shaping diagnostics fidelity implementation and BL-014 policy-backed contract hardening.

**Active-set sync note (2026-04-17 UNDO-B/UNDO-D closure):** `UNDO-B` and `UNDO-D` are now closed on implementation and validation evidence (`C-458`/`D-170`, `C-460`/`D-172`).
