#!/usr/bin/env node
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const assessmentHtml = fs.readFileSync(path.join(root, 'free-business-assessment', 'index.html'), 'utf8');
const configPath = path.join(root, 'free-business-assessment', 'abis-config.js');

if (!fs.existsSync(configPath)) {
  throw new Error('Missing free-business-assessment/abis-config.js endpoint config file.');
}

const configScriptTag = '<script src="./abis-config.js"></script>';
const configTagIndex = assessmentHtml.indexOf(configScriptTag);
const inlineEndpointIndex = assessmentHtml.indexOf('const ABIS_APPS_SCRIPT_ENDPOINT');

if (configTagIndex === -1) {
  throw new Error('Assessment page does not load abis-config.js.');
}

if (inlineEndpointIndex === -1) {
  throw new Error('Assessment page is missing ABIS_APPS_SCRIPT_ENDPOINT setup.');
}

if (configTagIndex > inlineEndpointIndex) {
  throw new Error('abis-config.js must load before inline endpoint setup.');
}

const configContent = fs.readFileSync(configPath, 'utf8');
if (!configContent.includes('window.ATLAS_ABIS_APPS_SCRIPT_ENDPOINT')) {
  throw new Error('abis-config.js must set window.ATLAS_ABIS_APPS_SCRIPT_ENDPOINT.');
}

if (!configContent.includes('PASTE_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE')) {
  throw new Error('abis-config.js must keep a safe placeholder until Manny provides the Web App URL.');
}

console.log('ABIS non-live endpoint prep check passed.');
