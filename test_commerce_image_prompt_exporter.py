from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPORTER_FILE = ROOT / "skills" / "commerce" / "commerce_image_prompt_exporter.py"


def load_exporter():
    spec = importlib.util.spec_from_file_location("commerce_image_prompt_exporter", EXPORTER_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommerceImagePromptExporterTests(unittest.TestCase):
    def approval_decisions_payload(self):
        return {
            "mission": "Commerce Approval Dashboard",
            "mission_folder": "mission-folder",
            "auto_publish_enabled": False,
            "manny_approval_guard": {"public_actions_blocked_until_manny_approval": True},
            "approval_decisions": {
                "micah_designs": [
                    {
                        "item_id": "micah-01",
                        "title": "Faith Family Shirts: Faith Family Matching Set",
                        "source_agent": "Micah",
                        "status": "approved",
                        "approved_by": "Manny",
                        "reviewed_at": "2026-06-17T19:15:00",
                        "notes": "Export prompt only.",
                    },
                    {
                        "item_id": "micah-02",
                        "title": "Custom Embroidered Hats: Kingdom Workwear Patch",
                        "source_agent": "Micah",
                        "status": "rejected",
                        "approved_by": "Manny",
                    },
                    {
                        "item_id": "micah-03",
                        "title": "Teacher Appreciation Shirts: Teacher Grace Collection",
                        "source_agent": "Micah",
                        "status": "pending_manny_review",
                        "approved_by": "",
                    },
                    {
                        "item_id": "micah-04",
                        "title": "Approved But Not Manny",
                        "source_agent": "Micah",
                        "status": "approved",
                        "approved_by": "Atlas",
                    },
                ],
                "amanda_listings": [
                    {
                        "item_id": "amanda-01",
                        "title": "Approved listing should not become image prompt",
                        "source_agent": "Amanda",
                        "status": "approved",
                        "approved_by": "Manny",
                    }
                ],
            },
        }

    def micah_prompt_payload(self):
        return {
            "mission": "Micah Design Prompt Engine",
            "generated_at": "2026-06-17T18:56:33",
            "design_concepts": [
                {
                    "rank": 1,
                    "source_keyword": "faith family shirts",
                    "source_opportunity_score": 9,
                    "design_title": "Faith Family Shirts: Faith Family Matching Set",
                    "design_concept": "Warm matching family shirt concept.",
                    "art_direction": "Stacked badge layout with subtle rays.",
                    "color_palette": ["cream", "deep forest green", "terracotta"],
                    "typography_suggestions": "Friendly bold serif headline.",
                    "openai_image_prompt": "OpenAI image generation prompt: Create original faith family shirt art.",
                    "commercial_use_notes": "No copyrighted characters or brand logos.",
                },
                {
                    "rank": 2,
                    "source_keyword": "custom embroidered hats",
                    "source_opportunity_score": 8,
                    "design_title": "Custom Embroidered Hats: Kingdom Workwear Patch",
                    "image_prompt": "OpenAI image generation prompt: Create original embroidered hat patch art.",
                },
                {
                    "rank": 3,
                    "source_keyword": "teacher appreciation shirts",
                    "design_title": "Teacher Appreciation Shirts: Teacher Grace Collection",
                    "openai_image_prompt": "OpenAI image generation prompt: Create original teacher appreciation shirt art.",
                },
                {
                    "rank": 4,
                    "source_keyword": "approved but not manny",
                    "design_title": "Approved But Not Manny",
                    "openai_image_prompt": "This should be blocked because Manny did not approve it.",
                },
            ],
        }

    def test_exports_openai_prompts_for_manny_approved_micah_designs_only(self) -> None:
        exporter = load_exporter()

        report = exporter.generate_image_prompt_export_report(
            self.approval_decisions_payload(),
            self.micah_prompt_payload(),
        )

        self.assertEqual(report["mission"], "Commerce Image Prompt Exporter")
        self.assertEqual(report["agent_chain"]["assigned_by"], "Atlas")
        self.assertEqual(report["agent_chain"]["builder"], "Mason")
        self.assertEqual(report["agent_chain"]["design_owner"], "Micah")
        self.assertEqual(report["agent_chain"]["approval_owner"], "Manny")
        self.assertFalse(report["image_generation_enabled"])
        self.assertFalse(report["auto_publish_enabled"])
        self.assertTrue(report["approval_required_before_public_action"])
        self.assertEqual(report["counts"]["approved_prompt_exports"], 1)
        self.assertEqual(report["counts"]["blocked_or_unapproved_designs"], 3)

        prompt = report["openai_image_prompts"][0]
        self.assertEqual(prompt["prompt_id"], "openai-image-prompt-01-faith-family-shirts-faith-family-matching-set")
        self.assertEqual(prompt["source_decision_item_id"], "micah-01")
        self.assertEqual(prompt["design_title"], "Faith Family Shirts: Faith Family Matching Set")
        self.assertIn("Create original faith family shirt art", prompt["openai_image_prompt"])
        self.assertIn("Manny", prompt["manny_approval_gate"]["approved_by"])
        self.assertFalse(prompt["manny_approval_gate"]["image_generation_performed"])
        self.assertEqual(prompt["export_status"], "prompt_exported_no_image_generated")
        self.assertNotIn("Custom Embroidered Hats", json.dumps(report))
        self.assertNotIn("Approved listing should not become image prompt", json.dumps(report))

    def test_export_writes_json_markdown_and_prompt_text_files_without_side_effects(self) -> None:
        exporter = load_exporter()
        report = exporter.generate_image_prompt_export_report(
            self.approval_decisions_payload(),
            self.micah_prompt_payload(),
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            exports = exporter.export_report(report, Path(temp_dir))
            latest_json = Path(exports["latest_json"])
            latest_report = Path(exports["latest_report"])
            prompt_dir = Path(exports["prompt_text_dir"])
            prompt_files = [Path(path) for path in exports["prompt_text_files"]]

            self.assertTrue(latest_json.exists())
            self.assertTrue(latest_report.exists())
            self.assertTrue(prompt_dir.exists())
            self.assertEqual(len(prompt_files), 1)
            self.assertTrue(prompt_files[0].exists())

            exported_payload = json.loads(latest_json.read_text(encoding="utf-8"))
            markdown = latest_report.read_text(encoding="utf-8")
            prompt_text = prompt_files[0].read_text(encoding="utf-8")

        self.assertIn("# Commerce Image Prompt Export Report", markdown)
        self.assertIn("## Approved OpenAI Image Prompts", markdown)
        self.assertIn("No images were generated", markdown)
        self.assertIn("Manny approval guard", markdown)
        self.assertIn("Create original faith family shirt art", prompt_text)
        self.assertFalse(exported_payload["image_generation_enabled"])
        self.assertFalse(exported_payload["auto_publish_enabled"])


if __name__ == "__main__":
    unittest.main()
