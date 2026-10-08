"use strict";
// Fixed-asset UI checks. No dataset access, subprocesses, or real networking.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const asset = path.resolve(__dirname, "../../src/malecns_sim/application/static/flight.js");
const read = fs.readFileSync.bind(fs);
fs.readFileSync = (target, ...args) => {
  if (typeof target !== "string" || path.resolve(target) !== asset) throw new Error("Only the fixed flight UI asset is admitted");
  return read(target, ...args);
};
const source = fs.readFileSync(asset, "utf8");
const pixels = (size = 256) => Array.from({length: size}, () => Array.from({length: size}, () => [1, 2, 3]));
const flush = async () => { for (let i = 0; i < 20; i++) await Promise.resolve(); };
const copy = value => JSON.parse(JSON.stringify(value));

function harness(configured) {
  const painted = [], clears = [];
  const context = {clearRect(){clears.push(true);}, createImageData(width, height){return {data: new Uint8ClampedArray(width*height*4)};}, putImageData(){painted.push(true);}, drawImage(){painted.push(true);}};
  const elements = Object.fromEntries(["run", "pause", "step", "reset", "refresh", "export", "status", "left", "right", "overview", "frame-status", "body", "sensory", "neural", "action", "identity", "spec"].map(id => [id,
    {id, disabled: true, textContent: "", handlers: {}, getContext: () => context, addEventListener(type, handler){this.handlers[type] = handler;}}]));
  let state = {configured, message: "No prepared model attached", running: false, failed: false, failure: null,
    simulation_ms: 0, condition: "intact", session_identity: "fixture", generation: 1, revision: 1,
    body: {terminal: false, position_cm: [0, 0, 1]}, latest: null,
    spec: {coupling: {control_ms: .2, maximum_steps: 10}}};
  let failNext = false, failRefresh = false, holdFrame = false, releaseFrame = null, failFrame = false, encodedFrame = false;
  const requests = [], timers = new Map(), documentHandlers = {};
  const sandbox = {URLSearchParams, Uint8ClampedArray, Uint8Array, JSON, Array, Number, Blob, atob,
    Image: class {constructor(){throw new Error("CSP blocks data-URL image loading");}},
    createImageBitmap: async blob => {assert.equal(blob.type, "image/jpeg"); assert.ok(blob.size > 0); return {close(){}};},
    location: {hash: "#token=fixture-session", pathname: "/flight"},
    sessionStorage: {setItem(){}, getItem(){return null;}}, history: {replaceState(){}},
    document: {hidden: false, getElementById: id => elements[id], addEventListener: (type, handler) => documentHandlers[type] = handler},
    setTimeout: fn => {const id = timers.size + 1; timers.set(id, fn); return id;}, clearTimeout: id => timers.delete(id),
    fetch: async (url, options) => {
      requests.push({url, options});
      assert.equal(options.headers["X-Local-Session"], "fixture-session");
      if (url.endsWith("/frame") && holdFrame) {holdFrame = false; await new Promise(resolve => {releaseFrame = resolve;});}
      if (url.endsWith("/frame") && failFrame) {failFrame = false; throw new Error("Temporary camera failure");}
      if (failRefresh && url === "/api/flight" && options.method === "GET") {failRefresh = false; throw new Error("Session unavailable");}
      if (failNext && options.method === "POST") {failNext = false; return {ok: false, json: async () => ({error: {message: "Rejected stale command"}})};}
      if (options.method === "POST") {
        const body = JSON.parse(options.body);
        assert.deepEqual(Object.keys(body).sort(), ["command", "generation", "revision"]);
        assert.equal(body.generation, state.generation); assert.equal(body.revision, state.revision);
        if (body.command === "run") state.running = true;
        if (body.command === "pause") state.running = false;
        if (body.command === "step" || body.command === "tick") state.simulation_ms += .2;
        state.revision++;
      }
      const response = url.endsWith("/frame") ? {session_identity: state.session_identity, generation: state.generation,
        revision: state.revision, simulation_ms: state.simulation_ms, eyes: encodedFrame ? {overview: {width:512, height:512, image_url:"data:image/jpeg;base64,/9j/2Q=="}} : {left: pixels(), right: pixels(), overview: pixels(512)}} : copy(state);
      return {ok: true, json: async () => response};
    }};
  vm.runInNewContext(source, sandbox);
  return {elements, requests, painted, clears, timers, documentHandlers, sandbox, fail: () => {failNext = true;},
    holdFrame: () => {holdFrame = true;}, releaseFrame: () => releaseFrame(), failFrame: () => {failFrame = true;},
    useEncoded: () => {encodedFrame = true;},
    failRefresh: () => {failRefresh = true;}, state: () => state, click: id => elements[id].handlers.click()};
}

(async () => {
  const absent = harness(false); await flush();
  assert.equal(absent.elements.run.disabled, true);
  assert.equal(absent.requests.length, 1);
  assert.equal(absent.painted.length, 0);
  const continuous = harness(true); await flush();
  continuous.state().spec.coupling.maximum_steps = null;
  continuous.state().simulation_ms = 601;
  continuous.click("refresh"); await flush();
  assert.equal(continuous.elements.run.disabled, false);
  assert.equal(continuous.elements.step.disabled, false);
  const ready = harness(true); await flush();
  assert.equal(ready.elements.run.disabled, false);
  assert.equal(ready.painted.length, 3);
  assert.equal(ready.elements.overview.width, 512);
  assert.equal(ready.elements.left.width, 256);
  assert.equal(ready.state().simulation_ms, 0);
  ready.holdFrame(); ready.click("step"); await flush();
  assert.equal(ready.clears.length, 0, "Retain the visible image while a new frame is in flight");
  assert.equal(ready.painted.length, 3);
  ready.releaseFrame(); await flush();
  assert.equal(ready.painted.length, 6);
  ready.useEncoded(); ready.click("refresh"); await flush();
  assert.equal(ready.painted.length, 7, "Decode and display the compressed primary frame");
  assert.equal(ready.clears.length, 0);
  ready.failFrame(); ready.click("refresh"); await flush();
  assert.equal(ready.clears.length, 0);
  assert.match(ready.elements["frame-status"].textContent, /Holding camera frame at 0.2 ms/);
  ready.click("step"); await flush();
  assert.equal(ready.state().simulation_ms, .4);
  assert.equal(ready.timers.size, 0);
  ready.click("run"); await flush();
  assert.equal(ready.timers.size, 1);
  assert.equal(ready.elements.step.disabled, true);
  ready.fail(); ready.timers.values().next().value(); await flush();
  assert.equal(ready.timers.size, 0);
  assert.match(ready.elements.status.textContent, /Execution stopped/);
  ready.failRefresh(); ready.click("refresh"); await flush();
  assert.equal(ready.timers.size, 0);
  assert.match(ready.elements.status.textContent, /Session unavailable/);
  ready.click("pause"); await flush();
  assert.equal(ready.state().running, false);
  const prior = ready.state().simulation_ms;
  ready.sandbox.document.hidden = true; ready.documentHandlers.visibilitychange(); await flush();
  assert.equal(ready.state().simulation_ms, prior);
  assert.equal(ready.timers.size, 0);
  assert.ok(ready.requests.filter(r => r.options.method === "POST").every(r => !r.options.body.includes("pose")));
  console.log("PASS: no-model fail-closed UI, token header, physical-frame display, manual step, serialized run, stop after command failure, hidden-tab pacing, no client-authored pose.");
})().catch(error => {console.error(error);process.exitCode = 1;});
