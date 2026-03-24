# Artefact Refinement Spec

Status: working implementation spec
Date: 2026-03-24
Scope: pipeline artefact only; website/UI intentionally excluded

## 1. Purpose

This document defines the next refinement step for the thesis artefact itself.

The core pipeline BL-004 to BL-009 already exists and produces deterministic outputs. The main refinement gap is not missing stages, but a weak control contract:

1. control surfaces are fragmented across input artefacts, environment variables, and controllability scenarios
2. user intent is not represented as a first-class run artefact
3. source-scope control is documented as required but still deferred
4. influence tracks exist in architecture and tests, but not as a clean stable run-time contract

The refinement goal is to make the artefact easier to explain, easier to control, and easier to audit.

## 2. Current Control Inventory

### 2.1 Upstream Input Composition

Current effective controls:

1. which listening events are present in the aligned input artefact
2. whether influence tracks are present
3. which interaction types are included
4. which candidate dataset is active

Current implementation state:

1. this control surface is real, but largely implicit
2. it is mostly exercised through input artefact selection and controllability scenarios
3. it is not yet normalized into a canonical run configuration object

Primary evidence:

1. `07_implementation/implementation_plan.md`
2. `05_design/architecture.md`
3. `07_implementation/implementation_notes/controllability/run_bl011_controllability_check.py`

### 2.2 BL-004 Profile Construction Controls

Current explicit controls:

1. `BL004_TOP_TAG_LIMIT`
2. `BL004_TOP_GENRE_LIMIT`
3. `BL004_TOP_LEAD_GENRE_LIMIT`
4. `BL004_USER_ID`

What they currently control:

1. the size of the retained semantic profile summary
2. the breadth of top tags and genres used downstream
3. the user identifier associated with the profile run

Important limitation:

1. influence tracks affect BL-004 indirectly through input events, not through a dedicated BL-004 control group

Primary evidence:

1. `07_implementation/implementation_notes/profile/build_bl004_preference_profile.py`

### 2.3 BL-005 Retrieval Controls

Current explicit controls:

1. `BL005_PROFILE_TOP_LEAD_GENRE_LIMIT`
2. `BL005_PROFILE_TOP_TAG_LIMIT`
3. `BL005_PROFILE_TOP_GENRE_LIMIT`
4. `BL005_SEMANTIC_STRONG_KEEP_SCORE`
5. `BL005_SEMANTIC_MIN_KEEP_SCORE`
6. `BL005_NUMERIC_SUPPORT_MIN_PASS`

What they currently control:

1. how much of the profile is exposed to candidate filtering
2. how strict semantic evidence must be before retention
3. how much numeric support is needed when semantic evidence is weaker

Important limitation:

1. numeric thresholds for tempo, key, mode, and duration exist in the script, but are not exposed as equivalent first-class configuration fields

Primary evidence:

1. `07_implementation/implementation_notes/retrieval/build_bl005_candidate_filter.py`

### 2.4 BL-006 Scoring Controls

Current explicit controls:

1. `BL006_COMPONENT_WEIGHTS_JSON`
2. `BL006_NUMERIC_THRESHOLDS_JSON`

What they currently control:

1. relative weight of semantic and numeric scoring components
2. tolerance thresholds for numeric similarity calculations

Current strength:

1. this is the strongest ranking-behavior control surface in the current pipeline

Primary evidence:

1. `07_implementation/implementation_notes/scoring/build_bl006_scored_candidates.py`

### 2.5 BL-007 Playlist Assembly Controls

Current explicit controls:

1. `BL007_TARGET_SIZE`
2. `BL007_MIN_SCORE_THRESHOLD`
3. `BL007_MAX_PER_GENRE`
4. `BL007_MAX_CONSECUTIVE`

What they currently control:

1. playlist length
2. final admission strictness
3. genre diversity cap
4. consecutive repetition tolerance

Primary evidence:

1. `07_implementation/implementation_notes/playlist/build_bl007_playlist.py`

### 2.6 BL-008 Transparency Controls

Current explicit control:

1. `BL008_TOP_CONTRIBUTOR_LIMIT`

What it currently controls:

1. explanation depth, not recommendation behavior

Primary evidence:

1. `07_implementation/implementation_notes/transparency/build_bl008_explanation_payloads.py`

### 2.7 BL-009 Observability Controls

Current explicit control:

1. `BL009_DIAGNOSTIC_SAMPLE_LIMIT`

What it currently controls:

1. logging and diagnostic sample depth, not recommendation behavior

Primary evidence:

1. `07_implementation/implementation_notes/observability/build_bl009_observability_log.py`

## 3. Missing Or Weak Controls

### 3.1 Missing First-Class Run Intent

Current problem:

1. the pipeline has outputs for profile, retrieval, scoring, assembly, transparency, and observability
2. it does not have a canonical artefact that records the intended run behavior before execution

Required refinement:

1. add a stable run-intent artefact as a primary input to execution

This artefact should record:

1. selected source scope
2. included interaction types
3. selected influence tracks
4. profile controls
5. retrieval controls
6. scoring controls
7. assembly controls
8. transparency controls
9. observability controls

### 3.2 Missing Source-Scope Control Contract

Current problem:

1. user-selectable source scope is explicitly identified as deferred work
2. the thesis state already describes it as desirable, but it is not implemented as part of the artefact contract

Required refinement:

1. implement BL-021 at the artefact level before treating it as a completed system capability

Primary evidence:

1. `07_implementation/backlog.md`
2. `00_admin/thesis_state.md`

### 3.3 Influence Tracks Are Not Formalized Enough

Current problem:

1. influence tracks clearly exist in architecture, controllability testing, and synthetic assets
2. they do not yet exist as a stable top-level configuration object for real runs

Required refinement:

1. formalize influence tracks in the canonical run config and downstream observability outputs

Primary evidence:

1. `05_design/architecture.md`
2. `07_implementation/implementation_plan.md`
3. `07_implementation/implementation_notes/controllability/run_bl011_controllability_check.py`

### 3.4 Control Naming Is Too Script-Centric

Current problem:

1. most controls are named as environment variable overrides
2. this is sufficient for engineering execution, but weak for artefact explanation and thesis defence

Required refinement:

1. group controls into semantic layers rather than stage-local env variables only

Recommended groups:

1. input composition controls
2. profile shaping controls
3. candidate selection controls
4. ranking controls
5. playlist behavior controls
6. explanation depth controls
7. observability depth controls

## 4. Proposed Canonical Run Configuration

The refined artefact should introduce a single canonical configuration file for each run.

Suggested location:

1. `07_implementation/implementation_notes/run_config/`

Suggested filename pattern:

1. `run_intent_<timestamp>.json`
2. `run_effective_config_<timestamp>.json`

Recommended structure:

```json
{
  "run_id": "RUN-INTENT-YYYYMMDD-HHMMSS-ffffff",
  "generated_at_utc": "2026-03-24T00:00:00Z",
  "input_scope": {
    "source_family": "spotify_api_export",
    "include_top_tracks": true,
    "top_time_ranges": ["short_term", "medium_term", "long_term"],
    "saved_tracks_limit": null,
    "include_saved_tracks": true,
    "include_playlists": true,
    "playlists_limit": null,
    "playlist_items_per_playlist_limit": null,
    "include_recently_played": true,
    "recently_played_limit": 50
  },
  "interaction_scope": {
    "include_interaction_types": ["history", "influence"]
  },
  "influence_tracks": {
    "enabled": true,
    "track_ids": [],
    "source": "manual_or_imported_selection"
  },
  "profile_controls": {
    "top_tag_limit": 10,
    "top_genre_limit": 10,
    "top_lead_genre_limit": 10
  },
  "retrieval_controls": {
    "profile_top_tag_limit": 10,
    "profile_top_genre_limit": 8,
    "profile_top_lead_genre_limit": 6,
    "semantic_strong_keep_score": 2,
    "semantic_min_keep_score": 1,
    "numeric_support_min_pass": 1,
    "numeric_thresholds": {
      "tempo": 20.0,
      "key": 2.0,
      "mode": 0.5,
      "duration_ms": 45000.0
    }
  },
  "scoring_controls": {
    "component_weights": {
      "tempo": 0.20,
      "duration_ms": 0.13,
      "key": 0.13,
      "mode": 0.09,
      "lead_genre": 0.17,
      "genre_overlap": 0.12,
      "tag_overlap": 0.16
    },
    "numeric_thresholds": {
      "tempo": 20.0,
      "key": 2.0,
      "mode": 0.5,
      "duration_ms": 45000.0
    }
  },
  "assembly_controls": {
    "target_size": 10,
    "min_score_threshold": 0.35,
    "max_per_genre": 4,
    "max_consecutive": 2
  },
  "transparency_controls": {
    "top_contributor_limit": 3
  },
  "observability_controls": {
    "diagnostic_sample_limit": 5
  }
}
```

## 5. Effective Configuration Rule

The artefact should distinguish between:

1. intended configuration
2. effective configuration

Intended configuration:

1. what the user or operator requested before run start

Effective configuration:

1. what the pipeline actually used after defaults, validation, and stage-level normalization

This distinction matters for deterministic replay and thesis traceability.

## 6. Required Refinement Work

### 6.1 Phase R1: Formalize Configuration Contract

Deliverables:

1. canonical run-intent schema
2. canonical effective-run schema
3. schema documentation and validation rules

Target outcome:

1. every run begins with a stable machine-readable contract

### 6.2 Phase R2: Implement BL-021 As Artefact Capability

Deliverables:

1. source-scope selection contract for top tracks, saved tracks, playlists, and recently played
2. per-source limits persisted into run metadata
3. profile and observability artefacts updated to record active source scope

Target outcome:

1. source selection becomes part of the real artefact definition rather than a deferred statement

### 6.3 Phase R3: Formalize Influence Track Contract

Deliverables:

1. influence-track list as explicit run input
2. clear recording of which influence tracks were active in BL-004 and BL-009 outputs
3. replay support for runs with and without influence tracks

Target outcome:

1. controllability evidence around influence tracks becomes part of the core artefact contract

### 6.4 Phase R4: Normalize Control Layers

Deliverables:

1. semantic grouping of controls across BL-004 to BL-009
2. mapping from semantic control groups to stage-level implementation fields
3. documentation that explains which controls affect profile construction, retrieval, ranking, assembly, explanation, and logging

Target outcome:

1. the artefact becomes easier to defend and easier to operate reproducibly

### 6.5 Phase R5: Upgrade Observability Schema

Deliverables:

1. BL-009 log extension to record full effective configuration
2. lineage links between run intent, profile, retrieval, scoring, playlist, transparency, and observability artefacts
3. explicit recording of source scope and influence-track participation

Target outcome:

1. BL-009 becomes the canonical execution record rather than only a downstream summary

## 7. Prioritization

Priority order:

1. P0: canonical run-intent and effective-config artefacts
2. P0: BL-021 source-scope contract implementation
3. P1: influence-track formalization
4. P1: control-layer normalization
5. P1: BL-009 observability schema upgrade

Explicit deprioritization for this refinement pass:

1. website flow changes
2. new ingestion adapters
3. corpus switching beyond currently tracked backlog items
4. model-logic expansion beyond current deterministic architecture

## 8. Implementation Order Across Stages

Recommended execution order:

1. add shared run-config schema and validation helpers
2. update ingestion/export metadata to emit source-scope selections
3. update BL-004 to consume source-scope and influence-track config from canonical run input
4. update BL-005 and BL-006 to read canonical config rather than stage-local assumptions only
5. update BL-007 to record playlist behavior controls from the same contract
6. update BL-008 to record explanation controls from the same contract
7. update BL-009 to snapshot intended and effective configuration with full lineage

## 9. Definition Of Done For Refinement

The artefact refinement pass is complete when:

1. every run has a canonical run-intent artefact
2. every run has a canonical effective-config artefact
3. source scope is user-selectable and recorded in run metadata
4. influence tracks are explicitly represented and traceable
5. BL-009 records the full effective configuration and upstream lineage
6. reproducibility and controllability tests can compare runs using canonical config artefacts rather than inferred stage overrides

## 10. Immediate Next Action

Implement the configuration contract first.

Practical next step:

1. create a shared run-config schema and loader
2. map all current BL-004 to BL-009 controls into that schema
3. treat BL-021 as the first real consumer-facing artefact refinement item after schema lock