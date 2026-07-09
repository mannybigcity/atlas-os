import os
import unittest

os.environ.setdefault("ATLAS_ADMIN_USERNAME", "atlas-admin-test")
os.environ.setdefault("ATLAS_ADMIN_PASSWORD", "Correct-Horse-Atlas-119!")
os.environ.setdefault("FLASK_SECRET_KEY", "atl119-test-secret")

import app


class AtlasAdminAuthTest(unittest.TestCase):
    def setUp(self):
        app.app.config.update(TESTING=True, SECRET_KEY="atl119-test-secret")
        self.client = app.app.test_client()

    def login(self):
        return self.client.post("/login", data={
            "username": "atlas-admin-test",
            "password": "Correct-Horse-Atlas-119!",
            "next": "/app",
        }, follow_redirects=False)

    def test_protected_app_routes_redirect_to_login_before_session(self):
        for route in ["/app", "/dashboard", "/missions", "/crm", "/design-gallery", "/commerce-command-center"]:
            with self.subTest(route=route):
                response = self.client.get(route, follow_redirects=False)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login", response.headers["Location"])
                self.assertIn("next=", response.headers["Location"])

    def test_mission_api_does_not_expose_executive_messages_without_session(self):
        response = self.client.get("/api/missions/list")
        self.assertEqual(response.status_code, 401)
        payload = response.get_json()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"], "Atlas admin login required.")

    def test_wrong_login_fails_without_creating_session(self):
        response = self.client.post("/login", data={
            "username": "atlas-admin-test",
            "password": "wrong-password",
            "next": "/app",
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Invalid Atlas admin credentials", response.data)
        self.assertEqual(self.client.get("/app").status_code, 302)

    def test_correct_login_enters_app_and_logout_reprotects(self):
        login_response = self.login()
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.headers["Location"], "/app")

        app_response = self.client.get("/app")
        self.assertEqual(app_response.status_code, 200)
        self.assertIn(b"THE LION'S DEN", app_response.data)
        self.assertIn(b"Good Morning Manny", app_response.data)
        self.assertIn(b"Waiting for PayPal connection", app_response.data)
        self.assertIn(b"data-atlas-page=\"dashboard\"", app_response.data)
        self.assertIn(b"/missions", app_response.data)
        self.assertIn(b"/crm", app_response.data)
        self.assertIn(b"/commerce-command-center", app_response.data)
        self.assertIn(b"/design-gallery", app_response.data)
        self.assertIn(b"/logout", app_response.data)

        api_response = self.client.get("/api/missions/list")
        self.assertEqual(api_response.status_code, 200)
        self.assertIn("executive_messages", api_response.get_json())

        logout_response = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(logout_response.status_code, 302)
        self.assertIn("/login", logout_response.headers["Location"])
        self.assertEqual(self.client.get("/app").status_code, 302)

    def test_mission_control_module_does_not_merge_client_portal(self):
        self.login()

        response = self.client.get("/missions")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The Lion's Den", response.data)
        self.assertIn(b"Customer Command", response.data)
        self.assertNotIn(b"QTIME Dashboard", response.data)
        self.assertNotIn(b"/qtime-productions", response.data)

    def test_unsafe_next_values_fall_back_to_app(self):
        response = self.client.post("/login", data={
            "username": "atlas-admin-test",
            "password": "Correct-Horse-Atlas-119!",
            "next": "https://evil.example/app",
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/app")


if __name__ == "__main__":
    unittest.main()
