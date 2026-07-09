# Atlas protected app next steps

ATL-118 prepared `/app` as the signed-in Atlas app entry point and moved the major internal tools into one shared SaaS shell.

Current state after ATL-119:
- `/login` and `/admin-login` provide a temporary Atlas admin gate for local testing.
- Credentials come from `ATLAS_ADMIN_USERNAME` and `ATLAS_ADMIN_PASSWORD` in the runtime environment or local `.env`; no password is hardcoded in source.
- `/app`, `/dashboard`, `/missions`, `/crm`, `/design-gallery`, and `/commerce-command-center` require the Flask session before loading.
- Mission APIs that expose `executive_messages` and protected Design Gallery / Commerce approval routes now require the same session.
- Existing page data sources remain unchanged after sign-in; Mission Control still reads the current mission API and executive message feed.

Recommended secure-login follow-up:
1. Replace the temporary single-admin gate with a real user/session model or external identity provider.
2. Store `FLASK_SECRET_KEY`, `ATLAS_ADMIN_USERNAME`, and `ATLAS_ADMIN_PASSWORD` outside source control in the production runtime environment.
3. Serve the Atlas OS app behind HTTPS on the final DigitalOcean domain/subdomain and update the GoDaddy website admin link if that URL changes.
4. Add role checks before destructive actions such as CRM deletes, gallery status changes, and commerce approval actions.
5. Add session expiry, CSRF protection for form/API mutations, secure cookie settings, rate limiting, audit logging, and password rotation.
