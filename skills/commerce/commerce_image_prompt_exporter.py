"""Commerce Image Prompt Exporter.

Takes Manny-approved Micah design decisions from the commerce approval dashboard
plus Micah's design prompt JSON and exports organized OpenAI image prompt files.
This exporter is prompt-only: it never generates images, publishes products,
creates live Printify products, spends money, or contacts customers.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BRAIN_DIR = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
DEFAULT_PIPELINE_ROOT = BRAIN_DIR / "06_MISSIONS" / "commerce_pipeline_runner"
DEFAULT_OUTPUT_DIR = BRAIN_DIR / "06_MISSIONS" / "commerce_image_prompt_exporter"

MANNY_APPROVAL_REQUIREMENT = (
    "Manny approval is required before generating images, publishing listings, creating live Printify products, "
    "changing pricing, ordering samples, spending ad budget, contacting customers, accepting custom orders, "
    "or making any public/reputation-impacting marketplace action."
)

ACTIONS_NOT_TAKEN = [
    "No images were generated.",
    "No Etsy listing was published.",
    "No live Printify product was created or modified.",
    "No sample order was placed.",
    "No ad budget was spent.",
    "No customer was contacted or committed.",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def load_approval_decisions_json(input_path: Path) -> dict[str, Any]:
    payload = load_json(input_path)
    decisions = payload.get("approval_decisions")
    if not isinstance(decisions, dict):
        raise ValueError("Approval decisions JSON must include an approval_decisions object.")
    micah_designs = decisions.get("micah_designs")
    if not isinstance(micah_designs, list):
        raise ValueError("Approval decisions JSON must include approval_decisions.micah_designs.")
    return payload


def load_micah_design_prompt_json(input_path: Path) -> dict[str, Any]:
    payload = load_json(input_path)
    concepts = payload.get("design_concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValueError("Micah design prompt JSON must include at least one design_concepts item.")
    return payload


def latest_mission_folder(pipeline_root: Path = DEFAULT_PIPELINE_ROOT) -> Path:
    if not pipeline_root.exists():
        raise FileNotFoundError(f"Commerce pipeline root not found: {pipeline_root}")
    candidates = [path for path in pipeline_root.iterdir() if path.is_dir() and path.name.startswith("commerce_pipeline_mission_")]
    if not candidates:
        raise FileNotFoundError(f"No commerce pipeline mission folders found under {pipeline_root}")
    return max(candidates, key=lambda path: path.name)


def mission_input_paths(mission_folder: Path) -> tuple[Path, Path]:
    decisions_path = mission_folder / "commerce_approval_decisions.json"
    micah_path = mission_folder / "02_micah_design_prompt_engine" / "micah_design_prompts_latest.json"
    return decisions_path, micah_path


def slug_text(raw: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", raw.lower()).strip("-")
    return value or "openai-image-prompt"


def _norm(raw: Any) -> str:
    return " ".join(str(raw or "").strip().lower().split())


def _prompt_from_design(design: dict[str, Any]) -> str:
    prompt = design.get("openai_image_prompt") or design.get("image_prompt")
    if not prompt:
        raise ValueError(f"Approved Micah design is missing openai_image_prompt/image_prompt: {design.get('design_title')}")
    return str(prompt)


def _concept_lookup(micah_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for concept in micah_payload.get("design_concepts", []) or []:
        if not isinstance(concept, dict):
            continue
        title = concept.get("design_title")
        if title:
            lookup[_norm(title)] = concept
        rank = concept.get("rank")
        if rank is not None:
            lookup[f"rank:{rank}"] = concept
    return lookup


def _matching_concept(decision: dict[str, Any], lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
    title_match = lookup.get(_norm(decision.get("title")))
    if title_match:
        return title_match

    item_id = str(decision.get("item_id") or "")
    match = re.search(r"(\d+)$", item_id)
    if match:
        rank_match = lookup.get(f"rank:{int(match.group(1))}")
        if rank_match:
            return rank_match

    raise ValueError(f"Approved Micah decision has no matching design concept: {decision.get('title') or item_id}")


def _is_manny_approved_design(decision: dict[str, Any]) -> bool:
    return _norm(decision.get("status")) == "approved" and _norm(decision.get("approved_by")) == "manny"


def _manny_approval_gate(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "required_approval": MANNY_APPROVAL_REQUIREMENT,
        "approved_by": str(decision.get("approved_by") or ""),
        "reviewed_at": str(decision.get("reviewed_at") or ""),
        "approval_notes": str(decision.get("notes") or ""),
        "prompt_export_allowed": True,
        "image_generation_allowed": False,
        "image_generation_performed": False,
        "publish_allowed": False,
        "customer_contact_allowed": False,
    }


def build_openai_image_prompt(rank: int, decision: dict[str, Any], design: dict[str, Any]) -> dict[str, Any]:
    title = str(design.get("design_title") or decision.get("title") or f"Micah design {rank}")
    prompt_id = f"openai-image-prompt-{rank:02d}-{slug_text(title)}"
    return {
        "rank": rank,
        "prompt_id": prompt_id,
        "source_decision_item_id": str(decision.get("item_id") or ""),
        "source_design_rank": design.get("rank", rank),
        "source_keyword": design.get("source_keyword"),
        "source_opportunity_score": design.get("source_opportunity_score"),
        "design_title": title,
        "design_concept": design.get("design_concept"),
        "art_direction": design.get("art_direction"),
        "color_palette": list(design.get("color_palette", []) or []),
        "typography_suggestions": design.get("typography_suggestions"),
        "openai_image_prompt": _prompt_from_design(design),
        "commercial_use_notes": design.get("commercial_use_notes"),
        "export_status": "prompt_exported_no_image_generated",
        "manny_approval_gate": _manny_approval_gate(decision),
    }


def approved_prompt_exports(decisions_payload: dict[str, Any], micah_payload: dict[str, Any]) -> list[dict[str, Any]]:
    micah_decisions = decisions_payload.get("approval_decisions", {}).get("micah_designs", []) or []
    lookup = _concept_lookup(micah_payload)
    prompts = []
    for decision in micah_decisions:
        if not isinstance(decision, dict) or not _is_manny_approved_design(decision):
            continue
        design = _matching_concept(decision, lookup)
        prompts.append(build_openai_image_prompt(len(prompts) + 1, decision, design))
    return prompts


def generate_image_prompt_export_report(decisions_payload: dict[str, Any], micah_payload: dict[str, Any]) -> dict[str, Any]:
    prompts = approved_prompt_exports(decisions_payload, micah_payload)
    micah_decisions = [item for item in decisions_payload.get("approval_decisions", {}).get("micah_designs", []) or [] if isinstance(item, dict)]
    return {
        "mission": "Commerce Image Prompt Exporter",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_mission": decisions_payload.get("mission", "Commerce Approval Dashboard"),
        "source_micah_mission": micah_payload.get("mission", "Micah Design Prompt Engine"),
        "mission_folder": decisions_payload.get("mission_folder"),
        "agent_chain": {
            "assigned_by": "Atlas",
            "builder": "Mason",
            "design_owner": "Micah",
            "approval_owner": "Manny",
        },
        "counts": {
            "micah_design_decisions": len(micah_decisions),
            "approved_prompt_exports": len(prompts),
            "blocked_or_unapproved_designs": max(0, len(micah_decisions) - len(prompts)),
        },
        "openai_image_prompts": prompts,
        "image_generation_enabled": False,
        "auto_publish_enabled": False,
        "approval_required_before_public_action": True,
        "manny_approval_guard": {
            "prompt_export_requires_manny_approved_micah_decision": True,
            "image_generation": "blocked_not_performed_by_exporter",
            "publish_action": "blocked_pending_separate_manny_approval",
            "printify_live_creation": "blocked_pending_separate_manny_approval",
            "pricing_change": "blocked_pending_separate_manny_approval",
            "sample_order": "blocked_pending_separate_manny_approval",
            "ad_spend": "blocked_pending_separate_manny_approval",
            "customer_contact": "blocked_pending_separate_manny_approval",
            "customer_commitment": "blocked_pending_separate_manny_approval",
            "requirement": MANNY_APPROVAL_REQUIREMENT,
        },
        "actions_not_taken": list(ACTIONS_NOT_TAKEN),
    }


def prompt_text(prompt: dict[str, Any]) -> str:
    lines = [
        f"Prompt ID: {prompt['prompt_id']}",
        f"Design title: {prompt['design_title']}",
        f"Source decision item ID: {prompt['source_decision_item_id']}",
        f"Source keyword: {prompt.get('source_keyword') or 'Unknown'}",
        "Manny approval guard: prompt export only; no image generation, publishing, customer contact, or customer commitment performed.",
        "",
        "OPENAI IMAGE PROMPT:",
        prompt["openai_image_prompt"],
        "",
        "Commercial use notes:",
        str(prompt.get("commercial_use_notes") or "Verify all fonts, graphics, phrases, and production assumptions before any public action."),
        "",
        MANNY_APPROVAL_REQUIREMENT,
    ]
    return "\n".join(lines)


def build_markdown_report(report: dict[str, Any]) -> str:
    counts = report.get("counts", {})
    lines = [
        "# Commerce Image Prompt Export Report",
        "",
        f"Generated: {report['generated_at']}",
        "Assigned by: Atlas",
        "Built by: Mason",
        "Design owner: Micah",
        "Approval owner: Manny",
        "Image generation enabled: false",
        "Auto-publish enabled: false",
        "No images were generated.",
        "",
        "## Executive Summary",
        "",
        f"- Micah design decisions reviewed: {counts.get('micah_design_decisions', 0)}",
        f"- Approved prompt exports: {counts.get('approved_prompt_exports', 0)}",
        f"- Blocked or unapproved designs: {counts.get('blocked_or_unapproved_designs', 0)}",
        "",
        "## Approved OpenAI Image Prompts",
        "",
    ]

    prompts = report.get("openai_image_prompts", []) or []
    if not prompts:
        lines.extend(["No Manny-approved Micah design prompts were exported.", ""])
    for prompt in prompts:
        lines.extend(
            [
                f"### {prompt['rank']}. {prompt['design_title']}",
                "",
                f"- Prompt ID: {prompt['prompt_id']}",
                f"- Source decision item ID: {prompt['source_decision_item_id']}",
                f"- Source keyword: {prompt.get('source_keyword') or 'Unknown'}",
                f"- Export status: {prompt['export_status']}",
                "",
                "```text",
                prompt["openai_image_prompt"],
                "```",
                "",
            ]
        )

    lines.extend(["## Manny approval guard", "", MANNY_APPROVAL_REQUIREMENT, ""])
    lines.extend(["## Actions Not Taken", ""])
    lines.extend(f"- {action}" for action in report.get("actions_not_taken", []))
    lines.append("")
    return "\n".join(lines)


def export_report(report: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    prompt_dir = output_dir / "openai_image_prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    prompt_text_files = []
    for prompt in report.get("openai_image_prompts", []) or []:
        prompt_path = prompt_dir / f"{prompt['prompt_id']}.txt"
        prompt_path.write_text(prompt_text(prompt), encoding="utf-8")
        prompt["prompt_text_path"] = str(prompt_path)
        prompt_text_files.append(str(prompt_path))

    archive_json = output_dir / f"commerce_image_prompts_{timestamp}.json"
    latest_json = output_dir / "commerce_image_prompts_latest.json"
    archive_md = output_dir / f"commerce_image_prompts_{timestamp}.md"
    latest_md = output_dir / "commerce_image_prompts_latest.md"

    report["exports"] = {
        "archive_json": str(archive_json),
        "latest_json": str(latest_json),
        "archive_report": str(archive_md),
        "latest_report": str(latest_md),
        "prompt_text_dir": str(prompt_dir),
        "prompt_text_files": prompt_text_files,
    }

    json_text = json.dumps(report, indent=2, ensure_ascii=False)
    markdown = build_markdown_report(report)

    archive_json.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    archive_md.write_text(markdown, encoding="utf-8")
    latest_md.write_text(markdown, encoding="utf-8")

    return dict(report["exports"])


def export_image_prompts_from_files(decisions_path: Path, micah_path: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    decisions_payload = load_approval_decisions_json(decisions_path)
    micah_payload = load_micah_design_prompt_json(micah_path)
    report = generate_image_prompt_export_report(decisions_payload, micah_payload)
    exports = export_report(report, output_dir)
    return {"report": report, "exports": exports}


def build_for_mission(mission_folder: Path, output_dir: Path | None = None) -> dict[str, Any]:
    decisions_path, micah_path = mission_input_paths(mission_folder)
    target_dir = output_dir or mission_folder / "05_commerce_image_prompt_exporter"
    return export_image_prompts_from_files(decisions_path, micah_path, target_dir)


def build_from_latest_mission(pipeline_root: Path = DEFAULT_PIPELINE_ROOT) -> dict[str, Any]:
    return build_for_mission(latest_mission_folder(pipeline_root))


def main() -> int:
    parser = argparse.ArgumentParser(description="Export OpenAI image prompt text/JSON/Markdown for Manny-approved Micah commerce designs only.")
    parser.add_argument("--pipeline-root", type=Path, default=DEFAULT_PIPELINE_ROOT, help="Root containing commerce_pipeline_mission_* folders.")
    parser.add_argument("--mission-folder", type=Path, help="Specific commerce pipeline mission folder. Defaults to latest under --pipeline-root when --decisions/--micah are not supplied.")
    parser.add_argument("--decisions", type=Path, help="Commerce approval decisions JSON input path.")
    parser.add_argument("--micah", type=Path, help="Micah design prompt JSON input path.")
    parser.add_argument("--output-dir", type=Path, help="Directory for JSON, Markdown, and prompt text exports.")
    args = parser.parse_args()

    if args.decisions or args.micah:
        if not args.decisions or not args.micah:
            parser.error("--decisions and --micah must be supplied together.")
        result = export_image_prompts_from_files(args.decisions, args.micah, args.output_dir or DEFAULT_OUTPUT_DIR)
    else:
        mission_folder = args.mission_folder or latest_mission_folder(args.pipeline_root)
        result = build_for_mission(mission_folder, args.output_dir)

    report = result["report"]
    exports = result["exports"]
    print("COMMERCE IMAGE PROMPT EXPORTER COMPLETE")
    print(f"Approved prompt exports: {report['counts']['approved_prompt_exports']}")
    print(f"JSON export: {exports['latest_json']}")
    print(f"Markdown report: {exports['latest_report']}")
    print(f"Prompt text directory: {exports['prompt_text_dir']}")
    print("Manny approval guard: active")
    print("No images were generated, no products were published, and no customers were contacted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
