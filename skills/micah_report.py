# skills/micah_report.py

from skills.agent_registry import load_agents


def micah_report():

    agents = load_agents()

    micah = None

    for agent in agents:
        if agent.get("name", "").lower() == "micah":
            micah = agent
            break

    if not micah:
        return "🦇 Alfred could not find Micah."

    report = "🦇 MICAH REPORT\n\n"

    report += f"Current Status: {micah.get('status')}\n"
    report += f"Current Task: {micah.get('current_task')}\n\n"

    report += "SUGGESTED FACEBOOK POST\n\n"

    report += (
        "Another order headed out the door.\n\n"
        "At FRESH Apparel & Design, every shirt, hat, and custom item "
        "helps support our mission of Faithfully Reaching Everyone Seeking Hope.\n\n"
        "Need shirts, hats, patches, signs, or custom promotional items?\n"
        "Send me a message and let's build something together.\n\n"
        "#FRESH #CustomApparel #SmallBusiness #FaithInAction"
    )

    return report


if __name__ == "__main__":
    print(micah_report())