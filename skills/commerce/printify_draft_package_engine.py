"""Printify Draft Package Engine.

Turns Amanda listing package JSON into Printify-ready draft packages.
The engine is deterministic, local-first, and intentionally does not publish,
create, or modify live Printify products. It exports structured JSON plus a
Markdown report for Manny approval before any marketplace action.
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
DEFAULT_INPUT_PATH = BRAIN_DIR / "06_MISSIONS" / "amanda_listing_engine" / "amanda_listing_packages_latest.json"
DEFAULT_OUTPUT_DIR = BRAIN_DIR / "06_MISSIONS" / "printify_draft_package_engine"

MANNY_APPROVAL_REQUIREMENT = (
    "Manny approval is required before creating live Printify products, publishing, "
    "changing pricing, ordering samples, spending ad budget, contacting customers, "
    "accepting custom orders, or making any public/reputation-impacting marketplace action."
)

PRODUCT_PROFILES = [
    {
        "terms": {"shirt", "shirts", "tee", "t-shirt", "apparel", "dtf", "screen print"},
        "product_type": "Unisex Jersey T-Shirt",
        "printify_category": "Men's Clothing > T-shirts OR Women's Clothing > T-shirts",
        "blueprint_search_terms": "unisex jersey t-shirt bella canvas comfort colors shirt",
        "recommended_blank": "Bella+Canvas 3001 or Comfort Colors 1717 if available in the target Printify shop.",
        "variant_notes": ["Start with core unisex sizes S-2XL.", "Use neutral, high-conversion colors such as black, white, heather, cream, navy, and forest."],
        "estimated_base_cost": 12.50,
        "estimated_shipping_cost": 4.75,
        "print_area_notes": [
            "Primary print area: front chest, centered, approximately 11-12 inches wide for adult shirts.",
            "Prepare transparent PNG artwork at 4500 x 5400 px, 300 DPI, sRGB, with no background box.",
            "Keep important text inside safe margins and verify contrast on each garment color.",
        ],
        "mockup_direction": [
            "Use a clean front-facing shirt hero mockup first.",
            "Include a close-up of the chest print, a lifestyle/family or church group context mockup, and a size/color chart image.",
        ],
    },
    {
        "terms": {"tumbler", "wrap", "drinkware", "sublimation"},
        "product_type": "20oz Skinny Tumbler",
        "printify_category": "Home & Living > Drinkware > Tumblers",
        "blueprint_search_terms": "20oz skinny tumbler stainless steel sublimation wrap",
        "recommended_blank": "20oz stainless skinny tumbler with full-wrap sublimation support.",
        "variant_notes": ["Start with 20oz size only until proofed.", "Confirm lid/straw inclusion and care-card wording before launch."],
        "estimated_base_cost": 14.75,
        "estimated_shipping_cost": 6.25,
        "print_area_notes": [
            "Primary print area: full tumbler wrap; confirm exact Printify template dimensions before final upload.",
            "Keep key phrase away from the seam and include bleed where the provider template requires it.",
            "Export high-resolution PNG in sRGB and verify repeat/pattern alignment before sample order.",
        ],
        "mockup_direction": [
            "Use a hero mockup showing the full tumbler body and a secondary mockup showing the wrap seam.",
            "Include detail close-up, lid/straw context, and a flat wrap preview if Amanda needs buyer clarity.",
        ],
    },
    {
        "terms": {"engraved", "engraving", "laser", "wood", "cutting", "board", "charcuterie"},
        "product_type": "Wooden Cutting Board",
        "printify_category": "Home & Living > Kitchen & Dining > Cutting Boards",
        "blueprint_search_terms": "wooden cutting board engraved kitchen gift personalized board",
        "recommended_blank": "Wood or bamboo cutting board-style blank if available; otherwise route to manual SIS laser production instead of Printify.",
        "variant_notes": ["Confirm Printify has a suitable board/provider before treating this as POD-ready.", "If exact blank is unavailable, keep this as a local SIS production draft."],
        "estimated_base_cost": 18.00,
        "estimated_shipping_cost": 7.95,
        "print_area_notes": [
            "Primary print/engraving area: front board face; confirm provider template or local laser bed dimensions.",
            "Use single-color vector or high-contrast raster art with generous safe margins around handles and edges.",
            "If Printify cannot support engraving on the selected board, do not force POD; flag for SIS in-house laser fulfillment.",
        ],
        "mockup_direction": [
            "Use a warm kitchen/countertop hero mockup and a close-up that shows engraved detail clearly.",
            "Include one personalization example with names/date and one scale/context image with kitchen props.",
        ],
    },
    {
        "terms": {"hat", "hats", "cap", "embroider", "embroidery", "patch"},
        "product_type": "Embroidered Trucker Hat",
        "printify_category": "Accessories > Hats",
        "blueprint_search_terms": "embroidered trucker hat dad cap patch hat",
        "recommended_blank": "Structured trucker hat or dad cap with embroidery support.",
        "variant_notes": ["Limit launch colors to 3-5 hat colors.", "Avoid tiny type; embroidery needs thicker strokes and fewer colors."],
        "estimated_base_cost": 13.25,
        "estimated_shipping_cost": 4.95,
        "print_area_notes": [
            "Primary print area: front center embroidery/patch zone; confirm provider stitch-area dimensions.",
            "Use simplified vector-style art with large text, limited thread colors, and no fine texture.",
            "Request digitized proof before Manny approves any public order commitment.",
        ],
        "mockup_direction": [
            "Use front-facing hat hero mockup plus angled side view.",
            "Include close-up of embroidery/patch area and one lifestyle/workwear context image.",
        ],
    },
    {
        "terms": {"poster", "print", "wall art", "sign"},
        "product_type": "Matte Vertical Poster",
        "printify_category": "Home & Living > Wall Decor > Posters",
        "blueprint_search_terms": "matte vertical poster wall art print",
        "recommended_blank": "Matte poster or canvas-style wall art, depending on margin and provider availability.",
        "variant_notes": ["Start with 8x10, 11x14, and 16x20 sizes.", "Confirm frame is not included unless the provider variant includes it."],
        "estimated_base_cost": 7.25,
        "estimated_shipping_cost": 4.50,
        "print_area_notes": [
            "Prepare print art at final aspect ratio, 300 DPI, with bleed/safe margins from provider template.",
            "Keep all personalization text editable in source art before final export.",
        ],
        "mockup_direction": [
            "Use a home wall hero mockup, close-up texture image, and size comparison chart.",
        ],
    },
]

DEFAULT_PROFILE = {
    "product_type": "Printify Custom Gift Product",
    "printify_category": "Printify catalog review required",
    "blueprint_search_terms": "custom personalized gift print on demand",
    "recommended_blank": "Select the closest Printify blank after Manny confirms product fit, margin, and fulfillment risk.",
    "variant_notes": ["Keep variants narrow until a sample is approved.", "Confirm provider availability and shipping class before launch."],
    "estimated_base_cost": 10.00,
    "estimated_shipping_cost": 5.00,
    "print_area_notes": [
        "Confirm exact Printify template dimensions before final art upload.",
        "Use high-resolution transparent PNG or provider-required production format.",
        "Keep key art inside safe margins and verify color contrast on the selected blank.",
    ],
    "mockup_direction": [
        "Use one clear hero mockup, one detail image, one personalization example, and one scale/context image.",
    ],
}

CHECKLIST_ITEMS = [
    "Manny approves product type, supplier/provider, and launch risk.",
    "Final artwork uses owned/licensed fonts and graphics only.",
    "No copyrighted characters, protected logos, celebrity names, lyrics, or trademarked slogans.",
    "Printify blueprint/provider and variant availability are confirmed.",
    "Print area dimensions, safe margins, bleed, and file format are verified.",
    "Retail price, fees, shipping assumptions, and margin are reviewed.",
    "Mockups accurately represent the selected blank, colors, and personalization limits.",
    "Description, tags, and customer-facing production time are reviewed.",
    "Sample/proof path is defined before public launch or customer commitment.",
]


def load_amanda_listing_package_json(input_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Amanda listing package JSON must contain an object at the top level.")
    packages = payload.get("listing_packages")
    if not isinstance(packages, list) or not packages:
        raise ValueError("Amanda listing package JSON must include at least one listing_package.")
    return payload


def truncate_text(text: str, limit: int) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip(" ,-|/") + "…"


def slug_text(raw: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", raw.lower()).strip("-")
    return value or "custom-gift"


def money_to_float(raw: Any) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    match = re.search(r"\d+(?:\.\d+)?", str(raw or ""))
    return float(match.group(0)) if match else 0.0


def package_context(package: dict[str, Any]) -> str:
    parts = [
        package.get("source_keyword"),
        package.get("source_design_title"),
        package.get("product_title"),
        package.get("category_recommendation"),
        package.get("description"),
    ]
    parts.extend(package.get("materials", []) or [])
    parts.extend(package.get("etsy_tags", []) or [])
    return " ".join(str(part or "") for part in parts).lower()


def product_profile(package: dict[str, Any]) -> dict[str, Any]:
    context = package_context(package)
    for profile in PRODUCT_PROFILES:
        if any(re.search(rf"\b{re.escape(term)}\b", context) for term in profile["terms"]):
            return profile
    return DEFAULT_PROFILE


def product_type_recommendation(package: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_type": profile["product_type"],
        "printify_category": profile["printify_category"],
        "recommended_blank": profile["recommended_blank"],
        "blueprint_search_terms": profile["blueprint_search_terms"],
        "variant_notes": list(profile["variant_notes"]),
        "source_category": package.get("category_recommendation", "Amanda category recommendation unavailable"),
        "selection_status": "recommended_not_selected",
    }


def normalize_tags(package: dict[str, Any]) -> list[str]:
    candidates = [str(tag) for tag in package.get("etsy_tags", []) if tag]
    candidates.extend([str(package.get("source_keyword", "")), "printify draft", "made to order"])
    tags: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        tag = re.sub(r"[^a-zA-Z0-9 &-]", "", candidate).lower().strip()
        tag = re.sub(r"\s+", " ", tag)
        if not tag:
            continue
        if len(tag) > 20:
            words = tag.split()
            shortened = ""
            for word in words:
                next_value = f"{shortened} {word}".strip()
                if len(next_value) <= 20:
                    shortened = next_value
            tag = shortened or tag[:20].rstrip()
        if tag not in seen:
            tags.append(tag)
            seen.add(tag)
        if len(tags) == 13:
            break
    return tags


def pricing_math(package: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    suggestion = package.get("pricing_suggestion", {}) or {}
    retail_price = money_to_float(suggestion.get("anchor_price"))
    if retail_price <= 0:
        price_range = str(suggestion.get("suggested_price_range") or "")
        prices = [float(match) for match in re.findall(r"\d+(?:\.\d+)?", price_range)]
        retail_price = round(sum(prices) / len(prices), 2) if prices else 29.99

    base_cost = float(profile["estimated_base_cost"])
    shipping_cost = float(profile["estimated_shipping_cost"])
    transaction_fee = round(retail_price * 0.065, 2)
    payment_fee = round(retail_price * 0.03 + 0.25, 2)
    estimated_total_cost = round(base_cost + shipping_cost + transaction_fee + payment_fee, 2)
    estimated_profit = round(retail_price - estimated_total_cost, 2)
    target_margin_percent = round((estimated_profit / retail_price) * 100, 1) if retail_price else 0.0

    return {
        "retail_price": round(retail_price, 2),
        "estimated_printify_base_cost": round(base_cost, 2),
        "estimated_shipping_cost": round(shipping_cost, 2),
        "estimated_marketplace_transaction_fee": transaction_fee,
        "estimated_payment_fee": payment_fee,
        "estimated_total_cost": estimated_total_cost,
        "estimated_profit": estimated_profit,
        "target_margin_percent": target_margin_percent,
        "source_average_price": suggestion.get("source_average_price", "Unknown"),
        "pricing_status": "draft_math_pending_manny_review",
        "notes": "Replace estimates with exact Printify provider cost, selected variant cost, shop fees, shipping profile, discounts, and tax assumptions before publishing.",
    }


def product_description(package: dict[str, Any]) -> str:
    title = str(package.get("product_title") or "Custom Printify Draft Product")
    source_description = str(package.get("description") or "Amanda listing description not supplied.")
    return "\n".join(
        [
            title,
            "",
            source_description,
            "",
            "Printify draft notes:",
            "- This is a draft package only; no product has been published automatically.",
            "- Final production art, provider, variants, price, shipping, and mockups require Manny approval.",
            "- Customer-facing promises must not be made until product proofing and fulfillment assumptions are confirmed.",
        ]
    )


def listing_checklist() -> list[dict[str, str]]:
    return [{"item": item, "status": "pending_manny_review"} for item in CHECKLIST_ITEMS]


def manny_approval_gate(package: dict[str, Any]) -> dict[str, Any]:
    return {
        "required_approval": MANNY_APPROVAL_REQUIREMENT,
        "approved_for_publish": False,
        "approved_for_sample_order": False,
        "approved_for_ad_spend": False,
        "approved_for_customer_commitment": False,
        "source_amanda_requirement": package.get("manny_approval_requirement"),
    }


def build_printify_draft_package(rank: int, package: dict[str, Any]) -> dict[str, Any]:
    profile = product_profile(package)
    title = truncate_text(str(package.get("product_title") or "Custom Printify Product Draft"), 100)
    tags = normalize_tags(package)
    recommendation = product_type_recommendation(package, profile)
    draft_id = f"printify-draft-{rank:02d}-{slug_text(str(package.get('source_keyword') or title))}"
    description = product_description(package)

    return {
        "rank": rank,
        "draft_id": draft_id,
        "source_listing_rank": package.get("rank", rank),
        "source_keyword": package.get("source_keyword"),
        "source_design_title": package.get("source_design_title"),
        "title": title,
        "product_type_recommendation": recommendation,
        "print_area_notes": list(profile["print_area_notes"]),
        "mockup_direction": [*profile["mockup_direction"], *[str(note) for note in package.get("mockup_notes", []) or []]],
        "product_description": description,
        "pricing_math": pricing_math(package, profile),
        "tags": tags,
        "listing_checklist": listing_checklist(),
        "manny_approval_gate": manny_approval_gate(package),
        "printify_draft_payload": {
            "title": title,
            "description": description,
            "tags": tags,
            "blueprint_search_terms": recommendation["blueprint_search_terms"],
            "recommended_product_type": recommendation["product_type"],
            "recommended_blank": recommendation["recommended_blank"],
            "visible": False,
            "is_locked": False,
            "publish_action": "none_manual_manny_approval_required",
        },
    }


def generate_printify_draft_packages(amanda_payload: dict[str, Any], count: int | None = None) -> list[dict[str, Any]]:
    packages = [item for item in amanda_payload.get("listing_packages", []) if isinstance(item, dict)]
    if not packages:
        raise ValueError("No Amanda listing packages available for Printify draft generation.")
    limit = len(packages) if count is None else max(1, count)
    return [build_printify_draft_package(index, package) for index, package in enumerate(packages[:limit], start=1)]


def generate_printify_draft_report(amanda_payload: dict[str, Any], count: int | None = None) -> dict[str, Any]:
    drafts = generate_printify_draft_packages(amanda_payload, count=count)
    return {
        "mission": "Printify Draft Package Engine",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_mission": amanda_payload.get("mission", "Amanda Listing Package JSON"),
        "source_generated_at": amanda_payload.get("generated_at"),
        "agent_chain": {
            "assigned_by": "Atlas",
            "builder": "Mason",
            "listing_owner": "Amanda",
            "draft_owner": "Mason",
            "approval_owner": "Manny",
        },
        "top_printify_draft_package": drafts[0] if drafts else None,
        "printify_draft_packages": drafts,
        "auto_publish_enabled": False,
        "approval_required_before_public_action": True,
        "manny_approval_requirement": MANNY_APPROVAL_REQUIREMENT,
    }


def build_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Printify Draft Package Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Source mission: {report.get('source_mission', 'Amanda Listing Package JSON')}",
        "Assigned by: Atlas",
        "Built by: Mason",
        "Listing owner: Amanda",
        "Draft owner: Mason",
        "Approval owner: Manny",
        "Auto-publish enabled: false",
        "No products were published automatically.",
        "",
        "## Executive Summary",
        "",
    ]

    top = report.get("top_printify_draft_package") or {}
    if top:
        lines.extend(
            [
                f"Top Printify draft: {top.get('title', 'Unknown')}",
                f"Recommended product type: {top.get('product_type_recommendation', {}).get('product_type', 'Needs review')}",
                f"Draft retail price: ${top.get('pricing_math', {}).get('retail_price', 0):.2f}",
                "",
            ]
        )
    else:
        lines.extend(["No Printify drafts were generated.", ""])

    lines.extend(["## Printify-Ready Draft Packages", ""])
    for draft in report.get("printify_draft_packages", []):
        recommendation = draft["product_type_recommendation"]
        pricing = draft["pricing_math"]
        lines.extend(
            [
                f"### {draft['rank']}. {draft['title']}",
                "",
                f"- Draft ID: {draft['draft_id']}",
                f"- Source listing rank: {draft['source_listing_rank']}",
                f"- Source keyword: {draft.get('source_keyword', 'Unknown')}",
                f"- Recommended product type: {recommendation['product_type']}",
                f"- Printify category: {recommendation['printify_category']}",
                f"- Blueprint search terms: {recommendation['blueprint_search_terms']}",
                f"- Recommended blank: {recommendation['recommended_blank']}",
                f"- Pricing math: retail ${pricing['retail_price']:.2f}; estimated cost ${pricing['estimated_total_cost']:.2f}; estimated profit ${pricing['estimated_profit']:.2f}; target margin {pricing['target_margin_percent']}%",
                f"- Tags: {', '.join(draft['tags'])}",
                "",
                "Product description:",
                draft["product_description"],
                "",
                "Print area notes:",
            ]
        )
        lines.extend(f"- {note}" for note in draft["print_area_notes"])
        lines.extend(["", "Mockup direction:"])
        lines.extend(f"- {note}" for note in draft["mockup_direction"])
        lines.extend(["", "Listing checklist:"])
        lines.extend(f"- [{item['status']}] {item['item']}" for item in draft["listing_checklist"])
        lines.extend(["", f"Manny approval gate: {draft['manny_approval_gate']['required_approval']}", ""])

    lines.extend(["## Approval Rule", "", MANNY_APPROVAL_REQUIREMENT, ""])
    return "\n".join(lines)


def export_report(report: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    archive_json = output_dir / f"printify_draft_packages_{timestamp}.json"
    latest_json = output_dir / "printify_draft_packages_latest.json"
    archive_md = output_dir / f"printify_draft_packages_{timestamp}.md"
    latest_md = output_dir / "printify_draft_packages_latest.md"

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
    parser = argparse.ArgumentParser(description="Generate Printify-ready draft packages from Amanda listing package JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Amanda listing package JSON input path.")
    parser.add_argument("--count", type=int, help="Optional number of draft packages to generate. Defaults to all Amanda packages.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for JSON and Markdown exports.")
    args = parser.parse_args()

    amanda_payload = load_amanda_listing_package_json(args.input)
    report = generate_printify_draft_report(amanda_payload, count=args.count)
    exports = export_report(report, args.output_dir)

    print("PRINTIFY DRAFT PACKAGE ENGINE COMPLETE")
    print(f"Draft packages: {len(report['printify_draft_packages'])}")
    if report["top_printify_draft_package"]:
        print(f"Top draft: {report['top_printify_draft_package']['title']}")
    print(f"JSON export: {exports['latest_json']}")
    print(f"Markdown report: {exports['latest_report']}")
    print("Approval note: Manny approval required before creating live Printify products or publishing anything.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
