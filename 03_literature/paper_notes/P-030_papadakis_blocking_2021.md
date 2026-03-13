id: P-030
citation_key: papadakis_blocking_2021
full_reference: Blocking and Filtering Techniques for Entity Resolution: A Survey. ACM Computing Surveys (2021). doi:10.1145/3377455.
document_status: processed_paper_note
confidence: high

research_problem:
Synthesize blocking/filtering approaches for entity resolution to manage scale while maintaining linkage effectiveness.

method_or_system_type:
Systematic/survey paper on entity resolution blocking and filtering techniques

key_findings:
- Blocking/filtering is central to practical entity resolution pipelines.
- Different blocking families present precision-recall-efficiency trade-offs.
- Evaluation should report both effectiveness and computational behavior.

limitations:
- Domain-agnostic survey; no direct music dataset ISRC benchmarking.

relevance_to_thesis:
Directly supports alignment-layer design choices for metadata fallback and ambiguity handling mechanics.

supported_architecture_layer:
- Track Alignment Layer
- Observability and Audit Layer

theme_mapping:
- entity_resolution
- cross_dataset_alignment

gap_implications:
Reduces the generic alignment-method gap, but still leaves music-identifier specific reliability (ISRC plus version/remaster ambiguity) under-supported.

design_implications:
- Explicitly separate blocking, candidate generation, and final matching phases.
- Capture alignment-stage diagnostics for reproducibility and troubleshooting.

chapter_use_cases:
- Chapter 2
- Chapter 3 (where relevant)

linked_files:
- 05_design/literature_architecture_mapping.md
- 03_literature/literature_gap_tracker.md