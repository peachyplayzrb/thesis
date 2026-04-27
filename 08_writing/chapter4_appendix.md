# Chapter 4 Appendices: Infrastructure and Governance Details

## A4.1: Run-Config Profile and Configuration Authority

The implementation manages all configuration parameters (feature weights, constraints, filtering thresholds, constraint parameters, and execution settings) through a persistent run-config profile. This converts configuration from a convenience mechanism into a methodological instrument for supporting reproducibility and controllability testing.

### Configuration Structure

A run-config profile is a structured file (JSON or YAML format) that captures:

**Feature Weighting:**
- Weight for rhythmic/harmonic similarity component
- Weight for affective/intensity similarity component
- Weight for semantic/contextual similarity component
- Normalisation of weights so they sum to 1.0

**Candidate Shaping Thresholds:**
- Profile-similarity distance threshold (maximum allowed distance for candidate inclusion)
- Influence-track nomination boost (how much to relax threshold for nominated tracks)
- Metadata-exclusion categories (which track types to exclude by default)

**Assembly Constraints:**
- Minimum score admissibility threshold (no track below this score)
- Maximum consecutive artists (e.g., no same artist appears twice in a row)
- Maximum per-genre count (e.g., maximum 4 tracks per genre in a 10-track playlist)
- Diversity pressure setting (target entropy or feature-distribution variance)
- Novelty allowance budget (number of lower-scored tracks allowed for diversity)

**Execution Settings:**
- Target playlist size
- Random seed (if any stochastic elements are present — currently deterministic, so unused)
- Output verbosity and logging level
- Validation strictness mode

### Configuration as Evidence

The persistent run-config serves three roles:

1. **Reproducibility Authority:** By capturing all active parameters in a single immutable snapshot, the configuration becomes the definitive record of "what settings produced this playlist." Two runs under identical configuration should produce identical outputs; comparing configuration hashes immediately shows whether parametrization was identical.

2. **Controlled-Variation Basis:** Documented parameter changes between runs enable isolation of single-parameter effects. When a run-config differs from a baseline only in one field (e.g., diversity_pressure increased by 0.1), observed output differences can be confidently attributed to that single change rather than confounded by multiple simultaneous variations.

3. **Audit Trail:** The full config snapshot is embedded in the observability record (BL-009), so later reviewers can reconstruct exactly what settings were active during any specific run without requiring external documentation or manual reconstruction.

### Example Configuration (from run 2026-04-22)

```json
{
  "run_id": "RUN-CONFIG-20260422-121800-example",
  "feature_weights": {
    "rhythmic_harmonic": 0.20,
    "affective_intensity": 0.27,
    "semantic_contextual": 0.53
  },
  "candidate_shaping": {
    "profile_similarity_threshold": 1.5,
    "influence_track_boost": 0.3,
    "metadata_exclusions": ["live_version", "bonus_track"]
  },
  "assembly_constraints": {
    "min_score_threshold": 0.35,
    "max_consecutive_artist": 2,
    "max_per_genre": 4,
    "novelty_allowance_budget": 0,
    "target_playlist_size": 10
  },
  "execution": {
    "log_level": "info",
    "validation_mode": "strict"
  }
}
```

This configuration explicitly records every meaningful parameter. No defaults are implicit; the run record makes all settings visible. This supports both reproducibility verification (two runs with identical configs should produce identical results) and controlled-variation analysis (changing one parameter at a time isolates its effect).

---

## A4.2: Objective-Linked Tranche Gates (REB-M3)

The implementation includes three objective-linked tranche gates that validate whether design property coverage is present at three progression points in the implementation cycle. These are internal governance checks rather than thesis-facing evaluation, but are documented here for completeness.

### Gate Structure

Each gate operates as a binary pass/fail checkpoint over a subset of the implementation layers:

**Tranche 1 Gate (T1):** Validates intake and profile quality
- Check: Alignment uncertainty is surfaced (BL-003 emits match-rate statistics and reason codes)
- Check: Profile structure is inspectable (BL-004 profile is feature-based and traceable)
- Artefacts: bl003_ds001_spotify_summary.json, bl004_preference_profile.json

**Tranche 2 Gate (T2):** Validates candidate-space and scoring mechanisms
- Check: Candidate shaping is explicit (BL-005 emits retention/exclusion counts and pathways)
- Check: Scoring is decomposable (BL-006 emits per-component scores)
- Artefacts: bl005_candidate_diagnostics.json, bl006_score_summary.json

**Tranche 3 Gate (T3):** Validates assembly, explanation, and observability
- Check: Assembly constraints are visible (BL-007 emits constraint satisfaction and relaxation records)
- Check: Explanations are mechanism-linked (BL-008 payloads reference score contributors)
- Check: Run observability is complete (BL-009 emits full execution record with hashes)
- Artefacts: bl007_assembly_report.json, bl008_explanation_payloads.json, bl009_run_observability_log.json

### Gate Reporting

Each gate produces a binary report:

```json
{
  "gate_id": "REB-M3-TRANCHE-1",
  "generated_at_utc": "2026-04-22T12:19:00Z",
  "stage_checks": [
    {
      "stage": "BL-003",
      "check": "Alignment uncertainty surfaced",
      "status": "PASS",
      "evidence": "bl003_ds001_spotify_summary.json contains match_rate_validation and unmatched reason codes"
    },
    {
      "stage": "BL-004",
      "check": "Profile structure inspectable",
      "status": "PASS",
      "evidence": "bl004_preference_profile.json contains per-feature statistics and uncertainty markers"
    }
  ],
  "overall_verdict": "PASS"
}
```

### Role in Development vs. Thesis

These gates are **internal development governance**, not part of the thesis narrative. They serve as:
- Proof points that each design commitment from Chapter 3 has a corresponding implementation surface
- Checkpoints during the implementation cycle to ensure no design property is missing
- Evidence that the implementation is coherent and complete at each progression step

Chapter 4 (the main thesis chapter) focuses on evidence surfaces and artefacts themselves. Chapter 5 evaluation addresses whether those surfaces meet intended quality criteria. These gates are the intermediate layer showing that the implementation is structurally complete relative to design.

---

## Summary

These appendices document infrastructure details (configuration authority and governance gates) that support the main thesis argument but are not part of the central narrative. Readers interested in reproducibility mechanics and development-phase governance can consult these sections; the main Chapter 4 remains focused on implementation architecture and evidence surfaces.
