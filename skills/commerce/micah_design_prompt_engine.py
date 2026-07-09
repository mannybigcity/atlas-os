"""Micah Design Prompt Engine.

Turns Hunter opportunity JSON into Etsy-ready design concepts for Micah.
The engine is deterministic, local-first, and exports both structured JSON and
Markdown so the design queue can be reviewed before any public marketplace action.
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
DEFAULT_INPUT_PATH = BRAIN_DIR / "06_MISSIONS" / "hunter_etsy_research" / "hunter_etsy_research_latest.json"
DEFAULT_OUTPUT_DIR = BRAIN_DIR / "06_MISSIONS" / "micah_design_prompt_engine"

DESIGN_ANGLES = [
    {
        "name": "Heirloom Scripture Minimal",
        "concept": "A premium personalized keepsake built around family names, short scripture text, and a clean monogram focal point.",
        "art_direction": "Minimal heirloom composition with centered engraving layout, fine line botanical accents, generous negative space, and balanced product mockup framing.",
        "palette": ["warm walnut brown", "soft ivory", "charcoal ink", "muted sage", "brushed gold accent"],
        "typography": "Elegant serif for the family name, small caps sans-serif for dates, and restrained script only for one accent word.",
        "prompt_style": "premium heirloom engraving layout, clean monogram centerpiece, fine botanical line art, warm natural material texture",
    },
    {
        "name": "Faith Family Matching Set",
        "concept": "A coordinated family or church-group apparel design that feels warm, modern, and photo-ready for Etsy listing mockups.",
        "art_direction": "Stacked badge layout with subtle rays, hand-lettered faith phrase, and adaptable placement for adult, youth, and toddler shirts.",
        "palette": ["cream", "deep forest green", "terracotta", "warm sand", "soft black"],
        "typography": "Friendly bold serif headline paired with rounded sans-serif supporting text; preserve readability at shirt-print distance.",
        "prompt_style": "modern faith family shirt graphic, stacked vintage badge, subtle sunrise rays, hand-lettered warmth",
    },
    {
        "name": "Church Retreat Badge",
        "concept": "An event-ready design system for retreats, youth groups, conferences, and ministry teams needing a clean custom shirt concept.",
        "art_direction": "Outdoor badge emblem with mountain or path symbolism, simple cross-negative-space detail, and editable event/date line.",
        "palette": ["navy", "bone", "copper", "olive", "sky blue"],
        "typography": "Condensed sans-serif for event text, sturdy slab serif for the theme phrase, clean microtype for location and year.",
        "prompt_style": "church retreat badge emblem, mountain path symbolism, clean cross negative space, screen print vector style",
    },
    {
        "name": "Teacher Grace Collection",
        "concept": "A teacher appreciation design with faith-forward encouragement that can live on shirts, tumblers, totes, or stickers.",
        "art_direction": "Soft classroom motifs with pencil, apple, tiny florals, and a positive hand-lettered phrase arranged for print-on-demand blanks.",
        "palette": ["dusty rose", "mustard", "cream", "sage", "graphite"],
        "typography": "Playful handwritten headline balanced by tidy rounded sans-serif; keep letters thick enough for vinyl or DTF transfer.",
        "prompt_style": "teacher appreciation faith graphic, soft classroom icons, cheerful hand lettering, boutique Etsy printable style",
    },
    {
        "name": "Local Business Heritage Mark",
        "concept": "A polished custom brand-mark concept for engraved gifts, hats, and promotional products aimed at local business buyers.",
        "art_direction": "Vintage maker's mark with border, initials area, subtle texture, and flexible badge variants for hat patches or laser engraving.",
        "palette": ["black", "natural leather", "antique gold", "smoke gray", "canvas tan"],
        "typography": "Industrial slab serif with clean geometric sans-serif; avoid overly thin strokes so the mark engraves cleanly.",
        "prompt_style": "vintage local business badge mark, premium maker logo, laser engraving friendly, hat patch compatible",
    },
    {
        "name": "Hope Forward Statement Tee",
        "concept": "A bold FRESH-aligned statement shirt built around encouragement, service, and everyday witness without copying common slogans.",
        "art_direction": "Modern typography-led shirt graphic with kinetic layout, small icon accents, and optional meal-giving impact line.",
        "palette": ["washed black", "off white", "sunrise orange", "royal blue", "muted gold"],
        "typography": "Heavy condensed headline, italic accent word, and simple sans-serif footer; prioritize clear production-ready hierarchy.",
        "prompt_style": "bold faith based statement tee, modern typographic streetwear layout, hopeful energy, screen print ready",
    },
    {
        "name": "Personalized Blessing Board",
        "concept": "A cutting board or wood sign concept for weddings, housewarmings, and family legacy gifts with personalization front and center.",
        "art_direction": "Arched composition with wreath frame, family surname, establishment year, and optional short blessing line engraved into warm wood.",
        "palette": ["maple wood", "dark walnut", "linen", "olive branch green", "matte black"],
        "typography": "Refined script for surname, high-readability serif for blessing text, and small sans-serif for year/location.",
        "prompt_style": "personalized blessing cutting board engraving, arched wreath frame, family legacy gift, elegant wood mockup",
    },
    {
        "name": "Youth Group Energy Drop",
        "concept": "A youth ministry shirt concept with high-energy graphics while staying clean enough for church approval and Etsy listing photos.",
        "art_direction": "Dynamic sticker-like composition with bold outline, halftone texture, motion lines, and editable ministry name block.",
        "palette": ["electric blue", "sun yellow", "white", "black", "coral"],
        "typography": "Chunky sans-serif headline with subtle hand-drawn secondary text; avoid distressed text that harms legibility.",
        "prompt_style": "youth group shirt graphic, energetic sticker style, bold outline, halftone accents, church appropriate",
    },
    {
        "name": "Scripture Tumbler Wrap",
        "concept": "A seamless tumbler wrap concept pairing scripture-inspired encouragement with floral or geometric details for giftable listings.",
        "art_direction": "Repeating wrap layout with central phrase panel, balanced pattern edges, and production-safe spacing for 20oz/30oz tumblers.",
        "palette": ["blush", "cream", "eucalyptus", "deep plum", "rose gold"],
        "typography": "Soft script accent with clean serif phrase text; keep phrase panel uncluttered for mockup readability.",
        "prompt_style": "seamless tumbler wrap design, scripture inspired encouragement, floral geometric border, Etsy sublimation style",
    },
    {
        "name": "Kingdom Workwear Patch",
        "concept": "A durable embroidered hat or workwear patch design for teams, volunteers, and entrepreneurs who want a faith-rooted identity piece.",
        "art_direction": "Simple patch-ready shield or rectangle mark with bold icon, limited thread colors, and clear silhouette for embroidery digitizing.",
        "palette": ["khaki", "deep navy", "white", "rust", "forest green"],
        "typography": "Block sans-serif or slab serif, no hairline strokes, all text large enough to survive embroidery on a hat front.",
        "prompt_style": "embroidered workwear hat patch, simple shield badge, faith rooted identity, limited thread color vector art",
    },
]

ANGLE_KEYWORD_HINTS = {
    "Heirloom Scripture Minimal": {"engraved", "engraving", "laser", "wood", "sign", "scripture", "gift", "personalized"},
    "Faith Family Matching Set": {"faith", "family", "shirt", "shirts", "matching", "christian", "apparel", "reunion"},
    "Church Retreat Badge": {"church", "retreat", "event", "conference", "ministry", "youth", "shirt", "shirts"},
    "Teacher Grace Collection": {"teacher", "appreciation", "school", "classroom", "shirt", "shirts", "tote"},
    "Local Business Heritage Mark": {"business", "logo", "brand", "hat", "hats", "engraved", "engraving", "laser", "promotional"},
    "Hope Forward Statement Tee": {"christian", "faith", "hope", "shirt", "shirts", "tee", "apparel", "fresh"},
    "Personalized Blessing Board": {"engraved", "engraving", "laser", "cutting", "board", "wood", "wedding", "housewarming", "family"},
    "Youth Group Energy Drop": {"youth", "group", "church", "event", "ministry", "shirt", "shirts"},
    "Scripture Tumbler Wrap": {"tumbler", "wrap", "sublimation", "scripture", "gift", "floral"},
    "Kingdom Workwear Patch": {"embroidered", "embroidery", "hat", "hats", "patch", "workwear", "team", "business"},
}


def slug_to_title(raw: str) -> str:
    words = re.sub(r"[^A-Za-z0-9]+", " ", raw).strip().split()
    return " ".join(word.capitalize() for word in words) or "Etsy Opportunity"


def load_hunter_opportunity_json(input_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Hunter opportunity JSON must contain an object at the top level.")
    opportunities = payload.get("opportunities")
    if not isinstance(opportunities, list) or not opportunities:
        raise ValueError("Hunter opportunity JSON must include at least one opportunity.")
    return payload


def ranked_opportunities(hunter_payload: dict[str, Any]) -> list[dict[str, Any]]:
    opportunities = [item for item in hunter_payload.get("opportunities", []) if isinstance(item, dict)]
    return sorted(opportunities, key=lambda item: int(item.get("opportunity_score") or 0), reverse=True)


def _sample_titles(opportunity: dict[str, Any]) -> list[str]:
    titles = []
    for listing in opportunity.get("sample_listings", []) or []:
        if isinstance(listing, dict) and listing.get("title"):
            titles.append(str(listing["title"]))
    return titles[:3]


def _opportunity_text(opportunity: dict[str, Any]) -> str:
    parts = [
        str(opportunity.get("keyword") or ""),
        str(opportunity.get("recommended_offer") or ""),
    ]
    parts.extend(_sample_titles(opportunity))
    return " ".join(parts).lower()


def _ranked_angles_for_opportunity(opportunity: dict[str, Any]) -> list[dict[str, Any]]:
    opportunity_text = _opportunity_text(opportunity)

    def score(angle: dict[str, Any]) -> int:
        hints = ANGLE_KEYWORD_HINTS.get(str(angle["name"]), set())
        return sum(1 for hint in hints if hint in opportunity_text)

    return sorted(DESIGN_ANGLES, key=score, reverse=True)


def _commercial_use_notes(keyword: str) -> str:
    return (
        f"Original artwork direction for the '{keyword}' opportunity. "
        "No copyrighted characters, sports/team marks, brand logos, celebrity names, protected lyrics, or trademarked slogans. "
        "Verify phrase trademark status before listing, use licensed fonts/graphics only, and create final production art from owned or properly licensed assets. "
        "Public listing, ad spend, or customer outreach requires Manny approval."
    )


def generate_design_concepts(hunter_payload: dict[str, Any], count: int = 10) -> list[dict[str, Any]]:
    opportunities = ranked_opportunities(hunter_payload)
    if not opportunities:
        raise ValueError("No Hunter opportunities available for Micah design generation.")

    total = max(1, count)
    concepts: list[dict[str, Any]] = []
    for index in range(total):
        opportunity = opportunities[index % len(opportunities)]
        ranked_angles = _ranked_angles_for_opportunity(opportunity)
        angle = ranked_angles[(index // len(opportunities)) % len(ranked_angles)]
        keyword = str(opportunity.get("keyword") or "Etsy opportunity")
        keyword_title = slug_to_title(keyword)
        sample_titles = _sample_titles(opportunity)
        sample_context = "; ".join(sample_titles) if sample_titles else "Hunter opportunity signals"
        offer = str(opportunity.get("recommended_offer") or "Build a differentiated Etsy-ready product concept.")
        demand = str(opportunity.get("demand_signal") or "Unknown")
        competition = str(opportunity.get("competition_level") or "Unknown")
        mission_fit = str(opportunity.get("mission_fit") or "Unknown")

        design_title = f"{keyword_title}: {angle['name']}"
        openai_image_prompt = (
            f"OpenAI image generation prompt: Create an original Etsy-ready product design for {keyword}. {angle['prompt_style']}. "
            f"Use this market context without copying listings: {sample_context}. "
            "Flat vector or clean product-design artwork, crisp edges, high readability, balanced composition, transparent background, "
            "print-on-demand ready, no mockup text cut off, no copyrighted characters, no brand logos, no trademarked slogans, no photorealistic people. "
            f"Color palette: {', '.join(angle['palette'])}."
        )

        concepts.append(
            {
                "rank": index + 1,
                "source_keyword": keyword,
                "source_opportunity_score": int(opportunity.get("opportunity_score") or 0),
                "source_signals": {
                    "demand": demand,
                    "competition": competition,
                    "mission_fit": mission_fit,
                },
                "design_title": design_title,
                "design_concept": f"{angle['concept']} Hunter offer context: {offer}",
                "art_direction": angle["art_direction"],
                "color_palette": list(angle["palette"]),
                "typography_suggestions": angle["typography"],
                "openai_image_prompt": openai_image_prompt,
                "image_prompt": openai_image_prompt,
                "commercial_use_notes": _commercial_use_notes(keyword),
            }
        )
    return concepts


def generate_design_prompt_report(hunter_payload: dict[str, Any], count: int = 10) -> dict[str, Any]:
    opportunities = ranked_opportunities(hunter_payload)
    top_opportunity = opportunities[0] if opportunities else None
    return {
        "mission": "Micah Design Prompt Engine",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_mission": hunter_payload.get("mission", "Hunter Opportunity JSON"),
        "source_generated_at": hunter_payload.get("generated_at"),
        "agent_chain": {"assigned_by": "Atlas", "builder": "Mason", "revenue_owner": "Hunter", "design_owner": "Micah"},
        "top_source_opportunity": top_opportunity,
        "design_concepts": generate_design_concepts(hunter_payload, count=count),
        "approval_required_before_public_action": True,
    }


def build_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Micah Etsy Design Prompt Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Source mission: {report.get('source_mission', 'Hunter Opportunity JSON')}",
        "Assigned by: Atlas",
        "Built by: Mason",
        "Revenue owner: Hunter",
        "Design owner: Micah",
        "",
        "## Executive Summary",
        "",
    ]

    top = report.get("top_source_opportunity") or {}
    if top:
        lines.extend(
            [
                f"Top source opportunity: {top.get('keyword', 'Unknown')} ({top.get('opportunity_score', 0)}/10)",
                f"Recommended offer context: {top.get('recommended_offer', 'No Hunter offer context supplied.')}",
                "",
            ]
        )

    lines.extend(
        [
            "## Etsy-Ready Design Concepts",
            "",
        ]
    )

    for concept in report.get("design_concepts", []):
        lines.extend(
            [
                f"### {concept['rank']}. {concept['design_title']}",
                "",
                f"- Source keyword: {concept['source_keyword']} ({concept['source_opportunity_score']}/10)",
                f"- Design concept: {concept['design_concept']}",
                f"- Art direction: {concept['art_direction']}",
                f"- Color palette: {', '.join(concept['color_palette'])}",
                f"- Typography suggestions: {concept['typography_suggestions']}",
                f"- OpenAI image prompt: {concept.get('openai_image_prompt') or concept['image_prompt']}",
                f"- Commercial use notes: {concept['commercial_use_notes']}",
                "",
            ]
        )

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

    archive_json = output_dir / f"micah_design_prompts_{timestamp}.json"
    latest_json = output_dir / "micah_design_prompts_latest.json"
    archive_md = output_dir / f"micah_design_prompts_{timestamp}.md"
    latest_md = output_dir / "micah_design_prompts_latest.md"

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
    parser = argparse.ArgumentParser(description="Generate Micah Etsy-ready design prompts from Hunter opportunity JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Hunter opportunity JSON input path.")
    parser.add_argument("--count", type=int, default=10, help="Number of design concepts to generate. Default: 10.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for JSON and Markdown exports.")
    args = parser.parse_args()

    hunter_payload = load_hunter_opportunity_json(args.input)
    report = generate_design_prompt_report(hunter_payload, count=max(args.count, 1))
    exports = export_report(report, args.output_dir)

    print("MICAH DESIGN PROMPT ENGINE COMPLETE")
    print(f"Design concepts: {len(report['design_concepts'])}")
    print(f"JSON export: {exports['latest_json']}")
    print(f"Markdown report: {exports['latest_report']}")
    print("Approval note: Manny approval required before public listing, ad spend, or customer outreach.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
