from pathlib import Path
import json
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
MISSION_FILE = ROOT / "missions" / "missions.json"
BUS_FILE = ROOT / "atlas_os" / "communications" / "executive_messages.json"

MISSION_FILE.parent.mkdir(parents=True, exist_ok=True)
BUS_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

mission_id = "MISSION_4TH_REVENUE_" + datetime.now().strftime("%Y%m%d_%H%M%S")

mission = {
    "mission_id": mission_id,
    "title": "4th of July Revenue Mission",
    "status": "active",
    "created_at": datetime.now().isoformat(timespec="seconds"),
    "commander": "Atlas",
    "goal": "Prepare money-making opportunities for Atlas, SIS Custom Creations, FRESH Apparel, digital products, and client acquisition.",
    "rules": [
        "Massive Action. Maximum Effort. Minimal Money.",
        "No public posts without Manny approval.",
        "No customer messages without Manny approval.",
        "No financial commitments without Manny approval.",
        "No paid ads or token-heavy actions without Manny approval.",
        "Prepare drafts, leads, offers, captions, product ideas, and next actions only."
    ],
    "assigned_agents": {
        "Hunter": "Find revenue opportunities and leads.",
        "Micah": "Draft social/content ideas.",
        "Amanda": "Draft outreach messages and marketplace copy.",
        "David": "Prepare CRM follow-up structure.",
        "Gideon": "Watch costs, margins, and pricing.",
        "Mason": "Keep systems running and queue technical fixes.",
        "Atlas": "Coordinate and prepare approval-ready actions for Manny."
    }
}

missions = load_json(MISSION_FILE, [])
if isinstance(missions, dict):
    missions = missions.get("missions", [])
missions.append(mission)
save_json(MISSION_FILE, missions)

messages = load_json(BUS_FILE, [])
for agent, assignment in mission["assigned_agents"].items():
    if agent == "Atlas":
        continue
    messages.append({
        "message_id": "msg_" + agent.lower() + "_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "from": "Atlas",
        "to": agent,
        "mission_id": mission_id,
        "priority": "high",
        "status": "new",
        "title": "4th of July Revenue Mission",
        "summary": assignment,
        "details": "Prepare approval-ready revenue actions only. Do not post, message, spend, or publish without Manny approval.",
        "next_action": "Prepare draft recommendations for Manny approval."
    })

save_json(BUS_FILE, messages)

print("ATLAS REVENUE MISSION ACTIVE")
print("Mission ID:", mission_id)
print("Agents queued:", ", ".join([a for a in mission["assigned_agents"] if a != "Atlas"]))
print("Public actions locked until Manny approval.")
