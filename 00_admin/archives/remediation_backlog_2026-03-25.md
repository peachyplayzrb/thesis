# Pipeline Remediation Backlog — 2026-03-25

**Scope**: Prioritized list of issues from comprehensive pipeline audit dated 2026-03-25  
**Status**: Audits performed; prioritization assigned; implementation plan documented  
**Assessment Window**: Pre-final hardening (2026-03-25 to 2026-04-10)

---

## Executive Summary

Comprehensive pipeline audit identified **25 issues** across critical, high, medium, and architectural categories. This document prioritizes them into two tiers:

1. **Tier 1 (Must Fix Before Final Submission)**: 5 issues with direct thesis validity risk
2. **Tier 2 (Defer to Future Work)**: 20 issues with lower impact or complexity trade-offs

**Already Completed (2026-03-25)**:
- ✅ CRI-001: Unmatched-track bias detection + validation gate + Chapter 3 documentation
- ✅ CRI-005: Circular key distance (verified already implemented correctly)

---

## Tier 1: Critical Path (Address Now)

These 5 issues must be resolved before thesis final hardening to prevent submission-blocking validity concerns.

### 1. **CRI-004: Positive Threshold Validation**
- **Current Status**: **✓ COMPLETED 2026-03-25**
- **Risk Level**: CRITICAL (pipeline corruption possible) → **RESOLVED**
- **Effort**: Low (30 min implementation) → **ACTUAL: 45 min**
- **Why Now**: Silent division-by-zero or invalid scores could compromise all downstream results
- **Completion Evidence**:
  - 9/9 unit tests pass (test_cri004_simple.py)
  - BL-013 integration test passes with valid configs
  - Invalid thresholds correctly rejected with clear error messages
  - Example error: "retrieval_controls.numeric_thresholds: threshold 'tempo' must be positive (> 0), got 0.0"
  - Change log entry: C-153
  - Test notes updated: TC-CRI004-001
- **Implementation**:
  - Add validation in `run_config_utils.py` to check all numeric thresholds > 0
  - Fail at config load time with clear error message
  - Add BL-014 sanity check
- **Thesis Impact**: Without this, undetected misconfigurations could invalidate results
- **Files to Modify**:
  - `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`
  - `07_implementation/implementation_notes/sanity_check/run_bl014_sanity_checks.py`
- **Evidence for Fix**: Configuration validation tests

---

### 2. **CRI-002: Numeric Threshold Coupling Between BL-005 & BL-006**
- **Current Status**: **✓ COMPLETED 2026-03-25**
- **Risk Level**: HIGH (semantic incoherence possible) -> **RESOLVED**
- **Effort**: Medium (1.5-2 hours) -> **ACTUAL: 50 min**
- **Why Now**: Decoupled thresholds can produce hard-to-interpret playlist outputs
- **Implementation**:
  - Add validation in `run_config_utils.py` to enforce:
    - `retrieval_controls.numeric_thresholds == scoring_controls.numeric_thresholds`
  - OR consolidate into single `numeric_thresholds` block
  - Emit warning if thresholds differ (with explanation)
  - Add test case verifying enforcement
- **Thesis Impact**: Prevents silent config drift that breaks reproducibility claims
- **Files to Modify**:
  - `07_implementation/implementation_notes/bl000_run_config/run_config_template_v1.json`
  - `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`
  - `07_implementation/implementation_notes/bl005_retrieval/build_bl005_candidate_filter.py`
  - `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
- **Evidence for Fix**: BL-013 orchestration with forced threshold mismatch (should fail)
- **Completion Evidence**:
  - BL-013 standard run passes with matched thresholds (`BL013-ENTRYPOINT-20260325-013331-903943`)
  - Forced mismatch config (`test_mismatched_numeric_thresholds.json`) fails fast with explicit coupling error
  - Error details include exact mismatch values (tempo retrieval=20.0 vs scoring=25.0)
  - Change log entry: C-154
  - Test notes updated: TC-CRI002-001

---

### 3. **HIGH-003: Undersized Playlist Warning & Documentation**
- **Current Status**: **✓ COMPLETED 2026-03-25**
- **Risk Level**: HIGH (silent quality loss) -> **RESOLVED**
- **Effort**: Low (45 min) -> **ACTUAL: 55 min**
- **Why Now**: Assembly rules can produce playlists with < 10 tracks without warning
- **Implementation**:
  - In BL-007, emit warning if final playlist < target_size
  - Log reason (e.g., "ran out of eligible candidates due to genre cap")
  - Document in Chapter 4 that undersized outputs are possible
  - Add BL-014 check flagging undersized results
- **Thesis Impact**: Prevents claims that "system produces 10-track playlists" without caveat
- **Files to Modify**:
  - `07_implementation/implementation_notes/bl007_playlist/build_bl007_playlist.py`
  - `08_writing/chapter4.md` (evaluation results section)
  - `07_implementation/implementation_notes/bl014_quality/run_bl014_sanity_checks.py`
- **Evidence for Fix**: BL-013 run with strict assembly controls (document undersized output)
- **Completion Evidence**:
  - BL-013 strict-controls run produces undersized playlist with explicit warning diagnostics (`BL013-ENTRYPOINT-20260325-013610-197098`)
  - BL-007 assembly report includes `undersized_playlist_warning` block with shortfall + exclusion pressures
  - Chapter 4 updated with explicit caveat text (Section 4.9.1)
  - BL-014 code updated to flag undersized outputs in advisories and run matrix fields
  - Change log entry: C-155
  - Test notes updated: TC-HIGH003-001

---

### 4. **HIGH-004: Profile-Retrieval Limit Constraint Validation**
- **Current Status**: **✓ COMPLETED 2026-03-25**
- **Risk Level**: HIGH (silent data misalignment) -> **RESOLVED**
- **Effort**: Medium (1 hour) -> **ACTUAL: 40 min**
- **Why Now**: BL-005 can reference non-existent profile dimensions
- **Implementation**:
  - In `run_config_utils.py`, add cross-config validation:
    - `retrieval_controls.profile_top_tag_limit ≤ profile_controls.top_tag_limit`
    - `retrieval_controls.profile_top_genre_limit ≤ profile_controls.top_genre_limit`
    - Same for `profile_top_lead_genre_limit`
  - Emit clear error if violated
  - Add test case
- **Thesis Impact**: Prevents undefined behavior in candidate filtering
- **Files to Modify**:
  - `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`
  - `07_implementation/implementation_notes/bl000_run_config/run_config_template_v1.json` (add comment)
- **Evidence for Fix**: Config validation test with mismatched limits
- **Completion Evidence**:
  - BL-013 canonical run passes (`BL013-ENTRYPOINT-20260325-013848-150034`)
  - Forced-violation config (`test_invalid_profile_retrieval_limits.json`) fails fast with explicit pairwise mismatch details
  - Template documentation updated with limit-coupling comments
  - Change log entry: C-156
  - Test notes updated: TC-HIGH004-001

---

### 5. **CRI-003: Component Weight Validation & Rebalance Warning**
- **Current Status**: **✓ COMPLETED 2026-03-25**
- **Risk Level**: HIGH (scoring instability) -> **RESOLVED**
- **Effort**: Medium (1.5 hours) -> **ACTUAL: 70 min**
- **Why Now**: Silent weight rebalancing can distort scoring without operator awareness
- **Implementation**:
  - In `run_config_utils.py`, validate component weights sum to 1.0 (tolerance ±0.01)
  - In BL-006, emit **warning** when rebalancing occurs (not fatal, but logged)
  - Log original vs. normalized weights
  - Document in observability output
  - Add BL-014 check for weight normalization alerts
- **Thesis Impact**: Ensures scoring transparency and prevents hidden weight drift
- **Files to Modify**:
  - `07_implementation/implementation_notes/bl000_run_config/run_config_utils.py`
  - `07_implementation/implementation_notes/bl006_scoring/build_bl006_scored_candidates.py`
  - `07_implementation/implementation_notes/bl009_observability/build_bl009_observability_log.py`
- **Evidence for Fix**: BL-013 run with edge-case weights; log shows rebalancing warning
- **Completion Evidence**:
  - Invalid sum config (1.10) fails fast with explicit tolerance error
  - Edge-case sum config (1.009) passes and emits BL-006 rebalancing warning (`BL013-ENTRYPOINT-20260325-014206-982935`)
  - BL-006 summary persists `weight_rebalance_diagnostics` with original vs normalized maps
  - BL-009 observability log includes propagated `weight_rebalance_diagnostics`
  - Change log entry: C-157
  - Test notes updated: TC-CRI003-001

---

## Tier 2: Deferred (Future Work)

These 20 issues have lower thesis-impact risk or greater implementation complexity. Address in thesis revision or follow-up work.

| Issue | Category | Risk | Effort | Target Release |
|-------|----------|------|--------|-----------------|
| HIGH-001 | Influence track non-determinism | Medium | High | v2 |
| HIGH-002 | Filtering decision detail (missing dimensions) | Low | Medium | v2 |
| HIGH-005 | Explanation causality reframing | Medium | Medium | v2 |
| HIGH-006 | Data integrity validation (row counts) | Medium | Low | v2 |
| HIGH-007 | Freshness guard array handling | Low | Low | v2 |
| MED-001 | Edge-case dataset test coverage | Low | Medium | v2 |
| MED-002 | Observability field completeness validation | Low | Low | v2 |
| MED-003 | Module import failure detection | Low | Low | v2 |
| GOV-001 | JSON Schema formal versioning | Admin | Low | v2 |
| GOV-002 | Semantic control map cross-reference audit | Admin | Medium | v2 |
| OBS-001 | Automated determinism verification | Admin | High | v2 |
| OBS-002 | Observability storage consolidation | Admin | High | v3 |
| ARCH-001 | Unified assessment rule documentation | Architecture | Low | v2 |
| ARCH-002 | Influence track semantics clarification | Architecture | Medium | v2 |
| ARCH-003 | Multi-user mode architecture sketch | Architecture | High | v3 |
| ARCH-004 | Neural matching integration points | Architecture | High | v3 |
| DS-001 | DS-001 corpus coverage expansion | Data | High | v2+ |
| REPO-001 | Git integration for artifact tracking | Infrastructure | Medium | v2 |
| PERF-001 | Pipeline execution profiling | Performance | Low | v2 |
| UI-001 | User-facing explanation format validation | UX | Medium | v3 |

---

## Implementation Schedule

### Week 1 (2026-03-25 to 2026-03-31)
- [x] CRI-001: Unmatched-track bias (COMPLETED 2026-03-25)
- [x] CRI-005: Circular key distance (COMPLETED 2026-03-25 - verified already implemented)
- [x] CRI-004: Positive threshold validation (COMPLETED 2026-03-25)
- [x] CRI-002: Numeric threshold coupling (COMPLETED 2026-03-25)
- [x] HIGH-003: Undersized playlist warning/documentation (COMPLETED 2026-03-25)
- [x] HIGH-004: Profile limit constraint validation (COMPLETED 2026-03-25)

### Week 2 (2026-04-01 to 2026-04-07)
- [x] CRI-003: Weight normalization validation (COMPLETED 2026-03-25)
- [x] Update Chapter 3 with bias documentation (COMPLETED 2026-03-25)
- [x] Update Chapter 4 with undersized playlist caveat (COMPLETED 2026-03-25)
- [x] Integrated test suite run with all Tier 1 fixes (COMPLETED 2026-03-25; BL-013 PASS, BL-014 PASS 21/21)

### Week 3 (2026-04-08 to 2026-04-10)
- [ ] Final audit pass: re-run comprehensive pipeline checks
- [ ] Thesis document synchronization (all chapters reflect implemented mitigations)
- [ ] Lock down Chapter 3 and 4 for final submission

---

## Risk Mitigation Strategy

**If any Tier 1 fix cannot be completed by 2026-04-08:**
- Add explicit thesis caveat in Chapter 4 explaining the deferral
- Document in unresolved_issues.md with evidence of why it was postponed
- Add to Chapter 5 "Future Work" section

**Validation Approach:**
- Each fix must pass: (1) unit test, (2) BL-013 integration test, (3) BL-014 sanity check
- No fix is merged without documented evidence

---

## Cross-References

- **Audit Report**: [pipeline_audit_comprehensive_2026-03-25.md](pipeline_audit_comprehensive_2026-03-25.md)
- **Unresolved Issues**: [unresolved_issues.md](unresolved_issues.md)
- **Change Log**: [change_log.md](change_log.md)
- **Tier-1 Execution Log**: [tier1_hardening_execution_log_2026-03-25.md](tier1_hardening_execution_log_2026-03-25.md)
- **Implementation Notes**: `07_implementation/test_notes.md` and per-stage README files

---

## Sign-Off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Implementer | AI Assistant | 2026-03-25 | Prioritization + backlog creation |
| Review | (Thesis Author) | — | Pending |
| Approval | (Thesis Author) | — | Pending |

**Last Updated**: 2026-03-25 14:30 UTC
