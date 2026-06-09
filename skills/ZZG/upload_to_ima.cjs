// upload_to_ima.cjs
// Optional IMA upload helper for Investor Harness.
//
// Usage:
//   node upload_to_ima.cjs --file <report_path> --notebook <name> --config config/ima.local.json
//
// The public repository does not contain notebook folder IDs or credentials.
// Copy config/ima.example.json to config/ima.local.json and fill in local values.

const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https');
const { URL } = require('url');

const args = process.argv.slice(2);
let filePath = null;
let notebookName = 'Company Analysis';
let customTitle = null;
const repoRoot = path.resolve(__dirname, '..', '..');
let configPath = process.env.IMA_CONFIG_PATH || path.join(repoRoot, 'config', 'ima.local.json');

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--file' || args[i] === '-f') {
    filePath = args[++i];
  } else if (args[i] === '--notebook' || args[i] === '-n') {
    notebookName = args[++i];
  } else if (args[i] === '--title' || args[i] === '-t') {
    customTitle = args[++i];
  } else if (args[i] === '--config' || args[i] === '-c') {
    configPath = args[++i];
  } else if (args[i] === '--help' || args[i] === '-h') {
    console.log('Usage: node upload_to_ima.cjs --file <report_path> [--notebook <name>] [--title <title>] [--config config/ima.local.json]');
    process.exit(0);
  }
}

function expandHome(p) {
  if (!p) return p;
  if (p === '~') return os.homedir();
  if (p.startsWith('~/') || p.startsWith('~\\')) return path.join(os.homedir(), p.slice(2));
  return p;
}

if (!filePath) {
  console.error('ERROR: --file <report_path> is required');
  process.exit(1);
}

filePath = expandHome(filePath);
configPath = expandHome(configPath);

if (!fs.existsSync(filePath)) {
  console.error('ERROR: File not found:', filePath);
  process.exit(1);
}

if (!fs.existsSync(configPath)) {
  console.error('ERROR: IMA config not found:', configPath);
  console.error('Copy config/ima.example.json to config/ima.local.json and fill in local values.');
  process.exit(1);
}

let config;
try {
  config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
} catch (e) {
  console.error('ERROR: Failed to parse IMA config:', e.message);
  process.exit(1);
}

const cid = config.client_id;
const key = config.api_key;
const notebooks = config.notebooks || {};
const folderId = notebooks[notebookName];

if (!cid || !key) {
  console.error('ERROR: IMA config must include client_id and api_key.');
  process.exit(1);
}

if (!folderId) {
  console.error('ERROR: Unknown notebook name:', notebookName);
  console.error('  Known notebooks:', Object.keys(notebooks).join(', ') || '(none configured)');
  process.exit(1);
}

const content = fs.readFileSync(filePath, 'utf8');

let title = customTitle;
if (!title) {
  const firstLine = content.split(/\r?\n/)[0] || '';
  const m = firstLine.match(/^#\s+(.+?)\s*$/);
  if (m) title = m[1];
}

const body = JSON.stringify({
  content_format: 1,
  content,
  folder_id: folderId,
});

const url = new URL('https://ima.qq.com/openapi/note/v1/import_doc');
const options = {
  method: 'POST',
  hostname: url.hostname,
  path: url.pathname,
  headers: {
    'ima-openapi-clientid': cid,
    'ima-openapi-apikey': key,
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body, 'utf8'),
  },
};

console.log('Uploading:', filePath);
console.log('  size:', content.length, 'chars');
console.log('  notebook:', notebookName);
if (title) console.log('  title:', title);

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    try {
      const j = JSON.parse(data);
      console.log();
      console.log('IMA response:');
      console.log(JSON.stringify(j, null, 2));
      if (j.code === 0 && j.data && j.data.note_id) {
        console.log();
        console.log('SUCCESS: note_id =', j.data.note_id);
        process.exit(0);
      }
      console.error();
      console.error('UPLOAD FAILED: code =', j.code, ', msg =', j.msg);
      process.exit(2);
    } catch (e) {
      console.error('Failed to parse response:', e.message);
      console.error('Raw body:', data);
      process.exit(2);
    }
  });
});

req.on('error', (e) => {
  console.error('Request error:', e.message);
  process.exit(2);
});

req.write(body);
req.end();
