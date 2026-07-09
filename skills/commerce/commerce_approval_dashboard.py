"""Commerce Kingdom Review Queue.

Builds a local, static HTML approval dashboard from the latest commerce pipeline
mission folder. Internal Kingdom work is auto-authorized when Manny issues the
command; this dashboard reviews completed results after execution. It never
publishes, creates live Printify products, spends money, contacts customers, or
makes marketplace changes without manual approval.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BRAIN_DIR = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
DEFAULT_PIPELINE_ROOT = BRAIN_DIR / "06_MISSIONS" / "commerce_pipeline_runner"
DASHBOARD_FILENAME = "commerce_approval_dashboard.html"
DECISIONS_FILENAME = "commerce_approval_decisions.json"

INTERNAL_AUTO_EXECUTE_WORK_TYPES = [
    "bug_fixes",
    "reports",
    "research",
    "asset_creation",
    "code_generation",
    "ui_improvements",
    "verification",
    "testing",
    "internal_refactoring",
    "dashboard_improvements",
]

MANUAL_APPROVAL_REQUIRED_ACTIONS = [
    "customer_contact",
    "invoices",
    "emails",
    "publishing_to_etsy",
    "publishing_to_shopify",
    "money_movement",
    "deleting_files",
    "external_actions",
]

MANNY_APPROVAL_REQUIREMENT = (
    "Manny approval is required only before customer contact, invoices, emails, "
    "publishing to Etsy or Shopify, money movement, deleting files, or any other external action. "
    "Internal Kingdom work runs automatically when Manny commands it; Manny reviews completed results."
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def latest_mission_folder(pipeline_root: Path = DEFAULT_PIPELINE_ROOT) -> Path:
    if not pipeline_root.exists():
        raise FileNotFoundError(f"Commerce pipeline root not found: {pipeline_root}")
    candidates = [path for path in pipeline_root.iterdir() if path.is_dir() and path.name.startswith("commerce_pipeline_mission_")]
    if not candidates:
        raise FileNotFoundError(f"No commerce pipeline mission folders found under {pipeline_root}")
    return max(candidates, key=lambda path: path.name)


def _stage_json_path(summary: dict[str, Any], stage_name: str, mission_folder: Path) -> Path:
    stages = summary.get("stages", {}) or {}
    stage = stages.get(stage_name, {}) or {}
    raw_path = stage.get("json_path")
    if raw_path:
        return Path(raw_path)

    fallback_names = {
        "hunter": mission_folder / "01_hunter_etsy_research" / "hunter_etsy_research_latest.json",
        "micah": mission_folder / "02_micah_design_prompt_engine" / "micah_design_prompts_latest.json",
        "amanda": mission_folder / "03_amanda_listing_engine" / "amanda_listing_packages_latest.json",
        "printify": mission_folder / "04_printify_draft_package_engine" / "printify_draft_packages_latest.json",
    }
    return fallback_names[stage_name]


def load_mission_payloads(mission_folder: Path) -> dict[str, dict[str, Any]]:
    summary_path = mission_folder / "commerce_pipeline_mission_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Commerce pipeline summary not found: {summary_path}")

    summary = load_json(summary_path)
    payloads = {"summary": summary}
    for stage_name in ("hunter", "micah", "amanda", "printify"):
        stage_path = _stage_json_path(summary, stage_name, mission_folder)
        if not stage_path.exists():
            raise FileNotFoundError(f"{stage_name.title()} stage JSON not found: {stage_path}")
        payloads[stage_name] = load_json(stage_path)
    return payloads


def _approval_item(item_id: str, title: str, source_agent: str, summary: str, details: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "title": title,
        "source_agent": source_agent,
        "summary": summary,
        "status": "pending_result_review",
        "authorization_status": "auto_executed_from_manny_command",
        "review_type": "approve_results_not_work",
        "approved_by": "",
        "reviewed_at": "",
        "rejection_reason": "",
        "notes": "",
        "approval_guard": MANNY_APPROVAL_REQUIREMENT,
        "manual_approval_required_only_for": MANUAL_APPROVAL_REQUIRED_ACTIONS,
        "details": details,
    }


def build_approval_decisions(mission_folder: Path, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    hunter_opportunities = []
    for index, opportunity in enumerate(payloads["hunter"].get("opportunities", []) or [], start=1):
        keyword = str(opportunity.get("keyword") or f"opportunity-{index}")
        hunter_opportunities.append(
            _approval_item(
                item_id=f"hunter-{index:02d}",
                title=keyword,
                source_agent="Hunter",
                summary=str(opportunity.get("recommended_offer") or "Hunter opportunity review required."),
                details={
                    "opportunity_score": opportunity.get("opportunity_score"),
                    "demand_signal": opportunity.get("demand_signal"),
                    "competition_level": opportunity.get("competition_level"),
                    "mission_fit": opportunity.get("mission_fit"),
                },
            )
        )

    micah_designs = []
    for index, design in enumerate(payloads["micah"].get("design_concepts", []) or [], start=1):
        micah_designs.append(
            _approval_item(
                item_id=f"micah-{index:02d}",
                title=str(design.get("design_title") or f"Micah design {index}"),
                source_agent="Micah",
                summary=str(design.get("design_concept") or "Micah design review required."),
                details={
                    "source_keyword": design.get("source_keyword"),
                    "source_opportunity_score": design.get("source_opportunity_score"),
                    "image_prompt": design.get("image_prompt") or design.get("openai_image_prompt"),
                },
            )
        )

    amanda_listings = []
    for index, listing in enumerate(payloads["amanda"].get("listing_packages", []) or [], start=1):
        pricing = listing.get("pricing_suggestion", {}) or {}
        amanda_listings.append(
            _approval_item(
                item_id=f"amanda-{index:02d}",
                title=str(listing.get("product_title") or f"Amanda listing {index}"),
                source_agent="Amanda",
                summary=str(listing.get("description") or "Amanda listing package review required.")[:500],
                details={
                    "source_keyword": listing.get("source_keyword"),
                    "source_design_title": listing.get("source_design_title"),
                    "anchor_price": pricing.get("anchor_price"),
                    "suggested_price_range": pricing.get("suggested_price_range"),
                    "tags": listing.get("etsy_tags", []),
                },
            )
        )

    printify_drafts = []
    for index, draft in enumerate(payloads["printify"].get("printify_draft_packages", []) or [], start=1):
        recommendation = draft.get("product_type_recommendation", {}) or {}
        pricing = draft.get("pricing_math", {}) or {}
        draft_payload = draft.get("printify_draft_payload", {}) or {}
        printify_drafts.append(
            _approval_item(
                item_id=str(draft.get("draft_id") or f"printify-{index:02d}"),
                title=str(draft.get("title") or f"Printify draft {index}"),
                source_agent="Printify Draft Package",
                summary=str(recommendation.get("recommended_blank") or "Printify draft package review required."),
                details={
                    "product_type": recommendation.get("product_type"),
                    "retail_price": pricing.get("retail_price"),
                    "estimated_profit": pricing.get("estimated_profit"),
                    "visible": draft_payload.get("visible"),
                    "publish_action": draft_payload.get("publish_action"),
                },
            )
        )

    review_queue = {
        "hunter_opportunities": hunter_opportunities,
        "micah_designs": micah_designs,
        "amanda_listings": amanda_listings,
        "printify_draft_packages": printify_drafts,
    }
    return {
        "mission": "Commerce Kingdom Review Queue",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mission_folder": str(mission_folder),
        "source_summary_json": str(mission_folder / "commerce_pipeline_mission_summary.json"),
        "workflow": "auto_execute_internal_work_review_results_after_completion",
        "approval_target": "results_not_work",
        "internal_work_auto_authorized": True,
        "internal_auto_execute_work_types": INTERNAL_AUTO_EXECUTE_WORK_TYPES,
        "auto_publish_enabled": False,
        "manny_approval_guard": {
            "internal_work_blocked_pending_approval": False,
            "public_actions_blocked_until_manny_approval": True,
            "manual_approval_required_actions": MANUAL_APPROVAL_REQUIRED_ACTIONS,
            "publish_action": "blocked_pending_manny_approval",
            "printify_live_creation": "blocked_pending_manny_approval",
            "pricing_change": "blocked_pending_manny_approval",
            "sample_order": "blocked_pending_manny_approval",
            "ad_spend": "blocked_pending_manny_approval",
            "customer_contact": "blocked_pending_manny_approval",
            "customer_commitment": "blocked_pending_manny_approval",
            "requirement": MANNY_APPROVAL_REQUIREMENT,
        },
        "counts": {key: len(value) for key, value in review_queue.items()},
        "review_queue": review_queue,
        "approval_decisions": review_queue,
    }


def _esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _render_detail_list(details: dict[str, Any]) -> str:
    rows = []
    for key, value in details.items():
        if value in (None, "", []):
            continue
        if isinstance(value, list):
            rendered = ", ".join(_esc(item) for item in value[:13])
        else:
            rendered = _esc(value)
        rows.append(f"<li><strong>{_esc(key.replace('_', ' ').title())}:</strong> {rendered}</li>")
    return "\n".join(rows)


def _render_card(category: str, item: dict[str, Any]) -> str:
    item_id = _esc(item["item_id"])
    title = _esc(item["title"])
    summary = _esc(item["summary"])
    source_agent = _esc(item["source_agent"])
    details = _render_detail_list(item.get("details", {}) or {})
    return f"""
      <article class="approval-card" data-category="{_esc(category)}" data-item-id="{item_id}" data-title="{title}" data-source-agent="{source_agent}">
        <div class="card-header">
          <div>
            <p class="eyebrow">{source_agent}</p>
            <h3>{title}</h3>
          </div>
          <label>Status
            <select class="decision-status" name="{item_id}-status">
              <option value="pending_result_review" selected>Pending Result Review</option>
              <option value="result_approved">Result Approved</option>
              <option value="needs_revision">Needs Revision</option>
              <option value="manual_external_approval_required">Manual External Approval Required</option>
            </select>
          </label>
        </div>
        <p>{summary}</p>
        <ul>{details}</ul>
        <div class="review-grid">
          <label>Reviewed by<input class="reviewed-by" type="text" placeholder="Manny" /></label>
          <label>Notes<textarea class="decision-notes" placeholder="Result review notes, conditions, or next action"></textarea></label>
          <label>Revision reason<textarea class="rejection-reason" placeholder="Required if needs revision"></textarea></label>
        </div>
      </article>
"""


def _render_section(title: str, category: str, items: list[dict[str, Any]]) -> str:
    cards = "\n".join(_render_card(category, item) for item in items) or "<p>No items found for this stage.</p>"
    return f"""
    <section>
      <h2>{_esc(title)}</h2>
      {cards}
    </section>
"""


def build_dashboard_html(decisions: dict[str, Any]) -> str:
    approval_decisions = decisions.get("review_queue", {}) or decisions.get("approval_decisions", {}) or {}
    decisions_json = json.dumps(decisions, indent=2, ensure_ascii=False)
    sections = "\n".join(
        [
            _render_section("Hunter Opportunity", "hunter_opportunities", approval_decisions.get("hunter_opportunities", [])),
            _render_section("Micah Designs", "micah_designs", approval_decisions.get("micah_designs", [])),
            _render_section("Amanda Listings", "amanda_listings", approval_decisions.get("amanda_listings", [])),
            _render_section("Printify Draft Packages", "printify_draft_packages", approval_decisions.get("printify_draft_packages", [])),
        ]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Commerce Kingdom Review Queue</title>
  <style>
    :root {{ color-scheme: dark; --bg:#101418; --panel:#182028; --card:#202a34; --text:#f7f1e8; --muted:#b8c0c8; --gold:#e5b95c; --danger:#ff7777; --ok:#78d38b; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
    header, main, footer {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    header {{ border-bottom: 1px solid #2c3946; }}
    h1 {{ margin: 0 0 8px; color: var(--gold); }}
    h2 {{ margin-top: 32px; border-bottom: 1px solid #31404f; padding-bottom: 8px; }}
    h3 {{ margin: 0; }}
    .guard {{ background: #2a1d1d; border: 1px solid var(--danger); border-radius: 12px; padding: 16px; margin-top: 16px; }}
    .workflow {{ background: #152719; border: 1px solid var(--ok); border-radius: 12px; padding: 16px; margin-top: 16px; }}
    .approval-card {{ background: var(--card); border: 1px solid #31404f; border-radius: 12px; margin: 16px 0; padding: 16px; }}
    .card-header {{ display: flex; gap: 16px; justify-content: space-between; align-items: start; flex-wrap: wrap; }}
    .eyebrow {{ color: var(--gold); font-size: 0.78rem; margin: 0 0 4px; text-transform: uppercase; letter-spacing: .08em; }}
    select, input, textarea, button {{ width: 100%; margin-top: 6px; border: 1px solid #44576a; border-radius: 8px; background: #111820; color: var(--text); padding: 10px; }}
    select {{ min-width: 220px; }}
    textarea {{ min-height: 80px; }}
    label {{ color: var(--muted); font-weight: 700; }}
    .review-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 12px; }}
    .actions {{ position: sticky; bottom: 0; background: rgba(16,20,24,.95); border-top: 1px solid #31404f; padding: 16px 0; }}
    button {{ cursor: pointer; background: var(--gold); color: #17120a; border: 0; font-weight: 800; }}
    pre {{ white-space: pre-wrap; background: #0b0f13; border: 1px solid #31404f; border-radius: 12px; padding: 16px; overflow: auto; }}
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">Atlas assigned Mason</p>
    <h1>Commerce Kingdom Review Queue</h1>
    <p>Mission folder: <code>{_esc(decisions.get('mission_folder'))}</code></p>
    <div class="workflow">
      <h2>New Workflow: Auto-Execute Internal Work</h2>
      <p>If Manny issues a command, internal Kingdom work is automatically authorized. Results land here after completion for review.</p>
      <p><strong>Approve results, not work.</strong> Auto-execute covers bug fixes, reports, research, asset creation, code generation, UI improvements, verification, testing, internal refactoring, and dashboard improvements.</p>
    </div>
    <div class="guard">
      <h2>Manual Approval Guard</h2>
      <p>Manual approval is required only for customer contact, invoices, emails, Etsy publishing, Shopify publishing, money movement, deleting files, or external actions.</p>
      <p>{_esc(MANNY_APPROVAL_REQUIREMENT)}</p>
    </div>
  </header>
  <main>
    {sections}
    <div class="actions">
      <button type="button" onclick="exportDecisions()">Export Review Queue JSON</button>
    </div>
    <h2>Initial JSON Export</h2>
    <pre id="initial-json">{_esc(decisions_json)}</pre>
  </main>
  <footer>
    <p>Local review dashboard only. Auto-publish enabled: false.</p>
  </footer>
  <script id="base-decisions" type="application/json">{_esc(decisions_json)}</script>
  <script>
    function exportDecisions() {{
      const base = JSON.parse(document.getElementById('base-decisions').textContent);
      const reviewedAt = new Date().toISOString();
      document.querySelectorAll('.approval-card').forEach((card) => {{
        const category = card.dataset.category;
        const itemId = card.dataset.itemId;
        const target = base.approval_decisions[category].find((item) => item.item_id === itemId);
        if (!target) return;
        target.status = card.querySelector('.decision-status').value;
        target.approved_by = card.querySelector('.reviewed-by').value;
        target.notes = card.querySelector('.decision-notes').value;
        target.rejection_reason = card.querySelector('.rejection-reason').value;
        target.reviewed_at = target.status === 'pending_result_review' ? '' : reviewedAt;
      }});
      base.exported_at = reviewedAt;
      base.auto_publish_enabled = false;
      const blob = new Blob([JSON.stringify(base, null, 2)], {{ type: 'application/json' }});
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = '{DECISIONS_FILENAME}';
      link.click();
      URL.revokeObjectURL(link.href);
    }}
  </script>
</body>
</html>
"""


def export_dashboard(mission_folder: Path, payloads: dict[str, dict[str, Any]]) -> dict[str, str]:
    decisions = build_approval_decisions(mission_folder, payloads)
    html_text = build_dashboard_html(decisions)

    dashboard_path = mission_folder / DASHBOARD_FILENAME
    decisions_path = mission_folder / DECISIONS_FILENAME
    dashboard_path.write_text(html_text, encoding="utf-8")
    decisions_path.write_text(json.dumps(decisions, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "mission_folder": str(mission_folder),
        "dashboard_html": str(dashboard_path),
        "approval_decisions_json": str(decisions_path),
        "kingdom_review_queue_json": str(decisions_path),
        "internal_work_auto_authorized": True,
        "auto_publish_enabled": False,
        "approval_required_before_public_action": True,
    }


def build_dashboard_for_mission(mission_folder: Path) -> dict[str, str]:
    payloads = load_mission_payloads(mission_folder)
    return export_dashboard(mission_folder, payloads)


def build_dashboard_from_latest_mission(pipeline_root: Path = DEFAULT_PIPELINE_ROOT) -> dict[str, str]:
    mission_folder = latest_mission_folder(pipeline_root)
    return build_dashboard_for_mission(mission_folder)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local commerce review queue from a commerce pipeline mission folder.")
    parser.add_argument("--pipeline-root", type=Path, default=DEFAULT_PIPELINE_ROOT, help="Root containing commerce_pipeline_mission_* folders.")
    parser.add_argument("--mission-folder", type=Path, help="Specific commerce pipeline mission folder. Defaults to latest under --pipeline-root.")
    args = parser.parse_args()

    result = build_dashboard_for_mission(args.mission_folder) if args.mission_folder else build_dashboard_from_latest_mission(args.pipeline_root)
    print("COMMERCE KINGDOM REVIEW QUEUE COMPLETE")
    print(f"Mission folder: {result['mission_folder']}")
    print(f"Dashboard HTML: {result['dashboard_html']}")
    print(f"Review queue JSON: {result['approval_decisions_json']}")
    print("Internal work auto-execute: active")
    print("Manual external-action approval guard: active")
    print("No products were published automatically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
