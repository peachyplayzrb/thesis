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
| assembly_rules (hardcoded) | BL-007 | Playlist structure | Genre cap, length, diversity | ❌ RIGID | HIGH |
| input_scope (sources) | BL-003 config | Profile input | Which Spotify sources included | ✓ WORKS | LOW |

## Impact Assessment

### WEAK Controls (Planned Redesign)
**Influence Tracks**
- Current: Added to seed table, merged into profile aggregation
- Problem: BL-011 testing shows ZERO playlist impact despite being enabled
- Reason: Profile shift too small to affect downstream filtering/scoring
- User expectation mismatch: "I selected these tracks" vs. "maybe they'll affect something"
- Redesign: Post-profile direct insertion with guaranteed playlist slots
- Timeline: Phase 2

**Assembly Rules**
- Current: Hard-coded R1-R4 (threshold, genre cap, consecutive, length)
- Problem: User cannot modify without config change
- Redesign: Expose as user-tunable parameters in run_config
- Timeline: Phase 3

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

## Planned Additions (Phase 4)

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
- [ ] Redesign influence_tracks (HIGH priority)
- [ ] Expose assembly_rules as user config (HIGH priority)  
- [ ] Add control-effect validation to orchestration (MEDIUM priority)
- [ ] Implement planned controls (Phase 4, BACKLOG)
