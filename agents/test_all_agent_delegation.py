from pathlib import Path
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
