# ATL-50 Client Portal Auth / Dashboard Infrastructure Review

## Scope

Reviewed existing Atlas Client Portal auth/dashboard work without rebuilding. Primary files checked:

- `client-portal/index.html`
- `client-portal/portal.js`
- `client-dashboard/auth.js`
- `client-dashboard/index.html`
- `client-dashboard/qtime-productions/index.html`
- `client-dashboard/qtime-productions/welcome/index.html`
- `client-dashboard/qtime-productions/onboarding/index.html`
- `client-dashboard/qtime-productions/approvals/index.html`
- `client-dashboard/qtime-productions/reports/index.html`
- `tools/verify-client-portal-security.js`
- Prior implementation notes: `ATL48_CLIENT_SIGN_IN_QTIME_DASHBOARD_NOTES.md`, `ATL45_MISSION_CONTROL_NOTES.md`

## Findings

- `/client-portal/` now uses the shared QTIME auth gate from `client-dashboard/auth.js` via `atlasProtectPage('qtime')`.
- `client-portal/portal.js` uses `atlasGetSession()` and authorizes only admin or `clientSlug === 'qtime-productions'`.
- Legacy `ACCESS_TOKEN`, `qtime-demo-v1`, and `executivePreview` bypass code is not present in active portal JS.
- QTIME Client #001 pages are present, noindexed, and protected with `atlasProtectPage('qtime')`.
- Admin dashboard remains protected with `atlasProtectPage('admin')`.
- Temporary deployable credentials remain hash-only in `client-dashboard/auth.js`; real temporary passwords are not stored in active deployable files.

## Fix applied during ATL-50

During verification, direct Client #001 routing exposed a low-cost infrastructure issue: a QTIME client session visiting `/client-dashboard/` could be denied by the admin gate before the client redirect ran. I corrected the order in `client-dashboard/auth.js` so authenticated client users hitting `/client-dashboard/` are routed to `/client-dashboard/qtime-productions/` before admin-only denial logic runs.

I also tightened `atlasHandleLogin()` routing so client users cannot be sent to arbitrary requested dashboard paths after sign-in. Client users now keep only QTIME-safe next paths:

- `/client-dashboard/qtime-productions/...`
- `/client-portal/...`

Otherwise they fall back to `/client-dashboard/qtime-productions/`. Admin users retain admin routing.

To avoid stale browser cache serving the prior auth gate, protected pages now reference:

- `/client-dashboard/auth.js?v=atl50`

## Verification performed

Local server:

```bash
python -m http.server 8087
```

Focused security check:

```bash
node tools/verify-client-portal-security.js
```

Result:

```text
Client portal security verification passed.
```

HTTP route checks returned 200:

- `/client-portal/`
- `/client-dashboard/`
- `/client-dashboard/qtime-productions/`
- `/client-dashboard/qtime-productions/welcome/`
- `/client-dashboard/qtime-productions/onboarding/`
- `/client-dashboard/qtime-productions/approvals/`
- `/client-dashboard/qtime-productions/reports/`

Browser checks:

- Unauthenticated `/client-portal/` redirects to `/client-sign-in/?next=%2Fclient-portal%2F`.
- Authenticated QTIME client session opens `/client-portal/` with `portalContent.hidden === false` and `lockedContent.hidden === true`.
- Authenticated QTIME client session visiting `/client-dashboard/` now routes to `/client-dashboard/qtime-productions/` and shows `Welcome, Quincy.`.
- Authenticated admin session visiting `/client-dashboard/` opens the admin command center.

## Current security disposition

Static V1 is acceptable only for sanitized dashboard summaries and approved public sample assets. It is not sufficient for private files, sensitive client data, real credentials, or production-grade access control because static files can still be downloaded by anyone who knows the URL.

No private QTIME files should be uploaded until server-side auth exists.

## Lowest-cost path to true server-side auth

1. Keep the current static pages as the visual shell and do not rebuild the dashboard.
2. Add a tiny server-side gate before private content:
   - A low-cost Node/Express or serverless function route for sign-in.
   - Store users server-side with salted password hashes, not in browser JS.
   - Issue an HttpOnly, Secure, SameSite session cookie.
3. Move client-specific dashboard data/private file links behind authenticated API routes:
   - `/api/session`
   - `/api/client-dashboard/qtime-productions`
   - `/api/client-files/qtime-productions/*`
4. Keep public static assets public, but move private QTIME files outside the web root.
5. Add role checks server-side:
   - `admin` can view all clients.
   - `client` can view only its own `clientSlug`.
6. Preserve the current noindex tags as a secondary privacy layer, not the primary security layer.
7. Reuse the existing `tools/verify-client-portal-security.js` check and add a server-side auth smoke test once the backend exists.

Recommended next owner: Mason for server-side auth architecture and implementation. David can support future CRM/session workflow needs after Mason chooses the backend path.
