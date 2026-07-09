import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

import app
from skills.commerce import etsy_connector


class EtsyConnectorTests(unittest.TestCase):
    def test_pkce_s256_challenge_matches_rfc7636_reference(self):
        verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        expected = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"

        challenge = etsy_connector.pkce_s256_challenge(verifier)

        self.assertEqual(challenge, expected)
        self.assertNotIn("=", challenge)

    def test_generated_verifier_and_challenge_are_base64url_and_related(self):
        verifier, challenge = etsy_connector.generate_pkce_pair()

        self.assertGreaterEqual(len(verifier), 43)
        self.assertLessEqual(len(verifier), 128)
        self.assertNotIn("=", verifier)
        expected = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode("ascii")).digest()
        ).decode("ascii").rstrip("=")
        self.assertEqual(challenge, expected)

    def test_authorization_url_uses_etsy_pkce_read_only_scopes(self):
        url, state, verifier = etsy_connector.build_authorization_url(
            keystring="test-key",
            redirect_uri="https://example.com/etsy/callback",
            code_verifier="abc123verifier",
            state="state-123",
        )
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        self.assertEqual("https://www.etsy.com/oauth/connect", f"{parsed.scheme}://{parsed.netloc}{parsed.path}")
        self.assertEqual(query["response_type"], ["code"])
        self.assertEqual(query["client_id"], ["test-key"])
        self.assertEqual(query["redirect_uri"], ["https://example.com/etsy/callback"])
        self.assertEqual(query["scope"], ["shops_r listings_r"])
        self.assertEqual(query["state"], ["state-123"])
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertEqual(query["code_challenge"], [etsy_connector.pkce_s256_challenge("abc123verifier")])
        self.assertEqual(state, "state-123")
        self.assertEqual(verifier, "abc123verifier")

    def test_dotenv_loader_reads_keystring_and_shared_secret_without_python_dotenv(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text(
                "ETSY_KEYSTRING=abc123\nETSY_SHARED_SECRET=secret456\n",
                encoding="utf-8",
            )

            config = etsy_connector.load_etsy_config(env_path)

        self.assertEqual(config.keystring, "abc123")
        self.assertEqual(config.shared_secret, "secret456")

    def test_save_tokens_safely_updates_env_and_creates_backup_without_printing_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text("ETSY_KEYSTRING=abc123\nETSY_SHARED_SECRET=secret456\n", encoding="utf-8")

            result = etsy_connector.save_tokens_safely(
                {"access_token": "access-token", "refresh_token": "refresh-token"},
                env_path=env_path,
            )
            updated = env_path.read_text(encoding="utf-8")

            self.assertIn("ETSY_ACCESS_TOKEN=access-token", updated)
            self.assertIn("ETSY_REFRESH_TOKEN=refresh-token", updated)
            self.assertTrue(Path(result["backup_path"]).exists())
            self.assertEqual(result["saved"], ["ETSY_ACCESS_TOKEN", "ETSY_REFRESH_TOKEN"])

    def test_exchange_code_uses_token_url_without_write_scope_or_customer_side_effects(self):
        calls = []

        def fake_post(url, form, headers):
            calls.append((url, form, headers))
            return {"access_token": "user.access", "refresh_token": "refresh"}

        tokens = etsy_connector.exchange_code_for_tokens(
            code="auth-code",
            redirect_uri="https://example.com/etsy/callback",
            code_verifier="verifier",
            keystring="test-key",
            post_form=fake_post,
        )

        self.assertEqual(tokens["access_token"], "user.access")
        self.assertEqual(calls[0][0], "https://api.etsy.com/v3/public/oauth/token")
        self.assertEqual(calls[0][1]["grant_type"], "authorization_code")
        self.assertEqual(calls[0][1]["client_id"], "test-key")
        self.assertEqual(calls[0][1]["code_verifier"], "verifier")
        self.assertNotIn("listings_w", json.dumps(calls[0]))
        self.assertNotIn("transactions_w", json.dumps(calls[0]))

    def test_verify_read_only_connection_uses_shops_read_endpoint_only(self):
        calls = []

        def fake_get(url, headers):
            calls.append((url, headers))
            return {"count": 1, "results": [{"shop_id": 123, "shop_name": "SIS"}]}

        result = etsy_connector.verify_read_only_connection(
            keystring="test-key",
            shared_secret="test-secret",
            access_token="98765.access-token",
            get_json=fake_get,
        )

        self.assertTrue(result["connected"])
        self.assertEqual(calls[0][0], "https://api.etsy.com/v3/application/users/98765/shops")
        self.assertEqual(calls[0][1]["x-api-key"], "test-key:test-secret")
        self.assertEqual(calls[0][1]["Authorization"], "Bearer 98765.access-token")


class EtsyRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        app.app.config.update(TESTING=True)
        self.pending_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.pending_dir.cleanup)
        self.pending_path = Path(self.pending_dir.name) / "etsy_oauth_pending.json"
        self.pending_path_patch = patch.object(app, "ETSY_OAUTH_PENDING_PATH", str(self.pending_path))
        self.pending_path_patch.start()
        self.addCleanup(self.pending_path_patch.stop)

    def test_etsy_connect_redirects_to_etsy_authorization_with_read_only_scopes(self):
        config = etsy_connector.EtsyConfig(keystring="route-key", shared_secret="route-secret")
        redirect_uri = "https://example-tunnel.ngrok-free.app/etsy/callback"
        with patch.object(app.etsy_connector, "load_etsy_config", return_value=config), \
            patch.object(app.etsy_connector, "read_dotenv", return_value={"ETSY_REDIRECT_URI": redirect_uri}), \
            patch.object(app.app.logger, "info") as debug_log:
            response = self.client.get("/etsy/connect", base_url="https://puter.local")

        self.assertEqual(response.status_code, 302)
        location = response.headers["Location"]
        parsed = urlparse(location)
        query = parse_qs(parsed.query)
        self.assertEqual("https://www.etsy.com/oauth/connect", f"{parsed.scheme}://{parsed.netloc}{parsed.path}")
        self.assertEqual(query["client_id"], ["route-key"])
        self.assertEqual(query["redirect_uri"], [redirect_uri])
        self.assertEqual(query["scope"], ["shops_r listings_r"])
        self.assertNotIn("listings_w", query["scope"][0])
        pending = json.loads(self.pending_path.read_text(encoding="utf-8"))
        self.assertEqual(pending["expected_state"], query["state"][0])
        self.assertTrue(pending["code_verifier"])
        debug_log.assert_any_call("Etsy OAuth redirect_uri: %s", redirect_uri)
        debug_log.assert_any_call("Etsy OAuth authorization URL: %s", location)

    def test_etsy_connect_requires_configured_redirect_uri(self):
        config = etsy_connector.EtsyConfig(keystring="route-key", shared_secret="route-secret")
        with patch.object(app.etsy_connector, "load_etsy_config", return_value=config), \
            patch.object(app.etsy_connector, "read_dotenv", return_value={}), \
            patch.dict("os.environ", {}, clear=True):
            response = self.client.get("/etsy/connect", base_url="https://puter.local")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required Etsy .env value: ETSY_REDIRECT_URI", response.get_json()["error"])

    def test_etsy_callback_exchanges_code_and_saves_tokens(self):
        config = etsy_connector.EtsyConfig(keystring="route-key", shared_secret="route-secret")
        saved = []

        self.pending_path.write_text(
            json.dumps({"expected_state": "state-abc", "code_verifier": "verifier-xyz"}),
            encoding="utf-8",
        )

        redirect_uri = "https://example-tunnel.ngrok-free.app/etsy/callback"
        with patch.object(app.etsy_connector, "load_etsy_config", return_value=config), \
            patch.object(app.etsy_connector, "read_dotenv", return_value={"ETSY_REDIRECT_URI": redirect_uri}), \
            patch.object(app.etsy_connector, "exchange_code_for_tokens", return_value={"access_token": "access", "refresh_token": "refresh"}) as exchange, \
            patch.object(app.etsy_connector, "save_tokens_safely", side_effect=lambda tokens, env_path=None: saved.append(tokens) or {"saved": ["ETSY_ACCESS_TOKEN", "ETSY_REFRESH_TOKEN"], "backup_path": "backup.env"}):
            response = self.client.get("/etsy/callback?code=code-123&state=state-abc")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Etsy OAuth connection saved", response.data)
        exchange.assert_called_once()
        self.assertEqual(exchange.call_args.kwargs["redirect_uri"], redirect_uri)
        self.assertEqual(saved[0]["access_token"], "access")
        self.assertEqual(saved[0]["refresh_token"], "refresh")
        self.assertFalse(self.pending_path.exists())

    def test_etsy_callback_returns_debug_error_when_pending_file_is_missing(self):
        response = self.client.get("/etsy/callback?code=code-123&state=state-abc")

        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"], "Missing pending Etsy OAuth file. Restart /etsy/connect.")
        self.assertEqual(payload["debug"]["pending_path"], str(self.pending_path))
        self.assertTrue(payload["debug"]["returned_state_present"])

    def test_etsy_test_route_verifies_read_only_connection(self):
        config = etsy_connector.EtsyConfig(
            keystring="route-key",
            shared_secret="route-secret",
            access_token="98765.access-token",
            refresh_token="refresh",
        )
        with patch.object(app.etsy_connector, "load_etsy_config", return_value=config), \
            patch.object(app.etsy_connector, "verify_read_only_connection", return_value={"connected": True, "shop_count": 1, "shops": [{"shop_id": 123}]}) as verify:
            response = self.client.get("/etsy/test")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        verify.assert_called_once_with(keystring="route-key", shared_secret="route-secret", access_token="98765.access-token")

    def test_etsy_test_route_refreshes_expired_access_token_without_printing_tokens(self):
        config = etsy_connector.EtsyConfig(
            keystring="route-key",
            shared_secret="route-secret",
            access_token="98765.expired-token",
            refresh_token="refresh-token",
        )
        verify_results = [
            etsy_connector.EtsyOAuthError('Etsy API read-only check failed with HTTP 401: {"error":"invalid_token"}'),
            {"connected": True, "shop_count": 1, "shops": [{"shop_id": 123}]},
        ]
        refreshed_tokens = {"access_token": "98765.fresh-token", "refresh_token": "new-refresh-token"}

        with patch.object(app.etsy_connector, "load_etsy_config", return_value=config), \
            patch.object(app.etsy_connector, "verify_read_only_connection", side_effect=verify_results) as verify, \
            patch.object(app.etsy_connector, "refresh_access_token", return_value=refreshed_tokens) as refresh, \
            patch.object(app.etsy_connector, "save_tokens_safely", return_value={"saved": ["ETSY_ACCESS_TOKEN", "ETSY_REFRESH_TOKEN"], "backup_path": "backup.env"}) as save:
            response = self.client.get("/etsy/test")

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertTrue(payload["token_refreshed"])
        self.assertNotIn("fresh-token", response.get_data(as_text=True))
        refresh.assert_called_once_with(refresh_token="refresh-token", keystring="route-key")
        save.assert_called_once_with(refreshed_tokens, env_path=app.ETSY_ENV_PATH)
        self.assertEqual(verify.call_count, 2)
        self.assertEqual(verify.call_args_list[1].kwargs["access_token"], "98765.fresh-token")


if __name__ == "__main__":
    unittest.main()
