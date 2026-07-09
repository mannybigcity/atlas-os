import unittest
from unittest.mock import patch

import app


class AtlasChatHermesRouteTests(unittest.TestCase):
    def setUp(self):
        app.app.config.update(TESTING=True)
        self.client = app.app.test_client()

    def test_normal_chat_routes_to_hermes_atlas_bridge(self):
        with patch.object(app, "ask_hermes", return_value="Hermes Atlas reply") as ask_hermes:
            response = self.client.post("/chat", json={"message": "What should we focus on today?"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["response"], "Hermes Atlas reply")
        ask_hermes.assert_called_once_with("What should we focus on today?")

    def test_direct_status_still_uses_fast_local_response(self):
        with patch.object(app, "ask_hermes", return_value="should not be used") as ask_hermes:
            response = self.client.post("/chat", json={"message": "atlas status"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("ATLAS is online", response.get_json()["response"])
        ask_hermes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
