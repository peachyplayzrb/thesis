# Standalone Implementation Submission Guide

## Overview

This is a **fully standalone, portable implementation** of the recommendation system that can be extracted and run independently from the thesis repository. It contains:

- **Complete 14-stage pipeline** (BL-003 through BL-014)
- **All supporting utilities** (data layer, configuration, reporting)
- **Reproducibility & validation stages** (BL-010, BL-011, BL-014)
- **Embedded runtime inputs** (DS-001 candidate dataset + BL-002 Spotify export bundle)
- **Full documentation** and setup scripts

## Quick Start (5 minutes)

### 1. Setup Environment

**On Windows (PowerShell):**
```powershell
# From the submission package root
.\setup.ps1

# Or manually:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**On macOS/Linux:**
```bash
# From the submission package root
chmod +x setup.sh
./setup.sh

# Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify Package Integrity

```bash
# Activate environment first
python test_standalone.py
```

Expected output:
```
✓ Package structure valid
✓ Core utilities importable
✓ Path resolution works
✓ Entry point available
✓ Requirements file valid

✓ Package is ready for deployment!
```

### 3. Run the Pipeline

**Prerequisite:** The package must include embedded runtime inputs under `src/data_layer/outputs/` and `src/ingestion/outputs/spotify_api_export/`.

```bash
# Basic run with validation
python main.py --validate-only

# Full pipeline run
python main.py \
    --run-config config/profiles/run_config_ui013_tuning_v1f.json

# With error continuation
python main.py --continue-on-error
```

## Package Structure

```
.
├── main.py                              # Entry point for standalone execution
├── setup.py                             # Package metadata for pip install
├── setup.sh                             # Unix/Linux setup script
├── setup.ps1                            # Windows PowerShell setup script
├── test_standalone.py                   # Smoke test for verification
├── README.md                            # User documentation
├── requirements.txt                     # Python dependencies
├── .gitignore                           # Git configuration
├── config/
│   └── profiles/                        # Runnable JSON configuration profiles
└── src/                                 # Core pipeline
    ├── shared_utils/                    # Shared utilities (path, I/O, hashing)
    ├── run_config/                      # Runtime config utilities
    ├── data_layer/                      # Embedded DS-001 candidate dataset
    ├── ingestion/                       # Spotify ingestion
    ├── alignment/                       # Dataset alignment
    ├── profile/                         # User profile construction
    ├── retrieval/                       # Candidate retrieval
    ├── scoring/                         # Track scoring
    ├── playlist/                        # Playlist generation
    ├── transparency/                    # Transparency reporting
    ├── observability/                   # System observability
    ├── reproducibility/                 # Reproducibility validation
    ├── controllability/                 # Controllability evaluation
    ├── orchestration/                   # Pipeline orchestrator
    └── quality/                         # Quality assurance
```

## Key Features

### ✓ Fully Standalone
- No dependencies on thesis repository structure
- All paths are relative to package root
- Works outside of original repository context

### ✓ Environment-Driven
- Configuration via CLI arguments
- Embedded candidate dataset bundled under `src/data_layer/outputs/`
- Embedded Spotify export bundle bundled under `src/ingestion/outputs/spotify_api_export/`
- Spotify credentials are optional and only needed for live export regeneration

### ✓ Reproducible
- Deterministic outputs (no randomization)
- Artifact registry tracks all generated files
- Reproducibility checks (BL-010) included
- Hash verification for critical outputs

### ✓ Transparent
- Stage-by-stage logging
- JSON-formatted reports
- Artifact manifests at each stage
- BL-008 transparency layer included

## Configuration Profiles

Available profiles in `config/profiles/`:

- `run_config_ui013_tuning_v1f.json` - **Default canonical baseline**
- `run_config_ui013_tuning_v1a.json` through `run_config_ui013_tuning_v1d.json` - Historical retained v1 variants
- `run_config_ui013_tuning_v1e_hard_swing_influence.json` - Historical retained influence variant
- `run_config_ui013_tuning_v2a_retrieval_tight.json` - Experimental retrieval-tight variant
- `run_config_ui013_tuning_v2b_language_recency_gate.json` - Experimental language/recency-gated variant
- `run_config_bl021_probe_v1.json` and `run_config_bl021_probe_v2.json` - Probe profiles (reference/testing only)

Use with:
```bash
python main.py --run-config config/profiles/[config-name].json
```

## Output Artifacts

After running the pipeline, outputs appear in:

```
src/
├── alignment/outputs/
├── profile/outputs/
├── retrieval/outputs/
├── scoring/outputs/
├── playlist/outputs/
├── transparency/outputs/
├── observability/outputs/
├── reproducibility/outputs/
├── controllability/outputs/
├── orchestration/outputs/
└── quality/outputs/
```

Key outputs:
- `src/playlist/outputs/playlist.json` - Generated playlist
- `src/transparency/outputs/bl008_explanation_payloads.json` - Explanation data
- `src/reproducibility/outputs/reproducibility_report.json` - Validation results
- `src/controllability/outputs/controllability_report.json` - Control evaluation

## Environment Variables

```bash
# Spotify Authentication (Optional: live export regeneration only)
export SPOTIPY_CLIENT_ID="your_client_id"
export SPOTIPY_CLIENT_SECRET="your_client_secret"

# Optional: Override implementation root (rarely needed)
export IMPL_ROOT="/path/to/final_artefact/src/"
```

## Troubleshooting

### Import Errors
**Problem:** `ImportError: No module named 'shared_utils'`
**Solution:** Ensure requirements are installed:
```bash
pip install -r requirements.txt
python test_standalone.py  # Verify with smoke test
```

### Missing Embedded Dataset
**Problem:** `Cannot find embedded candidate dataset at .../src/data_layer/outputs/ds001_working_candidate_dataset.csv`
**Solution:** Verify the submission package was extracted completely and still contains the embedded DS-001 dataset:
```bash
ls src/data_layer/outputs/
# Should show: ds001_working_candidate_dataset.csv
```

### Spotify Authentication
**Problem:** `SpotifyApiError: Invalid Client`
**Solution:** Not required for the packaged default run. If you are regenerating exports from the API, set credentials:
```bash
export SPOTIPY_CLIENT_ID="your_id"
export SPOTIPY_CLIENT_SECRET="your_secret"
```

### Path Resolution Issues
**Problem:** `RuntimeError: Cannot find src directory`
**Solution:** Run from package root:
```bash
cd /path/to/recommendation-implementation/
python main.py ...
```

## Technical Specifications

- **Python Version:** 3.10+
- **Operating Systems:** Windows, macOS, Linux
- **Key Dependencies:**
    - fastapi >= 0.111.0
    - h5py == 3.16.0
    - httpx >= 0.27.0
    - pypdf == 6.9.1
    - rapidfuzz == 3.14.3
    - spotipy == 2.23.0
    - uvicorn[standard] >= 0.29.0

- **Execution Time:** ~30-60 minutes for full pipeline
- **Disk Space:** ~2.5 GB (implementation + outputs)

## For Reviewers

### Reproducibility Verification
Run the reproducibility check:
```bash
python src/reproducibility/main.py \
    --replay-count 3
```

This verifies that BL-004 through BL-009 produce identical outputs across runs.

### Controllability Evaluation
Review controllability of recommendation parameters:
```bash
python src/controllability/main.py
```

### Quality Assurance
Run comprehensive quality checks:
```bash
python src/quality/sanity_checks.py
```

## Submission Contents Checklist

- ✓ Complete 14-stage pipeline (BL-003 through BL-014)
- ✓ All configuration profiles
- ✓ Setup scripts (Windows/Unix)
- ✓ Smoke test for validation
- ✓ Comprehensive README
- ✓ This submission guide
- ✓ Full requirements.txt
- ✓ .gitignore for clean repository

## Questions or Issues?

Refer to:
1. [README.md](README.md) - General usage documentation
2. `src/` - Domain-organized implementation packages
3. `config/profiles/` - Runnable configuration profiles
4. Stage output reports (`src/*/outputs/*_report.json`) - Detailed execution logs

---

**Package Version:** 1.0.0
**Created:** March 28, 2026
**Status:** Ready for academic review
