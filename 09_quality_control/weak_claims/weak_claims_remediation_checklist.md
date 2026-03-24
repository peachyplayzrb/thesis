# Chapter 2 Weak Claims: Complete Reference & Remediation Checklist

## All 17 Weak Claims from Audit (weak_support status)

| # | Paper | Claim (snippet) | Score | Ch 2 Location | Thesis Impact | Status |
|---|-------|-----------------|-------|---------------|---------------|--------|
| **1** | Knijnenburg 2012 | Non-expert explanation understandability | 49.02 | 2.3 ~70 | **HIGH** — Transparency core | 🔴 Needs rewording |
| **2** | Schweiger 2025 | Metric selection as configurable parameter | 47.05 | 2.2 ~45 | **HIGH** — Metric selection core | 🔴 Refocus to music evidence |
| **3** | Schweiger 2025 | Distance-function dependence in similarity | 44.86 | 2.2 ~47 | **HIGH** — Metric selection core | 🔴 Reframe as operative finding |
| **4** | Papadakis 2021 | Staged entity resolution process | 46.52 | 2.7 ~180 | **HIGH** — Entity resolution core | 🟡 Likely correct; verify source |
| **5** | Jin et al. 2020 | Traceable control parameter downstream effects | 48.41 | 2.3 ~140 | **HIGH** — Controllability core | 🔴 Split claim by source (Jin + Nauta) |
| **6** | Barlaug 2021 | Neural matching traceability trade-off | 47.81 | 2.7 ~200 | **HIGH** — Feature vs neural core | 🔴 Reframe as design choice |
| 7 | Allam et al. 2018 | Staged entity resolution (same claim as #4) | 47.66 | 2.7 ~180 | **HIGH** — Entity resolution core | 🟡 Likely correct w/ #4 fix |
| 8 | Bonnin & Jannach 2015 | Playlist trade-offs coherence/novelty/diversity | 48.09 | 2.5 ~150 | **MEDIUM** — Playlist design | 🟡 Add specific trade-off evidence |
| 9 | Ferraro et al. 2018 | Playlist trade-offs (same as #8) | 46.22 | 2.5 ~150 | **MEDIUM** — Playlist design | 🟡 Same fix as #8 |
| 10 | Vall et al. 2019 | Playlist trade-offs (same as #8, #9) | 47.32 | 2.5 ~150 | **MEDIUM** — Playlist design | 🟡 Same fix as #8 |
| 11 | Zamani et al. 2019 | Candidate pool handling importance | 41.62 | 2.4 ~120 | **MEDIUM** — Candidate generation | 🔴 Verify or reword loosely |
| 12 | Anelli et al. 2021 | Reproducibility proof via run context | 45.88 | 2.3 ~155 | **HIGH** — Reproducibility core | 🟡 Weak but likely defensible |
| 13 | Bellogin 2021 | Reproducibility same as #12 | 47.96 | 2.3 ~155 | **HIGH** — Reproducibility core | 🟡 Same fix as #12 |
| 14 | Liu et al. 2025 | Neural performance claims | 48.96 | 2.6 ~165 | **MEDIUM** — Comparator context | 🟡 Soften comparator claims |
| 15 | Liu (Multimodal) 2025 | Neural performance claims (same as #14) | 48.58 | 2.6 ~165 | **MEDIUM** — Comparator context | 🟡 Same fix as #14 |
| 16 | Ru et al. 2023 | Music4All corpus suitability evidence | 47.30 | 2.5 ~105 | **MEDIUM** — Data selection | 🟡 Verify or soften scope claim |
| 17 | Sotirou et al. 2025 | Explanations expose decision pathway | 49.73 | 2.7 ~240 | **HIGH** — Explanation fidelity | 🟡 Strengthen with XAI sources |

---

## Prioritized Action Plan

### 🔴 CRITICAL (Fix First) — 6 claims
These directly undermine the thesis narrative if left unresolved. Estimated time: 2–3 hours.

1. **Priority 1 — Knijnenburg (Explanation Understandability)**
   - Current weakness: Claims technical-fidelity vs non-expert divide not supported by PDF
   - Action: Replace with Tsai (2018) OR reword to match Knijnenburg's UX framework
   - Effort: 20 min — 1 claim, 1 location
   - Verification: Check Tsai abstract for "Explaining...to Casual Users" language

2. **Priority 2 & 3 — Schweiger (Metric Selection + Distance Dependence)**
   - Current weakness: Claims about general design practice not supported; Schweiger is music-specific empirical finding
   - Action: Separate claim; use Fkih for principle, Schweiger for music evidence
   - Effort: 45 min — 2 claims, 2 locations (can be combined into 1 paragraph)
   - Verification: Read Fkih abstract + Schweiger paper_note

3. **Priority 5 — Jin et al. (Traceable Control Effects)**
   - Current weakness: Dual claim (behavior + documentation) assigned to single source; documentation principle from Nauta
   - Action: Split into two sentences; first half stays with Jin (behavior), second half to Nauta (evaluation)
   - Effort: 30 min — 1 claim rewritten as 2 sentences
   - Verification: Check Jin section on interface behavior + Nauta on evaluation methods

4. **Priority 6 — Barlaug (Neural Trade-off)**
   - Current weakness: Trade-off claim (traceability vs transparency) is author inference, not in source
   - Action: Reframe as author's design decision supported by Barlaug's background on neural methods
   - Effort: 25 min — 1 claim, reword paragraph
   - Verification: Check Barlaug abstract + paper_note on "complexity"

### 🟡 MODERATE (Verify & Decide) — 7 claims
These are likely defensible but need verification or minor rewording. Estimated time: 1–2 hours.

5. **Priority 4 — Papadakis (Staged Entity Resolution)**
   - Status: Likely correct in substance; audit couldn't find textual evidence
   - Action: Manually verify against PDF Section 2–3, then cite exact section if found
   - Effort: 20 min — Find source quote
   - Decision: Keep as-is if verified, or reword if not explicitly stated as unified "staged process"

6. **Priorities 8, 9, 10 — Playlist Trade-offs (3 papers, 1 claim)**
   - Current weakness: Claim about "improving one dimension reduces another unless explicit" appears in audit but sources don't have strong textual match
   - Action: Keep claim; add specific example evidence (e.g., "Vall found that when diversity improved, coherence sensitivity increased")
   - Effort: 30 min — Find stronger quote from one of three papers, cite that one more prominently
   - Decision: Likely defensible; just needs stronger textual anchor

7. **Priority 12, 13 — Reproducibility (2 papers, same claim)**
   - Current weakness: Weak match on "preserving sufficient run context"
   - Action: Check Anelli abstract for "configuration" language; reword to match
   - Effort: 20 min — 1 unique reword
   - Decision: Defensible principle; just needs rewording for audit alignment

8. **Priorities 14, 15 — Neural Performance Claims (2 papers, comparator context)**
   - Current weakness: Comparator claims are intentionally softer (exploratory context)
   - Action: Soften language further if needed ("higher performance claimed in data-rich conditions" rather than definitive statements)
   - Effort: 15 min — Soften 2 claims with hedging language
   - Decision: Okay if marked as comparator context; keep as-is if that framing is clear

9. **Priority 16 — Music4All Corpus Evidence**
   - Current weakness: Claim about "suitability under project scope constraints" is author interpretation
   - Action: Reword to "provides evidence for multimodal music feature viability" without explicit scope claim
   - Effort: 15 min — Reword 1 claim
   - Decision: Defensible; just needs scope tempering

10. **Priority 17 — Sotirou Explanation Principle**
    - Current weakness: Weak textual match on "explanations expose decision pathway"
    - Action: Strengthen by adding Zhang & Chen (2020) as primary source, use Sotirou as music-domain support
    - Effort: 20 min — Add citation with split credit
    - Decision: Principle is sound; just needs secondary evidence

---

## Implementation Checklist

### PHASE 1: Critical Fixes (Priority 1–6)
- [ ] Fix Knijnenburg claim (Priority 1) — Add Tsai or reword
- [ ] Fix Schweiger metric claims (Priorities 2–3) — Separate principle from music evidence
- [ ] Fix Jin controllability claim (Priority 5) — Split between Jin (behavior) + Nauta (eval)
- [ ] Fix Barlaug neural claim (Priority 6) — Reframe as design rationale
- [ ] Verify Papadakis entity resolution (Priority 4) — Check PDF for staged process statement

### PHASE 2: Moderate Fixes (Priorities 4–10)
- [ ] Verify/update Papadakis citation with exact section (Priority 4)
- [ ] Add stronger evidence quotes for playlist trade-offs (Priorities 8–10)
- [ ] Soften neural performance claims for comparator context (Priorities 14–15)
- [ ] Reword Music4All scope claim (Priority 16)
- [ ] Add Zhang & Chen to Sotirou explanation claim (Priority 17)
- [ ] Verify reproducibility rewording (Priorities 12–13)

### PHASE 3: Re-audit & Final Check
- [ ] Run verbatim audit on revised Chapter 2
- [ ] Verify improvement in weak_support scores
- [ ] Document final results in audit summary

---

## Quick Reference: Which Claims Appear Multiple Times

**Entity Resolution (Staged Process)** — Priorities 4 & 7
- Allam et al. (2018) + Papadakis et al. (2021) cite the same claim
- **Fix once, both resolve** — Just need to verify source once

**Playlist Trade-offs** — Priorities 8, 9, 10
- Ferraro (2018), Vall (2019), Bonnin & Jannach (2015) all cite same claim about coherence/diversity/novelty trade-offs
- **Fix once (find best evidence), cite all three** — Strengthen textual anchor rather than rewrite three times

**Neural Performance** — Priorities 14, 15
- Liu (2025) appears twice in source set with same claim
- **Fix once** — Apply same hedging/framing to both Liu references

**Reproducibility** — Priorities 12, 13
- Anelli (2021) + Bellogin (2021) cite same reproducibility claim
- **Fix once, both improve** — Same rewording applies to both

---

## Estimated Effort Summary

| Phase | Claims | Effort | Priority |
|-------|--------|--------|----------|
| Phase 1: Critical | 6 claims | ~2 hrs | DO FIRST |
| Phase 2: Moderate | 11 claims (some duplicates) | ~1.5 hrs | THEN THIS |
| Phase 3: Re-audit | 1 full run | ~10 min | FINALLY |
| **TOTAL** | **17 claims** | **~3.5 hrs** | **Complete before submission review** |

---

## Notes on Thesis Impact

**HIGH Impact** (6 claims):
- Knijnenburg explanation
- Schweiger metrics (both)
- Papadakis entity resolution
- Jin controllability
- Barlaug neural trade-off

👉 **Must be resolved** — These are central to thesis narrative

**MEDIUM Impact** (8 claims):
- Playlist trade-offs
- Candidate handling
- Reproducibility
- Comparator context (neural)
- Corpus selection
- Explanation fidelity principle

👉 **Should be resolved** — Improves robustness, less critical to core narrative

---

## Success Criteria

After Phase 1–2 rewording:
- [ ] All 6 HIGH-impact claims score ≥ 60 in re-audit
- [ ] All MEDIUM-impact claims score ≥ 50 in re-audit
- [ ] No claim remains at weak_support (<50)
- [ ] All duplicated claims (entity resolution, playlist trade-offs, reproducibility) resolve together

---

## Additional Verification Needed

Before finalizing, manually spot-check these sources for exact language:
1. **Tsai & Brusilovsky (2018)** — "casual users" language for non-expert claim
2. **Fkih (2022)** — "configurable parameter" or "design parameter" language for metric claim
3. **Papadakis (2021)** — "staged" language for entity resolution framework
4. **Zhang & Chen (2020)** — "faithful explanation" vs "interpretable model" distinction for Sotirou upgrade

All paper PDFs are located in: `10_resources/papers/` and `10_resources/previous_drafts/lit_review_resource_pack/`
