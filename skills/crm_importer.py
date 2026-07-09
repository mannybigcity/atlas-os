from pathlib import Path
from datetime import datetime
import json

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
BRAIN = ROOT / "RAMFAM_KINGDOM_BRAIN"
DATA_FOLDER = BRAIN / "07_CRM_IMPORTER"
DATA_FOLDER.mkdir(parents=True, exist_ok=True)

def crm_importer_system(task, context=None):
    """
    Crm Importer system forged by Mason Infrastructure Forge.
    Manny approval is required before live use.
    """
    context = context or {}
    report = {
        "system": "Crm Importer",
        "status": "proposal_ready",
        "task": task,
        "context": context,
        "approval_required": True,
        "built_by": "Mason Infrastructure Forge",
        "orchestrated_by": "Atlas",
        "timestamp": datetime.now().isoformat(),
        "next_action": "Manny review and approval required before deployment."
    }

    latest_path = DATA_FOLDER / "crm_importer_latest.json"
    archive_path = DATA_FOLDER / f"crm_importer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    latest_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    archive_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report

if __name__ == "__main__":
    result = crm_importer_system("Smoke test for Crm Importer", {"requested_by": "Mason"})
    print(json.dumps(result, indent=2))
