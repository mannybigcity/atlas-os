from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"
if str(SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(SKILLS_DIR))

import executive_memory_foundation as memory_foundation


class ExecutiveMemoryFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_root = Path(self.temp_dir.name) / "99_MEMORY"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_initialization_creates_isolated_location_for_every_executive(self):
        registry = memory_foundation.initialize_memory_foundation(self.memory_root)

        self.assertEqual(len(registry["executives"]), 13)
        self.assertIn("atlas", registry["executives"])
        self.assertIn("solomon", registry["executives"])

        for slug, executive in registry["executives"].items():
            memory_file = self.memory_root / executive["memory_file"]
            readme_file = self.memory_root / executive["readme_file"]
            self.assertTrue(memory_file.exists(), slug)
            self.assertTrue(readme_file.exists(), slug)
            stored = json.loads(memory_file.read_text(encoding="utf-8"))
            self.assertEqual(stored["owner"], executive["display_name"])
            self.assertEqual(stored["entries"], [])

    def test_registry_and_loader_locate_executive_memory_deterministically(self):
        memory_foundation.initialize_memory_foundation(self.memory_root)

        location = memory_foundation.get_executive_memory_location(
            "Mason", self.memory_root
        )
        self.assertEqual(location.name, "memory.json")
        self.assertIn("mason", str(location).lower())

        loaded = memory_foundation.load_executive_memory("mason", self.memory_root)
        self.assertEqual(loaded["owner"], "Mason")
        self.assertEqual(loaded["entries"], [])

    def test_routing_layer_separates_memory_domains_without_ai_services(self):
        memory_foundation.initialize_memory_foundation(self.memory_root)

        company_route = memory_foundation.route_memory_request(
            "company", "policies", self.memory_root
        )
        client_route = memory_foundation.route_memory_request(
            "client", "sis_custom_creations", self.memory_root
        )
        active_mission_route = memory_foundation.route_memory_request(
            "mission", "active", self.memory_root
        )
        archive_route = memory_foundation.route_memory_request(
            "archive", "lessons_learned", self.memory_root
        )

        self.assertEqual(company_route["domain"], "company")
        self.assertEqual(client_route["domain"], "client")
        self.assertEqual(active_mission_route["domain"], "mission")
        self.assertEqual(archive_route["domain"], "archive")
        self.assertTrue((self.memory_root / active_mission_route["path"]).exists())
        self.assertEqual(active_mission_route["load_policy"], "load_only_requested_state")
        self.assertFalse(company_route["uses_ai"])
        self.assertFalse(company_route["uses_vector_search"])
        self.assertFalse(company_route["uses_semantic_search"])

    def test_knowledge_engine_context_loads_only_requested_routes(self):
        memory_foundation.initialize_memory_foundation(self.memory_root)

        context = memory_foundation.build_memory_context(
            executives=["Atlas", "Hunter"],
            company_sections=["pricing"],
            mission_states=["waiting"],
            memory_root=self.memory_root,
        )

        route_paths = [route["path"] for route in context["routes"]]
        self.assertEqual(len(route_paths), 4)
        self.assertTrue(any("executive_memory/atlas" in path for path in route_paths))
        self.assertTrue(any("executive_memory/hunter" in path for path in route_paths))
        self.assertTrue(any("company_memory/pricing" in path for path in route_paths))
        self.assertTrue(any("mission_memory/waiting" in path for path in route_paths))
        self.assertEqual(context["external_ai_api_cost_usd"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
