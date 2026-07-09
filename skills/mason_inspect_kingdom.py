import json
from pathlib import Path
from skills.mason_chat import mason_chat

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


def mason_inspect_kingdom():

    agents = load_agents()
    revenue = load_revenue()

    active_agents = len(
        [a for a in agents if a.get("status", "").lower() == "active"]
    )

    paid_orders = len(
        [r for r in revenue if r.get("status", "").lower() == "paid"]
    )

    outstanding_orders = len(
        [r for r in revenue if r.get("status", "").lower() == "outstanding"]
    )

    report = f"""
Kingdom Status Report

Active Agents: {active_agents}

Paid Revenue Items: {paid_orders}

Outstanding Revenue Items: {outstanding_orders}

Your task:
Act as Mason.

Review this Kingdom status.

Recommend ONE next build action for Manny.

Keep the answer practical.
Focus on revenue-supporting systems.
Keep it under 200 words.
"""

    return mason_chat(report)


if __name__ == "__main__":
    print(mason_inspect_kingdom())