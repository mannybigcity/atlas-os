import json
from pathlib import Path

from agents.assistant import ask_puter


HUNTER_LEADS_PATH = Path("data") / "hunter_leads.json"
SCOUT_OPPORTUNITIES_PATH = Path("data") / "scout_opportunities.json"
AMANDA_OUTREACH_PATH = Path("data") / "amanda_outreach.json"
PROJECT_STATUS_PATH = Path("data") / "project_statuses.json"


def load_json(path):
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_kingdom_summary():
    hunter_data = load_json(HUNTER_LEADS_PATH)
    scout_data = load_json(SCOUT_OPPORTUNITIES_PATH)
    amanda_data = load_json(AMANDA_OUTREACH_PATH)
    project_data = load_json(PROJECT_STATUS_PATH)

    hunter_leads = hunter_data.get("leads", [])
    scout_opportunities = scout_data.get("opportunities", [])
    outreach_queue = amanda_data.get("outreach_queue", [])
    projects = project_data.get("projects", [])

    pending_outreach = [
        item for item in outreach_queue
        if item.get("status") == "Pending Contact"
    ]

    building_projects = [
        project for project in projects
        if project.get("status", "").lower() == "building"
    ]

    completed_projects = [
        project for project in projects
        if project.get("status", "").lower() == "complete"
    ]

    total_pipeline_value = 0

    for lead in hunter_leads:
        try:
            total_pipeline_value += float(lead.get("value", 0))
        except:
            pass

    summary = f"""
RAMFAM KINGDOM STATUS

SCOUT OPPORTUNITIES:
{len(scout_opportunities)}

HUNTER LEADS:
{len(hunter_leads)}

AMANDA OUTREACH:
{len(outreach_queue)}

PENDING OUTREACH:
{len(pending_outreach)}

ACTIVE PROJECTS:
{len(building_projects)}

COMPLETED PROJECTS:
{len(completed_projects)}

PIPELINE VALUE:
${total_pipeline_value:,.2f}
"""

    return summary


def mason_inspect_kingdom_ai():
    kingdom_summary = build_kingdom_summary()

    prompt = f"""
You are Mason, Chief Architect of the RAMFAM Kingdom.

Analyze the Kingdom data below.

Provide:

1. Current Kingdom Status
2. Biggest Bottleneck
3. Revenue Recommendation
4. Development Recommendation
5. Next Best Action

Keep answers concise and actionable.

{kingdom_summary}
"""

    history = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    return ask_puter(history)


def mason_revenue_strategy_ai():
    kingdom_summary = build_kingdom_summary()

    prompt = f"""
You are Mason, Chief Architect.

Your mission is to maximize revenue.

Analyze the Kingdom data below.

Answer:

1. Fastest path to cash
2. Highest priority lead action
3. Biggest revenue risk
4. Recommended mission for Hunter
5. Recommended mission for Amanda

{kingdom_summary}
"""

    history = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    return ask_puter(history)


def mason_next_project_ai():
    kingdom_summary = build_kingdom_summary()

    prompt = f"""
You are Mason, Kingdom Architect.

Analyze the Kingdom.

Recommend the single highest-impact project to build next.

Explain:

- Why
- Revenue impact
- Difficulty
- Priority

{kingdom_summary}
"""

    history = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    return ask_puter(history)


if __name__ == "__main__":
    print(mason_inspect_kingdom_ai())