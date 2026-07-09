# ATLAS CODEBASE INVENTORY

**Purpose**

This document is the authoritative inventory of the Atlas Operating System.

Its purpose is to identify what already exists before adding new code.

---

# Core Rule

Do not rebuild existing functionality.

Extend, improve, or replace only after understanding the current implementation.

---

# Current Findings

## brain/

Purpose:
Core AI reasoning.

Files:

- conversation_memory.py
- decision_engine.py
- intent_router.py
- personality_layer.py

Status:
Needs review.

---

## memory/

Purpose:
Persistent memory storage.

Files:

- memory.py
- memory.json
- approval_memory.json
- followups.json
- invoices.json
- proposals.json
- memory/agents.json

Status:
Existing production memory system.

---

## missions/

Purpose:
Mission tracking.

Files:

- missions.json
- mission_skill.py

Status:
Needs review.

---

## agents/

Purpose:
Executive team.

Major components discovered:

- atlas_orchestrator.py
- atlas_delegation_router.py
- atlas_decision_engine.py
- atlas_orchestrated_response.py
- atlas_mason_kanban_bridge.py
- mason_context_loader.py
- kingdom_data_loader.py
- mason_worker.py

Status:
Major executive architecture already exists.

---

# Next Goal

Determine:

1. What each module already does.
2. Which files are current.
3. Which backups can be archived.
4. Which systems should become part of Atlas OS.
5. What should NOT be rewritten.

---

# Atlas OS Role

Atlas OS is not a replacement for the existing codebase.

Atlas OS becomes the governance layer that coordinates:

- Brain
- Memory
- Agents
- Missions
- CRM
- Client Data
- Skills
- Workflows

through Atlas Mission Control.

---

## agents/atlas_orchestrator.py

Purpose:
Routes Manny's request to the correct Atlas executive agent.

What it does:
- Answers Atlas identity and authority questions directly.
- Enforces Manny as final authority.
- Maintains allowed write-location policy.
- Detects named agents in user requests.
- Routes by keyword to Taylor, Ranger, David, Hunter, Gideon, Amanda, Scout, Micah, or Mason.
- Defaults build/system/code work to Mason.
- Calls atlas_agent_delegation.delegate_to_agent().
- Returns routed agent, reason, result, and timestamp.

Status:
KEEP. This is a core Atlas OS orchestration file.

Atlas OS Role:
Use this as the main executive router. Do not rebuild it.
