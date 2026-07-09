from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FORGE_FILE = ROOT / "skills" / "mason_infrastructure_forge.py"


def load_forge():
    spec = importlib.util.spec_from_file_location("mason_infrastructure_forge", FORGE_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MasonInfrastructureForgeTests(unittest.TestCase):
    def test_territory_manager_blueprint_creates_complete_system_with_manny_gate(self) -> None:
        forge = load_forge()
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            result = forge.forge_infrastructure_system("Territory Manager", project_root=project_root)

            self.assertEqual(result["status"], "forged_pending_manny_approval", json.dumps(result, indent=2))
            self.assertTrue(result["manny_approval_required"])
            self.assertTrue(result["approval_gate"]["required"])
            self.assertEqual(result["system_name"], "Territory Manager")
            self.assertIn("Manny", result["approval_gate"]["approver"])

            expected_paths = {
                "main_system": project_root / "territory_manager.py",
                "skills_blueprint": project_root / "RAMFAM_KINGDOM_BRAIN" / "04_MASON_FOUNDRY" / "TERRITORY_MANAGER_SKILLS.md",
                "test_file": project_root / "test_territory_manager.py",
                "data_folder": project_root / "RAMFAM_KINGDOM_BRAIN" / "07_TERRITORIES",
                "registry_update_notes": project_root / "RAMFAM_KINGDOM_BRAIN" / "04_MASON_FOUNDRY" / "TERRITORY_MANAGER_REGISTRY_UPDATE.md",
            }
            for key, path in expected_paths.items():
                self.assertEqual(Path(result["artifacts"][key]), path)
                self.assertTrue(path.exists(), f"missing {key}: {path}")

            main_text = expected_paths["main_system"].read_text(encoding="utf-8")
            test_text = expected_paths["test_file"].read_text(encoding="utf-8")
            skills_text = expected_paths["skills_blueprint"].read_text(encoding="utf-8")
            registry_text = expected_paths["registry_update_notes"].read_text(encoding="utf-8")
            self.assertIn("approval_required", main_text)
            self.assertIn("pending_manny_approval", main_text)
            self.assertIn("approval_required", test_text)
            self.assertIn("Manny approval required", skills_text)
            self.assertIn("registry update recommendation", registry_text.lower())
            self.assertIn("test_territory_manager.py", result["verification_command"])

    def test_existing_files_are_backed_up_before_being_replaced(self) -> None:
        forge = load_forge()
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            existing = project_root / "territory_manager.py"
            existing.write_text("WORKING = True\n", encoding="utf-8")

            result = forge.forge_infrastructure_system("Territory Manager", project_root=project_root)

            backups = result["backups_created"]
            self.assertEqual(len(backups), 1, json.dumps(result, indent=2))
            self.assertEqual(backups[0]["file"], str(existing))
            backup_path = Path(backups[0]["backup_path"])
            self.assertTrue(backup_path.exists())
            self.assertEqual(backup_path.read_text(encoding="utf-8"), "WORKING = True\n")
            self.assertNotEqual(existing.read_text(encoding="utf-8"), "WORKING = True\n")

    def test_empty_blueprint_is_rejected_without_writing_files(self) -> None:
        forge = load_forge()
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            result = forge.forge_infrastructure_system("   ", project_root=project_root)

            self.assertEqual(result["status"], "rejected")
            self.assertTrue(result["manny_approval_required"])
            self.assertFalse((project_root / "RAMFAM_KINGDOM_BRAIN").exists())


if __name__ == "__main__":
    unittest.main()
