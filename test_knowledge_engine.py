import unittest

from atlas_os.knowledge_engine import (
    atlas_knowledge_map,
    load_knowledge_for,
    knowledge_registry,
    mission_context,
)


class KnowledgeEngineFoundationTest(unittest.TestCase):
    def test_registry_contains_required_governance_and_executives(self):
        registry = knowledge_registry()

        self.assertEqual(registry["version"], "1.0")
        self.assertIn("ATLAS_CONSTITUTION_V2", registry["governing_documents"])
        self.assertIn("KNOWLEDGE_ENGINE_SPEC", registry["governing_documents"])
        self.assertEqual(len(registry["executives"]), 13)
        self.assertEqual(registry["executives"]["mason"]["department"], "architecture")

    def test_mason_knowledge_engine_loads_only_required_default_documents(self):
        result = load_knowledge_for(executive="Mason", task_type="knowledge_engine")
        document_ids = [document["id"] for document in result["documents"]]

        self.assertIn("ATLAS_DEVELOPMENT_STANDARD", document_ids)
        self.assertIn("ATLAS_MASTER_IMPLEMENTATION_PLAN", document_ids)
        self.assertIn("KNOWLEDGE_ENGINE_SPEC", document_ids)
        self.assertNotIn("EXECUTIVE_HANDBOOK", document_ids)
        self.assertFalse(any(document["optional"] for document in result["documents"]))
        self.assertEqual(document_ids, list(dict.fromkeys(document_ids)))

    def test_solomon_governance_gets_constitution_and_compliance_context(self):
        result = load_knowledge_for(executive="Solomon", task_type="governance")
        document_ids = [document["id"] for document in result["documents"]]
        knowledge_ids = [item["id"] for item in result["knowledge"]]

        self.assertIn("ATLAS_CONSTITUTION_V2", document_ids)
        self.assertIn("EXECUTIVE_HANDBOOK", document_ids)
        self.assertIn("governance", knowledge_ids)
        self.assertIn("compliance", knowledge_ids)

    def test_optional_knowledge_is_excluded_until_requested(self):
        default_result = load_knowledge_for(executive="Hunter", task_type="sales")
        optional_result = load_knowledge_for(executive="Hunter", task_type="sales", include_optional=True)

        self.assertFalse(any(document["optional"] for document in default_result["documents"]))
        self.assertGreater(len(optional_result["documents"]), len(default_result["documents"]))
        self.assertTrue(any(document["optional"] for document in optional_result["documents"]))

    def test_unknown_request_uses_minimal_governance_fallback(self):
        result = load_knowledge_for(executive="Unknown", task_type="mystery")
        document_ids = [document["id"] for document in result["documents"]]

        self.assertEqual(document_ids, ["ATLAS_DEVELOPMENT_STANDARD"])
        self.assertIn("No exact executive route", result["notes"][0])

    def test_legacy_mission_context_still_works(self):
        context = mission_context("mason")
        self.assertIn("skills", context["load_only"])
        self.assertIn("knowledge_route", context)

    def test_legacy_knowledge_map_still_reports_paths(self):
        knowledge_map = atlas_knowledge_map()
        self.assertIn("governing_documents", knowledge_map)
        self.assertTrue(knowledge_map["governing_documents"]["exists"])


if __name__ == "__main__":
    unittest.main()
