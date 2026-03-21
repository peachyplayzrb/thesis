# BL-013 Run Command Documentation

## Purpose
Use one command to execute the bootstrap pipeline stages BL-004 through BL-009 in deterministic order.

## Default command

```powershell
python 07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py
```

## Optional commands

Run only selected stages (ordered as provided):

```powershell
python 07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py --stages BL-004 BL-005 BL-006
```

Continue after a stage failure to inspect downstream behavior:

```powershell
python 07_implementation/implementation_notes/entrypoint/run_bl013_pipeline_entrypoint.py --continue-on-error
```

## Output artifacts
- Run summaries are written to:
  - `07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_<run_id>.json`
  - `07_implementation/implementation_notes/entrypoint/outputs/bl013_orchestration_run_latest.json`
- Each summary records:
  - executed stage order
  - per-stage command, return code, elapsed time, and stdout/stderr
  - stable artifact hashes for repeatability checks

## Repeatability check
1. Run the default command twice without changing code or inputs.
2. Compare `stable_artifact_hashes` in the two summary files.
3. Matching hashes indicate deterministic behavior for the stable pipeline outputs tracked by BL-013.
