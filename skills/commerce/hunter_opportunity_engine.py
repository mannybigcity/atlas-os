from datetime import datetime


def score_opportunity(price_high, competition, demand, uniqueness, mission_fit):
    score = 0

    if price_high >= 30:
        score += 2
    elif price_high >= 22:
        score += 1

    if competition.lower() == "low":
        score += 3
    elif competition.lower() == "medium":
        score += 2
    elif competition.lower() == "high":
        score += 1

    if demand.lower() == "high":
        score += 3
    elif demand.lower() == "medium":
        score += 2
    elif demand.lower() == "low":
        score += 1

    if uniqueness.lower() == "high":
        score += 2
    elif uniqueness.lower() == "medium":
        score += 1

    if mission_fit.lower() == "high":
        score += 2
    elif mission_fit.lower() == "medium":
        score += 1

    return min(score, 10)


def create_opportunity(keyword, marketplace, price_low, price_high, competition, demand, uniqueness, mission_fit, notes):
    return {
        "timestamp": datetime.now().isoformat(),
        "keyword": keyword,
        "marketplace": marketplace,
        "price_range": f"${price_low}-${price_high}",
        "competition": competition,
        "demand": demand,
        "uniqueness": uniqueness,
        "mission_fit": mission_fit,
        "notes": notes,
        "opportunity_score": score_opportunity(
            price_high,
            competition,
            demand,
            uniqueness,
            mission_fit
        )
    }


def rank_opportunities(opportunities):
    return sorted(opportunities, key=lambda item: item["opportunity_score"], reverse=True)


if __name__ == "__main__":
    opportunities = [
        create_opportunity(
            keyword="Christian Mom Shirts",
            marketplace="Etsy",
            price_low=22,
            price_high=32,
            competition="High",
            demand="High",
            uniqueness="Low",
            mission_fit="High",
            notes="Strong demand but crowded market."
        ),
        create_opportunity(
            keyword="Christian Grandpa Shirts",
            marketplace="Etsy",
            price_low=24,
            price_high=34,
            competition="Medium",
            demand="Medium",
            uniqueness="High",
            mission_fit="High",
            notes="Better niche angle. Good gift potential."
        ),
        create_opportunity(
            keyword="Faith Family Shirts",
            marketplace="Etsy",
            price_low=25,
            price_high=38,
            competition="Medium",
            demand="High",
            uniqueness="Medium",
            mission_fit="High",
            notes="Could work well for matching family shirts and church groups."
        ),
    ]

    ranked = rank_opportunities(opportunities)

    print("\nHUNTER PRODUCT OPPORTUNITY ENGINE\n")

    for index, item in enumerate(ranked, start=1):
        print(f"{index}. {item['keyword']}")
        print(f"   Marketplace: {item['marketplace']}")
        print(f"   Price Range: {item['price_range']}")
        print(f"   Competition: {item['competition']}")
        print(f"   Demand: {item['demand']}")
        print(f"   Uniqueness: {item['uniqueness']}")
        print(f"   Mission Fit: {item['mission_fit']}")
        print(f"   Score: {item['opportunity_score']}/10")
        print(f"   Notes: {item['notes']}")
        print()