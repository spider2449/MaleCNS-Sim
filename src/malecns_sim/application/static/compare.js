"use strict";
let comparison = null, pairedPlayback = null, compareCursor = 0, compareFrame = null, compareStamp = null;
let compareGeneration = 0;
const compareMaps = [new Map(), new Map()];

async function refreshCompareRuns() {
  const data = await api("/api/runs");
  const fill = (id, mode) => {
    const picker = $(id), previous = picker.value;
    picker.replaceChildren(...data.runs.filter(r => r.state === "COMPLETED" && r.mode === mode).map(r => {
      const option = document.createElement("option"); option.value = r.job_id;
      option.textContent = r.side + " · " + r.run_id.slice(0, 12) + " · " + r.job_id.slice(0, 8);
      return option;
    }));
    if ([...picker.options].some(o => o.value === previous)) picker.value = previous;
  };
  fill("compare-baseline", "none"); fill("compare-intervention", "outgoing_silence");
  await refreshCompareCandidates();
}
async function refreshCompareCandidates() {
  const baseline = $("compare-baseline").value;
  if (!baseline) {updateRunControls();return;}
  const data = await api("/api/comparisons/candidates?baseline_job_id=" + encodeURIComponent(baseline));
  const reasons = new Map(data.candidates.map(c => [c.job_id,c]));
  for (const option of $("compare-intervention").options) {
    const candidate = reasons.get(option.value);
    option.disabled = !candidate?.eligible;
    option.textContent = option.textContent.split(" · ")[0] + " · " + (candidate?.run_id || "pending").slice(0,12) + " · " + option.value.slice(0,8) + (candidate?.eligible ? " · paired" : " · " + (candidate?.reason || "INELIGIBLE"));
  }
  if ($("compare-intervention").selectedOptions[0]?.disabled) {
    const first = [...$("compare-intervention").options].find(o => !o.disabled);
    if (first) $("compare-intervention").value = first.value;
  }
  updateRunControls();
}
function clearComparison() {
  compareGeneration++;
  if (compareFrame !== null) cancelAnimationFrame(compareFrame);
  compareFrame = null; compareStamp = null; compareCursor = 0; comparison = null; pairedPlayback = null;
  compareMaps.forEach(map => map.clear()); $("compare-ready").hidden = true;
}
function compareIdentity(value) {
  return "Run: " + value.run_id + "\nSpec: " + value.spec_digest + "\nResult: " + value.result_digest +
    "\nDataset manifest: " + value.dataset.manifest_digest + "\nBase graph: " + value.base_graph_fingerprint +
    "\nPrepared graph: " + value.prepared_graph_fingerprint + "\nRealized schedule: " + value.schedule_fingerprint + "\nBackend: " + value.backend;
}
function compareMetric(name, metric) {
  return name + "\nBaseline: " + metric.baseline + "  Intervention: " + metric.intervention +
    "  Delta: " + metric.absolute_delta + "  Relative: " + (metric.relative_delta === null ? "unavailable — " + metric.warning : (metric.relative_delta * 100).toFixed(2) + "%");
}
async function loadComparison() {
  clearComparison(); $("compare-status").textContent = "Checking backend pairing…";
  const generation = compareGeneration;
  const started = performance.now();
  try {
    const baseline = $("compare-baseline").value, intervention = $("compare-intervention").value;
    if (!baseline || !intervention) throw new Error("Select completed baseline and intervention runs.");
    const result = await api("/api/comparisons", {baseline_job_id:baseline, intervention_job_id:intervention});
    if (generation !== compareGeneration) return;
    const mode = $("view-mode").value, cap = $("node-cap").value;
    const playback = await api("/api/comparisons/" + result.comparison_id + "/playback?mode=" + mode + "&cap=" + cap);
    if (generation !== compareGeneration) return;
    const loaded = performance.now();
    if (playback.comparison_id !== result.comparison_id || playback.baseline.run_id !== result.baseline.run_id || playback.intervention.run_id !== result.intervention.run_id ||
        playback.baseline.authoritative_result_digest !== result.baseline.result_digest || playback.intervention.authoritative_result_digest !== result.intervention.result_digest) throw new Error("Comparison/playback identity mismatch");
    const timings = presentComparison(result, playback);
    $("compare-status").textContent += "\nA006 certification measurement (this browser): pair request and dual playback load " + (loaded-started).toFixed(1) + " ms; dual raster indexing " + timings.indexing.toFixed(1) + " ms; union viewport preparation and initial render " + timings.render.toFixed(1) + " ms.";
  } catch (error) {
    if (generation === compareGeneration) throw error;
  }
}
function presentComparison(result, playback) {
  const started = performance.now();
  comparison = result; pairedPlayback = playback;
  [playback.baseline, playback.intervention].forEach((run, index) => {
    for (const event of run.sparse_spikes) {
      if (!Number.isInteger(event.timestep) || event.timestep < 1 || event.timestep > Math.round(run.duration_ms/run.dt_ms)) throw new Error("Invalid recorded spike timestep");
      if (!compareMaps[index].has(event.neuron_id)) compareMaps[index].set(event.neuron_id, []);
      compareMaps[index].get(event.neuron_id).push(event.timestep);
    }
  });
  const indexed = performance.now();
  $("compare-a-identity").textContent = compareIdentity(result.baseline) + "\nIntervention: none";
  $("compare-b-identity").textContent = compareIdentity(result.intervention) + "\nIntervention: " + result.intervention_state.kind + " · body " + result.intervention_state.neuron_ids.join(", ");
  $("compare-target").textContent = "Target: " + result.target.neuron_id + "\n" + compareMetric("Spike count", result.target.spike_count) + "\n" + compareMetric("Firing rate (Hz)", result.target.firing_rate_hz);
  $("compare-status").textContent = "PAIRED · " + result.comparison_id + " · digest " + result.authoritative_digest + " · no biological causal verdict";
  $("compare-filter").textContent = "Shared union display: " + playback.union_node_ids.length + " neurons · baseline " + playback.baseline_view.rendered_node_count + "/" + playback.baseline_view.total_candidate_nodes + " candidates · intervention " + playback.intervention_view.rendered_node_count + "/" + playback.intervention_view.total_candidate_nodes + " candidates. Truncated: " + (playback.baseline_view.truncated || playback.intervention_view.truncated ? "yes" : "no") + ". Display filter ≠ biological pathway.";
  $("compare-neuron").replaceChildren(...playback.raster_rows.map(id => { const option = document.createElement("option"); option.value = id; option.textContent = String(id); return option; }));
  $("compare-cursor").max = playback.baseline.duration_ms; $("compare-cursor").step = playback.baseline.dt_ms;
  $("compare-export").href = "/api/comparisons/" + result.comparison_id + "/export";
  $("compare-export").download = "malecns-comparison-" + result.comparison_id + ".json";
  const inspected = performance.now();
  $("compare-ready").hidden = false; setCompareCursor(0);
  return {indexing:indexed-started, inspector:inspected-indexed, render:performance.now()-inspected};

}

function compareActive(index, id) {
  if (!pairedPlayback) return false;
  const run = index ? pairedPlayback.intervention : pairedPlayback.baseline;
  const low = Math.max(0, compareCursor - 1), high = Math.min(run.duration_ms, compareCursor + 1);
  return (compareMaps[index].get(id) || []).some(step => step * run.dt_ms >= low - 1e-9 && step * run.dt_ms <= high + 1e-9);
}
function drawCompareRaster(index) {
  const canvas = $(index ? "compare-raster-b" : "compare-raster-a"), run = index ? pairedPlayback.intervention : pairedPlayback.baseline;
  const rows = pairedPlayback.raster_rows, width = canvas.clientWidth, height = Math.max(420, rows.length * 12 + 38), dpr = devicePixelRatio || 1;
  canvas.style.height = height + "px"; canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
  const ctx = canvas.getContext("2d"); ctx.scale(dpr,dpr); ctx.fillStyle = "#142430"; ctx.fillRect(0,0,width,height);
  const left = 72, right = 12, top = 14, bottom = 24, rowHeight = (height-top-bottom)/rows.length, span = width-left-right;
  ctx.font = "10px system-ui";
  rows.forEach((id,i) => {
    const y = top+(i+.5)*rowHeight;
    if (id === Number($("compare-neuron").value)) { ctx.fillStyle = "#31495d"; ctx.fillRect(0,top+i*rowHeight,width,rowHeight); }
    ctx.fillStyle = "#aebdca"; if (rowHeight >= 7) ctx.fillText(String(id),3,y+3);
    ctx.fillStyle = index ? "#d99bfa" : "#65d4b7";
    for (const step of compareMaps[index].get(id) || []) ctx.fillRect(left+step*run.dt_ms/run.duration_ms*span,y-Math.max(1,rowHeight*.35),1,Math.max(2,rowHeight*.7));
  });
  const x = left+compareCursor/run.duration_ms*span; ctx.strokeStyle = "#fff"; ctx.beginPath(); ctx.moveTo(x,top); ctx.lineTo(x,height-bottom); ctx.stroke();
  ctx.fillStyle = "#aebdca"; ctx.fillText("0 ms",left,height-5); ctx.fillText(run.duration_ms+" ms",Math.max(left,width-55),height-5);
}
function compareLayout() {
  const rows = pairedPlayback.raster_rows, positions = new Map();
  rows.forEach((id,i) => { const angle = 2*Math.PI*i/Math.max(1,rows.length); positions.set(id,{x:Math.cos(angle)*135,y:Math.sin(angle)*135}); });
  return positions;
}
function drawCompareGraph(index, positions) {
  const canvas = $(index ? "compare-graph-b" : "compare-graph-a"), view = index ? pairedPlayback.intervention_view : pairedPlayback.baseline_view;
  const width = canvas.clientWidth, height = canvas.clientHeight, dpr = devicePixelRatio || 1;
  canvas.width = Math.round(width*dpr); canvas.height = Math.round(height*dpr);
  const ctx = canvas.getContext("2d"); ctx.scale(dpr,dpr); ctx.fillStyle = "#142430"; ctx.fillRect(0,0,width,height);
  ctx.translate(width/2,height/2); const scale = Math.min(width/360,height/330); ctx.scale(scale,scale);
  const present = new Set(view.nodes.map(n => n.neuron_id));
  for (const edge of view.edges) { const a=positions.get(edge.source), b=positions.get(edge.target); if(!a||!b)continue;
    ctx.strokeStyle = index && edge.source === comparison.intervention_state.neuron_ids[0] ? "#a56b6b" : "#4b7284";
    ctx.setLineDash(index && edge.source === comparison.intervention_state.neuron_ids[0] ? [4,4] : []);
    ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke(); }
  ctx.setLineDash([]);
  for (const id of pairedPlayback.union_node_ids) { const p=positions.get(id); ctx.beginPath();ctx.arc(p.x,p.y,id===comparison.target.neuron_id?6:3,0,2*Math.PI);
    ctx.fillStyle = present.has(id) ? (index ? "#d99bfa" : "#65d4b7") : "#687887"; ctx.fill();
    if(compareActive(index,id)){ctx.beginPath();ctx.arc(p.x,p.y,9,0,2*Math.PI);ctx.strokeStyle="#f4a261";ctx.lineWidth=2;ctx.stroke();}
    if(id===Number($("compare-neuron").value)){ctx.beginPath();ctx.arc(p.x,p.y,12,0,2*Math.PI);ctx.strokeStyle="#fff";ctx.lineWidth=2;ctx.stroke();} }
}
function drawCompareTimeline(index) {
  const canvas = $(index ? "compare-timeline-b" : "compare-timeline-a"), run = index ? pairedPlayback.intervention : pairedPlayback.baseline;
  const width=canvas.clientWidth,height=canvas.clientHeight,dpr=devicePixelRatio||1;
  canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
  const ctx=canvas.getContext("2d");ctx.scale(dpr,dpr);ctx.fillStyle="#142430";ctx.fillRect(0,0,width,height);
  const count=Math.ceil(run.duration_ms/2),bins=new Array(count).fill(0),displayed=new Set((index ? pairedPlayback.intervention_view : pairedPlayback.baseline_view).nodes.map(n=>n.neuron_id));
  for(const [id,steps] of compareMaps[index]) if(displayed.has(id)) for(const step of steps) bins[Math.min(count-1,Math.floor((step*run.dt_ms-1e-9)/2))]++;
  const peak=Math.max(1,...bins);ctx.fillStyle=index?"#d99bfa":"#65d4b7";
  bins.forEach((value,i)=>{const bar=width/count;ctx.fillRect(i*bar,height-value/peak*(height-5),Math.max(1,bar-1),value/peak*(height-5));});
  const x=compareCursor/run.duration_ms*width;ctx.strokeStyle="#fff";ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,height);ctx.stroke();
}
function updateCompareNeuron() {
  if (!pairedPlayback) return;
  const id = Number($("compare-neuron").value);
  const detail = ["Selected body ID " + id];
  [pairedPlayback.baseline, pairedPlayback.intervention].forEach((run,index) => {
    const view = index ? pairedPlayback.intervention_view : pairedPlayback.baseline_view;
    const present = view.nodes.some(n => n.neuron_id === id);
    const steps = compareMaps[index].get(id) || [];
    const trace = run.selected_traces.some(t => t.neuron_id === id);
    detail.push((index ? "INTERVENTION" : "BASELINE") + ": " + (present ? "displayed" : "not present in this display filter") +
      " · recorded: yes · spike count: " + steps.length + " · firing rate: " + (steps.length*1000/run.duration_ms) + " Hz" +
      " · times (ms): " + (steps.map(s => (s*run.dt_ms).toFixed(1)).join(", ") || "none") + " · trace available: " + (trace ? "yes" : "no"));
  });
  $("compare-neuron-detail").textContent = detail.join("\n");
}
function setCompareCursor(value) {
  if (!pairedPlayback) return;
  const run = pairedPlayback.baseline;
  compareCursor = Math.max(0,Math.min(run.duration_ms,Math.round(value/run.dt_ms)*run.dt_ms));
  compareCursor = Number(compareCursor.toFixed(10)); $("compare-cursor").value = compareCursor;
  $("compare-time").textContent = compareCursor.toFixed(1) + " ms · shared inclusive ±1 ms display window";
  const positions = compareLayout(); [0,1].forEach(i => {drawCompareRaster(i);drawCompareTimeline(i);drawCompareGraph(i,positions);}); updateCompareNeuron();
}
function tickCompare(stamp) {
  if(compareStamp !== null) setCompareCursor(compareCursor+(stamp-compareStamp)*Number($("compare-speed").value));
  compareStamp=stamp;
  if(compareCursor >= pairedPlayback.baseline.duration_ms){compareFrame=null;compareStamp=null;return;}
  compareFrame=requestAnimationFrame(tickCompare);
}
$("compare-load").onclick = async () => {try {await loadComparison();} catch(e) {clearComparison();$("compare-status").textContent=e.message;}};
$("compare-baseline").onchange = () => {clearComparison();refreshCompareCandidates().catch(e=>{$("compare-status").textContent=e.message;});};
$("compare-intervention").onchange = clearComparison;
$("compare-create-intervention").onclick = async () => {if(runBusy())return;submittingRun=true;updateRunControls();try {const id=$("compare-baseline").value;if(!id)throw new Error("Select a completed baseline.");const created=await api("/api/runs/paired-intervention",{baseline_job_id:id});acceptRun(created,"outgoing_silence");watch(created.job_id);$("compare-status").textContent="Paired intervention running · "+created.job_id;const poll=setInterval(async()=>{try{const run=await api("/api/runs/"+created.job_id);if(run.state==="COMPLETED"){clearInterval(poll);await refreshCompareRuns();$("compare-intervention").value=created.job_id;await loadComparison();}else if(["FAILED","CANCELLED"].includes(run.state)){clearInterval(poll);$("compare-status").textContent="Intervention run failed.";}}catch(e){clearInterval(poll);$("compare-status").textContent=e.message;}},1000);}catch(e){submittingRun=false;updateRunControls();$("compare-status").textContent=e.message;}};
$("compare-cursor").oninput=e=>setCompareCursor(Number(e.target.value));
$("compare-neuron").onchange=()=>setCompareCursor(compareCursor);
$("compare-play").onclick=()=>{if(!pairedPlayback||compareFrame!==null||reducedMotion.matches)return;if(compareCursor>=pairedPlayback.baseline.duration_ms)setCompareCursor(0);compareFrame=requestAnimationFrame(tickCompare);};
$("compare-pause").onclick=()=>{if(compareFrame!==null)cancelAnimationFrame(compareFrame);compareFrame=null;compareStamp=null;};
$("compare-restart").onclick=()=>{$("compare-pause").click();setCompareCursor(0);};
$("compare-export").onclick=async e=>{e.preventDefault();try{const response=await fetch(e.target.href,{headers:{"X-Local-Session":token}});if(!response.ok)throw new Error("Comparison export failed");const blob=await response.blob();const url=URL.createObjectURL(blob);const link=document.createElement("a");link.href=url;link.download=e.target.download;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){$("compare-status").textContent=error.message;}};
window.addEventListener("resize",()=>{if(pairedPlayback)setCompareCursor(compareCursor);});
refreshCompareRuns().catch(e=>{$("compare-status").textContent=e.message;});
