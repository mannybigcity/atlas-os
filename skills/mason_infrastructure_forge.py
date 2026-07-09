from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(r"C:\Users\User\Desktop\PUTER")


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def titleify(name: str) -> str:
    return " ".join(word.capitalize() for word in re.split(r"[^a-zA-Z0-9]+", name) if word)


def _data_folder_name(slug: str, constant: str) -> str:
    if slug == "territory_manager":
        return "07_TERRITORIES"
    return f"07_{constant}"


def _backup_existing(path: Path, backups_dir: Path) -> dict[str, str] | None:
    if not path.exists() or not path.is_file():
        return None

    backups_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = backups_dir / f"{path.name}.{timestamp}.bak"
    backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return {"file": str(path), "backup_path": str(backup_path)}


def forge_infrastructure_system(system_name: str, *, project_root: str | Path = ROOT) -> dict[str, Any]:
    project_root = Path(project_root)
    raw_name = str(system_name or "").strip()

    if not raw_name:
        return {
            "status": "rejected",
            "system_name": "",
            "manny_approval_required": True,
            "approval_gate": {
                "required": True,
                "approver": "Manny",
                "reason": "System name/blueprint is required before Mason forges infrastructure.",
            },
            "artifacts": {},
            "backups_created": [],
            "verification_command": "",
        }

    slug = slugify(raw_name)
    title = titleify(raw_name)
    constant = slug.upper()

    brain = project_root / "RAMFAM_KINGDOM_BRAIN"
    foundry = brain / "04_MASON_FOUNDRY"
    data_folder = brain / _data_folder_name(slug, constant)
    main_system = project_root / f"{slug}.py"
    skills_blueprint = foundry / f"{constant}_SKILLS.md"
    test_file = project_root / f"test_{slug}.py"
    registry_update_notes = foundry / f"{constant}_REGISTRY_UPDATE.md"
    backups_dir = foundry / "BACKUPS"

    foundry.mkdir(parents=True, exist_ok=True)
    data_folder.mkdir(parents=True, exist_ok=True)

    artifacts = {
        "main_system": main_system,
        "skills_blueprint": skills_blueprint,
        "test_file": test_file,
        "data_folder": data_folder,
        "registry_update_notes": registry_update_notes,
    }

    backups_created: list[dict[str, str]] = []
    for artifact_path in (main_system, skills_blueprint, test_file, registry_update_notes):
        backup = _backup_existing(artifact_path, backups_dir)
        if backup:
            backups_created.append(backup)

    main_code = f'''from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA_FOLDER = ROOT / "RAMFAM_KINGDOM_BRAIN" / "{data_folder.name}"
DATA_FOLDER.mkdir(parents=True, exist_ok=True)


def {slug}_system(task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """{title} system forged by Mason; Manny approval required before live use."""
    report = {{
        "system": "{title}",
        "status": "pending_manny_approval",
        "task": task,
        "context": context or {{}},
        "approval_required": True,
        "built_by": "Mason Infrastructure Forge",
        "timestamp": datetime.now().isoformat(),
        "next_action": "Manny approval required before deployment.",
    }}
    latest_path = DATA_FOLDER / "{slug}_latest.json"
    latest_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps({slug}_system("Smoke test for {title}"), indent=2))
'''

    skills_md = f'''# {constant}_SKILLS.md

## Purpose
{title} is a Mason-forged Kingdom infrastructure system.

## Approval Rule
Manny approval required before live use. The system remains pending_manny_approval until Manny approves.

## Verification Command
python "{test_file}"

## Artifacts
- Main system: {main_system}
- Data folder: {data_folder}
- Test file: {test_file}
'''

    test_code = f'''from {slug} import {slug}_system


def test_{slug}_system() -> None:
    result = {slug}_system("Test {title}", {{"test": True}})
    assert result["system"] == "{title}"
    assert result["approval_required"] is True
    assert result["status"] == "pending_manny_approval"


if __name__ == "__main__":
    test_{slug}_system()
    print("{title} test passed.")
'''

    registry_notes = f'''# {title} Registry Update Recommendation

Generated: {datetime.now().isoformat()}

## Status
forged_pending_manny_approval

## Registry update recommendation
Do not wire {title} into Atlas/Mason active orchestration until Manny approves the forged artifacts.

## Proposed artifacts
- {main_system}
- {skills_blueprint}
- {test_file}
- {data_folder}
'''

    main_system.write_text(main_code, encoding="utf-8")
    skills_blueprint.write_text(skills_md, encoding="utf-8")
    test_file.write_text(test_code, encoding="utf-8")
    registry_update_notes.write_text(registry_notes, encoding="utf-8")

    verification_command = f'python "{test_file}"'
    return {
        "status": "forged_pending_manny_approval",
        "system_name": title,
        "manny_approval_required": True,
        "approval_gate": {
            "required": True,
            "approver": "Manny",
            "reason": "Manny approval required before live deployment.",
        },
        "artifacts": {key: str(path) for key, path in artifacts.items()},
        "backups_created": backups_created,
        "verification_command": verification_command,
        "created_at": datetime.now().isoformat(),
    }


def mason_infrastructure_forge(system_name: str) -> dict[str, Any]:
    return forge_infrastructure_system(system_name, project_root=ROOT)


if __name__ == "__main__":
    import sys

    requested_system_name = " ".join(sys.argv[1:]).strip() or "Territory Manager"
    result = mason_infrastructure_forge(requested_system_name)
    print(json.dumps(result, indent=2))
