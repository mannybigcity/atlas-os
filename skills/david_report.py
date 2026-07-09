# skills/david_report.py

from crm.crm_skill import load_prospects


def generate_david_report():
    prospects = load_prospects()

    report = "🐺 DAVID SALES REPORT\n\n"

    if not prospects:
        report += "No prospects found."
        return report

    report += f"Total Prospects: {len(prospects)}\n\n"

    for prospect in prospects:
        name = prospect.get("name", "Unknown")
        business = prospect.get("business", "Unknown")
        status = prospect.get("status", "Unknown")

        report += (
            f"Name: {name}\n"
            f"Business: {business}\n"
            f"Status: {status}\n\n"
        )

    report += "RECOMMENDED ACTIONS\n\n"

    for prospect in prospects:
        status = prospect.get("status", "").lower()

        if (
            "invoice" in status
            or "approved" in status
            or "follow" in status
        ):
            report += (
                f"• Follow up with "
                f"{prospect.get('name', 'Unknown')}\n"
            )

    return report