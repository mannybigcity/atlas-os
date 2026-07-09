"""Amanda Listing Engine.

Combines Hunter opportunity JSON with Micah design prompt JSON and turns the
strategy/design chain into Etsy-ready listing packages. The engine is local,
deterministic, and exports approval-ready JSON plus Markdown for Manny review
before anything is published.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRAIN_DIR = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
DEFAULT_HUNTER_INPUT_PATH = BRAIN_DIR / "06_MISSIONS" / "hunter_etsy_research" / "hunter_etsy_research_latest.json"
DEFAULT_MICAH_INPUT_PATH = BRAIN_DIR / "06_MISSIONS" / "micah_design_prompt_engine" / "micah_design_prompts_latest.json"
DEFAULT_OUTPUT_DIR = BRAIN_DIR / "06_MISSIONS" / "amanda_listing_engine"

MANNY_APPROVAL_REQUIREMENT = (
    "Manny approval is required before publishing this listing, changing live pricing, "
    "spending ad budget, contacting customers, accepting custom orders, or making any "
    "public/reputation-impacting marketplace action."
)

GENERIC_TAGS = [
    "custom gift",
    "personalized",
    "faith gift",
    "christian gift",
    "etsy gift",
    "handmade gift",
    "made to order",
    "family gift",
    "church gift",
    "unique gift",
    "custom order",
    "small business",
    "ramfam kingdom",
]

CATEGORY_HINTS = [
    {
        "terms": {"hat", "hats", "embroider", "embroidery", "patch"},
        "category": "Clothing > Unisex Adult Clothing > Hats & Caps > Baseball & Trucker Caps",
        "materials": ["structured trucker hat or dad hat blank", "embroidery thread or patch material", "stabilizer backing", "packaging sleeve"],
        "occasion": "Team event, church group order, business launch, Father's Day, volunteer appreciation",
        "recipient": "Church teams, dads, coaches, business owners, ministry volunteers",
        "tags": ["custom hat", "embroidered hat", "trucker hat", "dad hat", "church hats", "team hats", "logo hat", "hat patch"],
        "base_floor": 24.99,
        "base_ceiling": 34.99,
    },
    {
        "terms": {"shirt", "shirts", "tee", "apparel", "comfort colors", "dtf", "screen print"},
        "category": "Clothing > Unisex Adult Clothing > Tops & Tees > T-shirts",
        "materials": ["soft cotton or cotton-blend shirt", "DTF, screen print, or vinyl transfer", "care card", "shipping mailer"],
        "occasion": "Church event, family gathering, retreat, teacher appreciation, everyday faith wear",
        "recipient": "Families, church groups, teachers, youth ministries, faith-based shoppers",
        "tags": ["christian shirt", "faith shirt", "custom shirt", "church shirt", "family shirts", "teacher shirt", "jesus shirt", "retreat shirt"],
        "base_floor": 24.99,
        "base_ceiling": 32.99,
    },
    {
        "terms": {"engraved", "engraving", "laser", "wood", "cutting", "board", "sign"},
        "category": "Home & Living > Home Decor > Signs OR Kitchen & Dining > Cutting Boards",
        "materials": ["wood blank such as maple, bamboo, walnut, or acacia", "laser engraving", "food-safe finish when applicable", "protective packaging"],
        "occasion": "Wedding, housewarming, anniversary, Christmas, Mother's Day, closing gift",
        "recipient": "Couples, families, grandparents, homeowners, pastors, small business clients",
        "tags": ["engraved gift", "laser engraved", "cutting board", "wood sign", "wedding gift", "housewarming", "family name", "scripture gift"],
        "base_floor": 39.99,
        "base_ceiling": 59.99,
    },
    {
        "terms": {"tumbler", "wrap", "sublimation"},
        "category": "Home & Living > Kitchen & Dining > Drinkware > Tumblers & Water Glasses",
        "materials": ["stainless steel tumbler or sublimation blank", "sublimation transfer or UV DTF wrap", "lid and straw when applicable", "care card"],
        "occasion": "Birthday, encouragement gift, teacher appreciation, Mother's Day, church gift exchange",
        "recipient": "Moms, teachers, friends, ministry leaders, coworkers, faith-based gift buyers",
        "tags": ["tumbler wrap", "custom tumbler", "faith tumbler", "scripture cup", "teacher tumbler", "mom tumbler", "sublimation", "drinkware gift"],
        "base_floor": 29.99,
        "base_ceiling": 44.99,
    },
]


def slug_to_title(raw: str) -> str:
    words = re.sub(r"[^A-Za-z0-9]+", " ", raw).strip().split()
    return " ".join(word.capitalize() for word in words) or "Custom Etsy Product"


def truncate_text(text: str, limit: int) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip(" ,-|/") + "…"


def load_json_object(input_path: Path, label: str) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{label} JSON must contain an object at the top level.")
    return payload


def load_hunter_opportunity_json(input_path: Path) -> dict[str, Any]:
    payload = load_json_object(input_path, "Hunter opportunity")
    opportunities = payload.get("opportunities")
    if not isinstance(opportunities, list) or not opportunities:
        raise ValueError("Hunter opportunity JSON must include at least one opportunity.")
    return payload


def load_micah_design_prompt_json(input_path: Path) -> dict[str, Any]:
    payload = load_json_object(input_path, "Micah design prompt")
    concepts = payload.get("design_concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValueError("Micah design prompt JSON must include at least one design_concept.")
    return payload


def ranked_opportunities(hunter_payload: dict[str, Any]) -> list[dict[str, Any]]:
    opportunities = [item for item in hunter_payload.get("opportunities", []) if isinstance(item, dict)]
    return sorted(opportunities, key=lambda item: int(item.get("opportunity_score") or 0), reverse=True)


def ranked_design_concepts(micah_payload: dict[str, Any]) -> list[dict[str, Any]]:
    concepts = [item for item in micah_payload.get("design_concepts", []) if isinstance(item, dict)]
    return sorted(concepts, key=lambda item: int(item.get("rank") or 9999))


def opportunity_lookup(hunter_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for opportunity in ranked_opportunities(hunter_payload):
        keyword = str(opportunity.get("keyword") or "").lower()
        if keyword:
            lookup[keyword] = opportunity
    return lookup


def _context_text(opportunity: dict[str, Any], concept: dict[str, Any]) -> str:
    parts = [
        opportunity.get("keyword"),
        opportunity.get("recommended_offer"),
        concept.get("design_title"),
        concept.get("design_concept"),
        concept.get("art_direction"),
    ]
    return " ".join(str(part or "") for part in parts).lower()


def category_profile(opportunity: dict[str, Any], concept: dict[str, Any]) -> dict[str, Any]:
    context = _context_text(opportunity, concept)
    for profile in CATEGORY_HINTS:
        if any(re.search(rf"\b{re.escape(term)}\b", context) for term in profile["terms"]):
            return profile
    return {
        "category": "Handmade Products > Personalized Gifts",
        "materials": ["made-to-order product blank", "original artwork", "production-safe transfer or engraving method", "protective packaging"],
        "occasion": "Birthday, holiday, encouragement gift, ministry event, custom celebration",
        "recipient": "Faith-based gift buyers, families, churches, teachers, and local business customers",
        "tags": [],
        "base_floor": 24.99,
        "base_ceiling": 39.99,
    }


def clean_tag(raw_tag: str) -> str:
    tag = re.sub(r"[^a-zA-Z0-9 &-]", "", raw_tag).lower().strip()
    tag = re.sub(r"\s+", " ", tag)
    if len(tag) <= 20:
        return tag
    words = tag.split()
    shortened = ""
    for word in words:
        candidate = f"{shortened} {word}".strip()
        if len(candidate) <= 20:
            shortened = candidate
    return shortened or tag[:20].rstrip()


def etsy_tags(opportunity: dict[str, Any], concept: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    keyword = str(opportunity.get("keyword") or concept.get("source_keyword") or "custom gift")
    keyword_words = [word for word in re.sub(r"[^A-Za-z0-9]+", " ", keyword).lower().split() if len(word) > 2]
    candidates = [keyword, *profile.get("tags", []), *GENERIC_TAGS]

    if "family" in keyword_words:
        candidates.extend(["family shirts", "family reunion"])
    if "teacher" in keyword_words:
        candidates.extend(["teacher gift", "teacher shirt"])
    if "church" in keyword_words:
        candidates.extend(["church event", "ministry gift"])
    if "business" in keyword_words:
        candidates.extend(["business gift", "logo product"])

    tags: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        tag = clean_tag(str(candidate))
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
        if len(tags) == 13:
            return tags

    filler_index = 1
    while len(tags) < 13:
        filler = clean_tag(f"custom gift {filler_index}")
        if filler not in seen:
            tags.append(filler)
            seen.add(filler)
        filler_index += 1
    return tags


def pricing_suggestion(opportunity: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    average_price = float(opportunity.get("average_price") or 0.0)
    floor = float(profile.get("base_floor") or 24.99)
    ceiling = float(profile.get("base_ceiling") or 39.99)

    if average_price > 0:
        suggested_low = max(floor, round(average_price * 0.95, 2))
        suggested_high = max(suggested_low + 4.0, min(max(ceiling, average_price * 1.25), average_price + 18.0))
    else:
        suggested_low = floor
        suggested_high = ceiling

    return {
        "suggested_price_range": f"${suggested_low:.2f}-${suggested_high:.2f}",
        "anchor_price": f"${((suggested_low + suggested_high) / 2):.2f}",
        "source_average_price": f"${average_price:.2f}" if average_price > 0 else "Unknown",
        "rationale": (
            "Price inside or slightly above Hunter's sampled market range, then adjust after Manny reviews blank cost, labor, Etsy fees, "
            "shipping, personalization complexity, and desired margin."
        ),
        "manny_review_required": True,
    }


def product_title(opportunity: dict[str, Any], concept: dict[str, Any], profile: dict[str, Any]) -> str:
    keyword_title = slug_to_title(str(opportunity.get("keyword") or concept.get("source_keyword") or "Custom Gift"))
    design_title = str(concept.get("design_title") or keyword_title)
    angle = design_title.split(":", 1)[-1].strip() if ":" in design_title else design_title

    if "hat" in profile["category"].lower():
        raw = f"Custom Embroidered Hat - {angle} Personalized Church Team Business Cap"
    elif "t-shirt" in profile["category"].lower() or "clothing" in profile["category"].lower():
        raw = f"{keyword_title} - {angle} Custom Faith Shirt for Family Church Gifts"
    elif "cutting" in profile["category"].lower() or "sign" in profile["category"].lower():
        raw = f"{keyword_title} - Personalized Engraved Wood Gift for Family Wedding Housewarming"
    elif "tumbler" in profile["category"].lower():
        raw = f"{keyword_title} - Custom Faith Tumbler Gift with Personalized Design"
    else:
        raw = f"{keyword_title} - {angle} Personalized Faith Gift Made to Order"
    return truncate_text(raw, 140)


def seo_title(listing_title: str, opportunity: dict[str, Any], profile: dict[str, Any]) -> str:
    keyword = slug_to_title(str(opportunity.get("keyword") or "custom personalized gift"))
    raw = f"{listing_title} | {keyword}, Personalized, Made to Order, Faith Based Gift"
    return truncate_text(raw, 140)


def listing_description(opportunity: dict[str, Any], concept: dict[str, Any], title: str) -> str:
    offer = str(opportunity.get("recommended_offer") or "A differentiated custom product built for Etsy validation.")
    art_direction = str(concept.get("art_direction") or "Clean, production-ready artwork with a giftable presentation.")
    design_concept = str(concept.get("design_concept") or "Personalized product concept for Etsy shoppers.")
    keyword = str(opportunity.get("keyword") or concept.get("source_keyword") or "custom gift")

    return "\n".join(
        [
            title,
            "",
            "Create a meaningful made-to-order gift with a polished RAMFAM Kingdom/SIS Custom Creations production standard.",
            "",
            "Why shoppers will like it:",
            f"- Built around the proven Hunter opportunity: {keyword}.",
            f"- Design direction from Micah: {design_concept}",
            f"- Visual execution notes: {art_direction}",
            "- Personalization-friendly so buyers can request names, dates, church/team names, or short approved wording where the product allows.",
            "",
            "Ordering notes:",
            "1. Choose the product option and quantity.",
            "2. Add personalization details exactly as they should appear.",
            "3. Amanda/Manny review final wording, pricing, and production limits before public launch or customer commitment.",
            "",
            f"Offer context: {offer}",
            "",
            "Compliance note: Final art must avoid copyrighted characters, protected brand marks, celebrity names, unlicensed lyrics, and trademarked slogans.",
        ]
    )


def production_notes(opportunity: dict[str, Any], concept: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    notes = [
        "Confirm blank/product cost, supplier availability, labor time, packaging, shipping class, and Etsy fees before publishing.",
        "Create final production art from owned or properly licensed fonts and graphics only.",
        "Run a small sample or internal proof before accepting custom orders at scale.",
    ]
    context = _context_text(opportunity, concept)
    if "engraved" in context or "laser" in context:
        notes.append("Test laser settings on scrap material and confirm engraving contrast before photographing the sample.")
    if "shirt" in context or "tee" in context:
        notes.append("Check transfer size, shirt color contrast, wash-care language, and size chart accuracy.")
    if "hat" in context or "embroider" in context:
        notes.append("Digitize embroidery/patch artwork and verify stitch count, minimum text height, and thread color limits.")
    if "tumbler" in context or "sublimation" in context:
        notes.append("Verify wrap dimensions, seam placement, bleed margin, and color output on the tumbler blank.")
    return notes


def mockup_notes(concept: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    palette = ", ".join(str(color) for color in concept.get("color_palette", []) if color)
    art_direction = str(concept.get("art_direction") or "clean product-focused composition").rstrip(" .")
    notes = [
        f"Use mockups that clearly show the product category: {profile['category']}.",
        f"Reflect Micah art direction: {art_direction}.",
        "Include at least one hero image, one close-up/detail image, one personalization example, and one scale/context image.",
    ]
    if palette:
        notes.append(f"Keep mockup styling aligned with this color palette: {palette}.")
    notes.append("Do not publish mockups until Manny approves final wording, price, and production feasibility.")
    return notes


def build_listing_package(rank: int, opportunity: dict[str, Any], concept: dict[str, Any]) -> dict[str, Any]:
    profile = category_profile(opportunity, concept)
    title = product_title(opportunity, concept, profile)
    return {
        "rank": rank,
        "source_keyword": str(opportunity.get("keyword") or concept.get("source_keyword") or "custom gift"),
        "source_opportunity_score": int(opportunity.get("opportunity_score") or concept.get("source_opportunity_score") or 0),
        "source_design_title": concept.get("design_title"),
        "product_title": title,
        "seo_title": seo_title(title, opportunity, profile),
        "etsy_tags": etsy_tags(opportunity, concept, profile),
        "description": listing_description(opportunity, concept, title),
        "materials": list(profile["materials"]),
        "occasion": profile["occasion"],
        "recipient": profile["recipient"],
        "category_recommendation": profile["category"],
        "pricing_suggestion": pricing_suggestion(opportunity, profile),
        "production_notes": production_notes(opportunity, concept, profile),
        "mockup_notes": mockup_notes(concept, profile),
        "manny_approval_requirement": MANNY_APPROVAL_REQUIREMENT,
    }


def generate_listing_packages(
    hunter_payload: dict[str, Any], micah_payload: dict[str, Any], count: int | None = None
) -> list[dict[str, Any]]:
    opportunities = ranked_opportunities(hunter_payload)
    if not opportunities:
        raise ValueError("No Hunter opportunities available for Amanda listing generation.")
    concepts = ranked_design_concepts(micah_payload)
    if not concepts:
        raise ValueError("No Micah design concepts available for Amanda listing generation.")

    lookup = opportunity_lookup(hunter_payload)
    limit = len(concepts) if count is None else max(1, count)
    packages: list[dict[str, Any]] = []
    for index, concept in enumerate(concepts[:limit], start=1):
        source_keyword = str(concept.get("source_keyword") or "").lower()
        opportunity = lookup.get(source_keyword) or opportunities[(index - 1) % len(opportunities)]
        packages.append(build_listing_package(index, opportunity, concept))
    return packages


def generate_listing_report(
    hunter_payload: dict[str, Any], micah_payload: dict[str, Any], count: int | None = None
) -> dict[str, Any]:
    packages = generate_listing_packages(hunter_payload, micah_payload, count=count)
    top_package = packages[0] if packages else None
    return {
        "mission": "Amanda Listing Engine",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_missions": {
            "hunter": hunter_payload.get("mission", "Hunter Opportunity JSON"),
            "hunter_generated_at": hunter_payload.get("generated_at"),
            "micah": micah_payload.get("mission", "Micah Design Prompt JSON"),
            "micah_generated_at": micah_payload.get("generated_at"),
        },
        "agent_chain": {
            "assigned_by": "Atlas",
            "builder": "Mason",
            "revenue_owner": "Hunter",
            "design_owner": "Micah",
            "listing_owner": "Amanda",
            "approval_owner": "Manny",
        },
        "top_listing_package": top_package,
        "listing_packages": packages,
        "approval_required_before_public_action": True,
        "manny_approval_requirement": MANNY_APPROVAL_REQUIREMENT,
    }


def build_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Amanda Etsy Listing Package Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Hunter source: {report['source_missions'].get('hunter', 'Hunter Opportunity JSON')}",
        f"Micah source: {report['source_missions'].get('micah', 'Micah Design Prompt JSON')}",
        "Assigned by: Atlas",
        "Built by: Mason",
        "Revenue owner: Hunter",
        "Design owner: Micah",
        "Listing owner: Amanda",
        "Approval owner: Manny",
        "",
        "## Executive Summary",
        "",
    ]

    top = report.get("top_listing_package") or {}
    if top:
        lines.extend(
            [
                f"Top Etsy-ready package: {top.get('product_title', 'Unknown')}",
                f"Source keyword: {top.get('source_keyword', 'Unknown')} ({top.get('source_opportunity_score', 0)}/10)",
                f"Suggested pricing: {top.get('pricing_suggestion', {}).get('suggested_price_range', 'Needs review')}",
                "",
            ]
        )
    else:
        lines.extend(["No listing packages were generated.", ""])

    lines.extend(["## Etsy-Ready Listing Packages", ""])
    for package in report.get("listing_packages", []):
        lines.extend(
            [
                f"### {package['rank']}. {package['product_title']}",
                "",
                f"- Source keyword: {package['source_keyword']} ({package['source_opportunity_score']}/10)",
                f"- Source design: {package.get('source_design_title')}",
                f"- SEO title: {package['seo_title']}",
                f"- Etsy tags (13): {', '.join(package['etsy_tags'])}",
                f"- Materials: {', '.join(package['materials'])}",
                f"- Occasion: {package['occasion']}",
                f"- Recipient: {package['recipient']}",
                f"- Category recommendation: {package['category_recommendation']}",
                f"- Pricing suggestion: {package['pricing_suggestion']['suggested_price_range']} (anchor {package['pricing_suggestion']['anchor_price']})",
                f"- Pricing rationale: {package['pricing_suggestion']['rationale']}",
                "",
                "Description:",
                package["description"],
                "",
                "Production notes:",
            ]
        )
        lines.extend(f"- {note}" for note in package["production_notes"])
        lines.extend(["", "Mockup notes:"])
        lines.extend(f"- {note}" for note in package["mockup_notes"])
        lines.extend(["", f"Manny approval requirement: {package['manny_approval_requirement']}", ""])

    lines.extend(
        [
            "## Approval Rule",
            "",
            MANNY_APPROVAL_REQUIREMENT,
            "",
        ]
    )
    return "\n".join(lines)


def export_report(report: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    archive_json = output_dir / f"amanda_listing_packages_{timestamp}.json"
    latest_json = output_dir / "amanda_listing_packages_latest.json"
    archive_md = output_dir / f"amanda_listing_packages_{timestamp}.md"
    latest_md = output_dir / "amanda_listing_packages_latest.md"

    json_text = json.dumps(report, indent=2, ensure_ascii=False)
    markdown = build_markdown_report(report)

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Amanda Etsy listing packages from Hunter and Micah JSON inputs.")
    parser.add_argument("--hunter-input", type=Path, default=DEFAULT_HUNTER_INPUT_PATH, help="Hunter opportunity JSON input path.")
    parser.add_argument("--micah-input", type=Path, default=DEFAULT_MICAH_INPUT_PATH, help="Micah design prompt JSON input path.")
    parser.add_argument("--count", type=int, help="Optional number of listing packages to generate. Defaults to all Micah concepts.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for JSON and Markdown exports.")
    args = parser.parse_args()

    hunter_payload = load_hunter_opportunity_json(args.hunter_input)
    micah_payload = load_micah_design_prompt_json(args.micah_input)
    report = generate_listing_report(hunter_payload, micah_payload, count=args.count)
    exports = export_report(report, args.output_dir)

    print("AMANDA LISTING ENGINE COMPLETE")
    print(f"Listing packages: {len(report['listing_packages'])}")
    if report["top_listing_package"]:
        print(f"Top package: {report['top_listing_package']['product_title']}")
    print(f"JSON export: {exports['latest_json']}")
    print(f"Markdown report: {exports['latest_report']}")
    print("Approval note: Manny approval required before publishing, pricing changes, ad spend, or customer commitments.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
