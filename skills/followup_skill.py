import json
import os


FOLLOWUPS_FILE = "memory/followups.json"


def _ensure_file():
    os.makedirs("memory", exist_ok=True)

    if not os.path.exists(FOLLOWUPS_FILE):
        with open(FOLLOWUPS_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


def _load_followups():
    _ensure_file()

    with open(FOLLOWUPS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def _save_followups(followups):
    _ensure_file()

    with open(FOLLOWUPS_FILE, "w", encoding="utf-8") as file:
        json.dump(followups, file, indent=4)


def add_followup(
    name,
    business,
    product,
    follow_up_date,
    status="Follow Up Needed"
):
    followups = _load_followups()

    record = {
        "id": len(followups) + 1,
        "name": name,
        "business": business,
        "product": product,
        "follow_up": follow_up_date,
        "status": status
    }

    followups.append(record)
    _save_followups(followups)

    return record


def list_followups():
    return _load_followups()