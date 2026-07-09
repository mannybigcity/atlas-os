import json
import tempfile
import unittest
from pathlib import Path

import app


class CommerceCommandCenterRouteTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.pipeline_root = Path(self.tempdir.name)
        self.design_gallery_root = Path(self.tempdir.name) / "design_gallery"
        self.design_gallery_root.mkdir(parents=True, exist_ok=True)
        self.original_pipeline_root = getattr(app, "COMMERCE_PIPELINE_ROOT", None)
        self.original_prompt_root = getattr(app, "COMMERCE_IMAGE_PROMPT_ROOT", None)
        self.original_design_gallery_root = getattr(app, "DESIGN_GALLERY_DIR", None)
        app.COMMERCE_PIPELINE_ROOT = self.pipeline_root
        app.COMMERCE_IMAGE_PROMPT_ROOT = self.pipeline_root / "commerce_image_prompt_exporter"
        app.DESIGN_GALLERY_DIR = self.design_gallery_root
        self.client = app.app.test_client()
        with self.client.session_transaction() as session:
            session["atlas_admin_authenticated"] = True
            session["atlas_admin_username"] = "test-admin"

    def tearDown(self):
        if self.original_pipeline_root is not None:
            app.COMMERCE_PIPELINE_ROOT = self.original_pipeline_root
        if self.original_prompt_root is not None:
            app.COMMERCE_IMAGE_PROMPT_ROOT = self.original_prompt_root
        if self.original_design_gallery_root is not None:
            app.DESIGN_GALLERY_DIR = self.original_design_gallery_root
        self.tempdir.cleanup()

    def write_dashboard(self, mission_name: str, body: str) -> Path:
        mission_folder = self.pipeline_root / mission_name
        mission_folder.mkdir(parents=True, exist_ok=True)
        dashboard_path = mission_folder / "commerce_approval_dashboard.html"
        dashboard_path.write_text(body, encoding="utf-8")
        return dashboard_path

    def write_design_gallery_exports(self, mission_name: str) -> Path:
        exporter_folder = self.pipeline_root / mission_name / "05_commerce_image_prompt_exporter"
        exporter_folder.mkdir(parents=True, exist_ok=True)
        (exporter_folder / "commerce_image_prompts_latest.md").write_text("# Latest Design Prompt Report", encoding="utf-8")
        (exporter_folder / "commerce_image_prompts_latest.json").write_text('{"mission":"Commerce Image Prompt Exporter"}', encoding="utf-8")
        return exporter_folder

    def write_design_gallery_sources(self) -> None:
        pending_folder = self.design_gallery_root / "pending" / "asset-pending"
        pending_folder.mkdir(parents=True, exist_ok=True)
        listing_package = pending_folder / "listing_package"
        listing_package.mkdir(parents=True, exist_ok=True)
        (pending_folder / "asset-pending.svg").write_text("<svg>Faith Over Fear Tee</svg>", encoding="utf-8")
        (pending_folder / "asset-pending.png").write_bytes(b"\x89PNG\r\n\x1a\nasset")
        (listing_package / "etsy_listing.txt").write_text("Faith Over Fear Tee listing", encoding="utf-8")
        (listing_package / "seo_tags.txt").write_text("faith,hope,shirt", encoding="utf-8")
        (listing_package / "marketing_copy.txt").write_text("Wear your faith boldly.", encoding="utf-8")
        pending_metadata = {
            "asset_id": "asset-pending",
            "asset_name": "Faith Over Fear Tee",
            "approval_status": "Pending Approval",
            "marketplace_status": "Review Queue",
            "creator_agent": "Micah",
            "opportunity_agent": "Hunter",
            "file_locations": {
                "svg": str(pending_folder / "asset-pending.svg"),
                "png": str(pending_folder / "asset-pending.png"),
                "metadata": str(pending_folder / "asset_metadata.json"),
                "listing_package": str(listing_package),
                "seo_tags": str(listing_package / "seo_tags.txt"),
                "marketing_copy": str(listing_package / "marketing_copy.txt"),
            },
        }
        (pending_folder / "asset_metadata.json").write_text(json.dumps(pending_metadata), encoding="utf-8")

        approved_folder = self.design_gallery_root / "pending" / "asset-approved"
        approved_folder.mkdir(parents=True, exist_ok=True)
        approved_metadata = {
            "asset_id": "asset-approved",
            "asset_name": "SIS Event Banner",
            "approval_status": "Approved",
            "marketplace_status": "Review Queue",
            "creator_agent": "Mason",
            "file_locations": {
                "metadata": str(approved_folder / "asset_metadata.json"),
            },
        }
        (approved_folder / "asset_metadata.json").write_text(json.dumps(approved_metadata), encoding="utf-8")

        registry = {
            "assets": [
                {
                    "asset_id": "asset-pending",
                    "asset_name": "Faith Over Fear Tee",
                    "creator_agent": "Micah",
                    "creation_date": "2026-06-18",
                    "approval_status": "Pending Approval",
                    "marketplace_status": "Review Queue",
                    "file_location": "RAMFAM_KINGDOM_BRAIN/designs/faith-over-fear.png",
                    "asset_preview": "/assets/designs/faith-over-fear.png",
                    "file_locations": {
                        "svg": str(pending_folder / "asset-pending.svg"),
                        "png": str(pending_folder / "asset-pending.png"),
                        "metadata": str(pending_folder / "asset_metadata.json"),
                        "listing_package": str(listing_package),
                        "seo_tags": str(listing_package / "seo_tags.txt"),
                        "marketing_copy": str(listing_package / "marketing_copy.txt"),
                    },
                },
                {
                    "asset_id": "asset-approved",
                    "asset_name": "SIS Event Banner",
                    "creator_agent": "Mason",
                    "creation_date": "2026-06-17",
                    "approval_status": "Approved",
                    "marketplace_status": "Review Queue",
                    "file_location": "RAMFAM_KINGDOM_BRAIN/designs/sis-event-banner.svg",
                    "asset_preview": "",
                    "file_locations": {
                        "metadata": str(approved_folder / "asset_metadata.json"),
                    },
                },
                {
                    "asset_id": "asset-published",
                    "asset_name": "Fresh Hope Hoodie",
                    "creator_agent": "Micah",
                    "creation_date": "2026-06-16",
                    "approval_status": "Approved",
                    "marketplace_status": "Published",
                    "publication_type": "digital",
                    "publication_scope": "internal_kingdom_gallery_only",
                    "channels": ["kingdom_gallery"],
                    "external_channels": [],
                    "file_location": "RAMFAM_KINGDOM_BRAIN/designs/fresh-hope-hoodie.png",
                },
            ]
        }
        revenue = {
            "assets": {
                "asset-pending": {"total_revenue": 0, "units_sold": 0},
                "asset-approved": {"total_revenue": 0, "units_sold": 0},
                "asset-published": {"total_revenue": 428.75, "units_sold": 9, "is_top_seller": True},
            }
        }
        (self.design_gallery_root / "asset_registry.json").write_text(json.dumps(registry), encoding="utf-8")
        (self.design_gallery_root / "revenue_tracking.json").write_text(json.dumps(revenue), encoding="utf-8")

    def get_response_data(self, path: str) -> tuple[int, bytes]:
        response = self.client.get(path)
        try:
            return response.status_code, response.data
        finally:
            response.close()

    def test_commerce_command_center_serves_newest_existing_dashboard_without_hardcoded_timestamp(self):
        self.write_dashboard("commerce_pipeline_mission_20240101_010101", "<h1>Older Dashboard</h1>")
        newest = self.write_dashboard("commerce_pipeline_mission_20240103_010101", "<h1>Newest Dashboard</h1>")
        self.write_dashboard("commerce_pipeline_mission_20240102_010101", "<h1>Middle Dashboard</h1>")

        status_code, data = self.get_response_data("/commerce-command-center")

        self.assertEqual(status_code, 200)
        self.assertIn(b"commerce_pipeline_mission_20240103_010101", data)
        self.assertIn(b"/commerce-command-center/source", data)
        source_status, source_data = self.get_response_data("/commerce-command-center/source")
        self.assertEqual(source_status, 200)
        self.assertIn(b"Newest Dashboard", source_data)
        self.assertNotIn(b"Older Dashboard", source_data)
        self.assertTrue(newest.exists())

    def test_commerce_command_center_skips_newer_mission_without_dashboard_and_serves_newest_dashboard(self):
        self.write_dashboard("commerce_pipeline_mission_20240101_010101", "<h1>Older Dashboard</h1>")
        (self.pipeline_root / "commerce_pipeline_mission_20240104_010101").mkdir(parents=True)

        status_code, data = self.get_response_data("/commerce-command-center")

        self.assertEqual(status_code, 200)
        self.assertIn(b"commerce_pipeline_mission_20240101_010101", data)
        source_status, source_data = self.get_response_data("/commerce-command-center/source")
        self.assertEqual(source_status, 200)
        self.assertIn(b"Older Dashboard", source_data)
        self.assertNotIn(b"No Commerce Mission Dashboard Found", data)

    def test_commerce_command_center_shows_friendly_message_when_no_dashboard_exists(self):
        (self.pipeline_root / "commerce_pipeline_mission_20240104_010101").mkdir(parents=True)

        status_code, data = self.get_response_data("/commerce-command-center")

        self.assertEqual(status_code, 200)
        self.assertIn(b"No Commerce Mission Dashboard Found", data)

    def test_neural_core_has_clean_command_navigation(self):
        status_code, data = self.get_response_data("/neural")

        self.assertEqual(status_code, 200)
        self.assertIn("🚀 Atlas Mission Control".encode("utf-8"), data)
        self.assertIn("💰 Commerce Command Center".encode("utf-8"), data)
        self.assertIn("🎨 Kingdom Gallery".encode("utf-8"), data)
        self.assertIn("🐺 Customer Command".encode("utf-8"), data)
        self.assertIn(b"/commerce-command-center", data)
        self.assertIn(b"/design-gallery", data)
        self.assertIn(b"/crm", data)
        self.assertNotIn(b"David CRM", data)
        self.assertNotIn(b"/ramfam", data)

    def test_design_gallery_page_loads_kingdom_gallery_sections_and_client_data_source(self):
        status_code, data = self.get_response_data("/design-gallery")

        self.assertEqual(status_code, 200)
        self.assertIn(b"RAMFAM KINGDOM Gallery", data)
        self.assertIn(b"Recent Kingdom Activity", data)
        self.assertIn(b"Kingdom Review Queue", data)
        self.assertIn(b"Review Queue", data)
        self.assertIn(b"Approved", data)
        self.assertIn(b"Rejected", data)
        self.assertIn(b"Published", data)
        self.assertIn(b"Top Sellers", data)
        self.assertIn(b"/api/design-gallery/assets", data)

    def test_design_gallery_page_has_status_action_buttons_and_full_preview_modal(self):
        status_code, data = self.get_response_data("/design-gallery")

        self.assertEqual(status_code, 200)
        self.assertIn(b"Approve Result", data)
        self.assertIn(b"Needs Revision", data)
        self.assertIn(b"Publish Digital to Gallery", data)
        self.assertNotIn(b"Publish Physical", data)
        self.assertNotIn(b"Publish Both", data)
        self.assertNotIn(b">Publish</button>", data)
        self.assertIn(b"Preview", data)
        self.assertIn(b"preview-modal", data)
        self.assertIn(b"/api/commerce/approval/assets/", data)

    def test_design_gallery_page_renders_publication_type_and_channels(self):
        status_code, data = self.get_response_data("/design-gallery")

        self.assertEqual(status_code, 200)
        self.assertIn(b"Publication Type", data)
        self.assertIn(b"Published Channels", data)
        self.assertIn(b"Kingdom Gallery", data)
        self.assertNotIn(b"Etsy Digital", data)
        self.assertNotIn(b"Shopify Digital", data)
        self.assertNotIn(b"Shopify Physical", data)
        self.assertNotIn(b"Printify Fulfillment", data)

    def test_design_gallery_page_has_asset_file_buttons_and_timeline_renderer(self):
        status_code, data = self.get_response_data("/design-gallery")

        self.assertEqual(status_code, 200)
        self.assertIn(b"View SVG", data)
        self.assertIn(b"View PNG", data)
        self.assertIn(b"View Metadata", data)
        self.assertIn(b"View Listing Package", data)
        self.assertIn(b"View SEO Tags", data)
        self.assertIn(b"View Marketing Copy", data)
        self.assertIn(b"Asset Timeline", data)

    def test_design_gallery_preview_hover_targets_image_and_avoids_card_clipping(self):
        status_code, data = self.get_response_data("/design-gallery")
        html = data.decode("utf-8")

        self.assertEqual(status_code, 200)
        self.assertIn(".asset-preview.has-image:hover img", html)
        self.assertIn("transform: scale(2.75);", html)
        self.assertIn("transform-origin: left center;", html)
        self.assertIn(".asset-card:has(.asset-preview.has-image:hover)", html)
        self.assertIn("overflow: visible;", html)

    def test_design_gallery_api_groups_assets_by_status_and_merges_revenue(self):
        self.write_design_gallery_sources()

        response = self.client.get("/api/design-gallery/assets")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["counts"], {
            "pending_approval": 1,
            "approved": 1,
            "rejected": 0,
            "published_digital": 1,
            "top_sellers": 1,
        })
        self.assertEqual(payload["workflow"]["approval_target"], "results_not_work")
        self.assertTrue(payload["workflow"]["internal_work_auto_authorized"])
        self.assertEqual(payload["review_queue"][0]["asset_name"], "Faith Over Fear Tee")
        self.assertEqual(payload["sections"]["pending_approval"][0]["asset_name"], "Faith Over Fear Tee")
        self.assertEqual(payload["sections"]["approved"][0]["creator_agent"], "Mason")
        self.assertEqual(payload["sections"]["published_digital"][0]["marketplace_status"], "Published")
        self.assertEqual(payload["sections"]["top_sellers"][0]["revenue_tracking"]["total_revenue"], 428.75)
        self.assertEqual(payload["sections"]["top_sellers"][0]["file_location"], "RAMFAM_KINGDOM_BRAIN/designs/fresh-hope-hoodie.png")

    def test_design_gallery_api_returns_recent_activity_file_links_and_asset_timeline(self):
        self.write_design_gallery_sources()

        response = self.client.get("/api/design-gallery/assets")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        pending_asset = payload["sections"]["pending_approval"][0]
        self.assertEqual(pending_asset["file_links"]["svg"], "/design-gallery/file/pending/asset-pending/asset-pending.svg")
        self.assertEqual(pending_asset["file_links"]["png"], "/design-gallery/file/pending/asset-pending/asset-pending.png")
        self.assertEqual(pending_asset["file_links"]["metadata"], "/design-gallery/file/pending/asset-pending/asset_metadata.json")
        self.assertEqual(pending_asset["file_links"]["listing_package"], "/design-gallery/file/pending/asset-pending/listing_package/etsy_listing.txt")
        self.assertEqual(pending_asset["file_links"]["seo_tags"], "/design-gallery/file/pending/asset-pending/listing_package/seo_tags.txt")
        self.assertEqual(pending_asset["file_links"]["marketing_copy"], "/design-gallery/file/pending/asset-pending/listing_package/marketing_copy.txt")
        self.assertEqual(
            [step["action"] for step in pending_asset["timeline"]],
            [
                "Hunter discovered opportunity",
                "Micah created asset",
                "Mason stored asset",
                "Amanda created listing package",
            ],
        )
        self.assertIn("recent_activity", payload)
        self.assertEqual(payload["recent_activity"][0]["agent"], "Amanda")
        self.assertEqual(payload["recent_activity"][0]["action"], "created listing package")
        self.assertEqual(payload["recent_activity"][0]["asset"], "Faith Over Fear Tee")

    def test_design_gallery_status_api_approves_pending_asset_and_updates_metadata_file(self):
        self.write_design_gallery_sources()

        response = self.client.patch("/api/design-gallery/assets/asset-pending/status", json={"action": "approve"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["asset"]["approval_status"], "Approved")
        self.assertEqual(payload["asset"]["marketplace_status"], "Review Queue")
        self.assertEqual(payload["counts"]["pending_approval"], 0)
        self.assertEqual(payload["counts"]["approved"], 2)

        registry = json.loads((self.design_gallery_root / "asset_registry.json").read_text(encoding="utf-8"))
        registry_asset = next(asset for asset in registry["assets"] if asset["asset_id"] == "asset-pending")
        self.assertEqual(registry_asset["approval_status"], "Approved")
        self.assertEqual(registry_asset["marketplace_status"], "Review Queue")

        metadata = json.loads((self.design_gallery_root / "pending" / "asset-pending" / "asset_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["approval_status"], "Approved")
        self.assertEqual(metadata["marketplace_status"], "Review Queue")

    def test_design_gallery_status_api_marks_pending_result_for_revision_and_groups_rejected_section(self):
        self.write_design_gallery_sources()

        response = self.client.patch("/api/design-gallery/assets/asset-pending/status", json={"action": "reject"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["asset"]["approval_status"], "Rejected")
        self.assertEqual(payload["asset"]["marketplace_status"], "Review Queue")
        self.assertEqual(payload["counts"]["pending_approval"], 0)
        self.assertEqual(payload["counts"]["rejected"], 1)

    def test_design_gallery_status_api_publishes_approved_asset_to_internal_kingdom_gallery_only(self):
        self.write_design_gallery_sources()

        response = self.client.patch("/api/design-gallery/assets/asset-approved/status", json={"action": "publish_digital"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["asset"]["approval_status"], "Approved")
        self.assertEqual(payload["asset"]["marketplace_status"], "Published")
        self.assertEqual(payload["asset"]["publication_type"], "digital")
        self.assertEqual(payload["asset"]["publication_scope"], "internal_kingdom_gallery_only")
        self.assertEqual(payload["asset"]["channels"], ["kingdom_gallery"])
        self.assertEqual(payload["asset"]["external_channels"], [])
        self.assertFalse(payload["asset"]["manual_approval_required"])
        self.assertEqual(payload["asset"]["manual_approval_scope"], "internal_kingdom_gallery_only")
        self.assertTrue(payload["asset"]["external_publication_blocked"])
        self.assertEqual(payload["counts"]["approved"], 0)
        self.assertEqual(payload["counts"]["published_digital"], 2)

        registry = json.loads((self.design_gallery_root / "asset_registry.json").read_text(encoding="utf-8"))
        registry_asset = next(asset for asset in registry["assets"] if asset["asset_id"] == "asset-approved")
        self.assertEqual(registry_asset["publication_type"], "digital")
        self.assertEqual(registry_asset["channels"], ["kingdom_gallery"])
        self.assertEqual(registry_asset["external_channels"], [])

        metadata = json.loads((self.design_gallery_root / "pending" / "asset-approved" / "asset_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["publication_type"], "digital")
        self.assertEqual(metadata["channels"], ["kingdom_gallery"])

        blocked = self.client.patch("/api/design-gallery/assets/asset-pending/status", json={"action": "publish_digital"})
        self.assertEqual(blocked.status_code, 400)

    def test_commerce_approval_api_routes_approve_reject_and_publish_digital_to_gallery(self):
        self.write_design_gallery_sources()

        approve = self.client.post("/api/commerce/approval/assets/asset-pending/approve")
        self.assertEqual(approve.status_code, 200)
        self.assertEqual(approve.get_json()["asset"]["approval_status"], "Approved")

        self.write_design_gallery_sources()
        reject = self.client.post("/api/commerce/approval/assets/asset-pending/reject")
        self.assertEqual(reject.status_code, 200)
        self.assertEqual(reject.get_json()["asset"]["approval_status"], "Rejected")

        publish = self.client.post("/api/commerce/approval/assets/asset-approved/publish-digital")
        self.assertEqual(publish.status_code, 200)
        payload = publish.get_json()
        self.assertEqual(payload["asset"]["marketplace_status"], "Published")
        self.assertEqual(payload["asset"]["channels"], ["kingdom_gallery"])
        self.assertEqual(payload["asset"]["external_channels"], [])
        self.assertEqual(payload["external_side_effects"], [])

    def test_design_gallery_status_api_blocks_physical_and_both_external_publication_actions(self):
        self.write_design_gallery_sources()

        physical = self.client.patch("/api/design-gallery/assets/asset-approved/status", json={"action": "publish_physical"})
        self.assertEqual(physical.status_code, 400)
        self.assertIn("internal Kingdom Gallery", physical.get_json()["error"])

        both = self.client.patch("/api/design-gallery/assets/asset-approved/status", json={"action": "publish_both"})
        self.assertEqual(both.status_code, 400)
        self.assertIn("internal Kingdom Gallery", both.get_json()["error"])

    def test_design_gallery_status_api_creates_metadata_tracking_when_publishing_registry_only_asset(self):
        self.write_design_gallery_sources()
        registry_path = self.design_gallery_root / "asset_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["assets"].append({
            "asset_id": "asset-registry-only",
            "asset_name": "Registry Only Asset",
            "creator_agent": "Mason",
            "creation_date": "2026-06-18",
            "approval_status": "Approved",
            "marketplace_status": "Review Queue",
            "file_location": "RAMFAM_KINGDOM_BRAIN/designs/registry-only.svg",
        })
        registry_path.write_text(json.dumps(registry), encoding="utf-8")

        response = self.client.patch("/api/design-gallery/assets/asset-registry-only/status", json={"action": "publish_digital"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        metadata_path = Path(payload["metadata_path"])
        self.assertEqual(metadata_path, self.design_gallery_root / "pending" / "asset-registry-only" / "asset_metadata.json")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["asset_id"], "asset-registry-only")
        self.assertEqual(metadata["publication_type"], "digital")
        self.assertEqual(metadata["channels"], ["kingdom_gallery"])
        self.assertEqual(metadata["publication_scope"], "internal_kingdom_gallery_only")

    def test_design_gallery_serves_pending_factory_asset_previews(self):
        preview_folder = self.design_gallery_root / "pending" / "faith_over_fear"
        preview_folder.mkdir(parents=True, exist_ok=True)
        png_bytes = b"\x89PNG\r\n\x1a\npreview-bytes"
        (preview_folder / "faith_over_fear.png").write_bytes(png_bytes)

        status_code, data = self.get_response_data("/design-gallery/pending/faith_over_fear/faith_over_fear.png")

        self.assertEqual(status_code, 200)
        self.assertEqual(data, png_bytes)

    def test_design_gallery_file_route_serves_gallery_files_without_file_explorer(self):
        self.write_design_gallery_sources()

        status_code, data = self.get_response_data("/design-gallery/file/pending/asset-pending/listing_package/seo_tags.txt")

        self.assertEqual(status_code, 200)
        self.assertIn(b"faith,hope,shirt", data)

    def test_design_gallery_links_latest_prompt_exporter_outputs(self):
        self.write_design_gallery_exports("commerce_pipeline_mission_20240101_010101")

        status_code, data = self.get_response_data("/design-gallery")

        self.assertEqual(status_code, 200)
        self.assertIn(b"Latest prompt report", data)
        self.assertIn(b"/design-gallery/export/commerce_image_prompts_latest.md", data)
        self.assertIn(b"Latest prompt JSON", data)

        export_status, export_data = self.get_response_data("/design-gallery/export/commerce_image_prompts_latest.md")
        self.assertEqual(export_status, 200)
        self.assertIn(b"Latest Design Prompt Report", export_data)


if __name__ == "__main__":
    unittest.main()
