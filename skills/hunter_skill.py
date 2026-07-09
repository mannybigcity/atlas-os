import json
from pathlib import Path

from skills.amanda_outreach_skill import amanda_add_outreach
from skills.hunter_pipeline_skill import (
    hunter_show_pipeline,
    hunter_add_to_pipeline,
    hunter_update_pipeline_stage,
    hunter_pipeline_report
)


HUNTER_DATA_PATH = Path("data") / "hunter_opportunities.json"
HUNTER_LEADS_PATH = Path("data") / "hunter_leads.json"


def load_json(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_hunter_data():
    return load_json(HUNTER_DATA_PATH)


def load_hunter_leads():
    return load_json(HUNTER_LEADS_PATH)


def hunter_report():
    data = load_hunter_data()

    if data is None:
        return hunter_missing_data_error()

    report = "🦅 HUNTER REVENUE REPORT\n\n"
    report += f"MISSION: {data.get('mission', 'Find money.')}\n\n"
    report += build_money_due_section(data)
    report += "\n"
    report += build_website_leads_section(data)
    report += "\n"
    report += build_commission_opportunities_section(data)
    report += "\n"
    report += build_hunter_recommendation(data)

    return report


def hunter_money_due():
    data = load_hunter_data()

    if data is None:
        return hunter_missing_data_error()

    report = "🦅 HUNTER MONEY DUE REPORT\n\n"
    report += build_money_due_section(data)
    report += "\n"
    report += build_hunter_recommendation(data)

    return report


def hunter_website_leads():
    data = load_hunter_data()

    if data is None:
        return hunter_missing_data_error()

    report = "🦅 HUNTER WEBSITE LEADS\n\n"
    report += build_website_leads_section(data)

    return report


def hunter_commission_opportunities():
    data = load_hunter_data()

    if data is None:
        return hunter_missing_data_error()

    report = "🦅 HUNTER COMMISSION OPPORTUNITIES\n\n"
    report += build_commission_opportunities_section(data)

    return report


def hunter_show_leads():
    data = load_hunter_leads()

    if data is None:
        return hunter_missing_leads_error()

    leads = data.get("leads", [])

    report = "🦅 HUNTER LEADS\n\n"
    report += f"SYSTEM: {data.get('system_name', 'Hunter Lead Database')}\n"
    report += f"MISSION: {data.get('mission', 'Track leads.')}\n\n"

    if not leads:
        report += "LEADS:\n- None\n"
        return report

    report += "LEADS:\n"

    for lead in leads:
        report += format_lead_line(lead)

    return report


def hunter_lead_report():
    data = load_hunter_leads()

    if data is None:
        return hunter_missing_leads_error()

    leads = data.get("leads", [])

    total_leads = len(leads)
    total_value = 0
    high_priority = 0
    needs_follow_up = 0
    contacted = 0
    proposal_sent = 0
    won = 0
    lost = 0
    sent_to_amanda = 0

    for lead in leads:
        total_value += float(lead.get("value", 0))

        priority = str(lead.get("priority", "")).lower()
        status = str(lead.get("status", "")).lower()

        if priority == "high":
            high_priority += 1

        if "follow" in status:
            needs_follow_up += 1

        if "contacted" in status:
            contacted += 1

        if "proposal" in status:
            proposal_sent += 1

        if "sent to amanda" in status:
            sent_to_amanda += 1

        if status == "won" or status == "closed won":
            won += 1

        if status == "lost" or status == "closed lost":
            lost += 1

    report = "🦅 HUNTER LEAD REPORT\n\n"
    report += f"Total Leads: {total_leads}\n"
    report += f"Potential Value: ${total_value:.2f}\n"
    report += f"High Priority Leads: {high_priority}\n"
    report += f"Needs Follow-Up: {needs_follow_up}\n"
    report += f"Sent To Amanda: {sent_to_amanda}\n"
    report += f"Contacted: {contacted}\n"
    report += f"Proposal Sent: {proposal_sent}\n"
    report += f"Won: {won}\n"
    report += f"Lost: {lost}\n\n"

    report += "HUNTER RECOMMENDATION:\n"

    if leads:
        top_lead = choose_top_lead(leads)
        report += (
            f"Focus first on {top_lead.get('name', 'Unknown Lead')}. "
            f"Current status: {top_lead.get('status', 'Unknown')}."
        )
    else:
        report += "No leads found. Add leads to Hunter."

    return report


def hunter_add_lead(name, lead_type="Local Business Prospect", value=0, priority="Medium", notes="No notes"):
    data = load_hunter_leads()

    if data is None:
        return hunter_missing_leads_error()

    clean_name = name.strip()

    if not clean_name:
        return (
            "🦅 HUNTER ERROR\n\n"
            "No lead name was provided."
        )

    leads = data.get("leads", [])

    for lead in leads:
        if lead.get("name", "").lower() == clean_name.lower():
            return (
                "🦅 HUNTER NOTICE\n\n"
                f"Lead already exists:\n{lead.get('name')}"
            )

    new_lead = {
        "name": clean_name,
        "type": lead_type,
        "status": "New",
        "value": value,
        "priority": priority,
        "notes": notes
    }

    leads.append(new_lead)
    data["leads"] = leads

    save_json(HUNTER_LEADS_PATH, data)

    return (
        "🦅 LEAD ADDED\n\n"
        f"Lead: {clean_name}\n"
        f"Type: {lead_type}\n"
        f"Status: New\n"
        f"Value: ${value}\n"
        f"Priority: {priority}\n\n"
        "Hunter Status:\n"
        "Lead added to the revenue board."
    )


def hunter_remove_lead(name):
    data = load_hunter_leads()

    if data is None:
        return hunter_missing_leads_error()

    clean_name = name.strip().lower()
    leads = data.get("leads", [])

    remaining_leads = []
    removed_lead = None

    for lead in leads:
        lead_name = lead.get("name", "").lower()

        if clean_name in lead_name or lead_name in clean_name:
            removed_lead = lead
        else:
            remaining_leads.append(lead)

    if removed_lead is None:
        return (
            "🦅 HUNTER ERROR\n\n"
            f"No lead found matching:\n{name}"
        )

    data["leads"] = remaining_leads
    save_json(HUNTER_LEADS_PATH, data)

    return (
        "🦅 LEAD REMOVED\n\n"
        f"Removed Lead: {removed_lead.get('name', 'Unknown Lead')}\n\n"
        "Hunter Status:\n"
        "Lead removed from the revenue board."
    )


def hunter_update_lead_status(name, new_status):
    data = load_hunter_leads()

    if data is None:
        return hunter_missing_leads_error()

    clean_name = name.strip().lower()
    clean_status = normalize_status(new_status)

    if not clean_name:
        return (
            "🦅 HUNTER ERROR\n\n"
            "No lead name was provided."
        )

    if not clean_status:
        return (
            "🦅 HUNTER ERROR\n\n"
            "No status was provided."
        )

    leads = data.get("leads", [])

    for lead in leads:
        lead_name = lead.get("name", "").lower()

        if clean_name in lead_name or lead_name in clean_name:
            old_status = lead.get("status", "Unknown")
            lead["status"] = clean_status

            save_json(HUNTER_LEADS_PATH, data)

            return (
                "🦅 LEAD STATUS UPDATED\n\n"
                f"Lead: {lead.get('name', 'Unknown Lead')}\n"
                f"Old Status: {old_status}\n"
                f"New Status: {clean_status}\n\n"
                "Hunter Status:\n"
                "Lead pipeline updated successfully."
            )

    return (
        "🦅 HUNTER ERROR\n\n"
        f"No lead found matching:\n{name}"
    )


def hunter_send_lead_to_amanda(name):
    data = load_hunter_leads()

    if data is None:
        return hunter_missing_leads_error()

    clean_name = name.strip().lower()
    leads = data.get("leads", [])

    for lead in leads:
        lead_name = lead.get("name", "").lower()

        if clean_name in lead_name or lead_name in clean_name:
            old_status = lead.get("status", "Unknown")
            lead["status"] = "Sent To Amanda"

            save_json(HUNTER_LEADS_PATH, data)

            amanda_response = amanda_add_outreach(
                lead.get("name", "Unknown Lead"),
                "Hunter",
                "Sent from Hunter lead board."
            )

            pipeline_response = hunter_add_to_pipeline(
                lead.get("name", "Unknown Lead"),
                lead.get("value", 0),
                "Sent To Amanda",
                "Lead sent from Hunter to Amanda."
            )

            return (
                "🦅 HUNTER → AMANDA HANDOFF\n\n"
                f"Lead: {lead.get('name', 'Unknown Lead')}\n"
                f"Value: ${lead.get('value', 0)}\n"
                f"Old Status: {old_status}\n"
                f"New Status: Sent To Amanda\n\n"
                "AMANDA RESPONSE:\n"
                f"{amanda_response}\n\n"
                "PIPELINE RESPONSE:\n"
                f"{pipeline_response}"
            )

    return (
        "🦅 HUNTER ERROR\n\n"
        f"No lead found matching:\n{name}"
    )


def normalize_status(status):
    cleaned = status.strip()
    cleaned = " ".join(cleaned.split())

    if not cleaned:
        return ""

    status_map = {
        "new": "New",
        "contacted": "Contacted",
        "followed up": "Followed Up",
        "follow up": "Follow-Up",
        "follow-up": "Follow-Up",
        "needs follow up": "Needs Follow-Up",
        "needs follow-up": "Needs Follow-Up",
        "quote needed": "Quote Needed",
        "quoted": "Quoted",
        "proposal sent": "Proposal Sent",
        "invoice sent": "Invoice Sent",
        "waiting payment": "Awaiting Payment",
        "awaiting payment": "Awaiting Payment",
        "sent to amanda": "Sent To Amanda",
        "negotiating": "Negotiating",
        "closed won": "Closed Won",
        "won": "Closed Won",
        "closed lost": "Closed Lost",
        "lost": "Closed Lost"
    }

    lowered = cleaned.lower()

    if lowered in status_map:
        return status_map[lowered]

    return " ".join(word.capitalize() for word in cleaned.split())


def choose_top_lead(leads):
    if not leads:
        return {}

    for lead in leads:
        if str(lead.get("priority", "")).lower() == "high":
            return lead

    return leads[0]


def format_lead_line(lead):
    return (
        f"- {lead.get('name', 'Unknown Lead')} | "
        f"{lead.get('type', 'Unknown Type')} | "
        f"{lead.get('status', 'Unknown Status')} | "
        f"Value: ${lead.get('value', 0)} | "
        f"Priority: {lead.get('priority', 'Unknown')}\n"
        f"  Notes: {lead.get('notes', 'No notes')}\n"
    )


def build_money_due_section(data):
    money_due = data.get("money_due_now", [])

    report = "MONEY DUE NOW:\n"

    if not money_due:
        report += "- None\n"
    else:
        for item in money_due:
            report += (
                f"- {item.get('name', 'Unknown')} | "
                f"${item.get('amount', 0)} | "
                f"{item.get('status', 'Unknown')}\n"
                f"  Notes: {item.get('notes', 'No notes')}\n"
            )

    return report


def build_website_leads_section(data):
    website_leads = data.get("website_leads", [])

    report = "WEBSITE LEADS:\n"

    if not website_leads:
        report += "- None\n"
    else:
        for lead in website_leads:
            report += (
                f"- {lead.get('business', 'Unknown Business')} | "
                f"{lead.get('status', 'Unknown')}\n"
                f"  Notes: {lead.get('notes', 'No notes')}\n"
            )

    return report


def build_commission_opportunities_section(data):
    commission_opportunities = data.get("commission_opportunities", [])

    report = "COMMISSION OPPORTUNITIES:\n"

    if not commission_opportunities:
        report += "- None\n"
    else:
        for opportunity in commission_opportunities:
            report += (
                f"- {opportunity.get('company', 'Unknown Company')} | "
                f"{opportunity.get('industry', 'Unknown Industry')} | "
                f"{opportunity.get('status', 'Unknown')}\n"
                f"  Notes: {opportunity.get('notes', 'No notes')}\n"
            )

    return report


def build_hunter_recommendation(data):
    money_due = data.get("money_due_now", [])
    website_leads = data.get("website_leads", [])
    commission_opportunities = data.get("commission_opportunities", [])

    report = "HUNTER RECOMMENDATION:\n"

    if money_due:
        top_money = money_due[0]
        report += (
            f"Follow up on {top_money.get('name', 'Unknown')} first. "
            "That is the closest money to the bank."
        )
    elif website_leads:
        top_lead = website_leads[0]
        report += (
            f"Contact {top_lead.get('business', 'Unknown Business')} first. "
            "Website work can create fast cashflow."
        )
    elif commission_opportunities:
        top_opportunity = commission_opportunities[0]
        report += (
            f"Research {top_opportunity.get('company', 'Unknown Company')} first. "
            "Commission opportunities can create recurring income."
        )
    else:
        report += "No active revenue opportunities found. Feed Hunter new leads."

    return report


def hunter_missing_data_error():
    return (
        "🦅 HUNTER ERROR\n\n"
        "I could not find Hunter's opportunity database.\n\n"
        "Expected file:\n"
        "data/hunter_opportunities.json"
    )


def hunter_missing_leads_error():
    return (
        "🦅 HUNTER ERROR\n\n"
        "I could not find Hunter's lead database.\n\n"
        "Expected file:\n"
        "data/hunter_leads.json"
    )


if __name__ == "__main__":
    print(hunter_show_leads())