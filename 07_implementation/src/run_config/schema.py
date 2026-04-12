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


def coerce_field(value: Any, spec: FieldSpec, *, context: str) -> Any:
    if value is None:
        return spec.default

    if spec.type == "positive_int":
        parsed = to_int(value, to_int(spec.default, 1))
        if parsed <= 0:
            return to_int(spec.default, 1)
        return parsed

    if spec.type == "non_negative_float":
        parsed = to_float(value, to_float(spec.default, 0.0))
        if parsed < 0:
            return to_float(spec.default, 0.0)
        return parsed

    if spec.type == "fraction":
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            raise RunConfigSchemaError(f"{context} must be numeric")
        if parsed < 0.0 or parsed > 1.0:
            raise RunConfigSchemaError(f"{context} must be in [0,1]")
        return parsed

    if spec.type == "bool":
        if value is None:
            return bool(spec.default)
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

    if spec.type == "enum":
        choices = spec.choices or tuple()
        token = str(value).strip().lower()
        if token in choices:
            return token
        return spec.default

    if spec.type == "string_list":
        candidate = to_string_list(value, allow_tuple=True, drop_empty=True)
        if candidate:
            return candidate
        return list(spec.default) if isinstance(spec.default, list) else spec.default

    raise RunConfigSchemaError(f"Unsupported schema type for {context}: {spec.type}")


def validate_section(raw: dict[str, Any], schema: dict[str, FieldSpec], *, section: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, spec in schema.items():
        result[key] = coerce_field(raw.get(key), spec, context=f"{section}.{key}")
    return result
