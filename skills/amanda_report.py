# skills/amanda_report.py

from skills.agent_registry import load_agents


def amanda_report():
    agents = load_agents()

    amanda = None

    for agent in agents:
        if agent.get("name", "").lower() == "amanda":
            amanda = agent
            break

    if not amanda:
        return "🦇 Alfred could not find Amanda."

    report = "🦇 AMANDA REPORT\n\n"

    report += f"Current Status: {amanda.get('status')}\n"
    report += f"Current Task: {amanda.get('current_task')}\n\n"

    report += "ETSY OPPORTUNITIES\n\n"

    report += (
        "1. Custom Leather Patch Hats\n"
        "   - Business logos\n"
        "   - Construction companies\n"
        "   - Hunting clubs\n\n"
    )

    report += (
        "2. Custom Baseball Team Shirts\n"
        "   - Team names\n"
        "   - Coach gifts\n"
        "   - End-of-season shirts\n\n"
    )

    report += (
        "3. Christian Apparel\n"
        "   - FRESH collection\n"
        "   - Faith-based shirts\n"
        "   - Church fundraiser apparel\n\n"
    )

    report += (
        "4. Personalized Gifts\n"
        "   - Laser engraved signs\n"
        "   - Family name plaques\n"
        "   - Father's Day gifts\n\n"
    )

    report += "RECOMMENDED MARKETPLACE ACTION\n\n"
    report += (
        "Create one new Etsy listing this week focused on "
        "custom leather patch hats for local businesses."
    )

    return report


if __name__ == "__main__":
    print(amanda_report())