import json
import os

MISSIONS_FILE = "missions/missions.json"

def load_missions():
    if not os.path.exists(MISSIONS_FILE):
        return []

    with open(MISSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_missions(missions):
    with open(MISSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(missions, f, indent=2)

def add_mission(title, category, priority):
    missions = load_missions()

    new_mission = {
        "title": title,
        "category": category,
        "priority": priority,
        "status": "Open"
    }

    missions.append(new_mission)
    save_missions(missions)

    return f"Mission added: {title} | {category} | Priority: {priority}"

def show_missions():
    missions = load_missions()

    if not missions:
        return "No missions found."

    lines = []

    for mission in missions:
        lines.append(
            f"{mission['title']} | {mission['category']} | Priority: {mission['priority']} | Status: {mission['status']}"
        )

    return "\n".join(lines)

def complete_mission(title):
    missions = load_missions()

    for mission in missions:
        if mission["title"].lower() == title.lower():
            mission["status"] = "Complete"
            save_missions(missions)
            return f"Mission complete: {title}"

    return f"No mission found named: {title}"