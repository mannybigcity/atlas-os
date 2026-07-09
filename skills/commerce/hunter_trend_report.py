from datetime import datetime

def create_opportunity_report(
    keyword,
    marketplace,
    observed_trends,
    price_low,
    price_high,
    competition,
    notes
):
    score = 5

    if competition.lower() == "low":
        score += 3
    elif competition.lower() == "medium":
        score += 2

    if price_high >= 30:
        score += 1

    score = min(score, 10)

    report = {
        "timestamp": datetime.now().isoformat(),
        "keyword": keyword,
        "marketplace": marketplace,
        "observed_trends": observed_trends,
        "price_range": f"${price_low}-${price_high}",
        "competition": competition,
        "notes": notes,
        "opportunity_score": score
    }

    return report


if __name__ == "__main__":

    report = create_opportunity_report(
        keyword="Christian Shirts",
        marketplace="Etsy",
        observed_trends=[
            "Bible Verse Shirts",
            "Faith Over Fear",
            "Christian Mom Shirts",
            "Worship Apparel"
        ],
        price_low=22,
        price_high=34,
        competition="High",
        notes="Strong market but crowded."
    )

    print("\nHUNTER OPPORTUNITY REPORT\n")

    for key, value in report.items():
        print(f"{key}: {value}")