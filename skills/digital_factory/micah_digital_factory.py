"""Micah Digital Factory.

Phase 3 of the RAMFAM KINGDOM Digital Asset Factory.
Converts one approved opportunity name into a complete pending Design Gallery asset package.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_GALLERY_ROOT = PROJECT_ROOT / "design_gallery"
PENDING_DIRNAME = "pending"
REGISTRY_FILENAME = "asset_registry.json"
REVENUE_FILENAME = "revenue_tracking.json"
CREATOR_AGENT = "Micah the Fox"


def slug_text(raw: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", raw.strip().lower()).strip("_")
    return slug or "digital_asset"


def title_text(raw: str) -> str:
    return " ".join(str(raw or "").strip().split()) or "Untitled Opportunity"


def build_svg(asset_name: str) -> str:
    safe_name = escape(asset_name)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200" role="img" aria-label="{safe_name} digital asset">
  <defs>
    <radialGradient id="kingdomGlow" cx="50%" cy="38%" r="70%">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.34"/>
      <stop offset="45%" stop-color="#1e1b4b" stop-opacity="0.92"/>
      <stop offset="100%" stop-color="#020617"/>
    </radialGradient>
    <linearGradient id="gold" x1="0%" x2="100%">
      <stop offset="0%" stop-color="#fef3c7"/>
      <stop offset="50%" stop-color="#e5b95c"/>
      <stop offset="100%" stop-color="#92400e"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="1200" fill="url(#kingdomGlow)"/>
  <circle cx="600" cy="600" r="418" fill="none" stroke="#00e5ff" stroke-opacity="0.24" stroke-width="16"/>
  <path d="M600 180 L888 314 L816 850 L600 1018 L384 850 L312 314 Z" fill="#0f172a" fill-opacity="0.72" stroke="url(#gold)" stroke-width="18"/>
  <path d="M560 330 H640 V540 H815 V620 H640 V890 H560 V620 H385 V540 H560 Z" fill="url(#gold)"/>
  <text x="600" y="976" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="78" font-weight="900" fill="#f8fafc" letter-spacing="4">{safe_name}</text>
  <text x="600" y="1060" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="32" font-weight="700" fill="#67e8f9" letter-spacing="6">RAMFAM KINGDOM DIGITAL ASSET FACTORY</text>
</svg>
'''


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return struct.pack("!I", len(data)) + chunk_type + data + struct.pack("!I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)


def build_png_bytes(width: int = 512, height: int = 512) -> bytes:
    rows = []
    center_x = width // 2
    center_y = height // 2
    for y in range(height):
        row = bytearray()
        row.append(0)
        for x in range(width):
            dx = abs(x - center_x)
            dy = abs(y - center_y)
            in_shield = (120 < y < 440) and (dx < 145 - max(0, y - 250) // 3)
            in_cross = (236 <= x <= 276 and 150 <= y <= 385) or (160 <= x <= 352 and 230 <= y <= 270)
            border = abs(dx + max(0, y - 240) // 3 - 145) < 4 and 120 < y < 440
            if in_cross:
                rgb = (229, 185, 92)
            elif border:
                rgb = (103, 232, 249)
            elif in_shield:
                rgb = (15, 23, 42)
            else:
                glow = max(0, 120 - int(((x - center_x) ** 2 + (y - 190) ** 2) ** 0.5))
                rgb = (2 + glow // 8, 6 + glow // 5, 23 + glow // 3)
            row.extend(rgb)
        rows.append(bytes(row))
    raw = b"".join(rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _png_chunk(b"IDAT", zlib.compress(raw, 9))
    png += _png_chunk(b"IEND", b"")
    return png


def build_prompt(asset_name: str) -> str:
    return "\n".join(
        [
            f"Opportunity Name: {asset_name}",
            "Creator Agent: Micah the Fox",
            "",
            "Create an original, commercially safe RAMFAM Kingdom digital product design inspired by this approved opportunity.",
            "Style: bold faith-centered apparel graphic, premium print-on-demand composition, high contrast, clean typography, no copyrighted characters, no brand logos.",
            "Deliverable intent: SVG master art, PNG gallery preview, listing support notes, and pending approval metadata.",
            "Approval status: Pending Approval before marketplace publishing.",
        ]
    )


def build_listing_notes(asset_name: str) -> str:
    return "\n".join(
        [
            f"Listing Notes: {asset_name}",
            "",
            "Draft title angle: Faith-forward encouragement design for apparel, stickers, posters, and digital downloads.",
            "Customer promise: uplifting original artwork prepared for review before any public marketplace action.",
            "SEO seeds: faith apparel, inspirational shirt, Christian encouragement, kingdom family gift, positive message design.",
            "Production guard: verify artwork, spelling, trademark safety, pricing, fulfillment, and Manny approval before publishing.",
            "Marketplace status: Draft.",
        ]
    )


def load_json_object(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(fallback)
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return dict(fallback)
    return payload if isinstance(payload, dict) else dict(fallback)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def registry_assets(registry: dict[str, Any]) -> list[dict[str, Any]]:
    assets = registry.get("assets")
    if isinstance(assets, list):
        return [asset for asset in assets if isinstance(asset, dict)]
    if isinstance(assets, dict):
        return [dict({"asset_id": asset_id}, **asset) for asset_id, asset in assets.items() if isinstance(asset, dict)]
    return []


def register_asset(gallery_root: Path, registry_entry: dict[str, Any], revenue: float = 0) -> None:
    registry_path = gallery_root / REGISTRY_FILENAME
    registry = load_json_object(
        registry_path,
        {"factory": "RAMFAM KINGDOM Digital Asset Factory", "phase": "Phase 3 - Micah Digital Factory", "assets": []},
    )
    assets = registry_assets(registry)
    asset_id = registry_entry["asset_id"]
    assets = [asset for asset in assets if asset.get("asset_id") != asset_id]
    assets.append(registry_entry)
    registry["factory"] = registry.get("factory") or "RAMFAM KINGDOM Digital Asset Factory"
    registry["phase"] = "Phase 3 - Micah Digital Factory"
    registry["updated_at"] = datetime.now().date().isoformat()
    registry["assets"] = assets
    write_json(registry_path, registry)

    revenue_path = gallery_root / REVENUE_FILENAME
    revenue_payload = load_json_object(revenue_path, {"factory": "RAMFAM KINGDOM Digital Asset Factory", "assets": {}})
    revenue_assets = revenue_payload.get("assets")
    if not isinstance(revenue_assets, dict):
        revenue_assets = {}
    revenue_assets.setdefault(
        asset_id,
        {"total_revenue": float(revenue), "units_sold": 0, "profit": 0, "is_top_seller": False},
    )
    revenue_payload["factory"] = revenue_payload.get("factory") or "RAMFAM KINGDOM Digital Asset Factory"
    revenue_payload["updated_at"] = datetime.now().date().isoformat()
    revenue_payload["assets"] = revenue_assets
    write_json(revenue_path, revenue_payload)


def build_asset_package(opportunity_name: str, gallery_root: Path | str = DEFAULT_GALLERY_ROOT) -> dict[str, Any]:
    asset_name = title_text(opportunity_name)
    asset_id = slug_text(asset_name)
    root = Path(gallery_root)
    opportunity_folder = root / PENDING_DIRNAME / asset_id
    opportunity_folder.mkdir(parents=True, exist_ok=True)

    svg_path = opportunity_folder / f"{asset_id}.svg"
    png_path = opportunity_folder / f"{asset_id}.png"
    prompt_path = opportunity_folder / f"{asset_id}_prompt.txt"
    listing_notes_path = opportunity_folder / "listing_notes.txt"
    metadata_path = opportunity_folder / "asset_metadata.json"
    created_at = datetime.now().isoformat(timespec="seconds")
    creation_date = datetime.now().date().isoformat()

    file_locations = {
        "svg": str(svg_path),
        "png": str(png_path),
        "prompt": str(prompt_path),
        "listing_notes": str(listing_notes_path),
        "metadata": str(metadata_path),
    }
    preview_url = f"/design-gallery/pending/{asset_id}/{asset_id}.png"
    metadata = {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "creator_agent": CREATOR_AGENT,
        "date_created": created_at,
        "creation_date": creation_date,
        "approval_status": "Pending Approval",
        "marketplace_status": "Draft",
        "revenue": 0,
        "file_locations": file_locations,
        "output_location": str(opportunity_folder),
        "factory_phase": "Phase 3 - Micah Digital Factory",
    }

    svg_path.write_text(build_svg(asset_name), encoding="utf-8")
    png_path.write_bytes(build_png_bytes())
    prompt_path.write_text(build_prompt(asset_name), encoding="utf-8")
    listing_notes_path.write_text(build_listing_notes(asset_name), encoding="utf-8")
    write_json(metadata_path, metadata)

    registry_entry = {
        "asset_id": asset_id,
        "asset_preview": preview_url,
        "asset_name": asset_name,
        "creator_agent": CREATOR_AGENT,
        "creation_date": creation_date,
        "date_created": created_at,
        "approval_status": "Pending Approval",
        "marketplace_status": "Draft",
        "revenue": 0,
        "file_location": str(metadata_path),
        "file_locations": file_locations,
    }
    register_asset(root, registry_entry, revenue=0)

    return {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "opportunity_folder": str(opportunity_folder),
        "files_created": file_locations,
        "registry": str(root / REGISTRY_FILENAME),
        "metadata": metadata,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a pending Design Gallery asset package from one approved opportunity name.")
    parser.add_argument("opportunity_name", nargs="?", default="Faith Over Fear", help="Approved opportunity name to package.")
    parser.add_argument("--gallery-root", type=Path, default=DEFAULT_GALLERY_ROOT, help="Design Gallery root directory.")
    args = parser.parse_args()

    result = build_asset_package(args.opportunity_name, args.gallery_root)
    print("MICAH DIGITAL FACTORY BUILD COMPLETE")
    print(f"Asset: {result['asset_name']}")
    print(f"Opportunity folder: {result['opportunity_folder']}")
    print("Files created:")
    for label, path in result["files_created"].items():
        print(f"- {label}: {path}")
    print(f"Registered in: {result['registry']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
