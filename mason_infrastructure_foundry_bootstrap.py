import os
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
BRAIN = ROOT / "RAMFAM_KINGDOM_BRAIN"
FOUNDRY = BRAIN / "04_MASON_FOUNDRY"
FOUNDRY.mkdir(parents=True, exist_ok=True)

files_to_inspect = [
    ROOT / "mason_foundry_builder.py",
    ROOT / "mason_foundry_hermes.py",
    ROOT / "atlas_mission_runner.py",
    ROOT / "skills" / "mason_mission_runner.py",
    ROOT / "skills" / "mason_auto_builder.py",
    ROOT / "skills" / "mason_file_generator.py",
    ROOT / "skills" / "mason_capability_builder.py",
    ROOT / "skills" / "mason_capability_registry.py",
]

inspection = []
for file in files_to_inspect:
    if file.exists():
        text = file.read_text(encoding="utf-8", errors="ignore")
        inspection.append(f"FOUND: {file}\nLINES: {len(text.splitlines())}\n")
    else:
        inspection.append(f"MISSING: {file}\n")

plan = f"""# MASON INFRASTRUCTURE FOUNDRY PLAN

Generated: {datetime.now().isoformat()}

## Kingdom Course Correction

Manny approves.
Atlas orchestrates.
Mason builds.
Workers execute.

The Foundry must stop being only an agent-file generator and become an infrastructure generator.

## Inspection Results

{chr(10).join(inspection)}

## Current Diagnosis

Mason already has several builder pieces, but `mason_mission_runner.py` is only acting like a smoke-test mission runner right now.

It does not yet:
- read a directive file
- inspect existing systems deeply
- generate infrastructure plans
- create skill blueprints
- generate tests
- propose registry updates
- prepare full subsystem builds

## New Mason Capability Required

Create a reusable Mason Infrastructure Forge system.

This system should accept a plain-English system request and produce:

1. Main Python system file
2. Skills/blueprint markdown file
3. Test file
4. Data/report folder
5. Registry update recommendation
6. Verification command
7. Rollback notes
8. Manny approval gate

## First Blueprint Target

Use the already-working file:

C:\\Users\\User\\Desktop\\PUTER\\atlas_mission_runner.py

as the reference example for building future infrastructure systems.

## Required New Files

Mason should forge:

- C:\\Users\\User\\Desktop\\PUTER\\skills\\mason_infrastructure_forge.py
- C:\\Users\\User\\Desktop\\PUTER\\RAMFAM_KINGDOM_BRAIN\\04_MASON_FOUNDRY\\MISSION_RUNNER_SKILLS.md
- C:\\Users\\User\\Desktop\\PUTER\\test_mason_infrastructure_forge.py

## Success Test

Command:

python "C:\\Users\\User\\Desktop\\PUTER\\skills\\mason_infrastructure_forge.py" "Territory Manager"

Expected generated proposal:

- territory_manager.py
- TERRITORY_MANAGER_SKILLS.md
- test_territory_manager.py
- territory data folder
- registry update notes
- Manny approval required

## Foundry Law

Mason does not just build agents.

Mason builds Kingdom infrastructure.

Atlas does not hand-code infrastructure.

Atlas assigns infrastructure missions to Mason.

Manny approves before anything goes live.
"""

skills = """# MISSION_RUNNER_SKILLS.md

## Purpose

Mission Runner is the Kingdom execution engine.

It receives an Atlas-approved mission, routes it through assigned workers, collects their reports, creates an executive package, and saves mission history.

## Required Capabilities

- Accept mission text
- Call Atlas Orchestrator
- Identify assigned workers
- Load worker modules
- Execute worker functions
- Collect worker reports
- Save latest mission report
- Save timestamped archive
- Mark Manny approval required
- Return final executive package

## Build Pattern for Future Systems

Every Mason-forged infrastructure system must include:

1. Main system file
2. Skills markdown file
3. Test file
4. Data/report folder when needed
5. Registry update notes when needed
6. Verification command
7. Rollback notes
8. Manny approval gate

## Example Future Request

Mason, build a Territory Manager system.

## Expected Output

- territory_manager.py
- TERRITORY_MANAGER_SKILLS.md
- test_territory_manager.py
- RAMFAM_KINGDOM_BRAIN/07_TERRITORIES
- registry update recommendation
- verification command
- rollback notes
"""

forge_prompt = """MASON FORGE REQUEST

Read:
C:\\Users\\User\\Desktop\\PUTER\\RAMFAM_KINGDOM_BRAIN\\04_MASON_FOUNDRY\\MASON_INFRASTRUCTURE_FOUNDRY_PLAN.md
C:\\Users\\User\\Desktop\\PUTER\\RAMFAM_KINGDOM_BRAIN\\04_MASON_FOUNDRY\\MISSION_RUNNER_SKILLS.md

Then forge:
C:\\Users\\User\\Desktop\\PUTER\\skills\\mason_infrastructure_forge.py

Purpose:
Teach Mason to generate complete Kingdom infrastructure systems from plain-English blueprints.

Do not overwrite working files without backup.
Every generated system must include a test and Manny approval gate.
"""

(FOUNDRY / "MASON_INFRASTRUCTURE_FOUNDRY_PLAN.md").write_text(plan, encoding="utf-8")
(FOUNDRY / "MISSION_RUNNER_SKILLS.md").write_text(skills, encoding="utf-8")
(FOUNDRY / "MASON_FORGE_REQUEST_INFRASTRUCTURE.txt").write_text(forge_prompt, encoding="utf-8")

print("MASON INFRASTRUCTURE FOUNDRY BOOTSTRAP COMPLETE")
print(FOUNDRY / "MASON_INFRASTRUCTURE_FOUNDRY_PLAN.md")
print(FOUNDRY / "MISSION_RUNNER_SKILLS.md")
print(FOUNDRY / "MASON_FORGE_REQUEST_INFRASTRUCTURE.txt")
