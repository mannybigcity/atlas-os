# ATLAS NEXT STEPS

Last updated: 2026-06-30 10:57:50 CDT
Issue: ATL-56 - Stabilize Atlas and prepare it for demo/deployment

## Manny review path
1. Start the local Atlas app from `C:/Users/User/Desktop/PUTER`:
   - `python app.py`
2. Open:
   - `http://127.0.0.1:5000/`
3. Use the Demo Navigation panel in ATLAS Neural Core to review:
   - Executive Dashboard
   - Customer Dashboard
   - Client / CRM Area
   - Atlas Chat
   - Business Intake
   - Website Chat / SIS Site
   - QTime Productions
   - Commerce Command Center
   - Kingdom Gallery
4. Confirm whether the current demo route labels match how Manny wants to present Atlas.

## Deployment readiness next steps
1. Decide whether demo deployment should expose only the Atlas dashboard routes or also client/source markdown routes like `/qtime-productions`.
2. Provide the production host target if this should move beyond local demo.
3. Provide or confirm the Flask secret/deployment environment variables before public hosting.
4. Keep Etsy, Google Apps Script, Meta automation, paid ads, and public posting locked until real URLs/credentials/assets are provided.

## QTime Productions next steps
Owner: Manny / Quincy

Need source inputs before public use:
- Official logo file.
- Official brand colors.
- Website URL, if one exists.
- Current service list and pricing/packages.
- Upcoming events, flyers, photos, and videos.
- Preferred tone/phrases and banned phrases.
- Final approval path for content and outreach.

Atlas recommendation: keep QTime visible in the local demo as a source-backed client area, but do not present any QTime material as public-ready until Quincy confirms the missing inputs.

## ABIS / Free Business Assessment next steps
Owner: Manny

Current state:
- No `free-business-assessment` source file was found.
- Existing intake form is the SIS custom order/business intake form at `/sis/#custom-orders`.
- Existing backend endpoint is `/api/website-leads`.

If Manny wants Google Apps Script submission:
1. Deploy the Google Apps Script Web App.
2. Copy the real Web App URL.
3. Paste it in `sis-website/js/script.js` inside `saveLead(payload)`, replacing the current local fetch endpoint `/api/website-leads`.
4. Test one form submission and confirm it reaches the target sheet/app.

Do not paste a fake URL. Do not include credentials in the repo.

## Recommended follow-up issues
- Create a deployment issue once Manny chooses the host and public route scope.
- Create a QTime assets/intake issue after Quincy provides official assets and service/pricing details.
- Create a Google Apps Script connection issue after Manny provides the real Web App URL.

## Stop condition
ATL-56 stabilization is complete for local demo review. Next work should be a separate issue so the demo stabilization scope does not expand into deployment, QTime content production, or external automation.
