"use strict";
(() => {
  const $ = id => document.getElementById(id);
  let token = new URLSearchParams(location.hash.slice(1)).get("token") || "";
  try {
    if (token) sessionStorage.setItem("malecns-local-session", token);
    else token = sessionStorage.getItem("malecns-local-session") || "";
    if (token && location.hash) history.replaceState(null, "", location.pathname);
  } catch {}
  let snapshot = null, busy = false, timer = null, frameError = "", requestEpoch = 0, lastFrameTime = null, lastFrameWall = null;
  // Target dragging: the observer sets a goal only; the body moves the sphere in physics time.
  const BOUNDS = [[-10, 10], [-10, 10], [0.1, 5]];
  let pendingTarget = null, inflightTarget = null, drag = null, camera = null, overviewImage = null, mapView = null;
  let trail = [], trailGeneration = null;
  const clamp = (v, [low, high]) => Math.min(high, Math.max(low, v));
  const goal = () => pendingTarget || inflightTarget || snapshot?.body?.target_goal_cm || null;
  const movable = () => Boolean(snapshot?.configured && snapshot.body?.target_cm && !snapshot.failed);
  function project(p) {
    // MuJoCo cameras look along their local -z axis; xmat is row-major camera-to-world.
    if (!camera) return null;
    const m = camera.xmat, c = camera.position_cm, d = [p[0]-c[0], p[1]-c[1], p[2]-c[2]];
    const x = m[0]*d[0]+m[3]*d[1]+m[6]*d[2], y = m[1]*d[0]+m[4]*d[1]+m[7]*d[2], z = m[2]*d[0]+m[5]*d[1]+m[8]*d[2];
    if (z >= 0) return null;
    const half = $("overview").width/2, f = half/Math.tan(camera.fovy_deg*Math.PI/360);
    return {x: half+x/-z*f, y: half-y/-z*f, scale: f/-z};
  }
  function unproject(px, py, height) {
    if (!camera) return null;
    const m = camera.xmat, c = camera.position_cm, half = $("overview").width/2, f = half/Math.tan(camera.fovy_deg*Math.PI/360);
    const v = [(px-half)/f, -(py-half)/f, -1], ray = [0, 1, 2].map(i => m[3*i]*v[0]+m[3*i+1]*v[1]+m[3*i+2]*v[2]);
    const t = Math.abs(ray[2]) < 1e-9 ? -1 : (height-c[2])/ray[2];
    return t > 0 ? [c[0]+t*ray[0], c[1]+t*ray[1], height] : null;
  }
  function drawOverview() {
    if (!overviewImage) return;
    const ctx = $("overview").getContext("2d"), target = snapshot?.body?.target_cm, wanted = goal();
    ctx.drawImage(overviewImage, 0, 0);
    if (!target || !wanted || Math.hypot(...wanted.map((v, i) => v-target[i])) < 1e-4) return;
    const from = project(target), to = project(wanted);
    if (!to) return;
    ctx.save(); ctx.strokeStyle = "#ffb070"; ctx.lineWidth = 2; ctx.setLineDash([6, 5]);
    ctx.beginPath(); ctx.arc(to.x, to.y, Math.max(6, (snapshot.body.target_radius_cm || .08)*to.scale), 0, 2*Math.PI); ctx.stroke();
    if (from) { ctx.beginPath(); ctx.moveTo(from.x, from.y); ctx.lineTo(to.x, to.y); ctx.stroke(); }
    ctx.restore();
  }
  function fitMap() {
    const points = [...trail, snapshot?.body?.target_cm, goal()].filter(Boolean);
    if (!points.length) return null;
    const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
    const span = Math.max(2, Math.max(...xs)-Math.min(...xs), Math.max(...ys)-Math.min(...ys))*1.25;
    return {cx: (Math.max(...xs)+Math.min(...xs))/2, cy: (Math.max(...ys)+Math.min(...ys))/2, scale: $("map").width/span};
  }
  const toMap = p => [$("map").width/2+(p[0]-mapView.cx)*mapView.scale, $("map").height/2-(p[1]-mapView.cy)*mapView.scale];
  const fromMap = (x, y) => [mapView.cx+(x-$("map").width/2)/mapView.scale, mapView.cy-(y-$("map").height/2)/mapView.scale];
  function drawMap() {
    const canvas = $("map"), ctx = canvas.getContext("2d"), body = snapshot?.configured ? snapshot.body : null;
    ctx.fillStyle = "#0b151b"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    // Freeze the view while dragging so the pointer keeps a stable world mapping.
    if (!drag) mapView = body ? fitMap() : null;
    if (!mapView || !body) return;
    const step = mapView.scale >= 60 ? .5 : mapView.scale >= 15 ? 1 : 5;
    const [x0, y1] = fromMap(0, 0), [x1, y0] = fromMap(canvas.width, canvas.height);
    ctx.strokeStyle = "#1e323b"; ctx.lineWidth = 1; ctx.beginPath();
    for (let x = Math.ceil(x0/step)*step; x <= x1; x += step) { const [sx] = toMap([x, 0]); ctx.moveTo(sx, 0); ctx.lineTo(sx, canvas.height); }
    for (let y = Math.ceil(y0/step)*step; y <= y1; y += step) { const [, sy] = toMap([0, y]); ctx.moveTo(0, sy); ctx.lineTo(canvas.width, sy); }
    ctx.stroke();
    ctx.fillStyle = "#7f9aa3"; ctx.font = "11px system-ui"; ctx.fillText(`grid ${step} cm · top-down · +x right, +y up`, 8, canvas.height-8);
    if (trail.length > 1) {
      ctx.strokeStyle = "#8ccbb9"; ctx.lineWidth = 2; ctx.beginPath();
      trail.forEach((p, i) => { const [x, y] = toMap(p); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.stroke();
    }
    const radius = Math.max(5, (body.target_radius_cm || .08)*mapView.scale), wanted = goal(), target = body.target_cm;
    if (wanted && target) {
      const [gx, gy] = toMap(wanted), [tx, ty] = toMap(target);
      ctx.save(); ctx.setLineDash([5, 4]); ctx.strokeStyle = "#ffb070"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(gx, gy); ctx.stroke();
      ctx.beginPath(); ctx.arc(gx, gy, radius, 0, 2*Math.PI); ctx.stroke(); ctx.restore();
      ctx.fillStyle = "#f2591f"; ctx.beginPath(); ctx.arc(tx, ty, radius, 0, 2*Math.PI); ctx.fill();
    }
    if (body.reference?.com_cm) {
      // Policy controller: the neural-steered reference the learned policy is tracking.
      const [rx, ry] = toMap(body.reference.com_cm);
      ctx.strokeStyle = "#9bb8ff"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(rx, ry, 4, 0, 2*Math.PI); ctx.stroke();
    }
    const q = body.quaternion_wxyz, yaw = q ? Math.atan2(2*(q[0]*q[3]+q[1]*q[2]), 1-2*(q[2]*q[2]+q[3]*q[3])) : 0;
    const [fx, fy] = toMap(body.position_cm);
    ctx.save(); ctx.translate(fx, fy); ctx.rotate(-yaw); ctx.fillStyle = "#e4f0ef";
    ctx.beginPath(); ctx.moveTo(10, 0); ctx.lineTo(-6, 6); ctx.lineTo(-3, 0); ctx.lineTo(-6, -6); ctx.closePath(); ctx.fill(); ctx.restore();
  }
  function showTarget() {
    const target = snapshot?.configured ? snapshot.body?.target_cm : null, wanted = goal(), height = $("target-height");
    height.disabled = !movable();
    if (!movable()) {
      $("target-readout").textContent = !snapshot?.configured ? "No target available." : target ? "Target is frozen after a failure; Reset to continue." : "This body has no movable target.";
      return;
    }
    if (!drag && document.activeElement !== height) height.value = String(wanted[2]);
    $("target-height-value").textContent = Number(height.value).toFixed(2);
    const fmt = p => p.map(v => v.toFixed(2)).join(", ");
    const distance = Math.hypot(...snapshot.body.position_cm.map((v, i) => v-target[i]));
    $("target-readout").textContent = `Target (${fmt(target)}) cm → goal (${fmt(wanted)}) cm · ${(distance*10).toFixed(1)} mm from the fly${pendingTarget || inflightTarget ? " · sending goal…" : ""}`;
  }
  function requestTarget(position) {
    pendingTarget = position.map((v, i) => clamp(v, BOUNDS[i]));
    drawOverview(); drawMap(); showTarget();
    // While running, the next scheduled tick carries the goal; otherwise send it now.
    if (!busy && !snapshot.running) command("target");
  }
  function canvasPoint(event) {
    const canvas = event.currentTarget, rect = canvas.getBoundingClientRect();
    return [(event.clientX-rect.left)*canvas.width/rect.width, (event.clientY-rect.top)*canvas.height/rect.height];
  }
  function startDrag(event, kind) {
    drag = {canvas: kind, height: goal()[2]};
    event.currentTarget.setPointerCapture?.(event.pointerId);
    event.currentTarget.classList?.add("dragging");
    event.preventDefault();
  }
  $("overview").addEventListener("pointerdown", event => {
    if (!movable() || !camera) return;
    const [x, y] = canvasPoint(event), radius = snapshot.body.target_radius_cm || .08;
    const hit = [snapshot.body.target_cm, goal()].some(p => { const s = project(p); return s && Math.hypot(s.x-x, s.y-y) <= Math.max(18, radius*s.scale*1.5); });
    if (hit) startDrag(event, "overview");
  });
  $("map").addEventListener("pointerdown", event => {
    if (!movable() || !mapView) return;
    startDrag(event, "map");
    requestTarget([...fromMap(...canvasPoint(event)), drag.height]);
  });
  for (const id of ["overview", "map"]) {
    $(id).addEventListener("pointermove", event => {
      if (drag?.canvas !== id) return;
      const point = id === "map" ? [...fromMap(...canvasPoint(event)), drag.height] : unproject(...canvasPoint(event), drag.height);
      if (point) requestTarget(point);
    });
    const end = event => { if (drag?.canvas === id) { drag = null; event.currentTarget.classList?.remove("dragging"); drawMap(); } };
    $(id).addEventListener("pointerup", end);
    $(id).addEventListener("pointercancel", end);
  }
  $("target-height").addEventListener("input", event => {
    const wanted = goal();
    if (movable() && wanted) requestTarget([wanted[0], wanted[1], Number(event.currentTarget.value)]);
  });
  async function api(path, body) {
    const response = await fetch(path, {method: body ? "POST" : "GET",
      headers: {"X-Local-Session": token, "Content-Type": "application/json"},
      body: body ? JSON.stringify(body) : undefined});
    const value = await response.json();
    if (!response.ok) throw new Error(value.error?.message || value.message || "Model request failed");
    return value;
  }
  function controls() {
    const ready = !busy && snapshot?.configured;
    for (const name of ["run", "pause", "step", "reset", "export"]) $(name).disabled = !ready;
    $("refresh").disabled = busy;
    if (ready) {
      const limit = snapshot.spec.coupling.maximum_steps;
      const ended = snapshot.body.terminal || limit !== null && limit !== undefined && snapshot.simulation_ms >= snapshot.spec.coupling.control_ms * limit - 1e-9;
      $("run").disabled = snapshot.running || snapshot.failed || ended;
      $("step").disabled = snapshot.running || snapshot.failed || ended;
      $("pause").disabled = !snapshot.running;
    }
  }
  function paint() {
    if (!snapshot?.configured) {
      for (const side of ["overview", "left", "right"]) $(side).getContext("2d").clearRect(0, 0, $(side).width, $(side).height);
      lastFrameTime = null;
      $("status").textContent = snapshot?.message || "No configured flight session.";
      $("identity").textContent = "No prepared neural runtime and physical body attached.";
      for (const name of ["body", "sensory", "neural", "action", "spec"]) $(name).textContent = "No configured session.";
      $("frame-status").textContent = "No body-camera frame available.";
      overviewImage?.close?.(); overviewImage = camera = null;
      drawMap(); showTarget(); controls(); return;
    }
    $("status").textContent = `${snapshot.failed ? "FAILED" : snapshot.running ? "Running" : "Paused"} · ${snapshot.simulation_ms.toFixed(1)} ms · ${snapshot.condition}${snapshot.failure ? " · " + snapshot.failure : ""}`;
    $("body").textContent = JSON.stringify(snapshot.body, null, 2);
    for (const name of ["sensory", "neural", "action"]) $(name).textContent = JSON.stringify(snapshot.latest?.[name] || "No interval executed.", null, 2);
    if (snapshot.diagnostics) {
      const d = snapshot.diagnostics;
      const sensory = d.population_spikes.sensory_left+d.population_spikes.sensory_right;
      const motor = Object.entries(d.population_spikes).filter(([name]) => !name.startsWith("sensory_")).reduce((total, [, count]) => total+count, 0);
      const activity = d.input_events === 0 ? "No visual stimulus events have been applied." : sensory === 0 ? "Visual stimulus was applied; mapped sensory neurons have not spiked." : motor === 0 ? "Sensory neurons spiked; mapped motor readouts have not spiked." : "Mapped motor spikes observed; biological flight control remains unvalidated.";
      $("neural").textContent = activity+"\n"+JSON.stringify({episode_totals:d, last_interval:snapshot.latest?.neural}, null, 2);
    }
    if (trailGeneration !== snapshot.generation) { trail = []; trailGeneration = snapshot.generation; }
    const last = trail[trail.length-1], here = snapshot.body.position_cm;
    if (!last || Math.hypot(...here.map((v, i) => v-last[i])) > 1e-4) trail.push([...here]);
    if (trail.length > 5000) trail.splice(0, trail.length-5000);
    drawMap(); showTarget();
    $("identity").textContent = snapshot.session_identity;
    $("spec").textContent = JSON.stringify(snapshot.spec, null, 2);
    if (snapshot.spec.coupling) $("step").textContent = `Step · ${snapshot.spec.coupling.control_ms} ms`;
    controls();
  }
  async function drawEye(side, pixels) {
    if (pixels?.image_url) {
      if (!pixels.image_url.startsWith("data:image/jpeg;base64,") || pixels.width !== 512 || pixels.height !== 512) throw new Error("Invalid encoded camera frame");
      // Decode bytes directly: the page CSP rejects data-URL image loads.
      const bytes = Uint8Array.from(atob(pixels.image_url.split(",", 2)[1]), value => value.charCodeAt(0));
      const image = await createImageBitmap(new Blob([bytes], {type: "image/jpeg"}));
      const canvas = $(side);
      if (canvas.width !== pixels.width) canvas.width = pixels.width;
      if (canvas.height !== pixels.height) canvas.height = pixels.height;
      if (side === "overview") {
        // Keep the decoded frame so goal overlays can be redrawn while dragging.
        overviewImage?.close?.(); overviewImage = image;
        const geometry = pixels.camera;
        camera = geometry?.position_cm?.length === 3 && geometry.xmat?.length === 9 && geometry.fovy_deg > 0 ? geometry : null;
        drawOverview();
        return;
      }
      canvas.getContext("2d").drawImage(image, 0, 0);
      image.close();
      return;
    }
    const size = pixels?.length;
    if (!Array.isArray(pixels) || !Number.isInteger(size) || size < 16 || size > 512 || pixels.some(row => !Array.isArray(row) || row.length !== size)) throw new Error("Invalid body camera dimensions");
    const ctx = $(side).getContext("2d"), image = ctx.createImageData(size, size);
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      const rgb = pixels[y][x], offset = (y * size + x) * 4;
      if (!Array.isArray(rgb) || rgb.length !== 3 || rgb.some(v => !Number.isInteger(v) || v < 0 || v > 255)) throw new Error("Invalid body camera pixels");
      image.data.set([...rgb, 255], offset);
    }
    // Canvas dimension assignments clear its backing buffer, even when unchanged.
    // Replace the old frame only after the complete new pixel buffer is ready.
    if ($(side).width !== size) $(side).width = size;
    if ($(side).height !== size) $(side).height = size;
    ctx.putImageData(image, 0, 0);
  }
  async function drawFrame(epoch) {
    if (!snapshot?.configured) return;
    try {
      const frame = await api("/api/flight/frame");
      if (epoch !== requestEpoch || frame.session_identity !== snapshot.session_identity || frame.generation !== snapshot.generation || frame.revision !== snapshot.revision) return;
      if (frame.eyes.left) await drawEye("left", frame.eyes.left);
      if (frame.eyes.right) await drawEye("right", frame.eyes.right);
      if (frame.eyes.overview) await drawEye("overview", frame.eyes.overview);
      const now = Date.now();
      const speed = lastFrameWall !== null && now > lastFrameWall && frame.simulation_ms >= lastFrameTime ? (frame.simulation_ms-lastFrameTime)/(now-lastFrameWall) : 0;
      lastFrameTime = frame.simulation_ms;
      lastFrameWall = now;
      const initial = snapshot.spec.body?.initial_position_cm;
      const distance = initial ? Math.hypot(...snapshot.body.position_cm.map((v, i) => v-initial[i])) : null;
      frameError = ""; $("frame-status").textContent = `Physical camera frame · ${frame.simulation_ms.toFixed(1)} ms · playback ${speed.toFixed(3)}×${distance === null ? "" : ` · displacement ${(distance*10).toFixed(3)} mm`}`;
    } catch (error) {
      frameError = error.message;
      $("frame-status").textContent = lastFrameTime === null ? `Body camera unavailable: ${frameError}` : `Holding camera frame at ${lastFrameTime.toFixed(1)} ms · ${frameError}`;
    }
  }
  function schedule() {
    clearTimeout(timer);
    if (snapshot?.configured && snapshot.running && !snapshot.failed && !document.hidden) timer = setTimeout(() => command("tick"), 20);
  }
  async function refresh() {
    if (busy) return;
    busy = true; clearTimeout(timer); controls(); const epoch = ++requestEpoch; let succeeded = false;
    try { snapshot = await api("/api/flight"); paint(); await drawFrame(epoch); succeeded = true; }
    catch (error) { $("status").textContent = `${error.message}. Open the workbench session URL first.`; }
    finally { busy = false; controls(); if (succeeded) schedule(); }
  }
  async function command(name) {
    if (busy || !snapshot?.configured) return;
    busy = true; clearTimeout(timer); controls(); const epoch = ++requestEpoch; let succeeded = false;
    const request = {command: name, generation: snapshot.generation, revision: snapshot.revision};
    if (name === "reset") pendingTarget = null;
    else if (pendingTarget) { request.target_cm = pendingTarget; inflightTarget = pendingTarget; pendingTarget = null; }
    try {
      const value = await api("/api/flight", request);
      if (epoch !== requestEpoch) return;
      if (value.generation < snapshot.generation || value.generation === snapshot.generation && value.revision < snapshot.revision) throw new Error("Stale flight response");
      snapshot = value; paint(); await drawFrame(epoch);
      succeeded = true;
    } catch (error) {
      $("status").textContent = error.message;
      try {snapshot = await api("/api/flight"); paint();} catch {}
      $("status").textContent = `${error.message}. Execution stopped in this client; refresh explicitly before continuing.`;
      clearTimeout(timer); pendingTarget = null;
    } finally { busy = false; inflightTarget = null; controls(); if (snapshot?.configured) { showTarget(); drawMap(); } }
    if (succeeded) schedule();
    // A goal dragged while this request was in flight is sent once the channel frees.
    if (succeeded && pendingTarget && !snapshot.running) command("target");
  }
  for (const name of ["run", "pause", "step", "reset"]) $(name).addEventListener("click", () => command(name));
  $("refresh").addEventListener("click", refresh);
  $("export").addEventListener("click", async () => {
    try {
      const value = await api("/api/flight/events"), url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], {type: "application/json"}));
      const link = document.createElement("a"); link.href = url; link.download = "engineered-flight-evidence.json"; link.click(); URL.revokeObjectURL(url);
    } catch (error) { $("status").textContent = error.message; }
  });
  document.addEventListener("visibilitychange", () => { if (document.hidden) clearTimeout(timer); else refresh(); });
  refresh();
})();
