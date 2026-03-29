# Transparency Design Addendum

## Purpose
Extend `05_design/transparency_design.md` with current implementation patterns and identified transparency gaps.

## Current Transparency Architecture

### What is Well-Designed
**BL-008 Explanation Payloads** ✅
- Per-track explanations with score breakdown
- Shows: top contributors, component similarities, weighted contributions
- Format: Human-readable ("why_selected") + machine-structured (contributor data)
- Coverage: Every track in final playlist explained
- Status: Strong transparency of scoring decisions

**BL-009 Observability** ✅
- Comprehensive run logs documenting all stages
- Captures: config source, artifact hashes, diagnostics, exclusion samples
- Traceable: Full pipeline decisions logged
- Status: Strong operational transparency

**BL-010 Reproducibility** ✅
- Validates deterministic behavior
- Checks: Same input → same output across runs
- Ensures: Decisions are traceable and repeatable
- Status: Strong reproducibility verification

### Transparency Gaps (Identified)

**Gap 1: Control Application Traceability** ❌
- Current: Explanations don't show HOW user controls shaped outcome
- Missing: "This track was selected because YOUR genre preference drove the score"
- Missing: "This track would NOT make the playlist if you used stricter numeric thresholds"
- Impact: User cannot see connection between their control choices and outcomes

**Gap 2: Influence Control Transparency** ❌
- Current: Influence seeds are hidden in profile aggregation
- Gap: No explanation of which seeds came from influence_tracks vs. listening history
- Gap: No measurement of influence track effect on profile or playlist
- Impact: User cannot see if their influence selections matter

**Gap 3: Assembly Rule Transparency** ❌
- Current: BL-007 trace shows rule hits (R1-R4) but not configuration
- Gap: No explanation of rule parameter values that led to exclusion
- Missing: "Max per genre was set to 2, rejected 8 additional pop candidates"
- Impact: User cannot understand why different playlists result from config changes

**Gap 4: Candidate Filtering Rationale** ⚠️
- Current: BL-005 shows decision (pass/fail) but minimal context
- Gap: Doesn't explain WHICH thresholds caused rejection
- Gap: No summary of threshold impacts (e.g., "danceability threshold rejected 200 candidates")
- Impact: User cannot debug filtering behavior

**Gap 5: Counterfactual Reasoning** ❌
- Current: No what-if analysis
- Missing: "If you used looser thresholds, 50 more candidates would pass"
- Missing: "If you disabled language filter, 150 candidates would be added to pool"
- Impact: User cannot predict outcomes of control changes

## Transparency Requirements (Thesis Core)

From thesis problem statement:
> "Recommendation outputs are produced by complex model pipelines where the contribution of individual factors is not easily visible, and where small configuration or data changes can alter outcomes without clear traceability."

**Thesis expectation**: This system MUST be transparent about:
1. What decisions were made ✅ (BL-007 trace, BL-008 explanations)
2. Why decisions were made (partially addressed—score components shown, but not control application)
3. How control changes would affect outcomes ❌ (not implemented)
4. What uncertainty or alternatives exist ⚠️ (limited)

## Planned Transparency Enhancements

### T1: Control Application Tracing
Add to every explanation:
```json
{
  "track_explanation": {
    "why_selected": "...",
    "user_controls_that_enabled_this": {
      "genre_filter_sources": ["your top 3 genres"],
      "numeric_thresholds": ["passed danceability window"],
      "assembly_rules": ["passed score threshold rule (R1)"]
    }
  }
}
```

### T2: Influence Track Transparency
Add to BL-004 profile and BL-008 explanations:
```json
{
  "seed_source_breakdown": {
    "history_seeds": 1062,
    "history_seed_weight": 1062.3,
    "influence_seeds": 2,
    "influence_seed_weight": 2.0,
    "influence_seeds_list": ["track_1", "track_2"]
  }
}
```

### T3: Assembly Rule Transparency
Add to BL-007 trace:
```json
{
  "rule_application_context": {
    "r2_genre_cap": 2,
    "r2_rejections_due_to_genre_cap": 45,
    "r3_consecutive_limit": 1,
    "r3_rejections_due_to_consecutive": 12,
    "r4_target_size": 10,
    "r4_stop_reached_after": 10
  }
}
```

### T4: Candidate Filtering Rationale
Add to BL-005 summary:
```json
{
  "numeric_threshold_impact": {
    "danceability_distance_0_25": {"candidates_rejected": 2000, "reason": "outside window"},
    "energy_distance_0_3": {"candidates_rejected": 1500, "reason": "outside window"},
    "combined_numeric_passes": 46776
  },
  "semantic_filter_impact": {
    "language_filter": {"enabled": true, "candidates_rejected": 500},
    "genre_overlap_minimum": {"required": 1, "candidates_rejected": 250}
  }
}
```

### T5: Counterfactual Analysis
Add to observability and explanations:
```json
{
  "what_if_scenarios": [
    {"scenario": "if_no_influence_tracks", "expected_playlist_change": "0% (none selected)"},
    {"scenario": "if_looser_numeric_thresholds", "expected_candidate_pool": "60000 (vs 46776)"},
    {"scenario": "if_stricter_genre_cap", "expected_genre_diversity": "less mixed, more homogeneous"}
  ]
}
```

## Transparency Design Principles

1. **Control Traceability**: Every decision must be traceable to explicit user control or system rule ← Gap: Not implemented
2. **Counterfactual Clarity**: User can predict what would happen with different controls ← Gap: Not implemented
3. **Ranking Justification**: Why is Track A #2 and Track B #8? ✅ (BL-008 shows scoring)
4. **Rejection Rationale**: Why was Candidate X rejected? ⚠️ (Partial—shows fail, not which threshold)
5. **Configuration Impact**: How did my control choices affect the outcome? ❌ (Not traced)

## Next Steps (Phase 2-3)
- [ ] Design control traceability data flow
- [ ] Add influence seed source tracking to BL-004
- [ ] Document assembly rule context in BL-007
- [ ] Create what-if analysis layer
- [ ] Update transparency outputs to include control application
