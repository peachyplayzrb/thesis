# Requirements To Design Map

DOCUMENT STATUS: working traceability map
CONFIDENCE: medium-high
ROLE: literature-to-architecture bridge

## Seed Traceability
| Literature issue | Design requirement | Current mechanism | Literature justification needed |
| --- | --- | --- | --- |
| Opaque recommendation logic | Recommendation process must be inspectable | Deterministic scoring + score trace logging | Explainable RS + faithful explanation evidence |
| Limited user agency | Users can influence recommendation behavior | Influence tracks + parameter controls | Control-oriented interface studies |
| Playlist quality is more than ranking | Playlist-level constraints required | Playlist assembly stage with diversity/order rules | Playlist continuation and sequence-quality literature |
| Cross-source data fragmentation | Tracks must align across systems | ISRC-first + metadata fallback matching | Entity resolution / cross-platform reliability studies |
| Reproducibility concerns | Runs must be repeatable and auditable | Configuration profiles + observability logs | Reproducibility and experiment traceability evidence |

## Open Validation Checks
- Confirm acceptable alignment failure thresholds from literature.
- Confirm which feature descriptors best support transparent explanations.
- Confirm trade-off framing between transparency and recommendation utility.

## Chapter 2 Consequence Handoff (2026-03-14)
| Chapter 2 section | Design consequence carried forward | Chapter 3 target section | Mechanism anchor |
| --- | --- | --- | --- |
| 2.1 Foundations and scope positioning | Justify design against transparency, controllability, reproducibility objectives (not benchmark-max framing) | 3.1, 3.2 | Objective-aligned requirement framing under locked MVP constraints |
| 2.2 Transparency, explainability, controllability | Expose user controls and support sensitivity-oriented evaluation | 3.2, 3.8 | Influence tracks plus configurable parameters |
| 2.3 Music and playlist-specific challenges | Separate playlist assembly from item ranking and treat similarity as approximation | 3.6 | Rule-based playlist assembly with sequence/diversity constraints |
| 2.4 Deterministic design rationale | Keep metrics and feature weights explicit and reviewable | 3.5, 3.6 | Deterministic scoring pipeline with declared weights and rules |
| 2.5 Alignment reliability and reproducibility | Include staged matching diagnostics, unmatched-rate visibility, run-level logging | 3.4, 3.7 | ISRC-first plus metadata fallback, audit logs, replayable config |
| 2.6 Literature gap and conclusion | Evaluate system on transparency/control/reproducibility/rule-compliance criteria | 3.1, 3.7 | Evaluation criteria handoff to Chapter 4 protocol |

Handoff status: complete for Chapter 3 drafting scope; implementation evidence remains Chapter 4 responsibility.

## Layer-Level Traceability (MVP-Aligned)
| Architecture layer | Literature finding | Design requirement | System mechanism | Supporting papers | Support strength |
| --- | --- | --- | --- | --- | --- |
| User Interaction | One-size-fits-all controls are suboptimal; explanation goals matter | Provide controllable but understandable user influence | Influence tracks + minimal parameter controls | P-004, P-002 | medium |
| Data Ingestion | Music-RS must handle practical preference signals | Support one feasible ingestion route for MVP | Single adapter path + manual seed input | P-005 | medium |
| Track Alignment | Cross-source integration needed for pipeline continuity | Map imported tracks into feature corpus reliably | ISRC-first + metadata fallback | P-029, P-030, P-031 | medium |
| Preference Modelling | Preference representation must support recommendation behavior | Build interpretable profile from user history | Aggregated feature profile from matched tracks + influence tracks | P-005 (broad) | low-medium |
| Candidate Dataset | Music recommendation faces scale/selection challenges | Restrict candidate set for tractable scoring | Canonical corpus + candidate subset filtering | P-005 | medium |
| Feature Processing | Stable scoring requires comparable features | Normalize/select features and handle missing values | Feature prep pipeline before scoring | none direct in P-001..P-005 | low |
| Deterministic Scoring | Explainability requires faithful, inspectable mechanisms | Use explicit scoring with traceability | Weighted deterministic similarity + rule adjustments | P-001, P-002, P-003 | high |
| Playlist Assembly | Playlist quality is not equivalent to item ranking | Apply playlist-level constraints | Rule-based assembly (length/repetition/diversity/order) | P-005 | medium |
| Output and Explanation | Explanation value depends on faithful mechanism linkage | Explanations must reflect actual scoring process | Per-track contribution and adjustment reporting | P-001, P-002, P-003 | high |
| Observability and Audit | Evaluation beyond accuracy needs inspectable process evidence | Log enough detail for audit and interpretation | Run logs for inputs/alignment/config/output | P-032, P-033, P-034, P-010 | high |
| Configuration and Execution | Evaluation requires declared objective and reproducible setup | Enable deterministic replay and parameter experiments | Saved config profiles + controlled execution | P-032, P-033, P-034 | high |

## Gaps To Resolve In Next Literature Batch
- Strengthen feature-processing decision evidence.
- Add at least one music-domain alignment reliability benchmark to complement entity-resolution surveys.

