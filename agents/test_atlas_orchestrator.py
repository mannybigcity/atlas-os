from pathlib import Path
import sys
from unittest.mock import patch

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents import atlas_orchestrator as orchestrator_module

ROUTE_CASES = [
    ("Please build the retry system", "Mason"),
    ("Find new leads for SIS", "Hunter"),
    ("Review profit margin and cost", "Gideon"),
    ("Schedule CRM follow-up for customers", "David"),
    ("Write an outreach message for a partnership", "Amanda"),
    ("Handle this customer issue and retention risk", "Ranger"),
    ("Research and find info on competitors", "Scout"),
    ("Draft a social media caption for this post", "Micah"),
    ("Create website landing page copy", "Taylor"),
]


def fake_delegate(task, context=None):
    return {
        "status": "delegated",
        "delegated_to": context["agent"].title(),
        "task": task,
        "context": context,
        "result": {"status": "success", "agent": context["agent"].title()},
        "timestamp": "delegation-timestamp",
    }


def test_every_keyword_route_calls_atlas_agent_delegation():
    calls = []

    def capture_delegate(task, context=None):
        calls.append({"task": task, "context": context})
        return fake_delegate(task, context)

    with patch.object(orchestrator_module.atlas_agent_delegation, "delegate_to_agent", capture_delegate):
        for text, expected_agent in ROUTE_CASES:
            result = orchestrator_module.atlas_orchestrator(text, {"source": "test"})
            assert result["routed_to"] == expected_agent
            assert expected_agent in result["reason"]
            assert result["result"]["status"] == "delegated"
            assert result["result"]["delegated_to"] == expected_agent
            assert "timestamp" in result
            assert "T" in result["timestamp"]
            assert calls[-1]["task"] == text
            assert calls[-1]["context"]["agent"] == expected_agent.lower()
            assert calls[-1]["context"]["source"] == "test"


def test_context_agent_override_wins():
    with patch.object(orchestrator_module.atlas_agent_delegation, "delegate_to_agent", fake_delegate):
        result = orchestrator_module.atlas_orchestrator("Build a revenue page", {"agent": "hunter"})
    assert result["routed_to"] == "Hunter"
    assert "context override" in result["reason"].lower()
    assert result["result"]["delegated_to"] == "Hunter"


def test_unknown_request_defaults_to_mason_for_system_improvement():
    with patch.object(orchestrator_module.atlas_agent_delegation, "delegate_to_agent", fake_delegate):
        result = orchestrator_module.atlas_orchestrator("Make the operating system better")
    assert result["routed_to"] == "Mason"
    assert result["result"]["delegated_to"] == "Mason"


def test_atlas_identity_questions_answer_directly_without_delegation():
    with patch.object(orchestrator_module.atlas_agent_delegation, "delegate_to_agent") as delegate:
        result = orchestrator_module.atlas_orchestrator(
            "Who are you? What are your authority rules? What are your allowed write locations?"
        )

    delegate.assert_not_called()
    assert result["routed_to"] == "Atlas"
    assert result["result"]["agent"] == "Atlas"
    assert result["result"]["status"] == "answered_by_atlas"
    assert result["result"]["allowed_write_locations"]


if __name__ == "__main__":
    tests = [
        test_every_keyword_route_calls_atlas_agent_delegation,
        test_context_agent_override_wins,
        test_unknown_request_defaults_to_mason_for_system_improvement,
        test_atlas_identity_questions_answer_directly_without_delegation,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}: PASS")
    print("ATLAS ORCHESTRATOR ROUTES VERIFIED")
