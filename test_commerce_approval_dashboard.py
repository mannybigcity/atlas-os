from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DASHBOARD_FILE = ROOT / "skills" / "commerce" / "commerce_approval_dashboard.py"


def load_dashboard():
    spec = importlib.util.spec_from_file_location("commerce_approval_dashboard", DASHBOARD_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class CommerceApprovalDashboardTests(unittest.TestCase):
    def create_mission(self, root: Path, folder_name: str) -> Path:
        mission_folder = root / folder_name
        hunter_json = mission_folder / "01_hunter_etsy_research" / "hunter_etsy_research_latest.json"
        micah_json = mission_folder / "02_micah_design_prompt_engine" / "micah_design_prompts_latest.json"
        amanda_json = mission_folder / "03_amanda_listing_engine" / "amanda_listing_packages_latest.json"
        printify_json = mission_folder / "04_printify_draft_package_engine" / "printify_draft_packages_latest.json"

        write_json(
            hunter_json,
            {
                "mission": "Hunter Etsy Research",
                "top_opportunity": {
                    "keyword": "faith family shirts",
                    "opportunity_score": 9,
                    "recommended_offer": "Launch matching faith family shirts.",
                },
                "opportunities": [
                    {
                        "keyword": "faith family shirts",
                        "opportunity_score": 9,
                        "demand_signal": "High",
                        "competition_level": "Low",
                        "recommended_offer": "Launch matching faith family shirts.",
                    }
                ],
            },
        )
        write_json(
            micah_json,
            {
                "mission": "Micah Design Prompt Engine",
                "design_concepts": [
                    {
                        "rank": 1,
                        "source_keyword": "faith family shirts",
                        "design_title": "Faith Family Matching Set",
                        "design_concept": "Warm family shirt concept.",
                        "image_prompt": "Original design prompt.",
                    }
                ],
            },
        )
        write_json(
            amanda_json,
            {
                "mission": "Amanda Listing Engine",
                "listing_packages": [
                    {
                        "rank": 1,
                        "source_keyword": "faith family shirts",
                        "product_title": "Faith Family Shirts - Matching Set",
                        "pricing_suggestion": {"anchor_price": "$31.71"},
                        "manny_approval_requirement": "Manny approval is required before publishing this listing.",
                    }
                ],
            },
        )
        write_json(
            printify_json,
            {
                "mission": "Printify Draft Package Engine",
                "auto_publish_enabled": False,
                "printify_draft_packages": [
                    {
                        "rank": 1,
                        "draft_id": "printify-draft-01-faith-family-shirts",
                        "title": "Faith Family Shirts - Matching Set",
                        "product_type_recommendation": {"product_type": "Unisex Jersey T-Shirt"},
                        "pricing_math": {"retail_price": 31.71, "estimated_profit": 9.52},
                        "printify_draft_payload": {
                            "visible": False,
                            "publish_action": "none_manual_manny_approval_required",
                        },
                    }
                ],
            },
        )
        write_json(
            mission_folder / "commerce_pipeline_mission_summary.json",
            {
                "mission": "Commerce Pipeline Runner",
                "mission_folder": str(mission_folder),
                "auto_publish_enabled": False,
                "approval_required_before_public_action": True,
                "manny_approval_requirement": "Manny approval is required before any public action.",
                "stages": {
                    "hunter": {"json_path": str(hunter_json)},
                    "micah": {"json_path": str(micah_json)},
                    "amanda": {"json_path": str(amanda_json)},
                    "printify": {"json_path": str(printify_json)},
                },
            },
        )
        return mission_folder

    def test_builds_dashboard_from_latest_mission_and_exports_default_decisions_json(self) -> None:
        dashboard = load_dashboard()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.create_mission(root, "commerce_pipeline_mission_20240101_010101")
            latest = self.create_mission(root, "commerce_pipeline_mission_20240102_010101")

            result = dashboard.build_dashboard_from_latest_mission(root)

            self.assertEqual(Path(result["mission_folder"]), latest)
            html_path = Path(result["dashboard_html"])
            decisions_path = Path(result["approval_decisions_json"])
            self.assertTrue(html_path.exists())
            self.assertTrue(decisions_path.exists())

            html = html_path.read_text(encoding="utf-8")
            self.assertIn("Commerce Kingdom Review Queue", html)
            self.assertIn("New Workflow: Auto-Execute Internal Work", html)
            self.assertIn("Approve results, not work", html)
            self.assertIn("Hunter Opportunity", html)
            self.assertIn("Micah Designs", html)
            self.assertIn("Amanda Listings", html)
            self.assertIn("Printify Draft Packages", html)
            self.assertIn("Manual Approval Guard", html)
            self.assertIn("Manual approval is required only for customer contact, invoices, emails, Etsy publishing, Shopify publishing, money movement, deleting files, or external actions", html)
            self.assertIn("option value=\"result_approved\"", html)
            self.assertIn("option value=\"needs_revision\"", html)
            self.assertIn("Export Review Queue JSON", html)

            decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
            self.assertEqual(decisions["workflow"], "auto_execute_internal_work_review_results_after_completion")
            self.assertEqual(decisions["approval_target"], "results_not_work")
            self.assertTrue(decisions["internal_work_auto_authorized"])
            self.assertFalse(decisions["manny_approval_guard"]["internal_work_blocked_pending_approval"])
            self.assertFalse(decisions["auto_publish_enabled"])
            self.assertTrue(decisions["manny_approval_guard"]["public_actions_blocked_until_manny_approval"])
            self.assertEqual(decisions["manny_approval_guard"]["publish_action"], "blocked_pending_manny_approval")
            self.assertIn("publishing_to_etsy", decisions["manny_approval_guard"]["manual_approval_required_actions"])
            self.assertIn("testing", decisions["internal_auto_execute_work_types"])
            self.assertEqual(decisions["counts"], {
                "hunter_opportunities": 1,
                "micah_designs": 1,
                "amanda_listings": 1,
                "printify_draft_packages": 1,
            })
            self.assertEqual(decisions["review_queue"], decisions["approval_decisions"])
            for category_items in decisions["review_queue"].values():
                for item in category_items:
                    self.assertEqual(item["status"], "pending_result_review")
                    self.assertEqual(item["authorization_status"], "auto_executed_from_manny_command")
                    self.assertEqual(item["review_type"], "approve_results_not_work")
                    self.assertIn("Manny", item["approval_guard"])

    def test_rejects_missing_pipeline_mission_folder(self) -> None:
        dashboard = load_dashboard()

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(FileNotFoundError):
                dashboard.build_dashboard_from_latest_mission(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
