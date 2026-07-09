import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app


class MissionsApiTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_missions_file = app.MISSIONS_FILE
        self.original_bus_file = app.executive_bus.BUS_FILE
        app.MISSIONS_FILE = str(Path(self.tempdir.name) / "missions.json")
        app.executive_bus.BUS_FILE = Path(self.tempdir.name) / "executive_messages.json"
        Path(app.MISSIONS_FILE).write_text(json.dumps({"missions": []}), encoding="utf-8")
        app.executive_bus.BUS_FILE.write_text("[]", encoding="utf-8")
        self.client = app.app.test_client()
        with self.client.session_transaction() as session:
            session["atlas_admin_authenticated"] = True
            session["atlas_admin_username"] = "test-admin"

    def tearDown(self):
        app.MISSIONS_FILE = self.original_missions_file
        app.executive_bus.BUS_FILE = self.original_bus_file
        self.tempdir.cleanup()

    def test_complete_status_returns_success_contract_for_ui(self):
        create_response = self.client.post("/api/missions/create", json={
            "agent": "Mason",
            "priority": "HIGH",
            "mission": "Debug false error state",
        })
        self.assertEqual(create_response.status_code, 200)
        self.assertTrue(create_response.get_json()["success"])

        complete_response = self.client.post("/api/missions/status", json={
            "id": 1,
            "status": "Completed",
        })
        payload = complete_response.get_json()

        self.assertEqual(complete_response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["status"], "complete")
        self.assertEqual(payload["result"], "success")
        self.assertEqual(payload["message"], "BUILD COMPLETE")
        self.assertEqual(payload["mission"]["status"], "complete")

    def test_atlas_mission_control_assignment_routes_through_runtime_and_bus(self):
        runtime_result = {
            "routed_to": "Hunter",
            "result": {
                "status": "delegated",
                "summary": "Hunter found a revenue path.",
            },
        }

        with patch.object(app, "atlas_orchestrator", return_value=runtime_result) as orchestrator:
            response = self.client.post("/api/missions/create", json={
                "agent": "ATLAS",
                "priority": "HIGH",
                "mission": "Find new revenue leads for SIS",
            })

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["mission"]["agent"], "Hunter")
        self.assertEqual(payload["mission"]["status"], "complete")
        self.assertEqual(payload["mission"]["latest_result_summary"], "Hunter found a revenue path.")
        orchestrator.assert_called_once()
        self.assertEqual(orchestrator.call_args.args[0], "Find new revenue leads for SIS")

        messages = json.loads(app.executive_bus.BUS_FILE.read_text(encoding="utf-8"))
        self.assertEqual([message["status"] for message in messages], ["new", "working", "complete"])
        self.assertEqual(messages[-1]["to"], "Hunter")
        self.assertEqual(messages[-1]["result_summary"], "Hunter found a revenue path.")

        list_payload = self.client.get("/api/missions/list").get_json()
        listed_mission = list_payload["missions"][-1]
        self.assertEqual(listed_mission["agent"], "Hunter")
        self.assertEqual(listed_mission["status"], "complete")
        self.assertIn("mission_id", listed_mission)

    def test_hermes_work_order_returns_build_complete_contract(self):
        self.client.post("/api/missions/create", json={
            "agent": "Mason",
            "priority": "HIGH",
            "mission": "Review a work order",
        })

        with patch.object(app, "ask_hermes", return_value="Mason report ready."):
            hermes_response = self.client.post("/api/missions/hermes", json={"id": 1})

        payload = hermes_response.get_json()
        self.assertEqual(hermes_response.status_code, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["status"], "complete")
        self.assertEqual(payload["result"], "success")
        self.assertEqual(payload["message"], "BUILD COMPLETE")
        self.assertEqual(payload["response"], "Mason report ready.")

    def test_missing_mission_does_not_return_false_success(self):
        response = self.client.post("/api/missions/status", json={
            "id": 999,
            "status": "Completed",
        })
        payload = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(payload["success"])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"], "Mission not found.")


if __name__ == "__main__":
    unittest.main()
