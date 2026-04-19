# Comprehensive Pipeline Audit — 2026-03-25

## Historical Status Notice

This audit is a pre-rebuild/pre-UNDO hardening snapshot and is retained for traceability, not as the active implementation-status authority.

Active implementation authority has moved to `00_admin/thesis_state.md`, `00_admin/timeline.md`, and current BL-013/BL-014 run surfaces.

### Closeout Mapping (high level)
- CRI-001 (unmatched-track visibility risk): closed by later BL-003/BL-009 diagnostics hardening waves and governance synchronization.
- CRI-002 and CRI-004 (threshold/control validation risks): closed by inter-stage handshake and policy-validation hardening in BL-004 through BL-014.
- CRI-003 (weight-normalization observability risk): closed by BL-006 diagnostics and BL-009 observability enhancements.

For current closure evidence and run IDs, use the latest accepted entries in `00_admin/change_log.md` and `00_admin/decision_log.md`.

**Status:** Detailed analysis of thesis pipeline implementation
**Date:** 2026-03-25
**Coverage:** Architecture, design, implementation, governance, observability, edge cases
**Depth:** Thorough investigation with root-cause analysis

---

## Executive Summary

The thesis pipeline (BL-003 through BL-009, with orchestration via BL-013) is broadly functional and passes basic validation checks (BL-014: 21/21 checks). However, a systematic audit has identified **13 critical and high-priority issues** spanning data integrity, error handling, control-surface gaps, and observability blind spots. Most issues are **silent failures** or **edge cases that silently degrade quality** rather than throwing exceptions.

**Immediate action recommended:** Address critical issues before thesis submission hardening, particularly around unmatched-track handling, weight normalization, and numeric threshold validation.

---

## CRITICAL ISSUES

### CRI-001: Unmatched Track Silent Discard in BL-003 May Bias Preference Profile

**Description:**
In [build_bl003_ds001_spotify_seed_table.py](build_bl003_ds001_spotify_seed_table.py#L1) (`BL-003`), when Spotify-imported tracks fail to match the DS-001 corpus by both Spotify ID and normalized metadata, they are written to `bl003_ds001_spotify_unmatched.csv` but **not included in the seed table**. The BL-004 preference profile then builds from only the matched subset.

On the latest run (2026-03-24):
- Input events (after scope filter): 637
- Matched: 224 (35.2%)
- Unmatched: 413 (64.8%)

**Impact/Risk:**
- **Data loss bias:** 64.8% of imported user history is discarded. If unmatched tracks are systematically different (e.g., newer, more obscure, in specific genres), the preference profile becomes a biased view of the user's true listening habits.
- **Thesis validity concern:** Claims about "user preference" in the playlist outputs now rest on an incomplete signal. Chapter 3 assumes imported data are representative.
- **Reproducibility risk:** If the DS-001 corpus changes or mapping logic is improved, downstream baselines shift unpredictably.

**Affected Components:**
- BL-003 (seed construction)
- BL-004 (preference profile — builds only on matched seeds)
- BL-005, BL-006, BL-007 (downstream scoring and assembly rest on biased profile)
- Chapter 3, Chapter 4 (claims about preference accuracy and controllability)

**Current Mitigation (Weak):**
- BL-003 summary logs `unmatched_count` and writes unmatched rows to a separate CSV.
- BL-009 observability log records `history_track_count` and `matched_track_count`.
- **Issue:** No documented policy on acceptable match rates. No guidance on how to interpret or handle high unmatch rates.

**Suggested Mitigation:**
1. **Define acceptance threshold:** Document minimum acceptable match rate (e.g., ≥70%). Fail fast at BL-003 if match rate falls below threshold.
2. **Fallback strategy:** Consider whether unmatched tracks should contribute reduced-weight influence signals or be completely excluded.
3. **Sensitivity analysis:** Add a BL-011 scenario testing the effect of unmatched-vs-matched weighting bias on playlist outputs.
4. **Thesis transparency:** Explicitly state in Chapter 3 and Chapter 4 that preference profiles are built from **matched import subset only**, with measured bias quantification.

---

### CRI-002: Numeric Threshold Mismatch Between BL-005 (Filtering) and BL-006 (Scoring)

**Description:**
Both BL-005 and BL-006 define independent numeric thresholds for features (tempo, key, mode, duration). While defaults are synchronized, they are **separate, independently configurable** parameters:

- **BL-005** (retrieval): `retrieval_controls.numeric_thresholds` — used to gate which candidates pass a Boolean proximity test
- **BL-006** (scoring): `scoring_controls.numeric_thresholds` — used to compute continuous similarity scores

From [run_config_template_v1.json](run_config_template_v1.json#L1):
```json
"retrieval_controls": {
  "numeric_thresholds": { "tempo": 20.0, "key": 2.0, "mode": 0.5, "duration_ms": 45000.0 }
},
"scoring_controls": {
  "numeric_thresholds": { "tempo": 20.0, "key": 2.0, "mode": 0.5, "duration_ms": 45000.0 }
}
```

**Issue:**
An operator (or test suite) could unknowingly set different thresholds. Example:
- `retrieval_controls.numeric_thresholds.tempo = 15.0` (stricter filter)
- `scoring_controls.numeric_thresholds.tempo = 20.0` (looser score)

Result: A candidate that barely passes the filter (14.9 BPM away) could receive a high tempo-similarity score during scoring, despite being nearly rejected. The semantic meaning is broken.

**Impact/Risk:**
- **Silent inconsistency:** No error is raised. Playlist outputs become hard to interpret ("why was this borderline track admitted and scored highly?").
- **Reproducibility confusion:** Different runs with slightly different threshold configs produce structurally different playlists without clear causality.
- **Control-surface incoherence:** Users or evaluators expect that retrieval and scoring use aligned thresholds but cannot enforce this in the run-config schema.

**Affected Components:**
- BL-005 (candidate filtering)
- BL-006 (scoring)
- BL-013 (orchestration and config validation)
- BL-011 (controllability evaluation — scenarios may inadvertently trigger this inconsistency)

**Current Mitigation (Weak):**
- Run-config defaults are synchronized.
- **No validation** in `run_config_utils.py` to prevent drift.

**Suggested Mitigation:**
1. **Enforce schema constraint:** Modify `run_config_utils.py`'s validation to check that `retrieval_controls.numeric_thresholds == scoring_controls.numeric_thresholds` (or at least emit a warning if they differ).
2. **Alternative:** Consolidate thresholds into a single `numeric_thresholds` block used by both BL-005 and BL-006.
3. **Document in semantic control map:** Explicitly note this coupling and the validation rule.
4. **Test coverage:** Add a BL-011 scenario that intentionally diverges thresholds to demonstrate the effect (or fails if divergence is disallowed).

---

### CRI-003: Missing Component Weight Validation After Normalization

**Description:**
In [build_bl006_scored_candidates.py](build_bl006_scored_candidates.py#L1) (lines 45–65), component weights are rebalanced when numeric features are unavailable:

```python
def build_active_component_weights(
    active_numeric_components: set[str],
    component_weights: dict[str, float],
) -> dict[str, float]:
    active = {
        component: weight
        for component, weight in component_weights.items()
        if component not in NUMERIC_COMPONENTS or component in active_numeric_components
    }
    total = sum(active.values())
    if total <= 0:
        raise RuntimeError("BL-006 requires at least one active scoring component")
    return {component: weight / total for component, weight in active.items()}
```

**Issue:**
The normalization is correct. However, there is **no downstream auditing** that the re-normalized weights are sane:
1. After re-normalization, a single component (e.g., `tag_overlap`) could balloon to 80–90% of the total weight if all numeric features are missing.
2. No warning or diagnostic is emitted if this rebalancing occurs.
3. No check validates that the input `component_weights` sum to 1.0 before re-normalization.

**Example failure mode:**
If a user supplies `component_weights = {"tempo": 0.5, ...}` (invalid: sum >> 1.0), and all numeric features are absent, the active weights become even more distorted. The system silently proceeds.

**Impact/Risk:**
- **Silent scoring instability:** Re-normalized weights can change dramatically without operator awareness.
- **Invalid input acceptance:** Malformed weight configs don't fail early.
- **Score interpretation risk:** Explanations (BL-008) may cite "top contributors" that are actually artifacts of weight normalization, misleading users about causality.

**Affected Components:**
- BL-006 (scoring)
- BL-008 (transparency — explanation payloads cite component contributions)
- BL-009 (observability — should log weight re-normalizations)

**Current Mitigation (Weak):**
- BL-009 logs `component_weights_normalized` in the run observability log.
- **Issue:** Normalization is logged, but no trigger or warning if normalization significantly alters weights.

**Suggested Mitigation:**
1. **Validate input weights:** In `run_config_utils.py`, enforce that `scoring_controls.component_weights` sum to 1.0 (within floating-point tolerance, e.g., 0.99–1.01).
2. **Emit rebalance warning:** In BL-006, if weight re-normalization is triggered, emit a warning and log the delta in each component's effective weight.
3. **Explain constraint:** Document in semantic_control_map.md that component weights must sum to 1.0.
4. **Sanity check:** BL-014 should include a check that normalized weights sum to 1.0 within tolerance.

---

### CRI-004: No Validation of Numeric Thresholds ≤ 0

**Description:**
Throughout the pipeline, numeric thresholds are used directly without validation that they are positive. Examples:

- [build_bl005_candidate_filter.py](build_bl005_candidate_filter.py#L1): `numeric_thresholds.tempo`, `numeric_thresholds.key`, etc.
- [build_bl006_scored_candidates.py](build_bl006_scored_candidates.py#L1): Same thresholds used for similarity computation.
- [run_config_utils.py](run_config_utils.py#L1): No explicit validation on numeric threshold values.

**Issue:**
If a threshold is set to 0 or negative:
- **BL-005 filtering:** The Boolean gate becomes meaningless (all candidates either always pass or always fail, depending on comparison logic).
- **BL-006 scoring:** Similarity functions compute using division and subtraction; a threshold of 0 could cause division by zero or produce invalid similarity values (e.g., negative scores).

Example:
```json
"numeric_thresholds": { "tempo": 0.0, "key": -2.0, ... }
```

This config would be silently accepted and processed.

**Impact/Risk:**
- **Silent pipeline corruption:** Scoring produces invalid or meaningless results without error.
- **Thesis validity risk:** If a mistaken threshold config were used in final evaluation, outputs are invalid but appear to be generated cleanly.

**Affected Components:**
- BL-005 (retrieval filtering)
- BL-006 (scoring)
- BL-013 (config validation)
- BL-014 (sanity checks — should catch invalid scores)

**Current Mitigation (Weak):**
- BL-006 has a check: `threshold > 0` in line 46 when applying overrides. However, this is only for environment-variable overrides, not run-config values.
- **Issue:** Run-config thresholds bypass this check.

**Suggested Mitigation:**
1. **Add validation in run_config_utils.py:** In `resolve_effective_run_config()`, iterate through all numeric threshold fields and enforce `value > 0`.
2. **Raise RunConfigError:** If any threshold is ≤ 0, raise a clear error.
3. **Update defaults:** Ensure all default thresholds are explicitly positive in `DEFAULT_RUN_CONFIG`.
4. **Document:** Specify in semantic_control_map.md that thresholds must be positive.

---

### CRI-005: Circular Key Distance Computation May Produce Incorrect Matches

**Description:**
Musical keys are circular (0–11 semitones, wrapping). When computing key distance, you must account for circularity:
- Distance from key 0 (C) to key 11 (B) should be 1 semitone, not 11.

From [build_bl005_candidate_filter.py](build_bl005_candidate_filter.py#L1):
```python
NUMERIC_FEATURE_SPECS = {
    "key": {
        "candidate_column": "key",
        "threshold": 2.0,
        "circular": True,  # <-- Flag is set
    },
    ...
}
```

The `circular` flag is defined but appears to **not be used** in the actual distance computation. Searching the code:

- In BL-005 filtering: The distance is computed as part of the generic `candidate_numeric_value()` function, which does not appear to apply circular-distance logic.
- In BL-006 scoring: Similarly, the key similarity is computed via a generic numeric similarity function without circular wrapping.

**Impact/Risk:**
- **Silent mismatch:** Keys near the wraparound (e.g., 0 and 11) are scored as very different, even though they are musically adjacent. This biases filtering and scoring against perfectly valid matches.
- **Playlist quality risk:** Good candidates are incorrectly rejected or down-scored because of key-distance miscalculation.
- **Reproducibility concern:** If this bug is fixed later, all evaluation runs change unpredictably.

**Affected Components:**
- BL-005 (candidate filtering — incorrectly rejects some candidates)
- BL-006 (scoring — incorrectly scores key similarity)
- BL-011 (controllability evaluation — baseline may rest on incorrect key-distance logic)

**Current Mitigation (Weak):**
- The `circular` flag exists but is not implemented.
- No warning is emitted.

**Suggested Mitigation:**
1. **Implement circular distance:** In both BL-005 and BL-006, when computing key distance, use circular distance:
   ```python
   def circular_distance(a, b, max_val=12):
       return min(abs(a - b), max_val - abs(a - b))
   ```
2. **Apply to key feature only:** Wrap the comparison logic to apply circular distance only when `circular=True` in the feature spec.
3. **Test coverage:** Add a unit test that verifies key 0 and key 11 have distance 1 (not 11).
4. **Regression check:** Re-run BL-005/BL-006 to verify outputs change as expected; update baseline if needed.

---

## HIGH-PRIORITY ISSUES

### HIGH-001: BL-004 Profile Construction Non-Determinism Under Influence Tracks

**Description:**
From [build_bl004_preference_profile.py](build_bl004_preference_profile.py#L1), influence tracks are weighted separately:

```json
"influence_tracks": {
    "enabled": true,
    "track_ids": [],
    "preference_weight": 1.0,  // Single weight for all influence tracks
    "source": null
}
```

However, the current implementation **aggregates all influence tracks into a single weighted pool** without distinguishing individual influence tracks. If two influence tracks have the same track ID, or if the same track appears in both history and influence lists, **the weighting behavior is undefined**.

**Issue:**
1. **Ambiguous semantics:** Is `preference_weight` an absolute weight, a scaling factor, or something else?
2. **Potential double-counting:** If a track exists in both the history and influence inputs, it could be counted twice with different weights.
3. **Non-deterministic aggregation:** Under certain edge cases (e.g., duplicate influence tracks), the weighted sum could vary depending on list-processing order.

**Impact/Risk:**
- **Profile instability:** Small changes in influence track input can produce non-deterministic profile deltas.
- **Controllability evaluation risk:** BL-011 tests assume influence tracks produce causal, predictable profile changes, but the aggregation logic may break this assumption.
- **Thesis claim risk:** "Influence tracks allow controllable steering" assumes deterministic behavior.

**Affected Components:**
- BL-004 (preference profile construction)
- BL-011 (controllability evaluation — one scenario tests influence track steering)

**Current Mitigation (Weak):**
- The influence_weight is logged in BL-009 observability outputs.
- **Issue:** Non-determinism is not detected or warned.

**Suggested Mitigation:**
1. **Clarify semantics:** In run_config_utils.py, document exactly how influence_tracks.preference_weight is applied (absolute weight, scaling factor, etc.).
2. **De-duplication:** In BL-004, before aggregating influence tracks, de-duplicate by track ID. If a track appears multiple times, raise an error or combine weights explicitly.
3. **Mutual exclusion check:** If a track exists in both history and influence lists, either reject the config or apply a clear, documented weighting scheme.
4. **Test coverage:** Add a test case in BL-011 with duplicate influence tracks to verify determinism.

---

### HIGH-002: Candidate Filtering Decision Paths Are Incompletely Audited

**Description:**
From [build_bl005_candidate_filter.py](build_bl005_candidate_filter.py#L1), candidates are filtered via:
1. Semantic scoring (tag/genre overlap)
2. Numeric proximity gating (tempo, key, duration, etc.)

The decisions are traced in `bl005_candidate_decisions.csv` with columns:
- `track_id`
- `semantic_score`
- `decision` (keep/reject)
- `decision_reason`

However, the `decision_reason` field is **coarse and doesn't distinguish sub-cases within rejection reasons**. Examples:
- A track rejected for "insufficient numeric support" — but which numeric dimension(s) failed? (tempo? duration? key?)
- A track kept for "strong semantic match" — but which semantic dimensions contributed? (tags? genres? both?)

**Issue:**
1. **Incomplete diagnosticity:** Operators and evaluators cannot tell which specific feature(s) caused rejection.
2. **Hard to debug:** If candidate filtering is too strict or too lenient, it's unclear which thresholds to adjust.
3. **Observability gap:** BL-009 logs aggregate decision counts but not detailed dimensional breakdowns.

**Impact/Risk:**
- **Controllability opacity:** When tuning retrieval control parameters, it's unclear which dimension to adjust.
- **Thesis evaluation risk:** Cannot fully justify why certain candidates were rejected in Chapter 4.

**Affected Components:**
- BL-005 (candidate filtering)
- BL-009 (observability — should log dimensional breakdowns)
- BL-011 (controllability — tests assume clear cause-effect relationships)

**Current Mitigation (Weak):**
- `bl005_candidate_diagnostics.json` logs aggregate counts by decision path (e.g., `keep_strong_semantic`, `reject_numeric_without_semantic_support`).
- **Issue:** Diagnostics do not drill down to dimension level.

**Suggested Mitigation:**
1. **Expand decision trace:** Add optional columns to `bl005_candidate_decisions.csv`:
   - `semantic_dimensions_matched` (e.g., "tags:6, genres:3, lead_genre:1")
   - `numeric_dimensions_failed` (e.g., "tempo, duration")
   - `numeric_dimensions_passed` (e.g., "key, mode")
2. **Detailed diagnostics:** In `bl005_candidate_diagnostics.json`, add per-dimension rejection counts.
3. **Controllability mapping:** In BL-011, add a scenario that varies individual dimension thresholds to show cause-effect.

---

### HIGH-003: BL-007 Assembly Rules May Produce Empty or Undersized Playlists

**Description:**
From [build_bl007_playlist.py](build_bl007_playlist.py#L1), playlist assembly applies rules in order:
1. **R1:** Skip candidates below `min_score_threshold`
2. **R2:** Skip if lead genre has filled `max_per_genre` quota
3. **R3:** Skip if last `max_consecutive` tracks share same genre
4. **R4:** Stop when playlist reaches `target_size`

Default config:
```json
"assembly_controls": {
    "target_size": 10,
    "min_score_threshold": 0.35,
    "max_per_genre": 4,
    "max_consecutive": 2
}
```

**Issue:**
If the scored candidate pool is small (e.g., <10 candidates from BL-006) **and** the rules are strict, the pipeline **may fail to generate a full-sized playlist** without error:

Example:
- BL-006 produces only 8 scored candidates.
- All 8 have `final_score` ≥ 0.35.
- All 8 belong to the same genre.
- After applying R2 (max 4 per genre), only 4 candidates are eligible.
- Assembly produces a 4-track playlist instead of the requested 10.

**No error is raised.** The observability log will show `playlist_length=4` (below target), but there's no warning or failure signal to alert the operator.

**Impact/Risk:**
- **Silent output degradation:** Evaluation runs may produce undersized playlists without detection.
- **Thesis claim risk:** Claims about "10-track playlists" in Chapter 4 may rest on some runs with fewer tracks.
- **Reproducibility confusion:** Baseline playlists may be 10 tracks, but variations with different parameters yield 5–8 tracks, appearing to show a control effect when the actual cause is insufficient candidate pool.

**Affected Components:**
- BL-005 (candidate filtering — affects pool size)
- BL-006 (scoring — affects how many candidates survive `min_score_threshold`)
- BL-007 (assembly — rules may further reduce eligible set)
- BL-008 (transparency — explanations for <10 tracks are incomplete)
- BL-009 (observability — should warn if playlist is undersized)
- BL-011 (controllability — tests assume consistent playlist sizes)

**Current Mitigation (Weak):**
- BL-009 logs `playlist_track_count` alongside `target_size`.
- BL-014 sanity checks verify that `bl007_playlist.playlist_length` matches the count of tracks in `bl007_playlist.tracks`.
- **Issue:** No validation that `playlist_length >= target_size` or warning if not.

**Suggested Mitigation:**
1. **Enforce target size:** In BL-007, after assembly, check if `playlist_length < target_size`. If so, either:
     a. Fail with an error suggesting to adjust thresholds, OR
     b. Emit a critical warning and log the reason (pool too small, genre cap too tight, etc.).
2. **Diagnostic enhancement:** In `bl007_assembly_report.json`, add a field `target_underdelivery_reason` explaining why the playlist is short.
3. **Constraint relaxation:** Add a fallback rule in assembly: if playlist drops below a minimum size (e.g., 5 tracks), relax one constraint (e.g., increase `max_per_genre`) and re-attempt.
4. **Thesis transparency:** In Chapter 4, explicitly state the minimum and target playlist sizes for all runs, with note on underdelivery events.

---

### HIGH-004: Run-Config Validation Does Not Check Profile Control Consistency

**Description:**
The run-config schema defines:
- `profile_controls.top_tag_limit`
- `profile_controls.top_genre_limit`
- `profile_controls.top_lead_genre_limit`

And separately:
- `retrieval_controls.profile_top_tag_limit`
- `retrieval_controls.profile_top_genre_limit`
- `retrieval_controls.profile_top_lead_genre_limit`

These are used by BL-005 to select which profile dimensions are active for filtering.

**Issue:**
There is **no validation** that:
1. `retrieval_controls.profile_top_*_limit ≤ profile_controls.top_*_limit` (retrieval cannot use more profile dimensions than exist in the profile)
2. If `retrieval_controls.profile_top_tag_limit > 10` but `profile_controls.top_tag_limit = 5`, BL-005 will try to filter on 10 tags that don't exist in the profile, resulting in silent data misalignment.

**Impact/Risk:**
- **Silent data misalignment:** BL-005 may reference profile dimensions that were pruned in BL-004, producing undefined behavior (KeyErrors, empty match sets).
- **Reproducibility risk:** Configs that are accidentally misaligned produce invalid outputs without clear error messages.

**Affected Components:**
- BL-004 (profile construction)
- BL-005 (candidate filtering — assumes profile has requested dimensions)
- BL-013 (config validation)

**Current Mitigation (Weak):**
- **None explicitly.** Validation in `run_config_utils.py` does not check this coupling.

**Suggested Mitigation:**
1. **Add cross-config validation** in `resolve_effective_run_config()` after all sections are resolved:
     ```python
     if config["retrieval_controls"]["profile_top_tag_limit"] > config["profile_controls"]["top_tag_limit"]:
         raise RunConfigError("retrieval_controls.profile_top_tag_limit cannot exceed profile_controls.top_tag_limit")
     # (similar for genre and lead_genre)
     ```
2. **Emit warning if they differ:** Even if valid, log a notice that retrieval is using fewer profile dimensions than available.
3. **Test coverage:** Add a test case that intentionally violates this constraint and verify the error is raised.

---

### HIGH-005: Explanation Payloads May Mislead About Causality

**Description:**
From [build_bl008_explanation_payloads.py](build_bl008_explanation_payloads.py#L1), each track in the final playlist receives an explanation payload listing:
- `why_selected`: Human-readable narrative
- `top_score_contributors`: Top 3 components by weighted contribution
- `score_breakdown`: All component similarities and contributions

The payload generation reads `bl007_assembly_trace.csv` to identify which **rule** admitted the track (R1, R2, R3, R4, or admitted on first evaluation). However, **the score contributors in the explanation always reflect the component weights used in BL-006**, regardless of how the candidate was actually selected.

Example:
- A candidate is admitted because R1 (score threshold) is passed with a high tempo similarity and mediocre tag overlap.
- But BL-006's `component_weights` emphasize tag_overlap (0.16 vs tempo 0.20).
- The explanation payload lists "tag_overlap" as a top contributor, even though tempo was the actual reason for admission.

**Issue:**
1. **Misleading attribution:** Explanations suggest certain features caused selection, but the actual selection was driven by assembly rules, not scoring.
2. **Causal incoherence:** Users may assume "this track was selected because tag overlap is high," but the true cause is "the score happened to exceed the threshold."

**Impact/Risk:**
- **Transparency claim risk:** BL-008 explanations are presented as evidence of "transparency," but they may obscure true causality.
- **Thesis validity:** Claims in Chapter 4 about user understandability of explanations may not hold if explanations mislead.

**Affected Components:**
- BL-006 (scoring)
- BL-007 (assembly)
- BL-008 (transparency — explanations)
- BL-009 (observability — observability log should clarify this)

**Current Mitigation (Weak):**
- BL-008 does include `assembly_context` in each payload, indicating which rule admitted the track.
- **Issue:** The narrative explanation focuses on score contributors, not the actual rule that admitted the track.

**Suggested Mitigation:**
1. **Reframe explanation:** In `build_why_selected()`, prioritize the **assembly rule** that admitted the track, not just the score contributors:
     ```
     "Why Selected: Admitted by scoring rule [R1 or R3 or first-eval] because
      [specific dimensional match], with final score 0.XXX.
      Lead genre contribution: X, tag overlap: Y, ..."
     ```
2. **Conditional attribution:** Only list score contributors if they correlate with the rule that admitted the track.
3. **Transparency note:** Add a caveat in the explanation schema: "Score contributors above reflect the overall similarity across selected dimensions; the actual selection mechanism was the assembly rule."
4. **Thesis documentation:** In Chapter 4, clarify that explanations reflect post-hoc scoring analysis, not causal selection drivers.

---

### HIGH-006: Data Ingestion Does Not Validate Output Row Count Against Input

**Description:**
From [build_bl003_ds001_spotify_seed_table.py](build_bl003_ds001_spotify_seed_table.py#L1), the seed table is constructed by matching Spotify-imported tracks against the DS-001 corpus. The output seed table should be **a subset of matched input events**.

However, there is **no validation** that:
1. Output row count ≤ input event count
2. All output rows are present in the input event list
3. No duplicates were introduced during aggregation

**Impact/Risk:**
- **Silent data corruption:** If a bug in the matching or deduplication logic causes duplicate output rows or phantom rows, this would not be detected.
- **Reproducibility risk:** Subtle count mismatches across runs could indicate non-determinism.

**Affected Components:**
- BL-003 (seed construction)
- BL-004 (preference profile — ingests seed table)
- BL-009 (observability — should validate seed table integrity)
- BL-014 (sanity checks — should include seed table validation)

**Current Mitigation (Weak):**
- BL-003 summary logs `input_events`, `matched_count`, `unmatched_count`.
- **Issue:** No explicit validation that these numbers are consistent.

**Suggested Mitigation:**
1. **Add validation in BL-003:** After constructing the seed table, verify:
     ```python
     assert (seed_table_row_count + unmatched_count) == input_event_count
     assert all(output_row in input_events for output_row in seed_table)
     ```
2. **De-duplication check:** In seed table construction, explicitly de-duplicate by (ds001_id, spotify_id) and log any discards.
3. **BL-014 check:** Add a sanity check that validates seed table integrity:
     ```python
     check("bl003_seed_table_integrity",
           seed_table_count + unmatched_count == input_count,
           "BL-003 seed table row count consistency")
     ```

---

### HIGH-007: BL-003 Seed Freshness Guard Does Not Prevent Partial Config Changes

**Description:**
From [run_bl013_pipeline_entrypoint.py](run_bl013_pipeline_entrypoint.py#L1), the BL-003 freshness guard (`validate_bl003_seed_freshness()`) compares:
- **Expected contract** from the run-effective config
- **Observed contract** from the BL-003 summary

The check compares:
- `input_scope`
- `influence_tracks`

However, it **does not validate**:
- `top_time_ranges` array equality (only compares the entire object)
- Changes to individual array elements (e.g., if `top_time_ranges` is reordered but still includes same values)

**Issue:**
An operator could modify `top_time_ranges` from `["short_term", "medium_term", "long_term"]` to `["short_term", "medium_term"]` (omitting long_term), and the freshness guard would correctly reject this. However, if they reorder to `["medium_term", "short_term", "long_term"]`, the object comparison **may or may not catch it** depending on how the dictionaries are compared (order-sensitive or order-insensitive).

**Impact/Risk:**
- **Silent config drift:** If array ordering changes the semantics (unlikely but possible), this could be missed.
- **Assertion brittleness:** The compare logic depends on dictionary serialization order.

**Affected Components:**
- BL-003 (seed construction)
- BL-013 (orchestration — freshness validation)

**Current Mitigation (Weak):**
- The guard exists and is validated in UI-009.
- **Issue:** Edge cases around array equality are not explicitly handled.

**Suggested Mitigation:**
1. **Deep-dive comparison:** Replace dictionary equality with element-wise comparison for arrays:
     ```python
     if sorted(observed["input_scope"]["top_time_ranges"]) != sorted(expected["input_scope"]["top_time_ranges"]):
         return False, "top_time_ranges differ"
     ```
2. **Test coverage:** Add a test that reorders `top_time_ranges` and verify the freshness guard catches it.
3. **Explicit logging:** In the freshness check output, itemize which fields match/differ.

---

## MEDIUM-PRIORITY ISSUES

### MED-001: Missing Test Coverage for Edge-Case Dataset States

**Description:**
The pipeline has no test cases for:
- Empty preference profiles (no matched seeds)
- Candidates with all NaN/missing numeric features
- Profiles with only 1 top tag/genre (edge of discretion range)
- Run-configs with all controls set to minimum safe values

**Affected Components:** All stages (BL-004 through BL-009)

**Suggested Mitigation:**
Add synthetic test cases in BL-011 or a separate test module covering these edge states.

---

### MED-002: Observability Logs Not Validated for Required Fields

**Description:**
BL-009 constructs the observability log, but there is **no post-hoc validation** that all required sections and fields are present. BL-014 checks schema shape but not completeness within each section.

**Suggested Mitigation:**
In BL-014, add checks for required fields within each observability log section (e.g., `run_metadata.run_id`, `execution_scope_summary.history_track_count`, etc.).

---

### MED-003: Module Import Failures Not Caught Until Runtime

**Description:**
Several stage scripts dynamically load `run_config_utils.py` via `importlib.util.spec_from_file_location()`. If the module path is incorrect or the file is corrupted, the error occurs **mid-execution**, not at startup.

**Suggested Mitigation:**
In BL-013, validate that all required stage modules exist and are importable before launching any stages.

---

### MED-004: Genre Cap Rule in BL-007 Does Not Account for Mixed Genres

**Description:**
The `max_per_genre` rule in assembly limits tracks per **lead genre only**. However, tracks often have multiple genres. Two tracks could have different lead genres but overlapping secondary genres, potentially reducing diversity while appearing compliant.

**Suggested Mitigation:**
Document this limitation in Chapter 4. Optionally, add a secondary rule that limits tracks with overlapping genre sets, not just lead genre.

---

## LOW-PRIORITY ISSUES

### LOW-001: Logging Format Inconsistency Across Stages

**Description:**
Different stages use slightly different JSON formatting (indentation, key ordering, precision for floats). This makes reading logs tedious and introduces micro-diffs when comparing runs.

**Suggested Mitigation:**
Standardize JSON output format across all stages (e.g., 2-space indentation, sorted keys, consistent float precision).

---

### LOW-002: No Explicit Versioning for Data Layer Artifacts

**Description:**
DS-001 working dataset (`ds001_working_candidate_dataset.csv`) is regenerated periodically but has no versioning or changelog. If the source files change, there's no record of which version was used in which run.

**Suggested Mitigation:**
Add a version field to the DS-001 dataset manifest and link run artifacts to the dataset version used.

---

### LOW-003: Run-Config Default Values Not Validated Against Bounds

**Description:**
`DEFAULT_RUN_CONFIG` in `run_config_utils.py` is not validated. If a developer mistakenly edits defaults to invalid values (e.g., `target_size: -5`), the error appears only when a run is executed.

**Suggested Mitigation:**
Add a validation pass at module load time that checks all defaults against constraints.

---

## ARCHITECTURAL GAPS

### GAP-001: No Explicit Saga or Transaction Management

**Description:**
The pipeline has no mechanism to roll back partial runs or recover from mid-stream failures. If BL-006 crashes after BL-005 completes, the outputs are inconsistent but not rolled back.

**Suggested Mitigation:**
Document expected failure recovery (manual cleanup of outputs, re-run from scratch). Consider adding a run-state ledger to track partial completions.

---

### GAP-002: No Built-In Alerting or Metrics Thresholds

**Description:**
The pipeline does not alert on concerning metrics (e.g., unmatched track rate >50%, playlist undersized, zero candidates post-filtering). Operators must manually inspect logs.

**Suggested Mitigation:**
In BL-009, log explicit metrics with severity levels (OK, WARNING, ERROR) and define thresholds. Emit summary report highlighting warnings.

---

## GOVERNANCE & CONTROL SURFACE GAPS

### GOV-001: No Formal Change Control for Run-Config Schema

**Description:**
The run-config schema (run-config-v1) is defined in code, not in a separate schema file. If the schema changes, there's no versioning or migration path for old configs.

**Suggested Mitigation:**
Define a formal JSON Schema document for `run-config-v1` and maintain a schema changelog. When schema changes (e.g., add a field), bump version to `run-config-v2` and implement a migration function.

---

### GOV-002: Influence Tracks Control Has Unclear Semantics

**Description:**
The `influence_tracks.preference_weight` field is documented but its exact behavior (absolute weight, scaling factor, base-weight boost) is ambiguous. Different evaluators might interpret it differently.

**Suggested Mitigation:**
Add a detailed semantic explanation in `semantic_control_map.md` with mathematical formula and examples.

---

## OBSERVABILITY BLIND SPOTS

### OBS-001: No Structured Logging of Intermediate Processing Details

**Description:**
BL-009 logs stage-level summaries but not intermediate processing details (e.g., per-stage runtime, memory usage, I/O patterns). This makes performance debugging hard.

**Suggested Mitigation:**
Add optional detailed logging in each stage, controlled by a `--verbose` flag or environment variable. Include stage runtime, row counts at each step, and exception handling details.

---

### OBS-002: Determinism Validation Not Automated

**Description:**
BL-010 manually replays runs 3 times to check determinism. There's no automated check that production runs are deterministic en masse.

**Suggested Mitigation:**
Add a flag to BL-013 (`--verify-determinism`) that runs the pipeline twice and compares output hashes, failing if they differ.

---

## SUMMARY TABLE

| Issue ID | Severity | Category | Status | Mitigation Effort |
|---|---|---|---|---|
| CRI-001 | **CRITICAL** | Data Integrity | Open | Medium |
| CRI-002 | **CRITICAL** | Validation Gap | Open | High |
| CRI-003 | **CRITICAL** | Error Handling | Open | Medium |
| CRI-004 | **CRITICAL** | Validation Gap | Open | Low |
| CRI-005 | **CRITICAL** | Logic Bug | Open | High |
| HIGH-001 | **HIGH** | Semantics | Open | High |
| HIGH-002 | **HIGH** | Observability | Open | Medium |
| HIGH-003 | **HIGH** | Edge Case | Open | Medium |
| HIGH-004 | **HIGH** | Validation Gap | Open | Low |
| HIGH-005 | **HIGH** | User Facing | Open | Medium |
| HIGH-006 | **HIGH** | Data Integrity | Open | Low |
| HIGH-007 | **HIGH** | Control Surface | Open | Low |
| MED-001 | Medium | Testing | Open | Low |
| MED-002 | Medium | Observability | Open | Low |
| MED-003 | Medium | Error Handling | Open | Low |
| MED-004 | Medium | Design | Open | Low |
| LOW-001 | Low | Code Quality | Open | Low |
| LOW-002 | Low | Maintenance | Open | Low |
| LOW-003 | Low | Configuration | Open | Low |
| GAP-001 | **HIGH** | Architecture | Open | High |
| GAP-002 | **HIGH** | Observability | Open | Medium |
| GOV-001 | **HIGH** | Governance | Open | Medium |
| GOV-002 | **HIGH** | Documentation | Open | Low |
| OBS-001 | Medium | Observability | Open | Medium |
| OBS-002 | Medium | Testing | Open | Low |

---

## RECOMMENDATIONS FOR IMMEDIATE ACTION (Before Submission Hardening)

1. **Address CRI-001 (Unmatched Track Bias):** Define minimum match-rate threshold and document assumption in Chapter 3.
2. **Address CRI-002 (Numeric Threshold Mismatch):** Implement validation in run_config_utils.py to prevent drift.
3. **Address CRI-004 (Invalid Thresholds):** Add positive-value validation for all numeric thresholds.
4. **Address CRI-005 (Circular Key Distance):** Implement circular distance for key feature in BL-005 and BL-006.
5. **Address HIGH-003 (Undersized Playlists):** Add warning/error if playlist falls below target size; document in Chapter 4.
6. **Address GOV-001 (Schema Versioning):** Create formal JSON Schema document for run-config-v1.

---

**Document prepared:** 2026-03-25T00:00:00Z
**Review status:** Ready for author review
**Next Steps:** Prioritize and assign mitigation tasks to backlog
