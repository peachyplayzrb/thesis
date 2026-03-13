# Evaluation Plan

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

## Evidence Artifacts To Produce
- test logs and run configs in `07_implementation/test_notes.md` and experiment records.
- summarized metrics/tables for reproducibility and parameter effects.
- critical discussion of failures, trade-offs, and limitations for Chapter 5.

## Non-Goals For Evaluation
- Benchmarking against state-of-the-art accuracy models.
- Large-N human subject evaluation.
