# Test Notes

## Test Case TC-001: Ingestion Schema Validation (MVP)

- Date: 2026-03-13
- Backlog link: `BL-001`, `BL-002`
- Purpose: Verify that raw listening-history export is transformed into the normalized ingestion schema and invalid rows are flagged.

### Inputs
- Dataset/sample: `sample_listening_history.csv` (to be added under implementation test assets).
- Config assumptions:
	- Required fields: `track_name`, `artist_name`, `played_at`, `ms_played`
	- Optional field: `isrc`

### Expected Output
- Every valid row has all normalized required fields populated.
- Missing `isrc` rows are kept and flagged `missing_isrc`.
- Invalid timestamp rows are flagged `invalid_timestamp`.
- Summary metrics produced:
	- `rows_total`
	- `rows_valid`
	- `rows_invalid`
	- `rows_missing_isrc`

### Pass Criteria
- Parser completes without crash on mixed-quality input.
- Output schema matches `06_data_and_sources/schema_notes.md`.
- Validation summary metrics are emitted and internally consistent.

### Actual Result
- Status: pass
- Run evidence:
	- `07_implementation/implementation_notes/run_outputs/tc001_normalized_events.jsonl`
	- `07_implementation/implementation_notes/run_outputs/tc001_summary.json`
	- `07_implementation/implementation_notes/run_outputs/tc001_normalized_events_repeat.jsonl`
	- `07_implementation/implementation_notes/run_outputs/tc001_summary_repeat.json`
- Observed metrics:
	- `rows_total=5`
	- `rows_valid=2`
	- `rows_invalid=3`
	- `rows_missing_isrc=2`
- Notes:
	- Missing ISRC rows are retained and flagged as expected.
	- Invalid timestamp and invalid/missing core field behavior is flagged as expected.

## Reproducibility Log Stub
- `run_id`: `TC001-RUN1`
- `input_hash`: `925340dcd29e7a254ba3a4755d67f0ea582cd9641de7d67f67c69fcd20a77fe6`
- `config_hash`: `manual-mvp-config-v1` (CLI args: parser, source platform, run id, fixed input)
- `output_hash`: `77be60a9e4d483f90f2d71724da9cada0498215010da193bc278aadc6d247eb3`
- `deterministic_repeat_match`: `True`

## Test Case TC-002: ISRC-First Alignment With Metadata Fallback

- Date: 2026-03-13
- Backlog link: `BL-003`
- Purpose: Verify deterministic alignment behavior where ISRC-first matching is used and metadata fallback covers events without ISRC.

### Inputs
- Normalized events:
	- `07_implementation/implementation_notes/run_outputs/tc001_normalized_events.jsonl`
- Candidate corpus sample:
	- `07_implementation/implementation_notes/test_assets/sample_music4all_candidates.csv`

### Expected Output
- Valid events are considered for alignment.
- Hard-invalid rows are skipped by default.
- ISRC matches are preferred when available.
- Metadata fallback can match missing-ISRC rows by normalized `track_name` + `artist_name`.

### Pass Criteria
- Alignment script executes without failure.
- Summary reports `matched_isrc` and `matched_fallback` counts.
- Deterministic repeat run yields same `alignment_output_hash`.

### Actual Result
- Status: pass
- Run evidence:
	- `07_implementation/implementation_notes/run_outputs/tc002_alignment.jsonl`
	- `07_implementation/implementation_notes/run_outputs/tc002_summary.json`
	- `07_implementation/implementation_notes/run_outputs/tc002_alignment_repeat.jsonl`
	- `07_implementation/implementation_notes/run_outputs/tc002_summary_repeat.json`
- Observed metrics:
	- `rows_total=5`
	- `rows_considered=2`
	- `rows_skipped_invalid=3`
	- `matched_total=2`
	- `matched_isrc=1`
	- `matched_fallback=1`
	- `unmatched=0`
	- `match_rate=1.0`
- Reproducibility:
	- `alignment_output_hash=4edd70d71f2996d446301a2914d8467c51d15e5d07bd168fd714494104394418`
	- `repeat_alignment_hash_match=True`

## Reusable Evaluation Templates (Chapter 4)

Use these templates for consistent evidence capture across reproducibility, controllability, traceability, and rule-compliance tests.

### Template A: Reproducibility Replay Test

- `test_id`: `TC-REPRO-XXX`
- `date`: `YYYY-MM-DD`
- `purpose`: Verify identical outputs for identical inputs/config.
- `input_artifacts`:
	- `input_history_path:`
	- `influence_tracks_path:`
	- `candidate_corpus_snapshot:`
- `config_artifact`:
	- `config_path:`
	- `config_hash:`
- `runs`:
	- `run_1_id:`
	- `run_2_id:`
	- `run_3_id:`
- `output_hashes`:
	- `ranked_output_hash_run1:`
	- `ranked_output_hash_run2:`
	- `playlist_output_hash_run1:`
	- `playlist_output_hash_run2:`
- `result`:
	- `deterministic_match:` `True/False`
	- `status:` `pass/fail`
- `notes`:
	- If fail, record first mismatch artifact and likely cause.

### Template B: Parameter Sensitivity Test

- `test_id`: `TC-SENS-XXX`
- `date`: `YYYY-MM-DD`
- `parameter_under_test:`
- `baseline_value:`
- `variant_values:`
	- `v1:`
	- `v2:`
- `fixed_controls`:
	- List all parameters held constant.
- `comparison_metrics`:
	- `top_k_overlap:`
	- `rank_shift_summary:`
	- `playlist_rule_effects:`
- `interpretation`:
	- `directionally_consistent_with_intent:` `True/False`
	- `status:` `pass/fail`
- `notes`:
	- Record non-intuitive shifts and suspected mechanism-level cause.

### Template C: Explanation Fidelity Check

- `test_id`: `TC-EXPL-XXX`
- `date`: `YYYY-MM-DD`
- `sample_tracks_checked:`
	- `track_1_id:`
	- `track_2_id:`
	- `track_3_id:`
- `verification_fields`:
	- `raw_feature_values_present:` `True/False`
	- `feature_contributions_present:` `True/False`
	- `rule_adjustments_present:` `True/False`
	- `final_score_reconstructable:` `True/False`
- `reconstruction_error_tolerance:`
- `status:` `pass/fail`
- `notes`:
	- If fail, document which explanation field is missing or inconsistent.

### Template D: Playlist Rule-Compliance Check

- `test_id`: `TC-RULE-XXX`
- `date`: `YYYY-MM-DD`
- `playlist_id_or_run_id:`
- `configured_rules`:
	- `playlist_length:`
	- `artist_repeat_limit:`
	- `diversity_constraint:`
	- `ordering_constraint:`
- `observed_outcomes`:
	- `actual_playlist_length:`
	- `max_artist_repeats_observed:`
	- `diversity_signal_summary:`
	- `ordering_checks_summary:`
- `violations_detected:` `yes/no`
- `status:` `pass/fail`
- `notes`:
	- If fail, include violating track positions and rule IDs.

### Template E: Alignment Diagnostics Snapshot

- `test_id`: `TC-ALIGN-XXX`
- `date`: `YYYY-MM-DD`
- `events_total:`
- `events_considered:`
- `matched_isrc:`
- `matched_fallback:`
- `unmatched_count:`
- `unmatched_rate:`
- `known_causes`:
	- `missing_isrc_count:`
	- `metadata_conflict_count:`
- `status:` `pass/fail/bounded-risk`
- `notes`:
	- Track whether unmatched behavior stays within accepted MVP limitation bounds.

## Chapter 4 Execution Pack (From Evaluation Matrix EP-1)

Use these as the next priority run set. Keep artifacts under `07_implementation/implementation_notes/run_outputs/`.

## Test Case TC-003: Deterministic Replay (EP-REPRO-001)

- Purpose: Validate deterministic replay under fixed inputs and configuration.
- Inputs:
	- fixed normalized events artifact
	- fixed influence tracks artifact
	- fixed config profile (`config_hash` recorded)
- Procedure:
	1. Run pipeline three times with identical artifacts/config.
	2. Record ranked and playlist output hashes for each run.
	3. Compare run1/run2/run3 hashes.
- Expected:
	- all ranked hashes identical
	- all playlist hashes identical
- Pass criteria:
	- `ranked_output_hash_match=True`
	- `playlist_output_hash_match=True`

## Test Case TC-004: Explanation Fidelity Reconstruction (EP-EXPL-001)

- Purpose: Verify explanation payload is faithful to score traces.
- Inputs:
	- one completed run with score traces and explanation payloads
	- 5 sampled recommended tracks
- Procedure:
	1. Reconstruct final score from stored components for each sampled track.
	2. Compare reconstructed and reported final scores.
	3. Check mandatory explanation fields are present.
- Expected:
	- reconstruction error within tolerance
	- no missing mandatory fields
- Pass criteria:
	- `final_score_reconstructable=True`
	- `reconstruction_error <= defined_tolerance`

## Test Case TC-005: Influence Track Sensitivity (EP-CTRL-001)

- Purpose: Validate controllability through influence tracks.
- Baseline:
	- run with no additional influence tracks
- Variant:
	- run with defined influence-track set
- Procedure:
	1. Keep all non-target parameters fixed.
	2. Compare top-k overlap and rank shifts.
	3. Trace shifts to profile and score components.
- Pass criteria:
	- non-trivial, interpretable rank or composition shift
	- mechanism-level explanation available in traces

## Test Case TC-006: Feature Weight Sensitivity (EP-CTRL-002)

- Purpose: Validate controllability through feature-weight changes.
- Baseline:
	- default feature-weight profile
- Variants:
	- increase one selected feature weight
	- decrease same feature weight
- Procedure:
	1. Hold all other parameters fixed.
	2. Compare score-component deltas and rank shifts.
	3. Confirm direction matches expected feature emphasis.
- Pass criteria:
	- observed score/rank effects are directionally consistent
	- effects are traceable in score components

## Test Case TC-007: Candidate Threshold Sensitivity (EP-CTRL-003)

- Purpose: Validate controllability at candidate-generation stage.
- Variants:
	- stricter threshold
	- looser threshold
- Procedure:
	1. Compare candidate pool size across variants.
	2. Compare final playlist overlap with baseline.
	3. Check output changes remain interpretable.
- Pass criteria:
	- candidate pool size changes with threshold direction
	- downstream changes are explainable from diagnostics

## Test Case TC-008: Playlist Rule Compliance (EP-RULE-001 / EP-RULE-002)

- Purpose: Validate playlist assembly constraints.
- Controls tested:
	- playlist length target
	- artist repetition limit
- Procedure:
	1. Run baseline and rule-variant configurations.
	2. Inspect rule logs and final playlists.
	3. Record any rule violations.
- Pass criteria:
	- actual length equals configured target
	- artist repeats do not exceed limit
	- if violated, explicit violation diagnostics exist

## Test Case TC-009: Observability Completeness (EP-OBS-001)

- Purpose: Validate required run-log schema completeness.
- Procedure:
	1. Execute one end-to-end run.
	2. Verify presence of required sections:
		- run metadata
		- run config
		- ingestion/alignment diagnostics
		- scoring traces
		- assembly diagnostics
		- final outputs
- Pass criteria:
	- all required sections present and linked by `run_id`

## Test Case TC-010: Alignment Path Visibility (EP-ALIGN-001)

- Purpose: Validate ISRC-first/fallback/unmatched reporting quality.
- Procedure:
	1. Execute alignment with mixed ISRC availability sample.
	2. Record `matched_isrc`, `matched_fallback`, and `unmatched_count`.
	3. Record unmatched reason categories.
- Pass criteria:
	- all match-path counts reported
	- unmatched reasons recorded for all unmatched entries

