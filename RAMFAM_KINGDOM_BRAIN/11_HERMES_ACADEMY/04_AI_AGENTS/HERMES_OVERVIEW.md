# HERMES OVERVIEW

Purpose:
Hermes is a multi-agent AI framework designed to coordinate specialized AI agents, tools, memory systems, planning systems, and automation workflows.

Core Philosophy:

* Divide work among specialized agents.
* Give agents reusable skills.
* Allow agents to use tools.
* Maintain memory across tasks.
* Use planning systems to break large goals into steps.
* Enable delegation between agents.

Major Components:

agent/
Core agent logic responsible for decision making and execution.

skills/
Reusable capabilities that agents can invoke to perform tasks.

tools/
External systems and integrations available to agents.

plans/
Planning systems used to create and execute multi-step objectives.

gateway/
Communication layer that routes messages between agents, tools, and services.

providers/
Connections to AI model providers and LLM backends.

web/
Web interfaces, dashboards, APIs, and integrations.

Key Lessons for RAMFAM Kingdom:

1. Knowledge should be documented before automation.
2. Agents should specialize in specific responsibilities.
3. Memory should be organized and searchable.
4. Skills should be reusable across agents.
5. Large objectives should be broken into smaller delegated tasks.
6. Systems should be designed for scalability and long-term operation.
