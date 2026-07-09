# MASON INFRASTRUCTURE FOUNDRY DIRECTIVE

## PURPOSE
Teach Mason to build Kingdom infrastructure, not just individual agents.

## COURSE CORRECTION
Manny and ChatGPT should not manually hand-build every system.

Correct Kingdom order:

Manny approves.
Atlas orchestrates.
Mason builds.
Workers execute.

## CURRENT VERIFIED SYSTEM
atlas_mission_runner.py already works.

It:
- calls Atlas Orchestrator
- loads assigned workers
- executes workers
- collects reports
- builds executive package
- saves mission history to RAMFAM_KINGDOM_BRAIN\06_MISSIONS

## NEXT MASON CAPABILITY
Mason must learn to forge complete infrastructure systems from a plain-English blueprint.

A Mason-forged system should include:
- main Python file
- skill/blueprint markdown file
- test file
- registry entry if needed
- memory/report folder if needed
- verification command
- rollback notes

## FIRST TARGET
Forge a reusable MissionRunner system from this existing working example:

C:\Users\User\Desktop\PUTER\atlas_mission_runner.py

## SUCCESS CONDITION
Mason can receive a request like:

"Mason, build a Territory Manager system."

And generate:
- territory_manager.py
- TERRITORY_MANAGER_SKILLS.md
- test_territory_manager.py
- registry update notes
- data folder
- verification steps

## RULES
1. Do not overwrite working files unless creating a backup first.
2. Save new blueprints inside:
   C:\Users\User\Desktop\PUTER\RAMFAM_KINGDOM_BRAIN\04_MASON_FOUNDRY
3. Save generated systems in correct project folders.
4. Every build must include a test.
5. Every build must include Manny approval required.
6. Atlas remains orchestrator.
7. Mason remains builder.
8. Workers remain executors.

## MASON TASK NOW
Inspect existing Mason foundry files.
Inspect atlas_mission_runner.py.
Create a recommendation for how Mason can forge future infrastructure systems automatically.

Output the recommendation to:

C:\Users\User\Desktop\PUTER\RAMFAM_KINGDOM_BRAIN\04_MASON_FOUNDRY\MASON_INFRASTRUCTURE_FOUNDRY_PLAN.md
