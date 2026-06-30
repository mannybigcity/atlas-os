# ATL-48 Secure Client Sign-In + QTIME Dashboard Notes

## Local URLs

Run from this folder:

```bash
python -m http.server 8087
```

Then open:

- Client sign-in: http://127.0.0.1:8087/client-sign-in/
- Admin client dashboard: http://127.0.0.1:8087/client-dashboard/
- QTIME dashboard: http://127.0.0.1:8087/client-dashboard/qtime-productions/
- QTIME welcome: http://127.0.0.1:8087/client-dashboard/qtime-productions/welcome/
- QTIME onboarding: http://127.0.0.1:8087/client-dashboard/qtime-productions/onboarding/
- QTIME approvals: http://127.0.0.1:8087/client-dashboard/qtime-productions/approvals/
- QTIME reports: http://127.0.0.1:8087/client-dashboard/qtime-productions/reports/

## Temporary Login Instructions

Temporary passwords are not stored in deployable website files. Manny controls the actual temporary passwords offline. The browser file stores SHA-256 password hashes only.

- Manny admin username: `atlas-admin`
- Manny admin temporary password: held offline by Manny
- Quincy client username: `qtime-client`
- Quincy client temporary password: held offline by Manny / provided directly to Quincy

To change temporary credentials in this static V1:

1. Generate a new SHA-256 hash for the password.
2. Replace the matching `passwordHash` in `client-dashboard/auth.js`.
3. Do not write real passwords into public HTML/JS files.

## Security Notes

- Dashboard pages include `noindex, nofollow, noarchive` robots meta tags.
- Browser session access is required before normal viewing.
- Manny admin can access `/client-dashboard/` and all QTIME pages.
- Quincy client access routes only to `/client-dashboard/qtime-productions/` pages.
- Private QTIME source files are not linked from the website.
- Demo pages do not show phone numbers, emails, private notes, personal addresses, or private local file URLs.
- Deployable site files are checked for plaintext temporary portal passwords with `node tools/verify-client-portal-security.js`.
- Static frontend auth is not true production-grade security because static page source can still be downloaded by anyone who knows the URLs. Before uploading private documents or sensitive data, move auth and dashboard data behind server-side sessions.

## ATL-47 Priority Shift / 2026-06-30

Phase 1 ABIS work is approved but Phase 2 remains paused. The current priority is the secure Atlas Client Portal MVP and QTIME PRODUCTIONS as Client #001.

Concrete security hardening completed in this pass:

- Re-read the QTIME source folder, Atlas website files, portal pages, auth script, Mission Control, and implementation notes before editing.
- Preserved a rollback snapshot under `.snapshots/ATL-47-client-portal-security/20260630T004444Z/`.
- Removed plaintext temporary portal passwords from deployable website notes.
- Added `tools/verify-client-portal-security.js` to verify required portal routes, auth gates, noindex tags, QTIME Client #001 routing, SHA-256 hash use, and absence of plaintext temporary portal passwords in deployable HTML/JS/CSS/MD files outside `.snapshots`.
- Focused verification command: `node tools/verify-client-portal-security.js`.

## Source Material Read First

- `PROJECT_MEMORY.md`
- `BRAND_GUIDE.md`
- `OFFER_MAP.md`
- `BUSINESS_ASSESSMENT.md`
- `REPORTS/ATLAS_CLIENT_DASHBOARD.md`
- `REPORTS/MANNY_QUINCY_MISSING_ASSETS_CHECKLIST.md`
- `SOCIAL_MEDIA/2026-06-29_7_DAY_CONTENT_PACKAGE.md`
- `HUNTER_LEADS/DENVER_OPPORTUNITY_REPORT.md`
- `APPROVAL_QUEUE/APPROVAL_QUEUE.md`

## Changed / Created

- Created `/client-sign-in/` secure sign-in page.
- Created `/client-dashboard/` Manny admin page.
- Created `/client-dashboard/auth.js` shared session/role gate.
- Created QTIME dashboard route and required subroutes.
- Updated existing `/client-login/` to the new sign-in flow for backward compatibility.
- Existing `/client-portal/` is now a secure compatibility Client Portal route that extends the shared `client-dashboard/auth.js` gate, removes the old demo-token/executive-preview bypass, and links into Debbie-owned welcome/onboarding plus approval/report routes.

## Continuation Verification - 2026-06-30T00:50:20Z

- The prior Paperclip run failed before returning a summary with `spawn ENAMETOOLONG`; this continuation used short, focused commands and did not refetch the issue because the wake payload said fallback fetch was not needed.
- Re-read the QTIME source-of-truth files and the existing Atlas site portal files before making a disposition.
- Verified required routes return HTTP 200 from a local static server on port 8087.
- Verified unauthenticated browser access to `/client-dashboard/qtime-productions/` redirects to `/client-sign-in/?next=...`.
- Verified Quincy login opens the QTIME dashboard and Manny admin login opens the admin dashboard.
- Verified `node tools/verify-client-portal-security.js` passes.

## Existing Client Portal Hardening - 2026-06-30T01:06:05Z

- Latest Manny comment approved the prior portal MVP and clarified the next action: turn the existing `/client-portal/` into the production-ready Atlas Client Portal, with QTIME PRODUCTIONS as Client #001, without rebuilding completed work.
- Read before write: re-read `PROJECT_MEMORY.md`, `BRAND_GUIDE.md`, QTIME dashboard/checklist notes, the current `/client-portal/` files, the secure sign-in/auth/dashboard files, and current implementation notes.
- Preserved rollback snapshot under `.snapshots/ATL-47-existing-client-portal/20260630T010605Z/`.
- Hardened `/client-portal/index.html` with noindex metadata, the shared QTIME auth gate, secure sign-in fallback, and navigation into Welcome, Onboarding, Approvals, and Reports.
- Updated `/client-portal/portal.js` to use the shared secure session instead of the old browser demo token or executive preview bypass.
- Extended `tools/verify-client-portal-security.js` so future checks fail if `/client-portal/` loses noindex, loses shared QTIME auth, or reintroduces legacy demo-token/preview bypass access.

## ATL-49 Debbie Welcome / Onboarding Review - 2026-06-30T01:10:54Z

- Wake scope had no new pending comment; continued from the source-scoped recovery action and kept Debbie-owned work limited to the existing QTIME routes.
- Read before write: re-read the QTIME Project Memory, Manny/Quincy missing-assets checklist, sanitized demo checklist, existing welcome/onboarding/approvals pages, and this implementation note.
- Preserved rollback snapshot under `.snapshots/ATL-49-qtime-onboarding/20260630T011054Z/`.
- Refined `/client-dashboard/qtime-productions/welcome/` copy so Quincy is directed to start with the onboarding checklist and review approval gates rather than treating reports as the next public step.
- Refined `/client-dashboard/qtime-productions/onboarding/` checklist language to reduce back-and-forth: "none yet" is acceptable for unavailable inputs; permission now explicitly covers logos, flyers, photos, videos, and templates; service/pricing now asks for do-not-offer items and required outreach approval wording.
- Refined `/client-dashboard/qtime-productions/approvals/` copy to preserve Manny + Quincy approval gates for exact facts, materials, services/pricing, media, lead outreach, demos, and public publishing.
- Verification: `node tools/verify-client-portal-security.js` passed and focused HTML/auth/noindex parsing for the three touched routes passed.
