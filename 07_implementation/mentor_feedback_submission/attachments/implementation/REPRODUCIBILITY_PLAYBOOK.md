# Reproducibility Playbook

This playbook defines a repeatable operator path for deterministic replay evidence.

Scope:
- Active implementation runtime under `07_implementation/`
- BL-013 orchestration entrypoint run
- BL-010 deterministic replay verification
- BL-014 post-run contract validation

## Preconditions

- Python environment configured for this workspace.
- Dependencies installed from `requirements.txt`.
- Active profile available: `config/profiles/run_config_ui013_tuning_v1f.json`.
- Embedded candidate dataset present at `src/data_layer/outputs/ds001_working_candidate_dataset.csv`.

## Canonical Command Path

From `07_implementation/`:

```bash
python main.py --validate-only --verify-determinism --verify-determinism-replay-count 3
```

Equivalent VS Code task path:
- `07: Validate + Determinism Replay x3 (Wrapper)`

## What This Executes

1. BL-013 runs the configured stage path and emits run artifacts.
2. BL-010 executes deterministic replay verification (3 replays).
3. BL-014 validates contract continuity and quality checks.

`--validate-only` is additive. It does not skip BL-013.

## Expected Artifact Surfaces

Expected generated artifacts are emitted in run output directories used by BL-013 and downstream stages.

Primary evidence surfaces to inspect:
- BL-013 summary artifact: includes stage execution metadata and hash-input-chain metadata.
- BL-009 observability artifact: includes validity boundaries and reproducibility interpretation framing.
- BL-010 reproducibility artifact: includes deterministic replay verdict and interpretation boundaries.
- BL-014 sanity-check artifact: includes contract check outcomes.

## Pass Criteria

Treat a run as reproducibility-pass when all of the following are true:

- BL-010 reports `deterministic_match=true`.
- BL-014 reports all checks passing for the active gate posture.
- BL-013 indicates coherent stage execution with no missing requested stages (unless intentionally omitted by config).

## Interpretation Boundaries

Interpret deterministic replay evidence as artifact-level consistency evidence, not universal behavioral invariance.

Use these boundaries:
- Covered domain: reproducibility under the same pipeline code, fixed controls, fixed embedded datasets, and the same deterministic execution path.
- Not covered domain: environment changes, dataset swaps, external-source drift, or model-family changes outside the evaluated pipeline.
- Non-claims: this evidence does not claim cross-environment invariance for all future runtime conditions.

For report-facing interpretation, consult:
- BL-010 `interpretation_boundaries`
- BL-009 `validity_boundaries.reproducibility_interpretation`

## Troubleshooting

- If deterministic replay fails:
  - Confirm run config path and profile are correct.
  - Confirm no unintended environment overrides changed active controls.
  - Re-run with the same command and inspect BL-013/BL-010 artifact IDs and hash chain.
- If BL-014 fails while BL-010 passes:
  - Inspect contract checks for missing or malformed stage artifacts.
  - Verify upstream stage outputs were produced and not manually edited.

## Operator Notes

- Keep command path unchanged when producing thesis evidence unless an explicit change is logged.
- Capture BL-013, BL-009, BL-010, and BL-014 artifact IDs together for audit traceability.
