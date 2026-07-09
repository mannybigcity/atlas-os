from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE_FILE = ROOT / "skills" / "commerce" / "amanda_listing_engine.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("amanda_listing_engine", ENGINE_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AmandaListingEngineTests(unittest.TestCase):
    def hunter_payload(self):
        return {
            "mission": "Hunter Etsy Research",
            "generated_at": "2026-06-17T17:46:58",
            "opportunities": [
                {
                    "keyword": "custom laser engraved gifts",
                    "opportunity_score": 10,
                    "recommended_offer": "Launch a personalized engraved gift bundle with scripture, family names, or business branding.",
                    "average_price": 38.99,
                    "demand_signal": "High",
                    "competition_level": "Low",
                    "mission_fit": "High",
                },
                {
                    "keyword": "faith family shirts",
                    "opportunity_score": 9,
                    "recommended_offer": "Launch a faith-forward personalized apparel offer with matching family/church group options.",
                    "average_price": 28.83,
                    "demand_signal": "Medium",
                    "competition_level": "Low",
                    "mission_fit": "High",
                },
            ],
        }

    def micah_payload(self):
        return {
            "mission": "Micah Design Prompt Engine",
            "generated_at": "2026-06-17T18:13:38",
            "design_concepts": [
                {
                    "rank": 1,
                    "source_keyword": "custom laser engraved gifts",
                    "source_opportunity_score": 10,
                    "design_title": "Custom Laser Engraved Gifts: Heirloom Scripture Minimal",
                    "design_concept": "A premium personalized keepsake built around family names, short scripture text, and a clean monogram focal point.",
                    "art_direction": "Minimal heirloom composition with centered engraving layout, fine line botanical accents, and warm wood mockup framing.",
                    "color_palette": ["warm walnut brown", "soft ivory", "charcoal ink", "muted sage"],
                },
                {
                    "rank": 2,
                    "source_keyword": "faith family shirts",
                    "source_opportunity_score": 9,
                    "design_title": "Faith Family Shirts: Faith Family Matching Set",
                    "design_concept": "A coordinated family or church-group apparel design that feels warm, modern, and photo-ready.",
                    "art_direction": "Stacked badge layout with hand-lettered faith phrase and adaptable placement for adult, youth, and toddler shirts.",
                    "color_palette": ["cream", "deep forest green", "terracotta", "warm sand"],
                },
            ],
        }

    def test_generates_etsy_ready_listing_packages_from_hunter_and_micah_json(self) -> None:
        engine = load_engine()

        report = engine.generate_listing_report(self.hunter_payload(), self.micah_payload())

        self.assertEqual(report["mission"], "Amanda Listing Engine")
        self.assertEqual(report["agent_chain"]["assigned_by"], "Atlas")
        self.assertEqual(report["agent_chain"]["builder"], "Mason")
        self.assertEqual(report["agent_chain"]["listing_owner"], "Amanda")
        self.assertEqual(report["agent_chain"]["approval_owner"], "Manny")
        self.assertEqual(len(report["listing_packages"]), 2)
        self.assertTrue(report["approval_required_before_public_action"])

        required_fields = {
            "product_title",
            "seo_title",
            "etsy_tags",
            "description",
            "materials",
            "occasion",
            "recipient",
            "category_recommendation",
            "pricing_suggestion",
            "production_notes",
            "mockup_notes",
            "manny_approval_requirement",
        }
        for package in report["listing_packages"]:
            self.assertTrue(required_fields.issubset(package.keys()), json.dumps(package, indent=2))
            self.assertLessEqual(len(package["product_title"]), 140)
            self.assertLessEqual(len(package["seo_title"]), 140)
            self.assertEqual(len(package["etsy_tags"]), 13)
            self.assertEqual(len(set(package["etsy_tags"])), 13)
            self.assertTrue(all(len(tag) <= 20 for tag in package["etsy_tags"]))
            self.assertIn("Manny approval", package["manny_approval_requirement"])
            self.assertTrue(package["pricing_suggestion"]["manny_review_required"])

    def test_matches_categories_to_source_opportunities(self) -> None:
        engine = load_engine()

        packages = engine.generate_listing_packages(self.hunter_payload(), self.micah_payload())
        engraved_package = packages[0]
        shirt_package = packages[1]

        self.assertIn("Cutting Boards", engraved_package["category_recommendation"])
        self.assertTrue(any("laser" in note.lower() for note in engraved_package["production_notes"]))
        self.assertIn("T-shirts", shirt_package["category_recommendation"])
        self.assertTrue(any("shirt" in material.lower() for material in shirt_package["materials"]))

    def test_export_writes_json_and_markdown_report(self) -> None:
        engine = load_engine()
        report = engine.generate_listing_report(self.hunter_payload(), self.micah_payload())

        with tempfile.TemporaryDirectory() as temp_dir:
            exports = engine.export_report(report, Path(temp_dir))
            latest_json = Path(exports["latest_json"])
            latest_report = Path(exports["latest_report"])

            self.assertTrue(latest_json.exists())
            self.assertTrue(latest_report.exists())
            exported_payload = json.loads(latest_json.read_text(encoding="utf-8"))
            markdown = latest_report.read_text(encoding="utf-8")

        self.assertEqual(len(exported_payload["listing_packages"]), 2)
        self.assertIn("# Amanda Etsy Listing Package Report", markdown)
        self.assertIn("## Etsy-Ready Listing Packages", markdown)
        self.assertIn("Etsy tags (13)", markdown)
        self.assertIn("Manny approval requirement", markdown)


if __name__ == "__main__":
    unittest.main()
