from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNNER_FILE = ROOT / "skills" / "commerce" / "commerce_pipeline_runner.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("commerce_pipeline_runner", RUNNER_FILE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommercePipelineRunnerTests(unittest.TestCase):
    def test_runs_hunter_micah_amanda_and_printify_in_order_into_one_mission_folder(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as temp_dir:
            mission = runner.run_commerce_pipeline(
                output_root=Path(temp_dir),
                keywords=["faith family shirts", "custom laser engraved gifts"],
                hunter_limit=3,
                design_count=2,
                listing_count=2,
                draft_count=2,
                use_etsy_api=False,
            )

            mission_folder = Path(mission["mission_folder"])
            self.assertTrue(mission_folder.exists())
            self.assertEqual(mission["mission"], "Commerce Pipeline Runner")
            self.assertEqual(mission["pipeline_order"], ["Hunter", "Micah", "Amanda", "Printify Draft Package"])
            self.assertFalse(mission["auto_publish_enabled"])
            self.assertTrue(mission["approval_required_before_public_action"])
            self.assertEqual(mission["agent_chain"]["assigned_by"], "Atlas")
            self.assertEqual(mission["agent_chain"]["builder"], "Mason")
            self.assertEqual(mission["agent_chain"]["revenue_owner"], "Hunter")
            self.assertEqual(mission["agent_chain"]["design_owner"], "Micah")
            self.assertEqual(mission["agent_chain"]["listing_owner"], "Amanda")
            self.assertEqual(mission["agent_chain"]["approval_owner"], "Manny")

            expected_stage_names = ["hunter", "micah", "amanda", "printify"]
            self.assertEqual(list(mission["stages"].keys()), expected_stage_names)
            for stage_name in expected_stage_names:
                stage = mission["stages"][stage_name]
                self.assertEqual(stage["status"], "complete")
                self.assertTrue(Path(stage["json_path"]).exists(), stage)
                self.assertTrue(Path(stage["markdown_path"]).exists(), stage)
                self.assertTrue(str(Path(stage["json_path"]).parent).startswith(str(mission_folder)))
                self.assertTrue(str(Path(stage["markdown_path"]).parent).startswith(str(mission_folder)))

            printify_payload = json.loads(Path(mission["stages"]["printify"]["json_path"]).read_text(encoding="utf-8"))
            self.assertFalse(printify_payload["auto_publish_enabled"])
            self.assertEqual(len(printify_payload["printify_draft_packages"]), 2)
            for draft in printify_payload["printify_draft_packages"]:
                self.assertFalse(draft["printify_draft_payload"]["visible"])
                self.assertEqual(draft["printify_draft_payload"]["publish_action"], "none_manual_manny_approval_required")

    def test_exports_summary_json_and_markdown_with_manny_approval_gates(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as temp_dir:
            mission = runner.run_commerce_pipeline(
                output_root=Path(temp_dir),
                keywords=["faith family shirts"],
                hunter_limit=2,
                design_count=1,
                listing_count=1,
                draft_count=1,
                use_etsy_api=False,
            )

            summary_json = Path(mission["exports"]["summary_json"])
            summary_md = Path(mission["exports"]["summary_report"])
            self.assertTrue(summary_json.exists())
            self.assertTrue(summary_md.exists())

            summary_payload = json.loads(summary_json.read_text(encoding="utf-8"))
            markdown = summary_md.read_text(encoding="utf-8")

        self.assertFalse(summary_payload["auto_publish_enabled"])
        self.assertIn("manny_approval_gates", summary_payload)
        self.assertEqual(summary_payload["manny_approval_gates"]["publish"], "blocked_pending_manny_approval")
        self.assertEqual(summary_payload["manny_approval_gates"]["printify_live_creation"], "blocked_pending_manny_approval")
        self.assertEqual(summary_payload["manny_approval_gates"]["customer_commitment"], "blocked_pending_manny_approval")
        self.assertIn("# Commerce Pipeline Mission Report", markdown)
        self.assertIn("Pipeline order: Hunter → Micah → Amanda → Printify Draft Package", markdown)
        self.assertIn("Auto-publish enabled: false", markdown)
        self.assertIn("Manny approval gates", markdown)
        self.assertIn("No products were published automatically", markdown)


if __name__ == "__main__":
    unittest.main()
