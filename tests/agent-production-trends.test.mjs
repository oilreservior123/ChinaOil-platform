import test from 'node:test';
import assert from 'node:assert/strict';
const mod=await import('../dist/agent/production-trends.mjs').catch(()=>({}));
const rows=Array.from({length:60},(_,i)=>({well_id:'A',date:new Date(Date.UTC(2020,0,1+i)).toISOString().slice(0,10),oil:100+i,water:200+2*i,gas:1000+10*i}));
test('production trends extrapolate each measured target and derive explicitly oriented ratios',()=>{
 assert.equal(typeof mod.productionTrends,'function');const r=mod.productionTrends(rows,7);assert.equal(r.future.length,7);assert.equal(r.future[0].date,'2020-03-01');assert.ok(Math.abs(r.future[0].water-320)<1e-7);assert.ok(Math.abs(r.future[0].gas-1600)<1e-7);assert.ok(Math.abs(r.future[0].oil_gas_ratio-.1)<1e-9);assert.equal(r.future[0].gas_oil_ratio,10);assert.ok(r.models.water.validation.MAE<1e-7);assert.ok(r.duration>=0);
});
test('missing measurements, changing well coverage and duplicate records never become zero observations',()=>{
 assert.equal(typeof mod.productionTrends,'function');const b=rows.map(r=>({...r,well_id:'B'}));b.at(-1).gas=null;b.at(-2).water='';const r=mod.productionTrends([...rows,...b]);assert.equal(r.history.at(-1).gas,null);assert.equal(r.future[0].gas,null);assert.equal(r.future[0].oil_gas_ratio,null);assert.equal(r.history.at(-2).water,null);
 const missing=mod.productionTrends([...rows,...b.slice(0,-1)]);assert.equal(missing.history.at(-1).water,null);
 const duplicate=mod.productionTrends([...rows,{...rows.at(-1)}]);assert.equal(duplicate.history.at(-1).water,null);
});
test('zero denominators and sparse history yield explicit unavailable values',()=>{
 assert.equal(typeof mod.productionTrends,'function');const r=mod.productionTrends(rows.map(r=>({...r,gas:0})));assert.equal(r.future[0].gas,0);assert.equal(r.future[0].oil_gas_ratio,null);assert.equal(mod.productionTrends(rows.slice(0,8)).future[0].water,null);assert.equal(mod.productionTrends([]).future.length,0);
});
