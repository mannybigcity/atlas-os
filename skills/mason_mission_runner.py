"""First working Mason mission runner.

This module gives Mason a small, testable mission execution surface that Atlas
can import, run directly, and use to leave a report trail in the Mason
workspace.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
MASON_WORKSPACE = PROJECT_ROOT / "mason_workspace"
REPORTS_DIR = MASON_WORKSPACE / "reports"
MISSION_LOG = MASON_WORKSPACE / "mason_mission_log.json"


@dataclass
class MissionResult:
    """Structured result returned by Mason mission runs."""

    mission_id: str
    status: str
    summary: str
    mission: str
    context: dict[str, Any] = field(default_factory=dict)
    actions: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    report_path: str | None = None


def _ensure_workspace() -> None:
    """Ensure Mason's local workspace exists before writing outputs."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MISSION_LOG.exists():
        MISSION_LOG.write_text("[]\n", encoding="utf-8")


def _slug(value: str) -> str:
    """Create a filesystem-safe slug for report names."""
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned[:60] or "mission"


def _load_log() -> list[dict[str, Any]]:
    _ensure_workspace()
    try:
        data = json.loads(MISSION_LOG.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []


def _save_log(entries: list[dict[str, Any]]) -> None:
    MISSION_LOG.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_mission_report(result: MissionResult) -> str:
    """Write a Markdown report for a completed Mason mission."""
    _ensure_workspace()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"mason_mission_{_slug(result.mission_id)}_{stamp}.md"
    report = f"""# Mason Mission Runner Report

Time: {result.timestamp}
Mission ID: {result.mission_id}
Status: {result.status}

## Mission
{result.mission}

## Summary
{result.summary}

## Actions
"""
    if result.actions:
        report += "\n".join(f"- {action}" for action in result.actions)
    else:
        report += "- No actions recorded."
    report += "\n\n## Context\n"
    report += json.dumps(result.context, indent=2, ensure_ascii=False)
    report += "\n"
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)


def run_mission(mission: str, context: Mapping[str, Any] | None = None, *, write_report: bool = True) -> dict[str, Any]:
    """Run a Mason mission and return a JSON-serializable result.

    The first working version intentionally avoids external side effects beyond
    Mason's local workspace. It validates the mission, records deterministic
    execution steps, writes a report by default, and appends to the mission log.
    """
    _ensure_workspace()
    mission_text = str(mission or "").strip()
    mission_context = dict(context or {})

    if not mission_text:
        result = MissionResult(
            mission_id="empty_mission",
            status="failed",
            summary="Mason could not run an empty mission.",
            mission="",
            context=mission_context,
            actions=["Rejected empty mission text."],
        )
    else:
        mission_id = str(mission_context.get("mission_id") or _slug(mission_text))
        actions = [
            "Received mission from Atlas.",
            "Validated mission text.",
            "Prepared Mason workspace report trail.",
            "Returned structured mission result.",
        ]
        if mission_context:
            actions.append("Attached mission context for Atlas review.")
        result = MissionResult(
            mission_id=mission_id,
            status="complete",
            summary=f"Mason completed mission: {mission_text}",
            mission=mission_text,
            context=mission_context,
            actions=actions,
        )

    if write_report:
        result.report_path = write_mission_report(result)

    entries = _load_log()
    entries.append(asdict(result))
    _save_log(entries)
    return asdict(result)


def mason_mission_runner(mission_text, context=None):
    return run_mission(mission_text, context)


def run_test_mission() -> dict[str, Any]:
    """Run the built-in smoke test mission for Atlas/Mason verification."""
    return run_mission(
        "Verify Mason mission runner can execute a test mission",
        {
            "mission_id": "mason_runner_smoke_test",
            "requested_by": "Atlas",
            "priority": "systems_before_scale",
        },
    )


def report_to_atlas(result: Mapping[str, Any]) -> str:
    """Return a concise Atlas-ready status line."""
    status = result.get("status", "unknown")
    mission_id = result.get("mission_id", "unknown")
    report_path = result.get("report_path") or "no report written"
    return f"Atlas report: mission {mission_id} finished with status {status}. Report: {report_path}"


__all__ = [
    "MissionResult",
    "run_mission",
    "mason_mission_runner",
    "run_test_mission",
    "write_mission_report",
    "report_to_atlas",
    "PROJECT_ROOT",
    "MASON_WORKSPACE",
    "REPORTS_DIR",
    "MISSION_LOG",
]


if __name__ == "__main__":
    result = run_test_mission()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(report_to_atlas(result))
