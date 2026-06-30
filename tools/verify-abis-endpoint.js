#!/usr/bin/env node
const endpoint = process.argv[2] || process.env.ATLAS_ABIS_APPS_SCRIPT_ENDPOINT;

if (!endpoint || endpoint === 'PASTE_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE') {
  console.error('Usage: node tools/verify-abis-endpoint.js <GOOGLE_APPS_SCRIPT_WEB_APP_URL>');
  console.error('Or set ATLAS_ABIS_APPS_SCRIPT_ENDPOINT before running this script.');
  process.exit(2);
}

if (!/^https:\/\/script\.google\.com\/macros\/s\//.test(endpoint)) {
  console.error('Endpoint does not look like a Google Apps Script Web App URL.');
  process.exit(2);
}

const timestamp = new Date().toISOString();
const payload = {
  timestamp,
  clientId: `ABIS-TEST-${timestamp.replace(/[-:.]/g, '').slice(0, 15)}Z`,
  businessName: 'ABIS Endpoint Test',
  owner: 'Atlas Verification',
  email: 'info@atlasforentrepreneurs.com',
  assessmentAnswers: {
    offer: 'Verification-only test submission',
    blocker: 'Confirm Google Sheets append path',
    saturdays: 'Confirm Atlas can receive assessments without manual copy/paste'
  },
  status: 'New Assessment',
  source: 'Atlas Website'
};

async function main() {
  const health = await fetch(endpoint, { method: 'GET', redirect: 'follow' });
  if (!health.ok) {
    throw new Error(`GET health check failed with HTTP ${health.status}`);
  }

  const response = await fetch(endpoint, {
    method: 'POST',
    redirect: 'follow',
    headers: { 'Content-Type': 'text/plain;charset=utf-8' },
    body: JSON.stringify(payload)
  });

  const text = await response.text();
  if (!response.ok) {
    throw new Error(`POST failed with HTTP ${response.status}: ${text}`);
  }

  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch (error) {
    throw new Error(`POST returned non-JSON response: ${text.slice(0, 300)}`);
  }

  if (!parsed.ok) {
    throw new Error(`Apps Script rejected payload: ${text}`);
  }

  console.log(`ABIS endpoint verification passed. Test Client ID: ${payload.clientId}`);
  console.log('Next manual checks: confirm a row appeared in the Google Sheet and an email arrived at info@atlasforentrepreneurs.com.');
}

main().catch((error) => {
  console.error(`ABIS endpoint verification failed: ${error.message}`);
  process.exit(1);
});
