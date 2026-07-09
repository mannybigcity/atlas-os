# HERMES ACCELERATION PLAN

Prepared for: ATLAS / RAMFAM Kingdom
Mission: Increase Kingdom development speed without adding unnecessary complexity.
Audit posture: No installations performed. No production files modified. Report only.

---

## SECTION 1: Current Hermes Capability Inventory

### Installation Snapshot

- Hermes Agent version: v0.16.0 (2026.6.5)
- Installed Hermes project path: `C:\Users\User\AppData\Local\hermes\hermes-agent`
- Runtime Python: 3.11.15
- Active model/provider: gpt-5.5 via OpenAI API
- Gateway service: stopped
- Scheduled jobs: 0
- Installed skills: 60 total
- Skill source mix: 60 builtin, 0 hub-installed, 0 local custom
- Skill status: 60 enabled, 0 disabled
- No new skills were installed during this audit.

### Enabled Tool Acceleration

Current enabled Hermes toolsets that directly accelerate development:

- `terminal` — run tests, app commands, git, scripts, process checks.
- `file` — read, search, write, and patch project files.
- `code_execution` — sandboxed Python execution for quick validation and data shaping.
- `skills` — load reusable workflows for debugging, planning, TDD, reviews, GitHub work, and coding-agent delegation.
- `todo` — in-session task tracking for multi-step missions.
- `memory` — persistent user/project facts across sessions.
- `session_search` — recall prior decisions and previous work.
- `delegation` — spawn isolated subagents for parallel analysis.
- `cronjob` — scheduled recurring Hermes tasks.
- `web` / `browser` — current documentation and web-app validation when needed.
- `vision` / `image_gen` / `tts` — useful, but lower priority for core development speed.

Potential future toolsets currently disabled:

- `context_engine` — could help if Kingdom Brain / PUTER grows into a larger searchable context system.
- `moa` — Mixture of Agents; could help for high-stakes review but adds complexity.
- `video`, `video_gen`, `x_search`, `homeassistant`, `spotify`, `yuanbao` — not core to ATLAS development speed today.

### Installed Skill Catalog

#### Autonomous AI Agents

- `claude-code` — delegate coding to Claude Code CLI for features and PRs.
- `codex` — delegate coding to OpenAI Codex CLI for features and PRs.
- `hermes-agent` — configure, extend, or troubleshoot Hermes Agent.
- `opencode` — delegate coding to OpenCode CLI for features and PR review.

#### Software Development

- `hermes-agent-skill-authoring` — author in-repo `SKILL.md` files with correct frontmatter and structure.
- `node-inspect-debugger` — debug Node.js with inspector protocol.
- `plan` — write actionable implementation plans to `.hermes/plans/`.
- `requesting-code-review` — pre-commit review, security scan, quality gates, and auto-fix workflow.
- `simplify-code` — parallel three-agent cleanup of recent code changes.
- `spike` — throwaway experiments to validate an idea before production build.
- `systematic-debugging` — four-phase root-cause debugging before fixing.
- `test-driven-development` — RED-GREEN-REFACTOR workflow and test-first implementation.

#### GitHub / Repository Operations

- `codebase-inspection` — inspect codebases with `pygount`: LOC, languages, ratios.
- `github-auth` — GitHub authentication setup.
- `github-code-review` — review PR diffs and post inline comments via `gh` or REST.
- `github-issues` — create, triage, label, and assign GitHub issues.
- `github-pr-workflow` — branch, commit, open PR, monitor CI, merge.
- `github-repo-management` — clone, create, fork repos, manage remotes and releases.

#### Data Science / Python Exploration

- `jupyter-live-kernel` — iterative Python analysis through a live Jupyter kernel.

#### Documentation / Knowledge / Notes

- `obsidian` — read, search, create, and edit Obsidian vault notes.
- `ocr-and-documents` — extract text from PDFs and scanned documents.
- `llm-wiki` — build/query Karpathy-style interlinked LLM wiki knowledge bases.
- `youtube-content` — convert YouTube transcripts into summaries, posts, and blog drafts.

#### Productivity / Business Systems

- `airtable` — Airtable record CRUD, filters, and upserts.
- `google-workspace` — Gmail, Calendar, Drive, Docs, and Sheets workflows.
- `maps` — geocode, POIs, routes, and timezones.
- `notion` — Notion pages, databases, markdown, and Workers workflows.
- `powerpoint` — create, read, and edit `.pptx` decks.
- `teams-meeting-pipeline` — operate Teams meeting summary pipeline.
- `nano-pdf` — edit PDF text and titles.
- `himalaya` — IMAP/SMTP email from terminal.

#### Research / Market Intelligence

- `arxiv` — search arXiv papers.
- `blogwatcher` — monitor blogs and RSS/Atom feeds.
- `polymarket` — query Polymarket markets and prices.

#### MLOps / Model Work

- `huggingface-hub` — search/download/upload models and datasets.
- `llama-cpp` — local GGUF inference and Hugging Face model discovery.
- `segment-anything-model` — zero-shot image segmentation.
- `weights-and-biases` — experiment tracking and model registry.

#### Creative / UI / Visual Communication

- `architecture-diagram` — dark-themed SVG architecture/cloud diagrams.
- `ascii-art` — ASCII art via pyfiglet/cowsay/boxes/image-to-ascii.
- `ascii-video` — convert video/audio to colored ASCII MP4/GIF.
- `baoyu-infographic` — infographic generation with many layouts and styles.
- `claude-design` — one-off HTML landing pages, decks, and prototypes.
- `comfyui` — image, video, and audio generation through ComfyUI.
- `design-md` — author/validate/export Google `DESIGN.md` token specs.
- `excalidraw` — hand-drawn Excalidraw JSON diagrams.
- `humanizer` — make text sound more human and less AI-generated.
- `manim-video` — 3Blue1Brown-style math/algorithm animations.
- `p5js` — generative art and interactive browser sketches.
- `popular-web-designs` — 54 real design systems as HTML/CSS references.
- `pretext` — creative browser demos using text layout as geometry.
- `sketch` — throwaway HTML mockups and design variants.
- `songwriting-and-ai-music` — songwriting craft and Suno-style prompts.
- `touchdesigner-mcp` — control TouchDesigner via MCP.

#### Media / Smart Home / Miscellaneous

- `gif-search` — search and download GIFs from Tenor.
- `heartmula` — Suno-like song generation from lyrics and tags.
- `songsee` — audio spectrograms and feature extraction.
- `openhue` — Philips Hue lights, scenes, and rooms.
- `dogfood` — exploratory QA of web apps.
- `yuanbao` — Yuanbao groups and member queries.

### Skills That Directly Accelerate Requested Areas

- Python development: `test-driven-development`, `systematic-debugging`, `jupyter-live-kernel`, `spike`.
- Code generation: `claude-code`, `codex`, `opencode`, `plan`, `spike`.
- Debugging: `systematic-debugging`, `node-inspect-debugger`, `dogfood`, `requesting-code-review`.
- Refactoring: `simplify-code`, `requesting-code-review`, `test-driven-development`, `codebase-inspection`.
- Project planning: `plan`, `spike`, `github-issues`, `github-pr-workflow`.
- File analysis: `codebase-inspection`, `ocr-and-documents`, `obsidian`, `llm-wiki`.
- Repository analysis: `codebase-inspection`, `github-code-review`, `github-repo-management`, `github-pr-workflow`.
- Testing: `test-driven-development`, `requesting-code-review`, `dogfood`, `systematic-debugging`.
- Documentation: `plan`, `architecture-diagram`, `excalidraw`, `obsidian`, `hermes-agent-skill-authoring`, `llm-wiki`.

---

## SECTION 2: Top 10 Hermes Skills for ATLAS

| Rank | Skill name | Purpose | Why it helps ATLAS | Example use case | Priority score |
|---:|---|---|---|---|---:|
| 1 | `systematic-debugging` | Enforces root-cause debugging before code changes. | Prevents random fixes, protects customer/revenue flows, and reduces repeated breakage in the PUTER Flask/CRM system. | Diagnose why a CRM route fails before editing `app.py` or `crm/crm_skill.py`. | 10 |
| 2 | `test-driven-development` | Applies RED-GREEN-REFACTOR and requires tests before behavior changes. | Speeds development by making changes safer; every new Kingdom behavior gets a regression shield. | Add a failing test for a lead/customer workflow, implement the route fix, then refactor safely. | 10 |
| 3 | `requesting-code-review` | Runs pre-commit review, security checks, quality gates, and auto-fix workflow. | Highest near-term guardrail for ATLAS: ships faster without fragile production changes. | Before declaring a Mason build complete, review the diff and run relevant tests. | 10 |
| 4 | `plan` | Creates actionable implementation plans with exact paths, tasks, and verification. | Converts Kingdom commands into executable engineering missions without letting scope sprawl. | Plan “add customer follow-up automation” into specific files, tests, and rollout steps. | 9 |
| 5 | `codebase-inspection` | Measures repository structure, language mix, LOC, and hotspots with `pygount`. | Gives Mason a map before refactoring; helps find oversized modules and hidden complexity. | Identify large files like `app.py` and prioritize modular extraction only where it pays off. | 9 |
| 6 | `spike` | Runs throwaway experiments before production implementation. | Lets ATLAS validate risky ideas fast while protecting production files. | Prototype a lead-scoring formula against sample CSV data before adding it to the CRM. | 8 |
| 7 | `simplify-code` | Uses parallel cleanup review to find simplification opportunities. | Reduces technical debt after fast builds without slowing initial execution. | After a feature batch, ask for duplication, complexity, and reuse opportunities. | 8 |
| 8 | `claude-code` | Delegates bounded coding tasks to Claude Code CLI when installed/authenticated. | Can multiply Mason throughput for feature branches or PR-ready edits, especially on isolated tasks. | Delegate “add API tests and update docs for CRM status route” to a coding worker. | 8 |
| 9 | `github-pr-workflow` | Manages branch, commit, PR, CI, and merge workflow. | Adds disciplined shipping once ATLAS moves into PR-based deployment. | Create a feature branch, commit verified changes, open PR, monitor checks. | 7 |
| 10 | `jupyter-live-kernel` | Enables iterative Python exploration in a live notebook kernel. | Speeds CRM data analysis, revenue scoring, lead ranking, and operational reporting. | Explore lead CSVs, build scoring rules, then convert proven logic into tests/code. | 7 |

### Honorable Mentions

- `codex` — useful alternative coding-agent delegate if OpenAI Codex auth is configured.
- `opencode` — useful provider-flexible coding delegate; overlaps with `claude-code` and `codex`.
- `github-code-review` — high value when ATLAS uses GitHub PR review as the default workflow.
- `hermes-agent-skill-authoring` — valuable for turning recurring Kingdom procedures into reusable local Hermes skills.
- `dogfood` — valuable for browser-based QA of web app flows after UI changes.
- `architecture-diagram` / `excalidraw` — useful when explaining or documenting system architecture.

---

## SECTION 3: Recommended Installations

No installations should be performed automatically. Recommended candidates should be inspected and approved first.

### Recommended Hermes Skills Not Currently Installed

| Priority | Skill / identifier | Purpose | Why ATLAS should consider it | Complexity | Recommendation |
|---:|---|---|---|---|---|
| 1 | `official/software-development/code-wiki` | Generate codebase wiki docs and Mermaid diagrams for a repository. | ATLAS needs fast re-entry into PUTER structure across sessions. A code wiki would reduce rediscovery time for Flask routes, agents, CRM logic, and Kingdom Brain components. | Low | Install first after approval. |
| 2 | `official/software-development/rest-graphql-debug` | Debug REST/GraphQL APIs through structured status/auth/schema/repro workflows. | PUTER is a Flask app; this directly speeds route, payload, auth/session, webhook, PayPal, and CRM API debugging. | Low | Install second after approval. |
| 3 | A trusted Flask-specific skill, if available after inspection | Flask routing, app context, templates, sessions, API patterns, and deployment checks. | `requirements.txt` shows Flask is the core web framework. A focused Flask skill could reduce framework-specific mistakes. | Medium | Search/inspect trusted sources before installing. |
| 4 | A trusted pytest-specific skill, if available after inspection | Pytest fixture, parametrization, API test, and coverage workflow. | PUTER already has Python tests; deeper test workflow would speed safer changes. | Medium | Search/inspect trusted sources before installing. |
| 5 | `official/research/gitnexus-explorer` or similar code graph tooling | Codebase knowledge graph and navigation. | Useful if PUTER grows beyond quick file search and manual tracing. | Medium/high | Defer until scale demands it. |
| 6 | `official/mcp/fastmcp` | Build Python MCP servers. | Useful if ATLAS should expose Kingdom operations as reusable MCP tools. | Medium | Defer until an integration need is clear. |
| 7 | `official/mlops/chroma` or similar vector DB/RAG skill | Semantic search over documents/data. | Could support searchable Kingdom Brain, customer records, and SOP retrieval. | Medium/high | Defer unless retrieval becomes a revenue blocker. |

### Installation Discipline

- Install only one or two acceleration skills at a time.
- Prefer official skills before community skills.
- Inspect a skill before installing it.
- Do not install overlapping skills unless they serve distinct workflows.
- After installing, immediately test the skill on a low-risk task and document when to use it.

---

## SECTION 4: 30-Day Development Speed Improvement Plan

### Week 1 — Stabilize the Development Loop

Goal: Make every ATLAS code change faster to verify and harder to break.

Actions:

1. Use `systematic-debugging` for every bug or broken behavior.
2. Use `test-driven-development` for every new behavior and every bug fix.
3. Use `requesting-code-review` before any meaningful code change is considered done.
4. Use `codebase-inspection` to create a baseline map of PUTER size, hotspots, and high-risk files.
5. Standardize verification commands for the current Flask/CRM app:
   - `python -m unittest test_crm_system.py test_crm_api.py -v`
   - targeted tests for Mason/Atlas files when those systems are touched
   - route smoke checks for customer-facing flows when app routes change

Expected result:

- Less debugging guesswork.
- Fewer regressions.
- Faster confidence before customer-facing work ships.

### Week 2 — Reduce Context Reload Time

Goal: Make future Mason/ATLAS sessions start with a map instead of rediscovery.

Actions:

1. After approval, install `official/software-development/code-wiki`.
2. Generate a lightweight code wiki outside production runtime paths.
3. Document the system at a practical level:
   - Flask entrypoints
   - CRM data flow
   - agent delegation flow
   - Mason verifier/retry engine
   - customer/revenue-critical routes
4. Keep documentation operational and short enough to stay useful.

Expected result:

- Faster onboarding for future Hermes sessions.
- Less repeated file tracing.
- More time spent building instead of rediscovering.

### Week 3 — Improve API Debugging and Test Coverage

Goal: Make Flask/API bugs easier to reproduce and fix.

Actions:

1. After approval, install `official/software-development/rest-graphql-debug`.
2. Create an ATLAS API debug checklist:
   - endpoint
   - method
   - payload
   - auth/session expectations
   - status code
   - response body
   - expected CRM/customer side effect
3. Add regression tests around the highest-value customer/revenue routes.
4. Use `dogfood` for browser-based exploratory QA when UI flows change.

Expected result:

- Faster route debugging.
- Better customer-flow protection.
- Less risk from Flask route changes.

### Week 4 — Add Controlled Parallel Throughput

Goal: Increase speed without adding chaos.

Actions:

1. Use `plan` before any multi-file or multi-agent mission.
2. Use `spike` for risky or unclear ideas before touching production code.
3. Activate one coding-agent path only after CLI/auth readiness is confirmed:
   - preferred first candidate: `claude-code`
   - fallback candidates: `codex`, `opencode`
4. Use `simplify-code` after meaningful batches of changes, not after every tiny edit.
5. If GitHub becomes the shipping lane, use `github-pr-workflow` and `github-code-review` as the default release discipline.

Expected result:

- Faster implementation of bounded tasks.
- Lower technical debt.
- Better protection of the King’s focus and customer commitments.

---

## Final Question

What is the single highest ROI Hermes capability that should be activated next?

Answer: `requesting-code-review` as the default ATLAS pre-ship gate.

Why this is highest ROI:

- It is already installed and enabled.
- It requires no new installation.
- It adds minimal process overhead.
- It protects revenue/customer workflows by catching mistakes before completion.
- It fits the Kingdom principle: systems before scale.

Operating rule:

> No meaningful ATLAS code change is complete until `requesting-code-review` has reviewed the diff and relevant tests pass.
