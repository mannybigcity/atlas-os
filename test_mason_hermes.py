import unittest
from unittest.mock import patch

from skills.mason_hermes_skill import mason_ask_hermes


class MasonHermesSkillTest(unittest.TestCase):
    def test_mason_ask_hermes_delegates_with_mason_context(self):
        with patch("skills.mason_hermes_skill.ask_hermes", return_value="ok") as ask_hermes:
            response = mason_ask_hermes("Build safely")

        self.assertEqual(response, "ok")
        prompt = ask_hermes.call_args.args[0]
        self.assertIn("Mason is the builder", prompt)
        self.assertIn("Build safely", prompt)


if __name__ == "__main__":
    unittest.main()