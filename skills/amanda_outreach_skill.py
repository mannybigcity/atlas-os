import json
from pathlib import Path


OUTREACH_PATH = Path("data") / "amanda_outreach.json"


def load_outreach():
    if not OUTREACH_PATH.exists():
        return None

    with open(OUTREACH_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_outreach(data):
    with open(OUTREACH_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def amanda_show_outreach_queue():
    data = load_outreach()

    if data is None:
        return "🐼 Amanda outreach database not found."

    queue = data.get("outreach_queue", [])

    report = "🐼 AMANDA OUTREACH QUEUE\n\n"

    if not queue:
        report += "No outreach opportunities queued."
        return report

    for item in queue:
        report += (
            f"- {item.get('business_name')}\n"
            f"  Status: {item.get('status')}\n"
            f"  Source: {item.get('source')}\n"
            f"  Notes: {item.get('notes')}\n\n"
        )

    return report


def amanda_add_outreach(
    business_name,
    source="Hunter",
    notes="Added from revenue pipeline."
):
    data = load_outreach()

    if data is None:
        return "🐼 Amanda outreach database not found."

    queue = data.get("outreach_queue", [])

    for item in queue:
        if item.get("business_name", "").lower() == business_name.lower():
            return (
                "🐼 AMANDA NOTICE\n\n"
                f"Business already in outreach queue:\n{business_name}"
            )

    queue.append({
        "business_name": business_name,
        "source": source,
        "status": "Pending Contact",
        "notes": notes
    })

    data["outreach_queue"] = queue

    save_outreach(data)

    return (
        "🐼 OUTREACH ADDED\n\n"
        f"Business: {business_name}\n"
        f"Status: Pending Contact"
    )


def amanda_complete_outreach(business_name):
    data = load_outreach()

    if data is None:
        return "🐼 Amanda outreach database not found."

    queue = data.get("outreach_queue", [])

    for item in queue:
        if item.get("business_name", "").lower() == business_name.lower():
            item["status"] = "Contacted"

            save_outreach(data)

            return (
                "🐼 OUTREACH COMPLETED\n\n"
                f"Business: {business_name}\n"
                f"New Status: Contacted"
            )

    return (
        "🐼 AMANDA ERROR\n\n"
        f"No outreach record found for:\n{business_name}"
    )


def amanda_outreach_report():
    data = load_outreach()

    if data is None:
        return "🐼 Amanda outreach database not found."

    queue = data.get("outreach_queue", [])

    pending = 0
    contacted = 0

    for item in queue:
        status = item.get("status", "")

        if status == "Pending Contact":
            pending += 1

        if status == "Contacted":
            contacted += 1

    report = "🐼 AMANDA OUTREACH REPORT\n\n"
    report += f"Total Outreach Opportunities: {len(queue)}\n"
    report += f"Pending Contact: {pending}\n"
    report += f"Contacted: {contacted}\n\n"

    report += "AMANDA RECOMMENDATION:\n"

    if pending > 0:
        report += "Work the outreach queue."
    else:
        report += "Request more opportunities from Hunter."

    return report


if __name__ == "__main__":
    print(amanda_show_outreach_queue())