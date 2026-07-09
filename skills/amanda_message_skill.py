import json
from pathlib import Path


BUSINESS_PROFILE_PATH = Path("data") / "business_profile.json"
HUNTER_MAPS_PATH = Path("data") / "hunter_maps_targets.json"


def load_json(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def find_maps_target(business_name):
    data = load_json(HUNTER_MAPS_PATH)

    if data is None:
        return None

    clean_name = business_name.strip().lower()

    for target in data.get("targets", []):
        target_name = target.get("business_name", "").lower()

        if clean_name in target_name or target_name in clean_name:
            return target

    return None


def amanda_write_outreach(business_name):
    profile = load_json(BUSINESS_PROFILE_PATH)
    target = find_maps_target(business_name)

    if profile is None:
        return "🐼 AMANDA ERROR\n\nBusiness profile not found."

    if target is None:
        return (
            "🐼 AMANDA ERROR\n\n"
            f"No Hunter Maps target found matching:\n{business_name}"
        )

    business = target.get("business_name", business_name)
    category = target.get("category", "your industry")
    city = target.get("city", "your area")
    rating = target.get("rating", 0)
    reviews = target.get("review_count", 0)
    website_status = target.get("website_status", "Unknown")
    company = profile.get("business_name", "SIS Custom Creations")
    offer = profile.get("offer", "free quick website review")

    message = "🐼 AMANDA OUTREACH MESSAGE\n\n"

    message += f"Target: {business}\n"
    message += f"From: {company}\n\n"

    message += "MESSAGE:\n\n"
    message += f"Hello! My name is Amanda and I work with {company}.\n\n"
    message += (
        f"I came across {business} while looking at local {category} businesses "
        f"in {city}, and I noticed your company has a strong reputation"
    )

    if rating and reviews:
        message += f" with a {rating} rating and {reviews} reviews"
    elif rating:
        message += f" with a {rating} rating"

    message += ".\n\n"

    if "no website" in str(website_status).lower():
        message += (
            "I also noticed there may not be a website listed for your business. "
            "That can make it harder for potential customers to learn about your services, "
            "request quotes, or contact you online.\n\n"
        )
    elif "weak" in str(website_status).lower() or "outdated" in str(website_status).lower():
        message += (
            "I also noticed your website may be due for a refresh. "
            "A cleaner, modern website can help turn more of your great reputation into calls, quotes, and new customers.\n\n"
        )
    else:
        message += (
            "We help local businesses improve their online presence through websites, branding, and digital marketing.\n\n"
        )

    message += (
        f"We are offering a {offer}. If you are open to it, "
        "I would be happy to send over a few simple ideas for improving your online presence.\n\n"
    )

    message += "Thank you for your time, and congratulations on the reputation your business has built.\n\n"
    message += "Amanda\n"
    message += f"{company}"

    return message


if __name__ == "__main__":
    print(amanda_write_outreach("Test Roofing Company"))