import test from 'node:test';
import assert from 'node:assert/strict';
const mod=await import('../dist/decision/engine.mjs').catch(()=>({}));
test('reservoir volume balance uses PVT and checks pressure independently',()=>{
 assert.equal(typeof mod.balance,'function');
 const r=mod.balance({injection:120,oil:50,water:50,Bo:1.4,Bw:1,pressure:20,initial_pressure:25,pressure_trend:-.1});
 assert.ok(Math.abs(r.ratio-1)<1e-10);assert.equal(r.state,'平衡');
 assert.throws(()=>mod.balance({injection:-1,oil:1,water:1}),/非负/);
});
test('layer split conserves total and rejects zero capacity',()=>{
 assert.equal(typeof mod.layerSplit,'function');
 const r=mod.layerSplit([{layer:'A',permeability:100,thickness:5,connectivity:.8},{layer:'B',permeability:50,thickness:10,connectivity:.4}],300);
 assert.ok(Math.abs(r.reduce((s,x)=>s+x.volume,0)-300)<1e-9);assert.equal(r[0].fraction,2/3);
 assert.throws(()=>mod.layerSplit([{permeability:0,thickness:1,connectivity:1}],10),/吸水能力/);
});
test('lag correlation reports injection leading production',()=>{
 assert.equal(typeof mod.lagCorrelation,'function');
 const x=[1,7,2,9,4,8,3,6,2,5,10,3,6,1,9,4,7,2,8,5];const y=[0,0,...x.slice(0,-2)];
 const r=mod.lagCorrelation(x,y,5);assert.equal(r.lag,2);assert.ok(r.correlation>.99);
});
test('allocation obeys supply and per-layer pressure capacity',()=>{
 assert.equal(typeof mod.allocate,'function');
 const r=mod.allocate([{id:'A',weight:3,min:0,max:80,pressure:15,fracture:16,injectivity:10},{id:'B',weight:1,min:0,max:90,pressure:10,fracture:20,injectivity:10}],80);
 assert.ok(r[0].target<=10+1e-8);assert.ok(r.reduce((s,x)=>s+x.target,0)<=80+1e-8);
 assert.throws(()=>mod.allocate([{id:'A',weight:1,min:30,max:100,pressure:15,fracture:16,injectivity:10}],50),/不可行/);
});
test('measure effect subtracts baseline, reports economics and missing actuals',()=>{
 assert.equal(typeof mod.measureEffect,'function');
 const r=mod.measureEffect([{oil:120,baseline:100},{oil:130,baseline:100}],1000,200);
 assert.equal(r.incremental,50);assert.equal(r.net,9000);assert.equal(r.roi,9);
 assert.throws(()=>mod.measureEffect([],100,2),/实际/);
});
test('economic forecast stops at unprofitable production and refuses invalid decline',()=>{
 assert.equal(typeof mod.reserves,'function');
 const r=mod.reserves({qi:100,D:.1,b:0,days:365,oilPrice:100,waterCost:1,fixedCost:500,waterCut:.5});
 assert.ok(r.effectiveDays<365);assert.ok(r.volume>0);assert.throws(()=>mod.reserves({qi:100,D:-1,b:0,days:365,oilPrice:100,waterCost:1,fixedCost:500,waterCut:.5}),/递减/);
});
test('split rejects overlap and invalid percentages',()=>{
 assert.equal(typeof mod.partition,'function');
 const rows=Array.from({length:100},(_,i)=>({well_id:'P1',date:new Date(Date.UTC(2025,0,1+i)).toISOString().slice(0,10),oil:i}));
 const a=mod.partition(rows,[70,15,15]);assert.deepEqual(a.map(x=>x.length),[70,15,15]);
 assert.throws(()=>mod.partition(rows,[70,20,20]),/100/);assert.throws(()=>mod.partition([...rows,rows[0]],[70,15,15]),/重复/);
});
test('tree models learn nonlinear response with finite held-out outputs',()=>{
 assert.equal(typeof mod.trainTrees,'function');
 const rows=Array.from({length:100},(_,i)=>({x:i/100,y:(i/100)**2}));
 for(const id of ['boost','forest']){const fit=mod.trainTrees(id,rows.slice(0,80),['x'],'y',{trees:20,depth:3,seed:42});const pred=mod.predictTrees(fit,rows.slice(80));assert.ok(pred.every(Number.isFinite));assert.ok(mod.predictTrees(fit,[{x:.1}])[0]<mod.predictTrees(fit,[{x:.7}])[0]);}
});
test('isolation forest separates remote points from normal cluster',()=>{
 assert.equal(typeof mod.trainIsolation,'function');
 const rows=Array.from({length:100},(_,i)=>({x:Math.sin(i)*.1,y:Math.cos(i)*.1}));const fit=mod.trainIsolation(rows,['x','y'],{trees:80,seed:42});
 assert.ok(mod.isolationScores(fit,[{x:10,y:10}])[0]>mod.isolationScores(fit,[{x:0,y:0}])[0]);
});
test('NSGA-II returns feasible nondominated production structures',async()=>{
 const {nsga}=await import('../dist/decision/optimisation.mjs');
 const front=nsga({handling:600,cap:400,wc1:.3,wc2:.8,seed:42});assert.ok(front.length>1);
 for(const p of front){assert.ok(p.q1<=400&&p.q2<=400&&p.q1+p.q2<=600+1e-8);assert.ok(p.q1>=0&&p.q2>=0);}
 for(const a of front)for(const b of front)assert.ok(!(a.oil>b.oil&&a.water<b.water));
 assert.throws(()=>nsga({handling:-1,cap:400,wc1:.3,wc2:.8}),/非负/);
});
test('next-day feature builder never uses target-day observations',async()=>{
 const {nextDay}=await import('../dist/decision/training.mjs');
 const rows=[{well_id:'P1',date:'2025-01-01',oil:10,water:1,pressure:20,injection:30,water_cut:10},{well_id:'P1',date:'2025-01-02',oil:999,water:2,pressure:99,injection:999,water_cut:99}];
 const out=nextDay(rows);assert.equal(out[0].lag_oil,10);assert.equal(out[0].lag_pressure,20);assert.equal(out[0].oil,999);
 rows[1].date='2025-01-03';assert.equal(nextDay(rows).length,0);
});
test('DiD subtracts control change from treatment change',()=>{
 assert.equal(typeof mod.differenceInDifferences,'function');assert.equal(mod.differenceInDifferences({treatedBefore:100,treatedAfter:130,controlBefore:80,controlAfter:90}),20);
});
test('CSV string numeric fields produce same tree model as numeric JSON',()=>{
 const rows=Array.from({length:60},(_,i)=>({permeability:[2,10,20,80,100,400][i%6],fraction:[.1,.2,.3,.4,.5,.8][i%6]}));
 const strings=rows.map(r=>Object.fromEntries(Object.entries(r).map(([k,v])=>[k,String(v)])));
 const a=mod.trainTrees('forest',rows,['permeability'],'fraction',{trees:8,depth:3,seed:42});const b=mod.trainTrees('forest',strings,['permeability'],'fraction',{trees:8,depth:3,seed:42});
 assert.deepEqual(mod.predictTrees(a,rows),mod.predictTrees(b,rows));
});
test('active training rejects data mutations',()=>{
 assert.equal(typeof mod.assertExperimentWritable,'function');assert.throws(()=>mod.assertExperimentWritable({busy:true}),/训练/);assert.doesNotThrow(()=>mod.assertExperimentWritable({busy:false}));
});
test('report tools preserve independent scenario provenance and parameter inputs',()=>{
 assert.equal(typeof mod.toolEvidence,'function');const t=mod.toolEvidence({control:[{target:100}]},{control:{inputs:{supply:100},source:'合成小层'}});
 assert.equal(t.control.currentProductionEvidence,false);assert.equal(t.control.context.source,'合成小层');assert.equal(t.control.context.inputs.supply,100);assert.equal(t.control.result[0].target,100);
});
