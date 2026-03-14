id: P-035
citation_key: binette_almost_2022
full_reference: (Almost) all of entity resolution. Science Advances (2022). doi:10.1126/sciadv.abi8021.
document_status: processed_paper_note
confidence: medium

research_problem:
Summarize the broad methodological landscape of entity resolution and clarify foundational problem structure.

method_or_system_type:
Cross-domain entity-resolution synthesis/position paper

key_findings:
- Entity resolution performance depends strongly on pipeline design choices and data assumptions.
- Blocking, matching, and evaluation strategy interactions are central to practical system behavior.
- Comprehensive framing helps avoid simplistic one-step matching assumptions.

limitations:
- Not music-domain specific.
- Does not directly evaluate ISRC-based music alignment workflows.

relevance_to_thesis:
Strengthens the theoretical basis for staged metadata alignment beyond naive fuzzy matching.

supported_architecture_layer:
- Track Alignment Layer

theme_mapping:
- entity_resolution
- alignment_method_tradeoffs

gap_implications:
Improves general alignment-method support; music-specific reliability evidence is still needed.

design_implications:
- Treat alignment as a multi-stage process with explicit filtering and matching controls.
- Keep alignment diagnostics visible for auditability.

chapter_use_cases:
- Chapter 2
- Chapter 3

linked_files:
- 09_quality_control/claim_evidence_map.md
- 03_literature/literature_gap_tracker.md
