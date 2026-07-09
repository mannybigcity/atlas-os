import requests

from config.maps_config import GOOGLE_MAPS_API_KEY


def hunter_search_places(query):
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.userRatingCount,"
            "places.websiteUri"
        )
    }

    payload = {
        "textQuery": query
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    return response.json()


def hunter_test_search():
    data = hunter_search_places(
        "plumbers in Cypress Texas"
    )

    if "places" not in data:
        return f"ERROR:\n{data}"

    report = "🦅 HUNTER LIVE SEARCH\n\n"

    for place in data["places"][:10]:

        name = (
            place.get("displayName", {})
            .get("text", "Unknown")
        )

        address = place.get(
            "formattedAddress",
            "Unknown"
        )

        rating = place.get(
            "rating",
            "N/A"
        )

        reviews = place.get(
            "userRatingCount",
            0
        )

        website = place.get(
            "websiteUri",
            "No Website Listed"
        )

        report += (
            f"{name}\n"
            f"Rating: {rating}\n"
            f"Reviews: {reviews}\n"
            f"Website: {website}\n"
            f"Address: {address}\n\n"
        )

    return report