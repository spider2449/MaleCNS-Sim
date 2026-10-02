"use strict";
const urlToken = new URLSearchParams(location.hash.slice(1)).get("token");
let token = urlToken || "";
let sessionStored = false;
try {
  if (urlToken) sessionStorage.setItem("malecns-local-session", urlToken);
  else token = sessionStorage.getItem("malecns-local-session") || "";
  sessionStored = Boolean(token);
} catch (_) {
  // Keep the URL token usable when browser storage is unavailable.
}
if (location.hash && sessionStored) window.history.replaceState(null, "", location.pathname + location.search);
window.addEventListener("hashchange", () => {
  // Reload so every component uses the newly supplied session token.
  if (new URLSearchParams(location.hash.slice(1)).get("token")) location.reload();
});
const $ = id => document.getElementById(id);
let validSelection = null;
let timer = null;
let activeJob = null;
let graphView = null;
let selectedNode = null;
let transform = {x:0,y:0,scale:1};
let dragging = null;
function selection() { return {dataset_key:"male-cns-v1", side:$("side").value, frequency_hz:Number($("frequency").value), mode:$("mode").value, backend:$("backend").value, seed:Number($("seed").value)}; }
async function api(path, body) {
  const headers = {"X-Local-Session":token};
  const response = await fetch(path, body === undefined ? {headers} : {method:"POST", headers:{...headers,"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const data = await response.json();
  if (response.status === 403 && data.error?.message === "local session required") throw new Error((token ? "Local session does not match this server process." : "Local session token is missing.") + (data.error.server_instance_id ? " Server instance: " + data.error.server_instance_id + "." : "") + " Reopen the URL printed by the currently running workbench.");
  if (!response.ok) throw new Error(data.error?.code + ": " + data.error?.message);
  return data;
}
function error(message) { $("error").textContent = message; }
async function boot() {
  try {
    if (!token) throw new Error("Local session token is missing. Reopen the URL printed by the currently running workbench.");
    const status = await api("/api/status"); $("status").textContent = status.status + " ? Server instance: " + status.server_instance_id;
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
  try { const selected=selection(); const response=await api("/api/experiments/validate",selected);validSelection=selected;updateRunControls();$("preview").textContent=JSON.stringify({spec_digest:response.spec_digest,...response.spec},null,2);$("result").textContent="Validated by A002. Ready to run."; }
  catch(e) { validSelection=null;$("run").disabled=true;error(e.message); }
});
$("run").addEventListener("click",async()=>{ if(!validSelection||runBusy())return;submittingRun=true;updateRunControls();error("");$("run").disabled=true;try{const response=await api("/api/runs",validSelection);acceptRun(response,validSelection.mode);watch(response.job_id);}catch(e){submittingRun=false;error(e.message);updateRunControls();} });
async function loadRunHistory(){const data=await api("/api/runs");$("history").replaceChildren(...data.runs.map(r=>{const b=document.createElement("button");b.dataset.state=terminalStates.includes(r.state)?r.state:"ACTIVE";b.textContent=(terminalStates.includes(r.state)?r.state:"ACTIVE - "+r.state)+" · "+r.job_id.slice(0,8);b.onclick=()=>watch(r.job_id);return b;}));if(typeof refreshCompareRuns==="function")await refreshCompareRuns();updateRunControls();}
function watch(job){
  if(timer)clearInterval(timer); activeJob=job; graphView=null; selectedNode=null; resetPlayback(); drawGraph();
  $("result").textContent="Loading run…"; $("identity").textContent="Loading run…"; $("export").hidden=true;
  $("graph-empty").textContent="Preparing simulation graph…";
  const update=async()=>{try{
    const [run,events]=await Promise.all([api("/api/runs/"+job),api("/api/runs/"+job+"/events")]);
    if(activeJob!==job)return;
    $("identity").textContent="Job: "+job+"\nA002 run identity: "+(run.run_id||"pending")+"\nSpec digest: "+run.spec_digest+"\nState: "+run.state;
    $("events").replaceChildren(...events.events.map(e=>{const row=document.createElement("div");row.textContent=e.timestamp+" · "+e.event_type+" · "+e.phase+" · "+JSON.stringify(e.payload);return row;}));
    if(run.error)error(run.error.code+": "+run.error.message);
    if(run.state==="FAILED"||run.state==="CANCELLED"){$("graph-empty").textContent="Run "+run.state.toLowerCase()+"; graph unavailable.";$("playback-state").textContent="No completed playback result.";graphView=null;drawGraph();}
    if(["COMPLETED","FAILED","CANCELLED"].includes(run.state)){
      clearInterval(timer);timer=null;await loadRunHistory();
      if(run.state==="COMPLETED"){
        const result=await api("/api/runs/"+job+"/result");if(activeJob!==job)return;
        const trial=result.trials[0];
        $("result").textContent="MODEL SIMULATION RESULT · "+run.spec.stimulus.side+" sugar · "+run.spec.stimulus.frequency_hz+" Hz → MN9_"+(run.spec.stimulus.side==="L"?"R":"L")+" / "+run.spec.target.neuron_id+" · "+run.spec.backend+" · Target: "+trial.target_spikes+" spikes · "+trial.target_rate_hz+" Hz · "+run.state+" · Authoritative result digest: "+result.authoritative_digest;
        $("export").hidden=false;$("export").href="/api/runs/"+job+"/export";$("export").download="malecns-result-"+job+".json";
      }else $("result").textContent=run.state+" · "+(run.error?.message||"See event timeline.");
    }else $("result").textContent="Executing: "+run.state+". No estimated percentage is available.";
    if(!["FAILED","CANCELLED"].includes(run.state))await loadGraph(job,run);
  }catch(e){error(e.message);}};
  update();timer=setInterval(update,1000);
}
async function loadGraph(job,run){
  const mode=$("view-mode").value,cap=$("node-cap").value;
  try{const view=await api("/api/runs/"+job+"/subgraph?mode="+mode+"&cap="+cap);
    if(activeJob!==job||mode!==$("view-mode").value||cap!==$("node-cap").value)return;
    if(view.spec_digest!==run.spec_digest||view.run_id!==run.run_id)throw new Error("Graph/run identity mismatch");
    if(graphView?.filter_identity===view.filter_identity&&graphView?.run_id===view.run_id&&graphView?._state===run.state)return;
    graphView=view;graphView._state=run.state;selectedNode=null;layoutGraph();fitGraph();renderList();playbackGraphChanged();
    if(run.state==="COMPLETED")await loadPlayback(job,run,view);
    $("identity").textContent+="\nDataset: "+view.dataset_identity+"\nGraph: "+view.graph_fingerprint+"\nDisplay filter: "+view.filter_identity;
    $("filter-label").textContent="Display filter: "+view.filter_definition.rule+" · "+view.filter_definition.mode+" · cap "+cap+" nodes / "+view.filter_definition.edge_cap+" edges";
    $("truncation").textContent="Showing "+view.rendered_node_count+" of "+view.total_candidate_nodes+" candidate neurons; "+view.rendered_edge_count+" of "+view.total_candidate_edges+" induced edges."+(view.truncated?" Display truncated.":"");
    $("graph-empty").textContent=view.nodes.length?"":"No matching displayed nodes.";
  }catch(e){if(!e.message.startsWith("GRAPH_PENDING")){$("graph-empty").textContent="Subgraph unavailable: "+e.message;graphView=null;drawGraph();}}
}
function layoutGraph(){if(!graphView)return;const nodes=graphView.nodes;const groups={stimulus:[],target:[],context:[]};for(const node of nodes){const role=node.roles.includes("target")?"target":node.roles.includes("stimulus")?"stimulus":"context";groups[role].push(node);}for(const [role,list] of Object.entries(groups)){list.sort((a,b)=>a.neuron_id-b.neuron_id);list.forEach((node,i)=>{const angle=2*Math.PI*i/Math.max(1,list.length);const radius=role==="context"?180+Math.floor(i/50)*50:role==="stimulus"?90:0;const center=role==="stimulus"?-240:role==="target"?240:0;node.x=center+radius*Math.cos(angle);node.y=radius*Math.sin(angle);});}}
function fitGraph(){const canvas=$("graph");transform={x:canvas.clientWidth/2,y:canvas.clientHeight/2,scale:Math.min(canvas.clientWidth/1000,canvas.clientHeight/600)};drawGraph();}
function drawGraph(){const canvas=$("graph"),dpr=window.devicePixelRatio||1;canvas.width=Math.max(1,canvas.clientWidth*dpr);canvas.height=Math.max(1,canvas.clientHeight*dpr);const ctx=canvas.getContext("2d");ctx.scale(dpr,dpr);ctx.clearRect(0,0,canvas.clientWidth,canvas.clientHeight);if(!graphView)return;ctx.translate(transform.x,transform.y);ctx.scale(transform.scale,transform.scale);const positions=new Map(graphView.nodes.map(n=>[n.neuron_id,n]));for(const edge of graphView.edges){const a=positions.get(edge.source),b=positions.get(edge.target);if(!a||!b)continue;ctx.strokeStyle=edge.sign==="negative"?"#9b7890":"#4b7284";ctx.lineWidth=Math.min(3,0.5+Math.sqrt(edge.anatomical_weight)/6);ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}const active=activeSpikeSet();for(const node of graphView.nodes){const roles=node.roles;ctx.fillStyle=roles.includes("target")?"#f3c86a":roles.includes("intervention")?"#d99bfa":roles.includes("stimulus")?"#65d4b7":"#83a8ba";ctx.beginPath();ctx.arc(node.x,node.y,roles.includes("target")?10:roles.includes("stimulus")?6:4,0,Math.PI*2);ctx.fill();if(active.has(node.neuron_id)){ctx.strokeStyle="#f4a261";ctx.lineWidth=3;ctx.beginPath();ctx.arc(node.x,node.y,18,0,Math.PI*2);ctx.stroke();}if(node.neuron_id===selectedNode){ctx.strokeStyle="#fff";ctx.lineWidth=3;ctx.beginPath();ctx.arc(node.x,node.y,14,0,Math.PI*2);ctx.stroke();}}}
function selectNode(id){if(!graphView)return;const node=graphView.nodes.find(n=>n.neuron_id===id);if(!node)return;selectedNode=id;const incoming=graphView.edges.filter(e=>e.target===id),outgoing=graphView.edges.filter(e=>e.source===id);const sum=edges=>edges.reduce((a,e)=>a+e.anatomical_weight,0);$("neuron-inspector").textContent="Neuron/body ID: "+id+"\nRole: "+node.roles.join(", ")+"\nType/class: unavailable in prepared projection\nSide: unavailable in prepared projection\nDisplayed incoming: "+incoming.length+" · anatomical weight "+sum(incoming)+"\nDisplayed outgoing: "+outgoing.length+" · anatomical weight "+sum(outgoing)+"\n"+(playback?"Recorded spike count: "+(spikeByNeuron.get(id)?.length||0):node.activity.available?"Recorded spike count: "+node.activity.spike_count:"Activity not recorded for this neuron in this run.");drawGraph();drawRaster();updateActivityInspector();}
function renderList(){const query=$("node-search").value.trim();const nodes=(graphView?.nodes||[]).filter(n=>!query||String(n.neuron_id).includes(query));$("node-list").replaceChildren(...nodes.map(n=>{const b=document.createElement("button");b.textContent=n.neuron_id+" · "+n.roles.join(", ");b.onclick=()=>selectNode(n.neuron_id);return b;}));}
for(const id of ["view-mode","node-cap"])$(id).addEventListener("change",async()=>{graphView=null;drawGraph();if(activeJob){try{const run=await api("/api/runs/"+activeJob);await loadGraph(activeJob,run);}catch(e){error(e.message);}}});
$("node-search").addEventListener("input",renderList);
$("fit").onclick=fitGraph;
function zoom(factor){const canvas=$("graph");transform.x=canvas.clientWidth/2+(transform.x-canvas.clientWidth/2)*factor;transform.y=canvas.clientHeight/2+(transform.y-canvas.clientHeight/2)*factor;transform.scale=Math.max(.05,Math.min(6,transform.scale*factor));drawGraph();}
$("zoom-in").onclick=()=>zoom(1.25);$("zoom-out").onclick=()=>zoom(.8);
$("graph").addEventListener("pointerdown",e=>{dragging={x:e.clientX,y:e.clientY,moved:false};$("graph").setPointerCapture(e.pointerId);});
$("graph").addEventListener("pointermove",e=>{if(!dragging)return;const dx=e.clientX-dragging.x,dy=e.clientY-dragging.y;if(Math.abs(dx)+Math.abs(dy)>2)dragging.moved=true;transform.x+=dx;transform.y+=dy;dragging.x=e.clientX;dragging.y=e.clientY;drawGraph();});
$("graph").addEventListener("pointerup",e=>{if(!dragging)return;const moved=dragging.moved;dragging=null;if(moved||!graphView)return;const box=$("graph").getBoundingClientRect(),x=(e.clientX-box.left-transform.x)/transform.scale,y=(e.clientY-box.top-transform.y)/transform.scale;let nearest=null,distance=15;for(const node of graphView.nodes){const d=Math.hypot(node.x-x,node.y-y);if(d<distance){nearest=node;distance=d;}}if(nearest)selectNode(nearest.neuron_id);});
$("graph").addEventListener("wheel",e=>{e.preventDefault();zoom(e.deltaY<0?1.1:.9);},{passive:false});
window.addEventListener("resize",drawGraph);
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
