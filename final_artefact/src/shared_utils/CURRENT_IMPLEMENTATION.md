# BL000 Shared Utils - Current Implementation

Last Verified: 2026-03-26 03:18:36 (local time)

## Purpose
Provide common path, I/O, env, and config-loading helpers used across active implementation stages.

## Pipeline Role
Shared runtime utility layer for BL003-BL014.

## Primary Modules
- path_utils.py
- io_utils.py
- env_utils.py
- config_loader.py
- report_utils.py
- run_config_runtime.py
- constants.py
- types.py

## Key Functions
- path_utils: repo_root
- io_utils: load_json, load_csv_rows, write_json, sha256_of_file
- env_utils: env_int, env_float, env_str, env_bool
- config_loader: load_run_config_utils_module
- report_utils: write_text, write_json_ascii, write_csv_rows, render_csv_text
- run_config_runtime: get_run_config_path, resolve_run_config_controls

## Current Validation Behavior
- Used for path hardening and consistent hash/file operations.
