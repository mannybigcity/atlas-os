# ATL-47 ABIS Phase 1 Notes

## Wake acknowledgement

ATL-47 was scoped to Phase 1 only. The latest wake had no pending comment batch, so the next action changed from generic exploration to a strict audit-first implementation of the current Business Assessment and QTime paid-client milestone.

QTime Productions milestone logged: $50 payment received. QTime is now marked Paid / Active in Mission Control and the client portal.

Follow-up heartbeat 2026-06-30T01:39:51Z: Manny's latest wake explicitly confirmed QTime's $50 payment and required the client record to be updated before any further ABIS work. I re-read the ABIS implementation, QTime project memory, Mission Control, portal, Apps Script, and verification files first, then updated the QTime source-of-truth memory/dashboard records to Paid / Active without regenerating completed website work.

Follow-up heartbeat 2026-06-30T01:45:38Z: Latest comment acknowledged that Manny/local-board will deploy the Apps Script Web App and paste the deployed URL when ready. ATLAS did not request Google Workspace credentials. Scope was limited to non-live endpoint prep: add a safe endpoint config file, load it before the assessment submit script, and add a focused static verification command so the live URL can be installed later with one low-risk edit.

Recovery heartbeat 2026-06-30T19:22:17Z: Re-read the current ABIS implementation, QTime project memory, dashboard records, Apps Script source, endpoint config, verification scripts, and task history. No rebuild was needed. Re-ran the non-live endpoint prep verification and confirmed Phase 1 remains ready but blocked from live intake until Manny/local-board provides the deployed Apps Script Web App URL and approves Phase 2.

Live endpoint heartbeat 2026-06-30T19:25:23Z: Manny provided the live Apps Script Web App URL, so ATLAS restored the live execution path in `free-business-assessment/abis-config.js` and ran only the requested narrow endpoint verification. Verification did not pass because the deployed Web App responded with Google Apps Script HTML errors: `Script function not found: doGet` on GET and `Script function not found: doPost` on POST. No ABIS Phase 2 expansion, redesign, or client portal work was started.

## Existing implementation audit

### Files reviewed

- `free-business-assessment/index.html`
- `index.html`
- `styles.css`
- `mission-control/index.html`
- `client-portal/index.html`
- `client-portal/portal.js`
- `ATL44_CLIENT_PORTAL_NOTES.md`
- `ATL45_MISSION_CONTROL_NOTES.md`
- Existing assets folder listing, including Atlas logo/favicon/banner and QTime approved PDF/cover assets
- Existing snapshot folders under `.snapshots/ATL-44A`, `.snapshots/ATL-45`, `.snapshots/ATL-46`

### Existing fields

Current assessment fields before ATL-47:

1. `businessName` — Business name, required
2. `ownerName` — Owner / decision maker, required
3. `email` — Email, required
4. `offer` — What do you sell?
5. `blocker` — Biggest growth blocker
6. `saturdays` — What would create more Saturdays?

ATL-47 preserved these fields and added one hidden honeypot field:

7. `website` — hidden spam trap; real users should never fill it

### Existing button logic

Before ATL-47:

- Button label: `Preview Assessment Request`
- Submit handler prevented default form submission.
- Submit handler displayed a demo-only message.
- No network request was made.

After ATL-47:

- Button label: `Submit Free Business Assessment`
- Submit handler builds an ABIS payload with timestamp, client ID, client information, answers, status, and source.
- If the Apps Script endpoint is not installed, it blocks live submission and logs a safe payload preview in the browser console.
- If the endpoint is installed, it POSTs JSON to Google Apps Script with `mode: no-cors` and shows the generated Client ID.

### Existing storage

Before ATL-47:

- No assessment storage existed.
- Client portal access used browser `sessionStorage` only for the static QTime demo gate.
- No assessment data was written to localStorage, sessionStorage, files, APIs, or Google Sheets.

After ATL-47:

- Assessment storage path is prepared for Google Sheets via Apps Script.
- Live submission URL is installed, but endpoint verification is blocked until Manny/local-board redeploys the Apps Script Web App with the ABIS `doGet`/`doPost` functions.

### Existing Google integrations

Before ATL-47:

- No Google integrations were present in the static site.
- ATL-44/ATL-45 notes said Manny still needed to choose the assessment destination.

After ATL-47:

- Google Sheet selected as Atlas Intake Database:
  `https://docs.google.com/spreadsheets/d/1Biwt4rV4SkVkDBzLv1QZCb1rtBedF2hozClwUoiSdCE/edit?gid=1779141414`
- Direct local Google Sheets API access was not available in this environment because Google Workspace OAuth credentials are not configured.
- Lowest-cost implementation path prepared: Google Apps Script Web App -> append row -> email notification.

### Existing APIs

Before ATL-47:

- No website backend API existed for the assessment.
- The site is static HTML/CSS/JS and can be served by `python -m http.server`.

After ATL-47:

- New Apps Script source file added at `apps-script/abis-intake-web-app.gs`.
- Static page can POST to the deployed Apps Script Web App URL after installation.

### Existing workflow

Before ATL-47:

- Public site directs prospects to `/free-business-assessment/`.
- Assessment page is visual/static.
- Mission Control labels assessment destination as pending.
- Client portal is a static QTime dashboard demo.

After ATL-47:

- Public route remains unchanged.
- Assessment page becomes ABIS Phase 1 intake shell.
- Mission Control marks QTime Paid / Active and shows ABIS endpoint installation as the remaining gate.
- Client portal logs QTime's $50 payment milestone.

## Field mapping

| ABIS payload key | Source field / system value | Required | Downstream purpose |
| --- | --- | --- | --- |
| `timestamp` | Browser-generated ISO timestamp | Yes | Time received / ordering / audit trail |
| `clientId` | Browser-generated `ABIS-<timestamp>-<random>` | Yes | Unique intake tracking ID |
| `businessName` | `businessName` input | Yes | Client/business identification |
| `owner` | `ownerName` input | Yes | Decision-maker identification |
| `email` | `email` input | Yes | Follow-up and notification context |
| `assessmentAnswers.offer` | `offer` textarea | No | Understand product/service/audience |
| `assessmentAnswers.blocker` | `blocker` textarea | No | Route first strategic priority |
| `assessmentAnswers.saturdays` | `saturdays` textarea | No | Tie recommendations to More Saturdays outcome |
| `status` | Static value: `New Assessment` | Yes | Intake workflow state |
| `source` | Static value: `Atlas Website` | Yes | Attribution |

## Sheet mapping

Target spreadsheet ID:

`1Biwt4rV4SkVkDBzLv1QZCb1rtBedF2hozClwUoiSdCE`

Recommended sheet/tab name:

`Atlas Intake Database`

Apps Script will use that tab if it exists. If it does not exist, it falls back to the first sheet in the spreadsheet.

| Sheet column | ABIS source |
| --- | --- |
| Timestamp | `payload.timestamp` |
| Client ID | `payload.clientId` |
| Business Name | `payload.businessName` |
| Owner | `payload.owner` |
| Email | `payload.email` |
| Assessment Answers | JSON string of `payload.assessmentAnswers` |
| Status | `payload.status` |
| Source | `payload.source` |
| Received At | Server-side Apps Script receive timestamp |

## Apps Script endpoint

Source file:

`apps-script/abis-intake-web-app.gs`

Endpoint verifier:

`tools/verify-abis-endpoint.js`

Current endpoint status:

Installed in `free-business-assessment/abis-config.js`:

`https://script.google.com/macros/s/AKfycbzVK6dlKEQPq_vdhvK5aBs0o_FmsDAol3f3SYzhhP7yh7Ia3B1FD6amTGIqkYq8CrhQ/exec`

Live verification status: blocked by the deployed Apps Script version. The Web App currently returns Google Apps Script HTML errors instead of the ABIS JSON response: `Script function not found: doGet` on GET and `Script function not found: doPost` on POST. This means the provided deployment is not serving the `doGet`/`doPost` functions from `apps-script/abis-intake-web-app.gs`, so ATLAS cannot confirm the Google Sheet row or email delivery from this environment yet.

## Installation instructions

1. Open the Google Sheet Manny provided.
2. Create or confirm a tab named `Atlas Intake Database`.
3. Open Extensions -> Apps Script.
4. Paste the contents of `apps-script/abis-intake-web-app.gs`.
5. Save the script.
6. Run `setupAbisSheet()` once from the Apps Script editor and approve permissions.
7. Deploy -> New deployment -> Web app.
8. Set Execute as: `Me`.
9. Set Who has access: `Anyone` or the lowest-access public web app option that still accepts anonymous website submissions.
10. Copy the Web App URL.
11. In `free-business-assessment/abis-config.js`, replace the placeholder value:

```js
window.ATLAS_ABIS_APPS_SCRIPT_ENDPOINT = 'PASTE_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE';
```

12. Upload the updated static site files to the production host.

## Testing instructions

### Local static test

From `C:\Users\User\Desktop\ATLAS Marketing\atlas_godaddy_site`:

```bash
python -m http.server 8087
```

Open:

`http://127.0.0.1:8087/free-business-assessment/`

Submit the form before endpoint installation. Expected result:

- Button says `Submit Free Business Assessment`.
- Page does not submit live data.
- Message says the Apps Script endpoint still needs installation.
- Browser console shows a payload preview containing timestamp, Client ID, business name, owner, email, assessment answers, status `New Assessment`, and source `Atlas Website`.

### Apps Script test

After deployment:

1. Paste the Web App URL into `free-business-assessment/abis-config.js`.
2. Reload the assessment page.
3. Submit a test assessment.
4. Confirm a new row appears in the Google Sheet.
5. Confirm `info@atlasforentrepreneurs.com` receives the email notification.
6. Confirm the user sees `Assessment submitted. Your Atlas Client ID is ...`.

### Command-line endpoint verification

After Manny/local-board provides the deployed Apps Script Web App URL, run:

```bash
node tools/verify-abis-endpoint.js "https://script.google.com/macros/s/.../exec"
```

Expected result:

- `ABIS endpoint verification passed. Test Client ID: ...`
- A new verification row appears in the Google Sheet.
- `info@atlasforentrepreneurs.com` receives the email notification.

Latest result from 2026-06-30T19:25:23Z:

```bash
node tools/verify-abis-endpoint.js "https://script.google.com/macros/s/AKfycbzVK6dlKEQPq_vdhvK5aBs0o_FmsDAol3f3SYzhhP7yh7Ia3B1FD6amTGIqkYq8CrhQ/exec"
```

Result:

```text
ABIS endpoint verification failed: POST returned non-JSON response: Google Apps Script error page
```

Follow-up diagnostics confirmed:

- GET response body says `Script function not found: doGet`.
- POST response body says `Script function not found: doPost`.
- Because the endpoint did not execute `doPost`, ATLAS cannot confirm that the Google Sheet received a new test row.
- Because the endpoint did not execute `sendNotification_`, ATLAS cannot confirm that `info@atlasforentrepreneurs.com` received the email notification.

### Non-live endpoint prep verification

Before the Web App URL is available, run:

```bash
node tools/verify-abis-non-live-prep.js
```

Expected result:

- `ABIS non-live endpoint prep check passed.`
- `free-business-assessment/abis-config.js` exists, loads before the inline submission script, and still contains the safe placeholder.

## Files modified

- `free-business-assessment/index.html`
- `styles.css`
- `mission-control/index.html`
- `client-portal/index.html`
- `ATL44_CLIENT_PORTAL_NOTES.md`
- `ATL45_MISSION_CONTROL_NOTES.md`
- `apps-script/abis-intake-web-app.gs` (new)
- `ABIS_PHASE1_INTAKE_NOTES.md` (new)
- `tools/verify-abis-endpoint.js` (new)
- `free-business-assessment/abis-config.js` (follow-up: live endpoint URL installed from Manny/local-board)
- `tools/verify-abis-non-live-prep.js` (new follow-up: non-live endpoint prep verification)
- `C:/Users/User/Desktop/PUTER/CLIENTS/QTIME PRODUCTIONS/PROJECT_MEMORY.md` (follow-up: Paid / Active source-of-truth client record)
- `C:/Users/User/Desktop/PUTER/CLIENTS/QTIME PRODUCTIONS/REPORTS/ATLAS_CLIENT_DASHBOARD.md` (follow-up: Paid / Active dashboard record)

## Rollback / snapshot

Snapshot created before modifying the primary HTML/docs files:

`.snapshots/ATL-47/20260630T002544Z/`

Follow-up non-live endpoint prep snapshot:

`.snapshots/ATL-47-non-live-endpoint-prep/20260630T014538Z/`

## Remaining work after Phase 1

Do not begin until Manny approves Phase 2.

1. Manny/local-board should update/redeploy the Apps Script Web App so the deployment serves `doGet` and `doPost` from `apps-script/abis-intake-web-app.gs`.
2. Re-run the live Google Sheet append test with `node tools/verify-abis-endpoint.js <web-app-url>`.
3. Confirm email notification delivery to `info@atlasforentrepreneurs.com`.
4. Expand ABIS questions only after confirming the current six-field V1 works end-to-end and Manny approves Phase 2.
5. Decide whether ABIS should create client portal records automatically in a future backend/CRM phase.

## Estimated token cost for Phase 2

Estimated: 2,000 to 4,000 tokens if Phase 2 is limited to endpoint installation support, one live test, and documentation cleanup.

Estimated: 6,000 to 10,000 tokens if Phase 2 expands the questionnaire, adds CRM-style status tracking, or requires backend/API architecture decisions.
