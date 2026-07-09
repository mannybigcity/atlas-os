import json
from pathlib import Path

from skills.hunter_skill import hunter_add_lead


SCOUT_OPPORTUNITIES_PATH = Path("data") / "scout_opportunities.json"


def load_opportunities():
    if not SCOUT_OPPORTUNITIES_PATH.exists():
        return None

    with open(SCOUT_OPPORTUNITIES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_opportunities(data):
    with open(SCOUT_OPPORTUNITIES_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def scout_show_opportunities():
    data = load_opportunities()

    if data is None:
        return scout_missing_opportunities_error()

    opportunities = data.get("opportunities", [])

    report = "🦅 SCOUT OPPORTUNITIES\n\n"

    if not opportunities:
        report += "No opportunities found."
        return report

    for opp in opportunities:
        report += format_opportunity(opp)

    return report


def scout_add_opportunity(
    name,
    opportunity_type="Website",
    value=500
):
    data = load_opportunities()

    if data is None:
        return scout_missing_opportunities_error()

    clean_name = name.strip()

    if not clean_name:
        return (
            "🦅 SCOUT ERROR\n\n"
            "No opportunity name was provided."
        )

    opportunities = data.get("opportunities", [])

    for opp in opportunities:
        existing_name = opp.get("name", "").lower()

        if clean_name.lower() == existing_name:
            return (
                "🦅 SCOUT NOTICE\n\n"
                f"Opportunity already exists:\n{opp.get('name')}"
            )

    opportunities.append({
        "name": clean_name,
        "type": opportunity_type,
        "value": value,
        "status": "New"
    })

    data["opportunities"] = opportunities

    save_opportunities(data)

    return (
        "🦅 OPPORTUNITY ADDED\n\n"
        f"Name: {clean_name}\n"
        f"Type: {opportunity_type}\n"
        f"Value: ${value}"
    )


def scout_send_opportunity_to_hunter(name):
    data = load_opportunities()

    if data is None:
        return scout_missing_opportunities_error()

    clean_name = name.strip().lower()
    opportunities = data.get("opportunities", [])

    for opp in opportunities:
        opportunity_name = opp.get("name", "").lower()

        if clean_name in opportunity_name or opportunity_name in clean_name:
            opp["status"] = "Sent To Hunter"

            save_opportunities(data)

            hunter_response = hunter_add_lead(
                opp.get("name", "Unknown Opportunity"),
                "Website Opportunity",
                opp.get("value", 500),
                "High",
                "Sent from Scout opportunity board."
            )

            return (
                "🦅 SCOUT → HUNTER HANDOFF\n\n"
                f"Opportunity: {opp.get('name')}\n"
                f"Value: ${opp.get('value', 500)}\n"
                f"Scout Status: Sent To Hunter\n\n"
                "HUNTER RESPONSE:\n"
                f"{hunter_response}"
            )

    return (
        "🦅 SCOUT ERROR\n\n"
        f"No opportunity found matching:\n{name}"
    )


def format_opportunity(opp):
    return (
        f"- {opp.get('name', 'Unknown Opportunity')}\n"
        f"  Type: {opp.get('type', 'Unknown')}\n"
        f"  Value: ${opp.get('value', 0)}\n"
        f"  Status: {opp.get('status', 'Unknown')}\n\n"
    )


def scout_missing_opportunities_error():
    return (
        "🦅 SCOUT ERROR\n\n"
        "I could not find Scout's opportunity database.\n\n"
        "Expected file:\n"
        "data/scout_opportunities.json"
    )


if __name__ == "__main__":
    print(scout_show_opportunities())