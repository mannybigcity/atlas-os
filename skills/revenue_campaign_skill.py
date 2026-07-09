import json
from pathlib import Path


CAMPAIGN_PATH = Path("data") / "revenue_campaign.json"


def launch_revenue_campaign():
    if not CAMPAIGN_PATH.exists():
        return (
            "🦫 MASON ERROR\n\n"
            "Revenue campaign file not found."
        )

    with open(CAMPAIGN_PATH, "r", encoding="utf-8") as file:
        campaign = json.load(file)

    report = "🦫 REVENUE WAR ROOM\n\n"

    report += f"CAMPAIGN: {campaign.get('campaign_name')}\n"
    report += f"REVENUE GOAL: ${campaign.get('revenue_goal')}\n"
    report += f"STATUS: {campaign.get('status')}\n\n"

    hunter = campaign.get("hunter_mission", {})
    report += "🦅 HUNTER MISSION\n"
    report += f"Goal: {hunter.get('goal')} Prospects\n"
    report += "Targets:\n"

    for item in hunter.get("target_types", []):
        report += f"- {item}\n"

    report += "\n"

    amanda = campaign.get("amanda_mission", {})
    report += "🐼 AMANDA MISSION\n"
    report += f"Goal: {amanda.get('goal')} Opportunities\n"
    report += "Targets:\n"

    for item in amanda.get("target_types", []):
        report += f"- {item}\n"

    report += "\n"

    micah = campaign.get("micah_mission", {})
    report += "🦊 MICAH MISSION\n"
    report += f"Goal: {micah.get('goal')} Pieces Of Content\n"
    report += "Content:\n"

    for item in micah.get("content_types", []):
        report += f"- {item}\n"

    report += "\nKINGDOM OBJECTIVE:\n"
    report += "Generate revenue before building new systems."

    return report