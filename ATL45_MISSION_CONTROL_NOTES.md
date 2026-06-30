# ATL-45 Atlas Mission Control Dashboard Notes

## Local URLs

Run from this folder:

```bash
python -m http.server 8087
```

Then open:

- Mission Control: http://127.0.0.1:8087/mission-control/
- QTime client dashboard preview from Mission Control: http://127.0.0.1:8087/client-dashboard/qtime-productions/
- Client Sign-In: http://127.0.0.1:8087/client-sign-in/
- Public Website Preview: http://127.0.0.1:8087/
- Free Business Assessment: http://127.0.0.1:8087/free-business-assessment/
- QTime Business Assessment Presentation file: http://127.0.0.1:8087/assets/qtime-productions-business-assessment-presentation.pdf

## What is real

- Mission Control is a working static internal page under `/mission-control/`.
- Uses the existing Atlas logo/favicon/CSS/brand colors from the current Atlas static site.
- Links to the existing public website, client login, assessment page, QTime client portal, PayPal payment page, and QTime Business Assessment Presentation PDF.
- QTime client dashboard preview uses the existing `client-portal/` dashboard created in ATL-44.
- A rollback snapshot of the changed shared CSS and portal JavaScript was saved in `.snapshots/ATL-45/`.
- ATL-47 logged QTime's $50 payment milestone and marks QTime Productions as Paid / Active.
- ATL-47 prepared ABIS Phase 1 with Google Sheets as the selected intake database and Apps Script as the lowest-cost submission path.

## What is demo/static or not connected yet

- Executive overview numbers are V1 visibility placeholders and are labeled Pending, Demo, Static, or Not Connected Yet where live data is missing.
- Future client cards for SIS Custom Creations and FRESH Apparel are placeholders only.
- Executive agent status cards are static/demo; they are not connected to live Paperclip/Hermes runtime status yet.
- Activity feed is static/demo for V1.
- Approval center is static, but lists real approval gates before publishing or live integrations.
- The QTime portal `?executivePreview=mission-control` route bypasses the browser demo password for Manny's internal preview only. This is acceptable for the current static demo because no private client files or secrets are stored there. Strong authentication is still required before live private client data.

## Approval checklist before publishing

- Manny approves Mission Control copy, dashboard structure, and what should/should not be exposed on a public host.
- ATL-46 connected Manny's official PayPal payment link (`https://www.paypal.com/ncp/payment/CWU4JYU3WLGTJ`) to public pricing/contact CTAs; verify the payment flow after production upload.
- Manny deploys the ATL-47 Apps Script Web App and installs the endpoint URL into `/free-business-assessment/` before accepting live assessment submissions.
- Strong server-side authentication is implemented before private client files or sensitive dashboard data are uploaded.
- Live AI chat integration receives approval for provider, privacy handling, environment variables, budget, and backend architecture.
- Client assets and QTime permissions are confirmed before adding photos, logos, private documents, or testimonials.
- Final production upload is tested on the live host, including `/mission-control/`, `/client-login/`, `/client-portal/`, and `/free-business-assessment/` routes.
