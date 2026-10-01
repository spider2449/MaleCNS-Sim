"use strict";
const token = new URLSearchParams(location.hash.slice(1)).get("token") || "";
if (location.hash) window.history.replaceState(null, "", location.pathname + location.search);
const $ = id => document.getElementById(id);
let validSelection = null;
let timer = null;
function selection() { return {dataset_key:"male-cns-v1", side:$("side").value, frequency_hz:Number($("frequency").value), mode:$("mode").value, backend:$("backend").value, seed:Number($("seed").value)}; }
async function api(path, body) {
  const headers = {"X-Local-Session":token};
  const response = await fetch(path, body === undefined ? {headers} : {method:"POST", headers:{...headers,"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const data = await response.json();
  if (response.status === 403 && data.error?.message === "local session required") throw new Error("Local session expired. Reopen the URL printed by malecns-workbench.");
  if (!response.ok) throw new Error(data.error?.code + ": " + data.error?.message);
  return data;
}
function error(message) { $("error").textContent = message; }
async function boot() {
  try {
    if (!token) throw new Error("Local session expired. Reopen the URL printed by malecns-workbench.");
    const status = await api("/api/status"); $("status").textContent = status.status;
    const catalog = await api("/api/datasets");
    const dataset = catalog.datasets[0];
    $("dataset").textContent = dataset.display_name + " · " + dataset.status + " · manifest " + dataset.manifest_digest;
    if (!dataset.available) { error("DATASET_UNAVAILABLE: registered local Feather files are absent."); return; }
    const options = await api("/api/experiment/options");
    $("frequency").replaceChildren(...options.frequencies_hz.map(f => { const o=document.createElement("option");o.value=f;o.textContent=f+" Hz";if(f===100)o.selected=true;return o; }));
    $("backend").querySelector('[value="cuda"]').disabled = !options.cuda_available;
    if (!options.cuda_available) $("backend").querySelector('[value="cuda"]').textContent = "CUDA unavailable";
    await loadRunHistory();
  } catch (e) { $("status").textContent = "Session unavailable"; error(e.message); }
}
for (const id of ["side","frequency","mode","backend","seed"]) $(id).addEventListener("change", () => { validSelection=null;$("run").disabled=true;$("preview").textContent=""; });
$("validate").addEventListener("click", async () => {
  error("");
  try { const selected=selection(); const response=await api("/api/experiments/validate",selected);validSelection=selected;$("run").disabled=false;$("preview").textContent=JSON.stringify({spec_digest:response.spec_digest,...response.spec},null,2);$("result").textContent="Validated by A002. Ready to run."; }
  catch(e) { validSelection=null;$("run").disabled=true;error(e.message); }
});
$("run").addEventListener("click",async()=>{ if(!validSelection)return;error("");$("run").disabled=true;try{const response=await api("/api/runs",validSelection);watch(response.job_id);}catch(e){error(e.message);$("run").disabled=false;} });
async function loadRunHistory(){const data=await api("/api/runs");$("history").replaceChildren(...data.runs.map(r=>{const b=document.createElement("button");b.textContent=r.state+" · "+r.job_id.slice(0,8);b.onclick=()=>watch(r.job_id);return b;}));}
function watch(job){if(timer)clearInterval(timer);const update=async()=>{try{const [run,events]=await Promise.all([api("/api/runs/"+job),api("/api/runs/"+job+"/events")]);$("identity").textContent="Job: "+job+"\nA002 run identity: "+(run.run_id||"pending")+"\nSpec digest: "+run.spec_digest+"\nState: "+run.state;$("events").replaceChildren(...events.events.map(e=>{const row=document.createElement("div");row.textContent=e.timestamp+" · "+e.event_type+" · "+e.phase+" · "+JSON.stringify(e.payload);return row;}));if(run.error)error(run.error.code+": "+run.error.message);if(["COMPLETED","FAILED","CANCELLED"].includes(run.state)){clearInterval(timer);timer=null;await loadRunHistory();if(run.state==="COMPLETED"){const result=await api("/api/runs/"+job+"/result");const trial=result.trials[0];$("result").textContent="MODEL SIMULATION RESULT\nTarget MN9_"+(run.spec.stimulus.side==="L"?"R":"L")+" ("+run.spec.target.neuron_id+")\nSpike count: "+trial.target_spikes+"\nFiring rate: "+trial.target_rate_hz+" Hz\nResult digest: "+result.authoritative_digest+"\nEngine: "+result.provenance.engine_version+"\nDataset: "+result.provenance.dataset.manifest_digest;$("flow").textContent=result.stimulus_summary.member_count+" frozen sugar neurons → "+result.provenance.prepared_neuron_count+" prepared neurons / "+result.provenance.prepared_edge_count+" edges → MN9_"+(run.spec.stimulus.side==="L"?"R":"L")+" · "+trial.target_spikes+" emitted target spikes";$("export").hidden=false;$("export").href="/api/runs/"+job+"/export";$("export").download="malecns-result-"+job+".json";}else $("result").textContent=run.state+" · "+(run.error?.message||"See event timeline.");}else $("result").textContent="Executing: "+run.state+". No estimated percentage is available.";}catch(e){error(e.message);}};update();timer=setInterval(update,1000);}
$("export").addEventListener("click", async event => {
  event.preventDefault();
  try {
    const data = await api($("export").getAttribute("href"));
    const url = URL.createObjectURL(new Blob([JSON.stringify(data)], {type:"application/json"}));
    const link = document.createElement("a");
    link.href = url;
    link.download = $("export").download;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (e) { error(e.message); }
});
boot();
