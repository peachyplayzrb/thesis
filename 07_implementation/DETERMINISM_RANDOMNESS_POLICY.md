# Determinism and Randomness Policy

Date: 2026-04-19
Scope: MFT-B4 (seed/randomness policy artifact)
Status: Active

## Policy Statement
The active recommendation pipeline is intentionally deterministic under fixed inputs, fixed run configuration, and fixed implementation version.

## Current Runtime Stance
- No stochastic sampling path is part of the active BL-003 through BL-014 execution contract.
- No runtime random seed is required for normal operation because pseudo-random selection is not used in active scoring/assembly logic.
- Reproducibility claims are bounded to artifact-level deterministic replay under fixed inputs/configuration (not cross-environment behavioral identity).

## If Randomness Is Introduced Later
Any future stochastic path must satisfy all of the following before being considered compliant:
1. Emit explicit seed provenance in run-intent/effective-config artifacts.
2. Emit PRNG family/version and seed value used for each stochastic stage.
3. Provide deterministic replay mode that fixes seed and confirms stable outputs for the stochastic component.
4. Add stage-specific tests that verify same-seed reproducibility and different-seed divergence behavior.
5. Update BL-010/BL-014 contract checks to validate seed/PRNG metadata presence.

## Operator Guidance
- Treat deterministic replay as the default expected posture.
- If observed output drift occurs under fixed inputs/configuration, investigate:
  - environment drift,
  - dependency/version drift,
  - newly introduced unordered iteration in order-sensitive outputs,
  - undocumented stochastic logic.

## Evidence Surfaces
- Effective run config with runtime metadata: `src/run_config/outputs/bl013_run_effective_config_latest.json`
- Reproducibility report: `src/reproducibility/outputs/reproducibility_report.json`
- Golden fixture tests: `tests/test_golden_artifacts.py`
