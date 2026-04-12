from __future__ import annotations

import pytest

from run_config.schema import FieldSpec, RunConfigSchemaError, coerce_field, validate_section


def test_coerce_field_positive_int_and_default() -> None:
    spec = FieldSpec(type="positive_int", default=5)
    assert coerce_field("7", spec, context="x") == 7
    assert coerce_field(None, spec, context="x") == 5


def test_coerce_field_fraction_rejects_out_of_range() -> None:
    spec = FieldSpec(type="fraction", default=0.5)
    with pytest.raises(RunConfigSchemaError):
        coerce_field(1.1, spec, context="x")


def test_coerce_field_bool_like() -> None:
    spec = FieldSpec(type="bool", default=False)
    assert coerce_field("true", spec, context="x") is True
    assert coerce_field("0", spec, context="x") is False


def test_coerce_field_enum_fallback() -> None:
    spec = FieldSpec(type="enum", default="a", choices=("a", "b"))
    assert coerce_field("b", spec, context="x") == "b"
    assert coerce_field("z", spec, context="x") == "a"


def test_validate_section_applies_schema() -> None:
    schema = {
        "top_tag_limit": FieldSpec(type="positive_int", default=10),
        "confidence_bin": FieldSpec(type="fraction", default=0.5),
        "emit_diag": FieldSpec(type="bool", default=True),
    }
    raw = {"top_tag_limit": "12", "emit_diag": "false"}
    out = validate_section(raw, schema, section="profile_controls")
    assert out["top_tag_limit"] == 12
    assert out["confidence_bin"] == 0.5
    assert out["emit_diag"] is False
