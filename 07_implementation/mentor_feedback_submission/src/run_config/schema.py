from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from shared_utils.coerce import to_float, to_int, to_string_list

FieldType = Literal[
    "positive_int",
    "non_negative_float",
    "fraction",
    "bool",
    "enum",
    "string_list",
]


class RunConfigSchemaError(ValueError):
    """Raised when a value violates a declarative run-config field contract."""


@dataclass(frozen=True)
class FieldSpec:
    type: FieldType
    default: Any
    choices: tuple[str, ...] | None = None


def _coerce_positive_int(value: Any, *, default: Any) -> int:
    parsed = to_int(value, to_int(default, 1))
    if parsed <= 0:
        return to_int(default, 1)
    return parsed


def _coerce_non_negative_float(value: Any, *, default: Any) -> float:
    parsed = to_float(value, to_float(default, 0.0))
    if parsed < 0:
        return to_float(default, 0.0)
    return parsed


def _coerce_fraction(value: Any, *, context: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise RunConfigSchemaError(f"{context} must be numeric") from exc
    if parsed < 0.0 or parsed > 1.0:
        raise RunConfigSchemaError(f"{context} must be in [0,1]")
    return parsed


def _coerce_bool_like(value: Any, *, default: Any, context: str) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    token = str(value).strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    raise RunConfigSchemaError(f"{context} must be boolean-like")


def _coerce_enum(value: Any, *, default: Any, choices: tuple[str, ...] | None) -> Any:
    normalized_choices = choices or tuple()
    token = str(value).strip().lower()
    if token in normalized_choices:
        return token
    return default


def _coerce_string_list(value: Any, *, default: Any) -> Any:
    candidate = to_string_list(value, allow_tuple=True, drop_empty=True)
    if candidate:
        return candidate
    return list(default) if isinstance(default, list) else default


def coerce_field(value: Any, spec: FieldSpec, *, context: str) -> Any:
    if value is None:
        return spec.default

    if spec.type == "positive_int":
        return _coerce_positive_int(value, default=spec.default)

    if spec.type == "non_negative_float":
        return _coerce_non_negative_float(value, default=spec.default)

    if spec.type == "fraction":
        return _coerce_fraction(value, context=context)

    if spec.type == "bool":
        return _coerce_bool_like(value, default=spec.default, context=context)

    if spec.type == "enum":
        return _coerce_enum(value, default=spec.default, choices=spec.choices)

    if spec.type == "string_list":
        return _coerce_string_list(value, default=spec.default)

    raise RunConfigSchemaError(f"Unsupported schema type for {context}: {spec.type}")


def validate_section(raw: dict[str, Any], schema: dict[str, FieldSpec], *, section: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, spec in schema.items():
        result[key] = coerce_field(raw.get(key), spec, context=f"{section}.{key}")
    return result
