const fs = require('fs'), vm = require('vm'), assert = require('assert');
const data = JSON.parse(fs.readFileSync(process.argv[2],'utf8')), staticDir=process.argv[3];
class Element {
 constructor(tag='div'){this.tag=tag;this.children=[];this.dataset={};this.attributes={};this.value='';this.hidden=false;this.style={};this.clientWidth=500;this.clientHeight=300;this.textContent='';this.options=[];}
 replaceChildren(...items){this.children=items;this.options=items;}
 append(...items){this.children.push(...items);}
 setAttribute(key,value){this.attributes[key]=String(value);}
 getContext(){return new Proxy({},{get:()=>()=>{}});}
 click(){return this.onclick?.({target:this,preventDefault(){}});}
}
const elements=new Map(), el=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const measurements=[];
let currentApi=()=>new Promise(()=>{}), cancelled=0, clears=0, rendered=[], dialogs=[], frames=0;
const ctx=vm.createContext({console,performance,Map,Set,Math,Number,String,JSON,Promise,document:{createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag)},$:el,api:(...args)=>currentApi(...args),setInterval:()=>1,clearInterval(){},setTimeout(){},cancelAnimationFrame(){cancelled++;},requestAnimationFrame(){frames++;return 1;},window:{addEventListener(){}},devicePixelRatio:1,reducedMotion:{matches:false},updateRunControls(){},token:'private',fetch(){throw Error('unexpected fetch');},confirm:text=>{dialogs.push(text);return false;},validSelection:null,URL});
vm.runInContext(fs.readFileSync(staticDir+'/compare.js','utf8'),ctx);
vm.runInContext(fs.readFileSync(staticDir+'/robustness.js','utf8'),ctx);
const run=code=>vm.runInContext(code,ctx);
ctx.fixture=data;ctx.clearCount=()=>clears++;
const nativePresent=ctx.presentComparison;
ctx.presentComparison=(result,playback)=>{const timings=nativePresent(result,playback);rendered.push(result.comparison_id);return timings;};
function route(path){
 if(path==='/api/datasets')return {datasets:[{synthetic_review:true,manifest_digest:data.snapshot.spec.base_spec.dataset.manifest_digest}]};
 if(path==='/api/robustness')return {robustness:[{robustness_id:data.snapshot.result.robustness_id,overall_state:'COMPLETE'}]};
 if(path==='/api/robustness/'+data.snapshot.result.robustness_id)return data.snapshot;
 const parts=path.split('/'),e=data.evidence[parts[5]];return parts.length===6?e.variant:e[parts[6]];
}
const deferred=[];
(async()=>{
 currentApi=async path=>route(path);
 await ctx.chooseRobustParent(data.snapshot.result.robustness_id);
 measurements.push(el('robust-performance').textContent);
 assert.equal(el('robust-rows').children.length,8);
 assert.deepEqual(el('robust-rows').children.map(row=>row.children[0].children[0].textContent),['R0','V1','V2','V3','V4','V5','V6','V7']);
 assert(el('robust-rows').children[5].children[1].textContent.includes('0.200 mV · Direct input: 50 mV · derived by ×250 rule'));
 assert(el('robust-rows').children[7].children[1].textContent.includes('ConservativeSignPolicy'));
 assert(el('robust-rows').children[0].children[5].textContent.includes('unavailable · ZERO_BASELINE'));
 assert(el('robust-aggregate').textContent.includes('No aggregate robustness verdict requested.'));
 assert.equal(el('robust-synthetic').hidden,false);
 assert(el('robust-inspector').textContent.includes(data.snapshot.result.authoritative_digest));
 assert(el('robust-inspector').textContent.includes('Event identities/times matched across variants; prescribed amplitude follows variant configuration.'));
 assert(el('robust-rows').children[0].children[6].textContent.includes('REUSED'));
 assert(el('robust-rows').children[1].children[6].textContent.includes('COMPLETE'));
 assert(el('robust-rows').children[1].children[7].textContent.includes('EXECUTED'));
 assert.equal(el('robust-chart').children.length,8);
 assert.equal(el('robust-chart').children[0].children[1].children[0].attributes.y1,'60');
 await el('robust-rows').children[7].children[0].children[0].click();
 assert(el('robust-selected').textContent.endsWith('V7'));
 await el('robust-chart').children[5].click();assert(el('robust-selected').textContent.endsWith('V5'));
 assert.equal(run('comparison.comparison_id'),data.evidence.V5.comparison.comparison_id);
 assert.equal(run('pairedPlayback.baseline.run_id'),data.evidence.V5.playback.baseline.run_id);
 assert(el('compare-export').href.includes('/api/robustness/'));
 run('compareCursor=3; compareFrame=1; compareMaps[0].set(999,[1]);');
 currentApi=path=>new Promise(resolve=>deferred.push({path,resolve}));
 const old=ctx.selectRobustVariant(data.snapshot.result.robustness_id,'R0');
 const newer=ctx.selectRobustVariant(data.snapshot.result.robustness_id,'V3');
 assert.equal(run('compareCursor'),0);assert.equal(run('compareFrame'),null);assert.equal(run('compareMaps[0].size'),0);assert(el('compare-ready').hidden);
 deferred.find(x=>x.path.endsWith('/V3')).resolve(data.evidence.V3.variant);await new Promise(setImmediate);
 const requests=deferred.filter(x=>x.path.includes('/V3/'));assert.equal(requests.length,3);
 const newest=ctx.selectRobustVariant(data.snapshot.result.robustness_id,'V5');
 deferred.find(x=>x.path.endsWith('/V5')).resolve(data.evidence.V5.variant);await new Promise(setImmediate);
 for(const req of deferred.filter(x=>x.path.includes('/V5/')))req.resolve(route(req.path));await newest;
 const count=rendered.length;
 for(const req of requests)req.resolve(route(req.path));await newer;
 deferred.find(x=>x.path.endsWith('/R0')).resolve(data.evidence.R0.variant);await old;
 assert.equal(rendered.length,count);assert.equal(run('comparison.comparison_id'),data.evidence.V5.comparison.comparison_id);
 assert(!run('compareMaps[0].has(999)'));assert(cancelled>0);
 ctx.renderRobustMatrix(data.partial.result);assert(el('robust-rows').children[4].children[6].textContent.includes('FAILED'));assert(el('robust-rows').children[5].children[6].textContent.includes('not executed'));assert.equal(el('robust-rows').children[4].children[4].textContent,'unavailable');
 const authored=JSON.parse(JSON.stringify(data.snapshot.result));
 authored.variants[0].comparison.target.spike_count={baseline:77,intervention:12,absolute_delta:123,relative_delta:null,warning:'ZERO_BASELINE'};
 ctx.renderRobustMatrix(authored);ctx.renderRobustChart(authored);
 assert.equal(el('robust-rows').children[0].children[2].textContent,77);
 assert.equal(el('robust-rows').children[0].children[3].textContent,12);
 assert.equal(el('robust-rows').children[0].children[4].textContent,123);
 assert(el('robust-chart').children[0].children[0].textContent.includes('123 spikes'));
 const missing=JSON.parse(JSON.stringify(data.partial.result));missing.variants[4].state='CANCELLED';missing.variants[0].intervention.provenance='EXECUTED';ctx.renderRobustMatrix(missing);ctx.renderRobustChart(missing);
 assert(el('robust-rows').children[4].children[6].textContent.includes('CANCELLED'));assert(el('robust-rows').children[0].children[7].textContent.includes('baseline: EXECUTED · intervention: EXECUTED'));
 missing.variants[0].baseline.provenance='REUSED';ctx.renderRobustMatrix(missing);assert(el('robust-rows').children[0].children[7].textContent.includes('baseline: REUSED · intervention: EXECUTED'));
 assert.equal(el('robust-chart').children[4].children[1].children.length,1);
 currentApi=async path=>path==='/api/datasets'?route(path):({...data.snapshot,result:{...data.snapshot.result,overall_state:'RUNNING'},progress:{current_variant:'V3',current_role:'intervention',current_phase:'PREPARING',completed_variants:3,total_variants:8},elapsed_seconds:761});
 await ctx.updateRobustParent(data.snapshot.result.robustness_id);assert(el('robust-status').textContent.includes('ROBUSTNESS SWEEP ACTIVE'));assert(el('robust-status').textContent.includes('V3 · intervention · PREPARING'));assert(el('robust-status').textContent.includes('3 / 8 variants complete · Elapsed 12:41'));assert(!el('robust-status').textContent.includes('%'));
 await el('robust-release').click();assert(dialogs.pop().includes("this session's retained robustness evidence"));
 await el('robust-start').click();assert(el('robust-status').textContent.includes('Validate'));
 run('validSelection={mode:"none"};');await el('robust-start').click();assert(dialogs.pop().includes('up to 16 scientific child runs'));
 let requestedExport=null;
 ctx.URL={createObjectURL:()=>"blob:synthetic-review",revokeObjectURL(){}};
 ctx.fetch=async(path,options)=>{requestedExport={path,options};return {ok:true,blob:async()=>({backend:true})};};
 await el('robust-export').click();assert(requestedExport.path.endsWith('/export'));assert.equal(requestedExport.options.headers['X-Local-Session'],'private');
 el('compare-baseline').value='baseline';el('compare-intervention').value='intervention';
 let rejectNormal;
 currentApi=()=>new Promise((_,reject)=>{rejectNormal=reject;});const lateNormal=ctx.loadComparison();
 currentApi=async path=>route(path);await ctx.selectRobustVariant(data.snapshot.result.robustness_id,'V5');
 rejectNormal(Error('late normal request error'));await lateNormal;
 assert.equal(run('comparison.comparison_id'),data.evidence.V5.comparison.comparison_id);
 currentApi=async()=>new Promise(()=>{});const switching=ctx.chooseRobustParent('a'.repeat(64));assert.equal(run('pairedPlayback'),null);assert.equal(run('compareMaps[0].size'),0);assert.equal(el('robust-rows').children.length,0);
 console.log('A007C DOM/API contract checks PASS; out-of-order variant and parent switching PASS');
 console.log(measurements.join('\n'));
})().catch(e=>{console.error(e);process.exitCode=1;});
