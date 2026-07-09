from pathlib import Path
import sys
import json
import subprocess
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents import atlas_mason_kanban_bridge as mason_bridge

MASON_QUEUE_FILE = PROJECT_ROOT / "mason_workspace" / "mason_task_queue.json"
MASON_HERMES_PROFILE = mason_bridge.MASON_HERMES_PROFILE
MASON_HERMES_SKILL = mason_bridge.MASON_HERMES_SKILL

AGENT_FILES = {
    "hunter": ("skills.hunter_agent", "hunter_agent"),
    "oracle": ("skills.oracle_agent", "oracle_agent"),
    "gideon": ("skills.gideon_agent", "gideon_agent"),
    "amanda": ("skills.amanda_agent", "amanda_agent"),
    "david": ("skills.david_agent", "david_agent"),
    "ranger": ("skills.ranger_agent", "ranger_agent"),
    "scout": ("skills.scout_agent", "scout_agent"),
    "micah": ("skills.micah_agent", "micah_agent"),
    "taylor": ("skills.taylor_agent", "taylor_agent"),
}


def detect_agent(text):
    lowered = str(text or "").lower()
    if "mason" in lowered:
        return "mason"

    for agent_name in AGENT_FILES:
        if agent_name in lowered:
            return agent_name
    return None


def _load_mason_queue():
    MASON_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MASON_QUEUE_FILE.exists():
        MASON_QUEUE_FILE.write_text("[]", encoding="utf-8")

    try:
        return json.loads(MASON_QUEUE_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return []


def _save_mason_queue(tasks):
    MASON_QUEUE_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def _mason_execution_snapshot(task_id):
    tasks = _load_mason_queue()
    for item in reversed(tasks):
        if item.get("id") == task_id:
            return item
    return {}


def _task_title(task):
    return mason_bridge.task_title(task)


def _redact_sensitive_context(value):
    return mason_bridge.redact_sensitive_context(value)


def _mason_task_body(task, context, task_id):
    return mason_bridge.build_mason_task_body(task, context, task_id)


def _parse_kanban_task_id(stdout, fallback_task_id):
    return mason_bridge.parse_kanban_task_id(stdout, fallback_task_id)


def _run_mason_kanban_create(task, context, task_id):
    command = mason_bridge.build_create_command(task, context, task_id)
    return command, subprocess.run(command, cwd=str(PROJECT_ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")


def _run_mason_kanban_dispatch():
    command = mason_bridge.build_dispatch_command()
    return command, subprocess.run(command, cwd=str(PROJECT_ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")


def _legacy_enqueue_mason_task(task="", context=None):
    context = context or {}
    tasks = _load_mason_queue()

    task_id = "atlas_mason_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    mason_task = {
        "id": task_id,
        "agent": "Mason",
        "type": context.get("mason_task_type", "auto_builder"),
        "status": "pending",
        "task": task,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source": "atlas_agent_delegation_legacy",
        "context": context,
    }

    if context.get("file"):
        mason_task["file"] = context.get("file")

    tasks.append(mason_task)
    _save_mason_queue(tasks)

    response = {
        "status": "queued",
        "delegated_to": "Mason",
        "system": "legacy_mason_workspace",
        "task_id": task_id,
        "queue_file": str(MASON_QUEUE_FILE),
        "message": "Mason task accepted by legacy builder queue.",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    if context.get("auto_execute", True):
        try:
            from agents.mason_worker import process_once

            did_work = process_once()
            snapshot = _mason_execution_snapshot(task_id)
            response["worker_invoked"] = did_work
            response["worker_status"] = snapshot.get("status")
            for key in ("report", "result_preview", "result", "error"):
                if snapshot.get(key):
                    response[key] = snapshot.get(key)
            if did_work and snapshot.get("status") == "complete":
                response["status"] = "executed"
        except Exception as error:
            response["execution_error"] = str(error)

    return response


def enqueue_mason_task(task="", context=None):
    context = context or {}
    if context.get("use_legacy_mason"):
        return _legacy_enqueue_mason_task(task, context)

    task_id = "atlas_mason_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    create_command, create_result = _run_mason_kanban_create(task, context, task_id)

    if create_result.returncode != 0:
        return {
            "status": "blocked",
            "delegated_to": "Mason",
            "system": "hermes_kanban",
            "assignee": MASON_HERMES_PROFILE,
            "task_id": task_id,
            "message": "Atlas could not create the Hermes Kanban task for Mason.",
            "command": create_command,
            "error": (create_result.stderr or create_result.stdout or "Hermes Kanban create failed")[-2000:],
            "legacy_available": True,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    kanban_task_id = _parse_kanban_task_id(create_result.stdout, task_id)
    response = {
        "status": "queued",
        "delegated_to": "Mason",
        "system": "hermes_kanban",
        "assignee": MASON_HERMES_PROFILE,
        "task_id": task_id,
        "kanban_task_id": kanban_task_id,
        "message": "Atlas created a Hermes Kanban task for Mason.",
        "command": create_command,
        "kanban_create_stdout": (create_result.stdout or "")[-2000:],
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    if context.get("auto_execute", True):
        dispatch_command, dispatch_result = _run_mason_kanban_dispatch()
        response["dispatch_command"] = dispatch_command
        response["dispatch_stdout"] = (dispatch_result.stdout or "")[-2000:]
        response["dispatch_stderr"] = (dispatch_result.stderr or "")[-2000:]
        response["worker_invoked"] = dispatch_result.returncode == 0
        if dispatch_result.returncode == 0:
            response["status"] = "dispatched"
            response["message"] = "Atlas created and dispatched a Hermes Kanban task for Mason."
        else:
            response["dispatch_error"] = response["dispatch_stderr"] or response["dispatch_stdout"]

    return response


def delegate_to_agent(task="", context=None):
    context = context or {}
    agent_name = context.get("agent") or detect_agent(task)

    if not agent_name:
        return {
            "status": "needs_agent",
            "message": "No agent detected. Try: have Hunter rank leads, have Oracle research trends, have Amanda draft marketplace copy, or have Mason build.",
            "available_agents": sorted(list(AGENT_FILES.keys()) + ["mason"]),
        }

    agent_name = agent_name.lower()

    if agent_name == "mason":
        return enqueue_mason_task(task, context)

    if agent_name not in AGENT_FILES:
        return {
            "status": "unknown_agent",
            "agent": agent_name,
            "available_agents": sorted(list(AGENT_FILES.keys()) + ["mason"]),
        }

    module_name, function_name = AGENT_FILES[agent_name]

    module = __import__(module_name, fromlist=[function_name])
    agent_function = getattr(module, function_name)

    try:
        result = agent_function(task, context)
    except TypeError:
        result = agent_function(task)

    return {
        "status": "delegated",
        "delegated_to": agent_name.title(),
        "task": task,
        "result": result,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def _format_mason_delegation(task, queued_result, context):
    mason_result = {
        "agent": "Mason",
        "status": queued_result.get("status", "queued"),
        "system": queued_result.get("system"),
        "assignee": queued_result.get("assignee"),
        "task_id": queued_result.get("task_id"),
        "kanban_task_id": queued_result.get("kanban_task_id"),
        "queue_file": queued_result.get("queue_file"),
        "message": queued_result.get("message"),
    }

    for key in (
        "worker_invoked",
        "worker_status",
        "report",
        "result_preview",
        "result",
        "error",
        "execution_error",
        "dispatch_stdout",
        "dispatch_error",
    ):
        if key in queued_result:
            mason_result[key] = queued_result[key]

    if context.get("execute_now") and queued_result.get("system") == "legacy_mason_workspace" and queued_result.get("task_id") and queued_result.get("status") != "executed":
        try:
            from agents.mason_worker import process_once

            did_work = process_once()
            snapshot = _mason_execution_snapshot(queued_result["task_id"])
            worker_status = snapshot.get("status")

            if did_work and worker_status == "complete":
                mason_result["status"] = "executed"
            elif worker_status:
                mason_result["status"] = worker_status

            if snapshot.get("report"):
                mason_result["report"] = snapshot.get("report")
            if snapshot.get("result_preview"):
                mason_result["result_preview"] = snapshot.get("result_preview")
            if snapshot.get("result"):
                mason_result["result"] = snapshot.get("result")
            if snapshot.get("error"):
                mason_result["error"] = snapshot.get("error")
        except Exception as error:
            mason_result["status"] = "queued"
            mason_result["execution_note"] = f"Mason task queued, but execute_now could not run Mason Worker: {error}"

    return {
        "status": "delegated",
        "delegated_to": "Mason",
        "task": task,
        "result": mason_result,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def atlas_command(task="", context=None):
    context = context or {}
    result = delegate_to_agent(task, context)

    if result.get("delegated_to") == "Mason" and result.get("status") in {"queued", "dispatched", "executed", "blocked"}:
        return _format_mason_delegation(task, result, context)

    return result


if __name__ == "__main__":
    print(delegate_to_agent("Mason inspect Hunter agent", {"agent": "mason", "mason_task_type": "inspect_file", "file": r"C:\Users\User\Desktop\PUTER\skills\hunter_agent.py"}))
