"use strict";
const terminalStates = ["COMPLETED", "FAILED", "CANCELLED"];
const phaseLabels = {CREATED:"Run accepted; awaiting execution...", VALIDATING:"Validating experiment...", LOADING_DATA:"Loading dataset...", PREPARING_NETWORK:"Preparing simulation network...", RUNNING:"Running simulation...", FINALIZING:"Finalizing result...", COMPLETED:"Run completed", FAILED:"Run failed", CANCELLED:"Run cancelled"};
let executingRun = null, submittingRun = false, statusPollBusy = false;
function runBusy() { return submittingRun || Boolean(executingRun && !terminalStates.includes(executingRun.state)); }
function elapsedLabel(seconds) {
  const value = Math.max(0, Math.floor(seconds));
  return String(Math.floor(value / 60)).padStart(2,"0") + ":" + String(value % 60).padStart(2,"0");
}
function runPresentation(run, now = Date.now()) {
  const active = !terminalStates.includes(run.state);
  const end = active ? now : run.endedAt;
  return {active, label:phaseLabels[run.state] || run.state, role:run.mode === "none" ? "BASELINE" : run.mode === "outgoing_silence" ? "INTERVENTION" : "",
    elapsed:run.startedAt ? elapsedLabel((end - run.startedAt)/1000) : "unavailable"};
}
function updateRunControls() {
  const busy = runBusy();
  $("run").disabled = busy || !validSelection;
  $("run").textContent = submittingRun ? "Submitting..." : busy ? "ACTIVE - Running..." : "Run";
  $("compare-create-intervention").disabled = busy || !$("compare-baseline").value;
  const candidate = $("compare-intervention").selectedOptions[0];
  $("compare-load").disabled = !$("compare-baseline").value || !candidate || candidate.disabled;
  $("run-wait").textContent = busy ? "Waiting for active run to finish." : "";
}
function renderRunStatus() {
  updateRunControls();
  if (!executingRun) return;
  const run = executingRun, view = runPresentation(run);
  $("run-status").hidden = false;
  $("run-status").dataset.state = view.active ? "ACTIVE" : run.state;
  $("run-indicator").classList.toggle("spinning", view.active);
  $("run-heading").textContent = (view.active ? "ACTIVE - RUNNING" : run.state) + " - " + view.role;
  $("run-phase").textContent = view.label + " - " + run.state;
  $("run-job").textContent = "Job " + run.job_id.slice(0,8);
  $("run-elapsed").textContent = "Elapsed wall-clock " + view.elapsed;
  $("run-summary").textContent = run.error ? run.error.code + ": " + run.error.message : run.trialText || "";
  $("active-identity").textContent = (view.active ? "ACTIVE JOB" : run.state + " JOB") + " - " + view.role + "\nJob: " + run.job_id + "\nA002 run identity: " + (run.run_id || "pending") + "\nSpec digest: " + (run.spec_digest || "pending") + "\nState: " + run.state + "\nElapsed wall-clock " + view.elapsed;
  const previous = activeJob && activeJob !== run.job_id;
  const preparing = ["CREATED","VALIDATING","LOADING_DATA","PREPARING_NETWORK"].includes(run.state);
  $("execution-overlay").hidden = !view.active;
  $("execution-overlay").textContent = view.active ? "ACTIVE - " + view.role + " - Job " + run.job_id.slice(0,8) + " - " + view.label + (previous ? " Viewing previous result - Job " + activeJob.slice(0,8) : preparing ? " No completed activity for this job." : "") : "";
  $("previous-result").textContent = view.active && previous ? "Viewing previous result - Job " + activeJob.slice(0,8) + ". New job " + run.job_id.slice(0,8) + " currently active." : "";
  $("compare-active").textContent = view.active ? view.role + " running - " + view.label + " Waiting for active run to finish. Compare requires both completed results." : view.label;
}
function acceptRun(response, mode) {
  executingRun = {...response, state:"CREATED", mode, startedAt:Date.now(), endedAt:null};
  submittingRun = false;
  renderRunStatus();
  loadRunHistory().catch(e => error(e.message));
}
async function pollRunStatus() {
  if (statusPollBusy) return;
  statusPollBusy = true;
  try {
    const history = await api("/api/runs");
    const live = history.runs.find(r => !terminalStates.includes(r.state));
    const job = live?.job_id || (runBusy() ? executingRun?.job_id : null);
    if (!job) return;
    const [run, events] = await Promise.all([api("/api/runs/"+job), api("/api/runs/"+job+"/events")]);
    if (executingRun && executingRun.job_id !== job && !terminalStates.includes(executingRun.state)) return;
    const old = executingRun?.job_id === job ? executingRun : {};
    const first = Date.parse(events.events[0]?.timestamp);
    const counts = [...events.events].reverse().find(e => Number.isInteger(e.payload?.completed_trials) && Number.isInteger(e.payload?.total_trials));
    executingRun = {...old, ...run, mode:run.spec.intervention.kind, startedAt:Number.isFinite(first) ? first : old.startedAt,
      endedAt:terminalStates.includes(run.state) ? old.endedAt || Date.now() : null,
      trialText:counts ? "Completed trials " + counts.payload.completed_trials + " / " + counts.payload.total_trials : ""};
    renderRunStatus();
    if (terminalStates.includes(run.state) && !terminalStates.includes(old.state)) await loadRunHistory();
  } catch(e) { error(e.message); }
  finally { statusPollBusy = false; }
}
setInterval(() => {renderRunStatus(); pollRunStatus();}, 1000);
