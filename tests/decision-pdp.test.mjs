import test from 'node:test';import assert from 'node:assert/strict';
const m=await import('../dist/decision/pdp-model.mjs').catch(()=>({}));
function sample(){const rows=[];for(let i=0;i<46;i++){const year=2023+Math.floor(i/12),month=i%12+1,days=new Date(Date.UTC(year,month,0)).getUTCDate(),wells=i<39?100:93;rows.push({month:year+'-'+String(month).padStart(2,'0'),oil_tonnes:50*Math.exp(-.014*i)*days*wells*Math.exp(.025*Math.sin(i*1.7))*(i>=39?.8:1),active_wells:wells,water_m3:200000+i*7000,pressure_mpa:24-i*.03-(i>=39?1:0),density_t_per_m3:.85});}return rows;}
const opts={baseYear:2025,asOf:'2026-10',fitMonths:24,updateMonths:6,horizon:12,bootstrap:200,seed:42};
test('exponential fit normalizes month length and producing-well exposure',()=>{
 assert.equal(typeof m.fitDecline,'function');const rows=sample().slice(0,36).map((r,i)=>({...r,oil_tonnes:50*Math.exp(-.014*i)*m.monthDays(r.month)*r.active_wells}));const fit=m.fitDecline(rows);assert.ok(Math.abs(fit.beta+.014)<1e-10);assert.ok(Math.abs(fit.annualDecline-(1-Math.exp(-.014*12)))<1e-10);assert.equal(m.monthDays('2024-02'),29);
});
test('prior-year baseline is frozen and current/future data cannot alter it',()=>{
 assert.equal(typeof m.analyzePdp,'function');const rows=sample(),a=m.analyzePdp(rows,opts),changed=rows.map(r=>r.month>'2025-12'?{...r,oil_tonnes:r.oil_tonnes*.6}:r),b=m.analyzePdp(changed,opts);assert.deepEqual(a.baseline.map(r=>r.prediction),b.baseline.map(r=>r.prediction));assert.ok(a.current.some(r=>r.level==='红'));assert.equal(a.freezeDate,'2025-12-31');
 const future={...rows.at(-1),month:'2027-01',oil_tonnes:99999999};const c=m.analyzePdp([...rows,future],opts);assert.deepEqual(a.forecast,c.forecast);
});
test('updated predictions expose distinct confidence and single-month prediction intervals',()=>{
 assert.equal(typeof m.analyzePdp,'function');const a=m.analyzePdp(sample(),opts);assert.equal(a.forecast.length,12);assert.equal(a.forecast[0].month,'2026-11');assert.ok(a.forecast.every(r=>r.ci_low>0&&r.ci_high>=r.ci_low&&r.pi_high>=r.pi_low));assert.ok(a.forecast.reduce((s,r)=>s+r.pi_high-r.pi_low,0)>a.forecast.reduce((s,r)=>s+r.ci_high-r.ci_low,0));assert.ok(a.forecast.every(r=>r.actual===null));
});
test('missing observed months stay missing and zero production produces a real warning',()=>{
 assert.equal(typeof m.analyzePdp,'function');const rows=sample().filter(r=>r.month!=='2026-04').map(r=>r.month==='2026-05'?{...r,oil_tonnes:0,active_wells:0}:r),a=m.analyzePdp(rows,opts);assert.equal(a.current.find(r=>r.month==='2026-04').actual,null);assert.equal(a.current.find(r=>r.month==='2026-04').level,'灰');assert.equal(a.current.find(r=>r.month==='2026-05').actual,0);assert.equal(a.current.find(r=>r.month==='2026-05').level,'红');
});
test('original issued monthly plan is retained exactly and does not gain invented intervals',()=>{
 assert.equal(typeof m.analyzePdp,'function');const external=Array.from({length:12},(_,i)=>({month:'2026-'+String(i+1).padStart(2,'0'),forecast_oil_tonnes:100000-i*1000,issued_on:'2025-12-31'}));const a=m.analyzePdp(sample(),{...opts,externalBaseline:external});assert.equal(a.baseline[0].prediction,100000);assert.equal(a.baseline[0].ci_low,null);assert.equal(a.baseline[0].pi_low,null);assert.equal(a.baselineSource,'原始年末计划上传');assert.throws(()=>m.analyzePdp(sample(),{...opts,externalBaseline:external.map(r=>({...r,issued_on:'2026-02-01'}))}),/冻结/);
});
test('duplicates, invalid months and negative observations fail with actionable messages',()=>{
 assert.equal(typeof m.analyzePdp,'function');const a=sample();assert.throws(()=>m.analyzePdp([...a,a[0]],opts),/重复/);assert.throws(()=>m.analyzePdp([{...a[0],month:'2025-13'}],opts),/月份/);assert.throws(()=>m.analyzePdp(a.map((r,i)=>i? r:{...r,oil_tonnes:-1}),opts),/非负/);assert.throws(()=>m.analyzePdp(a,{...opts,asOf:'2025-10'}),/次年/);
});
test('expert system explains causes as candidates and never invents case success probabilities',async()=>{
 const e=await import('../dist/decision/pdp-expert.mjs');const r=m.analyzePdp(sample(),opts),report=e.assessPdp(r,[{id:'V1',source:'公开趋势',oil_change_pct:-25,water_cut_delta_pp:8,pressure_delta_mpa:-1,availability_change_pct:-7,conclusion:'非因果证据'}]);assert.ok(report.actions.length>0);assert.ok(report.petroleum.some(s=>s.includes('候选')));assert.equal(report.cases[0].source,'公开趋势');assert.ok(!JSON.stringify(report).includes('success_probability'));assert.ok(report.statistics.some(s=>s.includes('置信')));
});
test('two reference-style figures distinguish frozen plan, observed production, confidence and prediction bands',async()=>{
 const c=await import('../dist/decision/pdp-charts.mjs'),r=m.analyzePdp(sample(),opts),a=c.baselineFigure(r),b=c.forecastFigure(r);assert.ok(a.includes('2025-12-31'));assert.ok(a.includes('当年月油'));assert.ok(a.includes('半对数'));assert.ok(b.includes('95%均值置信区间 CI'));assert.ok(b.includes('95%单月预测区间 PI'));assert.ok(!a.includes('NaN')&&!b.includes('Infinity'));assert.ok(c.svgOnly(b).startsWith('<svg'));
});
test('default workbench exposes two figures and a local expert handoff without claiming field data',async()=>{
 const w=await import('../dist/decision/pdp-workbench.mjs');w.initializePdp(sample(),[]);const html=w.renderPdpWorkbench();assert.ok(html.includes('图1 ·'));assert.ok(html.includes('图2 ·'));assert.ok(html.includes('非新疆油田实测'));assert.ok(html.includes('data-pdp="assistant"'));assert.ok(html.includes('模型名称、结构、数学公式与参数注释'));
});
test('restoring zero active wells applies the same conditional gain to means and intervals',()=>{
 const rows=sample().map(r=>r.month==='2026-10'?{...r,oil_tonnes:0,active_wells:0}:r),a=m.analyzePdp(rows,{...opts,plannedWells:50,gainPct:0}),b=m.analyzePdp(rows,{...opts,plannedWells:50,gainPct:20});assert.ok(Math.abs(b.forecast[0].scenario/a.forecast[0].scenario-1.2)<1e-10);assert.ok(Math.abs(b.forecast[0].scenario_ci_low/a.forecast[0].scenario_ci_low-1.2)<1e-10);
});
test('standalone SVG exports retain visible chart titles and both uncertainty legends',async()=>{
 const c=await import('../dist/decision/pdp-charts.mjs'),r=m.analyzePdp(sample(),opts),svg=c.svgOnly(c.forecastFigure(r));assert.ok(svg.includes('>更新模型95%均值置信区间 CI</text>'));assert.ok(svg.includes('>更新模型95%单月预测区间 PI</text>'));assert.ok(svg.includes('图2：专家研判后的后续预测与置信区间'));
});
test('a multi-year original year-end PDP plan is accepted without being re-estimated',()=>{
 const external=Array.from({length:36},(_,i)=>({month:m.monthName(2026*12+i),forecast_oil_tonnes:100000-i*1000,issued_on:'2025-12-31'})),a=m.analyzePdp(sample(),{...opts,externalBaseline:external});assert.equal(a.baseline.length,36);assert.equal(a.forecast.at(-1).baseline,79000);
});
test('uploading new actuals preserves an explicitly uploaded frozen original plan',async()=>{
 const w=await import('../dist/decision/pdp-workbench.mjs'),rows=sample(),plan=Array.from({length:12},(_,i)=>({month:'2026-'+String(i+1).padStart(2,'0'),forecast_oil_tonnes:123456-i*1000,issued_on:'2025-12-31'})),file=(name,a)=>({name,size:100,text:async()=>JSON.stringify(a)}),ctx={render:()=>{},notify:()=>{}};
 w.initializePdp(rows,[]);await w.pdpUpload('original',file('plan.json',plan),ctx);assert.equal(w.pdpSummary().baselineSource,'原始年末计划上传');await w.pdpUpload('monthly',file('new-monthly.json',rows.map(r=>r.month>'2025-12'?{...r,oil_tonnes:r.oil_tonnes*.9}:r)),ctx);assert.equal(w.pdpSummary().baselineSource,'原始年末计划上传');assert.equal(w.pdpSummary().current[0].prediction,123456);
});
