import json
from pathlib import Path

from skills.scout_opportunity_skill import (
    scout_show_opportunities,
    scout_add_opportunity,
    scout_send_opportunity_to_hunter
)


SCOUT_TARGETS_PATH = Path("data") / "scout_targets.json"


def load_scout_targets():
    if not SCOUT_TARGETS_PATH.exists():
        return None

    with open(SCOUT_TARGETS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_scout_targets(data):
    with open(SCOUT_TARGETS_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def scout_report():
    data = load_scout_targets()

    if data is None:
        return scout_missing_targets_error()

    report = "🦅 SCOUT OPPORTUNITY REPORT\n\n"
    report += f"SYSTEM: {data.get('system_name', 'Scout Target Database')}\n"
    report += f"MISSION: {data.get('mission', 'Find opportunities.')}\n"
    report += f"LOCATION: {data.get('location', 'Unknown')}\n\n"

    report += "TARGET CATEGORIES:\n"
    for category in data.get("target_categories", []):
        report += f"- {category}\n"

    report += "\nTARGETS:\n"

    targets = data.get("targets", [])

    if not targets:
        report += "- None\n"
    else:
        for target in targets:
            report += format_target(target)

    report += "\nSCOUT RECOMMENDATION:\n"
    report += "Start with businesses that have no website or outdated websites."

    return report


def scout_show_targets():
    data = load_scout_targets()

    if data is None:
        return scout_missing_targets_error()

    targets = data.get("targets", [])

    report = "🦅 SCOUT TARGETS\n\n"

    if not targets:
        report += "- None\n"
        return report

    for target in targets:
        report += format_target(target)

    return report


def scout_add_target(
    business_name,
    category="Unknown",
    source="Manual",
    website_status="Unknown",
    facebook_status="Unknown",
    instagram_status="Unknown",
    opportunity_score=5,
    notes="No notes"
):
    data = load_scout_targets()

    if data is None:
        return scout_missing_targets_error()

    clean_name = business_name.strip()

    if not clean_name:
        return (
            "🦅 SCOUT ERROR\n\n"
            "No business name was provided."
        )

    targets = data.get("targets", [])

    for target in targets:
        if target.get("business_name", "").lower() == clean_name.lower():
            return (
                "🦅 SCOUT NOTICE\n\n"
                f"Target already exists:\n{target.get('business_name')}"
            )

    new_target = {
        "business_name": clean_name,
        "category": category,
        "source": source,
        "website_status": website_status,
        "facebook_status": facebook_status,
        "instagram_status": instagram_status,
        "opportunity_score": opportunity_score,
        "status": "New",
        "notes": notes
    }

    targets.append(new_target)
    data["targets"] = targets

    save_scout_targets(data)

    return (
        "🦅 SCOUT TARGET ADDED\n\n"
        f"Business: {clean_name}\n"
        f"Category: {category}\n"
        f"Source: {source}\n"
        f"Website Status: {website_status}\n"
        f"Opportunity Score: {opportunity_score}\n\n"
        "Scout Status:\n"
        "Target added to the opportunity board."
    )


def scout_opportunity_report():
    data = load_scout_targets()

    if data is None:
        return scout_missing_targets_error()

    targets = data.get("targets", [])

    no_website = 0
    weak_website = 0
    high_score = 0

    for target in targets:
        website_status = str(target.get("website_status", "")).lower()
        score = int(target.get("opportunity_score", 0))

        if "no website" in website_status:
            no_website += 1

        if "weak" in website_status or "outdated" in website_status:
            weak_website += 1

        if score >= 8:
            high_score += 1

    report = "🦅 SCOUT SUMMARY REPORT\n\n"
    report += f"Total Targets: {len(targets)}\n"
    report += f"No Website: {no_website}\n"
    report += f"Weak/Outdated Website: {weak_website}\n"
    report += f"High Opportunity Score: {high_score}\n\n"

    report += "SCOUT RECOMMENDATION:\n"

    if high_score > 0:
        report += "Send the highest-score targets to Hunter for revenue ranking."
    elif no_website > 0:
        report += "Prioritize no-website businesses first."
    else:
        report += "Add more targets from Google Maps, Facebook, and Instagram."

    return report


def format_target(target):
    return (
        f"- {target.get('business_name', 'Unknown Business')} | "
        f"{target.get('category', 'Unknown Category')} | "
        f"Website: {target.get('website_status', 'Unknown')} | "
        f"Score: {target.get('opportunity_score', 0)} | "
        f"Status: {target.get('status', 'Unknown')}\n"
        f"  Source: {target.get('source', 'Unknown')}\n"
        f"  Facebook: {target.get('facebook_status', 'Unknown')}\n"
        f"  Instagram: {target.get('instagram_status', 'Unknown')}\n"
        f"  Notes: {target.get('notes', 'No notes')}\n"
    )


def scout_missing_targets_error():
    return (
        "🦅 SCOUT ERROR\n\n"
        "I could not find Scout's target database.\n\n"
        "Expected file:\n"
        "data/scout_targets.json"
    )


if __name__ == "__main__":
    print(scout_report())