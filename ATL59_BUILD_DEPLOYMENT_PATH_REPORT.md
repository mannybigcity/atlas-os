# ATL-59 Build + Deployment Path Report

Scope: discovery only. No GoDaddy deployment was attempted. No production files were deleted or overwritten.

## Wake acknowledgement

Latest wake had no pending comment batch. The action for this heartbeat was to complete the ATL-59 discovery/inventory report using local project files first, then record a clear deployment path for Manny.

## 1. Website framework

The local Atlas website/client portal source is a plain static site: HTML, CSS, and vanilla JavaScript.

Evidence:
- `index.html`
- `styles.css`
- `client-dashboard/auth.js`
- route folders with `index.html`
- no `package.json`, `vite.config.js`, `next.config.js`, `src/`, `dist/`, or `build/` marker found in `C:/Users/User/Desktop/ATLAS Marketing/atlas_godaddy_site`

Current live homepage evidence:
- `https://atlasforentrepreneurs.com/` returns 200.
- The live homepage currently identifies as GoDaddy Website Builder: `Starfield Technologies; Go Daddy Website Builder 8.0.0000`.
- This means the local static `index.html` is not clearly the same source as the current live GoDaddy-builder homepage.

## 2. Source folder

Primary local source folder:

`C:/Users/User/Desktop/ATLAS Marketing/atlas_godaddy_site`

Important route locations:
- Marketing homepage: `index.html`
- Public assessment: `free-business-assessment/index.html`
- Typo/canonical helper route: `free-business-assesment/index.html`
- Client portal: `client-portal/index.html` and `client-portal/portal.js`
- Current sign-in page: `client-sign-in/index.html`
- Legacy sign-in page: `client-login/index.html`
- Admin dashboard: `client-dashboard/index.html`
- QTIME dashboard: `client-dashboard/qtime-productions/index.html`
- QTIME subpages:
  - `client-dashboard/qtime-productions/welcome/index.html`
  - `client-dashboard/qtime-productions/onboarding/index.html`
  - `client-dashboard/qtime-productions/approvals/index.html`
  - `client-dashboard/qtime-productions/reports/index.html`
- Shared dashboard auth script: `client-dashboard/auth.js`
- Internal/static mission control: `mission-control/index.html`

Project Memory note:
- A `PROJECT_MEMORY.md` file was not found in the Atlas static site folder during this audit.
- Existing task memory/notes were found in files such as `ABIS_PHASE1_INTAKE_NOTES.md`, `ATL48_CLIENT_SIGN_IN_QTIME_DASHBOARD_NOTES.md`, and `ATL50_CLIENT_PORTAL_AUTH_REVIEW.md`.

## 3. Build command

No build command is required or available. This is not React, Next.js, Vite, Flask templates, or a Node build.

Local preview command:

```bash
cd "C:/Users/User/Desktop/ATLAS Marketing/atlas_godaddy_site"
python -m http.server 8087
```

Production deployment is file upload, not a compiled build.

## 4. Production output folder

Because there is no build step, the deployable output is the static site folder itself:

`C:/Users/User/Desktop/ATLAS Marketing/atlas_godaddy_site`

Upload only runtime website files, not notes, snapshots, tools, temp JSON, or Apps Script source.

Deployable runtime file count verified: 26 files, about 24.86 MB.

## 5. GitHub status

The Atlas static site folder is not a Git repository.

Observed command result:

```text
fatal: not a git repository (or any of the parent directories): .git
```

Disposition:
- No Git remote was available from the local Atlas website folder.
- I cannot confirm that GitHub has the latest Atlas website/client portal version because this local folder is not tracked by git.
- If Manny wants GitHub as the source of truth, the low-cost next step is to create/choose a repo and commit this static site before any production upload.

## 6. Pages ready to deploy

Ready or mostly ready as static public pages, subject to Manny's final copy/brand approval:
- `/` from `index.html` — structurally ready locally, but replacing the current GoDaddy-builder homepage would be a brand/source-of-truth decision.
- `/free-business-assesment/` — helper typo route.

Conditionally ready:
- `/free-business-assessment/` — page is structurally ready and has no missing local assets found. However, the live ABIS endpoint needs an approved end-to-end production test before relying on the form for launch.

Local verification evidence:
- Client portal security verifier passed: `node tools/verify-client-portal-security.js`.
- Local deployable reference scan found 0 missing local `href/src` targets.

## 7. Pages not ready yet / publish risks

Not ready for sensitive/private production use:
- `/client-sign-in/`
- `/client-login/`
- `/client-portal/`
- `/client-dashboard/`
- `/client-dashboard/qtime-productions/` and subpages

Reason:
- The portal/dashboard uses static browser-side auth in `client-dashboard/auth.js` with `sessionStorage`.
- This is acceptable only for sanitized demo/static summaries, not private client files, sensitive business data, or real production security.

Do not publish publicly as-is unless Manny intentionally approves:
- `/mission-control/`

Reason:
- It is an internal/static mission-control page and should not be exposed accidentally.

Other readiness notes:
- Sign-in naming is inconsistent between `Client Sign-In` and `Client Login` across pages.
- QTime/QTIME casing varies.
- Mobile CSS exists, but navs wrap rather than collapse into a hamburger; small screens may show a tall header.
- `free-business-assessment/abis-config.js` contains a live Apps Script endpoint, but prior notes record endpoint verification failure from Apps Script `doGet`/`doPost` deployment issues. Treat ABIS as a launch risk until a live test confirms a Sheet row and email notification.

Current production route check:
- `/` returns 200.
- `/free-business-assessment/` returns 200.
- `/client-sign-in/` returns 404.
- `/client-portal/` returns 404.
- `/client-dashboard/` returns 404.

## 8. Exact GoDaddy upload instructions for Manny

Do not deploy until Manny approves replacing or augmenting the current GoDaddy Website Builder site.

Recommended low-risk path:

1. In GoDaddy/cPanel, confirm the correct document root. For a primary domain this is commonly `public_html/`; addon domains may use a subfolder.
2. Back up production first. At minimum, back up existing:
   - `/index.html`
   - `/styles.css`
   - `/assets/`
   - `/free-business-assessment/`
   - `/free-business-assesment/`
   - `/client-sign-in/`
   - `/client-login/`
   - `/client-dashboard/`
   - `/client-portal/`
   - `/mission-control/` if present
   - `.htaccess`, `web.config`, or redirect files if present
3. Prefer creating a temporary staging folder first, such as `public_html/_atl59_preview/`, to test upload mechanics without replacing production.
4. If Manny approves production upload, upload these runtime files/folders from `atlas_godaddy_site` while preserving folder paths:
   - `index.html`
   - `styles.css`
   - `assets/`
   - `free-business-assessment/`
   - `free-business-assesment/`
   - `client-sign-in/`
   - `client-login/`
   - `client-dashboard/`
   - `client-portal/`
   - `mission-control/` only if Manny intentionally wants it public
5. Do not upload:
   - `.snapshots/`
   - `.paperclip_tmp/`
   - `tools/`
   - `apps-script/`
   - `*.md`
   - temporary `atl47_*.json` files
6. Upload folders without flattening directories.
7. If uploading incrementally, upload `styles.css`, `client-dashboard/auth.js`, and `free-business-assessment/abis-config.js` last so pages do not temporarily reference missing scripts/styles.
8. Confirm normal web permissions: files commonly `0644`, folders commonly `0755`.
9. Clear GoDaddy/cPanel cache if enabled and test in an incognito/private browser.

Important root-path warning:
- The site uses absolute root paths such as `/client-dashboard/auth.js`, `/assets/favicon.png`, and `/client-sign-in/`.
- It should be deployed at the domain document root, not inside a subfolder, unless those paths are adjusted first.

## 9. Rollback instructions

Before upload:
- Compress/download a timestamped production backup, for example `atlas-production-backup-YYYYMMDD-HHMM.zip`.
- Download it locally and do not leave public backup zips in the web root long-term.

Fast rollback in GoDaddy File Manager:
1. Rename the failed deployment files/folders with a timestamp suffix, for example `index.html.failed-atl59-YYYYMMDD-HHMM`.
2. Extract the pre-upload backup zip back into the document root.
3. Confirm `/`, `/free-business-assessment/`, `/client-sign-in/`, and any pre-existing production routes return to pre-upload behavior.
4. Remove backup zips from public web root after restore.

FTP/SFTP rollback:
1. Re-upload the timestamped local backup over the document root.
2. Delete newly introduced ATL-59 folders that were not in the backup if they cause unwanted exposure.
3. Re-test public routes, assets, sign-in redirects, SSL, and payment/assessment links.

## 10. Post-upload smoke tests

Public site:
- `/` loads with Atlas logo, banner image, pricing, proof section, and no missing images.
- `/assets/favicon.png` loads.
- Main navigation anchors work: About, Team, How It Works, Proof, Client Platform, Pricing.
- PayPal button opens the approved PayPal URL in a new tab.
- QTime presentation PDF opens/downloads.

Assessment:
- `/free-business-assessment/` loads.
- `free-business-assessment/abis-config.js` returns 200.
- Only if Manny approves live ABIS testing: submit one clearly marked test and confirm page success, Google Sheet row, and notification email.

Portal/dashboard:
- `/client-sign-in/` loads over HTTPS.
- Unauthenticated dashboard/portal pages redirect to `/client-sign-in/?next=...`.
- With Manny-controlled test credentials only: admin reaches admin dashboard; QTIME client reaches QTIME dashboard; logout clears session.
- Confirm no private client files are uploaded publicly.

SSL/domain:
- `https://atlasforentrepreneurs.com/` loads without certificate warnings.
- `http://` redirects to `https://` if force HTTPS is enabled.
- Apex and `www` behavior matches the chosen canonical host.
- No browser mixed-content warnings appear.

## Final disposition

Discovery is complete. The safest recommendation is: do not overwrite the current GoDaddy Website Builder homepage until Manny decides whether the local static site should replace it. If Manny approves, back up production first and upload the 26 runtime static files/folders listed above to the domain document root, excluding notes/tools/snapshots/temp files.
