"""Commerce Pipeline Runner.

Runs the local commerce mission chain in order:
Hunter -> Micah -> Amanda -> Printify Draft Package.

The runner writes one complete mission folder containing every stage's JSON and
Markdown report plus a mission summary. It never publishes, creates live
Printify products, spends ad budget, contacts customers, or makes public
marketplace changes automatically.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skills.commerce import amanda_listing_engine as amanda
from skills.commerce import hunter_etsy_research as hunter
from skills.commerce import micah_design_prompt_engine as micah
from skills.commerce import printify_draft_package_engine as printify

BRAIN_DIR = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
DEFAULT_OUTPUT_ROOT = BRAIN_DIR / "06_MISSIONS" / "commerce_pipeline_runner"

PIPELINE_ORDER = ["Hunter", "Micah", "Amanda", "Printify Draft Package"]
MANNY_APPROVAL_REQUIREMENT = (
    "Manny approval is required before publishing listings, creating live Printify products, "
    "changing live pricing, ordering samples, spending ad budget, contacting customers, "
    "accepting custom orders, or making any public/reputation-impacting marketplace action."
)


def manny_approval_gates() -> dict[str, str]:
    return {
        "publish": "blocked_pending_manny_approval",
        "printify_live_creation": "blocked_pending_manny_approval",
        "pricing_change": "blocked_pending_manny_approval",
        "sample_order": "blocked_pending_manny_approval",
        "ad_spend": "blocked_pending_manny_approval",
        "customer_contact": "blocked_pending_manny_approval",
        "customer_commitment": "blocked_pending_manny_approval",
    }


def _new_mission_folder(output_root: Path, timestamp: str) -> Path:
    folder = output_root / f"commerce_pipeline_mission_{timestamp}"
    folder.mkdir(parents=True, exist_ok=False)
    return folder


def _stage_record(stage: str, exports: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "stage": stage,
        "status": "complete",
        "json_path": exports["latest_json"],
        "markdown_path": exports["latest_report"],
        "archive_json_path": exports["archive_json"],
        "archive_markdown_path": exports["archive_report"],
        "mission": payload.get("mission"),
        "generated_at": payload.get("generated_at"),
        "approval_required_before_public_action": bool(payload.get("approval_required_before_public_action", True)),
    }


def _mission_counts(
    hunter_report: dict[str, Any],
    micah_report: dict[str, Any],
    amanda_report: dict[str, Any],
    printify_report: dict[str, Any],
) -> dict[str, int]:
    return {
        "hunter_opportunities": len(hunter_report.get("opportunities", []) or []),
        "micah_design_concepts": len(micah_report.get("design_concepts", []) or []),
        "amanda_listing_packages": len(amanda_report.get("listing_packages", []) or []),
        "printify_draft_packages": len(printify_report.get("printify_draft_packages", []) or []),
    }


def build_mission_summary(
    mission_folder: Path,
    stages: dict[str, dict[str, Any]],
    counts: dict[str, int],
    hunter_report: dict[str, Any],
    printify_report: dict[str, Any],
) -> dict[str, Any]:
    top_opportunity = hunter_report.get("top_opportunity") or {}
    top_draft = printify_report.get("top_printify_draft_package") or {}
    return {
        "mission": "Commerce Pipeline Runner",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mission_folder": str(mission_folder),
        "pipeline_order": list(PIPELINE_ORDER),
        "agent_chain": {
            "assigned_by": "Atlas",
            "builder": "Mason",
            "revenue_owner": "Hunter",
            "design_owner": "Micah",
            "listing_owner": "Amanda",
            "draft_owner": "Mason",
            "approval_owner": "Manny",
        },
        "stages": stages,
        "counts": counts,
        "executive_summary": {
            "top_hunter_opportunity": top_opportunity.get("keyword"),
            "top_hunter_score": top_opportunity.get("opportunity_score"),
            "top_printify_draft": top_draft.get("title"),
            "top_printify_draft_id": top_draft.get("draft_id"),
        },
        "auto_publish_enabled": False,
        "actions_taken": [
            "Generated local Hunter opportunity research.",
            "Generated local Micah design prompt report.",
            "Generated local Amanda listing package report.",
            "Generated local Printify draft package report.",
            "Generated this local mission summary.",
        ],
        "actions_not_taken": [
            "No Etsy listing was published.",
            "No live Printify product was created or modified.",
            "No sample order was placed.",
            "No ad budget was spent.",
            "No customer was contacted or committed.",
        ],
        "approval_required_before_public_action": True,
        "manny_approval_requirement": MANNY_APPROVAL_REQUIREMENT,
        "manny_approval_gates": manny_approval_gates(),
    }


def build_markdown_report(summary: dict[str, Any]) -> str:
    counts = summary.get("counts", {})
    executive = summary.get("executive_summary", {})
    lines = [
        "# Commerce Pipeline Mission Report",
        "",
        f"Generated: {summary['generated_at']}",
        f"Mission folder: {summary['mission_folder']}",
        "Pipeline order: Hunter → Micah → Amanda → Printify Draft Package",
        "Assigned by: Atlas",
        "Built by: Mason",
        "Approval owner: Manny",
        "Auto-publish enabled: false",
        "No products were published automatically.",
        "",
        "## Executive Summary",
        "",
        f"- Top Hunter opportunity: {executive.get('top_hunter_opportunity') or 'Unavailable'} ({executive.get('top_hunter_score') or 0}/10)",
        f"- Top Printify draft: {executive.get('top_printify_draft') or 'Unavailable'}",
        f"- Top Printify draft ID: {executive.get('top_printify_draft_id') or 'Unavailable'}",
        "",
        "## Output Counts",
        "",
        f"- Hunter opportunities: {counts.get('hunter_opportunities', 0)}",
        f"- Micah design concepts: {counts.get('micah_design_concepts', 0)}",
        f"- Amanda listing packages: {counts.get('amanda_listing_packages', 0)}",
        f"- Printify draft packages: {counts.get('printify_draft_packages', 0)}",
        "",
        "## Stage Reports",
        "",
    ]

    for stage_name, stage in summary.get("stages", {}).items():
        lines.extend(
            [
                f"### {stage_name.title()}",
                "",
                f"- Status: {stage['status']}",
                f"- JSON: {stage['json_path']}",
                f"- Markdown: {stage['markdown_path']}",
                f"- Approval required before public action: {str(stage['approval_required_before_public_action']).lower()}",
                "",
            ]
        )

    lines.extend(["## Manny approval gates", ""])
    for gate, status in summary.get("manny_approval_gates", {}).items():
        lines.append(f"- {gate}: {status}")

    lines.extend(
        [
            "",
            "## Actions Not Taken",
            "",
        ]
    )
    lines.extend(f"- {action}" for action in summary.get("actions_not_taken", []))
    lines.extend(["", "## Approval Rule", "", summary["manny_approval_requirement"], ""])
    return "\n".join(lines)


def export_mission_summary(summary: dict[str, Any], mission_folder: Path) -> dict[str, str]:
    summary_json = mission_folder / "commerce_pipeline_mission_summary.json"
    summary_md = mission_folder / "commerce_pipeline_mission_summary.md"
    summary["exports"] = {
        "summary_json": str(summary_json),
        "summary_report": str(summary_md),
    }
    json_text = json.dumps(summary, indent=2, ensure_ascii=False)
    markdown = build_markdown_report(summary)
    summary_json.write_text(json_text, encoding="utf-8")
    summary_md.write_text(markdown, encoding="utf-8")
    return dict(summary["exports"])


def run_commerce_pipeline(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    keywords: list[str] | None = None,
    hunter_limit: int = 25,
    design_count: int = 10,
    listing_count: int | None = None,
    draft_count: int | None = None,
    use_etsy_api: bool = True,
) -> dict[str, Any]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mission_folder = _new_mission_folder(output_root, timestamp)

    hunter_dir = mission_folder / "01_hunter_etsy_research"
    micah_dir = mission_folder / "02_micah_design_prompt_engine"
    amanda_dir = mission_folder / "03_amanda_listing_engine"
    printify_dir = mission_folder / "04_printify_draft_package_engine"

    hunter_keywords = keywords or hunter.DEFAULT_KEYWORDS
    hunter_report = hunter.research_keywords(hunter_keywords, max(hunter_limit, 1), use_api=use_etsy_api)
    hunter_exports = hunter.export_report(hunter_report, hunter_dir)

    micah_report = micah.generate_design_prompt_report(hunter_report, count=max(design_count, 1))
    micah_exports = micah.export_report(micah_report, micah_dir)

    amanda_report = amanda.generate_listing_report(hunter_report, micah_report, count=listing_count)
    amanda_exports = amanda.export_report(amanda_report, amanda_dir)

    printify_report = printify.generate_printify_draft_report(amanda_report, count=draft_count)
    printify_exports = printify.export_report(printify_report, printify_dir)

    stages = {
        "hunter": _stage_record("Hunter", hunter_exports, hunter_report),
        "micah": _stage_record("Micah", micah_exports, micah_report),
        "amanda": _stage_record("Amanda", amanda_exports, amanda_report),
        "printify": _stage_record("Printify Draft Package", printify_exports, printify_report),
    }
    counts = _mission_counts(hunter_report, micah_report, amanda_report, printify_report)
    summary = build_mission_summary(mission_folder, stages, counts, hunter_report, printify_report)
    export_mission_summary(summary, mission_folder)
    return summary


def parse_keywords(raw_keywords: str | None) -> list[str] | None:
    if not raw_keywords:
        return None
    parsed = [keyword.strip() for keyword in raw_keywords.split(",") if keyword.strip()]
    return parsed or None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full RAMFAM commerce pipeline into one approval-ready mission folder.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="Root directory where a timestamped mission folder will be created.")
    parser.add_argument("--keywords", help="Comma-separated Etsy keywords for Hunter. Defaults to Hunter's built-in keyword list.")
    parser.add_argument("--hunter-limit", type=int, default=25, help="Listings sampled per keyword. Default: 25.")
    parser.add_argument("--design-count", type=int, default=10, help="Micah design concepts to generate. Default: 10.")
    parser.add_argument("--listing-count", type=int, help="Amanda listing packages to generate. Defaults to all Micah concepts.")
    parser.add_argument("--draft-count", type=int, help="Printify draft packages to generate. Defaults to all Amanda packages.")
    parser.add_argument("--no-api", action="store_true", help="Skip Etsy API and use Hunter offline seed research data.")
    args = parser.parse_args()

    summary = run_commerce_pipeline(
        output_root=args.output_root,
        keywords=parse_keywords(args.keywords),
        hunter_limit=args.hunter_limit,
        design_count=args.design_count,
        listing_count=args.listing_count,
        draft_count=args.draft_count,
        use_etsy_api=not args.no_api,
    )

    print("COMMERCE PIPELINE RUNNER COMPLETE")
    print(f"Mission folder: {summary['mission_folder']}")
    print(f"Summary JSON: {summary['exports']['summary_json']}")
    print(f"Summary Markdown: {summary['exports']['summary_report']}")
    print("Pipeline order: Hunter -> Micah -> Amanda -> Printify Draft Package")
    print("Approval note: Manny approval required before publishing, live Printify creation, ad spend, sample orders, customer contact, or customer commitments.")
    print("No products were published automatically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
