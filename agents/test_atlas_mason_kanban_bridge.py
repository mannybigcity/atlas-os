from pathlib import Path
import sys
from unittest.mock import Mock, patch

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents import atlas_agent_delegation
from agents import atlas_mason_kanban_bridge


def test_bridge_builds_clean_kanban_create_command_with_mason_rules_and_redaction():
    command = atlas_mason_kanban_bridge.build_create_command(
        "Build a clean Atlas-to-Mason bridge",
        {
            "agent": "mason",
            "auto_execute": False,
            "safe_note": "keep this",
            "secret_token": "must-not-leak",
            "nested": {"api_key": "nested-secret", "safe": "keep nested"},
        },
        "atlas_mason_test",
    )

    body = command[command.index("--body") + 1]
    assert command[:3] == ["hermes", "kanban", "create"]
    assert "--assignee" in command
    assert command[command.index("--assignee") + 1] == "mason"
    assert "--skill" in command
    assert command[command.index("--skill") + 1] == "mason-profile"
    assert "--workspace" in command
    assert command[command.index("--workspace") + 1].startswith("dir:")
    assert "--idempotency-key" in command
    assert command[command.index("--idempotency-key") + 1] == "atlas_mason_test"
    assert "Foundry Architect / Kingdom Architect" in body
    assert "Manny approval is required" in body
    assert "keep this" in body
    assert "keep nested" in body
    assert "must-not-leak" not in body
    assert "nested-secret" not in body
    assert "[REDACTED]" in body


def test_mason_delegation_uses_hermes_kanban_not_legacy_queue():
    created = Mock(returncode=0, stdout='{"id": "t_clean_bridge", "status": "ready"}', stderr="")

    with patch.object(atlas_agent_delegation, "_load_mason_queue", return_value=[]), patch.object(
        atlas_agent_delegation, "_save_mason_queue"
    ) as save_legacy_queue, patch.object(atlas_agent_delegation.subprocess, "run", return_value=created) as run:
        result = atlas_agent_delegation.delegate_to_agent(
            "Build a clean Atlas-to-Mason bridge",
            {"agent": "mason", "auto_execute": False},
        )

    save_legacy_queue.assert_not_called()
    assert run.call_count == 1
    assert run.call_args.args[0][:3] == ["hermes", "kanban", "create"]
    assert result["status"] == "queued"
    assert result["delegated_to"] == "Mason"
    assert result["system"] == "hermes_kanban"
    assert result["assignee"] == "mason"
    assert result["kanban_task_id"] == "t_clean_bridge"
    assert "queue_file" not in result


def test_mason_kanban_delegation_dispatches_when_auto_execute_enabled():
    created = Mock(returncode=0, stdout='{"id": "t123", "status": "ready"}', stderr="")
    dispatched = Mock(returncode=0, stdout='{"spawned": 1}', stderr="")

    with patch.object(atlas_agent_delegation.subprocess, "run", side_effect=[created, dispatched]) as run:
        result = atlas_agent_delegation.delegate_to_agent(
            "Build the Mason report",
            {"agent": "mason", "auto_execute": True},
        )

    commands = [call.args[0] for call in run.call_args_list]
    assert commands[0][:3] == ["hermes", "kanban", "create"]
    assert "--assignee" in commands[0]
    assert "mason" in commands[0]
    assert "--skill" in commands[0]
    assert "mason-profile" in commands[0]
    assert commands[1][:3] == ["hermes", "kanban", "dispatch"]
    assert result["status"] == "dispatched"
    assert result["kanban_task_id"] == "t123"
    assert result["worker_invoked"] is True


def test_kanban_task_id_parser_accepts_real_hermes_ids_in_text_output():
    text = "Created task t_2d0c0a8d for mason"
    assert atlas_mason_kanban_bridge.parse_kanban_task_id(text, "atlas_fallback") == "t_2d0c0a8d"


def test_mason_task_body_recursively_redacts_secret_context_values():
    body = atlas_mason_kanban_bridge.build_mason_task_body(
        "Build safe bridge",
        {
            "agent": "mason",
            "token": "top-level-token",
            "nested": {
                "api_key": "nested-api-key",
                "safe": "keep-me",
                "items": [{"password": "nested-password", "note": "keep-note"}],
            },
        },
        "atlas_mason_test",
    )

    assert "top-level-token" not in body
    assert "nested-api-key" not in body
    assert "nested-password" not in body
    assert "keep-me" in body
    assert "keep-note" in body
    assert "[REDACTED]" in body


if __name__ == "__main__":
    tests = [
        test_bridge_builds_clean_kanban_create_command_with_mason_rules_and_redaction,
        test_mason_delegation_uses_hermes_kanban_not_legacy_queue,
        test_mason_kanban_delegation_dispatches_when_auto_execute_enabled,
        test_kanban_task_id_parser_accepts_real_hermes_ids_in_text_output,
        test_mason_task_body_recursively_redacts_secret_context_values,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}: PASS")
    print("ATLAS MASON KANBAN BRIDGE VERIFIED")
