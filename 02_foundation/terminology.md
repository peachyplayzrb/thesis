# Terminology

## Pipeline Terms

- Ingestion (BL-001, BL-002): acquiring and validating raw listening-history data into normalized event records.
- Alignment or Preference Signal Construction (BL-003): cross-source transformation of imported events into auditable seed signals; current BL-020 path uses Last.fm semantic enrichment with explicit status capture.
- Preference Profile (BL-004): deterministic aggregation of seed signals into a user representation used for retrieval and scoring.
- Candidate Retrieval and Filtering (BL-005): deterministic narrowing of the candidate corpus before scoring.
- Scoring (BL-006): deterministic similarity and component-based ranking of retained candidates.
- Playlist Assembly (BL-007): rule-based construction of final playlist outputs from ranked candidates.
- Transparency (BL-008): explanation artifacts linking outputs to scoring components and rule effects.
- Observability (BL-009): run-level execution logs, diagnostics, and traceability artifacts.
- Reproducibility (BL-010): repeated-run consistency checks under fixed inputs/configuration.
- Controllability (BL-011): parameter/input variation checks to validate interpretable downstream effects.

## Data Terms

- DS-002: active integrated candidate corpus (`MSD subset + Last.fm tags`) used for current implementation runs.
- MusicBrainz fields: optional metadata fields present in DS-002 artifacts but not currently used in active pipeline scoring/filtering logic.
- Music4All or Onion: historical/baseline corpus references; not the active BL-020 canonical candidate dataset.

## Status Terms

- Active: currently implemented and used by the running pipeline.
- Deferred: approved/planned but intentionally not implemented yet.

