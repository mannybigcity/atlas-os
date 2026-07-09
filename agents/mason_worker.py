from pathlib import Path
import sys
import json
import time
import subprocess
import shutil
from datetime import datetime
from typing import Any

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skills.mason_auto_builder_skill import mason_auto_builder_task

WORKSPACE = PROJECT_ROOT / "mason_workspace"
QUEUE_FILE = WORKSPACE / "mason_task_queue.json"
REPORTS_DIR = WORKSPACE / "reports"
BACKUPS_DIR = WORKSPACE / "backups"
EXECUTION_LOG = WORKSPACE / "mason_execution_log.jsonl"
ETSY_RESEARCH_SKILL_FILE = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN" / "03_AGENT_SKILLS" / "ETSY_RESEARCH_V1.md"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_WRITE_DIRS = [
    PROJECT_ROOT / "agents",
    PROJECT_ROOT / "skills",
    PROJECT_ROOT / "ui",
    PROJECT_ROOT / "mason_workspace",
    PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN" / "03_AGENT_SKILLS",
]

ETSY_RESEARCH_KEYWORD_EXPANSIONS = [
    "{topic}",
    "{topic} shirts",
    "{topic} t shirt",
    "{topic} hoodie",
    "{topic} sweatshirt",
    "{topic} apparel",
    "faith based streetwear",
    "Jesus streetwear",
    "Bible verse streetwear",
    "Christian graphic tee",
]


def now():
    return datetime.now().isoformat(timespec="seconds")


def append_execution_log(task_id: str, event: str, details: dict[str, Any] | None = None):
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": now(),
        "task_id": task_id,
        "event": event,
        "details": details or {},
    }
    with EXECUTION_LOG.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    return entry


def ensure_task_log(task):
    task.setdefault("execution_log", [])
    task.setdefault("files_changed", [])
    task.setdefault("tests_run", [])


def log_task_event(task, event: str, details: dict[str, Any] | None = None):
    ensure_task_log(task)
    entry = append_execution_log(task.get("id", "unknown"), event, details)
    task["execution_log"].append(entry)
    return entry


def load_queue():
    if not QUEUE_FILE.exists():
        QUEUE_FILE.write_text("[]", encoding="utf-8")
    return json.loads(QUEUE_FILE.read_text(encoding="utf-8-sig"))


def save_queue(tasks):
    QUEUE_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def is_allowed_path(path):
    path = Path(path).resolve()
    for allowed in ALLOWED_WRITE_DIRS:
        try:
            path.relative_to(allowed.resolve())
            return True
        except ValueError:
            pass
    return False


def backup_file(path):
    path = Path(path)
    if not path.exists():
        return None

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = str(path).replace(":", "").replace("\\", "__").replace("/", "__")
    backup_path = BACKUPS_DIR / f"{backup_name}_{stamp}.bak"
    shutil.copy2(path, backup_path)
    return str(backup_path)


def safe_write_file(target_path, content):
    target_path = Path(target_path)

    if not is_allowed_path(target_path):
        raise PermissionError(f"Mason is not allowed to write here: {target_path}")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    backup = backup_file(target_path)
    target_path.write_text(content, encoding="utf-8")

    return {
        "written_file": str(target_path),
        "backup": backup,
        "status": "written",
    }


def run_python_file(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Test file does not exist: {file_path}")

    result = subprocess.run(
        [sys.executable, str(file_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    return {
        "file": str(file_path),
        "returncode": result.returncode,
        "success": result.returncode == 0,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    }


def inspect_file(file_path, limit=6000):
    file_path = Path(file_path)

    if not file_path.exists():
        return {
            "status": "missing",
            "file": str(file_path),
        }

    return {
        "status": "found",
        "file": str(file_path),
        "preview": file_path.read_text(encoding="utf-8", errors="replace")[:limit],
    }


def ensure_etsy_research_skill_file():
    ETSY_RESEARCH_SKILL_FILE.parent.mkdir(parents=True, exist_ok=True)
    if ETSY_RESEARCH_SKILL_FILE.exists():
        return {"status": "verified", "skill_file": str(ETSY_RESEARCH_SKILL_FILE)}

    content = """# ETSY_RESEARCH_V1

Purpose: Internal Etsy research skill for RAMFAM Kingdom marketplace planning.

Assigned agents:
- Hunter: opportunity scoring, demand, competition, revenue fit.
- Oracle: trend intelligence and market signal interpretation.
- Amanda: marketplace/listing draft recommendations only.

Inputs:
- topic or keywords to research.

Outputs:
- top 10 keyword opportunities
- competition score
- opportunity score
- recommended products/offers
- JSON and Markdown report paths

Rules:
- Use Etsy API only when ETSY_KEYSTRING is available.
- If the API is unavailable, clearly mark offline seed data.
- Do not publish listings, spend money, contact customers, or create products.
- Manny approval is required before any public, financial, customer-facing, or reputation-impacting action.
"""
    ETSY_RESEARCH_SKILL_FILE.write_text(content, encoding="utf-8")
    return {"status": "created", "skill_file": str(ETSY_RESEARCH_SKILL_FILE)}


def extract_research_topic(task):
    context = task.get("context") if isinstance(task.get("context"), dict) else {}
    for key in ("topic", "keywords", "research"):
        if context.get(key):
            return str(context[key]).strip()

    text = str(task.get("task", ""))
    for marker in ("Research:", "research:"):
        if marker in text:
            candidate = text.split(marker, 1)[1].strip().splitlines()[0].strip()
            if candidate:
                return candidate
    if " for " in text.lower():
        candidate = text.rsplit(" for ", 1)[1].strip().splitlines()[0].strip().strip('"')
        if candidate:
            return candidate
    return text.strip() or "Christian streetwear"


def expand_etsy_keywords(topic: str) -> list[str]:
    topic = " ".join(str(topic or "").strip().split()) or "Christian streetwear"
    keywords = []
    seen = set()
    for template in ETSY_RESEARCH_KEYWORD_EXPANSIONS:
        keyword = template.format(topic=topic).strip()
        normalized = keyword.lower()
        if normalized and normalized not in seen:
            keywords.append(keyword)
            seen.add(normalized)
    return keywords[:10]


def handle_etsy_research(task):
    from skills.commerce.hunter_etsy_research import export_report, research_keywords

    skill_status = ensure_etsy_research_skill_file()
    topic = extract_research_topic(task)
    keywords = expand_etsy_keywords(topic)
    output_dir = WORKSPACE / "etsy_research_v1" / datetime.now().strftime("%Y%m%d_%H%M%S")
    report = research_keywords(keywords, limit=25, use_api=True)
    exports = export_report(report, output_dir)
    top_keywords = [
        {
            "keyword": item["keyword"],
            "competition_level": item["competition_level"],
            "opportunity_score": item["opportunity_score"],
            "recommended_offer": item["recommended_offer"],
        }
        for item in report.get("opportunities", [])[:10]
    ]

    validation_checks = [
        {
            "name": "ETSY_RESEARCH_V1 generated 10 keyword rows",
            "success": len(top_keywords) == 10,
            "observed": len(top_keywords),
        },
        {
            "name": "ETSY_RESEARCH_V1 wrote JSON export",
            "success": Path(exports["latest_json"]).exists(),
            "file": exports["latest_json"],
        },
        {
            "name": "ETSY_RESEARCH_V1 wrote Markdown report",
            "success": Path(exports["latest_report"]).exists(),
            "file": exports["latest_report"],
        },
    ]

    return {
        "type": "ETSY_RESEARCH_V1",
        "status": "success" if all(check["success"] for check in validation_checks) else "failed",
        "topic": topic,
        "skill_status": skill_status,
        "top_10_keywords": top_keywords,
        "competition_score": report.get("top_opportunity", {}).get("competition_level"),
        "opportunity_score": report.get("top_opportunity", {}).get("opportunity_score"),
        "recommended_products": [item["recommended_offer"] for item in report.get("opportunities", [])[:5]],
        "api_used": report.get("api_used"),
        "api_errors": report.get("api_errors"),
        "exports": exports,
        "validation_checks": validation_checks,
    }


def build_agent_delegation_code():
    return r'''from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


AGENT_FILES = {
    "hunter": ("skills.hunter_agent", "hunter_agent"),
    "gideon": ("skills.gideon_agent", "gideon_agent"),
    "amanda": ("skills.amanda_agent", "amanda_agent"),
    "david": ("skills.david_agent", "david_agent"),
    "ranger": ("skills.ranger_agent", "ranger_agent"),
    "scout": ("skills.scout_agent", "scout_agent"),
    "micah": ("skills.micah_agent", "micah_agent"),
    "taylor": ("skills.taylor_agent", "taylor_agent"),
}


def detect_agent(text):
    lowered = text.lower()
    for agent_name in AGENT_FILES:
        if agent_name in lowered:
            return agent_name
    return None


def delegate_to_agent(task="", context=None):
    context = context or {}
    agent_name = context.get("agent") or detect_agent(task)

    if not agent_name:
        return {
            "status": "needs_agent",
            "message": "No agent detected. Try: have Hunter rank leads, have Micah draft a post, or have Gideon review profit.",
            "available_agents": sorted(AGENT_FILES.keys())
        }

    agent_name = agent_name.lower()

    if agent_name not in AGENT_FILES:
        return {
            "status": "unknown_agent",
            "agent": agent_name,
            "available_agents": sorted(AGENT_FILES.keys())
        }

    module_name, function_name = AGENT_FILES[agent_name]

    module = __import__(module_name, fromlist=[function_name])
    agent_function = getattr(module, function_name)

    result = agent_function(task, context)

    return {
        "status": "delegated",
        "delegated_to": agent_name.title(),
        "task": task,
        "result": result,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    test_context = {
        "agent": "hunter",
        "items": [
            {"name": "50 hat order", "value": 950, "urgency": 9, "ease": 7, "relationship": 6, "impact": 8},
            {"name": "Small shirt order", "value": 75, "urgency": 3, "ease": 8, "relationship": 2, "impact": 3}
        ]
    }

    print(delegate_to_agent("Have Hunter rank today's opportunities", test_context))
'''


def handle_build_agent_delegation(task):
    target = PROJECT_ROOT / "agents" / "atlas_agent_delegation.py"
    code = build_agent_delegation_code()
    write_result = safe_write_file(target, code)
    test_result = run_python_file(target)

    return {
        "type": "build_agent_delegation",
        "write_result": write_result,
        "test_result": test_result,
        "status": "success" if test_result["success"] else "failed",
    }


def handle_task(task):
    task_type = task.get("type", "auto_builder")
    task_text = str(task.get("task", ""))

    if task_type == "ETSY_RESEARCH_V1" or "ETSY_RESEARCH_V1" in task_text:
        return handle_etsy_research(task)

    if task_type == "inspect_file":
        return inspect_file(task.get("file"))

    if task_type == "write_file":
        return safe_write_file(task.get("file"), task.get("content", ""))

    if task_type == "run_python":
        return run_python_file(task.get("file"))

    if task_type == "build_agent_delegation":
        return handle_build_agent_delegation(task)

    return {
        "type": "auto_builder",
        "status": "success",
        "result": mason_auto_builder_task(task.get("task", "")),
    }


def collect_files_changed(result):
    if not isinstance(result, dict):
        return []
    changed = []
    if result.get("written_file"):
        changed.append(result.get("written_file"))
    if result.get("write_result", {}).get("written_file"):
        changed.append(result["write_result"]["written_file"])
    if result.get("skill_status", {}).get("status") == "created":
        changed.append(result["skill_status"].get("skill_file"))
    if result.get("exports"):
        changed.extend(str(path) for path in result["exports"].values())
    return changed


def collect_tests_run(result):
    if not isinstance(result, dict):
        return []
    tests = []
    if result.get("test_result"):
        tests.append(result["test_result"])
    if result.get("file") and "returncode" in result:
        tests.append(result)
    if result.get("validation_checks"):
        tests.extend(result["validation_checks"])
    return tests


def write_report(task, result):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_id = task.get("id", "unknown")
    report_path = REPORTS_DIR / f"mason_worker_{task_id}_{stamp}.md"

    report = f"""# Mason Worker Build Report

Time: {now()}

Task ID: {task.get('id', 'unknown')}

Agent: {task.get('agent', 'Mason')}

Task Type: {task.get('type', 'auto_builder')}

Status: {result.get('status', 'complete') if isinstance(result, dict) else 'complete'}

Execution Log:
{json.dumps(task.get('execution_log', []), indent=2, default=str)}

Files Changed:
{json.dumps(task.get('files_changed', []), indent=2, default=str)}

Tests Run:
{json.dumps(task.get('tests_run', []), indent=2, default=str)}

Task:
{task.get('task', '')}

Result:
{json.dumps(result, indent=2, default=str)}
"""

    report_path.write_text(report, encoding="utf-8")
    return str(report_path)


def process_once():
    tasks = load_queue()

    for task in tasks:
        if task.get("status") == "pending":
            ensure_task_log(task)
            log_task_event(task, "task_received", {"task": task.get("task"), "type": task.get("type")})
            print(f"Mason Worker executing: {task.get('task')}")

            task["status"] = "running"
            task["started_at"] = now()
            log_task_event(task, "task_started", {"started_at": task["started_at"]})
            save_queue(tasks)

            try:
                result = handle_task(task)
                task["files_changed"] = collect_files_changed(result)
                task["tests_run"] = collect_tests_run(result)
                log_task_event(task, "files_changed", {"files": task["files_changed"]})
                log_task_event(task, "tests_run", {"tests": task["tests_run"]})
                report_path = write_report(task, result)

                task["status"] = "complete" if result.get("status") != "failed" else "failed"
                task["completed_at"] = now()
                task["report"] = report_path
                task["result_preview"] = str(result)[:800]
                task["result"] = result
                log_task_event(
                    task,
                    "task_completed",
                    {"completed_at": task["completed_at"], "report": report_path, "status": task["status"]},
                )

                print(f"Complete. Report: {report_path}")

            except Exception as e:
                task["status"] = "failed"
                task["failed_at"] = now()
                task["error"] = str(e)
                log_task_event(task, "task_failed", {"failed_at": task["failed_at"], "error": str(e)})
                print(f"FAILED: {e}")

            save_queue(tasks)
            return True

    return False


def run_forever():
    print("Mason Worker online.")
    print("Mode: Builder Worker with safe local file tools and execution logging.")
    print(f"Watching queue: {QUEUE_FILE}")

    while True:
        did_work = process_once()
        if not did_work:
            print("No pending Mason tasks. Sleeping...")
        time.sleep(5)


if __name__ == "__main__":
    run_forever()
