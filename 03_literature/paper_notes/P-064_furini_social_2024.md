id: P-064
citation_key: furini_social_2024
full_reference: Furini, M., and Fragnelli, F. (2024) Social music discovery: an ethical recommendation system based on friend’s preferred songs. Multimedia Tools and Applications, 84(14), 13469-13483. doi:10.1007/s11042-024-19505-0.
document_status: processed_paper_note
confidence: medium

research_problem:
Design an ethically oriented social music recommendation approach and evaluate playlist quality from user ratings under different recommendation variants.

method_or_system_type:
Music playlist recommendation system with controlled similarity-metric check in a deterministic feature-space pipeline.

key_findings:
- The system computes track similarity in an explicit feature space and reports a direct Euclidean-versus-cosine comparison.
- Under the tested setup, Euclidean and cosine distance produced no significant difference in observed playlist outcomes.
- User-level acceptance varied by exploration preference, reinforcing audience-dependent interpretation of playlist quality.

limitations:
- Evidence is based on a small-scale user-study setting and does not provide large benchmark ranking-metric ablations.
- Reported metric-comparison result is mostly qualitative/insignificant rather than a broad causal map across datasets.

relevance_to_thesis:
Provides direct music-domain evidence for the V-ACT-002 target because it explicitly tests deterministic similarity-function alternatives within one pipeline.

supported_architecture_layer:
- Scoring and Similarity Layer
- Playlist Assembly Layer
- Evaluation and Comparator Framing

theme_mapping:
- similarity_measures
- playlist_generation
- evaluation_protocol_rigor

gap_implications:
Narrows the deterministic similarity-function isolation gap by adding one direct metric-swap case, while still leaving limited external generalization.

design_implications:
- Keep similarity-function choice explicit and testable in the scoring module.
- Report negative/no-difference metric-comparison results as valid evidence, not only positive gains.

chapter_use_cases:
- Chapter 2
- Chapter 5

linked_files:
- 03_literature/literature_gap_tracker.md
- 09_quality_control/claim_evidence_map.md
- 09_quality_control/citation_checks.md
