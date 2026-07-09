"""Deterministic Executive Memory Foundation for the Atlas Operating System.

This module extends the Atlas Knowledge Engine with a lightweight, file-backed
memory structure. It intentionally does not use AI services, vector databases,
or semantic search. The registry and routing functions are deterministic so
Atlas executives can locate only the memory they need for a mission.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRAIN_ROOT = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
DEFAULT_MEMORY_ROOT = BRAIN_ROOT / "99_MEMORY"

EXECUTIVE_MEMORY_DIR = "executive_memory"
COMPANY_MEMORY_DIR = "company_memory"
CLIENT_MEMORY_DIR = "client_memory"
MISSION_MEMORY_DIR = "mission_memory"
ARCHIVE_MEMORY_DIR = "archive_memory"
REGISTRY_FILE_NAME = "executive_memory_registry.json"

EXECUTIVE_OWNERSHIP: tuple[dict[str, str], ...] = (
    {
        "slug": "atlas",
        "display_name": "Atlas",
        "title": "Chief of Staff",
        "ownership": "Company strategy, executive coordination, priorities, accountability, and CEO-facing decisions.",
    },
    {
        "slug": "mason",
        "display_name": "Mason",
        "title": "Chief Technology Officer",
        "ownership": "Infrastructure, architecture, automation, integrations, technical implementation, and system reliability.",
    },
    {
        "slug": "hunter",
        "display_name": "Hunter",
        "title": "Revenue Commander",
        "ownership": "Revenue opportunities, market research, offer evaluation, and sales strategy lessons.",
    },
    {
        "slug": "micah",
        "display_name": "Micah",
        "title": "Marketing and Brand Executive",
        "ownership": "Marketing, content, campaigns, brand voice, and creative performance lessons.",
    },
    {
        "slug": "david",
        "display_name": "David",
        "title": "CRM and Automation Executive",
        "ownership": "CRM references, pipeline structure, automation patterns, and follow-up process memory.",
    },
    {
        "slug": "amanda",
        "display_name": "Amanda",
        "title": "Customer Experience and Marketplace Executive",
        "ownership": "Customer experience, listings, marketplace operations, and customer-facing draft lessons.",
    },
    {
        "slug": "gideon",
        "display_name": "Gideon",
        "title": "Finance and Profitability Executive",
        "ownership": "Pricing, profitability, financial controls, cash risk, and BI lessons.",
    },
    {
        "slug": "oracle",
        "display_name": "Oracle",
        "title": "Research and Strategy Executive",
        "ownership": "AI trends, strategic research, intelligence patterns, and future-facing recommendations.",
    },
    {
        "slug": "scout",
        "display_name": "Scout",
        "title": "Lead Research Executive",
        "ownership": "Prospecting, lead sources, opportunity records, and deterministic research notes.",
    },
    {
        "slug": "taylor",
        "display_name": "Taylor",
        "title": "Web and UX Executive",
        "ownership": "Websites, user experience, design systems, local assets, and website implementation memory.",
    },
    {
        "slug": "ranger",
        "display_name": "Ranger",
        "title": "Customer Success Executive",
        "ownership": "Retention, customer success, fulfillment communication, and relationship health lessons.",
    },
    {
        "slug": "lucky",
        "display_name": "Lucky",
        "title": "Media and Community Executive",
        "ownership": "Media, community, audio, personality, atmosphere, and audience engagement lessons.",
    },
    {
        "slug": "solomon",
        "display_name": "Solomon",
        "title": "Ethics and Compliance Executive",
        "ownership": "Ethics, compliance, legal-risk review, stewardship guardrails, and decision safeguards.",
    },
)

COMPANY_SECTIONS: tuple[str, ...] = (
    "constitution",
    "policies",
    "standard_operating_procedures",
    "products",
    "services",
    "pricing",
    "branding",
    "company_history",
)

CLIENT_SECTIONS: tuple[str, ...] = (
    "client_profiles",
    "crm_references",
    "communication_history",
    "project_references",
    "important_decisions",
    "client_files",
)

MISSION_STATES: tuple[str, ...] = (
    "active",
    "waiting",
    "completed",
    "archived",
)

ARCHIVE_SECTIONS: tuple[str, ...] = (
    "historical_decisions",
    "lessons_learned",
    "previous_implementations",
    "version_history",
)


class MemoryFoundationError(ValueError):
    """Raised when a deterministic memory request cannot be routed."""


def _normalize_slug(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _memory_root(memory_root: Path | str | None = None) -> Path:
    if memory_root is None:
        return DEFAULT_MEMORY_ROOT
    return Path(memory_root)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _write_json_if_missing(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _executive_index() -> dict[str, dict[str, str]]:
    return {executive["slug"]: dict(executive) for executive in EXECUTIVE_OWNERSHIP}


def build_registry(memory_root: Path | str | None = None) -> dict[str, Any]:
    """Build the deterministic Executive Memory Registry in memory."""
    root = _memory_root(memory_root)
    executive_base = root / EXECUTIVE_MEMORY_DIR
    executives: dict[str, dict[str, str]] = {}

    for executive in EXECUTIVE_OWNERSHIP:
        slug = executive["slug"]
        executive_dir = executive_base / slug
        memory_file = executive_dir / "memory.json"
        readme_file = executive_dir / "README.md"
        executives[slug] = {
            **executive,
            "memory_file": _relative(memory_file, root),
            "readme_file": _relative(readme_file, root),
            "load_policy": "load_only_when_owner_or_route_requires_it",
        }

    return {
        "registry_name": "Atlas Executive Memory Registry",
        "version": "1.0",
        "purpose": "Deterministic long-term operational memory for Atlas executives.",
        "knowledge_engine_extension": True,
        "uses_ai": False,
        "uses_vector_search": False,
        "uses_semantic_search": False,
        "executives": executives,
        "domains": {
            "executive": EXECUTIVE_MEMORY_DIR,
            "company": COMPANY_MEMORY_DIR,
            "client": CLIENT_MEMORY_DIR,
            "mission": MISSION_MEMORY_DIR,
            "archive": ARCHIVE_MEMORY_DIR,
        },
        "company_sections": list(COMPANY_SECTIONS),
        "client_sections": list(CLIENT_SECTIONS),
        "mission_states": list(MISSION_STATES),
        "archive_sections": list(ARCHIVE_SECTIONS),
    }


def initialize_memory_foundation(memory_root: Path | str | None = None) -> dict[str, Any]:
    """Create the persistent deterministic memory structure if missing."""
    root = _memory_root(memory_root)
    registry = build_registry(root)
    root.mkdir(parents=True, exist_ok=True)

    for slug, executive in registry["executives"].items():
        memory_file = root / executive["memory_file"]
        readme_file = root / executive["readme_file"]
        _write_json_if_missing(
            memory_file,
            {
                "owner": executive["display_name"],
                "slug": slug,
                "title": executive["title"],
                "ownership": executive["ownership"],
                "memory_type": "executive",
                "entries": [],
            },
        )
        _write_text_if_missing(
            readme_file,
            (
                f"# {executive['display_name']} Executive Memory\n\n"
                f"Owner: {executive['display_name']}\n\n"
                f"Title: {executive['title']}\n\n"
                f"Ownership: {executive['ownership']}\n\n"
                "This folder stores summarized long-term operational memory only. "
                "Do not store full conversations, secrets, raw CRM records, or unrelated executive memory here.\n"
            ),
        )

    for section in COMPANY_SECTIONS:
        _write_text_if_missing(
            root / COMPANY_MEMORY_DIR / section / "README.md",
            f"# Company Memory: {section.replace('_', ' ').title()}\n\nShared Atlas company memory for {section.replace('_', ' ')}.\n",
        )

    for section in CLIENT_SECTIONS:
        _write_text_if_missing(
            root / CLIENT_MEMORY_DIR / section / "README.md",
            f"# Client Memory: {section.replace('_', ' ').title()}\n\nArchitecture placeholder for client {section.replace('_', ' ')}. CRM functionality is intentionally not implemented here.\n",
        )

    for state in MISSION_STATES:
        _write_text_if_missing(
            root / MISSION_MEMORY_DIR / state / "README.md",
            f"# Mission Memory: {state.title()} Missions\n\nLightweight mission records in the {state} state. Load only this state when requested.\n",
        )

    for section in ARCHIVE_SECTIONS:
        _write_text_if_missing(
            root / ARCHIVE_MEMORY_DIR / section / "README.md",
            f"# Archive Memory: {section.replace('_', ' ').title()}\n\nLong-term archive storage for {section.replace('_', ' ')}. Not loaded unless explicitly requested.\n",
        )

    registry_file = root / EXECUTIVE_MEMORY_DIR / REGISTRY_FILE_NAME
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    registry_file.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return registry


def load_registry(memory_root: Path | str | None = None) -> dict[str, Any]:
    """Load the registry from disk, creating the foundation if missing."""
    root = _memory_root(memory_root)
    registry_file = root / EXECUTIVE_MEMORY_DIR / REGISTRY_FILE_NAME
    if not registry_file.exists():
        return initialize_memory_foundation(root)
    return json.loads(registry_file.read_text(encoding="utf-8"))


def get_executive_memory_location(executive: str, memory_root: Path | str | None = None) -> Path:
    """Return the JSON memory file for one executive."""
    root = _memory_root(memory_root)
    slug = _normalize_slug(executive)
    registry = load_registry(root)
    executives = registry["executives"]
    if slug not in executives:
        raise MemoryFoundationError(f"Unknown executive memory owner: {executive}")
    return root / executives[slug]["memory_file"]


def load_executive_memory(executive: str, memory_root: Path | str | None = None) -> dict[str, Any]:
    """Load one executive's deterministic memory file."""
    memory_file = get_executive_memory_location(executive, memory_root)
    if not memory_file.exists():
        initialize_memory_foundation(memory_root)
    return json.loads(memory_file.read_text(encoding="utf-8"))


def route_memory_request(domain: str, key: str, memory_root: Path | str | None = None) -> dict[str, Any]:
    """Route a deterministic memory request to a domain-specific path."""
    root = _memory_root(memory_root)
    initialize_memory_foundation(root)
    normalized_domain = _normalize_slug(domain)
    normalized_key = _normalize_slug(key)

    if normalized_domain == "executive":
        path = get_executive_memory_location(normalized_key, root)
        load_policy = "load_single_executive_memory"
    elif normalized_domain == "company":
        if normalized_key not in COMPANY_SECTIONS:
            raise MemoryFoundationError(f"Unknown company memory section: {key}")
        path = root / COMPANY_MEMORY_DIR / normalized_key
        load_policy = "load_only_requested_company_section"
    elif normalized_domain == "client":
        path = root / CLIENT_MEMORY_DIR / normalized_key
        path.mkdir(parents=True, exist_ok=True)
        load_policy = "load_only_requested_client_reference"
    elif normalized_domain == "mission":
        if normalized_key not in MISSION_STATES:
            raise MemoryFoundationError(f"Unknown mission memory state: {key}")
        path = root / MISSION_MEMORY_DIR / normalized_key
        load_policy = "load_only_requested_state"
    elif normalized_domain == "archive":
        if normalized_key not in ARCHIVE_SECTIONS:
            raise MemoryFoundationError(f"Unknown archive memory section: {key}")
        path = root / ARCHIVE_MEMORY_DIR / normalized_key
        load_policy = "load_only_explicit_archive_request"
    else:
        raise MemoryFoundationError(f"Unknown memory domain: {domain}")

    return {
        "domain": normalized_domain,
        "key": normalized_key,
        "path": _relative(path, root),
        "load_policy": load_policy,
        "uses_ai": False,
        "uses_vector_search": False,
        "uses_semantic_search": False,
    }


def build_memory_context(
    executives: Iterable[str] = (),
    company_sections: Iterable[str] = (),
    mission_states: Iterable[str] = (),
    memory_root: Path | str | None = None,
) -> dict[str, Any]:
    """Build a deterministic route list for the Knowledge Engine."""
    root = _memory_root(memory_root)
    routes: list[dict[str, Any]] = []
    for executive in executives:
        routes.append(route_memory_request("executive", executive, root))
    for section in company_sections:
        routes.append(route_memory_request("company", section, root))
    for state in mission_states:
        routes.append(route_memory_request("mission", state, root))

    return {
        "routes": routes,
        "route_count": len(routes),
        "external_ai_api_cost_usd": 0.0,
        "notes": "Deterministic file routing only; no AI, vector database, or semantic search required.",
    }


__all__ = [
    "ARCHIVE_SECTIONS",
    "CLIENT_SECTIONS",
    "COMPANY_SECTIONS",
    "DEFAULT_MEMORY_ROOT",
    "EXECUTIVE_OWNERSHIP",
    "MISSION_STATES",
    "MemoryFoundationError",
    "build_memory_context",
    "build_registry",
    "get_executive_memory_location",
    "initialize_memory_foundation",
    "load_executive_memory",
    "load_registry",
    "route_memory_request",
]


if __name__ == "__main__":
    print(json.dumps(initialize_memory_foundation(), indent=2, ensure_ascii=False))
