id: P-065
citation_key: schweiger_impact_2025
full_reference: Schweiger, H., Parada-Cabaleiro, E., and Schedl, M. (2025) The impact of playlist characteristics on coherence in user-curated music playlists. EPJ Data Science, 14(1), 24. doi:10.1140/epjds/s13688-025-00531-3.
document_status: processed_paper_note
confidence: high

research_problem:
Formalize and analyze playlist coherence under user-curated playlist settings, including causal effects of playlist attributes across feature-based distance definitions.

method_or_system_type:
Playlist-coherence measurement framework with distance-based objective design and causal analysis on large user-curated playlist data.

key_findings:
- Coherence is operationalized as a distance-based playlist objective with standardized comparability across feature dimensions.
- Coherence outcomes vary with playlist characteristics (for example length, edits, popularity, collaboration).
- Different distance-feature constructions can produce different coherence values and interpretation outcomes.

limitations:
- Focuses on coherence-analysis framing rather than same-model, same-feature, distance-function-only ablations.
- Does not by itself establish deterministic similarity-function effects on all ranking objectives (for example R-precision or NDCG).

relevance_to_thesis:
Strengthens playlist-objective metric-sensitivity evidence in music domain and supports explicit distance-metric governance in deterministic pipeline design.

supported_architecture_layer:
- Playlist Assembly Layer
- Scoring and Similarity Layer
- Evaluation and Comparator Framing

theme_mapping:
- playlist_generation
- similarity_measures
- evaluation_protocol_rigor

gap_implications:
Further narrows the playlist-objective evidence gap by showing that playlist-level objective values are distance-definition-dependent.

design_implications:
- Treat coherence/diversity objective definitions as explicit, configurable design choices.
- Document which distance-feature choices were used when reporting playlist-level outcomes.

chapter_use_cases:
- Chapter 2
- Chapter 5

linked_files:
- 03_literature/literature_gap_tracker.md
- 09_quality_control/claim_evidence_map.md
- 09_quality_control/citation_checks.md
