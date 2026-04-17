# Chapter 4: Implementation Architecture and Evidence Surfaces

## 4.1 Chapter Aim and Scope
This chapter reports the implemented architecture and the concrete evidence surfaces produced by the rebuilt artefact definition locked in REB-M3. It does not judge pass/fail outcomes. Instead, it specifies what was implemented, how objective-linked evidence is emitted, and how the design properties defined in Chapter 3 become visible in execution before formal evaluation in Chapter 5.

The chapter remains bounded to the active deterministic single-user scope and focuses on traceable control/evidence pathways rather than benchmark-comparison claims [@jannach_measuring_2019; @bauer_exploring_2024; @anelli_elliot_2021].

## 4.2 Chapter 3 to Chapter 4 Continuity Mapping
To prevent pre-rebuild design drift, each Chapter 3 commitment is mapped to one explicit implementation surface.

| Chapter 3 design commitment | Chapter 4 implementation check | Active evidence artifact |
| --- | --- | --- |
| O1 uncertainty-aware profiling | Confirm BL-004 exposes inspectable uncertainty and attribution structures | `07_implementation/src/profile/outputs/bl004_preference_profile.json` |
| O2 confidence-aware alignment and candidate shaping | Confirm BL-003 and BL-005 expose confidence and exclusion pathways | `07_implementation/src/alignment/outputs/bl003_ds001_spotify_summary.json`, `07_implementation/src/retrieval/outputs/bl005_candidate_diagnostics.json` |
| O3 controllable trade-offs | Confirm BL-006 and BL-007 preserve explicit scoring/assembly control surfaces | `07_implementation/src/scoring/outputs/bl006_score_summary.json`, `07_implementation/src/playlist/outputs/bl007_assembly_report.json` |
| O4 mechanism-linked explanation fidelity | Confirm BL-008 explanation payloads remain tied to mechanism-level contributors | `07_implementation/src/transparency/outputs/bl008_explanation_payloads.json` |
| O5 reproducibility and controllability readiness | Confirm BL-010 and BL-011 execution layers are present and traceable | `07_implementation/src/reproducibility/outputs/reproducibility_report.json`, `07_implementation/src/controllability/outputs/controllability_report.json` |
| O6 bounded-guidance surfaces | Confirm BL-007 and BL-009 expose explicit boundary-reporting structures | `07_implementation/src/playlist/outputs/bl007_assembly_report.json`, `07_implementation/src/observability/outputs/bl009_run_observability_log.json` |

This mapping matters because Chapter 4 is not only listing implementation modules. It is showing where the Chapter 3 design properties can be inspected in execution. Uncertainty visibility should be observable in alignment and profiling outputs, candidate-generation visibility in retrieval diagnostics, trade-off control in scoring and assembly reports, explanation fidelity in BL-008 payloads, and bounded-guidance surfaces in BL-007 and BL-009 reporting structures.

## 4.3 Implementation Overview
The rebuilt implementation remains a staged deterministic pipeline, but the stages are treated as evidence-producing architecture surfaces rather than only a recommendation workflow.

1. BL-003 alignment establishes cross-source seed construction with match-confidence, ambiguity, and unmatched diagnostics, making uncertainty visible at the point where evidence enters execution.
2. BL-004 profile construction emits semantic, numeric, attribution, and uncertainty structures so the preference profile remains inspectable rather than latent.
3. BL-005 retrieval shapes the candidate pool and records exclusion pathways, making candidate-space definition visible before ranking begins.
4. BL-006 scoring emits active component weights, strategy settings, and score-distribution outputs so ranked outcomes remain traceable to named mechanisms.
5. BL-007 assembly records constraint pressure, warning pathways, and ordering-rule effects, exposing playlist-level trade-offs as explicit execution behavior rather than hidden post-processing.
6. BL-008 explanation payloads map ranked outputs to mechanism contributors and control provenance, preserving the Chapter 3 requirement for explanation fidelity.
7. BL-009 observability consolidates lineage, config traceability, execution scope, and validity boundaries so run-level evidence remains reviewable across stages.
8. BL-010 and BL-011 remain executable evaluation layers for replayability and controllability, extending the implementation surface into explicit evidence-ready checks.
9. REB-M3 tranche gates provide objective-level acceptance checks over the above surfaces, linking local stage outputs back to the thesis-wide design contract.

Taken together, these stages show that the implemented artefact is not only functionally staged. It is instrumented so that the main design properties declared in Chapter 3 remain visible in the execution record itself.

## 4.4 Evidence Packaging
All active implementation evidence resolves through the canonical `07_implementation/src` output surface.

- Objective-gate evidence:
	- `07_implementation/src/quality/outputs/reb_m3_tranche1_gate_report.json`
	- `07_implementation/src/quality/outputs/reb_m3_tranche2_gate_report.json`
	- `07_implementation/src/quality/outputs/reb_m3_tranche3_gate_report.json`
- Core stage outputs:
	- `07_implementation/src/alignment/outputs/bl003_ds001_spotify_summary.json`
	- `07_implementation/src/profile/outputs/bl004_preference_profile.json`
	- `07_implementation/src/retrieval/outputs/bl005_candidate_diagnostics.json`
	- `07_implementation/src/scoring/outputs/bl006_score_summary.json`
	- `07_implementation/src/playlist/outputs/bl007_assembly_report.json`
	- `07_implementation/src/transparency/outputs/bl008_explanation_payloads.json`
	- `07_implementation/src/observability/outputs/bl009_run_observability_log.json`
- Evaluation-layer outputs (used in Chapter 5):
	- `07_implementation/src/reproducibility/outputs/reproducibility_report.json`
	- `07_implementation/src/controllability/outputs/controllability_report.json`
- Wrapper execution evidence (used in Chapter 5):
	- `BL013-ENTRYPOINT-20260412-141352-373476`
	- `BL014-SANITY-20260412-141423-183313`

This packaging structure is important because it makes the Chapter 3 design commitments inspectable as an evidence bundle rather than as dispersed implementation fragments. Alignment, profiling, candidate shaping, scoring, assembly, explanation, and observability each emit their own outputs, while the tranche gates and wrapper checks show that these local surfaces also participate in one coherent execution contract.

## 4.5 Chapter Summary
Chapter 4 defines the implemented architecture and its evidence surfaces under the rebuild contract. The chapter establishes where objective-linked evidence is generated, how the Chapter 3 design properties remain visible from alignment through observability, and how those stage outputs are packaged into one inspectable execution record. Formal evaluation of these surfaces, including success conditions and bounded interpretation, is presented in Chapter 5.
