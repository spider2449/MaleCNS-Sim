// Preserve the historical inline argv layout and every assertion.
process.argv = [process.execPath, process.argv[2]];

const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8').split('const $ =')[0];
function load(blocked, hash, stored) {
  let removed = false, reloads = 0;
  const listeners = {};
  const location = {hash, pathname:'/', search:'', reload(){reloads++;}};
  const storage = {
    getItem(){if(blocked) throw Error('blocked'); return stored;},
    setItem(key, value){if(blocked) throw Error('blocked'); stored = value;}
  };
  const context = vm.createContext({URLSearchParams, location, sessionStorage:storage,
    window:{history:{replaceState(){removed=true;location.hash='';}},
      addEventListener(name, handler){listeners[name]=handler;}}});
  vm.runInContext(source, context);
  return {context, location, listeners, removed, reloads:()=>reloads};
}
let page = load(false, '#token=fresh', 'stale');
assert.equal(vm.runInContext('token', page.context), 'fresh');
assert.equal(page.removed, true);
page.location.hash = '#token=replacement';
page.listeners.hashchange();
assert.equal(page.reloads(), 1);
page.location.hash = '#other';page.listeners.hashchange();
assert.equal(page.reloads(), 1);
page = load(true, '#token=fresh', 'stale');
assert.equal(vm.runInContext('token', page.context), 'fresh');
assert.equal(page.removed, false);
assert.equal(page.location.hash, '#token=fresh');
page = load(false, '', 'fresh');
assert.equal(vm.runInContext('token', page.context), 'fresh');
