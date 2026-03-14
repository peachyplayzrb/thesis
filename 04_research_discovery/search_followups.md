# Search Follow-ups

DOCUMENT STATUS: active
CONFIDENCE: medium
ROLE: prioritized evidence acquisition plan for gap closure
LAST_UPDATED: 2026-03-13

## Priority Order (Highest Impact First)
1. Music-domain track alignment reliability evidence
2. Music-domain similarity-metric comparison evidence
3. Recommender pipeline observability/logging schema evidence
4. Lightweight comparator/ablation evidence for evaluation framing

## Targeted Follow-up Checklist
| Priority | Gap to close | Why it matters | Claim links | Chapter impact | Minimum evidence target |
| --- | --- | --- | --- | --- | --- |
| P0 | Music-specific ISRC/metadata alignment reliability | Current support is mostly cross-domain entity resolution; assessors may challenge transfer validity | C-CLM-017, C-CLM-019 | Chapter 2, Chapter 3, Chapter 5 | 2 strong sources (>=1 music-domain empirical/benchmark) |
| P1 | Music-domain similarity metric sensitivity | Deterministic scoring justification currently has limited direct music-playlist metric support | C-CLM-016 | Chapter 2, Chapter 3, Chapter 5 | 1 to 2 sources with explicit metric-comparison findings |
| P1 | Pipeline observability/logging instrumentation detail | Supports concrete reproducibility/inspectability engineering, not only methodology-level claims | C-CLM-018 | Chapter 3, Chapter 4, Chapter 5 | 1 source with schema/trace-level implementation guidance |
| P2 | Scope-safe comparator/ablation evidence | Strengthens evaluation credibility without violating MVP scope | C-CLM-014, C-CLM-016, C-CLM-020 | Chapter 4, Chapter 5 | 1 source supporting simple baseline/ablation evaluation practice |

## Search Query Pack
Use these as starting strings in Scholar/ACM/IEEE/Scopus and log outcomes in `04_research_discovery/paper_search_log.md`.

### Q1: Music alignment reliability (P0)
- "music metadata entity resolution ISRC benchmark"
- "track matching across music catalogs ISRC title artist"
- "music record linkage remaster version ambiguity"
- "playlist dataset track identity resolution"

### Q2: Similarity metric evidence (P1)
- "music recommendation similarity metric comparison playlist"
- "audio feature similarity measures playlist continuation"
- "music recommender cosine euclidean correlation evaluation"

### Q3: Observability/logging schema (P1)
- "recommender system experiment logging schema reproducibility"
- "machine learning pipeline observability recommendation tracing"
- "recommender evaluation protocol configuration reporting"

### Q4: Comparator/ablation design (P2)
- "recommender systems ablation study best practices"
- "transparent recommender evaluation baseline methodology"

## Inclusion Rules
- Include papers with direct relevance to thesis scope (music recommendation, playlist generation, alignment, reproducibility, inspectability).
- Prefer peer-reviewed sources over blogs/grey literature.
- Prefer studies with empirical setup details, not only conceptual commentary.
- Keep scope locked: no requirement to add deep-model baseline to core artefact.

## Completion Criteria
- P0 complete when at least one music-domain alignment benchmark/reliability source is ingested and mapped.
- P1 complete when at least one music-domain similarity comparison and one observability-instrumentation source are ingested and mapped.
- P2 partially strengthened by `zhu_bars_2022` and `ferrari_dacrema_troubling_2021`; keep open until one source with explicit ablation/baseline design guidance is mapped.
- All new papers must be processed through `03_literature/paper_notes/`, `03_literature/source_index.csv`, and `09_quality_control/claim_evidence_map.md`.

