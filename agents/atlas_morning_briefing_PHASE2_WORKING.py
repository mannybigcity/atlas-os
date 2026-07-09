from datetime import datetime

from atlas_decision_engine import build_decision_report
from kingdom_data_loader import load_kingdom_items


def generate_morning_briefing():
    today = datetime.now().strftime("%A, %B %d, %Y")

    kingdom_items = load_kingdom_items()

    current_items = [
        item["name"]
        for item in kingdom_items
    ]

    decision_report = build_decision_report(current_items)

    briefing = f"""
========================================
ATLAS MORNING BRIEFING
========================================

Date:
{today}

KINGDOM STATUS

Active Kingdom Items:
{len(current_items)}

Revenue Focus:
- Follow up on outstanding invoices
- Generate new opportunities
- Protect cash flow

Kingdom Law Check:

✓ Revenue Before Expansion
✓ Systems Before Scale
✓ Protect The King's Focus

========================================
ATLAS ACTIVE ITEMS
========================================
"""

    for item in kingdom_items:
        briefing += (
            f"\n- {item['name']}"
            f"\n  Status: {item['status']}"
            f"\n  Type: {item['type']}\n"
        )

    briefing += f"""

========================================
ATLAS PRIORITY REPORT
========================================

{decision_report}

========================================
ATLAS FINAL RECOMMENDATION
========================================

Take action on the highest-ranked item first.

One completed priority is worth more than ten unfinished ideas.

========================================
"""

    return briefing


if __name__ == "__main__":
    print(generate_morning_briefing())