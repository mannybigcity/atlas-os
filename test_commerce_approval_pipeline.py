from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIPELINE_FILE = ROOT / "skills" / "commerce" / "commerce_approval_pipeline.py"


def load_pipeline():
    spec = importlib.util.spec_from_file_location("commerce_approval_pipeline", PIPELINE_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommerceApprovalPipelineTests(unittest.TestCase):
    def write_gallery_sources(self, gallery_root: Path) -> Path:
        approved_folder = gallery_root / "pending" / "asset-approved"
        approved_folder.mkdir(parents=True, exist_ok=True)
        metadata_path = approved_folder / "asset_metadata.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "asset_id": "asset-approved",
                    "asset_name": "SIS Digital Banner",
                    "approval_status": "Approved",
                    "marketplace_status": "Review Queue",
                    "creator_agent": "Micah",
                    "file_locations": {"metadata": str(metadata_path)},
                }
            ),
            encoding="utf-8",
        )
        registry = {
            "assets": [
                {
                    "asset_id": "asset-approved",
                    "asset_name": "SIS Digital Banner",
                    "approval_status": "Approved",
                    "marketplace_status": "Review Queue",
                    "creator_agent": "Micah",
                    "file_locations": {"metadata": str(metadata_path)},
                }
            ]
        }
        (gallery_root / "asset_registry.json").write_text(json.dumps(registry), encoding="utf-8")
        (gallery_root / "revenue_tracking.json").write_text(json.dumps({"assets": {}}), encoding="utf-8")
        return metadata_path

    def test_publish_digital_marks_internal_kingdom_gallery_only_and_blocks_external_channels(self) -> None:
        pipeline = load_pipeline()

        with tempfile.TemporaryDirectory() as temp_dir:
            gallery_root = Path(temp_dir)
            metadata_path = self.write_gallery_sources(gallery_root)

            result = pipeline.publish_digital_asset("asset-approved", gallery_root)

            self.assertTrue(result["success"])
            self.assertEqual(result["asset"]["approval_status"], "Approved")
            self.assertEqual(result["asset"]["marketplace_status"], "Published")
            self.assertEqual(result["asset"]["publication_type"], "digital")
            self.assertEqual(result["asset"]["publication_scope"], "internal_kingdom_gallery_only")
            self.assertEqual(result["asset"]["channels"], ["kingdom_gallery"])
            self.assertEqual(result["asset"]["external_channels"], [])
            self.assertFalse(result["asset"]["manual_approval_required"])
            self.assertEqual(result["asset"]["manual_approval_scope"], "internal_kingdom_gallery_only")
            self.assertTrue(result["asset"]["external_publication_blocked"])
            self.assertEqual(
                result["asset"]["blocked_external_channels"],
                ["etsy", "shopify", "printify", "social_media", "customers", "ads", "payments"],
            )
            self.assertEqual(result["external_side_effects"], [])

            registry = json.loads((gallery_root / "asset_registry.json").read_text(encoding="utf-8"))
            registry_asset = registry["assets"][0]
            self.assertEqual(registry_asset["marketplace_status"], "Published")
            self.assertEqual(registry_asset["channels"], ["kingdom_gallery"])
            self.assertNotIn("etsy_digital", registry_asset["channels"])
            self.assertNotIn("shopify_digital", registry_asset["channels"])

            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["marketplace_status"], "Published")
            self.assertEqual(metadata["channels"], ["kingdom_gallery"])
            self.assertEqual(metadata["publication_scope"], "internal_kingdom_gallery_only")

    def test_publish_digital_requires_approved_unpublished_asset(self) -> None:
        pipeline = load_pipeline()

        with tempfile.TemporaryDirectory() as temp_dir:
            gallery_root = Path(temp_dir)
            self.write_gallery_sources(gallery_root)
            registry_path = gallery_root / "asset_registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["assets"][0]["approval_status"] = "Pending Approval"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with self.assertRaises(ValueError):
                pipeline.publish_digital_asset("asset-approved", gallery_root)


if __name__ == "__main__":
    unittest.main()
