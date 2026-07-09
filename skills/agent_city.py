# skills/agent_city.py

from skills.agent_registry import load_agents


def show_agent_city():

    agents = load_agents()

    report = "🏙️ AGENT CITY\n\n"

    room_icons = {
        "Finance Room": "🏦",
        "Media Room": "📣",
        "Sales Room": "📋",
        "Marketplace Room": "🛒",
        "Command Center": "🦇",
    }

    for agent in agents:

        room = agent.get("location", agent.get("room", "Unknown Room"))
        icon = room_icons.get(room, "🏢")

        status = agent.get("status", "Unknown")
        name = agent.get("name", "Unknown")
        task = agent.get("current_task", "No task assigned")

        if status.lower() == "working":
            status_icon = "🟢"
        elif status.lower() == "active":
            status_icon = "🦇"
        else:
            status_icon = "⚪"

        report += f"{icon} {room}\n"
        report += f"{status_icon} {name}\n"
        report += f"{task}\n\n"

    report += "CAVE STATUS: GREEN"

    return report


if __name__ == "__main__":
    print(show_agent_city())