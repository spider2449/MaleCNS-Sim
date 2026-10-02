"use strict";
// Every selection owns a generation; obsolete requests cannot publish evidence.
class EvidenceSelection {
  constructor() { this.generation = 0; this.current = null; }
  select(robustnessId, variantId, comparisonId = null) {
    this.current = {generation: ++this.generation, robustnessId, variantId, comparisonId};
    return this.current;
  }
  owns(binding) { return this.current === binding && binding.generation === this.generation; }
}
const robustSelection = new EvidenceSelection();
let robustParentGeneration = 0, robustUpdateGeneration = 0;
let robustParent = null, robustSnapshot = null, robustPoll = null, robustLoading = false;
function exactChange(variant) {
  const definition = variant.definition;
  const labels = {tau_membrane_ms:"Membrane time constant (ms)", tau_synapse_ms:"Synaptic time constant (ms)", synaptic_delay_ms:"Synaptic delay (ms)", v_threshold_mV:"Threshold (mV)", sign_policy_id:"Sign policy"};
  return definition.overrides.map(([key, value]) => {
    if (key === "synaptic_weight_per_anatomical_synapse_mV") {
      const amplitude = variant.schedule_evidence?.input_amplitudes_mv?.[0];
      return "Synaptic weight: " + Number(value).toFixed(3) + " mV · Direct input: " + (amplitude ?? "unavailable until prepared") + (amplitude === undefined ? "" : " mV") + " · derived by ×" + definition.resolved_config.direct_input_weight_factor + " rule";
    }
    return (labels[key] || key) + ": " + value;
  }).join("; ") || "Reference configuration";
}
function robustRelative(metric) {
  if (!metric) return "unavailable";
  return metric.relative_delta === null ? "unavailable · " + metric.warning : (metric.relative_delta * 100).toFixed(2) + "%";
}
function roleProvenance(variant) {
  return ["baseline", "intervention"].map(role => role + ": " + (variant[role]?.provenance || "not executed")).join(" · ");
}
function clearRobustEvidence() {
  robustSelection.select(robustParent, null);
  clearComparison();
  $("compare-status").textContent = "Selected variant evidence unavailable or loading.";
  $("robust-inspector").textContent = "No variant evidence loaded.";
  $("robust-selected").textContent = "Selected variant comparison";
}
async function refreshRobustSweeps() {
  const data = await api("/api/robustness");
  $("robust-picker").replaceChildren(...data.robustness.map(parent => {
    const option = document.createElement("option"); option.value = parent.robustness_id;
    option.textContent = parent.overall_state + " · " + parent.robustness_id.slice(0,12); return option;
  }));
  if (data.robustness.some(parent => parent.robustness_id === robustParent)) $("robust-picker").value = robustParent;
  if (!robustParent && data.robustness.length) await chooseRobustParent($("robust-picker").value);
}
async function chooseRobustParent(id) {
  if (robustPoll) clearInterval(robustPoll);
  robustParentGeneration++;
  robustParent = id || null; robustSnapshot = null; clearRobustEvidence();
  $("robust-rows").replaceChildren(); $("robust-chart").replaceChildren();
  $("robust-synthetic").hidden = true;
  for (const action of ["cancel", "release", "export"]) $("robust-" + action).disabled = true;
  if (!id) return;
  await updateRobustParent(id);
  if (robustParent !== id || ["COMPLETE", "FAILED", "PARTIAL", "CANCELLED"].includes(robustSnapshot?.result.overall_state)) return;
  robustPoll = setInterval(() => updateRobustParent(id).catch(e => { if (robustParent === id) $("robust-status").textContent = e.message; }), 1000);
}
async function updateRobustParent(id) {
  const started = performance.now(), parentGeneration = robustParentGeneration, updateGeneration = ++robustUpdateGeneration;
  const snapshot = await api("/api/robustness/" + id);
  if (robustParent !== id || parentGeneration !== robustParentGeneration || updateGeneration !== robustUpdateGeneration) return;
  if (snapshot.result.robustness_id !== id) throw new Error("Robustness identity mismatch");
  robustSnapshot = snapshot;
  const result = snapshot.result, progress = snapshot.progress;
  const active = !["COMPLETE", "FAILED", "PARTIAL", "CANCELLED"].includes(result.overall_state);
  $("robust-status").textContent = (active ? "ROBUSTNESS SWEEP ACTIVE" : result.overall_state) + "\n" +
    (progress.current_variant || "—") + " · " + (progress.current_phase === "COMPARING" ? "Comparing" : progress.current_role || "—") + " · " + (progress.current_phase || "—") + "\n" +
    progress.completed_variants + " / " + progress.total_variants + " variants complete · Elapsed " + Math.floor(snapshot.elapsed_seconds / 60) + ":" + String(Math.floor(snapshot.elapsed_seconds % 60)).padStart(2,"0");
  $("robust-aggregate").textContent = result.aggregate_rule === "NO_AGGREGATE_RULE" ? "No aggregate robustness verdict requested." : result.aggregate_rule;
  const catalog = await api("/api/datasets");
  if (robustParent !== id || parentGeneration !== robustParentGeneration || updateGeneration !== robustUpdateGeneration) return;
  const synthetic = catalog.datasets.some(d => d.synthetic_review === true && d.manifest_digest === snapshot.spec.base_spec.dataset.manifest_digest);
  $("robust-synthetic").hidden = !synthetic;
  $("robust-cancel").disabled = !active; $("robust-release").disabled = active; $("robust-export").disabled = false;
  const matrixMs = renderRobustMatrix(result);
  const matrixDone = performance.now(); renderRobustChart(result);
  if (synthetic) $("robust-performance").textContent = "A007C synthetic UI measurements - panel load/render " + (performance.now()-started).toFixed(1) + " ms; matrix " + matrixMs.toFixed(1) + " ms; chart " + (performance.now()-matrixDone).toFixed(1) + " ms";
  if (!robustSelection.current?.variantId) {
    const first = result.variants.find(v => v.comparison);
    if (first) await selectRobustVariant(id, first.variant_id);
  }
  if (!active && robustPoll) {clearInterval(robustPoll); robustPoll = null;}
}
function renderRobustMatrix(result) {
  const started = performance.now();
  $("robust-rows").replaceChildren(...result.variants.map(variant => {
    const row = document.createElement("tr"), metric = variant.comparison?.target.spike_count;
    const button = document.createElement("button"); button.textContent = variant.variant_id;
    button.onclick = () => selectRobustVariant(result.robustness_id, variant.variant_id);
    const selected = robustSelection.current?.variantId === variant.variant_id;
    button.setAttribute("aria-pressed", String(selected)); row.dataset.selected = String(selected);
    const first = document.createElement("td"); first.append(button); row.append(first);
    const values = [exactChange(variant), metric?.baseline ?? "unavailable", metric?.intervention ?? "unavailable", metric?.absolute_delta ?? "unavailable", robustRelative(metric), variant.state + (variant.state === "PENDING" && ["PARTIAL", "FAILED", "CANCELLED"].includes(result.overall_state) ? " · not executed" : "") + (variant.error ? " · " + variant.error.code + ": " + variant.error.message : ""), roleProvenance(variant)];
    values.forEach(value => { const cell = document.createElement("td"); cell.textContent = value; row.append(cell); });
    row.onclick = e => {if (e.target !== button) button.click();}; return row;
  }));
  return performance.now()-started;
}
function renderRobustChart(result) {
  const values = result.variants.map(v => v.comparison?.target.spike_count.absolute_delta).filter(Number.isFinite);
  const span = Math.max(1,...values.map(Math.abs));
  $("robust-chart").replaceChildren(...result.variants.map(variant => {
    const mark = document.createElement("button"), value = variant.comparison?.target.spike_count.absolute_delta;
    mark.className = "delta-mark"; mark.setAttribute("aria-pressed", String(robustSelection.current?.variantId === variant.variant_id));
    const title = document.createElement("span"); title.textContent = variant.variant_id + " · " + (Number.isFinite(value) ? value + " spikes" : "unavailable");
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg"); svg.setAttribute("viewBox","0 0 80 120"); svg.setAttribute("aria-hidden","true");
    const line = document.createElementNS(svg.namespaceURI,"line"); for (const [key,val] of Object.entries({x1:0,x2:80,y1:60,y2:60,stroke:"#fff"})) line.setAttribute(key,val); svg.append(line);
    if (Number.isFinite(value)) {
      const rect = document.createElementNS(svg.namespaceURI,"rect"), height = Math.abs(value)/span*48;
      for (const [key,val] of Object.entries({x:22,width:36,y:value>0?60-height:60,height:value===0?2:height,fill:value<0?"#d99bfa":"#65d4b7"})) rect.setAttribute(key,val); svg.append(rect);
    }
    mark.append(title,svg); mark.onclick = () => selectRobustVariant(result.robustness_id,variant.variant_id); return mark;
  }));
}
async function selectRobustVariant(parent, variantId) {
  if (parent !== robustParent || !robustSnapshot) return;
  const expected = robustSnapshot.result.variants.find(v => v.variant_id === variantId);
  if (!expected) return;
  clearRobustEvidence();
  const binding = robustSelection.select(parent,variantId,expected.comparison?.comparison_id || null);
  binding.compareGeneration = compareGeneration;
  renderRobustMatrix(robustSnapshot.result); renderRobustChart(robustSnapshot.result);
  $("robust-selected").textContent = "Selected variant comparison · " + variantId;
  const started = performance.now(), base = "/api/robustness/" + parent + "/variants/" + variantId;
  try {
    const variant = await api(base);
    if (!(robustSelection.owns(binding) && binding.compareGeneration === compareGeneration)) return;
    if (variant.variant_id !== variantId || variant.variant_digest !== expected.variant_digest || variant.comparison?.comparison_id !== expected.comparison?.comparison_id) throw new Error("Variant identity mismatch");
    const inspectorStart = performance.now();
    $("robust-inspector").textContent = JSON.stringify({robustness_id:parent, robustness_result_digest:robustSnapshot.result.authoritative_digest, preset_id:robustSnapshot.result.preset_id, preset_digest:robustSnapshot.result.preset_digest, ...variant, warnings:robustSnapshot.result.warnings}, null, 2) + "\n" + (variant.schedule_evidence ? "Event identities/times matched across variants; prescribed amplitude follows variant configuration." : "Input event schedule comparability evidence unavailable.");
    const inspectorMs = performance.now()-inspectorStart;
    if (!variant.comparison) {$("compare-status").textContent = variant.state + " · comparison/playback/viewport unavailable";return;}
    const requests = {};
    const timedEvidence = async kind => {
      const requested = performance.now();
      const value = await api(base + "/" + kind);
      requests[kind] = performance.now()-requested;
      return value;
    };
    const [result, playback, graph] = await Promise.all([timedEvidence("comparison"),timedEvidence("playback"),timedEvidence("subgraph")]);
    if (!(robustSelection.owns(binding) && binding.compareGeneration === compareGeneration)) return;
    if (result.comparison_id !== binding.comparisonId || result.authoritative_digest !== variant.comparison.authoritative_digest || playback.comparison_id !== binding.comparisonId || graph.variant_digest !== variant.variant_digest) throw new Error("Variant evidence identity mismatch");
    for (const role of ["baseline","intervention"]) {
      if (result[role].run_id !== variant[role].run_id || result[role].result_digest !== variant[role].result_digest || playback[role].run_id !== variant[role].run_id || playback[role].authoritative_result_digest !== variant[role].result_digest || graph[role].run_id !== variant[role].run_id || graph[role].graph_fingerprint !== variant[role].graph_fingerprint || playback[role].graph_fingerprint !== variant[role].graph_fingerprint || playback[role + "_view"].graph_fingerprint !== variant[role].graph_fingerprint || playback[role + "_view"].run_id !== variant[role].run_id) throw new Error("Variant child identity mismatch");
    }
    const loaded = performance.now(); const timings = presentComparison(result, playback);
    $("compare-export").href = "/api/robustness/" + parent + "/export";
    $("compare-export").download = "malecns-robustness-" + parent.slice(0,12) + ".json";
    if (!$("robust-synthetic").hidden) $("robust-performance").textContent += "\nVariant " + variantId + ": comparison load " + requests.comparison.toFixed(1) + " ms; playback load " + requests.playback.toFixed(1) + " ms; viewport load " + requests.subgraph.toFixed(1) + " ms; indexing " + timings.indexing.toFixed(1) + " ms; inspector " + inspectorMs.toFixed(1) + " ms; pair presentation " + timings.inspector.toFixed(1) + " ms; raster/viewport render " + timings.render.toFixed(1) + " ms; total switch " + (performance.now()-started).toFixed(1) + " ms";
  } catch(e) {if ((robustSelection.owns(binding) && binding.compareGeneration === compareGeneration)) {clearComparison(); $("compare-status").textContent = e.message;}}
}
$("robust-picker").onchange = () => chooseRobustParent($("robust-picker").value).catch(e => {$("robust-status").textContent=e.message;});
$("robust-refresh").onclick = () => refreshRobustSweeps().catch(e => {$("robust-status").textContent=e.message;});
$("robust-start").onclick = async () => {
  if (robustLoading) return;
  try {
    if (!validSelection || validSelection.mode !== "none") throw new Error("Validate an eligible Baseline experiment first.");
    if (!confirm("Start 8 variants, up to 16 scientific child runs, executed serially? Exact reusable runs may reduce executions. Aggregate rule: none.")) return;
    robustLoading = true;
    const created = await api("/api/robustness",{selection:validSelection,preset_id:"application-historical-variation-family-v1",variant_ids:["R0","V1","V2","V3","V4","V5","V6","V7"],reuse_policy:"EXACT_REUSE_OR_EXECUTE",aggregate_rule:"NO_AGGREGATE_RULE"});
    await chooseRobustParent(created.robustness_id); await refreshRobustSweeps();
  } catch(e) {$("robust-status").textContent=e.message;} finally {robustLoading=false;}
};
$("robust-cancel").onclick = async () => {const id=robustParent;try {await api("/api/robustness/"+id+"/cancel",{});if(robustParent===id)await updateRobustParent(id);}catch(e){$("robust-status").textContent=e.message;}};
$("robust-release").onclick = async () => {
  const id=robustParent;
  if (!id || !confirm("Releasing removes this session's retained robustness evidence. Release this parent?")) return;
  try {await api("/api/robustness/"+id+"/release",{});if(robustParent===id)await chooseRobustParent(null);await refreshRobustSweeps();}catch(e){$("robust-status").textContent=e.message;}
};
$("robust-export").onclick = async () => {
  const id=robustParent;if(!id)return;
  try {const response=await fetch("/api/robustness/"+id+"/export",{headers:{"X-Local-Session":token}});if(!response.ok)throw new Error("Robustness export failed");const url=URL.createObjectURL(await response.blob());const link=document.createElement("a");link.href=url;link.download="malecns-robustness-"+id.slice(0,12)+".json";link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){$("robust-status").textContent=e.message;}
};
$("compare-back").onclick=()=>{$("compare-pause").click();if(pairedPlayback)setCompareCursor(compareCursor-pairedPlayback.baseline.dt_ms);};
$("compare-forward").onclick=()=>{$("compare-pause").click();if(pairedPlayback)setCompareCursor(compareCursor+pairedPlayback.baseline.dt_ms);};
refreshRobustSweeps().catch(e=>{$("robust-status").textContent=e.message;});
