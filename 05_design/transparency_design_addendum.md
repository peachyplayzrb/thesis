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
- Current: BL-007 report includes effective configuration plus rule hits (R1-R4)
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

## Known Limitations (Current Implementation)

1. Control-causality is not emitted as a unified per-track block linking user controls to final inclusion.
2. Influence-track impact remains weak and indirect; there is no dedicated influence-effect transparency contract.
3. BL-005 rejection rationale is partially transparent but not fully threshold-attribution complete.
4. Counterfactual what-if analysis is not emitted in BL-008 or BL-009.

## Future Work (Optional, Out of Current Scope)

1. Add control-application tracing fields at per-track and per-stage levels.
2. Add influence source/effect breakdown contracts where measurable impact exists.
3. Add richer threshold-impact attribution in BL-005 diagnostics.
4. Add counterfactual scenario summaries in observability outputs.

## Transparency Design Principles

1. **Control Traceability**: Every decision must be traceable to explicit user control or system rule ← Gap: Not implemented
2. **Counterfactual Clarity**: User can predict what would happen with different controls ← Gap: Not implemented
3. **Ranking Justification**: Why is Track A #2 and Track B #8? ✅ (BL-008 shows scoring)
4. **Rejection Rationale**: Why was Candidate X rejected? ⚠️ (Partial—shows fail, not which threshold)
5. **Configuration Impact**: How did my control choices affect the outcome? ❌ (Not traced)

## Next Steps
- [ ] Keep limitation statements explicit in thesis claims and evaluation framing
- [ ] Keep stage-level transparency descriptions aligned with emitted fields in code
- [ ] Revisit future-work transparency features only if scope expands
