// Fixed A007C validation entrypoint; historical frontend assertions are unchanged.
'use strict';
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
assert.equal(process.env.MALECNS_A019C_R2_FIREWALL, '1');
assert.equal(process.argv[2], 'a007c-synthetic-dom-contract-v1');
assert(process.permission);
for (const scope of ['child', 'worker', 'fs.write', 'addons', 'wasi']) {
  assert.equal(process.permission.has(scope), false);
}
const root = path.resolve(__dirname, '../..');
const probe = path.join(root, 'data', 'male-cns-v1', 'connectome-probe.feather');
assert.throws(() => fs.readFileSync(probe), {code: 'ERR_ACCESS_DENIED'});
console.log('A007C registered-payload probe BLOCKED before content read');
// Deny creation before a descendant can execute its registered-payload probe.
assert.throws(() => require('node:child_process').spawnSync(process.execPath,
  ['-e', 'require("fs").readFileSync(' + JSON.stringify(probe) + ')']),
  {code: 'ERR_ACCESS_DENIED'});
console.log('A007C descendant payload probe BLOCKED before process creation');
console.log('A007C guard ACTIVE; script-start; pid=' + process.pid);
process.argv = [process.execPath, path.join(root, 'tests/js/application_a007c.cjs'),
  process.argv[3], process.argv[4]];
console.log('A007C workload-start');
require(process.argv[1]);
