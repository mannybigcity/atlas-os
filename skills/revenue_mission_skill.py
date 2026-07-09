import json
from pathlib import Path

MISSION_PATH = Path("data") / "revenue_missions.json"


def show_revenue_missions():
    if not MISSION_PATH.exists():
        return (
            "🦫 MASON ERROR\n\n"
            "Revenue mission file not found."
        )

    with open(MISSION_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    report = "🦫 REVENUE MISSIONS\n\n"

    report += f"MISSION BOARD: {data.get('mission_name')}\n"
    report += f"STATUS: {data.get('status')}\n\n"

    for mission in data.get("missions", []):
        report += (
            f"{mission.get('agent')}:\n"
            f"- {mission.get('title')}\n"
            f"- Status: {mission.get('status')}\n\n"
        )

    return report