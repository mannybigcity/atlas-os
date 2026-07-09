import os
import json


def check_file(path):
    if os.path.exists(path):
        return f"✅ {path} exists"
    return f"❌ {path} is missing"


def check_json_file(path):
    if not os.path.exists(path):
        return f"❌ {path} is missing"

    try:
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
        return f"✅ {path} is valid JSON"
    except Exception as e:
        return f"⚠️ {path} has a JSON problem: {e}"


def show_missions():
    path = "agents/missions.json"

    if not os.path.exists(path):
        return "No active missions found yet."

    try:
        with open(path, "r", encoding="utf-8") as f:
            missions = json.load(f)
    except Exception as e:
        return f"⚠️ Could not read missions: {e}"

    if not missions:
        return "No active missions found yet."

    active_missions = [
        mission for mission in missions
        if mission.get("status", "").lower() != "complete"
    ]

    if not active_missions:
        return "No active missions found. All missions are complete."

    report = "ACTIVE MISSIONS\n\n"

    for mission in active_missions:
        report += f"🔥 {mission.get('agent', 'Unknown Agent')}\n"
        report += f"Role: {mission.get('role', 'No role listed')}\n"
        report += f"Room: {mission.get('room', 'No room listed')}\n"
        report += f"Priority: {mission.get('priority', 'Normal')}\n"
        report += f"Status: {mission.get('status', 'Unknown')}\n"
        report += f"Mission: {mission.get('mission', 'No mission listed')}\n"
        report += f"Task: {mission.get('task', 'No task listed')}\n"
        report += f"Goal: {mission.get('goal', 'No goal listed')}\n\n"

    return report


def run_diagnostics():
    checks = []

    checks.append(check_file("app.py"))
    checks.append(check_file("agents/assistant.py"))

    checks.append(check_file("skills/sales_coach_skill.py"))
    checks.append(check_file("skills/quote_skill.py"))
    checks.append(check_file("skills/alfred_skill.py"))

    checks.append(check_file("agents/sales_agent.py"))
    checks.append(check_file("agents/crm_agent.py"))
    checks.append(check_file("agents/content_agent.py"))
    checks.append(check_file("agents/operations_agent.py"))

    checks.append(check_file("crm/crm_skill.py"))
    checks.append(check_file("crm/update_prospect.py"))
    checks.append(check_file("crm/filter_prospects.py"))
    checks.append(check_file("crm/followups.py"))

    checks.append(check_file("orders/order_skill.py"))
    checks.append(check_file("orders/update_order.py"))

    checks.append(check_json_file("crm/prospects.json"))
    checks.append(check_json_file("orders/orders.json"))
    checks.append(check_json_file("memory/memory.json"))
    checks.append(check_json_file("agents/missions.json"))

    report = "ALFRED CAVE DIAGNOSTIC REPORT\n\n"
    report += "\n".join(checks)

    return report