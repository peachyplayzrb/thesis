# Limitations

The limits below are grounded in the implemented BL-010 and BL-011 evaluation outcomes, not only in planned scope statements.

1. Bootstrap-data bias in controllability outcomes.
	BL-011 showed clear sensitivity at candidate and ranking stages, but threshold variants did not change final playlist membership under the current synthetic candidate pool. This means control-path validity is supported, but some playlist-level effects are muted by the bootstrap data shape.

2. Semantic determinism and raw file-hash determinism are not equivalent.
	BL-010 confirmed deterministic replay for stable output content, while raw hashes for some JSON artifacts varied because those files intentionally include run metadata like timestamps and run ids. Reproducibility claims are therefore bounded to stable semantic fingerprints.

3. Candidate corpus and feature coverage still bound behaviour quality.
	The current Music4All-Onion execution path supports the locked MVP pipeline, but recommendation behaviour remains constrained by available features and corpus composition.

4. Single-user, deterministic design scope.
	The implemented system is intentionally single-user and deterministic for traceability. Results should not be generalized to multi-user dynamics, collaborative filtering behavior, or adaptive online learning settings.

5. No implemented deep or hybrid baseline comparator in MVP.
	Trade-off discussion with modern recommenders remains literature-based because the MVP does not include an implemented high-capacity baseline.

6. Ingestion and real-world alignment are deferred in bootstrap mode.
	BL-001 to BL-003 remain deferred in the active bootstrap strategy, so current findings center on downstream pipeline behavior after pre-aligned synthetic inputs.

7. External validity remains BSc-bounded.
	Evaluation focuses on reproducibility, controllability, and traceability in a feasible engineering setting. It does not include long-horizon user studies or large-scale production deployment testing.

## Failure Modes Observed

1. Run-id collision risk under rapid replays.
	Early BL-010 runs surfaced second-resolution run-id collisions. This was corrected by moving BL-004 to BL-009 run ids to microsecond precision.

2. False instability from volatile metadata in repeat checks.
	Initial BL-010/BL-011 checks were sensitive to non-semantic fields (timing and run metadata), creating false bounded-risk signals until normalization was corrected.

3. Control effects can be real but appear weak at final playlist level.
	BL-011 threshold tests changed candidate pool size in the expected direction, but playlist overlap stayed at 10/10 under the bootstrap corpus. This is treated as a bounded data-regime limitation, not as a broken control path.

## Interpretation Note

These limits define the validity boundary for this thesis. Conclusions are design-evidence claims about a transparent, controllable, and observable deterministic pipeline under the current data and scope constraints.

