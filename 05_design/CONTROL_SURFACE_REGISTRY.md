# Control Surface Registry

DOCUMENT STATUS: implementation-synchronized control registry companion
LAST SYNCHRONIZED: 2026-04-19 UTC
ROLE: thesis-facing control family map aligned to `src/run_config/control_registry.py`

## 1) Purpose
Summarize active user-facing controls, stage ownership, expected effect surfaces, and known implementation limits.

## 2) Canonical Authority
Machine-readable authority is `07_implementation/src/run_config/control_registry.py` (`control-registry-v1`, 24 controls).

## 3) Control Families and Evidence Surfaces

| Family | Primary Stage(s) | Config Surface | Primary Effect Surface | Validation Surface |
| --- | --- | --- | --- | --- |
| Profile controls | BL-004 | `profile_controls.*` | BL-004 profile diagnostics and summary | BL-014 handshake/continuity checks |
| Retrieval controls | BL-005 | `retrieval_controls.*` | Candidate keep/reject distribution and `candidate_shaping_fidelity` | BL-014 advisories/gates |
| Scoring controls | BL-006 | `scoring_controls.*` | Component contribution shifts, rank shifts | BL-008 explanation payload consistency + BL-014 checks |
| Assembly controls | BL-007 | `assembly_controls.*` | Playlist composition and `tradeoff_metrics_summary` | BL-014 handshakes and BL-009 summaries |
| Transparency controls | BL-008 | `transparency_controls.*` | Explanation payload shape/content | BL-014 explanation-fidelity checks |
| Observability controls | BL-009 | `observability_controls.*` | Run log section inclusion and diagnostics surfaces | BL-014 schema/contract checks |
| Reproducibility controls | BL-010 | `reproducibility_controls.*` | `deterministic_match` and replay verdict data | BL-014 and replay consistency surfaces |
| Controllability controls | BL-011 | `controllability_controls.*` | Scenario matrix differences and `interaction_coverage_summary` | BL-014 control-effect checks |
| Orchestration controls | BL-013 | `orchestration_controls.*`, CLI | Requested vs executed stage sequence (`stage_execution`) | BL-014 end-of-run checks |
| Sanity policies | BL-014 | env/run policy inputs | Gate/advisory severity behavior | BL-014 self-report (`gate_results`) |

## 4) Policy Convention
Where implemented, policy normalization follows:
1. `allow`: compatibility-tolerant, no hard failure.
2. `warn`: advisory/gate warning, run can remain pass.
3. `strict`: fail when required contract evidence is missing.

## 5) Known Issues and Limits
1. BL-007 policy order is fixed in code; not user-reorderable.
2. Influence-related controls can produce weaker effects than threshold/weight controls depending on candidate pool context.
3. Full counterfactual rerun explanation traces are not currently an active control family.

## 6) Practical Use
Use this registry with BL-011 and BL-013/BL-014 outputs when claiming control-effect evidence in Chapter 4/5.
