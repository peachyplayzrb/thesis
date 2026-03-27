# BL-013 Entrypoint

## Purpose
Orchestrate BL-004 through BL-009 execution with optional BL-003 refresh and canonical config artifact emission.

## Inputs
- Active pipeline stage scripts
- Optional run-config path

## Outputs
- BL-013 orchestration summary artifacts in `outputs/`
- Optional run-intent and run-effective-config artifacts

## Run
- See `bl013_run_command.md`
- `python bl013_entrypoint/run_bl013_pipeline_entrypoint.py --help`

## Validation
- Confirm all requested stages return pass and stable artifact hashes are present.
