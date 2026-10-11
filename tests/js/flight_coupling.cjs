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
  const strokes = [];
  const base = {clearRect(){clears.push(true);}, createImageData(width, height){return {data: new Uint8ClampedArray(width*height*4)};}, putImageData(){painted.push(true);}, drawImage(){painted.push(true);}, arc(x, y){strokes.push([x, y]);}};
  // Vector drawing calls (paths, fills, transforms) are accepted as no-ops.
  const context = new Proxy(base, {get: (target, name) => name in target ? target[name] : () => {}, set: () => true});
  const elements = Object.fromEntries(["run", "pause", "step", "reset", "refresh", "export", "status", "left", "right", "overview", "map", "target-height", "target-height-value", "target-readout", "frame-status", "body", "sensory", "neural", "action", "identity", "spec"].map(id => [id,
    {id, disabled: true, textContent: "", value: "", width: id === "map" ? 400 : 512, height: id === "map" ? 400 : 512, handlers: {}, getContext: () => context,
      classList: {add(){}, remove(){}}, setPointerCapture(){}, getBoundingClientRect(){return {left: 0, top: 0, width: this.width, height: this.height};},
      addEventListener(type, handler){this.handlers[type] = handler;}}]));
  let state = {configured, message: "No prepared model attached", running: false, failed: false, failure: null,
    simulation_ms: 0, condition: "intact", session_identity: "fixture", generation: 1, revision: 1,
    body: {terminal: false, position_cm: [0, 0, 1], quaternion_wxyz: [1, 0, 0, 0], target_cm: [.5, .2, 1], target_goal_cm: [.5, .2, 1], target_radius_cm: .08}, latest: null,
    spec: {coupling: {control_ms: .2, maximum_steps: 10}}};
  let failNext = false, failRefresh = false, holdFrame = false, releaseFrame = null, failFrame = false, encodedFrame = false;
  const requests = [], timers = new Map(), documentHandlers = {};
  const sandbox = {URLSearchParams, Uint8ClampedArray, Uint8Array, JSON, Array, Number, Blob, atob,
    Image: class {constructor(){throw new Error("CSP blocks data-URL image loading");}},
    createImageBitmap: async blob => {assert.equal(blob.type, "image/jpeg"); assert.ok(blob.size > 0); return {close(){}};},
    location: {hash: "#token=fixture-session", pathname: "/flight"},
    sessionStorage: {setItem(){}, getItem(){return null;}}, history: {replaceState(){}},
    document: {hidden: false, activeElement: null, getElementById: id => elements[id], addEventListener: (type, handler) => documentHandlers[type] = handler},
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
        const keys = Object.keys(body).sort();
        assert.ok(["command,generation,revision", "command,generation,revision,target_cm"].includes(keys.join()), keys.join());
        if (body.target_cm) { assert.notEqual(body.command, "reset"); state.body.target_goal_cm = body.target_cm; }
        assert.equal(body.generation, state.generation); assert.equal(body.revision, state.revision);
        if (body.command === "run") state.running = true;
        if (body.command === "pause") state.running = false;
        if (body.command === "step" || body.command === "tick") state.simulation_ms += .2;
        state.revision++;
      }
      const response = url.endsWith("/frame") ? {session_identity: state.session_identity, generation: state.generation,
        revision: state.revision, simulation_ms: state.simulation_ms, eyes: encodedFrame ? {overview: {width:512, height:512, image_url:"data:image/jpeg;base64,/9j/2Q==",
          // Camera 2 cm above (0, 0, 1) looking straight down; image +x is world +x.
          camera: {position_cm: [0, 0, 3], xmat: [1, 0, 0, 0, 1, 0, 0, 0, 1], fovy_deg: 90}}} : {left: pixels(), right: pixels(), overview: pixels(512)}} : copy(state);
      return {ok: true, json: async () => response};
    }};
  vm.runInNewContext(source, sandbox);
  return {elements, requests, painted, clears, timers, documentHandlers, sandbox, fail: () => {failNext = true;},
    holdFrame: () => {holdFrame = true;}, releaseFrame: () => releaseFrame(), failFrame: () => {failFrame = true;},
    useEncoded: () => {encodedFrame = true;},
    failRefresh: () => {failRefresh = true;}, state: () => state, click: id => elements[id].handlers.click(), strokes,
    pointer: (id, type, x, y) => elements[id].handlers[type]({currentTarget: elements[id], clientX: x, clientY: y, pointerId: 1, preventDefault(){}})};
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
  // Dragging the target in the body view: hit the projected sphere, then move on the z=1 plane.
  const drag = harness(true); await flush();
  drag.useEncoded(); drag.click("refresh"); await flush();
  const posts = () => drag.requests.filter(r => r.options.method === "POST").map(r => JSON.parse(r.options.body));
  // Sphere at (.5, .2, 1) seen from 2 cm above with f=256 px: (256+64, 256-25.6).
  drag.pointer("overview", "pointerdown", 0, 0);
  drag.pointer("overview", "pointermove", 100, 100); await flush();
  assert.equal(posts().length, 0, "A press away from the sphere does not start a drag");
  drag.pointer("overview", "pointerdown", 320, 230.4);
  drag.pointer("overview", "pointermove", 256-128, 256); await flush();
  let sent = posts().at(-1);
  assert.equal(sent.command, "target");
  assert.deepEqual(sent.target_cm.map(v => +v.toFixed(6)), [-1, 0, 1]);
  assert.deepEqual(drag.state().body.target_goal_cm, sent.target_cm);
  drag.pointer("overview", "pointerup", 0, 0);
  assert.equal(drag.state().simulation_ms, 0, "Moving the goal never advances simulated time");
  // Height slider keeps x/y and changes only z.
  drag.elements["target-height"].value = "2.5";
  drag.elements["target-height"].handlers.input({currentTarget: drag.elements["target-height"]}); await flush();
  assert.deepEqual(posts().at(-1).target_cm.map(v => +v.toFixed(6)), [-1, 0, 2.5]);
  // Map drags clamp to arena bounds; while running the goal rides on the next tick.
  drag.click("run"); await flush();
  drag.pointer("map", "pointerdown", 0, 0);
  drag.pointer("map", "pointermove", -1e6, 1e6); await flush();
  assert.equal(posts().at(-1).command, "run");
  drag.timers.values().next().value(); await flush();
  sent = posts().at(-1);
  assert.equal(sent.command, "tick");
  assert.deepEqual(sent.target_cm, [-10, -10, 2.5]);
  drag.pointer("map", "pointerup", 0, 0);
  drag.timers.values().next().value(); await flush();
  assert.equal(posts().at(-1).target_cm, undefined, "A goal is sent once, not repeated on every tick");
  drag.click("pause"); await flush();
  drag.pointer("map", "pointerdown", 200, 200); await flush();
  drag.click("reset"); await flush();
  assert.equal(posts().at(-1).target_cm, undefined, "Reset never carries a dragged goal");
  console.log("PASS: no-model fail-closed UI, token header, physical-frame display, manual step, serialized run, stop after command failure, hidden-tab pacing, no client-authored pose, target drag in view/map/height with bounds and tick piggybacking.");
})().catch(error => {console.error(error);process.exitCode = 1;});
