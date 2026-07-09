# skills/priority_report.py — Alfred's real next-action priority report

from revenue.revenue_skill import load_revenue, categorize_revenue_status
from skills.agent_registry import load_agents
from crm.crm_skill import load_prospects


def alfred_priority_report():
    revenue_items = load_revenue()
    agents = load_agents()
    prospects = load_prospects()

    report = "🦇 ALFRED'S PRIORITY REPORT\n\n"

    outstanding_items = []
    potential_items = []
    paid_items = []

    for item in revenue_items:
        status = item.get("status", "")
        category = categorize_revenue_status(status)

        if category == "outstanding":
            outstanding_items.append(item)
        elif category == "paid":
            paid_items.append(item)
        else:
            potential_items.append(item)

    outstanding_total = sum(float(item.get("amount", 0)) for item in outstanding_items)
    potential_total = sum(float(item.get("amount", 0)) for item in potential_items)

    report += "PRIORITY 1 — COLLECT MONEY\n"

    if outstanding_items:
        report += f"Outstanding Revenue: ${outstanding_total:.2f}\n"
        for item in outstanding_items:
            report += (
                f"- {item.get('customer', 'Unknown')} | "
                f"{item.get('source', 'Unknown Source')} | "
                f"${float(item.get('amount', 0)):.2f} | "
                f"{item.get('status', 'Unknown')}\n"
            )
    else:
        report += "No outstanding revenue found.\n"

    report += "\nPRIORITY 2 — FOLLOW UPS\n"

    followups = [
        prospect for prospect in prospects
        if prospect.get("follow_up")
    ]

    if followups:
        for prospect in followups:
            report += (
                f"- {prospect.get('name', 'Unknown')} | "
                f"{prospect.get('business', 'Unknown Business')} | "
                f"{prospect.get('product', 'Unknown Product')} | "
                f"Status: {prospect.get('status', 'Unknown')} | "
                f"Follow up: {prospect.get('follow_up')}\n"
            )
    else:
        report += "No follow-ups scheduled.\n"

    report += "\nPRIORITY 3 — ACTIVE AGENTS\n"

    active_agents = [
        agent for agent in agents
        if agent.get("status", "").lower() in ["active", "working"]
    ]

    if active_agents:
        for agent in active_agents:
            report += (
                f"- {agent.get('name', 'Unknown')} | "
                f"{agent.get('role', 'Unknown Role')} | "
                f"Status: {agent.get('status', 'Unknown')} | "
                f"Task: {agent.get('current_task', 'No task assigned')}\n"
            )
    else:
        report += "No active agents found.\n"

    report += "\nPRIORITY 4 — AVAILABLE AGENTS\n"

    standby_agents = [
        agent for agent in agents
        if agent.get("status", "").lower() in ["standby", "idle"]
    ]

    if standby_agents:
        for agent in standby_agents:
            report += (
                f"- {agent.get('name', 'Unknown')} | "
                f"{agent.get('role', 'Unknown Role')} | "
                f"Room: {agent.get('location', agent.get('room', 'Unknown Room'))}\n"
            )
    else:
        report += "No standby agents available.\n"

    report += "\nRECOMMENDED NEXT MOVE\n"

    if outstanding_items:
        top_item = max(outstanding_items, key=lambda item: float(item.get("amount", 0)))
        report += (
            f"Follow up with {top_item.get('customer', 'the customer')} "
            f"about {top_item.get('source', 'the outstanding payment')} "
            f"for ${float(top_item.get('amount', 0)):.2f}."
        )
    elif followups:
        top_followup = followups[0]
        report += (
            f"Follow up with {top_followup.get('name', 'the prospect')} "
            f"about {top_followup.get('product', 'their project')}."
        )
    elif potential_items:
        top_potential = max(potential_items, key=lambda item: float(item.get("amount", 0)))
        report += (
            f"Work the potential opportunity with {top_potential.get('customer', 'the customer')} "
            f"for {top_potential.get('source', 'the project')}."
        )
    else:
        report += "No urgent money task found. Assign Micah or Amanda to create new sales activity."

    return report


if __name__ == "__main__":
    print(alfred_priority_report())