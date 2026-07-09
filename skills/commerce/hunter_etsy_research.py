"""Hunter Etsy Research Engine.

Researches Etsy product opportunities for RAMFAM Kingdom, scores them for
revenue potential, exports structured JSON, and generates an automatic
Markdown research report.

The engine uses the Etsy public listings API when ETSY_KEYSTRING is available.
If the key is missing or the API call fails, it falls back to clearly marked
local seed research data so Hunter can still produce a useful planning report
without blocking on credentials.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DIR = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
DEFAULT_OUTPUT_DIR = BRAIN_DIR / "06_MISSIONS" / "hunter_etsy_research"
ETSY_API_BASE_URL = "https://openapi.etsy.com/v3/application"

DEFAULT_KEYWORDS = [
    "custom embroidered hats",
    "christian shirts",
    "faith family shirts",
    "church event shirts",
    "teacher appreciation shirts",
    "custom laser engraved gifts",
]

MISSION_TERMS = {
    "christian",
    "faith",
    "jesus",
    "bible",
    "scripture",
    "church",
    "family",
    "hope",
    "kingdom",
    "worship",
    "prayer",
    "mom",
    "dad",
    "teacher",
    "custom",
    "personalized",
    "embroidered",
    "engraved",
}

PERSONALIZATION_TERMS = {
    "custom",
    "personalized",
    "name",
    "monogram",
    "embroidered",
    "engraved",
    "matching",
    "team",
    "family reunion",
    "event",
    "church group",
}

SEED_MARKET_DATA = {
    "custom embroidered hats": [
        {"title": "Custom Embroidered Richardson 112 Trucker Hat", "price": 27.99, "currency": "USD", "favorites": 88, "url": "offline-seed"},
        {"title": "Personalized Dad Hat with Logo Embroidery", "price": 24.50, "currency": "USD", "favorites": 64, "url": "offline-seed"},
        {"title": "Bulk Custom Church Group Embroidered Hats", "price": 22.00, "currency": "USD", "favorites": 31, "url": "offline-seed"},
    ],
    "christian shirts": [
        {"title": "Faith Over Fear Christian T Shirt", "price": 23.99, "currency": "USD", "favorites": 210, "url": "offline-seed"},
        {"title": "Jesus Loves You Comfort Colors Shirt", "price": 29.99, "currency": "USD", "favorites": 175, "url": "offline-seed"},
        {"title": "Bible Verse Scripture Tee", "price": 21.99, "currency": "USD", "favorites": 136, "url": "offline-seed"},
    ],
    "faith family shirts": [
        {"title": "Matching Faith Family Shirts", "price": 28.00, "currency": "USD", "favorites": 92, "url": "offline-seed"},
        {"title": "Personalized Christian Family Reunion Shirts", "price": 31.99, "currency": "USD", "favorites": 48, "url": "offline-seed"},
        {"title": "Faith Based Family Vacation Shirts", "price": 26.50, "currency": "USD", "favorites": 41, "url": "offline-seed"},
    ],
    "church event shirts": [
        {"title": "Custom Church Retreat Shirts", "price": 24.99, "currency": "USD", "favorites": 38, "url": "offline-seed"},
        {"title": "Youth Group Event Shirt Design", "price": 19.99, "currency": "USD", "favorites": 26, "url": "offline-seed"},
        {"title": "Women Ministry Conference Shirt", "price": 25.50, "currency": "USD", "favorites": 44, "url": "offline-seed"},
    ],
    "teacher appreciation shirts": [
        {"title": "Teacher Appreciation Custom Shirt", "price": 22.99, "currency": "USD", "favorites": 115, "url": "offline-seed"},
        {"title": "Personalized Teacher Team Shirts", "price": 27.99, "currency": "USD", "favorites": 71, "url": "offline-seed"},
        {"title": "Faith Based Teacher Shirt", "price": 24.50, "currency": "USD", "favorites": 37, "url": "offline-seed"},
    ],
    "custom laser engraved gifts": [
        {"title": "Custom Laser Engraved Cutting Board Gift", "price": 39.99, "currency": "USD", "favorites": 132, "url": "offline-seed"},
        {"title": "Personalized Engraved Tumbler", "price": 34.99, "currency": "USD", "favorites": 96, "url": "offline-seed"},
        {"title": "Engraved Scripture Wood Sign", "price": 42.00, "currency": "USD", "favorites": 58, "url": "offline-seed"},
    ],
}


@dataclass
class ListingSnapshot:
    title: str
    price: float
    currency: str
    favorites: int
    url: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "price": round(self.price, 2),
            "currency": self.currency,
            "favorites": self.favorites,
            "url": self.url,
        }


def _price_from_etsy(raw_price: Any) -> float:
    if isinstance(raw_price, dict):
        amount = raw_price.get("amount")
        divisor = raw_price.get("divisor") or 100
        try:
            return float(amount) / float(divisor)
        except (TypeError, ValueError, ZeroDivisionError):
            return 0.0
    try:
        return float(raw_price)
    except (TypeError, ValueError):
        return 0.0


def _normalize_listing(raw_listing: dict[str, Any]) -> ListingSnapshot:
    return ListingSnapshot(
        title=str(raw_listing.get("title") or "Untitled Etsy listing"),
        price=_price_from_etsy(raw_listing.get("price")),
        currency=str(raw_listing.get("currency_code") or raw_listing.get("currency") or "USD"),
        favorites=int(raw_listing.get("num_favorers") or raw_listing.get("favorites") or 0),
        url=str(raw_listing.get("url") or ""),
    )


def fetch_etsy_listings(keyword: str, limit: int, api_key: str) -> list[ListingSnapshot]:
    params = urllib.parse.urlencode(
        {
            "keywords": keyword,
            "limit": min(max(limit, 1), 100),
            "sort_on": "score",
        }
    )
    request = urllib.request.Request(
        f"{ETSY_API_BASE_URL}/listings/active?{params}",
        headers={
            "x-api-key": api_key,
            "User-Agent": "RAMFAM-KINGDOM-HUNTER",
        },
    )

    with urllib.request.urlopen(request, timeout=12) as response:
        payload = json.loads(response.read().decode("utf-8"))

    listings = payload.get("results", []) if isinstance(payload, dict) else []
    return [_normalize_listing(item) for item in listings[:limit]]


def seed_listings(keyword: str, limit: int) -> list[ListingSnapshot]:
    exact = SEED_MARKET_DATA.get(keyword.lower())
    if exact:
        return [_normalize_listing(item) for item in exact[:limit]]

    # For custom user-provided keywords, combine closest seed buckets so report
    # generation still works while clearly marking the source as offline seed data.
    combined: list[dict[str, Any]] = []
    keyword_terms = set(keyword.lower().split())
    for seed_keyword, listings in SEED_MARKET_DATA.items():
        if keyword_terms.intersection(seed_keyword.split()):
            combined.extend(listings)
    if not combined:
        combined = [item for listings in SEED_MARKET_DATA.values() for item in listings]
    return [_normalize_listing(item) for item in combined[:limit]]


def level_from_score(score: float, low: float, high: float) -> str:
    if score >= high:
        return "High"
    if score >= low:
        return "Medium"
    return "Low"


def opportunity_score(
    average_price: float,
    listing_count: int,
    average_favorites: float,
    mission_hits: int,
    personalization_hits: int,
) -> int:
    score = 0

    if average_price >= 35:
        score += 3
    elif average_price >= 27:
        score += 2
    elif average_price >= 20:
        score += 1

    if average_favorites >= 100:
        score += 3
    elif average_favorites >= 50:
        score += 2
    elif average_favorites >= 20:
        score += 1

    if listing_count <= 20:
        score += 2
    elif listing_count <= 60:
        score += 1

    if mission_hits >= 4:
        score += 2
    elif mission_hits >= 2:
        score += 1

    if personalization_hits >= 3:
        score += 1

    return min(score, 10)


def recommended_offer(keyword: str, average_price: float, mission_fit: str, uniqueness: str) -> str:
    if "hat" in keyword.lower():
        return "Launch a 12-piece custom embroidered hat starter bundle for churches, teams, and local businesses."
    if "engraved" in keyword.lower() or "laser" in keyword.lower():
        return "Launch a personalized engraved gift bundle with scripture, family names, or business branding."
    if mission_fit == "High" and uniqueness in {"Medium", "High"}:
        return "Launch a faith-forward personalized apparel offer with matching family/church group options."
    if average_price >= 30:
        return "Test a premium personalized version before competing on commodity designs."
    return "Use this as a design-validation keyword, but only build after finding a stronger niche angle."


def analyze_keyword(keyword: str, listings: list[ListingSnapshot], source: str) -> dict[str, Any]:
    prices = [listing.price for listing in listings if listing.price > 0]
    favorites = [listing.favorites for listing in listings]
    titles = " ".join(listing.title.lower() for listing in listings)

    listing_count = len(listings)
    price_low = min(prices) if prices else 0.0
    price_high = max(prices) if prices else 0.0
    average_price = statistics.mean(prices) if prices else 0.0
    average_favorites = statistics.mean(favorites) if favorites else 0.0
    mission_hits = sum(1 for term in MISSION_TERMS if term in titles or term in keyword.lower())
    personalization_hits = sum(1 for term in PERSONALIZATION_TERMS if term in titles or term in keyword.lower())

    competition_level = "High" if listing_count >= 75 else "Medium" if listing_count >= 25 else "Low"
    demand_signal = level_from_score(average_favorites, 40, 90)
    mission_fit = level_from_score(float(mission_hits), 2, 4)
    uniqueness = level_from_score(float(personalization_hits), 2, 4)
    score = opportunity_score(average_price, listing_count, average_favorites, mission_hits, personalization_hits)

    risks = []
    if competition_level == "High":
        risks.append("Crowded Etsy search; must differentiate by niche, bundle, or personalization.")
    if average_price < 22:
        risks.append("Low average price may compress margin after blanks, labor, and marketplace fees.")
    if mission_fit == "Low":
        risks.append("Weak RAMFAM/FRESH mission fit; avoid unless profit margin is clearly superior.")
    if not risks:
        risks.append("Main risk is execution speed: validate demand before building a large catalog.")

    next_actions = [
        "Pick the strongest niche angle and draft 3 listing titles.",
        "Estimate blank/product cost, labor time, shipping, and Etsy fees before publishing.",
        "Create one mockup or sample photo, then test with local/social audience before scaling.",
    ]

    return {
        "keyword": keyword,
        "source": source,
        "sampled_listing_count": listing_count,
        "price_low": round(price_low, 2),
        "price_high": round(price_high, 2),
        "average_price": round(average_price, 2),
        "average_favorites": round(average_favorites, 2),
        "competition_level": competition_level,
        "demand_signal": demand_signal,
        "uniqueness_signal": uniqueness,
        "mission_fit": mission_fit,
        "opportunity_score": score,
        "recommended_offer": recommended_offer(keyword, average_price, mission_fit, uniqueness),
        "risks": risks,
        "next_actions": next_actions,
        "sample_listings": [listing.to_dict() for listing in listings[:5]],
    }


def research_keywords(keywords: list[str], limit: int, use_api: bool = True) -> dict[str, Any]:
    api_key = os.getenv("ETSY_KEYSTRING", "").strip()
    api_errors: dict[str, str] = {}
    opportunities = []

    for keyword in keywords:
        source = "etsy_api"
        try:
            if not use_api or not api_key:
                raise RuntimeError("ETSY_KEYSTRING not available or API disabled")
            listings = fetch_etsy_listings(keyword, limit, api_key)
            if not listings:
                raise RuntimeError("Etsy API returned no listings")
        except (RuntimeError, urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as error:
            source = "offline_seed_data"
            api_errors[keyword] = str(error)
            listings = seed_listings(keyword, limit)

        opportunities.append(analyze_keyword(keyword, listings, source))

    ranked = sorted(opportunities, key=lambda item: item["opportunity_score"], reverse=True)
    top = ranked[0] if ranked else None

    return {
        "mission": "Hunter Etsy Research",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "agent_chain": {"assigned_by": "Atlas", "builder": "Mason", "revenue_owner": "Hunter"},
        "api_used": any(item["source"] == "etsy_api" for item in ranked),
        "api_errors": api_errors,
        "keywords": keywords,
        "top_opportunity": top,
        "opportunities": ranked,
        "approval_required_before_public_action": True,
    }


def build_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Hunter Etsy Research Report",
        "",
        f"Generated: {report['generated_at']}",
        "Assigned by: Atlas",
        "Built by: Mason",
        "Revenue owner: Hunter",
        "",
        "## Executive Recommendation",
        "",
    ]

    top = report.get("top_opportunity")
    if top:
        lines.extend(
            [
                f"Top opportunity: {top['keyword']} ({top['opportunity_score']}/10)",
                f"Recommended offer: {top['recommended_offer']}",
                "",
            ]
        )
    else:
        lines.extend(["No opportunities were generated.", ""])

    if report.get("api_errors"):
        lines.extend(
            [
                "Data note: one or more keywords used offline seed data because the Etsy API key was unavailable, disabled, or returned an error.",
                "",
            ]
        )

    lines.extend(
        [
            "## Ranked Opportunities",
            "",
            "| Rank | Keyword | Score | Demand | Competition | Mission Fit | Avg Price | Source |",
            "|---:|---|---:|---|---|---|---:|---|",
        ]
    )
    for index, item in enumerate(report["opportunities"], start=1):
        lines.append(
            f"| {index} | {item['keyword']} | {item['opportunity_score']}/10 | "
            f"{item['demand_signal']} | {item['competition_level']} | {item['mission_fit']} | "
            f"${item['average_price']:.2f} | {item['source']} |"
        )

    lines.extend(["", "## Opportunity Details", ""])
    for index, item in enumerate(report["opportunities"], start=1):
        lines.extend(
            [
                f"### {index}. {item['keyword']}",
                "",
                f"- Score: {item['opportunity_score']}/10",
                f"- Price range: ${item['price_low']:.2f}-${item['price_high']:.2f}; average ${item['average_price']:.2f}",
                f"- Demand signal: {item['demand_signal']} ({item['average_favorites']:.1f} average favorites in sample)",
                f"- Competition: {item['competition_level']} ({item['sampled_listing_count']} sampled listings)",
                f"- Mission fit: {item['mission_fit']}",
                f"- Uniqueness/personalization signal: {item['uniqueness_signal']}",
                f"- Recommended offer: {item['recommended_offer']}",
                "- Risks:",
            ]
        )
        lines.extend(f"  - {risk}" for risk in item["risks"])
        lines.append("- Next actions:")
        lines.extend(f"  - {action}" for action in item["next_actions"])
        lines.extend(["", "Sample listings:"])
        for listing in item["sample_listings"][:3]:
            lines.append(f"- {listing['title']} — ${listing['price']:.2f} ({listing['favorites']} favorites)")
        lines.append("")

    lines.extend(
        [
            "## Approval Rule",
            "",
            "Public listing, pricing, ad spend, customer outreach, or brand-impacting action requires Manny approval before execution.",
            "",
        ]
    )
    return "\n".join(lines)


def export_report(report: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    archive_json = output_dir / f"hunter_etsy_research_{timestamp}.json"
    latest_json = output_dir / "hunter_etsy_research_latest.json"
    archive_md = output_dir / f"hunter_etsy_research_{timestamp}.md"
    latest_md = output_dir / "hunter_etsy_research_latest.md"

    markdown = build_markdown_report(report)
    json_text = json.dumps(report, indent=2, ensure_ascii=False)

    archive_json.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    archive_md.write_text(markdown, encoding="utf-8")
    latest_md.write_text(markdown, encoding="utf-8")

    return {
        "archive_json": str(archive_json),
        "latest_json": str(latest_json),
        "archive_report": str(archive_md),
        "latest_report": str(latest_md),
    }


def parse_keywords(raw_keywords: str | None) -> list[str]:
    if not raw_keywords:
        return DEFAULT_KEYWORDS
    parsed = [keyword.strip() for keyword in raw_keywords.split(",") if keyword.strip()]
    return parsed or DEFAULT_KEYWORDS


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Hunter Etsy opportunity research.")
    parser.add_argument("--keywords", help="Comma-separated Etsy keywords to research.")
    parser.add_argument("--limit", type=int, default=25, help="Listings sampled per keyword. Default: 25.")
    parser.add_argument("--no-api", action="store_true", help="Skip Etsy API and use offline seed research data.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for JSON and Markdown exports.")
    args = parser.parse_args()

    keywords = parse_keywords(args.keywords)
    report = research_keywords(keywords, max(args.limit, 1), use_api=not args.no_api)
    exports = export_report(report, args.output_dir)

    print("HUNTER ETSY RESEARCH COMPLETE")
    print(f"Top opportunity: {report['top_opportunity']['keyword']} ({report['top_opportunity']['opportunity_score']}/10)")
    print(f"JSON export: {exports['latest_json']}")
    print(f"Markdown report: {exports['latest_report']}")
    if report["api_errors"]:
        print("Data note: offline seed data was used for at least one keyword. Set ETSY_KEYSTRING for live Etsy API research.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
