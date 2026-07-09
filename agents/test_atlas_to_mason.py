from pathlib import Path
import sys
from unittest.mock import Mock, patch

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.atlas_agent_delegation import atlas_command
from agents import atlas_agent_delegation

created = Mock(returncode=0, stdout='{"id": "t-atlas-mason-test"}', stderr="")
dispatched = Mock(returncode=0, stdout='{"spawned": 1}', stderr="")

with patch.object(atlas_agent_delegation.subprocess, "run", side_effect=[created, dispatched]):
    result = atlas_command("Atlas, have Mason verify all agents", {"agent": "mason", "execute_now": True})

assert result["status"] == "delegated", result
assert result["delegated_to"] == "Mason", result
assert result["result"]["agent"] == "Mason", result
assert result["result"]["status"] in ["dispatched", "queued"], result
assert result["result"]["system"] == "hermes_kanban", result
assert result["result"]["kanban_task_id"] == "t-atlas-mason-test", result

print("ATLAS CAN SPEAK TO HERMES MASON: PASS")
print(result)
