# Chapter 5: Evaluation and Results

## 5.1 Chapter Aim and Scope
This chapter evaluates the implementation evidence surfaces defined in Chapter 4 against the objective-to-control-to-evidence contract formalized in Chapter 3. It is not a benchmark-comparison chapter. Instead, it assesses whether the deterministic pipeline satisfies pre-specified objective-linked criteria under bounded scope [@jannach_measuring_2019; @bauer_exploring_2024; @anelli_elliot_2021].

The chapter remains bounded to the single-user, offline-corpus, deterministic execution posture. Claims are therefore restricted to auditable engineering behavior under this scope, not broad recommender-family superiority.

The evaluation questions remain:

1. Does the pipeline make cross-source uncertainty explicit and inspectable?
2. Do alignment and candidate shaping expose confidence and exclusion pathways?
3. Are scoring and assembly trade-offs explicitly controllable?
4. Do explanation payloads remain structurally mechanism-linked?
5. Is reproducibility and controllability evidence executable and auditable?
6. Are validity boundaries and non-claims explicit enough for bounded guidance?

## 5.2 Evaluation Method and Locked Criteria
Evaluation follows an objective-linked method rather than metric-first ranking. Criteria are pre-specified before extraction to reduce post-hoc interpretation drift.

Locked constants:

- O1 missingness criterion: BL-004 must expose missingness and uncertainty markers where feature evidence is incomplete.
- O5 reproducibility replay count: 3 fixed-config replays.
- O4 structural-fidelity sample: 30 tracks (10 selected, 10 rejected, 10 boundary-ranked).
- O4 percentile tolerance: absolute difference <= 1.0 percentile point versus BL-006 source value.
- O5 measurable-delta rule: at least one downstream shift threshold met per tested variation (candidate-set >= 1.0% of baseline or >= 3 tracks, score-summary shift >= 0.01, or playlist composition change >= 1 track).

Table 5.1 defines active acceptance conditions.

| Objective | Acceptance condition |
| --- | --- |
| O1 | BL-004 includes uncertainty markers for features above missingness threshold, with attribution tracking and confidence-stratified visibility. |
| O2 | BL-003 exceeds minimum match-rate threshold and exposes unmatched reasons; BL-005 exposes separated exclusion pathways. |
| O3 | BL-006 exposes decomposed component scoring and active weights; BL-007 exposes rule activations/relaxations with reasoned diagnostics. |
| O4 | BL-008 required fields (`score_percentile`, `score_band`, attribution, rule effects, confidence marker) are structurally present and consistent against BL-006/BL-007 in the fixed sample. |
| O5 | BL-010 reports deterministic replay consistency for 3 replays; BL-011 reports measurable controllability deltas under the locked threshold rule. |
| O6 | BL-009 includes explicit non-claims and validity boundaries; BL-007 auditable case holds: relaxation evidence when triggered, or explicit no-relaxation confirmation when not triggered. |

## 5.3 O5 Evidence First: Reproducibility and Controllability
Following the credibility-first ordering, O5 is assessed before interpretation-sensitive objectives.

BL-010 reproducibility evidence confirms deterministic replay consistency under fixed inputs/configuration. The current authority report (`run_id=BL010-REPRO-20260419-214941`) records `replay_count=3`, `results.deterministic_match=true`, and `results.status=pass`, with stable-hash reference values present across all tracked stage artifacts.

BL-011 controllability evidence is evaluated through an explicit decision gate:

1. PASS: all tested scenarios meet at least one locked measurable-delta threshold.
2. PARTIAL: after one mandatory rerun attempt, only a subset of scenarios meets thresholds.
3. FAIL: no tested scenarios meet thresholds.

Using the refreshed BL-011 authority (`run_id=BL011-CTRL-20260427-174210`), the controllability gate resolves to FAIL: `0/7` non-baseline scenarios met the locked minimum-delta condition (candidate-pool shift, score-summary shift, or playlist composition change). This is consistent with the report-level summary (`results.status="bounded-risk"`, `all_variant_shifts_observable=false`, `no_op_controls_count=4`).

Table 5.2 summarizes O5 execution authorities.

| Check | Active evidence | Current reading |
| --- | --- | --- |
| Validate-only orchestration | `BL013-ENTRYPOINT-20260418-035540-208118` | Pass, pipeline contract completes end-to-end. |
| Sanity suite | `BL014-SANITY-20260418-035641-651065` | Pass (36/36), stage contracts internally coherent. |
| Reproducibility report | `07_implementation/src/reproducibility/outputs/reproducibility_report.json` (`BL010-REPRO-20260419-214941`) | Pass (`deterministic_match=true`, `replay_count=3`). |
| Controllability report | `07_implementation/src/controllability/outputs/controllability_report.json` (`BL011-CTRL-20260427-174210`) | Not satisfied under locked gate (`0/7` scenarios reached minimum-delta criteria; report status `bounded-risk`). |

### 5.3.1 Control-Surface Ablation and Sensitivity Write-Through

Table 5.3 restores the explicit ablation/sensitivity view so controllability evidence remains concrete and traceable to named variant scenarios.

| Scenario or axis | Expected direction | Observed in refreshed BL-011 |
| --- | --- | --- |
| `no_influence_tracks` | Shift away from influence-steered profile effects | Observable-shift flag present, but measurable-delta thresholds not met under locked gate. |
| `valence_weight_up` | Rank and contribution shift toward boosted component | No locked measurable delta observed; flagged as no-op in diagnostics. |
| `stricter_thresholds` | Candidate pool contraction and downstream reordering | No locked measurable delta observed; flagged as no-op in diagnostics. |
| `looser_thresholds` | Candidate pool expansion and downstream reordering | No locked measurable delta observed; flagged as no-op in diagnostics. |
| `fuzzy_enabled_strict` | Retrieval-side behavior shift under fuzzy controls | No locked measurable delta observed. |
| `no_influence_plus_stricter_thresholds` | Interaction effect beyond single-factor changes | Interaction row present; locked measurable-delta criteria not met. |
| `valence_up_plus_stricter_thresholds` | Interaction effect from combined score and threshold pressure | Interaction row present; locked measurable-delta criteria not met. |

This write-through keeps the controllability section auditable: scenario coverage exists, but current measurable-delta evidence is insufficient for O5 satisfaction under the locked threshold rule.

## 5.4 O1 Evidence: Uncertainty-Aware Profiling
O1 is evaluated using BL-003 alignment diagnostics and BL-004 profile structure. BL-003 exposes input uncertainty at intake (matched, ambiguous, unmatched, invalid pathways where available), and BL-004 carries uncertainty-aware profile representations with attribution surfaces.

Concrete observations from active artifacts: BL-003 reports `input_event_rows=9902`, `ambiguous_matches=19`, `invalid_records=0`, and explicit unmatched counts (`unmatched=7457`). BL-004 reports `events_total=1369`, `missing_numeric_track_count=0`, and confidence-bin diagnostics (`high_0_9_plus=1369`, medium/low bins `0`), with attribution continuity via `history_weight_share=0.99849` and `influence_weight_share=0.00151`.

Under the locked criterion, O1 is therefore satisfied: uncertainty and confidence structure are explicitly surfaced rather than latent.

## 5.5 O2 Evidence: Confidence-Aware Alignment and Candidate Shaping
O2 is evaluated through BL-003 and BL-005. BL-003 provides match-rate and unmatched-reason visibility; BL-005 records candidate shaping decisions and separated exclusion pathways.

The refreshed BL-003 authority reports `actual_match_rate=0.245` against `min_threshold=0.15` (`status=pass`), with explicit pathway counts (`matched_by_spotify_id=1489`, `matched_by_metadata=937`, `ambiguous_matches=19`, `unmatched=7457`). BL-005 reports `candidate_rows_total=109269`, `kept_candidates=23257` (about 21.3%), and separated pathway diagnostics including `influence_admitted=0`.

Match-rate interpretation remains bounded: even when current run authority is above threshold, the threshold itself is a minimum viability gate, not evidence of broad cross-source coverage.

For continuity with earlier validated chapter evidence, the previously cited canonical baseline aligned share (15.95%) remains an important boundary reference: passing a 15% gate should be interpreted as viability under constraints, not as broad corpus coverage.

Within this framing, O2 is satisfied because confidence and exclusion pathways are explicit and auditable.

## 5.6 O3 Evidence: Controllable Trade-Offs
O3 uses BL-006 and BL-007. BL-006 exposes component-wise scoring structure and active weight vectors. BL-007 records assembly-level rule effects, trade-off pressure, and relaxation behavior where applicable.

BL-006 reports `candidates_scored=23257` with explicit score-distribution metrics (`max_final_score=0.499521`, `mean_final_score=0.221453`, `median_final_score=0.226483`) and active component weights emitted in the report payload. BL-007 reports `tracks_included=10`, `R1_score_threshold` hits `22714`, `novelty_allowance_used=0`, `relaxation_records=[]`, and `undersized_playlist_warning.is_undersized=false`.

O3 is satisfied at the chapter criterion level because control surfaces and trade-off diagnostics are explicit and inspectable, even though BL-011 measurable-effect evidence for O5 remains insufficient.

## 5.7 O4 Evidence: Mechanism-Linked Explanation Fidelity
O4 evaluates structural fidelity, not perceived usefulness. BL-008 must remain traceable to scoring/assembly mechanisms through required payload fields and contributor mapping consistency.

Under the fixed 30-track structural check, mismatches are interpreted with the locked taxonomy:

- Critical mismatch: missing required field, contradictory rule-effect linkage, or wrong primary attribution.
- Minor mismatch: percentile tolerance breach with intact attribution/rule linkage.

Current evidence shows required-field presence for the available selected-track sample: BL-008 (`run_id=BL008-EXPLAIN-20260427-145551-660092`) emits `playlist_track_count=10`, and a structural check over the available selected payloads found `required_field_missing_count=0` for `score_percentile`, `score_band`, `primary_explanation_driver`, and `top_score_contributors`.

Because the locked sample contract is 30 tracks and current selected-track payload coverage is 10, O4 is assessed as Partially Satisfied pending completion of the full fixed-sample extraction cross-check. Perceived-usefulness claims remain routed to Chapter 6.

## 5.8 O6 Evidence: Bounded-Guidance Surfaces
O6 is evaluated through BL-007 and BL-009 boundary reporting. BL-009 must include explicit non-claims and validity boundaries. BL-007 must satisfy one auditable case:

1. Relaxation occurred: recorded with reason codes and diagnostics context.
2. No relaxation occurred: explicit no-relaxation confirmation and corroborating run-level boundary state.

Current artifacts satisfy the no-relaxation case: BL-007 explicitly emits `relaxation_records=[]`, `undersized_playlist_warning.is_undersized=false`, and `shortfall=0`. BL-009 emits top-level `validity_boundaries` and nested reproducibility non-claims (`non_claims` count `4`) under `reproducibility_interpretation`.

This criterion is satisfied because bounded guidance is evidence-backed and auditable rather than implied.

## 5.9 Control-Causality and Boundary Hardening Context
The current evaluation posture reflects hardening steps that were implemented before final chapter synthesis: BL-008 now carries explicit control-provenance structures, BL-009 boundary framing is emitted at top level, and BL-011 records no-op control diagnostics directly rather than masking weak-effect controls. These changes matter because they show that evidence contracts were engineered into the implementation and not added as post-hoc narrative wrappers.

## 5.10 Objective Synthesis and Acceptance Status
Interpretation discipline: the synthesis below reports criterion alignment under bounded artifact authority. It does not imply global recommender superiority or cross-regime generalization.

Table 5.4 consolidates objective outcomes under normalized verdict labels.

| Objective | Primary evidence surface | Verdict |
| --- | --- | --- |
| O1 | BL-003 + BL-004 | Satisfied |
| O2 | BL-003 + BL-005 | Satisfied |
| O3 | BL-006 + BL-007 | Satisfied |
| O4 | BL-008 (+ BL-006/BL-007 cross-check) | Partially Satisfied |
| O5 | BL-010 + BL-011 | Not Satisfied |
| O6 | BL-007 + BL-009 | Satisfied |

## 5.11 Evaluation Boundaries, Non-Claims, and Chapter 6 Handoff
This chapter does not claim:

1. broad cross-user personalization validity,
2. real-time or large-scale deployment performance,
3. superiority over hybrid/neural recommender families,
4. user-perceived explanation usefulness or trust effects.

Chapter 6 handoff logic:

- O5 fully satisfied: discuss reproducibility guarantees and controllability confidence within deterministic bounds.
- O5 partially satisfied: discuss reproducibility guarantees with explicit controllability coverage limits and unconfirmed interaction regions.
- O5 not satisfied (current authority): discuss reproducibility pass evidence alongside controllability shortfall, no-op control diagnostics, and bounded next-step remediation scope.

All claims are therefore bounded to the evidence surfaces and criteria defined here.

## 5.12 Chapter Summary
Chapter 5 evaluates the implemented pipeline through pre-specified objective-linked criteria with evidence-first reporting. O5 is resolved first and currently not satisfied under the locked measurable-delta gate, while O1, O2, O3, and O6 are satisfied and O4 is partially satisfied pending completion of the full fixed-sample structural extraction. The chapter therefore provides a bounded, auditable synthesis that distinguishes verified criterion alignment from unresolved controllability evidence.
