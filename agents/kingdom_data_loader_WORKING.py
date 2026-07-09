import json
from pathlib import Path

PUTER_ROOT = Path(__file__).resolve().parents[1]

KINGDOM_ITEMS_FILE = PUTER_ROOT / "data" / "kingdom_active_items.json"


def load_kingdom_items():
    if not KINGDOM_ITEMS_FILE.exists():
        return []

    with open(KINGDOM_ITEMS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("items", [])


if __name__ == "__main__":
    items = load_kingdom_items()

    print("KINGDOM ACTIVE ITEMS")
    print("--------------------")

    for item in items:
        print(item["name"])