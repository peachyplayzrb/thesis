"""Shared helpers for validation policy normalization and status resolution."""

from __future__ import annotations

from typing import Any

VALIDATION_POLICIES: tuple[str, ...] = ("allow", "warn", "strict")


def normalize_validation_policy(policy: Any, default: str = "warn") -> str:
    """Normalize policy string to one of: allow, warn, strict."""
    value = str(policy or default).strip().lower()
    if value in VALIDATION_POLICIES:
        return value
    return default


def resolve_policy_status(normalized_policy: str, violations: list[str]) -> str:
    """Resolve pass/warn/allow/fail status from policy and violations."""
    if normalized_policy == "strict" and bool(violations):
        return "fail"
    if violations and normalized_policy == "warn":
        return "warn"
    if violations and normalized_policy == "allow":
        return "allow"
    return "pass"
