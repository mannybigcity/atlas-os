import json
from pathlib import Path

from skills.amanda_outreach_skill import amanda_add_outreach


HUNTER_MAPS_PATH = Path("data") / "hunter_maps_targets.json"


def load_maps_targets():
    if not HUNTER_MAPS_PATH.exists():
        return None

    with open(HUNTER_MAPS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_maps_targets(data):
    with open(HUNTER_MAPS_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def hunter_maps_report():
    data = load_maps_targets()

    if data is None:
        return hunter_maps_missing_error()

    targets = data.get("targets", [])

    report = "🦅 HUNTER MAPS SCANNER\n\n"
    report += f"SYSTEM: {data.get('system_name')}\n"
    report += f"MISSION: {data.get('mission')}\n\n"

    report += "SEARCH AREAS:\n"
    for area in data.get("search_areas", []):
        report += f"- {area}\n"

    report += "\nTARGETS FOUND:\n"
    report += f"{len(targets)}\n\n"

    report += "HUNTER RECOMMENDATION:\n"
    report += "Prioritize businesses with strong reviews and no website, Facebook-only presence, weak websites, or outdated websites."

    return report


def hunter_show_maps_targets():
    data = load_maps_targets()

    if data is None:
        return hunter_maps_missing_error()

    targets = data.get("targets", [])

    report = "🦅 HUNTER MAPS TARGETS\n\n"

    if not targets:
        report += "No maps targets found."
        return report

    for target in targets:
        report += format_maps_target(target)

    return report


def hunter_add_maps_target(
    business_name,
    category="Unknown",
    city="Unknown",
    rating=0,
    review_count=0,
    website_status="Unknown",
    notes="No notes"
):
    data = load_maps_targets()

    if data is None:
        return hunter_maps_missing_error()

    clean_name = business_name.strip()

    if not clean_name:
        return "🦅 HUNTER ERROR\n\nNo business name provided."

    targets = data.get("targets", [])

    for target in targets:
        if target.get("business_name", "").lower() == clean_name.lower():
            return (
                "🦅 HUNTER NOTICE\n\n"
                f"Maps target already exists:\n{clean_name}"
            )

    score = calculate_opportunity_score(rating, review_count, website_status)
    label = classify_opportunity(score, website_status)

    targets.append({
        "business_name": clean_name,
        "category": category,
        "city": city,
        "rating": rating,
        "review_count": review_count,
        "website_status": website_status,
        "opportunity_score": score,
        "opportunity_label": label,
        "status": "New",
        "notes": notes
    })

    data["targets"] = targets
    save_maps_targets(data)

    return (
        "🦅 MAPS TARGET ADDED\n\n"
        f"Business: {clean_name}\n"
        f"Category: {category}\n"
        f"City: {city}\n"
        f"Rating: {rating}\n"
        f"Reviews: {review_count}\n"
        f"Website: {website_status}\n"
        f"Opportunity Score: {score}\n"
        f"Opportunity Label: {label}"
    )


def hunter_rescore_maps_targets():
    data = load_maps_targets()

    if data is None:
        return hunter_maps_missing_error()

    targets = data.get("targets", [])

    for target in targets:
        score = calculate_opportunity_score(
            target.get("rating", 0),
            target.get("review_count", 0),
            target.get("website_status", "Unknown")
        )

        target["opportunity_score"] = score
        target["opportunity_label"] = classify_opportunity(
            score,
            target.get("website_status", "Unknown")
        )

    data["targets"] = targets
    save_maps_targets(data)

    return (
        "🦅 HUNTER MAPS RESCORED\n\n"
        f"Targets Rescored: {len(targets)}"
    )


def hunter_rank_maps_targets():
    data = load_maps_targets()

    if data is None:
        return hunter_maps_missing_error()

    targets = data.get("targets", [])

    report = "🦅 HUNTER MAPS TARGETS\n\n"

    if not targets:
        report += "No maps targets to rank."
        return report

    ranked = sorted(
        targets,
        key=lambda item: int(item.get("opportunity_score", 0)),
        reverse=True
    )

    for target in ranked:
        report += format_maps_target(target)

    return report


def hunter_maps_summary():
    data = load_maps_targets()

    if data is None:
        return hunter_maps_missing_error()

    targets = data.get("targets", [])

    no_website = 0
    facebook_only = 0
    weak_website = 0
    outdated_website = 0
    unknown_website = 0
    high_score = 0
    sent_to_amanda = 0

    for target in targets:
        website = str(target.get("website_status", "")).lower()
        score = int(target.get("opportunity_score", 0))
        status = str(target.get("status", "")).lower()

        if "no website" in website:
            no_website += 1

        if "facebook" in website:
            facebook_only += 1

        if "weak" in website:
            weak_website += 1

        if "outdated" in website or "old" in website:
            outdated_website += 1

        if "unknown" in website:
            unknown_website += 1

        if score >= 8:
            high_score += 1

        if "sent to amanda" in status:
            sent_to_amanda += 1

    report = "🦅 HUNTER MAPS SUMMARY\n\n"
    report += f"Total Targets: {len(targets)}\n"
    report += f"No Website: {no_website}\n"
    report += f"Facebook Only: {facebook_only}\n"
    report += f"Weak Website: {weak_website}\n"
    report += f"Outdated Website: {outdated_website}\n"
    report += f"Unknown Website: {unknown_website}\n"
    report += f"High Score Targets: {high_score}\n"
    report += f"Sent To Amanda: {sent_to_amanda}\n\n"

    report += "HUNTER RECOMMENDATION:\n"

    if high_score > sent_to_amanda:
        report += "Send the highest-score targets to Amanda for outreach."
    else:
        report += "Hunt more businesses from Google Maps."

    return report


def hunter_send_maps_target_to_amanda(business_name):
    data = load_maps_targets()

    if data is None:
        return hunter_maps_missing_error()

    clean_name = business_name.strip().lower()
    targets = data.get("targets", [])

    for target in targets:
        target_name = target.get("business_name", "").lower()

        if clean_name in target_name or target_name in clean_name:
            old_status = target.get("status", "Unknown")
            target["status"] = "Sent To Amanda"

            save_maps_targets(data)

            amanda_response = amanda_add_outreach(
                target.get("business_name", "Unknown Business"),
                "Hunter Maps Scanner",
                (
                    f"Maps target. Category: {target.get('category', 'Unknown')}. "
                    f"City: {target.get('city', 'Unknown')}. "
                    f"Rating: {target.get('rating', 0)}. "
                    f"Reviews: {target.get('review_count', 0)}. "
                    f"Website: {target.get('website_status', 'Unknown')}. "
                    f"Score: {target.get('opportunity_score', 0)}. "
                    f"Label: {target.get('opportunity_label', 'Unlabeled')}."
                )
            )

            return (
                "🦅 HUNTER MAPS → AMANDA HANDOFF\n\n"
                f"Target: {target.get('business_name', 'Unknown Business')}\n"
                f"Score: {target.get('opportunity_score', 0)}\n"
                f"Label: {target.get('opportunity_label', 'Unlabeled')}\n"
                f"Old Status: {old_status}\n"
                f"New Status: Sent To Amanda\n\n"
                "AMANDA RESPONSE:\n"
                f"{amanda_response}"
            )

    return (
        "🦅 HUNTER ERROR\n\n"
        f"No maps target found matching:\n{business_name}"
    )


def calculate_opportunity_score(rating, review_count, website_status):
    score = 0

    try:
        rating = float(rating)
    except:
        rating = 0

    try:
        review_count = int(review_count)
    except:
        review_count = 0

    website = str(website_status).lower()

    if rating >= 4.9:
        score += 3
    elif rating >= 4.7:
        score += 2
    elif rating >= 4.4:
        score += 1

    if review_count >= 500:
        score += 4
    elif review_count >= 200:
        score += 3
    elif review_count >= 75:
        score += 2
    elif review_count >= 20:
        score += 1

    if "no website" in website:
        score += 5
    elif "facebook" in website:
        score += 4
    elif "weak" in website:
        score += 4
    elif "outdated" in website or "old" in website:
        score += 3
    elif "unknown" in website:
        score += 1

    if score > 10:
        score = 10

    return score


def classify_opportunity(score, website_status):
    website = str(website_status).lower()

    if "no website" in website and score >= 8:
        return "🔥 Prime Website Opportunity"

    if "facebook" in website and score >= 7:
        return "🔥 Facebook-Only Website Opportunity"

    if ("weak" in website or "outdated" in website or "old" in website) and score >= 7:
        return "⚠️ Website Refresh Opportunity"

    if score >= 8:
        return "High Opportunity"

    if score >= 5:
        return "Medium Opportunity"

    return "Low Opportunity"


def format_maps_target(target):
    return (
        f"- {target.get('business_name', 'Unknown Business')}\n"
        f"  Category: {target.get('category', 'Unknown')}\n"
        f"  City: {target.get('city', 'Unknown')}\n"
        f"  Rating: {target.get('rating', 0)}\n"
        f"  Reviews: {target.get('review_count', 0)}\n"
        f"  Website: {target.get('website_status', 'Unknown')}\n"
        f"  Score: {target.get('opportunity_score', 0)}\n"
        f"  Label: {target.get('opportunity_label', 'Unlabeled')}\n"
        f"  Status: {target.get('status', 'Unknown')}\n"
        f"  Notes: {target.get('notes', 'No notes')}\n\n"
    )


def hunter_maps_missing_error():
    return (
        "🦅 HUNTER ERROR\n\n"
        "I could not find Hunter's maps scanner database.\n\n"
        "Expected file:\n"
        "data/hunter_maps_targets.json"
    )


if __name__ == "__main__":
    print(hunter_show_maps_targets())