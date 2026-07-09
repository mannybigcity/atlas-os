"""Commerce approval pipeline for internal Kingdom Gallery publication.

Design Decision A: "Published Digital" means internal Kingdom Gallery publication
only. This module updates local registry/metadata JSON and never publishes to
Etsy, Shopify, Printify, social media, customers, ads, payments, or any other
external channel.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

REGISTRY_FILENAME = "asset_registry.json"
INTERNAL_CHANNEL = "kingdom_gallery"
INTERNAL_PUBLICATION_SCOPE = "internal_kingdom_gallery_only"
PUBLISHED_DIGITAL_STATUS = "Published"
READY_STATUS = "Review Queue"
BLOCKED_EXTERNAL_CHANNELS = [
    "etsy",
    "shopify",
    "printify",
    "social_media",
    "customers",
    "ads",
    "payments",
]
EXTERNAL_SIDE_EFFECTS: list[str] = []


def load_json(path: Path, fallback: Any) -> Any:
    if not path.is_file():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return fallback


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n")


def registry_assets(registry_data: Any) -> list[dict[str, Any]]:
    if isinstance(registry_data, list):
        return [asset for asset in registry_data if isinstance(asset, dict)]
    if not isinstance(registry_data, dict):
        return []

    assets = registry_data.get("assets") or registry_data.get("asset_registry") or []
    if isinstance(assets, list):
        return [asset for asset in assets if isinstance(asset, dict)]
    if isinstance(assets, dict):
        normalized = []
        for asset_id, asset in assets.items():
            if isinstance(asset, dict):
                asset.setdefault("asset_id", str(asset_id))
                normalized.append(asset)
        return normalized
    return []


def find_registry_asset(registry_data: Any, asset_id: str) -> dict[str, Any] | None:
    target = str(asset_id)
    for asset in registry_assets(registry_data):
        candidate = str(asset.get("asset_id") or asset.get("id") or asset.get("asset_name") or "")
        if candidate == target:
            return asset
    return None


def metadata_path_for_asset(asset: dict[str, Any], gallery_root: Path) -> Path:
    file_locations = asset.get("file_locations") if isinstance(asset.get("file_locations"), dict) else {}
    metadata_path = file_locations.get("metadata")
    if metadata_path:
        return Path(metadata_path)

    file_location = asset.get("file_location") or asset.get("path") or asset.get("file_path") or ""
    if file_location and Path(str(file_location)).name == "asset_metadata.json":
        return Path(str(file_location))

    asset_id = str(asset.get("asset_id") or asset.get("id") or asset.get("asset_name") or "untracked-asset")
    safe_asset_id = asset_id.replace("/", "_").replace("\\", "_").strip() or "untracked-asset"
    return gallery_root / "pending" / safe_asset_id / "asset_metadata.json"


def load_metadata(asset: dict[str, Any], metadata_path: Path) -> dict[str, Any]:
    metadata = load_json(metadata_path, {})
    if isinstance(metadata, dict):
        return metadata
    return {
        "asset_id": asset.get("asset_id") or asset.get("id"),
        "asset_name": asset.get("asset_name") or asset.get("name"),
        "creator_agent": asset.get("creator_agent") or asset.get("agent") or asset.get("creator"),
        "creation_date": asset.get("creation_date") or asset.get("created_at") or asset.get("date"),
        "file_location": asset.get("file_location") or asset.get("path") or asset.get("file_path"),
    }


def _is_pending_review(asset: dict[str, Any]) -> bool:
    approval_status = str(asset.get("approval_status") or asset.get("status") or "").strip().lower()
    return "pending" in approval_status or "review" in approval_status


def _is_approved_unpublished(asset: dict[str, Any]) -> bool:
    approval_status = str(asset.get("approval_status") or asset.get("status") or "").strip().lower()
    marketplace_status = str(asset.get("marketplace_status") or asset.get("publishing_status") or "").strip().lower()
    return "approved" in approval_status and "published" not in marketplace_status and "rejected" not in marketplace_status


def status_update_for_action(asset: dict[str, Any], action: str, changed_at: str) -> dict[str, Any]:
    normalized_action = str(action).strip().lower().replace("-", "_")

    if normalized_action == "approve":
        if not _is_pending_review(asset):
            raise ValueError("Only queued results can be approved.")
        return {
            "approval_status": "Approved",
            "marketplace_status": READY_STATUS,
        }

    if normalized_action == "reject":
        if not _is_pending_review(asset):
            raise ValueError("Only queued results can be marked for revision.")
        return {
            "approval_status": "Rejected",
            "marketplace_status": "Review Queue",
        }

    if normalized_action == "publish_digital":
        if not _is_approved_unpublished(asset):
            raise ValueError("Only approved, unpublished assets can be published to the internal Kingdom Gallery.")
        return {
            "approval_status": "Approved",
            "marketplace_status": PUBLISHED_DIGITAL_STATUS,
            "publication_type": "digital",
            "publication_scope": INTERNAL_PUBLICATION_SCOPE,
            "channels": [INTERNAL_CHANNEL],
            "external_channels": [],
            "manual_approval_required": False,
            "manual_approval_scope": INTERNAL_PUBLICATION_SCOPE,
            "external_publication_blocked": True,
            "blocked_external_channels": BLOCKED_EXTERNAL_CHANNELS,
            "internal_publication": {
                "channel": INTERNAL_CHANNEL,
                "label": "Kingdom Gallery",
                "published_at": changed_at,
            },
        }

    if normalized_action in {"publish_physical", "publish_both"}:
        raise ValueError('"Published Digital" is internal Kingdom Gallery only; external publishing actions are blocked.')

    raise ValueError("Action must be approve, reject, or publish_digital.")


def persist_asset_update(
    gallery_root: Path,
    registry_data: Any,
    asset: dict[str, Any],
    status_update: dict[str, Any],
    changed_at: str,
) -> dict[str, Any]:
    asset.update(status_update)
    asset["updated_at"] = changed_at
    asset["last_status_change"] = changed_at

    metadata_path = metadata_path_for_asset(asset, gallery_root)
    metadata = load_metadata(asset, metadata_path)
    metadata.update(status_update)
    metadata.setdefault("asset_id", asset.get("asset_id") or asset.get("id"))
    metadata.setdefault("asset_name", asset.get("asset_name") or asset.get("name"))
    metadata["updated_at"] = changed_at
    metadata["last_status_change"] = changed_at

    file_locations = asset.get("file_locations") if isinstance(asset.get("file_locations"), dict) else {}
    file_locations["metadata"] = str(metadata_path)
    asset["file_locations"] = file_locations
    metadata_file_locations = metadata.get("file_locations") if isinstance(metadata.get("file_locations"), dict) else {}
    metadata_file_locations["metadata"] = str(metadata_path)
    metadata["file_locations"] = metadata_file_locations

    write_json(metadata_path, metadata)
    if isinstance(registry_data, dict):
        registry_data["updated_at"] = changed_at
    write_json(gallery_root / REGISTRY_FILENAME, registry_data)

    return {
        "success": True,
        "asset": asset,
        "metadata_path": str(metadata_path),
        "changed_at": changed_at,
        "external_side_effects": EXTERNAL_SIDE_EFFECTS,
        "external_publication_blocked": bool(asset.get("external_publication_blocked", False)),
        "blocked_external_channels": asset.get("blocked_external_channels", []),
    }


def apply_asset_action(asset_id: str, action: str, gallery_root: str | Path) -> dict[str, Any]:
    root = Path(gallery_root)
    registry_path = root / REGISTRY_FILENAME
    registry_data = load_json(registry_path, {"assets": []})
    asset = find_registry_asset(registry_data, asset_id)
    if asset is None:
        raise FileNotFoundError("Design Gallery asset not found.")

    changed_at = datetime.now().isoformat(timespec="seconds")
    status_update = status_update_for_action(asset, action, changed_at)
    return persist_asset_update(root, registry_data, asset, status_update, changed_at)


def approve_asset(asset_id: str, gallery_root: str | Path) -> dict[str, Any]:
    return apply_asset_action(asset_id, "approve", gallery_root)


def reject_asset(asset_id: str, gallery_root: str | Path) -> dict[str, Any]:
    return apply_asset_action(asset_id, "reject", gallery_root)


def publish_digital_asset(asset_id: str, gallery_root: str | Path) -> dict[str, Any]:
    return apply_asset_action(asset_id, "publish_digital", gallery_root)
