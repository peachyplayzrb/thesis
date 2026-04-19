# Chapter 5: Evaluation and Results

## 5.1 Chapter Aim and Scope
This chapter evaluates the implementation surfaces defined in Chapter 4 against the objective-to-control-to-evidence contract formalized in Chapter 3. It is not a benchmark-comparison chapter. Instead, it tests whether the rebuilt deterministic pipeline satisfies objective-linked success conditions under bounded scope [@jannach_measuring_2019; @bauer_exploring_2024; @anelli_elliot_2021].

It also operationalizes the design-selection claim stated in Section 3.3.1: the deterministic staged architecture is assessed here as a scope-aligned option for transparency, controllability, and reproducibility evidence quality, rather than as a universal replacement for hybrid, collaborative, or neural alternatives.

The evaluation scope is bounded to six questions:

1. Does the pipeline make cross-source preference uncertainty explicit rather than hiding it in aggregate outputs?
2. Does alignment and candidate shaping expose confidence and exclusion logic?
3. Are scoring and playlist-assembly trade-offs explicitly controllable?
4. Do explanation and observability surfaces remain mechanism-linked?
5. Is reproducibility and controllability evidence executable and repeatable?
6. Are validity boundaries and failure conditions visible enough to support bounded design guidance?

## 5.2 Evaluation Criteria and Success Conditions
Evaluation in the rebuild posture is objective-linked rather than metric-first.

Table 5.1 defines the active Chapter 5 success conditions.

| Objective | Evaluation focus | Minimum success condition |
| --- | --- | --- |
| O1 | Uncertainty-aware profiling | BL-004 emits inspectable uncertainty, coverage, and attribution blocks; tranche-1 gate passes |
| O2 | Confidence-aware alignment and candidate generation | BL-003 and BL-005 expose confidence, exclusion, and candidate-decision evidence; tranche-1 gate passes |
| O3 | Controllable scoring and assembly trade-offs | BL-006 and BL-007 expose explicit control surfaces and measurable effect diagnostics; tranche-1 and BL-011 evidence remain green |
| O4 | Mechanism-linked explanations and observability | BL-008 explanations map to scoring/assembly mechanisms and BL-009 preserves run lineage; tranche-2 gate passes |
| O5 | Reproducibility and controllability evaluation readiness | BL-010 and BL-011 remain executable with pass verdicts and canonical config-pair traceability; tranche-2 gate passes |
| O6 | Bounded design guidance | BL-007 and BL-009 expose failure-boundary and validity-boundary evidence; tranche-2 and tranche-3 gates pass |

## 5.3 Evaluation Procedure
The rebuild evaluation procedure uses a layered acceptance structure.

1. Validate entry-surface completeness for O1 to O3 with the REB-M3 tranche-1 gate.
2. Validate explanation, observability, reproducibility, controllability, and bounded-guidance surfaces for O4 to O6 with the tranche-2 gate.
3. Validate control-causality and validity-boundary hardening with the tranche-3 gate.
4. Confirm end-to-end wrapper execution remains green through validate-only (`BL-013`) and sanity (`BL-014`) checks.
5. Use BL-010 and BL-011 reports as supporting evidence for repeatability and measured control effects.

This layered procedure is stricter than the pre-rebuild framing because it treats evidence completeness itself as part of implementation success rather than post-hoc packaging around runtime outputs [@beel_towards_2016; @ferrari_dacrema_troubling_2021; @zhu_bars_2022].

## 5.4 Objective-To-Evidence Results Matrix
Table 5.2 summarizes the current rebuild-era evidence posture.

| Objective | Primary acceptance evidence | Current result | Interpretation |
| --- | --- | --- | --- |
| O1 | REB-M3 tranche-1 gate `REB-M3-TRANCHE1-GATE-20260412-133635-735086` | `pass (9/9)` | BL-004 now emits uncertainty, coverage, attribution, and policy-effect blocks required for inspectable profiling. |
| O2 | REB-M3 tranche-1 gate `REB-M3-TRANCHE1-GATE-20260412-133635-735086` | `pass (9/9)` | BL-003 and BL-005 expose seed-contract, match-count, and exclusion-path evidence rather than collapsing candidate shaping into hidden preprocessing. |
| O3 | REB-M3 tranche-1 gate plus BL-011 report `BL011-CTRL-20260412-134945` | `pass` | Scoring and assembly controls are explicit, and BL-011 still reports repeat consistency with observable shifts at supported surfaces. |
| O4 | REB-M3 tranche-2 gate `REB-M3-TRANCHE2-GATE-20260412-134111-435035` | `pass (9/9)` | BL-008 primary drivers now map back to breakdown components and BL-009 preserves upstream stage lineage. |
| O5 | REB-M3 tranche-2 gate plus BL-010/BL-011 reports | `pass` | Reproducibility and controllability remain executable and tied to canonical config-pair and run-lineage evidence. |
| O6 | REB-M3 tranche-2 and tranche-3 gates | `pass` | BL-007 failure-boundary reporting and BL-009 validity-boundary reporting are now explicit enough to support bounded conclusions. |

## 5.5 Reproducibility, Controllability, and Observability Evidence
Table 5.3 condenses the most important current execution evidence.

| Check | Active evidence | Result | Notes |
| --- | --- | --- | --- |
| Validate-only orchestration | `BL013-ENTRYPOINT-20260418-035540-208118` | `pass` | Confirms the current active wrapper path completes without contract failure under the latest full-contract authority baseline. |
| Sanity suite | `BL014-SANITY-20260418-035641-651065` | `pass (36/36)` | Confirms active stage contracts remain internally consistent after the rebuild hardening wave. |
| Reproducibility report | `07_implementation/src/reproducibility/outputs/reproducibility_report.json` (`run_id=BL010-REPRO-20260418-040530`) | `pass` | BL-010 records deterministic replay status and retry-boundary reporting under fixed-input replay (`deterministic_match=True`). |
| Controllability report | `07_implementation/src/controllability/outputs/controllability_report.json` (`run_id=BL011-CTRL-20260412-134945`) | `pass` | BL-011 reports repeat-consistent scenario execution and explicit no-op control diagnostics where effect is absent. |
| Observability schema and scope | `07_implementation/src/observability/outputs/bl009_run_observability_log.json` (`run_id=BL009-OBSERVE-20260418-040529-209714`) | `pass` | BL-009 includes execution scope, upstream lineage, canonical config-pair traceability, and explicit validity-boundary reporting. |
| Stage-flow traceability | `BL013-ENTRYPOINT-20260418-040456-884132` | `pass` | BL-013 summary emits `stage_execution` with explicit requested-stage order, executed-stage sequence, non-requested stage execution reporting, and duplicate requested-stage execution counts. |

### 5.5.1 Control-Surface Ablation Evidence Table

Table 5.4 makes the ablation posture explicit by listing bounded control-surface perturbations and their expected evidence surfaces. In this thesis context, "ablation" means controlled profile or scenario variation against a fixed deterministic baseline, with interpretation focused on directionality and observability rather than leaderboard optimization [@jannach_measuring_2019; @bauer_exploring_2024].

| Ablation axis | Baseline setting | Variant setting | Evidence surface | Observed directionality |
| --- | --- | --- | --- | --- |
| Influence policy mode | `competitive` (`run_config_ui013_tuning_v1f.json`) | `reserved_slots` (`run_config_ui013_tuning_v1g_reserved_slots.json`) | BL-007 assembly diagnostics and BL-013 summary (`influence_assembly_summary`) | Influence inclusion behavior shifts from pure competition to reserved-slot injection behavior while remaining contract-valid. |
| Influence policy override posture | `reserved_slots` (no overrides) | `hybrid_override` (`run_config_ui013_tuning_v1h_hybrid_override.json`) | BL-007 diagnostics plus BL-014 contract pass under variant | Constraint-handling flexibility increases (genre/consecutive/threshold overrides allowed), producing an observable assembly-policy shift. |
| Influence signal strength | Mixed `history + influence` with moderate influence weight (`v1f`) | Influence-heavy swing profile (`run_config_ui013_tuning_v1e_hard_swing_influence.json`) | BL-004/BL-006/BL-007 influence-linked diagnostics | Upstream influence attribution and downstream ranking/assembly behavior shift measurably toward influence-led outcomes. |
| Retrieval strictness | Baseline retrieval thresholds (`v1f`) | Tight retrieval profile (`run_config_ui013_tuning_v2a_retrieval_tight.json`) | BL-005 candidate decisions and BL-009 retrieval summary | Candidate pool contracts under stricter retrieval gates, with exclusion pathways remaining explicit in diagnostics. |
| Language and recency gating | No explicit language gate, baseline recency behavior (`v1f`) | Language+recency gate profile (`run_config_ui013_tuning_v2b_language_recency_gate.json`) | BL-005 retrieval diagnostics and BL-009 observability log | Eligibility shifts by language/recency policy become visible and auditable without changing pipeline structure. |
| Multi-parameter interaction check (BL-011) | Single-factor scenarios only | Interaction scenarios (`no_influence_plus_stricter_thresholds`, `valence_up_plus_stricter_thresholds`) | BL-011 interaction matrix and `interaction_coverage_summary` | Interaction effects are explicitly separated from single-factor effects, strengthening controllability interpretation discipline. |

This table closes the remaining "implicit ablation" gap by making profile/scenario perturbations explicit and traceable to concrete evidence surfaces already executed in the active implementation.

### 5.5.2 Sensitivity-Analysis Write-Through (Diagnostics To Chapter Evidence)

Table 5.5 turns existing sensitivity diagnostics into explicit chapter-facing interpretation anchors. This avoids treating sensitivity as an implicit side effect of control runs and instead reports where directional change evidence is expected to appear.

| Sensitivity focus | Primary diagnostic surface | Evidence interpretation in this chapter |
| --- | --- | --- |
| BL-006 score-component perturbation sensitivity | BL-006 `scoring_sensitivity_diagnostics` (exposed through BL-009) | Confirms that bounded component perturbations produce auditable rank-overlap and dominance-shift diagnostics rather than opaque score changes. |
| BL-005 threshold sensitivity | BL-005 threshold-attribution and bounded what-if diagnostics (propagated to BL-009 retrieval summaries) | Shows threshold tightening/loosening effects as directional candidate-pool pressure, supporting bounded retrieval-control claims. |
| BL-007 assembly-policy sensitivity | BL-007 tradeoff and influence assembly diagnostics under policy variants (`competitive`, `reserved_slots`, `hybrid_override`) | Links policy toggles to observable assembly behavior changes while preserving deterministic execution posture. |
| BL-011 interaction sensitivity | BL-011 interaction matrix and `interaction_coverage_summary` | Distinguishes single-factor effects from interaction effects so controllability claims are not over-attributed to one-factor runs only. |
| BL-009 cross-stage sensitivity traceability | BL-009 control-causality, cross-stage influence attribution, and validity-boundary summaries | Ensures sensitivity interpretation remains cross-stage traceable and bounded by explicit non-claim/validity framing. |

Together, Tables 5.4 and 5.5 provide a two-layer evidence posture: ablation coverage (what was varied) and sensitivity write-through (how observed directional shifts are interpreted).

## 5.6 Control-Causality and Validity-Boundary Hardening
The most important late REB-M3 result is not only that tranche-3 passed, but that the underlying contract was strengthened after the first pass.

First, BL-008 explanations now carry `control_provenance`, which exposes the specific scoring and transparency settings that shaped explanation output. Second, BL-009 emits `validity_boundaries` at the top level rather than burying bounded-guidance evidence inside nested diagnostics. Third, BL-011 records explicit no-op control diagnostics so weak or ineffective controls are visible rather than silently ignored.

The follow-up hardening step added a direct section-validator requirement for top-level `validity_boundaries`, guarded by unit tests. This moves failure detection closer to the source of schema drift, rather than relying only on late-stage quality gates.

## 5.7 Interpretation Discipline
Results in this chapter are interpreted as engineering-evidence results, not as proof that the recommender is globally optimal or universally preferable. A pass verdict means that the intended control/evidence contract is currently implemented and auditable under bounded scope. It does not mean that the pipeline eliminates ambiguity, perfectly reflects human preference, or dominates alternative recommender families [@tintarev_evaluating_2012; @jannach_measuring_2019; @bauer_exploring_2024].

In that sense, this chapter tests whether the selected option from Section 3.3.1 is internally coherent and evidentially defensible under the declared thesis constraints. It does not claim that non-selected options are invalid in other data regimes or contribution settings.

## 5.8 Current Limits Visible in the Evidence
The current evidence surface still has explicit limits.

1. BL-010 reproducibility evidence is based on fixed-input replay and should be interpreted as artifact-level, contract-bounded replay consistency under fixed inputs and a pinned configuration snapshot. It does not claim cross-environment or cross-OS behavioral invariance, output identity under different run configurations, or broader environmental runtime invariance beyond the pinned configuration window. Raw output file hashes vary across replays by design (due to volatile run-metadata fields such as run_id and generated_at_utc); stable-hash comparison explicitly excludes these fields.
2. BL-011 includes no-op control diagnostics, which means some exposed controls remain weak or data-regime-dependent even though the measurement surface is now more honest.
3. BL-003 still reports a substantial unmatched portion of cross-source events. In the canonical active baseline, only 15.95% of imported history aligns to the offline corpus, so the current 15% match-rate gate should be interpreted as a minimum viability threshold rather than evidence of broad corpus coverage.
4. Bounded-guidance claims depend on visibility of scope and caveat reporting, not on wide external validation or user-study evidence [@beel_towards_2016; @bellogin_improving_2021; @cavenaghi_systematic_2023].

## 5.9 Chapter Summary
Chapter 5 evaluates the rebuilt artefact through objective-linked evidence contracts rather than legacy MVP reporting. The current result is that O1 to O6 have executable acceptance evidence, wrapper validation remains green, and late hardening work has moved bounded-guidance and control-causality reporting from implied behavior to explicit, testable contract surfaces.
