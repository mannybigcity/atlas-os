from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE_FILE = ROOT / "skills" / "commerce" / "printify_draft_package_engine.py"


def load_engine():
    spec = importlib.util.spec_from_file_location("printify_draft_package_engine", ENGINE_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PrintifyDraftPackageEngineTests(unittest.TestCase):
    def amanda_payload(self):
        return {
            "mission": "Amanda Listing Engine",
            "generated_at": "2026-06-17T18:31:14",
            "listing_packages": [
                {
                    "rank": 1,
                    "source_keyword": "faith family shirts",
                    "source_opportunity_score": 9,
                    "source_design_title": "Faith Family Shirts: Faith Family Matching Set",
                    "product_title": "Faith Family Shirts - Faith Family Matching Set Custom Faith Shirt for Family Church Gifts",
                    "seo_title": "Faith Family Shirts - Faith Family Matching Set Custom Faith Shirt for Family Church Gifts",
                    "etsy_tags": [
                        "faith family shirts",
                        "christian shirt",
                        "faith shirt",
                        "custom shirt",
                        "church shirt",
                        "family shirts",
                        "teacher shirt",
                        "jesus shirt",
                        "retreat shirt",
                        "custom gift",
                        "personalized",
                        "faith gift",
                        "christian gift",
                    ],
                    "description": "A coordinated family or church-group apparel design that feels warm, modern, and photo-ready.",
                    "materials": ["soft cotton or cotton-blend shirt", "DTF, screen print, or vinyl transfer"],
                    "category_recommendation": "Clothing > Unisex Adult Clothing > Tops & Tees > T-shirts",
                    "pricing_suggestion": {
                        "suggested_price_range": "$27.39-$36.04",
                        "anchor_price": "$31.71",
                        "source_average_price": "$28.83",
                        "manny_review_required": True,
                    },
                    "mockup_notes": [
                        "Reflect Micah art direction: Stacked badge layout with hand-lettered faith phrase.",
                        "Keep mockup styling aligned with this color palette: cream, deep forest green, terracotta.",
                    ],
                    "production_notes": ["Check transfer size, shirt color contrast, wash-care language, and size chart accuracy."],
                    "manny_approval_requirement": "Manny approval is required before publishing this listing.",
                },
                {
                    "rank": 2,
                    "source_keyword": "scripture tumbler wrap",
                    "source_opportunity_score": 8,
                    "source_design_title": "Scripture Tumbler Wrap: Encouragement Floral",
                    "product_title": "Scripture Tumbler Wrap - Custom Faith Tumbler Gift",
                    "etsy_tags": ["tumbler wrap", "custom tumbler", "faith tumbler"],
                    "description": "A seamless tumbler wrap concept pairing scripture-inspired encouragement with floral details.",
                    "materials": ["stainless steel tumbler", "sublimation transfer"],
                    "category_recommendation": "Home & Living > Kitchen & Dining > Drinkware > Tumblers & Water Glasses",
                    "pricing_suggestion": {"anchor_price": "$34.99", "manny_review_required": True},
                    "mockup_notes": ["Show full wrap seam placement and detail close-up."],
                    "production_notes": ["Verify wrap dimensions, seam placement, bleed margin, and color output."],
                    "manny_approval_requirement": "Manny approval is required before publishing this listing.",
                },
            ],
        }

    def test_generates_printify_ready_drafts_from_amanda_listing_package_json(self) -> None:
        engine = load_engine()

        report = engine.generate_printify_draft_report(self.amanda_payload())

        self.assertEqual(report["mission"], "Printify Draft Package Engine")
        self.assertEqual(report["agent_chain"]["assigned_by"], "Atlas")
        self.assertEqual(report["agent_chain"]["builder"], "Mason")
        self.assertEqual(report["agent_chain"]["listing_owner"], "Amanda")
        self.assertEqual(report["agent_chain"]["draft_owner"], "Mason")
        self.assertEqual(report["agent_chain"]["approval_owner"], "Manny")
        self.assertTrue(report["approval_required_before_public_action"])
        self.assertFalse(report["auto_publish_enabled"])
        self.assertEqual(len(report["printify_draft_packages"]), 2)

        required_fields = {
            "draft_id",
            "source_listing_rank",
            "product_type_recommendation",
            "print_area_notes",
            "mockup_direction",
            "product_description",
            "pricing_math",
            "tags",
            "listing_checklist",
            "manny_approval_gate",
            "printify_draft_payload",
        }
        for draft in report["printify_draft_packages"]:
            self.assertTrue(required_fields.issubset(draft.keys()), json.dumps(draft, indent=2))
            self.assertTrue(draft["draft_id"].startswith("printify-draft-"))
            self.assertIn("Manny", draft["manny_approval_gate"]["required_approval"])
            self.assertFalse(draft["manny_approval_gate"]["approved_for_publish"])
            self.assertFalse(draft["printify_draft_payload"]["visible"])
            self.assertFalse(draft["printify_draft_payload"]["is_locked"])
            self.assertLessEqual(len(draft["tags"]), 13)
            self.assertGreaterEqual(len(draft["listing_checklist"]), 8)
            self.assertTrue(all(item["status"] == "pending_manny_review" for item in draft["listing_checklist"]))
            self.assertGreater(draft["pricing_math"]["retail_price"], 0)
            self.assertIn("target_margin_percent", draft["pricing_math"])

    def test_product_type_recommendation_and_print_area_notes_match_source_category(self) -> None:
        engine = load_engine()

        drafts = engine.generate_printify_draft_packages(self.amanda_payload())
        shirt_draft = drafts[0]
        tumbler_draft = drafts[1]

        self.assertEqual(shirt_draft["product_type_recommendation"]["product_type"], "Unisex Jersey T-Shirt")
        self.assertIn("front", " ".join(shirt_draft["print_area_notes"]).lower())
        self.assertIn("4500 x 5400", " ".join(shirt_draft["print_area_notes"]))
        self.assertIn("shirt", shirt_draft["printify_draft_payload"]["blueprint_search_terms"])

        self.assertEqual(tumbler_draft["product_type_recommendation"]["product_type"], "20oz Skinny Tumbler")
        self.assertIn("wrap", " ".join(tumbler_draft["print_area_notes"]).lower())
        self.assertIn("seam", " ".join(tumbler_draft["mockup_direction"]).lower())
        self.assertIn("tumbler", tumbler_draft["printify_draft_payload"]["blueprint_search_terms"])

    def test_export_writes_json_and_markdown_report_without_publishing(self) -> None:
        engine = load_engine()
        report = engine.generate_printify_draft_report(self.amanda_payload())

        with tempfile.TemporaryDirectory() as temp_dir:
            exports = engine.export_report(report, Path(temp_dir))
            latest_json = Path(exports["latest_json"])
            latest_report = Path(exports["latest_report"])

            self.assertTrue(latest_json.exists())
            self.assertTrue(latest_report.exists())
            exported_payload = json.loads(latest_json.read_text(encoding="utf-8"))
            markdown = latest_report.read_text(encoding="utf-8")

        self.assertFalse(exported_payload["auto_publish_enabled"])
        self.assertIn("# Printify Draft Package Report", markdown)
        self.assertIn("## Printify-Ready Draft Packages", markdown)
        self.assertIn("Manny approval gate", markdown)
        self.assertIn("No products were published automatically", markdown)


if __name__ == "__main__":
    unittest.main()
