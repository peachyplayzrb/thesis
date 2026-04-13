# Code Size Analysis & Remediation Plan

**Scope:** `07_implementation/src/` — 119 Python files, ~22,700 lines  
**Date:** 2026-04-12

---

## Part 1: Why the Code Is So Large

### 1.1 Total Breakdown by Module

| Lines | Files | Module              | Primary Role                        |
|------:|------:|---------------------|-------------------------------------|
| 2,581 |    15 | alignment           | Seed table + BL-003 contracts       |
| 2,141 |     9 | ingestion           | Spotify API export + resilience     |
| 2,137 |     2 | run_config          | Config defaults, validation, resolve |
| 2,091 |    10 | retrieval           | BL-005 candidate filtering          |
| 1,994 |    16 | shared_utils        | Constants, I/O, parsing helpers     |
| 1,987 |    10 | scoring             | BL-006 candidate scoring            |
| 1,981 |    14 | controllability     | BL-011 scenario analysis            |
| 1,788 |     8 | quality             | BL-014 quality suite + sanity       |
| 1,552 |     8 | playlist            | BL-007 assembly + rules             |
| 1,356 |     5 | profile             | BL-004 preference profile           |
| 1,026 |     8 | orchestration       | BL-013 pipeline orchestration       |
|   813 |     2 | reproducibility     | BL-010 replay verification          |
|   757 |     3 | observability       | BL-009 diagnostics                  |
|   470 |     6 | transparency        | BL-008 contributor explanations     |
|    53 |     2 | data_layer          | Dataset path stubs                  |

### 1.2 The Five Root Causes

#### Cause A: Imperative Config Validation (~3,500 lines, ~15% of total)

**Where:** `run_config/run_config_utils.py` (2,137 lines), plus `resolve_runtime_controls()` methods in every `stage.py`

**What's happening:** Every config field is validated by hand, one at a time. The file contains:
- `_build_default_run_config()` — 120 lines manually assembling defaults from constants
- `resolve_effective_run_config()` — ~500 lines validating every field with its own 3-5 line block
- 12 separate `resolve_blXXX_controls()` functions that re-extract and re-cast the same fields
- 18+ coercion/validation helper functions that are near-duplicates of each other

**Example of the pattern (repeated ~100 times):**
```python
profile_controls["top_tag_limit"] = _coerce_positive_int(
    profile_controls.get("top_tag_limit"),
    DEFAULT_RUN_CONFIG["profile_controls"]["top_tag_limit"],
)
profile_controls["top_genre_limit"] = _coerce_positive_int(
    profile_controls.get("top_genre_limit"),
    DEFAULT_RUN_CONFIG["profile_controls"]["top_genre_limit"],
)
profile_controls["top_lead_genre_limit"] = _coerce_positive_int(
    profile_controls.get("top_lead_genre_limit"),
    DEFAULT_RUN_CONFIG["profile_controls"]["top_lead_genre_limit"],
)
```

Then each stage re-does the same coercion when consuming the controls:
```python
# retrieval/stage.py — 60 lines of this
profile_top_lead_genre_limit=RetrievalStage._safe_int(payload.get("profile_top_lead_genre_limit"), 6),
profile_top_tag_limit=RetrievalStage._safe_int(payload.get("profile_top_tag_limit"), 10),
profile_top_genre_limit=RetrievalStage._safe_int(payload.get("profile_top_genre_limit"), 8),
semantic_strong_keep_score=RetrievalStage._safe_int(payload.get("semantic_strong_keep_score"), 2),
# ... 30 more lines
```

**Impact:** This single pattern accounts for roughly 3,500 lines across the codebase. The actual logic (what fields exist, what types they are, what their defaults are) could be expressed in ~200 lines of schema definitions.

---

#### Cause B: Near-Duplicate Coercion Helpers (~300 lines)

**Where:** `run_config/run_config_utils.py` lines 186-476, plus `_safe_float`/`_safe_int`/`_clamp_0_1`/`_mapping`/`_string_list` duplicated in `retrieval/stage.py`, `scoring/stage.py`, `reproducibility/main.py`

**The duplicates:**
| Function                             | What it does                  | Duplicated in     |
|--------------------------------------|-------------------------------|-------------------|
| `_coerce_positive_int`               | int(x) > 0 or default        | run_config        |
| `_validate_positive_int_or_error`    | int(x) > 0 or raise          | run_config        |
| `_coerce_optional_positive_int`      | int(x) > 0 or None           | run_config        |
| `_validate_non_negative_int`         | int(x) >= 0 or raise         | run_config        |
| `_coerce_non_negative_float`         | float(x) >= 0 or default     | run_config        |
| `_validate_non_negative_float`       | float(x) >= 0 or raise       | run_config        |
| `_validate_fraction_zero_to_one`     | float(x) in [0,1] or raise   | run_config        |
| `_coerce_fraction_zero_to_one`       | float(x) in [0,1] or default | run_config        |
| `_coerce_min_positive_float`         | float(x) >= min or default    | run_config        |
| `_validate_positive_float`           | float(x) > 0 or raise        | run_config        |
| `_coerce_bool` / `_validate_bool_like` | bool parse with same logic  | run_config        |
| `_safe_float` / `_safe_int`          | try/except parse              | retrieval, scoring, reproducibility |
| `_clamp_0_1`                         | max(0, min(1, x))            | retrieval, scoring |
| `_mapping` / `_string_list`          | dict/list coercion            | retrieval, reproducibility |

These are all variations of "parse a value, apply a bound, return a fallback." The difference between them is: (a) whether they raise or return a default, (b) the numeric bounds, (c) whether the result is optional. That's three parameters, not 18 functions.

---

#### Cause C: Defaults Defined Three Times (~800 lines)

**Where:** `shared_utils/constants.py` (396 lines) → `run_config_utils.py:_build_default_run_config()` (120 lines) → each `resolve_blXXX_controls()` function re-specifying the same defaults as fallback arguments

**The chain:**
1. `constants.py` defines `DEFAULT_RETRIEVAL_CONTROLS["numeric_support_min_score"] = 1.0`
2. `_build_default_run_config()` copies it: `"numeric_support_min_score": safe_float(DEFAULT_RETRIEVAL_CONTROLS["numeric_support_min_score"])`
3. `resolve_effective_run_config()` validates it: `retrieval_controls["numeric_support_min_score"] = _coerce_non_negative_float(..., float(defaults["numeric_support_min_score"]))`
4. `resolve_bl005_controls()` re-extracts it: `"numeric_support_min_score": _coerce_non_negative_float(retrieval.get("numeric_support_min_score"), ...)`
5. `RetrievalStage.resolve_runtime_controls()` re-parses it: `numeric_support_min_score=RetrievalStage._safe_float(payload.get("numeric_support_min_score"), 1.0)`

**One config field touches five locations.** Multiply by ~80 fields and you get thousands of lines that all express the same information.

---

#### Cause D: Repeated Stage Ceremony (~1,500 lines)

**Where:** `profile/stage.py`, `retrieval/stage.py`, `scoring/stage.py`, `playlist/stage.py`, `quality/suite.py`, `reproducibility/main.py`, `observability/main.py`

Every pipeline stage independently implements the same workflow:
1. `__init__` with `self.root = root or impl_root()`
2. `resolve_paths()` returning a dataclass of Path objects
3. `resolve_runtime_controls()` coercing a dict into a typed dataclass
4. `load_inputs()` reading JSON/CSV and raising if malformed
5. `run()` with timing: `start_time = time.time()`, `run_id = f"BLXXX-..."`, then `elapsed = time.time() - start_time`
6. Build a summary dict with `run_id`, `schema_version`, `config`, `counts`, `elapsed_seconds`, `output_files`, `output_hashes_sha256`
7. `write_json()` / `open_text_write()` for each output artifact
8. Logger calls: `logger.info("BL-XXX complete.")`, `logger.info("path=%s", ...)`

**Example — the `run()` method across three stages:**
```python
# profile/stage.py
def run(self) -> ProfileArtifacts:
    paths = self.resolve_paths()
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    controls = self.resolve_runtime_controls()
    inputs = self.load_inputs(paths)
    start_time = time.time()
    run_id = f"BL004-PROFILE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    # ... stage-specific work ...

# scoring/stage.py
def run(self) -> ScoringArtifacts:
    paths = self.resolve_paths()
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    ensure_paths_exist([paths.profile_path, paths.filtered_candidates_path], stage_label="BL-006")
    inputs = self.load_inputs(paths)
    runtime_controls = self.resolve_runtime_controls()
    start_time = time.time()
    run_id = f"BL006-SCORE-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    # ... stage-specific work ...

# retrieval/stage.py — same pattern again
```

The boilerplate (path setup, timing, run ID, hashing outputs, writing summary JSON) is ~100-200 lines per stage. Across 7 stages, that's ~1,000-1,500 lines of structural repetition.

---

#### Cause E: Inline Data as Code (~600 lines)

**Where:** Column lists, field name arrays, feature spec dictionaries scattered across stage files

Examples:
- `retrieval/stage.py` lines 29-75: 45-line `DECISION_FIELDS` list
- `shared_utils/constants.py` lines 350-395: `NUMERIC_FEATURE_SPECS` dict (each feature = 5 lines of boilerplate)
- `profile/stage.py` lines 28-58: `NUMERIC_FEATURE_COLUMNS`, `SUMMARY_FEATURE_COLUMNS`, `BL004_REQUIRED_SEED_COLUMNS`
- `scoring/models.py`: `SCORED_CANDIDATE_FIELDS`, `NUMERIC_COMPONENTS`

These are static data declarations. They're not wrong, but they inflate the perceived complexity of each file.

---

## Part 2: Fixes to Make Before Refactoring

These are correctness and consistency issues to resolve first, so that the refactor starts from a clean baseline.

### Fix 1: Eliminate Redundant Double-Parsing

Several values are parsed multiple times through the call chain. Before refactoring, audit for cases where a value is coerced in `resolve_effective_run_config()` and then coerced again in the stage's `resolve_runtime_controls()`. After the first coercion the value is already the correct type — the second parse is dead code that masks bugs (if the first coercion returned a wrong type, the second silently fixes it instead of failing).

**Files to check:**
- `retrieval/stage.py` `resolve_runtime_controls()` — re-parses values already validated by `resolve_bl005_controls()`
- `scoring/stage.py` `resolve_runtime_controls()` — same issue with `resolve_bl006_controls()`
- `profile/stage.py` `_sanitize_controls()` — re-casts `int(str(controls["top_tag_limit"]))` on a value that's already an int

### Fix 2: Consolidate `_safe_float` / `_safe_int` / `_clamp_0_1` Copies

Before any structural refactor, delete the per-stage copies and import from one place. Currently:
- `retrieval/stage.py` defines `_safe_float`, `_safe_int`, `_clamp_0_1`, `_mapping`, `_string_list` as static methods
- `scoring/stage.py` defines `_to_float`, `_clamp_0_1` as static methods
- `reproducibility/main.py` defines `_object_mapping`, `_object_dict_list`, `_string_list` as module functions
- `shared_utils/parsing.py` already exports `safe_float`, `safe_int`

These should all be imports from `shared_utils.parsing`, not redefined per file.

### Fix 3: Resolve Default Value Conflicts

Some defaults appear in `constants.py` AND are hardcoded as literal fallbacks in stage code. If these ever diverge, the system uses different defaults depending on whether the value came through run_config or was omitted entirely.

**Example:**
```python
# constants.py says:
DEFAULT_NUMERIC_SUPPORT_MIN_SCORE = 1.0

# But retrieval/stage.py hardcodes:
numeric_support_min_score=RetrievalStage._safe_float(payload.get("numeric_support_min_score"), 1.0)
```

The `1.0` literal in the stage must always match the constant. Search for all hardcoded numeric defaults in stage files and replace them with constant imports.

### Fix 4: Pin Down the `resolve_blXXX_controls()` Return Types

The 12 `resolve_blXXX_controls()` functions in `run_config_utils.py` all return `dict[str, Any]`. The consuming stages then have to re-parse every field because there's no type guarantee. Before refactoring, decide: should these return typed dataclasses (making downstream parsing unnecessary) or should they remain dicts (keeping the schema-driven approach simpler)?

**Recommendation:** The typed dataclass approach is better for your thesis because it gives you static type checking. But it only works if the dataclass is the single source of truth for the field names, types, and defaults — not a third copy of the same information.

---

## Part 3: Target Architecture

### 3.1 Schema-Driven Config Validation

**Replace** the 2,137-line `run_config_utils.py` with a declarative schema.

**Current approach (imperative):**
```python
# 5 lines per field x ~80 fields = ~400 lines just for validation
profile_controls["top_tag_limit"] = _coerce_positive_int(
    profile_controls.get("top_tag_limit"),
    DEFAULT_RUN_CONFIG["profile_controls"]["top_tag_limit"],
)
```

**Target approach (declarative):**
```python
# Schema definition — one line per field
CONFIG_SCHEMA = {
    "profile_controls": {
        "top_tag_limit":    FieldSpec(type="positive_int", default=10),
        "top_genre_limit":  FieldSpec(type="positive_int", default=8),
        "top_lead_genre_limit": FieldSpec(type="positive_int", default=6),
        "confidence_weighting_mode": FieldSpec(
            type="enum",
            choices=["linear_half_bias", "direct_confidence", "none"],
            default="linear_half_bias",
        ),
        "confidence_bin_high_threshold": FieldSpec(type="fraction", default=0.90),
        "confidence_bin_medium_threshold": FieldSpec(type="fraction", default=0.50),
        "emit_profile_policy_diagnostics": FieldSpec(type="bool", default=True),
    },
    "retrieval_controls": {
        "semantic_strong_keep_score": FieldSpec(type="positive_int", default=2),
        "numeric_support_min_score": FieldSpec(type="non_negative_float", default=1.0),
        "use_weighted_semantics": FieldSpec(type="bool", default=False),
        # ...
    },
    # ...
}
```

**The engine — one function replaces hundreds of manual blocks:**
```python
@dataclass
class FieldSpec:
    type: str           # "positive_int", "non_negative_float", "fraction", "bool", "enum", "string_list"
    default: Any
    choices: list[str] | None = None    # for enum type
    min_val: float | None = None        # for numeric types
    max_val: float | None = None

def validate_section(raw: dict, schema: dict[str, FieldSpec]) -> dict:
    result = {}
    for key, spec in schema.items():
        result[key] = coerce_field(raw.get(key), spec, context=key)
    return result

def coerce_field(value: Any, spec: FieldSpec, context: str) -> Any:
    if value is None:
        return spec.default
    match spec.type:
        case "positive_int":
            parsed = int(value)
            if parsed <= 0: raise RunConfigError(f"{context} must be > 0")
            return parsed
        case "non_negative_float":
            parsed = float(value)
            if parsed < 0: raise RunConfigError(f"{context} must be >= 0")
            return parsed
        case "fraction":
            parsed = float(value)
            if not (0.0 <= parsed <= 1.0): raise RunConfigError(f"{context} must be in [0, 1]")
            return parsed
        case "bool":
            return _coerce_bool(value, spec.default)
        case "enum":
            token = str(value).strip().lower()
            return token if token in spec.choices else spec.default
        case "string_list":
            return _coerce_str_list(value) or spec.default
```

**What this eliminates:**
- `_build_default_run_config()` — defaults come from the schema
- `resolve_effective_run_config()` body — replaced by `validate_section()` calls
- All 18 coercion/validation helpers — replaced by one `coerce_field()` with a match statement
- Hardcoded fallback literals in stage files — the schema is the single source of truth

**Estimated reduction:** ~1,600 lines removed from `run_config_utils.py` alone.

---

### 3.2 Unified Coercion Module

**Replace** the scattered helper functions with a single module.

**Target file:** `shared_utils/coerce.py`

```python
def to_int(value, *, default, min_val=None, max_val=None, strict=False):
    """Single function replacing 6 int coercion variants."""

def to_float(value, *, default, min_val=None, max_val=None, strict=False):
    """Single function replacing 7 float coercion variants."""

def to_bool(value, *, default):
    """Single function replacing _coerce_bool and _validate_bool_like."""

def to_enum(value, *, choices, default):
    """Single function replacing inline enum validation blocks."""

def to_str_list(value, *, default=None, allowed=None):
    """Single function replacing _coerce_str_list, _normalize_allowed_tokens, _normalize_string_tokens."""

def clamp(value, low=0.0, high=1.0):
    """Single function replacing _clamp_0_1 copies."""
```

Then delete:
- `RetrievalStage._safe_float`, `._safe_int`, `._clamp_0_1`, `._mapping`, `._string_list`
- `ScoringStage._to_float`, `._clamp_0_1`
- `reproducibility/main.py:_object_mapping`, `_object_dict_list`, `_string_list`
- All 18 `_coerce_*` / `_validate_*` functions in `run_config_utils.py`

**Estimated reduction:** ~250 lines removed, plus elimination of behavioral divergence risk.

---

### 3.3 Base Pipeline Stage

**Replace** the repeated ceremony in every `stage.py` with a shared base class.

```python
# shared_utils/base_stage.py

class PipelineStage:
    stage_id: str           # e.g. "BL-004"
    stage_label: str        # e.g. "PROFILE"

    def __init__(self, root: Path | None = None):
        self.root = root or impl_root()

    def run(self) -> Any:
        paths = self.resolve_paths()
        paths.output_dir.mkdir(parents=True, exist_ok=True)
        controls = self.resolve_controls()
        inputs = self.load_inputs(paths)

        start = time.time()
        run_id = f"{self.stage_id}-{self.stage_label}-{utc_timestamp()}"

        result = self.execute(run_id=run_id, paths=paths, controls=controls, inputs=inputs)

        elapsed = time.time() - start
        summary = self.build_summary(run_id=run_id, elapsed=elapsed, result=result)
        self.write_outputs(paths=paths, summary=summary)

        logger.info("%s complete.", self.stage_id)
        return result

    # Subclass implements these:
    def resolve_paths(self) -> Any: ...
    def resolve_controls(self) -> Any: ...
    def load_inputs(self, paths) -> Any: ...
    def execute(self, *, run_id, paths, controls, inputs) -> Any: ...
    def build_summary(self, *, run_id, elapsed, result) -> dict: ...
    def write_outputs(self, *, paths, summary) -> None: ...

    # Shared helpers available to all stages:
    @staticmethod
    def write_json(path: Path, payload: dict) -> None:
        with open_text_write(path) as f:
            json.dump(payload, f, indent=2, ensure_ascii=True)

    @staticmethod
    def hash_file(path: Path) -> str:
        return sha256_of_file(path)
```

Each stage then only contains its unique logic:
```python
class ProfileStage(PipelineStage):
    stage_id = "BL-004"
    stage_label = "PROFILE"

    def resolve_paths(self):
        # 10 lines — just the paths
    def execute(self, *, run_id, paths, controls, inputs):
        # The actual profile aggregation logic — the valuable part
```

**Estimated reduction:** ~150-200 lines per stage, ~1,000 lines total across 7 stages.

---

### 3.4 Centralize Field/Column Declarations

Move all column lists and feature specs into a dedicated registry instead of scattering them across files.

**Target file:** `shared_utils/field_registry.py`

```python
DECISION_FIELDS = [...]           # currently in retrieval/stage.py
SCORED_CANDIDATE_FIELDS = [...]   # currently in scoring/models.py
NUMERIC_FEATURE_SPECS = {...}     # currently in shared_utils/constants.py
SEED_REQUIRED_COLUMNS = [...]     # currently in profile/stage.py
SUMMARY_FEATURE_COLUMNS = [...]   # currently in profile/stage.py
```

This is a minor organizational change (~0 net line reduction) but it makes it obvious that these are data declarations, not logic.

---

## Part 4: Estimated Impact

| Refactor                          | Lines Removed | Risk  | Priority |
|-----------------------------------|---------------|-------|----------|
| Schema-driven config validation   | ~1,600        | Medium | 1 — highest impact |
| Unified coercion module           | ~250          | Low    | 2 — do first as foundation |
| Base pipeline stage               | ~1,000        | Medium | 3 — do after config is stable |
| Remove double-parsing in stages   | ~300          | Low    | 4 — cleanup |
| Centralize field declarations     | ~0 (reorg)    | Low    | 5 — optional |

**Total estimated reduction: ~3,000-3,500 lines (13-15% of codebase)**

The remaining ~19,000 lines are actual logic: ingestion resilience, scoring math, retrieval filtering, playlist assembly rules, quality checks, observability diagnostics. That code is appropriately sized for what it does.

---

## Part 5: Execution Order

1. **Create `shared_utils/coerce.py`** — consolidate all coercion helpers into one module. Update all imports. This is low-risk and creates the foundation for everything else.

2. **Replace hardcoded default literals in stages** — every `_safe_float(x, 1.0)` where `1.0` should be `DEFAULT_NUMERIC_SUPPORT_MIN_SCORE`. Prevents divergence.

3. **Build the schema-driven config validator** — define `CONFIG_SCHEMA`, implement `validate_section()` and `coerce_field()`, then incrementally replace sections of `resolve_effective_run_config()`.

4. **Collapse `resolve_blXXX_controls()` functions** — once the schema produces correctly-typed output, these become thin wrappers (or disappear entirely if stages consume the validated config directly).

5. **Extract `PipelineStage` base class** — move shared ceremony out of each stage. Do this last because it touches every stage file and you want config to be stable first.

Each step is independently valuable and testable. You don't have to do all five to see improvement — step 1-3 alone would cut ~2,000 lines.
