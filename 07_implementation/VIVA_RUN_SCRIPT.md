# Defense / Viva Run Script

**Document authority**: MFT-F6 (UNDO-R submission-readiness)
**Status**: Active as of 2026-04-19

This document is the concise examiner-ready guide for demonstrating the live pipeline during a defense or viva session. It covers the recommended demo sequence, expected outputs at each step, verification checks, and a fallback plan if any step fails.

---

## Pre-Demo Checklist (complete before session)

```
[ ] Python 3.14.x venv is active (check: python --version)
[ ] requirements.txt installed (check: python -c "import rapidfuzz; print('ok')")
[ ] Embedded dataset present: 07_implementation/src/data_layer/outputs/ds001_working_candidate_dataset.csv
[ ] Embedded Spotify export present: 07_implementation/src/ingestion/outputs/spotify_api_export/
[ ] Default profile present: 07_implementation/config/profiles/run_config_ui013_tuning_v1f.json
[ ] Previous output artifacts cleared or noted as baseline reference
```

---

## Recommended Demo Sequence

### Step 0 — Environment activation (30 seconds)

```powershell
# From workspace root
cd 07_implementation
.\.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate         # macOS/Linux
python --version                     # confirm 3.14.x
```

**Expected output**: `Python 3.14.x`

---

### Step 1 — Preflight check (30 seconds)

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/preflight_windows.ps1
```

**Expected output**:
```
=== Preflight Checks (Windows) ===
PASS: Python version Python 3.14.x
PASS: Git available
PASS: Embedded DS-001 dataset found
PASS: Embedded Spotify export bundle found
PASS: Preflight checks complete
```

**If this fails**: check venv activation and embedded asset paths.

---

### Step 2 — Full pipeline + quality gate (3–5 minutes)

```powershell
python main.py --validate-only
```

This runs BL-003 through BL-013 (full pipeline), then BL-014 (quality gate).

**Expected output (summary)**:
- `BL-013` completes with `overall_status: pass` and stage count 8 (or 7 without seed refresh).
- `BL-014` completes with `overall_status: pass` and 36 passing sanity checks.
- Run IDs printed to stdout: `BL013-ENTRYPOINT-<timestamp>` and `BL014-SANITY-<timestamp>`.

**Key artifact paths**:
```
src/orchestration/outputs/bl013_orchestration_run_latest.json   ← run summary
src/quality/outputs/bl014_sanity_report.json                    ← 36/36 quality checks
src/run_config/outputs/bl013_run_effective_config_latest.json   ← runtime-environment metadata
```

---

### Step 3 — Deterministic verification (optional, 3 minutes)

Run the pipeline a second time to demonstrate repeatability:

```powershell
python main.py --validate-only
```

Then check that the BL-010 reproducibility report confirms a deterministic match:

```
src/reproducibility/outputs/bl010_reproducibility_report_latest.json
→ "deterministic_match": true
```

Alternatively, inspect the BL-013 summary for `deterministic_verification_status: pass`.

---

### Step 4 — Controllability demonstration (2–3 minutes)

Run with the reserved-slots influence profile to show influence-injection controllability:

```powershell
python main.py --run-config config/profiles/run_config_ui013_tuning_v1g_reserved_slots.json
```

**What to point out**:
- `src/orchestration/outputs/bl013_orchestration_run_latest.json` → `influence_assembly_summary` section.
- Compare `new_injected_count` vs `relabelled_count` — demonstrates additive vs reinterpretation injection paths.
- `src/quality/outputs/bl014_sanity_report.json` still passes with this config variant.

Compare to baseline:
```powershell
python main.py --run-config config/profiles/run_config_ui013_tuning_v1f.json
```

---

### Step 5 — Transparency inspection (1 minute)

Open or print the explanation artifact:

```powershell
python -c "
import json
payload = json.load(open('src/transparency/outputs/bl008_explanation_payload_latest.json'))
for t in payload.get('tracks', [])[:3]:
    print(t.get('track_id'), '|', t.get('why_selected', {}).get('headline_phrase'))
"
```

**Expected output**: Three track IDs with human-readable explanation phrases.

---

### Step 6 — Quality posture summary (30 seconds)

Point the examiner to the tooling evidence surfaces:

| Artifact | Location |
|---|---|
| Coverage report | `coverage_src_report_latest.txt` (69% measured, ≥65% gate) |
| Dependency audit | `pip_audit_report_latest.txt` (advisory findings, non-blocking) |
| Security scan | `bandit_src_report_latest.txt` (Ruff S-rules fallback on Python 3.14) |
| Type check | Run `pyright --project 07_implementation/pyrightconfig.json` → `0 errors` |

---

## Expected Artifacts After Full Demo Run

| Artifact | Expected content |
|---|---|
| `bl013_orchestration_run_latest.json` | `overall_status: pass`, `executed_stage_count: 8` |
| `bl014_sanity_report.json` | `overall_status: pass`, 36 checks |
| `bl013_run_effective_config_latest.json` | `runtime_environment` with Python version, platform, timezone |
| `bl010_reproducibility_report_latest.json` | `deterministic_match: true` (if second run done) |
| `bl008_explanation_payload_latest.json` | Per-track explanation phrases |

---

## Fallback Plan

| Problem | Fallback action |
|---|---|
| venv missing or broken | `python -m venv .venv && .venv\Scripts\Activate.ps1 && pip install -r requirements.txt` |
| Embedded dataset missing | Restore from `_deep_archive_march2026/` or from the packaged submission zip |
| BL-013 fails at a stage | Run with `--continue-on-error` flag; BL-014 will report which checks pass/fail |
| BL-014 shows `warn` not `pass` | Show specific check failures in the JSON report; most are advisory-only gates |
| Pyright errors after install | Confirm correct venv is active: `pyright --project pyrightconfig.json` |
| Coverage threshold fails | Threshold is set at 65%; measured baseline is 69% — rerun with `scripts/test_coverage.ps1` |

---

## Key Talking Points for Examiners

1. **Reproducibility**: Two sequential runs of `python main.py` produce `deterministic_match: true` — no stochastic paths, no floating-point non-determinism in assembly ordering.
2. **Controllability**: The `reserved_slots` profile (`v1g`) vs the default profile (`v1f`) produces measurably different influence injection counts, demonstrable in real time.
3. **Transparency**: Every included track has a machine-generated explanation in BL-008, linked to scoring component weights via `why_selected`.
4. **Quality gate**: BL-014 runs 36 cross-stage contract checks; all pass under the default profile.
5. **Tool evidence**: Coverage, type safety (pyright 0 errors), lint (ruff clean), and security scan (advisory) are all available as report artifacts in the workspace root.
