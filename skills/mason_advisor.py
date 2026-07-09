import json
from pathlib import Path
from skills.mason_chat import mason_chat

PUTER_ROOT = Path(__file__).resolve().parents[1]

AGENTS_FILE = PUTER_ROOT / "memory" / "memory" / "agents.json"
REVENUE_FILE = PUTER_ROOT / "revenue" / "revenue.json"
KINGDOM_FILE = PUTER_ROOT / "RAMFAM_KINGDOM_BRAIN" / "RAMFAM_KINGDOM.md"


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


def load_kingdom_summary():
    if not KINGDOM_FILE.exists():
        return "Kingdom file not found."

    return KINGDOM_FILE.read_text(
        encoding="utf-8"
    )[:3000]


def mason_advisor():

    agents = load_agents()
    revenue = load_revenue()
    kingdom = load_kingdom_summary()

    active_agents = len(
        [a for a in agents if a.get("status", "").lower() == "active"]
    )

    paid_items = len(
        [r for r in revenue if r.get("status", "").lower() == "paid"]
    )

    outstanding_items = len(
        [r for r in revenue if r.get("status", "").lower() == "outstanding"]
    )

    prompt = f"""
You are Mason.

Review the Kingdom information below.

KINGDOM SUMMARY:
{kingdom}

ACTIVE AGENTS:
{active_agents}

PAID REVENUE ITEMS:
{paid_items}

OUTSTANDING REVENUE ITEMS:
{outstanding_items}

Your task:

Act as Mason.

Advise Manny on:

1. What the Kingdom should focus on today.
2. What NOT to focus on today.
3. The single highest-value next build action.

Keep it under 250 words.

Be practical.

Follow Kingdom Law:
Revenue Before Expansion.

End with:

RECOMMENDED NEXT ACTION:
"""

    return mason_chat(prompt)


if __name__ == "__main__":
    print(mason_advisor())