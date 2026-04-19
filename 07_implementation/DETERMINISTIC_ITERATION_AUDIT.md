# Deterministic Iteration Audit

Date: 2026-04-19
Scope: MFT-B3 (dict/set-sensitive iteration audit)
Status: Completed

## Objective
Confirm that dict/set iteration paths do not introduce nondeterministic behavior in run-critical outputs under the active Python baseline (3.14.x) and current artifact contracts.

## Method
1. Static pattern sweep over `07_implementation/src/**/*.py` for iteration over `items()`, `keys()`, `values()`, and `set(...)` in loops/comprehensions.
2. Focused manual review of run-critical stages and artifact emitters:
   - BL-003 alignment summary/writers
   - BL-007 playlist assembly/reporting
   - BL-009 observability payload construction
   - BL-010 reproducibility payload/hash construction
   - BL-013 orchestration summary builder
3. Determinism posture check against existing replay evidence and fixed-fixture golden tests.

## Findings
- No high-risk nondeterministic iteration defects were identified in run-critical ordering paths.
- Paths that iterate mappings in reviewed surfaces are either:
  - commutative aggregations (counts/sums), or
  - deterministic by construction (ordered input lists, explicit sorting), or
  - consumed in contexts where key order is not a semantic contract (JSON object fields interpreted by key).
- Explicit sorted-set handling is already present where order-sensitive key unions are formed (for example, sorted set intersections/unions in run-config/observability logic).

## Reviewed High-Signal Surfaces
- `src/playlist/rules.py`: candidate ordering driven by ranked list and deterministic control flow; no set-order dependence in playlist position decisions.
- `src/playlist/reporting.py`: aggregate metric construction is value-commutative; no order-sensitive reduction affecting verdicts.
- `src/observability/main.py`: key-union paths for source diagnostics use explicit sorting where ordering is emitted.
- `src/reproducibility/main.py`: stable-hash and replay comparisons are based on canonicalized payloads and contract-defined stable fields.
- `src/orchestration/summary_builder.py`: stage execution ordering is captured from explicit sequence lists and counters.

## Evidence Linkage
- Golden fixture determinism tests: `tests/test_golden_artifacts.py` (hash-stable track order + genre mix).
- Replay determinism posture: BL-010 deterministic replay reporting surfaces (`deterministic_match=True` in current baseline records).

## Residual Risk
Low. Future risk is primarily additive changes that introduce new set/dict iteration in order-sensitive artifact fields without sorting/canonicalization.

## Maintenance Rule
When adding new order-sensitive outputs:
- Prefer sorted iteration over keys/sets.
- If order is intentionally non-semantic, keep consumers key-based and avoid hash comparisons over raw object key order.
- For replay/hash contracts, canonicalize JSON before hashing and explicitly exclude volatile metadata fields.
