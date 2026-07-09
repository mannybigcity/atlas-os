import os
import csv
import requests
from dotenv import load_dotenv
from pprint import pprint
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def google_maps_lead_generator(search_term):
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.nationalPhoneNumber,places.websiteUri"
    }

    payload = {
        "textQuery": search_term,
        "maxResultCount": 10
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    leads = []

    for place in data.get("places", []):
        leads.append({
            "search_term": search_term,
            "name": place.get("displayName", {}).get("text"),
            "address": place.get("formattedAddress"),
            "phone": place.get("nationalPhoneNumber", "N/A"),
            "website": place.get("websiteUri", "N/A"),
            "rating": place.get("rating", "N/A"),
            "source": "Google Places",
            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "http_status": response.status_code,
        "count": len(leads),
        "leads": leads,
        "raw_error": data.get("error")
    }

def save_leads_to_csv(leads, filename="google_maps_leads.csv"):
    folder = os.path.join(os.getcwd(), "crm", "exports")
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename)

    fieldnames = [
        "search_term",
        "name",
        "phone",
        "website",
        "address",
        "rating",
        "source",
        "date_found"
    ]

    file_exists = os.path.isfile(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for lead in leads:
            writer.writerow(lead)

    return filepath

if __name__ == "__main__":
    result = google_maps_lead_generator("HVAC Houston TX")
    pprint(result)

    if result["count"] > 0:
        saved_file = save_leads_to_csv(result["leads"])
        print(f"\nSaved leads to: {saved_file}")