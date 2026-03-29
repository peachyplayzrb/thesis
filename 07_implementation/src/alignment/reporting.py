"""BL-003 output writing and summary assembly."""

from __future__ import annotations

from alignment.summary_builder import build_and_write_summary
from alignment.validation import validate_match_rate
from alignment.writers import (
    SEED_TABLE_FIELDNAMES,
    TRACE_FIELDNAMES,
    canonical_json_hash,
    write_alignment_outputs,
    write_source_scope_manifest,
)
