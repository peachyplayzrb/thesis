# Controllability Design Addendum

## Purpose
Extend `05_design/controllability_design.md` with current implementation findings and measured effectiveness.

## Current Control Surfaces (Status Update)

### Working Controls
**Feature Weights** ✅
- User sets: `scoring_controls.component_weights`
- Current components: 10 active (7 numeric + 3 semantic)
- Effect: Measured in BL-006 score distribution
- Measurability: High—different weights produce different scores
- Status: Well-designed, functioning as intended

**Numeric Thresholds** ✅
- User sets: `retrieval_controls.numeric_thresholds`
- Effect: Measurable candidate pool size changes
- Evidence: BL-005 filters 109k → 46k based on thresholds
- Status: Working as per design

**Input Scope** ✅
- User sets: Which Spotify sources to include (top tracks, saved, playlists, recently played)
- Effect: Observable in BL-003 alignment source stats
- Status: Working

### Weak Controls (Requiring Redesign)
**Influence Tracks** ❌ WEAK
- **Current Design**: Pre-profile injection (BL-003 alignment)
- **Measurement**: BL-011 controllability test shows ZERO playlist effect
  - Test: Enabled vs. disabled influence tracks
  - Result: `top10_overlap_ratio=1.0`, `mean_abs_rank_delta=0.0`
- **Problem**: Indirect effect through profile aggregation is too probabilistic
- **User Expectation Gap**: "I selected these 5 tracks" → user expects them in playlist or measurable impact
- **Current Reality**: Seeds merge into profile, profile shift too small to affect filtering/scoring
- **Design Gap**: No guarantee of inclusion, no measurable effect in current setup
- **Redesign Direction**: Move to post-profile direct insertion with guaranteed playlist slots

**Assembly Rules** ❌ RIGID
- **Current Design**: Hard-coded R1-R4 rules in BL-007
  - R1: Score threshold
  - R2: Genre cap per playlist
  - R3: Consecutive-same-genre limit
  - R4: Target length cap
- **Problem**: User cannot adjust without code changes or config system redesign
- **Control Gap**: These are major diversity/coherence levers but are not user-tunable
- **Redesign Direction**: Expose as configuration in run_config

## Design Principles (from Thesis)
1. Controls must be semantically clear and documented ✅
2. Controls must be bounded to prevent unstable behavior ✅
3. **Control location in pipeline must be explicit** — Gap: influence tracks location is implicit/indirect
4. Control values must be persisted in run configuration ✅
5. **Each control should map to at least one measurable output effect** — Gap: influence_tracks has zero measured effect

## Measured Control Effectiveness

| Control | Measurable Effect | Effect Size | Interpretability | Stability |
|---------|-------------------|-------------|------------------|-----------|
| feature_weights | Scoring composition | High | Excellent | Good |
| numeric_thresholds | Candidate pool size | High | Excellent | Good |
| input_scope | Profile composition | Medium | Good | Good |
| influence_tracks | (Zero) | None measured | N/A | N/A |
| assembly_rules | (Not tunable) | N/A | N/A | N/A |

## Open Design Questions

1. **Influence slots policy**: Should influence tracks override genre caps and diversity rules?
   - Current: No (they're just seeds that may or may not make it through)
   - Proposed: Yes (user explicit intent overrides system rules)

2. **Assembly rule exposure scope**: Start with all 4 rules or subset?
   - Proposed: Start with target_size, max_per_genre, max_consecutive
   - Add others in Phase 4 if needed

3. **Control-effect validation**: Should pipeline FAIL if control has observed zero effect?
   - Proposed: YES (strong signal that something is broken)
   - Alternative: Warn only, allow manual investigation

## Next Steps (Phase 2-3)
- [ ] Design post-profile influence slot reservation logic
- [ ] Document influence slot policy decisions
- [ ] Design assembly rules exposure in run_config
- [ ] Create control-effect validation layer
- [ ] Document findings in CONTROL_SURFACE_REGISTRY.md
