from pathlib import Path
import json
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
ATLAS_OS = ROOT / "atlas_os"
BUS_FILE = ATLAS_OS / "communications" / "executive_messages.json"

BUS_FILE.parent.mkdir(parents=True, exist_ok=True)
if not BUS_FILE.exists():
    BUS_FILE.write_text("[]", encoding="utf-8")

def _load():
    try:
        return json.loads(BUS_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return []

def _save(messages):
    BUS_FILE.write_text(json.dumps(messages, indent=2), encoding="utf-8")

def _message_id():
    return "msg_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def send_message(sender, to, title, summary="", mission_id="", priority="normal", details="", next_action="", status="new", task="", result_summary="", result_file=""):
    messages = _load()
    message = {
        "message_id": _message_id(),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "from": sender,
        "to": to,
        "mission_id": mission_id,
        "priority": priority,
        "status": status,
        "title": title,
        "summary": summary,
        "task": task,
        "result_summary": result_summary or summary,
        "result_file": result_file,
        "details": details,
        "next_action": next_action
    }
    messages.append(message)
    _save(messages)
    return message

def record_mission_update(agent, mission_id, task, status, summary="", result_file="", priority="normal", details=""):
    status = str(status or "new").strip().lower()
    if status not in {"new", "working", "complete", "blocked"}:
        status = "working"
    title_task = str(task or "Mission")[:80]
    return send_message(
        "Atlas",
        agent,
        f"Mission {status}: {title_task}",
        summary=summary,
        mission_id=mission_id,
        priority=priority,
        details=details,
        status=status,
        task=task,
        result_summary=summary,
        result_file=result_file,
    )

def get_messages(to=None, status=None):
    messages = _load()
    if to:
        messages = [m for m in messages if str(m.get("to","")).lower() == str(to).lower()]
    if status:
        messages = [m for m in messages if m.get("status") == status]
    return messages

if __name__ == "__main__":
    print(send_message("Atlas", "Mason", "Executive Bus installed", "Atlas OS communication bus is now working."))
