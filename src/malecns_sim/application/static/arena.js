"use strict";
const $ = id => document.getElementById(id);
const fragment = new URLSearchParams(location.hash.slice(1));
let token = fragment.get("token") || "";
try {
  if (token) sessionStorage.setItem("malecns-local-session", token);
  else token = sessionStorage.getItem("malecns-local-session") || "";
  if (token && location.hash) history.replaceState(null,"",location.pathname);
} catch {}
window.addEventListener("hashchange",()=>{if(new URLSearchParams(location.hash.slice(1)).get("token")) location.reload();});
let snapshot = null, busy = false, timer = null, epoch = 0;
async function api(body) {
  const response = await fetch("/api/arena", {method:body?"POST":"GET",headers:{"X-Local-Session":token||"","Content-Type":"application/json"},body:body?JSON.stringify(body):undefined});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error.message);
  return data;
}
function schedule() {
  clearTimeout(timer);
  if (snapshot?.running) timer = setTimeout(()=>command("tick"), 20/Number($("speed").value));
}
async function command(name, values={}) {
  if (busy || !snapshot) return;
  busy = true; controls(); clearTimeout(timer); const requestEpoch = ++epoch;
  try {
    const data = await api({command:name,generation:snapshot.generation,revision:snapshot.revision,...values});
    if (requestEpoch !== epoch) return;
    if (data.generation < snapshot.generation || (data.generation===snapshot.generation && data.revision<snapshot.revision)) return;
    snapshot = data; render();
  } catch(error) { $("status").textContent = error.message; try { snapshot=await api(); render(); } catch {} }
  finally { busy=false; controls(); schedule(); }
}
function controls() {
  for (const id of ["run","pause","step","reset","move","silence3","silence4"]) $(id).disabled=busy||!snapshot;
  if (snapshot) { $("run").disabled ||= snapshot.running; $("step").disabled ||= snapshot.running; $("pause").disabled ||= !snapshot.running; }
}
function render() {
  const start=performance.now(), a=snapshot.arena, e=snapshot.latest;
  $("status").textContent=`${snapshot.running?"Running":"Paused"} ? ${a.simulation_ms.toFixed(0)} ms ? ${snapshot.event_count} events`;
  $("sensory").textContent=JSON.stringify({current_preview:snapshot.sensory_preview,last_applied:e?.sensory||null},null,2);
  $("neural").textContent=JSON.stringify(e?{window_ms:e.window_ms,counts:e.readout_counts,v_mV:e.selected_v_mV,g_mV:e.selected_g_mV}:"Step to produce neural evidence",null,2);
  $("action").textContent=JSON.stringify(e?.action||{forward_units_per_s:0,turn_rad_per_s:0},null,2);
  $("state").textContent=JSON.stringify({arena:a,neural_dt_ms:.1,control_interval_ms:20,performance_ms:snapshot.performance},null,2);
  $("spec").textContent=snapshot.session_identity+"\n"+JSON.stringify(snapshot.spec,null,2);
  $("sx").value=a.stimulus_x; $("sy").value=a.stimulus_y;
  for(const id of [3,4]) $("silence"+id).checked=snapshot.silenced.includes(id);
  const c=$("arena"),ctx=c.getContext("2d"),w=c.width,h=c.height;
  ctx.clearRect(0,0,w,h); ctx.strokeStyle="#294254";
  for(let i=0;i<=10;i++){ctx.beginPath();ctx.moveTo(i*w/10,0);ctx.lineTo(i*w/10,h);ctx.moveTo(0,i*h/10);ctx.lineTo(w,i*h/10);ctx.stroke();}
  ctx.strokeStyle="#6a9ca8";ctx.beginPath();snapshot.trail.forEach(([x,y],i)=>i?ctx.lineTo(x*w,y*h):ctx.moveTo(x*w,y*h));ctx.stroke();
  ctx.fillStyle="#ffca68";ctx.beginPath();ctx.arc(a.stimulus_x*w,a.stimulus_y*h,12,0,Math.PI*2);ctx.fill();
  ctx.save();ctx.translate(a.x*w,a.y*h);ctx.rotate(a.heading);ctx.fillStyle="#75caff";ctx.beginPath();ctx.moveTo(20,0);ctx.lineTo(-12,-12);ctx.lineTo(-7,0);ctx.lineTo(-12,12);ctx.closePath();ctx.fill();ctx.restore();
  ctx.fillStyle="#e2eaf3";ctx.font="16px system-ui";ctx.fillText(`Forward ${e?.action.forward_units_per_s.toFixed(3)||"0"} ? Turn ${e?.action.turn_rad_per_s.toFixed(3)||"0"}`,16,26);
  const t=$("timeline"),tc=t.getContext("2d");tc.clearRect(0,0,t.width,t.height);
  snapshot.history.forEach((v,i)=>{for(const [id,color,offset] of [[3,"#75caff",0],[4,"#ffca68",7]]){tc.fillStyle=color;const count=v.readout_counts[id];tc.fillRect(i*18+offset,110-count*15,6,count*15);}});
  window.arenaUIUpdateMs=performance.now()-start; controls();
}
for(const name of ["run","pause","step","reset"]) $(name).onclick=()=>command(name);
$("move").onclick=()=>command("stimulus",{x:Number($("sx").value),y:Number($("sy").value)});
$("arena").onclick=event=>{const r=$("arena").getBoundingClientRect();return command("stimulus",{x:Math.max(0,Math.min(1,(event.clientX-r.left)/r.width)),y:Math.max(0,Math.min(1,(event.clientY-r.top)/r.height))});};
for(const id of [3,4]) $("silence"+id).onchange=()=>command("intervention",{neuron_id:id,silenced:$("silence"+id).checked});
$("speed").onchange=schedule;
$("export").onclick=async event=>{event.preventDefault();try{const r=await fetch("/api/arena/events",{headers:{"X-Local-Session":token||""}});if(!r.ok)throw new Error("Event export unavailable");const blob=new Blob([JSON.stringify(await r.json(),null,2)],{type:"application/json"});const url=URL.createObjectURL(blob);const link=document.createElement("a");link.href=url;link.download="synthetic-arena-events.json";link.click();URL.revokeObjectURL(url);}catch(e){$("status").textContent=e.message;}};
api().then(data=>{snapshot=data;render();schedule();}).catch(error=>{$("status").textContent=error.message+". Open the full startup arena URL with #token.";});
