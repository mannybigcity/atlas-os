# skills/available_agents.py

import json
import os

AGENTS_FILE = "memory/memory/agents.json"


def load_agents():
    if not os.path.exists(AGENTS_FILE):
        return []

    with open(AGENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def show_available_agents():
    agents = load_agents()

    available = [
        agent for agent in agents
        if agent.get("status", "").lower() in ["active", "working", "standby"]
    ]

    if not available:
        return "🦁 No RAMFAM KINGDOM agents available."

    report = "🦁 AVAILABLE RAMFAM KINGDOM AGENTS\n\n"

    for agent in available:
        report += (
            f"{agent.get('name')} | "
            f"{agent.get('role')} | "
            f"{agent.get('room', 'Unassigned')}\n"
        )

    report += f"\nAvailable Agents: {len(available)}"

    return report


if __name__ == "__main__":
    print(show_available_agents())