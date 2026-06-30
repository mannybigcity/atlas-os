# ATL-44 Atlas Website Upgrade Notes

## Local URLs

Run from this folder:

```bash
python -m http.server 8087
```

Then open:

- Public website: http://127.0.0.1:8087/
- Free Business Assessment: http://127.0.0.1:8087/free-business-assessment/
- Client Sign-In: http://127.0.0.1:8087/client-sign-in/
- Client Dashboard: http://127.0.0.1:8087/client-dashboard/qtime-productions/

## Test Login

- Client: QTime Productions / Quincy
- Temporary passwords are controlled by Manny offline and are not documented in deployable website files.

V1 protection is browser/session based and suitable only for a demo dashboard with approved/non-private files. Do not upload private client files until real server-side authentication is added.

## What is real

- Uses existing Atlas logo/favicon/banner assets.
- Uses existing approved QTime Business Growth Blueprint PDF.
- Uses the rendered first page of the approved QTime Blueprint as the website/portal cover image (`assets/qtime-business-growth-blueprint-cover.png`).
- Login flow gates the portal in the browser for demo testing.
- Portal includes QTime dashboard, blueprint access, current priorities, active tasks, completed tasks, recommendations, digital presence/file area, and contact/assessment CTA.
- Atlas chat box is static/local and answers basic dashboard questions without API calls.
- ATL-47 marked QTime Productions as Paid / Active after the first $50 payment was received.

## What is placeholder / pending

- Free Business Assessment is now prepared as ABIS Phase 1. Live submission still waits on Apps Script Web App endpoint installation.
- Payment section is intentionally pending. Manny must provide the official PayPal link/button/subscription HTML before any payment code is added.
- Gallery, website audit, and digital presence links are marked Pending or Not Assessed Yet where approved data is missing.
- Live AI chat integration is intentionally not added; Manny approval, environment variables, privacy design, and backend work are required before client data is sent to an API.

## Approval checklist before going live

- Manny approves the public copy, $49/month offer display, and QTime permission language.
- Manny provides official PayPal payment link/button HTML if payments should be collected.
- Manny deploys the ATL-47 Apps Script Web App and installs its endpoint URL before live assessment submissions are accepted.
- Strong authentication is implemented before private client data/files are uploaded.
- Final upload is tested on the production host with the correct /free-business-assessment/ route.
