# HISTORICAL REFERENCE NOTICE

This checklist is retained as a historical phase artifact and is not an active submission-closeout control surface. For active readiness authority, use `00_admin/thesis_state.md`, `00_admin/timeline.md`, and current quality-control submission surfaces.

# Transparency Audit Checklist

## Purpose
Spot-check procedure to verify that transparency outputs satisfy thesis requirement: "User can understand why this outcome resulted from their choices."

## Pre-Run Transparency Audit (Design-Time)

### A1: Transparency Scope Check
- [ ] All BL stages have defined transparency outputs (logs, traces, artifacts)?
- [ ] BL-005 logs why candidates were rejected (or just pass/fail)?
- [ ] BL-006 explains top score drivers for top-ranked tracks?
- [ ] BL-007 shows which rule caused each rejection?
- [ ] BL-008 provides per-track explanations (not just scores)?
- [ ] BL-009 captures full run diagnostics?

**Success**: All stages have defined outputs that show WHAT happened.

### A2: Control Traceability Check
- [ ] Configuration is documented in run metadata?
- [ ] BL-003 shows which input sources were used?
- [ ] BL-004 trace shows which seeds came from influence vs. history?
- [ ] BL-006 shows which feature weights were active?
- [ ] BL-007 shows which assembly rules were applied?

**Success**: User can see which controls were active in this run.

### A3: Rule Application Check
- [ ] BL-005 explanation includes which thresholds were applied?
- [ ] BL-006 explanation includes which  components contributed most?
- [ ] BL-007 explanation includes which rule caused rejection (R1/R2/R3/R4)?
- [ ] BL-008 explanation includes top 3-5 factors (not all 10 components)?

**Success**: User can see WHICH RULES were applied.

### A4: User Intent Check
- [ ] Can user identify which tracks are there BECAUSE of their controls?
- [ ] Can user identify which tracks would NOT be there if they changed a control?
- [ ] Are influence_tracks (if enabled) visibly included or explicitly explained as absent?
- [ ] Does explanation distinguish "was selected because of your taste" vs. "was selected despite your thresholds being loose"?

**Success**: User intent is traceable through outputs.

## Post-Run Transparency Audit (Validation-Time)

### B1: Output Artifact Check
- [ ] Run produced `bl008_explanations.json` (not empty)?
- [ ] Run produced `bl009_diagnostics.json` (not empty)?
- [ ] Run produced `bl003_alignment_report.json` (shows matched/unmatched)?
- [ ] Run produced `bl004_seed_trace.csv` (shows seed sources)?
- [ ] Run produced `bl007_assembly_trace.json` (shows rule applications)?

**Success**: All transparency artifacts present and populated.

### B2: Explanation Quality Check
Sample 3 random tracks from final playlist and check:

For each track:
- [ ] Track ID is present?
- [ ] Score is shown?
- [ ] Top contributor components are identified (e.g., "danceability=0.91")?
- [ ] Explanation is human-readable (not just raw JSON)?
- [ ] If rank ≤3: top reason for selection is clear?

**Success**: Explanations are readable and actionable.

### B3: Rejection Documentation Check
Sample 10 candidates that were rejected and check:

For each rejection:
- [ ] Rejection reason is logged (BL-005/BL-006/BL-007)?
- [ ] If numeric threshold: which threshold caused rejection?
- [ ] If assembly rule: which rule (R1/R2/R3/R4)?
- [ ] Can user understand why they were filtered?

**Success**: Rejections are documented with reasons.

### B4: Control Application Tracing Check ⚠️ (Currently Incomplete)

Sample 5 tracks that were included and check:

For each track:
- [ ] Can you identify which of the user's controls enabled this selection?
- [ ] Example: "Selected because YOUR danceability weight of 1.5 boosted score"
- [ ] Example: "Selected because YOUR numeric threshold window included this range"
- [ ] Example: "Selected because YOUR input scope included this source"

**Success**: You can trace user intent → control → selection

**Current Status**: This check will FAIL (Gap 1 in TRANSPARENCY_SPEC). Mark as "TODO: Implement D-043" and continue with other checks.

### B5: What-If Clarity Check ⚠️ (Currently Missing)

For top 5 tracks, ask:

- [ ] "If I stricter numeric thresholds, would this track still be included?"
- [ ] "If I disable influence_tracks, would top-ranked tracks change order?"
- [ ] "If I changed feature weights to [X], would this track rank higher?"

**Success**: You can PREDICT what would happen

**Current Status**: This check will FAIL (requires AF2 from RESEARCH_DIRECTIONS). Mark as "TODO: Implement counterfactual analysis" and continue.

## Audit Checklist Template

### Transparency Audit Run
Date: [YYYY-MM-DD]
Run ID: [BL-009 run summary ID]
Auditor: [name]

**Pre-Run (Design-Time)**:
- [ ] A1 Transparency Scope: PASS / FAIL / PARTIAL
- [ ] A2 Control Traceability: PASS / FAIL / PARTIAL
- [ ] A3 Rule Application: PASS / FAIL / PARTIAL
- [ ] A4 User Intent: PASS / FAIL / PARTIAL
  - Issues found: [list any gaps]
  - Actions needed: [what to fix?]

**Post-Run (Validation-Time)**:
- [ ] B1 Output Artifacts: PASS / FAIL
- [ ] B2 Explanation Quality: PASS / FAIL / NEEDS_WORK
- [ ] B3 Rejection Documentation: PASS / FAIL / INCOMPLETE (expected)
- [ ] B4 Control Application Tracing: FAIL (expected, D-043 pending)
- [ ] B5 What-If Clarity: FAIL (expected, AF2 pending)
  - Issues found: [list any gaps]
  - Actions needed: [what to fix?]

**Summary**:
- Transparency quality: [STRONG / GOOD / ADEQUATE / WEAK]
- Critical gaps: [any show-stoppers?]
- Pending enhancements from design: [D-043, AF2, etc.]
- Signed off: [YES / NEEDS_REVISION]

---

## Expected Gaps (Acceptable for Phase 1-3)

| Check | Current Status | Design Ticket | Phase |
|-------|---|---|---|
| B4 Control Application Tracing | ❌ Not implemented | D-043 | Phase 3+ |
| B5 What-If Clarity | ❌ Not implemented | AF2 | Phase 4+ |
| Influence seed source visibility | ⚠️ Partial (aggregated only) | D-041/D-042 | Phase 3+ |
| Assembly rule transparency | ⚠️ Partial (rule name only) | TRANSPARENCY_SPEC | Phase 3+ |

## Audit Frequency

- **After every Phase 3+ change**: Run full audit
- **End of sprint**: Run full audit + document findings
- **Before thesis submission**: Comprehensive audit to verify all thesis requirements are met
- **Ad-hoc**: When implementing new controls or transparency enhancements

## Escalation

If audit finds:
- **CRITICAL TRANSPARENCY GAP**: Escalate to GOVERNANCE.md (control/transparency gate)
- **MODERATE GAP** (acceptable for now): Document in RESEARCH_DIRECTIONS.md
- **EXPECTED PENDING**: Mark with design ticket (D-043, AF2, etc.) and continue

## Success Criteria for Thesis

Transparency audit must show:
1. ✅ All outputs present and populated
2. ✅ Explanations are readable (B2)
3. ✅ Rejections are documented (B3)
4. ✅ Control application is traceable (B4) — currently pending D-043
5. ✅ User can predict what-if outcomes (B5) — currently pending AF2
