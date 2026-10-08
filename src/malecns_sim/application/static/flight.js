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
      controls(); return;
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
    try {
      const value = await api("/api/flight", {command: name, generation: snapshot.generation, revision: snapshot.revision});
      if (epoch !== requestEpoch) return;
      if (value.generation < snapshot.generation || value.generation === snapshot.generation && value.revision < snapshot.revision) throw new Error("Stale flight response");
      snapshot = value; paint(); await drawFrame(epoch);
      succeeded = true;
    } catch (error) {
      $("status").textContent = error.message;
      try {snapshot = await api("/api/flight"); paint();} catch {}
      $("status").textContent = `${error.message}. Execution stopped in this client; refresh explicitly before continuing.`;
      clearTimeout(timer);
    } finally { busy = false; controls(); }
    if (succeeded) schedule();
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
