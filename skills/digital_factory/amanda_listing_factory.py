"""Amanda Listing Factory.

Phase 4 of the RAMFAM KINGDOM Digital Asset Factory.
Converts one Design Gallery asset_metadata.json file into an Etsy-ready listing
package with listing copy, SEO tags, and social marketing captions.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METADATA_PATH = PROJECT_ROOT / "design_gallery" / "pending" / "faith_over_fear" / "asset_metadata.json"
OWNER_AGENT = "Amanda the Panda"
REQUIRED_DISCLAIMER = "This is a digital download.\nNo physical product will be shipped."
OUTPUT_FILENAMES = (
    "etsy_listing.txt",
    "seo_tags.txt",
    "marketing_copy.txt",
)

GENERIC_DIGITAL_TAGS = [
    "digital download",
    "printable art",
    "wall art",
    "svg png file",
    "instant download",
    "faith printable",
    "christian gift",
    "inspirational",
    "shirt design",
    "sticker design",
    "poster printable",
    "bible verse art",
    "ramfam kingdom",
]


def clean_title(raw: Any) -> str:
    return " ".join(str(raw or "").strip().split())


def slug_to_title(raw: str) -> str:
    words = re.sub(r"[^A-Za-z0-9]+", " ", raw).strip().split()
    return " ".join(word.capitalize() for word in words)


def truncate_text(text: str, limit: int) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip(" ,-|/") + "…"


def clean_tag(raw_tag: str) -> str:
    tag = re.sub(r"[^a-zA-Z0-9 &-]", "", raw_tag).lower().strip()
    tag = re.sub(r"\s+", " ", tag)
    if len(tag) <= 20:
        return tag
    shortened = ""
    for word in tag.split():
        candidate = f"{shortened} {word}".strip()
        if len(candidate) <= 20:
            shortened = candidate
    return shortened or tag[:20].rstrip()


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("asset_metadata.json must contain a JSON object.")
    return payload


def load_asset_metadata(metadata_path: Path | str) -> dict[str, Any]:
    path = Path(metadata_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Asset metadata file not found: {path}")
    metadata = load_json_object(path)
    asset_name = clean_title(metadata.get("asset_name"))
    if not asset_name:
        raise ValueError("asset_metadata.json must include asset_name.")
    metadata["asset_name"] = asset_name
    metadata["metadata_path"] = str(path)
    return metadata


def etsy_title(asset_name: str) -> str:
    return truncate_text(
        f"{asset_name} Digital Download, Faith SVG PNG Printable Art, Christian Inspirational Design",
        140,
    )


def shopify_title(asset_name: str) -> str:
    return truncate_text(f"{asset_name} Digital Download Artwork", 120)


def etsy_tags(asset_name: str) -> list[str]:
    name_words = [word for word in re.sub(r"[^A-Za-z0-9]+", " ", asset_name).lower().split() if word]
    candidates = [asset_name]
    if name_words:
        candidates.extend(
            [
                " ".join(name_words[:3]),
                f"{name_words[0]} design",
                f"{name_words[-1]} printable",
            ]
        )
    candidates.extend(GENERIC_DIGITAL_TAGS)

    tags: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        tag = clean_tag(candidate)
        if tag and tag not in seen:
            seen.add(tag)
            tags.append(tag)
        if len(tags) == 13:
            return tags

    filler_index = 1
    while len(tags) < 13:
        filler = clean_tag(f"digital art {filler_index}")
        if filler not in seen:
            seen.add(filler)
            tags.append(filler)
        filler_index += 1
    return tags


def usage_notes(asset_name: str) -> str:
    return "\n".join(
        [
            "Customer-Friendly Usage Notes:",
            f"- Download the {asset_name} files after purchase and save a backup copy.",
            "- Use the artwork for personal projects, gifts, apparel mockups, stickers, signs, framed prints, or approved small-business physical products.",
            "- Resize only from the included high-quality source files when possible so the final print stays sharp.",
            "- Colors may vary slightly by screen, printer, material, and production method.",
            "- Do not resell, redistribute, upload, share, or claim the digital files as your own standalone artwork.",
        ]
    )


def digital_download_disclaimer() -> str:
    return "\n".join(
        [
            "Digital Download Disclaimer:",
            REQUIRED_DISCLAIMER,
            "Because this is an instant digital product, review Etsy policies and contact SIS Custom Creations if you need help accessing the files.",
        ]
    )


def build_etsy_description(asset_name: str) -> str:
    return "\n".join(
        [
            "Product Overview:",
            f"Bring bold encouragement into your next creative project with this {asset_name} digital artwork package.",
            "",
            "This listing is prepared for customers who want a faith-forward design they can download and use quickly for personal projects, gifts, prints, apparel mockups, stickers, signs, and other approved physical finished goods.",
            "",
            "What You Receive:",
            "- Digital artwork files prepared from an approved RAMFAM Kingdom Design Gallery asset.",
            "- Marketplace-ready usage guidance for clear customer expectations.",
            "- Instant-download wording for Etsy listing compliance.",
            "",
            usage_notes(asset_name),
            "",
            digital_download_disclaimer(),
        ]
    )


def build_shopify_description(asset_name: str) -> str:
    return "\n".join(
        [
            f"The {asset_name} Digital Download Artwork package gives customers an uplifting faith-centered design for creative personal and small-business finished-product projects.",
            "",
            "Ideal for printable decor, apparel concepts, sticker projects, encouragement gifts, church event designs, and inspirational creative work.",
            "",
            usage_notes(asset_name),
            "",
            digital_download_disclaimer(),
        ]
    )


def product_faq(asset_name: str) -> str:
    return "\n".join(
        [
            "Product FAQ",
            "",
            "Q: Will I receive a physical product?",
            f"A: No. {REQUIRED_DISCLAIMER}",
            "",
            "Q: When do I receive my files?",
            "A: Files are available through the marketplace download flow after purchase, subject to the platform's normal processing time.",
            "",
            "Q: Can I use this for gifts or finished physical products?",
            f"A: Yes, the {asset_name} artwork is intended for personal projects, gifts, and approved finished physical products. Do not resell or redistribute the digital files themselves.",
            "",
            "Q: Can I edit the design?",
            "A: You may resize or adapt the files for your own project needs, but final quality depends on your software, printer, material, and production method.",
            "",
            "Q: What if I need help?",
            "A: Contact SIS Custom Creations through the marketplace message system with your order details and download question.",
        ]
    )


def marketing_copy(asset_name: str) -> str:
    return "\n".join(
        [
            "Facebook:",
            f"Faith over fear, purpose over pressure. The {asset_name} digital download is ready for prints, gifts, stickers, apparel concepts, and everyday encouragement.",
            "",
            "Instagram:",
            f"New digital design: {asset_name}. Download it, create with purpose, and keep encouragement close. #FaithOverFear #DigitalDownload #RAMFAMKingdom",
            "",
            "TikTok Caption:",
            f"Faith over fear energy. {asset_name} is ready as a digital download for your next creative project. #FaithOverFear #DigitalDesign",
            "",
            digital_download_disclaimer(),
        ]
    )


def build_listing_documents(metadata: dict[str, Any]) -> dict[str, str]:
    asset_name = metadata["asset_name"]
    tags = etsy_tags(asset_name)
    etsy_heading = etsy_title(asset_name)
    shopify_heading = shopify_title(asset_name)

    return {
        "etsy_listing.txt": "\n".join(
            [
                "Etsy Title:",
                etsy_heading,
                "",
                "Etsy Description:",
                build_etsy_description(asset_name),
                "",
                "13 Etsy Tags:",
                ", ".join(tags),
            ]
        )
        + "\n",
        "seo_tags.txt": "\n".join(["Etsy Tags (13):", *[f"{index}. {tag}" for index, tag in enumerate(tags, start=1)]]) + "\n",
        "marketing_copy.txt": marketing_copy(asset_name) + "\n",
    }


def build_listing_package(metadata_path: Path | str) -> dict[str, Any]:
    path = Path(metadata_path).resolve()
    metadata = load_asset_metadata(path)
    output_location = path.parent / "listing_package"
    output_location.mkdir(parents=True, exist_ok=True)

    documents = build_listing_documents(metadata)
    files_created: dict[str, str] = {}
    for filename in OUTPUT_FILENAMES:
        file_path = output_location / filename
        file_path.write_text(documents[filename], encoding="utf-8")
        files_created[filename] = str(file_path)

    return {
        "asset_id": metadata.get("asset_id") or re.sub(r"[^a-zA-Z0-9]+", "_", metadata["asset_name"].lower()).strip("_"),
        "asset_name": metadata["asset_name"],
        "metadata_path": str(path),
        "output_location": str(output_location),
        "files_created": files_created,
        "owner_agent": OWNER_AGENT,
        "factory_phase": "Phase 4 - Amanda Listing Factory",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build marketplace listing files from one Design Gallery asset_metadata.json file.")
    parser.add_argument("metadata_path", nargs="?", type=Path, default=DEFAULT_METADATA_PATH, help="Path to asset_metadata.json.")
    args = parser.parse_args()

    result = build_listing_package(args.metadata_path)
    print("AMANDA LISTING FACTORY BUILD COMPLETE")
    print(f"Asset: {result['asset_name']}")
    print(f"Output location: {result['output_location']}")
    print("Files created:")
    for filename, path in result["files_created"].items():
        print(f"- {filename}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
