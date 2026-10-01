"use strict";
let playback = null;
let spikeByStep = new Map();
let spikeByNeuron = new Map();
let playbackRows = [];
let playbackCursor = 0;
let playbackFrame = null;
let playbackStamp = null;
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");

function resetPlayback() {
  if (playbackFrame !== null) cancelAnimationFrame(playbackFrame);
  playbackFrame = null; playbackStamp = null; playback = null;
  spikeByStep = new Map(); spikeByNeuron = new Map(); playbackRows = []; playbackCursor = 0;
  $("playback-ready").hidden = true;
  $("playback-state").textContent = "Playback available after recorded result is finalized.";
  $("activity-inspector").textContent = "Select a displayed neuron or raster row.";
}
function playbackOrder(nodes) {
  const rank = n => n.roles.includes("stimulus") ? 0 : n.roles.includes("target") ? 3 : n.roles.includes("intervention") ? 2 : 1;
  return [...nodes].sort((a,b) => rank(a)-rank(b) || a.neuron_id-b.neuron_id).map(n => n.neuron_id);
}
async function loadPlayback(job, run, view) {
  if (run.state !== "COMPLETED") return;
  const start = performance.now();
  const data = await api("/api/runs/"+job+"/playback");
  if (activeJob !== job) return;
  if (data.job_id !== job || data.run_id !== run.run_id || data.spec_digest !== run.spec_digest || data.graph_fingerprint !== view.graph_fingerprint) throw new Error("Playback/run/graph identity mismatch");
  if (playback && playback.playback_payload_digest === data.playback_payload_digest) { playbackGraphChanged(); return; }
  resetPlayback(); playback = data;
  const decoded = performance.now()-start;
  const indexedAt = performance.now();
  for (const event of data.sparse_spikes) {
    if (!Number.isInteger(event.timestep) || event.timestep < 1 || event.timestep > Math.round(data.duration_ms/data.dt_ms)) throw new Error("Invalid authoritative spike timestep");
    if (!spikeByStep.has(event.timestep)) spikeByStep.set(event.timestep, []);
    spikeByStep.get(event.timestep).push(event.neuron_id);
    if (!spikeByNeuron.has(event.neuron_id)) spikeByNeuron.set(event.neuron_id, []);
    spikeByNeuron.get(event.neuron_id).push(event.timestep);
  }
  $("playback-ready").hidden = false; $("playback-state").textContent = "Completed recorded result";
  $("playback-cursor").max = data.duration_ms; $("playback-cursor").step = data.dt_ms;
  $("playback-identity").textContent = "Job: "+job+" · Run: "+data.run_id+" · Spec: "+data.spec_digest+" · Graph: "+data.graph_fingerprint+" · Result digest: "+data.authoritative_result_digest+" · Playback digest: "+data.playback_payload_digest;
  $("stimulus-schedule").textContent = "Configured stimulus window: "+data.stimulus.configured_start_ms+"–"+data.stimulus.configured_end_ms+" ms · requested "+data.stimulus.requested_frequency_hz+" Hz. Realized input events are not retained; no input event marks are inferred. Schedule fingerprint: "+data.stimulus.schedule_fingerprint;
  $("raster-note").textContent = "All prepared neurons were recorded for sparse output spikes. Rows show the current bounded viewport; zero marks means recorded with zero spikes. Decode/request "+decoded.toFixed(1)+" ms; index "+(performance.now()-indexedAt).toFixed(1)+" ms.";
  playbackGraphChanged(); setPlaybackCursor(0);
}
function playbackGraphChanged() {
  if (!playback || !graphView || playback.graph_fingerprint !== graphView.graph_fingerprint) return;
  playbackRows = playbackOrder(graphView.nodes);
  $("raster").style.height = Math.max(340, playbackRows.length*12+38)+"px";
  drawRaster(); drawPopulation(); drawGraph(); updateActivityInspector();
}
function activeSpikeSet() {
  const ids = new Set();
  if (!playback) return ids;
  const low = Math.max(0, playbackCursor-1), high = Math.min(playback.duration_ms, playbackCursor+1);
  const first = Math.max(1, Math.ceil((low-1e-9)/playback.dt_ms));
  const last = Math.min(Math.round(playback.duration_ms/playback.dt_ms), Math.floor((high+1e-9)/playback.dt_ms));
  for (let step=first; step<=last; step++) for (const id of spikeByStep.get(step)||[]) ids.add(id);
  return ids;
}
function setPlaybackCursor(time) {
  if (!playback) return;
  playbackCursor = Math.max(0, Math.min(playback.duration_ms, Math.round(time/playback.dt_ms)*playback.dt_ms));
  playbackCursor = Number(playbackCursor.toFixed(10));
  $("playback-cursor").value = playbackCursor;
  $("playback-time").textContent = playbackCursor.toFixed(1)+" ms";
  $("playback-window").textContent = "Highlighting recorded spikes in "+Math.max(0,playbackCursor-1).toFixed(1)+"–"+Math.min(playback.duration_ms,playbackCursor+1).toFixed(1)+" ms (inclusive display window)";
  drawGraph(); drawRaster(); drawTrace(); updateActivityInspector();
}
function stopPlayback() { if (playbackFrame !== null) cancelAnimationFrame(playbackFrame); playbackFrame=null; playbackStamp=null; }
function tickPlayback(stamp) {
  if (playbackStamp !== null) setPlaybackCursor(playbackCursor+(stamp-playbackStamp)*Number($("playback-speed").value));
  playbackStamp=stamp;
  if (playbackCursor >= playback.duration_ms) { stopPlayback(); return; }
  playbackFrame=requestAnimationFrame(tickPlayback);
}
function drawRaster() {
  const canvas=$("raster"), dpr=devicePixelRatio||1, width=Math.max(1,canvas.clientWidth), height=Math.max(1,canvas.clientHeight);
  canvas.width=Math.round(width*dpr); canvas.height=Math.round(height*dpr);
  const ctx=canvas.getContext("2d"); ctx.scale(dpr,dpr);ctx.fillStyle="#142430";ctx.fillRect(0,0,width,height);
  if (!playback || !playbackRows.length) return;
  const left=72, right=12, top=14, bottom=24, rowHeight=(height-top-bottom)/playbackRows.length, span=width-left-right;
  ctx.font="10px system-ui"; ctx.fillStyle="#aebdca";
  for(let i=0;i<playbackRows.length;i++) {
    const id=playbackRows[i], y=top+(i+.5)*rowHeight;
    if (id===selectedNode) {ctx.fillStyle="#31495d";ctx.fillRect(0,top+i*rowHeight,width,rowHeight);}
    ctx.fillStyle=id===playback.target_neuron_id?"#f3c86a":playback.stimulus.member_ids.includes(id)?"#65d4b7":"#aebdca";
    if(rowHeight>=7)ctx.fillText(String(id),3,y+3);
    ctx.fillStyle="#f4a261";
    for(const step of spikeByNeuron.get(id)||[]) {const x=left+step*playback.dt_ms/playback.duration_ms*span;ctx.fillRect(x,y-Math.max(1,rowHeight*.35),1,Math.max(2,rowHeight*.7));}
  }
  const cursorX=left+playbackCursor/playback.duration_ms*span;
  ctx.strokeStyle="#fff";ctx.beginPath();ctx.moveTo(cursorX,top);ctx.lineTo(cursorX,height-bottom);ctx.stroke();
  ctx.fillStyle="#aebdca";ctx.fillText("0 ms",left,height-5);ctx.fillText(playback.duration_ms+" ms",Math.max(left,width-55),height-5);
}
function drawPopulation() {
  const canvas=$("population"), dpr=devicePixelRatio||1, width=Math.max(1,canvas.clientWidth), height=Math.max(1,canvas.clientHeight);
  canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);const ctx=canvas.getContext("2d");ctx.scale(dpr,dpr);ctx.fillStyle="#142430";ctx.fillRect(0,0,width,height);
  if(!playback)return;
  const binWidth=Number($("bin-width").value), counts=new Array(Math.ceil(playback.duration_ms/binWidth)).fill(0), rows=new Set(playbackRows);
  for(const [id,steps] of spikeByNeuron) if(rows.has(id)) for(const step of steps) counts[Math.min(counts.length-1,Math.floor((step*playback.dt_ms-1e-9)/binWidth))]++;
  const peak=Math.max(1,...counts);ctx.fillStyle="#65d4b7";
  counts.forEach((count,i)=>{const bar=width/counts.length;ctx.fillRect(i*bar,height-count/peak*(height-4),Math.max(1,bar-1),count/peak*(height-4));});
}
function updateActivityInspector() {
  if(!playback || selectedNode===null)return;
  const steps=spikeByNeuron.get(selectedNode)||[];
  $("activity-inspector").textContent="Body ID "+selectedNode+" · recorded for output spikes · "+steps.length+" spikes\nTimesteps: "+(steps.join(", ")||"none")+"\nTimes (ms): "+(steps.map(step=>(step*playback.dt_ms).toFixed(1)).join(", ")||"none");
  drawTrace();
}
function drawTrace() {
  const canvas=$("trace"), trace=playback?.selected_traces.find(t=>t.neuron_id===selectedNode);
  $("trace-note").textContent=trace?"Authoritative selected voltage trace (mV); cursor is simulation time.":"No selected voltage trace recorded for this neuron in this run.";
  const dpr=devicePixelRatio||1,width=Math.max(1,canvas.clientWidth),height=Math.max(1,canvas.clientHeight);canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
  if(!trace)return;const ctx=canvas.getContext("2d");ctx.scale(dpr,dpr);const min=Math.min(...trace.v_mV),max=Math.max(...trace.v_mV),range=Math.max(1,max-min),left=48,right=8,top=8,bottom=22,plotWidth=width-left-right,plotHeight=height-top-bottom;ctx.strokeStyle="#65d4b7";ctx.beginPath();trace.v_mV.forEach((v,i)=>{const x=left+i/Math.max(1,trace.v_mV.length-1)*plotWidth,y=top+(max-v)/range*plotHeight;if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);});ctx.stroke();ctx.strokeStyle="#fff";ctx.beginPath();const x=left+playbackCursor/playback.duration_ms*plotWidth;ctx.moveTo(x,top);ctx.lineTo(x,height-bottom);ctx.stroke();ctx.font="10px system-ui";ctx.fillStyle="#aebdca";ctx.fillText(max.toFixed(1)+" mV",2,top+8);ctx.fillText(min.toFixed(1)+" mV",2,height-bottom);ctx.fillText("0 ms",left,height-4);ctx.fillText(playback.duration_ms+" ms",Math.max(left,width-55),height-4);
}
$("playback-cursor").addEventListener("input",e=>setPlaybackCursor(Number(e.target.value)));
$("playback-play").onclick=()=>{if(!playback||reducedMotion.matches||playbackFrame!==null)return;if(playbackCursor>=playback.duration_ms)setPlaybackCursor(0);playbackFrame=requestAnimationFrame(tickPlayback);};
$("playback-pause").onclick=stopPlayback;
$("playback-restart").onclick=()=>{stopPlayback();setPlaybackCursor(0);};
$("playback-back").onclick=()=>setPlaybackCursor(playbackCursor-(playback?.dt_ms||0));
$("playback-forward").onclick=()=>setPlaybackCursor(playbackCursor+(playback?.dt_ms||0));
$("bin-width").onchange=drawPopulation;
$("raster").addEventListener("click",e=>{if(!playback||!playbackRows.length)return;const box=e.target.getBoundingClientRect(),i=Math.floor(((e.clientY-box.top)-14)/(box.height-38)*playbackRows.length);if(i>=0&&i<playbackRows.length)selectNode(playbackRows[i]);});
reducedMotion.addEventListener("change",()=>{if(reducedMotion.matches)stopPlayback();$("playback-play").disabled=reducedMotion.matches;});
$("playback-play").disabled=reducedMotion.matches;
