from datetime import datetime

from atlas_decision_engine import build_decision_report


def generate_morning_briefing():
    today = datetime.now().strftime("%A, %B %d, %Y")

    current_items = [
        "Follow up with Uncle Ray about unpaid invoice",
        "Check Bobbie B&B HVAC customer order",
        "Improve Atlas decision system",
        "Work on FRESH Apparel website idea",
        "Build Amanda outreach agent",
    ]

    decision_report = build_decision_report(current_items)

    briefing = f"""
========================================
ATLAS MORNING BRIEFING
========================================

Date:
{today}

KINGDOM STATUS

Revenue Focus:
- Follow up on outstanding invoices
- Generate new opportunities
- Protect cash flow

Customer Commitments:
- Bobbie / B&B HVAC
- Existing SIS customers

Kingdom Law Check:

✓ Revenue Before Expansion
✓ Systems Before Scale
✓ Protect The King's Focus

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