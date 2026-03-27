from __future__ import annotations

import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


SETUP_DIR = Path(__file__).resolve().parent
if str(SETUP_DIR) not in sys.path:
    sys.path.insert(0, str(SETUP_DIR))

import website_api_server as server


class WebsiteApiServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        server.initialize_app_state(bind="127.0.0.1", port=5501)
        cls.client = TestClient(server.app)

    def test_health_endpoint_reports_ok(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["server"]["port"], 5501)

    def test_stage_catalog_contains_seven_pipeline_stages(self) -> None:
        response = self.client.get("/api/pipeline/stages")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        stage_ids = [stage["stage_id"] for stage in payload["stages"]]
        self.assertEqual(len(stage_ids), 7)
        self.assertEqual(stage_ids[0], "bl003")
        self.assertEqual(stage_ids[-1], "bl009")

    def test_runtime_config_validate_accepts_known_good_payload(self) -> None:
        response = self.client.post(
            "/api/runtime/config/validate",
            json={
                "stage_params": {
                    "bl004": {"top_tag_limit": 12},
                    "bl006": {"numeric_thresholds": {"tempo": 15.0}},
                }
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["normalized_stage_params"]["bl004"]["top_tag_limit"], 12)

    def test_missing_api_route_returns_error_payload(self) -> None:
        response = self.client.get("/api/does-not-exist")

        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertIn("error", payload)

    def test_invalid_request_body_returns_error_payload(self) -> None:
        response = self.client.post(
            "/api/runtime/config/validate",
            json={"stage_params": ["not", "a", "dict"]},
        )

        self.assertEqual(response.status_code, 422)
        payload = response.json()
        self.assertEqual(payload["error"], "Request validation failed.")
        self.assertIn("details", payload)


if __name__ == "__main__":
    unittest.main()
