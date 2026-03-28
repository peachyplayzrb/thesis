from __future__ import annotations

import sys
import unittest
import importlib
from pathlib import Path
from unittest.mock import patch


SETUP_DIR = Path(__file__).resolve().parent
REPO_ROOT = SETUP_DIR.parent.parent
IMPL_NOTES_DIR = REPO_ROOT / "07_implementation" / "implementation_notes"

if str(IMPL_NOTES_DIR) not in sys.path:
    sys.path.insert(0, str(IMPL_NOTES_DIR))

runtime_resolver = importlib.import_module("bl000_shared_utils.stage_runtime_resolver")  # pyright: ignore[reportMissingImports]
load_positive_numeric_map_from_env = runtime_resolver.load_positive_numeric_map_from_env
resolve_run_config_path = runtime_resolver.resolve_run_config_path
resolve_stage_selection = runtime_resolver.resolve_stage_selection


class StageRuntimeResolverTests(unittest.TestCase):
    def test_resolve_stage_selection_returns_all_when_stage_ids_missing(self) -> None:
        stage_specs = [
            {"stage_id": "bl003", "label": "A"},
            {"stage_id": "bl004", "label": "B"},
        ]

        resolved = resolve_stage_selection({}, stage_specs)

        self.assertEqual(resolved, stage_specs)

    def test_resolve_stage_selection_preserves_canonical_order(self) -> None:
        stage_specs = [
            {"stage_id": "bl003", "label": "A"},
            {"stage_id": "bl004", "label": "B"},
            {"stage_id": "bl005", "label": "C"},
        ]

        resolved = resolve_stage_selection({"stage_ids": ["bl005", "bl003"]}, stage_specs)

        self.assertEqual([item["stage_id"] for item in resolved], ["bl003", "bl005"])

    def test_resolve_stage_selection_rejects_unknown_stage(self) -> None:
        stage_specs = [{"stage_id": "bl003", "label": "A"}]

        with self.assertRaises(RuntimeError):
            resolve_stage_selection({"stage_ids": ["bl999"]}, stage_specs)

    def test_resolve_run_config_path_reads_named_env_var(self) -> None:
        with patch.dict("os.environ", {"BL_RUN_CONFIG_PATH": "  path/to/config.json  "}, clear=False):
            self.assertEqual(resolve_run_config_path(), "path/to/config.json")

        with patch.dict("os.environ", {"CUSTOM_CONFIG": "custom.json"}, clear=False):
            self.assertEqual(resolve_run_config_path("CUSTOM_CONFIG"), "custom.json")

    def test_load_positive_numeric_map_filters_non_positive_and_non_numeric(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "BL_TEST_NUMERIC_JSON": '{"tempo": 15, "mode": 0, "key": -1, "bad": "x", "danceability": 0.75}'
            },
            clear=False,
        ):
            payload = load_positive_numeric_map_from_env("BL_TEST_NUMERIC_JSON")

        self.assertEqual(payload, {"tempo": 15.0, "danceability": 0.75})

    def test_load_positive_numeric_map_returns_empty_on_invalid_json(self) -> None:
        with patch.dict("os.environ", {"BL_TEST_NUMERIC_JSON": "{invalid json"}, clear=False):
            payload = load_positive_numeric_map_from_env("BL_TEST_NUMERIC_JSON")

        self.assertEqual(payload, {})

    def test_load_positive_numeric_map_returns_empty_on_non_object_json(self) -> None:
        with patch.dict("os.environ", {"BL_TEST_NUMERIC_JSON": "[1,2,3]"}, clear=False):
            payload = load_positive_numeric_map_from_env("BL_TEST_NUMERIC_JSON")

        self.assertEqual(payload, {})


if __name__ == "__main__":
    unittest.main()
