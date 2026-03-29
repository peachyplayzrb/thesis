# Evaluation Plan

Last updated: 2026-03-29

## Evaluation Scope
Evaluate whether the artefact delivers deterministic behavior, transparent reasoning, and usable controllability under BSc-feasible conditions.

## What Will Be Evaluated
1. Reproducibility of recommendation runs.
2. Transparency and inspectability of recommendation logic.
3. Effect of controllability parameters on outputs.
4. Playlist-level quality constraints (basic coherence/diversity rules).
5. Implementation/testing rigor expected by module marking guidance.

## Evaluation Criteria
- `reproducibility`: identical input + config -> identical playlist output.
- `traceability`: each recommended track has readable score contribution breakdown.
- `controllability`: controlled parameter changes cause interpretable output shifts.
- `constraint_compliance`: generated playlists satisfy configured assembly constraints.
- `testing_quality`: documented test method, tools, results, and critical interpretation.

## Evaluation Methods
1. Deterministic replay tests:
- run same configuration multiple times and compare output identity.
2. Parameter sensitivity tests:
- change one control parameter at a time and measure ranked list/playlist deltas.
3. Explanation fidelity checks:
- validate explanation values against scoring function inputs and rule adjustments.
4. Rule compliance checks:
- verify playlist constraints (length, repetition, diversity/ordering) are enforced.
5. Lightweight qualitative inspection (optional but useful):
- small structured reflection from supervisor/user perspective on explanation clarity.

## Control-To-Metric Test Matrix

Use Table EP-1 as the execution contract between design intent and Chapter 4 evidence.

| Test ID | Control or condition | Manipulation | Primary metric(s) | Evidence artifact(s) | Pass rule |
| --- | --- | --- | --- | --- | --- |
| `EP-REPRO-001` | Fixed input + fixed config | Repeat identical run 3 times | `ranked_output_hash_match`, `playlist_output_hash_match` | run logs + output hashes | All repeated runs produce identical ranked and playlist hashes |
| `EP-EXPL-001` | Explanation fidelity | Reconstruct sampled final scores from trace components | `reconstruction_error`, field completeness | score trace + explanation payload | Reconstruction error within tolerance and no missing mandatory explanation fields |
| `EP-CTRL-001` | Influence tracks | Add/remove defined influence-track set | `top_k_overlap_delta`, `rank_shift_summary` | baseline/variant ranking snapshots | Directional shift is observable and explainable from profile/score traces. **Implementation caveat (BL-011)**: current testing shows zero measured playlist shift from influence-track actuation via the pre-profile injection path; this is a documented limitation, not an evaluation failure — report observed effect size and cite `05_design/CONTROL_SURFACE_REGISTRY.md` WEAK status. |
| `EP-CTRL-002` | Feature weight | Increase one feature weight while others fixed | `score_component_delta`, `rank_shift_summary` | config diff + score traces | Score/rank changes align with expected weighted feature emphasis |
| `EP-CTRL-003` | Candidate threshold | Tighten/loosen candidate filter threshold | `candidate_pool_size`, `playlist_overlap` | candidate diagnostics + outputs | Candidate pool changes as configured and downstream effects remain interpretable |
| `EP-RULE-001` | Playlist length rule | Vary target playlist length | `actual_playlist_length` | playlist output + rule logs | Output length equals configured target or explicit violation logged |
| `EP-RULE-002` | Artist repetition limit | Lower max repeats per artist | `max_artist_repeats_observed` | playlist output + rule logs | Observed repeats do not exceed configured limit |
| `EP-OBS-001` | Run observability completeness | Execute full pipeline run | required-field completeness over run schema | run metadata + stage diagnostics | All required run sections present (metadata, config, alignment, scoring, assembly, output) |
| `EP-ALIGN-001` | Alignment behavior visibility | DS-001 direct alignment with source-scope filtering enabled | `matched_events`, `unmatched_rate`, `match_method_counts`, `effective_scope_recorded` | alignment summary + scope manifest + diagnostics | Match/unmatched categories, method counts, and effective scope are all reported with traceable artifacts |

## Measurement Rules

1. Use one-factor-at-a-time changes for controllability tests.
2. Keep input artifacts and non-target parameters fixed for each sensitivity run.
3. Record baseline and variant `config_hash` values for every comparison.
4. Prefer deterministic hash comparison for replay checks before human interpretation.
5. If a test fails, record failure cause hypothesis and whether it is implementation defect, data limitation, or accepted scope limitation.

## Chapter 4 Reporting Contract

Chapter 4 should report EP-1 outcomes in three result tables:

1. Reproducibility and observability outcomes (`EP-REPRO-*`, `EP-OBS-*`, `EP-ALIGN-*`).
2. Controllability outcomes (`EP-CTRL-*`, `EP-RULE-*`).
3. Explanation fidelity outcomes (`EP-EXPL-*`).

## Evidence Artifacts To Produce
- test logs and run configs in `07_implementation/test_notes.md` and experiment records.
- summarized metrics/tables for reproducibility and parameter effects.
- critical discussion of failures, trade-offs, and limitations for Chapter 5.

## Non-Goals For Evaluation
- Benchmarking against state-of-the-art accuracy models.
- Large-N human subject evaluation.

