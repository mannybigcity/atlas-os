# MISSION_RUNNER_SKILLS.md

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
