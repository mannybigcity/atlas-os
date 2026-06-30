#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const forbiddenPlaintext = [
  ['More', 'Saturdays', '49!'].join(''),
  ['QTime', 'More', 'Saturdays', '49!'].join('')
];

const requiredFiles = [
  'client-sign-in/index.html',
  'client-login/index.html',
  'client-portal/index.html',
  'client-dashboard/auth.js',
  'client-dashboard/index.html',
  'client-dashboard/qtime-productions/index.html',
  'client-dashboard/qtime-productions/welcome/index.html',
  'client-dashboard/qtime-productions/onboarding/index.html',
  'client-dashboard/qtime-productions/approvals/index.html',
  'client-dashboard/qtime-productions/reports/index.html'
];

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === '.snapshots') continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, files);
    else if (/\.(html|js|md|css)$/i.test(entry.name)) files.push(full);
  }
  return files;
}

const failures = [];

for (const rel of requiredFiles) {
  if (!fs.existsSync(path.join(root, rel))) {
    failures.push(`Missing required portal file: ${rel}`);
  }
}

for (const file of walk(root)) {
  const rel = path.relative(root, file).replace(/\\/g, '/');
  const content = fs.readFileSync(file, 'utf8');
  for (const secret of forbiddenPlaintext) {
    if (content.includes(secret)) {
      failures.push(`Plaintext temporary portal password leaked in deployable file: ${rel}`);
    }
  }
}

for (const rel of requiredFiles.filter(file => file.endsWith('.html') && file.startsWith('client-dashboard/'))) {
  const content = fs.readFileSync(path.join(root, rel), 'utf8');
  if (!content.includes('noindex, nofollow, noarchive')) {
    failures.push(`Missing noindex robots meta on dashboard page: ${rel}`);
  }
  if (!content.includes("atlasProtectPage('admin')") && !content.includes("atlasProtectPage('qtime')")) {
    failures.push(`Missing auth gate on dashboard page: ${rel}`);
  }
}

const authJs = fs.readFileSync(path.join(root, 'client-dashboard/auth.js'), 'utf8');
if (!authJs.includes("username: 'qtime-client'")) failures.push('Missing QTIME client username in auth.js');
if (!authJs.includes("clientSlug: 'qtime-productions'")) failures.push('Missing QTIME client slug in auth.js');
if (!/passwordHash: '[a-f0-9]{64}'/.test(authJs)) failures.push('Missing SHA-256 password hashes in auth.js');
if (authJs.includes('password:')) failures.push('auth.js must not store plaintext password fields');

const existingPortalHtml = fs.readFileSync(path.join(root, 'client-portal/index.html'), 'utf8');
const existingPortalJs = fs.readFileSync(path.join(root, 'client-portal/portal.js'), 'utf8');
if (!existingPortalHtml.includes('noindex, nofollow, noarchive')) failures.push('Existing /client-portal/ route must be noindex');
if (!existingPortalHtml.includes("atlasProtectPage('qtime')")) failures.push('Existing /client-portal/ route must use the shared QTIME auth gate');
if (existingPortalJs.includes('ACCESS_TOKEN') || existingPortalJs.includes('qtime-demo-v1')) failures.push('Existing /client-portal/ must not use legacy demo token access');
if (existingPortalJs.includes('executivePreview')) failures.push('Existing /client-portal/ must not keep executivePreview auth bypass');

if (failures.length) {
  console.error('Client portal security verification failed:');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('Client portal security verification passed.');
