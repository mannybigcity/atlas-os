import unittest
from unittest.mock import Mock, patch

import atlas_hermes_bridge


class AtlasHermesBridgeTests(unittest.TestCase):
    def test_ask_hermes_uses_atlas_profile_chat_query(self):
        completed = Mock(returncode=0, stdout="Atlas through Hermes\n", stderr="")

        with patch.object(atlas_hermes_bridge.subprocess, "run", return_value=completed) as run:
            response = atlas_hermes_bridge.ask_hermes("What should we do next?")

        command = run.call_args.args[0]
        self.assertEqual(command[:4], ["hermes", "--profile", "atlas", "chat"])
        self.assertIn("-Q", command)
        self.assertIn("-q", command)
        self.assertIn("What should we do next?", command)
        self.assertEqual(response, "Atlas through Hermes")

    def test_ask_hermes_strips_cli_session_id_line(self):
        completed = Mock(returncode=0, stdout="session_id: 20260622_abc\nClean Atlas reply\n", stderr="")

        with patch.object(atlas_hermes_bridge.subprocess, "run", return_value=completed):
            response = atlas_hermes_bridge.ask_hermes("hello")

        self.assertEqual(response, "Clean Atlas reply")

    def test_ask_hermes_ignores_session_id_warning_on_stderr(self):
        completed = Mock(returncode=0, stdout="Clean Atlas reply\n", stderr="session_id: 20260622_abc\n")

        with patch.object(atlas_hermes_bridge.subprocess, "run", return_value=completed):
            response = atlas_hermes_bridge.ask_hermes("hello")

        self.assertEqual(response, "Clean Atlas reply")

    def test_ask_hermes_reports_failure_without_legacy_openai_path(self):
        completed = Mock(returncode=1, stdout="", stderr="profile failed")

        with patch.object(atlas_hermes_bridge.subprocess, "run", return_value=completed):
            response = atlas_hermes_bridge.ask_hermes("hello")

        self.assertIn("Hermes Atlas bridge failed", response)
        self.assertIn("profile failed", response)


if __name__ == "__main__":
    unittest.main()
