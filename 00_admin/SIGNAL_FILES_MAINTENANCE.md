# Signal Files Maintenance Guide

## Purpose
Ensure that governance and signal files remain current, discoverable, and continue to signal that controllability and transparency are thesis-core design priorities.

## About Signal Files

Signal files are persistent documentation artifacts that communicate design intent to every agent, reviewer, and contributor who enters the workspace. They are "read first" materials that establish thesis framing upfront.

**Signal files in this system**:
1. `.controllability-transparency.instructions.md` — Workspace root, framing for agents
2. `CONTROL_SURFACE_REGISTRY.md` — Audit of all controls and their designer status
3. `TRANSPARENCY_SPEC.md` — Mapping of outputs to transparency requirements
4. `GOVERNANCE.md` — Rules for control/transparency feature development
5. `RESEARCH_DIRECTIONS.md` — Open design questions and aspirational features
6. `00_admin/README.md` — Updated with thesis focus section prepended

## File-by-File Maintenance

### .controllability-transparency.instructions.md
**Location**: Workspace root (discoverable with first file list)

**Content**: Framing for agents/reviewers, thesis core statement, active references

**Update trigger**:
- Thesis scope changes (major decision point)
- Major design pivot (e.g., influence track redesign)
- Quarterly alignment check (ensure framing is still accurate)

**Maintenance task**:
```markdown
- [ ] Review current thesis core statement
- [ ] Verify all active references are accurate
- [ ] Check that links to key files are not broken
- [ ] Update date if modified
- [ ] Confirm readable by persons new to project
```

**Review frequency**: Quarterly or on major change

---

### CONTROL_SURFACE_REGISTRY.md
**Location**: `05_design/CONTROL_SURFACE_REGISTRY.md`

**Content**: Audit of all controls (weak/working status), measured effects, design gaps

**Update trigger**:
- After BL-011 controllability test ← **Primary trigger**
- When new control is proposed
- When control is redesigned or deprecated
- Quarterly cleanup/reconciliation

**Maintenance task**:
```markdown
- [ ] Run BL-011 controllability tests
- [ ] Update effect size measurements for each control
- [ ] Check for new "✅ WORKING" → "❌ WEAK" downgrades (investigate!)
- [ ] Record date of last test
- [ ] Update pending additions section if priorities changed
- [ ] Verify links to control definitions (run_config schema, code locations)
```

**Ownership**: Implementation owner (whoever is working on controls)

**Review frequency**: After each BL-011 test (typically weekly-ish during active development)

---

### TRANSPARENCY_SPEC.md
**Location**: `05_design/TRANSPARENCY_SPEC.md`

**Content**: Maps BL-004 through BL-008 to current outputs + gaps + planned enhancements

**Update trigger**:
- After TRANSPARENCY_AUDIT_CHECKLIST run ← **Primary trigger**
- When new transparency output is added
- When transparency gap is resolved
- When D-043 (control application tracing) or AF2 (what-if) is implemented

**Maintenance task**:
```markdown
- [ ] Run TRANSPARENCY_AUDIT_CHECKLIST
- [ ] Check each stage for new gaps or improvements
- [ ] Update "Gap X: [status]" section (not started / in progress / resolved)
- [ ] Verify all linked design files (controllability_design_addendum, transparency_design_addendum) are accurate
- [ ] Record date of last audit
- [ ] Cross-reference GOVERNANCE.md to ensure consistency
```

**Ownership**: Implementation owner

**Review frequency**: After each transparency audit (typically weekly-ish during active development)

---

### GOVERNANCE.md
**Location**: `00_admin/GOVERNANCE.md`

**Content**: Rules for control/transparency feature development (the 3-question gate)

**Update trigger**:
- When a new governance rule needs to be added
- When escalation procedures need refinement
- Quarterly alignment check
- When a design decision violates gate (need to refine gate itself)

**Maintenance task**:
```markdown
- [ ] Review "The Gate: Three Questions" section
- [ ] Check if any active work is blocked by gate (if so, gate may need refinement)
- [ ] Verify escalation rules are clear
- [ ] Confirm decision template matches decision_log.md format
- [ ] Check that stage stages (Design / Implementation / Verification / Maintenance) are still appropriate
```

**Ownership**: Project lead (with input from implementation team)

**Review frequency**: Quarterly or when new governance issue arises

---

### RESEARCH_DIRECTIONS.md
**Location**: `00_admin/RESEARCH_DIRECTIONS.md`

**Content**: Open design questions (RQ1-4), aspirational features (AF1-5), investigation tasks

**Update trigger**:
- After GOVERNANCE.md escalation (add new RQ/AF)
- After design meeting produces unresolved questions
- After control test shows unexpected behavior (escalate to RQ)
- End of sprint: check off completed investigations
- Quarterly: review AF status, reprioritize

**Maintenance task**:
```markdown
- [ ] Add new RQ entries for recently escalated questions
- [ ] Check off completed investigation tasks
- [ ] Update AF status (Aspirational → Design phase → Implementation phase)
- [ ] Review RQ blockers (do any block Phase 3 progress?)
- [ ] Verify no duplicate RQ entries
- [ ] Cross-reference to decision_log.md for related decisions
```

**Ownership**: Project lead + mentor (some RQs require advisor input)

**Review frequency**: Weekly (quick check) + monthly (comprehensive)

---

### 00_admin/README.md
**Location**: `00_admin/README.md`

**Content**: Governance hub with thesis focus section prepended

**Update trigger**:
- After major implementation milestone (Phase 2, Phase 4)
- After decision_log.md has new "accepted" decisions
- Quarterly alignment check
- Before thesis submission (final state snapshot)

**Maintenance task**:
```markdown
- [ ] Verify "Thesis Focus" section is prominent (first thing seen)
- [ ] Check that active control/transparency files are referenced
- [ ] Verify latest decision IDs are listed in "Active Decisions" section
- [ ] Cross-reference to GOVERNANCE.md, CONTROL_SURFACE_REGISTRY, TRANSPARENCY_SPEC
- [ ] Update "Last refreshed" date
- [ ] Confirm new contributors would immediately understand thesis priority
```

**Ownership**: Project lead

**Review frequency**: End of each phase, then quarterly

---

## Batch Maintenance Routine

### Weekly (5 minutes)
- [ ] Check CONTROL_SURFACE_REGISTRY for control test status
- [ ] Check RESEARCH_DIRECTIONS for new tasks
- [ ] Verify all files still exist and have no obvious errors

### End of Phase (30 minutes)
- [ ] Run full TRANSPARENCY_AUDIT_CHECKLIST
- [ ] Update TRANSPARENCY_SPEC with audit findings
- [ ] Update CONTROL_SURFACE_REGISTRY with all recent tests
- [ ] Add new entries to decision_log.md if decisions were made
- [ ] Update RESEARCH_DIRECTIONS with phase completions
- [ ] Update README.md with phase status
- [ ] Verify all 6 signal files are current and consistent

### Quarterly Alignment (1 hour)
- [ ] Full audit: Read each signal file top-to-bottom
- [ ] Check for contradictions between files
- [ ] Verify structure is still appropriate
- [ ] Update dates and refresh cycles
- [ ] Identify any obsolete files or redundancies
- [ ] Confirm thesis framing is still accurate
- [ ] Review mentor feedback for necessary updates
- [ ] Document any structural improvements needed

### End of Thesis Project
- [ ] Finalize all signal files (mark status as "complete")
- [ ] Create snapshot of all governance docs for archive
- [ ] Document any lessons learned for future projects
- [ ] Prepare summary of control/transparency evolution for chapter 4 (evaluation)

## Consistency Checks

Use these checks to detect problems early:

### Check C1: File Reference Consistency
Every file should reference every other signal file where appropriate.

```
.instructions.md → should reference CONTROL_SURFACE_REGISTRY, TRANSPARENCY_SPEC, GOVERNANCE
CONTROL_SURFACE_REGISTRY → should reference TRANSPARENCY_SPEC, GOVERNANCE, RESEARCH_DIRECTIONS
TRANSPARENCY_SPEC → should reference GOVERNANCE, RESEARCH_DIRECTIONS
GOVERNANCE → should reference RESEARCH_DIRECTIONS, decision_log
RESEARCH_DIRECTIONS → should reference GOVERNANCE, decision_log
README → should reference all of the above
```

**What to do if broken**: Add missing reference immediately; it indicates unfinished thought.

### Check C2: Cross-File Contradiction Detection
```
If CONTROL_SURFACE_REGISTRY says "influence_tracks: ❌ WEAK"
  Then RESEARCH_DIRECTIONS should have RQ1 about influence track redesign
  And decision_log should have decision about influence slot policy (D-042 ✓)
```

**What to do if broken**: Files are out of sync; update the stale one.

### Check C3: Stale Reference Detection
```
If GOVERNANCE references "D-041 not yet implemented"
  And decision_log shows "D-041: status: accepted"
  Then GOVERNANCE should reference it as "implemented in Phase 1" or update
```

**What to do if broken**: Old references become confusing; update for accuracy.

### Check C-4: Discrepancy Between REGISTRY and Actual Code
```
If CONTROL_SURFACE_REGISTRY says "feature_weights: ✅ WORKING"
  Then run_config schema must allow feature_weights configuration
  And BL-006 must actually use those weights
```

**What to do if broken**: Code changed but REGISTRY not updated; update REGISTRY immediately.

## Conflict Resolution

If two signal files disagree on a design decision:

1. **Check decision_log.md**: Did a newer decision supersede the older one?
2. **Check dates**: Which file was updated more recently?
3. **Escalate to mentor**: If unclear which is correct
4. **Record resolution in decision_log.md**: Document the correction
5. **Update both files**: Ensure they're now consistent

## When to Archive vs. Update

### Update (not archive) if:
- New information makes old guidance outdated but still relevant
- Gap is being resolved by Phase 3+ implementation
- Design decision evolves but thesis intent remains
- Measurement shows we were partially wrong but overall direction is good

### Archive (create superseded entry) if:
- Entire design approach is being replaced (rare)
- Research question is definitively answered and closed
- Control is being deprecated or removed

## File Format Standards

All signal files should follow these standards:

- Use Markdown formatting
- Include a Purpose section
- Use clear section headers (##, ###, ####)
- Include examples where possible
- Link to related files using relative paths: `../path/to/file.md`
- Update "Last updated" date on each modification
- Keep lines to ~100 characters for readability
- Use tables for structured data comparisons
- Include success criteria for each section

## Archival & History

**Archive location**: `_deep_archive_march2026/` (per repo convention)

**When to archive**: End of project or when signal file becomes obsolete

**What to preserve**:
- All versions of CONTROL_SURFACE_REGISTRY (shows control evolution)
- All versions of TRANSPARENCY_SPEC (shows transparency evolution)
- Snapshot of decision_log.md at each phase
- Final RESEARCH_DIRECTIONS.md (shows open questions at project end)

