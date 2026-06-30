# ATL-67 Atlas Website Launch Readiness Polish

## Wake acknowledgement

Latest wake had no pending comment batch. The heartbeat was actionable, so I treated the existing local static site as source of truth, inspected current files/assets/notes first, made focused launch-readiness edits, and verified locally without deploying or touching GoDaddy.

## Files changed

- `index.html`
  - Removed public/internal ticket comment from page source.
  - Reworded public proof section from client-specific QTime language to approved sample blueprint language.
  - Removed the public direct link to the QTIME dashboard and replaced it with a Free Assessment CTA.
  - Made client platform copy clearly private/client-access oriented.
  - Replaced client-specific dashboard preview data with generic client workspace preview copy.
  - Reworded PayPal copy from internal Manny wording to public Atlas payment wording.
- `styles.css`
  - Improved nav spacing and keyboard focus states.
  - Refined homepage spacing, mobile heading sizes, mobile nav wrapping, proof-card padding, and responsive proof label placement.
- `free-business-assessment/index.html`
  - Replaced internal ABIS/V1-facing language with public customer-facing assessment copy.
  - Standardized navigation to `Client Sign-In` and `/client-sign-in/`.
  - Replaced internal ATL/endpoint footer copy with launch-safe public copy.
- `client-sign-in/index.html`
  - Standardized stylesheet cache version.
  - Replaced dashboard nav link with sign-in nav link.
  - Removed public QTIME-specific security wording.
- `client-login/index.html`
  - Brought legacy sign-in route into naming/copy consistency with `client-sign-in`.
  - Removed direct dashboard nav link and QTIME-specific public wording.
- `assets/sample-business-growth-blueprint.pdf`
  - Added public/generic alias of the approved sample PDF so homepage source no longer exposes client name in public hrefs.
- `assets/sample-business-growth-blueprint-cover.png`
  - Added public/generic alias of the approved sample cover image so homepage source no longer exposes client name in public image refs.

Snapshot/rollback point:
- `.snapshots/ATL-67-launch-polish/20260630T204330Z/` for the original `index.html`, `styles.css`, `free-business-assessment/index.html`, and `client-sign-in/index.html` before launch-polish edits.

## Launch blockers found

No new launch blocker was found in the focused public-site smoke test.

Known remaining caution from prior readiness work still stands:
- `/client-dashboard/`, `/client-portal/`, `/client-dashboard/qtime-productions/`, and subpages are static/noindex client-demo or private dashboard routes. They should not be treated as secure production storage for private client files without real server-side auth.
- `/mission-control/` remains internal/demo-only and should not be uploaded publicly unless Manny intentionally approves it.
- The assessment form endpoint should still receive an approved end-to-end production test before relying on live intake.

## Issues fixed

- Removed public homepage QTime/QTIME visible references.
- Removed public homepage direct QTIME dashboard CTA.
- Removed public client-specific dashboard preview data.
- Removed internal ATL/ABIS deployment wording from public-facing pages.
- Standardized `Client Sign-In` naming across public assessment/sign-in paths.
- Replaced public sample asset links with generic `sample-business-growth-blueprint.*` filenames.
- Improved mobile/nav spacing and focus-visible affordances.
- Confirmed public pages do not expose `QTime`, `QTIME`, `mission-control`, `client-dashboard/qtime-productions`, `client-portal`, `ATL-`, or `ABIS Phase` in visible text or public-page attrs for the tested public pages.

## Pages ready for GoDaddy public launch

Ready as public/static pages after this polish:
- `/` from `index.html`
- `/free-business-assessment/`
- `/free-business-assesment/` typo/canonical helper route

Conditionally public but noindex/client-access oriented:
- `/client-sign-in/`
- `/client-login/` legacy route, now copy-aligned with sign-in

## Pages that should remain private or demo-only

Do not publish as public marketing pages:
- `/mission-control/`
- `/client-dashboard/`
- `/client-portal/`
- `/client-dashboard/qtime-productions/`
- `/client-dashboard/qtime-productions/welcome/`
- `/client-dashboard/qtime-productions/onboarding/`
- `/client-dashboard/qtime-productions/approvals/`
- `/client-dashboard/qtime-productions/reports/`

Reason: these are internal/static dashboard experiences and/or client-specific demo/private routes. Existing noindex/static auth helps reduce accidental exposure, but it is not a substitute for production server-side security.

## Verification performed

Local preview server:
- `python -m http.server 8087`

Smoke results:
- HTML reference scan: `13` HTML files scanned, `0` missing local refs.
- Public exposure scan: `0` findings across `/`, `/free-business-assessment/`, `/client-sign-in/`, and `/client-login/` for QTime/QTIME/internal route/ticket/source markers.
- Client portal security verifier: `node tools/verify-client-portal-security.js` passed.
- Local HTTP checks returned `200 OK` for:
  - `/`
  - `/free-business-assessment/`
  - `/client-sign-in/`
  - `/client-login/`
  - `/assets/favicon.png`
  - `/assets/sample-business-growth-blueprint.pdf`
  - `/assets/sample-business-growth-blueprint-cover.png`
- Browser smoke:
  - Homepage loaded with no console errors.
  - Assessment page loaded with no console errors.
  - Client sign-in page loaded with no console errors.
  - Visual QA found no broken visible images or severe layout overlap at the tested viewport.

## Final smoke-test checklist for GoDaddy

Before/after upload, verify:

Public site:
- `/` loads with logo, hero image, approved sample blueprint, pricing, and no missing images.
- Header anchors work: About, Team, How It Works, Proof, Client Platform, Pricing.
- Primary CTA opens `/free-business-assessment/`.
- Sample Presentation opens `/assets/sample-business-growth-blueprint.pdf`.
- PayPal button opens the approved Atlas PayPal payment link in a new tab.
- Footer text is public-facing and does not expose internal notes.

Assessment:
- `/free-business-assessment/` loads.
- Required fields enforce browser validation.
- If Manny approves live intake testing: submit one clearly marked test and confirm page success, Google Sheet row, and notification email.

Client access/demo:
- `/client-sign-in/` loads and stays noindex.
- `/client-login/` legacy route loads and stays noindex.
- Unauthenticated dashboard/portal pages redirect to sign-in.
- Do not upload or expose private client files, source folders, phone numbers, emails, private notes, or Mission Control unless Manny intentionally approves.

Disposition: done for ATL-67 launch-readiness polish. No deployment was attempted.
