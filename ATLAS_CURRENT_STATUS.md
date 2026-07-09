# ATLAS CURRENT STATUS

Last updated: 2026-06-30 10:57:50 CDT
Issue: ATL-56 - Stabilize Atlas and prepare it for demo/deployment

## Budget / model posture
- Manny asked: "Can you switch from GPT's to save money?"
- Action taken: kept this heartbeat deterministic/local-first: file reads, targeted edits, Python/Flask test-client checks, and unittest verification. No external OpenAI/API calls were made by the app during verification.
- Note: the active Paperclip/Hermes run model is controlled by the harness/session config. Atlas can reduce spend by avoiding large AI generations and using local commands first; persistent model/provider switching should be done in Hermes/Paperclip runtime config if Manny wants it changed globally.

## App entry point
- `app.py` is the Flask entry point.
- Local start command from repo root: `python app.py`
- Main local URL: `http://127.0.0.1:5000/`

## Demo-ready route map
- Executive Dashboard: `/`, `/neural`, `/executive-dashboard`
- Customer Dashboard: `/customer-dashboard`
- Client / CRM area: `/crm`, `/client-crm`
- Atlas Chat / Website Chat area: `/atlas-chat`, `/website-chat` redirect to `/neural#atlas-chat`
- Business Assessment / Intake page: `/business-assessment`, `/free-business-assessment` redirect to `/sis/#custom-orders`
- SIS website / intake source: `/sis/` and `/prototype/`
- QTime Productions client area: `/qtime-productions`
- Commerce Command Center: `/commerce-command-center`
- Kingdom Gallery: `/design-gallery`
- Missions: `/missions`

## Files and areas inspected
- `app.py` - Flask imports, entry routes, dashboard routes, CRM APIs, chat route, dashboard data route, SIS lead capture route.
- `ui/atlas_neural_core.html` - main Atlas interface, chat console, quick commands, dashboard data fetch.
- `ui/crm.html` - customer / CRM command center and CRM API fetches.
- `sis-website/index.html` - SIS website and custom order/intake form.
- `sis-website/js/script.js` - form submission and lead brief fallback behavior.
- `CLIENTS/QTIME PRODUCTIONS/PROJECT_MEMORY.md` - QTime Project Memory and source of truth.
- `CLIENTS/QTIME PRODUCTIONS/REPORTS/ATLAS_CLIENT_DASHBOARD.md` - QTime client dashboard.
- `CLIENTS/QTIME PRODUCTIONS/APPROVAL_QUEUE/APPROVAL_QUEUE.md` - QTime approval/publishing lock status.
- `README.md`, `CODEX_MISSION_CONTROL.md`, `requirements.txt` - startup and operating context.

## QTime Productions status
- Source files exist under `CLIENTS/QTIME PRODUCTIONS/`.
- `PROJECT_MEMORY.md` marks QTime Productions as Atlas Client #001 and the first paid/active client.
- Public-use gaps remain source-backed in the files: official logo, official colors, website URL if any, current services/pricing, upcoming event media/details, and final Quincy approval are still needed.
- No official logo assets were found in `CLIENTS/QTIME PRODUCTIONS/ASSETS/` beyond the README.
- The new `/qtime-productions` route only displays existing local QTime source files and status. It does not invent claims, services, logos, pricing, or public-ready content.

## ABIS / Free Business Assessment status
- No file named `free-business-assessment` or `assessment` was found in the project search.
- The closest existing source-backed intake flow is the SIS custom order/business intake form in `sis-website/index.html` with JavaScript in `sis-website/js/script.js`.
- Current form configuration: `sis-website/js/script.js` posts to the local Flask endpoint `/api/website-leads` inside `saveLead(payload)` at lines 145-153.
- If Manny wants Google Apps Script instead of the local Flask endpoint, paste the Google Apps Script Web App URL in `sis-website/js/script.js` inside `saveLead(payload)`, replacing `fetch('/api/website-leads', { ... })` with the real Web App URL. No fake URL or credential was inserted.

## Broken imports / startup / obvious route findings
- `python -m py_compile app.py atlas_hermes_bridge.py atlas_intent_router.py crm/crm_skill.py` passed.
- `python - <<'PY' ... import app ...` passed and listed Flask routes successfully.
- Focused CRM test suite passed: `python -m unittest test_crm_system.py test_crm_api.py -v` ran 13 tests OK.
- Flask test client verified demo routes return 200 or intentional 302 redirects.
- Etsy links in the SIS site remain intentionally unconfigured and clearly marked as needing configuration; this is not a broken link fix because no official Etsy URL was found/provided.

## Current blockers / missing Manny input
- Persistent model/provider switch to avoid GPT spend must be changed in Hermes/Paperclip configuration by Manny or the runtime owner if desired globally.
- QTime public use still needs Quincy/Manny source inputs: official logo, brand colors, service list/pricing, upcoming event assets, approved tone, and final publishing approval.
- Google Apps Script Web App URL is not provided; Atlas did not insert a fake endpoint.
- Etsy URL for SIS remains unconfigured until Manny provides the official shop URL.

## Verification evidence
- Route verification output included:
  - `/`, `/neural`, `/executive-dashboard`, `/customer-dashboard`, `/client-crm`, `/crm`, `/sis/`, `/dashboard-data`, `/commerce-command-center`, `/design-gallery`, `/missions`, `/qtime-productions` all reachable.
  - `/atlas-chat`, `/website-chat`, `/business-assessment`, `/free-business-assessment` return intentional redirects to existing source-backed areas.
- CRM tests: 13 passed.

## Estimated API/token spend
- External app/API spend from verification: $0.00 observed.
- Work was completed with local file/system operations and local Python checks. No large AI generation or external research calls were used.
