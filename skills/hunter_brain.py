import json
from pathlib import Path

from agents.assistant import ask_puter


HUNTER_LEADS_PATH = Path("data") / "hunter_leads.json"
HUNTER_PIPELINE_PATH = Path("data") / "hunter_pipeline.json"
SCOUT_TARGETS_PATH = Path("data") / "scout_targets.json"
SCOUT_OPPORTUNITIES_PATH = Path("data") / "scout_opportunities.json"


def load_json(path):
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_hunter_summary():
    leads_data = load_json(HUNTER_LEADS_PATH)
    pipeline_data = load_json(HUNTER_PIPELINE_PATH)
    targets_data = load_json(SCOUT_TARGETS_PATH)
    opportunities_data = load_json(SCOUT_OPPORTUNITIES_PATH)

    leads = leads_data.get("leads", [])
    pipeline = pipeline_data.get("pipeline", [])
    targets = targets_data.get("targets", [])
    opportunities = opportunities_data.get("opportunities", [])

    total_lead_value = 0

    for lead in leads:
        try:
            total_lead_value += float(lead.get("value", 0))
        except:
            pass

    pipeline_stages = {}

    for item in pipeline:
        stage = item.get("stage", "Unknown")
        pipeline_stages[stage] = pipeline_stages.get(stage, 0) + 1

    summary = f"""
HUNTER REVENUE SYSTEM

TOTAL LEADS:
{len(leads)}

TOTAL PIPELINE RECORDS:
{len(pipeline)}

SCOUT TARGETS:
{len(targets)}

SCOUT OPPORTUNITIES:
{len(opportunities)}

PIPELINE VALUE:
${total_lead_value:,.2f}

PIPELINE STAGES:
{pipeline_stages}
"""

    return summary


def hunter_where_is_the_money_ai():
    summary = build_hunter_summary()

    prompt = f"""
You are Hunter Skyborne.

You are the Revenue Commander of the RAMFAM Kingdom.

Analyze the information below.

Answer:

1. Where is the money?
2. Closest money to the bank
3. Highest value opportunity
4. Fastest action to create revenue
5. Recommended next move

Keep answers concise and focused on revenue.

{summary}
"""

    history = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    return ask_puter(history)


def hunter_rank_opportunities_ai():
    summary = build_hunter_summary()

    prompt = f"""
You are Hunter Skyborne.

Rank the current opportunities by revenue potential.

Provide:

1. Highest Priority
2. Medium Priority
3. Low Priority

Explain why.

{summary}
"""

    history = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    return ask_puter(history)


def hunter_fastest_path_to_cash_ai():
    summary = build_hunter_summary()

    prompt = f"""
You are Hunter Skyborne.

Your mission is to generate revenue quickly.

Analyze the current revenue system.

Provide:

1. Fastest path to $500
2. Fastest path to $1,000
3. Biggest revenue bottleneck
4. Immediate action required

{summary}
"""

    history = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    return ask_puter(history)


if __name__ == "__main__":
    print(hunter_where_is_the_money_ai())