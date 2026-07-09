from pathlib import Path
from datetime import datetime
import json

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
BRAIN = ROOT / "RAMFAM_KINGDOM_BRAIN"
DATA_FOLDER = BRAIN / "07_TERRITORY_MANAGER"
DATA_FOLDER.mkdir(parents=True, exist_ok=True)

def territory_manager_system(task, context=None):
    """
    Territory Manager system forged by Mason Infrastructure Forge.
    Manny approval is required before live use.
    """
    context = context or {}
    report = {
        "system": "Territory Manager",
        "status": "proposal_ready",
        "task": task,
        "context": context,
        "approval_required": True,
        "built_by": "Mason Infrastructure Forge",
        "orchestrated_by": "Atlas",
        "timestamp": datetime.now().isoformat(),
        "next_action": "Manny review and approval required before deployment."
    }

    latest_path = DATA_FOLDER / "territory_manager_latest.json"
    archive_path = DATA_FOLDER / f"territory_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    latest_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    archive_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report

if __name__ == "__main__":
    result = territory_manager_system("Smoke test for Territory Manager", {"requested_by": "Mason"})
    print(json.dumps(result, indent=2))
