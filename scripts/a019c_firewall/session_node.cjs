// Fixed permission entrypoint for unchanged browser-session assertions.
'use strict';
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
assert.equal(process.env.MALECNS_A019C_R2_FIREWALL, '1');
assert.equal(process.argv[2], 'browser-session-recovery-contract-v1');
assert(process.permission);
for (const scope of ['child', 'worker', 'fs.write', 'addons', 'wasi']) {
  assert.equal(process.permission.has(scope), false);
}
const root = path.resolve(__dirname, '../..');
const probe = path.join(root, 'data', 'male-cns-v1', 'connectome-probe.feather');
assert.throws(() => fs.readFileSync(probe), {code: 'ERR_ACCESS_DENIED'});
assert.throws(() => require('node:child_process').spawnSync(process.execPath, ['-e', '1']),
  {code: 'ERR_ACCESS_DENIED'});
console.log('Browser session guard ACTIVE; payload and descendants BLOCKED');
process.argv = [process.execPath, path.join(root, 'tests/js/workbench_session.cjs'), process.argv[3]];
require(process.argv[1]);
