id: P-029
citation_key: allam_improved_2018
full_reference: Improved suffix blocking for record linkage and entity resolution. Data and Knowledge Engineering (2018). doi:10.1016/j.datak.2018.07.005.
document_status: processed_paper_note
confidence: medium

research_problem:
Improve scalable record linkage/entity resolution by reducing candidate comparisons while preserving matching quality.

method_or_system_type:
Entity resolution method paper (blocking optimization)

key_findings:
- Blocking strategy design strongly affects linkage efficiency and downstream matching quality.
- Improved suffix blocking can reduce unnecessary comparisons versus naive pairwise matching.
- Practical linkage pipelines require explicit handling of candidate generation trade-offs.

limitations:
- Not music-domain specific.
- Does not directly evaluate ISRC-centric music identifier workflows.

relevance_to_thesis:
Provides direct methodological grounding for metadata-fallback matching stages in track alignment.

supported_architecture_layer:
- Track Alignment Layer

theme_mapping:
- entity_resolution
- metadata_matching_reliability

gap_implications:
Strengthens general linkage-method evidence but leaves music-specific identifier ambiguity and ISRC failure behavior only partially resolved.

design_implications:
- Treat metadata fallback matching as a staged candidate-generation and filtering pipeline.
- Log candidate counts and pruning thresholds for auditability.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md