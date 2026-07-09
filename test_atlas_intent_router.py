import unittest

from atlas_intent_router import route_intent


class AtlasIntentRouterMemoryTests(unittest.TestCase):
    def test_memory_questions_route_to_retrieval_without_atlas_prefix(self):
        cases = [
            "Who is my wife?",
            "What do you remember about me?",
            "What is Deleana current goal?",
            "What does SIS believe every project tells?",
        ]
        for message in cases:
            with self.subTest(message=message):
                self.assertEqual(route_intent(message)["intent"], "retrieval")

    def test_agent_availability_question_does_not_route_to_memory_retrieval(self):
        self.assertEqual(route_intent("Who is available today?")["intent"], "chat")


if __name__ == "__main__":
    unittest.main(verbosity=2)
