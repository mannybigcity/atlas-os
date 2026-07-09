import importlib
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import crm.crm_skill as crm_skill


class CRMSystemTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.prospects_file = Path(self.tempdir.name) / "prospects.json"
        self.customers_file = Path(self.tempdir.name) / "customers.json"
        self.prospects_file.write_text("[]", encoding="utf-8")
        self.customers_file.write_text("[]", encoding="utf-8")
        crm_skill.PROSPECTS_FILE = str(self.prospects_file)
        crm_skill.CUSTOMERS_FILE = str(self.customers_file)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_create_prospect_assigns_id_and_revenue_fields(self):
        prospect = crm_skill.create_prospect({
            "name": "Manny Ramirez",
            "business": "SIS Custom Creations",
            "product": "100 fundraiser shirts",
            "status": "Hot",
            "value": "1250.50",
            "email": "manny@example.com",
            "phone": "555-0101",
            "source": "Referral",
            "notes": "Needs quote today"
        })

        self.assertTrue(prospect["id"].startswith("crm_"))
        self.assertEqual(prospect["value"], 1250.50)
        self.assertEqual(prospect["status"], "Hot")
        self.assertEqual(prospect["next_action"], "Send quote / mockup and ask for decision date")
        self.assertEqual(len(crm_skill.load_prospects()), 1)

    def test_search_and_summary_prioritize_money_and_followups(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        crm_skill.create_prospect({"name": "Uncle Ray", "business": "Manpower Resources", "product": "Patch hats", "status": "Invoice Sent", "value": 800, "follow_up": yesterday})
        crm_skill.create_prospect({"name": "Kandy", "business": "Canes Baseball", "product": "Team shirts", "status": "Quoted", "value": 1200, "follow_up": tomorrow})
        crm_skill.create_prospect({"name": "Bobby", "business": "B&B HVAC", "product": "Hats", "status": "Closed Lost", "value": 500})

        matches = crm_skill.search_prospects("canes")
        summary = crm_skill.get_crm_dashboard()

        self.assertEqual([m["name"] for m in matches], ["Kandy"])
        self.assertEqual(summary["total_prospects"], 3)
        self.assertEqual(summary["active_pipeline_value"], 2000.0)
        self.assertEqual(summary["followups_overdue"], 1)
        self.assertEqual(summary["next_money_target"]["name"], "Kandy")

    def test_dashboard_includes_customer_book_of_business(self):
        crm_skill.create_customer({"name": "Kandy", "business": "Canes Baseball", "lifetime_value": 1200})
        crm_skill.create_customer({"name": "Bobby", "business": "B&B HVAC", "lifetime_value": 650})

        summary = crm_skill.get_crm_dashboard()

        self.assertEqual(summary["total_customers"], 2)
        self.assertEqual(summary["customer_lifetime_value"], 1850.0)

    def test_update_prospect_and_convert_to_customer(self):
        prospect = crm_skill.create_prospect({"name": "Bobby", "business": "B&B HVAC", "product": "Uniform shirts", "status": "Quoted", "value": 650})

        updated = crm_skill.update_prospect(prospect["id"], {"status": "Closed Won", "notes": "Paid deposit"})
        customer = crm_skill.convert_prospect_to_customer(prospect["id"])

        self.assertEqual(updated["status"], "Closed Won")
        self.assertEqual(customer["business"], "B&B HVAC")
        self.assertEqual(customer["lifetime_value"], 650.0)
        self.assertEqual(len(crm_skill.load_customers()), 1)

    def test_create_search_update_and_delete_customer_records(self):
        customer = crm_skill.create_customer({
            "name": "Manny Ramirez",
            "business": "SIS Custom Creations",
            "email": "manny@example.com",
            "phone": "555-0101",
            "last_product": "Fundraiser shirts",
            "lifetime_value": "$2,400",
            "status": "Active",
            "notes": "Prefers text updates"
        })

        self.assertTrue(customer["id"].startswith("cus_"))
        self.assertEqual(customer["lifetime_value"], 2400.0)
        self.assertEqual(crm_skill.search_customers("sis")[0]["id"], customer["id"])

        updated = crm_skill.update_customer(customer["id"], {"status": "VIP", "notes": "Repeat buyer"})
        self.assertEqual(updated["status"], "VIP")
        self.assertEqual(updated["notes"], "Repeat buyer")

        crm_skill.delete_customer(customer["id"])
        self.assertEqual(crm_skill.search_customers(), [])

    def test_legacy_add_prospect_still_works(self):
        message = crm_skill.add_prospect("Kandy", "Canes Baseball", "Team Shirts", "Hot", "Call Friday")
        saved = crm_skill.load_prospects()[0]

        self.assertIn("Prospect added: Kandy", message)
        self.assertTrue(saved["id"].startswith("crm_"))
        self.assertEqual(saved["notes"], "Call Friday")

    def test_log_touchpoints_on_prospects_and_customers(self):
        prospect = crm_skill.create_prospect({"name": "Kandy", "business": "Canes Baseball", "status": "Hot"})
        customer = crm_skill.create_customer({"name": "Manny", "business": "SIS Custom Creations"})

        prospect_touch = crm_skill.add_prospect_touchpoint(prospect["id"], {
            "type": "Call",
            "note": "Confirmed decision maker and jersey deadline",
            "next_follow_up": "2026-06-20",
        })
        customer_touch = crm_skill.add_customer_touchpoint(customer["id"], {
            "type": "Text",
            "note": "Asked for reorder timing",
        })

        updated_prospect = crm_skill.find_prospect(prospect["id"])
        updated_customer = crm_skill.search_customers("manny")[0]
        timeline = crm_skill.get_activity_timeline()

        self.assertTrue(prospect_touch["id"].startswith("act_"))
        self.assertEqual(updated_prospect["follow_up"], "2026-06-20")
        self.assertEqual(updated_prospect["activities"][0]["note"], "Confirmed decision maker and jersey deadline")
        self.assertEqual(customer_touch["type"], "Text")
        self.assertEqual(updated_customer["activities"][0]["note"], "Asked for reorder timing")
        self.assertEqual([item["record_type"] for item in timeline], ["customer", "prospect"])

    def test_customer_followups_are_tracked_in_dashboard_and_queue(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        crm_skill.create_customer({
            "name": "Manny",
            "business": "SIS Custom Creations",
            "status": "Needs Follow-Up",
            "follow_up": yesterday,
            "next_action": "Ask for reorder timing",
        })
        crm_skill.create_prospect({
            "name": "Kandy",
            "business": "Canes Baseball",
            "status": "Hot",
            "follow_up": tomorrow,
        })

        summary = crm_skill.get_crm_dashboard()
        followups = crm_skill.get_followups()

        self.assertEqual(summary["followups_total"], 2)
        self.assertEqual(summary["followups_overdue"], 1)
        self.assertEqual(followups[0]["record_type"], "customer")
        self.assertEqual(followups[0]["next_action"], "Ask for reorder timing")


if __name__ == "__main__":
    unittest.main()
