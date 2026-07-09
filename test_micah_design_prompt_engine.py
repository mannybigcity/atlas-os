from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE_FILE = ROOT / "skills" / "commerce" / "micah_design_prompt_engine.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("micah_design_prompt_engine", ENGINE_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MicahDesignPromptEngineTests(unittest.TestCase):
    def hunter_payload(self):
        return {
            "mission": "Hunter Etsy Research",
            "generated_at": "2026-06-17T17:46:58",
            "top_opportunity": {
                "keyword": "custom laser engraved gifts",
                "opportunity_score": 10,
                "recommended_offer": "Launch a personalized engraved gift bundle with scripture, family names, or business branding.",
                "demand_signal": "High",
                "competition_level": "Low",
                "mission_fit": "High",
            },
            "opportunities": [
                {
                    "keyword": "custom laser engraved gifts",
                    "opportunity_score": 10,
                    "recommended_offer": "Launch a personalized engraved gift bundle with scripture, family names, or business branding.",
                    "demand_signal": "High",
                    "competition_level": "Low",
                    "mission_fit": "High",
                    "sample_listings": [
                        {"title": "Custom Laser Engraved Cutting Board Gift"},
                        {"title": "Engraved Scripture Wood Sign"},
                    ],
                },
                {
                    "keyword": "faith family shirts",
                    "opportunity_score": 9,
                    "recommended_offer": "Launch a faith-forward personalized apparel offer with matching family/church group options.",
                    "demand_signal": "Medium",
                    "competition_level": "Low",
                    "mission_fit": "High",
                    "sample_listings": [
                        {"title": "Matching Faith Family Shirts"},
                    ],
                },
            ],
        }

    def test_generates_ten_etsy_ready_design_concepts_from_hunter_json(self) -> None:
        engine = load_engine()

        report = engine.generate_design_prompt_report(self.hunter_payload(), count=10)

        self.assertEqual(report["mission"], "Micah Design Prompt Engine")
        self.assertEqual(report["agent_chain"]["assigned_by"], "Atlas")
        self.assertEqual(report["agent_chain"]["builder"], "Mason")
        self.assertEqual(report["agent_chain"]["design_owner"], "Micah")
        self.assertEqual(len(report["design_concepts"]), 10)
        self.assertTrue(report["approval_required_before_public_action"])

        required_fields = {
            "rank",
            "source_keyword",
            "design_title",
            "design_concept",
            "art_direction",
            "color_palette",
            "typography_suggestions",
            "openai_image_prompt",
            "commercial_use_notes",
        }
        for concept in report["design_concepts"]:
            self.assertTrue(required_fields.issubset(concept.keys()), json.dumps(concept, indent=2))
            self.assertTrue(concept["design_title"])
            self.assertTrue(concept["design_concept"])
            self.assertTrue(concept["art_direction"])
            self.assertGreaterEqual(len(concept["color_palette"]), 4)
            self.assertIn("transparent background", concept["openai_image_prompt"].lower())
            self.assertIn("openai image generation", concept["openai_image_prompt"].lower())
            self.assertIn("no copyrighted", concept["commercial_use_notes"].lower())

    def test_matches_product_angle_to_source_keyword(self) -> None:
        engine = load_engine()

        report = engine.generate_design_prompt_report(self.hunter_payload(), count=10)
        engraved_concepts = [
            concept for concept in report["design_concepts"] if concept["source_keyword"] == "custom laser engraved gifts"
        ]
        shirt_concepts = [concept for concept in report["design_concepts"] if concept["source_keyword"] == "faith family shirts"]

        self.assertTrue(any("engraving" in concept["art_direction"].lower() for concept in engraved_concepts))
        self.assertTrue(any("shirt" in concept["art_direction"].lower() for concept in shirt_concepts))

    def test_export_writes_json_and_markdown_report(self) -> None:
        engine = load_engine()
        report = engine.generate_design_prompt_report(self.hunter_payload(), count=10)

        with tempfile.TemporaryDirectory() as temp_dir:
            exports = engine.export_report(report, Path(temp_dir))
            latest_json = Path(exports["latest_json"])
            latest_report = Path(exports["latest_report"])

            self.assertTrue(latest_json.exists())
            self.assertTrue(latest_report.exists())
            exported_payload = json.loads(latest_json.read_text(encoding="utf-8"))
            markdown = latest_report.read_text(encoding="utf-8")

        self.assertEqual(len(exported_payload["design_concepts"]), 10)
        self.assertIn("# Micah Etsy Design Prompt Report", markdown)
        self.assertIn("## Etsy-Ready Design Concepts", markdown)
        self.assertIn("OpenAI image prompt", markdown)
        self.assertIn("Commercial use notes", markdown)


if __name__ == "__main__":
    unittest.main()
