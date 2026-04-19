# Installation Posture

Status: active (MFT-H4)

## Decision

This repository is script-first for runtime execution and thesis evidence generation.

- Canonical execution path: run commands from `07_implementation/` using `python main.py ...`.
- Supported environment setup: local virtual environment plus `pip install -r requirements.txt`.
- Installable editable package (`pip install -e .`) is not required for the current thesis runtime contract.

## Rationale

1. The active wrapper and stage orchestration paths are already stable and validated as script-invoked flows.
2. Submission and viva evidence surfaces are tied to command-level reproducibility, not package-index distribution.
3. A script-first posture avoids introducing packaging-layer variance during final hardening.

## Supported Commands

```bash
# from 07_implementation/
python -m venv .venv
# activate venv, then
pip install -r requirements.txt
python main.py --validate-only
```

## Non-Goal For Current Baseline

- Publishing as a distributable package to PyPI is out of scope.
- Reworking source layout into an install-first package layout is out of scope.

## Future Option

If post-thesis productization is needed, packaging can be introduced as a separate change set with explicit build backend, editable-install validation, and CI packaging checks.
