import json
import os
from datetime import datetime

PROPOSALS_FILE = "memory/proposals.json"
APPROVAL_MEMORY_FILE = "memory/approval_memory.json"


def _ensure_file(file_path, default_data):
    os.makedirs("memory", exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=4)


def _load_json(file_path, default_data):
    _ensure_file(file_path, default_data)

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def create_proposal(prospect, contact_name, service, message):
    proposals = _load_json(PROPOSALS_FILE, [])

    proposal = {
        "id": len(proposals) + 1,
        "created_at": datetime.now().isoformat(),
        "prospect": prospect,
        "contact_name": contact_name,
        "service": service,
        "message": message,
        "status": "waiting_for_manny",
        "approved": False,
        "manny_feedback": ""
    }

    proposals.append(proposal)
    _save_json(PROPOSALS_FILE, proposals)

    return proposal


def list_pending_proposals():
    proposals = _load_json(PROPOSALS_FILE, [])
    return [p for p in proposals if p["approved"] is False]


def approve_proposal(proposal_id, manny_feedback="Approved by Manny"):
    proposals = _load_json(PROPOSALS_FILE, [])

    for proposal in proposals:
        if proposal["id"] == proposal_id:
            proposal["approved"] = True
            proposal["status"] = "approved_by_manny"
            proposal["manny_feedback"] = manny_feedback
            proposal["approved_at"] = datetime.now().isoformat()

            _save_json(PROPOSALS_FILE, proposals)
            _save_approval_memory(proposal, manny_feedback)

            return proposal

    return None


def _save_approval_memory(proposal, manny_feedback):
    approval_memory = _load_json(APPROVAL_MEMORY_FILE, [])

    memory_item = {
        "created_at": datetime.now().isoformat(),
        "proposal_id": proposal["id"],
        "prospect": proposal["prospect"],
        "service": proposal["service"],
        "approved_message": proposal["message"],
        "manny_feedback": manny_feedback,
        "lesson": "Manny approved this proposal. Use this as an example of his preferred sales style."
    }

    approval_memory.append(memory_item)
    _save_json(APPROVAL_MEMORY_FILE, approval_memory)


def list_approval_memory():
    return _load_json(APPROVAL_MEMORY_FILE, [])