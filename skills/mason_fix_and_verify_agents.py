from pathlib import Path
import sys
import subprocess

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
TEST_FILE = PROJECT_ROOT / "agents" / "test_all_agent_delegation.py"

fixed = r'''from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.atlas_agent_delegation import delegate_to_agent

AGENTS = ["hunter", "gideon", "amanda", "david", "ranger", "scout", "micah", "taylor"]

for agent in AGENTS:
    context = {
        "agent": agent,
        "items": [
            {"name": f"{agent.title()} high priority task", "value": 500, "urgency": 9, "ease": 7, "impact": 8, "relationship": 6},
            {"name": f"{agent.title()} low priority task", "value": 50, "urgency": 2, "ease": 5, "impact": 2, "relationship": 2},
        ]
    }

    result = delegate_to_agent(f"Have {agent.title()} complete Kingdom work", context)

    assert result["status"] == "delegated", result
    assert result["delegated_to"].lower() == agent, result
    assert result["result"]["status"] == "success", result

    print(f"{agent.upper()}: PASS")

print("KINGDOM ALL AGENTS VERIFIED")
'''

TEST_FILE.write_text(fixed, encoding="utf-8")

result = subprocess.run(
    [sys.executable, str(TEST_FILE)],
    cwd=str(PROJECT_ROOT),
    capture_output=True,
    text=True
)

print(result.stdout)
print(result.stderr)

if result.returncode == 0:
    print("STATUS: KINGDOM VERIFIED")
else:
    print("STATUS: FAILED")
