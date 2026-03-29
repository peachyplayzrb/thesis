# Control Testing Protocol

## Purpose
Define repeatable procedure for validating that controls work as intended and produce measurable effect on playlist outcomes.

## Prerequisite: BL-011 Controllability Testing

Every control must be validated through BL-011 (or equivalent) controllability test where:
- **Baseline run**: Execute pipeline with control at default value
- **Treatment run**: Execute pipeline with control value changed (per test design)
- **Measurement**: Compare outputs for measurable difference
- **Success criterion**: Measurable effect observed, documented, and size quantified

## Control-Effect Measurement Framework

### Effect Size Categories

**Large Effect** (≥10% change):
- Examples: Input scope changes (different sources), extreme threshold changes
- Confidence: High—control is working
- Action: Document in REGISTRY with effect size

**Medium Effect** (1-10% change):
- Examples: Feature weight adjustments, moderate threshold changes
- Confidence: Good—control is working but subtle
- Action: Document in REGISTRY, may need multiple runs for confidence

**Small Effect** (<1% change):
- Examples: Minor weight tweaks, small threshold adjustments
- Confidence: Uncertain—may be noise or real subtle effect
- Action: Run multiple times, aggregate results, document uncertainty

**Zero Effect** (no detectable change, ±0%):
- Examples: Current influence_tracks behavior (top10_overlap=1.0, rank_delta=0.0)
- Confidence: Critical failure
- Action: 🛑 ESCALATE—control is not working, requires redesign (see GOVERNANCE.md gate Q3)

### Measurement Methods

**Method 1: Playlist Composition Change** ✅ STANDARD
- Metric: % of tracks different between baseline and treatment playlist
- Threshold: ≥1% counts as "measurable effect"
- How to measure:
  ```
  baseline_set = set(baseline_playlist.track_ids)
  treatment_set = set(treatment_playlist.track_ids)
  overlap = len(baseline_set & treatment_set)
  diff_percentage = 100 * (1 - overlap / len(baseline_set))
  ```
- Example: 8/10 tracks overlap → 20% change (LARGE effect)

**Method 2: Rank Changes** ✅ STANDARD
- Metric: Mean absolute rank difference for overlapping tracks
- Threshold: ≥0.5 rank positions counts as "measurable effect"
- How to measure:
  ```
  for each track in both playlists:
    rank_delta = abs(baseline_rank[track] - treatment_rank[track])
  mean_abs_rank_delta = mean(rank_deltas)
  ```
- Example: mean rank delta = 1.5 positions (MEDIUM effect)

**Method 3: Candidate Pool Size** ✅ STANDARD (for retrieval controls)
- Metric: % change in candidates passing filter
- Threshold: ≥1% change counts as "measurable effect"
- How to measure:
  ```
  baseline_pool_size = len(baseline_candidates_passed)
  treatment_pool_size = len(treatment_candidates_passed)
  pct_change = 100 * abs(treatment_pool_size - baseline_pool_size) / baseline_pool_size
  ```
- Example: 50,000 → 45,000 candidates (10% reduction = LARGE effect)

**Method 4: Score Distribution** ✅ (for scoring/weighting controls)
- Metric: KL divergence or Wasserstein distance between score distributions
- Threshold: Divergence >0.1 counts as "measurable effect"
- How to measure:
  ```
  baseline_scores = [track.score for track in baseline_scored_candidates]
  treatment_scores = [track.score for track in treatment_scored_candidates]
  kl_div = entropy(baseline_scores) - entropy(treatment_scores)
  or
  wasserstein_dist = scipy.stats.wasserstein_distance(baseline_scores, treatment_scores)
  ```
- Example: KL divergence = 0.4 (MEDIUM effect)

## Test Scenario Templates

### Scenario T1: Feature Weight Impact
**Control**: Adjust one component weight (e.g., danceability) by ±50%

**Test design**:
```json
{
  "baseline_config": {"danceability_weight": 1.0, "...other_weights": "unchanged"},
  "treatment_config": {"danceability_weight": 1.5, "...other_weights": "unchanged"},
  "expectation": "Scoring should favor more danceable candidates; likely rank changes",
  "measurement_method": "Method 2 (rank changes)",
  "success_threshold": "mean_abs_rank_delta ≥ 0.5"
}
```

### Scenario T2: Numeric Threshold Impact
**Control**: Make thresholds stricter (narrower window)

**Test design**:
```json
{
  "baseline_config": {"danceability_distance": 0.3, "energy_distance": 0.3},
  "treatment_config": {"danceability_distance": 0.15, "energy_distance": 0.15},
  "expectation": "Candidate pool should shrink; fewer tracks pass filter",
  "measurement_method": "Method 3 (candidate pool size)",
  "success_threshold": "pct_change ≥ 5%"
}
```

### Scenario T3: Input Scope Impact
**Control**: Disable one Spotify source (e.g., playlists)

**Test design**:
```json
{
  "baseline_config": {"input_scope": ["top_tracks", "saved_tracks", "playlists", "recently_played"]},
  "treatment_config": {"input_scope": ["top_tracks", "saved_tracks", "recently_played"]},
  "expectation": "Profile should shift; seeds come from fewer sources",
  "measurement_method": "Method 1 (playlist composition) + examine seed source in profile artifact",
  "success_threshold": "≥10% playlist difference OR observable seed composition change"
}
```

### Scenario T4: Influence Tracks Impact (Current Weak Control)
**Control**: Add influence tracks to configuration

**Test design**:
```json
{
  "baseline_config": {"influence_tracks": {"enabled": false}},
  "treatment_config": {"influence_tracks": {"enabled": true, "track_ids": ["spotify:track:XXX", "spotify:track:YYY"]}},
  "expectation": "With current pre-profile design, effect is expected to be weak or zero",
  "measurement_method": "Method 1 (playlist composition) + check if influence tracks appear in playlist",
  "success_threshold": "Currently FAILS: mean_rank_delta ≈ 0.0, composition_overlap ≈ 100%",
  "note": "Known limitation; needs post-profile redesign (D-042)"
}
```

## Test Execution Checklist

- [ ] Choose control to test
- [ ] Define baseline config (default or specified)
- [ ] Define treatment config (single control perturbed)
- [ ] Confirm both run with SUCCESS status (no errors)
- [ ] Align or fresh-ingress data if needed
- [ ] Run BL-002 through BL-009 for both configs
- [ ] Generate artifacts (bl003, bl004, bl005, bl006, bl007, bl008, bl009)
- [ ] Run BL-010 to verify reproducibility (same config → same output)
- [ ] Compare using measurement method(s)
- [ ] Record effect size in CONTROL_SURFACE_REGISTRY.md
- [ ] If zero effect: escalate to GOVERNANCE.md, add to RESEARCH_DIRECTIONS.md
- [ ] If measurable effect: document in decision_log.md if significant finding

## Documentation Template

When documenting test results in CONTROL_SURFACE_REGISTRY.md:

```markdown
### [Control Name] — Test Result T-[Date]
- **Baseline config**: [...]
- **Treatment config**: [...]
- **Effect measured**: [which method?]
- **Effect size**: [quantitative result]
- **Conclusion**: [STRONG/MEDIUM/WEAK/ZERO effect]
- **Impact on thesis**: [does this support controllability/transparency goal?]
```

## When to Escalate

🛑 **Escalate if**:
- Control shows zero effect (add to RESEARCH_DIRECTIONS.md RQ-series)
- Effect is opposite of expected direction
- Effect size is inconsistent across runs (noise/instability)
- New control doesn't fit existing measurement methods

✅ **Proceed normally if**:
- Measurable effect observed
- Effect direction matches expectation
- Effect size is consistent and documentable

## Frequency & Ownership

- **When**: After every BL-011 run, before merging code changes
- **Who**: Implementation owner (running control changes) + optionally mentor review
- **Where**: Results documented in CONTROL_SURFACE_REGISTRY.md (cumulative record)
- **Tracking**: Decision_log.md references test result if decision is made
