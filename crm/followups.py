from datetime import date, datetime
from crm.crm_skill import load_prospects, save_prospects


def set_follow_up(name, follow_up_date):
    prospects = load_prospects()

    for prospect in prospects:
        if prospect["name"].lower() == name.lower():
            prospect["follow_up"] = follow_up_date
            save_prospects(prospects)
            return f"Follow-up set for {name}: {follow_up_date}"

    return f"No prospect found named {name}."


def parse_follow_up_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def get_follow_up_items():
    prospects = load_prospects()

    matches = []
    for prospect in prospects:
        follow_up = prospect.get("follow_up")

        if follow_up:
            matches.append(prospect)

    return matches


def get_follow_up_summary():
    today = date.today()
    items = get_follow_up_items()

    total = len(items)
    due_today = 0
    overdue = 0
    upcoming = 0

    for item in items:
        follow_up_date = parse_follow_up_date(item.get("follow_up"))

        if follow_up_date is None:
            upcoming += 1
        elif follow_up_date < today:
            overdue += 1
        elif follow_up_date == today:
            due_today += 1
        else:
            upcoming += 1

    return {
        "total": total,
        "due_today": due_today,
        "overdue": overdue,
        "upcoming": upcoming,
        "items": items
    }


def show_follow_ups():
    summary = get_follow_up_summary()
    matches = summary["items"]

    if not matches:
        return "No follow-ups saved yet."

    lines = []
    lines.append("🦇 FOLLOW-UP COMMAND CENTER")
    lines.append("")
    lines.append(f"Total Follow-Ups: {summary['total']}")
    lines.append(f"Due Today: {summary['due_today']}")
    lines.append(f"Overdue: {summary['overdue']}")
    lines.append(f"Upcoming: {summary['upcoming']}")
    lines.append("")
    lines.append("FOLLOW-UP ITEMS:")

    for p in matches:
        lines.append(
            f"{p.get('name', 'Unknown')} | "
            f"{p.get('business', 'Unknown Business')} | "
            f"{p.get('product', 'Unknown Product')} | "
            f"Status: {p.get('status', 'Unknown')} | "
            f"Follow up: {p.get('follow_up', 'None')}"
        )

    return "\n".join(lines)