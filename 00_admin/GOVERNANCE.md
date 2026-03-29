# Governance: Controllability & Transparency

## Authority
This document governs feature development, control implementation, and transparency verification for the thesis project.

## Core Principle
**Every feature must pass the Control & Transparency Gate** before implementation or merge.

## The Gate: Three Questions

When proposing ANY new feature, change, or control:

1. **Does this add measurable user control or transparency?**
   - If NO: This feature is out of scope
   - If YES: Proceed to Q2
   - If UNCLEAR: Escalate to decision_log for resolution

2. **Is the control-to-effect relationship traceable and testable?**
   - If NO: Return to design phase, define measurable effect
   - If YES: Proceed to Q3
   - If UNCERTAIN: Add to RESEARCH_DIRECTIONS.md as open design question

3. **Can we verify this is working via BL-010 (reproducibility) or BL-011 (controllability) tests?**
   - If NO: Cannot implement this feature
   - If YES: Proceed to implementation
   - If DEFERRED: Document in decision_log with justification

## Implementation Checklist

Before a feature is considered "done":

- [ ] Feature passes control/transparency gate (3 questions above)
- [ ] Control is documented in `07_implementation/CONTROL_SURFACE_REGISTRY.md`
- [ ] Transparency outputs are documented in `07_implementation/TRANSPARENCY_SPEC.md`
- [ ] Control-to-effect mapping is explicit in documentation
- [ ] BL-010 or BL-011 tests verify measurable effect
- [ ] Effect size is documented (e.g., "changing X produces Y% change in Z")
- [ ] Code changes are ONLY to support control/transparency (no other modifications)
- [ ] All documentation files are updated in same session

## Escalation Rules

### When to Escalate to decision_log.md
- Feature fails Gate (any of 3 questions)
- Control effect is unclear or unmeasurable
- Transparency requirements conflict with performance/simplicity
- Uncertain about control-effect measurement methodology

> Note: Influence track override semantics are no longer an open escalation item. Influence tracks are a documented WEAK/known-limitation control (zero measured playlist effect in BL-011 testing); assembly-layer redesign is explicitly deferred out of scope. See `07_implementation/CONTROL_SURFACE_REGISTRY.md`.

### When to Escalate to RESEARCH_DIRECTIONS.md
- Open design question (e.g., "How many influence slots?")
- Feature is aspirational (document, don't implement)
- Uncertain about best UX for a control
- Measuring control effect is challenging

### When to Escalate to mentor_question_log.md
- Thesis scope impacts (does this still fit thesis intent?)
- Foundational decisions that affect multiple features
- Evaluation methodology questions (how do we measure success?)

## Control Lifecycle

### Stage 1: Design
- Define control semantics (what does the user intend?)
- Propose control-to-effect mapping (what should change?)
- Identify where in pipeline control applies
- Document in RESEARCH_DIRECTIONS.md or decision_log.md

### Stage 2: Implementation
- Add control to run_config schema
- Update CONTROL_SURFACE_REGISTRY.md with implementation status
- Add control traceability to relevant stages (BL-004 through BL-009)
- Implement BL-011 test scenario to verify effect

### Stage 3: Verification
- Run BL-010 reproducibility check (same config → same output)
- Run BL-011 controllability check (different config → measurable difference)
- Document effect size and direction in REGISTRY
- Update TRANSPARENCY_SPEC.md with outputs showing control application

### Stage 4: Maintenance
- Keep REGISTRY and SPEC updated as changes are made
- If control stops producing measurable effect, investigate and document
- Archive/deprecate controls that become obsolete

## Documentation Governance

These files are "live" and must be kept current:

| File | Update Trigger | Refresh Frequency |
|------|---|---|
| CONTROL_SURFACE_REGISTRY.md | Control status changes | After each BL-011 test |
| TRANSPARENCY_SPEC.md | New transparency outputs added | After each stage completion |
| .instructions.md | Thesis framing evolves | Quarterly or on pivot |
| README in 00_admin | Implementation status changes | End of sprint |
| decision_log.md | Major design decisions made | Every session |

## Control-Effect Validation

Every control MUST be validated via the control-effect measurement protocol. If a control does not produce measurable change:

1. **Investigate**: Is the control implemented correctly?
2. **Measure**: What is the effect size? Is it non-zero?
3. **Document**: Why is effect smaller than expected? (e.g., influence_tracks shows 0% effect)
4. **Decide**: Redesign control or deprecate it?
5. **Record**: Add findings to CONTROL_SURFACE_REGISTRY.md

## Transparency Verification

Transparency outputs must cover:
- **WHAT** happened (decision made)
- **WHY** it happened (which rules/controls applied)
- **WHAT IF** (how control changes would alter outcome)

If any of these three is missing, the transparency is incomplete.

## When Controls Conflict

If two controls produce conflicting effects:
1. Document the interaction in CONTROL_SURFACE_REGISTRY.md
2. Define priority order (e.g., user intent > system rules)
3. Test interaction via BL-011 scenario
4. Update decision_log.md with resolution

Example: "Influence tracks override genre caps because user explicit intent > system diversity rules."

## Escalation Gates (What Blocks Implementation)

✋ **BLOCK implementation if**:
- Control-to-effect mapping is unclear
- No way to measure control effect
- BL-011 test cannot validate control works
- Feature reduces transparency of existing controls

✅ **ALLOW implementation if**:
- 3 gate questions are answered YES
- BL-011 test confirms measurable effect
- Documentation is updated simultaneously
- No regression in existing controls/transparency

## Decision Template

When making a control-related governance decision, record in decision_log.md:

```markdown
## D-XXX: [Control Name] Design Decision
- Problem: [What control gap are we addressing?]
- Options: [What were the alternatives?]
- Decision: [What did we choose?]
- Rationale: [Why this is better for controllability/transparency]
- Evidence: [What test/measurement / supports this?]
- Impact: [Effect on other controls/transparency]
```
