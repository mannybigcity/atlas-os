from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FACTORY_FILE = ROOT / "skills" / "digital_factory" / "amanda_listing_factory.py"
REQUIRED_DISCLAIMER = "This is a digital download.\nNo physical product will be shipped."


def load_factory():
    spec = importlib.util.spec_from_file_location("amanda_listing_factory", FACTORY_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AmandaListingFactoryTests(unittest.TestCase):
    def test_build_listing_package_converts_asset_metadata_into_etsy_ready_package(self) -> None:
        factory = load_factory()

        with tempfile.TemporaryDirectory() as temp_dir:
            asset_folder = Path(temp_dir) / "design_gallery" / "approved" / "faith_over_fear"
            asset_folder.mkdir(parents=True)
            metadata_path = asset_folder / "asset_metadata.json"
            metadata_path.write_text(
                json.dumps(
                    {
                        "asset_id": "faith_over_fear",
                        "asset_name": "Faith Over Fear",
                        "creator_agent": "Micah the Fox",
                        "approval_status": "Approved",
                        "marketplace_status": "Ready for Listing",
                        "file_locations": {
                            "svg": str(asset_folder / "faith_over_fear.svg"),
                            "png": str(asset_folder / "faith_over_fear.png"),
                            "metadata": str(metadata_path),
                        },
                        "output_location": str(asset_folder),
                    }
                ),
                encoding="utf-8",
            )

            result = factory.build_listing_package(metadata_path)

            expected_files = {
                "etsy_listing.txt",
                "seo_tags.txt",
                "marketing_copy.txt",
            }
            listing_package = asset_folder / "listing_package"
            self.assertEqual(Path(result["output_location"]), listing_package)
            self.assertEqual(expected_files, set(result["files_created"].keys()))
            for filename in expected_files:
                self.assertEqual(Path(result["files_created"][filename]), listing_package / filename)
                self.assertTrue((listing_package / filename).exists(), filename)

            etsy_listing = (listing_package / "etsy_listing.txt").read_text(encoding="utf-8")
            seo_tags = (listing_package / "seo_tags.txt").read_text(encoding="utf-8")
            marketing_copy = (listing_package / "marketing_copy.txt").read_text(encoding="utf-8")

            self.assertIn("Etsy Title:", etsy_listing)
            self.assertIn("Faith Over Fear", etsy_listing)
            title_line = etsy_listing.splitlines()[1]
            self.assertLessEqual(len(title_line), 140)
            self.assertIn("Digital Download", title_line)
            self.assertIn("Etsy Description:", etsy_listing)
            self.assertIn("Product Overview:", etsy_listing)
            self.assertIn("What You Receive:", etsy_listing)
            self.assertIn(REQUIRED_DISCLAIMER, etsy_listing)

            tag_lines = [line for line in seo_tags.splitlines() if line.strip() and line[0].isdigit()]
            self.assertEqual(len(tag_lines), 13)
            self.assertIn("faith over fear", seo_tags.lower())
            self.assertTrue(all(len(line.split(".", 1)[1].strip()) <= 20 for line in tag_lines))

            self.assertIn("Facebook:", marketing_copy)
            self.assertIn("Instagram:", marketing_copy)
            self.assertIn("TikTok Caption:", marketing_copy)
            self.assertIn("Faith Over Fear", marketing_copy)
            self.assertIn(REQUIRED_DISCLAIMER, marketing_copy)

    def test_load_asset_metadata_rejects_missing_asset_name(self) -> None:
        factory = load_factory()

        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_path = Path(temp_dir) / "asset_metadata.json"
            metadata_path.write_text(json.dumps({"asset_id": "missing_name"}), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "asset_name"):
                factory.build_listing_package(metadata_path)


if __name__ == "__main__":
    unittest.main()
