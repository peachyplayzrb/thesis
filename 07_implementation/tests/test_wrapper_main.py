from __future__ import annotations

from pathlib import Path

import pytest

import main


def test_normalize_stage_ids_returns_none_for_default() -> None:
    assert main._normalize_stage_ids(None) is None


def test_normalize_stage_ids_normalizes_case_and_whitespace() -> None:
    result = main._normalize_stage_ids([" bl-004 ", "BL-006"])

    assert result == ["BL-004", "BL-006"]


def test_normalize_stage_ids_rejects_invalid_stage() -> None:
    with pytest.raises(ValueError, match="Unsupported stage"):
        main._normalize_stage_ids(["BL-003"])


def test_build_bl013_command_defaults_refresh_seed() -> None:
    command = main._build_bl013_command(
        bl013_script=Path("orchestration/main.py"),
        run_config_path=Path("run_config/outputs/bl013_run_effective_config_latest.json"),
        continue_on_error=False,
        refresh_seed=True,
        stages=None,
        verify_determinism=False,
        verify_determinism_replay_count=None,
    )

    assert "--refresh-seed" in command
    assert "--continue-on-error" not in command
    assert "--stages" not in command
    assert "--verify-determinism" not in command
    assert "--verify-determinism-replay-count" not in command


def test_build_bl013_command_includes_stage_override_and_no_refresh() -> None:
    command = main._build_bl013_command(
        bl013_script=Path("orchestration/main.py"),
        run_config_path=Path("run_config/outputs/bl013_run_effective_config_latest.json"),
        continue_on_error=True,
        refresh_seed=False,
        stages=["BL-004", "BL-005"],
        verify_determinism=True,
        verify_determinism_replay_count=3,
    )

    assert "--refresh-seed" not in command
    assert "--continue-on-error" in command
    assert "--stages" in command
    assert "--verify-determinism" in command
    assert "--verify-determinism-replay-count" in command
    replay_count_index = command.index("--verify-determinism-replay-count")
    assert command[replay_count_index + 1] == "3"
    stage_index = command.index("--stages")
    assert command[stage_index + 1 : stage_index + 3] == ["BL-004", "BL-005"]


def test_validate_determinism_args_allows_default_none() -> None:
    error = main._validate_determinism_args(
        verify_determinism=False,
        verify_determinism_replay_count=None,
    )
    assert error is None


def test_validate_determinism_args_requires_verify_flag() -> None:
    error = main._validate_determinism_args(
        verify_determinism=False,
        verify_determinism_replay_count=3,
    )
    assert error is not None
    assert "requires --verify-determinism" in error


def test_validate_determinism_args_requires_positive_replay_count() -> None:
    error = main._validate_determinism_args(
        verify_determinism=True,
        verify_determinism_replay_count=0,
    )
    assert error is not None
    assert "positive integer" in error
