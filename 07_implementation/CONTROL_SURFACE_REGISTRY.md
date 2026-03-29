# Control Surface Registry

## Purpose
Audit all user-facing controls, their measurability, and implementation quality.
Thesis requirement: Each control must have measurable downstream effect.

## Current Control Surfaces

| Control | Location | Type | Effect | Status | Priority |
|---------|----------|------|--------|--------|----------|
| influence_tracks | BL-003 | Pre-profile | Profile shift (indirect) | ❌ WEAK | HIGH |
| feature_weights (scoring) | BL-006 config | Score input | Component emphasis in scoring | ✓ WORKS | MEDIUM |
| numeric_thresholds | BL-005/006 config | Filter/score | Candidate pool size change | ✓ WORKS | MEDIUM |
| assembly_rules (partially configurable) | BL-007 | Playlist structure | Genre cap, length, diversity, utility selection | ⚠️ PARTIAL | MEDIUM |
| input_scope (sources) | BL-003 config | Profile input | Which Spotify sources included | ✓ WORKS | LOW |

## Impact Assessment

### WEAK Controls (Known Limitation)
**Influence Tracks**
- Current: Added to seed table, merged into profile aggregation
- Problem: BL-011 testing shows ZERO playlist impact despite being enabled
- Reason: Profile shift too small to affect downstream filtering/scoring
- User expectation mismatch: "I selected these tracks" vs. "maybe they'll affect something"
- Scope position: documented limitation in current implementation scope

### PARTIAL Controls (Implemented with Fixed Residuals)
**Assembly Rules**
- Current: Rule thresholds/limits are configurable via BL-007 runtime controls (`target_size`, `min_score_threshold`, `max_per_genre`, `max_consecutive`)
- Also configurable: utility strategy/weights, adaptive limits, controlled relaxation, and diagnostics toggles
- Fixed residuals: rule order (R1 to R4) and some helper heuristics in rules/reporting remain hardcoded
- Scope position: current implementation is tunable but not fully policy-configurable

### WORKING Controls (Well-Designed)
**Feature Weights**
- User sets: component_weights in scoring_controls
- Effect: Changes score composition (e.g., prefer danceability over energy)
- Measurable: Final scores differ, candidate ranks shift
- Status: Good

**Numeric Thresholds**
- User sets: distance tolerances in retrieval/scoring
- Effect: Candidate pool size contracts/expands
- Measurable: BL-005 reports filtered candidate count
- Status: Good

## Future Work (Out of Current Scope)

| Control | Type | Purpose |
|---------|------|---------|
| playlist_influence_slots | BL-007 | How many slots reserved for influence tracks (0-10) |
| genre_diversity_strictness | BL-007 | How aggressively to enforce genre balance |
| consecutive_run_limit | BL-007 | Max consecutive same-genre tracks |
| score_threshold_override | BL-007 | Per-genre score floor overrides |

## Validation Requirements
- BL-010/BL-011 must verify each control actually produces observable output changes
- Fail pipeline if control has zero measurable effect
- Document effect size and direction

## Next Steps
- [ ] Keep influence_tracks limitation explicit in evaluation and chapter claims
- [ ] Preserve BL-007 partial-tunability wording consistently across governance/design docs
- [ ] Add control-effect validation to orchestration (MEDIUM priority)
- [ ] Revisit Future Work controls only if scope expands beyond current thesis implementation
