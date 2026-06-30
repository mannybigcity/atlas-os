const ABIS_CONFIG = {
  sheetId: '1Biwt4rV4SkVkDBzLv1QZCb1rtBedF2hozClwUoiSdCE',
  sheetName: 'Atlas Intake Database',
  notificationEmail: 'info@atlasforentrepreneurs.com',
  requiredHeaders: [
    'Timestamp',
    'Client ID',
    'Business Name',
    'Owner',
    'Email',
    'Assessment Answers',
    'Status',
    'Source',
    'Received At'
  ]
};

function setupAbisSheet() {
  const sheet = getAbisSheet_();
  const headerRange = sheet.getRange(1, 1, 1, ABIS_CONFIG.requiredHeaders.length);
  const existingHeaders = headerRange.getValues()[0];
  const needsHeaders = existingHeaders.every((cell) => String(cell || '').trim() === '');

  if (needsHeaders) {
    headerRange.setValues([ABIS_CONFIG.requiredHeaders]);
    sheet.setFrozenRows(1);
  }
}

function doPost(event) {
  try {
    const payload = parsePayload_(event);
    validatePayload_(payload);

    const row = [
      payload.timestamp,
      payload.clientId,
      payload.businessName,
      payload.owner,
      payload.email,
      JSON.stringify(payload.assessmentAnswers || {}),
      payload.status || 'New Assessment',
      payload.source || 'Atlas Website',
      new Date().toISOString()
    ];

    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      const sheet = getAbisSheet_();
      ensureHeaders_(sheet);
      sheet.appendRow(row);
    } finally {
      lock.releaseLock();
    }

    sendNotification_(payload);

    return jsonResponse_({ ok: true, clientId: payload.clientId });
  } catch (error) {
    console.error(error);
    return jsonResponse_({ ok: false, error: String(error && error.message ? error.message : error) });
  }
}

function doGet() {
  return jsonResponse_({ ok: true, service: 'Atlas ABIS Intake Web App' });
}

function getAbisSheet_() {
  const spreadsheet = SpreadsheetApp.openById(ABIS_CONFIG.sheetId);
  return spreadsheet.getSheetByName(ABIS_CONFIG.sheetName) || spreadsheet.getSheets()[0];
}

function ensureHeaders_(sheet) {
  const width = ABIS_CONFIG.requiredHeaders.length;
  const current = sheet.getRange(1, 1, 1, width).getValues()[0];
  const needsUpdate = ABIS_CONFIG.requiredHeaders.some((header, index) => current[index] !== header);
  if (needsUpdate) {
    sheet.getRange(1, 1, 1, width).setValues([ABIS_CONFIG.requiredHeaders]);
    sheet.setFrozenRows(1);
  }
}

function parsePayload_(event) {
  const raw = event && event.postData && event.postData.contents ? event.postData.contents : '{}';
  return JSON.parse(raw);
}

function validatePayload_(payload) {
  const required = ['timestamp', 'clientId', 'businessName', 'owner', 'email', 'assessmentAnswers', 'status', 'source'];
  const missing = required.filter((key) => payload[key] === undefined || payload[key] === null || String(payload[key]).trim() === '');
  if (missing.length) {
    throw new Error(`Missing required ABIS field(s): ${missing.join(', ')}`);
  }
}

function sendNotification_(payload) {
  const answers = payload.assessmentAnswers || {};
  const subject = `New Atlas Business Assessment: ${payload.businessName}`;
  const body = [
    'A new Atlas Business Intelligence Intake System submission was received.',
    '',
    `Timestamp: ${payload.timestamp}`,
    `Client ID: ${payload.clientId}`,
    `Business Name: ${payload.businessName}`,
    `Owner: ${payload.owner}`,
    `Email: ${payload.email}`,
    `Status: ${payload.status}`,
    `Source: ${payload.source}`,
    '',
    'Assessment Summary:',
    `What they sell: ${answers.offer || ''}`,
    `Growth blocker: ${answers.blocker || ''}`,
    `More Saturdays outcome: ${answers.saturdays || ''}`
  ].join('\n');

  MailApp.sendEmail(ABIS_CONFIG.notificationEmail, subject, body);
}

function jsonResponse_(body) {
  return ContentService
    .createTextOutput(JSON.stringify(body))
    .setMimeType(ContentService.MimeType.JSON);
}
