from skills.hunter_maps_search import hunter_search_places
from skills.hunter_maps_skill import hunter_add_maps_target


def hunter_hunt(industry, city):
    query = f"{industry} in {city} Texas"
    data = hunter_search_places(query)

    if "places" not in data:
        return f"🦅 HUNTER HUNT ERROR\n\n{data}"

    report = "🦅 HUNTER HUNT REPORT\n\n"
    report += f"Search: {query}\n\n"

    saved = 0
    skipped = 0

    for place in data.get("places", [])[:10]:
        name = place.get("displayName", {}).get("text", "Unknown Business")
        address = place.get("formattedAddress", "Unknown Address")
        rating = place.get("rating", 0)
        reviews = place.get("userRatingCount", 0)
        website = place.get("websiteUri", "No Website Found")

        if website == "No Website Found":
            website_status = "No Website Found"
        else:
            website_status = "Website Listed"

        result = hunter_add_maps_target(
            name,
            industry.title(),
            city.title(),
            rating,
            reviews,
            website_status,
            f"Auto-imported from Google Maps. Address: {address}. Website: {website}"
        )

        if "MAPS TARGET ADDED" in result:
            saved += 1
        else:
            skipped += 1

    report += f"Businesses Found: {len(data.get('places', []))}\n"
    report += f"Saved Targets: {saved}\n"
    report += f"Skipped/Duplicates: {skipped}\n\n"

    report += "HUNTER STATUS:\n"
    report += "Hunt complete. Review Hunter Maps rankings for best opportunities."

    return report


def hunter_hunt_plumbers_cypress():
    return hunter_hunt("plumbers", "Cypress")


if __name__ == "__main__":
    print(hunter_hunt_plumbers_cypress())