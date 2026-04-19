# Demo Profile Catalog

This catalog curates demo-ready run-config profiles for defense, viva, and walkthrough use.

Selection goals:
- Keep a stable baseline profile.
- Include explicit influence-policy variants.
- Include non-influence behavior variants for retrieval and filtering demonstrations.
- Provide quick command paths and what to highlight.

## Quick Run Pattern

From `07_implementation/`:

```bash
python main.py --run-config <profile-path> --validate-only
```

Use `--validate-only` when you want BL-014 check outcomes alongside the run.

## Core Baseline

### 1) Baseline default (anchor run)

- Profile: `config/profiles/run_config_ui013_tuning_v1f.json`
- Demo role: stable baseline for all comparisons.
- Highlights:
  - strict validation profile
  - influence tracks enabled
  - default assembly behavior (no explicit influence policy override)
  - standard retrieval and scoring thresholds

Recommended first run command:

```bash
python main.py --run-config config/profiles/run_config_ui013_tuning_v1f.json --validate-only
```

## Influence Policy Variants (Primary F4 Requirement)

### 2) Reserved slots influence policy

- Profile: `config/profiles/run_config_ui013_tuning_v1g_reserved_slots.json`
- Demo role: show policy-driven guaranteed influence placement behavior.
- Key controls:
  - `assembly_controls.influence_policy_mode = reserved_slots`
  - `assembly_controls.influence_reserved_slots = 3`
  - genre/consecutive/threshold override flags set to false
- What to show:
  - BL-007 and BL-013 influence assembly summaries
  - how reserved insertion differs from baseline competition

Run command:

```bash
python main.py --run-config config/profiles/run_config_ui013_tuning_v1g_reserved_slots.json --validate-only
```

### 3) Hybrid override influence policy

- Profile: `config/profiles/run_config_ui013_tuning_v1h_hybrid_override.json`
- Demo role: show influence policy with bounded overrides for assembly constraints.
- Key controls:
  - `assembly_controls.influence_policy_mode = hybrid_override`
  - `assembly_controls.influence_reserved_slots = 2`
  - override flags enabled for genre cap, consecutive cap, and threshold
- What to show:
  - policy difference vs reserved-slots mode
  - effect on inclusion flexibility under strict constraints

Run command:

```bash
python main.py --run-config config/profiles/run_config_ui013_tuning_v1h_hybrid_override.json --validate-only
```

### 4) Hard-swing influence stress variant

- Profile: `config/profiles/run_config_ui013_tuning_v1e_hard_swing_influence.json`
- Demo role: stress-test influence behavior with influence-heavy interaction scope.
- Key controls:
  - interaction scope set to influence-only
  - larger influence track set and higher influence preference weight
  - relaxed retrieval support requirement relative to strict baseline variants
- What to show:
  - strong influence signal propagation into downstream ranking/assembly
  - contrast against mixed history+influence baseline

Run command:

```bash
python main.py --run-config config/profiles/run_config_ui013_tuning_v1e_hard_swing_influence.json --validate-only
```

## Non-Influence Behavior Variants

### 5) Retrieval-tight variant

- Profile: `config/profiles/run_config_ui013_tuning_v2a_retrieval_tight.json`
- Demo role: show stricter retrieval and assembly gating.
- Key controls:
  - tighter semantic/numeric retrieval filters
  - stricter tempo/key/duration thresholds
  - higher min score threshold and lower max per genre
- What to show:
  - candidate pool narrowing
  - stricter quality/diversity trade behavior

Run command:

```bash
python main.py --run-config config/profiles/run_config_ui013_tuning_v2a_retrieval_tight.json --validate-only
```

### 6) Language + recency gate variant

- Profile: `config/profiles/run_config_ui013_tuning_v2b_language_recency_gate.json`
- Demo role: show language and recency filtering effects.
- Key controls:
  - `retrieval_controls.language_filter_enabled = true`
  - `retrieval_controls.language_filter_codes = ["en"]`
  - `retrieval_controls.recency_years_min_offset = 15`
  - release-year threshold included
- What to show:
  - explicit filtering rationale in retrieval diagnostics
  - change in candidate eligibility by language/recency policy

Run command:

```bash
python main.py --run-config config/profiles/run_config_ui013_tuning_v2b_language_recency_gate.json --validate-only
```

## Recommended Demo Sequence

1. Run baseline `v1f`.
2. Run `v1g_reserved_slots` and compare influence placement behavior.
3. Run `v1h_hybrid_override` and compare override-driven flexibility.
4. Run one non-influence variant (`v2a` or `v2b`) based on your narrative.

## Notes

- Keep baseline and variant runs close in time for easier artifact comparison.
- Capture BL-013 and BL-014 run IDs for each profile used in a demo.
- Prefer these curated profiles over ad hoc temporary profiles for examiner-facing sessions.
