import json
import tempfile
import unittest
from pathlib import Path

import app


class MetaIntegrationServiceTests(unittest.TestCase):
    def test_meta_status_loads_dotenv_verifies_page_and_masks_secrets(self):
        from skills.meta_connector import get_meta_status

        with tempfile.TemporaryDirectory() as tempdir:
            env_path = Path(tempdir) / ".env"
            env_path.write_text(
                "META_APP_ID=app_123\n"
                "META_APP_SECRET=secret_456\n"
                "META_USER_ACCESS_TOKEN=user_token_789\n"
                "META_PAGE_ID=123456789012345\n"
                "META_PAGE_ACCESS_TOKEN=page_token_abc\n"
                "THREADS_APP_ID=threads_123\n",
                encoding="utf-8",
            )

            calls = []

            def fake_get_json(path, params):
                calls.append((path, dict(params)))
                if path == "/me":
                    return {"id": "user-1", "name": "Manny"}
                self.assertEqual(path, "/123456789012345")
                return {
                    "id": "123456789012345",
                    "name": "ATLAS for Entrepreneurs",
                    "picture": {"data": {"url": "https://example.test/page.jpg"}},
                    "instagram_business_account": {"id": "ig-1", "username": "atlas"},
                }

            status = get_meta_status(env_path=env_path, get_json=fake_get_json)

        self.assertEqual(status["status"], "connected")
        self.assertEqual(status["page"], "ATLAS for Entrepreneurs")
        self.assertEqual(status["page_id"], "configured")
        self.assertEqual(status["page_id_masked"], "***********2345")
        self.assertEqual(status["instagram"], "connected")
        self.assertEqual(status["threads"], "configured")
        self.assertEqual(status["profile_picture"], "https://example.test/page.jpg")
        self.assertIn("last_check", status)
        serialized = json.dumps(status)
        self.assertNotIn("secret_456", serialized)
        self.assertNotIn("user_token_789", serialized)
        self.assertNotIn("page_token_abc", serialized)
        self.assertEqual(calls[0][1]["access_token"], "user_token_789")
        self.assertEqual(calls[1][1]["access_token"], "page_token_abc")

    def test_meta_status_reports_missing_configuration_without_network(self):
        from skills.meta_connector import get_meta_status

        with tempfile.TemporaryDirectory() as tempdir:
            env_path = Path(tempdir) / ".env"
            env_path.write_text("META_APP_ID=app_123\n", encoding="utf-8")

            def fail_get_json(path, params):
                raise AssertionError("network should not be called when configuration is incomplete")

            status = get_meta_status(env_path=env_path, get_json=fail_get_json)

        self.assertEqual(status["status"], "not_configured")
        self.assertEqual(status["page"], "Not configured")
        self.assertEqual(status["page_id"], "missing")
        self.assertEqual(status["instagram"], "unknown")
        self.assertEqual(status["threads"], "not_configured")
        self.assertIn("missing_config", status)
        self.assertIn("META_PAGE_ACCESS_TOKEN", status["missing_config"])


class MetaIntegrationRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.original_get_meta_status = app.get_meta_status

    def tearDown(self):
        app.get_meta_status = self.original_get_meta_status

    def test_api_meta_status_returns_safe_json(self):
        app.get_meta_status = lambda env_path=None: {
            "status": "connected",
            "page": "ATLAS for Entrepreneurs",
            "page_id": "configured",
            "page_id_masked": "***********2345",
            "instagram": "connected",
            "threads": "configured",
            "profile_picture": "https://example.test/page.jpg",
            "last_check": "2026-07-03T00:00:00Z",
        }

        response = self.client.get("/api/meta/status")
        body = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "connected")
        self.assertEqual(body["page"], "ATLAS for Entrepreneurs")
        self.assertNotIn("access_token", json.dumps(body).lower())
        self.assertNotIn("app_secret", json.dumps(body).lower())

    def test_neural_core_contains_meta_integration_card(self):
        response = self.client.get("/neural")
        html = response.data.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Meta Integration", html)
        self.assertIn("/api/meta/status", html)
        self.assertIn("metaPageName", html)


if __name__ == "__main__":
    unittest.main()
