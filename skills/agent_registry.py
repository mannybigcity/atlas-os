# skills/agent_registry.py — RAMFAM KINGDOM Agent Registry

import json
import os

AGENTS_FILE = "memory/memory/agents.json"


DEFAULT_AGENTS = []


def ensure_agents_file():
    os.makedirs(os.path.dirname(AGENTS_FILE), exist_ok=True)

    if not os.path.exists(AGENTS_FILE):
        with open(AGENTS_FILE, "w", encoding="utf-8") as file:
            json.dump(DEFAULT_AGENTS, file, indent=4)


def load_agents():
    ensure_agents_file()

    try:
        with open(AGENTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_agents(agents):
    ensure_agents_file()

    with open(AGENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(agents, file, indent=4)


def show_agents():
    agents = load_agents()

    if not agents:
        return "No RAMFAM KINGDOM agents registered."

    report = "🦁 RAMFAM KINGDOM AGENT REGISTRY\n\n"

    for agent in agents:
        room = agent.get("room") or agent.get("location") or "Unassigned"
        mascot = agent.get("mascot", "No mascot assigned")
        approval_required = agent.get("approval_required", True)

        report += (
            f"Name: {agent.get('name', 'Unknown')}\n"
            f"Role: {agent.get('role', 'Unknown')}\n"
            f"Mascot: {mascot}\n"
            f"Status: {agent.get('status', 'Unknown')}\n"
            f"Room: {room}\n"
            f"Current Task: {agent.get('current_task', 'No task assigned')}\n"
            f"Approval Required: {approval_required}\n"
            f"Last Report: {agent.get('last_report', 'No report yet')}\n\n"
        )

    return report


if __name__ == "__main__":
    print(show_agents())