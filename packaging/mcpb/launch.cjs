// The host provides Node. Only the selected binary reads MCP input.
'use strict';
const { createHash } = require('node:crypto');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { spawn } = require('node:child_process');

function selectBinary(platform, arch, binaries) {
  const target = `${platform}-${arch}`;
  const allowed = /^(darwin|linux|win32)-(x64|arm64)$/;
  if (!allowed.test(target) || !Object.hasOwn(binaries, target)) {
    throw new Error('unsupported platform');
  }
  const entry = binaries[target];
  const name = platform === 'win32' ? 'secrethandoff.exe' : 'secrethandoff';
  if (entry.path !== `bin/${target}/${name}` || !/^[a-f0-9]{64}$/.test(entry.sha256)) {
    throw new Error('invalid binary entry');
  }
  return entry;
}

function main() {
  let binary;
  try {
    const index = JSON.parse(readFileSync(join(__dirname, 'binaries.json'), 'utf8'));
    const entry = selectBinary(process.platform, process.arch, index.binaries);
    binary = join(__dirname, entry.path);
    const digest = createHash('sha256').update(readFileSync(binary)).digest('hex');
    if (digest !== entry.sha256) throw new Error('checksum mismatch');
  } catch {
    process.stderr.write('Secret Handoff: unsupported system or invalid bundle. Reinstall from the official download.\n');
    process.exitCode = 1;
    return;
  }
  // Never use a shell, read protocol input, or forward caller-supplied arguments.
  const child = spawn(binary, ['mcp'], { stdio: 'inherit', shell: false });
  child.on('error', () => {
    process.stderr.write('Secret Handoff: unable to start the bundled binary.\n');
    process.exitCode = 1;
  });
  for (const signal of ['SIGINT', 'SIGTERM']) {
    process.on(signal, () => { child.kill(signal); });
  }
  child.on('exit', (code, signal) => {
    process.exitCode = code ?? (signal === 'SIGINT' ? 130 : 143);
  });
}
module.exports = { selectBinary };
if (require.main === module) main();
