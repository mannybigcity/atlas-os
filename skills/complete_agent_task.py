# skills/complete_agent_task.py — Complete Agent City tasks

import json
import os
from datetime import datetime

AGENTS_FILE = "memory/memory/agents.json"


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


def complete_agent_task(agent_name):
    agents = load_agents()

    if not agents:
        return "🦇 Alfred could not find any agents in Agent City."

    found_agent = None

    for agent in agents:
        if agent.get("name", "").lower() == agent_name.lower():
            found_agent = agent
            break

    if not found_agent:
        available_agents = ", ".join(agent.get("name", "Unknown") for agent in agents)
        return f"🦇 Alfred could not find agent '{agent_name}'. Available agents: {available_agents}"

    current_status = found_agent.get("status", "").lower().strip()
    current_task = found_agent.get("current_task", "").lower().strip()

    if current_status in ["standby", "idle"] or current_task in [
        "waiting for assignment",
        "no task assigned",
        ""
    ]:
        return (
            f"🦇 {found_agent.get('name')} is already on standby and has no active task.\n\n"
            f"Status: {found_agent.get('status')}\n"
            f"Current Task: {found_agent.get('current_task')}"
        )

    completed_task = found_agent.get("current_task", "No task recorded")
    completed_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    found_agent["status"] = "Standby"
    found_agent["current_task"] = "Waiting for assignment"
    found_agent["last_report"] = f"Completed task on {completed_time}: {completed_task}"

    save_agents(agents)

    return (
        f"🦇 Task completed for {found_agent.get('name')}.\n\n"
        f"Completed Task: {completed_task}\n"
        f"New Status: {found_agent.get('status')}\n"
        f"Current Task: {found_agent.get('current_task')}\n"
        f"Last Report: {found_agent.get('last_report')}"
    )


if __name__ == "__main__":
    print(complete_agent_task("Micah"))