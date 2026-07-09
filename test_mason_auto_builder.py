import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agents import mason_auto_builder


class MasonAutoBuilderSafetyTests(unittest.TestCase):
    def make_project(self):
        temp_dir = tempfile.TemporaryDirectory()
        project = Path(temp_dir.name)
        (project / "agents").mkdir()
        (project / "skills").mkdir()
        (project / "agents" / "mason_auto_builder.py").write_text("print('builder')\n", encoding="utf-8")
        (project / "skills" / "mason_skill.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        return temp_dir, project

    def test_mason_plan_builder_creates_backups_before_returning_hermes_plan(self):
        temp_dir, project = self.make_project()
        self.addCleanup(temp_dir.cleanup)

        with patch.object(mason_auto_builder, "PROJECT_ROOT", project), patch.object(
            mason_auto_builder, "mason_ask_hermes", return_value="PLAN"
        ):
            result = mason_auto_builder.mason_plan_builder_task("improve mason")

        self.assertEqual(result["hermes_plan"], "PLAN")
        self.assertTrue(result["backup_directory"])
        backup_dir = Path(result["backup_directory"])
        self.assertTrue(backup_dir.exists())
        backed_up_files = {backup["file"] for backup in result["backups_created"]}
        self.assertIn("agents/mason_auto_builder.py", backed_up_files)
        self.assertIn("skills/mason_skill.py", backed_up_files)
        for backup in result["backups_created"]:
            self.assertTrue(Path(backup["backup_path"]).exists())

    def test_mason_plan_builder_runs_python_check_before_returning_hermes_plan(self):
        temp_dir, project = self.make_project()
        self.addCleanup(temp_dir.cleanup)

        with patch.object(mason_auto_builder, "PROJECT_ROOT", project), patch.object(
            mason_auto_builder, "mason_ask_hermes", return_value="PLAN"
        ):
            result = mason_auto_builder.mason_plan_builder_task("improve mason")

        self.assertTrue(result["python_check"]["passed"])
        self.assertTrue(result["python_check"]["command"])
        self.assertIn("agents/mason_auto_builder.py", result["python_check"]["checked_files"])
        self.assertIn("skills/mason_skill.py", result["python_check"]["checked_files"])

    def test_mason_plan_builder_blocks_hermes_plan_when_python_check_fails(self):
        temp_dir, project = self.make_project()
        self.addCleanup(temp_dir.cleanup)
        (project / "skills" / "mason_skill.py").write_text("def broken(:\n", encoding="utf-8")

        with patch.object(mason_auto_builder, "PROJECT_ROOT", project), patch.object(
            mason_auto_builder, "mason_ask_hermes", return_value="PLAN"
        ) as fake_hermes:
            result = mason_auto_builder.mason_plan_builder_task("improve mason")

        self.assertFalse(result["python_check"]["passed"])
        self.assertIsNone(result["hermes_plan"])
        fake_hermes.assert_not_called()
        self.assertIn("failed", result["status"].lower())


if __name__ == "__main__":
    unittest.main()
