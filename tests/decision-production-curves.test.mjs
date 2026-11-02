import test from 'node:test';import assert from 'node:assert/strict';
const mod=await import('../dist/decision/production-curves.mjs').catch(()=>({}));
test('daily gas and water are aggregated by date and oil-gas ratio uses ratio of totals',()=>{
 assert.equal(typeof mod.groupProductionRows,'function');
 const r=mod.groupProductionRows([{date:'2025-01-02',well_id:'A',oil:5,gas:0,water:2,pressure:20,injection:4,liquid:7},{date:'2025-01-01',well_id:'A',oil:10,gas:100,water:3,pressure:20,injection:4,liquid:13},{date:'2025-01-01',well_id:'B',oil:30,gas:900,water:7,pressure:24,injection:6,liquid:37}]);
 assert.deepEqual(r.map(x=>x.date),['2025-01-01','2025-01-02']);assert.equal(r[0].gas,1000);assert.equal(r[0].daily_water,10);assert.equal(r[0].oil_gas_ratio,.04);assert.equal(r[0].oil_per_10k_gas,400);assert.equal(r[1].oil_gas_ratio,null);assert.equal(r[1].gas,0);
 assert.equal(r[0].pressure,22);assert.equal(r[0].water_cut,20);assert.equal(r[0].injection,10);
});
test('missing or invalid gas is not filled with zero or divided into a false ratio',()=>{
 assert.equal(typeof mod.groupProductionRows,'function');
 for(const gas of [undefined,null,'',NaN,-2]){const r=mod.groupProductionRows([{date:'2025-01-01',well_id:'A',oil:10,gas:100,water:3},{date:'2025-01-01',well_id:'B',oil:5,gas,water:4}])[0];assert.equal(r.gas,null);assert.equal(r.oil_gas_ratio,null);assert.equal(r.gas_missing_count,1);}
 const r=mod.groupProductionRows([{date:'2025-01-01',well_id:'A',oil:0,gas:100,water:0}])[0];assert.equal(r.oil_gas_ratio,0);assert.equal(r.daily_water,0);
});
test('valid numeric CSV fields are accepted without mutating original rows',()=>{
 assert.equal(typeof mod.groupProductionRows,'function');const a=[{date:'2025-01-01',well_id:'A',oil:'2',gas:'400',water:'8',pressure:'10',liquid:'10',injection:'3'}],before=JSON.stringify(a);const r=mod.groupProductionRows(a)[0];assert.equal(r.gas,400);assert.equal(r.daily_water,8);assert.equal(r.oil_per_10k_gas,50);assert.equal(JSON.stringify(a),before);
});
test('three curve panels have individual colors, Chinese units and unambiguous oil/gas formula',()=>{
 assert.equal(typeof mod.productionCurvePanels,'function');const html=mod.productionCurvePanels(mod.groupProductionRows([{date:'2025-01-01',oil:2,gas:400,water:8,pressure:10,liquid:10}]));assert.ok(html.includes('日产水动态'));assert.ok(html.includes('日产气动态'));assert.ok(html.includes('油气比动态'));assert.ok(html.includes('日产油÷日产气×10000'));assert.ok(html.includes('标准立方米油/万标准立方米气'));assert.ok(html.includes('#0c98a5')&&html.includes('#7c55ab')&&html.includes('#bc8640'));
});
test('unavailable gas curve explains the missing gas field without inventing a series',()=>{
 assert.equal(typeof mod.productionCurvePanels,'function');const html=mod.productionCurvePanels(mod.groupProductionRows([{date:'2025-01-01',oil:2,water:8}]));assert.ok(html.includes('缺少有效日产气'));assert.ok(html.includes('gas'));assert.ok(!html.includes('Infinity')&&!html.includes('NaN'));
});
