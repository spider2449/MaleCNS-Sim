"""Synthetic browser-state regressions; no scientific engine runs."""
import shutil
import subprocess
from pathlib import Path


def test_visible_run_transitions():
    node = shutil.which("node")
    assert node, "Node is required for browser presentation regressions"
    static = Path(__file__).parents[1] / "src/malecns_sim/application/static"
    script = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const elements = new Map();
function $(id) {
 if (!elements.has(id)) elements.set(id,{textContent:'',hidden:true,disabled:false,value:'',dataset:{},classList:{toggle(){}},selectedOptions:[]});
 return elements.get(id);
}
let now = 100000;
const context = vm.createContext({$, Date, setInterval(){}, validSelection:{}, activeJob:null, api:async()=>({runs:[]}), error(){}, loadRunHistory:async()=>{}});
vm.runInContext(fs.readFileSync(process.argv[1]+'/run-status.js','utf8'),context);
function run(code){return vm.runInContext(code,context);}
run('acceptRun({job_id:"b4c124cd1234",spec_digest:"digest"},"none")');
assert.equal($('run').disabled,true); assert.match($('run').textContent,/Running/);
assert.match($('run-heading').textContent,/ACTIVE.*BASELINE/);
assert.match($('run-job').textContent,/b4c124cd/);
assert.equal($('compare-create-intervention').disabled,true);
for(const [state,label] of Object.entries({VALIDATING:'Validating experiment',LOADING_DATA:'Loading dataset',PREPARING_NETWORK:'Preparing simulation network',RUNNING:'Running simulation',FINALIZING:'Finalizing result'})){
 run(`executingRun.state=${JSON.stringify(state)}; renderRunStatus()`);
 assert.match($('run-phase').textContent,new RegExp(label));
 assert.equal($('execution-overlay').hidden,false);
 assert(!/\d+%/.test($('run-status').textContent+$('run-phase').textContent));
}
run('executingRun.startedAt=1000; executingRun.state="RUNNING"');
assert.equal(run('runPresentation(executingRun,278000).elapsed'),'04:37');
run('activeJob="previous123"; renderRunStatus()');
assert.match($('previous-result').textContent,/Viewing previous result.*previous/);
assert.match($('execution-overlay').textContent,/Job b4c124cd.*Viewing previous result/);
run('executingRun.mode="outgoing_silence"; renderRunStatus()');
assert.match($('compare-active').textContent,/INTERVENTION running/);
run('executingRun.trialText="Completed trials 1 / 2"; renderRunStatus()');
assert.equal($('run-summary').textContent,'Completed trials 1 / 2');
for(const [state,label] of Object.entries({COMPLETED:'Run completed',FAILED:'Run failed',CANCELLED:'Run cancelled'})){
 run(`executingRun.state=${JSON.stringify(state)}; executingRun.endedAt=278000; renderRunStatus()`);
 assert.equal($('run').disabled,false);assert.equal($('run-status').hidden,false);
 assert.match($('run-phase').textContent,new RegExp(label));
 assert.equal($('execution-overlay').hidden,true);
 assert.equal(run('runPresentation(executingRun,999999).elapsed'),'04:37');
}
run('executingRun.state="FAILED"; executingRun.error={code:"SIMULATION_FAILED",message:"local run failed"}; renderRunStatus()');
assert.equal($('run-summary').textContent,'SIMULATION_FAILED: local run failed');
assert.match($('active-identity').textContent,/A002 run identity: pending.*?/);
run('executingRun=null;submittingRun=true;updateRunControls()');assert.equal($('run').disabled,true);
assert.equal($('run').textContent,'Submitting...');
const css=fs.readFileSync(process.argv[1]+'/style.css','utf8');
assert.match(css,/@media\(prefers-reduced-motion:reduce\).*animation:none/);
assert.match(css,/#run-status\{position:sticky/);
const app=fs.readFileSync(process.argv[1]+'/app.js','utf8');
assert.match(app,/if\(!validSelection\|\|runBusy\(\)\)return/);
assert.match(app,/acceptRun\(response,validSelection.mode\);watch/);
assert.match(app,/ACTIVE - /);
(async()=>{
 run('executingRun=null;submittingRun=false;activeJob=null');
 let resolveRequest, requests=0;
 context.api=()=>{requests++;return new Promise(resolve=>{resolveRequest=resolve;});};
 context.error=()=>{};context.watch=()=>{};
 let click;
 $('run').addEventListener=(event,handler)=>{click=handler;};
 const handler=app.split('\n').find(line=>line.startsWith('$("run").addEventListener'));
 run(handler);
 const request=click(); assert.equal($('run').disabled,true);
 await click();assert.equal(requests,1);
 resolveRequest({job_id:'accepted123',spec_digest:'accepted-digest'});await request;
 assert.match($('run-heading').textContent,/ACTIVE/);assert.match($('run-job').textContent,/accepted/);
 const backend={job_id:'accepted123',state:'PREPARING_NETWORK',run_id:'real-identity',spec_digest:'accepted-digest',spec:{intervention:{kind:'none'}}};
 context.api=async(path)=>path==='/api/runs'?{runs:[backend]}:path.endsWith('/events')?{events:[{timestamp:'2026-10-02T00:00:00Z',payload:{}},{payload:{completed_trials:1,total_trials:2}}]}:backend;
 await run('pollRunStatus()');
 assert.match($('run-phase').textContent,/Preparing simulation network/);
 assert.match($('active-identity').textContent,/real-identity/);
 assert.equal($('run-summary').textContent,'Completed trials 1 / 2');
 backend.state='CANCELLED';await run('pollRunStatus()');
 assert.equal($('run').disabled,false);assert.match($('run-phase').textContent,/Run cancelled/);
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
    result = subprocess.run([node, "-e", script, str(static)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
