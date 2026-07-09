import json
from pathlib import Path


PROJECT_STATUS_PATH = Path("data") / "project_statuses.json"
HUNTER_LEADS_PATH = Path("data") / "hunter_leads.json"
SCOUT_OPPORTUNITIES_PATH = Path("data") / "scout_opportunities.json"
AMANDA_OUTREACH_PATH = Path("data") / "amanda_outreach.json"


def load_json(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def mason_recommend_next_project():
    projects = load_json(PROJECT_STATUS_PATH)

    if projects is None:
        return "🦫 MASON ERROR\n\nProject status database not found."

    report = "🦫 MASON PROJECT RECOMMENDATION\n\n"

    report += "Recommended Next Project:\n"
    report += "Mason v7 - Recommendation Engine\n\n"

    report += "Reason:\n"
    report += (
        "Mason needs the ability to analyze the Kingdom and recommend "
        "the next highest-impact action instead of only tracking projects.\n\n"
    )

    report += "Priority:\n"
    report += "High\n\n"

    report += "Kingdom Impact:\n"
    report += "This moves Mason from project manager toward architect brain."

    return report


def mason_recommend_revenue_action():
    hunter_data = load_json(HUNTER_LEADS_PATH)
    scout_data = load_json(SCOUT_OPPORTUNITIES_PATH)
    amanda_data = load_json(AMANDA_OUTREACH_PATH)

    if hunter_data is None:
        return "🦫 MASON ERROR\n\nHunter leads database not found."

    if scout_data is None:
        return "🦫 MASON ERROR\n\nScout opportunities database not found."

    if amanda_data is None:
        return "🦫 MASON ERROR\n\nAmanda outreach database not found."

    hunter_leads = hunter_data.get("leads", [])
    scout_opportunities = scout_data.get("opportunities", [])
    outreach_queue = amanda_data.get("outreach_queue", [])

    pending_outreach = [
        item for item in outreach_queue
        if item.get("status") == "Pending Contact"
    ]

    high_value_leads = [
        lead for lead in hunter_leads
        if float(lead.get("value", 0)) >= 500
    ]

    unsent_opportunities = [
        opportunity for opportunity in scout_opportunities
        if opportunity.get("status") != "Sent To Hunter"
    ]

    report = "🦫 MASON REVENUE RECOMMENDATION\n\n"

    report += "PIPELINE STATUS:\n"
    report += f"Scout Opportunities: {len(scout_opportunities)}\n"
    report += f"Hunter Leads: {len(hunter_leads)}\n"
    report += f"Amanda Outreach Queue: {len(outreach_queue)}\n"
    report += f"Pending Outreach: {len(pending_outreach)}\n"
    report += f"High Value Leads: {len(high_value_leads)}\n\n"

    if pending_outreach:
        first_pending = pending_outreach[0]
        report += "RECOMMENDED ACTION:\n"
        report += (
            f"Have Amanda contact {first_pending.get('business_name')} first.\n\n"
        )
        report += "Reason:\n"
        report += "The lead has already moved through Scout and Hunter. Outreach is the current bottleneck."
        return report

    if high_value_leads:
        first_lead = high_value_leads[0]
        report += "RECOMMENDED ACTION:\n"
        report += (
            f"Send {first_lead.get('name')} to Amanda for outreach.\n\n"
        )
        report += "Reason:\n"
        report += "Hunter has a high-value lead that has not been worked yet."
        return report

    if unsent_opportunities:
        first_opportunity = unsent_opportunities[0]
        report += "RECOMMENDED ACTION:\n"
        report += (
            f"Send {first_opportunity.get('name')} from Scout to Hunter.\n\n"
        )
        report += "Reason:\n"
        report += "Scout has opportunities that have not entered the revenue pipeline."
        return report

    report += "RECOMMENDED ACTION:\n"
    report += "Have Scout find more website opportunities.\n\n"
    report += "Reason:\n"
    report += "The current pipeline needs more fresh opportunities."

    return report


def mason_find_bottleneck():
    hunter_data = load_json(HUNTER_LEADS_PATH)
    scout_data = load_json(SCOUT_OPPORTUNITIES_PATH)
    amanda_data = load_json(AMANDA_OUTREACH_PATH)

    if hunter_data is None or scout_data is None or amanda_data is None:
        return (
            "🦫 MASON ERROR\n\n"
            "One or more revenue pipeline databases are missing."
        )

    hunter_leads = hunter_data.get("leads", [])
    scout_opportunities = scout_data.get("opportunities", [])
    outreach_queue = amanda_data.get("outreach_queue", [])

    pending_outreach = [
        item for item in outreach_queue
        if item.get("status") == "Pending Contact"
    ]

    sent_to_amanda = [
        lead for lead in hunter_leads
        if lead.get("status") == "Sent To Amanda"
    ]

    unsent_opportunities = [
        opportunity for opportunity in scout_opportunities
        if opportunity.get("status") != "Sent To Hunter"
    ]

    report = "🦫 MASON BOTTLENECK REPORT\n\n"

    if pending_outreach:
        report += "BOTTLENECK:\n"
        report += "Amanda outreach is waiting.\n\n"
        report += "Action:\n"
        report += "Contact pending outreach opportunities."
        return report

    if sent_to_amanda and not pending_outreach:
        report += "BOTTLENECK:\n"
        report += "Hunter sent leads to Amanda, but outreach queue may need verification.\n\n"
        report += "Action:\n"
        report += "Inspect Amanda outreach queue."
        return report

    if unsent_opportunities:
        report += "BOTTLENECK:\n"
        report += "Scout has opportunities that have not been sent to Hunter.\n\n"
        report += "Action:\n"
        report += "Send Scout opportunities to Hunter."
        return report

    if not scout_opportunities:
        report += "BOTTLENECK:\n"
        report += "Scout has no opportunities.\n\n"
        report += "Action:\n"
        report += "Begin prospect hunting."
        return report

    report += "BOTTLENECK:\n"
    report += "No major bottleneck detected.\n\n"
    report += "Action:\n"
    report += "Increase lead volume."

    return report


if __name__ == "__main__":
    print(mason_recommend_revenue_action())