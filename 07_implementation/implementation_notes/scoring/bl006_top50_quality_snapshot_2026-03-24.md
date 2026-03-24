# BL-006 Top-50 Quality Snapshot

**Date:** 2026-03-24
**Stage:** BL-006
**Source Artifact:** 07_implementation/implementation_notes/scoring/outputs/bl006_scored_candidates.csv
**Related Run:** BL006-SCORE-20260324-190145-197533

---

## 1. Scope
This snapshot summarizes distribution and contribution behavior for the top-50 ranked candidates after the bounded BL-006 retune.

## 2. Score Distribution (Top-50)
- max: 0.817654
- min: 0.672124
- mean: 0.700933
- median: 0.689827
- p10: 0.675414
- p90: 0.737008

Interpretation:
- Top-50 scores are dense (narrow band), indicating ranking sensitivity to relatively small contribution differences in upper ranks.

## 3. Contribution Balance (Top-50)
- numeric mean contribution: 0.390315
- semantic mean contribution: 0.310617
- rows with numeric > semantic: 41/50
- rows with semantic > numeric: 9/50

Interpretation:
- The retuned BL-006 now shows clear numeric-leading behavior in top-50 while preserving semantic signal.

## 4. Semantic Concentration Check
Lead-genre distribution (top-50):
- classic rock: 21
- pop: 20
- rock: 8
- progressive rock: 1

Matched vocabulary breadth (top-50):
- unique matched genres: 8
- unique matched tags: 10

Interpretation:
- Semantic breadth exists but lead-genre concentration is high around classic rock/pop.

## 5. Top-10 Track IDs (Reference)
- 8WnHV12FDAeaQwkd
- 9B6dNFjeE90pp4x6
- C0mhpBhouqyLmYSK
- m17iB8yxNZn3tqdE
- df0JOlTEeZCAVz1W
- 9qCc2lNrSBbmtjCj
- CaR8UnowNJUR5Dib
- YfV01HfNXWAFfgtm
- A8Q9gX4RokaFDMOP
- N1yOEQ8Rf8ljdHmf

## 6. Assessment
- Numeric-vs-semantic balance objective is currently satisfied for top ranks.
- The next quality risk to monitor is topical concentration (genre cluster tightness), not semantic-overlap overweighting.
