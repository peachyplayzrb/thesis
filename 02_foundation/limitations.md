# Limitations

The limits below are grounded in the implemented BL-010 and BL-011 evaluation outcomes, not only in planned scope statements.

1. Bootstrap-data bias in controllability outcomes.
	BL-011 showed clear sensitivity at candidate and ranking stages, but threshold variants did not change final playlist membership under the current synthetic candidate pool. This means control-path validity is supported, but some playlist-level effects are muted by the bootstrap data shape.

2. Semantic determinism and raw file-hash determinism are not equivalent.
	BL-010 confirmed deterministic replay for stable output content, while raw hashes for some JSON artifacts varied because those files intentionally include run metadata like timestamps and run ids. Reproducibility claims are therefore bounded to stable semantic fingerprints.

3. Candidate corpus and feature coverage still bound behaviour quality.
	The active DS-002 path supports deterministic candidate-side audio scoring, but recommendation behaviour remains constrained by corpus composition and cross-source coverage gaps.

4. Single-user, deterministic design scope.
	The implemented system is intentionally single-user and deterministic for traceability. Results should not be generalized to multi-user dynamics, collaborative filtering behavior, or adaptive online learning settings.

5. No implemented deep or hybrid baseline comparator in MVP.
	Trade-off discussion with modern recommenders remains literature-based because the MVP does not include an implemented high-capacity baseline.

6. User-side numeric audio features are externally constrained.
	Spotify Web API audio-feature endpoints are deprecated, so user-side `tempo`, `loudness`, `key`, and `mode` cannot be sourced directly from Spotify in the current pipeline. Current BL-020 fallback uses semantic user profiling (Last.fm tags) plus candidate-side DS-002 audio features.

7. External validity remains BSc-bounded.
	Evaluation focuses on reproducibility, controllability, and traceability in a feasible engineering setting. It does not include long-horizon user studies or large-scale production deployment testing.

## Failure Modes Observed

1. Run-id collision risk under rapid replays.
	Early BL-010 runs surfaced second-resolution run-id collisions. This was corrected by moving BL-004 to BL-009 run ids to microsecond precision.

2. False instability from volatile metadata in repeat checks.
	Initial BL-010/BL-011 checks were sensitive to non-semantic fields (timing and run metadata), creating false bounded-risk signals until normalization was corrected.

3. Control effects can be real but appear weak at final playlist level.
	BL-011 threshold tests changed candidate pool size in the expected direction, but playlist overlap stayed at 10/10 under the bootstrap corpus. This is treated as a bounded data-regime limitation, not as a broken control path.

4. Real-data alignment can fail even when deterministic code is correct.
	BL-020 real-data execution showed that DS-002 fuzzy alignment can produce plausible but wrong matches when the user's dominant artists are sparsely represented in the candidate corpus. This was treated as a data-plane mismatch and mitigated by a semantic-enrichment fallback, not by silently accepting low-quality matches.

## Interpretation Note

These limits define the validity boundary for this thesis. Conclusions are design-evidence claims about a transparent, controllable, and observable deterministic pipeline under the current data and scope constraints.

