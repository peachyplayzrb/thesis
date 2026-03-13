id: P-001
citation_key: zhang_explainable_2020
full_reference: Zhang, Y. and Chen, X. (2020) Explainable Recommendation: A Survey and New Perspectives. Foundations and Trends in Information Retrieval, 14(1), 1-101. doi:10.1561/1500000066.
document_status: processed_paper_note
confidence: medium

research_problem:
How explainable recommendation methods are categorized, what information sources/mechanisms they use, and how explainability should be evaluated beyond pure ranking performance.

method_or_system_type:
Survey/taxonomy paper (5W framing, timeline, 2D taxonomy by explanation source and algorithmic mechanism).

key_findings:
- Explainable recommendation spans both post-hoc and intrinsically explainable/transparent models.
- Explainability goals include transparency, trust, persuasiveness, effectiveness, and debugging support.
- Different explanation sources/mechanisms imply different trade-offs for fidelity and usability.

limitations:
- Survey scope is broad across domains, not specific to deterministic music playlist pipelines.
- Taxonomy guidance does not directly provide engineering blueprint for cross-source alignment or observability logging.

relevance_to_thesis:
High relevance for defining transparent-by-design choices and for distinguishing faithful scoring-derived explanations from post-hoc rationalizations.

theme_mapping:
- transparency_by_design
- explainable_recommenders
- explanation_faithfulness
- evaluation_of_explainable_systems

gap_implications:
Strengthens the need to justify faithful explanation generation tied to actual scoring traces.

design_implications:
- Choose explanation mechanisms directly linked to deterministic scoring internals.
- Define explanation evaluation criteria explicitly (not only accuracy metrics).

chapter_use_cases:
- Chapter 2: explainable recommendation landscape and taxonomy.
- Chapter 3: rationale for transparent scoring/explanation coupling.

linked_files:
- 03_literature/literature_gap_tracker.md
- 09_quality_control/claim_evidence_map.md
- 05_design/architecture.md
