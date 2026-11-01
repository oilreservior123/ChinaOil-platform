import test from 'node:test';import assert from 'node:assert/strict';
const e=await import('../dist/decision/evaluation.mjs').catch(()=>({}));
test('regression metrics include scale errors, signed bias and explicit coverage',()=>{
 assert.equal(typeof e.summarize,'function');const s=e.summarize({id:'boost',target:'oil'},[{actual:1,prediction:2},{actual:3,prediction:2},{actual:0,prediction:0},{actual:5,prediction:null}],5);
 assert.equal(s.metrics.MAE,2/3);assert.equal(s.metrics.MSE,2/3);assert.equal(s.metrics.Bias,0);assert.equal(s.metrics.N,3);assert.equal(s.predicted,3);assert.equal(s.coverage,60);assert.ok(Math.abs(s.metrics.MAPE-200/3)<1e-10);assert.equal(s.metrics.MAPE_N,2);
});
test('constant observations have undefined R2, zero observations have undefined MAPE',()=>{
 assert.equal(typeof e.summarize,'function');const s=e.summarize({id:'arps',target:'oil'},[{actual:0,prediction:1},{actual:0,prediction:0}],2);assert.equal(s.metrics.R2,null);assert.equal(s.metrics.MAPE,null);assert.ok(Number.isFinite(s.metrics.sMAPE));
});
test('unlabelled predictions retain outputs without inventing evaluation accuracy',()=>{
 assert.equal(typeof e.summarize,'function');const s=e.summarize({id:'isolation',target:'label'},[{prediction:1,score:.8},{prediction:0,score:.2}],2);assert.equal(s.predicted,2);assert.equal(s.metrics,null);assert.equal(s.confusion,null);
});
test('multiclass evaluation treats unknown true classes as actual errors',()=>{
 assert.equal(typeof e.summarize,'function');const s=e.summarize({id:'event3w',target:'event_code'},[{event_code:0,prediction:0},{event_code:1,prediction:0},{event_code:9,prediction:1}],3);
 assert.equal(s.kind,'classification');assert.equal(s.metrics.Accuracy,1/3);assert.equal(s.metrics.N,3);assert.equal(s.confusion.matrix.flat().reduce((a,b)=>a+b,0),3);assert.ok(s.confusion.labels.includes('9'));
});
test('multi-label evaluation does not compare pipe-separated labels as numbers',()=>{
 assert.equal(typeof e.summarize,'function');const s=e.summarize({id:'diagnosis',target:'root_cause'},[{root_cause:'堵塞|水窜',prediction:'堵塞'},{root_cause:'正常',prediction:'正常'}],2);
 assert.equal(s.kind,'multilabel');assert.equal(s.metrics.ExactMatch,.5);assert.equal(s.metrics.N,2);assert.equal(s.metrics.LabelN,6);
});
test('residual histogram accounts for all evaluated records and is finite for exact fits',()=>{
 assert.equal(typeof e.histogram,'function');const h=e.histogram([0,0,0],6);assert.equal(h.reduce((s,r)=>s+r.count,0),3);assert.ok(h.every(r=>Number.isFinite(r.left)&&Number.isFinite(r.right)));
});
test('split output export identifies datasets and preserves errors and source',()=>{
 assert.equal(typeof e.exportRows,'function');const s={train:{rows:[{well_id:'P1',actual:2,prediction:3}],kind:'regression'},validation:{rows:[{well_id:'P1',actual:4,prediction:2}],kind:'regression'}};const rows=e.exportRows(s,'user.csv');assert.equal(rows[0].dataset,'训练集');assert.equal(rows[0].error,1);assert.equal(rows[1].dataset,'验证集');assert.equal(rows[1].source,'user.csv');
});
test('recursive future scenario uses only previous observations and never exposes fake actual values',async()=>{
 const {forecast}=await import('../dist/decision/forecast.mjs');
 const model={id:'boost',mode:'tree',target:'oil',unit:'标准立方米/日'},history=[{well_id:'P1',date:'2025-01-01',oil:10,water:10,pressure:20,injection:40,water_cut:50}];const calls=[];
 const predict=async(m,fit,rows,context)=>{calls.push({date:rows[0].date,oil:context.at(-1).oil});return [{...rows[0],prediction:context.at(-1).oil+1}];};
 const r=await forecast(model,{},history,{days:3,well:'P1',residuals:[-2,2],predict});assert.deepEqual(r.rows.map(x=>x.prediction),[11,12,13]);assert.equal(r.rows[0].date,'2025-01-02');assert.ok(r.rows.every(x=>x.actual===null&&x.lower<=x.prediction&&x.upper>=x.prediction));assert.deepEqual(calls.map(x=>x.oil),[10,11,12]);assert.equal(history[0].oil,10);
});
test('future scenario refuses classification extrapolation and missing parameters',async()=>{
 const {forecast}=await import('../dist/decision/forecast.mjs');await assert.rejects(()=>forecast({id:'esp'}, {},[],{days:7}),/不支持/);await assert.rejects(()=>forecast({id:'arps'}, {},[{well_id:'P1',date:'not-a-date',oil:1}],{days:7}),/日期/);
});
test('evaluation keeps all three result sets and only passes earlier split history',async()=>{
 const {evaluateAll}=await import('../dist/decision/evaluation-runner.mjs');const sets=[[{well_id:'P1',date:'2025-01-01',oil:1}],[{well_id:'P1',date:'2025-01-02',oil:2}],[{well_id:'P1',date:'2025-01-03',oil:3}]],calls=[];
 const r=await evaluateAll({id:'boost',target:'oil'}, {},sets,null,{predictor:async(m,f,rows,context)=>{calls.push(context.map(r=>r.date));return rows.map(r=>({...r,actual:r.oil,prediction:r.oil}));}});
 assert.deepEqual(calls,[[],['2025-01-01'],['2025-01-01','2025-01-02']]);assert.equal(r.summaries.train.metrics.RMSE,0);assert.equal(r.summaries.validation.metrics.RMSE,0);assert.equal(r.summaries.test.metrics.RMSE,0);
});
test('ROC AUC handles ties and requires both true classes',()=>{assert.equal(e.roc([{y:0,score:.5},{y:1,score:.5}]).auc,.5);assert.equal(e.roc([{y:0,score:.1},{y:1,score:.9}]).auc,1);assert.equal(e.roc([{y:1,score:.9}]),null);});
test('all-missing regression outputs have zero coverage and no invented metrics',()=>{const s=e.summarize({id:'crm',target:'liquid'},[{liquid:100,prediction:null}],2);assert.equal(s.coverage,0);assert.equal(s.metrics,null);});
test('tree validation loss is measured without changing fitted trees or using test rows',async()=>{
 const {train}=await import('../dist/decision/training.mjs');const m={id:'effect',mode:'effect',target:'incremental',required:['permeability','incremental']},tr=Array.from({length:30},(_,i)=>({permeability:i,incremental:i*2})),va=Array.from({length:10},(_,i)=>({permeability:i,incremental:i*3}));
 const fit=await train(m,tr,va,{trees:3,depth:2},()=>{});assert.equal(fit.history.length,3);assert.ok(fit.history.every(h=>Number.isFinite(h.val_loss)));
});
test('forecast well selection cannot change while a forecast or evaluation is running',async()=>{
 const {applyForecastSelection}=await import('../dist/decision/forecast.mjs');const old={rows:[{well_id:'P1',prediction:1}]},state={busy:true,forecastWell:'P1',forecast:old};
 assert.equal(applyForecastSelection(state,'P2'),false);assert.equal(state.forecastWell,'P1');assert.equal(state.forecast,old);state.busy=false;
 assert.equal(applyForecastSelection(state,'P2'),true);assert.equal(state.forecastWell,'P2');assert.equal(state.forecast,null);
});
