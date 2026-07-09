from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FACTORY_FILE = ROOT / "skills" / "digital_factory" / "micah_digital_factory.py"


def load_factory():
    spec = importlib.util.spec_from_file_location("micah_digital_factory", FACTORY_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MicahDigitalFactoryTests(unittest.TestCase):
    def test_build_asset_package_creates_complete_pending_package_and_registers_asset(self) -> None:
        factory = load_factory()

        with tempfile.TemporaryDirectory() as temp_dir:
            gallery_root = Path(temp_dir) / "design_gallery"
            result = factory.build_asset_package("Faith Over Fear", gallery_root=gallery_root)

            opportunity_folder = gallery_root / "pending" / "faith_over_fear"
            expected_files = {
                "faith_over_fear.svg",
                "faith_over_fear.png",
                "faith_over_fear_prompt.txt",
                "listing_notes.txt",
                "asset_metadata.json",
            }

            self.assertEqual(Path(result["opportunity_folder"]), opportunity_folder)
            self.assertTrue(opportunity_folder.is_dir())
            self.assertEqual(expected_files, {path.name for path in opportunity_folder.iterdir()})
            for filename in expected_files:
                self.assertTrue((opportunity_folder / filename).exists(), filename)

            metadata = json.loads((opportunity_folder / "asset_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["asset_name"], "Faith Over Fear")
            self.assertEqual(metadata["creator_agent"], "Micah the Fox")
            self.assertEqual(metadata["approval_status"], "Pending Approval")
            self.assertEqual(metadata["marketplace_status"], "Draft")
            self.assertEqual(metadata["revenue"], 0)
            self.assertEqual(metadata["file_locations"]["svg"], str(opportunity_folder / "faith_over_fear.svg"))
            self.assertEqual(metadata["file_locations"]["png"], str(opportunity_folder / "faith_over_fear.png"))
            self.assertEqual(metadata["file_locations"]["prompt"], str(opportunity_folder / "faith_over_fear_prompt.txt"))
            self.assertEqual(metadata["file_locations"]["listing_notes"], str(opportunity_folder / "listing_notes.txt"))
            self.assertEqual(metadata["file_locations"]["metadata"], str(opportunity_folder / "asset_metadata.json"))

            prompt_text = (opportunity_folder / "faith_over_fear_prompt.txt").read_text(encoding="utf-8")
            notes_text = (opportunity_folder / "listing_notes.txt").read_text(encoding="utf-8")
            svg_text = (opportunity_folder / "faith_over_fear.svg").read_text(encoding="utf-8")
            png_bytes = (opportunity_folder / "faith_over_fear.png").read_bytes()

            self.assertIn("Faith Over Fear", prompt_text)
            self.assertIn("Faith Over Fear", notes_text)
            self.assertIn("Faith Over Fear", svg_text)
            self.assertTrue(png_bytes.startswith(b"\x89PNG\r\n\x1a\n"))

            registry = json.loads((gallery_root / "asset_registry.json").read_text(encoding="utf-8"))
            matching_assets = [asset for asset in registry["assets"] if asset["asset_id"] == "faith_over_fear"]
            self.assertEqual(len(matching_assets), 1)
            registered = matching_assets[0]
            self.assertEqual(registered["asset_name"], "Faith Over Fear")
            self.assertEqual(registered["creator_agent"], "Micah the Fox")
            self.assertEqual(registered["approval_status"], "Pending Approval")
            self.assertEqual(registered["marketplace_status"], "Draft")
            self.assertEqual(registered["file_location"], str(opportunity_folder / "asset_metadata.json"))
            self.assertEqual(registered["asset_preview"], "/design-gallery/pending/faith_over_fear/faith_over_fear.png")

    def test_registering_same_opportunity_updates_existing_registry_entry_instead_of_duplicating(self) -> None:
        factory = load_factory()

        with tempfile.TemporaryDirectory() as temp_dir:
            gallery_root = Path(temp_dir) / "design_gallery"
            factory.build_asset_package("Faith Over Fear", gallery_root=gallery_root)
            factory.build_asset_package("Faith Over Fear", gallery_root=gallery_root)

            registry = json.loads((gallery_root / "asset_registry.json").read_text(encoding="utf-8"))
            matching_assets = [asset for asset in registry["assets"] if asset["asset_id"] == "faith_over_fear"]

            self.assertEqual(len(matching_assets), 1)


if __name__ == "__main__":
    unittest.main()
