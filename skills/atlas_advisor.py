import json
from pathlib import Path
from skills.mason_advisor import mason_advisor

PUTER_ROOT = Path(__file__).resolve().parents[1]

AGENTS_FILE = PUTER_ROOT / "memory" / "memory" / "agents.json"
REVENUE_FILE = PUTER_ROOT / "revenue" / "revenue.json"


def load_agents():
    if not AGENTS_FILE.exists():
        return []

    with open(AGENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_revenue():
    if not REVENUE_FILE.exists():
        return []

    with open(REVENUE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def atlas_advisor():

    agents = load_agents()
    revenue = load_revenue()

    active_agents = len(
        [a for a in agents if a.get("status", "").lower() == "active"]
    )

    paid_items = len(
        [r for r in revenue if r.get("status", "").lower() == "paid"]
    )

    outstanding_items = len(
        [r for r in revenue if r.get("status", "").lower() == "outstanding"]
    )

    mason_analysis = mason_advisor()

    return f"""
🦁 ATLAS EXECUTIVE ADVISOR

KINGDOM STATUS

Active Agents: {active_agents}

Paid Revenue Items: {paid_items}

Outstanding Revenue Items: {outstanding_items}

==============================

MASON'S ANALYSIS

{mason_analysis}

==============================

ATLAS EXECUTIVE SUMMARY

Atlas recommends following Mason's highest-value recommendation.

Kingdom Law Reminder:

Revenue Before Expansion.

Protect Manny's focus.

One visible win at a time.
"""


if __name__ == "__main__":
    print(atlas_advisor())