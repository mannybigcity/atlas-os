# revenue/cleanup_revenue.py — cleanup tools for Alfred's revenue system

import json
from pathlib import Path

REVENUE_FILE = Path("revenue/revenue.json")


def load_revenue_items():
    if not REVENUE_FILE.exists():
        return []

    try:
        with open(REVENUE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_revenue_items(items):
    REVENUE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(REVENUE_FILE, "w", encoding="utf-8") as file:
        json.dump(items, file, indent=4)


def cleanup_zero_revenue_items():
    items = load_revenue_items()

    if not items:
        return "🦇 Alfred checked the revenue file. No revenue items found."

    cleaned_items = []
    removed_items = []

    for item in items:
        amount = float(item.get("amount", 0))

        if amount == 0:
            removed_items.append(item)
        else:
            cleaned_items.append(item)

    save_revenue_items(cleaned_items)

    if not removed_items:
        return "🦇 Alfred checked revenue. No zero-dollar revenue items needed cleanup."

    report = "🦇 Alfred cleaned up zero-dollar revenue items.\n\n"
    report += f"Removed Items: {len(removed_items)}\n\n"

    for item in removed_items:
        customer = item.get("customer", "Unknown Customer")
        source = item.get("source", "Unknown Source")
        status = item.get("status", "Unknown Status")
        report += f"- {customer} | {source} | $0.00 | {status}\n"

    return report