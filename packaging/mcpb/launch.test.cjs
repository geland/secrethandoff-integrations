'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { selectBinary } = require('./launch.cjs');
for (const platform of ['darwin', 'linux', 'win32']) {
  for (const arch of ['x64', 'arm64']) {
    test(`select ${platform}-${arch}`, () => {
      const entry = { path: `bin/${platform}-${arch}/secrethandoff${platform === 'win32' ? '.exe' : ''}`, sha256: 'a'.repeat(64) };
      assert.equal(selectBinary(platform, arch, {[`${platform}-${arch}`]: entry}), entry);
    });
  }
}
test('reject unsupported CPU and unsafe index paths', () => {
  assert.throws(() => selectBinary('linux', 'ia32', {}));
  assert.throws(() => selectBinary('darwin', 'arm64', {}));
  assert.throws(() => selectBinary('linux', 'x64', {'linux-x64': {path:'../../binary',sha256:'a'.repeat(64)}}));
});
