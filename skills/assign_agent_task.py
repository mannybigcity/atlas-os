# skills/assign_agent_task.py — Assign missions to RAMFAM KINGDOM agents

import json
import os
from datetime import datetime

AGENTS_FILE = "memory/memory/agents.json"

BLOCKED_AGENT_WORDS = {
    "you", "your", "yourself", "me", "my", "myself",
    "him", "her", "them", "it", "atlas"
}


def load_agents():
    if not os.path.exists(AGENTS_FILE):
        return []

    try:
        with open(AGENTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_agents(agents):
    os.makedirs(os.path.dirname(AGENTS_FILE), exist_ok=True)

    with open(AGENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(agents, file, indent=4)


def assign_agent_task(agent_name, task):
    agent_name = agent_name.strip()

    if agent_name.lower() in BLOCKED_AGENT_WORDS:
        return (
            "🦁 I heard that as a conversation request, not an agent assignment.\n\n"
            "If you want me to assign work, say something like:\n"
            "'Assign Mason to fix the voice speed.'"
        )

    agents = load_agents()

    if not agents:
        return "🦁 ATLAS could not find any agents in the Kingdom Registry."

    found_agent = None

    for agent in agents:
        if agent.get("name", "").lower() == agent_name.lower():
            found_agent = agent
            break

    if not found_agent:
        available_agents = ", ".join(agent.get("name", "Unknown") for agent in agents)
        return f"🦁 ATLAS could not find agent '{agent_name}'. Available agents: {available_agents}"

    assigned_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    found_agent["status"] = "Working"
    found_agent["current_task"] = task
    found_agent["last_report"] = f"Mission assigned by Manny on {assigned_time}."

    save_agents(agents)

    return (
        f"🦁 Mission assigned to {found_agent.get('name')}.\n\n"
        f"Role: {found_agent.get('role', 'Unknown Role')}\n"
        f"Room: {found_agent.get('location', found_agent.get('room', 'Unknown Room'))}\n"
        f"Status: {found_agent.get('status')}\n"
        f"Current Task: {found_agent.get('current_task')}\n"
        f"Last Report: {found_agent.get('last_report')}"
    )


if __name__ == "__main__":
    print(assign_agent_task("Gideon", "Follow up with Kandy about the Canes Baseball Team Shirts payment"))