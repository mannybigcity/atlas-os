# ATL-59 GoDaddy Deployment Checklist — Atlas Website / Client Portal

Scope: static-site deployment planning only for `C:\Users\User\Desktop\ATLAS Marketing\atlas_godaddy_site`. Do **not** request credentials, do **not** deploy, and do **not** overwrite production without Manny's approval and a production backup.

## 1) Deployment readiness summary

- Site type: static HTML/CSS/JS plus image/PDF assets; no Node/PHP build step found.
- Intended GoDaddy target: the domain document root, normally `public_html/` for the primary domain or the configured document root for an addon/subdomain.
- Local deployable footprint found: 26 static files, about 24.86 MB total.
- Local reference check: 167 local `href`/`src` references checked; 0 missing local targets.
- Client portal security verifier: `node tools/verify-client-portal-security.js` passed.
- ABIS/live assessment risk: `free-business-assessment/abis-config.js` contains a live Google Apps Script endpoint. Existing notes say prior live endpoint verification was blocked by Apps Script `doGet`/`doPost` deployment issues. Do not treat assessment submission as production-ready until a live test confirms Google Sheet row + email notification.
- Static auth caveat: `client-dashboard/auth.js` uses browser-side hashed temporary credentials and `sessionStorage`. This is acceptable only for sanitized/static V1 demos, not for private client files or sensitive data.

## 2) Files/folders to upload to GoDaddy

Upload these paths from the local folder into the matching paths under the production document root. Preserve folder names exactly, including the intentional misspelled redirect folder `free-business-assesment/`.

### Root files

- `index.html`
- `styles.css`

### Assets

- `assets/atlas-banner-web.jpg`
- `assets/atlas-banner.png`
- `assets/atlas-logo.png`
- `assets/favicon.png`
- `assets/founding-member-49.png`
- `assets/free-business-assessment.png`
- `assets/qtime-business-growth-blueprint-cover.png`
- `assets/qtime-business-growth-blueprint.pdf`
- `assets/qtime-productions-business-assessment-presentation.pdf`

### Public and internal routes

- `free-business-assessment/index.html`
- `free-business-assessment/abis-config.js`
- `free-business-assesment/index.html` — typo redirect/canonical helper; keep it so old/mistyped links do not 404.
- `client-sign-in/index.html`
- `client-login/index.html` — legacy/alternate sign-in route; keep if production already has it or if links may reference it.
- `client-dashboard/auth.js`
- `client-dashboard/index.html`
- `client-dashboard/qtime-productions/index.html`
- `client-dashboard/qtime-productions/welcome/index.html`
- `client-dashboard/qtime-productions/onboarding/index.html`
- `client-dashboard/qtime-productions/approvals/index.html`
- `client-dashboard/qtime-productions/reports/index.html`
- `client-portal/index.html`
- `client-portal/portal.js`
- `mission-control/index.html` — internal/static mission control page; upload only if Manny intentionally wants this route on production.

## 3) Files/folders not to upload

Do **not** upload local working, notes, snapshots, or tooling to production unless Manny explicitly asks for a documentation route.

- `.snapshots/`
- `.paperclip_tmp/`
- `tools/`
- `apps-script/`
- `*.md` files, including this checklist
- `atl47_*.json` / temporary task JSON files

Reason: these are source/audit/support files, not website runtime files. `apps-script/abis-intake-web-app.gs` belongs in Google Apps Script, not GoDaddy web root.

## 4) Back up production first

Before uploading anything, create a production backup from GoDaddy cPanel/File Manager or FTP/SFTP.

### Minimum backup set

Back up any existing production versions of these paths if they exist:

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
- Any production `.htaccess`, `web.config`, or redirect files in the document root

### Recommended backup format

- In File Manager: select the current production files/folders and Compress to a zip named like `atlas-production-backup-YYYYMMDD-HHMM.zip`; download the zip locally before uploading.
- In FTP/SFTP: download the current production document root to a timestamped local folder before uploading.
- Keep the backup outside `public_html` after download if possible. Do not leave backup zips publicly accessible in the web root long-term.

## 5) GoDaddy upload procedure — low-risk path

1. Confirm the correct document root in GoDaddy Hosting/cPanel. For the primary domain this is usually `public_html/`; addon domains may use a subfolder.
2. Confirm the domain points to the GoDaddy hosting account before scheduling the upload.
3. Back up production as described above.
4. Upload to a temporary staging folder first if possible, for example `public_html/_atl59_preview/`, to verify files transfer cleanly without replacing production.
5. If no staging folder is possible, upload during a low-traffic window.
6. Upload folders/files preserving relative paths. Do not flatten directories.
7. Upload `styles.css`, `client-dashboard/auth.js`, and `free-business-assessment/abis-config.js` last if using incremental overwrite, so pages do not temporarily reference partially uploaded scripts/styles.
8. In File Manager, verify uploaded files have normal web-readable permissions, commonly files `0644` and folders `0755`.
9. Clear/disable any GoDaddy/cPanel cache if enabled. Also test with a private/incognito browser session because CSS/JS uses cache-busting query strings but browsers may still cache aggressively.

## 6) Rollback plan

Use rollback if any critical route 404s, styling/assets are broken, sign-in cannot route correctly, SSL fails, PayPal/assessment links are wrong, or Manny sees production content that should not be public.

### Fast rollback using backup zip

1. Put site in maintenance only if GoDaddy/cPanel has a known safe maintenance mechanism; otherwise proceed directly to restore.
2. In File Manager, rename the failed deployment folders/files with a timestamp suffix, for example `index.html.failed-atl59-YYYYMMDD-HHMM` and `client-dashboard.failed-atl59-YYYYMMDD-HHMM/`.
3. Extract the pre-upload backup zip back into the document root.
4. Confirm `/`, `/free-business-assessment/`, `/client-sign-in/`, and any existing production routes return to their pre-upload behavior.
5. Remove any public backup zip from the web root after restore.

### FTP rollback

1. Re-upload the timestamped local production backup over the document root.
2. Delete any newly introduced ATL-59 folders that were not in the backup if they cause unwanted exposure.
3. Re-test the key routes below.

## 7) Post-upload smoke tests

Run these in a browser after upload. Use `https://` and the real domain.

### Public site

- `/` loads with Atlas logo, banner image, pricing, proof section, and no missing images.
- `/assets/favicon.png` loads.
- Main navigation works: About, Team, How It Works, Proof, Client Platform, Pricing.
- PayPal buttons open `https://www.paypal.com/ncp/payment/CWU4JYU3WLGTJ` in a new tab.
- PDF opens/downloads: `/assets/qtime-productions-business-assessment-presentation.pdf`.

### Assessment / ABIS

- `/free-business-assessment/` loads and shows `Submit Free Business Assessment`.
- Browser dev tools Network tab shows `free-business-assessment/abis-config.js` loads with HTTP 200.
- If Manny has approved live ABIS testing: submit one clearly marked test record, then confirm all three outcomes: page shows an Atlas Client ID, Google Sheet gets a new row, and `info@atlasforentrepreneurs.com` receives the notification.
- If live ABIS is not approved/verified: do not run production submissions; leave this as a known launch risk.
- `/free-business-assesment/` redirects or points users to `/free-business-assessment/`.

### Client portal and dashboard

- `/client-sign-in/` loads over HTTPS.
- `/client-login/` loads or redirects as expected if kept for compatibility.
- Unauthenticated `/client-dashboard/` redirects to `/client-sign-in/?next=...`.
- Unauthenticated `/client-dashboard/qtime-productions/` redirects to `/client-sign-in/?next=...`.
- Unauthenticated `/client-portal/` redirects to `/client-sign-in/?next=...`.
- With Manny-controlled test credentials only: admin user reaches `/client-dashboard/`; QTIME client reaches `/client-dashboard/qtime-productions/`; QTIME client cannot browse arbitrary admin-only dashboard pages.
- Log out button clears session and returns to sign-in.
- Confirm no private QTIME source files are present under `/assets/`, `/client-dashboard/`, or any public folder.

### Internal/static mission control, if uploaded

- `/mission-control/` loads only if Manny intentionally approved this route for production.
- Confirm it does not expose private notes, credentials, or unapproved client details.

## 8) SSL/domain routing readiness

Before upload/go-live:

- Domain DNS should point to the correct GoDaddy hosting account/document root.
- GoDaddy SSL certificate should be issued and active for both apex/root domain and `www` if both are used.
- Force HTTPS should be enabled using GoDaddy/cPanel SSL settings or a known-good `.htaccess` rule. Back up existing `.htaccess` before changing it.
- Decide canonical host: either `https://atlasforentrepreneurs.com` or `https://www.atlasforentrepreneurs.com`. Ensure the other redirects consistently.
- Confirm absolute-root links like `/client-dashboard/auth.js`, `/assets/favicon.png`, and `/client-sign-in/` resolve correctly at the chosen document root. These pages assume the Atlas site is hosted at the domain root, not inside a subdirectory.
- If deploying under a subfolder instead of the domain root, several absolute `/...` links will break and must be changed before upload.

After upload:

- `https://domain/` loads without browser certificate warnings.
- `http://domain/` redirects to `https://domain/`.
- `https://www.domain/` and `https://domain/` resolve according to the chosen canonical host.
- No mixed-content warnings appear in browser dev tools.

## 9) Highest deployment risks to call out to Manny

1. **Static portal auth is not real server-side security.** Do not upload private client files or sensitive details. The current dashboard is for sanitized summaries and approved public sample assets only.
2. **ABIS endpoint must be verified end-to-end.** The local `abis-config.js` currently contains a live Apps Script URL, but previous notes record deployment-function failures for an Apps Script endpoint. A production assessment launch is not complete until a test creates a Sheet row and sends notification email.
3. **Root deployment assumption.** Many routes use absolute `/...` paths. Uploading into a subfolder will break portal assets/scripts unless routes are adjusted.
4. **Production backup is mandatory.** Current production content must be zipped/downloaded before overwrites.
5. **Mission Control route may be internal.** Upload `/mission-control/` only if Manny approves exposing that static route.

## 10) Local verification commands used for this scout

From `C:\Users\User\Desktop\ATLAS Marketing\atlas_godaddy_site`:

```bash
node tools/verify-client-portal-security.js
```

Result: `Client portal security verification passed.`

A local HTML reference scan checked 167 local references and found 0 missing local targets.

`node tools/verify-abis-non-live-prep.js` did not pass because the site is no longer in placeholder/non-live endpoint mode; `free-business-assessment/abis-config.js` now contains a live Apps Script URL. `node tools/verify-abis-endpoint.js` requires an endpoint argument or environment variable and was not run against production to avoid submitting live test intake during this no-deploy/no-credentials scout.
