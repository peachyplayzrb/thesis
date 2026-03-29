# Research Directions

## Purpose
Document open design questions, aspirational features, and research opportunities for controllability and transparency.

## Active Research Questions

### RQ1: Influence Track Policy
**Question**: Should influence tracks override assembly rules (genre caps, consecutive limits)?

**Current State**: Not implemented; influence tracks are pre-profile seeds

**Options**:
- Option A: Influence tracks bypass all rules (user explicit intent dominates)
  - Pro: Strong user control, clear semantics
  - Con: May break playlist coherence if user selects incompatible tracks

- Option B: Influence tracks follow same rules as candidates
  - Pro: Maintains system coherence guarantees
  - Con: Weak user intent—tracks may still be excluded

**Implications**:
- Choice affects BL-007 assembly logic
- Affects transparency explanations (why was influence track rejected?)
- Affects test scenarios in BL-011

**Next Step**: Propose decision for decision_log.md

### RQ2: Influence Slot Reservation Strategy
**Question**: How many playlist slots should be reserved for influence tracks?

**Design Space**:
- Fixed (e.g., always 2 slots)?
- User-configurable (0-10 slots)?
- Adaptive (based on influence track count)?

**Criteria**:
- User control: How much say does user have?
- Playlist coherence: Does it break diversity?
- Simplicity: Can user reason about the tradeoff?

**Research Needed**:
- What happens if influence tracks conflict with genre diversity?
- How many influence tracks do users typically select?

### RQ3: Control-Effect Measurement Methodology
**Question**: How do we quantify "measurable effect" for a control?

**Current Examples**:
- Feature weights: Different scores → ranks different → measurable ✓
- Numeric thresholds: Different pool sizes → measurable ✓
- Influence tracks: 0% measured effect → weak ✗

**Challenge**: Effect size spectrum
- Some controls have large, obvious effects
- Some controls have small effects
- Some controls have zero or unmeasurable effects

**Questions**:
- What is minimum threshold for "measurable"? (e.g., 1% change? 5%?)
- How do we measure effect on intangible outcomes? (e.g., "coherence")
- Should we measure effect at each stage or only final playlist?

**Research Approach**:
- Define effect taxonomy: pool-size, rank-change, composition-change, etc.
- Create measurement protocol for each effect type
- Apply to all controls and document in REGISTRY

### RQ4: Transparency for Weak Controls
**Question**: How transparent can we be about a control that has zero effect?

**Challenge**:
- Influence tracks are "visible" in BL-004 seed aggregation
- But they have zero observed effect on final playlist
- How do we transparently explain "you picked these, they did nothing"?

**Options**:
- Option A: Show influence seeds in profile but explain effect was negligible
- Option B: Remove from outputs (they're hidden in aggregation anyway)
- Option C: Highlight as "ineffective" and suggest redesign

**Design Question**:
- Should transparency expose failed or weak controls?
- Or should transparency only show effective controls?

---

## Aspirational Features (Future Phases)

### AF1: Per-Control Configuration Profiles
**Idea**: Let users save/load bundles of control settings (e.g., "maximize diversity", "maximize coherence")

**Status**: Aspirational
**Complexity**: Medium
**Controllability Value**: High (easier control UX)
**Transparency Impact**: Could simplify explanations

### AF2: Control Sensitivity Analysis
**Idea**: Show user what would happen if they adjusted each control by +/-10%

**Status**: Aspirational
**Complexity**: High (requires what-if simulation)
**Controllability Value**: Very high (user can predict outcomes)
**Transparency Impact**: Supports counterfactual reasoning

### AF3: Control Interaction Matrix
**Idea**: Document which controls interact, and in what direction

**Status**: Design phase
**Example**:
```
feature_weights × numeric_thresholds = HIGH interaction
  (both affect which candidates are scored)

assembly_rules × influence_tracks = POTENTIAL conflict
  (rules might reject influence tracks)
```

### AF4: Automatic Effect Measurement
**Idea**: After every BL-011 run, automatically compute and log control-effect sizes

**Status**: Aspirational
**Complexity**: Medium
**Value**: Makes REGISTRY maintenance automatic

### AF5: Counterfactual Playlist Generation
**Idea**: Show user what playlist would look like under different control settings (on demand)

**Status**: Research phase
**Complexity**: High (requires re-running parts of pipeline)
**Value**: Maximum user understanding of control effects

---

## Design Partnerships (Open Collaboration)

### With Thesis Advisor
- **Question**: Do weak controls (zero effect) belong in the system?
  - Should we redesign them or remove them?
  - Or document as "research limitation"?

- **Question**: Is transparency about uncertainty valued?
  - Should we show user when a control had no effect?
  - Or hide weak controls?

### With Evaluation Team (Chapter 4)
- **Question**: How do we evaluate controllability?
  - Measure: User control effectiveness?
  - Measure: User understanding?
  - Measure: Reproducibility of control effects?

---

## Investigation Tasks (To-Do)

- [ ] Research how other recommendation systems handle transparent controls
- [ ] Interview users (if possible): what controls do they expect?
- [ ] Analyze BL-011 test results to understand control-effect spectrum
- [ ] Prototype influence slot reservation logic
- [ ] Design what-if simulation approach
- [ ] Evaluate performance impact of transparency features

---

## Blockers & Dependencies

| Task | Blocked By | Unblocks |
|------|-----------|----------|
| Influence redesign | RQ1 decision | Phase 3 implementation |
| Assembly rule exposure | PR2 decision | Phase 3 Assembly rule tuning |
| What-if analysis | AF2 design | Counterfactual transparency |
| Control interaction matrix | AF3 design | Advanced control documentation |

---

## Success Criteria for Research Phase

✅ Research complete when:
- All RQ1-RQ4 are answered or escalated to decision_log
- Control-effect measurement methodology is defined
- At least 2 aspirational features have preliminary designs
- Blockers are identified and have mitigation plans
