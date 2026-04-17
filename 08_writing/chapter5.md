# Chapter 5: Evaluation and Results

## 5.1 Chapter Aim and Scope
This chapter evaluates the implementation surfaces defined in Chapter 4 against the objective-to-control-to-evidence contract formalized in Chapter 3. It is not a benchmark-comparison chapter. Instead, it tests whether the rebuilt deterministic pipeline satisfies objective-linked success conditions under bounded scope [@jannach_measuring_2019; @bauer_exploring_2024; @anelli_elliot_2021].

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
| Validate-only orchestration | `BL013-ENTRYPOINT-20260412-141352-373476` | `pass` | Confirms the current active wrapper path completes without contract failure. |
| Sanity suite | `BL014-SANITY-20260412-141423-183313` | `pass (28/28)` | Confirms active stage contracts remain internally consistent after the rebuild hardening wave. |
| Reproducibility report | `07_implementation/src/reproducibility/outputs/reproducibility_report.json` | `pass` | BL-010 records deterministic replay status and retry-boundary reporting under fixed-input replay. |
| Controllability report | `07_implementation/src/controllability/outputs/controllability_report.json` (`run_id=BL011-CTRL-20260412-134945`) | `pass` | BL-011 reports repeat-consistent scenario execution and explicit no-op control diagnostics where effect is absent. |
| Observability schema and scope | `07_implementation/src/observability/outputs/bl009_run_observability_log.json` (`run_id=BL009-OBSERVE-20260412-141422-422054`) | `pass` | BL-009 includes execution scope, upstream lineage, canonical config-pair traceability, and explicit validity-boundary reporting. |

## 5.6 Control-Causality and Validity-Boundary Hardening
The most important late REB-M3 result is not only that tranche-3 passed, but that the underlying contract was strengthened after the first pass.

First, BL-008 explanations now carry `control_provenance`, which exposes the specific scoring and transparency settings that shaped explanation output. Second, BL-009 emits `validity_boundaries` at the top level rather than burying bounded-guidance evidence inside nested diagnostics. Third, BL-011 records explicit no-op control diagnostics so weak or ineffective controls are visible rather than silently ignored.

The follow-up hardening step added a direct section-validator requirement for top-level `validity_boundaries`, guarded by unit tests. This moves failure detection closer to the source of schema drift, rather than relying only on late-stage quality gates.

## 5.7 Interpretation Discipline
Results in this chapter are interpreted as engineering-evidence results, not as proof that the recommender is globally optimal or universally preferable. A pass verdict means that the intended control/evidence contract is currently implemented and auditable under bounded scope. It does not mean that the pipeline eliminates ambiguity, perfectly reflects human preference, or dominates alternative recommender families [@tintarev_evaluating_2012; @jannach_measuring_2019; @bauer_exploring_2024].

## 5.8 Current Limits Visible in the Evidence
The current evidence surface still has explicit limits.

1. BL-010 reproducibility evidence is based on fixed-input replay and should be interpreted as contract-bounded repeatability, not as a claim that every raw output file hash is invariant under all runtime metadata.
2. BL-011 includes no-op control diagnostics, which means some exposed controls remain weak or data-regime-dependent even though the measurement surface is now more honest.
3. BL-003 still reports a substantial unmatched portion of cross-source events. In the canonical active baseline, only 15.95% of imported history aligns to the offline corpus, so the current 15% match-rate gate should be interpreted as a minimum viability threshold rather than evidence of broad corpus coverage.
4. Bounded-guidance claims depend on visibility of scope and caveat reporting, not on wide external validation or user-study evidence [@beel_towards_2016; @bellogin_improving_2021; @cavenaghi_systematic_2023].

## 5.9 Chapter Summary
Chapter 5 evaluates the rebuilt artefact through objective-linked evidence contracts rather than legacy MVP reporting. The current result is that O1 to O6 have executable acceptance evidence, wrapper validation remains green, and late hardening work has moved bounded-guidance and control-causality reporting from implied behavior to explicit, testable contract surfaces.
