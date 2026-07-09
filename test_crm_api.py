import json
import tempfile
import unittest
from pathlib import Path

import app
import crm.crm_skill as crm_skill


class CRMApiTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        crm_skill.PROSPECTS_FILE = str(Path(self.tempdir.name) / "prospects.json")
        crm_skill.CUSTOMERS_FILE = str(Path(self.tempdir.name) / "customers.json")
        Path(crm_skill.PROSPECTS_FILE).write_text("[]", encoding="utf-8")
        Path(crm_skill.CUSTOMERS_FILE).write_text("[]", encoding="utf-8")
        self.client = app.app.test_client()
        with self.client.session_transaction() as session:
            session["atlas_admin_authenticated"] = True
            session["atlas_admin_username"] = "test-admin"

    def tearDown(self):
        self.tempdir.cleanup()

    def test_crm_api_creates_lists_and_updates_prospects(self):
        create_response = self.client.post("/api/crm/prospects", json={
            "name": "Kandy",
            "business": "Canes Baseball",
            "product": "Team shirts",
            "status": "Hot",
            "value": 1200,
        })
        self.assertEqual(create_response.status_code, 201)
        created = create_response.get_json()["prospect"]

        list_response = self.client.get("/api/crm/prospects?q=canes")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.get_json()["prospects"][0]["id"], created["id"])

        update_response = self.client.patch(f"/api/crm/prospects/{created['id']}", json={"status": "Invoice Sent"})
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.get_json()["prospect"]["next_action"], "Collect payment and confirm production timeline")

        summary_response = self.client.get("/api/crm/summary")
        self.assertEqual(summary_response.status_code, 200)
        self.assertEqual(summary_response.get_json()["summary"]["active_pipeline_value"], 1200.0)

    def test_crm_api_manages_customer_records(self):
        create_response = self.client.post("/api/crm/customers", json={
            "name": "Manny Ramirez",
            "business": "SIS Custom Creations",
            "last_product": "Event shirts",
            "lifetime_value": 1800,
            "status": "Active",
            "notes": "Kingdom priority account"
        })
        self.assertEqual(create_response.status_code, 201)
        customer = create_response.get_json()["customer"]

        list_response = self.client.get("/api/crm/customers?q=sis")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.get_json()["customers"][0]["id"], customer["id"])

        update_response = self.client.patch(f"/api/crm/customers/{customer['id']}", json={"status": "VIP"})
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.get_json()["customer"]["status"], "VIP")

        delete_response = self.client.delete(f"/api/crm/customers/{customer['id']}")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(self.client.get("/api/crm/customers").get_json()["customers"], [])

    def test_crm_api_logs_touchpoints_and_timeline(self):
        prospect_response = self.client.post("/api/crm/prospects", json={
            "name": "Kandy",
            "business": "Canes Baseball",
            "status": "Hot",
        })
        customer_response = self.client.post("/api/crm/customers", json={
            "name": "Manny Ramirez",
            "business": "SIS Custom Creations",
        })
        prospect_id = prospect_response.get_json()["prospect"]["id"]
        customer_id = customer_response.get_json()["customer"]["id"]

        prospect_touch_response = self.client.post(f"/api/crm/prospects/{prospect_id}/touchpoints", json={
            "type": "Call",
            "note": "Confirmed jersey deadline",
            "next_follow_up": "2026-06-20",
        })
        customer_touch_response = self.client.post(f"/api/crm/customers/{customer_id}/touchpoints", json={
            "type": "Text",
            "note": "Asked for reorder timing",
        })
        timeline_response = self.client.get("/api/crm/timeline")

        self.assertEqual(prospect_touch_response.status_code, 201)
        self.assertEqual(customer_touch_response.status_code, 201)
        self.assertEqual(prospect_touch_response.get_json()["touchpoint"]["note"], "Confirmed jersey deadline")
        self.assertEqual(timeline_response.status_code, 200)
        self.assertEqual([item["record_type"] for item in timeline_response.get_json()["timeline"]], ["customer", "prospect"])

    def test_crm_api_returns_customer_followups_in_command_queue(self):
        customer_response = self.client.post("/api/crm/customers", json={
            "name": "Manny Ramirez",
            "business": "SIS Custom Creations",
            "status": "Needs Follow-Up",
            "follow_up": "2026-06-20",
            "next_action": "Ask for reorder timing",
        })
        self.assertEqual(customer_response.status_code, 201)

        followup_response = self.client.get("/api/crm/followups")

        self.assertEqual(followup_response.status_code, 200)
        self.assertEqual(followup_response.get_json()["followups"][0]["record_type"], "customer")
        self.assertEqual(followup_response.get_json()["followups"][0]["next_action"], "Ask for reorder timing")

    def test_crm_page_serves_command_center(self):
        response = self.client.get("/crm")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Customer Command", response.data)
        self.assertIn(b"Customer Vault", response.data)
        self.assertIn(b"Activity Timeline", response.data)


if __name__ == "__main__":
    unittest.main()
