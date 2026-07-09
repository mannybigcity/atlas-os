# skills/alfred_report.py

from crm.crm_skill import get_prospect_summary
from crm.followups import get_follow_up_summary
from orders.order_skill import load_orders


def generate_alfred_report():
    prospect_summary = get_prospect_summary()
    followup_summary = get_follow_up_summary()
    orders = load_orders()

    paid_revenue = 0
    outstanding_revenue = 0

    for order in orders:
        amount = float(order.get("total", 0))
        status = str(order.get("status", "")).lower()

        if "paid" in status:
            paid_revenue += amount

        elif (
            "awaiting" in status
            or "outstanding" in status
            or "invoice" in status
            or "unpaid" in status
            or "due" in status
        ):
            outstanding_revenue += amount

    report = "🐶 ALFRED COMMAND CENTER REPORT\n\n"

    report += "BUSINESS STATUS\n\n"

    report += f"Prospects: {prospect_summary['total']}\n"
    report += f"Hot Prospects: {prospect_summary['hot']}\n"
    report += f"Quoted Prospects: {prospect_summary['quoted']}\n"
    report += f"Invoice Sent: {prospect_summary['invoice_sent']}\n\n"

    report += f"Followups: {followup_summary['total']}\n"
    report += f"Due Today: {followup_summary['due_today']}\n"
    report += f"Overdue: {followup_summary['overdue']}\n\n"

    report += f"Paid Revenue: ${paid_revenue:.2f}\n"
    report += f"Outstanding Revenue: ${outstanding_revenue:.2f}\n\n"

    report += "NEXT ACTIONS\n\n"

    if outstanding_revenue > 0:
        report += "• Follow up on outstanding invoices\n"

    if followup_summary["overdue"] > 0:
        report += "• Complete overdue followups\n"

    if prospect_summary["total"] < 10:
        report += "• Add more prospects to CRM\n"

    report += "\nMission Status: ACTIVE"

    return report